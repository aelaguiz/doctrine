from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from doctrine._diagnostics.contracts import DiagnosticRelatedLocation
from doctrine.diagnostics import CompileError, DiagnosticLocation, EmitError
from doctrine.verify_corpus import (
    CaseSpec,
    ExpectedDiagnosticSite,
    ManifestError,
    VerificationError,
    _assert_expected_exception,
    _build_tree_diff,
    _load_manifest,
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

    def test_flow_build_contract_surfaces_renderer_timeout_cleanly(self) -> None:
        case = self._flow_build_contract_case()

        with tempfile.TemporaryDirectory() as temp_dir:
            package_json = Path(temp_dir) / "node_modules" / "@terrastruct" / "d2" / "package.json"
            package_json.parent.mkdir(parents=True)
            package_json.write_text("{}\n")
            helper = Path(temp_dir) / "flow_svg.mjs"
            helper.write_text("// helper stub\n")

            # The corpus verifier runs flow SVG rendering as part of exact-tree
            # proof. A stuck Node renderer must become one bounded verification
            # failure, not a hung test or an unreadable subprocess traceback.
            with (
                patch("doctrine.flow_renderer.D2_PACKAGE_PATH", package_json),
                patch("doctrine.flow_renderer.D2_HELPER_PATH", helper),
                patch(
                    "doctrine.flow_renderer.subprocess.run",
                    side_effect=subprocess.TimeoutExpired(
                        cmd=["node", str(helper)],
                        timeout=60,
                    ),
                ),
            ):
                with self.assertRaises(VerificationError) as ctx:
                    _run_build_contract(case)

        rendered = str(ctx.exception)
        self.assertIn("E516 emit error", rendered)
        self.assertIn("Pinned D2 renderer failed", rendered)
        self.assertIn(
            "Could not render `AGENTS.flow.svg` from `AGENTS.flow.d2`: "
            "node timed out after 60 seconds while rendering flow SVG output",
            rendered,
        )

    def test_runtime_package_build_contract_stays_checked_in(self) -> None:
        result = _run_build_contract(self._runtime_package_build_contract_case())

        self.assertEqual(result.result, "PASS")
        self.assertEqual(result.detail, "build matched checked-in tree")


class VerifyCorpusCompileFailContractTests(unittest.TestCase):
    def test_compile_fail_manifest_loads_structured_location_and_related_sites(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            example_dir = Path(temp_dir).resolve()
            prompts = example_dir / "prompts"
            prompts.mkdir()
            (prompts / "AGENTS.prompt").write_text(
                "agent Demo:\n    role: \"Demo.\"\n",
                encoding="utf-8",
            )
            (prompts / "helper.prompt").write_text(
                "workflow Helper: \"Helper\"\n    \"Explain.\"\n",
                encoding="utf-8",
            )
            manifest_path = example_dir / "cases.toml"
            manifest_path.write_text(
                """\
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "structured compile fail"
status = "active"
kind = "compile_fail"
exception_type = "CompileError"
error_code = "E204"
location_line = 3
related = [
    { line = 1, label = "first field" },
    { path = "prompts/helper.prompt", line = 2 },
]
""",
                encoding="utf-8",
            )

            cases = _load_manifest(manifest_path)

        self.assertEqual(len(cases), 1)
        case = cases[0]
        self.assertEqual(case.expected_location, ExpectedDiagnosticSite(line=3))
        self.assertEqual(
            case.expected_related,
            (
                ExpectedDiagnosticSite(line=1, label="first field"),
                ExpectedDiagnosticSite(path=(prompts / "helper.prompt").resolve(), line=2),
            ),
        )

    def test_compile_fail_manifest_rejects_message_contains(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            example_dir = Path(temp_dir).resolve()
            prompts = example_dir / "prompts"
            prompts.mkdir()
            (prompts / "AGENTS.prompt").write_text(
                "agent Demo:\n    role: \"Demo.\"\n",
                encoding="utf-8",
            )
            manifest_path = example_dir / "cases.toml"
            manifest_path.write_text(
                """\
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "stale compile fail"
status = "active"
kind = "compile_fail"
exception_type = "CompileError"
message_contains = ["stale"]
""",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ManifestError, "message_contains is retired"):
                _load_manifest(manifest_path)

    def test_compile_fail_contract_asserts_location_and_related_sites(self) -> None:
        prompt_path = (REPO_ROOT / "examples/01_hello_world/prompts/AGENTS.prompt").resolve()
        case = CaseSpec(
            manifest_path=(REPO_ROOT / "examples/01_hello_world/cases.toml").resolve(),
            example_dir=(REPO_ROOT / "examples/01_hello_world").resolve(),
            name="structured compile fail proof",
            kind="compile_fail",
            prompt_path=prompt_path,
            approx_ref_path=None,
            exception_type="CompileError",
            error_code="E204",
            expected_location=ExpectedDiagnosticSite(line=7),
            expected_related=(ExpectedDiagnosticSite(line=3, label="first field"),),
        )
        error = CompileError.from_parts(
            code="E204",
            summary="Duplicate typed field",
            detail="The agent defines `output:` more than once.",
            location=DiagnosticLocation(path=prompt_path, line=7, column=5),
            related=(
                DiagnosticRelatedLocation(
                    label="first field",
                    location=DiagnosticLocation(path=prompt_path, line=3, column=5),
                ),
            ),
        )

        _assert_expected_exception(case, error)

    def test_compile_fail_contract_rejects_wrong_path(self) -> None:
        prompt_path = (
            REPO_ROOT / "examples/75_cross_root_standard_library_imports/prompts/AGENTS.prompt"
        ).resolve()
        case = CaseSpec(
            manifest_path=(
                REPO_ROOT / "examples/75_cross_root_standard_library_imports/cases.toml"
            ).resolve(),
            example_dir=(REPO_ROOT / "examples/75_cross_root_standard_library_imports").resolve(),
            name="repo-scoped compile fail proof",
            kind="compile_fail",
            prompt_path=prompt_path,
            approx_ref_path=None,
            exception_type="CompileError",
            error_code="E285",
            expected_location=ExpectedDiagnosticSite(path=(REPO_ROOT / "pyproject.toml").resolve()),
        )
        error = CompileError.from_parts(
            code="E285",
            summary="Compile config is invalid",
            detail="The compile config is invalid.",
            location=DiagnosticLocation(path=prompt_path),
        )

        with self.assertRaises(VerificationError) as ctx:
            _assert_expected_exception(case, error)

        self.assertIn("expected path pyproject.toml", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
