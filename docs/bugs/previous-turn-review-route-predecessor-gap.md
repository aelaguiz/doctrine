---
title: previous-turn emit missed review outcome predecessors
date: 2026-04-16
status: resolved
owners:
  - codex
reviewers: []
related:
  - doctrine/_compiler/flow.py
  - tests/test_emit_docs.py
  - tests/test_emit_flow.py
---

<!-- bugs:block:tldr:start -->
## TL;DR

- Symptom: emit-time previous-turn validation said an explicit selector had no reachable predecessor agent when the handoff came from `review.on_reject -> Agent`.
- Impact: Doctrine could not emit the Rally-shaped poem-loop review path even though review routing is already a shipped route-bearing surface.
- Most likely cause: flow extraction never turned attached review outcome routes into agent-to-agent predecessor edges.
- Next action: keep this covered by focused flow and emit regressions.
- Status: resolved
<!-- bugs:block:tldr:end -->

<!-- bugs:block:analysis:start -->
## Bug North Star

Doctrine emit must treat attached review routes as real predecessor edges for
previous-turn analysis.

## Bug Summary

The failing shape had three parts:

- a concrete agent with an attached `review:`
- a live `on_reject` route that hands work to another concrete agent
- a downstream `RallyPreviousTurnOutput` input with an explicit selector to the
  shared review final response

Before the fix, Doctrine already resolved review route semantics for emitted
route metadata, but flow extraction did not project those branches into
agent-to-agent edges. That left previous-turn validation with an empty
predecessor set and it failed with `Previous-turn selector ... has no reachable
predecessor agent.`

## Evidence

- Review route semantics already lower through
  `validate/route_semantics_context.py`.
- Agent route-semantic source selection already treats `review` as one
  route-bearing control surface.
- `emit_docs._build_previous_turn_contexts()` derives predecessor facts only
  from agent-to-agent flow edges.
- `flow.py` synthesized those edges for workflow routes and `final_output.route`
  but not for attached review outcome routes.
<!-- bugs:block:analysis:end -->

<!-- bugs:block:fix_plan:start -->
## Fix Plan

1. Reuse the existing attached-review route semantics path in `flow.py`.
2. Turn live review branches into `authored_route` agent-to-agent edges.
3. Add one focused flow test for review-route edge extraction.
4. Add one focused emit test for explicit previous-turn selection through a
   review reject route.
<!-- bugs:block:fix_plan:end -->

<!-- bugs:block:implementation:start -->
## Implementation

- Added `_collect_flow_from_review_route_context()` in
  `doctrine/_compiler/flow.py`.
  It resolves the attached review once, builds the live route context, and
  forwards those branches into normal agent-to-agent route edges.
- Added `_collect_flow_from_authored_route_context()` in
  `doctrine/_compiler/flow.py`.
  This keeps `final_output.route` and attached review routes on one shared edge
  path.
- Added
  `tests.test_emit_flow.EmitFlowCliTests.test_extract_graph_adds_route_edges_for_review_outcomes`.
  This pins the raw review predecessor edges.
- Added
  `tests.test_emit_docs.EmitDocsTests.test_emit_target_serializes_previous_turn_io_for_review_reject_route_selector`.
  This pins the shipped `final_output.contract.json` proof for the review reject
  previous-turn path.
- Updated `CHANGELOG.md` and `docs/VERSIONING.md` because this restores a
  broken stable emit surface at patch scope.

## Verification

- `uv run --locked python -m unittest tests.test_emit_flow.EmitFlowCliTests.test_extract_graph_adds_route_edges_for_review_outcomes`
- `uv run --locked python -m unittest tests.test_emit_docs.EmitDocsTests.test_emit_target_serializes_previous_turn_io_for_review_reject_route_selector`
- `uv run --locked python -m unittest tests.test_emit_flow tests.test_emit_docs tests.test_review_imported_outputs tests.test_output_rendering`
- `make verify-examples`

## Proof Surface Note

I did not add a new manifest-backed example for this bug. The focused flow test
pins the missing predecessor edge, and the focused emit test pins the shipped
contract output on the exact review-route previous-turn path.
<!-- bugs:block:implementation:end -->
