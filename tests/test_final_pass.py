from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.home_support import HomeProject


class FinalPassTests(HomeProject, unittest.TestCase):
    def test_member_home_gets_schema_and_contract(self):
        root = self.project('''output schema S: "Schema"
    field text: "Text"
        type: string
output shape Shape: "Shape"
    kind: JsonObject
    schema: S
output Result: "Result"
    target: TurnResponse
    shape: Shape
    requirement: Required
abstract agent Reporter:
    role: "Report."
    outputs: "Outputs"
        Result
    final_output: Result
team T: "Team"
    home: "team"
    member a1[Reporter]: "Reporter"
''')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 0, error)
        text = (root / 'team/a1/AGENTS.md').read_text()
        self.assertIn('schemas/result.schema.json', text)
        for name in ('team/a1/schemas/result.schema.json', 'team/a1/final_output.contract.json'):
            self.assertTrue((root / name).is_file())
            self.assertIn(name, json.loads((root / 'HOMES.contract.json').read_text())['files'])
        self.assertEqual(self.cli(root, 'build', '--check')[0], 0)

    def test_message_title_uses_receiver_values(self):
        root = self.project('''output Note: "Note"
    target: Message
        to: Beta.lead
team Alpha: "Alpha"
    home: "alpha"
    values:
        pod: "alpha pod"
    member sender: "sender"
        role: "Send."
        outputs: "Outputs"
            Note
team Beta: "Beta"
    home: "beta"
    values:
        pod: "beta pod"
    member lead: "{{team:pod}} lead"
        role: "Lead."
''')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 0, error)
        self.assertIn("Send this to Beta's beta pod lead.", (root / 'alpha/sender/AGENTS.md').read_text())

    def test_roster_in_shared_details_is_e621(self):
        root = self.project('''workflow W: "Work"
    details who: "Who"
        roster members: "Members"
            who: "Who" = "{{agent:title}}"
team Alpha: "Alpha"
    home: "alpha"
    work: W
    member a: "A"
        role: "A."
team Beta: "Beta"
    home: "beta"
    work: W
    member b: "B"
        role: "B."
''')
        code, _, error = self.cli(root, 'build')
        self.assertEqual(code, 1)
        self.assertIn('E621', error)

    def test_team_library_outside_project_root(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'project'
            (root / 'prompts').mkdir(parents=True)
            (base / 'shared/prompts/lib').mkdir(parents=True)
            (base / 'shared/prompts/lib/base.prompt').write_text('''export abstract team Base: "Base"
    member lead: "Lead"
        role: "Lead."
''')
            (root / 'prompts/AGENTS.prompt').write_text('''import lib.base
team Mine[lib.base.Base]: "Mine"
    home: "mine"
    inherit *
''')
            (root / 'pyproject.toml').write_text('''[tool.doctrine.compile]
additional_prompt_roots = ["../shared/prompts"]
[[tool.doctrine.emit.targets]]
name = "homes"
entrypoint = "prompts/AGENTS.prompt"
output_dir = "."
''')
            code, _, error = self.cli(root, 'build')
            self.assertEqual(code, 0, error)
            self.assertIn('source=../shared/prompts/lib/base.prompt', (root / 'mine/lead/AGENTS.md').read_text())

    def test_self_reading_title_is_e603(self):
        for title, role in (('Alpha {{team:title}}', 'Lead.'), ('Alpha', 'Lead.')):
            with self.subTest(title=title):
                member = 'Ann of {{team:members}}' if title == 'Alpha' else 'Ann'
                root = self.project(f'''team Alpha: "{title}"
    home: "alpha"
    role: "{role}"
    member a1: "{member}"
        role: "A."
''')
                code, _, error = self.cli(root, 'build')
                self.assertEqual(code, 1)
                self.assertIn('E603', error)

    def test_skill_target_is_usage_error(self):
        root = self.project('agent A:\n    role: "A."\n')
        (root / 'prompts/SKILL.prompt').write_text('skill package S: "Skill"\n    "Read."\n')
        with (root / 'pyproject.toml').open('a') as config:
            config.write('''\n[[tool.doctrine.emit.targets]]
name = "sk"
entrypoint = "prompts/SKILL.prompt"
output_dir = "skill"
''')
        code, _, error = self.cli(root, 'build', '--target', 'sk')
        self.assertEqual(code, 2)
        self.assertIn('Target sk has no homes.', error)
