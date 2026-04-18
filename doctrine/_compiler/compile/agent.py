from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from doctrine import model
from doctrine._compiler.diagnostics import compile_error, related_prompt_site
from doctrine._compiler.naming import (
    _agent_typed_field_key,
    _authored_slot_allows_law,
    _humanize_key,
)
from doctrine._compiler.resolved_types import (
    ActiveSkillBindAgentContext,
    AgentContract,
    AgentFieldCompileSpec,
    CompileError,
    CompiledAgent,
    CompiledBodyItem,
    CompiledField,
    CompiledFinalOutputSpec,
    CompiledIoContractSpec,
    CompiledPreviousTurnInputSpec,
    CompiledPreviousTurnOutputBindingSpec,
    CompiledPreviousTurnOutputSpec,
    CompiledRouteBranchSpec,
    CompiledRouteChoiceMemberSpec,
    CompiledRouteContractSpec,
    CompiledRouteSelectorSpec,
    CompiledRouteTargetSpec,
    CompiledSection,
    IndexedUnit,
    OutputDeclKey,
    ResolvedAbstractAgentSlot,
    ResolvedAgentSlot,
    ResolvedIoBody,
    ResolvedPreviousTurnInputSpec,
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
        self._enforce_legacy_role_workflow_order(agent, unit=unit)
        resolved_slot_states = self._resolve_agent_slots(agent, unit=unit)
        agent_contract = self._resolve_agent_contract(agent, unit=unit)
        agent_key = self._flow_agent_key(unit, agent.name)
        previous_turn_input_specs = tuple(
            spec
            for spec in (
                self._resolve_previous_turn_input_spec(
                    input_decl,
                    unit=input_unit,
                    agent_key=agent_key,
                )
                for (_input_key, (input_unit, input_decl)) in sorted(agent_contract.inputs.items())
            )
            if spec is not None
        )
        self._active_agent_key = agent_key
        self._active_previous_turn_input_specs = {
            spec.input_key: spec for spec in previous_turn_input_specs
        }
        prior_skill_bind_context = self._active_skill_bind_agent_context
        try:
            unresolved_abstract_slots = [
                slot.key
                for slot in resolved_slot_states
                if isinstance(slot, ResolvedAbstractAgentSlot)
            ]
            if unresolved_abstract_slots:
                missing_slot = next(
                    (
                        field
                        for field in agent.fields
                        if isinstance(field, model.AuthoredSlotAbstract)
                        and field.key in unresolved_abstract_slots
                    ),
                    None,
                )
                raise compile_error(
                    code="E209",
                    summary="Concrete agent is missing abstract authored slots",
                    detail=(
                        f"Concrete agent `{agent.name}` must define abstract authored slots: "
                        f"{', '.join(f'`{slot}`' for slot in unresolved_abstract_slots)}."
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=None if missing_slot is None else missing_slot.source_span,
                    hints=("Define each missing slot directly with `slot_key: ...`.",),
                )
            resolved_slots = {
                slot.key: slot.body
                for slot in resolved_slot_states
                if isinstance(slot, ResolvedAgentSlot)
            }
            has_workflow_slot = "workflow" in resolved_slots
            workflow_field = next(
                (
                    field
                    for field in agent.fields
                    if isinstance(
                        field,
                        (
                            model.AuthoredSlotField,
                            model.AuthoredSlotAbstract,
                            model.AuthoredSlotInherit,
                            model.AuthoredSlotOverride,
                        ),
                    )
                    and field.key == "workflow"
                ),
                None,
            )
            review_fields = [
                field for field in agent.fields if isinstance(field, model.ReviewField)
            ]
            final_output_fields = [
                field for field in agent.fields if isinstance(field, model.FinalOutputField)
            ]
            final_output_field = final_output_fields[0] if final_output_fields else None
            analysis_field = next(
                (field for field in agent.fields if isinstance(field, model.AnalysisField)),
                None,
            )
            self._active_skill_bind_agent_context = ActiveSkillBindAgentContext(
                agent=agent,
                unit=unit,
                agent_contract=agent_contract,
                analysis_field=analysis_field,
                final_output_field=final_output_field,
            )
            if has_workflow_slot and review_fields:
                raise compile_error(
                    code="E480",
                    summary="Concrete agent defines both workflow and review",
                    detail=(
                        f"Concrete agent `{agent.name}` may not define both "
                        "`workflow:` and `review:`."
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=review_fields[0].source_span,
                    related=(
                        related_prompt_site(
                            label="`workflow` field",
                            path=unit.prompt_file.source_path,
                            source_span=(
                                None if workflow_field is None else workflow_field.source_span
                            ),
                        ),
                    ),
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
            first_role_field: model.RoleScalar | model.RoleBlock | None = None
            seen_typed_fields: dict[str, model.Field] = {}

            for field in agent.fields:
                if isinstance(field, model.RoleScalar):
                    if seen_role:
                        raise compile_error(
                            code="E203",
                            summary="Duplicate role field",
                            detail=f"Agent `{agent.name}` defines `role` more than once.",
                            path=unit.prompt_file.source_path,
                            source_span=field.source_span,
                            related=(
                                related_prompt_site(
                                    label="first `role` field",
                                    path=unit.prompt_file.source_path,
                                    source_span=None if first_role_field is None else first_role_field.source_span,
                                ),
                            ),
                            hints=("Keep exactly one `role:` field per concrete agent.",),
                        )
                    seen_role = True
                    first_role_field = field
                    field_specs.append(AgentFieldCompileSpec(field=field))
                    continue

                if isinstance(field, model.RoleBlock):
                    if seen_role:
                        raise compile_error(
                            code="E203",
                            summary="Duplicate role field",
                            detail=f"Agent `{agent.name}` defines `role` more than once.",
                            path=unit.prompt_file.source_path,
                            source_span=field.source_span,
                            related=(
                                related_prompt_site(
                                    label="first `role` field",
                                    path=unit.prompt_file.source_path,
                                    source_span=None if first_role_field is None else first_role_field.source_span,
                                ),
                            ),
                            hints=("Keep exactly one `role:` field per concrete agent.",),
                        )
                    seen_role = True
                    first_role_field = field
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
                        raise compile_error(
                            code="E901",
                            summary="Internal compiler error",
                            detail=(
                                "Internal compiler error: missing resolved authored slot in "
                                f"agent {agent.name}: {field.key}"
                            ),
                            path=unit.prompt_file.source_path,
                            source_span=getattr(field, "source_span", None),
                        )
                    field_specs.append(AgentFieldCompileSpec(field=field, slot_body=slot_body))
                    continue

                field_key = _agent_typed_field_key(field)
                first_typed_field = seen_typed_fields.get(field_key)
                if first_typed_field is not None:
                    raise compile_error(
                        code="E204",
                        summary="Duplicate typed field",
                        detail=(
                            f"Agent `{agent.name}` defines typed field `{field_key}` more than once."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=getattr(field, "source_span", None),
                        related=(
                            related_prompt_site(
                                label=f"first `{field_key}` field",
                                path=unit.prompt_file.source_path,
                                source_span=getattr(first_typed_field, "source_span", None),
                            ),
                        ),
                        hints=(f"Keep exactly one `{field_key}:` field on the agent.",),
                    )
                seen_typed_fields[field_key] = field
                field_specs.append(AgentFieldCompileSpec(field=field))

            if not seen_role:
                raise compile_error(
                    code="E205",
                    summary="Concrete agent is missing role field",
                    detail=f"Concrete agent `{agent.name}` is missing its required `role` field.",
                    path=unit.prompt_file.source_path,
                    source_span=agent.source_span,
                    hints=("Add a `role:` field before the rest of the authored workflow surface.",),
                )

            selectors_field = next(
                (field for field in agent.fields if isinstance(field, model.SelectorsField)),
                None,
            )
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
                    selectors_field=selectors_field,
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
            route_contract = self._compile_final_response_route_contract(
                final_output=final_output,
                review_contract=review_contract,
                route_output_contexts=route_output_contexts,
            )
            io_contract = self._compile_agent_io_contract(
                agent_contract=agent_contract,
                previous_turn_inputs=previous_turn_input_specs,
                final_output=final_output,
            )
            return CompiledAgent(
                name=agent.name,
                fields=compiled_fields,
                final_output=final_output,
                review=review_contract,
                route=route_contract,
                io=io_contract,
            )
        finally:
            self._active_skill_bind_agent_context = prior_skill_bind_context
            self._active_agent_key = None
            self._active_previous_turn_input_specs = {}

    def _compile_agent_io_contract(
        self,
        *,
        agent_contract: AgentContract,
        previous_turn_inputs: tuple[ResolvedPreviousTurnInputSpec, ...],
        final_output: CompiledFinalOutputSpec | None,
    ) -> CompiledIoContractSpec:
        final_output_key = None if final_output is None else final_output.output_key
        outputs = tuple(
            self._compile_previous_turn_output_spec(
                output_key=output_key,
                output_unit=output_unit,
                output_decl=output_decl,
                final_output_key=final_output_key,
            )
            for output_key, (output_unit, output_decl) in sorted(agent_contract.outputs.items())
        )
        output_bindings = tuple(
            CompiledPreviousTurnOutputBindingSpec(
                binding_path=binding_path,
                output_key=(binding.artifact.unit.module_parts, binding.artifact.decl.name),
            )
            for binding_path, binding in sorted(agent_contract.output_bindings_by_path.items())
            if isinstance(binding.artifact.decl, model.OutputDecl)
        )
        return CompiledIoContractSpec(
            previous_turn_inputs=tuple(
                CompiledPreviousTurnInputSpec(
                    input_key=spec.input_key,
                    input_name=spec.input_decl.name,
                    input_title=spec.input_decl.title,
                    requirement=spec.requirement,
                    selector_kind=spec.selector_kind,
                    selector_text=spec.selector_text,
                    output_key=spec.output_key,
                    output_name=spec.output_decl.name,
                    output_title=spec.output_decl.title,
                    derived_contract_mode=spec.derived_contract_mode,
                    target_key=spec.target_key,
                    target_title=spec.target_title,
                    target_config=spec.target_config,
                    shape_name=spec.shape_name,
                    shape_title=spec.shape_title,
                    schema_name=spec.schema_name,
                    schema_title=spec.schema_title,
                    schema_profile=spec.schema_profile,
                    lowered_schema=spec.lowered_schema,
                    binding_path=spec.binding_path,
                )
                for spec in previous_turn_inputs
            ),
            outputs=outputs,
            output_bindings=output_bindings,
        )

    def _compile_previous_turn_output_spec(
        self,
        *,
        output_key: OutputDeclKey,
        output_unit: IndexedUnit,
        output_decl: model.OutputDecl,
        final_output_key: OutputDeclKey | None,
    ) -> CompiledPreviousTurnOutputSpec:
        scalar_items, section_items, _extras = self._split_record_items(
            output_decl.items,
            scalar_keys={"target", "shape", "requirement"},
            section_keys={"files"},
            owner_label=f"output {output_decl.name}",
        )
        files_section = section_items.get("files")
        if files_section is not None:
            return CompiledPreviousTurnOutputSpec(
                output_key=output_key,
                output_name=output_decl.name,
                output_title=output_decl.title,
                target_key="FileSet",
                target_title="File Set",
            )
        target_item = scalar_items.get("target")
        shape_item = scalar_items.get("shape")
        if target_item is None or shape_item is None or not isinstance(target_item.value, model.NameRef):
            return CompiledPreviousTurnOutputSpec(
                output_key=output_key,
                output_name=output_decl.name,
                output_title=output_decl.title,
                target_key="Unsupported",
                target_title="Unsupported",
            )
        (
            target_key,
            target_title,
            target_config,
            shape_name,
            shape_title,
            schema_name,
            schema_title,
            schema_profile,
            _lowered_schema,
            derived_contract_mode,
        ) = self._resolve_previous_turn_output_contract(output_decl, unit=output_unit)
        readback_mode = "unsupported"
        requires_final_output = False
        if self._is_builtin_turn_response_target_ref(target_item.value):
            requires_final_output = True
            if final_output_key == output_key:
                readback_mode = derived_contract_mode
        elif not target_item.value.module_parts and target_item.value.declaration_name == "File":
            readback_mode = derived_contract_mode
        return CompiledPreviousTurnOutputSpec(
            output_key=output_key,
            output_name=output_decl.name,
            output_title=output_decl.title,
            target_key=target_key,
            target_title=target_title,
            target_config=target_config,
            shape_name=shape_name,
            shape_title=shape_title,
            derived_contract_mode=derived_contract_mode,
            readback_mode=readback_mode,
            requires_final_output=requires_final_output,
            schema_name=schema_name,
            schema_title=schema_title,
            schema_profile=schema_profile,
        )

    def _compile_final_response_route_contract(
        self,
        *,
        final_output: CompiledFinalOutputSpec | None,
        review_contract,
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]],
    ) -> CompiledRouteContractSpec | None:
        contract_output_key = self._final_response_contract_output_key(
            final_output=final_output,
            review_contract=review_contract,
        )
        if contract_output_key is None:
            return None

        route_semantics = self._route_output_context_for_key(
            route_output_contexts,
            contract_output_key,
        )
        if route_semantics is None:
            return self._empty_final_response_route_contract()

        branches = tuple(
            CompiledRouteBranchSpec(
                target=CompiledRouteTargetSpec(
                    key=_dotted_decl_name(
                        branch.target_module_parts,
                        branch.target_name,
                    ),
                    module_parts=branch.target_module_parts,
                    name=branch.target_name,
                    title=self._route_semantic_branch_title(branch),
                ),
                label=branch.label,
                summary=self._route_semantic_branch_summary(branch),
                review_verdict=branch.review_verdict,
                choice_members=tuple(
                    CompiledRouteChoiceMemberSpec(
                        member_key=member.member_key,
                        member_title=member.member_title,
                        member_wire=member.member_wire,
                        enum_module_parts=member.enum_module_parts,
                        enum_name=member.enum_name,
                    )
                    for member in branch.choice_members
                ),
            )
            for branch in route_semantics.branches
        )
        return CompiledRouteContractSpec(
            exists=True,
            behavior=self._route_contract_behavior(route_semantics),
            has_unrouted_branch=route_semantics.has_unrouted_branch,
            unrouted_review_verdicts=tuple(sorted(route_semantics.unrouted_review_verdicts)),
            branches=branches,
            selector=(
                None
                if route_semantics.selector is None
                else CompiledRouteSelectorSpec(
                    surface=route_semantics.selector.surface,
                    field_path=route_semantics.selector.field_path,
                    null_behavior=route_semantics.selector.null_behavior,
                )
            ),
        )

    def _final_response_contract_output_key(
        self,
        *,
        final_output: CompiledFinalOutputSpec | None,
        review_contract,
    ) -> OutputDeclKey | None:
        if final_output is not None:
            return final_output.output_key
        if review_contract is None:
            return None
        # Review carrier and split final responses share the same top-level
        # route contract so harnesses do not need a review-only routing bridge.
        if review_contract.final_response.mode == "split":
            return review_contract.final_response.output_key
        return review_contract.comment_output.output_key

    def _empty_final_response_route_contract(self) -> CompiledRouteContractSpec:
        return CompiledRouteContractSpec(
            exists=False,
            behavior="never",
            has_unrouted_branch=False,
            unrouted_review_verdicts=(),
            branches=(),
            selector=None,
        )

    def _route_contract_behavior(
        self,
        route_semantics: RouteSemanticContext,
    ) -> str:
        if not route_semantics.branches:
            return "never"
        if route_semantics.has_unrouted_branch and not route_semantics.route_required:
            return "conditional"
        return "always"

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
                    previous_turn_contexts=self._previous_turn_contexts,
                    active_agent_key=self._active_agent_key,
                    active_skill_bind_agent_context=self._active_skill_bind_agent_context,
                    active_previous_turn_input_specs=self._active_previous_turn_input_specs,
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
                raise compile_error(
                    code="E901",
                    summary="Internal compiler error",
                    detail=(
                        "Internal compiler error: missing resolved authored slot in "
                        f"agent {agent_name}"
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=getattr(field, "source_span", None),
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
                raise compile_error(
                    code="E345",
                    summary="Law is not allowed on this authored slot",
                    detail=(
                        f"`law:` is not allowed on authored slot `{field.key}` in "
                        f"agent {agent_name}."
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=getattr(field, "source_span", None),
                    hints=(
                        "Attach `law:` only to `workflow:` or `handoff_routing:`.",
                        "Keep other authored slots as readable instruction surfaces.",
                    ),
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
        if isinstance(field, model.SelectorsField):
            return None
        if isinstance(field, model.SkillsField):
            return self._compile_skills_field(field, unit=unit)
        if isinstance(field, model.ReviewField):
            review_unit, review_decl = self._resolve_review_ref(field.value, unit=unit)
            if review_decl.abstract:
                raise compile_error(
                    code="E494",
                    summary="Concrete agent may not attach abstract review directly",
                    detail=(
                        "Concrete agent may not attach abstract review "
                        f"`{_dotted_decl_name(review_unit.module_parts, review_decl.name)}` "
                        "directly."
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=field.source_span,
                )
            return self._compile_review_decl(
                review_decl,
                unit=review_unit,
                agent_contract=agent_contract,
                owner_label=f"agent {agent_name} review",
            )
        if isinstance(field, model.FinalOutputField):
            if final_output is None or final_output.section is None:
                raise compile_error(
                    code="E901",
                    summary="Internal compiler error",
                    detail=(
                        "Internal compiler error: missing compiled final_output in "
                        f"agent {agent_name}"
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=field.source_span,
                )
            return final_output.section

        raise compile_error(
            code="E208",
            summary="Unsupported agent field",
            detail=(
                f"Agent `{agent_name}` uses unsupported field type "
                f"`{type(field).__name__}`."
            ),
            path=unit.prompt_file.source_path,
            source_span=getattr(field, "source_span", None),
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
                raise compile_error(
                    code="E901",
                    summary="Internal compiler error",
                    detail=(
                        f"Internal compiler error: {field_kind} field is missing title "
                        f"in {owner_label}"
                    ),
                    path=unit.prompt_file.source_path,
                    source_span=field.source_span,
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

        raise compile_error(
            code="E901",
            summary="Internal compiler error",
            detail=(
                f"Internal compiler error: unsupported {field_kind} field value in "
                f"{owner_label}: {type(field.value).__name__}"
            ),
            path=unit.prompt_file.source_path,
            source_span=field.source_span,
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
        if purpose_item is None:
            raise compile_error(
                code="E220",
                summary="Skill is missing string purpose",
                detail=f"Skill `{skill_decl.name}` is missing a string `purpose` field.",
                path=target_unit.prompt_file.source_path,
                source_span=skill_decl.source_span,
            )
        if not isinstance(purpose_item.value, str):
            raise compile_error(
                code="E220",
                summary="Skill is missing string purpose",
                detail=f"Skill `{skill_decl.name}` is missing a string `purpose` field.",
                path=target_unit.prompt_file.source_path,
                source_span=purpose_item.source_span or skill_decl.source_span,
            )

        metadata_scalars, _metadata_sections, metadata_extras = self._split_record_items(
            entry.items,
            scalar_keys={"requirement", "reason"},
            owner_label=f"skill reference {skill_decl.name}",
        )

        body: list[CompiledBodyItem] = []
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
            body.append("_Required skill_")
        body.append(
            CompiledSection(
                title="Purpose",
                body=(
                    self._interpolate_authored_prose_string(
                        purpose_item.value,
                        unit=target_unit,
                        owner_label=f"skill {skill_decl.name}",
                        surface_label="skill purpose",
                    ),
                ),
                semantic_target="skill.field",
            )
        )

        for extra in extras:
            body.extend(
                self._compile_skill_field_item(
                    extra,
                    unit=target_unit,
                    owner_label=f"skill {skill_decl.name}",
                    surface_label="skill prose",
                )
            )

        reason = metadata_scalars.get("reason")
        if reason is not None:
            if not isinstance(reason.value, str):
                raise compile_error(
                    code="E299",
                    summary="Compile failure",
                    detail=f"Skill reference reason must be a string in {skill_decl.name}",
                    path=entry.metadata_unit.prompt_file.source_path,
                    source_span=reason.source_span,
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
                    semantic_target="skill.field",
                )
            )

        for extra in metadata_extras:
            body.extend(
                self._compile_skill_field_item(
                    extra,
                    unit=entry.metadata_unit,
                    owner_label=f"skill reference {skill_decl.name}",
                    surface_label="skill reference prose",
                )
            )

        return CompiledSection(title=skill_decl.title, body=tuple(body))

    def _compile_skill_field_item(
        self,
        item: model.AnyRecordItem,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        if isinstance(item, model.RecordSection):
            return (
                CompiledSection(
                    title=item.title,
                    body=self._compile_record_support_items(
                        item.items,
                        unit=unit,
                        owner_label=f"{owner_label}.{item.key}",
                        surface_label=surface_label,
                    ),
                    semantic_target="skill.field",
                ),
            )

        if isinstance(item, model.RecordScalar):
            value = self._format_scalar_value(
                item.value,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
            )
            body: list[CompiledBodyItem] = [value]
            if item.body is not None:
                body.extend(
                    self._compile_record_support_items(
                        item.body,
                        unit=unit,
                        owner_label=f"{owner_label}.{item.key}",
                        surface_label=surface_label,
                    )
                )
            return (
                CompiledSection(
                    title=_humanize_key(item.key),
                    body=tuple(body),
                    semantic_target="skill.field",
                ),
            )

        return self._compile_record_item(
            item,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
        )
