from __future__ import annotations

import unittest

from tests.home_support import HomeProject


class DetailsPathTests(HomeProject, unittest.TestCase):
    def test_member_adds_case_under_paragraph(self):
        root = self.project('''abstract agent Base:
    role: "Test."
    work: "Work"
        paragraph plan: "Plan"
            "Think."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        details work.plan.local: "Local"
            "A local case."
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("A local case.", (root / "t/qa/DETAILS.md").read_text())

    def test_missing_parent_and_existing_key(self):
        source = '''abstract agent Base:
    role: "Test."
    work: "Work"
        details old: "Old"
            "Old case."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        details work.PATH: "New"
            "New case."
'''
        for path, message in (("missing.case", "`T.qa` patches `work.missing.case`, but its parent has no such key."),
                              ("old", "`T.qa` adds the case `work.old`, which it already has. Write `override work.old` to replace it.")):
            with self.subTest(path=path):
                root = self.project(source.replace("PATH", path))
                code, _, error = self.cli(root, "build", ".")
                self.assertEqual(code, 1)
                self.assertIn(message, error)

    def test_override_keeps_cases_and_drop_clears_collision(self):
        source = '''abstract agent Base:
    role: "Test."
    work: "Work"
        left: "Left"
            details case: "Left case"
                "Left case."
        right: "Right"
            details case: "Right case"
                "Right case."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        override work: "Work"
            "New idea."
DROP
'''
        root = self.project(source.replace("DROP\n", ""))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("`T.qa` overrides `work`, which would keep two cases keyed `case`. Drop one with a reason, or give them different keys.", error)
        (root / "prompts/AGENTS.prompt").write_text(source.replace("DROP", '        drop work.left.case: "It no longer fits."'))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        text = (root / "_details/base.md").read_text()
        self.assertNotIn("Left case.", text)
        self.assertIn("Right case.", text)
        code, output, error = self.cli(root, "load", "T.qa")
        self.assertEqual(code, 0, error)
        self.assertIn("It no longer fits.", output)

    def test_replacing_direct_case_and_collision_with_deeper_case(self):
        source = '''abstract agent Base:
    role: "Test."
    work: "Work"
        details case: "Case"
            "Old case."
NESTED
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        override work: "Work"
            details case: "Case"
                "New case."
'''
        root = self.project(source.replace("NESTED\n", ""))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("New case.", (root / "t/qa/DETAILS.md").read_text())
        self.assertFalse((root / "_details/base.md").exists())
        (root / "prompts/AGENTS.prompt").write_text(source.replace("NESTED", '''        child: "Child"
            details case: "Case"
                "Nested case."'''))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("which would keep two cases keyed `case`", error)

    def test_path_override_replaces_case_and_rejects_other_nested_patch(self):
        source = '''abstract agent Base:
    role: "Test."
    work: "Work"
        paragraph plan: "Plan"
            "Idea."
            details old: "Old"
                "Old case."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        override work.plan:
            "New idea."
        override work.plan.old: "New"
            "New case."
'''
        root = self.project(source)
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("New case.", (root / "t/qa/DETAILS.md").read_text())
        (root / "prompts/AGENTS.prompt").write_text(source.replace('override work.plan.old: "New"', 'override work.plan.absent: "New"'))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("`T.qa` patches `work.plan.absent` under `work.plan`, which it already dropped or overrode.", error)

    def test_workflow_and_document_overrides_keep_cases(self):
        sources = (
            '''workflow Base: "Work"
    plan: "Plan"
        "Old idea."
        details old: "Old"
            "Keep this case."
workflow Child[Base]: "Work"
    override plan:
        "New idea."
team T: "Team"
    home: "t"
    work: Child
''',
            '''document Base: "Document"
    section plan: "Plan"
        "Old idea."
        details old: "Old"
            "Keep this case."
document Child[Base]: "Document"
    override section plan:
        "New idea."
input I: "Input"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
    structure: Child
agent A:
    role: "Test."
    inputs: "Inputs"
        I
''',
        )
        for source in sources:
            with self.subTest(source=source):
                root = self.project(source)
                code, _, error = self.cli(root, "build", ".", "--target", "homes")
                self.assertEqual(code, 0, error)
                self.assertIn("Keep this case.", (root / "_details/base.md").read_text())

    def test_case_cannot_attach_to_bullets(self):
        root = self.project('''abstract agent Base:
    role: "Test."
    work: "Work"
        bullets list: "List"
            "One."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        details work.list.case:
            "Case."
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("`T.qa`: `details work.list.case` attaches to a `bullets`. Attach it to the section or paragraph that holds it.", error)

    def test_kept_case_reads_its_original_module(self):
        root = self.project('''import common
workflow Topic: "Wrong"
    "Text."
team T: "Team"
    home: "t"
    member qa[common.Base]: "QA"
        override work: "Work"
            "New idea."
''')
        (root / "prompts/common").mkdir()
        (root / "prompts/common/AGENTS.prompt").write_text('''workflow Topic: "Right"
    "Text."
export abstract agent Base:
    role: "Test."
    work: "Work"
        details old: "Old"
            "{{Topic:title}}"
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("Right", (root / "_details/common-base.md").read_text())
        self.assertNotIn("Wrong", (root / "_details/common-base.md").read_text())

    def test_slot_override_keeps_case_in_paragraph(self):
        root = self.project('''abstract agent Base:
    role: "Test."
    work: "Work"
        paragraph plan: "Plan"
            "Old idea."
            details old: "Old"
                "Keep this case."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        override work: "Work"
            "New idea."
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("Keep this case.", (root / "_details/base.md").read_text())

    def test_team_adds_case_and_override_keeps_bare_case(self):
        root = self.project('''abstract team Base:
    work: "Work"
        details:
            "A shared case."
team T[Base]: "Team"
    home: "t"
    details work.local: "Local"
        "Team case."
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("Team case.", (root / "t/DETAILS.md").read_text())
        self.assertIn("A shared case.", (root / "_details/base.md").read_text())

    def test_path_override_keeps_bare_case(self):
        root = self.project('''abstract agent Base:
    role: "Test."
    work: "Work"
        paragraph plan: "Plan"
            "Old idea."
            details:
                "A bare case."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        override work.plan:
            "New idea."
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("A bare case.", (root / "_details/base.md").read_text())

    def test_case_addition_beside_parent_override(self):
        root = self.project('''abstract agent Base:
    role: "Test."
    work: "Work"
        "Old idea."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        override work: "Work"
            "New idea."
        details work.local: "Local"
            "New case."
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("New case.", (root / "t/qa/DETAILS.md").read_text())

    def test_case_cannot_attach_to_role(self):
        root = self.project('''abstract agent Base:
    role: "Test."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        details role.case:
            "Case."
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("`T.qa`: `details role.case` attaches to a `scalar`. Attach it to the section or paragraph that holds it.", error)

    def test_case_reading_team_value_through_ref(self):
        root = self.project('''workflow Words: "{{team:unit}}"
    "Words."
abstract agent Qa:
    role: "Test."
    work: "Work"
        details shared: "Shared"
            "Shared text: {{Words:title}}."
        details plain: "Plain"
            "Plain case."
team A: "A"
    home: "a"
    values:
        unit: "bet"
    member qa[Qa]: "QA"
team B: "B"
    home: "b"
    values:
        unit: "feature"
    member qa[Qa]: "QA"
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("Shared text: bet.", (root / "a/qa/DETAILS.md").read_text())
        self.assertIn("Shared text: feature.", (root / "b/qa/DETAILS.md").read_text())
        shared = (root / "_details/qa.md").read_text()
        self.assertIn("Plain case.", shared)
        self.assertNotIn("Shared text", shared)

    def test_kept_case_in_local_section_at_two_depths_and_original_module(self):
        for override in ('override work: "Work"\n            "New."',
                         'override work.outer.middle: "Middle"\n            "New."'):
            with self.subTest(override=override):
                root = self.project('''import common
workflow Topic: "Wrong"
    "Text."
team T: "Team"
    home: "t"
    member qa[common.Base]: "QA"
        ''' + override + '\n')
                (root / "prompts/common").mkdir()
                (root / "prompts/common/AGENTS.prompt").write_text('''workflow Topic: "Right"
    "Text."
export abstract agent Base:
    role: "Test."
    work: "Work"
        outer: "Outer"
            section middle: "Middle"
                inner: "Inner"
                    details old: "Old"
                        "{{Topic:title}}"
''')
                code, _, error = self.cli(root, "build", ".")
                self.assertEqual(code, 0, error)
                self.assertIn("Right", (root / "_details/common-base.md").read_text())
                self.assertFalse((root / "t/qa/DETAILS.md").exists())

    def test_case_patch_conflicts_with_override_body(self):
        for patch in ('details work.new: "Added"\n            "Added."',
                      'override work.new: "Changed"\n            "Changed."'):
            with self.subTest(patch=patch):
                inherited = '' if patch.startswith('details') else '''        details new: "Old"
            "Old."
'''
                root = self.project('''abstract agent Base:
    role: "Test."
    work: "Work"
        "Idea."
''' + inherited + '''team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        override work: "Work"
            details new: "Body"
                "Body."
        ''' + patch + '\n')
                code, _, error = self.cli(root, "build", ".")
                self.assertEqual(code, 1, error)
                self.assertIn('`T.qa` patches `work.new`, and `override work` writes `new` too. Keep one.', error)

    def test_guard_override_and_drop_cases(self):
        for declaration, use in (
            ('workflow', 'team T: "Team"\n    home: "t"\n    work: Child\n'),
            ('document', 'input I: "Input"\n    source: Prompt\n    shape: MarkdownDocument\n    requirement: Required\n    structure: Child\nagent A:\n    role: "Test."\n    inputs: "Inputs"\n        I\n'),
        ):
            with self.subTest(declaration=declaration):
                root = self.project('''enum State: "State"
    ready: "Ready"
''' + declaration + ''' Base: "Base"
    guard g when State.ready == State.ready
        details case: "Case"
            "Keep this."
''' + declaration + ''' Child[Base]: "Child"
    override guard g when State.ready == State.ready
        "New."
''' + use)
                code, _, error = self.cli(root, "build", ".", "--target", "homes")
                self.assertEqual(code, 0, error)
                self.assertIn("Keep this.", (root / "_details/base.md").read_text())
        source = '''enum State: "State"
    ready: "Ready"
abstract agent Base:
    role: "Test."
    work: "Work"
        guard one when State.ready == State.ready
            details case: "One"
                "First."
        guard two when State.ready == State.ready
            details case: "Two"
                "Second."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        override work: "Work"
            "New."
DROP
'''
        root = self.project(source.replace('DROP\n', ''))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn('which would keep two cases keyed `case`', error)
        (root / 'prompts/AGENTS.prompt').write_text(source.replace('DROP', '        drop work.one.case: "Not needed."'))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        text = (root / '_details/base.md').read_text()
        self.assertIn('Second.', text)
        self.assertNotIn('First.', text)

    def test_workflow_case_override_heading_and_kept_case_ref(self):
        root = self.project('''workflow Base: "Work"
    plan: "Plan"
        details repl: "Repl"
            "Old."
workflow Child[Base]: "Work"
    override plan.repl: "Repl2"
        "New."
team T: "Team"
    home: "t"
    work: Child
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn('## Work\n\n### Plan\n\n#### Repl2', (root / '_details/child.md').read_text())
        (root / 'prompts/AGENTS.prompt').write_text('''workflow Base: "Work"
    plan: "Plan"
        details old: "Old case"
            "Old."
workflow Child[Base]: "Work"
    override plan: "Plan"
        "Ref {{Child:plan.old.title}}."
team T: "Team"
    home: "t"
    work: Child
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn('Ref Old case.', (root / 't/AGENTS.md').read_text())

    def test_nested_case_patch_conflicts_with_override_body(self):
        root = self.project('''abstract agent Base:
    role: "Test."
    work: "Work"
        plan: "Plan"
            details old: "Old"
                "Old."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        override work.plan:
            details old: "Body"
                "Body."
        override work.plan.old: "Changed"
            "Changed."
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1, error)
        self.assertIn('`T.qa` patches `work.plan.old`, and `override work.plan` writes `old` too. Keep one.', error)
