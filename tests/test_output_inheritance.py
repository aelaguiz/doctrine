from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class OutputInheritanceTests(unittest.TestCase):
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

    def test_output_inheritance_can_keep_shared_handoff_shape_and_add_local_field(self) -> None:
        agent = self._compile_agent(
            """
            output BaseHandoff: "Base Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

                must_include: "Must Include"
                    what_changed: "What Changed"
                        "Say what changed."

                standalone_read: "Standalone Read"
                    "The note should stand on its own."

            output LessonsLeadOutput[BaseHandoff]: "Lessons Lead Output"
                inherit target
                inherit shape
                inherit requirement
                inherit must_include
                inherit standalone_read

                hit: "Test"
                    "blah blah blah"

            agent Demo:
                role: "Emit the inherited handoff output."
                outputs: "Outputs"
                    LessonsLeadOutput
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("### Lessons Lead Output", rendered)
        self.assertIn("#### Must Include", rendered)
        self.assertIn("##### What Changed", rendered)
        self.assertIn("#### Test", rendered)
        self.assertIn("blah blah blah", rendered)

    def test_output_inheritance_can_use_imported_parent_output(self) -> None:
        agent = self._compile_agent(
            """
            import shared.base

            output LessonsLeadOutput[shared.base.BaseHandoff]: "Lessons Lead Output"
                inherit target
                inherit shape
                inherit requirement
                inherit must_include
                inherit standalone_read

                hit: "Test"
                    "blah blah blah"

            agent Demo:
                role: "Emit the imported inherited handoff output."
                outputs: "Outputs"
                    LessonsLeadOutput
            """,
            agent_name="Demo",
            extra_files={
                "prompts/shared/base.prompt": """
                output target IssueComment: "Issue Note"
                    note: "Target Note"

                output shape LessonsIssueNoteText: "Lessons Issue Note Text"
                    kind: Comment

                output BaseHandoff: "Base Handoff"
                    target: IssueComment
                    shape: LessonsIssueNoteText
                    requirement: Required

                    must_include: "Must Include"
                        what_changed: "What Changed"
                            "Say what changed."

                    standalone_read: "Standalone Read"
                        "The note should stand on its own."
                """,
            },
        )

        rendered = render_markdown(agent)
        self.assertIn("### Lessons Lead Output", rendered)
        self.assertIn("- Target: Issue Note", rendered)
        self.assertIn("- Shape: Lessons Issue Note Text", rendered)
        self.assertIn("#### Test", rendered)

    def test_imported_output_inheritance_keeps_parent_owned_item_and_attachment_refs(self) -> None:
        agent = self._compile_agent(
            """
            import shared.base

            output LessonsLeadSchemaOutput[shared.base.BaseSchemaHandoff]: "Lessons Lead Schema Output"
                inherit target
                inherit shape
                inherit render_profile
                inherit schema
                inherit requirement

                hit: "Test"
                    "blah blah blah"

            output LessonsLeadStructureOutput[shared.base.BaseStructureHandoff]: "Lessons Lead Structure Output"
                inherit target
                inherit shape
                inherit render_profile
                inherit structure
                inherit requirement
                inherit must_include
                inherit standalone_read

                hit: "Test"
                    "blah blah blah"

            agent Demo:
                role: "Emit the imported inherited handoff output."
                outputs: "Outputs"
                    LessonsLeadSchemaOutput
                    LessonsLeadStructureOutput
            """,
            agent_name="Demo",
            extra_files={
                "prompts/shared/base.prompt": """
                render_profile CompactComment:
                    properties -> sentence

                output target IssueComment: "Issue Note"
                    note: "Target Note"

                output shape LessonsDocumentShape: "Lessons Document Shape"
                    kind: MarkdownDocument

                schema HandoffSchema: "Handoff Schema"
                    sections:
                        summary: "Summary"

                document HandoffStructure: "Handoff Structure"
                    section summary: "Summary"
                        "Summarize the current state."

                output BaseSchemaHandoff: "Base Schema Handoff"
                    target: IssueComment
                    shape: LessonsDocumentShape
                    render_profile: CompactComment
                    schema: HandoffSchema
                    requirement: Required

                output BaseStructureHandoff: "Base Structure Handoff"
                    target: IssueComment
                    shape: LessonsDocumentShape
                    render_profile: CompactComment
                    structure: HandoffStructure
                    requirement: Required

                    must_include: "Must Include"
                        what_changed: "What Changed"
                            "Say what changed."

                    standalone_read: "Standalone Read"
                        "The note should stand on its own."
                """,
            },
        )

        rendered = render_markdown(agent)
        self.assertIn("- Target: Issue Note", rendered)
        self.assertIn("- Shape: Lessons Document Shape", rendered)
        self.assertIn("- Schema: Handoff Schema", rendered)
        self.assertIn("- Structure: Handoff Structure", rendered)
        self.assertIn("### Lessons Lead Schema Output", rendered)
        self.assertIn("### Lessons Lead Structure Output", rendered)
        self.assertIn("#### Test", rendered)

    def test_missing_inherited_output_entry_fails_loud(self) -> None:
        error = self._compile_error(
            """
            output BaseHandoff: "Base Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

                must_include: "Must Include"
                    what_changed: "What Changed"
                        "Say what changed."

            output LessonsLeadOutput[BaseHandoff]: "Lessons Lead Output"
                inherit target
                inherit shape
                inherit requirement

            agent Demo:
                role: "Fail loud when the child skips an inherited output entry."
                outputs: "Outputs"
                    LessonsLeadOutput
            """,
            agent_name="Demo",
        )

        self.assertEqual(error.code, "E003")
        self.assertIn("Missing inherited output entry", str(error))
        self.assertIn("must_include", str(error))

    def test_inheriting_undefined_output_key_fails_loud(self) -> None:
        error = self._compile_error(
            """
            output BaseHandoff: "Base Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

            output LessonsLeadOutput[BaseHandoff]: "Lessons Lead Output"
                inherit target
                inherit shape
                inherit requirement
                inherit current_truth

            agent Demo:
                role: "Fail loud when the child inherits a missing key."
                outputs: "Outputs"
                    LessonsLeadOutput
            """,
            agent_name="Demo",
        )

        self.assertEqual(error.code, "E253")
        self.assertIn("cannot inherit undefined key `current_truth`", str(error))

    def test_output_patch_without_parent_fails_loud(self) -> None:
        error = self._compile_error(
            """
            output LessonsLeadOutput: "Lessons Lead Output"
                inherit target
                target: TurnResponse
                shape: Comment
                requirement: Required

            agent Demo:
                role: "Fail loud when output patch syntax appears without a parent."
                outputs: "Outputs"
                    LessonsLeadOutput
            """,
            agent_name="Demo",
        )

        self.assertEqual(error.code, "E252")
        self.assertIn("requires an inherited output", str(error))
        self.assertIn("target", str(error))

    def test_inherited_output_parent_cannot_have_unkeyed_top_level_prose(self) -> None:
        error = self._compile_error(
            """
            output BaseHandoff: "Base Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required
                "Late prose"

            output LessonsLeadOutput[BaseHandoff]: "Lessons Lead Output"
                inherit target
                inherit shape
                inherit requirement

            agent Demo:
                role: "Fail loud when the parent output has unkeyed prose."
                outputs: "Outputs"
                    LessonsLeadOutput
            """,
            agent_name="Demo",
        )

        self.assertEqual(error.code, "E254")
        self.assertIn("contains unkeyed top-level items", str(error))

    def test_output_override_kind_mismatch_fails_loud(self) -> None:
        error = self._compile_error(
            """
            output BaseHandoff: "Base Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

                must_include: "Must Include"
                    what_changed: "What Changed"
                        "Say what changed."

            output LessonsLeadOutput[BaseHandoff]: "Lessons Lead Output"
                inherit target
                inherit shape
                inherit requirement
                override must_include: TurnResponse

            agent Demo:
                role: "Fail loud when output override kind does not match the parent."
                outputs: "Outputs"
                    LessonsLeadOutput
            """,
            agent_name="Demo",
        )

        self.assertEqual(error.code, "E255")
        self.assertIn("overrides entry `must_include` with the wrong kind", str(error))
