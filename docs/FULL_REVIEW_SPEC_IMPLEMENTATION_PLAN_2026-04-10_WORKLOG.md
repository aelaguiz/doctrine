# Worklog

Plan doc: docs/FULL_REVIEW_SPEC_IMPLEMENTATION_PLAN_2026-04-10.md

## Initial entry
- Run started.
- Current phase: Phase 1 — Review grammar and AST foundation

## 2026-04-10 — Phase 1 closed, Phase 2 and Phase 3 opened
- Added first-class review grammar, parser adapters, AST nodes, compiler indexing, and reserved agent-field handling for `review`.
- Implemented concrete review compilation with explicit review inheritance, review-contract gate export, outcome-branch validation, next-owner binding checks, guarded review-output refs, and baseline review rendering.
- Positive smoke: a concrete `review` agent now compiles and renders with guarded `ReviewVerdict` output sections.
- Negative smokes now fail on the review path for missing `fields`, invalid current carriers, non-exhaustive review matches, and multi-subject reviews without disambiguation.
- Verification run: `make verify-examples` passed after the compiler changes.

## 2026-04-10 — Phase 4 opened with example 43
- Added `examples/43_review_basic_verdict_and_route_coupling` as the first shipped review rung with one positive render contract and three adjacent compile negatives.
- Updated `AGENTS.md`, `docs/README.md`, and `examples/README.md` so the corpus range and review-ladder index match the shipped example set.
- Verification runs: `uv run --locked python -m doctrine.verify_corpus --manifest examples/43_review_basic_verdict_and_route_coupling/cases.toml`, `make verify-diagnostics`, and `make verify-examples` all passed.

## 2026-04-10 — Implement-loop follow-up on Phase 3 semantics and diagnostics
- Tightened review outcome branch collection to respect route-selection semantics instead of treating every nested `when` and `match` arm as simultaneously live. `route ... when ...` now participates in branch selection, `match` uses first-match-wins semantics with exhaustive fallthrough handling, and non-total review outcomes now fail with review-specific codes.
- Restricted review semantic names inside guarded output sections to review-bound `comment_output` surfaces instead of allowing `verdict` and `ReviewVerdict.*` globally across all outputs. The permission now follows the concrete agent’s resolved review comment output through inline outputs and outputs-block compilation.
- Aligned the review diagnostic mapping with the new compiler messages by adding reserved review coverage for invalid review declaration shape, non-total outcomes, multiple routes, and multiple currentness outcomes.
- Added review-specific diagnostic smoke coverage so `make verify-diagnostics` now exercises reserved review failures instead of only generic parse and compile bands.
- Verification runs in this environment passed: `uv run --locked python -m py_compile doctrine/compiler.py doctrine/diagnostics.py doctrine/diagnostic_smoke.py`, `uv run --locked python -m doctrine.verify_corpus --manifest examples/43_review_basic_verdict_and_route_coupling/cases.toml`, `make verify-diagnostics`, and `make verify-examples`.

## 2026-04-10 — Implement-loop follow-up on semantic/output agreement
- Added a resolved review outcome-agreement model so each terminal review branch now carries its resolved verdict, route, currentness result, carried semantic fields, and the best available reviewed-artifact subject identity instead of discarding branch semantics after structural validation.
- Review subject proof now accepts the explicit reviewed-artifact form when the bound `reviewed_artifact` output field structurally names exactly one declared subject member. Direct currentness proof and `subject_map` proof still work unchanged.
- Added semantic/output agreement validation for review-bound outputs: required `verdict` and `next_owner` bindings must stay live on the resolved branch, `next_owner` keeps the structural routed-target check under the review-specific band, current-artifact carrier fields must stay live for branches that declare currentness, carried `active_mode` and `trigger_reason` values must stay live in both the output shape and `trust_surface`, and `failing_gates` / `blocked_gate` must remain behind a guard that resolves with the `changes_requested` branch.
- Extended the reserved review diagnostics into the semantic/output-agreement range with live mappings for `E495` through `E499`, and widened review smoke coverage with representative `E496` and `E499` cases.
- Verification runs in this environment passed: `uv run --locked python -m py_compile doctrine/compiler.py doctrine/diagnostics.py`, `uv run --locked python -m doctrine.verify_corpus --manifest examples/43_review_basic_verdict_and_route_coupling/cases.toml`, `make verify-diagnostics`, and `make verify-examples`.

## 2026-04-10 — Implement-loop follow-up on exact gate identity
- Added a pre-outcome review gate collector and evaluator so concrete reviews now carry explicit gate-check branches before outcome routing. The compiler now tracks ordered local block gates, local reject gates, assertion-section identities, contract gate identities, and the accept-gate fallback in one canonical review path.
- Reject-side review agreement branches now bind exact `failing_gate_ids` and `blocked_gate_id` channels instead of the earlier placeholders. Contract failures are represented as ordered `contract.<gate_key>` identities, block failures retain source order with the first true block gate as `blocked_gate_id`, and accept-gate failure is emitted only when every earlier layer passed.
- Wired those exact gate identities into the resolved review semantic namespace so `failing_gates`, `blocked_gate`, `contract.passes`, `contract.failed_gates`, `contract.first_failed_gate`, `failed(contract.<gate>)`, and `passed(contract.<gate>)` all resolve from the same gate-identity model during review evaluation.
- Verification runs in this environment passed: `uv run --locked python -m py_compile doctrine/compiler.py`, `./.venv/bin/python -m py_compile doctrine/compiler.py`, `./.venv/bin/python -m doctrine.verify_corpus --manifest examples/43_review_basic_verdict_and_route_coupling/cases.toml`, `./.venv/bin/python -m doctrine.diagnostic_smoke`, `./.venv/bin/python -m doctrine.verify_corpus`, `make verify-diagnostics`, and `make verify-examples`.

## 2026-04-10 — Implement-loop follow-up on review semantic addressability
- Added a compiler-owned review semantic addressability layer for explicit lowercase `contract.*` and `fields.*` refs. Review-bound outputs now carry resolved semantic context keyed by the concrete `comment_output`, and the shared addressable path can traverse review contract facts, exported contract gates, and bound output-field aliases without inventing a second resolver.
- Guarded output validation now accepts explicit `fields.*` and `contract.*` refs, not just the earlier unqualified review field names. The review semantic evaluator now resolves `fields.verdict`, `fields.*` presence checks, `contract.passes`, `contract.failed_gates`, `contract.first_failed_gate`, and `failed(contract.<gate>)` / `passed(contract.<gate>)` from the same branch semantics used by output-agreement checks.
- Moved review prose interpolation off the early review-body resolution path and into the later compile pass where the resolved review semantic context exists. Review sections and review-bound output prose now interpolate `{{contract.*}}` and `{{fields.*}}` through the same compiler-owned addressable surface, and standalone-read guarded-detail checks now understand semantic field aliases that point into guarded output branches.
- Added direct smoke coverage that compiles and renders review prose and output guards using `{{contract.completeness}}`, `{{fields.reviewed_artifact}}`, `{{fields.next_owner}}`, and `fields.verdict == ReviewVerdict.changes_requested` so the addressability path is exercised end to end.
- Verification runs in this environment passed: `./.venv/bin/python -m py_compile doctrine/compiler.py doctrine/diagnostic_smoke.py`, `./.venv/bin/python -m doctrine.diagnostic_smoke`, `./.venv/bin/python -m doctrine.verify_corpus --manifest examples/43_review_basic_verdict_and_route_coupling/cases.toml`, `./.venv/bin/python -m doctrine.verify_corpus`, `make verify-diagnostics`, and `make verify-examples`.

## 2026-04-11 — Implement-loop follow-up on reserved review parse diagnostics
- Added live parser classification for the reserved review parse codes in `doctrine/diagnostics.py`. Illegal review-statement placement now surfaces as `E471`, and invalid guarded review match heads such as `else when ...` now surface as `E472`, instead of falling through to the generic unexpected-token band.
- Added direct diagnostic smoke coverage for both reserved parse failures so the shipped parser path now proves `E471` and `E472` with concrete review prompts.
- Extended `examples/43_review_basic_verdict_and_route_coupling` with two adjacent `parse_fail` negatives: one for illegal `block` placement inside `on_accept`, and one for an invalid guarded `else` match head. That keeps the new review parse codes manifest-backed on the shipped review ladder.
- Updated `docs/COMPILER_ERRORS.md` to document the full reserved review band and corrected the code-band overview so `E470`-`E499` are described as review-specific parse/compile errors rather than hidden inside the generic compile range.
- Verification runs in this environment passed: `uv sync`, `./.venv/bin/python -m py_compile doctrine/diagnostics.py doctrine/diagnostic_smoke.py`, `./.venv/bin/python -m doctrine.diagnostic_smoke`, `./.venv/bin/python -m doctrine.verify_corpus --manifest examples/43_review_basic_verdict_and_route_coupling/cases.toml`, `make verify-diagnostics`, and `make verify-examples`.

## 2026-04-11 — Implement-loop follow-up on corpus, docs, and VS Code convergence
- Fixed one real parser defect in review inheritance by normalizing generic `review_item_key` values to string keys. That unblocked shipped `inherit shared_checks` / `override shared_checks:` behavior and narrowed duplicate inherited-section failures to the intended `E491` path.
- Finished the review ladder through `49_review_capstone`. Examples `47`, `48`, and `49` now ship fully commented prompts plus adjacent invalid cases for subject-set disambiguation, carried-field bindings, missing inherited sections, duplicate inherited-section accounting, illegal concrete attachment of `abstract review`, mixed `current none` / `current artifact`, illegal outcome-local `block`, and disallowed review-output guards.
- Closed the last multi-subject blocked-review semantic gap in the compiler. Blocked `current none` reject branches in reviews that actually define block gates may now remain honest without inventing a fake reviewed subject, which lets the capstone match the spec’s handoff-first blocked-review shape.
- Added live capstone proof for review semantic refs in output prose with `{{fields.reviewed_artifact}}` and `{{contract.clarity}}`, keeping the compiler, renderer, and editor resolver aligned on the shipped lowercase review semantic surface.
- Updated live docs and indexes so shipped truth now consistently runs through review example `49`, promotes `docs/REVIEW_SPEC.md` as live shipped reference, removes stale "`review` is not shipped" wording, and explicitly documents VS Code full review colorization plus Ctrl/Cmd-follow review refs.
- Extended the VS Code proof surface with capstone review resolver coverage for `contract.<gate>` and `fields.<semantic_field>` refs, added a review capstone snapshot fixture, and verified the packaged extension still passes unit, snapshot, integration, alignment, and VSIX packaging checks.
- Verification runs in this environment passed: `uv sync`, `./.venv/bin/python -m py_compile doctrine/compiler.py doctrine/parser.py doctrine/diagnostics.py doctrine/diagnostic_smoke.py doctrine/model.py`, `./.venv/bin/python -m doctrine.verify_corpus --manifest examples/44_review_handoff_first_block_gates/cases.toml --manifest examples/45_review_contract_gate_export_and_exact_failures/cases.toml --manifest examples/46_review_current_truth_and_trust_surface/cases.toml --manifest examples/47_review_multi_subject_mode_and_trigger_carry/cases.toml --manifest examples/48_review_inheritance_and_explicit_patching/cases.toml --manifest examples/49_review_capstone/cases.toml`, `make verify-diagnostics`, `make verify-examples`, and `cd editors/vscode && make`.

## 2026-04-11 — Implement-loop follow-up on final live-truth cleanup
- Updated `AGENTS.md` so the repo instruction layer now names `examples/49_review_capstone` as the shipped corpus endpoint instead of stopping at `43`.
- Rewrote Section 19 of `docs/REVIEW_SPEC.md` from pre-ship "Remaining holes" follow-through wording into shipped-reference maintenance guidance, so the canonical live review reference no longer reads like unresolved implementation work.
- Re-ran the authoritative final verification commands in this environment after the live-truth cleanup: `uv sync`, `make verify-examples`, `make verify-diagnostics`, and `cd editors/vscode && make`. All four passed.
- Updated the authoritative implementation audit and reopened Phase 6 / Phase 8 plan sections back to the completed state so the arch-step artifact matches the repo's current shipped truth.

## 2026-04-11 — Implement-loop follow-up on I/O reference cleanup
- Updated `docs/AGENT_IO_DESIGN_NOTES.md` so the shipped I/O reference now runs through examples `08` to `49`, references `docs/REVIEW_SPEC.md` as live review truth, and documents review `comment_output` carriers, `active_mode` / `trigger_reason`, review-bound guarded semantic refs, and output-agreement checks.
- Re-ran the authoritative final verification commands after the I/O reference cleanup: `uv sync`, `make verify-examples`, `make verify-diagnostics`, and `cd editors/vscode && make`. All four passed.
- Updated the authoritative implementation audit plus Phase 6 / Phase 8 back to complete so the canonical arch artifact now matches the repo's current code, docs, and editor truth.
