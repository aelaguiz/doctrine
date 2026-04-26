from __future__ import annotations

import re

from doctrine import model


_NON_ID_CHARS = re.compile(r"[^a-zA-Z0-9_]+")


def render_skill_graph_mermaid(graph: model.ResolvedSkillGraph) -> str:
    lines = ["flowchart LR"]
    for stage in graph.stages:
        lines.append(
            f'    {_node_id(stage.canonical_name)}["{_label(stage)}"]'
        )
    for edge in graph.stage_edges:
        label = edge.why.replace('"', '\\"')
        lines.append(
            "    "
            f"{_node_id(edge.source_stage_name)} -->|{label}| "
            f"{_node_id(edge.target_stage_name)}"
        )
    return "\n".join(lines).rstrip() + "\n"


def _node_id(name: str) -> str:
    return "stage_" + _NON_ID_CHARS.sub("_", name).strip("_")


def _label(stage: model.ResolvedStage) -> str:
    bits = [stage.title, f"owner: {stage.owner_skill_name}"]
    if stage.lane_name is not None:
        bits.append(f"lane: {stage.lane_name}")
    return "<br/>".join(bit.replace('"', '\\"') for bit in bits)
