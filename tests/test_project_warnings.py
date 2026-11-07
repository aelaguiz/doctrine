from __future__ import annotations

import json
import unittest

from tests.ws3_support import HomeProject


class ProjectWarningTests(HomeProject, unittest.TestCase):
    def warnings(self, root, *args):
        result = self.cli(root, "check", "--json", *args)
        self.assertEqual(result[0], 0, result)
        return json.loads(result[1])["warnings"]

    def test_w301_type_1_and_near(self):
        root = self.project(example="188_project_warnings")
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace('team Root:', '''abstract agent Copy:
    role: "You test."
    plan: "Plan"
        "You follow the opportunity's card from the design on, and you write the test plan as the design settles."
team Root:'''))
        warnings = [item for item in self.warnings(root) if item["code"] == "W301"]
        self.assertEqual(len(warnings), 3)
        self.assertTrue(any(not item["examples"][0]["words"] for item in warnings))
        self.assertTrue(any("opportunity" in item["examples"][0]["words"] for item in warnings))

    def test_w301_short_paragraph_skipped(self):
        root = self.project('''team T: "Team"
    home: "pod"
    role: "You test."
    member qa: "QA"
        role: "You test."
''')
        self.assertEqual(self.warnings(root), [])

    def test_w301_shared_section_not_a_copy(self):
        root = self.project('''workflow Shared: "Shared"
    "Read every change with care and test each part that a user will meet today."
team T: "Team"
    home: "pod"
    member a: "A"
        role: "Test."
        work: Shared
    member b: "B"
        role: "Test."
        work: Shared
''')
        self.assertEqual(self.warnings(root), [])

    def test_w301_groups_by_declaration_pair(self):
        paragraph = '"Read every change with care and test each part that a user will meet today."'
        source = f'''abstract agent A:
    role: "Test."
    work: "Work"
        {paragraph}
        {paragraph}
abstract agent B:
    role: "Test."
    work: "Work"
        {paragraph}
        {paragraph}
team T: "Team"
    home: "pod"
    member a[A]: "A"
    member b[B]: "B"
'''
        warning, = self.warnings(self.project(source))
        self.assertEqual(len(warning["examples"]), 4)
        self.assertIn("share 4 paragraphs", warning["text"])
        self.assertEqual(len(warning["text"].splitlines()), 5)

    def test_w302_double_load(self):
        warnings = self.warnings(self.project(example="188_project_warnings"))
        warning, = [item for item in warnings if item["code"] == "W302"]
        self.assertIn("Shared reaches pods/growth/qa from AGENTS.md and pods/growth/qa/AGENTS.md", warning["text"])

    def test_w302_groups_across_slot_keys(self):
        root = self.project(example="188_project_warnings")
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace('    shared: Shared', '    first_key: Shared').replace('        again: Shared', '        second_key: Shared'))
        self.assertEqual(sum(item["code"] == "W302" for item in self.warnings(root)), 1)

    def test_w304_unused_value(self):
        root = self.project('''team T: "Team"
    home: "pod"
    values:
        unused: "Never read."
        first: "{{agent:second}}"
        second: "Read me."
    member qa: "QA"
        role: "{{agent:first}}"
''')
        warning, = self.warnings(root)
        self.assertEqual(warning["text"], "W304 unused value: unused at prompts/AGENTS.prompt:4 is read by no home.")

    def test_check_disable_list(self):
        self.assertEqual(self.warnings(self.project(example="188_project_warnings", fixture="project_disabled"), "--strict"), [])

    def test_strict_fails_on_warning(self):
        root = self.project(example="188_project_warnings")
        code, output, _ = self.cli(root, "check", "--json", "--strict")
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(output)["ok"])
