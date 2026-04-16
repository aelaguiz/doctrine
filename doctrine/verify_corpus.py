from __future__ import annotations

import argparse

from doctrine.emit_common import load_emit_targets
from doctrine.emit_docs import emit_target
from doctrine.emit_flow import emit_target_flow
from doctrine.emit_skill import emit_target_skill

from doctrine._verify_corpus.diff import _build_tree_diff
from doctrine._verify_corpus.manifest import (
    CaseSpec,
    ExpectedDiagnosticSite,
    ManifestError,
    _load_manifest,
)
from doctrine._verify_corpus.report import VerificationError, format_report
from doctrine._verify_corpus.runners import (
    _assert_expected_exception,
    _run_build_contract as _run_build_contract_internal,
    verify_corpus,
)


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    report = verify_corpus(args.manifest or None)
    print(format_report(report))
    return 1 if report.failed() else 0


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify Doctrine example manifests.")
    parser.add_argument(
        "--manifest",
        action="append",
        help="Repo-relative path to a single cases.toml manifest. Repeat to run multiple manifests.",
    )
    return parser


def _run_build_contract(case: CaseSpec) -> CaseResult:
    return _run_build_contract_internal(
        case,
        load_emit_targets_fn=load_emit_targets,
        emit_target_fn=emit_target,
        emit_target_flow_fn=emit_target_flow,
        emit_target_skill_fn=emit_target_skill,
    )


if __name__ == "__main__":
    raise SystemExit(main())
