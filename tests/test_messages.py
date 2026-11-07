from __future__ import annotations

import json
import unittest

from doctrine.compiler import CompilationSession
from doctrine.parser import parse_file
from tests.ws3_support import HomeProject


MESSAGE = '''output Note: "Note"
    target: Message
        to: T.reader
    "Read this."
    bullets carries: "It carries"
        "A change"
team T: "the team"
    home: "team"
    member sender: "sender"
        role: "Send."
        outputs: "Outputs"
            Note
    member reader: "reader"
        role: "Read."
        inputs: "Inputs"
            Note
'''


class MessageTests(HomeProject, unittest.TestCase):
    def build(self, source):
        root = self.project(source)
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 0, error)
        return root

    def warnings(self, source):
        root = self.project(source)
        code, output, error = self.cli(root, "check", "--json", "--target", "homes")
        self.assertEqual(code, 0, error)
        return [row["text"] for row in json.loads(output)["warnings"] if row["code"] == "W303"]

    def test_both_homes_share_body(self):
        root = self.build(MESSAGE)
        sender = (root / "team/sender/AGENTS.md").read_text()
        reader = (root / "team/reader/AGENTS.md").read_text()
        self.assertIn("Send this to the team's reader.", sender)
        self.assertIn("You receive this message.", reader)
        for text in (sender, reader):
            self.assertIn("Read this.\n\n#### It carries\n\n- A change", text)
        root = self.build(MESSAGE.replace("to: T.reader", "to: T"))
        self.assertIn("Send this to the team.", (root / "team/sender/AGENTS.md").read_text())

    def test_field_change_reaches_both(self):
        root = self.build(MESSAGE.replace('"A change"', '"A new change"'))
        for home in ("sender", "reader"):
            self.assertIn("- A new change", (root / f"team/{home}/AGENTS.md").read_text())

    def test_e660_shape_on_message(self):
        root = self.project(MESSAGE.replace('    "Read this."', '    shape: MarkdownDocument\n    "Read this."'))
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 1)
        self.assertIn("`Message` output `Note` can't have `shape`. A message is prose.", error)

    def test_e301_for_other_targets_stays(self):
        source = MESSAGE.replace('target: Message\n        to: T.reader', 'target: TurnResponse\n    shape: Comment')
        root = self.project(source)
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 1)
        self.assertIn("E301", error)

    def test_w303_no_reader(self):
        source = MESSAGE.replace('        inputs: "Inputs"\n            Note\n', '')
        self.assertEqual(self.warnings(source), [
            "W303 message without reader: Note goes to T.reader, and nothing there reads it."
        ])
        source = '''output Note: "Note"
    target: Message
        to: Reader
agent Reader: "Reader"
    role: "Read."
'''
        self.assertEqual(self.warnings(source), [
            "W303 message without reader: Note goes to Reader, and nothing there reads it."
        ])
        source += '    inputs: "Inputs"\n        Note\n'
        self.assertEqual(self.warnings(source), [])

    def test_string_to_has_no_reader_check(self):
        source = MESSAGE.replace('to: T.reader', 'to: "your next session"').replace('        inputs: "Inputs"\n            Note\n', '')
        self.assertEqual(self.warnings(source), [])

    def test_same_agent_sends_and_reads(self):
        source = MESSAGE.replace('to: T.reader', 'to: T.sender').replace('        outputs: "Outputs"', '        inputs: "Inputs"\n            Note\n        outputs: "Outputs"')
        root = self.build(source)
        text = (root / "team/sender/AGENTS.md").read_text()
        self.assertIn("You receive this message.", text)
        self.assertIn("Send this to the team's sender.", text)
        self.assertEqual(self.warnings(source), [])

    def test_e660_each_field(self):
        for field, line in (("shape", "shape: Comment"), ("requirement", "requirement: Required"),
                            ("schema", "schema: Missing"), ("structure", "structure: Missing"),
                            ("files", 'files: "Files"\n        file: "File"')):
            with self.subTest(field=field):
                source = MESSAGE.replace('    "Read this."', f'    {line}\n    "Read this."')
                root = self.project(source)
                code, _, error = self.cli(root, "build")
                self.assertEqual(code, 1)
                self.assertIn(f"`Message` output `Note` can't have `{field}`. A message is prose.", error)
        root = self.project(MESSAGE.replace('        to: T.reader\n', ''))
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 1)
        self.assertIn("E233", error)

    def test_e660_bad_to_ref(self):
        source = 'workflow Other: "Other"\n    "Work."\n' + MESSAGE.replace('to: T.reader', 'to: Other')
        root = self.project(source)
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 1)
        self.assertIn('`to:` in `Note` must be an agent, a team, or a string.', error)
        for ref in ('Missing', 'self:foo'):
            root = self.project(MESSAGE.replace('to: T.reader', f'to: {ref}'))
            code, _, error = self.cli(root, "build")
            self.assertEqual(code, 1)
            self.assertIn('`to:` in `Note` must be an agent, a team, or a string.', error)

    def test_w303_inherited_input_counts(self):
        source = MESSAGE.replace('team T:', 'abstract agent Reader:\n    role: "Read."\n    inputs: "Inputs"\n        Note\nteam T:').replace('member reader: "reader"\n        role: "Read."\n        inputs: "Inputs"\n            Note', 'member reader[Reader]: "reader"')
        self.assertEqual(self.warnings(source), [])

    def test_w303_team_scope(self):
        source = MESSAGE.replace('to: T.reader', 'to: T')
        self.assertEqual(self.warnings(source), [])
        source = source.replace('home: "team"', 'home: "team/inner"').replace('team T: "the team"', 'team Outer: "outer"\n    home: "team"\n    role: "Lead."\nteam T: "the team"').replace('to: T\n', 'to: Outer\n')
        self.assertEqual(self.warnings(source), [])
        self.assertEqual(len(self.warnings(source.replace('        inputs: "Inputs"\n            Note\n', ''))), 1)

    def test_message_input_in_flow_graph(self):
        root = self.project('''output Note: "Note"
    target: Message
        to: Reader
agent Reader: "Reader"
    role: "Read."
    inputs: "Inputs"
        Note
    outputs: "Outputs"
        Note
''')
        session = CompilationSession(parse_file(root / "prompts/AGENTS.prompt"))
        graph = session.extract_target_flow_graph(("Reader",))
        self.assertEqual([item.name for item in graph.inputs], ["Note"])
        self.assertTrue(any(edge.kind == "consume" and edge.source_name == "Note" for edge in graph.edges))
        self.assertEqual([item.name for item in graph.outputs], ["Note"])
