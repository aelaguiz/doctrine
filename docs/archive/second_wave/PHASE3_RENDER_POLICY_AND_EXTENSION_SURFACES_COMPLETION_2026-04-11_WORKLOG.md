# Worklog

Plan doc: docs/archive/second_wave/PHASE3_RENDER_POLICY_AND_EXTENSION_SURFACES_COMPLETION_2026-04-11.md

## Initial entry
- Run started.
- Current phase: Phase 1 — finish the remaining Phase 3 render-policy and late
  extension surfaces through the shipped owner path.
- Loop state armed for `implement-loop` / `auto-implement`.

## Final implementation update
- Work completed:
  - Finished the remaining Phase 3 grammar/model/parser/compiler/renderer
    surface for authored `render_profile`, compact `properties`, explicit
    readable `guard` shells, typed `item_schema:` / `row_schema:`, raw
    `markdown`, raw `html`, `footnotes`, `image`, and structured nested table
    cells.
  - Preserved the existing typed-markdown and identity ladder while extending
    addressability so Phase 3 descendants resolve through `properties`,
    footnotes, and inline row/item schema keys.
  - Added the manifest-backed Phase 3 proof ladder in
    `examples/64_render_profiles_and_properties`,
    `examples/65_row_and_item_schemas`, and
    `examples/66_late_extension_blocks`, while keeping the preexisting
    preservation signals for `examples/58_*` through `examples/63_*` green.
  - Aligned the evergreen docs, example index, VS Code resolver, tmLanguage
    keyword coverage, integration tests, and extension README so the shipped
    compiler, docs, and editor package all describe the same Phase 3 boundary.
- Tests run + results:
  - `uv sync` — passed.
  - `npm ci` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/58_readable_document_blocks/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/59_document_inheritance_and_descendants/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/60_shared_readable_bodies/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/61_multiline_code_and_readable_failures/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/62_identity_titles_keys_and_wire/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/63_schema_artifacts_and_groups/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/64_render_profiles_and_properties/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/65_row_and_item_schemas/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/66_late_extension_blocks/cases.toml` — passed.
  - `make verify-examples` — passed.
  - `cd editors/vscode && make` — passed.
- Issues / deviations:
  - `cd editors/vscode && make` surfaced two real editor-parity drifts during
    the first pass: the widened readable-header tmLanguage rule changed shipped
    snapshot coverage, and the footnotes resolver used a key-only regex that
    broke descendant clicks. Both were fixed before the final package/test run.
  - `make verify-diagnostics` was not run because this pass did not change
    diagnostics code or the diagnostics smoke surface.
- Next steps:
  - Leave `.codex/implement-loop-state.019d7eaf-b944-7103-a0ff-c7cb811a8c85.json`
    armed for the fresh `audit-implementation` step that owns the
    authoritative completion verdict and the `Use $arch-docs` handoff.

## Audit follow-up implementation update
- Work completed:
  - Preserved `document render_profile:` through the markdown-bearing
    `output structure:` lowering path unless the output attaches its own
    `render_profile:`.
  - Made the shipped semantic render-profile targets observable in the shared
    renderer path:
    `analysis.stages`, `review.contract_checks`, and
    `control.invalidations`.
  - Made output/readable interpolation honor profile-sensitive identity
    display on the active compile path so authored owner and enum-wire policy
    changes now surface in rendered output.
  - Closed the parser hole where repeated `item_schema:` or `row_schema:`
    blocks silently overwrote the earlier schema instead of failing loud.
  - Extended the proof ladder with:
    `examples/64_render_profiles_and_properties` for identity-profile behavior
    and explicit guard-shell negatives,
    `examples/65_row_and_item_schemas` for repeated schema-block negatives, and
    `examples/67_semantic_profile_lowering` for semantic lowering and
    document-profile structure lowering.
- Tests run + results:
  - `python -m py_compile doctrine/compiler.py doctrine/parser.py doctrine/renderer.py` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/61_multiline_code_and_readable_failures/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/64_render_profiles_and_properties/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/65_row_and_item_schemas/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/67_semantic_profile_lowering/cases.toml` — passed.
- Issues / deviations:
  - This follow-up pass did not rerun `make verify-examples`,
    `make verify-diagnostics`, or `cd editors/vscode && make`; the hook asked
    for the smallest credible proof checks for the reopened fixes, and the new
    targeted manifests directly cover those changes.
- Next steps:
  - Keep `.codex/implement-loop-state.019d7eaf-b944-7103-a0ff-c7cb811a8c85.json`
    armed for the next fresh `audit-implementation` pass.
