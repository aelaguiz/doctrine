from __future__ import annotations

import json
import tempfile
import textwrap
import unittest
from pathlib import Path
from types import SimpleNamespace

from doctrine import model
from doctrine.compiler import CompilationSession
from doctrine._compiler.context import CompilationContext
from doctrine.diagnostics import CompileError, ParseError
from doctrine.emit_common import load_emit_targets
from doctrine.emit_docs import emit_target
from doctrine.parser import parse_file, parse_text
from doctrine.renderer import render_markdown, render_readable_block
from doctrine._compiler.resolve.patches import expand_patch_items


class PatchLanguageTests(unittest.TestCase):
    def _assert_patches(
        self, source, *, keys=("a", "b", "c"), package=False, readable=None, shape=False
    ):
        def compile_patch(patch):
            authored = source.replace("    PATCH\n", textwrap.indent(patch, "    "))
            if package or readable:
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "prompts" / "SKILL.prompt"
                    path.parent.mkdir()
                    path.write_text(authored)
                    session = CompilationSession(parse_file(path))
                    if readable:
                        return render_readable_block(
                            session.compile_readable_declaration(readable, "Patched")
                        )
                    compiled = session.compile_skill_package("Package")
                    return ",".join(
                        field.key for field in compiled.contract.host_contract[0].receipt.fields
                    )
            if shape:
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "prompts" / "AGENTS.prompt"
                    path.parent.mkdir()
                    path.write_text(authored)
                    context = CompilationContext(CompilationSession(parse_file(path)))
                    context.compile_agent("Child")
                    resolved = context._resolve_local_output_shape_decl(
                        "Patched",
                        unit=context.root_entrypoint_unit,
                    )
                    return ",".join(item.key for item in resolved.items)
            return self._render(authored)

        a, b, c = keys
        result = compile_patch(f'drop {b}: "Not used here."\ninherit *\n')
        labels = keys if package or shape else ("Alpha", "Bravo", "Charlie")
        self.assertIn(labels[0], result)
        self.assertNotIn(labels[1], result)
        self.assertIn(labels[2], result)
        self.assertLess(result.index(labels[0]), result.index(labels[2]))
        for code, patch in (
            ("E610", 'drop gone: "Gone."\ninherit *\n'),
            ("E612", f'drop {a}: "Gone."\ninherit {a}\ninherit *\n'),
            ("E613", "inherit *\ninherit *\n"),
        ):
            with self.subTest(code=code), self.assertRaises(CompileError) as caught:
                compile_patch(patch)
            self.assertEqual(caught.exception.code, code)

    def test_agent(self):
        self._assert_patches("""abstract agent Base:
    role: "Base."
    a: "Alpha"
        "First."
    b: "Bravo"
        "Middle."
    c: "Charlie"
        "Last."
agent Child[Base]:
    PATCH
""")

    def test_workflow(self):
        self._assert_patches("""workflow Base: "Base"
    a: "Alpha"
        "First."
    b: "Bravo"
        "Middle."
    c: "Charlie"
        "Last."
workflow Patched[Base]: "Patched"
    PATCH
agent Child:
    role: "Role."
    work: Patched
""")

    def test_document(self):
        self._assert_patches("""document Base: "Base"
    section a: "Alpha"
        "First."
    section b: "Bravo"
        "Middle."
    section c: "Charlie"
        "Last."
document Patched[Base]: "Patched"
    PATCH
input Draft: "Draft"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
    structure: Patched
agent Child:
    role: "Role."
    inputs: "Inputs"
        Draft
""")

    def test_analysis(self):
        self._assert_patches("""analysis Base: "Base"
    a: "Alpha"
        "First."
    b: "Bravo"
        "Middle."
    c: "Charlie"
        "Last."
analysis Patched[Base]: "Patched"
    PATCH
agent Child:
    role: "Role."
    analysis: Patched
""")

    def test_schema(self):
        self._assert_patches(
            """input Doc: "Doc"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
schema Base: "Base"
    "Head prose."
    sections:
        a: "Alpha"
            "First."
    gates:
        b: "Bravo"
            "Middle."
    artifacts:
        c: "Charlie"
            ref: Doc
schema Patched[Base]: "Patched"
    inherit preamble
    PATCH
""",
            keys=("sections", "gates", "artifacts"),
            readable="schema",
        )

    def _assert_review_patches(self, kind):
        source = """input Draft: "Draft"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
workflow Contract: "Contract"
    complete: "Complete"
        "Check it."
output Comment: "Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required
    verdict: "Verdict"
        "Verdict."
    reviewed_artifact: "Artifact"
        "Artifact."
    analysis: "Analysis"
        "Analysis."
    readback: "Readback"
        "Readback."
    next_owner: "Owner"
        "Ask {{Owner}}."
    failing_gates: "Failing Gates" when verdict == ReviewVerdict.changes_requested:
        "Failures."
KIND Base: "Base"
    comment_output: Comment
    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis
        readback: readback
        next_owner: next_owner
        failing_gates: failing_gates
    a: "Alpha"
        reject "First." when Draft.missing_a
    b: "Bravo"
        reject "Middle." when Draft.missing_b
    c: "Charlie"
        reject "Last." when Draft.missing_c
KIND Patched[Base]: "Patched"
    PATCH
review Concrete[Patched]: "Review"
    subject: Draft
    contract: Contract
    inherit *
    check: "Check"
        accept "Ready." when contract.passes
    on_accept:
        current none
        route "Done." -> Owner
    on_reject:
        current none
        route "Fix." -> Owner
agent Owner:
    role: "Own it."
agent Child:
    role: "Review it."
    review: Concrete
    inputs: "Inputs"
        Draft
    outputs: "Outputs"
        Comment
""".replace("KIND", kind)
        self._assert_patches(source)
        with self.assertRaises(CompileError) as caught:
            self._render(
                source.replace("    PATCH", '    drop fields: "Not used."\n    inherit *')
            )
        self.assertEqual(caught.exception.code, "E473")
        self.assertIn("missing the required `fields:` block", str(caught.exception))

    def test_review(self):
        self._assert_review_patches("review")

    def test_review_family(self):
        self._assert_review_patches("review_family")

    def test_abstract_review(self):
        self._assert_review_patches("abstract review")

    def test_skills(self):
        self._assert_patches("""skill Shared: "Shared"
    purpose: "Work."
skills Base: "Base"
    skill a: Shared
        "Alpha"
    skill b: Shared
        "Bravo"
    skill c: Shared
        "Charlie"
skills Patched[Base]: "Patched"
    PATCH
agent Child:
    role: "Role."
    skills: Patched
""")

    def test_inputs(self):
        self._assert_patches("""input Draft: "Draft"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
inputs Base: "Base"
    a: "Alpha"
        Draft
    b: "Bravo"
        Draft
    c: "Charlie"
        Draft
inputs Patched[Base]: "Patched"
    PATCH
agent Child:
    role: "Role."
    inputs: Patched
""")

    def test_outputs(self):
        self._assert_patches("""output Comment: "Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required
outputs Base: "Base"
    a: "Alpha"
        Comment
    b: "Bravo"
        Comment
    c: "Charlie"
        Comment
outputs Patched[Base]: "Patched"
    PATCH
agent Child:
    role: "Role."
    outputs: Patched
""")

    def test_output(self):
        self._assert_patches("""output Base: "Base"
    target: TurnResponse
    shape: Comment
    requirement: Required
    a: "Alpha"
        "First."
    b: "Bravo"
        "Middle."
    c: "Charlie"
        "Last."
output Patched[Base]: "Patched"
    PATCH
agent Child:
    role: "Role."
    outputs: "Outputs"
        Patched
""")

    def test_output_shape(self):
        self._assert_patches(
            """output shape Base: "Base"
    kind: Comment
    a: "Alpha"
        "First."
    b: "Bravo"
        "Middle."
    c: "Charlie"
        "Last."
output shape Patched[Base]: "Patched"
    PATCH
output Comment: "Comment"
    target: TurnResponse
    shape: Patched
    requirement: Required
agent Child:
    role: "Role."
    outputs: "Outputs"
        Comment
    final_output: Comment
""",
            shape=True,
        )

    def test_output_schema(self):
        self._assert_patches("""output schema Base: "Base"
    field a: "Alpha"
        type: string
        note: "Alpha"
    field b: "Bravo"
        type: string
        note: "Bravo"
    field c: "Charlie"
        type: string
        note: "Charlie"
output schema Patched[Base]: "Patched"
    PATCH
output shape Shape: "Shape"
    kind: JsonObject
    schema: Patched
output Comment: "Comment"
    target: TurnResponse
    shape: Shape
    requirement: Required
agent Child:
    role: "Role."
    outputs: "Outputs"
        Comment
    final_output: Comment
""")

    def test_receipt(self):
        self._assert_patches(
            """receipt Base: "Base"
    a: string
    b: string
    c: string
receipt Patched[Base]: "Patched"
    PATCH
skill package Package: "Package"
    metadata:
        name: "package"
        description: "Work."
    host_contract:
        receipt result: Patched
    "Read the result."
""",
            package=True,
        )

    def _render(self, source, agent="Child", extra_files=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prompts" / "AGENTS.prompt"
            path.parent.mkdir()
            path.write_text(source)
            for name, contents in (extra_files or {}).items():
                extra_path = path.parent / name
                extra_path.parent.mkdir(parents=True, exist_ok=True)
                extra_path.write_text(contents)
            return render_markdown(CompilationSession(parse_file(path)).compile_agent(agent))

    def test_wildcard_keeps_override_in_parent_position(self):
        result = self._render("""abstract agent Base:
    role: "Base."
    a: "A"
        "First."
    b: "B"
        "Second."
agent Child[Base]:
    override b: "New B"
        "Replacement."
    inherit *
""")
        self.assertLess(result.index("## A"), result.index("## New B"))

    def test_explicit_inherit_moves_item_past_wildcard(self):
        result = self._render("""abstract agent Base:
    role: "Base."
    a: "A"
        "First."
    b: "B"
        "Second."
agent Child[Base]:
    inherit *
    inherit a
""")
        self.assertLess(result.index("## B"), result.index("## A"))

    def test_drop_requires_reason_parse_error(self):
        with self.assertRaises(ParseError) as caught:
            parse_text("agent A:\n    drop key\n")
        self.assertEqual(caught.exception.code, "E101")

    def test_disjoint_dotted_patches_are_legal(self):
        result = self._render("""abstract agent Base:
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
""")
        self.assertIn("### New A\n\nReplacement.", result)
        self.assertNotIn("Second.", result)

    def test_inherit_beside_dotted_patch_is_e612(self):
        unit = SimpleNamespace(prompt_file=SimpleNamespace(source_path=None))
        for items in (
            (model.InheritItem("a"), model.DropItem(("a", "b"), "Gone.")),
            (model.DropItem(("a", "b"), "Gone."), model.InheritItem("a")),
        ):
            with self.assertRaises(CompileError) as caught:
                expand_patch_items(
                    items, parent_keys=("a",), kind="workflow", owner_label="Child", unit=unit
                )
            self.assertEqual(caught.exception.code, "E612")

    def test_dotted_override_on_table_is_e611(self):
        with self.assertRaises(CompileError) as caught:
            self._render("""abstract agent Base:
    role: "Base."
    craft: "Craft"
        table checks: "Checks"
            columns:
                check: "Check"
agent Child[Base]:
    inherit role
    override craft.checks: "Checks"
        "Replacement."
""")
        self.assertEqual(caught.exception.code, "E611")
        self.assertIn("targets a `table`", str(caught.exception))

        with self.assertRaises(CompileError) as caught:
            self._render("""input Draft: "Draft"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
abstract agent Base:
    role: "Base."
    inputs: "Inputs"
        Draft
agent Child[Base]:
    inherit role
    override inputs.thing: "Thing"
        "Replacement."
""")
        self.assertEqual(caught.exception.code, "E611")
        self.assertIn("steps through `inputs`", str(caught.exception))

    def test_paragraph_override_rejects_section_body(self):
        with self.assertRaises(CompileError) as caught:
            self._render("""abstract agent Base:
    role: "Base."
    craft: "Craft"
        paragraph lead: "Lead."
            "First."
agent Child[Base]:
    inherit role
    override craft.lead: "Lead."
        nested: "Nested"
            "No."
""")
        self.assertEqual(caught.exception.code, "E611")
        self.assertIn("gives a paragraph a body it can't hold", str(caught.exception))

    def test_several_decisions_are_one_item(self):
        source = """decision First: "First Decision"
    "First choice."
decision Second: "Second Decision"
    "Second choice."
decision Third: "Third Decision"
    "Third choice."
abstract agent Base:
    role: "Role."
    decision: First
    work: "Work"
        "Work."
    decision: Second
agent Child[Base]:
    PATCH
"""
        keep = self._render(source.replace("    PATCH", "    inherit *\n    inherit decision"))
        self.assertLess(keep.index("## Work"), keep.index("## First Decision"))
        self.assertLess(keep.index("## First Decision"), keep.index("## Second Decision"))
        drop = self._render(
            source.replace("    PATCH", '    drop decision: "Not needed."\n    inherit *')
        )
        self.assertNotIn("Decision", drop)
        replace = self._render(source.replace("    PATCH", "    inherit *\n    decision: Third"))
        self.assertNotIn("First Decision", replace)
        self.assertNotIn("Second Decision", replace)
        self.assertLess(replace.index("## Work"), replace.index("## Third Decision"))

        several = self._render(
            source.replace(
                "    PATCH",
                "    inherit *\n    decision: Third\n    decision: First",
            )
        )
        self.assertLess(several.index("## Third Decision"), several.index("## First Decision"))
        self.assertLess(several.index("## Work"), several.index("## Third Decision"))
        self.assertNotIn("Second Decision", several)

    def test_inherited_role_refs_resolve_in_parent_module(self):
        source = """from parent import Base

document Doc: "Local Doc"
    "Local."
agent Child[Base]:
    inherit *
"""
        for role in ('role: "Read {{Doc:title}}."', 'role: "Role"\n        "Read {{Doc:title}}."'):
            with self.subTest(role=role):
                result = self._render(
                    source,
                    extra_files={
                        "parent/AGENTS.prompt": """document Doc: "Parent Doc"
    "Parent."
export abstract agent Base:
    ROLE
    work: "Work"
        "Read {{Doc:title}}."
""".replace("ROLE", role)
                    },
                )
                self.assertEqual(result.count("Read Parent Doc."), 2)
                self.assertNotIn("Local Doc", result)

    def test_inherit_preamble_needs_a_parent_preamble(self):
        for declaration, code in (
            ('workflow Work: "Work"', "E243"),
            ('workflow Work[Base]: "Work"', "E241"),
        ):
            with self.subTest(declaration=declaration), self.assertRaises(CompileError) as caught:
                self._render(
                    """workflow Base: "Base"
    a: "A"
        "Body."
DECLARATION
    inherit preamble
    inherit *
agent Child:
    role: "Role."
    work: Work
""".replace("DECLARATION", declaration).replace(
                        "    inherit *\n", "    inherit a\n" if "[Base]" in declaration else ""
                    )
                )
            self.assertEqual(caught.exception.code, code)
            self.assertIn("preamble", str(caught.exception))

    def test_schema_unknown_inherit_fails(self):
        with self.assertRaises(ParseError) as caught:
            parse_text("schema Child:\n    inherit nonsense\n")
        self.assertEqual(caught.exception.code, "E101")

    def test_drop_abstract_slot_is_e610(self):
        with self.assertRaises(CompileError) as caught:
            self._render("""abstract agent Base:
    role: "Role."
    abstract work
agent Child[Base]:
    drop work: "Not used."
    inherit *
""")
        self.assertEqual(caught.exception.code, "E610")
        self.assertEqual(
            caught.exception.diagnostic.detail,
            "`Child` patches `work`, but its parent has no such key.",
        )
        result = self._render("""abstract agent Base:
    role: "Role."
    abstract work
agent Child[Base]:
    inherit *
    work: "Work"
        "Fill the requirement."
""")
        self.assertIn("Fill the requirement.", result)

    def test_old_forms_keep_shipped_duplicate_errors(self):
        for source, code in (
            (
                """output Base: "Base"
    target: TurnResponse
    shape: Comment
    requirement: Required
    a: "A"
        "Body."
output Patched[Base]: "Patched"
    inherit a
    override a: "A"
        "New body."
    inherit target
    inherit shape
    inherit requirement
agent Child:
    role: "Role."
    outputs: "Outputs"
        Patched
""",
                "E255",
            ),
            (
                """abstract agent Base:
    role: "Role."
    work: "Work"
        "Body."
agent Child[Base]:
    inherit role
    inherit work
    override work: "Work"
        "New body."
""",
                "E299",
            ),
            (
                """review Base: "Base"
    a: "A"
        reject "No." when Draft.missing
review Patched[Base]: "Patched"
    inherit a
    override a: "A"
        reject "Still no." when Draft.missing
agent Child:
    role: "Role."
    review: Patched
""",
                "E491",
            ),
        ):
            with self.subTest(code=code), self.assertRaises(CompileError) as caught:
                self._render(source)
            self.assertEqual(caught.exception.code, code)
            self.assertEqual(len(caught.exception.diagnostic.related), 1)
            self.assertLess(
                caught.exception.diagnostic.related[0].location.line, caught.exception.location.line
            )

    def test_second_override_under_wildcard_keeps_shipped_error(self):
        for source, code in (
            ("""abstract agent Base:
    role: "Role."
    a: "A"
        "Original."
agent Child[Base]:
    override a: "First"
        "First."
    inherit *
    override a: "Second"
        "Second."
""", "E299"),
            ("""workflow Base: "Base"
    a: "A"
        "Original."
workflow Patched[Base]: "Patched"
    override a: "First"
        "First."
    inherit *
    override a: "Second"
        "Second."
agent Child:
    role: "Role."
    work: Patched
""", "E261"),
            ("""output Base: "Base"
    target: TurnResponse
    shape: Comment
    requirement: Required
    a: "A"
        "Original."
output Patched[Base]: "Patched"
    override a: "First"
        "First."
    inherit *
    override a: "Second"
        "Second."
agent Child:
    role: "Role."
    outputs: "Outputs"
        Patched
""", "E255"),
            ("""review Base: "Base"
    a: "A"
        reject "Original." when Draft.missing
review Patched[Base]: "Patched"
    override a: "First"
        reject "First." when Draft.missing
    inherit *
    override a: "Second"
        reject "Second." when Draft.missing
agent Child:
    role: "Role."
    review: Patched
""", "E491"),
        ):
            with self.subTest(code=code), self.assertRaises(CompileError) as caught:
                self._render(source)
            self.assertEqual(caught.exception.code, code)
            diagnostic = caught.exception.diagnostic
            self.assertEqual(diagnostic.related[0].location.line, source.splitlines().index(
                '    override a: "First"'
            ) + 1)
            self.assertEqual(diagnostic.location.line, source.splitlines().index(
                '    override a: "Second"'
            ) + 1)

    def test_inherit_star_with_nothing_is_e610(self):
        for source, owner in (
            ('agent Child:\n    role: "Role."\n    inherit *\n', "Child"),
            ('workflow W: "W"\n    inherit *\nagent Child:\n    role: "Role."\n    work: W\n', "W"),
            ("""abstract agent Base:
    role: "Role."
    a: "A"
        "Original."
agent Child[Base]:
    inherit role
    override a: "A"
        inherit *
""", "agent Child slot a"),
        ):
            with self.subTest(owner=owner), self.assertRaises(CompileError) as caught:
                self._render(source)
            self.assertEqual(caught.exception.code, "E610")
            self.assertEqual(caught.exception.diagnostic.detail,
                             f"`{owner}` writes `inherit *`, but it has nothing to inherit.")

    def test_dropped_slot_fails_requires_declare(self):
        with self.assertRaises(CompileError) as caught:
            self._render("""rule HasWork: "Has Work"
    scope:
        agent_tag: Child
    assertions:
        requires declare work
    message: "Keep the work slot."
abstract agent Base:
    role: "Role."
    work: "Work"
        "Work."
agent Child[Base]:
    inherit role
    drop work: "Unused."
""")
        self.assertEqual(caught.exception.code, "RULE005")

    def test_inherited_field_keeps_parent_imports(self):
        declaration = (
            'input Doc: "Parent Input"\n    source: Prompt\n'
            '    shape: MarkdownDocument\n    requirement: Required\n'
        )
        for imports, reference, files in (
            ("import shared as common\n", "common.Doc", {
                "shared/AGENTS.prompt": "export " + declaration,
            }),
            ("from shared import Doc as Selected\n", "Selected", {
                "shared/AGENTS.prompt": "export " + declaration,
            }),
            (declaration, "Doc", {}),
        ):
            with self.subTest(reference=reference):
                result = self._render("""from parent import Base
import other as common
agent Child[Base]:
    inherit *
""", extra_files={
                    **files,
                    "parent/AGENTS.prompt": (
                        imports + 'export abstract agent Base:\n    role: "Role."\n'
                        '    inputs: "Inputs"\n        ' + reference + "\n"
                    ),
                    "other/AGENTS.prompt": "export " + declaration.replace("Parent", "Wrong"),
                })
                self.assertIn("Parent Input", result)
                self.assertNotIn("Wrong Input", result)

    def test_inherited_final_output_reaches_previous_turn(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompts = root / "prompts"
            (prompts / "rally").mkdir(parents=True)
            (prompts / "rally" / "base_agent.prompt").write_text(
                """input source RallyPreviousTurnOutput: "Previous Turn"
    optional: "Optional Source Keys"
        output: "Output"
""")
            (prompts / "AGENTS.prompt").write_text("""output Result: "Result"
    target: TurnResponse
    shape: CommentText
    requirement: Required
outputs Results: "Results"
    reply: "Reply"
        Result
input Previous: "Previous"
    source: RallyPreviousTurnOutput
        output: Results:reply
    requirement: Advisory
abstract agent Base:
    role: "Send work."
    outputs: Results
    final_output: Result
agent WorkerA[Base]:
    inherit *
    workflow: "Work"
        law:
            current none
            active when true
            route "Continue." -> WorkerB
agent WorkerB:
    role: "Read the prior result."
    inputs: "Inputs"
        Previous
    outputs: Results
    final_output: Result
""")
            project = root / "pyproject.toml"
            project.write_text('''[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "demo"
entrypoint = "prompts/AGENTS.prompt"
output_dir = "build"
''')
            emit_target(load_emit_targets(project)["demo"])
            producer = json.loads((root / "build/worker_a/final_output.contract.json").read_text())
            self.assertTrue(producer["io"]["outputs"][0]["requires_final_output"])
            consumer = json.loads((root / "build/worker_b/final_output.contract.json").read_text())
            previous = consumer["io"]["previous_turn_inputs"][0]
            self.assertEqual(previous["binding_path"], ["reply"])
            self.assertEqual(previous["resolved_declaration_key"], "Result")

    def test_flow_keeps_inherited_role(self):
        for role in ('role: "Inherited role."', 'role: "Role"\n        "Inherited role."'):
            with self.subTest(role=role), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "prompts/AGENTS.prompt"
                path.parent.mkdir()
                path.write_text("""abstract agent Base:
    ROLE
agent Child[Base]:
    inherit *
agent Sender:
    role: "Send work."
    workflow: "Work"
        law:
            current none
            active when true
            route "Continue." -> Child
""".replace("ROLE", role))
                graph = CompilationSession(parse_file(path)).extract_target_flow_graph(
                    ("Sender", "Child")
                )
                child = next(node for node in graph.agents if node.name == "Child")
                self.assertIn("Inherited role.", "\n".join(child.detail_lines))

    def test_receipt_routes_are_inherited_items(self):
        source = """receipt Base: "Base"
    value: string
    route next_route: "Next Route"
        done: "Done." -> terminal
receipt Patched[Base]: "Patched"
    PATCH
skill package Package: "Package"
    metadata:
        name: "package"
        description: "Work."
    host_contract:
        receipt result: Patched
    "Read the result."
"""
        for patch, route_keys in (
            ("inherit value\n    inherit next_route", ("next_route",)),
            ("inherit *", ("next_route",)),
            ('drop next_route: "Unused."\n    inherit *', ()),
            ("inherit value", None),
        ):
            with self.subTest(patch=patch), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "prompts/SKILL.prompt"
                path.parent.mkdir()
                path.write_text(source.replace("PATCH", patch))
                session = CompilationSession(parse_file(path))
                if route_keys is None:
                    with self.assertRaises(CompileError) as caught:
                        session.compile_skill_package("Package")
                    self.assertEqual(caught.exception.code, "E544")
                    self.assertIn("next_route", str(caught.exception))
                else:
                    receipt = (
                        session.compile_skill_package("Package").contract.host_contract[0].receipt
                    )
                    self.assertEqual(tuple(route.key for route in receipt.routes), route_keys)
                    self.assertEqual(tuple(field.key for field in receipt.fields), ("value",))

    def test_dotted_override_needs_a_body(self):
        for declaration in ("agent Child:", 'workflow Child: "Child"'):
            for replacement in ("Other", '"Title"'):
                with self.subTest(declaration=declaration, replacement=replacement):
                    with self.assertRaises(ParseError):
                        parse_text(f"{declaration}\n    override craft.a: {replacement}\n")

    def test_paragraph_title_ref_inside_a_section(self):
        self.assertIn("Read the lead.", self._render("""workflow W: "W"
    a: "A"
        paragraph p: "the lead"
            "Body."
agent Child:
    role: "Read {{W:a.p.title}}."
    work: W
"""))
