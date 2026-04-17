from __future__ import annotations

from doctrine import model
from doctrine._compiler.authored_diagnostics import (
    authored_compile_error,
    authored_related_site,
)
from doctrine._compiler.naming import _dotted_ref_name, _humanize_key
from doctrine._compiler.reference_diagnostics import (
    reference_compile_error,
    reference_related_site,
)
from doctrine._compiler.resolved_types import (
    CompileError,
    IndexedUnit,
    ResolvedAbstractAgentSlot,
    ResolvedAgentSlot,
    ResolvedAgentSlotState,
    ResolvedWorkflowBody,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveAgentSlotsMixin:
    """Agent-slot and authored workflow resolution helpers for ResolveMixin."""

    def _authored_slot_field_by_key(
        self,
        fields: tuple[model.Field, ...],
        key: str,
    ) -> (
        model.AuthoredSlotField
        | model.AuthoredSlotAbstract
        | model.AuthoredSlotInherit
        | model.AuthoredSlotOverride
        | None
    ):
        return next(
            (
                field
                for field in fields
                if isinstance(
                    field,
                    (
                        model.AuthoredSlotField,
                        model.AuthoredSlotAbstract,
                        model.AuthoredSlotInherit,
                        model.AuthoredSlotOverride,
                    ),
                )
                and field.key == key
            ),
            None,
        )

    def _authored_slot_related_site(
        self,
        *,
        label: str,
        unit: IndexedUnit | None,
        source_span: model.SourceSpan | None,
    ):
        if unit is None or source_span is None:
            return ()
        return (
            authored_related_site(
                label=label,
                unit=unit,
                source_span=source_span,
            ),
        )

    def _missing_authored_slot_related_sites(
        self,
        *,
        parent_unit: IndexedUnit | None,
        parent_agent: model.Agent | None,
        missing_keys: tuple[str, ...],
    ) -> tuple:
        if parent_unit is None or parent_agent is None:
            return ()
        related = []
        for key in missing_keys:
            parent_field = self._authored_slot_field_by_key(parent_agent.fields, key)
            if parent_field is None or parent_field.source_span is None:
                continue
            related.append(
                authored_related_site(
                    label=f"inherited `{key}` slot",
                    unit=parent_unit,
                    source_span=parent_field.source_span,
                )
            )
        return tuple(related)

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
            raise authored_compile_error(
                code="E207",
                summary="Cyclic agent inheritance",
                detail=f"Cyclic agent inheritance: {cycle}",
                unit=unit,
                source_span=agent.source_span,
            )

        self._agent_slot_resolution_stack.append(agent_key)
        try:
            parent_slots: tuple[ResolvedAgentSlotState, ...] = ()
            parent_unit: IndexedUnit | None = None
            parent_agent: model.Agent | None = None
            parent_label: str | None = None
            if agent.parent_ref is not None:
                parent_unit, parent_agent = self._resolve_parent_agent_decl(agent, unit=unit)
                parent_slots = self._resolve_agent_slots(parent_agent, unit=parent_unit)
                parent_label = f"agent {_dotted_decl_name(parent_unit.module_parts, parent_agent.name)}"

            parent_slots_by_key = {slot.key: slot for slot in parent_slots}
            resolved_slots: list[ResolvedAgentSlotState] = []
            seen_slot_fields: dict[
                str,
                model.AuthoredSlotField
                | model.AuthoredSlotAbstract
                | model.AuthoredSlotInherit
                | model.AuthoredSlotOverride,
            ] = {}
            accounted_parent_concrete_keys: set[str] = set()

            for field in agent.fields:
                if isinstance(field, model.AuthoredSlotField):
                    self._ensure_valid_authored_slot_key(
                        field.key,
                        agent.name,
                        unit=unit,
                        source_span=field.source_span,
                    )
                    first_field = seen_slot_fields.get(field.key)
                    if first_field is not None:
                        raise authored_compile_error(
                            code="E299",
                            summary="Compile failure",
                            detail=f"Duplicate authored slot key in agent {agent.name}: {field.key}",
                            unit=unit,
                            source_span=field.source_span,
                            related=self._authored_slot_related_site(
                                label=f"first `{field.key}` slot",
                                unit=unit,
                                source_span=first_field.source_span,
                            ),
                        )
                    seen_slot_fields[field.key] = field

                    parent_slot = parent_slots_by_key.get(field.key)
                    if isinstance(parent_slot, ResolvedAgentSlot):
                        if field.key == "workflow" and isinstance(field.value, model.WorkflowBody):
                            resolved_body = self._resolve_workflow_body(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot workflow",
                                owner_source_span=field.source_span,
                                parent_workflow=parent_slot.body,
                                parent_body=None,
                                parent_unit=parent_unit,
                                parent_label=f"{parent_label} slot workflow",
                            )
                            accounted_parent_concrete_keys.add(field.key)
                            resolved_slots.append(
                                ResolvedAgentSlot(key=field.key, body=resolved_body)
                            )
                            continue
                        parent_field = (
                            None
                            if parent_agent is None
                            else self._authored_slot_field_by_key(parent_agent.fields, field.key)
                        )
                        raise authored_compile_error(
                            code="E299",
                            summary="Compile failure",
                            detail=(
                                f"Inherited authored slot requires `inherit {field.key}` or "
                                f"`override {field.key}` in agent {agent.name}"
                            ),
                            unit=unit,
                            source_span=field.source_span,
                            related=self._authored_slot_related_site(
                                label=f"inherited `{field.key}` slot",
                                unit=parent_unit,
                                source_span=(
                                    None if parent_field is None else parent_field.source_span
                                ),
                            ),
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        resolved_slots.append(
                            ResolvedAgentSlot(
                                key=field.key,
                                body=self._resolve_slot_value(
                                    field.value,
                                    unit=unit,
                                    owner_label=f"agent {agent.name} slot {field.key}",
                                    owner_source_span=field.source_span,
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
                                owner_source_span=field.source_span,
                            ),
                        )
                    )
                    continue

                if isinstance(field, model.AuthoredSlotAbstract):
                    self._ensure_valid_authored_slot_key(
                        field.key,
                        agent.name,
                        unit=unit,
                        source_span=field.source_span,
                    )
                    first_field = seen_slot_fields.get(field.key)
                    if first_field is not None:
                        raise authored_compile_error(
                            code="E299",
                            summary="Compile failure",
                            detail=f"Duplicate authored slot key in agent {agent.name}: {field.key}",
                            unit=unit,
                            source_span=field.source_span,
                            related=self._authored_slot_related_site(
                                label=f"first `{field.key}` slot",
                                unit=unit,
                                source_span=first_field.source_span,
                            ),
                        )
                    seen_slot_fields[field.key] = field
                    parent_slot = parent_slots_by_key.get(field.key)
                    if isinstance(parent_slot, ResolvedAgentSlot):
                        accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(ResolvedAbstractAgentSlot(key=field.key))
                    continue

                if isinstance(field, model.AuthoredSlotInherit):
                    self._ensure_valid_authored_slot_key(
                        field.key,
                        agent.name,
                        unit=unit,
                        source_span=field.source_span,
                    )
                    first_field = seen_slot_fields.get(field.key)
                    if first_field is not None:
                        raise authored_compile_error(
                            code="E299",
                            summary="Compile failure",
                            detail=f"Duplicate authored slot key in agent {agent.name}: {field.key}",
                            unit=unit,
                            source_span=field.source_span,
                            related=self._authored_slot_related_site(
                                label=f"first `{field.key}` slot",
                                unit=unit,
                                source_span=first_field.source_span,
                            ),
                        )
                    seen_slot_fields[field.key] = field
                    parent_slot = parent_slots_by_key.get(field.key)
                    if parent_slot is None:
                        label = parent_label or f"agent {agent.name}"
                        raise authored_compile_error(
                            code="E299",
                            summary="Compile failure",
                            detail=f"Cannot inherit undefined authored slot in {label}: {field.key}",
                            unit=unit,
                            source_span=field.source_span,
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        label = parent_label or f"agent {agent.name}"
                        parent_field = (
                            None
                            if parent_agent is None
                            else self._authored_slot_field_by_key(parent_agent.fields, field.key)
                        )
                        raise authored_compile_error(
                            code="E210",
                            summary="Abstract authored slot must be defined directly",
                            detail=(
                                f"Abstract authored slot in {label} must be defined directly "
                                f"in agent {agent.name}: {field.key}. "
                                f"`inherit {field.key}` cannot satisfy abstract authored slot."
                            ),
                            unit=unit,
                            source_span=field.source_span,
                            related=self._authored_slot_related_site(
                                label=f"abstract `{field.key}` slot",
                                unit=parent_unit,
                                source_span=(
                                    None if parent_field is None else parent_field.source_span
                                ),
                            ),
                            hints=("Define the slot directly with `slot_key: ...`.",),
                        )
                    accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(parent_slot)
                    continue

                if isinstance(field, model.AuthoredSlotOverride):
                    self._ensure_valid_authored_slot_key(
                        field.key,
                        agent.name,
                        unit=unit,
                        source_span=field.source_span,
                    )
                    first_field = seen_slot_fields.get(field.key)
                    if first_field is not None:
                        raise authored_compile_error(
                            code="E299",
                            summary="Compile failure",
                            detail=f"Duplicate authored slot key in agent {agent.name}: {field.key}",
                            unit=unit,
                            source_span=field.source_span,
                            related=self._authored_slot_related_site(
                                label=f"first `{field.key}` slot",
                                unit=unit,
                                source_span=first_field.source_span,
                            ),
                        )
                    seen_slot_fields[field.key] = field
                    parent_slot = parent_slots_by_key.get(field.key)
                    if parent_slot is None:
                        label = parent_label or f"agent {agent.name}"
                        raise authored_compile_error(
                            code="E001",
                            summary="Cannot override undefined inherited entry",
                            detail=f"Cannot override undefined authored slot in {label}: {field.key}",
                            unit=unit,
                            source_span=field.source_span,
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        label = parent_label or f"agent {agent.name}"
                        parent_field = (
                            None
                            if parent_agent is None
                            else self._authored_slot_field_by_key(parent_agent.fields, field.key)
                        )
                        raise authored_compile_error(
                            code="E210",
                            summary="Abstract authored slot must be defined directly",
                            detail=(
                                f"Abstract authored slot in {label} must be defined directly "
                                f"in agent {agent.name}: {field.key}. "
                                f"`override {field.key}` cannot satisfy abstract authored slot."
                            ),
                            unit=unit,
                            source_span=field.source_span,
                            related=self._authored_slot_related_site(
                                label=f"abstract `{field.key}` slot",
                                unit=parent_unit,
                                source_span=(
                                    None if parent_field is None else parent_field.source_span
                                ),
                            ),
                            hints=("Define the slot directly with `slot_key: ...`.",),
                        )
                    accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(
                        ResolvedAgentSlot(
                            key=field.key,
                            body=self._resolve_slot_value(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot {field.key}",
                                owner_source_span=field.source_span,
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
                raise authored_compile_error(
                    code="E003",
                    summary="Missing inherited entry",
                    detail=f"Missing inherited authored slot in agent {agent.name}: {missing}",
                    unit=unit,
                    source_span=agent.source_span,
                    related=self._missing_authored_slot_related_sites(
                        parent_unit=parent_unit,
                        parent_agent=parent_agent,
                        missing_keys=tuple(missing_parent_keys),
                    ),
                )

            for parent_slot in parent_slots:
                if (
                    isinstance(parent_slot, ResolvedAbstractAgentSlot)
                    and parent_slot.key not in seen_slot_fields
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
        owner_source_span: model.SourceSpan | None,
    ) -> ResolvedWorkflowBody:
        if isinstance(value, model.WorkflowBody):
            return self._resolve_workflow_body(
                value,
                unit=unit,
                owner_label=owner_label,
                owner_source_span=owner_source_span,
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
            raise authored_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"route_only is missing facts: {decl.name}",
                unit=unit,
                source_span=decl.source_span,
            )
        self._resolve_route_only_facts_decl(
            facts_ref,
            unit=unit,
            owner_label=owner_label,
        )
        if not decl.body.current_none:
            raise authored_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"route_only must declare `current none`: {decl.name}",
                unit=unit,
                source_span=decl.source_span,
            )
        if decl.body.handoff_output_ref is None:
            raise authored_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"route_only is missing handoff_output: {decl.name}",
                unit=unit,
                source_span=decl.source_span,
            )
        output_unit, output_decl = self._resolve_output_decl(
            decl.body.handoff_output_ref,
            unit=unit,
        )
        self._validate_route_only_guarded_output(
            output_decl,
            unit=unit,
            output_unit=output_unit,
            facts_ref=facts_ref,
            guarded=decl.body.guarded,
            owner_label=owner_label,
        )
        if not decl.body.routes:
            raise authored_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"route_only must declare at least one route: {decl.name}",
                unit=unit,
                source_span=decl.source_span,
            )

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
            raise authored_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"grounding is missing target: {decl.name}",
                unit=unit,
                source_span=decl.source_span,
            )

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
        lookup_targets = self._decl_lookup_targets(ref, unit=unit)
        matches: list[tuple[object, IndexedUnit, model.InputDecl | model.OutputDecl]] = []
        for lookup_target in lookup_targets:
            input_decl = lookup_target.unit.inputs_by_name.get(lookup_target.declaration_name)
            output_decl = self._resolve_local_output_decl(
                lookup_target.declaration_name,
                unit=lookup_target.unit,
            )
            if input_decl is not None and output_decl is not None:
                raise reference_compile_error(
                    code="E270",
                    summary="Ambiguous declaration reference",
                    detail=f"Ambiguous route_only facts in {owner_label}: {_dotted_ref_name(ref)}",
                    unit=unit,
                    source_span=ref.source_span,
                    related=tuple(
                        related
                        for related in (
                            reference_related_site(
                                label="input declaration",
                                unit=lookup_target.unit,
                                source_span=input_decl.source_span,
                            ),
                            reference_related_site(
                                label="output declaration",
                                unit=lookup_target.unit,
                                source_span=output_decl.source_span,
                            ),
                        )
                        if related.location.line is not None
                    ),
                )
            decl = input_decl if input_decl is not None else output_decl
            if decl is not None:
                matches.append((lookup_target, lookup_target.unit, decl))
        if len(matches) > 1:
            imported_target = next(
                (
                    lookup_target
                    for lookup_target, _target_unit, _decl in matches
                    if lookup_target.imported_symbol is not None
                ),
                None,
            )
            if imported_target is not None:
                local_decl = next(
                    (
                        decl
                        for lookup_target, _target_unit, decl in matches
                        if lookup_target.imported_symbol is None
                    ),
                    None,
                )
                self._raise_imported_symbol_ambiguity(
                    ref,
                    unit=unit,
                    binding=imported_target.imported_symbol,
                    detail=(
                        f"route_only facts `{ref.declaration_name}` in {owner_label} "
                        "matches both local and imported declarations."
                    ),
                    local_decl=local_decl,
                )
        if not matches:
            raise reference_compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"route_only facts must resolve to an input or output declaration in "
                    f"{owner_label}: {_dotted_ref_name(ref)}"
                ),
                unit=unit,
                source_span=ref.source_span,
            )
        _lookup_target, target_unit, decl = matches[0]
        return target_unit, decl
