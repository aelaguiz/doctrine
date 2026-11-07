from __future__ import annotations

import subprocess
import sys
import unittest

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.emit_common import load_emit_targets
from doctrine.homes import HEADER, compile_homes
from doctrine.parser import parse_file
from tests.home_support import HomeProject


class DetailsTests(HomeProject, unittest.TestCase):
    def test_details_override_keeps_its_lexical_owner(self):
        source = """workflow Parent: "Parent"
    details cases: "Cases"
        "Old case."
workflow Child[Parent]: "Child"
    override details cases:
        "New case."
team T: "Team"
    home: "t"
    work: Child
"""
        root = self.project(source)
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        companion = (root / "_details/child.md").read_text()
        self.assertIn("## Child\n\n### Cases\n\nNew case.", companion)
        self.assertNotIn("Old case.", companion)
        self.assertFalse((root / "_details/parent.md").exists())
        path = root / "prompts/AGENTS.prompt"
        path.write_text(source.replace("override details cases:", "override details absent:"))
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 1)
        self.assertIn("E001", error)

    def test_details_inside_guard_move_to_companion(self):
        root = self.project("""enum State: "State"
    ready: "Ready"
team T: "Team"
    home: "t"
    work: "Work"
        guard follow_up when State.ready == State.ready
            "Brief."
            details:
                "Long case."
""")
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        home = (root / "t/AGENTS.md").read_text()
        self.assertNotIn("Long case.", home)
        self.assertIn("Brief.", home)
        companion = (root / "t/DETAILS.md").read_text()
        self.assertIn("## Work\n\n### Follow Up\n\nLong case.", companion)

    def test_owner_table(self):
        cases = (
            (
                (
                    'team T: "Team"\n    home: "t"\n    work: "Work"\n        '
                    'details:\n            "Long case."\n'
                ),
                "t/DETAILS.md",
            ),
            (
                (
                    'team T: "Team"\n    home: "t"\n    member qa: "QA"\n        role: '
                    '"Test."\n        work: "Work"\n            details:\n                '
                    '"Long case."\n'
                ),
                "t/qa/DETAILS.md",
            ),
            (
                (
                    'agent A:\n    role: "Test."\n    work: "Work"\n        '
                    'details:\n            "Long case."\n'
                ),
                "a/DETAILS.md",
            ),
            (
                (
                    'abstract agent CraftRole:\n    role: "Test."\n    work: "Work"\n        '
                    'details:\n            "Long case."\nteam T: "Team"\n    home: "t"\n    '
                    'member qa[CraftRole]: "QA"\n'
                ),
                "_details/craft-role.md",
            ),
            (
                (
                    'abstract team BaseTeam:\n    work: "Work"\n        details:\n            '
                    '"Long case."\nteam T[BaseTeam]: "Team"\n    home: "t"\n'
                ),
                "_details/base-team.md",
            ),
            (
                (
                    'workflow W: "Work"\n    details:\n        "Long case."\nteam T: '
                    '"Team"\n    home: "t"\n    work: W\n'
                ),
                "_details/w.md",
            ),
            (
                (
                    'document D: "Document"\n    details:\n        "Long case."\ninput I: '
                    '"Input"\n    source: Prompt\n    shape: MarkdownDocument\n    '
                    'requirement: Required\n    structure: D\nagent A:\n    role: "Test."\n    '
                    'inputs: "Inputs"\n        I\n'
                ),
                "_details/d.md",
            ),
        )
        for source, companion in cases:
            with self.subTest(companion=companion):
                root = self.project(source)
                code, _, error = self.cli(root, "build", ".", "--target", "homes")
                self.assertEqual(code, 0, error)
                self.assertTrue((root / companion).is_file(), companion)
                self.assertIn("Long case.", (root / companion).read_text())

    def test_e620_in_skill_package(self):
        root = self.project('skill package S: "Skill"\n    details:\n        "Long case."\n')
        session = CompilationSession(parse_file(root / "prompts/AGENTS.prompt"))
        with self.assertRaises(CompileError) as caught:
            session.compile_skill_package("S")
        self.assertEqual(caught.exception.code, "E620")

    def test_one_pointer_line_per_home(self):
        root = self.project(example="182_shared_details")
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        text = (root / "pods/growth/qa/AGENTS.md").read_text()
        self.assertEqual(text.count("Fuller cases,"), 1)
        self.assertLess(text.index("[_details/habits.md]"), text.index("[_details/waiter.md]"))

    def test_companion_keeps_headings_and_depth(self):
        root = self.project("""team T: "Team"
    home: "t"
    work: "Work"
        step: "Step"
            details old: "Old case"
                "Long case."
""")
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        text = (root / "t/DETAILS.md").read_text()
        self.assertEqual(
            text[HEADER.match(text).end() :], "## Work\n\n### Step\n\n#### Old case\n\nLong case.\n"
        )

    def test_repeat_headings_get_suffix_anchors(self):
        root = self.project("""team T: "Team"
    home: "t"
    first: "Same"
        details old: "Case"
            "First."
    second: "Same"
        details old: "Case"
            "Second."
""")
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        text = (root / "t/DETAILS.md").read_text()
        self.assertEqual(text.count("## Same"), 2)
        self.assertEqual(text.count("### Case"), 2)

    def test_details_not_in_load(self):
        source = (
            'team T: "Team"\n    home: "t"\n    work: "Work"\n        '
            '"Brief."\n        details:\n            "LONG"\n'
        )
        root = self.project(source)
        before = self.loads(root)[0]["runtimes"]["codex"]
        (root / "prompts/AGENTS.prompt").write_text(source.replace("LONG", "LONG" * 1000))
        after = self.loads(root)[0]["runtimes"]["codex"]
        self.assertEqual(before["total"], after["total"])
        self.assertGreater(after["details_size"], before["details_size"])

    def test_shared_companion_bytes_ignore_consumers(self):
        root = self.project("""workflow W: "First"
    details:
        "First case."
workflow Retitled[W]: "New title"
    inherit *
abstract agent R:
    role: "Test."
    first: W
    second: W
team T: "Team"
    home: "t"
    member qa[R]: "QA"
        inherit second
        inherit first
    member lead[R]: "Lead"
        override first: Retitled
""")
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        path = root / "_details/w.md"
        self.assertEqual([file.name for file in (root / "_details").iterdir()], ["w.md"])
        original = path.read_bytes()
        self.assertIn(b"## First", original)
        self.assertNotIn(b"New title", original)
        source = root / "prompts/AGENTS.prompt"
        source.write_text(
            source.read_text().replace(
                "inherit second\n        inherit first", "inherit first\n        inherit second"
            )
        )
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.assertEqual(path.read_bytes(), original)

    def test_dotted_details_replacement_keeps_its_owner_and_headings(self):
        root = self.project("""abstract agent Base:
    role: "Test."
    work: "Work"
        child: "Child"
            section inner: "Inner"
                paragraph lead:
                    "Old."
abstract agent Child[Base]:
    inherit *
    override work.child.inner.lead:
        "New."
        details:
            "Long case."
team T: "Team"
    home: "t"
    member qa[Child]: "QA"
""")
        code, _, error = self.cli(root, "build", ".")
        self.assertEqual(code, 0, error)
        text = (root / "_details/child.md").read_text()
        self.assertIn("## Work\n\n### Child\n\n#### Inner\n\nLong case.", text)
        self.assertFalse((root / "_details/base.md").exists())

    def test_selected_build_does_not_compare_shared_companions(self):
        root = self.project("""abstract agent R:
    role: "Test."
    first: "First"
        details:
            "First case."
    second: "Second"
        details:
            "Second case."
team T: "Team"
    home: "t"
    member qa[R]: "QA"
        inherit role
        inherit first
        drop second: "The lead owns this case."
    member lead[R]: "Lead"
        inherit role
        inherit second
        drop first: "QA owns this case."
""")
        code, _, error = self.cli(root, "build", "T.qa")
        self.assertEqual(code, 0, error)
        self.assertNotIn("W307 stale level: _details/", error)
        companion = root / "_details/r.md"
        self.assertFalse(companion.exists())
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        original = companion.read_bytes()
        self.assertIn(b"First case.", original)
        self.assertIn(b"Second case.", original)
        code, _, error = self.cli(root, "build", "T.qa")
        self.assertEqual(code, 0, error)
        self.assertNotIn("W307", error)
        self.assertEqual(companion.read_bytes(), original)

    def test_details_in_document_section(self):
        root = self.project("""document D: "Document"
    section work: "Work"
        "Brief."
        details:
            "Long case."
input I: "Input"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
    structure: D
agent A:
    role: "Test."
    inputs: "Inputs"
        I
""")
        code, _, error = self.cli(root, "build", "--target", "homes")
        self.assertEqual(code, 0, error)
        self.assertIn("Long case.", (root / "_details/d.md").read_text())
        self.assertNotIn("Long case.", (root / "a/AGENTS.md").read_text())

    def test_e620_in_input_and_output(self):
        for kind, surface, field in (("input", "input", "inputs"), ("output", "output", "outputs")):
            with self.subTest(kind=kind):
                root = self.project(f"""{kind} Contract: "Contract"
    details:
        "Long case."
agent A:
    role: "Test."
    {field}: "Contract"
        Contract
""")
                code, _, error = self.cli(root, "build", "--target", "homes")
                self.assertEqual(code, 1)
                self.assertIn("E620 compile error: Details not allowed here", error)
                self.assertIn(f"`details` can't be used in an {surface} body.", error)

    def test_e620_in_output_structure(self):
        root = self.project("""document D: "Document"
    section work: "Work"
        "Brief."
        details:
            "Long case."
output O: "Output"
    target: File
        path: "result.md"
    shape: MarkdownDocument
    requirement: Required
    structure: D
agent A:
    role: "Test."
    outputs: "Outputs"
        O
""")
        code, _, error = self.cli(root, "build", "--target", "homes")
        self.assertEqual(code, 1)
        self.assertIn("E620 compile error: Details not allowed here", error)
        self.assertIn("`details` can't be used in an output structure.", error)
        self.assertFalse((root / "a/AGENTS.md").exists())

    def test_e620_in_skill(self):
        root = self.project("""skill S: "Skill"
    purpose: "Use the skill."
    details:
        "Long case."
skills Available: "Available"
    can_run: "Can run"
        skill s: S
agent A:
    role: "Test."
    skills: Available
""")
        code, _, error = self.cli(root, "build", "--target", "homes")
        self.assertEqual(code, 1)
        self.assertIn("E620 compile error: Details not allowed here", error)
        self.assertIn("`details` can't be used in a declaration without a home.", error)
        self.assertFalse((root / "a/AGENTS.md").exists())

    def test_e620_in_emit_docs(self):
        for soul in (False, True):
            with self.subTest(soul=soul):
                source = """agent A:
    role: "Test."
    work: "Work"
        details:
            "Long case."
"""
                root = self.project("import worker\n" if soul else source)
                if soul:
                    package = root / "prompts/worker"
                    package.mkdir()
                    (package / "AGENTS.prompt").write_text('export agent A:\n    role: "Test."\n')
                    (package / "SOUL.prompt").write_text(source)
                process = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "doctrine.emit_docs",
                        "--pyproject",
                        str(root / "pyproject.toml"),
                        "--target",
                        "homes",
                    ],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(process.returncode, 1, process.stderr)
                self.assertIn("E620 compile error: Details not allowed here", process.stderr)
                self.assertFalse((root / ("worker" if soul else "a") / "AGENTS.md").exists())
