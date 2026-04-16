from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import textwrap
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from doctrine.emit_common import load_emit_targets
from doctrine.emit_docs import emit_target
from doctrine.prove_output_schema_openai import main as prove_output_schema_openai_main


class ProveOutputSchemaOpenAITests(unittest.TestCase):
    def _emit_structured_schema(
        self,
        *,
        include_example: bool = False,
    ) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        prompts = root / "prompts"
        prompts.mkdir(parents=True)
        example_block = ""
        if include_example:
            example_block = textwrap.dedent(
                """\

                    example:
                        summary: "Branch is clean."
                """
            )
        (prompts / "AGENTS.prompt").write_text(
            textwrap.dedent(
                f"""\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field summary: "Summary"
                        type: string
                {example_block}

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

    def test_cli_requires_openai_api_key(self) -> None:
        temp_dir, schema_path = self._emit_structured_schema()
        self.addCleanup(temp_dir.cleanup)

        stderr = io.StringIO()
        with (
            patch.dict(os.environ, {}, clear=True),
            contextlib.redirect_stderr(stderr),
        ):
            exit_code = prove_output_schema_openai_main(
                ["--schema", str(schema_path), "--model", "gpt-4.1"]
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("OPENAI_API_KEY is not set", stderr.getvalue())

    def test_cli_submits_schema_with_official_responses_shape(self) -> None:
        temp_dir, schema_path = self._emit_structured_schema()
        self.addCleanup(temp_dir.cleanup)
        captured: dict[str, object] = {}

        class FakeResponses:
            def create(self, **kwargs: object) -> object:
                captured["request"] = kwargs
                return types.SimpleNamespace(
                    id="resp_test_123",
                    output_text='{"summary":"Branch is clean."}',
                )

        class FakeOpenAI:
            def __init__(self, *, api_key: str) -> None:
                captured["api_key"] = api_key
                self.responses = FakeResponses()

        fake_module = types.SimpleNamespace(OpenAI=FakeOpenAI)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True),
            patch.dict(sys.modules, {"openai": fake_module}),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            exit_code = prove_output_schema_openai_main(
                ["--schema", str(schema_path), "--model", "gpt-4.1"]
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(captured["api_key"], "test-key")
        request = captured["request"]
        self.assertEqual(request["model"], "gpt-4.1")
        self.assertEqual(
            request["text"]["format"]["type"],
            "json_schema",
        )
        self.assertEqual(
            request["text"]["format"]["name"],
            "repo_status_final_response",
        )
        self.assertTrue(request["text"]["format"]["strict"])
        self.assertEqual(request["text"]["format"]["schema"]["required"], ["summary"])
        self.assertIn("accepted", stdout.getvalue())
        self.assertIn("response_id: resp_test_123", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
