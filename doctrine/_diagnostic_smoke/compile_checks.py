from __future__ import annotations
from tempfile import TemporaryDirectory

from doctrine.compiler import compile_prompt
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown

from doctrine._diagnostic_smoke.fixtures import (
    SmokeFailure,
    _abstract_slot_annotation_unresolved_source,
    _analysis_attachment_source,
    _concrete_agent_wrong_family_binding_source,
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
    _output_shape_enum_only_selector_source,
    _output_target_typed_as_family_mismatch_source,
    _output_target_typed_as_unsupported_kind_source,
    _reserved_analysis_slot_source,
    _rule_forbids_bind_violated_source,
    _rule_requires_declare_violated_source,
    _rule_requires_inherit_violated_source,
    _rule_unknown_assertion_target_source,
    _rule_unknown_scope_target_source,
    _skill_binding_mode_audit_output_bind_source,
    _skill_binding_mode_enum_missing_source,
    _skill_binding_mode_not_in_enum_source,
    _write_prompt,
)
from doctrine._diagnostic_smoke.fixtures_reviews import (
    _review_case_gate_override_add_collision_source,
    _review_case_gate_override_remove_missing_source,
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
    _check_review_case_gate_override_remove_missing_has_specific_code()
    _check_review_case_gate_override_add_collision_has_specific_code()
    _check_output_target_typed_as_unsupported_kind_emits_e533()
    _check_output_target_typed_as_family_mismatch_emits_e534()
    _check_skill_binding_mode_enum_missing_emits_e540()
    _check_skill_binding_mode_audit_output_bind_emits_e541()
    _check_skill_binding_mode_not_in_enum_emits_e542()
    _check_output_shape_enum_only_selector_emits_e543()
    _check_concrete_agent_wrong_family_binding_emits_e538()
    _check_abstract_slot_annotation_unresolved_emits_e539()
    _check_rule_unknown_scope_target_emits_rule001()
    _check_rule_unknown_assertion_target_emits_rule002()
    _check_rule_requires_inherit_violated_emits_rule003()
    _check_rule_forbids_bind_violated_emits_rule004()
    _check_rule_requires_declare_violated_emits_rule005()


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


def _check_review_case_gate_override_remove_missing_has_specific_code() -> None:
    source = _review_case_gate_override_remove_missing_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "SelectedReviewFamilyDemo")
        except Exception as exc:
            _expect_compile_diagnostic(exc, code="E531", line=88)
            return
        raise SmokeFailure(
            "expected compile failure for review case override removing an undeclared gate, but compilation succeeded"
        )


def _check_review_case_gate_override_add_collision_has_specific_code() -> None:
    source = _review_case_gate_override_add_collision_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "SelectedReviewFamilyDemo")
        except Exception as exc:
            _expect_compile_diagnostic(exc, code="E532", line=89)
            return
        raise SmokeFailure(
            "expected compile failure for review case override adding a colliding gate, but compilation succeeded"
        )


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


def _check_output_target_typed_as_unsupported_kind_emits_e533() -> None:
    source = _output_target_typed_as_unsupported_kind_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "StrayHandoffDemo")
        except Exception as exc:
            _expect_compile_diagnostic(exc, code="E533", line=6)
            return
        raise SmokeFailure(
            "expected compile failure for typed_as referencing a non-document/schema/table entity, but compilation succeeded"
        )


def _check_output_target_typed_as_family_mismatch_emits_e534() -> None:
    source = _output_target_typed_as_family_mismatch_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "MismatchedHandoffDemo")
        except Exception as exc:
            _expect_compile_diagnostic(exc, code="E534", line=16)
            return
        raise SmokeFailure(
            "expected compile failure for output family mismatch with typed_as, but compilation succeeded"
        )


def _check_skill_binding_mode_enum_missing_emits_e540() -> None:
    source = _skill_binding_mode_enum_missing_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "ProducerAgent")
        except Exception as exc:
            _expect_compile_diagnostic(exc, code="E540", line=22)
            return
        raise SmokeFailure(
            "expected compile failure for skill-binding mode referencing an undeclared enum, but compilation succeeded"
        )


def _check_skill_binding_mode_audit_output_bind_emits_e541() -> None:
    source = _skill_binding_mode_audit_output_bind_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "AuditorAgent")
        except Exception as exc:
            _expect_compile_diagnostic(exc, code="E541", line=33)
            return
        raise SmokeFailure(
            "expected compile failure for audit-mode skill binding that emits to a final_output slot, but compilation succeeded"
        )


def _check_skill_binding_mode_not_in_enum_emits_e542() -> None:
    source = _skill_binding_mode_not_in_enum_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "ProducerAgent")
        except Exception as exc:
            _expect_compile_diagnostic(exc, code="E542", line=22)
            return
        raise SmokeFailure(
            "expected compile failure for skill-binding mode that is not a member of the enum, but compilation succeeded"
        )


def _check_output_shape_enum_only_selector_emits_e543() -> None:
    source = _output_shape_enum_only_selector_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "WriterDemo")
        except Exception as exc:
            _expect_compile_diagnostic(exc, code="E543", line=19)
            return
        raise SmokeFailure(
            "expected compile failure for deprecated enum-only output-shape selector form, but compilation succeeded"
        )


def _check_concrete_agent_wrong_family_binding_emits_e538() -> None:
    source = _concrete_agent_wrong_family_binding_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "TypedPolicyConcrete")
        except Exception as exc:
            _expect_compile_diagnostic(exc, code="E538", line=17)
            return
        raise SmokeFailure(
            "expected compile failure for concrete agent binding typed abstract slot to a wrong-family entity, but compilation succeeded"
        )


def _check_abstract_slot_annotation_unresolved_emits_e539() -> None:
    source = _abstract_slot_annotation_unresolved_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "TypedPolicyConcrete")
        except Exception as exc:
            _expect_compile_diagnostic(exc, code="E539", line=2)
            return
        raise SmokeFailure(
            "expected compile failure for typed abstract slot annotation referencing an unknown entity, but compilation succeeded"
        )


def _check_rule_unknown_scope_target_emits_rule001() -> None:
    source = _rule_unknown_scope_target_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "DemoComposer")
        except Exception as exc:
            _expect(
                type(exc).__name__ == "CompileError",
                f"expected CompileError, got {type(exc).__name__}",
            )
            _expect(
                getattr(exc, "code", None) == "RULE001",
                f"expected RULE001, got {getattr(exc, 'code', None)}",
            )
            return
        raise SmokeFailure(
            "expected compile failure for rule scope referencing an unknown agent, but compilation succeeded"
        )


def _check_rule_unknown_assertion_target_emits_rule002() -> None:
    source = _rule_unknown_assertion_target_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "DemoComposer")
        except Exception as exc:
            _expect(
                type(exc).__name__ == "CompileError",
                f"expected CompileError, got {type(exc).__name__}",
            )
            _expect(
                getattr(exc, "code", None) == "RULE002",
                f"expected RULE002, got {getattr(exc, 'code', None)}",
            )
            return
        raise SmokeFailure(
            "expected compile failure for rule assertion referencing an unknown agent, but compilation succeeded"
        )


def _check_rule_requires_inherit_violated_emits_rule003() -> None:
    source = _rule_requires_inherit_violated_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "HonestComposer")
        except Exception as exc:
            _expect(
                type(exc).__name__ == "CompileError",
                f"expected CompileError, got {type(exc).__name__}",
            )
            _expect(
                getattr(exc, "code", None) == "RULE003",
                f"expected RULE003, got {getattr(exc, 'code', None)}",
            )
            return
        raise SmokeFailure(
            "expected compile failure for scoped agent missing required inheritance, but compilation succeeded"
        )


def _check_rule_forbids_bind_violated_emits_rule004() -> None:
    source = _rule_forbids_bind_violated_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "BadComposer")
        except Exception as exc:
            _expect(
                type(exc).__name__ == "CompileError",
                f"expected CompileError, got {type(exc).__name__}",
            )
            _expect(
                getattr(exc, "code", None) == "RULE004",
                f"expected RULE004, got {getattr(exc, 'code', None)}",
            )
            return
        raise SmokeFailure(
            "expected compile failure for scoped agent binding a forbidden ancestor, but compilation succeeded"
        )


def _check_rule_requires_declare_violated_emits_rule005() -> None:
    source = _rule_requires_declare_violated_source()
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "PlainComposer")
        except Exception as exc:
            _expect(
                type(exc).__name__ == "CompileError",
                f"expected CompileError, got {type(exc).__name__}",
            )
            _expect(
                getattr(exc, "code", None) == "RULE005",
                f"expected RULE005, got {getattr(exc, 'code', None)}",
            )
            return
        raise SmokeFailure(
            "expected compile failure for scoped agent missing required slot declaration, but compilation succeeded"
        )
