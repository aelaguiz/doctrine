from __future__ import annotations

import unittest

from tests import test_late_binding
from doctrine.diagnostics import CompileError
from doctrine.renderer import render_markdown
from doctrine.emit_common import load_emit_targets
from doctrine.homes import compile_homes, build_homes


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

    def rebased(self, text, *, output="."):
        root = self.session('abstract agent Craft from "shared/craft.md"\nteam T: "Team"\n    home: "pods/core"\n    member qa[Craft]: "QA"\n    member analyst[Craft]: "Analyst"\n', {"shared/craft.md": "Role.\n## Work\n" + text + "\n"})
        config = root.root_flow.entrypoint_path.parent.parent / "pyproject.toml"
        config.write_text(f'[[tool.doctrine.emit.targets]]\nname = "homes"\nentrypoint = "prompts/AGENTS.prompt"\noutput_dir = "{output}"\n')
        target = load_emit_targets(config)["homes"]
        _, files = compile_homes(target)
        return files, target

    def test_relative_link_rebased_per_home(self):
        files, _ = self.rebased(
            '[case](cases.md) ![art](art.png) [angle](<more notes.md>) '
            '[nested](cases(old).md "Title")'
        )
        self.assertIn(b'[case](../../../shared/cases.md) ![art](../../../shared/art.png)', files['pods/core/qa/AGENTS.md'])
        self.assertIn(b'../../../shared/cases.md', files['pods/core/analyst/AGENTS.md'])
        self.assertIn(b'[angle](<../../../shared/more notes.md>)',
                      files['pods/core/qa/AGENTS.md'])
        self.assertIn(b'[nested](../../../shared/cases(old).md "Title")',
                      files['pods/core/qa/AGENTS.md'])

    def test_anchor_kept_on_rebased_link(self):
        files, _ = self.rebased('[case](cases.md#today)')
        self.assertIn(b'../../../shared/cases.md#today', files['pods/core/qa/AGENTS.md'])

    def test_scheme_root_and_anchor_links_left_alone(self):
        text = '[site](https://example.com) [mail](mailto:a@example.com) [root](/docs) [home](~/docs) [here](#today)'
        files, _ = self.rebased(text)
        self.assertIn(text.encode(), files['pods/core/qa/AGENTS.md'])

    def test_links_in_code_left_alone(self):
        text = '``[span](span.md) `quoted` ``\n\n````md\n[code](code.md)\n```\n[more](more.md)\n````'
        files, _ = self.rebased(text)
        self.assertIn(text.encode(), files['pods/core/qa/AGENTS.md'])

    def test_reference_definition_rebased(self):
        files, _ = self.rebased('[more]: <more notes.md#today> "Title"')
        self.assertIn(b'[more]: <../../../shared/more notes.md#today> "Title"', files['pods/core/qa/AGENTS.md'])

    def test_out_dir_keeps_rebased_bytes(self):
        files, target = self.rebased('[case](cases.md)', output="build")
        homes, files = compile_homes(target)
        other = target.output_dir.parent / "other"
        build_homes(target, homes, files, output_dir=other)
        self.assertEqual((other / 'pods/core/qa/AGENTS.md').read_bytes(), files['pods/core/qa/AGENTS.md'])

    def test_no_emit_target_keeps_links_as_written(self):
        text = '[case](cases.md#today)'
        rendered = render_markdown(self.markdown('Role.\n## Work\n' + text + '\n').compile_agent('A'))
        self.assertIn(text, rendered)

    def test_footnotes_and_prose_keep_their_text(self):
        text = '[^1]: See the old guide.\n[prose]: See the old guide.\n[ref]: guide.md "Guide"'
        files, _ = self.rebased(text)
        body = files['pods/core/qa/AGENTS.md'].decode()
        self.assertIn('[^1]: See the old guide.', body)
        self.assertIn('[prose]: See the old guide.', body)
        self.assertIn('[ref]: ../../../shared/guide.md "Guide"', body)

    def test_stray_backticks_stop_at_a_blank_line(self):
        text = 'A stray ` here.\n\n[case](cases.md)\n\nAnother ` here.'
        files, _ = self.rebased(text)
        self.assertIn(b'[case](../../../shared/cases.md)', files['pods/core/qa/AGENTS.md'])
