from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine import model
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.session import CompilationSession
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
                unit=session.root_unit,
            )
            return decl, context._lower_output_schema_decl(decl, unit=unit)

    def test_lowerer_handles_inheritance_defs_recursion_and_nullable_fields(self) -> None:
        decl, lowered = self._lower_output_schema(
            """
            output schema BasePayload: "Base Payload"
                field kind: "Kind"
                    type: string
                    const: base_payload
                    required
                    note: "Stable kind."

                field summary: "Summary"
                    type: string
                    required

                def SharedWindow: "Shared Window"
                    type: object

                    field start: "Start"
                        type: string
                        required

                    field end: "End"
                        type: string
                        required

                def Node: "Node"
                    type: object

                    field label: "Label"
                        type: string
                        required

                    field next: "Next"
                        ref: Node
                        optional

            output schema ChildPayload[BasePayload]: "Child Payload"
                inherit kind
                inherit summary
                inherit SharedWindow
                inherit Node

                field status: "Status"
                    type: string
                    enum:
                        ok
                        blocked
                    optional
                    note: "Current status."

                field window: "Window"
                    ref: SharedWindow
                    required

                field tags: "Tags"
                    type: array
                    items: string
                    optional

                field choice: "Choice"
                    any_of:
                        variant text:
                            type: string
                        variant count:
                            type: integer
                    optional
            """,
            schema_name="ChildPayload",
        )

        self.assertIsNone(decl.parent_ref)
        self.assertEqual([item.key for item in decl.items], ["kind", "summary", "SharedWindow", "Node", "status", "window", "tags", "choice"])

        self.assertEqual(lowered["title"], "Child Payload")
        self.assertEqual(lowered["type"], "object")
        self.assertEqual(lowered["additionalProperties"], False)
        self.assertEqual(
            list(lowered["properties"].keys()),
            ["kind", "summary", "status", "window", "tags", "choice"],
        )
        self.assertEqual(
            lowered["required"],
            ["kind", "summary", "status", "window", "tags", "choice"],
        )

        kind_schema = lowered["properties"]["kind"]
        self.assertEqual(kind_schema["type"], "string")
        self.assertEqual(kind_schema["const"], "base_payload")
        self.assertEqual(kind_schema["description"], "Stable kind.")

        status_schema = lowered["properties"]["status"]
        self.assertEqual(status_schema["type"], ["string", "null"])
        self.assertEqual(status_schema["enum"], ["ok", "blocked"])
        self.assertEqual(status_schema["description"], "Current status.")

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

    def test_imported_parent_keeps_local_def_refs_local_after_rebind(self) -> None:
        decl, lowered = self._lower_output_schema(
            """
            import shared.base

            output schema ChildPayload[shared.base.BasePayload]: "Child Payload"
                inherit SharedNote
                inherit note

                field status: "Status"
                    type: string
                    required
            """,
            schema_name="ChildPayload",
            extra_files={
                "prompts/shared/base.prompt": """
                output schema BasePayload: "Base Payload"
                    def SharedNote: "Shared Note"
                        type: object

                        field text: "Text"
                            type: string
                            required

                    field note: "Note"
                        ref: SharedNote
                        required
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


if __name__ == "__main__":
    unittest.main()
