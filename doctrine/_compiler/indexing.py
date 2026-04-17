from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeAlias

import doctrine._model.declarations as model
from doctrine._compiler.diagnostics import compile_error, file_scoped_related, related_prompt_site
from doctrine._model.core import ImportPath
from doctrine.diagnostics import CompileError, DoctrineError
from doctrine.parser import parse_file

if TYPE_CHECKING:
    from doctrine._compiler.session import CompilationSession

from doctrine._compiler.support import dotted_decl_name, path_location

_KNOWN_RENDER_PROFILE_TARGETS = {
    "review.contract_checks",
    "analysis.stages",
    "control.invalidations",
    "guarded_sections",
    "identity.owner",
    "identity.debug",
    "identity.enum_wire",
    "properties",
    "guard",
    "sequence",
    "bullets",
    "checklist",
    "definitions",
    "table",
    "callout",
    "code",
    "markdown",
    "html",
    "footnotes",
    "image",
}
_KNOWN_RENDER_PROFILE_MODES = {
    "sentence",
    "titled_section",
    "expanded_sequence",
    "natural_ordered_prose",
    "concise_explanatory_shell",
    "title",
    "title_and_key",
    "wire_only",
}
_RENDER_PROFILE_TARGET_MODE_CONSTRAINTS = {
    "analysis.stages": {"natural_ordered_prose", "titled_section"},
    "review.contract_checks": {"sentence", "titled_section"},
    "control.invalidations": {"sentence", "expanded_sequence"},
    "identity.owner": {"title", "title_and_key"},
    "identity.debug": {"title", "title_and_key"},
    "identity.enum_wire": {"title", "title_and_key", "wire_only"},
}

ModuleLoadKey: TypeAlias = tuple[Path, tuple[str, ...]]
ModuleSourceKind: TypeAlias = Literal["entrypoint", "file_module", "runtime_package"]


@dataclass(slots=True, frozen=True)
class ResolvedModuleSource:
    prompt_root: Path
    prompt_path: Path
    module_source_kind: ModuleSourceKind
    package_root: Path | None = None


@dataclass(slots=True, frozen=True)
class ImportedSymbolBinding:
    target_name: str
    target_unit: "IndexedUnit"
    import_decl: model.ImportDecl


@dataclass(slots=True, frozen=True)
class IndexedUnit:
    prompt_root: Path
    module_parts: tuple[str, ...]
    module_source_kind: ModuleSourceKind
    package_root: Path | None
    prompt_file: model.PromptFile
    imports: tuple[model.ImportDecl, ...]
    render_profiles_by_name: dict[str, model.RenderProfileDecl]
    analyses_by_name: dict[str, model.AnalysisDecl]
    decisions_by_name: dict[str, model.DecisionDecl]
    schemas_by_name: dict[str, model.SchemaDecl]
    tables_by_name: dict[str, model.TableDecl]
    documents_by_name: dict[str, model.DocumentDecl]
    workflows_by_name: dict[str, model.WorkflowDecl]
    route_onlys_by_name: dict[str, model.RouteOnlyDecl]
    groundings_by_name: dict[str, model.GroundingDecl]
    reviews_by_name: dict[str, model.ReviewDecl]
    inputs_blocks_by_name: dict[str, model.InputsDecl]
    inputs_by_name: dict[str, model.InputDecl]
    input_sources_by_name: dict[str, model.InputSourceDecl]
    outputs_blocks_by_name: dict[str, model.OutputsDecl]
    outputs_by_name: dict[str, model.OutputDecl]
    output_targets_by_name: dict[str, model.OutputTargetDecl]
    output_shapes_by_name: dict[str, model.OutputShapeDecl]
    output_schemas_by_name: dict[str, model.OutputSchemaDecl]
    skills_by_name: dict[str, model.SkillDecl]
    skill_packages_by_name: dict[str, model.SkillPackageDecl]
    skill_packages_by_id: dict[str, model.SkillPackageDecl]
    skills_blocks_by_name: dict[str, model.SkillsDecl]
    enums_by_name: dict[str, model.EnumDecl]
    agents_by_name: dict[str, model.Agent]
    imported_units: dict[tuple[str, ...], "IndexedUnit"]
    visible_imported_units: dict[tuple[str, ...], "IndexedUnit"]
    imported_symbols_by_name: dict[str, ImportedSymbolBinding]


@dataclass(slots=True, frozen=True)
class LoadedImports:
    imported_units: dict[tuple[str, ...], IndexedUnit]
    visible_imported_units: dict[tuple[str, ...], IndexedUnit]
    imported_symbols_by_name: dict[str, ImportedSymbolBinding]


def _clone_doctrine_error(error: DoctrineError) -> DoctrineError:
    return type(error)(diagnostic=error.diagnostic)


def _register_decl(
    registry: dict[str, object],
    declaration: object,
    name: str,
    module_parts: tuple[str, ...],
    *,
    source_path: Path | None,
) -> None:
    existing = registry.get(name)
    if existing is not None:
        dotted_name = ".".join((*module_parts, name)) or name
        raise compile_error(
            code="E288",
            summary="Duplicate declaration name",
            detail=f"Declaration `{dotted_name}` is defined more than once in the same module.",
            path=source_path,
            source_span=getattr(declaration, "source_span", None),
            related=(
                related_prompt_site(
                    label="first declaration",
                    path=source_path,
                    source_span=getattr(existing, "source_span", None),
                ),
            ),
            hints=("Keep one declaration for this name in the module.",),
        )


def skill_package_id(declaration: model.SkillPackageDecl) -> str:
    return declaration.metadata.name or declaration.name


def _register_skill_package_id(
    registry: dict[str, model.SkillPackageDecl],
    declaration: model.SkillPackageDecl,
    *,
    module_parts: tuple[str, ...],
    source_path: Path | None,
) -> None:
    package_id = skill_package_id(declaration)
    existing = registry.get(package_id)
    if existing is not None:
        dotted_module = ".".join(module_parts)
        owner_label = (
            f"module `{dotted_module}`" if dotted_module else "the root prompt module"
        )
        raise compile_error(
            code="E299",
            summary="Duplicate skill package id",
            detail=(
                f"Skill package id `{package_id}` is defined more than once in {owner_label}."
            ),
            path=source_path,
            source_span=declaration.source_span,
            related=(
                related_prompt_site(
                    label="first package id",
                    path=source_path,
                    source_span=getattr(existing, "source_span", None),
                ),
            ),
            hints=("Keep each skill package id unique within one module.",),
        )
    registry[package_id] = declaration


def _validate_enum_decl(
    decl: model.EnumDecl,
    *,
    owner_label: str,
    source_path: Path | None,
) -> None:
    seen_keys: dict[str, model.EnumMember] = {}
    seen_wire_values: dict[str, model.EnumMember] = {}
    for member in decl.members:
        existing_key = seen_keys.get(member.key)
        if existing_key is not None:
            raise compile_error(
                code="E293",
                summary="Duplicate enum member key",
                detail=f"Enum `{owner_label}` repeats member key `{member.key}`.",
                path=source_path,
                source_span=member.source_span,
                related=(
                    related_prompt_site(
                        label="first member",
                        path=source_path,
                        source_span=existing_key.source_span,
                    ),
                ),
                hints=("Keep each enum member key only once.",),
            )
        seen_keys[member.key] = member
        existing_wire = seen_wire_values.get(member.value)
        if existing_wire is not None:
            raise compile_error(
                code="E294",
                summary="Duplicate enum member wire",
                detail=f"Enum `{owner_label}` repeats wire value `{member.value}`.",
                path=source_path,
                source_span=member.source_span,
                related=(
                    related_prompt_site(
                        label="first member",
                        path=source_path,
                        source_span=existing_wire.source_span,
                    ),
                ),
                hints=("Keep each enum wire value only once.",),
            )
        seen_wire_values[member.value] = member


def _validate_render_profile_decl(
    decl: model.RenderProfileDecl,
    *,
    owner_label: str,
    source_path: Path | None,
) -> None:
    seen_targets: dict[tuple[str, ...], model.RenderProfileRule] = {}
    for rule in decl.rules:
        target_text = ".".join(rule.target_parts)
        if target_text not in _KNOWN_RENDER_PROFILE_TARGETS:
            raise compile_error(
                code="E298",
                summary="Invalid render_profile declaration",
                detail=f"Unknown render_profile target in {owner_label}: {target_text}",
                path=source_path,
                source_span=rule.source_span,
                hints=("Use only shipped render_profile targets.",),
            )
        if rule.mode not in _KNOWN_RENDER_PROFILE_MODES:
            raise compile_error(
                code="E298",
                summary="Invalid render_profile declaration",
                detail=f"Unknown render_profile mode in {owner_label}: {rule.mode}",
                path=source_path,
                source_span=rule.source_span,
                hints=("Use only shipped render_profile modes.",),
            )
        allowed_modes = _RENDER_PROFILE_TARGET_MODE_CONSTRAINTS.get(target_text)
        if allowed_modes is not None and rule.mode not in allowed_modes:
            raise compile_error(
                code="E298",
                summary="Invalid render_profile declaration",
                detail=f"Invalid render_profile mode for {target_text} in {owner_label}: {rule.mode}",
                path=source_path,
                source_span=rule.source_span,
                hints=("Keep each render_profile target on one of its shipped supported modes.",),
            )
        existing_rule = seen_targets.get(rule.target_parts)
        if existing_rule is not None:
            raise compile_error(
                code="E298",
                summary="Invalid render_profile declaration",
                detail=f"Duplicate render_profile rule target in {owner_label}: {target_text}",
                path=source_path,
                source_span=rule.source_span,
                related=(
                    related_prompt_site(
                        label="first rule",
                        path=source_path,
                        source_span=existing_rule.source_span,
                    ),
                ),
                hints=("Declare each render_profile target at most once.",),
            )
        seen_targets[rule.target_parts] = rule


def _resolve_import_path(
    import_decl: model.ImportDecl, *, module_parts: tuple[str, ...], source_path: Path | None
) -> tuple[str, ...]:
    import_path = import_decl.path
    if import_path.level == 0:
        return import_path.module_parts

    current_package_parts = module_parts[:-1] if module_parts else ()
    parent_walk = import_path.level - 1
    package_parts = (
        current_package_parts[:-parent_walk] if parent_walk else current_package_parts
    )
    if parent_walk > len(current_package_parts):
        dotted_import = "." * import_path.level + ".".join(import_path.module_parts)
        raise compile_error(
            code="E290",
            summary="Relative import walks above prompts root",
            detail=f"Import `{dotted_import}` walks above the prompts root.",
            path=source_path,
            source_span=import_decl.source_span,
        )

    return (*package_parts, *import_path.module_parts)


def _module_load_key(prompt_root: Path, module_parts: tuple[str, ...]) -> ModuleLoadKey:
    return (prompt_root, module_parts)


def _module_path_for_root(prompt_root: Path, module_parts: tuple[str, ...]) -> Path:
    return prompt_root.joinpath(*module_parts).with_suffix(".prompt")


def _runtime_package_path_for_root(prompt_root: Path, module_parts: tuple[str, ...]) -> Path:
    return prompt_root.joinpath(*module_parts, "AGENTS.prompt")


def _module_relpath_text(path: Path, *, prompt_root: Path) -> str:
    try:
        return path.relative_to(prompt_root).as_posix()
    except ValueError:
        return str(path)


def _resolve_module_source_in_root(
    prompt_root: Path,
    module_parts: tuple[str, ...],
    *,
    importer_path: Path | None = None,
    import_source_span=None,
    file_module_package_root: Path | None = None,
) -> ResolvedModuleSource | None:
    file_module_path = _module_path_for_root(prompt_root, module_parts)
    runtime_package_path = _runtime_package_path_for_root(prompt_root, module_parts)
    has_file_module = file_module_path.is_file()
    has_runtime_package = runtime_package_path.is_file()

    if has_file_module and has_runtime_package:
        dotted_name = ".".join(module_parts)
        raise compile_error(
            code="E287",
            summary="Ambiguous import module",
            detail=(
                f"Import module `{dotted_name}` matches more than one prompt file shape under "
                f"`{prompt_root}`."
            ),
            path=importer_path,
            source_span=import_source_span,
            related=(
                file_scoped_related(label="file module", path=file_module_path),
                file_scoped_related(label="runtime package", path=runtime_package_path),
            ),
            hints=("Keep one module owner for this dotted import path.",),
        )
    if has_runtime_package:
        return ResolvedModuleSource(
            prompt_root=prompt_root,
            prompt_path=runtime_package_path,
            module_source_kind="runtime_package",
            package_root=runtime_package_path.parent,
        )
    if has_file_module:
        return ResolvedModuleSource(
            prompt_root=prompt_root,
            prompt_path=file_module_path,
            module_source_kind="file_module",
            package_root=file_module_package_root,
        )
    return None


def _waiting_module_key(ancestry: tuple[ModuleLoadKey, ...]) -> ModuleLoadKey | None:
    if not ancestry:
        return None
    return ancestry[-1]


def _has_module_wait_cycle(
    session: "CompilationSession",
    *,
    waiting_module: ModuleLoadKey,
    target_module: ModuleLoadKey,
) -> bool:
    current = target_module
    seen: set[ModuleLoadKey] = set()
    while current is not None:
        if current == waiting_module:
            return True
        if current in seen:
            return False
        seen.add(current)
        current = session._module_waits.get(current)
    return False


def index_unit(
    session: "CompilationSession",
    prompt_file: model.PromptFile,
    *,
    prompt_root: Path,
    module_parts: tuple[str, ...],
    module_source_kind: ModuleSourceKind,
    package_root: Path | None,
    ancestry: tuple[ModuleLoadKey, ...],
    allow_parallel_imports: bool,
) -> IndexedUnit:
    imports: list[model.ImportDecl] = []
    render_profiles_by_name: dict[str, model.RenderProfileDecl] = {}
    analyses_by_name: dict[str, model.AnalysisDecl] = {}
    decisions_by_name: dict[str, model.DecisionDecl] = {}
    schemas_by_name: dict[str, model.SchemaDecl] = {}
    tables_by_name: dict[str, model.TableDecl] = {}
    documents_by_name: dict[str, model.DocumentDecl] = {}
    workflows_by_name: dict[str, model.WorkflowDecl] = {}
    route_onlys_by_name: dict[str, model.RouteOnlyDecl] = {}
    groundings_by_name: dict[str, model.GroundingDecl] = {}
    reviews_by_name: dict[str, model.ReviewDecl] = {}
    skills_blocks_by_name: dict[str, model.SkillsDecl] = {}
    inputs_blocks_by_name: dict[str, model.InputsDecl] = {}
    inputs_by_name: dict[str, model.InputDecl] = {}
    input_sources_by_name: dict[str, model.InputSourceDecl] = {}
    outputs_blocks_by_name: dict[str, model.OutputsDecl] = {}
    outputs_by_name: dict[str, model.OutputDecl] = {}
    output_targets_by_name: dict[str, model.OutputTargetDecl] = {}
    output_shapes_by_name: dict[str, model.OutputShapeDecl] = {}
    output_schemas_by_name: dict[str, model.OutputSchemaDecl] = {}
    skills_by_name: dict[str, model.SkillDecl] = {}
    skill_packages_by_name: dict[str, model.SkillPackageDecl] = {}
    skill_packages_by_id: dict[str, model.SkillPackageDecl] = {}
    agents_by_name: dict[str, model.Agent] = {}
    enums_by_name: dict[str, model.EnumDecl] = {}

    for declaration in prompt_file.declarations:
        if isinstance(declaration, model.ImportDecl):
            imports.append(declaration)
            continue
        if isinstance(declaration, model.RenderProfileDecl):
            _register_decl(
                render_profiles_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            _validate_render_profile_decl(
                declaration,
                owner_label=dotted_decl_name(module_parts, declaration.name),
                source_path=prompt_file.source_path,
            )
            render_profiles_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.AnalysisDecl):
            _register_decl(
                analyses_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            analyses_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.DecisionDecl):
            _register_decl(
                decisions_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            decisions_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.SchemaDecl):
            _register_decl(
                schemas_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            schemas_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.TableDecl):
            _register_decl(
                tables_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            tables_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.DocumentDecl):
            _register_decl(
                documents_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            documents_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.WorkflowDecl):
            _register_decl(
                workflows_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            workflows_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.RouteOnlyDecl):
            _register_decl(
                route_onlys_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            route_onlys_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.GroundingDecl):
            _register_decl(
                groundings_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            groundings_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.ReviewDecl):
            _register_decl(
                reviews_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            reviews_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.SkillsDecl):
            _register_decl(
                skills_blocks_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            skills_blocks_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.InputsDecl):
            _register_decl(
                inputs_blocks_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            inputs_blocks_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.InputDecl):
            _register_decl(
                inputs_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            inputs_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.InputSourceDecl):
            _register_decl(
                input_sources_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            input_sources_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.OutputsDecl):
            _register_decl(
                outputs_blocks_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            outputs_blocks_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.OutputDecl):
            _register_decl(
                outputs_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            outputs_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.OutputTargetDecl):
            _register_decl(
                output_targets_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            output_targets_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.OutputShapeDecl):
            _register_decl(
                output_shapes_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            output_shapes_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.OutputSchemaDecl):
            _register_decl(
                output_schemas_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            output_schemas_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.SkillDecl):
            _register_decl(
                skills_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            skills_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.SkillPackageDecl):
            _register_decl(
                skill_packages_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            skill_packages_by_name[declaration.name] = declaration
            _register_skill_package_id(
                skill_packages_by_id,
                declaration,
                module_parts=module_parts,
                source_path=prompt_file.source_path,
            )
            continue
        if isinstance(declaration, model.EnumDecl):
            _register_decl(
                enums_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            _validate_enum_decl(
                declaration,
                owner_label=dotted_decl_name(module_parts, declaration.name),
                source_path=prompt_file.source_path,
            )
            enums_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.Agent):
            _register_decl(
                agents_by_name,
                declaration,
                declaration.name,
                module_parts,
                source_path=prompt_file.source_path,
            )
            agents_by_name[declaration.name] = declaration
            continue
        raise compile_error(
            code="E901",
            summary="Internal compiler error",
            detail=(
                "Internal compiler error: unsupported declaration type: "
                f"{type(declaration).__name__}"
            ),
            path=prompt_file.source_path,
            source_span=getattr(declaration, "source_span", None),
            hints=("This is a compiler bug, not a prompt authoring error.",),
        )

    loaded_imports = load_imports(
        session,
        imports,
        prompt_root=prompt_root,
        package_root=package_root,
        module_parts=module_parts,
        importer_path=prompt_file.source_path,
        ancestry=ancestry,
        allow_parallel_imports=allow_parallel_imports,
    )

    return IndexedUnit(
        prompt_root=prompt_root,
        module_parts=module_parts,
        module_source_kind=module_source_kind,
        package_root=package_root,
        prompt_file=prompt_file,
        imports=tuple(imports),
        render_profiles_by_name=render_profiles_by_name,
        analyses_by_name=analyses_by_name,
        decisions_by_name=decisions_by_name,
        schemas_by_name=schemas_by_name,
        tables_by_name=tables_by_name,
        documents_by_name=documents_by_name,
        workflows_by_name=workflows_by_name,
        route_onlys_by_name=route_onlys_by_name,
        groundings_by_name=groundings_by_name,
        reviews_by_name=reviews_by_name,
        inputs_blocks_by_name=inputs_blocks_by_name,
        inputs_by_name=inputs_by_name,
        input_sources_by_name=input_sources_by_name,
        outputs_blocks_by_name=outputs_blocks_by_name,
        outputs_by_name=outputs_by_name,
        output_targets_by_name=output_targets_by_name,
        output_shapes_by_name=output_shapes_by_name,
        output_schemas_by_name=output_schemas_by_name,
        skills_by_name=skills_by_name,
        skill_packages_by_name=skill_packages_by_name,
        skill_packages_by_id=skill_packages_by_id,
        skills_blocks_by_name=skills_blocks_by_name,
        enums_by_name=enums_by_name,
        agents_by_name=agents_by_name,
        imported_units=loaded_imports.imported_units,
        visible_imported_units=loaded_imports.visible_imported_units,
        imported_symbols_by_name=loaded_imports.imported_symbols_by_name,
    )


def _visible_imported_module_parts(
    import_decl: model.ImportDecl,
    *,
    resolved_module_parts: tuple[str, ...],
) -> tuple[str, ...] | None:
    if import_decl.imported_name is not None:
        return None
    if import_decl.alias is not None:
        return (import_decl.alias,)
    return resolved_module_parts


def _import_display_name(
    import_decl: model.ImportDecl,
    *,
    resolved_module_parts: tuple[str, ...],
) -> str:
    if import_decl.imported_name is not None:
        visible_name = import_decl.alias or import_decl.imported_name
        return visible_name
    visible_module_parts = _visible_imported_module_parts(
        import_decl,
        resolved_module_parts=resolved_module_parts,
    )
    assert visible_module_parts is not None
    return ".".join(visible_module_parts)


def load_imports(
    session: "CompilationSession",
    imports: list[model.ImportDecl],
    *,
    prompt_root: Path,
    package_root: Path | None,
    module_parts: tuple[str, ...],
    importer_path: Path | None,
    ancestry: tuple[ModuleLoadKey, ...],
    allow_parallel_imports: bool,
) -> LoadedImports:
    imported_units: dict[tuple[str, ...], IndexedUnit] = {}
    visible_imported_units: dict[tuple[str, ...], IndexedUnit] = {}
    module_binding_decls: dict[tuple[str, ...], model.ImportDecl] = {}
    imported_symbols_by_name: dict[str, ImportedSymbolBinding] = {}
    if not imports:
        return LoadedImports(
            imported_units=imported_units,
            visible_imported_units=visible_imported_units,
            imported_symbols_by_name=imported_symbols_by_name,
        )

    resolved_imports = [
        (
            _resolve_import_path(
                import_decl,
                module_parts=module_parts,
                source_path=importer_path,
            ),
            import_decl,
        )
        for import_decl in imports
    ]
    # Import loading stays sequential. Parallel sibling loads can deadlock on
    # cyclic imports before ancestry-based cycle detection gets a chance to
    # surface the truthful E289 compile error.
    _ = allow_parallel_imports

    for resolved_module_parts, import_decl in resolved_imports:
        try:
            target_unit = load_module(
                session,
                resolved_module_parts,
                prompt_root=prompt_root if import_decl.path.level > 0 else None,
                package_import_root=package_root if import_decl.path.level == 0 else None,
                ancestry=ancestry,
                importer_path=importer_path,
                import_decl=import_decl,
            )
            imported_units[resolved_module_parts] = target_unit
        except DoctrineError as exc:
            raise exc.prepend_trace(
                f"resolve import `{'.'.join(resolved_module_parts)}`",
                location=path_location(importer_path),
            )
        visible_module_parts = _visible_imported_module_parts(
            import_decl,
            resolved_module_parts=resolved_module_parts,
        )
        if visible_module_parts is not None:
            existing_decl = module_binding_decls.get(visible_module_parts)
            if existing_decl is not None:
                existing_unit = visible_imported_units[visible_module_parts]
                same_visible_target = (
                    existing_unit.prompt_root == target_unit.prompt_root
                    and existing_unit.module_parts == target_unit.module_parts
                    and existing_decl.alias is None
                    and import_decl.alias is None
                )
                if not same_visible_target:
                    visible_name = ".".join(visible_module_parts)
                    raise compile_error(
                        code="E306",
                        summary="Duplicate module alias",
                        detail=(
                            f"Visible import module `{visible_name}` is defined more than once "
                            "in the same prompt file."
                        ),
                        path=importer_path,
                        source_span=import_decl.source_span,
                        related=(
                            related_prompt_site(
                                label="first import",
                                path=importer_path,
                                source_span=existing_decl.source_span,
                            ),
                        ),
                        hints=(
                            "Keep each visible import module name only once per prompt file.",
                            "Rename one import with `as` when both modules must stay visible.",
                        ),
                    )
            else:
                visible_imported_units[visible_module_parts] = target_unit
                module_binding_decls[visible_module_parts] = import_decl
            continue

        assert import_decl.imported_name is not None
        visible_name = import_decl.alias or import_decl.imported_name
        existing_binding = imported_symbols_by_name.get(visible_name)
        if existing_binding is not None:
            raise compile_error(
                code="E307",
                summary="Duplicate imported symbol",
                detail=(
                    f"Imported symbol `{visible_name}` is defined more than once in the "
                    "same prompt file."
                ),
                path=importer_path,
                source_span=import_decl.source_span,
                related=(
                    related_prompt_site(
                        label="first import",
                        path=importer_path,
                        source_span=existing_binding.import_decl.source_span,
                    ),
                ),
                hints=(
                    "Keep each imported symbol visible only once per prompt file.",
                    "Rename one symbol with `as` when both imports must stay visible.",
                ),
            )
        imported_symbols_by_name[visible_name] = ImportedSymbolBinding(
            target_name=import_decl.imported_name,
            target_unit=target_unit,
            import_decl=import_decl,
        )
    return LoadedImports(
        imported_units=imported_units,
        visible_imported_units=visible_imported_units,
        imported_symbols_by_name=imported_symbols_by_name,
    )


def load_module(
    session: "CompilationSession",
    module_parts: tuple[str, ...],
    *,
    prompt_root: Path | None,
    package_import_root: Path | None = None,
    ancestry: tuple[ModuleLoadKey, ...],
    importer_path: Path | None = None,
    import_decl: model.ImportDecl | None = None,
) -> IndexedUnit:
    resolved_source = resolve_module_source(
        session,
        module_parts,
        prompt_root=prompt_root,
        package_import_root=package_import_root,
        importer_path=importer_path,
        import_decl=import_decl,
    )
    module_key = _module_load_key(resolved_source.prompt_root, module_parts)
    cached = session._module_cache.get(module_key)
    if cached is not None:
        return cached
    if module_key in ancestry:
        raise compile_error(
            code="E289",
            summary="Cyclic import module",
            detail=f"Import cycle: {'.'.join(module_parts)}.",
            path=importer_path,
            source_span=None if import_decl is None else import_decl.source_span,
        )

    with session._module_lock:
        cached = session._module_cache.get(module_key)
        if cached is not None:
            return cached

        cached_error = session._module_load_errors.get(module_key)
        if cached_error is not None:
            if isinstance(cached_error, DoctrineError):
                raise _clone_doctrine_error(cached_error)
            raise cached_error

        ready = session._module_loading.get(module_key)
        if ready is None:
            ready = session._module_loading[module_key] = session._new_module_ready_event()
            is_loader = True
        else:
            is_loader = False

    if not is_loader:
        waiting_module = _waiting_module_key(ancestry)
        if waiting_module is not None:
            with session._module_lock:
                if _has_module_wait_cycle(
                    session,
                    waiting_module=waiting_module,
                    target_module=module_key,
                ):
                    raise compile_error(
                        code="E289",
                        summary="Cyclic import module",
                        detail=f"Import cycle: {'.'.join(module_parts)}.",
                        path=importer_path,
                        source_span=None if import_decl is None else import_decl.source_span,
                    )
                session._module_waits[waiting_module] = module_key
        try:
            ready.wait()
        finally:
            if waiting_module is not None:
                with session._module_lock:
                    if session._module_waits.get(waiting_module) == module_key:
                        session._module_waits.pop(waiting_module, None)
        with session._module_lock:
            cached = session._module_cache.get(module_key)
            if cached is not None:
                return cached
            cached_error = session._module_load_errors.get(module_key)
        if cached_error is None:
            raise compile_error(
                code="E901",
                summary="Internal compiler error",
                detail=(
                    "Internal compiler error: module load finished without a result: "
                    f"{'.'.join(module_parts)}"
                ),
                path=importer_path if importer_path is not None else resolved_source.prompt_path,
                source_span=None if import_decl is None else import_decl.source_span,
                hints=("This is a compiler bug, not a prompt authoring error.",),
            )
        if isinstance(cached_error, DoctrineError):
            raise _clone_doctrine_error(cached_error)
        raise cached_error

    module_path = resolved_source.prompt_path
    try:
        try:
            prompt_file = parse_file(module_path)
            indexed = index_unit(
                session,
                prompt_file,
                prompt_root=resolved_source.prompt_root,
                module_parts=module_parts,
                module_source_kind=resolved_source.module_source_kind,
                package_root=resolved_source.package_root,
                ancestry=(*ancestry, module_key),
                allow_parallel_imports=False,
            )
        except DoctrineError as exc:
            raise exc.prepend_trace(
                f"load import module `{'.'.join(module_parts)}`",
                location=path_location(module_path),
            ).ensure_location(path=module_path)
    except Exception as exc:
        with session._module_lock:
            if isinstance(exc, DoctrineError):
                session._module_load_errors[module_key] = _clone_doctrine_error(exc)
            else:
                session._module_load_errors[module_key] = exc
        raise
    else:
        with session._module_lock:
            session._module_cache[module_key] = indexed
        return indexed
    finally:
        with session._module_lock:
            ready = session._module_loading.pop(module_key, None)
        if ready is not None:
            ready.set()


def _searchable_import_roots(
    session: "CompilationSession",
    *,
    package_import_root: Path | None,
) -> tuple[tuple[Path, Path | None], ...]:
    candidate_roots: list[tuple[Path, Path | None]] = []
    seen_roots: set[Path] = set()

    if package_import_root is not None:
        resolved_package_root = package_import_root.resolve()
        candidate_roots.append((package_import_root, package_import_root))
        seen_roots.add(resolved_package_root)

    for candidate_root in session.import_roots:
        resolved_candidate_root = candidate_root.resolve()
        if resolved_candidate_root in seen_roots:
            continue
        candidate_roots.append((candidate_root, None))
        seen_roots.add(resolved_candidate_root)

    return tuple(candidate_roots)


def _import_root_label(
    session: "CompilationSession",
    prompt_root: Path,
    *,
    package_import_root: Path | None,
) -> str:
    resolved_root = prompt_root.resolve()
    if package_import_root is not None and resolved_root == package_import_root.resolve():
        if resolved_root not in session.import_root_labels:
            return f"skill package source root `{prompt_root}`"
    return session.import_root_labels.get(resolved_root, str(prompt_root))


def resolve_module_source(
    session: "CompilationSession",
    module_parts: tuple[str, ...],
    *,
    prompt_root: Path | None,
    package_import_root: Path | None = None,
    importer_path: Path | None = None,
    import_decl: model.ImportDecl | None = None,
) -> ResolvedModuleSource:
    if prompt_root is not None:
        resolved = _resolve_module_source_in_root(
            prompt_root,
            module_parts,
            importer_path=importer_path,
            import_source_span=None if import_decl is None else import_decl.source_span,
        )
        if resolved is not None:
            return resolved
        raise compile_error(
            code="E280",
            summary="Missing import module",
            detail=(
                f"Import module `{'.'.join(module_parts)}` could not be found in the active prompts roots."
            ),
            path=importer_path,
            source_span=None if import_decl is None else import_decl.source_span,
            hints=("Create the missing prompt file, or fix the import path.",),
        )

    matching_sources = tuple(
        resolved
        for candidate_root, file_module_package_root in _searchable_import_roots(
            session,
            package_import_root=package_import_root,
        )
        for resolved in (
            _resolve_module_source_in_root(
                candidate_root,
                module_parts,
                importer_path=importer_path,
                import_source_span=None if import_decl is None else import_decl.source_span,
                file_module_package_root=file_module_package_root,
            ),
        )
        if resolved is not None
    )
    if not matching_sources:
        raise compile_error(
            code="E280",
            summary="Missing import module",
            detail=(
                f"Import module `{'.'.join(module_parts)}` could not be found in the active prompts roots."
            ),
            path=importer_path,
            source_span=None if import_decl is None else import_decl.source_span,
            hints=("Create the missing prompt file, or fix the import path.",),
        )
    if len(matching_sources) > 1:
        root_list = ", ".join(
            _import_root_label(
                session,
                source.prompt_root,
                package_import_root=package_import_root,
            )
            for source in matching_sources
        )
        raise compile_error(
            code="E287",
            summary="Ambiguous import module",
            detail=(
                f"Import module `{'.'.join(module_parts)}` matches more than one active prompts root: "
                f"{root_list}."
            ),
            path=importer_path,
            source_span=None if import_decl is None else import_decl.source_span,
            hints=("Narrow the active prompts roots, or rename one of the colliding modules.",),
        )
    return matching_sources[0]


def resolve_module_root(
    session: "CompilationSession",
    module_parts: tuple[str, ...],
    *,
    prompt_root: Path | None,
) -> Path:
    return resolve_module_source(
        session,
        module_parts,
        prompt_root=prompt_root,
    ).prompt_root
