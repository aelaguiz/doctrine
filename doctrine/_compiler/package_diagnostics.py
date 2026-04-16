from __future__ import annotations

from pathlib import Path

from doctrine._compiler.diagnostics import compile_error, file_scoped_related
from doctrine._diagnostics.contracts import DiagnosticRelatedLocation
from doctrine._model.core import SourceSpan
from doctrine.diagnostics import CompileError


def package_compile_error(
    *,
    code: str,
    summary: str,
    detail: str,
    path: Path | None = None,
    source_span: SourceSpan | None = None,
    related: tuple[DiagnosticRelatedLocation, ...] = (),
    hints: tuple[str, ...] = (),
) -> CompileError:
    return compile_error(
        code=code,
        summary=summary,
        detail=detail,
        path=path,
        source_span=source_span,
        related=related,
        hints=hints,
    )


def package_related_path(
    *,
    label: str,
    path: Path | None,
) -> DiagnosticRelatedLocation:
    return file_scoped_related(label=label, path=path)
