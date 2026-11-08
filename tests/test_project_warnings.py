from __future__ import annotations

import json
import unittest

from tests.home_support import HomeProject


class ProjectWarningTests(HomeProject, unittest.TestCase):
    def test_w301_compares_markdown_backed_files(self):
        root = self.project('''file Guide from "prompts/guide.md"
    path: "shared/guide.md"
team T: "Team"
    home: "pod"
    role: "Read every change with care and test each part that a user will meet today."
''')
        (root / "prompts/guide.md").write_text(
            "# Guide\n\nRead every change with care and test each part that a reader will meet today.\n"
        )
        warning, = self.warnings(root)
        self.assertEqual(warning["code"], "W301")
        self.assertIn("prompts/guide.md:3", warning["text"])

    def test_w302_is_the_same_before_and_after_build(self):
        root = self.project(example="188_project_warnings")
        before = self.cli(root, "check", "--json")
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        after = self.cli(root, "check", "--json")
        first = [item["text"] for item in json.loads(before[1])["warnings"] if item["code"] == "W302"]
        second = [item["text"] for item in json.loads(after[1])["warnings"] if item["code"] == "W302"]
        self.assertTrue(first)
        self.assertEqual(first, second)

    def warnings(self, root, *args):
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        result = self.cli(root, "check", "--json", *args)
        self.assertEqual(result[0], 0, result)
        return json.loads(result[1])["warnings"]

    def test_whole_build_prints_project_warnings_but_selected_build_does_not(self):
        root = self.project(example="188_project_warnings")
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("W301", error)
        code, _, error = self.cli(root, "build", "GrowthPod.qa")
        self.assertEqual(code, 0, error)
        self.assertNotIn("W301", error)

    def test_w301_type_1_and_near(self):
        root = self.project(example="188_project_warnings")
        source = root / "prompts/AGENTS.prompt"
        copy = (
            'abstract agent Copy:\n    role: "You test."\n    plan: "Plan"\n'
            '        "You follow the opportunity\'s card from the design on, '
            'and you write the test plan as the design settles."\nteam Root:'
        )
        source.write_text(source.read_text().replace('team Root:', copy))
        warnings = [item for item in self.warnings(root) if item["code"] == "W301"]
        self.assertEqual(len(warnings), 3)
        self.assertTrue(any(not item["examples"][0]["words"] for item in warnings))
        self.assertTrue(any("opportunity" in item["examples"][0]["words"] for item in warnings))
        for warning in warnings:
            self.assertIn("share 1 paragraph that", warning["text"])
            if not warning["examples"][0]["words"]:
                self.assertEqual(
                    warning["text"].splitlines()[1],
                    "- " + " and ".join(warning["examples"][0]["sites"]),
                )

    def test_w301_short_paragraph_skipped(self):
        root = self.project('''team T: "Team"
    home: "pod"
    role: "You test."
    member qa: "QA"
        role: "You test."
''')
        self.assertEqual(self.warnings(root), [])

    def test_w301_reads_from_files(self):
        root = self.project('''abstract agent A from "first.md"
workflow B from "second.md"
team T: "Team"
    home: "pod"
    member qa[A]: "QA"
        work: B
''')
        paragraph = "Read every change with care and test each part that a user will meet today."
        (root / "first.md").write_text(
            f"# Role\n\n{paragraph}\n\n~~~text\n\n{paragraph}\n\n~~~\n"
        )
        (root / "second.md").write_text(
            f"# Work\n\n{paragraph.replace('user', 'reader')}\n\n```text\n\n{paragraph}\n\n```\n"
        )
        warning, = self.warnings(root)
        self.assertEqual(warning["code"], "W301")
        self.assertEqual(warning["examples"], [
            {"sites": ["first.md:3", "second.md:3"], "words": ["user", "reader"]},
            {"sites": ["first.md:3", "second.md:7"], "words": []},
            {"sites": ["first.md:7", "second.md:3"], "words": ["user", "reader"]},
            {"sites": ["first.md:7", "second.md:7"], "words": []},
        ])

    def test_w301_reads_each_from_file_once(self):
        root = self.project('''abstract agent A from "shared.md"
workflow B from "./shared.md"
team T: "Team"
    home: "pod"
    member qa[A]: "QA"
        work: B
''')
        (root / "shared.md").write_text(
            "Read every change with care and test each part that a user will meet today.\n"
        )
        self.assertEqual(self.warnings(root), [])

    def test_w304_default_counts_as_read(self):
        root = self.project('''abstract agent Role:
    role: "Read {{agent:word}}."
    values:
        word: "Default."
team T: "Team"
    home: "pod"
    values:
        word: "Team word."
    member qa[Role]: "QA"
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
        self.assertIn(
            "Shared reaches pods/growth/qa from AGENTS.md and pods/growth/qa/AGENTS.md",
            warning["text"],
        )

    def test_w302_groups_across_slot_keys(self):
        root = self.project(example="188_project_warnings")
        source = root / "prompts/AGENTS.prompt"
        source.write_text(
            source.read_text().replace('    shared: Shared', '    first_key: Shared')
            .replace('        again: Shared', '        second_key: Shared')
        )
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
        self.assertEqual(
            warning["text"],
            "W304 unused value: unused at prompts/AGENTS.prompt:4 is read by no home.",
        )

    def test_check_disable_list(self):
        root = self.project(example="188_project_warnings", fixture="project_disabled")
        self.assertEqual(self.warnings(root, "--strict"), [])
        config = root / "pyproject.toml"
        config.write_text(config.read_text().replace('"W304"', '"W304", "W306"') + (
            '[tool.doctrine.runtimes.codex]\nlimit = 100000\nwarn_at = 0.00001\n'
        ))
        self.assertEqual(self.warnings(root, "--strict"), [])

    def test_strict_fails_on_warning(self):
        root = self.project(example="188_project_warnings")
        code, output, _ = self.cli(root, "check", "--json", "--strict")
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(output)["ok"])
