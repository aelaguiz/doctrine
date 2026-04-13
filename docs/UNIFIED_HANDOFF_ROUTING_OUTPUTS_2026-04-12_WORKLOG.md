# Universal Route Semantics For Outputs - Worklog

Plan: [UNIFIED_HANDOFF_ROUTING_OUTPUTS_2026-04-12.md](UNIFIED_HANDOFF_ROUTING_OUTPUTS_2026-04-12.md)

## 2026-04-12

### Phase 1 - Shared route substrate and validator

Status: COMPLETE

- Added compiler-owned `RouteSemanticContext` and `RouteSemanticBranch`
  resolution in `doctrine/compiler.py`.
- Threaded route semantics through output compilation, final-output lowering,
  readable blocks, interpolation, scalar rendering, and guard validation.
- Unified routed-owner honesty checks under one shared route-aware validator
  reused by review and `route_only`.
- Fixed two gaps discovered during live probes:
  - conditional workflow-law routes now keep unrouted-branch liveness honest
  - bare `RecordRef` route reads inside output sections now participate in the
    shared validator path

### Phase 2 - Proof corpus, docs, and teaching surfaces

Status: COMPLETE

- Added focused unit coverage in `tests/test_route_output_semantics.py`.
- Expanded `tests/test_final_output.py` to cover split prose and JSON
  `final_output:` contracts that consume shared `route.*` semantics.
- Added diagnostic smoke coverage for unguarded route reads and route-only
  rendered route semantics.
- Added manifest-backed examples:
  - `87_workflow_route_output_binding`
  - `88_review_route_semantics_shared_binding`
  - `89_route_only_shared_route_semantics`
  - `90_split_handoff_and_final_output_shared_route_semantics`
- Reality-synced the evergreen docs to teach plain dotted `route.*` refs and
  `when route.exists:` guards instead of proposal-only `from route.*` wording.

### Verification

Completed:

- `uv sync`
- `npm ci`
- `uv run --locked python -m unittest tests.test_route_output_semantics tests.test_final_output tests.test_review_imported_outputs`
- `uv run --locked python -m doctrine.diagnostic_smoke`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/87_workflow_route_output_binding/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/88_review_route_semantics_shared_binding/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/89_route_only_shared_route_semantics/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/90_split_handoff_and_final_output_shared_route_semantics/cases.toml`
- `make verify-diagnostics`
- `make verify-examples`
