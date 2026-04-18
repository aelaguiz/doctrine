from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine import model
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file, parse_text
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

    def test_parser_builds_final_output_route_binding(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """
            output schema WriterDecisionSchema: "Writer Decision Schema"
                route field next_route: "Next Route"
                    seek_muse: "Send to Muse." -> Muse
                    ready_for_critic: "Send to Critic." -> Critic

            output shape WriterDecisionJson: "Writer Decision JSON"
                kind: JsonObject
                schema: WriterDecisionSchema

            output WriterDecision: "Writer Decision"
                target: TurnResponse
                shape: WriterDecisionJson
                requirement: Required

            agent Writer:
                role: "Write the next turn."
                outputs: "Outputs"
                    WriterDecision
                final_output:
                    output: WriterDecision
                    route: next_route
            """
            )
        )

        agent_decl = prompt.declarations[-1]
        self.assertIsInstance(agent_decl, model.Agent)
        final_output = next(
            field for field in agent_decl.fields if isinstance(field, model.FinalOutputField)
        )
        self.assertEqual(final_output.value.declaration_name, "WriterDecision")
        self.assertEqual(final_output.route_path, ("next_route",))

    def test_parser_rejects_duplicate_final_output_route_binding(self) -> None:
        with self.assertRaisesRegex(
            Exception,
            "final_output block may define `route:` only once",
        ):
            parse_text(
                textwrap.dedent(
                    """
                output FinalReply: "Final Reply"
                    target: TurnResponse
                    shape: CommentText
                    requirement: Required

                agent Writer:
                    role: "Write the next turn."
                    outputs: "Outputs"
                        FinalReply
                    final_output:
                        output: FinalReply
                        route: next_route
                        route: retry_route
                """
                    )
            )

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
        self.assertIn("| Message type | Final assistant message |", rendered)
        self.assertIn("| Format | Natural-language markdown |", rendered)
        self.assertIn("#### Expected Structure", rendered)
        self.assertIn("#### Read on Its Own", rendered)
        self.assertNotIn("## Outputs", rendered)

    def test_route_field_final_output_emits_selector_metadata_and_keeps_route_semantics_local(self) -> None:
        agent = self._compile_agent(
            """
            output schema WriterDecisionSchema: "Writer Decision Schema"
                route field next_route: "Next Route"
                    seek_muse: "Send to Muse." -> Muse
                    ready_for_critic: "Send to Critic." -> Critic
                    nullable

                field summary: "Summary"
                    type: string

            output shape WriterDecisionJson: "Writer Decision JSON"
                kind: JsonObject
                schema: WriterDecisionSchema

            output WriterDecision: "Writer Decision"
                target: TurnResponse
                shape: WriterDecisionJson
                requirement: Required

                muse_route: "Muse Route" when route.choice == WriterDecisionSchema.next_route.seek_muse:
                    "{{route.summary}}"

                critic_route: "Critic Route" when route.choice == WriterDecisionSchema.next_route.ready_for_critic:
                    "{{route.next_owner}}"

            output OtherReply: "Other Reply"
                target: TurnResponse
                shape: Comment
                requirement: Required

            agent Muse:
                role: "Help the writer."
                workflow: "Muse"
                    "Offer fresh direction."

            agent Critic:
                role: "Judge the draft."
                workflow: "Critic"
                    "Judge the draft."

            agent Writer:
                role: "Write the next turn."
                workflow: "Write"
                    "Write the next turn."
                outputs: "Outputs"
                    WriterDecision
                    OtherReply
                final_output:
                    output: WriterDecision
                    route: next_route
            """,
            agent_name="Writer",
        )

        self.assertIsNotNone(agent.route)
        self.assertTrue(agent.route.exists)
        self.assertEqual(agent.route.behavior, "conditional")
        self.assertTrue(agent.route.has_unrouted_branch)
        self.assertIsNotNone(agent.route.selector)
        self.assertEqual(agent.route.selector.surface, "final_output")
        self.assertEqual(agent.route.selector.field_path, ("next_route",))
        self.assertEqual(agent.route.selector.null_behavior, "no_route")
        self.assertEqual(
            [member.member_key for member in agent.route.branches[0].choice_members],
            ["seek_muse"],
        )
        self.assertIsNone(agent.route.branches[0].choice_members[0].enum_name)

        rendered = render_markdown(agent)
        final_output_block = rendered.split("## Final Output", 1)[1]
        outputs_block = rendered.split("## Outputs", 1)[1].split("## Final Output", 1)[0]
        self.assertIn(
            "Show this only when route.choice is WriterDecisionSchema.next_route.seek_muse.",
            final_output_block,
        )
        self.assertIn(
            "Show this only when route.choice is WriterDecisionSchema.next_route.ready_for_critic.",
            final_output_block,
        )
        self.assertNotIn("### Writer Decision", outputs_block)
        self.assertIn("### Other Reply", outputs_block)

    def test_final_output_route_requires_structured_output_schema(self) -> None:
        error = self._compile_error(
            """
            output FinalReply: "Final Reply"
                target: TurnResponse
                shape: CommentText
                requirement: Required

            agent Writer:
                role: "Write the next turn."
                workflow: "Write"
                    "Write the next turn."
                outputs: "Outputs"
                    FinalReply
                final_output:
                    output: FinalReply
                    route: next_route
            """,
            agent_name="Writer",
        )

        self.assertIn("final_output.route requires a structured final output", str(error))

    def test_final_output_route_requires_route_field_binding(self) -> None:
        error = self._compile_error(
            """
            output schema WriterDecisionSchema: "Writer Decision Schema"
                field next_route: "Next Route"
                    type: string

            output shape WriterDecisionJson: "Writer Decision JSON"
                kind: JsonObject
                schema: WriterDecisionSchema

            output WriterDecision: "Writer Decision"
                target: TurnResponse
                shape: WriterDecisionJson
                requirement: Required

            agent Writer:
                role: "Write the next turn."
                workflow: "Write"
                    "Write the next turn."
                outputs: "Outputs"
                    WriterDecision
                final_output:
                    output: WriterDecision
                    route: next_route
            """,
            agent_name="Writer",
        )

        self.assertIn("final_output.route must bind a `route field`", str(error))

    def test_inherited_prose_final_output_renders_dedicated_section_and_metadata(self) -> None:
        agent = self._compile_agent(
            """
            output BaseReply: "Base Reply"
                target: TurnResponse
                shape: CommentText
                requirement: Required

                standalone_read: "Standalone Read"
                    "The user should understand what changed and what happens next."

            output FinalReply[BaseReply]: "Final Reply"
                inherit target
                inherit shape
                inherit requirement
                inherit standalone_read

                format_notes: "Expected Structure"
                    "Lead with the shipped outcome."

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
        self.assertEqual(agent.final_output.output_name, "FinalReply")

        rendered = render_markdown(agent)
        self.assertIn("## Final Output", rendered)
        self.assertIn("### Final Reply", rendered)
        self.assertIn("| Format | Natural-language markdown |", rendered)
        self.assertIn("#### Expected Structure", rendered)
        self.assertIn("#### Read on Its Own", rendered)

    def test_inherited_final_output_keeps_inherited_trust_surface_and_standalone_read(self) -> None:
        agent = self._compile_agent(
            """
            output BaseReply: "Base Reply"
                target: TurnResponse
                shape: Comment
                requirement: Required

                current_artifact: "Current Artifact"
                    "Name the artifact that stays current."

                trust_surface:
                    current_artifact

                standalone_read: "Standalone Read"
                    "This final reply should stand on its own."

            output FinalReply[BaseReply]: "Final Reply"
                inherit target
                inherit shape
                inherit requirement
                inherit current_artifact
                inherit trust_surface
                inherit standalone_read

                format_notes: "Expected Structure"
                    "Lead with the shipped outcome."

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

        rendered = render_markdown(agent)
        self.assertIn("## Final Output", rendered)
        self.assertNotIn("## Outputs", rendered)
        self.assertIn("### Final Reply", rendered)
        self.assertIn("#### Trust Surface", rendered)
        self.assertIn("- Current Artifact", rendered)
        self.assertIn("#### Read on Its Own", rendered)

    def test_json_final_output_exposes_schema_metadata_and_payload_preview(self) -> None:
        agent = self._compile_agent(
            """
            output schema RepoStatusSchema: "Repo Status Schema"
                field summary: "Summary"
                    type: string
                    note: "Short natural-language status."

                field status: "Status"
                    type: enum
                    values:
                        ok
                        action_required
                    note: "Current repo outcome."

                field next_step: "Next Step"
                    type: string
                    nullable
                    note: "Null only when no follow-up is needed."

                example:
                    summary: "Branch is clean and checks passed."
                    status: "ok"
                    next_step: null

            output shape RepoStatusJson: "Repo Status JSON"
                kind: JsonObject
                schema: RepoStatusSchema

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
        )

        self.assertIsNotNone(agent.final_output)
        self.assertEqual(agent.final_output.format_mode, "json_object")
        self.assertEqual(agent.final_output.schema_name, "RepoStatusSchema")
        self.assertEqual(agent.final_output.schema_profile, "OpenAIStructuredOutput")
        self.assertEqual(
            agent.final_output.generated_schema_relpath,
            "schemas/repo_status_final_response.schema.json",
        )
        self.assertIsNotNone(agent.final_output.lowered_schema)

        rendered = render_markdown(agent)
        self.assertIn("| Format | Structured JSON |", rendered)
        self.assertIn("| Schema | Repo Status Schema |", rendered)
        self.assertIn("| Profile | OpenAIStructuredOutput |", rendered)
        self.assertIn(
            "| Generated Schema | `schemas/repo_status_final_response.schema.json` |",
            rendered,
        )
        self.assertIn("#### Payload Fields", rendered)
        self.assertIn(
            "| `next_step` | string | Yes | Yes | Null only when no follow-up is needed. |",
            rendered,
        )
        self.assertIn("#### Example", rendered)
        self.assertIn("```json", rendered)

    def test_json_final_output_accepts_nullable_enum_and_const_examples(self) -> None:
        # Nullable enum and const fields are valid structured-output shapes.
        # Their declared example must validate and the rendered row must stay readable.
        agent = self._compile_agent(
            """
            output schema StatusSchema: "Status Schema"
                field status: "Status"
                    type: enum
                    values:
                        ok
                        blocked
                    nullable

                field kind: "Kind"
                    type: string
                    const: status_result
                    nullable

                example:
                    status: null
                    kind: null

            output shape StatusJson: "Status JSON"
                kind: JsonObject
                schema: StatusSchema

            output StatusFinalResponse: "Status Final Response"
                target: TurnResponse
                shape: StatusJson
                requirement: Required

            agent StatusAgent:
                role: "Report status in structured form."
                outputs: "Outputs"
                    StatusFinalResponse
                final_output: StatusFinalResponse
            """,
            agent_name="StatusAgent",
        )

        self.assertIsNotNone(agent.final_output)
        self.assertIsNotNone(agent.final_output.lowered_schema)
        properties = agent.final_output.lowered_schema["properties"]
        self.assertEqual(properties["status"]["enum"], ["ok", "blocked", None])

        rendered = render_markdown(agent)
        self.assertIn("| `status` | string | Yes | Yes | One of `ok`, `blocked`. |", rendered)
        self.assertIn("| `kind` | string | Yes | Yes |  |", rendered)

    def test_json_final_output_renders_nested_object_payload_rows(self) -> None:
        # Nested payload objects are part of the public final-output contract.
        # The rendered table should expose child fields instead of hiding them.
        agent = self._compile_agent(
            """
            output schema RoutedSchema: "Routed Schema"
                field summary: "Summary"
                    type: string
                    note: "Short user-facing summary."

                field route: "Route"
                    type: object
                    note: "Routing facts for the next step."

                    field action: "Action"
                        type: enum
                        values:
                            reply
                            handoff
                            end_turn
                        note: "Chosen route action."

                    field owner: "Owner"
                        type: string
                        nullable
                        note: "Next owner when a handoff is needed."

                    field reason: "Reason"
                        type: string
                        note: "Why this route was chosen."

                example:
                    summary: "Route this to the reviewer."
                    route:
                        action: "handoff"
                        owner: "Reviewer"
                        reason: "A review is required."

            output shape RoutedJson: "Routed JSON"
                kind: JsonObject
                schema: RoutedSchema

            output RoutedFinalResponse: "Routed Final Response"
                target: TurnResponse
                shape: RoutedJson
                requirement: Required

            agent RoutedAgent:
                role: "Route work in structured form."
                outputs: "Outputs"
                    RoutedFinalResponse
                final_output: RoutedFinalResponse
            """,
            agent_name="RoutedAgent",
        )

        rendered = render_markdown(agent)
        self.assertIn(
            "| `route` | object | Yes | No | Routing facts for the next step. |",
            rendered,
        )
        self.assertIn("| `route.action` | string | Yes | No | Chosen route action. |", rendered)
        self.assertIn(
            "| `route.owner` | string | Yes | Yes | Next owner when a handoff is needed. |",
            rendered,
        )
        self.assertIn("| `route.reason` | string | Yes | No | Why this route was chosen. |", rendered)

    def test_json_final_output_requires_example_that_matches_lowered_schema(self) -> None:
        # The final-output example is compiler-owned proof, so it must satisfy
        # the lowered schema instead of living in an external JSON file.
        error = self._compile_error(
            """
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
            """,
            agent_name="RepoStatusAgent",
        )

        self.assertEqual(error.code, "E216")
        self.assertIn("does not match the lowered schema", str(error))

    def test_json_final_output_keeps_legacy_inline_enum_form_compatible(self) -> None:
        agent = self._compile_agent(
            """
            output schema LegacyStatusSchema: "Legacy Status Schema"
                field status: "Status"
                    type: string
                    enum:
                        ok
                        blocked

            output shape LegacyStatusJson: "Legacy Status JSON"
                kind: JsonObject
                schema: LegacyStatusSchema

            output LegacyStatusFinalResponse: "Legacy Status Final Response"
                target: TurnResponse
                shape: LegacyStatusJson
                requirement: Required

            agent LegacyStatusAgent:
                role: "Report status in the legacy enum form."
                outputs: "Outputs"
                    LegacyStatusFinalResponse
                final_output: LegacyStatusFinalResponse
            """,
            agent_name="LegacyStatusAgent",
        )

        self.assertIsNotNone(agent.final_output)
        self.assertIsNotNone(agent.final_output.lowered_schema)
        self.assertEqual(
            agent.final_output.lowered_schema["properties"]["status"]["enum"],
            ["ok", "blocked"],
        )

    def test_json_final_output_allows_missing_schema_owned_example(self) -> None:
        # Structured final-output contracts may omit `example:`. The rendered
        # contract should still expose the payload shape and skip the example
        # block instead of failing at compile time.
        agent = self._compile_agent(
            """
            output schema RepoStatusSchema: "Repo Status Schema"
                field summary: "Summary"
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
            """,
            agent_name="RepoStatusAgent",
        )

        self.assertIsNotNone(agent.final_output)
        self.assertEqual(agent.final_output.format_mode, "json_object")
        self.assertIsNotNone(agent.final_output.lowered_schema)

        rendered = render_markdown(agent)
        # Missing sample data must not erase the user-visible payload contract.
        self.assertIn("#### Payload Fields", rendered)
        self.assertNotIn("#### Example", rendered)
        self.assertNotIn("```json", rendered)

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
            from shared.outputs import ImportedFinalReply

            agent ImportedFinalAgent:
                role: "Use an imported final output."
                workflow: "Reply"
                    "Reply and stop."
                outputs: "Outputs"
                    ImportedFinalReply
                final_output: ImportedFinalReply
            """,
            agent_name="ImportedFinalAgent",
            extra_files={
                "prompts/shared/outputs/AGENTS.prompt": textwrap.dedent(
                    """\
                    export output ImportedFinalReply: "Imported Final Reply"
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
        self.assertIn("#### Read on Its Own", rendered)
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
        self.assertIn("Show this only when verdict is changes requested.", rendered)
        self.assertIn("#### Read on Its Own", rendered)

    def test_review_driven_final_output_renders_schema_backed_json_contract(self) -> None:
        agent = self._compile_agent(
            """
            output schema AcceptanceReviewSchema: "Acceptance Review Schema"
                field verdict: "Verdict"
                    type: enum
                    values:
                        accepted
                        changes_requested
                    note: "Review verdict."

                field reviewed_artifact: "Reviewed Artifact"
                    type: string
                    note: "Reviewed artifact name."

                field next_owner: "Next Owner"
                    type: string
                    note: "Next owner after review."

                example:
                    verdict: "accepted"
                    reviewed_artifact: "Draft Plan"
                    next_owner: "ReviewLead"

            output shape AcceptanceReviewJson: "Acceptance Review JSON"
                kind: JsonObject
                schema: AcceptanceReviewSchema

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
        )

        rendered = render_markdown(agent)
        self.assertIn("## Final Output", rendered)
        self.assertNotIn("## Outputs", rendered)
        self.assertIn("| Format | Structured JSON |", rendered)
        self.assertIn("| Schema | Acceptance Review Schema |", rendered)
        self.assertIn("#### Payload Fields", rendered)
        self.assertIn("| `verdict` | string | Yes | No | Review verdict. |", rendered)
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
        self.assertIn("Show this only when verdict is changes requested.", final_output_block)
        self.assertIn("Keep the control summary aligned with Current Artifact.", final_output_block)
        self.assertIn("#### Trust Surface", final_output_block)
        self.assertIn("- Current Artifact", final_output_block)
        self.assertIn("#### Read on Its Own", final_output_block)

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
        self.assertIn("Show this only when verdict is accepted and a routed owner exists.", final_output_block)
        self.assertIn("Accepted draft returns to ReviewLead. Next owner: Review Lead.", final_output_block)
        self.assertIn("#### Retry Route", final_output_block)
        self.assertIn("Show this only when verdict is changes requested and a routed owner exists.", final_output_block)
        self.assertIn("Draft Author", final_output_block)

    def test_review_driven_schema_backed_final_output_can_split_from_comment_output(self) -> None:
        # Schema-backed control outputs should keep the review's current-artifact
        # trust surface visible on the final JSON contract instead of rejecting it
        # just because the bound field lives on the review comment output.
        agent = self._compile_agent(
            """
            output schema AcceptanceControlSchema: "Acceptance Control Schema"
                field route: "Route"
                    type: enum
                    values:
                        follow_up
                        revise
                    note: "Control route for the next owner."

                field current_artifact: "Current Artifact"
                    type: string
                    note: "Current artifact after review."

                field next_owner: "Next Owner"
                    type: string
                    note: "Next owner after review."

                example:
                    route: "follow_up"
                    current_artifact: "Draft Plan"
                    next_owner: "ReviewLead"

            output shape AcceptanceControlJson: "Acceptance Control JSON"
                kind: JsonObject
                schema: AcceptanceControlSchema

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
        self.assertIn("#### Payload Fields", final_output_block)
        self.assertIn("#### Field Notes", final_output_block)
        self.assertIn("Keep `current_artifact` aligned with Current Artifact.", final_output_block)
        self.assertIn("Use `route` value `revise` only when Outline Complete fails.", final_output_block)
        self.assertIn("#### Changes Requested Note", final_output_block)
        self.assertIn("Show this only when verdict is changes requested.", final_output_block)
        self.assertIn("#### Trust Surface", final_output_block)
        self.assertIn("- Current Artifact", final_output_block)

    def test_review_driven_split_json_final_output_can_render_route_semantics(self) -> None:
        agent = self._compile_agent(
            """
            output schema AcceptanceControlSchema: "Acceptance Control Schema"
                field route: "Route"
                    type: enum
                    values:
                        follow_up
                        revise
                    note: "Control route for the next owner."

                field current_artifact: "Current Artifact"
                    type: string
                    note: "Current artifact after review."

                field next_owner: "Next Owner"
                    type: string
                    note: "Next owner after review."

                example:
                    route: "follow_up"
                    current_artifact: "Draft Plan"
                    next_owner: "ReviewLead"

            output shape AcceptanceControlJson: "Acceptance Control JSON"
                kind: JsonObject
                schema: AcceptanceControlSchema

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
        )

        rendered = render_markdown(agent)
        final_output_block = rendered.split("## Final Output", 1)[1]
        self.assertIn("#### Accepted Route", final_output_block)
        self.assertIn("Show this only when verdict is accepted and a routed owner exists.", final_output_block)
        self.assertIn("Accepted plan returns to ReviewLead. Next owner: Review Lead.", final_output_block)
        self.assertIn("#### Retry Route", final_output_block)
        self.assertIn("Show this only when verdict is changes requested and a routed owner exists.", final_output_block)
        self.assertIn("PlanAuthor", final_output_block)

    def test_split_final_output_route_reads_still_need_route_exists_on_blocked_review_branches(self) -> None:
        # A changes-requested verdict can still include blocked review branches
        # with no route. Guarding only on the verdict is not enough to make
        # route.* reads safe on the split final-output contract.
        error = self._compile_error(
            """
            input DraftPlan: "Draft Plan"
                source: File
                    path: "unit_root/DRAFT_PLAN.md"
                shape: MarkdownDocument
                requirement: Required
                basis_missing: "Basis Missing"
                outline_missing: "Outline Missing"

            schema PlanReviewContract: "Plan Review Contract"
                sections:
                    summary: "Summary"
                        "Summarize the reviewed plan."

                gates:
                    outline_complete: "Outline Complete"
                        "Confirm the reviewed plan includes the outline."

            agent ReviewLead:
                role: "Own accepted plan follow-up."
                workflow: "Follow Up"
                    "Take the accepted plan to the next step."

            agent PlanAuthor:
                role: "Repair non-blocked plan defects."
                workflow: "Revise"
                    "Revise the same plan when review requests changes."

            output AcceptanceReviewComment: "Acceptance Review Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required

                verdict: "Verdict"
                    "State whether the plan passed review or asked for changes."

                reviewed_artifact: "Reviewed Artifact"
                    "Name the reviewed artifact."

                analysis_performed: "Analysis Performed"
                    "Summarize the review analysis."

                output_contents_that_matter: "Output Contents That Matter"
                    "State what the next owner should read first."

                current_artifact: "Current Artifact" when present(current_artifact):
                    "Name the artifact that remains current after review."

                next_owner: "Next Owner" when present(next_owner):
                    "Name {{ReviewLead}} when the review accepts the plan and {{PlanAuthor}} when the review requests changes without a blocked gate."

                failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                    blocked_gate: "Blocked Gate" when present(blocked_gate):
                        "Name the blocking gate when review stopped before the normal content check."

                    failing_gates: "Failing Gates"
                        "List exact failing gates in authored order."

                trust_surface:
                    current_artifact

            output AcceptanceControlFinalResponse: "Acceptance Control Final Response"
                target: TurnResponse
                shape: CommentText
                requirement: Required

                retry_route: "Retry Route" when verdict == ReviewVerdict.changes_requested:
                    "{{route.summary}}"

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
                    blocked_gate: failure_detail.blocked_gate
                    next_owner: next_owner

                basis_checks: "Basis Checks"
                    block "The review basis is missing." when DraftPlan.basis_missing

                contract_checks: "Contract Checks"
                    reject contract.outline_complete when DraftPlan.outline_missing
                    accept "The acceptance review contract passes." when contract.passes

                on_accept: "If Accepted"
                    current artifact DraftPlan via AcceptanceReviewComment.current_artifact
                    route "Accepted plan goes to ReviewLead." -> ReviewLead

                on_reject: "If Rejected"
                    current none when present(blocked_gate)
                    current artifact DraftPlan via AcceptanceReviewComment.current_artifact when missing(blocked_gate)
                    route "Rejected plan goes to PlanAuthor." -> PlanAuthor when missing(blocked_gate)

            agent AcceptanceReviewSplitPartialDemo:
                role: "Emit the review comment and end with a small partial result."
                review: AcceptanceReview
                inputs: "Inputs"
                    DraftPlan
                outputs: "Outputs"
                    AcceptanceReviewComment
                    AcceptanceControlFinalResponse
                final_output: AcceptanceControlFinalResponse
            """,
            agent_name="AcceptanceReviewSplitPartialDemo",
        )

        self.assertIn("route semantics are not live on every branch", str(error))
        self.assertIn("AcceptanceControlFinalResponse.retry_route", str(error))
        self.assertIn("guard the read with `route.exists`", str(error))

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

    def test_final_output_missing_local_shape_ref_fails_loud(self) -> None:
        error = self._compile_error(
            """
            output FinalReply: "Final Reply"
                target: TurnResponse
                shape: MissingShape
                requirement: Required

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

        self.assertEqual(error.code, "E276")
        self.assertIn("Missing local declaration reference", str(error))
        self.assertIn(
            "Output shape declaration `MissingShape` does not exist in the current module.",
            str(error),
        )

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
        self.assertIn("not one `TurnResponse` assistant message", str(error))

    def test_handoff_routing_final_output_can_bind_route_fields(self) -> None:
        agent = self._compile_agent(
            """
            output schema TurnResultSchema: "Turn Result Schema"
                field next_owner: "Next Owner"
                    type: string
                    note: "The routed next owner key."

                field summary: "Summary"
                    type: string
                    note: "Short closeout summary."

                example:
                    next_owner: "ReviewLead"
                    summary: "Hand off to ReviewLead."

            output shape TurnResultJson: "Turn Result JSON"
                kind: JsonObject
                schema: TurnResultSchema

            agent ReviewLead:
                role: "Own routed follow-up."
                workflow: "Follow Up"
                    "Take the routed follow-up."

            output TurnResultFinalResponse: "Turn Result Final Response"
                target: TurnResponse
                shape: TurnResultJson
                requirement: Required

                next_owner: route.next_owner.key

                route_summary: "Route Summary"
                    "{{route.summary}}"

                standalone_read: "Standalone Read"
                    "This final JSON should stand on its own."

            agent HandoffFinalOutputDemo:
                role: "End with a route-aware final JSON result."
                outputs: "Outputs"
                    TurnResultFinalResponse
                final_output: TurnResultFinalResponse

                handoff_routing: "Handoff Routing"
                    "Route through compiler-owned handoff routing."

                    law:
                        active when true
                        stop "Hand off or finish the turn."
                        route "Hand off to ReviewLead." -> ReviewLead
            """,
            agent_name="HandoffFinalOutputDemo",
        )

        self.assertIsNotNone(agent.final_output)
        rendered = render_markdown(agent)
        final_output_block = rendered.split("## Final Output", 1)[1]
        self.assertIn("### Turn Result Final Response", final_output_block)
        self.assertIn("- Next Owner: ReviewLead", final_output_block)
        self.assertIn("Hand off to ReviewLead. Next owner: Review Lead.", final_output_block)

if __name__ == "__main__":
    unittest.main()
