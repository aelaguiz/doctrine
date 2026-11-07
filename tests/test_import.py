from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from doctrine.parser import parse_text
from tests.home_support import HomeProject


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
        self.assertIn('paragraph make_a_plan: "Make a plan."\n            """Start early."""', source)

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
        self.assertIn('paragraph text_1:\n            """Then work."""', source)

    def test_one_line_text_uses_triple_quoted_string(self):
        source = self.convert("## Craft\n\nStart early.\n")
        self.assertIn('        """Start early."""', source)

    def test_bold_only_paragraph_stays_text(self):
        source = self.convert("## Craft\n\n**A heading.**\n")
        self.assertIn('        """**A heading.**"""', source)
        self.assertNotIn("paragraph a_heading", source)

    def test_repeated_key_gets_suffix(self):
        source = self.convert("## Craft\n\nFirst.\n\n## Craft\n\nSecond.\n")
        self.assertIn('    craft: "Craft"', source)
        self.assertIn('    craft_2: "Craft"', source)

    def test_generated_paragraph_keys_do_not_collide(self):
        text = '**Thing.** First.\n\n**Thing.** Second.\n\n**Thing 2.** Third.\n'
        (self.root / 'source.md').write_text(text)
        code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertIn('paragraph thing_2_2:', source)

    def test_opening_bold_with_extra_space_stays_text(self):
        for gap in ('  ', '\t'):
            with self.subTest(gap=gap):
                (self.root / 'source.md').write_text(f'**Who.**{gap}You test.\n\nPhones are nearby.\n')
                code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
                self.assertEqual(code, 0, error)
                self.assertIn(f'**Who.**{gap}You test.', source)

    def test_sentence_ending_in_quote_allows_next_quote(self):
        (self.root / 'source.md').write_text('Owner, November 6, 2026: "One." Owner, November 7, 2026: "Two."\n')
        code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertEqual(source.count('{{Owner,'), 2)

    def test_agent_opening_gets_keyed_paragraphs(self):
        text = '# Title\n\n**Who you are.** You test.\n\nPhones are nearby.\n'
        (self.root / 'source.md').write_text(text)
        code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertIn('paragraph who_you_are: "Who you are."', source)
        self.assertIn('paragraph phones_are_nearby:', source)
        self.assertIn('Render matches.', error)

    def test_opening_keeps_blank_lines_in_fences(self):
        (self.root / 'source.md').write_text('Intro.\n\n```text\nfirst\n\nsecond\n```\n')
        code, _, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertIn('Render matches.', error)

    def test_opening_keeps_extra_blank_lines(self):
        (self.root / 'source.md').write_text('First.\n\n\nSecond.\n')
        code, _, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)

    def test_bold_opening_keeps_its_line_break(self):
        (self.root / 'source.md').write_text('**Who.**\nYou test.\n\nPhones are nearby.\n')
        code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertIn('paragraph who:', source)

    def test_import_quotes_and_report_unconverted_spans(self):
        text = ('# Title\n\nJane Doe, November 5, 2026, asking for you: "Keep this lesson for later use."\n\n'
                '(Jane Doe, November 6, 2026: "Keep the next lesson too.")\n\n'
                'Please ask Jane Doe, November 5, 2026: "This quote has six words in it."\n'
                'A short "one two three four five" quote.\n')
        (self.root / 'source.md').write_text(text)
        code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertTrue(source.startswith('person JaneDoe: "Jane Doe"\n'))
        self.assertEqual(source.count('person JaneDoe:'), 1)
        self.assertIn('{{JaneDoe, 2026-11-05, asking for you: "Keep this lesson for later use."}}', source)
        self.assertIn('({{JaneDoe, 2026-11-06: "Keep the next lesson too."}})', source)
        self.assertIn('paragraph jane_doe_november_5:', source)
        self.assertEqual(error, 'Quote left as prose at line 7.\nRender matches.\n')
        project = self.project(source + '\nteam Root: "Root"\n    home: "."\n    member reader[Guide]: "Reader"\n')
        code, output, error = self.cli(project, 'sources', '--json')
        self.assertEqual(code, 0, error)
        self.assertIn('Jane Doe', output)
        self.assertEqual([quote['on'] for quote in json.loads(output)['people'][0]['quotes']],
                         ['2026-11-05', '2026-11-06'])

    def test_quote_boundaries_and_person_order(self):
        text = ('Ada, January 1, 2026: "First quote."\n'
                'Done. Jane Doe, November 5, 2026: "Second quote."\n'
                'Done! Ada, January 2, 2026: "Third quote."\n'
                'Done? Mary Ann Lee, February 3, 2026, at 10:30: "Fourth quote."\n')
        (self.root / 'source.md').write_text(text)
        code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'workflow', '--check')
        self.assertEqual(code, 0, error)
        self.assertTrue(source.startswith('person Ada: "Ada"\nperson JaneDoe: "Jane Doe"\nperson MaryAnnLee: "Mary Ann Lee"\n'))
        self.assertEqual(source.count('{{'), 4)

    def test_quote_warnings_include_fences_and_each_span(self):
        text = ('Role.\n\n```text\nJane Doe, November 5, 2026: "one two three four five six"\n```\n\n'
                '"one two three four five six" and "one two three four five six seven"\n')
        (self.root / 'source.md').write_text(text)
        code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertNotIn('person JaneDoe:', source)
        self.assertEqual(error, 'Quote left as prose at line 4.\nQuote left as prose at line 7.\n'
                                'Quote left as prose at line 7.\nRender matches.\n')

    def test_quotes_that_cannot_render_exactly_stay_prose(self):
        text = ('Jane Doe, November 5, 2026, source session: "one two three four five six"\n'
                'Jane Doe, November 05, 2026: "one two three four five six"\n'
                'Jane Doe, February 30, 2026: "one two three four five six"\n')
        (self.root / 'source.md').write_text(text)
        code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertNotIn('person JaneDoe:', source)
        self.assertEqual(error, ''.join(f'Quote left as prose at line {n}.\n' for n in (1, 2, 3)) + 'Render matches.\n')

    def test_unconverted_multiline_quote_is_not_listed(self):
        (self.root / 'source.md').write_text('"one two three\nfour five six"\n')
        code, _, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertEqual(error, 'Render matches.\n')

    def test_stray_quote_does_not_shift_later_lines(self):
        (self.root / 'source.md').write_text('A 6" board.\n"one two three four five six"\n')
        code, _, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertEqual(error, 'Quote left as prose at line 2.\nRender matches.\n')

    def test_quote_in_bold_lead_stays_prose(self):
        (self.root / 'source.md').write_text('**(Jane Doe, November 5, 2026: "one two three four five six")** Body.\n\nOther.\n')
        code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertNotIn('person JaneDoe:', source)
        self.assertEqual(error, 'Quote left as prose at line 1.\nRender matches.\n')

    def test_check_with_quote_in_agent_without_opening(self):
        (self.root / 'source.md').write_text('## Work\n\nJane Doe, November 5, 2026: "Work carefully."\n')
        code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertTrue(source.startswith('person JaneDoe: "Jane Doe"\n'))
        self.assertEqual(error, 'Render matches.\n')

    def test_same_person_key_keeps_first_spelling(self):
        (self.root / 'source.md').write_text(
            'Ann Lee, November 5, 2026: "First quote."\n'
            'AnnLee, November 6, 2026: "This quote has six words in it."\n')
        code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertEqual(source.count('person AnnLee:'), 1)
        self.assertTrue(source.startswith('person AnnLee: "Ann Lee"\n'))
        self.assertIn('AnnLee, November 6, 2026: "This quote has six words in it.', source)
        self.assertEqual(error, 'Quote left as prose at line 2.\nRender matches.\n')

    def test_nested_quote_stays_prose_and_is_listed(self):
        (self.root / 'source.md').write_text(
            'Jane Doe, November 5, 2026: "Keep "this" lesson for later use."\n')
        code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
        self.assertEqual(code, 0, error)
        self.assertNotIn('person JaneDoe:', source)
        self.assertEqual(error, 'Quote left as prose at line 1.\nRender matches.\n')

    def test_quote_closing_boundary(self):
        for ending in ('', ' ', ')', '.', ',', ';', ':', '!', '?'):
            with self.subTest(ending=ending):
                (self.root / 'source.md').write_text(
                    f'Jane Doe, November 5, 2026: "Keep this lesson."{ending}\n')
                code, source, error = self.cli(self.root, 'import', 'source.md', '--name', 'Guide', '--kind', 'agent', '--check')
                self.assertEqual(code, 0, error)
                self.assertIn('{{JaneDoe, 2026-11-05: "Keep this lesson."}}', source)

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
