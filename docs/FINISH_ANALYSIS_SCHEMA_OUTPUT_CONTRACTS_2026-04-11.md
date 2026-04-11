---
title: "Doctrine - Finish Analysis Schema Output Contracts - Architecture Plan"
date: 2026-04-11
status: active
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: parity_plan
related:
  - docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md
  - docs/ANALYSIS_AND_SCHEMA_SPEC.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/README.md
  - docs/COMPILER_ERRORS.md
  - examples/README.md
  - examples/54_analysis_attachment
  - examples/55_owner_aware_schema_attachments
  - examples/57_schema_review_contracts
  - doctrine/grammars/doctrine.lark
  - doctrine/model.py
  - doctrine/parser.py
  - doctrine/compiler.py
  - doctrine/renderer.py
  - editors/vscode/resolver.js
  - AGENTS.md
---

# TL;DR

## Outcome

Finish every Phase 2 obligation in
`docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md` without cutting scope, then
leave the repo with one honest completion story across `doctrine/`,
manifest-backed examples, evergreen docs, diagnostics docs, and VS Code parity
surfaces.

## Problem

Phase 2 is partially shipped, not cleanly unfinished. The repo already has
top-level `analysis` / `schema` declarations, agent `analysis:` attachment,
owner-aware `output.schema`, schema-backed review contracts, and positive
corpus/examples for part of the phase. But the Phase 2 doc still promises more
than the current language path clearly ships, especially `schema artifacts:` /
`groups:`, the full Phase 2 proof ladder, and a completion story that matches
live docs and editor behavior instead of leaving split truth behind.

## Approach

Treat `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md` as the authoritative
Phase 2 boundary. Audit it line by line against the shipped grammar, model,
parser, compiler, renderer, corpus, docs, and VS Code resolver; separate
already-landed surfaces from real gaps; then finish the missing core language
work and convergence work through the existing Doctrine owner paths only.

## Plan

1. Audit every promised Phase 2 surface against current shipped repo evidence.
2. Separate already-shipped, partially-shipped, and missing obligations in the
   Phase 2 doc.
3. Land the remaining core Phase 2 language work, likely centered on the parts
   of `schema` that are still absent from the grammar/model/parser/compiler
   path, plus any missing diagnostics, rendering, addressability, and proof.
4. Converge live docs, examples, and editor-facing truth so Phase 2 is neither
   understated nor overclaimed.
5. Close with repo-owned verification and only mark Phase 2 complete when the
   shipped truth and proof surfaces agree.

## Non-negotiables

- Do not slim the scope or reinterpret `docs/02_*` into a smaller subset.
- Do not keep split truth between the Phase 2 doc, evergreen docs, examples,
  diagnostics docs, and editor behavior.
- Do not add a second owner path for schema inventory semantics, addressability,
  or rendering.
- Do not preserve a partial Phase 2 story where later schema consumers ship on
  top of an unfinished `schema` core.
- Do not silently change the owner-aware `schema:` rule:
  `output.schema -> Doctrine schema`, `output shape.schema -> json schema`.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-11
Verdict (code): COMPLETE
Manual QA: pending (non-blocking)

## Code blockers (why code is not done)
- None. Fresh audit verification passed on 2026-04-11:
  `make verify-examples`, `make verify-diagnostics`, and
  `cd editors/vscode && make`.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Run the short live-editor smoke ladder from `editors/vscode/README.md` if a
  human package-install spot check is still desired after the passing VS Code
  package/test run.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-11
external_research_grounding: not run (repo evidence was sufficient on 2026-04-11)
deep_dive_pass_2: done 2026-04-11
recommended_flow: implement-loop
note: Auto-plan completed research, deep-dive pass 1, deep-dive pass 2, and phase-plan from repo evidence without external research. The doc is ready for implement-loop.
-->
<!-- arch_skill:block:planning_passes:end -->

Worklog: `docs/FINISH_ANALYSIS_SCHEMA_OUTPUT_CONTRACTS_2026-04-11_WORKLOG.md`

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly,
`docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md` will become an honest
description of shipped Doctrine Phase 2 rather than a mixed future/current
spec. Concretely:

- `analysis` will fully ship as a reusable, renderable, inheritable,
  addressable declaration family with typed verbs, diagnostics, and
  manifest-backed proof.
- `schema` will fully ship as the reusable inventory/gate contract promised by
  Phase 2, including `sections:`, `gates:`, `artifacts:`, `groups:`,
  owner-aware output attachment, inheritance, addressability, rendering,
  diagnostics, and proof.
- already-landed later consumers, such as schema-backed review contracts, will
  sit on top of a finished Phase 2 core instead of outrunning it.
- live docs, examples, diagnostics docs, and VS Code parity surfaces will tell
  the same Phase 2 story as the shipped compiler path.

The claim is false if any explicit Phase 2 surface from `docs/02_*` still lacks
the required grammar/model/parser/compiler/renderer support or proof, or if the
repo still contains live docs or editor behavior that describe a different
Phase 2 boundary than the code actually ships.

## 0.2 In scope

- Every explicit Phase 2 promise in
  `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md`:
  - first-class `analysis`
  - first-class `schema`
  - concrete-agent `analysis:` attachment
  - owner-aware `output.schema` versus `output shape.schema`
  - `schema sections:` and `gates:`
  - `schema artifacts:` and `groups:`
  - analysis/schema inheritance, addressability, rendering, and diagnostics
  - the positive and compile-negative proof ladder for those surfaces
- The canonical owner-path work needed to finish those promises through:
  - `doctrine/grammars/doctrine.lark`
  - `doctrine/model.py`
  - `doctrine/parser.py`
  - `doctrine/compiler.py`
  - `doctrine/renderer.py`
- Manifest-backed examples, evergreen docs, diagnostics docs, and VS Code
  parity surfaces that must match shipped Phase 2 truth.
- Architectural convergence needed because the repo already partially ships
  Phase 2 and some later consumers:
  - preserve working `analysis` attachment and owner-aware `schema:` behavior
  - avoid breaking schema-backed review contracts while finishing the Phase 2
    core they depend on
  - update or demote stale live truth surfaces that would otherwise keep
    conflicting completion stories alive

## 0.3 Out of scope

- Cutting `docs/02_*` down to only the currently working subset.
- New language capabilities that Phase 2 does not promise.
- Replanning the readable-markdown / `document` wave as if it were part of this
  task, except where already-shipped readable surfaces intersect directly with
  Phase 2 contracts or proof.
- Expanding Phase 2 into new review/control-plane functionality beyond what is
  required to finish the promised Phase 2 core and keep already-shipped later
  consumers truthful.
- Compatibility shims, alternate schema-inventory owners, or shadow resolver
  logic that preserves parallel meanings outside the explicit owner-aware rule.

## 0.4 Definition of done (acceptance evidence)

- The shipped Phase 2 core in `doctrine/` matches the full contract described
  by `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md`, not just the subset
  already landed.
- The repo has manifest-backed proof for the full positive and negative Phase 2
  ladder, including the missing `schema` inventory surfaces if they are indeed
  still absent.
- `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_DESIGN_NOTES.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md`,
  `docs/README.md`, and `examples/README.md` agree with shipped Phase 2 truth.
- If editor-facing files move, `editors/vscode/` reflects the same Phase 2
  contracts as the compiler and docs.
- Relevant verification passes at closeout:
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics change
  - targeted manifest-backed runs for touched examples
  - `cd editors/vscode && make` if `editors/vscode/` changes

Behavior-preservation evidence:

- already-shipped examples, especially `54_analysis_attachment`,
  `55_owner_aware_schema_attachments`, and `57_schema_review_contracts`, stay
  green unless an explicitly justified bug fix changes behavior
- existing owner-aware `schema:` meaning does not regress
- later schema-backed consumers do not become the only place where Phase 2
  inventory semantics appear to work

## 0.5 Key invariants (fix immediately if violated)

- No scope cutting from `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md`.
- No new parallel owner path for output inventory semantics.
- No silent drift in the owner-aware `schema:` resolution rule.
- No live doc or example may claim Phase 2 is complete while required language
  surfaces are still missing.
- No later-phase consumer may remain green only because it bypasses an
  unfinished Phase 2 core contract.
- No runtime fallbacks or compatibility shims. The phase either ships
  correctly or fails loudly.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Finish every Phase 2 promise exactly as written before declaring completion.
2. Keep one canonical owner path for `analysis` and `schema` semantics.
3. Preserve already-shipped examples and later integrations while finishing the
   missing core.
4. Converge docs, diagnostics, corpus, and editor truth to the same shipped
   boundary.

## 1.2 Constraints

- The repo is already in a partial second-wave state, so this is completion and
  convergence work, not a greenfield phase.
- `schema:` already has a naming collision with `json schema`, and the current
  owner-aware split must stay explicit across compiler, docs, proof, and editor
  tooling.
- Later schema consumers already exist in the repo, so finishing Phase 2 must
  preserve them or deliberately realign them through the same core contracts.
- The spec doc's proposed diagnostic bands may not match the currently shipped
  diagnostics surface and need evidence-based reconciliation rather than
  wishful renumbering.

## 1.3 Architectural principles (rules we will enforce)

- `docs/02_*` defines requested Phase 2 behavior; `doctrine/` and manifest
  cases define shipped truth.
- Grammar, model, parser, compiler, renderer, examples, docs, and editor
  parity move together; no partial feature shipping.
- `schema` remains the single reusable inventory owner for output-attached
  Doctrine inventory contracts.
- Unsupported or unresolved analysis/schema use fails loudly.
- Later integrations must extend the finished Phase 2 core instead of carrying
  private copies of missing Phase 2 behavior.

## 1.4 Known tradeoffs (explicit)

- Some of the remaining work may be convergence in docs/proof/editor surfaces
  rather than pure compiler work, but it is still in scope because the task is
  to finish the Phase 2 doc honestly.
- Finishing `schema artifacts:` / `groups:` may widen touched files beyond the
  narrow parser/model slice so rendering, addressability, proof, and docs stay
  aligned.
- If the current diagnostics story conflicts with the Phase 2 doc, the plan
  must reconcile to one shipped truth rather than preserve both stories.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- The shipped grammar, model, parser, and compiler already know about top-level
  `analysis` and `schema`.
- Concrete-agent `analysis:` attachment is already represented in the corpus.
- Owner-aware `schema:` on `output` versus `output shape` is already present in
  the language and docs.
- Schema-backed review contracts already exist as a later consumer.
- Evergreen docs already teach part of the Phase 2 surface.

## 2.2 What’s broken / missing (concrete)

- `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md` still promises `schema
  artifacts:` and `groups:` plus their addressability, rendering, diagnostics,
  and proof, but the current schema AST/parser path only clearly owns
  `sections:` and `gates:`.
- Companion Phase 2-facing docs do not currently tell one consistent story.
  `docs/ANALYSIS_AND_SCHEMA_SPEC.md` carries a "fully implemented" status note
  and an older phase split that gives schema-review integration to the same
  wave, while `docs/02_*` keeps schema-backed review consumers out of scope for
  this phase.
- The Phase 2 proof and diagnostics story is not yet visibly reconciled to the
  current shipped repo truth.
- Live docs currently under-describe some promised Phase 2 inventory surfaces,
  which makes it impossible to tell from one source whether Phase 2 is actually
  done.

## 2.3 Constraints implied by the problem

- The missing work must land through the existing Phase 2 owner paths, not
  through a sidecar schema inventory system.
- Already-shipped examples and later integrations form preservation signals and
  must stay green.
- Completion requires truth convergence, not only code landing.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- None adopted in the first planning pass. Repo evidence is sufficient to drive
  the remaining Phase 2 completion work, and the open questions are about
  Doctrine parity rather than outside prior art.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md` — requested-scope
    authority for the full Phase 2 contract, including `schema artifacts:` /
    `groups:`, namespaced schema addressability, owner-aware `output.schema`,
    and the negative proof ladder.
  - `doctrine/grammars/doctrine.lark` — shipped grammar already admits
    top-level `analysis` / `schema`, concrete-agent `analysis:`, and
    owner-aware `output schema:` via `analysis_field` and `output_schema_stmt`,
    but the schema block surface is still organized around `sections:` and
    `gates:` only.
  - `doctrine/model.py` — `analysis` is already a dedicated declaration family;
    the schema object model currently stops at `SchemaSection`,
    `SchemaGate`, block wrappers for `sections` / `gates`, and matching
    override forms. There are no first-class schema artifact or group node
    types today.
  - `doctrine/parser.py` — `schema_body()` enforces one-accounting-only for
    `sections` and `gates`, and the transformer only builds those block kinds.
    No parser path currently accounts for `artifacts`, `groups`, or their
    override forms.
  - `doctrine/compiler.py` — `ResolvedSchemaBody` currently carries only
    `sections` and `gates`; `_resolve_schema_body()`,
    `_compile_schema_decl()`, `_collect_schema_review_contract_gates()`, and
    `_schema_items_to_addressable_children()` therefore only own those two
    schema families today.
  - `doctrine/diagnostic_smoke.py` — direct smoke coverage already exists for
    analysis attachment rendering, owner-aware output-schema rendering, and the
    parse-time `schema:` plus `must_include:` ownership conflict.
  - `examples/54_analysis_attachment`, `examples/55_owner_aware_schema_attachments`,
    and `examples/57_schema_review_contracts` — active manifest-backed
    preservation signals for concrete-agent `analysis:`, owner-aware output
    schema attachment, and schema-backed review contracts.
  - `docs/LANGUAGE_REFERENCE.md` and `docs/AGENT_IO_DESIGN_NOTES.md` — live
    docs already teach `analysis:`, owner-aware `schema:`, and schema-backed
    review consumers, but they under-describe the full Phase 2 schema
    inventory surface promised by `docs/02_*`.
  - `docs/COMPILER_ERRORS.md` — canonical code bands already reserve
    `E500-E699` for emit and build-target failures, so the `E520-E531` schema
    code story in `docs/02_*` is drift, not a code band we can adopt
    unchanged.
  - `editors/vscode/resolver.js`, `editors/vscode/tests/integration/suite/index.js`,
    and `editors/vscode/README.md` — editor parity already knows about
    `analysis`, owner-aware `schema:` refs, `structure:`, and schema-backed
    review contract navigation, but the schema block parser and navigation
    assumptions still only recognize `sections` and `gates`.
- Canonical path / owner to reuse:
  - `doctrine/grammars/doctrine.lark` -> `doctrine/model.py` ->
    `doctrine/parser.py` -> `doctrine/compiler.py` -> `doctrine/renderer.py`
    — this existing schema declaration pipeline remains the only valid owner
    for any missing `artifacts` / `groups` semantics, addressability, and
    rendering. Later consumers and editor parity must follow this path rather
    than grow private schema logic.
- Existing patterns to reuse:
  - `doctrine/model.py`, `doctrine/parser.py`, and `doctrine/compiler.py` —
    the shipped `analysis` family already shows the intended first-class typed
    declaration pattern for inheritance, resolution, readable rendering, and
    addressability.
  - `doctrine/parser.py` and `doctrine/compiler.py` — the current
    `sections` / `gates` schema accounting path provides the local pattern to
    extend, not replace, when adding `artifacts` / `groups`.
  - `examples/README.md` plus manifest-backed `cases.toml` files — the repo's
    proof model is positive and negative corpus coverage, not ad hoc examples
    without manifests.
- Prompt surfaces / agent contract to reuse:
  - `examples/*/prompts/AGENTS.prompt` — these are proof inputs, not the owner
    of the feature. There is no separate prompt-layer workaround to bless for
    missing schema semantics.
- Native model or agent capabilities to lean on:
  - Not applicable. This task is deterministic compiler, docs, and editor
    parity work; no model-capability gap justifies wrappers or sidecars.
- Existing grounding / tool / file exposure:
  - `make verify-examples` — shipped proof for the active corpus.
  - `make verify-diagnostics` — shipped verification surface when diagnostics
    or the error catalog change.
  - `cd editors/vscode && make` — shipped editor parity verification surface.
  - `doctrine/diagnostic_smoke.py` — small direct preservation checks for core
    diagnostics and rendering.
- Duplicate or drifting paths relevant to this change:
  - `docs/ANALYSIS_AND_SCHEMA_SPEC.md` — stale "fully implemented" note, older
    phase split, and older example numbering; useful as background only.
  - `docs/README.md` — still describes schema-backed review integration as a
    later phase boundary even though example `57` is already shipped.
  - `docs/LANGUAGE_REFERENCE.md` / `docs/AGENT_IO_DESIGN_NOTES.md` — partial
    Phase 2 teaching under-describes `schema artifacts:` / `groups:`.
  - `examples/55_owner_aware_schema_attachments/prompts/AGENTS.prompt` — its
    section key named `artifacts` is only a schema section label today, not
    proof that the first-class `schema artifacts:` inventory surface exists.
- Capability-first opportunities before new tooling:
  - Finish the existing schema declaration pipeline and editor parity directly.
    Do not add a schema-inventory sidecar, doc-only interpretation layer, or
    resolver-specific fallback model to paper over the missing compiler truth.
- Behavior-preservation signals already available:
  - `examples/54_analysis_attachment/cases.toml` — preserves concrete-agent
    `analysis:` attachment and unknown-analysis compile failure behavior.
  - `examples/55_owner_aware_schema_attachments/cases.toml` — preserves the
    owner-aware split between `output shape.schema` and `output.schema`, plus
    the parse-time local `must_include:` conflict.
  - `examples/57_schema_review_contracts/cases.toml` — preserves schema-backed
    review contracts and the fail-loud no-gates contract check.
  - `doctrine/diagnostic_smoke.py` — preserves direct rendering and conflict
    diagnostics for the already-shipped surfaces.
  - `editors/vscode/tests/integration/suite/index.js` — preserves go-to
    definition for examples `54`, `55`, `56`, and `57`.

## 3.3 Open questions (evidence-based)

- Should schema addressability stay flattened by child key, or converge to the
  namespaced Phase 2 contract from `docs/02_*` such as
  `Schema:sections.summary.title` and `Schema:artifacts.manifest_file.title`?
  — settle by comparing `docs/02_*` examples, the current
  `_schema_items_to_addressable_children()` collision risk, and whether any
  shipped corpus already depends on flat schema child paths.
- Should the missing `schema artifacts:` / `groups:` proof live in example
  `55`, or in a new dedicated example? — settle by the repo's "one new idea per
  example" rule, the fact that `55` already owns owner-aware `schema:` versus
  `json schema`, and the current corpus already using `56` through `62`.
- Does the finished Phase 2 cut need new dedicated schema diagnostics, or is
  the honest first implementation to keep some failures on `E199` / `E299`
  until narrower canonical codes are added under the current error-band rules?
  — settle by the existing `docs/COMPILER_ERRORS.md` band contract and the
  actual failure shapes introduced during implementation.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:reference_pack:start -->
# Reference Pack (folded materials; phase-aligned)
Updated: 2026-04-11

## Inventory

- R1 — Phase 2 - Analysis Schema And Output Contracts — `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md`
- R2 — Analysis And Schema Language Surfaces — `docs/ANALYSIS_AND_SCHEMA_SPEC.md`
- R3 — Shipped Language Reference — `docs/LANGUAGE_REFERENCE.md`
- R4 — Agent I/O Model — `docs/AGENT_IO_DESIGN_NOTES.md`
- R5 — Examples Guide — `examples/README.md`
- R6 — Example 54: analysis attachment — `examples/54_analysis_attachment/`
- R7 — Example 55: owner-aware schema attachments — `examples/55_owner_aware_schema_attachments/`
- R8 — Example 57: schema review contracts — `examples/57_schema_review_contracts/`

## Binding obligations (distilled; must satisfy)

- Treat R1 as requested-scope authority for this plan: finish first-class
  `analysis`, first-class `schema`, concrete-agent `analysis:`, owner-aware
  `output.schema`, schema `sections:` / `gates:` / `artifacts:` / `groups:`,
  inheritance, addressability, rendering, diagnostics, and the full proof
  ladder. (From: R1)
- Preserve the owner-aware field split everywhere:
  `output.schema -> Doctrine schema`; `output shape.schema -> json schema`.
  (From: R1, R3, R4, R7)
- Preserve the single-owner rule on output inventory seams: an output with
  Doctrine `schema:` may not also own local `must_include:`. (From: R1, R7)
- Preserve fail-loud validation for missing or bad analysis/schema refs,
  duplicate keys, missing required sections, bad artifact refs, unknown group
  members, and empty groups when those surfaces are present. (From: R1)
- Treat `schema artifacts:` and `groups:` as Phase 2 core, not deferred
  control-plane sugar. (From: R1)
- Preserve already-shipped proof surfaces: example `54` proves concrete-agent
  `analysis:` attachment; example `55` proves owner-aware output-schema
  behavior; example `57` proves later schema-backed review consumers already
  depend on the Phase 2 core. (From: R5, R6, R7, R8)
- Use R2 as secondary design background only where it agrees with R1 and
  shipped code/examples. Its "fully implemented" status note and older phase
  split/example numbering are drift signals that must be reconciled, not scope
  authority over R1. (From: R1, R2, R5)
- Keep the evergreen docs honest: R3 and R4 currently teach the shipped
  `analysis` attachment and owner-aware output-schema rule, but they
  under-describe the full Phase 2 inventory surface promised by R1. (From: R1,
  R3, R4)
- Keep the teaching/proof story honest: R5 already treats `54` through `62` as
  active shipped second-wave corpus, so any missing Phase 2 core semantics or
  stale docs must be reconciled in the same cut. (From: R5)

## Instruction-bearing structure (only when present; preserve exact or equivalent operational form)

### R1 — Phase 2 - Analysis Schema And Output Contracts

1. Phase 2 owns:
   - first-class `analysis`
   - first-class `schema`
   - `analysis:` attachment on concrete agents
   - owner-aware `schema:` on outputs
   - schema sections and gates
   - schema artifacts and reusable groups
   - analysis and schema inheritance, addressability, rendering, and diagnostics
2. Phase 2 does not own:
   - authored render profiles
   - review lowering to typed markdown
   - dedicated `review_family`
   - dedicated `route_only`
   - dedicated `grounding`
   - schema-backed `review contract:` consumers
3. Exact implementation order preserved from the source:
   1. Add first-class `analysis` plus agent `analysis:` attachment.
   2. Land analysis rendering, addressability, inheritance, and diagnostics.
   3. Add first-class `schema` with `sections:`.
   4. Land owner-aware `output.schema` resolution without disturbing `output shape.schema`.
   5. Add schema `gates:` plus schema inheritance and gate diagnostics.
   6. Add schema `artifacts:` and `groups:` plus addressability and diagnostics.
   7. Extend proof to cover both positive and negative cases before later review or control-plane consumers are added.
- Hard negatives:
  - `analysis` may not target `review:`, `inputs:`, `outputs:`, `skills:`, or output `schema:`.
  - an output with Doctrine `schema:` may not also own local `must_include:`.
  - groups may not be empty.
- Branch conditions and fail-loud rules:
  - `classify ... as <name_ref>` must resolve to an `enum`
  - analysis basis refs must be addressable
  - every artifact `ref:` must resolve to a concrete input or output root
  - every group member must name a local artifact key

### R2 — Analysis And Schema Language Surfaces

1. The source currently opens with a status note that says the `analysis` and
   `schema` surfaces are believed to be fully implemented and that shipped code
   plus manifest-backed examples should win on drift.
2. The source preserves an older phase split:
   - Phase 1: `schema sections:` only plus output attachment
   - Phase 2: optional `gates:` plus `review contract:` targeting `schema`
3. The source preserves older example naming and ordering:
   - Example `54` analysis basic
   - Example `55` analysis classify/compare
   - Example `56` schema output contract
   - Example `57` schema inheritance
   - Example `60` schema review contract
- Consequence:
  - treat this source as background design intent and drift evidence, not as the
    authority that can silently override R1 or the current shipped corpus map

## Phase alignment guidance (advisory; core planning commands adopt into Section 7 if needed)

### Global (applies across phases)

- Preserve the owner-aware output-schema rule and the single-owner inventory
  seam while finishing any missing Phase 2 core semantics. (From: R1, R3, R4,
  R7)
- Keep already-shipped examples `54`, `55`, and `57` green as preservation
  signals while the missing Phase 2 remainder is finished. (From: R5, R6, R7,
  R8)
- Reconcile companion-doc drift instead of keeping multiple completion stories
  alive. (From: R1, R2, R3, R4, R5)

### Future foundation / core-semantics phase

- Potentially relevant obligations (advisory):
  - close any missing `schema artifacts:` / `groups:` grammar, model, parser,
    compiler, renderer, addressability, and diagnostics work
  - preserve analysis/schema fail-loud boundaries while completing that work
- References:
  - R1, R2, R3, R6, R7, R8

### Future proof / truth-convergence phase

- Potentially relevant obligations (advisory):
  - align evergreen docs with the full Phase 2 boundary actually shipped
  - reconcile older companion-spec status notes and example numbering if they
    still imply a different completion story
  - keep the active corpus story honest because `examples/README.md` already
    treats `54` through `62` as shipped second-wave examples
- References:
  - R1, R2, R3, R4, R5

### Future editor-parity phase

- Potentially relevant obligations (advisory):
  - if editor files move, keep resolver and docs aligned with the same
    owner-aware `schema:` rule and with any finished schema inventory surfaces
- References:
  - R1, R3, R4

## Folded sources (verbatim; inlined so they cannot be missed)

### R1 — Phase 2 - Analysis Schema And Output Contracts — `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md`
~~~~markdown
## Phase Boundary

This phase owns:

- first-class `analysis`
- first-class `schema`
- `analysis:` attachment on concrete agents
- owner-aware `schema:` on outputs
- schema sections and gates
- schema artifacts and reusable groups
- analysis and schema inheritance, addressability, rendering, and diagnostics

This phase does not own:

- authored render profiles
- review lowering to typed markdown
- dedicated `review_family`
- dedicated `route_only`
- dedicated `grounding`
- schema-backed `review contract:` consumers

### Artifact inventories and reusable groups

Phase 2 also gives `schema` a first-class place to name concrete artifact
surfaces and reusable bundles of those surfaces for later control-plane use.

Rules:

- `artifacts:` declares keyed, titled concrete artifact entries inside a schema
- each artifact entry owns one `ref:` that resolves to a concrete addressable
  input or output root
- `groups:` declares keyed, titled bundles of local artifact keys
- group member order is authored and preserved

### Owner-aware `schema:` rules

- `output.schema` resolves to a Doctrine `schema`
- `output shape.schema` resolves to a `json schema`
- these are not competing meanings; they are owner-scoped meanings

### Static rules

- a schema must declare at least one `sections:` or `artifacts:` block
- an output with `schema:` may not also own local `must_include:`
- an output-attached schema must still expose at least one section
- every artifact `ref:` must resolve to a concrete input or output root
- every group member must name a local artifact key
- groups may not be empty

### Diagnostics And Invariants

- `E527` duplicate schema artifact key
- `E528` duplicate schema group key
- `E529` schema artifact `ref:` unresolved or not a concrete artifact root
- `E530` schema group member unknown
- `E531` empty schema group

### Proof Plan

Positive ladder for phase 2:

1. analysis attachment on a concrete agent
2. analysis classify/compare/defend coverage
3. owner-aware output `schema:` attachment
4. schema inheritance and gate catalogs
5. schema artifacts and reusable groups
~~~~

### R2 — Analysis And Schema Language Surfaces — `docs/ANALYSIS_AND_SCHEMA_SPEC.md`
~~~~markdown
> Status note (2026-04-11): We believe the `analysis` and `schema` surfaces
> described in this document are fully implemented in the current repo. If this
> spec and the shipped implementation ever drift, trust `doctrine/` and the
> manifest-backed examples.

### Phase split

Phase 1:

- sections only
- attach to outputs
- no review integration yet

Phase 2:

- add optional gates
- allow `review contract:` to target a schema

### Example ladder entries for schema

Example 56 - `56_schema_output_contract`
Example 57 - `57_schema_inheritance`
Example 60 - `60_schema_review_contract`
~~~~

### R3 — Shipped Language Reference — `docs/LANGUAGE_REFERENCE.md`
~~~~markdown
### Schemas

`schema` declares a reusable artifact inventory and optional gate catalog.

Important rules:

- `schema` owns artifact inventory sections and optional named `gates:`.
- On `output`, `schema:` points at a Doctrine `schema` declaration.
- On `output shape`, `schema:` remains the owner-aware attachment point for
  `json schema`.
- Schema sections and gates are addressable by authored key.
- `review contract:` may point at either a `workflow` or a `schema`.
~~~~

### R4 — Agent I/O Model — `docs/AGENT_IO_DESIGN_NOTES.md`
~~~~markdown
Important rules:

- `schema:` on `output` attaches a Doctrine `schema` declaration.
- `schema:` on `output shape` still attaches a `json schema`; the field name is
  owner-aware rather than globally retyped.

## Example Map

- `55`: owner-aware output `schema:` attachments
- `57`: schema-backed review contracts on ordinary output carriers
~~~~

### R5 — Examples Guide — `examples/README.md`
~~~~markdown
## Learning Paths

- `54` through `62`: second-wave integration surfaces for `analysis`,
  owner-aware `schema:` / `structure:` attachments, readable markdown
  documents and descendants, shared readable block reuse, multiline code
  blocks, schema-backed review contracts, and title-bearing identity
  projections for concrete agents and enum members

## Corpus Index

| `54_analysis_attachment` | Concrete-agent `analysis:` attachment and analysis-root addressability. |
| `55_owner_aware_schema_attachments` | Owner-aware split between `output shape.schema` and `output.schema`. |
| `57_schema_review_contracts` | Schema-backed `review contract:` with exported schema gates. |
~~~~

### R6 — Example 54: analysis attachment — `examples/54_analysis_attachment/`
~~~~markdown
analysis ReleaseAnalysis: "Release Analysis"
    stages: "Stages"
        derive "Release plan" from {CurrentPlan}
        classify "Risk band" as RiskBand
        compare "Coverage" against {CurrentPlan}
        defend "Recommendation" using {CurrentPlan}

agent ReleaseAnalysisDemo:
    workflow: "Ship"
        "Use the attached analysis before you finalize the release plan."
    analysis: ReleaseAnalysis

[[cases]]
name = "agent analysis attachment renders through the compiled readable path"

[[cases]]
name = "analysis field fails loudly on an unknown declaration"
error_code = "E299"
~~~~

### R7 — Example 55: owner-aware schema attachments — `examples/55_owner_aware_schema_attachments/`
~~~~markdown
output shape DeliveryPayload: "Delivery Payload"
    kind: JsonObject
    schema: DeliveryJsonSchema

schema DeliveryInventory: "Delivery Inventory"
    sections:
        summary: "Summary"
            "Include a short summary."

        artifacts: "Artifacts"
            "List the produced artifacts."

output DeliveryPlan: "Delivery Plan"
    shape: MarkdownDocument
    schema: DeliveryInventory

[[cases]]
name = "owner-aware schema attachments keep json schema and doctrine schema separate"

[[cases]]
name = "output schema rejects local must_include ownership"
kind = "parse_fail"
error_code = "E199"
~~~~

### R8 — Example 57: schema review contracts — `examples/57_schema_review_contracts/`
~~~~markdown
schema PlanReviewContract: "Plan Review Contract"
    sections:
        summary: "Summary"
            "Summarize the reviewed plan."

    gates:
        outline_complete: "Outline Complete"
            "Confirm the reviewed plan includes the outline."

review SchemaBackedPlanReview: "Schema Backed Plan Review"
    contract: PlanReviewContract

[[cases]]
name = "review contracts can target schemas with exported gates"

[[cases]]
name = "schema review contracts must export at least one gate"
error_code = "E299"
message_contains = [
  "Review contract must export at least one gate",
  "GateLessContract",
]
~~~~
<!-- arch_skill:block:reference_pack:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

The current Phase 2 surface is split across one real language owner path plus
proof, docs, and editor followers:

- `doctrine/grammars/doctrine.lark` — owns the syntax for top-level
  `analysis` / `schema`, concrete-agent `analysis:`, and owner-aware
  `output schema:`.
- `doctrine/model.py` — owns the typed AST families. `analysis` is already a
  dedicated declaration family; `schema` currently has dedicated types only for
  `sections` and `gates`.
- `doctrine/parser.py` — owns transformer-time block accounting and therefore
  currently bounds schema syntax to `sections` / `gates`.
- `doctrine/compiler.py` — owns declaration indexing, inheritance resolution,
  readable rendering, output attachment behavior, schema-backed review contract
  export, and addressable child mapping.
- `doctrine/renderer.py` — follows compiled sections after the compiler decides
  what a schema contributes.
- `examples/54_*`, `55_*`, and `57_*` — the active Phase 2 preservation corpus.
- `docs/` — live truth surfaces already teaching part of the Phase 2 story.
- `editors/vscode/resolver.js` plus extension tests and README — the editor
  follower for go-to-definition and owner-aware typed refs.

## 4.2 Control paths (runtime)

The shipped control flow today is concrete:

1. The grammar parses top-level `analysis_decl` / `schema_decl`, concrete-agent
   `analysis_field`, and `output_schema_stmt`.
2. The parser transforms `analysis` into titled section nodes plus typed verbs,
   but transforms `schema` into a `SchemaBody` whose block accounting only
   understands `sections`, `gates`, and their inherit/override forms.
3. The compiler indexes `SchemaDecl` alongside other declarations, resolves
   schema inheritance through `_resolve_schema_decl()` and
   `_resolve_schema_body()`, and materializes a `ResolvedSchemaBody` that only
   carries `sections` and `gates`.
4. Output compilation resolves `output.schema` through the same compiler owner
   path and renders `- Schema: ...` plus "Required Sections" from schema
   sections only.
5. Review contracts can already target a schema; the schema contract export path
   reads only resolved schema gates through `_collect_schema_review_contract_gates()`.
6. Addressability for `schema` is currently flattened to direct child keys by
   `_schema_items_to_addressable_children()`, unlike the explicit
   family-prefixed paths promised by `docs/02_*`.
7. VS Code follows this shipped model: owner-aware `schema:` refs already work,
   but schema block parsing and container discovery still only recognize
   `sections` and `gates`.

## 4.3 Object model + key abstractions

- `analysis` is already substantially complete as a first-class readable
  declaration family: dedicated AST, inheritance, attachment on concrete
  agents, rendering, addressability, and positive/negative proof.
- `schema` is first-class only in a narrower sense. The live AST and compiler
  own:
  - whole-declaration inheritance
  - `sections:`
  - `gates:`
  - owner-aware `output.schema`
  - schema-backed review contracts that export gates
- The missing surface is not theoretical. There are no first-class schema
  artifact or group nodes, no resolver support for those block kinds, and no
  manifest-backed proof for them.
- Example `55` does not contradict that finding. Its keyed section named
  `artifacts` is just a regular schema section, not proof of the separate
  `schema artifacts:` inventory family.

## 4.4 Observability + failure behavior today

- Positive preservation signals already exist:
  - example `54` renders attached analysis content
  - example `55` proves owner-aware `schema:` on `output` versus `output shape`
  - example `57` proves schema-backed review contracts
- Negative preservation signals already exist:
  - unknown `analysis:` target fails at compile time on `E299`
  - `output schema:` plus local `must_include:` fails at parse time on `E199`
  - schema-backed review contracts with no gates fail at compile time on `E299`
- `doctrine/diagnostic_smoke.py` duplicates the most important direct checks for
  analysis rendering, output-schema rendering, and the schema-owner conflict.
- The diagnostics surface is therefore fail-loud, but not yet harmonized with
  the Phase 2 doc's proposed `E520+` schema codes. The canonical error catalog
  now reserves `E500+` for emit/build, so the spec doc's diagnostic numbering
  is stale.
- The other important drift is addressability. The Phase 2 doc promises
  `Schema:sections.<key>...`, `Schema:gates.<key>...`,
  `Schema:artifacts.<key>...`, and `Schema:groups.<key>...`, while the shipped
  compiler currently exposes schema children as a flat direct-key map.

## 4.5 UI surfaces (ASCII mockups, if UI work)

There is no end-user UI here, but VS Code is a real parity surface. The current
extension README and integration tests already cover `analysis`, owner-aware
`schema:` refs, `structure:`, and schema-backed review contracts. They do not
yet cover first-class schema `artifacts:` / `groups:` or any schema-family
namespaced addressability contract.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

Phase 2 completion stays on the existing owner path and extends it end to end:

- `doctrine/grammars/doctrine.lark` grows the missing schema block families and
  their inherit/override forms.
- `doctrine/model.py` and `doctrine/parser.py` gain first-class artifact/group
  nodes and parser accounting through the same schema family.
- `doctrine/compiler.py` becomes the single place that resolves, validates,
  renders, and exposes addressability for all four schema families.
- manifest-backed examples, live docs, diagnostics docs, and VS Code parity
  follow that compiler truth in the same cut.
- If a dedicated artifact/group example is added beyond `62`, `examples/README.md`
  and the repo-root `AGENTS.md` corpus-boundary statement must move with it.

## 5.2 Control paths (future)

The future compile path is explicit and single-owner:

1. `schema` grammar accepts `sections:`, `gates:`, `artifacts:`, and `groups:`
   plus `inherit` / `override` accounting for each family.
2. The parser materializes those families as typed schema items and continues to
   fail loudly when a child accounts for the same schema family more than once.
3. The compiler resolves a schema into one `ResolvedSchemaBody` that owns all
   four families, whole-declaration inheritance, and all static validation:
   - a schema must declare at least one `sections:` or `artifacts:` block
   - an output-attached schema must still expose at least one section
   - every artifact `ref:` resolves to a concrete input or output root
   - every group member names a local artifact key
   - groups may not be empty
4. Output compilation keeps the shipped owner-aware `schema:` rule unchanged and
   continues to render attached schema guidance through the compiler path rather
   than a parallel output-specific schema interpreter.
5. Schema-backed review contracts continue to consume schema gates only, but now
   do so on top of a finished schema core instead of outrunning it.
6. Schema addressability converges to explicit family namespaces:
   - `Schema:sections.<key>...`
   - `Schema:gates.<key>...`
   - `Schema:artifacts.<key>...`
   - `Schema:groups.<key>...`
   This removes cross-family key collisions and makes the Phase 2 path contract
   in `docs/02_*` honest. No flat-key compatibility shim is planned.

## 5.3 Object model + abstractions (future)

- `schema` remains one declaration family, not a split between "renderable
  sections/gates" and a second inventory-only surface.
- The schema model grows first-class artifact and group item types plus matching
  block and override wrappers alongside the existing section and gate families.
- `ResolvedSchemaBody` becomes the compiler-owned SSOT for all resolved schema
  content.
- Schema addressability becomes namespace-first at the schema root. The schema
  root exposes family containers; each family exposes authored keys; authored
  items expose the same scalar fields the language already treats as addressable
  such as `.title`, and any additional scalar fields the implementation makes
  explicitly pathable.
- Output-attached schema rendering remains readable and narrow: attached outputs
  still surface the schema title and required sections, while standalone schema
  rendering can expand to show the full schema contract, including artifact and
  group catalogs.

## 5.4 Invariants and boundaries

- `analysis` and `schema` remain first-class typed declarations; no ad hoc prose
  or sidecar manifest can replace the compiler-owned contract.
- `schema` is the single owner for reusable Doctrine output inventory contracts.
- Owner-aware `schema:` meaning does not change:
  - `output.schema` -> Doctrine `schema`
  - `output shape.schema` -> `json schema`
- Later consumers may depend only on the finished schema core; they may not
  bypass it or shadow it.
- Diagnostics must stay honest to the canonical error-band contract. If the cut
  adds narrower schema codes, they must fit the current `docs/COMPILER_ERRORS.md`
  bands instead of reviving the stale `E520-E531` allocation.
- No runtime fallbacks, alias layers, or resolver-only compatibility paths.

## 5.5 UI surfaces (ASCII mockups, if UI work)

VS Code follows the same compiler truth:

- owner-aware `schema:` navigation stays intact
- schema block parsing adds `artifacts` / `groups`
- any new schema-family addressability contract is reflected in resolver logic,
  README smoke guidance, and extension tests
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Scope authority | `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md` | full doc | authoritative requested Phase 2 contract, including artifacts/groups and namespaced schema paths | keep as scope authority and reconcile implementation to it | no scope cutting allowed | no new API; baseline contract | parity audit against shipped repo |
| Schema grammar | `doctrine/grammars/doctrine.lark` | `schema_body`, schema block productions, `output_schema_stmt` context | schema declarations parse top-level and owner-aware output attachment, but schema blocks are still `sections` / `gates` only | add `artifacts:` / `groups:` plus `inherit` / `override` forms through the same schema grammar family | Phase 2 contract still missing core syntax | full schema block surface owned by one grammar | corpus positives/negatives; parser/compile checks |
| Schema AST | `doctrine/model.py` | `SchemaSection`, `SchemaGate`, `SchemaItem`, `SchemaBody`, `SchemaDecl` | schema AST only models sections/gates and their override wrappers | add first-class schema artifact/group item and block types; extend schema item union and resolved-body assumptions | parser/compiler cannot own missing semantics without typed nodes | one schema family with four block kinds | examples; diagnostics; addressability |
| Schema parser | `doctrine/parser.py` | `schema_body()`, `schema_sections_block()`, `schema_gates_block()`, `schema_inherit()`, override handlers | parser accounting enforces one-accounting-only for sections/gates and ignores artifact/group families entirely | extend parser accounting, duplicate checks, and transformer handlers for artifacts/groups and their override forms | keeps fail-loud schema structure rules in the parser instead of ad hoc compiler repair | explicit schema family accounting for all four block kinds | parser negatives; manifest-backed compile negatives |
| Schema resolution | `doctrine/compiler.py` | `ResolvedSchemaBody`, `_resolve_schema_decl()`, `_resolve_schema_body()`, `_schema_body_action()`, merge helpers | resolved schema state carries only sections/gates | widen resolved schema state and inheritance merge logic to cover artifacts/groups and new static rules | single-owner schema semantics live here | one resolved schema body for sections/gates/artifacts/groups | full corpus; targeted manifest runs |
| Schema render + output attach | `doctrine/compiler.py`, `doctrine/renderer.py` | `_compile_schema_decl()`, output schema compile path, rendered schema detail lines | output-attached schemas render title plus required sections; standalone schema rendering only knows sections/gates | preserve output-side owner-aware behavior while extending standalone schema rendering and any compiler-owned schema detail surfaces for artifacts/groups | finish Phase 2 without creating a second render path | output-attached schemas still require sections; standalone schema refs can show full schema catalog | example `55`; new artifact/group example; renderer snapshots if any |
| Schema addressability | `doctrine/compiler.py` | `_schema_items_to_addressable_children()`, schema target handling in addressable resolution | schema child paths are flattened by authored key | converge schema addressability to explicit family namespaces and migrate any touched schema refs accordingly | avoids cross-family collisions and matches `docs/02_*` | `Schema:sections.<key>...`, `Schema:gates.<key>...`, `Schema:artifacts.<key>...`, `Schema:groups.<key>...` | targeted addressability corpus and any affected docs/examples |
| Review consumer preservation | `doctrine/compiler.py` | `_resolve_review_contract_spec()`, `_collect_schema_review_contract_gates()` | review contracts already target schemas through gates only | keep review contracts gate-only while reusing the widened resolved schema body | later consumers must stay on the same schema core | no new review control plane; schema gates remain the contract export | example `57`; review-related diagnostics |
| Diagnostics | `doctrine/diagnostic_smoke.py`, `docs/COMPILER_ERRORS.md`, possibly `doctrine/diagnostics.py` | smoke checks, stable-code catalog, any new narrower codes | current proof uses `E199` / `E299` for several schema failures; docs/02 has stale `E520+` plan | decide honest code strategy, add smoke coverage if needed, and update the canonical error catalog to match shipped behavior | avoid split truth and invalid code-band reuse | stable schema diagnostics under current code-band policy | `make verify-diagnostics` if touched; smoke checks |
| Corpus proof | `examples/54_analysis_attachment`, `examples/55_owner_aware_schema_attachments`, `examples/57_schema_review_contracts`, likely new `examples/63_*` | manifests, prompts, refs | existing examples preserve shipped second-wave behavior but do not prove first-class schema artifacts/groups | add dedicated positive/negative proof for artifacts/groups without overloading the owner-aware schema example | repo rule is one new idea per example; Phase 2 completion needs proof | dedicated manifest-backed artifact/group example plus negatives | `make verify-examples`; targeted `verify_corpus` runs |
| Live docs | `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/README.md`, `docs/ANALYSIS_AND_SCHEMA_SPEC.md`, `docs/COMPILER_ERRORS.md`, `examples/README.md` | live truth and example map | docs already teach part of the surface, but phase boundaries, addressability, diagnostics, and completeness claims drift | rewrite or demote stale claims in the same cut | completion requires one honest truth story | shipped docs match finished code/proof and current corpus numbering | doc review; relevant verify commands |
| Repo instructions | `AGENTS.md` | shipped corpus note | repo instructions currently state the shipped corpus ends at `62` | update only if the proof ladder adds a new active example beyond `62` | avoid instruction drift after proof expansion | corpus-boundary statement matches reality | no separate test; verify through example map consistency |
| Editor parity | `editors/vscode/resolver.js`, `editors/vscode/tests/integration/suite/index.js`, `editors/vscode/README.md` | schema block regexes, schema-body container logic, go-to-definition smoke map | extension understands analysis/owner-aware schema/structure/review but still only parses schema `sections` / `gates` | add artifact/group schema block handling and any new schema-family path/navigation behavior; update README smoke steps | keep editor/compiler parity and avoid private semantics | resolver follows the same schema family and path contract as compiler | `cd editors/vscode && make` |

## 6.2 Migration notes

* Canonical owner path / shared code path:
  `doctrine/grammars/doctrine.lark` -> `doctrine/model.py` ->
  `doctrine/parser.py` -> `doctrine/compiler.py` -> `doctrine/renderer.py`
  remains the only valid schema owner path. Examples, docs, diagnostics, and
  VS Code must follow it.
* Deprecated APIs (if any):
  Flat schema child addressability should be treated as drift once the new work
  lands. If any touched source still uses it, migrate it in the same cut rather
  than add aliases.
* Delete list (what must be removed; include superseded shims/parallel paths if any):
  stale "fully implemented" and older phase/example claims in
  `docs/ANALYSIS_AND_SCHEMA_SPEC.md`; any live doc text implying example `55`
  already proves first-class schema artifacts/groups; any editor or doc note
  that preserves sections/gates-only schema truth after the compiler changes.
* Capability-replacing harnesses to delete or justify:
  none should be introduced. A schema-inventory sidecar, doc-only interpreter,
  or resolver-only fallback is out of bounds.
* Live docs/comments/instructions to update or delete:
  `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md` when its completion state
  changes, `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/README.md`,
  `docs/ANALYSIS_AND_SCHEMA_SPEC.md`, `docs/COMPILER_ERRORS.md`,
  `examples/README.md`, `editors/vscode/README.md`, and `AGENTS.md` if the
  active corpus grows.
* Behavior-preservation signals for refactors:
  examples `54`, `55`, and `57`; `doctrine/diagnostic_smoke.py`; existing VS
  Code integration coverage for examples `54` through `57`.

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Schema core | `doctrine/model.py`, `doctrine/parser.py`, `doctrine/compiler.py` | one schema family with four explicit block kinds and explicit inherit/override accounting | prevents a second inventory-only schema interpretation from growing in later consumers | include |
| Addressability | `doctrine/compiler.py`, `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md`, live docs/examples that cite schema refs | namespace-first schema addressability | prevents cross-family key collisions and doc/code divergence | include |
| Proof ladder | `examples/55_*`, likely new `examples/63_*`, `examples/README.md`, `AGENTS.md` | one-new-idea-per-example proof expansion | prevents example `55` from carrying two concepts and hiding missing proof | include |
| Diagnostics truth | `docs/COMPILER_ERRORS.md`, `doctrine/diagnostic_smoke.py`, any new schema negatives | canonical current error-band policy | prevents resurrecting stale `E520+` assumptions | include |
| Live docs | `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/README.md`, `docs/ANALYSIS_AND_SCHEMA_SPEC.md` | one shipped Phase 2 completion story | prevents split truth across evergreen and drafting docs | include |
| Review-specific docs | `docs/REVIEW_SPEC.md` and related review references | schema review contracts stay gate-only on top of finished schema core | useful parity check, but may not require edits if wording stays true | defer |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests. Also: document new patterns or gotchas in code comments at the canonical boundary only when they materially help the next pass.

## Phase 1 — Finish the schema core through the existing owner path

Status: COMPLETE

* Goal:
  Ship the missing Phase 2 schema core in `doctrine/` itself: first-class
  `artifacts:` / `groups:`, whole-schema inheritance for those families, and
  the canonical schema addressability contract, without regressing already
  shipped `analysis`, owner-aware `output.schema`, or schema-backed review
  consumers.
* Work:
  Extend `doctrine/grammars/doctrine.lark` for schema artifacts/groups and
  their inherit/override forms; add matching schema AST and resolved-schema
  types in `doctrine/model.py` / `doctrine/compiler.py`; widen
  `doctrine/parser.py` schema accounting and duplicate checks; widen compiler
  resolution, validation, rendering, and schema addressability in
  `doctrine/compiler.py`; preserve the owner-aware output-schema rule and keep
  review contracts gate-only on top of the widened schema body.
* Verification (smallest signal):
  Run targeted manifest-backed preservation checks for examples `54`, `55`, and
  `57`, plus a targeted compile/proof signal for one real artifact/group schema
  input before broadening to full-corpus verification.
* Docs/comments (propagation; only if needed):
  Add a short code comment only at the canonical schema addressability or schema
  validation boundary if the namespace-first contract would otherwise be hard to
  recover from code alone.
* Exit criteria:
  `doctrine/` can parse, resolve, render, validate, and address first-class
  schema artifacts/groups through the canonical schema pipeline; existing
  second-wave preservation examples still hold.
* Rollback:
  Revert the widened schema core as one slice if the implementation cannot
  preserve the owner-aware `schema:` rule or lands with ambiguous schema path
  semantics.

## Phase 2 — Turn the finished semantics into proof, diagnostics, and editor parity

Status: COMPLETE

* Goal:
  Leave the missing schema core with manifest-backed proof, fail-loud
  diagnostics, and VS Code behavior that follows the same compiler truth.
* Work:
  Add a dedicated artifact/group corpus example, likely beyond `62`, with both
  positive and negative cases; preserve example `55` as the owner-aware schema
  split example; update `doctrine/diagnostic_smoke.py` and
  `docs/COMPILER_ERRORS.md` as needed to reflect the honest diagnostic outcome;
  update `editors/vscode/resolver.js`, `editors/vscode/tests/integration/suite/index.js`,
  and `editors/vscode/README.md` for schema artifact/group navigation and any
  new schema-family path contract; update `examples/README.md` and `AGENTS.md`
  if the active corpus grows past `62`.
* Verification (smallest signal):
  Run `make verify-examples`; run `make verify-diagnostics` if diagnostics or
  the compiler error catalog changed; run `cd editors/vscode && make` if the
  extension moved; use targeted `uv run --locked python -m doctrine.verify_corpus --manifest ...`
  for the new or changed schema examples while iterating.
* Docs/comments (propagation; only if needed):
  Update example-map and editor README smoke instructions in the same phase; add
  a brief resolver comment only if the schema-family container logic becomes
  materially non-obvious.
* Exit criteria:
  The full positive/negative Phase 2 proof ladder exists for artifacts/groups,
  diagnostics are honest, and editor parity matches shipped compiler behavior.
* Rollback:
  Revert proof/editor surfaces together with any unfinished schema-core change
  that made them necessary.

## Phase 3 — Converge every live truth surface and close Phase 2 honestly

Status: COMPLETE

Manual QA (non-blocking): Run the short live-editor smoke ladder from
`editors/vscode/README.md` only if a human package-install spot check is still
desired after the passing VS Code package/test run.

* Goal:
  Make the repo's docs and instructions say exactly what the shipped Phase 2
  code and proof now do, with no stale completion claims, stale phase splits,
  or stale schema-path/diagnostic guidance left behind.
* Work:
  Update `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md`,
  `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/README.md`,
  `docs/ANALYSIS_AND_SCHEMA_SPEC.md`, `docs/COMPILER_ERRORS.md`,
  `examples/README.md`, `editors/vscode/README.md`, and `AGENTS.md` when
  applicable; demote or rewrite stale lines about "fully implemented" status,
  phase ownership, example numbering, schema addressability, and diagnostic
  codes instead of layering caveats on top.
* Verification (smallest signal):
  Re-run the relevant shipped commands for every touched surface:
  `make verify-examples`; `make verify-diagnostics` when diagnostics changed;
  `cd editors/vscode && make` when editor files changed; plus one targeted
  manifest-backed verification run for the new artifact/group example at
  closeout.
* Docs/comments (propagation; only if needed):
  Delete stale wording instead of preserving drafting-history caveats on live
  surfaces. Git already retains the old truth.
* Exit criteria:
  No live doc, example map, diagnostics catalog, repo instruction, or editor
  README tells a different Phase 2 story than the shipped compiler and
  manifest-backed examples.
* Rollback:
  Revert doc truth-convergence together with any feature or proof change that
  created the new truth; do not keep partial doc rewrites detached from shipped
  behavior.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

Keep verification proportional. Prefer the existing corpus, diagnostics checks,
and editor verification surfaces over new harnesses.

## 8.1 Unit tests (contracts)

- Prefer existing parser/compiler/diagnostics smoke or targeted corpus-negative
  cases over bespoke test harnesses.
- Any refactor-heavy change must prove preserved behavior through existing Phase
  2 and later examples where possible.

## 8.2 Integration tests (flows)

- `make verify-examples` is the main shipped proof signal.
- Use targeted manifest-backed runs while landing or debugging the missing
  Phase 2 slices.
- Run `make verify-diagnostics` if diagnostic catalog or normalization changes.
- Run `cd editors/vscode && make` if editor files move.

## 8.3 E2E / device tests (realistic)

- No device/E2E surface is expected here.
- Finalization may use short manual spot checks of compiled example output or
  editor navigation only if the repo-owned programmatic signals leave a narrow
  ambiguity.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

Hard cutover inside the repo. Phase 2 should move from partial completion to
one shipped truth without preserving alternate doc or editor stories.

## 9.2 Telemetry changes

No production telemetry surface is expected. Verification is repo-local.

## 9.3 Operational runbook

- Keep the canonical plan doc honest as implementation and audit progress.
- Re-run the relevant verification commands before marking the plan complete.
- If completion changes the truth status of overlapping docs, update or demote
  them in the same run.

# 10) Decision Log (append-only)

## 2026-04-11 - Treat Phase 2 as completion-plus-convergence, not greenfield

Context

`docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md` describes a complete Phase 2
surface, but the live repo already ships part of that surface and even some
later consumers. The task is therefore to finish the missing remainder and
converge repo truth, not to plan the phase as if nothing has landed.

Options

- Treat Phase 2 as greenfield and ignore current partial implementation.
- Slim the task to only the obviously missing compiler slice.
- Treat `docs/02_*` as authoritative scope, audit the partially shipped repo
  against it, finish the missing remainder, and converge live truth surfaces.

Decision

Treat this as a no-scope-cutting parity/completion plan against `docs/02_*`.

Consequences

- The plan must include both code/proof gaps and live-truth convergence work.
- Already-landed later consumers become preservation signals, not excuses to
  skip missing Phase 2 core work.

Follow-ups

- Keep the implementation pass scoped to the schema-core owner path plus the
  required proof/docs/editor convergence surfaces.
- Use `implement-loop` next so implementation and completeness audit stay
  bounded to this artifact.

## 2026-04-11 - Converge schema addressability onto explicit family namespaces

Context

Research and deep-dive confirmed that the current compiler exposes schema child
paths as a flat direct-key map through `_schema_items_to_addressable_children()`,
while `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md` promises explicit
family-qualified paths such as `Schema:sections.summary.title` and
`Schema:artifacts.manifest_file.title`. The same pass also confirmed that
first-class `schema artifacts:` / `groups:` do not yet exist in the shipped
schema model, parser, compiler, or VS Code resolver.

Options

- Keep flat schema child paths and treat the `docs/02_*` path examples as
  aspirational prose only.
- Add artifacts/groups but preserve flat schema child paths with compatibility
  aliases.
- Finish schema artifacts/groups and converge schema addressability to explicit
  family namespaces in the same cut.

Decision

Finish schema artifacts/groups and move schema addressability to explicit
family namespaces with no compatibility shim.

Consequences

- The schema root becomes the only place that owns `sections`, `gates`,
  `artifacts`, and `groups` as addressable child families.
- VS Code parity, live docs, and corpus examples must follow the namespaced
  contract in the same cut.
- If any touched source currently depends on flat schema child paths, it must
  be migrated instead of preserved through aliases.

## 2026-04-11 - Fresh implement-loop audit closed clean

Context

The implementation landed the missing schema artifact/group core, namespaced
schema addressability, a dedicated proof example, and the corresponding live
docs and VS Code parity updates. The plan artifact still needed a fresh
repo-owned audit so the phase status and audit block reflected current code
truth rather than the pre-implementation `IN PROGRESS` state.

Options

- Leave the plan marked active/in progress and stop after the code changes.
- Run the full repo-owned verification set, rewrite the audit block to current
  truth, and close the implementation loop cleanly.

Decision

- Run the repo-owned closeout verification from the current worktree.
- Mark the authoritative audit `COMPLETE`, set the plan `status: complete`, and
  close the loop with the required docs-cleanup handoff.

Consequences

- The plan, worklog, shipped corpus, diagnostics smoke, and VS Code package
  verification now tell the same finished Phase 2 story.
- The repo-local `implement-loop` state can be cleared.

Follow-ups

- Use `$arch-docs` for any broader archival or docs-cleanup work beyond this
  code-complete implementation pass.

## 2026-04-11 - Fresh audit reopened Phase 3 for remaining live-doc drift

Context

A fresh repo-owned audit re-ran `uv sync`, `npm ci`, targeted manifest checks
for examples `54`, `55`, `57`, and `63`, `make verify-examples`,
`make verify-diagnostics`, and `cd editors/vscode && make`. Compiler, corpus,
diagnostics, and editor packaging all passed, but
`docs/ANALYSIS_AND_SCHEMA_SPEC.md` still contains live legacy guidance for the
old `E520-E539` schema band and the old schema example ladder.

Options

- Keep the plan `complete` and treat that document as harmless background.
- Reopen Phase 3 because this plan explicitly made touched live-doc cleanup
  part of code-completeness and required stale lines to be rewritten or
  retired instead of caveated.

Decision

Reopen Phase 3 and mark the implementation audit `NOT COMPLETE` until
`docs/ANALYSIS_AND_SCHEMA_SPEC.md` stops presenting the legacy schema guidance
as live truth.

Consequences

- The remaining blocker is narrowed to doc truth convergence in one touched
  file, not compiler or editor behavior.
- Frontmatter status returns to `active` until that cleanup lands and is
  re-audited.

Follow-ups

- Rewrite or delete the stale schema diagnostics and example-ladder sections in
  `docs/ANALYSIS_AND_SCHEMA_SPEC.md`, then rerun the already-proven shipped
  verification surface and re-run `audit-implementation`.
