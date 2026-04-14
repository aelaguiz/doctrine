from __future__ import annotations

from doctrine._compiler.types import FlowAgentNode, FlowEdge, FlowGraph, FlowInputNode, FlowOutputNode
from doctrine._flow_render.layout import (
    agent_node_paths,
    edge_style,
    graph_participants,
    node_id,
    node_label_lines,
    node_palette,
    node_paths,
    plan_agent_lanes,
    quoted,
    section_palette,
    wrap_lines,
)


def render_flow_d2(graph: FlowGraph) -> str:
    lines = [
        "direction: down",
        "",
    ]

    input_consumers, output_producers = graph_participants(graph)
    shared_input_keys = {
        (node.module_parts, node.name)
        for node in graph.inputs
        if len(input_consumers.get((node.module_parts, node.name), ())) > 1
    }
    shared_output_keys = {
        (node.module_parts, node.name)
        for node in graph.outputs
        if len(output_producers.get((node.module_parts, node.name), ())) > 1
        or node.trust_surface
        or node.notes
    }

    sectioned_nodes = {
        "shared_inputs": [
            node for node in graph.inputs if (node.module_parts, node.name) in shared_input_keys
        ],
        "local_inputs": [
            node for node in graph.inputs if (node.module_parts, node.name) not in shared_input_keys
        ],
        "shared_outputs_and_carriers": [
            node for node in graph.outputs if (node.module_parts, node.name) in shared_output_keys
        ],
        "local_outputs": [
            node for node in graph.outputs if (node.module_parts, node.name) not in shared_output_keys
        ],
    }
    lane_plan = plan_agent_lanes(graph)
    path_map: dict[tuple[str, tuple[str, ...], str], str] = {}
    for section_id, nodes in sectioned_nodes.items():
        path_map.update(node_paths(section_id, nodes))
    path_map.update(agent_node_paths(graph, lane_plan))

    for section_id, section_label in (
        ("shared_inputs", "Shared Inputs"),
        ("local_inputs", "Local Inputs"),
    ):
        nodes = sectioned_nodes[section_id]
        if not nodes:
            continue
        lines.extend(
            _render_section(
                section_id,
                section_label,
                nodes,
                path_map,
                input_consumers,
                output_producers,
                direction="down",
            )
        )
        lines.append("")

    if graph.agents:
        lines.extend(_render_agent_section(graph, lane_plan, path_map))
        lines.append("")

    for section_id, section_label in (
        ("shared_outputs_and_carriers", "Shared Outputs And Carriers"),
        ("local_outputs", "Local Outputs"),
    ):
        nodes = sectioned_nodes[section_id]
        if not nodes:
            continue
        lines.extend(
            _render_section(
                section_id,
                section_label,
                nodes,
                path_map,
                input_consumers,
                output_producers,
                direction="down",
            )
        )
        lines.append("")

    for edge in graph.edges:
        lines.extend(_render_edge(edge, path_map))
        lines.append("")

    return "\n".join(line for line in lines if line is not None).rstrip() + "\n"


def _render_node(
    node_name: str,
    node: FlowAgentNode | FlowInputNode | FlowOutputNode,
    *,
    consumer_names: tuple[str, ...] = (),
    producer_names: tuple[str, ...] = (),
) -> list[str]:
    label_lines = node_label_lines(
        node,
        consumer_names=consumer_names,
        producer_names=producer_names,
    )

    fill, stroke = node_palette(node)
    label = quoted(wrap_lines(label_lines, width=30))
    return [
        f"{node_name}: {{",
        f"  label: {label}",
        "  shape: rectangle",
        "  style: {",
        f"    fill: \"{fill}\"",
        f"    stroke: \"{stroke}\"",
        "  }",
        "}",
    ]


def _render_edge(
    edge: FlowEdge,
    path_map: dict[tuple[str, tuple[str, ...], str], str],
) -> list[str]:
    source_id = path_map[(edge.source_kind, edge.source_module_parts, edge.source_name)]
    target_id = path_map[(edge.target_kind, edge.target_module_parts, edge.target_name)]
    stroke, dash = edge_style(edge.kind)
    lines = [
        f"{source_id} -> {target_id}: {{",
        f"  label: {quoted(wrap_lines((edge.label,), width=28))}",
        "  style: {",
        f"    stroke: \"{stroke}\"",
    ]
    if dash is not None:
        lines.append(f"    stroke-dash: {dash}")
    lines.extend(
        [
            "  }",
            "}",
        ]
    )
    return lines


def _render_section(
    section_id: str,
    section_label: str,
    nodes: list[FlowAgentNode | FlowInputNode | FlowOutputNode],
    path_map: dict[tuple[str, tuple[str, ...], str], str],
    input_consumers: dict[tuple[tuple[str, ...], str], tuple[str, ...]],
    output_producers: dict[tuple[tuple[str, ...], str], tuple[str, ...]],
    *,
    direction: str,
) -> list[str]:
    lines = [
        f"{section_id}: {{",
        f"  label: {quoted(section_label)}",
        f"  direction: {direction}",
        "  style: {",
    ]
    fill, stroke = section_palette(section_id)
    lines.extend(
        [
            f"    fill: \"{fill}\"",
            f"    stroke: \"{stroke}\"",
            "  }",
        ]
    )

    for node in nodes:
        kind = "agent"
        participant_names: tuple[str, ...] = ()
        if isinstance(node, FlowInputNode):
            kind = "input"
            participant_names = input_consumers.get((node.module_parts, node.name), ())
        elif isinstance(node, FlowOutputNode):
            kind = "output"
            participant_names = output_producers.get((node.module_parts, node.name), ())
        node_key = (kind, node.module_parts, node.name)
        nested_id = path_map[node_key].split(".", 1)[1]
        child_lines = _render_node(
            nested_id,
            node,
            consumer_names=participant_names if kind == "input" else (),
            producer_names=participant_names if kind == "output" else (),
        )
        lines.extend(f"  {line}" for line in child_lines)
        lines.append("")

    if lines[-1] == "":
        lines.pop()
    lines.append("}")
    return lines


def _render_agent_section(
    graph: FlowGraph,
    lane_plan,
    path_map: dict[tuple[str, tuple[str, ...], str], str],
) -> list[str]:
    section_direction = (
        "right"
        if lane_plan.secondary_route_agents or lane_plan.standalone_agents
        else "down"
    )
    lines = [
        "agent_handoffs: {",
        f"  label: {quoted('Agent Handoffs')}",
        f"  direction: {section_direction}",
        "  style: {",
    ]
    fill, stroke = section_palette("agent_handoffs")
    lines.extend(
        [
            f"    fill: \"{fill}\"",
            f"    stroke: \"{stroke}\"",
            "  }",
        ]
    )

    agents_by_key = {
        (node.module_parts, node.name): node
        for node in graph.agents
    }

    if lane_plan.secondary_route_agents:
        lines.extend(
            _render_agent_cluster(
                "route_starts",
                lane_plan.secondary_route_agents,
                agents_by_key,
                path_map,
                direction="down",
            )
        )
        lines.append("")

    if lane_plan.primary_lane:
        lines.extend(
            _render_agent_cluster(
                "primary_lane",
                lane_plan.primary_lane,
                agents_by_key,
                path_map,
                direction="down",
            )
        )
        lines.append("")

    if lane_plan.standalone_agents:
        lines.extend(
            _render_agent_cluster(
                "secondary_lanes",
                lane_plan.standalone_agents,
                agents_by_key,
                path_map,
                direction="down",
            )
        )
        lines.append("")

    if lines[-1] == "":
        lines.pop()
    lines.append("}")
    return lines


def _render_agent_cluster(
    cluster_id: str,
    agent_keys,
    agents_by_key: dict,
    path_map: dict[tuple[str, tuple[str, ...], str], str],
    *,
    direction: str,
) -> list[str]:
    lines = [
        f"  {cluster_id}: {{",
        f"    label: {quoted('')}",
        f"    direction: {direction}",
        "    style: {",
        "      fill: \"transparent\"",
        "      stroke: \"transparent\"",
        "    }",
    ]
    for agent_key in agent_keys:
        node = agents_by_key[agent_key]
        nested_id = path_map[("agent", node.module_parts, node.name)].rsplit(".", 1)[1]
        child_lines = _render_node(nested_id, node)
        lines.extend(f"    {line}" for line in child_lines)
        lines.append("")
    if lines[-1] == "":
        lines.pop()
    lines.append("  }")
    return lines
