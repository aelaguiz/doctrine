from __future__ import annotations

import unittest

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.emit_common import load_emit_targets
from doctrine.homes import HEADER, compile_homes
from doctrine.parser import parse_file
from tests.ws3_support import HomeProject


class DetailsTests(HomeProject, unittest.TestCase):
    def test_details_override_keeps_its_lexical_owner(self):
        source = '''workflow Parent: "Parent"
    details cases: "Cases"
        "Old case."
workflow Child[Parent]: "Child"
    override details cases:
        "New case."
team T: "Team"
    home: "t"
    work: Child
'''
        root = self.project(source)
        code, _, error = self.cli(root, 'build', '.')
        self.assertEqual(code, 0, error)
        companion = (root / '_details/child.md').read_text()
        self.assertIn('## Child\n\n### Cases\n\nNew case.', companion)
        self.assertNotIn('Old case.', companion)
        self.assertFalse((root / '_details/parent.md').exists())
        path = root / 'prompts/AGENTS.prompt'
        path.write_text(source.replace('override details cases:', 'override details absent:'))
        code, _, error = self.cli(root, 'build', '.')
        self.assertEqual(code, 1)
        self.assertIn('E001', error)

    def test_details_inside_guard_move_to_companion(self):
        root = self.project('''enum State: "State"
    ready: "Ready"
team T: "Team"
    home: "t"
    work: "Work"
        guard follow_up when State.ready == State.ready
            "Brief."
            details:
                "Long case."
''')
        code, _, error = self.cli(root, 'build', '.')
        self.assertEqual(code, 0, error)
        home = (root / 't/AGENTS.md').read_text()
        self.assertNotIn('Long case.', home)
        self.assertIn('Brief.', home)
        companion = (root / 't/DETAILS.md').read_text()
        self.assertIn('## Work\n\n### Follow Up\n\nLong case.', companion)

    def test_owner_table(self):
        cases = (
            ('team T: "Team"\n    home: "t"\n    work: "Work"\n        details:\n            "Long case."\n', 't/DETAILS.md'),
            ('team T: "Team"\n    home: "t"\n    member qa: "QA"\n        role: "Test."\n        work: "Work"\n            details:\n                "Long case."\n', 't/qa/DETAILS.md'),
            ('agent A:\n    role: "Test."\n    work: "Work"\n        details:\n            "Long case."\n', 'a/DETAILS.md'),
            ('abstract agent CraftRole:\n    role: "Test."\n    work: "Work"\n        details:\n            "Long case."\nteam T: "Team"\n    home: "t"\n    member qa[CraftRole]: "QA"\n', '_details/craft-role.md'),
            ('abstract team BaseTeam:\n    work: "Work"\n        details:\n            "Long case."\nteam T[BaseTeam]: "Team"\n    home: "t"\n', '_details/base-team.md'),
            ('workflow W: "Work"\n    details:\n        "Long case."\nteam T: "Team"\n    home: "t"\n    work: W\n', '_details/w.md'),
            ('document D: "Document"\n    details:\n        "Long case."\ninput I: "Input"\n    source: Prompt\n    shape: MarkdownDocument\n    requirement: Required\n    structure: D\nagent A:\n    role: "Test."\n    inputs: "Inputs"\n        I\n', '_details/d.md'),
        )
        for source, companion in cases:
            with self.subTest(companion=companion):
                root = self.project(source)
                code, _, error = self.cli(root, 'build', '.', '--target', 'homes')
                self.assertEqual(code, 0, error)
                self.assertTrue((root / companion).is_file(), companion)
                self.assertIn('Long case.', (root / companion).read_text())

    def test_e620_in_skill_package(self):
        root = self.project('skill package S: "Skill"\n    details:\n        "Long case."\n')
        session = CompilationSession(parse_file(root / 'prompts/AGENTS.prompt'))
        with self.assertRaises(CompileError) as caught:
            session.compile_skill_package('S')
        self.assertEqual(caught.exception.code, 'E620')

    def test_one_pointer_line_per_home(self):
        root = self.project(example='182_shared_details')
        self.assertEqual(self.cli(root, 'build', '.')[0], 0)
        text = (root / 'pods/growth/qa/AGENTS.md').read_text()
        self.assertEqual(text.count('Fuller cases,'), 1)
        self.assertLess(text.index('[_details/habits.md]'), text.index('[_details/waiter.md]'))

    def test_companion_keeps_headings_and_depth(self):
        root = self.project('''team T: "Team"
    home: "t"
    work: "Work"
        step: "Step"
            details old: "Old case"
                "Long case."
''')
        self.assertEqual(self.cli(root, 'build', '.')[0], 0)
        text = (root / 't/DETAILS.md').read_text()
        self.assertEqual(text[HEADER.match(text).end():], '## Work\n\n### Step\n\n#### Old case\n\nLong case.\n')

    def test_repeat_headings_get_suffix_anchors(self):
        root = self.project('''team T: "Team"
    home: "t"
    first: "Same"
        details old: "Case"
            "First."
    second: "Same"
        details old: "Case"
            "Second."
''')
        self.assertEqual(self.cli(root, 'build', '.')[0], 0)
        text = (root / 't/DETAILS.md').read_text()
        self.assertEqual(text.count('## Same'), 2)
        self.assertEqual(text.count('### Case'), 2)

    def test_details_not_in_load(self):
        source = 'team T: "Team"\n    home: "t"\n    work: "Work"\n        "Brief."\n        details:\n            "LONG"\n'
        root = self.project(source)
        before = self.loads(root)[0]['runtimes']['codex']
        (root / 'prompts/AGENTS.prompt').write_text(source.replace('LONG', 'LONG' * 1000))
        after = self.loads(root)[0]['runtimes']['codex']
        self.assertEqual(before['total'], after['total'])
        self.assertGreater(after['details_size'], before['details_size'])

    def test_shared_companion_bytes_ignore_consumers(self):
        root = self.project('''workflow W: "First"
    details:
        "First case."
workflow Retitled[W]: "New title"
    inherit *
abstract agent R:
    role: "Test."
    first: W
    second: W
team T: "Team"
    home: "t"
    member qa[R]: "QA"
        inherit second
        inherit first
    member lead[R]: "Lead"
        override first: Retitled
''')
        code, _, error = self.cli(root, 'build', '.')
        self.assertEqual(code, 0, error)
        path = root / '_details/w.md'
        self.assertEqual([file.name for file in (root / '_details').iterdir()], ['w.md'])
        original = path.read_bytes()
        self.assertIn(b'## First', original)
        self.assertNotIn(b'New title', original)
        source = root / 'prompts/AGENTS.prompt'
        source.write_text(source.read_text().replace('inherit second\n        inherit first', 'inherit first\n        inherit second'))
        self.assertEqual(self.cli(root, 'build', '.')[0], 0)
        self.assertEqual(path.read_bytes(), original)
