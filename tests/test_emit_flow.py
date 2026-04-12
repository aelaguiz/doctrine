from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from doctrine.emit_flow import main as emit_flow_main


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


if __name__ == "__main__":
    unittest.main()
