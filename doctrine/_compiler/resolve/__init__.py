from __future__ import annotations

from dataclasses import replace

from doctrine._compiler.constants import (
    _ADDRESSABLE_ROOT_REGISTRIES,
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
from doctrine._compiler.resolve.outputs import ResolveOutputsMixin
from doctrine._compiler.resolve.refs import ResolveRefsMixin
from doctrine._compiler.resolve.reviews import ResolveReviewsMixin
from doctrine._compiler.resolve.schemas import ResolveSchemasMixin
from doctrine._compiler.resolve.workflows import ResolveWorkflowsMixin
from doctrine._compiler.naming import (
    _display_addressable_ref,
    _dotted_ref_name,
    _humanize_key,
    _law_path_from_name_ref,
    _lowercase_initial,
    _name_ref_from_dotted_name,
)
from doctrine._compiler.resolved_types import *  # noqa: F401,F403
from doctrine._compiler.support_files import _default_worker_count, _dotted_decl_name


class ResolveMixin(
    ResolveSchemasMixin,
    ResolveWorkflowsMixin,
    ResolveReviewsMixin,
    ResolveOutputsMixin,
    ResolveRefsMixin,
):
    """Resolution helper owner for CompilationContext."""

    def _resolve_route_semantic_ref_value(
        self,
        ref: model.AddressableRef,
        *,
        owner_label: str,
        surface_label: str,
        route_semantics: RouteSemanticContext | None,
    ) -> DisplayValue | None:
        parts = self._route_semantic_parts(ref)
        if route_semantics is None or parts is None:
            return None
        ref_label = _display_addressable_ref(ref)
        if parts == ("route",):
            return DisplayValue(text="Route", kind="title")
        if parts == ("route", "exists"):
            if route_semantics.route_required:
                return DisplayValue(text="true", kind="symbol")
            if route_semantics.branches and not route_semantics.has_unrouted_branch:
                return DisplayValue(text="true", kind="symbol")
            if not route_semantics.branches:
                return DisplayValue(text="false", kind="symbol")
            raise CompileError(
                f"route.exists is branch-dependent in {surface_label} {owner_label}: {ref_label}"
            )

        branches = self._route_semantic_branches_for_read(
            route_semantics,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
        )
        if parts[1] == "next_owner":
            unique_targets = {
                (branch.target_module_parts, branch.target_name)
                for branch in branches
            }
            if len(unique_targets) == 1:
                branch = branches[0]
                if len(parts) == 2:
                    return DisplayValue(
                        text=self._route_semantic_branch_title(branch),
                        kind="title",
                    )
                if len(parts) == 3 and parts[2] in {"name", "key"}:
                    return DisplayValue(text=branch.target_name, kind="symbol")
                if len(parts) == 3 and parts[2] == "title":
                    return DisplayValue(text=self._route_semantic_branch_title(branch), kind="title")
            if self._route_choice_branches_are_live(branches):
                if len(parts) == 2 or (len(parts) == 3 and parts[2] == "title"):
                    return DisplayValue(text="the selected route's next owner", kind="title")
                if len(parts) == 3 and parts[2] in {"name", "key"}:
                    return DisplayValue(text="the selected route's next owner key", kind="symbol")
            raise CompileError(
                f"Ambiguous route.next_owner in {surface_label} {owner_label}: {ref_label}"
            )
        if parts[1] == "choice":
            member = self._unique_route_choice_member(
                branches,
                owner_label=owner_label,
                surface_label=surface_label,
                ref_label=ref_label,
                detail_label="route.choice",
            )
            if len(parts) == 2:
                return DisplayValue(text=member.member_title, kind="title")
            if len(parts) == 3 and parts[2] == "key":
                return DisplayValue(text=member.member_key, kind="symbol")
            if len(parts) == 3 and parts[2] == "title":
                return DisplayValue(text=member.member_title, kind="title")
            if len(parts) == 3 and parts[2] == "wire":
                return DisplayValue(text=member.member_wire, kind="symbol")
        if parts == ("route", "label"):
            branch = self._unique_route_semantic_branch(
                branches,
                key_fn=lambda item: item.label,
                owner_label=owner_label,
                surface_label=surface_label,
                ref_label=ref_label,
                detail_label="route.label",
            )
            return DisplayValue(text=branch.label, kind="title")
        if parts == ("route", "summary"):
            branch = self._unique_route_semantic_branch(
                branches,
                key_fn=lambda item: self._route_semantic_branch_summary(item),
                owner_label=owner_label,
                surface_label=surface_label,
                ref_label=ref_label,
                detail_label="route.summary",
            )
            return DisplayValue(
                text=self._route_semantic_branch_summary(branch),
                kind="title",
            )
        raise CompileError(
            f"Unknown route semantic path on {surface_label} in {owner_label}: {ref_label}"
        )

    def _resolve_agent_contract(self, agent: model.Agent, *, unit: IndexedUnit) -> AgentContract:
        inputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]] = {}
        input_bindings_by_path: dict[tuple[str, ...], ContractBinding] = {}
        outputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]] = {}
        output_bindings_by_path: dict[tuple[str, ...], ContractBinding] = {}

        for field in agent.fields:
            if isinstance(field, model.InputsField):
                summary = self._summarize_contract_field(
                    field,
                    unit=unit,
                    field_kind="inputs",
                    owner_label=f"agent {agent.name}",
                )
                self._merge_contract_summary(
                    summary,
                    decls_sink=inputs,
                    bindings_sink=input_bindings_by_path,
                )
            elif isinstance(field, model.OutputsField):
                summary = self._summarize_contract_field(
                    field,
                    unit=unit,
                    field_kind="outputs",
                    owner_label=f"agent {agent.name}",
                )
                self._merge_contract_summary(
                    summary,
                    decls_sink=outputs,
                    bindings_sink=output_bindings_by_path,
                )

        return AgentContract(
            inputs=inputs,
            input_bindings_by_path=input_bindings_by_path,
            outputs=outputs,
            output_bindings_by_path=output_bindings_by_path,
        )

    def _resolve_contract_artifact_ref(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> ContractArtifact:
        if item.body is not None:
            raise CompileError(
                f"Declaration refs cannot define inline bodies in {owner_label}: "
                f"{_dotted_ref_name(item.ref)}"
            )
        if field_kind == "inputs":
            if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="outputs_by_name"):
                raise CompileError(
                    "Inputs refs must resolve to input declarations, not output declarations: "
                    f"{_dotted_ref_name(item.ref)}"
                )
            target_unit, decl = self._resolve_input_decl(item.ref, unit=unit)
            return ContractArtifact(kind="input", unit=target_unit, decl=decl)

        if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="inputs_by_name"):
            raise CompileError(
                "Outputs refs must resolve to output declarations, not input declarations: "
                f"{_dotted_ref_name(item.ref)}"
            )
        target_unit, decl = self._resolve_output_decl(item.ref, unit=unit)
        return ContractArtifact(kind="output", unit=target_unit, decl=decl)

    def _resolve_agent_slots(
        self, agent: model.Agent, *, unit: IndexedUnit
    ) -> tuple[ResolvedAgentSlotState, ...]:
        agent_key = (unit.module_parts, agent.name)
        cached = self._resolved_agent_slot_cache.get(agent_key)
        if cached is not None:
            return cached

        if agent_key in self._agent_slot_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._agent_slot_resolution_stack, agent_key]
            )
            raise CompileError(f"Cyclic agent inheritance: {cycle}")

        self._agent_slot_resolution_stack.append(agent_key)
        try:
            parent_slots: tuple[ResolvedAgentSlotState, ...] = ()
            parent_label: str | None = None
            if agent.parent_ref is not None:
                parent_unit, parent_agent = self._resolve_parent_agent_decl(agent, unit=unit)
                parent_slots = self._resolve_agent_slots(parent_agent, unit=parent_unit)
                parent_label = f"agent {_dotted_decl_name(parent_unit.module_parts, parent_agent.name)}"

            parent_slots_by_key = {slot.key: slot for slot in parent_slots}
            resolved_slots: list[ResolvedAgentSlotState] = []
            seen_slot_keys: set[str] = set()
            accounted_parent_concrete_keys: set[str] = set()

            for field in agent.fields:
                if isinstance(field, model.AuthoredSlotField):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)

                    parent_slot = parent_slots_by_key.get(field.key)
                    if isinstance(parent_slot, ResolvedAgentSlot):
                        if field.key == "workflow" and isinstance(field.value, model.WorkflowBody):
                            resolved_body = self._resolve_workflow_body(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot workflow",
                                parent_workflow=parent_slot.body,
                                parent_label=f"{parent_label} slot workflow",
                            )
                            accounted_parent_concrete_keys.add(field.key)
                            resolved_slots.append(
                                ResolvedAgentSlot(key=field.key, body=resolved_body)
                            )
                            continue
                        raise CompileError(
                            f"Inherited authored slot requires `inherit {field.key}` or `override {field.key}` in agent {agent.name}"
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        resolved_slots.append(
                            ResolvedAgentSlot(
                                key=field.key,
                                body=self._resolve_slot_value(
                                    field.value,
                                    unit=unit,
                                    owner_label=f"agent {agent.name} slot {field.key}",
                                ),
                            )
                        )
                        continue

                    resolved_slots.append(
                        ResolvedAgentSlot(
                            key=field.key,
                            body=self._resolve_slot_value(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot {field.key}",
                            ),
                        )
                    )
                    continue

                if isinstance(field, model.AuthoredSlotAbstract):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)
                    parent_slot = parent_slots_by_key.get(field.key)
                    if isinstance(parent_slot, ResolvedAgentSlot):
                        accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(ResolvedAbstractAgentSlot(key=field.key))
                    continue

                if isinstance(field, model.AuthoredSlotInherit):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)
                    parent_slot = parent_slots_by_key.get(field.key)
                    if parent_slot is None:
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"Cannot inherit undefined authored slot in {label}: {field.key}"
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"E210 Abstract authored slot in {label} must be defined directly in agent {agent.name}: {field.key}"
                        )
                    accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(parent_slot)
                    continue

                if isinstance(field, model.AuthoredSlotOverride):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)
                    parent_slot = parent_slots_by_key.get(field.key)
                    if parent_slot is None:
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"E001 Cannot override undefined authored slot in {label}: {field.key}"
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"E210 Abstract authored slot in {label} must be defined directly in agent {agent.name}: {field.key}"
                        )
                    accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(
                        ResolvedAgentSlot(
                            key=field.key,
                            body=self._resolve_slot_value(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot {field.key}",
                            ),
                        )
                    )

            missing_parent_keys = [
                parent_slot.key
                for parent_slot in parent_slots
                if isinstance(parent_slot, ResolvedAgentSlot)
                and parent_slot.key not in accounted_parent_concrete_keys
            ]
            if missing_parent_keys:
                missing = ", ".join(missing_parent_keys)
                raise CompileError(
                    f"E003 Missing inherited authored slot in agent {agent.name}: {missing}"
                )

            for parent_slot in parent_slots:
                if (
                    isinstance(parent_slot, ResolvedAbstractAgentSlot)
                    and parent_slot.key not in seen_slot_keys
                ):
                    resolved_slots.append(parent_slot)

            resolved = tuple(resolved_slots)
            self._resolved_agent_slot_cache[agent_key] = resolved
            return resolved
        finally:
            self._agent_slot_resolution_stack.pop()

    def _resolve_slot_value(
        self,
        value: model.WorkflowSlotValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedWorkflowBody:
        if isinstance(value, model.WorkflowBody):
            return self._resolve_workflow_body(
                value,
                unit=unit,
                owner_label=owner_label,
            )
        try:
            target_unit, workflow_decl = self._resolve_workflow_ref(value, unit=unit)
        except CompileError as workflow_error:
            route_only = self._try_resolve_route_only_ref(value, unit=unit)
            if route_only is not None:
                route_unit, route_decl = route_only
                return self._resolve_route_only_decl_as_workflow(
                    route_decl,
                    unit=route_unit,
                    owner_label=owner_label,
                )
            grounding = self._try_resolve_grounding_ref(value, unit=unit)
            if grounding is not None:
                grounding_unit, grounding_decl = grounding
                return self._resolve_grounding_decl_as_workflow(
                    grounding_decl,
                    unit=grounding_unit,
                    owner_label=owner_label,
                )
            raise workflow_error
        return self._resolve_workflow_decl(workflow_decl, unit=target_unit)

    def _resolve_route_only_decl_as_workflow(
        self,
        decl: model.RouteOnlyDecl,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedWorkflowBody:
        facts_ref = decl.body.facts_ref
        if facts_ref is None:
            raise CompileError(f"route_only is missing facts: {decl.name}")
        self._resolve_route_only_facts_decl(
            facts_ref,
            unit=unit,
            owner_label=owner_label,
        )
        if not decl.body.current_none:
            raise CompileError(f"route_only must declare `current none`: {decl.name}")
        if decl.body.handoff_output_ref is None:
            raise CompileError(f"route_only is missing handoff_output: {decl.name}")
        output_unit, output_decl = self._resolve_output_decl(
            decl.body.handoff_output_ref,
            unit=unit,
        )
        self._validate_route_only_guarded_output(
            output_decl,
            facts_ref=facts_ref,
            guarded=decl.body.guarded,
            owner_label=owner_label,
        )
        if not decl.body.routes:
            raise CompileError(f"route_only must declare at least one route: {decl.name}")

        law_items: list[model.LawStmt] = []
        active_expr = self._combine_exprs_with_and(
            tuple(self._prefix_route_only_expr(expr, facts_ref) for expr in decl.body.when_exprs)
        )
        if active_expr is not None:
            law_items.append(model.ActiveWhenStmt(expr=active_expr))
        law_items.append(model.CurrentNoneStmt())
        law_items.append(model.StopStmt(message="No specialist artifact is current for this turn."))

        next_owner_expr = model.ExprRef(
            parts=(*facts_ref.module_parts, facts_ref.declaration_name, "next_owner")
        )
        route_cases: list[model.MatchArm] = []
        for route in decl.body.routes:
            self._validate_route_target(route.target, unit=unit)
            _route_unit, route_agent = self._resolve_agent_ref(route.target, unit=unit)
            route_title = route_agent.title or _humanize_key(route_agent.name)
            route_stmt = model.LawRouteStmt(
                label=f"Route to {route_title}.",
                target=route.target,
            )
            route_cases.append(
                model.MatchArm(
                    head=route.key,
                    items=(route_stmt,),
                    display_label=route_title if route.key is not None else None,
                )
            )
        law_items.append(model.MatchStmt(expr=next_owner_expr, cases=tuple(route_cases)))

        preamble: list[model.ProseLine] = [f"Emit {output_decl.title}."]
        return ResolvedWorkflowBody(
            title=decl.body.title,
            preamble=tuple(preamble),
            items=(),
            law=model.LawBody(items=tuple(law_items)),
        )

    def _resolve_grounding_decl_as_workflow(
        self,
        decl: model.GroundingDecl,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedWorkflowBody:
        if decl.body.target is None:
            raise CompileError(f"grounding is missing target: {decl.name}")

        preamble: list[model.ProseLine] = []
        if decl.body.source_ref is not None:
            preamble.append(
                f"Ground this pass against {self._display_ref(decl.body.source_ref, unit=unit)}."
            )
        preamble.append(f"Target: {decl.body.target}.")

        for item in decl.body.policy_items:
            if isinstance(item, model.GroundingPolicyStartFrom):
                if item.unless is None:
                    preamble.append(f"Start from {item.source}.")
                else:
                    preamble.append(f"Start from {item.source} unless {item.unless}.")
                continue
            if isinstance(item, model.GroundingPolicyForbid):
                preamble.append(f"Do not use {item.value}.")
                continue
            if isinstance(item, model.GroundingPolicyAllow):
                preamble.append(f"Allow {item.value}.")
                continue
            self._validate_route_target(item.target, unit=unit)
            preamble.append(
                f"If {item.condition}, route to {self._display_ref(item.target, unit=unit)}."
            )

        return ResolvedWorkflowBody(
            title=decl.body.title,
            preamble=tuple(preamble),
            items=(),
            law=None,
        )

    def _resolve_route_only_facts_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[IndexedUnit, model.InputDecl | model.OutputDecl]:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        input_decl = target_unit.inputs_by_name.get(ref.declaration_name)
        output_decl = target_unit.outputs_by_name.get(ref.declaration_name)
        if input_decl is not None and output_decl is not None:
            raise CompileError(
                f"Ambiguous route_only facts in {owner_label}: {_dotted_ref_name(ref)}"
            )
        if input_decl is None and output_decl is None:
            raise CompileError(
                f"route_only facts must resolve to an input or output declaration in {owner_label}: "
                f"{_dotted_ref_name(ref)}"
            )
        return target_unit, input_decl if input_decl is not None else output_decl

    def _resolve_contract_bucket_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
        path_prefix: tuple[str, ...] = (),
    ) -> ResolvedContractBucket:
        body: list[CompiledBodyItem] = []
        artifacts: list[ContractArtifact] = []
        bindings: list[ContractBinding] = []
        direct_artifacts: list[ContractArtifact] = []
        has_keyed_children = False

        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(
                    self._interpolate_authored_prose_line(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=f"{field_kind} prose",
                )
                )
                continue

            if isinstance(item, model.RecordSection):
                resolved_section = self._resolve_io_section_item(
                    item,
                    unit=unit,
                    field_kind=field_kind,
                    binding_path=(*path_prefix, item.key),
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=excluded_output_keys,
                )
                if resolved_section is None:
                    continue
                has_keyed_children = True
                body.append(resolved_section.section)
                artifacts.extend(resolved_section.artifacts)
                bindings.extend(resolved_section.bindings)
                continue

            if isinstance(item, model.RecordRef):
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
                    continue
                compiled_section, artifact = resolved_ref
                body.append(compiled_section)
                artifacts.append(artifact)
                direct_artifacts.append(artifact)
                continue

            if isinstance(item, model.RecordScalar):
                raise CompileError(
                    f"Scalar keyed items are not allowed in {owner_label}: {item.key}"
                )

            raise CompileError(
                f"Unsupported {field_kind} bucket item in {owner_label}: {type(item).__name__}"
            )

        return ResolvedContractBucket(
            body=tuple(body),
            artifacts=tuple(artifacts),
            bindings=tuple(bindings),
            direct_artifacts=tuple(direct_artifacts),
            has_keyed_children=has_keyed_children,
        )

    def _resolve_contract_bucket_ref_entry(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> tuple[CompiledSection, ContractArtifact] | None:
        if item.body is not None:
            raise CompileError(
                f"Declaration refs cannot define inline bodies in {owner_label}: "
                f"{_dotted_ref_name(item.ref)}"
            )

        if field_kind == "inputs":
            if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="outputs_by_name"):
                raise CompileError(
                    "Inputs refs must resolve to input declarations, not output declarations: "
                    f"{_dotted_ref_name(item.ref)}"
                )
            target_unit, decl = self._resolve_input_decl(item.ref, unit=unit)
            return (
                self._compile_input_decl(decl, unit=target_unit),
                ContractArtifact(kind="input", unit=target_unit, decl=decl),
            )

        if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="inputs_by_name"):
            raise CompileError(
                "Outputs refs must resolve to output declarations, not input declarations: "
                f"{_dotted_ref_name(item.ref)}"
            )
        target_unit, decl = self._resolve_output_decl(item.ref, unit=unit)
        output_key = (target_unit.module_parts, decl.name)
        if output_key in excluded_output_keys:
            return None
        review_semantics = self._review_output_context_for_key(
            review_output_contexts,
            output_key,
        )
        route_semantics = self._route_output_context_for_key(
            route_output_contexts,
            output_key,
        )
        return (
            self._compile_output_decl(
                decl,
                unit=target_unit,
                allow_review_semantics=review_semantics is not None,
                allow_route_semantics=route_semantics is not None,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            ),
            ContractArtifact(kind="output", unit=target_unit, decl=decl),
        )

    def _resolve_skills_decl(
        self, skills_decl: model.SkillsDecl, *, unit: IndexedUnit
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        cached = self._resolved_skills_cache.get(skills_key)
        if cached is not None:
            return cached

        if skills_key in self._skills_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._skills_resolution_stack, skills_key]
            )
            raise CompileError(f"Cyclic skills inheritance: {cycle}")

        self._skills_resolution_stack.append(skills_key)
        try:
            parent_skills: ResolvedSkillsBody | None = None
            parent_label: str | None = None
            if skills_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_skills_decl(
                    skills_decl,
                    unit=unit,
                )
                parent_skills = self._resolve_skills_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"skills {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_skills_body(
                skills_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, skills_decl.name),
                parent_skills=parent_skills,
                parent_label=parent_label,
            )
            self._resolved_skills_cache[skills_key] = resolved
            return resolved
        finally:
            self._skills_resolution_stack.pop()

    def _resolve_skills_for_addressable_paths(
        self,
        skills_decl: model.SkillsDecl,
        *,
        unit: IndexedUnit,
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        if (
            skills_key in self._skills_resolution_stack
            or skills_key in self._skills_addressable_resolution_stack
        ):
            return self._resolve_skills_addressable_decl(skills_decl, unit=unit)
        return self._resolve_skills_decl(skills_decl, unit=unit)

    def _resolve_skills_addressable_decl(
        self, skills_decl: model.SkillsDecl, *, unit: IndexedUnit
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        cached = self._addressable_skills_cache.get(skills_key)
        if cached is not None:
            return cached

        if skills_key in self._skills_addressable_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [
                    *self._skills_addressable_resolution_stack,
                    skills_key,
                ]
            )
            raise CompileError(f"Cyclic skills inheritance: {cycle}")

        self._skills_addressable_resolution_stack.append(skills_key)
        try:
            parent_skills: ResolvedSkillsBody | None = None
            parent_label: str | None = None
            if skills_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_skills_decl(
                    skills_decl,
                    unit=unit,
                )
                parent_skills = self._resolve_skills_for_addressable_paths(
                    parent_decl,
                    unit=parent_unit,
                )
                parent_label = (
                    f"skills {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_skills_addressable_body(
                skills_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, skills_decl.name),
                parent_skills=parent_skills,
                parent_label=parent_label,
            )
            self._addressable_skills_cache[skills_key] = resolved
            return resolved
        finally:
            self._skills_addressable_resolution_stack.pop()

    def _resolve_analysis_decl(
        self, analysis_decl: model.AnalysisDecl, *, unit: IndexedUnit
    ) -> ResolvedAnalysisBody:
        analysis_key = (unit.module_parts, analysis_decl.name)
        cached = self._resolved_analysis_cache.get(analysis_key)
        if cached is not None:
            return cached

        if analysis_key in self._analysis_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._analysis_resolution_stack, analysis_key]
            )
            raise CompileError(f"Cyclic analysis inheritance: {cycle}")

        self._analysis_resolution_stack.append(analysis_key)
        try:
            parent_analysis: ResolvedAnalysisBody | None = None
            parent_label: str | None = None
            if analysis_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_analysis_decl(
                    analysis_decl,
                    unit=unit,
                )
                parent_analysis = self._resolve_analysis_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"analysis {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_analysis_body(
                analysis_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, analysis_decl.name),
                parent_analysis=parent_analysis,
                parent_label=parent_label,
            )
            resolved = replace(
                resolved,
                render_profile=(
                    self._resolve_render_profile_ref(analysis_decl.render_profile_ref, unit=unit)
                    if analysis_decl.render_profile_ref is not None
                    else parent_analysis.render_profile if parent_analysis is not None else None
                ),
            )
            self._resolved_analysis_cache[analysis_key] = resolved
            return resolved
        finally:
            self._analysis_resolution_stack.pop()

    def _resolve_document_decl(
        self, document_decl: model.DocumentDecl, *, unit: IndexedUnit
    ) -> ResolvedDocumentBody:
        document_key = (unit.module_parts, document_decl.name)
        cached = self._resolved_document_cache.get(document_key)
        if cached is not None:
            return cached

        if document_key in self._document_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._document_resolution_stack, document_key]
            )
            raise CompileError(f"Cyclic document inheritance: {cycle}")

        self._document_resolution_stack.append(document_key)
        try:
            parent_document: ResolvedDocumentBody | None = None
            parent_label: str | None = None
            if document_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_document_decl(
                    document_decl,
                    unit=unit,
                )
                parent_document = self._resolve_document_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"document {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_document_body(
                document_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, document_decl.name),
                parent_document=parent_document,
                parent_label=parent_label,
            )
            resolved = replace(
                resolved,
                render_profile=(
                    self._resolve_render_profile_ref(document_decl.render_profile_ref, unit=unit)
                    if document_decl.render_profile_ref is not None
                    else parent_document.render_profile if parent_document is not None else None
                ),
            )
            self._resolved_document_cache[document_key] = resolved
            return resolved
        finally:
            self._document_resolution_stack.pop()

    def _resolve_inputs_decl(
        self, inputs_decl: model.InputsDecl, *, unit: IndexedUnit
    ) -> ResolvedIoBody:
        inputs_key = (unit.module_parts, inputs_decl.name)
        cached = self._resolved_inputs_cache.get(inputs_key)
        if cached is not None:
            return cached

        if inputs_key in self._inputs_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._inputs_resolution_stack, inputs_key]
            )
            raise CompileError(f"Cyclic inputs inheritance: {cycle}")

        self._inputs_resolution_stack.append(inputs_key)
        try:
            parent_io: ResolvedIoBody | None = None
            parent_label: str | None = None
            if inputs_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_inputs_decl(
                    inputs_decl,
                    unit=unit,
                )
                parent_io = self._resolve_inputs_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"inputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_io_body(
                inputs_decl.body,
                unit=unit,
                field_kind="inputs",
                owner_label=_dotted_decl_name(unit.module_parts, inputs_decl.name),
                parent_io=parent_io,
                parent_label=parent_label,
            )
            self._resolved_inputs_cache[inputs_key] = resolved
            return resolved
        finally:
            self._inputs_resolution_stack.pop()

    def _resolve_skills_value(
        self,
        value: model.SkillsValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSkillsBody:
        if isinstance(value, model.NameRef):
            target_unit, skills_decl = self._resolve_skills_ref(value, unit=unit)
            return self._resolve_skills_decl(skills_decl, unit=target_unit)
        return self._resolve_skills_body(
            value,
            unit=unit,
            owner_label=owner_label,
        )

    def _resolve_skills_value_for_addressable_paths(
        self,
        value: model.SkillsValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSkillsBody:
        if isinstance(value, model.NameRef):
            target_unit, skills_decl = self._resolve_skills_ref(value, unit=unit)
            return self._resolve_skills_for_addressable_paths(skills_decl, unit=target_unit)
        return self._resolve_skills_addressable_body(
            value,
            unit=unit,
            owner_label=owner_label,
        )

    def _resolve_skills_body(
        self,
        skills_body: model.SkillsBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_skills: ResolvedSkillsBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedSkillsBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="skills prose",
                ambiguous_label="skills prose interpolation ref",
            )
            for line in skills_body.preamble
        )
        if parent_skills is None:
            return ResolvedSkillsBody(
                title=skills_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_skills_items(
                    skills_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_skills.items}
        resolved_items: list[ResolvedSkillsItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in skills_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(
                    self._resolve_skill_entry(
                        item,
                        unit=unit,
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined skills entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined skills entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSkillsSection):
                if not isinstance(parent_item, ResolvedSkillsSection):
                    raise CompileError(
                        f"Override kind mismatch for skills entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedSkillEntry):
                raise CompileError(
                    f"Override kind mismatch for skills entry in {owner_label}: {key}"
                )
            resolved_items.append(
                self._resolve_skill_entry(
                    item,
                    unit=unit,
                )
            )

        missing_keys = [
            parent_item.key
            for parent_item in parent_skills.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited skills entry in {owner_label}: {missing}"
            )

        return ResolvedSkillsBody(
            title=skills_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
        )

    def _resolve_analysis_body(
        self,
        analysis_body: model.AnalysisBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_analysis: ResolvedAnalysisBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedAnalysisBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="analysis prose",
                ambiguous_label="analysis prose interpolation ref",
            )
            for line in analysis_body.preamble
        )
        if parent_analysis is None:
            resolved_items = self._resolve_non_inherited_analysis_items(
                analysis_body.items,
                unit=unit,
                owner_label=owner_label,
            )
            return ResolvedAnalysisBody(
                title=analysis_body.title,
                preamble=resolved_preamble,
                items=resolved_items,
            )

        parent_items_by_key = {item.key: item for item in parent_analysis.items}
        resolved_items: list[ResolvedAnalysisSection] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in analysis_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate analysis section key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.AnalysisSection):
                if key in parent_items_by_key:
                    raise CompileError(
                        f"Inherited analysis requires `override {key}` in {owner_label}"
                    )
                resolved_items.append(
                    ResolvedAnalysisSection(
                        unit=unit,
                        key=key,
                        title=item.title,
                        items=self._resolve_analysis_section_items(
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
                        f"Cannot inherit undefined analysis entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined analysis entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            resolved_items.append(
                ResolvedAnalysisSection(
                    unit=unit,
                    key=key,
                    title=item.title if item.title is not None else parent_item.title,
                    items=self._resolve_analysis_section_items(
                        item.items,
                        unit=unit,
                        owner_label=f"{owner_label}.{key}",
                    ),
                )
            )

        missing_keys = [
            parent_item.key for parent_item in parent_analysis.items if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited analysis entry in {owner_label}: {missing}"
            )

        return ResolvedAnalysisBody(
            title=analysis_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
        )

    def _resolve_non_inherited_analysis_items(
        self,
        items: tuple[model.AnalysisItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedAnalysisSection, ...]:
        resolved_items: list[ResolvedAnalysisSection] = []
        seen_keys: set[str] = set()
        for item in items:
            if isinstance(item, model.AnalysisSection):
                if item.key in seen_keys:
                    raise CompileError(f"Duplicate analysis section key in {owner_label}: {item.key}")
                seen_keys.add(item.key)
                resolved_items.append(
                    ResolvedAnalysisSection(
                        unit=unit,
                        key=item.key,
                        title=item.title,
                        items=self._resolve_analysis_section_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                        ),
                    )
                )
                continue
            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited analysis declaration in {owner_label}: {item.key}"
            )
        return tuple(resolved_items)

    def _resolve_analysis_section_items(
        self,
        items: tuple[model.AnalysisSectionItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedAnalysisSectionItem, ...]:
        resolved: list[ResolvedAnalysisSectionItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                resolved.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="analysis prose",
                        ambiguous_label="analysis prose interpolation ref",
                    )
                )
                continue
            if isinstance(item, model.SectionBodyRef):
                display = self._resolve_addressable_ref_value(
                    item.ref,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label="analysis refs",
                    ambiguous_label="analysis ref",
                    missing_local_label="analysis",
                )
                resolved.append(ResolvedSectionRef(label=display.text))
                continue
            if isinstance(item, (model.ProveStmt, model.DeriveStmt, model.CompareStmt, model.DefendStmt)):
                basis = self._coerce_path_set(item.basis)
                if not basis.paths:
                    raise CompileError(f"Analysis basis may not be empty in {owner_label}")
                self._validate_path_set_roots(
                    basis,
                    unit=unit,
                    agent_contract=None,
                    owner_label=owner_label,
                    statement_label="analysis basis",
                    allowed_kinds=("input", "output", "enum"),
                )
                resolved.append(replace(item, basis=basis))
                continue
            if isinstance(item, model.ClassifyStmt):
                self._resolve_enum_ref(item.enum_ref, unit=unit)
                resolved.append(item)
                continue
            raise CompileError(
                f"Unsupported analysis item in {owner_label}: {type(item).__name__}"
            )
        return tuple(resolved)

    def _resolve_document_body(
        self,
        document_body: model.DocumentBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_document: ResolvedDocumentBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedDocumentBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="document prose",
                ambiguous_label="document prose interpolation ref",
            )
            for line in document_body.preamble
        )
        if parent_document is None:
            return ResolvedDocumentBody(
                title=document_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_document_items(
                    document_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_document.items}
        resolved_items: list[model.DocumentBlock] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in document_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate document block key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.DocumentBlock):
                if key in parent_items_by_key:
                    raise CompileError(
                        f"Inherited document requires `override {key}` in {owner_label}"
                    )
                resolved_items.append(
                    self._resolve_document_block(
                        item,
                        unit=unit,
                        owner_label=f"{owner_label}.{key}",
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined document entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined document entry in {parent_label}: {key}"
                )
            if item.kind != parent_item.kind:
                raise CompileError(
                    f"Override kind mismatch for document entry in {owner_label}: {key}"
                )
            accounted_keys.add(key)
            resolved_items.append(
                self._resolve_document_block(
                    model.DocumentBlock(
                        kind=item.kind,
                        key=item.key,
                        title=item.title if item.title is not None else parent_item.title,
                        payload=item.payload,
                        requirement=(
                            item.requirement
                            if item.requirement is not None
                            else parent_item.requirement
                        ),
                        when_expr=item.when_expr if item.when_expr is not None else parent_item.when_expr,
                        item_schema=(
                            item.item_schema
                            if item.item_schema is not None
                            else parent_item.item_schema
                        ),
                        row_schema=(
                            item.row_schema if item.row_schema is not None else parent_item.row_schema
                        ),
                        anonymous=parent_item.anonymous,
                        legacy_section=parent_item.legacy_section,
                    ),
                    unit=unit,
                    owner_label=f"{owner_label}.{key}",
                )
            )

        missing_keys = [
            parent_item.key for parent_item in parent_document.items if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited document entry in {owner_label}: {missing}"
            )

        return ResolvedDocumentBody(
            title=document_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
        )

    def _resolve_non_inherited_document_items(
        self,
        items: tuple[model.DocumentItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.DocumentBlock, ...]:
        resolved: list[model.DocumentBlock] = []
        seen_keys: set[str] = set()
        for item in items:
            if isinstance(item, model.DocumentBlock):
                if item.key in seen_keys:
                    raise CompileError(f"Duplicate document block key in {owner_label}: {item.key}")
                seen_keys.add(item.key)
                resolved.append(
                    self._resolve_document_block(
                        item,
                        unit=unit,
                        owner_label=f"{owner_label}.{item.key}",
                    )
                )
                continue
            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited document declaration in {owner_label}: {item.key}"
            )
        return tuple(resolved)

    def _resolve_document_block(
        self,
        item: model.DocumentBlock,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> model.DocumentBlock:
        if item.when_expr is not None:
            self._validate_readable_guard_expr(
                item.when_expr,
                unit=unit,
                owner_label=owner_label,
            )
        item_schema = self._resolve_readable_inline_schema(
            item.item_schema,
            unit=unit,
            owner_label=owner_label,
            schema_label="item_schema",
            surface_label=f"{item.kind} item schema",
        )
        row_schema = self._resolve_readable_inline_schema(
            item.row_schema,
            unit=unit,
            owner_label=owner_label,
            schema_label="row_schema",
            surface_label=f"{item.kind} row schema",
        )
        if item.kind == "section":
            return replace(
                item,
                payload=self._resolve_document_shared_readable_body(
                    item.payload,
                    unit=unit,
                    owner_label=owner_label,
                    kind="section",
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind in {"sequence", "bullets", "checklist"}:
            resolved_items: list[model.ReadableListItem] = []
            seen_keys: set[str] = set()
            for list_item in self._require_tuple_payload(
                item.payload,
                owner_label=owner_label,
                kind=item.kind,
            ):
                if not isinstance(list_item, model.ReadableListItem):
                    raise CompileError(
                        f"Readable {item.kind} items must stay list entries in {owner_label}"
                    )
                if list_item.key is not None:
                    if list_item.key in seen_keys:
                        raise CompileError(
                            f"Duplicate {item.kind} item key in {owner_label}: {list_item.key}"
                        )
                    seen_keys.add(list_item.key)
                resolved_items.append(
                    replace(
                        list_item,
                        text=self._interpolate_authored_prose_line(
                            list_item.text,
                            unit=unit,
                            owner_label=owner_label,
                            surface_label=f"{item.kind} item prose",
                            ambiguous_label=f"{item.kind} item interpolation ref",
                        ),
                    )
                )
            return replace(
                item,
                payload=tuple(resolved_items),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "properties":
            return replace(
                item,
                payload=self._resolve_readable_properties_payload(
                    item.payload,
                    unit=unit,
                    owner_label=owner_label,
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "definitions":
            resolved_items: list[model.ReadableDefinitionItem] = []
            seen_keys: set[str] = set()
            for definition in self._require_tuple_payload(
                item.payload,
                owner_label=owner_label,
                kind="definitions",
            ):
                if not isinstance(definition, model.ReadableDefinitionItem):
                    raise CompileError(
                        f"Readable definitions entries must stay definition items in {owner_label}"
                    )
                if definition.key in seen_keys:
                    raise CompileError(
                        f"Duplicate definitions item key in {owner_label}: {definition.key}"
                    )
                seen_keys.add(definition.key)
                resolved_items.append(
                    replace(
                        definition,
                        body=tuple(
                            self._interpolate_authored_prose_line(
                                line,
                                unit=unit,
                                owner_label=f"{owner_label}.{definition.key}",
                                surface_label="definitions prose",
                                ambiguous_label="definitions prose interpolation ref",
                            )
                            for line in definition.body
                        ),
                    )
                )
            return replace(
                item,
                payload=tuple(resolved_items),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "table":
            resolved_table = self._resolve_document_readable_table_payload(
                item.payload,
                unit=unit,
                owner_label=owner_label,
            )
            return replace(
                item,
                payload=resolved_table,
                item_schema=item_schema,
                row_schema=resolved_table.row_schema,
            )
        if item.kind == "guard":
            return replace(
                item,
                payload=self._resolve_document_shared_readable_body(
                    item.payload,
                    unit=unit,
                    owner_label=owner_label,
                    kind="guard",
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "callout":
            if not isinstance(item.payload, model.ReadableCalloutData):
                raise CompileError(f"Readable callout payload must stay callout-shaped in {owner_label}")
            if item.payload.kind is not None and item.payload.kind not in {
                "required",
                "important",
                "warning",
                "note",
            }:
                raise CompileError(f"Unknown callout kind in {owner_label}: {item.payload.kind}")
            return replace(
                item,
                payload=model.ReadableCalloutData(
                    kind=item.payload.kind,
                    body=tuple(
                        self._interpolate_authored_prose_line(
                            line,
                            unit=unit,
                            owner_label=owner_label,
                            surface_label="callout prose",
                            ambiguous_label="callout interpolation ref",
                        )
                        for line in item.payload.body
                    ),
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "code":
            if not isinstance(item.payload, model.ReadableCodeData):
                raise CompileError(f"Readable code payload must stay code-shaped in {owner_label}")
            if "\n" not in item.payload.text:
                raise CompileError(f"Code block text must use a multiline string in {owner_label}")
            return replace(item, item_schema=item_schema, row_schema=row_schema)
        if item.kind in {"markdown", "html"}:
            if not isinstance(item.payload, model.ReadableRawTextData):
                raise CompileError(f"Readable {item.kind} payload must stay text-shaped in {owner_label}")
            text = self._interpolate_authored_prose_string(
                item.payload.text,
                unit=unit,
                owner_label=owner_label,
                surface_label=f"{item.kind} text",
                ambiguous_label=f"{item.kind} interpolation ref",
            )
            if "\n" not in text:
                raise CompileError(f"Raw {item.kind} blocks must use a multiline string in {owner_label}")
            return replace(
                item,
                payload=model.ReadableRawTextData(text=text),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "footnotes":
            return replace(
                item,
                payload=self._resolve_readable_footnotes_payload(
                    item.payload,
                    unit=unit,
                    owner_label=owner_label,
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "image":
            if not isinstance(item.payload, model.ReadableImageData):
                raise CompileError(f"Readable image payload must stay image-shaped in {owner_label}")
            return replace(
                item,
                payload=model.ReadableImageData(
                    src=self._interpolate_authored_prose_string(
                        item.payload.src,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="image src",
                        ambiguous_label="image src interpolation ref",
                    ),
                    alt=self._interpolate_authored_prose_string(
                        item.payload.alt,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="image alt",
                        ambiguous_label="image alt interpolation ref",
                    ),
                    caption=(
                        self._interpolate_authored_prose_string(
                            item.payload.caption,
                            unit=unit,
                            owner_label=owner_label,
                            surface_label="image caption",
                            ambiguous_label="image caption interpolation ref",
                        )
                        if item.payload.caption is not None
                        else None
                    ),
                ),
                item_schema=item_schema,
                row_schema=row_schema,
            )
        if item.kind == "rule":
            return replace(item, item_schema=item_schema, row_schema=row_schema)
        return replace(
            item,
            payload=self._require_tuple_payload(
                item.payload,
                owner_label=owner_label,
                kind=item.kind,
            ),
            item_schema=item_schema,
            row_schema=row_schema,
        )

    def _resolve_document_shared_readable_body(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        kind: str,
    ) -> tuple[model.ReadableSectionBodyItem, ...]:
        resolved: list[model.ReadableSectionBodyItem] = []
        for child in self._require_tuple_payload(payload, owner_label=owner_label, kind=kind):
            if isinstance(child, (str, model.EmphasizedLine)):
                resolved.append(
                    self._interpolate_authored_prose_line(
                        child,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="document prose",
                        ambiguous_label="document prose interpolation ref",
                    )
                )
                continue
            if not isinstance(child, model.ReadableBlock):
                raise CompileError(
                    f"Readable {kind} payload must stay block-shaped in {owner_label}"
                )
            resolved.append(
                self._resolve_document_block(
                    child,
                    unit=unit,
                    owner_label=f"{owner_label}.{child.key}",
                )
            )
        return tuple(resolved)

    def _resolve_readable_inline_schema(
        self,
        schema: model.ReadableInlineSchemaData | None,
        *,
        unit: IndexedUnit,
        owner_label: str,
        schema_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> model.ReadableInlineSchemaData | None:
        if schema is None:
            return None
        seen_keys: set[str] = set()
        entries: list[model.ReadableSchemaEntry] = []
        for entry in schema.entries:
            if entry.key in seen_keys:
                raise CompileError(f"Duplicate {schema_label} key in {owner_label}: {entry.key}")
            seen_keys.add(entry.key)
            entries.append(
                replace(
                    entry,
                    body=tuple(
                        self._interpolate_authored_prose_line(
                            line,
                            unit=unit,
                            owner_label=f"{owner_label}.{schema_label}.{entry.key}",
                            surface_label=surface_label,
                            ambiguous_label=f"{schema_label} interpolation ref",
                            review_semantics=review_semantics,
                            route_semantics=route_semantics,
                            render_profile=render_profile,
                        )
                        for line in entry.body
                    ),
                )
            )
        return model.ReadableInlineSchemaData(entries=tuple(entries))

    def _resolve_readable_properties_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> model.ReadablePropertiesData:
        if not isinstance(payload, model.ReadablePropertiesData):
            raise CompileError(f"Readable properties payload must stay properties-shaped in {owner_label}")
        seen_keys: set[str] = set()
        entries: list[model.ReadablePropertyItem] = []
        for entry in payload.entries:
            if entry.key in seen_keys:
                raise CompileError(f"Duplicate properties entry key in {owner_label}: {entry.key}")
            seen_keys.add(entry.key)
            entries.append(
                replace(
                    entry,
                    body=tuple(
                        self._interpolate_authored_prose_line(
                            line,
                            unit=unit,
                            owner_label=f"{owner_label}.{entry.key}",
                            surface_label="properties prose",
                            ambiguous_label="properties interpolation ref",
                            review_semantics=review_semantics,
                            route_semantics=route_semantics,
                            render_profile=render_profile,
                        )
                        for line in entry.body
                    ),
                )
            )
        return model.ReadablePropertiesData(entries=tuple(entries))

    def _resolve_readable_footnotes_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> model.ReadableFootnotesData:
        if not isinstance(payload, model.ReadableFootnotesData):
            raise CompileError(f"Readable footnotes payload must stay footnotes-shaped in {owner_label}")
        seen_keys: set[str] = set()
        entries: list[model.ReadableFootnoteItem] = []
        for entry in payload.entries:
            if entry.key in seen_keys:
                raise CompileError(f"Duplicate footnote key in {owner_label}: {entry.key}")
            seen_keys.add(entry.key)
            entries.append(
                model.ReadableFootnoteItem(
                    key=entry.key,
                    text=self._interpolate_authored_prose_line(
                        entry.text,
                        unit=unit,
                        owner_label=f"{owner_label}.{entry.key}",
                        surface_label="footnotes prose",
                        ambiguous_label="footnote interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=route_semantics,
                        render_profile=render_profile,
                    ),
                )
            )
        return model.ReadableFootnotesData(entries=tuple(entries))

    def _resolve_document_readable_table_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> model.ReadableTableData:
        if not isinstance(payload, model.ReadableTableData):
            raise CompileError(f"Readable table payload must stay table-shaped in {owner_label}")
        resolved_columns: list[model.ReadableTableColumn] = []
        column_keys: set[str] = set()
        for column in payload.columns:
            if column.key in column_keys:
                raise CompileError(f"Duplicate table column key in {owner_label}: {column.key}")
            column_keys.add(column.key)
            resolved_columns.append(
                replace(
                    column,
                    body=tuple(
                        self._interpolate_authored_prose_line(
                            line,
                            unit=unit,
                            owner_label=f"{owner_label}.columns.{column.key}",
                            surface_label="table column prose",
                            ambiguous_label="table column interpolation ref",
                        )
                        for line in column.body
                    ),
                )
            )
        if not resolved_columns:
            raise CompileError(f"Readable table must declare at least one column in {owner_label}")

        row_schema = self._resolve_readable_inline_schema(
            payload.row_schema,
            unit=unit,
            owner_label=owner_label,
            schema_label="row_schema",
            surface_label="table row schema",
        )

        resolved_rows: list[model.ReadableTableRow] = []
        row_keys: set[str] = set()
        for row in payload.rows:
            if row.key in row_keys:
                raise CompileError(f"Duplicate table row key in {owner_label}: {row.key}")
            row_keys.add(row.key)
            cell_keys: set[str] = set()
            resolved_cells: list[model.ReadableTableCell] = []
            for cell in row.cells:
                if cell.key not in column_keys:
                    raise CompileError(
                        f"Table row references an unknown column in {owner_label}: {cell.key}"
                    )
                if cell.key in cell_keys:
                    raise CompileError(
                        f"Duplicate table row cell in {owner_label}.{row.key}: {cell.key}"
                    )
                cell_keys.add(cell.key)
                if cell.body is not None:
                    resolved_cells.append(
                        model.ReadableTableCell(
                            key=cell.key,
                            body=self._resolve_document_shared_readable_body(
                                cell.body,
                                unit=unit,
                                owner_label=f"{owner_label}.{row.key}.{cell.key}",
                                kind="table cell body",
                            ),
                        )
                    )
                    continue
                cell_text = self._interpolate_authored_prose_string(
                    cell.text or "",
                    unit=unit,
                    owner_label=f"{owner_label}.{row.key}.{cell.key}",
                    surface_label="table cell prose",
                    ambiguous_label="table cell interpolation ref",
                )
                if "\n" in cell_text:
                    raise CompileError(
                        "Readable table inline cells must stay single-line in "
                        f"{owner_label}.{row.key}.{cell.key}; nested tables require structured cell bodies."
                    )
                resolved_cells.append(model.ReadableTableCell(key=cell.key, text=cell_text))
            resolved_rows.append(model.ReadableTableRow(key=row.key, cells=tuple(resolved_cells)))

        resolved_notes = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="table notes",
                ambiguous_label="table note interpolation ref",
            )
            for line in payload.notes
        )

        return model.ReadableTableData(
            columns=tuple(resolved_columns),
            rows=tuple(resolved_rows),
            notes=resolved_notes,
            row_schema=row_schema,
        )

    def _resolve_skills_addressable_body(
        self,
        skills_body: model.SkillsBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_skills: ResolvedSkillsBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedSkillsBody:
        if parent_skills is None:
            return ResolvedSkillsBody(
                title=skills_body.title,
                preamble=(),
                items=self._resolve_non_inherited_addressable_skills_items(
                    skills_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_skills.items}
        resolved_items: list[ResolvedSkillsItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in skills_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_skills_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(self._resolve_skill_entry(item, unit=unit))
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined skills entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined skills entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSkillsSection):
                if not isinstance(parent_item, ResolvedSkillsSection):
                    raise CompileError(
                        f"Override kind mismatch for skills entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_addressable_skills_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedSkillEntry):
                raise CompileError(
                    f"Override kind mismatch for skills entry in {owner_label}: {key}"
                )
            resolved_items.append(self._resolve_skill_entry(item, unit=unit))

        missing_keys = [
            parent_item.key
            for parent_item in parent_skills.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited skills entry in {owner_label}: {missing}"
            )

        return ResolvedSkillsBody(
            title=skills_body.title,
            preamble=(),
            items=tuple(resolved_items),
        )

    def _resolve_non_inherited_skills_items(
        self,
        skills_items: tuple[model.SkillsItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSkillsItem, ...]:
        resolved_items: list[ResolvedSkillsItem] = []
        seen_keys: set[str] = set()

        for item in skills_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(self._resolve_skill_entry(item, unit=unit))
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited skills block in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_addressable_skills_items(
        self,
        skills_items: tuple[model.SkillsItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSkillsItem, ...]:
        resolved_items: list[ResolvedSkillsItem] = []
        seen_keys: set[str] = set()

        for item in skills_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_skills_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(self._resolve_skill_entry(item, unit=unit))
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited skills block in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_io_items(
        self,
        io_items: tuple[model.IoItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> tuple[ResolvedIoItem, ...]:
        resolved_items: list[ResolvedIoItem] = []
        seen_keys: set[str] = set()

        for item in io_items:
            if isinstance(item, model.RecordRef):
                resolved_item = self._resolve_io_ref_item(
                    item,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=owner_label,
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=excluded_output_keys,
                )
                if resolved_item is not None:
                    resolved_items.append(resolved_item)
                continue

            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate {field_kind} item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.RecordSection):
                resolved_item = self._resolve_io_section_item(
                    item,
                    unit=unit,
                    field_kind=field_kind,
                    binding_path=(item.key,),
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=excluded_output_keys,
                )
                if resolved_item is not None:
                    resolved_items.append(resolved_item)
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited {field_kind} block in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_skills_section_body_items(
        self,
        items: tuple[model.SkillsSectionItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSkillsSectionBodyItem, ...]:
        resolved: list[ResolvedSkillsSectionBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                resolved.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="skills prose",
                        ambiguous_label="skills prose interpolation ref",
                    )
                )
                continue
            resolved.append(self._resolve_skill_entry(item, unit=unit))
        return tuple(resolved)

    def _resolve_addressable_skills_section_body_items(
        self,
        items: tuple[model.SkillsSectionItem, ...],
        *,
        unit: IndexedUnit,
    ) -> tuple[ResolvedSkillsSectionBodyItem, ...]:
        resolved: list[ResolvedSkillsSectionBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                continue
            resolved.append(self._resolve_skill_entry(item, unit=unit))
        return tuple(resolved)

    def _resolve_skill_entry(
        self,
        entry: model.SkillEntry | model.OverrideSkillEntry,
        *,
        unit: IndexedUnit,
    ) -> ResolvedSkillEntry:
        target_unit, skill_decl = self._resolve_skill_decl(entry.target, unit=unit)
        return ResolvedSkillEntry(
            key=entry.key,
            metadata_unit=unit,
            target_unit=target_unit,
            skill_decl=skill_decl,
            items=entry.items,
        )

    def _resolve_section_body_items(
        self,
        items: tuple[model.SectionBodyItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSectionBodyItem, ...]:
        resolved: list[ResolvedSectionBodyItem] = []
        for item in items:
            if isinstance(item, str):
                resolved.append(
                    self._interpolate_authored_prose_string(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="workflow strings",
                        ambiguous_label="workflow string interpolation ref",
                    )
                )
                continue
            if isinstance(item, model.EmphasizedLine):
                resolved.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="workflow strings",
                        ambiguous_label="workflow string interpolation ref",
                    )
                )
                continue
            if isinstance(item, model.LocalSection):
                resolved.append(
                    ResolvedSectionItem(
                        key=item.key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                        ),
                    )
                )
                continue
            if isinstance(item, model.ReadableBlock):
                resolved.append(item)
                continue
            if isinstance(item, model.SectionBodyRef):
                resolved.append(
                    self._resolve_section_body_ref(item.ref, unit=unit, owner_label=owner_label)
                )
                continue
            target_unit, target_agent = self._resolve_agent_ref(item.target, unit=unit)
            if target_agent.abstract:
                dotted_name = _dotted_ref_name(item.target)
                raise CompileError(f"Route target must be a concrete agent: {dotted_name}")
            resolved.append(
                ResolvedRouteLine(
                    label=self._interpolate_authored_prose_string(
                        item.label,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="route labels",
                    ),
                    target_module_parts=target_unit.module_parts,
                    target_name=target_agent.name,
                    target_display_name=target_agent.title or target_agent.name,
                )
            )
        return tuple(resolved)

    def _resolve_addressable_section_body_items(
        self,
        items: tuple[model.SectionBodyItem, ...],
        *,
        unit: IndexedUnit,
    ) -> tuple[ResolvedSectionBodyItem, ...]:
        resolved: list[ResolvedSectionBodyItem] = []
        for item in items:
            if not isinstance(item, model.LocalSection):
                continue
            resolved.append(
                ResolvedSectionItem(
                    key=item.key,
                    title=item.title,
                    items=self._resolve_addressable_section_body_items(
                        item.items,
                        unit=unit,
                    ),
                )
            )
        return tuple(resolved)

    def _resolve_section_body_ref(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSectionRef:
        value = self._resolve_addressable_ref_value(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label="workflow section bodies",
            ambiguous_label="workflow section declaration ref",
            missing_local_label="workflow section body",
        )
        return ResolvedSectionRef(label=value.text)

    def _resolve_authored_prose_interpolation_expr(
        self,
        expression: str,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> str:
        match = _INTERPOLATION_EXPR_RE.fullmatch(expression)
        if match is None:
            raise CompileError(
                f"Invalid interpolation in {owner_label}: {{{{{expression}}}}}"
            )

        ref = model.AddressableRef(
            root=_name_ref_from_dotted_name(match.group(1)),
            path=tuple(match.group(2).split(".")) if match.group(2) is not None else (),
        )
        return self._resolve_addressable_ref_value(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ambiguous_label=ambiguous_label or f"{surface_label} interpolation ref",
            missing_local_label=surface_label,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
            render_profile=render_profile,
        ).text

    def _resolve_readable_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str,
        missing_local_label: str,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> tuple[IndexedUnit, ReadableDecl]:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        matches = self._find_readable_decl_matches(
            ref.declaration_name,
            unit=target_unit,
        )
        dotted_name = _dotted_ref_name(ref) if ref.module_parts else ref.declaration_name

        if len(matches) == 1:
            decl = matches[0][1]
            if isinstance(decl, model.Agent) and decl.abstract:
                raise CompileError(
                    f"Abstract agent refs are not allowed in {surface_label}; "
                    f"mention a concrete agent instead: {dotted_name}"
                )
            return target_unit, decl

        if len(matches) > 1:
            labels = ", ".join(label for label, _decl in matches)
            raise CompileError(
                f"Ambiguous {ambiguous_label} in {owner_label}: "
                f"{dotted_name} matches {labels}"
            )

        if target_unit.workflows_by_name.get(ref.declaration_name) is not None:
            raise CompileError(
                f"Workflow refs are not allowed in {surface_label}; "
                f"use `use` for workflow composition: {dotted_name}"
            )

        fallback_unit = self._review_semantic_fallback_lookup_unit(
            ref,
            unit=unit,
            review_semantics=review_semantics,
        )
        if fallback_unit is not None:
            fallback_matches = self._find_readable_decl_matches(
                ref.declaration_name,
                unit=fallback_unit,
            )
            if len(fallback_matches) == 1:
                decl = fallback_matches[0][1]
                if isinstance(decl, model.Agent) and decl.abstract:
                    raise CompileError(
                        f"Abstract agent refs are not allowed in {surface_label}; "
                        f"mention a concrete agent instead: {dotted_name}"
                    )
                return fallback_unit, decl
            if len(fallback_matches) > 1:
                labels = ", ".join(label for label, _decl in fallback_matches)
                raise CompileError(
                    f"Ambiguous {ambiguous_label} in {owner_label}: "
                    f"{dotted_name} matches {labels}"
                )
            if fallback_unit.workflows_by_name.get(ref.declaration_name) is not None:
                raise CompileError(
                    f"Workflow refs are not allowed in {surface_label}; "
                    f"use `use` for workflow composition: {dotted_name}"
                )

        if ref.module_parts:
            raise CompileError(f"Missing imported declaration: {dotted_name}")

        raise CompileError(
            f"Missing local declaration ref in {missing_local_label} {owner_label}: "
            f"{ref.declaration_name}"
        )

    def _resolve_addressable_ref_value(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str,
        missing_local_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> DisplayValue:
        ref_label = _display_addressable_ref(ref)
        route_value = self._resolve_route_semantic_ref_value(
            ref,
            owner_label=owner_label,
            surface_label=surface_label,
            route_semantics=route_semantics,
        )
        if route_value is not None:
            return route_value
        semantic_node = self._resolve_review_semantic_node(
            ref,
            review_semantics=review_semantics,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
        )
        if semantic_node is not None:
            return self._display_addressable_target_value(
                semantic_node,
                owner_label=owner_label,
                surface_label=surface_label,
                render_profile=render_profile,
            )
        if not ref.path:
            target_unit, decl = self._resolve_readable_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
                missing_local_label=missing_local_label,
                review_semantics=review_semantics,
            )
            return self._display_addressable_target_value(
                AddressableNode(unit=target_unit, root_decl=decl, target=decl),
                owner_label=owner_label,
                surface_label=surface_label,
                render_profile=render_profile,
            )

        target_unit, decl = self._resolve_addressable_root_decl(
            ref.root,
            unit=unit,
            owner_label=owner_label,
            ambiguous_label=ambiguous_label,
            missing_local_label=missing_local_label,
            review_semantics=review_semantics,
        )
        return self._resolve_addressable_path_value(
            AddressableNode(unit=target_unit, root_decl=decl, target=decl),
            ref.path,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
            render_profile=render_profile,
        )

    def _resolve_addressable_root_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        ambiguous_label: str,
        missing_local_label: str,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> tuple[IndexedUnit, AddressableRootDecl]:
        semantic_root = self._resolve_review_semantic_root_decl(
            ref,
            review_semantics=review_semantics,
        )
        if semantic_root is not None and review_semantics is not None:
            output_unit, _output_decl = self._resolve_review_semantic_output_decl(review_semantics)
            return output_unit, semantic_root
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        matches = self._find_addressable_root_matches(
            ref.declaration_name,
            unit=target_unit,
        )
        dotted_name = _dotted_ref_name(ref) if ref.module_parts else ref.declaration_name

        if len(matches) == 1:
            decl = matches[0][1]
            if isinstance(decl, model.Agent) and decl.abstract:
                raise CompileError(
                    "Abstract agent refs are not allowed in addressable paths; "
                    f"mention a concrete agent instead: {dotted_name}"
                )
            return target_unit, decl

        if len(matches) > 1:
            labels = ", ".join(label for label, _decl in matches)
            raise CompileError(
                f"Ambiguous {ambiguous_label} in {owner_label}: "
                f"{dotted_name} matches {labels}"
            )

        fallback_unit = self._review_semantic_fallback_lookup_unit(
            ref,
            unit=unit,
            review_semantics=review_semantics,
        )
        if fallback_unit is not None:
            fallback_matches = self._find_addressable_root_matches(
                ref.declaration_name,
                unit=fallback_unit,
            )
            if len(fallback_matches) == 1:
                decl = fallback_matches[0][1]
                if isinstance(decl, model.Agent) and decl.abstract:
                    raise CompileError(
                        "Abstract agent refs are not allowed in addressable paths; "
                        f"mention a concrete agent instead: {dotted_name}"
                    )
                return fallback_unit, decl
            if len(fallback_matches) > 1:
                labels = ", ".join(label for label, _decl in fallback_matches)
                raise CompileError(
                    f"Ambiguous {ambiguous_label} in {owner_label}: "
                    f"{dotted_name} matches {labels}"
                )

        if ref.module_parts:
            raise CompileError(f"Missing imported declaration: {dotted_name}")

        raise CompileError(
            f"Missing local declaration ref in {missing_local_label} {owner_label}: "
            f"{ref.declaration_name}"
        )

    def _resolve_addressable_path_value(
        self,
        start: AddressableNode,
        path: tuple[str, ...],
        *,
        owner_label: str,
        surface_label: str,
        ref_label: str,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> DisplayValue:
        current = self._resolve_addressable_path_node(
            start,
            path,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
        )

        return self._display_addressable_target_value(
            current,
            owner_label=owner_label,
            surface_label=surface_label,
            render_profile=render_profile,
        )

    def _resolve_addressable_path_node(
        self,
        start: AddressableNode,
        path: tuple[str, ...],
        *,
        owner_label: str,
        surface_label: str,
        ref_label: str,
    ) -> AddressableNode:
        current = start

        for index, segment in enumerate(path):
            is_last = index == len(path) - 1
            if is_last:
                projection = self._resolve_addressable_projection(
                    current,
                    segment=segment,
                    owner_label=owner_label,
                    surface_label=surface_label,
                )
                if projection is not None:
                    return AddressableNode(
                        unit=current.unit,
                        root_decl=current.root_decl,
                        target=projection,
                    )
            if is_last and segment in {"name", "title", "key", "wire"}:
                raise CompileError(
                    f"Unknown addressable path on {surface_label} in {owner_label}: "
                    f"{ref_label}"
                )

            children = self._get_addressable_children(current)
            if children is None:
                raise CompileError(
                    "Addressable path must stay addressable on "
                    f"{surface_label} in {owner_label}: {ref_label}"
                )
            next_node = children.get(segment)
            if next_node is None:
                raise CompileError(
                    f"Unknown addressable path on {surface_label} in {owner_label}: "
                    f"{ref_label}"
                )
            current = next_node

        return current

    def _resolve_addressable_projection(
        self,
        node: AddressableNode,
        *,
        segment: str,
        owner_label: str,
        surface_label: str,
    ) -> AddressableProjectionTarget | None:
        target = node.target
        if segment == "title":
            title = self._display_addressable_title(
                node,
                owner_label=owner_label,
                surface_label=surface_label,
            )
            if title is not None:
                return AddressableProjectionTarget(text=title, kind="title")
            return None
        if isinstance(target, model.Agent):
            if segment in {"name", "key"}:
                return AddressableProjectionTarget(text=target.name, kind="symbol")
            return None
        if isinstance(target, model.EnumMember):
            if segment == "key":
                return AddressableProjectionTarget(text=target.key, kind="symbol")
            if segment == "wire":
                return AddressableProjectionTarget(text=target.value, kind="symbol")
            return None
        return None

    def _resolve_readable_decl_lookup_unit(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> IndexedUnit:
        if not ref.module_parts or ref.module_parts == unit.module_parts:
            return unit

        target_unit = unit.imported_units.get(ref.module_parts)
        if target_unit is None:
            raise CompileError(f"Missing import module: {'.'.join(ref.module_parts)}")
        return target_unit

    def _resolve_constant_enum_member(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> str | None:
        if isinstance(expr, str):
            return expr
        if isinstance(expr, model.ExprRef) and self._expr_ref_matches_review_verdict(expr):
            return _REVIEW_VERDICT_TEXT[expr.parts[1]]
        if not isinstance(expr, model.ExprRef) or len(expr.parts) < 2:
            return None
        name_ref = _name_ref_from_dotted_name(".".join(expr.parts[:-1]))
        enum_decl = self._try_resolve_enum_decl(name_ref, unit=unit)
        if enum_decl is None:
            return None
        member = next((member for member in enum_decl.members if member.key == expr.parts[-1]), None)
        if member is None:
            return None
        return member.value

    def _resolve_match_enum_decl(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        mode_bindings: dict[str, model.ModeStmt],
    ) -> model.EnumDecl | None:
        if not isinstance(expr, model.ExprRef) or len(expr.parts) != 1:
            return None
        mode_stmt = mode_bindings.get(expr.parts[0])
        if mode_stmt is None:
            return None
        enum_unit, enum_decl = self._resolve_decl_ref(
            mode_stmt.enum_ref,
            unit=unit,
            registry_name="enums_by_name",
            missing_label="enum declaration",
        )
        _ = enum_unit
        return enum_decl

    def _resolve_fixed_match_value(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: LawBranch,
    ) -> str | None:
        if not isinstance(expr, model.ExprRef) or len(expr.parts) != 1:
            return None
        for mode_stmt in reversed(branch.mode_bindings):
            if mode_stmt.name == expr.parts[0]:
                return self._resolve_constant_enum_member(mode_stmt.expr, unit=unit)
        return None

    def _resolve_law_path(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> ResolvedLawPath:
        matches: list[ResolvedLawPath] = []
        if agent_contract is not None:
            matches.extend(
                self._resolve_bound_law_matches(
                    path,
                    agent_contract=agent_contract,
                    allowed_kinds=allowed_kinds,
                )
            )
        for split_index in range(1, len(path.parts) + 1):
            ref = model.NameRef(
                module_parts=path.parts[: split_index - 1],
                declaration_name=path.parts[split_index - 1],
            )
            try:
                lookup_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
            except CompileError:
                continue
            remainder = path.parts[split_index:]
            if "input" in allowed_kinds:
                input_decl = lookup_unit.inputs_by_name.get(ref.declaration_name)
                if input_decl is not None:
                    matches.append(
                        ResolvedLawPath(
                            unit=lookup_unit,
                            decl=input_decl,
                            remainder=remainder,
                            wildcard=path.wildcard,
                        )
                    )
            if "output" in allowed_kinds:
                output_decl = lookup_unit.outputs_by_name.get(ref.declaration_name)
                if output_decl is not None:
                    matches.append(
                        ResolvedLawPath(
                            unit=lookup_unit,
                            decl=output_decl,
                            remainder=remainder,
                            wildcard=path.wildcard,
                        )
                    )
            if "enum" in allowed_kinds:
                enum_decl = lookup_unit.enums_by_name.get(ref.declaration_name)
                if enum_decl is not None:
                    matches.append(
                        ResolvedLawPath(
                            unit=lookup_unit,
                            decl=enum_decl,
                            remainder=remainder,
                            wildcard=path.wildcard,
                        )
                    )
            if "grounding" in allowed_kinds:
                grounding_decl = lookup_unit.groundings_by_name.get(ref.declaration_name)
                if grounding_decl is not None:
                    matches.append(
                        ResolvedLawPath(
                            unit=lookup_unit,
                            decl=grounding_decl,
                            remainder=remainder,
                            wildcard=path.wildcard,
                        )
                    )
            if "schema_family" in allowed_kinds:
                schema_decl = lookup_unit.schemas_by_name.get(ref.declaration_name)
                if schema_decl is not None and remainder:
                    resolved_schema = self._resolve_schema_decl(schema_decl, unit=lookup_unit)
                    family_items_by_key = {
                        "sections": resolved_schema.sections,
                        "gates": resolved_schema.gates,
                        "artifacts": resolved_schema.artifacts,
                        "groups": resolved_schema.groups,
                    }
                    family_items = family_items_by_key.get(remainder[0])
                    if family_items is not None:
                        matches.append(
                            ResolvedLawPath(
                                unit=lookup_unit,
                                decl=SchemaFamilyTarget(
                                    family_key=remainder[0],
                                    title=_SCHEMA_FAMILY_TITLES[remainder[0]],
                                    items=family_items,
                                ),
                                remainder=remainder[1:],
                                wildcard=path.wildcard,
                            )
                        )
            if "schema_group" in allowed_kinds:
                schema_decl = lookup_unit.schemas_by_name.get(ref.declaration_name)
                if schema_decl is not None and len(remainder) >= 2 and remainder[0] == "groups":
                    resolved_schema = self._resolve_schema_decl(schema_decl, unit=lookup_unit)
                    group = next(
                        (item for item in resolved_schema.groups if item.key == remainder[1]),
                        None,
                    )
                    if group is not None:
                        matches.append(
                            ResolvedLawPath(
                                unit=lookup_unit,
                                decl=group,
                                remainder=remainder[2:],
                                wildcard=path.wildcard,
                            )
                        )

        unique_matches: list[ResolvedLawPath] = []
        seen: set[tuple[tuple[str, ...], str, tuple[str, ...], str]] = set()
        for match in matches:
            key = self._law_path_match_key(match)
            if key in seen:
                continue
            seen.add(key)
            unique_matches.append(match)

        if len(unique_matches) == 1:
            return unique_matches[0]
        if len(unique_matches) > 1:
            choices = ", ".join(
                _dotted_decl_name(match.unit.module_parts, self._law_path_decl_identity(match.decl))
                for match in unique_matches
            )
            raise CompileError(
                f"Ambiguous {statement_label} path in {owner_label}: "
                f"{'.'.join(path.parts)} matches {choices}"
            )

        allowed_text = self._law_path_allowed_text(
            allowed_kinds,
            agent_contract=agent_contract,
        )
        raise CompileError(
            f"{statement_label} target must resolve to a {allowed_text} in {owner_label}: "
            f"{'.'.join(path.parts)}"
        )

    def _resolve_bound_law_matches(
        self,
        path: model.LawPath,
        *,
        agent_contract: AgentContract,
        allowed_kinds: tuple[str, ...],
    ) -> tuple[ResolvedLawPath, ...]:
        for split_index in range(len(path.parts), 0, -1):
            prefix = path.parts[:split_index]
            candidates: list[ContractBinding] = []
            if "input" in allowed_kinds:
                binding = agent_contract.input_bindings_by_path.get(prefix)
                if binding is not None:
                    candidates.append(binding)
            if "output" in allowed_kinds:
                binding = agent_contract.output_bindings_by_path.get(prefix)
                if binding is not None:
                    candidates.append(binding)
            if not candidates:
                continue
            return tuple(
                ResolvedLawPath(
                    unit=binding.artifact.unit,
                    decl=binding.artifact.decl,
                    remainder=path.parts[len(binding.binding_path) :],
                    wildcard=path.wildcard,
                    binding_path=binding.binding_path,
                )
                for binding in candidates
            )
        return ()
