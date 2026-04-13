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
  - doctrine/verify_corpus.py
---

# TL;DR

Outcome

Doctrine will ship one clear versioning and breaking-change policy with hard
boundaries between the Doctrine language version, Doctrine release versions,
and narrow support-surface versions. A user should be able to see what
changed, whether a release changed the language or not, whether the release is
breaking or non-breaking for them, which version line moved, and the exact
upgrade steps without reading git history or guessing from scattered docs.

Problem

Doctrine already versions some machine-readable artifacts and keeps stable
compiler error codes, but it does not yet publish one canonical language
version contract, one separate release-version contract, or one required
breaking-change workflow across code, docs, examples, diagnostics, tagged
releases, and contributor instructions.

Approach

Design one canonical versioning model with two first-class lines: a Doctrine
language version for grammar and semantics, and Doctrine release versions for
tagged shipments. Keep breaking-change classification tied to real
client-visible behavior, pair each release with annotated tags and plain-
language notes, add human-readable upgrade guidance plus fail-loud diagnostics,
and wire the same rules into live docs, proof examples, and `AGENTS.md`.

Plan

Confirm the North Star, research strong language-versioning practice, map
Doctrine's current versioned surfaces and real break points, choose the
canonical language-version owner, release-version owner, and migration model,
then integrate it into code, docs, examples, diagnostics, release notes, and
contributor guidance.

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
- Broad release automation or packaging work beyond one small repo-local
  release helper.
- Inventing multiple user-facing version numbers for the same surface without a
  clear need.
- Calling a docs cleanup alone "versioning support" without a real shipped
  contract.

## 0.4 Definition of done (acceptance evidence)

- Doctrine's live docs explain the canonical versioning model in plain English.
- A user can tell, from one canonical surface, whether a change is breaking for
  their usage and what to do next.
- A user can inspect a tagged release and tell whether it is breaking or
  non-breaking for their usage, and whether the language version changed.
- One operator can prepare and tag either a breaking or non-breaking release by
  following one short canonical flow.
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
  corpus through `examples/94_route_choice_guard_narrowing` as proof.
- The live docs path is `README.md`, `docs/README.md`,
  `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_DESIGN_NOTES.md`,
  `docs/COMPILER_ERRORS.md`, and `examples/README.md`.
- `doctrine/emit_contract.py` already versions emitted machine-readable
  contracts with `contract_version = 1`.
- `doctrine.verify_corpus` already enforces `schema_version = 1` for example
  manifests.
- `docs/COMPILER_ERRORS.md` already promises stable error identities and human
  wording.
- Root `AGENTS.md` already requires fail-loud behavior, proof, and doc
  alignment, but it does not yet define a breaking-change workflow.

## 2.2 What's broken / missing (concrete)

- There is no canonical Doctrine language version that a user can point to.
- There is no clear boundary between the Doctrine language version, Doctrine
  release versions, and support-surface versioning such as manifest schema or
  emitted contract versions.
- There is no repo-wide rule for deciding whether a change is breaking,
  additive, or internal-only.
- There is no required migration note or upgrade recipe when syntax,
  semantics, docs, or diagnostics change in a user-visible way.
- There is no one place a user can check to answer, "Do I need to act, and if
  so, how?"
- There is no clear git tag or release-note convention that mirrors the same
  version and upgrade contract.
- There is no simple repo task surface for preparing a version change and
  creating a tagged release.
- There is no `AGENTS.md` rule that says a breaking change must update docs,
  examples, and upgrade guidance in the same change.

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
  - [doctrine/verify_corpus.py](../doctrine/verify_corpus.py) — current
    manifest schema owner with `schema_version = 1` as a hard gate.
  - [doctrine/diagnostics.py](../doctrine/diagnostics.py) — canonical error
    formatting and JSON-safe diagnostic payload shape.
- Canonical path / owner to reuse:
  - `docs/VERSIONING.md` — chosen canonical owner path for the final
    user-facing versioning and upgrade policy. It does not exist yet, which is
    why current truth is still split.
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
  - Version-related truth is split today across
    [docs/LANGUAGE_DESIGN_NOTES.md](LANGUAGE_DESIGN_NOTES.md),
    [docs/LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md),
    [docs/COMPILER_ERRORS.md](COMPILER_ERRORS.md),
    [docs/EMIT_GUIDE.md](EMIT_GUIDE.md),
    [doctrine/emit_contract.py](../doctrine/emit_contract.py),
    [doctrine/verify_corpus.py](../doctrine/verify_corpus.py),
    [README.md](../README.md), [docs/README.md](README.md), and
    [AGENTS.md](../AGENTS.md).
  - There is no repo-owned release operator surface yet in `Makefile`, and no
    current path that ties tagged releases, release notes, and version policy
    together.
  - [pyproject.toml](../pyproject.toml) and
    [doctrine/diagnostic_smoke.py](../doctrine/diagnostic_smoke.py) both carry
    `version = "0.0.0"` package or test metadata that should not be confused
    with a public Doctrine language version.
- Capability-first opportunities before new tooling:
  - Reuse the live docs path and existing fail-loud diagnostics before adding
    broad release automation or migration tooling.
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

No plan-shaping blockers remain after this deep-dive pass. The architecture now
makes these calls:

- `docs/VERSIONING.md` will be the canonical user-facing owner for the policy,
  with [docs/README.md](README.md) and [README.md](../README.md) linking to it.
- `docs/VERSIONING.md` will also own the current Doctrine language version and
  the hard boundary between language version, release version, and
  support-surface versions.
- The current released Doctrine version will live in the latest stable
  annotated git tag and matching GitHub release, not in prompt syntax or in
  `pyproject.toml`.
- Every tagged release will state the shipped language version and whether that
  language version changed in that release.
- Doctrine will not add a new `language_version:` prompt field or a new
  code-owned public language-version constant in the first rollout.
- Every breaking change will ship one fixed compatibility payload across docs,
  release notes, and contributor guidance.
- Diagnostics will keep failing on the real break point. The first rollout
  will not add a generic language-version mismatch diagnostic because there is
  no authored language-version field today.
- The first rollout will standardize stable annotated tags only. Prerelease
  tags and signed tags are explicit follow-up hardening, not blockers.
- The repo will expose one canonical operator flow for release setup and tag
  creation through `Makefile` plus `doctrine/release_flow.py`.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:external_research:start -->
# External Research (best-in-class references; plan-adjacent)

> Goal: anchor the plan in idiomatic, broadly accepted practices where
> applicable. This section intentionally avoids project-specific internals.

## Topics researched (and why)

- Public language versioning and compatibility boundaries — Doctrine needs one
  clear versioning story that does not force churn for internal-only work.
- Deprecation and incompatible-change policy — the plan needs a clear rule for
  when to warn, when to break, and what migration data must ship.
- Separate stability lines for support artifacts — Doctrine already has
  `contract_version` and `schema_version`, so the plan needs a clean way to
  explain them without mixing them into the public language version.
- Release staging and upgrade ergonomics — the plan needs a simple rule for
  prereleases, stable releases, and exact upgrade steps.
- Git tagging and release surfaces — the user asked for an integrated git
  release and tagging approach, so the public version contract must line up
  with tags and GitHub releases.

## Findings + how we apply them

### Public language versioning and compatibility boundaries

- Best practices (synthesized):
  - A public version line only works if the public contract is explicit.
  - Release cadence and language compatibility should not be silently mixed.
  - Major versions signal incompatible public changes.
  - Minor versions cover backward-compatible additions.
  - Patch versions fit release-level fixes better than language-level meaning.
- Adopt for this plan:
  - Use one SemVer-like Doctrine release version for tagged releases.
  - Use one separate Doctrine language version for grammar, semantics, and
    authored language behavior.
  - Let releases ship with an unchanged language version when the language did
    not change.
  - Treat release major bumps as any shipped public surface that now requires
    client action, while release notes name the exact affected surface.
  - Treat language major bumps as breaking language changes and language minor
    bumps as backward-compatible language additions.
- Reject for this plan:
  - Do not reuse package metadata like `0.0.0` as either the Doctrine release
    version or the Doctrine language version.
  - Do not use the release version as a proxy for the language version.
  - Do not bump the language version for internal-only or non-language
    releases.
- Pitfalls / footguns:
  - One version number becomes noise if it tries to cover release cadence,
    language compatibility, and support artifacts at the same time.
- Sources:
  - Semantic Versioning 2.0.0 — https://semver.org/spec/v2.0.0.html — official
    versioning spec
  - Go 1 compatibility promise — https://go.dev/doc/go1compat — official
    compatibility policy from the Go team

### Deprecation and incompatible-change policy

- Best practices (synthesized):
  - Incompatible changes should be easy to resolve.
  - Breaking proposals should carry an explicit compatibility section.
  - Deprecate before removal when that delay is honest and safe.
  - Tools or diagnostics should point at breakage when possible.
- Adopt for this plan:
  - Require one compatibility payload for every breaking change:
    - affected surface
    - old behavior
    - new behavior
    - first affected version
    - exact upgrade steps
    - before/after example
    - verification step
  - Use soft deprecation when a change can wait without hiding the future
    removal.
  - Point users at the exact breakage in diagnostics or docs when possible.
- Reject for this plan:
  - No vague "might break" notes.
  - No diff-only release notes for breaking changes.
- Pitfalls / footguns:
  - A deprecation without a date, version, or upgrade step still leaves users
    guessing.
- Sources:
  - PEP 387 — https://peps.python.org/pep-0387/ — official Python backwards
    compatibility policy
  - PEP 3002 — https://peps.python.org/pep-3002/ — official Python process for
    backwards-incompatible changes
  - TypeScript 4.2 release notes —
    https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-2.html
    — official example of explaining breaking-but-manageable changes

### Separate stability lines for support artifacts

- Best practices (synthesized):
  - Separate stability labels help users tell the public contract from narrower
    support surfaces.
  - Different surfaces can keep their own version line when they guard
    different contracts.
- Adopt for this plan:
  - Keep `contract_version` and `schema_version` separate from both the
    Doctrine language version and Doctrine release versions.
  - Explain all four lines in one live policy so users can see how they
    relate.
  - Treat the Doctrine language version as the language contract, the Doctrine
    release version as the shipment identifier, and the support-surface
    versions as narrow compatibility lines.
- Reject for this plan:
  - Do not collapse every surface into one universal version field.
  - Do not add Rust-style editions to Doctrine right now.
- Pitfalls / footguns:
  - If the docs do not say which surface changed, users will still be confused
    even with good version numbers.
- Sources:
  - PEP 689 — https://peps.python.org/pep-0689/ — official guidance on marking
    stability levels
  - Rust Edition Guide —
    https://doc.rust-lang.org/stable/edition-guide/editions/transitioning-an-existing-project-to-a-new-edition.html
    — official migration guidance and a good contrast point

### Release staging and upgrade ergonomics

- Best practices (synthesized):
  - Prereleases are the right place to front-load likely breaking changes.
  - Stable release notes should say who is affected, what changed, and how to
    fix it.
  - Upgrade steps should be ordered and easy to verify.
- Adopt for this plan:
  - If Doctrine uses prereleases, use annotated tags like `vX.Y.Z-beta.N` and
    `vX.Y.Z-rc.N`.
  - Keep release candidates mostly to bug fixes and wording cleanup after
    beta.
  - Require ordered upgrade notes for every breaking change.
  - Require every release note to state the shipped language version and
    whether it changed in that release.
- Reject for this plan:
  - Do not ship large stable releases with unannounced breaking changes.
- Pitfalls / footguns:
  - A release note that says only "breaking change" still fails the user.
- Sources:
  - TypeScript's release process —
    https://github.com/microsoft/TypeScript/wiki/TypeScript%27s-Release-Process
    — official maintainer release staging guidance
  - Rust Edition Guide —
    https://doc.rust-lang.org/stable/edition-guide/editions/transitioning-an-existing-project-to-a-new-edition.html
    — official example of step-ordered migration guidance

### Git tagging and release surfaces

- Best practices (synthesized):
  - Annotated tags are the right release tags.
  - Lightweight tags are not the durable public release surface.
  - A release surface should make it easy to tell whether a release is
    breaking or non-breaking.
  - GitHub releases sit on top of git tags and can mark prereleases and
    compare against earlier tags.
  - Published release points should not be silently moved.
- Adopt for this plan:
  - Publish stable Doctrine releases from annotated `vX.Y.Z` tags.
  - Require each tagged release and release note to say whether it is
    breaking or non-breaking for the public language contract.
  - Require each tagged release and release note to say whether the Doctrine
    language version changed or stayed the same.
  - Publish GitHub releases from those tags with plain-language notes that use
    the same compatibility payload as the docs.
  - If prereleases are used, publish annotated prerelease tags and mark the
    GitHub releases as prereleases too.
- Reject for this plan:
  - Do not use lightweight tags for public Doctrine releases.
  - Do not move a published stable release tag to a different commit.
- Pitfalls / footguns:
  - Tags without matching notes still leave users guessing what changed.
- Sources:
  - `git-tag` documentation — https://git-scm.com/docs/git-tag.html — official
    Git reference for annotated versus lightweight tags
  - GitHub About Releases —
    https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
    — official release model on top of tags
  - GitHub Managing Releases —
    https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
    — official guidance for prereleases and tag comparison

## Adopt / Reject summary

- Adopt:
  - one SemVer-like Doctrine release version
  - one separate Doctrine language version
  - one required compatibility payload for every breaking change
  - separate support-surface versions for `contract_version` and
    `schema_version`
  - annotated stable release tags in the first rollout, with beta and rc tags
    reserved as a later extension only if the repo needs prereleases
  - GitHub releases and release notes that reuse the same plain-language
    migration story as the docs
- Reject:
  - package-version metadata as the public release version or language version
  - using the release version as a proxy for the language version
  - one universal version field for unrelated support surfaces
  - Rust-style editions for Doctrine right now
  - lightweight public release tags
  - moving published stable release tags

## Decision gaps that must be resolved before implementation

No plan-shaping blockers remain after deep-dive. The design now makes these
calls:

- `docs/VERSIONING.md` is the canonical user-facing policy owner.
- Stable annotated tags and matching GitHub releases own the current released
  Doctrine version.
- `docs/VERSIONING.md` owns the current Doctrine language version.
- Tagged releases must always say whether they changed the language version or
  shipped the same language version again.
- The first rollout does not add a new prompt-level `language_version:` field
  or a new code-owned public language-version constant.
- The first rollout standardizes stable tags only. Prerelease tags and tag
  signing are follow-up hardening work.
<!-- arch_skill:block:external_research:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `README.md` is the repo entry story. It explains what Doctrine is and how to
  run it, but it does not define a versioning contract.
- `docs/README.md` is the live docs index. It points at the shipped docs, but
  it does not include a versioning guide.
- `docs/LANGUAGE_REFERENCE.md` owns the shipped syntax and behavior overview.
- `docs/LANGUAGE_DESIGN_NOTES.md` owns durable guardrails and non-goals.
- `docs/COMPILER_ERRORS.md` owns stable error-code meanings and formatter
  order.
- `docs/EMIT_GUIDE.md` explains emitted Markdown and the companion contract.
- `examples/README.md` explains the numbered corpus and manifest-backed proof.
- `doctrine/emit_contract.py` owns the machine-readable companion contract and
  its `COMPILED_AGENT_CONTRACT_VERSION = 1` constant.
- `doctrine/verify_corpus.py` owns manifest loading and the hard
  `schema_version = 1` gate for `cases.toml`.
- `pyproject.toml` still has `version = "0.0.0"` as Python package metadata
  only.
- The repo has no `docs/VERSIONING.md`, no changelog, no `.changeset/`, no
  `.github/` release workflow, and no git tags today.
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
5. There is no release path in the repo that maps a stable tag, release note,
   current release version, and current language version together.

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
  - the boundary between those two lines
  - change classification
  - breaking versus non-breaking tagged releases
  - required upgrade payload
- There is also no authored `language_version:` field in prompt source and no
  code-owned public language-version constant.

## 4.4 Observability + failure behavior today

- Parse, compile, and emit failures are already fail-loud.
- Manifest schema mismatches already fail loud with
  `Expected schema_version = 1`.
- `tests/test_emit_docs.py` locks the emitted companion-contract payload shape.
- `make verify-examples`, `make verify-diagnostics`, and `make tests` are the
  existing preservation signals for this area.
- There is no version-aware upgrade hint, release-note template, or tagged
  release classification anywhere in the shipped repo truth.
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

- Add one new live guide: `docs/VERSIONING.md`.
- `docs/VERSIONING.md` becomes the canonical user-facing owner for:
  - current Doctrine language version
  - language-version rules
  - release-version rules
  - change-class rules
  - breaking-change payload rules
  - tagged release note shape
  - the hard boundary between the Doctrine language version, Doctrine release
    versions, and support-surface versions
- `docs/README.md` and `README.md` link to `docs/VERSIONING.md` as the entry
  point for versioning and upgrades.
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
- `Makefile` becomes the human operator entry surface for release work with two
  narrow commands:
  - `make release-prepare RELEASE=vX.Y.Z CLASS=internal|additive|soft-deprecated|breaking LANGUAGE_VERSION=unchanged|X.Y`
  - `make release-tag RELEASE=vX.Y.Z`
- `doctrine/release_flow.py` owns the validation and formatted output behind
  those Make targets.
- Stable annotated git tags and matching GitHub releases become the canonical
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
3. The canonical release setup flow starts with:
   `make release-prepare RELEASE=vX.Y.Z CLASS=internal|additive|soft-deprecated|breaking LANGUAGE_VERSION=unchanged|X.Y`
4. `release-prepare` reads the latest stable annotated tag and the current
   language version from `docs/VERSIONING.md`, validates that the requested
   release bump and language-version move match the chosen class, and fails
   loud on mismatch.
5. `release-prepare` prints one fixed release worksheet:
   - derived release kind: breaking or non-breaking
   - previous stable tag
   - previous language version
   - requested release version
   - requested language version state
   - required docs and proof surfaces to update
   - exact release-note header
   - exact verify commands to run
   - exact annotated tag command to run next
6. Every tagged release must carry one explicit top-line call:
   `Release kind: Breaking` or `Release kind: Non-breaking`.
7. Every tagged release must also say:
   - release version
   - language version
   - affected surfaces
   - who must act
   - who does not need to act
   - exact upgrade steps
   - verification step
   - support-surface version changes, if any
8. After the docs and proof work is complete, the canonical tag flow is:
   `make release-tag RELEASE=vX.Y.Z`
9. `release-tag` creates one annotated stable `vX.Y.Z` tag with the canonical
   tag message and fails loud if the tag already exists or the release format
   is invalid.
10. Stable releases publish from annotated `vX.Y.Z` tags and matching GitHub
   releases. The first rollout standardizes stable tags only.
11. If a release changes the Doctrine language version, the same change must
    update:
   - `docs/VERSIONING.md`
   - the affected live docs
   - release notes
   - examples or verification only when shipped language behavior or proof
     contracts actually changed
12. If a change is breaking outside the language surface, the same change must
    still update:
   - `docs/VERSIONING.md`
   - the affected live docs
   - contributor instructions in `AGENTS.md`
   - release notes
   - examples or verification only when shipped behavior or proof contracts
     actually changed
13. Diagnostics keep failing at the real break point. The first rollout does
   not add a generic language-version mismatch error because there is no
   authored language version to compare against.

## 5.3 Object model + abstractions (future)

Doctrine will carry a separate Doctrine release version, a separate Doctrine
language version, and narrow support-surface versions.

| Surface | Canonical owner | Meaning | Bump rule |
| --- | --- | --- | --- |
| Doctrine release version | Stable annotated git tag + matching GitHub release | The identifier for one shipped Doctrine release | Changes on every tagged release: major when any shipped public surface needs client action; minor for backward-compatible public additions or soft deprecations; patch for internal-only or other non-breaking fixes |
| Doctrine language version | `docs/VERSIONING.md`, restated in each tagged release | The grammar, semantics, and authored language behavior that release ships | Changes only when the language surface changes: major for breaking language changes; minor for backward-compatible language additions; unchanged for releases that do not change the language |
| Emitted companion contract | `doctrine/emit_contract.py` | The machine-readable JSON contract for emitted agent metadata | Bump `contract_version` only when that JSON contract becomes incompatible |
| Corpus manifest schema | `doctrine/verify_corpus.py` plus `examples/*/cases.toml` | The manifest shape required by corpus verification | Bump `schema_version` only when the manifest contract becomes incompatible |

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
- `Release version: vX.Y.Z`
- `Language version: unchanged (still X.Y)` or `Language version: X.Y -> Z.W`
- `Affected surfaces: ...`
- `Who must act: ...`
- `Who does not need to act: ...`
- `Upgrade steps: ...`
- `Verification: ...`
- `Support-surface version changes: ...`

This is the operator rule that keeps the flow simple:

| Operator input | Derived release kind | Allowed release-version move | Allowed language-version move |
| --- | --- | --- | --- |
| `CLASS=internal LANGUAGE_VERSION=unchanged` | Non-breaking | Patch only | Unchanged only |
| `CLASS=additive LANGUAGE_VERSION=unchanged` | Non-breaking | Minor only | Unchanged when the release adds no language feature |
| `CLASS=additive LANGUAGE_VERSION=<next minor>` | Non-breaking | Minor only | Minor only when the release adds language syntax or semantics |
| `CLASS=soft-deprecated LANGUAGE_VERSION=unchanged` | Non-breaking | Minor only | Unchanged only |
| `CLASS=breaking LANGUAGE_VERSION=unchanged` | Breaking | Major only | Unchanged when the break is outside the language surface |
| `CLASS=breaking LANGUAGE_VERSION=<next major>` | Breaking | Major only | Major only when the language surface itself broke |

## 5.4 Invariants and boundaries

- `docs/VERSIONING.md` is the one live policy owner for current language
  version, language-version rules, and upgrade rules.
- `Makefile` is the one repo operator entry surface for preparing and tagging a
  release.
- The latest stable annotated tag and matching GitHub release are the one
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
- Every tagged release must say clearly whether it is breaking or
  non-breaking.
- `release-prepare` and `release-tag` are the only supported repo release task
  surfaces in the first rollout.
- Breaking notes must name affected and unaffected users, not just changed
  files.
- Do not create a second live release-notes path under `docs/`. Dated release
  notes belong on GitHub releases. Evergreen rules belong in
  `docs/VERSIONING.md`.
- Prerelease tags and signed tags are not part of the first rollout.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not UI work.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Canonical versioning guide | `docs/VERSIONING.md` | new live doc | No user-facing versioning owner exists | Add one canonical guide for language-version rules, release-version rules, hard boundaries, compatibility payload, and release-note shape | Users need one place to learn the policy | New live docs SSOT for versioning and upgrades | Docs-only |
| Release operator flow | `Makefile`, `doctrine/release_flow.py`, `tests/test_release_flow.py` | No release task surface exists today | Add `make release-prepare RELEASE=... CLASS=... LANGUAGE_VERSION=...` and `make release-tag RELEASE=...` with one small validating helper | The user wants version changes and tagged releases to stay simple and repeatable | Canonical repo operator flow for release setup and tagging | `tests/test_release_flow.py` plus any docs checks this helper depends on |
| Docs index | `docs/README.md` | live docs index | No versioning entry point | Add `docs/VERSIONING.md` near the top of the live path | Users start here for docs navigation | Live docs path now includes versioning guide | Docs-only |
| Repo entry docs | `README.md` | top-level project story | No upgrade or release policy entry point | Add a short pointer to the versioning guide and tagged release model | Users often start here first | README points to canonical versioning owner | Docs-only |
| Language docs | `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_DESIGN_NOTES.md` | syntax reference and guardrails | These docs could drift into mixed policy ownership | Keep their narrow roles and link out to `docs/VERSIONING.md` for compatibility policy | Prevent split truth across docs | Syntax and design docs stay narrow | Docs-only |
| Diagnostics contract | `docs/COMPILER_ERRORS.md`, `doctrine/diagnostics.py` | stable error codes and formatting | Stable error-code meaning exists, but no upgrade-policy bridge | Keep stable code meanings; add versioning-guide pointer only where breaking guidance is useful; do not add generic version mismatch code in v1 | Breaking changes should be explained at the real failure point without noisy new machinery | Diagnostics keep current contract; guidance link is additive only | `make verify-diagnostics` only if diagnostics change |
| Emitted contract surface | `doctrine/emit_contract.py`, `docs/EMIT_GUIDE.md`, `tests/test_emit_docs.py` | `COMPILED_AGENT_CONTRACT_VERSION`, contract docs | Contract version is real but isolated | Keep `contract_version` separate; document what it covers and when it bumps | Contract consumers need a narrow compatibility story | Companion-contract version stays a surface-local contract | `tests/test_emit_docs.py` if payload or wording changes in code |
| Corpus manifest surface | `doctrine/verify_corpus.py`, `examples/README.md`, `examples/*/cases.toml` | `schema_version` gate and manifest docs | Manifest schema version is real but isolated | Keep `schema_version` separate; document what it covers and when it bumps | Manifest authors need a narrow compatibility story | Manifest schema version stays a surface-local contract | `make verify-examples` if manifest behavior or examples change |
| Contributor workflow | `AGENTS.md` | build, verify, definition of done | No explicit breaking-change workflow | Add required release classification, compatibility payload, doc update, and proof obligations | Contributors must follow the same policy users read | Contributor contract now includes breaking-change duties | Docs-only |
| Release surface | git tags, GitHub releases | stable release point | No declared release convention | Standardize stable annotated `vX.Y.Z` tags and one fixed release-note header that always states the shipped language version | Git and GitHub must tell the same story as the docs | Stable tags + GitHub releases become release SSOT | Docs-only |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  `docs/VERSIONING.md` is the user-facing owner for the current language
  version and versioning policy. Stable annotated tags and matching GitHub
  releases own the current release version. Narrow support-surface versions
  stay owned by `doctrine/emit_contract.py` and `doctrine/verify_corpus.py`.
- Deprecated APIs (if any):
  None in the first rollout. This plan adds policy and contributor rules, not a
  new runtime API.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  Do not create `docs/releases/`, a second versioning guide, a new public
  language-version constant in code, a new `language_version:` prompt field
  for v1, or a second release helper path outside `Makefile` plus the one
  helper module. Rewrite versioning mentions in place on the surviving live
  docs path.
- Capability-replacing harnesses to delete or justify:
  None beyond the one narrow release helper. This rollout still does not need
  broad release automation, parsers, or wrappers.
- Live docs/comments/instructions to update or delete:
  `README.md`, `Makefile`, `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md`,
  `docs/EMIT_GUIDE.md`, `examples/README.md`, `AGENTS.md`,
  `doctrine/release_flow.py`, and `tests/test_release_flow.py`. Add short
  boundary comments in `doctrine/emit_contract.py` or
  `doctrine/verify_corpus.py` only if the implementation touches those files.
- Behavior-preservation signals for refactors:
  `make verify-examples`, `make verify-diagnostics` if diagnostics move,
  `tests/test_emit_docs.py` if the companion contract changes, helper tests for
  release validation behavior, and manual cold read of the new docs plus
  release-note template.
- Breaking changes must say exactly who is affected and who is not affected.
- Tagged releases must say clearly whether they are breaking or non-breaking.
- Tagged releases must say clearly whether the language version changed or
  stayed the same.
- Release notes must use the same compatibility payload and version names as
  the live docs.
- Stable release tags should identify one immutable public release point.
- The canonical release flow must stay short enough that one operator can run
  it without reading several docs.
- No compatibility shim should become the default answer to a breaking change.

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| --- | --- | --- | --- | --- |
| Docs index | `docs/README.md` | Link to one canonical versioning guide | Stops users from hunting across docs | Include |
| Operator tasks | `Makefile`, `doctrine/release_flow.py` | One canonical release setup and tag flow | Stops release drift and hand-written one-off steps | Include |
| Repo entry docs | `README.md` | Point to versioning and tagged release policy | Stops a split between repo entry docs and live docs | Include |
| Syntax docs | `docs/LANGUAGE_REFERENCE.md` | Link out for compatibility policy instead of owning it | Keeps syntax reference from becoming a release guide | Include |
| Design guardrails | `docs/LANGUAGE_DESIGN_NOTES.md` | Link out for release policy instead of owning it | Keeps design notes narrow and stable | Include |
| Emit docs | `docs/EMIT_GUIDE.md` | Explain `contract_version` as a narrow version line | Prevents users from treating it as the language version or release version | Include |
| Corpus docs | `examples/README.md` | Explain `schema_version` as a narrow version line | Prevents users from treating it as the language version or release version | Include |
| Error docs | `docs/COMPILER_ERRORS.md` | Keep stable error meanings and point to versioning guide when useful | Aligns failure guidance with release policy | Include |
| Support-surface code | `doctrine/emit_contract.py`, `doctrine/verify_corpus.py` | Keep narrow version owners where they already live | Preserves code-owned surface boundaries | Include |
| Package metadata | `pyproject.toml` | Keep package version separate from language and release versions | Prevents false SSOT | Exclude |
| Prompt syntax | grammar, parser, compiler | Do not add `language_version:` in v1 | Prevents repo-wide churn and a second version source | Exclude |
| Broad release automation | CI, GitHub workflow, packaging pipeline | Do not automate the whole release system in v1 | Keep the solution small and easy to trust | Exclude |
| Prerelease flow | git tags, GitHub releases | Add beta or rc tags later only if needed | Keeps v1 simple and readable | Defer |
| Signed tags | git tags | Add signing only as later hardening | Not needed to make the policy clear | Defer |
<!-- arch_skill:block:call_site_audit:end -->

# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

This section will be authored by `phase-plan` after `research` and
`deep-dive`. The expected foundational slices are:

- external-research-backed version and compatibility policy
- hard boundary between Doctrine language version and Doctrine release version
- release-tag and release-note policy that states both version lines clearly
- one simple repo operator flow for preparing and tagging releases
- internal surface inventory and owner-path convergence
- code and diagnostics integration
- live docs, examples, and `AGENTS.md` follow-through

# 8) Verification Strategy (common-sense; non-blocking)

Avoid verification bureaucracy. Prefer the smallest existing signal. Default to
1-3 checks per meaningful phase. Keep manual cold-read review for finalization
unless a code change needs stronger proof.

## 8.1 Unit tests (contracts)

- Add targeted unit coverage only if new version-classification or metadata
  logic lands in code.
- Add targeted helper tests for release-class and version-bump validation if the
  repo gains the release helper.
- If diagnostics change, run `make verify-diagnostics`.

## 8.2 Integration tests (flows)

- Run `make verify-examples` when the shipped language or example-backed proof
  changes.
- If a new versioning example ships, also run the targeted manifest-backed
  verification for that example.
- If emitted contract surfaces change, use the smallest stable emit-level proof
  that shows the new contract clearly.
- If the release helper lands, run its narrow test coverage and cold-read one
  generated release worksheet for both a breaking and non-breaking example,
  including one case where the language version stays unchanged.

## 8.3 E2E / device tests (realistic)

Not device work. The realistic end-to-end check here is a cold read of the live
docs, release notes, plus any version-aware diagnostics or emitted metadata to
confirm a user can tell what changed, which version line moved, and what to do
next.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

Roll this out through the live docs set, not through dated notes. The policy
should ship before or with the first breaking change that claims to use it. If
Doctrine adopts prereleases, breaking changes should show up there first with
the same compatibility payload that will later ship in the stable release.
Stable releases should publish from annotated tags with plain-language notes
and an explicit upgrade path. Every stable release should also say whether the
language version changed or stayed the same.

## 9.2 Telemetry changes

No product telemetry is assumed. The likely operational signal is better docs,
clearer diagnostics, and fewer user questions about whether a change applies to
them.

## 9.3 Operational runbook

- Update the live docs index when the versioning guide becomes real.
- Keep `AGENTS.md` aligned with the shipped policy.
- If a breaking change lands, update the right version truth in the same
  change:
  - language version in `docs/VERSIONING.md` when the language changed
  - release version in the tag and release notes
  - upgrade guidance and proof surfaces where they changed
- Use the canonical repo release flow to prepare the release and create the
  annotated tag.
- Publish stable releases from annotated tags and matching plain-language
  release notes that also state the shipped language version.
- Keep old plans out of the live docs path once their durable truth lands.

# 10) Decision Log (append-only)

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
