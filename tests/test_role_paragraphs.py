import unittest
import json

from doctrine.diagnostics import CompileError, ParseError
from doctrine.parser import parse_text
from doctrine.renderer import render_markdown
from tests import test_late_binding
from tests.home_support import HomeProject


class RoleParagraphTests(HomeProject, unittest.TestCase):
    session = test_late_binding.LateBindingTests.session

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
