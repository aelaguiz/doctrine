from __future__ import annotations

import re
from typing import Callable

from doctrine._diagnostics._message_builders_agents import _AGENT_MESSAGE_BUILDERS
from doctrine._diagnostics._message_builders_authored import _AUTHORED_MESSAGE_BUILDERS
from doctrine._diagnostics._message_builders_emit import _EMIT_MESSAGE_BUILDERS
from doctrine._diagnostics._message_builders_readables import _READABLE_MESSAGE_BUILDERS
from doctrine._diagnostics._message_builders_refs import _REFERENCE_MESSAGE_BUILDERS
from doctrine._diagnostics._message_builders_reviews import _REVIEW_MESSAGE_BUILDERS
from doctrine._diagnostics._message_builders_workflow_law import _WORKFLOW_LAW_MESSAGE_BUILDERS
from doctrine._diagnostics.contracts import DoctrineDiagnostic

_PatternBuilder = tuple[
    re.Pattern[str],
    str,
    str,
    Callable[[re.Match[str]], str | None],
    tuple[str, ...],
]

_COMPILE_MISC_BUILDERS: tuple[_PatternBuilder, ...] = (
    (
        re.compile(r"^Could not resolve prompts/ root for (?P<path>.+)\.$"),
        "E292",
        "Could not resolve prompts root",
        lambda match: f"Could not resolve `prompts/` root for `{match.group('path')}`.",
        (),
    ),
    (
        re.compile(r"^Internal compiler error: (?P<detail>.+)$"),
        "E901",
        "Internal compiler error",
        lambda match: match.group("detail"),
        ("This is a compiler bug, not a prompt authoring error.",),
    ),
)

_COMPILE_PATTERN_BUILDERS: tuple[_PatternBuilder, ...] = (
    *_AGENT_MESSAGE_BUILDERS,
    *_AUTHORED_MESSAGE_BUILDERS,
    *_REFERENCE_MESSAGE_BUILDERS,
    *_READABLE_MESSAGE_BUILDERS,
    *_WORKFLOW_LAW_MESSAGE_BUILDERS,
    *_REVIEW_MESSAGE_BUILDERS,
    *_COMPILE_MISC_BUILDERS,
)


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


def _compile_diagnostic_from_message(message: str) -> DoctrineDiagnostic:
    return _build_diagnostic_from_message(
        message=message,
        stage="compile",
        fallback_code="E299",
        fallback_summary="Compile failure",
        pattern_builders=_COMPILE_PATTERN_BUILDERS,
    )


def _emit_diagnostic_from_message(message: str) -> DoctrineDiagnostic:
    return _build_diagnostic_from_message(
        message=message,
        stage="emit",
        fallback_code="E599",
        fallback_summary="Emit failure",
        pattern_builders=_EMIT_MESSAGE_BUILDERS,
    )
