# Worklog

Plan doc: docs/OMITTED_SUBITEM_TITLES_LOWER_SINGLE_CHILD_SURFACES_2026-04-15.md

## Initial entry

- Run started with `$miniarch-step auto-implement`.
- Current phase: Phase 1 - Replace title-copy bucket data with flattening data.

## Phase 1 (Replace title-copy bucket data with flattening data) Progress Update

- Work completed:
  - Replaced `ResolvedContractBucket.sole_direct_title` with direct child
    section and body-position data.
  - Updated IO bucket resolution to record direct child sections.
- Tests run + results:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/23_first_class_io_blocks/cases.toml` - PASS.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/27_addressable_record_paths/cases.toml` - PASS.
- Issues / deviations:
  - None.
- Next steps:
  - Implement resolver-owned lowering and update focused proof.

## Phase 2 (Implement IO lowering and focused proof) Progress Update

- Work completed:
  - Flattened one direct child declaration body for omitted base IO wrapper
    titles.
  - Preserved explicit wrapper titles and inherited override titles.
  - Updated fail-loud wording to require one lowerable direct declaration.
  - Rewrote `examples/117_io_omitted_wrapper_titles`.
- Tests run + results:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/117_io_omitted_wrapper_titles/cases.toml` - PASS.
  - `make verify-diagnostics` - PASS.
- Issues / deviations:
  - The first focused manifest run failed only on expected blank lines after
    flattening; the expected lines were updated to match actual renderer
    output, then the manifest passed.
- Next steps:
  - Run adjacent-surface preservation guards.

## Phase 3 (Prove adjacent surfaces stayed stable) Progress Update

- Work completed:
  - Verified explicit IO, inherited IO, addressable record paths, and
    titleless readable lists.
- Tests run + results:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/23_first_class_io_blocks/cases.toml` - PASS.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/24_io_block_inheritance/cases.toml` - PASS.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/27_addressable_record_paths/cases.toml` - PASS.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/113_titleless_readable_lists/cases.toml` - PASS.
- Issues / deviations:
  - None.
- Next steps:
  - Update public docs and run full verification.

## Phase 4 (Update public docs, release notes, and full verification) Progress Update

- Work completed:
  - Updated `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`,
    `examples/README.md`, `docs/VERSIONING.md`, and `CHANGELOG.md`.
  - Removed scoped wording that said omitted IO wrapper titles reuse a direct
    declaration title.
- Tests run + results:
  - `uv sync` - PASS.
  - `npm ci` - PASS.
  - `make verify-examples` - PASS.
  - `make verify-diagnostics` - PASS.
- Issues / deviations:
  - `make verify-package` was not run because this pass did not change package
    metadata or release helper output.
- Next steps:
  - Await fresh implementation audit from the hook-backed implement loop.
