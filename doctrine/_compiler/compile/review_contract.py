from __future__ import annotations

from dataclasses import dataclass

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.constants import _REVIEW_VERDICT_TEXT
from doctrine._compiler.final_output_diagnostics import final_output_compile_error
from doctrine._compiler.review_diagnostics import (
    collect_review_accept_stmts,
    find_review_decl_item,
    review_compile_error,
    review_related_site,
)
from doctrine._compiler.resolved_types import (
    AgentContract,
    CompileError,
    CompiledReviewFinalResponseSpec,
    CompiledReviewOutcomeSpec,
    CompiledReviewOutputSpec,
    CompiledReviewSpec,
    IndexedUnit,
    OutputDeclKey,
    ResolvedReviewAgreementBranch,
    ResolvedReviewBody,
    ReviewContractGate,
    ReviewContractSpec,
)
from doctrine._compiler.support_files import _dotted_decl_name


@dataclass(slots=True, frozen=True)
class _ResolvedCompiledReview:
    comment_output_unit: IndexedUnit
    comment_output_decl: model.OutputDecl
    carrier_field_bindings: dict[str, tuple[str, ...]]
    accept_branches: tuple[ResolvedReviewAgreementBranch, ...]
    reject_branches: tuple[ResolvedReviewAgreementBranch, ...]


class CompileReviewContractMixin:
    """Review metadata helpers for compiled agent contracts."""

    def _invalid_final_output_review_fields(
        self,
        *,
        agent_name: str,
        unit: IndexedUnit,
        source_span: model.SourceSpan | None,
        detail: str,
    ) -> None:
        raise compile_error(
            code="E500",
            summary="`final_output.review_fields` is used in an invalid place",
            detail=(
                f"Agent `{agent_name}` uses `final_output.review_fields` in an invalid "
                f"place. {detail}"
            ),
            path=unit.prompt_file.source_path,
            source_span=source_span,
            hints=(
                "Use `review_fields:` only on split final responses for review-driven agents.",
            ),
        )

    def _compile_agent_review_contract(
        self,
        *,
        agent: model.Agent,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        final_output_field: model.FinalOutputField | None,
    ) -> CompiledReviewSpec | None:
        review_fields = [field for field in agent.fields if isinstance(field, model.ReviewField)]
        authored_review_fields = (
            final_output_field.review_fields if final_output_field is not None else None
        )
        if not review_fields:
            if authored_review_fields is not None:
                self._invalid_final_output_review_fields(
                    agent_name=agent.name,
                    unit=unit,
                    source_span=final_output_field.source_span,
                    detail="review_fields require a review-driven agent",
                )
            return None

        review_field = review_fields[0]
        review_unit, review_decl = self._resolve_review_ref(review_field.value, unit=unit)
        if review_decl.abstract:
            raise review_compile_error(
                code="E494",
                summary="Concrete agent may not attach abstract review directly",
                detail=(
                    "Concrete agent may not attach abstract review "
                    f"`{_dotted_decl_name(review_unit.module_parts, review_decl.name)}` "
                    "directly."
                ),
                unit=unit,
                source_span=review_field.source_span,
                related=(
                    review_related_site(
                        label="abstract review declaration",
                        unit=review_unit,
                        source_span=review_decl.source_span,
                    ),
                ),
            )

        resolved_review = self._resolve_compiled_review(
            review_decl,
            unit=review_unit,
            agent_contract=agent_contract,
            owner_label=f"agent {agent.name} review",
        )
        comment_output_key = (
            resolved_review.comment_output_unit.module_parts,
            resolved_review.comment_output_decl.name,
        )
        all_branches = (
            *resolved_review.accept_branches,
            *resolved_review.reject_branches,
        )

        final_mode = "none"
        final_output_key: OutputDeclKey | None = None
        final_output_name: str | None = None
        final_response_fields: dict[str, tuple[str, ...]] = {}
        control_ready = False

        if final_output_field is not None:
            final_output_unit, final_output_decl = self._resolve_final_output_decl(
                final_output_field.value,
                unit=unit,
                owner_label=f"agent {agent.name} final_output",
                source_span=final_output_field.source_span,
            )
            final_output_key = (final_output_unit.module_parts, final_output_decl.name)
            final_output_name = final_output_decl.name
            if final_output_key not in agent_contract.outputs:
                raise final_output_compile_error(
                    code="E212",
                    summary="Final output is not emitted by the concrete turn",
                    detail=(
                        f"Agent `{agent.name}` declares `final_output` as "
                        f"`{_dotted_decl_name(final_output_unit.module_parts, final_output_decl.name)}`, "
                        "but that output is not emitted by the concrete turn."
                    ),
                    unit=unit,
                    source_span=final_output_field.source_span,
                    hints=(
                        "Add the output to the agent `outputs:` contract, or point `final_output:` at one that already is.",
                    ),
                )
            if final_output_key == comment_output_key:
                if authored_review_fields is not None:
                    self._invalid_final_output_review_fields(
                        agent_name=agent.name,
                        unit=unit,
                        source_span=final_output_field.source_span,
                        detail="review_fields may appear only on split final responses",
                    )
                final_mode = "carrier"
                control_ready = True
            else:
                final_mode = "split"
                if authored_review_fields is not None:
                    final_response_fields = self._validate_review_field_bindings(
                        authored_review_fields,
                        output_decl=final_output_decl,
                        output_unit=final_output_unit,
                        owner_label=f"agent {agent.name} final_output.review_fields",
                        require_core_fields=False,
                        require_blocked_gate=False,
                        require_active_mode=False,
                        require_trigger_reason=False,
                    )
                    final_response_field_spans = self._review_field_binding_source_spans(
                        authored_review_fields
                    )
                    self._validate_review_semantic_output_bindings(
                        all_branches,
                        review_unit=review_unit,
                        field_binding_unit=unit,
                        output_decl=final_output_decl,
                        output_unit=final_output_unit,
                        field_bindings=final_response_fields,
                        field_binding_spans=final_response_field_spans,
                        owner_label=f"agent {agent.name} final_output.review_fields",
                    )
                control_ready = self._review_final_response_is_control_ready(
                    all_branches,
                    review_unit=review_unit,
                    field_bindings=final_response_fields,
                )

        return CompiledReviewSpec(
            comment_output=CompiledReviewOutputSpec(
                output_key=comment_output_key,
                output_name=resolved_review.comment_output_decl.name,
            ),
            carrier_fields=tuple(resolved_review.carrier_field_bindings.items()),
            final_response=CompiledReviewFinalResponseSpec(
                mode=final_mode,
                output_key=final_output_key,
                output_name=final_output_name,
                review_fields=tuple(final_response_fields.items()),
                control_ready=control_ready,
            ),
            outcomes=(
                (
                    "accept",
                    CompiledReviewOutcomeSpec(
                        exists=bool(resolved_review.accept_branches),
                        verdict="accept",
                        route_behavior=self._review_route_behavior(
                            resolved_review.accept_branches,
                            review_unit=review_unit,
                        ),
                    ),
                ),
                (
                    "changes_requested",
                    CompiledReviewOutcomeSpec(
                        exists=bool(resolved_review.reject_branches),
                        verdict="changes_requested",
                        route_behavior=self._review_route_behavior(
                            resolved_review.reject_branches,
                            review_unit=review_unit,
                        ),
                    ),
                ),
                (
                    "blocked",
                    CompiledReviewOutcomeSpec(
                        exists=any(
                            branch.blocked_gate_id is not None
                            for branch in resolved_review.reject_branches
                        ),
                        verdict="changes_requested",
                        route_behavior=self._review_route_behavior(
                            tuple(
                                branch
                                for branch in resolved_review.reject_branches
                                if branch.blocked_gate_id is not None
                            ),
                            review_unit=review_unit,
                        ),
                    ),
                ),
            ),
        )

    def _resolve_compiled_review(
        self,
        review_decl: model.ReviewDecl,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> _ResolvedCompiledReview:
        resolved = self._resolve_review_decl(review_decl, unit=unit)
        if resolved.comment_output is None:
            raise review_compile_error(
                code="E478",
                summary="Review is missing comment_output",
                detail=f"Review `{review_decl.name}` is missing `comment_output:`.",
                unit=unit,
                source_span=review_decl.source_span,
                hints=("Add one `comment_output:` entry to the review.",),
            )
        if resolved.fields is None:
            raise review_compile_error(
                code="E473",
                summary="Review is missing fields",
                detail=f"Review `{review_decl.name}` is missing the required `fields:` block.",
                unit=unit,
                source_span=review_decl.source_span,
                hints=("Add a `fields:` block that binds the required review channels.",),
            )
        if resolved.cases:
            return self._resolve_case_selected_compiled_review(
                review_decl,
                resolved=resolved,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
            )
        return self._resolve_standard_compiled_review(
            review_decl,
            resolved=resolved,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
        )

    def _resolve_standard_compiled_review(
        self,
        review_decl: model.ReviewDecl,
        *,
        resolved: ResolvedReviewBody,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> _ResolvedCompiledReview:
        if resolved.subject is None:
            raise review_compile_error(
                code="E474",
                summary="Review is missing subject",
                detail=f"Review `{review_decl.name}` is missing `subject:`.",
                unit=unit,
                source_span=review_decl.source_span,
                hints=("Add one `subject:` entry that names the reviewed artifact.",),
            )
        if resolved.contract is None:
            raise review_compile_error(
                code="E476",
                summary="Review is missing contract",
                detail=f"Review `{review_decl.name}` is missing `contract:`.",
                unit=unit,
                source_span=review_decl.source_span,
                hints=("Add one `contract:` entry that names the shared review contract.",),
            )

        subjects = self._resolve_review_subjects(
            resolved.subject,
            unit=unit,
            owner_label=owner_label,
        )
        subject_keys = {
            (subject_unit.module_parts, subject_decl.name) for subject_unit, subject_decl in subjects
        }
        if resolved.subject_map is not None:
            self._resolved_review_subject_map(
                resolved.subject_map,
                unit=unit,
                owner_label=owner_label,
                subject_keys=subject_keys,
            )
        contract_spec = self._resolve_review_contract_spec(
            resolved.contract.contract_ref,
            unit=unit,
            owner_label=owner_label,
        )
        comment_output_unit, comment_output_decl = self._resolve_output_decl(
            resolved.comment_output.output_ref,
            unit=unit,
        )
        comment_output_key = (comment_output_unit.module_parts, comment_output_decl.name)
        if comment_output_key not in agent_contract.outputs:
            raise review_compile_error(
                code="E479",
                summary="Review comment_output is not emitted",
                detail=(
                    f"Review `{review_decl.name}` declares comment output "
                    f"`{comment_output_decl.name}`, but {owner_label} does not emit it."
                ),
                unit=unit,
                source_span=resolved.comment_output.source_span,
                hints=("Emit the declared review comment output from the concrete agent.",),
            )

        pre_sections: list[model.ReviewSection] = []
        on_accept: model.ReviewOutcomeSection | None = None
        on_reject: model.ReviewOutcomeSection | None = None
        for item in resolved.items:
            if isinstance(item, model.ReviewSection):
                pre_sections.append(item)
                continue
            if item.key == "on_accept":
                on_accept = item
            elif item.key == "on_reject":
                on_reject = item

        if on_accept is None:
            raise review_compile_error(
                code="E483",
                summary="Review is missing a reserved outcome section",
                detail=f"Review `{review_decl.name}` is missing `on_accept:`.",
                unit=unit,
                source_span=review_decl.source_span,
                hints=("Add one `on_accept:` outcome section to the review.",),
            )
        if on_reject is None:
            raise review_compile_error(
                code="E483",
                summary="Review is missing a reserved outcome section",
                detail=f"Review `{review_decl.name}` is missing `on_reject:`.",
                unit=unit,
                source_span=review_decl.source_span,
                hints=("Add one `on_reject:` outcome section to the review.",),
            )

        section_titles = {section.key: self._review_section_title(section) for section in pre_sections}
        gate_observation = self._review_gate_observation(comment_output_decl)
        accept_stmts: list[model.ReviewAcceptStmt] = []
        any_block_gates = False
        for section in pre_sections:
            accept_stmts.extend(collect_review_accept_stmts(section.items))
            any_block_gates = any_block_gates or self._review_items_contain_blocks(section.items)
            self._validate_review_pre_outcome_items(
                section.items,
                unit=unit,
                owner_label=f"{owner_label}.{section.key}",
                contract_spec=contract_spec,
                section_titles=section_titles,
                agent_contract=agent_contract,
            )
        if len(accept_stmts) != 1:
            if not accept_stmts:
                raise review_compile_error(
                    code="E481",
                    summary="Review is missing accept",
                    detail=f"Review `{review_decl.name}` must define exactly one `accept` gate.",
                    unit=unit,
                    source_span=review_decl.source_span,
                    hints=("Add one `accept ... when ...` gate inside the review checks.",),
                )
            raise review_compile_error(
                code="E482",
                summary="Review has multiple accept gates",
                detail=f"Review `{review_decl.name}` defines more than one `accept` gate.",
                unit=unit,
                source_span=accept_stmts[-1].source_span,
                related=(
                    review_related_site(
                        label="first `accept` gate",
                        unit=unit,
                        source_span=accept_stmts[0].source_span,
                    ),
                ),
                hints=("Keep exactly one `accept ... when ...` gate across the review checks.",),
            )
        pre_outcome_branches = self._resolve_review_pre_outcome_branches(
            pre_sections,
            unit=unit,
            contract_spec=contract_spec,
            section_titles=section_titles,
            owner_label=owner_label,
            gate_observation=gate_observation,
        )
        accept_gate_branches = tuple(
            branch for branch in pre_outcome_branches if branch.verdict == _REVIEW_VERDICT_TEXT["accept"]
        )
        reject_gate_branches = tuple(
            branch
            for branch in pre_outcome_branches
            if branch.verdict == _REVIEW_VERDICT_TEXT["changes_requested"]
        )

        carried_fields = {
            field_name
            for field_name in (
                *self._collect_review_carried_fields(on_accept.items),
                *self._collect_review_carried_fields(on_reject.items),
            )
        }
        field_bindings = self._validate_review_field_bindings(
            resolved.fields,
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            owner_label=owner_label,
            require_blocked_gate=any_block_gates,
            require_active_mode="active_mode" in carried_fields,
            require_trigger_reason="trigger_reason" in carried_fields,
        )
        field_binding_spans = self._review_field_binding_source_spans(resolved.fields)

        accept_branches = self._validate_review_outcome_section(
            on_accept,
            unit=unit,
            field_binding_unit=unit,
            owner_label=owner_label,
            agent_contract=agent_contract,
            comment_output_decl=comment_output_decl,
            comment_output_unit=comment_output_unit,
            next_owner_field_path=field_bindings["next_owner"],
            field_bindings=field_bindings,
            field_binding_spans=field_binding_spans,
            subject_keys=subject_keys,
            subject_map=resolved.subject_map,
            blocked_gate_required=any_block_gates,
            gate_branches=accept_gate_branches,
        )
        reject_branches = self._validate_review_outcome_section(
            on_reject,
            unit=unit,
            field_binding_unit=unit,
            owner_label=owner_label,
            agent_contract=agent_contract,
            comment_output_decl=comment_output_decl,
            comment_output_unit=comment_output_unit,
            next_owner_field_path=field_bindings["next_owner"],
            field_bindings=field_bindings,
            field_binding_spans=field_binding_spans,
            subject_keys=subject_keys,
            subject_map=resolved.subject_map,
            blocked_gate_required=any_block_gates,
            gate_branches=reject_gate_branches,
        )
        self._validate_review_current_artifact_alignment(
            (*accept_branches, *reject_branches),
            review_unit=unit,
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            owner_label=owner_label,
        )
        self._validate_review_optional_field_alignment(
            (*accept_branches, *reject_branches),
            field_binding_unit=unit,
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            field_bindings=field_bindings,
            field_binding_spans=field_binding_spans,
            owner_label=owner_label,
        )

        return _ResolvedCompiledReview(
            comment_output_unit=comment_output_unit,
            comment_output_decl=comment_output_decl,
            carrier_field_bindings=field_bindings,
            accept_branches=accept_branches,
            reject_branches=reject_branches,
        )

    def _resolve_case_selected_compiled_review(
        self,
        review_decl: model.ReviewDecl,
        *,
        resolved: ResolvedReviewBody,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> _ResolvedCompiledReview:
        if resolved.selector is None:
            raise review_compile_error(
                code="E470",
                summary="Invalid review declaration shape",
                detail=f"Case-selected review `{review_decl.name}` is missing `selector:`.",
                unit=unit,
                source_span=review_decl.source_span,
                hints=("Add one `selector:` block before the `cases:` block.",),
            )
        if (
            resolved.subject is not None
            or resolved.contract is not None
            or resolved.subject_map is not None
        ):
            misplaced_item = find_review_decl_item(
                review_decl,
                predicate=lambda item: isinstance(
                    item,
                    (
                        model.ReviewSubjectConfig,
                        model.ReviewSubjectMapConfig,
                        model.ReviewContractConfig,
                    ),
                ),
            )
            raise review_compile_error(
                code="E470",
                summary="Invalid review declaration shape",
                detail=(
                    f"Case-selected review `{review_decl.name}` must declare `subject:`, "
                    "`subject_map:`, and `contract:` inside each case."
                ),
                unit=unit,
                source_span=(
                    review_decl.source_span
                    if misplaced_item is None
                    else getattr(misplaced_item, "source_span", None)
                ),
                hints=("Move shared `subject:` and `contract:` entries into each case block.",),
            )

        comment_output_unit, comment_output_decl = self._resolve_output_decl(
            resolved.comment_output.output_ref,
            unit=unit,
        )
        comment_output_key = (comment_output_unit.module_parts, comment_output_decl.name)
        if comment_output_key not in agent_contract.outputs:
            raise review_compile_error(
                code="E479",
                summary="Review comment_output is not emitted",
                detail=(
                    f"Review `{review_decl.name}` declares comment output "
                    f"`{comment_output_decl.name}`, but {owner_label} does not emit it."
                ),
                unit=unit,
                source_span=resolved.comment_output.source_span,
                hints=("Emit the declared review comment output from the concrete agent.",),
            )

        pre_sections = [
            item for item in resolved.items if isinstance(item, model.ReviewSection)
        ]
        outcome_sections = [
            item for item in resolved.items if isinstance(item, model.ReviewOutcomeSection)
        ]
        if outcome_sections:
            misplaced_section = find_review_decl_item(
                review_decl,
                predicate=lambda item: isinstance(item, model.ReviewOutcomeSection),
            )
            raise review_compile_error(
                code="E470",
                summary="Invalid review declaration shape",
                detail=(
                    f"Case-selected review `{review_decl.name}` must keep `on_accept:` and "
                    "`on_reject:` inside each case."
                ),
                unit=unit,
                source_span=(
                    review_decl.source_span
                    if misplaced_section is None
                    else getattr(misplaced_section, "source_span", None)
                ),
                hints=("Move the outcome sections into each case block.",),
            )

        enum_decl = self._try_resolve_enum_decl(resolved.selector.enum_ref, unit=unit)
        if enum_decl is None:
            raise review_compile_error(
                code="E470",
                summary="Invalid review declaration shape",
                detail=(
                    f"Case-selected review `{review_decl.name}` selector must resolve to a "
                    "closed enum."
                ),
                unit=unit,
                source_span=resolved.selector.source_span,
                hints=("Point `selector:` at a closed enum member path.",),
            )

        seen_case_members: dict[str, model.ReviewCase] = {}
        expected_case_members = {member.value for member in enum_decl.members}
        for case in resolved.cases:
            if len(case.subject.subjects) != 1:
                raise review_compile_error(
                    code="E470",
                    summary="Invalid review declaration shape",
                    detail=(
                        f"Review case `{case.key}` in `{review_decl.name}` must declare "
                        "exactly one subject."
                    ),
                    unit=unit,
                    source_span=case.subject.source_span or case.source_span,
                    hints=("Keep one `subject:` entry in each review case.",),
                )
            for option in case.head.options:
                resolved_option = self._resolve_review_match_option(option, unit=unit)
                if resolved_option is None:
                    raise review_compile_error(
                        code="E470",
                        summary="Invalid review declaration shape",
                        detail=(
                            f"Review case `{case.key}` in `{review_decl.name}` must select "
                            f"a member of `{enum_decl.name}`."
                        ),
                        unit=unit,
                        source_span=option.source_span or case.head.source_span or case.source_span,
                        hints=("Use enum member refs from the selected enum in each `when` line.",),
                    )
                option_enum_decl, member_value = resolved_option
                if option_enum_decl.name != enum_decl.name:
                    raise review_compile_error(
                        code="E470",
                        summary="Invalid review declaration shape",
                        detail=(
                            f"Review case `{case.key}` in `{review_decl.name}` must select "
                            f"a member of `{enum_decl.name}`."
                        ),
                        unit=unit,
                        source_span=option.source_span or case.head.source_span or case.source_span,
                        hints=("Use enum member refs from the selected enum in each `when` line.",),
                    )
                previous_case = seen_case_members.get(member_value)
                if previous_case is not None:
                    raise review_compile_error(
                        code="E470",
                        summary="Invalid review declaration shape",
                        detail=(
                            f"Review `{review_decl.name}` has overlapping cases for selector "
                            f"value `{member_value}`."
                        ),
                        unit=unit,
                        source_span=case.head.source_span or case.source_span,
                        related=(
                            review_related_site(
                                label=f"first case for `{member_value}`",
                                unit=unit,
                                source_span=previous_case.head.source_span
                                or previous_case.source_span,
                            ),
                        ),
                        hints=("Keep each selector value in exactly one case.",),
                    )
                seen_case_members[member_value] = case
        if set(seen_case_members) != expected_case_members:
            cases_config = find_review_decl_item(
                review_decl,
                predicate=lambda item: isinstance(item, model.ReviewCasesConfig),
            )
            missing_members = ", ".join(sorted(expected_case_members - set(seen_case_members)))
            raise review_compile_error(
                code="E470",
                summary="Invalid review declaration shape",
                detail=(
                    f"Review `{review_decl.name}` is missing cases for selector values: "
                    f"{missing_members}."
                ),
                unit=unit,
                source_span=(
                    getattr(cases_config, "source_span", None)
                    or resolved.selector.source_span
                    or review_decl.source_span
                ),
                hints=("Keep the case-selected review exhaustive, or cover every enum member.",),
            )

        gate_observation = self._review_gate_observation(comment_output_decl)
        all_contract_gates: list[ReviewContractGate] = []
        seen_contract_gate_keys: set[str] = set()
        all_accept_branches: list[ResolvedReviewAgreementBranch] = []
        all_reject_branches: list[ResolvedReviewAgreementBranch] = []

        carried_fields = {
            field_name
            for case in resolved.cases
            for field_name in (
                *self._collect_review_carried_fields(case.on_accept.items),
                *self._collect_review_carried_fields(case.on_reject.items),
            )
        }
        field_bindings = self._validate_review_field_bindings(
            resolved.fields,
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            owner_label=owner_label,
            require_blocked_gate=any(
                self._review_items_contain_blocks(section.items) for section in pre_sections
            )
            or any(self._review_items_contain_blocks(case.checks) for case in resolved.cases),
            require_active_mode=(
                resolved.selector.field_name == "active_mode" or "active_mode" in carried_fields
            ),
            require_trigger_reason="trigger_reason" in carried_fields,
        )
        field_binding_spans = self._review_field_binding_source_spans(resolved.fields)

        for case in resolved.cases:
            contract_spec = self._resolve_review_contract_spec(
                case.contract.contract_ref,
                unit=unit,
                owner_label=f"{owner_label}.cases.{case.key}",
            )
            for gate in contract_spec.gates:
                if gate.key in seen_contract_gate_keys:
                    continue
                seen_contract_gate_keys.add(gate.key)
                all_contract_gates.append(gate)

        shared_titles = {
            section.key: self._review_section_title(section) for section in pre_sections
        }
        shared_contract_spec = ReviewContractSpec(
            kind="review",
            title="Selected Review Contract",
            gates=tuple(all_contract_gates),
        )

        for section in pre_sections:
            self._validate_review_pre_outcome_items(
                section.items,
                unit=unit,
                owner_label=f"{owner_label}.{section.key}",
                contract_spec=shared_contract_spec,
                section_titles=shared_titles,
                agent_contract=agent_contract,
            )

        for case in resolved.cases:
            subjects = self._resolve_review_subjects(
                case.subject,
                unit=unit,
                owner_label=f"{owner_label}.cases.{case.key}",
            )
            subject_keys = {
                (subject_unit.module_parts, subject_decl.name)
                for subject_unit, subject_decl in subjects
            }
            contract_spec = self._resolve_review_contract_spec(
                case.contract.contract_ref,
                unit=unit,
                owner_label=f"{owner_label}.cases.{case.key}",
            )
            case_checks = model.ReviewSection(
                key=f"{case.key}_checks",
                title="Checks",
                items=case.checks,
            )
            case_pre_sections = [*pre_sections, case_checks]
            case_titles = {
                **shared_titles,
                case_checks.key: self._review_section_title(case_checks),
            }
            accept_stmts: list[model.ReviewAcceptStmt] = []
            any_block_gates = False
            for section in case_pre_sections:
                accept_stmts.extend(collect_review_accept_stmts(section.items))
                any_block_gates = any_block_gates or self._review_items_contain_blocks(section.items)
                self._validate_review_pre_outcome_items(
                    section.items,
                    unit=unit,
                    owner_label=f"{owner_label}.cases.{case.key}.{section.key}",
                    contract_spec=contract_spec,
                    section_titles=case_titles,
                    agent_contract=agent_contract,
                )
            if len(accept_stmts) != 1:
                if not accept_stmts:
                    raise review_compile_error(
                        code="E470",
                        summary="Invalid review declaration shape",
                        detail=(
                            f"Review case `{case.key}` in `{review_decl.name}` must define "
                            "exactly one `accept` gate."
                        ),
                        unit=unit,
                        source_span=case.source_span or case.head.source_span,
                        hints=("Add one `accept ... when ...` gate inside the case checks.",),
                    )
                raise review_compile_error(
                    code="E470",
                    summary="Invalid review declaration shape",
                    detail=(
                        f"Review case `{case.key}` in `{review_decl.name}` defines more than "
                        "one `accept` gate."
                    ),
                    unit=unit,
                    source_span=accept_stmts[-1].source_span,
                    related=(
                        review_related_site(
                            label="first `accept` gate",
                            unit=unit,
                            source_span=accept_stmts[0].source_span,
                        ),
                    ),
                    hints=("Keep exactly one `accept ... when ...` gate in each review case.",),
                )

            pre_outcome_branches = self._resolve_review_pre_outcome_branches(
                case_pre_sections,
                unit=unit,
                contract_spec=contract_spec,
                section_titles=case_titles,
                owner_label=f"{owner_label}.cases.{case.key}",
                gate_observation=gate_observation,
            )
            accept_gate_branches = tuple(
                branch
                for branch in pre_outcome_branches
                if branch.verdict == _REVIEW_VERDICT_TEXT["accept"]
            )
            reject_gate_branches = tuple(
                branch
                for branch in pre_outcome_branches
                if branch.verdict == _REVIEW_VERDICT_TEXT["changes_requested"]
            )
            accept_branches = self._validate_review_outcome_section(
                case.on_accept,
                unit=unit,
                field_binding_unit=unit,
                owner_label=f"{owner_label}.cases.{case.key}",
                agent_contract=agent_contract,
                comment_output_decl=comment_output_decl,
                comment_output_unit=comment_output_unit,
                next_owner_field_path=field_bindings["next_owner"],
                field_bindings=field_bindings,
                field_binding_spans=field_binding_spans,
                subject_keys=subject_keys,
                subject_map=None,
                blocked_gate_required=any_block_gates,
                gate_branches=accept_gate_branches,
            )
            reject_branches = self._validate_review_outcome_section(
                case.on_reject,
                unit=unit,
                field_binding_unit=unit,
                owner_label=f"{owner_label}.cases.{case.key}",
                agent_contract=agent_contract,
                comment_output_decl=comment_output_decl,
                comment_output_unit=comment_output_unit,
                next_owner_field_path=field_bindings["next_owner"],
                field_bindings=field_bindings,
                field_binding_spans=field_binding_spans,
                subject_keys=subject_keys,
                subject_map=None,
                blocked_gate_required=any_block_gates,
                gate_branches=reject_gate_branches,
            )
            all_accept_branches.extend(accept_branches)
            all_reject_branches.extend(reject_branches)

        self._validate_review_current_artifact_alignment(
            (*all_accept_branches, *all_reject_branches),
            review_unit=unit,
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            owner_label=owner_label,
        )
        self._validate_review_optional_field_alignment(
            (*all_accept_branches, *all_reject_branches),
            field_binding_unit=unit,
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            field_bindings=field_bindings,
            field_binding_spans=field_binding_spans,
            owner_label=owner_label,
        )

        return _ResolvedCompiledReview(
            comment_output_unit=comment_output_unit,
            comment_output_decl=comment_output_decl,
            carrier_field_bindings=field_bindings,
            accept_branches=tuple(all_accept_branches),
            reject_branches=tuple(all_reject_branches),
        )

    def _review_final_response_is_control_ready(
        self,
        branches: tuple[ResolvedReviewAgreementBranch, ...],
        *,
        review_unit: IndexedUnit,
        field_bindings: dict[str, tuple[str, ...]],
    ) -> bool:
        if "verdict" not in field_bindings:
            return False
        if (
            any(self._resolved_review_route(branch, unit=review_unit) is not None for branch in branches)
            and "next_owner" not in field_bindings
        ):
            return False
        if (
            any(branch.blocked_gate_id is not None for branch in branches)
            and "blocked_gate" not in field_bindings
        ):
            return False
        return True

    def _review_route_behavior(
        self,
        branches: tuple[ResolvedReviewAgreementBranch, ...],
        *,
        review_unit: IndexedUnit,
    ) -> str:
        if not branches:
            return "never"
        routed = sum(
            1
            for branch in branches
            if self._resolved_review_route(branch, unit=review_unit) is not None
        )
        if routed == len(branches):
            return "always"
        if routed == 0:
            return "never"
        return "conditional"
