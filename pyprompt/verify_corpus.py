from __future__ import annotations

import argparse
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from difflib import unified_diff
from pathlib import Path
from typing import Any

from pyprompt.compiler import compile_prompt
from pyprompt.diagnostics import PyPromptError
from pyprompt.emit_docs import EmitError, emit_target, load_emit_targets
from pyprompt.parser import parse_file
from pyprompt.renderer import render_markdown

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILD_CONTRACT_REF_DIR = "build_ref"


class ManifestError(RuntimeError):
    """Raised when a case manifest is structurally invalid."""


class VerificationError(RuntimeError):
    """Raised when a case outcome does not match its contract."""


@dataclass(slots=True, frozen=True)
class CaseSpec:
    manifest_path: Path
    example_dir: Path
    name: str
    status: str
    kind: str
    prompt_path: Path
    approx_ref_path: Path | None
    agent: str | None = None
    build_target: str | None = None
    assertion: str | None = None
    expected_lines: tuple[str, ...] = ()
    exception_type: str | None = None
    error_code: str | None = None
    message_contains: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class CaseResult:
    case: CaseSpec
    outcome: str
    detail: str


@dataclass(slots=True, frozen=True)
class AdvisoryDiff:
    case: CaseSpec
    label: str
    diff: str


@dataclass(slots=True)
class VerificationReport:
    manifest_errors: list[str]
    active_results: list[CaseResult]
    planned_cases: list[CaseSpec]
    advisory_diffs: list[AdvisoryDiff]
    surfaced_inconsistencies: list[str]

    def failed(self) -> bool:
        return bool(
            self.manifest_errors
            or any(result.outcome == "FAIL" for result in self.active_results)
            or self.surfaced_inconsistencies
        )


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    report = verify_corpus(args.manifest or None)
    print(format_report(report))
    return 1 if report.failed() else 0


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify PyPrompt example manifests.")
    parser.add_argument(
        "--manifest",
        action="append",
        help="Repo-relative path to a single cases.toml manifest. Repeat to run multiple manifests.",
    )
    return parser


def verify_corpus(manifest_args: list[str] | None = None) -> VerificationReport:
    manifest_errors: list[str] = []
    active_results: list[CaseResult] = []
    planned_cases: list[CaseSpec] = []
    advisory_diffs: list[AdvisoryDiff] = []
    surfaced_inconsistencies: list[str] = []

    try:
        manifests = _resolve_manifest_paths(manifest_args)
    except ManifestError as exc:
        return VerificationReport(
            manifest_errors=[str(exc)],
            active_results=active_results,
            planned_cases=planned_cases,
            advisory_diffs=advisory_diffs,
            surfaced_inconsistencies=surfaced_inconsistencies,
        )

    cases: list[CaseSpec] = []
    for manifest_path in manifests:
        try:
            cases.extend(_load_manifest(manifest_path))
        except ManifestError as exc:
            manifest_errors.append(f"{_display_path(manifest_path)}: {exc}")

    for case in cases:
        if case.status == "planned":
            planned_cases.append(case)
            advisory_diff = _build_contract_ref_diff(
                case,
                expected_lines=case.expected_lines,
                output_label=f"contract://{case.name}",
            )
            if advisory_diff is not None:
                advisory_diffs.append(advisory_diff)
            continue

        try:
            if case.kind == "render_contract":
                active_results.append(_run_render_contract(case, advisory_diffs))
            elif case.kind == "build_contract":
                active_results.append(_run_build_contract(case))
            elif case.kind == "parse_fail":
                active_results.append(_run_parse_fail(case))
            elif case.kind == "compile_fail":
                active_results.append(_run_compile_fail(case))
            else:  # pragma: no cover - blocked by manifest validation
                raise ManifestError(f"Unsupported case kind {case.kind!r}.")
        except Exception as exc:  # pragma: no cover - exercised by the command itself
            active_results.append(
                CaseResult(case=case, outcome="FAIL", detail=_format_case_failure(exc))
            )

    return VerificationReport(
        manifest_errors=manifest_errors,
        active_results=active_results,
        planned_cases=planned_cases,
        advisory_diffs=advisory_diffs,
        surfaced_inconsistencies=surfaced_inconsistencies,
    )


def _resolve_manifest_paths(manifest_args: list[str] | None) -> tuple[Path, ...]:
    if manifest_args:
        resolved = tuple(_resolve_repo_path(manifest) for manifest in manifest_args)
    else:
        resolved = tuple(sorted((REPO_ROOT / "examples").glob("*/cases.toml")))

    if not resolved:
        raise ManifestError("No manifest files were found.")

    missing = [path for path in resolved if not path.is_file()]
    if missing:
        formatted = ", ".join(str(path.relative_to(REPO_ROOT)) for path in missing)
        raise ManifestError(f"Missing manifest file(s): {formatted}")

    return resolved


def _resolve_repo_path(path_str: str) -> Path:
    candidate = Path(path_str)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    return candidate.resolve()


def _load_manifest(path: Path) -> tuple[CaseSpec, ...]:
    try:
        raw = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as exc:
        raise ManifestError(f"Invalid TOML: {exc}") from exc

    if not isinstance(raw, dict):
        raise ManifestError("Manifest root must be a TOML table.")

    schema_version = raw.get("schema_version")
    if schema_version != 1:
        raise ManifestError(f"Expected schema_version = 1, got {schema_version!r}.")

    example_dir = path.parent.resolve()
    default_prompt_rel = _require_str(raw, "default_prompt")
    default_prompt_path = _resolve_example_path(
        example_dir, default_prompt_rel, label="default_prompt"
    )

    raw_cases = raw.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ManifestError("Manifest must define at least one [[cases]] entry.")

    seen_names: set[str] = set()
    cases: list[CaseSpec] = []
    for index, raw_case in enumerate(raw_cases, start=1):
        if not isinstance(raw_case, dict):
            raise ManifestError(f"cases[{index}] must be a TOML table.")
        case = _load_case(
            manifest_path=path.resolve(),
            example_dir=example_dir,
            default_prompt_path=default_prompt_path,
            default_prompt_rel=default_prompt_rel,
            raw_case=raw_case,
            case_index=index,
        )
        if case.name in seen_names:
            raise ManifestError(f"Duplicate case name {case.name!r} in {path.name}.")
        seen_names.add(case.name)
        cases.append(case)

    return tuple(cases)


def _load_case(
    *,
    manifest_path: Path,
    example_dir: Path,
    default_prompt_path: Path,
    default_prompt_rel: str,
    raw_case: dict[str, Any],
    case_index: int,
) -> CaseSpec:
    name = _require_str(raw_case, "name", case_index=case_index)
    status = _require_choice(
        raw_case,
        "status",
        {"active", "planned"},
        case_index=case_index,
    )
    kind = _require_choice(
        raw_case,
        "kind",
        {"render_contract", "build_contract", "parse_fail", "compile_fail"},
        case_index=case_index,
    )

    prompt_rel = raw_case.get("prompt", default_prompt_rel)
    if not isinstance(prompt_rel, str):
        raise ManifestError(f"cases[{case_index}].prompt must be a string when provided.")
    prompt_path = (
        default_prompt_path
        if prompt_rel == default_prompt_rel
        else _resolve_example_path(example_dir, prompt_rel, label=f"cases[{case_index}].prompt")
    )

    approx_ref_rel = raw_case.get("approx_ref")
    approx_ref_path: Path | None = None
    if approx_ref_rel is not None:
        if not isinstance(approx_ref_rel, str):
            raise ManifestError(
                f"cases[{case_index}].approx_ref must be a string when provided."
            )
        approx_ref_path = _resolve_example_path(
            example_dir, approx_ref_rel, label=f"cases[{case_index}].approx_ref"
        )

    if kind == "render_contract":
        agent = _require_str(raw_case, "agent", case_index=case_index)
        assertion = _require_choice(
            raw_case, "assertion", {"exact_lines"}, case_index=case_index
        )
        expected_lines = _require_string_list(
            raw_case, "expected_lines", case_index=case_index
        )
        return CaseSpec(
            manifest_path=manifest_path,
            example_dir=example_dir,
            name=name,
            status=status,
            kind=kind,
            prompt_path=prompt_path,
            approx_ref_path=approx_ref_path,
            agent=agent,
            assertion=assertion,
            expected_lines=expected_lines,
        )

    if kind == "build_contract":
        build_target = _require_str(raw_case, "build_target", case_index=case_index)
        return CaseSpec(
            manifest_path=manifest_path,
            example_dir=example_dir,
            name=name,
            status=status,
            kind=kind,
            prompt_path=prompt_path,
            approx_ref_path=approx_ref_path,
            build_target=build_target,
        )

    exception_type = _require_str(raw_case, "exception_type", case_index=case_index)
    error_code = raw_case.get("error_code")
    if error_code is not None and not isinstance(error_code, str):
        raise ManifestError(f"cases[{case_index}].error_code must be a string when provided.")
    message_contains = _require_string_list(
        raw_case, "message_contains", case_index=case_index
    )

    agent: str | None = None
    if kind == "compile_fail":
        agent = _require_str(raw_case, "agent", case_index=case_index)

    return CaseSpec(
        manifest_path=manifest_path,
        example_dir=example_dir,
        name=name,
        status=status,
        kind=kind,
        prompt_path=prompt_path,
        approx_ref_path=approx_ref_path,
        agent=agent,
        exception_type=exception_type,
        error_code=error_code,
        message_contains=message_contains,
    )


def _resolve_example_path(example_dir: Path, rel_path: str, *, label: str) -> Path:
    resolved = (example_dir / rel_path).resolve()
    try:
        resolved.relative_to(example_dir)
    except ValueError as exc:
        raise ManifestError(
            f"{label} escapes the owning example directory: {rel_path!r}."
        ) from exc

    if not resolved.is_file():
        raise ManifestError(f"{label} does not exist: {rel_path!r}.")

    return resolved


def _run_render_contract(
    case: CaseSpec, advisory_diffs: list[AdvisoryDiff]
) -> CaseResult:
    prompt_file = parse_file(case.prompt_path)
    compiled = compile_prompt(prompt_file, case.agent or "")
    rendered = render_markdown(compiled)
    advisory_diff = _build_contract_ref_diff(
        case,
        expected_lines=tuple(rendered.splitlines()),
        output_label=f"rendered://{case.agent}",
    )
    if advisory_diff is not None:
        advisory_diffs.append(advisory_diff)

    actual_lines = tuple(rendered.splitlines())
    if actual_lines != case.expected_lines:
        diff = _build_diff(
            case.expected_lines,
            actual_lines,
            fromfile=f"expected://{case.name}",
            tofile=f"rendered://{case.agent}",
        )
        raise VerificationError(
            "Rendered output did not match the prompt-derived contract.\n"
            + diff
        )

    return CaseResult(
        case=case,
        outcome="PASS",
        detail="render matched exact_lines contract",
    )


def _run_parse_fail(case: CaseSpec) -> CaseResult:
    try:
        parse_file(case.prompt_path)
    except Exception as exc:
        _assert_expected_exception(case, exc)
        return CaseResult(case=case, outcome="PASS", detail="parse failed as expected")

    raise VerificationError("Expected parse to fail, but it succeeded.")


def _run_build_contract(case: CaseSpec) -> CaseResult:
    try:
        targets = load_emit_targets(start_dir=REPO_ROOT)
        target = targets.get(case.build_target or "")
        if target is None:
            raise VerificationError(f"Unknown build target: {case.build_target}")
    except EmitError as exc:
        raise VerificationError(str(exc)) from exc

    expected_root = case.example_dir / BUILD_CONTRACT_REF_DIR
    if not expected_root.is_dir():
        raise VerificationError(
            "Checked-in build reference tree does not exist for target "
            f"{target.name}: {expected_root}"
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        actual_root = Path(temp_dir)
        try:
            emit_target(target, output_dir_override=actual_root)
        except EmitError as exc:
            raise VerificationError(str(exc)) from exc

        diff = _build_tree_diff(expected_root=expected_root, actual_root=actual_root)
        if diff is not None:
            raise VerificationError(
                "Emitted build tree did not match the checked-in build contract.\n" + diff
            )

    return CaseResult(
        case=case,
        outcome="PASS",
        detail="build matched checked-in tree",
    )


def _run_compile_fail(case: CaseSpec) -> CaseResult:
    prompt_file = parse_file(case.prompt_path)
    try:
        compile_prompt(prompt_file, case.agent or "")
    except Exception as exc:
        _assert_expected_exception(case, exc)
        return CaseResult(case=case, outcome="PASS", detail="compile failed as expected")

    raise VerificationError("Expected compile to fail, but it succeeded.")


def _assert_expected_exception(case: CaseSpec, exc: Exception) -> None:
    actual_type = type(exc).__name__
    if actual_type != case.exception_type:
        raise VerificationError(
            f"Expected {case.exception_type}, got {actual_type}: {exc}"
        )

    actual_code = getattr(exc, "code", None)
    if case.error_code is not None and actual_code != case.error_code:
        raise VerificationError(
            f"Expected error code {case.error_code}, got {actual_code}: {exc}"
        )

    message = str(exc)
    missing = [snippet for snippet in case.message_contains if snippet not in message]
    if missing:
        joined = ", ".join(repr(snippet) for snippet in missing)
        raise VerificationError(
            f"{case.exception_type} did not include required excerpt(s): {joined}"
        )


def _build_contract_ref_diff(
    case: CaseSpec, *, expected_lines: tuple[str, ...], output_label: str
) -> AdvisoryDiff | None:
    if case.approx_ref_path is None:
        return None

    ref_lines = tuple(case.approx_ref_path.read_text().splitlines())
    if ref_lines == expected_lines:
        return None

    return AdvisoryDiff(
        case=case,
        label=f"{case.approx_ref_path.relative_to(REPO_ROOT)} vs {case.name}",
        diff=_build_diff(
            ref_lines,
            expected_lines,
            fromfile=str(case.approx_ref_path.relative_to(REPO_ROOT)),
            tofile=output_label,
        ),
    )


def _build_diff(
    before_lines: tuple[str, ...],
    after_lines: tuple[str, ...],
    *,
    fromfile: str,
    tofile: str,
) -> str:
    return "".join(
        unified_diff(
            [line + "\n" for line in before_lines],
            [line + "\n" for line in after_lines],
            fromfile=fromfile,
            tofile=tofile,
        )
    )


def _build_tree_diff(*, expected_root: Path, actual_root: Path) -> str | None:
    expected_files = {
        path.relative_to(expected_root): path
        for path in expected_root.rglob("*")
        if path.is_file()
    }
    actual_files = {
        path.relative_to(actual_root): path
        for path in actual_root.rglob("*")
        if path.is_file()
    }

    lines: list[str] = []

    missing = sorted(expected_files.keys() - actual_files.keys())
    if missing:
        lines.append("Missing emitted files:")
        for rel_path in missing:
            lines.append(f"- {rel_path.as_posix()}")

    unexpected = sorted(actual_files.keys() - expected_files.keys())
    if unexpected:
        if lines:
            lines.append("")
        lines.append("Unexpected emitted files:")
        for rel_path in unexpected:
            lines.append(f"- {rel_path.as_posix()}")

    common = sorted(expected_files.keys() & actual_files.keys())
    for rel_path in common:
        expected_lines = tuple(expected_files[rel_path].read_text().splitlines())
        actual_lines = tuple(actual_files[rel_path].read_text().splitlines())
        if expected_lines == actual_lines:
            continue
        if lines:
            lines.append("")
        rel_label = rel_path.as_posix()
        lines.append(
            _build_diff(
                expected_lines,
                actual_lines,
                fromfile=f"expected://{rel_label}",
                tofile=f"emitted://{rel_label}",
            ).rstrip("\n")
        )

    return "\n".join(lines) if lines else None


def format_report(report: VerificationReport) -> str:
    lines: list[str] = []

    if report.manifest_errors:
        lines.append("Manifest errors:")
        for error in report.manifest_errors:
            lines.append(f"- {error}")
        lines.append("")

    lines.append("Active case results:")
    if report.active_results:
        for result in report.active_results:
            case_path = _display_path(result.case.manifest_path)
            lines.append(
                f"- {result.outcome} {case_path} :: {result.case.name} :: {result.detail}"
            )
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Planned cases:")
    if report.planned_cases:
        for case in report.planned_cases:
            case_path = _display_path(case.manifest_path)
            lines.append(f"- PLANNED {case_path} :: {case.name}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Advisory ref diffs:")
    if report.advisory_diffs:
        for advisory in report.advisory_diffs:
            lines.append(f"- {advisory.label}")
            lines.append(advisory.diff.rstrip("\n"))
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Surfaced inconsistencies:")
    if report.surfaced_inconsistencies:
        for inconsistency in report.surfaced_inconsistencies:
            lines.append(f"- {inconsistency}")
    else:
        # Keep the reporting lane explicit even when this run settles cleanly.
        lines.append("- None surfaced during this run.")

    return "\n".join(lines)


def _require_str(raw: dict[str, Any], key: str, *, case_index: int | None = None) -> str:
    value = raw.get(key)
    if not isinstance(value, str):
        location = key if case_index is None else f"cases[{case_index}].{key}"
        raise ManifestError(f"{location} must be a string.")
    return value


def _require_choice(
    raw: dict[str, Any],
    key: str,
    allowed: set[str],
    *,
    case_index: int | None = None,
) -> str:
    value = _require_str(raw, key, case_index=case_index)
    if value not in allowed:
        location = key if case_index is None else f"cases[{case_index}].{key}"
        allowed_str = ", ".join(sorted(repr(item) for item in allowed))
        raise ManifestError(f"{location} must be one of {allowed_str}, got {value!r}.")
    return value


def _require_string_list(
    raw: dict[str, Any], key: str, *, case_index: int | None = None
) -> tuple[str, ...]:
    value = raw.get(key)
    location = key if case_index is None else f"cases[{case_index}].{key}"
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ManifestError(f"{location} must be a list of strings.")
    return tuple(value)


def _format_case_failure(exc: Exception) -> str:
    if isinstance(exc, PyPromptError):
        return f"{type(exc).__name__} [{exc.code}]:\n{exc}"
    return f"{type(exc).__name__}: {exc}"


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
