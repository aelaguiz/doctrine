from __future__ import annotations
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
    _final_output_missing_local_shape_source,
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


def _expect_compile_diagnostic(
    exc: Exception,
    *,
    code: str,
    line: int | None,
    related: tuple[tuple[str, int | None], ...] = (),
) -> None:
    _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
    _expect(getattr(exc, "code", None) == code, f"expected {code}, got {getattr(exc, 'code', None)}")
    location = getattr(exc, "location", None)
    _expect(location is not None, "expected diagnostic location")
    _expect(getattr(location, "line", None) == line, f"expected line {line}, got {getattr(location, 'line', None)}")
    actual_related = tuple(
        (
            item.label,
            item.location.line if item.location is not None else None,
        )
        for item in getattr(getattr(exc, "diagnostic", None), "related", ())
    )
    _expect(
        actual_related == related,
        f"expected related {related}, got {actual_related}",
    )


def run_compile_checks() -> None:
    _check_compile_missing_role_has_specific_code()
    _check_analysis_field_renders()
    _check_final_output_prose_renders()
    _check_final_output_json_renders()
    _check_final_output_invalid_lowered_schema_has_specific_code()
    _check_final_output_excessive_nesting_has_specific_code()
    _check_final_output_invalid_example_json_has_specific_code()
    _check_final_output_missing_example_is_allowed()
    _check_final_output_non_output_ref_has_specific_code()
    _check_final_output_missing_local_shape_has_specific_code()
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
            _expect_compile_diagnostic(exc, code="E205", line=1)
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
        prompt = parse_file(prompt_path)
        compiled = compile_prompt(prompt, "RepoStatusAgent")
        _expect(compiled.final_output is not None, "expected compiled final_output metadata")
        _expect(compiled.final_output.format_mode == "json_object", str(compiled.final_output))
        _expect(compiled.final_output.schema_profile == "OpenAIStructuredOutput", str(compiled.final_output))
        rendered = render_markdown(compiled)
        _expect("| Format | Structured JSON |" in rendered, rendered)
        _expect("| Profile | OpenAIStructuredOutput |" in rendered, rendered)
        _expect("#### Payload Fields" in rendered, rendered)
        _expect(
            "| `next_step` | string | Yes | Yes | Null only when no follow-up is needed. |" in rendered,
            rendered,
        )


def _check_final_output_invalid_lowered_schema_has_specific_code() -> None:
    source = _final_output_json_source(
        schema_body="""output schema RepoStatusSchema: "Repo Status Schema"
    field status: "Status"
        type: definitely_not_a_real_json_schema_type
""",
        example_body="""example:
        status: "ok"
""",
    )
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "RepoStatusAgent")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E320", f"expected E320, got {getattr(exc, 'code', None)}")
            _expect("definitely_not_a_real_json_schema_type" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for unknown output-schema `type:` name, but compilation succeeded")


def _check_final_output_excessive_nesting_has_specific_code() -> None:
    source = _final_output_json_source(
        schema_body="""output schema RepoStatusSchema: "Repo Status Schema"
    field level_0: "Level 0"
        type: object

        field level_1: "Level 1"
            type: object

            field level_2: "Level 2"
                type: object

                field level_3: "Level 3"
                    type: object

                    field level_4: "Level 4"
                        type: object

                        field level_5: "Level 5"
                            type: object

                            field summary: "Summary"
                                type: string
""",
    )
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "RepoStatusAgent")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E218", f"expected E218, got {getattr(exc, 'code', None)}")
            _expect("nesting exceeds 5 levels" in str(exc), str(exc))
            _expect("output schema RepoStatusSchema" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for excessive final_output schema nesting, but compilation succeeded")


def _check_final_output_invalid_example_json_has_specific_code() -> None:
    source = _final_output_json_source(
        example_body="""example:
        summary: 7
        status: "ok"
        next_step: null
""",
    )
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "RepoStatusAgent")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E216", f"expected E216, got {getattr(exc, 'code', None)}")
            _expect("does not match the lowered schema" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for invalid final_output example instance, but compilation succeeded")


def _check_final_output_missing_example_is_allowed() -> None:
    source = _final_output_json_source(example_body=None)
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        compiled = compile_prompt(prompt, "RepoStatusAgent")
        rendered = render_markdown(compiled)
        _expect("#### Payload Fields" in rendered, rendered)
        _expect("#### Example" not in rendered, rendered)


def _check_final_output_non_output_ref_has_specific_code() -> None:
    source = _final_output_non_output_ref_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "InvalidFinalOutputAgent")
        except Exception as exc:
            _expect_compile_diagnostic(exc, code="E211", line=10)
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
            _expect_compile_diagnostic(exc, code="E212", line=10)
            return
        raise SmokeFailure("expected compile failure for non-emitted final_output, but compilation succeeded")


def _check_final_output_missing_local_shape_has_specific_code() -> None:
    source = _final_output_missing_local_shape_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "InvalidFinalOutputAgent")
        except Exception as exc:
            _expect_compile_diagnostic(exc, code="E276", line=3)
            return
        raise SmokeFailure("expected compile failure for missing local final_output shape, but compilation succeeded")


def _check_final_output_file_target_has_specific_code() -> None:
    source = _final_output_file_target_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "InvalidFinalOutputAgent")
        except Exception as exc:
            _expect_compile_diagnostic(
                exc,
                code="E213",
                line=2,
                related=(("`final_output` field", 13),),
            )
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
            _expect_compile_diagnostic(exc, code="E299", line=7)
            return
        raise SmokeFailure("expected compile failure for reserved analysis slot key, but compilation succeeded")


def _check_output_schema_attachment_renders() -> None:
    source = _output_schema_attachment_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "OutputDemo"))
        _expect("| Contract | Value |" in rendered, rendered)
        _expect("| Schema | Lesson Inventory |" in rendered, rendered)
        _expect("#### Required Sections" in rendered, rendered)
        _expect("##### Summary" in rendered, rendered)


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
            _expect_compile_diagnostic(exc, code="E296", line=6)
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
            _expect_compile_diagnostic(exc, code="E297", line=2)
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
