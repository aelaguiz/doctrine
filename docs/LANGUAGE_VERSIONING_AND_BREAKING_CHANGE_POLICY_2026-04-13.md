---
title: "Doctrine - Language Versioning And Breaking Change Policy - Architecture Plan"
date: 2026-04-13
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - README.md
  - Makefile
  - docs/README.md
  - docs/VERSIONING.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/COMPILER_ERRORS.md
  - docs/EMIT_GUIDE.md
  - examples/README.md
  - AGENTS.md
  - doctrine/emit_contract.py
  - doctrine/_release_flow/
  - doctrine/_verify_corpus/manifest.py
  - doctrine/verify_corpus.py
---

This plan was restored from git history and re-grounded to the current repo.
[docs/VERSIONING.md](VERSIONING.md) is the current live guide for the shipped
versioning surface today.
This plan remains the canonical artifact for the broader still-unshipped
language-version, release-version, and release-flow model described below.

# TL;DR

Outcome

Doctrine will ship one clear versioning and breaking-change policy with hard
boundaries between the Doctrine language version, Doctrine release versions,
and narrow support-surface versions.
A user should be able to see what changed, whether a release changed the
language or not, whether the release is breaking or non-breaking for them,
which version line moved, and the exact upgrade steps without reading git
history or guessing from scattered docs.
An operator should also be able to run the full release process, including
prerelease and stable publication, changelog and release-note preparation,
tagging, GitHub release publication, and release correction rules, from one
coherent repo-owned flow.

Problem

Doctrine already versions some machine-readable artifacts and keeps stable
compiler error codes.
It now also has a canonical breaking-change guide in `docs/VERSIONING.md`.
But it still does not publish one separate public language-version contract,
one separate release-version contract, or one full release process across
code, docs, examples, diagnostics, changelog, tags, GitHub releases, and
release recovery.

Approach

Design one canonical versioning model with two first-class lines: a Doctrine
language version for grammar and semantics, and Doctrine release versions for
tagged shipments. Keep breaking-change classification tied to real
client-visible behavior, pair each release with annotated tags and plain-
language notes, add human-readable upgrade guidance plus fail-loud diagnostics,
and wire the same rules into live docs, proof examples, and `AGENTS.md`.

Plan

Ship this in phases: expand `docs/VERSIONING.md` and the North Star into the
full public policy, ground the complete release process with external
research, update the architecture and phase plan for prereleases, stable
releases, changelog and release-note flow, signed tags, GitHub release
publication, and recovery rules, then implement the smallest repo-owned flow
that truthfully covers that full release surface.

Non-negotiables

- No ambiguous "this might break you" messaging.
- No language-version bump just because internals changed.
- No breaking change without exact upgrade guidance.
- No release version may be mistaken for a language version.
- No second source of truth for any version line or migration status.
- Keep the system human-readable first and machine-readable where it adds
  clarity.
- Fail loud when required version or migration metadata is missing or
  inconsistent.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-14
Verdict (code): COMPLETE
Manual QA: pending (non-blocking)

## Code blockers (why code is not done)

- None. Fresh audit checked the full approved ordered frontier in Section 7:
  live policy and changelog, release helper core and signed tag flow, GitHub
  draft and publish flow, live-doc convergence, and final proof.
- No execution-side weakening was found. The completed work kept the approved
  requirements for language-version separation, release-version separation,
  breaking non-language releases, signed annotated pushed tags, GitHub draft
  and publish rules, changelog alignment, and targeted release-flow proof.
- Code-complete evidence:
  - `docs/VERSIONING.md:1` through `docs/VERSIONING.md:180` now owns the public
    language-version, release-version, release-class, changelog, signed-tag,
    GitHub, correction, and breaking-change rules.
  - `CHANGELOG.md:1` through `CHANGELOG.md:57` now owns the portable release
    history template and placeholder rules.
  - `Makefile:50` through `Makefile:69` exposes the four canonical release
    operator tasks.
  - `doctrine/_release_flow/ops.py:103` through
    `doctrine/_release_flow/ops.py:167` prints the worksheet, including the
    required breaking non-language docs, release-note, instruction, and proof
    surfaces.
  - `doctrine/_release_flow/ops.py:170` through
    `doctrine/_release_flow/ops.py:271` owns tag creation, draft creation, and
    publish publication through one helper path.
  - `doctrine/_release_flow/tags.py:175` through
    `doctrine/_release_flow/tags.py:299` enforces clean worktree, signing-key,
    annotated tag, real `git verify-tag`, pushed tag, and local-vs-origin tag
    object checks.
  - `doctrine/_release_flow/parsing.py:289` through
    `doctrine/_release_flow/parsing.py:337` validates the fixed release entry
    header, non-placeholder public fields, breaking upgrade steps, and curated
    changelog body.
  - `tests/test_release_flow.py:384` through
    `tests/test_release_flow.py:513` covers current-tag rejection,
    `git verify-tag` spoof resistance, pushed-tag missing and mismatch cases,
    and the breaking non-language release worksheet.
- Proof run in this audit:
  - `uv run --locked python -m unittest tests.test_release_flow` — passed with
    22 tests.
  - `python -m py_compile doctrine/release_flow.py
    doctrine/_release_flow/common.py doctrine/_release_flow/models.py
    doctrine/_release_flow/ops.py doctrine/_release_flow/parsing.py
    doctrine/_release_flow/tags.py tests/test_release_flow.py` — passed.
  - `git diff --check` — passed.

## Reopened phases (false-complete fixes)

- None. Phase 1, Phase 2, Phase 3, Phase 4, and Phase 5 can remain
  `Status: COMPLETE`.

## Missing items (code gaps; evidence-anchored; no tables)

- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)

- Use the new release flow once on a real Doctrine release after the first
  public release entry is prepared in `CHANGELOG.md`.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-13
external_research_grounding: done 2026-04-13
deep_dive_pass_2: done 2026-04-13
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine adopts one first-class versioning contract with a separate
Doctrine language version, separate Doctrine release versions, and separate
support-surface versions, then a user should be able to look at the docs,
diagnostics, and changed release surface and tell:

- whether the change is breaking for them
- whether the tagged release is breaking or non-breaking for them
- whether the tagged release changed the language version or shipped the same
  language version again
- why it is breaking or not breaking
- which version line moved
- what exact steps upgrade their authored `.prompt` source or repo process

The policy should also let Doctrine ship releases that do not change the
language version at all when the language did not change.

## 0.2 In scope

- One canonical Doctrine versioning policy that explains:
  - the Doctrine language version for grammar, semantics, and authored
    language behavior
  - Doctrine release versions for tagged shipments
  - narrow support-surface versions such as `contract_version` and
    `schema_version`
- Clear rules for classifying changes as breaking, additive,
  soft-deprecated, or internal-only, with docs-only and diagnostics-only
  treated as internal-only.
- One canonical live guide for the current language version and versioning
  rules, one canonical stable release tag and GitHub release for the current
  released Doctrine version, and separate owner paths for narrow
  support-surface version fields such as `contract_version` and
  `schema_version`.
- Required upgrade guidance for breaking changes, including who is affected,
  old behavior, new behavior, exact upgrade steps, and before/after examples
  where helpful.
- Fail-loud diagnostics or emitted metadata updates when they materially help a
  user understand a version or migration boundary.
- Live docs updates in `docs/` and `README.md` so versioning becomes part of
  the shipped Doctrine story.
- Clear `AGENTS.md` requirements for contributors who make breaking changes.
- Git tag and release-note rules that clearly separate the release version
  from the language version while keeping both in sync with the docs.
- Rules for how each tagged release is labeled and explained as breaking or
  non-breaking.
- One canonical, low-friction repo operator flow for preparing a version
  change and creating a tagged release for both breaking and non-breaking
  releases, including releases that leave the language version unchanged.
- The full repo release process, not just the version labels:
  - prerelease and stable release channels
  - release notes plus a portable changelog
  - signed and annotated public release tags
  - GitHub draft, prerelease, and stable release publication
  - immutable stable release expectations and release-correction rules
  - release-note generation help and release-form configuration where it
    improves the operator flow without replacing curated notes
- Example-backed proof and relevant verification updates for any new versioning
  surface that becomes shipped truth.
- Architectural convergence across the canonical Doctrine owner paths:
  `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`,
  `doctrine/model.py`, `doctrine/compiler.py`, `doctrine/emit_common.py`,
  `doctrine/emit_flow.py`, `doctrine/renderer.py`, `doctrine/verify_corpus.py`,
  `docs/`, and the manifest-backed numbered corpus.

## 0.3 Out of scope

- Promising forever-support for every old syntax or semantic shape.
- Silent compatibility shims that hide real breakage.
- Inventing multiple user-facing version numbers for the same surface without a
  clear need.
- Calling a docs cleanup alone "versioning support" without a real shipped
  contract.
- Inventing external package-publishing or distribution surfaces that this repo
  does not actually own today.

## 0.4 Definition of done (acceptance evidence)

- Doctrine's live docs explain the canonical versioning model in plain English.
- A user can tell, from one canonical surface, whether a change is breaking for
  their usage and what to do next.
- A user can inspect a tagged release and tell whether it is breaking or
  non-breaking for their usage, and whether the language version changed.
- One operator can prepare and publish either a prerelease or a stable release
  by following one short canonical flow.
- Breaking changes have required human-readable upgrade guidance and exact
  adoption steps.
- The plan names one clear owner for the current language version and one
  clear owner for the current release version.
- Machine-readable version fields, if kept or added, have a clear purpose and
  do not conflict with the human-readable policy.
- `AGENTS.md` tells contributors exactly what must change when they ship a
  breaking change.
- Stable release tags and release notes follow the same language-version and
  release-version story as the live docs.
- `CHANGELOG.md`, GitHub release notes, and the live docs tell the same story
  without one replacing the others.
- The release process has an explicit rule for draft releases, prereleases,
  stable releases, signed tags, and correcting a bad public release without
  silently mutating it in place.
- The relevant proof surfaces run green, or the plan records plainly why a
  proof surface did not need to change.

## 0.5 Key invariants (fix immediately if violated)

- No silent breaking changes.
- No tagged release without a clear breaking or non-breaking call.
- No second release process parallel to the canonical repo flow.
- No major language-version bump unless a client-used surface actually breaks.
- A tagged release may ship with an unchanged language version.
- No one may infer the language version from the release version number alone.
- No dual source of truth for any version line or migration status.
- No confusing wording about who is affected.
- No public stable release may be silently mutated in place after publication.
- No public release notes may exist only on GitHub with no portable changelog
  story in the repo.
- No fallbacks or runtime shims unless they are explicitly approved and
  timeboxed.
- Keep code, docs, examples, and contributor instructions aligned.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. A user can tell in one read whether a release changed the language or not.
2. A user can tell in one read whether a change affects them.
3. Only real client-visible breakage forces language-version or upgrade work.
4. Every tagged release says whether it is breaking or non-breaking.
5. Every breaking change carries exact upgrade steps and examples.
6. Preparing and tagging a release is one short, canonical operator flow.
7. Each version line has one clear owner and one clear meaning.
8. Machine-readable support must serve human clarity, not replace it.

## 1.2 Constraints

- Shipped truth lives in `doctrine/` and the manifest-backed corpus, not in
  draft notes.
- Doctrine already versions some machine-readable surfaces today:
  `contract_version` in [doctrine/emit_contract.py](../doctrine/emit_contract.py)
  and `schema_version` in example manifests enforced by
  [doctrine/verify_corpus.py](../doctrine/verify_corpus.py).
- `docs/COMPILER_ERRORS.md` already treats stable error identities as a shipped
  contract, so versioning work must fit that same stability mindset.
- The live docs index says durable truth belongs in evergreen docs, not in
  dated plans, so this work must end in repo docs, not just in this plan.
- The repo bias is fail-loud and example-first, so versioning must be clear in
  both docs and proof surfaces.
- The policy must let Doctrine ship a tagged release without changing the
  language version when the language did not change.

## 1.3 Architectural principles (rules we will enforce)

- Version real user-facing contracts, not internal refactors.
- Keep one source of truth for each version line and for migration rules.
- Treat the language version and the release version as different things with
  different jobs.
- Never use the release version as shorthand for the language version.
- Tie breaking-change classification to the specific language surface a user
  relies on.
- Require human-readable change and upgrade guidance for every breaking change.
- Use machine-readable version fields only when they remove ambiguity.
- Diagnostics should say what changed, why it failed, and where to find the
  fix.
- Prefer additive evolution and narrow removals over broad breaking rewrites.

## 1.4 Known tradeoffs (explicit)

- This policy adds discipline to language work, but it should cut downstream
  confusion.
- "Breaking only if you use feature X" cases will need crisp definitions.
- Clear migration writing takes time, but it is cheaper than making every user
  reverse-engineer change intent from diffs.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- Doctrine's shipped language truth lives in `doctrine/`, with the numbered
  corpus through `examples/106_review_split_final_output_json_schema_partial`
  as proof.
- The live docs path now includes `README.md`, `docs/README.md`,
  `docs/VERSIONING.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/EMIT_GUIDE.md`,
  `docs/COMPILER_ERRORS.md`, `docs/WORKFLOW_LAW.md`,
  `docs/REVIEW_SPEC.md`, `docs/SKILL_PACKAGE_AUTHORING.md`, and
  `examples/README.md`.
- `doctrine/emit_contract.py` already versions emitted machine-readable
  contracts with `contract_version = 1`.
- `doctrine.verify_corpus` already enforces `schema_version = 1` for example
  manifests through `doctrine/_verify_corpus/manifest.py`.
- `docs/COMPILER_ERRORS.md` already promises stable error identities and human
  wording.
- Root `AGENTS.md` already requires fail-loud behavior, proof, and doc
  alignment. It now also says changes that affect public compatibility or a
  versioned surface must update `docs/VERSIONING.md`.

## 2.2 What's broken / missing (concrete)

- `docs/VERSIONING.md` is now the canonical place to explain today's narrow
  versioned surfaces and breaking-change duties, but Doctrine still does not
  publish a separate public language version.
- The repo now explains `contract_version` and `schema_version`, but it still
  does not publish a separate Doctrine release-version contract or a clear
  split between a released Doctrine version and a Doctrine language version.
- The repo now has a breaking-change guide, but it still does not define
  release classes such as additive or internal-only as part of a shipped
  release process.
- The repo now requires exact upgrade steps when a shipped surface breaks, but
  it still does not define a tagged release note format that carries the same
  guidance.
- A user can now check `docs/VERSIONING.md` for current shipped guidance, but
  they still cannot inspect a Doctrine release and learn the release version,
  language version, and breakage call from one release surface.
- There is no clear git tag or release-note convention that mirrors the same
  version and upgrade contract.
- There is no simple repo task surface for preparing a version change and
  creating a tagged release.
- `AGENTS.md` now covers versioned-surface updates, but it still does not
  define a full release workflow with release classification and tagged-release
  duties.

## 2.3 Constraints implied by the problem

- The fix must keep human-readable guidance as the first-class surface.
- It must allow tagged releases that do not change the language version.
- It must avoid language-version churn for internal refactors or non-language
  releases.
- It must fit Doctrine's fail-loud, example-first, docs-backed shipping model.
- It must explain how language versioning relates to existing versioned support
  artifacts instead of leaving users to infer that relationship.

# 3) Research Grounding (external + internal "ground truth")

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

These are the external anchor families that best match the repo evidence. The
official-source check now lives in the external research block below.

- Semantic Versioning — adopt as the release-number rule for tagged Doctrine
  releases; reject using one SemVer line as both the release version and the
  language version — it gives familiar breaking versus additive release
  semantics without collapsing the language contract and release cadence into
  one number.
- Python-style backwards-compatibility guidance — adopt explicit deprecation
  windows and plain migration notes when a removal can wait; reject soft
  "might break" wording — it fits Doctrine's human-readable, fail-loud bias.
- Go-style compatibility promise — adopt the rule that internal refactors
  should not force user action; reject a blanket forever-compatibility promise
  at Doctrine's current stage — the language is still growing.
- Rust-style migration guidance — adopt the idea that truly breaking changes
  need one clear upgrade path; reject edition-scale machinery unless Doctrine
  grows past a simpler policy — current scope is clarity, not a second mode.
- TypeScript-style change communication — adopt "who is affected / what changed
  / what to do" release notes and examples; reject diff-only explanations —
  this directly matches the North Star.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - [docs/LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md) — current public
    language model, declaration surface, and fail-loud rules.
  - [docs/LANGUAGE_DESIGN_NOTES.md](LANGUAGE_DESIGN_NOTES.md) — durable
    language guardrails, shipped boundary, and non-goals.
  - [docs/COMPILER_ERRORS.md](COMPILER_ERRORS.md) — stable error identities,
    code bands, and the existing "keep shipped meanings stable" policy.
  - [doctrine/emit_contract.py](../doctrine/emit_contract.py) — current
    machine-readable emitted contract owner with `contract_version = 1`.
  - [doctrine/_verify_corpus/manifest.py](../doctrine/_verify_corpus/manifest.py)
    — current manifest schema owner with `schema_version = 1` as a hard gate,
    reached through [doctrine/verify_corpus.py](../doctrine/verify_corpus.py).
  - [doctrine/diagnostics.py](../doctrine/diagnostics.py) — canonical error
    formatting and JSON-safe diagnostic payload shape.
- Canonical path / owner to reuse:
  - [docs/VERSIONING.md](VERSIONING.md) — canonical user-facing owner for the
    current shipped versioning and breaking-change guide. It exists now, but
    it still does not publish a separate Doctrine language version or tagged
    release workflow.
  - [docs/LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md) — public behavior
    companion once versioning policy links out of the syntax docs.
  - [docs/LANGUAGE_DESIGN_NOTES.md](LANGUAGE_DESIGN_NOTES.md) — guardrail
    companion once versioning policy links out of the design notes.
- Existing patterns to reuse:
  - [docs/COMPILER_ERRORS.md](COMPILER_ERRORS.md) +
    [doctrine/diagnostics.py](../doctrine/diagnostics.py) — stable identity +
    human-readable detail + fail-loud messaging.
  - [doctrine/emit_contract.py](../doctrine/emit_contract.py) +
    [tests/test_emit_docs.py](../tests/test_emit_docs.py) — versioned
    machine-readable contract with a locked payload shape.
  - [doctrine/verify_corpus.py](../doctrine/verify_corpus.py) +
    [examples/README.md](../examples/README.md) — manifest-backed proof with a
    schema-version gate.
  - [Makefile](../Makefile) +
    [doctrine/diagnostic_smoke.py](../doctrine/diagnostic_smoke.py) —
    targeted diagnostics verification already wired into the repo.
- Prompt surfaces / agent contract to reuse:
  - [README.md](../README.md), [docs/README.md](README.md), and
    [AGENTS.md](../AGENTS.md) — the current release-facing and
    contributor-facing contract surfaces that should point at the final policy.
- Native model or agent capabilities to lean on:
  - Not applicable — this is compiler, docs, and policy work, not a
    model-runtime capability gap.
- Existing grounding / tool / file exposure:
  - `make verify-examples` — broad shipped proof across the manifest-backed
    corpus.
  - `make verify-diagnostics` — stable diagnostics smoke coverage.
  - `make tests` — unit coverage for emitted contract behavior and emit-flow
    failures.
- Duplicate or drifting paths relevant to this change:
  - Version-related truth is now narrower than when this plan was written, but
    it is still spread across
    [docs/LANGUAGE_DESIGN_NOTES.md](LANGUAGE_DESIGN_NOTES.md),
    [docs/LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md),
    [docs/COMPILER_ERRORS.md](COMPILER_ERRORS.md),
    [docs/VERSIONING.md](VERSIONING.md),
    [docs/EMIT_GUIDE.md](EMIT_GUIDE.md),
    [doctrine/emit_contract.py](../doctrine/emit_contract.py),
    [doctrine/_verify_corpus/manifest.py](../doctrine/_verify_corpus/manifest.py),
    [README.md](../README.md), [docs/README.md](README.md), and
    [AGENTS.md](../AGENTS.md).
  - There is still no repo-owned release operator surface in `Makefile`, and
    no current path that ties tagged releases and release notes back to the
    live versioning guide.
  - [pyproject.toml](../pyproject.toml) and
    [doctrine/_diagnostic_smoke/flow_emit_checks.py](../doctrine/_diagnostic_smoke/flow_emit_checks.py)
    both carry `version = "0.0.0"` package or fixture metadata that should not
    be confused with a public Doctrine language version.
- Capability-first opportunities before new tooling:
  - Reuse the live docs path and existing fail-loud diagnostics before adding
    external package publishing or CI-only release gates.
  - Keep support-surface versions separate where they already guard different
    contracts instead of inventing one universal version field.
  - Prove new version behavior with narrow manifest-backed examples before
    adding a new harness.
- Behavior-preservation signals already available:
  - [examples/README.md](../examples/README.md) +
    `make verify-examples` — shipped corpus proof.
  - [tests/test_emit_docs.py](../tests/test_emit_docs.py) — emitted contract
    payload stability.
  - [tests/test_emit_flow.py](../tests/test_emit_flow.py) — emit-flow failure
    diagnostics and dependency errors.
  - [doctrine/diagnostic_smoke.py](../doctrine/diagnostic_smoke.py) +
    `make verify-diagnostics` — exact-code fail-loud diagnostics.

## 3.3 Decision gaps that must be resolved before implementation

None.

Current grounded status for this reactivated plan:

- `docs/VERSIONING.md` is the canonical user-facing owner for the current
  shipped versioning and breaking-change guide.
- [docs/README.md](README.md) and [README.md](../README.md) point readers at
  `docs/VERSIONING.md`.
- The broader model in this plan is still unshipped:
  - no separate public Doctrine language version is published today
  - no tagged release workflow is documented today
  - no `CHANGELOG.md` release history exists today
  - no `.github/release.yml` release-note configuration exists today
  - no `language_version:` prompt field exists
  - no code-owned public language-version constant exists
  - no `release-prepare`, `release-tag`, `release-draft`, `release-publish`,
    or `doctrine/release_flow.py` exists
- Those gaps are target implementation work for this plan, not unresolved
  plan-shaping decisions.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:external_research:start -->
# External Research (best-in-class references; plan-adjacent)

> Goal: anchor the plan in idiomatic, broadly accepted practices where
> applicable. This section intentionally avoids project-specific internals.

## Topics researched (and why)

- Public version lines, prereleases, and immutability — Doctrine needs one
  clear release version line, one clear language version line, and explicit
  prerelease rules that do not allow silent stable-release mutation.
- Human changelog plus GitHub release notes — the user now wants the full
  release process, so the plan needs a portable changelog plus GitHub release
  notes that stay aligned instead of competing.
- Git tags, signing, and GitHub publish flow — the repo needs one canonical
  path for signed annotated tags, draft releases, prereleases, stable
  releases, and final publication.
- Release correction rules — the plan needs an explicit answer for what
  happens when a public prerelease or stable release is wrong.

## Findings + how we apply them

### Public version lines, prereleases, and immutability

- Best practices (synthesized):
  - A versioning scheme only works when the public contract is explicit.
  - Stable release contents should stay immutable after publication.
  - Pre-release identifiers are the normal way to mark unstable beta and rc
    builds ahead of a stable release.
  - Public compatibility meaning should stay separate from narrower support
    contracts.
- Adopt for this plan:
  - Use one SemVer-like Doctrine release version for tagged releases.
  - Use one separate Doctrine language version for grammar, semantics, and
    authored language behavior.
  - Let releases ship with an unchanged language version when the language did
    not change.
  - Use SemVer-style prerelease tags for beta and rc releases:
    `vX.Y.Z-beta.N` and `vX.Y.Z-rc.N`.
  - Treat release major bumps as any shipped public surface that now requires
    client action, while release notes name the exact affected surface.
  - Treat language major bumps as breaking language changes and language minor
    bumps as backward-compatible language additions.
  - Treat stable published releases as immutable. Correction happens through a
    new version, not by moving a published stable tag.
- Reject for this plan:
  - Do not reuse package metadata like `0.0.0` as either the Doctrine release
    version or the Doctrine language version.
  - Do not use the release version as a proxy for the language version.
  - Do not bump the language version for internal-only or non-language
    releases.
  - Do not use build metadata or ad hoc suffixes as the public channel model.
- Pitfalls / footguns:
  - One version number becomes noise if it tries to cover release cadence,
    language compatibility, and support artifacts at the same time.
  - A prerelease channel becomes misleading if beta, rc, and stable are not
    clearly separated in tags and release notes.
- Sources:
  - Semantic Versioning 2.0.0 — https://semver.org/spec/v2.0.0.html — official
    versioning spec for public API, immutable releases, and prerelease naming

### Human changelog plus GitHub release notes

- Best practices (synthesized):
  - A changelog should be curated for humans, not dumped from commit history.
  - Every released version should have an entry, with an `Unreleased` section
    ready for the next cycle.
  - Deprecations, removals, and breaking changes should be easy to spot.
  - GitHub-generated notes work well as a helper when categories and excludes
    are configured, but they should not become the only release history.
- Adopt for this plan:
  - Add `CHANGELOG.md` as the portable release-history surface with one
    `Unreleased` section and one entry per public release.
  - Keep one fixed compatibility payload for every breaking change in both the
    changelog entry and the GitHub release notes:
    - affected surface
    - old behavior
    - new behavior
    - first affected version
    - who must act
    - who does not need to act
    - exact upgrade steps
    - before/after example
    - verification step
  - Keep GitHub release notes as a publication surface built from the same
    curated story, not a second source of truth.
  - Add `.github/release.yml` so GitHub-generated notes can group labels and
    exclude noise where that helps.
- Reject for this plan:
  - No commit-log-diff release notes.
  - No GitHub-only release history with no portable repo changelog.
  - No empty or vague changelog entry that points users back to git history.
- Pitfalls / footguns:
  - Generated notes get noisy fast when categories are not configured and the
    curated top section is weak.
  - A changelog without clear deprecation and removal calls still leaves users
    guessing when breakage lands.
- Sources:
  - Keep a Changelog 1.1.0 — https://keepachangelog.com/en/1.1.0/ — primary
    changelog convention and guidance on `Unreleased`, deprecations, removals,
    and yanked releases
  - GitHub Automatically Generated Release Notes —
    https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes
    — official guidance for generated notes and `.github/release.yml`

### Git tags, signing, and GitHub publish flow

- Best practices (synthesized):
  - Annotated tags are the right release tags.
  - Signed tags add provenance without changing the release-version model.
  - GitHub releases are built from tags and support draft, prerelease, and
    latest-release states.
  - Draft-first release creation fits best when immutability is enabled or
    likely to be enabled later.
- Adopt for this plan:
  - Keep `contract_version` and `schema_version` separate from both the
    Doctrine language version and Doctrine release versions.
  - Use signed annotated public tags for beta, rc, and stable releases.
  - Make the repo-owned release flow create the tag locally, verify it on the
    remote, create a draft GitHub release, then publish that draft after human
    review.
  - Make prereleases use GitHub's prerelease flag and keep them off the
    latest-release label.
  - Keep generated notes optional and additive. The fixed release header plus
    curated changelog entry stay the primary story.
- Reject for this plan:
  - Do not use lightweight tags for public Doctrine releases.
  - Do not let GitHub create the public tag for us during release creation.
  - Do not rely on manual web-only release drafting as the canonical operator
    flow.
- Pitfalls / footguns:
  - If the GitHub release command does not verify that the tag already exists,
    GitHub can create a tag from branch state instead of the signed annotated
    tag we intended.
  - If stable and prerelease tags share one note template without channel
    language, users will misread beta or rc as stable.
- Sources:
  - `git-tag` documentation — https://git-scm.com/docs/git-tag.html — official
    Git reference for annotated versus lightweight tags and tag signing
  - GitHub Signing Tags —
    https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-tags
    — official GitHub guidance for signed tags
  - GitHub About Releases —
    https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
    — official release model on top of tags
  - GitHub Managing Releases —
    https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
    — official guidance for draft, prerelease, latest, and CLI-backed publish

### Release correction rules

- Best practices (synthesized):
  - Stable releases should be fixed forward with a new version, not silently
    replaced.
  - Bad releases should stay visible in changelog history with an explicit
    correction marker.
  - Draft releases are the safe place to adjust assets or wording before the
    release becomes immutable.
- Adopt for this plan:
  - Turn on an explicit correction rule in `docs/VERSIONING.md`:
    - draft release: edit or replace before publication
    - prerelease: publish a newer prerelease if needed
    - stable release: never move the tag or replace assets; publish a new
      version and mark the older one as yanked or superseded in
      `CHANGELOG.md` and release notes
  - Keep stable release-note edits limited to clarifying text, not silently
    changing what shipped.
- Reject for this plan:
  - No silent stable-tag moves.
  - No asset overwrite after a stable release is public.
  - No deleting a bad stable release from history as if it never happened.
- Pitfalls / footguns:
  - Editing stable release notes is useful for clarifying the record, but it is
    not a substitute for shipping the correcting version.
- Sources:
  - Semantic Versioning 2.0.0 — https://semver.org/spec/v2.0.0.html — says a
    released version's contents must not be modified
  - GitHub Managing Releases —
    https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
    — official draft-first and immutable-release guidance
  - GitHub Preventing Changes to Your Releases —
    https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/preventing-changes-to-your-releases
    — official immutable-release protections
  - Keep a Changelog 1.1.0 — https://keepachangelog.com/en/1.1.0/ — guidance
    for visible yanked-release history

## Adopt / Reject summary

- Adopt:
  - one SemVer-like Doctrine release version
  - one separate Doctrine language version
  - explicit beta and rc prerelease channels
  - one required compatibility payload for every breaking change
  - separate support-surface versions for `contract_version` and
    `schema_version`
  - `CHANGELOG.md` as the portable release-history surface with an
    `Unreleased` section
  - `.github/release.yml` as helper config for generated release notes
  - signed annotated public tags plus GitHub draft and publish flow
  - immutable stable releases with explicit fix-forward and yank or supersede
    rules
  - GitHub releases and release notes that reuse the same plain-language
    migration story as the docs and changelog
- Reject:
  - package-version metadata as the public release version or language version
  - using the release version as a proxy for the language version
  - one universal version field for unrelated support surfaces
  - lightweight public release tags
  - GitHub-only release history
  - moving published stable release tags or overwriting their assets

## Decision gaps that must be resolved before implementation

No plan-shaping blockers remain after this pass. Operational preconditions are
part of the helper preflight, not open design questions:

- signed-tag support must be configured in Git before the first real release
- GitHub release publication requires `gh` plus repo write access
<!-- arch_skill:block:external_research:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `README.md` is the repo entry story. It explains what Doctrine is and how to
  run it, but it does not define a versioning contract.
- `docs/README.md` is the live docs index. It points at the shipped docs, but
  it now includes a versioning guide.
- `docs/LANGUAGE_REFERENCE.md` owns the shipped syntax and behavior overview.
- `docs/LANGUAGE_DESIGN_NOTES.md` owns durable guardrails and non-goals.
- `docs/COMPILER_ERRORS.md` owns stable error-code meanings and formatter
  order.
- `docs/EMIT_GUIDE.md` explains emitted Markdown and the companion contract.
- `examples/README.md` explains the numbered corpus and manifest-backed proof.
- `doctrine/emit_contract.py` owns the machine-readable companion contract and
  its `COMPILED_AGENT_CONTRACT_VERSION = 1` constant.
- `doctrine/verify_corpus.py` owns the public verifier entrypoint, and
  `doctrine/_verify_corpus/manifest.py` owns the hard `schema_version = 1`
  gate for `cases.toml`.
- `pyproject.toml` still has `version = "0.0.0"` as Python package metadata
  only.
- The repo now has `docs/VERSIONING.md`, but it still has no `CHANGELOG.md`,
  no `.github/release.yml`, no repo-owned GitHub release workflow or form
  config, and no git tags today.
- The repo has no first-class split between the current Doctrine language
  version and the current Doctrine release version.

## 4.2 Control paths (runtime)

1. Authored `.prompt` source flows through
   `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`,
   `doctrine/compiler.py`, and `doctrine/renderer.py` to produce the runtime
   Markdown surface.
2. `doctrine.emit_docs` emits `AGENTS.md` plus `AGENTS.contract.json`. That
   companion JSON already carries `contract_version = 1`.
3. `doctrine.verify_corpus` loads each example manifest, hard-fails if
   `schema_version != 1`, then verifies compile, render, and emit proof
   against checked-in refs.
4. `doctrine.diagnostics` formats stable `code + stage + summary` errors, but
   it does not point at any versioning or upgrade surface.
5. There is no release path in the repo that maps changelog entry, beta or rc
   or stable tag, GitHub draft or published release, current release version,
   and current language version together.

## 4.3 Object model + key abstractions

- The public language contract is implicit across the grammar, parser,
  compiler, renderer, and live docs.
- The repo already has two explicit support-surface version lines:
  `contract_version` for emitted companion contracts and `schema_version` for
  example manifests.
- Stable compiler-error identities are already treated like a shipped contract.
- There is no first-class abstraction for:
  - Doctrine language version
  - Doctrine release version
  - release channel
  - the boundary between those two lines
  - change classification
  - breaking versus non-breaking tagged releases
  - required upgrade payload
  - portable release history
  - GitHub draft or publish flow
  - bad-release correction policy
- There is also no authored `language_version:` field in prompt source and no
  code-owned public language-version constant.

## 4.4 Observability + failure behavior today

- Parse, compile, and emit failures are already fail-loud.
- Manifest schema mismatches already fail loud with
  `Expected schema_version = 1`.
- `tests/test_emit_docs.py` locks the emitted companion-contract payload shape.
- `make verify-examples`, `make verify-diagnostics`, and `make tests` are the
  existing preservation signals for this area.
- `docs/VERSIONING.md` now defines breaking-change duties, but there is still
  no shipped changelog, no release-note template, no signed-tag preflight, and
  no tagged release classification anywhere in the shipped repo truth.
- The repo emits companion contracts, but it does not read them back through a
  consumer path in `doctrine/`, so `contract_version` is write-only truth
  today.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not UI work. The user-facing surfaces here are docs, diagnostics, emitted
contracts, manifests, and release metadata.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Keep `docs/VERSIONING.md` as the canonical user-facing owner for the current
  shipped versioning guide.
- If the broader model in this plan ever ships, `docs/VERSIONING.md` should
  remain the canonical user-facing owner for:
  - current Doctrine language version
  - language-version rules
  - release-version rules
  - prerelease-channel rules
  - change-class rules
  - breaking-change payload rules
  - tagged release note shape
  - the hard boundary between the Doctrine language version, Doctrine release
    versions, and support-surface versions
- `CHANGELOG.md` becomes the portable, chronological release history with:
  - one `Unreleased` section at the top
  - one section per public beta, rc, or stable release
  - a visible `YANKED` or superseded marker when a bad public release must be
    corrected
- `docs/README.md` and `README.md` link to `docs/VERSIONING.md` as the entry
  point for versioning and upgrades, and point to `CHANGELOG.md` for release
  history.
- `docs/LANGUAGE_REFERENCE.md` stays the syntax and behavior reference. It
  links to `docs/VERSIONING.md` for compatibility and upgrade policy instead of
  trying to own that policy itself.
- `docs/LANGUAGE_DESIGN_NOTES.md` stays the guardrail and non-goal document. It
  links to `docs/VERSIONING.md` for release policy instead of becoming a mixed
  design-plus-release doc.
- `docs/EMIT_GUIDE.md` and `examples/README.md` explain the narrow version
  lines they already expose: `contract_version` and `schema_version`.
- `doctrine/emit_contract.py` and `doctrine/verify_corpus.py` keep owning
  their existing support-surface versions. The first rollout does not add a
  new public `language_version` constant in code.
- `.github/release.yml` becomes the canonical GitHub-generated note
  configuration. It groups release-note categories and excludes noisy labels or
  authors, but it does not replace the changelog or versioning guide.
- `Makefile` becomes the human operator entry surface for release work with
  four canonical commands:
  - `make release-prepare RELEASE=vX.Y.Z CLASS=internal|additive|soft-deprecated|breaking LANGUAGE_VERSION=unchanged|X.Y CHANNEL=stable|beta|rc`
  - `make release-tag RELEASE=vX.Y.Z CHANNEL=stable|beta|rc`
  - `make release-draft RELEASE=vX.Y.Z CHANNEL=stable|beta|rc PREVIOUS_TAG=auto`
  - `make release-publish RELEASE=vX.Y.Z`
- `doctrine/release_flow.py` owns the public release-helper CLI surface, and
  `doctrine/_release_flow/` owns the parsing, validation, changelog parsing,
  release-note assembly, signed-tag preflight, and GitHub draft and publish
  command internals behind those Make targets.
- Signed annotated git tags and matching GitHub releases become the canonical
  source for the current released Doctrine version. `pyproject.toml` does not.
- `docs/VERSIONING.md` becomes the canonical source for the current Doctrine
  language version. Each tagged release must restate that language version and
  say whether it changed in that release.

## 5.2 Control paths (future)

1. Prompt authoring, compile, render, emit, and corpus verification stay on
   their current code paths. The first rollout does not add a new
   `language_version:` source field.
2. Every shipped change is classified before release as one of four classes:
   internal-only, additive, soft-deprecated, or breaking.
3. Every release cycle keeps the `CHANGELOG.md` `Unreleased` section current
   until it is turned into the next public release entry.
4. The canonical release setup flow starts with:
   `make release-prepare RELEASE=vX.Y.Z CLASS=internal|additive|soft-deprecated|breaking LANGUAGE_VERSION=unchanged|X.Y CHANNEL=stable|beta|rc`
5. `release-prepare` reads the latest stable signed annotated tag, the latest
   tag on the requested channel, the current language version from
   `docs/VERSIONING.md`, and the matching `CHANGELOG.md` entry shape. It
   validates that the requested release bump, channel, and language-version
   move match the chosen class, and fails loud on mismatch.
6. `release-prepare` prints one fixed release worksheet:
   - derived release kind: breaking or non-breaking
   - derived release channel: stable, beta, or rc
   - previous stable tag
   - previous same-channel tag when relevant
   - previous language version
   - requested release version
   - requested language version state
   - changelog entry status
   - required docs and proof surfaces to update
   - exact release-note header and changelog entry header
   - exact verify commands to run
   - exact `release-tag`, `release-draft`, and `release-publish` commands to
     run next
7. Every draft and published release must carry one explicit top-line call:
   `Release kind: Breaking` or `Release kind: Non-breaking`.
8. Every draft and published release must also say:
   - release channel
   - release version
   - language version
   - affected surfaces
   - who must act
   - who does not need to act
   - exact upgrade steps
   - verification step
   - support-surface version changes, if any
9. After the docs and proof work are complete, the canonical tag flow is:
   `make release-tag RELEASE=vX.Y.Z CHANNEL=stable|beta|rc`
10. `release-tag` creates one signed annotated public tag with the canonical
    tag message, pushes that tag to `origin`, and fails loud if the tag
    already exists, the release format is invalid, the worktree is not ready,
    or tag signing is not configured.
11. The canonical draft flow is:
    `make release-draft RELEASE=vX.Y.Z CHANNEL=stable|beta|rc PREVIOUS_TAG=auto`
12. `release-draft` uses the existing pushed tag and a GitHub CLI-backed draft
    flow that verifies the remote tag, sets prerelease state for beta or rc
    releases, keeps prereleases off the latest-release label, uses the fixed
    compatibility header plus curated changelog body, and may append generated
    notes configured by `.github/release.yml`.
13. The canonical publish flow is:
    `make release-publish RELEASE=vX.Y.Z`
14. `release-publish` publishes an existing reviewed draft release. Stable
    releases publish from signed annotated `vX.Y.Z` tags and matching GitHub
    releases. Beta and rc releases publish from signed annotated prerelease
    tags and matching GitHub prereleases.
15. If a release changes the Doctrine language version, the same change must
    update:
   - `docs/VERSIONING.md`
   - the affected live docs
   - `CHANGELOG.md`
   - release notes
   - examples or verification only when shipped language behavior or proof
     contracts actually changed
16. If a change is breaking outside the language surface, the same change must
    still update:
   - `docs/VERSIONING.md`
   - `CHANGELOG.md`
   - the affected live docs
   - contributor instructions in `AGENTS.md`
   - release notes
   - examples or verification only when shipped behavior or proof contracts
     actually changed
17. Stable published releases stay immutable. If a stable release is wrong:
   - do not move the tag
   - do not replace the release assets in place
   - update the notes only to clarify the public record
   - publish a correcting new version
   - mark the older release as yanked or superseded in `CHANGELOG.md`
18. Diagnostics keep failing at the real break point. The first rollout does
   not add a generic language-version mismatch error because there is no
   prompt-level `language_version:` source field to compare against in v1.

## 5.3 Object model + abstractions (future)

Doctrine will carry a separate Doctrine release version, a separate Doctrine
language version, narrow support-surface versions, and explicit release-note
surfaces.

| Surface | Canonical owner | Meaning | Bump rule |
| --- | --- | --- | --- |
| Doctrine release version | Signed annotated git tag + matching GitHub release | The identifier for one shipped Doctrine release or prerelease | Changes on every public tag: major when any shipped public surface needs client action; minor for backward-compatible public additions or soft deprecations; patch for internal-only or other non-breaking fixes; beta and rc releases use SemVer prerelease suffixes |
| Doctrine language version | `docs/VERSIONING.md`, restated in each tagged release | The grammar, semantics, and authored language behavior that release ships | Changes only when the language surface changes: major for breaking language changes; minor for backward-compatible language additions; unchanged for releases that do not change the language |
| Emitted companion contract | `doctrine/emit_contract.py` | The machine-readable JSON contract for emitted agent metadata | Bump `contract_version` only when that JSON contract becomes incompatible |
| Corpus manifest schema | `doctrine/verify_corpus.py` plus `examples/*/cases.toml` | The manifest shape required by corpus verification | Bump `schema_version` only when the manifest contract becomes incompatible |

Release publication also has two non-version surfaces:

| Surface | Canonical owner | Meaning | Update rule |
| --- | --- | --- | --- |
| Portable release history | `CHANGELOG.md` | Curated chronological history with one `Unreleased` section and one entry per public release | Update on every public release and every visible correction or yank |
| Generated-note config | `.github/release.yml` | GitHub-generated note categories and excludes | Update only when release-note grouping rules change |

Change classification will be explicit and shared across docs, release notes,
and contributor workflow.

| Class | When it applies | Release version move | Language version move | Tagged release call | Required guidance |
| --- | --- | --- | --- | --- | --- |
| Internal-only | Refactor, cleanup, docs-only, diagnostics-only, or tooling change that does not change any shipped public surface contract | Patch | Unchanged | Non-breaking | Brief note only |
| Additive | New backward-compatible public capability | Minor | Minor only if the added capability changes the language surface; otherwise unchanged | Non-breaking | What was added and who may want it |
| Soft-deprecated | Existing behavior still works, but a future removal is now announced | Minor | Unchanged | Non-breaking | What is discouraged now, when removal may happen, and how to move early |
| Breaking | Any shipped surface now requires client action, including language semantics, stable error-code meaning, emitted contract compatibility, or manifest schema compatibility | Major | Major only if the language surface itself broke; otherwise unchanged | Breaking | Full compatibility payload |

The required compatibility payload for every breaking change is fixed:

- affected surface
- old behavior
- new behavior
- first affected version
- who must act
- who does not need to act
- exact upgrade steps
- before/after example
- verification step

This is the release-note header shape for every tagged release:

- `Release kind: Breaking` or `Release kind: Non-breaking`
- `Release channel: stable` or `Release channel: beta.N / rc.N`
- `Release version: vX.Y.Z`
- `Language version: unchanged (still X.Y)` or `Language version: X.Y -> Z.W`
- `Affected surfaces: ...`
- `Who must act: ...`
- `Who does not need to act: ...`
- `Upgrade steps: ...`
- `Verification: ...`
- `Support-surface version changes: ...`

This is the channel rule that keeps release staging readable:

| Channel | Tag shape | GitHub release state | Latest-release rule | Use case |
| --- | --- | --- | --- | --- |
| `stable` | `vX.Y.Z` | Published normal release | latest or auto | Supported public release |
| `beta` | `vX.Y.Z-beta.N` | Published prerelease | never latest | Early public feedback for likely unstable work |
| `rc` | `vX.Y.Z-rc.N` | Published prerelease | never latest | Final candidate before stable; mostly bug and wording cleanup |

This is the operator rule that keeps release kind, channel, and version moves
explicit:

| Operator input | Derived release kind | Allowed release-version move | Allowed language-version move |
| --- | --- | --- | --- |
| `CLASS=internal LANGUAGE_VERSION=unchanged CHANNEL=stable|beta|rc` | Non-breaking | Patch only | Unchanged only |
| `CLASS=additive LANGUAGE_VERSION=unchanged CHANNEL=stable|beta|rc` | Non-breaking | Minor only | Unchanged when the release adds no language feature |
| `CLASS=additive LANGUAGE_VERSION=<next minor> CHANNEL=stable|beta|rc` | Non-breaking | Minor only | Minor only when the release adds language syntax or semantics |
| `CLASS=soft-deprecated LANGUAGE_VERSION=unchanged CHANNEL=stable|beta|rc` | Non-breaking | Minor only | Unchanged only |
| `CLASS=breaking LANGUAGE_VERSION=unchanged CHANNEL=stable|beta|rc` | Breaking | Major only | Unchanged when the break is outside the language surface |
| `CLASS=breaking LANGUAGE_VERSION=<next major> CHANNEL=beta|rc|stable` | Breaking | Major only | Major only when the language surface itself broke |

## 5.4 Invariants and boundaries

- `docs/VERSIONING.md` is the one live policy owner for current language
  version, language-version rules, and upgrade rules.
- `CHANGELOG.md` is the one portable release-history owner.
- `Makefile` plus `doctrine/release_flow.py` are the one repo operator surface
  for preparing, tagging, drafting, and publishing a release.
- `.github/release.yml` may shape generated notes, but it does not replace
  `CHANGELOG.md` or `docs/VERSIONING.md`.
- The latest stable signed annotated tag and matching GitHub release are the one
  source of truth for the current released Doctrine version.
- Do not infer the current language version from the release version number.
- Tagged releases may ship an unchanged language version.
- Every tagged release must say whether the language version changed.
- Do not reuse `pyproject.toml` package metadata as the public Doctrine
  release version or language version.
- Do not add a new `language_version:` prompt field in the first rollout.
- Keep `contract_version` and `schema_version` separate from both the Doctrine
  language version and the Doctrine release version.
- Stable tagged releases must stay immutable once published.
- Public beta, rc, and stable tags must be signed annotated tags.
- Every tagged release must say clearly whether it is breaking or
  non-breaking.
- Every prerelease must be marked as a prerelease and must not be marked as the
  latest release.
- `release-prepare`, `release-tag`, `release-draft`, and `release-publish` are
  the only supported repo release task surfaces in the first rollout.
- Breaking notes must name affected and unaffected users, not just changed
  files.
- Do not create a second live release-notes path under `docs/`. Dated release
  notes belong in `CHANGELOG.md` and GitHub releases. Evergreen rules belong in
  `docs/VERSIONING.md`.
- Do not let GitHub-generated notes become the only human-readable release
  history.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not UI work.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Canonical versioning guide | `docs/VERSIONING.md` | canonical live doc | A user-facing versioning owner now exists, but it stays narrow | Expand it so it defines the public language version, release version, prerelease channels, release classes, breaking-change payload, signed-tag rules, draft and publish flow, and correction policy | Users still need one place to learn the full policy | Existing live docs SSOT for versioning and upgrades | Docs-only |
| Portable release history | `CHANGELOG.md` | new top-level changelog | No portable release history exists today | Add one curated changelog with `Unreleased`, one entry per public release, and visible yank or supersede markers | Users should not need GitHub alone to learn release history | Canonical portable release-history surface | Docs-only unless helper code parses it |
| GitHub release-note config | `.github/release.yml` | generated-note categories | No GitHub release-note config exists today | Add generated-note categories and excludes that fit Doctrine's release classes and noise profile | Generated notes are useful only if they stay readable | Canonical GitHub-generated note helper config | Docs-only unless helper code validates it |
| Release operator flow | `Makefile`, `doctrine/release_flow.py`, `doctrine/_release_flow/*`, `tests/test_release_flow.py` | No release task surface exists today | Add `make release-prepare`, `make release-tag`, `make release-draft`, and `make release-publish` with one validating helper | The user wants the full release process to stay simple and repeatable | Canonical repo operator flow for release prep, signed tags, drafts, and publish | `tests/test_release_flow.py` plus any docs checks this helper depends on |
| Docs index | `docs/README.md` | live docs index | The versioning entry point already exists | Keep `docs/VERSIONING.md` near the top of the live path and keep dated plan docs out of the live reader path | Users start here for docs navigation | Live docs path includes the versioning guide without adding a second owner | Docs-only |
| Repo entry docs | `README.md` | top-level project story | A versioning entry point already exists | Keep short pointers to the versioning guide, changelog, and public release model whenever the release policy grows | Users often start here first | README points to the canonical versioning owner and release history | Docs-only |
| Language docs | `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_DESIGN_NOTES.md` | syntax reference and guardrails | These docs could drift into mixed policy ownership | Keep their narrow roles and link out to `docs/VERSIONING.md` for compatibility policy | Prevent split truth across docs | Syntax and design docs stay narrow | Docs-only |
| Diagnostics contract | `docs/COMPILER_ERRORS.md`, `doctrine/diagnostics.py` | stable error codes and formatting | Stable error-code meaning exists, but no upgrade-policy bridge | Keep stable code meanings; add versioning-guide pointer only where breaking guidance is useful; do not add generic version mismatch code in v1 | Breaking changes should be explained at the real failure point without noisy new machinery | Diagnostics keep current contract; guidance link is additive only | `make verify-diagnostics` only if diagnostics change |
| Emitted contract surface | `doctrine/emit_contract.py`, `docs/EMIT_GUIDE.md`, `tests/test_emit_docs.py` | `COMPILED_AGENT_CONTRACT_VERSION`, contract docs | Contract version is real but isolated | Keep `contract_version` separate; document what it covers and when it bumps | Contract consumers need a narrow compatibility story | Companion-contract version stays a surface-local contract | `tests/test_emit_docs.py` if payload or wording changes in code |
| Corpus manifest surface | `doctrine/_verify_corpus/manifest.py`, `doctrine/verify_corpus.py`, `examples/README.md`, `examples/*/cases.toml` | `schema_version` gate and manifest docs | Manifest schema version is real but isolated | Keep `schema_version` separate; document what it covers and when it bumps | Manifest authors need a narrow compatibility story | Manifest schema version stays a surface-local contract | `make verify-examples` if manifest behavior or examples change |
| Contributor workflow | `AGENTS.md` | build, verify, definition of done | A narrow versioning-update rule now exists | Keep the existing `docs/VERSIONING.md` update rule. Add changelog, release classification, release-history, and correction duties when the broader model ships | Contributors must follow the same policy users read | Contributor contract includes release-history and versioned-surface duties | Docs-only |
| Release surface | git tags, GitHub releases, `gh` | public release point | No declared release convention | Standardize signed annotated beta, rc, and stable tags plus matching GitHub draft and published releases | Git and GitHub must tell the same story as the docs and changelog | Public tag + GitHub release become release SSOT | `tests/test_release_flow.py` plus cold-read checks for generated worksheet, changelog entry, and release-note body |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  Under this plan, `docs/VERSIONING.md` becomes the user-facing owner for the
  public language version and versioning policy. `CHANGELOG.md` becomes the
  portable release-history owner. Signed annotated tags and matching GitHub
  releases become the current release-version owner. Narrow support-surface
  versions stay owned by `doctrine/emit_contract.py` and
  `doctrine/verify_corpus.py`.
- Deprecated APIs (if any):
  None in the first rollout. This plan adds policy and release-operator flow,
  not a new runtime API.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  Do not create `docs/releases/`, a second versioning guide, a new public
  language-version constant in code, a new `language_version:` prompt field
  for v1, a GitHub-only release history with no `CHANGELOG.md`, unsigned public
  release tags, or a second release helper path outside `Makefile` plus the
  one helper module. Rewrite versioning mentions in place on the surviving
  live docs path.
- Capability-replacing harnesses to delete or justify:
  None beyond the one narrow release helper and GitHub release config. This
  rollout still does not need external registry publication, CI autopublish,
  parsers, or wrappers.
- Live docs/comments/instructions to update or delete:
  `README.md`, `CHANGELOG.md`, `.github/release.yml`, `Makefile`,
  `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md`,
  `docs/EMIT_GUIDE.md`, `examples/README.md`, `AGENTS.md`,
  `doctrine/release_flow.py`, `doctrine/_release_flow/*`, and
  `tests/test_release_flow.py`. Add short boundary comments in
  `doctrine/emit_contract.py` or
  `doctrine/verify_corpus.py` only if the implementation touches those files.
- Behavior-preservation signals for refactors:
  `make verify-examples`, `make verify-diagnostics` if diagnostics move,
  `tests/test_emit_docs.py` if the companion contract changes, helper tests for
  release validation behavior, helper tests for changelog and GitHub command
  assembly, and manual cold read of the new docs plus release-note template.
- Breaking changes must say exactly who is affected and who is not affected.
- Tagged releases must say clearly whether they are breaking or non-breaking.
- Tagged releases must say clearly whether the language version changed or
  stayed the same.
- Tagged prereleases must say clearly that they are beta or rc and not stable.
- Release notes must use the same compatibility payload and version names as
  the live docs and changelog.
- Stable release tags should identify one immutable public release point.
- The canonical release flow must stay short enough that one operator can run
  it without reading several docs.
- No compatibility shim should become the default answer to a breaking change.

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| --- | --- | --- | --- | --- |
| Docs index | `docs/README.md` | Link to one canonical versioning guide | Stops users from hunting across docs | Include |
| Portable release history | `CHANGELOG.md` | One curated changelog with `Unreleased` and per-release entries | Stops GitHub from becoming the only release history | Include |
| Generated-note config | `.github/release.yml` | One GitHub release-note config tied to the repo's release classes | Stops generated notes from drifting into noise | Include |
| Operator tasks | `Makefile`, `doctrine/release_flow.py` | One canonical release prep, tag, draft, and publish flow | Stops release drift and hand-written one-off steps | Include |
| GitHub release publication | `gh` + GitHub releases | Draft first, publish after review, prerelease and latest rules | Stops ad hoc release creation and tag drift | Include |
| Repo entry docs | `README.md` | Point to versioning, changelog, and release policy | Stops a split between repo entry docs and live docs | Include |
| Syntax docs | `docs/LANGUAGE_REFERENCE.md` | Link out for compatibility policy instead of owning it | Keeps syntax reference from becoming a release guide | Include |
| Design guardrails | `docs/LANGUAGE_DESIGN_NOTES.md` | Link out for release policy instead of owning it | Keeps design notes narrow and stable | Include |
| Emit docs | `docs/EMIT_GUIDE.md` | Explain `contract_version` as a narrow version line | Prevents users from treating it as the language version or release version | Include |
| Corpus docs | `examples/README.md` | Explain `schema_version` as a narrow version line | Prevents users from treating it as the language version or release version | Include |
| Error docs | `docs/COMPILER_ERRORS.md` | Keep stable error meanings and point to versioning guide when useful | Aligns failure guidance with release policy | Include |
| Support-surface code | `doctrine/emit_contract.py`, `doctrine/verify_corpus.py` | Keep narrow version owners where they already live | Preserves code-owned surface boundaries | Include |
| Package metadata | `pyproject.toml` | Keep package version separate from language and release versions | Prevents false SSOT | Exclude |
| Prompt syntax | grammar, parser, compiler | Do not add `language_version:` in v1 | Prevents repo-wide churn and a second version source | Exclude |
| External package publication | CI, package registry pipeline | Do not automate registry release beyond the repo's own Git and GitHub release flow in v1 | Keep the first rollout repo-owned and easy to trust | Exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Full policy and changelog model in live docs

Status: COMPLETE

Completed work:

- Expanded `docs/VERSIONING.md` into the live owner for language-version
  rules, release-version rules, release classes, fixed changelog header
  fields, signed-tag rules, and correction policy.
- Added `CHANGELOG.md` as the portable release-history surface with one
  `Unreleased` section and a fixed public release-entry template.
- Updated `AGENTS.md` so release-flow work now has an explicit verify command
  and a hard rule to keep `docs/VERSIONING.md` and `CHANGELOG.md` aligned.

* Goal: Make `docs/VERSIONING.md`, `CHANGELOG.md`, and `AGENTS.md` the human
  source of truth for the full release process before helper code lands.
* Work: Expand `docs/VERSIONING.md` to define the Doctrine language version,
  Doctrine release version, prerelease channels, release classes, fixed
  compatibility payload, signed-tag rules, draft and publish flow, and bad-
  release correction policy. Add `CHANGELOG.md` with `Unreleased`, one
  per-release entry shape, and yanked or superseded rules. Update `AGENTS.md`
  so contributors must keep release classification, changelog, upgrade
  guidance, and `docs/VERSIONING.md` aligned when the broader model ships.
* Verification (required proof): Cold-read `docs/VERSIONING.md`,
  `CHANGELOG.md`, and `AGENTS.md` together and confirm they answer the same
  questions with the same terms. No repo verify command is needed if this
  phase stays docs-only.
* Docs/comments (propagation; only if needed): Keep `docs/VERSIONING.md` as the
  only live policy owner and `CHANGELOG.md` as the only portable release
  history. Do not copy policy text into other docs yet.
* Exit criteria: A reader can learn the full release model from
  `docs/VERSIONING.md` plus `CHANGELOG.md`, and contributor duties in
  `AGENTS.md` match them.
* Rollback: Revert `docs/VERSIONING.md`, `CHANGELOG.md`, and `AGENTS.md`
  together if the model is not stable enough to encode yet.

## Phase 2 — Release helper core and signed tag flow

Status: COMPLETE

Completed work:

- Added `doctrine/release_flow.py` as the public helper surface and
  `doctrine/_release_flow/` for the internal parsing, validation, worksheet,
  and git preflight logic.
- Added `make release-prepare` and `make release-tag` to `Makefile`.
- Added `tests/test_release_flow.py` coverage for release-move validation and
  tag preflight failure.
- Added one shared release-entry validation path for prepare-ready status, tag
  creation, and draft creation. It now rejects wrong release kind, wrong
  language-version state, placeholder compatibility payload fields, and stale
  support-surface wording.
- Added prior-release-tag validation so release math now rejects lightweight
  and ordinary unsigned public tags before using them as release history.
- Split the shared release-flow helper again into smaller modules by moving
  git error handling into `doctrine/_release_flow/common.py` and release-tag
  parsing and proof into `doctrine/_release_flow/tags.py`.
- Replaced marker-text public-tag checks with real `git verify-tag`
  validation.
- Updated the release worksheet so breaking non-language releases now list
  `docs/VERSIONING.md`, affected live docs, release-note work, contributor
  instructions, and proof duties.

* Goal: Make the release classification, channel, version-move rules, and
  signed-tag path executable through one repo-owned flow.
* Work: Add `doctrine/release_flow.py`, add `make release-prepare` and
  `make release-tag` in `Makefile`, and add `tests/test_release_flow.py`.
  Parse the current language-version value from `docs/VERSIONING.md`, inspect
  the latest stable and same-channel tags, inspect the matching changelog
  state, validate the requested release move and channel, fail loud on dirty
  worktree or missing signing config, print the fixed release worksheet, and
  create and push signed annotated beta, rc, or stable tags.
* Verification (required proof): Run targeted release-helper unit coverage with
  `uv run --locked python -m unittest tests.test_release_flow`. Cold-read one
  non-breaking stable worksheet, one breaking prerelease worksheet, and one
  unchanged-language worksheet.
* Docs/comments (propagation; only if needed): Update command examples in
  `docs/VERSIONING.md` if flags or wording shift while coding. Add one short
  boundary comment in `doctrine/release_flow.py` only where the docs-owned
  language-version parse, changelog parse, or tag-validation rule would
  otherwise be hard to see.
* Exit criteria: One operator can prepare a release and create and push a
  signed annotated tag through `Makefile`, helper tests pass, and the helper
  fails loud when the requested release move or signing state conflicts with
  the policy.
* Rollback: Remove the helper, Make targets, and helper tests together if the
  flow cannot express the policy truthfully.

## Phase 3 — GitHub draft and publish flow

Status: COMPLETE

Completed work:

- Extended `doctrine/release_flow.py` with `draft` and `publish` paths.
- Added `.github/release.yml` for generated-note categories and excludes.
- Added `make release-draft` and `make release-publish` to `Makefile`.
- Added targeted tests for prerelease draft command assembly, generated-note
  diff anchors, and publish command assembly.
- Added the same stronger release-entry validation before GitHub draft
  creation, so drafts now fail loud on stale or placeholder changelog truth.
- Added proof for both the stable draft body path and the prerelease draft
  body path.
- Added local current-tag validation before `release-draft` and
  `release-publish`, so both GitHub publication paths now fail loud when the
  local target release tag is missing, lightweight, or ordinarily unsigned.
- Tightened `release-draft` and `release-publish` again so both commands now
  verify that `origin` points at the same verified local signed annotated tag
  object before GitHub publication.
- Updated `docs/VERSIONING.md` so the live guide now matches the pushed-tag
  publication boundary.

* Goal: Make the GitHub release step part of the same repo-owned release path.
* Work: Add `make release-draft` and `make release-publish`, add
  `.github/release.yml`, and extend `doctrine/release_flow.py` so draft
  releases use the existing pushed tag, verify the remote tag, mark beta and rc
  releases as prereleases, keep prereleases off the latest-release label, and
  compose release notes from the fixed compatibility header plus curated
  changelog entry while still supporting a generated-note appendix from
  `.github/release.yml`.
* Verification (required proof): Run targeted release-helper unit coverage for
  GitHub command assembly and release-note rendering with
  `uv run --locked python -m unittest tests.test_release_flow`. Cold-read one
  stable draft body and one prerelease draft body. Do not require a live
  network publish in automated tests.
* Docs/comments (propagation; only if needed): Update `docs/VERSIONING.md` and
  `CHANGELOG.md` examples if note wording or command flags shift while coding.
  Keep `.github/release.yml` comments short and tied to the release classes.
* Exit criteria: One operator can draft and publish a GitHub release through
  the repo flow, beta and rc drafts are marked as prereleases, stable drafts
  are not, and the notes come from the same story as the docs and changelog.
* Rollback: Remove the GitHub release targets and config together if the flow
  is unreliable or becomes a second source of truth.

## Phase 4 — Live doc and support-surface convergence

Status: COMPLETE

Completed work:

- Updated `README.md`, `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, and
  `docs/LANGUAGE_DESIGN_NOTES.md` to point readers at the canonical versioning
  guide and changelog.
- Updated `docs/EMIT_GUIDE.md`, `examples/README.md`, and
  `docs/COMPILER_ERRORS.md` so `contract_version`, `schema_version`, and the
  release-helper error codes are now framed as narrow or release-local
  surfaces only.

* Goal: Align every touched live doc and narrow support-surface guide with the
  new model without creating a second owner.
* Work: Update `README.md`, `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/EMIT_GUIDE.md`,
  `examples/README.md`, and `docs/COMPILER_ERRORS.md` where needed so they
  point back to `docs/VERSIONING.md` for policy, point to `CHANGELOG.md` for
  release history, and explain `contract_version` and `schema_version` as
  narrow version lines only. No behavior change is planned for
  `doctrine/emit_contract.py` or `doctrine/_verify_corpus/manifest.py` in this
  phase.
* Verification (required proof): Cold-read the touched docs and confirm no live
  doc competes with `docs/VERSIONING.md` or `CHANGELOG.md`. No additional repo
  verify command is expected in this phase because the plan does not change
  shipped language behavior, manifest semantics, or diagnostics behavior here.
* Docs/comments (propagation; only if needed): Delete or rewrite stale touched
  versioning wording in place. Do not create a second versioning guide or a
  `docs/releases/` tree.
* Exit criteria: Touched docs, support-surface docs, and optional boundary
  comments all describe one versioning story with one live policy owner and
  one portable release-history owner.
* Rollback: Revert the touched live docs and optional boundary comments
  together if they create mixed ownership or stale wording.

## Phase 5 — Final proof and release-readiness cleanup

Status: COMPLETE

Completed work:

- Ran `uv sync` and `npm ci`.
- Ran `uv run --locked python -m unittest tests.test_release_flow`.
- Ran `git diff --check`.
- Synced the helper, live docs, changelog, and contributor instructions to the
  same release-version and language-version story.
- Expanded `tests/test_release_flow.py` to cover wrong release kind, wrong
  language-version header, placeholder verification text, unsigned or
  lightweight prior tags, and stable draft release-body rendering.
- Expanded `tests/test_release_flow.py` again to cover missing, lightweight,
  and unsigned current release tags on the draft and publish paths.
- Reran `uv run --locked python -m unittest tests.test_release_flow` after the
  audited fixes landed.
- Expanded `tests/test_release_flow.py` again to cover real `git verify-tag`
  enforcement, missing pushed public tags, mismatched pushed tag objects, and
  the breaking non-language release worksheet.

Manual QA (non-blocking):

- Use the new release flow once on a real Doctrine release after the first
  public release entry is prepared in `CHANGELOG.md`.

* Goal: Close the remaining gaps so the repo is ready to ship the full release
  model without stale live truth.
* Work: Reconcile any leftover call-site-audit items, finalize the helper's
  release-note header and tag-message wording, finalize yank or supersede
  wording for bad releases, and sync all touched docs, instructions, and tests
  to the same terms. Do not add external registry publication, CI autopublish,
  or a prompt-level `language_version:` field.
* Verification (required proof): Run the smallest full set that matches the
  touched surfaces. Expected floor: targeted release-helper tests, one local
  dry run of the release path against a temp git repo or mocked GitHub
  boundary, and a cold read of the generated release worksheet, changelog
  entry, and draft release body.
* Docs/comments (propagation; only if needed): Final pass over
  `docs/VERSIONING.md`, `CHANGELOG.md`, `README.md`, `docs/README.md`, and
  `AGENTS.md` to remove stale release wording before any real public release is
  created.
* Exit criteria: Docs, changelog, helper output, GitHub release config,
  instructions, and proof surfaces all tell the same release-version and
  language-version story, and no touched live versioning text is stale.
* Rollback: Revert final wording and helper-output polish together before any
  real public release is created.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

Avoid verification bureaucracy. Prefer the smallest existing signal. Default to
1-3 checks per meaningful phase. Keep manual cold-read review for finalization
unless a code change needs stronger proof.

## 8.1 Unit tests (contracts)

- Add targeted helper tests for release class, release channel, SemVer and
  prerelease tag parsing, language-version move validation, changelog entry
  parsing, release-note body rendering, signed-tag preflight behavior, and
  GitHub draft and publish command assembly.
- Keep diagnostics tests unchanged unless implementation changes diagnostics.
  This plan does not change diagnostics behavior.

## 8.2 Integration tests (flows)

- Expected proof for this plan is
  `uv run --locked python -m unittest tests.test_release_flow`.
- Cold-read one non-breaking stable worksheet, one breaking prerelease
  worksheet, one unchanged-language worksheet, one stable draft release body,
  and one prerelease draft release body.
- This plan does not change shipped language behavior, manifest semantics,
  emitted contract payloads, or diagnostics behavior. Do not use
  `make verify-examples`, `make verify-diagnostics`, or emit-contract tests as
  baseline proof unless implementation expands into those surfaces and the plan
  is reopened.

## 8.3 E2E / device tests (realistic)

Not device work. The realistic end-to-end check here is a dry run of the full
repo-owned release path against a temp git repo or mocked GitHub boundary plus
a cold read of the live docs, changelog, and release notes to confirm a user
can tell what changed, which version line moved, and what to do next.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

Roll this out through the live docs set plus `CHANGELOG.md`, not through dated
plan notes. The policy should ship before or with the first release that claims
to use it. Breaking or wide-scope changes should use beta or rc releases first
when that helps gather feedback. Stable releases should publish from signed
annotated tags, reviewed GitHub draft releases, and plain-language notes with
an explicit upgrade path. Every stable release should also say whether the
language version changed or stayed the same.

## 9.2 Telemetry changes

No product telemetry is assumed. The likely operational signal is better docs,
clearer diagnostics, and fewer user questions about whether a change applies to
them.

## 9.3 Operational runbook

- Keep the live docs index aligned with the versioning guide.
- Keep `CHANGELOG.md` aligned with the current release story and keep the
  `Unreleased` section ready for the next cycle.
- Keep `AGENTS.md` aligned with the shipped policy.
- If a breaking change lands, update the right version truth in the same
  change:
  - language version in `docs/VERSIONING.md` when the language changed
  - release version in the tag, `CHANGELOG.md`, and release notes
  - upgrade guidance and proof surfaces where they changed
- Use the canonical repo release flow in order:
  - `make release-prepare`
  - run the required verify commands
  - `make release-tag`
  - `make release-draft`
  - review the draft release body
  - `make release-publish`
- Publish stable releases from signed annotated tags and matching
  plain-language release notes that also state the shipped language version.
- If a public stable release is bad, fix forward with a new version. Do not
  move the stable tag or replace its assets in place. Mark the older release as
  yanked or superseded in `CHANGELOG.md` and clarify the GitHub release notes
  as needed.
- Keep old plans out of the live docs path once their durable truth lands.

# 10) Decision Log (append-only)

These entries stay close to the original plan record.
Some follow-ups below already shipped. Others are still only proposed work.

## 2026-04-13 - Treat versioning and breaking-change guidance as shipped truth

Context

Doctrine already has versioned support artifacts and stable compiler-error
identities, but it does not yet have one clear language-version and
breaking-change contract that users and contributors can follow.

Options

- Keep versioning implicit and rely on release notes or git history.
- Version support artifacts only and leave the language story informal.
- Add one integrated Doctrine versioning and breaking-change policy across
  code, docs, proof, diagnostics, and contributor guidance.

Decision

Plan around one integrated policy. Docs-only hints or artifact-only version
numbers are not enough for the requested clarity.

Consequences

- The work must touch code-owned version truth, live docs, proof surfaces, and
  contributor instructions together.
- The policy must explain how language versioning relates to existing artifact
  versions.
- The final design must minimize version churn for users who do not touch the
  changed surface.

Follow-ups

- Run `research` against strong external anchors and Doctrine's current
  versioned surfaces.
- Resolve the canonical owner path and version model in `deep-dive`.
- Build the authoritative phase plan only after those choices are explicit.

## 2026-04-13 - Use one public language version plus separate support-surface versions

Context

Doctrine already has `contract_version` and `schema_version`, but they guard
different support surfaces. The new public version policy still needs one clear
main language contract.

Options

- Collapse every versioned surface into one universal version field.
- Keep separate support-surface versions and leave the public language version
  informal.
- Add one public Doctrine language version and keep the support-surface
  versions separate but explained together.

Decision

Plan around one public Doctrine language version plus separate
support-surface versions for narrower contracts.

Consequences

- Users get one main version story for language changes.
- `contract_version` and `schema_version` can keep their narrow compatibility
  role without pretending to version the whole language.
- The live docs must explain how the three version lines relate.

Follow-ups

- Decide where the public language version lives in shipped truth.
- Define the exact compatibility payload and migration wording shape.
- Audit docs and diagnostics so users can tell which surface changed.

## 2026-04-13 - Release tags should be annotated and aligned with the public version contract

Context

The user asked for an integrated git release and tagging approach. Doctrine has
no declared release-tag rule today.

Options

- Use lightweight tags or ad hoc git history as the release record.
- Use annotated stable tags only and skip prereleases for now.
- Use annotated stable tags plus optional annotated prerelease tags.

Decision

Plan around annotated stable release tags that match the public Doctrine
version contract. Allow optional annotated beta and rc tags if the release flow
needs early feedback.

Consequences

- Git tags, GitHub releases, and live docs can all point at the same public
  version story.
- Every tagged release must make a clear breaking or non-breaking call.
- Published stable tags should stay fixed once released.
- Release notes must carry the same compatibility payload as the docs.

Follow-ups

- Decide whether Doctrine wants prerelease tags now or later.
- Decide whether signed tags are a current requirement.
- Define the exact release-note template in `deep-dive`.

## 2026-04-13 - Canonical user-facing versioning owner is docs/VERSIONING.md

Context

Doctrine already has a syntax reference, design notes, emit docs, error docs,
and example docs. None of those files can cleanly own the full versioning and
upgrade contract without mixing roles.

Options

- Put the full policy into `docs/LANGUAGE_DESIGN_NOTES.md`.
- Put the full policy into `docs/LANGUAGE_REFERENCE.md`.
- Add one new live guide and link to it from the existing docs path.

Decision

Add `docs/VERSIONING.md` as the canonical user-facing owner for versioning,
breaking-change policy, and tagged release guidance.

Consequences

- The live docs path gets one clear policy owner.
- `README.md`, `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, and
  `docs/LANGUAGE_DESIGN_NOTES.md` must link to that guide instead of splitting
  the policy.
- The repo avoids mixing syntax reference, design guardrails, and release
  policy into one overloaded document.

Follow-ups

- Author `docs/VERSIONING.md`.
- Update the live docs index and repo entry docs to point at it.
- Keep other docs narrow and link out instead of copying policy text.

## 2026-04-13 - Public released Doctrine version lives in stable tags and releases, not in source syntax

Context

The repo has explicit support-surface versions today, but it has no authored
`language_version:` field and no code-owned public release-version constant.
The package metadata version is still `0.0.0`.

Options

- Add a new `language_version:` field to prompt source.
- Add a new code-owned public release-version constant.
- Use stable annotated tags and matching GitHub releases as the released
  version truth, while docs explain the policy.

Decision

The first rollout uses stable annotated tags and matching GitHub releases as
the canonical released Doctrine version. It does not add a new prompt field or
reuse package metadata as release truth.

Consequences

- The rollout avoids repo-wide source churn.
- Release truth stays aligned with what users actually install or read in a
  shipped release.
- `contract_version` and `schema_version` remain narrow support-surface
  versions instead of pretending to be the public release version.

Follow-ups

- Define the release-note header shape in the new versioning guide.
- Update contributor instructions so breaking releases and non-breaking
  releases are labeled the same way everywhere.
- Keep `pyproject.toml` out of the public versioning story.

## 2026-04-13 - First rollout uses stable-only annotated tags

Context

External research supports beta and rc tags, but the repo has no existing tag
or release process and the current ask is clarity first.

Options

- Standardize stable tags only for the first rollout.
- Standardize stable plus prerelease tags in the first rollout.
- Add signed prerelease and stable tags together.

Decision

The first rollout standardizes stable annotated `vX.Y.Z` tags only. Prerelease
tags and tag signing are deferred until the repo has a real need for them.

Consequences

- The first shipped policy is simpler to read and follow.
- The release-note template can lock in one stable shape before the repo adds
  beta or rc branches.
- Later prerelease or tag-signing work can extend the same contract without
  changing the core versioning model.

Follow-ups

- Define the stable release-note template in `docs/VERSIONING.md`.
- Add prerelease or signing guidance only if later release practice needs it.

## 2026-04-13 - Release setup and tagging must use one simple repo flow

Context

The repo has no release task surface today. The user wants both version setup
and tagged release work to stay simple for breaking and non-breaking releases.

Options

- Keep release setup fully manual across several docs and git commands.
- Add broad release automation and CI-driven publishing in the first rollout.
- Add one small repo-local prepare flow and one small tag flow on top of the
  existing `Makefile` command surface.

Decision

Add one canonical repo release flow through `Makefile` plus
`doctrine/release_flow.py`. The flow will expose `make release-prepare` for
setup and validation, and `make release-tag` for annotated tag creation.

Consequences

- One operator can prepare and tag a release without memorizing the rules.
- Version-class and bump rules become executable, not just documented.
- The first rollout still avoids broad release automation or CI complexity.

Follow-ups

- Define the exact helper inputs and output worksheet in `phase-plan`.
- Add narrow helper tests for version-class and bump validation.
- Keep the helper small enough that the docs still stay readable on their own.

## 2026-04-13 - Doctrine language version and Doctrine release version are separate lines

Context

The plan originally converged on one top-line public version plus
support-surface versions. That was still too blurry. The user wants a hard
split between the Doctrine language version and Doctrine release versions so a
release can ship without changing the language version at all.

Options

- Keep one public version line and explain the distinction only in prose.
- Use a release version plus a separate language version with hard owner
  boundaries.
- Add a language version to prompt source and make releases infer it from
  compiled artifacts.

Decision

Doctrine will use two first-class public version lines:

- Doctrine release version: the stable annotated tag and matching GitHub
  release for one shipped release.
- Doctrine language version: the grammar, semantics, and authored language
  behavior described in `docs/VERSIONING.md`.

Each tagged release must say whether the language version changed or stayed the
same. Releases may ship with an unchanged language version.

Consequences

- `docs/VERSIONING.md` owns the current language version and the rules for
  bumping it.
- Stable annotated tags and matching GitHub releases own the current release
  version.
- Release notes must show both lines, not just one overloaded `version`.
- The repo operator flow must use `RELEASE=` and `LANGUAGE_VERSION=` so the
  inputs are hard to confuse.
- `contract_version` and `schema_version` stay separate from both public
  version lines.

Follow-ups

- Make the release-note header show both version lines.
- Make the release helper validate both release bumps and language-version
  moves.
- Keep releases with unchanged language versions explicit in docs and notes.

## 2026-04-13 - Expand the plan to the full repo release process

Context

The user widened the ask from versioning policy plus basic tagging to the full
release process, including changelog, prereleases, signed tags, GitHub draft
and publish flow, and bad-release correction rules.

Options

- Keep the earlier narrow plan that only covers version rules plus stable
  tagging.
- Expand the plan to the full repo-owned release process and keep external
  registry publishing out of scope.
- Expand straight to CI autopublish and external package-registry automation.

Decision

Expand this plan to the full repo-owned release process. The first rollout will
cover:

- `docs/VERSIONING.md` as the policy owner
- `CHANGELOG.md` as the portable release-history owner
- signed annotated beta, rc, and stable public tags
- GitHub draft, prerelease, and stable release publication through one repo
  flow
- `.github/release.yml` for generated-note categories and excludes
- explicit fix-forward and yank or supersede rules for bad public releases

This supersedes the earlier stable-only and sign-later deferrals in the plan.
It still keeps external registry publication and CI autopublish out of scope
for v1.

Consequences

- The plan now needs `release-draft` and `release-publish` work, not just
  `release-prepare` and `release-tag`.
- `CHANGELOG.md` becomes a new shipped truth surface.
- Signed-tag preflight and GitHub CLI preflight become part of the operator
  path.
- A later consistency pass must re-check the whole artifact before
  implementation because the release surface is materially larger now.

Follow-ups

- Rework target architecture, call-site audit, phase plan, verification, and
  ops around the full release path.
- Keep the correction path explicit: no stable tag moves, no silent asset
  replacement, fix forward instead.
- Keep generated notes as helper output, not the only release history.

## 2026-04-13 - Keep release-process proof targeted to release surfaces

Context

The plan now covers the full repo release process, but it still does not change
the shipped language, manifest behavior, emitted contract payloads, or
diagnostics behavior. The proof bar should match the touched surfaces.

Options

- Run full corpus and diagnostics verification as a default baseline.
- Use targeted release-helper tests plus dry-run and cold-read proof for the
  release surfaces this plan changes.
- Add new doc-policing gates as proof for release-process consistency.

Decision

Use targeted release-helper tests, one local dry run against a temp git repo or
mocked GitHub boundary, and cold-read review of generated release artifacts. Do
not add doc-policing gates. Do not run `make verify-examples` or
`make verify-diagnostics` unless implementation expands into those surfaces and
the plan is reopened.

Consequences

- Proof stays aligned with the actual change surface.
- The repo avoids slow or low-value verification that does not test the new
  release flow.
- If implementation widens into language, manifest, emit, or diagnostics
  behavior, the plan and proof bar must widen with it.

## 2026-04-13 - First explicit Doctrine language version starts at 1.0

Context

The plan required `docs/VERSIONING.md` to own one current Doctrine language
version, but the reactivated plan did not pin the first public value.

Options

- Keep the current language version implicit until the first public tag.
- Start the first explicit public Doctrine language version at `0.1`.
- Start the first explicit public Doctrine language version at `1.0`.

Decision

Start the first explicit public Doctrine language version at `1.0`.

Consequences

- `docs/VERSIONING.md` can now carry one parseable current language-version
  line that the release helper can validate against.
- Releases can say `unchanged (still 1.0)` until the language actually moves.
- The public language contract now starts at a stable-looking first value even
  though no public release tag exists yet.

## 2026-04-13 - Breaking non-language releases may still publish on stable

Context

The approved plan already allowed `make release-prepare` to accept
`CHANNEL=stable|beta|rc` with `LANGUAGE_VERSION=unchanged`, but one operator
table row still limited breaking non-language releases to beta or rc only.

Options

- Keep the stricter beta or rc-only row.
- Let breaking non-language releases use the same stable, beta, or rc channel
  set as the rest of the plan already described.

Decision

Let breaking non-language releases use `stable`, `beta`, or `rc` while still
keeping the Doctrine language version unchanged when the language did not
change.

Consequences

- The operator table now matches the broader target architecture and helper
  contract.
- Stable public releases can carry a breaking non-language change without a
  fake language-version bump.
