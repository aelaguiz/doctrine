from __future__ import annotations

from doctrine import model


def render_graph_markdown(graph: model.ResolvedSkillGraph) -> str:
    lines = [f"# {graph.title}", "", graph.purpose, ""]
    lines.extend(["## Roots", ""])
    for root in graph.roots:
        lines.append(f"- `{root.kind} {root.name}`")
    if not graph.roots:
        lines.append("- None.")
    lines.append("")

    lines.extend(["## Sets", ""])
    if graph.sets:
        for entry in graph.sets:
            lines.append(f"- `{entry.name}`: {entry.title}")
    else:
        lines.append("- None.")
    lines.append("")

    lines.extend(["## Policy", ""])
    if graph.policies:
        for policy in graph.policies:
            suffix = f": {policy.reason}" if policy.reason else ""
            lines.append(f"- `{policy.action} {policy.key}`{suffix}")
    else:
        lines.append("- No graph policy lines.")
    lines.append("")

    lines.extend(["## Skill Relations", ""])
    if graph.skill_relations:
        for relation in graph.skill_relations:
            why = f" - {relation.why}" if relation.why else ""
            lines.append(
                f"- `{relation.source_skill_name}` {relation.kind} "
                f"`{relation.target_skill_name}`{why}"
            )
    else:
        lines.append("- No reached skill relations.")
    lines.append("")

    lines.extend(["## Warnings", ""])
    if graph.warnings:
        for warning in graph.warnings:
            lines.append(
                f"- `{warning.code}` `{warning.owner_kind} {warning.owner_name}`: "
                f"{warning.summary}. {warning.detail}"
            )
    else:
        lines.append("- No graph warnings.")
    lines.append("")

    lines.extend(["## Reached", ""])
    lines.append(f"- Flows: {len(graph.flows)}")
    lines.append(f"- Stages: {len(graph.stages)}")
    lines.append(f"- Skills: {len(graph.skills)}")
    lines.append(f"- Artifacts: {len(graph.artifacts)}")
    lines.append(f"- Receipts: {len(graph.receipts)}")
    lines.append(f"- Packages: {len(graph.packages)}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_skill_inventory(graph: model.ResolvedSkillGraph) -> str:
    lines = [
        "# Skill Inventory",
        "",
        "| Skill | Package | Purpose |",
        "| --- | --- | --- |",
    ]
    for skill in graph.skills:
        package_id = skill.package_id or "-"
        purpose = skill.purpose or "-"
        metadata = ", ".join(
            value
            for value in (
                f"category={skill.category}" if skill.category else "",
                f"visibility={skill.visibility}" if skill.visibility else "",
                f"manual_only={skill.manual_only}" if skill.manual_only else "",
                (
                    f"default_flow_member={skill.default_flow_member}"
                    if skill.default_flow_member
                    else ""
                ),
                f"aliases={skill.aliases}" if skill.aliases else "",
            )
            if value
        )
        suffix = f" ({metadata})" if metadata else ""
        lines.append(
            f"| {_md_cell(skill.title + suffix)} | {_md_code(package_id)} | "
            f"{_md_cell(purpose)} |"
        )
    if not graph.skills:
        lines.append("| - | - | No reached skills. |")
    lines.append("")
    lines.extend(
        [
            "## Relations",
            "",
            "| Source | Kind | Target | Why |",
            "| --- | --- | --- | --- |",
        ]
    )
    if graph.skill_relations:
        for relation in graph.skill_relations:
            lines.append(
                f"| {_md_code(relation.source_skill_name)} | {_md_code(relation.kind)} | "
                f"{_md_code(relation.target_skill_name)} | {_md_cell(relation.why or '-')} |"
            )
    else:
        lines.append("| - | - | - | No reached skill relations. |")
    lines.append("")
    return "\n".join(lines)


def render_flow_registry(graph: model.ResolvedSkillGraph) -> str:
    lines = ["# Flow Registry", ""]
    for flow in graph.flows:
        lines.extend(
            [
                f"## {flow.title}",
                "",
                f"- Name: `{flow.canonical_name}`",
                f"- Intent: {flow.intent or '-'}",
                f"- Start: {_render_node(flow.start)}",
                f"- Approve: `{flow.approve}`" if flow.approve else "- Approve: -",
                f"- Terminals: {', '.join(f'`{name}`' for name in flow.terminals) or '-'}",
                "",
                "### Edges",
                "",
                "| From | To | Kind | Route | When | Why |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        if flow.edges:
            for edge in flow.edges:
                route_text = (
                    "-"
                    if edge.route is None
                    else (
                        f"`{edge.route.receipt_name}.{edge.route.route_field_key}."
                        f"{edge.route.choice_key}`"
                    )
                )
                when_text = (
                    "-"
                    if edge.when is None
                    else f"`{edge.when.enum_name}.{edge.when.member_key}`"
                )
                lines.append(
                    "| "
                    f"{_md_code(edge.source.name)} ({_md_cell(edge.source.kind)}) | "
                    f"{_md_code(edge.target.name)} ({_md_cell(edge.target.kind)}) | "
                    f"{_md_code(edge.kind)} | {_md_cell(route_text)} | "
                    f"{_md_cell(when_text)} | {_md_cell(edge.why)} |"
                )
        else:
            lines.append("| - | - | - | - | - | No authored edges. |")
        lines.extend(["", "### Repeats", "", "| Repeat | Flow | Over | Order | Why |", "| --- | --- | --- | --- | --- |"])
        if flow.repeats:
            for repeat in flow.repeats:
                lines.append(
                    f"| {_md_code(repeat.name)} | {_md_code(repeat.target_flow_name)} | "
                    f"{_md_code(f'{repeat.over_kind}:{repeat.over_name}')} | "
                    f"{_md_code(repeat.order)} | {_md_cell(repeat.why)} |"
                )
        else:
            lines.append("| - | - | - | - | No repeat nodes. |")
        lines.append("")
    if not graph.flows:
        lines.extend(["No reached flows.", ""])
    return "\n".join(lines)


def render_stage_contracts(graph: model.ResolvedSkillGraph) -> str:
    lines = ["# Stage Contracts", ""]
    for stage in graph.stages:
        lines.extend(
            [
                f"## {stage.title}",
                "",
                f"- Name: `{stage.canonical_name}`",
                f"- Id: `{stage.stage_id}`" if stage.stage_id else "- Id: -",
                f"- Owner: `{stage.owner_skill_name}`",
                f"- Lane: `{stage.lane_name}`" if stage.lane_name else "- Lane: -",
                (
                    "- Supports: "
                    + ", ".join(f"`{name}`" for name in stage.support_skill_names)
                    if stage.support_skill_names
                    else "- Supports: -"
                ),
                (
                    "- Applies to: "
                    + ", ".join(f"`{name}`" for name in stage.applies_to_flow_names)
                    if stage.applies_to_flow_names
                    else "- Applies to: -"
                ),
                f"- Emits: `{stage.emits_receipt_name}`"
                if stage.emits_receipt_name
                else "- Emits: -",
                (
                    "- Artifacts: "
                    + ", ".join(f"`{name}`" for name in stage.artifact_names)
                    if stage.artifact_names
                    else "- Artifacts: -"
                ),
                f"- Checkpoint: `{stage.checkpoint}`",
                f"- Intent: {stage.intent}",
                f"- Durable target: {stage.durable_target or '-'}",
                f"- Durable evidence: {stage.durable_evidence or '-'}",
                f"- Advance condition: {stage.advance_condition}",
                f"- Risk guarded: {stage.risk_guarded or '-'}",
                f"- Entry: {stage.entry or '-'}",
                f"- Repair routes: {stage.repair_routes or '-'}",
                f"- Waiver policy: {stage.waiver_policy or '-'}",
                (
                    "- Forbidden outputs: "
                    + ", ".join(f"`{value}`" for value in stage.forbidden_outputs)
                    if stage.forbidden_outputs
                    else "- Forbidden outputs: -"
                ),
                "",
                "### Inputs",
                "",
                "| Key | Kind | Type |",
                "| --- | --- | --- |",
            ]
        )
        if stage.inputs:
            for entry in stage.inputs:
                lines.append(
                    f"| {_md_code(entry.key)} | {_md_code(entry.type_kind)} | "
                    f"{_md_code(entry.type_name)} |"
                )
        else:
            lines.append("| - | - | No typed inputs. |")
        lines.append("")
    if not graph.stages:
        lines.extend(["No reached stages.", ""])
    return "\n".join(lines)


def render_artifact_inventory(graph: model.ResolvedSkillGraph) -> str:
    lines = [
        "# Artifact Inventory",
        "",
        "| Artifact | Owner stage | Path family | Location | Intent |",
        "| --- | --- | --- | --- | --- |",
    ]
    if graph.artifacts:
        for artifact in graph.artifacts:
            path_family = (
                "-"
                if artifact.path_family_name is None
                else f"`{artifact.path_family_kind}:{artifact.path_family_name}`"
            )
            location_parts = [
                value
                for value in (
                    f"path={artifact.path}" if artifact.path else "",
                    f"section={artifact.section}" if artifact.section else "",
                    f"anchor={artifact.anchor}" if artifact.anchor else "",
                )
                if value
            ]
            lines.append(
                f"| {_md_code(artifact.name)} | {_md_code(artifact.owner_stage_name)} | "
                f"{_md_cell(path_family)} | {_md_cell(', '.join(location_parts) or '-')} | "
                f"{_md_cell(artifact.intent or '-')} |"
            )
    else:
        lines.append("| - | - | - | - | No reached artifacts. |")
    lines.append("")
    return "\n".join(lines)


def render_recovery_audit(graph: model.ResolvedSkillGraph) -> str:
    lines = ["# Recovery Audit", ""]
    if graph.recovery is None:
        lines.extend(["No recovery refs were declared on this graph.", ""])
        return "\n".join(lines)
    lines.extend(
        [
            "| Key | Target |",
            "| --- | --- |",
            f"| {_md_code('flow_receipt')} | {_md_code(graph.recovery.flow_receipt_name or '-')} |",
            f"| {_md_code('stage_status')} | {_md_code(graph.recovery.stage_status_name or '-')} |",
            "| `durable_artifact_status` | "
            f"{_md_code(graph.recovery.durable_artifact_status_name or '-')} |",
            "",
            "This is a static authoring audit. It does not claim live runtime state.",
            "",
        ]
    )
    return "\n".join(lines)


def render_stepwise_manifest(graph: model.ResolvedSkillGraph) -> str:
    lines = ["# Stepwise Manifest", ""]
    lines.extend(["## Root order", ""])
    for index, root in enumerate(graph.roots, start=1):
        lines.append(f"{index}. `{root.kind} {root.name}`")
    if not graph.roots:
        lines.append("1. No roots.")
    lines.extend(["", "## Reached stage order", ""])
    for index, stage in enumerate(graph.stages, start=1):
        flow_names = ", ".join(
            f"`{name}`"
            for name in graph.stage_reaching_flows.get(stage.canonical_name, ())
        )
        lines.append(
            f"{index}. `{stage.canonical_name}`"
            + (f" via {flow_names}" if flow_names else "")
        )
    if not graph.stages:
        lines.append("1. No reached stages.")
    lines.extend(
        [
            "",
            "This is a static generated reference. It does not claim live progress.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_node(node: model.ResolvedSkillFlowNode | None) -> str:
    if node is None:
        return "-"
    return f"`{node.name}` ({node.kind})"


def _md_cell(value: object) -> str:
    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")


def _md_code(value: object) -> str:
    escaped = _md_cell(value).replace("`", "\\`")
    return f"`{escaped}`"
