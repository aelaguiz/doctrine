from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
