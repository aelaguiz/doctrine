from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine import model
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.session import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file


class OutputSchemaLoweringTests(unittest.TestCase):
    def _lower_output_schema(
        self,
        source: str,
        *,
        schema_name: str,
        extra_files: dict[str, str] | None = None,
    ) -> tuple[model.OutputSchemaDecl, dict[str, object]]:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompts" / "AGENTS.prompt"
            prompt_path.parent.mkdir(parents=True)
            prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
            for rel_path, contents in (extra_files or {}).items():
                target_path = root / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(textwrap.dedent(contents), encoding="utf-8")

            prompt = parse_file(prompt_path)
            session = CompilationSession(prompt)
            context = CompilationContext(session)
            unit, decl = context._resolve_output_schema_decl(
                model.NameRef(module_parts=(), declaration_name=schema_name),
                unit=session.root_flow.entrypoint_unit,
            )
            return decl, context._lower_output_schema_decl(decl, unit=unit)

    def _lower_output_schema_error(
        self,
        source: str,
        *,
        schema_name: str,
        extra_files: dict[str, str] | None = None,
    ) -> CompileError:
        with self.assertRaises(CompileError) as ctx:
            self._lower_output_schema(
                source,
                schema_name=schema_name,
                extra_files=extra_files,
            )
        return ctx.exception

    def test_lowerer_handles_inheritance_defs_recursion_and_nullable_fields(self) -> None:
        decl, lowered = self._lower_output_schema(
            """
            output schema BasePayload: "Base Payload"
                field kind: "Kind"
                    type: string
                    const: base_payload
                    note: "Stable kind."

                field summary: "Summary"
                    type: string

                def SharedWindow: "Shared Window"
                    type: object

                    field start: "Start"
                        type: string

                    field end: "End"
                        type: string

                def Node: "Node"
                    type: object

                    field label: "Label"
                        type: string

                    field next: "Next"
                        ref: Node
                        nullable

            output schema ChildPayload[BasePayload]: "Child Payload"
                inherit kind
                inherit summary
                inherit SharedWindow
                inherit Node

                field status: "Status"
                    type: enum
                    values:
                        ok
                        blocked
                    nullable
                    note: "Current status."

                field fixed_kind: "Fixed Kind"
                    type: string
                    const: child_payload
                    nullable
                    note: "Optional stable kind."

                field window: "Window"
                    ref: SharedWindow

                field tags: "Tags"
                    type: array
                    items: string
                    nullable

                field choice: "Choice"
                    any_of:
                        variant text:
                            type: string
                        variant count:
                            type: integer
                    nullable
            """,
            schema_name="ChildPayload",
        )

        self.assertIsNone(decl.parent_ref)
        self.assertEqual(
            [item.key for item in decl.items],
            [
                "kind",
                "summary",
                "SharedWindow",
                "Node",
                "status",
                "fixed_kind",
                "window",
                "tags",
                "choice",
            ],
        )

        self.assertEqual(lowered["title"], "Child Payload")
        self.assertEqual(lowered["type"], "object")
        self.assertEqual(lowered["additionalProperties"], False)
        self.assertEqual(
            list(lowered["properties"].keys()),
            ["kind", "summary", "status", "fixed_kind", "window", "tags", "choice"],
        )
        self.assertEqual(
            lowered["required"],
            ["kind", "summary", "status", "fixed_kind", "window", "tags", "choice"],
        )

        kind_schema = lowered["properties"]["kind"]
        self.assertEqual(kind_schema["type"], "string")
        self.assertEqual(kind_schema["const"], "base_payload")
        self.assertEqual(kind_schema["description"], "Stable kind.")

        status_schema = lowered["properties"]["status"]
        self.assertEqual(status_schema["type"], ["string", "null"])
        self.assertEqual(status_schema["enum"], ["ok", "blocked", None])
        self.assertEqual(status_schema["description"], "Current status.")

        fixed_kind_schema = lowered["properties"]["fixed_kind"]
        self.assertEqual(
            fixed_kind_schema["anyOf"],
            [
                {"type": "string", "const": "child_payload"},
                {"type": "null"},
            ],
        )
        self.assertEqual(fixed_kind_schema["description"], "Optional stable kind.")

        self.assertEqual(
            lowered["properties"]["window"],
            {
                "title": "Window",
                "$ref": "#/$defs/SharedWindow",
            },
        )
        self.assertEqual(
            lowered["properties"]["tags"],
            {
                "title": "Tags",
                "type": ["array", "null"],
                "items": {"type": "string"},
            },
        )
        self.assertEqual(
            lowered["properties"]["choice"]["anyOf"],
            [
                {"title": "text", "type": "string"},
                {"title": "count", "type": "integer"},
                {"type": "null"},
            ],
        )

        self.assertEqual(list(lowered["$defs"].keys()), ["SharedWindow", "Node"])
        self.assertEqual(
            lowered["$defs"]["SharedWindow"],
            {
                "title": "Shared Window",
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "start": {"title": "Start", "type": "string"},
                    "end": {"title": "End", "type": "string"},
                },
                "required": ["start", "end"],
            },
        )
        self.assertEqual(
            lowered["$defs"]["Node"]["properties"]["next"],
            {
                "title": "Next",
                "anyOf": [
                    {"$ref": "#/$defs/Node"},
                    {"type": "null"},
                ],
            },
        )

    def test_legacy_string_enum_form_lowers_like_new_inline_enum_values_form(self) -> None:
        _, new_lowered = self._lower_output_schema(
            """
            output schema StatusPayload: "Status Payload"
                field status: "Status"
                    type: enum
                    values:
                        ok
                        blocked
                    nullable
            """,
            schema_name="StatusPayload",
        )
        _, legacy_lowered = self._lower_output_schema(
            """
            output schema StatusPayload: "Status Payload"
                field status: "Status"
                    type: string
                    enum:
                        ok
                        blocked
                    nullable
            """,
            schema_name="StatusPayload",
        )

        self.assertEqual(new_lowered, legacy_lowered)
        self.assertEqual(
            new_lowered["properties"]["status"],
            {
                "title": "Status",
                "type": ["string", "null"],
                "enum": ["ok", "blocked", None],
            },
        )

    def test_malformed_inline_enum_forms_fail_loud(self) -> None:
        cases = (
            (
                "missing_values",
                """
                output schema BrokenPayload: "Broken Payload"
                    field status: "Status"
                        type: enum
                """,
                "E227",
                "missing `values:`",
            ),
            (
                "values_without_type_enum",
                """
                output schema BrokenPayload: "Broken Payload"
                    field status: "Status"
                        values:
                            ok
                            blocked
                """,
                "E228",
                "`values:` requires `type: enum`",
            ),
            (
                "string_type_with_values",
                """
                output schema BrokenPayload: "Broken Payload"
                    field status: "Status"
                        type: string
                        values:
                            ok
                            blocked
                """,
                "E228",
                "`values:` requires `type: enum`",
            ),
            (
                "enum_type_with_legacy_enum_block",
                """
                output schema BrokenPayload: "Broken Payload"
                    field status: "Status"
                        type: enum
                        enum:
                            ok
                            blocked
                """,
                "E229",
                "cannot be mixed",
            ),
        )

        for case_name, source, expected_code, expected_text in cases:
            with self.subTest(case=case_name):
                error = self._lower_output_schema_error(
                    source,
                    schema_name="BrokenPayload",
                )
                self.assertEqual(error.code, expected_code)
                self.assertIn(expected_text, str(error))

    def test_route_field_lowers_to_string_enum_wire_shape(self) -> None:
        _decl, lowered = self._lower_output_schema(
            """
            output schema WriterDecisionSchema: "Writer Decision Schema"
                route field next_route: "Next Route"
                    seek_muse: "Send to Muse." -> Muse
                    ready_for_critic: "Send to Critic." -> Critic
                    nullable
                    note: "Selected next step."

                field summary: "Summary"
                    type: string
            """,
            schema_name="WriterDecisionSchema",
        )

        self.assertEqual(
            lowered["properties"]["next_route"],
            {
                "title": "Next Route",
                "description": "Selected next step.",
                "type": ["string", "null"],
                "enum": ["seek_muse", "ready_for_critic", None],
            },
        )

    def test_route_field_defaults_to_non_null_wire_shape(self) -> None:
        _decl, lowered = self._lower_output_schema(
            """
            output schema WriterDecisionSchema: "Writer Decision Schema"
                route field next_route: "Next Route"
                    seek_muse: "Send to Muse." -> Muse
                    ready_for_critic: "Send to Critic." -> Critic
            """,
            schema_name="WriterDecisionSchema",
        )

        self.assertEqual(
            lowered["properties"]["next_route"],
            {
                "title": "Next Route",
                "type": "string",
                "enum": ["seek_muse", "ready_for_critic"],
            },
        )

    def test_route_field_rejects_mixed_primary_shape_owners(self) -> None:
        error = self._lower_output_schema_error(
            """
            output schema WriterDecisionSchema: "Writer Decision Schema"
                route field next_route: "Next Route"
                    type: string
                    seek_muse: "Send to Muse." -> Muse
                    ready_for_critic: "Send to Critic." -> Critic
            """,
            schema_name="WriterDecisionSchema",
        )

        self.assertIn("Route field cannot be combined with another primary shape", str(error))

    def test_route_field_rejects_retired_optional_flag(self) -> None:
        error = self._lower_output_schema_error(
            """
            output schema WriterDecisionSchema: "Writer Decision Schema"
                route field next_route: "Next Route"
                    seek_muse: "Send to Muse." -> Muse
                    optional
            """,
            schema_name="WriterDecisionSchema",
        )

        self.assertEqual(error.code, "E237")
        self.assertIn("Use `nullable`", str(error))

    def test_imported_parent_keeps_local_def_refs_local_after_rebind(self) -> None:
        decl, lowered = self._lower_output_schema(
            """
            import shared.base

            output schema ChildPayload[shared.base.BasePayload]: "Child Payload"
                inherit SharedNote
                inherit note

                field status: "Status"
                    type: string
            """,
            schema_name="ChildPayload",
            extra_files={
                "prompts/shared/base/AGENTS.prompt": """
                export output schema BasePayload: "Base Payload"
                    def SharedNote: "Shared Note"
                        type: object

                        field text: "Text"
                            type: string

                    field note: "Note"
                        ref: SharedNote
                """,
            },
        )

        self.assertIsNone(decl.parent_ref)
        self.assertEqual([item.key for item in decl.items], ["SharedNote", "note", "status"])
        self.assertEqual(
            lowered["properties"]["note"],
            {
                "title": "Note",
                "$ref": "#/$defs/SharedNote",
            },
        )
        self.assertEqual(
            lowered["$defs"]["SharedNote"],
            {
                "title": "Shared Note",
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "text": {"title": "Text", "type": "string"},
                },
                "required": ["text"],
            },
        )

    def test_retired_presence_flags_fail_loud(self) -> None:
        cases = (
            (
                "required_field",
                """
                output schema BrokenPayload: "Broken Payload"
                    field summary: "Summary"
                        type: string
                        required
                """,
                "E236",
                "Delete `required`",
            ),
            (
                "optional_field",
                """
                output schema BrokenPayload: "Broken Payload"
                    field next_route: "Next Route"
                        type: string
                        optional
                """,
                "E237",
                "Use `nullable`",
            ),
        )

        for case_name, source, expected_code, expected_text in cases:
            with self.subTest(case=case_name):
                error = self._lower_output_schema_error(
                    source,
                    schema_name="BrokenPayload",
                )
                self.assertEqual(error.code, expected_code)
                self.assertIn(expected_text, str(error))


if __name__ == "__main__":
    unittest.main()
