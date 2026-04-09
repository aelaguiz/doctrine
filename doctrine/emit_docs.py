from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from doctrine import model
from doctrine.compiler import compile_prompt
from doctrine.diagnostics import DiagnosticLocation, EmitError, DoctrineError
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_FILE_NAME = "pyproject.toml"
_CAMEL_BOUNDARY_RE = re.compile(r"(?<!^)(?=[A-Z])")
SUPPORTED_ENTRYPOINTS = ("AGENTS.prompt", "SOUL.prompt")


@dataclass(slots=True, frozen=True)
class EmitTarget:
    name: str
    entrypoint: Path
    output_dir: Path


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_arg_parser().parse_args(argv)
        config_path = resolve_pyproject_path(args.pyproject)
        targets = load_emit_targets(config_path)

        for target_name in args.target:
            target = targets.get(target_name)
            if target is None:
                raise _emit_error(
                    "E501",
                    "Unknown emit target",
                    f"Emit target `{target_name}` is not defined in `pyproject.toml`.",
                    location=_path_location(config_path),
                )
            emitted = emit_target(target)
            print(
                f"{target.name}: emitted {len(emitted)} file(s) to {_display_path(target.output_dir)}"
            )
        return 0
    except DoctrineError as exc:
        print(exc, file=sys.stderr)
        return 1


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Emit compiled Markdown trees for configured Doctrine targets."
    )
    parser.add_argument(
        "--pyproject",
        help=(
            "Path to the pyproject.toml that defines [tool.doctrine.emit]. "
            "Defaults to the nearest parent pyproject.toml from the current working directory."
        ),
    )
    parser.add_argument(
        "--target",
        action="append",
        required=True,
        help="Configured target name from [tool.doctrine.emit.targets]. Repeat to emit multiple targets.",
    )
    return parser


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
            raise _emit_error(
                "E507",
                "Emit config path must point at pyproject.toml",
                f"Emit config must point at `pyproject.toml`, got `{resolved}`.",
                location=_path_location(resolved),
            )
        if not resolved.is_file():
            raise _emit_error(
                "E504",
                "Missing pyproject.toml",
                f"Missing `pyproject.toml`: `{resolved}`.",
                location=_path_location(resolved),
            )
        return resolved

    for candidate_dir in [base_dir, *base_dir.parents]:
        candidate = candidate_dir / PYPROJECT_FILE_NAME
        if candidate.is_file():
            return candidate.resolve()

    raise _emit_error(
        "E504",
        "Missing pyproject.toml",
        f"Could not find `pyproject.toml` in `{base_dir}` or any parent directory.",
        location=_path_location(base_dir),
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
    emit = (
        raw.get("tool", {})
        .get("doctrine", {})
        .get("emit", {})
    )
    raw_targets = emit.get("targets")
    if not isinstance(raw_targets, list) or not raw_targets:
        raise _emit_error(
            "E503",
            "Missing emit targets",
            "The current `pyproject.toml` does not define any `[tool.doctrine.emit.targets]`.",
            location=_path_location(config_path),
        )

    config_dir = config_path.parent
    targets: dict[str, EmitTarget] = {}
    for index, raw_target in enumerate(raw_targets, start=1):
        if not isinstance(raw_target, dict):
            raise _emit_error(
                "E508",
                "Emit target must be a TOML table",
                f"Emit target #{index} must be a TOML table.",
                location=_path_location(config_path),
            )

        name = _require_str(raw_target, "name", label=f"emit target #{index}")
        if name in targets:
            raise _emit_error(
                "E509",
                "Duplicate emit target name",
                f"Emit target `{name}` is defined more than once.",
                location=_path_location(config_path),
            )

        entrypoint = _resolve_config_file(
            config_dir,
            _require_str(raw_target, "entrypoint", label=f"emit target {name}"),
            label=f"emit target {name} entrypoint",
        )
        if entrypoint.name not in SUPPORTED_ENTRYPOINTS:
            raise _emit_error(
                "E510",
                "Emit target entrypoint must be AGENTS.prompt or SOUL.prompt",
                f"Emit target `{name}` must point at an `AGENTS.prompt` or `SOUL.prompt` entrypoint, got `{entrypoint.name}`.",
                location=_path_location(entrypoint),
            )

        output_dir = _resolve_config_path(
            config_dir,
            _require_str(raw_target, "output_dir", label=f"emit target {name}"),
        )
        if output_dir.is_file():
            raise _emit_error(
                "E511",
                "Emit target output_dir is a file",
                f"Emit target `{name}` output_dir is a file: `{output_dir}`.",
                location=_path_location(output_dir),
            )

        targets[name] = EmitTarget(name=name, entrypoint=entrypoint, output_dir=output_dir)

    return targets


def emit_target(
    target: EmitTarget,
    *,
    output_dir_override: Path | None = None,
) -> tuple[Path, ...]:
    try:
        prompt_file = parse_file(target.entrypoint)
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"emit target `{target.name}` entrypoint",
            location=_path_location(target.entrypoint),
        )
    agent_names = _root_concrete_agents(prompt_file)
    if not agent_names:
        raise _emit_error(
            "E502",
            "Emit target has no concrete agents",
            f"Emit target `{target.name}` has no concrete agents in `{target.entrypoint}`.",
            location=_path_location(target.entrypoint),
        )

    output_root = (output_dir_override or target.output_dir).resolve()
    emitted_dir = output_root / _entrypoint_relative_dir(target.entrypoint)

    emitted_paths: list[Path] = []
    seen_paths: dict[Path, str] = {}
    for agent_name in agent_names:
        emit_path = _emit_path_for_agent(
            emitted_dir,
            agent_name,
            output_name=_entrypoint_output_name(target.entrypoint),
        )
        prior_agent = seen_paths.get(emit_path)
        if prior_agent is not None:
            raise _emit_error(
                "E505",
                "Emit target path collision",
                f"Emit target `{target.name}` maps both `{prior_agent}` and `{agent_name}` to `{emit_path}`.",
                location=_path_location(emit_path),
            )
        seen_paths[emit_path] = agent_name

        try:
            rendered = render_markdown(compile_prompt(prompt_file, agent_name))
        except DoctrineError as exc:
            raise exc.prepend_trace(
                f"emit target `{target.name}`",
                location=_path_location(target.entrypoint),
            )
        emit_path.parent.mkdir(parents=True, exist_ok=True)
        emit_path.write_text(rendered)
        emitted_paths.append(emit_path)

    return tuple(emitted_paths)


def _emit_path_for_agent(emitted_dir: Path, agent_name: str, *, output_name: str) -> Path:
    agent_slug = _agent_slug(agent_name)
    if emitted_dir.parts and emitted_dir.parts[-1] == agent_slug:
        return emitted_dir / output_name
    return emitted_dir / agent_slug / output_name


def _root_concrete_agents(prompt_file: model.PromptFile) -> tuple[str, ...]:
    names = [
        declaration.name
        for declaration in prompt_file.declarations
        if isinstance(declaration, model.Agent) and not declaration.abstract
    ]
    return tuple(names)


def _entrypoint_relative_dir(entrypoint: Path) -> Path:
    resolved = entrypoint.resolve()
    for candidate in [resolved.parent, *resolved.parents]:
        if candidate.name == "prompts":
            rel_dir = resolved.relative_to(candidate).parent
            return Path() if rel_dir == Path(".") else rel_dir
    raise _emit_error(
        "E514",
        "Could not resolve prompts root",
        f"Could not resolve `prompts/` root for `{resolved}`.",
        location=_path_location(resolved),
    )


def _entrypoint_output_name(entrypoint: Path) -> str:
    return f"{entrypoint.stem}.md"


def _agent_slug(name: str) -> str:
    return _CAMEL_BOUNDARY_RE.sub("_", name).lower()


def _resolve_config_file(config_dir: Path, value: str, *, label: str) -> Path:
    path = _resolve_config_path(config_dir, value)
    if not path.is_file():
        raise _emit_error(
            "E512",
            "Emit config path does not exist",
            f"{label} does not exist: {value}",
            location=_path_location(path),
        )
    return path


def _resolve_config_path(config_dir: Path, value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = config_dir / candidate
    return candidate.resolve()


def _require_str(raw: dict[str, object], key: str, *, label: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str):
        raise _emit_error(
            "E513",
            "Emit config value must be a string",
            f"{label}.{key} must be a string.",
        )
    return value


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _path_location(path: Path | None) -> DiagnosticLocation | None:
    if path is None:
        return None
    return DiagnosticLocation(path=path.resolve())


def _emit_error(
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


if __name__ == "__main__":
    raise SystemExit(main())
