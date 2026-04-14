from __future__ import annotations

import textwrap
from collections import defaultdict
from dataclasses import dataclass

from doctrine._compiler.types import FlowAgentNode, FlowEdge, FlowGraph, FlowInputNode, FlowOutputNode

AgentKey = tuple[tuple[str, ...], str]
ROUTE_EDGE_KINDS = {"authored_route", "law_route"}


@dataclass(slots=True, frozen=True)
class FlowLanePlan:
    primary_lane: tuple[AgentKey, ...]
    route_starts: tuple[AgentKey, ...]
    secondary_lanes: tuple[AgentKey, ...]


def node_palette(
    node: FlowAgentNode | FlowInputNode | FlowOutputNode,
) -> tuple[str, str]:
    if isinstance(node, FlowInputNode):
        return ("#E8F1FF", "#2F6FEB")
    if isinstance(node, FlowOutputNode):
        return ("#ECFDF3", "#067647")
    return ("#FFF7E6", "#B54708")


def edge_style(kind: str) -> tuple[str, int | None]:
    if kind == "consume":
        return ("#5B708B", 4)
    if kind == "produce":
        return ("#067647", 4)
    if kind == "authored_route":
        return ("#B54708", None)
    return ("#D92D20", None)


def node_id(kind: str, module_parts: tuple[str, ...], name: str) -> str:
    parts = "_".join((*module_parts, name)).replace(".", "_").lower()
    return f"{kind}_{parts}"


def graph_participants(
    graph: FlowGraph,
) -> tuple[
    dict[tuple[tuple[str, ...], str], tuple[str, ...]],
    dict[tuple[tuple[str, ...], str], tuple[str, ...]],
]:
    agent_titles = {
        (agent.module_parts, agent.name): agent.title or agent.name
        for agent in graph.agents
    }
    input_consumers: dict[tuple[tuple[str, ...], str], set[str]] = defaultdict(set)
    output_producers: dict[tuple[tuple[str, ...], str], set[str]] = defaultdict(set)

    for edge in graph.edges:
        if edge.kind == "consume" and edge.source_kind == "input" and edge.target_kind == "agent":
            input_consumers[(edge.source_module_parts, edge.source_name)].add(
                agent_titles.get((edge.target_module_parts, edge.target_name), edge.target_name)
            )
        if edge.kind == "produce" and edge.source_kind == "agent" and edge.target_kind == "output":
            output_producers[(edge.target_module_parts, edge.target_name)].add(
                agent_titles.get((edge.source_module_parts, edge.source_name), edge.source_name)
            )

    return (
        {key: tuple(sorted(names)) for key, names in input_consumers.items()},
        {key: tuple(sorted(names)) for key, names in output_producers.items()},
    )


def node_paths(
    section_id: str,
    nodes: list[FlowInputNode | FlowOutputNode],
) -> dict[tuple[str, tuple[str, ...], str], str]:
    paths: dict[tuple[str, tuple[str, ...], str], str] = {}
    for node in nodes:
        kind = "input" if isinstance(node, FlowInputNode) else "output"
        paths[(kind, node.module_parts, node.name)] = (
            f"{section_id}.{node_id(kind, node.module_parts, node.name)}"
        )
    return paths


def agent_node_paths(
    graph: FlowGraph,
    lane_plan: FlowLanePlan,
) -> dict[tuple[str, tuple[str, ...], str], str]:
    paths: dict[tuple[str, tuple[str, ...], str], str] = {}
    for node in graph.agents:
        node_key = (node.module_parts, node.name)
        if node_key in lane_plan.primary_lane:
            container = "primary_lane"
        elif node_key in lane_plan.route_starts:
            container = "route_starts"
        else:
            container = "secondary_lanes"
        paths[("agent", node.module_parts, node.name)] = (
            f"agent_handoffs.{container}.{node_id('agent', node.module_parts, node.name)}"
        )
    return paths


def plan_agent_lanes(graph: FlowGraph) -> FlowLanePlan:
    ordered_agents = tuple((node.module_parts, node.name) for node in graph.agents)
    route_edges = [
        edge
        for edge in graph.edges
        if edge.kind in ROUTE_EDGE_KINDS
        and edge.source_kind == "agent"
        and edge.target_kind == "agent"
    ]
    if not route_edges:
        return FlowLanePlan(
            primary_lane=ordered_agents,
            route_starts=(),
            secondary_lanes=(),
        )

    route_outgoing: dict[AgentKey, list[FlowEdge]] = defaultdict(list)
    route_in_degree: dict[AgentKey, int] = defaultdict(int)
    route_participants: set[AgentKey] = set()
    first_route_source: AgentKey | None = None

    for edge in route_edges:
        source = (edge.source_module_parts, edge.source_name)
        target = (edge.target_module_parts, edge.target_name)
        if first_route_source is None:
            first_route_source = source
        route_participants.add(source)
        route_participants.add(target)
        route_outgoing[source].append(edge)
        route_in_degree[target] += 1
        route_in_degree.setdefault(source, 0)

    ordered_routed_agents = tuple(
        agent_key for agent_key in ordered_agents if agent_key in route_participants
    )
    route_starts = [
        agent_key
        for agent_key in ordered_routed_agents
        if route_in_degree.get(agent_key, 0) == 0
    ]
    if not route_starts and first_route_source is not None:
        route_starts = [first_route_source]

    primary_start = route_starts[0] if route_starts else ordered_routed_agents[0]
    primary_lane_full: list[AgentKey] = []
    seen_on_primary_lane: set[AgentKey] = set()
    current = primary_start

    while current not in seen_on_primary_lane:
        primary_lane_full.append(current)
        seen_on_primary_lane.add(current)
        next_agent: AgentKey | None = None
        for edge in route_outgoing.get(current, ()):
            target = (edge.target_module_parts, edge.target_name)
            if target in seen_on_primary_lane:
                continue
            next_agent = target
            break
        if next_agent is None:
            break
        current = next_agent

    if len(route_starts) > 1 and len(primary_lane_full) > 1:
        primary_lane = tuple(primary_lane_full[1:])
        route_start_agents = tuple(route_starts)
    else:
        primary_lane = tuple(primary_lane_full)
        route_start_agents = tuple(
            agent_key for agent_key in route_starts if agent_key not in primary_lane
        )

    secondary_lane_agents = tuple(
        agent_key
        for agent_key in ordered_agents
        if agent_key not in primary_lane and agent_key not in route_start_agents
    )

    return FlowLanePlan(
        primary_lane=primary_lane,
        route_starts=route_start_agents,
        secondary_lanes=secondary_lane_agents,
    )


def node_label_lines(
    node: FlowAgentNode | FlowInputNode | FlowOutputNode,
    *,
    consumer_names: tuple[str, ...] = (),
    producer_names: tuple[str, ...] = (),
) -> list[str]:
    label_lines = [node.title]
    if isinstance(node, FlowInputNode):
        label_lines.append("Shared Input" if len(consumer_names) > 1 else "Input")
        if node.source_title:
            label_lines.append(f"Source: {node.source_title}")
        label_lines.extend(node.detail_lines)
        if node.shape_title:
            label_lines.append(f"Shape: {node.shape_title}")
        if node.requirement_title:
            label_lines.append(f"Requirement: {node.requirement_title}")
        if consumer_names:
            label_lines.append("Used by: " + ", ".join(consumer_names))
        label_lines.extend(node.notes)
        return label_lines

    if isinstance(node, FlowOutputNode):
        if len(producer_names) > 1 and (node.trust_surface or node.notes):
            label_lines.append("Shared Output / Carrier")
        elif len(producer_names) > 1:
            label_lines.append("Shared Output")
        elif node.trust_surface or node.notes:
            label_lines.append("Carrier Output")
        else:
            label_lines.append("Output")
        if node.target_title:
            label_lines.append(f"Target: {node.target_title}")
        if node.primary_path:
            label_lines.append(f"Path: {node.primary_path}")
        label_lines.extend(node.detail_lines)
        if node.shape_title:
            label_lines.append(f"Shape: {node.shape_title}")
        if node.requirement_title:
            label_lines.append(f"Requirement: {node.requirement_title}")
        if producer_names:
            label_lines.append("Produced by: " + ", ".join(producer_names))
        if node.trust_surface:
            label_lines.append("Trust: " + ", ".join(node.trust_surface))
        label_lines.extend(node.notes)
        return label_lines

    label_lines.append("Agent")
    label_lines.extend(node.detail_lines)
    label_lines.extend(node.notes)
    return label_lines


def section_palette(section_id: str) -> tuple[str, str]:
    if section_id == "shared_inputs":
        return ("#F5F8FF", "#2F6FEB")
    if section_id == "local_inputs":
        return ("#F8FAFC", "#94A3B8")
    if section_id == "agent_handoffs":
        return ("#FFF8EB", "#B54708")
    if section_id == "shared_outputs_and_carriers":
        return ("#F3FFF8", "#067647")
    return ("#F8FAFC", "#94A3B8")


def wrap_lines(lines: tuple[str, ...] | list[str], *, width: int) -> str:
    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(textwrap.wrap(line, width=width) or [""])
    return "\n".join(wrapped)


def quoted(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")
    return f"\"{escaped}\""
