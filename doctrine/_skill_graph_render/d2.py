from __future__ import annotations

import re

from doctrine import model


_NON_ID_CHARS = re.compile(r"[^a-zA-Z0-9_]+")
_SAFE_UNQUOTED_TITLE = re.compile(r"^[a-zA-Z0-9 _.-]+$")


def render_skill_graph_d2(graph: model.ResolvedSkillGraph) -> str:
    lines = [f"title: {_title_value(graph.title)}", "direction: right", ""]
    for stage in graph.stages:
        node_id = _node_id(stage.canonical_name)
        label_lines = [stage.title, f"owner: {stage.owner_skill_name}"]
        if stage.lane_name is not None:
            label_lines.append(f"lane: {stage.lane_name}")
        lines.append(f'{node_id}: "{_escape_label(label_lines)}"')
    if graph.stages:
        lines.append("")
    for edge in graph.stage_edges:
        label = _escape_label_text(edge.why)
        if edge.route_receipt_name is not None:
            label = (
                f"{label}\\nroute: {edge.route_receipt_name}."
                f"{edge.route_field_key}.{edge.route_choice_key}"
            )
        lines.append(
            f'{_node_id(edge.source_stage_name)} -> {_node_id(edge.target_stage_name)}: "{label}"'
        )
    return "\n".join(lines).rstrip() + "\n"


def _node_id(name: str) -> str:
    return "stage_" + _NON_ID_CHARS.sub("_", name).strip("_")


def _escape_label(lines: list[str]) -> str:
    return "\\n".join(_escape_label_text(line) for line in lines)


def _title_value(value: str) -> str:
    escaped = _escape_label_text(value)
    if _SAFE_UNQUOTED_TITLE.fullmatch(value):
        return escaped
    return f'"{escaped}"'


def _escape_label_text(value: str) -> str:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
