# Worklog

Plan doc: docs/ORDINARY_OUTPUT_CONTRACT_RENDERING_REFRESH_2026-04-15.md

## Initial entry
- Run started.
- Current phase: Phase 1 - Owner split and single-artifact contract-table foundation.

## Completion entry
- Completed Phases 1 through 6.
- Shipped the grouped ordinary-output renderer in `doctrine/_compiler/compile/outputs.py`.
- Added focused proof in `tests/test_output_rendering.py` and updated inherited-output expectations in `tests/test_output_inheritance.py`.
- Refreshed the affected manifest-backed corpus cases plus checked-in `ref/` and `build_ref/` proof under `examples/`.
- Updated `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/EMIT_GUIDE.md`, `docs/LANGUAGE_REFERENCE.md`, `examples/README.md`, `docs/VERSIONING.md`, and `CHANGELOG.md`.
- Verification passed:
  - `make verify-examples`
  - `make verify-diagnostics`
  - `uv run --locked python -m unittest tests.test_output_rendering`

## Reopened phase follow-up
- Fresh audit reopened Phase 2 because `doctrine/_compiler/compile/outputs.py` still kept the stale `_compile_output_files(...)` bullet renderer beside the grouped multi-file path.
- Replaced the duplicate path by making `_compile_output_files(...)` own the grouped `Artifacts` table directly and deleting the superseded `_compile_ordinary_output_files_table(...)` helper.
- Re-ran the required proof for the reopened work:
  - `uv run --locked python -m unittest tests.test_output_rendering tests.test_emit_docs`
  - `uv run --locked python -m unittest tests.test_output_rendering tests.test_output_inheritance tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_final_output tests.test_emit_docs`
  - `make verify-diagnostics`
  - `make verify-examples`
- All rerun proof passed.
