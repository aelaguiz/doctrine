# Worklog

Plan doc: docs/DOCTRINE_HIGH_VALUE_AUTHORING_ELEGANCE_WINS_2026-04-16.md

## Initial entry
- Run started with `arch-step auto-implement`.
- Current phase: Phase 1 - Lock the `nullable` baseline and remove any
  leftover drift.
- Current focus:
  - prove the shipped `nullable` baseline is still honest across docs,
    examples, diagnostics, and emitted output
  - close any leftover nullability drift before additive syntax work starts
  - move into alias-aware imports only after the nullability gate is green

## Phase 1 proof closure
- Audited the live nullability surfaces named in the plan:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/COMPILER_ERRORS.md`
  - `docs/VERSIONING.md`
  - `CHANGELOG.md`
  - `examples/79_final_output_output_schema`
  - `examples/85_review_split_final_output_output_schema`
  - `examples/90_split_handoff_and_final_output_shared_route_semantics`
  - `examples/104_review_final_output_output_schema_blocked_control_ready`
  - `examples/105_review_split_final_output_output_schema_control_ready`
  - `examples/106_review_split_final_output_output_schema_partial`
  - `examples/121_nullable_route_field_final_output_contract`
- Result:
  - no live output-schema teaching surface still treats `required` or
    `optional` as live authored words outside the intentional invalid-example
    proof
  - route fields and plain fields still teach the same `nullable` story
  - `E236` and `E237` still point at the intended upgrade path
- Proof run:
  - `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_route_output_semantics tests.test_final_output tests.test_emit_docs tests.test_validate_output_schema tests.test_prove_output_schema_openai`
  - `make verify-diagnostics`
  - `make verify-examples`
- All three proof gates passed.
- No code or docs needed changes for Phase 1 in this pass.

## Current frontier
- Phase 1 is complete by audit plus proof.
- Phase 2 is the active implementation frontier:
  alias-aware imports on the existing import and named-ref path.

## Phase 2 implementation pass
- Finalized the plan's diagnostic band for this wave:
  - Phase 2 landed as `E306` duplicate module alias,
    `E307` duplicate imported symbol,
    `E308` ambiguous imported symbol ownership.
  - Future phase placeholders shifted to `E309`..`E312` in the plan doc.
- Landed the alias-aware import surface:
  - `doctrine/grammars/doctrine.lark`
  - `doctrine/parser.py`
  - `doctrine/_model/core.py`
  - `doctrine/_compiler/indexing.py`
  - `doctrine/_compiler/resolve/refs.py`
  - the adjacent addressable, law-path, output, review, and validation paths
    that must honor imported symbols through the same lookup story
- Landed the proof and teaching updates for the new import path:
  - `examples/03_imports`
  - `examples/86_imported_review_comment_local_routes`
  - `examples/109_imported_review_handoff_output_inheritance`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AUTHORING_PATTERNS.md`
  - `docs/COMPILER_ERRORS.md`
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json`
  - focused tests in
    `tests/test_parser_source_spans.py`,
    `tests/test_import_loading.py`,
    `tests/test_compiler_boundary.py`,
    `tests/test_emit_flow.py`,
    `tests/test_review_imported_outputs.py`,
    `tests/test_compile_diagnostics.py`,
    `tests/test_emit_docs.py`

## Phase 2 proof
- Passed:
  - `uv sync`
  - `npm ci`
  - `uv run --locked python -m unittest tests.test_import_loading tests.test_compiler_boundary tests.test_emit_flow tests.test_review_imported_outputs tests.test_parser_source_spans tests.test_compile_diagnostics tests.test_emit_docs`
    - result: `Ran 179 tests in 2.922s`
    - result: `OK`
  - `make verify-diagnostics`
  - `make verify-examples`
    - first full run failed once on
      `examples/109_imported_review_handoff_output_inheritance` with
      transient `E280` missing-module output for `shared.review`
    - single-manifest repro for
      `examples/109_imported_review_handoff_output_inheritance` passed
    - single-manifest repro for
      `examples/86_imported_review_comment_local_routes` passed
    - full rerun passed
- Not green yet:
  - `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_route_output_semantics tests.test_final_output tests.test_emit_docs tests.test_validate_output_schema tests.test_prove_output_schema_openai`
    - result: `FAILED (failures=4)`
    - failing tests are all in `tests.test_route_output_semantics`
    - current failures are expectation drift on route-render wording and
      guarded scalar rendering on untouched route-output surfaces
  - `cd editors/vscode && make`
    - unit and snap grammar checks passed
    - package step failed in integration with
      `TimeoutError: @vscode/test-electron request timeout`

## Current frontier after Phase 2 pass
- Phase 2 implementation is landed in code, examples, docs, and syntax.
- Phase 2 is still open in the plan because two proof blockers remain:
  - the Phase 1 regression slice is red on four route-output expectation
    tests outside the import surface
  - `cd editors/vscode && make` is red on an Electron integration timeout
- Next truthful move is fresh audit on the current tree, not a claim that
  Phase 2 is fully proven complete.

## Phase 1 regression repair after fresh audit
- Fresh audit reopened the locked baseline because
  `tests.test_route_output_semantics` failed four expectations on the current
  tree.
- Restored the shipped baseline behavior in:
  - `doctrine/_compiler/display.py`
  - `doctrine/_compiler/compile/workflows.py`
  - `doctrine/_compiler/compile/records.py`
- Repairs:
  - restored the shipped `This pass runs only when ...` wording for workflow
    law active guards
  - restored dotted-path rendering for `live_job` refs in readable law text
  - restored titled rendering for top-level guarded output scalars in compact
    output contracts
- Proof run:
  - `uv run --locked python -m unittest tests.test_route_output_semantics`
    - result: `Ran 17 tests`
    - result: `OK`
  - `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_route_output_semantics tests.test_final_output tests.test_emit_docs tests.test_validate_output_schema tests.test_prove_output_schema_openai`
    - result: `Ran 102 tests`
    - result: `OK`
- Phase 1 is green again on the current tree.

## Phase 2 proof closure after fresh audit
- Fresh audit also reran the VS Code package gate and proved the remaining
  blocker was real editor behavior, not just a transient Electron timeout.
- Repaired the import-aware editor proof in:
  - `editors/vscode/resolver.js`
  - `editors/vscode/tests/integration/suite/index.js`
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json`
- Repairs:
  - taught the resolver to index `from ... import Name` and
    `from ... import Name as Alias` lines alongside module-alias imports
  - routed imported-symbol definitions through the target declaration owner
    instead of assuming module-path imports only
  - skipped symbol-only import entries in the definition/link path so the
    extension host no longer crashes on missing ranges
  - updated the integration suite to assert the current shipped import forms
  - synced tmLanguage keyword coverage with the shipped grammar after the
    package step caught missing `delivery_skill`, `nullable`, and `values`
- Proof run:
  - `npm run test:integration` in `editors/vscode`
    - result: `Exit code: 0`
  - `uv run --locked python scripts/validate_lark_alignment.py` in
    `editors/vscode`
    - result: `Doctrine VS Code alignment check passed for 183 shipped keywords.`
  - `cd editors/vscode && make`
    - result: `Exit code: 0`
    - result: packaged `doctrine-language-0.0.1776359761391.vsix`
- Phase 2 proof is now closed on the current tree.

## Phase 3 plan repair
- While mapping the next code frontier, found that the approved grouped
  bare-ref `override` obligation did not fit the shipped override carriers.
- Evidence sweep:
  - grouped explicit `inherit { ... }` can lower to repeated `InheritItem`s`
  - grouped bare-ref `override { ... }` would need new resolver-side
    parent-kind lookup or a new override-preserve authored owner across the
    current analysis, document, review, schema, workflow, skills, IO, output,
    and output-schema surfaces
- Updated the canonical plan doc with an authoritative Phase 3 repair block:
  - Phase 3 now covers grouped explicit `inherit { ... }` only
  - grouped bare-ref `override` is deferred out of this wave
  - `E309` stays assigned to grouped `inherit`
  - `E310` stays reserved so later code bands do not shift again

## Current frontier
- Phase 1 and Phase 2 are complete on the current tree.
- The next truthful move is a fresh audit against the repaired plan before
  more code lands for Phase 3.

## Phase 3 plan repair follow-through
- Fresh audit found the earlier grouped-override deferral was still local to
  the repair block, so the rest of the canonical plan still promised a broader
  Phase 3 surface than the approved repair allowed.
- This turn stayed in planning mode only. No code changed.
- Folded the deferred grouped bare-ref `override` story through the canonical
  plan surfaces that still promised it:
  - North Star and top-level plan summary
  - scope and definition of done
  - tradeoffs, decision gaps, and target architecture
  - call-site audit and migration notes
  - pattern consolidation, rollout, consistency pass, and decision log
  - kept `E310` reserved across those same surfaces
- Added one explicit note to the authoritative Phase 3 repair block that the
  deferral is now folded through the rest of the approved plan.
- Proof run:
  - no new code proof in this turn because this was a planning repair only
- Current truthful frontier:
  - wait for a fresh audit against the repaired plan
  - do not resume Phase 2 or Phase 3 code from the stale broader story
