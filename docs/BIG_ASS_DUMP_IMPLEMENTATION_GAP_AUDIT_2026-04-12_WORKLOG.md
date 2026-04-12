# Worklog

Plan doc: docs/BIG_ASS_DUMP_IMPLEMENTATION_GAP_AUDIT_2026-04-12.md

## Initial entry
- Run started.
- Current phase: Phase 1 - Freeze the last architecture verdicts and explicit scope matrix.
- Initial implementation ledger:
  - `decision` / candidate-pool surface | grammar/parser/model/compiler/agent field/examples/docs/editor | still todo
  - preservation bundle verdict | plan/workflow-law/examples/docs reconciliation | still todo
  - final shipped-family reconciliation | examples/docs/editor parity | still todo

## 2026-04-12 - Decision surface shipped and verification closed
- Architecture verdicts closed:
  - `decision` / candidate-pool remains a genuine missing core surface and now
    ships as a top-level `decision` declaration plus concrete-agent
    `decision:` attachment.
  - reusable preservation bundles are explicitly rejected as a new declaration
    family; preservation reuse stays inside named workflow-law subsections plus
    inheritance and patching.
- Implementation owners changed:
  - `doctrine/grammars/doctrine.lark`
  - `doctrine/parser.py`
  - `doctrine/model.py`
  - `doctrine/compiler.py`
  - `examples/74_decision_attachment/`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/WORKFLOW_LAW.md`
  - `examples/README.md`
  - `editors/vscode/resolver.js`
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json`
  - `editors/vscode/README.md`
  - `editors/vscode/tests/unit/declarations.test.prompt`
  - `editors/vscode/tests/unit/controls-and-fields.test.prompt`
  - `editors/vscode/tests/snap/examples/58_readable_document_blocks/prompts/AGENTS.prompt.snap`
  - `editors/vscode/tests/snap/examples/59_document_inheritance_and_descendants/prompts/AGENTS.prompt.snap`
- Implementation notes:
  - `decision` declarations lower through the readable compiler path and render
    natural sentences for candidate minimums, ranking/reject requirements,
    candidate-pool evidence requirements, winner selection, and `rank_by`
    dimensions.
  - `DecisionDecl` titles are addressable, so refs such as
    `{{PlayableStrategyChoice:title}}` render correctly.
  - VS Code parity required two follow-up fixes during verification:
    snapshot reconciliation for widened `required` tokenization and adding the
    shipped Lark keyword `one` to the TextMate keyword coverage.
- Commands run:
  - `uv sync`
  - `npm ci`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/37_law_reuse_and_patching/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/54_analysis_attachment/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/74_decision_attachment/cases.toml`
  - `cd editors/vscode && make`
  - `make verify-examples`
- Command results:
  - all three targeted manifest runs passed
  - `cd editors/vscode && make` passed after snapshot updates and tmLanguage
    keyword alignment for `one`
  - `make verify-examples` passed across the full shipped corpus through
    `examples/74_decision_attachment`
- Checks not run:
  - `make verify-diagnostics` was not run because no diagnostics files or
    catalog docs changed in this wave
- Current phase outcome:
  - Phase 1 verdicts: complete
  - Phase 2 decision implementation: complete
  - Phase 3 preservation verdict: complete
  - Phase 4 proof/docs/editor reconciliation: complete pending fresh audit

## 2026-04-12 - Live docs index reconciled to the shipped decision wave
- Fresh audit reopened Phase 4 because `docs/README.md` still described the
  live corpus as ending at `examples/73_flow_visualizer_showcase` and still
  framed the 01-04 phase docs as the live second-wave completion story.
- Fixes applied:
  - updated `docs/README.md` to point the live corpus at
    `examples/74_decision_attachment`
  - reclassified the 01-04 phase-doc section as historical implementation
    notes instead of the current live completeness path
  - pointed readers back to `docs/LANGUAGE_REFERENCE.md`,
    `docs/WORKFLOW_LAW.md`, and `examples/README.md` for the current shipped
    surface
- Proof for this slice:
  - narrow cold read of `docs/README.md`
  - targeted `rg` checks confirming the live index now names
    `examples/74_decision_attachment` and the phase-doc section is marked
    historical
- Checks not rerun:
  - `make verify-examples` and `cd editors/vscode && make` were not rerun for
    this slice because the audit had just rerun them green and this follow-up
    changed only live docs wording
