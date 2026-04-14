from __future__ import annotations

from doctrine import model
from doctrine._compiler.constants import _REVIEW_CONTRACT_FACT_KEYS, _REVIEW_VERDICT_TEXT
from doctrine._compiler.naming import (
    _dotted_ref_name,
    _law_path_from_name_ref,
    _name_ref_from_dotted_name,
)
from doctrine._compiler.resolved_types import (
    AddressableNode,
    AgentContract,
    CompileError,
    IndexedUnit,
    ResolvedReviewAgreementBranch,
    ResolvedReviewBody,
    ResolvedReviewGateBranch,
    ReviewContractSpec,
    ReviewGateObservation,
    ReviewOutcomeBranch,
    ReviewPreOutcomeBranch,
    ReviewSemanticContext,
    ReviewSemanticContractRoot,
    ReviewSemanticFieldsRoot,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveReviewsMixin:
    """Review resolution helpers for ResolveMixin."""

    def _resolve_review_semantic_output_decl(
        self,
        review_semantics: ReviewSemanticContext,
    ) -> tuple[IndexedUnit, model.OutputDecl]:
        if review_semantics.output_module_parts:
            output_unit = self._load_module(review_semantics.output_module_parts)
        else:
            output_unit = self.root_unit
        output_decl = output_unit.outputs_by_name.get(review_semantics.output_name)
        if output_decl is None:
            raise CompileError(
                "Internal compiler error: missing review comment output while resolving "
                f"review semantics: {review_semantics.output_name}"
            )
        return output_unit, output_decl

    def _resolve_review_semantic_root_decl(
        self,
        ref: model.NameRef,
        *,
        review_semantics: ReviewSemanticContext | None,
    ) -> ReviewSemanticFieldsRoot | ReviewSemanticContractRoot | None:
        if review_semantics is None or ref.module_parts:
            return None
        node = self._review_semantic_root_node(ref.declaration_name, review_semantics)
        if node is None:
            return None
        target = node.target
        if isinstance(target, (ReviewSemanticFieldsRoot, ReviewSemanticContractRoot)):
            return target
        return None

    def _resolve_review_semantic_node(
        self,
        ref: model.AddressableRef,
        *,
        review_semantics: ReviewSemanticContext | None,
        owner_label: str,
        surface_label: str,
        ref_label: str,
    ) -> AddressableNode | None:
        if review_semantics is None:
            return None
        parts = self._review_semantic_addressable_parts(ref)
        if parts is None:
            return None
        root_node = self._review_semantic_root_node(parts[0], review_semantics)
        if root_node is None:
            return None
        return self._resolve_addressable_path_node(
            root_node,
            parts[1:],
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
        )

    def _resolve_review_subjects(
        self,
        subject: model.ReviewSubjectConfig,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[tuple[IndexedUnit, model.InputDecl | model.OutputDecl], ...]:
        resolved: list[tuple[IndexedUnit, model.InputDecl | model.OutputDecl]] = []
        seen: set[tuple[tuple[str, ...], str]] = set()
        for ref in subject.subjects:
            target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
            input_decl = target_unit.inputs_by_name.get(ref.declaration_name)
            output_decl = target_unit.outputs_by_name.get(ref.declaration_name)
            if input_decl is not None and output_decl is not None:
                raise CompileError(
                    f"Ambiguous review subject in {owner_label}: {_dotted_ref_name(ref)}"
                )
            if input_decl is None and output_decl is None:
                raise CompileError(
                    f"Review subject must resolve to an input or output declaration in {owner_label}: "
                    f"{_dotted_ref_name(ref)}"
                )
            decl = input_decl if input_decl is not None else output_decl
            key = (target_unit.module_parts, decl.name)
            if key in seen:
                raise CompileError(
                    f"Duplicate review subject in {owner_label}: {_dotted_ref_name(ref)}"
                )
            seen.add(key)
            resolved.append((target_unit, decl))
        return tuple(resolved)

    def _resolve_enum_member_identity(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, ...], str, str] | None:
        if not isinstance(expr, model.ExprRef) or len(expr.parts) < 2:
            return None
        enum_ref = _name_ref_from_dotted_name(".".join(expr.parts[:-1]))
        try:
            lookup_unit = self._resolve_readable_decl_lookup_unit(enum_ref, unit=unit)
        except CompileError:
            return None
        enum_decl = lookup_unit.enums_by_name.get(enum_ref.declaration_name)
        if enum_decl is None:
            return None
        member = next((member for member in enum_decl.members if member.key == expr.parts[-1]), None)
        if member is None:
            return None
        return (lookup_unit.module_parts, enum_decl.name, member.key)

    def _resolve_review_contract_spec(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ReviewContractSpec:
        contract_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        workflow_decl = contract_unit.workflows_by_name.get(ref.declaration_name)
        schema_decl = contract_unit.schemas_by_name.get(ref.declaration_name)
        dotted_name = _dotted_ref_name(ref)

        if workflow_decl is not None and schema_decl is not None:
            raise CompileError(f"Ambiguous review contract in {owner_label}: {dotted_name}")

        if workflow_decl is not None:
            workflow_body = self._resolve_workflow_decl(workflow_decl, unit=contract_unit)
            gates = self._collect_review_contract_gates(
                workflow_body,
                owner_label=(
                    f"{owner_label} contract "
                    f"{_dotted_decl_name(contract_unit.module_parts, workflow_decl.name)}"
                ),
            )
            if not gates:
                raise CompileError(
                    f"Review contract must export at least one gate in {owner_label}: {workflow_decl.name}"
                )
            return ReviewContractSpec(
                kind="workflow",
                title=workflow_body.title,
                gates=gates,
            )

        if schema_decl is not None:
            schema_body = self._resolve_schema_decl(schema_decl, unit=contract_unit)
            gates = self._collect_schema_review_contract_gates(
                schema_body,
                owner_label=(
                    f"{owner_label} contract "
                    f"{_dotted_decl_name(contract_unit.module_parts, schema_decl.name)}"
                ),
            )
            if not gates:
                raise CompileError(
                    f"Review contract must export at least one gate in {owner_label}: {schema_decl.name}"
                )
            return ReviewContractSpec(
                kind="schema",
                title=schema_body.title,
                gates=gates,
            )

        raise CompileError(
            f"Review contract must resolve to a workflow or schema declaration in {owner_label}: "
            f"{dotted_name}"
        )

    def _resolve_review_pre_outcome_branches(
        self,
        sections: list[model.ReviewSection],
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        gate_observation: ReviewGateObservation,
    ) -> tuple[ResolvedReviewGateBranch, ...]:
        pre_branches = (ReviewPreOutcomeBranch(),)
        for section in sections:
            section_branches = self._collect_review_pre_section_branches(
                section,
                unit=unit,
                contract_spec=contract_spec,
                section_titles=section_titles,
                owner_label=f"{owner_label}.{section.key}",
            )
            next_branches: list[ReviewPreOutcomeBranch] = []
            for branch in pre_branches:
                for section_branch in section_branches:
                    next_branches.append(
                        ReviewPreOutcomeBranch(
                            block_checks=(*branch.block_checks, *section_branch.block_checks),
                            reject_checks=(*branch.reject_checks, *section_branch.reject_checks),
                            accept_checks=(*branch.accept_checks, *section_branch.accept_checks),
                            assertion_gate_ids=(
                                *branch.assertion_gate_ids,
                                *((section.key,) if section_branch.has_assertions else ()),
                            ),
                        )
                    )
            pre_branches = tuple(next_branches)

        resolved: list[ResolvedReviewGateBranch] = []
        for branch in pre_branches:
            resolved.extend(
                self._resolve_review_gate_branch(
                    branch,
                    unit=unit,
                    contract_spec=contract_spec,
                    gate_observation=gate_observation,
                )
            )
        return tuple(resolved)

    def _resolve_review_gate_branch(
        self,
        branch: ReviewPreOutcomeBranch,
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        gate_observation: ReviewGateObservation,
    ) -> tuple[ResolvedReviewGateBranch, ...]:
        block_states = [tuple[str, ...]()]
        for check in branch.block_checks:
            next_states: list[tuple[str, ...]] = []
            for state in block_states:
                result = self._evaluate_review_gate_condition(
                    check.expr,
                    unit=unit,
                    contract_failed_gate_ids=(),
                )
                if result is not False:
                    next_states.append((*state, check.identity))
                if result is not True:
                    next_states.append(state)
            block_states = next_states

        resolved: list[ResolvedReviewGateBranch] = []
        for block_failed_gate_ids in block_states:
            if block_failed_gate_ids:
                resolved.append(
                    ResolvedReviewGateBranch(
                        verdict=_REVIEW_VERDICT_TEXT["changes_requested"],
                        failing_gate_ids=tuple(block_failed_gate_ids),
                        blocked_gate_id=block_failed_gate_ids[0],
                    )
                )
                continue

            reject_states = [tuple[str, ...]()]
            for check in branch.reject_checks:
                next_reject_states: list[tuple[str, ...]] = []
                for state in reject_states:
                    result = self._evaluate_review_gate_condition(
                        check.expr,
                        unit=unit,
                        contract_failed_gate_ids=(),
                    )
                    if result is not False:
                        next_reject_states.append((*state, check.identity))
                    if result is not True:
                        next_reject_states.append(state)
                reject_states = next_reject_states

            for reject_failed_gate_ids in reject_states:
                assertion_states = [tuple[str, ...]()]
                for assertion_gate_id in branch.assertion_gate_ids:
                    next_assertion_states: list[tuple[str, ...]] = []
                    for state in assertion_states:
                        next_assertion_states.append((*state, assertion_gate_id))
                        next_assertion_states.append(state)
                    assertion_states = next_assertion_states

                for assertion_failed_gate_ids in assertion_states:
                    contract_states = self._review_contract_failure_states(
                        contract_spec,
                        observation=self._review_gate_observation_with_accept_checks(
                            gate_observation,
                            accept_checks=branch.accept_checks,
                        ),
                    )

                    for contract_failed_gate_ids in contract_states:
                        earlier_failures = (
                            *reject_failed_gate_ids,
                            *assertion_failed_gate_ids,
                            *contract_failed_gate_ids,
                        )
                        if earlier_failures:
                            resolved.append(
                                ResolvedReviewGateBranch(
                                    verdict=_REVIEW_VERDICT_TEXT["changes_requested"],
                                    failing_gate_ids=tuple(earlier_failures),
                                )
                            )
                            continue

                        accept_states = [ResolvedReviewGateBranch(verdict=_REVIEW_VERDICT_TEXT["accept"])]
                        for check in branch.accept_checks:
                            next_accept_states: list[ResolvedReviewGateBranch] = []
                            for state in accept_states:
                                result = self._evaluate_review_gate_condition(
                                    check.expr,
                                    unit=unit,
                                    contract_failed_gate_ids=contract_failed_gate_ids,
                                )
                                if result is not False:
                                    next_accept_states.append(state)
                                if result is not True:
                                    next_accept_states.append(
                                        ResolvedReviewGateBranch(
                                            verdict=_REVIEW_VERDICT_TEXT["changes_requested"],
                                            failing_gate_ids=(check.identity,),
                                        )
                                    )
                            accept_states = next_accept_states
                        resolved.extend(accept_states)

        return tuple(resolved)

    def _resolve_review_gate_expr_constant(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
        contract_failed_gate_ids: tuple[str, ...],
    ) -> str | int | bool | tuple[str | int | bool, ...] | None:
        if isinstance(expr, (str, int, bool)):
            return expr
        if isinstance(expr, model.ExprSet):
            values: list[str | int | bool] = []
            for item in expr.items:
                value = self._resolve_review_gate_expr_constant(
                    item,
                    unit=unit,
                    branch=branch,
                    contract_failed_gate_ids=contract_failed_gate_ids,
                )
                if value is None or isinstance(value, tuple):
                    return None
                values.append(value)
            return tuple(values)
        if isinstance(expr, model.ExprCall):
            if expr.name in {"failed", "passed"} and len(expr.args) == 1:
                gate_identity = self._resolve_review_contract_gate_identity(expr.args[0])
                if gate_identity is None:
                    return None
                is_failed = gate_identity in contract_failed_gate_ids
                return is_failed if expr.name == "failed" else not is_failed
            if (
                expr.name in {"present", "missing"}
                and len(expr.args) == 1
                and isinstance(expr.args[0], model.ExprRef)
                and len(expr.args[0].parts) == 1
            ):
                field_name = expr.args[0].parts[0]
                is_present = any(carry.field_name == field_name for carry in branch.carries)
                return is_present if expr.name == "present" else not is_present
            return None
        if isinstance(expr, model.ExprRef):
            contract_value = self._resolve_review_contract_expr_constant(
                expr,
                contract_failed_gate_ids=contract_failed_gate_ids,
            )
            if contract_value is not None:
                return contract_value
            return self._resolve_review_expr_constant(expr, unit=unit, branch=branch)
        if isinstance(expr, model.ExprBinary):
            return self._evaluate_review_gate_condition_with_branch(
                expr,
                unit=unit,
                branch=branch,
                contract_failed_gate_ids=contract_failed_gate_ids,
            )
        return None

    def _resolve_review_contract_gate_identity(self, expr: model.Expr) -> str | None:
        if not isinstance(expr, model.ExprRef):
            return None
        if len(expr.parts) != 2 or expr.parts[0] != "contract":
            return None
        return f"contract.{expr.parts[1]}"

    def _resolve_review_contract_expr_constant(
        self,
        expr: model.ExprRef,
        *,
        contract_failed_gate_ids: tuple[str, ...],
    ) -> str | bool | tuple[str, ...] | None:
        if len(expr.parts) < 2 or expr.parts[0] != "contract":
            return None
        if expr.parts[1] == "passes" and len(expr.parts) == 2:
            return not contract_failed_gate_ids
        if expr.parts[1] == "failed_gates" and len(expr.parts) == 2:
            return contract_failed_gate_ids
        if expr.parts[1] == "first_failed_gate" and len(expr.parts) == 2:
            return contract_failed_gate_ids[0] if contract_failed_gate_ids else None
        return None

    def _resolve_review_match_option(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> tuple[model.EnumDecl, str] | None:
        if not isinstance(expr, model.ExprRef) or len(expr.parts) < 2:
            return None
        enum_ref = _name_ref_from_dotted_name(".".join(expr.parts[:-1]))
        enum_decl = self._try_resolve_enum_decl(enum_ref, unit=unit)
        if enum_decl is None:
            return None
        member = next((member for member in enum_decl.members if member.key == expr.parts[-1]), None)
        if member is None:
            return None
        return enum_decl, member.value

    def _resolve_review_agreement_branch(
        self,
        branch: ReviewOutcomeBranch,
        *,
        section_key: str,
        unit: IndexedUnit,
        owner_label: str,
        agent_contract: AgentContract,
        comment_output_decl: model.OutputDecl,
        comment_output_unit: IndexedUnit,
        field_bindings: dict[str, tuple[str, ...]],
        subject_keys: set[tuple[tuple[str, ...], str]],
        subject_map: model.ReviewSubjectMapConfig | None,
        blocked_gate_required: bool,
        gate_branch: ResolvedReviewGateBranch,
    ) -> ResolvedReviewAgreementBranch:
        route = branch.routes[0] if branch.routes else None
        if route is not None:
            self._validate_route_target(route.target, unit=unit)

        current = branch.currents[0]
        current_carrier_path: tuple[str, ...] | None = None
        current_subject_key: tuple[tuple[str, ...], str] | None = None
        if isinstance(current, model.ReviewCurrentArtifactStmt):
            synthetic_current = model.CurrentArtifactStmt(
                target=_law_path_from_name_ref(current.artifact_ref),
                carrier=model.LawPath(parts=current.carrier.parts),
            )
            current_subject_key = self._validate_current_artifact_stmt(
                synthetic_current,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
            )
            current_carrier_path = self._validate_carrier_path(
                synthetic_current.carrier,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
                statement_label="current artifact",
            ).remainder
            if (
                current_subject_key not in subject_keys
                and current_subject_key not in agent_contract.outputs
            ):
                raise CompileError(
                    "Review current artifact must stay rooted in a review subject or emitted "
                    f"output in {owner_label}: {_dotted_ref_name(current.artifact_ref)}"
                )

        carried_values: dict[str, model.ReviewCarryStmt] = {}
        for carry in branch.carries:
            if carry.field_name in carried_values:
                raise CompileError(
                    f"Duplicate carried review field in {owner_label}: {carry.field_name}"
                )
            carried_values[carry.field_name] = carry
            if carry.field_name not in field_bindings:
                raise CompileError(
                    f"Carried review field is missing a binding in {owner_label}: {carry.field_name}"
                )

        return ResolvedReviewAgreementBranch(
            section_key=section_key,
            verdict=gate_branch.verdict,
            route=route,
            current=current,
            current_carrier_path=current_carrier_path,
            current_subject_key=current_subject_key,
            reviewed_subject_key=self._resolve_reviewed_artifact_subject_key(
                current_subject_key=current_subject_key,
                subject_keys=subject_keys,
                subject_map=subject_map,
                branch=branch,
                review_unit=unit,
                output_decl=comment_output_decl,
                output_unit=comment_output_unit,
                field_path=field_bindings["reviewed_artifact"],
                owner_label=owner_label,
            ),
            carries=tuple(carried_values.values()),
            requires_failure_detail=bool(gate_branch.failing_gate_ids),
            blocked_gate_required=blocked_gate_required and section_key == "on_reject",
            failing_gate_ids=gate_branch.failing_gate_ids,
            blocked_gate_id=gate_branch.blocked_gate_id,
        )

    def _resolve_reviewed_artifact_subject_key(
        self,
        *,
        current_subject_key: tuple[tuple[str, ...], str] | None,
        subject_keys: set[tuple[tuple[str, ...], str]],
        subject_map: model.ReviewSubjectMapConfig | None,
        branch: ReviewOutcomeBranch,
        review_unit: IndexedUnit,
        output_decl: model.OutputDecl,
        output_unit: IndexedUnit,
        field_path: tuple[str, ...],
        owner_label: str,
    ) -> tuple[tuple[str, ...], str] | None:
        if current_subject_key in subject_keys:
            return current_subject_key
        if len(subject_keys) == 1:
            return next(iter(subject_keys))
        if subject_map is not None:
            mapped = self._review_subject_key_from_subject_map(
                branch,
                unit=review_unit,
                subject_keys=subject_keys,
                subject_map=subject_map,
                owner_label=owner_label,
            )
            if mapped is not None:
                return mapped

        field_node = self._resolve_output_field_node(
            output_decl,
            path=field_path,
            unit=output_unit,
            owner_label=owner_label,
            surface_label="reviewed_artifact binding",
        )
        referenced_subjects = self._record_item_subject_keys(
            field_node.target,
            subject_keys=subject_keys,
            unit=output_unit,
            owner_label=owner_label,
        )
        if len(referenced_subjects) == 1:
            return referenced_subjects[0]
        return None

    def _resolve_review_semantic_expr_constant(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ResolvedReviewAgreementBranch,
    ) -> str | int | bool | tuple[str | int | bool, ...] | None:
        if isinstance(expr, (str, int, bool)):
            return expr
        if isinstance(expr, model.ExprSet):
            values: list[str | int | bool] = []
            for item in expr.items:
                value = self._resolve_review_semantic_expr_constant(
                    item,
                    unit=unit,
                    branch=branch,
                )
                if value is None or isinstance(value, tuple):
                    return None
                values.append(value)
            return tuple(values)
        if isinstance(expr, model.ExprCall):
            if expr.name in {"present", "missing"} and len(expr.args) == 1 and isinstance(
                expr.args[0], model.ExprRef
            ):
                field_name = self._review_semantic_field_ref_name(expr.args[0])
                if field_name is not None:
                    present = self._review_semantic_field_present(
                        field_name,
                        unit=unit,
                        branch=branch,
                    )
                    if present is None:
                        return None
                    return present if expr.name == "present" else not present
            if expr.name in {"failed", "passed"} and len(expr.args) == 1:
                gate_identity = self._resolve_review_contract_gate_identity(expr.args[0])
                if gate_identity is None:
                    return None
                contract_failed_gate_ids = tuple(
                    gate_id
                    for gate_id in branch.failing_gate_ids
                    if gate_id.startswith("contract.")
                )
                is_failed = gate_identity in contract_failed_gate_ids
                return is_failed if expr.name == "failed" else not is_failed
            return None
        if isinstance(expr, model.ExprRef):
            contract_failed_gate_ids = tuple(
                gate_id
                for gate_id in branch.failing_gate_ids
                if gate_id.startswith("contract.")
            )
            contract_value = self._resolve_review_contract_expr_constant(
                expr,
                contract_failed_gate_ids=contract_failed_gate_ids,
            )
            if contract_value is not None:
                return contract_value
            field_name = self._review_semantic_field_ref_name(expr)
            if field_name is not None:
                return self._review_semantic_ref_value(
                    field_name,
                    unit=unit,
                    branch=branch,
                )
            return self._resolve_constant_enum_member(expr, unit=unit)
        if isinstance(expr, model.ExprBinary):
            return self._evaluate_review_semantic_guard(expr, unit=unit, branch=branch)
        return None

    def _resolve_review_expr_constant(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: ReviewOutcomeBranch,
    ) -> str | int | bool | tuple[str | int | bool, ...] | None:
        if isinstance(expr, (str, int, bool)):
            return expr
        if isinstance(expr, model.ExprRef):
            for carry in reversed(branch.carries):
                if len(expr.parts) == 1 and carry.field_name == expr.parts[0]:
                    return self._resolve_review_expr_constant(
                        carry.expr,
                        unit=unit,
                        branch=branch,
                    )
            return self._resolve_constant_enum_member(expr, unit=unit)
        if isinstance(expr, model.ExprSet):
            values: list[str | int | bool] = []
            for item in expr.items:
                value = self._resolve_review_expr_constant(item, unit=unit, branch=branch)
                if value is None or isinstance(value, tuple):
                    return None
                values.append(value)
            return tuple(values)
        if (
            isinstance(expr, model.ExprCall)
            and expr.name in {"present", "missing"}
            and len(expr.args) == 1
            and isinstance(expr.args[0], model.ExprRef)
            and len(expr.args[0].parts) == 1
        ):
            field_name = expr.args[0].parts[0]
            if field_name == "blocked_gate" and branch.blocked_gate_present is not None:
                is_present = branch.blocked_gate_present
            else:
                is_present = any(carry.field_name == field_name for carry in branch.carries)
            return is_present if expr.name == "present" else not is_present
        if isinstance(expr, model.ExprBinary):
            return self._evaluate_review_condition(expr, unit=unit, branch=branch)
        return None

    def _resolve_review_decl(
        self, review_decl: model.ReviewDecl, *, unit: IndexedUnit
    ) -> ResolvedReviewBody:
        review_key = (unit.module_parts, review_decl.name)
        cached = self._resolved_review_cache.get(review_key)
        if cached is not None:
            return cached

        if review_key in self._review_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._review_resolution_stack, review_key]
            )
            raise CompileError(f"Cyclic review inheritance: {cycle}")

        self._review_resolution_stack.append(review_key)
        try:
            parent_review: ResolvedReviewBody | None = None
            parent_label: str | None = None
            if review_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_decl_ref(
                    review_decl.parent_ref,
                    unit=unit,
                    registry_name="reviews_by_name",
                    missing_label="review declaration",
                )
                parent_review = self._resolve_review_decl(parent_decl, unit=parent_unit)
                parent_label = f"review {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"

            resolved = self._resolve_review_body(
                review_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, review_decl.name),
                parent_review=parent_review,
                parent_label=parent_label,
            )
            self._resolved_review_cache[review_key] = resolved
            return resolved
        finally:
            self._review_resolution_stack.pop()

    def _resolve_review_body(
        self,
        review_body: model.ReviewBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_review: ResolvedReviewBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedReviewBody:
        subject = parent_review.subject if parent_review is not None else None
        subject_map = parent_review.subject_map if parent_review is not None else None
        contract = parent_review.contract if parent_review is not None else None
        comment_output = parent_review.comment_output if parent_review is not None else None
        fields = parent_review.fields if parent_review is not None else None
        selector = parent_review.selector if parent_review is not None else None
        cases = parent_review.cases if parent_review is not None else ()

        if parent_review is None:
            fields_accounted = True
            parent_items_by_key: dict[str, model.ReviewSection | model.ReviewOutcomeSection] = {}
        else:
            fields_accounted = parent_review.fields is None
            parent_items_by_key = {item.key: item for item in parent_review.items}

        resolved_items: list[model.ReviewSection | model.ReviewOutcomeSection] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in review_body.items:
            if isinstance(item, model.ReviewSubjectConfig):
                subject = item
                continue
            if isinstance(item, model.ReviewSubjectMapConfig):
                subject_map = item
                continue
            if isinstance(item, model.ReviewContractConfig):
                contract = item
                continue
            if isinstance(item, model.ReviewCommentOutputConfig):
                comment_output = item
                continue
            if isinstance(item, model.ReviewFieldsConfig):
                if parent_review is not None and parent_review.fields is not None:
                    raise CompileError(
                        f"Inherited review fields require `inherit fields` or `override fields` in {owner_label}"
                    )
                fields = item
                fields_accounted = True
                continue
            if isinstance(item, model.ReviewSelectorConfig):
                if parent_review is not None and parent_review.selector is not None:
                    raise CompileError(
                        f"Inherited review selector cannot be redefined in {owner_label}"
                    )
                selector = item
                continue
            if isinstance(item, model.ReviewCasesConfig):
                if parent_review is not None and parent_review.cases:
                    raise CompileError(
                        f"Inherited review cases cannot be redefined in {owner_label}"
                    )
                cases = tuple(
                    model.ReviewCase(
                        key=case.key,
                        title=case.title,
                        head=case.head,
                        subject=case.subject,
                        contract=case.contract,
                        checks=self._resolve_review_pre_outcome_items(
                            case.checks,
                            unit=unit,
                            owner_label=f"{owner_label}.cases.{case.key}.checks",
                        ),
                        on_accept=model.ReviewOutcomeSection(
                            key="on_accept",
                            title=case.on_accept.title,
                            items=self._resolve_review_outcome_items(
                                case.on_accept.items,
                                unit=unit,
                                owner_label=f"{owner_label}.cases.{case.key}.on_accept",
                            ),
                        ),
                        on_reject=model.ReviewOutcomeSection(
                            key="on_reject",
                            title=case.on_reject.title,
                            items=self._resolve_review_outcome_items(
                                case.on_reject.items,
                                unit=unit,
                                owner_label=f"{owner_label}.cases.{case.key}.on_reject",
                            ),
                        ),
                    )
                    for case in item.cases
                )
                continue

            if isinstance(item, model.InheritItem) and item.key == "fields":
                if parent_review is None or parent_review.fields is None:
                    raise CompileError(
                        f"Cannot inherit undefined review entry in {parent_label or owner_label}: fields"
                    )
                fields = parent_review.fields
                fields_accounted = True
                continue

            if isinstance(item, model.ReviewOverrideFields):
                if parent_review is None or parent_review.fields is None:
                    raise CompileError(
                        f"`override` requires an inherited review in {owner_label}: fields"
                    )
                fields = model.ReviewFieldsConfig(bindings=item.bindings)
                fields_accounted = True
                continue

            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate review item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.ReviewSection):
                resolved_items.append(
                    model.ReviewSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_review_pre_outcome_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.ReviewOutcomeSection):
                resolved_items.append(
                    model.ReviewOutcomeSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_review_outcome_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined review entry in {parent_label or owner_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"`override` requires an inherited review in {owner_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.ReviewOverrideSection):
                if not isinstance(parent_item, model.ReviewSection):
                    raise CompileError(
                        f"Override kind mismatch for review entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    model.ReviewSection(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_review_pre_outcome_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, model.ReviewOutcomeSection):
                raise CompileError(
                    f"Override kind mismatch for review entry in {owner_label}: {key}"
                )
            resolved_items.append(
                model.ReviewOutcomeSection(
                    key=key,
                    title=item.title if item.title is not None else parent_item.title,
                    items=self._resolve_review_outcome_items(
                        item.items,
                        unit=unit,
                        owner_label=f"{owner_label}.{key}",
                    ),
                )
            )

        if parent_review is not None:
            missing_keys = [
                parent_item.key
                for parent_item in parent_review.items
                if parent_item.key not in accounted_keys
            ]
            if missing_keys:
                raise CompileError(
                    f"Missing inherited review entry in {owner_label}: {', '.join(missing_keys)}"
                )
            if parent_review.fields is not None and not fields_accounted:
                raise CompileError(
                    f"Missing inherited review entry in {owner_label}: fields"
                )

        return ResolvedReviewBody(
            title=review_body.title,
            subject=subject,
            subject_map=subject_map,
            contract=contract,
            comment_output=comment_output,
            fields=fields,
            selector=selector,
            cases=cases,
            items=tuple(resolved_items),
        )

    def _resolve_review_pre_outcome_items(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.ReviewPreOutcomeStmt, ...]:
        resolved: list[model.ReviewPreOutcomeStmt] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                resolved.append(item)
                continue
            if isinstance(item, model.ReviewPreOutcomeWhenStmt):
                resolved.append(
                    model.ReviewPreOutcomeWhenStmt(
                        expr=item.expr,
                        items=self._resolve_review_pre_outcome_items(
                            item.items,
                            unit=unit,
                            owner_label=owner_label,
                        ),
                    )
                )
                continue
            if isinstance(item, model.ReviewPreOutcomeMatchStmt):
                resolved.append(
                    model.ReviewPreOutcomeMatchStmt(
                        expr=item.expr,
                        cases=tuple(
                            model.ReviewPreOutcomeMatchArm(
                                head=case.head,
                                items=self._resolve_review_pre_outcome_items(
                                    case.items,
                                    unit=unit,
                                    owner_label=owner_label,
                                ),
                            )
                            for case in item.cases
                        ),
                    )
                )
                continue
            resolved.append(item)
        return tuple(resolved)

    def _resolve_review_outcome_items(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.ReviewOutcomeStmt, ...]:
        resolved: list[model.ReviewOutcomeStmt] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                resolved.append(item)
                continue
            if isinstance(item, model.ReviewOutcomeWhenStmt):
                resolved.append(
                    model.ReviewOutcomeWhenStmt(
                        expr=item.expr,
                        items=self._resolve_review_outcome_items(
                            item.items,
                            unit=unit,
                            owner_label=owner_label,
                        ),
                    )
                )
                continue
            if isinstance(item, model.ReviewOutcomeMatchStmt):
                resolved.append(
                    model.ReviewOutcomeMatchStmt(
                        expr=item.expr,
                        cases=tuple(
                            model.ReviewOutcomeMatchArm(
                                head=case.head,
                                items=self._resolve_review_outcome_items(
                                    case.items,
                                    unit=unit,
                                    owner_label=owner_label,
                                ),
                            )
                            for case in item.cases
                        ),
                    )
                )
                continue
            resolved.append(item)
        return tuple(resolved)
