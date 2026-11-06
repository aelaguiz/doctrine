from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from doctrine._compiler.context import CompilationContext
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class LateBindingTests(unittest.TestCase):
    def session(self, source, files=None):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        path = root / 'prompts/AGENTS.prompt'
        path.parent.mkdir()
        path.write_text(source)
        for name, text in (files or {}).items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        return CompilationSession(parse_file(path))

    def render(self, source, name='A'):
        return render_markdown(self.session(source).compile_agent(name))

    def test_value_reaches_parent_workflow_text(self):
        source = '''workflow W: "Work"
    "First {{agent:unit}}."
    "Second {{agent:unit}}."
abstract agent Base:
    role: "Test {{agent:unit}}."
    work: W
agent A[Base]:
    values:
        unit: "change"
    inherit *
'''
        self.assertEqual(self.render(source), 'Test change.\n\n## Work\n\nFirst change.\n\nSecond change.\n')

    def test_value_in_title(self):
        self.assertIn('## Test changes\n', self.render('agent A:\n    role: "Test."\n    values:\n        unit: "changes"\n    work: "Test {{agent:unit}}"\n        "Read."\n'))

    def test_value_in_markdown_block(self):
        for kind in ('markdown', 'html'):
            with self.subTest(kind=kind):
                self.assertIn('Test changes.', self.render(f'agent A:\n    role: "Test."\n    values:\n        unit: "changes"\n    work: "Work"\n        {kind} text: "Text"\n            text: """Test {{{{agent:unit}}}}.\n"""\n'))

    def test_code_block_stays_literal(self):
        self.assertIn('{{agent:unit}}', self.render('agent A:\n    role: "Test."\n    work: "Work"\n        code literal: "Literal"\n            text: """{{agent:unit}}\n"""\n'))

    def test_resolved_declaration_cache_shared_across_agents(self):
        context = CompilationContext(self.session('''workflow W: "Work"
    "Test {{agent:unit}}."
agent A:
    role: "A."
    values:
        unit: "first"
    work: W
agent B:
    role: "B."
    values:
        unit: "second"
    work: W
'''))
        with patch.object(context, '_resolve_workflow_body', wraps=context._resolve_workflow_body) as resolve:
            first = render_markdown(context.compile_agent('A'))
            cached = context._resolved_workflow_cache[((), 'W')]
            second = render_markdown(context.compile_agent('B'))
        self.assertEqual(resolve.call_count, 1)
        self.assertIs(context._resolved_workflow_cache[((), 'W')], cached)
        self.assertIn('first', first)
        self.assertIn('second', second)
        self.assertIn('{{agent:unit}}', cached.preamble[0])

    def test_e601_lists_all_blanks_and_sites(self):
        session = self.session('agent A:\n    role: "{{agent:first}} {{agent:second}}"\n    work: "Work"\n        "{{agent:first}}"\n')
        with self.assertRaises(CompileError) as caught:
            session.compile_agent('A')
        diagnostic = caught.exception.diagnostic
        self.assertEqual(diagnostic.code, 'E601')
        path = session.root_flow.entrypoint_path
        self.assertEqual(diagnostic.detail, f'Home `A` reads values nothing fills:\n- `agent:first` at {path}:2\n- `agent:first` at {path}:4\n- `agent:second` at {path}:2')

    def test_e603_prints_cycle(self):
        with self.assertRaises(CompileError) as caught:
            self.render('agent A:\n    role: "{{agent:a}}"\n    values:\n        a: "{{agent:b}}"\n        b: "{{agent:a}}"\n')
        self.assertEqual(caught.exception.code, 'E603')
        self.assertEqual(caught.exception.diagnostic.detail, 'Values read each other: `a -> b -> a`')

    def test_e602_in_skill_package(self):
        session = self.session('skill package P: "Package"\n    "Read {{agent:unit}}."\n')
        with self.assertRaises(CompileError) as caught:
            session.compile_skill_package('P')
        self.assertEqual(caught.exception.code, 'E602')
        self.assertEqual(caught.exception.diagnostic.detail, "`{{agent:unit}}` can't be read here: a skill package has no home.")

    def test_e602_in_output_schema(self):
        session = self.session('''output schema S: "Schema"
    field text: "Text"
        type: string
        note: "Read {{agent:unit}}."
output shape Shape: "Shape"
    kind: JsonObject
    schema: S
output O: "Output"
    target: TurnResponse
    shape: Shape
    requirement: Required
agent A:
    role: "A."
    outputs: "Outputs"
        O
    final_output: O
''')
        with self.assertRaises(CompileError) as caught:
            session.compile_agent('A')
        self.assertEqual(caught.exception.code, 'E602')
        self.assertEqual(caught.exception.diagnostic.detail, "`{{agent:unit}}` can't be read here: output schema text is machine text.")

    def test_value_reads_value(self):
        self.assertIn('test-changes', self.render('agent A:\n    role: "{{agent:handle}}"\n    values:\n        handle: "test-{{agent:unit}}"\n        unit: "changes"\n'))

    def test_value_refs_keep_the_module_that_wrote_them(self):
        session = self.session('''import roles
workflow Local: "Wrong"
    "Wrong."
agent A[roles.Base]:
    values:
        ending: "today"
    inherit *
''', {'prompts/roles/AGENTS.prompt': '''workflow Local: "Right"
    "Right."
export abstract agent Base:
    role: "{{agent:words}}"
    values:
        words: "{{Local:title}} {{agent:ending}}"
'''})
        self.assertEqual(render_markdown(session.compile_agent('A')), 'Right today\n')

    def test_e601_excludes_unread_sites_and_keeps_imported_sites(self):
        session = self.session('''import craft
workflow Unread: "Unread"
    "Unused {{agent:blank}}."
agent A:
    role: "Role."
    work: craft.W
''', {'prompts/craft/AGENTS.prompt': 'export workflow W: "Work"\n    "Read {{agent:blank}}."\n'})
        with self.assertRaises(CompileError) as caught:
            session.compile_agent('A')
        detail = caught.exception.diagnostic.detail
        self.assertEqual(caught.exception.code, 'E601')
        self.assertEqual(detail.count('- `agent:blank` at'), 1)
        self.assertIn('/prompts/craft/AGENTS.prompt:2', detail)

    def test_e602_in_emitted_document(self):
        session = self.session('''document D: "Doc"
    "Read {{team:title}}."
skill package P: "Package"
    emit:
        "references/doc.md": D
    "Read the doc."
''')
        with self.assertRaises(CompileError) as caught:
            session.compile_skill_package('P')
        self.assertEqual(caught.exception.code, 'E602')
        self.assertEqual(caught.exception.diagnostic.detail, "`{{team:title}}` can't be read here: an emitted document has no home.")
