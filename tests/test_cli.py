from __future__ import annotations

import json
import subprocess
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.ws3_support import HomeProject


class CliTests(HomeProject, unittest.TestCase):
    def test_exit_codes_for_build_check_and_load(self):
        for command in (("build",), ("check",), ("load", "GrowthPod.qa", "--full")):
            with self.subTest(command=command):
                root = self.project()
                self.assertEqual(self.cli(root, *command)[0], 0)
                self.assertEqual(self.cli(root, *command, "--target", "absent")[0], 2)
                source = root / "prompts/AGENTS.prompt"
                source.write_text(source.read_text().replace("QA text.", "{{agent:missing}}"))
                code, _, error = self.cli(root, *command)
                self.assertEqual(code, 1)
                self.assertIn("E601", error)

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
        self.assertEqual(self.cli(root, "build", "GrowthPod.qa")[0], 0)
        self.assertTrue((root / "pods/growth/qa/AGENTS.md").exists())
        self.assertFalse((root / "pods/growth/AGENTS.md").exists())
        self.assertFalse((root / "pods/growth/analyst/AGENTS.md").exists())
        self.assertFalse((root / "HOMES.contract.json").exists())

    def test_build_prints_w307_for_stale_level(self):
        root = self.project()
        result = self.cli(root, "build", "GrowthPod.qa")
        self.assertEqual(result[0], 0)
        self.assertIn("W307 stale level: pods/growth/AGENTS.md differs from this build.", result[2])

    def test_check_mode_reports_stale_edited_missing(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        path = root / "prompts/AGENTS.prompt"
        path.write_text(path.read_text().replace("Team text.", "New team text."))
        (root / "pods/growth/qa/AGENTS.md").write_text("Hand edit.\n")
        (root / "pods/growth/analyst/CLAUDE.md").unlink()
        before = (root / "pods/growth/AGENTS.md").read_bytes()
        code, output, error = self.cli(root, "build", ".", "--check")
        self.assertEqual(code, 1, error)
        for line in (
            "stale pods/growth/AGENTS.md",
            "edited pods/growth/qa/AGENTS.md",
            "missing pods/growth/analyst/CLAUDE.md",
        ):
            self.assertIn(line, output)
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

    def test_w307_for_level_no_longer_emitted(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace('    role: "Team text."\n', ""))
        result = self.cli(root, "build", "GrowthPod.qa")
        self.assertEqual(result[0], 0)
        self.assertIn("W307 stale level: pods/growth/AGENTS.md", result[2])

    def test_with_overlays_one_file(self):
        root = self.project()
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

    def test_build_never_fails_on_budget_or_rule(self):
        root = self.project("""rule HasWork: "Has Work"
    scope:
        agent_tag: A
    assertions:
        requires declare work
    message: "Keep work."
agent A:
    role: "Ordinary agent."
team T: "Team"
    home: "t"
    role: "Team text."
    budget:
        codex: 1
""")
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("W306 near budget:", error)
        self.assertTrue((root / "t/AGENTS.md").is_file())

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
                    set(result), {"format_version", "ok", "homes", "errors", "warnings"}
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
            set(result), {"format_version", "written", "unchanged", "removed", "stale_levels"}
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
        for key in ("unchanged", "removed", "stale_levels"):
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
