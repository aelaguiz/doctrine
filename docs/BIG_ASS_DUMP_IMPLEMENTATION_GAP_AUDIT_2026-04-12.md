---
title: "Doctrine - Big Ass Dump Full Implementation - Architecture Plan"
date: 2026-04-12
status: active
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: parity_plan
related:
  - docs/big_ass_dump.md
  - docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md
  - docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md
  - docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md
  - docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/WORKFLOW_LAW.md
  - docs/REVIEW_SPEC.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/README.md
  - docs/COMPILER_ERRORS.md
  - examples/README.md
  - doctrine/grammars/doctrine.lark
  - doctrine/parser.py
  - doctrine/model.py
  - doctrine/compiler.py
  - doctrine/emit_common.py
  - doctrine/emit_flow.py
  - doctrine/renderer.py
  - doctrine/verify_corpus.py
  - editors/vscode/README.md
  - editors/vscode/resolver.js
  - editors/vscode/syntaxes/doctrine.tmLanguage.json
---

# TL;DR

## Outcome

Doctrine closes the real remaining implementation gaps represented by
`docs/big_ass_dump.md` without narrowing the dump to only the easiest reusable
subset. The work is only done when every still-relevant dump feature family is
either proved already shipped by repo evidence or shipped end to end through
`doctrine/`, manifest-backed examples, live docs, diagnostics, and VS Code
parity where relevant.

## Problem

`docs/big_ass_dump.md` is a 4,700+ line mixed design dump that combines early
and later design passes, generic Doctrine ideas, and Lessons-flavored examples.
Current shipped truth is split across the Doctrine implementation, the live
docs set, the numbered example corpus, and the repo-local VS Code extension.
If this work starts from a narrowed read of the dump, or from docs-only
evidence, we will miss genuine gaps and claim completion too early.

## Approach

Treat the dump as exhaustive design input, audit every materially distinct
feature family against shipped repo truth, and then implement only the genuine
Doctrine-side gaps through the existing canonical owners. Preserve fidelity by
translating dump examples that use Lessons or poker jargon into generic public
Doctrine examples instead of dropping their semantics.

## Plan

1. Freeze the full dump-family matrix and the last open architecture verdicts
   so the remaining work is explicit and finite.
2. Ship the chosen generic decision / candidate-pool solution through the
   canonical Doctrine owners only.
3. Resolve reusable preservation bundles with one honest outcome: ship the
   abstraction or explicitly reject it in favor of existing workflow law.
4. Add or repair generic public proof, live docs, and same-wave editor parity
   wherever the final missing surfaces or shipped-family reconciliations need
   it.
5. Run the full verification sweep and close the parity loop so code, examples,
   docs, diagnostics, and editor behavior all tell the same story.

## Implementation Update (2026-04-12)

- A first-class generic `decision` declaration plus concrete-agent
  `decision:` attachment now ship through grammar, parser, model, compiler,
  docs, examples, and VS Code parity.
- Reusable preservation bundles were closed as an explicit no-new-surface
  verdict: Doctrine reuses preservation semantics through named workflow-law
  subsections plus inheritance and patching instead of adding a second
  declaration family.
- Verification passed for the targeted preservation baseline, the pre-existing
  `analysis` family, the new `decision` family, `cd editors/vscode && make`,
  and the full `make verify-examples` corpus run.

## Non-negotiables

- No narrowing to "non-Lessons reusable Doctrine ideas only."
- No importing product names, internal skill slugs, poker-domain jargon, or
  company-specific workflow language into public Doctrine docs or examples.
- No "already implemented" claim unless code, examples, docs, and editor truth
  agree for the relevant surface.
- No fallback shims, shadow declarations, or second owner paths.
- No code-only completion; examples, tests, docs, and editor parity are part
  of the shipped surface.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-12
Verdict (code): COMPLETE
Manual QA: pending (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None. The earlier Phase 4 docs blocker is closed in the current repo state.
  - Evidence anchors:
    - `docs/README.md:3`
    - `docs/README.md:42`
    - `docs/LANGUAGE_REFERENCE.md:24`
    - `docs/LANGUAGE_REFERENCE.md:228`
    - `docs/WORKFLOW_LAW.md:246`
    - `examples/README.md:39`
    - `editors/vscode/README.md:58`
    - `docs/BIG_ASS_DUMP_IMPLEMENTATION_GAP_AUDIT_2026-04-12_WORKLOG.md:48`
    - `docs/BIG_ASS_DUMP_IMPLEMENTATION_GAP_AUDIT_2026-04-12_WORKLOG.md:70`
  - Plan expects:
    - the shipped `decision` wave, the preservation-reuse verdict, the live
      docs path, the proof corpus, and editor parity to reconcile into one
      final completion story
  - Code reality:
    - `docs/README.md` now points the live corpus at
      `examples/74_decision_attachment` and marks the 01-04 phase docs as
      historical implementation notes; `docs/LANGUAGE_REFERENCE.md`,
      `docs/WORKFLOW_LAW.md`, `examples/README.md`, and
      `editors/vscode/README.md` all describe the shipped `decision` surface
      and the no-new-surface preservation verdict; the worklog records passing
      targeted manifests, `cd editors/vscode && make`, and `make verify-examples`
  - Fix:
    - no code fix required; keep the final docs cold read as a manual
      non-blocking follow-up

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Do one final cold read of the shipped docs path against `doctrine/` and the
  active corpus.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-12
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-12
recommended_flow: implement-loop
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly, Doctrine will have one honest answer to the
question "what from `docs/big_ass_dump.md` is still not implemented?":

- every materially distinct dump feature family will be classified against
  shipped repo truth
- every genuinely missing Doctrine-side capability will ship through the normal
  `doctrine/` owner paths
- every new or corrected surface will have manifest-backed proof, live docs
  coverage, and VS Code parity when the surface affects the editor
- domain-flavored examples from the dump will be preserved semantically through
  generic public Doctrine examples rather than being dropped

Initial repo evidence already suggests that many second-wave features now ship,
including `document`, `analysis`, `schema`, `review_family`, `route_only`,
`grounding`, `render_profile`, `properties`, explicit guard shells, typed
row/item schemas, and currentness/preservation law. The likely remaining gap
set appears smaller than the dump suggests, but this claim stays false until
the full audit proves that with code-level evidence across the whole dump.

The claim is false if:

- the audit prefilters the dump instead of classifying it exhaustively
- a dump feature is marked "shipped" based only on adjacent docs or vague
  resemblance
- a newly added feature lands without examples, docs, and verification
- the repo ends up with two competing explanations of the same seam

## 0.2 In scope

- A full end-to-end audit of `docs/big_ass_dump.md`, including repeated and
  mixed-era sections, so the repo has one canonical classification of every
  material feature family the dump proposes.
- Any missing generic Doctrine declaration, workflow-law surface, render/readback
  behavior, or validation rule needed to preserve the dump's intended feature
  set faithfully.
- Grammar, parser, model, compiler, renderer, emit, diagnostics, and
  verification work needed to ship the missing surfaces through the existing
  Doctrine owners.
- Manifest-backed positive examples, compile-negative coverage where needed, and
  proof updates in `examples/README.md`.
- Evergreen docs updates across the live docs set so the public reference path
  reflects shipped truth after the cutover.
- Repo-local VS Code syntax, resolver, alignment, tests, and README follow
  through for any affected syntax or addressability changes.
- Genericizing dump examples that currently use Lessons- or poker-specific
  names so their semantics can be proved in public Doctrine examples without
  violating repo authoring rules.
- Architectural convergence needed to keep one source of truth across code,
  examples, docs, and editor tooling.

## 0.3 Out of scope

- Narrowing away dump sections just because their motivating examples come from
  Lessons.
- Importing Lessons-specific artifact names, poker pedagogy, or internal
  workflow jargon into Doctrine's public examples or evergreen docs.
- Implementing a Lessons pack, poker content system, or other domain pack
  inside this repo beyond the generic language features and generic examples
  required to preserve the dump's semantics.
- Adding wrappers, compatibility layers, fallback renderers, or a second
  control-plane architecture to simulate completion.
- Unrelated doctrine feature work that is not needed to close the
  `big_ass_dump`-derived gap set honestly.

## 0.4 Definition of done (acceptance evidence)

- This plan's research and deep-dive sections contain one exhaustive feature
  matrix for `docs/big_ass_dump.md`, and no material dump family remains
  uncategorized.
- Every missing Doctrine-side capability identified by that audit ships through
  `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`,
  `doctrine/model.py`, `doctrine/compiler.py`, `doctrine/emit_common.py`,
  `doctrine/emit_flow.py`, and `doctrine/renderer.py` as needed.
- Every new or corrected surface has manifest-backed proof in `examples/`, with
  positive and negative coverage where the failure semantics matter.
- The live docs path is updated so `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md`, and
  `examples/README.md` match shipped truth.
- Any editor-facing syntax or resolver changes are reflected in
  `editors/vscode/` and `cd editors/vscode && make` passes.
- Final verification includes:
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics change
  - targeted manifest-backed verification while developing new proof cases
  - `cd editors/vscode && make` when editor surfaces change

Behavior-preservation evidence:

- the current shipped corpus through `examples/74_decision_attachment`
  stays green unless a specifically documented bug fix changes behavior
- previously shipped diagnostics remain fail loud and deterministic
- the VS Code extension continues to resolve and highlight previously shipped
  surfaces correctly while expanding to any new ones

## 0.5 Key invariants (fix immediately if violated)

- No scope narrowing before the whole dump is classified.
- One owner path per feature family.
- One live truth path across shipped code, examples, docs, and editor tooling.
- Public Doctrine examples stay generic even when they preserve domain-flavored
  semantics from the dump.
- No fallback or shim path; unsupported or contradictory authoring must fail
  loud.
- No "implemented in code but not in proof/docs/editor" split.
- New surfaces must feel like Doctrine, not like one-off sidecars bolted onto
  the language.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Preserve full dump fidelity at the feature-family level before narrowing
   implementation scope.
2. Ship only the genuinely missing generic Doctrine work, but ship it fully
   with examples, tests, docs, and editor parity.
3. Keep public Doctrine surfaces generic while preserving the semantics of the
   dump's strongest motivating examples.
4. Reuse the existing Doctrine architecture from phases 1 through 4 rather than
   inventing a second language or control-plane path.
5. Preserve the already shipped corpus and fail-loud behavior while expanding
   the language.

## 1.2 Constraints

- `docs/big_ass_dump.md` is a raw historical dump with repeated sections,
  mixed design eras, and domain-flavored examples, so it cannot be treated as a
  ready-to-implement checklist without audit work.
- The repo already ships a substantial second-wave surface, so gap finding must
  distinguish true missing features from older text that later shipped under a
  different shape.
- Repo authoring rules forbid product names, internal skill slugs, and
  company-specific workflow jargon in public docs and examples.
- Shipped truth lives in `doctrine/` and the manifest-backed corpus, not in
  proposal prose alone.
- Diagnostics and VS Code parity are explicit parts of Doctrine's language
  surface, not optional follow-up polish.

## 1.3 Architectural principles (rules we will enforce)

- Audit the whole dump against repo truth before finalizing the missing scope.
- Reuse existing Doctrine families where they preserve semantics honestly; add
  a new generic surface only when the shipped ones cannot carry the dump's
  intent without loss.
- Translate domain-heavy examples into generic public examples instead of
  either copying the domain jargon or dropping the example entirely.
- Keep one compiler path, one render path, one docs path, one corpus path, and
  one editor parity path.
- Prefer fail-loud boundaries, explicit deletes, and direct parity updates over
  compatibility shims or dual truths.

## 1.4 Known tradeoffs (explicit)

- A full audit-first pass is slower than immediately implementing the two most
  obvious gaps, but it is the only honest way to avoid losing fidelity.
- Some dump ideas may prove to be already shipped under existing Doctrine
  surfaces; proving that still requires docs and example reconciliation work.
- Genericizing Lessons-flavored examples increases example-design effort, but
  it is the only way to preserve semantics while following Doctrine's public
  authoring rules.
- Some missing capability may land as an extension to an existing family rather
  than as a new top-level declaration. The audit has to justify that choice
  explicitly.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already ships a large second-wave surface through the live docs and
current repo code:

- typed `document` plus `structure:` attachments
- first-class `analysis`
- first-class `schema`
- `properties`, explicit guard shells, and `render_profile`
- typed row/item schemas
- `review_family`
- `route_only`
- `grounding`
- workflow-law surfaces for currentness, preservation, invalidation,
  `support_only`, and `ignore ... for rewrite_evidence`
- a manifest-backed example corpus through `examples/74_decision_attachment`
- a repo-local VS Code extension that mirrors the shipped grammar and resolver

At the same time, `docs/big_ass_dump.md` still sits in the repo as a raw design
input whose strongest examples are Lessons-flavored and whose text spans more
than one design era.

## 2.2 What’s broken / missing (concrete)

- The repo does not yet have one canonical, exhaustive audit that ties every
  material dump feature family to current shipped proof or missing work.
- A same-day aborted audit narrowed the scope to "non-Lessons reusable
  Doctrine ideas only," which is not faithful to the current request and cannot
  serve as the planning baseline.
- At least some dump proposals still appear to have no obvious shipped generic
  Doctrine surface today, most notably a first-class decision / candidate-pool
  family and reusable preservation bundles.
- Some richer dump patterns may be only partially represented today through
  adjacent features rather than explicit generic surfaces, and that distinction
  has not been audited across the whole dump.
- Without that audit, the repo cannot honestly say whether the remaining work
  is tiny, moderate, or larger than the obvious two-gap shortlist.

## 2.3 Constraints implied by the problem

- The fix must start from whole-dump classification, not from a narrowed gap
  list.
- The implementation path must stay generic Doctrine, even when the motivating
  examples come from a specific domain pack.
- Code, examples, docs, diagnostics, and editor parity must move together or
  the repo will keep split-brain truth.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- No external paper or system is required for the planning baseline. Repo-local
  evidence is the primary ground truth because the request is specifically to
  finish implementing the unimplemented parts of `docs/big_ass_dump.md` inside
  this repo.
- `docs/big_ass_dump.md` is the exhaustive historical design-input anchor to
  classify, not the shipped truth surface to trust blindly.
- `docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md` through
  `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md` are
  adopted as the current implementation-order explanation of the second-wave
  language. They are useful because they describe how the repo intended the
  shipped work to be grouped, but they still defer to `doctrine/` plus the
  manifest-backed corpus when wording and code disagree.
- `docs/LANGUAGE_MECHANICS_SPEC.md` is useful only as historical pressure. It
  already records some formerly-proposed features such as `properties`,
  `render_profile`, `review_family`, `route_only`, and `grounding` as shipped,
  so it reinforces that `big_ass_dump` spans multiple design eras and cannot be
  treated as a current missing-features list without audit.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors:
  - `doctrine/grammars/doctrine.lark` defines the shipped top-level declaration
    surface. Repo search shows real grammar owners for `render_profile`,
    `route_only`, `grounding`, `review_family`, `analysis`, `schema`,
    `document`, `properties`, readable `guard`, `item_schema`, and
    `row_schema`, but no top-level `decision` declaration family and no
    reusable `preservation` declaration family.
  - `doctrine/parser.py` and `doctrine/model.py` are the AST truth for what the
    compiler can actually parse and carry. Repo search shows explicit parser and
    model support for `render_profile`, `route_only`, `grounding`,
    `review_family`, readable properties/guards, and row/item schemas, which
    strengthens the conclusion that these are shipped rather than still
    proposal-only.
  - `doctrine/compiler.py` is the semantic owner for workflow law, review,
    schema groups, currentness, preservation, invalidation, render-profile
    lowering, and readable descendant addressability. It already contains the
    fail-loud checks for `current artifact`, `own only`, `preserve exact`,
    schema-group invalidation, route-only validation, grounding refs, and
    review-family resolution that the dump spends prose on.
  - `doctrine/renderer.py` and `doctrine/emit_common.py` own natural emitted
    Markdown. These are the canonical readback surfaces for deciding whether any
    remaining dump feature still needs renderer work instead of just docs or
    examples.
  - `doctrine/emit_flow.py` and `doctrine/flow_renderer.py` are the flow-output
    owners. Any genuinely new declaration family has to be audited here too so
    the plan does not accidentally create a markdown-only feature that silently
    drifts from flow emission.
  - `doctrine/diagnostics.py` and `doctrine/diagnostic_smoke.py` are the
    fail-loud diagnostic owners.
  - `doctrine/verify_corpus.py` plus `examples/**` are the authoritative proof
    surfaces.
- Live docs anchors:
  - `docs/LANGUAGE_REFERENCE.md` for the shipped declaration inventory
  - `docs/WORKFLOW_LAW.md` for preservation, currentness, invalidation, and
    related law surfaces
  - `docs/REVIEW_SPEC.md` for review and review-family truth
  - `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/README.md`, and
    `docs/COMPILER_ERRORS.md` for the public shipped reference path
- Editor parity anchors:
  - `editors/vscode/resolver.js`
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json`
  - `editors/vscode/language-configuration.json`
  - `editors/vscode/scripts/validate_lark_alignment.py`
- Existing patterns to reuse:
  - `examples/README.md` already indexes examples `54` through `73` as proof for
    `analysis`, owner-aware `schema:` / `structure:`, document blocks and
    descendants, render profiles, compact `properties`, row/item schemas,
    `review_family`, dedicated `route_only`, dedicated `grounding`,
    schema-group invalidation, and flow visualization. Those examples are the
    reuse baseline for proving "already shipped" instead of making broad doc
    claims.
  - `docs/WORKFLOW_LAW.md` already documents `current artifact`, `current none`,
    `own only`, `preserve exact`, `preserve decisions`, `ignore ... for
    rewrite_evidence`, invalidation, and schema groups. That means reusable
    preservation semantics already ship as statements even if reusable
    preservation bundles may not.
  - `docs/REVIEW_SPEC.md` already documents `review_family` and case-selected
    families, so critic-style dump ideas should default to review-family reuse
    before proposing anything new.
  - `editors/vscode/resolver.js` already mirrors `render_profile`,
    `review_family`, `route_only`, `grounding`, readable properties/guards, and
    row/item schema descendants. Any remaining syntax work should extend this
    path rather than inventing editor-only detection.
  - Generic public examples remain the correct translation target even when a
    private domain motivated the original design pressure in the dump.
- Canonical owner path / owner to reuse:
  - `doctrine/grammars/doctrine.lark` + `doctrine/parser.py` +
    `doctrine/model.py` should own any genuinely new declaration family or new
    workflow-law surface.
  - `doctrine/compiler.py` should own any new semantic validation, lowering,
    addressability, or preservation behavior.
  - `doctrine/renderer.py` + `doctrine/emit_common.py` + `doctrine/emit_flow.py`
    should own any new readback or flow consequences.
  - `examples/**` + `doctrine/verify_corpus.py` should remain the proof gate.
  - `editors/vscode/**` should remain the editor parity gate.
- Duplicate or drifting paths relevant to this change:
  - `docs/big_ass_dump.md` is a historical design dump, while the live shipped
    story lives in `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`,
    `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`, and the example corpus. This
    is the main drift seam the audit must reconcile.
  - The four phase docs under `docs/` are implementation-order explanations,
    not the primary shipped truth. If any remaining gap changes the language
    boundary they describe, those docs must be updated together with the live
    docs instead of left as stale quasi-truth.
  - The aborted same-day audit at this `DOC_PATH` previously narrowed scope to a
    non-Lessons subset. That narrowed interpretation is a local drift surface
    that must stay retired.
- Capability-first opportunities before new tooling:
  - extend existing `analysis`, `schema`, `document`, `review_family`,
    workflow-law preservation/currentness surfaces, and `render_profile` before
    blessing a new top-level declaration family
  - use generic public examples to preserve the dump's semantics before
    considering any domain-pack import or private-jargon copy
  - reuse existing flow emission and editor parity hooks before adding a new
    support harness
- Behavior-preservation signals already available:
  - `make verify-examples` protects the current shipped corpus, including the
    second-wave examples already indexed in `examples/README.md`
  - targeted manifest-backed runs protect the smallest changed proof surface
  - `make verify-diagnostics` protects diagnostic drift when compiler errors
    change
  - `cd editors/vscode && make` protects syntax, resolver, and alignment parity
  - checked-in `example_73_flow_visualizer_showcase` flow artifacts provide a
    concrete signal if any new declaration affects flow emission

## 3.3 Open questions from research

- Does the dump's decision / candidate-pool idea require a new top-level
  declaration, or can an extension to existing `analysis`, `schema`,
  `document`, or workflow-law surfaces preserve the semantics honestly?
- Are reusable preservation bundles a genuine missing abstraction, or does the
  current combination of workflow law plus inheritance already cover the dump's
  reuse goal well enough?
- Pass 2 targeted proof shows the dump's render-template pressure is already
  carried by shipped `render_profile`, semantic lowering, `properties`, and
  readable guard shells. The remaining question is docs/proof reconciliation,
  not a fresh render-surface architecture wave.
- Which dump examples are truly generic language pressure, and which are domain
  pack semantics that must stay out of Doctrine core while still being
  represented by public examples?
- Do any genuinely missing surfaces also require `emit_flow` or flow-render
  follow-through, or are they markdown-only?
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/grammars/doctrine.lark` is the top-level language inventory and
  currently includes `render_profile`, `review_family`, `route_only`,
  `grounding`, readable `properties`, explicit readable `guard`, and typed
  `item_schema` / `row_schema`, alongside `analysis`, `schema`, and
  `document`.
- `doctrine/parser.py` and `doctrine/model.py` mirror those declaration
  families and readable descendants in the shipped AST.
- `doctrine/compiler.py`, `doctrine/emit_common.py`, `doctrine/emit_flow.py`,
  and `doctrine/renderer.py` are the single semantic and readback pipeline for
  workflow law, review semantics, render-profile lowering, schema groups, and
  emitted Markdown / flow output.
- `docs/` contains two distinct documentation layers:
  - the live shipped reference path under `docs/README.md`,
    `docs/LANGUAGE_REFERENCE.md`, `docs/WORKFLOW_LAW.md`,
    `docs/REVIEW_SPEC.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, and
    `docs/COMPILER_ERRORS.md`
  - historical design input and implementation-order context such as
    `docs/big_ass_dump.md` and the four second-wave phase docs
- `examples/` is the proof corpus and already carries second-wave proof through
  `examples/74_decision_attachment`.
- `editors/vscode/` is the repo-local parity surface for syntax, resolver
  behavior, alignment, packaging, and tests.

## 4.2 Control paths (runtime)

- `.prompt` authoring flows through the shared grammar, parser, model, and
  compiler. There is no second parser or alternate semantic pipeline for the
  second-wave features already shipped.
- Workflow-law and review semantics are resolved in the compiler, including
  `current artifact`, `trust_surface`, `own only`, `preserve exact`,
  `preserve decisions`, `ignore ... for rewrite_evidence`, schema-group
  invalidation, route-only validation, and review-family selection.
- Natural emitted homes flow through the same compile path into
  `doctrine/renderer.py`, while diagram output flows through `doctrine/emit_flow.py`
  and `doctrine/flow_renderer.py`.
- The proof path is manifest-backed and example-first through
  `doctrine/verify_corpus.py`.
- The VS Code extension mirrors the shipped grammar and addressability behavior
  through `resolver.js`, the TextMate grammar, language-configuration rules,
  alignment validation, and extension tests.

## 4.3 Object model + key abstractions

Current feature-family status from pass-1 repo evidence plus pass-2 targeted
render proof:

| Dump family | Current shipped carrier | Proof anchors | Current status |
| ---- | ---- | ---- | ---- |
| Document schemas for authored artifacts | `document` + `structure:` + readable descendants | `docs/LANGUAGE_REFERENCE.md`, `examples/56_*`, `58_*`, `59_*` | Shipped |
| Analysis obligations / structured reasoning programs | `analysis` + semantic lowering | `docs/LANGUAGE_REFERENCE.md`, `examples/54_*`, `67_*` | Shipped |
| Review scaffold reuse / parameterized critic families | `review_family` + case-selected review families | `docs/REVIEW_SPEC.md`, `examples/68_*`, `69_*` | Shipped |
| Routing-only turns | dedicated `route_only` declaration | `docs/WORKFLOW_LAW.md`, `examples/70_*` | Shipped |
| Grounding protocols | dedicated `grounding` declaration | `docs/WORKFLOW_LAW.md`, `examples/71_*` | Shipped |
| Natural readback / render templates pressure | `render_profile` + semantic lowering + `properties` + readable guard shells | `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md`, `examples/64_*`, `67_*`, `editors/vscode/resolver.js` | Shipped and targeted-proof confirmed in pass 2 |
| Preservation / currentness / invalidation state law | workflow law statements + schema groups + bound roots | `docs/WORKFLOW_LAW.md`, `examples/31_*` through `42_*`, `50_*` through `53_*`, `72_*` | Shipped as statements and carriers |
| Reusable preservation bundles | named workflow-law subsections + inheritance/patching | `docs/WORKFLOW_LAW.md`, `examples/37_*`, `examples/33_*` through `38_*`, `52_*`, `72_*` | Closed as explicit no-new-surface verdict |
| Decision / candidate-pool authoring | `decision` declaration + concrete-agent `decision:` attachment | `docs/LANGUAGE_REFERENCE.md`, `examples/74_*`, `editors/vscode/resolver.js`, `editors/vscode/syntaxes/doctrine.tmLanguage.json` | Shipped in this implementation wave |
| Domain-pack semantics from the dump | intentionally not Doctrine core | repo authoring rules, Section 0 scope | Must be translated into generic public proof, not added as core semantics |

## 4.4 Observability + failure behavior today

- The repo's primary proof path is `make verify-examples`.
- Diagnostics are owned by fail-loud compiler surfaces and `make verify-diagnostics`
  when the catalog changes.
- Targeted manifest-backed runs provide the narrowest development-time signal.
- Pass 2 ran targeted proof for the render-profile family:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/64_render_profiles_and_properties/cases.toml`
    passed and proved `properties`, attached comment profiles, explicit guard
    shells, and fail-loud invalid cases for duplicate property keys, unknown
    `render_profile` targets, invalid identity modes, and invalid guard-shell
    sources.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/67_semantic_profile_lowering/cases.toml`
    passed and proved semantic lowering for `analysis.stages` and document
    semantic targets, including fail-loud rejection of unsupported semantic
    render-profile modes.
- VS Code parity is verified through `cd editors/vscode && make`.
- `doctrine/compiler.py` already enforces the fail-loud control-plane rules the
  dump cares about: `current artifact` roots and carriers, `trust_surface`
  membership, `own only` rooting, schema-group invalidation, and route-only
  contracts.
- This implementation wave adds an explicit `decision` declaration family and
  concrete-agent `decision:` attachment. Missing decision refs fail loud in the
  same declaration-resolution path used elsewhere.
- Preservation reuse remains inside workflow law. The repo now states that
  named law subsections plus inheritance and patching are the canonical reuse
  path instead of adding a second reusable preservation declaration family.
- There is no runtime telemetry surface; compiler diagnostics, example proof,
  flow output, and editor tests are the practical observability path.

## 4.5 UI surfaces (ASCII mockups, if UI work)

UI scope is limited to repo-local editor parity:

- syntax highlighting for shipped declaration heads and readable block kinds
- resolver behavior for `render_profile`, `review_family`, `route_only`,
  `grounding`, readable properties/guards, and row/item schema descendants
- extension tests, alignment validation, and README smoke guidance
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Keep the same owner layout:
  - `doctrine/` for the language implementation
  - `examples/` for proof
  - `docs/` for the live reference path
  - `editors/vscode/` for editor parity
- Keep `docs/big_ass_dump.md` as historical design input, not as the live
  shipped reference path.

## 5.2 Control paths (future)

- One full audit in this plan classifies every dump family against current repo
  truth.
- Every genuinely missing feature then ships through the normal
  grammar -> parser/model -> compiler/emit/renderer -> examples/docs/editor
  chain.
- No feature is considered shipped until the proof corpus, live docs, and
  editor parity agree with the code.
- Shipped second-wave families that the audit confirms as already implemented
  do not get reimplemented; they get documented and proved cleanly against the
  dump where needed.

## 5.3 Object model + abstractions (future)

Each dump family should end in one explicit disposition:

| Dump family | Target disposition | Canonical owner path | Required proof shape |
| ---- | ---- | ---- | ---- |
| `document` / schema-like authored artifact structure | Confirm already shipped and reconcile docs/readback against the dump | live docs + examples + current compiler truth | docs cold read; no new core surface unless proof disagrees |
| `analysis` obligations | Confirm already shipped and identify any semantic holes | `analysis` declaration path in grammar/parser/model/compiler | docs/example reconciliation unless later proof disagrees |
| `review_family`, route-only, and grounding pressures | Treat shipped control-plane declarations as the canonical owner | existing review/workflow-law/compiler paths | docs/example reconciliation only unless a real missing behavior appears |
| Render-template / natural readback pressure | Treat the shipped `render_profile` + semantic-lowering + `properties` + guard path as the canonical solution | compiler render-profile lowering + renderer + examples + docs | targeted manifest proof plus docs/readback reconciliation; add code only if later proof disagrees |
| Decision / candidate-pool authoring | Ship through one generic top-level `decision` declaration plus concrete-agent `decision:` attachment | grammar/parser/model/compiler, then examples/docs/editor | positive and negative manifest-backed example proof plus VS Code parity |
| Reusable preservation bundles | Explicitly reject a new declaration family and keep reuse inside workflow-law inheritance and named subsections | `docs/WORKFLOW_LAW.md` + preservation examples + audit text | docs reconciliation plus preservation-baseline proof |
| Domain-flavored dump examples | Translate into generic public Doctrine proof surfaces | examples/ + docs | new generic examples and docs wording |

- Any new surface must stay generic and public-repo-safe, even when it was
  motivated by Lessons-flavored examples in the dump.
- No new top-level family should be added if an existing shipped family can
  preserve the dump's semantics honestly.

## 5.4 Invariants and boundaries

- One owner path per missing surface.
- No parallel declaration family, shadow renderer, or editor-only grammar.
- No import of domain-pack names or semantics into Doctrine core.
- No "docs say yes, code says no" or "code says yes, examples say no" split.
- No fallback behavior. Unsupported authored states fail loud.
- If a new top-level family is approved, flow emit and VS Code parity move in
  the same wave.
- If a dump pressure is already satisfied by shipped `render_profile`,
  workflow-law, review-family, or schema/document behavior, prefer proof and
  docs reconciliation over new syntax.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Editor parity stays repo-local and direct:

- any genuinely new keyword or declaration head highlights correctly
- any genuinely new addressable paths resolve through the same resolver path
- extension tests and README guidance expand to the new proof cases when
  required
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Audit matrix | `docs/BIG_ASS_DUMP_IMPLEMENTATION_GAP_AUDIT_2026-04-12.md`, `docs/big_ass_dump.md` | Sections 3, 4, 5, 6 | The plan now has research grounding, but the full dump-family classification is not yet folded into one explicit matrix | Expand the matrix so every material dump family lands in shipped / partial / missing / domain-only | The later implementation scope depends on this classification being exhaustive | One canonical audit matrix in the plan doc | Plan integrity only |
| Decision / candidate-pool core surface | `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, `doctrine/model.py`, `doctrine/compiler.py` | top-level declaration inventory and semantic lowering path | No explicit `decision` declaration family or candidate-pool semantic surface is visible in grammar, parser, model, compiler, docs, or examples | Lock the smallest faithful generic surface here during phase planning | This is the clearest remaining dump feature family with no shipped explicit carrier today | One generic decision/candidate-pool contract or a justified extension to an existing family | `make verify-examples`, compile negatives, `make verify-diagnostics`, VS Code parity |
| Decision readback and flow parity | `doctrine/renderer.py`, `doctrine/emit_common.py`, `doctrine/emit_flow.py`, `doctrine/flow_renderer.py` | emitted-home and flow-output rendering | No explicit decision-family readback exists because the family does not exist yet | Add natural emitted-home and flow behavior only if a real decision-family surface lands | The dump cares about natural output, not just parse support | One readback and flow contract for the chosen surface | Manifest-backed emitted output, targeted flow proof if affected |
| Reusable preservation bundles | `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, `doctrine/model.py`, `doctrine/compiler.py`, `docs/WORKFLOW_LAW.md` | workflow-law productions and validation helpers such as currentness / scope / invalidation | Workflow law already ships `own only`, `preserve exact`, `preserve decisions`, `ignore ... for rewrite_evidence`, and schema-group invalidation, but no reusable bundle declaration is visible | Decide whether to add a reusable abstraction or explicitly reject it as unnecessary because inheritance + existing law already cover the reuse need | The dump asks for reusable preservation packets, not just individual statements | Either one reusable preservation abstraction or one explicit no-new-surface verdict | Existing preservation corpus, new examples if added, docs reconciliation |
| Render-template / natural readback pressure | `doctrine/compiler.py`, `doctrine/renderer.py`, `docs/LANGUAGE_REFERENCE.md`, `examples/64_*`, `examples/67_*` | render-profile lowering and readable compact shells | Current code, phase docs, and targeted manifest proof already ship `render_profile`, `properties`, readable guards, and semantic lowering | Reconcile docs/readback against the dump and do not open a new render family unless later proof finds a real hole | Pass 2 showed the dump's render-template pressure already maps to shipped carriers | Existing render-profile lowering path remains canonical | Existing examples `64_*` and `67_*`; no new render-specific tests unless later proof disagrees |
| Shipped-family proof reconciliation | `docs/LANGUAGE_REFERENCE.md`, `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`, `examples/README.md`, phase docs under `docs/` | live docs and example indexes | Many dump families appear shipped, but the repo lacks one explicit reconciliation against the dump | Update docs and phase explanations wherever the audit proves "already shipped" or "shipped under a different shape" | Prevent false missing-feature work and stale competing explanations | One public docs story for shipped families | Doc cold read plus repo verification |
| Generic public example translation | `examples/**`, `examples/README.md` | new or revised proof cases | The dump's strongest motivating examples are Lessons-flavored and cannot be copied directly into public Doctrine proof | Design generic public examples for any remaining real gaps or for any shipped family that still needs dump-faithful proof | Preserve semantics without importing domain jargon | One generic example ladder for the remaining gaps | `make verify-examples`, targeted manifests |
| Diagnostics | `doctrine/diagnostics.py`, `doctrine/diagnostic_smoke.py`, `docs/COMPILER_ERRORS.md` | compiler error families and smoke coverage | Current diagnostics cover shipped surfaces only | Add new diagnostics only for genuinely new surfaces; otherwise keep docs aligned to the shipped catalog | Missing-surface authoring must fail loudly and documentedly | Stable public diagnostic contract | `make verify-diagnostics` |
| Editor parity | `editors/vscode/resolver.js`, `editors/vscode/syntaxes/doctrine.tmLanguage.json`, `editors/vscode/language-configuration.json`, `editors/vscode/scripts/validate_lark_alignment.py`, `editors/vscode/tests/**` | syntax, resolver, alignment, tests | The editor mirrors the current shipped surface and already knows the second-wave families found in pass 1 | Extend parity only for genuinely new syntax or new addressable descendants | Editor behavior is part of Doctrine's practical language contract | One editor parity path | `cd editors/vscode && make` |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - design input: `docs/big_ass_dump.md`
  - audit and architecture truth during this controller run:
    `docs/BIG_ASS_DUMP_IMPLEMENTATION_GAP_AUDIT_2026-04-12.md`
  - shipped language owners: `doctrine/grammars/doctrine.lark`,
    `doctrine/parser.py`, `doctrine/model.py`, `doctrine/compiler.py`,
    `doctrine/emit_common.py`, `doctrine/emit_flow.py`, `doctrine/renderer.py`
  - proof owners: `examples/**`, `examples/README.md`,
    `doctrine/verify_corpus.py`, `doctrine/diagnostic_smoke.py`
  - docs owners: the evergreen docs set under `docs/`
  - editor owners: `editors/vscode/**`
- Deprecated APIs (if any):
  - none are approved yet; the audit must prove any new surface before we
    decide whether an older pattern should be documented as superseded
- Delete list:
  - stale claims that narrow this work to a prefiltered subset of the dump
  - stale live-doc claims that describe a feature as missing or shipped when
    code/examples disagree
  - temporary sidecar notes or helper summaries that would compete with this
    plan doc as the source of truth
- Capability-replacing harnesses to delete or justify:
  - none are justified today; pass 1 found no need for a separate harness
    beyond the existing compiler, example corpus, diagnostics, flow emit, and
    VS Code parity surfaces
- Live docs/comments/instructions to update or delete:
  - `docs/README.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/WORKFLOW_LAW.md`
  - `docs/REVIEW_SPEC.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/COMPILER_ERRORS.md`
  - `examples/README.md`
  - `editors/vscode/README.md`
- Behavior-preservation signals for refactors:
  - existing corpus remains green
  - targeted manifest-backed runs for changed examples
  - diagnostic smoke stays deterministic
  - `cd editors/vscode && make` remains green when editor-facing changes land

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Live docs classification | `docs/LANGUAGE_REFERENCE.md`, `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`, `examples/README.md` | Explicit shipped-vs-missing reconciliation against the dump | Prevents repeated false "still missing" claims for already-shipped second-wave families | include |
| Preservation verdict | `docs/WORKFLOW_LAW.md`, `examples/33_*` through `38_*`, `52_*`, `72_*` | Reuse shipped workflow-law preservation semantics before inventing a new bundle family | Prevents a duplicate preservation surface if inheritance already solves the reuse problem | include |
| Review-family reuse verdict | `docs/REVIEW_SPEC.md`, `examples/68_*`, `69_*` | Treat review-family and case-selected review as the canonical owner for critic-family dump pressure | Prevents reopening critique scaffolds under a second abstraction | include |
| Render-template verdict | `examples/64_*`, `67_*`, `doctrine/compiler.py`, `doctrine/renderer.py` | Keep the targeted-proof-confirmed render-profile lowering path as the canonical render answer | Prevents a shadow render-template feature family after pass-2 proof already showed the existing path works | include |
| Flow parity | `doctrine/emit_flow.py`, `doctrine/flow_renderer.py`, `examples/73_*` | Keep flow output in the same wave for any genuinely new top-level surface | Prevents markdown-only feature drift | include |
| Historical mechanics framing | `docs/LANGUAGE_MECHANICS_SPEC.md`, phase docs under `docs/` | Update only after the final missing-surface verdict is stable | Avoids rewriting historical framing too early | defer |
| Archive and historical notes | `docs/archive/**` | Leave historical material alone unless live docs point at it incorrectly | Avoids unnecessary churn outside the active truth path | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria +
> explicit verification plan (tests optional). Refactors, consolidations, and
> shared-path extractions must preserve existing behavior with the smallest
> credible signal. No fallbacks or runtime shims. Prefer programmatic checks
> per phase and defer manual verification to finalization. Avoid negative-value
> tests. Also document new patterns or gotchas in code comments at the
> canonical boundary when that prevents future drift.

## Phase 1 - Freeze the last architecture verdicts and explicit scope matrix

Goal:
Finish the remaining planning-grade decisions so implementation can proceed
without hidden branches, stale "maybe missing" language, or duplicate
interpretations of the dump.

Work:

- finish the explicit dump-family matrix in Sections 3, 4, 5, and 6 so every
  material family lands in shipped, missing, or domain-only status
- lock the decision / candidate-pool architecture verdict: new declaration
  family versus honest extension to an existing shipped family
- lock the reusable-preservation verdict: new reusable abstraction versus
  explicit no-new-surface rejection in favor of existing workflow law and
  inheritance
- define the generic public example translations needed for any still-missing
  surface and for any already-shipped family that still lacks dump-faithful
  public proof

Verification (smallest signal):

- Section 5 names one owner path per remaining gap
- Section 6 no longer contains unresolved architecture forks disguised as
  implementation work
- this doc can name every material dump family explicitly and no feature family
  remains uncategorized

Docs/comments (propagation; only if needed):

- update only this controller doc and append any meaningful verdicts to
  Section 10

Exit criteria:

- no remaining "decide in phase plan" work is hiding inside later
  implementation phases
- the remaining implementation scope is explicit, justified, and no longer
  dependent on a narrowed interpretation of the dump

Rollback:

- revert any architecture or scope verdict in the plan as soon as later repo
  evidence disproves it

## Phase 2 - Ship the decision / candidate-pool solution end to end

Goal:
Ship the chosen generic decision / candidate-pool solution through the
canonical Doctrine owners with no parser-only or markdown-only half state.

Work:

- update grammar, parser, model, compiler, emitted-home readback, and flow
  emission for the chosen decision-family shape
- add fail-loud diagnostics and addressability rules where the decision surface
  needs them
- add manifest-backed positive and negative examples for the decision path
- update VS Code syntax, resolver, alignment, and tests in the same wave if the
  shipped surface adds syntax or new addressable descendants

Verification (smallest signal):

- targeted manifest-backed proof for the decision examples
- `make verify-diagnostics` when diagnostics change
- `cd editors/vscode && make` when syntax or resolver behavior changes
- existing affected proof cases stay green

Docs/comments (propagation; only if needed):

- update `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md`,
  `examples/README.md`, and any touched emitted-output references in the same
  wave
- add concise comments only at true SSOT boundaries where the new invariants
  are otherwise easy to forget

Exit criteria:

- the decision solution compiles, renders naturally, emits flow when required,
  fails loud on invalid authoring, and has no editor-parity lag if it changed
  the public syntax surface

Rollback:

- revert incomplete decision-surface work rather than leaving hidden partial
  support

## Phase 3 - Resolve reusable preservation bundles with proof, not theory

Goal:
Close the preservation-reuse gap one honest way: ship a reusable abstraction if
the gap is real, or explicitly reject it and prove the current workflow-law
path already covers the dump's reuse pressure.

Work:

- if Phase 1 confirms a real missing abstraction, implement it through
  grammar/parser/model/compiler, add fail-loud validation, and extend examples,
  docs, diagnostics, flow, and editor parity where the chosen surface requires
  them
- if Phase 1 rejects a new abstraction, codify that verdict in
  `docs/WORKFLOW_LAW.md`, generic proof cases, and the remaining audit text so
  the gap is closed by evidence rather than left as an open theory question
- reconcile preservation-related examples and workflow-law wording to the final
  truth in the same wave

Verification (smallest signal):

- targeted manifest-backed proof for the chosen preservation path
- `make verify-diagnostics` when diagnostics change
- `cd editors/vscode && make` when syntax or resolver behavior changes
- existing shipped preservation corpus stays green

Docs/comments (propagation; only if needed):

- update `docs/WORKFLOW_LAW.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/COMPILER_ERRORS.md`, and `examples/README.md` to match the final
  preservation verdict

Exit criteria:

- reusable preservation behavior is no longer an open architectural question
- if a new surface was approved, it is fully proved and documented
- if no new surface was approved, the rejection path is explicit and backed by
  proof

Rollback:

- remove a partial preservation abstraction rather than leaving split docs/code
  truth behind

## Phase 4 - Reconcile shipped families, generic proof, and close the parity loop

Goal:
Make the live docs path, proof corpus, and editor story describe one final
honest answer for the whole dump, including already-shipped second-wave
families.

Status: COMPLETE (fresh audit found no missing code work)

Manual QA (non-blocking):
- Do one final cold read of the live docs path against `doctrine/` and the
  active corpus before retiring the plan as implementation-complete.

Work:

- add or repair generic public examples where the dump's motivating examples are
  still domain-flavored or where an already-shipped family still lacks
  dump-faithful public proof
- reconcile `docs/LANGUAGE_REFERENCE.md`, `docs/WORKFLOW_LAW.md`,
  `docs/REVIEW_SPEC.md`, `docs/README.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  phase docs under `docs/`, and `examples/README.md` against the final shipped
  truth
- remove stale "likely missing," "future wave," or dump-era wording that no
  longer matches code and proof
- run the full verification sweep and final docs cold read against shipped code
  and manifests

Verification (smallest signal):

- `make verify-examples`
- `cd editors/vscode && make`
- `make verify-diagnostics` when diagnostics changed
- manual cold read of live docs versus shipped code and manifests

Docs/comments (propagation; only if needed):

- delete or rewrite stale live truth surfaces in the same wave
- update `editors/vscode/README.md` only when public editor behavior changed

Exit criteria:

- code, manifests, docs, diagnostics, and editor parity agree on the final
  big-ass-dump completion story
- `docs/big_ass_dump.md` remains historical input only, not a competing live
  truth surface

Rollback:

- revert doc or example claims that outrun shipped behavior
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

Keep verification lean and honest: prefer the smallest existing signal, use the
repo's current verify surfaces instead of bespoke harnesses, and treat docs and
editor parity as part of the shipped language rather than as optional cleanup.

## 8.1 Unit tests (contracts)

- Prefer the existing compiler and diagnostic smoke surfaces before inventing a
  new unit-test harness.
- Add narrow parser, compiler, or resolver contract checks only when they are
  cheaper and more stable than a whole manifest-backed example.
- When diagnostics change, keep `doctrine/diagnostics.py`,
  `doctrine/diagnostic_smoke.py`, and `docs/COMPILER_ERRORS.md` aligned and run
  `make verify-diagnostics`.

## 8.2 Integration tests (flows)

- Manifest-backed examples are the primary integration proof surface.
- Add at least one focused positive example per genuinely new surface and
  negative cases where failure semantics matter.
- For any new top-level family or new addressable surface, run the targeted
  manifests and editor-parity checks in the same slice instead of deferring
  them to a later cleanup phase.
- Use targeted manifest-backed runs while developing and finish with
  `make verify-examples`.
- Existing shipped examples must continue to pass unless an intentional bug fix
  is explicitly documented.

## 8.3 E2E / device tests (realistic)

- There is no device surface here; the realistic end-to-end check is the
  emitted Markdown plus the repo-local VS Code extension.
- When syntax, resolver, or addressability changes, run
  `cd editors/vscode && make`.
- Use manual cold reads of emitted homes and live docs only at finalization,
  not as a substitute for manifests or diagnostics.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Ship this as one coherent Doctrine-language completion wave, even if the
  branch work lands in multiple phases internally.
- Do not leave long-lived periods where code claims a surface that the examples
  or live docs still do not prove.
- Keep `docs/big_ass_dump.md` as historical design input; the live docs path
  should always point to shipped truth instead.

## 9.2 Telemetry changes

- No runtime telemetry changes are expected.
- Practical observability comes from compiler diagnostics, manifest-backed
  example proof, and VS Code tests.
- If a new surface needs extra smoke coverage, keep it deterministic and
  repo-local.

## 9.3 Operational runbook

- Start each implementation slice with the narrowest affected manifest or
  compile probe.
- When a slice adds public syntax or new addressability, run
  `cd editors/vscode && make` in that same slice instead of treating editor
  parity as a later cleanup pass.
- Re-run `make verify-examples` after each shipped feature cluster.
- Run `make verify-diagnostics` whenever diagnostic families or public error
  docs change.
- Do a final cold read of the live docs path against shipped code and proof
  before closing the plan.

# 10) Decision Log (append-only)

## 2026-04-12 - Execute the remaining work as two gap-closure waves plus one final reconciliation wave

Context

Deep-dive pass 2 proved that render-template pressure is already shipped and
narrowed the likely remaining core work to decision / candidate-pool authoring,
reusable preservation bundles, and docs/proof reconciliation for already-
shipped families. The earlier generic five-phase skeleton was still too broad
and incorrectly implied that proof and editor parity could trail new syntax as a
separate cleanup wave.

Options

- Keep the earlier broad five-phase skeleton and let implementation discover
  the real gaps opportunistically.
- Recast Section 7 around the actual remaining gap set and require targeted
  proof plus editor parity in the same slice whenever a new public surface
  lands.

Decision

Recast the execution plan into four phases: freeze the last architecture
verdicts, ship the decision solution, resolve preservation reuse, then perform
the final generic-proof and docs reconciliation wave. Any new public syntax or
new addressable surface carries same-wave VS Code parity instead of deferring
editor work to later cleanup.

Consequences

- The implementation checklist is now matched to the real remaining gap set.
- New language surfaces cannot claim completion while editor parity still lags.
- Finalization work focuses on honest reconciliation of shipped families rather
  than reopening already-shipped second-wave features.

Follow-ups

- `implement` should execute against the four-phase checklist in Section 7.
- Later audits should treat delayed editor parity for new syntax as incomplete
  work, not optional cleanup.

## 2026-04-12 - Render-template pressure is not a remaining core gap

Context

Deep-dive pass 2 compared the dump's render-template and typed-markdown
pressure against the shipped `render_profile`, semantic lowering,
`properties`, readable guard-shell path, the current phase docs, and two
targeted manifest-backed proof runs.

Options

- Re-open a broad render-template implementation wave as if the dump still
  represented missing render capability.
- Treat the shipped render-profile path as the canonical answer and limit the
  remaining work to docs/proof reconciliation unless later evidence disproves
  it.

Decision

Treat render-template pressure as already satisfied by the shipped
`render_profile` + semantic lowering + `properties` + guard-shell path.
Do not open a new render family unless later proof finds a real semantic hole.

Consequences

- Remaining likely core-gap work narrows to decision / candidate-pool
  authoring, reusable preservation bundles, and dump-to-live-doc proof
  reconciliation.
- Render work in later phases should be docs/proof cleanup, not new syntax, by
  default.
- Example and docs reconciliation now matter more than renderer expansion for
  this dump family.

Follow-ups

- Phase planning should not schedule a fresh render-template feature family by
  default.
- Live docs and phase docs should explicitly reconcile the dump's render
  pressure against the shipped render-profile examples.

## 2026-04-12 - Ship a dedicated `decision` declaration for candidate-pool and winner-selection scaffolds

Context

The implementation pass rechecked the dump's candidate-pool pressure against
the shipped repo and confirmed that no existing top-level family could carry
typed minimum-candidate, ranking, rejection, and winner-selection obligations
without collapsing back into prose-only authoring.

Options

- Keep candidate-pool doctrine as prose-only guidance under `analysis`,
  `workflow`, or ordinary readable blocks.
- Ship one small generic `decision` declaration family and a matching
  concrete-agent `decision:` attachment through the same owner chain used for
  `analysis`, `schema`, and `document`.

Decision

Ship a dedicated `decision` declaration family with typed statements for
candidate minimums, required ranking/rejects/pool evidence, winner selection,
and optional `rank_by` dimensions. Lower it through the normal readable
compiler path, make `DecisionDecl` addressable by title, and attach it to
concrete agents with `decision:`.

Consequences

- Candidate-pool doctrine is now a first-class shipped surface instead of
  prose convention.
- The new surface stays generic and public-repo-safe.
- Missing decision references fail loud through the normal declaration lookup
  path.

Follow-ups

- Keep `examples/74_decision_attachment` as the canonical positive and
  negative proof surface.
- Keep VS Code syntax, resolver behavior, and alignment validation in lockstep
  with future `decision` syntax changes.

## 2026-04-12 - Close preservation reuse without adding a second declaration family

Context

The preservation-reuse review rechecked workflow-law examples, especially
`37_law_reuse_and_patching`, against the dump's desire for reusable
preservation packets. The repo already ships named workflow-law subsections,
inheritance, and patching, plus the full preservation/currentness surface.

Options

- Add a new reusable preservation declaration family on top of workflow law.
- Explicitly state that preservation reuse stays inside named workflow-law
  subsections plus inheritance and patching.

Decision

Reject a new reusable preservation declaration family. Doctrine should reuse
preservation semantics through named workflow-law subsections and inherited law
patching instead of creating a second owner path for the same semantics.

Consequences

- Preservation reuse is no longer an open architectural question in this plan.
- Workflow law remains the single owner of preservation/currentness semantics.
- Docs and proof can close the gap without introducing duplicate language
  surfaces.

Follow-ups

- Keep `docs/WORKFLOW_LAW.md` explicit about this verdict.
- Keep `examples/37_law_reuse_and_patching` and the existing preservation
  ladder as the proof baseline for reuse.

## 2026-04-12 - Verification closed the implementation wave cleanly

Context

After the code and docs landed, the repo still needed proof that the new
surface did not regress shipped families or leave editor parity behind.

Options

- Stop after targeted local checks and let a later audit discover drift.
- Run the normal repo gates now and record the results in the plan artifact.

Decision

Run `uv sync`, `npm ci`, targeted manifest-backed proof for
`examples/37_law_reuse_and_patching`, `examples/54_analysis_attachment`, and
`examples/74_decision_attachment`, then `cd editors/vscode && make`, and
finish with `make verify-examples`.

Consequences

- The new `decision` surface is proved through both targeted and corpus-wide
  checks.
- The pre-existing `analysis` and preservation baselines stayed green.
- VS Code parity closed in the same wave, including snapshot reconciliation
  and shipped-keyword alignment for `one`.

Follow-ups

- A fresh implementation audit should now validate completeness against this
  updated plan and the shipped repo state.

## 2026-04-12 - Treat most broad second-wave dump families as shipped unless code or proof disagrees

Context

Deep-dive pass 1 compared the dump's broad second-wave feature families against
the current grammar, parser, compiler, live docs, examples, and VS Code
resolver surfaces. That pass found strong shipped evidence for `document`,
`analysis`, `review_family`, `route_only`, `grounding`, `render_profile`,
`properties`, row/item schemas, and workflow-law preservation/currentness
semantics.

Options

- Re-open a broad second-wave implementation wave as if the dump still
  represented the current missing-feature list.
- Treat the broad second-wave families as shipped by default, then focus the
  remaining implementation work on explicit missing abstractions or
  proof/docs reconciliation gaps.

Decision

Treat the broad second-wave families as shipped by default unless later code or
proof review disproves that. Focus the remaining architecture work on explicit
candidate gaps such as decision / candidate-pool authoring, reusable
preservation bundles, and any cold-read render-gap that pass 2 proves real.

Consequences

- The implementation burden is likely narrower than the raw dump suggests.
- The audit still has to classify the whole dump explicitly; this is not a
  license to skip fidelity work.
- Later passes should prefer docs/proof reconciliation over reopening already
  shipped feature families.

Follow-ups

- Deep-dive pass 2 must pressure-test the render-template verdict and the full
  dump-family matrix.
- Phase planning should only put new core implementation work on genuinely
  missing abstractions.

## 2026-04-12 - Do not narrow the dump to a prefiltered subset

Context

`docs/big_ass_dump.md` uses Lessons-flavored examples, and an aborted same-day
audit rewrote the scope as "non-Lessons reusable Doctrine ideas only." That is
not faithful to the current request for a full plan that preserves fidelity.

Options

- Narrow the work immediately to only the most obviously generic Doctrine-core
  ideas.
- Treat the whole dump as design input, classify every material feature family,
  and only then decide what is already shipped, partially shipped, or missing.

Decision

Treat the whole dump as design input and classify it exhaustively before
freezing the missing implementation scope.

Consequences

- The audit step is broader up front.
- The plan avoids false "already implemented" conclusions caused by prefiltering.
- Domain-flavored examples must be preserved semantically through generic public
  examples instead of being silently discarded.

Follow-ups

- Research and deep-dive must produce the full feature-family matrix.
- No later phase may rely on the earlier narrowed audit as authoritative truth.

## 2026-04-12 - Reuse the aborted file path as the single canonical plan doc

Context

An earlier aborted turn already created this file path, but with a non-canonical
audit artifact. Creating a second plan doc would violate the single-document
rule and leave competing planning artifacts in `docs/`.

Options

- Create a new plan doc beside this one.
- Rewrite this file in place as the canonical `DOC_PATH`.

Decision

Rewrite this file in place and treat it as the one canonical plan artifact for
the `big_ass_dump` completion effort.

Consequences

- The filename is not perfect, but the repo keeps one plan doc instead of two.
- Later `arch-step` commands have a clear default `DOC_PATH`.

Follow-ups

- If a future docs-cleanup pass wants a cleaner filename, do it only as an
  explicit docs hygiene step with no parallel plan docs left behind.

## 2026-04-12 - Keep public Doctrine proof generic while preserving semantics

Context

The dump's most detailed examples are Lessons- and poker-flavored, but
Doctrine's public authoring rules forbid importing product names, internal
skill slugs, or company-specific workflow jargon into public docs and examples.

Options

- Copy the domain-specific examples directly into Doctrine.
- Drop those examples and lose fidelity.
- Preserve the semantics through generic Doctrine examples and docs.

Decision

Preserve the semantics through generic public Doctrine examples, docs, and
tests instead of importing private domain language or dropping the feature
pressure entirely.

Consequences

- Example design work increases.
- The public repo stays policy-compliant and reusable.
- Feature decisions stay anchored in generic language capability rather than in
  one product pack's names.

Follow-ups

- Phase 1 must identify which domain-flavored example shapes need generic
  public replacements.
