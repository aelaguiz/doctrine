from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.emit_common import collect_runtime_emit_roots
from doctrine.emit_docs import _build_previous_turn_contexts
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class OutputRenderingTests(unittest.TestCase):
    def _compile_agent(
        self,
        source: str,
        *,
        agent_name: str,
        extra_files: dict[str, str] | None = None,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompts" / "AGENTS.prompt"
            prompt_path.parent.mkdir(parents=True)
            prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
            for rel_path, contents in (extra_files or {}).items():
                target_path = root / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(textwrap.dedent(contents), encoding="utf-8")
            prompt = parse_file(prompt_path)
            return CompilationSession(prompt).compile_agent(agent_name)

    def _compile_runtime_agent(
        self,
        source: str,
        *,
        agent_name: str,
        extra_files: dict[str, str] | None = None,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompts" / "AGENTS.prompt"
            prompt_path.parent.mkdir(parents=True)
            prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
            for rel_path, contents in (extra_files or {}).items():
                target_path = root / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(textwrap.dedent(contents), encoding="utf-8")
            prompt = parse_file(prompt_path)
            session = CompilationSession(prompt)
            runtime_roots = collect_runtime_emit_roots(session)
            agent_roots = tuple((root.unit, root.agent_name) for root in runtime_roots)
            previous_turn_contexts = _build_previous_turn_contexts(
                session,
                agent_roots=agent_roots,
            )
            target_root = next(
                root for root in runtime_roots if root.agent_name == agent_name
            )
            return session.compile_agent_from_unit(
                target_root.unit,
                agent_name,
                previous_turn_contexts=previous_turn_contexts,
            )

    def _render_agent_markdown(
        self,
        source: str,
        *,
        agent_name: str,
        extra_files: dict[str, str] | None = None,
    ) -> str:
        return render_markdown(
            self._compile_agent(
                source,
                agent_name=agent_name,
                extra_files=extra_files,
            )
        )

    def test_io_wrapper_shorthand_renders_like_titleless_long_form(self) -> None:
        long_form = self._render_agent_markdown(
            """
            input LessonsIssueLedger: "Lessons Issue Ledger"
                source: File
                    path: "catalog/lessons_issue_ledger.json"
                shape: "JSON Document"
                requirement: Required

            output SectionHandoff: "Section Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

            inputs SectionDossierInputs: "Your Inputs"
                issue_ledger:
                    LessonsIssueLedger

            outputs SectionDossierOutputs: "Your Outputs"
                section_handoff:
                    SectionHandoff

            agent Demo:
                role: "Keep IO wrappers concise."
                inputs: SectionDossierInputs
                outputs: SectionDossierOutputs
            """,
            agent_name="Demo",
        )
        shorthand = self._render_agent_markdown(
            """
            input LessonsIssueLedger: "Lessons Issue Ledger"
                source: File
                    path: "catalog/lessons_issue_ledger.json"
                shape: "JSON Document"
                requirement: Required

            output SectionHandoff: "Section Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

            inputs SectionDossierInputs: "Your Inputs"
                issue_ledger: LessonsIssueLedger

            outputs SectionDossierOutputs: "Your Outputs"
                section_handoff: SectionHandoff

            agent Demo:
                role: "Keep IO wrappers concise."
                inputs: SectionDossierInputs
                outputs: SectionDossierOutputs
            """,
            agent_name="Demo",
        )

        self.assertEqual(shorthand, long_form)

    def test_override_io_wrapper_shorthand_renders_like_long_form_override(self) -> None:
        long_form = self._render_agent_markdown(
            """
            input BaseReviewPacket: "Base Review Packet"
                source: File
                    path: "catalog/base_review_packet.json"
                shape: "JSON Document"
                requirement: Required

            input FreshReviewPacket: "Fresh Review Packet"
                source: File
                    path: "catalog/fresh_review_packet.json"
                shape: "JSON Document"
                requirement: Required

            output BaseReviewHandoff: "Base Review Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

            output FreshReviewHandoff: "Fresh Review Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

            inputs BaseInputs: "Your Inputs"
                review_packet: "Review Packet"
                    BaseReviewPacket

            outputs BaseOutputs: "Your Outputs"
                review_handoff: "Review Handoff"
                    BaseReviewHandoff

            inputs ChildInputs[BaseInputs]: "Your Inputs"
                override review_packet:
                    FreshReviewPacket

            outputs ChildOutputs[BaseOutputs]: "Your Outputs"
                override review_handoff:
                    FreshReviewHandoff

            agent Demo:
                role: "Keep inherited IO patches concise."
                inputs: ChildInputs
                outputs: ChildOutputs
            """,
            agent_name="Demo",
        )
        shorthand = self._render_agent_markdown(
            """
            input BaseReviewPacket: "Base Review Packet"
                source: File
                    path: "catalog/base_review_packet.json"
                shape: "JSON Document"
                requirement: Required

            input FreshReviewPacket: "Fresh Review Packet"
                source: File
                    path: "catalog/fresh_review_packet.json"
                shape: "JSON Document"
                requirement: Required

            output BaseReviewHandoff: "Base Review Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

            output FreshReviewHandoff: "Fresh Review Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

            inputs BaseInputs: "Your Inputs"
                review_packet: "Review Packet"
                    BaseReviewPacket

            outputs BaseOutputs: "Your Outputs"
                review_handoff: "Review Handoff"
                    BaseReviewHandoff

            inputs ChildInputs[BaseInputs]: "Your Inputs"
                override review_packet: FreshReviewPacket

            outputs ChildOutputs[BaseOutputs]: "Your Outputs"
                override review_handoff: FreshReviewHandoff

            agent Demo:
                role: "Keep inherited IO patches concise."
                inputs: ChildInputs
                outputs: ChildOutputs
            """,
            agent_name="Demo",
        )

        self.assertEqual(shorthand, long_form)

    def test_single_artifact_output_renders_grouped_contract_and_support_tables(self) -> None:
        agent = self._compile_agent(
            """
            output DemoOutput: "Demo Output"
                target: File
                    path: "section_root/PLAN.md"
                shape: MarkdownDocument
                requirement: Required

                must_include: "Must Include"
                    summary: "Summary"
                        "Start with a short summary."

                support_files: "Support Files"
                    audit: "AUDIT.md"
                        path: "section_root/AUDIT.md"
                        when: "Use when ordering matters."

                standalone_read: "Standalone Read"
                    "This output should stand on its own."

            agent Demo:
                role: "Ship the file."
                outputs: "Outputs"
                    DemoOutput
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("| Contract | Value |", rendered)
        self.assertIn("| Target | File |", rendered)
        self.assertIn("| Path | `section_root/PLAN.md` |", rendered)
        self.assertIn("| Shape | Markdown Document |", rendered)
        self.assertIn("| Requirement | Required |", rendered)
        self.assertIn("#### Must Include", rendered)
        self.assertIn("| **Summary** | Start with a short summary. |", rendered)
        self.assertIn("#### Support Files", rendered)
        self.assertIn(
            "| `AUDIT.md` | `section_root/AUDIT.md` | Use when ordering matters. |",
            rendered,
        )

    def test_file_set_output_renders_contract_and_artifacts_table(self) -> None:
        agent = self._compile_agent(
            """
            output LessonManifestOutput: "Lesson Manifest Output"
                files: "Files"
                    manifest: "Built Lesson"
                        path: "lesson_root/lesson_manifest.json"
                        shape: JsonObject

                    validation: "Validation File"
                        path: "lesson_root/MANIFEST_VALIDATION.md"
                        shape: MarkdownDocument

                requirement: Required

            agent Demo:
                role: "Ship the files."
                outputs: "Outputs"
                    LessonManifestOutput
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("| Target | File Set |", rendered)
        self.assertIn("| Requirement | Required |", rendered)
        self.assertIn("#### Artifacts", rendered)
        self.assertIn("| Artifact | Path | Shape |", rendered)
        self.assertIn(
            "| Built Lesson | `lesson_root/lesson_manifest.json` | Json Object |",
            rendered,
        )
        self.assertIn(
            "| Validation File | `lesson_root/MANIFEST_VALIDATION.md` | Markdown Document |",
            rendered,
        )

    def test_missing_local_output_shape_ref_fails_loud(self) -> None:
        with self.assertRaises(CompileError) as caught:
            self._compile_agent(
                """
                output DemoOutput: "Demo Output"
                    target: TurnResponse
                    shape: MissingShape
                    requirement: Required

                agent Demo:
                    role: "Ship the reply."
                    outputs: "Outputs"
                        DemoOutput
                """,
                agent_name="Demo",
            )

        self.assertEqual(caught.exception.code, "E276")
        self.assertIn("Missing local declaration reference", str(caught.exception))
        self.assertIn(
            "Output shape declaration `MissingShape` does not exist in the current module.",
            str(caught.exception),
        )

    def test_zero_config_previous_turn_input_fails_without_emit_time_flow_facts(self) -> None:
        with self.assertRaises(CompileError) as caught:
            self._compile_agent(
                """
                output schema SharedTurnSchema: "Shared Turn Schema"
                    field kind: "Kind"
                        type: string

                    example:
                        kind: "handoff"

                output shape SharedTurnJson: "Shared Turn JSON"
                    kind: JsonObject
                    schema: SharedTurnSchema

                output SharedTurnResult: "Shared Turn Result"
                    target: TurnResponse
                    shape: SharedTurnJson
                    requirement: Required

                input PreviousTurnResult: "Previous Turn Result"
                    source: RallyPreviousTurnOutput
                    requirement: Advisory

                agent Demo:
                    role: "Read the previous turn."
                    workflow: "Act"
                        "Read the previous turn."
                    inputs: "Inputs"
                        PreviousTurnResult
                    outputs: "Outputs"
                        SharedTurnResult
                    final_output: SharedTurnResult
                """,
                agent_name="Demo",
                extra_files={
                    "prompts/rally/base_agent.prompt": """
                    input source RallyPreviousTurnOutput: "Rally Previous Turn Output"
                        optional: "Optional Source Keys"
                            output: "Output"
                    """,
                },
            )

        self.assertIn(
            "needs flow-owned predecessor facts",
            str(caught.exception),
        )

    def test_explicit_structured_previous_turn_input_supports_field_paths(self) -> None:
        agent = self._compile_agent(
            """
            output schema SharedTurnSchema: "Shared Turn Schema"
                field kind: "Kind"
                    type: string

                example:
                    kind: "handoff"

            output shape SharedTurnJson: "Shared Turn JSON"
                kind: JsonObject
                schema: SharedTurnSchema

            output SharedTurnResult: "Shared Turn Result"
                target: TurnResponse
                shape: SharedTurnJson
                requirement: Required

            input PreviousTurnResult: "Previous Turn Result"
                source: RallyPreviousTurnOutput
                    output: SharedTurnResult
                requirement: Advisory

            agent Demo:
                role: "Read the previous turn."
                workflow: "Act"
                    law:
                        current none
                        active when PreviousTurnResult.kind == "handoff"
                inputs: "Inputs"
                    PreviousTurnResult
                outputs: "Outputs"
                    SharedTurnResult
                final_output: SharedTurnResult
            """,
            agent_name="Demo",
            extra_files={
                "prompts/rally/base_agent.prompt": """
                input source RallyPreviousTurnOutput: "Rally Previous Turn Output"
                    optional: "Optional Source Keys"
                        output: "Output"
                """,
            },
        )

        rendered = render_markdown(agent)
        self.assertIn("- Previous Output: SharedTurnResult", rendered)
        self.assertIn("- Derived Contract: Structured JSON", rendered)
        self.assertIn("- Derived Schema: Shared Turn Schema", rendered)

    def test_imported_previous_turn_output_binding_selector_renders_derived_contract(self) -> None:
        agent = self._compile_runtime_agent(
            """
            input PreviousRoutingHandoff: "Previous Routing Handoff"
                source: RallyPreviousTurnOutput
                    output: ProjectLeadOutputs:coordination_handoff
                requirement: Advisory

            agent WorkerB:
                role: "Read the previous turn."
                workflow: "Act"
                    law:
                        current none
                        active when PreviousRoutingHandoff.kind == "handoff"
                inputs: "Inputs"
                    PreviousRoutingHandoff
                outputs: ProjectLeadOutputs
                final_output: SharedTurnResult

            agent WorkerA:
                role: "Hand work to Worker B."
                workflow: "Route"
                    law:
                        current none
                        active when true
                        route "Send to Worker B." -> WorkerB
                outputs: ProjectLeadOutputs
                final_output: SharedTurnResult
            """,
            agent_name="WorkerB",
            extra_files={
                "prompts/rally/base_agent.prompt": """
                input source RallyPreviousTurnOutput: "Rally Previous Turn Output"
                    optional: "Optional Source Keys"
                        output: "Output"
                """,
                "prompts/shared/outputs.prompt": """
                output schema SharedTurnSchema: "Shared Turn Schema"
                    field kind: "Kind"
                        type: string

                    example:
                        kind: "handoff"

                output shape SharedTurnJson: "Shared Turn JSON"
                    kind: JsonObject
                    schema: SharedTurnSchema

                output SharedTurnResult: "Shared Turn Result"
                    target: TurnResponse
                    shape: SharedTurnJson
                    requirement: Required

                outputs ProjectLeadOutputs: "Project Lead Outputs"
                    coordination_handoff: "Coordination Handoff"
                        SharedTurnResult
                """,
            },
        )

        rendered = render_markdown(agent)
        self.assertIn(
            "- Previous Output: ProjectLeadOutputs:coordination_handoff",
            rendered,
        )
        self.assertIn("- Derived Contract: Structured JSON", rendered)
        self.assertIn("- Derived Schema: Shared Turn Schema", rendered)

    def test_readable_previous_turn_input_rejects_field_paths(self) -> None:
        with self.assertRaises(CompileError) as caught:
            self._compile_agent(
                """
                output ReadableReply: "Readable Reply"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                input PreviousReadableReply: "Previous Readable Reply"
                    source: RallyPreviousTurnOutput
                        output: ReadableReply
                    requirement: Advisory

                agent Demo:
                    role: "Read the previous turn."
                    workflow: "Act"
                        law:
                            current none
                            active when PreviousReadableReply.kind == "handoff"
                    inputs: "Inputs"
                        PreviousReadableReply
                    outputs: "Outputs"
                        ReadableReply
                    final_output: ReadableReply
                """,
                agent_name="Demo",
                extra_files={
                    "prompts/rally/base_agent.prompt": """
                    input source RallyPreviousTurnOutput: "Rally Previous Turn Output"
                        optional: "Optional Source Keys"
                            output: "Output"
                    """,
                },
            )

        self.assertIn(
            "active when reads invalid input source",
            str(caught.exception),
        )

    def test_current_truth_and_trust_surface_render_as_grouped_contract_sections(self) -> None:
        agent = self._compile_agent(
            """
            output CoordinationHandoff: "Coordination Handoff"
                target: TurnResponse
                shape: Comment
                requirement: Required

                current_truth: "Current Truth"
                    current_artifact: "Current Artifact"
                        "Name the current artifact that still stands."

                    invalidations: "Invalidations"
                        "Use [] when nothing was invalidated."

                trust_surface:
                    current_truth.current_artifact
                    current_truth.invalidations

                standalone_read: "Standalone Read"
                    "This handoff should stand on its own."

            agent Demo:
                role: "Ship the handoff."
                outputs: "Outputs"
                    CoordinationHandoff
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("#### Current Truth", rendered)
        self.assertIn(
            "| **Current Artifact** | Name the current artifact that still stands. |",
            rendered,
        )
        self.assertIn("| **Invalidations** | Use [] when nothing was invalidated. |", rendered)
        self.assertIn("#### Trust Surface", rendered)
        self.assertIn("- `Current Artifact`", rendered)
        self.assertIn("- `Invalidations`", rendered)

    def test_structure_and_parseable_notes_render_as_one_artifact_contract(self) -> None:
        agent = self._compile_agent(
            """
            document ReleaseGuide: "Release Guide"
                section summary: "Summary"
                    "Lead with the release goal."

                definitions must_include: "Must Include" required
                    verdict: "Verdict"
                        "Say whether the release is ready."

                table release_gates: "Release Gates" required
                    columns:
                        gate: "Gate"
                            "What must pass before shipment."

                        evidence: "Evidence"
                            "What proves the gate passed."

                    notes:
                        "List one row per release gate."

            output ReleaseGuideFile: "Release Guide File"
                target: File
                    path: "release_root/RELEASE_GUIDE.md"
                shape: MarkdownDocument
                structure: ReleaseGuide
                requirement: Required

                notes: "Notes"
                    "Use `CONCEPTS.md` only as scratch evidence while the map is being earned."

            agent Demo:
                role: "Ship the file."
                outputs: "Outputs"
                    ReleaseGuideFile
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("| Structure | Release Guide |", rendered)
        self.assertIn("#### Artifact Structure", rendered)
        self.assertIn("| **Summary** | Section | Lead with the release goal. |", rendered)
        self.assertIn("| **Must Include** | Definitions | Define `Verdict`. |", rendered)
        self.assertIn(
            "| **Release Gates** | Table | List one row per release gate. |",
            rendered,
        )
        self.assertIn("##### Must Include Definitions", rendered)
        self.assertIn("##### Release Gates Contract", rendered)
        self.assertIn("#### Notes", rendered)
        self.assertIn(
            "| `CONCEPTS.md` | Use only as scratch evidence while the map is being earned. |",
            rendered,
        )

    def test_schema_attached_output_keeps_schema_row_and_detail_section(self) -> None:
        agent = self._compile_agent(
            """
            schema DeliveryInventory: "Delivery Inventory"
                sections:
                    summary: "Summary"
                        "Include a short summary."

                    artifacts: "Artifacts"
                        "List the produced artifacts."

            output DeliveryPlan: "Delivery Plan"
                target: File
                    path: "unit_root/DELIVERY_PLAN.md"
                shape: MarkdownDocument
                requirement: Required
                schema: DeliveryInventory

            agent Demo:
                role: "Ship the plan."
                outputs: "Outputs"
                    DeliveryPlan
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("| Schema | Delivery Inventory |", rendered)
        self.assertIn("#### Required Sections", rendered)
        self.assertIn("##### Summary", rendered)
        self.assertIn("##### Artifacts", rendered)

    def test_readable_definitions_must_include_stays_on_generic_readable_path(self) -> None:
        agent = self._compile_agent(
            """
            output ReleaseComment: "Release Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required

                definitions must_include: "Must Include" required
                    summary: "Summary"
                        "Summarize the release outcome."

                    next_owner: "Next Owner"
                        "Name who owns the next action."

            agent Demo:
                role: "Ship the comment."
                outputs: "Outputs"
                    ReleaseComment
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("#### Must Include", rendered)
        self.assertIn("_Required · definitions_", rendered)
        self.assertIn("- **Summary** — Summarize the release outcome.", rendered)
        self.assertIn("- **Next Owner** — Name who owns the next action.", rendered)

    def test_titled_properties_blocks_render_as_contract_tables(self) -> None:
        agent = self._compile_agent(
            """
            output ReleaseComment: "Release Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required

                properties current_truth: "Current Truth"
                    current_artifact: "Current Artifact"
                        "Set this to home:issue.md."

                    invalidations: "Invalidations"
                        "Use [] when nothing was invalidated."

            agent Demo:
                role: "Ship the comment."
                outputs: "Outputs"
                    ReleaseComment
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("#### Current Truth", rendered)
        self.assertIn("| **Current Artifact** | Set this to home:issue.md. |", rendered)
        self.assertIn("| **Invalidations** | Use [] when nothing was invalidated. |", rendered)

    def test_titled_properties_blocks_keep_duplicate_key_validation(self) -> None:
        source = """
        output ReviewComment: "Review Comment"
            target: TurnResponse
            shape: Comment
            requirement: Required

            properties summary: "Summary"
                verdict: "Verdict"
                    "Use changes requested when the contract fails."

                verdict: "Verdict Again"
                    "This should fail."

        agent Demo:
            role: "Compile the broken review comment."
            outputs: "Outputs"
                ReviewComment
        """

        with self.assertRaises(Exception) as caught:
            self._compile_agent(source, agent_name="Demo")

        self.assertEqual(type(caught.exception).__name__, "CompileError")
        self.assertEqual(getattr(caught.exception, "code", None), "E295")
        self.assertIn("properties entry key `verdict`", str(caught.exception))
        self.assertIn("verdict", str(caught.exception))

    def test_titled_lists_drop_kind_metadata_and_keep_meaningful_metadata(self) -> None:
        agent = self._compile_agent(
            """
            agent Demo:
                role: "Review the release."
                workflow: "Guide"
                    titled_lists: "Titled Lists"
                        sequence read_order: "Read Order" advisory
                            "Read the issue."
                            "Read the repo status."

                        bullets evidence: "Evidence"
                            current_status: "Read the current status."
                            latest_notes: "Read the latest validation notes."

                        checklist checks: "Checks" required
                            lint: "Run lint."
                            tests: "Run tests."
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("#### Read Order", rendered)
        self.assertIn("_Advisory_", rendered)
        self.assertNotIn("ordered list", rendered)
        self.assertIn("1. Read the issue.", rendered)
        self.assertIn("2. Read the repo status.", rendered)
        self.assertIn("#### Evidence", rendered)
        self.assertNotIn("unordered list", rendered)
        self.assertIn("- Read the current status.", rendered)
        self.assertIn("- Read the latest validation notes.", rendered)
        self.assertIn("#### Checks", rendered)
        self.assertIn("_Required_", rendered)
        self.assertNotIn("· checklist", rendered)
        self.assertIn("- [ ] Run lint.", rendered)
        self.assertIn("- [ ] Run tests.", rendered)

    def test_titleless_lists_render_directly_inside_parent_sections(self) -> None:
        agent = self._compile_agent(
            """
            agent Demo:
                role: "Follow the guide."
                workflow: "Guide"
                    read_first: "Read First"
                        sequence steps:
                            "Read `home:issue.md` first."
                            "Then read this role's local rules, files, and outputs."
                            "Check `rally-memory` only when past work like this could help."

                    shared_rules: "Shared Rules"
                        bullets rules:
                            "Use `home:issue.md` as the shared ledger for this run."
                            "Leave one short saved note only when later readers need it."
                            "Keep notes run-local. Use `rally-memory` for cross-run lessons."

                    done_before_handoff: "Done Before Handoff"
                        checklist checks:
                            "Confirm the current artifact."
                            "Confirm the next owner."
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn(
            "### Read First\n\n"
            "1. Read `home:issue.md` first.\n"
            "2. Then read this role's local rules, files, and outputs.\n"
            "3. Check `rally-memory` only when past work like this could help.",
            rendered,
        )
        self.assertIn(
            "### Shared Rules\n\n"
            "- Use `home:issue.md` as the shared ledger for this run.\n"
            "- Leave one short saved note only when later readers need it.\n"
            "- Keep notes run-local. Use `rally-memory` for cross-run lessons.",
            rendered,
        )
        self.assertIn(
            "### Done Before Handoff\n\n"
            "- [ ] Confirm the current artifact.\n"
            "- [ ] Confirm the next owner.",
            rendered,
        )
        self.assertNotIn("#### Steps", rendered)
        self.assertNotIn("#### Rules", rendered)
        self.assertNotIn("#### Checks", rendered)
        self.assertNotIn("ordered list", rendered)
        self.assertNotIn("unordered list", rendered)
        self.assertNotIn("checklist", rendered)

    def test_titleless_list_overrides_compile_through_document_inheritance(self) -> None:
        agent = self._compile_agent(
            """
            document BaseGuide: "Base Guide"
                sequence read_order: "Read Order"
                    "Read the brief."

            document ChildGuide[BaseGuide]: "Child Guide"
                override sequence read_order:
                    "Read the learner goal."
                    "Read the current lesson plan."

            output ChildGuideFile: "Child Guide File"
                target: File
                    path: "guide_root/CHILD_GUIDE.md"
                shape: MarkdownDocument
                structure: ChildGuide
                requirement: Required

            agent Demo:
                role: "Write the guide."
                outputs: "Outputs"
                    ChildGuideFile
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("| **Read Order** | Ordered List | Read the learner goal. Read the current lesson plan. |", rendered)
        self.assertIn("1. Read the learner goal.", rendered)
        self.assertIn("2. Read the current lesson plan.", rendered)
        self.assertNotIn("##### Read Order", rendered)
        self.assertNotIn("ordered list", rendered)

    def test_workflow_root_readable_blocks_render_and_stay_addressable(self) -> None:
        agent = self._compile_agent(
            """
            workflow ReleaseGuide: "Release Guide"
                sequence read_first:
                    "Read `home:issue.md` first."
                    "Then read the role rules."

                bullets shared_rules:
                    "Use `home:issue.md` as the shared ledger."
                    "End with the final JSON."

                callout evidence_note: "Evidence Note"
                    kind: note
                    "Ground the current claim before you summarize."

                definitions done_when: "Done When"
                    summary: "Summary"
                        "State the release result."

            agent Demo:
                role: "Use {{ReleaseGuide:evidence_note.title}} and {{ReleaseGuide:done_when.summary.title}}."
                workflow: ReleaseGuide
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("Use Evidence Note and Summary.", rendered)
        self.assertIn(
            "## Release Guide\n\n"
            "1. Read `home:issue.md` first.\n"
            "2. Then read the role rules.",
            rendered,
        )
        self.assertIn(
            "- Use `home:issue.md` as the shared ledger.\n"
            "- End with the final JSON.",
            rendered,
        )
        self.assertNotIn("### Read First", rendered)
        self.assertNotIn("### Shared Rules", rendered)
        self.assertIn("> **NOTE \u2014 Evidence Note**", rendered)
        self.assertIn("### Done When", rendered)
        self.assertIn("- **Summary** \u2014 State the release result.", rendered)

    def test_custom_authored_slot_workflow_root_readable_blocks_render(self) -> None:
        # Custom authored slots use the same legal workflow body shape as the built-in
        # `workflow` slot. Root readable blocks must render, not trip an internal
        # compiler guard because the slot compile path lost its owner context.
        agent = self._compile_agent(
            """
            workflow ReleaseGuide: "Release Guide"
                sequence read_first:
                    "Read `home:issue.md` first."
                    "Then read the role rules."

                callout evidence_note: "Evidence Note"
                    kind: note
                    "Ground the claim before you summarize."

            agent Demo:
                role: "Follow the guide."
                read_first: ReleaseGuide
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn(
            "## Release Guide\n\n"
            "1. Read `home:issue.md` first.\n"
            "2. Then read the role rules.",
            rendered,
        )
        self.assertNotIn("### Read First", rendered)
        self.assertIn("> **NOTE \u2014 Evidence Note**", rendered)

    def test_workflow_root_readable_overrides_keep_non_list_titles_and_drop_list_titles(self) -> None:
        agent = self._compile_agent(
            """
            workflow BaseGuide: "Guide"
                sequence read_first: "Read First"
                    "Read the brief."

                definitions done_when: "Done When"
                    summary: "Summary"
                        "State the base result."

            workflow ChildGuide[BaseGuide]: "Guide"
                override sequence read_first:
                    "Read the learner goal."
                    "Read the current lesson plan."

                override definitions done_when:
                    summary: "Summary"
                        "State the child result."

            agent Demo:
                role: "Use {{ChildGuide:done_when.title}}."
                workflow: ChildGuide
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("Use Done When.", rendered)
        self.assertIn("1. Read the learner goal.", rendered)
        self.assertIn("2. Read the current lesson plan.", rendered)
        self.assertNotIn("### Read First", rendered)
        self.assertIn("### Done When", rendered)
        self.assertIn("- **Summary** \u2014 State the child result.", rendered)
