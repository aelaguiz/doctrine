from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from doctrine import model
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import (
    EmitTarget,
    SUPPORTED_ENTRYPOINTS,
    _validate_path_within_root,
    display_path,
    emit_error,
    ensure_supported_entrypoint,
    entrypoint_relative_dir,
    load_emit_targets,
    path_location,
    resolve_direct_emit_target,
    resolve_pyproject_path,
)
from doctrine.emit_skill import (
    _render_resolved_receipt_field,
    _render_resolved_receipt_json_schema,
    _render_resolved_receipt_route,
    _target_skill_package_decl,
)
from doctrine.flow_renderer import FlowRenderDependencyError, FlowRenderFailure, render_flow_svg
from doctrine.parser import parse_file
from doctrine.skill_graph_source_receipts import (
    SOURCE_RECEIPT_FILE_NAME,
    build_graph_source_receipt_payload,
    receipt_path_for_target as graph_receipt_path_for_target,
    render_graph_source_receipt_json,
)
from doctrine.skill_source_receipts import receipt_path_for_target as skill_receipt_path_for_target
from doctrine._skill_graph_render.d2 import render_skill_graph_d2
from doctrine._skill_graph_render.markdown import (
    render_flow_registry,
    render_graph_markdown,
    render_recovery_audit,
    render_skill_inventory,
    render_stage_contracts,
    render_stepwise_manifest,
)
from doctrine._skill_graph_render.mermaid import render_skill_graph_mermaid


GRAPH_CONTRACT_FILE = "SKILL_GRAPH.contract.json"
GRAPH_JSON_FILE = "references/skill-graph.json"
GRAPH_MARKDOWN_FILE = "references/skill-graph.md"
SKILL_INVENTORY_FILE = "references/skill-inventory.md"
FLOW_REGISTRY_FILE = "references/flow-registry.md"
STAGE_CONTRACTS_FILE = "references/stage-contracts.md"
RECOVERY_AUDIT_FILE = "references/recovery-audit.md"
STEPWISE_MANIFEST_FILE = "references/stepwise-manifest.md"
GRAPH_D2_FILE = "references/skill-graph.d2"
GRAPH_SVG_FILE = "references/skill-graph.svg"
GRAPH_MERMAID_FILE = "references/skill-graph.mmd"

DEFAULT_GRAPH_VIEW_PATHS = {
    "graph_contract": GRAPH_CONTRACT_FILE,
    "graph_source": SOURCE_RECEIPT_FILE_NAME,
    "graph_json": GRAPH_JSON_FILE,
    "graph_markdown": GRAPH_MARKDOWN_FILE,
    "skill_inventory": SKILL_INVENTORY_FILE,
    "flow_registry": FLOW_REGISTRY_FILE,
    "stage_contracts": STAGE_CONTRACTS_FILE,
    "recovery_audit": RECOVERY_AUDIT_FILE,
    "stepwise_manifest": STEPWISE_MANIFEST_FILE,
    "diagram_d2": GRAPH_D2_FILE,
    "diagram_svg": GRAPH_SVG_FILE,
    "diagram_mermaid": GRAPH_MERMAID_FILE,
}


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_arg_parser().parse_args(argv)
        config_path = (
            resolve_pyproject_path(args.pyproject)
            if args.target
            else Path(args.pyproject).resolve() if args.pyproject else None
        )
        for target in _resolve_requested_targets(args, config_path):
            emitted = emit_target_skill_graph(target)
            print(
                f"{target.name}: emitted {len(emitted)} file(s) to {display_path(target.output_dir)}"
            )
        return 0
    except DoctrineError as exc:
        print(exc, file=sys.stderr)
        return 1


def emit_target_skill_graph(
    target: EmitTarget,
    *,
    output_dir_override: Path | None = None,
) -> tuple[Path, ...]:
    ensure_supported_entrypoint(
        target.entrypoint,
        allowed_entrypoints=SUPPORTED_ENTRYPOINTS,
        owner_label=f"emit_skill_graph target `{target.name}`",
    )
    try:
        prompt_file = parse_file(target.entrypoint)
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"emit target `{target.name}` entrypoint",
            location=path_location(target.entrypoint),
        )

    session = CompilationSession(prompt_file, project_config=target.project_config)
    try:
        graph = session.compile_skill_graph(target.graph)
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"emit target `{target.name}`",
            location=path_location(target.entrypoint),
        )

    if not graph.stages and not graph.flows:
        raise emit_error(
            "E565",
            "Skill graph emit failed",
            f"Emit target `{target.name}` resolved graph `{graph.canonical_name}` but reached no flows or stages.",
            location=path_location(target.entrypoint),
        )

    output_root = (output_dir_override or target.output_dir).resolve()
    emitted_dir = output_root / entrypoint_relative_dir(target.entrypoint)
    emitted_dir.mkdir(parents=True, exist_ok=True)
    resolved_paths = _resolve_graph_view_paths(
        target=target,
        graph=graph,
        emitted_dir=emitted_dir,
    )

    files_to_write = {
        "graph_contract": json.dumps(_render_graph_contract(graph), indent=2, sort_keys=False)
        + "\n",
        "graph_json": json.dumps(_render_graph_query_json(graph), indent=2, sort_keys=False)
        + "\n",
        "graph_markdown": render_graph_markdown(graph),
        "skill_inventory": render_skill_inventory(graph),
        "flow_registry": render_flow_registry(graph),
        "stage_contracts": render_stage_contracts(graph),
        "recovery_audit": render_recovery_audit(graph),
        "stepwise_manifest": render_stepwise_manifest(graph),
        "diagram_d2": render_skill_graph_d2(graph),
        "diagram_mermaid": render_skill_graph_mermaid(graph),
    }

    emitted_paths: list[Path] = []
    for view_key, content in files_to_write.items():
        path = resolved_paths[view_key]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        emitted_paths.append(path)

    try:
        render_flow_svg(
            resolved_paths["diagram_d2"],
            resolved_paths["diagram_svg"],
        )
    except FlowRenderDependencyError as exc:
        raise emit_error(
            "E565",
            "Skill graph emit failed",
            str(exc),
            location=path_location(resolved_paths["diagram_d2"]),
            hints=exc.hints,
        ) from exc
    except FlowRenderFailure as exc:
        raise emit_error(
            "E565",
            "Skill graph emit failed",
            f"Could not render `{resolved_paths['diagram_svg'].name}` from `{resolved_paths['diagram_d2'].name}`: {exc}",
            location=path_location(resolved_paths["diagram_svg"]),
        ) from exc
    emitted_paths.append(resolved_paths["diagram_svg"])

    linked_package_receipts = _linked_package_receipts(target=target, graph=graph)
    input_paths = tuple(session.root_flow.member_paths)
    receipt_payload = build_graph_source_receipt_payload(
        target=target,
        graph=graph,
        input_paths=input_paths,
        emitted_dir=emitted_dir,
        emitted_paths=tuple(emitted_paths),
        linked_package_receipts=linked_package_receipts,
    )
    source_receipt_path = resolved_paths["graph_source"]
    source_receipt_path.write_text(
        render_graph_source_receipt_json(receipt_payload),
        encoding="utf-8",
    )
    emitted_paths.append(source_receipt_path)
    return tuple(emitted_paths)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Emit compiled skill-graph artifacts for configured Doctrine targets "
            "or a direct Doctrine entrypoint."
        )
    )
    parser.add_argument(
        "--pyproject",
        help=(
            "Path to the pyproject.toml that defines [tool.doctrine.emit]. "
            "Defaults to the nearest parent pyproject.toml from the current working directory."
        ),
    )
    parser.add_argument(
        "--target",
        action="append",
        help="Configured target name from [tool.doctrine.emit.targets]. Repeat to emit multiple targets.",
    )
    parser.add_argument(
        "--entrypoint",
        help=(
            "Direct Doctrine entrypoint to emit without a named target. "
            "Must point at a supported Doctrine entrypoint under a prompts/ tree."
        ),
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for direct entrypoint mode. Required with --entrypoint.",
    )
    parser.add_argument(
        "--graph",
        help=(
            "Direct mode graph name. Optional when exactly one visible graph is available."
        ),
    )
    return parser


def _resolve_requested_targets(
    args: argparse.Namespace,
    config_path: Path | None,
) -> tuple[EmitTarget, ...]:
    target_mode = bool(args.target)
    direct_mode = args.entrypoint is not None or args.output_dir is not None

    if target_mode and direct_mode:
        raise emit_error(
            "E563",
            "Invalid skill graph target",
            "Use either configured target mode (`--target`) or direct mode "
            "(`--entrypoint` with `--output-dir`), not both.",
            location=path_location(config_path),
        )

    if target_mode:
        if config_path is None:
            config_path = resolve_pyproject_path(args.pyproject)
        targets = load_emit_targets(config_path)
        resolved: list[EmitTarget] = []
        for target_name in args.target:
            target = targets.get(target_name)
            if target is None:
                raise emit_error(
                    "E563",
                    "Invalid skill graph target",
                    f"Emit target `{target_name}` is not defined in `pyproject.toml`.",
                    location=path_location(config_path),
                )
            resolved.append(target)
        return tuple(resolved)

    if direct_mode:
        if args.entrypoint is None or args.output_dir is None:
            raise emit_error(
                "E563",
                "Invalid skill graph target",
                "Direct `emit_skill_graph` mode requires both `--entrypoint` and `--output-dir`.",
                location=path_location(config_path),
                hints=(
                    "Use `--target <name>` for configured targets.",
                    "Use `--entrypoint path/to/SKILL.prompt --output-dir build` for direct mode.",
                ),
            )
        return (
            resolve_direct_emit_target(
                pyproject_path=config_path,
                start_dir=Path.cwd(),
                entrypoint=args.entrypoint,
                output_dir=args.output_dir,
                graph=args.graph,
                allowed_entrypoints=SUPPORTED_ENTRYPOINTS,
            ),
        )

    raise emit_error(
        "E563",
        "Invalid skill graph target",
        "Use configured target mode (`--target`) or direct mode (`--entrypoint` with `--output-dir`).",
        location=path_location(config_path),
        hints=(
            "Use `--target <name>` for configured targets.",
            "Use `--entrypoint path/to/SKILL.prompt --output-dir build` for direct mode.",
        ),
    )


def _resolve_graph_view_paths(
    *,
    target: EmitTarget,
    graph: model.ResolvedSkillGraph,
    emitted_dir: Path,
) -> dict[str, Path]:
    raw_paths = dict(DEFAULT_GRAPH_VIEW_PATHS)
    for view in graph.views:
        if view.key not in model.SKILL_GRAPH_VIEW_KEYS:
            raise emit_error(
                "E564",
                "Invalid skill graph view path",
                f"Skill graph `{graph.canonical_name}` declares unsupported view key `{view.key}`.",
                location=path_location(target.entrypoint),
            )
        raw_paths[view.key] = view.path

    resolved: dict[str, Path] = {}
    seen_paths: dict[Path, str] = {}
    for view_key, raw_path in raw_paths.items():
        candidate = Path(raw_path)
        path = candidate.resolve() if candidate.is_absolute() else (emitted_dir / candidate).resolve()
        _validate_path_within_root(
            candidate_path=path,
            root=emitted_dir,
            detail_prefix=f"Skill graph `{graph.canonical_name}` view `{view_key}`",
            code="E564",
            summary="Invalid skill graph view path",
        )
        existing_key = seen_paths.get(path)
        if existing_key is not None:
            raise emit_error(
                "E564",
                "Invalid skill graph view path",
                f"Skill graph `{graph.canonical_name}` maps both `{existing_key}` and `{view_key}` to `{display_path(path)}`.",
                location=path_location(path),
            )
        seen_paths[path] = view_key
        resolved[view_key] = path
    return resolved


def _render_graph_contract(graph: model.ResolvedSkillGraph) -> dict[str, object]:
    return {
        "contract_version": 1,
        "graph": {
            "name": graph.canonical_name,
            "title": graph.title,
            "purpose": graph.purpose,
        },
        "roots": [{"kind": root.kind, "name": root.name} for root in graph.roots],
        "sets": {
            entry.name: {"title": entry.title}
            for entry in graph.sets
        },
        "recovery": (
            None
            if graph.recovery is None
            else {
                "flow_receipt": graph.recovery.flow_receipt_name,
                "stage_status": graph.recovery.stage_status_name,
                "durable_artifact_status": graph.recovery.durable_artifact_status_name,
            }
        ),
        "policies": [
            {"action": policy.action, "key": policy.key}
            for policy in graph.policies
        ],
        "views": {
            view.key: view.path
            for view in graph.views
        },
        "skills": {
            skill.name: {
                "title": skill.title,
                "purpose": skill.purpose,
                "package_id": skill.package_id,
            }
            for skill in graph.skills
        },
        "stages": {
            stage.canonical_name: {
                "title": stage.title,
                "id": stage.stage_id,
                "owner": stage.owner_skill_name,
                "lane": stage.lane_name,
                "supports": list(stage.support_skill_names),
                "applies_to": list(stage.applies_to_flow_names),
                "inputs": {
                    entry.key: {
                        "kind": entry.type_kind,
                        "type": entry.type_name,
                    }
                    for entry in stage.inputs
                },
                "emits": stage.emits_receipt_name,
                "checkpoint": stage.checkpoint,
                "intent": stage.intent,
                "durable_target": stage.durable_target,
                "durable_evidence": stage.durable_evidence,
                "advance_condition": stage.advance_condition,
                "risk_guarded": stage.risk_guarded,
                "forbidden_outputs": list(stage.forbidden_outputs),
            }
            for stage in graph.stages
        },
        "flows": {
            flow.canonical_name: _render_graph_flow(flow)
            for flow in graph.flows
        },
        "receipts": {
            receipt.canonical_name: {
                "title": receipt.title,
                "fields": {
                    field.key: _render_resolved_receipt_field(field)
                    for field in receipt.fields
                },
                "routes": {
                    route.key: _render_resolved_receipt_route(route)
                    for route in receipt.routes
                },
                "json_schema": _render_resolved_receipt_json_schema(receipt),
            }
            for receipt in graph.receipts
        },
        "packages": {
            package.package_id: {
                "name": package.package_name,
                "title": package.package_title,
            }
            for package in graph.packages
        },
        "stage_edges": [
            _render_stage_edge(edge)
            for edge in graph.stage_edges
        ],
        "stage_successors": {
            key: list(values) for key, values in graph.stage_successors.items()
        },
        "stage_predecessors": {
            key: list(values) for key, values in graph.stage_predecessors.items()
        },
        "stage_reaching_flows": {
            key: list(values) for key, values in graph.stage_reaching_flows.items()
        },
    }


def _render_graph_query_json(graph: model.ResolvedSkillGraph) -> dict[str, object]:
    return {
        "graph": {
            "name": graph.canonical_name,
            "title": graph.title,
            "purpose": graph.purpose,
        },
        "roots": [{"kind": root.kind, "name": root.name} for root in graph.roots],
        "sets": [{"name": entry.name, "title": entry.title} for entry in graph.sets],
        "recovery": (
            None
            if graph.recovery is None
            else {
                "flow_receipt": graph.recovery.flow_receipt_name,
                "stage_status": graph.recovery.stage_status_name,
                "durable_artifact_status": graph.recovery.durable_artifact_status_name,
            }
        ),
        "policies": [
            {"action": policy.action, "key": policy.key}
            for policy in graph.policies
        ],
        "skills": [
            {
                "name": skill.name,
                "title": skill.title,
                "purpose": skill.purpose,
                "package_id": skill.package_id,
            }
            for skill in graph.skills
        ],
        "stages": [
            {
                "name": stage.canonical_name,
                "title": stage.title,
                "owner": stage.owner_skill_name,
                "lane": stage.lane_name,
                "reaching_flows": list(graph.stage_reaching_flows.get(stage.canonical_name, ())),
            }
            for stage in graph.stages
        ],
        "flows": [
            {
                "name": flow.canonical_name,
                "title": flow.title,
                "intent": flow.intent,
                "start": None if flow.start is None else {"kind": flow.start.kind, "name": flow.start.name},
                "approve": flow.approve,
            }
            for flow in graph.flows
        ],
        "receipts": [
            {
                "name": receipt.canonical_name,
                "title": receipt.title,
            }
            for receipt in graph.receipts
        ],
        "packages": [
            {
                "package_id": package.package_id,
                "name": package.package_name,
                "title": package.package_title,
            }
            for package in graph.packages
        ],
        "stage_edges": [_render_stage_edge(edge) for edge in graph.stage_edges],
    }


def _render_graph_flow(flow: model.ResolvedSkillGraphFlow) -> dict[str, object]:
    return {
        "title": flow.title,
        "intent": flow.intent,
        "start": None if flow.start is None else {"kind": flow.start.kind, "name": flow.start.name},
        "approve": flow.approve,
        "nodes": [
            {"kind": node.kind, "name": node.name}
            for node in flow.nodes
        ],
        "edges": [
            {
                "from": edge.source.name,
                "from_kind": edge.source.kind,
                "to": edge.target.name,
                "to_kind": edge.target.kind,
                "kind": edge.kind,
                "why": edge.why,
                "route": (
                    None
                    if edge.route is None
                    else {
                        "receipt": edge.route.receipt_name,
                        "field": edge.route.route_field_key,
                        "choice": edge.route.choice_key,
                    }
                ),
                "when": (
                    None
                    if edge.when is None
                    else {
                        "enum": edge.when.enum_name,
                        "member": edge.when.member_key,
                    }
                ),
            }
            for edge in flow.edges
        ],
        "repeat_nodes": {
            repeat.name: {
                "target_flow": repeat.target_flow_name,
                "over_kind": repeat.over_kind,
                "over": repeat.over_name,
                "order": repeat.order,
                "why": repeat.why,
            }
            for repeat in flow.repeats
        },
        "variations": {
            variation.name: {
                "title": variation.title,
                "safe_when": (
                    None
                    if variation.safe_when is None
                    else {
                        "enum": variation.safe_when.enum_name,
                        "member": variation.safe_when.member_key,
                    }
                ),
            }
            for variation in flow.variations
        },
        "unsafe_variations": {
            variation.name: {"title": variation.title}
            for variation in flow.unsafe_variations
        },
        "changed_workflow": (
            None
            if flow.changed_workflow is None
            else {
                "allow_provisional_flow": flow.changed_workflow.allow_provisional_flow,
                "requires": list(flow.changed_workflow.requires),
            }
        ),
        "terminals": list(flow.terminals),
    }


def _render_stage_edge(edge: model.ResolvedSkillGraphStageEdge) -> dict[str, object]:
    payload: dict[str, object] = {
        "from": edge.source_stage_name,
        "to": edge.target_stage_name,
        "via_flow": edge.via_flow_name,
        "kind": edge.kind,
        "why": edge.why,
    }
    if edge.route_receipt_name is not None:
        payload["route"] = (
            f"{edge.route_receipt_name}.{edge.route_field_key}.{edge.route_choice_key}"
        )
    return payload


def _linked_package_receipts(
    *,
    target: EmitTarget,
    graph: model.ResolvedSkillGraph,
) -> tuple[dict[str, object], ...]:
    config_path = target.project_config.path
    if config_path is None or not graph.packages:
        return tuple()
    try:
        targets = load_emit_targets(config_path)
    except DoctrineError:
        return tuple()
    package_targets: dict[str, list[EmitTarget]] = {}
    for candidate in targets.values():
        if candidate.name == target.name or candidate.graph is not None:
            continue
        if candidate.entrypoint.name != "SKILL.prompt":
            continue
        try:
            prompt_file = parse_file(candidate.entrypoint)
            session = CompilationSession(prompt_file, project_config=candidate.project_config)
            package_decl = _target_skill_package_decl(session)
        except DoctrineError:
            continue
        package_id = package_decl.metadata.name or package_decl.name
        package_targets.setdefault(package_id, []).append(candidate)

    linked: list[dict[str, object]] = []
    for package in graph.packages:
        matches = package_targets.get(package.package_id, ())
        if len(matches) != 1:
            continue
        match = matches[0]
        receipt_path = skill_receipt_path_for_target(match)
        if not receipt_path.is_file():
            continue
        linked.append(
            {
                "package_id": package.package_id,
                "target_name": match.name,
                "receipt_path": display_path(receipt_path.resolve()),
                "sha256": _sha256_file(receipt_path),
            }
        )
    return tuple(linked)


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
