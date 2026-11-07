from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown, render_readable_block
from tests.home_support import HomeProject


class SuperTests(unittest.TestCase):
    def compile(self, source, kind='agent'):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'prompts' / 'AGENTS.prompt'
            path.parent.mkdir()
            path.write_text(source)
            session = CompilationSession(parse_file(path))
            if kind == 'agent':
                return render_markdown(session.compile_agent('Child'))
            return render_readable_block(session.compile_readable_declaration('document', 'Child'))

    def test_slot_parent_prose_and_blocks(self):
        result = self.compile('''abstract agent Base:
    role: "Role."
    work: "Work"
        "Parent."
        nested: "Nested"
            "Block."
agent Child[Base]:
    override work:
        "Before."
        super
        "After."
        own: "Own"
            "Child block."
    inherit *
''')
        self.assertLess(result.index('Before.'), result.index('Parent.'))
        self.assertLess(result.index('Parent.'), result.index('After.'))
        self.assertLess(result.index('After.'), result.index('Block.'))
        self.assertLess(result.index('Block.'), result.index('Child block.'))

    def test_document_bullets(self):
        result = self.compile('''document Base: "Base"
    bullets steps:
        "Parent."
document Child[Base]: "Child"
    override bullets steps:
        "Before."
        super
        "After."
''', 'document')
        self.assertIn('- Before.\n- Parent.\n- After.', result)

    def test_section_override(self):
        result = self.compile('''workflow Base: "Base"
    steps: "Steps"
        "Parent."
workflow Patched[Base]: "Patched"
    override steps:
        "Before."
        super
        "After."
agent Child:
    role: "Role."
    work: Patched
''')
        self.assertIn('Before.\n\nParent.\n\nAfter.', result)

    def test_patches_under_super(self):
        result = self.compile('''abstract agent Base:
    role: "Role."
    work: "Work"
        "Parent."
        part: "Part"
            "Old."
        unused: "Unused"
            "Dropped."
agent Child[Base]:
    override work:
        super
        "Child."
    override work.part:
        "New."
    drop work.unused: "Not needed."
    inherit *
''')
        self.assertIn('New.', result)
        self.assertNotIn('Old.', result)
        self.assertNotIn('Dropped.', result)

    def test_super_outside_override(self):
        with self.assertRaises(Exception) as caught:
            self.compile('''agent Child:
    role: "Role."
    work: "Work"
        super
''')
        self.assertEqual(caught.exception.code, 'E614')

    def test_dotted_list(self):
        result = self.compile('''abstract agent Base:
    role: "Role."
    work: "Work"
        bullets steps:
            "Parent."
agent Child[Base]:
    override work.steps:
        super
        "Child."
    inherit *
''')
        self.assertIn('- Parent.\n- Child.', result)

    def test_duplicate_super(self):
        with self.assertRaises(Exception) as caught:
            self.compile('''abstract agent Base:
    role: "Role."
    work: "Work"
        "Parent."
agent Child[Base]:
    override work:
        super
        super
    inherit *
''')
        self.assertEqual(caught.exception.code, 'E612')

    def test_key_collision(self):
        with self.assertRaises(Exception) as caught:
            self.compile('''abstract agent Base:
    role: "Role."
    work: "Work"
        part: "Part"
            "Parent."
agent Child[Base]:
    override work:
        super
        part: "Part"
            "Child."
    inherit *
''')
        self.assertEqual(caught.exception.code, 'E612')

    def test_document_section_and_paragraph(self):
        for kind in ('section', 'paragraph'):
            with self.subTest(kind=kind):
                result = self.compile(f'''document Base: "Base"
    {kind} work: "Work"
        "Parent."
document Child[Base]: "Child"
    override {kind} work:
        "Before."
        super
        "After."
''', 'document')
                self.assertLess(result.index('Before.'), result.index('Parent.'))
                self.assertLess(result.index('Parent.'), result.index('After.'))

    def test_parent_named_workflow(self):
        result = self.compile('''workflow Shared: "Work"
    "Parent."
    part: "Part"
        "A block."
abstract agent Base:
    role: "Role."
    work: Shared
agent Child[Base]:
    override work:
        super
        "Child."
    inherit *
''')
        self.assertIn('Parent.', result)
        self.assertIn('A block.', result)
        self.assertIn('Child.', result)

    def test_list_path_rejects_non_list_body(self):
        with self.assertRaises(Exception) as caught:
            self.compile('''abstract agent Base:
    role: "Role."
    work: "Work"
        bullets steps:
            "Parent."
agent Child[Base]:
    override work.steps:
        part: "Part"
            "No."
    inherit *
''')
        self.assertEqual(caught.exception.code, 'E611')
        self.assertIn("`Child`: `override work.steps` gives a list a body it can't hold. A list takes items.", str(caught.exception))

    def test_document_super_outside_override(self):
        with self.assertRaises(Exception) as caught:
            self.compile('''document Child: "Child"
    section work: "Work"
        super
''', 'document')
        self.assertEqual(caught.exception.code, 'E614')

    def test_section_before_and_after(self):
        for before in (True, False):
            line = '        super\n        "Added."\n' if before else '        "Added."\n        super\n'
            result = self.compile('''workflow Base: "Base"
    steps: "Steps"
        "Parent."
workflow Patched[Base]: "Patched"
    override steps:
''' + line + '''agent Child:
    role: "Role."
    work: Patched
''')
            self.assertEqual(result.index('Parent.') < result.index('Added.'), before)

    def test_list_overrides_with_and_without_titles(self):
        for kind in ('bullets', 'checklist', 'sequence'):
            for title in ('', ' "New"'):
                with self.subTest(kind=kind, title=title):
                    result = self.compile(f'''document Base: "Base"
    {kind} steps: "Steps"
        "Parent."
document Child[Base]: "Child"
    override {kind} steps:{title}
        super
        "Child."
''', 'document')
                    self.assertLess(result.index('Parent.'), result.index('Child.'))

    def test_repeated_key_message(self):
        with self.assertRaises(Exception) as caught:
            self.compile('''abstract agent Base:
    role: "Role."
    work: "Work"
        part: "Part"
            "Parent."
agent Child[Base]:
    override work:
        super
        part: "Part"
            "Child."
    inherit *
''')
        self.assertIn('`Child` writes `part` in `override work`, and `super` already brings it. Patch it with `override work.part`.', str(caught.exception))

    def test_parent_prose_keeps_its_module(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'prompts'
            root.mkdir()
            (root / 'AGENTS.prompt').write_text('''import roles
workflow Local: "Wrong"
    "Wrong."
agent Child[roles.Base]:
    override work:
        super
        "Child."
    inherit *
''')
            (root / 'roles').mkdir()
            (root / 'roles' / 'AGENTS.prompt').write_text('''workflow Local: "Right"
    "Right."
export abstract agent Base:
    role: "Role."
    work: "Work"
        "Read {{Local:title}}."
''')
            result = render_markdown(CompilationSession(parse_file(root / 'AGENTS.prompt')).compile_agent('Child'))
            self.assertIn('Read Right.', result)
            self.assertNotIn('Wrong', result)

    def test_list_path_without_super_replaces_items(self):
        result = self.compile('''abstract agent Base:
    role: "Role."
    work: "Work"
        bullets steps:
            "Parent."
agent Child[Base]:
    override work.steps:
        "Child."
    inherit *
''')
        self.assertNotIn('Parent.', result)
        self.assertIn('- Child.', result)


class SuperDiffTests(HomeProject, unittest.TestCase):
    def test_parent_edit_reaches_member(self):
        source = '''abstract agent Craft:
    role: "Role."
    work: "Work"
        "Parent."
team T: "Team"
    home: "pod"
    member qa[Craft]: "QA"
        override work:
            super
            "Child."
'''
        before = self.project(source)
        after = self.project(source.replace('Parent.', 'Parent grows.'))
        code, output, error = self.cli(after, 'diff', '--base-tree', str(before), '--json')
        self.assertEqual(code, 0, error)
        self.assertEqual([entry['home'] for entry in json.loads(output)['homes']], ['pod/qa'])

    def test_super_keeps_a_named_workflow_use(self):
        source = '''workflow Shared: "Shared"
    part: "Part"
        "From use."
abstract agent Craft:
    role: "Role."
    work: "Work"
        use shared: Shared
team T: "Team"
    home: "pod"
    member qa[Craft]: "QA"
        override work:
            super
            "Child."
'''
        root = self.project(source)
        code, _, error = self.cli(root, 'build', '.')
        self.assertEqual(code, 0, error)
        text = (root / 'pod' / 'qa' / 'AGENTS.md').read_text()
        self.assertIn('From use.', text)
        self.assertIn('Child.', text)

    def test_parent_case_keeps_its_origin(self):
        source = '''abstract agent Craft:
    role: "Role."
    work: "Work"
        "Parent."
        details old: "Old"
            "Parent case."
team T: "Team"
    home: "pod"
    member qa[Craft]: "QA"
        override work:
            super
            "Child."
'''
        root = self.project(source)
        code, _, error = self.cli(root, 'build', '.')
        self.assertEqual(code, 0, error)
        text = (root / '_details' / 'craft.md').read_text()
        self.assertEqual(text.count('Parent case.'), 1)

    def test_new_case_in_untitled_override(self):
        source = '''abstract agent Craft:
    role: "Role."
    work: "Work"
        "Parent."
team T: "Team"
    home: "pod"
    member qa[Craft]: "QA"
        override work:
            super
            details own: "Own"
                "Child case."
'''
        root = self.project(source)
        code, _, error = self.cli(root, 'build', '.')
        self.assertEqual(code, 0, error)
        text = (root / 'pod' / 'qa' / 'DETAILS.md').read_text()
        self.assertIn('Child case.', text)
