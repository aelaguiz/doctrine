from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeAlias
from weakref import WeakKeyDictionary

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

ModuleSourceKind: TypeAlias = Literal["entrypoint", "file_module", "runtime_package"]
FlowBoundaryKind: TypeAlias = Literal["agent_flow", "skill_flow"]
FlowLoadKey: TypeAlias = tuple[Path, Path]
_FLOW_ENTRYPOINT_FILENAMES: dict[str, FlowBoundaryKind] = {
    "AGENTS.prompt": "agent_flow",
    "SOUL.prompt": "agent_flow",
    "SKILL.prompt": "skill_flow",
}


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
class UnitDeclarations:
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


@dataclass(slots=True, frozen=True, eq=False, weakref_slot=True)
class IndexedUnit:
    prompt_root: Path
    module_parts: tuple[str, ...]
    module_source_kind: ModuleSourceKind
    package_root: Path | None
    prompt_file: model.PromptFile
    imports: tuple[model.ImportDecl, ...]
    exported_names: frozenset[str]


@dataclass(slots=True, frozen=True)
class LoadedImports:
    imported_units: dict[tuple[str, ...], IndexedUnit]
    visible_imported_units: dict[tuple[str, ...], IndexedUnit]
    imported_symbols_by_name: dict[str, ImportedSymbolBinding]


@dataclass(slots=True, frozen=True)
class IndexedFlow:
    prompt_root: Path
    flow_root: Path
    flow_parts: tuple[str, ...]
    entrypoint_path: Path
    boundary_kind: FlowBoundaryKind
    member_paths: tuple[Path, ...]
    entrypoint_unit: IndexedUnit
    units_by_path: dict[Path, IndexedUnit]
    units_by_module_parts: dict[tuple[str, ...], IndexedUnit]
    unit_declarations_by_path: dict[Path, UnitDeclarations]
    loaded_imports_by_path: dict[Path, "LoadedImports"]
    declaration_owner_units_by_id: dict[int, IndexedUnit]
    exported_names: frozenset[str]
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


_FLOW_OWNER_BY_UNIT: WeakKeyDictionary[IndexedUnit, IndexedFlow] = WeakKeyDictionary()
_STANDALONE_DECLARATIONS_BY_UNIT: WeakKeyDictionary[IndexedUnit, UnitDeclarations] = (
    WeakKeyDictionary()
)
_STANDALONE_LOADED_IMPORTS_BY_UNIT: WeakKeyDictionary[IndexedUnit, "LoadedImports"] = (
    WeakKeyDictionary()
)


def _unit_source_path(unit: IndexedUnit) -> Path | None:
    source_path = unit.prompt_file.source_path
    if source_path is None:
        return None
    return source_path.resolve()


def _register_unit_state(
    unit: IndexedUnit,
    *,
    declarations: UnitDeclarations,
    loaded_imports: "LoadedImports",
) -> None:
    _STANDALONE_DECLARATIONS_BY_UNIT[unit] = declarations
    _STANDALONE_LOADED_IMPORTS_BY_UNIT[unit] = loaded_imports


def _register_flow_owner(flow: IndexedFlow) -> None:
    for unit in flow.units_by_path.values():
        _FLOW_OWNER_BY_UNIT[unit] = flow
        _STANDALONE_DECLARATIONS_BY_UNIT.pop(unit, None)
        _STANDALONE_LOADED_IMPORTS_BY_UNIT.pop(unit, None)


def unit_declarations(unit: IndexedUnit) -> UnitDeclarations:
    owner_flow = _FLOW_OWNER_BY_UNIT.get(unit)
    source_path = _unit_source_path(unit)
    if owner_flow is not None and source_path is not None:
        declarations = owner_flow.unit_declarations_by_path.get(source_path)
        if declarations is not None:
            return declarations
    declarations = _STANDALONE_DECLARATIONS_BY_UNIT.get(unit)
    if declarations is not None:
        return declarations
    raise compile_error(
        code="E901",
        summary="Internal compiler error",
        detail="Internal compiler error: missing indexed unit declarations.",
        path=source_path,
        hints=("This is a compiler bug, not a prompt authoring error.",),
    )


def unit_loaded_imports(unit: IndexedUnit) -> "LoadedImports":
    owner_flow = _FLOW_OWNER_BY_UNIT.get(unit)
    source_path = _unit_source_path(unit)
    if owner_flow is not None and source_path is not None:
        loaded_imports = owner_flow.loaded_imports_by_path.get(source_path)
        if loaded_imports is not None:
            return loaded_imports
    loaded_imports = _STANDALONE_LOADED_IMPORTS_BY_UNIT.get(unit)
    if loaded_imports is not None:
        return loaded_imports
    raise compile_error(
        code="E901",
        summary="Internal compiler error",
        detail="Internal compiler error: missing indexed unit import state.",
        path=source_path,
        hints=("This is a compiler bug, not a prompt authoring error.",),
    )


def flow_boundary_kind_for_path(path: Path) -> FlowBoundaryKind | None:
    return _FLOW_ENTRYPOINT_FILENAMES.get(path.name)


def resolve_flow_entrypoint(source_path: Path, *, prompt_root: Path | None = None) -> Path:
    resolved = source_path.resolve()
    boundary_kind = flow_boundary_kind_for_path(resolved)
    if boundary_kind is not None:
        if prompt_root is not None:
            resolved_prompt_root = prompt_root.resolve()
            try:
                resolved.relative_to(resolved_prompt_root)
            except ValueError:
                pass
            else:
                return resolved
        else:
            return resolved
    resolved_prompt_root = None if prompt_root is None else prompt_root.resolve()
    search_roots = (resolved.parent, *resolved.parents) if resolved.is_file() else (resolved, *resolved.parents)
    for candidate in search_roots:
        if resolved_prompt_root is not None:
            try:
                candidate.relative_to(resolved_prompt_root)
            except ValueError:
                continue
        for entrypoint_name in _FLOW_ENTRYPOINT_FILENAMES:
            entrypoint_path = candidate / entrypoint_name
            if entrypoint_path.is_file():
                return entrypoint_path
    raise compile_error(
        code="E292",
        summary="Could not resolve flow root",
        detail=f"Could not resolve a flow entrypoint for {resolved}.",
        path=resolved,
    )


def _is_hidden_path(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def _is_editor_backup(path: Path) -> bool:
    return (
        path.name.endswith("~")
        or path.name.endswith(".bak")
        or path.name.endswith(".swp")
        or path.name.endswith(".tmp")
    )


def discover_flow_members(
    flow_root: Path,
    *,
    entrypoint_path: Path | None = None,
) -> tuple[Path, ...]:
    flow_root = flow_root.resolve()
    resolved_entrypoint = None if entrypoint_path is None else entrypoint_path.resolve()
    member_paths: list[Path] = []
    for path in sorted(flow_root.rglob("*.prompt")):
        if path.is_symlink():
            continue
        relative_path = path.relative_to(flow_root)
        if _is_hidden_path(relative_path) or _is_editor_backup(path):
            continue
        if (
            resolved_entrypoint is not None
            and path.name in _FLOW_ENTRYPOINT_FILENAMES
            and path.resolve() != resolved_entrypoint
        ):
            continue
        if relative_path != Path(path.name):
            parent_parts = relative_path.parts[:-1]
            nested_flow = False
            for depth in range(1, len(parent_parts) + 1):
                candidate_dir = flow_root.joinpath(*parent_parts[:depth])
                if any(
                    (candidate_dir / entrypoint_name).is_file()
                    for entrypoint_name in _FLOW_ENTRYPOINT_FILENAMES
                ):
                    nested_flow = True
                    break
            if nested_flow:
                continue
        member_paths.append(path.resolve())
    return tuple(member_paths)


def _module_parts_for_prompt_path(prompt_root: Path, prompt_path: Path) -> tuple[str, ...]:
    resolved_prompt_root = prompt_root.resolve()
    resolved_prompt_path = prompt_path.resolve()
    relative_path = resolved_prompt_path.relative_to(resolved_prompt_root)
    if resolved_prompt_path.name in _FLOW_ENTRYPOINT_FILENAMES:
        return relative_path.parent.parts
    return relative_path.with_suffix("").parts


def _flow_module_source_kind(
    *,
    prompt_path: Path,
    entrypoint_path: Path,
    entrypoint_module_source_kind: ModuleSourceKind,
) -> ModuleSourceKind:
    if prompt_path.resolve() == entrypoint_path.resolve():
        return entrypoint_module_source_kind
    return "file_module"


def _flow_package_root(
    *,
    flow_root: Path,
    boundary_kind: FlowBoundaryKind,
    entrypoint_module_source_kind: ModuleSourceKind,
) -> Path | None:
    if boundary_kind == "skill_flow" or entrypoint_module_source_kind == "runtime_package":
        return flow_root
    return None


def _register_flow_registry(
    registry: dict[str, object],
    unit_registry: dict[str, object],
    *,
    owner_unit: IndexedUnit,
    declaration_owner_units_by_id: dict[int, IndexedUnit],
    flow_parts: tuple[str, ...],
    source_path: Path | None,
) -> None:
    for name, declaration in unit_registry.items():
        existing = registry.get(name)
        if existing is not None:
            existing_owner_unit = declaration_owner_units_by_id.get(id(existing))
            existing_owner_path = (
                None
                if existing_owner_unit is None
                else existing_owner_unit.prompt_file.source_path
            )
            if (
                existing_owner_path is not None
                and source_path is not None
                and existing_owner_path.resolve() != source_path.resolve()
            ):
                flow_label = ".".join(flow_parts) or "the root flow"
                raise compile_error(
                    code="E316",
                    summary="Sibling declaration collision",
                    detail=(
                        f"Declaration `{name}` is defined more than once in flow "
                        f"`{flow_label}` across sibling prompt files."
                    ),
                    path=source_path,
                    source_span=getattr(declaration, "source_span", None),
                    related=(
                        related_prompt_site(
                            label="first declaration",
                            path=existing_owner_path,
                            source_span=getattr(existing, "source_span", None),
                        ),
                    ),
                    hints=(
                        "Keep one declaration name per flow, or rename one sibling declaration.",
                    ),
                )
        _register_decl(
            registry,
            declaration,
            name,
            flow_parts,
            source_path=source_path,
        )
        registry[name] = declaration
        declaration_owner_units_by_id[id(declaration)] = owner_unit


def lookup_flow_registry_decl(
    flow: IndexedFlow,
    *,
    registry_name: str,
    declaration_name: str,
) -> tuple[IndexedUnit, object] | None:
    registry = getattr(flow, registry_name)
    declaration = registry.get(declaration_name)
    if declaration is None:
        return None
    owner_unit = flow.declaration_owner_units_by_id[id(declaration)]
    return owner_unit, declaration


def _empty_loaded_imports() -> LoadedImports:
    return LoadedImports(
        imported_units={},
        visible_imported_units={},
        imported_symbols_by_name={},
    )


def _raise_same_flow_import_retired(
    import_decl: model.ImportDecl,
    *,
    importer_path: Path | None,
    target_path: Path | None,
    resolved_module_parts: tuple[str, ...],
    flow_parts: tuple[str, ...],
) -> None:
    dotted_name = ".".join(resolved_module_parts)
    flow_label = ".".join(flow_parts) or "the root flow"
    raise compile_error(
        code="E315",
        summary="Same-flow import retired",
        detail=(
            f"Import `{dotted_name}` stays inside flow `{flow_label}`. "
            "Sibling prompt files already share one flat namespace."
        ),
        path=importer_path,
        source_span=import_decl.source_span,
        related=(
            file_scoped_related(
                label="same-flow member",
                path=target_path,
            ),
        ),
        hints=(
            "Delete the import and use the declaration by bare name inside the flow.",
            "Keep `import` only for real cross-flow boundaries.",
        ),
    )


def _raise_duplicate_import_name(
    import_decl: model.ImportDecl,
    *,
    importer_path: Path | None,
    existing_import_decl: model.ImportDecl,
    visible_name: str,
) -> None:
    raise compile_error(
        code="E307",
        summary="Duplicate imported name",
        detail=(
            f"Imported name `{visible_name}` is defined more than once in the same "
            "prompt file."
        ),
        path=importer_path,
        source_span=import_decl.source_span,
        related=(
            related_prompt_site(
                label="first import",
                path=importer_path,
                source_span=existing_import_decl.source_span,
            ),
        ),
        hints=(
            "Keep each imported name visible only once per prompt file.",
            "Rename one import with `as` when both flows or symbols must stay visible.",
        ),
    )


def _rebind_unit_to_flow(
    target_unit: IndexedUnit,
    *,
    flow_units_by_module_parts: dict[tuple[str, ...], IndexedUnit],
) -> IndexedUnit:
    rebound_unit = flow_units_by_module_parts.get(target_unit.module_parts)
    if rebound_unit is None:
        return target_unit
    if rebound_unit.prompt_root != target_unit.prompt_root:
        return target_unit
    return rebound_unit


def _rebind_loaded_imports_to_flow(
    loaded_imports: LoadedImports,
    *,
    flow_units_by_module_parts: dict[tuple[str, ...], IndexedUnit],
) -> LoadedImports:
    imported_units = {
        module_parts: _rebind_unit_to_flow(
            target_unit,
            flow_units_by_module_parts=flow_units_by_module_parts,
        )
        for module_parts, target_unit in loaded_imports.imported_units.items()
    }
    visible_imported_units = {
        module_parts: _rebind_unit_to_flow(
            target_unit,
            flow_units_by_module_parts=flow_units_by_module_parts,
        )
        for module_parts, target_unit in loaded_imports.visible_imported_units.items()
    }
    imported_symbols_by_name = {
        name: ImportedSymbolBinding(
            target_name=binding.target_name,
            target_unit=_rebind_unit_to_flow(
                binding.target_unit,
                flow_units_by_module_parts=flow_units_by_module_parts,
            ),
            import_decl=binding.import_decl,
        )
        for name, binding in loaded_imports.imported_symbols_by_name.items()
    }
    return LoadedImports(
        imported_units=imported_units,
        visible_imported_units=visible_imported_units,
        imported_symbols_by_name=imported_symbols_by_name,
    )


def build_indexed_flow(
    *,
    prompt_root: Path,
    entrypoint_path: Path,
    session: "CompilationSession" | None = None,
    ancestry: tuple[FlowLoadKey, ...] = (),
    entrypoint_module_source_kind: ModuleSourceKind = "entrypoint",
    prompt_file_overrides: dict[Path, model.PromptFile] | None = None,
) -> IndexedFlow:
    resolved_entrypoint = entrypoint_path.resolve()
    boundary_kind = flow_boundary_kind_for_path(resolved_entrypoint)
    assert boundary_kind is not None
    resolved_prompt_root = prompt_root.resolve()
    flow_root = resolved_entrypoint.parent.resolve()
    flow_parts = flow_root.relative_to(resolved_prompt_root).parts
    package_root = _flow_package_root(
        flow_root=flow_root,
        boundary_kind=boundary_kind,
        entrypoint_module_source_kind=entrypoint_module_source_kind,
    )
    member_paths = discover_flow_members(
        flow_root,
        entrypoint_path=resolved_entrypoint,
    )

    units_by_path: dict[Path, IndexedUnit] = {}
    units_by_module_parts: dict[tuple[str, ...], IndexedUnit] = {}
    entrypoint_unit: IndexedUnit | None = None
    declaration_owner_units_by_id: dict[int, IndexedUnit] = {}
    exported_names: set[str] = set()

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
    skills_blocks_by_name: dict[str, model.SkillsDecl] = {}
    enums_by_name: dict[str, model.EnumDecl] = {}
    agents_by_name: dict[str, model.Agent] = {}
    resolved_overrides = (
        None
        if prompt_file_overrides is None
        else {path.resolve(): prompt_file for path, prompt_file in prompt_file_overrides.items()}
    )

    for member_path in member_paths:
        if resolved_overrides is None:
            prompt_file = parse_file(member_path)
        else:
            prompt_file = resolved_overrides.get(member_path.resolve())
            if prompt_file is None:
                prompt_file = parse_file(member_path)
        module_parts = _module_parts_for_prompt_path(prompt_root, member_path)
        indexed_unit = index_unit(
            session,
            prompt_file,
            prompt_root=prompt_root,
            module_parts=module_parts,
            module_source_kind=_flow_module_source_kind(
                prompt_path=member_path,
                entrypoint_path=resolved_entrypoint,
                entrypoint_module_source_kind=entrypoint_module_source_kind,
            ),
            package_root=package_root,
            ancestry=(),
            allow_parallel_imports=False,
            resolve_imports=False,
        )
        units_by_path[member_path.resolve()] = indexed_unit
        units_by_module_parts[module_parts] = indexed_unit
        exported_names.update(indexed_unit.exported_names)
        if member_path.resolve() == resolved_entrypoint:
            entrypoint_unit = indexed_unit
        declarations = unit_declarations(indexed_unit)

        _register_flow_registry(
            render_profiles_by_name,
            declarations.render_profiles_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            analyses_by_name,
            declarations.analyses_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            decisions_by_name,
            declarations.decisions_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            schemas_by_name,
            declarations.schemas_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            tables_by_name,
            declarations.tables_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            documents_by_name,
            declarations.documents_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            workflows_by_name,
            declarations.workflows_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            route_onlys_by_name,
            declarations.route_onlys_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            groundings_by_name,
            declarations.groundings_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            reviews_by_name,
            declarations.reviews_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            inputs_blocks_by_name,
            declarations.inputs_blocks_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            inputs_by_name,
            declarations.inputs_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            input_sources_by_name,
            declarations.input_sources_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            outputs_blocks_by_name,
            declarations.outputs_blocks_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            outputs_by_name,
            declarations.outputs_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            output_targets_by_name,
            declarations.output_targets_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            output_shapes_by_name,
            declarations.output_shapes_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            output_schemas_by_name,
            declarations.output_schemas_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            skills_by_name,
            declarations.skills_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            skills_blocks_by_name,
            declarations.skills_blocks_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            skill_packages_by_name,
            declarations.skill_packages_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        for declaration in declarations.skill_packages_by_name.values():
            _register_skill_package_id(
                skill_packages_by_id,
                declaration,
                module_parts=flow_parts,
                source_path=member_path,
            )
        _register_flow_registry(
            enums_by_name,
            declarations.enums_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )
        _register_flow_registry(
            agents_by_name,
            declarations.agents_by_name,
            owner_unit=indexed_unit,
            declaration_owner_units_by_id=declaration_owner_units_by_id,
            flow_parts=flow_parts,
            source_path=member_path,
        )

    assert entrypoint_unit is not None
    unit_declarations_by_path = {
        member_path: unit_declarations(indexed_unit)
        for member_path, indexed_unit in units_by_path.items()
    }
    loaded_imports_by_path = {
        member_path: unit_loaded_imports(indexed_unit)
        for member_path, indexed_unit in units_by_path.items()
    }
    indexed_flow = IndexedFlow(
        prompt_root=prompt_root,
        flow_root=flow_root,
        flow_parts=flow_parts,
        entrypoint_path=resolved_entrypoint,
        boundary_kind=boundary_kind,
        member_paths=member_paths,
        entrypoint_unit=entrypoint_unit,
        units_by_path=units_by_path,
        units_by_module_parts=units_by_module_parts,
        unit_declarations_by_path=unit_declarations_by_path,
        loaded_imports_by_path=loaded_imports_by_path,
        declaration_owner_units_by_id=declaration_owner_units_by_id,
        exported_names=frozenset(exported_names),
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
    )
    _register_flow_owner(indexed_flow)
    if session is None:
        return indexed_flow

    rebound_loaded_imports_by_path: dict[Path, LoadedImports] = {}
    for member_path, indexed_unit in units_by_path.items():
        rebound_loaded_imports_by_path[member_path] = _rebind_loaded_imports_to_flow(
            load_imports(
                session,
                list(indexed_unit.imports),
                prompt_root=indexed_unit.prompt_root,
                package_root=indexed_unit.package_root,
                module_parts=indexed_unit.module_parts,
                importer_path=indexed_unit.prompt_file.source_path,
                ancestry=ancestry,
                allow_parallel_imports=False,
                current_flow=indexed_flow,
            ),
            flow_units_by_module_parts=units_by_module_parts,
        )

    indexed_flow = replace(
        indexed_flow,
        loaded_imports_by_path=rebound_loaded_imports_by_path,
    )
    _register_flow_owner(indexed_flow)
    return indexed_flow


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


def _flow_load_key(prompt_root: Path, flow_root: Path) -> FlowLoadKey:
    return (prompt_root.resolve(), flow_root.resolve())


def _waiting_flow_key(ancestry: tuple[FlowLoadKey, ...]) -> FlowLoadKey | None:
    if not ancestry:
        return None
    return ancestry[-1]


def _has_flow_wait_cycle(
    session: "CompilationSession",
    *,
    waiting_flow: FlowLoadKey,
    target_flow: FlowLoadKey,
) -> bool:
    current = target_flow
    seen: set[FlowLoadKey] = set()
    while current is not None:
        if current == waiting_flow:
            return True
        if current in seen:
            return False
        seen.add(current)
        current = session._flow_waits.get(current)
    return False


def index_unit(
    session: "CompilationSession" | None,
    prompt_file: model.PromptFile,
    *,
    prompt_root: Path,
    module_parts: tuple[str, ...],
    module_source_kind: ModuleSourceKind,
    package_root: Path | None,
    ancestry: tuple[FlowLoadKey, ...],
    allow_parallel_imports: bool,
    resolve_imports: bool = True,
) -> IndexedUnit:
    imports: list[model.ImportDecl] = []
    exported_names = frozenset(prompt_file.exported_names)
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

    if resolve_imports:
        assert session is not None
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
    else:
        loaded_imports = _empty_loaded_imports()

    indexed_unit = IndexedUnit(
        prompt_root=prompt_root,
        module_parts=module_parts,
        module_source_kind=module_source_kind,
        package_root=package_root,
        prompt_file=prompt_file,
        imports=tuple(imports),
        exported_names=exported_names,
    )
    _register_unit_state(
        indexed_unit,
        declarations=UnitDeclarations(
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
        ),
        loaded_imports=loaded_imports,
    )
    return indexed_unit


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
    ancestry: tuple[FlowLoadKey, ...],
    allow_parallel_imports: bool,
    current_flow: IndexedFlow | None = None,
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
            if current_flow is not None:
                resolved_source = resolve_module_source(
                    session,
                    resolved_module_parts,
                    prompt_root=prompt_root if import_decl.path.level > 0 else None,
                    package_import_root=package_root if import_decl.path.level == 0 else None,
                    importer_path=importer_path,
                    import_decl=import_decl,
                )
                same_flow_unit = current_flow.units_by_module_parts.get(resolved_module_parts)
                if (
                    same_flow_unit is not None
                    and same_flow_unit.prompt_file.source_path is not None
                    and same_flow_unit.prompt_file.source_path.resolve()
                    == resolved_source.prompt_path.resolve()
                ):
                    _raise_same_flow_import_retired(
                        import_decl,
                        importer_path=importer_path,
                        target_path=same_flow_unit.prompt_file.source_path,
                        resolved_module_parts=resolved_module_parts,
                        flow_parts=current_flow.flow_parts,
                    )
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
                    _raise_duplicate_import_name(
                        import_decl,
                        importer_path=importer_path,
                        existing_import_decl=existing_decl,
                        visible_name=visible_name,
                    )
            else:
                visible_imported_units[visible_module_parts] = target_unit
                module_binding_decls[visible_module_parts] = import_decl
            continue

        assert import_decl.imported_name is not None
        visible_name = import_decl.alias or import_decl.imported_name
        existing_binding = imported_symbols_by_name.get(visible_name)
        if existing_binding is not None:
            _raise_duplicate_import_name(
                import_decl,
                importer_path=importer_path,
                existing_import_decl=existing_binding.import_decl,
                visible_name=visible_name,
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
    ancestry: tuple[FlowLoadKey, ...],
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
    indexed_flow = load_flow(
        session,
        source_path=resolved_source.prompt_path,
        prompt_root=resolved_source.prompt_root,
        ancestry=ancestry,
        importer_path=importer_path,
        import_decl=import_decl,
        entrypoint_module_source_kind=resolved_source.module_source_kind,
    )
    cached = indexed_flow.units_by_module_parts.get(module_parts)
    if cached is not None:
        return cached
    raise compile_error(
        code="E280",
        summary="Missing import module",
        detail=(
            f"Import module `{'.'.join(module_parts)}` is not a member of flow "
            f"`{indexed_flow.flow_root}`."
        ),
        path=importer_path if importer_path is not None else resolved_source.prompt_path,
        source_span=None if import_decl is None else import_decl.source_span,
        hints=("Create the missing prompt file, or fix the import path.",),
    )


def load_flow(
    session: "CompilationSession",
    *,
    source_path: Path,
    prompt_root: Path,
    ancestry: tuple[FlowLoadKey, ...],
    importer_path: Path | None = None,
    import_decl: model.ImportDecl | None = None,
    entrypoint_module_source_kind: ModuleSourceKind = "entrypoint",
) -> IndexedFlow:
    resolved_prompt_root = prompt_root.resolve()
    entrypoint_path = resolve_flow_entrypoint(source_path, prompt_root=resolved_prompt_root)
    flow_root = entrypoint_path.parent.resolve()
    flow_key = _flow_load_key(resolved_prompt_root, flow_root)
    cached = session._flow_cache.get(flow_key)
    if cached is not None:
        return cached
    if flow_key in ancestry:
        raise compile_error(
            code="E289",
            summary="Cyclic import module",
            detail=(
                "Import cycle: "
                f"{'.'.join(source_path.resolve().relative_to(resolved_prompt_root).with_suffix('').parts)}."
            ),
            path=importer_path,
            source_span=None if import_decl is None else import_decl.source_span,
        )

    with session._flow_lock:
        cached = session._flow_cache.get(flow_key)
        if cached is not None:
            return cached

        cached_error = session._flow_load_errors.get(flow_key)
        if cached_error is not None:
            if isinstance(cached_error, DoctrineError):
                raise _clone_doctrine_error(cached_error)
            raise cached_error

        ready = session._flow_loading.get(flow_key)
        if ready is None:
            ready = session._flow_loading[flow_key] = session._new_flow_ready_event()
            is_loader = True
        else:
            is_loader = False

    if not is_loader:
        waiting_flow = _waiting_flow_key(ancestry)
        if waiting_flow is not None:
            with session._flow_lock:
                if _has_flow_wait_cycle(
                    session,
                    waiting_flow=waiting_flow,
                    target_flow=flow_key,
                ):
                    raise compile_error(
                        code="E289",
                        summary="Cyclic import module",
                        detail=(
                            "Import cycle: "
                            f"{'.'.join(source_path.resolve().relative_to(resolved_prompt_root).with_suffix('').parts)}."
                        ),
                        path=importer_path,
                        source_span=None if import_decl is None else import_decl.source_span,
                    )
                session._flow_waits[waiting_flow] = flow_key
        try:
            ready.wait()
        finally:
            if waiting_flow is not None:
                with session._flow_lock:
                    if session._flow_waits.get(waiting_flow) == flow_key:
                        session._flow_waits.pop(waiting_flow, None)
        with session._flow_lock:
            cached = session._flow_cache.get(flow_key)
            if cached is not None:
                return cached
            cached_error = session._flow_load_errors.get(flow_key)
        if cached_error is None:
            raise compile_error(
                code="E901",
                summary="Internal compiler error",
                detail=(
                    "Internal compiler error: flow load finished without a result: "
                    f"{entrypoint_path}"
                ),
                path=importer_path if importer_path is not None else entrypoint_path,
                source_span=None if import_decl is None else import_decl.source_span,
                hints=("This is a compiler bug, not a prompt authoring error.",),
            )
        if isinstance(cached_error, DoctrineError):
            raise _clone_doctrine_error(cached_error)
        raise cached_error

    try:
        try:
            indexed_flow = build_indexed_flow(
                prompt_root=resolved_prompt_root,
                entrypoint_path=entrypoint_path,
                session=session,
                ancestry=(*ancestry, flow_key),
                entrypoint_module_source_kind=entrypoint_module_source_kind,
            )
        except DoctrineError as exc:
            raise exc.prepend_trace(
                f"load flow `{entrypoint_path.parent.name}`",
                location=path_location(entrypoint_path),
            ).ensure_location(path=entrypoint_path)
    except Exception as exc:
        with session._flow_lock:
            if isinstance(exc, DoctrineError):
                session._flow_load_errors[flow_key] = _clone_doctrine_error(exc)
            else:
                session._flow_load_errors[flow_key] = exc
        raise
    else:
        with session._flow_lock:
            session._flow_cache[flow_key] = indexed_flow
        return indexed_flow
    finally:
        with session._flow_lock:
            ready = session._flow_loading.pop(flow_key, None)
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
