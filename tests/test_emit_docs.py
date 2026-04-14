from __future__ import annotations

import json
import shutil
import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.diagnostics import EmitError
from doctrine.emit_common import load_emit_targets
from doctrine.emit_docs import emit_target

REPO_ROOT = Path(__file__).resolve().parents[1]


class EmitDocsTests(unittest.TestCase):
    def _emit_example_contract(
        self,
        *,
        example_dir_name: str,
        agent_slug_name: str,
        prompt_text_override: str | None = None,
    ) -> dict:
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
            if (example_dir / "examples").is_dir():
                shutil.copytree(example_dir / "examples", root / "examples")

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

            contract_path = root / "build" / agent_slug_name / "AGENTS.contract.json"
            return json.loads(contract_path.read_text())

    def test_emit_target_writes_markdown_and_companion_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (root / "schemas").mkdir(parents=True)
            (root / "examples").mkdir(parents=True)

            (root / "schemas" / "repo_status.schema.json").write_text(
                textwrap.dedent(
                    """\
                    {
                      "type": "object",
                      "properties": {
                        "summary": {
                          "type": "string"
                        }
                      }
                    }
                    """
                ),
                encoding="utf-8",
            )
            (root / "examples" / "repo_status.example.json").write_text(
                '{\n  "summary": "Branch is clean."\n}\n',
                encoding="utf-8",
            )
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    json schema RepoStatusSchema: "Repo Status Schema"
                        profile: OpenAIStructuredOutput
                        file: "schemas/repo_status.schema.json"

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
            emitted = emit_target(target)

            markdown_path = root / "build" / "repo_status_agent" / "AGENTS.md"
            contract_path = root / "build" / "repo_status_agent" / "AGENTS.contract.json"
            self.assertEqual(emitted, (markdown_path, contract_path))
            self.assertTrue(markdown_path.is_file())
            self.assertTrue(contract_path.is_file())

            payload = json.loads(contract_path.read_text())
            self.assertEqual(payload["contract_version"], 1)
            self.assertEqual(
                payload["agent"],
                {
                    "name": "RepoStatusAgent",
                    "slug": "repo_status_agent",
                    "entrypoint": "prompts/AGENTS.prompt",
                },
            )
            self.assertEqual(
                payload["final_output"],
                {
                    "exists": True,
                    "declaration_key": "RepoStatusFinalResponse",
                    "declaration_name": "RepoStatusFinalResponse",
                    "format_mode": "json_schema",
                    "schema_profile": "OpenAIStructuredOutput",
                    "schema_file": "schemas/repo_status.schema.json",
                    "example_file": "examples/repo_status.example.json",
                },
            )
            self.assertNotIn("review", payload)

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
            emit_target(target)

            contract_path = root / "build" / "hello_agent" / "AGENTS.contract.json"
            payload = json.loads(contract_path.read_text())
            self.assertEqual(
                payload["final_output"],
                {
                    "exists": False,
                    "declaration_key": None,
                    "declaration_name": None,
                    "format_mode": None,
                    "schema_profile": None,
                    "schema_file": None,
                    "example_file": None,
                },
            )
            self.assertNotIn("review", payload)

    def test_emit_target_includes_review_metadata_for_carrier_final_output(self) -> None:
        payload = self._emit_example_contract(
            example_dir_name="104_review_final_output_json_schema_blocked_control_ready",
            agent_slug_name="acceptance_review_blocked_json_demo",
        )

        self.assertEqual(
            payload["review"]["comment_output"],
            {
                "declaration_key": "AcceptanceReviewResponse",
                "declaration_name": "AcceptanceReviewResponse",
            },
        )
        self.assertEqual(payload["review"]["final_response"]["mode"], "carrier")
        self.assertEqual(
            payload["review"]["final_response"]["declaration_key"],
            "AcceptanceReviewResponse",
        )
        self.assertEqual(payload["review"]["final_response"]["review_fields"], {})
        self.assertTrue(payload["review"]["final_response"]["control_ready"])
        self.assertEqual(
            payload["review"]["carrier_fields"]["blocked_gate"],
            "failure_detail.blocked_gate",
        )
        self.assertEqual(
            payload["review"]["outcomes"],
            {
                "accept": {
                    "exists": True,
                    "verdict": "accept",
                    "route_behavior": "always",
                },
                "changes_requested": {
                    "exists": True,
                    "verdict": "changes_requested",
                    "route_behavior": "never",
                },
                "blocked": {
                    "exists": True,
                    "verdict": "changes_requested",
                    "route_behavior": "never",
                },
            },
        )

    def test_emit_target_marks_split_control_ready_review_final_output(self) -> None:
        payload = self._emit_example_contract(
            example_dir_name="105_review_split_final_output_json_schema_control_ready",
            agent_slug_name="acceptance_review_split_control_ready_demo",
        )

        self.assertEqual(payload["review"]["final_response"]["mode"], "split")
        self.assertEqual(
            payload["review"]["final_response"]["declaration_key"],
            "AcceptanceControlFinalResponse",
        )
        self.assertEqual(
            payload["review"]["final_response"]["review_fields"],
            {
                "verdict": "verdict",
                "current_artifact": "current_artifact",
                "next_owner": "next_owner",
                "blocked_gate": "blocked_gate",
            },
        )
        self.assertTrue(payload["review"]["final_response"]["control_ready"])
        self.assertEqual(
            payload["review"]["outcomes"]["blocked"]["route_behavior"],
            "never",
        )

    def test_emit_target_marks_split_partial_review_final_output(self) -> None:
        prompt_text = (
            REPO_ROOT
            / "examples"
            / "106_review_split_final_output_json_schema_partial"
            / "prompts"
            / "AGENTS.prompt"
        ).read_text(encoding="utf-8")
        payload = self._emit_example_contract(
            example_dir_name="106_review_split_final_output_json_schema_partial",
            agent_slug_name="acceptance_review_split_partial_demo",
            prompt_text_override=prompt_text.split("\n\noutput SummaryReply:", 1)[0],
        )

        self.assertEqual(payload["review"]["final_response"]["mode"], "split")
        self.assertEqual(
            payload["review"]["final_response"]["review_fields"],
            {
                "current_artifact": "current_artifact",
                "next_owner": "next_owner",
            },
        )
        self.assertFalse(payload["review"]["final_response"]["control_ready"])
        self.assertEqual(
            payload["review"]["outcomes"]["accept"]["route_behavior"],
            "always",
        )
        self.assertEqual(
            payload["review"]["outcomes"]["changes_requested"]["route_behavior"],
            "never",
        )

    def test_emit_target_rejects_support_files_outside_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir).resolve()
            root = base / "project"
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (base / "external.schema.json").write_text(
                '{\n  "type": "object",\n  "properties": {}\n}\n',
                encoding="utf-8",
            )
            (base / "external.example.json").write_text("{ }\n", encoding="utf-8")
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    json schema RepoStatusSchema: "Repo Status Schema"
                        profile: OpenAIStructuredOutput
                        file: "../external.schema.json"

                    output shape RepoStatusJson: "Repo Status JSON"
                        kind: JsonObject
                        schema: RepoStatusSchema
                        example_file: "../external.example.json"

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
            with self.assertRaises(EmitError) as exc_info:
                emit_target(target)

            self.assertEqual(exc_info.exception.code, "E519")
            self.assertIn("outside the target project root", str(exc_info.exception))


if __name__ == "__main__":
    unittest.main()
