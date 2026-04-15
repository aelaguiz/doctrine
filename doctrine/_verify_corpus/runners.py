from __future__ import annotations

import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from doctrine.compiler import CompilationSession, compile_prompt
from doctrine.diagnostics import DoctrineError, EmitError
from doctrine._compiler.support import default_worker_count
from doctrine.emit_common import load_emit_targets
from doctrine.emit_docs import emit_target
from doctrine.emit_flow import emit_target_flow
from doctrine.emit_skill import emit_target_skill
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown, render_readable_block

from doctrine._verify_corpus.diff import (
    _build_contract_ref_diff,
    _build_diff,
    _build_ref_has_flow_artifacts,
    _build_ref_has_svg_artifacts,
    _build_tree_diff,
)
from doctrine._verify_corpus.manifest import (
    CaseSpec,
    ManifestError,
    REPO_ROOT,
    _display_path,
    _load_manifest,
    _resolve_manifest_paths,
)
from doctrine._verify_corpus.report import (
    CaseResult,
    VerificationError,
    VerificationReport,
    _format_case_failure,
)

BUILD_CONTRACT_REF_DIR = "build_ref"


@dataclass(slots=True, frozen=True)
class CompileCaseOutcome:
    result: CaseResult
    ref_diff: object | None = None


class _CompilationSessionCache:
    def __init__(self) -> None:
        self._sessions: dict[Path, CompilationSession] = {}
        self._errors: dict[Path, Exception] = {}
        self._loading: dict[Path, threading.Event] = {}
        self._lock = threading.Lock()

    def get(self, prompt_path: Path) -> CompilationSession:
        with self._lock:
            cached_session = self._sessions.get(prompt_path)
            if cached_session is not None:
                return cached_session

            cached_error = self._errors.get(prompt_path)
            if cached_error is not None:
                if isinstance(cached_error, DoctrineError):
                    raise _clone_doctrine_error(cached_error)
                raise cached_error

            ready = self._loading.get(prompt_path)
            if ready is None:
                ready = threading.Event()
                self._loading[prompt_path] = ready
                is_loader = True
            else:
                is_loader = False

        if not is_loader:
            ready.wait()
            with self._lock:
                cached_session = self._sessions.get(prompt_path)
                if cached_session is not None:
                    return cached_session
                cached_error = self._errors.get(prompt_path)
            if cached_error is None:
                raise RuntimeError(
                    f"Compilation session build finished without a result: {prompt_path}"
                )
            if isinstance(cached_error, DoctrineError):
                raise _clone_doctrine_error(cached_error)
            raise cached_error

        try:
            session = CompilationSession(parse_file(prompt_path))
        except Exception as exc:
            with self._lock:
                if isinstance(exc, DoctrineError):
                    self._errors[prompt_path] = _clone_doctrine_error(exc)
                else:
                    self._errors[prompt_path] = exc
            raise
        else:
            with self._lock:
                self._sessions[prompt_path] = session
            return session
        finally:
            with self._lock:
                ready = self._loading.pop(prompt_path, None)
            if ready is not None:
                ready.set()


def verify_corpus(manifest_args: list[str] | None = None) -> VerificationReport:
    manifest_errors: list[str] = []
    case_results: list[CaseResult] = []
    ref_diffs: list[object] = []
    surfaced_inconsistencies: list[str] = []

    try:
        manifests = _resolve_manifest_paths(manifest_args)
    except ManifestError as exc:
        return VerificationReport(
            manifest_errors=[str(exc)],
            case_results=case_results,
            ref_diffs=ref_diffs,
            surfaced_inconsistencies=surfaced_inconsistencies,
        )

    cases: list[CaseSpec] = []
    for manifest_path in manifests:
        try:
            cases.extend(_load_manifest(manifest_path))
        except ManifestError as exc:
            manifest_errors.append(f"{_display_path(manifest_path)}: {exc}")

    ordered_results: list[CaseResult | None] = [None] * len(cases)
    ordered_ref_diffs: list[object | None] = [None] * len(cases)

    compile_case_indexes = [
        index
        for index, case in enumerate(cases)
        if case.kind in {"render_contract", "render_declaration", "compile_fail"}
    ]
    if compile_case_indexes:
        session_cache = _CompilationSessionCache()
        with ThreadPoolExecutor(
            max_workers=default_worker_count(len(compile_case_indexes))
        ) as executor:
            futures = {
                executor.submit(_run_compile_case, cases[index], session_cache): index
                for index in compile_case_indexes
            }
            for future in as_completed(futures):
                index = futures[future]
                case = cases[index]
                try:
                    outcome = future.result()
                except Exception as exc:
                    ordered_results[index] = CaseResult(
                        case=case,
                        result="FAIL",
                        detail=_format_case_failure(exc),
                    )
                else:
                    ordered_results[index] = outcome.result
                    ordered_ref_diffs[index] = outcome.ref_diff

    for index, case in enumerate(cases):
        if ordered_results[index] is not None:
            continue
        try:
            if case.kind == "render_contract":
                outcome = _run_render_contract(case)
                ordered_results[index] = outcome.result
                ordered_ref_diffs[index] = outcome.ref_diff
            elif case.kind == "render_declaration":
                outcome = _run_render_declaration(case)
                ordered_results[index] = outcome.result
                ordered_ref_diffs[index] = outcome.ref_diff
            elif case.kind == "build_contract":
                ordered_results[index] = _run_build_contract(case)
            elif case.kind == "parse_fail":
                ordered_results[index] = _run_parse_fail(case)
            elif case.kind == "compile_fail":
                ordered_results[index] = _run_compile_fail(case)
            else:
                raise ManifestError(f"Unsupported case kind {case.kind!r}.")
        except Exception as exc:
            ordered_results[index] = CaseResult(
                case=case,
                result="FAIL",
                detail=_format_case_failure(exc),
            )

    case_results = [result for result in ordered_results if result is not None]
    ref_diffs = [ref_diff for ref_diff in ordered_ref_diffs if ref_diff is not None]

    return VerificationReport(
        manifest_errors=manifest_errors,
        case_results=case_results,
        ref_diffs=ref_diffs,
        surfaced_inconsistencies=surfaced_inconsistencies,
    )


def _clone_doctrine_error(error: DoctrineError) -> DoctrineError:
    return type(error)(diagnostic=error.diagnostic)


def _run_render_contract(
    case: CaseSpec,
    *,
    session: CompilationSession | None = None,
) -> CompileCaseOutcome:
    if session is None:
        prompt_file = parse_file(case.prompt_path)
        compiled = compile_prompt(prompt_file, case.agent or "")
    else:
        compiled = session.compile_agent(case.agent or "")
    rendered = render_markdown(compiled)
    ref_diff = _build_contract_ref_diff(
        case,
        expected_lines=tuple(rendered.splitlines()),
        output_label=f"rendered://{case.agent}",
    )

    actual_lines = tuple(rendered.splitlines())
    if actual_lines != case.expected_lines:
        diff = _build_diff(
            case.expected_lines,
            actual_lines,
            fromfile=f"expected://{case.name}",
            tofile=f"rendered://{case.agent}",
        )
        raise VerificationError(
            "Rendered output did not match the prompt-derived contract.\n" + diff
        )

    return CompileCaseOutcome(
        result=CaseResult(
            case=case,
            result="PASS",
            detail="render matched exact_lines contract",
        ),
        ref_diff=ref_diff,
    )


def _run_render_declaration(
    case: CaseSpec,
    *,
    session: CompilationSession | None = None,
) -> CompileCaseOutcome:
    if session is None:
        session = CompilationSession(parse_file(case.prompt_path))
    compiled = session.compile_readable_declaration(
        case.declaration_kind or "", case.declaration_name or ""
    )
    rendered = render_readable_block(compiled, depth=2)
    ref_diff = _build_contract_ref_diff(
        case,
        expected_lines=tuple(rendered.splitlines()),
        output_label=f"rendered://{case.declaration_kind}:{case.declaration_name}",
    )

    actual_lines = tuple(rendered.splitlines())
    if actual_lines != case.expected_lines:
        diff = _build_diff(
            case.expected_lines,
            actual_lines,
            fromfile=f"expected://{case.name}",
            tofile=f"rendered://{case.declaration_kind}:{case.declaration_name}",
        )
        raise VerificationError(
            "Rendered declaration output did not match the prompt-derived contract.\n" + diff
        )

    return CompileCaseOutcome(
        result=CaseResult(
            case=case,
            result="PASS",
            detail="declaration render matched exact_lines contract",
        ),
        ref_diff=ref_diff,
    )


def _run_parse_fail(case: CaseSpec) -> CaseResult:
    try:
        parse_file(case.prompt_path)
    except Exception as exc:
        _assert_expected_exception(case, exc)
        return CaseResult(case=case, result="PASS", detail="parse failed as expected")

    raise VerificationError("Expected parse to fail, but it succeeded.")


def _run_build_contract(
    case: CaseSpec,
    *,
    load_emit_targets_fn=load_emit_targets,
    emit_target_fn=emit_target,
    emit_target_flow_fn=emit_target_flow,
    emit_target_skill_fn=emit_target_skill,
) -> CaseResult:
    try:
        targets = load_emit_targets_fn(start_dir=REPO_ROOT)
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
            _emit_build_contract_target(
                target,
                expected_root=expected_root,
                actual_root=actual_root,
                emit_target_fn=emit_target_fn,
                emit_target_flow_fn=emit_target_flow_fn,
                emit_target_skill_fn=emit_target_skill_fn,
            )
        except DoctrineError as exc:
            raise VerificationError(str(exc)) from exc

        diff = _build_tree_diff(expected_root=expected_root, actual_root=actual_root)
        if diff is not None:
            raise VerificationError(
                "Emitted build tree did not match the checked-in build contract.\n" + diff
            )

    return CaseResult(
        case=case,
        result="PASS",
        detail="build matched checked-in tree",
    )


def _emit_build_contract_target(
    target,
    *,
    expected_root: Path,
    actual_root: Path,
    emit_target_fn,
    emit_target_flow_fn,
    emit_target_skill_fn,
) -> None:
    if target.entrypoint.name == "SKILL.prompt":
        emit_target_skill_fn(target, output_dir_override=actual_root)
        return

    # Runtime build-contract proof always rides the canonical emit_docs +
    # emit_flow path, including imported runtime-package trees.
    emit_target_fn(target, output_dir_override=actual_root)
    if _build_ref_has_flow_artifacts(expected_root):
        emit_target_flow_fn(
            target,
            output_dir_override=actual_root,
            include_svg=_build_ref_has_svg_artifacts(expected_root),
        )


def _run_compile_fail(
    case: CaseSpec,
    *,
    session: CompilationSession | None = None,
    session_cache: _CompilationSessionCache | None = None,
) -> CaseResult:
    try:
        active_session: CompilationSession
        if session_cache is not None:
            active_session = session_cache.get(case.prompt_path)
        elif session is not None:
            active_session = session
        else:
            prompt_file = parse_file(case.prompt_path)
            active_session = CompilationSession(prompt_file)

        if case.agent is not None:
            active_session.compile_agent(case.agent)
        elif active_session.root_unit.skill_packages_by_name:
            active_session.compile_skill_package()
        else:
            raise VerificationError(
                "compile_fail case omitted `agent`, but the prompt does not define a skill package."
            )
    except Exception as exc:
        _assert_expected_exception(case, exc)
        return CaseResult(case=case, result="PASS", detail="compile failed as expected")

    raise VerificationError("Expected compile to fail, but it succeeded.")


def _run_compile_case(
    case: CaseSpec,
    session_cache: _CompilationSessionCache,
) -> CompileCaseOutcome:
    if case.kind == "render_contract":
        return _run_render_contract(case, session=session_cache.get(case.prompt_path))
    if case.kind == "render_declaration":
        return _run_render_declaration(case, session=session_cache.get(case.prompt_path))
    if case.kind == "compile_fail":
        return CompileCaseOutcome(
            result=_run_compile_fail(case, session_cache=session_cache)
        )
    raise ManifestError(f"Unsupported parallel compile case kind {case.kind!r}.")


def _assert_expected_exception(case: CaseSpec, exc: Exception) -> None:
    actual_type = type(exc).__name__
    if actual_type != case.exception_type:
        raise VerificationError(f"Expected {case.exception_type}, got {actual_type}: {exc}")

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
