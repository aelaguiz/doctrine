# Changelog

All notable Doctrine release changes live here.
This file is the portable release history. `docs/VERSIONING.md` is the
evergreen policy guide.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

Use this section for work that is not public yet.

### Added
- Added split GitHub Actions workflows for PR checks, main-branch CI, dependency review, scorecards, and release packaging.
- Added repo-owned GitHub surfaces for `CODEOWNERS`, Dependabot, richer release-note labels, and stronger issue and PR templates.
- Prepared the first package-index rollout under the `doctrine-agents`
  distribution name while keeping the Python import path as `doctrine`.

### Changed
- Updated public support and security docs for the 1.x line and GitHub private vulnerability reporting.
- Added package metadata links for changelog, discussions, and security policy so future package pages point to live repo surfaces.
- Documented the GitHub release publish path that builds dist artifacts, smoke tests an external install, uploads release assets, and can publish to package indexes through Trusted Publishing.
- Wired the publish workflow for `testpypi` and `pypi` environments and staged
  the rollout behind GitHub repo variables.

When you cut a public release:

1. Copy the release entry template below.
2. Replace the placeholders.
3. Move the real change notes into the new release section.
4. Leave `## Unreleased` at the top for the next cycle.

Public release entries must replace every placeholder before `make release-tag`
or `make release-draft` runs. The helper rejects placeholder compatibility
payload text and breaking releases with no real upgrade steps.

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
