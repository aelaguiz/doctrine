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

    def test_final_output_is_not_supported_on_review_driven_agents_in_v1(self) -> None:
        error = self._compile_error(
            """
            output FinalReply: "Final Reply"
                target: TurnResponse
                shape: CommentText
                requirement: Required

            agent InvalidAgent:
                role: "Try to mix review and final_output."
                review: ChangeReview
                outputs: "Outputs"
                    FinalReply
                final_output: FinalReply
            """,
            agent_name="InvalidAgent",
        )

        self.assertEqual(error.code, "E214")
        self.assertIn("review-driven agents", str(error))


if __name__ == "__main__":
    unittest.main()
