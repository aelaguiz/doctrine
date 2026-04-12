from __future__ import annotations

import contextlib
import io
import json
import re
import signal
import textwrap
from pathlib import Path
from tempfile import TemporaryDirectory

from doctrine.compiler import compile_prompt, extract_target_flow_graph
from doctrine.diagnostics import diagnostic_to_dict
from doctrine.emit_docs import main as emit_docs_main
from doctrine.emit_flow import main as emit_flow_main
from doctrine.parser import parse_file, parse_text
from doctrine.renderer import render_markdown


class SmokeFailure(RuntimeError):
    """Raised when the direct diagnostic smoke checks fail."""


def main() -> int:
    _check_transform_errors_surface_as_parse_errors()
    _check_invalid_string_literals_surface_as_parse_errors()
    _check_parse_text_preserves_source_path_for_compilation()
    _check_compile_missing_role_has_specific_code()
    _check_analysis_field_renders()
    _check_reserved_analysis_slot_key_is_rejected()
    _check_output_schema_attachment_renders()
    _check_input_structure_attachment_renders()
    _check_readable_guard_rejects_output_owned_refs()
    _check_readable_table_requires_columns()
    _check_output_schema_owner_conflict_surfaces_as_parse_error()
    _check_review_illegal_statement_placement_has_specific_code()
    _check_review_invalid_guarded_match_head_has_specific_code()
    _check_review_multiple_currentness_has_specific_code()
    _check_review_outcome_not_total_has_specific_code()
    _check_review_next_owner_alignment_has_specific_code()
    _check_review_failure_detail_guard_has_specific_code()
    _check_review_exact_contract_gate_modes_do_not_blow_up()
    _check_review_semantic_addressability_renders()
    _check_emit_docs_handles_invalid_toml_without_traceback()
    _check_emit_docs_uses_specific_code_for_missing_entrypoint()
    _check_emit_docs_uses_entrypoint_stem_for_output_name()
    _check_flow_graph_extracts_routes_and_shared_io()
    _check_emit_flow_uses_entrypoint_stem_for_output_name()
    _check_emit_flow_direct_mode_groups_shared_surfaces()
    _check_emit_flow_direct_mode_requires_output_dir()
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


def _check_invalid_string_literals_surface_as_parse_errors() -> None:
    source = """agent Demo:
    role: "bad \\x"
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        try:
            parse_file(prompt_path)
        except Exception as exc:
            _expect(type(exc).__name__ == "ParseError", f"expected ParseError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E106", f"expected E106, got {getattr(exc, 'code', None)}")
            rendered = str(exc)
            _expect("Invalid string literal" in rendered, rendered)
            _expect("truncated \\xXX escape" in rendered, rendered)
            return
        raise SmokeFailure("expected invalid string literal parse failure, but parsing succeeded")


def _check_parse_text_preserves_source_path_for_compilation() -> None:
    source = """agent GreetingDemo:
    role: "Say hello."
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        parsed = parse_text(prompt_path.read_text(), source_path=prompt_path)
        _expect(parsed.source_path == prompt_path.resolve(), f"expected source_path {prompt_path.resolve()}, got {parsed.source_path!r}")
        rendered = compile_prompt(parsed, "GreetingDemo")
        _expect(rendered.name == "GreetingDemo", f"expected GreetingDemo, got {rendered.name}")


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


def _check_analysis_field_renders() -> None:
    source = _analysis_attachment_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "AnalysisDemo"))
        _expect("## Draft Analysis" in rendered, rendered)
        _expect("### Facts" in rendered, rendered)
        _expect("Restate the current draft job before you route work." in rendered, rendered)


def _check_reserved_analysis_slot_key_is_rejected() -> None:
    source = _reserved_analysis_slot_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "AnalysisDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect("reserved typed agent field" in str(exc).lower(), str(exc))
            _expect("analysis" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for reserved analysis slot key, but compilation succeeded")


def _check_output_schema_attachment_renders() -> None:
    source = _output_schema_attachment_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "OutputDemo"))
        _expect("- Schema: Lesson Inventory" in rendered, rendered)
        _expect("### Required Sections" in rendered, rendered)
        _expect("#### Summary" in rendered, rendered)


def _check_input_structure_attachment_renders() -> None:
    source = _input_structure_attachment_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "InputDemo"))
        _expect("- Structure: Lesson Plan" in rendered, rendered)
        _expect("### Structure: Lesson Plan" in rendered, rendered)
        _expect("#### Summary" in rendered, rendered)


def _check_readable_guard_rejects_output_owned_refs() -> None:
    source = _invalid_readable_guard_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "ReadableGuardDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect("Readable guard reads disallowed source" in str(exc), str(exc))
            _expect("BrokenComment.summary_present" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for readable guard source, but compilation succeeded")


def _check_readable_table_requires_columns() -> None:
    source = _invalid_readable_table_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "ReadableTableDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect("Readable table must declare at least one column" in str(exc), str(exc))
            _expect("BrokenGuide.release_gates" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for readable table without columns, but compilation succeeded")


def _check_output_schema_owner_conflict_surfaces_as_parse_error() -> None:
    source = _output_schema_owner_conflict_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        try:
            parse_file(prompt_path)
        except Exception as exc:
            _expect(type(exc).__name__ == "ParseError", f"expected ParseError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E199", f"expected E199, got {getattr(exc, 'code', None)}")
            _expect("schema" in str(exc).lower(), str(exc))
            _expect("must_include" in str(exc), str(exc))
            return
        raise SmokeFailure("expected parse failure for output schema owner conflict, but parsing succeeded")


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


def _check_emit_flow_direct_mode_groups_shared_surfaces() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "showcase"
        prompts.mkdir(parents=True)
        entrypoint = prompts / "AGENTS.prompt"
        entrypoint.write_text(_flow_visualizer_showcase_source())
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[project]
name = "doctrine-smoke"
version = "0.0.0"
"""
        )

        exit_code = emit_flow_main(
            [
                "--pyproject",
                str(pyproject),
                "--entrypoint",
                str(entrypoint.relative_to(root)),
                "--output-dir",
                "build",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")

        d2_path = root / "build" / "showcase" / "AGENTS.flow.d2"
        svg_path = root / "build" / "showcase" / "AGENTS.flow.svg"
        _expect(d2_path.is_file(), f"missing emitted AGENTS.flow.d2: {d2_path}")
        _expect(svg_path.is_file(), f"missing emitted AGENTS.flow.svg: {svg_path}")

        rendered = d2_path.read_text()
        _expect("shared_inputs: {" in rendered, rendered)
        _expect("agent_handoffs: {" in rendered, rendered)
        _expect("shared_outputs_and_carriers: {" in rendered, rendered)
        _expect("Shared Input" in rendered, rendered)
        _expect("Shared Output / Carrier" in rendered, rendered)
        _expect("Used by:" in rendered, rendered)
        _expect("Produced by:" in rendered, rendered)
        _expect("Start research with" in rendered, rendered)
        _expect("Return the draft to" in rendered, rendered)


def _check_emit_flow_direct_mode_requires_output_dir() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts"
        prompts.mkdir()
        entrypoint = prompts / "AGENTS.prompt"
        entrypoint.write_text(
            """agent DemoAgent:
    role: "Own the demo flow."
"""
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[project]
name = "doctrine-smoke"
version = "0.0.0"
"""
        )

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_flow_main(
                [
                    "--pyproject",
                    str(pyproject),
                    "--entrypoint",
                    str(entrypoint.relative_to(root)),
                ]
            )
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E518 emit error" in output, output)
        _expect("Direct emit flow mode requires entrypoint and output_dir" in output, output)


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


def _analysis_attachment_source() -> str:
    return """analysis DraftAnalysis: "Draft Analysis"
    facts: "Facts"
        "Restate the current draft job before you route work."

agent AnalysisDemo:
    role: "Keep the analysis attachment visible."
    analysis: DraftAnalysis
"""


def _reserved_analysis_slot_source() -> str:
    return """analysis DraftAnalysis: "Draft Analysis"
    facts: "Facts"
        "Restate the current draft job before you route work."

abstract agent AnalysisBase:
    role: "Base role."
    abstract analysis

agent AnalysisDemo [AnalysisBase]:
    role: "Keep the analysis attachment visible."
    analysis: DraftAnalysis
"""


def _output_schema_attachment_source() -> str:
    return """schema LessonInventory: "Lesson Inventory"
    sections:
        summary: "Summary"
            "State the required summary."

output SchemaOutput: "Schema Output"
    target: TurnResponse
    shape: JsonObject
    requirement: Required
    schema: LessonInventory

agent OutputDemo:
    role: "Keep the schema attachment visible."
    outputs: "Outputs"
        SchemaOutput
"""


def _input_structure_attachment_source() -> str:
    return """document LessonPlan: "Lesson Plan"
    section summary: "Summary"
        "State the lesson summary."

input DraftSpec: "Draft Spec"
    source: File
        path: "draft.md"
    shape: MarkdownDocument
    requirement: Required
    structure: LessonPlan

agent InputDemo:
    role: "Keep the structure attachment visible."
    inputs: "Inputs"
        DraftSpec
"""


def _invalid_readable_guard_source() -> str:
    return """output BrokenComment: "Broken Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    callout scope: "Scope" when BrokenComment.summary_present
        kind: note
        "This should fail."

agent ReadableGuardDemo:
    role: "Keep readable guards honest."
    outputs: "Outputs"
        BrokenComment
"""


def _invalid_readable_table_source() -> str:
    return """document BrokenGuide: "Broken Guide"
    table release_gates: "Release Gates"
        notes:
            "This should fail."

output BrokenGuideFile: "Broken Guide File"
    target: File
        path: "broken.md"
    shape: MarkdownDocument
    requirement: Required
    structure: BrokenGuide

agent ReadableTableDemo:
    role: "Keep readable tables honest."
    outputs: "Outputs"
        BrokenGuideFile
"""


def _output_schema_owner_conflict_source() -> str:
    return """schema LessonInventory: "Lesson Inventory"
    sections:
        summary: "Summary"
            "State the required summary."

output SchemaOutput: "Schema Output"
    target: TurnResponse
    shape: JsonObject
    requirement: Required
    schema: LessonInventory

    must_include: "Must Include"
        summary: "Summary"
            "Repeat the summary locally."

agent OutputDemo:
    role: "Keep the schema attachment visible."
    outputs: "Outputs"
        SchemaOutput
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


def _review_exact_gate_stress_source(*, gate_count: int) -> str:
    base_path = (
        Path(__file__).resolve().parent.parent
        / "examples"
        / "45_review_contract_gate_export_and_exact_failures"
        / "prompts"
        / "AGENTS.prompt"
    )
    base = base_path.read_text()
    modes = "\n".join(f"    m{i}: \"m{i}\"" for i in range(gate_count))
    gates = "".join(
        f"""    gate_{i}: "Gate {i}"
        "Confirm gate {i}."

"""
        for i in range(gate_count)
    )
    gate_refs = ", ".join(f"{{{{contract.gate_{i}}}}}" for i in range(gate_count))
    mode_checks = "".join(
        f"""            ReviewMode.m{i}:
                reject contract.gate_{i} when ReviewFacts.selected_review_basis_failed

"""
        for i in range(gate_count)
    )
    source = (
        f"""enum ReviewMode: "Review Mode"
{modes}

input ReviewFacts: "Review Facts"
    source: Prompt
    shape: JsonObject
    requirement: Required

"""
        + base
    )
    source = re.sub(
        r'workflow ExactGateReviewContract: "Exact Gate Review Contract"\n(?:    .*?\n\n)+?# Declare the owners',
        'workflow ExactGateReviewContract: "Exact Gate Review Contract"\n'
        + gates
        + "# Declare the owners",
        source,
        flags=re.S,
    )
    source = source.replace(
        '    inputs: "Inputs"\n        DraftSpec\n',
        '    inputs: "Inputs"\n        DraftSpec\n        ReviewFacts\n',
    )
    source = source.replace(
        '            "Name the exact exported shared-contract gate identities in authored order, including {{contract.completeness}}, {{contract.clarity}}, and {{contract.handoff_truth}} when they fail."',
        f'            "Name the exact exported shared-contract gate identities in authored order, including {gate_refs} when they fail."',
    )
    source = re.sub(
        r'    contract_gate_checks: "Contract Gate Checks"\n(?:        .*\n)+?\n    on_accept:',
        '    contract_gate_checks: "Contract Gate Checks"\n'
        '        match ReviewFacts.selected_mode:\n'
        + mode_checks
        + '        accept "The shared review contract passes." when contract.passes\n\n'
        '    on_accept:',
        source,
    )
    return source


def _flow_visualizer_showcase_source() -> str:
    return """input ProjectBrief: "Project Brief"
    source: File
        path: "project_root/_authoring/PROJECT_BRIEF.md"
    shape: MarkdownDocument
    requirement: Required

input AudienceGuide: "Audience Guide"
    source: File
        path: "project_root/_authoring/AUDIENCE_GUIDE.md"
    shape: MarkdownDocument
    requirement: Required

output ExecutionPlan: "Execution Plan"
    target: File
        path: "project_root/_authoring/EXECUTION_PLAN.md"
    shape: MarkdownDocument
    requirement: Required

output ResearchPacket: "Research Packet"
    target: File
        path: "project_root/_authoring/RESEARCH_PACKET.md"
    shape: MarkdownDocument
    requirement: Required

output LaunchDraft: "Launch Draft"
    target: File
        path: "project_root/_authoring/LAUNCH_DRAFT.md"
    shape: MarkdownDocument
    requirement: Required

output SharedHandoff: "Shared Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the artifact that is current after this turn."

    use_now: "Use Now"
        "Name the file or comment the next owner should read first."

    next_owner: "Next Owner"
        "Name the honest next owner."

    trust_surface:
        current_artifact
        use_now
        next_owner

agent ProjectLead:
    role: "Plan the work and route it to research."
    workflow: "Project Lead"
        routing: "Project Routing"
            route "Start research with ResearchSpecialist." -> ResearchSpecialist
    inputs: "Inputs"
        ProjectBrief
        AudienceGuide
    outputs: "Outputs"
        ExecutionPlan
        SharedHandoff

agent ResearchSpecialist:
    role: "Turn the brief into a research packet."
    workflow: "Research"
        routing: "Project Routing"
            route "Hand the research packet to WritingSpecialist." -> WritingSpecialist
    inputs: "Inputs"
        ProjectBrief
        AudienceGuide
    outputs: "Outputs"
        ResearchPacket
        SharedHandoff

agent WritingSpecialist:
    role: "Turn the research packet into a launch draft."
    workflow: "Writing"
        routing: "Project Routing"
            route "Return the draft to ProjectLead." -> ProjectLead
    inputs: "Inputs"
        ProjectBrief
        AudienceGuide
    outputs: "Outputs"
        LaunchDraft
        SharedHandoff
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
