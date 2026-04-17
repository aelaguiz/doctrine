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

## v2.0.0 - 2026-04-17

Release kind: Breaking
Release channel: stable
Release version: v2.0.0
Language version: 2.2 -> 3.0
Affected surfaces: authored `output schema` language (authored `required` and `optional` retired; use `nullable`), emitted runtime Markdown layout (`## Outputs` now renders grouped contract tables, compacted Doctrine-owned surfaces, and drops `_ordered list_` and `_unordered list_` helper lines), emitted companion contracts (`AGENTS.contract.json` retired; `final_output.contract.json` gains additive top-level `route` and `io` blocks; emitted `schemas/<output-slug>.schema.json` is the sole structured-output wire contract; emitted `SKILL.contract.json` sidecars appear for host-bound skill packages), shipped example directory names (structured final-output examples renamed from `_json_schema` to `_output_schema`), structured `JsonObject` final-output authoring (example object now lives inside `output schema`, checked-in `.example.json` support files no longer read), Doctrine language (additive: output inheritance, first-class named `table`, omitted first-class IO wrapper titles, `delivery_skill:` on `output target`, provider-supplied prompt roots, runtime package imports and emit, workflow-root readable blocks, titleless readable lists, anonymous inline readable blocks, triple-quote escape, hyphenated code language, import aliases and symbol imports, grouped `inherit`, review-field identity shorthand, one-line IO wrapper refs, `self:` path roots, inline skill `package:`, package `host_contract:`, skill-entry `bind:`, package-scoped `host:`, `type: enum` plus `values:`, `route field` and `final_output.route:`, nullable route fields), first-party skill packages (`agent-linter` and `doctrine-learn`) with checked-in public install trees under `skills/.curated/`, diagnostics catalog (`E236`, `E237`, `E289`, `E306`–`E309`, `E312`), live docs (`AGENT_LINTER.md`, `AUTHORING_PATTERNS.md`, `DOCTRINE_LEARN.md`, `FAIL_LOUD_GAPS.md`, `THIN_HARNESS_FAT_SKILLS.md`, `WARNINGS.md`, `PRINCIPLES.md`), and VS Code extension language coverage.
Who must act: authors using `required` or `optional` inside `output schema` fields or route fields (fails loud with `E236` and `E237` in 2.0.0); downstream consumers of emitted `AGENTS.contract.json` (no longer written); downstream snapshot, parser, or scraper users of emitted `## Outputs` Markdown, the old `_ordered list_` or `_unordered list_` helper lines, or the old compiler-owned review-semantics and single-child `* Binding` wrappers; callers that read `<example>.example.json` sidecars alongside structured final outputs; downstream users referencing the renamed structured final-output example directories.
Who does not need to act: users consuming `schemas/<output-slug>.schema.json` wire shapes (string-enum wire shape unchanged), authors whose `.prompt` files already parse under 3.0, users of the stable `AL###` agent-linter catalog, users who do not rely on emitted-Markdown layout snapshots or the retired sidecar, and users of the stable `doctrine` Python import path.
Upgrade steps: (1) install `doctrine-agents==2.0.0` from the package index; (2) replace authored `required` and `optional` inside `output schema` fields and route fields with `nullable` where the field may be `null` (compile errors cite `E236` and `E237`); (3) stop reading emitted `AGENTS.contract.json` — read `final_output.contract.json` for final-output, review-control, and the new top-level `route` and `io` metadata, and read `schemas/<output-slug>.schema.json` for structured-output wire shape; (4) refresh downstream emitted-Markdown snapshots and parsers to the new `## Outputs` grouped-contract layout and updated Doctrine-owned surfaces (no `_ordered list_` or `_unordered list_` helper lines, compacted review-semantics and single-child `* Binding` wrappers); (5) move inline structured-final example objects into `output schema` and stop shipping `<example>.example.json` sidecars; (6) update any references to `*_json_schema` shipped example directories to their `*_output_schema` names; (7) optionally adopt the additive authoring forms (import aliases, grouped `inherit`, review-field identity shorthand, one-line IO wrapper refs, `self:`, inline skill `package:`, `host_contract:`, `bind:`, `type: enum` plus `values:`) — the older forms still compile.
Verification: `uv run --locked python -m unittest tests.test_package_release && make verify-package && make verify-examples && make verify-diagnostics`.
Support-surface version changes: Doctrine language 2.0 -> 3.0; package metadata 1.0.2 -> 2.0.0; distribution name `doctrine-agents` unchanged; `final_output.contract.json` gains additive top-level `route` and `io` blocks; emitted `schemas/<output-slug>.schema.json` is now the sole structured-output wire contract; emitted `AGENTS.contract.json` retired; emitted runtime Markdown layout updated for grouped `## Outputs`, compacted Doctrine-owned surfaces, and dropped helper kind lines; emitted `SKILL.contract.json` sidecars appear for host-bound skill packages; `skills/.curated/` checked-in public install trees added.

### Added
- Added the manifest-backed `125_multiline_escape_triple_quote` example and
  a diagnostic smoke check so triple-quoted literals may embed a literal
  `"""` sequence by escaping the first quote as `\"""`. All existing
  literals parse unchanged.
- Added the manifest-backed `126_hyphenated_code_language` example so
  readable `code` block `language:` values accept hyphens. Informal fence
  names like `prompt-fragment`, `shell-session`, or `js-jsx` now survive
  through the renderer without renaming the fence.
- Added the manifest-backed `127_inline_anonymous_readable_blocks` example
  so anonymous inline `code:`, `markdown:`, and `html:` blocks render bare
  inside document sections without requiring an authored key. Named blocks
  continue to parse unchanged.
- Refactored the two first-party skill packages (`skills/agent-linter/` and
  `skills/doctrine-learn/`) to author their reference bundles as Doctrine
  `document` declarations under `prompts/refs/*.prompt`, emitted to
  `references/<slug>.md` through the `skill package` `emit:` block. The
  public install trees under `skills/.curated/<name>/` are byte-identical
  to the previous raw-`.md` shape, so consumers see no change.
- Added a first-party `skills/doctrine-learn/` skill package, its
  `doctrine_learn_skill` and `doctrine_learn_public_skill` emit targets, and
  live docs at `docs/DOCTRINE_LEARN.md`. The skill is prompt-only and teaches
  Doctrine authoring end-to-end through twelve loadable references
  (principles, language overview, agents and workflows, reviews, outputs and
  schemas, documents and tables, skills and packages, imports and refs, emit
  targets, authoring patterns, examples ladder, verify and ship).
- Added a first-party `skills/agent-linter/` skill package, its
  `doctrine_agent_linter_skill` emit target, focused emit proof, and live
  docs for emit, install, and use.
- Added explicit `emit:` companion docs for `skill package`, plus package-
  local prompt imports from the `SKILL.prompt` source root so one skill can
  ship many prompt-authored `.md` files without path magic.
- Added package host binding for fat skills:
  - inline skill `package:`
  - package `host_contract:`
  - skill-entry `bind:`
  - package-scoped `host:` refs across the prompt-authored emitted tree
  - emitted `SKILL.contract.json` sidecars from `emit_skill` for host-bound
    packages
- Added the manifest-backed `124_skill_package_host_binding` example and
  focused unit and smoke proof for package host binding.
- Added a checked-in public install tree at `skills/.curated/agent-linter/`
  so `npx skills add .` discovers one supported public skill from the repo
  root.
- Added the high-value authoring wave: import aliases and symbol imports,
  grouped explicit `inherit { ... }`, bare identity shorthand on
  `review.fields`, `review override fields`, and
  `final_output.review_fields`, one-line first-class `inputs` / `outputs`
  wrapper refs, and `self:` on the existing `PATH_REF` surfaces.
- Added shipped fail-loud diagnostics `E306`, `E307`, `E308`, `E309`, and
  `E312` for that wave. `E310` stays reserved for the deferred grouped-
  override investigation, and `E311` stays reserved for a future dedicated
  IO-wrapper shorthand diagnostic.
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
- Added omitted titles for first-class `inputs` and `outputs` wrapper sections
  when the wrapper body resolves to one direct declaration. The omitted wrapper
  lowers into that declaration's heading instead of adding a second heading.
  Ambiguous shapes such as multiple direct refs or keyed child sections fail
  loud instead of guessing.
- Added workflow-root readable blocks so workflows may own non-section
  readable blocks directly instead of wrapping them in a local section first.
- Added `115_runtime_agent_packages` as the generic checked-in runtime-package
  proof example.
- Added first-class named `table` declarations so documents can reuse one
  table contract with local `table key: TableRef` use sites while keeping
  inline tables and rendered Markdown unchanged.
- Added `116_first_class_named_tables` as the focused proof example for named
  table declarations.
- Added `117_io_omitted_wrapper_titles` as the focused proof example for
  omitted first-class IO wrapper title lowering.
- Added target-owned output delivery skill binding with
  `output target ... delivery_skill:` and the focused
  `118_output_target_delivery_skill_binding` proof example.
- Added provider-supplied prompt roots so embedding runtimes can pass named
  dependency-owned `prompts/` roots without adding install paths to host
  compile config.
- Added a canonical top-level `route` block to `final_output.contract.json`.
  It exposes compiler-resolved named-agent route targets for ordinary routed
  finals, `route_only`, `route_from`, and routed review finals. Harnesses
  should read this block instead of asking the model to copy the next owner
  into a private control field.
- Added first-class routed structured final outputs with `route field` plus
  `final_output.route:`. This lets one final-output field own the route
  choice keys, labels, named targets, and emitted runtime route metadata.
- Added additive `route.selector` metadata to `final_output.contract.json`
  so harnesses can find the selected route field without local reconstruction.
- Added an additive top-level `io` block to `final_output.contract.json`.
  It carries resolved `previous_turn_inputs`, emitted `outputs`, and
  `output_bindings` in the same public runtime contract file.
- Added `type: enum` plus `values:` as the preferred local inline enum form
  for `output schema` fields. Legacy `type: string` plus `enum:` still works
  in this first cut, and both forms lower to the same emitted string-enum
  schema shape.

### Changed
- Changed the public skill install story to one line:
  `npx skills add .`.
- Tightened the first-party `agent-linter` skill so it more clearly treats
  prompt bulk without reusable leverage as bloat and keeps safety guidance in
  the existing runtime-boundary family, without changing the stable `AL###`
  catalog or the saved proof schema.
- Changed package verification to include pinned `skills` CLI smoke tests for
  discovery and Codex install.
- Changed the public docs, teaching examples, and VS Code support to teach
  the preferred additive forms for imports, grouped `inherit`, review-field
  identity binds, first-class IO wrapper shorthand, and self-addressed
  addressable refs.
- Changed `output schema` authoring for the next language-major line. Use
  `nullable` when an output-schema field or route field may be `null`.
  Object properties still stay present on the wire on the current
  structured-output profile, so this change keeps the emitted wire shape the
  same while fixing the authored language.
- Changed `emit_docs`, `emit_flow`, corpus build-contract proof, and
  diagnostic smoke checks to share one runtime frontier instead of assuming
  root-only runtime emit.
- Changed `emit_skill` to write `SKILL.contract.json` beside `SKILL.md` only
  when a skill package has real host-binding truth.
- Clarified the release policy to prefer the next patch version for routine
  public work and keep minor bumps for real backward-compatible public
  additions or soft deprecations.
- Changed structured `JsonObject` final outputs to keep their example object
  inside `output schema`, make that `example:` block optional, validate it
  against the lowered OpenAI-compatible schema when present, and stop reading
  checked-in `.example.json` support files.
- Changed `emit_docs` to write `AGENTS.md` plus the real lowered
  `schemas/<output-slug>.schema.json` artifact for structured final outputs,
  plus `final_output.contract.json` for final-output and review-control
  metadata. Doctrine no longer emits `AGENTS.contract.json`.
- Changed emitted final-output companion contracts to include
  `route.exists: false` for unrouted final responses, so harnesses can consume
  one route contract shape for routed and unrouted turns. When a final output
  carries route semantics through a nullable `route field`, `route.exists`
  now stays `true` and `route.selector.null_behavior` says whether `null`
  means no handoff.
- Renamed the shipped structured final-output examples from `_json_schema` to
  `_output_schema` so the public corpus matches the approved feature story.
- Added `python -m doctrine.validate_output_schema --schema ...` as the
  built-in file validator for emitted structured-output schema files.
- Changed emitted ordinary `## Outputs` Markdown to one grouped contract block
  per output. Single artifacts now start with a `Contract | Value` table,
  `files:` outputs add an `Artifacts` table, and `structure:` now renders as
  one `Artifact Structure` section. Downstream emitted-Markdown snapshots or
  parsers will need to update.
- Changed emitted runtime Markdown to compact several Doctrine-owned surfaces.
  Simple `TurnResponse` ordinary outputs may now render as bullet contracts,
  summary-only output structures may render as `Required Structure:` lists,
  split review finals now use one short carrier note instead of a repeated
  review-semantics section, and compiler-owned single-child `* Binding`
  wrappers may collapse when they add no extra meaning. Downstream emitted-
  Markdown snapshots or parsers will need to update.
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

### Removed
- Retired authored `required` and `optional` inside `output schema`,
  including output-schema route fields and route-field overrides. Doctrine
  still parses those spellings there only so it can raise targeted `E236` and
  `E237` upgrade errors.

### Fixed
- Fixed custom authored workflow slots such as `read_first` so workflows with
  root readable blocks no longer fail with `E901` during emit.
- Fixed emit-time previous-turn extraction so zero-config
  `RallyPreviousTurnOutput` now resolves through `final_output.route`, and
  workflow-root readable blocks no longer crash flow-graph collection on that
  path.
- Fixed emit-time previous-turn extraction so attached review outcome routes
  such as `review.on_reject -> Agent` now count as reachable predecessor
  edges for explicit `RallyPreviousTurnOutput` selectors.
- Fixed output-guard validation so ordinary `shape: JsonObject` input fields
  such as `RouteFacts.live_job` still work in workflow-law and route-only
  guards after previous-turn input validation tightened.

### Release Entry Template

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
