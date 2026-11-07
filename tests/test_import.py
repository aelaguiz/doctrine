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
                source = self.convert("Intro.\n\n## Craft\n\n**Plan.** Start.\n", kind)
                self.assertTrue(parse_text(source).declarations)
