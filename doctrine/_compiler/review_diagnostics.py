from __future__ import annotations

from collections.abc import Callable

from doctrine import model
from doctrine._compiler.diagnostics import compile_error, related_prompt_site
from doctrine._compiler.resolved_types import CompileError, IndexedUnit
from doctrine._diagnostics.contracts import DiagnosticRelatedLocation
from doctrine._model.core import SourceSpan


def review_compile_error(
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


def review_related_site(
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


def find_review_decl_item(
    review_decl: model.ReviewDecl,
    *,
    predicate: Callable[[object], bool],
) -> object | None:
    return next((item for item in review_decl.body.items if predicate(item)), None)


def collect_review_accept_stmts(
    items: tuple[model.ReviewPreOutcomeStmt, ...],
) -> tuple[model.ReviewAcceptStmt, ...]:
    collected: list[model.ReviewAcceptStmt] = []
    for item in items:
        if isinstance(item, model.ReviewAcceptStmt):
            collected.append(item)
            continue
        if isinstance(item, model.ReviewPreOutcomeWhenStmt):
            collected.extend(collect_review_accept_stmts(item.items))
            continue
        if isinstance(item, model.ReviewPreOutcomeMatchStmt):
            for case in item.cases:
                collected.extend(collect_review_accept_stmts(case.items))
    return tuple(collected)
