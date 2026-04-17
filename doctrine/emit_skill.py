from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import (
    EmitTarget,
    SKILL_ENTRYPOINTS,
    display_path,
    ensure_supported_entrypoint,
    emit_error,
    entrypoint_output_name,
    entrypoint_relative_dir,
    load_emit_targets,
    path_location,
    resolve_pyproject_path,
)
from doctrine.parser import parse_file
from doctrine.renderer import render_readable_block


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
            emitted = emit_target_skill(target)
            print(
                f"{target.name}: emitted {len(emitted)} file(s) to {display_path(target.output_dir)}"
            )
        return 0
    except DoctrineError as exc:
        print(exc, file=sys.stderr)
        return 1


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Emit compiled skill-package trees for configured Doctrine targets."
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


def emit_target_skill(
    target: EmitTarget,
    *,
    output_dir_override: Path | None = None,
) -> tuple[Path, ...]:
    ensure_supported_entrypoint(
        target.entrypoint,
        allowed_entrypoints=SKILL_ENTRYPOINTS,
        owner_label=f"emit_skill target `{target.name}`",
    )
    try:
        prompt_file = parse_file(target.entrypoint)
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"emit target `{target.name}` entrypoint",
            location=path_location(target.entrypoint),
        )

    session = CompilationSession(prompt_file, project_config=target.project_config)
    try:
        compiled = session.compile_skill_package()
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"emit target `{target.name}`",
            location=path_location(target.entrypoint),
        )

    output_root = (output_dir_override or target.output_dir).resolve()
    emitted_dir = output_root / entrypoint_relative_dir(target.entrypoint)
    markdown_path = emitted_dir / entrypoint_output_name(target.entrypoint)
    contract_path = emitted_dir / "SKILL.contract.json"
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_skill_package_markdown(compiled), encoding="utf-8")
    emitted_paths: list[Path] = [markdown_path]
    if _should_emit_skill_package_contract_json(compiled):
        contract_path.write_text(render_skill_package_contract_json(compiled), encoding="utf-8")
        emitted_paths.append(contract_path)
    for bundled_file in compiled.files:
        bundled_path = emitted_dir / Path(bundled_file.path)
        bundled_path.parent.mkdir(parents=True, exist_ok=True)
        bundled_path.write_bytes(bundled_file.content)
        emitted_paths.append(bundled_path)
    return tuple(emitted_paths)


def render_skill_package_markdown(compiled) -> str:
    frontmatter_lines = ["---"]
    for key, value in compiled.frontmatter:
        frontmatter_lines.append(f"{key}: {json.dumps(value)}")
    frontmatter_lines.extend(["---", ""])

    rendered_root = render_readable_block(compiled.root, depth=1).rstrip()
    if rendered_root:
        frontmatter_lines.append(rendered_root)
    return "\n".join(frontmatter_lines).rstrip() + "\n"


def render_skill_package_contract_json(compiled) -> str:
    payload = {
        "contract_version": compiled.contract.contract_version,
        "package": {
            "name": compiled.contract.package_name,
            "title": compiled.contract.package_title,
        },
        "host_contract": {
            slot.key: {
                "family": slot.family,
                "title": slot.title,
            }
            for slot in compiled.contract.host_contract
        },
        "artifacts": {
            artifact.path: {
                "kind": artifact.kind,
                **({"source": artifact.source} if artifact.source is not None else {}),
                "referenced_host_paths": list(artifact.referenced_host_paths),
            }
            for artifact in compiled.contract.artifacts
        },
    }
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def _should_emit_skill_package_contract_json(compiled) -> bool:
    return bool(compiled.contract.host_contract or compiled.contract.artifacts)


if __name__ == "__main__":
    raise SystemExit(main())
