from __future__ import annotations

import subprocess
import textwrap
from collections import defaultdict
from pathlib import Path

from doctrine.compiler import FlowAgentNode, FlowEdge, FlowGraph, FlowInputNode, FlowOutputNode

REPO_ROOT = Path(__file__).resolve().parent.parent
D2_HELPER_PATH = Path(__file__).resolve().with_name("flow_svg.mjs")
D2_PACKAGE_PATH = REPO_ROOT / "node_modules" / "@terrastruct" / "d2" / "package.json"


class FlowRenderDependencyError(RuntimeError):
    """Raised when the pinned D2 dependency is unavailable."""


class FlowRenderFailure(RuntimeError):
    """Raised when D2 fails to render SVG output."""


def render_flow_d2(graph: FlowGraph) -> str:
    lines = [
        "direction: down",
        "",
    ]

    input_consumers, output_producers = _graph_participants(graph)
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
        "agent_handoffs": list(graph.agents),
        "shared_outputs_and_carriers": [
            node for node in graph.outputs if (node.module_parts, node.name) in shared_output_keys
        ],
        "local_outputs": [
            node for node in graph.outputs if (node.module_parts, node.name) not in shared_output_keys
        ],
    }
    node_paths = _node_paths(sectioned_nodes)

    for section_id, section_label in (
        ("shared_inputs", "Shared Inputs"),
        ("local_inputs", "Local Inputs"),
        ("agent_handoffs", "Agent Handoffs"),
        ("shared_outputs_and_carriers", "Shared Outputs And Carriers"),
        ("local_outputs", "Local Outputs"),
    ):
        nodes = sectioned_nodes[section_id]
        if not nodes:
            continue
        lines.extend(_render_section(section_id, section_label, nodes, node_paths, input_consumers, output_producers))
        lines.append("")

    for edge in graph.edges:
        lines.extend(_render_edge(edge, node_paths))
        lines.append("")

    return "\n".join(line for line in lines if line is not None).rstrip() + "\n"


def render_flow_svg(d2_path: Path, svg_path: Path) -> None:
    if not D2_PACKAGE_PATH.is_file():
        raise FlowRenderDependencyError(
            "Pinned D2 dependency is missing under `node_modules/@terrastruct/d2`. Run `npm ci`."
        )
    if not D2_HELPER_PATH.is_file():
        raise FlowRenderDependencyError(
            f"Doctrine D2 helper is missing: `{D2_HELPER_PATH}`."
        )

    result = subprocess.run(
        ["node", str(D2_HELPER_PATH), str(d2_path), str(svg_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return
    detail = (result.stderr or result.stdout).strip() or f"node exited {result.returncode}"
    raise FlowRenderFailure(detail)


def _render_node(
    node_id: str,
    node: FlowAgentNode | FlowInputNode | FlowOutputNode,
    *,
    consumer_names: tuple[str, ...] = (),
    producer_names: tuple[str, ...] = (),
) -> list[str]:
    label_lines = _node_label_lines(
        node,
        consumer_names=consumer_names,
        producer_names=producer_names,
    )

    fill, stroke = _node_palette(node)
    label = _quoted(_wrap_lines(label_lines, width=30))
    return [
        f"{node_id}: {{",
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
    node_paths: dict[tuple[str, tuple[str, ...], str], str],
) -> list[str]:
    source_id = node_paths[(edge.source_kind, edge.source_module_parts, edge.source_name)]
    target_id = node_paths[(edge.target_kind, edge.target_module_parts, edge.target_name)]
    stroke, dash = _edge_style(edge.kind)
    lines = [
        f"{source_id} -> {target_id}: {{",
        f"  label: {_quoted(_wrap_lines((edge.label,), width=28))}",
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


def _node_palette(
    node: FlowAgentNode | FlowInputNode | FlowOutputNode,
) -> tuple[str, str]:
    if isinstance(node, FlowInputNode):
        return ("#E8F1FF", "#2F6FEB")
    if isinstance(node, FlowOutputNode):
        return ("#ECFDF3", "#067647")
    return ("#FFF7E6", "#B54708")


def _edge_style(kind: str) -> tuple[str, int | None]:
    if kind == "consume":
        return ("#5B708B", 4)
    if kind == "produce":
        return ("#067647", 4)
    if kind == "authored_route":
        return ("#B54708", None)
    return ("#D92D20", None)


def _node_id(kind: str, module_parts: tuple[str, ...], name: str) -> str:
    parts = "_".join((*module_parts, name)).replace(".", "_").lower()
    return f"{kind}_{parts}"


def _graph_participants(
    graph: FlowGraph,
) -> tuple[
    dict[tuple[tuple[str, ...], str], tuple[str, ...]],
    dict[tuple[tuple[str, ...], str], tuple[str, ...]],
]:
    input_consumers: dict[tuple[tuple[str, ...], str], set[str]] = defaultdict(set)
    output_producers: dict[tuple[tuple[str, ...], str], set[str]] = defaultdict(set)

    for edge in graph.edges:
        if edge.kind == "consume" and edge.source_kind == "input" and edge.target_kind == "agent":
            input_consumers[(edge.source_module_parts, edge.source_name)].add(edge.target_name)
        if edge.kind == "produce" and edge.source_kind == "agent" and edge.target_kind == "output":
            output_producers[(edge.target_module_parts, edge.target_name)].add(edge.source_name)

    return (
        {key: tuple(sorted(names)) for key, names in input_consumers.items()},
        {key: tuple(sorted(names)) for key, names in output_producers.items()},
    )


def _node_paths(
    sectioned_nodes: dict[str, list[FlowAgentNode | FlowInputNode | FlowOutputNode]],
) -> dict[tuple[str, tuple[str, ...], str], str]:
    paths: dict[tuple[str, tuple[str, ...], str], str] = {}
    for section_id, nodes in sectioned_nodes.items():
        for node in nodes:
            kind = "agent"
            if isinstance(node, FlowInputNode):
                kind = "input"
            elif isinstance(node, FlowOutputNode):
                kind = "output"
            node_id = _node_id(kind, node.module_parts, node.name)
            paths[(kind, node.module_parts, node.name)] = f"{section_id}.{node_id}"
    return paths


def _render_section(
    section_id: str,
    section_label: str,
    nodes: list[FlowAgentNode | FlowInputNode | FlowOutputNode],
    node_paths: dict[tuple[str, tuple[str, ...], str], str],
    input_consumers: dict[tuple[tuple[str, ...], str], tuple[str, ...]],
    output_producers: dict[tuple[tuple[str, ...], str], tuple[str, ...]],
) -> list[str]:
    lines = [
        f"{section_id}: {{",
        f"  label: {_quoted(section_label)}",
        "  direction: right",
        "  style: {",
    ]
    fill, stroke = _section_palette(section_id)
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
        nested_id = node_paths[node_key].split(".", 1)[1]
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


def _node_label_lines(
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


def _section_palette(section_id: str) -> tuple[str, str]:
    if section_id == "shared_inputs":
        return ("#F5F8FF", "#2F6FEB")
    if section_id == "local_inputs":
        return ("#F8FAFC", "#94A3B8")
    if section_id == "agent_handoffs":
        return ("#FFF8EB", "#B54708")
    if section_id == "shared_outputs_and_carriers":
        return ("#F3FFF8", "#067647")
    return ("#F8FAFC", "#94A3B8")


def _wrap_lines(lines: tuple[str, ...] | list[str], *, width: int) -> str:
    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(textwrap.wrap(line, width=width) or [""])
    return "\n".join(wrapped)


def _quoted(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")
    return f"\"{escaped}\""
