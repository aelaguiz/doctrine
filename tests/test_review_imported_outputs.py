from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class ReviewImportedOutputsTests(unittest.TestCase):
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

    def test_imported_review_comment_output_can_bind_local_routed_agents(self) -> None:
        agent = self._compile_agent(
            """
            import shared.review

            input DraftSpec: "Draft Spec"
                source: File
                    path: "unit_root/DRAFT_SPEC.md"
                shape: MarkdownDocument
                requirement: Required

            workflow DraftReviewContract: "Draft Review Contract"
                completeness: "Completeness"
                    "Confirm the draft covers the required sections."

            agent ReviewLead:
                role: "Own accepted draft follow-up."
                workflow: "Follow Up"
                    "Take the accepted draft to the next planning step."

            agent DraftAuthor:
                role: "Fix rejected draft defects."
                workflow: "Revise"
                    "Revise the same draft when review requests changes."

            review DraftReview: "Draft Review"
                subject: DraftSpec
                contract: DraftReviewContract
                comment_output: shared.review.DraftReviewComment

                fields:
                    verdict: verdict
                    reviewed_artifact: reviewed_artifact
                    analysis: analysis_performed
                    readback: output_contents_that_matter
                    current_artifact: current_artifact
                    failing_gates: failure_detail.failing_gates
                    next_owner: next_owner

                contract_checks: "Contract Checks"
                    accept "The shared draft review contract passes." when contract.passes

                on_accept: "If Accepted"
                    current artifact DraftSpec via shared.review.DraftReviewComment.current_artifact
                    route "Accepted draft returns to ReviewLead." -> ReviewLead

                on_reject: "If Rejected"
                    current artifact DraftSpec via shared.review.DraftReviewComment.current_artifact
                    route "Rejected draft returns to DraftAuthor." -> DraftAuthor

            agent ImportedDraftReviewDemo:
                role: "Use an imported comment output that still binds local routed owners."
                review: DraftReview
                inputs: "Inputs"
                    DraftSpec
                outputs: "Outputs"
                    shared.review.DraftReviewComment
            """,
            agent_name="ImportedDraftReviewDemo",
            extra_files={
                "prompts/shared/review.prompt": """
                output DraftReviewComment: "Draft Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    verdict: "Verdict"
                        "Say whether the review accepted the draft or requested changes."

                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."

                    analysis_performed: "Analysis Performed"
                        "Summarize the review analysis that led to the verdict."

                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize the parts of the draft the next owner must read first."

                    current_artifact: "Current Artifact"
                        "Name the artifact that remains current after review."

                    next_owner: "Next Owner"
                        "Name the next owner, including {{ReviewLead}} when the draft is accepted and {{DraftAuthor}} when the draft is rejected."

                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "Name the failing review gates in authored order."

                    trust_surface:
                        current_artifact

                    standalone_read: "Standalone Read"
                        "A downstream owner should be able to read this review alone and understand the verdict, current artifact, and next owner."
                """,
            },
        )

        rendered = render_markdown(agent)
        self.assertIn("Accepted draft returns to ReviewLead.", rendered)
        self.assertIn("Rejected draft returns to DraftAuthor.", rendered)
        self.assertIn(
            "Name the next owner, including ReviewLead when the draft is accepted and DraftAuthor when the draft is rejected.",
            rendered,
        )

    def test_imported_review_comment_output_can_feed_split_final_output_trust_surface(self) -> None:
        # Imported review comment outputs and local split final outputs share one
        # routed-owner story. The final message must still surface Current Artifact
        # through the imported review binding instead of crashing on module boundaries.
        agent = self._compile_agent(
            """
            import shared.review

            input DraftSpec: "Draft Spec"
                source: File
                    path: "unit_root/DRAFT_SPEC.md"
                shape: MarkdownDocument
                requirement: Required

            workflow DraftReviewContract: "Draft Review Contract"
                completeness: "Completeness"
                    "Confirm the draft covers the required sections."

            agent ReviewLead:
                role: "Own accepted draft follow-up."
                workflow: "Follow Up"
                    "Take the accepted draft to the next planning step."

            agent DraftAuthor:
                role: "Fix rejected draft defects."
                workflow: "Revise"
                    "Revise the same draft when review requests changes."

            output DraftReviewDecision: "Draft Review Decision"
                target: TurnResponse
                shape: CommentText
                requirement: Required

                trust_surface:
                    current_artifact

                control_summary: "Control Summary"
                    "End with one short control summary for the routed owner."

                standalone_read: "Standalone Read"
                    "The final control summary should stand on its own for the routed owner."

            review DraftReview: "Draft Review"
                subject: DraftSpec
                contract: DraftReviewContract
                comment_output: shared.review.DraftReviewComment

                fields:
                    verdict: verdict
                    reviewed_artifact: reviewed_artifact
                    analysis: analysis_performed
                    readback: output_contents_that_matter
                    current_artifact: current_artifact
                    failing_gates: failure_detail.failing_gates
                    next_owner: next_owner

                contract_checks: "Contract Checks"
                    accept "The shared draft review contract passes." when contract.passes

                on_accept: "If Accepted"
                    current artifact DraftSpec via shared.review.DraftReviewComment.current_artifact
                    route "Accepted draft returns to ReviewLead." -> ReviewLead

                on_reject: "If Rejected"
                    current artifact DraftSpec via shared.review.DraftReviewComment.current_artifact
                    route "Rejected draft returns to DraftAuthor." -> DraftAuthor

            agent ImportedDraftReviewSplitDemo:
                role: "Use an imported review comment output and a local control-only final output."
                review: DraftReview
                inputs: "Inputs"
                    DraftSpec
                outputs: "Outputs"
                    shared.review.DraftReviewComment
                    DraftReviewDecision
                final_output: DraftReviewDecision
            """,
            agent_name="ImportedDraftReviewSplitDemo",
            extra_files={
                "prompts/shared/review.prompt": """
                output DraftReviewComment: "Draft Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    verdict: "Verdict"
                        "Say whether the review accepted the draft or requested changes."

                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."

                    analysis_performed: "Analysis Performed"
                        "Summarize the review analysis that led to the verdict."

                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize the parts of the draft the next owner must read first."

                    current_artifact: "Current Artifact"
                        "Name the artifact that remains current after review."

                    next_owner: "Next Owner"
                        "Name the next owner, including {{ReviewLead}} when the draft is accepted and {{DraftAuthor}} when the draft is rejected."

                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "Name the failing review gates in authored order."

                    trust_surface:
                        current_artifact

                    standalone_read: "Standalone Read"
                        "A downstream owner should be able to read this review alone and understand the verdict, current artifact, and next owner."
                """,
            },
        )

        rendered = render_markdown(agent)
        self.assertIn("## Outputs", rendered)
        self.assertIn("## Final Output", rendered)
        final_output_block = rendered.split("## Final Output", 1)[1]
        self.assertIn("### Draft Review Decision", final_output_block)
        self.assertIn("#### Trust Surface", final_output_block)
        self.assertIn("- Current Artifact", final_output_block)
        self.assertIn("#### Read on Its Own", final_output_block)


if __name__ == "__main__":
    unittest.main()
