from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from doctrine import model
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError, ParseError
from doctrine.parser import parse_file, parse_text
from doctrine.renderer import render_markdown
from doctrine._compiler.resolve.patches import expand_patch_items


class PatchLanguageTests(unittest.TestCase):
    def _assert_kind(self, kind):
        unit = SimpleNamespace(prompt_file=SimpleNamespace(source_path=None))
        inherit = model.AuthoredSlotInherit if kind == "agent" else model.InheritItem
        expansion = expand_patch_items(
            (model.DropItem(("b",), "Not used here."), model.InheritAll()),
            parent_keys=("a", "b", "c"), kind=kind, owner_label="Child", unit=unit,
        )
        self.assertEqual([item.key for item in expansion.items], ["a", "c"])
        self.assertEqual(expansion.dropped_keys, {"b"})
        self.assertEqual(set(item.key for item in expansion.items) | expansion.dropped_keys,
                         {"a", "b", "c"})
        for code, items in (
            ("E610", (model.DropItem(("gone",), "Gone."),)),
            ("E612", (model.DropItem(("a",), "Gone."), inherit("a"))),
            ("E613", (model.InheritAll(), model.InheritAll())),
        ):
            with self.subTest(kind=kind, code=code), self.assertRaises(CompileError) as caught:
                expand_patch_items(items, parent_keys=("a", "b", "c"), kind=kind,
                                   owner_label="Child", unit=unit)
            self.assertEqual(caught.exception.code, code)

    def test_agent(self):
        self._assert_kind("agent")

    def test_workflow(self):
        self._assert_kind("workflow")

    def test_document(self):
        self._assert_kind("document")

    def test_analysis(self):
        self._assert_kind("analysis")

    def test_schema(self):
        self._assert_kind("schema")

    def test_review(self):
        self._assert_kind("review")

    def test_review_family(self):
        self._assert_kind("review_family")

    def test_abstract_review(self):
        self._assert_kind("abstract review")

    def test_skills(self):
        self._assert_kind("skills")

    def test_inputs(self):
        self._assert_kind("inputs")

    def test_outputs(self):
        self._assert_kind("outputs")

    def test_output(self):
        self._assert_kind("output")

    def test_output_shape(self):
        self._assert_kind("output shape")

    def test_output_schema(self):
        self._assert_kind("output schema")

    def test_receipt(self):
        self._assert_kind("receipt")

    def _render(self, source, agent="Child"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prompts" / "AGENTS.prompt"
            path.parent.mkdir()
            path.write_text(source)
            return render_markdown(CompilationSession(parse_file(path)).compile_agent(agent))

    def test_wildcard_keeps_override_in_parent_position(self):
        result = self._render('''abstract agent Base:
    role: "Base."
    a: "A"
        "First."
    b: "B"
        "Second."
agent Child[Base]:
    override b: "New B"
        "Replacement."
    inherit *
''')
        self.assertLess(result.index("## A"), result.index("## New B"))

    def test_explicit_inherit_moves_item_past_wildcard(self):
        result = self._render('''abstract agent Base:
    role: "Base."
    a: "A"
        "First."
    b: "B"
        "Second."
agent Child[Base]:
    inherit *
    inherit a
''')
        self.assertLess(result.index("## B"), result.index("## A"))

    def test_drop_requires_reason_parse_error(self):
        with self.assertRaises(ParseError) as caught:
            parse_text('agent A:\n    drop key\n')
        self.assertEqual(caught.exception.code, "E101")

    def test_disjoint_dotted_patches_are_legal(self):
        result = self._render('''abstract agent Base:
    role: "Base."
    craft: "Craft"
        a: "A"
            "First."
        b: "B"
            "Second."
agent Child[Base]:
    inherit role
    override craft.a: "New A"
        "Replacement."
    drop craft.b: "Not used here."
''')
        self.assertIn("### New A\n\nReplacement.", result)
        self.assertNotIn("Second.", result)

    def test_inherit_beside_dotted_patch_is_e612(self):
        unit = SimpleNamespace(prompt_file=SimpleNamespace(source_path=None))
        for items in (
            (model.InheritItem("a"), model.DropItem(("a", "b"), "Gone.")),
            (model.DropItem(("a", "b"), "Gone."), model.InheritItem("a")),
        ):
            with self.assertRaises(CompileError) as caught:
                expand_patch_items(items, parent_keys=("a",), kind="workflow",
                                   owner_label="Child", unit=unit)
            self.assertEqual(caught.exception.code, "E612")

    def test_dotted_override_on_table_is_e611(self):
        with self.assertRaises(CompileError) as caught:
            self._render('''abstract agent Base:
    role: "Base."
    craft: "Craft"
        table checks: "Checks"
            columns:
                check: "Check"
agent Child[Base]:
    inherit role
    override craft.checks: "Checks"
        "Replacement."
''')
        self.assertEqual(caught.exception.code, "E611")
        self.assertIn("targets a `table`", str(caught.exception))

    def test_paragraph_override_rejects_section_body(self):
        with self.assertRaises(CompileError) as caught:
            self._render('''abstract agent Base:
    role: "Base."
    craft: "Craft"
        paragraph lead: "Lead."
            "First."
agent Child[Base]:
    inherit role
    override craft.lead: "Lead."
        nested: "Nested"
            "No."
''')
        self.assertEqual(caught.exception.code, "E611")
        self.assertIn("gives a paragraph a body it can't hold", str(caught.exception))
