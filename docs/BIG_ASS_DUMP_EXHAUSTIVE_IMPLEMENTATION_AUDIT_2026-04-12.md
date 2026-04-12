---
title: "Doctrine - Big Ass Dump Gap Closure - Architecture Plan"
date: 2026-04-12
status: active
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: phased_refactor
related:
  - docs/big_ass_dump.md
  - docs/BIG_ASS_DUMP_EXHAUSTIVE_IMPLEMENTATION_AUDIT_2026-04-12.md
  - docs/BIG_ASS_DUMP_IMPLEMENTATION_GAP_AUDIT_2026-04-12.md
  - docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md
  - docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md
  - docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md
  - docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/WORKFLOW_LAW.md
  - docs/REVIEW_SPEC.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/COMPILER_ERRORS.md
  - doctrine/grammars/doctrine.lark
  - doctrine/parser.py
  - doctrine/model.py
  - doctrine/compiler.py
  - doctrine/renderer.py
  - doctrine/diagnostic_smoke.py
  - editors/vscode/resolver.js
  - editors/vscode/syntaxes/doctrine.tmLanguage.json
  - examples/README.md
---

# TL;DR

## Outcome

Turn the current exhaustive audit into the one canonical implementation plan
that closes every remaining `docs/big_ass_dump.md` gap on the Doctrine side
without silently shrinking the scope. After this plan lands, Doctrine should no
longer be "mostly right with missing tails." It should either ship each
remaining semantic tail cleanly or explicitly reject it as dump-only sugar and
make the narrower public surface the canonical truth.

## Problem

Doctrine already ships most of the large families the dump wanted:
`document`, `structure:`, typed readable blocks, `analysis`, `schema`,
`review_family`, `route_only`, `grounding`, render profiles, preservation law,
currentness, invalidation, schema artifacts/groups, and the generic `decision`
family. The remaining blocker was not missing foundation. It was a finite set
of detail-level semantic tails and one ownership seam. This implementation
pass closed that matrix as follows:

- `analysis` now ships `prove ... from ...` and explicitly rejects or re-homes
  the remaining dump-era pseudo-ops and stage carriers
- the richer decision tail is now closed by shipping
  `sequencing_proof required`, normalizing `winner required` to the canonical
  winner-selection path, and rejecting literal `solver_screen graded_reps`
- `render_profile` no longer pretends `current_artifact`, `own_only`, and
  `preserve_exact` are authored target names; those sentences stay owned by
  workflow-law lowering
- `schema:` + `structure:` is now parser-banned instead of double-rendering the
  artifact surface
- the previously undercalled analysis-tail pressure from the dump is now
  recorded explicitly in docs as shipped, rejected, or re-homed rather than
  left as implicit future-wave pressure

## Approach

Keep one canonical doc and rewrite it into a real full-arch plan. Use the
audit as the evidence base, reread the dump for exact requirement pressure, and
close the remaining matrix one requirement at a time. Each item must end in one
of two states only:

1. shipped end to end through grammar, parser, model, compiler, docs, examples,
   diagnostics, and editor parity
2. explicitly rejected as a first-class Doctrine surface, with the surviving
   shipped surface documented as the final canonical answer

The plan does not reopen already-shipped families. It only closes the missing
tails, the overlap seam, and the documentation truth.

## Plan

1. Freeze one exact closure matrix for every remaining dump-tail requirement,
   including the analysis-tail forms the audit still undercalled.
2. Close the analysis semantic tails or explicitly reject them with faithful
   mappings to the existing shipped surface.
3. Close the decision semantic tails, keeping the public surface generic.
4. Finish the render-profile target gap and close the `schema:` +
   `structure:` ownership seam with a fail-loud rule.
5. Reconcile docs, examples, diagnostics, and VS Code parity, then rerun the
   dump-to-shipped audit against the final repo state.

Implementation status (parent `implement-loop` pass, 2026-04-12):

- Phases 1 through 5 were executed in one bounded implementation pass.
- Code, docs, examples, diagnostics, and VS Code parity were updated to the
  implemented closure matrix recorded below.
- Fresh `audit-implementation` still owns the authoritative clean-or-not-clean
  verdict and the eventual `Use $arch-docs` handoff.

## Non-negotiables

- No loss of fidelity or scope from the audit or from `docs/big_ass_dump.md`.
- No silent narrowing. Any rejected dump shape must have an explicit, named,
  documented canonical replacement or an explicit "not a Doctrine surface"
  verdict.
- No new parallel owner paths for artifact structure.
- No runtime shims, fallback behavior, or graceful optionality.
- Keep public Doctrine examples generic even when the dump pressure came from
  Lessons-flavored examples.
- Stop feature growth once this matrix is closed. After that, the bottleneck is
  Lessons migration and normalization, not more Doctrine language design.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-12
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None. Fresh audit found the planned closure matrix implemented and verified
  end to end.
  - Evidence anchors:
    - `docs/big_ass_dump.md:85`
    - `docs/big_ass_dump.md:93`
    - `docs/big_ass_dump.md:531`
    - `docs/big_ass_dump.md:540`
    - `docs/big_ass_dump.md:1086`
    - `doctrine/grammars/doctrine.lark:293`
    - `doctrine/grammars/doctrine.lark:327`
    - `doctrine/grammars/doctrine.lark:329`
    - `doctrine/parser.py:596`
    - `doctrine/parser.py:705`
    - `doctrine/parser.py:819`
    - `doctrine/parser.py:825`
    - `doctrine/model.py:649`
    - `doctrine/compiler.py:821`
    - `doctrine/compiler.py:970`
    - `doctrine/compiler.py:4092`
    - `doctrine/compiler.py:4181`
    - `doctrine/diagnostic_smoke.py:221`
    - `docs/LANGUAGE_REFERENCE.md:209`
    - `docs/LANGUAGE_REFERENCE.md:253`
    - `docs/LANGUAGE_REFERENCE.md:299`
    - `docs/AGENT_IO_DESIGN_NOTES.md:99`
    - `examples/54_analysis_attachment/cases.toml:5`
    - `examples/55_owner_aware_schema_attachments/cases.toml:52`
    - `examples/64_render_profiles_and_properties/cases.toml:60`
    - `examples/74_decision_attachment/cases.toml:27`
    - `uv sync`
    - `npm ci`
    - `make verify-diagnostics`
    - `make verify-examples`
    - `cd editors/vscode && make`
  - Plan expects:
    - ship `prove ... from ...` through the normal analysis owner chain
    - keep decision-owned `sequencing_proof required` and normalize
      `winner required` to `choose one winner`
    - reject literal `solver_screen graded_reps`
    - reject authored `current_artifact`, `own_only`, and `preserve_exact`
      render-profile targets
    - parser-ban `schema:` + `structure:` and keep live docs, manifests,
      diagnostics, and VS Code parity aligned
  - Code reality:
    - the grammar/parser/model/compiler chain ships `prove`,
      `sequencing_proof required`, and `winner required` normalization; the
      parser rejects `schema:` + `structure:`; render profiles still reject
      workflow-law sentence targets; live docs describe the same narrow public
      surface; the targeted manifests, full corpus, diagnostics smoke, and VS
      Code package/test pass all succeeded in this audit
  - Fix:
    - None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-12
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-12
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed cleanly, Doctrine will become sufficient on its own
side for the `big_ass_dump` completion goal. The remaining risk will no longer
be "missing Doctrine foundation." It will be whether Lessons migrates cleanly
onto the completed Doctrine surface.

This claim is false if any of the following remain true after implementation:

- a dump-tail requirement still matters semantically but remains prose-only or
  half-shipped
- the repo still claims broad family completion while specific dump-tail
  requirements remain unresolved
- `schema:` + `structure:` can still produce one readable-but-bloated artifact
  contract with two implied owners
- the final repo truth cannot say, requirement by requirement, whether the dump
  tail shipped or was explicitly retired

## 0.2 In scope

Requested behavior scope:

- turn this file into the one canonical full implementation plan for the
  remaining Doctrine-side `big_ass_dump` closure work
- preserve the audit's evidence and broaden it where the audit still
  undercalled the dump's exact requirement pressure
- close the remaining Doctrine-side semantic tails called out by the audit and
  the follow-up reread of the dump:
  - analysis-tail pseudo-ops and carriers
  - decision-tail winner/proof/screen pressure
  - partial render-profile semantic targets
  - `schema:` + `structure:` overlap/owner ambiguity

Allowed architectural convergence scope:

- grammar, parser, model, compiler, renderer, diagnostics, docs, examples, and
  VS Code parity work needed to land or explicitly reject the remaining tails
- small refactors needed to keep one owner path for a given semantic surface
- docs and example cleanup required to stop stale "future wave" claims from
  competing with shipped truth

## 0.3 Out of scope

- reopening already-shipped Doctrine families just because the dump narrates
  them as proposals
- new Doctrine families beyond what is needed to close or explicitly retire the
  remaining dump tails
- moving pedagogy, poker taste, voice, or agent personality into Doctrine
- eliminating prose that correctly belongs to Lessons judgment rather than to a
  compiler-owned seam
- speculative wrappers, deterministic sidecars, or new runtime infrastructure

## 0.4 Definition of done (acceptance evidence)

The plan is done only when all of the following are true:

- every remaining relevant requirement from `docs/big_ass_dump.md` is marked as
  one of:
  - shipped
  - explicitly rejected as a Doctrine surface
  - already shipped under an explicit canonical replacement
- the repo ships no unresolved overlap between `schema:` and `structure:` on
  one output declaration
- any newly shipped syntax is fully landed through:
  - `doctrine/`
  - live docs
  - manifest-backed examples
  - diagnostics
  - VS Code support when syntax changed
- the smallest credible proof set is green:
  - targeted new or changed manifest-backed examples
  - `make verify-diagnostics` when diagnostics changed
  - `make verify-examples`
  - `cd editors/vscode && make` when syntax or resolver behavior changed
- a fresh exhaustive reread of `docs/big_ass_dump.md` against shipped code says
  the Doctrine side is complete except for any explicit, documented rejection

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks.
- No silent scope cuts.
- No family-level completion claims without requirement-level closure.
- No second owner path for the same artifact surface.
- No domain-specific public Doctrine syntax just because the dump examples are
  Lessons-flavored.
- No more Doctrine feature growth after this matrix closes.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Close the remaining semantics honestly, not cosmetically.
2. Preserve the dump's requirement pressure without importing Lessons-specific
   public jargon into Doctrine.
3. Keep one owner path per artifact surface and one truth path per requirement.
4. Preserve already-shipped behavior while closing the gaps.
5. End with a repo whose live docs tell the same story as the grammar,
   compiler, examples, diagnostics, and editor tooling.

## 1.2 Constraints

- The broad architecture is already right. This plan must not behave as if the
  repo still lacks `document`, `analysis`, `schema`, `review_family`,
  `route_only`, `grounding`, or typed markdown.
- Public Doctrine docs/examples must stay generic.
- The examples are manifest-backed proof, not mere design notes.
- If syntax changes, VS Code parity changes in the same wave.
- This canonical doc must stay aligned with the real repo state. Planning turns
  may be docs-only, but implementation turns must update the doc in the same
  wave as the code changes.

## 1.3 Architectural principles (rules we will enforce)

- Implement or explicitly retire. Do not leave pseudo-surfaces in limbo.
- Reuse the current owner chain: grammar -> parser -> model -> compiler ->
  renderer/diagnostics -> examples/docs -> editor parity.
- Keep screening/proof/reasoning semantics in the most coherent owner family.
  Do not duplicate the same concept under both `analysis` and `decision`.
- Prefer hard-cutover and fail-loud guardrails over permissive dual-owner
  authoring.
- If a dump shape is only sugar over an already-shipped semantic path, reject
  the sugar explicitly instead of carrying two public surfaces.

## 1.4 Known tradeoffs (explicit)

- Shipping more analysis-tail syntax reduces prose drift but grows the language.
- Rejecting some dump-tail sugar keeps the language smaller but only works if
  the docs and proof corpus preserve the semantic intent explicitly.
- A hard `schema:` + `structure:` ban is simpler and sharper than merged
  rendering, but it forecloses one currently allowed authoring pattern.
- Finishing `render_profile` targets increases coherence for human-facing
  output, but it also commits the renderer to a more explicit semantic contract.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

The repo already ships the following high-value Doctrine surfaces:

- typed `document` plus `structure:` attachments
- rich readable block kinds including `properties`, `guard`, `item_schema`,
  `row_schema`, raw `markdown`, raw `html`, `footnotes`, and `image`
- `analysis`
- `schema` with `sections:`, `gates:`, `artifacts:`, and `groups:`
- `review_family`
- `route_only`
- `grounding`
- workflow-law preservation/currentness/invalidation semantics
- `render_profile`
- schema-backed review contracts
- manifest-backed example coverage through `examples/74_decision_attachment`

## 2.2 What’s broken / missing (concrete)

The remaining problem is detail-level closure, not missing foundation.

The exact pressure this plan had to close was:

- analysis-tail semantics, now closed as:
  - shipped `derive`, `prove`, `classify`, `compare`, `defend`
  - explicit rejection or re-homing for `require`, `screen ... with ...`,
    `basis:` / `upstream_truth`, `assign ... using ...`, `export ...`,
    analysis-local shorthand compare/fallback/preservation, and
    analysis-local `rank_by`
- decision-tail semantics, now closed as:
  - shipped `candidates minimum`, `rank required`, `rejects required`,
    `candidate_pool required`, `kept required`, `rejected required`,
    `winner_reasons required`, `choose one winner`, `rank_by`, and
    `sequencing_proof required`
  - author-facing `winner required`, which now normalizes to the canonical
    `choose one winner` path
  - explicit rejection of literal `solver_screen graded_reps` as a shipped
    keyword
- authored `render_profile`, now narrowed to the shipped semantic targets only;
  `current_artifact`, `own_only`, and `preserve_exact` were retired as authored
  target names and remain workflow-law sentence lowering only
- output-owner conflicts, now closed as:
  - shipped parser ban for `schema:` + local `must_include:`
  - shipped parser ban for `schema:` + `structure:`

## 2.3 Constraints implied by the problem

- The remaining work must stay generic and reusable.
- The plan must distinguish true missing semantics from dump-only sugar.
- The final answer must be explicit enough that future audits cannot fall back
  to "family shipped" while the requirement tails remain unresolved.
- After these closures, Doctrine must stop growing. The next bottleneck should
  be Lessons migration, not more language design.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

No external paper or third-party system is required for this pass.
This plan is deciding whether Doctrine already closes the semantics promised by
`docs/big_ass_dump.md`, so the only authoritative inputs are internal:

- `docs/big_ass_dump.md` as the widest requirement sketch
- the user-provided architecture verdict that Doctrine already owns the right
  broad families and only needs semantic-tail closure plus one overlap
  guardrail
- the shipped Doctrine owners in `doctrine/`
- the live language reference and manifest-backed examples

External prior art would not answer the real question here, which is owner and
closure consistency inside this repo.

## 3.2 Internal ground truth (code as spec)

Authoritative shipped owners, in order of truth:

- grammar and accepted syntax:
  - `doctrine/grammars/doctrine.lark`
- parser and fail-loud authoring rules:
  - `doctrine/parser.py`
- typed surface inventory:
  - `doctrine/model.py`
- lowering, semantic rendering, and cross-surface validation:
  - `doctrine/compiler.py`
  - `doctrine/renderer.py`
- live shipped docs:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/WORKFLOW_LAW.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
- proof corpus:
  - `examples/33_scope_and_exact_preservation`
  - `examples/54_analysis_attachment`
  - `examples/55_owner_aware_schema_attachments`
  - `examples/56_document_structure_attachments`
  - `examples/63_schema_artifacts_and_groups`
  - `examples/64_render_profiles_and_properties`
  - `examples/67_semantic_profile_lowering`
  - `examples/74_decision_attachment`
- editor/runtime parity surfaces:
  - `editors/vscode/resolver.js`
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json`
  - `editors/vscode/tests/integration/suite/index.js`

Concrete shipped facts from those owners:

### Analysis-tail grounding

`analysis` is narrower in shipped Doctrine than in the dump sketches. The live
grammar only accepts prose, workflow section refs, `derive`, `classify`,
`compare`, and `defend` inside analysis sections; the compiler lowers exactly
those four typed items and nothing else. The live language reference matches
that narrow surface. The strongest local proof points are:

- `doctrine/grammars/doctrine.lark:291-301`
- `doctrine/compiler.py:4094-4118`
- `docs/LANGUAGE_REFERENCE.md:217-225`
- `examples/54_analysis_attachment`

| Dump-tail item | Dump anchors | Shipped state | Planning consequence |
| --- | --- | --- | --- |
| `derive`, `classify`, `compare`, `defend` | `docs/big_ass_dump.md:681-713` | Already shipped exactly | Keep canonical and do not reopen |
| `prove ... from ...` | `docs/big_ass_dump.md:85-90`, `481-485` | Shipped in grammar, parser, model, compiler, docs, examples, and editor parity | Preserve as the one real Doctrine-side analysis addition |
| `require ...` inside `analysis` | `docs/big_ass_dump.md:88-97`, `693` | Explicitly rejected as an analysis verb; similar requiredness stays elsewhere in decisions and typed readable blocks | Keep requiredness on its existing owners instead of growing a second generic path |
| `screen ... with ...` | `docs/big_ass_dump.md:98`, `541` | Explicitly rejected in `analysis`; no grammar production exists | Keep screening out of analysis unless a future generic owner is proven |
| top-level `basis:` / `upstream_truth` carrier | `docs/big_ass_dump.md:681-686`, `1322`, `1866` | Explicitly rejected as public syntax; live analysis uses per-item basis sets only | Treat as draft drift rather than a real shared-basis owner |
| `assign ... using ...` | `docs/big_ass_dump.md:484` | Semantically covered by shipped `classify ... as ...` | Prefer explicit mapping, not a second synonym |
| `export ...` | `docs/big_ass_dump.md:701`, `713` | Explicitly rejected as analysis syntax | Re-home into output/schema/document ownership instead of growing analysis-local artifact routing |
| fallback/preservation shorthand | `docs/big_ass_dump.md:699-713` | `compare` exists; preservation already belongs to workflow law; `fallback` remains draft-only | Keep ownership split clear: `compare` stays in analysis, preservation stays in law |
| analysis-local `rank_by` | `docs/big_ass_dump.md:533-534` | Explicitly rejected; shipped only on `decision` | Normalize to decision-owned ranking, not second-owner analysis syntax |

The key correction versus the prior audit is that the dump's richer analysis
shape is not just three missing verbs. It also contains multiple drift-only
carriers that would blur ownership if they were implemented literally.

### Decision-tail grounding

The shipped `decision` family is materially real, manifest-backed, and already
owns the generic candidate-pool scaffold. The grammar, parser, model,
compiler, docs, and example `74` all agree on the current public surface:

- `candidates minimum <n>`
- `rank required`
- `rejects required`
- `candidate_pool required`
- `kept required`
- `rejected required`
- `winner_reasons required`
- `choose one winner`
- `rank_by {dimension, ...}`

Primary anchors:

- `doctrine/grammars/doctrine.lark:303-325`
- `doctrine/parser.py:760-814`
- `doctrine/compiler.py:4171-4185`
- `docs/LANGUAGE_REFERENCE.md:228-253`
- `examples/74_decision_attachment`

| Dump-tail item | Dump anchors | Shipped state | Planning consequence |
| --- | --- | --- | --- |
| core candidate and evidence fields | `docs/big_ass_dump.md:110-123`, `527-540` | Already shipped | Preserve as the canonical public decision scaffold |
| `choose one winner` | `docs/big_ass_dump.md:114` | Already shipped | Canonical winner-selection wording |
| `winner required` | `docs/big_ass_dump.md:531` | Shipped as author syntax that normalizes to `choose one winner` | Keep one canonical winner-selection owner while preserving the dump's wording pressure |
| `sequencing_proof required` | `docs/big_ass_dump.md:540` | Shipped | Keep typed sequencing evidence decision-owned |
| `solver_screen graded_reps` | `docs/big_ass_dump.md:541` | Explicitly rejected as a shipped keyword | Preserve the semantic pressure only if a future generic evidence owner is proven |
| `rank_by` outside decision or under analysis | `docs/big_ass_dump.md:123`, `533-534` | Shipped only as decision-local | Normalize the owner path and stop carrying mixed placement in docs |

The main research outcome here is that the repo already had the foundation the
dump wanted. The implementation pass then closed the remaining decision work as
tail closure and wording cleanup, not as a missing family.

### Render-profile and overlap grounding

`render_profile` is shipped as a real mechanism. This implementation pass
closed the dump's three law-shaped tail targets by retiring them as authored
`render_profile` targets instead of pretending they were semantically shipped.
The live reference and manifest-backed examples now treat
`analysis.stages`, `review.contract_checks`, and `control.invalidations` as the
shipped semantic target set, while the sentence forms for `Current artifact`,
`Own only`, and `Preserve exact` remain owned by workflow-law lowering.

Primary anchors:

- target registry and validation:
  - `doctrine/compiler.py:820-830`
  - `doctrine/compiler.py:968-986`
- shipped built-in renderer modes:
  - `doctrine/renderer.py:26-57`
- actual workflow-law sentence rendering:
  - `doctrine/compiler.py:14482-14491`
- live docs versus phase-doc sketch:
  - `docs/LANGUAGE_REFERENCE.md:338-373`
  - `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md:184-196`
- proof examples:
  - `examples/33_scope_and_exact_preservation`
  - `examples/64_render_profiles_and_properties`
  - `examples/67_semantic_profile_lowering`

| Requirement cluster | Dump anchors | Shipped state | Planning consequence |
| --- | --- | --- | --- |
| `current_artifact -> sentence` | `docs/big_ass_dump.md:1086-1090`, `4096-4098` | Explicitly retired as a shipped authored render-profile target; negative proof now lives in `examples/64_render_profiles_and_properties` | Keep workflow-law sentence lowering as the owner and remove the false sense of target-style closure |
| `own_only -> sentence` | same | Same status | Same closure rule |
| `preserve_exact -> sentence` | same | Same status | Same closure rule |
| `schema:` + local `must_include:` | `docs/big_ass_dump.md:1720`, `2305` | Explicitly guarded in parser; manifest-backed parse failure exists in example `55` | Already closed and should be preserved |
| `schema:` + `structure:` on one output | no explicit dump ban; overlap concern is audit-derived | Explicitly parser-banned; negative manifest proof and smoke coverage now exist | Close the overlap as a Doctrine-side ownership rule without inventing a second owner path |

Important nuance: the overlap guardrail requested by the user is not an
explicit `big_ass_dump.md` requirement. It is an audit-derived cleanup based on
current shipped behavior plus the dump's one-owner principle for
`schema:` + `must_include:`.

## 3.3 Reusable implementation patterns and drift surfaces

Patterns already present in the repo that future implementation should reuse:

- analysis-item ownership already has a clean grammar -> parser -> compiler
  lowering path; any approved new analysis operator should use that same model
  rather than ad hoc prose rewriting
- decision required items already use a compact, typed accounting pattern; any
  approved new decision-tail requirement should follow that pattern
- render-profile semantic targets already have a validation and mode-constraint
  path; if the three law-shaped targets stay, they should close through that
  same mechanism
- output attachment overlap rules already fail loud in the parser for
  `schema:` + `must_include:`; the same parser-level ownership check is the
  right reuse point for `schema:` + `structure:`
- the strongest proof shape in this repo is still manifest-backed example
  coverage, not draft docs

Known drift surfaces that this plan must normalize during implementation:

- `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md` and
  `docs/ANALYSIS_AND_SCHEMA_SPEC.md` still carry richer draft-era `analysis`
  sketches such as `basis:`, `fallback`, and `export`
- `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md`
  sketches `current_artifact -> sentence`, `own_only -> sentence`, and
  `preserve_exact -> sentence` as if they are phase-owned targets, while
  `docs/LANGUAGE_REFERENCE.md` does not list them as shipped render-profile
  behavior
- `docs/AGENT_IO_DESIGN_NOTES.md:132-138` currently blesses a typed output that
  carries both `schema:` and `structure:`, which directly conflicts with the
  proposed overlap guardrail
- examples `55` and `56` prove schema and structure separately, which is good,
  but there is currently no manifest-backed proof that combining them should
  fail

Behavior-preservation signals for later implementation and audit:

- preserve example `54` for shipped analysis
- preserve example `74` for shipped decision behavior
- preserve example `55` for schema ownership guardrails
- preserve example `56` for structure lowering
- preserve example `67` for shipped semantic render-profile lowering
- preserve example `33` for workflow-law sentence rendering
- run `make verify-examples` after any implementation change
- run `make verify-diagnostics` if overlap or render-profile diagnostics change
- run `cd editors/vscode && make` if editor truth surfaces change

## 3.4 Resolved questions from research

These were the real design decisions Phase 1 had to close before code landed.
They are now resolved as follows:

1. `prove` is a real first-class analysis operator and now ships.
2. `require` does not get its own analysis-level operator; typed requiredness
   remains owned by decisions, documents, schemas, and ordinary readable
   blocks.
3. Generic screening did not survive as public syntax in this pass; literal
   `solver_screen` wording stays rejected, and any future typed screening
   obligation would still need one coherent owner.
4. `winner required` now normalizes to the already-shipped `choose one winner`
   wording, and `rank_by` stays exclusively decision-owned.
5. `current_artifact`, `own_only`, and `preserve_exact` were retired as
   authored `render_profile` targets, with workflow-law sentence rendering kept
   as the shipped behavior.
6. `schema:` + `structure:` now closes as a hard parser error, with
   markdown-shape validation for `structure:` staying compile-owned.

<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

| Layer | Files | What they own today |
| --- | --- | --- |
| Grammar | `doctrine/grammars/doctrine.lark` | the public declaration surface for `analysis`, `decision`, `schema`, `document`, `render_profile`, output attachments, and workflow law |
| Parser / transform | `doctrine/parser.py` | attachment collection, duplicate-field rejection, analysis/decision body shaping, and the shipped `schema:` + local `must_include:` ownership ban |
| Model | `doctrine/model.py` | typed nodes for analysis statements, decision items, output schema/structure attachments, and workflow-law currentness/preservation statements |
| Compiler | `doctrine/compiler.py` | declaration resolution, semantic lowering, output rendering, render-profile target validation, workflow-law validation, and natural sentence rendering |
| Renderer | `doctrine/renderer.py` | built-in profile tables and semantic target modes for the currently shipped render-profile paths |
| Diagnostics / smoke | `doctrine/diagnostics.py`, `doctrine/diagnostic_smoke.py` | parse, compile, and emit error codes plus smoke coverage for analysis, output attachments, render-profile validation, workflow law, and emit CLIs |
| Emit / manifest-backed proof | `doctrine/emit_common.py`, `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, `doctrine/verify_corpus.py`, `Makefile`, `examples/33_*`, `54_*`, `55_*`, `56_*`, `64_*`, `67_*`, `74_*` | configured emit target loading, docs/flow emission, manifest execution, and checked-in `ref/` / `build_ref/` comparison for the remaining gap families |
| Live docs | `docs/LANGUAGE_REFERENCE.md`, `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md`, `docs/EMIT_GUIDE.md`, `docs/README.md`, `examples/README.md` | the current shipped reference story and the split between live truth, emitted proof, and historical phase docs |
| Editor parity | `editors/vscode/resolver.js`, `editors/vscode/syntaxes/doctrine.tmLanguage.json`, `editors/vscode/tests/integration/suite/index.js` | grammar-parity syntax highlighting, definition resolution, and editor integration tests |

## 4.2 Control paths (runtime)

1. Analysis path:
   - grammar accepts only `derive`, `classify`, `compare`, and `defend` in
     `analysis_section_item`
   - parser lowers those through `analysis_body`, `derive_stmt`,
     `classify_stmt`, `compare_stmt`, and `defend_stmt`
   - model stores them as `DeriveStmt`, `ClassifyStmt`, `CompareStmt`, and
     `DefendStmt`
   - compiler resolves and renders them through `_compile_analysis_decl` and
     `_compile_analysis_section_body`
   - downstream semantic target is only `analysis.stages`

2. Decision path:
   - grammar accepts `candidates minimum`, typed `... required` items,
     `choose one winner`, and `rank_by`
   - parser dedupes those in `decision_body`
   - model stores them as `DecisionMinimumCandidates`,
     `DecisionRequiredItem`, `DecisionChooseWinner`, and `DecisionRankBy`
   - compiler lowers them through `_compile_decision_decl` and
     `_render_decision_required_item`

3. Output attachment and render-profile path:
   - parser `output_body` collects `schema:`, `structure:`, `render_profile:`,
     and `trust_surface`
   - parser rejects duplicate `schema:`, duplicate `structure:`, duplicate
     `render_profile:`, and `schema:` + local `must_include:`
   - compiler `_compile_output_decl` renders `- Schema:` sections and
     `- Structure:` document bodies independently
   - because parser does not currently reject `schema:` + `structure:`, the
     compiler will render both when both are attached

4. Workflow-law currentness and preservation path:
   - grammar admits `current artifact`, `own only`, and `preserve ...`
   - parser lowers them to `CurrentArtifactStmt`, `OwnOnlyStmt`, and
     `PreserveStmt`
   - compiler validates carrier and scope rules, then renders natural
     sentences directly in `_compile_workflow_law_stmt`
   - this is where the human-facing sentence forms for `Current artifact`,
     `Own only`, and `Preserve exact` actually ship today

5. Editor parity path:
   - VS Code resolver and grammar track the public syntax surface generically
   - current keyword coverage and definition-link tests match the shipped
     surface, not the full dump sketch

Current failure points relevant to this plan:

- `analysis` stays intentionally narrow, but now includes shipped
  `prove ... from ...`; the remaining dump-era tails are explicitly rejected or
  re-homed in live docs
- `decision` stays generic and now includes `sequencing_proof required`, while
  `winner required` normalizes to `choose one winner` and literal
  `solver_screen graded_reps` is rejected
- authored `render_profile` no longer accepts `current_artifact`, `own_only`,
  or `preserve_exact`; those sentences stay owned by workflow law
- `schema:` + `structure:` is parser-banned and covered by negative manifest
  proof

## 4.3 Object model + key abstractions

| Surface | Key nodes / symbols | Current truth |
| --- | --- | --- |
| `analysis` | `AnalysisDecl`, `AnalysisSection`, `AnalysisSectionItem`, `DeriveStmt`, `ProveStmt`, `ClassifyStmt`, `CompareStmt`, `DefendStmt` | shipped and manifest-backed as the narrow five-verb analysis surface |
| `decision` | `DecisionDecl`, `DecisionMinimumCandidates`, `DecisionRequiredItem`, `DecisionChooseWinner`, `DecisionRankBy` | shipped and manifest-backed as the generic candidate/winner scaffold, now including `sequencing_proof required` and `winner required` normalization |
| Output attachments | `OutputSchemaConfig`, `OutputStructureConfig`, `OutputDecl`, `output_body`, `_compile_output_decl` | shipped as separate attachment families, with parser-owned overlap bans for `schema:` + `must_include:` and `schema:` + `structure:` |
| `render_profile` | `_KNOWN_RENDER_PROFILE_TARGETS`, `_KNOWN_RENDER_PROFILE_MODES`, `_RENDER_PROFILE_TARGET_MODE_CONSTRAINTS`, `_resolve_render_profile_ref`, `_BUILTIN_PROFILE_MODES` | shipped as a real validation/policy layer with the authored target set narrowed to the semantically shipped targets |
| Workflow law | `CurrentArtifactStmt`, `OwnOnlyStmt`, `PreserveStmt`, `_compile_workflow_law_stmt` | ships the actual currentness and preservation sentence forms today |
| Docs and proof | `docs/LANGUAGE_REFERENCE.md`, `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `examples/README.md`, `examples/33/54/55/56/64/67/74`, `doctrine/verify_corpus.py`, `doctrine/diagnostic_smoke.py` | current repo truth is mostly narrower and cleaner than the dump sketches, but the proof lane runs through explicit manifests and verifier code, not examples alone |

## 4.4 Observability + failure behavior today

Fail-loud behavior already present:

- parser:
  - rejects duplicate `schema:`, duplicate `structure:`, and duplicate
    `render_profile:` attachments
  - rejects `schema:` + local `must_include:` with parse code `E199`
- compiler:
  - rejects unknown render-profile targets and unsupported render-profile modes
    with `E298`
  - rejects invalid output attachment declarations such as sectionless schemas
    or non-markdown `structure:` targets with `E302`
  - rejects unsupported decision required keys if they appear outside the
    shipped set
  - rejects invalid workflow-law currentness, carrier, and ownership shapes
  - emit surfaces also ship dedicated emit failure codes `E507` through
    `E518`, plus fallback `E599`
- smoke and manifest proof:
  - `_check_analysis_field_renders`
  - `_check_output_schema_attachment_renders`
  - `_check_output_schema_owner_conflict_surfaces_as_parse_error`
  - `_check_emit_docs_handles_invalid_toml_without_traceback`
  - `_check_emit_docs_uses_specific_code_for_missing_entrypoint`
  - `_check_emit_flow_uses_entrypoint_stem_for_output_name`
  - `_check_emit_flow_direct_mode_groups_shared_surfaces`
  - `_check_emit_flow_direct_mode_requires_output_dir`
  - `make verify-examples` runs `doctrine.verify_corpus` across `cases.toml`,
    `ref/`, and `build_ref/` contracts
  - manifest-backed examples `33`, `54`, `55`, `56`, `64`, `67`, and `74`

Current blind spots:

- a fresh `audit-implementation` pass still needs to author the authoritative
  code-complete verdict for this `implement-loop` session
- broader docs retirement and drafting-artifact cleanup still belong to
  post-clean `arch-docs`, not to this parent implementation pass

## 4.5 UI surfaces (ASCII mockups, if UI work)

No product UI is in scope. The human-facing surfaces in scope are:

- rendered AGENTS/readable markdown
- rendered output contract sections and structure shells
- live reference docs and compiler error docs
- VS Code syntax, definition resolution, and integration-test parity

<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (implemented result)

## 5.1 On-disk structure (implemented owner chain)

Keep the same owner chain. Do not create a new declaration family, runtime
shim, or sidecar planner.

Expected implementation homes stay inside the current canonical chain:

- public syntax and typed ownership:
  - `doctrine/grammars/doctrine.lark`
  - `doctrine/parser.py`
  - `doctrine/model.py`
- lowering and markdown presentation policy:
  - `doctrine/compiler.py`
  - `doctrine/renderer.py`
- diagnostics and proof:
  - `doctrine/diagnostics.py`
  - `doctrine/diagnostic_smoke.py`
  - `doctrine/emit_common.py`
  - `doctrine/emit_docs.py`
  - `doctrine/emit_flow.py`
  - `doctrine/verify_corpus.py`
  - `Makefile`
  - existing manifest-backed examples, with one focused new example only when a
    real new idea ships
- live truth surfaces:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/WORKFLOW_LAW.md`
  - `docs/REVIEW_SPEC.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/COMPILER_ERRORS.md`
  - `docs/EMIT_GUIDE.md`
  - `docs/README.md`
  - `examples/README.md`
- editor parity, only if the public syntax or ref surface changes:
  - `editors/vscode/resolver.js`
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json`
  - `editors/vscode/tests/integration/suite/index.js`
  - `editors/vscode/README.md`

## 5.2 Control paths (implemented)

1. Analysis stays narrow by default.
   - `prove ... from ...` now ships through the existing
     `analysis_section_item -> parser -> model -> compiler` path.
   - `require`, `screen`, `basis:`, `upstream_truth`, `export`, fallback
     shorthand, preservation shorthand, and analysis-local `rank_by` do not get
     free admission just because they appeared in the dump. They are now
     explicitly re-homed or rejected in code and live docs.

2. Decision remains the typed candidate/winner/proof owner.
   - `choose one winner` remains the canonical winner-selection wording.
   - `winner required` now normalizes to that canonical winner-selection path.
   - typed sequencing evidence now ships here as `sequencing_proof required`.
   - literal `solver_screen graded_reps` does not ship as a public keyword.
     Any future typed screening obligation would still need one decision-owned
     or review-owned home, not a second analysis sublanguage.

3. Render-profile closure reuses existing semantics.
   - `render_profile` continues to be a policy mechanism, not a new semantic
     family.
   - `current_artifact`, `own_only`, and `preserve_exact` are now explicitly
     retired as authored `render_profile` targets.
   - workflow-law/currentness text remains the source of those readable
     sentences.
   - No sidecar lowering path is introduced.

4. Output overlap closure is parser-first.
   - `schema:` + `structure:` is now a parser-owned hard error on any output
     declaration that carries both attachments.
   - `structure:` still separately requires a markdown-bearing output shape at
     compile time.
   - compiler-side rejection remains only as defense in depth
   - docs, manifests, smoke checks, and editor truth surfaces align behind that
     single ownership rule

## 5.3 Object model + abstractions (implemented closure matrix)

Implemented closure matrix:

| Requirement | Recommended default | Canonical owner | Notes |
| --- | --- | --- | --- |
| `prove ... from ...` | shipped as the only new analysis operator in this pass | `analysis` | it fits the existing analysis owner chain without duplicating another family |
| `require ...` inside `analysis` | explicitly rejected as public analysis syntax; mapped to decision/readable `required`/prose owners | docs plus existing owners | no second generic requiredness language |
| `screen ... with ...` | explicitly rejected as a public analysis sublanguage | `decision` or `review_family` only if real typed semantics ever return | dump pressure is real, but analysis is not the owner |
| top-level `basis:` / `upstream_truth` carrier | explicitly rejected as public syntax | per-op basis sets plus titled sections | the shipped analysis shape already has a cleaner owner |
| `assign ... using ...` | explicitly normalized to `classify ... as ...` | `analysis` docs | no second synonym for the same typed move |
| `export ...` | explicitly rejected as analysis syntax | `schema`, `document`, or ordinary outputs | no analysis-local artifact-routing sublanguage |
| fallback / preservation shorthand in `analysis` | explicitly normalized to shipped `compare`, prose, and workflow law | `analysis` + `law` | preserve one owner per concern |
| analysis-local `rank_by` | explicitly rejected | `decision` | ranking remains decision-owned |
| `winner required` | shipped as author syntax that normalizes to `choose one winner` | `decision` | preserve the dump wording without adding a second winner owner |
| `sequencing_proof required` | shipped as a typed decision obligation | `decision` | this was the strongest remaining generic decision tail |
| `solver_screen graded_reps` | explicitly rejected as a literal public token | `decision` by default | do not mint domain-shaped syntax |
| `current_artifact -> sentence` | explicitly retired as an authored `render_profile` target style | workflow law + compiler | this was readability pressure, not a second public target family |
| `own_only -> sentence` | same | workflow law + compiler | same closure rule |
| `preserve_exact -> sentence` | same | workflow law + compiler | same closure rule |
| `schema:` + `structure:` on one output declaration | shipped as a hard parser error, with compile-time markdown-shape validation for `structure:` kept separate | output attachment validation | parser is the SSOT for ownership bans; markdown-shape validation stays compile-owned |

## 5.4 Invariants and boundaries

- One semantic seam, one owner path. Anything without a crisp owner gets
  rejected or re-homed; it does not get duplicated.
- Doctrine owns structure, proof shape, state, routing, preservation, review
  shape, grounding shape, and render policy.
- Lessons owns pedagogy, poker judgment, and voice.
- `analysis` owns reusable reasoning programs, not decision scaffolds,
  artifact inventories, or workflow-law preservation semantics.
- `decision` owns candidate search, ranking, explicit winner selection, and any
  surviving typed evidence obligations around that scaffold.
- Workflow law owns currentness, scope, and preservation semantics. Render
  profile may change how those semantics read, but it does not create a second
  source of truth for them.
- Output artifact structure must have one owner path only.
- Historical phase docs may stay historical, but live docs must say the same
  thing as the code and manifests.
- Any dump-tail rejected as syntax must survive as an explicit documented
  mapping or explicit "not a Doctrine surface" verdict.

## 5.5 UI surfaces (ASCII mockups, if UI work)

The target human-facing shape is:

```text
author syntax
  -> fail-loud parse/compile rules
  -> natural AGENTS/output rendering
  -> live docs that match the shipped surface
  -> manifest-backed proof
  -> matching editor behavior
```

No extra runtime or UI layer is added.

<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Analysis tail syntax and ownership | `doctrine/grammars/doctrine.lark` | `analysis_section_item`, `derive_stmt`, `prove_stmt`, `classify_stmt`, `compare_stmt`, `defend_stmt` | `analysis` now admits the shipped five-verb surface, including `prove ... from ...` | implemented `prove ... from ...`; kept rejected dump-era sugar out of the grammar | preserve one owner path and stop family-level hand-waving | shipped analysis stays narrow, with one added proof operator | `examples/54_analysis_attachment`, `examples/67_semantic_profile_lowering`, `cd editors/vscode && make` |
| Analysis tail parse/model | `doctrine/parser.py`, `doctrine/model.py` | `analysis_body`, `AnalysisSectionItem`, `DeriveStmt`, `ProveStmt`, `ClassifyStmt`, `CompareStmt`, `DefendStmt`, `AnalysisDecl` | parser/model now carry the approved analysis addition only | implemented `ProveStmt` and kept rejected/re-homed sugar out of the model | fail-loud ownership is easier when rejected shapes never become model nodes | existing chain plus shipped `ProveStmt` | targeted manifests, smoke only if new failures appear |
| Analysis readable lowering and docs | `doctrine/compiler.py`, `docs/LANGUAGE_REFERENCE.md`, `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md` | `_compile_analysis_decl`, `_compile_analysis_section_body`, analysis docs | live docs now name `prove` and explicitly document rejected/re-homed analysis tails | implemented lowering for `prove` and documented all rejected/re-homed analysis tails | stop pretending dump-era sketch forms still live in analysis | one final public analysis surface with explicit mappings | docs cold read, `examples/54_*`, `examples/README.md` |
| Decision tail closure | `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, `doctrine/model.py`, `doctrine/compiler.py` | `decision_body_line`, `DecisionRequiredItem`, `DecisionChooseWinner`, `DecisionRankBy`, `_compile_decision_decl`, `_render_decision_required_item` | decision core is shipped; `winner required` now normalizes to `choose one winner`, `sequencing_proof required` now ships, and literal dump-era screening remains rejected | implemented the generic decision closure without adding a second screening language | keep candidate/winner semantics in one family | final generic decision scaffold with no extra public drift tokens | `examples/74_decision_attachment`, docs/reference sync |
| Render-profile target completion | `doctrine/compiler.py`, `doctrine/renderer.py` | `_KNOWN_RENDER_PROFILE_TARGETS`, `_validate_render_profile_decl`, `_resolve_render_profile_ref`, `_BUILTIN_PROFILE_MODES` | `current_artifact`, `own_only`, and `preserve_exact` are no longer accepted authored targets | explicitly retired those three target names and kept the shipped semantic target set narrow | close target-name-only limbo without inventing a second renderer family | authored `render_profile` stays policy-owned while workflow-law sentences remain compiler-owned | `examples/64_render_profiles_and_properties`, `examples/67_semantic_profile_lowering`, semantic anchors from `33`, `35`, and `38` |
| Workflow-law sentence reuse | `doctrine/compiler.py`, `docs/WORKFLOW_LAW.md` | `CurrentArtifactStmt`, `OwnOnlyStmt`, `PreserveStmt`, `_compile_workflow_law_stmt` | the natural sentence forms for currentness and preservation continue to ship here | kept this as the semantic source instead of duplicating it through render-profile targets | one SSOT for the sentence semantics | no new law family and no second render-profile lowering path | `examples/33_scope_and_exact_preservation`, `examples/35_basis_roles_and_rewrite_evidence`, `examples/38_metadata_polish_capstone` |
| Output overlap guardrail | `doctrine/parser.py`, `doctrine/compiler.py`, `doctrine/diagnostics.py`, `doctrine/diagnostic_smoke.py`, `docs/COMPILER_ERRORS.md` | `output_body`, `TransformParseFailure`, `OutputSchemaConfig`, `OutputStructureConfig`, `_compile_output_decl`, `E199`, `E302`, `_check_output_schema_owner_conflict_surfaces_as_parse_error` | parser now bans both `schema:` + local `must_include:` and `schema:` + `structure:` | implemented a parser-first hard error for any output declaration that attaches both `schema:` and `structure:`; kept `structure:` markdown-shape validation and compiler defense in depth | one owner path per output artifact surface | one explicit overlap ban with stage-correct diagnostics | negative manifest-backed proof, smoke updates, existing `55` and `56` stay green |
| Diagnostics and error catalog | `doctrine/diagnostics.py`, `doctrine/diagnostic_smoke.py`, `docs/COMPILER_ERRORS.md` | `E199`, `E298`, `E302`, `E507`-`E518`, currentness/preservation families, smoke checks around analysis, output attachments, and emit flows | live diagnostics now cover the overlap rule and authored render-profile target retirement | updated smoke coverage and live docs without inventing a second error surface | fail-loud doctrine must stay teachable and provable | final error catalog matches the shipped closure | `make verify-diagnostics`, smoke reruns, new compile-fail cases |
| Live docs and instructions | `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`, `docs/COMPILER_ERRORS.md`, `docs/EMIT_GUIDE.md`, `docs/README.md`, `examples/README.md`, `editors/vscode/README.md` | analysis, decision, schema/structure, render_profile, workflow law, emit/corpus guidance | live truth now reflects the final shipped story for analysis, decision, overlap ownership, and render-profile targets | rewrote live docs where needed and removed wording that implied rejected syntax was still pending | stale docs would recreate the same drift after code lands | one repo-wide docs truth story | full docs cold read after code/proof lands |
| Drafting artifacts / provenance docs | `docs/LANGUAGE_MECHANICS_SPEC.md`, `docs/README.md` | root-level drafting artifact plus docs-index classification | the file remains in `docs/` for provenance and link stability, but `docs/README.md` does not treat it as live truth | relabel or trim it only if the final shipped closure would otherwise leave actively misleading claims in a root-visible drafting artifact | keep provenance without promoting drafts back into shipped reference | drafting artifacts stay historical and the docs index stays honest | docs cold read after the live docs pass |
| Example corpus and manifests | `doctrine/verify_corpus.py`, `Makefile`, `examples/33_*`, `54_*`, `55_*`, `56_*`, `64_*`, `67_*`, `74_*` plus one new example only if needed | `verify_corpus`, `_run_compile_case`, `cases.toml`, `prompts/AGENTS.prompt`, `ref/**`, `build_ref/**` | existing manifests and the verifier prove the shipped families but not the remaining overlap or any approved new tail | reuse existing proof homes where possible; add one-new-idea-only examples only when a real new surface ships, and keep the verifier path explicit in the plan | proof should stay generic and composable | final corpus proves both new closure and preserved behavior | targeted manifests plus `make verify-examples` |
| VS Code parity | `editors/vscode/resolver.js`, `editors/vscode/syntaxes/doctrine.tmLanguage.json`, `editors/vscode/language-configuration.json`, `editors/vscode/package.json`, `editors/vscode/tests/integration/run.js`, `editors/vscode/tests/integration/suite/index.js`, `editors/vscode/scripts/validate_lark_alignment.py`, `editors/vscode/README.md` | `KEYED_DECL_RE`, package scripts, grammar alignment validator, integration definition-link tests, render-profile navigation tests | editor surfaces match the shipped public syntax today and the build/test contract already validates tmLanguage, package metadata, and runtime integration together | update only if syntax or ref behavior changes; the overlap ban alone should not force lexer churn | keep editor truth aligned without inventing extra scope | final public syntax stays compiler/editor-consistent | `cd editors/vscode && make`, `npm test`, `uv run --locked python scripts/validate_lark_alignment.py` |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  grammar -> parser -> model -> compiler -> renderer/diagnostics -> manifests
  -> live docs/editor parity. No second semantic family, no runtime shim, and
  no second plan doc.
- Deprecated APIs (if any):
  no runtime API layer is being deprecated, but dump-era wording such as
  `winner required`, analysis-local `rank_by`, `basis:` / `upstream_truth`,
  `export ...`, and literal `solver_screen graded_reps` must be either
  explicitly normalized or explicitly rejected.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  any live doc or example that presents `schema:` + `structure:` on one
  output declaration as valid final doctrine; any live wording that still implies
  draft-only analysis tails or render-profile targets are already shipped when
  they are not.
- Capability-replacing harnesses to delete or justify:
  none should be added. This plan is language/compiler/docs convergence, not a
  prompt-replacement or deterministic-sidecar exercise.
- Live docs/comments/instructions to update or delete:
  `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`, `docs/COMPILER_ERRORS.md`,
  `docs/EMIT_GUIDE.md`, `docs/README.md`, `examples/README.md`,
  `editors/vscode/README.md`, plus any example prompt/ref that still models
  rejected syntax as accepted truth.
  Touch `docs/LANGUAGE_MECHANICS_SPEC.md` only if the drafting-artifact copy
  would otherwise remain actively misleading after the final shipped closure.
- Behavior-preservation signals for refactors:
  keep `33`, `54`, `55`, `56`, `64`, `67`, and `74` green; keep
  `_check_analysis_field_renders`,
  `_check_output_schema_attachment_renders`, and
  `_check_output_schema_owner_conflict_surfaces_as_parse_error` aligned; run
  `make verify-examples`, `make verify-diagnostics`, and
  `cd editors/vscode && make` for touched surfaces.

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Analysis tail closure | `analysis_section_item`, `analysis_body`, `_compile_analysis_decl` | one-owner narrow analysis family | prevents a second pseudo-analysis language from growing beside the shipped one | include |
| Decision tail closure | `DecisionRequiredItem`, `_compile_decision_decl` | keep candidate/winner evidence in `decision` | prevents split ownership between analysis and decision | include |
| Render-profile completion | `_KNOWN_RENDER_PROFILE_TARGETS`, `_BUILTIN_PROFILE_MODES`, `_compile_workflow_law_stmt` | finish the existing registry/mode path | prevents sidecar renderers or duplicate sentence logic | include |
| Output attachment bans | `output_body`, `_compile_output_decl` | parser-first ownership rejection | prevents dual-owner markdown outputs | include |
| Docs truth split | `docs/README.md`, historical phase docs, live reference docs | keep historical docs historical and live docs live | prevents phase-doc intent from masquerading as shipped truth | include |
| Editor feature growth | VS Code hover/completion/rename beyond parity | broaden editor product scope | not required for doctrine-surface closure | defer |
| Dedicated `solver_screen` family | any new literal domain keyword path | domain-specific syntax family | would create another semantic owner path for one dump term | exclude |
| Second preservation abstraction | any new non-law preservation family | duplicate currentness/preservation owner | shipped workflow law already owns this concern | exclude |
| Runtime fallbacks or shadow renderers | any shim path outside compiler/parser truth | compatibility masking | violates fail-loud cutover doctrine | exclude |

<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 - Freeze the semantic closure matrix before writing code

Status: COMPLETE

Completed work:

- locked one explicit verdict per remaining dump-tail item
- recorded the final closure defaults that actually shipped:
  - ship `prove ... from ...`
  - ship `sequencing_proof required`
  - accept `winner required` as author syntax that normalizes to
    `choose one winner`
  - reject literal `solver_screen graded_reps`
  - retire `current_artifact`, `own_only`, and `preserve_exact` as authored
    `render_profile` targets
  - parser-ban `schema:` + `structure:`
- updated the plan and Decision Log to carry those owner calls forward into
  implementation

Goal:

Turn every remaining dump-tail requirement into an explicit implementation or
rejection verdict so later phases are not improvising syntax or silently
narrowing scope.

Work:

- reread the dump and lock the exact remaining requirement inventory, including
  the audit-undercalled analysis-tail forms:
  - `basis:` / `upstream_truth`
  - `prove ... from ...`
  - `require ...`
  - `screen ... with ...`
  - `assign ... using ...`
  - analysis-local `export ...`
  - shorthand compare/fallback/preservation forms
  - analysis-local `rank_by`
  - `winner required`
  - `sequencing_proof required`
  - `solver_screen graded_reps`
  - `current_artifact` / `own_only` / `preserve_exact` render-profile targets
  - `schema:` + `structure:` overlap
- record one explicit verdict per item:
  - implement as first-class Doctrine surface
  - explicitly reject as dump-only sugar and map to the surviving canonical
    surface
  - re-home to the coherent owner family if the dump placed it in the wrong one
- decide the exact overlap closure policy; default target is a hard error on
  any output declaration that attaches both `schema:` and `structure:`, while
  `structure:` keeps its separate markdown-shape validation

Verification (smallest signal):

- plan-only consistency pass across Sections 3, 5, 6, 7, and 10
- no open "probably covered" items remain in the matrix

Docs/comments (propagation; only if needed):

- update this plan and the Decision Log with the final matrix

Exit criteria:

- every remaining relevant dump-tail item has an explicit closure verdict
- the plan no longer depends on vague family-level completion claims

Rollback:

- revert any premature syntax commitment that still leaves multiple plausible
  owner paths

## Phase 2 - Close the analysis semantic tails honestly

Status: COMPLETE

Completed work:

- shipped `prove ... from ...` through grammar, parser, model, compiler, docs,
  examples, diagnostics, and editor parity
- updated `examples/54_analysis_attachment` to prove the new analysis operator
- explicitly documented rejected or re-homed analysis sugar in the live
  reference so `require`, `screen ... with ...`, `basis:`, `upstream_truth`,
  `assign ... using ...`, `export ...`, shorthand fallback/preservation, and
  analysis-local `rank_by` do not linger as fake pending syntax
- kept existing structure/schema proof homes green while the analysis wave
  landed

Goal:

Either ship the genuinely missing analysis semantics or explicitly retire the
dump-only sugar with faithful public mappings.

Work:

- implement the approved generic analysis-tail items through grammar, parser,
  model, compiler, docs, examples, diagnostics, and editor parity
- default approved set:
  - `prove ... from ...`
- default reject or re-home set:
  - `require ...`
  - `screen ... with ...`
- explicitly document rejected sugar where the surviving canonical surface is
  already coherent:
  - `assign ... using ...` -> `classify ... as ...`
  - top-level `basis:` / `upstream_truth` -> per-op basis plus titled sections
    unless Phase 1 disproves
  - analysis-local `rank_by` -> `decision.rank_by`
  - `require ...` -> decision obligations, readable `required`, or prose unless
    Phase 1 proves a missing analysis-owned semantic
  - `screen ... with ...` -> decision-owned typed evidence or
    `review_family` gate only if Phase 1 proves a real non-prose semantic
  - analysis-local shorthand compare/fallback/export/preservation -> explicit
    mappings to shipped `compare`, prose, workflow law, or document/schema
    structure unless Phase 1 disproves
- add focused generic proof for any newly shipped analysis-tail syntax and keep
  existing analysis/render-profile baselines green

Verification (smallest signal):

- targeted manifest-backed proof for the approved analysis-tail example(s)
- existing `examples/54_analysis_attachment` stays green
- existing `examples/55_owner_aware_schema_attachments` stays green when output
  owner rules change
- existing `examples/56_document_structure_attachments` stays green when
  overlap or structure attachment behavior changes
- existing `examples/67_semantic_profile_lowering` stays green when analysis
  rendering changes
- `make verify-diagnostics` if diagnostics change
- `cd editors/vscode && make` if syntax or resolver behavior changes

Docs/comments (propagation; only if needed):

- update `docs/LANGUAGE_REFERENCE.md`
- update `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md` only if its
  historical-doc copy would otherwise remain misleading after the live-doc pass
- update `examples/README.md`
- add a short comment only if the final analysis-tail grammar would otherwise be
  easy to mis-own later

Exit criteria:

- analysis-tail pressure is no longer half-shipped
- every rejected analysis dump-shape has an explicit canonical mapping in docs
- no new analysis syntax lands without proof and editor parity

Rollback:

- remove partial analysis-tail syntax rather than leaving parser-only or docs-
  only support behind

## Phase 3 - Close the richer decision tail without duplicating analysis

Status: COMPLETE

Completed work:

- shipped `sequencing_proof required` through the normal decision declaration
  chain
- accepted `winner required` as author syntax and normalized it to the
  canonical `choose one winner` path
- explicitly rejected literal `solver_screen graded_reps` as a shipped decision
  keyword in live docs
- updated `examples/74_decision_attachment` and the language reference so the
  decision family closes generically instead of carrying dump-only drift

Goal:

Finish the decision-side winner/proof closure while keeping generic screening
owned by one coherent family only.

Work:

- implement approved decision required items through the normal declaration
  chain; default target set:
  - `sequencing_proof required`
- normalize `winner required` to the already-shipped `choose one winner`
- explicitly settle the `solver_screen graded_reps` pressure:
  - preferred target: reject the literal token and keep any surviving typed
    screening obligation decision-owned
  - only re-home it to `review_family` if Phase 1 proves the semantics are
    really artifact-gating rather than candidate-selection evidence
- keep `rank_by` explicitly decision-owned and remove analysis-side ambiguity
  from live docs

Verification (smallest signal):

- targeted manifest-backed proof for the chosen decision-tail closure
- existing `examples/74_decision_attachment` stays green or is updated in the
  same wave
- `make verify-diagnostics` if diagnostics change
- `cd editors/vscode && make` if syntax or resolver behavior changes

Docs/comments (propagation; only if needed):

- update `docs/LANGUAGE_REFERENCE.md`
- update `docs/COMPILER_ERRORS.md` if new failures are introduced
- update `examples/README.md`
- update `editors/vscode/README.md` if public editor behavior changed

Exit criteria:

- the richer decision tail is no longer in limbo
- the final decision surface stays generic
- screening is owned by one family only

Rollback:

- revert partial decision-tail syntax rather than leaving split docs/code truth

## Phase 4 - Finish render-profile target closure and add the output overlap guardrail

Status: COMPLETE

Completed work:

- closed the render-profile tail honestly by retiring authored
  `current_artifact`, `own_only`, and `preserve_exact` targets instead of
  pretending they were semantically shipped
- kept workflow-law/currentness text as the SSOT for those readable sentences
- added a parser-first hard error for any output declaration that attaches both
  `schema:` and `structure:`
- added negative proof for the overlap guardrail and for authored
  render-profile use of the retired target names
- rewrote live examples/docs that previously modeled both attachments on one
  output declaration

Goal:

Make the remaining semantic render targets fully real and remove the
double-owner artifact surface.

Work:

- implement full shipped closure for render-profile targets:
  - `current_artifact`
  - `own_only`
  - `preserve_exact`
- update the compiler target registry, built-in renderer mode tables, workflow-
  law sentence reuse, docs, and proof so those targets behave like the other
  shipped semantic targets
- add the chosen `schema:` + `structure:` output guardrail; default target is a
  parser-first hard authoring error for any output declaration that attaches
  both, while `structure:` keeps its separate markdown-shape validation and the
  compiler keeps defense in depth
- update docs and examples that currently show both attachments together on one
  output declaration

Verification (smallest signal):

- targeted manifest-backed proof for the render-profile target closure
- existing `examples/64_render_profiles_and_properties` stays green or is
  updated in the same wave
- existing `examples/67_semantic_profile_lowering` stays green
- targeted negative proof for the new overlap guardrail
- existing structure/schema corpora stay green
- `make verify-diagnostics` if diagnostics change
- `cd editors/vscode && make` if syntax or resolver behavior changes

Docs/comments (propagation; only if needed):

- update `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md`
  only if its historical-doc copy would otherwise remain misleading after the
  live-doc pass
- update `docs/AGENT_IO_DESIGN_NOTES.md`
- update `docs/LANGUAGE_REFERENCE.md`
- update `docs/COMPILER_ERRORS.md`
- update `docs/LANGUAGE_MECHANICS_SPEC.md` only if its drafting-artifact copy
  would otherwise remain actively misleading after the shipped closure

Exit criteria:

- `current_artifact`, `own_only`, and `preserve_exact` are either fully shipped
  render-profile targets or explicitly retired as a target style
- one output declaration no longer allows ambiguous dual ownership between
  `schema:` and `structure:`

Rollback:

- remove partial renderer/guardrail work rather than leaving target-name-only
  closure or soft overlap ambiguity

## Phase 5 - Normalize live truth and prove the final Doctrine-side answer

Status: COMPLETE

Completed work:

- updated live docs and examples to the final shipped story for analysis,
  decision, overlap ownership, and render-profile target closure
- updated VS Code keyword parity for `prove` and `sequencing_proof`
- ran the full verification stack for this pass:
  - `uv sync`
  - `npm ci`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/54_analysis_attachment/cases.toml --manifest examples/55_owner_aware_schema_attachments/cases.toml --manifest examples/64_render_profiles_and_properties/cases.toml --manifest examples/74_decision_attachment/cases.toml`
  - `make verify-diagnostics`
  - `make verify-examples`
  - `cd editors/vscode && make`
- left the session-scoped `implement-loop` state armed so fresh
  `audit-implementation` can write the authoritative code verdict

Goal:

End with one honest repo story: code, docs, manifests, diagnostics, and editor
behavior all say the same thing about the dump.

Work:

- reconcile all live docs to the final shipped or explicitly rejected answer:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/WORKFLOW_LAW.md`
  - `docs/REVIEW_SPEC.md`
  - `docs/COMPILER_ERRORS.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/EMIT_GUIDE.md`
  - `docs/README.md`
  - `examples/README.md`
  - `editors/vscode/README.md`
- keep `docs/LANGUAGE_MECHANICS_SPEC.md` as a drafting artifact unless its
  wording becomes actively misleading; if it does, relabel or trim it without
  promoting it back into the live reference path
- keep `docs/01_*` through `docs/04_*` historical unless they become actively
  misleading after the final shipped closure
- remove stale future-wave or pseudo-feature wording that survived the earlier
  audits
- rerun the full shipped proof set
- perform a fresh exhaustive reread of `docs/big_ass_dump.md` against shipped
  truth and record any explicit rejections in the final audit outcome instead of
  leaving them implicit
- lock the final Doctrine-side verdict: after this phase, stop new Doctrine
  feature growth for this effort

Verification (smallest signal):

- `make verify-examples`
- `make verify-diagnostics` when diagnostics changed
- `cd editors/vscode && make` when syntax or resolver behavior changed
- final cold read of live docs versus shipped code and manifests

Docs/comments (propagation; only if needed):

- rewrite or delete stale live truth surfaces in the same wave
- if docs are deleted, obey the restore-point commit policy first

Exit criteria:

- Doctrine-side `big_ass_dump` closure is either shipped or explicitly retired
  requirement by requirement
- the final repo story no longer depends on "family shipped" blur
- the remaining bottleneck is Lessons migration, not Doctrine surface drift

Rollback:

- revert any doc or example claim that outruns shipped behavior

<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

Keep verification lean and honest. Use the repo's existing proof surfaces
instead of building new harnesses just to feel formal.

## 8.1 Unit tests (contracts)

- Prefer parser/compiler contract changes and `doctrine/diagnostic_smoke.py`
  before inventing new unit harnesses.
- When diagnostics change, keep `doctrine/diagnostics.py`,
  `doctrine/diagnostic_smoke.py`, and `docs/COMPILER_ERRORS.md` aligned and run
  `make verify-diagnostics`.
- If the overlap guardrail lands as a new parser/compiler error, it needs one
  explicit negative prompt proof and matching diagnostic text.

## 8.2 Integration tests (flows)

- Manifest-backed examples are the primary integration proof surface.
- Add one new idea per new example.
- Reuse existing examples where the new work is truly extending the same public
  surface rather than introducing a new one.
- Keep `examples/54`, `55`, `56`, `64`, `67`, and `74` green because they are
  the nearest existing proof homes for the remaining gaps.

## 8.3 E2E / device tests (realistic)

- No product UI or device layer is in scope.
- The realistic end-to-end proof here is:
  - parse
  - compile
  - render
  - manifest-backed verification
  - diagnostics smoke
  - editor parity when syntax changed

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Ship each approved surface as a hard cutover in docs/examples/editor parity,
  not as a hidden half-state.
- If a dump-tail shape is explicitly rejected, make the narrower surviving
  canonical surface the only live story in the same wave.
- After the final gap-closure wave, stop new Doctrine feature growth for this
  effort.

## 9.2 Telemetry changes

- No product telemetry changes are required.
- The operational signals are the existing verify gates and the final dump
  reread against shipped truth.

## 9.3 Operational runbook

- For code phases:
  - `uv sync`
  - `npm ci`
  - targeted manifest-backed verification for the changed examples
  - `make verify-diagnostics` when diagnostics changed
  - `make verify-examples`
  - `cd editors/vscode && make` when syntax/resolver changed
- For doc deletions:
  - make a restore-point commit first

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: explorer 1, explorer 2, self-integrator
- Scope checked:
  - frontmatter, `# TL;DR`, `# 0)` through `# 10)`, appendices, and helper-block drift
  - architecture, call-site audit, verification, rollout, and cleanup alignment
- Findings summary:
  - the artifact was missing the `consistency_pass` helper block
  - the live-doc migration set was inconsistent across Sections 4, 5, 6, 7, and cleanup lists
  - the verification section undercalled the example homes later phases depend on for output-owner and structure checks
- Integrated repairs:
  - aligned the live-doc set to include `docs/REVIEW_SPEC.md` and `docs/EMIT_GUIDE.md` everywhere the plan treats live docs as canonical truth
  - aligned verification expectations to keep `examples/55` and `examples/56` green alongside the other nearest proof homes
  - qualified historical phase-doc updates so `docs/02_*` and `docs/03_*` are only touched if they would otherwise remain misleading
  - recorded this pass in the artifact
- Remaining inconsistencies:
  - none
- Decision: proceed to implement? yes
<!-- arch_skill:block:consistency_pass:end -->

# 10) Decision Log (append-only)

## 2026-04-12 - Reuse the existing audit path as the one canonical plan doc

Context

This path already existed as the exhaustive audit. Creating another plan doc
would violate the single-document rule and recreate the exact "one doc, not
two" problem this repo just tripped over.

Options

- Create a new plan doc beside this one.
- Rewrite this file in place as the canonical architecture plan.

Decision

Rewrite this file in place and keep it as the one canonical plan artifact for
the remaining `big_ass_dump` Doctrine-side closure.

Consequences

- The filename is audit-flavored, but the repo keeps one canonical artifact.
- Later `arch-step` commands have a clear default `DOC_PATH`.

Follow-ups

- Only rename this file later as an explicit docs hygiene step if no parallel
  plan docs remain.

## 2026-04-12 - Doctrine is already sufficient at the family level; only the semantic tails remain

Context

The current repo already ships most of the broad families the dump wanted.
What remains is a finite set of semantic tails and one overlap seam, not a
missing foundation.

Options

- Treat the repo as still missing broad families and reopen major language
  design.
- Treat the broad architecture as correct and only close the remaining semantic
  tails and ownership seam.

Decision

Treat the broad architecture as correct. This plan only closes the remaining
semantic tails, the output overlap seam, and the live-doc truth path.

Consequences

- Scope stays finite.
- This effort can end with a hard stop on new Doctrine growth.

Follow-ups

- Do not reopen already-shipped families unless code or proof disproves the
  current audit.

## 2026-04-12 - Keep public Doctrine proof generic while preserving dump semantics

Context

The dump's motivating examples are strongly Lessons-flavored, but Doctrine's
public authoring rules forbid importing private product vocabulary into live
public docs/examples.

Options

- Copy the Lessons-specific examples literally.
- Drop the detail-level pressure and lose fidelity.
- Preserve the same semantics through generic public Doctrine surfaces.

Decision

Preserve the semantics through generic public Doctrine examples, docs, and
proof. Do not import private domain language and do not use public-genericity
as an excuse to narrow the semantics.

Consequences

- Example design work may increase.
- The public repo remains policy-compliant.

Follow-ups

- Phase 1 must identify which dump-specific examples need generic public proof
  replacements.

## 2026-04-12 - Stop Doctrine feature growth after the gap matrix closes

Context

The user-provided architecture verdict is that Doctrine already owns the right
broad seams. After the remaining gap closures, the next bottleneck should be
Lessons migration and normalization.

Options

- Keep extending Doctrine after the remaining tails close.
- Stop Doctrine surface growth once the matrix is closed and shift the work to
  migration/normalization.

Decision

Stop Doctrine feature growth once this plan closes the remaining matrix.

Consequences

- The implementation work stays focused.
- Future work can judge Doctrine changes against a much higher bar.

Follow-ups

- The final audit must say plainly whether the remaining bottleneck is Doctrine
  or Lessons migration.

## 2026-04-12 - The prior exhaustive audit still undercalled some analysis-tail pressure

Context

The audit correctly identified `prove`, `require`, `screen ... with ...`,
decision tails, render-profile partials, and the overlap seam. A fresh reread
of the dump shows additional analysis-tail pressure that must be closed one way
or another:

- `basis:` / `upstream_truth`
- `assign ... using ...`
- analysis-local `export ...`
- shorthand compare/fallback/preservation forms

Options

- Ignore those forms because the audit did not foreground them.
- Add them to the explicit closure matrix and settle them in Phase 1.

Decision

Add them to the closure matrix. This plan must not repeat the earlier audit's
"close enough" flattening.

Consequences

- Phase 1 becomes stricter.
- The final plan is less likely to leave a hidden dump-tail gap behind.

Follow-ups

- Appendix A records the exact dump-tail inventory that Phase 1 closed.

## 2026-04-12 - Deep-dive owner defaults prefer narrow analysis, decision-owned evidence, and parser-first overlap bans

Context

The deep-dive pass sharpened the architecture beyond the earlier audit summary.
The current plan was still too loose on three owner calls:

- whether `analysis` should grow beyond `prove`
- whether `winner required` should become a new public decision token
- whether the `schema:` + `structure:` overlap should be described as a generic
  fail-loud rule or a parser-owned SSOT

Options

- Keep multiple owner families open and let implementation decide case by case.
- Tighten the defaults now so later phases only reopen them with explicit
  evidence.

Decision

Tighten the defaults now:

- `analysis` stays narrow by default; `prove ... from ...` is the only new
  analysis operator with a favorable default
- `winner required` normalizes to shipped `choose one winner`
- any surviving typed screening obligation stays decision-owned by default,
  unless Phase 1 proves it is really a `review_family` gate
- `schema:` + `structure:` closes as a parser-first hard error, with compiler
  defense in depth

Consequences

- The target architecture is concrete enough for implementation planning.
- Phase 1 still has room to overturn a default, but only with explicit
  evidence.
- The plan no longer treats the dump as permission to duplicate owners.

## 2026-04-12 - Second deep-dive pass made the proof lane and overlap wording stage-correct

Context

The first deep-dive pass still undernamed the actual proof lane and left two
precision problems behind:

- the plan talked about manifests and examples without naming
  `doctrine.verify_corpus` or the emit lane it exercises
- the overlap ban was described as if the parser could key off
  markdown-bearing output shapes, which is not how the shipped parser sees the
  world
- `docs/LANGUAGE_MECHANICS_SPEC.md` was being treated too much like a live doc
  even though `docs/README.md` classifies it as drafting/provenance material

Options

- Leave the wording loose and let later phases infer the real proof and
  diagnostics path.
- Tighten the plan now so the proof owners, diagnostic stages, and doc classes
  match the shipped repo exactly.

Decision

Tighten the plan now:

- treat `doctrine/verify_corpus.py`, `Makefile`, and the emit lane as explicit
  proof owners in the architecture and call-site inventory
- describe `schema:` + `structure:` as a parser-first ban on any output
  declaration carrying both attachments, while keeping `structure:` shape
  validation compile-owned
- keep `docs/LANGUAGE_MECHANICS_SPEC.md` as a drafting artifact unless it
  becomes actively misleading after final closure

Consequences

- later phases now have the real proof runner and stage-correct diagnostics in
  scope
- the overlap guardrail no longer smuggles compile-time shape knowledge into
  parse-time wording
- the doc cleanup pass can distinguish live truth from historical provenance
  without losing either

Follow-ups

- Phase 2 and Phase 3 must follow these defaults unless Phase 1 records an
  explicit override.

## 2026-04-12 - Preserve the dump's boundary language and example scaffolding in the canonical plan

Context

The rewrite preserved the gap matrix, but it flattened too much of the source
document's own explanation layer:

- the sharp Doctrine-versus-Lessons boundary language
- the before/after examples showing symbolic source versus readable emitted
  `AGENTS.md`
- the mini example ladder that explained which features were meant to land
  one at a time

Losing those examples would not just remove prose polish. It would remove the
source's concrete demonstrations of what the remaining tails are supposed to
feel like in authored prompts and rendered homes.

Options

- Keep only the requirement inventory and let future implementers reconstruct
  the examples from the dump again.
- Preserve the source language and examples inside this canonical plan, while
  clearly labeling which parts are still-open gaps versus already-shipped or
  historical anchors.

Decision

Preserve the source boundary language and example scaffolding inside appendices
of this canonical plan.

Consequences

- the plan keeps more of the dump's fidelity without creating a second doc
- already-shipped families can stay closed while their motivating examples
  remain visible
- future implementation passes have concrete prompt-side and emitted-home
  targets to compare against, instead of only abstract matrix entries

## 2026-04-12 - Parent implementation pass closed the matrix without widening Doctrine

Context

The phase plan is now implemented across `doctrine/`, live docs, examples,
diagnostics, and VS Code parity. The last open owner decision was whether to
literalize every dump-era tail or close the matrix by shipping only the generic
pieces that fit Doctrine cleanly.

Options

- Ship every dump-shaped token literally, including law-shaped
  `render_profile` targets and literal `solver_screen` wording.
- Close the matrix by shipping only the generic tails that materially fit
  Doctrine and explicitly rejecting or re-homing the rest.

Decision

Close the matrix without widening Doctrine:

- ship `prove ... from ...` in `analysis`
- ship `sequencing_proof required` in `decision`
- accept `winner required` as author syntax that normalizes to
  `choose one winner`
- reject literal `solver_screen graded_reps` as a shipped keyword
- parser-ban `schema:` + `structure:`
- retire `current_artifact`, `own_only`, and `preserve_exact` as authored
  `render_profile` targets
- keep workflow-law sentence lowering as the owner for currentness and
  preservation wording
- update live docs, examples, diagnostics, and editor parity to the final
  shipped story

Consequences

- every remaining dump-tail item is now either implemented, explicitly rejected,
  or explicitly re-homed
- the public Doctrine surface stays generic instead of accreting domain-shaped
  or duplicate-owner syntax
- readable emitted homes remain a hard acceptance bar without inventing a
  second render/law family
- the parent implementation pass can now hand off to fresh
  `audit-implementation`, but it must not author the authoritative code-complete
  verdict itself

Follow-ups

- fresh `audit-implementation` must write the authoritative code verdict and,
  if clean, the `Use $arch-docs` handoff

# Appendix A) Imported Notes (unplaced; do not delete)

## A.1 Exact remaining dump-tail inventory this plan closed

Analysis-side pressure pulled directly from `docs/big_ass_dump.md`:

- `prove lesson_count from {prior_knowledge_mapping, advancement_delta, learning_jobs}`
- `require strawman_sizing_pass`
- `require why_not_shorter`
- `require why_not_longer`
- `require candidate_pool`
- `require kept_and_rejected`
- `require sequencing_ledger`
- `require dumb_strategy_playtest`
- `screen graded_reps with solver_clarity`
- top-level `basis:` / `upstream_truth` carriers
- `assign step_roles using StepRole`
- analysis-local `export ...`
- analysis-local shorthand compare/fallback/preservation forms
- analysis-local `rank_by { ... }`

Decision-side pressure pulled directly from `docs/big_ass_dump.md`:

- `winner required`
- `sequencing_proof required`
- `solver_screen graded_reps`
- `rank_by {teaching_fit, product_reality, capstone_coherence, downstream_preservability}`

Render and overlap pressure pulled directly from `docs/big_ass_dump.md`:

- `current_artifact -> sentence`
- `own_only -> sentence`
- `preserve_exact -> sentence`
- the shipped `schema:` + local `must_include:` exclusion
- the formerly still-open `schema:` + `structure:` seam on one output declaration

## A.2 Broad families this plan must not reopen as if they were still missing

- `document`
- `structure:`
- typed readable blocks
- `schema`
- `review_family`
- `route_only`
- `grounding`
- workflow-law preservation/currentness/invalidation
- schema artifacts/groups
- the generic `decision` family itself

## A.3 Source-language guardrails that must survive the rewrite

These phrases from `docs/big_ass_dump.md` are not fluff. They are boundary
rules that this plan must preserve:

- Doctrine owns the grammar of the move; Lessons owns the specific game being
  played.
- Doctrine owns structure, proof, and state. Lessons owns pedagogy, domain
  judgment, and voice.
- The language owns shape; the workflow owns meaning.
- Human-readable emitted homes are a hard requirement, not a soft preference.
- The source becomes symbolic, but the rendered `AGENTS.md` still reads like
  guidance, not bytecode.
- Do not let the renderer mirror the AST mechanically.

Planning consequence:

- keep human-readable emitted homes as a hard acceptance bar, not a nice-to-have
- keep Doctrine generic even when the motivating source examples are
  Lessons-flavored
- preserve semantic fidelity when rejecting or re-homing dump syntax; do not
  preserve only the name and lose the behavior
- treat render-profile closure as readability infrastructure, not as decorative
  formatter work

## A.4 Representative before/after examples from the dump that this plan must preserve semantically

These are not all new implementation asks. Some are already-shipped style
anchors. They stay here so the plan keeps the source's concrete target shapes.

### Metadata pass example (already-shipped style anchor, not a new gap family)

Before prompt:

```prompt
workflow MetadataWordingWorkflow: "Metadata Wording Workflow"
    "Work in exactly one mode per turn: lesson-title mode or section mode."
    "In lesson-title mode, own only title."
    "In section mode, own only name and description."
    "Do not treat both files as current in one turn."
```

After prompt:

```prompt
enum MetadataPassMode:
    lesson_title: "lesson-title mode"
    section: "section mode"

workflow MetadataWording:
    law:
        mode pass_mode = metadata_route_facts.active_mode as MetadataPassMode

        match pass_mode:
            MetadataPassMode.lesson_title:
                current artifact lesson_title_manifest via coordination_handoff.current_artifact
                own only lesson_title_manifest.title
                preserve exact lesson_title_manifest.* except lesson_title_manifest.title

            MetadataPassMode.section:
                current artifact section_metadata_file via coordination_handoff.current_artifact
                own only {section_metadata_file.name, section_metadata_file.description}
                preserve exact section_metadata_file.* except {section_metadata_file.name, section_metadata_file.description}
```

After emitted `AGENTS.md`:

```text
Work in exactly one mode per turn: lesson-title mode or section mode.

If lesson-title mode is live:
- Current artifact: Lesson Title Manifest File.
- Own only title.
- Preserve every other manifest field exactly.

If section mode is live:
- Current artifact: Section Metadata File.
- Own only name and description.
- Preserve every other section metadata field exactly.
```

Why this stays in the plan:

- it is the cleanest proof that symbolic source plus natural emitted guidance is
  already a shipped doctrine pattern
- it shows what "readable emitted homes" means in concrete terms
- it should not be misread as an `analysis` gap; it is a law/rendering success
  anchor

### Lesson-architect analysis example (directly relevant to the remaining analysis tail)

Before prompt:

```prompt
workflow LessonPlanAnalysis:
    "Build nearby-lesson evidence."
    "Build real comparable lessons."
    "Decide size and pacing."
    "Build the step arc table."
```

After prompt:

```prompt
analysis LessonPlanDerivation:
    prove lesson_count from {prior_knowledge_mapping, advancement_delta, learning_jobs}
    compare against local_corridor using prior_lesson_counts
    assign step_roles using StepRole
    preserve route_skeleton from section_playable_strategy
```

After emitted `AGENTS.md`:

```text
Before you lock the count, prove it from:
- prior knowledge mapping
- advancement delta
- learning jobs

Required tables:
- Prior-Lessons Step-Count Table
- Step Arc Table
- Real Comparable Lessons

Stable constraint:
Preserve the approved route skeleton from the section playable strategy.
```

Why this stays in the plan:

- `prove ... from ...` was the clearest analysis-tail candidate and now ships
- `assign ... using ...` is the clearest synonym-pressure example that this plan
  normalizes to `classify ... as ...`
- `preserve route_skeleton ...` is the clearest example of source pressure that
  belongs under workflow law rather than a new analysis-local preservation
  sublanguage
- the "Required tables" payoff is already mostly owned by shipped
  `document` / `structure:` / typed-readable-block families and must not be
  reopened as if missing

### Strategy and candidate-pool example (directly relevant to the remaining decision tail)

Before prompt:

```text
Build a short list of real options instead of jumping straight to one favorite.
Rank the serious options and record why each rejected option lost.
Use FastCards first to build a real candidate pool with alternatives and rejects before you choose the kept reps.
```

After prompt:

```prompt
decision PlayableStrategyChoice:
    candidates minimum 3
    rank required
    rejects required
    winner required

analysis PlayableStrategyRanking:
    rank_by {teaching_fit, product_reality, capstone_coherence, downstream_preservability}

decision RepSelection:
    candidate_pool required
    kept required
    rejected required
    sequencing_proof required
    solver_screen graded_reps
```

After emitted `AGENTS.md`:

```text
Generate at least three serious options.
Rank them by teaching fit, product reality, capstone coherence, and what later roles can preserve.

Build a real candidate pool before you freeze the keep set.
Record the kept reps, the serious rejects, and why the winners won.
```

Why this stays in the plan:

- `winner required` is the clearest source-pressure example that now maps to
  shipped `choose one winner`
- analysis-local `rank_by { ... }` is the clearest mixed-owner example that
  this plan normalizes back to `decision`
- `sequencing_proof required` was the strongest live decision-tail candidate
  and now ships
- `solver_screen graded_reps` remains the clearest literal token that this plan
  rejects or re-homes instead of shipping unchanged

### Render-profile example (directly relevant to the remaining readability tail)

Source sketch:

```prompt
render_profile LessonsHome:
    current_artifact -> sentence
    own_only -> sentence
    preserve_exact -> sentence
    review.contract_checks -> titled_section
    analysis.stages -> natural_ordered_prose
    guarded_sections -> concise_explanatory_shell
```

Why this stays in the plan:

- it is the cleanest single example of the dump's demand that output stay
  readable and natural instead of mechanically AST-shaped
- the three law-shaped targets are now explicitly retired as authored
  `render_profile` targets, while their readability pressure remains satisfied
  by workflow-law sentence lowering plus the shipped baseline profiles
- the dump also named `ContractMarkdown`, `ArtifactMarkdown`, and
  `CommentMarkdown` as the canonical baseline profiles; those names are now
  already shipped and should stay visible as the baseline rather than being
  replaced by an ad hoc parallel family
- the already-shipped targets `review.contract_checks`,
  `analysis.stages`, and `guarded_sections` must stay visible as the baseline
  the new tail is trying to match

## A.5 Mini example ladder preserved from the dump, mapped to current repo reality

The dump included a staged example ladder starting at `54`. Those exact folder
names are now partly obsolete because the repo already shipped a different
second-wave ladder. The semantic progression still matters and must stay
visible in this plan.

| Dump ladder item | Source purpose | How this plan preserves it now |
| --- | --- | --- |
| `54_analysis_basic` | top-level `analysis` declaration, basic lowering, readable emitted section | preserve as the semantic reason `analysis` exists; current shipped anchor is `examples/54_analysis_attachment`, which now also proves `prove`, rather than recreating the obsolete exact folder |
| `55_analysis_classify_compare` | enum-aware `classify`, reference-aware `compare`, clean readable analysis rendering | preserve as already-mostly-shipped semantics; do not recreate the old example name unless a still-missing generic behavior needs new proof |
| `56_schema_output_contract` | `schema` declarations plus output attachment and owner conflict with local `must_include` | preserve as already shipped; the current generic anchor is `examples/55_owner_aware_schema_attachments` |
| `57_schema_inheritance` | route/mode-specific schema extension without dynamic conditional schema logic | preserve as historical semantic ladder context; not a remaining Doctrine-side gap in this plan |
| `58_lessons_lesson_architect_capstone` | near-real prose-heavy lane migrated onto `analysis` plus typed output structure | preserve as a migration target and semantic payoff example, not as a public generic Doctrine example requirement |
| `59_lessons_section_architecture_capstone` | prove the same approach scales to another large lane | preserve as migration context, not as a required public example before Doctrine closure |
| `60_schema_review_contract` | schema-gate export integrated with first-class review | preserve as historical semantic pressure; current Doctrine closure should only reopen it if a genuinely unshipped generic seam is rediscovered |

Planning consequence:

- when later phases add proof examples, preserve the ladder's semantic order
  even if the literal old example IDs are no longer the right public repo
  homes
- keep the public examples generic and repo-native; do not import
  Lessons-private names just because the source ladder used them

# Appendix B) Conversion Notes

- This file used to be the exhaustive audit. It is now the canonical plan doc.
- The audit's meaning-bearing findings were re-homed into Sections 2 through 7.
- The newly surfaced analysis-tail forms that the audit undercalled were added
  to Section 3, Section 5, the Phase 1 matrix, and Appendix A.
- A later docs-only audit restored lost boundary language, before/after
  examples, and the mini example ladder from `docs/big_ass_dump.md`.
- No sidecar plan doc was created.
