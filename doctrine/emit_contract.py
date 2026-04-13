from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from doctrine.compiler import CompiledAgent
from doctrine.emit_common import EmitTarget, agent_slug, display_path, emit_error, path_location

COMPILED_AGENT_CONTRACT_VERSION = 1


def render_compiled_agent_contract(
    *,
    compiled: CompiledAgent,
    target: EmitTarget,
) -> str:
    payload = build_compiled_agent_contract_payload(compiled=compiled, target=target)
    return json.dumps(payload, indent=2) + "\n"


def build_compiled_agent_contract_payload(
    *,
    compiled: CompiledAgent,
    target: EmitTarget,
) -> dict[str, Any]:
    return {
        "contract_version": COMPILED_AGENT_CONTRACT_VERSION,
        "agent": {
            "name": compiled.name,
            "slug": agent_slug(compiled.name),
            "entrypoint": _project_relative_path(
                target.entrypoint,
                target=target,
                surface_label="entrypoint",
            ),
        },
        "final_output": _final_output_payload(compiled=compiled, target=target),
    }


def _final_output_payload(
    *,
    compiled: CompiledAgent,
    target: EmitTarget,
) -> dict[str, Any]:
    final_output = compiled.final_output
    if final_output is None:
        return {
            "exists": False,
            "declaration_key": None,
            "declaration_name": None,
            "format_mode": None,
            "schema_profile": None,
            "schema_file": None,
            "example_file": None,
        }

    return {
        "exists": True,
        "declaration_key": _render_output_key(final_output.output_key),
        "declaration_name": final_output.output_name,
        "format_mode": final_output.format_mode,
        "schema_profile": final_output.schema_profile,
        "schema_file": _optional_project_relative_path(
            final_output.resolved_schema_file,
            target=target,
            surface_label="schema_file",
        ),
        "example_file": _optional_project_relative_path(
            final_output.resolved_example_file,
            target=target,
            surface_label="example_file",
        ),
    }


def _render_output_key(output_key: tuple[tuple[str, ...], str]) -> str:
    module_parts, name = output_key
    if not module_parts:
        return name
    return ".".join((*module_parts, name))


def _optional_project_relative_path(
    resolved_path: Path | None,
    *,
    target: EmitTarget,
    surface_label: str,
) -> str | None:
    if resolved_path is None:
        return None
    return _project_relative_path(resolved_path, target=target, surface_label=surface_label)


def _project_relative_path(
    resolved_path: Path,
    *,
    target: EmitTarget,
    surface_label: str,
) -> str:
    project_root = target.project_config.config_dir
    if project_root is None:
        raise emit_error(
            "E519",
            "Emit contract path requires project root",
            f"Emit target `{target.name}` cannot serialize `{surface_label}` without an owning project root.",
            location=path_location(target.entrypoint),
        )
    try:
        return resolved_path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError as exc:
        raise emit_error(
            "E519",
            "Emit contract support file must stay within project root",
            f"Emit target `{target.name}` resolved `{surface_label}` outside the target project root: "
            f"`{display_path(resolved_path.resolve())}` is not under `{display_path(project_root.resolve())}`.",
            location=path_location(resolved_path),
        ) from exc
