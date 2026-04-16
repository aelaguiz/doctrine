---
title: "Doctrine - First-Class Selected Route Final Outputs - Worklog"
date: 2026-04-16
doc_type: implementation_worklog
related:
  - docs/FIRST_CLASS_SELECTED_ROUTE_FINAL_OUTPUTS_2026-04-16.md
---

# Worklog

Plan doc: docs/FIRST_CLASS_SELECTED_ROUTE_FINAL_OUTPUTS_2026-04-16.md

## Initial entry
- Run started under `miniarch-step auto-implement`.
- Current phase: Phase 1 - Surface Syntax And Authored Model.
- Loop state will stay armed at `.codex/miniarch-step-implement-loop-state.019d95bf-019d-7dc3-b9e8-46e22ba1a43c.json` until the fresh audit path clears it.

## Implementation progress
- Compiler, parser, route semantics, emit, and example work for first-class
  routed final outputs are in place in the shipped repo.
- Focused route-field proof passed:
  `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_final_output tests.test_output_schema_lowering tests.test_route_output_semantics tests.test_emit_docs`
- Focused manifest proof passed:
  `uv run --locked python -m doctrine.verify_corpus --manifest examples/120_route_field_final_output_contract/cases.toml --manifest examples/121_nullable_route_field_final_output_contract/cases.toml`
- Full shipped corpus passed:
  `make verify-examples`

## Editor follow-through
- Added VS Code syntax coverage for:
  - `route field`
  - `override route field`
  - inline route-choice rows
  - nested `final_output.route:`
- Updated editor unit syntax proof and Lark-alignment checks for those forms.
- Ran `cd editors/vscode && make`.
- That check did not finish cleanly in this environment.
  - First failure: `@vscode/test-electron` request timeout during integration.
  - Retry failure: VS Code update API response parse failure while resolving
    the test host version.
- Unit and snap grammar checks passed before the integration timeout.

## Consistency pass
- The plan and public docs now use the same `nullable route field` story as
  the shipped examples and passing proof.
