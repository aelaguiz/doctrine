# Worklog

Plan doc: docs/BIG_ASS_DUMP_EXHAUSTIVE_IMPLEMENTATION_AUDIT_2026-04-12.md

## Initial entry
- Run started.
- Current phase: Phase 1 - Freeze the semantic closure matrix before writing code

## 2026-04-12 - Parent implementation pass completed

- Phase 1:
  - locked the closure matrix
  - chose the shipped verdicts:
    - ship `prove ... from ...`
    - ship `sequencing_proof required`
    - accept `winner required` as syntax that normalizes to `choose one winner`
    - reject literal `solver_screen graded_reps`
    - retire authored `current_artifact`, `own_only`, and `preserve_exact`
      render-profile targets
    - parser-ban `schema:` + `structure:`
- Phase 2:
  - implemented `prove ... from ...` in grammar, parser, model, compiler,
    docs, examples, and VS Code parity
  - updated `examples/54_analysis_attachment`
- Phase 3:
  - implemented `sequencing_proof required`
  - normalized `winner required` to `choose one winner`
  - documented `solver_screen graded_reps` as rejected
  - updated `examples/74_decision_attachment`
- Phase 4:
  - added parser-first `schema:` + `structure:` conflict rejection
  - added negative proof in `examples/55_owner_aware_schema_attachments`
  - retired authored law-shaped `render_profile` targets and added negative
    proof in `examples/64_render_profiles_and_properties`
- Phase 5:
  - updated live docs and examples to the final shipped story
  - updated VS Code keyword parity for `prove` and `sequencing_proof`

Verification:

- `uv sync`
- `npm ci`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/54_analysis_attachment/cases.toml --manifest examples/55_owner_aware_schema_attachments/cases.toml --manifest examples/64_render_profiles_and_properties/cases.toml --manifest examples/74_decision_attachment/cases.toml`
- `make verify-diagnostics`
- `make verify-examples`
- `cd editors/vscode && make`

Notes:

- full corpus verify finished with no checked ref diffs and no surfaced
  inconsistencies
- the session-scoped `implement-loop` state remains armed
- fresh `audit-implementation` still owns the authoritative code verdict
