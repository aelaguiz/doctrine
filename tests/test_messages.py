from __future__ import annotations

import json
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.parser import parse_file
from doctrine.emit_common import load_emit_targets
from doctrine.emit_docs import emit_target
from tests.home_support import HomeProject


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
        code, _, error = self.cli(root, "build", "--target", "homes")
        self.assertEqual(code, 0, error)
        return root

    def warnings(self, source):
        root = self.project(source)
        self.assertEqual(self.cli(root, "build", "--target", "homes")[0], 0)
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
agent Sender: "Sender"
    role: "Send."
    outputs: "Outputs"
        Note
'''
        self.assertEqual(self.warnings(source), [
            "W303 message without reader: Note goes to Reader, and nothing there reads it."
        ])
        source = source.replace('    role: "Read."', '    role: "Read."\n    inputs: "Inputs"\n        Note')
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
        self.assertIn('E299', error)
        for ref, expected in (('Missing', 'E299'), ('self:foo', '`to:` in `Note` must be an agent, a team, or a string.')):
            root = self.project(MESSAGE.replace('to: T.reader', f'to: {ref}'))
            code, _, error = self.cli(root, "build")
            self.assertEqual(code, 1)
            self.assertIn(expected, error)

    def test_w303_inherited_input_counts(self):
        source = MESSAGE.replace('team T:', 'abstract agent Reader:\n    role: "Read."\n    inputs: "Inputs"\n        Note\nteam T:').replace('member reader: "reader"\n        role: "Read."\n        inputs: "Inputs"\n            Note', 'member reader[Reader]: "reader"')
        self.assertEqual(self.warnings(source), [])

    def test_w303_team_scope(self):
        source = MESSAGE.replace('to: T.reader', 'to: T')
        self.assertEqual(self.warnings(source), [])
        source = source.replace('home: "team"', 'home: "team/inner"').replace('team T: "the team"', 'team Outer: "outer"\n    home: "team"\n    role: "Lead."\nteam T: "the team"').replace('to: T\n', 'to: Outer\n')
        self.assertEqual(self.warnings(source), [])
        self.assertEqual(len(self.warnings(source.replace('        inputs: "Inputs"\n            Note\n', ''))), 1)

    def test_w303_skips_abstract_scope(self):
        for declaration in ('abstract team Scope: "Scope"\n    member reader: "reader"\n        role: "Read."\n',
                            'abstract agent Scope:\n    role: "Read."\n'):
            with self.subTest(declaration=declaration):
                source = declaration + MESSAGE.replace('to: T.reader', 'to: Scope')
                self.assertEqual(self.warnings(source), [])

    def test_w303_unsent_message_has_no_check(self):
        source = '''output Unsent: "Unsent"
    target: Message
        to: Reader
output Unused[Missing]: "Unused"
    inherit target
agent Reader: "Reader"
    role: "Read."
'''
        self.assertEqual(self.warnings(source), [])

    def test_w303_child_output_reads_as_itself(self):
        source = '''output Base: "Base"
    target: Message
        to: T.reader
output Child[Base]: "Child"
    inherit target
team T: "Team"
    home: "team"
    member sender: "sender"
        role: "Send."
        outputs: "Outputs"
            Child
    member another: "another sender"
        role: "Send."
        outputs: "Outputs"
            Child
    member reader: "reader"
        role: "Read."
        inputs: "Inputs"
            Child
'''
        self.assertEqual(self.warnings(source), [])
        source = source.replace('        inputs: "Inputs"\n            Child\n', '')
        self.assertEqual(self.warnings(source), [
            "W303 message without reader: Child goes to T.reader, and nothing there reads it."
        ])

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

    def test_message_in_sibling_file(self):
        source = '''agent Reader: "Reader"
    role: "Read."
    inputs: "Inputs"
        Note
'''
        root = self.project(source)
        sibling = root / "prompts/note.prompt"
        sibling.write_text('''output Note: "Note"
    target: Message
        to: Reader
    "A short note."
''')
        code, _, error = self.cli(root, "build", "--target", "homes")
        self.assertEqual(code, 0, error)
        self.assertIn("You receive this message.", (root / "reader/AGENTS.md").read_text())
        sibling.write_text('''output Note: "Note"
    target: TurnResponse
    shape: Comment
''')
        code, _, error = self.cli(root, "build", "--target", "homes")
        self.assertEqual(code, 1)
        self.assertIn("E301", error)

    def test_to_follows_export_rule(self):
        for recipient, declaration in (
            ('lib.Reader', 'agent Reader: "Reader"\n    role: "Read."\n'),
            ('lib.Remote', 'team Remote: "Remote"\n    home: "remote"\n    member reader: "reader"\n        role: "Read."\n'),
            ('lib.Remote.reader', 'team Remote: "Remote"\n    home: "remote"\n    member reader: "reader"\n        role: "Read."\n'),
        ):
            with self.subTest(recipient=recipient):
                root = self.project('import lib\n' + MESSAGE.replace('to: T.reader', f'to: {recipient}'))
                (root / "prompts/lib").mkdir()
                lib = root / "prompts/lib/AGENTS.prompt"
                lib.write_text(declaration)
                code, _, error = self.cli(root, "build")
                self.assertEqual(code, 1)
                self.assertIn("E314", error)
                lib.write_text('export ' + declaration)
                code, _, error = self.cli(root, "build")
                self.assertEqual(code, 0, error)
        root = self.project('''abstract team Template: "Template"
    member reader: "reader"
        role: "Read."
''' + MESSAGE.replace('to: T.reader', 'to: Template.reader'))
        code, _, error = self.cli(root, "build")
        self.assertEqual(code, 1)
        self.assertIn("E276", error)

    def test_child_output_keeps_parent_to(self):
        for import_line, parent in (("import lib", "lib.Base"),
                                    ("import lib as l", "l.Base"),
                                    ("from lib import Base", "Base")):
            for recipient, title in (("Reader", "Reader"), ("T", "Team"), ("T.reader", "Team's reader")):
                with self.subTest(import_line=import_line, recipient=recipient):
                    root = self.project(f'''{import_line}
output Child[{parent}]: "Child"
    inherit target
agent Sender: "Sender"
    role: "Send."
    outputs: "Outputs"
        Child
''')
                    (root / "prompts/lib").mkdir()
                    (root / "prompts/lib/AGENTS.prompt").write_text(f'''export output Base: "Base"
    target: Message
        to: {recipient}
agent Reader: "Reader"
    role: "Read."
team T: "Team"
    home: "team"
    member reader: "reader"
        role: "Read."
''')
                    code, _, error = self.cli(root, "build", "--target", "homes")
                    self.assertEqual(code, 0, error)
                    self.assertIn(f"Send this to {title}.", (root / "sender/AGENTS.md").read_text())

    def test_w303_team_in_another_flow(self):
        root = self.project('''from lib import Note
agent Sender: "Sender"
    role: "Send."
    outputs: "Outputs"
        Note
''')
        (root / "prompts/lib").mkdir()
        lib = root / "prompts/lib/AGENTS.prompt"
        lib.write_text('''export output Note: "Note"
    target: Message
        to: Outer
team Outer: "Outer"
    home: "team"
team Inner: "Inner"
    home: "team/inner"
    member reader: "reader"
        role: "Read."
        inputs: "Inputs"
            Note
''')
        self.assertEqual(self.cli(root, "build", ".", "--target", "homes")[0], 0)
        code, output, error = self.cli(root, "check", "--json", "--target", "homes")
        self.assertEqual(code, 0, error)
        self.assertFalse([row for row in json.loads(output)["warnings"] if row["code"] == "W303"])
        lib.write_text(lib.read_text().replace('        inputs: "Inputs"\n            Note\n', ''))
        self.assertEqual(self.cli(root, "build", ".", "--target", "homes")[0], 0)
        code, output, error = self.cli(root, "check", "--json", "--target", "homes")
        self.assertEqual(code, 0, error)
        self.assertEqual(len([row for row in json.loads(output)["warnings"] if row["code"] == "W303"]), 1)

    def test_review_comment_message(self):
        prompts = Path(__file__).resolve().parents[1] / "examples/86_imported_review_comment_local_routes/prompts"
        output = (prompts / "shared/review/AGENTS.prompt").read_text()
        output = output.replace("export output DraftReviewComment", "output ImportedComment")
        output = output.replace("target: TurnResponse\n    shape: Comment\n    requirement: Required",
                                "target: Message\n        to: Reader")
        source = (prompts / "AGENTS.prompt").read_text().replace(
            "from shared.review import DraftReviewComment as ImportedComment", output)
        source += '''
agent Reader: "Reader"
    role: "Read."
    inputs: "Inputs"
        ImportedComment
'''
        root = self.build(source)
        reader = (root / "reader/AGENTS.md").read_text()
        sender = next(path.read_text() for path in root.rglob("AGENTS.md")
                      if "Use an imported comment output that still binds" in path.read_text())
        self.assertIn("You receive this message.", reader)
        self.assertIn("Send this to Reader.", sender)
        self.assertIn("Name the failing review gates in authored order.", reader)
        self.assertIn("Name the failing review gates in authored order.", sender)

    def test_sidecar_names_message_target(self):
        root = self.project('''output Done: "Done"
    target: TurnResponse
    shape: Comment
output Note: "Note"
    target: Message
        to: "next session"
agent Sender: "Sender"
    role: "Send."
    outputs: "Outputs"
        Done
        Note
    final_output: Done
''')
        (root / "pyproject.toml").write_text('''[[tool.doctrine.emit.targets]]
name = "docs"
entrypoint = "prompts/AGENTS.prompt"
output_dir = "build"
''')
        emit_target(load_emit_targets(root / "pyproject.toml")["docs"])
        contract = json.loads((root / "build/sender/final_output.contract.json").read_text())
        note = next(item for item in contract["io"]["outputs"] if item["declaration_key"] == "Note")
        self.assertEqual(note["target"]["key"], "Message")
        self.assertEqual(note["target"]["title"], "Message")
        self.assertEqual(note["readback_mode"], "unsupported")

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
