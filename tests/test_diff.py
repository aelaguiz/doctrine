from __future__ import annotations

import json
import subprocess
import unittest

from tests.ws3_support import HomeProject


SOURCE = '''abstract agent Craft:
    role: "You test."
    work: "Work"
        "Read the change."
team T: "Team"
    home: "pod"
    member qa[Craft]: "QA"
'''


class DiffTests(HomeProject, unittest.TestCase):
    def compare(self, old, new, *args):
        before, after = self.project(old), self.project(new)
        result = self.cli(after, "diff", "--base-tree", str(before), *args)
        self.assertEqual(result[0], 0, result)
        return result[1]

    def test_moving_a_declaration_changes_no_hash(self):
        result = json.loads(self.compare(SOURCE, "\n\n" + SOURCE, "--json"))
        self.assertEqual(result["changed_declarations"], [])
        self.assertEqual(result["homes"], [])

    def test_reach_lists_only_changed_homes(self):
        source = SOURCE + '''team Other: "Other"
    home: "other"
    member qa: "QA"
        role: "Other role."
'''
        result = json.loads(self.compare(
            source, source.replace("Read the change.", "Read the whole change."), "--json"
        ))
        self.assertEqual([home["home"] for home in result["homes"]], ["pod/qa"])
        self.assertEqual(
            result["changed_declarations"][0]["homes"],
            [{"home": "pod/qa", "delta": {"always_on": 6, "details": 0}}],
        )

    def test_change_at_a_level_reaches_homes_below(self):
        source = SOURCE.replace('    home: "pod"', '    home: "pod"\n    role: "Team text."')
        result = json.loads(self.compare(
            source, source.replace("Team text.", "New team text."), "--json"
        ))
        self.assertEqual([home["home"] for home in result["homes"]], ["pod", "pod/qa"])
        self.assertEqual(
            result["changed_declarations"][0]["homes"],
            [{"home": path, "delta": {"always_on": 4, "details": 0}}
             for path in ("pod", "pod/qa")],
        )
        self.assertEqual([home["delta"]["always_on"] for home in result["homes"]], [4, 4])

    def test_size_range_printed_when_homes_differ(self):
        source = '''abstract agent Craft:
    role: "You test."
    work: "Work"
        "Read {{agent:word}}."
team T: "Team"
    home: "pod"
    member a[Craft]: "A"
        values:
            word: "a"
    member b[Craft]: "B"
        values:
            word: "long"
'''
        output = self.compare(
            source, source.replace('Read {{agent:word}}.', 'Read {{agent:word}}{{agent:word}}.')
        )
        self.assertIn("+1 to +4 characters", output)

    def test_details_delta_separate(self):
        source = SOURCE.replace(
            '        "Read the change."',
            '        "Read the change."\n        details:\n            "An older case."'
        )
        new = source.replace("An older case.", "An older case, with more words.")
        result = json.loads(self.compare(source, new, "--json"))
        self.assertEqual(result["homes"][0]["delta"], {"always_on": 0, "details": 17})
        self.assertIn("(details +17)", self.compare(source, new))
        same_size = json.loads(self.compare(
            source, source.replace("An older case.", "A newer case.."), "--json"
        ))
        self.assertEqual(same_size["changed_declarations"][0]["name"], "Craft")
        self.assertEqual(same_size["homes"][0]["delta"], {"always_on": 0, "details": 0})

    def test_declaration_homes_carry_each_delta(self):
        source = '''abstract agent Craft:
    role: "Read {{agent:word}}."
team T: "Team"
    home: "pod"
    member a[Craft]: "A"
        values:
            word: "a"
    member b[Craft]: "B"
        values:
            word: "long"
'''
        result = json.loads(self.compare(
            source, source.replace('{{agent:word}}', '{{agent:word}}{{agent:word}}'), "--json"
        ))
        declaration, = result["changed_declarations"]
        self.assertEqual(declaration["homes"], [
            {"home": "pod/a", "delta": {"always_on": 1, "details": 0}},
            {"home": "pod/b", "delta": {"always_on": 4, "details": 0}},
        ])
        self.assertNotIn("delta", declaration)

    def test_failed_base_exits_2(self):
        before = self.project(SOURCE.replace("You test.", "{{agent:missing}}"))
        result = self.cli(self.project(SOURCE), "diff", "--base-tree", str(before))
        self.assertEqual(result[0], 2, result)
        self.assertEqual(result[1], "")
        self.assertTrue(result[2].startswith(
            f"Base {before} does not compile, so nothing was compared.\n"
        ), result)
        self.assertIn("E601", result[2])

    def test_text_blocks_for_new_sections_and_over_budget(self):
        source = '''workflow Base: "Base"
    old: "Old"
        "Old text."
workflow Child[Base]: "Child"
    inherit *
team T: "Team"
    home: "pod"
    member qa: "QA"
        role: "Test."
        budget:
            codex: 1
        craft: Child
'''
        new = source.replace(
            'workflow Child', '    added: "Added"\n        "New text."\nworkflow Child'
        )
        output = self.compare(source, new)
        self.assertIn(
            "New sections that arrive through inherit *:\n  Base.added reaches pod/qa", output
        )
        self.assertRegex(output, r"Over budget:\n  pod/qa on codex: [\d,]+ of 1\n")

    def test_new_section_through_wildcard(self):
        source = '''workflow Base: "Base"
    old: "Old"
        "Old text."
workflow Child[Base]: "Child"
    inherit *
team T: "Team"
    home: "pod"
    member qa: "QA"
        role: "Test."
        craft: Child
'''
        new = source.replace(
            'workflow Child', '    added: "Added"\n        "New text."\nworkflow Child'
        )
        result = json.loads(self.compare(source, new, "--json"))
        self.assertEqual(result["new_sections"], [
            {"origin": "Base", "path": ["added"], "homes": ["pod/qa"]}
        ])

    def test_explicit_member_fails_instead_of_new_section(self):
        source = '''workflow Base: "Base"
    old: "Old"
        "Old text."
    added: "Added"
        "New text."
workflow Child[Base]: "Child"
    inherit old
team T: "Team"
    home: "pod"
    member qa: "QA"
        role: "Test."
        craft: Child
'''
        before = self.project(SOURCE)
        result = self.cli(self.project(source), "diff", "--base-tree", str(before))
        self.assertEqual(result[0], 1, result)
        self.assertIn("E003", result[2])

    def test_outputs_list_exact_paths(self):
        result = json.loads(self.compare(
            SOURCE, SOURCE.replace("Read the change.", "Read all changes."), "--json"
        ))
        self.assertEqual(result["outputs"], ["pod/qa/AGENTS.md"])

    def test_outputs_hold_only_changed_files(self):
        source = SOURCE.replace('    home: "pod"', '    home: "pod"\n    role: "Team text."')
        result = json.loads(self.compare(
            source, source.replace("Team text.", "New team text."), "--json"
        ))
        self.assertEqual(len(result["homes"]), 2)
        self.assertEqual(result["outputs"], ["pod/AGENTS.md"])

    def test_outputs_list_removed_paths(self):
        result = json.loads(self.compare(SOURCE, SOURCE.split('    member qa')[0], "--json"))
        self.assertEqual(result["outputs"], [
            "HOMES.contract.json", "pod/TEAM.contract.json", "pod/qa/AGENTS.md", "pod/qa/CLAUDE.md"
        ])

    def test_with_ignores_other_uncommitted_edits(self):
        root = self.project('team T: "Team"\n    home: "pod"\n    member qa[Craft]: "QA"\n')
        craft = root / "prompts/craft.prompt"
        craft.write_text(
            SOURCE.split('team T:')[0].replace('abstract agent', 'export abstract agent')
        )
        for args in (
            ("init", "-q"),
            ("config", "user.name", "Fixture"),
            ("config", "user.email", "fixture@example.com"),
            ("add", "."),
            ("commit", "-qm", "Fixture [skip ci]"),
        ):
            subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
        craft.write_text(craft.read_text().replace("Read the change.", "Read all changes."))
        (root / "prompts/AGENTS.prompt").write_text("Broken source.\n")
        result = self.cli(root, "diff", "--with", "prompts/craft.prompt", "--json")
        self.assertEqual(result[0], 0, result)
        self.assertEqual(json.loads(result[1])["outputs"], ["pod/qa/AGENTS.md"])

    def test_with_overlays_base_tree(self):
        source = 'team T: "Team"\n    home: "pod"\n    member qa[Craft]: "QA"\n'
        before, after = self.project(source), self.project(source)
        (before / "prompts/craft.prompt").write_text(SOURCE.split('team T:')[0])
        (after / "prompts/craft.prompt").write_text(
            SOURCE.split('team T:')[0].replace("Read the change.", "Read all changes.")
        )
        (after / "prompts/AGENTS.prompt").write_text("Broken source.\n")
        result = self.cli(
            after, "diff", "--base-tree", str(before), "--with", "prompts/craft.prompt", "--json"
        )
        self.assertEqual(result[0], 0, result)
        self.assertEqual(json.loads(result[1])["outputs"], ["pod/qa/AGENTS.md"])

    def test_json_format_version(self):
        result = json.loads(self.compare(SOURCE, SOURCE, "--json"))
        self.assertEqual(result["format_version"], 1)
        self.assertEqual(result["outputs"], [])

    def test_inherited_text_keeps_its_source_module(self):
        source = '''from parent import Craft
document Lesson: "Local words"
    "Local text."
team T: "Team"
    home: "pod"
    member qa[Craft]: "QA"
'''
        before, after = self.project(source), self.project(source)
        for root, title in ((before, "Old words"), (after, "New words")):
            (root / "prompts/parent").mkdir()
            (root / "prompts/parent/AGENTS.prompt").write_text(
                f'''document Lesson: "{title}"
    "Private shared lesson."
export abstract agent Craft:
    role: "Read {{{{Lesson:title}}}}."
''')
        result = self.cli(after, "diff", "--base-tree", str(before), "--json")
        self.assertEqual(result[0], 0, result)
        self.assertEqual(
            [item["name"] for item in json.loads(result[1])["changed_declarations"]],
            ["parent.Lesson"],
        )

    def test_value_at_outer_team_reaches_member(self):
        source = SOURCE.replace('team T:', '''team Root: "Root"
    home: "."
    values:
        word: "old"
team T:''').replace('"Read the change."', '"Read {{agent:word}}."')
        result = json.loads(self.compare(
            source, source.replace('word: "old"', 'word: "newer"'), "--json"
        ))
        self.assertEqual([item["name"] for item in result["changed_declarations"]], ["Root"])
        self.assertEqual(result["homes"][0]["delta"]["always_on"], 2)

    def test_from_file_content_changes_source_hash(self):
        source = (
            'abstract agent Craft from "craft.md"\nteam T: "Team"\n'
            '    home: "pod"\n    member qa[Craft]: "QA"\n'
        )
        before, after = self.project(source), self.project(source)
        (before / "craft.md").write_text("Old role.\n")
        (after / "craft.md").write_text("New role.\n")
        code, output, error = self.cli(after, "diff", "--base-tree", str(before), "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(
            [item["name"] for item in json.loads(output)["changed_declarations"]], ["Craft"]
        )
