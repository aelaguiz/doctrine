from __future__ import annotations

import json
import shutil
import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession, ProvidedPromptRoot
from doctrine.diagnostics import CompileError
from doctrine.emit_common import collect_runtime_emit_roots, load_emit_targets
from doctrine.emit_docs import emit_target
from doctrine.parser import parse_file

REPO_ROOT = Path(__file__).resolve().parents[1]


class EmitDocsTests(unittest.TestCase):
    def _emit_example_markdown(
        self,
        *,
        example_dir_name: str,
        agent_slug_name: str,
        prompt_text_override: str | None = None,
    ) -> tuple[str, str | None, dict[str, object] | None]:
        example_dir = REPO_ROOT / "examples" / example_dir_name
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            (root / "prompts").mkdir(parents=True)
            if prompt_text_override is None:
                shutil.copytree(example_dir / "prompts", root / "prompts", dirs_exist_ok=True)
            else:
                (root / "prompts" / "AGENTS.prompt").write_text(
                    prompt_text_override,
                    encoding="utf-8",
                )
            if (example_dir / "schemas").is_dir():
                shutil.copytree(example_dir / "schemas", root / "schemas")

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
            emit_target(target)

            markdown_path = root / "build" / agent_slug_name / "AGENTS.md"
            old_contract_path = root / "build" / agent_slug_name / "AGENTS.contract.json"
            final_output_contract_path = (
                root / "build" / agent_slug_name / "final_output.contract.json"
            )
            schema_dir = root / "build" / agent_slug_name / "schemas"
            schema_paths = sorted(schema_dir.glob("*.json")) if schema_dir.is_dir() else []
            schema_text = (
                schema_paths[0].read_text(encoding="utf-8")
                if len(schema_paths) == 1
                else None
            )
            self.assertFalse(old_contract_path.exists())
            return (
                markdown_path.read_text(encoding="utf-8"),
                schema_text,
                (
                    json.loads(final_output_contract_path.read_text(encoding="utf-8"))
                    if final_output_contract_path.is_file()
                    else None
                ),
            )

    def _emit_prompt_markdown(
        self,
        *,
        prompt_text: str,
        agent_slug_name: str,
    ) -> tuple[str, str | None, dict[str, object] | None]:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(prompt_text),
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
            emit_target(target)

            markdown_path = root / "build" / agent_slug_name / "AGENTS.md"
            final_output_contract_path = (
                root / "build" / agent_slug_name / "final_output.contract.json"
            )
            return (
                markdown_path.read_text(encoding="utf-8"),
                None,
                (
                    json.loads(final_output_contract_path.read_text(encoding="utf-8"))
                    if final_output_contract_path.is_file()
                    else None
                ),
            )

    def test_emit_target_writes_markdown_and_schema_for_structured_final_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    output schema RepoStatusSchema: "Repo Status Schema"
                        field summary: "Summary"
                            type: string

                        example:
                            summary: "Branch is clean."

                    output shape RepoStatusJson: "Repo Status JSON"
                        kind: JsonObject
                        schema: RepoStatusSchema

                    output RepoStatusFinalResponse: "Repo Status Final Response"
                        target: TurnResponse
                        shape: RepoStatusJson
                        requirement: Required

                    agent RepoStatusAgent:
                        role: "Report repo status."
                        workflow: "Summarize"
                            "Summarize the repo state."
                        outputs: "Outputs"
                            RepoStatusFinalResponse
                        final_output: RepoStatusFinalResponse
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

            target = load_emit_targets(pyproject)["demo"]
            emitted = emit_target(target)

            markdown_path = root / "build" / "repo_status_agent" / "AGENTS.md"
            old_contract_path = root / "build" / "repo_status_agent" / "AGENTS.contract.json"
            final_output_contract_path = (
                root / "build" / "repo_status_agent" / "final_output.contract.json"
            )
            schema_path = (
                root
                / "build"
                / "repo_status_agent"
                / "schemas"
                / "repo_status_final_response.schema.json"
            )
            self.assertEqual(emitted, (markdown_path, schema_path, final_output_contract_path))
            self.assertTrue(markdown_path.is_file())
            self.assertTrue(schema_path.is_file())
            self.assertFalse(old_contract_path.exists())
            self.assertTrue(final_output_contract_path.is_file())

            rendered = markdown_path.read_text(encoding="utf-8")
            self.assertIn("| Format | Structured JSON |", rendered)
            self.assertIn("| Schema | Repo Status Schema |", rendered)
            self.assertIn(
                "| Generated Schema | `schemas/repo_status_final_response.schema.json` |",
                rendered,
            )
            self.assertIn("#### Example", rendered)
            self.assertIn('"summary": "Branch is clean."', rendered)

            schema_data = json.loads(schema_path.read_text(encoding="utf-8"))
            self.assertEqual(schema_data["type"], "object")
            self.assertEqual(schema_data["required"], ["summary"])
            contract_data = json.loads(final_output_contract_path.read_text(encoding="utf-8"))
            self.assertEqual(contract_data["contract_version"], 1)
            self.assertEqual(contract_data["agent"]["name"], "RepoStatusAgent")
            self.assertEqual(contract_data["agent"]["slug"], "repo_status_agent")
            self.assertEqual(contract_data["agent"]["entrypoint"], "prompts/AGENTS.prompt")
            self.assertEqual(
                contract_data["route"],
                {
                    "exists": False,
                    "behavior": "never",
                    "has_unrouted_branch": False,
                    "unrouted_review_verdicts": [],
                    "branches": [],
                },
            )
            self.assertEqual(
                contract_data["final_output"],
                {
                    "exists": True,
                    "declaration_key": "RepoStatusFinalResponse",
                    "declaration_name": "RepoStatusFinalResponse",
                    "format_mode": "json_object",
                    "schema_profile": "OpenAIStructuredOutput",
                    "emitted_schema_relpath": "schemas/repo_status_final_response.schema.json",
                },
            )
            self.assertNotIn("review", contract_data)

    def test_emit_target_writes_route_contract_for_routed_final_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent ReviewLead:
                        role: "Own routed follow-up."
                        workflow: "Follow Up"
                            "Take the routed follow-up."

                    output RouteReply: "Route Reply"
                        target: TurnResponse
                        shape: Comment
                        requirement: Required

                    agent Router:
                        role: "Route and answer."
                        workflow: "Route"
                            law:
                                active when true
                                current none
                                route "Go to review." -> ReviewLead
                        outputs: "Outputs"
                            RouteReply
                        final_output: RouteReply
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

            target = load_emit_targets(pyproject)["demo"]
            emit_target(target)

            contract_path = root / "build" / "router" / "final_output.contract.json"
            contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
            self.assertEqual(
                contract_data["route"],
                {
                    "exists": True,
                    "behavior": "always",
                    "has_unrouted_branch": False,
                    "unrouted_review_verdicts": [],
                    "branches": [
                        {
                            "target": {
                                "key": "ReviewLead",
                                "module_parts": [],
                                "name": "ReviewLead",
                                "title": "Review Lead",
                            },
                            "label": "Go to review.",
                            "summary": "Go to review. Next owner: Review Lead.",
                            "choice_members": [],
                        },
                    ],
                },
            )

    def test_emit_target_keeps_io_contract_stable_for_io_wrapper_shorthand(self) -> None:
        long_form_prompt = """
            input BaseReviewPacket: "Base Review Packet"
                source: File
                    path: "catalog/base_review_packet.json"
                shape: "JSON Document"
                requirement: Required

            input FreshReviewPacket: "Fresh Review Packet"
                source: File
                    path: "catalog/fresh_review_packet.json"
                shape: "JSON Document"
                requirement: Required

            output BaseReviewHandoff: "Base Review Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

            output FreshReviewHandoff: "Fresh Review Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

            output FinalReply: "Final Reply"
                target: TurnResponse
                shape: Comment
                requirement: Required

            inputs BaseInputs: "Your Inputs"
                review_packet: "Review Packet"
                    BaseReviewPacket

            outputs BaseOutputs: "Your Outputs"
                review_handoff: "Review Handoff"
                    BaseReviewHandoff

                final_reply: "Final Reply"
                    FinalReply

            inputs ChildInputs[BaseInputs]: "Your Inputs"
                override review_packet:
                    FreshReviewPacket

            outputs ChildOutputs[BaseOutputs]: "Your Outputs"
                inherit {final_reply}

                override review_handoff:
                    FreshReviewHandoff

            agent Demo:
                role: "Keep IO contracts stable."
                inputs: ChildInputs
                outputs: ChildOutputs
                final_output: FinalReply
        """
        shorthand_prompt = """
            input BaseReviewPacket: "Base Review Packet"
                source: File
                    path: "catalog/base_review_packet.json"
                shape: "JSON Document"
                requirement: Required

            input FreshReviewPacket: "Fresh Review Packet"
                source: File
                    path: "catalog/fresh_review_packet.json"
                shape: "JSON Document"
                requirement: Required

            output BaseReviewHandoff: "Base Review Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

            output FreshReviewHandoff: "Fresh Review Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

            output FinalReply: "Final Reply"
                target: TurnResponse
                shape: Comment
                requirement: Required

            inputs BaseInputs: "Your Inputs"
                review_packet: BaseReviewPacket

            outputs BaseOutputs: "Your Outputs"
                review_handoff: BaseReviewHandoff

                final_reply: FinalReply

            inputs ChildInputs[BaseInputs]: "Your Inputs"
                override review_packet: FreshReviewPacket

            outputs ChildOutputs[BaseOutputs]: "Your Outputs"
                inherit {final_reply}

                override review_handoff: FreshReviewHandoff

            agent Demo:
                role: "Keep IO contracts stable."
                inputs: ChildInputs
                outputs: ChildOutputs
                final_output: FinalReply
        """

        _, _, long_contract = self._emit_prompt_markdown(
            prompt_text=long_form_prompt,
            agent_slug_name="demo",
        )
        _, _, shorthand_contract = self._emit_prompt_markdown(
            prompt_text=shorthand_prompt,
            agent_slug_name="demo",
        )

        assert long_contract is not None
        assert shorthand_contract is not None
        self.assertEqual(shorthand_contract["io"], long_contract["io"])

    def test_emit_target_serializes_io_block_for_exact_previous_final_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "rally").mkdir(parents=True)
            (prompts / "rally" / "base_agent.prompt").write_text(
                textwrap.dedent(
                    """\
                    input source RallyPreviousTurnOutput: "Rally Previous Turn Output"
                        optional: "Optional Source Keys"
                            output: "Output"
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    output schema SharedTurnSchema: "Shared Turn Schema"
                        field kind: "Kind"
                            type: string

                        example:
                            kind: "handoff"

                    output shape SharedTurnJson: "Shared Turn JSON"
                        kind: JsonObject
                        schema: SharedTurnSchema

                    output SharedTurnResult: "Shared Turn Result"
                        target: TurnResponse
                        shape: SharedTurnJson
                        requirement: Required

                    input PreviousTurnResult: "Previous Turn Result"
                        source: RallyPreviousTurnOutput
                        requirement: Advisory

                    agent WorkerB:
                        role: "Read the previous turn."
                        workflow: "Act"
                            law:
                                current none
                                active when PreviousTurnResult.kind == "handoff"
                        inputs: "Inputs"
                            PreviousTurnResult
                        outputs: "Outputs"
                            SharedTurnResult
                        final_output: SharedTurnResult

                    agent WorkerA:
                        role: "Hand work to Worker B."
                        workflow: "Route"
                            law:
                                current none
                                active when true
                                route "Send to Worker B." -> WorkerB
                        outputs: "Outputs"
                            SharedTurnResult
                        final_output: SharedTurnResult
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

            target = load_emit_targets(pyproject)["demo"]
            emit_target(target)

            contract_path = root / "build" / "worker_b" / "final_output.contract.json"
            contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
            self.assertIn("io", contract_data)
            self.assertEqual(
                contract_data["io"]["previous_turn_inputs"],
                [
                    {
                        "input_key": "PreviousTurnResult",
                        "input_name": "PreviousTurnResult",
                        "selector_kind": "default_final_output",
                        "selector_text": "Exact previous final output",
                        "resolved_declaration_key": "SharedTurnResult",
                        "resolved_declaration_name": "SharedTurnResult",
                        "derived_contract_mode": "structured_json",
                        "requirement": "Advisory",
                        "target": {
                            "key": "TurnResponse",
                            "title": "Turn Response",
                            "config": {},
                        },
                        "shape": {
                            "name": "SharedTurnJson",
                            "title": "Shared Turn JSON",
                        },
                        "schema": {
                            "name": "SharedTurnSchema",
                            "title": "Shared Turn Schema",
                            "profile": "OpenAIStructuredOutput",
                        },
                    }
                ],
            )
            output_keys = {
                item["declaration_key"] for item in contract_data["io"]["outputs"]
            }
            for binding in contract_data["io"]["output_bindings"]:
                self.assertIn(binding["declaration_key"], output_keys)

    def test_emit_target_serializes_previous_turn_io_for_route_field_final_output_with_root_readables(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "rally").mkdir(parents=True)
            (prompts / "rally" / "base_agent.prompt").write_text(
                textwrap.dedent(
                    """\
                    input source RallyPreviousTurnOutput: "Rally Previous Turn Output"
                        optional: "Optional Source Keys"
                            output: "Output"
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    workflow RouteGuide: "Route Guide"
                        sequence choose_route:
                            "Pick the next owner."
                            "Return the routed final output."

                    workflow PreviousTurnGuide: "Previous Turn Guide"
                        callout readback: "Readback"
                            kind: note
                            "Read the previous turn before you continue."

                    output schema TurnResultSchema: "Turn Result Schema"
                        route field next_route: "Next Route"
                            send_to_worker_b: "Send to Worker B." -> WorkerB

                        field kind: "Kind"
                            type: string

                        example:
                            kind: "handoff"
                            next_route: "send_to_worker_b"

                    output shape TurnResultJson: "Turn Result JSON"
                        kind: JsonObject
                        schema: TurnResultSchema

                    output TurnResult: "Turn Result"
                        target: TurnResponse
                        shape: TurnResultJson
                        requirement: Required

                    input PreviousTurnResult: "Previous Turn Result"
                        source: RallyPreviousTurnOutput
                        requirement: Advisory

                    agent WorkerB:
                        role: "Read the previous turn."
                        workflow: PreviousTurnGuide
                        inputs: "Inputs"
                            PreviousTurnResult
                        outputs: "Outputs"
                            TurnResult
                        final_output: TurnResult

                    agent WorkerA:
                        role: "Hand work to Worker B."
                        workflow: RouteGuide
                        outputs: "Outputs"
                            TurnResult
                        final_output:
                            output: TurnResult
                            route: next_route
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

            target = load_emit_targets(pyproject)["demo"]
            emit_target(target)

            contract_path = root / "build" / "worker_b" / "final_output.contract.json"
            contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
            self.assertEqual(
                contract_data["io"]["previous_turn_inputs"],
                [
                    {
                        "input_key": "PreviousTurnResult",
                        "input_name": "PreviousTurnResult",
                        "selector_kind": "default_final_output",
                        "selector_text": "Exact previous final output",
                        "resolved_declaration_key": "TurnResult",
                        "resolved_declaration_name": "TurnResult",
                        "derived_contract_mode": "structured_json",
                        "requirement": "Advisory",
                        "target": {
                            "key": "TurnResponse",
                            "title": "Turn Response",
                            "config": {},
                        },
                        "shape": {
                            "name": "TurnResultJson",
                            "title": "Turn Result JSON",
                        },
                        "schema": {
                            "name": "TurnResultSchema",
                            "title": "Turn Result Schema",
                            "profile": "OpenAIStructuredOutput",
                        },
                    }
                ],
            )

    def test_emit_target_serializes_io_block_for_imported_previous_output_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "rally").mkdir(parents=True)
            (prompts / "shared").mkdir(parents=True)
            (prompts / "rally" / "base_agent.prompt").write_text(
                textwrap.dedent(
                    """\
                    input source RallyPreviousTurnOutput: "Rally Previous Turn Output"
                        optional: "Optional Source Keys"
                            output: "Output"
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "shared" / "outputs.prompt").write_text(
                textwrap.dedent(
                    """\
                    output schema SharedTurnSchema: "Shared Turn Schema"
                        field kind: "Kind"
                            type: string

                        example:
                            kind: "handoff"

                    output shape SharedTurnJson: "Shared Turn JSON"
                        kind: JsonObject
                        schema: SharedTurnSchema

                    output SharedTurnResult: "Shared Turn Result"
                        target: TurnResponse
                        shape: SharedTurnJson
                        requirement: Required

                    outputs ProjectLeadOutputs: "Project Lead Outputs"
                        coordination_handoff: "Coordination Handoff"
                            SharedTurnResult
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    input PreviousRoutingHandoff: "Previous Routing Handoff"
                        source: RallyPreviousTurnOutput
                            output: ProjectLeadOutputs:coordination_handoff
                        requirement: Advisory

                    agent WorkerB:
                        role: "Read the previous turn."
                        workflow: "Act"
                            law:
                                current none
                                active when PreviousRoutingHandoff.kind == "handoff"
                        inputs: "Inputs"
                            PreviousRoutingHandoff
                        outputs: ProjectLeadOutputs
                        final_output: SharedTurnResult

                    agent WorkerA:
                        role: "Hand work to Worker B."
                        workflow: "Route"
                            law:
                                current none
                                active when true
                                route "Send to Worker B." -> WorkerB
                        outputs: ProjectLeadOutputs
                        final_output: SharedTurnResult
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

            target = load_emit_targets(pyproject)["demo"]
            emit_target(target)

            contract_path = root / "build" / "worker_b" / "final_output.contract.json"
            contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
            previous_input = contract_data["io"]["previous_turn_inputs"][0]
            self.assertEqual(previous_input["input_key"], "PreviousRoutingHandoff")
            self.assertEqual(previous_input["input_name"], "PreviousRoutingHandoff")
            self.assertEqual(previous_input["selector_kind"], "output_binding")
            self.assertEqual(
                previous_input["selector_text"],
                "ProjectLeadOutputs:coordination_handoff",
            )
            self.assertEqual(
                previous_input["resolved_declaration_key"],
                "shared.outputs.SharedTurnResult",
            )
            self.assertEqual(
                previous_input["resolved_declaration_name"],
                "SharedTurnResult",
            )
            self.assertEqual(previous_input["derived_contract_mode"], "structured_json")
            self.assertEqual(previous_input["requirement"], "Advisory")
            self.assertEqual(
                previous_input["target"],
                {
                    "key": "TurnResponse",
                    "title": "Turn Response",
                    "config": {},
                },
            )
            self.assertEqual(
                previous_input["shape"],
                {
                    "name": "SharedTurnJson",
                    "title": "Shared Turn JSON",
                },
            )
            self.assertEqual(
                previous_input["schema"],
                {
                    "name": "SharedTurnSchema",
                    "title": "Shared Turn Schema",
                    "profile": "OpenAIStructuredOutput",
                },
            )
            self.assertEqual(previous_input["binding_path"], ["coordination_handoff"])
            output_keys = {
                item["declaration_key"] for item in contract_data["io"]["outputs"]
            }
            self.assertIn(previous_input["resolved_declaration_key"], output_keys)
            self.assertIn(
                {
                    "binding_path": ["coordination_handoff"],
                    "declaration_key": "shared.outputs.SharedTurnResult",
                },
                contract_data["io"]["output_bindings"],
            )

    def test_emit_target_serializes_previous_turn_io_for_review_reject_route_selector(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "rally").mkdir(parents=True)
            (prompts / "shared").mkdir(parents=True)
            (prompts / "rally" / "base_agent.prompt").write_text(
                textwrap.dedent(
                    """\
                    input source RallyPreviousTurnOutput: "Rally Previous Turn Output"
                        optional: "Optional Source Keys"
                            output: "Output"
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "shared" / "review.prompt").write_text(
                textwrap.dedent(
                    """\
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
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    input DraftPoem: "Draft Poem"
                        source: File
                            path: "unit_root/DRAFT_POEM.md"
                        shape: MarkdownDocument
                        requirement: Required
                        needs_revision: "Needs Revision"

                    input PreviousPoemReview: "Previous Poem Review"
                        source: RallyPreviousTurnOutput
                            output: PoemReviewFinalResponse
                        requirement: Advisory

                    workflow PoemReviewContract: "Poem Review Contract"
                        inspect_meter: "Inspect Meter"
                            "Check whether the poem keeps its rhythm."

                    output MuseReply: "Muse Reply"
                        target: TurnResponse
                        shape: Comment
                        requirement: Required

                    agent Publisher:
                        role: "Take accepted poems to publishing."
                        workflow: "Publish"
                            "Prepare the accepted poem."

                    agent Muse:
                        role: "Revise rejected poems."
                        workflow: "Revise"
                            "Read the previous review before you revise."
                        inputs: "Inputs"
                            PreviousPoemReview
                        outputs: "Outputs"
                            MuseReply
                        final_output: MuseReply

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
                            reject contract.inspect_meter when DraftPoem.needs_revision
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

            target = load_emit_targets(pyproject)["demo"]
            emit_target(target)

            contract_path = root / "build" / "muse" / "final_output.contract.json"
            contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
            previous_input = contract_data["io"]["previous_turn_inputs"][0]

            self.assertEqual(previous_input["input_key"], "PreviousPoemReview")
            self.assertEqual(previous_input["input_name"], "PreviousPoemReview")
            self.assertEqual(previous_input["selector_kind"], "output_decl")
            self.assertEqual(
                previous_input["selector_text"],
                "PoemReviewFinalResponse",
            )
            self.assertEqual(
                previous_input["resolved_declaration_key"],
                "shared.review.PoemReviewFinalResponse",
            )
            self.assertEqual(
                previous_input["resolved_declaration_name"],
                "PoemReviewFinalResponse",
            )

    def test_emit_target_rejects_non_final_turn_response_previous_selector(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "rally").mkdir(parents=True)
            (prompts / "rally" / "base_agent.prompt").write_text(
                textwrap.dedent(
                    """\
                    input source RallyPreviousTurnOutput: "Rally Previous Turn Output"
                        optional: "Optional Source Keys"
                            output: "Output"
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    output schema SharedTurnSchema: "Shared Turn Schema"
                        field kind: "Kind"
                            type: string

                        example:
                            kind: "handoff"

                    output shape SharedTurnJson: "Shared Turn JSON"
                        kind: JsonObject
                        schema: SharedTurnSchema

                    output SharedTurnResult: "Shared Turn Result"
                        target: TurnResponse
                        shape: SharedTurnJson
                        requirement: Required

                    output CoordinationHandoff: "Coordination Handoff"
                        target: TurnResponse
                        shape: Comment
                        requirement: Required

                    input PreviousReadableReply: "Previous Readable Reply"
                        source: RallyPreviousTurnOutput
                            output: CoordinationHandoff
                        requirement: Advisory

                    agent WorkerB:
                        role: "Read the previous turn."
                        workflow: "Act"
                            "Read the previous turn."
                        inputs: "Inputs"
                            PreviousReadableReply
                        outputs: "Outputs"
                            SharedTurnResult
                        final_output: SharedTurnResult

                    agent WorkerA:
                        role: "Hand work to Worker B."
                        workflow: "Route"
                            law:
                                current none
                                active when true
                                route "Send to Worker B." -> WorkerB
                        outputs: "Outputs"
                            CoordinationHandoff
                            SharedTurnResult
                        final_output: SharedTurnResult
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

            target = load_emit_targets(pyproject)["demo"]
            with self.assertRaises(CompileError) as caught:
                emit_target(target)

            self.assertIn("non-final `TurnResponse`", str(caught.exception))

    def test_emit_target_writes_selector_metadata_for_route_field_final_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    output schema WriterDecisionSchema: "Writer Decision Schema"
                        route field next_route: "Next Route"
                            seek_muse: "Send to Muse." -> Muse
                            ready_for_critic: "Send to Critic." -> Critic
                            nullable

                        field summary: "Summary"
                            type: string

                        example:
                            next_route: "seek_muse"
                            summary: "Need fresher images."

                    output shape WriterDecisionJson: "Writer Decision JSON"
                        kind: JsonObject
                        schema: WriterDecisionSchema

                    output WriterDecision: "Writer Decision"
                        target: TurnResponse
                        shape: WriterDecisionJson
                        requirement: Required

                    agent Muse:
                        role: "Help the writer."
                        workflow: "Muse"
                            "Offer fresh direction."

                    agent Critic:
                        role: "Judge the draft."
                        workflow: "Critic"
                            "Judge the draft."

                    agent Writer:
                        role: "Write the next turn."
                        workflow: "Write"
                            "Write the next turn."
                        outputs: "Outputs"
                            WriterDecision
                        final_output:
                            output: WriterDecision
                            route: next_route
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

            target = load_emit_targets(pyproject)["demo"]
            emit_target(target)

            contract_path = root / "build" / "writer" / "final_output.contract.json"
            contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
            self.assertEqual(
                contract_data["route"],
                {
                    "exists": True,
                    "behavior": "conditional",
                    "has_unrouted_branch": True,
                    "unrouted_review_verdicts": [],
                    "selector": {
                        "surface": "final_output",
                        "field_path": ["next_route"],
                        "null_behavior": "no_route",
                    },
                    "branches": [
                        {
                            "target": {
                                "key": "Muse",
                                "module_parts": [],
                                "name": "Muse",
                                "title": "Muse",
                            },
                            "label": "Send to Muse.",
                            "summary": "Send to Muse. Next owner: Muse.",
                            "choice_members": [
                                {
                                    "member_key": "seek_muse",
                                    "member_title": "Send to Muse.",
                                    "member_wire": "seek_muse",
                                }
                            ],
                        },
                        {
                            "target": {
                                "key": "Critic",
                                "module_parts": [],
                                "name": "Critic",
                                "title": "Critic",
                            },
                            "label": "Send to Critic.",
                            "summary": "Send to Critic. Next owner: Critic.",
                            "choice_members": [
                                {
                                    "member_key": "ready_for_critic",
                                    "member_title": "Send to Critic.",
                                    "member_wire": "ready_for_critic",
                                }
                            ],
                        },
                    ],
                },
            )

    def test_emit_target_omits_example_section_when_schema_has_no_example(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    output schema RepoStatusSchema: "Repo Status Schema"
                        field summary: "Summary"
                            type: string

                    output shape RepoStatusJson: "Repo Status JSON"
                        kind: JsonObject
                        schema: RepoStatusSchema

                    output RepoStatusFinalResponse: "Repo Status Final Response"
                        target: TurnResponse
                        shape: RepoStatusJson
                        requirement: Required

                    agent RepoStatusAgent:
                        role: "Report repo status."
                        workflow: "Summarize"
                            "Summarize the repo state."
                        outputs: "Outputs"
                            RepoStatusFinalResponse
                        final_output: RepoStatusFinalResponse
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

            target = load_emit_targets(pyproject)["demo"]
            emit_target(target)

            markdown_path = root / "build" / "repo_status_agent" / "AGENTS.md"
            schema_path = (
                root
                / "build"
                / "repo_status_agent"
                / "schemas"
                / "repo_status_final_response.schema.json"
            )
            self.assertTrue(markdown_path.is_file())
            self.assertTrue(schema_path.is_file())

            rendered = markdown_path.read_text(encoding="utf-8")
            # Installed and repo-local emit paths must agree that no authored
            # example means no rendered Example section.
            self.assertIn("#### Payload Fields", rendered)
            self.assertNotIn("#### Example", rendered)

    def test_emit_target_marks_agents_without_final_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    output SummaryReply: "Summary Reply"
                        target: TurnResponse
                        shape: CommentText
                        requirement: Required

                    agent HelloAgent:
                        role: "Answer plainly."
                        workflow: "Reply"
                            "Reply and stop."
                        outputs: "Outputs"
                            SummaryReply
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

            target = load_emit_targets(pyproject)["demo"]
            emitted = emit_target(target)

            markdown_path = root / "build" / "hello_agent" / "AGENTS.md"
            old_contract_path = root / "build" / "hello_agent" / "AGENTS.contract.json"
            final_output_contract_path = root / "build" / "hello_agent" / "final_output.contract.json"
            schema_dir = root / "build" / "hello_agent" / "schemas"
            self.assertEqual(emitted, (markdown_path,))
            self.assertTrue(markdown_path.is_file())
            self.assertFalse(old_contract_path.exists())
            self.assertFalse(final_output_contract_path.exists())
            self.assertFalse(schema_dir.exists())

    def test_emit_target_renders_titleless_readable_lists_without_helper_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent HelloAgent:
                        role: "Follow the guide."
                        workflow: "Guide"
                            read_first: "Read First"
                                sequence steps:
                                    "Read `home:issue.md` first."
                                    "Then read this role's local rules."

                            shared_rules: "Shared Rules"
                                bullets rules:
                                    "Use `home:issue.md` as the shared ledger."
                                    "End with the final JSON."
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

            target = load_emit_targets(pyproject)["demo"]
            emit_target(target)

            markdown_path = root / "build" / "hello_agent" / "AGENTS.md"
            rendered = markdown_path.read_text(encoding="utf-8")
            self.assertIn(
                "### Read First\n\n"
                "1. Read `home:issue.md` first.\n"
                "2. Then read this role's local rules.",
                rendered,
            )
            self.assertIn(
                "### Shared Rules\n\n"
                "- Use `home:issue.md` as the shared ledger.\n"
                "- End with the final JSON.",
                rendered,
            )
            self.assertNotIn("#### Steps", rendered)
            self.assertNotIn("#### Rules", rendered)
            self.assertNotIn("ordered list", rendered)
            self.assertNotIn("unordered list", rendered)

    def test_emit_target_emits_review_carrier_markdown_without_sidecar(self) -> None:
        rendered, schema_text, contract_data = self._emit_example_markdown(
            example_dir_name="104_review_final_output_output_schema_blocked_control_ready",
            agent_slug_name="acceptance_review_blocked_json_demo",
        )
        self.assertIsNotNone(schema_text)
        self.assertIsNotNone(contract_data)
        self.assertIn("| Schema | Acceptance Review Schema |", rendered)
        self.assertIn('"blocked_gate": "The review basis is missing."', rendered)
        assert contract_data is not None
        self.assertEqual(contract_data["final_output"]["format_mode"], "json_object")
        self.assertEqual(
            contract_data["final_output"]["emitted_schema_relpath"],
            "schemas/acceptance_review_response.schema.json",
        )
        self.assertEqual(contract_data["review"]["final_response"]["mode"], "carrier")
        self.assertTrue(contract_data["review"]["final_response"]["control_ready"])
        self.assertEqual(
            contract_data["review"]["carrier_fields"]["blocked_gate"],
            "failure_detail.blocked_gate",
        )
        self.assertEqual(contract_data["route"]["behavior"], "conditional")
        self.assertEqual(contract_data["route"]["unrouted_review_verdicts"], ["changes requested"])
        self.assertEqual(contract_data["route"]["branches"][0]["target"]["key"], "ReviewLead")
        self.assertEqual(contract_data["route"]["branches"][0]["review_verdict"], "accepted")

    def test_emit_target_emits_split_control_ready_review_markdown_without_sidecar(self) -> None:
        rendered, schema_text, contract_data = self._emit_example_markdown(
            example_dir_name="105_review_split_final_output_output_schema_control_ready",
            agent_slug_name="acceptance_review_split_control_ready_demo",
        )
        self.assertIsNotNone(schema_text)
        self.assertIsNotNone(contract_data)
        self.assertIn(
            "This final response is separate from the review carrier: AcceptanceReviewComment.",
            rendered,
        )
        self.assertIn(
            "This final response is control-ready. A host may read it as the review outcome.",
            rendered,
        )
        assert contract_data is not None
        self.assertEqual(contract_data["review"]["final_response"]["mode"], "split")
        self.assertTrue(contract_data["review"]["final_response"]["control_ready"])
        self.assertEqual(
            contract_data["review"]["final_response"]["review_fields"]["blocked_gate"],
            "blocked_gate",
        )
        self.assertEqual(
            contract_data["final_output"]["emitted_schema_relpath"],
            "schemas/acceptance_control_final_response.schema.json",
        )
        self.assertEqual(contract_data["route"]["behavior"], "conditional")
        self.assertEqual(contract_data["route"]["branches"][0]["target"]["key"], "ReviewLead")
        self.assertEqual(contract_data["route"]["branches"][0]["review_verdict"], "accepted")

    def test_emit_target_emits_split_partial_review_markdown_without_sidecar(self) -> None:
        prompt_text = (
            REPO_ROOT
            / "examples"
            / "106_review_split_final_output_output_schema_partial"
            / "prompts"
            / "AGENTS.prompt"
        ).read_text(encoding="utf-8")
        rendered, schema_text, contract_data = self._emit_example_markdown(
            example_dir_name="106_review_split_final_output_output_schema_partial",
            agent_slug_name="acceptance_review_split_partial_demo",
            prompt_text_override=prompt_text.split("\n\noutput SummaryReply:", 1)[0],
        )
        self.assertIsNotNone(schema_text)
        self.assertIsNotNone(contract_data)
        self.assertIn(
            "This final response is separate from the review carrier: AcceptanceReviewComment.",
            rendered,
        )
        self.assertIn(
            "Read the review carrier for the full review outcome.",
            rendered,
        )
        self.assertIn(
            "#### Current Artifact",
            rendered,
        )
        assert contract_data is not None
        self.assertEqual(contract_data["review"]["final_response"]["mode"], "split")
        self.assertFalse(contract_data["review"]["final_response"]["control_ready"])
        self.assertEqual(
            contract_data["review"]["final_response"]["review_fields"]["current_artifact"],
            "current_artifact",
        )
        self.assertEqual(contract_data["route"]["behavior"], "conditional")
        self.assertEqual(contract_data["route"]["has_unrouted_branch"], True)
        self.assertEqual(contract_data["route"]["branches"][0]["target"]["key"], "ReviewLead")

    def test_emit_target_renders_workflow_root_readable_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    workflow ReleaseGuide: "Release Guide"
                        sequence read_first:
                            "Read `home:issue.md` first."
                            "Then read the role rules."

                        definitions done_when: "Done When"
                            summary: "Summary"
                                "State the release result."

                    agent HelloAgent:
                        role: "Use {{ReleaseGuide:done_when.summary.title}}."
                        workflow: ReleaseGuide
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

            target = load_emit_targets(pyproject)["demo"]
            emit_target(target)

            markdown_path = root / "build" / "hello_agent" / "AGENTS.md"
            rendered = markdown_path.read_text(encoding="utf-8")
            self.assertIn("Use Summary.", rendered)
            self.assertIn(
                "## Release Guide\n\n"
                "1. Read `home:issue.md` first.\n"
                "2. Then read the role rules.",
                rendered,
            )
            self.assertNotIn("### Read First", rendered)
            self.assertIn("### Done When", rendered)
            self.assertIn("- **Summary** \u2014 State the release result.", rendered)

    def test_emit_target_rejects_legacy_example_file_on_output_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir).resolve()
            root = base / "project"
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    output schema RepoStatusSchema: "Repo Status Schema"
                        field summary: "Summary"
                            type: string

                        example:
                            summary: "Branch is clean."

                    output shape RepoStatusJson: "Repo Status JSON"
                        kind: JsonObject
                        schema: RepoStatusSchema
                        example_file: "examples/repo_status.example.json"

                    output RepoStatusFinalResponse: "Repo Status Final Response"
                        target: TurnResponse
                        shape: RepoStatusJson
                        requirement: Required

                    agent RepoStatusAgent:
                        role: "Report repo status."
                        workflow: "Summarize"
                            "Summarize the repo state."
                        outputs: "Outputs"
                            RepoStatusFinalResponse
                        final_output: RepoStatusFinalResponse
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

            target = load_emit_targets(pyproject)["demo"]
            with self.assertRaises(CompileError) as exc_info:
                emit_target(target)

            self.assertEqual(exc_info.exception.code, "E215")
            self.assertIn("retire `example_file`", str(exc_info.exception))

    def test_collect_runtime_emit_roots_preserves_first_seen_runtime_package_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "agents" / "alpha").mkdir(parents=True)
            (prompts / "agents" / "beta").mkdir(parents=True)
            (prompts / "shared").mkdir(parents=True)
            (prompts / "agents" / "alpha" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent AlphaHome:
                        role: "Own alpha."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "agents" / "beta" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent BetaHome:
                        role: "Own beta."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "shared" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    import agents.alpha

                    workflow SharedFlow: "Shared Flow"
                        "Keep alpha reachable through a nested import."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    import shared
                    import agents.beta
                    import agents.alpha

                    agent BuildHandle:
                        role: "Own the build handle."
                    """
                ),
                encoding="utf-8",
            )

            session = CompilationSession(parse_file(prompts / "AGENTS.prompt"))
            roots = collect_runtime_emit_roots(session)

        self.assertEqual(
            tuple(root.agent_name for root in roots),
            ("BuildHandle", "AlphaHome", "BetaHome"),
        )

    def test_emit_target_emits_imported_runtime_package_tree_with_peer_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "runtime_home" / "assets").mkdir(parents=True)
            (prompts / "runtime_home" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent RuntimeHome:
                        role: "Own the runtime package."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "runtime_home" / "assets" / "tone.txt").write_text(
                "keep replies crisp\n",
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
            emitted = emit_target(target)

            markdown_path = root / "build" / "runtime_home" / "AGENTS.md"
            peer_path = root / "build" / "runtime_home" / "assets" / "tone.txt"
            self.assertEqual(emitted, (markdown_path, peer_path))
            self.assertEqual(peer_path.read_text(encoding="utf-8"), "keep replies crisp\n")
            rendered = markdown_path.read_text(encoding="utf-8")
            self.assertIn("Own the runtime package.", rendered)

    def test_emit_target_uses_provider_prompt_roots_without_host_config_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            provider_prompts = root / "framework" / "prompts"
            (provider_prompts / "framework" / "stdlib").mkdir(parents=True)
            (provider_prompts / "framework" / "stdlib" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    output ProviderReply: "Provider Reply"
                        target: TurnResponse
                        shape: CommentText
                        requirement: Required

                    agent ProviderAgent:
                        role: "Own the provider runtime package."
                        workflow: "Reply"
                            "Reply from the provider package."
                        outputs: "Outputs"
                            ProviderReply
                        final_output: ProviderReply
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
            emitted = emit_target(target)

            markdown_path = root / "build" / "framework" / "stdlib" / "AGENTS.md"
            contract_path = (
                root
                / "build"
                / "framework"
                / "stdlib"
                / "final_output.contract.json"
            )
            self.assertEqual(emitted, (markdown_path, contract_path))
            self.assertNotIn("framework/prompts", pyproject.read_text(encoding="utf-8"))
            rendered = markdown_path.read_text(encoding="utf-8")
            self.assertIn("Own the provider runtime package.", rendered)
            contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
            self.assertEqual(
                contract_data["agent"]["entrypoint"],
                "framework_stdlib:framework/stdlib/AGENTS.prompt",
            )
            self.assertNotIn(str(provider_prompts), json.dumps(contract_data))

    def test_emit_target_emits_matching_runtime_package_soul_prompt(self) -> None:
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
            (prompts / "runtime_home" / "SOUL.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent RuntimeHome:
                        role: "Carry the package background."
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
            emitted = emit_target(target)

            agents_path = root / "build" / "runtime_home" / "AGENTS.md"
            soul_path = root / "build" / "runtime_home" / "SOUL.md"
            self.assertEqual(emitted, (agents_path, soul_path))
            self.assertIn("Own the runtime package.", agents_path.read_text(encoding="utf-8"))
            self.assertIn("Carry the package background.", soul_path.read_text(encoding="utf-8"))

    def test_emit_target_rejects_runtime_package_soul_prompt_with_extra_concrete_agent(self) -> None:
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
            (prompts / "runtime_home" / "SOUL.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent RuntimeHome:
                        role: "Carry the package background."

                    agent ExtraSoul:
                        role: "This should fail."
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
            with self.assertRaises(CompileError) as exc_info:
                emit_target(target)

        self.assertIn("sibling `SOUL.prompt`", str(exc_info.exception))

    def test_emit_target_rejects_runtime_package_extra_prompt_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "runtime_home" / "helpers").mkdir(parents=True)
            (prompts / "runtime_home" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent RuntimeHome:
                        role: "Own the runtime package."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "runtime_home" / "helpers" / "shadow.prompt").write_text(
                textwrap.dedent(
                    """\
                    workflow ShadowGuide: "Shadow Guide"
                        "This should fail."
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
            with self.assertRaises(CompileError) as exc_info:
                emit_target(target)

        self.assertIn("extra prompt files", str(exc_info.exception))

    def test_emit_target_rejects_runtime_package_peer_soul_markdown_paths(self) -> None:
        # Runtime packages own generated SOUL.md output. A peer file with that
        # name must fail loud so bundled files cannot shadow compiler output.
        for peer_name in ("SOUL.md", "soul.md"):
            with self.subTest(peer_name=peer_name):
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
                    (prompts / "runtime_home" / peer_name).write_text(
                        "This path must stay compiler-owned.\n",
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
                    with self.assertRaises(CompileError) as exc_info:
                        emit_target(target)

                self.assertTrue(
                    "SOUL.md" in str(exc_info.exception)
                    or "case-collides" in str(exc_info.exception)
                )


class ValidValuesLineHelperTests(unittest.TestCase):
    """Unit cases for the canonical `render_valid_values_line` helper."""

    def _enum_type_ref(self):
        from doctrine import model
        from doctrine._compiler.resolve.field_types import EnumTypeRef

        members = (
            model.EnumMember(key="ok", title="OK"),
            model.EnumMember(key="blocked", title="Blocked"),
        )
        decl = model.EnumDecl(name="Status", title="Status", members=members)
        ref = model.NameRef(module_parts=(), declaration_name="Status")
        return EnumTypeRef(ref=ref, decl=decl)

    def _builtin_type_ref(self):
        from doctrine._compiler.resolve.field_types import BuiltinTypeRef

        return BuiltinTypeRef(name="string")

    def test_returns_none_for_none_type_ref(self) -> None:
        from doctrine.emit_common import render_valid_values_line

        self.assertIsNone(render_valid_values_line(None))

    def test_returns_none_for_builtin_type_ref(self) -> None:
        from doctrine.emit_common import render_valid_values_line

        self.assertIsNone(render_valid_values_line(self._builtin_type_ref()))

    def test_renders_valid_values_line_for_enum_type_ref(self) -> None:
        from doctrine.emit_common import render_valid_values_line

        rendered = render_valid_values_line(self._enum_type_ref())
        self.assertEqual(rendered, "Valid values: ok, blocked.")

    def test_renders_keys_even_when_enum_members_declare_wire(self) -> None:
        from doctrine import model
        from doctrine._compiler.resolve.field_types import EnumTypeRef
        from doctrine.emit_common import render_valid_values_line

        members = (
            model.EnumMember(key="section_author", title="Section Author", wire="section-author"),
            model.EnumMember(key="copy_editor", title="Copy Editor", wire="copy-editor"),
        )
        decl = model.EnumDecl(name="NextOwner", title="Next Owner", members=members)
        ref = model.NameRef(module_parts=(), declaration_name="NextOwner")
        rendered = render_valid_values_line(EnumTypeRef(ref=ref, decl=decl))
        self.assertEqual(
            rendered,
            "Valid values: section_author, copy_editor.",
        )


class TypedFieldBodyEmitTests(unittest.TestCase):
    """Emit-side unit cases across every field-shaped surface for type_ref.

    Covers readable table column, readable row_schema / item_schema entry,
    record scalar, and output-schema field surfaces with `None`,
    `BuiltinTypeRef`, and `EnumTypeRef` inputs to confirm the shared helper
    is the only place that renders the `Valid values:` line.
    """

    def _compile_agent_markdown(self, source: str, agent_name: str) -> str:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompts = root / "prompts"
            prompts.mkdir()
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(source),
                encoding="utf-8",
            )
            session = CompilationSession(parse_file(prompts / "AGENTS.prompt"))
            compiled = session.compile_agent(agent_name)
            from doctrine.renderer import render_markdown

            return render_markdown(compiled)

    # -- readable table column ------------------------------------------------

    def test_readable_table_column_renders_valid_values_for_enum_type(self) -> None:
        markdown = self._compile_agent_markdown(
            """\
            enum Status: "Status"
                ok: "OK"
                blocked: "Blocked"

            document StatusDoc: "Status Doc"
                table StatusTable: "Status Table"
                    columns:
                        status: "Status"
                            type: Status
                            "Current status."

            agent StatusTableColumnDemo:
                role: "Demo."
                outputs: "Outputs"
                    StatusDocFile
            output StatusDocFile: "Status Doc File"
                target: File
                    path: "status.md"
                shape: MarkdownDocument
                structure: StatusDoc
                requirement: Required
            """,
            agent_name="StatusTableColumnDemo",
        )
        self.assertIn("Valid values: ok, blocked.", markdown)

    def test_readable_table_column_omits_valid_values_for_builtin_type(self) -> None:
        markdown = self._compile_agent_markdown(
            """\
            document CountDoc: "Count Doc"
                table CountTable: "Count Table"
                    columns:
                        count: "Count"
                            type: integer
                            "Item count."

            output CountDocFile: "Count Doc File"
                target: File
                    path: "count.md"
                shape: MarkdownDocument
                structure: CountDoc
                requirement: Required

            agent CountTableColumnDemo:
                role: "Demo."
                outputs: "Outputs"
                    CountDocFile
            """,
            agent_name="CountTableColumnDemo",
        )
        self.assertNotIn("Valid values:", markdown)

    def test_readable_table_column_omits_valid_values_when_untyped(self) -> None:
        markdown = self._compile_agent_markdown(
            """\
            document NoteDoc: "Note Doc"
                table NoteTable: "Note Table"
                    columns:
                        note: "Note"
                            "A note."

            output NoteDocFile: "Note Doc File"
                target: File
                    path: "note.md"
                shape: MarkdownDocument
                structure: NoteDoc
                requirement: Required

            agent NoteTableColumnDemo:
                role: "Demo."
                outputs: "Outputs"
                    NoteDocFile
            """,
            agent_name="NoteTableColumnDemo",
        )
        self.assertNotIn("Valid values:", markdown)

    # -- readable row_schema / item_schema entry ------------------------------
    #
    # Row_schema and item_schema entries only surface via `_render_inline_schema`
    # under the `ContractMarkdown` profile. The existing manifest-backed corpus
    # does not exercise that surface, so these tests drive the renderer helper
    # directly with a typed `ReadableSchemaEntry`.

    def _build_schema_data(self, *, type_ref) -> object:
        from doctrine._model.readable import (
            ReadableInlineSchemaData,
            ReadableSchemaEntry,
        )

        return ReadableInlineSchemaData(
            entries=(
                ReadableSchemaEntry(
                    key="status",
                    title="Status",
                    body=("Row status.",),
                    type_ref=type_ref,
                ),
            ),
        )

    def test_readable_schema_entry_row_schema_renders_valid_values_for_enum(self) -> None:
        from doctrine import model
        from doctrine._compiler.resolve.field_types import EnumTypeRef
        from doctrine._compiler.resolved_types import ResolvedRenderProfile
        from doctrine._renderer.blocks import _render_inline_schema

        members = (
            model.EnumMember(key="ok", title="OK"),
            model.EnumMember(key="blocked", title="Blocked"),
        )
        decl = model.EnumDecl(name="Status", title="Status", members=members)
        ref = model.NameRef(module_parts=(), declaration_name="Status")
        schema = self._build_schema_data(type_ref=EnumTypeRef(ref=ref, decl=decl))

        lines = _render_inline_schema(
            "Row Schema",
            schema,
            profile=ResolvedRenderProfile(name="ContractMarkdown"),
        )
        rendered = "\n".join(lines)
        self.assertIn("Valid values: ok, blocked.", rendered)

    def test_readable_schema_entry_item_schema_omits_valid_values_for_builtin(self) -> None:
        from doctrine._compiler.resolve.field_types import BuiltinTypeRef
        from doctrine._compiler.resolved_types import ResolvedRenderProfile
        from doctrine._renderer.blocks import _render_inline_schema

        schema = self._build_schema_data(type_ref=BuiltinTypeRef(name="integer"))
        lines = _render_inline_schema(
            "Item Schema",
            schema,
            profile=ResolvedRenderProfile(name="ContractMarkdown"),
        )
        rendered = "\n".join(lines)
        self.assertNotIn("Valid values:", rendered)

    def test_readable_schema_entry_item_schema_omits_valid_values_when_untyped(self) -> None:
        from doctrine._compiler.resolved_types import ResolvedRenderProfile
        from doctrine._renderer.blocks import _render_inline_schema

        schema = self._build_schema_data(type_ref=None)
        lines = _render_inline_schema(
            "Item Schema",
            schema,
            profile=ResolvedRenderProfile(name="ContractMarkdown"),
        )
        rendered = "\n".join(lines)
        self.assertNotIn("Valid values:", rendered)

    # -- record scalar --------------------------------------------------------

    def test_record_scalar_renders_valid_values_for_enum_type(self) -> None:
        markdown = self._compile_agent_markdown(
            """\
            enum Status: "Status"
                ok: "OK"
                blocked: "Blocked"

            output StatusOutput: "Status Output"
                target: TurnResponse
                shape: Comment
                requirement: Required

                status: "Status"
                    type: Status

            agent StatusScalarDemo:
                role: "Demo."
                outputs: "Outputs"
                    StatusOutput
            """,
            agent_name="StatusScalarDemo",
        )
        self.assertIn("Valid values: ok, blocked.", markdown)

    def test_record_scalar_omits_valid_values_for_builtin_type(self) -> None:
        markdown = self._compile_agent_markdown(
            """\
            output CountOutput: "Count Output"
                target: TurnResponse
                shape: Comment
                requirement: Required

                count: "Count"
                    type: integer

            agent CountScalarDemo:
                role: "Demo."
                outputs: "Outputs"
                    CountOutput
            """,
            agent_name="CountScalarDemo",
        )
        self.assertNotIn("Valid values:", markdown)

    def test_record_scalar_omits_valid_values_when_untyped(self) -> None:
        markdown = self._compile_agent_markdown(
            """\
            output NoteOutput: "Note Output"
                target: TurnResponse
                shape: Comment
                requirement: Required

                note: "Note"
                    "A short note."

            agent NoteScalarDemo:
                role: "Demo."
                outputs: "Outputs"
                    NoteOutput
            """,
            agent_name="NoteScalarDemo",
        )
        self.assertNotIn("Valid values:", markdown)

    # -- output-schema field (via _json_schema_meaning) -----------------------

    def test_output_schema_field_renders_one_of_when_description_and_enum_present(
        self,
    ) -> None:
        markdown = self._compile_agent_markdown(
            """\
            enum Status: "Status"
                ok: "OK"
                blocked: "Blocked"

            output schema StatusSchema: "Status Schema"
                field status: "Status"
                    type: Status
                    note: "Current outcome."

                example:
                    status: "ok"

            output shape StatusJson: "Status JSON"
                kind: JsonObject
                schema: StatusSchema

            output StatusFinalResponse: "Status Final Response"
                target: TurnResponse
                shape: StatusJson
                requirement: Required

            agent OutputSchemaEnumDescDemo:
                role: "Demo."
                outputs: "Outputs"
                    StatusFinalResponse
                final_output: StatusFinalResponse
            """,
            agent_name="OutputSchemaEnumDescDemo",
        )
        self.assertIn(
            "| `status` | string | Yes | No | Current outcome. One of `ok`, `blocked`. |",
            markdown,
        )

    def test_output_schema_field_renders_description_only_for_builtin(self) -> None:
        markdown = self._compile_agent_markdown(
            """\
            output schema SummarySchema: "Summary Schema"
                field summary: "Summary"
                    type: string
                    note: "Short summary."

                example:
                    summary: "All good."

            output shape SummaryJson: "Summary JSON"
                kind: JsonObject
                schema: SummarySchema

            output SummaryFinalResponse: "Summary Final Response"
                target: TurnResponse
                shape: SummaryJson
                requirement: Required

            agent OutputSchemaBuiltinDemo:
                role: "Demo."
                outputs: "Outputs"
                    SummaryFinalResponse
                final_output: SummaryFinalResponse
            """,
            agent_name="OutputSchemaBuiltinDemo",
        )
        self.assertIn(
            "| `summary` | string | Yes | No | Short summary. |",
            markdown,
        )


class JsonSchemaMeaningDescriptionPlusEnumTests(unittest.TestCase):
    """Direct unit cases for `_json_schema_meaning`'s extended branches."""

    def _meaning(self, field_schema: dict, *, root_schema: dict | None = None) -> str:
        from doctrine._compiler.validate import ValidateMixin

        class _Stub(ValidateMixin):
            pass

        return _Stub()._json_schema_meaning(
            field_schema,
            root_schema=root_schema if root_schema is not None else field_schema,
        )

    def test_description_plus_enum_renders_both_lines(self) -> None:
        meaning = self._meaning(
            {
                "description": "Current outcome.",
                "enum": ["ok", "blocked"],
            }
        )
        self.assertEqual(meaning, "Current outcome. One of `ok`, `blocked`.")

    def test_description_only_still_renders_description(self) -> None:
        meaning = self._meaning({"description": "Short summary."})
        self.assertEqual(meaning, "Short summary.")

    def test_enum_only_still_renders_one_of(self) -> None:
        meaning = self._meaning({"enum": ["ok", "blocked"]})
        self.assertEqual(meaning, "One of `ok`, `blocked`.")

    def test_empty_schema_renders_empty_string(self) -> None:
        meaning = self._meaning({})
        self.assertEqual(meaning, "")


if __name__ == "__main__":
    unittest.main()
