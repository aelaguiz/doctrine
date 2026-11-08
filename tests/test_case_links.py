from __future__ import annotations

import json
import subprocess
import sys
import unittest

from doctrine._compiler.markdown_reader import heading_anchor
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file
from tests.home_support import HomeProject


class CaseLinksTests(HomeProject, unittest.TestCase):
    def test_case_links_in_titles_and_headings_are_rejected(self):
        token = "{{details:work.case}}"
        source = '''team T: "Team"
    home: "t"
    work: "Work"
        details case: "Case"
            "Text."
    member qa: "QA"
        role: "Test."
'''
        for before in ('"Team"', '"QA"', '"Work"', '"Case"'):
            with self.subTest(title=before):
                root = self.project(source.replace(before, f'"{token}"', 1))
                code, _, error = self.cli(root, "build", ".")
                self.assertEqual(code, 1)
                self.assertIn("E602", error)
                self.assertIn(f"`{token}` can't be read here: a case link belongs in a sentence the agent always reads.", error)

    def test_case_links_in_soul_and_classic_emit_are_rejected(self):
        source = 'agent A:\n    role: "Read {{details:work.case}}."\n'
        for soul in (False, True):
            with self.subTest(soul=soul):
                root = self.project("import worker\n" if soul else source)
                if soul:
                    package = root / "prompts/worker"
                    package.mkdir()
                    (package / "AGENTS.prompt").write_text('export agent A:\n    role: "Test."\n')
                    (package / "SOUL.prompt").write_text(source)
                    code, _, error = self.cli(root, "build", ".")
                    self.assertEqual(code, 1)
                    self.assertIn("E602", error)
                result = subprocess.run([sys.executable, "-m", "doctrine.emit_docs", "--pyproject",
                    str(root / "pyproject.toml"), "--target", "homes"], capture_output=True, text=True)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("E602", result.stderr)
                self.assertIn("a case link belongs in a sentence the agent always reads.", result.stderr)

    def test_links_at_two_depths_and_values(self):
        root = self.project(example="198_case_links")
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        for home, shared, value in (("pods/growth/lead", "../../../", "feature"),
                                    ("pods/growth/deep/lead", "../../../../", "release")):
            text = (root / home / "AGENTS.md").read_text()
            self.assertIn(f"[Reading the answers]({shared}_details/lead.md#reading-the-answers)", text)
            self.assertIn(f"[Plan the {value}](DETAILS.md#plan-the-{value})", text)
            self.assertIn(f"[Writing a test plan]({shared}shared/testing.md#writing-a-test-plan)", text)
            self.assertIn("The title is Writing a test plan.", text)
            self.assertNotIn("Fuller cases,", text)

    def test_anchor_matches_github_for_hyphens_and_symbols(self):
        self.assertEqual(heading_anchor("memmove-able", {}), "memmove-able")
        self.assertEqual(heading_anchor("C++ tips & tricks", {}), "c-tips--tricks")
        self.assertEqual(heading_anchor("Snake_case: a guide", {}), "snake_case-a-guide")

    def test_unlinked_cases_keep_only_their_companion_pointer(self):
        root = self.project(example="198_case_links")
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace('            "Take each answer in turn."',
            '            "Take each answer in turn."\n        details more: "More"\n            "More cases."'))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        text = (root / "pods/growth/lead/AGENTS.md").read_text()
        self.assertIn("Fuller cases, under the same headings: [_details/lead.md]", text)
        self.assertNotIn("[DETAILS.md]", text)

    def test_load_lists_linked_companions(self):
        root = self.project(example="198_case_links")
        code, output, error = self.cli(root, "load", "pods/growth/lead", "--runtime", "codex", "--json")
        self.assertEqual(code, 0, error)
        report = json.loads(output)["homes"][0]["runtimes"]["codex"]
        self.assertEqual({row["path"] for row in report["on_demand"]},
                         {"_details/lead.md", "pods/growth/lead/DETAILS.md", "shared/testing.md"})
        before = report["total"]
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace("Take each answer in turn.", "LONG " * 1000))
        code, output, error = self.cli(root, "load", "pods/growth/lead", "--runtime", "codex", "--json")
        self.assertEqual(code, 0, error)
        self.assertEqual(before, json.loads(output)["homes"][0]["runtimes"]["codex"]["total"])

    def test_override_follows_new_title_and_drop_fails(self):
        root = self.project('''abstract agent Base:
    role: "Test."
    work: "Work"
        "Read {{details:work.case}}."
        details case: "Old title"
            "Old case."
abstract agent Child[Base]:
    inherit *
    override work.case: "New title"
        "New case."
team T: "Team"
    home: "t"
    member qa[Child]: "QA"
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("[New title](../../_details/child.md#new-title)",
                      (root / "t/qa/AGENTS.md").read_text())
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace('    override work.case: "New title"\n        "New case."',
                                                     '    drop work.case: "No longer needed."'))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("`t/qa` links to `details:work.case`, which it doesn't have.", error)
        self.assertIn("Override the sentence that links to it, or keep the case.", error)
        source.write_text(source.read_text().replace('    drop work.case:',
            '    override work:\n        "No case needed."\n    drop work.case:'))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)

    def test_bad_case_links(self):
        for path, message in (("work", "`details:work` isn't a case."),
                              ("work.details", "`details:work.details` has no title to link to. Give the case a title."),
                              ("work.missing", "`t` links to `details:work.missing`, which it doesn't have.")):
            with self.subTest(path=path):
                root = self.project(f'''team T: "Team"
    home: "t"
    work: "Work"
        "Read {{{{details:{path}}}}}."
        details:
            "A case."
''')
                code, _, error = self.cli(root, "build", ".")
                self.assertEqual(code, 1)
                self.assertIn("E637", error)
                self.assertIn(message, error)

    def test_case_link_inside_case_is_rejected(self):
        root = self.project('''team T: "Team"
    home: "t"
    work: "Work"
        details first: "First"
            "Read {{details:work.second}}."
        details second: "Second"
            "A case."
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("E602", error)
        self.assertIn("a case link belongs in a sentence the agent always reads", error)

    def test_file_section_errors_and_nested_link(self):
        for body, link, expected in (
            ('    section plans: "Plans"\n        "Text."\n', 'Testing:missing', '`Testing` has no section `missing`.'),
            ('', 'Testing:plans', "`Testing` is kept as written, so Doctrine doesn't read its sections. Link to the file."),
        ):
            with self.subTest(link=link):
                root = self.project(f'''file Testing: "Testing"
    path: "testing.md"
{body}team T: "Team"
    home: "t"
    role: "Read {{{{{link}}}}}."
''')
                code, _, error = self.cli(root, "build", ".")
                self.assertEqual(code, 1)
                self.assertIn("E637", error)
                self.assertIn(expected, error)
        root = self.project(example="198_case_links")
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace("{{Testing:plans}}", "{{Testing:plans.review}}"))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("[Reviewing the plan](../../../shared/testing.md#reviewing-the-plan)",
                      (root / "pods/growth/lead/AGENTS.md").read_text())

    def test_skill_package_cannot_link_to_file_section(self):
        root = self.project('''file Testing: "Testing"
    path: "testing.md"
    section plans: "Plans"
        "Text."
skill package P: "Package"
    "Read {{Testing:plans}}."
''')
        session = CompilationSession(parse_file(root / "prompts/AGENTS.prompt"))
        with self.assertRaises(CompileError) as caught:
            session.compile_skill_package("P")
        self.assertEqual(caught.exception.code, "E655")
        self.assertEqual(caught.exception.diagnostic.detail,
            "A skill package has no home to link from, so it can't read `{{Testing:plans}}`.")

    def test_repeated_case_heading_full_build_gate(self):
        source = '''abstract agent R:
    role: "Test."
    first: "First"
        details old: "Case"
            "First case."
    second: "Second"
        "Read {{details:second.old}}."
        details old: "Other"
            "Second case."
team T: "Team"
    home: "t"
    member qa[R]: "QA"
        inherit role
        inherit second
        drop first: "QA owns second."
    member lead[R]: "Lead"
        inherit role
        inherit first
        drop second: "Lead owns first."
'''
        root = self.project(source)
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        (root / "prompts/AGENTS.prompt").write_text(source.replace('details old: "Other"', 'details old: "Case"'))
        code, _, error = self.cli(root, "build", "T.qa")
        self.assertEqual(code, 0, error)
        for command in ("build", "check"):
            code, _, error = self.cli(root, command, ".")
            self.assertEqual(code, 1)
            self.assertIn("`details:second.old` shares its heading with another in `_details/r.md`. Give it a title of its own.", error)

    def test_repeated_file_heading(self):
        root = self.project('''file Testing: "Testing"
    path: "testing.md"
    section plans: "Plans"
        "Text."
    section more: "Plans"
        "More."
team T: "Team"
    home: "t"
    role: "Read {{Testing:plans}}."
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("`Testing:plans` shares its heading with another in `testing.md`. Give it a title of its own.", error)

    def test_imported_workflow_keeps_its_case_path(self):
        root = self.project('''import shared
team T: "Team"
    home: "t"
    work: shared.W
''')
        module = root / "prompts/shared/AGENTS.prompt"
        module.parent.mkdir()
        module.write_text('''export workflow W: "Work"
    "Read {{details:old}}."
    details old: "Old"
        "The case."
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("[Old](../_details/shared-w.md#old)", (root / "t/AGENTS.md").read_text())

    def test_case_links_are_rejected_in_other_surfaces(self):
        cases = (
            ('skill package P: "Package"\n    "Read {{details:work.case}}."\n',
             lambda session: session.compile_skill_package("P")),
            ('document D: "Document"\n    "Read {{details:work.case}}."\n',
             lambda session: session.compile_readable_declaration("document", "D")),
        )
        for source, compile_it in cases:
            with self.subTest(source=source):
                root = self.project(source)
                session = CompilationSession(parse_file(root / "prompts/AGENTS.prompt"))
                with self.assertRaises(CompileError) as caught:
                    compile_it(session)
                self.assertEqual(caught.exception.code, "E602")
                self.assertEqual(caught.exception.diagnostic.detail,
                    "`{{details:work.case}}` can't be read here: a case link belongs in a sentence the agent always reads.")
        root = self.project('''file Guide: "Guide"
    path: "guide.md"
    "Read {{details:work.case}}."
team T: "Team"
    home: "t"
    role: "Read {{Guide}}."
''')
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("E602", error)
        self.assertIn("a case link belongs in a sentence the agent always reads", error)

    def test_idea_heading_counts_as_duplicate_but_unlinked_repeats_are_fine(self):
        source = '''team T: "Team"
    home: "t"
    work: "Case"
        details first: "Case"
            "Text."
'''
        root = self.project(source)
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        (root / "prompts/AGENTS.prompt").write_text(source.replace('        details first:',
            '        "Read {{details:work.first}}."\n        details first:'))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("`details:work.first` shares its heading with another in `t/DETAILS.md`.", error)

    def test_shared_companion_uses_its_own_file_section_path(self):
        root = self.project(example="198_case_links")
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace('"Take each answer in turn."',
            '"Take each answer in turn. Read {{Testing:plans}}."'))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        text = (root / "_details/lead.md").read_text()
        self.assertIn("[Writing a test plan](../shared/testing.md#writing-a-test-plan)", text)

    def test_file_links_in_nested_sections_and_cases(self):
        root = self.project(example="198_case_links")
        source = root / "prompts/AGENTS.prompt"
        source.write_text(source.read_text().replace(
            '        "Before planning, read {{Testing:plans}}. The title is {{Testing:plans.title}}."',
            '        nested: "Nested"\n            "Read {{Testing}}."'
        ).replace('            "Take each answer in turn."',
            '            section nested: "Nested"\n                "Read {{Testing:plans}}."'))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        self.assertIn("[How we test](../../../shared/testing.md)",
                      (root / "pods/growth/lead/AGENTS.md").read_text())
        self.assertIn("[Writing a test plan](../shared/testing.md#writing-a-test-plan)",
                      (root / "_details/lead.md").read_text())
