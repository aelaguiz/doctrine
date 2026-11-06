from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class ProseRenderTests(unittest.TestCase):
    def _render(self, source):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prompts" / "AGENTS.prompt"
            path.parent.mkdir()
            path.write_text(source)
            return render_markdown(CompilationSession(parse_file(path)).compile_agent("A"))

    def test_adjacent_strings_get_blank_line_in_each_surface(self):
        for source in (
            'agent A:\n    role: "Role"\n        "First."\n        "Second."\n',
            'agent A:\n    role: "Role."\n    work: "Work"\n        "First."\n        "Second."\n',
            'agent A:\n    role: "Role."\n    work: "Work"\n        section: "Section"\n            "First."\n            "Second."\n',
            'document D: "Doc"\n    "First."\n    "Second."\ninput I: "Input"\n    source: Prompt\n    shape: MarkdownDocument\n    requirement: Required\n    structure: D\nagent A:\n    role: "Role."\n    inputs: "Inputs"\n        I\n',
            'skill S: "Skill"\n    purpose: "Purpose."\n    "First."\n    "Second."\nagent A:\n    role: "Role."\n    skills: "Skills"\n        skill s: S\n',
            'agent A:\n    role: "Role."\n    work: "Work"\n        callout note: "Note"\n            "First."\n            "Second."\n',
        ):
            with self.subTest(source=source):
                rendered = self._render(source).replace("> ", "").replace("\n>\n", "\n\n")
                self.assertIn("First.\n\nSecond.", rendered)

    def test_multiline_string_keeps_inner_newlines(self):
        self.assertIn(
            "First.\nSecond.\n\nThird.",
            self._render('''agent A:
    role: "Role."
    work: "Work"
        """First.
Second."""
        "Third."
'''),
        )

    def test_e605_fence_split_across_strings(self):
        for source, owner in (
            (
                'agent A:\n    role: "Role."\n    work: "Work"\n'
                '        "```bash"\n        "make all"\n        "```"\n',
                "agent A slot work",
            ),
            (
                'agent A:\n    role: "Role."\n    work: "Work"\n'
                '        check: "Check"\n'
                '            "  ```bash"\n            "make all"\n            "```"\n',
                "agent A slot work.check",
            ),
            (
                'skill S: "Skill"\n    purpose: "```bash"\n'
                'agent A:\n    role: "Role."\n    skills: "Skills"\n        skill s: S\n',
                "skill S",
            ),
            (
                'skill S: "Skill"\n    purpose: "Purpose."\n'
                'agent A:\n    role: "Role."\n    skills: "Skills"\n'
                '        skill s: S\n            reason: "```bash"\n',
                "skill reference S",
            ),
        ):
            with self.subTest(owner=owner):
                with self.assertRaises(CompileError) as caught:
                    self._render(source)
                diagnostic = caught.exception.diagnostic
                self.assertEqual(diagnostic.code, "E605")
                self.assertEqual(diagnostic.summary, "Code fence split across strings")
                self.assertEqual(
                    diagnostic.detail,
                    f"A string in {owner} opens a code fence it doesn't close.",
                )
                self.assertEqual(
                    diagnostic.hints,
                    ('Put the whole fence in one `"""` string, or use a `code` block.',),
                )

    def test_fence_whole_in_one_string_compiles(self):
        result = self._render('''agent A:
    role: "Role."
    work: "Work"
        """```bash
make all
```"""
''')
        self.assertIn("```bash\nmake all\n```", result)

    def test_list_strings_become_a_loose_list(self):
        result = self._render('''agent A:
    role: "Role."
    work: "Work"
        "- First"
        "- Second"
''')
        self.assertIn("- First\n\n- Second", result)

    def test_section_metadata_only_with_requirement(self):
        source = """agent A:
    role: "Role."
    work: "Work"
        step: "Step"
            section check: "Check"%s
                "Check it."
"""
        self.assertNotIn("_section_", self._render(source % ""))
        self.assertIn("_Required · section_", self._render(source % " required"))

    def test_paragraph_title_runs_in(self):
        result = self._render("""agent A:
    role: "Role."
    work: "Work"
        paragraph lead: "Read this."
            "First."
            "Second."
""")
        self.assertIn("**Read this.** First.\n\nSecond.", result)

    def test_untitled_paragraph_has_no_heading(self):
        result = self._render("""agent A:
    role: "Role."
    work: "Work"
        paragraph lead:
            "First."
""")
        self.assertEqual(result, "Role.\n\n## Work\n\nFirst.\n")

    def test_paragraph_renders_in_document(self):
        result = self._render("""document D: "Doc"
    paragraph lead: "Read this."
        "First."
        "Second."
input I: "Input"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
    structure: D
agent A:
    role: "Role."
    inputs: "Inputs"
        I
""")
        self.assertIn("**Read this.** First.\n\nSecond.", result)

    def test_generated_lines_keep_their_layout(self):
        path = Path(__file__).resolve().parents[1] / (
            "examples/104_review_final_output_output_schema_blocked_control_ready/"
            "prompts/AGENTS.prompt"
        )
        rendered = render_markdown(
            CompilationSession(parse_file(path)).compile_agent("AcceptanceReviewBlockedJsonDemo")
        )
        self.assertIn('''```json
{
  "verdict": "changes_requested",
  "reviewed_artifact": "Draft Plan",
  "current_artifact": null,
  "next_owner": null,
  "blocked_gate": "The review basis is missing."
}
```''', rendered)
        self.assertIn(
            "> **Final answer contract**\n"
            "> End the turn with one final assistant message that follows this schema.",
            rendered,
        )
        self.assertIn(
            "- Source: File\n- Path: `unit_root/DRAFT_PLAN.md`\n"
            "- Shape: Markdown Document\n- Requirement: Required",
            rendered,
        )
