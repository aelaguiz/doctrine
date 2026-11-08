from __future__ import annotations

import json
import unittest

from tests.home_support import HomeProject


class ClassesSourceTests(HomeProject, unittest.TestCase):
    def test_class_and_mermaid_read_rosters_without_compiling(self):
        for example, fixture, selectors in (
            ("181_details", "project_team_words", ("Qa",)),
            ("193_small_team_end_to_end", "project", ("Pod", "GrowthPod", "FeaturePod")),
        ):
            root = self.project(example=example, fixture=fixture)
            for selector in (*selectors, None):
                args = ("classes", selector, "--json") if selector else ("classes", "--mermaid")
                with self.subTest(example=example, selector=selector):
                    code, _, error = self.cli(root, *args)
                    self.assertEqual(code, 0, error)

    def test_reads_follow_output_but_not_typed_slot_declarations(self):
        root = self.project('''output Report: "Report for {{team:boss}}"
    target: Message
        to: "{{team:boss}}"
    "Send to {{agent:inbox}}."
document Policy: "Policy"
    section summary: "Summary"
        "Check {{team:unit}} facts."
abstract agent Shape:
    role: "Test."
    abstract policy: Policy
abstract agent QA[Shape]:
    inherit *
    values:
        inbox: "the {{team:boss}} inbox"
    policy: Policy
    outputs: "Outputs"
        Report
team Pod: "pod"
    home: "pod"
    member qa[QA]: "QA"
''')
        code, output, error = self.cli(root, "classes", "QA", "--json")
        self.assertEqual(code, 0, error)
        names = [item["name"] for item in json.loads(output)["reads"]]
        self.assertEqual(set(names), {"team:boss", "agent:inbox"})
        code, output, error = self.cli(root, "classes", "--mermaid")
        self.assertEqual(code, 0, error)
        self.assertNotIn("team:unit", output)

    def test_overridden_workflow_is_not_in_class_uses(self):
        root = self.project('''workflow Craft: "Craft"
    "Test {{team:unit}}."
abstract agent QA:
    role: "Test."
    testing: Craft
abstract agent AppQA[QA]:
    inherit role
    override testing: "App testing"
        "Test on a phone."
team Pod: "pod"
    home: "pod"
    member qa[AppQA]: "QA"
''')
        code, output, error = self.cli(root, "classes", "AppQA", "--json")
        self.assertEqual(code, 0, error)
        view = json.loads(output)
        self.assertEqual(view["uses"], [])
        self.assertEqual(view["reads"], [])

    def test_markdown_class_has_its_own_slots(self):
        root = self.project('''abstract agent Qa from "specialists/qa.md"
team Pod: "pod"
    home: "pod"
    member qa[Qa]: "QA"
''')
        (root / "specialists").mkdir()
        (root / "specialists/qa.md").write_text('# QA\n\nTest.\n\n## Craft\n\nTest {{team:unit}}.\n')
        code, output, error = self.cli(root, "classes", "Qa", "--json")
        self.assertEqual(code, 0, error)
        view = json.loads(output)
        self.assertEqual(view["slots"], [{"key": "craft", "title": "Craft", "abstract": False}])
        self.assertEqual(view["reads"], [])
        code, output, error = self.cli(root, "classes", "--mermaid")
        self.assertEqual(code, 0, error)
        self.assertNotIn("team:unit", output)
        code, output, error = self.cli(root, "classes", "Pod.qa", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["values"], [])

    def test_sibling_source_uses_root_flow_names(self):
        root = self.project('''team Pod: "pod"
    home: "pod"
    member qa[QA]: "QA"
''')
        (root / "prompts/shared").mkdir()
        (root / "prompts/shared/roles.prompt").write_text('''abstract agent QA:
    role: "Test."
''')
        code, output, error = self.cli(root, "classes", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["agents"][0]["name"], "QA")
        code, output, error = self.cli(root, "classes", "QA", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["name"], "QA")
        code, output, error = self.cli(root, "classes", "Pod.qa", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["order"], ["Pod.qa", "QA"])
        self.assertEqual(json.loads(output)["sections"][0]["from"], "QA")

    def test_title_references_do_not_read_or_use_their_declarations(self):
        root = self.project('''document Guide: "Guide"
    section a: "A"
        "Read {{team:secret}}."
workflow Steps: "Steps"
    "Step {{team:hidden}}."
abstract agent QA:
    role: "See {{Guide:title}}, {{Steps:title}}, {{Guide}} and {{Steps}}."
team Pod: "pod"
    home: "pod"
    member qa[QA]: "QA"
''')
        code, output, error = self.cli(root, "classes", "QA", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["reads"], [])
        self.assertEqual(json.loads(output)["uses"], [])
        code, output, error = self.cli(root, "classes", "--mermaid")
        self.assertEqual(code, 0, error)
        self.assertNotIn("team:secret", output)
        self.assertNotIn("team:hidden", output)

    def test_typed_slot_does_not_use_same_named_workflow(self):
        root = self.project('''workflow Guide: "Workflow guide"
    "Read {{team:hidden}}."
document Guide: "Document guide"
    section a: "A"
        "Read {{team:secret}}."
abstract agent Shape:
    role: "Test."
    abstract guide: Guide
abstract agent QA[Shape]:
    inherit role
    guide: Guide
team Pod: "pod"
    home: "pod"
    member qa[QA]: "QA"
''')
        code, output, error = self.cli(root, "classes", "QA", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["uses"], [])
        self.assertEqual(json.loads(output)["reads"], [])
        code, output, error = self.cli(root, "classes", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["agents"][0]["children"][0]["uses"], [])
        code, output, error = self.cli(root, "classes", "--mermaid")
        self.assertEqual(code, 0, error)
        self.assertNotIn("team:hidden", output)
        self.assertNotIn("W_Guide", output)

    def test_class_reads_omit_builtin_facts_but_agent_values_keep_them(self):
        root = self.project('''abstract agent QA:
    role: "{{agent:key}} {{agent:title}} {{agent:home}} {{agent:folder}} {{team:members}} {{team:others}} {{team:unit}}"
team Pod: "pod"
    home: "pod"
    values:
        unit: "games"
    member qa[QA]: "QA"
    member dev: "Dev"
        role: "Build."
''')
        code, output, error = self.cli(root, "classes", "QA", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual([x["name"] for x in json.loads(output)["reads"]], ["team:unit"])
        code, output, error = self.cli(root, "classes", "Pod.qa", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual([x["name"] for x in json.loads(output)["values"]], [
            "agent:key", "agent:title", "agent:home", "agent:folder", "team:members", "team:others", "team:unit"])
        code, output, error = self.cli(root, "classes", "--mermaid")
        self.assertEqual(code, 0, error)
        self.assertNotIn("agent:title", output)
        self.assertIn("team:unit", output)
        root = self.project(example="193_small_team_end_to_end", fixture="project")
        code, output, error = self.cli(root, "classes", "Pod", "--json")
        self.assertEqual(code, 0, error)
        self.assertNotIn("team:members", [x["name"] for x in json.loads(output)["reads"]])
        self.assertNotIn("agent:title", [x["name"] for x in json.loads(output)["reads"]])

    def test_effective_and_own_workflow_reads(self):
        root = self.project('''workflow Detail: "Detail"
    "Check {{team:audience}}."
workflow Craft: "Craft"
    "Test {{team:unit}}."
    use detail: Detail
abstract agent QA:
    role: "Test."
    testing: Craft
abstract agent AppQA[QA]:
    inherit role
    override testing: "Phone test"
        "Check {{agent:phone}}."
team Pod: "pod"
    home: "pod"
    member qa[AppQA]: "QA"
''')
        code, output, error = self.cli(root, "classes", "QA", "--json")
        self.assertEqual(code, 0, error)
        view = json.loads(output)
        self.assertEqual(view["uses"], ["Craft", "Detail"])
        self.assertEqual([item["name"] for item in view["reads"]], ["team:unit", "team:audience"])
        code, output, error = self.cli(root, "classes", "AppQA", "--json")
        self.assertEqual(code, 0, error)
        view = json.loads(output)
        self.assertEqual(view["uses"], [])
        self.assertEqual([item["name"] for item in view["reads"]], ["agent:phone"])
        code, output, error = self.cli(root, "classes", "--mermaid")
        self.assertEqual(code, 0, error)
        self.assertIn('class C_AppQA["AppQA"] {\n        <<abstract>>\n        agent:phone\n        testing()\n    }', output)

    def test_inline_slot_does_not_use_workflow_with_class_name(self):
        root = self.project('''workflow QA: "Workflow"
    "Workflow text."
abstract agent QA:
    role: "Role."
    testing: "Tests"
        "Test."
team Pod: "pod"
    home: "pod"
''')
        code, output, error = self.cli(root, "classes", "QA", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["uses"], [])

