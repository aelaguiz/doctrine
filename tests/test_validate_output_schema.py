from __future__ import annotations

import contextlib
import io
import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.emit_common import load_emit_targets
from doctrine.emit_docs import emit_target
from doctrine.validate_output_schema import main as validate_output_schema_main


class ValidateOutputSchemaCliTests(unittest.TestCase):
    def _emit_structured_schema(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        prompts = root / "prompts"
        prompts.mkdir(parents=True)
        (prompts / "AGENTS.prompt").write_text(
            textwrap.dedent(
                """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field summary: "Summary"
                        type: string
                        required

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
        emit_target(load_emit_targets(pyproject)["demo"])
        schema_path = (
            root
            / "build"
            / "repo_status_agent"
            / "schemas"
            / "repo_status_final_response.schema.json"
        )
        return temp_dir, schema_path

    def test_cli_validates_emitted_schema_file(self) -> None:
        temp_dir, schema_path = self._emit_structured_schema()
        self.addCleanup(temp_dir.cleanup)

        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = validate_output_schema_main(["--schema", str(schema_path)])

        self.assertEqual(exit_code, 0)
        self.assertIn("validated", stdout.getvalue())
        self.assertIn(str(schema_path), stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_cli_rejects_non_object_schema_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            schema_path = Path(temp_dir) / "bad.schema.json"
            schema_path.write_text("[]\n", encoding="utf-8")

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = validate_output_schema_main(["--schema", str(schema_path)])

        self.assertEqual(exit_code, 1)
        self.assertIn("schema file must contain one JSON object", stderr.getvalue())

    def test_cli_rejects_openai_subset_violation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            schema_path = Path(temp_dir) / "bad.schema.json"
            schema_path.write_text(
                json.dumps(
                    {
                        "type": "object",
                        "properties": {"summary": {"type": "string"}},
                        "required": ["summary"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = validate_output_schema_main(["--schema", str(schema_path)])

        self.assertEqual(exit_code, 1)
        self.assertIn("E218", stderr.getvalue())
        self.assertIn("additionalProperties: false", stderr.getvalue())

    def test_cli_validates_optional_example_file(self) -> None:
        temp_dir, schema_path = self._emit_structured_schema()
        self.addCleanup(temp_dir.cleanup)
        example_path = Path(temp_dir.name) / "example.json"
        example_path.write_text('{"summary": "Branch is clean."}\n', encoding="utf-8")

        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = validate_output_schema_main(
                ["--schema", str(schema_path), "--example", str(example_path)]
            )

        self.assertEqual(exit_code, 0)
        self.assertIn(str(example_path), stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_cli_rejects_invalid_example_file(self) -> None:
        temp_dir, schema_path = self._emit_structured_schema()
        self.addCleanup(temp_dir.cleanup)
        example_path = Path(temp_dir.name) / "example.json"
        example_path.write_text('{"summary": 7}\n', encoding="utf-8")

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = validate_output_schema_main(
                ["--schema", str(schema_path), "--example", str(example_path)]
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("E216", stderr.getvalue())
        self.assertIn("does not match lowered schema", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
