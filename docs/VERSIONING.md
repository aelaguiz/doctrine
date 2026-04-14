# Versioning

This file is the canonical home for Doctrine versioning, release rules, and
breaking-change guidance.

Current Doctrine language version: 1.0
Current public Doctrine release version: v1.0.2. Use the latest signed
annotated tag and matching GitHub release as the public release record.

## The Version Lines

### Doctrine Language Version

The Doctrine language version tracks grammar, semantics, and authored language
behavior.

- Use `major.minor`.
- Bump the major version when the language itself breaks.
- Bump the minor version when the language adds backward-compatible syntax or
  semantics.
- Leave it unchanged when a release does not change the language.

### Doctrine Release Version

The Doctrine release version tracks one public shipped release or prerelease.

- Use signed annotated tags and matching GitHub releases as the public release
  record.
- Stable tags use `vX.Y.Z`.
- Beta tags use `vX.Y.Z-beta.N`.
- RC tags use `vX.Y.Z-rc.N`.
- Release major bumps cover any public surface that now needs user action,
  even when the language version stays the same.
- Release minor bumps cover backward-compatible public additions and soft
  deprecations.
- Release patch bumps cover internal-only or other non-breaking public fixes.

### Narrow Support-Surface Versions

Doctrine also ships narrower version lines.

- `contract_version` in emitted `.contract.json` files only versions that JSON
  contract shape. It is not the Doctrine language version.
- `schema_version` in `cases.toml` only versions the corpus-manifest format.
  It is not the Doctrine language version.
- The package metadata version in `pyproject.toml` versions the published
  Python package. It is not the Doctrine language version.
- The published distribution name may differ from the Python import package
  name. Package-index installs use the published distribution name, while the
  module path stays `doctrine`.
- For public stable releases, `vX.Y.Z` maps to package version `X.Y.Z`.
- For public beta releases, `vX.Y.Z-beta.N` maps to package version `X.Y.ZbN`.
- For public rc releases, `vX.Y.Z-rc.N` maps to package version `X.Y.ZrcN`.
- `make release-tag` and `make release-draft` must fail if `[project].version`
  does not match that release-package version.

For the emitted contract surface, use [EMIT_GUIDE.md](EMIT_GUIDE.md).
For the corpus manifest surface, use [../examples/README.md](../examples/README.md).

## Release Classes

Every public release uses one release class.

- `internal`: docs-only, tooling-only, diagnostics-only, refactor, or cleanup
  work that does not change a shipped public surface. Release kind:
  `Non-breaking`.
- `additive`: backward-compatible public additions. Release kind:
  `Non-breaking`.
- `soft-deprecated`: behavior still works, but Doctrine now tells users what
  to move away from and how to move early. Release kind: `Non-breaking`.
- `breaking`: any shipped public surface now needs user action. This includes
  language breaks, emitted contract breaks, manifest-schema breaks, and other
  stable public surface breaks. Release kind: `Breaking`.

Breaking releases outside the language surface may keep the Doctrine language
version unchanged. Breaking language releases must bump the Doctrine language
version major.

## Required Breaking-Change Payload

Every breaking change must say:

- affected surface
- old behavior
- new behavior
- first affected version
- who must act
- who does not need to act
- exact upgrade steps
- before and after example when that helps
- verification step

Do not ship vague "this might break you" wording.

## Changelog Entry Shape

Before `make release-tag` or `make release-draft`, `CHANGELOG.md` must contain
one matching release section:

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
```

Beta and RC releases use the same shape, but `Release channel:` becomes
`beta.N` or `rc.N`, and `Release version:` uses the prerelease tag.

The helper reads that header back out of `CHANGELOG.md` for tag messages and
GitHub draft notes. Keep it exact.
Replace every placeholder before you tag or draft a public release. The helper
rejects `fill this in`, `update for this release`, `...`, and similar
placeholder text in public release entries. Breaking releases must carry real
upgrade steps.

## Release Process

1. Update `docs/VERSIONING.md` when the language version, version rules, or
   compatibility guidance changed.
2. Update `pyproject.toml`. Set `[project].version` to the package version for
   the requested public release.
3. Update `CHANGELOG.md`. Add the next release section with the fixed release
   header and curated change notes.
4. Update the touched live docs and contributor instructions when the release
   changes their truth.
5. Run `make release-prepare RELEASE=vX.Y.Z CLASS=internal|additive|soft-deprecated|breaking LANGUAGE_VERSION=unchanged|X.Y CHANNEL=stable|beta|rc`.
6. Run the required proof for the touched surfaces.
7. Run `make release-tag RELEASE=vX.Y.Z CHANNEL=stable|beta|rc`.
8. Run `make release-draft RELEASE=vX.Y.Z CHANNEL=stable|beta|rc PREVIOUS_TAG=auto`.
9. Review the GitHub draft release body.
10. Run `make release-publish RELEASE=vX.Y.Z`.
11. The GitHub release publish workflow builds dist artifacts, smoke tests an
    external install, uploads release assets, and can publish to package
    indexes through Trusted Publishing when the repo settings are ready.
12. Before the first package-index publish for a new project name, register
    the GitHub Trusted Publishers on TestPyPI and PyPI for the package
    project, workflow `.github/workflows/publish.yml`, and matching
    environments such as `testpypi` and `pypi`.

The helper prints the fixed worksheet, the exact release-note header, the exact
changelog header, and the next commands to run.

## Signed Tag And GitHub Rules

- Public beta, rc, and stable tags must be signed annotated tags.
- `make release-tag` fails if the git worktree is dirty or tag signing is not
  configured.
- `make release-tag` and `make release-draft` fail if `[project].version` in
  `pyproject.toml` does not match the requested release's package version.
- `make release-draft` and `make release-publish` fail if the current public
  release tag is missing, lightweight, fails `git verify-tag`, is not pushed
  to `origin`, or points to a different tag object on `origin` than the
  verified local tag.
- Beta and RC GitHub releases must be marked as prereleases and must not be
  marked as the latest release.
- Stable releases publish from signed annotated `vX.Y.Z` tags.
- Every public release must say whether it is `Breaking` or `Non-breaking`.
- Every public release must say whether the Doctrine language version changed
  or stayed the same.
- Stable public releases are immutable once published.

## Bad Release Correction

If a public release is wrong:

- do not move a stable tag
- do not replace stable release assets in place
- fix forward with a new version
- mark the older release as `YANKED` or superseded in `CHANGELOG.md`
- update GitHub release notes only to clarify the public record

## Breaking-Change Duties

- Do not ship silent breakage.
- If a change breaks authored `.prompt` files, emitted `.contract.json` files,
  `cases.toml` manifests, or another stable public surface, update this file in
  the same change.
- Say who is affected.
- Say what changed.
- Give exact upgrade steps.
- Keep code, docs, examples, changelog, and instructions aligned.
- Update manifest-backed proof when shipped behavior changes, or say plainly
  why it did not need to change.
- If you change diagnostics, update [COMPILER_ERRORS.md](COMPILER_ERRORS.md)
  and run `make verify-diagnostics`.

## What Not To Infer

- Do not infer Doctrine language compatibility from the release version number.
- Do not infer Doctrine language compatibility from `contract_version`.
- Do not infer Doctrine language compatibility from `schema_version`.
- Do not treat the package metadata version in `pyproject.toml` as the Doctrine
  language version. It only versions the published Python package.

## Related Docs

- [../README.md](../README.md): repo entry docs
- [README.md](README.md): live docs index
- [../CHANGELOG.md](../CHANGELOG.md): portable release history
- [EMIT_GUIDE.md](EMIT_GUIDE.md): emitted contract files and layout
- [../examples/README.md](../examples/README.md): manifest-backed proof
- [COMPILER_ERRORS.md](COMPILER_ERRORS.md): stable error codes
