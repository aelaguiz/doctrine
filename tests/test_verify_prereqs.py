from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from doctrine.verify_prereqs import main as verify_prereqs_main


class VerifyPrereqsCliTests(unittest.TestCase):
    def test_missing_flow_renderer_dependency_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_package = Path(temp_dir) / "missing" / "package.json"
            stderr = io.StringIO()
            with (
                patch("doctrine.flow_renderer.D2_PACKAGE_PATH", missing_package),
                contextlib.redirect_stderr(stderr),
            ):
                exit_code = verify_prereqs_main(["--require-flow-renderer"])

        output = stderr.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("Pinned D2 dependency is missing", output)
        self.assertIn("Run `npm ci` at the repo root.", output)

    def test_missing_flow_renderer_helper_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package_json = Path(temp_dir) / "node_modules" / "@terrastruct" / "d2" / "package.json"
            package_json.parent.mkdir(parents=True)
            package_json.write_text("{}\n")
            missing_helper = Path(temp_dir) / "missing_flow_svg.mjs"

            stderr = io.StringIO()
            with (
                patch("doctrine.flow_renderer.D2_PACKAGE_PATH", package_json),
                patch("doctrine.flow_renderer.D2_HELPER_PATH", missing_helper),
                contextlib.redirect_stderr(stderr),
            ):
                exit_code = verify_prereqs_main(["--require-flow-renderer"])

        output = stderr.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("Doctrine flow renderer helper is missing", output)
        self.assertIn("Restore the `flow_svg.mjs` helper file.", output)

    def test_present_flow_renderer_dependency_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package_json = Path(temp_dir) / "node_modules" / "@terrastruct" / "d2" / "package.json"
            package_json.parent.mkdir(parents=True)
            package_json.write_text("{}\n")
            helper = Path(temp_dir) / "flow_svg.mjs"
            helper.write_text("// helper stub\n")

            stderr = io.StringIO()
            with (
                patch("doctrine.flow_renderer.D2_PACKAGE_PATH", package_json),
                patch("doctrine.flow_renderer.D2_HELPER_PATH", helper),
                contextlib.redirect_stderr(stderr),
            ):
                exit_code = verify_prereqs_main(["--require-flow-renderer"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
