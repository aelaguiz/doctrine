from __future__ import annotations

import argparse
import sys
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import (
    DOCS_ENTRYPOINTS,
    EmitTarget,
    RuntimeEmitRoot,
    collect_runtime_emit_roots,
    display_path,
    ensure_supported_entrypoint,
    emit_error,
    entrypoint_relative_dir,
    load_emit_targets,
    path_location,
    resolve_direct_emit_target,
    resolve_pyproject_path,
)
from doctrine.flow_renderer import (
    FlowRenderDependencyError,
    FlowRenderFailure,
    render_flow_d2,
    render_flow_svg,
)
from doctrine.parser import parse_file


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_arg_parser().parse_args(argv)
        config_path = (
            resolve_pyproject_path(args.pyproject)
            if args.target
            else Path(args.pyproject).resolve() if args.pyproject else None
        )
        for target in _resolve_requested_targets(args, config_path):
            emitted = emit_target_flow(target)
            print(
                f"{target.name}: emitted {len(emitted)} file(s) to {display_path(target.output_dir)}"
            )
        return 0
    except DoctrineError as exc:
        print(exc, file=sys.stderr)
        return 1


def emit_target_flow(
    target: EmitTarget,
    *,
    output_dir_override: Path | None = None,
    include_svg: bool = True,
) -> tuple[Path, ...]:
    ensure_supported_entrypoint(
        target.entrypoint,
        allowed_entrypoints=DOCS_ENTRYPOINTS,
        owner_label=f"emit_flow target `{target.name}`",
    )
    try:
        prompt_file = parse_file(target.entrypoint)
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"emit target `{target.name}` entrypoint",
            location=path_location(target.entrypoint),
        )

    session = CompilationSession(prompt_file, project_config=target.project_config)
    runtime_roots = _runtime_flow_roots_for_target(session, target=target)
    if not runtime_roots:
        raise emit_error(
            "E502",
            "Emit target has no concrete agents",
            f"Emit target `{target.name}` has no concrete agents in `{target.entrypoint}`.",
            location=path_location(target.entrypoint),
        )

    output_root = (output_dir_override or target.output_dir).resolve()
    emitted_dir = output_root / entrypoint_relative_dir(target.entrypoint)
    output_name = f"{target.entrypoint.stem}.flow"
    d2_path = emitted_dir / f"{output_name}.d2"
    svg_path = emitted_dir / f"{output_name}.svg"

    try:
        graph = session.extract_target_flow_graph_from_units(
            tuple((root.unit, root.agent_name) for root in runtime_roots)
        )
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"emit target `{target.name}`",
            location=path_location(target.entrypoint),
        )

    emitted_dir.mkdir(parents=True, exist_ok=True)
    d2_source = render_flow_d2(graph)
    d2_path.write_text(d2_source)
    emitted_paths = [d2_path]

    if include_svg:
        try:
            render_flow_svg(d2_path, svg_path)
        except FlowRenderDependencyError as exc:
            raise emit_error(
                "E515",
                "Flow renderer prerequisite is unavailable",
                str(exc),
                location=path_location(d2_path),
                hints=exc.hints,
            ) from exc
        except FlowRenderFailure as exc:
            raise emit_error(
                "E516",
                "Pinned D2 renderer failed",
                f"Could not render `{svg_path.name}` from `{d2_path.name}`: {exc}",
                location=path_location(svg_path),
            ) from exc
        emitted_paths.append(svg_path)

    return tuple(emitted_paths)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Emit workflow data-flow artifacts for configured Doctrine targets or "
            "a direct Doctrine entrypoint."
        )
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
        help="Configured target name from [tool.doctrine.emit.targets]. Repeat to emit multiple targets.",
    )
    parser.add_argument(
        "--entrypoint",
        help=(
            "Direct Doctrine entrypoint to emit without a named target. "
            "Must point at AGENTS.prompt or SOUL.prompt under a prompts/ tree."
        ),
    )
    parser.add_argument(
        "--output-dir",
        help=(
            "Output directory for direct entrypoint mode. Required with --entrypoint."
        ),
    )
    return parser


def _resolve_requested_targets(
    args: argparse.Namespace,
    config_path: Path | None,
) -> tuple[EmitTarget, ...]:
    target_mode = bool(args.target)
    direct_mode = args.entrypoint is not None or args.output_dir is not None

    if target_mode and direct_mode:
        raise emit_error(
            "E517",
            "Emit flow CLI requires exactly one resolution mode",
            "Use either configured target mode (`--target`) or direct mode "
            "(`--entrypoint` with `--output-dir`), not both.",
            location=path_location(config_path),
        )

    if target_mode:
        if config_path is None:
            config_path = resolve_pyproject_path(args.pyproject)
        targets = load_emit_targets(config_path)
        resolved: list[EmitTarget] = []
        for target_name in args.target:
            target = targets.get(target_name)
            if target is None:
                raise emit_error(
                    "E501",
                    "Unknown emit target",
                    f"Emit target `{target_name}` is not defined in `pyproject.toml`.",
                    location=path_location(config_path),
                )
            resolved.append(target)
        return tuple(resolved)

    if direct_mode:
        if args.entrypoint is None or args.output_dir is None:
            raise emit_error(
                "E518",
                "Direct emit flow mode requires entrypoint and output_dir",
                "Direct `emit_flow` mode requires both `--entrypoint` and "
                "`--output-dir`.",
                location=path_location(config_path),
                hints=(
                    "Use `--target <name>` for configured targets.",
                    "Use `--entrypoint path/to/AGENTS.prompt --output-dir build` for direct mode.",
                ),
            )
        return (
            resolve_direct_emit_target(
                pyproject_path=config_path,
                start_dir=Path.cwd(),
                entrypoint=args.entrypoint,
                output_dir=args.output_dir,
                allowed_entrypoints=DOCS_ENTRYPOINTS,
            ),
        )

    raise emit_error(
        "E517",
        "Emit flow CLI requires exactly one resolution mode",
        "Use configured target mode (`--target`) or direct mode (`--entrypoint` "
        "with `--output-dir`).",
        location=path_location(config_path),
        hints=(
            "Use `--target <name>` for configured targets.",
            "Use `--entrypoint path/to/AGENTS.prompt --output-dir build` for direct mode.",
        ),
    )


def _runtime_flow_roots_for_target(
    session: CompilationSession,
    *,
    target: EmitTarget,
) -> tuple[RuntimeEmitRoot, ...]:
    """Flow-graph-specific frontier for one emit target.

    For `SOUL.prompt` entrypoints the flow graph needs *every* concrete
    agent in the root flow so the rendered diagram can show handoffs
    between siblings. For `AGENTS.prompt` and `SKILL.prompt` entrypoints
    the graph follows the standard emit frontier from
    `collect_runtime_emit_roots` — the root flow's concrete agents plus
    first-seen imported runtime packages.
    """
    if target.entrypoint.name == "SOUL.prompt":
        return tuple(
            RuntimeEmitRoot(
                unit=session.root_flow.declaration_owner_units_by_id[id(agent)],
                agent_name=agent_name,
            )
            for agent_name, agent in session.root_flow.agents_by_name.items()
            if not agent.abstract
        )
    return collect_runtime_emit_roots(session)


if __name__ == "__main__":
    raise SystemExit(main())
