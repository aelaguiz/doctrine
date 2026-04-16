# Worklog

Plan doc: docs/PREVIOUS_TURN_OUTPUT_INPUT_SOURCE_REFERENCES_2026-04-16.md

## Initial entry
- Run started.
- Current phase: Phase 1 - Doctrine derived-source contract.
- Current focus:
  - Add a source-specific previous-turn input contract model.
  - Teach emit-time compilation to resolve zero-config previous final-output
    exactly from the target flow graph.
  - Add the first `io` payload emission path on the existing contract file.

## Doctrine-only completion
- Scope stayed inside the Doctrine repo. `../rally` and `../psflows` were left
  out of scope.
- Repaired guard validation so ordinary `shape: JsonObject` inputs still work
  in workflow-law and output guards for:
  - direct input roots
  - agent-local input bindings
- Added focused regressions in `tests/test_route_output_semantics.py` for
  direct and bound dynamic JsonObject input reads.
- Refreshed the eleven checked-in
  `examples/*/build_ref/*/final_output.contract.json` files that needed the new
  additive top-level `io` block.
- Updated Doctrine docs and release truth:
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/EMIT_GUIDE.md`
  - `docs/VERSIONING.md`
  - `CHANGELOG.md`
- Restored the dedicated `E470` review-family inheritance diagnostic so the
  shipped compile-fail corpus matches the intended review-shape error.
- Final proof:
  - `uv run --locked python -m unittest tests.test_route_output_semantics tests.test_output_rendering tests.test_emit_docs tests.test_compile_diagnostics`
  - `make verify-diagnostics`
  - `make verify-package`
  - `make verify-examples`

## Plan repair after fresh audit
- A fresh child audit reopened Phases 3 through 5 because the overall plan
  still includes Rally runtime work and the Lessons proof chain.
- I did not touch `../rally` or `../psflows`.
- I repaired the plan artifact instead:
  - added an execution-scope note under `0.2 In scope`
  - marked Phase 3 blocked for this pass
  - marked Phase 4 blocked for this pass
  - marked Phase 5 partial for this pass
  - appended a matching Decision Log entry
- The implementation-loop state file is still armed for this doc/session.
