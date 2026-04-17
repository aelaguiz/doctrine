from __future__ import annotations

from tempfile import TemporaryDirectory

from doctrine.compiler import compile_prompt
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown

from doctrine._diagnostic_smoke.fixtures import SmokeFailure, _expect, _write_prompt


def run_route_flow_checks() -> None:
    _check_route_output_read_requires_guard()
    _check_handoff_routing_output_can_render_route_semantics()
    _check_route_from_final_output_can_render_selected_owner()
    _check_route_choice_guard_can_narrow_route_summary()
    _check_route_field_final_output_can_render_route_choice_guards()
    _check_nullable_route_field_final_output_can_render_route_exists_guards()
    _check_final_output_route_rejects_non_route_field_binding()
    _check_route_from_selector_rejects_workflow_local_mode()
    _check_route_from_rejects_duplicate_route_choice()
    _check_route_summary_needs_one_selected_branch()
    _check_handoff_routing_law_rejects_currentness_statements()
    _check_non_route_slot_law_has_specific_code()
    _check_route_only_output_can_render_route_semantics()


def _check_route_output_read_requires_guard() -> None:
    source = """input RouteFacts: "Route Facts"
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
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "MaybeRouteBindingDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect("route semantics are not live on every branch" in str(exc), str(exc))
            _expect("guard the read with `route.exists`" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for unguarded route output read, but compilation succeeded")


def _check_handoff_routing_output_can_render_route_semantics() -> None:
    source = """agent ReviewLead:
    role: "Own routed follow-up."
    workflow: "Follow Up"
        "Take the routed follow-up."

output HandoffRouteBindingComment: "Handoff Route Binding Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    next_owner: route.next_owner

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
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "HandoffRouteBindingDemo"))
        _expect("## Handoff Routing" in rendered, rendered)
        _expect("- Next Owner: Review Lead" in rendered, rendered)
        _expect("Hand off to ReviewLead. Next owner: Review Lead." in rendered, rendered)


def _check_route_from_final_output_can_render_selected_owner() -> None:
    source = """enum ProofRoute: "Proof Route"
    accept: "Accept"
    change: "Change"

output ProofResult: "Proof Result"
    target: TurnResponse
    shape: Comment
    requirement: Required
    route_choice: "Route Choice"

output RouteFromReply: "Route From Reply"
    target: TurnResponse
    shape: Comment
    requirement: Required

    next_owner: route.next_owner.key

agent AcceptanceCritic:
    role: "Accept routed work."

agent ChangeEngineer:
    role: "Change routed work."

agent RouteFromFinalOutputDemo:
    role: "Read selected owner truth from route_from."
    outputs: "Outputs"
        ProofResult
        RouteFromReply
    final_output: RouteFromReply

    handoff_routing: "Handoff Routing"
        law:
            route_from ProofResult.route_choice as ProofRoute:
                ProofRoute.accept:
                    route "Send to AcceptanceCritic." -> AcceptanceCritic
                ProofRoute.change:
                    route "Send to ChangeEngineer." -> ChangeEngineer
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "RouteFromFinalOutputDemo"))
        _expect("- Next Owner: the selected route's next owner key" in rendered, rendered)
        _expect("Choose a route from ProofResult.route_choice." in rendered, rendered)


def _check_route_choice_guard_can_narrow_route_summary() -> None:
    source = """enum ProofRoute: "Proof Route"
    accept: "Accept"
    change: "Change"

output ProofResult: "Proof Result"
    target: TurnResponse
    shape: Comment
    requirement: Required
    route_choice: "Route Choice"

output RouteChoiceReply: "Route Choice Reply"
    target: TurnResponse
    shape: Comment
    requirement: Required

    accept_summary: "Accept Summary" when route.choice == ProofRoute.accept
        "{{route.summary}}"

agent AcceptanceCritic:
    role: "Accept routed work."

agent ChangeEngineer:
    role: "Change routed work."

agent RouteChoiceGuardDemo:
    role: "Use route.choice to narrow route detail."
    outputs: "Outputs"
        ProofResult
        RouteChoiceReply

    handoff_routing: "Handoff Routing"
        law:
            route_from ProofResult.route_choice as ProofRoute:
                ProofRoute.accept:
                    route "Send to AcceptanceCritic." -> AcceptanceCritic
                ProofRoute.change:
                    route "Send to ChangeEngineer." -> ChangeEngineer
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "RouteChoiceGuardDemo"))
        _expect("Show this only when route.choice is Accept." in rendered, rendered)
        _expect("Send to AcceptanceCritic. Next owner: Acceptance Critic." in rendered, rendered)


def _check_route_field_final_output_can_render_route_choice_guards() -> None:
    source = """output schema WriterDecisionSchema: "Writer Decision Schema"
    route field next_route: "Next Route"
        seek_muse: "Send to Muse." -> Muse
        ready_for_critic: "Send to Critic." -> Critic

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

agent Muse:
    role: "Help the writer."
    workflow: "Muse"
        "Offer one fresh image."

agent Critic:
    role: "Judge the draft."
    workflow: "Critic"
        "Judge the draft."

agent WriterRouteFieldDemo:
    role: "Choose the next owner on the final output."
    outputs: "Outputs"
        WriterDecision
    final_output:
        output: WriterDecision
        route: next_route
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "WriterRouteFieldDemo"))
        _expect("## Final Output" in rendered, rendered)
        _expect(
            "Show this only when route.choice is WriterDecisionSchema.next_route.seek_muse."
            in rendered,
            rendered,
        )
        _expect("Send to Muse. Next owner: Muse." in rendered, rendered)


def _check_nullable_route_field_final_output_can_render_route_exists_guards() -> None:
    source = """output schema WriterTurnResultSchema: "Writer Turn Result Schema"
    route field next_route: "Next Route"
        revise_more: "Send to RevisionPartner." -> RevisionPartner
        nullable

    field summary: "Summary"
        type: string

output shape WriterTurnResultJson: "Writer Turn Result JSON"
    kind: JsonObject
    schema: WriterTurnResultSchema

output WriterTurnResult: "Writer Turn Result"
    target: TurnResponse
    shape: WriterTurnResultJson
    requirement: Required

    routed_owner: "Routed Owner" when route.exists
        "{{route.next_owner}}"

    no_route: "No Route" when route.exists == false
        "There is no handoff on this turn."

agent RevisionPartner:
    role: "Take one more pass."
    workflow: "Revise"
        "Revise the draft."

agent WriterNullableRouteFieldDemo:
    role: "Either hand off or finish from one final output."
    outputs: "Outputs"
        WriterTurnResult
    final_output:
        output: WriterTurnResult
        route: next_route
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "WriterNullableRouteFieldDemo"))
        _expect("Show this only when a routed owner exists." in rendered, rendered)
        _expect("Show this only when not (a routed owner exists)." in rendered, rendered)
        _expect("There is no handoff on this turn." in rendered, rendered)


def _check_final_output_route_rejects_non_route_field_binding() -> None:
    source = """output schema WriterDecisionSchema: "Writer Decision Schema"
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
    outputs: "Outputs"
        WriterDecision
    final_output:
        output: WriterDecision
        route: next_route
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "Writer")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect("final_output.route must bind a `route field`" in str(exc), str(exc))
            return
        raise SmokeFailure(
            "expected compile failure for non-route final_output.route binding, but compilation succeeded"
        )


def _check_route_from_selector_rejects_workflow_local_mode() -> None:
    source = """enum ProofRoute: "Proof Route"
    accept: "Accept"

output ProofResult: "Proof Result"
    target: TurnResponse
    shape: Comment
    requirement: Required

agent AcceptanceCritic:
    role: "Accept routed work."

agent InvalidRouteFromSelectorDemo:
    role: "Keep route_from selectors on declared surfaces."
    outputs: "Outputs"
        ProofResult

    handoff_routing: "Handoff Routing"
        law:
            mode pass_mode = ProofRoute.accept as ProofRoute
            route_from pass_mode as ProofRoute:
                ProofRoute.accept:
                    route "Send to AcceptanceCritic." -> AcceptanceCritic
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "InvalidRouteFromSelectorDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E346", f"expected E346, got {getattr(exc, 'code', None)}")
            _expect("pass_mode" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for invalid route_from selector, but compilation succeeded")


def _check_route_from_rejects_duplicate_route_choice() -> None:
    source = """enum ProofRoute: "Proof Route"
    accept: "Accept"
    change: "Change"

input RouteFacts: "Route Facts"
    source: Prompt
    shape: JsonObject
    requirement: Required
    route_choice: "Route Choice"

agent AcceptanceCritic:
    role: "Accept routed work."

agent BackupCritic:
    role: "Backup routed work."

agent ChangeEngineer:
    role: "Change routed work."

workflow DuplicateRouteFromWorkflow: "Duplicate Route From Workflow"
    law:
        current none
        route_from RouteFacts.route_choice as ProofRoute:
            ProofRoute.accept:
                route "Send to AcceptanceCritic." -> AcceptanceCritic
            ProofRoute.accept:
                route "Send to BackupCritic." -> BackupCritic
            ProofRoute.change:
                route "Send to ChangeEngineer." -> ChangeEngineer

agent DuplicateRouteFromDemo:
    role: "Reject duplicate route_from choices."
    inputs: "Inputs"
        RouteFacts
    workflow: DuplicateRouteFromWorkflow
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "DuplicateRouteFromDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E348", f"expected E348, got {getattr(exc, 'code', None)}")
            _expect("Accept" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for duplicate route_from choice, but compilation succeeded")


def _check_route_summary_needs_one_selected_branch() -> None:
    source = """enum ProofRoute: "Proof Route"
    accept: "Accept"
    change: "Change"

output ProofResult: "Proof Result"
    target: TurnResponse
    shape: Comment
    requirement: Required
    route_choice: "Route Choice"

output RouteSummaryReply: "Route Summary Reply"
    target: TurnResponse
    shape: Comment
    requirement: Required

    route_summary: "Route Summary"
        "{{route.summary}}"

agent AcceptanceCritic:
    role: "Accept routed work."

agent ChangeEngineer:
    role: "Change routed work."

agent AmbiguousRouteSummaryDemo:
    role: "Do not read branch-specific route detail without narrowing."
    outputs: "Outputs"
        ProofResult
        RouteSummaryReply

    handoff_routing: "Handoff Routing"
        law:
            route_from ProofResult.route_choice as ProofRoute:
                ProofRoute.accept:
                    route "Send to AcceptanceCritic." -> AcceptanceCritic
                ProofRoute.change:
                    route "Send to ChangeEngineer." -> ChangeEngineer
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "AmbiguousRouteSummaryDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E347", f"expected E347, got {getattr(exc, 'code', None)}")
            _expect("route.summary" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for ambiguous route.summary, but compilation succeeded")


def _check_handoff_routing_law_rejects_currentness_statements() -> None:
    source = """output SimpleReply: "Simple Reply"
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
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "InvalidHandoffLawDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E344", f"expected E344, got {getattr(exc, 'code', None)}")
            _expect("current none" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for invalid handoff_routing law, but compilation succeeded")


def _check_non_route_slot_law_has_specific_code() -> None:
    source = """output SimpleReply: "Simple Reply"
    target: TurnResponse
    shape: CommentText
    requirement: Required

agent InvalidSlotLawDemo:
    role: "Keep law off plain authored slots."
    outputs: "Outputs"
        SimpleReply

    your_job: "Your Job"
        law:
            stop "Reply and stop."
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "InvalidSlotLawDemo")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E345", f"expected E345, got {getattr(exc, 'code', None)}")
            _expect("your_job" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for law on plain authored slot, but compilation succeeded")


def _check_route_only_output_can_render_route_semantics() -> None:
    source = """input RouteFacts: "Route Facts"
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
    role: "Handle reroutes when specialist work cannot continue safely."
    workflow: "Instructions"
        "Take back the same issue when the next specialist owner is still not justified."

workflow RouteOnlyTurns: "Routing-Only Turns"
    "Handle turns that can only stop, reroute, or keep ownership explicit."

    law:
        active when true
        current none
        stop "No specialist artifact is current for this turn."
        route "Keep the issue on RoutingOwner until the next specialist owner is clear." -> RoutingOwner when RouteFacts.next_owner_unknown

agent RouteOnlyRouteBindingDemo:
    role: "Read route truth from a route-only comment output."
    workflow: RouteOnlyTurns
    inputs: "Inputs"
        RouteFacts
    outputs: "Outputs"
        RouteOnlyHandoffOutput
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        rendered = render_markdown(compile_prompt(prompt, "RouteOnlyRouteBindingDemo"))
        _expect("#### Route Handoff" in rendered, rendered)
        _expect("Show this only when a routed owner exists." in rendered, rendered)
        _expect("- Next Owner: Routing Owner" in rendered, rendered)
        _expect(
            "Keep the issue on RoutingOwner until the next specialist owner is clear. Next owner: Routing Owner."
            in rendered,
            rendered,
        )
