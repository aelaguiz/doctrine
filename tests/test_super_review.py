from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from doctrine.compiler import CompilationSession
from doctrine.parser import parse_file
from tests.home_support import HomeProject
from tests import test_super


class SuperReviewTests(HomeProject, unittest.TestCase):
    def test_abstract_override_case_heading(self):
        root = self.project('''abstract agent Base:
    role: "Role."
    work: "Work"
        "Parent."
abstract agent Child[Base]:
    override work:
        super
        details own: "Own"
            "Child case."
    inherit *
team T: "Team"
    home: "pod"
    member qa[Child]: "QA"
''')
        code, _, error = self.cli(root, 'build', '.')
        self.assertEqual(code, 0, error)
        self.assertIn('## Work', (root / '_details/child.md').read_text())

    def test_workflow_root_lists(self):
        for kind in ('bullets', 'checklist', 'sequence'):
            with self.subTest(kind=kind):
                source = f'''workflow Base: "Base"
    {kind} steps: "Steps"
        "Parent."
workflow Patched[Base]: "Patched"
    override {kind} steps:
        super
        "Child."
agent Child:
    role: "Role."
    work: Patched
'''
                result = test_super.SuperTests().compile(source)
                self.assertLess(result.index('Parent.'), result.index('Child.'))

    def test_untitled_list_override_with_super_keeps_parent_title(self):
        for kind in ('bullets', 'checklist', 'sequence'):
            for surface in ('document', 'workflow'):
                with self.subTest(kind=kind, surface=surface):
                    source = f'''{surface} Base: "Base"
    {kind} steps: "Steps"
        "Parent."
{surface} Child[Base]: "Child"
    override {kind} steps:
        super
        "Child."
'''
                    if surface == 'workflow':
                        source = source.replace('workflow Child[Base]', 'workflow Patched[Base]')
                        source += 'agent Child:\n    role: "Role."\n    work: Patched\n'
                    result = test_super.SuperTests().compile(source, surface if surface == 'document' else 'agent')
                    self.assertIn('### Steps', result)
                    self.assertLess(result.index('Parent.'), result.index('Child.'))

    def test_dotted_list_explicit_title(self):
        result = test_super.SuperTests().compile('''abstract agent Base:
    role: "Role."
    work: "Work"
        bullets steps:
            "Parent."
agent Child[Base]:
    override work.steps: "New title"
        super
        "Child."
    inherit *
''')
        self.assertIn('New title', result)

    def test_case_override_super(self):
        root = self.project('''abstract agent Base:
    role: "Role."
    work: "Work"
        details cases: "Cases"
            "Parent case."
abstract agent Child[Base]:
    override work.cases:
        super
        "Child case."
    inherit *
team T: "Team"
    home: "pod"
    member qa[Child]: "QA"
''')
        code, _, error = self.cli(root, 'build', '.')
        self.assertEqual(code, 0, error)
        text = (root / '_details/child.md').read_text()
        self.assertIn('Parent case.', text)
        self.assertIn('Child case.', text)

    def test_parent_nested_case_keeps_origin(self):
        for kind in ('section', 'paragraph'):
            with self.subTest(kind=kind):
                root = self.project(f'''abstract agent Base:
    role: "Role."
    work: "Work"
        holder: "Holder"
            {kind} intro: "Intro"
                details cases: "Cases"
                    "Parent case."
abstract agent Child[Base]:
    override work.holder.intro:
        super
        "Child."
    inherit *
team T: "Team"
    home: "pod"
    member qa[Child]: "QA"
''')
                code, _, error = self.cli(root, 'build', '.')
                self.assertEqual(code, 0, error)
                self.assertIn('Parent case.', (root / '_details/base.md').read_text())
                self.assertFalse((root / '_details/child.md').exists())
                code, output, error = self.cli(root, 'where', 'Parent case.', '--json')
                self.assertEqual(code, 0, error)
                self.assertEqual(json.loads(output)['matches'][0]['origin'], 'Base.work.holder.intro.cases')

    def test_parent_case_ref_keeps_flow(self):
        root = self.project('''import roles
workflow Local: "Wrong"
    "Wrong."
abstract agent Child[roles.Base]:
    override work.holder.intro:
        super
        "Child."
    inherit *
team T: "Team"
    home: "pod"
    member qa[Child]: "QA"
''')
        (root / 'prompts/roles').mkdir()
        (root / 'prompts/roles/AGENTS.prompt').write_text('''workflow Local: "Right"
    "Right."
export workflow Shared: "Work"
    holder: "Holder"
        section intro: "Intro"
            details cases: "Cases"
                "Read {{Local:title}}."
export abstract agent Base:
    role: "Role."
    work: Shared
''')
        code, _, error = self.cli(root, 'build', '.')
        self.assertEqual(code, 0, error)
        text = (root / '_details/roles-shared.md').read_text()
        self.assertIn('Read Right.', text)
        self.assertNotIn('Wrong', text)

    def test_stray_super_reports_own_file(self):
        for imported in ('workflow', 'document', 'slot'):
            with self.subTest(imported=imported), TemporaryDirectory() as directory:
                root = Path(directory) / 'prompts'
                (root / 'roles').mkdir(parents=True)
                declarations = {
                    'workflow': ('export workflow Shared: "Shared"\n    super\n', 'work: roles.Shared'),
                    'document': ('export document Shared: "Shared"\n    section body: "Body"\n        super\n', 'outputs: "Outputs"\n        Out'),
                    'slot': ('export abstract agent Shared:\n    role: "Role."\n    work: "Work"\n        super\n', None),
                }
                source, field = declarations[imported]
                (root / 'roles/AGENTS.prompt').write_text(source)
                if imported == 'slot':
                    main = 'import roles\nagent Child[roles.Shared]:\n    inherit *\n'
                else:
                    main = 'import roles\n'
                    if imported == 'document':
                        main += 'output Out: "Out"\n    target: File\n        path: "out.md"\n    shape: MarkdownDocument\n    structure: roles.Shared\n    requirement: Required\n'
                    main += f'agent Child:\n    role: "Role."\n    {field}\n'
                (root / 'AGENTS.prompt').write_text(main)
                with self.assertRaises(Exception) as caught:
                    CompilationSession(parse_file(root / 'AGENTS.prompt')).compile_agent('Child')
                self.assertEqual(caught.exception.code, 'E614')
                self.assertEqual(Path(caught.exception.diagnostic.location.path).resolve(), (root / 'roles/AGENTS.prompt').resolve())

    def test_super_on_last_line_without_newline(self):
        with self.assertRaises(Exception) as caught:
            test_super.SuperTests().compile('agent Child:\n    role: "Role."\n    work: "Work"\n        super')
        self.assertEqual(caught.exception.code, 'E614')

    def test_conflicting_patch_on_non_tuple_payload(self):
        forms = (
            ('rule mark', 'override rule mark'),
            ('callout mark: "Mark"\n        kind: note\n        "Old."',
             'override callout mark:\n        kind: note\n        "New."'),
            ('table mark: "Mark"\n        columns:\n            value: "Value"',
             'override table mark:\n        columns:\n            value: "Value"'),
        )
        for parent, child in forms:
            with self.subTest(parent=parent):
                source = f'''workflow Base: "Base"
    {parent}
workflow Patched[Base]: "Patched"
    {child}
    drop mark.child: "Unused."
agent Child:
    role: "Role."
    work: Patched
'''
                with self.assertRaises(Exception) as caught:
                    test_super.SuperTests().compile(source)
                self.assertEqual(caught.exception.code, 'E612')

    def test_named_workflow_law_and_drops(self):
        source = '''workflow Original: "Original"
    gone: "Gone"
        "Old."
    keep: "Keep"
        "Keep."
workflow Shared[Original]: "Shared"
    drop gone: "Not needed."
    inherit *
    law:
        current none
        active when true
        route "Hand off." -> Receiver
abstract agent Base:
    role: "Role."
    workflow: Shared
agent Child[Base]:
    override workflow:
        super
        "Child."
    inherit *
agent Receiver:
    role: "Receive."
'''
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'prompts/AGENTS.prompt'
            path.parent.mkdir()
            path.write_text(source)
            session = CompilationSession(parse_file(path))
            compiled = session.compile_agent('Child')
            field = next(field for field in compiled.fields if getattr(field, 'key', None) == 'workflow')
            self.assertEqual([(drop.path, drop.reason) for drop in field.drops], [(('gone',), 'Not needed.')])
            graph = session.extract_target_flow_graph(('Child',))
            self.assertTrue(any(edge.target_name == 'Receiver' for edge in graph.edges))
            path.write_text(source.replace('        "Child."', '''        "Child."
        law:
            current none
            active when true
            route "Other." -> Other''') + 'agent Other:\n    role: "Other."\n')
            session = CompilationSession(parse_file(path))
            graph = session.extract_target_flow_graph(('Child',))
            self.assertTrue(any(edge.target_name == 'Other' for edge in graph.edges))
            self.assertFalse(any(edge.target_name == 'Receiver' for edge in graph.edges))
