from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.home_support import HomeProject


class ClassesTests(HomeProject, unittest.TestCase):
    def test_files_in_own_and_inherited_class_text(self):
        root = self.project('''file Guide: "Guide title"
    path: "guide.md"
    section steps: "Steps"
        "Check."
file Basics: "Basics title"
    path: "basics.md"
    "Read."
file TitleOnly: "Only a title"
    path: "title.md"
    "Read."
abstract agent Base:
    role: """Read {{Guide:steps}} and {{TitleOnly:title}}.
Read first: {{load:Basics}}"""
abstract agent Child[Base]:
    inherit *
team T: "Team"
    home: "t"
    member qa[Child]: "QA"
''')
        code, output, error = self.cli(root, "classes", "--json")
        self.assertEqual(code, 0, error)
        base = json.loads(output)["agents"][0]
        self.assertEqual((base["loads"], base["links"]), (["Basics"], ["Guide"]))
        self.assertEqual((base["children"][0]["loads"], base["children"][0]["links"]), ([], []))
        code, output, error = self.cli(root, "classes", "Child", "--json")
        self.assertEqual(code, 0, error)
        view = json.loads(output)
        self.assertEqual((view["loads"], view["links"]), (["Basics"], ["Guide"]))
        code, output, error = self.cli(root, "classes", "--mermaid")
        self.assertEqual(code, 0, error)
        self.assertIn('class F_Basics["Basics"] {\n        <<file>>', output)
        self.assertIn("C_Base *-- F_Basics : loads", output)
        self.assertIn("C_Base ..> F_Guide : links", output)
        self.assertNotIn("F_TitleOnly", output)

    def test_inherited_file_keeps_its_module_scope(self):
        root = self.project('''from roles import Base
file Guide: "Other guide"
    path: "other.md"
    "Other."
abstract agent Child[Base]:
    inherit *
team T: "Team"
    home: "t"
    member qa[Child]: "QA"
''')
        (root / "prompts/roles").mkdir()
        (root / "prompts/roles/AGENTS.prompt").write_text('''file Guide: "Role guide"
    path: "role.md"
    "Role."
export abstract agent Base:
    role: "Read {{Guide}}."
''')
        code, output, error = self.cli(root, "classes", "Child", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["links"], ["roles.Guide"])

    def project_with_classes(self, suffix=""):
        source = (Path(__file__).resolve().parents[1] /
                  "examples/196_doctrine_classes/prompts/AGENTS.prompt").read_text()
        return self.project(source + suffix)

    def test_tree(self):
        root = self.project_with_classes()
        code, output, error = self.cli(root, "classes")
        self.assertEqual(code, 0, error)
        self.assertEqual(output.splitlines(), [
            "Agents",
            "QA  (abstract)  uses Craft  loads AppEngineering  links TestGuide  abstract policy",
            "├── AppQA  (abstract)",
            "│   └── Feature.qa  pods/feature/qa",
            "└── WebQA  (abstract)",
            "    ├── Growth.qa  pods/growth/qa",
            "    └── Product.qa  pods/product/qa  overrides testing",
            "",
            "Teams",
            "Pod  (abstract)  abstract win",
            "├── Feature  pods/feature  members qa",
            "├── Growth  pods/growth  members qa",
            "└── Product  pods/product  members qa",
        ])
        code, output, error = self.cli(root, "classes", "--json")
        self.assertEqual(code, 0, error)
        tree = json.loads(output)
        self.assertEqual((tree["format_version"], tree["view"]), (1, "tree"))
        self.assertEqual(tree["agents"][0]["children"][1]["name"], "WebQA")
        self.assertEqual(tree["teams"][0]["abstract_slots"], ["win"])

    def test_tree_keeps_team_with_missing_parent(self):
        root = self.project_with_classes('''\nteam Broken[Missing]: "broken"
    home: "bad"
    member qa: "QA"
        role: "Test."
''')
        for flags in ((), ("--json",)):
            with self.subTest(flags=flags):
                code, output, error = self.cli(root, "classes", *flags)
                self.assertEqual(code, 0, error)
                if flags:
                    self.assertEqual(json.loads(output)["teams"][0]["broken_parent"],
                                     {"name": "Missing", "reason": "not found"})
                    self.assertEqual(json.loads(output)["teams"][0]["members"], ["qa"])
                else:
                    self.assertIn("Broken  bad  members qa parent Missing not found", output)
                    self.assertNotIn("Broken.qa", output)

    def test_json_and_mermaid_are_exclusive(self):
        root = self.project_with_classes()
        self.assertEqual(self.cli(root, "classes", "--json", "--mermaid")[0], 2)

    def test_cycle_is_shown_at_the_top(self):
        root = self.project_with_classes('''\nabstract agent First[Second]:
    role: "First."
abstract agent Second[First]:
    role: "Second."
''')
        code, output, error = self.cli(root, "classes")
        self.assertEqual(code, 0, error)
        self.assertIn("First  (abstract) parent Second makes a cycle", output)
        self.assertIn("Second  (abstract) parent First makes a cycle", output)
        code, output, error = self.cli(root, "classes", "--json")
        self.assertEqual(code, 0, error)
        first = next(node for node in json.loads(output)["agents"] if node["name"] == "First")
        self.assertEqual(first["broken_parent"], {"name": "Second", "reason": "cycle"})

    def test_unmatched_selector(self):
        root = self.project_with_classes()
        code, _, error = self.cli(root, "classes", "Missing")
        self.assertEqual(code, 1)
        self.assertEqual(error.splitlines(), [
            "E640 compile error: No home matches", "", "Detail:",
            "- `Missing` matches no class, team, member or home.",
        ])

    def test_member_view(self):
        root = self.project_with_classes()
        code, output, error = self.cli(root, "classes", "Growth.qa", "--json")
        self.assertEqual(code, 0, error)
        result = json.loads(output)
        self.assertEqual(result["order"], ["Growth.qa", "WebQA", "QA"])
        self.assertEqual(result["team"], ["Growth", "Pod"])
        self.assertEqual(result["sections"], [
            {"key": "role", "from": "QA"}, {"key": "testing", "from": "QA"},
        ])
        self.assertEqual(result["values"], [
            {"name": "agent:subject", "value": "bet", "set_by": "QA"},
            {"name": "team:unit", "value": "bet", "set_by": "Growth"},
            {"name": "team:audience", "value": "new users", "set_by": "Growth"},
        ])
        code, text, error = self.cli(root, "classes", "pods/growth/qa")
        self.assertEqual(code, 0, error)
        self.assertEqual(text.splitlines(), [
            "Growth.qa  (member)  pods/growth/qa",
            "Order: Growth.qa, WebQA, QA",
            "Team: Growth, Pod",
            "",
            "Sections:",
            "  role     QA",
            "  testing  QA",
            "",
            "Values:",
            "  agent:subject  bet        QA",
            "  team:unit      bet        Growth",
            "  team:audience  new users  Growth",
        ])

    def test_member_view_with_broken_sibling(self):
        root = self.project_with_classes('''\nteam Broken[Missing]: "broken"
    home: "bad"
''')
        code, output, _ = self.cli(root, "classes", "Growth.qa", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["name"], "Growth.qa")

    def test_plain_agent_view(self):
        root = self.project('''agent A: "Reviewer"
    role: "Review {{agent:subject}}."
    values:
        subject: "changes"
''')
        code, output, error = self.cli(root, "classes", "A", "--target", "homes", "--json")
        self.assertEqual(code, 0, error)
        view = json.loads(output)
        self.assertEqual(view["team"], [])
        self.assertEqual(view["values"], [
            {"name": "agent:subject", "value": "changes", "set_by": "A"},
        ])

    def test_member_view_uses_imported_role_scope(self):
        root = self.project('''from shared import QA
team Growth: "growth"
    home: "growth"
    values:
        subject: "feature"
    member qa[QA]: "QA"
''')
        shared = root / "prompts/shared"
        shared.mkdir()
        (shared / "AGENTS.prompt").write_text('''workflow Craft: "Craft"
    "Test {{agent:subject}}."
export abstract agent QA:
    role: "Test."
    testing: Craft
''')
        code, output, error = self.cli(root, "classes", "Growth.qa", "--json")
        self.assertEqual(code, 0, error)
        view = json.loads(output)
        self.assertEqual(view["values"], [
            {"name": "agent:subject", "value": "feature", "set_by": "Growth"},
        ])
        self.assertEqual(view["sections"][1], {"key": "testing", "from": "shared.QA"})

    def test_team_home_and_member_without_class(self):
        root = self.project('''team Growth: "growth"
    home: "growth"
    role: "Work on {{team:unit}}."
    values:
        unit: "games"
    member qa: "QA"
        role: "Test {{team:audience}}."
''')
        code, output, error = self.cli(root, "classes", "growth", "--json")
        self.assertEqual(code, 0, error)
        view = json.loads(output)
        self.assertEqual(view["kind"], "team")
        self.assertEqual(view["members"], [{"key": "qa", "class": None}])
        self.assertEqual(view["reads"], [
            {"name": "team:unit", "default": "games", "set_by": "Growth"},
        ])
        code, output, error = self.cli(root, "classes", "Growth")
        self.assertEqual(code, 0, error)
        self.assertIn("Members:\n  qa\n", output)

    def test_class_defaults_belong_to_nearest_class(self):
        root = self.project('''abstract agent Base:
    role: "Test {{agent:subject}} for {{team:unit}}."
    values:
        subject: "base"
        unit: "not a team value"
abstract agent Child[Base]:
    inherit *
    values:
        subject: "child"
team Growth: "growth"
    home: "growth"
    values:
        unit: "games"
        subject: "team"
    member qa[Child]: "QA"
''')
        for name, default, setter in (("Base", "base", "Base"), ("Child", "child", "Child")):
            code, output, error = self.cli(root, "classes", name, "--json")
            self.assertEqual(code, 0, error)
            self.assertEqual(json.loads(output)["reads"], [
                {"name": "agent:subject", "default": default, "set_by": setter},
                {"name": "team:unit", "default": None, "set_by": None},
            ])
        code, output, error = self.cli(root, "classes", "Growth.qa", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["values"][0], {
            "name": "agent:subject", "value": "team", "set_by": "Growth",
        })

    def test_values_keep_whitespace_in_json_and_fold_it_in_text(self):
        root = self.project('''abstract agent Base:
    role: "Test {{agent:subject}}."
    values:
        subject: "one   two"
team Growth: "growth"
    home: "growth"
    member qa[Base]: "QA"
''')
        for selector in ("Base", "Growth.qa"):
            code, text, error = self.cli(root, "classes", selector)
            self.assertEqual(code, 0, error)
            self.assertIn("one two", text)
            code, output, error = self.cli(root, "classes", selector, "--json")
            self.assertEqual(code, 0, error)
            self.assertIn("one   two", output)

    def test_only_home_target_needs_no_team_or_flag(self):
        root = self.project('''agent A: "Reviewer"
    role: "Review."
''')
        for args in (("classes",), ("build", "."), ("check",), ("load", "A", "--runtime", "codex")):
            with self.subTest(args=args):
                code, _, error = self.cli(root, *args)
                self.assertEqual(code, 0, error)

    def test_overridden_member_is_a_team_change(self):
        root = self.project('''abstract team Pod: "pod"
    member qa: "QA"
        role: "Test."
team Growth[Pod]: "growth"
    home: "growth"
    override member qa: "QA"
        role: "Test more."
''')
        code, output, error = self.cli(root, "classes")
        self.assertEqual(code, 0, error)
        self.assertIn("Growth  growth  overrides qa", output)
        code, output, error = self.cli(root, "classes", "Pod", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["changed_below"], [
            {"owner": "Growth", "change": "overrides", "keys": ["qa"]},
        ])

    def test_name_wins_over_another_home(self):
        root = self.project('''team Alpha: "alpha"
    home: "Beta"
    role: "Work."
abstract agent Beta: "Beta class"
    role: "Work."
''')
        code, output, error = self.cli(root, "classes", "Beta", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["kind"], "abstract agent")

    def test_nested_entrypoint_and_imported_agent_without_home(self):
        root = self.project('''from shared.kit import Base
output Report: "Report"
    target: Message
        to: "lead"
    "Report."
agent Local: "Local"
    role: "Work."
    outputs: "Outputs"
        Report
team Pod: "pod"
    home: "pod"
    member a[Base]: "A"
''')
        (root / "prompts/main").mkdir()
        (root / "prompts/main/AGENTS.prompt").write_text((root / "prompts/AGENTS.prompt").read_text())
        (root / "prompts/AGENTS.prompt").unlink()
        (root / "prompts/shared").mkdir()
        (root / "prompts/shared/kit.prompt").write_text('''export abstract agent Base: "Base"
    role: "Base."
export agent Tool[Base]: "Tool"
    inherit role
''')
        config = root / "pyproject.toml"
        config.write_text(config.read_text().replace("prompts/AGENTS.prompt", "prompts/main/AGENTS.prompt"))
        code, output, error = self.cli(root, "classes", "--json")
        self.assertEqual(code, 0, error)
        tree = json.loads(output)
        self.assertIn("shared.kit.Base", [item["name"] for item in tree["agents"]])
        self.assertEqual(tree["teams"][0]["name"], "Pod")
        code, output, error = self.cli(root, "classes", "shared.kit.Tool", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["kind"], "agent")
        code, output, error = self.cli(root, "classes", "Local", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["sections"], [
            {"key": "role", "from": "Local"}, {"key": "outputs", "from": "Local"},
        ])

    def test_team_chain_excludes_enclosing_teams(self):
        root = self.project('''abstract agent QA:
    role: "Test {{team:unit}}."
team Outer: "outer"
    home: "pods"
    values:
        unit: "games"
team Inner: "inner"
    home: "pods/inner"
    member qa[QA]: "QA"
''')
        code, output, error = self.cli(root, "classes", "Inner.qa", "--json")
        self.assertEqual(code, 0, error)
        view = json.loads(output)
        self.assertEqual(view["team"], ["Inner"])
        self.assertEqual(view["values"][0]["set_by"], "Outer")

    def test_imported_inherited_members_use_the_team_name(self):
        root = self.project('''import roles
team Growth[roles.Pod]: "growth"
    home: "growth"
    values:
        unit: "games"
''')
        (root / "prompts/roles").mkdir()
        (root / "prompts/roles/AGENTS.prompt").write_text('''export abstract agent QA:
    role: "Test {{team:unit}}."
export abstract team Pod: "pod"
    member qa[QA]: "QA"
''')
        code, output, error = self.cli(root, "classes", "Growth", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["members"], [{"key": "qa", "class": "roles.QA"}])
        code, output, error = self.cli(root, "classes", "Growth.qa", "--json")
        self.assertEqual(code, 0, error)
        view = json.loads(output)
        self.assertEqual(view["order"], ["Growth.qa", "roles.QA"])
        self.assertEqual(view["sections"][0]["from"], "roles.QA")
        self.assertEqual(view["values"][0]["set_by"], "Growth")

    def test_mermaid_uses_distinct_ids_for_keywords_and_name_clashes(self):
        root = self.project('''workflow note: "Notes"
    "Read {{team:unit}}."
abstract agent note:
    role: "Work."
    testing: note
abstract agent T_a:
    role: "Work."
team T: "team"
    home: "t"
    member a: "A"
        role: "Work."
''')
        code, output, error = self.cli(root, "classes", "--mermaid")
        self.assertEqual(code, 0, error)
        self.assertIn('class C_note["note"]', output)
        self.assertIn('class W_note["note"]', output)
        self.assertIn('C_note *-- W_note', output)
        self.assertIn('        team:unit', output)
        self.assertIn('class C_T_a["T.a"]', output)
        self.assertIn('class C_T_a_2["T_a"]', output)

    def test_empty_mermaid_is_empty(self):
        root = self.project('''workflow Craft: "Craft"
    "Work."
''')
        code, output, error = self.cli(root, "classes", "--mermaid")
        self.assertEqual(code, 0, error)
        self.assertEqual(output, "")

    def test_markdown_slots_appear_in_class_and_mermaid(self):
        root = self.project('''abstract agent Qa from "specialists/qa.md"
team Pod: "pod"
    home: "pod"
    member qa[Qa]: "QA"
''')
        (root / "specialists").mkdir()
        (root / "specialists/qa.md").write_text('# QA\n\nTest.\n\n## Craft\n\nWork.\n')
        code, output, error = self.cli(root, "classes", "Qa", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["slots"], [{"key": "craft", "title": "Craft", "abstract": False}])
        code, output, error = self.cli(root, "classes", "--mermaid")
        self.assertEqual(code, 0, error)
        self.assertIn("        craft()", output)

    def test_mermaid_draws_classes_with_broken_parents_and_cycles(self):
        root = self.project('''abstract agent First[Second]:
    role: "First."
abstract agent Second[First]:
    role: "Second."
abstract agent Missing[Unknown]:
    role: "Missing."
abstract agent Broken:
    role: "Broken."
    work: "Work"
        use missing: Nope
team Pod: "pod"
    home: "pod"
''')
        code, output, error = self.cli(root, "classes", "--mermaid")
        self.assertEqual(code, 0, error)
        for name in ("First", "Second", "Missing", "Broken"):
            self.assertIn(f'class C_{name}["{name}"]', output)
