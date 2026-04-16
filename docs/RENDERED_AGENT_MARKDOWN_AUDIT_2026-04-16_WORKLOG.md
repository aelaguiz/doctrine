# Worklog

Plan doc: docs/RENDERED_AGENT_MARKDOWN_AUDIT_2026-04-16.md

## Initial entry

- Run started with `$miniarch-step auto-implement`.
- Current phase: Phase 1 - Remove split review and final-output restatement.

## Phase 1 (Remove split review and final-output restatement) Progress Update

- Work completed:
  - Removed the dedicated `Review Response Semantics` section from split review
    final outputs.
  - Added a short inline note that tells the reader when the final response is
    separate from the review carrier and whether they should read the carrier
    for the full outcome.
  - Updated split prose and split schema proof surfaces.
- Tests run + results:
  - `uv run --locked python -m unittest tests.test_final_output tests.test_emit_docs tests.test_review_imported_outputs` - PASS.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/84_review_split_final_output_prose/cases.toml --manifest examples/85_review_split_final_output_output_schema/cases.toml --manifest examples/90_split_handoff_and_final_output_shared_route_semantics/cases.toml --manifest examples/105_review_split_final_output_output_schema_control_ready/cases.toml --manifest examples/106_review_split_final_output_output_schema_partial/cases.toml` - PASS.
- Issues / deviations:
  - None.
- Next steps:
  - Compact simple ordinary-output contracts and scalar support items.

## Phase 2 (Compact ordinary comment contracts and tiny scalar outputs) Progress Update

- Work completed:
  - Added bullet-first compaction for eligible simple `TurnResponse`
    contracts.
  - Flattened simple scalar and simple guarded support items into one bullet
    line.
  - Preserved tables for file outputs, delivery-skill rows, target-config
    rows, schema-bearing outputs, and richer support sections.
- Tests run + results:
  - `uv run --locked python -m unittest tests.test_output_rendering tests.test_output_target_delivery_skill tests.test_emit_docs` - PASS.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/38_metadata_polish_capstone/cases.toml --manifest examples/56_document_structure_attachments/cases.toml --manifest examples/84_review_split_final_output_prose/cases.toml --manifest examples/85_review_split_final_output_output_schema/cases.toml --manifest examples/90_split_handoff_and_final_output_shared_route_semantics/cases.toml --manifest examples/105_review_split_final_output_output_schema_control_ready/cases.toml --manifest examples/106_review_split_final_output_output_schema_partial/cases.toml --manifest examples/117_io_omitted_wrapper_titles/cases.toml --manifest examples/119_route_only_final_output_contract/cases.toml` - PASS.
- Issues / deviations:
  - The initial focused proof understated the blast radius. The same ordinary
    output path also drives inherited outputs, route-law outputs, review
    carriers, and several route-only examples.
- Next steps:
  - Flatten redundant compiler-owned binding shells on the shared resolved IO
    path.

## Phase 3 (Flatten compiler-generated binding shells) Progress Update

- Work completed:
  - Lowered redundant compiler-owned `* Binding` wrappers in
    `doctrine/_compiler/resolve/outputs.py` instead of flattening them late in
    markdown compile.
  - Preserved explicit wrapper titles and omitted-title fail-loud behavior.
  - Refreshed the adjacent IO, currentness, and review examples that share the
    lowering path.
- Tests run + results:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/38_metadata_polish_capstone/cases.toml --manifest examples/51_inherited_bound_io_roots/cases.toml --manifest examples/117_io_omitted_wrapper_titles/cases.toml` - PASS.
- Issues / deviations:
  - The owner path moved from the initial phase sketch. The resolved IO layer
    was the real canonical boundary.
- Next steps:
  - Compact simple structure attachments while preserving richer structure
    blocks.

## Phase 4 (Compact simple artifact structure) Progress Update

- Work completed:
  - Added the compact `Required Structure:` render for summary-only structure
    attachments.
  - Kept the full `Artifact Structure` section for richer shapes with
    preamble or detail blocks.
  - Updated the lesson-plan structure proof and output inheritance
    expectations.
- Tests run + results:
  - `uv run --locked python -m unittest tests.test_output_rendering tests.test_output_inheritance` - PASS.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/56_document_structure_attachments/cases.toml` - PASS.
- Issues / deviations:
  - None.
- Next steps:
  - Humanize the shared workflow-law wording surfaces and rerun diagnostics.

## Phase 5 (Humanize workflow-law wording) Progress Update

- Work completed:
  - Reworded pass gates, mode lines, currentness lines, route-selection lines,
    stop lines, and preservation lines in compiler-owned workflow-law output.
  - Fixed condition rendering so enum-backed refs stayed readable after the
    wording cleanup.
  - Refreshed the route-heavy and review-heavy example families that share the
    same wording helpers.
- Tests run + results:
  - `uv run --locked python -m unittest tests.test_compile_diagnostics tests.test_final_output` - PASS.
  - `make verify-diagnostics` - PASS.
- Issues / deviations:
  - The first full corpus run failed on a much wider set of render contracts
    than the focused pass covered. The failures were expected snapshot drift,
    not semantic regressions.
- Next steps:
  - Refresh the widened proof surface, align public docs, and rerun the full
    corpus.

## Phase 6 (Corpus sweep, docs alignment, and final proof) Progress Update

- Work completed:
  - Updated `examples/README.md`, `docs/EMIT_GUIDE.md`,
    `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
    `docs/VERSIONING.md`, and `CHANGELOG.md`.
  - Refreshed all touched manifest-backed `expected_lines`, `ref/`, and
    `build_ref/` artifacts across the widened blast radius.
  - Manually re-read representative outputs for examples `09`, `38`, `51`,
    `56`, `64`, `67`, `83`, `84`, `85`, `90`, `104`, `105`, `106`, `117`,
    and `119`.
- Tests run + results:
  - `uv sync` - PASS.
  - `npm ci` - PASS.
  - `make verify-examples` - PASS.
  - `make verify-diagnostics` - PASS.
- Issues / deviations:
  - The first batch refresh wrote trailing newlines into several `approx_ref`
    files. A second normalization pass removed that drift, and the final full
    corpus run reported `Checked ref diffs: None`.
- Next steps:
  - Await the fresh hook-backed implementation audit.
