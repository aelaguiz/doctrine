from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine import model
from doctrine.compiler import CompilationSession
from doctrine.parser import parse_file, parse_text


class ReviewBindingShorthandTests(unittest.TestCase):
    def _compile_agent(self, source: str, *, agent_name: str):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompts" / "AGENTS.prompt"
            prompt_path.parent.mkdir(parents=True)
            prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
            prompt = parse_file(prompt_path)
            return CompilationSession(prompt).compile_agent(agent_name)

    def test_identity_shorthand_lowers_on_all_review_binding_surfaces(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """\
                input DraftPlan: "Draft Plan"
                    source: File
                        path: "unit_root/DRAFT_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required

                workflow PlanReviewContract: "Plan Review Contract"
                    completeness: "Completeness"
                        "Confirm the reviewed plan includes the required structure."

                agent ReviewLead:
                    role: "Own accepted plans."
                    workflow: "Follow Up"
                        "Take accepted plans forward."

                agent PlanAuthor:
                    role: "Fix rejected plans."
                    workflow: "Revise"
                        "Revise the rejected plan."

                output AcceptanceReviewComment: "Acceptance Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    verdict: "Verdict"
                        "State whether the plan passed review."

                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact."

                    analysis_performed: "Analysis Performed"
                        "Summarize the review analysis."

                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize what the next owner should read first."

                    current_artifact: "Current Artifact"
                        "Name the artifact that remains current after review."

                    next_owner: "Next Owner"
                        "Name the next owner."

                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "List exact failing gates in authored order."

                    trust_surface:
                        current_artifact

                output AcceptanceControlFinalResponse: "Acceptance Control Final Response"
                    target: TurnResponse
                    shape: CommentText
                    requirement: Required

                    verdict: "Verdict"
                        "Repeat the review verdict."

                    current_artifact: "Current Artifact"
                        "Repeat the current artifact."

                    next_owner: "Next Owner"
                        "Repeat the next owner."

                abstract review BaseAcceptanceReview: "Base Acceptance Review"
                    subject: DraftPlan
                    contract: PlanReviewContract
                    comment_output: AcceptanceReviewComment

                    fields:
                        verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        current_artifact
                        failing_gates: failure_detail.failing_gates
                        next_owner

                    contract_checks: "Contract Checks"
                        accept "The acceptance review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current artifact DraftPlan via AcceptanceReviewComment.current_artifact
                        route "Accepted plan goes to ReviewLead." -> ReviewLead

                    on_reject: "If Rejected"
                        current artifact DraftPlan via AcceptanceReviewComment.current_artifact
                        route "Rejected plan goes to PlanAuthor." -> PlanAuthor

                review AcceptanceReview[BaseAcceptanceReview]: "Acceptance Review"
                    override fields:
                        verdict
                        reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        current_artifact: current_artifact
                        failing_gates: failure_detail.failing_gates
                        next_owner
                    inherit contract_checks
                    inherit on_accept
                    inherit on_reject

                agent AcceptanceReviewDemo:
                    role: "Keep review binding shorthand aligned."
                    review: AcceptanceReview
                    inputs: "Inputs"
                        DraftPlan
                    outputs: "Outputs"
                        AcceptanceReviewComment
                        AcceptanceControlFinalResponse
                    final_output:
                        output: AcceptanceControlFinalResponse
                        review_fields:
                            verdict
                            current_artifact: current_artifact
                            next_owner
                """
            )
        )

        base_review = next(
            decl
            for decl in prompt.declarations
            if isinstance(decl, model.ReviewDecl) and decl.name == "BaseAcceptanceReview"
        )
        child_review = next(
            decl
            for decl in prompt.declarations
            if isinstance(decl, model.ReviewDecl) and decl.name == "AcceptanceReview"
        )
        agent = next(
            decl
            for decl in prompt.declarations
            if isinstance(decl, model.Agent) and decl.name == "AcceptanceReviewDemo"
        )

        base_fields = next(
            item for item in base_review.body.items if isinstance(item, model.ReviewFieldsConfig)
        )
        override_fields = next(
            item for item in child_review.body.items if isinstance(item, model.ReviewOverrideFields)
        )
        final_output = next(
            field for field in agent.fields if isinstance(field, model.FinalOutputField)
        )
        assert final_output.review_fields is not None

        self.assertEqual(base_fields.bindings[0].field_path, ("verdict",))
        self.assertEqual(base_fields.bindings[0].source_span, model.SourceSpan(line=71, column=9))
        self.assertEqual(override_fields.bindings[1].field_path, ("reviewed_artifact",))
        self.assertIsNotNone(override_fields.bindings[1].source_span)
        self.assertEqual(final_output.review_fields.bindings[0].field_path, ("verdict",))
        self.assertIsNotNone(final_output.review_fields.bindings[0].source_span)
        self.assertEqual(final_output.review_fields.bindings[1].field_path, ("current_artifact",))
        self.assertEqual(final_output.review_fields.bindings[2].field_path, ("next_owner",))

    def test_review_fields_and_final_output_shorthand_compile_like_explicit_bindings(self) -> None:
        explicit_agent = self._compile_agent(
            self._review_binding_prompt(
                review_fields="""
                    verdict: verdict
                    reviewed_artifact: reviewed_artifact
                    analysis: analysis_performed
                    readback: output_contents_that_matter
                    current_artifact: current_artifact
                    failing_gates: failure_detail.failing_gates
                    next_owner: next_owner
                """,
                final_output_review_fields="""
                    verdict: verdict
                    current_artifact: current_artifact
                    next_owner: next_owner
                """,
            ),
            agent_name="AcceptanceReviewAgent",
        )
        shorthand_agent = self._compile_agent(
            self._review_binding_prompt(
                review_fields="""
                    verdict
                    reviewed_artifact
                    analysis: analysis_performed
                    readback: output_contents_that_matter
                    current_artifact
                    failing_gates: failure_detail.failing_gates
                    next_owner
                """,
                final_output_review_fields="""
                    verdict
                    current_artifact: current_artifact
                    next_owner
                """,
            ),
            agent_name="AcceptanceReviewAgent",
        )

        assert explicit_agent.review is not None
        assert shorthand_agent.review is not None
        self.assertEqual(shorthand_agent.review.carrier_fields, explicit_agent.review.carrier_fields)
        self.assertEqual(
            shorthand_agent.review.final_response.review_fields,
            explicit_agent.review.final_response.review_fields,
        )
        self.assertEqual(
            shorthand_agent.review.final_response.control_ready,
            explicit_agent.review.final_response.control_ready,
        )

    def test_review_override_fields_shorthand_compiles_like_explicit_bindings(self) -> None:
        explicit_agent = self._compile_agent(
            self._review_override_prompt(
                override_fields="""
                    verdict: verdict
                    reviewed_artifact: reviewed_artifact
                    analysis: analysis_performed
                    readback: output_contents_that_matter
                    current_artifact: current_artifact
                    failing_gates: failure_detail.failing_gates
                    next_owner: next_owner
                """,
            ),
            agent_name="AcceptanceReviewOverrideDemo",
        )
        shorthand_agent = self._compile_agent(
            self._review_override_prompt(
                override_fields="""
                    verdict
                    reviewed_artifact: reviewed_artifact
                    analysis: analysis_performed
                    readback: output_contents_that_matter
                    current_artifact
                    failing_gates: failure_detail.failing_gates
                    next_owner: next_owner
                """,
            ),
            agent_name="AcceptanceReviewOverrideDemo",
        )

        assert explicit_agent.review is not None
        assert shorthand_agent.review is not None
        self.assertEqual(shorthand_agent.review.carrier_fields, explicit_agent.review.carrier_fields)

    def _review_binding_prompt(
        self,
        *,
        review_fields: str,
        final_output_review_fields: str,
    ) -> str:
        return f"""
        input DraftPlan: "Draft Plan"
            source: File
                path: "unit_root/DRAFT_PLAN.md"
            shape: MarkdownDocument
            requirement: Required

        schema PlanReviewContract: "Plan Review Contract"
            sections:
                summary: "Summary"
                    "Summarize the reviewed plan."

            gates:
                outline_complete: "Outline Complete"
                    "Confirm the reviewed plan includes the outline."

        agent ReviewLead:
            role: "Own accepted plans."
            workflow: "Follow Up"
                "Take accepted plans forward."

        agent PlanAuthor:
            role: "Fix rejected plans."
            workflow: "Revise"
                "Revise the rejected plan."

        output AcceptanceReviewComment: "Acceptance Review Comment"
            target: TurnResponse
            shape: Comment
            requirement: Required

            verdict: "Verdict"
                "State whether the plan passed review."

            reviewed_artifact: "Reviewed Artifact"
                "Name the reviewed artifact."

            analysis_performed: "Analysis Performed"
                "Summarize the review analysis."

            output_contents_that_matter: "Output Contents That Matter"
                "Summarize what the next owner should read first."

            current_artifact: "Current Artifact"
                "Name the artifact that remains current after review."

            next_owner: "Next Owner"
                "Name {{{{ReviewLead}}}} when accepted and {{{{PlanAuthor}}}} when rejected."

            failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                failing_gates: "Failing Gates"
                    "List exact failing gates in authored order."

            trust_surface:
                current_artifact

        output AcceptanceControlFinalResponse: "Acceptance Control Final Response"
            target: TurnResponse
            shape: CommentText
            requirement: Required

            verdict: "Verdict"
                "Repeat the review verdict."

            current_artifact: "Current Artifact"
                "Repeat the current artifact."

            next_owner: "Next Owner"
                "Name {{{{ReviewLead}}}} when accepted and {{{{PlanAuthor}}}} when rejected."

        review AcceptanceReview: "Acceptance Review"
            subject: DraftPlan
            contract: PlanReviewContract
            comment_output: AcceptanceReviewComment

            fields:
{textwrap.indent(textwrap.dedent(review_fields).strip(), "                ")}

            contract_checks: "Contract Checks"
                accept "The acceptance review contract passes." when contract.passes

            on_accept: "If Accepted"
                current artifact DraftPlan via AcceptanceReviewComment.current_artifact
                route "Accepted plan goes to ReviewLead." -> ReviewLead

            on_reject: "If Rejected"
                current artifact DraftPlan via AcceptanceReviewComment.current_artifact
                route "Rejected plan goes to PlanAuthor." -> PlanAuthor

        agent AcceptanceReviewAgent:
            role: "Emit the review comment and end with a control summary."
            review: AcceptanceReview
            inputs: "Inputs"
                DraftPlan
            outputs: "Outputs"
                AcceptanceReviewComment
                AcceptanceControlFinalResponse
            final_output:
                output: AcceptanceControlFinalResponse
                review_fields:
{textwrap.indent(textwrap.dedent(final_output_review_fields).strip(), "                    ")}
        """

    def _review_override_prompt(self, *, override_fields: str) -> str:
        return f"""
        input DraftPlan: "Draft Plan"
            source: File
                path: "unit_root/DRAFT_PLAN.md"
            shape: MarkdownDocument
            requirement: Required

        workflow PlanReviewContract: "Plan Review Contract"
            completeness: "Completeness"
                "Confirm the reviewed plan includes the required structure."

        agent ReviewLead:
            role: "Own accepted plans."
            workflow: "Follow Up"
                "Take accepted plans forward."

        agent PlanAuthor:
            role: "Fix rejected plans."
            workflow: "Revise"
                "Revise the rejected plan."

        output AcceptanceReviewComment: "Acceptance Review Comment"
            target: TurnResponse
            shape: Comment
            requirement: Required

            verdict: "Verdict"
                "State whether the plan passed review."

            reviewed_artifact: "Reviewed Artifact"
                "Name the reviewed artifact."

            analysis_performed: "Analysis Performed"
                "Summarize the review analysis."

            output_contents_that_matter: "Output Contents That Matter"
                "Summarize what the next owner should read first."

            current_artifact: "Current Artifact"
                "Name the artifact that remains current after review."

            next_owner: "Next Owner"
                "Name {{{{ReviewLead}}}} when accepted and {{{{PlanAuthor}}}} when rejected."

            failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                failing_gates: "Failing Gates"
                    "List exact failing gates in authored order."

            trust_surface:
                current_artifact

        abstract review BaseAcceptanceReview: "Base Acceptance Review"
            subject: DraftPlan
            contract: PlanReviewContract
            comment_output: AcceptanceReviewComment

            fields:
                verdict: verdict
                reviewed_artifact: reviewed_artifact
                analysis: analysis_performed
                readback: output_contents_that_matter
                current_artifact: current_artifact
                failing_gates: failure_detail.failing_gates
                next_owner: next_owner

            contract_checks: "Contract Checks"
                accept "The acceptance review contract passes." when contract.passes

            on_accept: "If Accepted"
                current artifact DraftPlan via AcceptanceReviewComment.current_artifact
                route "Accepted plan goes to ReviewLead." -> ReviewLead

            on_reject: "If Rejected"
                current artifact DraftPlan via AcceptanceReviewComment.current_artifact
                route "Rejected plan goes to PlanAuthor." -> PlanAuthor

        review AcceptanceReview[BaseAcceptanceReview]: "Acceptance Review"
            override fields:
{textwrap.indent(textwrap.dedent(override_fields).strip(), "                ")}
            inherit contract_checks
            inherit on_accept
            inherit on_reject

        agent AcceptanceReviewOverrideDemo:
            role: "Use the inherited review with override fields."
            review: AcceptanceReview
            inputs: "Inputs"
                DraftPlan
            outputs: "Outputs"
                AcceptanceReviewComment
        """
