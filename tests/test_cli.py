from __future__ import annotations

import json
import subprocess
import tomllib
import unittest
from contextlib import chdir
from pathlib import Path
from unittest.mock import patch

from tests.home_support import HomeProject
from doctrine import model
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import DoctrineError
from doctrine.parser import parse_file
from doctrine._compiler.home_map import build_home_map
from doctrine.emit_docs import _build_previous_turn_contexts, emit_target
from doctrine.emit_common import load_emit_targets
from doctrine._verify_corpus.manifest import _load_manifest
from doctrine.classes import agent_view


class CliTests(HomeProject, unittest.TestCase):
    def test_selected_build_checks_only_its_members_rules(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text() + '''rule AnalystWork: "Analyst work"
    scope:
        member: analyst
    assertions:
        requires declare work
    message: "Add work."
''')
        code, _, error = self.cli(root, "build", "GrowthPod.qa")
        self.assertEqual(code, 0, error)
        code, _, error = self.cli(root, "build", "GrowthPod.analyst")
        self.assertEqual(code, 1, error)
        self.assertIn("RULE005", error)

    def test_selected_build_with_rule_ignores_broken_sibling_team(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text() + '''team Other[Nope]: "Other"
    home: "pods/feature"
rule AnalystWork: "Analyst work"
    scope:
        member: analyst
    assertions:
        requires declare work
    message: "Add work."
''')
        code, _, error = self.cli(root, "build", "GrowthPod.qa")
        self.assertEqual(code, 0, error)
        self.assertIn("E299", error)

    def test_broken_parent_team_stops_selected_build_and_check(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        source = root / "prompts/AGENTS.prompt"
        original = source.read_text()
        for home, expected in ((".", 1), ("pods/feature", 0)):
            source.write_text(original + f'team Other[Nope]: "Other"\n    home: "{home}"\n')
            for command in ("build", "check"):
                with self.subTest(home=home, command=command):
                    code, _, error = self.cli(root, command, "GrowthPod.qa")
                    self.assertEqual(code, expected, error)
                    self.assertIn("E299", error)

    def test_check_handles_record_missing_files_key(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        (root / "HOMES.contract.json").write_text("{}")
        code, _, error = self.cli(root, "check")
        self.assertEqual(code, 1, error)
        self.assertIn("stale HOMES.contract.json", error)
        code, output, error = self.cli(root, "check", "--json")
        self.assertEqual(code, 1, error)
        self.assertIn({"path": "HOMES.contract.json", "state": "stale"}, json.loads(output)["paths"])

    def test_check_does_not_report_already_deleted_obsolete_file(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().split('    member analyst:')[0])
        (root / "pods/growth/analyst/AGENTS.md").unlink()
        code, _, error = self.cli(root, "check")
        self.assertEqual(code, 1, error)
        self.assertNotIn("obsolete pods/growth/analyst/AGENTS.md", error)

    def test_load_revision_marks_deleted_external_in_rows_and_full_headers(self):
        root = self.project(
            'team T: "Team"\n    home: "t"\n    member qa: "QA"\n        role: "Test."\n',
            settings='[tool.doctrine.runtimes.codex]\nexternal = [{path="outside.md"}]\n',
        )
        (root / "outside.md").write_text("External.\n")
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.git_project(root)
        (root / "outside.md").unlink()
        for extra in ((), ("--full",)):
            code, output, error = self.cli(root, "load", "T.qa", "--runtime", "codex", "--rev", "HEAD", *extra)
            self.assertEqual(code, 0, error)
            if extra:
                self.assertIn("===== outside.md (10) missing =====", output)
            else:
                self.assertRegex(output, r"outside\.md\s+10\s+missing")

    def test_exit_codes_for_build_check_and_load(self):
        for command in (("build",), ("check",), ("load", "GrowthPod.qa", "--full")):
            with self.subTest(command=command):
                root = self.project()
                self.assertEqual(self.cli(root, "build", ".")[0], 0)
                self.assertEqual(self.cli(root, *command)[0], 0)
                self.assertEqual(self.cli(root, *command, "--target", "absent")[0], 2)
                source = root / "prompts/AGENTS.prompt"
                source.write_text(source.read_text().replace("QA text.", "{{agent:missing}}"))
                code, _, error = self.cli(root, *command)
                self.assertEqual(code, 1)
                self.assertIn("E601", error)

    def test_load_marks_a_missing_runtime_link(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        (root / "pods/growth/qa/CLAUDE.md").unlink()
        code, output, error = self.cli(root, "load", "GrowthPod.qa", "--runtime", "claude", "--json")
        self.assertEqual(code, 0, error)
        files = json.loads(output)["homes"][0]["runtimes"]["claude"]["files"]
        self.assertEqual(files[-1]["path"], "pods/growth/qa/CLAUDE.md")
        self.assertFalse(files[-1]["on_disk"])
        self.assertTrue(files[0]["on_disk"])
        code, output, error = self.cli(root, "load", "GrowthPod.qa", "--runtime", "claude")
        self.assertEqual(code, 0, error)
        self.assertIn("pods/growth/qa/CLAUDE.md", output)
        self.assertIn("missing", output)
        code, output, error = self.cli(
            root, "load", "GrowthPod.qa", "--runtime", "claude", "--full"
        )
        self.assertEqual(code, 0, error)
        self.assertRegex(output, r"===== pods/growth/qa/CLAUDE\.md \(\d+\) missing =====")

    def test_load_revision_checks_the_live_runtime_link(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.git_project(root)
        (root / "pods/growth/qa/CLAUDE.md").unlink()
        code, output, error = self.cli(
            root, "load", "GrowthPod.qa", "--runtime", "claude", "--rev", "HEAD", "--json"
        )
        self.assertEqual(code, 0, error)
        row = json.loads(output)["homes"][0]["runtimes"]["claude"]["files"][-1]
        self.assertEqual(row["path"], "pods/growth/qa/CLAUDE.md")
        self.assertFalse(row["on_disk"])

    def test_rule_failure_preserves_every_built_file(self):
        root = self.project(example="186_rule_load_assertions", fixture="project_forbidden")
        source = root / "prompts/AGENTS.prompt"
        full = source.read_text()
        source.write_text(full.split('rule PodsSkipSpecialistsLesson:')[0])
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        source.write_text(full)
        before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1, error)
        self.assertIn("RULE007", error)
        self.assertEqual({path: path.read_bytes() for path in before}, before)

    def test_check_revision_compares_live_files(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.git_project(root)
        (root / "pods/growth/qa/AGENTS.md").write_text("Hand edit.\n")
        code, _, error = self.cli(root, "check", "GrowthPod.qa", "--rev", "HEAD")
        self.assertEqual(code, 1, error)
        self.assertIn("edited pods/growth/qa/AGENTS.md", error)
        self.assertNotIn("analyst", error)

    def test_where_finds_value_text(self):
        root = self.project(example="187_doctrine_diff")
        code, output, error = self.cli(root, "where", "YOU   FOLLOW the BET")
        self.assertEqual(code, 0, error)
        self.assertIn("PodQa.whom  prompts/AGENTS.prompt:3", output)
        self.assertIn("reaches 1 home: pods/growth/qa", output)
        self.assertNotIn("pods/feature/qa", output)

    def test_where_json(self):
        root = self.project(example="187_doctrine_diff")
        code, output, error = self.cli(root, "where", "YOU   FOLLOW the BET", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output), {
            "format_version": 1,
            "matches": [{
                "origin": "PodQa.whom", "site": "prompts/AGENTS.prompt:3",
                "homes": ["pods/growth/qa"],
            }],
            "closest": None,
        })
        code, output, error = self.cli(root, "where", "No such text", "--json")
        self.assertEqual(code, 1, error)
        self.assertEqual(json.loads(output), {"format_version": 1, "matches": [], "closest": None})

    def test_where_value_reach_and_selected_home(self):
        root = self.project(example="187_doctrine_diff")
        code, output, error = self.cli(root, "where", " BET ", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output), {
            "format_version": 1,
            "matches": [
                {"origin": "value unit", "site": "prompts/AGENTS.prompt:10",
                 "homes": ["pods/growth/qa"]},
                {"origin": "PodQa.whom", "site": "prompts/AGENTS.prompt:3",
                 "homes": ["pods/growth/qa"]},
            ],
            "closest": None,
        })
        code, output, error = self.cli(root, "where", "bet", "--home", "pods/feature/qa", "--json")
        self.assertEqual(code, 1, error)
        self.assertEqual(json.loads(output)["matches"], [])

        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace(
            '    member qa[PodQa]: "QA"',
            '    member qa[PodQa]: "QA"\n        values:\n            unit: "override"', 1))
        code, output, error = self.cli(root, "where", "bet")
        self.assertEqual(code, 0, error)
        self.assertEqual(output, "value unit  prompts/AGENTS.prompt:10\n  reaches 0 homes\n")
        code, output, error = self.cli(root, "where", "bet", "--home", "pods/growth/qa", "--json")
        self.assertEqual(code, 1, error)
        self.assertEqual(json.loads(output)["matches"], [])
        code, output, error = self.cli(root, "where", "override")
        self.assertEqual(code, 0, error)
        self.assertIn("value unit  prompts/AGENTS.prompt:13\n  reaches 1 home: pods/growth/qa", output)

    def test_where_closest_sentence_and_json(self):
        root = self.project(example="187_doctrine_diff")
        words = "You follow the bet from the design stage."
        code, output, error = self.cli(root, "where", words)
        self.assertEqual(code, 1, error)
        self.assertEqual(output, "No exact match. Closest:\n"
                         "PodQa.whom  prompts/AGENTS.prompt:3\n"
                         "  You follow the bet from the design on.\n"
                         "  reaches 1 home: pods/growth/qa\n")
        code, output, error = self.cli(root, "where", words, "--json")
        self.assertEqual(code, 1, error)
        self.assertEqual(json.loads(output), {
            "format_version": 1, "matches": [], "closest": {
                "origin": "PodQa.whom", "site": "prompts/AGENTS.prompt:3",
                "homes": ["pods/growth/qa"], "text": "You follow the bet from the design on.",
            },
        })
        code, output, error = self.cli(root, "where", words, "--home", "pods/feature/qa", "--json")
        self.assertEqual(code, 1, error)
        self.assertEqual(json.loads(output)["closest"]["homes"], ["pods/feature/qa"])
        code, output, error = self.cli(root, "where", "zebra quartz nebula", "--json")
        self.assertEqual(code, 1, error)
        self.assertIsNone(json.loads(output)["closest"])
        code, output, error = self.cli(root, "where", "zebra quartz nebula")
        self.assertEqual(code, 1, error)
        self.assertEqual(output, "")

    def test_where_value_reach_includes_homes_that_load_the_team(self):
        root = self.project('''team T: "Team"
    home: "pod"
    values:
        topic: "common work"
    role: "Review {{team:topic}}."
    member qa: "QA"
        role: "Test."
    member writer: "Writer"
        role: "Write."
''')
        code, output, error = self.cli(root, "where", "common work", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["matches"][0], {
            "origin": "value topic", "site": "prompts/AGENTS.prompt:4",
            "homes": ["pod", "pod/qa", "pod/writer"],
        })
        code, output, error = self.cli(root, "where", "common work", "--home", "pod", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["matches"][0]["homes"], ["pod"])

    def test_where_closest_breaks_ties_in_source_order(self):
        root = self.project('''team T: "Team"
    home: "pod"
    member zed: "Zed"
        role: "Size your testing to the risk of the change."
    member alpha: "Alpha"
        role: "Size your testing to the risk of the change."
''')
        code, output, error = self.cli(
            root, "where", "Size your testing to the risk of a change.", "--json")
        self.assertEqual(code, 1, error)
        self.assertEqual(json.loads(output)["closest"], {
            "origin": "T.zed.role", "site": "prompts/AGENTS.prompt:4",
            "homes": ["pod/zed"], "text": "Size your testing to the risk of the change.",
        })

    def test_where_closest_splits_punctuation_and_lines(self):
        root = self.project('''team T: "Team"
    home: "pod"
    member qa: "QA"
        role: "Check the plan! Read the notes?\\nReview the result"
''')
        for words, expected in (
            ("Check the plans!", "Check the plan!"),
            ("Read the note?", "Read the notes?"),
            ("Review the results", "Review the result"),
        ):
            with self.subTest(words=words):
                code, output, error = self.cli(root, "where", words, "--json")
                self.assertEqual(code, 1, error)
                self.assertEqual(json.loads(output)["closest"]["text"], expected)

    def test_where_reports_reach(self):
        root = self.project('''team T: "Team"
    home: "pod"
    role: "Read this shared sentence."
    member qa: "QA"
        role: "Test."
    member writer: "Writer"
        role: "Write."
''')
        result = self.cli(root, "where", "this shared sentence")
        self.assertEqual(result[0], 0, result)
        self.assertIn("reaches 3 homes: pod, pod/qa, pod/writer", result[1])
        result = self.cli(root, "where", "this shared sentence", "--home", "pod/qa")
        self.assertEqual(result[0], 0, result)
        self.assertIn("reaches 1 home: pod/qa", result[1])

    def test_where_searches_head_when_source_has_syntax_error(self):
        root = self.project(example="187_doctrine_diff")
        self.git_project(root)
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text() + "\nnot valid syntax\n")
        code, output, error = self.cli(root, "where", "You follow the bet")
        self.assertEqual(code, 0, error)
        self.assertIn("PodQa.whom  prompts/AGENTS.prompt:3", output)
        self.assertEqual(error, "Source has errors. Searching HEAD.\n")

    def test_where_does_not_search_head_for_a_missing_home(self):
        root = self.project(example="187_doctrine_diff")
        self.git_project(root)
        source = root / "prompts/AGENTS.prompt"
        text = source.read_text()
        source.write_text(text.replace('home: "pods/growth"', 'home: "pods/changed"'))
        code, output, error = self.cli(root, "where", "bet", "--home", "pods/growth/qa")
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("E640", error)
        self.assertNotIn("Searching HEAD", error)

    def test_where_prints_original_error_when_head_is_missing(self):
        root = self.project(example="187_doctrine_diff")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text() + "\nnot valid syntax\n")
        with chdir(root):
            with self.assertRaises(DoctrineError) as caught:
                parse_file(Path("prompts/AGENTS.prompt"))
            original = str(caught.exception)
        code, output, error = self.cli(root, "where", "You follow the bet")
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertEqual(error, original + "\n")

    def test_where_prints_original_error_when_head_is_broken(self):
        root = self.project(example="187_doctrine_diff")
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text() + "\ninvalid committed syntax\n")
        self.git_project(root)
        source.write_text("invalid working syntax\n")
        with chdir(root):
            with self.assertRaises(DoctrineError) as caught:
                parse_file(Path("prompts/AGENTS.prompt"))
            original = str(caught.exception)
        code, output, error = self.cli(root, "where", "You follow the bet")
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertEqual(error, original + "\n")

    def test_exit_codes_for_diff_and_where(self):
        root = self.project(example="187_doctrine_diff")
        for command in (("diff", "--base-tree", "base"), ("where", "You test")):
            with self.subTest(command=command):
                self.assertEqual(self.cli(root, *command)[0], 0)
                self.assertEqual(self.cli(root, *command, "--target", "absent")[0], 2)
        self.assertEqual(self.cli(root, "where", "No such text")[0], 1)
        path = root / "prompts/AGENTS.prompt"
        path.write_text(path.read_text().replace("You test.", "{{agent:missing}}"))
        self.assertEqual(self.cli(root, "diff", "--base-tree", "base")[0], 1)
        self.assertEqual(self.cli(root, "where", "You test")[0], 1)

    def test_load_rule_unknown_declaration_is_rule002(self):
        for target in ("Missing", "Lesson.missing", "T.missing"):
            with self.subTest(target=target):
                root = self.project('''workflow Lesson: "Lesson"
    "Shared text."
team T: "Team"
    home: "pod"
    member qa: "QA"
        role: "Test."
        work: Lesson
rule R: "Rule"
    scope:
        member: qa
    assertions:
        requires load TARGET
    message: "Read the lesson."
'''.replace("TARGET", target))
                result = self.cli(root, "check")
                self.assertEqual(result[0], 1, result)
                self.assertIn("RULE002", result[2])
                self.assertEqual(self.cli(root, "build", "T.qa")[0], 1)

    def test_whole_build_checks_unknown_load_target_outside_all_homes(self):
        root = self.project('''team T: "Team"
    home: "pod"
    member qa: "QA"
        role: "Test."
''')
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text() + '''rule R: "Rule"
    scope:
        member: absent
    assertions:
        requires load Missing
    message: "Read the lesson."
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("RULE002", error)
        self.assertEqual(self.cli(root, "build", "T.qa")[0], 0)

    def test_home_scope_matches_agent_outside_a_team(self):
        root = self.project('''workflow Lesson: "Lesson"
    "Shared text."
agent Qa:
    role: "Test."
rule R: "Rule"
    scope:
        home: "qa"
    assertions:
        requires load Lesson
    message: "Read the lesson."
''')
        result = self.cli(root, "check", "--target", "homes")
        self.assertEqual(result[0], 1, result)
        self.assertIn("RULE006", result[2])
        self.assertIn("\n- Qa must load Lesson.", result[2])

    def test_named_team_scope_matches_only_its_members(self):
        source = '''workflow Lesson: "Lesson"
    "Shared text."
team A: "First team"
    home: "first"
    member qa: "QA"
        role: "Test."
        work: Lesson
team B: "Second team"
    home: "second"
    member qa: "QA"
        role: "Test."
rule R: "Rule"
    scope:
        team: A
    assertions:
        requires load Lesson
    message: "Read the lesson."
'''
        root = self.project(source)
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.assertEqual(self.cli(root, "check")[0], 0)
        result = self.cli(self.project(source.replace('team: A', 'team: B')), "check")
        self.assertEqual(result[0], 1, result)
        self.assertIn("RULE006", result[2])
        self.assertIn("B.qa must load Lesson.", result[2])

    def test_load_rules_stay_in_their_flow(self):
        root = self.project('''import worker
workflow Lesson: "Lesson"
    "Root lesson."
team T: "Team"
    home: "pod"
    role: "Root role."
rule R: "Root rule"
    scope:
        agent_tag: A
    assertions:
        requires load Lesson
    message: "Read the lesson."
''')
        (root / "prompts/worker").mkdir()
        (root / "prompts/worker/AGENTS.prompt").write_text('''workflow Local: "Local lesson"
    "Local text."
export agent A:
    role: "Test."
    work: Local
rule R: "Local rule"
    scope:
        agent_tag: A
    assertions:
        requires load Local
    message: "Read the local lesson."
''')
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        result = self.cli(root, "check")
        self.assertEqual(result[0], 0, result)

    def test_build_checks_load_rules(self):
        root = self.project(example="186_rule_load_assertions", fixture="project_forbidden")
        result = self.cli(root, "build", ".")
        self.assertEqual(result[0], 1, result)
        self.assertIn("RULE007", result[2])

    def test_home_glob_star_stays_in_one_segment(self):
        source = '''workflow Lesson: "Lesson"
    "Shared text."
team T: "Team"
    home: "pods/team"
    member qa: "QA"
        role: "Test."
        work: Lesson
rule R: "Rule"
    scope:
        home: "pods/*"
    assertions:
        forbids load Lesson
    message: "No lesson."
'''
        root = self.project(source)
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.assertEqual(self.cli(root, "check")[0], 0)
        result = self.cli(self.project(source.replace("pods/*", "pods/**")), "check")
        self.assertEqual(result[0], 1, result)
        self.assertIn("RULE007", result[2])

    def test_emit_docs_checks_load_rules_for_compiled_homes(self):
        source = '''workflow Lesson: "Lesson"
    "Shared text."
agent Qa:
    role: "Test."
rule R: "Rule"
    scope:
        agent_tag: Qa
    assertions:
        requires load Lesson
    message: "Read the lesson."
'''
        root = self.project(source)
        target = load_emit_targets(root / "pyproject.toml")["homes"]
        with self.assertRaises(DoctrineError) as caught:
            emit_target(target)
        self.assertEqual(caught.exception.code, "RULE006")
        self.assertFalse((root / "AGENTS.md").exists())
        path = root / "prompts/AGENTS.prompt"
        path.write_text(source.replace('    role: "Test."', '    role: "Test."\n    work: Lesson'))
        self.assertTrue(emit_target(target))

    def git_project(self, root):
        for args in (
            ("init", "-q"),
            ("config", "user.name", "Fixture"),
            ("config", "user.email", "fixture@example.com"),
            ("add", "."),
            ("commit", "-qm", "Fixture [skip ci]"),
        ):
            subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    def test_build_writes_only_selected_folders(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        before = (root / "pods/growth/analyst/AGENTS.md").read_bytes()
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace("QA text.", "New QA text."))
        self.assertEqual(self.cli(root, "build", "GrowthPod.qa")[0], 0)
        self.assertIn("New QA text.", (root / "pods/growth/qa/AGENTS.md").read_text())
        self.assertEqual((root / "pods/growth/analyst/AGENTS.md").read_bytes(), before)

    def test_selected_build_fails_when_a_loaded_parent_fails(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        parent = root / "pods/growth/AGENTS.md"
        member = root / "pods/growth/qa/AGENTS.md"
        before = parent.read_bytes(), member.read_bytes()
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace("Team text.", "{{agent:missing}}"))
        code, _, error = self.cli(root, "build", "GrowthPod.qa")
        self.assertEqual(code, 1)
        self.assertIn("E601", error)
        self.assertEqual((parent.read_bytes(), member.read_bytes()), before)

    def test_selected_build_survives_an_unrelated_semantic_error(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace("Analyst text.", "{{agent:missing}}"))
        code, _, error = self.cli(root, "build", "GrowthPod.qa")
        self.assertEqual(code, 0, error)

    def test_selected_build_fails_for_stale_level(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        path = root / "prompts/AGENTS.prompt"
        path.write_text(path.read_text().replace("Team text.", "New team text."))
        result = self.cli(root, "build", "GrowthPod.qa")
        self.assertEqual(result[0], 1)
        self.assertIn("`pods/growth/qa` loads `pods/growth/AGENTS.md`, which is out of date.", result[2])

    def test_check_mode_reports_stale_edited_missing(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        path = root / "prompts/AGENTS.prompt"
        path.write_text(path.read_text().replace("Team text.", "New team text."))
        (root / "pods/growth/qa/AGENTS.md").write_text("Hand edit.\n")
        (root / "pods/growth/analyst/CLAUDE.md").unlink()
        before = (root / "pods/growth/AGENTS.md").read_bytes()
        code, output, error = self.cli(root, "check", ".")
        self.assertEqual(code, 1, error)
        for line in (
            "stale pods/growth/AGENTS.md",
            "edited pods/growth/qa/AGENTS.md",
            "missing pods/growth/analyst/CLAUDE.md",
        ):
            self.assertIn(line, error)
        self.assertEqual((root / "pods/growth/AGENTS.md").read_bytes(), before)

    def test_e634_names_section_and_origin(self):
        root = self.project(
            (
                'abstract agent Role:\n    role: "Test."\n    work: "Your job"\n        '
                '"Do the work."\nteam T: "Team"\n    home: "pod"\n    member qa[Role]: '
                '"QA"\n'
            )
        )
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        path = root / "pod/qa/AGENTS.md"
        path.write_text(path.read_text().replace("Do the work.", "Hand edit."))
        result = self.cli(root, "build", ".")
        self.assertEqual(result[0], 1)
        self.assertIn("Your job: Role at prompts/AGENTS.prompt:3", result[2])

    def test_e634_writes_nothing(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        path = root / "pods/growth/qa/AGENTS.md"
        path.write_text(path.read_text() + "Hand edit.\n")
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace("Team text.", "New text."))
        before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
        self.assertEqual(self.cli(root, "build", ".")[0], 1)
        self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_force_overwrites_edit(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        path = root / "pods/growth/qa/AGENTS.md"
        clean = path.read_bytes()
        path.write_text("Hand edit.\n")
        self.assertEqual(self.cli(root, "build", ".", "--force")[0], 0)
        self.assertEqual(path.read_bytes(), clean)

    def test_force_removes_edited_obsolete_file(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        (root / "pods/growth/analyst/AGENTS.md").write_text("Hand edit.\n")
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().split("    member analyst:")[0])
        self.assertEqual(self.cli(root, "build", ".", "--force")[0], 0)
        self.assertFalse((root / "pods/growth/analyst/AGENTS.md").exists())

    def test_rev_extracts_only_what_the_result_depends_on(self):
        root = self.project(
            (
                'abstract agent Role from "craft.md"\nteam T: "Team"\n    home: "pod"\n    '
                'member qa[Role]: "QA"\n'
            )
        )
        (root / "craft.md").write_text("Role from revision.\n")
        (root / "unrelated.bin").write_bytes(b"Not a dependency.")
        self.git_project(root)
        archive_paths = []
        original = subprocess.check_output

        def capture(args, **kwargs):
            if args[:2] == ["git", "archive"]:
                archive_paths.extend(args[args.index("--") + 1 :])
            return original(args, **kwargs)

        with patch("subprocess.check_output", side_effect=capture):
            result = self.cli(root, "build", ".", "--rev", "HEAD")
        self.assertEqual(result[0], 0, result)
        self.assertEqual(set(archive_paths), {"pyproject.toml", "prompts", "craft.md"})
        self.assertIn("Role from revision.", (root / "pod/qa/AGENTS.md").read_text())

    def test_rev_reads_codex_limit_from_revision(self):
        root = self.project(example="183_load_budgets")
        project = root / "pyproject.toml"
        project.write_text(project.read_text().replace("limit = 800", ""))
        (root / ".codex").mkdir()
        config = root / ".codex/config.toml"
        config.write_text("project_doc_max_bytes = 800\n")
        self.git_project(root)
        config.write_text("project_doc_max_bytes = 999999\n")
        result = self.cli(root, "check", "--rev", "HEAD")
        self.assertEqual(result[0], 1, result)
        self.assertIn("of 800 bytes on codex", result[2])

    def test_level_no_longer_emitted_needs_full_build(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace('    role: "Team text."\n', ""))
        result = self.cli(root, "build", "GrowthPod.qa")
        self.assertEqual(result[0], 1)
        self.assertIn("E635", result[2])
        result = self.cli(root, "check", "GrowthPod.qa")
        self.assertEqual(result[0], 1)
        self.assertIn("stale pods/growth/AGENTS.md", result[2])

    def test_with_overlays_one_file(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.git_project(root)
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace("QA text.", "Changed QA."))
        (root / "pyproject.toml").write_text("An unrelated unfinished edit.")
        result = self.cli(
            root, "build", "GrowthPod.qa", "--rev", "HEAD", "--with", "prompts/AGENTS.prompt"
        )
        self.assertEqual(result[0], 0, result)
        self.assertIn("Changed QA.", (root / "pods/growth/qa/AGENTS.md").read_text())

    def test_e640_selector(self):
        root = self.project()
        self.assertIn("`missing` matches no home.", self.cli(root, "build", "missing")[2])

    def test_e641_revision(self):
        root = self.project()
        self.git_project(root)
        result = self.cli(root, "build", ".", "--rev", "unknown-revision")
        self.assertEqual(result[0], 1)
        self.assertIn("`unknown-revision` is not a revision in this repository.", result[2])

    def test_console_scripts_declared(self):
        root = Path(__file__).resolve().parents[1]
        scripts = tomllib.loads((root / "pyproject.toml").read_text())["project"]["scripts"]
        self.assertEqual(scripts["doctrine"], "doctrine.cli:main")
        self.assertEqual(scripts["doctrine-agents"], "doctrine.cli:main")

    def test_build_fails_on_budget(self):
        root = self.project("""team T: "Team"
    home: "t"
    role: "Team text."
    budget:
        codex: 1
""")
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1, error)
        self.assertIn("E630", error)
        self.assertFalse((root / "t/AGENTS.md").exists())
        code, _, error = self.cli(root, "build", ".", "--force")
        self.assertEqual(code, 1, error)
        self.assertIn("E630", error)
        self.assertFalse((root / "t/AGENTS.md").exists())

    def test_check_fails_on_budget_and_rule(self):
        for source, error_code in (
            (
                (
                    'team T: "Team"\n    home: "t"\n    role: "Team text."\n    '
                    "budget:\n        codex: 1\n"
                ),
                "E630",
            ),
            (
                (
                    'rule HasWork: "Has Work"\n    scope:\n        agent_tag: A\n    '
                    'assertions:\n        requires declare work\n    message: "Keep work."\n'
                    'agent A:\n    role: "Agent."\nteam T: "Team"\n    home: "t"\n    role: '
                    '"Team."\n'
                ),
                "RULE005",
            ),
        ):
            with self.subTest(error_code=error_code):
                root = self.project(source)
                code, _, error = self.cli(root, "check")
                self.assertEqual(code, 1)
                self.assertIn(error_code, error)
                self.assertFalse((root / "t/AGENTS.md").exists())

    def test_check_json_shape(self):
        for settings in (
            "",
            "[tool.doctrine.runtimes.codex]\nlimit = 1\n",
            '[tool.doctrine.runtimes.codex]\nlimit = 1\nover = "warn"\n',
        ):
            with self.subTest(settings=settings):
                root = self.project(
                    'team T: "Team"\n    home: "t"\n    role: "Team text."\n', settings=settings
                )
                plain_code, _, plain_error = self.cli(root, "check")
                code, output, error = self.cli(root, "check", "--json")
                self.assertEqual(code, plain_code)
                self.assertEqual(error, "")
                result = json.loads(output)
                self.assertEqual(
                    set(result), {"format_version", "ok", "homes", "errors", "warnings", "paths"}
                )
                self.assertEqual(result["format_version"], 1)
                self.assertEqual(result["homes"], 1)
                self.assertEqual(result["ok"], code == 0)
                for finding in result["errors"] + result["warnings"]:
                    self.assertEqual(set(finding), {"code", "text"})
                    self.assertIn(finding["text"], plain_error)
                    self.assertTrue(finding["text"].startswith(finding["code"]))
                if settings:
                    self.assertEqual(
                        len(
                            result["warnings"] if 'over = "warn"' in settings else result["errors"]
                        ),
                        1,
                    )
        root = self.project('team T: "Team"\n    home: "t"\n    role: "{{agent:missing}}"\n')
        code, output, error = self.cli(root, "check", "--json")
        self.assertEqual(code, 1)
        self.assertEqual(error, "")
        self.assertEqual(json.loads(output)["errors"][0]["code"], "E601")

    def test_e634_section_gone_from_source(self):
        source = 'team T: "Team"\n    home: "t"\n    work: "Old work"\n        "Do the work."\n'
        root = self.project(source)
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        path = root / "t/AGENTS.md"
        path.write_text(path.read_text().replace("Do the work.", "Hand edit."))
        (root / "prompts/AGENTS.prompt").write_text(
            'team T: "Team"\n    home: "t"\n    role: "New work."\n'
        )
        before = path.read_bytes()
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("- Old work: no longer in source", error)
        self.assertEqual(path.read_bytes(), before)

    def test_e634_matches_repeated_titles_in_order(self):
        root = self.project("""abstract agent Base:
    role: "Test."
    first: "Same"
        "First."
    second: "Same"
        "Second."
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        override second: "Same"
            "Changed."
""")
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        path = root / "t/qa/AGENTS.md"
        path.write_text(path.read_text().replace("Changed.", "Hand edit."))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("- Same: T.qa at prompts/AGENTS.prompt:10", error)
        self.assertNotIn("- Same: Base", error)

    def test_e634_companion_names_only_its_source(self):
        root = self.project(
            (
                'team T: "Team"\n    home: "t"\n    work: "Work"\n        '
                'details:\n            "Long case."\n'
            )
        )
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        path = root / "t/DETAILS.md"
        path.write_text(path.read_text().replace("Long case.", "Hand edit."))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("`t/DETAILS.md` was edited by hand.", error)
        self.assertIn("source=prompts/AGENTS.prompt", error)
        self.assertNotIn("- Work:", error)

    def test_source_and_target_usage_errors(self):
        root = self.project()
        for verb in ("build", "check", "load"):
            with self.subTest(verb=verb):
                code, _, error = self.cli(root, verb, "--with", "prompts/AGENTS.prompt")
                self.assertEqual(code, 2)
                self.assertIn("--with needs --rev", error)
        config = root / "pyproject.toml"
        config.write_text(
            config.read_text() + "\n[[tool.doctrine.emit.targets]]\n"
            'name = "other"\nentrypoint = "prompts/AGENTS.prompt"\n'
            'output_dir = "other"\n'
        )
        for verb in ("build", "check", "load"):
            with self.subTest(verb=verb):
                code, _, error = self.cli(root, verb)
                self.assertEqual(code, 2)
                self.assertEqual(error, "Choose a target with --target.\n")

    def test_build_json(self):
        root = self.project()
        code, output, error = self.cli(root, "build", ".", "--json")
        self.assertEqual(code, 0, error)
        result = json.loads(output)
        self.assertEqual(
            set(result), {"format_version", "written", "unchanged", "removed"}
        )
        self.assertEqual(result["format_version"], 1)
        expected = sorted(
            ["HOMES.contract.json", "pods/growth/TEAM.contract.json"]
            + [
                f"{home}/{filename}"
                for home in ("pods/growth", "pods/growth/qa", "pods/growth/analyst")
                for filename in ("AGENTS.md", "CLAUDE.md")
            ]
        )
        self.assertEqual(result["written"], expected)
        for key in ("unchanged", "removed"):
            self.assertEqual(result[key], [])

    def test_e634_file_written_by_hand(self):
        root = self.project()
        path = root / "pods/growth/AGENTS.md"
        path.parent.mkdir(parents=True)
        path.write_text("Hand text.\n")
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("E634 compile error: Hand edit in a compiled file", error)
        self.assertIn("`pods/growth/AGENTS.md` was written by hand.", error)
        self.assertEqual(path.read_text(), "Hand text.\n")
        self.assertFalse((root / "pods/growth/TEAM.contract.json").exists())

    def test_e634_binary_file_written_by_hand(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        (root / "pods/growth/qa/AGENTS.md").write_bytes(b"Hand written: \xff\n")
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("E634", error)
        self.assertIn("was written by hand.", error)
        self.assertNotIn("Traceback", error)

    def test_every_compiling_corpus_agent_builds(self):
        examples = Path(__file__).resolve().parents[1] / "examples"
        prompts = {
            case.prompt_path
            for manifest in examples.glob("*/cases.toml")
            if int(manifest.parent.name.split("_")[0]) <= 184
            for case in _load_manifest(manifest)
            if case.kind not in ("parse_fail", "cli_contract")
        }
        count = 0
        for path in sorted(prompts):
            try:
                session = CompilationSession(parse_file(path), evaluate_rules=False)
            except DoctrineError:
                continue
            for unit in session.root_flow.units_by_path.values():
                for agent in unit.prompt_file.declarations:
                    if isinstance(agent, model.Agent) and not agent.abstract:
                        with self.subTest(path=path, agent=agent.name):
                            try:
                                roots = tuple(
                                    (owner, declaration.name)
                                    for owner in session.root_flow.units_by_path.values()
                                    for declaration in owner.prompt_file.declarations
                                    if isinstance(declaration, model.Agent)
                                    and not declaration.abstract
                                )
                                compiled = session.compile_agent_from_unit(
                                    unit,
                                    agent.name,
                                    previous_turn_contexts=_build_previous_turn_contexts(
                                        session, agent_roots=roots
                                    ),
                                )
                            except DoctrineError:
                                continue
                            build_home_map(compiled)
                            with patch("doctrine.classes.compile_homes", return_value=(
                                {"home": {"compiled": compiled}}, {}, [], False
                            )):
                                agent_view(None, session, agent.name, unit, agent, "home")
                            count += 1
        self.assertGreater(count, 350)

    def test_error_in_unselected_home_cannot_stop_build(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        path = root / "prompts/AGENTS.prompt"
        path.write_text(path.read_text().replace("Analyst text.", "{{agent:missing}}"))
        code, _, error = self.cli(root, "build", "pods/growth/qa")
        self.assertEqual(code, 0, error)
        self.assertTrue((root / "pods/growth/qa/AGENTS.md").exists())
        self.assertTrue((root / "pods/growth/analyst/AGENTS.md").exists())
        path.write_text(path.read_text().replace("Team text.", "{{agent:missing}}"))
        code, _, error = self.cli(root, "build", "pods/growth/qa")
        self.assertEqual(code, 1, error)
        self.assertIn("E601", error)
        self.assertTrue((root / "pods/growth/AGENTS.md").exists())

    def test_bad_budget_or_external_stops_build(self):
        for budget, settings, diagnostic in (
            ("        codex: 0\n", "", "E631"),
            ("", "[tool.doctrine.runtimes.codex]\nlimt = 10\n", "E632"),
            ("", '[tool.doctrine.runtimes.codex]\nexternal = [{path="missing.md"}]\n', "E633"),
        ):
            with self.subTest(diagnostic=diagnostic):
                source = 'team T: "Team"\n    home: "t"\n    role: "Test."\n'
                root = self.project(
                    source + ("    budget:\n" + budget if budget else ""), settings=settings
                )
                code, output, error = self.cli(root, "build", ".")
                self.assertEqual(code, 1, error)
                self.assertIn(diagnostic, error)
                self.assertFalse((root / "t/AGENTS.md").exists())
                self.assertNotIn("W306", error)
        root = self.project(
            'team T: "Team"\n    home: "t"\n    role: "Test."\n',
            runtimes='["codex"]',
            settings=('[tool.doctrine.runtimes.claude]\nexternal = [{path="absent.md"}]\n'),
        )
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertNotIn("E633", error)

    def test_build_warns_only_for_selected_homes(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        path = root / "pyproject.toml"
        path.write_text(path.read_text() + "[tool.doctrine.runtimes.codex]\nlimit = 10\nover = \"warn\"\n")
        code, _, error = self.cli(root, "build", "GrowthPod.qa")
        self.assertEqual(code, 0, error)
        self.assertIn("W306 over budget: pods/growth/qa loads", error)
        self.assertNotIn("budget: pods/growth loads", error)
        self.assertNotIn("budget: pods/growth/analyst loads", error)

    def test_broken_unrelated_target_cannot_stop_build(self):
        root = self.project()
        path = root / "pyproject.toml"
        path.write_text(
            path.read_text() + "\n[[tool.doctrine.emit.targets]]\n"
            'name = "broken"\nentrypoint = "absent/AGENTS.prompt"\n'
            'output_dir = "other"\n'
        )
        with patch("doctrine.home_commands.CompilationSession", wraps=CompilationSession) as make:
            code, _, error = self.cli(root, "build", "--target", "homes")
        self.assertEqual(code, 0, error)
        self.assertEqual(make.call_count, 1)

    def test_rule_in_soul_cannot_stop_build(self):
        root = self.project("import worker\n")
        package = root / "prompts/worker"
        package.mkdir()
        (package / "AGENTS.prompt").write_text('export agent A:\n    role: "Test."\n')
        (package / "SOUL.prompt").write_text("""rule HasWork: "Has Work"
    scope:
        agent_tag: A
    assertions:
        requires declare work
    message: "Keep work."
agent A:
    role: "Soul."
""")
        code, _, error = self.cli(root, "build", "--target", "homes")
        self.assertEqual(code, 1, error)
        self.assertIn("RULE005", error)
        self.assertFalse((root / "worker/SOUL.md").exists())
        code, _, error = self.cli(root, "check", "--target", "homes")
        self.assertEqual(code, 1)
        self.assertIn("RULE005", error)

    def test_selected_build_skips_hand_written_files(self):
        root = self.project()
        path = root / "AGENTS.md"
        path.write_text("Hand written.\n")
        code, _, error = self.cli(root, "build", "pods/growth", "GrowthPod.qa")
        self.assertEqual(code, 0, error)
        self.assertEqual(path.read_text(), "Hand written.\n")

    def test_broken_team_elsewhere_cannot_stop_build(self):
        for problem, diagnostic in (("parent", "Missing"), ("plan", "E299"), ("collision", "E607")):
            with self.subTest(problem=problem):
                root = self.project()
                self.assertEqual(self.cli(root, "build", ".")[0], 0)
                source = root / "prompts/AGENTS.prompt"
                if problem == "parent":
                    source.write_text(source.read_text() +
                        'team FeaturePod[Missing]: "Feature"\n    home: "pods/feature"\n')
                    broken = "FeaturePod"
                elif problem == "plan":
                    source.write_text("import worker\n" + source.read_text())
                    package = root / "prompts/worker"
                    package.mkdir()
                    (package / "AGENTS.prompt").write_text('export agent A:\n    role: "Work."\n')
                    (package / "extra.prompt").write_text('workflow Extra: "Extra"\n    "Text."\n')
                    broken = "A"
                else:
                    source.write_text(source.read_text() +
                        'team First: "First"\n    home: "other"\n    role: "First."\n'
                        'team Second: "Second"\n    home: "other"\n    role: "Second."\n')
                    broken = "other"
                code, _, error = self.cli(root, "build", "pods/growth/qa")
                self.assertEqual(code, 0, error)
                self.assertTrue((root / "pods/growth/qa/AGENTS.md").is_file())
                self.assertTrue((root / "pods/growth/AGENTS.md").exists())
                selectors = [".", broken]
                if problem == "parent":
                    selectors.append("pods")
                elif problem == "collision":
                    selectors.append("Second")
                for selector in selectors:
                    code, _, error = self.cli(root, "build", selector)
                    self.assertEqual(code, 1)
                    self.assertIn(diagnostic, error)
                    self.assertNotIn("E640", error)
                if problem != "collision":
                    code, _, error = self.cli(root, "build", "absent")
                    self.assertEqual(code, 1)
                    self.assertIn(diagnostic, error)
                    self.assertNotIn("E640", error)

    def test_malformed_settings_are_e632(self):
        for setting, external, config in (
            ('external = [1]', None, None),
            ('external = [{}]', None, None),
            ('external = [{path=1}]', None, None),
            ('external = 1', None, None),
            ('external = [{path="foreign.md"}]', b"\xffforeign", None),
            ('', None, b'project_doc_max_bytes = ['),
            ('', None, b'\xff'),
        ):
            with self.subTest(setting=setting, config=config):
                root = self.project()
                project = root / "pyproject.toml"
                project.write_text(project.read_text() +
                                   "\n[tool.doctrine.runtimes.codex]\n" + setting + "\n")
                if external is not None:
                    (root / "foreign.md").write_bytes(external)
                if config is not None:
                    (root / ".codex").mkdir()
                    (root / ".codex/config.toml").write_bytes(config)
                for verb in ("check", "load", "build"):
                    code, output, error = self.cli(root, verb)
                    self.assertEqual(code, 1, error)
                    self.assertIn("E632 compile error: Invalid runtime settings", error)
                    self.assertNotIn("W306", error)
                    self.assertFalse((root / "pods/growth/qa/AGENTS.md").exists())

    def test_binary_level_file_needs_full_build(self):
        root = self.project()
        paths = [
            str(Path(folder) / filename)
            for folder in (".", "pods/growth")
            for filename in ("AGENTS.md", "CLAUDE.md")
        ]
        for name in paths:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"Hand written: \xff\n")
        code, _, error = self.cli(root, "build", "GrowthPod.qa")
        self.assertEqual(code, 1, error)
        self.assertIn("E635", error)
        self.assertFalse((root / "pods/growth/qa/AGENTS.md").exists())
        for name in paths:
            self.assertEqual((root / name).read_bytes(), b"Hand written: \xff\n")

    def test_target_with_no_emit_table_exits_2(self):
        root = self.project()
        (root / "pyproject.toml").write_text('[project]\nname = "fixture"\nversion = "0.0.0"\n')
        for verb in ("build", "check", "load"):
            code, _, error = self.cli(root, verb, "--target", "nope")
            self.assertEqual(code, 2)
            self.assertEqual(error, "Unknown target: nope\n")

    def test_check_json_is_only_json(self):
        root = self.project()
        code, output, error = self.cli(root, "check", ".", "--json")
        self.assertEqual(code, 1, error)
        result = json.loads(output)
        self.assertEqual(set(result), {"format_version", "ok", "homes", "errors", "warnings", "paths"})
        self.assertEqual(result["format_version"], 1)
        self.assertTrue(result["paths"])
        for path in result["paths"]:
            self.assertEqual(set(path), {"path", "state"})
            self.assertEqual(path["state"], "missing")
        self.assertFalse((root / "HOMES.contract.json").exists())

    def test_unknown_target_with_rev_exits_2(self):
        root = self.project()
        self.git_project(root)
        for verb in ("build", "check", "load"):
            code, _, error = self.cli(root, verb, "--rev", "HEAD", "--target", "nope")
            self.assertEqual(code, 2)
            self.assertEqual(error, "Unknown target: nope\n")

    def test_with_outside_repo_exits_2(self):
        root = self.project()
        self.git_project(root)
        for verb in ("build", "check", "load"):
            code, _, error = self.cli(root, verb, "--rev", "HEAD", "--with", "../outside.prompt")
            self.assertEqual(code, 2)
            self.assertIn("outside the repository", error)

    def test_e634_heading_from_prose(self):
        root = self.project(
            'team T: "Team"\n    home: "t"\n    role: """Role.\n\n## Prose\n\nText.\n"""\n'
        )
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        path = root / "t/AGENTS.md"
        path.write_text(path.read_text().replace("Text.", "Hand edit."))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("\n  - Prose\n", error)
        self.assertNotIn("Prose:", error)

    def test_e634_names_the_markdown_source(self):
        root = self.project(
            'abstract agent Craft from "craft.md"\n'
            'team T: "Team"\n    home: "t"\n    member qa[Craft]: "QA"\n'
        )
        (root / "craft.md").write_text("# Craft\nRole.\n\n## Work\nText.\n")
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        path = root / "t/qa/AGENTS.md"
        path.write_text(path.read_text().replace("Text.", "Hand edit."))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("- Work: Craft at craft.md:4", error)

    def test_team_name_selects_its_members(self):
        for selector in ("GrowthPod", "pods/growth"):
            with self.subTest(selector=selector):
                root = self.project()
                code, _, error = self.cli(root, "build", selector)
                self.assertEqual(code, 0, error)
                for home in ("pods/growth", "pods/growth/qa", "pods/growth/analyst"):
                    self.assertTrue((root / home / "AGENTS.md").is_file())
                contract = json.loads((root / "pods/growth/TEAM.contract.json").read_text())
                self.assertEqual([item["key"] for item in contract["members"]], ["qa", "analyst"])
                self.assertFalse((root / "HOMES.contract.json").exists())
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        contract = (root / "pods/growth/TEAM.contract.json").read_bytes()
        code, _, error = self.cli(root, "build", "GrowthPod.qa")
        self.assertEqual(code, 0, error)
        self.assertEqual((root / "pods/growth/TEAM.contract.json").read_bytes(), contract)

    def test_skill_target_is_usage_error(self):
        root = self.project('agent A:\n    role: "A."\n')
        (root / 'prompts/SKILL.prompt').write_text('skill package S: "Skill"\n    "Read."\n')
        with (root / 'pyproject.toml').open('a') as config:
            config.write('''\n[[tool.doctrine.emit.targets]]
name = "sk"
entrypoint = "prompts/SKILL.prompt"
output_dir = "skill"
''')
        code, _, error = self.cli(root, 'build', '--target', 'sk')
        self.assertEqual(code, 2)
        self.assertIn('Target sk has no homes.', error)
