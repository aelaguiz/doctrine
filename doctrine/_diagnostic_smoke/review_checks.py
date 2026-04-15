from __future__ import annotations

import signal
from pathlib import Path
from tempfile import TemporaryDirectory

from doctrine.compiler import compile_prompt
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown

from doctrine._diagnostic_smoke.fixtures import (
    SmokeFailure,
    _expect,
    _final_output_review_prose_source,
    _final_output_review_split_json_source,
    _final_output_review_split_prose_source,
    _review_exact_gate_stress_source,
    _review_invalid_guarded_match_head_source,
    _review_smoke_source,
    _write_prompt,
)


def run_review_checks() -> None:
    _check_review_driven_final_output_renders()
    _check_review_driven_split_final_output_renders()
    _check_review_driven_split_json_final_output_renders()
    _check_review_split_control_ready_final_output_renders()
    _check_review_split_partial_final_output_renders()
    _check_review_illegal_statement_placement_has_specific_code()
    _check_review_invalid_guarded_match_head_has_specific_code()
    _check_review_multiple_currentness_has_specific_code()
    _check_review_outcome_not_total_has_specific_code()
    _check_review_next_owner_alignment_has_specific_code()
    _check_review_failure_detail_guard_has_specific_code()
    _check_final_output_review_fields_require_review_agent()
    _check_final_output_review_fields_reject_review_carrier()
    _check_review_semantic_addressability_renders()
    _check_review_exact_contract_gate_modes_do_not_blow_up()


def _check_review_driven_final_output_renders() -> None:
    source = _final_output_review_prose_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        compiled = compile_prompt(prompt, "ReviewFinalOutputAgent")
        _expect(compiled.final_output is not None, "expected compiled final_output metadata")
        _expect(compiled.final_output.format_mode == "prose", str(compiled.final_output))
        rendered = render_markdown(compiled)
        _expect("## Final Output" in rendered, rendered)
        _expect("#### Trust Surface" in rendered, rendered)
        _expect("- Current Artifact" in rendered, rendered)
        _expect("Show this only when verdict is changes requested." in rendered, rendered)
        _expect("## Outputs" not in rendered, rendered)


def _check_review_driven_split_final_output_renders() -> None:
    source = _final_output_review_split_prose_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        compiled = compile_prompt(prompt, "SplitReviewFinalOutputAgent")
        _expect(compiled.final_output is not None, "expected compiled final_output metadata")
        _expect(compiled.final_output.format_mode == "prose", str(compiled.final_output))
        rendered = render_markdown(compiled)
        outputs_block = rendered.split("## Outputs", 1)[1].split("## Final Output", 1)[0]
        final_output_block = rendered.split("## Final Output", 1)[1]
        _expect("### Draft Review Comment" in outputs_block, rendered)
        _expect("### Draft Review Decision" not in outputs_block, rendered)
        _expect("### Draft Review Decision" in final_output_block, rendered)
        _expect("Show this only when verdict is changes requested." in final_output_block, rendered)
        _expect("Keep the control summary aligned with Current Artifact." in final_output_block, rendered)


def _check_review_driven_split_json_final_output_renders() -> None:
    source = _final_output_review_split_json_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        compiled = compile_prompt(prompt, "ReviewSplitJsonFinalOutputAgent")
        _expect(compiled.final_output is not None, "expected compiled final_output metadata")
        _expect(compiled.final_output.format_mode == "json_object", str(compiled.final_output))
        rendered = render_markdown(compiled)
        outputs_block = rendered.split("## Outputs", 1)[1].split("## Final Output", 1)[0]
        final_output_block = rendered.split("## Final Output", 1)[1]
        _expect("### Acceptance Review Comment" in outputs_block, rendered)
        _expect("### Acceptance Control Final Response" not in outputs_block, rendered)
        _expect("| Schema | Acceptance Control Schema |" in final_output_block, rendered)
        _expect("Keep `current_artifact` aligned with Current Artifact." in final_output_block, rendered)
        _expect("Use `route` value `revise` only when Outline Complete fails." in final_output_block, rendered)
        _expect("Show this only when verdict is changes requested." in final_output_block, rendered)


def _repo_example_prompt_path(*parts: str) -> Path:
    return Path(__file__).resolve().parents[2] / "examples" / Path(*parts)


def _check_review_split_control_ready_final_output_renders() -> None:
    prompt_path = _repo_example_prompt_path(
        "105_review_split_final_output_json_object_control_ready",
        "prompts",
        "AGENTS.prompt",
    )
    prompt = parse_file(prompt_path)
    rendered = render_markdown(compile_prompt(prompt, "AcceptanceReviewSplitControlReadyDemo"))
    final_output_block = rendered.split("## Final Output", 1)[1]
    _expect("#### Review Response Semantics" in final_output_block, rendered)
    _expect("| Verdict | `verdict` |" in final_output_block, rendered)
    _expect(
        "This final response is control-ready. A host may read it as the review outcome."
        in final_output_block,
        rendered,
    )


def _check_review_split_partial_final_output_renders() -> None:
    prompt_path = _repo_example_prompt_path(
        "106_review_split_final_output_json_object_partial",
        "prompts",
        "AGENTS.prompt",
    )
    prompt = parse_file(prompt_path)
    rendered = render_markdown(compile_prompt(prompt, "AcceptanceReviewSplitPartialDemo"))
    final_output_block = rendered.split("## Final Output", 1)[1]
    _expect("#### Review Response Semantics" in final_output_block, rendered)
    _expect("| Current Artifact | `current_artifact` |" in final_output_block, rendered)
    _expect("| Next Owner | `next_owner` |" in final_output_block, rendered)
    _expect(
        "This final response is not control-ready. Read the review carrier for the full review outcome."
        in final_output_block,
        rendered,
    )


def _check_review_illegal_statement_placement_has_specific_code() -> None:
    source = _review_smoke_source(
        on_accept_body="""
        block "Do not block inside on_accept." when DraftSpec.needs_follow_up
""",
    )
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        try:
            parse_file(prompt_path)
        except Exception as exc:
            _expect(type(exc).__name__ == "ParseError", f"expected ParseError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E471", f"expected E471, got {getattr(exc, 'code', None)}")
            _expect("Illegal statement placement" in str(exc), str(exc))
            return
        raise SmokeFailure("expected parse failure for illegal review statement placement, but parsing succeeded")


def _check_review_invalid_guarded_match_head_has_specific_code() -> None:
    source = _review_invalid_guarded_match_head_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        try:
            parse_file(prompt_path)
        except Exception as exc:
            _expect(type(exc).__name__ == "ParseError", f"expected ParseError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E472", f"expected E472, got {getattr(exc, 'code', None)}")
            _expect("Invalid guarded match head" in str(exc), str(exc))
            return
        raise SmokeFailure("expected parse failure for invalid guarded review match head, but parsing succeeded")


def _check_review_multiple_currentness_has_specific_code() -> None:
    source = _review_smoke_source(
        on_accept_body="""
        current none
        current none
        route "Accepted draft goes to AcceptOwner." -> AcceptOwner
""",
    )
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "ReviewDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E486", f"expected E486, got {getattr(exc, 'code', None)}")
            _expect("more than one currentness result" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for duplicate review currentness, but compilation succeeded")


def _check_review_outcome_not_total_has_specific_code() -> None:
    source = _review_smoke_source(
        on_accept_body="""
        when DraftSpec.needs_follow_up:
            current none
            route "Accepted draft goes to AcceptOwner." -> AcceptOwner
""",
    )
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "ReviewDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E484", f"expected E484, got {getattr(exc, 'code', None)}")
            _expect("not total" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for non-total review outcome, but compilation succeeded")


def _check_review_next_owner_alignment_has_specific_code() -> None:
    source = _review_smoke_source(
        on_accept_body="""
        current none
        route "Accepted draft goes to AcceptOwner." -> AcceptOwner
""",
        next_owner_text='"Name the next owner without naming the routed owner."',
    )
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "ReviewDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E496", f"expected E496, got {getattr(exc, 'code', None)}")
            _expect("next owner" in str(exc).lower(), str(exc))
            return
        raise SmokeFailure("expected compile failure for review next_owner mismatch, but compilation succeeded")


def _check_review_failure_detail_guard_has_specific_code() -> None:
    source = _review_smoke_source(
        on_accept_body="""
        current none
        route "Accepted draft goes to AcceptOwner." -> AcceptOwner
""",
        failure_detail_guard="verdict == ReviewVerdict.accept",
    )
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "ReviewDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E499", f"expected E499, got {getattr(exc, 'code', None)}")
            _expect("conditional" in str(exc).lower(), str(exc))
            return
        raise SmokeFailure("expected compile failure for review failure-detail guard mismatch, but compilation succeeded")


def _check_final_output_review_fields_require_review_agent() -> None:
    prompt_path = _repo_example_prompt_path(
        "106_review_split_final_output_json_object_partial",
        "prompts",
        "AGENTS.prompt",
    )
    prompt = parse_file(prompt_path)
    try:
        compile_prompt(prompt, "InvalidFinalOutputReviewFieldsWithoutReviewDemo")
    except Exception as exc:
        _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
        _expect(getattr(exc, "code", None) == "E500", f"expected E500, got {getattr(exc, 'code', None)}")
        _expect("review_fields" in str(exc), str(exc))
        _expect("review-driven agent" in str(exc), str(exc))
        return
    raise SmokeFailure(
        "expected compile failure when final_output.review_fields appear on a non-review agent, but compilation succeeded"
    )


def _check_final_output_review_fields_reject_review_carrier() -> None:
    prompt_path = _repo_example_prompt_path(
        "106_review_split_final_output_json_object_partial",
        "prompts",
        "AGENTS.prompt",
    )
    prompt = parse_file(prompt_path)
    try:
        compile_prompt(prompt, "InvalidFinalOutputReviewFieldsOnCarrierDemo")
    except Exception as exc:
        _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
        _expect(getattr(exc, "code", None) == "E500", f"expected E500, got {getattr(exc, 'code', None)}")
        _expect("review_fields" in str(exc), str(exc))
        _expect("split final responses" in str(exc), str(exc))
        return
    raise SmokeFailure(
        "expected compile failure when final_output.review_fields appear on the review carrier, but compilation succeeded"
    )


def _check_review_semantic_addressability_renders() -> None:
    source = _review_smoke_source(
        on_accept_body="""
        current none
        route "Accepted draft goes to AcceptOwner." -> AcceptOwner
""",
    )
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "ReviewDemo"))
        _expect("{{fields." not in rendered, rendered)
        _expect("{{contract." not in rendered, rendered)
        _expect("Use Completeness before you route Next Owner." in rendered, rendered)
        _expect("compare Reviewed Artifact with Completeness." in rendered, rendered)


def _check_review_exact_contract_gate_modes_do_not_blow_up() -> None:
    source = _review_exact_gate_stress_source(gate_count=17)
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)

        class _Timeout(RuntimeError):
            pass

        def _handle_timeout(_signum, _frame):
            raise _Timeout()

        previous = signal.signal(signal.SIGALRM, _handle_timeout)
        try:
            signal.alarm(5)
            compile_prompt(prompt, "ExactGateReviewDemo")
            signal.alarm(0)
        except _Timeout as exc:
            raise SmokeFailure(
                "expected exact-gate multi-mode review compilation to finish without "
                "review contract branch blow-up"
            ) from exc
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous)
