from __future__ import annotations

import textwrap
from tempfile import TemporaryDirectory

from doctrine.compiler import compile_prompt
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown

from doctrine._diagnostic_smoke.fixtures import (
    SmokeFailure,
    _analysis_attachment_source,
    _expect,
    _final_output_file_target_source,
    _final_output_json_source,
    _final_output_missing_emission_source,
    _final_output_non_output_ref_source,
    _final_output_prose_source,
    _input_structure_attachment_source,
    _invalid_readable_guard_source,
    _invalid_readable_table_source,
    _output_schema_attachment_source,
    _output_schema_owner_conflict_source,
    _output_schema_structure_conflict_source,
    _reserved_analysis_slot_source,
    _write_prompt,
)


def run_compile_checks() -> None:
    _check_compile_missing_role_has_specific_code()
    _check_analysis_field_renders()
    _check_final_output_prose_renders()
    _check_final_output_json_renders()
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
        _expect("#### Read on Its Own" in rendered, rendered)
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
        _expect("#### Payload Fields" in rendered, rendered)
        _expect("| `next_step` | string \\| null | Null only when no follow-up is needed. |" in rendered, rendered)


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
