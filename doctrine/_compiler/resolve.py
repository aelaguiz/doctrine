from __future__ import annotations

from doctrine._compiler.shared import *  # noqa: F401,F403
from doctrine._compiler.shared import (
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
    _default_worker_count,
    _display_addressable_ref,
    _dotted_decl_name,
    _dotted_ref_name,
    _humanize_key,
    _law_path_from_name_ref,
    _lowercase_initial,
    _name_ref_from_dotted_name,
    _resolve_render_profile_mode,
    _semantic_render_target_for_block,
)


class ResolveMixin:
    """Resolution helper owner for CompilationContext."""

    def _resolve_final_output_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[IndexedUnit, model.OutputDecl]:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        local_decl = target_unit.outputs_by_name.get(ref.declaration_name)
        if local_decl is not None:
            return target_unit, local_decl

        other_kind = self._named_non_output_decl_kind(ref.declaration_name, unit=target_unit)
        if other_kind is not None:
            raise CompileError(
                "E211 final_output must point at an output declaration in "
                f"{owner_label}: {_dotted_ref_name(ref)} resolves to {other_kind}"
            )
        return self._resolve_output_decl(ref, unit=unit)

    def _resolve_final_output_json_shape_summary(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
    ) -> FinalOutputJsonShapeSummary | None:
        if isinstance(value, (str, model.AddressableRef)):
            return None
        if not self._ref_exists_in_registry(value, unit=unit, registry_name="output_shapes_by_name"):
            return None

        shape_unit, shape_decl = self._resolve_output_shape_decl(value, unit=unit)
        shape_scalars, _shape_sections, shape_extras = self._split_record_items(
            shape_decl.items,
            scalar_keys={"kind", "schema", "example_file"},
            owner_label=f"output shape {shape_decl.name}",
        )
        schema_item = shape_scalars.get("schema")
        if schema_item is None or not isinstance(schema_item.value, model.NameRef):
            return None

        schema_unit, schema_decl = self._resolve_json_schema_ref(schema_item.value, unit=shape_unit)
        schema_scalars, _schema_sections, _schema_extras = self._split_record_items(
            schema_decl.items,
            scalar_keys={"profile", "file"},
            owner_label=f"json schema {schema_decl.name}",
        )
        profile_item = schema_scalars.get("profile")
        schema_file_item = schema_scalars.get("file")
        example_file_item = shape_scalars.get("example_file")
        if profile_item is None:
            schema_profile = None
        elif isinstance(profile_item.value, model.NameRef) and not profile_item.value.module_parts:
            schema_profile = profile_item.value.declaration_name
        else:
            schema_profile = self._display_symbol_value(
                profile_item.value,
                unit=schema_unit,
                owner_label=f"json schema {schema_decl.name}",
                surface_label="json schema fields",
            )
        if schema_file_item is None:
            schema_file = None
        elif isinstance(schema_file_item.value, str):
            schema_file = schema_file_item.value
        else:
            schema_file = self._display_symbol_value(
                schema_file_item.value,
                unit=schema_unit,
                owner_label=f"json schema {schema_decl.name}",
                surface_label="json schema fields",
            )
        example_file = (
            example_file_item.value
            if example_file_item is not None and isinstance(example_file_item.value, str)
            else None
        )
        payload_rows = self._load_json_schema_payload_rows(
            schema_unit=schema_unit,
            schema_decl=schema_decl,
            schema_file=schema_file,
        )
        resolved_schema_file = (
            self._resolve_declared_support_path(schema_unit, schema_file)
            if schema_file is not None
            else None
        )
        resolved_example_file = (
            self._resolve_declared_support_path(shape_unit, example_file)
            if example_file is not None
            else None
        )
        example_text = (
            self._read_required_final_output_support_text(
                shape_unit,
                example_file,
                owner_label=f"output shape {shape_decl.name}",
            )
            if example_file is not None
            else None
        )
        return FinalOutputJsonShapeSummary(
            shape_unit=shape_unit,
            shape_decl=shape_decl,
            schema_unit=schema_unit,
            schema_decl=schema_decl,
            schema_profile=schema_profile,
            schema_file=schema_file,
            example_file=example_file,
            resolved_schema_file=resolved_schema_file,
            resolved_example_file=resolved_example_file,
            payload_rows=payload_rows,
            example_text=example_text,
            extra_items=shape_extras,
        )

    def _resolve_output_render_profiles(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        files_section: model.RecordSection | None,
        shape_item: model.RecordScalar | None,
    ) -> tuple[ResolvedRenderProfile | None, ResolvedRenderProfile | None]:
        explicit_render_profile: ResolvedRenderProfile | None = None
        if decl.render_profile_ref is not None:
            if files_section is not None:
                raise CompileError(
                    f"Output render_profile requires one markdown-bearing output artifact in {decl.name}"
                )
            if shape_item is None or not (
                self._is_markdown_shape_value(shape_item.value, unit=unit)
                or self._is_comment_shape_value(shape_item.value, unit=unit)
            ):
                raise CompileError(
                    f"Output render_profile requires a markdown-bearing shape in output {decl.name}"
                )
            explicit_render_profile = self._resolve_render_profile_ref(
                decl.render_profile_ref,
                unit=unit,
            )

        default_render_profile: ResolvedRenderProfile | None = None
        if files_section is None and shape_item is not None:
            if self._is_comment_shape_value(shape_item.value, unit=unit):
                default_render_profile = ResolvedRenderProfile(name="CommentMarkdown")
            elif self._is_markdown_shape_value(shape_item.value, unit=unit):
                default_render_profile = ResolvedRenderProfile(name="ArtifactMarkdown")

        return explicit_render_profile, (explicit_render_profile or default_render_profile)

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
            if all(branch.choice_members for branch in branches):
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

    def _resolve_io_field_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> ResolvedIoBody:
        if field_kind == "inputs":
            if self._ref_exists_in_registry(
                ref,
                unit=unit,
                registry_name="outputs_blocks_by_name",
            ):
                raise CompileError(
                    "Inputs fields must resolve to inputs blocks, not outputs blocks: "
                    f"{_dotted_ref_name(ref)}"
                )
            target_unit, inputs_decl = self._resolve_inputs_block_ref(ref, unit=unit)
            return self._resolve_inputs_decl(inputs_decl, unit=target_unit)

        if self._ref_exists_in_registry(
            ref,
            unit=unit,
            registry_name="inputs_blocks_by_name",
        ):
            raise CompileError(
                "Outputs fields must resolve to outputs blocks, not inputs blocks: "
                f"{_dotted_ref_name(ref)}"
            )
        target_unit, outputs_decl = self._resolve_outputs_block_ref(ref, unit=unit)
        return self._resolve_outputs_decl(
            outputs_decl,
            unit=target_unit,
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            excluded_output_keys=excluded_output_keys,
        )

    def _resolve_io_field_patch(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> ResolvedIoBody:
        parent_ref = field.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: {field_kind} patch field is missing parent ref in {owner_label}"
            )
        if not isinstance(field.value, model.IoBody) or field.title is None:
            raise CompileError(
                f"Internal compiler error: {field_kind} patch field is missing body in {owner_label}"
            )

        if field_kind == "inputs":
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="outputs_blocks_by_name",
            ):
                raise CompileError(
                    "Inputs patch fields must inherit from inputs blocks, not outputs blocks: "
                    f"{_dotted_ref_name(parent_ref)}"
                )
            parent_unit, parent_decl = self._resolve_inputs_block_ref(parent_ref, unit=unit)
            parent_body = self._resolve_inputs_decl(parent_decl, unit=parent_unit)
            inheritance_parent_body = parent_body
        else:
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="inputs_blocks_by_name",
            ):
                raise CompileError(
                    "Outputs patch fields must inherit from outputs blocks, not inputs blocks: "
                    f"{_dotted_ref_name(parent_ref)}"
                )
            parent_unit, parent_decl = self._resolve_outputs_block_ref(parent_ref, unit=unit)
            parent_body = self._resolve_outputs_decl(
                parent_decl,
                unit=parent_unit,
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                excluded_output_keys=excluded_output_keys,
            )
            inheritance_parent_body = parent_body
            if excluded_output_keys:
                inheritance_parent_body = self._resolve_outputs_decl(
                    parent_decl,
                    unit=parent_unit,
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=frozenset(),
                )

        return self._resolve_io_body(
            field.value,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            parent_io=parent_body,
            inheritance_parent_io=inheritance_parent_body,
            parent_label=f"{field_kind} {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}",
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            excluded_output_keys=excluded_output_keys,
        )

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
        route = branch.routes[0]
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

    def _resolve_input_source_spec(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> ConfigSpec:
        if not ref.module_parts:
            builtin = _BUILTIN_INPUT_SOURCES.get(ref.declaration_name)
            if builtin is not None:
                return builtin
            local_decl = unit.input_sources_by_name.get(ref.declaration_name)
            if local_decl is not None:
                return self._config_spec_from_decl(local_decl, owner_label=f"input source {local_decl.name}")

        target_unit, decl = self._resolve_input_source_decl(ref, unit=unit)
        return self._config_spec_from_decl(decl, owner_label=f"input source {decl.name}")

    def _resolve_output_target_spec(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> ConfigSpec:
        if not ref.module_parts:
            builtin = _BUILTIN_OUTPUT_TARGETS.get(ref.declaration_name)
            if builtin is not None:
                return builtin
            local_decl = unit.output_targets_by_name.get(ref.declaration_name)
            if local_decl is not None:
                return self._config_spec_from_decl(
                    local_decl,
                    owner_label=f"output target {local_decl.name}",
                )

        target_unit, decl = self._resolve_output_target_decl(ref, unit=unit)
        return self._config_spec_from_decl(decl, owner_label=f"output target {decl.name}")

    def _resolve_workflow_decl(
        self, workflow_decl: model.WorkflowDecl, *, unit: IndexedUnit
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        cached = self._resolved_workflow_cache.get(workflow_key)
        if cached is not None:
            return cached

        if workflow_key in self._workflow_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._workflow_resolution_stack, workflow_key]
            )
            raise CompileError(f"Cyclic workflow inheritance: {cycle}")

        self._workflow_resolution_stack.append(workflow_key)
        try:
            parent_workflow: ResolvedWorkflowBody | None = None
            parent_label: str | None = None
            if workflow_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_workflow_decl(
                    workflow_decl,
                    unit=unit,
                )
                parent_workflow = self._resolve_workflow_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"workflow {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_workflow_body(
                workflow_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, workflow_decl.name),
                parent_workflow=parent_workflow,
                parent_label=parent_label,
            )
            self._resolved_workflow_cache[workflow_key] = resolved
            return resolved
        finally:
            self._workflow_resolution_stack.pop()

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
                parent_label = (
                    f"review {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

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

    def _resolve_workflow_for_addressable_paths(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        if (
            workflow_key in self._workflow_resolution_stack
            or workflow_key in self._workflow_addressable_resolution_stack
        ):
            return self._resolve_workflow_addressable_decl(workflow_decl, unit=unit)
        return self._resolve_workflow_decl(workflow_decl, unit=unit)

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

    def _resolve_workflow_addressable_decl(
        self, workflow_decl: model.WorkflowDecl, *, unit: IndexedUnit
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        cached = self._addressable_workflow_cache.get(workflow_key)
        if cached is not None:
            return cached

        if workflow_key in self._workflow_addressable_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [
                    *self._workflow_addressable_resolution_stack,
                    workflow_key,
                ]
            )
            raise CompileError(f"Cyclic workflow inheritance: {cycle}")

        self._workflow_addressable_resolution_stack.append(workflow_key)
        try:
            parent_workflow: ResolvedWorkflowBody | None = None
            parent_label: str | None = None
            if workflow_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_workflow_decl(
                    workflow_decl,
                    unit=unit,
                )
                parent_workflow = self._resolve_workflow_for_addressable_paths(
                    parent_decl,
                    unit=parent_unit,
                )
                parent_label = (
                    f"workflow {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_workflow_addressable_body(
                workflow_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, workflow_decl.name),
                parent_workflow=parent_workflow,
                parent_label=parent_label,
            )
            self._addressable_workflow_cache[workflow_key] = resolved
            return resolved
        finally:
            self._workflow_addressable_resolution_stack.pop()

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

    def _resolve_schema_decl(
        self, schema_decl: model.SchemaDecl, *, unit: IndexedUnit
    ) -> ResolvedSchemaBody:
        schema_key = (unit.module_parts, schema_decl.name)
        cached = self._resolved_schema_cache.get(schema_key)
        if cached is not None:
            return cached

        if schema_key in self._schema_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._schema_resolution_stack, schema_key]
            )
            raise CompileError(f"Cyclic schema inheritance: {cycle}")

        self._schema_resolution_stack.append(schema_key)
        try:
            parent_schema: ResolvedSchemaBody | None = None
            parent_label: str | None = None
            if schema_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_schema_decl(
                    schema_decl,
                    unit=unit,
                )
                parent_schema = self._resolve_schema_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"schema {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_schema_body(
                schema_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, schema_decl.name),
                parent_schema=parent_schema,
                parent_label=parent_label,
            )
            resolved = replace(
                resolved,
                render_profile=(
                    self._resolve_render_profile_ref(schema_decl.render_profile_ref, unit=unit)
                    if schema_decl.render_profile_ref is not None
                    else parent_schema.render_profile if parent_schema is not None else None
                ),
            )
            self._resolved_schema_cache[schema_key] = resolved
            return resolved
        finally:
            self._schema_resolution_stack.pop()

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

    def _resolve_outputs_decl(
        self,
        outputs_decl: model.OutputsDecl,
        *,
        unit: IndexedUnit,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> ResolvedIoBody:
        outputs_key = (
            unit.module_parts,
            outputs_decl.name,
            review_output_contexts,
            route_output_contexts,
            excluded_output_keys,
        )
        cached = self._resolved_outputs_cache.get(outputs_key)
        if cached is not None:
            return cached

        if outputs_key in self._outputs_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name, _review_keys, _route_keys, _excluded_keys in [
                    *self._outputs_resolution_stack,
                    outputs_key,
                ]
            )
            raise CompileError(f"Cyclic outputs inheritance: {cycle}")

        self._outputs_resolution_stack.append(outputs_key)
        try:
            parent_io: ResolvedIoBody | None = None
            inheritance_parent_io: ResolvedIoBody | None = None
            parent_label: str | None = None
            if outputs_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_outputs_decl(
                    outputs_decl,
                    unit=unit,
                )
                parent_io = self._resolve_outputs_decl(
                    parent_decl,
                    unit=parent_unit,
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=excluded_output_keys,
                )
                inheritance_parent_io = parent_io
                if excluded_output_keys:
                    inheritance_parent_io = self._resolve_outputs_decl(
                        parent_decl,
                        unit=parent_unit,
                        review_output_contexts=review_output_contexts,
                        route_output_contexts=route_output_contexts,
                        excluded_output_keys=frozenset(),
                    )
                parent_label = f"outputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"

            resolved = self._resolve_io_body(
                outputs_decl.body,
                unit=unit,
                field_kind="outputs",
                owner_label=_dotted_decl_name(unit.module_parts, outputs_decl.name),
                parent_io=parent_io,
                inheritance_parent_io=inheritance_parent_io,
                parent_label=parent_label,
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                excluded_output_keys=excluded_output_keys,
            )
            self._resolved_outputs_cache[outputs_key] = resolved
            return resolved
        finally:
            self._outputs_resolution_stack.pop()

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

    def _resolve_io_body(
        self,
        io_body: model.IoBody,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        parent_io: ResolvedIoBody | None = None,
        inheritance_parent_io: ResolvedIoBody | None = None,
        parent_label: str | None = None,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> ResolvedIoBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label=f"{field_kind} prose",
                ambiguous_label=f"{field_kind} prose interpolation ref",
            )
            for line in io_body.preamble
        )
        if parent_io is None:
            resolved_items = self._resolve_non_inherited_io_items(
                io_body.items,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                excluded_output_keys=excluded_output_keys,
            )
            return ResolvedIoBody(
                title=io_body.title,
                preamble=resolved_preamble,
                items=resolved_items,
                artifacts=self._resolved_io_body_artifacts(resolved_items),
                bindings=self._resolved_io_body_bindings(resolved_items),
            )

        inherited_parent_io = inheritance_parent_io if inheritance_parent_io is not None else parent_io
        unkeyed_parent_titles = [
            item.section.title for item in inherited_parent_io.items if isinstance(item, ResolvedIoRef)
        ]
        if unkeyed_parent_titles:
            details = ", ".join(unkeyed_parent_titles)
            raise CompileError(
                f"Cannot inherit {field_kind} block with unkeyed top-level refs in {parent_label}: {details}"
            )

        parent_items_by_key = {
            item.key: item for item in inherited_parent_io.items if isinstance(item, ResolvedIoSection)
        }
        visible_parent_items_by_key = {
            item.key: item for item in parent_io.items if isinstance(item, ResolvedIoSection)
        }
        resolved_items: list[ResolvedIoItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in io_body.items:
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
            if key in emitted_keys:
                raise CompileError(f"Duplicate {field_kind} item key in {owner_label}: {key}")
            emitted_keys.add(key)

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

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined {field_kind} entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                visible_parent_item = visible_parent_items_by_key.get(key)
                if visible_parent_item is not None:
                    resolved_items.append(visible_parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined {field_kind} entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if not isinstance(item, model.OverrideIoSection):
                raise CompileError(
                    f"Internal compiler error: unsupported {field_kind} override in {owner_label}: {type(item).__name__}"
                )
            resolved_bucket = self._resolve_contract_bucket_items(
                item.items,
                unit=unit,
                field_kind=field_kind,
                owner_label=(
                    f"{field_kind} section `{item.title if item.title is not None else parent_item.section.title}`"
                ),
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                path_prefix=(key,),
                excluded_output_keys=excluded_output_keys,
            )
            bindings = list(resolved_bucket.bindings)
            if not resolved_bucket.has_keyed_children and len(resolved_bucket.direct_artifacts) == 1:
                bindings.append(
                    ContractBinding(
                        binding_path=(key,),
                        artifact=resolved_bucket.direct_artifacts[0],
                    )
                )
            if resolved_bucket.body or resolved_bucket.artifacts or bindings:
                resolved_items.append(
                    ResolvedIoSection(
                        key=key,
                        section=CompiledSection(
                            title=item.title if item.title is not None else parent_item.section.title,
                            body=resolved_bucket.body,
                        ),
                        artifacts=resolved_bucket.artifacts,
                        bindings=tuple(bindings),
                    )
                )

        missing_keys = [
            item.key
            for item in inherited_parent_io.items
            if isinstance(item, ResolvedIoSection) and item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited {field_kind} entry in {owner_label}: {missing}"
            )

        return ResolvedIoBody(
            title=io_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
            artifacts=self._resolved_io_body_artifacts(tuple(resolved_items)),
            bindings=self._resolved_io_body_bindings(tuple(resolved_items)),
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

    def _resolve_schema_body(
        self,
        schema_body: model.SchemaBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_schema: ResolvedSchemaBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedSchemaBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="schema prose",
                ambiguous_label="schema prose interpolation ref",
            )
            for line in schema_body.preamble
        )
        sections_mode, sections_items = self._schema_body_action(schema_body.items, block_key="sections")
        gates_mode, gates_items = self._schema_body_action(schema_body.items, block_key="gates")
        artifacts_mode, artifacts_items = self._schema_body_action(
            schema_body.items,
            block_key="artifacts",
        )
        groups_mode, groups_items = self._schema_body_action(schema_body.items, block_key="groups")

        if parent_schema is None:
            for block_key, mode in (
                ("sections", sections_mode),
                ("gates", gates_mode),
                ("artifacts", artifacts_mode),
                ("groups", groups_mode),
            ):
                if mode not in {"define", None}:
                    raise CompileError(
                        f"{mode} requires an inherited schema declaration in {owner_label}: {block_key}"
                    )
            resolved_sections = self._resolve_schema_sections(sections_items, unit=unit, owner_label=owner_label)
            resolved_gates = self._resolve_schema_gates(gates_items, unit=unit, owner_label=owner_label)
            resolved_artifacts = self._resolve_schema_artifacts(
                artifacts_items,
                unit=unit,
                owner_label=owner_label,
            )
            resolved_groups = self._resolve_schema_groups(groups_items, owner_label=owner_label)
        else:
            resolved_sections = self._resolve_schema_block_with_parent(
                block_key="sections",
                mode=sections_mode,
                items=sections_items,
                parent_items=parent_schema.sections,
                unit=unit,
                owner_label=owner_label,
                parent_label=parent_label,
            )
            resolved_gates = self._resolve_schema_block_with_parent(
                block_key="gates",
                mode=gates_mode,
                items=gates_items,
                parent_items=parent_schema.gates,
                unit=unit,
                owner_label=owner_label,
                parent_label=parent_label,
            )
            resolved_artifacts = self._resolve_schema_block_with_parent(
                block_key="artifacts",
                mode=artifacts_mode,
                items=artifacts_items,
                parent_items=parent_schema.artifacts,
                unit=unit,
                owner_label=owner_label,
                parent_label=parent_label,
            )
            resolved_groups = self._resolve_schema_block_with_parent(
                block_key="groups",
                mode=groups_mode,
                items=groups_items,
                parent_items=parent_schema.groups,
                unit=unit,
                owner_label=owner_label,
                parent_label=parent_label,
            )

        if not resolved_sections and not resolved_artifacts:
            raise CompileError(
                f"Schema must export at least one `sections:` or `artifacts:` block in {owner_label}"
            )
        self._validate_schema_group_members(
            resolved_groups,
            artifacts=resolved_artifacts,
            owner_label=owner_label,
        )

        return ResolvedSchemaBody(
            title=schema_body.title,
            preamble=resolved_preamble,
            sections=resolved_sections,
            gates=resolved_gates,
            artifacts=resolved_artifacts,
            groups=resolved_groups,
        )

    def _resolve_schema_block_with_parent(
        self,
        *,
        block_key: str,
        mode: str | None,
        items: tuple[object, ...],
        parent_items: tuple[object, ...],
        unit: IndexedUnit,
        owner_label: str,
        parent_label: str | None,
    ) -> tuple[object, ...]:
        if parent_items:
            if mode == "inherit":
                return parent_items
            if mode == "override":
                return self._resolve_schema_block_items(
                    block_key=block_key,
                    items=items,
                    unit=unit,
                    owner_label=owner_label,
                )
            if mode == "define":
                raise CompileError(
                    f"Inherited schema must use `override {block_key}:` in {owner_label}"
                )
            raise CompileError(f"E003 Missing inherited schema block in {owner_label}: {block_key}")

        if mode == "inherit":
            raise CompileError(
                f"Cannot inherit undefined schema block in {parent_label}: {block_key}"
            )
        if mode == "override":
            raise CompileError(
                f"E001 Cannot override undefined schema block in {parent_label}: {block_key}"
            )
        return self._resolve_schema_block_items(
            block_key=block_key,
            items=items,
            unit=unit,
            owner_label=owner_label,
        )

    def _resolve_schema_block_items(
        self,
        *,
        block_key: str,
        items: tuple[object, ...],
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[object, ...]:
        if block_key == "sections":
            return self._resolve_schema_sections(
                items,
                unit=unit,
                owner_label=owner_label,
            )
        if block_key == "gates":
            return self._resolve_schema_gates(
                items,
                unit=unit,
                owner_label=owner_label,
            )
        if block_key == "artifacts":
            return self._resolve_schema_artifacts(
                items,
                unit=unit,
                owner_label=owner_label,
            )
        if block_key == "groups":
            return self._resolve_schema_groups(items, owner_label=owner_label)
        raise CompileError(
            f"Internal compiler error: unsupported schema block key in {owner_label}: {block_key}"
        )

    def _resolve_schema_sections(
        self,
        items: tuple[object, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.SchemaSection, ...]:
        seen: set[str] = set()
        resolved: list[model.SchemaSection] = []
        for item in items:
            if not isinstance(item, model.SchemaSection):
                raise CompileError(
                    f"Internal compiler error: unsupported schema section item in {owner_label}: {type(item).__name__}"
                )
            if item.key in seen:
                raise CompileError(f"Duplicate schema section key in {owner_label}: {item.key}")
            seen.add(item.key)
            resolved.append(
                replace(
                    item,
                    body=tuple(
                        self._interpolate_authored_prose_line(
                            line,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                            surface_label="schema section prose",
                            ambiguous_label="schema prose interpolation ref",
                        )
                        for line in item.body
                    ),
                )
            )
        return tuple(resolved)

    def _resolve_schema_gates(
        self,
        items: tuple[object, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.SchemaGate, ...]:
        seen: set[str] = set()
        resolved: list[model.SchemaGate] = []
        for item in items:
            if not isinstance(item, model.SchemaGate):
                raise CompileError(
                    f"Internal compiler error: unsupported schema gate item in {owner_label}: {type(item).__name__}"
                )
            if item.key in seen:
                raise CompileError(f"Duplicate schema gate key in {owner_label}: {item.key}")
            seen.add(item.key)
            resolved.append(
                replace(
                    item,
                    body=tuple(
                        self._interpolate_authored_prose_line(
                            line,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                            surface_label="schema gate prose",
                            ambiguous_label="schema prose interpolation ref",
                        )
                        for line in item.body
                    ),
                )
            )
        return tuple(resolved)

    def _resolve_schema_artifacts(
        self,
        items: tuple[object, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSchemaArtifact, ...]:
        seen: set[str] = set()
        resolved: list[ResolvedSchemaArtifact] = []
        for item in items:
            if not isinstance(item, model.SchemaArtifact):
                raise CompileError(
                    f"Internal compiler error: unsupported schema artifact item in {owner_label}: {type(item).__name__}"
                )
            if item.key in seen:
                raise CompileError(f"Duplicate schema artifact key in {owner_label}: {item.key}")
            seen.add(item.key)
            resolved.append(
                ResolvedSchemaArtifact(
                    key=item.key,
                    title=item.title,
                    ref=item.ref,
                    artifact=self._resolve_schema_artifact_ref(
                        item.ref,
                        unit=unit,
                        owner_label=owner_label,
                    ),
                )
            )
        return tuple(resolved)

    def _resolve_schema_artifact_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ContractArtifact:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        if (decl := target_unit.inputs_by_name.get(ref.declaration_name)) is not None:
            return ContractArtifact(kind="input", unit=target_unit, decl=decl)
        if (decl := target_unit.outputs_by_name.get(ref.declaration_name)) is not None:
            return ContractArtifact(kind="output", unit=target_unit, decl=decl)

        dotted_name = _dotted_ref_name(ref)
        if ref.module_parts:
            if self._find_readable_decl_matches(ref.declaration_name, unit=target_unit):
                raise CompileError(
                    f"Schema artifact refs must resolve to input or output declarations in {owner_label}: {dotted_name}"
                )
            raise CompileError(f"Missing imported declaration: {dotted_name}")

        if self._find_readable_decl_matches(ref.declaration_name, unit=target_unit):
            raise CompileError(
                f"Schema artifact refs must resolve to input or output declarations in {owner_label}: {ref.declaration_name}"
            )
        raise CompileError(
            f"Missing local declaration ref in schema artifact {owner_label}: {ref.declaration_name}"
        )

    def _resolve_schema_groups(
        self,
        items: tuple[object, ...],
        *,
        owner_label: str,
    ) -> tuple[ResolvedSchemaGroup, ...]:
        seen: set[str] = set()
        resolved: list[ResolvedSchemaGroup] = []
        for item in items:
            if not isinstance(item, model.SchemaGroup):
                raise CompileError(
                    f"Internal compiler error: unsupported schema group item in {owner_label}: {type(item).__name__}"
                )
            if item.key in seen:
                raise CompileError(f"Duplicate schema group key in {owner_label}: {item.key}")
            if not item.members:
                raise CompileError(f"Schema groups may not be empty in {owner_label}: {item.key}")
            seen.add(item.key)
            resolved.append(
                ResolvedSchemaGroup(
                    key=item.key,
                    title=item.title,
                    members=item.members,
                )
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

    def _resolve_workflow_body(
        self,
        workflow_body: model.WorkflowBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_workflow: ResolvedWorkflowBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedWorkflowBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="workflow strings",
                ambiguous_label="workflow string interpolation ref",
            )
            for line in workflow_body.preamble
        )
        if parent_workflow is None:
            return ResolvedWorkflowBody(
                title=workflow_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_items(
                    workflow_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
                law=self._resolve_law_body(
                    workflow_body.law,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_workflow.items}
        resolved_items: list[ResolvedWorkflowItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in workflow_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
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
                        f"Cannot inherit undefined workflow entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined workflow entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSection):
                if not isinstance(parent_item, ResolvedSectionItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.OverrideWorkflowSkillsItem):
                if not isinstance(parent_item, ResolvedWorkflowSkillsItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedUseItem):
                raise CompileError(
                    f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                )
            target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
            resolved_items.append(
                ResolvedUseItem(
                    key=key,
                    target_unit=target_unit,
                    workflow_decl=workflow_decl,
                )
            )

        missing_keys = [
            parent_item.key
            for parent_item in parent_workflow.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited workflow entry in {owner_label}: {missing}"
            )

        return ResolvedWorkflowBody(
            title=workflow_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
            law=self._resolve_law_body(
                workflow_body.law,
                owner_label=owner_label,
                parent_law=parent_workflow.law,
                parent_label=parent_label,
            ),
        )

    def _resolve_law_body(
        self,
        law_body: model.LawBody | None,
        *,
        owner_label: str,
        parent_law: model.LawBody | None = None,
        parent_label: str | None = None,
    ) -> model.LawBody | None:
        if law_body is None:
            return parent_law
        if parent_law is None:
            return law_body

        parent_items = parent_law.items
        parent_has_sections = all(
            isinstance(item, model.LawSection) for item in parent_items
        )
        child_has_named_items = all(
            isinstance(
                item,
                (model.LawSection, model.LawInherit, model.LawOverrideSection),
            )
            for item in law_body.items
        )

        if not parent_has_sections or not child_has_named_items:
            raise CompileError(
                f"Inherited law blocks must use named sections only in {owner_label}"
            )

        parent_items_by_key = {
            item.key: item for item in parent_items if isinstance(item, model.LawSection)
        }
        resolved_items: list[model.LawTopLevelItem] = []
        accounted_keys: set[str] = set()

        for item in law_body.items:
            if isinstance(item, model.LawSection):
                if item.key in parent_items_by_key:
                    raise CompileError(
                        f"Inherited law block accounts for the same parent subsection more than once in {owner_label}: {item.key}"
                    )
                resolved_items.append(item)
                continue

            parent_item = parent_items_by_key.get(item.key)
            if parent_item is None:
                raise CompileError(
                    f"Cannot override undefined law section in {parent_label}: {item.key}"
                )
            if item.key in accounted_keys:
                raise CompileError(
                    f"Inherited law block accounts for the same parent subsection more than once in {owner_label}: {item.key}"
                )
            accounted_keys.add(item.key)

            if isinstance(item, model.LawInherit):
                resolved_items.append(parent_item)
            else:
                resolved_items.append(model.LawSection(key=item.key, items=item.items))

        missing_keys = sorted(set(parent_items_by_key) - accounted_keys)
        if missing_keys:
            raise CompileError(
                f"Inherited law block omits parent subsection(s) in {owner_label}: {', '.join(missing_keys)}"
            )

        return model.LawBody(items=tuple(resolved_items))

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

    def _resolve_workflow_addressable_body(
        self,
        workflow_body: model.WorkflowBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_workflow: ResolvedWorkflowBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedWorkflowBody:
        if parent_workflow is None:
            return ResolvedWorkflowBody(
                title=workflow_body.title,
                preamble=(),
                items=self._resolve_non_inherited_addressable_workflow_items(
                    workflow_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
                law=self._resolve_law_body(
                    workflow_body.law,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_workflow.items}
        resolved_items: list[ResolvedWorkflowItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in workflow_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value_for_addressable_paths(
                            item.value,
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
                        f"Cannot inherit undefined workflow entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined workflow entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSection):
                if not isinstance(parent_item, ResolvedSectionItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.OverrideWorkflowSkillsItem):
                if not isinstance(parent_item, ResolvedWorkflowSkillsItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value_for_addressable_paths(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedUseItem):
                raise CompileError(
                    f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                )
            target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
            resolved_items.append(
                ResolvedUseItem(
                    key=key,
                    target_unit=target_unit,
                    workflow_decl=workflow_decl,
                )
            )

        missing_keys = [
            parent_item.key
            for parent_item in parent_workflow.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited workflow entry in {owner_label}: {missing}"
            )

        return ResolvedWorkflowBody(
            title=workflow_body.title,
            preamble=(),
            items=tuple(resolved_items),
            law=self._resolve_law_body(
                workflow_body.law,
                owner_label=owner_label,
                parent_law=parent_workflow.law,
                parent_label=parent_label,
            ),
        )

    def _resolve_non_inherited_items(
        self,
        workflow_items: tuple[model.WorkflowItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedWorkflowItem, ...]:
        resolved_items: list[ResolvedWorkflowItem] = []
        seen_keys: set[str] = set()

        for item in workflow_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited workflow in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_addressable_workflow_items(
        self,
        workflow_items: tuple[model.WorkflowItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedWorkflowItem, ...]:
        resolved_items: list[ResolvedWorkflowItem] = []
        seen_keys: set[str] = set()

        for item in workflow_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value_for_addressable_paths(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited workflow in {owner_label}: {key}"
            )

        return tuple(resolved_items)

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

    def _resolve_io_section_item(
        self,
        item: model.RecordSection,
        *,
        unit: IndexedUnit,
        field_kind: str,
        binding_path: tuple[str, ...],
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> ResolvedIoSection | None:
        resolved_bucket = self._resolve_contract_bucket_items(
            item.items,
            unit=unit,
            field_kind=field_kind,
            owner_label=f"{field_kind} section `{item.title}`",
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            path_prefix=binding_path,
            excluded_output_keys=excluded_output_keys,
        )
        bindings = list(resolved_bucket.bindings)
        if not resolved_bucket.has_keyed_children and len(resolved_bucket.direct_artifacts) == 1:
            bindings.append(
                ContractBinding(
                    binding_path=binding_path,
                    artifact=resolved_bucket.direct_artifacts[0],
                )
            )
        if not resolved_bucket.body and not resolved_bucket.artifacts and not bindings:
            return None
        return ResolvedIoSection(
            key=item.key,
            section=CompiledSection(
                title=item.title,
                body=resolved_bucket.body,
            ),
            artifacts=resolved_bucket.artifacts,
            bindings=tuple(bindings),
        )

    def _resolve_io_ref_item(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> ResolvedIoRef | None:
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
        section, artifact = resolved_ref
        return ResolvedIoRef(
            section=section,
            artifact=artifact,
        )

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

    def _resolve_output_field_node(
        self,
        decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
    ) -> AddressableNode:
        def resolve_from_root(
            root_decl: model.OutputDecl,
            *,
            root_unit: IndexedUnit,
            field_path: tuple[str, ...],
        ) -> AddressableNode | None:
            current_node = AddressableNode(unit=root_unit, root_decl=root_decl, target=root_decl)
            if not field_path:
                return current_node
            for segment in field_path:
                children = self._get_addressable_children(current_node)
                if children is None or segment not in children:
                    return None
                current_node = children[segment]
            return current_node

        current_node = resolve_from_root(decl, root_unit=unit, field_path=path)
        if current_node is not None:
            return current_node

        if review_semantics is not None and path:
            semantic_field_path = self._review_semantic_field_path(review_semantics, path[0])
            if semantic_field_path is not None:
                semantic_unit, semantic_output_decl = self._resolve_review_semantic_output_decl(
                    review_semantics
                )
                semantic_node = resolve_from_root(
                    semantic_output_decl,
                    root_unit=semantic_unit,
                    field_path=(*semantic_field_path, *path[1:]),
                )
                if semantic_node is not None:
                    return semantic_node

        raise CompileError(
            f"Unknown output field on {surface_label} in {owner_label}: "
            f"{decl.name}.{'.'.join(path)}"
        )

    def _resolve_workflow_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.WorkflowDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="workflows_by_name",
            missing_label="workflow declaration",
        )

    def _resolve_review_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.ReviewDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="reviews_by_name",
            missing_label="review declaration",
        )

    def _resolve_skills_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.SkillsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="skills_blocks_by_name",
            missing_label="skills declaration",
        )

    def _resolve_render_profile_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> ResolvedRenderProfile:
        if not ref.module_parts:
            local_profile = unit.render_profiles_by_name.get(ref.declaration_name)
            if local_profile is not None:
                return ResolvedRenderProfile(name=local_profile.name, rules=local_profile.rules)
            if ref.declaration_name in _BUILTIN_RENDER_PROFILE_NAMES:
                return ResolvedRenderProfile(name=ref.declaration_name)
        profile_unit, profile_decl = self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="render_profiles_by_name",
            missing_label="render_profile declaration",
        )
        return ResolvedRenderProfile(name=profile_decl.name, rules=profile_decl.rules)

    def _resolve_analysis_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.AnalysisDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="analyses_by_name",
            missing_label="analysis declaration",
        )

    def _resolve_decision_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.DecisionDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="decisions_by_name",
            missing_label="decision declaration",
        )

    def _resolve_schema_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.SchemaDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="schemas_by_name",
            missing_label="schema declaration",
        )

    def _resolve_document_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.DocumentDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="documents_by_name",
            missing_label="document declaration",
        )

    def _resolve_enum_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.EnumDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="enums_by_name",
            missing_label="enum declaration",
        )

    def _resolve_inputs_block_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="inputs_blocks_by_name",
            missing_label="inputs block",
        )

    def _resolve_outputs_block_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="outputs_blocks_by_name",
            missing_label="outputs block",
        )

    def _resolve_parent_workflow_decl(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.WorkflowDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=workflow_decl.name,
            child_label="workflow",
            parent_ref=workflow_decl.parent_ref,
            registry_name="workflows_by_name",
            resolve_parent_ref=self._resolve_workflow_ref,
        )

    def _resolve_parent_analysis_decl(
        self,
        analysis_decl: model.AnalysisDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.AnalysisDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=analysis_decl.name,
            child_label="analysis",
            parent_ref=analysis_decl.parent_ref,
            registry_name="analyses_by_name",
            resolve_parent_ref=self._resolve_analysis_ref,
        )

    def _resolve_parent_schema_decl(
        self,
        schema_decl: model.SchemaDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.SchemaDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=schema_decl.name,
            child_label="schema",
            parent_ref=schema_decl.parent_ref,
            registry_name="schemas_by_name",
            resolve_parent_ref=self._resolve_schema_ref,
        )

    def _resolve_parent_document_decl(
        self,
        document_decl: model.DocumentDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.DocumentDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=document_decl.name,
            child_label="document",
            parent_ref=document_decl.parent_ref,
            registry_name="documents_by_name",
            resolve_parent_ref=self._resolve_document_ref,
        )

    def _resolve_parent_skills_decl(
        self,
        skills_decl: model.SkillsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.SkillsDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=skills_decl.name,
            child_label="skills",
            parent_ref=skills_decl.parent_ref,
            registry_name="skills_blocks_by_name",
            resolve_parent_ref=self._resolve_skills_ref,
        )

    def _resolve_parent_inputs_decl(
        self,
        inputs_decl: model.InputsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.InputsDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=inputs_decl.name,
            child_label="inputs block",
            parent_ref=inputs_decl.parent_ref,
            registry_name="inputs_blocks_by_name",
            resolve_parent_ref=self._resolve_inputs_block_ref,
        )

    def _resolve_parent_outputs_decl(
        self,
        outputs_decl: model.OutputsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.OutputsDecl]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=outputs_decl.name,
            child_label="outputs block",
            parent_ref=outputs_decl.parent_ref,
            registry_name="outputs_blocks_by_name",
            resolve_parent_ref=self._resolve_outputs_block_ref,
        )

    def _resolve_input_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="inputs_by_name",
            missing_label="input declaration",
        )

    def _resolve_input_source_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputSourceDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="input_sources_by_name",
            missing_label="input source declaration",
        )

    def _resolve_output_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="outputs_by_name",
            missing_label="output declaration",
        )

    def _resolve_output_target_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputTargetDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="output_targets_by_name",
            missing_label="output target declaration",
        )

    def _resolve_output_shape_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputShapeDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="output_shapes_by_name",
            missing_label="output shape declaration",
        )

    def _resolve_json_schema_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.JsonSchemaDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="json_schemas_by_name",
            missing_label="json schema declaration",
        )

    def _resolve_skill_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.SkillDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="skills_by_name",
            missing_label="skill declaration",
        )

    def _resolve_agent_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.Agent]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="agents_by_name",
            missing_label="agent declaration",
        )

    def _resolve_parent_agent_decl(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.Agent]:
        return self._resolve_parent_decl(
            unit=unit,
            child_name=agent.name,
            child_label="agent",
            parent_ref=agent.parent_ref,
            registry_name="agents_by_name",
            resolve_parent_ref=self._resolve_agent_ref,
        )

    def _resolve_parent_decl(
        self,
        *,
        unit: IndexedUnit,
        child_name: str,
        child_label: str,
        parent_ref: model.NameRef | None,
        registry_name: str,
        resolve_parent_ref,
    ):
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: {child_label} has no parent ref: {child_name}"
            )
        if not parent_ref.module_parts:
            registry = getattr(unit, registry_name)
            parent_decl = registry.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent {child_label} for {child_name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return resolve_parent_ref(parent_ref, unit=unit)

    def _resolve_decl_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        registry_name: str,
        missing_label: str,
    ):
        if not ref.module_parts:
            registry = getattr(unit, registry_name)
            decl = registry.get(ref.declaration_name)
            if decl is None:
                raise CompileError(f"Missing local {missing_label}: {ref.declaration_name}")
            return unit, decl

        if ref.module_parts == unit.module_parts:
            registry = getattr(unit, registry_name)
            decl = registry.get(ref.declaration_name)
            if decl is None:
                dotted_name = _dotted_ref_name(ref)
                raise CompileError(f"Missing imported declaration: {dotted_name}")
            return unit, decl

        target_unit = unit.imported_units.get(ref.module_parts)
        if target_unit is None:
            raise CompileError(f"Missing import module: {'.'.join(ref.module_parts)}")

        registry = getattr(target_unit, registry_name)
        decl = registry.get(ref.declaration_name)
        if decl is None:
            dotted_name = _dotted_ref_name(ref)
            raise CompileError(f"Missing imported declaration: {dotted_name}")
        return target_unit, decl

    def _expr_ref_matches_review_verdict(self, ref: model.ExprRef) -> bool:
        return (
            len(ref.parts) == 2
            and ref.parts[0] == "ReviewVerdict"
            and ref.parts[1] in _REVIEW_VERDICT_TEXT
        )

    def _display_ref(self, ref: model.NameRef, *, unit: IndexedUnit) -> str:
        try:
            lookup_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        except CompileError:
            lookup_unit = None
        if lookup_unit is not None:
            matches = self._find_readable_decl_matches(ref.declaration_name, unit=lookup_unit)
            if len(matches) == 1:
                return self._display_readable_decl(matches[0][1])
        if ref.module_parts:
            return ".".join((*ref.module_parts, ref.declaration_name))
        return _humanize_key(ref.declaration_name)

    def _try_resolve_enum_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
    ) -> model.EnumDecl | None:
        try:
            lookup_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        except CompileError:
            return None
        return lookup_unit.enums_by_name.get(ref.declaration_name)

    def _find_readable_decl_matches(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, ReadableDecl], ...]:
        matches: list[tuple[str, ReadableDecl]] = []
        for label, registry_name in _READABLE_DECL_REGISTRIES:
            decl = getattr(unit, registry_name).get(declaration_name)
            if decl is not None:
                matches.append((label, decl))
        return tuple(matches)

    def _find_addressable_root_matches(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, AddressableRootDecl], ...]:
        matches: list[tuple[str, AddressableRootDecl]] = []
        for label, registry_name in _ADDRESSABLE_ROOT_REGISTRIES:
            decl = getattr(unit, registry_name).get(declaration_name)
            if decl is not None:
                matches.append((label, decl))
        return tuple(matches)

    def _display_readable_decl(self, decl: ReadableDecl) -> str:
        if isinstance(decl, model.Agent):
            return decl.title or _humanize_key(decl.name)
        return decl.title
