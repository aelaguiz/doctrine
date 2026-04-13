# Elegant Doctrine Gap Closure Worklog

Plan: [docs/ELEGANT_DOCTRINE_GAP_CLOSURE_PLAN_2026-04-12.md](/Users/aelaguiz/workspace/doctrine/docs/ELEGANT_DOCTRINE_GAP_CLOSURE_PLAN_2026-04-12.md)

## 2026-04-12

- Started the implementation pass on branch `codex/elegant-gap-closure-20260412`.
- Armed implement-loop state at `.codex/implement-loop-state.019d8496-b98e-7921-9ee6-ec1ae41d46cf.json`.
- Reused the in-flight dirty worktree for the broad preservation, grounding,
  render-profile, and decision work already underway.
- Added inline `when` support for review-outcome `current artifact` /
  `current none` in:
  - `doctrine/grammars/doctrine.lark`
  - `doctrine/parser.py`
  - `doctrine/model.py`
  - `doctrine/compiler.py`
- Taught review outcome branch resolution to honor
  `missing(blocked_gate)` / `present(blocked_gate)` without tripping the
  mixed-currentness error on mutually exclusive reject paths.
- Restored route-only emitted labels to `Route to ...`.
- Centralized the touched law-target kind rules into
  `_LAW_TARGET_ALLOWED_KINDS` and `_PRESERVE_TARGET_ALLOWED_KINDS`.
- Added direct positive proof in
  `examples/46_review_current_truth_and_trust_surface/prompts/GUARDED_CURRENTNESS_ON_BLOCKED_GATE.prompt`
  and updated the manifest-backed expected contract in
  `examples/46_review_current_truth_and_trust_surface/cases.toml`.
- Synced docs to the shipped syntax:
  - `docs/SECOND_WAVE_LANGUAGE_NOTES.md`
  - `docs/INTEGRATION_SURFACES_SPEC.md`
  - `docs/REVIEW_SPEC.md`
  - `examples/README.md`
- Applied the follow-up doc repair from the fresh implementation audit:
  - `docs/WORKFLOW_LAW.md` now says `own only` may root in the current
    artifact, an emitted output surface the concrete turn owns, or a declared
    schema family.

## Verification

- `uv run --locked python -m doctrine.verify_corpus --manifest examples/46_review_current_truth_and_trust_surface/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/70_route_only_declaration/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/44_review_handoff_first_block_gates/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/49_review_capstone/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/68_review_family_shared_scaffold/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/69_case_selected_review_family/cases.toml`
- `uv sync`
- `npm ci`
- `make verify-diagnostics`
- `make verify-examples`
- `rg -n "owned paths must stay rooted|emitted output surface|declared schema family" docs/WORKFLOW_LAW.md`

## Deferred

- `.doc-audit-ledger.md` and `diff.txt` remain unrelated local scratch files.
- `docs/big_ass_dump.md` still requires restore-point handling before any
  deletion or archival move under repo doc-deletion safety.
