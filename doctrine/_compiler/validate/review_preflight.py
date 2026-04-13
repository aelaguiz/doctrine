from __future__ import annotations

from doctrine import model
from dataclasses import replace

from doctrine._compiler.constants import _REVIEW_REQUIRED_FIELD_NAMES
from doctrine._compiler.resolved_types import (
    AgentContract,
    CompileError,
    IndexedUnit,
    ReviewContractSpec,
    ReviewGateCheck,
    ReviewOutcomeBranch,
    ReviewPreSectionBranch,
)
from doctrine._compiler.validate.routes import (
    _LAW_TARGET_ALLOWED_KINDS,
    _PRESERVE_TARGET_ALLOWED_KINDS,
)


class ValidateReviewPreflightMixin:
    """Review pre-outcome validation helpers for ValidateMixin."""

    def _validate_review_field_bindings(
        self,
        fields: model.ReviewFieldsConfig,
        *,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        owner_label: str,
        require_blocked_gate: bool,
        require_active_mode: bool,
        require_trigger_reason: bool,
    ) -> dict[str, tuple[str, ...]]:
        bindings: dict[str, tuple[str, ...]] = {}
        for binding in fields.bindings:
            if binding.semantic_field in bindings:
                raise CompileError(
                    f"Duplicate review field binding in {owner_label}: {binding.semantic_field}"
                )
            self._resolve_output_field_node(
                output_decl,
                path=binding.field_path,
                unit=output_unit,
                owner_label=owner_label,
                surface_label="review field binding",
            )
            bindings[binding.semantic_field] = binding.field_path

        required = set(_REVIEW_REQUIRED_FIELD_NAMES)
        if require_blocked_gate:
            required.add("blocked_gate")
        if require_active_mode:
            required.add("active_mode")
        if require_trigger_reason:
            required.add("trigger_reason")
        missing = sorted(required - set(bindings))
        if missing:
            raise CompileError(
                f"Review fields are incomplete in {owner_label}: {', '.join(missing)}"
            )
        return bindings

    def _count_review_accept_stmts(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
    ) -> int:
        count = 0
        for item in items:
            if isinstance(item, model.ReviewAcceptStmt):
                count += 1
            elif isinstance(item, model.ReviewPreOutcomeWhenStmt):
                count += self._count_review_accept_stmts(item.items)
            elif isinstance(item, model.ReviewPreOutcomeMatchStmt):
                for case in item.cases:
                    count += self._count_review_accept_stmts(case.items)
        return count

    def _review_items_contain_blocks(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
    ) -> bool:
        for item in items:
            if isinstance(item, model.ReviewBlockStmt):
                return True
            if isinstance(item, model.ReviewPreOutcomeWhenStmt) and self._review_items_contain_blocks(
                item.items
            ):
                return True
            if isinstance(item, model.ReviewPreOutcomeMatchStmt):
                for case in item.cases:
                    if self._review_items_contain_blocks(case.items):
                        return True
        return False

    def _collect_review_carried_fields(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
    ) -> tuple[str, ...]:
        fields: list[str] = []
        for item in items:
            if isinstance(item, model.ReviewCarryStmt):
                fields.append(item.field_name)
                continue
            if isinstance(item, model.ReviewOutcomeWhenStmt):
                fields.extend(self._collect_review_carried_fields(item.items))
                continue
            if isinstance(item, model.ReviewOutcomeMatchStmt):
                for case in item.cases:
                    fields.extend(self._collect_review_carried_fields(case.items))
        return tuple(fields)

    def _validate_review_pre_outcome_items(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        agent_contract: AgentContract,
    ) -> None:
        for item in items:
            if isinstance(item, model.ReviewPreOutcomeWhenStmt):
                self._validate_review_pre_outcome_items(
                    item.items,
                    unit=unit,
                    owner_label=owner_label,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                    agent_contract=agent_contract,
                )
                continue
            if isinstance(item, model.ReviewPreOutcomeMatchStmt):
                self._validate_review_match_cases(
                    item.cases,
                    unit=unit,
                    owner_label=owner_label,
                )
                for case in item.cases:
                    self._validate_review_pre_outcome_items(
                        case.items,
                        unit=unit,
                        owner_label=owner_label,
                        contract_spec=contract_spec,
                        section_titles=section_titles,
                        agent_contract=agent_contract,
                    )
                continue
            if isinstance(item, (model.ReviewBlockStmt, model.ReviewRejectStmt, model.ReviewAcceptStmt)):
                self._validate_review_gate_label(
                    item.gate,
                    contract_spec=contract_spec,
                    section_titles=section_titles,
                    owner_label=owner_label,
                )
                continue
            if isinstance(item, model.OwnOnlyStmt):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=self._law_stmt_name(item),
                    allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["own_only"],
                )
                continue
            if isinstance(item, (model.SupportOnlyStmt, model.IgnoreStmt)):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=self._law_stmt_name(item),
                    allowed_kinds=_LAW_TARGET_ALLOWED_KINDS["path_set"],
                )
                continue
            if isinstance(item, model.PreserveStmt):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label=f"preserve {item.kind}",
                    allowed_kinds=_PRESERVE_TARGET_ALLOWED_KINDS[item.kind],
                )

    def _validate_review_gate_label(
        self,
        gate: model.ReviewGateLabel,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
    ) -> None:
        if isinstance(gate, model.ContractGateRef):
            if gate.key not in {item.key for item in contract_spec.gates}:
                raise CompileError(
                    f"Unknown review contract gate in {owner_label}: contract.{gate.key}"
                )
            return
        if isinstance(gate, model.SectionGateRef) and gate.key not in section_titles:
            raise CompileError(f"Unknown review section gate in {owner_label}: {gate.key}")

    def _collect_review_pre_section_branches(
        self,
        section: model.ReviewSection,
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
    ) -> tuple[ReviewPreSectionBranch, ...]:
        return self._collect_review_pre_outcome_leaf_branches(
            section.items,
            unit=unit,
            contract_spec=contract_spec,
            section_titles=section_titles,
            owner_label=owner_label,
        )

    def _collect_review_pre_outcome_leaf_branches(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        branch: ReviewPreSectionBranch | None = None,
    ) -> tuple[ReviewPreSectionBranch, ...]:
        branches = (branch or ReviewPreSectionBranch(),)
        index = 0
        while index < len(items):
            item = items[index]
            if isinstance(item, model.ReviewPreOutcomeWhenStmt):
                next_branches: list[ReviewPreSectionBranch] = []
                for current_branch in branches:
                    condition = self._evaluate_review_condition(
                        item.expr,
                        unit=unit,
                        branch=ReviewOutcomeBranch(),
                    )
                    if condition is not False:
                        next_branches.extend(
                            self._collect_review_pre_outcome_leaf_branches(
                                item.items,
                                unit=unit,
                                contract_spec=contract_spec,
                                section_titles=section_titles,
                                owner_label=owner_label,
                                branch=current_branch,
                            )
                        )
                    if condition is not True:
                        next_branches.append(current_branch)
                branches = tuple(next_branches)
                index += 1
                continue
            if isinstance(item, model.ReviewPreOutcomeMatchStmt):
                next_branches: list[ReviewPreSectionBranch] = []
                for current_branch in branches:
                    next_branches.extend(
                        self._collect_review_pre_match_branches(
                            item,
                            unit=unit,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                            owner_label=owner_label,
                            branch=current_branch,
                        )
                    )
                branches = tuple(next_branches)
                index += 1
                continue

            next_branches = []
            for current_branch in branches:
                next_branches.append(
                    self._branch_with_review_pre_outcome_stmt(
                        current_branch,
                        item,
                        contract_spec=contract_spec,
                        section_titles=section_titles,
                    )
                )
            branches = tuple(next_branches)
            index += 1
        return branches

    def _collect_review_pre_match_branches(
        self,
        stmt: model.ReviewPreOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        branch: ReviewPreSectionBranch,
    ) -> tuple[ReviewPreSectionBranch, ...]:
        selected: list[ReviewPreSectionBranch] = []
        pending = [branch]
        empty_branch = ReviewOutcomeBranch()

        for case in stmt.cases:
            next_pending: list[ReviewPreSectionBranch] = []
            for current_branch in pending:
                if case.head is None:
                    selected.extend(
                        self._collect_review_pre_outcome_leaf_branches(
                            case.items,
                            unit=unit,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                            owner_label=owner_label,
                            branch=current_branch,
                        )
                    )
                    continue
                condition = self._review_match_head_matches(
                    stmt.expr,
                    case.head,
                    unit=unit,
                    branch=empty_branch,
                )
                if condition is not False:
                    selected.extend(
                        self._collect_review_pre_outcome_leaf_branches(
                            case.items,
                            unit=unit,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                            owner_label=owner_label,
                            branch=current_branch,
                        )
                    )
                if condition is not True:
                    next_pending.append(current_branch)
            pending = next_pending

        if pending and not self._review_pre_match_is_exhaustive(stmt, unit=unit):
            selected.extend(pending)
        return tuple(selected)

    def _review_pre_match_is_exhaustive(
        self,
        stmt: model.ReviewPreOutcomeMatchStmt,
        *,
        unit: IndexedUnit,
    ) -> bool:
        outcome_stmt = model.ReviewOutcomeMatchStmt(
            expr=stmt.expr,
            cases=tuple(
                model.ReviewOutcomeMatchArm(head=case.head, items=())
                for case in stmt.cases
            ),
        )
        return self._review_match_is_exhaustive(outcome_stmt, unit=unit)

    def _branch_with_review_pre_outcome_stmt(
        self,
        branch: ReviewPreSectionBranch,
        stmt: model.ReviewPreOutcomeStmt,
        *,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
    ) -> ReviewPreSectionBranch:
        if isinstance(stmt, model.ReviewBlockStmt):
            return replace(
                branch,
                block_checks=(
                    *branch.block_checks,
                    ReviewGateCheck(
                        identity=self._review_gate_identity(
                            stmt.gate,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                        ),
                        expr=stmt.expr,
                    ),
                ),
            )
        if isinstance(stmt, model.ReviewRejectStmt):
            return replace(
                branch,
                reject_checks=(
                    *branch.reject_checks,
                    ReviewGateCheck(
                        identity=self._review_gate_identity(
                            stmt.gate,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                        ),
                        expr=stmt.expr,
                    ),
                ),
            )
        if isinstance(stmt, model.ReviewAcceptStmt):
            return replace(
                branch,
                accept_checks=(
                    *branch.accept_checks,
                    ReviewGateCheck(
                        identity=self._review_gate_identity(
                            stmt.gate,
                            contract_spec=contract_spec,
                            section_titles=section_titles,
                        ),
                        expr=stmt.expr,
                    ),
                ),
            )
        if isinstance(stmt, (model.PreserveStmt, model.SupportOnlyStmt, model.IgnoreStmt)):
            return replace(branch, has_assertions=True)
        return branch
