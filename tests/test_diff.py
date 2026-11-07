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

    def git_project(self, root):
        for args in (
            ("init", "-q"),
            ("config", "user.name", "Fixture"),
            ("config", "user.email", "fixture@example.com"),
            ("add", "."),
            ("commit", "-qm", "Fixture [skip ci]"),
        ):
            subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    def test_bad_base_is_e641(self):
        root = self.project(SOURCE)
        self.git_project(root)
        result = self.cli(root, "diff", "--base", "absent-revision")
        self.assertEqual(result[0], 1, result)
        self.assertIn("E641", result[2])
        self.assertNotIn("does not compile", result[2])

    def test_two_role_edit_reports_true_reach(self):
        source = '''abstract agent Qa:
    role: "You test."
abstract agent Writer:
    role: "You write."
team GrowthPod: "Growth"
    home: "pods/growth"
    member qa[Qa]: "QA"
    member writer[Writer]: "Writer"
team FeaturePod: "Feature"
    home: "pods/feature"
    member qa[Qa]: "QA"
    member writer[Writer]: "Writer"
'''
        new = source.replace("You test.", "You test changes.").replace(
            "You write.", "You write guides."
        )
        result = json.loads(self.compare(source, new, "--json"))
        self.assertEqual(
            [item["name"] for item in result["changed_declarations"]], ["Qa", "Writer"]
        )
        for declaration in result["changed_declarations"]:
            member = "qa" if declaration["name"] == "Qa" else "writer"
            self.assertEqual([item["home"] for item in declaration["homes"]], [
                f"pods/feature/{member}", f"pods/growth/{member}"
            ])
        source = '''workflow Lesson: "Lesson"
    "Shared text."
workflow Middle: "Middle"
    use lesson: Lesson
workflow Far: "Far"
    use middle: Middle
''' + source.replace('    role: "You test."', '    role: "You test."\n    work: Far').replace(
            '    role: "You write."', '    role: "You write."\n    work: Lesson'
        ) + '''rule R: "No lesson"
    scope:
        member: qa
    assertions:
        forbids load Lesson
    message: "No lesson."
'''
        code, _, error = self.cli(self.project(source), "check")
        self.assertEqual(code, 1, error)
        self.assertIn(
            "\n- It arrives by: GrowthPod.qa -> Qa -> Far -> Middle -> Lesson", error
        )

    def test_team_name_selects_its_members_in_diff(self):
        source = SOURCE + '''team Other: "Other"
    home: "other"
    member qa[Craft]: "QA"
'''
        result = json.loads(self.compare(
            source, source.replace("Read the change.", "Read all changes."), "T", "--json"
        ))
        self.assertEqual([home["home"] for home in result["homes"]], ["pod/qa"])
        self.assertEqual(
            [home["home"] for home in result["changed_declarations"][0]["homes"]], ["pod/qa"]
        )

    def test_removals_name_their_cause(self):
        source = '''team T: "Team"
    home: "pod"
    role: "Team text."
    member qa: "QA"
        role: "Test."
'''
        result = json.loads(self.compare(source, source.split('    member qa')[0], "--json"))
        self.assertEqual([item["name"] for item in result["changed_declarations"]], ["T.qa"])
        self.assertEqual(result["changed_declarations"][0]["homes"][0]["home"], "pod/qa")
        self.assertLess(result["changed_declarations"][0]["homes"][0]["delta"]["always_on"], 0)
        result = json.loads(self.compare(
            source, source.replace('    role: "Team text."\n', ''), "--json"
        ))
        self.assertEqual([item["name"] for item in result["changed_declarations"]], ["T"])
        self.assertEqual(
            [home["home"] for home in result["changed_declarations"][0]["homes"]],
            ["pod", "pod/qa"],
        )

    def test_one_member_edit_is_one_declaration(self):
        source = '''team T: "Team"
    home: "pod"
    member qa: "QA"
        role: "Test."
    member writer: "Writer"
        role: "Write."
'''
        result = json.loads(self.compare(
            source, source.replace("Test.", "Test changes."), "--json"
        ))
        self.assertEqual([item["name"] for item in result["changed_declarations"]], ["T.qa"])
        self.assertEqual([home["home"] for home in result["homes"]], ["pod/qa"])

    def test_with_deleted_file(self):
        before, after = self.project(SOURCE), self.project(SOURCE)
        for root in (before, after):
            (root / "prompts/other.prompt").write_text('''team Other: "Other"
    home: "other"
    role: "Other text."
''')
        self.git_project(after)
        (after / "prompts/other.prompt").unlink()
        (after / "prompts/AGENTS.prompt").write_text("Broken source.\n")
        for base in (("--base", "HEAD"), ("--base-tree", str(before))):
            with self.subTest(base=base):
                code, output, error = self.cli(
                    after, "diff", *base, "--with", "prompts/other.prompt", "--json"
                )
                self.assertEqual(code, 0, error)
                result = json.loads(output)
                self.assertEqual(
                    [item["name"] for item in result["changed_declarations"]], ["other.Other"]
                )
                self.assertEqual(result["outputs"], [
                    "HOMES.contract.json", "other/AGENTS.md", "other/CLAUDE.md"
                ])

    def test_prompt_root_outside_the_project(self):
        root = self.project('''import shared
team T: "Team"
    home: "pod"
    member qa[shared.Craft]: "QA"
''')
        app = root / "app"
        app.mkdir()
        (root / "prompts").rename(app / "prompts")
        (root / "pyproject.toml").rename(app / "pyproject.toml")
        config = app / "pyproject.toml"
        config.write_text(config.read_text() + (
            '[tool.doctrine.compile]\nadditional_prompt_roots = ["../shared/prompts"]\n'
        ))
        shared = root / "shared/prompts"
        shared.mkdir(parents=True)
        craft = shared / "shared.prompt"
        craft.write_text('''export abstract agent Craft:
    role: "Read {{agent:word}}."
    values:
        word: "old"
        unused: "No reader."
''')
        self.git_project(root)
        code, _, error = self.cli(app, "check")
        self.assertEqual(code, 0, error)
        self.assertIn("../shared/prompts/shared.prompt:5", error)
        craft.write_text(craft.read_text().replace('word: "old"', 'word: "newer"'))
        code, output, error = self.cli(app, "diff", "--json")
        self.assertEqual(code, 0, error)
        declaration, = json.loads(output)["changed_declarations"]
        self.assertEqual(declaration["name"], "shared.Craft")
        self.assertEqual(declaration["site"], "../shared/prompts/shared.prompt:1")

    def test_new_section_at_a_level_lists_homes_under_it(self):
        source = '''workflow Base: "Base"
    old: "Old"
        "Old text."
workflow Child[Base]: "Child"
    inherit *
workflow Middle: "Middle"
    use lesson: Child
workflow Outer: "Outer"
    use middle: Middle
team T: "Team"
    home: "pod"
    craft: Outer
    member qa: "QA"
        role: "Test."
    member writer: "Writer"
        role: "Write."
'''
        new = source.replace(
            'workflow Child', '    added: "Added"\n        "New text."\nworkflow Child'
        )
        result = json.loads(self.compare(source, new, "--json"))
        self.assertEqual(result["new_sections"], [{
            "origin": "Base", "path": ["added"], "homes": ["pod", "pod/qa", "pod/writer"]
        }])
        self.assertTrue(any(
            entry["path"] == ["craft", "middle", "lesson", "added"]
            for home in result["homes"] for entry in home["entries"]
        ))
        selected = json.loads(self.compare(source, new, "T.qa", "--json"))
        self.assertEqual(selected["new_sections"], [{
            "origin": "Base", "path": ["added"], "homes": ["pod/qa"]
        }])

    def test_stamped_member_keeps_its_team_module(self):
        source = '''import roles
team GrowthPod[roles.Pod]: "Growth"
    home: "pod"
    inherit *
'''
        before, after = self.project(source), self.project(source)
        for root, role in ((before, "Test."), (after, "Test changes.")):
            (root / "prompts/roles").mkdir()
            (root / "prompts/roles/AGENTS.prompt").write_text(f'''export workflow Lesson: "Lesson"
    "Shared text."
export abstract team Pod: "Pod"
    member qa: "QA"
        role: "{role}"
        work: Lesson
''')
        code, output, error = self.cli(after, "diff", "--base-tree", str(before), "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(
            [item["name"] for item in json.loads(output)["changed_declarations"]], ["GrowthPod.qa"]
        )
        (after / "prompts/AGENTS.prompt").write_text(source + '''rule R: "No lesson"
    scope:
        member: qa
    assertions:
        forbids load roles.Lesson
    message: "No lesson."
''')
        code, _, error = self.cli(after, "check")
        self.assertEqual(code, 1, error)
        self.assertIn("\n- It arrives by: GrowthPod.qa -> roles.Lesson", error)
        self.assertNotIn("roles.GrowthPod.qa", error)

    def test_roster_home_depends_on_members(self):
        source = '''team T: "Team"
    home: "pod"
    how: "How"
        roster calls: "Calls"
            call: "Call" = "{{agent:calls}}"
    member qa: "QA"
        role: "Test."
        values:
            calls: "Old call."
    member writer: "Writer"
        role: "Write."
        values:
            calls: "Write a guide."
'''
        result = json.loads(self.compare(
            source, source.replace("Old call.", "Newer call."), "--json"
        ))
        self.assertEqual([item["name"] for item in result["changed_declarations"]], ["T.qa"])
        self.assertEqual(
            [home["home"] for home in result["changed_declarations"][0]["homes"]],
            ["pod", "pod/qa", "pod/writer"],
        )

    def test_team_scope_on_abstract_team_is_rule001(self):
        for target in ("Pod", "roles.Foreign"):
            with self.subTest(target=target):
                root = self.project('''import roles
abstract team Pod: "Pod"
    member qa: "QA"
        role: "Test."
team T: "Team"
    home: "pod"
    member qa: "QA"
        role: "Test."
rule R: "Rule"
    scope:
        team: TARGET
    assertions:
        requires declare work
    message: "Read the work."
'''.replace("TARGET", target))
                (root / "prompts/roles").mkdir()
                (root / "prompts/roles/AGENTS.prompt").write_text('''export team Foreign: "Foreign"
    home: "other"
    member qa: "QA"
        role: "Test."
''')
                code, _, error = self.cli(root, "check")
                self.assertEqual(code, 1, error)
                self.assertIn("RULE001", error)
                self.assertEqual(self.cli(root, "build", "T.qa")[0], 0)

    def test_shipped_assertions_skip_teams(self):
        for scope in ('home: "**"', 'file_tree: "**"'):
            with self.subTest(scope=scope):
                source = SOURCE + f'''rule R: "Rule"
    scope:
        {scope}
    assertions:
        requires inherit Craft
    message: "Inherit the shared role."
'''
                result = self.cli(self.project(source), "check")
                self.assertEqual(result[0], 0, result)

    def test_forbids_load_sees_any_depth(self):
        source = '''workflow Lesson: "Lesson"
    secret: "Secret"
        "Deep shared words."
workflow Middle: "Middle"
    use lesson: Lesson
workflow Outer: "Outer"
    use middle: Middle
team T: "Team"
    home: "pod"
    member qa: "QA"
        role: "Test."
        craft: Outer
rule R: "No lesson"
    scope:
        member: qa
    assertions:
        forbids load Lesson
    message: "No lesson."
'''
        root = self.project(source)
        code, _, error = self.cli(root, "check")
        self.assertEqual(code, 1, error)
        self.assertIn("RULE007", error)
        code, output, error = self.cli(root, "where", "Deep shared words", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["matches"], [{
            "origin": "Lesson.secret", "site": "prompts/AGENTS.prompt:2", "homes": ["pod/qa"]
        }])
