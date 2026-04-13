from __future__ import annotations

from tempfile import TemporaryDirectory

from doctrine.compiler import extract_target_flow_graph
from doctrine.parser import parse_file

from doctrine._diagnostic_smoke.fixtures import _expect, _write_prompt


def run_flow_graph_checks() -> None:
    _check_flow_graph_extracts_routes_and_shared_io()


def _check_flow_graph_extracts_routes_and_shared_io() -> None:
    source = """input SharedInput: "Shared Input"
    source: Prompt
    shape: JsonObject
    requirement: Required

output DurableArtifact: "Durable Artifact"
    target: File
        path: "artifact.md"
    shape: MarkdownDocument
    requirement: Required

output CarrierComment: "Carrier Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the current artifact."

    trust_surface:
        current_artifact

agent RoutingOwner:
    role: "Own reroutes."
    workflow: "Routing"
        "Take the issue back."

agent WorkerA:
    role: "Produce the durable artifact."
    workflow: "Worker A"
        routing: "Routing"
            route "Escalate to RoutingOwner." -> RoutingOwner
        law:
            active when SharedInput.ready
            current artifact DurableArtifact via CarrierComment.current_artifact
            route "Return to RoutingOwner." -> RoutingOwner
    inputs: "Inputs"
        SharedInput
    outputs: "Outputs"
        DurableArtifact
        CarrierComment

agent WorkerB:
    role: "Read the same shared input."
    workflow: "Worker B"
        "Observe the shared handoff."
    inputs: "Inputs"
        SharedInput
    outputs: "Outputs"
        CarrierComment
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        graph = extract_target_flow_graph(prompt, ("RoutingOwner", "WorkerA", "WorkerB"))
        _expect(len(graph.inputs) == 1, f"expected 1 input node, got {len(graph.inputs)}")
        _expect(len(graph.outputs) == 2, f"expected 2 output nodes, got {len(graph.outputs)}")

        edges = {(edge.kind, edge.source_name, edge.target_name, edge.label) for edge in graph.edges}
        _expect(
            ("authored_route", "WorkerA", "RoutingOwner", "Escalate to RoutingOwner.") in edges,
            f"missing authored route edge: {edges}",
        )
        _expect(
            ("law_route", "WorkerA", "RoutingOwner", "Return to RoutingOwner.") in edges,
            f"missing workflow-law route edge: {edges}",
        )
        _expect(
            ("consume", "SharedInput", "WorkerA", "consumes") in edges,
            f"missing shared input consume edge for WorkerA: {edges}",
        )
        _expect(
            ("consume", "SharedInput", "WorkerB", "consumes") in edges,
            f"missing shared input consume edge for WorkerB: {edges}",
        )

        carrier_comment = next(
            (node for node in graph.outputs if node.name == "CarrierComment"),
            None,
        )
        _expect(carrier_comment is not None, "missing CarrierComment output node")
        _expect(
            carrier_comment is not None
            and "Current Artifact" in carrier_comment.trust_surface
            and "Carries current for Durable Artifact" in carrier_comment.notes,
            f"missing currentness carrier note on CarrierComment: {carrier_comment}",
        )

