from __future__ import annotations

from doctrine import model
from doctrine._compiler.resolved_types import (
    CompileError,
    IndexedUnit,
    ResolvedReviewGateBranch,
    ReviewContractSpec,
    ReviewGateCheck,
    ReviewGateObservation,
    ReviewOutcomeBranch,
)


class ValidateReviewGateObservationMixin:
    """Review gate observation helpers for ValidateMixin."""

    def _review_gate_observation_with_accept_checks(
        self,
        observation: ReviewGateObservation,
        *,
        accept_checks: tuple[ReviewGateCheck, ...],
    ) -> ReviewGateObservation:
        flags = {
            "needs_blocked_gate_presence": observation.needs_blocked_gate_presence,
            "needs_blocked_gate_value": observation.needs_blocked_gate_value,
            "needs_failing_gates_presence": observation.needs_failing_gates_presence,
            "needs_failing_gates_value": observation.needs_failing_gates_value,
            "needs_contract_failed_gates_value": observation.needs_contract_failed_gates_value,
            "needs_contract_first_failed_gate": observation.needs_contract_first_failed_gate,
            "needs_contract_passes": observation.needs_contract_passes,
        }
        referenced_contract_gate_ids = set(observation.referenced_contract_gate_ids)
        for check in accept_checks:
            self._collect_review_gate_observation_from_expr(
                check.expr,
                flags=flags,
                referenced_contract_gate_ids=referenced_contract_gate_ids,
            )
        return ReviewGateObservation(
            needs_blocked_gate_presence=flags["needs_blocked_gate_presence"],
            needs_blocked_gate_value=flags["needs_blocked_gate_value"],
            needs_failing_gates_presence=flags["needs_failing_gates_presence"],
            needs_failing_gates_value=flags["needs_failing_gates_value"],
            needs_contract_failed_gates_value=flags["needs_contract_failed_gates_value"],
            needs_contract_first_failed_gate=flags["needs_contract_first_failed_gate"],
            needs_contract_passes=flags["needs_contract_passes"],
            referenced_contract_gate_ids=tuple(sorted(referenced_contract_gate_ids)),
        )

    def _review_contract_failure_states(
        self,
        contract_spec: ReviewContractSpec,
        *,
        observation: ReviewGateObservation,
    ) -> tuple[tuple[str, ...], ...]:
        gate_ids = tuple(f"contract.{gate.key}" for gate in contract_spec.gates)
        if not gate_ids:
            return ((),)

        if observation.needs_contract_failed_gates_value:
            return self._enumerate_review_contract_failure_states(gate_ids)

        referenced = set(observation.referenced_contract_gate_ids)
        referenced_gate_ids = tuple(gate_id for gate_id in gate_ids if gate_id in referenced)
        unreferenced_gate_ids = tuple(gate_id for gate_id in gate_ids if gate_id not in referenced)

        states: list[tuple[str, ...]] = [()]
        seen = {()}

        def add(state: tuple[str, ...]) -> None:
            if state in seen:
                return
            seen.add(state)
            states.append(state)

        for state in self._enumerate_review_contract_failure_states(referenced_gate_ids):
            if state:
                add(state)

        if unreferenced_gate_ids:
            add((unreferenced_gate_ids[0],))

        if observation.needs_contract_first_failed_gate:
            for gate_id in gate_ids:
                add((gate_id,))

        if observation.needs_contract_passes and len(states) == 1:
            add((gate_ids[0],))

        if len(states) == 1:
            add((gate_ids[0],))

        return tuple(states)

    def _enumerate_review_contract_failure_states(
        self,
        gate_ids: tuple[str, ...],
    ) -> tuple[tuple[str, ...], ...]:
        states: list[tuple[str, ...]] = [()]
        for gate_id in gate_ids:
            next_states: list[tuple[str, ...]] = []
            for state in states:
                next_states.append(state)
                next_states.append((*state, gate_id))
            states = next_states
        return tuple(states)

    def _evaluate_review_gate_condition(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        contract_failed_gate_ids: tuple[str, ...],
    ) -> bool | None:
        return self._evaluate_review_gate_condition_with_branch(
            expr,
            unit=unit,
            branch=ReviewOutcomeBranch(),
            contract_failed_gate_ids=contract_failed_gate_ids,
        )

    def _evaluate_review_gate_condition_with_branch(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
        contract_failed_gate_ids: tuple[str, ...],
    ) -> bool | None:
        if isinstance(expr, model.ExprBinary):
            if expr.op == "and":
                left = self._evaluate_review_gate_condition_with_branch(
                    expr.left,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                right = self._evaluate_review_gate_condition_with_branch(
                    expr.right,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                if left is False or right is False:
                    return False
                if left is True and right is True:
                    return True
                return None
            if expr.op == "or":
                left = self._evaluate_review_gate_condition_with_branch(
                    expr.left,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                right = self._evaluate_review_gate_condition_with_branch(
                    expr.right,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                if left is True or right is True:
                    return True
                if left is False and right is False:
                    return False
                return None

        left = self._resolve_review_gate_expr_constant(
            expr,
            unit=unit,
            branch=branch,
            contract_failed_gate_ids=contract_failed_gate_ids,
        )
        if isinstance(left, bool):
            return left
        if not isinstance(expr, model.ExprBinary):
            return None
        left = self._resolve_review_gate_expr_constant(
            expr.left,
            unit=unit,
            branch=branch,
            contract_failed_gate_ids=contract_failed_gate_ids,
        )
        right = self._resolve_review_gate_expr_constant(
            expr.right,
            unit=unit,
            branch=branch,
            contract_failed_gate_ids=contract_failed_gate_ids,
        )
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

    def _validate_review_match_cases(
        self,
        cases: tuple[model.ReviewPreOutcomeMatchArm | model.ReviewOutcomeMatchArm, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        if any(case.head is None for case in cases):
            return

        enum_decl: model.EnumDecl | None = None
        seen_members: set[str] = set()
        for case in cases:
            if case.head is None:
                continue
            for option in case.head.options:
                resolved = self._resolve_review_match_option(option, unit=unit)
                if resolved is None:
                    return
                option_enum_decl, member_value = resolved
                if enum_decl is None:
                    enum_decl = option_enum_decl
                elif enum_decl.name != option_enum_decl.name:
                    return
                seen_members.add(member_value)

        if enum_decl is None:
            return

        expected_members = {member.value for member in enum_decl.members}
        if seen_members != expected_members:
            raise CompileError(
                f"Review match must be exhaustive or include else in {owner_label}"
            )

    def _compress_review_gate_branches_for_validation(
        self,
        gate_branches: tuple[ResolvedReviewGateBranch, ...],
        *,
        output_decl: model.OutputDecl,
        field_bindings: dict[str, tuple[str, ...]],
    ) -> tuple[ResolvedReviewGateBranch, ...]:
        observation = self._review_gate_observation(output_decl)
        deduped: dict[tuple[object, ...], ResolvedReviewGateBranch] = {}
        for branch in gate_branches:
            deduped.setdefault(
                self._review_gate_branch_validation_key(
                    branch,
                    observation=observation,
                    preserve_blocked_gate_presence="blocked_gate" in field_bindings,
                ),
                branch,
            )
        return tuple(deduped.values())

    def _review_gate_branch_validation_key(
        self,
        branch: ResolvedReviewGateBranch,
        *,
        observation: ReviewGateObservation,
        preserve_blocked_gate_presence: bool = False,
    ) -> tuple[object, ...]:
        contract_failed_gate_ids = tuple(
            gate_id for gate_id in branch.failing_gate_ids if gate_id.startswith("contract.")
        )
        key: list[object] = [branch.verdict]

        if observation.needs_failing_gates_value:
            key.append(branch.failing_gate_ids)
        elif observation.needs_failing_gates_presence:
            key.append(bool(branch.failing_gate_ids))

        if observation.needs_blocked_gate_value:
            key.append(branch.blocked_gate_id)
        elif observation.needs_blocked_gate_presence:
            key.append(branch.blocked_gate_id is not None)
        elif preserve_blocked_gate_presence:
            key.append(branch.blocked_gate_id is not None)

        if observation.needs_contract_failed_gates_value:
            key.append(contract_failed_gate_ids)
        elif observation.needs_contract_first_failed_gate:
            key.append(contract_failed_gate_ids[0] if contract_failed_gate_ids else None)
        elif observation.needs_contract_passes:
            key.append(not contract_failed_gate_ids)

        if observation.referenced_contract_gate_ids:
            key.append(
                tuple(
                    gate_id in contract_failed_gate_ids
                    for gate_id in observation.referenced_contract_gate_ids
                )
            )

        return tuple(key)

    def _review_gate_observation(self, output_decl: model.OutputDecl) -> ReviewGateObservation:
        flags = {
            "needs_blocked_gate_presence": False,
            "needs_blocked_gate_value": False,
            "needs_failing_gates_presence": False,
            "needs_failing_gates_value": False,
            "needs_contract_failed_gates_value": False,
            "needs_contract_first_failed_gate": False,
            "needs_contract_passes": False,
        }
        referenced_contract_gate_ids: set[str] = set()

        self._collect_review_gate_observation_from_output_items(
            output_decl.items,
            flags=flags,
            referenced_contract_gate_ids=referenced_contract_gate_ids,
        )
        for item in output_decl.trust_surface:
            if item.when_expr is None:
                continue
            self._collect_review_gate_observation_from_expr(
                item.when_expr,
                flags=flags,
                referenced_contract_gate_ids=referenced_contract_gate_ids,
            )

        return ReviewGateObservation(
            needs_blocked_gate_presence=flags["needs_blocked_gate_presence"],
            needs_blocked_gate_value=flags["needs_blocked_gate_value"],
            needs_failing_gates_presence=flags["needs_failing_gates_presence"],
            needs_failing_gates_value=flags["needs_failing_gates_value"],
            needs_contract_failed_gates_value=flags["needs_contract_failed_gates_value"],
            needs_contract_first_failed_gate=flags["needs_contract_first_failed_gate"],
            needs_contract_passes=flags["needs_contract_passes"],
            referenced_contract_gate_ids=tuple(sorted(referenced_contract_gate_ids)),
        )

    def _collect_review_gate_observation_from_output_items(
        self,
        items: tuple[model.OutputRecordItem, ...] | tuple[model.AnyRecordItem, ...],
        *,
        flags: dict[str, bool],
        referenced_contract_gate_ids: set[str],
    ) -> None:
        for item in items:
            if isinstance(item, (model.GuardedOutputSection, model.GuardedOutputScalar)):
                self._collect_review_gate_observation_from_expr(
                    item.when_expr,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )
                nested_items = item.items if isinstance(item, model.GuardedOutputSection) else item.body
                if nested_items is not None:
                    self._collect_review_gate_observation_from_output_items(
                        nested_items,
                        flags=flags,
                        referenced_contract_gate_ids=referenced_contract_gate_ids,
                    )
                continue
            if isinstance(item, model.RecordSection):
                self._collect_review_gate_observation_from_output_items(
                    item.items,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )
                continue
            if isinstance(item, model.RecordScalar) and item.body is not None:
                self._collect_review_gate_observation_from_output_items(
                    item.body,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )

    def _collect_review_gate_observation_from_expr(
        self,
        expr: model.Expr,
        *,
        flags: dict[str, bool],
        referenced_contract_gate_ids: set[str],
    ) -> None:
        if isinstance(expr, model.ExprBinary):
            self._collect_review_gate_observation_from_expr(
                expr.left,
                flags=flags,
                referenced_contract_gate_ids=referenced_contract_gate_ids,
            )
            self._collect_review_gate_observation_from_expr(
                expr.right,
                flags=flags,
                referenced_contract_gate_ids=referenced_contract_gate_ids,
            )
            return

        if isinstance(expr, model.ExprSet):
            for item in expr.items:
                self._collect_review_gate_observation_from_expr(
                    item,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )
            return

        if isinstance(expr, model.ExprCall):
            if expr.name in {"present", "missing"} and len(expr.args) == 1:
                field_name = (
                    self._review_semantic_field_ref_name(expr.args[0])
                    if isinstance(expr.args[0], model.ExprRef)
                    else None
                )
                if field_name == "blocked_gate":
                    flags["needs_blocked_gate_presence"] = True
                elif field_name == "failing_gates":
                    flags["needs_failing_gates_presence"] = True
                return
            if expr.name in {"failed", "passed"} and len(expr.args) == 1:
                gate_identity = self._resolve_review_contract_gate_identity(expr.args[0])
                if gate_identity is not None:
                    referenced_contract_gate_ids.add(gate_identity)
            for arg in expr.args:
                self._collect_review_gate_observation_from_expr(
                    arg,
                    flags=flags,
                    referenced_contract_gate_ids=referenced_contract_gate_ids,
                )
            return

        if isinstance(expr, model.ExprRef):
            field_name = self._review_semantic_field_ref_name(expr)
            if field_name == "blocked_gate":
                flags["needs_blocked_gate_value"] = True
                return
            if field_name == "failing_gates":
                flags["needs_failing_gates_value"] = True
                return
            if len(expr.parts) == 2 and expr.parts[0] == "contract":
                if expr.parts[1] == "failed_gates":
                    flags["needs_contract_failed_gates_value"] = True
                elif expr.parts[1] == "first_failed_gate":
                    flags["needs_contract_first_failed_gate"] = True
                elif expr.parts[1] == "passes":
                    flags["needs_contract_passes"] = True
