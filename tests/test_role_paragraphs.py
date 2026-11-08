import unittest
import json

from doctrine._compiler.home_map import build_home_map
from doctrine.diagnostics import CompileError, ParseError
from doctrine.parser import parse_text
from doctrine.renderer import render_markdown
from tests import test_late_binding
from tests.home_support import HomeProject


class RoleParagraphTests(HomeProject, unittest.TestCase):
    session = test_late_binding.LateBindingTests.session

    def test_role_block_resolves_in_each_module(self):
        session = self.session('''import shared as lib
workflow Facts: "Child module"
    "Read."
agent Child[lib.Base]:
    role:
        paragraph opening:
            "See {{Facts:title}}."
        override paragraph who:
            super
            "See {{Facts:title}}."
        inherit *
''', {'prompts/shared/AGENTS.prompt': '''workflow Facts: "Parent module"
    "Read."
export abstract agent Base:
    role:
        paragraph who:
            "See {{Facts:title}}."
        paragraph other:
            "Also see {{Facts:title}}."
'''})
        self.assertEqual(render_markdown(session.compile_agent('Child')), 'See Child module.\n\nSee Parent module.\n\nSee Child module.\n\nAlso see Parent module.\n')

    def test_role_block_diagnostic_messages(self):
        parent = '''abstract agent Base:
    role:
        paragraph one:
            "One."
        paragraph two:
            "Two."
agent Child[Base]:
    role:
'''
        cases = (
            ('        override paragraph one:\n            "New."\n', 'E003', 'Missing inherited role paragraph in agent Child: two'),
            ('        override paragraph absent:\n            "New."\n', 'E610', '`Child` patches `role.absent`, but its parent has no such key.'),
            ('        inherit one\n', 'E003', 'Missing inherited role paragraph in agent Child: two'),
            ('        inherit absent\n        inherit *\n', 'E610', '`Child` patches `role.absent`, but its parent has no such key.'),
            ('        override paragraph absent:\n            "Text."\n        inherit *\n', 'E610', '`Child` patches `role.absent`, but its parent has no such key.'),
            ('        paragraph one:\n            "Text."\n        inherit *\n', 'E612', '`Child` adds the paragraph `role.one`, which it already inherits. Write `override paragraph one:` to replace it.'),
            ('        inherit one\n        override paragraph one:\n            "Text."\n        inherit *\n', 'E612', '`Child` patches `role.one` twice.'),
            ('        inherit *\n        inherit *\n', 'E613', '`Child` writes `inherit *` more than once.'),
        )
        for body, code, detail in cases:
            with self.subTest(code=code, body=body):
                session = self.session(parent + body)
                with self.assertRaises(CompileError) as caught:
                    session.compile_agent('Child')
                self.assertEqual(caught.exception.code, code)
                self.assertIn(detail, str(caught.exception))
        session = self.session('abstract agent Base:\n    role: "Words."\nagent Child[Base]:\n    role:\n        inherit *\n')
        with self.assertRaises(CompileError) as caught:
            session.compile_agent('Child')
        self.assertEqual(caught.exception.code, 'E611')
        self.assertIn('`Child` inherits from `role`, which has no keyed paragraphs.', str(caught.exception))

    def test_override_only_role_block_patches_the_parent(self):
        session = self.session('''abstract agent Base:
    role:
        paragraph one:
            "One."
agent Child[Base]:
    role:
        override paragraph one:
            super
            "New."
''')
        self.assertEqual(render_markdown(session.compile_agent('Child')), 'One.\n\nNew.\n')

    def test_role_patch_without_parent_role_fails(self):
        for parent, child in (
            ('', 'agent Child:'),
            ('abstract agent Base:\n    work: "Work"\n        "Do it."\n', 'agent Child[Base]:\n    inherit *'),
        ):
            with self.subTest(parent=parent):
                session = self.session(parent + child + '\n    role:\n        inherit *\n')
                with self.assertRaises(CompileError) as caught:
                    session.compile_agent('Child')
                self.assertEqual(caught.exception.code, 'E611')
                self.assertIn('`Child` inherits from `role`, which has no keyed paragraphs.', str(caught.exception))

    def test_role_block_and_path_patch_conflict(self):
        session = self.session('''abstract agent Base:
    role:
        paragraph one:
            "One."
agent Child[Base]:
    role:
        inherit *
    override role.one:
        "New."
''')
        with self.assertRaises(CompileError) as caught:
            session.compile_agent('Child')
        self.assertEqual(caught.exception.code, 'E612')

    def test_super_in_role_paragraph_resolves_in_each_module(self):
        session = self.session('''import shared as lib
workflow Facts: "Child module"
    "Read."
agent Child[lib.Base]:
    override role.who:
        "Before."
        super
        "See {{Facts:title}}."
team T: "Team"
    home: "t"
    member qa[lib.Base]: "QA"
        override role.who:
            super
            "Added."
''', {'prompts/shared/AGENTS.prompt': '''workflow Facts: "Parent module"
    "Read."
export abstract agent Base:
    role:
        paragraph who:
            "See {{Facts:title}}."
'''})
        self.assertEqual(render_markdown(session.compile_agent('Child')), 'Before.\n\nSee Parent module.\n\nSee Child module.\n')
        self.assertEqual(render_markdown(session.compile_agent('T.qa')), 'See Parent module.\n\nAdded.\n')

    def test_super_role_paragraph_requires_an_existing_key(self):
        session = self.session('''abstract agent Base:
    role:
        paragraph who:
            "Words."
agent Child[Base]:
    override role.missing:
        super
''')
        with self.assertRaises(CompileError) as caught:
            session.compile_agent('Child')
        self.assertEqual(caught.exception.code, 'E610')

    def test_super_twice_in_role_paragraph_fails(self):
        session = self.session('''abstract agent Base:
    role:
        paragraph who:
            "Words."
agent Child[Base]:
    override role.who:
        super
        super
''')
        with self.assertRaises(CompileError) as caught:
            session.compile_agent('Child')
        self.assertEqual(caught.exception.code, 'E612')

    def test_role_block_override_home_map_points_to_child_line(self):
        session = self.session('''import shared as lib
agent C[lib.Base]:
    role:
        override paragraph a:
            super
            "A2."
        inherit b
''', {'prompts/shared/AGENTS.prompt': '''export abstract agent Base:
    role:
        paragraph a:
            "A."
        paragraph b:
            "B."
'''})
        entries = {entry.path: entry for entry in build_home_map(session.compile_agent('C')).entries}
        self.assertEqual((entries[('role', 'a')].origin, entries[('role', 'a')].origin_path,
                          entries[('role', 'a')].site), ('C', ('role', 'a'), 'prompts/AGENTS.prompt:4'))
        self.assertEqual((entries[('role', 'b')].origin, entries[('role', 'b')].site),
                         ('shared.Base', 'prompts/shared/AGENTS.prompt:5'))

    def test_where_reports_role_paragraph_author(self):
        root = self.project('''abstract agent Base:
    role:
        paragraph who:
            "Original words."
        paragraph other:
            "Inherited words."
team T: "Team"
    home: "."
    member qa[Base]: "QA"
        override role.who:
            "New child words."
''')
        for words, origin in (('New child words', 'T.qa.role.who'), ('Inherited words', 'Base.role.other')):
            code, output, error = self.cli(root, 'where', words, '--json')
            self.assertEqual(code, 0, error)
            self.assertEqual([match['origin'] for match in json.loads(output)['matches']], [origin])

    def test_duplicate_role_paragraph_fails_even_if_dropped(self):
        session = self.session('''abstract agent Base:
    role:
        paragraph who:
            "First."
        paragraph who:
            "Second."
agent Child[Base]:
    drop role.who: "Reason."
''')
        with self.assertRaises(CompileError) as caught:
            session.compile_agent('Child')
        self.assertEqual(caught.exception.code, 'E295')
        self.assertIn('`Base` repeats role paragraph key `who`.', str(caught.exception))

    def test_dropping_every_role_paragraph_is_missing_role(self):
        session = self.session('''abstract agent Base:
    role:
        paragraph who:
            "First."
agent Child[Base]:
    drop role.who: "Reason."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        drop role.who: "Reason."
''')
        for name in ('Child', 'T.qa'):
            with self.subTest(name=name), self.assertRaises(CompileError) as caught:
                session.compile_agent(name)
            self.assertEqual(caught.exception.code, 'E205')

    def test_from_generated_paragraph_keys_do_not_collide(self):
        session = self.session('''abstract agent Base from "source.md"
agent Child[Base]:
    drop role.thing_2_2: "Reason."
''', {'source.md': '**Thing.** First.\n\n**Thing.** Second.\n\n**Thing 2.** Third.\n'})
        self.assertEqual(render_markdown(session.compile_agent('Child')), '**Thing.** First.\n\n**Thing.** Second.\n')

    def test_from_preserves_bold_lead_spacing(self):
        for gap in ('  ', '\t'):
            with self.subTest(gap=gap):
                text = f'**Who.**{gap}You test.\n\nPhones are nearby.\n'
                session = self.session('''abstract agent Base from "source.md"
agent Child[Base]:
    inherit role
''', {'source.md': text})
                self.assertEqual(render_markdown(session.compile_agent('Child')), text)

    def test_role_override_body_accepts_only_prose(self):
        source = '''abstract agent A:
    role:
        paragraph who:
            "Words."
agent B[A]:
    override role.who:
        details:
            "Hidden."
'''
        with self.assertRaises(ParseError):
            parse_text(source)

    def test_children_and_members_patch_roles(self):
        source = '''abstract agent Base:
    role:
        paragraph who: "Who you are."
            "You are a member of the core team."
        paragraph phones:
            "The phones are nearby."
agent Child[Base]:
    drop role.who: "Not on the core team."
    override role.phones:
        "The phones are elsewhere."
agent Kept[Base]:
    inherit role
agent Replaced[Base]:
    role: "A different role."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        drop role.who: "Not on the core team."
        override role.phones:
            "The phones are elsewhere."
'''
        session = self.session(source)
        self.assertEqual(render_markdown(session.compile_agent('Child')), 'The phones are elsewhere.\n')
        self.assertEqual(render_markdown(session.compile_agent('T.qa')), 'The phones are elsewhere.\n')
        self.assertEqual(render_markdown(session.compile_agent('Replaced')), 'A different role.\n')
        self.assertEqual(render_markdown(session.compile_agent('Kept')), '**Who you are.** You are a member of the core team.\n\nThe phones are nearby.\n')

    def test_missing_key_and_unkeyed_role(self):
        for role, code, detail in (
            ('role:\n        paragraph who:\n            "Text."', 'E610', '`Child` patches `role.missing`, but its parent has no such key.'),
            ('role: "Text."', 'E611', '`Child`: `role.missing` steps through `role`, which has no keyed paragraphs.'),
        ):
            with self.subTest(code=code):
                session = self.session(f'abstract agent Base:\n    {role}\nagent Child[Base]:\n    drop role.missing: "Reason"\n')
                with self.assertRaises(CompileError) as caught:
                    session.compile_agent('Child')
                self.assertEqual(caught.exception.code, code)
                self.assertIn(detail, str(caught.exception))

    def test_markdown_stays_literal_after_a_drop(self):
        session = self.session('''abstract agent Base from "source.md"
agent Child[Base]:
    drop role.first_paragraph: "Reason."
''', {'source.md': 'First paragraph.\n\nKeep {{literal}} as written.\n'})
        self.assertEqual(render_markdown(session.compile_agent('Child')), 'Keep {{literal}} as written.\n')

    def test_parent_role_resolves_refs_in_its_module(self):
        session = self.session('''import shared as lib
agent Child[lib.Base]:
    drop role.who: "Reason."
''', {'prompts/shared/AGENTS.prompt': '''workflow Facts: "Right module"
    "Read."
export abstract agent Base:
    role:
        paragraph who:
            "Drop this."
        paragraph facts:
            "See {{Facts:title}}."
'''})
        self.assertEqual(render_markdown(session.compile_agent('Child')), 'See Right module.\n')

    def test_sources_counts_a_quote_in_a_role_once(self):
        root = self.project('''person Owner: "Owner"
team T: "Team"
    home: "."
    role:
        paragraph who:
            """{{Owner, 2026-11-05: "Words"}}"""
''')
        code, output, error = self.cli(root, 'sources', '--json')
        self.assertEqual(code, 0, error)
        self.assertEqual(len(json.loads(output)['people'][0]['quotes']), 1)
