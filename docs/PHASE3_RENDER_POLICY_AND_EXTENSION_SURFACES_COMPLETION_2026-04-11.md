---
title: "Doctrine - Phase 3 Render Policy And Extension Surfaces Completion - Architecture Plan"
date: 2026-04-11
status: active
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: parity_plan
related:
  - docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md
  - docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md
  - docs/READABLE_MARKDOWN_SPEC.md
  - docs/LANGUAGE_MECHANICS_SPEC.md
  - docs/SECOND_WAVE_LANGUAGE_NOTES.md
  - docs/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md
  - docs/DOCTRINE_INTEGRATION_SURFACES_FULL_IMPLEMENTATION_2026-04-11.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/REVIEW_SPEC.md
  - docs/README.md
  - docs/COMPILER_ERRORS.md
  - examples/README.md
  - doctrine/grammars/doctrine.lark
  - doctrine/model.py
  - doctrine/parser.py
  - doctrine/compiler.py
  - doctrine/renderer.py
  - doctrine/diagnostics.py
  - doctrine/verify_corpus.py
  - editors/vscode/README.md
  - editors/vscode/resolver.js
  - AGENTS.md
---

# TL;DR

## Outcome

Finish every Phase 3 obligation in
`docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md`
that is not already shipped, without cutting scope, then leave the repo with
one honest completion story across `doctrine/`, manifest-backed examples,
evergreen docs, phase docs, and VS Code parity surfaces.

## Problem

Phase 3 is currently described as an active implementation-order phase, and
Phase 4 explicitly assumes its surfaces already exist. But current repo
evidence suggests the opposite boundary: the shipped codebase clearly has
phase-1/phase-2 readable-markdown foundations plus readable-guard restrictions,
yet `properties`, standalone readable `guard` shells, authored
`render_profile`, `row_schema`, `item_schema`, and the late extension blocks
appear in docs and design notes rather than in the shipped compiler, renderer,
corpus, evergreen docs, or VS Code parity surfaces. Historical completion docs
also explicitly deferred or excluded part of this surface, which leaves split
truth behind.

## Approach

Treat `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md`
as the authoritative requested-scope boundary. Audit it line by line against
the shipped grammar, model, parser, compiler, renderer, examples, docs, and
editor surfaces; separate already-landed groundwork from genuinely missing
Phase 3 work; then finish the missing language, lowering, proof, docs, and
editor parity through Doctrine's existing readable owner path only.

## Plan

1. Audit every explicit Phase 3 promise against current shipped repo evidence.
2. Separate already-grounded behavior from truly missing render-policy and
   extension-surface semantics.
3. Land the missing Phase 3 language work through the canonical
   grammar -> model -> parser -> compiler -> renderer path, not through
   comment-specific or docs-only sidecars.
4. Add the proof ladder, live-doc convergence, and VS Code parity needed to
   make the shipped boundary honest.
5. Reconcile later-phase and historical docs so they no longer assume Phase 3
   is shipped when the code says otherwise.

## Non-negotiables

- Do not slim the scope or reinterpret `docs/03_*` into a smaller subset.
- Do not preserve split truth between `docs/03_*`, `docs/04_*`, historical
  implementation artifacts, evergreen docs, examples, and shipped code.
- Do not add a second readable-render architecture, comment-only shell path,
  or fallback layer for profile-sensitive rendering.
- Do not silently move Phase 4 control-plane product scope into Phase 3, but
  do keep Phase 4 docs truthful about the Phase 3 baseline they depend on.
- Do not ship `properties`, `guard`, `render_profile`, row/item schemas, or
  the late block extensions without proof, docs, and editor parity.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-11
external_research_grounding: not run - repo evidence was sufficient on 2026-04-11
deep_dive_pass_2: done 2026-04-11
recommended_flow: implement-loop
note: Auto-plan completed research, two deep-dive passes, and phase-plan from repo evidence only. The artifact is ready for implement-loop.
-->
<!-- arch_skill:block:planning_passes:end -->

Worklog: `docs/PHASE3_RENDER_POLICY_AND_EXTENSION_SURFACES_COMPLETION_2026-04-11_WORKLOG.md`

Implementation status: broad Phase 3 code, proof, docs, and VS Code parity
landed on 2026-04-11, and the core repo checks pass. Fresh
`audit-implementation` found remaining code-completeness gaps in
render-profile behavior and semantic-lowering proof, so the authoritative
verdict below is `NOT COMPLETE` and the session-scoped loop state remains armed
at `.codex/implement-loop-state.019d7eaf-b944-7103-a0ff-c7cb811a8c85.json`.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-11
Verdict (code): NOT COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)

- Authored `render_profile` accepts identity, analysis, review, control, list,
  table, and late-block targets that do not currently affect rendered output;
  only `properties` and `guarded_sections` / `guard` are consumed by the
  renderer.
- Document-level `render_profile:` attachments are ignored when an output uses
  `structure:` to lower a document into a markdown-bearing output.
- The Phase 3 proof ladder is incomplete for the plan's analysis/review/control
  lowering targets and some required compile-negative surfaces.
- Live docs now claim the full render-profile identity display family as
  shipped, but the compiler/renderer do not yet implement profile-sensitive
  identity display.

## Reopened phases (false-complete fixes)

- Phase 2 (explicit guard shells and render profiles) — reopened because:
  - profile resolution and validation landed, but several accepted profile
    targets are inert at render time
  - identity display still uses unconditional title/key/wire projections rather
    than profile-sensitive defaults
  - `document render_profile:` does not survive the common `output structure:`
    lowering path
- Phase 3 (semantic lowering targets and inline block schemas) — reopened
  because:
  - accepted `analysis.stages`, `review.contract_checks`, and
    `control.invalidations` profile targets are not implemented as lowering
    behavior
  - the manifest-backed proof only covers row/item schema descendants, not the
    planned analysis/review/control lowering targets
- Phase 5 (proof ladder, truth convergence, VS Code parity, and closeout) —
  reopened because:
  - the full positive and compile-negative Phase 3 proof ladder is not present
  - docs and editor parity passed for the implemented subset, but surviving docs
    overstate profile behavior that code does not yet own

## Missing items (code gaps; evidence-anchored; no tables)

- Render-profile target semantics
  - Evidence anchors:
    - doctrine/compiler.py:801
    - doctrine/compiler.py:806
    - doctrine/compiler.py:810
    - doctrine/renderer.py:223
    - doctrine/renderer.py:451
    - doctrine/renderer.py:559
    - doctrine/compiler.py:12691
  - Plan expects:
    - Phase 2 says the renderer consumes post-compilation profile policy so
      shells, compactness, and identity defaults vary by profile.
    - Phase 3 says analysis, review-shaped outputs, and concrete invalidation
      expansion lower into typed markdown by profile.
  - Code reality:
    - `_KNOWN_RENDER_PROFILE_TARGETS` accepts `review.contract_checks`,
      `analysis.stages`, `control.invalidations`, `identity.owner`,
      `identity.debug`, `identity.enum_wire`, list/table, and late-block
      targets, but `_resolve_profile_mode()` is only called by properties and
      guard rendering.
    - addressable identity display still returns title/key/wire values through
      the existing projection path without any active profile parameter.
  - Fix:
    - Either implement the accepted profile targets that Phase 3 promises, or
      fail loud / defer unsupported targets so authored profiles cannot appear
      to ship behavior that the renderer ignores. At minimum, implement
      profile-sensitive identity display and the planned analysis/review/control
      lowering modes before claiming code completion.

- Document profile attachment through output structure lowering
  - Evidence anchors:
    - doctrine/compiler.py:4208
    - doctrine/compiler.py:4212
    - doctrine/compiler.py:4214
    - doctrine/compiler.py:14762
  - Plan expects:
    - Phase 2 says authored `render_profile` attaches to `document`,
      `analysis`, `schema`, and markdown-bearing `output`.
  - Code reality:
    - `output structure:` resolves the document, compiles only its body, and
      wraps it in a fresh `CompiledSection` without carrying the resolved
      document `render_profile`.
    - A document-level profile can be parsed and resolved, but it is ignored in
      the common markdown-output structure path.
  - Fix:
    - Preserve the document's resolved profile when compiling structured output,
      while keeping output-level profile override semantics explicit and
      fail-loud.

- Phase 3 proof ladder coverage
  - Evidence anchors:
    - examples/64_render_profiles_and_properties/cases.toml:4
    - examples/64_render_profiles_and_properties/cases.toml:59
    - examples/65_row_and_item_schemas/cases.toml:4
    - examples/66_late_extension_blocks/cases.toml:83
    - docs/PHASE3_RENDER_POLICY_AND_EXTENSION_SURFACES_COMPLETION_2026-04-11.md:1240
  - Plan expects:
    - targeted manifest-backed examples for analysis/review/control-plane
      lowering targets, `item_schema:` / `row_schema:`, and the full
      compile-negative ladder from `docs/03_*`.
  - Code reality:
    - examples 64-66 prove compact `properties`, explicit guard-shell rendering,
      row/item schema addressability, and late extensions.
    - they do not prove analysis lowering by profile, review/control lowering
      by profile, invalid guard source inside an explicit `guard` shell, or
      malformed row/item schema cases beyond duplicate keys.
  - Fix:
    - Add the missing behavior first where it is absent, then add manifest cases
      that exercise those exact lowering and negative surfaces.

- Live-doc truth for profile behavior
  - Evidence anchors:
    - docs/LANGUAGE_REFERENCE.md:260
    - docs/LANGUAGE_REFERENCE.md:263
    - docs/PHASE3_RENDER_POLICY_AND_EXTENSION_SURFACES_COMPLETION_2026-04-11.md:1292
  - Plan expects:
    - surviving live docs agree with the shipped Phase 3 boundary.
  - Code reality:
    - live docs now teach identity-display override support through
      `render_profile`, but code only validates identity targets and does not
      apply them to rendering.
  - Fix:
    - After the code behavior is real, keep the docs as shipped truth; otherwise
      narrow the docs to the implemented subset and record the remaining targets
      as deferred.

## Non-blocking follow-ups (manual QA / screenshots / human verification)

- None. The remaining blockers are code/proof/docs truth gaps, not manual QA.
<!-- arch_skill:block:implementation_audit:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly,
`docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md` will
become an honest description of shipped Doctrine Phase 3. Concretely:

- `properties` will ship as a first-class readable block on the surfaces the
  Phase 3 doc says it should serve.
- explicit readable `guard` shells will ship on top of the existing guard
  expression discipline without inventing a second guard model.
- built-in profile families and authored `render_profile` will ship as the
  Phase 3 doc promises them, and render policy will change readback shape
  without changing semantic meaning or addressability.
- identity-aware title/key/wire rendering defaults, lowering targets,
  `row_schema` / `item_schema`, and the late block extensions
  (`markdown`, `html`, `footnotes`, `image`, and structured-cell nested
  tables) will be implemented, proved, and documented through the shipped
  Doctrine path instead of remaining proposal-only prose.
- later docs that depend on this phase, especially `docs/04_*`, will stop
  assuming a shipped baseline that the code does not yet own.

The claim is false if any explicit Phase 3 surface remains docs-only, if the
compiler and renderer still lack the promised render-policy and extension
surfaces, if the proof/docs/editor parity wave remains absent, or if Phase 4
and the evergreen docs keep assuming a different shipped boundary than the code
actually implements.

## 0.2 In scope

- Every explicit Phase 3 promise in
  `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md`,
  including:
  - `properties`
  - explicit readable `guard` shells
  - authored `render_profile`
  - built-in `ContractMarkdown`, `ArtifactMarkdown`, and `CommentMarkdown`
    profile families
  - identity-aware title/key/wire rendering defaults in readable fields
  - analysis/review/control-plane lowering targets into typed markdown
  - `row_schema:` and `item_schema:`
  - raw `markdown` and `html` blocks
  - `footnotes`
  - `image`
  - nested tables through structured-cell bodies
  - the positive and compile-negative proof ladders those surfaces require
- Canonical owner-path work across:
  - `doctrine/grammars/doctrine.lark`
  - `doctrine/model.py`
  - `doctrine/parser.py`
  - `doctrine/compiler.py`
  - `doctrine/renderer.py`
  - `doctrine/diagnostics.py`
- Manifest-backed examples, evergreen docs, diagnostics docs, and VS Code
  parity surfaces that must match the shipped Phase 3 boundary.
- Architectural convergence needed to keep one truthful readable architecture:
  - reuse the existing typed-markdown pipeline instead of inventing a
    comment-only mini-language
  - sync `docs/04_*` and other live docs that currently assume Phase 3 is
    already shipped
  - reconcile historical implementation docs that explicitly deferred or
    excluded part of this surface

Allowed architectural convergence scope:

- widen touched files across `doctrine/`, `examples/`, `docs/`, and
  `editors/vscode/` as needed to keep one owner path for render policy and
  extension surfaces
- replace prose-only or doc-only assumptions with real compiler/renderer truth
  instead of preserving both stories in parallel
- update or demote stale live truth surfaces that would otherwise keep
  conflicting completion stories alive

## 0.3 Out of scope

- Cutting `docs/03_*` down to only the currently grounded subset.
- Pulling Phase 4 product scope such as `review_family`, `route_only`, or
  `grounding` into this plan except where a touched doc must tell the truth
  about what Phase 3 does or does not provide.
- New editor-product surfaces such as hover, rename, completion, or a language
  server that are unrelated to Phase 3 parity.
- Runtime shims, fallback renderers, shadow comment shells, or compatibility
  layers that keep old and new readable semantics alive in parallel.
- Making raw `markdown` or `html` the default readable path instead of explicit
  block kinds.

## 0.4 Definition of done (acceptance evidence)

- `doctrine/grammars/doctrine.lark`, `doctrine/model.py`,
  `doctrine/parser.py`, `doctrine/compiler.py`, and `doctrine/renderer.py`
  implement the full explicit Phase 3 surface from `docs/03_*`, not only the
  already-shipped readable-markdown subset.
- The repo contains manifest-backed proof for the positive and compile-negative
  Phase 3 ladder, including the late extension blocks defined by the Phase 3
  boundary.
- `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_DESIGN_NOTES.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/REVIEW_SPEC.md`, `docs/README.md`,
  `docs/COMPILER_ERRORS.md`, and `examples/README.md` agree with the shipped
  Phase 3 boundary.
- If editor-facing files move, `editors/vscode/` teaches and resolves the same
  Phase 3 surface as the compiler and docs.
- Relevant verification passes at closeout:
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics change
  - targeted manifest-backed runs for touched examples while the ladder is
    under construction
  - `cd editors/vscode && make` if `editors/vscode/` changes

Behavior-preservation evidence:

- the shipped corpus through
  `examples/63_schema_artifacts_and_groups` stays green unless an explicitly
  justified bug fix changes behavior
- existing readable guard-source restrictions remain fail-loud
- existing title/key/wire identity semantics stay consistent while Phase 3
  adds profile-aware rendering on top
- already-shipped Phase 1 and Phase 2 readable/document/schema surfaces do not
  regress while Phase 3 is added

## 0.5 Key invariants (fix immediately if violated)

- No scope cutting from
  `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md`.
- One readable architecture, one compiler path, one renderer path.
- Render policy changes readback shape, not semantic meaning or addressability.
- Explicit `guard` shells reuse existing guard visibility restrictions.
- Late extensions remain explicit block kinds, not silent fallbacks.
- Human-facing profiles default title-bearing identities to human-facing titles
  unless a more explicit policy is chosen.
- No live doc may assume Phase 3 is complete while the corresponding shipped
  compiler/editor/proof surfaces are still missing.
- No runtime fallbacks or compatibility shims. The phase either ships
  correctly or fails loudly.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Finish every explicit Phase 3 promise before declaring completion.
2. Keep one canonical readable-block owner path for render policy and
   extension surfaces.
3. Preserve already-shipped readable/document/schema behavior while Phase 3 is
   added on top.
4. Converge docs, examples, diagnostics, and editor truth to the same shipped
   boundary.
5. Avoid turning profile-sensitive readback into a second mini-language or
   comment-only architecture.

## 1.2 Constraints

- The repo is already in a partial second-wave state, so this is completion and
  convergence work, not a greenfield feature wave.
- `docs/04_*` assumes `properties`, render profiles, and explicit guard shells
  are already available, so finishing Phase 3 also has a truth-convergence
  obligation.
- Current code search suggests most Phase 3 declaration names and late
  extension blocks are still docs-only, which means the plan likely spans the
  full grammar/model/parser/compiler/renderer path plus examples/docs/editor
  parity.
- Phase 3 includes both render-policy work and late block extensions, so the
  plan cannot stop at `properties` and `render_profile`.

## 1.3 Architectural principles (rules we will enforce)

- `docs/03_*` defines requested Phase 3 behavior; `doctrine/` plus
  manifest-backed cases define shipped truth.
- Grammar, model, parser, compiler, renderer, examples, docs, and editor
  parity move together; no docs-only shipping.
- Reuse the existing readable-block pipeline instead of building separate
  comment, artifact-shell, or contract-only renderers.
- Unsupported or invalid Phase 3 surfaces fail loudly.
- Later phases consume the shipped Phase 3 readable targets; they do not carry
  private copies of missing Phase 3 semantics.

## 1.4 Known tradeoffs (explicit)

- Some of the remaining work may be truth convergence in docs, examples, and
  editor parity rather than pure compiler implementation, but it is still in
  scope because the task is to finish the Phase 3 doc honestly.
- Identity-aware rendering may reuse existing title/key/wire projection
  foundations rather than inventing new identity semantics, but the plan still
  has to make the Phase 3 rendering rules explicit and shipped.
- The late block extensions may widen the touched area materially, especially
  proof and docs, because Phase 3 defines them in the same phase boundary.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- `doctrine/grammars/doctrine.lark` already ships the current typed-markdown
  foundation that Phase 3 says it can build on: top-level `analysis`,
  `schema`, and `document` declarations; shared readable block kinds
  (`sequence`, `bullets`, `checklist`, `definitions`, `table`, `callout`,
  `code`, `rule`); multiline strings; input `structure:`; and output
  `schema:` / `structure:`.
- `doctrine/model.py` and `doctrine/parser.py` already materialize those
  surfaces as first-class data structures, including `DocumentDecl`,
  `ReadableBlock`, `ReadableTableRow`, `InputStructureConfig`,
  `OutputSchemaConfig`, and `OutputStructureConfig`.
- `doctrine/compiler.py` and `doctrine/renderer.py` already compile and render
  analysis/schema/document bodies through one shared readable IR, and the same
  compiler already owns addressable `title` / `key` / `wire` projections.
- The shipped corpus already proves important Phase 1 and 2 groundwork:
  readable guard-source rejection in
  `examples/61_multiline_code_and_readable_failures`, identity projections in
  `examples/62_identity_titles_keys_and_wire`, and schema
  sections/artifacts/groups in `examples/63_schema_artifacts_and_groups`.
- `editors/vscode/README.md` and
  `editors/vscode/tests/integration/suite/index.js` already track these newer
  surfaces, including analysis/schema/document refs, structure/schema refs,
  schema-backed review contracts, and addressable readable descendants.
- `docs/04_*` already assumes a later baseline that includes `properties`,
  render profiles, and explicit guard shells.

## 2.2 What’s broken / missing (concrete)

- Search across shipped code, evergreen docs, and editor parity surfaces shows
  no real support yet for the Phase 3 additive layer itself:
  `properties`, explicit readable `guard` shells, authored
  `render_profile`, built-in profile families, `row_schema`, `item_schema`,
  raw `markdown`, raw `html`, `footnotes`, `image`, and structured-cell nested
  tables are still concentrated in the phase doc and historical planning
  material rather than in the shipped language path.
- Current readable guards are only inline `when <expr>` attachments on existing
  readable blocks. The explicit readable shell from `docs/03_*` does not exist
  yet.
- Current identity behavior already supports `title` / `key` / `wire`
  projections, but the Phase 3 rule that profiles choose human-facing defaults
  for compact readbacks is not yet implemented as a render-policy surface.
- There is no shipped authored `render_profile` declaration or attachment path
  on `document`, `analysis`, `schema`, or markdown-bearing `output`.
- There is no manifest-backed positive and negative proof ladder yet for the
  full Phase 3 surface, and evergreen docs do not currently teach it as
  shipped truth.
- `docs/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md`
  explicitly records explored controls such as `properties`, standalone
  `guard`, and `render_profile` as deferred or excluded from that earlier wave.
- `docs/DOCTRINE_INTEGRATION_SURFACES_FULL_IMPLEMENTATION_2026-04-11.md`
  explicitly treats user-authored `render_profile` as out of scope for that
  completed wave.
- Evergreen docs and examples guides do not currently teach the full Phase 3
  surface as shipped truth.

## 2.3 Constraints implied by the problem

- The missing work must be additive on top of the already-shipped typed-markdown
  path, not a replacement for it and not a comment-only sidecar.
- Profile-sensitive rendering must remain post-compilation policy. It cannot
  mutate semantics, addressability, or the meaning of existing readable nodes.
- Already-shipped readable/document/schema examples and editor tests are
  preservation signals and must stay green while the new Phase 3 layer lands.
- Completion requires truth convergence across code, examples, evergreen docs,
  historical docs, and VS Code parity, not only compiler changes.

<!-- arch_skill:block:reference_pack:start -->
# Reference Pack (folded materials; phase-aligned)
Updated: 2026-04-11

## Inventory

- R1 — Phase 3 - Advanced Typed Markdown Render Policy And Extension Surfaces — `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md`
- R2 — Phase 4 - Review Route Only Grounding And Control Plane Integration — `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md`
- R3 — Historical Mechanics-Wave Disposition — `docs/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md`
- R4 — Historical Integration-Wave Disposition — `docs/DOCTRINE_INTEGRATION_SURFACES_FULL_IMPLEMENTATION_2026-04-11.md`

## Binding obligations (distilled; must satisfy)

- Treat R1 as the requested-scope authority for this plan: Phase 3 owns
  `properties`, explicit readable guard shells, authored `render_profile`,
  built-in profile families, identity-aware title/key/wire rendering defaults,
  lowering targets, `row_schema:` / `item_schema:`, and the late extension
  blocks including `markdown`, `html`, `footnotes`, `image`, and structured-cell
  nested tables. (From: R1)
- Preserve the exact Phase 3 boundary from R1: do not silently pull dedicated
  `review_family`, `route_only`, `grounding`, or control-plane currentness
  semantics into this plan, even though Phase 3 must provide the readable
  machinery those later surfaces depend on. (From: R1, R2)
- Preserve R1's contract that render policy changes readback shape only; it
  does not change semantic meaning or addressability. (From: R1)
- Preserve R1's explicit guard-shell rule: the shell reuses the existing
  expression language and existing guard visibility restrictions rather than
  inventing a second guard discipline. (From: R1, R2)
- Keep the direct Phase 4 dependency visible: R2 explicitly assumes Phase 3
  ships `properties`, render profiles, explicit guard shells, and
  `item_schema:`-backed invalidation readbacks, so Phase 3 completion must
  either provide those surfaces or update the dependent docs truthfully. (From: R2)
- Treat R3's defer/exclude stance as historical drift evidence, not scope
  authority over R1: the earlier mechanics-wave work explicitly left
  `properties`, standalone `guard`, and `render_profile` out of the shipped
  wave unless a later planning pass promoted them, and this Phase 3 plan is
  that later promotion. (From: R1, R3)
- Treat R4's exclusion of user-authored `render_profile` as historical drift
  evidence that must be reconciled if Phase 3 now ships that surface; do not
  preserve both stories live. (From: R1, R4)
- Use R1's exact implementation order as the advisory source sequence for this
  scope:
  `properties` -> identity-aware rendering -> explicit guard shells ->
  built-in and authored `render_profile` -> lowering targets ->
  `row_schema:` / `item_schema:` -> raw `markdown` / `html` ->
  `footnotes` / `image` / structured-cell nested tables. (From: R1)
- Use R1's positive and compile-negative proof ladders as the authoritative
  proof obligations for this phase, including duplicate property keys, invalid
  profile targets, invalid guard sources, malformed row/item schemas, raw
  markdown without multiline text, and nested tables in inline cells. (From: R1)
- Keep late extensions explicit and fail-loud. They must not become silent
  fallback render paths or default escape hatches. (From: R1, R3)
- Keep one readable architecture. Do not add a comment-only shell path,
  artifact-only renderer, or profile-specific compiler path. (From: R1, R3, R4)

## Instruction-bearing structure (only when present; preserve exact or equivalent operational form)

### R1 — Phase 3 - Advanced Typed Markdown Render Policy And Extension Surfaces

1. Preserve the exact ownership boundary:
   - `properties`
   - explicit readable guard shells
   - authored `render_profile`
   - canonical contract, artifact, and comment profile families
   - identity-aware title/key/wire rendering defaults
   - lowering of semantic declarations into typed markdown
   - typed row and item schemas on readable blocks
   - later block extensions that earlier drafts left outside v1
2. Preserve the exact Phase 3 exclusions:
   - dedicated `review_family`
   - dedicated `route_only`
   - dedicated `grounding`
   - control-plane currentness semantics
3. Preserve the exact implementation order from the source:
   1. Add `properties` as a compact readable block.
   2. Add identity-aware title/key/wire rendering defaults for title-bearing values inside readable blocks.
   3. Add explicit `guard` shells on top of the phase-1 guard model.
   4. Add built-in render profiles and authored `render_profile`.
   5. Lower `analysis` and review-shaped readable outputs into typed markdown by profile.
   6. Add control-plane lowering targets for concrete invalidation expansion.
   7. Add `row_schema:` and `item_schema:` on readable blocks.
   8. Add raw markdown and HTML blocks as explicit late extensions.
   9. Add footnotes, images, and nested tables through structured cells.
- Hard negatives:
  - render policy does not change semantics or addressability
  - guard expressions must obey existing visibility rules
  - late extensions remain explicit blocks, not silent fallbacks
- Branch conditions and future-consumer rules:
  - profiles apply after compilation into typed markdown, not before
  - later phases may target row/item schemas and control-plane lowering targets
    once Phase 3 provides them

### R2 — Phase 4 - Review Route Only Grounding And Control Plane Integration

1. Preserve the assumed-shipped baseline from the source:
   - typed markdown is the shared readable architecture
   - `document`, `analysis`, and `schema` already exist
   - owner-aware `schema:` resolution is stable
   - schema `gates:` exist
   - render profiles, `properties`, and explicit guard shells exist
2. Preserve the later-phase ownership boundary:
   - schema-backed `review contract:` integration
   - `review_family`
   - case-selected multi-mode review
   - `route_only`
   - `grounding`
   - control-plane integration with preservation, invalidation,
     `support_only`, `ignore rewrite_evidence`, and `trust_surface`
3. Preserve the Phase 4 dependency on Phase 3 readback machinery:
   - route-only comments reuse phase-3 typed markdown, `properties`, guard
     shells, and comment profiles
   - concrete invalidation expansions rely on `sequence` plus `item_schema:`
- Hard negatives:
  - render profiles and typed markdown only change readability; they do not own
    currentness semantics
  - Phase 4 surfaces must interoperate with workflow law, review, outputs, and
    `trust_surface` rather than replace them
- Branch conditions:
  - invalidating a schema group must preserve member-level currentness semantics
    while expanding one concrete readable member per artifact in authored order

### R3 — Historical Mechanics-Wave Disposition

1. Preserve the historical disposition accurately:
   - the earlier mechanics-wave artifact treated `properties`, standalone
     `guard`, and `render_profile` as explicitly explored controls
   - it also treated raw markdown, HTML-specific constructs, footnotes, images,
     and nested tables as not part of the first shipped readable wave
2. Preserve the consequence of that historical stance:
   - those exclusions are historical drift evidence to reconcile, not a reason
     to shrink the current Phase 3 scope
- Hard negatives:
  - do not silently inherit the earlier defer list as the current plan's scope
    boundary

### R4 — Historical Integration-Wave Disposition

1. Preserve the historical integration-wave exclusions accurately:
   - no separate `review_family` or `route_only` declaration kinds in that wave
   - no silent promotion of explored `grounding` or user-authored
     `render_profile` into shipped core language in that wave
2. Preserve the consequence of that stance:
   - if Phase 3 now ships user-authored `render_profile`, the overlapping
     historical story must be updated, folded, or retired instead of left live
- Hard negatives:
  - do not let the historical integration-wave exclusions silently overrule the
    explicit Phase 3 source doc

## Phase alignment guidance (advisory; core planning commands adopt into Section 7 if needed)

### Global (applies across phases)

- Keep the exact R1 boundary live with no scope cuts and no silent promotion of
  later Phase 4 product surfaces into this plan. (From: R1, R2)
- Keep one readable architecture and one truth story; reconcile the historical
  defer/exclude docs rather than preserving them beside the current Phase 3
  completion story. (From: R1, R3, R4)
- Keep Phase 4 dependency claims honest throughout planning and implementation.
  (From: R2)

### Future foundation / core-semantics phase

- Potentially relevant obligations (advisory):
  - add first-class parser/model/compiler/renderer support for `properties`,
    identity-aware rendering policy, explicit guard shells, built-in and
    authored render profiles, and row/item schemas (From: R1)
  - keep render policy post-compilation and keep guard rules aligned with
    existing visibility restrictions (From: R1)
- References:
  - R1

### Future lowering / extension phase

- Potentially relevant obligations (advisory):
  - add analysis/review/control-plane lowering targets into typed markdown,
    including concrete invalidation expansion targets that later Phase 4 docs
    rely on (From: R1, R2)
  - add the late extension blocks as explicit, fail-loud block kinds rather
    than default escapes (From: R1)
- References:
  - R1, R2

### Future docs / truth-convergence phase

- Potentially relevant obligations (advisory):
  - update dependent Phase 4 baseline claims if implementation sequencing means
    they would otherwise remain ahead of shipped truth (From: R2)
  - reconcile or retire the overlapping historical mechanics/integration-wave
    exclusions once the current Phase 3 truth is known (From: R3, R4)
- References:
  - R2, R3, R4

## Folded sources (verbatim; inlined so they cannot be missed)

### R1 — Phase 3 - Advanced Typed Markdown Render Policy And Extension Surfaces — `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md`
~~~~markdown
## Phase Boundary

This phase owns:

- `properties`
- explicit readable guard shells
- authored `render_profile`
- canonical contract, artifact, and comment profile families
- identity-aware title/key/wire rendering defaults
- lowering of semantic declarations into typed markdown
- typed row and item schemas on readable blocks
- later block extensions that earlier drafts left outside v1

This phase does not own:

- dedicated `review_family`
- dedicated `route_only`
- dedicated `grounding`
- control-plane currentness semantics

## Proof Plan

Positive ladder for phase 3:

1. `properties` in documents and comment-style outputs
2. identity-aware title/key/wire rendering in compact fields
3. explicit guard shells with profile-sensitive render
4. built-in and authored `render_profile`
5. analysis and review lowering into typed markdown
6. control-plane lowering targets for schema-group invalidation expansion
7. `row_schema` and `item_schema`
8. raw markdown and HTML blocks
9. footnotes, images, and nested tables through structured cells

Compile-negative ladder for phase 3:

- duplicate property key
- invalid title/key/wire profile projection target
- invalid profile target
- invalid guard source in a guard shell
- malformed `row_schema:` or `item_schema:`
- raw markdown without multiline text
- nested table in an inline cell

## Exact Implementation Order

1. Add `properties` as a compact readable block.
2. Add identity-aware title/key/wire rendering defaults for title-bearing
   values inside readable blocks.
3. Add explicit `guard` shells on top of the phase-1 guard model.
4. Add built-in render profiles and authored `render_profile`.
5. Lower `analysis` and review-shaped readable outputs into typed markdown by
   profile.
6. Add control-plane lowering targets for concrete invalidation expansion.
7. Add `row_schema:` and `item_schema:` on readable blocks.
8. Add raw markdown and HTML blocks as explicit late extensions.
9. Add footnotes, images, and nested tables through structured cells.
~~~~

### R2 — Phase 4 - Review Route Only Grounding And Control Plane Integration — `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md`
~~~~markdown
## Assumed Shipped Baseline

This phase assumes phases 1 through 3 are available:

- typed markdown is the shared readable architecture
- `document`, `analysis`, and `schema` already exist
- owner-aware `schema:` resolution is stable
- schema `gates:` exist
- render profiles, `properties`, and explicit guard shells exist

## `route_only`

Rules:

- `route_only` owns activation, `current none`, handoff output choice, and
  next-owner routing for routing-only turns
- route-only comments reuse phase-3 typed markdown, `properties`, guard shells,
  and comment profiles
- `route_only` remains explicit about there being no current specialist
  artifact for the turn

## Currentness, Carriage, And Readback

Example concrete invalidation expansion:

```prompt
document RebuildRoutingComment: "Rebuild Routing Comment"
    properties summary: "Route State"
        next_owner: "Next Owner"
        active_mode: "Active Mode"

    sequence invalidations: "Invalidations"
        item_schema:
            artifact_title: "Artifact"
            artifact_path: "Path"
```

Rendered intent:

```markdown
## Invalidations

1. Outline File (`unit_root/OUTLINE.md`) is no longer current.
2. Review Comment (`unit_root/REVIEW_COMMENT.md`) is no longer current.
3. Manifest File (`unit_root/MANIFEST.json`) is no longer current.
```
~~~~

### R3 — Historical Mechanics-Wave Disposition — `docs/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md`
~~~~markdown
## 5.4 Invariants and boundaries

- The mechanics-spec doc’s explicitly explored controls
  (`properties`, standalone `guard`, `render_profile`) do not become
  ship-blocking unless the doc-truth audit explicitly promotes them; the core
  cutover ships the concrete surfaces already specified by the split spec set.

## Historical Reference Pack Excerpt

- Treat `properties`, explicit `guard` blocks, `render_profile`, `row_schema:`,
  and `item_schema:` as explored/deferred surfaces, not first-wave ship
  blockers unless a later core planning command explicitly adopts them.
- Do not add raw markdown escape hatches, HTML-specific constructs, footnotes,
  images, nested tables, or domain-specific table semantics in Doctrine core
  v1.
~~~~

### R4 — Historical Integration-Wave Disposition — `docs/DOCTRINE_INTEGRATION_SURFACES_FULL_IMPLEMENTATION_2026-04-11.md`
~~~~markdown
## Non-negotiables

- No separate `review_family` or `route_only` declaration kinds.
- No silent promotion of explored `grounding` or user-authored
  `render_profile` into shipped core language when the spec explicitly leaves
  them later-wave or deferred.

## 0.3 Out of scope

- Shipping separate `review_family` or `route_only` declaration kinds when the
  spec explicitly says to keep those seams on existing review/workflow-law
  surfaces.
- Shipping first-class `grounding` or user-authored `render_profile` as part of
  this implementation wave. Full implementation of the spec means making those
  defer decisions explicit and truthful, not silently converting them into core
  language.
~~~~
<!-- arch_skill:block:reference_pack:end -->

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- No external research was adopted for auto-plan. The open work is not a prior
  art problem; it is a repo-truth and parity problem inside Doctrine's already
  shipped typed-markdown architecture.

## 3.2 Internal ground truth (code as spec)

- `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md`
  is the authoritative requested-scope boundary for the full Phase 3 surface.
- `doctrine/grammars/doctrine.lark` already proves the shipped baseline named
  by `docs/03_*`: `analysis_decl`, `schema_decl`, `document_decl`, multiline
  strings, shared readable blocks, input `structure:`, and output
  `schema:` / `structure:` all exist today.
- `doctrine/model.py` and `doctrine/parser.py` already prove that analysis,
  schema, document, readable blocks, readable tables, input structure, and
  output structure/schema are first-class model and parser surfaces rather than
  design-note fiction.
- `doctrine/compiler.py` already has the owner-path functions that Phase 3 must
  reuse, not replace:
  `_compile_analysis_decl`, `_compile_schema_decl`, `_compile_document_decl`,
  `_compile_input_decl`, `_compile_output_decl`,
  `_compile_authored_readable_block`, and `_validate_readable_guard_expr`.
- `doctrine/compiler.py` also already owns identity and addressability
  projections for `title`, `key`, and `wire`, which means Phase 3 does not need
  new identity semantics; it needs render-policy defaults on top of those
  existing projections.
- `doctrine/renderer.py` already renders the shared compiled readable blocks,
  which makes it the canonical place for profile-aware shape changes once the
  missing policy layer exists.
- `examples/61_multiline_code_and_readable_failures/cases.toml` and
  `doctrine/diagnostic_smoke.py` prove that readable guard-source validation is
  already fail-loud today.
- `docs/LANGUAGE_REFERENCE.md`,
  `examples/62_identity_titles_keys_and_wire/cases.toml`, and
  `examples/63_schema_artifacts_and_groups/cases.toml` prove that identity
  projections, schema artifacts/groups, and descendant addressability are
  already shipped.
- `editors/vscode/README.md`,
  `editors/vscode/scripts/validate_lark_alignment.py`, and
  `editors/vscode/tests/integration/suite/index.js` prove current editor parity
  for the shipped baseline: analysis/schema/document refs, structure/schema
  refs, schema-backed review contracts, and descendant navigation already work.
- `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md`
  assumes Phase 3 is already shipped and therefore becomes part of the truth
  convergence surface for this work.
- `docs/README.md` still routes readers through the phased plan set and lists
  Phase 3 as the implementation-order doc for these surfaces.
- `docs/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md`
  records `properties`, standalone `guard`, and `render_profile` as deferred or
  excluded from the earlier mechanics wave.
- `docs/DOCTRINE_INTEGRATION_SURFACES_FULL_IMPLEMENTATION_2026-04-11.md`
  records user-authored `render_profile` as out of scope for that completed
  integration wave.
- Current search evidence also makes the remaining gap concrete: outside the
  Phase 3 and historical plan docs, shipped code and evergreen docs do not yet
  expose `properties`, `render_profile`, `row_schema`, `item_schema`, the
  canonical profile families, or the late extension blocks.
- The canonical owner path to reuse remains:
  `doctrine/grammars/doctrine.lark` -> `doctrine/model.py` ->
  `doctrine/parser.py` -> `doctrine/compiler.py` -> `doctrine/renderer.py`,
  with `examples/`, `doctrine/diagnostic_smoke.py`, live docs, and
  `editors/vscode/` following that path.

## 3.3 Research conclusions and remaining local decisions

- The biggest correction from research is architectural, not scoping:
  Doctrine already ships most of the Phase 1 and 2 readable foundation that
  the old draft treated as missing. The remaining Phase 3 work is the additive
  render-policy and extension layer on top of that foundation.
- The canonical implementation shape is therefore:
  additive grammar/model/parser nodes, additive compiler lowering and
  validation, and a profile-aware renderer layered onto the existing compiled
  readable IR.
- No second readable architecture is justified. The shipped document, schema,
  analysis, input/output structure, addressability, and renderer path already
  cover the right ownership boundary.
- Remaining design choices are local implementation choices, not plan blockers:
  exact model shapes for `properties` and explicit `guard`, how authored
  `render_profile` rules are stored internally, and how structured cell bodies
  piggyback on existing table and block dispatch.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- Scope intent lives in `docs/03_*`, while Phase 4 dependency claims live in
  `docs/04_*` and the historical defer/exclude stories live in the two
  `docs/DOCTRINE_*_FULL_IMPLEMENTATION_2026-04-11.md` artifacts.
- Shipped language behavior already fans through the standard Doctrine stack:
  `doctrine/grammars/doctrine.lark` -> `doctrine/model.py` ->
  `doctrine/parser.py` -> `doctrine/compiler.py` -> `doctrine/renderer.py`.
- Proof already lives in the manifest-backed corpus under `examples/`, with
  `doctrine/verify_corpus.py` and `make verify-examples` as the preservation
  path.
- Diagnostic proof already has a separate fail-loud lane in
  `doctrine/diagnostic_smoke.py` and `make verify-diagnostics`.
- Live documentation and editor parity surfaces that must converge with any new
  Phase 3 work live under `docs/` and `editors/vscode/`.

## 4.2 Control paths (runtime)

- Authored `analysis`, `schema`, `document`, and shared readable blocks already
  parse into `model.ReadableBlock`-based structures and compile through the
  shared authored-readable path in `doctrine/compiler.py`.
- Input `structure:` and output `schema:` / `structure:` already resolve onto
  document/schema declarations during compilation, which proves that
  declaration-attached readable policy can reuse existing root-declaration
  attachment points.
- Readable guards already exist today only as inline `when <expr>` metadata on
  readable blocks, and `_validate_readable_guard_expr` enforces the current
  visibility boundary.
- Addressable display and interpolation already resolve through the compiler's
  addressability path, including root and descendant `title`, `key`, and
  `wire` projections.
- The missing Phase 3 surfaces currently have no end-to-end runtime path:
  authors cannot parse, compile, or render `properties`, explicit readable
  `guard` shells, authored profiles, row/item schemas, or the late block
  extensions through shipped Doctrine today.

## 4.3 Object model + key abstractions

- The repo already has the abstractions that should stay central:
  `ReadableBlock`, readable table rows/cells, compiled readable block variants,
  declaration-owned document/schema/analysis nodes, and addressable projection
  targets.
- Those abstractions already support keyed descendants and human-facing titles,
  so Phase 3 should extend them instead of introducing a parallel "compact
  comment" object model.
- Current evidence does not show first-class model/compiler abstractions yet
  for `properties`, explicit readable `guard` shells, authored
  `render_profile`, built-in render profile selection, inline `row_schema:` /
  `item_schema:`, or structured cell bodies.

## 4.4 Observability + failure behavior today

- Repo-owned verification already exists:
  - `make verify-examples`
  - `make verify-diagnostics`
  - `cd editors/vscode && make`
- Existing readable guard failures are already fail-loud and corpus-backed.
- Existing identity and schema-addressability behavior are already manifest
  backed, which makes `examples/61_*` through `examples/63_*` the immediate
  preservation signals while Phase 3 expands.
- For the missing Phase 3 features, the current failure mode is simply "surface
  does not exist yet", which is why doc truth is currently ahead of shipped
  language truth.

## 4.5 UI surfaces (ASCII mockups, if UI work)

- No end-user UI is in scope.
- The only UI-adjacent surface is the VS Code extension parity path, which
  must stay aligned with the shipped language truth.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Phase 3 must ship entirely through the existing Doctrine owner path:
  `doctrine/grammars/doctrine.lark` -> `doctrine/model.py` ->
  `doctrine/parser.py` -> `doctrine/compiler.py` -> `doctrine/renderer.py`.
- The implementation expands that path with additive readable-policy and late
  extension nodes only. It does not create comment-specific renderers, artifact
  shell sidecars, or a second markdown architecture.
- Examples, diagnostics, evergreen docs, historical docs, and VS Code parity
  files are downstream truth surfaces. They update because the owner path
  changes, not as an alternative source of semantics.

## 5.2 Control paths (future)

- `properties`, explicit readable `guard` shells, authored `render_profile`,
  built-in render profile defaults, `row_schema:` / `item_schema:`, and late
  extension blocks all parse into the shared readable family.
- Profiles attach only to readable producers that `docs/03_*` names:
  `document`, `analysis`, `schema`, and markdown-bearing `output`.
- Compilation stays semantic-first: analysis/review/control-plane producers
  lower into the same typed-markdown structures first, then profile selection
  chooses how that already-compiled readable structure is rendered.
- Structured cell bodies for nested tables reuse the same readable block
  dispatch and validation path as top-level blocks.

## 5.3 Object model + abstractions (future)

- Add first-class readable-family representations for the missing surfaces:
  compact keyed properties, explicit guard shells, authored profile
  declarations and attachments, inline block schemas, raw markdown/raw HTML,
  footnotes, images, and structured cell bodies.
- Extend compiled readable IR only where the current variants cannot faithfully
  represent the new block families or profile-specific metadata.
- Treat render policy as explicit post-compilation data. The renderer consumes
  policy and compiled readable structures together, while addressability and
  semantic meaning stay owned by the compiler.

## 5.4 Invariants and boundaries

- One readable architecture, not separate document, comment, and artifact-shell
  renderers.
- No fallback comment shell, compatibility layer, or doc-only profile
  simulation.
- Render policy may change shape, ordering, verbosity, shell framing, and
  default identity projection, but not semantic meaning, addressability, or
  guard visibility rules.
- Explicit `guard` shells reuse the existing guard expression language and
  current readable guard-source restrictions.
- `properties`, row/item schemas, and structured cell bodies remain keyed and
  addressable beneath their owning readable block.
- Late extensions remain explicit blocks and fail loudly when malformed.
- Phase 3 still does not add `review_family`, `route_only`, `grounding`, or
  currentness semantics; it only provides the reusable readback machinery those
  later surfaces consume.

## 5.5 UI surfaces (ASCII mockups, if UI work)

- VS Code syntax, resolver behavior, README examples, and integration tests
  expand only as needed to teach and navigate the newly shipped Phase 3
  surfaces.
- No new editor product surface exists beyond parity with shipped Doctrine
  semantics.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Phase boundary | `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md` | full Phase 3 doc | requested scope is explicit, but parts of it are not shipped | keep it as the behavioral source and implement every still-missing obligation it names | user asked for no scope cuts | authoritative Phase 3 surface list | examples, docs review |
| Grammar | `doctrine/grammars/doctrine.lark` | readable block grammar, top-level declarations, attachment points | shipped readable grammar stops before the additive Phase 3 surfaces | add syntax for `properties`, explicit readable `guard`, `render_profile`, attachment clauses, `row_schema:`, `item_schema:`, `markdown`, `html`, `footnotes`, `image`, and structured cell bodies | features do not exist until grammar accepts them | additive readable-policy and extension grammar | verify-examples, VS Code |
| Model | `doctrine/model.py` | readable block/data classes | model has current readable blocks, tables, and producer attachments only | add first-class model representations for Phase 3 block families, profile declarations/attachments, and inline block schemas | keep one semantic object model | widened readable-family model | verify-examples |
| Parser | `doctrine/parser.py` | readable block parsing, producer parsing | parser handles current readable family and structure/schema refs | parse every new Phase 3 surface onto the shared model, preserving current producer attachments | keep parse path aligned with grammar and compiler | canonical parsed Phase 3 AST | verify-examples |
| Compiler: readable lowering | `doctrine/compiler.py` | `_compile_authored_readable_block` and adjacent readable compilation/addressability helpers | compiler lowers current readable blocks and enforces guard visibility; Phase 3 additions are absent | add compilation, addressability, uniqueness checks, and validation for `properties`, explicit `guard`, row/item schemas, and late block extensions | keep additive work on the existing owner path | compiled readable IR covers full Phase 3 block family | verify-examples, verify-diagnostics |
| Compiler: producer lowering | `doctrine/compiler.py` | `_compile_analysis_decl`, `_compile_schema_decl`, `_compile_document_decl`, `_compile_output_decl` | current producers compile/read back without authored render policy | add profile attachment resolution and the lowering targets Phase 3 owns for analysis/review/control-plane readbacks | later phases depend on these producer seams | producer-level profile + lowering contract | verify-examples |
| Renderer | `doctrine/renderer.py` | readable block dispatch and markdown emission | renderer outputs current readable family with one default shape | make renderer profile-aware without changing semantics; add rendering for new block kinds and shell behaviors | Phase 3 is mostly about readback shape | one profile-aware markdown renderer | verify-examples |
| Diagnostics | `doctrine/diagnostic_smoke.py`, `docs/COMPILER_ERRORS.md` | compile-negative coverage and error catalog | current diagnostics cover existing readable guard failures and other shipped rules, not the full Phase 3 ladder | add fail-loud validation coverage and document the resulting error surfaces | requested scope includes the compile-negative ladder | explicit Phase 3 validation contract | verify-diagnostics |
| Proof corpus | `examples/README.md`, new `examples/64+` manifests/artifacts | example ladder | shipped corpus stops at current baseline examples; no dedicated Phase 3 ladder exists | add manifest-backed positive and negative examples in the source-doc order | Doctrine is example-first and proof-backed | canonical Phase 3 proof ladder | verify-examples |
| Evergreen docs | `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/REVIEW_SPEC.md`, `docs/README.md` | live docs truth | live docs teach the shipped baseline but not the missing Phase 3 layer | update the surviving canonical docs to describe the new surfaces and their boundaries accurately | avoid split truth | one live docs story | docs review |
| Historical / dependent docs | `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md`, `docs/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md`, `docs/DOCTRINE_INTEGRATION_SURFACES_FULL_IMPLEMENTATION_2026-04-11.md` | baseline assumptions and earlier defer/exclude claims | dependent docs are ahead of code and historical docs still preserve earlier exclusions | reconcile, demote, or annotate these docs so they stop competing with shipped truth | phase completion is not honest until drift is removed | truthful cross-phase and historical story | docs review |
| VS Code parity | `editors/vscode/syntaxes/doctrine.tmLanguage.json`, `editors/vscode/resolver.js`, `editors/vscode/scripts/validate_lark_alignment.py`, `editors/vscode/README.md`, `editors/vscode/tests/integration/suite/index.js` | syntax, navigation, alignment, README, integration tests | editor parity already covers the shipped baseline but not the Phase 3 additive layer | extend syntax, resolver coverage, README examples, and tests only where new Phase 3 surfaces need parity | editor truth is in scope | broader parity on the same language path | `cd editors/vscode && make` |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `doctrine/grammars/doctrine.lark` -> `doctrine/model.py` ->
    `doctrine/parser.py` -> `doctrine/compiler.py` -> `doctrine/renderer.py`
    remains the only valid owner path.
- Deprecated APIs if any:
  - none should be added; Phase 3 widens the existing readable path rather than
    introducing a public sidecar surface.
- Delete or rewrite list:
  - any stale wording in `docs/04_*` that still assumes unshipped Phase 3
    surfaces during the rollout
  - the defer/exclude wording in the two historical implementation docs once
    the corresponding Phase 3 surfaces ship
  - any temporary README, reference, or editor wording that preserves a split
    completion story
- Capability-replacing harnesses to delete or justify:
  - none identified; this is compiler/renderer/docs parity work, not a prompt
    or tooling replacement problem.
- Live docs/comments/instructions to update or delete:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/LANGUAGE_DESIGN_NOTES.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/REVIEW_SPEC.md`
  - `docs/README.md`
  - `docs/COMPILER_ERRORS.md`
  - `examples/README.md`
  - `editors/vscode/README.md`
- Behavior-preservation signals for refactors:
  - `make verify-examples`
  - targeted manifest-backed runs for new Phase 3 examples while the ladder is
    under construction
  - `examples/61_multiline_code_and_readable_failures`
  - `examples/62_identity_titles_keys_and_wire`
  - `examples/63_schema_artifacts_and_groups`
  - `make verify-diagnostics` when diagnostics move
  - `cd editors/vscode && make` when editor files change

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Readable block family | `doctrine/grammars/doctrine.lark`, `doctrine/model.py`, `doctrine/parser.py`, `doctrine/compiler.py`, `doctrine/renderer.py` | add new Phase 3 surfaces as shared readable-family members instead of sidecars | prevents comment-only or artifact-only drift | include |
| Identity display | `doctrine/compiler.py`, `doctrine/renderer.py`, `docs/LANGUAGE_REFERENCE.md`, `examples/62_identity_titles_keys_and_wire` | reuse shipped `title` / `key` / `wire` projection semantics for profile defaults | prevents a second identity system | include |
| Producer attachments | `doctrine/compiler.py`, `doctrine/parser.py`, `docs/04_*`, `docs/REVIEW_SPEC.md` | attach render policy at producer declarations and lower semantic producers into typed markdown | prevents review/control-plane readbacks from forking later | include |
| Block-owned symbolic shape | readable table/list compilation and addressability paths | thread `row_schema:` / `item_schema:` through existing keyed descendant logic | prevents later review/preservation code from inventing ad hoc shape metadata | include |
| Late extension rendering | readable block dispatch + VS Code syntax | make `markdown`, `html`, `footnotes`, `image`, and structured cells explicit block kinds | prevents silent fallback escapes | include |
| Historical truth cleanup | `docs/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md`, `docs/DOCTRINE_INTEGRATION_SURFACES_FULL_IMPLEMENTATION_2026-04-11.md` | rewrite or demote earlier exclusions after implementation lands | prevents live contradictory completion stories | include |
| Later product seams | `review_family`, `route_only`, `grounding`, currentness semantics | keep later-phase product semantics out of this implementation wave | prevents scope creep into Phase 4 | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — `properties` and compact identity rendering

* Goal:
  Establish the compact fact-panel primitive and the default identity-display
  rule on top of the already-shipped readable path.
* Work:
  Add grammar/model/parser/compiler/renderer support for `properties` as a
  keyed readable block family member.
  Reuse the existing `title` / `key` / `wire` projection machinery so compact
  property bodies default to human-facing titles unless the author or profile
  asks for structural output.
  Add duplicate-property-key and invalid profile-projection validation where
  needed.
* Verification (smallest signal):
  Add one targeted manifest-backed example for `properties` plus identity
  projection behavior and run it with `uv run --locked python -m doctrine.verify_corpus --manifest ...`.
  Keep `examples/62_identity_titles_keys_and_wire` green.
* Docs/comments (propagation; only if needed):
  Add one succinct code comment at the compiler or renderer boundary if the
  identity-default rule is easy to misuse.
* Exit criteria:
  `properties` exists as a first-class readable block kind, stays addressable,
  and does not introduce a second identity system.
* Rollback:
  Remove the additive `properties` surface if it cannot be routed through the
  shared readable path without semantic duplication.

## Phase 2 — explicit guard shells and render profiles

Status: REOPENED (audit found missing code work)

Missing (code):
- Accepted `render_profile` targets beyond `properties` and
  `guarded_sections` / `guard` are currently inert at render time.
- Identity display does not vary by active profile even though identity profile
  targets are accepted and documented.
- `document render_profile:` is ignored when a markdown-bearing output lowers a
  `structure:` document body.

* Goal:
  Add post-compilation render policy without changing meaning, visibility, or
  addressability.
* Work:
  Add explicit readable `guard` shells that reuse the current guard expression
  language and `_validate_readable_guard_expr` restrictions.
  Add built-in `ContractMarkdown`, `ArtifactMarkdown`, and `CommentMarkdown`
  defaults plus authored `render_profile` declarations and attachments on
  `document`, `analysis`, `schema`, and markdown-bearing `output`.
  Make the renderer consume profile policy after compilation so shells,
  compactness, and identity defaults vary by profile instead of by semantic
  source.
* Verification (smallest signal):
  Add targeted manifest-backed examples for explicit guard shells and authored
  profiles.
  Keep `examples/61_multiline_code_and_readable_failures` green.
  Run `make verify-diagnostics` if new validation surfaces are added.
* Docs/comments (propagation; only if needed):
  Update the canonical docs that explain readable guards and rendering policy.
  Add one boundary comment if needed to make "profiles are post-compilation"
  hard to violate.
* Exit criteria:
  The same compiled readable structure can render under built-in or authored
  profiles, and explicit guard shells do not create a second condition model.
* Rollback:
  Remove profile attachments and shell syntax if implementation drifts toward a
  parallel readable architecture or mutates semantics.

## Phase 3 — semantic lowering targets and inline block schemas

Status: REOPENED (audit found missing code work)

Missing (code):
- Accepted `analysis.stages`, `review.contract_checks`, and
  `control.invalidations` render-profile targets do not currently drive
  lowering or rendering behavior.
- Manifest proof is missing for analysis/review/control-plane lowering targets.

* Goal:
  Let semantic producers target shared typed-markdown shapes and expose stable
  symbolic shape references for later consumers.
* Work:
  Add the Phase 3 lowering targets for analysis, review-shaped outputs, and
  concrete invalidation expansion so they compile into typed markdown by
  profile.
  Add `item_schema:` and `row_schema:` on the readable blocks the source doc
  names and thread their keyed descendants through addressability and
  validation.
  Keep `review_family`, `route_only`, `grounding`, and control-plane
  currentness semantics out of scope.
* Verification (smallest signal):
  Add targeted manifest-backed examples for analysis/review/control-plane
  lowering targets and for `item_schema:` / `row_schema:`.
  Keep `examples/63_schema_artifacts_and_groups` green.
* Docs/comments (propagation; only if needed):
  Update the docs that define what Phase 3 owns versus what Phase 4 still owns.
* Exit criteria:
  Later phases can lower onto Phase 3 typed-markdown targets without adding new
  readable code paths, and block-owned schemas are stable symbolic shape
  surfaces.
* Rollback:
  Remove the lowering or schema additions if they start carrying currentness or
  later product semantics instead of shared typed-markdown structure.

## Phase 4 — late extension blocks through shared dispatch

* Goal:
  Finish the late extension surface without opening escape hatches.
* Work:
  Add explicit `markdown`, `html`, `footnotes`, and `image` block kinds.
  Add structured cell bodies so nested tables become legal only in the explicit
  structured-cell form from `docs/03_*`.
  Enforce multiline `text` for raw markdown and HTML and keep nested tables
  illegal in plain inline cells.
* Verification (smallest signal):
  Add targeted manifest-backed examples for each late block family plus compile
  negatives for malformed raw markdown/HTML and nested tables in inline cells.
* Docs/comments (propagation; only if needed):
  Update the block catalog docs and the compiler error catalog for the new
  fail-loud rules.
* Exit criteria:
  Every late block extension from Phase 3 is explicit, shared-dispatch, and
  fail-loud.
* Rollback:
  Remove any late extension that only works by bypassing the shared readable
  dispatch path.

## Phase 5 — proof ladder, truth convergence, VS Code parity, and closeout

Status: REOPENED (audit found missing code work)

Missing (code):
- The full positive and compile-negative Phase 3 proof ladder is not complete:
  missing proof includes analysis/review/control lowering, invalid guard source
  inside an explicit guard shell, and malformed row/item schemas beyond
  duplicate-key checks.
- Live docs currently overstate shipped render-profile identity behavior.

* Goal:
  Leave one honest shipped-truth story for Phase 3 across compiler, proof,
  docs, and editor surfaces.
* Work:
  Finish the full positive and compile-negative manifest ladder in the source
  doc's order.
  Update `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_DESIGN_NOTES.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/REVIEW_SPEC.md`, `docs/README.md`,
  `docs/COMPILER_ERRORS.md`, and `examples/README.md`.
  Reconcile `docs/04_*` and the two historical implementation docs so they no
  longer preserve split truth.
  Extend VS Code syntax, alignment, resolver, README, and integration tests for
  the newly shipped surfaces.
* Verification (smallest signal):
  Run `make verify-examples`.
  Run `make verify-diagnostics` if diagnostics changed.
  Run `cd editors/vscode && make` if editor files changed.
* Docs/comments (propagation; only if needed):
  Delete or rewrite any touched live doc or editor instruction that remains
  ahead of shipped truth.
* Exit criteria:
  `docs/03_*` is honest as shipped Doctrine truth, dependent docs no longer
  assume a different boundary, and the editor teaches the same surface the
  compiler ships.
* Rollback:
  Revert doc/editor claims that outrun implementation rather than leaving split
  truth behind.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Prefer existing compiler and diagnostic verification surfaces over new custom
  harnesses.
- Add the smallest fail-loud checks needed for invalid Phase 3 authoring.

## 8.2 Integration tests (flows)

- `make verify-examples` should stay the primary preservation signal.
- Use targeted manifest-backed runs while building the new Phase 3 ladder.
- Keep `examples/61_multiline_code_and_readable_failures`,
  `examples/62_identity_titles_keys_and_wire`, and
  `examples/63_schema_artifacts_and_groups` as preservation sentinels.
- Run `make verify-diagnostics` if diagnostics or the error catalog move.

## 8.3 E2E / device tests (realistic)

- Run `cd editors/vscode && make` if `editors/vscode/` changes.
- Manual live-editor smoke can remain a finalization check rather than an early
  gate.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Hard-cut the shipped language/docs/editor truth together in one repo wave.
- Do not leave Phase 3 half-shipped behind feature flags, fallback paths, or
  docs-only claims.

## 9.2 Telemetry changes

- None expected. This is compiler/docs/editor parity work, not runtime
  telemetry work.

## 9.3 Operational runbook

- Use repo-owned verification commands only.
- Keep touched docs and instructions aligned in the same pass that lands the
  behavior.

# 10) Decision Log (append-only)

## 2026-04-11 - Create canonical Phase 3 completion plan

Context

- The user asked for a full plan to finish whichever parts of
  `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md`
  are not done and explicitly said not to slim scope.
- The existing Phase 3 doc is a phase/spec artifact, not a canonical full-arch
  plan doc.

Options

- Reformat `docs/03_*` into the canonical arch artifact.
- Create a new canonical full-arch completion plan that treats `docs/03_*` as
  the requested-scope source.

Decision

- Create a new canonical completion plan and keep `docs/03_*` as the
  authoritative scope document.

Consequences

- The workflow now has one canonical artifact for execution truth without
  mutating the original phase/spec doc.
- Later `arch-step` commands can deepen research, architecture, and phase
  planning against this artifact while preserving the full Phase 3 scope.

Follow-ups

- Confirm the North Star and this no-scope-cut interpretation before deeper
  planning.

## 2026-04-11 - Ground Phase 3 against shipped Doctrine before planning

Context

- Auto-plan required a real research pass before architecture and phase
  planning.
- The draft artifact still implicitly treated much of the typed-markdown
  foundation as missing.

Options

- Keep planning as if Phase 3 were mostly greenfield.
- Re-ground the plan against shipped code and narrow the missing work to the
  additive Phase 3 layer only.

Decision

- Re-ground the plan against shipped Doctrine and treat the missing work as the
  additive render-policy, lowering, inline-schema, and late-extension layer on
  top of the already-shipped readable foundation.

Consequences

- The plan now reuses the existing readable/document/schema owner path instead
  of inventing a second readable architecture.
- The authoritative execution checklist is now focused on the real missing
  surfaces: `properties`, explicit readable `guard`, `render_profile`,
  lowering targets, row/item schemas, and the late extension blocks.

Follow-ups

- Carry this corrected architecture through implementation, proof, docs, and
  VS Code parity without reviving the older defer/exclude stories.

## 2026-04-11 - Complete auto-plan without external research

Context

- The auto-plan controller requires research, two deep-dive passes, and
  phase-plan before handing off to implementation.
- Repo evidence was sufficient to answer the architectural questions.

Options

- Pause for external research even though the remaining questions were internal
  repo-truth questions.
- Finish the planning arc from repo evidence only.

Decision

- Complete auto-plan from repo evidence only and mark external research as not
  run because it was unnecessary for this architecture.

Consequences

- The canonical artifact now has updated research grounding, architecture,
  exhaustive call-site inventory, and the authoritative phased implementation
  plan.
- The next honest move is `implement-loop`, not more planning ceremony.

Follow-ups

- Start implementation against this artifact and keep the plan/worklog truth
  aligned as code lands.
