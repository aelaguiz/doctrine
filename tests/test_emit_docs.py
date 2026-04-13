from __future__ import annotations

import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.diagnostics import EmitError
from doctrine.emit_common import load_emit_targets
from doctrine.emit_docs import emit_target


class EmitDocsTests(unittest.TestCase):
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
