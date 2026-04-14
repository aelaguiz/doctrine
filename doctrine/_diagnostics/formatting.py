from __future__ import annotations

from pathlib import Path
from typing import Any

from doctrine._diagnostics.contracts import (
    DiagnosticExcerptLine,
    DiagnosticLocation,
    DiagnosticTraceFrame,
    DoctrineDiagnostic,
)


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple):
        return [_json_safe_value(item) for item in value]
    if isinstance(value, list):
        return [_json_safe_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe_value(item) for key, item in value.items()}
    if isinstance(value, DiagnosticLocation):
        return {
            "path": _json_safe_value(value.path),
            "line": value.line,
            "column": value.column,
        }
    if isinstance(value, DiagnosticExcerptLine):
        return {
            "number": value.number,
            "text": value.text,
        }
    if isinstance(value, DiagnosticTraceFrame):
        return {
            "label": value.label,
            "location": _json_safe_value(value.location),
        }
    if isinstance(value, DoctrineDiagnostic):
        return {
            "code": value.code,
            "stage": value.stage,
            "summary": value.summary,
            "detail": value.detail,
            "location": _json_safe_value(value.location),
            "excerpt": _json_safe_value(value.excerpt),
            "caret_column": value.caret_column,
            "hints": _json_safe_value(value.hints),
            "trace": _json_safe_value(value.trace),
            "cause": value.cause,
        }
    return value


def _format_location(location: DiagnosticLocation) -> str:
    path = location.path
    if path is None:
        return "<unknown>"
    rendered = _display_path(path)
    if location.line is None:
        return rendered
    if location.column is None:
        return f"{rendered}:{location.line}"
    return f"{rendered}:{location.line}:{location.column}"


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    try:
        return str(resolved.relative_to(cwd))
    except ValueError:
        return str(resolved)


def _format_block(text: str) -> list[str]:
    return [f"- {line}" if index == 0 else f"  {line}" for index, line in enumerate(text.splitlines())]


def _format_excerpt(
    excerpt: tuple[DiagnosticExcerptLine, ...],
    *,
    highlight_line: int | None = None,
    caret_column: int | None,
) -> list[str]:
    number_width = max(len(str(line.number)) for line in excerpt)
    lines: list[str] = []
    for entry in excerpt:
        lines.append(f"  {entry.number:>{number_width}} | {entry.text}")
        if caret_column is not None and highlight_line is not None and entry.number == highlight_line:
            padding = " " * (number_width + 5 + max(caret_column - 1, 0))
            lines.append(f"{padding}^")
    return lines


def _build_excerpt(
    source: str,
    *,
    line: int | None,
    column: int | None,
) -> tuple[tuple[DiagnosticExcerptLine, ...], int | None]:
    if line is None:
        return (), None
    all_lines = source.splitlines()
    if not all_lines:
        return (), column
    start = max(line - 2, 1)
    end = min(line + 1, len(all_lines))
    excerpt = tuple(
        DiagnosticExcerptLine(number=index, text=all_lines[index - 1])
        for index in range(start, end + 1)
    )
    return excerpt, column
