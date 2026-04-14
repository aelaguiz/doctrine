from __future__ import annotations

from doctrine import model
from doctrine._compiler.naming import _dotted_ref_name, _humanize_key
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
