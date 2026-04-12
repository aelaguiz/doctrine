---
title: "Doctrine - Lessons Port Remaining Language Gaps Full Implementation - Architecture Plan"
date: 2026-04-11
status: historical
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: parity_plan
related:
  - docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md
  - docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md
  - docs/archive/PHASE4_REVIEW_ROUTE_ONLY_GROUNDING_CONTROL_PLANE_COMPLETION_2026-04-11.md
  - docs/archive/PHASE4_REVIEW_ROUTE_ONLY_GROUNDING_CONTROL_PLANE_COMPLETION_2026-04-11_WORKLOG.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/REVIEW_SPEC.md
  - docs/WORKFLOW_LAW.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/README.md
  - examples/68_review_family_shared_scaffold
  - examples/69_case_selected_review_family
  - examples/70_route_only_declaration
  - examples/71_grounding_declaration
  - examples/72_schema_group_invalidation
  - doctrine/grammars/doctrine.lark
  - doctrine/model.py
  - doctrine/parser.py
  - doctrine/compiler.py
---

# TL;DR

## Outcome

Treat `docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md` as the full
requested-scope boundary, then leave Doctrine in one honest end state where
every item in that doc is either fully shipped and evidenced or explicitly
classified as already-shipped baseline or non-gap with the repo truth updated
to match.

## Problem

The source gap doc says Doctrine still needs clean final language closure for
case-selected review families and schema-owned restart surfaces, while the live
repo already shows strong Phase 4 evidence in `doctrine/`, `examples/68_*`
through `examples/72_*`, the live docs index, and the historical Phase 4
completion worklog. Right now the main risk is split truth: the repo may
already implement most or all of the remaining language work, but the docs and
instruction surfaces do not yet tell one stable story about that fact.

## Approach

Run a full-scope audit against the source gap doc and the live shipped repo.
Begin by revalidating the already-landed Phase 4 proof ladder and live docs
against the source gap doc. If any promised language surface is still not
truly shipped, implement it through Doctrine's canonical grammar -> model ->
parser -> compiler -> renderer/diagnostics path, then close the loop through
manifest-backed proof, live docs, and editor support. If the current proof
holds, finish the same full scope by converging the stale truth surfaces
instead of pretending that "already landed somewhere" is enough.

## Plan

1. Audit the source gap doc line by line against the live compiler, examples,
   diagnostics, docs, and editor surfaces.
2. Lock the preserved baseline: already-solved identity/rendering/review
   substrate items stay off the remaining-gap list and must remain green.
3. Revalidate the existing Phase 4 manifests and only reopen compiler files if
   that proof or the source-gap audit shows a real missing semantic promise.
4. Converge live docs and instructions so the repo teaches one truthful story
   about `review_family`, case-selected review law, `route_only`, `grounding`,
   and schema-group invalidation.
5. Prove closeout with the required Doctrine verification commands, not just
   targeted spot checks.

## Non-negotiables

- Do not narrow the scope to a convenient subset.
- Do not reopen the already-solved Lessons pressure points as new feature work.
- Do not ship Lessons-specific escape hatches, namespaces, or ad hoc knobs.
- Do not keep split truth between the source gap doc, live docs, examples,
  `doctrine/`, diagnostics, editor support, and repo instructions.
- Do not add fallback shims or a second semantic control plane.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-11
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Broader docs cleanup, consolidation, or plan/worklog retirement can now move
  to `Use $arch-docs` if desired.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-11
external_research_grounding: not run - repo evidence sufficient so far on 2026-04-11
deep_dive_pass_2: done 2026-04-11
recommended_flow: phase plan -> implement
note: Deep-dive pass 2 hardened the default implementation posture: convergence-first with targeted revalidation of the already-landed Phase 4 proof ladder, and compiler-file reopening only if that proof or the source-gap audit exposes a real missing semantic promise.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly, Doctrine will end with one truthful answer
to the Lessons remaining-gap doc:

- case-selected exact review law will be fully shipped as Doctrine-native
  `review_family` / `selector` / `cases` behavior, or the audit will prove that
  it already is shipped and the remaining work was only truth convergence
- schema-owned restart surfaces will be fully shipped through
  `schema.groups.*` invalidation with concrete rendered expansion, or the audit
  will prove that it already is shipped and the remaining work was only truth
  convergence
- dedicated Phase 4 declaration families such as `review_family`,
  `route_only`, and `grounding` will remain wrappers over the existing
  review/workflow/schema semantics rather than becoming a second semantic owner
  path
- the repo's live docs, examples, diagnostics, editor support, and instruction
  surfaces will agree with the shipped language boundary

The claim is false if, after implementation and verification, any remaining-gap
item from the source doc is still missing required shipped support in
`doctrine/`, lacks manifest-backed proof, lacks required editor/diagnostic
coverage, or remains contradicted by live docs or instructions.

## 0.2 In scope

- The full requested scope in
  `docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md`, including:
  - preserving the items that should stay off the remaining-gap list
  - the full closure story for one critic surface with case-selected exact
    review law
  - the full closure story for schema-owned restart surfaces that invalidate
    concretely
  - the requirement that dedicated Phase 4 surfaces stay declaration-level
    reuse over existing Doctrine semantics, not a shadow control plane
- Any canonical owner-path code work required in:
  - `doctrine/grammars/doctrine.lark`
  - `doctrine/model.py`
  - `doctrine/parser.py`
  - `doctrine/compiler.py`
  - `doctrine/renderer.py`
  - `doctrine/diagnostics.py`
  - `doctrine/diagnostic_smoke.py`
  - `doctrine/verify_corpus.py`
- Manifest-backed example work for the relevant proof ladder, especially
  `examples/57`, `examples/63`, and `examples/68_*` through `examples/72_*`
- Live doc, historical-doc routing, and instruction-surface convergence needed
  so the repo says one honest thing about the shipped Phase 4 boundary
- Editor parity work under `editors/vscode/` if the audit shows the live
  language surface still outpaces the resolver or grammar tooling

## 0.3 Out of scope

- Narrowing the requested behavior to only the subset that is easiest to close
  quickly
- Adding Lessons-specific product or workflow vocabulary to the Doctrine
  language
- Inventing a new invalidation-only declaration family when `schema.artifacts`
  and `schema.groups` already own the inventory story
- Replacing explicit case-selected review structure with an implicit dynamic
  wrapper contract
- Runtime fallbacks, compatibility shims, or parallel semantic owner paths
- Broad second-wave redesign unrelated to the remaining-gap doc

## 0.4 Definition of done (acceptance evidence)

- Every claim in
  `docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md` is accounted for as
  one of:
  - preserved already-shipped baseline
  - genuine remaining gap now implemented
  - non-gap explicitly left off the Doctrine worklist
- The canonical shipped surfaces agree on the result:
  - `doctrine/` implements the final behavior
  - relevant manifest-backed examples prove it
  - live docs teach it
  - diagnostics/error guidance are aligned where behavior changed
  - VS Code support is aligned if touched
- Final closeout runs the Doctrine verification required by the touched
  surfaces:
  - `uv sync`
  - `npm ci`
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics change
  - `cd editors/vscode && make` when editor files change
- If any live doc must be deleted or retired, that work follows the restore-
  point commit rule rather than silently removing history

## 0.5 Key invariants (fix immediately if violated)

- No scope narrowing relative to the source gap doc
- No Lessons-specific escape hatches or namespace bleed
- No second semantic control plane beside Doctrine's existing review/workflow/
  schema owner paths
- No fallback shims
- No dual truth between shipped code, manifest-backed proof, live docs, and
  live instructions
- No silent regression in the already-shipped review, workflow-law, schema, or
  rendering behavior that this work builds on

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Produce one honest repo-wide answer about the remaining-gap doc.
2. Preserve the full requested scope instead of shrinking it during planning or
   implementation.
3. Keep the implementation Doctrine-native and generic, not Lessons-branded.
4. Preserve already-shipped behavior while closing residual gaps.
5. Finish with proof, docs, and editor parity rather than code-only closure.

## 1.2 Constraints

- The source gap doc is not shipped truth on its own; `doctrine/` and
  manifest-backed examples are.
- The live repo already contains strong evidence that Phase 4 landed further
  than the source gap doc implies, so the plan must distinguish baseline from
  residual delta.
- Root instructions currently disagree about shipped corpus coverage: this
  repo's live docs index references `examples/72_schema_group_invalidation`
  while the root `AGENTS.md` still says the current shipped corpus covers
  through `examples/63_schema_artifacts_and_groups`.
- Any doc retirement during implementation must follow the restore-point rule.
- User expectation is explicit: full implementation and test closure, not a
  doc-only interpretation.

## 1.3 Architectural principles (rules we will enforce)

- Use the source gap doc as the requested-scope boundary, not as runtime truth.
- Use `doctrine/` plus manifest-backed examples as shipped truth.
- Reuse existing review, workflow-law, schema, and renderer owner paths.
- Prefer explicit typed branches and fail-loud semantics over dynamic wrapper
  indirection.
- Keep examples, live docs, diagnostics, and instructions aligned in the same
  run as shipped behavior changes.

## 1.4 Known tradeoffs (explicit)

- The later implementation pass may discover that some "remaining gap" work is
  already fully shipped; that does not reduce scope, it changes the residual
  delta from code-writing to truth convergence.
- Full-scope closure may widen beyond the obvious compiler files into docs,
  examples, diagnostics, and editor tooling.
- A truthful final answer may require retiring or reclassifying stale docs even
  when the code delta is small or zero.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- The remaining-gap doc identifies two Doctrine-native closures:
  case-selected review families and schema-owned restart surfaces.
- The live repo already appears to ship first-class `review_family`,
  `route_only`, `grounding`, and schema-group invalidation support in the core
  grammar/parser/compiler path.
- The live docs index already teaches `examples/68_*` through `examples/72_*`
  as the Phase 4 proof ladder.
- A historical Phase 4 completion plan and worklog already exist, but they are
  not enough to declare the remaining-gap doc fully closed without a fresh
  audit.

## 2.2 What’s broken / missing (concrete)

- The remaining-gap doc still frames these surfaces as open language closure,
  which may now be stale relative to the shipped repo.
- Live docs, historical docs, examples, editor support, and instruction files
  need one audited verdict about what is truly shipped versus merely proposed.
- If any part of the remaining-gap story is not actually complete in the live
  code path, the repo still needs that missing implementation and proof.

## 2.3 Constraints implied by the problem

- We cannot assume missing code just because a doc says "remaining."
- We cannot assume completion just because a historical worklog says "done."
- We must re-ground the remaining-gap doc against the live repo before
  choosing whether the residual work is code, convergence, or both.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- None required yet — reject external research for now — the live Doctrine repo
  already contains the relevant language, proof, and doc surfaces for this
  planning pass, and the main uncertainty is shipped-state convergence rather
  than missing design precedent.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/grammars/doctrine.lark` — top-level declarations already include
    `route_only`, `grounding`, and `review_family`, plus `selector` support
    inside review bodies and the schema `groups:` family needed for restart-set
    ownership.
  - `doctrine/parser.py` — parser entry points already materialize
    `review_family_decl`, `route_only_decl`, `grounding_decl`, and
    `selector_block`, which means the Phase 4 surfaces are not merely doc prose.
  - `doctrine/model.py` — the model layer already carries case-selected review
    structures such as `ReviewCase` and related `cases` tuples.
  - `doctrine/compiler.py` — the compiler already resolves `route_only` and
    `grounding` through the ordinary workflow owner path, validates
    case-selected review families, and widens invalidation through
    schema-group resolution.
  - `doctrine/diagnostics.py` and `docs/COMPILER_ERRORS.md` — the repo already
    ships compile-negative handling for these surfaces, although Phase 4
    failures still appear to bucket under generic `E299` unless a narrower code
    is added later.
- Canonical owner path / owner to reuse:
  - `doctrine/grammars/doctrine.lark` -> `doctrine/parser.py` ->
    `doctrine/model.py` -> `doctrine/compiler.py` — the one semantic owner path
    for the remaining-gap language; no second control-plane engine is justified.
  - `docs/LANGUAGE_REFERENCE.md`, `docs/REVIEW_SPEC.md`,
    `docs/WORKFLOW_LAW.md`, and `docs/AGENT_IO_DESIGN_NOTES.md` — the live
    teaching surfaces that must stay aligned with the shipped compiler path.
- Existing patterns to reuse:
  - `examples/57_schema_review_contracts` — preserved baseline for schema-
    backed `review contract:` semantics.
  - `examples/63_schema_artifacts_and_groups` — preserved baseline for typed
    artifact inventories and reusable `schema.groups`.
  - `examples/68_review_family_shared_scaffold` and
    `examples/69_case_selected_review_family` — the live proof ladder for
    shared review scaffolds and exhaustive case-selected review families.
  - `examples/70_route_only_declaration`,
    `examples/71_grounding_declaration`, and
    `examples/72_schema_group_invalidation` — the live proof ladder for the
    dedicated Phase 4 wrappers and concrete invalidation expansion.
  - `docs/AGENT_IO_DESIGN_NOTES.md` — the reuse rule that `review_family`,
    `route_only`, and `grounding` still feed ordinary outputs and
    `trust_surface`, rather than inventing a second emitted contract system.
- Prompt surfaces / agent contract to reuse:
  - Not a model-capability problem. This work lives on deterministic compiler,
    example, and doc surfaces, not on prompt repair or agent harness design.
- Native model or agent capabilities to lean on:
  - None. The correct lever is existing Doctrine compiler truth plus manifest-
    backed proof, not new LLM-side machinery.
- Existing grounding / tool / file exposure:
  - `examples/README.md` and `make verify-examples` — the canonical proof and
    corpus verification surface.
  - `make verify-diagnostics` — the preservation signal when diagnostic
    behavior or wording changes.
  - `editors/vscode/` plus `cd editors/vscode && make` — the editor parity
    surface if the audit finds keyword or grammar drift.
  - `docs/archive/PHASE4_REVIEW_ROUTE_ONLY_GROUNDING_CONTROL_PLANE_COMPLETION_2026-04-11.md`
    and `docs/archive/PHASE4_REVIEW_ROUTE_ONLY_GROUNDING_CONTROL_PLANE_COMPLETION_2026-04-11_WORKLOG.md`
    — historical evidence only, useful for intent and prior closeout claims but
    not authoritative over the live code path.
- Duplicate or drifting paths relevant to this change:
  - `docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md` — still frames
    the two remaining language families as open closure work, which may now be
    partially or wholly stale.
  - `AGENTS.md` — currently says the shipped corpus covers through
    `examples/63_schema_artifacts_and_groups`, which conflicts with the live
    docs index and examples ladder that already teach through `examples/72_*`.
  - `docs/archive/PHASE4_REVIEW_ROUTE_ONLY_GROUNDING_CONTROL_PLANE_COMPLETION_2026-04-11.md`
    and related historical notes — claim completion, but remain archival rather
    than live truth.
  - historical design docs such as `docs/SECOND_WAVE_LANGUAGE_NOTES.md` may
    still preserve pre-Phase-4 rejection logic; they matter only if any live
    doc or instruction still treats them as current authority.
- Capability-first opportunities before new tooling:
  - Use the existing compiler path, corpus, and live docs surfaces before
    adding any new harness or helper. The likely residual work is language
    truth convergence and proof completeness, not new scaffolding.
- Behavior-preservation signals already available:
  - targeted manifest checks for `examples/57_*`, `63_*`, and `68_*` through
    `72_*`
  - `make verify-examples`
  - `make verify-diagnostics`
  - `cd editors/vscode && make`

## 3.3 Open questions from research

- Does any source-gap claim still require net-new compiler or renderer work, or
  is the remaining delta now entirely docs/examples/diagnostics/editor
  convergence? — settle by line-by-line audit of the source gap doc against
  `doctrine/`, the examples ladder, and live docs.
- Which live instruction surfaces are now stale enough to block an honest
  shipped story? — settle by auditing `AGENTS.md`, the live docs index, and any
  surviving live references that still frame Phase 4 as future work.
- Do Phase 4 failures need narrower diagnostic codes or is the current generic
  `E299` bucket intentionally acceptable? — settle by reviewing the compile-
  negative corpus and the current `docs/COMPILER_ERRORS.md` contract during
  deep-dive.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

The remaining-gap behavior already spans the normal Doctrine layers:

- semantic declaration and parsing:
  - `doctrine/grammars/doctrine.lark`
  - `doctrine/parser.py`
  - `doctrine/model.py`
- semantic resolution, validation, lowering, and emitted behavior:
  - `doctrine/compiler.py`
  - `doctrine/renderer.py`
  - `doctrine/diagnostics.py`
  - `doctrine/diagnostic_smoke.py`
- proof and shipped teaching corpus:
  - `examples/57_schema_review_contracts`
  - `examples/63_schema_artifacts_and_groups`
  - `examples/68_review_family_shared_scaffold`
  - `examples/69_case_selected_review_family`
  - `examples/70_route_only_declaration`
  - `examples/71_grounding_declaration`
  - `examples/72_schema_group_invalidation`
  - `examples/README.md`
- live documentation:
  - `docs/README.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/REVIEW_SPEC.md`
  - `docs/WORKFLOW_LAW.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/COMPILER_ERRORS.md`
- editor parity:
  - `editors/vscode/resolver.js`
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json`
  - `editors/vscode/tests/`
- remaining drift surfaces under audit:
  - `docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md`
  - `AGENTS.md`
  - historical context docs such as `docs/SECOND_WAVE_LANGUAGE_NOTES.md` and
    `docs/archive/PHASE4_REVIEW_ROUTE_ONLY_GROUNDING_CONTROL_PLANE_COMPLETION_2026-04-11.md`

## 4.2 Control paths (runtime)

The live compiler path already owns the Phase 4 semantics:

1. `doctrine/grammars/doctrine.lark` recognizes top-level `review_family`,
   `route_only`, and `grounding`, plus review `selector` blocks, exhaustive
   `cases`, schema `groups:`, and workflow-law `invalidate`.
2. `doctrine/parser.py` materializes those authored surfaces into typed model
   objects rather than flattening them into generic prose-only structures.
3. `doctrine/compiler.py` then routes them through the canonical semantic
   owners:
   - `review_family` stays on the review compiler path, including inherited
     selectors, exhaustive cases, and case-local contract validation
   - `route_only` is resolved as a workflow-like declaration and lowered into
     the same `current none`, `stop`, route, and guarded-output validation path
   - `grounding` is resolved through the same workflow/control-plane boundary
     instead of a separate protocol engine
   - `invalidate` may target a full input/output artifact or a declared schema
     group, and the compiler expands that group through the schema inventory
4. `renderer.py` and the checked-in refs under the example corpus prove the
   emitted readback shape.
5. `examples/README.md` and the live docs already teach this ladder through
   `examples/72_schema_group_invalidation`.
6. The historical Phase 4 worklog records prior targeted manifests for
   `68_*` through `72_*` and one prior full verification run, which is useful
   as provenance but does not replace fresh closeout verification in this plan.

The practical consequence is that the repo does not currently look like a
missing-compiler-surface branch. It looks like a mostly-landed compiler path
with stale framing on a few live surfaces and with compiler files now acting as
reopen-on-failure surfaces rather than as the default first edit target.

## 4.3 Object model + key abstractions

The relevant live abstractions are already explicit:

- `review_family` is not just naming convention; it is a first-class review
  declaration that rides the same review compiler path as ordinary `review`
- review case selection is represented through explicit selector configuration
  plus exhaustive review cases, not through an implicit
  `selected_contract.*`-style projection shim
- `route_only` and `grounding` are first-class authored declarations that lower
  through existing workflow/control-plane semantics
- `schema.groups` is the reusable typed owner for grouped invalidation sets
- downstream trust still flows through declared output carriers and
  `trust_surface`; these Phase 4 surfaces do not invent a second emitted
  contract channel

## 4.4 Observability + failure behavior today

The current preservation and drift signals are:

- manifest-backed positive and compile-negative proof in the example corpus,
  especially `68_*` through `72_*`
- `examples/69_case_selected_review_family/cases.toml`, which already proves
  both the positive render contract and compile-negative overlap/non-total case
  failures
- `examples/72_schema_group_invalidation/cases.toml`, which already proves
  concrete invalidation expansion and a dedicated `E371` current-artifact
  contradiction case
- `make verify-examples` as the full corpus signal
- `make verify-diagnostics` if diagnostics wording or mapping changes
- `cd editors/vscode && make` for resolver/tmLanguage/test parity
- `docs/COMPILER_ERRORS.md`, which currently says several Phase 4 failures
  still bucket under generic `E299`

Current drift or ambiguity visible from repo evidence:

- `docs/README.md` and `examples/README.md` already present the Phase 4 ladder
  as shipped through `examples/72_*`
- `AGENTS.md` still says the current shipped corpus ends at `examples/63_*`
- `docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md` still frames the
  remaining work as open closure, while also admitting the current Phase 4
  branch already has the relevant grammar/model/parser/compiler scaffolding
- `docs/SECOND_WAVE_LANGUAGE_NOTES.md` contains pre-Phase-4 rejection logic for
  separate `review_family`, `route_only`, and `grounding`, but it is not
  indexed as the primary live reference path

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. The only user-facing surface here is authoring, emitted text,
docs, diagnostics, and editor support.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

The target repo shape is one truthful split:

- `doctrine/` remains the only semantic owner path for these declarations
- manifest-backed examples remain the proof ladder for shipped behavior
- live docs teach the shipped Phase 4 boundary and examples through the true
  shipped corpus
- root instructions do not understate or contradict shipped coverage
- historical plans/notes remain historical and do not compete with live truth

If the audit finds residual code gaps, they land only in the existing semantic
owner files and immediately propagate to proof/docs/editor surfaces in the same
run. If the targeted manifests and source-gap classification both hold, the
implementation path should stay out of compiler code and close the feature by
converging truth surfaces plus running full verification.

## 5.2 Control paths (future)

The target control path does not add any new engine:

- `review_family` continues on the ordinary review compiler path
- case-selected exact review law remains explicit through `selector` and
  exhaustive `cases`
- `route_only` continues to lower through ordinary workflow-law currentness,
  route, and guarded-output validation
- `grounding` continues to lower through the same control-plane/output boundary
- `schema.groups.*` continues to own reusable restart surfaces consumed by
  workflow-law invalidation

The architectural delta is therefore not a new subsystem. It is completion and
truth convergence on the already-established compiler path, with explicit
re-entry into compiler files only when targeted revalidation proves a still-
missing promise.

## 5.3 Object model + abstractions (future)

The final model should be:

- one reusable review-family abstraction for shared critic scaffolds
- one explicit case-selection mechanism for mode-local subject/contract/current
  truth/route behavior
- one typed restart-set owner in `schema.groups`
- one emitted-contract boundary through ordinary outputs and `trust_surface`
- one classification pass for the source remaining-gap doc:
  - preserved baseline
  - genuine residual gap
  - non-gap / stale framing

No new wrapper contract, packet surface, invalidation-only declaration family,
or Lessons-specific declaration kind is allowed.

Execution default for the next stage:

- first classify the source gap doc against shipped reality
- re-run the targeted proof ladder that already exists for the two claimed
  remaining gaps
- only if that revalidation fails or reveals a missing explicit promise should
  implementation widen back into grammar/parser/model/compiler changes

## 5.4 Invariants and boundaries

- No second semantic control plane
- No Lessons-specific product vocabulary in the language
- No implicit dynamic contract wrapper in place of explicit cases
- No stale live docs or instructions teaching that these shipped surfaces are
  still future-only
- No code/doc/example/editor split-brain after closeout
- No silent regression in preserved baseline examples such as `57`, `63`,
  `68`, `69`, `70`, `71`, and `72`

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Scope source | `docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md` | remaining-gap classifications and closeout language | Treats two surfaces as remaining gaps, while also acknowledging current branch scaffolding | Line-by-line classify each claim as preserved baseline, residual real gap, or stale framing | The plan must close the full requested scope without mistaking stale docs for shipped truth | None unless wording is updated | Full corpus verify only if proof-facing examples/docs change |
| Canonical phase spec | `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md` | Phase 4 promised behavior | Defines the intended shipped Phase 4 contract | Use as the requested-scope boundary and check every explicit promise against live code/docs/examples | Prevent scope shrink and prevent inventing new scope | None | Targeted manifests around `68_*` through `72_*` |
| Grammar | `doctrine/grammars/doctrine.lark` | top-level declarations, `selector_block`, schema `groups:`, `invalidate_stmt` | Already declares the key Phase 4 syntax | Leave unchanged unless source-gap classification or targeted revalidation proves a still-missing authored-shape promise | Grammar is now a reopen-on-failure surface, not the default first edit | Possible only if residual syntax gap exists | Targeted manifests first, then `make verify-examples` |
| Parser/model | `doctrine/parser.py`, `doctrine/model.py` | `review_family_decl`, `route_only_decl`, `grounding_decl`, selector/case structures, schema groups | Already materializes the Phase 4 surfaces into typed objects | Leave unchanged unless the source-gap audit finds a typed-structure omission that the current manifests do not actually cover | Avoid fake completion based only on grammar acceptance, but also avoid unnecessary compiler churn | Possible only if residual semantic shape gap exists | Targeted manifests first, then `make verify-examples` |
| Compiler semantics | `doctrine/compiler.py` | route-only and grounding lowering, review-family case validation, schema-group invalidation resolution | Already resolves these surfaces through the canonical owner path | Treat as reopen-on-failure: edit only if targeted revalidation or line-by-line source-gap audit exposes a missing or contradictory semantic promise | This is the real shipped owner path and the only valid place for any residual code fix | Possible residual validation/lowering contract only if audit finds one | Targeted manifests first, then `make verify-examples` |
| Diagnostics | `doctrine/diagnostics.py`, `docs/COMPILER_ERRORS.md` | Phase 4 compile-failure mapping | Some failures still document under generic `E299` | Decide whether narrower stable codes are required or whether current mapping is acceptable | The error contract must be honest if behavior changed | Possible narrower error-code contract, otherwise none | `make verify-diagnostics` if touched |
| Proof ladder | `examples/57_schema_review_contracts`, `examples/63_schema_artifacts_and_groups`, `examples/68_*` through `examples/72_*`, `examples/README.md` | positive and compile-negative corpus | Corpus already teaches and proves much of the shipped story, including explicit positive and negative cases for the two claimed remaining gaps | Re-run targeted manifests first and classify any mismatch before touching compiler code; add or tighten examples only if a source-gap promise is still not proved cleanly | Manifest-backed proof is the first closeout signal and the gate for reopening code | Possible example/ref additions only if residual proof gap exists | Targeted manifests, then `make verify-examples` |
| Live docs | `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/REVIEW_SPEC.md`, `docs/WORKFLOW_LAW.md`, `docs/AGENT_IO_DESIGN_NOTES.md` | shipped language teaching path | Already teaches the dedicated Phase 4 surfaces as shipped | Converge any remaining wording mismatch or stale framing; otherwise preserve | Repo needs one live explanation of shipped behavior | None unless wording changes expose a real contract adjustment | Spot-check named examples; full corpus verify if doc/example coupling changes |
| Repo instructions | `AGENTS.md` | shipped corpus statement and repo truth guidance | Still says the current shipped corpus ends at `examples/63_*` | Update if implementation closeout confirms the live shipped corpus statement should match `examples/72_*` | This is a live instruction surface inside scope and currently conflicts with live docs | None | No code tests; full relevant verify if docs/examples changed |
| Historical context | `docs/archive/PHASE4_REVIEW_ROUTE_ONLY_GROUNDING_CONTROL_PLANE_COMPLETION_2026-04-11.md`, `docs/archive/PHASE4_REVIEW_ROUTE_ONLY_GROUNDING_CONTROL_PLANE_COMPLETION_2026-04-11_WORKLOG.md`, `docs/SECOND_WAVE_LANGUAGE_NOTES.md` | old completion and pre-Phase-4 reasoning | Useful provenance, but not live truth | Keep historical unless they are still linked or phrased in a way that confuses live guidance; do not delete without restore-point commit | Need clean live/historical separation, not docs archaeology in the live path | None | N/A unless docs navigation changes |
| Editor parity | `editors/vscode/resolver.js`, `editors/vscode/syntaxes/doctrine.tmLanguage.json`, `editors/vscode/tests/` | keyword detection, declaration parsing, syntax coverage | Already includes the new declaration families and keywords | Confirm no lag relative to live compiler truth; patch only if a residual mismatch is found | Full closeout includes editor parity when relevant | Possible resolver/syntax contract only if lag exists | `cd editors/vscode && make` |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `doctrine/grammars/doctrine.lark` -> `doctrine/parser.py` ->
    `doctrine/model.py` -> `doctrine/compiler.py`, with
    `examples/README.md` plus the manifest-backed corpus as proof and the live
    docs set as the teaching layer.
- Default implementation posture:
  - revalidate the shipped proof ladder and classify the source gap doc first
  - update live truth surfaces next if that proof holds
  - reopen compiler files only on proof-backed failure or uncovered promise
- Deprecated APIs (if any):
  - None identified yet. The likely cleanup is stale framing, not a public API
    rename.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - No code-path delete is justified from repo evidence so far.
  - Any eventual live-doc deletion must obey the restore-point commit rule.
- Capability-replacing harnesses to delete or justify:
  - None. Do not add any new harness to "prove" what the existing corpus and
    compiler path already can prove.
- Live docs/comments/instructions to update or delete:
  - `docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md` if its role or
    phrasing needs to change after the audit verdict
  - `AGENTS.md` if the shipped-corpus statement remains stale after closeout
  - `docs/COMPILER_ERRORS.md` if diagnostic mapping changes
  - any live doc still phrasing these surfaces as future-only once the
    implementation verdict is final
- Behavior-preservation signals for refactors:
  - targeted manifests for `examples/57_*`, `63_*`, and `68_*` through `72_*`
  - `make verify-examples`
  - `make verify-diagnostics`
  - `cd editors/vscode && make`

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Live truth | `AGENTS.md` and `docs/README.md` / `examples/README.md` | one shared shipped-corpus statement | Prevent repo instructions from understating shipped Phase 4 proof coverage | include |
| Source-gap framing | `docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md` | one explicit classification of baseline vs residual gap vs stale framing | Prevent the source scope doc from remaining an accidental competing truth surface | include |
| Phase 4 teaching path | `docs/LANGUAGE_REFERENCE.md`, `docs/REVIEW_SPEC.md`, `docs/WORKFLOW_LAW.md`, `docs/AGENT_IO_DESIGN_NOTES.md` | dedicated declarations as wrappers over existing semantics | Prevent split-brain docs where one live guide teaches a second control plane | include |
| Diagnostics contract | `docs/COMPILER_ERRORS.md` | explicit error-code story for residual Phase 4 failures | Prevent generic error wording from drifting away from the real compile behavior | defer unless implementation changes diagnostics |
| Historical notes | `docs/SECOND_WAVE_LANGUAGE_NOTES.md`, archive plan/worklog docs | explicit historical/non-live role | Prevent background notes from being mistaken for live doctrine without forcing unnecessary deletions now | defer |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Revalidate the shipped Phase 4 baseline and classify the source gap doc

Status: COMPLETE

* Goal:
  Decide, from repo evidence rather than stale framing, whether any semantic
  code work actually remains for the two claimed language gaps.
* Work:
  - Re-run the targeted manifest-backed proof ladder that already corresponds
    to the claimed remaining-gap surfaces and preserved prerequisites:
    `examples/57_schema_review_contracts`,
    `examples/63_schema_artifacts_and_groups`,
    `examples/68_review_family_shared_scaffold`,
    `examples/69_case_selected_review_family`,
    `examples/70_route_only_declaration`,
    `examples/71_grounding_declaration`, and
    `examples/72_schema_group_invalidation`.
  - Audit `docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md` line by
    line against:
    - `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md`
    - the live compiler path under `doctrine/`
    - the current example ladder and live docs
  - Classify every source-gap claim as one of:
    - preserved already-shipped baseline
    - proof-backed remaining semantic gap
    - stale framing / non-gap requiring truth convergence
  - Record the exact reopen file set if any proof-backed semantic gap still
    exists; otherwise keep compiler files closed for now.
* Verification (smallest signal):
  - targeted manifest checks for `57`, `63`, and `68` through `72`
* Docs/comments (propagation; only if needed):
  - none yet except truthful worklog/plan updates if Phase 1 finds a real
    reopen condition
* Exit criteria:
  - the remaining-gap classification is complete
  - either a concrete residual semantic gap is identified with exact file
    owners, or the implementation posture remains convergence-first with no
    compiler reopen
* Rollback:
  - revert any premature claim changes that outran the Phase 1 evidence and
    return to the last truthful classification
Completed work:
  - reran targeted manifests for `examples/57_schema_review_contracts`,
    `examples/63_schema_artifacts_and_groups`, and `examples/68_*` through
    `examples/72_*`
  - confirmed all targeted preserved-baseline and claimed-gap proofs passed
  - classified the source gap doc as closure-note truth that still needed live
    wording convergence, not residual compiler implementation

## Phase 2 — Close any proof-backed residual semantic gap in the canonical owner path

Status: COMPLETE

* Goal:
  Ship any still-missing semantic promise from the source gap doc through the
  existing Doctrine owner path, but only if Phase 1 proved that such a gap
  still exists.
* Work:
  - If Phase 1 reopened compiler work, patch only the exact required surfaces
    under:
    - `doctrine/grammars/doctrine.lark`
    - `doctrine/parser.py`
    - `doctrine/model.py`
    - `doctrine/compiler.py`
    - `doctrine/renderer.py`
    - `doctrine/diagnostics.py`
    - `examples/` and `editors/vscode/` when the changed behavior requires it
  - Keep the implementation Doctrine-native:
    - explicit typed cases over dynamic wrapper contracts
    - `schema.groups` over any new invalidation-only declaration kind
    - ordinary output/trust surfaces over any new packet or shadow channel
  - If Phase 1 found no residual semantic gap, mark this phase a truthful no-op
    and proceed without touching compiler code.
* Verification (smallest signal):
  - rerun the impacted targeted manifests immediately after each semantic fix
  - run `make verify-diagnostics` if diagnostic behavior or wording changes
  - run `cd editors/vscode && make` if editor files change in this phase
* Docs/comments (propagation; only if needed):
  - update any touched live language guide or compiler-error reference in the
    same phase when the shipped behavior changes
  - add only high-leverage boundary comments if the implementation introduces a
    non-obvious invariant
* Exit criteria:
  - every proof-backed residual semantic gap from Phase 1 is closed and
    manifested in the corpus, or the phase is explicitly no-op because no such
    gap existed
* Rollback:
  - revert the residual semantic edits while keeping the Phase 1 classification
    evidence intact
Completed work:
  - no-op by evidence: Phase 1 found no proof-backed residual semantic gap, so
    compiler files stayed closed

## Phase 3 — Converge live docs and instruction truth to the shipped verdict

Status: COMPLETE

* Goal:
  Eliminate the in-scope split truth so the repo teaches one honest story about
  the remaining-gap verdict.
* Work:
  - Update `docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md` so it no
    longer reads like a competing live truth surface once the classification is
    final
  - Update `AGENTS.md` if the shipped-corpus statement should now match the
    live docs and examples through `examples/72_*`
  - Update any in-scope live guides that still phrase these surfaces as
    future-only or otherwise contradict the final shipped verdict:
    - `docs/LANGUAGE_REFERENCE.md`
    - `docs/REVIEW_SPEC.md`
    - `docs/WORKFLOW_LAW.md`
    - `docs/AGENT_IO_DESIGN_NOTES.md`
    - `docs/COMPILER_ERRORS.md` if diagnostics changed or if the current Phase
      4 error-code story needs explicit clarification
  - Keep historical notes historical. Do not delete any docs in this phase
    without the required restore-point commit.
* Verification (smallest signal):
  - cross-check the updated live docs against `examples/README.md`, the
    targeted Phase 4 manifests, and the canonical compiler owner path
* Docs/comments (propagation; only if needed):
  - this phase is the primary live-doc and instruction convergence phase
* Exit criteria:
  - no in-scope live doc or instruction file contradicts the final shipped
    verdict
  - any remaining historical notes are clearly non-live rather than accidental
    competing doctrine
* Rollback:
  - revert the live-truth edits while keeping semantic proof and classification
    intact
Completed work:
  - updated `docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md` from
    open-gap framing to shipped closure/classification truth
  - repaired stale related-doc links in that doc
  - updated `AGENTS.md` so the shipped-corpus statement matches the live docs
    and example ladder through `examples/72_schema_group_invalidation`

## Phase 4 — Run full closeout verification and record the implementation audit

Status: COMPLETE

* Goal:
  Prove the full remaining-gap closeout end to end and leave an authoritative
  audit trail for `implement-loop`.
* Work:
  - Run `uv sync`
  - Run `npm ci`
  - Run `make verify-examples`
  - Run `make verify-diagnostics` when diagnostics changed
  - Run `cd editors/vscode && make` when editor files changed
  - Update the canonical worklog and implementation-audit truth based on the
    actual results
* Verification (smallest signal):
  - the commands above are the phase verification
* Docs/comments (propagation; only if needed):
  - update the worklog and implementation-audit surfaces with exact results,
    failures, or reopened work
* Exit criteria:
  - all required closeout commands for the touched surfaces have run
  - the plan/worklog/audit truth matches the actual repo state
  - the doc is ready for fresh `audit-implementation`
* Rollback:
  - if any required command fails, do not cash out; reopen the relevant prior
    phase with the exact blocker recorded
* Completed work:
  - ran `uv sync`
  - ran `npm ci`
  - ran `make verify-examples`; the full manifest-backed corpus passed through
    `examples/72_schema_group_invalidation` with no surfaced inconsistencies
  - did not run `make verify-diagnostics` because no diagnostics surfaces
    changed in this implementation pass
  - did not run `cd editors/vscode && make` because no editor files changed in
    this implementation pass
  - synced the worklog to the actual closeout result; this fresh
    `audit-implementation` pass confirmed the clean code-complete outcome
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

- Avoid verification bureaucracy; use the existing Doctrine corpus and build
  surfaces.
- Because the requested finish is "fully implemented and tested," final
  closeout should run the full relevant repo checks, not only targeted cases.

## 8.1 Unit tests (contracts)

- Start with targeted manifest-backed example checks for
  `examples/57_schema_review_contracts`,
  `examples/63_schema_artifacts_and_groups`, and `examples/68_*` through
  `examples/72_*` to decide whether compiler files need reopening at all.
- Use targeted manifest-backed example checks while iterating on any specific
  remaining-gap surface after that initial revalidation.
- Run `make verify-diagnostics` if diagnostics or diagnostic wording change.

## 8.2 Integration tests (flows)

- Run `make verify-examples` for final closeout.
- Preserve the relevant baselines around reviews, workflow law, and schema
  invalidation while auditing any residual delta.

## 8.3 E2E / device tests (realistic)

- If `editors/vscode/` changes, run `cd editors/vscode && make`.
- No separate device test surface is expected for this language/compiler work.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

Hard cutover only. Once the remaining-gap story is fully implemented and
verified, the repo should have one live truth and any stale parallel story
should be updated, archived, or retired honestly.

## 9.2 Telemetry changes

No product telemetry is expected. The relevant operational signals are the
existing verify/build surfaces and any compile-negative corpus additions needed
for honest proof.

## 9.3 Operational runbook

- Start with `uv sync` and `npm ci`.
- Use targeted manifest checks during implementation.
- Finish with the required repo verification commands for the touched surfaces.
- If doc retirement is required, take the mandated restore-point commit before
  deletion.

# 10) Decision Log (append-only)

## 2026-04-11 - Treat the remaining-gap doc as scope boundary, not shipped truth

### Context

The user asked for a full implementation plan for
`docs/archive/LESSONS_PORT_REMAINING_LANGUAGE_GAPS_2026-04-11.md`, but the live repo
already shows strong evidence that much of Phase 4 is implemented.

### Options

- Assume the doc is fully current and plan only net-new code work.
- Assume the live repo is already complete and skip implementation planning.
- Treat the doc as requested-scope boundary while grounding shipped truth in
  `doctrine/`, examples, docs, diagnostics, and editor surfaces.

### Decision

Treat the gap doc as the authoritative scope boundary and the live repo as the
authoritative shipped-state boundary.

### Consequences

The plan preserves the full requested scope while leaving room for the audit to
discover that some residual work is convergence rather than new code.

### Follow-ups

- Confirm the North Star.
- Run `research` and `deep-dive` against the live repo before finalizing the
  phase plan.

## 2026-04-11 - Full closure includes truth convergence, not just compiler code

### Context

The main uncertainty is not only whether the language features exist, but
whether the repo tells one honest story about them.

### Options

- Limit the plan to compiler files only.
- Include docs/examples/editor/instruction convergence as part of full closure.

### Decision

Include compiler, proof, docs, and editor/instruction convergence in the same
full-scope plan.

### Consequences

Implementation may widen beyond the obvious language files, but it stays within
architectural convergence rather than adding new product capability.

### Follow-ups

- Audit live instruction surfaces, especially where shipped corpus coverage is
  currently understated.

## 2026-04-11 - Deep-dive pass 2 sets convergence-first implementation posture

### Context

Deep-dive pass 1 confirmed that the live repo already contains first-class
grammar, parser, model, compiler, docs, example, and editor surfaces for the
Phase 4 declarations named by the source gap doc. The remaining planning
question was whether implementation should default to compiler edits or to
revalidation plus truth convergence.

### Options

- Default to compiler edits first because the source doc still says "remaining"
- Default to convergence-first and reopen compiler files only when targeted
  proof or line-by-line source-gap classification exposes a real missing
  semantic promise

### Decision

Default to convergence-first. Treat compiler files as reopen-on-failure
surfaces while the targeted manifests and source-gap classification decide
whether any semantic code work still remains.

### Consequences

Phase planning can now build from a concrete default order instead of a vague
"maybe code, maybe docs" posture. If targeted proof stays green, the main work
becomes source-gap classification plus live doc/instruction convergence and
full verification.

### Follow-ups

- Re-run the targeted manifests for the two claimed remaining-gap families at
  implementation time before touching compiler code.
- Use phase planning to separate required live-truth updates from deferred
  historical-note cleanup.

## 2026-04-11 - Phase plan locks the reopen gate for compiler work

### Context

After deep-dive pass 2, the remaining risk was still that implementation might
slide back into speculative compiler editing even though the live repo already
contains a strong shipped Phase 4 path.

### Options

- Start implementation in compiler files and let later verification decide
  whether those edits were necessary
- Make the existing targeted manifests and source-gap classification the gate
  that must fail before compiler files reopen

### Decision

Use the targeted manifests plus source-gap classification as the explicit
reopen gate. Phase 1 revalidates and classifies; Phase 2 edits compiler code
only on proof-backed failure.

### Consequences

The implementation order is now concrete and scope-safe: prove the baseline,
close any residual semantic mismatch only if one survives proof, then converge
live truth and run full repo verification.

### Follow-ups

- Let `implement-loop` execute the phases in order.
- Reopen the audit immediately if any full closeout check contradicts the Phase
  1 classification.
