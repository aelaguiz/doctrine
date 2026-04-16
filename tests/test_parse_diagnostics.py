from __future__ import annotations

import textwrap
import unittest

from doctrine.parser import parse_text


class ParseDiagnosticsTests(unittest.TestCase):
    def _assert_parse_error_points_at_line(
        self,
        *,
        source: str,
        source_path: str,
        anchor_line: str,
        summary_snippet: str,
        expected_code: str = "E199",
        occurrence: int = 1,
        expected_column: int = 5,
    ) -> None:
        matches = [
            index
            for index, line in enumerate(source.splitlines(), start=1)
            if line == anchor_line
        ]
        self.assertGreaterEqual(len(matches), occurrence, f"missing occurrence {occurrence} of {anchor_line!r}")
        expected_line = matches[occurrence - 1]

        try:
            parse_text(source, source_path=source_path)
        except Exception as exc:
            # These transform-stage checks run after the body already parsed, so the
            # diagnostic must point at the later conflicting line authors need to change.
            self.assertEqual(type(exc).__name__, "ParseError")
            self.assertEqual(getattr(exc, "code", None), expected_code)
            self.assertEqual(getattr(exc, "location").line, expected_line)
            self.assertEqual(getattr(exc, "location").column, expected_column)
            self.assertIn(anchor_line.strip(), str(exc))
            self.assertIn(summary_snippet, str(exc))
            return

        self.fail("expected parsing to fail")

    def test_output_schema_owner_conflict_points_at_must_include(self) -> None:
        source = textwrap.dedent(
            """\
            schema LessonInventory: "Lesson Inventory"
                sections:
                    summary: "Summary"
                        "State the required summary."

            output SchemaOutput: "Schema Output"
                target: TurnResponse
                shape: JsonObject
                requirement: Required
                schema: LessonInventory

                must_include: "Must Include"
                    summary: "Summary"
                        "Repeat the summary locally."
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/schema-owner-conflict.prompt",
            anchor_line='    must_include: "Must Include"',
            summary_snippet="Outputs may not define both `schema:` and `must_include:`.",
        )

    def test_output_schema_owner_conflict_points_at_override_must_include(self) -> None:
        source = textwrap.dedent(
            """\
            schema LessonInventory: "Lesson Inventory"
                sections:
                    summary: "Summary"
                        "State the required summary."

            output SchemaOutput: "Schema Output"
                target: TurnResponse
                shape: JsonObject
                requirement: Required
                schema: LessonInventory

                override must_include: "Must Include"
                    summary: "Summary"
                        "Repeat the summary locally."
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/schema-owner-override-conflict.prompt",
            anchor_line='    override must_include: "Must Include"',
            summary_snippet="Outputs may not define both `schema:` and `must_include:`.",
        )

    def test_output_schema_structure_conflict_points_at_structure(self) -> None:
        source = textwrap.dedent(
            """\
            schema DeliveryInventory: "Delivery Inventory"
                sections:
                    summary: "Summary"
                        "Include a short summary."

            document DeliveryPlan: "Delivery Plan"
                section summary: "Summary"
                    "Write the summary."

            output InvalidDeliveryPlan: "Invalid Delivery Plan"
                target: File
                    path: "unit_root/INVALID_DELIVERY_PLAN.md"
                shape: MarkdownDocument
                requirement: Required
                schema: DeliveryInventory
                structure: DeliveryPlan
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/schema-structure-conflict.prompt",
            anchor_line="    structure: DeliveryPlan",
            summary_snippet="Outputs may not define both `schema:` and `structure:`.",
        )

    def test_workflow_late_prose_points_at_the_late_line(self) -> None:
        source = textwrap.dedent(
            """\
            workflow Shared: "Shared"
                intro: "Intro"
                    "First item."
                "Late prose"
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/workflow-late-prose.prompt",
            anchor_line='    "Late prose"',
            summary_snippet="Workflow prose lines must appear before keyed workflow entries.",
        )

    def test_analysis_late_prose_points_at_the_late_line(self) -> None:
        source = textwrap.dedent(
            """\
            analysis InspectDraft: "Inspect Draft"
                facts: "Facts"
                    "Capture facts."
                "Late prose"
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/analysis-late-prose.prompt",
            anchor_line='    "Late prose"',
            summary_snippet="Analysis prose lines must appear before keyed analysis entries.",
        )

    def test_decision_late_prose_points_at_the_late_line(self) -> None:
        source = textwrap.dedent(
            """\
            decision PickOne: "Pick One"
                candidates minimum 2
                "Late prose"
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/decision-late-prose.prompt",
            anchor_line='    "Late prose"',
            summary_snippet="Decision prose lines must appear before typed decision entries.",
        )

    def test_schema_late_prose_points_at_the_late_line(self) -> None:
        source = textwrap.dedent(
            """\
            schema Delivery: "Delivery"
                sections:
                    summary: "Summary"
                        "Body."
                "Late prose"
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/schema-late-prose.prompt",
            anchor_line='    "Late prose"',
            summary_snippet="Schema prose lines must appear before typed schema blocks.",
        )

    def test_document_late_prose_points_at_the_late_line(self) -> None:
        source = textwrap.dedent(
            """\
            document Guide: "Guide"
                section intro: "Intro"
                    "Body."
                "Late prose"
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/document-late-prose.prompt",
            anchor_line='    "Late prose"',
            summary_snippet="Document prose lines must appear before keyed document blocks.",
        )

    def test_io_late_prose_points_at_the_late_line(self) -> None:
        source = textwrap.dedent(
            """\
            inputs SharedInputs: "Shared Inputs"
                draft: "Draft"
                    source: File
                        path: "draft.md"
                "Late prose"
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/io-late-prose.prompt",
            anchor_line='    "Late prose"',
            summary_snippet="Inputs and outputs prose lines must appear before keyed entries.",
        )

    def test_skills_late_prose_points_at_the_late_line(self) -> None:
        source = textwrap.dedent(
            """\
            skill GroundingSkill: "Grounding Skill"
                purpose: "Ground the current claim before you write."

            skills SharedSkills: "Skills"
                skill primary: GroundingSkill
                    requirement: Required
                "Late prose"
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/skills-late-prose.prompt",
            anchor_line='    "Late prose"',
            summary_snippet="Skills prose lines must appear before keyed skills entries.",
        )

    def test_output_duplicate_render_profile_points_at_the_later_line(self) -> None:
        source = textwrap.dedent(
            """\
            output Demo: "Demo"
                target: TurnResponse
                shape: JsonObject
                requirement: Required
                render_profile: Profiles.default
                render_profile: Profiles.detail
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/output-duplicate-render-profile.prompt",
            anchor_line="    render_profile: Profiles.detail",
            summary_snippet="Output declarations may define `render_profile:` only once.",
        )

    def test_grouped_inherit_duplicate_key_points_at_the_group_line(self) -> None:
        source = textwrap.dedent(
            """\
            workflow ChildWorkflow[BaseWorkflow]: "Child Workflow"
                inherit {opening, opening}
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/grouped-inherit-duplicate.prompt",
            anchor_line="    inherit {opening, opening}",
            summary_snippet="Grouped `inherit` may list key `opening` only once.",
            expected_code="E309",
        )

    def test_grouped_inherit_empty_group_points_at_the_group_line(self) -> None:
        source = textwrap.dedent(
            """\
            output ChildOutput[BaseOutput]: "Child Output"
                inherit {}
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/grouped-inherit-empty.prompt",
            anchor_line="    inherit {}",
            summary_snippet="Grouped `inherit` must list at least one key.",
            expected_code="E309",
        )

    def test_grouped_schema_inherit_unknown_key_points_at_the_group_line(self) -> None:
        source = textwrap.dedent(
            """\
            schema ChildSchema[BaseSchema]: "Child Schema"
                inherit {sections, unknown}
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/grouped-schema-inherit-unknown.prompt",
            anchor_line="    inherit {sections, unknown}",
            summary_snippet="Grouped `inherit` uses unknown key `unknown`.",
            expected_code="E309",
        )

    def test_analysis_duplicate_render_profile_points_at_the_later_line(self) -> None:
        source = textwrap.dedent(
            """\
            analysis InspectDraft: "Inspect Draft"
                render_profile: Profiles.default
                render_profile: Profiles.detail
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/analysis-duplicate-render-profile.prompt",
            anchor_line="    render_profile: Profiles.detail",
            summary_snippet="Analysis declarations may define `render_profile:` only once.",
        )

    def test_decision_duplicate_render_profile_points_at_the_later_line(self) -> None:
        source = textwrap.dedent(
            """\
            decision PickOne: "Pick One"
                render_profile: Profiles.default
                render_profile: Profiles.detail
                candidates minimum 2
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/decision-duplicate-render-profile.prompt",
            anchor_line="    render_profile: Profiles.detail",
            summary_snippet="Decision declarations may define `render_profile:` only once.",
        )

    def test_schema_duplicate_render_profile_points_at_the_later_line(self) -> None:
        source = textwrap.dedent(
            """\
            schema Delivery: "Delivery"
                render_profile: Profiles.default
                render_profile: Profiles.detail
                sections:
                    summary: "Summary"
                        "Body."
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/schema-duplicate-render-profile.prompt",
            anchor_line="    render_profile: Profiles.detail",
            summary_snippet="Schema declarations may define `render_profile:` only once.",
        )

    def test_document_duplicate_render_profile_points_at_the_later_line(self) -> None:
        source = textwrap.dedent(
            """\
            document Guide: "Guide"
                render_profile: Profiles.default
                render_profile: Profiles.detail
                section intro: "Intro"
                    "Body."
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/document-duplicate-render-profile.prompt",
            anchor_line="    render_profile: Profiles.detail",
            summary_snippet="Document declarations may define `render_profile:` only once.",
        )

    def test_schema_duplicate_sections_points_at_the_later_block(self) -> None:
        source = textwrap.dedent(
            """\
            schema Delivery: "Delivery"
                sections:
                    summary: "Summary"
                        "Body."
                sections:
                    extra: "Extra"
                        "Body."
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/schema-duplicate-sections.prompt",
            anchor_line="    sections:",
            summary_snippet="Schema declarations may account for `sections` only once.",
            occurrence=2,
        )

    def test_input_duplicate_structure_points_at_the_later_line(self) -> None:
        source = textwrap.dedent(
            """\
            document Plan: "Plan"
                section intro: "Intro"
                    "Body."

            input CurrentIssue: "Current Issue"
                source: Prompt
                shape: MarkdownDocument
                requirement: Required
                structure: Plan
                structure: Plan
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/input-duplicate-structure.prompt",
            anchor_line="    structure: Plan",
            summary_snippet="Input declarations may define `structure:` only once.",
            occurrence=2,
        )

    def test_output_duplicate_trust_surface_points_at_the_later_block(self) -> None:
        source = textwrap.dedent(
            """\
            output ReviewComment: "Review Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required
                verdict: "Verdict"
                    "Say whether the review passed."
                trust_surface:
                    verdict
                trust_surface:
                    verdict
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/output-duplicate-trust-surface.prompt",
            anchor_line="    trust_surface:",
            summary_snippet="Output declarations may define `trust_surface` only once.",
            occurrence=2,
        )

    def test_output_duplicate_trust_surface_points_at_override_trust_surface_block(self) -> None:
        source = textwrap.dedent(
            """\
            output ReviewComment: "Review Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required
                verdict: "Verdict"
                    "Say whether the review passed."
                trust_surface:
                    verdict
                override trust_surface:
                    verdict
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/output-override-trust-surface.prompt",
            anchor_line="    override trust_surface:",
            summary_snippet="Output declarations may define `trust_surface` only once.",
        )

    def test_workflow_duplicate_law_points_at_the_later_block(self) -> None:
        source = textwrap.dedent(
            """\
            workflow DraftWorkflow: "Draft Workflow"
                law:
                    activation:
                        active when draft_ready
                law:
                    activation:
                        active when draft_ready
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/workflow-duplicate-law.prompt",
            anchor_line="    law:",
            summary_snippet="Workflow declarations may define `law` only once.",
            occurrence=2,
        )

    def test_decision_duplicate_minimum_points_at_the_later_line(self) -> None:
        source = textwrap.dedent(
            """\
            decision PickOne: "Pick One"
                candidates minimum 2
                candidates minimum 3
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/decision-duplicate-minimum.prompt",
            anchor_line="    candidates minimum 3",
            summary_snippet="Decision declarations may account for `minimum_candidates` only once.",
        )

    def test_decision_duplicate_required_points_at_the_later_line(self) -> None:
        source = textwrap.dedent(
            """\
            decision PickOne: "Pick One"
                rank required
                rank required
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/decision-duplicate-rank-required.prompt",
            anchor_line="    rank required",
            summary_snippet="Decision declarations may account for `required:rank` only once.",
            occurrence=2,
        )

    def test_document_duplicate_item_schema_points_at_the_later_block(self) -> None:
        source = textwrap.dedent(
            """\
            document LessonPlan: "Lesson Plan"
                sequence read_order: "Read Order"
                    item_schema:
                        step_label: "Step Label"
                            "Say what the reader should do at this step."

                    item_schema:
                        teaching_job: "Teaching Job"
                            "This should fail."
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/document-duplicate-item-schema.prompt",
            anchor_line="        item_schema:",
            summary_snippet="Readable list bodies may define `item_schema:` only once.",
            occurrence=2,
            expected_column=9,
        )

    def test_document_duplicate_row_schema_points_at_the_later_block(self) -> None:
        source = textwrap.dedent(
            """\
            document LessonPlan: "Lesson Plan"
                table step_arc: "Step Arc"
                    row_schema:
                        topic: "Topic"
                            "Name the topic that the row covers."

                    row_schema:
                        evidence: "Evidence"
                            "This should fail."

                    columns:
                        topic: "Topic"
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/document-duplicate-row-schema.prompt",
            anchor_line="        row_schema:",
            summary_snippet="Readable table bodies may define `row_schema:` only once.",
            occurrence=2,
            expected_column=9,
        )

    def test_document_duplicate_raw_text_points_at_the_later_line(self) -> None:
        source = textwrap.dedent(
            '''\
            document ReleaseAppendix: "Release Appendix"
                markdown appendix_markdown: "Appendix Markdown" advisory
                    text: """
                    First.
                    """
                    text: """
                    Second.
                    """
            '''
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/document-duplicate-raw-text.prompt",
            anchor_line='        text: """',
            summary_snippet="Raw text readable blocks may define `text:` only once.",
            occurrence=2,
            expected_column=9,
        )

    def test_document_duplicate_image_alt_points_at_the_later_line(self) -> None:
        source = textwrap.dedent(
            """\
            document ReleaseAppendix: "Release Appendix"
                image evidence: "Evidence" optional
                    src: "https://example.com/release.png"
                    alt: "Release checklist screenshot"
                    alt: "Second alt"
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/document-duplicate-image-alt.prompt",
            anchor_line='        alt: "Second alt"',
            summary_snippet="Image readable blocks may define `alt:` only once.",
            expected_column=9,
        )

    def test_enum_duplicate_wire_points_at_the_later_line(self) -> None:
        source = textwrap.dedent(
            """\
            enum NextOwner: "Next Owner"
                section_author: "Section Author"
                    wire: "same-owner"
                    wire: "same-owner"
            """
        )
        self._assert_parse_error_points_at_line(
            source=source,
            source_path="/tmp/enum-duplicate-wire.prompt",
            anchor_line='        wire: "same-owner"',
            summary_snippet="Enum member may declare `wire` at most once.",
            occurrence=2,
            expected_column=9,
        )


if __name__ == "__main__":
    unittest.main()
