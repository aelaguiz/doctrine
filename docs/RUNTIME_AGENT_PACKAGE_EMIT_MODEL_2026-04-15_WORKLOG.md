# Worklog

Plan doc: docs/RUNTIME_AGENT_PACKAGE_EMIT_MODEL_2026-04-15.md

## Initial entry
- Run started.
- Current phase: Phase 1 - Import loading learns directory-backed runtime packages

## Phase 1-4 Progress Update
- Work completed:
  - Landed directory-backed runtime package imports with explicit module
    metadata and fail-loud file-versus-directory collisions.
  - Extracted a shared package-layout helper and moved skill-package ordinary
    file bundling onto it.
  - Added the shared runtime frontier plus unit-aware compile and flow-root
    helpers.
  - Moved `emit_docs` and `emit_flow` onto package-aware runtime roots with
    peer-file bundling and sibling `SOUL.prompt` validation.
- Tests run + results:
  - `uv run --locked python -m unittest tests.test_import_loading` — passed
  - `uv run --locked python -m unittest tests.test_emit_skill` — passed
  - `uv run --locked python -m unittest tests.test_compiler_boundary tests.test_emit_docs tests.test_emit_flow` — passed
- Issues / deviations:
  - Phase 5 and later proof, example, and docs work have not started yet.
- Next steps:
  - Move corpus proof, smoke proof, and one generic example onto the new
    runtime package path.

## Phase 5 Progress Update
- Work completed:
  - Updated the canonical corpus and smoke proof helpers to check
    package-backed runtime output trees and flow roots.
  - Added the generic `115_runtime_agent_packages` example plus checked-in
    `build_ref/` truth for the new runtime-package story.
  - Added corpus coverage for the new build-contract target and restored the
    shipped skill-package collision wording after the shared package-layout
    helper briefly widened it.
- Tests run + results:
  - `uv run --locked python -m unittest tests.test_verify_corpus` — passed
  - `make verify-diagnostics` — passed
  - `make verify-examples` — passed
- Issues / deviations:
  - The first `make verify-examples` pass exposed one wording regression in
    the existing skill-package collision error. I fixed the shared helper to
    keep the old skill-specific message before rerunning the proof.
- Next steps:
  - Rewrite the live runtime-package docs and release truth, then run
    `make verify-package`.

## Phase 6-7 Progress Update
- Work completed:
  - Rewrote the live emit, language, skill-package, and example docs so they
    teach one package-backed runtime story and the thin build-handle pattern.
  - Updated versioning and changelog truth to classify the runtime-package
    surface as an additive public change.
  - Ran the full required repo sweep after the docs landed and confirmed the
    final runtime-package story stays aligned across code, examples,
    diagnostics, docs, and package smoke proof.
- Tests run + results:
  - `make verify-package` — passed
  - `uv sync` — passed
  - `npm ci` — passed
  - `make verify-examples` — passed
  - `make verify-diagnostics` — passed
  - `make verify-package` — passed
- Issues / deviations:
  - None.
- Next steps:
  - Wait for the fresh implementation audit pass.

## Phase 4 Reopen Fix
- Work completed:
  - Retired `root_concrete_agents()` from `doctrine/emit_common.py`.
  - Moved the last direct `SOUL.prompt` runtime-root selection in
    `emit_docs` and `emit_flow` onto root-unit concrete agent selection.
  - Moved the remaining flow tests onto the shared runtime-root object path.
- Tests run + results:
  - `uv run --locked python -m unittest tests.test_emit_docs tests.test_emit_flow` — passed
- Issues / deviations:
  - None.
- Next steps:
  - Rerun the full Phase 7 repo proof sweep after the cleanup.

## Phase 7 Reopen Fix
- Work completed:
  - Reran the full required repo sweep after the Phase 4 cleanup.
- Tests run + results:
  - `uv sync` — passed
  - `npm ci` — passed
  - `make verify-examples` — passed
  - `make verify-diagnostics` — passed
  - `make verify-package` — passed
- Issues / deviations:
  - None.
- Next steps:
  - Wait for the fresh implementation audit pass.

## Phase 4 Collision Reopen Fix
- Work completed:
  - Reserved `SOUL.md` unconditionally for runtime-package emit planning so a
    peer file cannot emit or case-collide with that compiler-owned output.
  - Added focused emit proof that package peer `SOUL.md` and `soul.md` fail
    loud without a sibling `SOUL.prompt`.
- Tests run + results:
  - `uv run --locked python -m unittest tests.test_emit_docs tests.test_emit_flow` — passed
- Issues / deviations:
  - None.
- Next steps:
  - Rerun the full Phase 7 repo proof sweep after the collision fix.

## Phase 7 Collision Reopen Fix
- Work completed:
  - Reran the full required repo sweep after the Phase 4 `SOUL.md` collision
    fix.
- Tests run + results:
  - `uv sync` — passed
  - `npm ci` — passed
  - `make verify-examples` — passed
  - `make verify-diagnostics` — passed
  - `make verify-package` — passed
- Issues / deviations:
  - None.
- Next steps:
  - Wait for the fresh implementation audit pass.
