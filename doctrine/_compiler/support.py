from __future__ import annotations

import os
from pathlib import Path

from doctrine.diagnostics import CompileError, DiagnosticLocation


def default_worker_count(task_count: int) -> int:
    if task_count <= 1:
        return 1
    cpu_count = os.cpu_count() or 1
    return min(task_count, max(2, cpu_count))


def resolve_prompt_root(source_path: Path | None) -> Path:
    if source_path is None:
        raise CompileError("Prompt source path is required for compilation.")

    resolved = source_path.resolve()
    for candidate in [resolved.parent, *resolved.parents]:
        if candidate.name == "prompts":
            return candidate

    raise CompileError(f"Could not resolve prompts/ root for {resolved}.")


def resolve_import_roots(
    prompt_root: Path,
    additional_prompt_roots: tuple[Path, ...],
) -> tuple[Path, ...]:
    import_roots = [prompt_root]
    seen_roots = {prompt_root}
    for additional_root in additional_prompt_roots:
        if additional_root in seen_roots:
            raise CompileError(f"Duplicate configured prompts root: {additional_root}")
        seen_roots.add(additional_root)
        import_roots.append(additional_root)
    return tuple(import_roots)


def dotted_decl_name(module_parts: tuple[str, ...], name: str) -> str:
    return ".".join((*module_parts, name)) if module_parts else name


def path_location(path: Path | None) -> DiagnosticLocation | None:
    if path is None:
        return None
    return DiagnosticLocation(path=path.resolve())
