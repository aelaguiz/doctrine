from __future__ import annotations

from dataclasses import replace

from doctrine._compiler.constants import _REVIEW_VERDICT_TEXT
from doctrine._compiler.resolved_types import *  # noqa: F401,F403


class ValidateRouteSemanticsContextMixin:
    """Route-semantic collection and narrowing helpers for ValidateMixin."""

    def _route_semantic_context_from_review_decl(
        self,
        review_decl: model.ReviewDecl,
        *,
        unit: IndexedUnit,
    ) -> RouteSemanticContext | None:
        resolved = self._resolve_review_decl(review_decl, unit=unit)
        branches: list[RouteSemanticBranch] = []
        has_unrouted_branch = False

        def collect_section(
            section: model.ReviewOutcomeSection,
            *,
            verdict: str,
        ) -> None:
            nonlocal has_unrouted_branch
            for branch in self._collect_review_outcome_leaf_branches(section.items, unit=unit):
                if not branch.routes:
                    has_unrouted_branch = True
                    continue
                for route in branch.routes:
                    branches.append(
                        self._route_semantic_branch_from_route(
                            route,
                            label=route.label,
                            unit=unit,
                            review_verdict=verdict,
                        )
                    )

        if resolved.cases:
            for case in resolved.cases:
                collect_section(case.on_accept, verdict=_REVIEW_VERDICT_TEXT["accept"])
                collect_section(case.on_reject, verdict=_REVIEW_VERDICT_TEXT["changes_requested"])
        else:
            for item in resolved.items:
                if not isinstance(item, model.ReviewOutcomeSection):
                    continue
                verdict = (
                    _REVIEW_VERDICT_TEXT["accept"]
                    if item.key == "on_accept"
                    else _REVIEW_VERDICT_TEXT["changes_requested"]
                )
                collect_section(item, verdict=verdict)

        return self._build_route_semantic_context(
            branches,
            has_unrouted_branch=has_unrouted_branch,
        )

    def _route_semantic_context_from_law_items(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
    ) -> RouteSemanticContext | None:
        branches: list[RouteSemanticBranch] = []
        has_unrouted_branch = False
        for branch in self._collect_law_leaf_branches(items, unit=unit):
            if not branch.routes:
                has_unrouted_branch = True
                continue
            if not any(route.when_expr is None for route in branch.routes):
                has_unrouted_branch = True
            for route in branch.routes:
                branches.append(
                    self._route_semantic_branch_from_route(
                        route,
                        label=route.label,
                        unit=unit,
                    )
                )
        return self._build_route_semantic_context(
            branches,
            has_unrouted_branch=has_unrouted_branch,
        )

    def _route_semantic_context_from_law_body(
        self,
        law_body: model.LawBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> RouteSemanticContext | None:
        return self._route_semantic_context_from_law_items(
            self._flatten_law_items(law_body, owner_label=owner_label),
            unit=unit,
        )

    def _route_semantic_branch_from_route(
        self,
        route: model.LawRouteStmt | model.ReviewOutcomeRouteStmt,
        *,
        label: str,
        unit: IndexedUnit,
        review_verdict: str | None = None,
    ) -> RouteSemanticBranch:
        route_unit, route_agent = self._resolve_agent_ref(route.target, unit=unit)
        return RouteSemanticBranch(
            target_module_parts=route_unit.module_parts,
            target_name=route_agent.name,
            target_title=route_agent.title,
            label=label,
            review_verdict=review_verdict,
            choice_members=(
                self._route_choice_members_from_route(route, unit=unit)
                if isinstance(route, model.LawRouteStmt)
                else ()
            ),
        )

    def _build_route_semantic_context(
        self,
        branches: list[RouteSemanticBranch],
        *,
        has_unrouted_branch: bool,
    ) -> RouteSemanticContext | None:
        if not branches and not has_unrouted_branch:
            return None
        seen: set[tuple[tuple[str, ...], str, str, str | None]] = set()
        deduped: list[RouteSemanticBranch] = []
        for branch in branches:
            key = (
                branch.target_module_parts,
                branch.target_name,
                branch.label,
                branch.review_verdict,
                tuple(
                    (
                        member.enum_module_parts,
                        member.enum_name,
                        member.member_key,
                        member.member_wire,
                    )
                    for member in branch.choice_members
                ),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(branch)
        return RouteSemanticContext(
            branches=tuple(deduped),
            has_unrouted_branch=has_unrouted_branch,
        )

    def _narrow_route_semantics(
        self,
        route_semantics: RouteSemanticContext | None,
        expr: model.Expr | None,
        *,
        unit: IndexedUnit,
    ) -> RouteSemanticContext | None:
        if route_semantics is None or expr is None:
            return route_semantics

        narrowed = route_semantics
        exists_state = self._route_guard_exists_state(expr)
        if exists_state is True:
            narrowed = replace(narrowed, route_required=True)
        elif exists_state is False:
            narrowed = RouteSemanticContext(branches=(), has_unrouted_branch=False)

        verdict = self._route_guard_review_verdict(expr, unit=unit)
        if verdict is not None:
            narrowed = self._route_semantics_for_review_verdict(narrowed, verdict)
        narrowed = self._narrow_route_semantics_for_choice(
            narrowed,
            expr,
            unit=unit,
        )
        return narrowed

    def _route_choice_members_from_route(
        self,
        route: model.LawRouteStmt,
        *,
        unit: IndexedUnit,
    ) -> tuple[RouteChoiceMember, ...]:
        if route.choice_enum_ref is None:
            return ()
        enum_unit, enum_decl = self._resolve_decl_ref(
            route.choice_enum_ref,
            unit=unit,
            registry_name="enums_by_name",
            missing_label="enum declaration",
        )
        if route.choice_else:
            excluded = {
                self._resolve_constant_enum_member(head, unit=unit)
                for head in route.choice_case_heads
            }
            members = tuple(member for member in enum_decl.members if member.value not in excluded)
        else:
            members = tuple(
                self._resolve_route_from_member(
                    head,
                    enum_decl=enum_decl,
                    enum_unit=enum_unit,
                    owner_label=f"route_from {enum_decl.name}",
                )
                for head in route.choice_case_heads
            )
        return tuple(
            RouteChoiceMember(
                enum_module_parts=enum_unit.module_parts,
                enum_name=enum_decl.name,
                member_key=member.key,
                member_title=member.title,
                member_wire=member.value,
            )
            for member in members
        )

    def _route_choice_branches_are_live(
        self,
        branches: tuple[RouteSemanticBranch, ...],
    ) -> bool:
        return bool(branches) and all(branch.choice_members for branch in branches)

    def _route_choice_is_live(
        self,
        route_semantics: RouteSemanticContext | None,
    ) -> bool:
        return route_semantics is not None and self._route_choice_branches_are_live(
            route_semantics.branches
        )

    def _route_guard_exists_state(self, expr: model.Expr) -> bool | None:
        if isinstance(expr, model.ExprRef):
            return True if expr.parts == ("route", "exists") else None
        if isinstance(expr, model.ExprBinary):
            if expr.op in {"==", "!="}:
                left_is_route = isinstance(expr.left, model.ExprRef) and expr.left.parts == (
                    "route",
                    "exists",
                )
                right_is_route = isinstance(expr.right, model.ExprRef) and expr.right.parts == (
                    "route",
                    "exists",
                )
                if left_is_route and isinstance(expr.right, bool):
                    return expr.right if expr.op == "==" else not expr.right
                if right_is_route and isinstance(expr.left, bool):
                    return expr.left if expr.op == "==" else not expr.left
            if expr.op == "and":
                left = self._route_guard_exists_state(expr.left)
                right = self._route_guard_exists_state(expr.right)
                if left is False or right is False:
                    return False
                if left is True or right is True:
                    return True
        return None

    def _route_guard_review_verdict(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> str | None:
        if isinstance(expr, model.ExprBinary):
            if expr.op == "and":
                left = self._route_guard_review_verdict(expr.left, unit=unit)
                right = self._route_guard_review_verdict(expr.right, unit=unit)
                if left is None:
                    return right
                if right is None:
                    return left
                return left if left == right else None
            if expr.op == "==":
                left_is_verdict = isinstance(expr.left, model.ExprRef) and expr.left.parts == (
                    "verdict",
                )
                right_is_verdict = isinstance(expr.right, model.ExprRef) and expr.right.parts == (
                    "verdict",
                )
                if left_is_verdict:
                    return self._resolve_constant_enum_member(expr.right, unit=unit)
                if right_is_verdict:
                    return self._resolve_constant_enum_member(expr.left, unit=unit)
        return None

    def _route_guard_choice_match(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> tuple[str, str, bool] | None:
        if not isinstance(expr, model.ExprBinary):
            return None
        if expr.op == "and":
            return None
        if expr.op not in {"==", "!="}:
            return None
        left_parts = expr.left.parts if isinstance(expr.left, model.ExprRef) else None
        right_parts = expr.right.parts if isinstance(expr.right, model.ExprRef) else None
        invert = expr.op == "!="
        if left_parts is not None:
            expected = self._route_guard_choice_expected_value(
                left_parts,
                expr.right,
                unit=unit,
            )
            if expected is not None:
                return (left_parts[-1] if len(left_parts) > 2 else "choice", expected, invert)
        if right_parts is not None:
            expected = self._route_guard_choice_expected_value(
                right_parts,
                expr.left,
                unit=unit,
            )
            if expected is not None:
                return (right_parts[-1] if len(right_parts) > 2 else "choice", expected, invert)
        return None

    def _route_guard_choice_expected_value(
        self,
        parts: tuple[str, ...],
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> str | None:
        if not parts or parts[0] != "route" or parts[1] != "choice":
            return None
        if len(parts) == 2:
            return self._resolve_constant_enum_member(expr, unit=unit)
        if len(parts) != 3:
            return None
        if parts[2] == "key":
            if isinstance(expr, str):
                return expr
            if isinstance(expr, model.ExprRef):
                identity = self._resolve_enum_member_identity(expr, unit=unit)
                if identity is not None:
                    return identity[2]
            return None
        if parts[2] == "wire":
            return self._resolve_constant_enum_member(expr, unit=unit)
        if parts[2] == "title":
            return expr if isinstance(expr, str) else None
        return None

    def _narrow_route_semantics_for_choice(
        self,
        route_semantics: RouteSemanticContext,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> RouteSemanticContext:
        if not self._route_choice_branches_are_live(route_semantics.branches):
            return route_semantics
        if isinstance(expr, model.ExprBinary) and expr.op == "and":
            narrowed = self._narrow_route_semantics_for_choice(route_semantics, expr.left, unit=unit)
            return self._narrow_route_semantics_for_choice(narrowed, expr.right, unit=unit)
        match = self._route_guard_choice_match(expr, unit=unit)
        if match is None:
            return route_semantics
        field_name, expected, invert = match
        matching: list[RouteSemanticBranch] = []
        for branch in route_semantics.branches:
            filtered = tuple(
                member
                for member in branch.choice_members
                if self._route_choice_member_matches(member, field_name=field_name, expected=expected)
                != invert
            )
            if not filtered:
                continue
            matching.append(replace(branch, choice_members=filtered))
        has_unrouted_branch = route_semantics.has_unrouted_branch and not matching
        return RouteSemanticContext(
            branches=tuple(matching),
            has_unrouted_branch=has_unrouted_branch,
            route_required=route_semantics.route_required,
        )

    def _route_choice_member_matches(
        self,
        member: RouteChoiceMember,
        *,
        field_name: str,
        expected: str,
    ) -> bool:
        if field_name == "choice":
            return member.member_wire == expected
        if field_name == "key":
            return member.member_key == expected
        if field_name == "title":
            return member.member_title == expected
        if field_name == "wire":
            return member.member_wire == expected
        return False

    def _route_semantics_for_review_verdict(
        self,
        route_semantics: RouteSemanticContext,
        verdict: str,
    ) -> RouteSemanticContext:
        matching = tuple(
            branch for branch in route_semantics.branches if branch.review_verdict in {None, verdict}
        )
        has_unrouted_branch = route_semantics.has_unrouted_branch and not matching
        return RouteSemanticContext(
            branches=matching,
            has_unrouted_branch=has_unrouted_branch,
            route_required=route_semantics.route_required,
        )
