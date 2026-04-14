# Worklog

Plan doc: docs/LANGUAGE_VERSIONING_AND_BREAKING_CHANGE_POLICY_2026-04-13.md

## Initial entry
- Run started.
- Current phase: Phase 1 — Full policy and changelog model in live docs

## Phase 1 (Full policy and changelog model in live docs) Progress Update
- Work completed:
  - Expanded `docs/VERSIONING.md` into the live release-policy owner.
  - Added `CHANGELOG.md` with one `Unreleased` section and a fixed release-entry template.
  - Updated `AGENTS.md` release-flow duties and the targeted release-helper test command.
- Tests run + results:
  - No repo verify command. Docs-only phase.
- Issues / deviations:
  - The plan did not pin the first public language-version value. I checked git history and found no prior recorded value.
- Next steps:
  - Implement the release helper and repo task surface.

## Phase 2 (Release helper core and signed tag flow) Progress Update
- Work completed:
  - Added `doctrine/release_flow.py` as the public helper boundary and split the internal logic into `doctrine/_release_flow/`.
  - Added `make release-prepare` and `make release-tag`.
  - Added release-helper tests for version moves and tag preflight.
- Tests run + results:
  - `python -m py_compile doctrine/release_flow.py doctrine/_release_flow/models.py doctrine/_release_flow/parsing.py doctrine/_release_flow/ops.py` — passed.
- Issues / deviations:
  - Tag preflight now checks signing-key presence before git tag creation.
- Next steps:
  - Add GitHub draft and publish flow on the same helper path.

## Phase 3 (GitHub draft and publish flow) Progress Update
- Work completed:
  - Added `draft` and `publish` to the same public release-helper boundary and its internal `_release_flow` helpers.
  - Added `make release-draft`, `make release-publish`, and `.github/release.yml`.
  - Added tests for prerelease draft command assembly and publish command assembly.
- Tests run + results:
  - Covered later by `uv run --locked python -m unittest tests.test_release_flow`.
- Issues / deviations:
  - The helper uses `CHANGELOG.md` as the curated release-note source and lets GitHub append generated notes.
- Next steps:
  - Align the touched live docs and support-surface guides.

## Phase 4 (Live doc and support-surface convergence) Progress Update
- Work completed:
  - Updated `README.md`, `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, and `docs/LANGUAGE_DESIGN_NOTES.md`.
  - Updated `docs/EMIT_GUIDE.md`, `docs/COMPILER_ERRORS.md`, and `examples/README.md`.
- Tests run + results:
  - No extra repo verify command. This phase only changed live docs.
- Issues / deviations:
  - Fixed one plan contradiction so breaking non-language releases may stay on the stable channel without a fake language-version bump.
- Next steps:
  - Run the targeted proof and finish the release-readiness cleanup.

## Phase 5 (Final proof and release-readiness cleanup) Progress Update
- Work completed:
  - Ran `uv sync` and `npm ci`.
  - Fixed the changelog-language header comparison and then split the release helper into smaller modules without changing the public CLI.
  - Marked all implemented phases complete in the plan doc.
- Tests run + results:
  - `uv run --locked python -m unittest tests.test_release_flow` — passed.
  - `git diff --check` — passed.
- Issues / deviations:
  - Real host-side tag signing and GitHub auth are still non-blocking manual QA until the first public release is cut.
- Next steps:
  - Await the fresh `audit-implementation` pass from the armed loop.

## Reopened phases (audit follow-through) Progress Update
- Work completed:
  - Added one shared release-entry truth validator for prepare-ready status, tag creation, and draft creation.
  - Added fail-loud prior-tag checks for lightweight and unsigned public tags.
  - Updated `docs/VERSIONING.md` and `CHANGELOG.md` so the public release-entry rules now match the stricter helper behavior.
- Tests run + results:
  - `uv run --locked python -m unittest tests.test_release_flow` — passed with 12 tests.
  - `python -m py_compile doctrine/release_flow.py doctrine/_release_flow/models.py doctrine/_release_flow/parsing.py doctrine/_release_flow/ops.py` — passed.
  - `git diff --check` — passed.
- Issues / deviations:
  - The happy-path release tests now patch prior-tag validation because the temp git repos use fake history tags instead of real signed public tags.
- Next steps:
  - Await the next fresh `audit-implementation` pass from the armed loop.

## Reopened phases (current-tag publication boundary) Progress Update
- Work completed:
  - Added current-tag validation before `release-draft` and `release-publish`.
  - Made the GitHub publication paths fail loud when the current release tag is missing, lightweight, or unsigned.
  - Updated `docs/VERSIONING.md` so the live guide now says draft and publish also enforce the signed annotated current-tag rule.
- Tests run + results:
  - `uv run --locked python -m unittest tests.test_release_flow` — passed with 18 tests.
  - `python -m py_compile doctrine/release_flow.py doctrine/_release_flow/models.py doctrine/_release_flow/parsing.py doctrine/_release_flow/ops.py` — passed.
- Issues / deviations:
  - Happy-path GitHub draft and publish tests still patch the current-tag validator because the temp git repos do not carry real signed public tags.
- Next steps:
  - Await the next fresh `audit-implementation` pass from the armed loop.

## Reopened phases (signed pushed tag proof and worksheet completion) Progress Update
- Work completed:
  - Moved shared git error handling into `doctrine/_release_flow/common.py` and split tag parsing and tag proof into `doctrine/_release_flow/tags.py` so the release helper no longer keeps that logic in one oversized parser file.
  - Replaced marker-text tag checks with real `git verify-tag` validation for public release tags.
  - Made `release-draft` and `release-publish` prove that `origin` points at the same verified local signed annotated tag object before GitHub publication.
  - Fixed the breaking non-language release worksheet so it now lists `docs/VERSIONING.md`, affected live docs, contributor instructions, release-note work, and proof duties.
  - Updated `docs/VERSIONING.md` to match the stricter pushed-tag publication rule.
- Tests run + results:
  - `python -m py_compile doctrine/release_flow.py doctrine/_release_flow/common.py doctrine/_release_flow/models.py doctrine/_release_flow/ops.py doctrine/_release_flow/parsing.py doctrine/_release_flow/tags.py tests/test_release_flow.py` — passed.
  - `uv run --locked python -m unittest tests.test_release_flow` — passed with 22 tests.
  - `git diff --check` — passed.
- Issues / deviations:
  - Happy-path GitHub draft and publish tests still patch the pushed-tag validator because the temp git repos do not carry a real signed pushed public tag.
- Next steps:
  - Await the next fresh `audit-implementation` pass from the armed loop.
