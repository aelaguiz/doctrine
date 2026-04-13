from __future__ import annotations

from doctrine._compiler.constants import _REVIEW_VERDICT_TEXT
from doctrine._compiler.naming import _dotted_ref_name
from doctrine._compiler.resolved_types import *  # noqa: F401,F403


class CompileReviewCasesMixin:
    """Case-selected review compile helpers for CompilationContext."""

    def _compile_case_selected_review_decl(
        self,
        review_decl: model.ReviewDecl,
        *,
        resolved: ResolvedReviewBody,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> CompiledSection:
        if resolved.selector is None:
            raise CompileError(
                f"Case-selected review is missing selector: {review_decl.name}"
            )
        if resolved.subject is not None or resolved.contract is not None or resolved.subject_map is not None:
            raise CompileError(
                f"Case-selected review must declare subject and contract inside cases: {review_decl.name}"
            )

        comment_output_unit, comment_output_decl = self._resolve_output_decl(
            resolved.comment_output.output_ref,
            unit=unit,
        )
        comment_output_key = (comment_output_unit.module_parts, comment_output_decl.name)
        if comment_output_key not in agent_contract.outputs:
            raise CompileError(
                f"Review comment_output must be emitted by the concrete turn in {owner_label}: "
                f"{comment_output_decl.name}"
            )

        pre_sections = [
            item for item in resolved.items if isinstance(item, model.ReviewSection)
        ]
        outcome_sections = [
            item for item in resolved.items if isinstance(item, model.ReviewOutcomeSection)
        ]
        if outcome_sections:
            raise CompileError(
                f"Case-selected review must keep on_accept and on_reject inside cases: {review_decl.name}"
            )

        enum_decl = self._try_resolve_enum_decl(resolved.selector.enum_ref, unit=unit)
        if enum_decl is None:
            raise CompileError(
                f"Review selector must resolve to a closed enum in {owner_label}: "
                f"{_dotted_ref_name(resolved.selector.enum_ref)}"
            )

        seen_case_members: dict[str, str] = {}
        expected_case_members = {member.value for member in enum_decl.members}
        for case in resolved.cases:
            if len(case.subject.subjects) != 1:
                raise CompileError(
                    f"Review case must declare exactly one subject in {owner_label}: {case.key}"
                )
            for option in case.head.options:
                resolved_option = self._resolve_review_match_option(option, unit=unit)
                if resolved_option is None:
                    raise CompileError(
                        f"Review case selector must resolve to {enum_decl.name} in {owner_label}: {case.key}"
                    )
                option_enum_decl, member_value = resolved_option
                if option_enum_decl.name != enum_decl.name:
                    raise CompileError(
                        f"Review case selector must resolve to {enum_decl.name} in {owner_label}: {case.key}"
                    )
                previous_case = seen_case_members.get(member_value)
                if previous_case is not None:
                    raise CompileError(
                        f"Review cases overlap in {owner_label}: {previous_case}, {case.key}"
                    )
                seen_case_members[member_value] = case.key
        if set(seen_case_members) != expected_case_members:
            raise CompileError(f"Review cases must be exhaustive in {owner_label}")

        shared_titles = {
            section.key: self._review_section_title(section) for section in pre_sections
        }
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

        body: list[CompiledBodyItem] = [
            f"Selected review mode: {enum_decl.title}.",
        ]

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

        review_semantics = ReviewSemanticContext(
            review_module_parts=unit.module_parts,
            output_module_parts=comment_output_unit.module_parts,
            output_name=comment_output_decl.name,
            field_bindings=tuple(field_bindings.items()),
            contract_gates=tuple(all_contract_gates),
        )

        shared_contract_spec = ReviewContractSpec(
            kind="review",
            title="Selected Review Contract",
            gates=tuple(all_contract_gates),
        )

        for section in pre_sections:
            if body and body[-1] != "":
                body.append("")
            body.append(
                CompiledSection(
                    title=self._review_section_title(section),
                    body=self._compile_review_pre_outcome_section_body(
                        section.items,
                        unit=unit,
                        contract_spec=shared_contract_spec,
                        section_titles=shared_titles,
                        owner_label=f"{owner_label}.{section.key}",
                        review_semantics=review_semantics,
                    ),
                )
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
            accept_gate_count = 0
            any_block_gates = False
            for section in case_pre_sections:
                accept_gate_count += self._count_review_accept_stmts(section.items)
                any_block_gates = any_block_gates or self._review_items_contain_blocks(section.items)
                self._validate_review_pre_outcome_items(
                    section.items,
                    unit=unit,
                    owner_label=f"{owner_label}.cases.{case.key}.{section.key}",
                    contract_spec=contract_spec,
                    section_titles=case_titles,
                    agent_contract=agent_contract,
                )
            if accept_gate_count != 1:
                raise CompileError(
                    f"Review case must define exactly one accept gate in {owner_label}: {case.key}"
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
                owner_label=f"{owner_label}.cases.{case.key}",
                agent_contract=agent_contract,
                comment_output_decl=comment_output_decl,
                comment_output_unit=comment_output_unit,
                next_owner_field_path=field_bindings["next_owner"],
                field_bindings=field_bindings,
                subject_keys=subject_keys,
                subject_map=None,
                blocked_gate_required=any_block_gates,
                gate_branches=accept_gate_branches,
            )
            reject_branches = self._validate_review_outcome_section(
                case.on_reject,
                unit=unit,
                owner_label=f"{owner_label}.cases.{case.key}",
                agent_contract=agent_contract,
                comment_output_decl=comment_output_decl,
                comment_output_unit=comment_output_unit,
                next_owner_field_path=field_bindings["next_owner"],
                field_bindings=field_bindings,
                subject_keys=subject_keys,
                subject_map=None,
                blocked_gate_required=any_block_gates,
                gate_branches=reject_gate_branches,
            )
            all_accept_branches.extend(accept_branches)
            all_reject_branches.extend(reject_branches)

            case_body: list[CompiledBodyItem] = [
                self._render_review_subject_summary(subjects),
                f"Shared review contract: {contract_spec.title}.",
            ]
            if case_body and case_body[-1] != "":
                case_body.append("")
            case_body.append(
                CompiledSection(
                    title=self._review_section_title(case_checks),
                    body=self._compile_review_pre_outcome_section_body(
                        case.checks,
                        unit=unit,
                        contract_spec=contract_spec,
                        section_titles=case_titles,
                        owner_label=f"{owner_label}.cases.{case.key}.checks",
                        review_semantics=review_semantics,
                    ),
                )
            )
            for key, section in (("on_accept", case.on_accept), ("on_reject", case.on_reject)):
                if case_body and case_body[-1] != "":
                    case_body.append("")
                case_body.append(
                    CompiledSection(
                        title=section.title or ("If Accepted" if key == "on_accept" else "If Rejected"),
                        body=self._compile_review_outcome_section_body(
                            section.items,
                            unit=unit,
                            owner_label=f"{owner_label}.cases.{case.key}.{key}",
                            review_semantics=review_semantics,
                        ),
                    )
                )
            if body and body[-1] != "":
                body.append("")
            body.append(CompiledSection(title=case.title, body=tuple(case_body)))

        self._validate_review_current_artifact_alignment(
            (*all_accept_branches, *all_reject_branches),
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            owner_label=owner_label,
        )
        self._validate_review_optional_field_alignment(
            (*all_accept_branches, *all_reject_branches),
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            field_bindings=field_bindings,
            owner_label=owner_label,
        )
        return CompiledSection(title=resolved.title, body=tuple(body))
