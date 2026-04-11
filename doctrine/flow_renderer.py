from __future__ import annotations

import subprocess
import textwrap
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

    for node in graph.inputs:
        lines.extend(_render_node(_node_id("input", node.module_parts, node.name), node))
        lines.append("")
    for node in graph.agents:
        lines.extend(_render_node(_node_id("agent", node.module_parts, node.name), node))
        lines.append("")
    for node in graph.outputs:
        lines.extend(_render_node(_node_id("output", node.module_parts, node.name), node))
        lines.append("")

    for edge in graph.edges:
        lines.extend(_render_edge(edge))
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
) -> list[str]:
    label_lines = [node.title]
    if isinstance(node, FlowInputNode):
        label_lines.append("Input")
    elif isinstance(node, FlowOutputNode):
        label_lines.append("Output")
    else:
        label_lines.append("Agent")

    label_lines.extend(node.detail_lines)
    if isinstance(node, FlowOutputNode) and node.trust_surface:
        label_lines.append("Trust: " + ", ".join(node.trust_surface))
    label_lines.extend(node.notes)

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


def _render_edge(edge: FlowEdge) -> list[str]:
    source_id = _node_id(edge.source_kind, edge.source_module_parts, edge.source_name)
    target_id = _node_id(edge.target_kind, edge.target_module_parts, edge.target_name)
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
