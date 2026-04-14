from __future__ import annotations

from doctrine import model
from doctrine._compiler.constants import (
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
    _resolve_render_profile_mode,
    _semantic_render_target_for_block,
)
from doctrine._compiler.naming import (
    _authored_slot_allows_law,
    _display_addressable_ref,
    _dotted_ref_name,
    _humanize_key,
    _law_path_from_name_ref,
    _lowercase_initial,
    _name_ref_from_dotted_name,
)
from doctrine._compiler.resolved_types import (
    AgentContract,
    CompileError,
    ConfigSpec,
    FlowAgentKey,
    FlowAgentNode,
    FlowArtifactKey,
    FlowEdge,
    FlowGraph,
    FlowInputNode,
    FlowOutputNode,
    IndexedUnit,
    LawBranch,
    ResolvedAgentSlot,
    ResolvedLawPath,
    ResolvedRouteLine,
    ResolvedSchemaGroup,
    ResolvedSectionBodyItem,
    ResolvedSectionItem,
    ResolvedWorkflowBody,
    ResolvedWorkflowSkillsItem,
)
from doctrine._compiler.support_files import _default_worker_count, _dotted_decl_name


class FlowMixin:
    """Flow extraction helper owner for CompilationContext."""

    def extract_target_flow_graph(self, agent_names: tuple[str, ...]) -> FlowGraph:
        root_agents: list[tuple[IndexedUnit, model.Agent]] = []
        for agent_name in agent_names:
            agent = self.root_unit.agents_by_name.get(agent_name)
            if agent is None:
                raise CompileError(f"Missing target agent: {agent_name}")
            if agent.abstract:
                raise CompileError(f"Abstract agent does not render: {agent_name}")
            root_agents.append((self.root_unit, agent))

        agent_nodes: dict[FlowAgentKey, FlowAgentNode] = {}
        input_nodes: dict[FlowArtifactKey, FlowInputNode] = {}
        output_nodes: dict[FlowArtifactKey, FlowOutputNode] = {}
        agent_notes: dict[FlowAgentKey, list[str]] = {}
        input_notes: dict[FlowArtifactKey, list[str]] = {}
        output_notes: dict[FlowArtifactKey, list[str]] = {}
        edges: dict[
            tuple[
                str,
                str,
                tuple[str, ...],
                str,
                str,
                tuple[str, ...],
                str,
                str,
            ],
            FlowEdge,
        ] = {}

        for unit, agent in root_agents:
            agent_key = (unit.module_parts, agent.name)
            self._flow_upsert_agent_node(agent_nodes, agent, unit=unit)

            agent_contract = self._resolve_agent_contract(agent, unit=unit)
            resolved_slot_states = self._resolve_agent_slots(agent, unit=unit)
            resolved_slots = {
                slot.key: slot.body
                for slot in resolved_slot_states
                if isinstance(slot, ResolvedAgentSlot)
            }
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
            for input_key, (input_unit, input_decl) in sorted(agent_contract.inputs.items()):
                self._flow_upsert_input_node(input_nodes, input_decl, unit=input_unit)
                self._flow_add_edge(
                    edges,
                    FlowEdge(
                        kind="consume",
                        source_kind="input",
                        source_module_parts=input_key[0],
                        source_name=input_key[1],
                        target_kind="agent",
                        target_module_parts=agent_key[0],
                        target_name=agent_key[1],
                        label="consumes",
                    ),
                )

            for output_key, (output_unit, output_decl) in sorted(agent_contract.outputs.items()):
                self._flow_upsert_output_node(output_nodes, output_decl, unit=output_unit)
                self._flow_add_edge(
                    edges,
                    FlowEdge(
                        kind="produce",
                        source_kind="agent",
                        source_module_parts=agent_key[0],
                        source_name=agent_key[1],
                        target_kind="output",
                        target_module_parts=output_key[0],
                        target_name=output_key[1],
                        label="produces",
                    ),
                )

            for slot_state in resolved_slot_states:
                if not isinstance(slot_state, ResolvedAgentSlot):
                    continue
                self._collect_flow_from_workflow_body(
                    slot_state.body,
                    workflow_unit=unit,
                    agent_unit=unit,
                    agent=agent,
                    agent_contract=agent_contract,
                    agent_nodes=agent_nodes,
                    agent_notes=agent_notes,
                    input_notes=input_notes,
                    output_nodes=output_nodes,
                    output_notes=output_notes,
                    edges=edges,
                    owner_label=f"agent {agent.name} slot {slot_state.key}",
                    slot_key=slot_state.key,
                    workflow_stack=(),
                )

        # Preserve first-seen flow order so the renderer can recover the routed
        # handoff lane instead of receiving an alphabetized graph.
        return FlowGraph(
            agents=tuple(
                FlowAgentNode(
                    module_parts=node.module_parts,
                    name=node.name,
                    title=node.title,
                    detail_lines=node.detail_lines,
                    notes=tuple(agent_notes.get((node.module_parts, node.name), ())),
                )
                for node in agent_nodes.values()
            ),
            inputs=tuple(
                FlowInputNode(
                    module_parts=node.module_parts,
                    name=node.name,
                    title=node.title,
                    source_title=node.source_title,
                    shape_title=node.shape_title,
                    requirement_title=node.requirement_title,
                    detail_lines=node.detail_lines,
                    notes=tuple(input_notes.get((node.module_parts, node.name), ())),
                )
                for node in input_nodes.values()
            ),
            outputs=tuple(
                FlowOutputNode(
                    module_parts=node.module_parts,
                    name=node.name,
                    title=node.title,
                    target_title=node.target_title,
                    primary_path=node.primary_path,
                    shape_title=node.shape_title,
                    requirement_title=node.requirement_title,
                    detail_lines=node.detail_lines,
                    trust_surface=node.trust_surface,
                    notes=tuple(output_notes.get((node.module_parts, node.name), ())),
                )
                for node in output_nodes.values()
            ),
            edges=tuple(edges.values()),
        )

    def _collect_flow_from_workflow_body(
        self,
        workflow_body: ResolvedWorkflowBody,
        *,
        workflow_unit: IndexedUnit,
        agent_unit: IndexedUnit,
        agent: model.Agent,
        agent_contract: AgentContract,
        agent_nodes: dict[FlowAgentKey, FlowAgentNode],
        agent_notes: dict[FlowAgentKey, list[str]],
        input_notes: dict[FlowArtifactKey, list[str]],
        output_nodes: dict[FlowArtifactKey, FlowOutputNode],
        output_notes: dict[FlowArtifactKey, list[str]],
        edges: dict[
            tuple[
                str,
                str,
                tuple[str, ...],
                str,
                str,
                tuple[str, ...],
                str,
                str,
            ],
            FlowEdge,
        ],
        owner_label: str,
        slot_key: str,
        workflow_stack: tuple[tuple[tuple[str, ...], str], ...],
    ) -> None:
        agent_key = (agent_unit.module_parts, agent.name)

        for item in workflow_body.items:
            if isinstance(item, ResolvedSectionItem):
                self._collect_flow_from_section_items(
                    item.items,
                    agent_key=agent_key,
                    agent_nodes=agent_nodes,
                    edges=edges,
                )
                continue
            if isinstance(item, ResolvedWorkflowSkillsItem):
                continue

            workflow_key = (item.target_unit.module_parts, item.workflow_decl.name)
            if workflow_key in workflow_stack:
                cycle = " -> ".join(
                    ".".join(parts + (name,)) or name
                    for parts, name in [*workflow_stack, workflow_key]
                )
                raise CompileError(f"Cyclic workflow composition: {cycle}")

            self._collect_flow_from_workflow_body(
                self._resolve_workflow_decl(item.workflow_decl, unit=item.target_unit),
                workflow_unit=item.target_unit,
                agent_unit=agent_unit,
                agent=agent,
                agent_contract=agent_contract,
                agent_nodes=agent_nodes,
                agent_notes=agent_notes,
                input_notes=input_notes,
                output_nodes=output_nodes,
                output_notes=output_notes,
                edges=edges,
                owner_label=f"workflow {_dotted_decl_name(item.target_unit.module_parts, item.workflow_decl.name)}",
                slot_key=slot_key,
                workflow_stack=(*workflow_stack, workflow_key),
            )

        if workflow_body.law is None:
            return

        if not _authored_slot_allows_law(slot_key):
            raise CompileError(
                f"law may appear only on workflow or handoff_routing in {owner_label}: {slot_key}"
            )
        flat_items = self._flatten_law_items(workflow_body.law, owner_label=owner_label)
        if slot_key == "handoff_routing":
            self._validate_handoff_routing_law(
                flat_items,
                unit=workflow_unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
            )
        else:
            self._validate_workflow_law(
                flat_items,
                unit=workflow_unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
            )
        branches = self._collect_law_leaf_branches(flat_items, unit=workflow_unit)
        if not branches:
            branches = (LawBranch(),)

        for branch in branches:
            current = branch.current_subjects[0] if branch.current_subjects else None
            if isinstance(current, model.CurrentNoneStmt):
                self._flow_append_note(
                    agent_notes,
                    agent_key,
                    "May end with no current artifact",
                )
            elif isinstance(current, model.CurrentArtifactStmt):
                target = self._validate_law_path_root(
                    current.target,
                    unit=workflow_unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label="current artifact",
                    allowed_kinds=("input", "output"),
                )
                if target.remainder or target.wildcard:
                    raise CompileError(
                        "current artifact must stay rooted at one input or output artifact in "
                        f"{owner_label}: {'.'.join(current.target.parts)}"
                    )
                carrier = self._validate_carrier_path(
                    current.carrier,
                    unit=workflow_unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label="current artifact",
                )
                target_label = self._display_readable_decl(target.decl)
                carrier_label = self._flow_carrier_label(
                    carrier,
                    owner_label=owner_label,
                )
                self._flow_append_artifact_note(
                    input_notes=input_notes,
                    output_notes=output_notes,
                    resolved=target,
                    note=f"Current via {carrier_label}",
                )
                self._flow_append_note(
                    output_notes,
                    (carrier.unit.module_parts, carrier.decl.name),
                    f"Carries current for {target_label}",
                )

            for invalidate in branch.invalidations:
                target = self._validate_law_path_root(
                    invalidate.target,
                    unit=workflow_unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label="invalidate",
                    allowed_kinds=("input", "output", "schema_group"),
                )
                if target.remainder or target.wildcard:
                    raise CompileError(
                        f"invalidate must name one full input or output artifact or schema group in {owner_label}: "
                        f"{'.'.join(invalidate.target.parts)}"
                    )
                carrier = self._validate_carrier_path(
                    invalidate.carrier,
                    unit=workflow_unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                    statement_label="invalidate",
                )
                carrier_label = self._flow_carrier_label(
                    carrier,
                    owner_label=owner_label,
                )
                if isinstance(target.decl, ResolvedSchemaGroup):
                    target_labels: list[str] = []
                    for member in self._schema_group_member_artifacts(target.decl, unit=target.unit):
                        target_labels.append(member.title)
                        self._flow_append_artifact_note(
                            input_notes=input_notes,
                            output_notes=output_notes,
                            resolved=ResolvedLawPath(
                                unit=member.artifact.unit,
                                decl=member.artifact.decl,
                                remainder=(),
                            ),
                            note=f"Invalidated via {carrier_label}",
                        )
                    target_label = ", ".join(target_labels) or target.decl.title
                else:
                    target_label = self._display_readable_decl(target.decl)
                    self._flow_append_artifact_note(
                        input_notes=input_notes,
                        output_notes=output_notes,
                        resolved=target,
                        note=f"Invalidated via {carrier_label}",
                    )
                self._flow_append_note(
                    output_notes,
                    (carrier.unit.module_parts, carrier.decl.name),
                    f"Carries invalidation for {target_label}",
                )

            for route in branch.routes:
                route_label = self._interpolate_authored_prose_string(
                    route.label,
                    unit=workflow_unit,
                    owner_label=owner_label,
                    surface_label="route labels",
                )
                target_unit, target_agent = self._resolve_agent_ref(route.target, unit=workflow_unit)
                self._flow_upsert_agent_node(agent_nodes, target_agent, unit=target_unit)
                self._flow_add_edge(
                    edges,
                    FlowEdge(
                        kind="law_route",
                        source_kind="agent",
                        source_module_parts=agent_key[0],
                        source_name=agent_key[1],
                        target_kind="agent",
                        target_module_parts=target_unit.module_parts,
                        target_name=target_agent.name,
                        label=route_label,
                    ),
                )

        for output_key, (output_unit, output_decl) in sorted(agent_contract.outputs.items()):
            if output_key not in output_nodes:
                self._flow_upsert_output_node(output_nodes, output_decl, unit=output_unit)

    def _collect_flow_from_section_items(
        self,
        items: tuple[ResolvedSectionBodyItem, ...],
        *,
        agent_key: FlowAgentKey,
        agent_nodes: dict[FlowAgentKey, FlowAgentNode],
        edges: dict[
            tuple[
                str,
                str,
                tuple[str, ...],
                str,
                str,
                tuple[str, ...],
                str,
                str,
            ],
            FlowEdge,
        ],
    ) -> None:
        for item in items:
            if isinstance(item, ResolvedSectionItem):
                self._collect_flow_from_section_items(
                    item.items,
                    agent_key=agent_key,
                    agent_nodes=agent_nodes,
                    edges=edges,
                )
                continue
            if not isinstance(item, ResolvedRouteLine):
                continue
            target_unit = (
                self._load_module(item.target_module_parts)
                if item.target_module_parts
                else self.root_unit
            )
            target_agent = target_unit.agents_by_name.get(item.target_name)
            if target_agent is not None:
                self._flow_upsert_agent_node(agent_nodes, target_agent, unit=target_unit)
            self._flow_add_edge(
                edges,
                FlowEdge(
                    kind="authored_route",
                    source_kind="agent",
                    source_module_parts=agent_key[0],
                    source_name=agent_key[1],
                    target_kind="agent",
                    target_module_parts=item.target_module_parts,
                    target_name=item.target_name,
                    label=item.label,
                ),
            )

    def _flow_upsert_agent_node(
        self,
        nodes: dict[FlowAgentKey, FlowAgentNode],
        agent: model.Agent,
        *,
        unit: IndexedUnit,
    ) -> None:
        key = (unit.module_parts, agent.name)
        if key in nodes:
            return
        nodes[key] = FlowAgentNode(
            module_parts=unit.module_parts,
            name=agent.name,
            title=agent.title or agent.name,
            detail_lines=self._flow_agent_detail_lines(agent, unit=unit),
        )

    def _flow_upsert_input_node(
        self,
        nodes: dict[FlowArtifactKey, FlowInputNode],
        decl: model.InputDecl,
        *,
        unit: IndexedUnit,
    ) -> None:
        key = (unit.module_parts, decl.name)
        if key in nodes:
            return
        source_title, shape_title, requirement_title, detail_lines = self._flow_input_summary(
            decl,
            unit=unit,
        )
        nodes[key] = FlowInputNode(
            module_parts=unit.module_parts,
            name=decl.name,
            title=decl.title,
            source_title=source_title,
            shape_title=shape_title,
            requirement_title=requirement_title,
            detail_lines=detail_lines,
        )

    def _flow_upsert_output_node(
        self,
        nodes: dict[FlowArtifactKey, FlowOutputNode],
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> None:
        key = (unit.module_parts, decl.name)
        if key in nodes:
            return
        target_title, primary_path, shape_title, requirement_title, detail_lines = (
            self._flow_output_summary(
                decl,
                unit=unit,
            )
        )
        nodes[key] = FlowOutputNode(
            module_parts=unit.module_parts,
            name=decl.name,
            title=decl.title,
            target_title=target_title,
            primary_path=primary_path,
            shape_title=shape_title,
            requirement_title=requirement_title,
            detail_lines=detail_lines,
            trust_surface=self._flow_trust_surface_labels(decl, unit=unit),
        )

    def _flow_agent_detail_lines(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
    ) -> tuple[str, ...]:
        for field in agent.fields:
            if isinstance(field, model.RoleScalar):
                return (
                    self._interpolate_authored_prose_string(
                        field.text,
                        unit=unit,
                        owner_label=f"agent {agent.name}",
                        surface_label="role prose",
                    ),
                )
            if isinstance(field, model.RoleBlock):
                if not field.lines:
                    return (field.title,)
                return (
                    self._interpolate_authored_prose_string(
                        field.lines[0].text if isinstance(field.lines[0], model.EmphasizedLine) else field.lines[0],
                        unit=unit,
                        owner_label=f"agent {agent.name}",
                        surface_label="role prose",
                    ),
                )
        return ()

    def _flow_input_summary(
        self,
        decl: model.InputDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[str, str, str, tuple[str, ...]]:
        scalar_items, _section_items, _extras = self._split_record_items(
            decl.items,
            scalar_keys={"source", "shape", "requirement"},
            owner_label=f"input {decl.name}",
        )
        source_item = scalar_items.get("source")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        if source_item is None or not isinstance(source_item.value, model.NameRef):
            raise CompileError(f"Input source must stay typed: {decl.name}")
        if shape_item is None or requirement_item is None:
            raise CompileError(f"Input is missing required fields: {decl.name}")

        source_spec = self._resolve_input_source_spec(source_item.value, unit=unit)
        config_lines, _config_values = self._flow_config_summary(
            source_item.body or (),
            spec=source_spec,
            unit=unit,
            owner_label=f"input {decl.name} source",
        )
        shape_title = self._display_symbol_value(
            shape_item.value,
            unit=unit,
            owner_label=f"input {decl.name}",
            surface_label="input fields",
        )
        requirement_title = self._display_symbol_value(
            requirement_item.value,
            unit=unit,
            owner_label=f"input {decl.name}",
            surface_label="input fields",
        )
        lines = list(config_lines)
        if decl.structure_ref is not None:
            _document_unit, document_decl = self._resolve_document_ref(decl.structure_ref, unit=unit)
            lines.append(f"Structure: {document_decl.title}")
        return (
            source_spec.title,
            shape_title,
            requirement_title,
            tuple(lines),
        )

    def _flow_output_summary(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[str, str | None, str | None, str | None, tuple[str, ...]]:
        scalar_items, section_items, _extras = self._split_record_items(
            decl.items,
            scalar_keys={"target", "shape", "requirement"},
            section_keys={"files"},
            owner_label=f"output {decl.name}",
        )
        target_item = scalar_items.get("target")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        files_section = section_items.get("files")

        target_title: str | None = None
        primary_path: str | None = None
        shape_title: str | None = None
        lines: list[str] = []
        if files_section is not None:
            target_title = "Files"
            lines.extend(
                self._flow_output_files_detail_lines(
                    files_section,
                    unit=unit,
                    output_name=decl.name,
                )
            )
        else:
            if target_item is None or not isinstance(target_item.value, model.NameRef):
                raise CompileError(f"Output target must stay typed: {decl.name}")
            if shape_item is None:
                raise CompileError(f"Output must define a shape: {decl.name}")
            target_spec = self._resolve_output_target_spec(target_item.value, unit=unit)
            target_title = target_spec.title
            config_lines, config_values = self._flow_config_summary(
                target_item.body or (),
                spec=target_spec,
                unit=unit,
                owner_label=f"output {decl.name} target",
            )
            primary_path = config_values.get("path")
            lines.extend(
                line for line in config_lines if line != f"Path: {primary_path}"
            )
            shape_title = self._display_output_shape(
                shape_item.value,
                unit=unit,
                owner_label=f"output {decl.name}",
                surface_label="output fields",
            )

        requirement_title: str | None = None
        if requirement_item is not None:
            requirement_title = self._display_symbol_value(
                requirement_item.value,
                unit=unit,
                owner_label=f"output {decl.name}",
                surface_label="output fields",
            )
        if decl.schema_ref is not None:
            _schema_unit, schema_decl = self._resolve_schema_ref(decl.schema_ref, unit=unit)
            lines.append(f"Schema: {schema_decl.title}")
        if decl.structure_ref is not None:
            _document_unit, document_decl = self._resolve_document_ref(decl.structure_ref, unit=unit)
            lines.append(f"Structure: {document_decl.title}")
        return (
            target_title,
            primary_path,
            shape_title,
            requirement_title,
            tuple(lines),
        )

    def _flow_output_files_detail_lines(
        self,
        section: model.RecordSection,
        *,
        unit: IndexedUnit,
        output_name: str,
    ) -> tuple[str, ...]:
        lines: list[str] = ["Target: Files"]
        for item in section.items:
            if not isinstance(item, model.RecordSection):
                raise CompileError(
                    f"`files` entries must be titled sections in output {output_name}"
                )
            scalar_items, _section_items, _extras = self._split_record_items(
                item.items,
                scalar_keys={"path", "shape"},
                owner_label=f"output {output_name} file {item.key}",
            )
            path_item = scalar_items.get("path")
            shape_item = scalar_items.get("shape")
            if path_item is None or not isinstance(path_item.value, str):
                raise CompileError(
                    f"Output file entry is missing string path in {output_name}: {item.key}"
                )
            if shape_item is None:
                raise CompileError(
                    f"Output file entry is missing shape in {output_name}: {item.key}"
                )
            lines.append(f"{item.title}: {path_item.value}")
            lines.append(
                f"{item.title} Shape: {self._display_output_shape(shape_item.value, unit=unit, owner_label=f'output {output_name} file {item.key}', surface_label='output file fields')}"
            )
        return tuple(lines)

    def _flow_config_lines(
        self,
        config_items: tuple[model.RecordItem, ...],
        *,
        spec: ConfigSpec,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[str, ...]:
        lines, _values = self._flow_config_summary(
            config_items,
            spec=spec,
            unit=unit,
            owner_label=owner_label,
        )
        return lines

    def _flow_config_summary(
        self,
        config_items: tuple[model.RecordItem, ...],
        *,
        spec: ConfigSpec,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[tuple[str, ...], dict[str, str]]:
        lines: list[str] = []
        values: dict[str, str] = {}
        seen_keys: set[str] = set()
        allowed_keys = {**spec.required_keys, **spec.optional_keys}

        for item in config_items:
            if not isinstance(item, model.RecordScalar) or item.body is not None:
                raise CompileError(f"Config entries must be scalar key/value lines in {owner_label}")
            if item.key in seen_keys:
                raise CompileError(f"Duplicate config key in {owner_label}: {item.key}")
            seen_keys.add(item.key)
            if item.key not in allowed_keys:
                raise CompileError(f"Unknown config key in {owner_label}: {item.key}")
            rendered = self._display_scalar_value(
                item.value,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label="config values",
            ).text
            values[item.key] = rendered
            lines.append(
                f"{allowed_keys[item.key]}: {rendered}"
            )

        missing_required = [key for key in spec.required_keys if key not in seen_keys]
        if missing_required:
            missing = ", ".join(missing_required)
            raise CompileError(f"Missing required config key in {owner_label}: {missing}")

        return tuple(lines), values

    def _flow_trust_surface_labels(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[str, ...]:
        if not decl.trust_surface:
            return ()
        section = self._compile_trust_surface_section(decl, unit=unit)
        return tuple(
            item[2:]
            for item in section.body
            if isinstance(item, str) and item.startswith("- ")
        )

    def _flow_carrier_label(
        self,
        resolved: ResolvedLawPath,
        *,
        owner_label: str,
    ) -> str:
        if not isinstance(resolved.decl, model.OutputDecl):
            return self._display_readable_decl(resolved.decl)
        field_node = self._resolve_output_field_node(
            resolved.decl,
            path=resolved.remainder,
            unit=resolved.unit,
            owner_label=owner_label,
            surface_label="flow graph",
        )
        field_label = self._display_addressable_target_value(
            field_node,
            owner_label=owner_label,
            surface_label="flow graph",
        ).text
        return f"{resolved.decl.title}.{field_label}"

    def _flow_append_artifact_note(
        self,
        *,
        input_notes: dict[FlowArtifactKey, list[str]],
        output_notes: dict[FlowArtifactKey, list[str]],
        resolved: ResolvedLawPath,
        note: str,
    ) -> None:
        key = (resolved.unit.module_parts, resolved.decl.name)
        if isinstance(resolved.decl, model.InputDecl):
            self._flow_append_note(input_notes, key, note)
            return
        if isinstance(resolved.decl, model.OutputDecl):
            self._flow_append_note(output_notes, key, note)

    def _flow_append_note(
        self,
        notes_by_key: dict[tuple[tuple[str, ...], str], list[str]],
        key: tuple[tuple[str, ...], str],
        note: str,
    ) -> None:
        bucket = notes_by_key.setdefault(key, [])
        if note not in bucket:
            bucket.append(note)

    def _flow_add_edge(
        self,
        edges: dict[
            tuple[
                str,
                str,
                tuple[str, ...],
                str,
                str,
                tuple[str, ...],
                str,
                str,
            ],
            FlowEdge,
        ],
        edge: FlowEdge,
    ) -> None:
        key = (
            edge.kind,
            edge.source_kind,
            edge.source_module_parts,
            edge.source_name,
            edge.target_kind,
            edge.target_module_parts,
            edge.target_name,
            edge.label,
        )
        edges.setdefault(key, edge)
