---
title: previous-turn emit crashed on root workflow readables and missed routed predecessors
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

- Symptom: `emit_docs` crashed with `AttributeError: 'ReadableBlock' object has no attribute 'target_unit'` when zero-config `RallyPreviousTurnOutput` forced emit-time predecessor extraction through workflows that owned root readable blocks.
- Impact: Doctrine could not emit the Rally-shaped previous-turn proof when the upstream handoff came from `final_output.route`.
- Most likely cause: flow extraction had two gaps. It treated root workflow readables like workflow-use items, and it did not add predecessor agent edges for `final_output.route`.
- Next action: keep this covered by the focused flow and emit regressions.
- Status: resolved
<!-- bugs:block:tldr:end -->

<!-- bugs:block:analysis:start -->
## Bug North Star

Doctrine emit must derive previous-turn facts from real routed predecessors without crashing on ordinary readable workflow content.

## Bug Summary

The failing shape had three parts:

- an upstream agent that routes through `final_output.route`
- a downstream agent that reads zero-config `rally.base_agent.RallyPreviousTurnOutput`
- workflows that contain ordinary root readable blocks such as `sequence` or `callout`

Before the fix, Doctrine failed in two ways:

- `flow.py` crashed on `ReadableBlock` while walking workflow items
- if that crash was removed, zero-config previous-turn resolution still failed with `E299` because the flow graph had no predecessor edge from `final_output.route`

## Evidence

- Local repro hit the reported crash in `doctrine/_compiler/flow.py:335` during `emit_docs._build_previous_turn_contexts()`.
- A second local repro without root readable blocks failed with `E299` and said the previous-turn input had no reachable predecessor final output.
- `ResolvedWorkflowBody.items` can contain `model.ReadableBlock` and `ResolvedUseItem`. The old traversal only handled sections, skills, and workflow-use items by attribute assumption.
- Route semantics for `final_output.route` are already resolved in `route_output_contexts`, but flow extraction did not turn those branches into agent-to-agent edges.
<!-- bugs:block:analysis:end -->

<!-- bugs:block:fix_plan:start -->
## Fix Plan

1. Make workflow-body flow extraction dispatch by resolved item kind instead of assuming every non-section item is a workflow-use item.
2. Skip `ReadableBlock` items during flow collection.
3. Add route edges for `final_output.route` branches so zero-config previous-turn resolution can find predecessor agents.
4. Add one focused flow-graph test and one focused emit test for the full previous-turn shape.
<!-- bugs:block:fix_plan:end -->

<!-- bugs:block:implementation:start -->
## Implementation

- Updated `doctrine/_compiler/flow.py` so `_collect_flow_from_workflow_body()` now:
  - recurses only on `ResolvedUseItem`
  - skips `ReadableBlock` and workflow skills
  - fails loud on any unexpected resolved workflow item instead of crashing on missing attributes
- Added `_collect_flow_from_final_output_route_contexts()` in `doctrine/_compiler/flow.py`.
  It turns `final_output.route` branches into agent-to-agent route edges during flow extraction.
- Added `tests.test_emit_flow.EmitFlowCliTests.test_extract_graph_adds_route_edges_for_final_output_route`.
  This pins the missing-predecessor half of the bug.
- Added `tests.test_emit_docs.EmitDocsTests.test_emit_target_serializes_previous_turn_io_for_route_field_final_output_with_root_readables`.
  This pins the full emit path with root readable workflows and zero-config previous-turn input.
- Updated `CHANGELOG.md` and `docs/VERSIONING.md` because this is a patch-level fix on a shipped emit surface.

## Verification

- `uv run --locked python -m unittest tests.test_emit_flow.EmitFlowCliTests.test_extract_graph_adds_route_edges_for_final_output_route`
- `uv run --locked python -m unittest tests.test_emit_docs.EmitDocsTests.test_emit_target_serializes_previous_turn_io_for_route_field_final_output_with_root_readables`
- `uv run --locked python -m unittest tests.test_emit_flow tests.test_emit_docs tests.test_output_rendering`
- `make verify-examples`

## Proof Surface Note

I did not add a new manifest-backed example for this bug. The focused flow test
pins the missing predecessor edge at the graph boundary, and the focused emit
test pins the shipped `final_output.contract.json` result on the exact failing
previous-turn path.
<!-- bugs:block:implementation:end -->
