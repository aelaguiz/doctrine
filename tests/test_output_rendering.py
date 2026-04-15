from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
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
        self.assertIn("Duplicate properties entry key", str(caught.exception))
        self.assertIn("verdict", str(caught.exception))
