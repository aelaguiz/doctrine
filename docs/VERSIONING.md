# Versioning

This file is the canonical home for Doctrine versioning, release rules, and
breaking-change guidance.

Current Doctrine language version: 5.7

## The Version Lines

### Doctrine Language Version

The Doctrine language version tracks grammar, semantics, and authored language
behavior.

- Use `major.minor`.
- Bump the major version when the language itself breaks.
- Retiring authored language like `required` or `optional` inside
  `output schema` is a language break even when the lowered wire shape stays
  the same.
- Bump the minor version when the language adds backward-compatible syntax or
  semantics.
- A new backward-compatible language surface such as direct `output`
  inheritance, workflow-root readable blocks, or omitted first-class IO
  wrapper titles needs the next minor language version when it ships publicly.
- A first-class named declaration such as reusable top-level `table`
  declarations also needs the next minor language version when it ships
  publicly.
- A new typed attachment such as `delivery_skill:` on `output target` also
  needs the next minor language version when it ships publicly.
- A new backward-compatible import or emit language surface such as
  directory-backed runtime package imports and emitted runtime-package trees
  also needs the next minor language version when it ships publicly.
- The high-value authoring wave that adds import aliases and symbol imports,
  grouped explicit `inherit`, review-field identity shorthand, one-line
  first-class IO wrapper refs, and `self:` path roots is one
  backward-compatible language move. It advances the language line from
  `2.0` to `2.1`.
- A new backward-compatible compile or emit API such as provider-supplied
  prompt roots needs the next minor release version when it ships publicly.
- Leave it unchanged when a release does not change the language.
- The package host-binding surface that adds inline skill `package:`,
  package `host_contract:`, skill-entry `bind:`, and package-scoped `host:`
  refs is one backward-compatible language move. It advances the language
  line from `2.1` to `2.2`.

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
- Prefer the next patch tag for routine public work. Use `v1.0.2`, not
  `v1.2.0`, for fixes, docs, tooling, packaging, and other routine
  non-breaking releases.
- Refreshing a first-party emitted skill bundle while keeping its stable code
  catalog, install layout, and machine-readable proof shape unchanged is still
  a patch-level public fix.
- Restoring a broken stable surface such as routed previous-turn emit facts is
  still a patch fix. It is not a new additive feature when the public shape
  stays the same.
- The same patch rule applies when previous-turn predecessor analysis missed an
  already-shipped route-bearing surface such as `review.on_accept` or
  `review.on_reject`.
- Use `CHANGELOG.md`, the latest signed annotated tag, and the matching
  GitHub release as the public release record.

### Narrow Support-Surface Versions

Doctrine also ships narrower version lines.

- `schema_version` in `cases.toml` only versions the corpus-manifest format.
  It is not the Doctrine language version.
- Emitted Markdown from `emit_docs` and `emit_flow` is part of the public
  surface.
- Emitted skill-package trees from `emit_skill` are part of the public
  surface when Doctrine ships first-party `SKILL.prompt` bundles.
- Emitted `SKILL.source.json` files are part of that public surface. They
  prove the source and output hashes for an emitted skill-package tree.
- When present, emitted `SKILL.contract.json` files are also part of that
  public skill-package surface.
- Generated public install trees such as `skills/.curated/agent-linter/`
  are part of the public surface when this repo is used as an `npx skills`
  source. They are build artifacts. The `.prompt` sources and emit targets
  own the shipped truth.
- For structured final outputs, emitted
  `schemas/<output-slug>.schema.json` files are also part of the public
  surface for payload wire shape.
- Emitted `final_output.contract.json` files are also part of the public
  surface for final-output, review-control, route, and `io` metadata.
- Doctrine does not ship `AGENTS.contract.json` anymore.
- The package metadata version in `pyproject.toml` versions the published
  Python package. It is not the Doctrine language version.
- `import_name`, `pypi_environment`, and `testpypi_environment` under
  `[tool.doctrine.package]` are part of the package publish path. Keep them
  explicit in `pyproject.toml`.
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
- Adding omitted first-class IO wrapper titles that lower one direct
  declaration while keeping the explicit long form valid is an `additive`
  release.
- Adding directory-backed runtime package imports, package-root `AGENTS.md`
  or `SOUL.md` emit, bundled runtime peer files, or matching shared flow-root
  behavior is an `additive` release when older local-root entrypoints still
  work.
- Adding target-owned `delivery_skill:` binding on `output target` is an
  `additive` release when existing output targets without the binding still
  work.
- Adding provider-supplied prompt roots is an `additive` release when existing
  `additional_prompt_roots`, local entrypoints, and emit target placement
  still work.
- Adding `skill package emit:` companion docs and package-local prompt imports
  is an `additive` release when existing `SKILL.md`, bundled-file, and
  bundled-agent package behavior still works.
- Adding package host binding with inline skill `package:`, package
  `host_contract:`, skill-entry `bind:`, package-scoped `host:` refs, and
  conditional emitted `SKILL.contract.json` sidecars for host-bound packages is
  an `additive` release when older inline skills and older skill packages
  still keep working unchanged.
- Adding `type: enum` plus `values:` for local `output schema` enums was an
  `additive` release when legacy `type: string` plus `enum:` still worked and
  emitted schema files kept the same string-enum wire shape. Both forms are
  deleted in the 4.1 → 5.0 breaking cut below.
- Adding a top-level `route` block to `final_output.contract.json` is an
  `additive` release when existing `final_output` and `review` keys keep their
  shape and `contract_version` stays compatible.
- The flow-root namespace cut is `breaking`. It retires relative imports and
  same-flow imports, makes `export` the cross-flow visibility gate, retires
  `E306`, adds `E314`, `E315`, and `E316`, and advances the language line from
  `3.0` to `4.0`. `E310` stays reserved for the deferred grouped-override
  investigation, and `E311` stays reserved for a future dedicated IO-wrapper
  shorthand diagnostic.
- Relaxing `E500` so carrier-mode review-driven agents may opt into
  structural binding validation with `final_output.review_fields:` is an
  `additive` language move. Existing programs keep compiling and emitting
  unchanged because the relaxation only activates when the author writes
  `review_fields:` on the carrier. Ships with a stdlib authoring pattern that
  splits `shared_rules:` from `how_to_take_a_turn:` in role homes so
  concrete roles can override the turn sequence without losing generic
  rules. Also ships a `via review.on_<section>.route` clause inside
  `next_owner:` output bodies so a shared review-carrier output can bind to
  each critic's resolved route without forking prose per layer (new compile
  code `E317`; baseline structural interpolation check still fires when both
  `via` and literal interpolation are absent). Adds `selector:` on
  `output shape` with `case EnumType.member:` dispatch inside shape bodies
  plus an agent-side `selectors:` binding so one shared output shape can
  carry role-specific field notes that the compiler inlines per agent (new
  compile codes `E318` and `E319`). Advances the language line from `4.0` to
  `4.1`. An audit pass tightened the shipped `E317` / `E318` / `E319`
  catalog to cover misplaced `case` and `via` clauses, cross-flow enum
  identity, inherited selector-backed shapes, and duplicate or unknown
  selector bindings. Language 4.1 itself is unchanged; only the diagnostic
  surface got sharper.
- Unifying field vocabularies on one canonical form is `breaking`. The 4.1 →
  5.0 cut deletes the inline `type: enum` plus `values:` form and the legacy
  `type: string` plus `enum:` form that `output schema` fields once accepted.
  The canonical form is to declare `enum X: "..."` once and type the field
  with `type: X`. Four field-shaped surfaces now accept `type: <EnumName>`
  with identical rendering: output-schema fields, readable `row_schema` and
  `item_schema` entries, readable table columns, and record scalars. The
  renderer emits a `Valid values: ...` line in declared order; the
  JSON-schema path emits the same members as `enum`. Typing against an
  unknown name fails loud with `E320`. Advances the language line from
  `4.0` / `4.1` to `5.0`. Glossary and label nodes (`properties` items,
  `definitions` items) stay prose-only by design.
- Adding a per-case `override gates:` block inside a `review_family` case
  body is an `additive` language move. One `review` contract may now back
  several cases that need slightly different gate sets without forking the
  contract. The block accepts `add NAME: "Title"`, `remove NAME`, and
  `modify NAME: "Title"` clauses, and the case still references the same
  `contract.NAME` symbols inside `checks:` (now resolved against the
  per-case effective gate set). Removing or modifying a gate the contract
  does not declare fails loud with `E531`; adding a name that already
  exists fails loud with `E532`. Existing programs without the block keep
  compiling unchanged. Advances the language line from `5.0` to `5.1`.
- Adding a typed `receipt` host-slot family to `host_contract:` is one
  backward-compatible language move. A skill package may now declare
  `receipt <slot_key>: "Title"` with typed `<field_key>: <DeclaredType>`
  entries (or `<field_key>: list[<DeclaredType>]`) so the package owns the
  typed envelope it emits on every run. Receipt slots are not call-site
  bound; the package owns them. Downstream consumers may reference fields
  through the skill binding at `<skill_binding_key>.receipt.<field_key>`.
  Empty receipt bodies fail loud with `E535`, unresolved receipt field
  references fail with `E536`, and untyped field names fail with `E537`.
  `SKILL.contract.json` now carries each receipt slot with its typed
  `fields` map so runtime hosts can validate the emitted envelope.
  Existing programs without a `receipt` slot keep compiling unchanged.
  Advances the language line from `5.1` to `5.2`.
- Adding `typed_as:` to `output target` bodies is one backward-compatible
  language move. A custom `output target` may now point at a declared
  `document`, `schema`, or `table` so the target carries the handoff-note
  family identity. Consuming outputs may then omit a redundant
  `structure:` or `schema:` line, or state the matching family for
  clarity. The emitted output contract gains one `Typed As` row
  immediately after `Target`. Typed targets whose ref does not resolve
  to a `document`, `schema`, or `table` fail loud with `E533`. If a
  downstream output's own `structure:` or `schema:` names a family that
  disagrees with the target's `typed_as:` family, the compiler raises
  `E534`. Existing programs without `typed_as:` keep compiling unchanged.
  Advances the language line from `5.2` to `5.3`.
- Adding a canonical `mode CNAME = expr as <Enum>` statement on skill
  entries and normalizing `output shape` `selector:` to the same
  production is one backward-compatible language move. Skill entries
  now distinguish producer and audit uses of the same skill with the
  same `mode_stmt` grammar production that review cases, law matchers,
  and output-shape selectors already share. Three new compile codes
  fail loud on authoring mistakes: `E540` for a mode `as` target that
  does not resolve to a declared enum, `E541` for an audit-mode skill
  entry that binds to an `output` or `final_output` host slot, and
  `E542` for a `CNAME` that is not a member of the declared enum. The
  enum-only `output shape` selector form (`mode CNAME as <Enum>`) is
  soft-deprecated with `E543`. **Timebox:** the enum-only form will be
  removed at the next minor language bump (language 5.4 → 5.5).
  Existing programs that already use the expr-based form — every
  shipped use in review cases, law matchers, and existing `mode`
  statements — keep compiling unchanged. Advances the language line
  from `5.3` to `5.4`.
- Adding an optional `: <TypedEntityRef>` annotation on `abstract`
  authored-agent slots is one backward-compatible language move. An
  abstract agent may now narrow an abstract slot to a specific
  declared family (`document`, `schema`, `table`, `enum`, `agent`, or
  `workflow`). Concrete descendants must bind the slot to a `name_ref`
  of the declared family. The compiler raises `E538` when a concrete
  binds the slot with the wrong family or an inline workflow block,
  and `E539` when the annotation fails to resolve. The annotation is
  deliberately narrower than skill `host_contract` family typing and
  output-schema field typing; the three shapes stay distinct. Existing
  untyped abstract slots keep compiling unchanged. Advances the
  language line from `5.4` to `5.5`.
- Adding the declarative top-level `rule` primitive is one
  backward-compatible language move. A `rule` declaration lints the
  authored agent graph at compile time through a closed `scope:`
  predicate set (`agent_tag: <CNAME>`, `flow: <NameRef>`,
  `role_class: <CNAME>`, `file_tree: <STRING>`) and a closed
  `assertions:` predicate set (`requires inherit <NameRef>`,
  `forbids bind <NameRef>`, `requires declare <CNAME>`). Rule-check
  diagnostics live in their own `RULE###` band so they stay visibly
  distinct from the `E###` codes. The shipped codes are `RULE001`
  (scope predicate target does not resolve), `RULE002` (assertion
  target does not resolve), `RULE003` (scoped agent fails
  `requires inherit`), `RULE004` (scoped agent violates
  `forbids bind`), and `RULE005` (scoped agent fails
  `requires declare`). **RULE-band stability rule:** codes `RULE006`
  through `RULE099` are reserved for future extensions of this
  closed-predicate surface, and codes `RULE100` and above are reserved
  for any future open-expression-language evolution of the rule
  primitive. Existing programs that declare no `rule` keep compiling
  unchanged. Advances the language line from `5.5` to `5.6`.
- Adding skill-package source receipts is one backward-compatible language
  move. `skill package` may now declare `source:` with `id:` and `track:`
  entries. `emit_skill` always emits `SKILL.source.json` beside `SKILL.md`.
  Configured skill emit targets may declare `source_root`, `source_id`, and
  `lock_file` so a downstream repo can emit from a named upstream source tree
  and verify freshness later. The new verifier command checks receipts for
  `current`, `missing_receipt`, `stale_source`, `edited_artifact`,
  `unexpected_artifact`, `foreign_package`, `lock_out_of_date`,
  `receipt_lock_mismatch`, and `unsupported_receipt_version`. Existing skill
  packages keep compiling; they now gain a receipt sidecar. Advances the
  language line from `5.6` to `5.7`.
- Adding `route field`, `final_output.route:`, and additive `route.selector`
  metadata is an `additive` release when existing `route_from`,
  `handoff_routing`, review, and emitted contract shapes keep working.
- Adding an additive top-level `io` block to `final_output.contract.json` is
  an `additive` release when existing `final_output`, `review`, and `route`
  keys keep their shape and `contract_version` stays compatible.
- `soft-deprecated`: behavior still works, but Doctrine now tells users what
  to move away from and how to move early. Release kind: `Non-breaking`.
- `breaking`: any shipped public surface now needs user action. This includes
  language breaks, emitted contract breaks, manifest-schema breaks, and other
  stable public surface breaks. Release kind: `Breaking`.
- Emitted runtime Markdown is part of that public surface. If ordinary
  `## Outputs` changes from one layout to another, downstream snapshot,
  parser, or scraper users may need to act even when the language version
  stays the same.
- First-party emitted skill-package trees are also part of that public
  surface. If emitted `SKILL.md` content or bundled companion-file layout
  changes in a way that affects installers or loaders, downstream users may
  need to act.
- The same rule applies to render-only compaction such as changing a simple
  output contract from a table to bullets, collapsing redundant compiler-owned
  wrapper headings, or replacing a repeated split-review semantics section
  with one shorter note.
- Removing emitted sidecar artifacts such as `AGENTS.contract.json` is also a
  breaking public-surface change.

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
Language version: unchanged (still 2.0)
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
6. Run the required proof for the touched surfaces. Every public release must
   also run `uv run --locked python -m unittest tests.test_package_release`
   and `make verify-package`.
7. If you changed the release flow or release policy, also run
   `uv run --locked python -m unittest tests.test_release_flow`.
8. Run `make release-tag RELEASE=vX.Y.Z CHANNEL=stable|beta|rc`.
9. Run `make release-draft RELEASE=vX.Y.Z CHANNEL=stable|beta|rc PREVIOUS_TAG=auto`.
10. Review the GitHub draft release body.
11. Run `make release-publish RELEASE=vX.Y.Z`.
12. The GitHub release publish workflow builds dist artifacts, smoke tests an
    external wheel and sdist install, uploads release assets, and publishes
    through GitHub environments plus Trusted Publishing.
13. Before the first package-index publish for a new project name, register
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
- If a change breaks authored `.prompt` files, emitted
  `schemas/<output-slug>.schema.json` files, `cases.toml` manifests, or
  another stable public surface, update this file in the same change.
- Treat emitted runtime Markdown layout as one of those stable public
  surfaces. For example, regrouping ordinary `## Outputs` from bullet lists
  into contract tables is a breaking emitted-Markdown change even though the
  input language does not change.
- Treat emitted helper-line removal the same way. For example, removing
  `_ordered list_` or `_unordered list_` from detailed readable list renders
  is a breaking emitted-Markdown change even when the language change itself
  is additive, such as making list titles optional.
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
