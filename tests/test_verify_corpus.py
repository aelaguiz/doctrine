from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from doctrine.diagnostics import DiagnosticLocation, EmitError
from doctrine.verify_corpus import (
    CaseSpec,
    VerificationError,
    _build_tree_diff,
    _run_build_contract,
)


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
    def _flow_build_contract_case(self) -> CaseSpec:
        return CaseSpec(
            manifest_path=(REPO_ROOT / "examples/73_flow_visualizer_showcase/cases.toml").resolve(),
            example_dir=(REPO_ROOT / "examples/73_flow_visualizer_showcase").resolve(),
            name="flow build-contract proof",
            kind="build_contract",
            prompt_path=(
                REPO_ROOT / "examples/73_flow_visualizer_showcase/prompts/AGENTS.prompt"
            ).resolve(),
            build_target="example_73_flow_visualizer_showcase",
            approx_ref_path=None,
        )

    def _runtime_package_build_contract_case(self) -> CaseSpec:
        return CaseSpec(
            manifest_path=(REPO_ROOT / "examples/115_runtime_agent_packages/cases.toml").resolve(),
            example_dir=(REPO_ROOT / "examples/115_runtime_agent_packages").resolve(),
            name="runtime package build-contract proof stays checked in",
            kind="build_contract",
            prompt_path=(
                REPO_ROOT / "examples/115_runtime_agent_packages/prompts/AGENTS.prompt"
            ).resolve(),
            build_target="example_115_runtime_agent_packages",
            approx_ref_path=None,
        )

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

    def test_binary_build_diff_reports_a_binary_mismatch_cleanly(self) -> None:
        # This protects the verifier path for bundled binary assets. When bytes
        # differ, the user should get a clear path-level mismatch report instead
        # of a Unicode decode crash or a lossy text diff.
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            expected_root = root / "expected"
            actual_root = root / "actual"
            expected_root.mkdir()
            actual_root.mkdir()
            (expected_root / "icon.png").write_bytes(b"\x89PNGexpected")
            (actual_root / "icon.png").write_bytes(b"\x89PNGactual")

            diff = _build_tree_diff(expected_root=expected_root, actual_root=actual_root)

        self.assertIsNotNone(diff)
        self.assertIn("Binary file mismatch: icon.png", diff)
        self.assertIn("expected 12 bytes", diff)
        self.assertIn("emitted 10 bytes", diff)

    def test_build_contract_uses_repo_root_emit_targets_even_when_cwd_moves(self) -> None:
        case = CaseSpec(
            manifest_path=(REPO_ROOT / "examples/07_handoffs/cases.toml").resolve(),
            example_dir=(REPO_ROOT / "examples/07_handoffs").resolve(),
            name="repo-root emit target lookup stays stable",
            kind="build_contract",
            prompt_path=(REPO_ROOT / "examples/07_handoffs/prompts/AGENTS.prompt").resolve(),
            build_target="example_07_handoffs",
            approx_ref_path=None,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            os.chdir(temp_dir)
            try:
                # Build-contract verification is repo-owned proof. It must keep
                # loading the repo's emit target registry even if the caller runs
                # the verifier from another working directory.
                result = _run_build_contract(case)
            finally:
                os.chdir(original_cwd)

        self.assertEqual(result.result, "PASS")
        self.assertEqual(result.detail, "build matched checked-in tree")

    def test_flow_build_contract_surfaces_missing_pinned_d2_cleanly(self) -> None:
        case = self._flow_build_contract_case()

        missing_package = (
            Path(tempfile.gettempdir())
            / f"doctrine-missing-d2-{uuid.uuid4()}"
            / "package.json"
        ).resolve()

        # Flow build-contract proof depends on the pinned D2 package. If that
        # package is missing, the verifier should report one clean verification
        # failure with the emit code and setup hint instead of crashing.
        with patch("doctrine.flow_renderer.D2_PACKAGE_PATH", missing_package):
            with self.assertRaises(VerificationError) as ctx:
                _run_build_contract(case)

        rendered = str(ctx.exception)
        self.assertIn("E515 emit error", rendered)
        self.assertIn("Flow renderer prerequisite is unavailable", rendered)
        self.assertIn("Run `npm ci`", rendered)

    def test_flow_build_contract_surfaces_missing_helper_cleanly(self) -> None:
        case = self._flow_build_contract_case()

        with tempfile.TemporaryDirectory() as temp_dir:
            package_json = Path(temp_dir) / "node_modules" / "@terrastruct" / "d2" / "package.json"
            package_json.parent.mkdir(parents=True)
            package_json.write_text("{}\n")
            missing_helper = Path(temp_dir) / "missing_flow_svg.mjs"

            # Flow build-contract proof wraps `emit_target_flow()` through the
            # verifier. A missing shipped helper must still become one readable
            # verification failure instead of an uncaught filesystem error.
            with (
                patch("doctrine.flow_renderer.D2_PACKAGE_PATH", package_json),
                patch("doctrine.flow_renderer.D2_HELPER_PATH", missing_helper),
            ):
                with self.assertRaises(VerificationError) as ctx:
                    _run_build_contract(case)

        rendered = str(ctx.exception)
        self.assertIn("E515 emit error", rendered)
        self.assertIn("Flow renderer prerequisite is unavailable", rendered)
        self.assertIn("Doctrine flow renderer helper is missing", rendered)
        self.assertIn("Restore the `flow_svg.mjs` helper file.", rendered)

    def test_flow_build_contract_surfaces_renderer_failure_cleanly(self) -> None:
        case = self._flow_build_contract_case()

        with tempfile.TemporaryDirectory() as temp_dir:
            package_json = Path(temp_dir) / "node_modules" / "@terrastruct" / "d2" / "package.json"
            package_json.parent.mkdir(parents=True)
            package_json.write_text("{}\n")
            helper = Path(temp_dir) / "flow_svg.mjs"
            helper.write_text("// helper stub\n")

            # Flow build-contract proof should keep renderer crash detail when
            # the Node helper exits non-zero, so verifier output still tells the
            # caller what failed inside the flow render step.
            with (
                patch("doctrine.flow_renderer.D2_PACKAGE_PATH", package_json),
                patch("doctrine.flow_renderer.D2_HELPER_PATH", helper),
                patch(
                    "doctrine.flow_renderer.subprocess.run",
                    return_value=subprocess.CompletedProcess(
                        args=["node", str(helper)],
                        returncode=9,
                        stdout="",
                        stderr="render crashed",
                    ),
                ),
            ):
                with self.assertRaises(VerificationError) as ctx:
                    _run_build_contract(case)

        rendered = str(ctx.exception)
        self.assertIn("E516 emit error", rendered)
        self.assertIn("Pinned D2 renderer failed", rendered)
        self.assertIn(
            "Could not render `AGENTS.flow.svg` from `AGENTS.flow.d2`: render crashed",
            rendered,
        )

    def test_runtime_package_build_contract_stays_checked_in(self) -> None:
        result = _run_build_contract(self._runtime_package_build_contract_case())

        self.assertEqual(result.result, "PASS")
        self.assertEqual(result.detail, "build matched checked-in tree")


if __name__ == "__main__":
    unittest.main()
