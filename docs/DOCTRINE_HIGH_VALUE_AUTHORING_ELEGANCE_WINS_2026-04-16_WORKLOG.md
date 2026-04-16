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

## Phase 3 grouped inherit completion
- Landed grouped explicit `inherit { ... }` across the full approved inherited
  family without changing resolver semantics.
- Finalized `E309` for malformed grouped `inherit`.
- Updated shipped teaching surfaces in:
  - `examples/24_io_block_inheritance`
  - `examples/107_output_inheritance_basic`
  - `examples/108_output_inheritance_attachments`
- Updated live docs and editor syntax:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AUTHORING_PATTERNS.md`
  - `docs/COMPILER_ERRORS.md`
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json`
- Proof run:
  - `uv run --locked python -m unittest tests.test_grouped_inherit tests.test_parse_diagnostics tests.test_output_inheritance tests.test_parser_source_spans`
    - result: `Ran 48 tests`
    - result: `OK`
  - `make verify-diagnostics`
    - result: `diagnostic smoke checks passed`
  - `make verify-examples`
    - result: `PASS`
  - Phase 1 regression slice
    - result: `Ran 102 tests`
    - result: `OK`
  - `cd editors/vscode && make`
    - result: `Exit code 0`

## Phase 4 review-binding shorthand completion
- Landed bare identity shorthand on:
  - `review.fields`
  - `review override fields`
  - `final_output.review_fields`
- Kept all non-identity review binds explicit and kept explicit identity binds
  legal.
- Added focused shorthand proof in:
  - `tests/test_review_binding_shorthand.py`
  - `tests/test_parser_source_spans.py`
  - `tests/test_review_imported_outputs.py`
- Updated the shipped review examples:
  - `85`, `86`, `90`, `104`, `105`, and `106`
- Updated live docs and editor syntax:
  - `docs/REVIEW_SPEC.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AUTHORING_PATTERNS.md`
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json`
  - `editors/vscode/tests/unit/review.test.prompt`
- Proof run:
  - `uv run --locked python -m unittest tests.test_review_binding_shorthand tests.test_parser_source_spans tests.test_review_imported_outputs tests.test_final_output tests.test_emit_docs`
    - result: `Ran 67 tests`
    - result: `OK`
  - focused manifest proof for `85`, `86`, `90`, `104`, `105`, and `106`
    - result: all passed
  - `make verify-diagnostics`
    - result: `diagnostic smoke checks passed`
  - `make verify-examples`
    - result: `PASS`
  - Phase 1 regression slice
    - result: `Ran 102 tests`
    - result: `OK`
  - `cd editors/vscode && make`
    - result: `Exit code 0`

## Current frontier after Phase 4
- Phase 1 through Phase 4 are complete on the current tree.
- The next ordered frontier is Phase 5 IO wrapper shorthand.

## Phase 5 plan repair
- While grounding the next code frontier, found that two approved Phase 5
  obligations did not fit the shipped IO path or the shipped proof surface.
- Evidence sweep:
  - `key: NameRef` and `override key: NameRef` on first-class IO wrappers are
    parser sugar to one title-omitted `IoSection` or `OverrideIoSection`
    with one direct `RecordRef`
  - on the current `ValidateContractsMixin` ->
    `ResolveIoContractsMixin` -> `ResolveOutputsMixin` path, that sugar does
    not create the old planned shorthand-specific "multi-child ref" failure
    state; malformed title-omitted wrapper cases already ride the current
    omitted-title diagnostics path
  - `examples/24_io_block_inheritance` and
    `examples/117_io_omitted_wrapper_titles` are manifest-backed render and
    compile proof only; they do not ship
    `final_output.contract.json.io` sidecars
- Updated the canonical plan doc with an authoritative Phase 5 repair block:
  - Phase 5 still ships one-line `key: NameRef` and `override key: NameRef`
    on first-class `inputs` / `outputs` wrappers only
  - `E311` is no longer part of this wave and now stays reserved so later
    code bands do not shift
  - the Phase 5 proof surface now uses rewritten `24` / `117`
    manifest-backed render and compile cases plus targeted emitted-contract
    tests, instead of absent sidecar byte-equality
  - folded that repair through the canonical plan surfaces that still carried
    the old `E311` or `final_output.contract.json.io` story
- Proof run:
  - no new code proof in this turn because this was a planning repair only

## Current frontier after Phase 5 repair
- The next truthful move is a fresh audit against the repaired plan before
  Phase 5 code starts.

## Phase 5 IO wrapper shorthand completion
- Landed one-line first-class IO wrapper shorthand on:
  - `inputs`
  - `outputs`
  - base keyed wrappers
  - override keyed wrappers
- Lowered both shorthand forms to the existing title-omitted wrapper section
  path with one direct declaration ref. No sidecar IO lowering path was
  added.
- Added focused shorthand proof in:
  - `tests/test_parser_source_spans.py`
  - `tests/test_compile_diagnostics.py`
  - `tests/test_output_rendering.py`
  - `tests/test_emit_docs.py`
- Updated the shipped IO shorthand examples:
  - `24`
  - `117`
- Updated live docs and editor support:
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AUTHORING_PATTERNS.md`
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json`
  - `editors/vscode/tests/unit/io-blocks.test.prompt`
  - `editors/vscode/tests/integration/suite/index.js`
  - `editors/vscode/resolver.js`
- Proof run:
  - `uv run --locked python -m unittest tests.test_parser_source_spans tests.test_compile_diagnostics tests.test_output_rendering tests.test_emit_docs`
    - result: `Ran 226 tests`
    - result: `OK`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/24_io_block_inheritance/cases.toml`
    - result: all cases passed
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/117_io_omitted_wrapper_titles/cases.toml`
    - result: all cases passed
  - `make verify-diagnostics`
    - result: `diagnostic smoke checks passed`
  - `make verify-examples`
    - result: `PASS`
  - Phase 1 regression slice
    - result: `Ran 103 tests`
    - result: `OK`
  - `cd editors/vscode && make`
    - result: `Exit code 0`
    - result: packaged `doctrine-language-0.0.1776372227223.vsix`

## Current frontier after Phase 5
- Phase 1 through Phase 5 are complete on the current tree.
- The next ordered frontier is Phase 6 `self:` shorthand on the existing
  `PATH_REF` family.

## Phase 6 self-addressed `PATH_REF` shorthand completion
- Landed `self:` as a self-rooted `AddressableRef` shorthand on the approved
  existing `PATH_REF` family without adding a second addressable resolver or a
  sentinel root string.
- Bound self-rooted refs back to the current declaration root before normal
  addressable descent and kept malformed usage fail-loud on `E312`.
- Added focused proof in:
  - `tests/test_addressable_self_refs.py`
  - `tests/test_parser_source_spans.py`
  - `tests/test_compile_diagnostics.py`
- Updated the shipped self-root teaching example:
  - `examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt`
- Updated live docs and editor support:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AUTHORING_PATTERNS.md`
  - `docs/COMPILER_ERRORS.md`
  - `editors/vscode/resolver.js`
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json`
  - `editors/vscode/tests/integration/suite/index.js`
  - `editors/vscode/tests/unit/io-blocks.test.prompt`
- Proof run:
  - `uv sync`
    - result: `Checked 8 packages`
  - `npm ci`
    - result: `found 0 vulnerabilities`
  - `uv run --locked python -m unittest tests.test_addressable_self_refs tests.test_parser_source_spans tests.test_compile_diagnostics tests.test_route_output_semantics`
    - result: `Ran 202 tests`
    - result: `OK`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/28_addressable_workflow_paths/cases.toml`
    - result: all cases passed
  - Phase 1 regression proof
    - command: `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_route_output_semantics tests.test_final_output tests.test_emit_docs tests.test_validate_output_schema tests.test_prove_output_schema_openai`
    - result: `Ran 103 tests`
    - result: `OK`
  - `make verify-diagnostics`
    - result: `diagnostic smoke checks passed`
  - `make verify-examples`
    - result: `PASS`
  - `cd editors/vscode && make`
    - result: `Exit code 0`
    - result: packaged `doctrine-language-0.0.1776374108820.vsix`

## Current frontier after Phase 6
- Phase 1 through Phase 6 are complete on the current tree.
- The next ordered frontier is Phase 7 release truth, changelog alignment, and
  the full-wave proof sweep.

## Phase 7 release truth and full-wave proof completion
- Updated release truth in:
  - `docs/VERSIONING.md`
  - `CHANGELOG.md`
- Release-truth updates:
  - advanced the current Doctrine language line from `2.0` to `2.1`
  - recorded the high-value authoring wave as one additive language move
  - named shipped diagnostics `E306`, `E307`, `E308`, `E309`, and `E312`
  - kept `E310` reserved for the deferred grouped-override investigation
  - kept `E311` reserved for a future dedicated IO-wrapper shorthand
    diagnostic
- Checked the wave-level index surfaces:
  - `docs/README.md`
  - `examples/README.md`
  - result: no stale or deprecated teaching track needed a Phase 7 index edit
- Full wave proof run:
  - `uv sync`
    - result: `Checked 8 packages`
  - `npm ci`
    - result: `found 0 vulnerabilities`
  - `uv run --locked python -m unittest tests.test_import_loading tests.test_compiler_boundary tests.test_emit_flow tests.test_review_imported_outputs tests.test_output_inheritance tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_validate_output_schema tests.test_prove_output_schema_openai tests.test_route_output_semantics tests.test_final_output tests.test_emit_docs tests.test_output_rendering tests.test_compile_diagnostics`
    - result: `Ran 337 tests`
    - result: `OK`
  - `make verify-diagnostics`
    - result: `diagnostic smoke checks passed`
  - `make verify-examples`
    - result: `PASS`
  - `cd editors/vscode && make`
    - result: `Exit code 0`
    - result: packaged `doctrine-language-0.0.1776374108820.vsix`

## Current frontier after Phase 7
- Phase 1 through Phase 7 are complete on the current tree.
- The next truthful move is a fresh audit against the current plan and tree.
