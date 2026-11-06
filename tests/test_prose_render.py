from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
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
        ):
            with self.subTest(source=source):
                self.assertIn("First.\n\nSecond.", self._render(source))

    def test_multiline_string_keeps_inner_newlines(self):
        self.assertIn("First.\nSecond.\n\nThird.", self._render('''agent A:
    role: "Role."
    work: "Work"
        """First.
Second."""
        "Third."
'''))

    def test_section_metadata_only_with_requirement(self):
        source = '''agent A:
    role: "Role."
    work: "Work"
        step: "Step"
            section check: "Check"%s
                "Check it."
'''
        self.assertNotIn("_section_", self._render(source % ""))
        self.assertIn("_Required · section_", self._render(source % " required"))

    def test_paragraph_title_runs_in(self):
        result = self._render('''agent A:
    role: "Role."
    work: "Work"
        paragraph lead: "Read this."
            "First."
            "Second."
''')
        self.assertIn("**Read this.** First.\n\nSecond.", result)

    def test_untitled_paragraph_has_no_heading(self):
        result = self._render('''agent A:
    role: "Role."
    work: "Work"
        paragraph lead:
            "First."
''')
        self.assertEqual(result, "Role.\n\n## Work\n\nFirst.\n")
