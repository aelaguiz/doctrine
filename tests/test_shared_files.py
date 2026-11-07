from __future__ import annotations

import unittest
import json
import shutil
import tempfile
from pathlib import Path

from tests.home_support import HomeProject


class SharedFilesTests(HomeProject, unittest.TestCase):
    def test_exported_file_keeps_its_project_path(self):
        root = self.project('''from shared import Guide
team T: "Team"
    home: "t"
    role: "Read {{Guide}}."
''')
        flow = root / "prompts/shared/AGENTS.prompt"
        flow.parent.mkdir()
        flow.write_text('export file Guide: "Guide"\n    path: "guide.md"\n')
        (root / "guide.md").write_text("Guide.\n")
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 0, error)
        self.assertIn("[Guide](../guide.md)", (root / "t/AGENTS.md").read_text())

    def test_file_refs_keep_authored_paragraphs_separate(self):
        root = self.project('''file Guide: "Guide"
    path: "guide.md"
team T: "Team"
    home: "t"
    how: "How"
        "First {{Guide}}."
        "Second {{Guide}}."
''')
        (root / "guide.md").write_text("Guide.\n")
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 0, error)
        self.assertIn("First [Guide](../guide.md).\n\nSecond [Guide](../guide.md).",
                      (root / "t/AGENTS.md").read_text())

    def test_diff_reports_kept_file_growth_and_readers(self):
        root = self.project('''file Guide: "Guide"
    path: "guide.md"
team T: "Team"
    home: "t"
    member qa: "QA"
        role: "Read {{Guide}}."
''')
        (root / "guide.md").write_text("Guide.\n")
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary) / "base"
            shutil.copytree(root, base)
            (root / "guide.md").write_text("Guide.\nMore.\n")
            code, output, error = self.cli(root, "diff", "--base-tree", str(base), "--json")
            self.assertEqual(code, 0, error)
            self.assertEqual(json.loads(output)["shared_files"], [
                {"path": "guide.md", "delta": 6, "homes": ["t/qa"]}])
            code, output, error = self.cli(root, "diff", "--base-tree", str(base))
            self.assertEqual(code, 0, error)
            self.assertIn("guide.md  +6 characters, read by 1 home", output)

    def test_where_searches_the_kept_file_and_lists_its_readers(self):
        root = self.project('''file Guide: "Guide"
    path: "guide.md"
team T: "Team"
    home: "t"
    member qa: "QA"
        role: "Read {{Guide}}."
''')
        (root / "guide.md").write_text("Title.\nA memorable test sentence.\n")
        code, output, error = self.cli(root, "where", "memorable test sentence", "--json")
        self.assertEqual(code, 0, error)
        self.assertIn({"origin": "file Guide", "site": "guide.md:2", "homes": ["t/qa"]},
                      json.loads(output)["matches"])

    def test_near_copy_warns_for_kept_file_text(self):
        root = self.project('''file Guide: "Guide"
    path: "guide.md"
team T: "Team"
    home: "t"
    role: "Read every change with care and test each part that a user will meet today."
''')
        (root / "guide.md").write_text("Read every change with care and test each part that a user will meet today.\n")
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 0, error)
        self.assertIn("W301 near copy: T and Guide", error)

    def test_load_reports_on_demand_and_codex_read_first(self):
        root = self.project('''file Guide: "Guide"
    path: "guide.md"
file Basics: "Basics"
    path: "basics.md"
team T: "Team"
    home: "t"
    member qa: "QA"
        role: "Read {{Guide}} before a test."
        work: "Work"
            "Read first: {{load:Basics}}"
''')
        (root / "guide.md").write_text("Guide.\n")
        (root / "basics.md").write_text("Basics.\n")
        code, output, error = self.cli(root, "load", "t/qa", "--runtime", "codex", "--json")
        self.assertEqual(code, 0, error)
        report = json.loads(output)["homes"][0]["runtimes"]["codex"]
        self.assertEqual(report["on_demand"], [{"path": "guide.md", "size": 7}])
        self.assertEqual(report["files"][-1]["kind"], "read_first")
        self.assertEqual(report["files"][-1]["path"], "basics.md")
        self.assertEqual(report["total"], sum(row["size"] for row in report["files"] if row["kind"] == "home"))
        code, output, error = self.cli(root, "load", "t/qa", "--runtime", "codex")
        self.assertEqual(code, 0, error)
        self.assertIn("read first", output)
        self.assertIn("On demand:\n  guide.md", output)
        code, output, error = self.cli(root, "load", "--json")
        self.assertEqual(code, 0, error)
        shared = json.loads(output)["shared_files"]
        self.assertEqual(shared, [
            {"path": "basics.md", "size": 8, "homes": ["t/qa"]},
            {"path": "guide.md", "size": 7, "homes": ["t/qa"]},
        ])
        self.assertIn("Shared files:", self.cli(root, "load")[1])

    def test_shared_file_rejects_details_and_home_values(self):
        for body, diagnostic in (
            ('    details case: "Case"\n        "More."\n', "E620"),
            ('    "The {{team:title}}."\n', "E602"),
        ):
            with self.subTest(diagnostic=diagnostic):
                root = self.project(
                    'file Guide: "Guide"\n    path: "guide.md"\n' + body
                    + 'team T: "Team"\n    home: "t"\n    role: "Read {{Guide}}."\n'
                )
                code, _, error = self.cli(root, "build")
                self.assertEqual(code, 1, error)
                self.assertIn(diagnostic, error)

    def test_requires_load_distinguishes_a_pointer(self):
        root = self.project('''file Guide: "Guide"
    path: "guide.md"
team T: "Team"
    home: "t"
    member qa: "QA"
        role: "Read {{load:Guide}}"
rule R: "Load guide"
    scope:
        member: qa
    assertions:
        requires load Guide
    message: "Read it."
''')
        (root / "guide.md").write_text("Guide.\n")
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 0, error)
        self.assertIn("Read @../../guide.md", (root / "t/qa/AGENTS.md").read_text())
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace("{{load:Guide}}", "{{Guide}}"))
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 1, error)
        self.assertIn("RULE006", error)

    def test_links_resolve_from_each_home_and_keep_the_plain_file(self):
        root = self.project('''file Guide: "The guide"
    path: "shared/guide.md"
team Pod: "Pod"
    home: "pod"
    member qa: "QA"
        role: "Read {{Guide}} and {{Guide:title}}."
team Other: "Other"
    home: "pod/deep"
    member qa: "QA"
        role: "Read {{Guide}}."
''')
        guide = root / "shared/guide.md"
        guide.parent.mkdir()
        guide.write_text("## Same\nOne.\n## Same\nTwo.\n")
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 0, error)
        self.assertIn("[The guide](../../shared/guide.md) and The guide", (root / "pod/qa/AGENTS.md").read_text())
        self.assertIn("[The guide](../../../shared/guide.md)", (root / "pod/deep/qa/AGENTS.md").read_text())
        self.assertEqual(guide.read_text(), "## Same\nOne.\n## Same\nTwo.\n")
        self.assertEqual(self.cli(root, "check")[0], 0)

    def test_missing_and_invalid_file_refs_fail(self):
        for guide, text, code, message in (
            ("missing.md", "{{Guide}}", "E652", "`Guide` names `missing.md`, which doesn't exist."),
            ("guide.md", "{{load:Guide}} now", "E655", "`{{load:Guide}}` must end its line."),
            ("guide file.md", "{{load:Guide}}", "E655", "`{{load:Guide}}` can't load `guide file.md`, because an import path ends at a space. Rename the file."),
        ):
            with self.subTest(text=text):
                root = self.project(f'''file Guide: "Guide"
    path: "{guide}"
team T: "Team"
    home: "t"
    role: "{text}"
''')
                if guide != "missing.md":
                    (root / guide).write_text("Guide.\n")
                result, _, error = self.cli(root, "build")
                self.assertEqual(result, 1, error)
                self.assertIn(code, error)
                self.assertIn(message, error)

    def test_load_of_an_unknown_name_fails(self):
        root = self.project('team T: "Team"\n    home: "t"\n    role: "{{load:Missing}}"\n')
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 1, error)
        self.assertIn("load", error)

    def test_space_in_a_pointed_at_path_uses_angle_brackets(self):
        root = self.project('''file Guide: "Guide"
    path: "guide file.md"
team T: "Team"
    home: "t"
    role: "Read {{Guide}}."
''')
        (root / "guide file.md").write_text("Guide.\n")
        result, _, error = self.cli(root, "build")
        self.assertEqual(result, 0, error)
        self.assertIn("[Guide](<../guide file.md>)", (root / "t/AGENTS.md").read_text())

    def test_built_file_has_a_guard_and_duplicate_paths_fail(self):
        root = self.project('''file Guide: "Guide"
    path: "guide.md"
    "Read this."
team T: "Team"
    home: "t"
    role: "Read {{Guide}}."
''')
        self.assertEqual(self.cli(root, "build")[0], 0)
        guide = root / "guide.md"
        self.assertIn("# Guide\n\nRead this.", guide.read_text())
        guide.write_text(guide.read_text() + "Edited.\n")
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 1, error)
        self.assertIn("E634", error)
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text() + '\nfile Other: "Other"\n    path: "guide.md"\n    "Other."\n')
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 1, error)
        self.assertIn("E607", error)
