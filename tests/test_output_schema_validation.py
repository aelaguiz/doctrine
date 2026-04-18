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


class OutputSchemaValidationTests(unittest.TestCase):
    def _new_context(self, source: str | None = None) -> CompilationContext:
        prompt_source = source or """
        agent Demo:
            role: "Answer plainly."
            workflow: "Reply"
                "Reply and stop."
        """
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        prompt_path = root / "prompts" / "AGENTS.prompt"
        prompt_path.parent.mkdir(parents=True)
        prompt_path.write_text(textwrap.dedent(prompt_source), encoding="utf-8")
        prompt = parse_file(prompt_path)
        return CompilationContext(CompilationSession(prompt))

    def test_validator_rejects_invalid_draft_2020_12_schema(self) -> None:
        context = self._new_context()

        with self.assertRaises(CompileError) as ctx:
            context._validate_final_output_lowered_schema(
                {"type": "definitely_not_a_real_json_schema_type"},
                owner_label="output schema BrokenPayload",
            )

        self.assertEqual(ctx.exception.code, "E217")
        self.assertIn("Draft 2020-12", str(ctx.exception))

    def test_validator_rejects_root_any_of(self) -> None:
        context = self._new_context()

        with self.assertRaises(CompileError) as ctx:
            context._validate_final_output_lowered_schema(
                {
                    "anyOf": [
                        {"type": "object", "additionalProperties": False, "properties": {}, "required": []},
                        {"type": "null"},
                    ]
                },
                owner_label="output schema BrokenPayload",
            )

        self.assertEqual(ctx.exception.code, "E218")
        self.assertIn("root schema cannot use `anyOf`", str(ctx.exception))

    def test_validator_rejects_missing_additional_properties_false(self) -> None:
        context = self._new_context()

        with self.assertRaises(CompileError) as ctx:
            context._validate_final_output_lowered_schema(
                {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                    },
                    "required": ["summary"],
                },
                owner_label="output schema BrokenPayload",
            )

        self.assertEqual(ctx.exception.code, "E218")
        self.assertIn("additionalProperties: false", str(ctx.exception))

    def test_validator_rejects_unsupported_keywords(self) -> None:
        context = self._new_context()

        with self.assertRaises(CompileError) as ctx:
            context._validate_final_output_lowered_schema(
                {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "summary": {"type": "string"},
                    },
                    "required": ["summary"],
                    "patternProperties": {
                        ".*": {"type": "string"},
                    },
                },
                owner_label="output schema BrokenPayload",
            )

        self.assertEqual(ctx.exception.code, "E218")
        self.assertIn("unsupported keyword `patternProperties`", str(ctx.exception))

    def test_validator_accepts_nullable_and_recursive_lowered_schema(self) -> None:
        context = self._new_context(
            """
            output schema RecursivePayload: "Recursive Payload"
                field root: "Root"
                    ref: Node

                def Node: "Node"
                    type: object

                    field label: "Label"
                        type: string

                    field next: "Next"
                        ref: Node
                        nullable

            agent Demo:
                role: "Answer plainly."
                workflow: "Reply"
                    "Reply and stop."
            """
        )

        unit, decl = context._resolve_output_schema_decl(
            model.NameRef(module_parts=(), declaration_name="RecursivePayload"),
            unit=context.root_entrypoint_unit,
        )
        lowered = context._lower_output_schema_decl(decl, unit=unit)

        context._validate_final_output_lowered_schema(
            lowered,
            owner_label="output schema RecursivePayload",
        )
        context._validate_final_output_example_instance(
            {
                "root": {
                    "label": "start",
                    "next": None,
                }
            },
            lowered,
            owner_label="output schema RecursivePayload",
        )

    def test_validator_rejects_example_instance_that_does_not_match_lowered_schema(self) -> None:
        context = self._new_context()
        lowered = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "summary": {"type": "string"},
            },
            "required": ["summary"],
        }

        with self.assertRaises(CompileError) as ctx:
            context._validate_final_output_example_instance(
                {"summary": 7},
                lowered,
                owner_label="output schema BrokenPayload",
            )

        self.assertEqual(ctx.exception.code, "E216")
        self.assertIn("output schema BrokenPayload", str(ctx.exception))

    def test_validator_allows_up_to_one_thousand_enum_values(self) -> None:
        context = self._new_context()
        values = [f"v{index}" for index in range(1000)]
        lowered = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "choice": {"type": "string", "enum": values},
            },
            "required": ["choice"],
        }

        context._validate_final_output_lowered_schema(
            lowered,
            owner_label="output schema EnumPayload",
        )

    def test_validator_rejects_excessive_nesting(self) -> None:
        context = self._new_context()
        schema: dict[str, object] = {
            "type": "object",
            "additionalProperties": False,
            "properties": {},
            "required": [],
        }
        current = schema
        for level in range(6):
            child = {
                "type": "object",
                "additionalProperties": False,
                "properties": {},
                "required": [],
            }
            current["properties"] = {f"level_{level}": child}
            current["required"] = [f"level_{level}"]
            current = child

        with self.assertRaises(CompileError) as ctx:
            context._validate_final_output_lowered_schema(
                schema,
                owner_label="output schema TooDeepPayload",
            )

        self.assertEqual(ctx.exception.code, "E218")
        self.assertIn("nesting exceeds 5 levels", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
