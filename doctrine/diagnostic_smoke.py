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
    _check_final_output_prose_renders()
    _check_final_output_json_renders()
    _check_review_driven_final_output_renders()
    _check_review_driven_split_final_output_renders()
    _check_review_driven_split_json_final_output_renders()
    _check_final_output_missing_schema_file_has_specific_code()
    _check_final_output_invalid_schema_json_has_specific_code()
    _check_final_output_missing_example_file_has_specific_code()
    _check_final_output_non_output_ref_has_specific_code()
    _check_final_output_missing_emission_has_specific_code()
    _check_final_output_file_target_has_specific_code()
    _check_reserved_analysis_slot_key_is_rejected()
    _check_output_schema_attachment_renders()
    _check_input_structure_attachment_renders()
    _check_readable_guard_rejects_output_owned_refs()
    _check_readable_table_requires_columns()
    _check_output_schema_owner_conflict_surfaces_as_parse_error()
    _check_output_schema_structure_conflict_surfaces_as_parse_error()
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


def _check_final_output_prose_renders() -> None:
    source = _final_output_prose_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        compiled = compile_prompt(prompt, "HelloAgent")
        _expect(compiled.final_output is not None, "expected compiled final_output metadata")
        _expect(compiled.final_output.format_mode == "prose", str(compiled.final_output))
        rendered = render_markdown(compiled)
        _expect("## Final Output" in rendered, rendered)
        _expect("| Format | Natural-language markdown |" in rendered, rendered)
        _expect("#### Read It Cold" in rendered, rendered)
        _expect("## Outputs" not in rendered, rendered)


def _check_final_output_json_renders() -> None:
    source = _final_output_json_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        root = prompt_path.parent.parent
        (root / "schemas").mkdir(exist_ok=True)
        (root / "examples").mkdir(exist_ok=True)
        (root / "schemas" / "repo_status.schema.json").write_text(
            textwrap.dedent(
                """\
                {
                  "type": "object",
                  "additionalProperties": false,
                  "properties": {
                    "summary": {
                      "type": "string",
                      "description": "Short natural-language status."
                    },
                    "status": {
                      "type": "string",
                      "enum": ["ok", "action_required"],
                      "description": "Current repo outcome."
                    },
                    "next_step": {
                      "type": ["string", "null"],
                      "description": "Null only when no follow-up is needed."
                    }
                  }
                }
                """
            ),
            encoding="utf-8",
        )
        (root / "examples" / "repo_status.example.json").write_text(
            textwrap.dedent(
                """\
                {
                  "summary": "Branch is clean and checks passed.",
                  "status": "ok",
                  "next_step": null
                }
                """
            ),
            encoding="utf-8",
        )
        prompt = parse_file(prompt_path)
        compiled = compile_prompt(prompt, "RepoStatusAgent")
        _expect(compiled.final_output is not None, "expected compiled final_output metadata")
        _expect(compiled.final_output.format_mode == "json_schema", str(compiled.final_output))
        _expect(compiled.final_output.schema_profile == "OpenAIStructuredOutput", str(compiled.final_output))
        rendered = render_markdown(compiled)
        _expect("| Format | Structured JSON |" in rendered, rendered)
        _expect("| Profile | OpenAIStructuredOutput |" in rendered, rendered)
        _expect("#### Payload Shape" in rendered, rendered)
        _expect("| `next_step` | string \\| null | Null only when no follow-up is needed. |" in rendered, rendered)


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
        _expect("Rendered only when verdict is changes requested." in rendered, rendered)
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
        _expect("Rendered only when verdict is changes requested." in final_output_block, rendered)
        _expect("Keep the control summary aligned with Current Artifact." in final_output_block, rendered)


def _check_review_driven_split_json_final_output_renders() -> None:
    source = _final_output_review_split_json_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        root = prompt_path.parent.parent
        (root / "schemas").mkdir(exist_ok=True)
        (root / "examples").mkdir(exist_ok=True)
        (root / "schemas" / "acceptance_control.schema.json").write_text(
            textwrap.dedent(
                """\
                {
                  "type": "object",
                  "additionalProperties": false,
                  "properties": {
                    "route": {
                      "type": "string",
                      "enum": ["follow_up", "revise"],
                      "description": "Control route for the next owner."
                    },
                    "current_artifact": {
                      "type": "string",
                      "description": "Current artifact after review."
                    },
                    "next_owner": {
                      "type": "string",
                      "description": "Next owner after review."
                    }
                  }
                }
                """
            ),
            encoding="utf-8",
        )
        (root / "examples" / "acceptance_control.example.json").write_text(
            textwrap.dedent(
                """\
                {
                  "route": "follow_up",
                  "current_artifact": "Draft Plan",
                  "next_owner": "ReviewLead"
                }
                """
            ),
            encoding="utf-8",
        )
        prompt = parse_file(prompt_path)
        compiled = compile_prompt(prompt, "ReviewSplitJsonFinalOutputAgent")
        _expect(compiled.final_output is not None, "expected compiled final_output metadata")
        _expect(compiled.final_output.format_mode == "json_schema", str(compiled.final_output))
        rendered = render_markdown(compiled)
        outputs_block = rendered.split("## Outputs", 1)[1].split("## Final Output", 1)[0]
        final_output_block = rendered.split("## Final Output", 1)[1]
        _expect("### Acceptance Review Comment" in outputs_block, rendered)
        _expect("### Acceptance Control Final Response" not in outputs_block, rendered)
        _expect("| Schema | Acceptance Control Schema |" in final_output_block, rendered)
        _expect("Keep `current_artifact` aligned with Current Artifact." in final_output_block, rendered)
        _expect("Use `route` value `revise` only when Outline Complete fails." in final_output_block, rendered)
        _expect("Rendered only when verdict is changes requested." in final_output_block, rendered)


def _check_final_output_missing_schema_file_has_specific_code() -> None:
    source = _final_output_json_source(schema_file="schemas/missing_repo_status.schema.json")
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        root = prompt_path.parent.parent
        (root / "examples").mkdir(exist_ok=True)
        (root / "examples" / "repo_status.example.json").write_text(
            "{\n  \"status\": \"ok\"\n}\n",
            encoding="utf-8",
        )
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "RepoStatusAgent")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E215", f"expected E215, got {getattr(exc, 'code', None)}")
            _expect("missing or unreadable" in str(exc), str(exc))
            _expect("schemas/missing_repo_status.schema.json" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for missing final_output schema file, but compilation succeeded")


def _check_final_output_invalid_schema_json_has_specific_code() -> None:
    source = _final_output_json_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        root = prompt_path.parent.parent
        (root / "schemas").mkdir(exist_ok=True)
        (root / "examples").mkdir(exist_ok=True)
        (root / "schemas" / "repo_status.schema.json").write_text(
            "{not json",
            encoding="utf-8",
        )
        (root / "examples" / "repo_status.example.json").write_text(
            "{\n  \"status\": \"ok\"\n}\n",
            encoding="utf-8",
        )
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "RepoStatusAgent")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E216", f"expected E216, got {getattr(exc, 'code', None)}")
            _expect("valid JSON object" in str(exc), str(exc))
            _expect("schemas/repo_status.schema.json" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for invalid final_output schema JSON, but compilation succeeded")


def _check_final_output_missing_example_file_has_specific_code() -> None:
    source = _final_output_json_source(example_file="examples/missing_repo_status.example.json")
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        root = prompt_path.parent.parent
        (root / "schemas").mkdir(exist_ok=True)
        (root / "schemas" / "repo_status.schema.json").write_text(
            textwrap.dedent(
                """\
                {
                  "type": "object",
                  "properties": {
                    "status": {
                      "type": "string",
                      "description": "Current repo outcome."
                    }
                  }
                }
                """
            ),
            encoding="utf-8",
        )
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "RepoStatusAgent")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E215", f"expected E215, got {getattr(exc, 'code', None)}")
            _expect("missing or unreadable" in str(exc), str(exc))
            _expect("examples/missing_repo_status.example.json" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for missing final_output example file, but compilation succeeded")


def _check_final_output_non_output_ref_has_specific_code() -> None:
    source = _final_output_non_output_ref_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "InvalidFinalOutputAgent")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E211", f"expected E211, got {getattr(exc, 'code', None)}")
            _expect("output declaration" in str(exc), str(exc))
            _expect("schema declaration" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for wrong-kind final_output ref, but compilation succeeded")


def _check_final_output_missing_emission_has_specific_code() -> None:
    source = _final_output_missing_emission_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "InvalidFinalOutputAgent")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E212", f"expected E212, got {getattr(exc, 'code', None)}")
            _expect("not emitted by the concrete turn" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for non-emitted final_output, but compilation succeeded")


def _check_final_output_file_target_has_specific_code() -> None:
    source = _final_output_file_target_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "InvalidFinalOutputAgent")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E213", f"expected E213, got {getattr(exc, 'code', None)}")
            _expect("TurnResponse" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for file-backed final_output, but compilation succeeded")


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


def _check_output_schema_structure_conflict_surfaces_as_parse_error() -> None:
    source = _output_schema_structure_conflict_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        try:
            parse_file(prompt_path)
        except Exception as exc:
            _expect(type(exc).__name__ == "ParseError", f"expected ParseError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E199", f"expected E199, got {getattr(exc, 'code', None)}")
            _expect("schema" in str(exc).lower(), str(exc))
            _expect("structure" in str(exc), str(exc))
            return
        raise SmokeFailure("expected parse failure for output schema and structure conflict, but parsing succeeded")


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
        _expect(rendered.startswith("direction: down\n"), rendered)
        _expect("Shared Input" in rendered, rendered)
        _expect("Shared Output / Carrier" in rendered, rendered)
        _expect("Used by:" in rendered, rendered)
        _expect("Produced by:" in rendered, rendered)
        _expect('primary_lane: {\n    label: ""\n    direction: down' in rendered, rendered)
        _expect(
            "agent_handoffs.primary_lane.agent_projectlead -> agent_handoffs.primary_lane.agent_researchspecialist"
            in rendered,
            rendered,
        )
        _expect(
            "agent_handoffs.primary_lane.agent_researchspecialist -> agent_handoffs.primary_lane.agent_writingspecialist"
            in rendered,
            rendered,
        )
        _expect(
            "agent_handoffs.primary_lane.agent_writingspecialist -> agent_handoffs.primary_lane.agent_projectlead"
            in rendered,
            rendered,
        )
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


def _output_schema_structure_conflict_source() -> str:
    return """schema DeliveryInventory: "Delivery Inventory"
    sections:
        summary: "Summary"
            "Include a short summary."

document DeliveryPlan: "Delivery Plan"
    section summary: "Summary"
        "Write the summary."

output InvalidDeliveryPlan: "Invalid Delivery Plan"
    target: File
        path: "unit_root/INVALID_DELIVERY_PLAN.md"
    shape: MarkdownDocument
    requirement: Required
    schema: DeliveryInventory
    structure: DeliveryPlan
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


def _final_output_prose_source() -> str:
    return """output FinalReply: "Final Reply"
    target: TurnResponse
    shape: CommentText
    requirement: Required

    format_notes: "Expected Structure"
        "Lead with the shipped outcome."

    standalone_read: "Standalone Read"
        "The user should understand what changed and what happens next."

agent HelloAgent:
    role: "Answer plainly and end the turn."
    workflow: "Reply"
        "Reply and stop."
    outputs: "Outputs"
        FinalReply
    final_output: FinalReply
"""


def _final_output_json_source(
    *,
    schema_file: str = "schemas/repo_status.schema.json",
    example_file: str = "examples/repo_status.example.json",
) -> str:
    return f"""json schema RepoStatusSchema: "Repo Status Schema"
    profile: OpenAIStructuredOutput
    file: "{schema_file}"

output shape RepoStatusJson: "Repo Status JSON"
    kind: JsonObject
    schema: RepoStatusSchema
    example_file: "{example_file}"

    explanation: "Field Notes"
        "Use the schema fields exactly once."

output RepoStatusFinalResponse: "Repo Status Final Response"
    target: TurnResponse
    shape: RepoStatusJson
    requirement: Required

    standalone_read: "Standalone Read"
        "The final answer should stand on its own as one structured repo-status result."

agent RepoStatusAgent:
    role: "Report repo status in structured form."
    workflow: "Summarize"
        "Summarize the repo state and end with the declared final output."
    outputs: "Outputs"
        RepoStatusFinalResponse
    final_output: RepoStatusFinalResponse
"""


def _final_output_non_output_ref_source() -> str:
    return """schema ReleaseSchema: "Release Schema"
    sections:
        summary: "Summary"
            "Provide a summary."

agent InvalidFinalOutputAgent:
    role: "Try to point final_output at a schema."
    workflow: "Reply"
        "Reply and stop."
    final_output: ReleaseSchema
"""


def _final_output_missing_emission_source() -> str:
    return """output FinalReply: "Final Reply"
    target: TurnResponse
    shape: CommentText
    requirement: Required

agent InvalidFinalOutputAgent:
    role: "Forget to emit the declared final output."
    workflow: "Reply"
        "Reply and stop."
    final_output: FinalReply
"""


def _final_output_file_target_source() -> str:
    return """output ReleaseNotesFile: "Release Notes File"
    target: File
        path: "artifacts/RELEASE_NOTES.md"
    shape: MarkdownDocument
    requirement: Required

agent InvalidFinalOutputAgent:
    role: "Try to end with a file."
    workflow: "Reply"
        "Reply and stop."
    outputs: "Outputs"
        ReleaseNotesFile
    final_output: ReleaseNotesFile
"""


def _final_output_review_prose_source() -> str:
    return """input DraftSpec: "Draft Spec"
    source: File
        path: "unit_root/DRAFT_SPEC.md"
    shape: MarkdownDocument
    requirement: Required

workflow DraftReviewContract: "Draft Review Contract"
    completeness: "Completeness"
        "Confirm the draft covers the required sections."

agent ReviewLead:
    role: "Own accepted drafts."
    workflow: "Follow Up"
        "Take accepted drafts forward."

agent DraftAuthor:
    role: "Fix rejected drafts."
    workflow: "Revise"
        "Revise the rejected draft."

output DraftReviewComment: "Draft Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    verdict: "Verdict"
        "State whether the draft passed review."

    reviewed_artifact: "Reviewed Artifact"
        "Name the reviewed artifact."

    analysis_performed: "Analysis Performed"
        "Summarize the review analysis."

    output_contents_that_matter: "Output Contents That Matter"
        "Summarize what the next owner should read first."

    current_artifact: "Current Artifact"
        "Name the artifact that remains current after review."

    next_owner: "Next Owner"
        "Name {{ReviewLead}} when accepted and {{DraftAuthor}} when rejected."

    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
        failing_gates: "Failing Gates"
            "List the failing review gates in authored order."

    trust_surface:
        current_artifact

    standalone_read: "Standalone Read"
        "A downstream owner should understand the review verdict, current artifact, and next owner from this output alone."

review DraftReview: "Draft Review"
    subject: DraftSpec
    contract: DraftReviewContract
    comment_output: DraftReviewComment

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        current_artifact: current_artifact
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    contract_checks: "Contract Checks"
        accept "The shared draft review contract passes." when contract.passes

    on_accept: "If Accepted"
        current artifact DraftSpec via DraftReviewComment.current_artifact
        route "Accepted draft returns to ReviewLead." -> ReviewLead

    on_reject: "If Rejected"
        current artifact DraftSpec via DraftReviewComment.current_artifact
        route "Rejected draft returns to DraftAuthor." -> DraftAuthor

agent ReviewFinalOutputAgent:
    role: "Keep review final outputs aligned."
    review: DraftReview
    inputs: "Inputs"
        DraftSpec
    outputs: "Outputs"
        DraftReviewComment
    final_output: DraftReviewComment
"""


def _final_output_review_split_prose_source() -> str:
    return _final_output_review_prose_source() + """

output DraftReviewDecision: "Draft Review Decision"
    target: TurnResponse
    shape: CommentText
    requirement: Required

    control_summary: "Control Summary"
        "End with one short control summary for the routed owner."

    retry_note: "Retry Note" when verdict == ReviewVerdict.changes_requested:
        "Only include this note when the review requests changes."

    current_alignment: "Current Artifact Alignment"
        "Keep the control summary aligned with {{fields.current_artifact}}."

    standalone_read: "Standalone Read"
        "The final control summary should stand on its own for the routed owner."

agent SplitReviewFinalOutputAgent:
    role: "Emit the rich review comment and a small final control summary."
    review: DraftReview
    inputs: "Inputs"
        DraftSpec
    outputs: "Outputs"
        DraftReviewComment
        DraftReviewDecision
    final_output: DraftReviewDecision
"""


def _final_output_review_split_json_source() -> str:
    return """json schema AcceptanceControlSchema: "Acceptance Control Schema"
    profile: OpenAIStructuredOutput
    file: "schemas/acceptance_control.schema.json"

output shape AcceptanceControlJson: "Acceptance Control JSON"
    kind: JsonObject
    schema: AcceptanceControlSchema
    example_file: "examples/acceptance_control.example.json"

    field_notes: "Field Notes"
        "Keep `current_artifact` aligned with {{fields.current_artifact}}."
        "Use `route` value `revise` only when {{contract.outline_complete}} fails."

input DraftPlan: "Draft Plan"
    source: File
        path: "unit_root/DRAFT_PLAN.md"
    shape: MarkdownDocument
    requirement: Required

schema PlanReviewContract: "Plan Review Contract"
    sections:
        summary: "Summary"
            "Summarize the reviewed plan."

    gates:
        outline_complete: "Outline Complete"
            "Confirm the reviewed plan includes the outline."

agent ReviewLead:
    role: "Own accepted plans."
    workflow: "Follow Up"
        "Take accepted plans forward."

agent PlanAuthor:
    role: "Fix rejected plans."
    workflow: "Revise"
        "Revise the rejected plan."

output AcceptanceReviewComment: "Acceptance Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    verdict: "Verdict"
        "State whether the plan passed review."

    reviewed_artifact: "Reviewed Artifact"
        "Name the reviewed artifact."

    analysis_performed: "Analysis Performed"
        "Summarize the review analysis."

    output_contents_that_matter: "Output Contents That Matter"
        "Summarize what the next owner should read first."

    current_artifact: "Current Artifact"
        "Name the artifact that remains current after review."

    next_owner: "Next Owner"
        "Name {{ReviewLead}} when accepted and {{PlanAuthor}} when rejected."

    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
        failing_gates: "Failing Gates"
            "List exact failing gates, including {{contract.outline_complete}} when it fails."

    trust_surface:
        current_artifact

    standalone_read: "Standalone Read"
        "A downstream owner should understand the acceptance verdict, current artifact, and next owner from this output alone."

output AcceptanceControlFinalResponse: "Acceptance Control Final Response"
    target: TurnResponse
    shape: AcceptanceControlJson
    requirement: Required

    changes_requested_note: "Changes Requested Note" when verdict == ReviewVerdict.changes_requested:
        "Only emit this retry control when the review requests changes."

    standalone_read: "Standalone Read"
        "This final JSON should be enough for the next owner to route the review result."

review AcceptanceReview: "Acceptance Review"
    subject: DraftPlan
    contract: PlanReviewContract
    comment_output: AcceptanceReviewComment

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        current_artifact: current_artifact
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    contract_checks: "Contract Checks"
        accept "The acceptance review contract passes." when contract.passes

    on_accept: "If Accepted"
        current artifact DraftPlan via AcceptanceReviewComment.current_artifact
        route "Accepted plan returns to ReviewLead." -> ReviewLead

    on_reject: "If Rejected"
        current artifact DraftPlan via AcceptanceReviewComment.current_artifact
        route "Rejected plan returns to PlanAuthor." -> PlanAuthor

agent ReviewSplitJsonFinalOutputAgent:
    role: "Emit the review comment and end with a control-only JSON result."
    review: AcceptanceReview
    inputs: "Inputs"
        DraftPlan
    outputs: "Outputs"
        AcceptanceReviewComment
        AcceptanceControlFinalResponse
    final_output: AcceptanceControlFinalResponse
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
