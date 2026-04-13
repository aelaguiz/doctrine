from __future__ import annotations

from doctrine import model
from doctrine._compiler.resolved_types import (
    CompileError,
    IndexedUnit,
    ReviewSemanticContext,
    RouteSemanticContext,
)


class ValidateReadablesMixin:
    """Readable guard validation helpers for ValidateMixin."""

    def _validate_readable_guard_expr(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        owner_label: str,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> None:
        if isinstance(expr, model.ExprRef):
            if self._output_guard_ref_allowed(
                expr,
                unit=unit,
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            ):
                return
            raise CompileError(
                f"Readable guard reads disallowed source in {owner_label}: {'.'.join(expr.parts)}"
            )
        if isinstance(expr, model.ExprBinary):
            self._validate_readable_guard_expr(
                expr.left,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
            self._validate_readable_guard_expr(
                expr.right,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=allow_review_semantics,
                allow_route_semantics=allow_route_semantics,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
            return
        if isinstance(expr, model.ExprCall):
            for arg in expr.args:
                self._validate_readable_guard_expr(
                    arg,
                    unit=unit,
                    owner_label=owner_label,
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )
            return
        if isinstance(expr, model.ExprSet):
            for item in expr.items:
                self._validate_readable_guard_expr(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    allow_review_semantics=allow_review_semantics,
                    allow_route_semantics=allow_route_semantics,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                )

    def _readable_guard_text(
        self,
        expr: model.Expr | None,
        *,
        unit: IndexedUnit,
    ) -> str | None:
        if expr is None:
            return None
        return self._render_condition_expr(expr, unit=unit)
