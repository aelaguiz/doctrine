from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from doctrine._diagnostics.contracts import (
    DiagnosticExcerptLine,
    DiagnosticLocation,
    DiagnosticRelatedLocation,
)
from doctrine._diagnostics.formatting import _build_excerpt
from doctrine.diagnostics import CompileError

if TYPE_CHECKING:
    from doctrine._model.core import SourceSpan


def prompt_site(
    *,
    path: Path | None,
    source_span: "SourceSpan | None",
) -> tuple[DiagnosticLocation | None, tuple[DiagnosticExcerptLine, ...], int | None]:
    if path is None:
        return None, (), None
    resolved_path = path.resolve()
    if source_span is None:
        return DiagnosticLocation(path=resolved_path), (), None
    source = _read_source(resolved_path)
    excerpt, caret_column = _build_excerpt(
        source or "",
        line=source_span.line,
        column=source_span.column,
    )
    return (
        DiagnosticLocation(
            path=resolved_path,
            line=source_span.line,
            column=source_span.column,
        ),
        excerpt,
        caret_column,
    )


def related_prompt_site(
    *,
    label: str,
    path: Path | None,
    source_span: "SourceSpan | None",
) -> DiagnosticRelatedLocation:
    location, excerpt, caret_column = prompt_site(path=path, source_span=source_span)
    return DiagnosticRelatedLocation(
        label=label,
        location=location,
        excerpt=excerpt,
        caret_column=caret_column,
    )


def file_scoped_related(
    *,
    label: str,
    path: Path | None,
) -> DiagnosticRelatedLocation:
    return DiagnosticRelatedLocation(
        label=label,
        location=DiagnosticLocation(path=path.resolve()) if path is not None else None,
    )


def compile_error(
    *,
    code: str,
    summary: str,
    detail: str | None = None,
    path: Path | None = None,
    source_span: "SourceSpan | None" = None,
    related: tuple[DiagnosticRelatedLocation, ...] = (),
    hints: tuple[str, ...] = (),
    cause: str | None = None,
) -> CompileError:
    location, excerpt, caret_column = prompt_site(path=path, source_span=source_span)
    return CompileError.from_parts(
        code=code,
        summary=summary,
        detail=detail,
        location=location,
        excerpt=excerpt,
        caret_column=caret_column,
        related=related,
        hints=hints,
        cause=cause,
    )


def _read_source(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None
