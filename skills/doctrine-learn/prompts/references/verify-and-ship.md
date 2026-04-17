# Verify And Ship

Every Doctrine change runs through the same loop: sync, edit, verify,
align docs, commit. This reference covers the exact commands, the
Definition of Done, release rules, and the shortcuts to avoid.

The source of truth is `/Users/aelaguiz/workspace/doctrine/AGENTS.md`.
This file teaches how to apply that truth.

## Verify Commands

Use the command that matches the surface you changed. Do not run
every command on every change.

| Command | When to run it |
| --- | --- |
| `uv sync` | After pulling new code or adding a Python dep. Syncs the locked env. |
| `npm ci` | Once per checkout. Installs the pinned flow-render dep. |
| `make verify-examples` | After any change to shipped language behavior, emit layout, or the example corpus. Runs the full manifest-backed corpus. |
| `make verify-diagnostics` | After any change to compiler diagnostics or the emit CLI error surface. |
| `make verify-package` | After changes to package metadata, publish flow, or public install work. Chains `verify-skill-install`, `build-dist`, and smoke installs for wheel and sdist. |
| `make verify-skill-install` | After a change to a first-party skill. Runs the pinned `skills` CLI smoke tests for the public install surface. |
| `uv run --locked python -m unittest tests.test_release_flow` | After release-flow or release-policy changes. |
| `uv run --locked python -m doctrine.verify_corpus --manifest examples/<dir>/cases.toml` | Fast path for one manifest-backed example. |
| `cd editors/vscode && make` | After any change under `editors/vscode/`. |
| `uv run --locked python -m doctrine.validate_output_schema --schema <path>` | After editing an `output schema` that produces an emitted `schemas/*.schema.json` file. |

Rules:

- Run the narrowest command that proves the surface you changed.
- Run `make verify-examples` before you cut a public release.
- If a dep is missing or the env cannot run a check, say that plainly
  instead of skipping.

## Definition Of Done

Pulled from `AGENTS.md`. Every change ships with these points
confirmed:

- Ran the relevant verify command for the surface you changed.
- Implementation, examples, docs, and instructions are aligned.
- If behavior changed, updated the manifest-backed proof. Or said
  plainly why the proof did not need to change.
- If the change affects public compatibility, a versioned surface, or
  the repo release flow, updated `docs/VERSIONING.md` and
  `CHANGELOG.md`.
- Kept release classification, changelog entry shape, upgrade
  guidance, and release helper output aligned when the release
  policy changes.
- Preferred a patch bump for routine public releases. Used `1.0.2`,
  not `1.2.0`, unless the release ships a real backward-compatible
  public feature, a soft deprecation, or a breaking change.

## Release Classification

Every public release uses one class. See
`/Users/aelaguiz/workspace/doctrine/docs/VERSIONING.md` for the full
rules.

- **internal**: docs-only, tooling-only, diagnostics-only, refactor,
  or cleanup. No shipped public surface changed. Non-breaking.
- **additive**: backward-compatible public additions. Non-breaking.
- **soft-deprecated**: behavior still works, but Doctrine now tells
  users how to move off of it. Non-breaking.
- **breaking**: any shipped public surface now needs user action.
  Breaking.

Version bump rules:

- **Patch** (`1.0.2`): routine internal work, fixes, docs, tooling.
  Prefer this for most public releases.
- **Minor** (`1.1.0`): real backward-compatible public additions or
  soft deprecations.
- **Major** (`2.0.0`): breaking public-surface changes.

Do not bump minor for routine work. Do not bump major without real
upgrade steps.

## Changelog Entry Shape

Before `make release-tag` or `make release-draft`, add a matching
section to `CHANGELOG.md`. The helper reads the header back out for
tag messages and GitHub draft notes. Keep it exact.

Concrete stanza (modeled on the shipped `v1.0.2` entry in
`CHANGELOG.md`):

```md
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
- Describe backward-compatible user-facing additions.

### Changed
- Describe user-visible behavior or workflow changes.
```

Rules:

- Replace every placeholder before you tag. The helper rejects
  `fill this in`, `update for this release`, `...`, and similar text.
- Breaking releases must carry real upgrade steps. Vague "this might
  break you" wording is not allowed.
- Beta and RC releases use the same shape, but `Release channel:`
  becomes `beta.N` or `rc.N` and `Release version:` uses the
  prerelease tag.

## Doc Deletion Safety

`AGENTS.md` carries one hard rule about deleting docs:

- Never delete docs without first making a restore-point commit that
  contains the pre-deletion state.
- Apply this even when the docs look stale, low-quality, or obviously
  wrong.
- If you are not making that restore-point commit in the current task,
  do not delete the docs.
- After the restore-point commit, delete stale docs instead of moving
  them into an archive directory.
- Git history is the archive. Do not keep or create `docs/archive/` as
  a long-term holding area.

Follow this order:

1. Make one commit that only contains the current state of the doc you
   plan to delete. Use a clear message such as
   `backup: pre-delete stale X`.
2. Delete the doc in the next commit.
3. Update any links that pointed at the old doc.

## What To Check Before Committing

Every commit run-through:

- Ran the verify target that matches the surface you changed.
- Implementation, examples, docs, and `AGENTS.md` are aligned.
- Updated `docs/VERSIONING.md` and `CHANGELOG.md` if public
  compatibility changed.
- Updated `/Users/aelaguiz/workspace/doctrine/docs/COMPILER_ERRORS.md`
  if you changed diagnostics, and ran `make verify-diagnostics`.
- Re-emitted first-party skill bundles when the `.prompt` source
  changed. The dev `build/` tree and the curated `skills/.curated/`
  tree must stay in sync.
- Wrote a restore-point commit before deleting any doc.

## What Not To Do

- Do not use `--no-verify` to skip pre-commit hooks. Fix the problem
  the hook reported.
- Do not use `--no-gpg-sign` on a release tag. Public tags are signed
  annotated tags.
- Do not amend an existing commit when a hook fails. Create a new
  commit after fixing the issue.
- Do not delete docs without a restore-point commit first.
- Do not create `docs/archive/` or keep old docs in a long-term
  archive directory. Git history is the archive.
- Do not move a stable tag after a bad release. Fix forward with a new
  version and mark the old release as `YANKED` in `CHANGELOG.md`.
- Do not bump the minor version for routine fixes. Prefer patch.
- Do not commit emitted `build/` drift without re-running the matching
  emit command.
- Do not hand-edit emitted Markdown, `schemas/*.schema.json`,
  `final_output.contract.json`, or `SKILL.contract.json`. Edit the
  source `.prompt`, then re-emit.
- Do not skip `make verify-examples` before a public release.

## Related References

- `references/principles.md`: the authoring principles that drive
  every verify and ship decision.
- `references/emit-targets.md`: emit commands, target config, and
  generated contract files.
- `/Users/aelaguiz/workspace/doctrine/AGENTS.md`: canonical build,
  verify, and Definition of Done rules.
- `/Users/aelaguiz/workspace/doctrine/docs/VERSIONING.md`: canonical
  versioning and release policy.
- `/Users/aelaguiz/workspace/doctrine/CHANGELOG.md`: portable release
  history and entry shapes.
- `/Users/aelaguiz/workspace/doctrine/docs/COMPILER_ERRORS.md`: stable
  error catalog.

**Load when:** The author is about to commit, cut a release, delete a
doc, or pick the right verify command for the surface they changed.
