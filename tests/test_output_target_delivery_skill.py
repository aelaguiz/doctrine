from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine import model
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError, ParseError
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class OutputTargetDeliverySkillTests(unittest.TestCase):
    def _write_prompt(
        self,
        root: Path,
        source: str,
        *,
        rel_path: str = "prompts/AGENTS.prompt",
    ) -> Path:
        prompt_path = root / rel_path
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
        return prompt_path

    def _compile_agent(
        self,
        source: str,
        *,
        agent_name: str,
        extra_files: dict[str, str] | None = None,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(root, source)
            for rel_path, contents in (extra_files or {}).items():
                self._write_prompt(root, contents, rel_path=rel_path)
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

    def test_output_target_parses_delivery_skill_as_typed_ref(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """
                skill NoteDelivery: "note-delivery"
                    purpose: "Append a note."

                output target IssueNoteAppend: "Issue Note Append"
                    delivery_skill: NoteDelivery
                    required: "Required"
                        note_id: "Note ID"
                """,
            )

            prompt = parse_file(prompt_path)

        target = next(
            decl
            for decl in prompt.declarations
            if isinstance(decl, model.OutputTargetDecl)
        )
        self.assertIsInstance(target.delivery_skill_ref, model.NameRef)
        self.assertEqual(target.delivery_skill_ref.declaration_name, "NoteDelivery")
        self.assertEqual(target.items[0].key, "required")

    def test_delivery_skill_renders_after_target_and_before_config_rows(self) -> None:
        agent = self._compile_agent(
            """
            skill NoteDelivery: "note-delivery"
                purpose: "Append a note."

            output target IssueNoteAppend: "Issue Note Append"
                delivery_skill: NoteDelivery
                required: "Required"
                    note_id: "Note ID"

            output IssueNote: "Issue Note"
                target: IssueNoteAppend
                    note_id: "N-123"
                shape: MarkdownDocument
                requirement: Advisory

            agent Demo:
                role: "Write the note."
                outputs: "Outputs"
                    IssueNote
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("| Delivered Via | `note-delivery` |", rendered)
        self.assertLess(
            rendered.index("| Target | Issue Note Append |"),
            rendered.index("| Delivered Via | `note-delivery` |"),
        )
        self.assertLess(
            rendered.index("| Delivered Via | `note-delivery` |"),
            rendered.index("| Note ID | `N-123` |"),
        )

    def test_config_only_targets_do_not_render_delivered_via(self) -> None:
        agent = self._compile_agent(
            """
            output PlainFile: "Plain File"
                target: File
                    path: "notes.md"
                shape: MarkdownDocument
                requirement: Required

            agent Demo:
                role: "Write the note."
                outputs: "Outputs"
                    PlainFile
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("| Target | File |", rendered)
        self.assertNotIn("Delivered Via", rendered)

    def test_imported_target_resolves_delivery_skill_from_target_module(self) -> None:
        agent = self._compile_agent(
            """
            import shared.delivery

            output LocalNote: "Local Note"
                target: shared.delivery.IssueNoteAppend
                    note_id: "N-456"
                shape: MarkdownDocument
                requirement: Required

            agent Demo:
                role: "Write the note."
                outputs: "Outputs"
                    LocalNote
            """,
            agent_name="Demo",
            extra_files={
                "prompts/shared/delivery.prompt": """
                skill NoteDelivery: "note-delivery"
                    purpose: "Append a note."

                output target IssueNoteAppend: "Issue Note Append"
                    delivery_skill: NoteDelivery
                    required: "Required"
                        note_id: "Note ID"
                """,
            },
        )

        rendered = render_markdown(agent)
        self.assertIn("| Target | Issue Note Append |", rendered)
        self.assertIn("| Delivered Via | `note-delivery` |", rendered)
        self.assertIn("| Note ID | `N-456` |", rendered)

    def test_unknown_delivery_skill_fails_loud_when_target_is_used(self) -> None:
        error = self._compile_error(
            """
            output target IssueNoteAppend: "Issue Note Append"
                delivery_skill: MissingSkill

            output IssueNote: "Issue Note"
                target: IssueNoteAppend
                shape: MarkdownDocument
                requirement: Required

            agent Demo:
                role: "Write the note."
                outputs: "Outputs"
                    IssueNote
            """,
            agent_name="Demo",
        )

        self.assertIn("Missing local skill declaration: MissingSkill", str(error))

    def test_duplicate_delivery_skill_fails_during_parse(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """
                skill FirstDelivery: "first-delivery"
                    purpose: "Append a note."

                skill SecondDelivery: "second-delivery"
                    purpose: "Append another note."

                output target IssueNoteAppend: "Issue Note Append"
                    delivery_skill: FirstDelivery
                    delivery_skill: SecondDelivery
                """,
            )

            with self.assertRaises(ParseError) as ctx:
                parse_file(prompt_path)

        self.assertIn("may define `delivery_skill:` only once", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
