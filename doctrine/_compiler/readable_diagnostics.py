from __future__ import annotations

from doctrine._compiler.diagnostics import compile_error, related_prompt_site
from doctrine._compiler.resolved_types import CompileError, IndexedUnit
from doctrine._diagnostics.contracts import DiagnosticRelatedLocation
from doctrine._model.core import SourceSpan


def readable_compile_error(
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


def readable_related_site(
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


def readable_source_span(value: object | None) -> SourceSpan | None:
    return getattr(value, "source_span", None)


def duplicate_readable_key_error(
    *,
    subject_label: str,
    owner_label: str,
    kind_label: str,
    key: str,
    unit: IndexedUnit,
    source_span: SourceSpan | None,
    first_source_span: SourceSpan | None,
) -> CompileError:
    related = ()
    if first_source_span is not None:
        related = (
            readable_related_site(
                label=f"first `{key}` {kind_label}",
                unit=unit,
                source_span=first_source_span,
            ),
        )
    return readable_compile_error(
        code="E295",
        summary="Duplicate readable key",
        detail=f"{subject_label} `{owner_label}` repeats {kind_label} key `{key}`.",
        unit=unit,
        source_span=source_span,
        related=related,
    )


def invalid_readable_block_error(
    *,
    detail: str,
    unit: IndexedUnit,
    source_span: SourceSpan | None,
    hints: tuple[str, ...] = (),
) -> CompileError:
    return readable_compile_error(
        code="E297",
        summary="Invalid readable block structure",
        detail=detail,
        unit=unit,
        source_span=source_span,
        hints=hints,
    )


def document_patch_error(
    *,
    detail: str,
    unit: IndexedUnit,
    source_span: SourceSpan | None,
    related: tuple[DiagnosticRelatedLocation, ...] = (),
    hints: tuple[str, ...] = (),
) -> CompileError:
    return readable_compile_error(
        code="E305",
        summary="Invalid document inheritance patch",
        detail=detail,
        unit=unit,
        source_span=source_span,
        related=related,
        hints=hints,
    )
