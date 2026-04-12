from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from doctrine import model
from doctrine.diagnostics import DiagnosticLocation, EmitError
from doctrine.project_config import (
    PYPROJECT_FILE_NAME,
    ProjectConfig,
    find_nearest_pyproject,
    load_project_config,
    load_project_config_for_source,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CAMEL_BOUNDARY_RE = re.compile(r"(?<!^)(?=[A-Z])")
SUPPORTED_ENTRYPOINTS = ("AGENTS.prompt", "SOUL.prompt")


@dataclass(slots=True, frozen=True)
class EmitTarget:
    name: str
    entrypoint: Path
    output_dir: Path
    project_config: ProjectConfig


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
        if entrypoint.name not in SUPPORTED_ENTRYPOINTS:
            raise emit_error(
                "E510",
                "Emit target entrypoint must be AGENTS.prompt or SOUL.prompt",
                f"Emit target `{name}` must point at an `AGENTS.prompt` or `SOUL.prompt` entrypoint, got `{entrypoint.name}`.",
                location=path_location(entrypoint),
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
    if entrypoint_path.name not in SUPPORTED_ENTRYPOINTS:
        raise emit_error(
            "E510",
            "Emit target entrypoint must be AGENTS.prompt or SOUL.prompt",
            "Direct emit entrypoint must point at an `AGENTS.prompt` or `SOUL.prompt` file, "
            f"got `{entrypoint_path.name}`.",
            location=path_location(entrypoint_path),
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


def root_concrete_agents(prompt_file: model.PromptFile) -> tuple[str, ...]:
    names = [
        declaration.name
        for declaration in prompt_file.declarations
        if isinstance(declaration, model.Agent) and not declaration.abstract
    ]
    return tuple(names)


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


def agent_slug(name: str) -> str:
    return CAMEL_BOUNDARY_RE.sub("_", name).lower()


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


def path_location(path: Path | None) -> DiagnosticLocation | None:
    if path is None:
        return None
    return DiagnosticLocation(path=path.resolve())


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
