from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path, PurePosixPath

from doctrine._compiler.constants import (
    _ADDRESSABLE_ROOT_REGISTRIES,
    _BUILTIN_INPUT_SOURCES,
    _BUILTIN_OUTPUT_TARGETS,
    _BUILTIN_RENDER_PROFILE_NAMES,
    _INTERPOLATION_EXPR_RE,
    _INTERPOLATION_RE,
    _READABLE_DECL_REGISTRIES,
    _RESERVED_AGENT_FIELD_KEYS,
    _REVIEW_CONTRACT_FACT_KEYS,
    _REVIEW_GUARD_FIELD_NAMES,
    _REVIEW_OPTIONAL_FIELD_NAMES,
    _REVIEW_REQUIRED_FIELD_NAMES,
    _REVIEW_VERDICT_TEXT,
    _SCHEMA_FAMILY_TITLES,
    _resolve_render_profile_mode,
    _semantic_render_target_for_block,
)
from doctrine._compiler.compile.agent import CompileAgentMixin
from doctrine._compiler.compile.final_output import CompileFinalOutputMixin
from doctrine._compiler.compile.readables import CompileReadablesMixin
from doctrine._compiler.compile.skill_package import CompileSkillPackageMixin
from doctrine._compiler.naming import (
    _agent_typed_field_key,
    _authored_slot_allows_law,
    _display_addressable_ref,
    _dotted_ref_name,
    _humanize_key,
    _law_path_from_name_ref,
    _lowercase_initial,
    _name_ref_from_dotted_name,
)
from doctrine._compiler.resolved_types import *  # noqa: F401,F403
from doctrine._compiler.support_files import _default_worker_count, _dotted_decl_name
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown, render_readable_block


class CompileMixin(
    CompileAgentMixin,
    CompileReadablesMixin,
    CompileFinalOutputMixin,
    CompileSkillPackageMixin,
):
    """Compile helper owner for CompilationContext."""

    def _compile_input_decl(self, decl: model.InputDecl, *, unit: IndexedUnit) -> CompiledSection:
        scalar_items, _section_items, extras = self._split_record_items(
            decl.items,
            scalar_keys={"source", "shape", "requirement"},
            owner_label=f"input {decl.name}",
        )
        source_item = scalar_items.get("source")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        if source_item is None:
            raise CompileError(f"Input is missing typed source: {decl.name}")
        if not isinstance(source_item.value, model.NameRef):
            raise CompileError(f"Input source must stay typed: {decl.name}")
        if shape_item is None:
            raise CompileError(f"Input is missing shape: {decl.name}")
        if requirement_item is None:
            raise CompileError(f"Input is missing requirement: {decl.name}")

        source_spec = self._resolve_input_source_spec(source_item.value, unit=unit)
        body: list[CompiledBodyItem] = [f"- Source: {source_spec.title}"]
        body.extend(
            self._compile_config_lines(
                source_item.body or (),
                spec=source_spec,
                unit=unit,
                owner_label=f"input {decl.name} source",
            )
        )
        body.append(
            f"- Shape: {self._display_symbol_value(shape_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
        )
        body.append(
            f"- Requirement: {self._display_symbol_value(requirement_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
        )
        if decl.structure_ref is not None:
            document_unit, document_decl = self._resolve_document_ref(decl.structure_ref, unit=unit)
            if not self._is_markdown_shape_value(shape_item.value, unit=unit):
                raise CompileError(
                    f"Input structure requires a markdown-bearing shape in input {decl.name}"
                )
            body.append(f"- Structure: {document_decl.title}")
            body.append("")
            body.append(
                CompiledSection(
                    title=f"Structure: {document_decl.title}",
                    body=self._compile_document_body(
                        self._resolve_document_decl(document_decl, unit=document_unit),
                        unit=document_unit,
                    ),
                )
            )

        if extras:
            body.append("")
            body.extend(
                self._compile_record_support_items(
                    extras,
                    unit=unit,
                    owner_label=f"input {decl.name}",
                    surface_label="input prose",
                )
            )

        return CompiledSection(title=decl.title, body=tuple(body))

    def _compile_output_decl(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> CompiledSection:
        self._validate_output_guard_sections(
            decl,
            unit=unit,
            allow_review_semantics=allow_review_semantics,
            allow_route_semantics=allow_route_semantics,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
        )
        scalar_items, section_items, extras = self._split_record_items(
            decl.items,
            scalar_keys={"target", "shape", "requirement"},
            section_keys={"files"},
            owner_label=f"output {decl.name}",
        )

        target_item = scalar_items.get("target")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        files_section = section_items.get("files")

        if files_section is not None and (target_item is not None or shape_item is not None):
            raise CompileError(
                f"Output mixes `files` with `target` or `shape`: {decl.name}"
            )
        if files_section is None and (target_item is None or shape_item is None):
            raise CompileError(
                f"Output must define either `files` or both `target` and `shape`: {decl.name}"
            )

        explicit_render_profile, render_profile = self._resolve_output_render_profiles(
            decl,
            unit=unit,
            files_section=files_section,
            shape_item=shape_item,
        )

        body: list[CompiledBodyItem] = []
        if files_section is not None:
            body.extend(
                self._compile_output_files(
                    files_section,
                    unit=unit,
                    output_name=decl.name,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            )
        else:
            if not isinstance(target_item.value, model.NameRef):
                raise CompileError(f"Output target must stay typed: {decl.name}")
            target_spec = self._resolve_output_target_spec(target_item.value, unit=unit)
            body.append(f"- Target: {target_spec.title}")
            body.extend(
                self._compile_config_lines(
                    target_item.body or (),
                    spec=target_spec,
                    unit=unit,
                    owner_label=f"output {decl.name} target",
                )
            )
            body.append(
                f"- Shape: {self._display_output_shape(shape_item.value, unit=unit, owner_label=decl.name, surface_label='output fields')}"
            )

        if requirement_item is not None:
            body.append(
                f"- Requirement: {self._display_symbol_value(requirement_item.value, unit=unit, owner_label=f'output {decl.name}', surface_label='output fields')}"
            )
        if decl.schema_ref is not None:
            schema_unit, schema_decl = self._resolve_schema_ref(decl.schema_ref, unit=unit)
            resolved_schema = self._resolve_schema_decl(schema_decl, unit=schema_unit)
            if not resolved_schema.sections:
                raise CompileError(
                    f"Output-attached schema must export at least one section in output {decl.name}: {schema_decl.name}"
                )
            body.append(f"- Schema: {schema_decl.title}")
            body.append("")
            body.append(self._compile_schema_sections_block(resolved_schema))
        if decl.structure_ref is not None:
            if files_section is not None:
                raise CompileError(
                    f"Output structure requires one markdown-bearing output artifact in {decl.name}"
                )
            if shape_item is None or not self._is_markdown_shape_value(shape_item.value, unit=unit):
                raise CompileError(
                    f"Output structure requires a markdown-bearing shape in output {decl.name}"
                )
            document_unit, document_decl = self._resolve_document_ref(decl.structure_ref, unit=unit)
            resolved_document = self._resolve_document_decl(document_decl, unit=document_unit)
            body.append(f"- Structure: {document_decl.title}")
            body.append("")
            body.append(
                CompiledSection(
                    title=f"Structure: {document_decl.title}",
                    body=self._compile_document_body(
                        resolved_document,
                        unit=document_unit,
                    ),
                    render_profile=explicit_render_profile or resolved_document.render_profile,
                )
            )

        trust_surface_section = (
            self._compile_trust_surface_section(
                decl,
                unit=unit,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
            if decl.trust_surface
            else None
        )

        if extras:
            support_items = self._compile_output_support_items(
                extras,
                unit=unit,
                owner_label=f"output {decl.name}",
                surface_label="output prose",
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
                trust_surface_section=trust_surface_section,
            )
            body.append("")
            body.extend(support_items)
        elif trust_surface_section is not None:
            body.append("")
            body.append(trust_surface_section)

        return CompiledSection(
            title=decl.title,
            body=tuple(body),
            render_profile=render_profile,
        )

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

    def _compile_trust_surface_section(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> CompiledSection:
        lines: list[CompiledBodyItem] = []
        for item in decl.trust_surface:
            field_node = self._resolve_output_field_node(
                decl,
                path=item.path,
                unit=unit,
                owner_label=f"output {decl.name}",
                surface_label="trust_surface",
                review_semantics=review_semantics,
            )
            label = self._display_addressable_target_value(
                field_node,
                owner_label=f"output {decl.name}",
                surface_label="trust_surface",
                route_semantics=route_semantics,
                render_profile=render_profile,
            ).text
            if item.when_expr is not None:
                label = self._render_trust_surface_label(
                    label,
                    item.when_expr,
                    unit=unit,
                )
            lines.append(f"- {label}")
        return CompiledSection(title="Trust Surface", body=tuple(lines))

    def _compile_output_files(
        self,
        section: model.RecordSection,
        *,
        unit: IndexedUnit,
        output_name: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in section.items:
            if not isinstance(item, model.RecordSection):
                raise CompileError(
                    f"`files` entries must be titled sections in output {output_name}"
                )
            scalar_items, _section_items, extras = self._split_record_items(
                item.items,
                scalar_keys={"path", "shape"},
                owner_label=f"output {output_name} file {item.key}",
            )
            path_item = scalar_items.get("path")
            shape_item = scalar_items.get("shape")
            if path_item is None or not isinstance(path_item.value, str):
                raise CompileError(
                    f"Output file entry is missing string path in {output_name}: {item.key}"
                )
            if shape_item is None:
                raise CompileError(
                    f"Output file entry is missing shape in {output_name}: {item.key}"
                )
            body.append(f"- {item.title}: `{path_item.value}`")
            body.append(
                f"- {item.title} Shape: {self._display_output_shape(shape_item.value, unit=unit, owner_label=f'output {output_name} file {item.key}', surface_label='output file fields')}"
            )
            if extras:
                body.append("")
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_record_support_items(
                            extras,
                            unit=unit,
                            owner_label=f"output {output_name} file {item.key}",
                            surface_label="output file prose",
                            review_semantics=review_semantics,
                            route_semantics=route_semantics,
                            render_profile=render_profile,
                        ),
                    )
                )
        return tuple(body)

    def _compile_record_support_items(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in items:
            body.extend(
                self._compile_record_item(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            )
        return tuple(body)

    def _compile_record_item(
        self,
        item: model.AnyRecordItem,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        if isinstance(item, (str, model.EmphasizedLine)):
            return (
                self._interpolate_authored_prose_line(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                ),
            )

        if isinstance(item, model.RecordSection):
            return (
                CompiledSection(
                    title=item.title,
                    body=self._compile_record_support_items(
                        item.items,
                        unit=unit,
                        owner_label=f"{owner_label}.{item.key}",
                        surface_label=surface_label,
                        review_semantics=review_semantics,
                        route_semantics=route_semantics,
                        render_profile=render_profile,
                    ),
                ),
            )

        if isinstance(item, model.ReadableBlock):
            return (
                self._compile_authored_readable_block(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                    section_body_compiler=lambda payload, nested_owner_label: self._compile_record_support_items(
                        payload,
                        unit=unit,
                        owner_label=nested_owner_label,
                        surface_label=surface_label,
                        review_semantics=review_semantics,
                        route_semantics=self._narrow_route_semantics(
                            route_semantics,
                            item.when_expr,
                            unit=unit,
                        ) if item.when_expr is not None else route_semantics,
                        render_profile=render_profile,
                    ),
                ),
            )

        if isinstance(item, model.GuardedOutputSection):
            guarded_route_semantics = self._narrow_route_semantics(
                route_semantics,
                item.when_expr,
                unit=unit,
            )
            condition = self._render_condition_expr(item.when_expr, unit=unit)
            body: list[CompiledBodyItem] = [f"Show this only when {condition}."]
            compiled_items = self._compile_record_support_items(
                item.items,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=guarded_route_semantics,
                render_profile=render_profile,
            )
            if compiled_items:
                body.append("")
                body.extend(compiled_items)
            return (CompiledSection(title=item.title, body=tuple(body)),)

        if isinstance(item, model.GuardedOutputScalar):
            guarded_route_semantics = self._narrow_route_semantics(
                route_semantics,
                item.when_expr,
                unit=unit,
            )
            label = _humanize_key(item.key)
            condition = self._render_condition_expr(item.when_expr, unit=unit)
            value = self._format_scalar_value(
                item.value,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=guarded_route_semantics,
                render_profile=render_profile,
            )
            body: list[CompiledBodyItem] = [f"Show this only when {condition}.", "", value]
            if item.body is not None:
                compiled_items = self._compile_record_support_items(
                    item.body,
                    unit=unit,
                    owner_label=f"{owner_label}.{item.key}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=guarded_route_semantics,
                    render_profile=render_profile,
                )
                if compiled_items:
                    body.append("")
                    body.extend(compiled_items)
            return (CompiledSection(title=label, body=tuple(body)),)

        if isinstance(item, model.RecordScalar):
            return self._compile_fallback_scalar(
                item,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )

        if isinstance(item, model.RecordRef):
            body = (
                self._compile_record_support_items(
                    item.body,
                    unit=unit,
                    owner_label=f"{owner_label}.{_dotted_ref_name(item.ref)}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
                if item.body is not None
                else ()
            )
            return (
                CompiledSection(
                    title=self._display_ref(item.ref, unit=unit),
                    body=body,
                ),
            )

        raise CompileError(f"Unsupported record item: {type(item).__name__}")

    def _compile_fallback_scalar(
        self,
        item: model.RecordScalar,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        label = _humanize_key(item.key)
        value = self._format_scalar_value(
            item.value,
            unit=unit,
            owner_label=f"{owner_label}.{item.key}",
            surface_label=surface_label,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
            render_profile=render_profile,
        )
        if item.body is None:
            return (f"- {label}: {value}",)

        body: list[CompiledBodyItem] = [value]
        body.extend(
            self._compile_record_support_items(
                item.body,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
        )
        return (CompiledSection(title=label, body=tuple(body)),)

    def _compile_authored_readable_block(
        self,
        block: model.ReadableBlock,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        section_body_compiler,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> CompiledReadableBlock:
        if block.when_expr is not None:
            self._validate_readable_guard_expr(
                block.when_expr,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=review_semantics is not None,
                allow_route_semantics=route_semantics is not None,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
        block_route_semantics = self._narrow_route_semantics(
            route_semantics,
            block.when_expr,
            unit=unit,
        )
        when_text = self._readable_guard_text(block.when_expr, unit=unit)
        title = None if block.kind == "properties" and block.anonymous else (
            block.title or _humanize_key(block.key)
        )
        block_owner_label = f"{owner_label}.{block.key}"
        if block.kind == "section":
            payload = self._require_tuple_payload(
                block.payload,
                owner_label=block_owner_label,
                kind="section",
            )
            return CompiledSection(
                title=title or _humanize_key(block.key),
                body=section_body_compiler(payload, block_owner_label),
                requirement=block.requirement,
                when_text=when_text,
                emit_metadata=True,
                semantic_target=_semantic_render_target_for_block(block.kind, block.key),
            )
        if block.kind in {"sequence", "bullets", "checklist"}:
            items: list[model.ProseLine] = []
            seen_keys: set[str] = set()
            for list_item in self._require_tuple_payload(
                block.payload,
                owner_label=block_owner_label,
                kind=block.kind,
            ):
                if not isinstance(list_item, model.ReadableListItem):
                    raise CompileError(
                        f"Readable {block.kind} items must stay list entries in {block_owner_label}"
                    )
                if list_item.key is not None:
                    if list_item.key in seen_keys:
                        raise CompileError(
                            f"Duplicate {block.kind} item key in {block_owner_label}: {list_item.key}"
                        )
                    seen_keys.add(list_item.key)
                items.append(
                    self._interpolate_authored_prose_line(
                        list_item.text,
                        unit=unit,
                        owner_label=block_owner_label,
                        surface_label=f"{block.kind} item prose",
                        ambiguous_label=f"{block.kind} item interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=block_route_semantics,
                        render_profile=render_profile,
                    )
                )
            item_schema = self._resolve_readable_inline_schema(
                block.item_schema,
                unit=unit,
                owner_label=block_owner_label,
                schema_label="item_schema",
                surface_label=f"{block.kind} item schema",
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            compiled_cls = {
                "sequence": CompiledSequenceBlock,
                "bullets": CompiledBulletsBlock,
                "checklist": CompiledChecklistBlock,
            }[block.kind]
            return compiled_cls(
                title=title,
                items=tuple(items),
                requirement=block.requirement,
                when_text=when_text,
                item_schema=item_schema,
                semantic_target=_semantic_render_target_for_block(block.kind, block.key),
            )
        if block.kind == "properties":
            properties = self._resolve_readable_properties_payload(
                block.payload,
                unit=unit,
                owner_label=block_owner_label,
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            return CompiledPropertiesBlock(
                title=title,
                entries=properties.entries,
                requirement=block.requirement,
                when_text=when_text,
                anonymous=block.anonymous,
            )
        if block.kind == "definitions":
            definitions: list[model.ReadableDefinitionItem] = []
            seen_keys: set[str] = set()
            for definition in self._require_tuple_payload(
                block.payload,
                owner_label=block_owner_label,
                kind="definitions",
            ):
                if not isinstance(definition, model.ReadableDefinitionItem):
                    raise CompileError(
                        f"Readable definitions entries must stay definition items in {block_owner_label}"
                    )
                if definition.key in seen_keys:
                    raise CompileError(
                        f"Duplicate definitions item key in {block_owner_label}: {definition.key}"
                    )
                seen_keys.add(definition.key)
                definitions.append(
                    replace(
                        definition,
                        body=tuple(
                            self._interpolate_authored_prose_line(
                                line,
                                unit=unit,
                                owner_label=f"{block_owner_label}.{definition.key}",
                                surface_label="definitions prose",
                                ambiguous_label="definitions prose interpolation ref",
                                review_semantics=review_semantics,
                                route_semantics=block_route_semantics,
                                render_profile=render_profile,
                            )
                            for line in definition.body
                        ),
                    )
                )
            return CompiledDefinitionsBlock(
                title=title,
                items=tuple(definitions),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "table":
            if not isinstance(block.payload, model.ReadableTableData):
                raise CompileError(
                    f"Readable table payload must stay table-shaped in {block_owner_label}"
                )
            resolved_columns: list[CompiledTableColumn] = []
            column_keys: set[str] = set()
            for column in block.payload.columns:
                if column.key in column_keys:
                    raise CompileError(
                        f"Duplicate table column key in {block_owner_label}: {column.key}"
                    )
                column_keys.add(column.key)
                resolved_columns.append(
                    CompiledTableColumn(
                        key=column.key,
                        title=column.title,
                        body=tuple(
                            self._interpolate_authored_prose_line(
                                line,
                                unit=unit,
                                owner_label=f"{block_owner_label}.columns.{column.key}",
                                surface_label="table column prose",
                                ambiguous_label="table column interpolation ref",
                                review_semantics=review_semantics,
                                route_semantics=block_route_semantics,
                                render_profile=render_profile,
                            )
                            for line in column.body
                        ),
                    )
                )
            if not resolved_columns:
                raise CompileError(
                    f"Readable table must declare at least one column in {block_owner_label}"
                )
            resolved_rows: list[CompiledTableRow] = []
            row_keys: set[str] = set()
            for row in block.payload.rows:
                if row.key in row_keys:
                    raise CompileError(
                        f"Duplicate table row key in {block_owner_label}: {row.key}"
                    )
                row_keys.add(row.key)
                cell_keys: set[str] = set()
                resolved_cells: list[CompiledTableCell] = []
                for cell in row.cells:
                    if cell.key not in column_keys:
                        raise CompileError(
                            f"Table row references an unknown column in {block_owner_label}: {cell.key}"
                        )
                    if cell.key in cell_keys:
                        raise CompileError(
                            f"Duplicate table row cell in {block_owner_label}.{row.key}: {cell.key}"
                        )
                    cell_keys.add(cell.key)
                    if cell.body is not None:
                        resolved_cells.append(
                            CompiledTableCell(
                                key=cell.key,
                                body=section_body_compiler(
                                    cell.body,
                                    f"{block_owner_label}.{row.key}.{cell.key}",
                                ),
                            )
                        )
                        continue
                    cell_text = self._interpolate_authored_prose_string(
                        cell.text or "",
                        unit=unit,
                        owner_label=f"{block_owner_label}.{row.key}.{cell.key}",
                        surface_label="table cell prose",
                        ambiguous_label="table cell interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=block_route_semantics,
                        render_profile=render_profile,
                    )
                    if "\n" in cell_text:
                        raise CompileError(
                            "Readable table inline cells must stay single-line in "
                            f"{block_owner_label}.{row.key}.{cell.key}; nested tables require structured cell bodies."
                        )
                    resolved_cells.append(CompiledTableCell(key=cell.key, text=cell_text))
                resolved_rows.append(CompiledTableRow(key=row.key, cells=tuple(resolved_cells)))
            resolved_notes = tuple(
                self._interpolate_authored_prose_line(
                    line,
                    unit=unit,
                    owner_label=block_owner_label,
                    surface_label="table notes",
                    ambiguous_label="table note interpolation ref",
                    review_semantics=review_semantics,
                    route_semantics=block_route_semantics,
                    render_profile=render_profile,
                )
                for line in block.payload.notes
            )
            row_schema = self._resolve_readable_inline_schema(
                block.row_schema or block.payload.row_schema,
                unit=unit,
                owner_label=block_owner_label,
                schema_label="row_schema",
                surface_label="table row schema",
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            return CompiledTableBlock(
                title=title or _humanize_key(block.key),
                table=CompiledTableData(
                    columns=tuple(resolved_columns),
                    rows=tuple(resolved_rows),
                    notes=resolved_notes,
                    row_schema=row_schema,
                ),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "guard":
            payload = self._require_tuple_payload(
                block.payload,
                owner_label=block_owner_label,
                kind="guard",
            )
            if when_text is None:
                raise CompileError(
                    f"Readable guard shells must define a guard expression in {block_owner_label}"
                )
            return CompiledGuardBlock(
                title=title or _humanize_key(block.key),
                body=section_body_compiler(payload, block_owner_label),
                when_text=when_text,
            )
        if block.kind == "callout":
            if not isinstance(block.payload, model.ReadableCalloutData):
                raise CompileError(
                    f"Readable callout payload must stay callout-shaped in {block_owner_label}"
                )
            if block.payload.kind is not None and block.payload.kind not in {
                "required",
                "important",
                "warning",
                "note",
            }:
                raise CompileError(
                    f"Unknown callout kind in {block_owner_label}: {block.payload.kind}"
                )
            return CompiledCalloutBlock(
                title=title or _humanize_key(block.key),
                kind=block.payload.kind,
                body=tuple(
                    self._interpolate_authored_prose_line(
                        line,
                        unit=unit,
                        owner_label=block_owner_label,
                        surface_label="callout prose",
                        ambiguous_label="callout interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=block_route_semantics,
                        render_profile=render_profile,
                    )
                    for line in block.payload.body
                ),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "code":
            if not isinstance(block.payload, model.ReadableCodeData):
                raise CompileError(
                    f"Readable code payload must stay code-shaped in {block_owner_label}"
                )
            if "\n" not in block.payload.text:
                raise CompileError(
                    f"Code block text must use a multiline string in {block_owner_label}"
                )
            return CompiledCodeBlock(
                title=title or _humanize_key(block.key),
                text=block.payload.text,
                language=block.payload.language,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind in {"markdown", "html"}:
            if not isinstance(block.payload, model.ReadableRawTextData):
                raise CompileError(
                    f"Readable {block.kind} payload must stay text-shaped in {block_owner_label}"
                )
            text = self._interpolate_authored_prose_string(
                block.payload.text,
                unit=unit,
                owner_label=block_owner_label,
                surface_label=f"{block.kind} text",
                ambiguous_label=f"{block.kind} interpolation ref",
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            if "\n" not in text:
                raise CompileError(
                    f"Raw {block.kind} blocks must use a multiline string in {block_owner_label}"
                )
            return CompiledRawTextBlock(
                title=title or _humanize_key(block.key),
                text=text,
                kind=block.kind,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "footnotes":
            footnotes = self._resolve_readable_footnotes_payload(
                block.payload,
                unit=unit,
                owner_label=block_owner_label,
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            return CompiledFootnotesBlock(
                title=title or _humanize_key(block.key),
                entries=footnotes.entries,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "image":
            if not isinstance(block.payload, model.ReadableImageData):
                raise CompileError(f"Readable image payload must stay image-shaped in {block_owner_label}")
            return CompiledImageBlock(
                title=title or _humanize_key(block.key),
                src=self._interpolate_authored_prose_string(
                    block.payload.src,
                    unit=unit,
                    owner_label=block_owner_label,
                    surface_label="image src",
                    ambiguous_label="image src interpolation ref",
                    review_semantics=review_semantics,
                    route_semantics=block_route_semantics,
                    render_profile=render_profile,
                ),
                alt=self._interpolate_authored_prose_string(
                    block.payload.alt,
                    unit=unit,
                    owner_label=block_owner_label,
                    surface_label="image alt",
                    ambiguous_label="image alt interpolation ref",
                    review_semantics=review_semantics,
                    route_semantics=block_route_semantics,
                    render_profile=render_profile,
                ),
                caption=(
                    self._interpolate_authored_prose_string(
                        block.payload.caption,
                        unit=unit,
                        owner_label=block_owner_label,
                        surface_label="image caption",
                        ambiguous_label="image caption interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=block_route_semantics,
                        render_profile=render_profile,
                    )
                    if block.payload.caption is not None
                    else None
                ),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "rule":
            return CompiledRuleBlock(
                requirement=block.requirement,
                when_text=when_text,
            )
        raise CompileError(f"Unsupported readable block kind in {block_owner_label}: {block.kind}")

    def _compile_config_lines(
        self,
        config_items: tuple[model.RecordItem, ...],
        *,
        spec: ConfigSpec,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        seen_keys: set[str] = set()
        allowed_keys = {**spec.required_keys, **spec.optional_keys}

        for item in config_items:
            if not isinstance(item, model.RecordScalar) or item.body is not None:
                raise CompileError(f"Config entries must be scalar key/value lines in {owner_label}")
            if item.key in seen_keys:
                raise CompileError(f"Duplicate config key in {owner_label}: {item.key}")
            seen_keys.add(item.key)
            if item.key not in allowed_keys:
                raise CompileError(f"Unknown config key in {owner_label}: {item.key}")
            body.append(
                f"- {allowed_keys[item.key]}: {self._format_scalar_value(item.value, unit=unit, owner_label=f'{owner_label}.{item.key}', surface_label='config values')}"
            )

        missing_required = [
            key for key in spec.required_keys if key not in seen_keys
        ]
        if missing_required:
            missing = ", ".join(missing_required)
            raise CompileError(f"Missing required config key in {owner_label}: {missing}")

        return tuple(body)

    def _compile_workflow_decl(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
        slot_key: str = "workflow",
    ) -> CompiledSection:
        workflow_key = (unit.module_parts, workflow_decl.name)
        if workflow_key in self._workflow_compile_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._workflow_compile_stack, workflow_key]
            )
            raise CompileError(f"Cyclic workflow composition: {cycle}")

        self._workflow_compile_stack.append(workflow_key)
        try:
            return self._compile_resolved_workflow(
                self._resolve_workflow_decl(workflow_decl, unit=unit),
                unit=unit,
                agent_contract=agent_contract,
                owner_label=f"workflow {_dotted_decl_name(unit.module_parts, workflow_decl.name)}",
                slot_key=slot_key,
            )
        finally:
            self._workflow_compile_stack.pop()

    def _compile_resolved_workflow(
        self,
        workflow_body: ResolvedWorkflowBody,
        *,
        unit: IndexedUnit | None = None,
        agent_contract: AgentContract | None = None,
        owner_label: str | None = None,
        slot_key: str = "workflow",
    ) -> CompiledSection:
        body: list[CompiledBodyItem] = list(workflow_body.preamble)
        if workflow_body.law is not None:
            if unit is None or agent_contract is None or owner_label is None:
                raise CompileError(
                    "Internal compiler error: workflow law requires unit, agent contract, and owner label"
                )
            if not _authored_slot_allows_law(slot_key):
                raise CompileError(
                    f"law may appear only on workflow or handoff_routing in {owner_label}: {slot_key}"
                )
            if body and body[-1] != "":
                body.append("")
            if slot_key == "handoff_routing":
                body.extend(
                    self._compile_handoff_routing_law(
                        workflow_body.law,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                    )
                )
            else:
                body.extend(
                    self._compile_workflow_law(
                        workflow_body.law,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                    )
                )
        for item in workflow_body.items:
            if body and body[-1] != "":
                body.append("")
            if isinstance(item, ResolvedSectionItem):
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_section_body(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                        ),
                    )
                )
                continue

            if isinstance(item, ResolvedWorkflowSkillsItem):
                body.append(self._compile_resolved_skills(item.body))
                continue

            body.append(
                self._compile_workflow_decl(
                    item.workflow_decl,
                    unit=item.target_unit,
                    agent_contract=agent_contract,
                    slot_key=slot_key,
                )
            )

        return CompiledSection(title=workflow_body.title, body=tuple(body))

    def _compile_workflow_law(
        self,
        law_body: model.LawBody,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        flat_items = self._flatten_law_items(law_body, owner_label=owner_label)
        self._validate_workflow_law(
            flat_items,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
        )

        lines: list[str] = []
        mode_bindings: dict[str, model.ModeStmt] = {}
        for item in flat_items:
            rendered: list[str] = []
            if isinstance(item, model.ActiveWhenStmt):
                rendered.append(
                    f"This pass runs only when {self._render_condition_expr(item.expr, unit=unit)}."
                )
            elif isinstance(item, model.ModeStmt):
                mode_bindings[item.name] = item
                fixed_mode = self._resolve_constant_enum_member(item.expr, unit=unit)
                if fixed_mode is not None:
                    rendered.append(f"Active mode: {fixed_mode}.")
            elif isinstance(item, model.MatchStmt):
                rendered.extend(
                    self._render_match_stmt(
                        item,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                    )
                )
            elif isinstance(item, model.RouteFromStmt):
                rendered.extend(
                    self._render_route_from_stmt(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                    )
                )
            elif isinstance(item, model.WhenStmt):
                rendered.extend(
                    self._render_when_stmt(
                        item,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                    )
                )
            else:
                rendered.extend(
                    self._render_law_stmt_lines(
                        item,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        bullet=False,
                    )
                )

            if not rendered:
                continue
            if lines:
                lines.append("")
            lines.extend(rendered)

        return tuple(lines)

    def _compile_handoff_routing_law(
        self,
        law_body: model.LawBody,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        flat_items = self._flatten_law_items(law_body, owner_label=owner_label)
        self._validate_handoff_routing_law(
            flat_items,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
        )

        lines: list[str] = []
        mode_bindings: dict[str, model.ModeStmt] = {}
        for item in flat_items:
            rendered: list[str] = []
            if isinstance(item, model.ActiveWhenStmt):
                rendered.append(
                    f"This pass runs only when {self._render_condition_expr(item.expr, unit=unit)}."
                )
            elif isinstance(item, model.ModeStmt):
                mode_bindings[item.name] = item
                fixed_mode = self._resolve_constant_enum_member(item.expr, unit=unit)
                if fixed_mode is not None:
                    rendered.append(f"Active mode: {fixed_mode}.")
            elif isinstance(item, model.MatchStmt):
                rendered.extend(
                    self._render_match_stmt(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                    )
                )
            elif isinstance(item, model.RouteFromStmt):
                rendered.extend(
                    self._render_route_from_stmt(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                    )
                )
            elif isinstance(item, model.WhenStmt):
                rendered.extend(
                    self._render_when_stmt(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                    )
                )
            else:
                rendered.extend(
                    self._render_law_stmt_lines(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        bullet=False,
                    )
                )

            if not rendered:
                continue
            if lines:
                lines.append("")
            lines.extend(rendered)

        return tuple(lines)

    def _compile_section_body(
        self,
        items: tuple[ResolvedSectionBodyItem, ...],
        *,
        unit: IndexedUnit | None = None,
        owner_label: str | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        previous_kind: str | None = None

        for item in items:
            current_kind = "ref" if isinstance(item, ResolvedSectionRef) else "prose"
            if previous_kind is not None and current_kind != previous_kind and body:
                if body[-1] != "":
                    body.append("")

            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(item)
            elif isinstance(item, ResolvedSectionItem):
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_section_body(
                            item.items,
                            unit=unit,
                            owner_label=(
                                f"{owner_label}.{item.key}" if owner_label is not None else None
                            ),
                        ),
                    )
                )
            elif isinstance(item, model.ReadableBlock):
                if unit is None or owner_label is None:
                    raise CompileError(
                        "Internal compiler error: workflow readable block compilation requires unit and owner label"
                    )
                body.append(
                    self._compile_authored_readable_block(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="workflow section bodies",
                        section_body_compiler=lambda payload, nested_owner_label: self._compile_section_body(
                            self._resolve_section_body_items(
                                payload,
                                unit=unit,
                                owner_label=nested_owner_label,
                            ),
                            unit=unit,
                            owner_label=nested_owner_label,
                        ),
                    )
                )
            elif isinstance(item, ResolvedRouteLine):
                body.append(f"{item.label} -> {item.target_display_name}")
            else:
                body.append(f"- {item.label}")

            previous_kind = current_kind

        return tuple(body)
