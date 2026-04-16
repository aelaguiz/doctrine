from __future__ import annotations

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.naming import (
    _authored_slot_allows_law,
    _authored_slot_carries_route_semantics,
)
from doctrine._compiler.review_diagnostics import review_related_site
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
from doctrine._compiler.workflow_diagnostics import (
    workflow_compile_error,
    workflow_related_site,
)


class ValidateAgentsMixin:
    """Agent-specific validation helpers for ValidateMixin."""

    def _agent_slot_source_span(
        self,
        agent: model.Agent,
        *,
        slot_key: str,
    ) -> model.SourceSpan | None:
        field = next(
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
                and field.key == slot_key
            ),
            None,
        )
        return None if field is None else field.source_span

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
            self._ensure_concrete_review_decl(
                review_decl,
                unit=review_unit,
                owner_unit=unit,
                attached_review_span=field.source_span,
            )
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
                        unit=unit,
                    ),
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=f"agent {agent.name} slot {slot_key}",
                )
                continue
            if not _authored_slot_allows_law(slot_key):
                raise workflow_compile_error(
                    code="E345",
                    summary="Law is not allowed on this authored slot",
                    detail=(
                        f"`law:` is not allowed on authored slot `{slot_key}` in "
                        f"agent {agent.name}."
                    ),
                    unit=unit,
                    source_span=self._agent_slot_source_span(agent, slot_key=slot_key)
                    or slot_body.law.source_span,
                    hints=(
                        "Attach `law:` only to `workflow:` or `handoff_routing:`.",
                        "Keep other authored slots as readable instruction surfaces.",
                    ),
                )

    def _route_semantic_sources_for_agent(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
        resolved_slots: dict[str, ResolvedWorkflowBody],
        agent_contract: AgentContract,
    ) -> tuple[tuple[str, RouteSemanticContext, model.SourceSpan | None], ...]:
        sources: list[tuple[str, RouteSemanticContext, model.SourceSpan | None]] = []
        review_field = next(
            (field for field in agent.fields if isinstance(field, model.ReviewField)),
            None,
        )
        if review_field is not None:
            review_unit, review_decl = self._resolve_review_ref(review_field.value, unit=unit)
            self._ensure_concrete_review_decl(
                review_decl,
                unit=review_unit,
                owner_unit=unit,
                attached_review_span=review_field.source_span,
            )
            review_context = self._route_semantic_context_from_review_decl(
                review_decl,
                unit=review_unit,
                agent_contract=agent_contract,
                owner_label=f"agent {agent.name} review",
            )
            if review_context is not None:
                sources.append(("review", review_context, review_field.source_span))

        workflow_body = resolved_slots.get("workflow")
        if workflow_body is not None and workflow_body.law is not None:
            workflow_context = self._route_semantic_context_from_law_body(
                workflow_body.law,
                unit=unit,
                owner_label=f"agent {agent.name} workflow",
            )
            if workflow_context is not None:
                sources.append(
                    (
                        "workflow",
                        workflow_context,
                        self._agent_slot_source_span(agent, slot_key="workflow")
                        or workflow_body.law.source_span,
                    )
                )

        for slot_key, slot_body in resolved_slots.items():
            if slot_key == "workflow":
                continue
            if not _authored_slot_carries_route_semantics(slot_key) or slot_body.law is None:
                continue
            slot_context = self._route_semantic_context_from_law_body(
                slot_body.law,
                unit=unit,
                owner_label=f"agent {agent.name} slot {slot_key}",
            )
            if slot_context is not None:
                sources.append(
                    (
                        slot_key,
                        slot_context,
                        self._agent_slot_source_span(agent, slot_key=slot_key)
                        or slot_body.law.source_span,
                    )
                )

        return tuple(sources)

    def _ensure_concrete_review_decl(
        self,
        review_decl: model.ReviewDecl,
        *,
        unit: IndexedUnit,
        owner_unit: IndexedUnit,
        attached_review_span: model.SourceSpan | None,
    ) -> None:
        if review_decl.abstract:
            dotted_name = _dotted_decl_name(unit.module_parts, review_decl.name)
            raise compile_error(
                code="E494",
                summary="Concrete agent may not attach abstract review directly",
                detail=f"Concrete agent may not attach abstract review `{dotted_name}` directly.",
                path=owner_unit.prompt_file.source_path,
                source_span=attached_review_span,
                related=(
                    review_related_site(
                        label=f"abstract review `{dotted_name}`",
                        unit=unit,
                        source_span=review_decl.source_span,
                    ),
                ),
            )

    def _raise_route_semantic_conflict(
        self,
        *,
        agent_name: str,
        unit: IndexedUnit,
        sources: tuple[tuple[str, model.SourceSpan | None], ...],
    ) -> None:
        labels = ", ".join(source for source, _source_span in sources)
        primary_source, primary_source_span = sources[-1]
        related = tuple(
            workflow_related_site(
                label=f"live `{source}` route-bearing surface",
                unit=unit,
                source_span=source_span,
            )
            for source, source_span in sources[:-1]
        )
        raise workflow_compile_error(
            code="E343",
            summary="Multiple route-bearing control surfaces are live",
            detail=(
                f"Agent `{agent_name}` has more than one live route-bearing control "
                f"surface: {labels}."
            ),
            unit=unit,
            source_span=primary_source_span,
            related=related,
            hints=(
                "Keep shared `route.*` truth on exactly one surface per concrete turn.",
                "Use exactly one of `workflow:`, `review:`, `handoff_routing:`, or `final_output.route:` to supply route semantics.",
            ),
        )

    def _route_semantic_context_for_agent(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
        resolved_slots: dict[str, ResolvedWorkflowBody],
        agent_contract: AgentContract,
    ) -> RouteSemanticContext | None:
        sources = self._route_semantic_sources_for_agent(
            agent,
            unit=unit,
            resolved_slots=resolved_slots,
            agent_contract=agent_contract,
        )
        if len(sources) > 1:
            self._raise_route_semantic_conflict(
                agent_name=agent.name,
                unit=unit,
                sources=tuple(
                    (source, source_span)
                    for source, _context, source_span in sources
                ),
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
            agent_contract=agent_contract,
        )
        output_contexts: set[tuple[OutputDeclKey, RouteSemanticContext]] = set()
        if context is not None:
            output_contexts.update((output_key, context) for output_key in emitted_output_keys)

        final_output_field = next(
            (field for field in agent.fields if isinstance(field, model.FinalOutputField)),
            None,
        )
        if final_output_field is None or final_output_field.route_path is None:
            return frozenset(output_contexts)

        review_field = next(
            (field for field in agent.fields if isinstance(field, model.ReviewField)),
            None,
        )
        if review_field is not None:
            raise compile_error(
                code="E299",
                summary="Compile failure",
                detail=(
                    f"final_output.route is not supported on review-driven agents in v1: "
                    f"{agent.name}"
                ),
                path=unit.prompt_file.source_path,
                source_span=final_output_field.source_span,
                related=(
                    workflow_related_site(
                        label="attached `review` field",
                        unit=unit,
                        source_span=review_field.source_span,
                    ),
                ),
            )

        sources = self._route_semantic_sources_for_agent(
            agent,
            unit=unit,
            resolved_slots=resolved_slots,
            agent_contract=agent_contract,
        )
        if sources:
            self._raise_route_semantic_conflict(
                agent_name=agent.name,
                unit=unit,
                sources=tuple(
                    (source, source_span)
                    for source, _context, source_span in sources
                )
                + (("final_output.route", final_output_field.source_span),),
            )

        binding = self._resolve_final_output_route_binding(
            agent_name=agent.name,
            field=final_output_field,
            unit=unit,
            agent_contract=agent_contract,
        )
        if binding is None:
            return frozenset(output_contexts)
        output_contexts.add(
            (
                binding.output_key,
                self._route_semantic_context_from_final_output_route_binding(
                    binding,
                    owner_label=f"agent {agent.name} final_output.route",
                ),
            )
        )
        return frozenset(output_contexts)

    def _route_output_context_for_key(
        self,
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]],
        output_key: OutputDeclKey,
    ) -> RouteSemanticContext | None:
        for key, context in route_output_contexts:
            if key == output_key:
                return context
        return None
