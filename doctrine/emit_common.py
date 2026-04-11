from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from doctrine import model
from doctrine.diagnostics import DiagnosticLocation, EmitError

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_FILE_NAME = "pyproject.toml"
CAMEL_BOUNDARY_RE = re.compile(r"(?<!^)(?=[A-Z])")
SUPPORTED_ENTRYPOINTS = ("AGENTS.prompt", "SOUL.prompt")


@dataclass(slots=True, frozen=True)
class EmitTarget:
    name: str
    entrypoint: Path
    output_dir: Path


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

    for candidate_dir in [base_dir, *base_dir.parents]:
        candidate = candidate_dir / PYPROJECT_FILE_NAME
        if candidate.is_file():
            return candidate.resolve()

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

    try:
        raw = tomllib.loads(config_path.read_text())
    except tomllib.TOMLDecodeError as exc:
        raise EmitError.from_toml_decode(path=config_path, exc=exc) from exc
    emit = raw.get("tool", {}).get("doctrine", {}).get("emit", {})
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

        targets[name] = EmitTarget(name=name, entrypoint=entrypoint, output_dir=output_dir)

    return targets


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
