from __future__ import annotations

import textwrap
import unittest

from doctrine import model
from doctrine.parser import parse_text


class ParserSourceSpanTests(unittest.TestCase):
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
                        verdict: verdict
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

        checks = review.body.items[4]
        self.assertIsInstance(checks, model.ReviewSection)
        self.assertEqual(checks.source_span, model.SourceSpan(line=7, column=5))
        self.assertEqual(checks.items[0].source_span, model.SourceSpan(line=8, column=9))

        on_accept = review.body.items[5]
        self.assertIsInstance(on_accept, model.ReviewOutcomeSection)
        self.assertEqual(on_accept.source_span, model.SourceSpan(line=9, column=5))
        self.assertEqual(on_accept.items[0].source_span, model.SourceSpan(line=10, column=9))

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


if __name__ == "__main__":
    unittest.main()
