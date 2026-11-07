from __future__ import annotations

import json
import unittest

from tests.test_diff import SOURCE
from tests.ws3_support import HomeProject


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
        self.assertIn('Glob `missing/*.prompt` in `owns:` matches no file.', error)

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

    def test_build_does_not_read_ownership(self):
        root = self.project('person A: "A"\n    owns:\n        Missing\n' + SOURCE)
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 0, error)

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
