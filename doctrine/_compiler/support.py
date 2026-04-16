from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from doctrine._compiler.diagnostics import compile_error, file_scoped_related
from doctrine.diagnostics import CompileError, DiagnosticLocation

if TYPE_CHECKING:
    from doctrine.project_config import ProvidedPromptRoot


def default_worker_count(task_count: int) -> int:
    if task_count <= 1:
        return 1
    cpu_count = os.cpu_count() or 1
    return min(task_count, max(2, cpu_count))


def resolve_prompt_root(source_path: Path | None) -> Path:
    if source_path is None:
        raise compile_error(
            code="E291",
            summary="Prompt source path is required for compilation",
            detail="Prompt source path is required for compilation.",
        )

    resolved = source_path.resolve()
    for candidate in [resolved.parent, *resolved.parents]:
        if candidate.name == "prompts":
            return candidate

    raise compile_error(
        code="E292",
        summary="Could not resolve prompts root",
        detail=f"Could not resolve prompts/ root for {resolved}.",
        path=resolved,
    )


def resolve_import_roots(
    prompt_root: Path,
    additional_prompt_roots: tuple[Path, ...],
    provided_prompt_roots: tuple["ProvidedPromptRoot", ...] = (),
) -> tuple[Path, ...]:
    import_roots = [prompt_root]
    seen_roots = {prompt_root: "entrypoint prompts root"}
    for additional_root in additional_prompt_roots:
        if additional_root in seen_roots:
            resolved_root = additional_root.resolve()
            raise compile_error(
                code="E286",
                summary="Duplicate active prompts root",
                detail=(
                    "Duplicate active prompts root: "
                    f"{resolved_root} ({seen_roots[additional_root]} and configured prompts root)"
                ),
                path=resolved_root,
                related=(
                    file_scoped_related(
                        label=seen_roots[additional_root],
                        path=resolved_root,
                    ),
                ),
                hints=("Keep each active prompts root on one unique `prompts/` directory.",),
            )
        seen_roots[additional_root] = "configured prompts root"
        import_roots.append(additional_root)
    for provided_root in provided_prompt_roots:
        provided_path = Path(provided_root.path).resolve()
        owner_label = f"provided prompts root `{provided_root.name}`"
        if provided_path in seen_roots:
            raise compile_error(
                code="E286",
                summary="Duplicate active prompts root",
                detail=(
                    "Duplicate active prompts root: "
                    f"{provided_path} ({seen_roots[provided_path]} and {owner_label})"
                ),
                path=provided_path,
                related=(
                    file_scoped_related(
                        label=seen_roots[provided_path],
                        path=provided_path,
                    ),
                ),
                hints=("Keep each active prompts root on one unique `prompts/` directory.",),
            )
        seen_roots[provided_path] = owner_label
        import_roots.append(provided_path)
    return tuple(import_roots)


def dotted_decl_name(module_parts: tuple[str, ...], name: str) -> str:
    return ".".join((*module_parts, name)) if module_parts else name


def path_location(path: Path | None) -> DiagnosticLocation | None:
    if path is None:
        return None
    return DiagnosticLocation(path=path.resolve())
