from __future__ import annotations

from dataclasses import dataclass, field

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.resolved_types import CompileError, IndexedUnit


@dataclass(slots=True)
class _NodeExpansion:
    start_stages: tuple[str, ...] = ()
    terminal_stages: tuple[str, ...] = ()
    reached_stage_names: set[str] = field(default_factory=set)
    reached_flow_names: set[str] = field(default_factory=set)
    stage_edges: list[model.ResolvedSkillGraphStageEdge] = field(default_factory=list)
    stage_reaching_flows: dict[str, set[str]] = field(default_factory=dict)


@dataclass(slots=True)
class _FlowExpansion:
    graph_flow: model.ResolvedSkillGraphFlow
    owner_unit: IndexedUnit
    start_stages: tuple[str, ...]
    terminal_stages: tuple[str, ...]
    reached_stage_names: tuple[str, ...]
    reached_flow_names: tuple[str, ...]
    stage_edges: tuple[model.ResolvedSkillGraphStageEdge, ...]
    stage_reaching_flows: dict[str, tuple[str, ...]]


class ResolveSkillGraphsMixin:
    """Top-level skill_graph resolution helpers for ResolveMixin."""

    def _resolved_skill_graph_cache(self):
        cache = getattr(self, "_resolved_skill_graph_decl_cache", None)
        if cache is None:
            cache = {}
            object.__setattr__(self, "_resolved_skill_graph_decl_cache", cache)
        return cache

    def _skill_graph_error(
        self,
        *,
        detail: str,
        unit: IndexedUnit,
        source_span,
        hints: tuple[str, ...] = (),
    ) -> CompileError:
        return compile_error(
            code="E562",
            summary="Invalid skill graph",
            detail=detail,
            path=unit.prompt_file.source_path,
            source_span=source_span,
            hints=hints,
        )

    def _resolve_skill_graph_decl(
        self,
        graph_decl: model.SkillGraphDecl,
        *,
        unit: IndexedUnit,
    ) -> model.ResolvedSkillGraph:
        cache = self._resolved_skill_graph_cache()
        cache_key = (id(unit), graph_decl.name)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        owner_label = (
            ".".join((*unit.module_parts, graph_decl.name))
            if unit.module_parts
            else graph_decl.name
        )
        purpose_items: list[model.SkillGraphPurposeItem] = []
        roots_items: list[model.SkillGraphRootsItem] = []
        sets_items: list[model.SkillGraphSetsItem] = []
        recovery_items: list[model.SkillGraphRecoveryItem] = []
        policy_items: list[model.SkillGraphPolicyItem] = []
        views_items: list[model.SkillGraphViewsItem] = []
        for item in graph_decl.items:
            if isinstance(item, model.SkillGraphPurposeItem):
                purpose_items.append(item)
            elif isinstance(item, model.SkillGraphRootsItem):
                roots_items.append(item)
            elif isinstance(item, model.SkillGraphSetsItem):
                sets_items.append(item)
            elif isinstance(item, model.SkillGraphRecoveryItem):
                recovery_items.append(item)
            elif isinstance(item, model.SkillGraphPolicyItem):
                policy_items.append(item)
            elif isinstance(item, model.SkillGraphViewsItem):
                views_items.append(item)

        for label, items in (
            ("purpose", purpose_items),
            ("roots", roots_items),
            ("sets", sets_items),
            ("recovery", recovery_items),
            ("policy", policy_items),
            ("views", views_items),
        ):
            if len(items) > 1:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` declares `{label}:` more "
                        "than once."
                    ),
                    unit=unit,
                    source_span=items[1].source_span or graph_decl.source_span,
                    hints=(f"Keep one `{label}:` block per skill graph.",),
                )

        if not purpose_items:
            raise self._skill_graph_error(
                detail=f"Skill graph `{owner_label}` is missing required `purpose:`.",
                unit=unit,
                source_span=graph_decl.source_span,
                hints=("Add `purpose: \"...\"` to state what this graph owns.",),
            )
        if not roots_items:
            raise self._skill_graph_error(
                detail=f"Skill graph `{owner_label}` is missing required `roots:`.",
                unit=unit,
                source_span=graph_decl.source_span,
                hints=(
                    "Add one or more `flow <Ref>` or `stage <Ref>` lines under `roots:`.",
                ),
            )

        graph_sets = self._resolve_skill_graph_sets(
            sets_items[0] if sets_items else None,
            unit=unit,
            owner_label=owner_label,
            graph_decl=graph_decl,
        )
        set_names = {entry.name for entry in graph_sets}
        graph_policies = self._resolve_skill_graph_policies(
            policy_items[0] if policy_items else None,
            unit=unit,
            owner_label=owner_label,
            graph_decl=graph_decl,
        )
        graph_views = self._resolve_skill_graph_views(
            views_items[0] if views_items else None,
            unit=unit,
            owner_label=owner_label,
            graph_decl=graph_decl,
        )
        graph_recovery = self._resolve_skill_graph_recovery(
            recovery_items[0] if recovery_items else None,
            unit=unit,
            owner_label=owner_label,
            graph_decl=graph_decl,
        )
        graph_roots, root_decls = self._resolve_skill_graph_roots(
            roots_items[0],
            unit=unit,
            owner_label=owner_label,
            graph_decl=graph_decl,
        )

        flow_cache: dict[tuple[int, str], _FlowExpansion] = {}
        flow_stack: list[tuple[int, str]] = []
        reached_stage_order: list[str] = []
        reached_stage_seen: set[str] = set()
        reached_stage_units: dict[str, IndexedUnit] = {}
        reached_stage_decls: dict[str, model.StageDecl] = {}
        reached_flow_order: list[str] = []
        reached_flow_seen: set[str] = set()
        reached_flow_units: dict[str, IndexedUnit] = {}
        reached_skill_units: dict[str, IndexedUnit] = {}
        reached_skill_decls: dict[str, model.SkillDecl] = {}
        reached_package_units: dict[str, IndexedUnit] = {}
        reached_package_decls: dict[str, model.SkillPackageDecl] = {}
        reached_receipt_units: dict[str, IndexedUnit] = {}
        reached_receipt_decls: dict[str, model.ReceiptDecl] = {}
        aggregate_edges: list[model.ResolvedSkillGraphStageEdge] = []
        aggregate_stage_reaching_flows: dict[str, set[str]] = {}

        def remember_stage(
            stage_name: str,
            *,
            owner_unit: IndexedUnit,
            stage_decl: model.StageDecl,
        ) -> None:
            if stage_name not in reached_stage_seen:
                reached_stage_seen.add(stage_name)
                reached_stage_order.append(stage_name)
            reached_stage_units.setdefault(stage_name, owner_unit)
            reached_stage_decls.setdefault(stage_name, stage_decl)

        def remember_flow(flow_name: str, *, owner_unit: IndexedUnit) -> None:
            if flow_name not in reached_flow_seen:
                reached_flow_seen.add(flow_name)
                reached_flow_order.append(flow_name)
            reached_flow_units.setdefault(flow_name, owner_unit)

        def remember_receipt(
            receipt_name: str,
            *,
            owner_unit: IndexedUnit,
            receipt_decl: model.ReceiptDecl,
        ) -> None:
            reached_receipt_units.setdefault(receipt_name, owner_unit)
            reached_receipt_decls.setdefault(receipt_name, receipt_decl)

        def remember_skill(
            skill_name: str,
            *,
            owner_unit: IndexedUnit,
            skill_decl: model.SkillDecl,
        ) -> None:
            reached_skill_units.setdefault(skill_name, owner_unit)
            reached_skill_decls.setdefault(skill_name, skill_decl)
            if skill_decl.package_link is None:
                return
            package_unit, package_decl = self._resolve_skill_package_id(
                skill_decl.package_link.package_id,
                unit=owner_unit,
                owner_label=f"skill `{skill_decl.name}` package link",
                source_span=skill_decl.package_link.source_span,
            )
            package_id = skill_decl.package_link.package_id
            reached_package_units.setdefault(package_id, package_unit)
            reached_package_decls.setdefault(package_id, package_decl)

        def merge_node_expansion(dest: _NodeExpansion, src: _NodeExpansion) -> None:
            dest.reached_stage_names.update(src.reached_stage_names)
            dest.reached_flow_names.update(src.reached_flow_names)
            dest.stage_edges.extend(src.stage_edges)
            for stage_name, flow_names in src.stage_reaching_flows.items():
                dest.stage_reaching_flows.setdefault(stage_name, set()).update(flow_names)

        def augment_with_parent_flow(
            expansion: _FlowExpansion,
            *,
            parent_flow_name: str,
        ) -> _NodeExpansion:
            stage_reaching_flows = {
                stage_name: set(flow_names)
                for stage_name, flow_names in expansion.stage_reaching_flows.items()
            }
            for stage_name in expansion.reached_stage_names:
                stage_reaching_flows.setdefault(stage_name, set()).add(parent_flow_name)
            return _NodeExpansion(
                start_stages=expansion.start_stages,
                terminal_stages=expansion.terminal_stages,
                reached_stage_names=set(expansion.reached_stage_names),
                reached_flow_names=set(expansion.reached_flow_names),
                stage_edges=list(expansion.stage_edges),
                stage_reaching_flows=stage_reaching_flows,
            )

        def resolve_stage_by_name(
            stage_name: str,
            *,
            current_unit: IndexedUnit,
            source_span,
            role: str,
        ) -> tuple[IndexedUnit, model.StageDecl]:
            ref = model.NameRef(
                module_parts=(),
                declaration_name=stage_name,
                source_span=source_span,
            )
            try:
                return self._resolve_decl_ref(
                    ref,
                    unit=current_unit,
                    registry_name="stages_by_name",
                    missing_label="stage declaration",
                )
            except CompileError as exc:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` {role} stage `{stage_name}` "
                        "does not resolve to a top-level `stage` declaration."
                    ),
                    unit=current_unit,
                    source_span=source_span,
                    hints=("Declare the stage at the top level, or fix the ref.",),
                ) from exc

        def resolve_flow_by_name(
            flow_name: str,
            *,
            current_unit: IndexedUnit,
            source_span,
            role: str,
        ) -> tuple[IndexedUnit, model.SkillFlowDecl]:
            ref = model.NameRef(
                module_parts=(),
                declaration_name=flow_name,
                source_span=source_span,
            )
            try:
                return self._resolve_decl_ref(
                    ref,
                    unit=current_unit,
                    registry_name="skill_flows_by_name",
                    missing_label="skill_flow declaration",
                )
            except CompileError as exc:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` {role} flow `{flow_name}` "
                        "does not resolve to a top-level `skill_flow` declaration."
                    ),
                    unit=current_unit,
                    source_span=source_span,
                    hints=("Declare the flow at the top level, or fix the ref.",),
                ) from exc

        def resolve_receipt_by_name(
            receipt_name: str,
            *,
            current_unit: IndexedUnit,
            source_span,
            role: str,
        ) -> tuple[IndexedUnit, model.ReceiptDecl]:
            ref = model.NameRef(
                module_parts=(),
                declaration_name=receipt_name,
                source_span=source_span,
            )
            try:
                return self._resolve_receipt_ref(ref, unit=current_unit)
            except CompileError as exc:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` {role} receipt `{receipt_name}` "
                        "does not resolve to a top-level `receipt` declaration."
                    ),
                    unit=current_unit,
                    source_span=source_span,
                    hints=("Declare the receipt at the top level, or fix the ref.",),
                ) from exc

        def resolve_stage_dependencies(
            stage_decl: model.StageDecl,
            *,
            owner_unit: IndexedUnit,
        ) -> None:
            stage_label = self._stage_owner_label(stage_decl, unit=owner_unit)
            for item in stage_decl.items:
                if isinstance(item, model.StageOwnerItem):
                    skill_unit, skill_decl = self._resolve_stage_skill_ref(
                        item.owner_ref,
                        unit=owner_unit,
                        owner_label=stage_label,
                        role="owner",
                        error_code="E546",
                    )
                    remember_skill(skill_decl.name, owner_unit=skill_unit, skill_decl=skill_decl)
                elif isinstance(item, model.StageSupportsItem):
                    for support_ref in item.skill_refs:
                        skill_unit, skill_decl = self._resolve_stage_skill_ref(
                            support_ref,
                            unit=owner_unit,
                            owner_label=stage_label,
                            role="support",
                            error_code="E547",
                        )
                        remember_skill(
                            skill_decl.name,
                            owner_unit=skill_unit,
                            skill_decl=skill_decl,
                        )

            resolved_stage = self._resolve_stage_decl(stage_decl, unit=owner_unit)
            for input_entry in resolved_stage.inputs:
                if input_entry.type_kind != "receipt":
                    continue
                receipt_unit, receipt_decl = resolve_receipt_by_name(
                    input_entry.type_name,
                    current_unit=owner_unit,
                    source_span=stage_decl.source_span,
                    role="stage input",
                )
                remember_receipt(
                    receipt_decl.name,
                    owner_unit=receipt_unit,
                    receipt_decl=receipt_decl,
                )
            if resolved_stage.emits_receipt_name is not None:
                receipt_unit, receipt_decl = resolve_receipt_by_name(
                    resolved_stage.emits_receipt_name,
                    current_unit=owner_unit,
                    source_span=stage_decl.source_span,
                    role="stage emit",
                )
                remember_receipt(
                    receipt_decl.name,
                    owner_unit=receipt_unit,
                    receipt_decl=receipt_decl,
                )

        def node_expansion(
            node: model.ResolvedSkillFlowNode,
            *,
            current_unit: IndexedUnit,
            current_flow_name: str,
            graph_flow: model.ResolvedSkillGraphFlow,
        ) -> _NodeExpansion:
            if node.kind == "stage":
                stage_unit, stage_decl = resolve_stage_by_name(
                    node.name,
                    current_unit=current_unit,
                    source_span=node.source_span,
                    role="reached",
                )
                remember_stage(node.name, owner_unit=stage_unit, stage_decl=stage_decl)
                resolve_stage_dependencies(stage_decl, owner_unit=stage_unit)
                return _NodeExpansion(
                    start_stages=(node.name,),
                    terminal_stages=(node.name,),
                    reached_stage_names={node.name},
                    stage_reaching_flows={node.name: {current_flow_name}},
                )
            if node.kind == "flow":
                child_unit, child_decl = resolve_flow_by_name(
                    node.name,
                    current_unit=current_unit,
                    source_span=node.source_span,
                    role="reached",
                )
                child = expand_flow(child_decl, owner_unit=child_unit)
                return augment_with_parent_flow(child, parent_flow_name=current_flow_name)
            repeat = next(
                (entry for entry in graph_flow.repeats if entry.name == node.name),
                None,
            )
            if repeat is None:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` cannot expand repeat "
                        f"`{node.name}` because the flow repeat metadata is missing."
                    ),
                    unit=current_unit,
                    source_span=node.source_span,
                    hints=("This is a compiler bug, not an authoring error.",),
                )
            child_unit, child_decl = resolve_flow_by_name(
                repeat.target_flow_name,
                current_unit=current_unit,
                source_span=node.source_span,
                role="repeat target",
            )
            child = expand_flow(child_decl, owner_unit=child_unit)
            return augment_with_parent_flow(child, parent_flow_name=current_flow_name)

        def flow_terminal_nodes(
            graph_flow: model.ResolvedSkillGraphFlow,
        ) -> tuple[model.ResolvedSkillFlowNode, ...]:
            if not graph_flow.nodes:
                return tuple()
            incoming = {(edge.target.kind, edge.target.name) for edge in graph_flow.edges}
            outgoing = {(edge.source.kind, edge.source.name) for edge in graph_flow.edges}
            if not graph_flow.edges:
                if graph_flow.start is not None:
                    return (graph_flow.start,)
                return tuple(graph_flow.nodes)
            terminal_nodes = tuple(
                node
                for node in graph_flow.nodes
                if (node.kind, node.name) not in outgoing
            )
            if terminal_nodes:
                return terminal_nodes
            if graph_flow.start is not None:
                return (graph_flow.start,)
            return tuple(
                node
                for node in graph_flow.nodes
                if (node.kind, node.name) not in incoming
            )

        def expand_flow(
            flow_decl: model.SkillFlowDecl,
            *,
            owner_unit: IndexedUnit,
        ) -> _FlowExpansion:
            cache_key = (id(owner_unit), flow_decl.name)
            cached_flow = flow_cache.get(cache_key)
            if cached_flow is not None:
                return cached_flow
            if cache_key in flow_stack:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` expands flow `{flow_decl.name}` "
                        "through a nested flow cycle."
                    ),
                    unit=owner_unit,
                    source_span=flow_decl.source_span,
                    hints=(
                        "Break the nested flow cycle, or rewrite the loop as a typed repeat.",
                    ),
                )
            flow_stack.append(cache_key)
            try:
                resolved_flow = self._resolve_skill_flow_decl(
                    flow_decl,
                    unit=owner_unit,
                    allow_graph_set_candidates=True,
                )
                graph_repeats: list[model.ResolvedSkillGraphRepeat] = []
                for repeat in resolved_flow.repeats:
                    over_kind = repeat.over_kind
                    if over_kind == "graph_set_candidate":
                        if repeat.over_name not in set_names:
                            raise self._skill_graph_error(
                                detail=(
                                    f"Skill graph `{owner_label}` repeat "
                                    f"`{repeat.name}` in flow `{flow_decl.name}` "
                                    f"uses graph set `{repeat.over_name}`, but "
                                    "that set is not declared under `sets:`."
                                ),
                                unit=owner_unit,
                                source_span=repeat.source_span or flow_decl.source_span,
                                hints=(
                                    "Declare the graph set under `sets:`, or point `over:` at a declared enum, table, or schema.",
                                ),
                            )
                        over_kind = "graph_set"
                    graph_repeats.append(
                        model.ResolvedSkillGraphRepeat(
                            name=repeat.name,
                            target_flow_name=repeat.target_flow_name,
                            over_kind=over_kind,
                            over_name=repeat.over_name,
                            order=repeat.order,
                            why=repeat.why,
                            source_span=repeat.source_span,
                        )
                    )
                graph_flow = model.ResolvedSkillGraphFlow(
                    canonical_name=resolved_flow.canonical_name,
                    title=resolved_flow.title,
                    intent=resolved_flow.intent,
                    start=resolved_flow.start,
                    approve=resolved_flow.approve,
                    nodes=resolved_flow.nodes,
                    edges=resolved_flow.edges,
                    repeats=tuple(graph_repeats),
                    variations=resolved_flow.variations,
                    unsafe_variations=resolved_flow.unsafe_variations,
                    changed_workflow=resolved_flow.changed_workflow,
                    terminals=resolved_flow.terminals,
                    source_span=resolved_flow.source_span,
                )
                remember_flow(flow_decl.name, owner_unit=owner_unit)

                result = _NodeExpansion()
                if graph_flow.start is not None:
                    start_expansion = node_expansion(
                        graph_flow.start,
                        current_unit=owner_unit,
                        current_flow_name=flow_decl.name,
                        graph_flow=graph_flow,
                    )
                    if not result.start_stages:
                        result.start_stages = start_expansion.start_stages
                    merge_node_expansion(result, start_expansion)
                elif graph_flow.nodes:
                    incoming = {
                        (edge.target.kind, edge.target.name)
                        for edge in graph_flow.edges
                    }
                    start_nodes = tuple(
                        node
                        for node in graph_flow.nodes
                        if (node.kind, node.name) not in incoming
                    )
                    start_stages: list[str] = []
                    for start_node in start_nodes:
                        start_expansion = node_expansion(
                            start_node,
                            current_unit=owner_unit,
                            current_flow_name=flow_decl.name,
                            graph_flow=graph_flow,
                        )
                        merge_node_expansion(result, start_expansion)
                        for stage_name in start_expansion.start_stages:
                            if stage_name not in start_stages:
                                start_stages.append(stage_name)
                    result.start_stages = tuple(start_stages)

                for edge in graph_flow.edges:
                    source_expansion = node_expansion(
                        edge.source,
                        current_unit=owner_unit,
                        current_flow_name=flow_decl.name,
                        graph_flow=graph_flow,
                    )
                    target_expansion = node_expansion(
                        edge.target,
                        current_unit=owner_unit,
                        current_flow_name=flow_decl.name,
                        graph_flow=graph_flow,
                    )
                    merge_node_expansion(result, source_expansion)
                    merge_node_expansion(result, target_expansion)
                    for source_stage in source_expansion.terminal_stages:
                        for target_stage in target_expansion.start_stages:
                            result.stage_edges.append(
                                model.ResolvedSkillGraphStageEdge(
                                    source_stage_name=source_stage,
                                    target_stage_name=target_stage,
                                    via_flow_name=flow_decl.name,
                                    kind=edge.kind,
                                    why=edge.why,
                                    route_receipt_name=(
                                        None if edge.route is None else edge.route.receipt_name
                                    ),
                                    route_field_key=(
                                        None if edge.route is None else edge.route.route_field_key
                                    ),
                                    route_choice_key=(
                                        None if edge.route is None else edge.route.choice_key
                                    ),
                                    source_span=edge.source_span,
                                )
                            )
                            if edge.route is not None:
                                receipt_unit, receipt_decl = resolve_receipt_by_name(
                                    edge.route.receipt_name,
                                    current_unit=owner_unit,
                                    source_span=edge.source_span,
                                    role="route binding",
                                )
                                remember_receipt(
                                    receipt_decl.name,
                                    owner_unit=receipt_unit,
                                    receipt_decl=receipt_decl,
                                )

                terminal_nodes = flow_terminal_nodes(graph_flow)
                terminal_stages: list[str] = []
                for terminal_node in terminal_nodes:
                    terminal_expansion = node_expansion(
                        terminal_node,
                        current_unit=owner_unit,
                        current_flow_name=flow_decl.name,
                        graph_flow=graph_flow,
                    )
                    merge_node_expansion(result, terminal_expansion)
                    for stage_name in terminal_expansion.terminal_stages:
                        if stage_name not in terminal_stages:
                            terminal_stages.append(stage_name)

                if graph_flow.approve is not None:
                    approve_unit, approve_decl = resolve_flow_by_name(
                        graph_flow.approve,
                        current_unit=owner_unit,
                        source_span=graph_flow.source_span,
                        role="approve",
                    )
                    approve_expansion = expand_flow(approve_decl, owner_unit=approve_unit)
                    approve_node = augment_with_parent_flow(
                        approve_expansion,
                        parent_flow_name=flow_decl.name,
                    )
                    merge_node_expansion(result, approve_node)
                    for source_stage in terminal_stages:
                        for target_stage in approve_node.start_stages:
                            result.stage_edges.append(
                                model.ResolvedSkillGraphStageEdge(
                                    source_stage_name=source_stage,
                                    target_stage_name=target_stage,
                                    via_flow_name=flow_decl.name,
                                    kind="approval",
                                    why=(
                                        f"Approval flow `{graph_flow.approve}` runs after "
                                        f"`{flow_decl.name}`."
                                    ),
                                    source_span=graph_flow.source_span,
                                )
                            )
                    terminal_stages = list(approve_node.terminal_stages)

                result.terminal_stages = tuple(terminal_stages)
                expansion = _FlowExpansion(
                    graph_flow=graph_flow,
                    owner_unit=owner_unit,
                    start_stages=result.start_stages,
                    terminal_stages=result.terminal_stages,
                    reached_stage_names=tuple(sorted(result.reached_stage_names)),
                    reached_flow_names=tuple(
                        sorted({flow_decl.name, *result.reached_flow_names})
                    ),
                    stage_edges=tuple(result.stage_edges),
                    stage_reaching_flows={
                        stage_name: tuple(sorted(flow_names))
                        for stage_name, flow_names in result.stage_reaching_flows.items()
                    },
                )
                flow_cache[cache_key] = expansion
                return expansion
            finally:
                flow_stack.pop()

        for root_kind, root_unit, root_decl, root_entry in root_decls:
            if root_kind == "stage":
                resolved_stage = self._resolve_stage_decl(root_decl, unit=root_unit)
                remember_stage(root_decl.name, owner_unit=root_unit, stage_decl=root_decl)
                resolve_stage_dependencies(root_decl, owner_unit=root_unit)
                aggregate_stage_reaching_flows.setdefault(root_decl.name, set())
            else:
                flow_expansion = expand_flow(root_decl, owner_unit=root_unit)
                aggregate_edges.extend(flow_expansion.stage_edges)
                for stage_name in flow_expansion.reached_stage_names:
                    stage_decl = reached_stage_decls[stage_name]
                    stage_unit = reached_stage_units[stage_name]
                    remember_stage(stage_name, owner_unit=stage_unit, stage_decl=stage_decl)
                for stage_name, flow_names in flow_expansion.stage_reaching_flows.items():
                    aggregate_stage_reaching_flows.setdefault(stage_name, set()).update(flow_names)

        if graph_recovery is not None:
            if graph_recovery.flow_receipt_name is not None:
                receipt_unit, receipt_decl = resolve_receipt_by_name(
                    graph_recovery.flow_receipt_name,
                    current_unit=unit,
                    source_span=graph_decl.source_span,
                    role="recovery",
                )
                remember_receipt(
                    receipt_decl.name,
                    owner_unit=receipt_unit,
                    receipt_decl=receipt_decl,
                )

        resolved_stages: list[model.ResolvedStage] = []
        for stage_name in sorted(reached_stage_order):
            stage_unit = reached_stage_units[stage_name]
            stage_decl = reached_stage_decls[stage_name]
            resolved_stage = self._resolve_stage_decl(stage_decl, unit=stage_unit)
            reaching_flows = aggregate_stage_reaching_flows.get(stage_name, set())
            if resolved_stage.applies_to_flow_names:
                missing_flows = sorted(
                    set(reaching_flows) - set(resolved_stage.applies_to_flow_names)
                )
                if missing_flows:
                    raise self._skill_graph_error(
                        detail=(
                            f"Skill graph `{owner_label}` reaches stage `{stage_name}` "
                            f"through flow(s) {', '.join(missing_flows)}, but stage "
                            "`applies_to:` does not list them."
                        ),
                        unit=stage_unit,
                        source_span=stage_decl.source_span,
                        hints=(
                            "List every reaching `skill_flow` under `applies_to:`, or remove the restriction.",
                        ),
                    )
            resolved_stages.append(resolved_stage)

        if any(
            policy.action == "require" and policy.key == "stage_lane"
            for policy in graph_policies
        ):
            for stage in resolved_stages:
                if stage.lane_name is not None:
                    continue
                stage_unit = reached_stage_units[stage.canonical_name]
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` requires `stage_lane`, but "
                        f"stage `{stage.canonical_name}` has no `lane:`."
                    ),
                    unit=stage_unit,
                    source_span=stage.source_span,
                    hints=("Add `lane: <EnumName>.<member>` to the stage.",),
                )

        dedup_stage_edges: list[model.ResolvedSkillGraphStageEdge] = []
        seen_stage_edges: set[
            tuple[str, str, str, str, str, str | None, str | None, str | None]
        ] = set()
        for edge in aggregate_edges:
            edge_key = (
                edge.source_stage_name,
                edge.target_stage_name,
                edge.via_flow_name,
                edge.kind,
                edge.why,
                edge.route_receipt_name,
                edge.route_field_key,
                edge.route_choice_key,
            )
            if edge_key in seen_stage_edges:
                continue
            seen_stage_edges.add(edge_key)
            dedup_stage_edges.append(edge)

        stage_successors: dict[str, list[str]] = {}
        stage_predecessors: dict[str, list[str]] = {}
        for edge in dedup_stage_edges:
            stage_successors.setdefault(edge.source_stage_name, [])
            if edge.target_stage_name not in stage_successors[edge.source_stage_name]:
                stage_successors[edge.source_stage_name].append(edge.target_stage_name)
            stage_predecessors.setdefault(edge.target_stage_name, [])
            if edge.source_stage_name not in stage_predecessors[edge.target_stage_name]:
                stage_predecessors[edge.target_stage_name].append(edge.source_stage_name)

        self._validate_skill_graph_dag(
            graph_name=graph_decl.name,
            stage_edges=tuple(dedup_stage_edges),
            unit=unit,
            source_span=graph_decl.source_span,
        )

        resolved_skills: list[model.ResolvedSkillGraphSkill] = []
        for skill_name in sorted(reached_skill_decls):
            skill_decl = reached_skill_decls[skill_name]
            resolved_skills.append(
                model.ResolvedSkillGraphSkill(
                    name=skill_decl.name,
                    title=skill_decl.title,
                    purpose=self._skill_decl_purpose(skill_decl),
                    package_id=(
                        None
                        if skill_decl.package_link is None
                        else skill_decl.package_link.package_id
                    ),
                    source_span=skill_decl.source_span,
                )
            )

        resolved_packages: list[model.ResolvedSkillGraphPackage] = []
        for package_id in sorted(reached_package_decls):
            package_decl = reached_package_decls[package_id]
            resolved_packages.append(
                model.ResolvedSkillGraphPackage(
                    package_id=package_id,
                    package_name=package_decl.name,
                    package_title=package_decl.title,
                    source_span=package_decl.source_span,
                )
            )

        resolved_receipts: list[model.ResolvedReceipt] = []
        for receipt_name in sorted(reached_receipt_decls):
            receipt_decl = reached_receipt_decls[receipt_name]
            receipt_unit = reached_receipt_units[receipt_name]
            resolved_receipts.append(
                self._resolve_resolved_receipt(receipt_decl, unit=receipt_unit)
            )

        resolved_flows = [
            flow_cache[key].graph_flow
            for key in sorted(flow_cache, key=lambda item: item[1])
        ]
        resolved = model.ResolvedSkillGraph(
            canonical_name=graph_decl.name,
            title=graph_decl.title,
            purpose=purpose_items[0].value,
            roots=graph_roots,
            sets=graph_sets,
            recovery=graph_recovery,
            policies=graph_policies,
            views=graph_views,
            flows=tuple(resolved_flows),
            stages=tuple(resolved_stages),
            skills=tuple(resolved_skills),
            receipts=tuple(resolved_receipts),
            packages=tuple(resolved_packages),
            stage_edges=tuple(dedup_stage_edges),
            stage_successors={
                key: tuple(values) for key, values in sorted(stage_successors.items())
            },
            stage_predecessors={
                key: tuple(values) for key, values in sorted(stage_predecessors.items())
            },
            stage_reaching_flows={
                key: tuple(sorted(values))
                for key, values in sorted(aggregate_stage_reaching_flows.items())
            },
            source_span=graph_decl.source_span,
        )
        cache[cache_key] = resolved
        return resolved

    def _resolve_skill_graph_sets(
        self,
        sets_item: model.SkillGraphSetsItem | None,
        *,
        unit: IndexedUnit,
        owner_label: str,
        graph_decl: model.SkillGraphDecl,
    ) -> tuple[model.ResolvedSkillGraphSet, ...]:
        if sets_item is None:
            return tuple()
        seen: set[str] = set()
        resolved: list[model.ResolvedSkillGraphSet] = []
        for entry in sets_item.entries:
            if entry.name in seen:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` declares graph set "
                        f"`{entry.name}` more than once."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=("Keep one entry per graph set name.",),
                )
            seen.add(entry.name)
            resolved.append(
                model.ResolvedSkillGraphSet(
                    name=entry.name,
                    title=entry.title,
                    source_span=entry.source_span,
                )
            )
        return tuple(resolved)

    def _resolve_skill_graph_recovery(
        self,
        recovery_item: model.SkillGraphRecoveryItem | None,
        *,
        unit: IndexedUnit,
        owner_label: str,
        graph_decl: model.SkillGraphDecl,
    ) -> model.ResolvedSkillGraphRecovery | None:
        if recovery_item is None:
            return None
        seen: set[str] = set()
        values: dict[str, str] = {}
        for entry in recovery_item.entries:
            if entry.key in seen:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` declares recovery key "
                        f"`{entry.key}` more than once."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=("Keep one ref per recovery key.",),
                )
            seen.add(entry.key)
            if entry.key == "flow_receipt":
                receipt_unit, receipt_decl = self._resolve_receipt_ref(entry.target_ref, unit=unit)
                _ = receipt_unit
                values[entry.key] = receipt_decl.name
                continue
            resolved_enum = self._try_resolve_enum_decl_with_unit(entry.target_ref, unit=unit)
            if resolved_enum is None:
                dotted = self._dotted_ref(entry.target_ref)
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` recovery ref `{entry.key}: "
                        f"{dotted}` does not resolve to a top-level `enum`."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=("Point recovery enum refs at declared top-level enums.",),
                )
            _enum_unit, enum_decl = resolved_enum
            values[entry.key] = enum_decl.name
        return model.ResolvedSkillGraphRecovery(
            flow_receipt_name=values.get("flow_receipt"),
            stage_status_name=values.get("stage_status"),
            durable_artifact_status_name=values.get("durable_artifact_status"),
            source_span=recovery_item.source_span,
        )

    def _resolve_skill_graph_policies(
        self,
        policy_item: model.SkillGraphPolicyItem | None,
        *,
        unit: IndexedUnit,
        owner_label: str,
        graph_decl: model.SkillGraphDecl,
    ) -> tuple[model.ResolvedSkillGraphPolicy, ...]:
        if policy_item is None:
            return tuple()
        seen: set[tuple[str, str]] = set()
        resolved: list[model.ResolvedSkillGraphPolicy] = []
        for entry in policy_item.entries:
            policy_key = (entry.action, entry.key)
            if policy_key in seen:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` repeats policy "
                        f"`{entry.action} {entry.key}`."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=("List each graph policy once.",),
                )
            seen.add(policy_key)
            if entry.action == "dag":
                if entry.key != "acyclic":
                    raise self._skill_graph_error(
                        detail=(
                            f"Skill graph `{owner_label}` declares unsupported "
                            f"`dag {entry.key}` policy."
                        ),
                        unit=unit,
                        source_span=entry.source_span or graph_decl.source_span,
                        hints=("Sub-plan 4 supports only `dag acyclic`.",),
                    )
            elif entry.action == "require":
                if entry.key not in model.SKILL_GRAPH_STRICT_POLICY_KEYS:
                    raise self._skill_graph_error(
                        detail=(
                            f"Skill graph `{owner_label}` declares unsupported "
                            f"`require {entry.key}` policy."
                        ),
                        unit=unit,
                        source_span=entry.source_span or graph_decl.source_span,
                        hints=(
                            "Sub-plan 4 accepts only shipped strict graph policy keys.",
                        ),
                    )
            elif entry.action == "warn":
                if entry.key not in model.SKILL_GRAPH_WARNING_POLICY_KEYS:
                    raise self._skill_graph_error(
                        detail=(
                            f"Skill graph `{owner_label}` declares unsupported "
                            f"`warn {entry.key}` policy."
                        ),
                        unit=unit,
                        source_span=entry.source_span or graph_decl.source_span,
                        hints=(
                            "Sub-plan 4 accepts warning policy keys only as inert metadata.",
                        ),
                    )
            resolved.append(
                model.ResolvedSkillGraphPolicy(
                    action=entry.action,
                    key=entry.key,
                    source_span=entry.source_span,
                )
            )
        return tuple(resolved)

    def _resolve_skill_graph_views(
        self,
        views_item: model.SkillGraphViewsItem | None,
        *,
        unit: IndexedUnit,
        owner_label: str,
        graph_decl: model.SkillGraphDecl,
    ) -> tuple[model.ResolvedSkillGraphView, ...]:
        if views_item is None:
            return tuple()
        seen: set[str] = set()
        resolved: list[model.ResolvedSkillGraphView] = []
        for entry in views_item.entries:
            if entry.key in seen:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` declares view key "
                        f"`{entry.key}` more than once."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=("Keep one output path per graph view key.",),
                )
            seen.add(entry.key)
            resolved.append(
                model.ResolvedSkillGraphView(
                    key=entry.key,
                    path=entry.path,
                    source_span=entry.source_span,
                )
            )
        return tuple(resolved)

    def _resolve_skill_graph_roots(
        self,
        roots_item: model.SkillGraphRootsItem,
        *,
        unit: IndexedUnit,
        owner_label: str,
        graph_decl: model.SkillGraphDecl,
    ) -> tuple[
        tuple[model.ResolvedSkillGraphRoot, ...],
        tuple[tuple[str, IndexedUnit, object, model.SkillGraphRootEntry], ...],
    ]:
        seen: set[tuple[str, str]] = set()
        resolved_roots: list[model.ResolvedSkillGraphRoot] = []
        resolved_decls: list[tuple[str, IndexedUnit, object, model.SkillGraphRootEntry]] = []
        for entry in roots_item.entries:
            try:
                owner_unit, declaration = self._resolve_decl_ref(
                    entry.target_ref,
                    unit=unit,
                    registry_name=(
                        "skill_flows_by_name" if entry.kind == "flow" else "stages_by_name"
                    ),
                    missing_label=(
                        "skill_flow declaration" if entry.kind == "flow" else "stage declaration"
                    ),
                )
            except CompileError as exc:
                dotted = self._dotted_ref(entry.target_ref)
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` root `{entry.kind} {dotted}` "
                        "does not resolve."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=(
                        "Point roots at visible top-level `stage` or `skill_flow` declarations.",
                    ),
                ) from exc
            root_name = declaration.name
            root_key = (entry.kind, root_name)
            if root_key in seen:
                raise self._skill_graph_error(
                    detail=(
                        f"Skill graph `{owner_label}` lists root "
                        f"`{entry.kind} {root_name}` more than once."
                    ),
                    unit=unit,
                    source_span=entry.source_span or graph_decl.source_span,
                    hints=("List each graph root once.",),
                )
            seen.add(root_key)
            resolved_roots.append(
                model.ResolvedSkillGraphRoot(
                    kind=entry.kind,
                    name=root_name,
                    source_span=entry.source_span,
                )
            )
            resolved_decls.append((entry.kind, owner_unit, declaration, entry))
        return tuple(resolved_roots), tuple(resolved_decls)

    def _validate_skill_graph_dag(
        self,
        *,
        graph_name: str,
        stage_edges: tuple[model.ResolvedSkillGraphStageEdge, ...],
        unit: IndexedUnit,
        source_span,
    ) -> None:
        adjacency: dict[str, tuple[str, ...]] = {}
        edge_by_pair: dict[tuple[str, str], model.ResolvedSkillGraphStageEdge] = {}
        for edge in stage_edges:
            adjacency.setdefault(edge.source_stage_name, tuple())
            targets = list(adjacency[edge.source_stage_name])
            if edge.target_stage_name not in targets:
                targets.append(edge.target_stage_name)
                adjacency[edge.source_stage_name] = tuple(targets)
            edge_by_pair.setdefault(
                (edge.source_stage_name, edge.target_stage_name),
                edge,
            )

        white = 0
        gray = 1
        black = 2
        color: dict[str, int] = {}
        cycle_edge: model.ResolvedSkillGraphStageEdge | None = None

        def visit(node: str) -> None:
            nonlocal cycle_edge
            color[node] = gray
            for target in adjacency.get(node, ()):
                state = color.get(target, white)
                if state == gray:
                    cycle_edge = edge_by_pair[(node, target)]
                    return
                if state == white:
                    visit(target)
                    if cycle_edge is not None:
                        return
            color[node] = black

        for node in sorted(adjacency):
            if color.get(node, white) != white:
                continue
            visit(node)
            if cycle_edge is not None:
                break

        if cycle_edge is None:
            return
        raise self._skill_graph_error(
            detail=(
                f"Skill graph `{graph_name}` expands to a stage cycle through "
                f"`{cycle_edge.source_stage_name} -> {cycle_edge.target_stage_name}`."
            ),
            unit=unit,
            source_span=cycle_edge.source_span or source_span,
            hints=(
                "Break the cross-flow cycle, or rewrite the loop as a typed repeat.",
            ),
        )

    def _skill_decl_purpose(
        self,
        skill_decl: model.SkillDecl,
    ) -> str | None:
        for item in skill_decl.items:
            if isinstance(item, model.RecordScalar) and item.key == "purpose":
                if isinstance(item.value, str):
                    return item.value
        return None

    def _validate_all_skill_graphs_in_flow(self, flow) -> None:
        registry = getattr(flow, "skill_graphs_by_name", None)
        if not registry:
            return
        validated_key = (flow.prompt_root.resolve(), flow.flow_root.resolve())
        cache = getattr(self, "_skill_graphs_validated_flows", None)
        if cache is None:
            cache = set()
            object.__setattr__(self, "_skill_graphs_validated_flows", cache)
        if validated_key in cache:
            return
        cache.add(validated_key)
        for graph_decl in registry.values():
            owner_unit = flow.declaration_owner_units_by_id[id(graph_decl)]
            self._resolve_skill_graph_decl(graph_decl, unit=owner_unit)
