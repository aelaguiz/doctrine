from __future__ import annotations

import unittest
import json
import shutil
import tempfile
from pathlib import Path

from tests.home_support import HomeProject
from doctrine.emit_common import load_emit_targets
from doctrine.emit_docs import emit_target
from doctrine.emit_flow import emit_target_flow


class SharedFilesTests(HomeProject, unittest.TestCase):
    def test_guide_is_charged_only_to_the_home_that_loads_it(self):
        root = self.project(example="197_shared_files")
        code, output, error = self.cli(root, "load", "--json")
        self.assertEqual(code, 0, error)
        homes = {home["home"]: home for home in json.loads(output)["homes"]}
        for name in ("pod/qa", "pod/deep/qa"):
            report = homes[name]["runtimes"]["claude"]
            self.assertNotIn("shared/guide.md", [row["path"] for row in report["files"]])
            self.assertIn("shared/guide.md", [row["path"] for row in report["on_demand"]])
        report = homes["pod/analyst"]["runtimes"]["claude"]
        guide = next(row for row in report["files"] if row["path"] == "shared/guide.md")
        self.assertEqual(guide["kind"], "import")
        self.assertEqual(report["total"], sum(row["size"] for row in report["files"]))

    def test_shared_files_report_uses_each_runtime_and_sorts_by_first(self):
        source = '''file Letters: "Letters"
    path: "letters.md"
file Faces: "Faces"
    path: "faces.md"
team T: "Team"
    home: "t"
    member qa: "QA"
        role: "Read {{Letters}}."
    member analyst: "Analyst"
        role: "Read {{Letters}}."
        work: "Work"
            "Read first: {{load:Faces}}"
'''
        for runtimes, first in (('["claude", "codex"]', "letters.md"),
                                ('["codex", "claude"]', "faces.md")):
            with self.subTest(runtimes=runtimes):
                root = self.project(source, runtimes=runtimes)
                (root / "letters.md").write_text("aaaaaa")
                (root / "faces.md").write_text("🙂🙂")
                code, output, error = self.cli(root, "load", "--json")
                self.assertEqual(code, 0, error)
                rows = json.loads(output)["shared_files"]
                self.assertEqual(rows[0]["path"], first)
                self.assertEqual({row["path"]: row["sizes"] for row in rows}, {
                    "letters.md": {"claude": 6, "codex": 6},
                    "faces.md": {"claude": 4, "codex": 8}})
                self.assertEqual(next(row for row in rows if row["path"] == "letters.md")["homes"],
                                 ["t/analyst", "t/qa"])
                code, output, error = self.cli(root, "load")
                self.assertEqual(code, 0, error)
                self.assertIn("Shared files:\n  Path", output)
                self.assertIn("Homes", output)

    def test_shared_files_with_equal_sizes_sort_by_path(self):
        root = self.project('''file Z: "Z"
    path: "z.md"
file A: "A"
    path: "a.md"
team T: "Team"
    home: "t"
    role: "Read {{Z}} and {{A}}."
''')
        (root / "z.md").write_text("same")
        (root / "a.md").write_text("same")
        code, output, error = self.cli(root, "load", "--runtime", "codex", "--json")
        self.assertEqual(code, 0, error)
        rows = json.loads(output)["shared_files"]
        self.assertEqual([row["path"] for row in rows], ["a.md", "z.md"])
        self.assertEqual(rows[0]["sizes"], {"claude": 4, "codex": 4})

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

    def test_missing_imports_and_handles_add_no_load_rows(self):
        root = self.project(example="197_shared_files")
        (root / "CLAUDE.md").write_text("Parent notes. Ask @someone before you ship.\n@missing.md\n")
        for command in (("build", "."), ("load", "pod/qa", "--runtime", "claude", "--json")):
            code, output, error = self.cli(root, *command)
            self.assertEqual(code, 0, error)
            self.assertNotIn("someone", output)
            self.assertNotIn("missing.md", output)

    def test_all_dead_links_are_reported_in_build_order(self):
        root = self.project('''team T: "Team"
    home: "t"
    member one: "One"
        role: "Read [missing](../missing.md)."
    member two: "Two"
        role: "Read [missing](../missing.md)."
''')
        for command in ("build", "check"):
            code, _, error = self.cli(root, command)
            self.assertEqual(code, 1, error)
            self.assertEqual(error.count("E636"), 1)
            self.assertLess(error.index("t/one/AGENTS.md points"), error.index("t/two/AGENTS.md points"))

    def test_emit_docs_renders_shared_links_and_loads(self):
        root = self.project('''file Guide: "Test design"
    path: "shared/guide.md"
agent Writer:
    role: "Before you write, read {{Guide}}."
    work: "Work"
        "Read first: {{load:Guide}}"
''')
        guide = root / "shared/guide.md"
        guide.parent.mkdir()
        guide.write_text("Guide.\n")
        config = root / "pyproject.toml"
        config.write_text(config.read_text().replace('output_dir = "."', 'output_dir = "out"'))
        target = load_emit_targets(config)["homes"]
        for path in emit_target(target):
            self.assertNotIn(b"\x1e", path.read_bytes())
        output = (root / "out/writer/AGENTS.md").read_text()
        self.assertIn("[Test design](../../shared/guide.md)", output)
        self.assertIn("@../../shared/guide.md", output)

    def test_team_contract_resolves_links_from_the_contract_folder(self):
        root = self.project('''file Guide: "Guide"
    path: "guide.md"
team T: "Team"
    home: "t"
    values:
        ref: "{{Guide}}"
    member one: "One"
        role: "Work."
        work: "Read {{team:ref}}"
            "Work."
''')
        (root / "guide.md").write_text("Guide.\n")
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 0, error)
        contract = json.loads((root / "t/TEAM.contract.json").read_text())
        self.assertEqual(contract["members"][0]["sections"], ["Read [Guide](../guide.md)"])

    def test_flow_renders_file_links_from_the_diagram_folder(self):
        root = self.project('''file Guide: "Guide"
    path: "guide.md"
workflow Steps: "Steps"
    next: "Next"
        route "Read {{Guide}}" -> Other
agent Writer:
    role: "Write."
    work: Steps
agent Other:
    role: "Review."
''')
        (root / "guide.md").write_text("Guide.\n")
        target = load_emit_targets(root / "pyproject.toml")["homes"]
        emitted = emit_target_flow(target, include_svg=False)
        output = emitted[0].read_text()
        self.assertNotIn("\x1e", output)
        self.assertIn("[Guide](guide.md)", output)

    def test_missing_imports_are_skipped_from_each_loaded_file(self):
        root = self.project('''team T: "Team"
    home: "t"
    role: "Ask @compiled before work."
''', settings='[tool.doctrine.runtimes.claude]\nexternal = [{path="external.md"}]\n')
        (root / "CLAUDE.md").write_text("Ask @parent before work.\n@missing-parent.md\n")
        (root / "external.md").write_text("Ask @external before work.\n@missing-external.md\n@imported.md\n")
        (root / "imported.md").write_text("Ask @imported before work.\n@missing-import.md\n")
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 0, error)
        code, output, error = self.cli(root, "load", "t", "--runtime", "claude", "--json")
        self.assertEqual(code, 0, error)
        rows = json.loads(output)["homes"][0]["runtimes"]["claude"]["files"]
        paths = [row["path"] for row in rows]
        self.assertIn("imported.md", paths)
        for name in ("compiled", "parent", "external", "imported", "missing-parent.md",
                     "missing-external.md", "missing-import.md"):
            self.assertNotIn(name, paths)

    def test_an_import_path_ends_at_a_space_even_after_a_backslash(self):
        root = self.project('''team T: "Team"
    home: "t"
    role: "Work."
''', settings='[tool.doctrine.runtimes.claude]\nexternal = [{path="external.md"}]\n')
        (root / "external.md").write_text("@guide\\ rest.md\n")
        (root / "guide\\").write_text("Guide.\n")
        code, output, error = self.cli(root, "load", "t", "--runtime", "claude", "--json")
        self.assertEqual(code, 0, error)
        paths = [row["path"] for row in json.loads(output)["homes"][0]["runtimes"]["claude"]["files"]]
        self.assertIn("guide\\", paths)
        self.assertNotIn("guide rest.md", paths)

    def test_from_keeps_handles_and_rebases_only_existing_imports(self):
        root = self.project(example="179_markdown_backed_declarations", fixture="project_imports")
        (root / "shared/craft.md").write_text(
            "A role. Post as @brand and ping @alice before you ship.\n\n"
            "See [ask @alice](other.md).\n\n@other.md\n")
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 0, error)
        text = (root / "pod/qa/AGENTS.md").read_text()
        self.assertIn("Post as @brand and ping @alice before you ship.", text)
        self.assertIn("[ask @alice](../../shared/other.md)", text)
        self.assertIn("@../../shared/other.md", text)

    def test_handle_in_a_valid_link_does_not_trigger_e636(self):
        root = self.project('''team T: "Team"
    home: "t"
    role: "Questions go to [ask @alice](../people.md)."
''')
        (root / "people.md").write_text("People.\n")
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 0, error)
        self.assertIn("[ask @alice](../people.md)", (root / "t/AGENTS.md").read_text())

    def test_kept_file_with_invalid_utf8_works_in_all_reports(self):
        root = self.project('''file Guide: "Guide"
    path: "guide.md"
team T: "Team"
    home: "t"
    role: "Read {{Guide}}."
''')
        (root / "guide.md").write_bytes(b"Find this needle.\xff\n")
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary) / "base"
            shutil.copytree(root, base)
            for command in (("build", "."), ("load",), ("where", "needle"),
                            ("diff", "--base-tree", str(base))):
                with self.subTest(command=command):
                    code, _, error = self.cli(root, *command)
                    self.assertEqual(code, 0, error)

    def test_home_under_symlinked_folder_loads(self):
        root = self.project('''team T: "Team"
    home: "linked/team"
    role: "Work."
''')
        with tempfile.TemporaryDirectory() as temporary:
            (root / "linked").symlink_to(temporary, target_is_directory=True)
            for command in (("build", "."), ("load", "linked/team")):
                code, _, error = self.cli(root, *command)
                self.assertEqual(code, 0, error)
            self.assertTrue((Path(temporary) / "team/AGENTS.md").is_file())

    def test_file_limit_must_be_a_positive_integer(self):
        for value in ('"40000"', "40000.5", "0", "true"):
            with self.subTest(value=value):
                root = self.project('team T: "Team"\n    home: "t"\n    role: "Work."\n',
                                    settings=f'[tool.doctrine.runtimes.claude]\nfile_limit = {value}\n')
                code, _, error = self.cli(root, "build")
                self.assertEqual(code, 1, error)
                self.assertIn("E632", error)

    def test_codex_counts_an_external_root_level_once(self):
        root = self.project('team T: "Team"\n    home: "t"\n    role: "Work."\n',
                            settings='[tool.doctrine.runtimes.codex]\nexternal = [{path="AGENTS.md"}]\n')
        (root / "AGENTS.md").write_text("Root instructions.\n")
        code, output, error = self.cli(root, "load", "t", "--runtime", "codex", "--json")
        self.assertEqual(code, 0, error)
        load = json.loads(output)["homes"][0]["runtimes"]["codex"]
        self.assertEqual([row["path"] for row in load["files"]].count("AGENTS.md"), 1)
        self.assertEqual(load["total"], sum(row["size"] for row in load["files"]))

    def test_codex_full_omits_read_first_files(self):
        root = self.project(example="197_shared_files")
        (root / "shared/guide.md").write_text("Unique guide text.\n")
        code, output, error = self.cli(root, "load", "pod/analyst", "--runtime", "codex", "--full")
        self.assertEqual(code, 0, error)
        self.assertNotIn("Unique guide text.", output)
        self.assertNotIn("===== shared/guide.md", output)

    def test_loaded_and_linked_file_is_not_on_demand_for_claude(self):
        root = self.project('''file Guide: "Guide"
    path: "guide.md"
team T: "Team"
    home: "t"
    role: "Read {{Guide}}."
    work: "Work"
        "Read first: {{load:Guide}}"
''')
        (root / "guide.md").write_text("Guide.\n")
        code, output, error = self.cli(root, "load", "t", "--runtime", "claude", "--json")
        self.assertEqual(code, 0, error)
        load = json.loads(output)["homes"][0]["runtimes"]["claude"]
        self.assertIn("guide.md", [row["path"] for row in load["files"]])
        self.assertNotIn("guide.md", [row["path"] for row in load["on_demand"]])
