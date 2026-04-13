from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class RouteOutputSemanticsTests(unittest.TestCase):
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

    def test_workflow_output_can_bind_route_fields_on_routed_branch(self) -> None:
        agent = self._compile_agent(
            """
            agent ReviewLead:
                role: "Own routed follow-up."
                workflow: "Follow Up"
                    "Take the routed follow-up."

            output RoutedReply: "Routed Reply"
                target: TurnResponse
                shape: Comment
                requirement: Required

                next_owner: route.next_owner
                next_owner_key: route.next_owner.key

                route_summary: "Route Summary"
                    "{{route.summary}}"

            workflow RoutedWorkflow: "Routed Workflow"
                "Always route the turn."

                law:
                    active when true
                    current none
                    stop "Reply and stop."
                    route "Hand off to ReviewLead." -> ReviewLead

            agent RouteBindingDemo:
                role: "Bind ordinary outputs from compiler-owned route semantics."
                workflow: RoutedWorkflow
                outputs: "Outputs"
                    RoutedReply
            """,
            agent_name="RouteBindingDemo",
        )

        rendered = render_markdown(agent)
        self.assertIn("- Next Owner: Review Lead", rendered)
        self.assertIn("- Next Owner Key: ReviewLead", rendered)
        self.assertIn("Hand off to ReviewLead. Next owner: Review Lead.", rendered)

    def test_route_semantics_require_guard_when_some_branches_do_not_route(self) -> None:
        error = self._compile_error(
            """
            input RouteFacts: "Route Facts"
                source: Prompt
                shape: JsonObject
                requirement: Required
                should_route: "Should Route"

            agent ReviewLead:
                role: "Own routed follow-up."
                workflow: "Follow Up"
                    "Take the routed follow-up."

            output MaybeRoutedReply: "Maybe Routed Reply"
                target: TurnResponse
                shape: Comment
                requirement: Required

                next_owner: route.next_owner

            workflow MaybeRoutedWorkflow: "Maybe Routed Workflow"
                "Route only when the host facts require it."

                law:
                    active when true
                    current none
                    stop "Reply and stop."
                    route "Hand off to ReviewLead." -> ReviewLead when RouteFacts.should_route

            agent MaybeRouteBindingDemo:
                role: "Fail loud when unguarded route reads span unrouted branches."
                workflow: MaybeRoutedWorkflow
                inputs: "Inputs"
                    RouteFacts
                outputs: "Outputs"
                    MaybeRoutedReply
            """,
            agent_name="MaybeRouteBindingDemo",
        )

        self.assertIn("route semantics are not live on every branch", str(error))
        self.assertIn("guard the read with `route.exists`", str(error))

    def test_guarded_output_section_can_read_route_semantics(self) -> None:
        agent = self._compile_agent(
            """
            input RouteFacts: "Route Facts"
                source: Prompt
                shape: JsonObject
                requirement: Required
                should_route: "Should Route"

            agent ReviewLead:
                role: "Own routed follow-up."
                workflow: "Follow Up"
                    "Take the routed follow-up."

            output MaybeRoutedReply: "Maybe Routed Reply"
                target: TurnResponse
                shape: Comment
                requirement: Required

                route_details: "Route Details" when route.exists:
                    next_owner: route.next_owner

                    summary: "Summary"
                        "{{route.summary}}"

            workflow MaybeRoutedWorkflow: "Maybe Routed Workflow"
                "Route only when the host facts require it."

                law:
                    active when true
                    current none
                    stop "Reply and stop."
                    route "Hand off to ReviewLead." -> ReviewLead when RouteFacts.should_route

            agent GuardedRouteBindingDemo:
                role: "Guard route-specific readback with route.exists."
                workflow: MaybeRoutedWorkflow
                inputs: "Inputs"
                    RouteFacts
                outputs: "Outputs"
                    MaybeRoutedReply
            """,
            agent_name="GuardedRouteBindingDemo",
        )

        rendered = render_markdown(agent)
        self.assertIn("Show this only when a routed owner exists.", rendered)
        self.assertIn("- Next Owner: Review Lead", rendered)
        self.assertIn("Hand off to ReviewLead. Next owner: Review Lead.", rendered)

    def test_guarded_output_scalar_can_read_route_semantics(self) -> None:
        agent = self._compile_agent(
            """
            input RouteFacts: "Route Facts"
                source: Prompt
                shape: JsonObject
                requirement: Required
                should_route: "Should Route"

            agent ReviewLead:
                role: "Own routed follow-up."
                workflow: "Follow Up"
                    "Take the routed follow-up."

            output MaybeRoutedReply: "Maybe Routed Reply"
                target: TurnResponse
                shape: Comment
                requirement: Required

                next_owner: route.next_owner when route.exists

            workflow MaybeRoutedWorkflow: "Maybe Routed Workflow"
                "Route only when host route facts require it."

                law:
                    active when true
                    current none
                    stop "Reply and stop."
                    route "Hand off to ReviewLead." -> ReviewLead when RouteFacts.should_route

            agent GuardedRouteScalarDemo:
                role: "Guard route-specific readback with route.exists."
                workflow: MaybeRoutedWorkflow
                inputs: "Inputs"
                    RouteFacts
                outputs: "Outputs"
                    MaybeRoutedReply
            """,
            agent_name="GuardedRouteScalarDemo",
        )

        rendered = render_markdown(agent)
        self.assertIn("#### Next Owner", rendered)
        self.assertIn("Show this only when a routed owner exists.", rendered)
        self.assertIn("Review Lead", rendered)
        self.assertNotIn("- Next Owner: Review Lead", rendered)

    def test_review_output_can_combine_review_and_route_semantics(self) -> None:
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
                role: "Own accepted draft follow-up."
                workflow: "Follow Up"
                    "Take the accepted draft to the next planning step."

            agent DraftAuthor:
                role: "Fix rejected draft defects."
                workflow: "Revise"
                    "Revise the same draft when review requests changes."

            output DraftReviewComment: "Draft Review Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required

                verdict: "Verdict"
                    "Say whether the review accepted the draft or requested changes."

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
                        "Name the failing review gates in authored order."

                accepted_route: "Accepted Route" when verdict == ReviewVerdict.accept and route.exists:
                    "{{route.summary}}"

                retry_route: "Retry Route" when verdict == ReviewVerdict.changes_requested and route.exists:
                    "{{route.next_owner.title}}"

                trust_surface:
                    current_artifact

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

            agent ReviewRouteBindingDemo:
                role: "Use review semantics and route semantics on the same output."
                review: DraftReview
                inputs: "Inputs"
                    DraftSpec
                outputs: "Outputs"
                    DraftReviewComment
            """,
            agent_name="ReviewRouteBindingDemo",
        )

        rendered = render_markdown(agent)
        self.assertIn("Show this only when verdict is accepted and a routed owner exists.", rendered)
        self.assertIn("Accepted draft returns to ReviewLead. Next owner: Review Lead.", rendered)
        self.assertIn("Show this only when verdict is changes requested and a routed owner exists.", rendered)
        self.assertIn("Draft Author", rendered)

    def test_route_only_output_can_interpolate_route_next_owner(self) -> None:
        agent = self._compile_agent(
            """
            input RouteFacts: "Route Facts"
                source: Prompt
                shape: JsonObject
                requirement: Required
                next_owner_unknown: "Next Owner Unknown"

            output RouteOnlyHandoffOutput: "Routing Handoff Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required

                route_handoff: "Route Handoff" when route.exists:
                    next_owner: route.next_owner

                    route_readback: "Route Readback"
                        "{{route.summary}}"

            agent RoutingOwner:
                role: "Own explicit reroutes when specialist work cannot continue safely."
                workflow: "Instructions"
                    "Take back the same issue when the next specialist owner is still not justified."

            workflow RouteOnlyTurns: "Routing-Only Turns"
                "Handle turns that can only stop, reroute, or keep ownership explicit."

                law:
                    active when true
                    current none
                    stop "No specialist artifact is current for this turn."
                    route "Keep the issue on RoutingOwner until the next specialist owner is actually justified." -> RoutingOwner when RouteFacts.next_owner_unknown

            agent RouteOnlyRouteBindingDemo:
                role: "Read route truth from a route-only comment output."
                workflow: RouteOnlyTurns
                inputs: "Inputs"
                    RouteFacts
                outputs: "Outputs"
                    RouteOnlyHandoffOutput
            """,
            agent_name="RouteOnlyRouteBindingDemo",
        )

        rendered = render_markdown(agent)
        self.assertIn("#### Route Handoff", rendered)
        self.assertIn("Show this only when a routed owner exists.", rendered)
        self.assertIn("- Next Owner: Routing Owner", rendered)
        self.assertIn("Keep the issue on RoutingOwner until the next specialist owner is actually justified. Next owner: Routing Owner.", rendered)

    def test_handoff_routing_outputs_can_bind_route_fields_from_law(self) -> None:
        agent = self._compile_agent(
            """
            agent ReviewLead:
                role: "Own routed follow-up."
                workflow: "Follow Up"
                    "Take the routed follow-up."

            output HandoffRouteBindingComment: "Handoff Route Binding Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required

                next_owner: route.next_owner
                next_owner_key: route.next_owner.key

                route_summary: "Route Summary"
                    "{{route.summary}}"

            agent HandoffRouteBindingDemo:
                role: "Read route truth from handoff routing."
                outputs: "Outputs"
                    HandoffRouteBindingComment

                handoff_routing: "Handoff Routing"
                    "Route through compiler-owned handoff routing."

                    law:
                        active when true
                        stop "Hand off or finish the turn."
                        route "Hand off to ReviewLead." -> ReviewLead
            """,
            agent_name="HandoffRouteBindingDemo",
        )

        rendered = render_markdown(agent)
        self.assertIn("## Handoff Routing", rendered)
        self.assertIn("Route through compiler-owned handoff routing.", rendered)
        self.assertIn("- Next Owner: Review Lead", rendered)
        self.assertIn("- Next Owner Key: ReviewLead", rendered)
        self.assertIn("Hand off to ReviewLead. Next owner: Review Lead.", rendered)

    def test_handoff_routing_outputs_require_route_exists_guards_on_maybe_routed_branches(self) -> None:
        agent = self._compile_agent(
            """
            input RouteFacts: "Route Facts"
                source: Prompt
                shape: JsonObject
                requirement: Required
                should_route: "Should Route"

            agent ReviewLead:
                role: "Own routed follow-up."
                workflow: "Follow Up"
                    "Take the routed follow-up."

            output TurnResultComment: "Turn Result Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required

                kind: "handoff" when route.exists
                next_owner: route.next_owner.key when route.exists

                kind: "done" when route.exists == false
                summary: "Write one short closeout summary." when route.exists == false

            agent HandoffMaybeRouteDemo:
                role: "Keep route truth in the output contract."
                inputs: "Inputs"
                    RouteFacts
                outputs: "Outputs"
                    TurnResultComment

                handoff_routing: "Handoff Routing"
                    "Route only when the host route facts require it."

                    law:
                        active when true
                        stop "Hand off or finish the turn."
                        route "Hand off to ReviewLead." -> ReviewLead when RouteFacts.should_route
            """,
            agent_name="HandoffMaybeRouteDemo",
        )

        rendered = render_markdown(agent)
        self.assertIn("#### Kind", rendered)
        self.assertIn("Show this only when a routed owner exists.", rendered)
        self.assertIn("Show this only when not (a routed owner exists).", rendered)
        self.assertIn("#### Next Owner", rendered)
        self.assertIn("ReviewLead", rendered)

    def test_handoff_routing_prose_routes_do_not_seed_route_semantics(self) -> None:
        error = self._compile_error(
            """
            agent ReviewLead:
                role: "Own routed follow-up."
                workflow: "Follow Up"
                    "Take the routed follow-up."

            output HandoffRouteBindingComment: "Handoff Route Binding Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required

                next_owner: route.next_owner when route.exists

            agent ProseOnlyHandoffDemo:
                role: "Keep prose handoff routes readable."
                outputs: "Outputs"
                    HandoffRouteBindingComment

                handoff_routing: "Handoff Routing"
                    ready_for_review: "Ready For Review"
                        route "Hand off to ReviewLead." -> ReviewLead
            """,
            agent_name="ProseOnlyHandoffDemo",
        )

        self.assertEqual(error.code, "E338")
        self.assertIn("disallowed source", str(error))
        self.assertIn("route.exists", str(error))

    def test_handoff_routing_conflicts_with_other_live_route_surface(self) -> None:
        error = self._compile_error(
            """
            agent ReviewLead:
                role: "Own routed follow-up."
                workflow: "Follow Up"
                    "Take the routed follow-up."

            output HandoffRouteBindingComment: "Handoff Route Binding Comment"
                target: TurnResponse
                shape: Comment
                requirement: Required

                next_owner: route.next_owner

            workflow RoutedWorkflow: "Routed Workflow"
                "Always route through workflow law."

                law:
                    active when true
                    current none
                    stop "Reply and stop."
                    route "Hand off to ReviewLead." -> ReviewLead

            agent ConflictingRouteSurfaceDemo:
                role: "Do not let two route surfaces drive one output."
                workflow: RoutedWorkflow
                outputs: "Outputs"
                    HandoffRouteBindingComment

                handoff_routing: "Handoff Routing"
                    "Route through handoff routing too."

                    law:
                        active when true
                        stop "Hand off or finish the turn."
                        route "Hand off to ReviewLead from handoff routing." -> ReviewLead
            """,
            agent_name="ConflictingRouteSurfaceDemo",
        )

        self.assertEqual(error.code, "E343")
        self.assertIn("workflow, handoff_routing", str(error))

    def test_handoff_routing_law_rejects_currentness_statements(self) -> None:
        error = self._compile_error(
            """
            output SimpleReply: "Simple Reply"
                target: TurnResponse
                shape: CommentText
                requirement: Required

            agent InvalidHandoffLawDemo:
                role: "Keep handoff routing limited to route semantics."
                outputs: "Outputs"
                    SimpleReply

                handoff_routing: "Handoff Routing"
                    law:
                        current none
                        stop "Reply and stop."
            """,
            agent_name="InvalidHandoffLawDemo",
        )

        self.assertEqual(error.code, "E344")
        self.assertIn("unsupported statement `current none`", str(error))


if __name__ == "__main__":
    unittest.main()
