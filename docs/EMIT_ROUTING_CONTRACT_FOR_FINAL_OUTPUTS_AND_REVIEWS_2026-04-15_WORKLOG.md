# Worklog

Plan doc: docs/EMIT_ROUTING_CONTRACT_FOR_FINAL_OUTPUTS_AND_REVIEWS_2026-04-15.md

## Initial entry
- Run started under `miniarch-step implement-loop`.
- Current phase: Phase 1 - Shared Compile And Emit Route Contract.
- Loop state armed at `.codex/miniarch-step-implement-loop-state.019d9357-80b4-73e3-bd6d-fca0f13437ff.json`.

## Phase 1 (Shared Compile And Emit Route Contract) Progress Update
- Work completed:
  - Added compiled route contract types and attached one route contract to `CompiledAgent`.
  - Normalized route metadata in `doctrine/_compiler/compile/agent.py`.
  - Serialized a top-level `route` block from `doctrine/emit_docs.py`.
  - Added unit coverage for unrouted, routed, and review-routed final-output contracts.
- Tests run + results:
  - `uv run --locked python -m unittest tests.test_emit_docs tests.test_final_output tests.test_route_output_semantics` - passed.
- Issues / deviations:
  - None.
- Next steps:
  - Extend ordinary routed proof examples and emit smoke.

## Phase 2 (Ordinary Routed Final-Response Proof Ladder) Progress Update
- Work completed:
  - Extended emit smoke checks for routed and unrouted route blocks.
  - Added build-contract proof for workflow-law, handoff, and `route_from` examples.
  - Added `examples/119_route_only_final_output_contract` as the dedicated route-only final-output proof.
  - Kept `examples/111_inherited_output_route_semantics` unchanged because inherited final-output contract emission did not move.
- Tests run + results:
  - `make verify-diagnostics` - passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/87_workflow_route_output_binding/cases.toml --manifest examples/91_handoff_routing_route_output_binding/cases.toml --manifest examples/93_handoff_routing_route_from_final_output/cases.toml --manifest examples/104_review_final_output_output_schema_blocked_control_ready/cases.toml --manifest examples/105_review_split_final_output_output_schema_control_ready/cases.toml --manifest examples/106_review_split_final_output_output_schema_partial/cases.toml --manifest examples/119_route_only_final_output_contract/cases.toml` - passed.
- Issues / deviations:
  - The planned `116_route_only_final_output_contract` slot was already occupied by existing `116_*` examples. The implementation used next open slot `119_route_only_final_output_contract`.
- Next steps:
  - Extend review final-response proof.

## Phase 3 (Review Final-Response Route Proof Ladder) Progress Update
- Work completed:
  - Extended review route assertions in `tests/test_emit_docs.py`.
  - Added build-contract cases and checked-in refs for examples `104`, `105`, and `106`.
  - Split example `106` invalid agents into dedicated invalid prompt files so its default prompt can build.
  - Updated review diagnostic smoke checks to read those invalid prompt files.
- Tests run + results:
  - `uv run --locked python -m unittest tests.test_emit_docs` - passed.
  - Targeted review manifests for examples `104`, `105`, and `106` - passed.
  - `make verify-diagnostics` - passed.
- Issues / deviations:
  - Example `106` needed prompt-file split because a build-contract case compiles every concrete agent in the default prompt.
- Next steps:
  - Update public docs, versioning, changelog, and run final proof.

## Phase 4 (Public Docs, Versioning, And Full Proof) Progress Update
- Work completed:
  - Updated shipped docs and examples index for the top-level `route` block.
  - Updated `docs/VERSIONING.md` and `CHANGELOG.md` for the additive public contract surface.
  - Regenerated checked-in `build_ref/` trees for affected emitted final-output contracts.
- Tests run + results:
  - `uv sync` - passed.
  - `npm ci` - passed.
  - `uv run --locked python -m unittest tests.test_emit_docs tests.test_final_output tests.test_route_output_semantics` - passed.
  - `make verify-diagnostics` - passed.
  - `make verify-examples` - passed.
  - `make verify-package` - passed.
- Issues / deviations:
  - None.
- Next steps:
  - Leave loop state armed and let the fresh hook audit write the authoritative implementation verdict.
