from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from doctrine.diagnostics import DiagnosticLocation, EmitError
from doctrine.verify_corpus import CaseSpec, VerificationError, _run_build_contract


REPO_ROOT = Path(__file__).resolve().parents[1]
MISSING_MANIFEST = "does/not/exist/cases.toml"


class VerifyCorpusCliTests(unittest.TestCase):
    def test_missing_manifest_reports_a_manifest_error(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "doctrine.verify_corpus", "--manifest", MISSING_MANIFEST],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertNotIn("Traceback", result.stdout)
        self.assertIn("Manifest errors:", result.stdout)
        self.assertIn(f"- Missing manifest file(s): {MISSING_MANIFEST}", result.stdout)
        self.assertIn("Case results:\n- None.", result.stdout)

    def test_missing_absolute_manifest_outside_repo_reports_a_manifest_error(self) -> None:
        missing_manifest = (
            Path(tempfile.gettempdir()) / f"doctrine-missing-{uuid.uuid4()}.toml"
        ).resolve()

        result = subprocess.run(
            [sys.executable, "-m", "doctrine.verify_corpus", "--manifest", str(missing_manifest)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        # The CLI accepts absolute manifest paths, so a missing one outside the repo
        # must still render a normal manifest report instead of crashing while formatting it.
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertNotIn("Traceback", result.stdout)
        self.assertIn("Manifest errors:", result.stdout)
        self.assertIn(f"- Missing manifest file(s): {missing_manifest}", result.stdout)
        self.assertIn("Case results:\n- None.", result.stdout)


class VerifyCorpusBuildContractTests(unittest.TestCase):
    def test_emit_target_loading_failure_becomes_a_verification_error(self) -> None:
        case = CaseSpec(
            manifest_path=(REPO_ROOT / "examples/01_hello_world/cases.toml").resolve(),
            example_dir=(REPO_ROOT / "examples/01_hello_world").resolve(),
            name="emit target loading surfaces cleanly",
            kind="build_contract",
            prompt_path=(REPO_ROOT / "examples/01_hello_world/prompts/AGENTS.prompt").resolve(),
            build_target="missing-target",
            approx_ref_path=None,
        )
        emit_error = EmitError.from_parts(
            code="E503",
            summary="Missing emit targets",
            detail="The current `pyproject.toml` does not define any `[tool.doctrine.emit.targets]`.",
            location=DiagnosticLocation(path=(REPO_ROOT / "pyproject.toml").resolve()),
        )

        # Manifest-backed proof runs should report emit-target loading problems as
        # ordinary verification failures instead of crashing the verifier itself.
        with patch("doctrine.verify_corpus.load_emit_targets", side_effect=emit_error):
            with self.assertRaises(VerificationError) as ctx:
                _run_build_contract(case)

        self.assertIn("Missing emit targets", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
