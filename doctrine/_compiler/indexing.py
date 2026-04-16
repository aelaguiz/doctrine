from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeAlias

import doctrine._model.declarations as model
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
    skills_blocks_by_name: dict[str, model.SkillsDecl]
    enums_by_name: dict[str, model.EnumDecl]
    agents_by_name: dict[str, model.Agent]
    imported_units: dict[tuple[str, ...], "IndexedUnit"]


def _clone_doctrine_error(error: DoctrineError) -> DoctrineError:
    return type(error)(diagnostic=error.diagnostic)


def _register_decl(
    registry: dict[str, object],
    name: str,
    module_parts: tuple[str, ...],
) -> None:
    if name in registry:
        dotted_name = ".".join((*module_parts, name)) or name
        raise CompileError(f"Duplicate declaration name: {dotted_name}")


def _validate_enum_decl(decl: model.EnumDecl, *, owner_label: str) -> None:
    seen_keys: set[str] = set()
    seen_wire_values: set[str] = set()
    for member in decl.members:
        if member.key in seen_keys:
            raise CompileError(f"Duplicate enum member key in {owner_label}: {member.key}")
        seen_keys.add(member.key)
        if member.value in seen_wire_values:
            raise CompileError(f"Duplicate enum member wire in {owner_label}: {member.value}")
        seen_wire_values.add(member.value)


def _validate_render_profile_decl(decl: model.RenderProfileDecl, *, owner_label: str) -> None:
    seen_targets: set[tuple[str, ...]] = set()
    for rule in decl.rules:
        target_text = ".".join(rule.target_parts)
        if target_text not in _KNOWN_RENDER_PROFILE_TARGETS:
            raise CompileError(f"Unknown render_profile target in {owner_label}: {target_text}")
        if rule.mode not in _KNOWN_RENDER_PROFILE_MODES:
            raise CompileError(f"Unknown render_profile mode in {owner_label}: {rule.mode}")
        allowed_modes = _RENDER_PROFILE_TARGET_MODE_CONSTRAINTS.get(target_text)
        if allowed_modes is not None and rule.mode not in allowed_modes:
            raise CompileError(
                "Invalid render_profile mode for "
                f"{target_text} in {owner_label}: {rule.mode}"
            )
        if rule.target_parts in seen_targets:
            raise CompileError(
                f"Duplicate render_profile rule target in {owner_label}: {target_text}"
            )
        seen_targets.add(rule.target_parts)


def _resolve_import_path(
    import_path: ImportPath, *, module_parts: tuple[str, ...]
) -> tuple[str, ...]:
    if import_path.level == 0:
        return import_path.module_parts

    current_package_parts = module_parts[:-1] if module_parts else ()
    parent_walk = import_path.level - 1
    package_parts = (
        current_package_parts[:-parent_walk] if parent_walk else current_package_parts
    )
    if parent_walk > len(current_package_parts):
        dotted_import = "." * import_path.level + ".".join(import_path.module_parts)
        raise CompileError(f"Relative import walks above prompts root: {dotted_import}")

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
) -> ResolvedModuleSource | None:
    file_module_path = _module_path_for_root(prompt_root, module_parts)
    runtime_package_path = _runtime_package_path_for_root(prompt_root, module_parts)
    has_file_module = file_module_path.is_file()
    has_runtime_package = runtime_package_path.is_file()

    if has_file_module and has_runtime_package:
        dotted_name = ".".join(module_parts)
        # Fail loud instead of guessing which module shape owns the dotted path.
        raise CompileError(
            "Ambiguous import module: "
            f"{dotted_name} (both `{_module_relpath_text(file_module_path, prompt_root=prompt_root)}` "
            f"and `{_module_relpath_text(runtime_package_path, prompt_root=prompt_root)}` exist "
            f"under prompts root `{prompt_root}`)"
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
            package_root=None,
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
    agents_by_name: dict[str, model.Agent] = {}
    enums_by_name: dict[str, model.EnumDecl] = {}

    for declaration in prompt_file.declarations:
        if isinstance(declaration, model.ImportDecl):
            imports.append(declaration)
            continue
        if isinstance(declaration, model.RenderProfileDecl):
            _register_decl(render_profiles_by_name, declaration.name, module_parts)
            _validate_render_profile_decl(
                declaration,
                owner_label=f"render_profile {dotted_decl_name(module_parts, declaration.name)}",
            )
            render_profiles_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.AnalysisDecl):
            _register_decl(analyses_by_name, declaration.name, module_parts)
            analyses_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.DecisionDecl):
            _register_decl(decisions_by_name, declaration.name, module_parts)
            decisions_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.SchemaDecl):
            _register_decl(schemas_by_name, declaration.name, module_parts)
            schemas_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.TableDecl):
            _register_decl(tables_by_name, declaration.name, module_parts)
            tables_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.DocumentDecl):
            _register_decl(documents_by_name, declaration.name, module_parts)
            documents_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.WorkflowDecl):
            _register_decl(workflows_by_name, declaration.name, module_parts)
            workflows_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.RouteOnlyDecl):
            _register_decl(route_onlys_by_name, declaration.name, module_parts)
            route_onlys_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.GroundingDecl):
            _register_decl(groundings_by_name, declaration.name, module_parts)
            groundings_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.ReviewDecl):
            _register_decl(reviews_by_name, declaration.name, module_parts)
            reviews_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.SkillsDecl):
            _register_decl(skills_blocks_by_name, declaration.name, module_parts)
            skills_blocks_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.InputsDecl):
            _register_decl(inputs_blocks_by_name, declaration.name, module_parts)
            inputs_blocks_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.InputDecl):
            _register_decl(inputs_by_name, declaration.name, module_parts)
            inputs_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.InputSourceDecl):
            _register_decl(input_sources_by_name, declaration.name, module_parts)
            input_sources_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.OutputsDecl):
            _register_decl(outputs_blocks_by_name, declaration.name, module_parts)
            outputs_blocks_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.OutputDecl):
            _register_decl(outputs_by_name, declaration.name, module_parts)
            outputs_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.OutputTargetDecl):
            _register_decl(output_targets_by_name, declaration.name, module_parts)
            output_targets_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.OutputShapeDecl):
            _register_decl(output_shapes_by_name, declaration.name, module_parts)
            output_shapes_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.OutputSchemaDecl):
            _register_decl(output_schemas_by_name, declaration.name, module_parts)
            output_schemas_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.SkillDecl):
            _register_decl(skills_by_name, declaration.name, module_parts)
            skills_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.SkillPackageDecl):
            _register_decl(skill_packages_by_name, declaration.name, module_parts)
            skill_packages_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.EnumDecl):
            _register_decl(enums_by_name, declaration.name, module_parts)
            _validate_enum_decl(
                declaration,
                owner_label=f"enum {dotted_decl_name(module_parts, declaration.name)}",
            )
            enums_by_name[declaration.name] = declaration
            continue
        if isinstance(declaration, model.Agent):
            _register_decl(agents_by_name, declaration.name, module_parts)
            agents_by_name[declaration.name] = declaration
            continue
        raise CompileError(f"Unsupported declaration type: {type(declaration).__name__}")

    imported_units = load_imports(
        session,
        imports,
        prompt_root=prompt_root,
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
        skills_blocks_by_name=skills_blocks_by_name,
        enums_by_name=enums_by_name,
        agents_by_name=agents_by_name,
        imported_units=imported_units,
    )


def load_imports(
    session: "CompilationSession",
    imports: list[model.ImportDecl],
    *,
    prompt_root: Path,
    module_parts: tuple[str, ...],
    importer_path: Path | None,
    ancestry: tuple[ModuleLoadKey, ...],
    allow_parallel_imports: bool,
) -> dict[tuple[str, ...], IndexedUnit]:
    imported_units: dict[tuple[str, ...], IndexedUnit] = {}
    if not imports:
        return imported_units

    resolved_imports = [
        (_resolve_import_path(import_decl.path, module_parts=module_parts), import_decl)
        for import_decl in imports
    ]
    # Import loading stays sequential. Parallel sibling loads can deadlock on
    # cyclic imports before ancestry-based cycle detection gets a chance to
    # surface the truthful E289 compile error.
    _ = allow_parallel_imports

    for resolved_module_parts, import_decl in resolved_imports:
        try:
            imported_units[resolved_module_parts] = load_module(
                session,
                resolved_module_parts,
                prompt_root=prompt_root if import_decl.path.level > 0 else None,
                ancestry=ancestry,
            )
        except DoctrineError as exc:
            raise exc.prepend_trace(
                f"resolve import `{'.'.join(resolved_module_parts)}`",
                location=path_location(importer_path),
            )
    return imported_units


def load_module(
    session: "CompilationSession",
    module_parts: tuple[str, ...],
    *,
    prompt_root: Path | None,
    ancestry: tuple[ModuleLoadKey, ...],
) -> IndexedUnit:
    resolved_source = resolve_module_source(
        session,
        module_parts,
        prompt_root=prompt_root,
    )
    module_key = _module_load_key(resolved_source.prompt_root, module_parts)
    cached = session._module_cache.get(module_key)
    if cached is not None:
        return cached
    if module_key in ancestry:
        raise CompileError(f"Cyclic import module: {'.'.join(module_parts)}")

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
                    raise CompileError(f"Cyclic import module: {'.'.join(module_parts)}")
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
            raise CompileError(
                f"Internal compiler error: module load finished without a result: {'.'.join(module_parts)}"
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


def resolve_module_source(
    session: "CompilationSession",
    module_parts: tuple[str, ...],
    *,
    prompt_root: Path | None,
) -> ResolvedModuleSource:
    if prompt_root is not None:
        resolved = _resolve_module_source_in_root(prompt_root, module_parts)
        if resolved is not None:
            return resolved
        raise CompileError(f"Missing import module: {'.'.join(module_parts)}")

    matching_sources = tuple(
        resolved
        for candidate_root in session.import_roots
        for resolved in (_resolve_module_source_in_root(candidate_root, module_parts),)
        if resolved is not None
    )
    if not matching_sources:
        raise CompileError(f"Missing import module: {'.'.join(module_parts)}")
    if len(matching_sources) > 1:
        root_list = ", ".join(str(source.prompt_root) for source in matching_sources)
        raise CompileError(
            f"Ambiguous import module: {'.'.join(module_parts)} (matching prompts roots: {root_list})"
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
