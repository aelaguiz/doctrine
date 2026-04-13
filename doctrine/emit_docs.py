from __future__ import annotations

import argparse
import sys
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import (
    EmitTarget,
    agent_slug,
    display_path,
    emit_error,
    entrypoint_contract_name,
    entrypoint_output_name,
    entrypoint_relative_dir,
    load_emit_targets,
    path_location,
    resolve_pyproject_path,
    root_concrete_agents,
)
from doctrine.emit_contract import render_compiled_agent_contract
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_arg_parser().parse_args(argv)
        config_path = resolve_pyproject_path(args.pyproject)
        targets = load_emit_targets(config_path)

        for target_name in args.target:
            target = targets.get(target_name)
            if target is None:
                raise emit_error(
                    "E501",
                    "Unknown emit target",
                    f"Emit target `{target_name}` is not defined in `pyproject.toml`.",
                    location=path_location(config_path),
                )
            emitted = emit_target(target)
            print(
                f"{target.name}: emitted {len(emitted)} file(s) to {display_path(target.output_dir)}"
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
            location=path_location(target.entrypoint),
        )
    agent_names = root_concrete_agents(prompt_file)
    if not agent_names:
        raise emit_error(
            "E502",
            "Emit target has no concrete agents",
            f"Emit target `{target.name}` has no concrete agents in `{target.entrypoint}`.",
            location=path_location(target.entrypoint),
        )

    output_root = (output_dir_override or target.output_dir).resolve()
    emitted_dir = output_root / entrypoint_relative_dir(target.entrypoint)

    planned_emits: list[tuple[str, Path, Path]] = []
    seen_paths: dict[Path, str] = {}
    for agent_name in agent_names:
        markdown_path = _emit_path_for_agent(
            emitted_dir,
            agent_name,
            output_name=entrypoint_output_name(target.entrypoint),
        )
        contract_path = _emit_path_for_agent(
            emitted_dir,
            agent_name,
            output_name=entrypoint_contract_name(target.entrypoint),
        )
        prior_agent = seen_paths.get(markdown_path)
        if prior_agent is not None:
            raise emit_error(
                "E505",
                "Emit target path collision",
                f"Emit target `{target.name}` maps both `{prior_agent}` and `{agent_name}` to `{markdown_path}`.",
                location=path_location(markdown_path),
            )
        if contract_path in seen_paths:
            prior_agent = seen_paths[contract_path]
            raise emit_error(
                "E505",
                "Emit target path collision",
                f"Emit target `{target.name}` maps both `{prior_agent}` and `{agent_name}` to `{contract_path}`.",
                location=path_location(contract_path),
            )
        seen_paths[markdown_path] = agent_name
        seen_paths[contract_path] = agent_name
        planned_emits.append((agent_name, markdown_path, contract_path))

    session = CompilationSession(prompt_file, project_config=target.project_config)
    try:
        compiled_agents = session.compile_agents(
            tuple(agent_name for agent_name, _, _ in planned_emits)
        )
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"emit target `{target.name}`",
            location=path_location(target.entrypoint),
        )

    emitted_paths: list[Path] = []
    for (_agent_name, markdown_path, contract_path), compiled in zip(
        planned_emits,
        compiled_agents,
        strict=True,
    ):
        rendered = render_markdown(compiled)
        contract_json = render_compiled_agent_contract(compiled=compiled, target=target)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(rendered)
        contract_path.write_text(contract_json)
        emitted_paths.extend((markdown_path, contract_path))

    return tuple(emitted_paths)


def _emit_path_for_agent(emitted_dir: Path, agent_name: str, *, output_name: str) -> Path:
    slug = agent_slug(agent_name)
    if emitted_dir.parts and emitted_dir.parts[-1] == slug:
        return emitted_dir / output_name
    return emitted_dir / slug / output_name


if __name__ == "__main__":
    raise SystemExit(main())
