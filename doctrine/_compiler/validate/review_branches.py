from __future__ import annotations

from dataclasses import replace

from doctrine._compiler.resolved_types import *  # noqa: F401,F403


class ValidateReviewBranchesMixin:
    """Review outcome branch helpers for ValidateMixin."""

    def _validate_review_outcome_items(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        for item in items:
            if isinstance(item, model.ReviewOutcomeWhenStmt):
                self._validate_review_outcome_items(
                    item.items,
                    unit=unit,
                    owner_label=owner_label,
                )
                continue
            if isinstance(item, model.ReviewOutcomeMatchStmt):
                self._validate_review_match_cases(
                    item.cases,
                    unit=unit,
                    owner_label=owner_label,
                )
                for case in item.cases:
                    self._validate_review_outcome_items(
                        case.items,
                        unit=unit,
                        owner_label=owner_label,
                    )
                continue
            if isinstance(item, model.ReviewOutcomeRouteStmt):
                self._validate_route_target(item.target, unit=unit)

    def _collect_review_outcome_leaf_branches(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch | None = None,
    ) -> tuple[ReviewOutcomeBranch, ...]:
        branches = (branch or ReviewOutcomeBranch(),)
        index = 0
        while index < len(items):
            item = items[index]
            if isinstance(item, model.ReviewOutcomeWhenStmt):
                next_branches: list[ReviewOutcomeBranch] = []
                for current_branch in branches:
                    condition = self._evaluate_review_condition(
                        item.expr,
                        unit=unit,
                        branch=current_branch,
                    )
                    if condition is not False:
                        next_branches.extend(
                            self._collect_review_outcome_leaf_branches(
                                item.items,
                                unit=unit,
                                branch=current_branch,
                            )
                        )
                    if condition is not True:
                        next_branches.append(current_branch)
                branches = tuple(next_branches)
            elif isinstance(item, model.ReviewOutcomeMatchStmt):
                next_branches: list[ReviewOutcomeBranch] = []
                for current_branch in branches:
                    next_branches.extend(
                        self._collect_review_outcome_match_branches(
                            item,
                            unit=unit,
                            branch=current_branch,
                        )
                    )
                branches = tuple(next_branches)
            else:
                next_branches = []
                for current_branch in branches:
                    next_branches.extend(
                        self._branch_with_review_outcome_stmt(
                            current_branch,
                            item,
                            unit=unit,
                        )
                    )
                branches = tuple(next_branches)
            index += 1
        return branches

    def _branch_with_review_outcome_stmt(
        self,
        branch: ReviewOutcomeBranch,
        stmt: model.ReviewOutcomeStmt,
        *,
        unit: IndexedUnit,
    ) -> tuple[ReviewOutcomeBranch, ...]:
        if isinstance(stmt, (model.ReviewCurrentArtifactStmt, model.ReviewCurrentNoneStmt)):
            if stmt.when_expr is None:
                return (replace(branch, currents=(*branch.currents, stmt)),)
            condition = self._evaluate_review_condition(
                stmt.when_expr,
                unit=unit,
                branch=branch,
            )
            if condition is True:
                return (replace(branch, currents=(*branch.currents, stmt)),)
            if condition is False:
                return (branch,)
            true_branch = self._assume_review_outcome_condition(
                branch,
                stmt.when_expr,
                expected=True,
            )
            false_branch = self._assume_review_outcome_condition(
                branch,
                stmt.when_expr,
                expected=False,
            )
            branches: list[ReviewOutcomeBranch] = []
            if true_branch is not None:
                branches.append(replace(true_branch, currents=(*true_branch.currents, stmt)))
            if false_branch is not None:
                branches.append(false_branch)
            if branches:
                return tuple(branches)
            return (
                replace(branch, currents=(*branch.currents, stmt)),
                branch,
            )
        if isinstance(stmt, model.ReviewCarryStmt):
            return (replace(branch, carries=(*branch.carries, stmt)),)
        if isinstance(stmt, model.ReviewOutcomeRouteStmt):
            if branch.route_selected:
                return (branch,)
            if stmt.when_expr is None:
                return (
                    replace(
                        branch,
                        routes=(*branch.routes, stmt),
                        route_selected=True,
                    ),
                )
            condition = self._evaluate_review_condition(
                stmt.when_expr,
                unit=unit,
                branch=branch,
            )
            if condition is True:
                return (
                    replace(
                        branch,
                        routes=(*branch.routes, stmt),
                        route_selected=True,
                    ),
                )
            if condition is False:
                return (branch,)
            return (
                replace(
                    branch,
                    routes=(*branch.routes, stmt),
                    route_selected=True,
                ),
                branch,
            )
        return (branch,)

    def _assume_review_outcome_condition(
        self,
        branch: ReviewOutcomeBranch,
        expr: model.Expr,
        *,
        expected: bool,
    ) -> ReviewOutcomeBranch | None:
        if (
            isinstance(expr, model.ExprCall)
            and expr.name in {"present", "missing"}
            and len(expr.args) == 1
            and isinstance(expr.args[0], model.ExprRef)
            and expr.args[0].parts == ("blocked_gate",)
        ):
            blocked_gate_present = expected if expr.name == "present" else not expected
            if (
                branch.blocked_gate_present is not None
                and branch.blocked_gate_present != blocked_gate_present
            ):
                return None
            return replace(branch, blocked_gate_present=blocked_gate_present)
        return None

    def _collect_review_outcome_match_branches(
        self,
        stmt: model.ReviewOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
    ) -> tuple[ReviewOutcomeBranch, ...]:
        selected: list[ReviewOutcomeBranch] = []
        pending = [branch]

        for case in stmt.cases:
            next_pending: list[ReviewOutcomeBranch] = []
            for current_branch in pending:
                if case.head is None:
                    selected.extend(
                        self._collect_review_outcome_leaf_branches(
                            case.items,
                            unit=unit,
                            branch=current_branch,
                        )
                    )
                    continue

                condition = self._review_match_head_matches(
                    stmt.expr,
                    case.head,
                    unit=unit,
                    branch=current_branch,
                )
                if condition is not False:
                    selected.extend(
                        self._collect_review_outcome_leaf_branches(
                            case.items,
                            unit=unit,
                            branch=current_branch,
                        )
                    )
                if condition is not True:
                    next_pending.append(current_branch)
            pending = next_pending

        if pending and not self._review_match_is_exhaustive(stmt, unit=unit):
            selected.extend(pending)
        return tuple(selected)

    def _review_match_head_matches(
        self,
        expr: model.Expr,
        head: model.ReviewMatchHead,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
    ) -> bool | None:
        subject_value = self._resolve_review_expr_constant(expr, unit=unit, branch=branch)
        matched = False
        saw_unknown_option = False
        if subject_value is None:
            option_result: bool | None = None
        else:
            option_result = False
            for option in head.options:
                option_value = self._resolve_review_expr_constant(option, unit=unit, branch=branch)
                if option_value is None:
                    saw_unknown_option = True
                    continue
                if subject_value == option_value:
                    matched = True
                    option_result = True
                    break
            if not matched and saw_unknown_option:
                option_result = None
        if option_result is False:
            return False
        if head.when_expr is None:
            return option_result
        guard_result = self._evaluate_review_condition(
            head.when_expr,
            unit=unit,
            branch=branch,
        )
        return self._combine_review_condition(option_result, guard_result)

    def _review_match_is_exhaustive(
        self,
        stmt: model.ReviewOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
    ) -> bool:
        if any(case.head is None for case in stmt.cases):
            return True

        enum_decl: model.EnumDecl | None = None
        seen_members: set[str] = set()
        for case in stmt.cases:
            if case.head is None or case.head.when_expr is not None:
                return False
            for option in case.head.options:
                resolved = self._resolve_review_match_option(option, unit=unit)
                if resolved is None:
                    return False
                option_enum_decl, member_value = resolved
                if enum_decl is None:
                    enum_decl = option_enum_decl
                elif enum_decl.name != option_enum_decl.name:
                    return False
                seen_members.add(member_value)

        if enum_decl is None:
            return False
        return seen_members == {member.value for member in enum_decl.members}

    def _evaluate_review_condition(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
    ) -> bool | None:
        constant = self._resolve_review_expr_constant(expr, unit=unit, branch=branch)
        if isinstance(constant, bool):
            return constant
        if not isinstance(expr, model.ExprBinary):
            return None

        if expr.op == "and":
            left = self._evaluate_review_condition(expr.left, unit=unit, branch=branch)
            right = self._evaluate_review_condition(expr.right, unit=unit, branch=branch)
            if left is False or right is False:
                return False
            if left is True and right is True:
                return True
            return None
        if expr.op == "or":
            left = self._evaluate_review_condition(expr.left, unit=unit, branch=branch)
            right = self._evaluate_review_condition(expr.right, unit=unit, branch=branch)
            if left is True or right is True:
                return True
            if left is False and right is False:
                return False
            return None

        left = self._resolve_review_expr_constant(expr.left, unit=unit, branch=branch)
        right = self._resolve_review_expr_constant(expr.right, unit=unit, branch=branch)
        if left is None or right is None:
            return None

        if expr.op == "==":
            return left == right
        if expr.op == "!=":
            return left != right
        if expr.op == "in":
            return self._review_membership_contains(right, left)
        if expr.op == "not in":
            return not self._review_membership_contains(right, left)
        if expr.op == ">":
            return left > right
        if expr.op == ">=":
            return left >= right
        if expr.op == "<":
            return left < right
        if expr.op == "<=":
            return left <= right
        return None

    def _combine_review_condition(
        self,
        left: bool | None,
        right: bool | None,
    ) -> bool | None:
        if left is False or right is False:
            return False
        if left is True and right is True:
            return True
        return None

    def _review_branch_proves_subject(
        self,
        branch: ReviewOutcomeBranch,
        *,
        unit: IndexedUnit,
        subject_keys: set[tuple[tuple[str, ...], str]],
        subject_map: model.ReviewSubjectMapConfig | None,
        current_subject_key: tuple[tuple[str, ...], str] | None,
        reviewed_subject_key: tuple[tuple[str, ...], str] | None,
        owner_label: str,
    ) -> bool:
        if current_subject_key is not None and current_subject_key in subject_keys:
            return True
        if reviewed_subject_key is not None and reviewed_subject_key in subject_keys:
            return True
        if subject_map is None:
            return False
        return (
            self._review_subject_key_from_subject_map(
                branch,
                unit=unit,
                subject_keys=subject_keys,
                subject_map=subject_map,
                owner_label=owner_label,
            )
            in subject_keys
        )

    def _validate_review_next_owner_binding(
        self,
        route: model.ReviewOutcomeRouteStmt,
        *,
        review_unit: IndexedUnit,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        field_path: tuple[str, ...],
        owner_label: str,
    ) -> None:
        field_node = self._resolve_output_field_node(
            output_decl,
            path=field_path,
            unit=output_unit,
            owner_label=owner_label,
            surface_label="review next_owner binding",
        )
        target = field_node.target
        if not isinstance(
            target,
            (
                model.RecordScalar,
                model.RecordSection,
                model.GuardedOutputSection,
                model.GuardedOutputScalar,
            ),
        ):
            raise CompileError(
                f"Review next_owner binding must point at an output field in {owner_label}: "
                f"{output_decl.name}.{'.'.join(field_path)}"
            )
        route_branch = self._route_semantic_branch_from_route(
            route,
            label=route.label,
            unit=review_unit,
        )
        self._validate_route_owner_alignment(
            target,
            route_branch=route_branch,
            unit=output_unit,
            fallback_unit=(
                review_unit if review_unit.module_parts != output_unit.module_parts else None
            ),
            owner_label=f"output {output_decl.name}.{'.'.join(field_path)}",
            error_message=(
                f"Review next_owner field must structurally bind the routed target in {owner_label}: "
                f"{output_decl.name}.{'.'.join(field_path)} -> {route_branch.target_name}"
            ),
        )
