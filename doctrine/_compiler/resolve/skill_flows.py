from __future__ import annotations

from collections.abc import Callable

from doctrine import model
from doctrine._compiler.indexing import unit_declarations
from doctrine._compiler.package_diagnostics import package_compile_error
from doctrine._compiler.resolved_types import CompileError, IndexedUnit
from doctrine._compiler.support import dotted_decl_name
from doctrine._model.skill_graph import (
    SKILL_FLOW_CHANGED_WORKFLOW_REQUIRES,
    SKILL_FLOW_EDGE_KINDS,
    SKILL_FLOW_REPEAT_ORDERS,
)


_SKILL_FLOW_INVALID_CODE = "E561"
_SKILL_FLOW_INVALID_SUMMARY = "Invalid skill flow"


class ResolveSkillFlowsMixin:
    """Top-level skill_flow resolution helpers for ResolveMixin.

    Sub-plan 3 lifts `skill_flow` from registry-only to a real flow-local
    declaration. The resolver:

      * normalizes the raw body into one resolved flow object
      * resolves `start:` and edge endpoints against top-level `stage`,
        top-level `skill_flow`, and local repeat names
      * validates edge `kind:` against the closed kind set
      * validates `route:` bindings against the resolved receipt route
        metadata produced by sub-plan 2
      * enforces the strict default: a routed source stage must bind the
        exact receipt route choice on every edge whose target the route
        choice names
      * validates `when:` and `safe_when:` branch refs against declared
        enum members
      * enforces local enum-branch coverage from one source node
      * resolves repeat targets and `over:` refs (top-level enum/table/
        schema in this slice)
      * checks repeat-name uniqueness and shadowing
      * lowers `variation`, `unsafe`, and `changed_workflow:` items into
        compiler-owned facts only

    Graph closure across flows, graph-set repeat refs, graph policies, and
    graph emit stay in sub-plan 4. Checked skill mentions stay in sub-plan
    5.
    """

    # ---- Public sweep -----------------------------------------------------

    def _validate_all_skill_flows_in_flow(self, flow) -> None:
        registry = getattr(flow, "skill_flows_by_name", None)
        if not registry:
            return
        validated_key = (flow.prompt_root.resolve(), flow.flow_root.resolve())
        cache = getattr(self, "_skill_flows_validated_flows", None)
        if cache is None:
            cache = set()
            object.__setattr__(self, "_skill_flows_validated_flows", cache)
        if validated_key in cache:
            return
        cache.add(validated_key)
        for flow_decl in registry.values():
            owner_unit = flow.declaration_owner_units_by_id[id(flow_decl)]
            self._resolve_skill_flow_decl(flow_decl, unit=owner_unit)

    # ---- Cache -----------------------------------------------------------

    def _resolved_skill_flow_cache(self):
        cache = getattr(self, "_resolved_skill_flow_decl_cache", None)
        if cache is None:
            cache = {}
            object.__setattr__(self, "_resolved_skill_flow_decl_cache", cache)
        return cache

    # ---- Owner label helper ---------------------------------------------

    def _skill_flow_owner_label(
        self,
        decl: model.SkillFlowDecl,
        *,
        unit: IndexedUnit,
    ) -> str:
        if unit.module_parts:
            return ".".join((*unit.module_parts, decl.name))
        return decl.name

    # ---- Resolution ------------------------------------------------------

    def _resolve_skill_flow_decl(
        self,
        flow_decl: model.SkillFlowDecl,
        *,
        unit: IndexedUnit,
        allow_graph_set_candidates: bool = False,
        allow_unbound_edges: bool = False,
        allow_incomplete_branch_coverage: bool = False,
        branch_coverage_warning_callback: Callable[
            [str, str, str, tuple[str, ...], object],
            None,
        ]
        | None = None,
    ) -> model.ResolvedSkillFlow:
        owner_label = self._skill_flow_owner_label(flow_decl, unit=unit)
        cache = self._resolved_skill_flow_cache()
        cache_key = (
            id(unit),
            flow_decl.name,
            allow_graph_set_candidates,
            allow_unbound_edges,
            allow_incomplete_branch_coverage,
        )
        cached = cache.get(cache_key)
        if cached is not None:
            if allow_incomplete_branch_coverage:
                self._emit_incomplete_branch_coverage_warnings(
                    edges=cached.edges,
                    unit=unit,
                    owner_label=owner_label,
                    warning_callback=branch_coverage_warning_callback,
                )
            return cached

        intent_items: list[model.SkillFlowIntentItem] = []
        start_items: list[model.SkillFlowStartItem] = []
        approve_items: list[model.SkillFlowApproveItem] = []
        edge_items: list[model.SkillFlowEdgeItem] = []
        repeat_items: list[model.SkillFlowRepeatItem] = []
        variation_items: list[model.SkillFlowVariationItem] = []
        unsafe_items: list[model.SkillFlowUnsafeItem] = []
        changed_items: list[model.SkillFlowChangedWorkflowItem] = []

        for item in flow_decl.items:
            if isinstance(item, model.SkillFlowIntentItem):
                intent_items.append(item)
            elif isinstance(item, model.SkillFlowStartItem):
                start_items.append(item)
            elif isinstance(item, model.SkillFlowApproveItem):
                approve_items.append(item)
            elif isinstance(item, model.SkillFlowEdgeItem):
                edge_items.append(item)
            elif isinstance(item, model.SkillFlowRepeatItem):
                repeat_items.append(item)
            elif isinstance(item, model.SkillFlowVariationItem):
                variation_items.append(item)
            elif isinstance(item, model.SkillFlowUnsafeItem):
                unsafe_items.append(item)
            elif isinstance(item, model.SkillFlowChangedWorkflowItem):
                changed_items.append(item)

        for label, items in (
            ("intent", intent_items),
            ("start", start_items),
            ("approve", approve_items),
            ("changed_workflow", changed_items),
        ):
            if len(items) > 1:
                raise self._skill_flow_error(
                    detail=(
                        f"Skill flow `{owner_label}` declares `{label}:` more "
                        "than once."
                    ),
                    unit=unit,
                    source_span=items[1].source_span or flow_decl.source_span,
                    hints=(f"Keep one `{label}:` block per skill flow.",),
                )

        intent = intent_items[0].value if intent_items else None

        # Resolve repeats first so node lookups can prefer local repeat names.
        resolved_repeats, repeats_by_name = self._resolve_skill_flow_repeats(
            repeat_items,
            flow_decl=flow_decl,
            unit=unit,
            owner_label=owner_label,
            allow_graph_set_candidates=allow_graph_set_candidates,
        )

        # Resolve start
        start_node: model.ResolvedSkillFlowNode | None = None
        if start_items:
            start_node = self._resolve_flow_node_ref(
                start_items[0].node_ref,
                unit=unit,
                owner_label=owner_label,
                repeats_by_name=repeats_by_name,
                source_span=start_items[0].source_span,
                role="start",
            )

        # Resolve approve (must point at a top-level skill_flow declaration).
        approve_name: str | None = None
        approve_module_parts: tuple[str, ...] = ()
        if approve_items:
            approve_ref = approve_items[0].flow_ref
            approve_unit, approve_decl = self._resolve_flow_skill_flow_ref(
                approve_ref,
                unit=unit,
                owner_label=owner_label,
                source_span=approve_items[0].source_span,
                role="approve",
            )
            approve_name = approve_decl.name
            approve_module_parts = approve_unit.module_parts

        # Resolve edges.
        resolved_edges, nodes_by_id = self._resolve_skill_flow_edges(
            edge_items,
            flow_decl=flow_decl,
            unit=unit,
            owner_label=owner_label,
            repeats_by_name=repeats_by_name,
            start_node=start_node,
            allow_unbound_edges=allow_unbound_edges,
        )

        # Local DAG check (after expansion just enough to flag cycles among
        # the directly authored edges in this flow).
        self._validate_skill_flow_dag(
            edges=resolved_edges,
            unit=unit,
            owner_label=owner_label,
            flow_decl=flow_decl,
        )

        # Branch coverage: every source that uses `when:` on any outgoing
        # edge must use the same enum family across all outgoing edges and
        # cover every member exactly once.
        self._validate_branch_coverage(
            edges=resolved_edges,
            edge_items=edge_items,
            unit=unit,
            owner_label=owner_label,
            allow_incomplete_coverage=allow_incomplete_branch_coverage,
            warning_callback=branch_coverage_warning_callback,
        )

        resolved_variations = self._resolve_skill_flow_variations(
            variation_items,
            flow_decl=flow_decl,
            unit=unit,
            owner_label=owner_label,
        )
        resolved_unsafe = self._resolve_skill_flow_unsafe(
            unsafe_items,
            flow_decl=flow_decl,
            unit=unit,
            owner_label=owner_label,
        )
        resolved_changed: model.ResolvedSkillFlowChangedWorkflow | None = None
        if changed_items:
            resolved_changed = self._resolve_changed_workflow(
                changed_items[0],
                flow_decl=flow_decl,
                unit=unit,
                owner_label=owner_label,
            )

        # Derive nodes (start + everything reached from edges + repeats).
        nodes: dict[tuple[str, str], model.ResolvedSkillFlowNode] = {}
        if start_node is not None:
            nodes[(start_node.kind, start_node.name)] = start_node
        for edge in resolved_edges:
            nodes[(edge.source.kind, edge.source.name)] = edge.source
            nodes[(edge.target.kind, edge.target.name)] = edge.target
        for repeat in resolved_repeats:
            key = ("repeat", repeat.name)
            if key not in nodes:
                nodes[key] = model.ResolvedSkillFlowNode(
                    name=repeat.name,
                    kind="repeat",
                    source_span=repeat.source_span,
                )

        terminals = self._derive_terminals(resolved_edges, nodes_by_id=nodes)

        resolved = model.ResolvedSkillFlow(
            canonical_name=flow_decl.name,
            title=flow_decl.title,
            intent=intent,
            start=start_node,
            approve=approve_name,
            nodes=tuple(nodes.values()),
            edges=resolved_edges,
            repeats=resolved_repeats,
            variations=resolved_variations,
            unsafe_variations=resolved_unsafe,
            changed_workflow=resolved_changed,
            terminals=terminals,
            approve_module_parts=approve_module_parts,
            source_span=flow_decl.source_span,
        )
        cache[cache_key] = resolved
        return resolved

    # ---- Repeats ---------------------------------------------------------

    def _resolve_skill_flow_repeats(
        self,
        repeat_items: list[model.SkillFlowRepeatItem],
        *,
        flow_decl: model.SkillFlowDecl,
        unit: IndexedUnit,
        owner_label: str,
        allow_graph_set_candidates: bool,
    ) -> tuple[
        tuple[model.ResolvedSkillFlowRepeat, ...],
        dict[str, model.ResolvedSkillFlowRepeat],
    ]:
        seen_names: dict[str, model.SkillFlowRepeatItem] = {}
        for item in repeat_items:
            if item.name in seen_names:
                raise self._skill_flow_error(
                    detail=(
                        f"Skill flow `{owner_label}` declares repeat name "
                        f"`{item.name}` more than once."
                    ),
                    unit=unit,
                    source_span=item.source_span or flow_decl.source_span,
                    hints=("Use a unique name for each `repeat` in a flow.",),
                )
            seen_names[item.name] = item

        # Repeat-name shadowing must surface before edge resolution because
        # nested flow refs and stage refs may share the same name space.
        decls = unit_declarations(unit)
        for name, item in seen_names.items():
            if name in decls.stages_by_name:
                raise self._skill_flow_error(
                    detail=(
                        f"Skill flow `{owner_label}` repeat `{name}` shadows "
                        "a top-level `stage` declaration."
                    ),
                    unit=unit,
                    source_span=item.source_span or flow_decl.source_span,
                    hints=(
                        "Pick a repeat name that does not collide with a "
                        "top-level `stage` name.",
                    ),
                )
            if name in decls.skill_flows_by_name:
                raise self._skill_flow_error(
                    detail=(
                        f"Skill flow `{owner_label}` repeat `{name}` shadows "
                        "a top-level `skill_flow` declaration."
                    ),
                    unit=unit,
                    source_span=item.source_span or flow_decl.source_span,
                    hints=(
                        "Pick a repeat name that does not collide with a "
                        "top-level `skill_flow` name.",
                    ),
                )

        resolved: list[model.ResolvedSkillFlowRepeat] = []
        repeats_by_name: dict[str, model.ResolvedSkillFlowRepeat] = {}
        for item in repeat_items:
            if item.order not in SKILL_FLOW_REPEAT_ORDERS:
                allowed = ", ".join(sorted(SKILL_FLOW_REPEAT_ORDERS))
                raise self._skill_flow_error(
                    detail=(
                        f"Skill flow `{owner_label}` repeat `{item.name}` "
                        f"declares `order: {item.order}`, but the closed "
                        f"value set is {{{allowed}}}."
                    ),
                    unit=unit,
                    source_span=item.source_span or flow_decl.source_span,
                    hints=(
                        "Use one of `serial`, `parallel`, or `unspecified`.",
                    ),
                )
            target_unit, target_flow = self._resolve_flow_skill_flow_ref(
                item.target_flow_ref,
                unit=unit,
                owner_label=owner_label,
                source_span=item.source_span,
                role="repeat target",
            )
            over_kind, over_name = self._resolve_repeat_over_ref(
                item.over_ref,
                unit=unit,
                owner_label=owner_label,
                source_span=item.source_span,
                repeat_name=item.name,
                allow_graph_set_candidates=allow_graph_set_candidates,
            )
            entry = model.ResolvedSkillFlowRepeat(
                name=item.name,
                target_flow_name=target_flow.name,
                over_kind=over_kind,
                over_name=over_name,
                order=item.order,
                why=item.why,
                target_flow_module_parts=target_unit.module_parts,
                source_span=item.source_span,
            )
            resolved.append(entry)
            repeats_by_name[item.name] = entry
        return tuple(resolved), repeats_by_name

    def _resolve_repeat_over_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span,
        repeat_name: str,
        allow_graph_set_candidates: bool,
    ) -> tuple[str, str]:
        # Local flow validation stays strict by default. Graph closure can
        # opt into late binding so unresolved names carry forward as graph-set
        # candidates instead of failing here.
        try:
            lookup_targets = self._decl_lookup_targets(ref, unit=unit)
        except CompileError:
            if allow_graph_set_candidates:
                return ("graph_set_candidate", self._dotted_ref(ref))
            raise
        for lookup_target in lookup_targets:
            target_decls = unit_declarations(lookup_target.unit)
            target_name = lookup_target.declaration_name
            if target_name in target_decls.enums_by_name:
                return ("enum", target_name)
            if target_name in target_decls.tables_by_name:
                return ("table", target_name)
            if target_name in target_decls.schemas_by_name:
                return ("schema", target_name)
        if allow_graph_set_candidates:
            return ("graph_set_candidate", self._dotted_ref(ref))
        dotted = self._dotted_ref(ref)
        raise self._skill_flow_error(
            detail=(
                f"Skill flow `{owner_label}` repeat `{repeat_name}` "
                f"declares `over: {dotted}`, but that name does not resolve "
                "to a top-level `enum`, `table`, or `schema` declaration."
            ),
            unit=unit,
            source_span=ref.source_span or source_span,
            hints=(
                "Sub-plan 3 limits `over:` to declared `enum`, `table`, or "
                "`schema` refs. Graph `sets:` arrive in a later slice.",
            ),
        )

    # ---- Edges -----------------------------------------------------------

    def _resolve_skill_flow_edges(
        self,
        edge_items: list[model.SkillFlowEdgeItem],
        *,
        flow_decl: model.SkillFlowDecl,
        unit: IndexedUnit,
        owner_label: str,
        repeats_by_name: dict[str, model.ResolvedSkillFlowRepeat],
        start_node: model.ResolvedSkillFlowNode | None,
        allow_unbound_edges: bool = False,
    ) -> tuple[
        tuple[model.ResolvedSkillFlowEdge, ...],
        dict[tuple[str, str], model.ResolvedSkillFlowNode],
    ]:
        nodes_by_id: dict[
            tuple[str, tuple[str, ...], str], model.ResolvedSkillFlowNode
        ] = {}
        if start_node is not None:
            nodes_by_id[self._flow_node_key(start_node)] = start_node
        resolved: list[model.ResolvedSkillFlowEdge] = []
        for item in edge_items:
            if item.kind not in SKILL_FLOW_EDGE_KINDS:
                allowed = ", ".join(sorted(SKILL_FLOW_EDGE_KINDS))
                raise self._skill_flow_error(
                    detail=(
                        f"Skill flow `{owner_label}` edge declares "
                        f"`kind: {item.kind}`, but the closed value set is "
                        f"{{{allowed}}}."
                    ),
                    unit=unit,
                    source_span=item.source_span or flow_decl.source_span,
                    hints=(
                        "Use one of `normal`, `review`, `repair`, "
                        "`recovery`, `approval`, or `handoff`.",
                    ),
                )
            source_node = self._resolve_flow_node_ref(
                item.source_ref,
                unit=unit,
                owner_label=owner_label,
                repeats_by_name=repeats_by_name,
                source_span=item.source_span,
                role="edge source",
            )
            target_node = self._resolve_flow_node_ref(
                item.target_ref,
                unit=unit,
                owner_label=owner_label,
                repeats_by_name=repeats_by_name,
                source_span=item.source_span,
                role="edge target",
            )
            if (
                source_node.kind == target_node.kind
                and source_node.name == target_node.name
                and source_node.module_parts == target_node.module_parts
            ):
                raise self._skill_flow_error(
                    detail=(
                        f"Skill flow `{owner_label}` edge `{source_node.name} "
                        f"-> {target_node.name}` is a direct self-reference."
                    ),
                    unit=unit,
                    source_span=item.source_span or flow_decl.source_span,
                    hints=(
                        "Direct self-edges are not allowed. Route the work "
                        "through a different node or remove the edge.",
                    ),
                )

            resolved_when: model.ResolvedSkillFlowEdgeWhen | None = None
            if item.when is not None:
                resolved_when = self._resolve_branch_when(
                    item.when,
                    unit=unit,
                    owner_label=owner_label,
                    source_span=item.source_span,
                    role="when",
                )

            resolved_route: model.ResolvedSkillFlowEdgeRouteBinding | None = (
                None
            )
            if item.route is not None:
                resolved_route = self._resolve_edge_route_binding(
                    item.route,
                    edge=item,
                    unit=unit,
                    owner_label=owner_label,
                    source_node=source_node,
                    target_node=target_node,
                )

            # Strict default: when the source stage emits a routed receipt
            # whose route choice points at the edge target, the edge must
            # bind that route choice exactly.
            if not allow_unbound_edges:
                self._enforce_required_route_binding(
                    edge=item,
                    unit=unit,
                    owner_label=owner_label,
                    source_node=source_node,
                    target_node=target_node,
                    resolved_route=resolved_route,
                )

            resolved.append(
                model.ResolvedSkillFlowEdge(
                    source=source_node,
                    target=target_node,
                    kind=item.kind,
                    why=item.why,
                    route=resolved_route,
                    when=resolved_when,
                    source_span=item.source_span,
                )
            )
            nodes_by_id[self._flow_node_key(source_node)] = source_node
            nodes_by_id[self._flow_node_key(target_node)] = target_node
        return tuple(resolved), nodes_by_id

    def _enforce_required_route_binding(
        self,
        *,
        edge: model.SkillFlowEdgeItem,
        unit: IndexedUnit,
        owner_label: str,
        source_node: model.ResolvedSkillFlowNode,
        target_node: model.ResolvedSkillFlowNode,
        resolved_route: model.ResolvedSkillFlowEdgeRouteBinding | None,
    ) -> None:
        # Only stage source nodes can emit routed receipts.
        if source_node.kind != "stage":
            return
        emitted_receipt = self._lookup_stage_emitted_receipt(
            stage_ref=edge.source_ref,
            unit=unit,
        )
        if emitted_receipt is None:
            return
        # Find any route choice that matches the edge target.
        matching: list[
            tuple[model.ResolvedReceiptRouteField, model.ResolvedReceiptRouteChoice]
        ] = []
        for route_field in emitted_receipt.routes:
            for choice in route_field.choices:
                if self._receipt_route_choice_matches_target(
                    choice, target_node=target_node
                ):
                    matching.append((route_field, choice))
        if not matching:
            return
        if resolved_route is None:
            field_choice_pairs = ", ".join(
                f"`{emitted_receipt.canonical_name}.{rf.key}.{ch.key}`"
                for rf, ch in matching
            )
            raise self._skill_flow_error(
                detail=(
                    f"Skill flow `{owner_label}` edge `{source_node.name} -> "
                    f"{target_node.name}` is unbound, but stage "
                    f"`{source_node.name}` emits routed receipt "
                    f"`{emitted_receipt.canonical_name}` whose route "
                    f"choices reach this target: {field_choice_pairs}."
                ),
                unit=unit,
                source_span=edge.source_span,
                hints=(
                    "Add `route: <ReceiptRef>.<route_field>.<choice>` so the "
                    "edge binds the exact authorized route choice.",
                ),
            )
        # Verify that the chosen route is one of the matching routes (not
        # for a different target).
        match_keys = {
            (rf.key, ch.key) for rf, ch in matching
        }
        if (resolved_route.route_field_key, resolved_route.choice_key) not in match_keys:
            raise self._skill_flow_error(
                detail=(
                    f"Skill flow `{owner_label}` edge `{source_node.name} -> "
                    f"{target_node.name}` declares `route: "
                    f"{resolved_route.receipt_name}."
                    f"{resolved_route.route_field_key}."
                    f"{resolved_route.choice_key}`, but that choice does "
                    "not target this edge target."
                ),
                unit=unit,
                source_span=edge.source_span,
                hints=(
                    "Pick a route choice on the source stage's emitted "
                    "receipt whose target matches the edge target.",
                ),
            )

    def _receipt_route_choice_matches_target(
        self,
        choice: model.ResolvedReceiptRouteChoice,
        *,
        target_node: model.ResolvedSkillFlowNode,
    ) -> bool:
        if target_node.kind == "stage":
            return (
                choice.target_kind == "stage"
                and choice.target_name == target_node.name
                and choice.target_module_parts == target_node.module_parts
            )
        if target_node.kind == "flow":
            return (
                choice.target_kind == "flow"
                and choice.target_name == target_node.name
                and choice.target_module_parts == target_node.module_parts
            )
        return False

    def _lookup_stage_emitted_receipt(
        self,
        *,
        stage_ref: model.NameRef | None = None,
        stage_name: str | None = None,
        unit: IndexedUnit,
    ) -> model.ResolvedReceipt | None:
        if stage_ref is not None:
            stage_unit, stage_decl = self._resolve_decl_ref(
                stage_ref,
                unit=unit,
                registry_name="stages_by_name",
                missing_label="stage declaration",
            )
        elif stage_name is not None:
            stage_unit = unit
            stage_decl = unit_declarations(unit).stages_by_name.get(stage_name)
            if stage_decl is None:
                return None
        else:
            return None
        emits_item: model.StageEmitsItem | None = None
        for item in stage_decl.items:
            if isinstance(item, model.StageEmitsItem):
                emits_item = item
                break
        if emits_item is None:
            return None
        receipt_ref = emits_item.receipt_ref
        try:
            receipt_unit, receipt_decl = self._resolve_decl_ref(
                receipt_ref,
                unit=stage_unit,
                registry_name="receipts_by_name",
                missing_label="receipt declaration",
            )
        except CompileError:
            return None
        return self._resolve_resolved_receipt(receipt_decl, unit=receipt_unit)

    def _resolve_edge_route_binding(
        self,
        route: model.SkillFlowEdgeRouteRef,
        *,
        edge: model.SkillFlowEdgeItem,
        unit: IndexedUnit,
        owner_label: str,
        source_node: model.ResolvedSkillFlowNode,
        target_node: model.ResolvedSkillFlowNode,
    ) -> model.ResolvedSkillFlowEdgeRouteBinding:
        receipt_ref = route.receipt_ref
        try:
            receipt_unit, receipt_decl = self._resolve_decl_ref(
                receipt_ref,
                unit=unit,
                registry_name="receipts_by_name",
                missing_label="receipt declaration",
            )
        except CompileError as exc:
            dotted = self._dotted_ref(receipt_ref)
            raise self._skill_flow_error(
                detail=(
                    f"Skill flow `{owner_label}` edge `{source_node.name} -> "
                    f"{target_node.name}` declares "
                    f"`route: {dotted}.{route.route_field_key}."
                    f"{route.choice_key}`, but `{dotted}` does not resolve "
                    "to a top-level `receipt` declaration."
                ),
                unit=unit,
                source_span=edge.source_span,
                hints=(
                    "Declare the receipt at the top level, or fix the "
                    "`route:` ref to point at one.",
                ),
            ) from exc
        resolved_receipt = self._resolve_resolved_receipt(receipt_decl, unit=receipt_unit)
        route_field: model.ResolvedReceiptRouteField | None = None
        for candidate in resolved_receipt.routes:
            if candidate.key == route.route_field_key:
                route_field = candidate
                break
        if route_field is None:
            raise self._skill_flow_error(
                detail=(
                    f"Skill flow `{owner_label}` edge `{source_node.name} -> "
                    f"{target_node.name}` declares "
                    f"`route: {resolved_receipt.canonical_name}."
                    f"{route.route_field_key}.{route.choice_key}`, but "
                    "receipt "
                    f"`{resolved_receipt.canonical_name}` has no route "
                    f"field `{route.route_field_key}`."
                ),
                unit=unit,
                source_span=edge.source_span,
                hints=(
                    "Add the route field to the receipt or fix the route "
                    "binding to name an existing field.",
                ),
            )
        choice: model.ResolvedReceiptRouteChoice | None = None
        for candidate_choice in route_field.choices:
            if candidate_choice.key == route.choice_key:
                choice = candidate_choice
                break
        if choice is None:
            raise self._skill_flow_error(
                detail=(
                    f"Skill flow `{owner_label}` edge `{source_node.name} -> "
                    f"{target_node.name}` declares "
                    f"`route: {resolved_receipt.canonical_name}."
                    f"{route_field.key}.{route.choice_key}`, but route "
                    f"field `{route_field.key}` has no choice "
                    f"`{route.choice_key}`."
                ),
                unit=unit,
                source_span=edge.source_span,
                hints=(
                    "Add the choice to the route field or fix the route "
                    "binding to name an existing choice.",
                ),
            )
        if not self._receipt_route_choice_matches_target(choice, target_node=target_node):
            actual_target_kind = choice.target_kind
            actual_target_name = dotted_decl_name(
                choice.target_module_parts,
                choice.target_name,
            )
            raise self._skill_flow_error(
                detail=(
                    f"Skill flow `{owner_label}` edge `{source_node.name} -> "
                    f"{target_node.name}` declares "
                    f"`route: {resolved_receipt.canonical_name}."
                    f"{route_field.key}.{choice.key}`, but that choice "
                    f"targets {actual_target_kind} `{actual_target_name}` "
                    "instead of the declared edge target."
                ),
                unit=unit,
                source_span=edge.source_span,
                hints=(
                    "Pick the route choice whose `-> <target>` matches the "
                    "edge target, or fix the edge target.",
                ),
            )
        return model.ResolvedSkillFlowEdgeRouteBinding(
            receipt_name=resolved_receipt.canonical_name,
            route_field_key=route_field.key,
            choice_key=choice.key,
            target_kind=choice.target_kind,
            target_name=choice.target_name,
            target_module_parts=choice.target_module_parts,
            source_span=route.source_span,
        )

    # ---- Branch coverage --------------------------------------------------

    def _validate_branch_coverage(
        self,
        *,
        edges: tuple[model.ResolvedSkillFlowEdge, ...],
        edge_items: list[model.SkillFlowEdgeItem],
        unit: IndexedUnit,
        owner_label: str,
        allow_incomplete_coverage: bool = False,
        warning_callback: Callable[[str, str, str, tuple[str, ...], object], None]
        | None = None,
    ) -> None:
        sources_with_when: dict[
            tuple[str, tuple[str, ...], str], list[model.ResolvedSkillFlowEdge]
        ] = {}
        sources_all: dict[
            tuple[str, tuple[str, ...], str], list[model.ResolvedSkillFlowEdge]
        ] = {}
        for edge in edges:
            key = self._flow_node_key(edge.source)
            sources_all.setdefault(key, []).append(edge)
            if edge.when is not None:
                sources_with_when.setdefault(key, []).append(edge)

        for source_key, branched in sources_with_when.items():
            enum_name = branched[0].when.enum_name
            enum_identity = branched[0].when.enum_identity or enum_name
            # all outgoing edges from this source must use `when:` and the
            # same enum.
            for edge in sources_all[source_key]:
                if edge.when is None:
                    raise self._skill_flow_error(
                        detail=(
                            f"Skill flow `{owner_label}` source "
                            f"`{edge.source.name}` mixes branched and "
                            "unbranched outgoing edges. Every outgoing edge "
                            "must declare `when: <Enum>.<member>`."
                        ),
                        unit=unit,
                        source_span=edge.source_span,
                        hints=(
                            "Add a `when:` to every outgoing edge from this "
                            "source, or remove the branching from the others.",
                        ),
                    )
                edge_enum_identity = edge.when.enum_identity or edge.when.enum_name
                if edge_enum_identity != enum_identity:
                    raise self._skill_flow_error(
                        detail=(
                            f"Skill flow `{owner_label}` source "
                            f"`{edge.source.name}` branches on enum "
                            f"`{enum_identity}` and `{edge_enum_identity}`. "
                            "Branch edges from one source must use one enum "
                            "family."
                        ),
                        unit=unit,
                        source_span=edge.source_span,
                        hints=(
                            "Pick one enum family for the branch and rewrite "
                            "the other edges accordingly.",
                        ),
                    )
            # Coverage: every enum member must appear exactly once.
            members = set(branched[0].when.enum_members)
            if not members:
                enum_decl = self._lookup_enum_decl(enum_name=enum_name, unit=unit)
                if enum_decl is None:
                    # Should not happen because resolve_branch_when checks this.
                    continue
                members = {member.key for member in enum_decl.members}
            seen: dict[str, model.ResolvedSkillFlowEdge] = {}
            for edge in branched:
                key = edge.when.member_key
                if key in seen:
                    raise self._skill_flow_error(
                        detail=(
                            f"Skill flow `{owner_label}` source "
                            f"`{edge.source.name}` branches on "
                            f"`{enum_name}.{key}` more than once."
                        ),
                        unit=unit,
                        source_span=edge.source_span,
                        hints=(
                            "Use each enum member exactly once across branch "
                            "edges from one source.",
                        ),
                    )
                seen[key] = edge
            missing = sorted(members - set(seen.keys()))
            if missing:
                if allow_incomplete_coverage:
                    self._emit_branch_coverage_warning(
                        owner_label=owner_label,
                        source_name=branched[0].source.name,
                        enum_name=enum_name,
                        missing=tuple(missing),
                        source_span=branched[0].source_span,
                        warning_callback=warning_callback,
                    )
                    continue
                missing_text = ", ".join(missing)
                raise self._skill_flow_error(
                    detail=(
                        f"Skill flow `{owner_label}` source "
                        f"`{branched[0].source.name}` branches on enum "
                        f"`{enum_name}` but does not cover member(s): "
                        f"{missing_text}."
                    ),
                    unit=unit,
                    source_span=branched[0].source_span,
                    hints=(
                        "Add one branch edge per missing enum member. "
                        "Sub-plan 3 has no `otherwise:` escape hatch.",
                    ),
                )

    def _emit_incomplete_branch_coverage_warnings(
        self,
        *,
        edges: tuple[model.ResolvedSkillFlowEdge, ...],
        unit: IndexedUnit,
        owner_label: str,
        warning_callback: Callable[[str, str, str, tuple[str, ...], object], None]
        | None,
    ) -> None:
        sources_with_when: dict[
            tuple[str, tuple[str, ...], str], list[model.ResolvedSkillFlowEdge]
        ] = {}
        for edge in edges:
            if edge.when is None:
                continue
            key = self._flow_node_key(edge.source)
            sources_with_when.setdefault(key, []).append(edge)
        for branched in sources_with_when.values():
            enum_name = branched[0].when.enum_name
            members = set(branched[0].when.enum_members)
            if not members:
                enum_decl = self._lookup_enum_decl(enum_name=enum_name, unit=unit)
                if enum_decl is None:
                    continue
                members = {member.key for member in enum_decl.members}
            seen = {edge.when.member_key for edge in branched}
            missing = tuple(sorted(members - seen))
            if not missing:
                continue
            self._emit_branch_coverage_warning(
                owner_label=owner_label,
                source_name=branched[0].source.name,
                enum_name=enum_name,
                missing=missing,
                source_span=branched[0].source_span,
                warning_callback=warning_callback,
            )

    def _emit_branch_coverage_warning(
        self,
        *,
        owner_label: str,
        source_name: str,
        enum_name: str,
        missing: tuple[str, ...],
        source_span,
        warning_callback: Callable[[str, str, str, tuple[str, ...], object], None]
        | None,
    ) -> None:
        if warning_callback is None:
            return
        warning_callback(owner_label, source_name, enum_name, missing, source_span)

    # ---- Branch ref resolution -------------------------------------------

    def _resolve_branch_when(
        self,
        when_ref: model.SkillFlowEdgeWhenRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span,
        role: str,
    ) -> model.ResolvedSkillFlowEdgeWhen:
        resolved_enum = self._try_resolve_enum_decl_with_unit(
            when_ref.enum_ref,
            unit=unit,
        )
        if resolved_enum is None:
            dotted = self._dotted_ref(when_ref.enum_ref)
            raise self._skill_flow_error(
                detail=(
                    f"Skill flow `{owner_label}` `{role}: "
                    f"{dotted}.{when_ref.member_key}` does not resolve to a "
                    "declared enum member."
                ),
                unit=unit,
                source_span=when_ref.source_span or source_span,
                hints=(
                    "Declare the enum at the top level, or fix the branch "
                    "ref to name an existing enum member.",
                ),
            )
        enum_unit, enum_decl = resolved_enum
        if not any(member.key == when_ref.member_key for member in enum_decl.members):
            raise self._skill_flow_error(
                detail=(
                    f"Skill flow `{owner_label}` `{role}: "
                    f"{enum_decl.name}.{when_ref.member_key}` names a "
                    f"member that is not on enum `{enum_decl.name}`."
                ),
                unit=unit,
                source_span=when_ref.source_span or source_span,
                hints=(
                    "Use one of the enum members declared on the branch enum.",
                ),
            )
        return model.ResolvedSkillFlowEdgeWhen(
            enum_name=enum_decl.name,
            member_key=when_ref.member_key,
            enum_identity=self._branch_enum_identity(enum_unit, enum_decl),
            enum_members=tuple(member.key for member in enum_decl.members),
            source_span=when_ref.source_span,
        )

    def _branch_enum_identity(
        self,
        enum_unit: IndexedUnit,
        enum_decl: model.EnumDecl,
    ) -> str:
        if enum_unit.module_parts:
            return ".".join((*enum_unit.module_parts, enum_decl.name))
        return enum_decl.name

    def _lookup_enum_decl(
        self,
        *,
        enum_name: str,
        unit: IndexedUnit,
    ) -> model.EnumDecl | None:
        decls = unit_declarations(unit)
        return decls.enums_by_name.get(enum_name)

    # ---- Variations and unsafe ------------------------------------------

    def _resolve_skill_flow_variations(
        self,
        items: list[model.SkillFlowVariationItem],
        *,
        flow_decl: model.SkillFlowDecl,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.ResolvedSkillFlowVariation, ...]:
        seen: set[str] = set()
        resolved: list[model.ResolvedSkillFlowVariation] = []
        for item in items:
            if item.name in seen:
                raise self._skill_flow_error(
                    detail=(
                        f"Skill flow `{owner_label}` declares variation "
                        f"`{item.name}` more than once."
                    ),
                    unit=unit,
                    source_span=item.source_span or flow_decl.source_span,
                    hints=("Use a unique name for each variation.",),
                )
            seen.add(item.name)
            safe_when: model.ResolvedSkillFlowEdgeWhen | None = None
            if item.safe_when is not None:
                safe_when = self._resolve_branch_when(
                    item.safe_when,
                    unit=unit,
                    owner_label=owner_label,
                    source_span=item.source_span,
                    role=f"variation `{item.name}` safe_when",
                )
            resolved.append(
                model.ResolvedSkillFlowVariation(
                    name=item.name,
                    title=item.title,
                    safe_when=safe_when,
                    source_span=item.source_span,
                )
            )
        return tuple(resolved)

    def _resolve_skill_flow_unsafe(
        self,
        items: list[model.SkillFlowUnsafeItem],
        *,
        flow_decl: model.SkillFlowDecl,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.ResolvedSkillFlowUnsafe, ...]:
        seen: set[str] = set()
        resolved: list[model.ResolvedSkillFlowUnsafe] = []
        for item in items:
            if item.name in seen:
                raise self._skill_flow_error(
                    detail=(
                        f"Skill flow `{owner_label}` declares unsafe "
                        f"variation `{item.name}` more than once."
                    ),
                    unit=unit,
                    source_span=item.source_span or flow_decl.source_span,
                    hints=("Use a unique name for each unsafe variation.",),
                )
            seen.add(item.name)
            resolved.append(
                model.ResolvedSkillFlowUnsafe(
                    name=item.name,
                    title=item.title,
                    source_span=item.source_span,
                )
            )
        return tuple(resolved)

    # ---- Changed workflow -----------------------------------------------

    def _resolve_changed_workflow(
        self,
        item: model.SkillFlowChangedWorkflowItem,
        *,
        flow_decl: model.SkillFlowDecl,
        unit: IndexedUnit,
        owner_label: str,
    ) -> model.ResolvedSkillFlowChangedWorkflow:
        for require_key in item.requires:
            if require_key not in SKILL_FLOW_CHANGED_WORKFLOW_REQUIRES:
                allowed = ", ".join(sorted(SKILL_FLOW_CHANGED_WORKFLOW_REQUIRES))
                raise self._skill_flow_error(
                    detail=(
                        f"Skill flow `{owner_label}` `changed_workflow:` "
                        f"requires unknown key `{require_key}`. The closed "
                        f"set is {{{allowed}}}."
                    ),
                    unit=unit,
                    source_span=item.source_span or flow_decl.source_span,
                    hints=(
                        "Use one of `nearest_flow`, `difference`, or "
                        "`safety_rationale`.",
                    ),
                )
        return model.ResolvedSkillFlowChangedWorkflow(
            allow_provisional_flow=item.allow_provisional_flow,
            requires=item.requires,
            source_span=item.source_span,
        )

    # ---- DAG validation --------------------------------------------------

    def _validate_skill_flow_dag(
        self,
        *,
        edges: tuple[model.ResolvedSkillFlowEdge, ...],
        unit: IndexedUnit,
        owner_label: str,
        flow_decl: model.SkillFlowDecl,
    ) -> None:
        # Build adjacency over local node ids and check for cycles. Repeat
        # nodes are templates and never close a cycle by themselves; an
        # edge that re-enters a stage from a repeat node is a real cycle.
        adjacency: dict[
            tuple[str, tuple[str, ...], str],
            list[tuple[tuple[str, tuple[str, ...], str], model.ResolvedSkillFlowEdge]],
        ] = {}
        for edge in edges:
            src = self._flow_node_key(edge.source)
            tgt = self._flow_node_key(edge.target)
            adjacency.setdefault(src, []).append((tgt, edge))

        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[tuple[str, tuple[str, ...], str], int] = {}
        cycle_edge: model.ResolvedSkillFlowEdge | None = None

        def visit(node: tuple[str, tuple[str, ...], str]) -> None:
            nonlocal cycle_edge
            color[node] = GRAY
            for tgt, edge in adjacency.get(node, ()):
                if cycle_edge is not None:
                    return
                state = color.get(tgt, WHITE)
                if state == GRAY:
                    cycle_edge = edge
                    return
                if state == WHITE:
                    visit(tgt)
                    if cycle_edge is not None:
                        return
            color[node] = BLACK

        for node in list(adjacency.keys()):
            if color.get(node, WHITE) == WHITE:
                visit(node)
                if cycle_edge is not None:
                    break

        if cycle_edge is not None:
            raise self._skill_flow_error(
                detail=(
                    f"Skill flow `{owner_label}` edges form a cycle through "
                    f"`{cycle_edge.source.name} -> {cycle_edge.target.name}`."
                ),
                unit=unit,
                source_span=cycle_edge.source_span or flow_decl.source_span,
                hints=(
                    "Sub-plan 3 expects a local DAG. Remove the cycle or "
                    "split the loop into a typed repeat node.",
                ),
            )

    # ---- Node ref resolution --------------------------------------------

    def _resolve_flow_node_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        repeats_by_name: dict[str, model.ResolvedSkillFlowRepeat],
        source_span,
        role: str,
    ) -> model.ResolvedSkillFlowNode:
        # Local repeat names take precedence over top-level stage and flow
        # refs, but only when the ref is bare (no module path).
        if not ref.module_parts and ref.declaration_name in repeats_by_name:
            repeat = repeats_by_name[ref.declaration_name]
            return model.ResolvedSkillFlowNode(
                name=repeat.name,
                kind="repeat",
                module_parts=(),
                source_span=ref.source_span,
            )

        # Try stage first.
        lookup_targets = self._decl_lookup_targets(ref, unit=unit)
        for lookup_target in lookup_targets:
            target_decls = unit_declarations(lookup_target.unit)
            target_name = lookup_target.declaration_name
            if target_name in target_decls.stages_by_name:
                return model.ResolvedSkillFlowNode(
                    name=target_name,
                    kind="stage",
                    module_parts=lookup_target.unit.module_parts,
                    source_span=ref.source_span,
                )
            if target_name in target_decls.skill_flows_by_name:
                return model.ResolvedSkillFlowNode(
                    name=target_name,
                    kind="flow",
                    module_parts=lookup_target.unit.module_parts,
                    source_span=ref.source_span,
                )
        dotted = self._dotted_ref(ref)
        raise self._skill_flow_error(
            detail=(
                f"Skill flow `{owner_label}` {role} `{dotted}` does not "
                "resolve to a top-level `stage`, top-level `skill_flow`, or "
                "a local `repeat` name."
            ),
            unit=unit,
            source_span=ref.source_span or source_span,
            hints=(
                "Declare the target at the top level, fix the ref, or add a "
                "matching `repeat` block.",
            ),
        )

    def _resolve_flow_skill_flow_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        source_span,
        role: str,
    ) -> tuple[IndexedUnit, model.SkillFlowDecl]:
        try:
            return self._resolve_decl_ref(
                ref,
                unit=unit,
                registry_name="skill_flows_by_name",
                missing_label="skill_flow declaration",
            )
        except CompileError as exc:
            dotted = self._dotted_ref(ref)
            raise self._skill_flow_error(
                detail=(
                    f"Skill flow `{owner_label}` {role} ref `{dotted}` does "
                    "not resolve to a top-level `skill_flow` declaration."
                ),
                unit=unit,
                source_span=ref.source_span or source_span,
                hints=(
                    "Declare the `skill_flow` at the top level, or fix the "
                    "ref.",
                ),
            ) from exc

    # ---- Terminal derivation --------------------------------------------

    def _derive_terminals(
        self,
        edges: tuple[model.ResolvedSkillFlowEdge, ...],
        *,
        nodes_by_id: dict[tuple[str, tuple[str, ...], str], model.ResolvedSkillFlowNode],
    ) -> tuple[str, ...]:
        sources = {self._flow_node_key(edge.source) for edge in edges}
        terminals: list[str] = []
        seen: set[tuple[tuple[str, ...], str]] = set()
        for edge in edges:
            key = self._flow_node_key(edge.target)
            if key in sources:
                continue
            terminal_key = (edge.target.module_parts, edge.target.name)
            if terminal_key in seen:
                continue
            seen.add(terminal_key)
            terminals.append(edge.target.name)
        return tuple(terminals)

    # ---- Helpers --------------------------------------------------------

    def _flow_node_key(
        self,
        node: model.ResolvedSkillFlowNode,
    ) -> tuple[str, tuple[str, ...], str]:
        return (node.kind, node.module_parts, node.name)

    def _dotted_ref(self, ref: model.NameRef) -> str:
        if ref.module_parts:
            return ".".join((*ref.module_parts, ref.declaration_name))
        return ref.declaration_name

    def _skill_flow_error(
        self,
        *,
        detail: str,
        unit: IndexedUnit,
        source_span,
        hints: tuple[str, ...] = (),
    ):
        return package_compile_error(
            code=_SKILL_FLOW_INVALID_CODE,
            summary=_SKILL_FLOW_INVALID_SUMMARY,
            detail=detail,
            path=unit.prompt_file.source_path,
            source_span=source_span,
            hints=hints,
        )
