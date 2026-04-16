from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class DiagnosticLocation:
    path: Path | None = None
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class DiagnosticExcerptLine:
    number: int
    text: str


@dataclass(slots=True, frozen=True)
class DiagnosticTraceFrame:
    label: str
    location: DiagnosticLocation | None = None


@dataclass(slots=True, frozen=True)
class DiagnosticRelatedLocation:
    label: str
    location: DiagnosticLocation | None = None
    excerpt: tuple["DiagnosticExcerptLine", ...] = ()
    caret_column: int | None = None


@dataclass(slots=True, frozen=True)
class DoctrineDiagnostic:
    code: str
    stage: str
    summary: str
    detail: str | None = None
    location: DiagnosticLocation | None = None
    excerpt: tuple[DiagnosticExcerptLine, ...] = ()
    caret_column: int | None = None
    related: tuple[DiagnosticRelatedLocation, ...] = ()
    hints: tuple[str, ...] = ()
    trace: tuple[DiagnosticTraceFrame, ...] = ()
    cause: str | None = None


class TransformParseFailure(ValueError):
    def __init__(
        self,
        detail: str,
        *,
        code: str = "E199",
        summary: str = "Parse failure",
        hints: tuple[str, ...] = (),
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        super().__init__(detail)
        self.code = code
        self.summary = summary
        self.hints = hints
        self.line = line
        self.column = column
