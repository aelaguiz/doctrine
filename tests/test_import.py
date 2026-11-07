from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from doctrine.parser import parse_text
from tests.ws3_support import HomeProject


class ImportTests(HomeProject, unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def convert(self, markdown, kind="workflow"):
        (self.root / "source.md").write_text(markdown)
        code, output, error = self.cli(
            self.root, "import", "source.md", "--name", "Guide", "--kind", kind
        )
        self.assertEqual(code, 0, error)
        return output

    def test_lead_in_becomes_paragraph(self):
        source = self.convert("## Craft\n\n**Make a plan.** Start early.\n")
        self.assertIn('paragraph make_a_plan: "Make a plan."\n            "Start early."', source)

    def test_check_passes_on_lossless(self):
        for kind, markdown in (
            ("agent", "# Title\n\nRole.\n\n## Work\n\nText.\n"),
            ("agent", "# Title\n\n## Work\n\nText.\n"),
            ("workflow", "# Title\n\nIntro.\n\n## Work\n\nText.\n"),
            ("workflow", "# Title\n\n**Lead-in.** Text.\n\n## Work\n\nText.\n"),
            ("agent", ""),
            ("agent", "# Title\n"),
        ):
            with self.subTest(kind=kind, markdown=markdown):
                (self.root / "source.md").write_text(markdown)
                code, output, error = self.cli(
                    self.root, "import", "source.md", "--name", "Guide", "--kind", kind, "--check"
                )
                self.assertEqual(code, 0, error)
                self.assertTrue(output.startswith("abstract agent Guide:" if kind == "agent" else 'workflow Guide: "Title"'))

    def test_check_reports_first_difference(self):
        (self.root / "source.md").write_text("# Title\n\n## Work\nText.\n")
        code, output, error = self.cli(
            self.root, "import", "source.md", "--name", "Guide", "--kind", "agent", "--check"
        )
        self.assertEqual(code, 1)
        self.assertTrue(output.startswith("abstract agent Guide:"))
        self.assertEqual(error, "Line 4 differs.\n  Markdown: Text.\n  Render: \n")

    def test_text_after_keyed_item_gets_untitled_paragraph(self):
        source = self.convert("## Craft\n\n**Plan.** Start.\n\nThen work.\n")
        self.assertIn('paragraph text_1:\n            "Then work."', source)

    def test_one_line_text_uses_plain_string(self):
        source = self.convert("## Craft\n\nStart early.\n")
        self.assertIn('        "Start early."', source)

    def test_bold_only_paragraph_stays_text(self):
        source = self.convert("## Craft\n\n**A heading.**\n")
        self.assertIn('        "**A heading.**"', source)
        self.assertNotIn("paragraph a_heading", source)

    def test_repeated_key_gets_suffix(self):
        source = self.convert("## Craft\n\nFirst.\n\n## Craft\n\nSecond.\n")
        self.assertIn('    craft: "Craft"', source)
        self.assertIn('    craft_2: "Craft"', source)

    def test_printed_source_parses(self):
        for kind in ("agent", "workflow"):
            with self.subTest(kind=kind):
                source = self.convert(
                    "Intro.\n\n## 1. Setup\n\n**1. Plan.** Start.\n\n"
                    "### Use\n\nUse it.\n\n## Route\n\nRoute it.\n\n"
                    "## Home\n\nStay.\n\n## Skills\n\nLearn.\n", kind
                )
                self.assertTrue(parse_text(source).declarations)
                self.assertIn('_1_setup: "1. Setup"', source)
                self.assertIn('paragraph _1_plan: "1. Plan."', source)
                if kind == "workflow":
                    self.assertIn('skills_: "Skills"', source)
        markdown = 'Say "hello" at C:\\work and """end""".\n'
        source = self.convert(markdown)
        self.assertIn('Say "hello" at C:\\\\work', source)
        self.assertTrue(parse_text(source).declarations)
        code, _, error = self.cli(
            self.root, "import", "source.md", "--name", "Guide", "--kind", "workflow", "--check"
        )
        self.assertEqual(code, 0, error)
