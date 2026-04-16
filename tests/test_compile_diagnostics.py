from __future__ import annotations

from dataclasses import replace
import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine import model
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.resolved_types import AddressableNode
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file


class CompileDiagnosticTests(unittest.TestCase):
    def _write_prompt(
        self,
        root: Path,
        source: str,
        *,
        rel_path: str = "prompts/AGENTS.prompt",
    ) -> Path:
        prompt_path = root / rel_path
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
        return prompt_path

    def test_missing_import_points_at_import_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                import shared.missing

                agent Demo:
                    role: "Own the reply."
                    workflow: "Reply"
                        "Answer directly."
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E280")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 1)
        self.assertEqual(error.diagnostic.location.column, 1)
        self.assertIn("import shared.missing", str(error))
        self.assertIn("Create the missing prompt file, or fix the import path.", str(error))

    def test_duplicate_declaration_name_reports_related_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                table ReleaseGates: "Release Gates"
                    columns:
                        gate: "Gate"

                table ReleaseGates: "Release Gates Again"
                    columns:
                        proof: "Proof"
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E288")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 5)
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, 1)
        self.assertIn("Related:", str(error))
        self.assertIn("first declaration", str(error))

    def test_duplicate_agent_typed_field_reports_related_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                decision PlayableStrategyChoice: "Playable Strategy Choice"
                    candidates minimum 3
                    rank required
                    rejects required
                    winner required
                    rank_by {teaching_fit, product_reality, capstone_coherence, downstream_preservability}

                agent Demo:
                    role: "Own the reply."
                    workflow: "Reply"
                        "Answer directly."
                    decision: PlayableStrategyChoice
                    decision: PlayableStrategyChoice
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E204")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 13)
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, 12)
        self.assertIn(
            "Agent `Demo` defines typed field `decision:PlayableStrategyChoice` more than once.",
            str(error),
        )
        self.assertIn("first `decision:PlayableStrategyChoice` field", str(error))

    def test_invalid_project_toml_points_at_the_toml_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pyproject_path = root / "pyproject.toml"
            pyproject_path.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.compile]
                    additional_prompt_roots = ["shared/prompts"
                    """
                ),
                encoding="utf-8",
            )
            prompt_path = self._write_prompt(
                root,
                """\
                agent Demo:
                    role: "Own the reply."
                    workflow: "Reply"
                        "Answer directly."
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, pyproject_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 3)
        self.assertIsNotNone(error.diagnostic.location.column)
        self.assertIn('additional_prompt_roots = ["shared/prompts"', str(error))

    def test_invalid_project_config_points_at_the_config_item(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pyproject_path = root / "pyproject.toml"
            pyproject_path.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.compile]
                    additional_prompt_roots = ["shared/not_prompts"]
                    """
                ),
                encoding="utf-8",
            )
            prompt_path = self._write_prompt(
                root,
                """\
                agent Demo:
                    role: "Own the reply."
                    workflow: "Reply"
                        "Answer directly."
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E285")
        self.assertEqual(error.diagnostic.location.path, pyproject_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 2)
        self.assertIsNotNone(error.diagnostic.location.column)
        self.assertIn('additional_prompt_roots = ["shared/not_prompts"]', str(error))

    def test_duplicate_route_from_arm_reports_related_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                enum ProofRoute: "Proof Route"
                    accept: "Accept"
                    change: "Change"
                input RouteFacts: "Route Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required
                    route_choice: "Route Choice"
                agent AcceptanceCritic:
                    role: "Accept routed work."
                agent BackupCritic:
                    role: "Backup routed work."
                agent ChangeEngineer:
                    role: "Handle requested changes."
                workflow DuplicateRouteFromWorkflow: "Duplicate Route From Workflow"
                    law:
                        current none
                        route_from RouteFacts.route_choice as ProofRoute:
                            ProofRoute.accept:
                                route "Send to AcceptanceCritic." -> AcceptanceCritic
                            ProofRoute.accept:
                                route "Send to BackupCritic." -> BackupCritic
                            ProofRoute.change:
                                route "Send to ChangeEngineer." -> ChangeEngineer
                agent Demo:
                    role: "Reject duplicate route_from choices."
                    inputs: "Inputs"
                        RouteFacts
                    workflow: DuplicateRouteFromWorkflow
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E348")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 21)
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, 19)
        self.assertIn("first `Accept` arm", str(error))
        self.assertIn("Related:", str(error))

    def test_route_from_selector_invalid_source_points_at_selector_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                enum ProofRoute: "Proof Route"
                    accept: "Accept"
                    change: "Change"
                input RouteFacts: "Route Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required
                    route_choice: "Route Choice"
                agent AcceptanceCritic:
                    role: "Accept routed work."
                agent ChangeEngineer:
                    role: "Handle requested changes."
                workflow InvalidComputedRouteFromWorkflow: "Invalid Computed Route From Workflow"
                    law:
                        current none
                        route_from RouteFacts.route_choice == ProofRoute.accept as ProofRoute:
                            ProofRoute.accept:
                                route "Send to AcceptanceCritic." -> AcceptanceCritic
                            ProofRoute.change:
                                route "Send to ChangeEngineer." -> ChangeEngineer
                agent Demo:
                    role: "Keep route_from selectors direct."
                    inputs: "Inputs"
                        RouteFacts
                    workflow: InvalidComputedRouteFromWorkflow
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E346")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 16)
        self.assertIn("route_from RouteFacts.route_choice == ProofRoute.accept as ProofRoute:", str(error))

    def test_route_target_abstract_agent_points_at_route_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                abstract agent ReviewLead:
                    role: "Accept routed work."

                agent Demo:
                    role: "Reject abstract route targets."
                    workflow: "Route"
                        law:
                            current none
                            route "Hand off to ReviewLead." -> ReviewLead
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E282")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 9)
        self.assertIn('route "Hand off to ReviewLead." -> ReviewLead', str(error))

    def test_active_when_invalid_source_points_at_active_when_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                workflow InvalidActiveWhenWorkflow: "Invalid Active When Workflow"
                    law:
                        current none
                        active when MissingInput.ready

                agent Demo:
                    role: "Reject invalid active when reads."
                    workflow: InvalidActiveWhenWorkflow
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 4)
        self.assertIn("active when reads invalid input source", str(error))

    def test_mode_value_outside_enum_points_at_mode_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                enum EditMode: "Edit Mode"
                    manifest_title: "manifest-title"
                    section_summary: "section-summary"

                workflow InvalidModeAwareEdit: "Mode-Aware Edit"
                    law:
                        mode edit_mode = "taxonomy" as EditMode
                        current none

                agent Demo:
                    role: "Reject invalid mode values."
                    workflow: InvalidModeAwareEdit
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E341")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 7)
        self.assertIn('mode edit_mode = "taxonomy" as EditMode', str(error))

    def test_nonexhaustive_mode_match_points_at_match_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                enum EditMode: "Edit Mode"
                    manifest_title: "manifest-title"
                    section_summary: "section-summary"

                input CurrentHandoff: "Current Handoff"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow InvalidModeAwareEdit: "Mode-Aware Edit"
                    law:
                        mode edit_mode = CurrentHandoff.active_mode as EditMode
                        match edit_mode:
                            EditMode.manifest_title:
                                current none

                agent Demo:
                    role: "Reject nonexhaustive mode matches."
                    workflow: InvalidModeAwareEdit
                    inputs: "Inputs"
                        CurrentHandoff
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E342")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 13)
        self.assertIn("match edit_mode:", str(error))

    def test_handoff_routing_nonrouting_statement_points_at_statement_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                output SimpleReply: "Simple Reply"
                    target: TurnResponse
                    shape: CommentText
                    requirement: Required

                agent Demo:
                    role: "Keep handoff routing limited to route semantics."
                    outputs: "Outputs"
                        SimpleReply

                    handoff_routing: "Handoff Routing"
                        law:
                            current none
                            stop "Reply and stop."
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E344")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 13)
        self.assertIn("unsupported statement `current none`", str(error))

    def test_multiple_current_subjects_report_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input CurrentHandoff: "Current Handoff"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                output CoordinationComment: "Coordination Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    current_artifact: "Current Artifact"
                        "Name the current artifact."
                    trust_surface:
                        current_artifact

                workflow InvalidRouteOnlyTurns: "Route-Only Triage"
                    law:
                        when CurrentHandoff.missing:
                            current none
                            current artifact CoordinationComment via CoordinationComment.current_artifact

                agent Demo:
                    role: "Trigger conflicting currentness."
                    workflow: InvalidRouteOnlyTurns
                    inputs: "Inputs"
                        CurrentHandoff
                    outputs: "Outputs"
                        CoordinationComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E332")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                "            current artifact CoordinationComment via CoordinationComment.current_artifact"
            )
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("            current none") + 1,
        )
        self.assertIn("first current-subject form", str(error))

    def test_current_none_with_owned_scope_points_at_owned_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input ApprovedPlan: "Approved Plan"
                    source: File
                        path: "unit_root/_authoring/APPROVED_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required

                workflow InvalidOwnedRouteOnlyTurn: "Invalid Owned Route-Only Turn"
                    law:
                        current none
                        own only ApprovedPlan

                agent Demo:
                    role: "Reject owned scope on route-only turns."
                    workflow: InvalidOwnedRouteOnlyTurn
                    inputs: "Inputs"
                        ApprovedPlan
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        own only ApprovedPlan") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("        current none") + 1,
        )
        self.assertIn("`current none` statement", str(error))

    def test_current_artifact_invalidation_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output SectionReview: "Section Review"
                    target: File
                        path: "unit_root/_authoring/SECTION_REVIEW.md"
                    shape: MarkdownDocument
                    requirement: Required

                output CoordinationHandoff: "Coordination Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    current_artifact: "Current Artifact"
                        "Name the one artifact that is current now."
                    invalidations: "Invalidations"
                        "Name any artifacts that are no longer current."
                    trust_surface:
                        current_artifact
                        invalidations

                workflow InvalidStructureChange: "Structure Change"
                    law:
                        current artifact SectionReview via CoordinationHandoff.current_artifact
                        invalidate SectionReview via CoordinationHandoff.invalidations

                agent Demo:
                    role: "Reject invalidating the current artifact."
                    workflow: InvalidStructureChange
                    outputs: "Outputs"
                        SectionReview
                        CoordinationHandoff
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E371")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                "        invalidate SectionReview via CoordinationHandoff.invalidations"
            )
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index(
                "        current artifact SectionReview via CoordinationHandoff.current_artifact"
            )
            + 1,
        )
        self.assertIn("current artifact statement", str(error))

    def test_current_artifact_wrong_kind_points_at_current_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                enum MetadataPolishMode: "Metadata Polish Mode"
                    manifest_title: "manifest-title"
                    section_summary: "section-summary"
                output CoordinationHandoff: "Coordination Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    current_artifact: "Current Artifact"
                        "Name the one artifact that is current now."
                    trust_surface:
                        current_artifact
                workflow InvalidCarryCurrentTruth: "Carry Current Truth"
                    law:
                        current artifact MetadataPolishMode via CoordinationHandoff.current_artifact
                agent Demo:
                    role: "Trigger a wrong-kind current target."
                    workflow: InvalidCarryCurrentTruth
                    outputs: "Outputs"
                        CoordinationHandoff
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E335")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 14)
        self.assertIn("current artifact MetadataPolishMode via CoordinationHandoff.current_artifact", str(error))

    def test_review_comment_output_not_emitted_points_at_comment_output_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow DraftReviewContract: "Draft Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent ReviewLead:
                    role: "Own accepted draft follow-up."

                agent DraftAuthor:
                    role: "Fix rejected draft defects."

                output DraftReviewComment: "Draft Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "Say whether the review accepted the draft or asked for changes."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."
                    analysis_performed: "Analysis Performed"
                        "Sum up the review work."
                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize the parts that matter."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "Name the failing review gates."

                review DraftReview: "Draft Review"
                    subject: DraftSpec
                    contract: DraftReviewContract
                    comment_output: DraftReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    checks: "Checks"
                        accept "The shared draft review contract passes." when contract.passes

                    on_accept:
                        current none
                        route "Accepted draft goes to ReviewLead." -> ReviewLead

                    on_reject:
                        current none
                        route "Rejected draft goes to DraftAuthor." -> DraftAuthor

                agent Demo:
                    role: "Trigger missing review output emission."
                    review: DraftReview
                    inputs: "Inputs"
                        DraftSpec
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E479")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    comment_output: DraftReviewComment") + 1,
        )
        self.assertIn("comment_output: DraftReviewComment", str(error))

    def test_review_multiple_accept_gates_report_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow DraftReviewContract: "Draft Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent ReviewLead:
                    role: "Own accepted draft follow-up."

                agent DraftAuthor:
                    role: "Fix rejected draft defects."

                output DraftReviewComment: "Draft Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "Say whether the review accepted the draft or asked for changes."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."
                    analysis_performed: "Analysis Performed"
                        "Sum up the review work."
                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize the parts that matter."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "Name the failing review gates."

                review DraftReview: "Draft Review"
                    subject: DraftSpec
                    contract: DraftReviewContract
                    comment_output: DraftReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    checks: "Checks"
                        accept "First gate passes." when contract.passes
                        accept "Second gate passes." when contract.passes

                    on_accept:
                        current none
                        route "Accepted draft goes to ReviewLead." -> ReviewLead

                    on_reject:
                        current none
                        route "Rejected draft goes to DraftAuthor." -> DraftAuthor

                agent Demo:
                    role: "Reject duplicate accept gates."
                    review: DraftReview
                    inputs: "Inputs"
                        DraftSpec
                    outputs: "Outputs"
                        DraftReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E482")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        accept "Second gate passes." when contract.passes')
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('        accept "First gate passes." when contract.passes')
            + 1,
        )
        self.assertIn("first `accept` gate", str(error))
        self.assertIn("Related:", str(error))

    def test_case_selected_review_overlap_reports_related_case_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                enum ReviewMode: "Review Mode"
                    draft_rewrite: "draft-rewrite"
                    metadata_refresh: "metadata-refresh"

                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                input MetadataRecord: "Metadata Record"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                input ReviewFacts: "Review Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow DraftReviewContract: "Draft Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                workflow MetadataReviewContract: "Metadata Review Contract"
                    freshness: "Freshness"
                        "Confirm the metadata stays current."

                agent RevisionOwner:
                    role: "Own the next revision pass after review."

                output SelectedReviewComment: "Selected Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "Say whether the review accepted the selected subject or asked for changes."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."
                    analysis_performed: "Analysis Performed"
                        "Sum up the review work that led to the verdict."
                    output_contents_that_matter: "Output Contents That Matter"
                        "Sum up the parts of the selected subject the next owner should read first."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    current_artifact: "Current Artifact"
                        "Name the artifact that is current now."
                    trust_surface:
                        current_artifact

                review_family SelectedReviewFamily: "Selected Review"
                    comment_output: SelectedReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        next_owner: next_owner
                        current_artifact: current_artifact

                    selector:
                        mode selected_mode = ReviewFacts.selected_mode as ReviewMode

                    cases:
                        draft_path: "Draft Path"
                            when ReviewMode.draft_rewrite
                            subject: DraftSpec
                            contract: DraftReviewContract
                            checks:
                                accept "The draft review contract passes." when contract.passes
                            on_accept:
                                current artifact DraftSpec via SelectedReviewComment.current_artifact
                                route "Accepted draft rewrite goes to RevisionOwner." -> RevisionOwner
                            on_reject:
                                current artifact DraftSpec via SelectedReviewComment.current_artifact
                                route "Rejected draft rewrite goes to RevisionOwner." -> RevisionOwner

                        duplicate_draft_path: "Duplicate Draft Path"
                            when ReviewMode.draft_rewrite
                            subject: MetadataRecord
                            contract: MetadataReviewContract
                            checks:
                                accept "The metadata review contract passes." when contract.passes
                            on_accept:
                                current artifact MetadataRecord via SelectedReviewComment.current_artifact
                                route "Accepted metadata refresh goes to RevisionOwner." -> RevisionOwner
                            on_reject:
                                current artifact MetadataRecord via SelectedReviewComment.current_artifact
                                route "Rejected metadata refresh goes to RevisionOwner." -> RevisionOwner

                agent Demo:
                    role: "Reject overlapping review cases."
                    review: SelectedReviewFamily
                    inputs: "Inputs"
                        DraftSpec
                        MetadataRecord
                        ReviewFacts
                    outputs: "Outputs"
                        SelectedReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)
            match_lines = [
                line_number
                for line_number, line in enumerate(rendered.splitlines(), start=1)
                if line == "            when ReviewMode.draft_rewrite"
            ]

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E470")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, match_lines[1])
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, match_lines[0])
        self.assertIn("first case for `draft-rewrite`", str(error))
        self.assertIn("Related:", str(error))

    def test_missing_inherited_review_entry_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow PatchedDraftReviewContract: "Patched Draft Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent ReviewLead:
                    role: "Own accepted draft follow-up."

                agent DraftAuthor:
                    role: "Repair rejected draft defects."

                output InheritedReviewComment: "Inherited Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "Say whether the review accepted the draft or asked for changes."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."
                    analysis_performed: "Analysis Performed"
                        "Sum up the review work that led to the verdict."
                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize the parts of the draft the next owner must read first."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "Name the failing review gates in authored order."

                abstract review BaseDraftReview: "Base Draft Review"
                    comment_output: InheritedReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    shared_checks: "Shared Checks"
                        reject "The draft still lacks the shared context." when DraftSpec.context_missing

                review PatchedDraftReview[BaseDraftReview]: "Patched Draft Review"
                    subject: DraftSpec
                    contract: PatchedDraftReviewContract
                    inherit fields

                    child_specifics: "Child Specifics"
                        accept "The patched draft review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current none
                        route "Accepted draft goes to ReviewLead." -> ReviewLead

                    on_reject: "If Rejected"
                        current none
                        route "Rejected draft goes to DraftAuthor." -> DraftAuthor

                agent Demo:
                    role: "Keep missing inherited review sections from compiling."
                    review: PatchedDraftReview
                    inputs: "Inputs"
                        DraftSpec
                    outputs: "Outputs"
                        InheritedReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E490")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('review PatchedDraftReview[BaseDraftReview]: "Patched Draft Review"')
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    shared_checks: "Shared Checks"') + 1,
        )
        self.assertIn("Missing inherited review entry", str(error))
        self.assertIn("Related:", str(error))

    def test_duplicate_review_item_key_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow PatchedDraftReviewContract: "Patched Draft Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent ReviewLead:
                    role: "Own accepted draft follow-up."

                agent DraftAuthor:
                    role: "Repair rejected draft defects."

                output InheritedReviewComment: "Inherited Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "Say whether the review accepted the draft or asked for changes."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."
                    analysis_performed: "Analysis Performed"
                        "Sum up the review work that led to the verdict."
                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize the parts of the draft the next owner must read first."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "Name the failing review gates in authored order."

                abstract review BaseDraftReview: "Base Draft Review"
                    comment_output: InheritedReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    shared_checks: "Shared Checks"
                        reject "The draft still lacks the shared context." when DraftSpec.context_missing

                review PatchedDraftReview[BaseDraftReview]: "Patched Draft Review"
                    subject: DraftSpec
                    contract: PatchedDraftReviewContract
                    inherit fields
                    inherit shared_checks
                    override shared_checks:
                        reject "The draft still lacks the shared context." when DraftSpec.context_missing

                    child_specifics: "Child Specifics"
                        accept "The patched draft review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current none
                        route "Accepted draft goes to ReviewLead." -> ReviewLead

                    on_reject: "If Rejected"
                        current none
                        route "Rejected draft goes to DraftAuthor." -> DraftAuthor

                agent Demo:
                    role: "Keep duplicate inherited review section accounting from compiling."
                    review: PatchedDraftReview
                    inputs: "Inputs"
                        DraftSpec
                    outputs: "Outputs"
                        InheritedReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E491")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    override shared_checks:") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    inherit shared_checks") + 1,
        )
        self.assertIn("Duplicate review item key", str(error))
        self.assertIn("first `shared_checks` entry", str(error))

    def test_review_contract_without_gates_points_at_contract_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                schema GateLessContract: "Gate-Less Contract"
                    sections:
                        summary: "Summary"
                            "Summarize the reviewed plan."

                input DraftPlan: "Draft Plan"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                output PlanReviewComment: "Plan Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "State the review verdict."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact."
                    analysis_performed: "Analysis Performed"
                        "Summarize the review analysis."
                    output_contents_that_matter: "Output Contents That Matter"
                        "State what the next owner should read first."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "List exact failing gates when they fail."

                review InvalidGateLessReview: "Invalid Gate-Less Review"
                    subject: DraftPlan
                    contract: GateLessContract
                    comment_output: PlanReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    contract_gate_checks: "Contract Gate Checks"
                        accept "The schema review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current none

                    on_reject: "If Rejected"
                        current none

                agent Demo:
                    role: "This review references a schema contract with no gates."
                    review: InvalidGateLessReview
                    inputs: "Inputs"
                        DraftPlan
                    outputs: "Outputs"
                        PlanReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E477")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    contract: GateLessContract") + 1,
        )
        self.assertIn("Review contract `GateLessContract`", str(error))

    def test_missing_input_source_points_at_input_header(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input MissingSource: "Missing Source"
                    shape: JsonObject
                    requirement: Required

                agent Demo:
                    role: "Reject inputs without a typed source."
                    inputs: "Inputs"
                        MissingSource
                    workflow: "Reply"
                        "Answer directly."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E221")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('input MissingSource: "Missing Source"') + 1,
        )
        self.assertIn("Input `MissingSource` is missing a typed `source` field.", str(error))

    def test_output_files_and_target_conflict_reports_related_locations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output InvalidBundle: "Invalid Bundle"
                    target: TurnResponse
                    shape: Comment
                    files: "Files"
                        transcript: "Transcript"
                            path: "unit_root/TRANSCRIPT.md"
                            shape: MarkdownDocument

                agent Demo:
                    role: "Reject mixed output contracts."
                    outputs: "Outputs"
                        InvalidBundle
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E224")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    files: "Files"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 2)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    target: TurnResponse") + 1,
        )
        self.assertEqual(
            error.diagnostic.related[1].location.line,
            rendered.splitlines().index("    shape: Comment") + 1,
        )
        self.assertIn("mixes `files` with `target` or `shape`", str(error))
        self.assertIn("conflicting `target` field", str(error))

    def test_output_missing_shape_points_at_target_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output IncompleteOutput: "Incomplete Output"
                    target: TurnResponse

                agent Demo:
                    role: "Reject incomplete output declarations."
                    outputs: "Outputs"
                        IncompleteOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E224")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    target: TurnResponse") + 1,
        )
        self.assertIn("must define either `files` or both `target` and `shape`", str(error))

    def test_duplicate_output_target_config_key_reports_related_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output InvalidFileOutput: "Invalid File Output"
                    target: File
                        path: "unit_root/ONE.md"
                        path: "unit_root/TWO.md"
                    shape: MarkdownDocument

                agent Demo:
                    role: "Reject duplicate output target config keys."
                    outputs: "Outputs"
                        InvalidFileOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E231")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        path: "unit_root/TWO.md"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('        path: "unit_root/ONE.md"') + 1,
        )
        self.assertIn("repeats key `path`", str(error))
        self.assertIn("first `path` config entry", str(error))

    def test_unknown_output_target_config_key_points_at_config_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output InvalidFileOutput: "Invalid File Output"
                    target: File
                        path: "unit_root/ONE.md"
                        mode: "append"
                    shape: MarkdownDocument

                agent Demo:
                    role: "Reject unknown output target config keys."
                    outputs: "Outputs"
                        InvalidFileOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E232")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        mode: "append"') + 1,
        )
        self.assertIn("uses unknown key `mode`", str(error))

    def test_missing_output_target_config_key_points_at_target_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output InvalidFileOutput: "Invalid File Output"
                    target: File
                    shape: MarkdownDocument

                agent Demo:
                    role: "Reject missing required output target config keys."
                    outputs: "Outputs"
                        InvalidFileOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E233")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    target: File") + 1,
        )
        self.assertIn("is missing required key `path`", str(error))

    def test_input_config_entries_must_be_scalar_lines_point_at_bad_config_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input InboxFile: "Inbox File"
                    source: File
                        path: "unit_root/INBOX.md"
                            "This should fail."
                    shape: MarkdownDocument
                    requirement: Required

                agent Demo:
                    role: "Reject config entries with nested bodies."
                    inputs: "Inputs"
                        InboxFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E230")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        path: "unit_root/INBOX.md"') + 1,
        )
        self.assertIn("scalar key/value lines", str(error))

    def test_duplicate_input_config_key_reports_related_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input InboxFile: "Inbox File"
                    source: File
                        path: "unit_root/ONE.md"
                        path: "unit_root/TWO.md"
                    shape: MarkdownDocument
                    requirement: Required

                agent Demo:
                    role: "Reject duplicate config keys."
                    inputs: "Inputs"
                        InboxFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E231")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        path: "unit_root/TWO.md"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('        path: "unit_root/ONE.md"') + 1,
        )
        self.assertIn("repeats key `path`", str(error))

    def test_missing_input_config_key_points_at_source_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input InboxFile: "Inbox File"
                    source: File
                    shape: MarkdownDocument
                    requirement: Required

                agent Demo:
                    role: "Reject missing required config keys."
                    inputs: "Inputs"
                        InboxFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E233")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    source: File") + 1,
        )
        self.assertIn("is missing required key `path`", str(error))

    def test_config_key_declaration_must_use_string_label_points_at_decl_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input source InboxSource: "Inbox Source"
                    required: "Required"
                        path: File

                input InboxFile: "Inbox File"
                    source: InboxSource
                        path: "unit_root/INBOX.md"
                    shape: MarkdownDocument
                    requirement: Required

                agent Demo:
                    role: "Reject non-string config key labels."
                    inputs: "Inputs"
                        InboxFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E234")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        path: File") + 1,
        )
        self.assertIn("must use a string label", str(error))

    def test_imported_duplicate_config_key_declaration_reports_imported_file_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            imported_path = self._write_prompt(
                root,
                """\
                input source InboxSource: "Inbox Source"
                    required: "Required"
                        path: "Path"
                        path: "Path Again"
                """,
                rel_path="prompts/shared/input_source.prompt",
            )
            source = """\
                import shared.input_source

                input InboxFile: "Inbox File"
                    source: shared.input_source.InboxSource
                        path: "unit_root/INBOX.md"
                    shape: MarkdownDocument
                    requirement: Required

                agent Demo:
                    role: "Reject duplicate imported config key declarations."
                    inputs: "Inputs"
                        InboxFile
                """
            imported_rendered = textwrap.dedent(
                """\
                input source InboxSource: "Inbox Source"
                    required: "Required"
                        path: "Path"
                        path: "Path Again"
                """
            )
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E235")
        self.assertEqual(error.diagnostic.location.path, imported_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            imported_rendered.splitlines().index('        path: "Path Again"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            imported_rendered.splitlines().index('        path: "Path"') + 1,
        )
        self.assertIn("repeats config key declaration `path`", str(error))

    def test_missing_local_output_shape_points_at_shape_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenOutput: "Broken Output"
                    target: TurnResponse
                    shape: MissingShape
                    requirement: Required

                agent Demo:
                    role: "Reject missing local output shapes."
                    outputs: "Outputs"
                        BrokenOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E276")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    shape: MissingShape") + 1,
        )
        self.assertIn("does not exist in the current module", str(error))

    def test_missing_local_table_declaration_points_at_named_table_use_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document ReleaseGuide: "Release Guide"
                    table release_gates: MissingTable required

                output ReleaseGuideFile: "Release Guide File"
                    target: File
                        path: "release_root/RELEASE_GUIDE.md"
                    shape: MarkdownDocument
                    structure: ReleaseGuide
                    requirement: Required

                agent Demo:
                    role: "Ship the file."
                    outputs: "Outputs"
                        ReleaseGuideFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E276")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    table release_gates: MissingTable required") + 1,
        )
        self.assertIn("Missing local table declaration: MissingTable", str(error))

    def test_input_source_must_stay_typed_points_at_source_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input BrokenInput: "Broken Input"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                agent Demo:
                    role: "Reject untyped input source titles."
                    workflow: "Reply"
                        "{{BrokenInput.source.title}}"
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            session = CompilationSession(parse_file(prompt_path))
            context = CompilationContext(session)
            input_decl = session.root_unit.inputs_by_name["BrokenInput"]
            source_item = next(
                item
                for item in input_decl.items
                if isinstance(item, model.RecordScalar) and item.key == "source"
            )
            broken_item = replace(source_item, value="Prompt")
            broken_input_decl = replace(
                input_decl,
                items=tuple(
                    broken_item if item is source_item else item for item in input_decl.items
                ),
            )

            with self.assertRaises(CompileError) as ctx:
                context._display_record_scalar_title(
                    broken_item,
                    node=AddressableNode(
                        unit=session.root_unit,
                        root_decl=broken_input_decl,
                        target=broken_item,
                    ),
                    owner_label="agent Demo workflow",
                    surface_label="workflow prose",
                )

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E275")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    source: Prompt") + 1,
        )
        self.assertIn("Input source must stay typed", str(error))

    def test_output_target_must_stay_typed_points_at_target_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenOutput: "Broken Output"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                agent Demo:
                    role: "Reject untyped output target titles."
                    workflow: "Reply"
                        "{{BrokenOutput.target.title}}"
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            session = CompilationSession(parse_file(prompt_path))
            context = CompilationContext(session)
            output_decl = session.root_unit.outputs_by_name["BrokenOutput"]
            target_item = next(
                item
                for item in output_decl.items
                if isinstance(item, model.RecordScalar) and item.key == "target"
            )
            broken_item = replace(target_item, value="TurnResponse")
            broken_output_decl = replace(
                output_decl,
                items=tuple(
                    broken_item if item is target_item else item for item in output_decl.items
                ),
            )

            with self.assertRaises(CompileError) as ctx:
                context._display_record_scalar_title(
                    broken_item,
                    node=AddressableNode(
                        unit=session.root_unit,
                        root_decl=broken_output_decl,
                        target=broken_item,
                    ),
                    owner_label="agent Demo workflow",
                    surface_label="workflow prose",
                )

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E275")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    target: TurnResponse") + 1,
        )
        self.assertIn("Output target must stay typed", str(error))

    def test_output_structure_requires_markdown_shape_points_at_shape_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document LessonPlan: "Lesson Plan"
                    section overview: "Overview"
                        "Start with the plan overview."

                output InvalidCommentOutput: "Invalid Comment Output"
                    target: TurnResponse
                    shape: Comment
                    structure: LessonPlan
                    requirement: Required

                agent Demo:
                    role: "Reject non-markdown output structure attachments."
                    outputs: "Outputs"
                        InvalidCommentOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E302")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    shape: Comment") + 1,
        )
        self.assertIn("Output structure requires a markdown-bearing shape", str(error))

    def test_output_attached_schema_without_sections_reports_schema_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input OutlineFile: "Outline File"
                    source: File
                        path: "unit_root/OUTLINE.md"
                    shape: MarkdownDocument
                    requirement: Required

                schema ArtifactOnlySchema: "Artifact Only Schema"
                    artifacts:
                        outline_file: "Outline File"
                            ref: OutlineFile

                output BuildPlan: "Build Plan"
                    target: File
                        path: "unit_root/BUILD_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required
                    schema: ArtifactOnlySchema

                agent Demo:
                    role: "Reject attached schemas without sections."
                    outputs: "Outputs"
                        BuildPlan
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E302")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('output BuildPlan: "Build Plan"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('schema ArtifactOnlySchema: "Artifact Only Schema"') + 1,
        )
        self.assertIn("Output-attached schema must export at least one section", str(error))
        self.assertIn("attached schema `ArtifactOnlySchema`", str(error))

    def test_output_files_entries_must_be_titled_sections_points_at_bad_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenBundle: "Broken Bundle"
                    files: "Files"
                        path: "unit_root/BROKEN.md"
                    requirement: Required

                agent Demo:
                    role: "Reject non-section output artifacts."
                    outputs: "Outputs"
                        BrokenBundle
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        path: "unit_root/BROKEN.md"') + 1,
        )
        self.assertIn("`files` entries must be titled sections", str(error))

    def test_output_file_entry_missing_shape_points_at_artifact_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenBundle: "Broken Bundle"
                    files: "Files"
                        artifact: "Artifact"
                            path: "unit_root/BROKEN.md"
                    requirement: Required

                agent Demo:
                    role: "Reject output artifacts without shape."
                    outputs: "Outputs"
                        BrokenBundle
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        artifact: "Artifact"') + 1,
        )
        self.assertIn("Output file entry is missing shape in BrokenBundle: artifact", str(error))

    def test_output_record_table_failure_points_at_offending_block_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenOutput: "Broken Output"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    must_include: "Must Include"
                        bullets summary: "Summary"
                            "This should fail."

                agent Demo:
                    role: "Reject non-record must_include blocks."
                    outputs: "Outputs"
                        BrokenOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        bullets summary: "Summary"') + 1,
        )
        self.assertIn("Must Include must stay record-shaped", str(error))

    def test_support_files_entries_must_be_titled_sections_points_at_bad_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenOutput: "Broken Output"
                    target: File
                        path: "unit_root/OUT.md"
                    shape: MarkdownDocument
                    requirement: Required

                    support_files: "Support Files"
                        path: "unit_root/AUDIT.md"

                agent Demo:
                    role: "Reject non-section support files."
                    outputs: "Outputs"
                        BrokenOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        path: "unit_root/AUDIT.md"') + 1,
        )
        self.assertIn("support_files entries must be titled sections", str(error))

    def test_support_files_entry_missing_string_path_points_at_path_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenOutput: "Broken Output"
                    target: File
                        path: "unit_root/OUT.md"
                    shape: MarkdownDocument
                    requirement: Required

                    support_files: "Support Files"
                        audit: "AUDIT.md"
                            path: TurnResponse

                agent Demo:
                    role: "Reject support files without a string path."
                    outputs: "Outputs"
                        BrokenOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("            path: TurnResponse") + 1,
        )
        self.assertIn(
            "support_files entry is missing string path in output BrokenOutput.support_files: audit",
            str(error),
        )

    def test_final_output_requires_output_declaration_points_at_final_output_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                schema ReleaseSchema: "Release Schema"
                    sections:
                        summary: "Summary"
                            "Provide a summary."

                agent InvalidAgent:
                    role: "Try to point final_output at a schema."
                    workflow: "Reply"
                        "Reply and stop."
                    final_output: ReleaseSchema
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("InvalidAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E211")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    final_output: ReleaseSchema") + 1,
        )
        self.assertIn("points at `ReleaseSchema`", str(error))

    def test_final_output_not_emitted_points_at_final_output_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output FinalReply: "Final Reply"
                    target: TurnResponse
                    shape: CommentText
                    requirement: Required

                agent InvalidAgent:
                    role: "Forget to emit the declared final output."
                    workflow: "Reply"
                        "Reply and stop."
                    final_output: FinalReply
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("InvalidAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E212")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    final_output: FinalReply") + 1,
        )
        self.assertIn("not emitted by the concrete turn", str(error))

    def test_final_output_rejects_file_target_points_at_target_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output ReleaseNotesFile: "Release Notes File"
                    target: File
                        path: "artifacts/RELEASE_NOTES.md"
                    shape: MarkdownDocument
                    requirement: Required

                agent InvalidAgent:
                    role: "Try to end with a file."
                    workflow: "Reply"
                        "Reply and stop."
                    outputs: "Outputs"
                        ReleaseNotesFile
                    final_output: ReleaseNotesFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("InvalidAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E213")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    target: File") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    final_output: ReleaseNotesFile") + 1,
        )
        self.assertIn("not one `TurnResponse` assistant message", str(error))
        self.assertIn("`final_output` field", str(error))

    def test_final_output_example_file_retired_points_at_example_file_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field summary: "Summary"
                        type: string

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema
                    example_file: "examples/repo_status.json"

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E215")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    example_file: "examples/repo_status.json"') + 1,
        )
        self.assertIn("still uses retired `example_file`", str(error))

    def test_final_output_example_mismatch_points_at_example_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field summary: "Summary"
                        type: string

                    example:
                        summary: 7

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E216")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    example:") + 1,
        )
        self.assertIn("does not match the lowered schema", str(error))
        self.assertIn("7 is not of type 'string'", str(error))

    def test_final_output_invalid_json_schema_points_at_schema_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field summary: "Summary"
                        type: definitely_not_a_real_json_schema_type

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E217")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('output schema RepoStatusSchema: "Repo Status Schema"') + 1,
        )
        self.assertIn("not valid Draft 2020-12 JSON Schema", str(error))
        self.assertIn("definitely_not_a_real_json_schema_type", str(error))

    def test_final_output_openai_subset_failure_points_at_schema_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field level_1: "Level 1"
                        type: object
                        field level_2: "Level 2"
                            type: object
                            field level_3: "Level 3"
                                type: object
                                field level_4: "Level 4"
                                    type: object
                                    field level_5: "Level 5"
                                        type: object
                                        field level_6: "Level 6"
                                            type: string

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E218")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('output schema RepoStatusSchema: "Repo Status Schema"') + 1,
        )
        self.assertIn("outside the supported OpenAI structured outputs subset", str(error))
        self.assertIn("nesting exceeds 5 levels", str(error))

    def test_output_schema_inline_enum_requires_values_points_at_type_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        type: enum

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E227")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        type: enum") + 1,
        )
        self.assertIn("missing `values:`", str(error))

    def test_output_schema_values_requires_type_enum_points_at_values_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        type: string
                        values:
                            ok
                            blocked

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E228")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        values:") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("        type: string") + 1,
        )
        self.assertIn("`values:` requires `type: enum`", str(error))

    def test_output_schema_mixed_inline_enum_forms_point_at_legacy_enum_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        type: enum
                        enum:
                            ok
                            blocked

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E229")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        enum:") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("        type: enum") + 1,
        )
        self.assertIn("cannot be mixed", str(error))

    def test_output_schema_legacy_enum_requires_string_points_at_enum_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        type: integer
                        enum:
                            1
                            2

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E229")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        enum:") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("        type: integer") + 1,
        )
        self.assertIn("requires `type: string`", str(error))

    def test_output_schema_required_points_at_required_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        type: string
                        required

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E236")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        required") + 1,
        )
        self.assertIn("Delete `required`", str(error))

    def test_output_schema_optional_points_at_optional_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        type: string
                        optional

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E237")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        optional") + 1,
        )
        self.assertIn("Use `nullable`", str(error))

    def test_missing_inherited_output_entry_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BaseHandoff: "Base Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    must_include: "Must Include"
                        what_changed: "What Changed"
                            "Say what changed."

                output LessonsLeadOutput[BaseHandoff]: "Lessons Lead Output"
                    inherit target
                    inherit shape
                    inherit requirement

                agent Demo:
                    role: "Fail loud when the child skips an inherited output entry."
                    outputs: "Outputs"
                        LessonsLeadOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E003")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                'output LessonsLeadOutput[BaseHandoff]: "Lessons Lead Output"'
            )
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    must_include: "Must Include"') + 1,
        )
        self.assertIn("Missing inherited output entry in LessonsLeadOutput: must_include", str(error))
        self.assertIn("Related:", str(error))

    def test_output_patch_without_parent_points_at_inherit_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output LessonsLeadOutput: "Lessons Lead Output"
                    inherit target
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                agent Demo:
                    role: "Fail loud when output patch syntax appears without a parent."
                    outputs: "Outputs"
                        LessonsLeadOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E252")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    inherit target") + 1,
        )
        self.assertIn("requires an inherited output", str(error))

    def test_duplicate_output_item_key_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BaseHandoff: "Base Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    standalone_read: "Standalone Read"
                        "Keep the note standalone."

                output LessonsLeadOutput[BaseHandoff]: "Lessons Lead Output"
                    inherit target
                    inherit shape
                    inherit requirement
                    inherit standalone_read
                    override standalone_read: "Standalone Read"
                        "Re-state the note for the local child."

                agent Demo:
                    role: "Reject duplicate inherited output item accounting."
                    outputs: "Outputs"
                        LessonsLeadOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E255")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    override standalone_read: "Standalone Read"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    inherit standalone_read") + 1,
        )
        self.assertIn("repeats output item key `standalone_read`", str(error))
        self.assertIn("first `standalone_read` entry", str(error))

    def test_output_override_kind_mismatch_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BaseHandoff: "Base Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    must_include: "Must Include"
                        what_changed: "What Changed"
                            "Say what changed."

                output LessonsLeadOutput[BaseHandoff]: "Lessons Lead Output"
                    inherit target
                    inherit shape
                    inherit requirement
                    override must_include: TurnResponse

                agent Demo:
                    role: "Fail loud when output override kind does not match the parent."
                    outputs: "Outputs"
                        LessonsLeadOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E255")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    override must_include: TurnResponse") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    must_include: "Must Include"') + 1,
        )
        self.assertIn("overrides entry `must_include` with the wrong kind", str(error))
        self.assertIn("Related:", str(error))

    def test_duplicate_workflow_item_key_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow DuplicateWorkflow: "Duplicate Workflow"
                    step_one: "Step One"
                        "Say hello."
                    step_one: "Step One Again"
                        "Say world."

                agent Demo:
                    role: "Reject duplicate workflow section keys."
                    workflow: DuplicateWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E261")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    step_one: "Step One Again"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    step_one: "Step One"') + 1,
        )
        self.assertIn("repeats key `step_one`", str(error))
        self.assertIn("first `step_one` entry", str(error))

    def test_workflow_patch_without_parent_points_at_inherit_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow ChildWorkflow: "Child Workflow"
                    inherit greeting

                agent Demo:
                    role: "Fail loud when workflow patch syntax appears without a parent."
                    workflow: ChildWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E243")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    inherit greeting") + 1,
        )
        self.assertIn("requires an inherited workflow", str(error))

    def test_missing_inherited_workflow_entry_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow BaseWorkflow: "Base Workflow"
                    greeting: "Greeting"
                        "Say hello."
                    closing: "Closing"
                        "Say goodbye."

                workflow ChildWorkflow[BaseWorkflow]: "Child Workflow"
                    inherit greeting

                agent Demo:
                    role: "Keep inherited workflows explicit."
                    workflow: ChildWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E003")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('workflow ChildWorkflow[BaseWorkflow]: "Child Workflow"')
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    closing: "Closing"') + 1,
        )
        self.assertIn("Missing inherited workflow entry in ChildWorkflow: closing", str(error))
        self.assertIn("Related:", str(error))

    def test_workflow_override_kind_mismatch_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow HelperWorkflow: "Helper Workflow"
                    helper_step: "Helper Step"
                        "Do helper work."

                workflow BaseWorkflow: "Base Workflow"
                    shared_step: "Shared Step"
                        "Do the base work."

                workflow ChildWorkflow[BaseWorkflow]: "Child Workflow"
                    override shared_step: HelperWorkflow

                agent Demo:
                    role: "Reject workflow override kind mismatches."
                    workflow: ChildWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E242")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    override shared_step: HelperWorkflow") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    shared_step: "Shared Step"') + 1,
        )
        self.assertIn("overrides `shared_step` with the wrong kind", str(error))
        self.assertIn("Related:", str(error))

    def test_duplicate_inherited_law_subsection_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow BaseWorkflow: "Base Workflow"
                    law:
                        currentness:
                            current none

                workflow ChildWorkflow[BaseWorkflow]: "Child Workflow"
                    law:
                        inherit currentness
                        inherit currentness

                agent Demo:
                    role: "Reject duplicate inherited law subsections."
                    workflow: ChildWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E382")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        inherit_lines = [
            line_number
            for line_number, line in enumerate(rendered.splitlines(), start=1)
            if line == "        inherit currentness"
        ]
        self.assertEqual(error.diagnostic.location.line, inherit_lines[1])
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, inherit_lines[0])
        self.assertIn("accounts for subsection `currentness` more than once", str(error))
        self.assertIn("first `currentness` subsection", str(error))

    def test_missing_inherited_law_subsection_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow BaseWorkflow: "Base Workflow"
                    law:
                        currentness:
                            current none
                        stop_lines:
                            stop "Stop here."

                workflow ChildWorkflow[BaseWorkflow]: "Child Workflow"
                    law:
                        inherit stop_lines

                agent Demo:
                    role: "Keep inherited law sections explicit."
                    workflow: ChildWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E383")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        inherit_line = rendered.splitlines().index("        inherit stop_lines") + 1
        self.assertEqual(
            error.diagnostic.location.line,
            inherit_line,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("        currentness:") + 1,
        )
        self.assertIn("omits parent subsection(s) `currentness`", str(error))
        self.assertIn("Related:", str(error))

    def test_duplicate_properties_entry_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
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
                    workflow: "Review"
                        "This should fail."
                    outputs: "Outputs"
                        ReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E295")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        verdict: "Verdict Again"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('        verdict: "Verdict"') + 1,
        )
        self.assertIn("properties entry key `verdict`", str(error))
        self.assertIn("first `verdict` properties entry", str(error))

    def test_readable_guard_disallowed_source_points_at_guard_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenComment: "Broken Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    callout scope: "Scope" when BrokenComment.summary_present
                        kind: note
                        "This should fail."

                agent Demo:
                    role: "Compile the broken comment."
                    workflow: "Warn"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E296")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                '    callout scope: "Scope" when BrokenComment.summary_present'
            )
            + 1,
        )
        self.assertIn("Readable guard reads disallowed source", str(error))
        self.assertIn("BrokenComment.summary_present", str(error))

    def test_guard_shell_without_when_reports_guard_line_for_agent_compile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenComment: "Broken Comment"
                    target: TurnResponse
                    shape: Comment

                    guard follow_up when true
                        properties:
                            escalation: "Escalation"
                                "This should fail."

                agent Demo:
                    role: "Compile the broken guard shell."
                    workflow: "Review"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)
            output_decl = next(
                decl for decl in prompt.declarations if isinstance(decl, model.OutputDecl)
            )
            guard_block = next(
                item
                for item in output_decl.items
                if isinstance(item, model.ReadableBlock) and item.kind == "guard"
            )
            mutated_output = replace(
                output_decl,
                items=tuple(
                    replace(item, when_expr=None) if item is guard_block else item
                    for item in output_decl.items
                ),
            )
            mutated_prompt = replace(
                prompt,
                declarations=tuple(
                    mutated_output if decl is output_decl else decl for decl in prompt.declarations
                ),
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(mutated_prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E297")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    guard follow_up when true") + 1,
        )
        self.assertIn("Readable guard shell `output BrokenComment.follow_up`", str(error))
        self.assertIn("must define a guard expression", str(error))

    def test_unknown_callout_kind_points_at_kind_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenComment: "Broken Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    callout warning_box: "Warning Box"
                        kind: urgent
                        "This should fail."

                agent Demo:
                    role: "Compile the broken comment."
                    workflow: "Warn"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E297")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        kind: urgent") + 1,
        )
        self.assertIn("unknown callout kind `urgent`", str(error))
        self.assertIn("shipped callout kinds", str(error))

    def test_document_table_without_columns_points_at_table_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document BrokenGuide: "Broken Guide"
                    table release_gates: "Release Gates"
                        notes:
                            "This should fail."

                output BrokenGuideFile: "Broken Guide File"
                    target: File
                        path: "release_root/BROKEN_GUIDE.md"
                    shape: MarkdownDocument
                    structure: BrokenGuide
                    requirement: Required

                agent Demo:
                    role: "Compile the broken guide."
                    workflow: "Draft"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenGuideFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E297")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    table release_gates: "Release Gates"') + 1,
        )
        self.assertIn("must declare at least one column", str(error))

    def test_duplicate_document_block_key_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document BrokenGuide: "Broken Guide"
                    section summary: "Summary"
                        "Start with the current goal."

                    section summary: "Summary Again"
                        "This should fail."

                output BrokenGuideFile: "Broken Guide File"
                    target: File
                        path: "release_root/BROKEN_GUIDE.md"
                    shape: MarkdownDocument
                    structure: BrokenGuide
                    requirement: Required

                agent Demo:
                    role: "Compile the broken guide."
                    workflow: "Draft"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenGuideFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E295")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    section summary: "Summary Again"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    section summary: "Summary"') + 1,
        )
        self.assertIn("document block key `summary`", str(error))
        self.assertIn("first `summary` document block", str(error))

    def test_guard_shell_without_when_reports_guard_line_for_declaration_compile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document BrokenGuide: "Broken Guide"
                    guard follow_up when true
                        section escalation: "Escalation"
                            "This should fail."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)
            document_decl = next(
                decl for decl in prompt.declarations if isinstance(decl, model.DocumentDecl)
            )
            guard_block = next(
                item
                for item in document_decl.body.items
                if isinstance(item, model.ReadableBlock) and item.kind == "guard"
            )
            mutated_document = replace(
                document_decl,
                body=replace(
                    document_decl.body,
                    items=tuple(
                        replace(item, when_expr=None) if item is guard_block else item
                        for item in document_decl.body.items
                    ),
                ),
            )
            mutated_prompt = replace(
                prompt,
                declarations=tuple(
                    mutated_document if decl is document_decl else decl
                    for decl in prompt.declarations
                ),
            )
            session = CompilationSession(mutated_prompt)

            with self.assertRaises(CompileError) as ctx:
                session.compile_readable_declaration("document", "BrokenGuide")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E297")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    guard follow_up when true") + 1,
        )
        self.assertIn("Readable guard shell `follow_up`", str(error))
        self.assertIn("must define a guard expression", str(error))

    def test_document_override_without_parent_points_at_override_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document BrokenGuide: "Broken Guide"
                    override section summary: "Summary"
                        "This should fail."

                output BrokenGuideFile: "Broken Guide File"
                    target: File
                        path: "release_root/BROKEN_GUIDE.md"
                    shape: MarkdownDocument
                    structure: BrokenGuide
                    requirement: Required

                agent Demo:
                    role: "Compile the broken guide."
                    workflow: "Draft"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenGuideFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E305")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    override section summary: "Summary"') + 1,
        )
        self.assertIn("requires an inherited document declaration", str(error))

    def test_document_override_kind_mismatch_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document LessonPlan: "Lesson Plan"
                    sequence read_order: "Read Order"
                        first: "Read the brief."

                document BrokenLessonPlan[LessonPlan]: "Broken Lesson Plan"
                    override definitions read_order: "Read Order"
                        first: "Read the brief."

                output BrokenLessonPlanFile: "Broken Lesson Plan File"
                    target: File
                        path: "lesson_root/BROKEN_LESSON_PLAN.md"
                    shape: MarkdownDocument
                    structure: BrokenLessonPlan
                    requirement: Required

                agent Demo:
                    role: "Compile the broken lesson plan."
                    workflow: "Adapt"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenLessonPlanFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E305")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    override definitions read_order: "Read Order"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    sequence read_order: "Read Order"') + 1,
        )
        self.assertIn("overrides entry `read_order` with the wrong block kind", str(error))
        self.assertIn("inherited `read_order` entry", str(error))

    def test_missing_inherited_document_entry_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document BaseGuide: "Base Guide"
                    section summary: "Summary"
                        "Lead with the current goal."

                    sequence read_order: "Read Order"
                        first: "Read the brief."

                document ChildGuide[BaseGuide]: "Child Guide"
                    inherit summary

                output ChildGuideFile: "Child Guide File"
                    target: File
                        path: "guide_root/CHILD_GUIDE.md"
                    shape: MarkdownDocument
                    structure: ChildGuide
                    requirement: Required

                agent Demo:
                    role: "Compile the incomplete child guide."
                    workflow: "Draft"
                        "This should fail."
                    outputs: "Outputs"
                        ChildGuideFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E003")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('document ChildGuide[BaseGuide]: "Child Guide"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    sequence read_order: "Read Order"') + 1,
        )
        self.assertIn("Missing inherited document entry in ChildGuide: read_order", str(error))
        self.assertIn("inherited `read_order` entry", str(error))

    def test_skill_package_case_collision_uses_file_scoped_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            prompt_path = prompts / "SKILL.prompt"
            prompt_path.write_text(
                textwrap.dedent(
                    """\
                    skill package PathCasePreservation: "Path Case Preservation"
                        metadata:
                            name: "path-case-preservation"
                        "Keep companion paths stable."
                    """
                ),
                encoding="utf-8",
            )
            collision_path = prompts / "skill.md"
            collision_path.write_text(
                "This file case-collides with the compiled `SKILL.md` output.\n",
                encoding="utf-8",
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_skill_package()

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E304")
        self.assertEqual(error.diagnostic.location.path, collision_path.resolve())
        self.assertIsNone(error.diagnostic.location.line)
        self.assertIn("case-collides", str(error))

    def test_skill_package_agent_output_collision_reports_related_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "agents").mkdir(parents=True)
            prompt_path = prompts / "SKILL.prompt"
            prompt_path.write_text(
                textwrap.dedent(
                    """\
                    skill package AgentOutputCollision: "Agent Output Collision"
                        metadata:
                            name: "agent-output-collision"
                        "Fail loud when bundled files shadow compiled agent output."
                    """
                ),
                encoding="utf-8",
            )
            bundled_prompt_path = prompts / "agents" / "reviewer.prompt"
            bundled_prompt_path.write_text(
                textwrap.dedent(
                    """\
                    agent Reviewer:
                        role: "Review the bundle."
                    """
                ),
                encoding="utf-8",
            )
            collision_path = prompts / "agents" / "reviewer.md"
            collision_path.write_text(
                "This file collides with the compiled bundled agent markdown.\n",
                encoding="utf-8",
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_skill_package()

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E304")
        self.assertEqual(error.diagnostic.location.path, collision_path.resolve())
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.path,
            bundled_prompt_path.resolve(),
        )
        self.assertIn("Duplicate skill package bundled path", str(error))
        self.assertIn("Related:", str(error))


if __name__ == "__main__":
    unittest.main()
