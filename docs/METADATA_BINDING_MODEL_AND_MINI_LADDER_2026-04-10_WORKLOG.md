# Worklog

Plan: [METADATA_BINDING_MODEL_AND_MINI_LADDER_2026-04-10.md](/Users/aelaguiz/workspace/doctrine/docs/METADATA_BINDING_MODEL_AND_MINI_LADDER_2026-04-10.md)

## 2026-04-10

- Started `implement-loop` on branch `feature/metadata-binding-model-20260410-215227`.
- Confirmed the real loop runtime is installed:
  - `codex_hooks` is enabled.
  - `~/.agents/skills/arch-step/` contains the `implement_loop_stop_hook.py` runner.
  - `~/.codex/hooks.json` points Stop hooks at the implement-loop controller.
- Synced the repo with `uv sync`.
- Marked Phase 1 in progress before the first compiler edits.
- Landed the compiler-owned bound-root substrate in `doctrine/compiler.py`:
  - concrete-turn keyed `inputs:` and `outputs:` leaves now resolve as first-class workflow-law roots
  - bound roots normalize through the same currentness, carrier, invalidation, scope, and overlap checks as direct declaration roots
  - review currentness reuse now benefits from the same root-resolution path
- Updated diagnostics and live error docs for the new "declared or bound concrete-turn" wording where it became shipped truth.
- Added the shipped proof ladder:
  - `examples/50_bound_currentness_roots`
  - `examples/51_inherited_bound_io_roots`
  - `examples/52_bound_scope_and_preservation`
  - `examples/53_review_bound_carrier_roots`
- Updated live corpus/docs boundary to acknowledge the shipped ladder in:
  - `AGENTS.md`
  - `docs/README.md`
  - `examples/README.md`
  - `docs/WORKFLOW_LAW.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/LANGUAGE_DESIGN_NOTES.md`
  - `docs/COMPILER_ERRORS.md`
- Verification completed for this pass:
  - targeted manifests for `24`, `31`, `33`, `46`, `49`, `50`, `51`, `52`, and `53`
  - `make verify-diagnostics`
  - `make verify-examples`
- Remaining implementation still open for the next loop:
  - rewrite `examples/38_metadata_polish_capstone` onto the bound-root idiom
  - extend live review docs such as `docs/REVIEW_SPEC.md`
  - ship VS Code bound-root colorization and navigation parity
- Implement-loop follow-through pass landed the remaining audit items:
  - rewrote `examples/38_metadata_polish_capstone` onto the bound-root idiom
    where the compiler truth actually supports it:
    - concrete agents now bind their metadata inputs and outputs through keyed
      `inputs:` / `outputs:` sections
    - manifest-title and rewrite-aware section-summary law now root currentness,
      scope, preservation, comparison support, and carrier paths through those
      bindings
    - the shared base workflow now holds only truly shared metadata law, so the
      specialized workflows no longer mention roots absent from their concrete
      turns
  - updated `examples/38_metadata_polish_capstone/cases.toml` and checked-in
    refs to the new rendered contract shape
  - tightened `docs/REVIEW_SPEC.md` so the live shipped review reference now
    describes portable currentness as
    `current artifact ... via output_root.field`, where `output_root` may be a
    declared emitted output or a bound concrete-turn output root
  - archived the long-form proposal as
    `docs/archive/PRO_PROPOSAL_2026-04-10.md` and replaced
    `docs/PRO_PROPOSAL.md` with a short historical pointer so live docs stop
    reading like an active unshipped proposal
  - rewrote `docs/archive/LESSONS_METADATA_PORT_BLOCKER_NOTE_2026-04-10.md` as
    resolved historical context now that Doctrine ships concrete-turn bound
    roots
  - finished VS Code parity:
    - `editors/vscode/resolver.js` now resolves lower-case bound workflow/review
      roots through concrete agent bindings, including descendant path clicks to
      the underlying typed declaration fields
    - `editors/vscode/syntaxes/doctrine.tmLanguage.json` now colors lower-case
      bound currentness and carrier refs with the same reference-family scopes
    - `editors/vscode/tests/unit/*.prompt`,
      `editors/vscode/tests/integration/suite/index.js`, and
      `editors/vscode/README.md` now cover the bound-root ladder through
      examples `50`, `51`, and `53`
- One important shipped boundary stayed explicit:
  - output guard conditions still read declared inputs directly
  - bound roots are now shipped in workflow/review law and editor navigation,
    but they are not yet valid inside output guard expressions, so the metadata
    capstone trust-surface guards intentionally stayed on `CurrentHandoff.*`
- Verification completed for this pass:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/38_metadata_polish_capstone/cases.toml`
  - `make verify-examples`
  - `cd editors/vscode && make`
