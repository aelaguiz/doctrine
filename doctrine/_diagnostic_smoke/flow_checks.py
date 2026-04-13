from __future__ import annotations

import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory

from doctrine.compiler import compile_prompt, extract_target_flow_graph
from doctrine.emit_flow import main as emit_flow_main
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown

from doctrine._diagnostic_smoke.fixtures import (
    SmokeFailure,
    _expect,
    _flow_visualizer_showcase_source,
    _write_prompt,
)


def run_flow_checks() -> None:
    _check_route_output_read_requires_guard()
    _check_handoff_routing_output_can_render_route_semantics()
    _check_route_from_final_output_can_render_selected_owner()
    _check_route_choice_guard_can_narrow_route_summary()
    _check_route_from_selector_rejects_workflow_local_mode()
    _check_route_from_rejects_duplicate_route_choice()
    _check_route_summary_needs_one_selected_branch()
    _check_handoff_routing_law_rejects_currentness_statements()
    _check_non_route_slot_law_has_specific_code()
    _check_route_only_output_can_render_route_semantics()
    _check_flow_graph_extracts_routes_and_shared_io()
    _check_emit_flow_uses_entrypoint_stem_for_output_name()
    _check_emit_flow_rejects_skill_entrypoints()
    _check_emit_flow_direct_mode_groups_shared_surfaces()
    _check_emit_flow_direct_mode_requires_output_dir()
    _check_emit_flow_direct_mode_rejects_output_dir_outside_project_root()


def _check_route_output_read_requires_guard() -> None:
    source = """input RouteFacts: "Route Facts"
    source: Prompt
    shape: JsonObject
    requirement: Required
    should_route: "Should Route"

agent ReviewLead:
    role: "Own routed follow-up."
    workflow: "Follow Up"
        "Take the routed follow-up."

output MaybeRoutedReply: "Maybe Routed Reply"
    target: TurnResponse
    shape: Comment
    requirement: Required

    next_owner: route.next_owner

workflow MaybeRoutedWorkflow: "Maybe Routed Workflow"
    "Route only when the host facts require it."

    law:
        active when true
        current none
        stop "Reply and stop."
        route "Hand off to ReviewLead." -> ReviewLead when RouteFacts.should_route

agent MaybeRouteBindingDemo:
    role: "Fail loud when unguarded route reads span unrouted branches."
    workflow: MaybeRoutedWorkflow
    inputs: "Inputs"
        RouteFacts
    outputs: "Outputs"
        MaybeRoutedReply
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "MaybeRouteBindingDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect("route semantics are not live on every branch" in str(exc), str(exc))
            _expect("guard the read with `route.exists`" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for unguarded route output read, but compilation succeeded")


def _check_handoff_routing_output_can_render_route_semantics() -> None:
    source = """agent ReviewLead:
    role: "Own routed follow-up."
    workflow: "Follow Up"
        "Take the routed follow-up."

output HandoffRouteBindingComment: "Handoff Route Binding Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    next_owner: route.next_owner

    route_summary: "Route Summary"
        "{{route.summary}}"

agent HandoffRouteBindingDemo:
    role: "Read route truth from handoff routing."
    outputs: "Outputs"
        HandoffRouteBindingComment

    handoff_routing: "Handoff Routing"
        "Route through compiler-owned handoff routing."

        law:
            active when true
            stop "Hand off or finish the turn."
            route "Hand off to ReviewLead." -> ReviewLead
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "HandoffRouteBindingDemo"))
        _expect("## Handoff Routing" in rendered, rendered)
        _expect("- Next Owner: Review Lead" in rendered, rendered)
        _expect("Hand off to ReviewLead. Next owner: Review Lead." in rendered, rendered)


def _check_route_from_final_output_can_render_selected_owner() -> None:
    source = """enum ProofRoute: "Proof Route"
    accept: "Accept"
    change: "Change"

output ProofResult: "Proof Result"
    target: TurnResponse
    shape: Comment
    requirement: Required
    route_choice: "Route Choice"

output RouteFromReply: "Route From Reply"
    target: TurnResponse
    shape: Comment
    requirement: Required

    next_owner: route.next_owner.key

agent AcceptanceCritic:
    role: "Accept routed work."

agent ChangeEngineer:
    role: "Change routed work."

agent RouteFromFinalOutputDemo:
    role: "Read selected owner truth from route_from."
    outputs: "Outputs"
        ProofResult
        RouteFromReply
    final_output: RouteFromReply

    handoff_routing: "Handoff Routing"
        law:
            route_from ProofResult.route_choice as ProofRoute:
                ProofRoute.accept:
                    route "Send to AcceptanceCritic." -> AcceptanceCritic
                ProofRoute.change:
                    route "Send to ChangeEngineer." -> ChangeEngineer
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "RouteFromFinalOutputDemo"))
        _expect("- Next Owner: the selected route's next owner key" in rendered, rendered)
        _expect("Select one route from ProofResult.route_choice." in rendered, rendered)


def _check_route_choice_guard_can_narrow_route_summary() -> None:
    source = """enum ProofRoute: "Proof Route"
    accept: "Accept"
    change: "Change"

output ProofResult: "Proof Result"
    target: TurnResponse
    shape: Comment
    requirement: Required
    route_choice: "Route Choice"

output RouteChoiceReply: "Route Choice Reply"
    target: TurnResponse
    shape: Comment
    requirement: Required

    accept_summary: "Accept Summary" when route.choice == ProofRoute.accept
        "{{route.summary}}"

agent AcceptanceCritic:
    role: "Accept routed work."

agent ChangeEngineer:
    role: "Change routed work."

agent RouteChoiceGuardDemo:
    role: "Use route.choice to narrow route detail."
    outputs: "Outputs"
        ProofResult
        RouteChoiceReply

    handoff_routing: "Handoff Routing"
        law:
            route_from ProofResult.route_choice as ProofRoute:
                ProofRoute.accept:
                    route "Send to AcceptanceCritic." -> AcceptanceCritic
                ProofRoute.change:
                    route "Send to ChangeEngineer." -> ChangeEngineer
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "RouteChoiceGuardDemo"))
        _expect("Show this only when route.choice is Accept." in rendered, rendered)
        _expect("Send to AcceptanceCritic. Next owner: Acceptance Critic." in rendered, rendered)


def _check_route_from_selector_rejects_workflow_local_mode() -> None:
    source = """enum ProofRoute: "Proof Route"
    accept: "Accept"

output ProofResult: "Proof Result"
    target: TurnResponse
    shape: Comment
    requirement: Required

agent AcceptanceCritic:
    role: "Accept routed work."

agent InvalidRouteFromSelectorDemo:
    role: "Keep route_from selectors on declared surfaces."
    outputs: "Outputs"
        ProofResult

    handoff_routing: "Handoff Routing"
        law:
            mode pass_mode = ProofRoute.accept as ProofRoute
            route_from pass_mode as ProofRoute:
                ProofRoute.accept:
                    route "Send to AcceptanceCritic." -> AcceptanceCritic
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "InvalidRouteFromSelectorDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E346", f"expected E346, got {getattr(exc, 'code', None)}")
            _expect("pass_mode" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for invalid route_from selector, but compilation succeeded")


def _check_route_from_rejects_duplicate_route_choice() -> None:
    source = """enum ProofRoute: "Proof Route"
    accept: "Accept"
    change: "Change"

input RouteFacts: "Route Facts"
    source: Prompt
    shape: JsonObject
    requirement: Required
    route_choice: "Route Choice"

agent AcceptanceCritic:
    role: "Accept routed work."

agent BackupCritic:
    role: "Backup routed work."

agent ChangeEngineer:
    role: "Change routed work."

workflow DuplicateRouteFromWorkflow: "Duplicate Route From Workflow"
    law:
        current none
        route_from RouteFacts.route_choice as ProofRoute:
            ProofRoute.accept:
                route "Send to AcceptanceCritic." -> AcceptanceCritic
            ProofRoute.accept:
                route "Send to BackupCritic." -> BackupCritic
            ProofRoute.change:
                route "Send to ChangeEngineer." -> ChangeEngineer

agent DuplicateRouteFromDemo:
    role: "Reject duplicate route_from choices."
    inputs: "Inputs"
        RouteFacts
    workflow: DuplicateRouteFromWorkflow
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "DuplicateRouteFromDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E348", f"expected E348, got {getattr(exc, 'code', None)}")
            _expect("Accept" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for duplicate route_from choice, but compilation succeeded")


def _check_route_summary_needs_one_selected_branch() -> None:
    source = """enum ProofRoute: "Proof Route"
    accept: "Accept"
    change: "Change"

output ProofResult: "Proof Result"
    target: TurnResponse
    shape: Comment
    requirement: Required
    route_choice: "Route Choice"

output RouteSummaryReply: "Route Summary Reply"
    target: TurnResponse
    shape: Comment
    requirement: Required

    route_summary: "Route Summary"
        "{{route.summary}}"

agent AcceptanceCritic:
    role: "Accept routed work."

agent ChangeEngineer:
    role: "Change routed work."

agent AmbiguousRouteSummaryDemo:
    role: "Do not read branch-specific route detail without narrowing."
    outputs: "Outputs"
        ProofResult
        RouteSummaryReply

    handoff_routing: "Handoff Routing"
        law:
            route_from ProofResult.route_choice as ProofRoute:
                ProofRoute.accept:
                    route "Send to AcceptanceCritic." -> AcceptanceCritic
                ProofRoute.change:
                    route "Send to ChangeEngineer." -> ChangeEngineer
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "AmbiguousRouteSummaryDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E347", f"expected E347, got {getattr(exc, 'code', None)}")
            _expect("route.summary" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for ambiguous route.summary, but compilation succeeded")


def _check_handoff_routing_law_rejects_currentness_statements() -> None:
    source = """output SimpleReply: "Simple Reply"
    target: TurnResponse
    shape: CommentText
    requirement: Required

agent InvalidHandoffLawDemo:
    role: "Keep handoff routing limited to route semantics."
    outputs: "Outputs"
        SimpleReply

    handoff_routing: "Handoff Routing"
        law:
            current none
            stop "Reply and stop."
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "InvalidHandoffLawDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E344", f"expected E344, got {getattr(exc, 'code', None)}")
            _expect("current none" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for invalid handoff_routing law, but compilation succeeded")


def _check_non_route_slot_law_has_specific_code() -> None:
    source = """output SimpleReply: "Simple Reply"
    target: TurnResponse
    shape: CommentText
    requirement: Required

agent InvalidSlotLawDemo:
    role: "Keep law off plain authored slots."
    outputs: "Outputs"
        SimpleReply

    your_job: "Your Job"
        law:
            stop "Reply and stop."
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "InvalidSlotLawDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E345", f"expected E345, got {getattr(exc, 'code', None)}")
            _expect("your_job" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for law on plain authored slot, but compilation succeeded")


def _check_route_only_output_can_render_route_semantics() -> None:
    source = """input RouteFacts: "Route Facts"
    source: Prompt
    shape: JsonObject
    requirement: Required
    next_owner_unknown: "Next Owner Unknown"

output RouteOnlyHandoffOutput: "Routing Handoff Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    route_handoff: "Route Handoff" when route.exists:
        next_owner: route.next_owner

        route_readback: "Route Readback"
            "{{route.summary}}"

agent RoutingOwner:
    role: "Handle reroutes when specialist work cannot continue safely."
    workflow: "Instructions"
        "Take back the same issue when the next specialist owner is still not justified."

workflow RouteOnlyTurns: "Routing-Only Turns"
    "Handle turns that can only stop, reroute, or keep ownership explicit."

    law:
        active when true
        current none
        stop "No specialist artifact is current for this turn."
        route "Keep the issue on RoutingOwner until the next specialist owner is clear." -> RoutingOwner when RouteFacts.next_owner_unknown

agent RouteOnlyRouteBindingDemo:
    role: "Read route truth from a route-only comment output."
    workflow: RouteOnlyTurns
    inputs: "Inputs"
        RouteFacts
    outputs: "Outputs"
        RouteOnlyHandoffOutput
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "RouteOnlyRouteBindingDemo"))
        _expect("#### Route Handoff" in rendered, rendered)
        _expect("Show this only when a routed owner exists." in rendered, rendered)
        _expect("- Next Owner: Routing Owner" in rendered, rendered)
        _expect(
            "Keep the issue on RoutingOwner until the next specialist owner is clear. Next owner: Routing Owner."
            in rendered,
            rendered,
        )


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


def _check_emit_flow_uses_entrypoint_stem_for_output_name() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "demo" / "agents" / "demo_agent"
        prompts.mkdir(parents=True)
        agents_prompt = prompts / "AGENTS.prompt"
        soul_prompt = prompts / "SOUL.prompt"
        source = """input SharedInput: "Shared Input"
    source: Prompt
    shape: JsonObject
    requirement: Required

output SharedComment: "Shared Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

agent DemoAgent:
    role: "Own the demo flow."
    workflow: "Demo Flow"
        "Read the shared input and leave one comment."
    inputs: "Inputs"
        SharedInput
    outputs: "Outputs"
        SharedComment
"""
        agents_prompt.write_text(source)
        soul_prompt.write_text(source)
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "demo_agents"
entrypoint = "prompts/demo/agents/demo_agent/AGENTS.prompt"
output_dir = "build"

[[tool.doctrine.emit.targets]]
name = "demo_soul"
entrypoint = "prompts/demo/agents/demo_agent/SOUL.prompt"
output_dir = "build"
"""
        )
        exit_code = emit_flow_main(
            [
                "--pyproject",
                str(pyproject),
                "--target",
                "demo_agents",
                "--target",
                "demo_soul",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        agents_d2 = root / "build" / "demo" / "agents" / "demo_agent" / "AGENTS.flow.d2"
        agents_svg = root / "build" / "demo" / "agents" / "demo_agent" / "AGENTS.flow.svg"
        soul_d2 = root / "build" / "demo" / "agents" / "demo_agent" / "SOUL.flow.d2"
        soul_svg = root / "build" / "demo" / "agents" / "demo_agent" / "SOUL.flow.svg"
        _expect(agents_d2.is_file(), f"missing emitted AGENTS.flow.d2: {agents_d2}")
        _expect(agents_svg.is_file(), f"missing emitted AGENTS.flow.svg: {agents_svg}")
        _expect(soul_d2.is_file(), f"missing emitted SOUL.flow.d2: {soul_d2}")
        _expect(soul_svg.is_file(), f"missing emitted SOUL.flow.svg: {soul_svg}")


def _check_emit_flow_rejects_skill_entrypoints() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "skill_pkg"
        prompts.mkdir(parents=True)
        entrypoint = prompts / "SKILL.prompt"
        entrypoint.write_text(
            """skill package DemoSkill: "Demo Skill"
    metadata:
        name: "demo-skill"
    "This package should not emit flow artifacts."
"""
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "demo_skill"
entrypoint = "prompts/skill_pkg/SKILL.prompt"
output_dir = "build"
"""
        )

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_flow_main(
                [
                    "--pyproject",
                    str(pyproject),
                    "--target",
                    "demo_skill",
                ]
            )
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E510 emit error" in output, output)
        _expect("must point at `AGENTS.prompt` or `SOUL.prompt`" in output, output)


def _check_emit_flow_direct_mode_groups_shared_surfaces() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "showcase"
        prompts.mkdir(parents=True)
        entrypoint = prompts / "AGENTS.prompt"
        entrypoint.write_text(_flow_visualizer_showcase_source())
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[project]
name = "doctrine-smoke"
version = "0.0.0"
"""
        )

        exit_code = emit_flow_main(
            [
                "--pyproject",
                str(pyproject),
                "--entrypoint",
                str(entrypoint.relative_to(root)),
                "--output-dir",
                "build",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")

        d2_path = root / "build" / "showcase" / "AGENTS.flow.d2"
        svg_path = root / "build" / "showcase" / "AGENTS.flow.svg"
        _expect(d2_path.is_file(), f"missing emitted AGENTS.flow.d2: {d2_path}")
        _expect(svg_path.is_file(), f"missing emitted AGENTS.flow.svg: {svg_path}")

        rendered = d2_path.read_text()
        _expect("shared_inputs: {" in rendered, rendered)
        _expect("agent_handoffs: {" in rendered, rendered)
        _expect("shared_outputs_and_carriers: {" in rendered, rendered)
        _expect(rendered.startswith("direction: down\n"), rendered)
        _expect("Shared Input" in rendered, rendered)
        _expect("Shared Output / Carrier" in rendered, rendered)
        _expect("Used by:" in rendered, rendered)
        _expect("Produced by:" in rendered, rendered)
        _expect('primary_lane: {\n    label: ""\n    direction: down' in rendered, rendered)
        _expect(
            "agent_handoffs.primary_lane.agent_projectlead -> agent_handoffs.primary_lane.agent_researchspecialist"
            in rendered,
            rendered,
        )
        _expect(
            "agent_handoffs.primary_lane.agent_researchspecialist -> agent_handoffs.primary_lane.agent_writingspecialist"
            in rendered,
            rendered,
        )
        _expect(
            "agent_handoffs.primary_lane.agent_writingspecialist -> agent_handoffs.primary_lane.agent_projectlead"
            in rendered,
            rendered,
        )
        _expect("Start research with" in rendered, rendered)
        _expect("Return the draft to" in rendered, rendered)


def _check_emit_flow_direct_mode_requires_output_dir() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts"
        prompts.mkdir()
        entrypoint = prompts / "AGENTS.prompt"
        entrypoint.write_text(
            """agent DemoAgent:
    role: "Own the demo flow."
"""
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[project]
name = "doctrine-smoke"
version = "0.0.0"
"""
        )

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_flow_main(
                [
                    "--pyproject",
                    str(pyproject),
                    "--entrypoint",
                    str(entrypoint.relative_to(root)),
                ]
            )
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E518 emit error" in output, output)
        _expect("Direct emit flow mode requires entrypoint and output_dir" in output, output)


def _check_emit_flow_direct_mode_rejects_output_dir_outside_project_root() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts"
        prompts.mkdir()
        entrypoint = prompts / "AGENTS.prompt"
        entrypoint.write_text(
            """agent DemoAgent:
    role: "Own the demo flow."
"""
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[project]
name = "doctrine-smoke"
version = "0.0.0"
"""
        )

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_flow_main(
                [
                    "--pyproject",
                    str(pyproject),
                    "--entrypoint",
                    str(entrypoint.relative_to(root)),
                    "--output-dir",
                    "../outside",
                ]
            )
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E520 emit error" in output, output)
        _expect("outside the target project root" in output, output)
