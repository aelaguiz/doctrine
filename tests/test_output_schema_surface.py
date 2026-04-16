from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine import model
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file, parse_text
from doctrine.renderer import render_markdown


class OutputSchemaSurfaceTests(unittest.TestCase):
    def _compile_agent(
        self,
        source: str,
        *,
        agent_name: str,
        extra_files: dict[str, str] | None = None,
    ):
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
            return CompilationSession(prompt).compile_agent(agent_name)

    def _compile_error(
        self,
        source: str,
        *,
        agent_name: str,
        extra_files: dict[str, str] | None = None,
    ) -> CompileError:
        with self.assertRaises(CompileError) as ctx:
            self._compile_agent(
                source,
                agent_name=agent_name,
                extra_files=extra_files,
            )
        return ctx.exception

    def test_parser_builds_output_schema_nodes_and_nested_items(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """
            output schema BasePayload: "Base Payload"
                field kind: "Kind"
                    type: string
                    required

                def SharedNote: "Shared Note"
                    type: object

                    field text: "Text"
                        type: string

                example:
                    kind: "base_payload"
                    shared_note:
                        text: "hello"

            output schema ChildPayload[BasePayload]: "Child Payload"
                inherit kind
                inherit SharedNote
                inherit example

                override field kind: "Kind"
                    type: string
                    const: "child_payload"

                field status: "Status"
                    type: string
                    optional

                override example:
                    kind: "child_payload"
                    shared_note:
                        text: "hello"
                    status: "ready"
                """
            )
        )

        self.assertEqual(len(prompt.declarations), 2)

        base_decl = prompt.declarations[0]
        self.assertIsInstance(base_decl, model.OutputSchemaDecl)
        self.assertEqual(base_decl.name, "BasePayload")
        self.assertIsNone(base_decl.parent_ref)
        self.assertIsInstance(base_decl.items[0], model.OutputSchemaField)
        self.assertIsInstance(base_decl.items[1], model.OutputSchemaDef)
        self.assertIsInstance(base_decl.items[2], model.OutputSchemaExample)

        shared_note = base_decl.items[1]
        self.assertIsInstance(shared_note, model.OutputSchemaDef)
        self.assertEqual(shared_note.key, "SharedNote")
        self.assertEqual(len(shared_note.items), 2)
        self.assertIsInstance(shared_note.items[1], model.OutputSchemaField)
        example = base_decl.items[2]
        self.assertIsInstance(example, model.OutputSchemaExample)
        self.assertEqual(example.key, "example")
        self.assertEqual(example.value.entries[0].key, "kind")

        child_decl = prompt.declarations[1]
        self.assertIsInstance(child_decl, model.OutputSchemaDecl)
        self.assertIsNotNone(child_decl.parent_ref)
        self.assertEqual(child_decl.parent_ref.declaration_name, "BasePayload")
        self.assertIsInstance(child_decl.items[0], model.InheritItem)
        self.assertIsInstance(child_decl.items[1], model.InheritItem)
        self.assertIsInstance(child_decl.items[2], model.InheritItem)
        self.assertIsInstance(child_decl.items[3], model.OutputSchemaOverrideField)
        self.assertIsInstance(child_decl.items[4], model.OutputSchemaField)
        self.assertIsInstance(child_decl.items[5], model.OutputSchemaOverrideExample)

    def test_local_inherited_output_shape_keeps_inherited_items_and_points_schema_at_output_schema(self) -> None:
        agent = self._compile_agent(
            """
            output schema BasePayload: "Base Payload"
                field kind: "Kind"
                    type: string
                    required

                example:
                    kind: "base_payload"

            output schema ChildPayload[BasePayload]: "Child Payload"
                inherit kind

                field status: "Status"
                    type: string
                    required

                override example:
                    kind: "base_payload"
                    status: "ready"

            output shape BaseJson: "Base JSON"
                kind: JsonObject
                schema: BasePayload

                field_notes: "Field Notes"
                    "Use the shared payload shell."

            output shape ChildJson[BaseJson]: "Child JSON"
                inherit kind
                override schema: ChildPayload
                inherit field_notes

            output ChildResponse: "Child Response"
                target: TurnResponse
                shape: ChildJson
                requirement: Required

                details: "Details"
                    "Schema title: {{ChildJson:schema.title}}"
                    "Kind title: {{ChildJson:kind.title}}"
                    "Notes title: {{ChildJson:field_notes.title}}"

            agent Demo:
                role: "Emit the child response."
                outputs: "Outputs"
                    ChildResponse
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("Schema title: Child Payload", rendered)
        self.assertIn("Kind title: Json Object", rendered)
        self.assertIn("Notes title: Field Notes", rendered)

    def test_imported_inherited_output_shape_rebinds_parent_output_schema_ref(self) -> None:
        agent = self._compile_agent(
            """
            import shared.base

            output shape ChildJson[shared.base.BaseJson]: "Child JSON"
                inherit kind
                inherit schema
                inherit field_notes

            output ChildResponse: "Child Response"
                target: TurnResponse
                shape: ChildJson
                requirement: Required

                details: "Details"
                    "Schema title: {{ChildJson:schema.title}}"
                    "Notes title: {{ChildJson:field_notes.title}}"

            agent Demo:
                role: "Emit the child response."
                outputs: "Outputs"
                    ChildResponse
            """,
            agent_name="Demo",
            extra_files={
                "prompts/shared/base.prompt": """
                output schema BasePayload: "Shared Base Payload Title"
                    field kind: "Kind"
                        type: string
                        required

                    example:
                        kind: "shared_base"

                output shape BaseJson: "Base JSON"
                    kind: JsonObject
                    schema: BasePayload

                    field_notes: "Field Notes"
                        "Use the shared payload shell."
                """,
            },
        )

        rendered = render_markdown(agent)
        self.assertIn("Schema title: Shared Base Payload Title", rendered)
        self.assertIn("Notes title: Field Notes", rendered)

    def test_inherited_output_schema_example_stays_explicit_when_parent_has_none(self) -> None:
        error = self._compile_error(
            """
            output schema BasePayload: "Base Payload"
                field kind: "Kind"
                    type: string
                    required

            output schema ChildPayload[BasePayload]: "Child Payload"
                inherit kind
                inherit example

            output shape ChildJson: "Child JSON"
                kind: JsonObject
                schema: ChildPayload

            output ChildResponse: "Child Response"
                target: TurnResponse
                shape: ChildJson
                requirement: Required

            agent Demo:
                role: "Emit the child response."
                outputs: "Outputs"
                    ChildResponse
                final_output: ChildResponse
            """,
            agent_name="Demo",
        )

        # Child schemas must not silently invent sample data when a parent
        # never declared an example to inherit.
        self.assertIn("Cannot inherit undefined output schema entry", str(error))


if __name__ == "__main__":
    unittest.main()
