# Changelog

All notable Doctrine release changes live here.
This file is the portable release history. `docs/VERSIONING.md` is the
evergreen policy guide.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

Use this section for work that is not public yet.

When you cut a public release:

1. Copy the release entry template below.
2. Replace the placeholders.
3. Move the real change notes into the new release section.
4. Leave `## Unreleased` at the top for the next cycle.

Public release entries must replace every placeholder before `make release-tag`
or `make release-draft` runs. The helper rejects placeholder compatibility
payload text and breaking releases with no real upgrade steps.

### Added
- Added directory-backed runtime package imports that resolve
  `<module>/AGENTS.prompt` and let thin `AGENTS.prompt` build handles emit
  real runtime package trees.
- Added runtime-package emit support for package-root `AGENTS.md`, optional
  same-name sibling `SOUL.md`, and bundled peer files.
- Added direct `output[...]` declaration inheritance with explicit top-level
  `inherit` and `override` patching, plus fail-loud errors for missing,
  wrong-kind, cyclic, and parentless output patches.
- Added shipped corpus coverage for inherited outputs on ordinary output
  contracts, imported handoff reuse, `final_output:`, shared `route.*`
  semantics, and fail-loud output-inheritance cases.
- Added optional titles for `sequence`, `bullets`, and `checklist` readable
  blocks while keeping the authored key required for inheritance and refs.
- Added a shipped corpus example for titled and titleless ordered and
  unordered readable lists.
- Added workflow-root readable blocks so workflows may own non-section
  readable blocks directly instead of wrapping them in a local section first.
- Added `115_runtime_agent_packages` as the generic checked-in runtime-package
  proof example.

### Changed
- Changed `emit_docs`, `emit_flow`, corpus build-contract proof, and
  diagnostic smoke checks to share one runtime frontier instead of assuming
  root-only runtime emit.
- Clarified the release policy to prefer the next patch version for routine
  public work and keep minor bumps for real backward-compatible public
  additions or soft deprecations.
- Changed structured `JsonObject` final outputs to keep their example object
  inside `output schema`, validate that example against the lowered
  OpenAI-compatible schema, and stop reading checked-in `.example.json`
  support files.
- Changed `emit_docs` to write `AGENTS.md` plus the real lowered
  `schemas/<output-slug>.schema.json` artifact for structured final outputs,
  plus `final_output.contract.json` for final-output and review-control
  metadata. Doctrine no longer emits `AGENTS.contract.json`.
- Renamed the shipped structured final-output examples from `_json_schema` to
  `_output_schema` so the public corpus matches the approved feature story.
- Added `python -m doctrine.validate_output_schema --schema ...` as the
  built-in file validator for emitted structured-output schema files.
- Changed emitted ordinary `## Outputs` Markdown to one grouped contract block
  per output. Single artifacts now start with a `Contract | Value` table,
  `files:` outputs add an `Artifacts` table, and `structure:` now renders as
  one `Artifact Structure` section. Downstream emitted-Markdown snapshots or
  parsers will need to update.
- Changed detailed readable list rendering to drop helper kind lines such as
  `_ordered list_` and `_unordered list_`. Titled lists keep their heading,
  and titleless lists render directly in the parent section.
- Moved the public release record fully onto `CHANGELOG.md`, signed tags, and
  matching GitHub releases. `docs/VERSIONING.md` now stays policy-only.
- Centralized package release metadata and package smoke proof so release
  prep, CI, and publish flows use the same repo-owned path.
- Moved source-checkout setup docs onto `make setup` and package smoke docs
  onto `make verify-package` to reduce repeated shell instructions.
- Made the package publish path require explicit `[tool.doctrine.package]`
  fields instead of falling back to code defaults.
- Added `tests.test_package_release` to the release worksheet proof path and
  added `make verify-package` to the PR checklist for package and publish
  work.
- Tightened the README, docs index, and contributing guide so they point back
  to `docs/VERSIONING.md` and `CHANGELOG.md` instead of becoming second
  release-policy owners.

### Fixed
- Fixed custom authored workflow slots such as `read_first` so workflows with
  root readable blocks no longer fail with `E901` during emit.

### Release Entry Template

```md
## vX.Y.Z - YYYY-MM-DD

Release kind: Non-breaking
Release channel: stable
Release version: vX.Y.Z
Language version: unchanged (still 1.0)
Affected surfaces: ...
Who must act: ...
Who does not need to act: ...
Upgrade steps: ...
Verification: ...
Support-surface version changes: none

### Added
- Describe backward-compatible user-facing additions.

### Changed
- Describe user-visible behavior or workflow changes.

### Deprecated
- Describe soft-deprecated public surfaces and early move guidance.

### Removed
- Describe removed public surfaces.

### Fixed
- Describe important fixes that matter to users or maintainers.

### YANKED
- Use this only when a bad public release was superseded later.
```

## v1.0.2 - 2026-04-14

Release kind: Non-breaking
Release channel: stable
Release version: v1.0.2
Language version: unchanged (still 1.0)
Affected surfaces: package-index installs, GitHub Trusted Publishing, and the public install docs.
Who must act: users installing Doctrine from PyPI or TestPyPI and maintainers publishing Doctrine to package indexes.
Who does not need to act: users running Doctrine from a source checkout and users of the `doctrine` Python module path or `[tool.doctrine.emit]` config surface.
Upgrade steps: Install `doctrine-agents==1.0.2` from the package index you use. Keep using `python -m doctrine.emit_docs` and the `doctrine` module path exactly as before.
Verification: Install `doctrine-agents==1.0.2` in a fresh venv and run `python -m doctrine.emit_docs --pyproject ... --target ...` from a temp project outside this repo.
Support-surface version changes: package metadata 1.0.1 -> 1.0.2; distribution name doctrine -> doctrine-agents

### Added
- Added the first public package-index rollout for Doctrine under the `doctrine-agents` distribution name.
- Added GitHub Trusted Publishing wiring for `testpypi` and `pypi`, including repo environments and gated publish workflow paths.

### Changed
- Kept the Python import path as `doctrine` while making the package-index install name explicit in the docs and README.
- Added a package-index smoke path that builds the wheel, installs it in a fresh environment, and compiles a temp project outside the repo root.

## v1.0.1 - 2026-04-14

Release kind: Non-breaking
Release channel: stable
Release version: v1.0.1
Language version: unchanged (still 1.0)
Affected surfaces: Python package metadata, the public release flow, and external package install compatibility.
Who must act: maintainers cutting Doctrine releases and users installing Doctrine through package resolvers that require `doctrine>=1.0.0,<2`.
Who does not need to act: users pinned to repo commits and users who are not consuming Doctrine as a Python package.
Upgrade steps: Install Doctrine v1.0.1. If you added a local `0.0.0` workaround, remove it and resolve against the released package again.
Verification: uv run --locked python -m unittest tests.test_release_flow && make verify-diagnostics
Support-surface version changes: package metadata 0.0.0 -> 1.0.1

### Changed
- Made the published package metadata line up with the released Doctrine 1.0 patch line.
- Taught the release flow to check `pyproject.toml` package metadata before tagging or drafting a public release.

### Fixed
- Restored clean downstream installs for dependents that correctly require `doctrine>=1.0.0,<2`.

## v1.0.0 - 2026-04-14

Release kind: Non-breaking
Release channel: stable
Release version: v1.0.0
Language version: unchanged (still 1.0)
Affected surfaces: Doctrine 1.0 language docs, manifest-backed corpus guidance, and the public release flow.
Who must act: maintainers cutting public releases and users adopting Doctrine from tagged releases.
Who does not need to act: users staying on unreleased commits and maintainers not cutting a release today.
Upgrade steps: No upgrade from an earlier public release is required. New users can start from README.md, docs/LANGUAGE_REFERENCE.md, and examples/01_hello_world.
Verification: uv sync && npm ci && uv run --locked python -m unittest tests.test_release_flow && make verify-examples
Support-surface version changes: none

### Added
- Shipped the first public Doctrine 1.0 release with the live language docs, compiler-backed AGENTS.md output flow, and the full manifest-backed example corpus.
- Added a repo-owned public release flow with `make release-prepare`, `make release-tag`, `make release-draft`, and `make release-publish`.

### Changed
- Moved versioning, release, and compatibility guidance into the canonical `docs/VERSIONING.md` and `CHANGELOG.md` pair.
- Clarified the public docs links for release history, support, security, and collaboration rules.

### Fixed
- Corrected the skill-package example range in `examples/README.md` to `95` through `103`.

### YANKED
- Superseded by v1.0.1 because `pyproject.toml` still advertised `0.0.0`, which broke package resolvers that correctly required the Doctrine 1.x line.
