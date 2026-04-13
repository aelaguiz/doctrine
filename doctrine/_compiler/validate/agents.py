from __future__ import annotations

from doctrine import model
from doctrine._compiler.naming import (
    _authored_slot_allows_law,
    _authored_slot_carries_route_semantics,
)
from doctrine._compiler.resolved_types import (
    AgentContract,
    CompileError,
    IndexedUnit,
    OutputDeclKey,
    ResolvedWorkflowBody,
    ReviewContractGate,
    ReviewSemanticContext,
    RouteSemanticContext,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ValidateAgentsMixin:
    """Agent-specific validation helpers for ValidateMixin."""

    def _review_output_contexts_for_agent(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
    ) -> frozenset[tuple[OutputDeclKey, ReviewSemanticContext]]:
        output_contexts: set[tuple[OutputDeclKey, ReviewSemanticContext]] = set()
        for field in agent.fields:
            if not isinstance(field, model.ReviewField):
                continue
            review_unit, review_decl = self._resolve_review_ref(field.value, unit=unit)
            resolved = self._resolve_review_decl(review_decl, unit=review_unit)
            if resolved.comment_output is None:
                continue
            output_unit, output_decl = self._resolve_output_decl(
                resolved.comment_output.output_ref,
                unit=review_unit,
            )
            contract_gates: tuple[ReviewContractGate, ...] = ()
            if resolved.cases:
                collected: list[ReviewContractGate] = []
                seen_gate_keys: set[str] = set()
                for case in resolved.cases:
                    try:
                        case_gates = self._resolve_review_contract_spec(
                            case.contract.contract_ref,
                            unit=review_unit,
                            owner_label=(
                                f"review {_dotted_decl_name(review_unit.module_parts, review_decl.name)}"
                            ),
                        ).gates
                    except CompileError:
                        continue
                    for gate in case_gates:
                        if gate.key in seen_gate_keys:
                            continue
                        seen_gate_keys.add(gate.key)
                        collected.append(gate)
                contract_gates = tuple(collected)
            elif resolved.contract is not None:
                try:
                    contract_gates = self._resolve_review_contract_spec(
                        resolved.contract.contract_ref,
                        unit=review_unit,
                        owner_label=(
                            f"review {_dotted_decl_name(review_unit.module_parts, review_decl.name)}"
                        ),
                    ).gates
                except CompileError:
                    contract_gates = ()
            field_bindings: list[tuple[str, tuple[str, ...]]] = []
            seen_bindings: set[str] = set()
            if resolved.fields is not None:
                for binding in resolved.fields.bindings:
                    if binding.semantic_field in seen_bindings:
                        continue
                    seen_bindings.add(binding.semantic_field)
                    field_bindings.append((binding.semantic_field, binding.field_path))
            output_contexts.add(
                (
                    (output_unit.module_parts, output_decl.name),
                    ReviewSemanticContext(
                        review_module_parts=review_unit.module_parts,
                        output_module_parts=output_unit.module_parts,
                        output_name=output_decl.name,
                        field_bindings=tuple(field_bindings),
                        contract_gates=contract_gates,
                    ),
                )
            )
        return frozenset(output_contexts)

    def _review_output_context_for_key(
        self,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
        output_key: OutputDeclKey,
    ) -> ReviewSemanticContext | None:
        for key, context in review_output_contexts:
            if key == output_key:
                return context
        return None

    def _primary_review_output_context(
        self,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
    ) -> tuple[OutputDeclKey, ReviewSemanticContext] | None:
        if not review_output_contexts:
            return None
        return sorted(
            review_output_contexts,
            key=lambda item: _dotted_decl_name(item[0][0], item[0][1]),
        )[0]

    def _validate_agent_slot_laws(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
        resolved_slots: dict[str, ResolvedWorkflowBody],
        agent_contract: AgentContract,
    ) -> None:
        for slot_key, slot_body in resolved_slots.items():
            if slot_body.law is None:
                continue
            if slot_key == "workflow":
                continue
            if slot_key == "handoff_routing":
                self._validate_handoff_routing_law(
                    self._flatten_law_items(
                        slot_body.law,
                        owner_label=f"agent {agent.name} slot {slot_key}",
                    ),
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=f"agent {agent.name} slot {slot_key}",
                )
                continue
            if not _authored_slot_allows_law(slot_key):
                raise CompileError(
                    f"law may appear only on workflow or handoff_routing in agent {agent.name}: {slot_key}"
                )

    def _route_semantic_sources_for_agent(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
        resolved_slots: dict[str, ResolvedWorkflowBody],
    ) -> tuple[tuple[str, RouteSemanticContext], ...]:
        sources: list[tuple[str, RouteSemanticContext]] = []
        review_fields = [field for field in agent.fields if isinstance(field, model.ReviewField)]
        if review_fields:
            review_unit, review_decl = self._resolve_review_ref(review_fields[0].value, unit=unit)
            review_context = self._route_semantic_context_from_review_decl(
                review_decl,
                unit=review_unit,
            )
            if review_context is not None:
                sources.append(("review", review_context))

        workflow_body = resolved_slots.get("workflow")
        if workflow_body is not None and workflow_body.law is not None:
            workflow_context = self._route_semantic_context_from_law_body(
                workflow_body.law,
                unit=unit,
                owner_label=f"agent {agent.name} workflow",
            )
            if workflow_context is not None:
                sources.append(("workflow", workflow_context))

        for slot_key, slot_body in resolved_slots.items():
            if not _authored_slot_carries_route_semantics(slot_key) or slot_body.law is None:
                continue
            slot_context = self._route_semantic_context_from_law_body(
                slot_body.law,
                unit=unit,
                owner_label=f"agent {agent.name} slot {slot_key}",
            )
            if slot_context is not None:
                sources.append((slot_key, slot_context))

        return tuple(sources)

    def _route_semantic_context_for_agent(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
        resolved_slots: dict[str, ResolvedWorkflowBody],
    ) -> RouteSemanticContext | None:
        sources = self._route_semantic_sources_for_agent(
            agent,
            unit=unit,
            resolved_slots=resolved_slots,
        )
        if len(sources) > 1:
            labels = ", ".join(source for source, _context in sources)
            raise CompileError(
                f"Multiple route-bearing control surfaces are live in agent {agent.name}: {labels}"
            )
        if not sources:
            return None
        return sources[0][1]

    def _route_output_contexts_for_agent(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
        resolved_slots: dict[str, ResolvedWorkflowBody],
        agent_contract: AgentContract,
    ) -> frozenset[tuple[OutputDeclKey, RouteSemanticContext]]:
        emitted_output_keys = tuple(agent_contract.outputs.keys())
        if not emitted_output_keys:
            return frozenset()

        context = self._route_semantic_context_for_agent(
            agent,
            unit=unit,
            resolved_slots=resolved_slots,
        )
        if context is None:
            return frozenset()
        return frozenset((output_key, context) for output_key in emitted_output_keys)

    def _route_output_context_for_key(
        self,
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]],
        output_key: OutputDeclKey,
    ) -> RouteSemanticContext | None:
        for key, context in route_output_contexts:
            if key == output_key:
                return context
        return None
