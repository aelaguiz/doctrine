# Worklog

Plan doc: docs/PHASE4_REVIEW_ROUTE_ONLY_GROUNDING_CONTROL_PLANE_COMPLETION_2026-04-11.md

## Initial entry
- Run started.
- Current phase: Phase 2 - Review family and case-selected review core.

## Phase 2 closeout
- Added shipped `review_family` and case-selected review support to
  `doctrine/grammars/doctrine.lark`, `doctrine/model.py`,
  `doctrine/parser.py`, and `doctrine/compiler.py`.
- Added manifest-backed proof in:
  - `examples/68_review_family_shared_scaffold`
  - `examples/69_case_selected_review_family`
- Verified targeted manifests:
  - `examples/68_review_family_shared_scaffold/cases.toml`
  - `examples/69_case_selected_review_family/cases.toml`
  - preserved baselines `43`, `46`, `47`, `49`, and `57`

## Phase 3 closeout
- Added dedicated `route_only` and `grounding` declarations on the shared
  workflow path.
- Added manifest-backed proof in:
  - `examples/70_route_only_declaration`
  - `examples/71_grounding_declaration`
- Verified targeted manifests:
  - `examples/70_route_only_declaration/cases.toml`
  - `examples/71_grounding_declaration/cases.toml`
  - preserved route-only baselines `30`, `40`, `41`, and `42`

## Phase 4 closeout
- Widened invalidation to consume `schema.groups.*` and expand group members in
  authored order.
- Fixed the current-artifact versus invalidated-schema-group overlap bug on the
  shared law-path containment check.
- Added manifest-backed proof in:
  - `examples/72_schema_group_invalidation`
- Verified targeted manifests:
  - `examples/72_schema_group_invalidation/cases.toml`
  - preserved schema baseline `63`

## Phase 5 closeout
- Converged live docs and the surviving draft mechanics note so the repo no
  longer teaches the pre-Phase-4 restriction against `review_family` or
  dedicated `route_only`.
- Updated VS Code resolver and tmLanguage coverage for `review_family`,
  `route_only`, `grounding`, review `current_artifact`, and the new control
  keywords.
- Verification completed:
  - `uv sync`
  - `npm ci`
  - `make verify-examples`
  - `make verify-diagnostics`
  - `cd editors/vscode && make`
- Current phase: Complete.
