from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from doctrine.compiler import CompilationSession
from doctrine.emit_common import root_concrete_agents
from doctrine.emit_flow import main as emit_flow_main
from doctrine.parser import parse_file


class EmitFlowCliTests(unittest.TestCase):
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
        self.assertIn("Pinned D2 dependency is unavailable", output)
        self.assertIn("Node.js is required to render flow SVG output", output)
        self.assertIn("Run `npm ci` at the repo root.", output)

    def test_split_review_final_outputs_keep_review_bound_trust_surface_in_flow(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for prompt_rel_path, output_name in (
            (
                "examples/84_review_split_final_output_prose/prompts/AGENTS.prompt",
                "DraftReviewDecision",
            ),
            (
                "examples/85_review_split_final_output_json_schema/prompts/AGENTS.prompt",
                "AcceptanceControlFinalResponse",
            ),
        ):
            with self.subTest(prompt=prompt_rel_path):
                prompt = parse_file(repo_root / prompt_rel_path)

                # Split review final outputs inherit current-artifact truth from
                # the attached review. Flow extraction must keep that label live,
                # or shipped flow emit targets can fail before they render.
                graph = CompilationSession(prompt).extract_target_flow_graph(
                    root_concrete_agents(prompt)
                )
                outputs = {node.name: node for node in graph.outputs}

                self.assertIn(output_name, outputs)
                self.assertEqual(outputs[output_name].trust_surface, ("Current Artifact",))


if __name__ == "__main__":
    unittest.main()
