from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class FinalOutputTests(unittest.TestCase):
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
                target_path.write_text(contents, encoding="utf-8")
            prompt = parse_file(prompt_path)
            return CompilationSession(prompt).compile_agent(agent_name)

    def _compile_error(
        self,
        source: str,
        *,
        agent_name: str,
        extra_files: dict[str, str] | None = None,
    ) -> CompileError:
        with self.assertRaises(CompileError) as ctx:
            self._compile_agent(
                source,
                agent_name=agent_name,
                extra_files=extra_files,
            )
        return ctx.exception

    def test_final_output_is_none_when_agent_does_not_declare_it(self) -> None:
        agent = self._compile_agent(
            """
            output SummaryReply: "Summary Reply"
                target: TurnResponse
                shape: CommentText
                requirement: Required

            agent HelloAgent:
                role: "Answer plainly."
                workflow: "Reply"
                    "Reply and stop."
                outputs: "Outputs"
                    SummaryReply
            """,
            agent_name="HelloAgent",
        )

        self.assertIsNone(agent.final_output)
        self.assertNotIn("## Final Output", render_markdown(agent))

    def test_prose_final_output_renders_dedicated_section_and_metadata(self) -> None:
        agent = self._compile_agent(
            """
            output FinalReply: "Final Reply"
                target: TurnResponse
                shape: CommentText
                requirement: Required

                format_notes: "Expected Structure"
                    "Lead with the shipped outcome."

                standalone_read: "Standalone Read"
                    "The user should understand what changed and what happens next."

            agent HelloAgent:
                role: "Answer plainly and end the turn."
                workflow: "Reply"
                    "Reply and stop."
                outputs: "Outputs"
                    FinalReply
                final_output: FinalReply
            """,
            agent_name="HelloAgent",
        )

        self.assertIsNotNone(agent.final_output)
        self.assertEqual(agent.final_output.format_mode, "prose")
        self.assertEqual(agent.final_output.output_name, "FinalReply")
        self.assertEqual(agent.final_output.shape_name, "CommentText")

        rendered = render_markdown(agent)
        self.assertIn("## Final Output", rendered)
        self.assertIn("### Final Reply", rendered)
        self.assertIn("| Message kind | Final assistant message |", rendered)
        self.assertIn("| Format | Natural-language markdown |", rendered)
        self.assertIn("#### Expected Structure", rendered)
        self.assertIn("#### Read It Cold", rendered)
        self.assertNotIn("## Outputs", rendered)

    def test_json_final_output_exposes_schema_metadata_and_payload_preview(self) -> None:
        agent = self._compile_agent(
            """
            json schema RepoStatusSchema: "Repo Status Schema"
                profile: OpenAIStructuredOutput
                file: "schemas/repo_status.schema.json"

            output shape RepoStatusJson: "Repo Status JSON"
                kind: JsonObject
                schema: RepoStatusSchema
                example_file: "examples/repo_status.example.json"

                explanation: "Field Notes"
                    "Use the schema fields exactly once."

            output RepoStatusFinalResponse: "Repo Status Final Response"
                target: TurnResponse
                shape: RepoStatusJson
                requirement: Required

                standalone_read: "Standalone Read"
                    "The final answer should stand on its own as one structured repo-status result."

            agent RepoStatusAgent:
                role: "Report repo status in structured form."
                workflow: "Summarize"
                    "Summarize the repo state and end with the declared final output."
                outputs: "Outputs"
                    RepoStatusFinalResponse
                final_output: RepoStatusFinalResponse
            """,
            agent_name="RepoStatusAgent",
            extra_files={
                "schemas/repo_status.schema.json": textwrap.dedent(
                    """\
                    {
                      "type": "object",
                      "additionalProperties": false,
                      "properties": {
                        "summary": {
                          "type": "string",
                          "description": "Short natural-language status."
                        },
                        "status": {
                          "type": "string",
                          "enum": ["ok", "action_required"],
                          "description": "Current repo outcome."
                        },
                        "next_step": {
                          "type": ["string", "null"],
                          "description": "Null only when no follow-up is needed."
                        }
                      }
                    }
                    """
                ),
                "examples/repo_status.example.json": textwrap.dedent(
                    """\
                    {
                      "summary": "Branch is clean and checks passed.",
                      "status": "ok",
                      "next_step": null
                    }
                    """
                ),
            },
        )

        self.assertIsNotNone(agent.final_output)
        self.assertEqual(agent.final_output.format_mode, "json_schema")
        self.assertEqual(agent.final_output.schema_name, "RepoStatusSchema")
        self.assertEqual(agent.final_output.schema_profile, "OpenAIStructuredOutput")
        self.assertEqual(agent.final_output.schema_file, "schemas/repo_status.schema.json")
        self.assertEqual(agent.final_output.example_file, "examples/repo_status.example.json")

        rendered = render_markdown(agent)
        self.assertIn("| Format | Structured JSON |", rendered)
        self.assertIn("| Schema | Repo Status Schema |", rendered)
        self.assertIn("| Profile | OpenAIStructuredOutput |", rendered)
        self.assertIn("#### Payload Shape", rendered)
        self.assertIn("| `next_step` | string \\| null | Null only when no follow-up is needed. |", rendered)
        self.assertIn("#### Example Shape", rendered)
        self.assertIn("```json", rendered)

    def test_json_final_output_requires_readable_schema_file(self) -> None:
        # Schema-backed final answers must fail loud when the declared schema file
        # cannot be read, or the rendered contract silently drops the payload shape.
        error = self._compile_error(
            """
            json schema RepoStatusSchema: "Repo Status Schema"
                profile: OpenAIStructuredOutput
                file: "schemas/missing_repo_status.schema.json"

            output shape RepoStatusJson: "Repo Status JSON"
                kind: JsonObject
                schema: RepoStatusSchema
                example_file: "examples/repo_status.example.json"

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
            """,
            agent_name="RepoStatusAgent",
            extra_files={
                "examples/repo_status.example.json": textwrap.dedent(
                    """\
                    {
                      "summary": "Branch is clean and checks passed.",
                      "status": "ok",
                      "next_step": null
                    }
                    """
                ),
            },
        )

        self.assertEqual(error.code, "E215")
        self.assertIn("missing or unreadable", str(error))
        self.assertIn("schemas/missing_repo_status.schema.json", str(error))

    def test_json_final_output_requires_valid_schema_json(self) -> None:
        # The final-output contract should fail before render when the declared
        # schema file is malformed, not silently degrade to metadata-only JSON.
        error = self._compile_error(
            """
            json schema RepoStatusSchema: "Repo Status Schema"
                profile: OpenAIStructuredOutput
                file: "schemas/repo_status.schema.json"

            output shape RepoStatusJson: "Repo Status JSON"
                kind: JsonObject
                schema: RepoStatusSchema
                example_file: "examples/repo_status.example.json"

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
            """,
            agent_name="RepoStatusAgent",
            extra_files={
                "schemas/repo_status.schema.json": "{not json",
                "examples/repo_status.example.json": textwrap.dedent(
                    """\
                    {
                      "summary": "Branch is clean and checks passed.",
                      "status": "ok",
                      "next_step": null
                    }
                    """
                ),
            },
        )

        self.assertEqual(error.code, "E216")
        self.assertIn("valid JSON object", str(error))
        self.assertIn("schemas/repo_status.schema.json", str(error))

    def test_json_final_output_requires_readable_example_file(self) -> None:
        # The example block is part of the user-visible final contract, so a
        # declared example file must fail loud instead of disappearing.
        error = self._compile_error(
            """
            json schema RepoStatusSchema: "Repo Status Schema"
                profile: OpenAIStructuredOutput
                file: "schemas/repo_status.schema.json"

            output shape RepoStatusJson: "Repo Status JSON"
                kind: JsonObject
                schema: RepoStatusSchema
                example_file: "examples/missing_repo_status.example.json"

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
            """,
            agent_name="RepoStatusAgent",
            extra_files={
                "schemas/repo_status.schema.json": textwrap.dedent(
                    """\
                    {
                      "type": "object",
                      "properties": {
                        "summary": {
                          "type": "string",
                          "description": "Short natural-language status."
                        }
                      }
                    }
                    """
                ),
            },
        )

        self.assertEqual(error.code, "E215")
        self.assertIn("missing or unreadable", str(error))
        self.assertIn("examples/missing_repo_status.example.json", str(error))

    def test_final_output_is_omitted_from_outputs_when_side_artifacts_remain(self) -> None:
        agent = self._compile_agent(
            """
            output FinalReply: "Final Reply"
                target: TurnResponse
                shape: CommentText
                requirement: Required

            output ReleaseNotesFile: "Release Notes File"
                target: File
                    path: "artifacts/RELEASE_NOTES.md"
                shape: MarkdownDocument
                requirement: Required

            agent ReleaseAgent:
                role: "Ship the change."
                workflow: "Ship"
                    "Ship and stop."
                outputs: "Outputs"
                    FinalReply
                    ReleaseNotesFile
                final_output: FinalReply
            """,
            agent_name="ReleaseAgent",
        )

        rendered = render_markdown(agent)
        self.assertIn("## Final Output", rendered)
        self.assertIn("## Outputs", rendered)
        self.assertIn("### Release Notes File", rendered)
        outputs_block = rendered.split("## Outputs", 1)[1].split("## Final Output", 1)[0]
        self.assertNotIn("### Final Reply", outputs_block)

    def test_final_output_can_flow_through_patched_outputs_block(self) -> None:
        # Child agents still emit the final TurnResponse contract even when the
        # output comes from an inherited outputs block patch. Hiding that output
        # from the ordinary Outputs section must not break inherited-key accounting.
        agent = self._compile_agent(
            """
            output FinalReply: "Final Reply"
                target: TurnResponse
                shape: CommentText
                requirement: Required

                standalone_read: "Standalone Read"
                    "The final answer should still render through a patched outputs block."

            output ReleaseNotesFile: "Release Notes File"
                target: File
                    path: "artifacts/RELEASE_NOTES.md"
                shape: MarkdownDocument
                requirement: Required

            outputs SharedOutputs: "Outputs"
                final_reply: "Final Reply"
                    FinalReply
                release_notes: "Release Notes File"
                    ReleaseNotesFile

            abstract agent BaseAgent:
                role: "Use shared outputs."
                outputs: SharedOutputs

            agent PatchedFinalAgent[BaseAgent]:
                role: "Patch shared outputs and still end with the final answer."
                workflow: "Ship"
                    "Ship and stop."
                outputs[SharedOutputs]: "Outputs"
                    inherit final_reply
                    inherit release_notes
                final_output: FinalReply
            """,
            agent_name="PatchedFinalAgent",
        )

        rendered = render_markdown(agent)
        self.assertIn("## Outputs", rendered)
        self.assertIn("## Final Output", rendered)
        outputs_block = rendered.split("## Outputs", 1)[1].split("## Final Output", 1)[0]
        self.assertNotIn("### Final Reply", outputs_block)
        self.assertIn("### Release Notes File", outputs_block)
        self.assertIn("### Final Reply", rendered.split("## Final Output", 1)[1])

    def test_final_output_can_use_imported_output_declaration(self) -> None:
        # Imported output declarations are a first-class reuse surface. The
        # dedicated final-output contract should still render when the chosen
        # TurnResponse output comes from an imported module.
        agent = self._compile_agent(
            """
            import shared.outputs

            agent ImportedFinalAgent:
                role: "Use an imported final output."
                workflow: "Reply"
                    "Reply and stop."
                outputs: "Outputs"
                    shared.outputs.ImportedFinalReply
                final_output: shared.outputs.ImportedFinalReply
            """,
            agent_name="ImportedFinalAgent",
            extra_files={
                "prompts/shared/outputs.prompt": textwrap.dedent(
                    """\
                    output ImportedFinalReply: "Imported Final Reply"
                        target: TurnResponse
                        shape: CommentText
                        requirement: Required

                        standalone_read: "Standalone Read"
                            "Imported final outputs should still render as the dedicated final answer contract."
                    """
                ),
            },
        )

        rendered = render_markdown(agent)
        self.assertIn("## Final Output", rendered)
        self.assertIn("### Imported Final Reply", rendered)
        self.assertIn("#### Read It Cold", rendered)
        self.assertNotIn("## Outputs", rendered)

    def test_review_driven_final_output_renders_dedicated_prose_contract(self) -> None:
        agent = self._compile_agent(
            """
            input DraftSpec: "Draft Spec"
                source: File
                    path: "unit_root/DRAFT_SPEC.md"
                shape: MarkdownDocument
                requirement: Required

            workflow DraftReviewContract: "Draft Review Contract"
                completeness: "Completeness"
                    "Confirm the draft covers the required sections."

            agent ReviewLead:
                role: "Own accepted drafts."
                workflow: "Follow Up"
                    "Take accepted drafts forward."

            agent DraftAuthor:
                role: "Fix rejected drafts."
                workflow: "Revise"
                    "Revise the rejected draft."

            output DraftReviewComment: "Draft Review Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required

                verdict: "Verdict"
                    "State whether the draft passed review."

                reviewed_artifact: "Reviewed Artifact"
                    "Name the reviewed artifact."

                analysis_performed: "Analysis Performed"
                    "Summarize the review analysis."

                output_contents_that_matter: "Output Contents That Matter"
                    "Summarize what the next owner should read first."

                current_artifact: "Current Artifact"
                    "Name the artifact that remains current after review."

                next_owner: "Next Owner"
                    "Name {{ReviewLead}} when accepted and {{DraftAuthor}} when rejected."

                failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                    failing_gates: "Failing Gates"
                        "List the failing review gates in authored order."

                trust_surface:
                    current_artifact

                standalone_read: "Standalone Read"
                    "A downstream owner should understand the review verdict, current artifact, and next owner from this output alone."

            review DraftReview: "Draft Review"
                subject: DraftSpec
                contract: DraftReviewContract
                comment_output: DraftReviewComment

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
                    current artifact DraftSpec via DraftReviewComment.current_artifact
                    route "Accepted draft returns to ReviewLead." -> ReviewLead

                on_reject: "If Rejected"
                    current artifact DraftSpec via DraftReviewComment.current_artifact
                    route "Rejected draft returns to DraftAuthor." -> DraftAuthor

            agent DraftReviewAgent:
                role: "Keep review final outputs aligned."
                review: DraftReview
                inputs: "Inputs"
                    DraftSpec
                outputs: "Outputs"
                    DraftReviewComment
                final_output: DraftReviewComment
            """,
            agent_name="DraftReviewAgent",
        )

        rendered = render_markdown(agent)
        self.assertIn("## Final Output", rendered)
        self.assertNotIn("## Outputs", rendered)
        self.assertIn("### Draft Review Comment", rendered)
        self.assertIn("#### Trust Surface", rendered)
        self.assertIn("- Current Artifact", rendered)
        self.assertIn("#### Failure Detail", rendered)
        self.assertIn("Rendered only when verdict is changes requested.", rendered)
        self.assertIn("#### Read It Cold", rendered)

    def test_review_driven_final_output_renders_schema_backed_json_contract(self) -> None:
        agent = self._compile_agent(
            """
            json schema AcceptanceReviewSchema: "Acceptance Review Schema"
                profile: OpenAIStructuredOutput
                file: "schemas/acceptance_review.schema.json"

            output shape AcceptanceReviewJson: "Acceptance Review JSON"
                kind: JsonObject
                schema: AcceptanceReviewSchema
                example_file: "examples/acceptance_review.example.json"

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

            output AcceptanceReviewResponse: "Acceptance Review Response"
                target: TurnResponse
                shape: AcceptanceReviewJson
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
                    "Name {{ReviewLead}} when accepted and {{PlanAuthor}} when rejected."

                failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                    failing_gates: "Failing Gates"
                        "List exact failing gates, including {{contract.outline_complete}} when it fails."

                trust_surface:
                    current_artifact

                standalone_read: "Standalone Read"
                    "A downstream owner should understand the acceptance verdict, current artifact, and next owner from this output alone."

            review AcceptanceReview: "Acceptance Review"
                subject: DraftPlan
                contract: PlanReviewContract
                comment_output: AcceptanceReviewResponse

                fields:
                    verdict: verdict
                    reviewed_artifact: reviewed_artifact
                    analysis: analysis_performed
                    readback: output_contents_that_matter
                    current_artifact: current_artifact
                    failing_gates: failure_detail.failing_gates
                    next_owner: next_owner

                contract_gate_checks: "Contract Gate Checks"
                    accept "The acceptance review contract passes." when contract.passes

                on_accept: "If Accepted"
                    current artifact DraftPlan via AcceptanceReviewResponse.current_artifact
                    route "Accepted plan returns to ReviewLead." -> ReviewLead

                on_reject: "If Rejected"
                    current artifact DraftPlan via AcceptanceReviewResponse.current_artifact
                    route "Rejected plan returns to PlanAuthor." -> PlanAuthor

            agent AcceptanceReviewAgent:
                role: "Keep schema-backed review final outputs aligned."
                review: AcceptanceReview
                inputs: "Inputs"
                    DraftPlan
                outputs: "Outputs"
                    AcceptanceReviewResponse
                final_output: AcceptanceReviewResponse
            """,
            agent_name="AcceptanceReviewAgent",
            extra_files={
                "schemas/acceptance_review.schema.json": textwrap.dedent(
                    """\
                    {
                      "type": "object",
                      "additionalProperties": false,
                      "properties": {
                        "verdict": {
                          "type": "string",
                          "enum": ["accepted", "changes_requested"],
                          "description": "Review verdict."
                        },
                        "reviewed_artifact": {
                          "type": "string",
                          "description": "Reviewed artifact name."
                        },
                        "next_owner": {
                          "type": "string",
                          "description": "Next owner after review."
                        }
                      }
                    }
                    """
                ),
                "examples/acceptance_review.example.json": textwrap.dedent(
                    """\
                    {
                      "verdict": "accepted",
                      "reviewed_artifact": "Draft Plan",
                      "next_owner": "ReviewLead"
                    }
                    """
                ),
            },
        )

        rendered = render_markdown(agent)
        self.assertIn("## Final Output", rendered)
        self.assertNotIn("## Outputs", rendered)
        self.assertIn("| Format | Structured JSON |", rendered)
        self.assertIn("| Schema | Acceptance Review Schema |", rendered)
        self.assertIn("#### Payload Shape", rendered)
        self.assertIn("| `verdict` | string | Review verdict. |", rendered)
        self.assertIn("#### Trust Surface", rendered)
        self.assertIn("- Current Artifact", rendered)
        self.assertIn("#### Failure Detail", rendered)
        self.assertIn("List exact failing gates, including Outline Complete when it fails.", rendered)

    def test_review_driven_final_output_can_split_from_comment_output(self) -> None:
        # Split review final outputs still need the same readable current-artifact
        # trust surface as the review comment, even though that field is bound by
        # review semantics rather than declared directly on the split output.
        agent = self._compile_agent(
            """
            input DraftSpec: "Draft Spec"
                source: File
                    path: "unit_root/DRAFT_SPEC.md"
                shape: MarkdownDocument
                requirement: Required

            workflow DraftReviewContract: "Draft Review Contract"
                completeness: "Completeness"
                    "Confirm the draft covers the required sections."

            agent ReviewLead:
                role: "Own accepted drafts."
                workflow: "Follow Up"
                    "Take accepted drafts forward."

            agent DraftAuthor:
                role: "Fix rejected drafts."
                workflow: "Revise"
                    "Revise the rejected draft."

            output DraftReviewComment: "Draft Review Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required

                verdict: "Verdict"
                    "State whether the draft passed review."

                reviewed_artifact: "Reviewed Artifact"
                    "Name the reviewed artifact."

                analysis_performed: "Analysis Performed"
                    "Summarize the review analysis."

                output_contents_that_matter: "Output Contents That Matter"
                    "Summarize what the next owner should read first."

                current_artifact: "Current Artifact"
                    "Name the artifact that remains current after review."

                next_owner: "Next Owner"
                    "Name {{ReviewLead}} when accepted and {{DraftAuthor}} when rejected."

                failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                    failing_gates: "Failing Gates"
                        "List the failing review gates in authored order."

                trust_surface:
                    current_artifact

                standalone_read: "Standalone Read"
                    "A downstream owner should understand the review verdict, current artifact, and next owner from this output alone."

            output DraftReviewDecision: "Draft Review Decision"
                target: TurnResponse
                shape: CommentText
                requirement: Required

                trust_surface:
                    current_artifact

                control_summary: "Control Summary"
                    "End with one short control summary for the routed owner."

                retry_note: "Retry Note" when verdict == ReviewVerdict.changes_requested:
                    "Only include this note when the review requests changes."

                current_alignment: "Current Artifact Alignment"
                    "Keep the control summary aligned with {{fields.current_artifact}}."

                standalone_read: "Standalone Read"
                    "The final control summary should stand on its own for the routed owner."

            review DraftReview: "Draft Review"
                subject: DraftSpec
                contract: DraftReviewContract
                comment_output: DraftReviewComment

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
                    current artifact DraftSpec via DraftReviewComment.current_artifact
                    route "Accepted draft returns to ReviewLead." -> ReviewLead

                on_reject: "If Rejected"
                    current artifact DraftSpec via DraftReviewComment.current_artifact
                    route "Rejected draft returns to DraftAuthor." -> DraftAuthor

            agent DraftReviewAgent:
                role: "Emit the rich review comment and a small final control summary."
                review: DraftReview
                inputs: "Inputs"
                    DraftSpec
                outputs: "Outputs"
                    DraftReviewComment
                    DraftReviewDecision
                final_output: DraftReviewDecision
            """,
            agent_name="DraftReviewAgent",
        )

        rendered = render_markdown(agent)
        self.assertIn("## Outputs", rendered)
        self.assertIn("## Final Output", rendered)
        outputs_block = rendered.split("## Outputs", 1)[1].split("## Final Output", 1)[0]
        final_output_block = rendered.split("## Final Output", 1)[1]
        self.assertIn("### Draft Review Comment", outputs_block)
        self.assertNotIn("### Draft Review Decision", outputs_block)
        self.assertIn("### Draft Review Decision", final_output_block)
        self.assertIn("#### Retry Note", final_output_block)
        self.assertIn("Rendered only when verdict is changes requested.", final_output_block)
        self.assertIn("Keep the control summary aligned with Current Artifact.", final_output_block)
        self.assertIn("#### Trust Surface", final_output_block)
        self.assertIn("- Current Artifact", final_output_block)
        self.assertIn("#### Read It Cold", final_output_block)

    def test_review_driven_split_final_output_can_render_route_semantics(self) -> None:
        agent = self._compile_agent(
            """
            input DraftSpec: "Draft Spec"
                source: File
                    path: "unit_root/DRAFT_SPEC.md"
                shape: MarkdownDocument
                requirement: Required

            workflow DraftReviewContract: "Draft Review Contract"
                completeness: "Completeness"
                    "Confirm the draft covers the required sections."

            agent ReviewLead:
                role: "Own accepted drafts."
                workflow: "Follow Up"
                    "Take accepted drafts forward."

            agent DraftAuthor:
                role: "Fix rejected drafts."
                workflow: "Revise"
                    "Revise the rejected draft."

            output DraftReviewComment: "Draft Review Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required

                verdict: "Verdict"
                    "State whether the draft passed review."

                reviewed_artifact: "Reviewed Artifact"
                    "Name the reviewed artifact."

                analysis_performed: "Analysis Performed"
                    "Summarize the review analysis."

                output_contents_that_matter: "Output Contents That Matter"
                    "Summarize what the next owner should read first."

                current_artifact: "Current Artifact"
                    "Name the artifact that remains current after review."

                next_owner: "Next Owner"
                    "Name {{ReviewLead}} when accepted and {{DraftAuthor}} when rejected."

                failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                    failing_gates: "Failing Gates"
                        "List the failing review gates in authored order."

                trust_surface:
                    current_artifact

                standalone_read: "Standalone Read"
                    "A downstream owner should understand the review verdict, current artifact, and next owner from this output alone."

            output DraftReviewDecision: "Draft Review Decision"
                target: TurnResponse
                shape: CommentText
                requirement: Required

                accepted_route: "Accepted Route" when verdict == ReviewVerdict.accept and route.exists:
                    "{{route.summary}}"

                retry_route: "Retry Route" when verdict == ReviewVerdict.changes_requested and route.exists:
                    "{{route.next_owner.title}}"

                standalone_read: "Standalone Read"
                    "The final control summary should stand on its own for the routed owner."

            review DraftReview: "Draft Review"
                subject: DraftSpec
                contract: DraftReviewContract
                comment_output: DraftReviewComment

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
                    current artifact DraftSpec via DraftReviewComment.current_artifact
                    route "Accepted draft returns to ReviewLead." -> ReviewLead

                on_reject: "If Rejected"
                    current artifact DraftSpec via DraftReviewComment.current_artifact
                    route "Rejected draft returns to DraftAuthor." -> DraftAuthor

            agent DraftReviewAgent:
                role: "Emit the review comment and a route-aware final control summary."
                review: DraftReview
                inputs: "Inputs"
                    DraftSpec
                outputs: "Outputs"
                    DraftReviewComment
                    DraftReviewDecision
                final_output: DraftReviewDecision
            """,
            agent_name="DraftReviewAgent",
        )

        rendered = render_markdown(agent)
        final_output_block = rendered.split("## Final Output", 1)[1]
        self.assertIn("#### Accepted Route", final_output_block)
        self.assertIn("Rendered only when verdict is accepted and a routed owner exists.", final_output_block)
        self.assertIn("Accepted draft returns to ReviewLead. Next owner: Review Lead.", final_output_block)
        self.assertIn("#### Retry Route", final_output_block)
        self.assertIn("Rendered only when verdict is changes requested and a routed owner exists.", final_output_block)
        self.assertIn("Draft Author", final_output_block)

    def test_review_driven_schema_backed_final_output_can_split_from_comment_output(self) -> None:
        # Schema-backed control outputs should keep the review's current-artifact
        # trust surface visible on the final JSON contract instead of rejecting it
        # just because the bound field lives on the review comment output.
        agent = self._compile_agent(
            """
            json schema AcceptanceControlSchema: "Acceptance Control Schema"
                profile: OpenAIStructuredOutput
                file: "schemas/acceptance_control.schema.json"

            output shape AcceptanceControlJson: "Acceptance Control JSON"
                kind: JsonObject
                schema: AcceptanceControlSchema
                example_file: "examples/acceptance_control.example.json"

                field_notes: "Field Notes"
                    "Keep `current_artifact` aligned with {{fields.current_artifact}}."
                    "Use `route` value `revise` only when {{contract.outline_complete}} fails."

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
                    "Name {{ReviewLead}} when accepted and {{PlanAuthor}} when rejected."

                failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                    failing_gates: "Failing Gates"
                        "List exact failing gates, including {{contract.outline_complete}} when it fails."

                trust_surface:
                    current_artifact

                standalone_read: "Standalone Read"
                    "A downstream owner should understand the acceptance verdict, current artifact, and next owner from this output alone."

            output AcceptanceControlFinalResponse: "Acceptance Control Final Response"
                target: TurnResponse
                shape: AcceptanceControlJson
                requirement: Required

                trust_surface:
                    current_artifact

                changes_requested_note: "Changes Requested Note" when verdict == ReviewVerdict.changes_requested:
                    "Only emit this retry control when the review requests changes."

                standalone_read: "Standalone Read"
                    "This final JSON should be enough for the next owner to route the review result."

            review AcceptanceReview: "Acceptance Review"
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
                    route "Accepted plan returns to ReviewLead." -> ReviewLead

                on_reject: "If Rejected"
                    current artifact DraftPlan via AcceptanceReviewComment.current_artifact
                    route "Rejected plan returns to PlanAuthor." -> PlanAuthor

            agent AcceptanceReviewAgent:
                role: "Emit the review comment and end with a control-only JSON result."
                review: AcceptanceReview
                inputs: "Inputs"
                    DraftPlan
                outputs: "Outputs"
                    AcceptanceReviewComment
                    AcceptanceControlFinalResponse
                final_output: AcceptanceControlFinalResponse
            """,
            agent_name="AcceptanceReviewAgent",
            extra_files={
                "schemas/acceptance_control.schema.json": textwrap.dedent(
                    """\
                    {
                      "type": "object",
                      "additionalProperties": false,
                      "properties": {
                        "route": {
                          "type": "string",
                          "enum": ["follow_up", "revise"],
                          "description": "Control route for the next owner."
                        },
                        "current_artifact": {
                          "type": "string",
                          "description": "Current artifact after review."
                        },
                        "next_owner": {
                          "type": "string",
                          "description": "Next owner after review."
                        }
                      }
                    }
                    """
                ),
                "examples/acceptance_control.example.json": textwrap.dedent(
                    """\
                    {
                      "route": "follow_up",
                      "current_artifact": "Draft Plan",
                      "next_owner": "ReviewLead"
                    }
                    """
                ),
            },
        )

        rendered = render_markdown(agent)
        self.assertIn("## Outputs", rendered)
        self.assertIn("## Final Output", rendered)
        outputs_block = rendered.split("## Outputs", 1)[1].split("## Final Output", 1)[0]
        final_output_block = rendered.split("## Final Output", 1)[1]
        self.assertIn("### Acceptance Review Comment", outputs_block)
        self.assertNotIn("### Acceptance Control Final Response", outputs_block)
        self.assertIn("### Acceptance Control Final Response", final_output_block)
        self.assertIn("| Schema | Acceptance Control Schema |", final_output_block)
        self.assertIn("#### Payload Shape", final_output_block)
        self.assertIn("#### Field Notes", final_output_block)
        self.assertIn("Keep `current_artifact` aligned with Current Artifact.", final_output_block)
        self.assertIn("Use `route` value `revise` only when Outline Complete fails.", final_output_block)
        self.assertIn("#### Changes Requested Note", final_output_block)
        self.assertIn("Rendered only when verdict is changes requested.", final_output_block)
        self.assertIn("#### Trust Surface", final_output_block)
        self.assertIn("- Current Artifact", final_output_block)

    def test_review_driven_split_json_final_output_can_render_route_semantics(self) -> None:
        agent = self._compile_agent(
            """
            json schema AcceptanceControlSchema: "Acceptance Control Schema"
                profile: OpenAIStructuredOutput
                file: "schemas/acceptance_control.schema.json"

            output shape AcceptanceControlJson: "Acceptance Control JSON"
                kind: JsonObject
                schema: AcceptanceControlSchema
                example_file: "examples/acceptance_control.example.json"

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
                    "Name {{ReviewLead}} when accepted and {{PlanAuthor}} when rejected."

                failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                    failing_gates: "Failing Gates"
                        "List exact failing gates, including {{contract.outline_complete}} when it fails."

                trust_surface:
                    current_artifact

                standalone_read: "Standalone Read"
                    "A downstream owner should understand the acceptance verdict, current artifact, and next owner from this output alone."

            output AcceptanceControlFinalResponse: "Acceptance Control Final Response"
                target: TurnResponse
                shape: AcceptanceControlJson
                requirement: Required

                accepted_route: "Accepted Route" when verdict == ReviewVerdict.accept and route.exists:
                    "{{route.summary}}"

                retry_route: "Retry Route" when verdict == ReviewVerdict.changes_requested and route.exists:
                    "{{route.next_owner.key}}"

                standalone_read: "Standalone Read"
                    "This final JSON should be enough for the next owner to route the review result."

            review AcceptanceReview: "Acceptance Review"
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
                    route "Accepted plan returns to ReviewLead." -> ReviewLead

                on_reject: "If Rejected"
                    current artifact DraftPlan via AcceptanceReviewComment.current_artifact
                    route "Rejected plan returns to PlanAuthor." -> PlanAuthor

            agent AcceptanceReviewAgent:
                role: "Emit the review comment and end with a route-aware JSON control result."
                review: AcceptanceReview
                inputs: "Inputs"
                    DraftPlan
                outputs: "Outputs"
                    AcceptanceReviewComment
                    AcceptanceControlFinalResponse
                final_output: AcceptanceControlFinalResponse
            """,
            agent_name="AcceptanceReviewAgent",
            extra_files={
                "schemas/acceptance_control.schema.json": textwrap.dedent(
                    """\
                    {
                      "type": "object",
                      "additionalProperties": false,
                      "properties": {
                        "route": {
                          "type": "string",
                          "enum": ["follow_up", "revise"],
                          "description": "Control route for the next owner."
                        },
                        "current_artifact": {
                          "type": "string",
                          "description": "Current artifact after review."
                        },
                        "next_owner": {
                          "type": "string",
                          "description": "Next owner after review."
                        }
                      }
                    }
                    """
                ),
                "examples/acceptance_control.example.json": textwrap.dedent(
                    """\
                    {
                      "route": "follow_up",
                      "current_artifact": "Draft Plan",
                      "next_owner": "ReviewLead"
                    }
                    """
                ),
            },
        )

        rendered = render_markdown(agent)
        final_output_block = rendered.split("## Final Output", 1)[1]
        self.assertIn("#### Accepted Route", final_output_block)
        self.assertIn("Rendered only when verdict is accepted and a routed owner exists.", final_output_block)
        self.assertIn("Accepted plan returns to ReviewLead. Next owner: Review Lead.", final_output_block)
        self.assertIn("#### Retry Route", final_output_block)
        self.assertIn("Rendered only when verdict is changes requested and a routed owner exists.", final_output_block)
        self.assertIn("PlanAuthor", final_output_block)

    def test_final_output_requires_output_declaration(self) -> None:
        error = self._compile_error(
            """
            schema ReleaseSchema: "Release Schema"
                sections:
                    summary: "Summary"
                        "Provide a summary."

            agent InvalidAgent:
                role: "Try to point final_output at a schema."
                workflow: "Reply"
                    "Reply and stop."
                final_output: ReleaseSchema
            """,
            agent_name="InvalidAgent",
        )

        self.assertEqual(error.code, "E211")
        self.assertIn("final_output", str(error))
        self.assertIn("schema declaration", str(error))

    def test_final_output_must_be_emitted_by_outputs_contract(self) -> None:
        error = self._compile_error(
            """
            output FinalReply: "Final Reply"
                target: TurnResponse
                shape: CommentText
                requirement: Required

            agent InvalidAgent:
                role: "Forget to emit the declared final output."
                workflow: "Reply"
                    "Reply and stop."
                final_output: FinalReply
            """,
            agent_name="InvalidAgent",
        )

        self.assertEqual(error.code, "E212")
        self.assertIn("not emitted by the concrete turn", str(error))

    def test_final_output_rejects_file_outputs(self) -> None:
        error = self._compile_error(
            """
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
            """,
            agent_name="InvalidAgent",
        )

        self.assertEqual(error.code, "E213")
        self.assertIn("TurnResponse", str(error))

    def test_final_output_rejects_non_turn_response_targets(self) -> None:
        error = self._compile_error(
            """
            output target TrackerComment: "Tracker Comment"
                required: "Required Target Keys"
                    issue: "Issue"

            output TrackerReply: "Tracker Reply"
                target: TrackerComment
                    issue: "CURRENT_ISSUE"
                shape: CommentText
                requirement: Required

            agent InvalidAgent:
                role: "Try to end with a tracker comment."
                workflow: "Reply"
                    "Reply and stop."
                outputs: "Outputs"
                    TrackerReply
                final_output: TrackerReply
            """,
            agent_name="InvalidAgent",
        )

        self.assertEqual(error.code, "E213")
        self.assertIn("another target", str(error))

if __name__ == "__main__":
    unittest.main()
