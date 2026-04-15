from __future__ import annotations

from doctrine import model
from concurrent.futures import ThreadPoolExecutor

from doctrine._compiler.naming import _agent_typed_field_key, _authored_slot_allows_law
from doctrine._compiler.resolved_types import (
    AgentContract,
    AgentFieldCompileSpec,
    CompileError,
    CompiledAgent,
    CompiledBodyItem,
    CompiledField,
    CompiledFinalOutputSpec,
    CompiledSection,
    IndexedUnit,
    OutputDeclKey,
    ResolvedAbstractAgentSlot,
    ResolvedAgentSlot,
    ResolvedIoBody,
    ResolvedSkillEntry,
    ResolvedSkillsBody,
    ResolvedSkillsSection,
    ResolvedSkillsSectionBodyItem,
    ReviewSemanticContext,
    RouteSemanticContext,
)
from doctrine._compiler.support_files import _default_worker_count, _dotted_decl_name


class CompileAgentMixin:
    """Agent compile helpers for CompilationContext."""

    def _compile_agent_decl(self, agent: model.Agent, *, unit: IndexedUnit) -> CompiledAgent:
        self._enforce_legacy_role_workflow_order(agent)
        resolved_slot_states = self._resolve_agent_slots(agent, unit=unit)
        agent_contract = self._resolve_agent_contract(agent, unit=unit)
        unresolved_abstract_slots = [
            slot.key
            for slot in resolved_slot_states
            if isinstance(slot, ResolvedAbstractAgentSlot)
        ]
        if unresolved_abstract_slots:
            missing = ", ".join(unresolved_abstract_slots)
            raise CompileError(
                f"E209 Concrete agent is missing abstract authored slots in agent {agent.name}: {missing}"
            )
        resolved_slots = {
            slot.key: slot.body
            for slot in resolved_slot_states
            if isinstance(slot, ResolvedAgentSlot)
        }
        has_workflow_slot = "workflow" in resolved_slots
        review_fields = [
            field for field in agent.fields if isinstance(field, model.ReviewField)
        ]
        final_output_fields = [
            field for field in agent.fields if isinstance(field, model.FinalOutputField)
        ]
        final_output_field = final_output_fields[0] if final_output_fields else None
        if has_workflow_slot and review_fields:
            raise CompileError(
                f"Concrete agent may not define both `workflow` and `review`: {agent.name}"
            )
        self._validate_agent_slot_laws(
            agent,
            unit=unit,
            resolved_slots=resolved_slots,
            agent_contract=agent_contract,
        )
        _ = self._route_semantic_context_for_agent(
            agent,
            unit=unit,
            resolved_slots=resolved_slots,
            agent_contract=agent_contract,
        )
        review_output_contexts = self._review_output_contexts_for_agent(agent, unit=unit)
        route_output_contexts = self._route_output_contexts_for_agent(
            agent,
            unit=unit,
            resolved_slots=resolved_slots,
            agent_contract=agent_contract,
        )
        primary_review_output_context = self._primary_review_output_context(
            review_output_contexts
        )
        review_contract = self._compile_agent_review_contract(
            agent=agent,
            unit=unit,
            agent_contract=agent_contract,
            final_output_field=final_output_field,
        )
        field_specs: list[AgentFieldCompileSpec] = []
        seen_role = False
        seen_typed_fields: set[str] = set()

        for field in agent.fields:
            if isinstance(field, model.RoleScalar):
                if seen_role:
                    raise CompileError(f"Duplicate role field in agent {agent.name}")
                seen_role = True
                field_specs.append(AgentFieldCompileSpec(field=field))
                continue

            if isinstance(field, model.RoleBlock):
                if seen_role:
                    raise CompileError(f"Duplicate role field in agent {agent.name}")
                seen_role = True
                field_specs.append(AgentFieldCompileSpec(field=field))
                continue

            if isinstance(
                field,
                (
                    model.AuthoredSlotField,
                    model.AuthoredSlotAbstract,
                    model.AuthoredSlotInherit,
                    model.AuthoredSlotOverride,
                ),
            ):
                slot_body = resolved_slots.get(field.key)
                if slot_body is None:
                    raise CompileError(
                        f"Internal compiler error: missing resolved authored slot in agent {agent.name}: {field.key}"
                    )
                field_specs.append(AgentFieldCompileSpec(field=field, slot_body=slot_body))
                continue

            field_key = _agent_typed_field_key(field)
            if field_key in seen_typed_fields:
                raise CompileError(f"Duplicate typed field in agent {agent.name}: {field_key}")
            seen_typed_fields.add(field_key)
            field_specs.append(AgentFieldCompileSpec(field=field))

        if not seen_role:
            raise CompileError(f"Concrete agent is missing role field: {agent.name}")

        final_output = (
            self._compile_final_output_spec(
                agent_name=agent.name,
                field=final_output_field,
                unit=unit,
                agent_contract=agent_contract,
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                review_contract=review_contract,
                fallback_review_semantics=(
                    primary_review_output_context[1]
                    if primary_review_output_context is not None
                    else None
                ),
            )
            if final_output_field is not None
            else None
        )
        compiled_fields = self._compile_agent_fields(
            field_specs,
            agent_name=agent.name,
            unit=unit,
            agent_contract=agent_contract,
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            final_output=final_output,
        )
        return CompiledAgent(
            name=agent.name,
            fields=compiled_fields,
            final_output=final_output,
            review=review_contract,
        )

    def _compile_agent_fields(
        self,
        specs: list[AgentFieldCompileSpec],
        *,
        agent_name: str,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]],
        final_output: CompiledFinalOutputSpec | None,
    ) -> tuple[CompiledField, ...]:
        if len(specs) <= 1:
            compiled = [
                self._compile_agent_field(
                    spec,
                    agent_name=agent_name,
                    unit=unit,
                    agent_contract=agent_contract,
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    final_output=final_output,
                )
                for spec in specs
            ]
            return tuple(field for field in compiled if field is not None)

        with ThreadPoolExecutor(max_workers=_default_worker_count(len(specs))) as executor:
            futures = [
                executor.submit(
                    self.session._compile_agent_field_task,
                    spec,
                    agent_name=agent_name,
                    unit=unit,
                    agent_contract=agent_contract,
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    final_output=final_output,
                )
                for spec in specs
            ]
            return tuple(
                field
                for future in futures
                if (field := future.result()) is not None
            )

    def _compile_agent_field(
        self,
        spec: AgentFieldCompileSpec,
        *,
        agent_name: str,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]],
        final_output: CompiledFinalOutputSpec | None,
    ) -> CompiledField | None:
        field = spec.field

        if isinstance(field, model.RoleScalar):
            return model.RoleScalar(
                text=self._interpolate_authored_prose_string(
                    field.text,
                    unit=unit,
                    owner_label=f"agent {agent_name}",
                    surface_label="role prose",
                )
            )

        if isinstance(field, model.RoleBlock):
            return CompiledSection(
                title=field.title,
                body=tuple(
                    self._interpolate_authored_prose_line(
                        line,
                        unit=unit,
                        owner_label=f"agent {agent_name}",
                        surface_label="role prose",
                    )
                    for line in field.lines
                ),
            )

        if isinstance(
            field,
            (
                model.AuthoredSlotField,
                model.AuthoredSlotAbstract,
                model.AuthoredSlotInherit,
                model.AuthoredSlotOverride,
            ),
        ):
            if spec.slot_body is None:
                raise CompileError(
                    f"Internal compiler error: missing resolved authored slot in agent {agent_name}"
                )
            if field.key == "workflow":
                return self._compile_resolved_workflow(
                    spec.slot_body,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=f"agent {agent_name} workflow",
                    slot_key=field.key,
                )
            if field.key == "handoff_routing":
                return self._compile_resolved_workflow(
                    spec.slot_body,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=f"agent {agent_name} slot {field.key}",
                    slot_key=field.key,
                )
            if spec.slot_body.law is not None and not _authored_slot_allows_law(field.key):
                raise CompileError(
                    f"law may appear only on workflow or handoff_routing in agent {agent_name}: {field.key}"
                )
            return self._compile_resolved_workflow(
                spec.slot_body,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=f"agent {agent_name} slot {field.key}",
                slot_key=field.key,
            )

        if isinstance(field, model.InputsField):
            return self._compile_inputs_field(
                field,
                unit=unit,
                owner_label=f"agent {agent_name}",
            )
        if isinstance(field, model.OutputsField):
            return self._compile_outputs_field(
                field,
                unit=unit,
                owner_label=f"agent {agent_name}",
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                excluded_output_keys=(
                    frozenset({final_output.output_key}) if final_output is not None else frozenset()
                ),
            )
        if isinstance(field, model.AnalysisField):
            analysis_unit, analysis_decl = self._resolve_analysis_ref(field.value, unit=unit)
            return self._compile_analysis_decl(analysis_decl, unit=analysis_unit)
        if isinstance(field, model.DecisionField):
            decision_unit, decision_decl = self._resolve_decision_ref(field.value, unit=unit)
            return self._compile_decision_decl(decision_decl, unit=decision_unit)
        if isinstance(field, model.SkillsField):
            return self._compile_skills_field(field, unit=unit)
        if isinstance(field, model.ReviewField):
            review_unit, review_decl = self._resolve_review_ref(field.value, unit=unit)
            if review_decl.abstract:
                raise CompileError(
                    "Concrete agents may not attach abstract reviews directly: "
                    f"{_dotted_decl_name(review_unit.module_parts, review_decl.name)}"
                )
            return self._compile_review_decl(
                review_decl,
                unit=review_unit,
                agent_contract=agent_contract,
                owner_label=f"agent {agent_name} review",
            )
        if isinstance(field, model.FinalOutputField):
            if final_output is None or final_output.section is None:
                raise CompileError(
                    f"Internal compiler error: missing compiled final_output in agent {agent_name}"
                )
            return final_output.section

        raise CompileError(
            f"Unsupported agent field in {agent_name}: {type(field).__name__}"
        )

    def _compile_inputs_field(
        self,
        field: model.InputsField,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> CompiledSection:
        return self._compile_io_field(
            field=field,
            unit=unit,
            field_kind="inputs",
            owner_label=owner_label,
        )

    def _compile_outputs_field(
        self,
        field: model.OutputsField,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> CompiledSection | None:
        return self._compile_io_field(
            field=field,
            unit=unit,
            field_kind="outputs",
            owner_label=owner_label,
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            excluded_output_keys=excluded_output_keys,
        )

    def _compile_io_field(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> CompiledSection | None:
        if field.parent_ref is not None:
            resolved = self._resolve_io_field_patch(
                field,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                excluded_output_keys=excluded_output_keys,
            )
            if field_kind == "outputs" and self._resolved_io_body_is_empty(resolved):
                return None
            return self._compile_resolved_io_body(resolved)

        if isinstance(field.value, tuple):
            if field.title is None:
                raise CompileError(
                    f"Internal compiler error: {field_kind} field is missing title in {owner_label}"
                )
            compiled_section = CompiledSection(
                title=field.title,
                body=self._compile_contract_bucket_items(
                    field.value,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=f"{field_kind} field `{field.title}`",
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=excluded_output_keys,
                ),
            )
            if field_kind == "outputs" and not compiled_section.body:
                return None
            return compiled_section

        if isinstance(field.value, model.NameRef):
            resolved = self._resolve_io_field_ref(
                field.value,
                unit=unit,
                field_kind=field_kind,
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                excluded_output_keys=excluded_output_keys,
            )
            if field_kind == "outputs" and self._resolved_io_body_is_empty(resolved):
                return None
            return self._compile_resolved_io_body(resolved)

        raise CompileError(
            f"Internal compiler error: unsupported {field_kind} field value in {owner_label}: "
            f"{type(field.value).__name__}"
        )

    def _compile_resolved_io_body(self, io_body: ResolvedIoBody) -> CompiledSection:
        body: list[CompiledBodyItem] = list(io_body.preamble)
        for item in io_body.items:
            body.append(item.section)
        return CompiledSection(title=io_body.title, body=tuple(body))

    def _compile_skills_field(
        self,
        field: model.SkillsField,
        *,
        unit: IndexedUnit,
    ) -> CompiledSection:
        return self._compile_resolved_skills(
            self._resolve_skills_value(
                field.value,
                unit=unit,
                owner_label="agent skills field",
            )
        )

    def _compile_contract_bucket_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> tuple[CompiledBodyItem, ...]:
        return self._resolve_contract_bucket_items(
            items,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            excluded_output_keys=excluded_output_keys,
        ).body

    def _compile_contract_bucket_ref(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> CompiledSection | None:
        resolved_ref = self._resolve_contract_bucket_ref_entry(
            item,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            excluded_output_keys=excluded_output_keys,
        )
        if resolved_ref is None:
            return None
        section, _artifact = resolved_ref
        return section

    def _compile_resolved_skills(self, skills_body: ResolvedSkillsBody) -> CompiledSection:
        body: list[CompiledBodyItem] = list(skills_body.preamble)
        for item in skills_body.items:
            if isinstance(item, ResolvedSkillsSection):
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_resolved_skills_section_items(item.items),
                    )
                )
                continue
            body.append(self._compile_resolved_skill_entry(item))
        return CompiledSection(title=skills_body.title, body=tuple(body))

    def _compile_resolved_skills_section_items(
        self,
        items: tuple[ResolvedSkillsSectionBodyItem, ...],
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(item)
                continue
            body.append(self._compile_resolved_skill_entry(item))
        return tuple(body)

    def _compile_resolved_skill_entry(self, entry: ResolvedSkillEntry) -> CompiledSection:
        target_unit = entry.target_unit
        skill_decl = entry.skill_decl
        scalar_items, _section_items, extras = self._split_record_items(
            skill_decl.items,
            scalar_keys={"purpose"},
            owner_label=f"skill {skill_decl.name}",
        )
        purpose_item = scalar_items.get("purpose")
        if purpose_item is None or not isinstance(purpose_item.value, str):
            raise CompileError(f"Skill is missing string purpose: {skill_decl.name}")

        metadata_scalars, _metadata_sections, metadata_extras = self._split_record_items(
            entry.items,
            scalar_keys={"requirement", "reason"},
            owner_label=f"skill reference {skill_decl.name}",
        )

        body: list[CompiledBodyItem] = []
        purpose_body: list[CompiledBodyItem] = [
            self._interpolate_authored_prose_string(
                purpose_item.value,
                unit=target_unit,
                owner_label=f"skill {skill_decl.name}",
                surface_label="skill purpose",
            )
        ]
        requirement = metadata_scalars.get("requirement")
        if (
            requirement is not None
            and self._value_to_symbol(
                requirement.value,
                unit=entry.metadata_unit,
                owner_label=f"skill reference {skill_decl.name}",
                surface_label="skill reference metadata",
            )
            == "Required"
        ):
            purpose_body.extend(
                [
                    "",
                    "This skill is required for this role. If you cannot locate it, stop and escalate instead of guessing.",
                ]
            )
        body.append(CompiledSection(title="Purpose", body=tuple(purpose_body)))

        for extra in extras:
            body.extend(
                self._compile_record_item(
                    extra,
                    unit=target_unit,
                    owner_label=f"skill {skill_decl.name}",
                    surface_label="skill prose",
                )
            )

        reason = metadata_scalars.get("reason")
        if reason is not None:
            if not isinstance(reason.value, str):
                raise CompileError(
                    f"Skill reference reason must be a string in {skill_decl.name}"
                )
            body.append(
                CompiledSection(
                    title="Reason",
                    body=(
                        self._interpolate_authored_prose_string(
                            reason.value,
                            unit=entry.metadata_unit,
                            owner_label=f"skill reference {skill_decl.name}",
                            surface_label="skill reason",
                        ),
                    ),
                )
            )

        for extra in metadata_extras:
            body.extend(
                self._compile_record_item(
                    extra,
                    unit=entry.metadata_unit,
                    owner_label=f"skill reference {skill_decl.name}",
                    surface_label="skill reference prose",
                )
            )

        return CompiledSection(title=skill_decl.title, body=tuple(body))
