---
title: "Doctrine - Phase 1 Typed Markdown Completion Parity Plan - Architecture Plan"
date: 2026-04-11
status: historical
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: parity_plan
related:
  - docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md
  - docs/READABLE_MARKDOWN_SPEC.md
  - docs/archive/second_wave/DOCTRINE_READABLE_MARKDOWN_FULL_IMPLEMENTATION_2026-04-11.md
  - docs/archive/second_wave/DOCTRINE_READABLE_MARKDOWN_FULL_IMPLEMENTATION_2026-04-11_WORKLOG.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/README.md
  - examples/README.md
  - AGENTS.md
  - doctrine/grammars/doctrine.lark
  - doctrine/model.py
  - doctrine/parser.py
  - doctrine/compiler.py
  - doctrine/diagnostics.py
  - doctrine/renderer.py
  - doctrine/verify_corpus.py
  - examples/29_enums
  - examples/56_document_structure_attachments
  - examples/58_readable_document_blocks
  - examples/59_document_inheritance_and_descendants
  - examples/60_shared_readable_bodies
  - examples/61_multiline_code_and_readable_failures
  - editors/vscode/README.md
---

# TL;DR

## Outcome

Finish Phase 1 exactly as `docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md`
defines it, with no scope cutting: either every promised surface is already
shipped and proved, or the remaining gaps are closed and every live truth
surface in the repo says so consistently.

## Problem

Phase 1 is no longer a clean "not started" spec. The document/readable core now
exists across `doctrine/`, `examples/56_*` through `examples/61_*`, and editor
docs, but repo truth is split across the Phase 1 spec, broader readable-markdown
implementation artifacts, stale corpus-boundary statements that still stop at
`53`, and a likely real remaining identity gap around concrete-agent titles and
explicit enum `wire` handling that is promised by `docs/01_*` but not evident on
the current grammar/model path.

## Approach

Treat `docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md` as the
authoritative Phase 1 boundary, then do a line-item parity pass against shipped
Doctrine, manifest-backed proof, live docs, instructions, and VS Code parity
surfaces. Any actual code gap stays in scope. Any stale truth surface gets
updated or folded so Phase 1 has one honest completion story.

## Plan

1. Audit every Phase 1 obligation in `docs/01_*` against the current shipped
   compiler, renderer, corpus, and editor surfaces.
2. Separate true remaining implementation/proof gaps from already-landed work
   that only needs docs or status convergence.
3. Close any real code or proof gaps through the existing `doctrine/` owner
   path, not through a parallel readable path or new staging layer.
4. Sync live truth surfaces, including corpus-boundary docs and the broader
   readable-markdown plan/worklog pair, so they reflect the same final Phase 1
   state.
5. End with manifest-backed proof plus the relevant repo verification commands,
   then mark Phase 1 complete only if that evidence is green.

## Non-negotiables

- Do not slim the scope or reinterpret `docs/01_*` into a smaller subset.
- Do not reopen already-landed Phase 1 surfaces as speculative redesign work.
- Do not keep split truth between `docs/01_*`, live docs, examples, `AGENTS.md`,
  and active plan artifacts.
- Do not carry two readable-markdown owner paths, two renderer stories, or two
  competing completion checklists.
- Do not declare Phase 1 complete while any promised proof, validation, or
  editor-facing shipped surface still disagrees with repo reality.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-11
Verdict (code): COMPLETE
Manual QA: pending (non-blocking)

## Code blockers (why code is not done)
- None. The archived follow-through worklog records the reconciliation of the
  overlapping readable-markdown plan plus passing reruns for the targeted
  identity manifest, diagnostic smoke, and `cd editors/vscode && make` from
  the main worktree.

## Reopened phases (false-complete fixes)
- None. The later follow-through recorded in
  `docs/archive/PHASE1_TYPED_MARKDOWN_COMPLETION_PARITY_PLAN_2026-04-11_WORKLOG.md`
  closed both reopened items.

## Missing items (code gaps; evidence-anchored; no tables)
- None. This archived parity plan is retained as historical implementation
  trail only.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None required for this archived copy.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-11
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-11
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: Auto-plan completed the two required architecture passes from repo evidence alone; external research stayed unnecessary for this parity task.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly, `docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md`
will become an honest description of shipped Doctrine Phase 1. Concretely:

- first-class `document` remains shipped through the canonical grammar, parser,
  model, compiler, and renderer path
- the readable block family named in Phase 1 is either proved end to end where
  the doc says it ships or any missing semantics are finished through the same
  owner path
- multiline strings, `structure:` attachments, title/key/wire identity
  projections, document addressability, inheritance, validation, and proof are
  all either manifest-backed shipped truth or explicitly finished in this cut
- live docs, repo instructions, and editor-facing proof surfaces tell the same
  Phase 1 story instead of mixing old and new corpus boundaries or stale audit
  states

The claim is false if any Phase 1 obligation in `docs/01_*` still lacks shipped
implementation or proof, if live truth surfaces still disagree about whether the
post-`53` readable-markdown ladder is shipped, or if an active plan continues to
report Phase 1-adjacent work as incomplete after current evidence says it is
green.

## 0.2 In scope

- Every explicit Phase 1 surface in
  `docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md`:
  - typed markdown block model
  - first-class `document`
  - shared readable block family
  - multiline strings
  - `structure:` on markdown-bearing inputs and outputs
  - title-bearing concrete-agent and enum-member identity surfaces, including
    `:title`, `:key`, and `:wire`
  - renderer conversion from section-only recursion to block dispatch
  - document addressability, inheritance, validation, diagnostics, and proof
- The manifest-backed proof and example ladder needed to call those Phase 1
  surfaces shipped, especially the current readable-markdown examples under
  `examples/56_*` through `examples/61_*`.
- Live docs and instructions that make claims about the shipped Phase 1 surface
  or shipped corpus boundary, including `docs/README.md`,
  `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_DESIGN_NOTES.md`,
  `examples/README.md`, `editors/vscode/README.md`, and `AGENTS.md`.
- Architectural convergence needed to keep one truthful owner path:
  - updating or folding stale readable-markdown implementation artifacts
  - repairing stale implementation-audit blocks
  - deleting or rewriting outdated corpus-boundary claims

## 0.3 Out of scope

- Any new language capability that `docs/01_*` does not promise.
- Later numbered-phase work from `docs/02_*` through `docs/04_*`, except where a
  live doc or example index must mention them accurately to keep Phase 1 truth
  honest.
- Raw-markdown escape hatches, HTML features, images, footnotes, nested tables,
  or any other readable-markdown expansion explicitly outside the Phase 1
  document.
- Replacing the current readable compiler and renderer path with a new wrapper,
  migration shim, or alternate mini-language.

## 0.4 Definition of done (acceptance evidence)

Phase 1 is done only when:

- every line item in `docs/01_*` is classified as shipped-and-proved or closed
  by the implementation pass
- the active proof ladder for the Phase 1 readable/document wave is green,
  including the targeted manifest-backed examples that prove document
  structures, rich readable blocks, inheritance/descendants, shared readable
  bodies, and multiline code/readable failures
- `make verify-examples` passes as the repo-wide preservation signal
- `make verify-diagnostics` passes if diagnostics move
- `cd editors/vscode && make` passes if any `editors/vscode/` truth surface or
  parity surface changes
- live docs and instructions no longer claim a pre-`54` shipped boundary or a
  stale incomplete status for landed readable-markdown work

Behavior preservation is proved by the existing full corpus and the current
readable-markdown ladder staying green rather than by new bespoke harnesses.

## 0.5 Key invariants (fix immediately if violated)

- No scope cutting against `docs/01_*`.
- No second readable renderer or compiler owner path.
- No dual truth between spec docs, live docs, examples, and active plan docs.
- Keys remain structural law; titles remain prose; wire values remain external
  codecs, not structural identities.
- `structure:` stays document-only and markdown-bearing.
- Validation stays fail loud.
- Historical implementation evidence may stay in worklogs, but stale active
  status blocks may not remain live truth.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Finish exact parity with `docs/01_*`, not a narrowed reinterpretation.
2. Preserve the one canonical `doctrine/` owner path for readable markdown and
   identity semantics.
3. Converge live docs, proof, and plan state in the same cut so completion is
   auditable.
4. Preserve existing shipped behavior outside any real Phase 1 gap.

## 1.2 Constraints

- `doctrine/verify_corpus.py` resolves manifests by globbing `examples/*/cases.toml`,
  so the repo-wide verification surface is broader than legacy docs that still
  stop at `53`.
- The repo already contains Phase 1-aligned examples and editor docs, so the
  remaining work must distinguish landed behavior from stale narrative.
- Existing broader readable-markdown artifacts are useful evidence but are not
  automatically the authoritative Phase 1 completion surface.

## 1.3 Architectural principles (rules we will enforce)

- Use `docs/01_*` as the requested behavior boundary for this plan.
- Treat `doctrine/` plus manifest-backed examples as shipped truth when docs
  disagree.
- Prefer status repair, proof repair, and live-doc convergence before inventing
  new code.
- Delete or rewrite stale live truth instead of preserving conflicting history
  in active docs.

## 1.4 Known tradeoffs (explicit)

- The readable/document half may end as mostly convergence work, but the current
  grammar/model path still suggests a real implementation gap around concrete-agent
  titles and explicit enum `wire` support, so the plan cannot assume a docs-only
  finish.
- The broader readable-markdown plan may need status repair or folding so this
  Phase 1 completion plan does not create a competing truth surface.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, `doctrine/model.py`,
  `doctrine/compiler.py`, and `doctrine/renderer.py` already define and compile
  the document/readable half of Phase 1: `document`, `structure:` attachments,
  readable block kinds, multiline-code validation, and block-dispatch rendering.
- `examples/README.md` currently teaches the corpus through
  `examples/61_multiline_code_and_readable_failures`, including the readable
  Phase 1 ladder at `56`, `58`, `59`, `60`, and `61`.
- `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, and `editors/vscode/README.md`
  already describe large parts of the shipped Phase 1 surface.
- `docs/archive/second_wave/DOCTRINE_READABLE_MARKDOWN_FULL_IMPLEMENTATION_2026-04-11.md` and its
  worklog capture a broader readable-markdown implementation effort with real
  execution history.
- The current identity path is older than the Phase 1 source doc:
  `agent` heads have no authored title slot, and enum members are still modeled
  as `key/value` pairs rather than explicit `key/title/wire` metadata.

## 2.2 What’s broken / missing (concrete)

- There is no dedicated canonical artifact that maps `docs/01_*` line by line
  to current shipped reality and remaining debt.
- The current grammar/model/compiler path does not yet visibly implement the
  full Phase 1 identity slice from `docs/01_*`: concrete-agent declaration-head
  titles, explicit enum-member `wire:` values, or the corresponding fail-loud
  validation rules.
- Some live truth surfaces still speak in the older "shipped corpus stops at
  `53`" frame, including `AGENTS.md` and `docs/LANGUAGE_DESIGN_NOTES.md`.
- The active readable-markdown plan still contains a `NOT COMPLETE` audit block
  that conflicts with later worklog entries showing repeated passing
  `cd editors/vscode && make` evidence.
- Because of that split truth, "what remains to finish Phase 1?" is not
  currently answerable from one honest repo surface.

## 2.3 Constraints implied by the problem

- The fix must separate true missing implementation from stale documentation or
  stale audit state.
- Any completion plan has to include docs and instruction convergence, not just
  compiler edits.
- The verification story has to rely on existing corpus and editor signals,
  because Phase 1 already has a meaningful proof ladder in-repo.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- None required for this planning pass — reject external prior-art work for now
  — the remaining questions are grounded by shipped repo evidence rather than by
  a missing systems-design reference.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md` — the exact Phase 1
    scope boundary, including both the readable/document wave and the
    title/key/wire identity slice.
  - `doctrine/grammars/doctrine.lark` — ships `document`, readable nonsection
    blocks, `structure:` attachments, and multiline strings; still declares
    `agent` as `agent CNAME ... :` with no head-title slot and `enum_member` as
    `CNAME ":" string` with no explicit `wire:` form.
  - `doctrine/parser.py` — builds `DocumentDecl`, input/output `structure:`
    configs, readable blocks, `EnumDecl(name, title, members)`, and
    `EnumMember(key, value)`, which confirms the readable/document path is landed
    while the explicit Phase 1 enum wire split is not.
  - `doctrine/model.py` — `ReadableBlock`, `ReadableOverrideBlock`,
    `DocumentDecl`, `InputStructureConfig`, and `OutputStructureConfig` are
    shipped; `Agent(name, fields, ...)` has no title field and
    `EnumMember(key, value)` has no separate title or wire metadata.
  - `doctrine/compiler.py` — `_compile_document_decl` and
    `_resolve_document_decl` own document compilation and inheritance today;
    readable failures are fail loud; enum member resolution still returns
    `member.value`, and diagnostics stop at duplicate enum member keys rather
    than Phase 1 wire-specific rules.
  - `doctrine/renderer.py` — block-dispatch rendering is already shipped for
    code, rules, callouts, definitions, tables, sequences, bullets, and
    checklists.
  - `doctrine/verify_corpus.py` and `examples/README.md` — manifests are the
    proof surface, and the active corpus already walks `examples/*/cases.toml`
    rather than a legacy stop-at-`53` boundary.
- Canonical path / owner to reuse:
  - `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`,
    `doctrine/model.py`, `doctrine/compiler.py`, and `doctrine/renderer.py` —
    the one implementation path that must own any remaining Phase 1 work.
  - `examples/*/cases.toml` plus `doctrine/verify_corpus.py` — the one proof
    path; do not create a separate parity harness.
- Existing patterns to reuse:
  - `doctrine/compiler.py` — fail-loud `CompileError` style for readable and
    enum validation; extend this style instead of inventing tolerant fallbacks.
  - `examples/56_document_structure_attachments` through
    `examples/61_multiline_code_and_readable_failures` — one-new-idea-per-example
    proof ladder with positive and compile-negative coverage.
  - `editors/vscode/README.md` plus the extension build/test path — editor
    parity rides the shipped grammar and example corpus rather than a separate
    grammar truth.
- Prompt surfaces / agent contract to reuse:
  - `AGENTS.md` — repo-level rules for verification, shipped truth, and how
    docs must yield to `doctrine/` plus manifest-backed proof.
  - `docs/archive/PHASE1_TYPED_MARKDOWN_COMPLETION_PARITY_PLAN_2026-04-11.md` — the
    canonical full-arch artifact; no second execution checklist should emerge.
- Native model or agent capabilities to lean on:
  - Codex runtime with `codex_hooks` and the installed `arch-step` stop-hook
    controller — enough to keep one `DOC_PATH`, one planning arc, and one final
    handoff without extra orchestration code in the repo.
- Existing grounding / tool / file exposure:
  - repo-wide read access through `rg`, `sed`, manifests, live docs, and the
    stop-hook/controller surfaces already installed under `~/.agents/skills/arch-step/`.
- Duplicate or drifting paths relevant to this change:
  - `AGENTS.md` and `docs/LANGUAGE_DESIGN_NOTES.md` — still claim the shipped
    corpus stops at `examples/53_review_bound_carrier_roots`.
  - `docs/archive/second_wave/DOCTRINE_READABLE_MARKDOWN_FULL_IMPLEMENTATION_2026-04-11.md` —
    still carries a `NOT COMPLETE` audit block that conflicts with its later
    worklog and with the newer `56` through `61` proof wave.
  - `docs/LANGUAGE_REFERENCE.md` — already documents most readable/document
    behavior, but does not yet act as an honest Phase 1 truth surface for the
    explicit concrete-agent and enum `wire` identity split.
- Capability-first opportunities before new tooling:
  - existing corpus search plus the shipped readable/document manifests can
    settle whether any non-identity Phase 1 gap remains without new machinery.
  - the current grammar/parser/model/compiler path can own the remaining
    identity work directly; no wrapper parser, no shadow renderer, no parity
    harness.
  - the current plan artifact and auto-plan controller already provide the
    needed project-management surface; no second planning doc should be created.
- Behavior-preservation signals already available:
  - `make verify-examples` — repo-wide preservation for the shipped corpus.
  - targeted manifests under `examples/56_*`, `58_*`, `59_*`, `60_*`, and
    `61_*` — focused readable/document proof.
  - `make verify-diagnostics` — only if new identity or readable diagnostics
    move.
  - `cd editors/vscode && make` — only if editor files change.

## 3.3 Open questions from research

- Do any readable/document semantics from `docs/01_*` remain missing beyond the
  identity slice — settle this with the line-item parity matrix plus the shipped
  `56` through `61` manifests and renderer/compiler anchors.
- Which existing example should carry the missing concrete-agent-title and enum
  `wire` proof, or does Phase 1 need one new narrow manifest-backed identity
  example — settle this with a corpus search against the current examples and
  the "one new idea per example" rule.
- Should the broader readable-markdown implementation doc be repaired in place,
  folded into historical context, or left active with rewritten status text —
  settle this after Section 7 decides whether any live execution checklist
  remains outside this plan.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- Phase source boundary: `docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md`
- Broader readable-markdown context:
  `docs/archive/second_wave/DOCTRINE_READABLE_MARKDOWN_FULL_IMPLEMENTATION_2026-04-11.md` and
  `_WORKLOG.md`
- Shipped implementation path for the readable/document wave:
  `doctrine/grammars/doctrine.lark`, `doctrine/model.py`, `doctrine/parser.py`,
  `doctrine/compiler.py`, `doctrine/renderer.py`
- Proof and teaching surfaces for the readable/document wave:
  `examples/README.md`, `examples/56_*`, `examples/58_*`, `examples/59_*`,
  `examples/60_*`, `examples/61_*`
- Earlier identity-adjacent proof surfaces:
  `examples/29_enums` plus older title/interpolation examples, which prove
  generic enum and addressability behavior but do not yet show explicit Phase 1
  concrete-agent head titles or enum-member `wire:` values
- Editor truth surfaces: `editors/vscode/README.md` and the extension build/test
  path

## 4.2 Control paths (runtime)

- `make verify-examples` runs `uv run --locked python -m doctrine.verify_corpus`,
  which defaults to every `examples/*/cases.toml` manifest.
- Readable/document behavior compiles through the current `doctrine/compiler.py`
  path and renders through `doctrine/renderer.py`; there is no second renderer
  or document-specific backend.
- Enum-member semantics still flow through the older `key/value` path in
  `doctrine/compiler.py`, where enum resolution returns `member.value` and no
  explicit `wire:` branch exists.
- Editor parity and packaging prove through `cd editors/vscode && make` when the
  VS Code surface changes.

## 4.3 Object model + key abstractions

- Readable/document path that is already landed:
  - `DocumentDecl` in `doctrine/model.py`
  - input/output `structure:` configs in `doctrine/model.py`
  - readable block parsing and overrides in `doctrine/parser.py`
  - compiled readable/document resolution and validation in
    `doctrine/compiler.py`
  - markdown-native block rendering in `doctrine/renderer.py`
- Identity path that still predates the Phase 1 source doc:
  - `Agent` in `doctrine/model.py` stores `name`, `fields`, `abstract`, and
    `parent_ref`, but no human-facing title
  - `EnumMember` stores only `key` and `value`
  - grammar and parser expose enum members as one authored string value, not as
    explicit `title` plus optional `wire`
  - interpolation and enum-resolution logic still treat the member's single
    value as the externally visible text

## 4.4 Observability + failure behavior today

- Compiler failures are fail loud for readable/document behavior; current
  diagnostics already cover duplicate enum member keys, readable table column
  requirements, unknown callout kinds, override kind mismatches, and multiline
  code enforcement.
- The missing observability on the identity side is structural, not just
  textual: there is no current wire-specific validation surface for duplicate
  enum wire values, illegal `wire:` placement, or invalid `:wire` projections
  because the shipped grammar/model path does not own those semantics yet.
- Manifest-backed corpus verification and diagnostics smoke already exist.
- The other major observability failure is truth drift: active docs and
  instructions can disagree about what has shipped even when code and proof are
  green.

## 4.5 UI surfaces (ASCII mockups, if UI work)

No product UI is in scope. The human-facing surfaces are rendered markdown and
the VS Code extension.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- This doc remains the canonical Phase 1 completion artifact and the one
  authoritative execution checklist.
- `docs/01_*` remains the requested behavior boundary.
- `doctrine/` stays the only implementation owner path for both the already
  landed readable/document work and the still-missing identity slice.
- Live docs, instructions, examples, and overlapping readable-markdown plan
  artifacts are updated or folded so they reflect one final Phase 1 truth.

## 5.2 Control paths (future)

- One parity matrix maps every `docs/01_*` obligation to one of two states:
  shipped-and-proved, or still requiring implementation/proof.
- Readable/document behavior stays on the existing grammar -> parser -> model ->
  compiler -> renderer path with no wrapper and no shadow renderer.
- Any remaining identity work lands on the same canonical path:
  - concrete `agent` heads gain an optional authored title
  - enum members move from a single authored value to explicit structural key
    plus human-facing title plus optional external `wire`
  - one-line enum member shorthand remains legal as `title == wire`
  - `:title`, `:key`, and enum `:wire` projections resolve through the existing
    addressability/interpolation machinery rather than through bespoke helper
    code
- Final completion proof runs through the existing repo verification commands,
  with one narrow identity manifest added or repurposed only if the current
  corpus truly lacks that proof.

## 5.3 Object model + abstractions (future)

- Reuse the shipped readable/document abstractions as-is unless the parity audit
  finds a specific defect in them.
- Extend the current identity model rather than adding a second one:
  - `Agent` should expose optional human-facing title metadata on concrete heads
  - `EnumMember` should expose explicit title and wire semantics while keeping
    the stable member key as structural identity
  - existing interpolation/addressability logic should remain the one SSOT for
    all title/key/wire projections
- Validation remains fail loud:
  - duplicate enum `wire` values fail
  - `wire:` remains legal only on enum members
  - invalid `:wire` projections fail
  - title-bearing projections only resolve on surfaces that actually own them

## 5.4 Invariants and boundaries

- `docs/01_*` defines requested behavior scope for this plan.
- No new readable sublanguage, no shadow renderer, no compatibility shim, and
  no identity wrapper layer.
- The readable/document wave stays preserved while the identity slice lands on
  the same owner path.
- Active status surfaces must match the best current verification evidence.
- Historical context may stay in worklogs or archived docs, not in stale active
  completion claims.

## 5.5 UI surfaces (ASCII mockups, if UI work)

No product UI work. Editor help, grammar support, and rendered markdown examples
must stay aligned with the final shipped syntax and proof surface.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Phase 1 source boundary | `docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md` | whole document | Defines full Phase 1 scope, including readable/document and title/key/wire identity work, but does not classify what is already shipped | Build the line-item parity matrix and keep this doc as the scope boundary | The user asked to finish exactly this doc without scope cuts | No new API; this remains the parity boundary | Targeted Phase 1 manifests plus full corpus |
| Readable/document grammar + parser | `doctrine/grammars/doctrine.lark`, `doctrine/parser.py` | `document_decl`, `readable_*_block`, `input_structure_stmt`, `output_structure_stmt`, `MULTILINE_STRING` | Shipped on the canonical path for `document`, block kinds, `structure:`, and multiline strings | Preserve as-is unless the parity matrix finds a real readable/document defect | Avoid re-implementing already-landed work | Same grammar/parser path remains SSOT | `examples/56_*`, `58_*`, `59_*`, `60_*`, `61_*`, full corpus |
| Identity syntax + data model | `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, `doctrine/model.py` | `agent`, `enum_decl`, `enum_member`, `Agent`, `EnumMember` | Concrete agents have no head-title slot; enum members are still `key/value`; no explicit `wire:` syntax exists | Add the missing Phase 1 identity surfaces through the same owner path if the parity audit confirms this gap | `docs/01_*` explicitly owns concrete-agent titles and enum `wire` semantics | One declaration/addressability model; no shadow identity layer | Targeted identity manifest, full corpus |
| Identity resolution + validation | `doctrine/compiler.py`, `doctrine/diagnostics.py` | enum resolution, interpolation/projection validation, duplicate checks | Enum resolution returns `member.value`; diagnostics cover duplicate enum keys but not duplicate wire values, illegal `wire:` placement, or invalid `:wire` projection | Extend the current resolver and fail-loud diagnostics for `:title`, `:key`, and enum `:wire` semantics | Finish the missing Phase 1 identity slice without changing owner path | Same compiler/interpolation path remains SSOT | Targeted identity manifest, `make verify-diagnostics` if touched, full corpus |
| Readable/document proof ladder | `examples/56_document_structure_attachments/cases.toml`, `examples/58_readable_document_blocks/cases.toml`, `examples/59_document_inheritance_and_descendants/cases.toml`, `examples/60_shared_readable_bodies/cases.toml`, `examples/61_multiline_code_and_readable_failures/cases.toml` | manifest-backed proof | Already proves the readable/document wave, including compile-negative failures | Preserve and only extend if the parity matrix finds a real readable/document miss | These are the current preservation signals for the landed half of Phase 1 | One proof ladder, no replacement ladder | Targeted manifest runs, `make verify-examples` |
| Phase 1 identity proof | `examples/29_enums/cases.toml` and `examples/*` (one narrow new identity example only if needed) | manifest-backed proof for titles / wire / projections | Current corpus proves enum basics and general title interpolation, but not explicit concrete-agent head titles or enum-member `wire` splits | Reuse an existing example if honest; otherwise add one narrow manifest-backed example for agent titles, enum `:key`, enum `:wire`, duplicate wire, and invalid `:wire` | `docs/01_*` requires proof, not just implementation claims | One narrow identity proof surface adjacent to the shipped corpus | Targeted identity manifest, `make verify-examples` |
| Live docs + instructions | `AGENTS.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/README.md`, `examples/README.md`, `docs/COMPILER_ERRORS.md` | shipped boundary statements, language reference, error catalog | `AGENTS.md` and `docs/LANGUAGE_DESIGN_NOTES.md` still stop at `53`; `docs/LANGUAGE_REFERENCE.md` is ahead on readable/document behavior but not yet an honest source for the full Phase 1 identity split | Rewrite the surviving docs to match final shipped proof and diagnostics | Phase 1 cannot close with split truth | Live docs must follow shipped code + manifests | Re-run any cited check; manual doc audit |
| Overlapping readable-markdown plan state | `docs/archive/second_wave/DOCTRINE_READABLE_MARKDOWN_FULL_IMPLEMENTATION_2026-04-11.md`, `docs/archive/second_wave/DOCTRINE_READABLE_MARKDOWN_FULL_IMPLEMENTATION_2026-04-11_WORKLOG.md` | active status blocks vs worklog evidence | Active doc still says `NOT COMPLETE` while the worklog records repeated green editor verification and shipped post-`57` proof | Repair the active status or demote/fold the doc so it no longer competes with this plan | One active completion narrative is required | One live completion story | Re-run any proof signal restated as green |
| Editor parity | `editors/vscode/README.md`, `editors/vscode/resolver.js`, `editors/vscode/syntaxes/doctrine.tmLanguage.json`, `editors/vscode/language-configuration.json`, `editors/vscode/tests/**` | syntax, resolver, smoke guidance | Readable/document examples are already referenced, but any new agent-title or enum `wire` syntax would require matching editor support | Update editor syntax/resolver/tests only if the implementation adds new shipped grammar | Editor behavior must mirror compiler truth | One editor grammar/resolver path | `cd editors/vscode && make` if touched |

## 6.2 Migration notes

* Canonical owner path / shared code path:
  `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`,
  `doctrine/model.py`, `doctrine/compiler.py`, `doctrine/renderer.py`,
  `doctrine/verify_corpus.py`, and manifest-backed `examples/*/cases.toml`.
* Deprecated APIs (if any):
  none at runtime; the deprecations here are stale truth surfaces, not public
  code APIs.
* Delete list (what must be removed; include superseded shims/parallel paths if any):
  stale stop-at-`53` claims in `AGENTS.md` and `docs/LANGUAGE_DESIGN_NOTES.md`,
  any surviving `NOT COMPLETE` block or stale editor-red claim in the active
  readable-markdown implementation doc, and any temporary parity-only example or
  note if a cleaner canonical proof surface replaces it.
* Capability-replacing harnesses to delete or justify:
  do not add a parity harness, wrapper parser, shadow renderer, or helper layer
  for title/key/wire projections; the current compiler path should own them.
* Live docs/comments/instructions to update or delete:
  `AGENTS.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/README.md`, `examples/README.md`, `docs/COMPILER_ERRORS.md`,
  `editors/vscode/README.md`, and the broader readable-markdown implementation
  doc if it remains live.
* Behavior-preservation signals for refactors:
  `make verify-examples`, targeted `56` through `61` manifests, targeted
  identity manifests, `make verify-diagnostics` when diagnostics move, and
  `cd editors/vscode && make` when editor files move.

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Readable/document implementation | `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, `doctrine/compiler.py`, `doctrine/renderer.py` | one canonical readable/document owner path | prevents a second readable or document renderer story | include |
| Identity metadata | `Agent`, `EnumMember`, interpolation/resolution code in `doctrine/compiler.py` | title/key/wire semantics through the existing addressability path | prevents one-off enum or agent special cases | include |
| Proof ladder | `examples/56_*` through `61_*` plus one narrow identity manifest if required | one-new-idea-per-example, manifest-backed proof | prevents docs-only completion claims and duplicate ladders | include |
| Live truth surfaces | `AGENTS.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/LANGUAGE_REFERENCE.md`, readable-markdown implementation docs | one shipped boundary and one active completion story | prevents stale truth and contradictory status narratives | include |
| New planning or parity machinery | any new checker, wrapper, or parallel checklist | no extra harness when code + manifests already settle truth | avoids architecture theater and controller sprawl | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:reference_pack:start -->
# Reference Pack (folded materials; phase-aligned)
Updated: 2026-04-11

## Inventory
- R1 — Phase 1 Typed Markdown Foundation And Document System — `docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md`
- R2 — Examples Readme And Proof Rules — `examples/README.md`
- R3 — Example 56 Document Structure Attachments — `examples/56_document_structure_attachments/`
- R4 — Example 58 Readable Document Blocks — `examples/58_readable_document_blocks/`
- R5 — Example 59 Document Inheritance And Descendants — `examples/59_document_inheritance_and_descendants/`
- R6 — Example 60 Shared Readable Bodies — `examples/60_shared_readable_bodies/`
- R7 — Example 61 Multiline Code And Readable Failures — `examples/61_multiline_code_and_readable_failures/`

## Binding obligations (distilled; must satisfy)
- Phase 1 completion must stay inside the exact boundary from R1: typed markdown block model, first-class `document`, shared readable block family, multiline strings, typed `structure:` attachments, title/key/wire identity surfaces, block-dispatch rendering, document addressability, inheritance, validation, and proof. Later-phase surfaces named in R1 remain out of scope here. (From: R1)
- The unfinished post-`53` proof wave for this plan must explicitly cover the R1 proof-ladder territory that maps to document/readable work: `structure:` attachments, rich readable blocks, document inheritance and descendant refs, shared readable bodies, multiline code, and compile-negative readable validation. (From: R1, R3, R4, R5, R6, R7)
- `structure:` must stay typed, document-only, and markdown-bearing; non-markdown output attachments must keep failing loud. (From: R1, R3)
- Non-section readable blocks must keep their markdown-native rendering contract rather than collapsing back into titled heading shells. (From: R1, R4, R6, R7)
- Document inheritance must preserve explicit accounting and block-kind invariance, and keyed descendants must remain addressable through inherited documents. (From: R1, R5)
- Shared readable blocks are not document-only in the Phase 1 design; parity work must account for workflow, skill-entry, and output-body reuse where that shared model is part of the shipped readable surface. (From: R1, R6)
- The fail-loud readable validation set folded into unfinished work includes at least: non-markdown `structure:` misuse, document override kind mismatch, unknown `callout.kind`, duplicate document block keys, readable guards reading disallowed output-owned refs, tables without columns, and code blocks without multiline string text. (From: R1, R3, R5, R7)
- Manifests are the proof surface. Checked-in refs alone are not proof, and docs must yield to `doctrine/` plus manifest-backed cases when they disagree. (From: R2)
- Example additions or repairs should keep the "one new idea per example" discipline, so any remaining proof follow-through should prefer repairing or clarifying the current `56` through `61` ladder instead of inventing a broad replacement ladder without need. (From: R2, R3, R4, R5, R6, R7)
- The parity audit still has to account for all of R1, including title-bearing identity surfaces, even though the unfinished example wave folded here is centered on the document/readable portion. Existing earlier proof may satisfy those identity obligations, but the audit must classify them explicitly instead of letting them disappear. (From: R1)

## Instruction-bearing structure (only when present; preserve exact or equivalent operational form)
### R1 — Phase 1 Typed Markdown Foundation And Document System
1. Keep the Phase 1 ownership boundary exact:
   - typed markdown block model
   - first-class `document`
   - shared readable block family
   - multiline strings
   - `structure:` on markdown-bearing inputs and outputs
   - title-bearing identity surfaces and explicit `:title`, `:key`, `:wire`
   - renderer conversion from section-only recursion to block dispatch
   - document addressability, inheritance, validation, and proof
2. Preserve the core design constraints:
   - Doctrine owns structure and rendering semantics.
   - Keys are law. Titles are prose.
   - one readable renderer path
   - one compiled block union
   - no shadow document renderer
3. Preserve the proof and implementation order structure:
   - positive ladder from identity surfaces through multiline code
   - compile-negative ladder for the readable/document failure set
   - exact implementation order from identity metadata through proof landing
- Hard negatives:
  - do not pull `analysis`, `schema`, owner-aware `schema:`, review integration,
    `route_only`, `grounding`, or authored render profiles into Phase 1
  - do not allow `wire:` outside enum members
  - do not weaken explicit-accounting inheritance or block-kind invariance
- Escalation or branch conditions:
  - if a discovered gap belongs to a later-phase excluded surface, record it as
    follow-up instead of promoting it into Phase 1 completion work

### R2 — Examples Readme And Proof Rules
1. Read the examples in numeric order; the sequence is intentional.
2. Treat the manifest as the proof surface.
3. If docs and examples disagree, trust `doctrine/` and the manifest-backed
   cases.
4. Keep new examples narrow; one new idea per example is the design rule.
5. Keep verification scalable without changing manifest order or emitted
   language.
- Hard negatives:
  - do not mistake checked-in refs for proof on their own
  - do not bundle multiple new ideas into one example unless the reference pack
    later records why
- Escalation or branch conditions:
  - if unfinished work needs more proof, prefer the existing `56` through `61`
    ladder unless a real uncovered Phase 1 obligation forces another example

## Phase alignment guidance (advisory; core planning commands adopt into Section 7 if needed)
### Global (applies across phases)
- Keep the Phase 1 boundary exact and preserve the R1 invariants around one
  readable path, fail-loud validation, and keys-vs-titles law. (From: R1)
- Treat `examples/56_*` through `examples/61_*` as the folded post-`53`
  readable/document proof wave for unfinished work, and treat manifests as the
  authoritative proof surface. (From: R2, R3, R4, R5, R6, R7)
- Keep the unfinished-work audit explicit about whether title-bearing identity
  surfaces are already proved elsewhere or still need parity follow-through.
  (From: R1)

### Phase 1 — Baseline Phase 1 parity audit
- Potentially relevant obligations (advisory):
  - classify every R1 surface explicitly, including the identity-surface items
    not covered by the folded post-`53` example wave (From: R1)
  - map the unfinished readable/document proof ladder to the current examples:
    `56` for typed `structure:`, `58` for rich document blocks, `59` for
    inheritance and descendants, `60` for shared readable bodies, `61` for
    multiline code and readable failures (From: R3, R4, R5, R6, R7)
  - use R2's proof rules when deciding whether a claimed surface is already
    shipped-and-proved or only described in docs (From: R2)
- References:
  - R1, R2, R3, R4, R5, R6, R7

### Phase 2 — Remaining code and proof closure
- Potentially relevant obligations (advisory):
  - if `structure:` behavior is incomplete, keep it document-only and
    markdown-bearing, and preserve the non-markdown compile fail (From: R1, R3)
  - if rich rendering is incomplete, preserve markdown-native forms for
    callouts, definitions, tables, checklists, code, and rules (From: R1, R4, R6, R7)
  - if inheritance or descendant resolution is incomplete, preserve explicit
    accounting and descendant addressability through inherited documents (From: R1, R5)
  - if validation gaps remain, close them through the fail-loud readable
    failure set already described by R1, R3, R5, and R7 rather than inventing a
    different validation story (From: R1, R3, R5, R7)
- References:
  - R1, R3, R4, R5, R6, R7

### Phase 3 — Live truth convergence
- Potentially relevant obligations (advisory):
  - keep live docs and instructions aligned with the current post-`53`
    readable/document proof wave and the "manifests are proof" rule (From: R2, R3, R4, R5, R6, R7)
  - keep Phase 1 truth narrow enough that later-phase exclusions from R1 do not
    get reintroduced during docs cleanup (From: R1)
- References:
  - R1, R2, R3, R4, R5, R6, R7

### Phase 4 — Final Phase 1 closeout
- Potentially relevant obligations (advisory):
  - use the repo-wide verify surface plus the current readable/document manifest
    ladder to support the final completion claim (From: R2, R3, R4, R5, R6, R7)
- References:
  - R2, R3, R4, R5, R6, R7

## Folded sources (verbatim; inlined so they cannot be missed)
### R1 — Phase 1 Typed Markdown Foundation And Document System — `docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md`
~~~~markdown
---
title: "Doctrine Phase 1 - Typed Markdown Foundation And Document System"
status: active
doc_type: phased_plan
phase: 1
---

# Phase 1 - Typed Markdown Foundation And Document System

## Summary

Phase 1 builds the readable-output foundation that every later phase relies on.
It replaces the heading-only readable tree with a typed markdown block system,
ships first-class `document`, adds multiline strings, makes markdown-bearing
contracts point at named document structures through `structure:`, and locks the
base key-versus-title identity model that later control-plane surfaces rely on
for human-readable owner and mode names.

This phase exists to solve a structural problem, not a cosmetic one. Doctrine
already renders readable content, but today rich semantic differences collapse
into heading depth. The goal of this phase is to make structure explicit in the
language and preserve natural rendered Markdown without forcing every readable
surface into nested heading shells.

## Phase Boundary

This phase owns:

- the typed markdown block model
- first-class `document`
- the shared readable block family
- multiline strings
- `structure:` on markdown-bearing inputs and outputs
- title-bearing identity surfaces for concrete agents and enum members
- explicit identity projections such as `:title`, `:key`, and enum `:wire`
- the renderer conversion from section-only recursion to block dispatch
- document addressability, inheritance, validation, and proof

This phase does not own:

- `analysis`
- `schema`
- owner-aware `schema:`
- review integration
- `route_only`
- `grounding`
- authored render profiles

Those come later, but this phase must leave a stable block IR and renderer path
that later phases can reuse without redesign.

## Assumed Baseline

Baseline before phase 1:

- Doctrine already ships readable declarations and output contracts.
- Existing keyed sections, emphasized prose lines, and rendered Markdown remain
  legal and must stay backward compatible.
- Existing addressability, explicit inheritance accounting, and fail-loud
  diagnostics remain the governing language style.
- Existing untitled agents and one-string enum members remain legal migration
  forms until later cleanup passes remove the shorthand.

## Core Decision

Doctrine should render readable output from semantic block kinds rather than
from heading depth alone.

The phase therefore introduces:

- a first-class `document` declaration
- a shared readable block family
- a richer compiled readable block union
- renderer dispatch based on block kind

The governing boundary is:

- Doctrine owns structure and rendering semantics.
- Domain packs own document names, required blocks, table names, and domain
  column meanings.

Keys are law. Titles are prose.

## Surfaces Owned By Phase 1

### Top-level declaration

```prompt
document LessonPlan: "Lesson Plan"
    ...
```

`document` is a named, addressable, inheritable schema for a markdown artifact.
It describes readable structure, not workflow control flow.

### Shared readable block family

Phase 1 ships these block kinds:

- `section`
- `sequence`
- `bullets`
- `checklist`
- `definitions`
- `table`
- `callout`
- `code`
- `rule`

Every renderable block has a stable symbolic key separate from its title.

### Attachment field

```prompt
structure: LessonPlan
```

`structure:` attaches a named `document` to a markdown-bearing `input` or
`output`.

### Multiline strings

Phase 1 adds a general multiline string literal to Doctrine. The primary use
case is `code.text`, but the feature belongs to the language core rather than
to a one-off code-block exception.

### Title-bearing identity surfaces

Phase 1 also makes the "keys are law, titles are prose" rule apply directly to
the human-facing identities that later phases need to render cleanly.

Canonical forms:

```prompt
agent ProjectLead: "Project Lead"
    role: "Own blocked follow-up and unresolved route repair."

enum NextOwner: "Next Owner"
    section_author: "Section Author"
        wire: "section-author"

    copy_editor: "Copy Editor"
        wire: "copy-editor"
```

Rules:

- a concrete `agent` may declare a human-facing title in its declaration head
- the declaration key remains the structural identity used by inheritance,
  routing, and patching
- enum members gain the same key-versus-title split as other titled surfaces
- enum members may additionally declare `wire:` for host-facing or external
  serialized values
- one-line enum member form remains legal as shorthand for `title == wire`
- authored prose and later `properties` bodies default `{{Ref}}` to the
  human-facing title when the target exposes one
- `:key` remains available when a machine-oriented or debugging surface needs
  the structural identity explicitly
- enum members additionally expose `:wire` when the external serialized value
  must be shown explicitly

## Surface Syntax

### Canonical `document` form

```prompt
document LessonPlan: "Lesson Plan"
    callout durable_truth: "Durable Truth" advisory
        kind: important
        "This file owns the lesson job, pacing, and stable-vs-variable boundaries."

    section lesson_promise: "Lesson Promise" required
        "State what this lesson owns now."

    sequence step_order: "Step Order" required
        first: "Read the active issue."
        second: "Read the current issue plan."
        third: "Read the latest current comment."

    definitions step_roles: "Step Roles" required
        introduce: "Introduce"
            "Name what each step is doing using `introduce`."
        practice: "Practice"
            "Name what each step is doing using `practice`."

    table step_arc: "Step Arc Table" required
        columns:
            step: "Step"
                "Step identifier or ordinal."
            role: "Role"
                "The step role."
            introduces: "Introduces"
                "What is genuinely introduced here."
        notes:
            "Add one row per step."

    code example_manifest: "Example Manifest" advisory
        language: json
        text: """
        {
          "title": "PLACEHOLDER: Lesson title",
          "steps": []
        }
        """

    rule section_break
```

### Common block header

All document blocks share this header shape:

```text
<block_kind> <key>: "Title" <requirement>? <guard>?
```

Requirement values:

- `required`
- `advisory`
- `optional`

Guard form:

- `when <expr>`

### Block-specific rules

`section`

- heading plus block body
- body may contain any readable block

`sequence`

- ordered list
- keyed items are recommended because they remain addressable
- authored order is preserved

`bullets`

- unordered list
- keyed items remain the canonical style when addressability matters

`checklist`

- markdown task-list output
- used for operator checklists and contract readbacks

`definitions`

- compact labeled term/explanation rows
- clean replacement for repeated heading ladders such as "Must Include"

`table`

- ordered, keyed columns
- optional keyed rows
- column bodies serve as contract descriptions when no concrete rows are
  present
- row cells stay inline markdown in this phase

`callout`

- blockquote-style admonition
- allowed kinds in phase 1:
  - `required`
  - `important`
  - `warning`
  - `note`

`code`

- fenced code block
- optional `language`
- `text` must use multiline string form

`rule`

- thematic break rendered as `---`

## `structure:` On Inputs And Outputs

Markdown-bearing contracts may attach a named document structure.

Input example:

```prompt
input LessonPlanContract: "Lesson Plan"
    source: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: MarkdownDocument
    structure: LessonPlan
    requirement: Required
```

Output example:

```prompt
output LessonPlanFileOutput: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: AgentOutputDocument
    structure: LessonPlan
    requirement: Required
```

Rules:

- `structure:` must resolve to a `document`
- `structure:` is descriptive and typed, not a prose convention
- `structure:` may appear on `input` and `output`
- `structure:` requires a markdown-bearing shape such as `MarkdownDocument` or
  `AgentOutputDocument`

## Addressability And Symbolic Identity

Document roots and keyed descendants are addressable through the standard path
discipline.

Examples:

```text
{{LessonPlan:title}}
{{LessonPlan:step_arc.title}}
{{LessonPlan:step_arc.columns.role.title}}
{{LessonPlan:step_arc.columns.role}}
{{ProjectLead}}
{{ProjectLead:key}}
{{NextOwner.section_author}}
{{NextOwner.section_author:key}}
{{NextOwner.section_author:wire}}
```

Addressability rules:

- document root is addressable
- title-bearing concrete agent roots are addressable for identity projection
- enum roots are addressable
- enum members are addressable
- keyed block children are addressable
- table columns are addressable
- table rows are addressable when present
- keyed list items are addressable
- keyed definition items are addressable
- anonymous list items are legal but not addressable
- `:title` resolves when the target owns a human-facing title
- `:key` resolves for title-bearing declaration and enum-member identities
- `:wire` resolves only for enum members that declare or inherit a wire value

## Inheritance And Patching

Document inheritance follows Doctrine's explicit-accounting style.

Example:

```prompt
document BaseLessonPlan: "Lesson Plan"
    section lesson_promise: "Lesson Promise" required
        "State what this lesson owns now."

    table step_arc: "Step Arc Table" required
        columns:
            step: "Step"
            role: "Role"

document WalkthroughLessonPlan[BaseLessonPlan]: "Lesson Plan"
    inherit lesson_promise
    inherit step_arc

    table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" required
        columns:
            lesson: "Lesson"
            beat_count: "Beat Count"
            target_count: "Target Count"
            variance_reason: "Variance Reason"
```

Rules:

- inherited document blocks must be explicitly accounted for
- `override` may replace title, body, or both
- block kind is invariant under override
- missing inherited block accounting is a compile error
- duplicate accounting is a compile error

## Guards And Backward Compatibility

### Guards

Document blocks support `when <expr>`.

Example:

```prompt
table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" required when LessonFacts.walkthrough_in_scope
    columns:
        lesson: "Lesson"
        beat_count: "Beat Count"
```

Rules:

- guard syntax reuses Doctrine's existing expression language
- contract render mode emits guarded shells, not runtime evaluation
- document guards obey the same source restrictions as guarded output sections

### Backward compatibility

Existing authored keyed sections remain legal and compile as semantic `section`
blocks. Existing emphasized prose lines remain legal and keep their current
render behavior unless a prompt explicitly rewrites them as `callout`.

Existing untitled concrete agents remain legal. Existing one-line enum members
remain legal and continue to expose one authored string that acts as both title
and wire value until the prompt is upgraded to the explicit split form.

## Render And Readback Rules

Only `section` consumes heading depth. Every other readable block keeps its own
markdown syntax.

Examples:

`section`

```markdown
### Lesson Promise

_Required · section_

State what this lesson owns now.
```

`sequence`

```markdown
### Step Order

_Required · ordered list_

1. Read the active issue.
2. Read the current issue plan.
3. Read the latest current comment.
```

`definitions`

```markdown
#### Must Include

_Required · definitions_

- **Verdict** - Say `accept` or `changes requested`.
- **Reviewed Artifact** - Name the reviewed artifact this review judged.
```

`table`

```markdown
### Step Arc Table

_Required · table_

| Column | Meaning |
| --- | --- |
| Step | Step identifier or ordinal. |
| Role | The step role. |
| Introduces | What is genuinely introduced here. |
```

`callout`

```markdown
> **IMPORTANT - Durable Truth**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.
```

`code`

````markdown
#### Example Manifest

_Advisory · code · json_

```json
{
  "title": "PLACEHOLDER: Lesson title",
  "steps": []
}
```
````

Identity projection in authored prose

```markdown
If the route is still unclear, Project Lead keeps the issue.

When next owner is Section Author, hand the same issue to Section Author.

Debug owner key: `ProjectLead`
Wire value: `section-author`
```

## Validation, Diagnostics, And Invariants

These rules fail loud in phase 1:

- `structure:` must resolve to a `document`
- document block keys must be unique
- inherited document blocks must be explicitly accounted for
- `override` must target an existing inherited key
- `override` must preserve block kind
- table must have columns
- column keys must be unique
- rows may reference only declared columns
- row keys must be unique
- cells must stay inline markdown in this phase
- keyed items must be unique within list and definitions blocks
- `callout.kind` must be in the closed core set
- `code.text` must use multiline string form
- guard expressions must obey existing guarded-output restrictions
- title-bearing identity projections must target surfaces that actually expose
  them
- enum member `wire` values must be unique within the owning enum
- `wire:` is legal only on enum members
- title-bearing concrete-agent heads and enum-member heads must preserve one
  stable structural key plus one optional human-facing title

Phase invariants:

- one readable renderer path
- one compiled block union
- no shadow document renderer
- keys remain stable symbolic law
- titles remain prose
- wire values remain host-facing codecs, not structural identities

## Compiler Touchpoints

Primary implementation surfaces:

- `doctrine/grammars/doctrine.lark`
- `doctrine/model.py`
- `doctrine/parser.py`
- `doctrine/compiler.py`
- `doctrine/renderer.py`

Required compiler changes:

- extend agent heads and enum members with title-bearing identity metadata
- add `document_decl`
- add readable block node types
- add multiline string literal support
- replace the `CompiledSection`-only readable tree with a richer block union
- compile `structure:` on markdown-bearing inputs and outputs
- compile title/key/wire identity projections alongside existing addressable
  refs
- compile document addressable roots
- replace section-only rendering with block dispatch

## Proof Plan

Positive ladder for phase 1:

1. title-bearing concrete agents in authored prose
2. titled enum members with explicit `wire:`
3. first-class `document`
4. rich blocks in output contracts
5. documents with tables and definitions
6. document inheritance
7. document guards
8. multiline strings and code blocks

Compile-negative ladder for phase 1:

- invalid identity projection such as `:wire` on a non-enum target
- duplicate enum wire value in one enum
- non-document `structure:` ref
- duplicate document block key
- document override kind mismatch
- table row references unknown column
- table without columns
- unknown `callout.kind`
- code block without multiline string

## Exact Implementation Order

1. Add title-bearing identity metadata for concrete-agent heads and enum
   members, including explicit `title`, `key`, and `wire` projections.
2. Add the typed markdown IR and compiled block union.
3. Add multiline strings to the core grammar and parser.
4. Add first-class `document` plus block parsing.
5. Compile document and identity addressable roots plus inheritance.
6. Add `structure:` resolution for markdown-bearing inputs and outputs.
7. Replace section-only rendering with block-dispatch rendering.
8. Land the positive and negative proof ladder for the document system and
   identity surfaces.
~~~~

### R2 — Examples Readme And Proof Rules — `examples/README.md`
~~~~markdown
# Examples

The examples are both the language teaching surface and the verification
corpus.
They are also the main proof that Doctrine stays deterministic and tractable as
prompt graphs grow, because the shipped verify and emit surfaces reuse shared
compile sessions while keeping manifest and output ordering stable.

Each numbered example may contain:

- `prompts/`: authored `.prompt` source
- `cases.toml`: manifest-backed proof used by `doctrine.verify_corpus`
- `ref/`: checked-in expected render or error output
- `build_ref/`: checked-in emitted tree output when the emit pipeline matters,
  including compiled Markdown trees and target-scoped `.flow.{d2,svg}`
  artifacts

## How To Read The Corpus

- Read the examples in numeric order. The sequence is intentional.
- The manifest is the proof surface. A checked-in ref file is not proof on its
  own.
- If docs and examples disagree, trust `doctrine/` and the manifest-backed
  cases.
- Keep new examples narrow. One new idea per example is the design rule.
- Batch verification and emit commands are expected to stay scalable on this
  corpus without changing emitted language or manifest order.

## Learning Paths

- `01` through `06`: core syntax, sections, imports, inheritance, and explicit
  workflow patching
- `07` through `29`: authored slots, routing, inputs, outputs, skills, refs,
  interpolation, reusable blocks, addressable paths, and enums
- `30` through `42`: workflow law, currentness, trust carriers, preservation,
  invalidation, guarded output sections, and route-only turns
- `43` through `49`: first-class `review`
- `50` through `53`: bound roots for workflow law and review carriers
- `54` through `61`: second-wave integration surfaces for `analysis`,
  owner-aware `schema:` / `structure:` attachments, readable markdown
  documents and descendants, shared readable block reuse, multiline code
  blocks, and schema-backed review contracts

## Corpus Index

| ID | Focus |
| --- | --- |
| `54_analysis_attachment` | Concrete-agent `analysis:` attachment and analysis-root addressability. |
| `55_owner_aware_schema_attachments` | Owner-aware split between `output shape.schema` and `output.schema`. |
| `56_document_structure_attachments` | Typed `structure:` attachments on markdown-bearing inputs and outputs. |
| `57_schema_review_contracts` | Schema-backed `review contract:` with exported schema gates. |
| `58_readable_document_blocks` | Rich readable document blocks render natively through `structure:`. |
| `59_document_inheritance_and_descendants` | Document inheritance plus keyed readable descendants on lists and tables. |
| `60_shared_readable_bodies` | Shared readable blocks on workflow sections, skill-entry bodies, and output bodies. |
| `61_multiline_code_and_readable_failures` | Multiline readable code blocks plus compile-negative readable validation. |

## Useful Commands

Verify the whole active corpus:

```bash
make verify-examples
```

Verify one example manifest:

```bash
uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml
```
~~~~

### R3 — Example 56 Document Structure Attachments — `examples/56_document_structure_attachments/`
~~~~markdown
FILE: examples/56_document_structure_attachments/cases.toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "document structure attachments render on markdown inputs and outputs"
status = "active"
kind = "render_contract"
agent = "LessonPlanStructureDemo"
assertion = "exact_lines"
approx_ref = "ref/lesson_plan_structure_demo/AGENTS.md"
expected_lines = [
  "Keep Overview and Sequence aligned in Lesson Plan.",
  "",
  "## Rewrite",
  "",
  "Use the shared document structure for both the current and next lesson plans.",
  "",
  "## Inputs",
  "",
  "### Current Lesson Plan",
  "",
  "- Source: File",
  "- Path: `lesson_root/CURRENT_LESSON_PLAN.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "- Structure: Lesson Plan",
  "",
  "#### Structure: Lesson Plan",
  "",
  "##### Overview",
  "",
  "Start with the plan overview.",
  "",
  "##### Sequence",
  "",
  "List the lesson steps in order.",
  "",
  "## Outputs",
  "",
  "### Next Lesson Plan",
  "",
  "- Target: File",
  "- Path: `lesson_root/NEXT_LESSON_PLAN.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "- Structure: Lesson Plan",
  "",
  "#### Structure: Lesson Plan",
  "",
  "##### Overview",
  "",
  "Start with the plan overview.",
  "",
  "##### Sequence",
  "",
  "List the lesson steps in order.",
]

[[cases]]
name = "output structure fails on non-markdown output shapes"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_NON_MARKDOWN_OUTPUT_STRUCTURE.prompt"
agent = "InvalidNonMarkdownOutputStructure"
exception_type = "CompileError"
error_code = "E299"
message_contains = [
  "Output structure requires a markdown-bearing shape",
  "InvalidCommentOutput",
]

FILE: examples/56_document_structure_attachments/prompts/AGENTS.prompt
# This example introduces typed `structure:` attachments on markdown-bearing
# inputs and outputs through a reusable `document`.

document LessonPlan: "Lesson Plan"
    section overview: "Overview"
        "Start with the plan overview."

    section sequence: "Sequence"
        "List the lesson steps in order."


input CurrentLessonPlan: "Current Lesson Plan"
    source: File
        path: "lesson_root/CURRENT_LESSON_PLAN.md"
    shape: MarkdownDocument
    structure: LessonPlan
    requirement: Required


output NextLessonPlan: "Next Lesson Plan"
    target: File
        path: "lesson_root/NEXT_LESSON_PLAN.md"
    shape: MarkdownDocument
    structure: LessonPlan
    requirement: Required


agent LessonPlanStructureDemo:
    role: "Keep {{LessonPlan:overview.title}} and {{LessonPlan:sequence.title}} aligned in {{LessonPlan:title}}."
    workflow: "Rewrite"
        "Use the shared document structure for both the current and next lesson plans."
    inputs: "Inputs"
        CurrentLessonPlan
    outputs: "Outputs"
        NextLessonPlan

FILE: examples/56_document_structure_attachments/prompts/INVALID_NON_MARKDOWN_OUTPUT_STRUCTURE.prompt
document LessonPlan: "Lesson Plan"
    section overview: "Overview"
        "Start with the plan overview."


output InvalidCommentOutput: "Invalid Comment Output"
    target: TurnResponse
    shape: Comment
    structure: LessonPlan
    requirement: Required


agent InvalidNonMarkdownOutputStructure:
    role: "This agent attaches structure to a non-markdown output."
    workflow: "Reply"
        "The workflow body is otherwise ordinary."
    outputs: "Outputs"
        InvalidCommentOutput
~~~~

### R4 — Example 58 Readable Document Blocks — `examples/58_readable_document_blocks/`
~~~~markdown
FILE: examples/58_readable_document_blocks/cases.toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "document structure renders callouts definitions tables checklists and rules natively"
status = "active"
kind = "render_contract"
agent = "ReleaseGuideDemo"
assertion = "exact_lines"
expected_lines = [
  "Keep Verdict and Evidence aligned in Release Guide.",
  "",
  "## Publish",
  "",
  "Write the release guide using the attached document structure.",
  "",
  "## Outputs",
  "",
  "### Release Guide File",
  "",
  "- Target: File",
  "- Path: `release_root/RELEASE_GUIDE.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "- Structure: Release Guide",
  "",
  "#### Structure: Release Guide",
  "",
  "> **IMPORTANT — Durable Truth**",
  "> _Required · callout_",
  "> This file owns the current release checklist.",
  "",
  "##### Summary",
  "",
  "Lead with the release goal and the current shipment boundary.",
  "",
  "##### Must Include",
  "",
  "_Required · definitions_",
  "",
  "- **Verdict** — Say whether the release is ready.",
  "- **Next Owner** — Name who owns the next action.",
  "",
  "##### Release Gates",
  "",
  "_Required · table_",
  "",
  "| Column | Meaning |",
  "| --- | --- |",
  "| Gate | What must pass before shipment. |",
  "| Evidence | What proves the gate passed. |",
  "",
  "List one row per release gate.",
  "",
  "##### Checks",
  "",
  "_Advisory · checklist_",
  "",
  "- [ ] Run lint.",
  "- [ ] Run tests.",
  "",
  "_rule_",
  "",
  "---",
]

FILE: examples/58_readable_document_blocks/prompts/AGENTS.prompt
# This example renders the richer document block kinds through `structure:`.

document ReleaseGuide: "Release Guide"
    callout durable_truth: "Durable Truth" required
        kind: important
        "This file owns the current release checklist."

    section summary: "Summary"
        "Lead with the release goal and the current shipment boundary."

    definitions must_include: "Must Include" required
        verdict: "Verdict"
            "Say whether the release is ready."

        next_owner: "Next Owner"
            "Name who owns the next action."

    table release_gates: "Release Gates" required
        columns:
            gate: "Gate"
                "What must pass before shipment."

            evidence: "Evidence"
                "What proves the gate passed."

        notes:
            "List one row per release gate."

    checklist checks: "Checks" advisory
        lint: "Run lint."
        tests: "Run tests."

    rule divider


output ReleaseGuideFile: "Release Guide File"
    target: File
        path: "release_root/RELEASE_GUIDE.md"
    shape: MarkdownDocument
    structure: ReleaseGuide
    requirement: Required


agent ReleaseGuideDemo:
    role: "Keep {{ReleaseGuide:must_include.verdict}} and {{ReleaseGuide:release_gates.columns.evidence.title}} aligned in {{ReleaseGuide:title}}."
    workflow: "Publish"
        "Write the release guide using the attached document structure."
    outputs: "Outputs"
        ReleaseGuideFile
~~~~

### R5 — Example 59 Document Inheritance And Descendants — `examples/59_document_inheritance_and_descendants/`
~~~~markdown
FILE: examples/59_document_inheritance_and_descendants/cases.toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "document inheritance keeps descendant refs addressable"
status = "active"
kind = "render_contract"
agent = "AdaptedLessonPlanDemo"
assertion = "exact_lines"
expected_lines = [
  "Keep Read the learner goal., Coaching Level, and Step 1 aligned in Adapted Lesson Plan.",
  "",
  "## Adapt",
  "",
  "Write the adapted lesson plan using the inherited document.",
  "",
  "## Outputs",
  "",
  "### Adapted Lesson Plan File",
  "",
  "- Target: File",
  "- Path: `lesson_root/ADAPTED_LESSON_PLAN.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "- Structure: Adapted Lesson Plan",
  "",
  "#### Structure: Adapted Lesson Plan",
  "",
  "##### Overview",
  "",
  "Start with the current lesson goal.",
  "",
  "##### Read Order",
  "",
  "_Advisory · ordered list_",
  "",
  "1. Read the learner goal.",
  "2. Read the current lesson plan.",
  "3. Read the prior feedback.",
  "",
  "##### Step Arc",
  "",
  "_Required · table_",
  "",
  "| Step | Coaching Level |",
  "| --- | --- |",
  "| 1 | High |",
]

[[cases]]
name = "document overrides fail when the child changes block kind"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_DOCUMENT_OVERRIDE_KIND_MISMATCH.prompt"
agent = "BrokenLessonPlanDemo"
exception_type = "CompileError"
error_code = "E299"
message_contains = [
  "Override kind mismatch for document entry",
  "read_order",
]

FILE: examples/59_document_inheritance_and_descendants/prompts/AGENTS.prompt
# This example shows document inheritance plus descendant refs on keyed items.

document LessonPlan: "Lesson Plan"
    section overview: "Overview"
        "Start with the current lesson goal."

    sequence read_order: "Read Order" required
        first: "Read the brief."
        second: "Read the current lesson plan."

    table step_arc: "Step Arc" required
        columns:
            step: "Step"
                "Step identifier."

            coaching_level: "Coaching Level"
                "How much help the step gives."

        rows:
            step_1:
                step: "1"
                coaching_level: "High"


document AdaptedLessonPlan[LessonPlan]: "Adapted Lesson Plan"
    inherit overview

    override sequence read_order: "Read Order" advisory
        first: "Read the learner goal."
        second: "Read the current lesson plan."
        third: "Read the prior feedback."

    inherit step_arc


output AdaptedLessonPlanFile: "Adapted Lesson Plan File"
    target: File
        path: "lesson_root/ADAPTED_LESSON_PLAN.md"
    shape: MarkdownDocument
    structure: AdaptedLessonPlan
    requirement: Required


agent AdaptedLessonPlanDemo:
    role: "Keep {{AdaptedLessonPlan:read_order.first}}, {{AdaptedLessonPlan:step_arc.columns.coaching_level.title}}, and {{AdaptedLessonPlan:step_arc.rows.step_1}} aligned in {{AdaptedLessonPlan:title}}."
    workflow: "Adapt"
        "Write the adapted lesson plan using the inherited document."
    outputs: "Outputs"
        AdaptedLessonPlanFile

FILE: examples/59_document_inheritance_and_descendants/prompts/INVALID_DOCUMENT_OVERRIDE_KIND_MISMATCH.prompt
document LessonPlan: "Lesson Plan"
    sequence read_order: "Read Order"
        first: "Read the brief."


document BrokenLessonPlan[LessonPlan]: "Broken Lesson Plan"
    override definitions read_order: "Read Order"
        first: "Read the brief."


output BrokenLessonPlanFile: "Broken Lesson Plan File"
    target: File
        path: "lesson_root/BROKEN_LESSON_PLAN.md"
    shape: MarkdownDocument
    structure: BrokenLessonPlan
    requirement: Required


agent BrokenLessonPlanDemo:
    role: "Compile the broken lesson plan."
    workflow: "Adapt"
        "This should fail."
    outputs: "Outputs"
        BrokenLessonPlanFile
~~~~

### R6 — Example 60 Shared Readable Bodies — `examples/60_shared_readable_bodies/`
~~~~markdown
FILE: examples/60_shared_readable_bodies/cases.toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "workflow skill entry and output bodies share the readable block model"
status = "active"
kind = "render_contract"
agent = "SharedReadableBodiesDemo"
assertion = "exact_lines"
expected_lines = [
  "Use Summary and Usage Note before you route the release.",
  "",
  "## Review",
  "",
  "### Summary",
  "",
  "#### Evidence",
  "",
  "_unordered list_",
  "",
  "- Read the current status.",
  "- Read the latest validation notes.",
  "",
  "Do not route without evidence.",
  "",
  "## Release Skills",
  "",
  "### Can Run",
  "",
  "#### Grounding Skill",
  "",
  "##### Purpose",
  "",
  "Ground the current claim before you write.",
  "",
  "> **NOTE — Usage Note**",
  "> _callout_",
  "> Use this before you summarize evidence.",
  "",
  "## Outputs",
  "",
  "### Release Comment",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Must Include",
  "",
  "_definitions_",
  "",
  "- **Summary** — Summarize the release outcome.",
  "- **Next Owner** — Name who owns the next action.",
]

FILE: examples/60_shared_readable_bodies/prompts/AGENTS.prompt
# This example reuses readable blocks in workflow, skill-entry, and output bodies.

skill GroundingSkill: "Grounding Skill"
    purpose: "Ground the current claim before you write."


skills ReleaseSkills: "Release Skills"
    can_run: "Can Run"
        skill grounding: GroundingSkill
            callout usage_note: "Usage Note"
                kind: note
                "Use this before you summarize evidence."


output ReleaseComment: "Release Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    definitions must_include: "Must Include"
        summary: "Summary"
            "Summarize the release outcome."

        next_owner: "Next Owner"
            "Name who owns the next action."


agent SharedReadableBodiesDemo:
    role: "Use {{ReleaseComment:must_include.summary.title}} and {{ReleaseSkills:can_run.grounding.usage_note.title}} before you route the release."
    workflow: "Review"
        summary: "Summary"
            bullets evidence: "Evidence"
                current_status: "Read the current status."
                validation: "Read the latest validation notes."
            "Do not route without evidence."
    skills: ReleaseSkills
    outputs: "Outputs"
        ReleaseComment
~~~~

### R7 — Example 61 Multiline Code And Readable Failures — `examples/61_multiline_code_and_readable_failures/`
~~~~markdown
FILE: examples/61_multiline_code_and_readable_failures/cases.toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "multiline code blocks render through the shared readable path"
status = "active"
kind = "render_contract"
agent = "ManifestGuideDemo"
assertion = "exact_lines"
expected_lines = [
  "Reuse Example Manifest when you draft the manifest guide.",
  "",
  "## Draft",
  "",
  "Write the guide and keep the example manifest in sync.",
  "",
  "## Outputs",
  "",
  "### Manifest Guide",
  "",
  "- Target: File",
  "- Path: `release_root/MANIFEST_GUIDE.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "#### Example Manifest",
  "",
  "_Advisory · code · json_",
  "",
  "```json",
  "",
  "{",
  '  "title": "PLACEHOLDER: Release title",',
  '  "steps": []',
  "}",
  "```",
]

[[cases]]
name = "callout kind must stay in the closed readable set"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_CALLOUT_UNKNOWN_KIND.prompt"
agent = "InvalidCalloutKindDemo"
exception_type = "CompileError"
error_code = "E299"
message_contains = [
  "Unknown callout kind",
  "urgent",
]

[[cases]]
name = "code block text must use multiline string form"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_CODE_BLOCK_WITHOUT_MULTILINE_STRING.prompt"
agent = "InvalidCodeBlockDemo"
exception_type = "CompileError"
error_code = "E299"
message_contains = [
  "Code block text must use a multiline string",
  "output BrokenGuide",
]

[[cases]]
name = "document block keys must stay unique"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_DOCUMENT_DUPLICATE_BLOCK_KEY.prompt"
agent = "InvalidDuplicateDocumentKeyDemo"
exception_type = "CompileError"
error_code = "E299"
message_contains = [
  "Duplicate document block key",
  "summary",
]

[[cases]]
name = "readable guards reject output-owned refs"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_READABLE_GUARD_SOURCE.prompt"
agent = "InvalidReadableGuardDemo"
exception_type = "CompileError"
error_code = "E299"
message_contains = [
  "Readable guard reads disallowed source",
  "BrokenComment.summary_present",
]

[[cases]]
name = "tables must declare at least one column"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_TABLE_WITHOUT_COLUMNS.prompt"
agent = "InvalidTableWithoutColumnsDemo"
exception_type = "CompileError"
error_code = "E299"
message_contains = [
  "Readable table must declare at least one column",
  "BrokenGuide.release_gates",
]

FILE: examples/61_multiline_code_and_readable_failures/prompts/AGENTS.prompt
# This example shows multiline readable `code` blocks on ordinary output bodies.

output ManifestGuide: "Manifest Guide"
    target: File
        path: "release_root/MANIFEST_GUIDE.md"
    shape: MarkdownDocument
    requirement: Required

    code example_manifest: "Example Manifest" advisory
        language: json
        text: """
{
  "title": "PLACEHOLDER: Release title",
  "steps": []
}
"""


agent ManifestGuideDemo:
    role: "Reuse {{ManifestGuide:example_manifest.title}} when you draft the manifest guide."
    workflow: "Draft"
        "Write the guide and keep the example manifest in sync."
    outputs: "Outputs"
        ManifestGuide

FILE: examples/61_multiline_code_and_readable_failures/prompts/INVALID_CALLOUT_UNKNOWN_KIND.prompt
output BrokenComment: "Broken Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    callout warning_box: "Warning Box"
        kind: urgent
        "This should fail."


agent InvalidCalloutKindDemo:
    role: "Compile the broken comment."
    workflow: "Warn"
        "This should fail."
    outputs: "Outputs"
        BrokenComment

FILE: examples/61_multiline_code_and_readable_failures/prompts/INVALID_CODE_BLOCK_WITHOUT_MULTILINE_STRING.prompt
output BrokenGuide: "Broken Guide"
    target: File
        path: "release_root/BROKEN_GUIDE.md"
    shape: MarkdownDocument
    requirement: Required

    code example_manifest: "Example Manifest"
        language: json
        text: "not multiline"


agent InvalidCodeBlockDemo:
    role: "Compile the broken guide."
    workflow: "Draft"
        "This should fail."
    outputs: "Outputs"
        BrokenGuide

FILE: examples/61_multiline_code_and_readable_failures/prompts/INVALID_DOCUMENT_DUPLICATE_BLOCK_KEY.prompt
document BrokenGuide: "Broken Guide"
    section summary: "Summary"
        "Start with the current goal."

    section summary: "Summary Again"
        "This should fail."


output BrokenGuideFile: "Broken Guide File"
    target: File
        path: "release_root/BROKEN_GUIDE.md"
    shape: MarkdownDocument
    structure: BrokenGuide
    requirement: Required


agent InvalidDuplicateDocumentKeyDemo:
    role: "Compile the broken guide."
    workflow: "Draft"
        "This should fail."
    outputs: "Outputs"
        BrokenGuideFile

FILE: examples/61_multiline_code_and_readable_failures/prompts/INVALID_READABLE_GUARD_SOURCE.prompt
output BrokenComment: "Broken Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    callout scope: "Scope" when BrokenComment.summary_present
        kind: note
        "This should fail."


agent InvalidReadableGuardDemo:
    role: "Compile the broken comment."
    workflow: "Warn"
        "This should fail."
    outputs: "Outputs"
        BrokenComment

FILE: examples/61_multiline_code_and_readable_failures/prompts/INVALID_TABLE_WITHOUT_COLUMNS.prompt
document BrokenGuide: "Broken Guide"
    table release_gates: "Release Gates"
        notes:
            "This should fail."


output BrokenGuideFile: "Broken Guide File"
    target: File
        path: "release_root/BROKEN_GUIDE.md"
    shape: MarkdownDocument
    structure: BrokenGuide
    requirement: Required


agent InvalidTableWithoutColumnsDemo:
    role: "Compile the broken guide."
    workflow: "Draft"
        "This should fail."
    outputs: "Outputs"
        BrokenGuideFile
~~~~
<!-- arch_skill:block:reference_pack:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 - Exact Phase 1 parity matrix

Status: COMPLETE

* Goal:
  classify every `docs/01_*` obligation against current shipped code, proof, and
  truth surfaces, with explicit attention to the identity slice and no scope
  cuts.
* Work:
  - build the line-item parity matrix for: readable/document blocks, multiline
    strings, `structure:`, document inheritance/descendants, concrete-agent
    titles, enum `title/key/wire` behavior, validation, and proof
  - confirm the readable/document wave is already shipped where the current
    grammar/compiler/examples say it is
  - explicitly record the current identity gaps already visible in the owner
    path unless later evidence disproves them
  - choose whether the missing identity proof can reuse an existing example or
    needs one narrow new manifest-backed example
* Verification (smallest signal):
  repo search, symbol-level code audit, and targeted manifest inspection only;
  no implementation claims without file anchors
* Docs/comments (propagation; only if needed):
  update this plan only if the parity matrix changes the architecture or phase
  order
* Exit criteria:
  there is no ambiguity about which Phase 1 items are already shipped-and-proved
  versus still unfinished
* Rollback:
  revert plan-hardening claims if a later code read disproves them

## Phase 2 - Finish the remaining Phase 1 identity slice on the canonical owner path

Status: COMPLETE

* Goal:
  land the still-missing Phase 1 identity behavior, currently expected to be
  concrete-agent declaration-head titles plus explicit enum `wire` semantics and
  projections.
* Work:
  - extend the grammar, parser, and model for optional concrete-agent titles and
    enum-member title/wire metadata while preserving shorthand compatibility
  - extend compiler resolution/interpolation so `:title`, `:key`, and enum
    `:wire` resolve through the existing addressability machinery
  - add fail-loud validation for duplicate enum wire values, illegal `wire:`
    placement, and invalid `:wire` projections
  - keep the already-landed readable/document path unchanged except for any
    necessary mechanical fallout
* Verification (smallest signal):
  targeted identity manifest runs; `make verify-diagnostics` if diagnostics move
* Docs/comments (propagation; only if needed):
  add concise code comments only at the canonical identity boundary if the new
  metadata/projection path would otherwise be hard to read
* Exit criteria:
  the remaining Phase 1 identity semantics compile and fail loud on the same
  owner path as the rest of the language
* Rollback:
  revert the identity slice if targeted proof or the broader corpus disproves
  preservation

## Phase 3 - Proof closure without ladder sprawl

Status: COMPLETE

* Goal:
  end with manifest-backed proof for every surviving Phase 1 obligation without
  creating a noisy second example ladder.
* Work:
  - preserve the current `56` through `61` readable/document ladder
  - add or repurpose one narrow identity manifest if the current corpus does not
    already prove the missing agent-title and enum-wire behavior
  - include compile-negative coverage for the new identity validation rules if
    they land
  - rerun targeted manifests before broader doc convergence starts
* Verification (smallest signal):
  targeted readable/document manifests, targeted identity manifest, then
  `make verify-examples`
* Docs/comments (propagation; only if needed):
  update `examples/README.md` and related live example docs only if the proof
  surface changes
* Exit criteria:
  every `docs/01_*` promise is either shipped-and-proved or blocked by a named
  remaining issue, with no proof gap hidden behind docs text
* Rollback:
  revert the touched example/manifest or implementation slice if preservation
  breaks

## Phase 4 - Live truth convergence and stale-status cleanup

Status: COMPLETE

Implementation pass result:

- `docs/archive/second_wave/DOCTRINE_READABLE_MARKDOWN_FULL_IMPLEMENTATION_2026-04-11.md` was
  demoted to `historical` and its current Phase 5 state now matches its own
  `Verdict (code): COMPLETE`.
- The later follow-through worklog recorded the reconciliation work and passing
  reruns from the main worktree.

* Goal:
  make code, proof, docs, instructions, and active plan artifacts tell the same
  final Phase 1 story.
* Work:
  - update `AGENTS.md`, `docs/LANGUAGE_DESIGN_NOTES.md`,
    `docs/LANGUAGE_REFERENCE.md`, `docs/README.md`, `examples/README.md`,
    `docs/COMPILER_ERRORS.md`, and `editors/vscode/README.md` as required by
    the final shipped state
  - repair, fold, or demote the stale `NOT COMPLETE` readable-markdown status
    block so it no longer competes with this plan
  - remove any surviving stop-at-`53` language from live truth surfaces
* Verification (smallest signal):
  rerun any command whose result is restated as green; `cd editors/vscode && make`
  if editor files change
* Docs/comments (propagation; only if needed):
  delete stale active truth rather than preserving it as live commentary
* Exit criteria:
  no live truth surface contradicts the final Phase 1 implementation/proof
  state
* Rollback:
  revert any truth-surface change that cannot be backed by rerun evidence

## Phase 5 - Final verification and closeout

Status: COMPLETE

Implementation pass result:

- fresh repo-local language proof is green in the main worktree:
  - `./.venv/bin/python -m doctrine.verify_corpus --manifest examples/62_identity_titles_keys_and_wire/cases.toml`
  - `./.venv/bin/python -m doctrine.diagnostic_smoke`
- `cd editors/vscode && make` passed again from the main worktree on
  2026-04-11, including `npm run test:integration`, alignment validation, and
  VSIX packaging
- the only remaining red signal is the stale authoritative audit block from the
  child auditor's non-reproducible `SIGABRT`; the main worktree proof is green
  and the loop may be manually disarmed if the operator accepts that audit-only
  mismatch

* Goal:
  prove the completed Phase 1 story end to end and leave the repo with one
  honest completion narrative.
* Work:
  - run the relevant repo verification commands
  - update final status and decision-log entries
  - leave the surviving plan artifacts in an honest completed-or-still-open
    state
* Verification (smallest signal):
  `make verify-examples`; `make verify-diagnostics` when applicable;
  `cd editors/vscode && make` when applicable
* Docs/comments (propagation; only if needed):
  mark surviving plan surfaces complete only when the cited checks are actually
  green
* Exit criteria:
  verification is green and Phase 1 truth is singular, current, and manifest-backed
* Rollback:
  reopen the affected phase immediately if any cited proof signal fails
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Smallest credible signals

- repo-wide preservation: `make verify-examples`
- focused Phase 1 proof: targeted readable/document manifests under
  `examples/56_*`, `58_*`, `59_*`, `60_*`, and `61_*`, plus the narrow identity
  manifest selected in Phase 1 if the current corpus lacks that proof
- diagnostics: `make verify-diagnostics` only if validation behavior changes
- editor parity: `cd editors/vscode && make` only if editor truth or editor
  support changes

## 8.2 Preservation signals

- existing pre-Phase-1 and post-Phase-1 manifests must stay green
- readable markdown must continue to compile and render through the same owner
  path; no extra preservation harness is needed if the corpus already catches
  regressions
- identity metadata and projections must land on the same owner path and proof
  surface, not in a sidecar checker or docs-only claim

## 8.3 Manual checks

- brief manual review of the final doc and example references to ensure no live
  surface still advertises the old shipped boundary or stale completion state

## 8.4 What we will not add

- no bespoke parity harness
- no doc-inventory gate
- no golden machinery beyond the existing manifest-backed references

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout

This is a hard-cutover repo-truth change, not a staged production rollout.
Completion happens when the shipped language, proof corpus, docs, instructions,
and editor truth agree.

## 9.2 Rollback

If final proof disproves parity, reopen the affected phase immediately and
revert any unsupported completion/status claim.

## 9.3 Telemetry / operational follow-through

No product telemetry is required. The operational follow-through is keeping the
verification commands and live documentation honest.

# 10) Decision Log (append-only)

## 2026-04-11 - Created a dedicated Phase 1 completion-parity plan

The user asked for a plan to finish whichever parts of
`docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md` are not done, without
slimming scope. A broader active readable-markdown plan already exists, but it
has wider scope and currently contains stale implementation-audit state relative
to its worklog. This new artifact treats `docs/01_*` as the requested behavior
boundary and makes the completion problem explicit as Phase 1 parity, proof, and
truth-surface convergence.

## 2026-04-11 - Folded the Phase 1 spec and unfinished readable/document examples into the plan

The user advanced from `new` into `fold-in`, which is sufficient confirmation to
move this artifact from `draft` to `active` without changing scope. Folded
`docs/01_*`, the corpus proof rules from `examples/README.md`, and the specific
unfinished readable/document example folders (`56`, `58`, `59`, `60`, `61`) into
one advisory `reference_pack` so later phases cannot miss the exact Phase 1
obligations, proof surfaces, and compile-negative failure set. Section 7 stayed
unchanged on purpose.

## 2026-04-11 - North Star explicitly confirmed

The user explicitly confirmed the drafted North Star with no scope edits. Treat
this plan's current TL;DR and Section 0 as approved for later `arch-step`
commands unless a later instruction reopens them.

## 2026-04-11 - Auto-plan found a real remaining identity gap, not just docs drift

The `auto-plan` pass hardened the architecture against current repo truth.
Readable/document surfaces are already landed on the canonical `doctrine/`
path and proved by the `56` through `61` ladder, but the current grammar/model
path still does not show the explicit concrete-agent title head or enum
`wire:` split promised by `docs/01_*`. The authoritative phased plan therefore
now treats Phase 1 completion as: parity matrix, identity-path implementation,
manifest-backed proof, truth-surface convergence, and final verification.

## 2026-04-11 - Phase 1 completion parity landed through example 62

The implementation loop closed the remaining Phase 1 identity slice on the
canonical `doctrine/` path. Concrete agents now support head titles, enum
members now split key/title/wire identity through the same addressability path,
duplicate enum wires have a dedicated `E294` diagnostic, the proof ladder now
extends through `examples/62_identity_titles_keys_and_wire`, and the live truth
surfaces plus VS Code package path were rerun green from this worktree.

## 2026-04-11 - Manual loop stop accepted after main-worktree proof stayed green

The fresh child audit reopened the loop on two items. One was real and was
fixed: the overlapping readable-markdown implementation doc was demoted to
historical and no longer competes as an active truth surface. The other was an
auditor-only VS Code integration `SIGABRT` that did not reproduce from the main
worktree; `./.venv/bin/python -m doctrine.verify_corpus --manifest examples/62_identity_titles_keys_and_wire/cases.toml`,
`./.venv/bin/python -m doctrine.diagnostic_smoke`, and
`cd editors/vscode && make` all passed. The loop was therefore manually
disarmed by operator decision rather than waiting for another fresh audit pass
to rewrite the authoritative audit block.
