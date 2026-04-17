from __future__ import annotations

import re
from typing import Callable

from doctrine._diagnostics._message_builders_emit import _EMIT_MESSAGE_BUILDERS
from doctrine._diagnostics.contracts import DoctrineDiagnostic

_PatternBuilder = tuple[
    re.Pattern[str],
    str,
    str,
    Callable[[re.Match[str]], str | None],
    tuple[str, ...],
]

def _build_diagnostic_from_message(
    *,
    message: str,
    stage: str,
    fallback_code: str,
    fallback_summary: str,
    pattern_builders: tuple[_PatternBuilder, ...],
) -> DoctrineDiagnostic:
    for pattern, code, summary, detail_builder, hints in pattern_builders:
        match = pattern.match(message)
        if match is None:
            continue
        detail = detail_builder(match)
        return DoctrineDiagnostic(
            code=code,
            stage=stage,
            summary=summary,
            detail=detail,
            hints=hints,
            cause=message if message != detail else None,
        )
    return DoctrineDiagnostic(
        code=fallback_code,
        stage=stage,
        summary=fallback_summary,
        detail=message,
    )


def _emit_diagnostic_from_message(message: str) -> DoctrineDiagnostic:
    return _build_diagnostic_from_message(
        message=message,
        stage="emit",
        fallback_code="E599",
        fallback_summary="Emit failure",
        pattern_builders=_EMIT_MESSAGE_BUILDERS,
    )
