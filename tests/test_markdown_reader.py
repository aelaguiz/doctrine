from __future__ import annotations

import unittest

from tests import test_late_binding
from doctrine.diagnostics import CompileError
from doctrine.renderer import render_markdown


class MarkdownReaderTests(unittest.TestCase):
    session = test_late_binding.LateBindingTests.session

    def markdown(self, text, extra=''):
        return self.session('abstract agent Craft from "craft.md"\nagent A[Craft]:\n' + extra + '    inherit *\n', {'craft.md': text})

    def test_slug_rules(self):
        session = self.markdown('# Craft\nRole.\n\n## The call: who & when?\nText.\n', '    drop the_call_who_when: "Other call."\n')
        self.assertEqual(render_markdown(session.compile_agent('A')), 'Role.\n')

    def test_headings_in_fences_ignored(self):
        session = self.markdown('# Craft\nRole.\n\n## Work\n```md\n## Not a section\n### Not a child\n```\n')
        self.assertIn('```md\n## Not a section\n### Not a child\n```', render_markdown(session.compile_agent('A')))

    def test_deeper_headings_stay_text(self):
        session = self.markdown('# Craft\nRole.\n\n## Work\nText.\n### Child\nText.\n#### Deep\nDeep text.\n')
        self.assertIn('#### Deep\nDeep text.', render_markdown(session.compile_agent('A')))

    def test_e653_duplicate_key(self):
        with self.assertRaises(CompileError) as caught:
            self.markdown('# Craft\nRole.\n## A call\nFirst.\n## A-call\nSecond.\n')
        self.assertEqual(caught.exception.code, 'E653')
        self.assertEqual(caught.exception.diagnostic.detail, '`craft.md` has two sibling headings with key `a_call`, at lines 3 and 5.')

    def test_e654_import_line(self):
        with self.assertRaises(CompileError) as caught:
            self.markdown('# Craft\nRole.\n@shared.md\n')
        self.assertEqual(caught.exception.code, 'E654')
        self.assertEqual(caught.exception.diagnostic.detail, '`craft.md` line 3 is a runtime import, and its path would break once inlined. Declare that file too and compose it.')

    def test_role_from_text_before_first_heading(self):
        session = self.markdown('# Title dropped\nRole line.\n\nSecond paragraph with {{literal}}.\n## Work\nWork.\n')
        rendered = render_markdown(session.compile_agent('A'))
        self.assertTrue(rendered.startswith('Role line.\n\nSecond paragraph with {{literal}}.\n'))
        self.assertNotIn('Title dropped', rendered)

    def test_drop_gone_heading_is_e610(self):
        with self.assertRaises(CompileError) as caught:
            self.markdown('# Craft\nRole.\n## Work\nWork.\n', '    drop gone: "Old heading."\n').compile_agent('A')
        self.assertEqual(caught.exception.code, 'E610')

    def test_fence_rules_follow_commonmark(self):
        for opening, middle, closing in (
            ('````md', '```\n## Still code\n```', '````'),
            ('```md', '```python\n## Still code', '```'),
            ('~~~md', '```\n## Still code\n~~~python\n## Also code', '~~~~'),
        ):
            text = 'Role.\n## Keep\n' + opening + '\n' + middle + '\n' + closing + '\n## Gone\nRemove.\n'
            with self.subTest(opening=opening, middle=middle):
                rendered = render_markdown(self.markdown(text, '    drop gone: "Unused."\n').compile_agent('A'))
                self.assertEqual(rendered, 'Role.\n\n## Keep\n\n' + opening + '\n' + middle + '\n' + closing + '\n')
        rendered = render_markdown(self.markdown('Role.\n```x``` is inline.\n## Gone\nRemove.\n', '    drop gone: "Unused."\n').compile_agent('A'))
        self.assertEqual(rendered, 'Role.\n```x``` is inline.\n')

    def test_reserved_heading_gets_final_underscore(self):
        session = self.markdown('Role.\n## Skills\nUse these skills.\n')
        self.assertEqual(render_markdown(session.compile_agent('A')), 'Role.\n\n## Skills\n\nUse these skills.\n')
        dropped = self.markdown('Role.\n## Skills\nUse these skills.\n', '    drop skills_: "Unused."\n')
        self.assertEqual(render_markdown(dropped.compile_agent('A')), 'Role.\n')
