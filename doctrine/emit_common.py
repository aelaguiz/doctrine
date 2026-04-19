"""Shared emit plumbing for `emit_docs`, `emit_flow`, and `emit_skill`.

This module owns target resolution and the output-layout rules that all three
emitters share. The high-level story lives in `docs/EMIT_GUIDE.md`; these
docstrings pin the callable contract (inputs, outputs, error codes) so the
three emitters can rely on one canonical owner.

Key invariants held here:

- Emitted output for an entrypoint lands under
  `<target.output_dir>/<entrypoint_relative_dir(target.entrypoint)>`. The
  `prompts/` directory in the authored tree is the pivot.
- Only concrete agents emit. The walk in `collect_runtime_emit_roots` picks
  up concrete agents in the root flow plus first-seen imported runtime
  packages; file-module imports are traversed but never emit.
- Target entrypoints must be one of `SUPPORTED_ENTRYPOINTS`.
"""
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.indexing import unit_declarations, unit_loaded_imports
from doctrine._compiler.support import path_location
from doctrine.diagnostics import EmitError
from doctrine.project_config import (
    PYPROJECT_FILE_NAME,
    ProvidedPromptRoot,
    ProjectConfig,
    find_nearest_pyproject,
    load_project_config,
    load_project_config_for_source,
)

if TYPE_CHECKING:
    from doctrine._compiler.indexing import IndexedUnit
    from doctrine._compiler.resolve.field_types import FieldTypeRef
    from doctrine._compiler.session import CompilationSession

REPO_ROOT = Path(__file__).resolve().parent.parent
CAMEL_BOUNDARY_RE = re.compile(r"(?<!^)(?=[A-Z])")
DOCS_ENTRYPOINTS = ("AGENTS.prompt", "SOUL.prompt")
SKILL_ENTRYPOINTS = ("SKILL.prompt",)
SUPPORTED_ENTRYPOINTS = DOCS_ENTRYPOINTS + SKILL_ENTRYPOINTS


# Single rendering path for field vocabularies across all field-shaped surfaces.
def render_valid_values_line(type_ref: "FieldTypeRef | None") -> str | None:
    """Format the canonical `Valid values: ...` line for an enum-typed field.

    Returns `"Valid values: <k1>, <k2>, ..., <kn>."` when `type_ref` is an
    `EnumTypeRef`, drawing each member's declared key in declared order.
    Returns `None` for `BuiltinTypeRef` or `None`. This is the single
    rendering path for field vocabularies across every field-shaped
    surface (readable table columns, readable row_schema and item_schema
    entries, record scalars, output-schema fields).
    """
    from doctrine._compiler.resolve.field_types import EnumTypeRef

    if not isinstance(type_ref, EnumTypeRef):
        return None
    values = [member.key for member in type_ref.decl.members]
    if not values:
        return None
    rendered = ", ".join(values)
    return f"Valid values: {rendered}."


@dataclass(slots=True, frozen=True)
class EmitTarget:
    name: str
    entrypoint: Path
    output_dir: Path
    project_config: ProjectConfig


@dataclass(slots=True, frozen=True)
class RuntimeEmitRoot:
    unit: "IndexedUnit"
    agent_name: str


def _entrypoint_options_text(entrypoints: tuple[str, ...]) -> str:
    if len(entrypoints) == 1:
        return f"`{entrypoints[0]}`"
    if len(entrypoints) == 2:
        return f"`{entrypoints[0]}` or `{entrypoints[1]}`"
    quoted = ", ".join(f"`{value}`" for value in entrypoints[:-1])
    return f"{quoted}, or `{entrypoints[-1]}`"


def ensure_supported_entrypoint(
    entrypoint: Path,
    *,
    allowed_entrypoints: tuple[str, ...],
    owner_label: str,
) -> None:
    if entrypoint.name in allowed_entrypoints:
        return
    raise emit_error(
        "E510",
        "Emit target entrypoint must match the emitter surface",
        f"{owner_label} must point at {_entrypoint_options_text(allowed_entrypoints)}, got `{entrypoint.name}`.",
        location=path_location(entrypoint),
    )


def resolve_pyproject_path(
    pyproject_path: str | Path | None = None,
    *,
    start_dir: str | Path | None = None,
) -> Path:
    base_dir = (Path(start_dir) if start_dir is not None else Path.cwd()).resolve()

    if pyproject_path is not None:
        candidate = Path(pyproject_path)
        if not candidate.is_absolute():
            candidate = base_dir / candidate
        resolved = candidate.resolve()
        if resolved.name != PYPROJECT_FILE_NAME:
            raise emit_error(
                "E507",
                "Emit config path must point at pyproject.toml",
                f"Emit config must point at `pyproject.toml`, got `{resolved}`.",
                location=path_location(resolved),
            )
        if not resolved.is_file():
            raise emit_error(
                "E504",
                "Missing pyproject.toml",
                f"Missing `pyproject.toml`: `{resolved}`.",
                location=path_location(resolved),
            )
        return resolved

    resolved = find_nearest_pyproject(base_dir)
    if resolved is not None:
        return resolved

    raise emit_error(
        "E504",
        "Missing pyproject.toml",
        f"Could not find `pyproject.toml` in `{base_dir}` or any parent directory.",
        location=path_location(base_dir),
    )


def load_emit_targets(
    pyproject_path: str | Path | None = None,
    *,
    start_dir: str | Path | None = None,
    provided_prompt_roots: tuple[ProvidedPromptRoot, ...] = (),
) -> dict[str, EmitTarget]:
    """Load `[[tool.doctrine.emit.targets]]` from pyproject.toml.

    Returns a dict keyed by `name`. Each `EmitTarget` carries the resolved
    entrypoint path, output directory, and the loaded `ProjectConfig`.

    Validation and error codes:

    - E503 — pyproject.toml has no emit targets defined.
    - E504 — pyproject.toml is missing.
    - E507 — `pyproject_path` does not point at a `pyproject.toml` file.
    - E508 — a target entry is not a TOML table.
    - E509 — duplicate target name.
    - E510 — entrypoint basename is not in `SUPPORTED_ENTRYPOINTS`.
    - E511 — `output_dir` resolves to an existing file.
    - E512/E513 — entrypoint path or required string field is missing/invalid.
    - E520/E521 — `output_dir` or entrypoint falls outside the project root.

    `provided_prompt_roots` is caller-owned input passed through to
    `ProjectConfig`; it does not come from host TOML.
    """
    config_path = resolve_pyproject_path(pyproject_path, start_dir=start_dir)
    project_config = _load_emit_project_config(
        config_path,
        provided_prompt_roots=provided_prompt_roots,
    )
    emit = project_config.raw_emit if isinstance(project_config.raw_emit, dict) else {}
    raw_targets = emit.get("targets")
    if not isinstance(raw_targets, list) or not raw_targets:
        raise emit_error(
            "E503",
            "Missing emit targets",
            "The current `pyproject.toml` does not define any `[tool.doctrine.emit.targets]`.",
            location=path_location(config_path),
        )

    config_dir = config_path.parent
    targets: dict[str, EmitTarget] = {}
    for index, raw_target in enumerate(raw_targets, start=1):
        if not isinstance(raw_target, dict):
            raise emit_error(
                "E508",
                "Emit target must be a TOML table",
                f"Emit target #{index} must be a TOML table.",
                location=path_location(config_path),
            )

        name = require_str(raw_target, "name", label=f"emit target #{index}")
        if name in targets:
            raise emit_error(
                "E509",
                "Duplicate emit target name",
                f"Emit target `{name}` is defined more than once.",
                location=path_location(config_path),
            )

        entrypoint = resolve_config_file(
            config_dir,
            require_str(raw_target, "entrypoint", label=f"emit target {name}"),
            label=f"emit target {name} entrypoint",
        )
        _validate_entrypoint_within_project_root(
            entrypoint,
            project_root=project_config.config_dir,
            detail_prefix=f"Emit target `{name}` entrypoint",
        )
        ensure_supported_entrypoint(
            entrypoint,
            allowed_entrypoints=SUPPORTED_ENTRYPOINTS,
            owner_label=f"Emit target `{name}`",
        )

        output_dir = resolve_config_path(
            config_dir,
            require_str(raw_target, "output_dir", label=f"emit target {name}"),
        )
        if output_dir.is_file():
            raise emit_error(
                "E511",
                "Emit target output_dir is a file",
                f"Emit target `{name}` output_dir is a file: `{output_dir}`.",
                location=path_location(output_dir),
            )
        _validate_output_dir_within_project_root(
            output_dir,
            project_root=project_config.config_dir,
            detail_prefix=f"Emit target `{name}` output_dir",
        )

        targets[name] = EmitTarget(
            name=name,
            entrypoint=entrypoint,
            output_dir=output_dir,
            project_config=project_config,
        )

    return targets


def resolve_direct_emit_target(
    *,
    entrypoint: str | Path,
    output_dir: str | Path,
    pyproject_path: str | Path | None = None,
    start_dir: str | Path | None = None,
    name: str | None = None,
    allowed_entrypoints: tuple[str, ...] = SUPPORTED_ENTRYPOINTS,
    provided_prompt_roots: tuple[ProvidedPromptRoot, ...] = (),
) -> EmitTarget:
    """Build one `EmitTarget` from a bare entrypoint/output_dir pair.

    This is the CLI-direct path used when no `[tool.doctrine.emit.targets]`
    entry is available. Runs the same entrypoint, prompts-root, and
    project-root checks as `load_emit_targets` and raises the same E5xx
    codes on failure.

    If `pyproject_path` is omitted, the `ProjectConfig` is loaded from the
    nearest pyproject.toml found above `entrypoint`. `name` defaults to
    `entrypoint.stem.lower()` when not supplied.
    """
    base_dir = (Path(start_dir) if start_dir is not None else Path.cwd()).resolve()
    if pyproject_path is not None:
        config_path = resolve_pyproject_path(pyproject_path, start_dir=start_dir)
        config_dir = config_path.parent
        project_config = _load_emit_project_config(
            config_path,
            provided_prompt_roots=provided_prompt_roots,
        )
    else:
        config_dir = base_dir
        project_config = None

    entrypoint_path = resolve_config_file(
        config_dir,
        str(entrypoint),
        label="direct emit entrypoint",
    )
    ensure_supported_entrypoint(
        entrypoint_path,
        allowed_entrypoints=allowed_entrypoints,
        owner_label="Direct emit entrypoint",
    )

    # Reuse the same prompts-root validation the configured target path uses.
    entrypoint_relative_dir(entrypoint_path)

    output_dir_path = resolve_config_path(config_dir, str(output_dir))
    if output_dir_path.is_file():
        raise emit_error(
            "E511",
            "Emit target output_dir is a file",
            f"Direct emit output_dir is a file: `{output_dir_path}`.",
            location=path_location(output_dir_path),
        )

    if project_config is None:
        project_config = _load_compile_project_config_for_entrypoint(
            entrypoint_path,
            provided_prompt_roots=provided_prompt_roots,
        )
    _validate_output_dir_within_project_root(
        output_dir_path,
        project_root=project_config.config_dir,
        detail_prefix="Direct emit output_dir",
    )

    return EmitTarget(
        name=name or entrypoint_path.stem.lower(),
        entrypoint=entrypoint_path,
        output_dir=output_dir_path,
        project_config=project_config,
    )


def _load_emit_project_config(
    config_path: Path,
    *,
    provided_prompt_roots: tuple[ProvidedPromptRoot, ...] = (),
) -> ProjectConfig:
    try:
        return load_project_config(
            config_path,
            provided_prompt_roots=provided_prompt_roots,
        )
    except tomllib.TOMLDecodeError as exc:
        raise EmitError.from_toml_decode(path=config_path, exc=exc) from exc


def _load_compile_project_config_for_entrypoint(
    entrypoint_path: Path,
    *,
    provided_prompt_roots: tuple[ProvidedPromptRoot, ...] = (),
) -> ProjectConfig:
    try:
        return load_project_config_for_source(
            entrypoint_path,
            provided_prompt_roots=provided_prompt_roots,
        )
    except tomllib.TOMLDecodeError as exc:
        config_path = find_nearest_pyproject(entrypoint_path.parent)
        if config_path is None:
            raise
        raise EmitError.from_toml_decode(path=config_path, exc=exc) from exc


def collect_runtime_emit_roots(
    session: "CompilationSession",
) -> tuple[RuntimeEmitRoot, ...]:
    """Return the agents the three emitters should actually write.

    The result is, in order:

    1. Every concrete agent declared in the root flow itself.
    2. Every first-seen imported *runtime package* reached by walking
       imports in pre-order from the root flow. Each runtime package must
       define exactly one concrete agent — that agent is the package's
       emit root.

    Imports that resolve to ordinary file modules are walked (so their
    transitive runtime-package imports still surface) but do not themselves
    emit. Pre-order traversal keeps first-seen ordering stable so the three
    emitters agree on which package is responsible for a shared surface.

    Raises `CompileError` (E299) if an imported runtime package has zero or
    more than one concrete agent.
    """
    root_flow = session.root_flow
    roots = [
        RuntimeEmitRoot(
            unit=root_flow.declaration_owner_units_by_id[id(agent)],
            agent_name=agent_name,
        )
        for agent_name, agent in root_flow.agents_by_name.items()
        if not agent.abstract
    ]
    seen_flows: set[tuple[Path, Path]] = set()
    seen_runtime_packages: set[tuple[Path, Path]] = set()
    visited_units_by_flow: dict[tuple[Path, Path], set[Path | tuple[str, ...]]] = {}

    def walk(flow) -> None:
        flow_key = (flow.prompt_root, flow.flow_root)
        if flow_key in seen_flows:
            return
        seen_flows.add(flow_key)
        visited_units = visited_units_by_flow.setdefault(flow_key, set())

        def append_runtime_root(imported_flow) -> None:
            imported_key = (imported_flow.prompt_root, imported_flow.flow_root)
            if imported_key in seen_runtime_packages:
                return
            concrete_agents = tuple(
                agent.name
                for agent in imported_flow.agents_by_name.values()
                if not agent.abstract
            )
            if not concrete_agents:
                return
            if len(concrete_agents) != 1:
                dotted_name = ".".join(imported_flow.flow_parts)
                raise compile_error(
                    code="E299",
                    summary="Runtime package import must define one concrete agent",
                    detail=(
                        "Runtime package import must define exactly one concrete agent: "
                        f"{dotted_name or '<entrypoint>'}"
                    ),
                    path=imported_flow.entrypoint_path,
                )
            owner_unit = imported_flow.declaration_owner_units_by_id[
                id(imported_flow.agents_by_name[concrete_agents[0]])
            ]
            roots.append(
                RuntimeEmitRoot(
                    unit=owner_unit,
                    agent_name=concrete_agents[0],
                )
            )
            seen_runtime_packages.add(imported_key)

        def walk_unit(unit) -> None:
            unit_key: Path | tuple[str, ...]
            source_path = unit.prompt_file.source_path
            if source_path is None:
                unit_key = unit.module_parts
            else:
                unit_key = source_path.resolve()
            if unit_key in visited_units:
                return
            visited_units.add(unit_key)
            for imported_unit in unit_loaded_imports(unit).imported_units.values():
                imported_flow = session.flow_for_unit(imported_unit)
                imported_flow_key = (imported_flow.prompt_root, imported_flow.flow_root)
                if imported_flow_key == flow_key:
                    walk_unit(imported_unit)
                    continue
                if imported_flow.entrypoint_unit.module_source_kind == "runtime_package":
                    # Pre-order import traversal keeps runtime roots in first-seen
                    # graph order without asking the build handle to repeat imports.
                    append_runtime_root(imported_flow)
                walk(imported_flow)

        for unit in flow.units_by_path.values():
            walk_unit(unit)

    walk(root_flow)
    return tuple(roots)


def _unit_concrete_agent_names(unit: "IndexedUnit") -> tuple[str, ...]:
    return tuple(
        agent.name
        for agent in unit_declarations(unit).agents_by_name.values()
        if not agent.abstract
    )


def entrypoint_relative_dir(entrypoint: Path) -> Path:
    """Path below the nearest `prompts/` ancestor.

    Walks the parent chain of `entrypoint` and returns the path from the
    first ancestor named `prompts` down to the entrypoint's parent. Returns
    an empty `Path()` when the entrypoint sits directly inside `prompts/`.

    This is the pivot every emitter uses to layer output: emitted files for
    an entrypoint land under `<target.output_dir> / entrypoint_relative_dir(
    target.entrypoint)`, preserving the authored subtree below `prompts/`.

    Raises emit error E514 when no `prompts/` ancestor is found.
    """
    resolved = entrypoint.resolve()
    for candidate in [resolved.parent, *resolved.parents]:
        if candidate.name == "prompts":
            rel_dir = resolved.relative_to(candidate).parent
            return Path() if rel_dir == Path(".") else rel_dir
    raise emit_error(
        "E514",
        "Could not resolve prompts root",
        f"Could not resolve `prompts/` root for `{resolved}`.",
        location=path_location(resolved),
    )


def entrypoint_output_name(entrypoint: Path) -> str:
    return f"{entrypoint.stem}.md"


def _validate_output_dir_within_project_root(
    output_dir: Path,
    *,
    project_root: Path | None,
    detail_prefix: str,
) -> None:
    _validate_path_within_project_root(
        candidate_path=output_dir,
        project_root=project_root,
        detail_prefix=detail_prefix,
        code="E520",
        summary="Emit target output_dir must stay within project root",
    )


def _validate_entrypoint_within_project_root(
    entrypoint: Path,
    *,
    project_root: Path | None,
    detail_prefix: str,
) -> None:
    _validate_path_within_project_root(
        candidate_path=entrypoint,
        project_root=project_root,
        detail_prefix=detail_prefix,
        code="E521",
        summary="Emit target entrypoint must stay within project root",
    )


def _validate_path_within_project_root(
    *,
    candidate_path: Path,
    project_root: Path | None,
    detail_prefix: str,
    code: str,
    summary: str,
) -> None:
    if project_root is None:
        return

    resolved_candidate_path = candidate_path.resolve()
    resolved_project_root = project_root.resolve()
    try:
        resolved_candidate_path.relative_to(resolved_project_root)
    except ValueError as exc:
        raise emit_error(
            code,
            summary,
            f"{detail_prefix} resolves outside the target project root: "
            f"`{display_path(resolved_candidate_path)}` is not under "
            f"`{display_path(resolved_project_root)}`.",
            location=path_location(candidate_path),
        ) from exc


def name_slug(name: str) -> str:
    return CAMEL_BOUNDARY_RE.sub("_", name).lower()


def agent_slug(name: str) -> str:
    return name_slug(name)


def resolve_config_file(config_dir: Path, value: str, *, label: str) -> Path:
    path = resolve_config_path(config_dir, value)
    if not path.is_file():
        raise emit_error(
            "E512",
            "Emit config path does not exist",
            f"{label} does not exist: {value}",
            location=path_location(path),
        )
    return path


def resolve_config_path(config_dir: Path, value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = config_dir / candidate
    return candidate.resolve()


def require_str(raw: dict[str, object], key: str, *, label: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str):
        raise emit_error(
            "E513",
            "Emit config value must be a string",
            f"{label}.{key} must be a string.",
        )
    return value


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def emit_error(
    code: str,
    summary: str,
    detail: str,
    *,
    location: DiagnosticLocation | None = None,
    hints: tuple[str, ...] = (),
) -> EmitError:
    return EmitError.from_parts(
        code=code,
        summary=summary,
        detail=detail,
        location=location,
        hints=hints,
    )
