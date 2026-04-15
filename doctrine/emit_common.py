from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from doctrine._compiler.support import path_location
from doctrine.diagnostics import CompileError, EmitError
from doctrine.project_config import (
    PYPROJECT_FILE_NAME,
    ProjectConfig,
    find_nearest_pyproject,
    load_project_config,
    load_project_config_for_source,
)

if TYPE_CHECKING:
    from doctrine._compiler.indexing import IndexedUnit
    from doctrine._compiler.session import CompilationSession

REPO_ROOT = Path(__file__).resolve().parent.parent
CAMEL_BOUNDARY_RE = re.compile(r"(?<!^)(?=[A-Z])")
DOCS_ENTRYPOINTS = ("AGENTS.prompt", "SOUL.prompt")
SKILL_ENTRYPOINTS = ("SKILL.prompt",)
SUPPORTED_ENTRYPOINTS = DOCS_ENTRYPOINTS + SKILL_ENTRYPOINTS


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
) -> dict[str, EmitTarget]:
    config_path = resolve_pyproject_path(pyproject_path, start_dir=start_dir)
    project_config = _load_emit_project_config(config_path)
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
) -> EmitTarget:
    base_dir = (Path(start_dir) if start_dir is not None else Path.cwd()).resolve()
    if pyproject_path is not None:
        config_path = resolve_pyproject_path(pyproject_path, start_dir=start_dir)
        config_dir = config_path.parent
        project_config = _load_emit_project_config(config_path)
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
        project_config = _load_compile_project_config_for_entrypoint(entrypoint_path)
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


def _load_emit_project_config(config_path: Path) -> ProjectConfig:
    try:
        return load_project_config(config_path)
    except tomllib.TOMLDecodeError as exc:
        raise EmitError.from_toml_decode(path=config_path, exc=exc) from exc


def _load_compile_project_config_for_entrypoint(entrypoint_path: Path) -> ProjectConfig:
    try:
        return load_project_config_for_source(entrypoint_path)
    except tomllib.TOMLDecodeError as exc:
        config_path = find_nearest_pyproject(entrypoint_path.parent)
        if config_path is None:
            raise
        raise EmitError.from_toml_decode(path=config_path, exc=exc) from exc
def collect_runtime_emit_roots(
    session: "CompilationSession",
) -> tuple[RuntimeEmitRoot, ...]:
    roots = [
        RuntimeEmitRoot(unit=session.root_unit, agent_name=agent_name)
        for agent_name in _unit_concrete_agent_names(session.root_unit)
    ]
    seen_units: set[tuple[Path, tuple[str, ...]]] = set()
    seen_runtime_packages: set[tuple[Path, tuple[str, ...]]] = set()

    def walk(unit: "IndexedUnit") -> None:
        unit_key = (unit.prompt_root, unit.module_parts)
        if unit_key in seen_units:
            return
        seen_units.add(unit_key)
        for imported_unit in unit.imported_units.values():
            imported_key = (imported_unit.prompt_root, imported_unit.module_parts)
            if (
                imported_unit.module_source_kind == "runtime_package"
                and imported_key not in seen_runtime_packages
            ):
                # Pre-order import traversal keeps runtime roots in first-seen
                # graph order without asking the build handle to repeat imports.
                concrete_agents = _unit_concrete_agent_names(imported_unit)
                if len(concrete_agents) != 1:
                    dotted_name = ".".join(imported_unit.module_parts)
                    raise CompileError(
                        "Runtime package import must define exactly one concrete agent: "
                        f"{dotted_name or '<entrypoint>'}"
                    )
                roots.append(
                    RuntimeEmitRoot(
                        unit=imported_unit,
                        agent_name=concrete_agents[0],
                    )
                )
                seen_runtime_packages.add(imported_key)
            walk(imported_unit)

    walk(session.root_unit)
    return tuple(roots)


def _unit_concrete_agent_names(unit: "IndexedUnit") -> tuple[str, ...]:
    return tuple(
        agent.name
        for agent in unit.agents_by_name.values()
        if not agent.abstract
    )


def entrypoint_relative_dir(entrypoint: Path) -> Path:
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
