from __future__ import annotations

import json
import unittest

from tests.test_diff import SOURCE
from tests.home_support import HomeProject


class ProvenanceTests(HomeProject, unittest.TestCase):
    def test_owners_add_up(self):
        source = 'person A: "A"\n    owns:\n        Craft\nperson B: "B"\n    owns:\n        Craft\n' + SOURCE
        before, after = self.project(source), self.project(source.replace('Read the change.', 'Read it.'))
        code, output, error = self.cli(after, 'diff', '--base-tree', str(before), '--json')
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)['owned'], [{'name': 'Craft', 'owners': ['A', 'B']}])

    def test_owners_read_from_both_sides(self):
        source = 'person A: "A"\n    owns:\n        Craft\n' + SOURCE
        before = self.project(source)
        after = self.project(source.replace('    owns:\n        Craft\n', '').replace('Read the change.', 'Read it.'))
        code, output, error = self.cli(after, 'diff', '--base-tree', str(before), '--json')
        self.assertEqual(code, 0, error)
        self.assertIn({'name': 'Craft', 'owners': ['A']}, json.loads(output)['owned'])

    def test_e651_glob_matches_nothing(self):
        root = self.project('person A: "A"\n    owns:\n        "missing/*.prompt"\n' + SOURCE)
        code, _, error = self.cli(root, 'check')
        self.assertEqual(code, 1)
        self.assertIn('Glob `missing/*.prompt` in `owns:` matches no source file.', error)

    def test_glob_owns_from_file_readers(self):
        source = 'person A: "A"\n    owns:\n        "rules.md"\nworkflow Rules from "rules.md"\nteam T: "Team"\n    home: "."\n    rules: Rules\n'
        before, after = self.project(source), self.project(source)
        (before / 'rules.md').write_text('# Rules\n\nOld.\n')
        (after / 'rules.md').write_text('# Rules\n\nNew.\n')
        code, output, error = self.cli(after, 'diff', '--base-tree', str(before), '--json')
        self.assertEqual(code, 0, error)
        self.assertIn({'name': 'Rules', 'owners': ['A']}, json.loads(output)['owned'])

    def test_team_ownership_covers_member(self):
        source = 'person A: "A"\n    owns:\n        T\n' + SOURCE
        before = self.project(source)
        after = self.project(source.replace('member qa[Craft]: "QA"', 'member qa[Craft]: "New QA"'))
        code, output, error = self.cli(after, 'diff', '--base-tree', str(before), '--json')
        self.assertEqual(code, 0, error)
        self.assertIn({'name': 'T.qa', 'owners': ['A']}, json.loads(output)['owned'])

    def test_build_checks_ownership(self):
        root = self.project('person A: "A"\n    owns:\n        Missing\n' + SOURCE)
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 1, error)
        self.assertIn("E651", error)

    def test_unreached_owned_declaration_is_reported(self):
        source = 'person A: "A"\n    owns:\n        Free\nworkflow Free: "Free"\n    "Old."\n' + SOURCE
        before, after = self.project(source), self.project(source.replace('"Old."', '"New."'))
        code, output, error = self.cli(after, 'diff', '--base-tree', str(before), '--json')
        self.assertEqual(code, 0, error)
        result = json.loads(output)
        self.assertEqual(result['homes'], [])
        self.assertEqual(result['owned'], [{'name': 'Free', 'owners': ['A']}])

    def test_exported_person_can_be_imported(self):
        root = self.project('from common import Owner\n' + SOURCE)
        (root / 'prompts/common').mkdir()
        (root / 'prompts/common/AGENTS.prompt').write_text('export person Owner: "Owner"\n')
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        code, _, error = self.cli(root, 'check')
        self.assertEqual(code, 0, error)

    def test_owner_in_imported_flow(self):
        source = 'from common import Rules\n' + SOURCE.replace('    member qa[Craft]', '    work: Rules\n    member qa[Craft]')
        before, after = self.project(source), self.project(source)
        for root, text in ((before, 'Old.'), (after, 'New.')):
            (root / 'prompts/common').mkdir()
            (root / 'prompts/common/AGENTS.prompt').write_text(
                'person Owner: "Owner"\n    owns:\n        Rules\n'
                'export workflow Rules: "Rules"\n    "' + text + '"\n'
            )
        code, output, error = self.cli(after, 'diff', '--base-tree', str(before), '--json')
        self.assertEqual(code, 0, error)
        self.assertIn({'name': 'common.Rules', 'owners': ['common.Owner']}, json.loads(output)['owned'])

    def test_e651_member_ref(self):
        root = self.project('''person A: "A"
    owns:
        Growth.lead
abstract team Pod: "Pod"
    member lead: "Lead"
        role: "Lead."
team Growth[Pod]: "Growth"
    home: "growth"
    inherit *
''')
        code, _, error = self.cli(root, 'check')
        self.assertEqual(code, 1)
        self.assertIn('`Growth.lead` in `owns:` resolves to nothing.', error)

    def test_person_and_workflow_share_a_name(self):
        source = 'person Craft: "Person"\nworkflow Craft: "Craft"\n    "Read."\nteam T: "Team"\n    home: "."\n    work: Craft\n'
        before, after = self.project(source), self.project(source.replace('"Read."', '"Read more."'))
        code, output, error = self.cli(after, 'diff', '--base-tree', str(before), '--json')
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)['changed_declarations'][0]['name'], 'Craft')

    def test_quote_render_forms(self):
        for fields, suffix in (("", ""), ('    to: "Lee"\n', ', to Lee'),
                               ('    about: "code"\n', ', about code'),
                               ('    to: "Lee"\n    about: "code"\n', ', to Lee, about code')):
            with self.subTest(fields=fields):
                source = ('person A: "Author"\nquote Q: "Words"\n    by: A\n'
                          '    on: "2026-11-05"\n' + fields +
                          'workflow W: "Work"\n    part: "Part"\n        Q\n'
                          'team T: "Team"\n    home: "."\n    work: W\n')
                root = self.project(source)
                code, _, error = self.cli(root, 'build')
                self.assertEqual(code, 0, error)
                self.assertIn(f'Author, November 5, 2026{suffix}: "Words"', (root / 'AGENTS.md').read_text().splitlines())

    def test_inline_quote_matches_named_render(self):
        root = self.project('''person A: "Author"
quote Q: "Words"
    by: A
    on: "2026-11-05"
team T: "Team"
    home: "."
    role: """{{Q}} {{A, 2026-11-05: "Words"}}"""
''')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 0, error)
        self.assertEqual((root / 'AGENTS.md').read_text().count('Author, November 5, 2026: "Words"'), 2)

    def test_inline_quote_field_order_free(self):
        root = self.project('''person A: "Author"
team T: "Team"
    home: "."
    role: """{{A, 2026-11-05, source session:abc, about code, to Lee: "Words"}}"""
''')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 0, error)
        self.assertIn('about code, to Lee: "Words"', (root / 'AGENTS.md').read_text())

    def test_free_words_and_parentheses(self):
        root = self.project('''person A: "Author"
quote Q: "Words"
    by: A
    on: "2026-11-05"
    context: "for Lee"
team T: "Team"
    home: "."
    role: """({{Q}}) ({{A, 2026-11-05, for Lee: "Words"}})"""
''')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 0, error)
        self.assertEqual((root / 'AGENTS.md').read_text().count('(Author, November 5, 2026, for Lee: "Words")'), 2)

    def test_inline_free_words_keep_field_order(self):
        root = self.project('''person A: "Author"
team T: "Team"
    home: "."
    role: """{{A, 2026-11-05, for Lee, about code, asking for you: "Words"}}"""
''')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 0, error)
        self.assertIn('Author, November 5, 2026, for Lee, about code, asking for you: "Words"',
                      (root / 'AGENTS.md').read_text())

    def test_e650_bad_date(self):
        for date in ('2026-1-5', '20261105', '2026-02-30'):
            with self.subTest(date=date):
                root = self.project(f'person A: "A"\nquote Q: "Words"\n    by: A\n    on: "{date}"\nteam T: "T"\n    home: "."\n    role: "{{{{Q}}}}"\n')
                code, _, error = self.cli(root, 'build')
                self.assertEqual(code, 1)
                self.assertIn('`on:` in `Q` must be a date, `YYYY-MM-DD`.', error)

    def test_e650_unknown_person(self):
        root = self.project('quote Q: "Words"\n    by: Missing\n    on: "2026-11-05"\nteam T: "T"\n    home: "."\n    role: "{{Q}}"\n')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 1)
        self.assertIn('`by:` in `Q` is not a `person`.', error)

    def test_sources_flags_missing_source(self):
        root = self.project(example='190_quotes')
        code, output, error = self.cli(root, 'sources', '--json')
        self.assertEqual(code, 0, error)
        self.assertEqual(len([q for q in json.loads(output)['people'][0]['quotes'] if q['source'] is None]), 1)

    def test_sources_lists_inline_by_site(self):
        root = self.project(example='190_quotes')
        code, output, error = self.cli(root, 'sources', '--json')
        self.assertEqual(code, 0, error)
        inline = next(q for q in json.loads(output)['people'][0]['quotes'] if q['source'] == '53dcb019')
        self.assertEqual(inline['key'], inline['site'])
        self.assertEqual(inline['cited_in'], ['Root'])

    def test_e650_repeated_field(self):
        root = self.project('person A: "A"\nquote Q: "Words"\n    by: A\n    on: "2026-11-05"\n    on: "2026-11-06"\nteam T: "T"\n    home: "."\n    role: "{{Q}}"\n')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 1)
        self.assertIn('`on:` in `Q` is set twice.', error)

    def test_e650_unknown_person_filter(self):
        root = self.project(example='190_quotes')
        code, _, error = self.cli(root, 'sources', '--person', 'Missing')
        self.assertEqual(code, 1)
        self.assertIn('`--person Missing` is not a `person`.', error)

    def test_bad_quote_stops_only_its_home(self):
        root = self.project('''person A: "A"
quote Q: "Words"
    by: A
    on: "bad"
team T: "T"
    home: "."
    member good: "Good"
        role: "Fine."
    member bad: "Bad"
        role: "{{Q}}"
''')
        code, _, error = self.cli(root, 'build', 'T.good')
        self.assertEqual(code, 0, error)
        self.assertEqual(self.cli(root, 'build', 'T.bad')[0], 1)

    def test_inline_person_title_reaches_home(self):
        source = '''person A: "A"
team T: "T"
    home: "."
    role: """{{A, 2026-11-05: "Words"}}"""
'''
        before, after = self.project(source), self.project(source.replace('person A: "A"', 'person A: "Author"'))
        code, output, error = self.cli(after, 'diff', '--base-tree', str(before), '--json')
        self.assertEqual(code, 0, error)
        self.assertTrue(any(d['name'] == 'A' for d in json.loads(output)['changed_declarations']))

    def test_w305_counts_unreached_citations(self):
        root = self.project('''person A: "A"
quote Q: "Words"
    by: A
    on: "2026-11-05"
workflow Unused: "Unused"
    "{{Q}}"
team T: "T"
    home: "."
    role: "Fine."
''')
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        code, _, error = self.cli(root, 'check')
        self.assertEqual(code, 0, error)
        self.assertNotIn('W305', error)

    def test_inline_diagnostics(self):
        for expression, expected in (
            ('Missing, 2026-11-05: "Words"', '`Missing` is not a `person`'),
            ('A, 20261105: "Words"', '`20261105` must be a date'),
            ('A, 2026-11-05, to Lee, to Bob: "Words"', '`to` is set twice'),
            ('A, 2026-11-05: words', 'the words must come last'),
            ('A, 2026-11-05: "{Words}"', "`{` and `}` can't appear"),
        ):
            with self.subTest(expression=expression):
                root = self.project('person A: "A"\nteam T: "T"\n    home: "."\n    role: """{{' + expression + '}}"""\n')
                code, _, error = self.cli(root, 'build')
                self.assertEqual(code, 1, error)
                self.assertIn(expected, error)

    def test_w305_can_be_disabled(self):
        root = self.project(example='190_quotes', fixture='project_unused')
        with (root / 'pyproject.toml').open('a') as config:
            config.write('\n[tool.doctrine.check]\ndisable = ["W305"]\n')
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        code, _, error = self.cli(root, 'check')
        self.assertEqual(code, 0, error)
        self.assertNotIn('W305', error)

    def test_e650_missing_fields(self):
        for fields, detail in (('    on: "2026-11-05"\n', 'needs `by:`'), ('    by: A\n', 'needs `on:`')):
            with self.subTest(fields=fields):
                root = self.project('person A: "A"\nquote Q: "Words"\n' + fields + 'team T: "T"\n    home: "."\n    role: "{{Q}}"\n')
                code, _, error = self.cli(root, 'build')
                self.assertEqual(code, 1)
                self.assertIn(detail, error)

    def test_sources_tracks_repeated_inline_quotes(self):
        root = self.project('''person A: "A"
team T: "T"
    home: "."
    work: "Work"
        """{{A, 2026-11-05: "Words"}}"""
        """{{A, 2026-11-05: "Words"}}"""
''')
        code, output, error = self.cli(root, 'sources', '--json')
        self.assertEqual(code, 0, error)
        quotes = json.loads(output)['people'][0]['quotes']
        self.assertEqual(len(quotes), 2)
        self.assertNotEqual(quotes[0]['site'], quotes[1]['site'])

    def test_named_quote_late_values(self):
        root = self.project('''person A: "A"
quote Q: "{{agent:word}}"
    by: A
    on: "2026-11-05"
team T: "T"
    home: "."
    values:
        word: "late"
    role: "{{Q}}"
''')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 0, error)
        self.assertIn('"late"', (root / 'AGENTS.md').read_text())

    def test_bad_qualified_person_is_e650(self):
        root = self.project('quote Q: "Words"\n    by: Missing.Person\n    on: "2026-11-05"\nteam T: "T"\n    home: "."\n    role: "{{Q}}"\n')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 1)
        self.assertIn('E650', error)

    def test_sources_finds_escaped_inline_site(self):
        root = self.project('person A: "A"\nteam T: "T"\n    home: "."\n    role: "{{A, 2026-11-05: \\"Words\\"}}"\n')
        code, output, error = self.cli(root, 'sources', '--json')
        self.assertEqual(code, 0, error)
        self.assertTrue(json.loads(output)['people'][0]['quotes'][0]['site'].endswith(':4'))

    def test_same_named_person_is_not_lost(self):
        root = self.project('person Craft: "Person"\n    owns:\n        Missing\nworkflow Craft: "Craft"\n    "Read."\nteam T: "Team"\n    home: "."\n    work: Craft\n')
        code, _, error = self.cli(root, 'check')
        self.assertEqual(code, 1)
        self.assertIn('E651', error)

    def test_w305_counts_bare_citation_in_unreached_workflow(self):
        root = self.project('''person A: "A"
quote Q: "Words"
    by: A
    on: "2026-11-05"
workflow Unused: "Unused"
    section: "Section"
        Q
team T: "T"
    home: "."
    role: "Fine."
''')
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        code, _, error = self.cli(root, 'check')
        self.assertEqual(code, 0, error)
        self.assertNotIn('W305', error)

    def test_inline_quote_with_no_date(self):
        root = self.project('''person Owner: "Owner"
team T: "T"
    home: "."
    role: """{{Owner: "a, b"}}"""
''')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 1, error)
        self.assertIn('Inline quote: `` must be a date, `YYYY-MM-DD`.', error)

    def test_code_block_keeps_comma_braces(self):
        root = self.project('''workflow W: "title {{a, b}}"
    code sample: "Example"
        text: """{{a, b}}
"""
team T: "T"
    home: "."
    work: W
''')
        for command in ('build', 'check', 'sources'):
            with self.subTest(command=command):
                code, _, error = self.cli(root, command)
                self.assertEqual(code, 0, error)
        self.assertIn('{{a, b}}', (root / 'AGENTS.md').read_text())

    def test_citing_a_quote_leaves_owned_text_out_of_reach(self):
        source = '''person Owner: "Owner"
    owns:
        Other
quote Q: "Words"
    by: Owner
    on: "2026-11-05"
workflow Other: "Other"
    "Old."
team T: "T"
    home: "."
    role: "{{Q}}"
'''
        before, after = self.project(source), self.project(source.replace('"Old."', '"New."'))
        code, output, error = self.cli(after, 'diff', '--base-tree', str(before), '--json')
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)['homes'], [])
        self.assertEqual(json.loads(output)['changed_declarations'], [])

    def test_inline_words_keep_punctuation(self):
        root = self.project('''person A: "Author"
team T: "T"
    home: "."
    role: """{{A, 2026-11-05: "Say: "yes", please."}}"""
''')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 0, error)
        self.assertIn('Say: "yes", please.', (root / 'AGENTS.md').read_text())
        code, _, error = self.cli(root, 'check')
        self.assertEqual(code, 0, error)
        code, output, error = self.cli(root, 'sources')
        self.assertEqual(code, 0, error)
        self.assertIn('cited in 1 declaration, reaches 1 home', output)

    def test_self_line_passes_check(self):
        root = self.project('''workflow W: "Work"
    gates: "Gates"
        "Check."
    run: "Run"
        self:gates.title
team T: "T"
    home: "."
    work: W
''')
        for command in ('build', 'check', 'sources'):
            with self.subTest(command=command):
                code, _, error = self.cli(root, command)
                self.assertEqual(code, 0, error)

    def test_person_filter_takes_plain_name(self):
        root = self.project('''quote Q: "Words"
    by: Amir
    on: "2026-11-05"
team T: "T"
    home: "."
    role: "{{Q}}"
''')
        (root / 'prompts/shared').mkdir()
        (root / 'prompts/shared/people.prompt').write_text('export person Amir: "Amir"\n')
        for name in ('Amir', 'shared.people.Amir'):
            with self.subTest(name=name):
                code, output, error = self.cli(root, 'sources', '--person', name, '--json')
                self.assertEqual(code, 0, error)
                self.assertEqual(json.loads(output)['people'][0]['key'], 'shared.people.Amir')

    def test_glob_matches_only_sources(self):
        source = '''person A: "A"
    owns:
        "specs/*.md"
team T: "T"
    home: "."
    role: "Test."
'''
        root = self.project(source)
        (root / 'specs').mkdir()
        (root / 'specs/rules.md').write_text('# Rules\n\nRead this.\n')
        code, _, error = self.cli(root, 'check')
        self.assertEqual(code, 1)
        self.assertIn('Glob `specs/*.md` in `owns:` matches no source file.', error)
        (root / 'prompts/AGENTS.prompt').write_text(source + 'workflow Rules from "specs/rules.md"\n')
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        code, _, error = self.cli(root, 'check')
        self.assertEqual(code, 0, error)
        before = self.project(source + 'workflow Rules from "specs/rules.md"\n')
        (before / 'specs').mkdir()
        (before / 'specs/rules.md').write_text('# Rules\n\nOld.\n')
        code, output, error = self.cli(root, 'diff', '--base-tree', str(before), '--json')
        self.assertEqual(code, 0, error)
        self.assertIn({'name': 'Rules', 'owners': ['A']}, json.loads(output)['owned'])

    def test_quote_path_form_counts_as_cited(self):
        root = self.project('''person A: "A"
quote Q: "Words"
    by: A
    on: "2026-11-05"
workflow Unused: "Unused"
    "{{Q:title}}"
team T: "T"
    home: "."
    role: "Fine."
''')
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        code, _, error = self.cli(root, 'check')
        self.assertEqual(code, 0, error)
        self.assertNotIn('W305', error)
        code, output, error = self.cli(root, 'sources', '--json')
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)['people'][0]['quotes'][0]['cited_in'], ['Unused'])

    def test_inline_field_needs_text(self):
        for field in ('to', 'about', 'source'):
            with self.subTest(field=field):
                root = self.project('person A: "A"\nteam T: "T"\n    home: "."\n'
                                    '    role: """{{A, 2026-11-05, ' + field + ': "x"}}"""\n')
                code, _, error = self.cli(root, 'build')
                self.assertEqual(code, 1)
                self.assertIn(f'Inline quote: `{field}` needs text.', error)

    def test_inline_sites_ignore_walk_order(self):
        root = self.project('''person A: "A"
team T: """{{A, 2026-11-05: "First"}}"""
    home: "."
    role: """{{A, 2026-11-06: "Second"}}"""
''')
        code, output, error = self.cli(root, 'sources', '--json')
        self.assertEqual(code, 0, error)
        quotes = json.loads(output)['people'][0]['quotes']
        self.assertEqual([(q['on'], q['site']) for q in quotes], [
            ('2026-11-05', 'prompts/AGENTS.prompt:2'),
            ('2026-11-06', 'prompts/AGENTS.prompt:4'),
        ])

    def test_bare_quote_in_analysis_is_plain(self):
        root = self.project('''person A: "Author"
quote Q: "Words"
    by: A
    on: "2026-11-05"
analysis Study: "Study"
    stages: "Stages"
        Q
abstract agent Reader:
    role: "Test."
    analysis: Study
team T: "T"
    home: "."
    member reader[Reader]: "Reader"
''')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 0, error)
        text = (root / 'reader/AGENTS.md').read_text().splitlines()
        self.assertIn('Author, November 5, 2026: "Words"', text)
