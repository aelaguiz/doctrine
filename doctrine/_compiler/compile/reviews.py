from __future__ import annotations

from doctrine._compiler.constants import _REVIEW_VERDICT_TEXT
from doctrine._compiler.resolved_types import *  # noqa: F401,F403


class CompileReviewsMixin:
    """Review compile helpers for CompilationContext."""

    def _compile_review_decl(
        self,
        review_decl: model.ReviewDecl,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> CompiledSection:
        resolved = self._resolve_review_decl(review_decl, unit=unit)
        if resolved.comment_output is None:
            raise CompileError(f"Review is missing comment_output: {review_decl.name}")
        if resolved.fields is None:
            raise CompileError(f"Review is missing fields: {review_decl.name}")
        if resolved.cases:
            return self._compile_case_selected_review_decl(
                review_decl,
                resolved=resolved,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
            )
        if resolved.subject is None:
            raise CompileError(f"Review is missing subject: {review_decl.name}")
        if resolved.contract is None:
            raise CompileError(f"Review is missing contract: {review_decl.name}")

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
            raise CompileError(
                f"Review comment_output must be emitted by the concrete turn in {owner_label}: "
                f"{comment_output_decl.name}"
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
            raise CompileError(f"Review is missing on_accept: {review_decl.name}")
        if on_reject is None:
            raise CompileError(f"Review is missing on_reject: {review_decl.name}")

        section_titles = {section.key: self._review_section_title(section) for section in pre_sections}
        gate_observation = self._review_gate_observation(comment_output_decl)
        accept_gate_count = 0
        any_block_gates = False
        for section in pre_sections:
            accept_gate_count += self._count_review_accept_stmts(section.items)
            any_block_gates = any_block_gates or self._review_items_contain_blocks(section.items)
            self._validate_review_pre_outcome_items(
                section.items,
                unit=unit,
                owner_label=f"{owner_label}.{section.key}",
                contract_spec=contract_spec,
                section_titles=section_titles,
                agent_contract=agent_contract,
            )
        if accept_gate_count != 1:
            raise CompileError(
                f"Review must define exactly one accept gate in {owner_label}: found {accept_gate_count}"
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
        review_semantics = ReviewSemanticContext(
            review_module_parts=unit.module_parts,
            output_module_parts=comment_output_unit.module_parts,
            output_name=comment_output_decl.name,
            field_bindings=tuple(field_bindings.items()),
            contract_gates=contract_spec.gates,
        )

        accept_branches = self._validate_review_outcome_section(
            on_accept,
            unit=unit,
            owner_label=owner_label,
            agent_contract=agent_contract,
            comment_output_decl=comment_output_decl,
            comment_output_unit=comment_output_unit,
            next_owner_field_path=field_bindings["next_owner"],
            field_bindings=field_bindings,
            subject_keys=subject_keys,
            subject_map=resolved.subject_map,
            blocked_gate_required=any_block_gates,
            gate_branches=accept_gate_branches,
        )
        reject_branches = self._validate_review_outcome_section(
            on_reject,
            unit=unit,
            owner_label=owner_label,
            agent_contract=agent_contract,
            comment_output_decl=comment_output_decl,
            comment_output_unit=comment_output_unit,
            next_owner_field_path=field_bindings["next_owner"],
            field_bindings=field_bindings,
            subject_keys=subject_keys,
            subject_map=resolved.subject_map,
            blocked_gate_required=any_block_gates,
            gate_branches=reject_gate_branches,
        )
        self._validate_review_current_artifact_alignment(
            (*accept_branches, *reject_branches),
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            owner_label=owner_label,
        )
        self._validate_review_optional_field_alignment(
            (*accept_branches, *reject_branches),
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            field_bindings=field_bindings,
            owner_label=owner_label,
        )

        body: list[CompiledBodyItem] = [
            self._render_review_subject_summary(subjects),
            f"Shared review contract: {contract_spec.title}.",
        ]
        for section in pre_sections:
            if body and body[-1] != "":
                body.append("")
            body.append(
                CompiledSection(
                    title=self._review_section_title(section),
                    body=self._compile_review_pre_outcome_section_body(
                        section.items,
                        unit=unit,
                        contract_spec=contract_spec,
                        section_titles=section_titles,
                        owner_label=f"{owner_label}.{section.key}",
                        review_semantics=review_semantics,
                    ),
                    semantic_target=(
                        "review.contract_checks" if section.key == "contract_checks" else None
                    ),
                )
            )

        for key, section in (("on_accept", on_accept), ("on_reject", on_reject)):
            if body and body[-1] != "":
                body.append("")
            body.append(
                CompiledSection(
                    title=section.title or ("If Accepted" if key == "on_accept" else "If Rejected"),
                    body=self._compile_review_outcome_section_body(
                        section.items,
                        unit=unit,
                        owner_label=f"{owner_label}.{key}",
                        review_semantics=review_semantics,
                    ),
                )
            )

        return CompiledSection(title=resolved.title, body=tuple(body))

    def _compile_review_pre_outcome_section_body(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> tuple[CompiledBodyItem, ...]:
        lines: list[CompiledBodyItem] = []
        for item in items:
            rendered = self._render_review_pre_outcome_item(
                item,
                unit=unit,
                contract_spec=contract_spec,
                section_titles=section_titles,
                owner_label=owner_label,
                review_semantics=review_semantics,
            )
            if not rendered:
                continue
            if lines and lines[-1] != "":
                lines.append("")
            lines.extend(rendered)
        return tuple(lines)

    def _compile_review_outcome_section_body(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> tuple[CompiledBodyItem, ...]:
        lines: list[CompiledBodyItem] = []
        for item in items:
            rendered = self._render_review_outcome_item(
                item,
                unit=unit,
                owner_label=owner_label,
                review_semantics=review_semantics,
            )
            if not rendered:
                continue
            if lines and lines[-1] != "":
                lines.append("")
            lines.extend(rendered)
        return tuple(lines)
