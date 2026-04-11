from __future__ import annotations

import contextlib
import io
import json
import textwrap
from pathlib import Path
from tempfile import TemporaryDirectory

from doctrine.compiler import compile_prompt, extract_target_flow_graph
from doctrine.diagnostics import diagnostic_to_dict
from doctrine.emit_docs import main as emit_docs_main
from doctrine.emit_flow import main as emit_flow_main
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class SmokeFailure(RuntimeError):
    """Raised when the direct diagnostic smoke checks fail."""


def main() -> int:
    _check_transform_errors_surface_as_parse_errors()
    _check_compile_missing_role_has_specific_code()
    _check_review_illegal_statement_placement_has_specific_code()
    _check_review_invalid_guarded_match_head_has_specific_code()
    _check_review_multiple_currentness_has_specific_code()
    _check_review_outcome_not_total_has_specific_code()
    _check_review_next_owner_alignment_has_specific_code()
    _check_review_failure_detail_guard_has_specific_code()
    _check_review_semantic_addressability_renders()
    _check_emit_docs_handles_invalid_toml_without_traceback()
    _check_emit_docs_uses_specific_code_for_missing_entrypoint()
    _check_emit_docs_uses_entrypoint_stem_for_output_name()
    _check_flow_graph_extracts_routes_and_shared_io()
    _check_emit_flow_uses_entrypoint_stem_for_output_name()
    _check_diagnostic_to_dict_is_json_safe()
    print("diagnostic smoke checks passed")
    return 0


def _check_transform_errors_surface_as_parse_errors() -> None:
    source = """workflow Shared: "Shared"
    "hi"

agent Demo:
    role: "hi"
    override workflow: Shared
        "body"
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        try:
            parse_file(prompt_path)
        except Exception as exc:
            _expect(type(exc).__name__ == "ParseError", f"expected ParseError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E105", f"expected E105, got {getattr(exc, 'code', None)}")
            rendered = str(exc)
            _expect("Invalid authored slot body" in rendered, rendered)
            _expect("override workflow" in rendered, rendered)
            return
        raise SmokeFailure("expected transformer-stage parse failure, but parsing succeeded")


def _check_compile_missing_role_has_specific_code() -> None:
    source = """agent MissingRole:
    workflow: "Instructions"
        "No role here."
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "MissingRole")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E205", f"expected E205, got {getattr(exc, 'code', None)}")
            _expect("missing role field" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for missing role field, but compilation succeeded")


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
        route "Accepted draft returns to AcceptOwner." -> AcceptOwner
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
            route "Accepted draft returns to AcceptOwner." -> AcceptOwner
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
        route "Accepted draft returns to AcceptOwner." -> AcceptOwner
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
        route "Accepted draft returns to AcceptOwner." -> AcceptOwner
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


def _check_review_semantic_addressability_renders() -> None:
    source = _review_smoke_source(
        on_accept_body="""
        current none
        route "Accepted draft returns to AcceptOwner." -> AcceptOwner
""",
    )
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "ReviewDemo"))
        _expect("{{fields." not in rendered, rendered)
        _expect("{{contract." not in rendered, rendered)
        _expect("Use Completeness before you route Next Owner." in rendered, rendered)
        _expect("compare Reviewed Artifact against Completeness." in rendered, rendered)


def _check_emit_docs_handles_invalid_toml_without_traceback() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        pyproject = root / "pyproject.toml"
        pyproject.write_text("[tool.doctrine.emit\n")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_docs_main(["--pyproject", str(pyproject), "--target", "x"])
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E506 emit error: Invalid emit config TOML" in output, output)
        _expect("Traceback" not in output, output)


def _check_emit_docs_uses_specific_code_for_missing_entrypoint() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "bad"
entrypoint = "prompts/OTHER.prompt"
output_dir = "build"
"""
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_docs_main(["--pyproject", str(pyproject), "--target", "bad"])
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E512 emit error" in output, output)
        _expect("entrypoint does not exist" in output, output)


def _check_emit_docs_uses_entrypoint_stem_for_output_name() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "demo" / "agents" / "demo_agent"
        prompts.mkdir(parents=True)
        agents_prompt = prompts / "AGENTS.prompt"
        soul_prompt = prompts / "SOUL.prompt"
        agents_prompt.write_text(
            """agent DemoAgent:
    role: "You are Demo Agent."
"""
        )
        soul_prompt.write_text(
            """agent DemoAgent:
    role: "You are Demo Agent. Let this background shape your tone."
"""
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "demo_agents"
entrypoint = "prompts/demo/agents/demo_agent/AGENTS.prompt"
output_dir = "build"

[[tool.doctrine.emit.targets]]
name = "demo_soul"
entrypoint = "prompts/demo/agents/demo_agent/SOUL.prompt"
output_dir = "build"
"""
        )
        exit_code = emit_docs_main(
            [
                "--pyproject",
                str(pyproject),
                "--target",
                "demo_agents",
                "--target",
                "demo_soul",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        agents_path = root / "build" / "demo" / "agents" / "demo_agent" / "AGENTS.md"
        soul_path = root / "build" / "demo" / "agents" / "demo_agent" / "SOUL.md"
        _expect(agents_path.is_file(), f"missing emitted AGENTS.md: {agents_path}")
        _expect(soul_path.is_file(), f"missing emitted SOUL.md: {soul_path}")


def _check_flow_graph_extracts_routes_and_shared_io() -> None:
    source = """input SharedInput: "Shared Input"
    source: Prompt
    shape: JsonObject
    requirement: Required

output DurableArtifact: "Durable Artifact"
    target: File
        path: "artifact.md"
    shape: MarkdownDocument
    requirement: Required

output CarrierComment: "Carrier Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the current artifact."

    trust_surface:
        current_artifact

agent RoutingOwner:
    role: "Own reroutes."
    workflow: "Routing"
        "Take the issue back."

agent WorkerA:
    role: "Produce the durable artifact."
    workflow: "Worker A"
        routing: "Routing"
            route "Escalate to RoutingOwner." -> RoutingOwner
        law:
            active when SharedInput.ready
            current artifact DurableArtifact via CarrierComment.current_artifact
            route "Return to RoutingOwner." -> RoutingOwner
    inputs: "Inputs"
        SharedInput
    outputs: "Outputs"
        DurableArtifact
        CarrierComment

agent WorkerB:
    role: "Read the same shared input."
    workflow: "Worker B"
        "Observe the shared handoff."
    inputs: "Inputs"
        SharedInput
    outputs: "Outputs"
        CarrierComment
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        graph = extract_target_flow_graph(prompt, ("RoutingOwner", "WorkerA", "WorkerB"))
        _expect(len(graph.inputs) == 1, f"expected 1 input node, got {len(graph.inputs)}")
        _expect(len(graph.outputs) == 2, f"expected 2 output nodes, got {len(graph.outputs)}")

        edges = {(edge.kind, edge.source_name, edge.target_name, edge.label) for edge in graph.edges}
        _expect(
            ("authored_route", "WorkerA", "RoutingOwner", "Escalate to RoutingOwner.") in edges,
            f"missing authored route edge: {edges}",
        )
        _expect(
            ("law_route", "WorkerA", "RoutingOwner", "Return to RoutingOwner.") in edges,
            f"missing workflow-law route edge: {edges}",
        )
        _expect(
            ("consume", "SharedInput", "WorkerA", "consumes") in edges,
            f"missing shared input consume edge for WorkerA: {edges}",
        )
        _expect(
            ("consume", "SharedInput", "WorkerB", "consumes") in edges,
            f"missing shared input consume edge for WorkerB: {edges}",
        )

        carrier_comment = next(
            (node for node in graph.outputs if node.name == "CarrierComment"),
            None,
        )
        _expect(carrier_comment is not None, "missing CarrierComment output node")
        _expect(
            carrier_comment is not None
            and "Current Artifact" in carrier_comment.trust_surface
            and "Carries current for Durable Artifact" in carrier_comment.notes,
            f"missing currentness carrier note on CarrierComment: {carrier_comment}",
        )


def _check_emit_flow_uses_entrypoint_stem_for_output_name() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "demo" / "agents" / "demo_agent"
        prompts.mkdir(parents=True)
        agents_prompt = prompts / "AGENTS.prompt"
        soul_prompt = prompts / "SOUL.prompt"
        source = """input SharedInput: "Shared Input"
    source: Prompt
    shape: JsonObject
    requirement: Required

output SharedComment: "Shared Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

agent DemoAgent:
    role: "Own the demo flow."
    workflow: "Demo Flow"
        "Read the shared input and leave one comment."
    inputs: "Inputs"
        SharedInput
    outputs: "Outputs"
        SharedComment
"""
        agents_prompt.write_text(source)
        soul_prompt.write_text(source)
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "demo_agents"
entrypoint = "prompts/demo/agents/demo_agent/AGENTS.prompt"
output_dir = "build"

[[tool.doctrine.emit.targets]]
name = "demo_soul"
entrypoint = "prompts/demo/agents/demo_agent/SOUL.prompt"
output_dir = "build"
"""
        )
        exit_code = emit_flow_main(
            [
                "--pyproject",
                str(pyproject),
                "--target",
                "demo_agents",
                "--target",
                "demo_soul",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        agents_d2 = root / "build" / "demo" / "agents" / "demo_agent" / "AGENTS.flow.d2"
        agents_svg = root / "build" / "demo" / "agents" / "demo_agent" / "AGENTS.flow.svg"
        soul_d2 = root / "build" / "demo" / "agents" / "demo_agent" / "SOUL.flow.d2"
        soul_svg = root / "build" / "demo" / "agents" / "demo_agent" / "SOUL.flow.svg"
        _expect(agents_d2.is_file(), f"missing emitted AGENTS.flow.d2: {agents_d2}")
        _expect(agents_svg.is_file(), f"missing emitted AGENTS.flow.svg: {agents_svg}")
        _expect(soul_d2.is_file(), f"missing emitted SOUL.flow.d2: {soul_d2}")
        _expect(soul_svg.is_file(), f"missing emitted SOUL.flow.svg: {soul_svg}")


def _check_diagnostic_to_dict_is_json_safe() -> None:
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, 'agent Broken\n    role: "x"\n')
        try:
            parse_file(prompt_path)
        except Exception as exc:
            payload = diagnostic_to_dict(exc)
            json.dumps(payload)
            return
        raise SmokeFailure("expected parse failure for JSON-safety check, but parsing succeeded")


def _write_prompt(tmp_dir: str, source: str) -> Path:
    root = Path(tmp_dir)
    prompts = root / "prompts"
    prompts.mkdir()
    prompt_path = prompts / "AGENTS.prompt"
    prompt_path.write_text(source)
    return prompt_path


def _review_smoke_source(
    *,
    on_accept_body: str,
    next_owner_text: str = '"Name the next owner, including {{AcceptOwner}} when the draft is accepted and {{RejectOwner}} when the draft is rejected."',
    failure_detail_guard: str = "fields.verdict == ReviewVerdict.changes_requested",
) -> str:
    return f"""input DraftSpec: "Draft Spec"
    source: File
        path: "draft.md"
    shape: MarkdownDocument
    requirement: Required

workflow DraftReviewContract: "Draft Review Contract"
    completeness: "Completeness"
        "Confirm the draft covers the required sections."

agent AcceptOwner:
    role: "Own accepted drafts."
    workflow: "Accept"
        "Handle the accepted draft."

agent RejectOwner:
    role: "Own rejected drafts."
    workflow: "Reject"
        "Handle the rejected draft."

output DraftReviewComment: "Draft Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    verdict: "Verdict"
        "Say whether the review accepted the draft or requested changes."

    reviewed_artifact: "Reviewed Artifact"
        "Name the reviewed artifact this review judged."

    analysis_performed: "Analysis Performed"
        "Summarize the review analysis that led to the verdict and compare {{{{fields.reviewed_artifact}}}} against {{{{contract.completeness}}}}."

    output_contents_that_matter: "Output Contents That Matter"
        "Summarize the parts of the draft the next owner must read first."

    next_owner: "Next Owner"
        {next_owner_text}

    failure_detail: "Failure Detail" when {failure_detail_guard}:
        failing_gates: "Failing Gates"
            "Name the failing review gates in authored order."

review DraftReview: "Draft Review"
    subject: DraftSpec
    contract: DraftReviewContract
    comment_output: DraftReviewComment

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    contract_checks: "Contract Checks"
        "Use {{{{contract.completeness}}}} before you route {{{{fields.next_owner}}}}."
        accept "The shared draft review contract passes." when contract.passes

    on_accept:
{_indent_block(on_accept_body, 8)}

    on_reject:
        current none
        route "Rejected draft returns to RejectOwner." -> RejectOwner

agent ReviewDemo:
    role: "Keep review routing aligned."
    review: DraftReview
    inputs: "Inputs"
        DraftSpec
    outputs: "Outputs"
        DraftReviewComment
"""


def _review_invalid_guarded_match_head_source() -> str:
    return """input DraftSpec: "Draft Spec"
    source: File
        path: "draft.md"
    shape: MarkdownDocument
    requirement: Required

workflow DraftReviewContract: "Draft Review Contract"
    completeness: "Completeness"
        "Confirm the draft covers the required sections."

output DraftReviewComment: "Draft Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

review DraftReview: "Draft Review"
    subject: DraftSpec
    contract: DraftReviewContract
    comment_output: DraftReviewComment

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    checks: "Checks"
        match DraftSpec.status:
            else when DraftSpec.needs_follow_up:
                accept "The shared draft review contract passes." when contract.passes

    on_accept:
        current none
        route "Accepted draft returns to AcceptOwner." -> AcceptOwner

    on_reject:
        current none
        route "Rejected draft returns to RejectOwner." -> RejectOwner

agent AcceptOwner:
    role: "Own accepted drafts."
    workflow: "Accept"
        "Handle the accepted draft."

agent RejectOwner:
    role: "Own rejected drafts."
    workflow: "Reject"
        "Handle the rejected draft."

agent ReviewDemo:
    role: "Keep review routing aligned."
    review: DraftReview
    inputs: "Inputs"
        DraftSpec
    outputs: "Outputs"
        DraftReviewComment
"""


def _indent_block(text: str, spaces: int) -> str:
    prefix = " " * spaces
    normalized = textwrap.dedent(text).strip("\n")
    return "\n".join(f"{prefix}{line}" if line else "" for line in normalized.splitlines())


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


if __name__ == "__main__":
    raise SystemExit(main())
