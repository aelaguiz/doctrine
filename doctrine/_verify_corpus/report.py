from __future__ import annotations

from dataclasses import dataclass

from doctrine.diagnostics import DoctrineError

from doctrine._verify_corpus.manifest import CaseSpec, _display_path


class VerificationError(RuntimeError):
    """Raised when a case result does not match its contract."""


@dataclass(slots=True, frozen=True)
class CaseResult:
    case: CaseSpec
    result: str
    detail: str


@dataclass(slots=True, frozen=True)
class RefDiff:
    case: CaseSpec
    label: str
    diff: str


@dataclass(slots=True)
class VerificationReport:
    manifest_errors: list[str]
    case_results: list[CaseResult]
    ref_diffs: list[RefDiff]
    surfaced_inconsistencies: list[str]

    def failed(self) -> bool:
        return bool(
            self.manifest_errors
            or any(result.result == "FAIL" for result in self.case_results)
            or self.surfaced_inconsistencies
        )


def format_report(report: VerificationReport) -> str:
    lines: list[str] = []

    if report.manifest_errors:
        lines.append("Manifest errors:")
        for error in report.manifest_errors:
            lines.append(f"- {error}")
        lines.append("")

    lines.append("Case results:")
    if report.case_results:
        for result in report.case_results:
            case_path = _display_path(result.case.manifest_path)
            lines.append(
                f"- {result.result} {case_path} :: {result.case.name} :: {result.detail}"
            )
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Checked ref diffs:")
    if report.ref_diffs:
        for ref_diff in report.ref_diffs:
            lines.append(f"- {ref_diff.label}")
            lines.append(ref_diff.diff.rstrip("\n"))
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Surfaced inconsistencies:")
    if report.surfaced_inconsistencies:
        for inconsistency in report.surfaced_inconsistencies:
            lines.append(f"- {inconsistency}")
    else:
        lines.append("- None surfaced during this run.")

    return "\n".join(lines)


def _format_case_failure(exc: Exception) -> str:
    if isinstance(exc, DoctrineError):
        return f"{type(exc).__name__} [{exc.code}]:\n{exc}"
    return f"{type(exc).__name__}: {exc}"
