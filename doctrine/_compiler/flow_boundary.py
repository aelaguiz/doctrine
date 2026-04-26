from __future__ import annotations

from pathlib import Path
from typing import Literal, TypeAlias

from doctrine._compiler.diagnostics import compile_error

FlowBoundaryKind: TypeAlias = Literal["agent_flow", "skill_flow"]
_FLOW_ENTRYPOINT_FILENAMES: dict[str, FlowBoundaryKind] = {
    "AGENTS.prompt": "agent_flow",
    "SOUL.prompt": "agent_flow",
    "GRAPH.prompt": "skill_flow",
    "SKILL.prompt": "skill_flow",
}


def flow_boundary_kind_for_path(path: Path) -> FlowBoundaryKind | None:
    return _FLOW_ENTRYPOINT_FILENAMES.get(path.name)


def resolve_flow_entrypoint(source_path: Path, *, prompt_root: Path | None = None) -> Path:
    resolved = source_path.resolve()
    boundary_kind = flow_boundary_kind_for_path(resolved)
    if boundary_kind is not None:
        if prompt_root is not None:
            resolved_prompt_root = prompt_root.resolve()
            try:
                resolved.relative_to(resolved_prompt_root)
            except ValueError:
                pass
            else:
                return resolved
        else:
            return resolved
    resolved_prompt_root = None if prompt_root is None else prompt_root.resolve()
    search_roots = (resolved.parent, *resolved.parents) if resolved.is_file() else (resolved, *resolved.parents)
    for candidate in search_roots:
        if resolved_prompt_root is not None:
            try:
                candidate.relative_to(resolved_prompt_root)
            except ValueError:
                continue
        for entrypoint_name in _FLOW_ENTRYPOINT_FILENAMES:
            entrypoint_path = candidate / entrypoint_name
            if entrypoint_path.is_file():
                return entrypoint_path
    raise compile_error(
        code="E292",
        summary="Could not resolve flow root",
        detail=f"Could not resolve a flow entrypoint for {resolved}.",
        path=resolved,
    )


def _is_hidden_path(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def _is_editor_backup(path: Path) -> bool:
    return (
        path.name.endswith("~")
        or path.name.endswith(".bak")
        or path.name.endswith(".swp")
        or path.name.endswith(".tmp")
    )


def discover_flow_members(
    flow_root: Path,
    *,
    entrypoint_path: Path | None = None,
) -> tuple[Path, ...]:
    flow_root = flow_root.resolve()
    resolved_entrypoint = None if entrypoint_path is None else entrypoint_path.resolve()
    member_paths: list[Path] = []
    for path in sorted(flow_root.rglob("*.prompt")):
        if path.is_symlink():
            continue
        relative_path = path.relative_to(flow_root)
        if _is_hidden_path(relative_path) or _is_editor_backup(path):
            continue
        if (
            resolved_entrypoint is not None
            and path.name in _FLOW_ENTRYPOINT_FILENAMES
            and path.resolve() != resolved_entrypoint
        ):
            continue
        if relative_path != Path(path.name):
            parent_parts = relative_path.parts[:-1]
            nested_flow = False
            for depth in range(1, len(parent_parts) + 1):
                candidate_dir = flow_root.joinpath(*parent_parts[:depth])
                if any(
                    (candidate_dir / entrypoint_name).is_file()
                    for entrypoint_name in _FLOW_ENTRYPOINT_FILENAMES
                ):
                    nested_flow = True
                    break
            if nested_flow:
                continue
        member_paths.append(path.resolve())
    return tuple(member_paths)
