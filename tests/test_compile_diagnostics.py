from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
