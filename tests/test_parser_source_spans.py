from __future__ import annotations

import textwrap
import unittest

from doctrine import model
from doctrine.parser import parse_text


class ParserSourceSpanTests(unittest.TestCase):
    def test_import_alias_nodes_keep_source_spans(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """\
                import shared.review as shared_review
                from shared.review import DraftReviewComment as ImportedComment
                from shared.steps import Greeting
                """
            )
        )

        first_import = prompt.declarations[0]
        second_import = prompt.declarations[1]
        third_import = prompt.declarations[2]

        self.assertIsInstance(first_import, model.ImportDecl)
        self.assertEqual(first_import.path.module_parts, ("shared", "review"))
        self.assertEqual(first_import.alias, "shared_review")
        self.assertIsNone(first_import.imported_name)
        self.assertEqual(first_import.source_span, model.SourceSpan(line=1, column=1))

        self.assertIsInstance(second_import, model.ImportDecl)
        self.assertEqual(second_import.path.module_parts, ("shared", "review"))
        self.assertEqual(second_import.imported_name, "DraftReviewComment")
        self.assertEqual(second_import.alias, "ImportedComment")
        self.assertEqual(second_import.source_span, model.SourceSpan(line=2, column=1))

        self.assertIsInstance(third_import, model.ImportDecl)
        self.assertEqual(third_import.path.module_parts, ("shared", "steps"))
        self.assertEqual(third_import.imported_name, "Greeting")
        self.assertIsNone(third_import.alias)
        self.assertEqual(third_import.source_span, model.SourceSpan(line=3, column=1))

    def test_workflow_law_nodes_keep_source_spans(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """\
                workflow RouteFromWorkflow: "Route From Workflow"
                    law:
                        current none
                        stop "Hand off or finish the turn."
                        route_from RouteFacts.route_choice as ProofRoute:
                            ProofRoute.accept:
                                route "Send to AcceptanceCritic." -> AcceptanceCritic
                            else:
                                route "Keep drafting." -> DraftLead
                """
            )
        )

        workflow = prompt.declarations[0]
        self.assertIsInstance(workflow, model.WorkflowDecl)
        self.assertEqual(workflow.source_span, model.SourceSpan(line=1, column=1))
        self.assertIsNotNone(workflow.body.law)
        self.assertEqual(workflow.body.law.source_span, model.SourceSpan(line=3, column=9))

        route_from = workflow.body.law.items[2]
        self.assertIsInstance(route_from, model.RouteFromStmt)
        self.assertEqual(route_from.source_span, model.SourceSpan(line=5, column=9))
        self.assertEqual(route_from.cases[0].source_span, model.SourceSpan(line=6, column=13))
        self.assertEqual(route_from.cases[0].route.source_span, model.SourceSpan(line=7, column=17))
        self.assertEqual(route_from.cases[1].source_span, model.SourceSpan(line=8, column=13))

    def test_review_nodes_keep_source_spans(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """\
                review DraftReview: "Draft Review"
                    subject: DraftSpec
                    contract: DraftReviewContract
                    comment_output: DraftReviewComment
                    fields:
                        verdict
                    contract_checks: "Contract Checks"
                        reject contract.outline_complete when DraftSpec.outline_missing
                    on_accept: "If Accepted"
                        current artifact DraftSpec via DraftReviewComment.current_artifact
                    on_reject: "If Rejected"
                        current artifact DraftSpec via DraftReviewComment.current_artifact
                """
            )
        )

        review = prompt.declarations[0]
        self.assertIsInstance(review, model.ReviewDecl)
        self.assertEqual(review.source_span, model.SourceSpan(line=1, column=1))
        self.assertEqual(review.body.items[0].source_span, model.SourceSpan(line=2, column=5))
        self.assertEqual(review.body.items[1].source_span, model.SourceSpan(line=3, column=5))
        self.assertEqual(review.body.items[3].source_span, model.SourceSpan(line=5, column=5))
        self.assertEqual(review.body.items[3].bindings[0].source_span, model.SourceSpan(line=6, column=9))
        self.assertEqual(review.body.items[3].bindings[0].field_path, ("verdict",))

        checks = review.body.items[4]
        self.assertIsInstance(checks, model.ReviewSection)
        self.assertEqual(checks.source_span, model.SourceSpan(line=7, column=5))
        self.assertEqual(checks.items[0].source_span, model.SourceSpan(line=8, column=9))

        on_accept = review.body.items[5]
        self.assertIsInstance(on_accept, model.ReviewOutcomeSection)
        self.assertEqual(on_accept.source_span, model.SourceSpan(line=9, column=5))
        self.assertEqual(on_accept.items[0].source_span, model.SourceSpan(line=10, column=9))

    def test_io_wrapper_shorthand_nodes_keep_source_spans(self) -> None:
        rendered = textwrap.dedent(
            """\
            input LessonsIssueLedger: "Lessons Issue Ledger"
                source: File
                    path: "catalog/lessons_issue_ledger.json"
                shape: "JSON Document"
                requirement: Required

            input ForwardIssueLedger: "Forward Issue Ledger"
                source: File
                    path: "catalog/forward_issue_ledger.json"
                shape: "JSON Document"
                requirement: Advisory

            inputs SectionDossierInputs: "Your Inputs"
                issue_ledger: LessonsIssueLedger

            inputs ForwardSectionInputs[SectionDossierInputs]: "Your Inputs"
                override issue_ledger: ForwardIssueLedger
            """
        )
        prompt = parse_text(rendered)

        base_inputs = prompt.declarations[2]
        self.assertIsInstance(base_inputs, model.InputsDecl)
        base_section = base_inputs.body.items[0]
        self.assertIsInstance(base_section, model.IoSection)
        self.assertEqual(
            base_section.source_span,
            model.SourceSpan(
                line=rendered.splitlines().index("    issue_ledger: LessonsIssueLedger") + 1,
                column=5,
            ),
        )
        self.assertEqual(base_section.title, None)
        self.assertEqual(
            base_section.items[0].source_span,
            model.SourceSpan(
                line=rendered.splitlines().index("    issue_ledger: LessonsIssueLedger") + 1,
                column=19,
            ),
        )

        child_inputs = prompt.declarations[3]
        self.assertIsInstance(child_inputs, model.InputsDecl)
        override_section = child_inputs.body.items[0]
        self.assertIsInstance(override_section, model.OverrideIoSection)
        self.assertEqual(
            override_section.source_span,
            model.SourceSpan(
                line=rendered.splitlines().index("    override issue_ledger: ForwardIssueLedger")
                + 1,
                column=5,
            ),
        )
        self.assertEqual(override_section.title, None)
        self.assertEqual(
            override_section.items[0].source_span,
            model.SourceSpan(
                line=rendered.splitlines().index("    override issue_ledger: ForwardIssueLedger")
                + 1,
                column=28,
            ),
        )

    def test_self_path_ref_nodes_keep_source_spans(self) -> None:
        rendered = textwrap.dedent(
            """\
            workflow WorkflowRoot: "Workflow Root"
                review_sequence: "Review Sequence"
                    self:steps.first

                steps: "Steps"
                    first: "First"
                        "Do the first step."

            output BaseRouteNote: "Base Route Note"
                target: TurnResponse
                shape: MarkdownDocument
                requirement: Required

                details: "Details"
                    summary: "Summary"
                        "Keep the route record honest."

                summary_copy: self:details.summary
                guarded_summary: self:details.summary when route.exists

            output RouteNote[BaseRouteNote]: "Route Note"
                override summary_copy: self:details

            input DemoInput: "Demo Input"
                source: File
                    path: self:title
                shape: MarkdownDocument
                requirement: Required
            """
        )
        prompt = parse_text(rendered)
        lines = rendered.splitlines()

        workflow = prompt.declarations[0]
        self.assertIsInstance(workflow, model.WorkflowDecl)
        workflow_ref = workflow.body.items[0].items[0]
        self.assertIsInstance(workflow_ref, model.SectionBodyRef)
        self.assertTrue(workflow_ref.ref.self_rooted)
        self.assertEqual(
            workflow_ref.ref.source_span,
            model.SourceSpan(
                line=lines.index("        self:steps.first") + 1,
                column=lines[lines.index("        self:steps.first")].index("self:steps.first") + 1,
            ),
        )

        base_output = prompt.declarations[1]
        self.assertIsInstance(base_output, model.OutputDecl)
        summary_copy = base_output.items[4]
        self.assertIsInstance(summary_copy, model.RecordScalar)
        self.assertIsInstance(summary_copy.value, model.AddressableRef)
        self.assertTrue(summary_copy.value.self_rooted)
        self.assertEqual(
            summary_copy.value.source_span,
            model.SourceSpan(
                line=lines.index("    summary_copy: self:details.summary") + 1,
                column=lines[lines.index("    summary_copy: self:details.summary")].index(
                    "self:details.summary"
                )
                + 1,
            ),
        )

        guarded_summary = base_output.items[5]
        self.assertIsInstance(guarded_summary, model.GuardedOutputScalar)
        self.assertIsInstance(guarded_summary.value, model.AddressableRef)
        self.assertTrue(guarded_summary.value.self_rooted)
        self.assertEqual(
            guarded_summary.value.source_span,
            model.SourceSpan(
                line=lines.index("    guarded_summary: self:details.summary when route.exists")
                + 1,
                column=lines[
                    lines.index(
                        "    guarded_summary: self:details.summary when route.exists"
                    )
                ].index("self:details.summary")
                + 1,
            ),
        )

        child_output = prompt.declarations[2]
        self.assertIsInstance(child_output, model.OutputDecl)
        override_summary = child_output.items[0]
        self.assertIsInstance(override_summary, model.OutputOverrideRecordScalar)
        self.assertIsInstance(override_summary.value, model.AddressableRef)
        self.assertTrue(override_summary.value.self_rooted)
        self.assertEqual(
            override_summary.value.source_span,
            model.SourceSpan(
                line=lines.index("    override summary_copy: self:details") + 1,
                column=lines[
                    lines.index("    override summary_copy: self:details")
                ].index("self:details")
                + 1,
            ),
        )

        input_decl = prompt.declarations[3]
        self.assertIsInstance(input_decl, model.InputDecl)
        source_item = input_decl.items[0]
        self.assertIsInstance(source_item, model.RecordScalar)
        self.assertIsNotNone(source_item.body)
        path_item = source_item.body[0]
        self.assertIsInstance(path_item, model.RecordScalar)
        self.assertIsInstance(path_item.value, model.AddressableRef)
        self.assertTrue(path_item.value.self_rooted)
        self.assertEqual(
            path_item.value.source_span,
            model.SourceSpan(
                line=lines.index("        path: self:title") + 1,
                column=lines[lines.index("        path: self:title")].index("self:title") + 1,
            ),
        )

    def test_readable_nodes_keep_source_spans(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """\
                document ReleaseGuide: "Release Guide"
                    properties release_window: "Release Window"
                        start: "Start"
                    table release_gates: "Release Gates"
                        columns:
                            gate: "Gate"
                        notes:
                            "List one row per release gate."
                    callout caution: "Caution"
                        kind: warning
                        "Watch the rollout."
                    footnotes references: "References"
                        gate_doc: "Gate doc."
                """
            )
        )

        document = prompt.declarations[0]
        self.assertIsInstance(document, model.DocumentDecl)
        self.assertEqual(document.source_span, model.SourceSpan(line=1, column=1))

        properties = document.body.items[0]
        self.assertIsInstance(properties, model.ReadableBlock)
        self.assertEqual(properties.source_span, model.SourceSpan(line=2, column=5))
        self.assertIsInstance(properties.payload, model.ReadablePropertiesData)
        self.assertEqual(properties.payload.source_span, model.SourceSpan(line=3, column=9))
        self.assertEqual(properties.payload.entries[0].source_span, model.SourceSpan(line=3, column=9))

        table_block = document.body.items[1]
        self.assertIsInstance(table_block, model.ReadableBlock)
        self.assertEqual(table_block.source_span, model.SourceSpan(line=4, column=5))
        self.assertIsInstance(table_block.payload, model.ReadableTableData)
        self.assertEqual(table_block.payload.columns[0].source_span, model.SourceSpan(line=6, column=13))

        callout = document.body.items[2]
        self.assertIsInstance(callout, model.ReadableBlock)
        self.assertEqual(callout.source_span, model.SourceSpan(line=9, column=5))
        self.assertIsInstance(callout.payload, model.ReadableCalloutData)
        self.assertEqual(callout.payload.source_span, model.SourceSpan(line=10, column=9))

        footnotes = document.body.items[3]
        self.assertIsInstance(footnotes, model.ReadableBlock)
        self.assertEqual(footnotes.source_span, model.SourceSpan(line=12, column=5))
        self.assertIsInstance(footnotes.payload, model.ReadableFootnotesData)
        self.assertEqual(footnotes.payload.entries[0].source_span, model.SourceSpan(line=13, column=9))

    def test_output_attachment_nodes_keep_source_spans(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """\
                render_profile CompactComment:
                    properties -> sentence

                output ChildReply[BaseReply]: "Child Reply"
                    inherit target
                    override schema: SharedSchema
                    inherit render_profile
                    override trust_surface:
                        verdict
                """
            )
        )

        output_decl = prompt.declarations[1]
        self.assertIsInstance(output_decl, model.OutputDecl)
        self.assertEqual(output_decl.source_span, model.SourceSpan(line=4, column=1))
        self.assertEqual(output_decl.schema_source_span, model.SourceSpan(line=6, column=5))
        self.assertEqual(
            output_decl.render_profile_source_span,
            model.SourceSpan(line=7, column=5),
        )
        self.assertEqual(
            output_decl.trust_surface_source_span,
            model.SourceSpan(line=8, column=5),
        )

    def test_schema_nodes_keep_source_spans(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """\
                schema ReleaseSchema: "Release Schema"
                    sections:
                        summary: "Summary"
                            "Summarize the release."

                    artifacts:
                        release_notes: "Release Notes"
                            ref: ReleaseNotes

                    groups:
                        publish_packet: "Publish Packet"
                            release_notes
                """
            )
        )

        schema_decl = prompt.declarations[0]
        self.assertIsInstance(schema_decl, model.SchemaDecl)
        self.assertEqual(schema_decl.source_span, model.SourceSpan(line=1, column=1))

        sections_block = schema_decl.body.items[0]
        self.assertIsInstance(sections_block, model.SchemaSectionsBlock)
        self.assertEqual(sections_block.source_span, model.SourceSpan(line=2, column=5))
        self.assertEqual(
            sections_block.items[0].source_span,
            model.SourceSpan(line=3, column=9),
        )

        artifacts_block = schema_decl.body.items[1]
        self.assertIsInstance(artifacts_block, model.SchemaArtifactsBlock)
        self.assertEqual(artifacts_block.source_span, model.SourceSpan(line=6, column=5))
        self.assertEqual(
            artifacts_block.items[0].source_span,
            model.SourceSpan(line=7, column=9),
        )

        groups_block = schema_decl.body.items[2]
        self.assertIsInstance(groups_block, model.SchemaGroupsBlock)
        self.assertEqual(groups_block.source_span, model.SourceSpan(line=10, column=5))
        self.assertEqual(
            groups_block.items[0].source_span,
            model.SourceSpan(line=11, column=9),
        )

    def test_analysis_nodes_keep_source_spans(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """\
                analysis BaseAnalysis: "Base Analysis"
                    stages: "Stages"
                        prove "Release plan" from {CurrentPlan}
                        classify "Risk band" as RiskBand
                        compare "Coverage" against {CurrentPlan}
                        defend "Recommendation" using {CurrentPlan}

                analysis ChildAnalysis[BaseAnalysis]: "Child Analysis"
                    override stages: "Stages"
                        derive "Updated plan" from {CurrentPlan}
                """
            )
        )

        base_analysis = prompt.declarations[0]
        self.assertIsInstance(base_analysis, model.AnalysisDecl)
        self.assertEqual(base_analysis.source_span, model.SourceSpan(line=1, column=1))

        stages = base_analysis.body.items[0]
        self.assertIsInstance(stages, model.AnalysisSection)
        self.assertEqual(stages.source_span, model.SourceSpan(line=2, column=5))
        self.assertEqual(stages.items[0].source_span, model.SourceSpan(line=3, column=9))
        self.assertEqual(stages.items[1].source_span, model.SourceSpan(line=4, column=9))
        self.assertEqual(stages.items[2].source_span, model.SourceSpan(line=5, column=9))
        self.assertEqual(stages.items[3].source_span, model.SourceSpan(line=6, column=9))

        child_analysis = prompt.declarations[1]
        self.assertIsInstance(child_analysis, model.AnalysisDecl)
        self.assertEqual(child_analysis.source_span, model.SourceSpan(line=8, column=1))

        override_section = child_analysis.body.items[0]
        self.assertIsInstance(override_section, model.AnalysisOverrideSection)
        self.assertEqual(override_section.source_span, model.SourceSpan(line=9, column=5))
        self.assertEqual(
            override_section.items[0].source_span,
            model.SourceSpan(line=10, column=9),
        )

    def test_skills_nodes_keep_source_spans(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """\
                skill GroundingSkill: "Grounding Skill"
                    purpose: "Ground the reply."

                skill ResearchSkill: "Research Skill"
                    purpose: "Research the facts."

                skills BaseSkills: "Base Skills"
                    support: "Support"
                        skill grounding: GroundingSkill
                            requirement: Required

                skills ChildSkills[BaseSkills]: "Child Skills"
                    override support: "Support"
                        skill research: ResearchSkill
                            requirement: Advisory
                """
            )
        )

        base_skills = prompt.declarations[2]
        self.assertIsInstance(base_skills, model.SkillsDecl)
        self.assertEqual(base_skills.source_span, model.SourceSpan(line=7, column=1))

        support_section = base_skills.body.items[0]
        self.assertIsInstance(support_section, model.SkillsSection)
        self.assertEqual(support_section.source_span, model.SourceSpan(line=8, column=5))
        self.assertEqual(
            support_section.items[0].source_span,
            model.SourceSpan(line=9, column=9),
        )

        child_skills = prompt.declarations[3]
        self.assertIsInstance(child_skills, model.SkillsDecl)
        self.assertEqual(child_skills.source_span, model.SourceSpan(line=12, column=1))

        override_section = child_skills.body.items[0]
        self.assertIsInstance(override_section, model.OverrideSkillsSection)
        self.assertEqual(override_section.source_span, model.SourceSpan(line=13, column=5))
        self.assertEqual(
            override_section.items[0].source_span,
            model.SourceSpan(line=14, column=9),
        )

    def test_skill_package_emit_entries_keep_source_spans(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """\
                skill package LayoutChecklist: "Layout Checklist"
                    metadata:
                        name: "layout-checklist"
                    emit:
                        "references/checklist.md": ChecklistGuide
                        "references/qa.md": QaGuide
                    "Keep the root file short."
                """
            )
        )

        package = prompt.declarations[0]
        self.assertIsInstance(package, model.SkillPackageDecl)
        self.assertEqual(package.source_span, model.SourceSpan(line=1, column=1))
        self.assertEqual(len(package.emit_entries), 2)
        self.assertEqual(
            package.emit_entries[0].source_span,
            model.SourceSpan(line=5, column=9),
        )
        self.assertEqual(package.emit_entries[0].path, "references/checklist.md")
        self.assertEqual(package.emit_entries[0].ref.declaration_name, "ChecklistGuide")
        self.assertEqual(
            package.emit_entries[1].source_span,
            model.SourceSpan(line=6, column=9),
        )
        self.assertEqual(package.emit_entries[1].path, "references/qa.md")
        self.assertEqual(package.emit_entries[1].ref.declaration_name, "QaGuide")


if __name__ == "__main__":
    unittest.main()
