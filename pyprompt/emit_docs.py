from __future__ import annotations

import argparse
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from pyprompt import model
from pyprompt.compiler import compile_prompt
from pyprompt.parser import parse_file
from pyprompt.renderer import render_markdown

REPO_ROOT = Path(__file__).resolve().parent.parent
_CAMEL_BOUNDARY_RE = re.compile(r"(?<!^)(?=[A-Z])")


class EmitError(RuntimeError):
    """Raised when build-target configuration or emission is invalid."""


@dataclass(slots=True, frozen=True)
class EmitTarget:
    name: str
    entrypoint: Path
    output_dir: Path


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    targets = load_emit_targets()

    for target_name in args.target:
        target = targets.get(target_name)
        if target is None:
            raise EmitError(f"Unknown emit target: {target_name}")
        emitted = emit_target(target)
        print(f"{target.name}: emitted {len(emitted)} file(s) to {_display_path(target.output_dir)}")

    return 0


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Emit compiled AGENTS.md trees for configured PyPrompt targets."
    )
    parser.add_argument(
        "--target",
        action="append",
        required=True,
        help="Configured target name from [tool.pyprompt.emit.targets]. Repeat to emit multiple targets.",
    )
    return parser


def load_emit_targets(pyproject_path: Path | None = None) -> dict[str, EmitTarget]:
    config_path = (pyproject_path or (REPO_ROOT / "pyproject.toml")).resolve()
    if not config_path.is_file():
        raise EmitError(f"Missing pyproject.toml: {config_path}")

    raw = tomllib.loads(config_path.read_text())
    emit = (
        raw.get("tool", {})
        .get("pyprompt", {})
        .get("emit", {})
    )
    raw_targets = emit.get("targets")
    if not isinstance(raw_targets, list) or not raw_targets:
        raise EmitError("pyproject.toml does not define any [tool.pyprompt.emit.targets].")

    config_dir = config_path.parent
    targets: dict[str, EmitTarget] = {}
    for index, raw_target in enumerate(raw_targets, start=1):
        if not isinstance(raw_target, dict):
            raise EmitError(f"Emit target #{index} must be a TOML table.")

        name = _require_str(raw_target, "name", label=f"emit target #{index}")
        if name in targets:
            raise EmitError(f"Duplicate emit target name: {name}")

        entrypoint = _resolve_config_file(
            config_dir,
            _require_str(raw_target, "entrypoint", label=f"emit target {name}"),
            label=f"emit target {name} entrypoint",
        )
        if entrypoint.name != "AGENTS.prompt":
            raise EmitError(
                f"Emit target {name} must point at an AGENTS.prompt entrypoint, got {entrypoint.name}"
            )

        output_dir = _resolve_config_path(
            config_dir,
            _require_str(raw_target, "output_dir", label=f"emit target {name}"),
        )
        if output_dir.is_file():
            raise EmitError(f"Emit target {name} output_dir is a file: {output_dir}")

        targets[name] = EmitTarget(name=name, entrypoint=entrypoint, output_dir=output_dir)

    return targets


def emit_target(
    target: EmitTarget,
    *,
    output_dir_override: Path | None = None,
) -> tuple[Path, ...]:
    prompt_file = parse_file(target.entrypoint)
    agent_names = _root_concrete_agents(prompt_file)
    if not agent_names:
        raise EmitError(f"Emit target {target.name} has no concrete agents in {target.entrypoint}")

    output_root = (output_dir_override or target.output_dir).resolve()
    emitted_dir = output_root / _entrypoint_relative_dir(target.entrypoint)

    emitted_paths: list[Path] = []
    seen_paths: dict[Path, str] = {}
    for agent_name in agent_names:
        emit_path = emitted_dir / _agent_slug(agent_name) / "AGENTS.md"
        prior_agent = seen_paths.get(emit_path)
        if prior_agent is not None:
            raise EmitError(
                f"Emit target {target.name} maps both {prior_agent} and {agent_name} to {emit_path}"
            )
        seen_paths[emit_path] = agent_name

        rendered = render_markdown(compile_prompt(prompt_file, agent_name))
        emit_path.parent.mkdir(parents=True, exist_ok=True)
        emit_path.write_text(rendered)
        emitted_paths.append(emit_path)

    return tuple(emitted_paths)


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
    raise EmitError(f"Could not resolve prompts/ root for {resolved}")


def _agent_slug(name: str) -> str:
    return _CAMEL_BOUNDARY_RE.sub("_", name).lower()


def _resolve_config_file(config_dir: Path, value: str, *, label: str) -> Path:
    path = _resolve_config_path(config_dir, value)
    if not path.is_file():
        raise EmitError(f"{label} does not exist: {value}")
    return path


def _resolve_config_path(config_dir: Path, value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = config_dir / candidate
    return candidate.resolve()


def _require_str(raw: dict[str, object], key: str, *, label: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str):
        raise EmitError(f"{label}.{key} must be a string.")
    return value


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
