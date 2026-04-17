from __future__ import annotations

from doctrine._compiler.diagnostics import compile_error, related_prompt_site
from doctrine._compiler.resolved_types import CompileError, IndexedUnit
from doctrine._diagnostics.contracts import DiagnosticRelatedLocation
from doctrine._model.core import SourceSpan


def final_output_compile_error(
    *,
    code: str,
    summary: str,
    detail: str,
    unit: IndexedUnit,
    source_span: SourceSpan | None,
    related: tuple[DiagnosticRelatedLocation, ...] = (),
    hints: tuple[str, ...] = (),
) -> CompileError:
    return compile_error(
        code=code,
        summary=summary,
        detail=detail,
        path=unit.prompt_file.source_path,
        source_span=source_span,
        related=related,
        hints=hints,
    )


def final_output_related_site(
    *,
    label: str,
    unit: IndexedUnit,
    source_span: SourceSpan | None,
) -> DiagnosticRelatedLocation:
    return related_prompt_site(
        label=label,
        path=unit.prompt_file.source_path,
        source_span=source_span,
    )
