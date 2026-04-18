from __future__ import annotations

import contextlib
import io
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from doctrine._compiler.types import FlowAgentNode, FlowEdge, FlowGraph
from doctrine.compiler import CompilationSession, ProvidedPromptRoot
from doctrine.emit_common import (
    DOCS_ENTRYPOINTS,
    collect_runtime_emit_roots,
    load_emit_targets,
    resolve_direct_emit_target,
)
from doctrine.emit_flow import emit_target_flow, main as emit_flow_main
from doctrine.flow_renderer import render_flow_d2
from doctrine.parser import parse_file


class EmitFlowCliTests(unittest.TestCase):
    def _extract_graph(
        self,
        source: str,
        *,
        extra_files: dict[str, str] | None = None,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompts" / "AGENTS.prompt"
            prompt_path.parent.mkdir(parents=True)
            prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
            for rel_path, contents in (extra_files or {}).items():
                target_path = root / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(textwrap.dedent(contents), encoding="utf-8")
            prompt = parse_file(prompt_path)
            session = CompilationSession(prompt)
            runtime_roots = collect_runtime_emit_roots(session)
            return session.extract_target_flow_graph_from_units(
                tuple((root.unit, root.agent_name) for root in runtime_roots)
            )

    def test_extract_graph_adds_route_edges_for_final_output_route(self) -> None:
        graph = self._extract_graph(
            """
            output schema TurnResultSchema: "Turn Result Schema"
                route field next_route: "Next Route"
                    send_to_worker_b: "Send to Worker B." -> WorkerB

                field summary: "Summary"
                    type: string

                example:
                    next_route: "send_to_worker_b"
                    summary: "Hand work to WorkerB."

            output shape TurnResultJson: "Turn Result JSON"
                kind: JsonObject
                schema: TurnResultSchema

            output TurnResult: "Turn Result"
                target: TurnResponse
                shape: TurnResultJson
                requirement: Required

            agent WorkerB:
                role: "Take the routed handoff."
                workflow: "Act"
                    "Continue the turn."

            agent WorkerA:
                role: "Pick the next owner from the final output."
                workflow: "Route"
                    "Choose the next owner."
                outputs: "Outputs"
                    TurnResult
                final_output:
                    output: TurnResult
                    route: next_route
            """
        )
        edges = {(edge.kind, edge.source_name, edge.target_name, edge.label) for edge in graph.edges}
        self.assertIn(
            ("authored_route", "WorkerA", "WorkerB", "Send to Worker B."),
            edges,
        )

    def test_extract_graph_adds_route_edges_for_review_outcomes(self) -> None:
        graph = self._extract_graph(
            """
            input DraftPoem: "Draft Poem"
                source: File
                    path: "unit_root/DRAFT_POEM.md"
                shape: MarkdownDocument
                requirement: Required
                needs_revision: "Needs Revision"

            workflow PoemReviewContract: "Poem Review Contract"
                rhythm: "Rhythm"
                    "Confirm the poem keeps its rhythm."

            agent Publisher:
                role: "Take accepted poems to publishing."
                workflow: "Publish"
                    "Prepare the accepted poem."

            agent Muse:
                role: "Revise rejected poems."
                workflow: "Revise"
                    "Revise the poem before another review."

            output PoemReviewFinalResponse: "Poem Review Final Response"
                target: TurnResponse
                shape: Comment
                requirement: Required

                trust_surface:
                    current_artifact

                verdict: "Verdict"
                    "Say whether the poem passed review."

                reviewed_artifact: "Reviewed Artifact"
                    "Name the poem under review."

                analysis_performed: "Analysis Performed"
                    "Summarize the review analysis."

                output_contents_that_matter: "Output Contents That Matter"
                    "Summarize the parts the next owner should read first."

                current_artifact: "Current Artifact"
                    "Name the artifact that remains current after review."

                next_owner: "Next Owner"
                    "Name {{Publisher}} when the poem passes and {{Muse}} when it needs revision."

                failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                    failing_gates: "Failing Gates"
                        "List the failing review gates."

            review PoemReview: "Poem Review"
                subject: DraftPoem
                contract: PoemReviewContract
                comment_output: PoemReviewFinalResponse

                fields:
                    verdict: verdict
                    reviewed_artifact: reviewed_artifact
                    analysis: analysis_performed
                    readback: output_contents_that_matter
                    current_artifact: current_artifact
                    failing_gates: failure_detail.failing_gates
                    next_owner: next_owner

                contract_checks: "Contract Checks"
                    reject contract.rhythm when DraftPoem.needs_revision
                    accept "The poem review passes." when contract.passes

                on_accept: "If Accepted"
                    current artifact DraftPoem via PoemReviewFinalResponse.current_artifact
                    route "Accepted poem goes to Publisher." -> Publisher

                on_reject: "If Rejected"
                    current artifact DraftPoem via PoemReviewFinalResponse.current_artifact
                    route "Rejected poem returns to Muse." -> Muse

            agent Reviewer:
                role: "Review the poem and route the next owner."
                review: PoemReview
                inputs: "Inputs"
                    DraftPoem
                outputs: "Outputs"
                    PoemReviewFinalResponse
                final_output: PoemReviewFinalResponse
            """
        )
        edges = {(edge.kind, edge.source_name, edge.target_name, edge.label) for edge in graph.edges}
        self.assertIn(
            ("authored_route", "Reviewer", "Publisher", "Accepted poem goes to Publisher."),
            edges,
        )
        self.assertIn(
            ("authored_route", "Reviewer", "Muse", "Rejected poem returns to Muse."),
            edges,
        )

    def test_missing_node_reports_dependency_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompts = root / "prompts" / "demo"
            prompts.mkdir(parents=True)
            entrypoint = prompts / "AGENTS.prompt"
            entrypoint.write_text(
                """agent DemoAgent:
    role: "Own the demo flow."
"""
            )
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                """[project]
name = "doctrine-test"
version = "0.0.0"
"""
            )
            helper = root / "flow_svg.mjs"
            helper.write_text("// test helper stub\n")
            package_json = root / "package.json"
            package_json.write_text("{}\n")

            stderr = io.StringIO()
            with (
                patch("doctrine.flow_renderer.D2_HELPER_PATH", helper),
                patch("doctrine.flow_renderer.D2_PACKAGE_PATH", package_json),
                patch(
                    "doctrine.flow_renderer.subprocess.run",
                    side_effect=FileNotFoundError("node"),
                ),
                contextlib.redirect_stderr(stderr),
            ):
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

        output = stderr.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("E515 emit error", output)
        self.assertIn("Flow renderer prerequisite is unavailable", output)
        self.assertIn("Node.js is required to render flow SVG output", output)
        self.assertNotIn("Run `npm ci` at the repo root.", output)

    def test_missing_helper_reports_dependency_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompts = root / "prompts" / "demo"
            prompts.mkdir(parents=True)
            entrypoint = prompts / "AGENTS.prompt"
            entrypoint.write_text(
                """agent DemoAgent:
    role: "Own the demo flow."
"""
            )
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                """[project]
name = "doctrine-test"
version = "0.0.0"
"""
            )
            missing_helper = root / "missing_flow_svg.mjs"
            package_json = root / "node_modules" / "@terrastruct" / "d2" / "package.json"
            package_json.parent.mkdir(parents=True)
            package_json.write_text("{}\n")

            stderr = io.StringIO()
            with (
                patch("doctrine.flow_renderer.D2_HELPER_PATH", missing_helper),
                patch("doctrine.flow_renderer.D2_PACKAGE_PATH", package_json),
                patch(
                    "doctrine.flow_renderer.subprocess.run",
                    side_effect=AssertionError("renderer should not run without the helper"),
                ),
                contextlib.redirect_stderr(stderr),
            ):
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

        output = stderr.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("E515 emit error", output)
        self.assertIn("Flow renderer prerequisite is unavailable", output)
        self.assertIn("Doctrine flow renderer helper is missing", output)
        self.assertIn("Restore the `flow_svg.mjs` helper file.", output)

    def test_renderer_exit_reports_failure_detail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompts = root / "prompts" / "demo"
            prompts.mkdir(parents=True)
            entrypoint = prompts / "AGENTS.prompt"
            entrypoint.write_text(
                """agent DemoAgent:
    role: "Own the demo flow."
"""
            )
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                """[project]
name = "doctrine-test"
version = "0.0.0"
"""
            )
            helper = root / "flow_svg.mjs"
            helper.write_text("// test helper stub\n")
            package_json = root / "node_modules" / "@terrastruct" / "d2" / "package.json"
            package_json.parent.mkdir(parents=True)
            package_json.write_text("{}\n")

            stderr = io.StringIO()
            with (
                patch("doctrine.flow_renderer.D2_HELPER_PATH", helper),
                patch("doctrine.flow_renderer.D2_PACKAGE_PATH", package_json),
                patch(
                    "doctrine.flow_renderer.subprocess.run",
                    return_value=subprocess.CompletedProcess(
                        args=["node", str(helper)],
                        returncode=9,
                        stdout="",
                        stderr="render crashed",
                    ),
                ),
                contextlib.redirect_stderr(stderr),
            ):
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

        output = stderr.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("E516 emit error", output)
        self.assertIn("Pinned D2 renderer failed", output)
        self.assertIn("Could not render `AGENTS.flow.svg` from `AGENTS.flow.d2`: render crashed", output)

    def test_split_review_final_outputs_keep_review_bound_trust_surface_in_flow(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for prompt_rel_path, output_name in (
            (
                "examples/84_review_split_final_output_prose/prompts/AGENTS.prompt",
                "DraftReviewDecision",
            ),
            (
                "examples/85_review_split_final_output_output_schema/prompts/AGENTS.prompt",
                "AcceptanceControlFinalResponse",
            ),
        ):
            with self.subTest(prompt=prompt_rel_path):
                prompt = parse_file(repo_root / prompt_rel_path)

                # Split review final outputs inherit current-artifact truth from
                # the attached review. Flow extraction must keep that label live,
                # or shipped flow emit targets can fail before they render.
                session = CompilationSession(prompt)
                runtime_roots = collect_runtime_emit_roots(session)
                graph = session.extract_target_flow_graph_from_units(
                    tuple((root.unit, root.agent_name) for root in runtime_roots)
                )
                outputs = {node.name: node for node in graph.outputs}

                self.assertIn(output_name, outputs)
                self.assertEqual(outputs[output_name].trust_surface, ("Current Artifact",))

    def test_imported_review_comment_output_keeps_split_final_output_truth_live_in_flow(
        self,
    ) -> None:
        # Imported review bindings and local split final outputs meet at one
        # compiler story. Flow extraction must keep Current Artifact live for
        # both outputs, or shipped flow docs can drift from rendered markdown.
        graph = self._extract_graph(
            """
            input DraftSpec: "Draft Spec"
                source: File
                    path: "unit_root/DRAFT_SPEC.md"
                shape: MarkdownDocument
                requirement: Required

            workflow DraftReviewContract: "Draft Review Contract"
                completeness: "Completeness"
                    "Confirm the draft covers the required sections."

            agent ReviewLead:
                role: "Own accepted draft follow-up."
                workflow: "Follow Up"
                    "Take the accepted draft to the next planning step."

            agent DraftAuthor:
                role: "Fix rejected draft defects."
                workflow: "Revise"
                    "Revise the same draft when review requests changes."

            output DraftReviewDecision: "Draft Review Decision"
                target: TurnResponse
                shape: CommentText
                requirement: Required

                trust_surface:
                    current_artifact

                control_summary: "Control Summary"
                    "End with one short control summary for the routed owner."

                standalone_read: "Standalone Read"
                    "The final control summary should stand on its own for the routed owner."

            review DraftReview: "Draft Review"
                subject: DraftSpec
                contract: DraftReviewContract
                comment_output: DraftReviewComment

                fields:
                    verdict: verdict
                    reviewed_artifact: reviewed_artifact
                    analysis: analysis_performed
                    readback: output_contents_that_matter
                    current_artifact: current_artifact
                    failing_gates: failure_detail.failing_gates
                    next_owner: next_owner

                contract_checks: "Contract Checks"
                    accept "The shared draft review contract passes." when contract.passes

                on_accept: "If Accepted"
                    current artifact DraftSpec via DraftReviewComment.current_artifact
                    route "Accepted draft returns to ReviewLead." -> ReviewLead

                on_reject: "If Rejected"
                    current artifact DraftSpec via DraftReviewComment.current_artifact
                    route "Rejected draft returns to DraftAuthor." -> DraftAuthor

            agent ImportedDraftReviewSplitDemo:
                role: "Use an imported review comment output and a local control-only final output."
                review: DraftReview
                inputs: "Inputs"
                    DraftSpec
                outputs: "Outputs"
                    DraftReviewComment
                    DraftReviewDecision
                final_output: DraftReviewDecision
            """,
            extra_files={
                "prompts/shared/review.prompt": """
                output DraftReviewComment: "Draft Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    verdict: "Verdict"
                        "Say whether the review accepted the draft or requested changes."

                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."

                    analysis_performed: "Analysis Performed"
                        "Summarize the review analysis that led to the verdict."

                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize the parts of the draft the next owner must read first."

                    current_artifact: "Current Artifact"
                        "Name the artifact that remains current after review."

                    next_owner: "Next Owner"
                        "Name the next owner, including {{ReviewLead}} when the draft is accepted and {{DraftAuthor}} when the draft is rejected."

                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "Name the failing review gates in authored order."

                    trust_surface:
                        current_artifact

                    standalone_read: "Standalone Read"
                        "A downstream owner should be able to read this review alone and understand the verdict, current artifact, and next owner."
                """,
            },
        )
        outputs = {node.name: node for node in graph.outputs}

        self.assertIn("DraftReviewComment", outputs)
        self.assertEqual(outputs["DraftReviewComment"].trust_surface, ("Current Artifact",))
        self.assertIn("DraftReviewDecision", outputs)
        self.assertEqual(outputs["DraftReviewDecision"].trust_surface, ("Current Artifact",))

    def test_emit_target_flow_keeps_imported_carrier_trust_labels_in_d2(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        prompt_path = (
            repo_root / "examples/86_imported_review_comment_local_routes/prompts/AGENTS.prompt"
        )
        with tempfile.TemporaryDirectory(dir=repo_root) as temp_dir:
            output_dir = Path(temp_dir) / "build"
            target = resolve_direct_emit_target(
                entrypoint=prompt_path,
                output_dir=output_dir,
                start_dir=repo_root,
                name="imported-review-flow",
                allowed_entrypoints=DOCS_ENTRYPOINTS,
            )

            emitted = emit_target_flow(target, include_svg=False)

            # Imported review carriers and local split final outputs are one public
            # flow story. The emitted D2 file must keep both carrier labels and their
            # Current Artifact trust surface, or shipped flow docs drift from compile.
            self.assertEqual(len(emitted), 1)
            d2_text = emitted[0].read_text(encoding="utf-8")

        self.assertIn("shared_review_draftreviewcomment:", d2_text)
        self.assertIn("Draft Review Comment\\nShared Output / Carrier", d2_text)
        self.assertIn(
            "ImportedDraftReviewDemo,\\nImportedDraftReviewSplitDemo\\nTrust: Current Artifact",
            d2_text,
        )
        self.assertIn("draftreviewdecision:", d2_text)
        self.assertIn("Draft Review Decision\\nCarrier Output", d2_text)
        self.assertIn(
            "Produced by:\\nImportedDraftReviewSplitDemo\\nTrust: Current Artifact",
            d2_text,
        )

    def test_render_flow_d2_keeps_side_branch_agents_out_of_route_starts(self) -> None:
        # A routed side branch is not a new route start. The public D2 file must
        # place that agent in a secondary lane, or the flow diagram lies about
        # where routing begins and which agent is the branch point.
        graph = FlowGraph(
            agents=(
                FlowAgentNode(module_parts=(), name="A", title="A"),
                FlowAgentNode(module_parts=(), name="B", title="B"),
                FlowAgentNode(module_parts=(), name="C", title="C"),
                FlowAgentNode(module_parts=(), name="D", title="D"),
            ),
            inputs=(),
            outputs=(),
            edges=(
                FlowEdge(
                    kind="authored_route",
                    source_kind="agent",
                    source_module_parts=(),
                    source_name="A",
                    target_kind="agent",
                    target_module_parts=(),
                    target_name="B",
                    label="A to B",
                ),
                FlowEdge(
                    kind="authored_route",
                    source_kind="agent",
                    source_module_parts=(),
                    source_name="B",
                    target_kind="agent",
                    target_module_parts=(),
                    target_name="C",
                    label="B to C",
                ),
                FlowEdge(
                    kind="authored_route",
                    source_kind="agent",
                    source_module_parts=(),
                    source_name="B",
                    target_kind="agent",
                    target_module_parts=(),
                    target_name="D",
                    label="B to D",
                ),
            ),
        )

        d2_text = render_flow_d2(graph)

        self.assertNotIn("route_starts:", d2_text)
        self.assertIn("secondary_lanes:", d2_text)
        self.assertIn(
            "agent_handoffs.primary_lane.agent_b -> agent_handoffs.secondary_lanes.agent_d",
            d2_text,
        )
        self.assertNotIn(
            "agent_handoffs.primary_lane.agent_b -> agent_handoffs.route_starts.agent_d",
            d2_text,
        )

    def test_render_flow_d2_keeps_true_multi_start_agents_in_route_starts(self) -> None:
        # When two routed starts converge into one shared lane, both starts should
        # stay in the route-start column and the main lane should begin after them.
        graph = FlowGraph(
            agents=(
                FlowAgentNode(module_parts=(), name="A", title="A"),
                FlowAgentNode(module_parts=(), name="X", title="X"),
                FlowAgentNode(module_parts=(), name="Hub", title="Hub"),
                FlowAgentNode(module_parts=(), name="Y", title="Y"),
            ),
            inputs=(),
            outputs=(),
            edges=(
                FlowEdge(
                    kind="authored_route",
                    source_kind="agent",
                    source_module_parts=(),
                    source_name="A",
                    target_kind="agent",
                    target_module_parts=(),
                    target_name="Hub",
                    label="A to Hub",
                ),
                FlowEdge(
                    kind="authored_route",
                    source_kind="agent",
                    source_module_parts=(),
                    source_name="X",
                    target_kind="agent",
                    target_module_parts=(),
                    target_name="Hub",
                    label="X to Hub",
                ),
                FlowEdge(
                    kind="authored_route",
                    source_kind="agent",
                    source_module_parts=(),
                    source_name="Hub",
                    target_kind="agent",
                    target_module_parts=(),
                    target_name="Y",
                    label="Hub to Y",
                ),
            ),
        )

        d2_text = render_flow_d2(graph)

        self.assertIn("route_starts:", d2_text)
        self.assertIn("agent_a:", d2_text)
        self.assertIn("agent_x:", d2_text)
        self.assertIn("agent_hub:", d2_text)
        self.assertIn(
            "agent_handoffs.route_starts.agent_a -> agent_handoffs.primary_lane.agent_hub",
            d2_text,
        )
        self.assertIn(
            "agent_handoffs.route_starts.agent_x -> agent_handoffs.primary_lane.agent_hub",
            d2_text,
        )

    def test_extract_target_flow_graph_from_imported_runtime_package_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "runtime_home").mkdir(parents=True)
            (prompts / "runtime_home" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    input SharedInput: "Shared Input"
                        source: File
                            path: "unit_root/INPUT.md"
                        shape: MarkdownDocument
                        requirement: Required

                    agent RuntimeHome:
                        role: "Own the runtime package."
                        workflow: "Reply"
                            "Reply from the imported package."
                        inputs: "Inputs"
                            SharedInput
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    import runtime_home

                    agent BuildHandle:
                        role: "Own the build handle."
                    """
                ),
                encoding="utf-8",
            )

            session = CompilationSession(parse_file(prompts / "AGENTS.prompt"))
            runtime_unit = session.load_module(("runtime_home",))
            graph = session.extract_target_flow_graph_from_units(
                ((runtime_unit, "RuntimeHome"),)
            )

        self.assertEqual(
            tuple((node.module_parts, node.name) for node in graph.agents),
            ((("runtime_home",), "RuntimeHome"),),
        )

    def test_emit_target_flow_roots_on_imported_runtime_packages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "runtime_home").mkdir(parents=True)
            (prompts / "runtime_home" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent RuntimeHome:
                        role: "Own the runtime package."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "AGENTS.prompt").write_text(
                "import runtime_home\n",
                encoding="utf-8",
            )
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.emit]

                    [[tool.doctrine.emit.targets]]
                    name = "demo"
                    entrypoint = "prompts/AGENTS.prompt"
                    output_dir = "build"
                    """
                ),
                encoding="utf-8",
            )

            target = load_emit_targets(pyproject)["demo"]
            emitted = emit_target_flow(target, include_svg=False)

            d2_path = root / "build" / "AGENTS.flow.d2"
            self.assertEqual(emitted, (d2_path,))
            self.assertIn("RuntimeHome", d2_path.read_text(encoding="utf-8"))

    def test_emit_target_flow_uses_provider_prompt_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            provider_prompts = root / "framework" / "prompts"
            (provider_prompts / "framework" / "stdlib").mkdir(parents=True)
            (provider_prompts / "framework" / "stdlib" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    export agent ProviderAgent:
                        role: "Own the provider runtime package."
                    """
                ),
                encoding="utf-8",
            )
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    import framework.stdlib

                    agent BuildHandle:
                        role: "Own the build handle."
                        workflow: "Route"
                            law:
                                active when true
                                current none
                                stop "Reply and stop."
                                route "Hand off to the provider package." -> framework.stdlib.ProviderAgent
                    """
                ),
                encoding="utf-8",
            )
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.emit]

                    [[tool.doctrine.emit.targets]]
                    name = "demo"
                    entrypoint = "prompts/AGENTS.prompt"
                    output_dir = "build"
                    """
                ),
                encoding="utf-8",
            )

            target = load_emit_targets(
                pyproject,
                provided_prompt_roots=(
                    ProvidedPromptRoot("framework_stdlib", provider_prompts),
                ),
            )["demo"]
            emitted = emit_target_flow(target, include_svg=False)

            d2_path = root / "build" / "AGENTS.flow.d2"
            d2_text = d2_path.read_text(encoding="utf-8")
            self.assertEqual(emitted, (d2_path,))
            self.assertNotIn("framework/prompts", pyproject.read_text(encoding="utf-8"))
            self.assertIn("ProviderAgent", d2_text)
            self.assertIn("Hand off to the provider\\npackage.", d2_text)

    def test_direct_emit_target_flow_uses_provider_prompt_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            provider_prompts = root / "framework" / "prompts"
            (provider_prompts / "framework" / "stdlib").mkdir(parents=True)
            (provider_prompts / "framework" / "stdlib" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    export agent ProviderAgent:
                        role: "Own the provider runtime package."
                    """
                ),
                encoding="utf-8",
            )
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                "import framework.stdlib\n",
                encoding="utf-8",
            )
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [project]
                    name = "doctrine-test"
                    version = "0.0.0"
                    """
                ),
                encoding="utf-8",
            )

            target = resolve_direct_emit_target(
                pyproject_path=pyproject,
                entrypoint="prompts/AGENTS.prompt",
                output_dir="build",
                allowed_entrypoints=DOCS_ENTRYPOINTS,
                provided_prompt_roots=(
                    ProvidedPromptRoot("framework_stdlib", provider_prompts),
                ),
            )
            emitted = emit_target_flow(target, include_svg=False)

            d2_path = root / "build" / "AGENTS.flow.d2"
            self.assertEqual(emitted, (d2_path,))
            self.assertIn("ProviderAgent", d2_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
