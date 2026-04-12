---
title: "Doctrine - Phase 4 Review Route Only Grounding Control Plane Completion - Architecture Plan"
date: 2026-04-11
status: active
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: parity_plan
related:
  - docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md
  - docs/PHASE3_RENDER_POLICY_AND_EXTENSION_SURFACES_COMPLETION_2026-04-11.md
  - docs/FINISH_ANALYSIS_SCHEMA_OUTPUT_CONTRACTS_2026-04-11.md
  - docs/REVIEW_SPEC.md
  - docs/WORKFLOW_LAW.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/LANGUAGE_MECHANICS_SPEC.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/EMIT_GUIDE.md
  - docs/README.md
  - docs/COMPILER_ERRORS.md
  - examples/README.md
  - examples/30_law_route_only_turns
  - examples/40_route_only_local_ownership
  - examples/41_route_only_reroute_handoff
  - examples/42_route_only_handoff_capstone
  - examples/43_review_basic_verdict_and_route_coupling
  - examples/46_review_current_truth_and_trust_surface
  - examples/47_review_multi_subject_mode_and_trigger_carry
  - examples/49_review_capstone
  - examples/57_schema_review_contracts
  - examples/63_schema_artifacts_and_groups
  - doctrine/grammars/doctrine.lark
  - doctrine/model.py
  - doctrine/parser.py
  - doctrine/compiler.py
  - doctrine/renderer.py
  - doctrine/flow_renderer.py
  - doctrine/diagnostics.py
  - doctrine/diagnostic_smoke.py
  - doctrine/verify_corpus.py
  - editors/vscode/resolver.js
  - AGENTS.md
---

# TL;DR

## Outcome

Finish every explicit Phase 4 obligation in
`docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md` that is
not already shipped, without slimming scope, then leave the repo with one
honest completion story across `doctrine/`, manifest-backed examples, live
docs, diagnostics, and editor parity surfaces.

## Problem

The repo already ships part of the Phase 4 baseline, but not the whole phase.
Today Doctrine has schema-backed `review contract:` support, the first-class
`review` surface, workflow-law `current none`, `route`, `invalidate`,
`support_only`, `ignore ... for rewrite_evidence`, trusted current-artifact
carriers, and shipped `schema artifacts:` / `groups:`. But the dedicated
Phase-4 surfaces described in `docs/04_*` are not yet a finished shipped
story: there is no first-class `review_family`, no case-selected review-family
surface, no dedicated `route_only`, no dedicated `grounding`, no
schema-group invalidation consumption in workflow law, and no reconciled
control-plane readback/docs story that matches those promised surfaces.
Some live docs also still argue against adding `review_family` or `route_only`,
which leaves split truth alive.

## Approach

Treat `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md` as
the authoritative requested-scope boundary. Audit it line by line against the
shipped grammar, model, parser, compiler, renderer, examples, diagnostics,
live docs, and VS Code surfaces; lock which prerequisites are already shipped
and must be preserved; then finish the missing Phase 4 language and
convergence work through Doctrine's canonical compiler owner path instead of
quietly shrinking the phase to the subset that already exists.

## Plan

1. Audit every explicit Phase 4 promise against current repo evidence and mark
   the exact shipped baseline that must remain green.
2. Separate the dedicated missing surfaces from already-shipped review,
   workflow-law, and schema prerequisites.
3. Land the missing control-plane language through the shared
   grammar -> model -> parser -> compiler -> renderer path, including
   `review_family`, explicit review-case selection, `route_only`,
   `grounding`, and schema-group invalidation consumption.
4. Add manifest-backed proof, diagnostics, live-doc convergence, and editor
   parity so the repo tells one truthful Phase 4 story.
5. Reconcile surviving docs that currently contradict the Phase 4 boundary
   instead of leaving "do not add this" guidance live next to shipped code.

## Non-negotiables

- Do not slim the scope or reinterpret `docs/04_*` into a smaller subset.
- Do not pretend the existing workflow-law route-only ladder or abstract-review
  reuse already satisfies the dedicated Phase 4 surfaces if the language does
  not actually ship them.
- Do not keep split truth between `docs/04_*`, `docs/REVIEW_SPEC.md`,
  `docs/WORKFLOW_LAW.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/LANGUAGE_MECHANICS_SPEC.md`, examples, and `doctrine/`.
- Do not add fallback shims or a second control-plane owner path beside the
  canonical compiler semantics.
- Preserve the already-shipped review, workflow-law, and schema behavior that
  this phase builds on.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-11
Verdict (code): COMPLETE
Manual QA: pending (non-blocking)

## Code blockers (why code is not done)
- None. Fresh audit verification passed on 2026-04-11:
  - `make verify-examples`
  - `make verify-diagnostics`
  - `cd editors/vscode && make`
- Completion anchors:
  - `doctrine/grammars/doctrine.lark:15`
  - `doctrine/parser.py:306`
  - `doctrine/parser.py:330`
  - `doctrine/compiler.py:3301`
  - `doctrine/compiler.py:4641`
  - `doctrine/compiler.py:15394`
  - `docs/REVIEW_SPEC.md:28`
  - `docs/WORKFLOW_LAW.md:137`
  - `docs/LANGUAGE_REFERENCE.md:24`
  - `examples/README.md:39`

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Optional human spot check:
  - read the emitted Markdown for `examples/68_review_family_shared_scaffold`
    through `examples/72_schema_group_invalidation`
  - install the packaged VSIX locally if a manual editor smoke test is still
    desired after the passing automated package/test run
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-11
external_research_grounding: not run - repo evidence sufficient so far on 2026-04-11
deep_dive_pass_2: done 2026-04-11
recommended_flow: implement-loop
note: Auto-plan completed research, deep-dive pass 1, deep-dive pass 2, and phase-plan from repo evidence only. The Phase 4 artifact is ready for implement-loop.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly,
`docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md` will
become an honest description of shipped Doctrine Phase 4 rather than a future
spec layered on top of partially-related earlier surfaces. Concretely:

- schema-backed `review contract:` support will remain shipped and explicitly
  treated as preserved baseline, not rediscovered as new work
- `review_family` will ship as a real reusable declaration family for shared
  review scaffolds
- case-selected multi-mode reviews will ship as first-class typed review
  structure rather than ad hoc match trees standing in for the missing surface
- `route_only` will ship as a dedicated declaration for routing-only turns
  instead of remaining only a workflow-law example pattern
- `grounding` will ship as a dedicated protocol surface for evidence-safe or
  wording-safe behavior
- workflow-law invalidation will consume `schema.groups.*` and expand concrete
  members in readable output
- review and route-only readbacks, diagnostics, examples, live docs, and
  editor parity will agree with the shipped language boundary

The claim is false if any explicit Phase 4 promise from `docs/04_*` still
lacks the required grammar/model/parser/compiler/renderer/proof surface, or if
the repo still contains live docs that materially contradict the resulting
Phase 4 boundary.

## 0.2 In scope

- Every explicit Phase 4 promise in
  `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md`:
  - schema-backed `review contract:` integration as preserved baseline
  - `review_family`
  - case-selected multi-mode reviews with exact gate export
  - dedicated `route_only`
  - dedicated `grounding`
  - control-plane integration with `preserve`, `invalidate`, `support_only`,
    `ignore rewrite_evidence`, and current-artifact carriage via
    `trust_surface`
  - schema-group invalidation consumption and concrete expansion
  - compact typed-markdown readback for review and route-only comments
- The canonical owner-path work needed to finish those promises through:
  - `doctrine/grammars/doctrine.lark`
  - `doctrine/model.py`
  - `doctrine/parser.py`
  - `doctrine/compiler.py`
  - `doctrine/renderer.py`
  - `doctrine/diagnostics.py`
- Manifest-backed examples, diagnostics docs, live language docs, and VS Code
  parity surfaces that must match the shipped Phase 4 truth.
- Architectural convergence needed because the repo already partially ships the
  prerequisites:
  - preserve schema-backed `review contract:` semantics
  - preserve the shipped workflow-law route-only ladder while converting it
    from "proof of related behavior" into truthful baseline for the new
    dedicated declaration
  - preserve current-truth and `trust_surface` rules while widening the
    control-plane surfaces that use them
  - reconcile live docs that still reject the dedicated Phase 4 declarations
    if the code now ships them

## 0.3 Out of scope

- Cutting `docs/04_*` down to only the currently shipped subset.
- Treating the existing workflow-law route-only examples, review subject maps,
  or abstract-review reuse as a reason not to implement the dedicated surfaces
  the Phase 4 doc explicitly asks for.
- New product capabilities or domain-specific control-plane features beyond the
  Phase 4 promises.
- Replanning Phases 1 through 3 as whole phases. If a still-open Phase 3
  render-profile or lowering gap blocks an exact Phase 4 readback promise,
  this plan may depend on that specific prerequisite, but it does not absorb
  unrelated Phase 3 scope.
- Runtime fallbacks, compatibility shims, or shadow route/currentness
  semantics.

## 0.4 Definition of done (acceptance evidence)

- The shipped `doctrine/` path implements the full Phase 4 contract described
  by `docs/04_*`, not just the adjacent surfaces that were already present.
- The repo has manifest-backed positive and compile-negative proof for:
  - `review_family` inheritance and patching
  - case-selected review semantics
  - dedicated `route_only`
  - dedicated `grounding`
  - schema-group invalidation consumption and concrete expansion
  - current-truth and `trust_surface` integration across the new surfaces
- `docs/REVIEW_SPEC.md`, `docs/WORKFLOW_LAW.md`,
  `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_MECHANICS_SPEC.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md`,
  `docs/README.md`, and `examples/README.md` agree with shipped Phase 4 truth.
- If grammar or resolver surfaces move, `editors/vscode/` reflects the same
  Phase 4 contracts as the compiler and docs.
- Relevant closeout verification runs pass:
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics change
  - targeted manifest-backed runs for touched examples
  - `cd editors/vscode && make` if `editors/vscode/` changes

Behavior-preservation evidence:

- existing Phase 4-adjacent proof examples remain green unless an explicitly
  justified bug fix changes behavior:
  - `30_law_route_only_turns`
  - `40_route_only_local_ownership`
  - `41_route_only_reroute_handoff`
  - `42_route_only_handoff_capstone`
  - `43_review_basic_verdict_and_route_coupling`
  - `46_review_current_truth_and_trust_surface`
  - `47_review_multi_subject_mode_and_trigger_carry`
  - `49_review_capstone`
  - `57_schema_review_contracts`
  - `63_schema_artifacts_and_groups`
- existing schema-backed review contracts do not regress
- workflow-law `current none`, route, invalidation, `support_only`, and
  `ignore rewrite_evidence` remain truthful and fail loud

## 0.5 Key invariants (fix immediately if violated)

- No scope cutting from
  `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md`.
- No second control-plane owner path beside the canonical compiler semantics.
- No silent behavior drift in existing review, workflow-law, or schema
  semantics while widening Phase 4.
- No live doc may keep saying "do not add `review_family`" or
  "do not add `route_only`" once shipped code says otherwise.
- No route-only surface may pretend a current artifact exists when the branch
  is semantically `current none`.
- No grounding surface may silently invent receipts or unresolved truth.
- No schema-group invalidation may stop at the group label when the runtime
  readback is supposed to expand concrete members.
- No runtime fallbacks or compatibility shims. The phase either ships
  correctly or fails loudly.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Finish every explicit Phase 4 promise exactly as written before claiming the
   phase is complete.
2. Preserve and reuse the shipped review/workflow/schema owner paths instead of
   inventing parallel control-plane semantics.
3. Keep the completion story honest across code, examples, live docs,
   diagnostics, and editor tooling.
4. Resolve existing doc drift explicitly rather than burying it under new code.

## 1.2 Constraints

- Schema-backed review contracts are already shipped and must be treated as
  preserved baseline, not re-scoped away.
- Workflow law already owns `current none`, route semantics, invalidation,
  narrow authority, comparison-only support, and rewrite-evidence exclusions.
- `schema artifacts:` and `groups:` are already shipped and addressable, so
  Phase 4 should consume them rather than designing a replacement inventory
  surface.
- `docs/LANGUAGE_MECHANICS_SPEC.md` still contains live "do not add" guidance
  that conflicts with `docs/04_*`; the plan must converge those surfaces.
- The reopened Phase 3 render-profile/lowering gaps may affect how ambitious
  Phase 4's typed-markdown readback can be without exact prerequisite work.

## 1.3 Architectural principles (rules we will enforce)

- `docs/04_*` defines requested Phase 4 behavior; `doctrine/` plus
  manifest-backed cases define shipped truth.
- New Phase 4 declarations still route through the shared
  grammar -> model -> parser -> compiler -> renderer pipeline.
- Existing review/workflow/schema semantics remain the substrate; dedicated
  Phase 4 declarations must integrate with them, not shadow them.
- Unsupported or contradictory control-plane uses fail loudly.
- One live truth surface per behavior: no doc or example is allowed to teach a
  different Phase 4 boundary than the compiler ships.

## 1.4 Known tradeoffs (explicit)

- Introducing `review_family`, `route_only`, and `grounding` adds new
  declaration families, which is a real widening of the language surface. The
  justification has to be explicit because older docs currently argue against
  that move.
- Preserving the existing workflow-law route-only ladder while adding a
  dedicated `route_only` surface may require sharper documentation so the old
  examples remain useful without implying the dedicated declaration is
  unnecessary.
- Compact typed-markdown control-plane readback is desirable, but it must not
  depend on Phase 3 render-profile behavior that the repo still does not ship.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- `review` is a shipped first-class declaration with workflow-or-schema
  `contract:` support, inherited fields, subject disambiguation, currentness
  carriers, and exact route/verdict semantics.
- Workflow law is the shipped control-plane surface for `current none`,
  `current artifact`, `route`, `stop`, `invalidate`, `support_only`,
  `preserve`, and `ignore ... for rewrite_evidence`.
- Route-only behavior is currently proven as a workflow-law pattern in the
  staged example ladder (`30`, `40`, `41`, `42`), not as a dedicated
  declaration.
- Multi-subject and mode-sensitive review behavior is currently proven through
  ordinary review constructs and `match`-based outcomes (`47`, `49`), not via
  a dedicated case-selected review-family surface.
- `schema artifacts:` and `groups:` are already shipped and addressable
  (`63`), but workflow-law invalidation does not yet consume `schema.groups.*`
  as a concrete expansion target.

## 2.2 What’s broken / missing (concrete)

- The Phase 4 doc promises dedicated surfaces that the shipped language does
  not yet provide.
- The repo contains live docs that still reject adding some of those dedicated
  surfaces, which leaves a split-truth design boundary.
- The current proof ladder demonstrates adjacent capabilities, but not the
  exact Phase 4 abstractions or their fail-loud diagnostics.
- The current route-only examples intentionally keep their handoff comments
  outside `trust_surface`; that is useful baseline behavior, but it is not the
  final Phase 4 integration story described in `docs/04_*`.

## 2.3 Constraints implied by the problem

- The new work must preserve already-shipped semantics while widening them.
- The plan must distinguish "already shipped prerequisite" from "still-missing
  Phase 4 surface" so implementation does not redo solved work or declare
  false completion.
- The plan must explicitly reconcile contradictory docs because the repo is
  already teaching more than one answer.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- No external research added in this pass. Rejected for now because the open
  questions are about Doctrine's own shipped boundary, owner path, and
  contradictory live docs, and repo evidence is already sufficient to drive the
  next architecture pass honestly.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md` —
    requested-scope source for the dedicated Phase 4 surfaces.
  - `doctrine/compiler.py` — `_resolve_review_contract_spec()` and
    `_validate_review_outcome_section()` already own workflow-or-schema review
    contracts, exact review outcome routing, and currentness agreement.
  - `doctrine/compiler.py` — `_review_subject_key_from_subject_map()` proves the
    current shipped review path already supports multi-subject mode
    disambiguation through `subject_map`.
  - `doctrine/compiler.py` — `_validate_workflow_law()`,
    `_validate_route_only_next_owner_contract()`, and
    `_validate_route_only_standalone_read_contract()` prove today's route-only
    semantics live under workflow law and `current none`, not under a dedicated
    declaration family.
  - `doctrine/compiler.py` — `_validate_invalidation_stmt()` still restricts
    `invalidate` to one full input or output artifact root, which means
    `schema.groups.*` invalidation consumption is genuinely unshipped today.
  - `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, and
    `doctrine/model.py` ship `subject_map`, `trust_surface`, `support_only`,
    and `ignore ... for rewrite_evidence`, but there is no first-class
    `review_family`, `route_only`, or `grounding` declaration surface in the
    grammar/model/parser path.
  - `examples/57_schema_review_contracts` — proves `review contract:` can target
    a `schema` with exported gates.
  - `examples/47_review_multi_subject_mode_and_trigger_carry` and
    `examples/49_review_capstone` — prove the current review substrate already
    carries mode-sensitive subject selection, carried fields, handoff-first
    blocks, and exact route/currentness outcomes.
  - `examples/30_law_route_only_turns`, `examples/40_route_only_local_ownership`,
    `examples/41_route_only_reroute_handoff`, and
    `examples/42_route_only_handoff_capstone` — prove the existing workflow-law
    route-only ladder that Phase 4 must preserve while widening.
  - `examples/63_schema_artifacts_and_groups` — proves `schema artifacts:` and
    `groups:` already exist and are addressable.

- Canonical path / owner to reuse:
  - `doctrine/grammars/doctrine.lark` -> `doctrine/model.py` ->
    `doctrine/parser.py` -> `doctrine/compiler.py` -> `doctrine/renderer.py` —
    the one canonical owner path for any new Phase 4 language surface.
  - `doctrine/compiler.py` review-resolution helpers — canonical owner for
    `review_family` and case-selected review integration, because the current
    review contract, subject_map, currentness, and route agreement already live
    there.
  - `doctrine/compiler.py` workflow-law validators — canonical owner for the
    dedicated `route_only` semantics if the new declaration lowers into the
    same branch/currentness/route checks instead of creating a parallel engine.
  - `doctrine/compiler.py` schema artifact/group resolution path — canonical
    owner for `schema.groups.*` invalidation consumption.

- Existing patterns to reuse:
  - `examples/47_review_multi_subject_mode_and_trigger_carry` — subject-set +
    `subject_map` + carried-mode review pattern to reuse instead of inventing a
    detached selected-contract wrapper.
  - `examples/49_review_capstone` — named pre-outcome review sections,
    handoff-first blocking, carried active mode/trigger state, and exact
    route/currentness outcomes.
  - `examples/42_route_only_handoff_capstone` — guarded route-only handoff
    readback and explicit `current none` semantics.
  - `examples/63_schema_artifacts_and_groups` — authored artifact inventories
    and ordered reusable groups to reuse instead of inventing a second
    invalidation inventory type.

- Prompt surfaces / agent contract to reuse:
  - `docs/REVIEW_SPEC.md` — shipped review contract, subject_map, field
    bindings, and currentness/trust rules.
  - `docs/WORKFLOW_LAW.md` — shipped workflow-law contract for `current none`,
    route, invalidation, `support_only`, and `ignore rewrite_evidence`.
  - `docs/AGENT_IO_DESIGN_NOTES.md` — emitted-output and `trust_surface`
    portability rules that new Phase 4 surfaces must preserve.

- Native model or agent capabilities to lean on:
  - Not a model-capability problem. This phase is compiler-owned language work,
    so the capability-first version is to reuse shipped Doctrine semantics and
    readable lowering surfaces before inventing harnesses, wrappers, or side
    channels.

- Existing grounding / tool / file exposure:
  - `examples/*/cases.toml` plus `doctrine/verify_corpus.py` — manifest-backed
    proof ladder for positive and negative language behavior.
  - `doctrine/diagnostic_smoke.py` and `docs/COMPILER_ERRORS.md` — existing
    diagnostic surfacing path.
  - `make verify-examples`, `make verify-diagnostics`, and
    `cd editors/vscode && make` — closeout verification surfaces already wired
    by repo policy.

- Duplicate or drifting paths relevant to this change:
  - `docs/LANGUAGE_MECHANICS_SPEC.md` — still says not to add `review_family`
    or `route_only`, which conflicts directly with `docs/04_*`.
  - `docs/WORKFLOW_LAW.md` — currently teaches the workflow-law route-only
    ladder as the shipped route-only story; once dedicated `route_only` lands,
    this doc must distinguish preserved baseline from superseding Phase 4
    surface.
  - `docs/REVIEW_SPEC.md` — currently positions `abstract review` as the
    inheritance-only reusable review story; if `review_family` ships, that
    boundary must be rewritten truthfully.
  - `docs/PHASE3_RENDER_POLICY_AND_EXTENSION_SURFACES_COMPLETION_2026-04-11.md`
    — still records reopened render-profile/lowering gaps that may matter if
    Phase 4 tries to claim profile-sensitive readback behavior beyond the
    already-shipped readable subset.

- Capability-first opportunities before new tooling:
  - Reuse current review agreement, `subject_map`, and carried-field machinery
    before adding any selected-contract wrapper or review-side adapter layer.
  - Reuse current workflow-law branch/currentness/route validations before
    inventing a parallel route-only engine.
  - Reuse current schema artifact/group model before inventing a second
    invalidation-only bucket type.
  - Reuse ordinary `document` / `output` / `trust_surface` readback surfaces
    before inventing side-channel control-plane packets.

- Behavior-preservation signals already available:
  - `examples/57_schema_review_contracts/cases.toml` — schema-backed review
    contract baseline.
  - `examples/30_law_route_only_turns/cases.toml` and
    `examples/42_route_only_handoff_capstone/cases.toml` — route-only baseline.
  - `examples/46_review_current_truth_and_trust_surface/cases.toml`,
    `examples/47_review_multi_subject_mode_and_trigger_carry/cases.toml`, and
    `examples/49_review_capstone/cases.toml` — review current-truth and
    mode-carry baseline.
  - `examples/63_schema_artifacts_and_groups/cases.toml` — schema group
    baseline.
  - `make verify-examples` and `make verify-diagnostics` — repo-wide proof and
    diagnostics guards for closeout.

## 3.3 Open questions (evidence-based)

- Where should `review_family` integrate into the current review compiler path?
  — Settle by tracing the existing review inheritance/field/outcome owner points
  in `doctrine/compiler.py` and choosing the narrowest extension seam.
- Should dedicated `route_only` lower through the existing workflow-law branch
  validator or through a sibling compiled agreement object? — Settle by mapping
  which current workflow-law checks are already reusable without semantic drift.
- Can Phase 4's typed-markdown readback promises ship against the currently
  implemented readable subset, or do they require a narrow Phase 3 prerequisite?
  — Settle by comparing the needed Phase 4 output forms against the reopened
  Phase 3 render-profile/lowering gaps.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- Core language owner path:
  - `doctrine/grammars/doctrine.lark` — shipped declaration grammar for
    `review`, workflow law, `subject_map`, `trust_surface`, `support_only`, and
    `ignore ... for rewrite_evidence`
  - `doctrine/model.py` / `doctrine/parser.py` — AST + parse ownership for the
    same shipped surfaces
  - `doctrine/compiler.py` — semantic owner for review agreement, workflow law,
    invalidation, schema groups, and output agreement
  - `doctrine/renderer.py` / `doctrine/flow_renderer.py` — rendered Markdown and
    flow output
  - `doctrine/diagnostics.py` / `doctrine/diagnostic_smoke.py` — fail-loud
    diagnostic catalog and smoke coverage
- Live truth surfaces:
  - `docs/REVIEW_SPEC.md`
  - `docs/WORKFLOW_LAW.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/LANGUAGE_MECHANICS_SPEC.md`
- Existing proof ladder for the relevant baseline:
  - `examples/30_law_route_only_turns`
  - `examples/40_route_only_local_ownership`
  - `examples/41_route_only_reroute_handoff`
  - `examples/42_route_only_handoff_capstone`
  - `examples/43_review_basic_verdict_and_route_coupling`
  - `examples/46_review_current_truth_and_trust_surface`
  - `examples/47_review_multi_subject_mode_and_trigger_carry`
  - `examples/49_review_capstone`
  - `examples/57_schema_review_contracts`
  - `examples/63_schema_artifacts_and_groups`

## 4.2 Control paths (runtime)

- Review path:
  - `_compile_review_decl()` compiles the top-level review declaration.
  - `_resolve_review_contract_spec()` resolves workflow-or-schema `contract:`
    targets.
  - `_validate_review_outcome_section()` enforces exact route/currentness
    outcomes.
  - `_review_subject_key_from_subject_map()` resolves multi-subject review
    disambiguation from carried mode state.
- Workflow-law control path:
  - `_validate_workflow_law()` is the semantic home for `current none`,
    `current artifact`, route, invalidate, preserve, `support_only`, and
    `ignore` behavior today.
  - `_validate_route_only_next_owner_contract()` and
    `_validate_route_only_standalone_read_contract()` add extra route-only
    validation when a workflow-law branch uses `current none`.
- Schema inventory path:
  - `_resolve_schema_artifacts()`, `_resolve_schema_groups()`, and
    `_validate_schema_group_members()` already compile and validate authored
    inventories and reusable groups.
  - `_validate_invalidation_stmt()` still accepts only one concrete input or
    output artifact root, so invalidation stops before schema-group
    consumption.

## 4.3 Object model + key abstractions

- Shipped first-class declaration families already include `review`,
  `abstract review`, `workflow`, `analysis`, `schema`, `document`, `output`,
  `input`, `agent`, and `enum`.
- The shipped reusable review story is still `abstract review` plus ordinary
  review inheritance. There is no dedicated `review_family` declaration in the
  grammar/model/parser/compiler path.
- The shipped route-only story is still a workflow-law pattern around
  `current none`, not a dedicated `route_only` declaration.
- The shipped grounding story is repeated prose and workflow/readback
  conventions, not a dedicated `grounding` declaration.
- The shipped multi-mode review story uses `subject_map`, carried fields, and
  `match` inside ordinary review outcomes, not a case-selected review-family
  abstraction.

## 4.4 Observability + failure behavior today

- Review and workflow-law diagnostics already fail loud on unknown review
  contract gates, invalid truth carriers, contradictory `current none`
  branches, invalid scope rules, and related control-plane contradictions.
- Route-only branches already trigger extra next-owner interpolation and
  standalone-read checks, but only because they are detected as workflow-law
  branches with `current none`.
- There is no Phase 4-specific diagnostic ladder yet for unknown
  `review_family`, invalid case coverage, unresolved grounding routes, or
  invalid `schema.groups.*` invalidation targets.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. The relevant output surface is emitted Markdown in example refs.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Keep all new Phase 4 semantics on the same compiler path that owns the
  current substrate:
  - declaration syntax in `doctrine/grammars/doctrine.lark`
  - AST and parser support in `doctrine/model.py` and `doctrine/parser.py`
  - semantic lowering, validation, and agreement in `doctrine/compiler.py`
  - emitted Markdown and flow rendering in `doctrine/renderer.py` and
    `doctrine/flow_renderer.py`
  - fail-loud diagnostics in `doctrine/diagnostics.py`
- Extend the example ladder rather than creating sidecar proof harnesses.
- Converge live docs and editor parity in the same closeout path.

## 5.2 Control paths (future)

- `review_family` should integrate into the existing review compile path rather
  than wrapping review in a second resolver:
  - family-owned fields and pre-outcome scaffolds should feed the current
    review field binding, gate evaluation, currentness, and route agreement
    machinery
  - the extension seam should stay near `_compile_review_decl()` and the
    existing review agreement helpers, not in a second post-compile adapter
  - case-selected reviews should compile to the same exact route/currentness
    guarantees the existing review path already enforces
- Dedicated `route_only` should lower through the current workflow-law
  branch/currentness/route semantics rather than inventing a second route-only
  engine:
  - the dedicated declaration may normalize into the same branch checks used by
    `_validate_workflow_law()`
  - the current next-owner interpolation and standalone-read contracts should
    remain one shared validation path
- Dedicated `grounding` should own explicit protocol shape and unresolved-state
  routing, but still emit through ordinary output/document surfaces and reuse
  the existing route/currentness contracts where applicable:
  - no hidden receipt channel
  - no domain-specific grounding engine in core Doctrine
- `schema.groups.*` invalidation should extend the current invalidation path so
  authored groups remain owned by `schema` and readable expansion stays ordered
  and concrete:
  - widen invalidation target resolution instead of adding a second invalidation
    statement kind
  - keep readable expansion in authored group order

## 5.3 Object model + abstractions (future)

- Preserve the existing review/workflow/schema substrate.
- Add only the abstractions Phase 4 explicitly requires:
  - `review_family`
  - explicit review-family case selection
  - `route_only`
  - `grounding`
- Keep readable control-plane output on ordinary `document` / `output` /
  `trust_surface` surfaces instead of introducing packet-like side channels.
- If a narrow Phase 3 prerequisite is needed for truthful control-plane
  readback, record that dependency explicitly and keep it as convergence work,
  not as silent scope drift.
- Default assumption after pass 2: do not reopen Phase 3 broadly. Only reopen a
  narrow Phase 3 item if a specific Phase 4 emitted surface cannot be expressed
  through the already-shipped readable subset.

## 5.4 Invariants and boundaries

- Existing review/workflow/schema behavior stays canonical and must remain
  green while Phase 4 widens the language.
- `review_family` is additive reuse, not a replacement for concrete review
  ownership of subjects, contracts, and outcomes.
- `route_only` must stay explicit about `current none`; it cannot imply a
  durable specialist artifact when none is live.
- `grounding` owns protocol shape, not domain truth or hidden receipts.
- `schema.groups.*` remains authored inventory structure. Invalidation may
  consume it, but it may not duplicate it in a second inventory model.
- Any live doc that contradicts the shipped Phase 4 boundary must be updated
  or demoted in the same run.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. Rendered Markdown snippets in example refs are the relevant
output surface.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar | `doctrine/grammars/doctrine.lark` | top-level declaration grammar; review/workflow/schema grammar | Ships review/workflow/schema + law + `subject_map`, but no `review_family`, `route_only`, or `grounding` declaration surface | Add the dedicated Phase 4 declarations and the supporting syntax for family cases and `schema.groups.*` invalidation targets | The Phase 4 spec promises real language surfaces, not convention-only patterns | Dedicated Phase 4 declaration grammar | New positive and negative corpus; VS Code parity if grammar changes |
| Model / parser | `doctrine/model.py`, `doctrine/parser.py` | review/workflow/schema AST + parse surfaces | AST/parser represent the shipped review/workflow/schema model only | Add typed AST and parsing for `review_family`, case selection, `route_only`, `grounding`, and widened invalidation targets | Keep one compiler-owned representation | New Phase 4 AST / parse contracts | New corpus; parser/resolver parity |
| Review compiler | `doctrine/compiler.py` | `_compile_review_decl()`, `_resolve_review_contract_spec()`, `_validate_review_outcome_section()`, `_review_subject_key_from_subject_map()` | Review already supports workflow/schema contracts, subject_map disambiguation, carried fields, and exact route/currentness outcomes | Integrate `review_family` reuse and case-selected review semantics into the existing review agreement path | Finish Phase 4 review semantics without wrapping them in a second engine | Family-backed review compilation and case-owned exact gate export | Existing review examples plus new Phase 4 review ladder |
| Workflow/control compiler | `doctrine/compiler.py` | `_validate_workflow_law()`, `_validate_route_only_next_owner_contract()`, `_validate_route_only_standalone_read_contract()` | Route-only behavior exists only as workflow-law `current none` branches | Add dedicated `route_only` and `grounding`, lowering through the same branch/currentness/route rules where possible | Finish the promised declarations without drifting from shipped semantics | Dedicated route-only and grounding contracts | Existing route-only ladder plus new Phase 4 corpus |
| Invalidation compiler | `doctrine/compiler.py` | `_validate_invalidation_stmt()` | `invalidate` accepts only one concrete input/output artifact root | Widen invalidation target resolution to consume `schema.groups.*` and support concrete expansion | Phase 4 explicitly promises schema-group invalidation consumption | Widened invalidation target contract | New positive and negative invalidation corpus |
| Schema inventory compiler | `doctrine/compiler.py` | `_resolve_schema_artifacts()`, `_resolve_schema_groups()`, `_validate_schema_group_members()` | Schema artifacts and groups already ship as ordered reusable inventory | Reuse this path as the source of truth for invalidation expansion | Avoid inventing a second inventory model | No new inventory owner path | `63_schema_artifacts_and_groups` stays green; new expansion corpus |
| Rendering / flow | `doctrine/renderer.py`, `doctrine/flow_renderer.py` | review/control readback rendering | Renders existing review/workflow/schema outputs but not the dedicated Phase 4 contracts | Render the new surfaces and concrete invalidation expansion truthfully using ordinary output/document lowering | Keep emitted Markdown and flow artifacts aligned with shipped semantics | Phase 4 readable rendering behavior | New ref outputs; flow outputs if touched |
| Diagnostics | `doctrine/diagnostics.py`, `doctrine/diagnostic_smoke.py` | review/workflow/control-plane diagnostics | Existing diagnostics stop short of Phase 4-specific failures | Add fail-loud diagnostics for unknown family, invalid case coverage, unresolved grounding routes, and invalid group invalidations | The Phase 4 spec requires a negative ladder, not best-effort behavior | Phase 4 diagnostic catalog | `make verify-diagnostics`; negative corpus |
| Live docs / examples / editor | `docs/REVIEW_SPEC.md`, `docs/WORKFLOW_LAW.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_MECHANICS_SPEC.md`, `examples/*`, `editors/vscode/resolver.js` | live truth surfaces and proof ladder | Docs teach the baseline and some contradictory design guidance | Converge docs, proof ladder, and editor parity to the shipped Phase 4 boundary | Close split truth and keep tooling honest | Updated language/docs/editor contracts | `make verify-examples`; `cd editors/vscode && make` if touched |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - Keep all new semantics on the shared grammar -> model -> parser ->
    compiler -> renderer path.
- Deprecated APIs (if any):
  - None yet. The likely migration is docs/examples truth convergence rather
    than API deletion.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - Delete or rewrite live doc claims that `review_family` and `route_only`
    should not exist once the code ships them.
- Capability-replacing harnesses to delete or justify:
  - No new harnesses are justified at planning time. Reuse current review,
    workflow-law, schema, and output/readback semantics first.
- Live docs/comments/instructions to update or delete:
  - `docs/LANGUAGE_MECHANICS_SPEC.md`
  - `docs/WORKFLOW_LAW.md`
  - `docs/REVIEW_SPEC.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `examples/README.md`
- Behavior-preservation signals for refactors:
  - `examples/30`, `40`, `41`, `42`, `46`, `47`, `49`, `57`, and `63`
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics change
- Narrow dependency stance:
  - do not block Phase 4 on a broad Phase 3 reopen
  - only elevate a specific Phase 3 gap if a concrete Phase 4 output contract
    cannot be emitted truthfully without it

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Review reuse | `docs/REVIEW_SPEC.md`, `doctrine/compiler.py` review path | Fold reusable review scaffolds into `review_family` on top of the existing review agreement path | Prevent parallel reusable-review stories (`abstract review` only vs new family semantics) | include |
| Route-only semantics | `docs/WORKFLOW_LAW.md`, route-only examples, workflow-law validators | Keep workflow-law route-only checks as substrate for dedicated `route_only` | Prevent a second route/currentness engine | include |
| Inventory consumption | schema group compiler + invalidation validation | Reuse shipped schema groups for invalidation targets and expansion | Prevent a second invalidation inventory type | include |
| Readback polish | `docs/PHASE3_RENDER_POLICY_AND_EXTENSION_SURFACES_COMPLETION_2026-04-11.md` | Reopen only the narrow readable-lowering prerequisite if Phase 4 truly needs it | Prevent Phase 4 from silently absorbing unrelated Phase 3 scope | defer |
| Historical design guidance | `docs/LANGUAGE_MECHANICS_SPEC.md` | Remove or rewrite anti-Phase-4 guidance after code lands | Prevent contradictory live doctrine | include |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan. Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. No fallbacks or runtime shims. Prefer programmatic checks per phase and delete or rewrite stale live docs in the same run when reality changes.

## 7.1 Phase 1 - Promise audit and baseline lock

Goal:
- Lock the exact shipped Phase 4 baseline versus genuinely missing work before
  code changes start.

Work:
- Audit `docs/04_*` promise by promise against current code, examples, and live
  docs.
- Confirm the preserved baseline:
  schema-backed review contracts, review currentness/trust carriers,
  workflow-law route-only behavior, and schema groups.
- Confirm the contradictory live-doc inventory and the narrow Phase 3
  dependency rule.

Verification (smallest signal):
- Read-only evidence pass recorded in Sections 3 through 6.

Docs/comments (propagation; only if needed):
- Keep the plan artifact honest if any additional contradiction appears before
  implementation begins.

Exit criteria:
- Implementation can tell "already shipped prerequisite" from "missing Phase 4
  surface" without guesswork.

Rollback:
- No code change yet; doc-only correction.

## 7.2 Phase 2 - Review family and case-selected review core

Status: COMPLETED

Goal:
- Ship `review_family` and the explicit case-selected review surface on top of
  the current review agreement path.

Work:
- Add grammar/model/parser support for `review_family` and case selection.
- Extend `_compile_review_decl()` and the existing review agreement helpers so
  family-owned fields and pre-outcome scaffolds feed the same currentness,
  contract, and route machinery.
- Preserve workflow-or-schema `contract:` behavior, exact gate export, and
  current subject disambiguation.
- Add targeted examples for review-family inheritance/patching and
  case-selected review routing/currentness.

Verification (smallest signal):
- Targeted manifest-backed runs for the new review-family ladder plus the
  existing review baselines in `43`, `46`, `47`, `49`, and `57`.
- Compile-negative cases for unknown family, overlapping/non-total case sets,
  and unresolved subject/contract surfaces.

Docs/comments (propagation; only if needed):
- Update `docs/REVIEW_SPEC.md` and `docs/LANGUAGE_REFERENCE.md`.
- Remove or rewrite any surviving live claim that `abstract review` is the only
  reusable review surface once `review_family` ships.

Exit criteria:
- The dedicated review-family surface exists as shipped language and does not
  regress existing review semantics.

Rollback:
- Revert to the last fully green review baseline if the widened review path
  breaks existing review examples.

## 7.3 Phase 3 - Dedicated route_only and grounding core

Status: COMPLETED

Goal:
- Ship dedicated `route_only` and `grounding` declarations without creating a
  second route/currentness engine.

Work:
- Add grammar/model/parser support for `route_only` and `grounding`.
- Lower `route_only` through the existing workflow-law branch/currentness/route
  semantics where possible, preserving `current none`, next-owner interpolation,
  and standalone-read contracts.
- Add `grounding` protocol semantics for explicit policy and unresolved-state
  routing while keeping output/readback on ordinary surfaces.
- Add targeted examples for route-only and grounding behavior.

Verification (smallest signal):
- Targeted manifest-backed runs for the new route-only/grounding ladder plus
  the existing route-only baselines in `30`, `40`, `41`, and `42`.
- Compile-negative cases for unresolved route targets, contradictory
  currentness, and unresolved grounding routing.

Docs/comments (propagation; only if needed):
- Update `docs/WORKFLOW_LAW.md` and `docs/LANGUAGE_REFERENCE.md`.
- Reframe the workflow-law route-only example ladder as preserved baseline
  rather than the final Phase 4 answer once dedicated `route_only` lands.

Exit criteria:
- Dedicated route-only and grounding surfaces compile, render, fail loudly, and
  preserve the shipped control-plane rules.

Rollback:
- Fall back to the existing workflow-law-only baseline if the new declarations
  regress shipped behavior before the phase is green.

## 7.4 Phase 4 - Schema-group invalidation consumption and control-plane integration

Status: COMPLETED

Goal:
- Consume the already-shipped schema inventory/group surface and integrate the
  new declarations into one coherent control-plane semantics story.

Work:
- Widen invalidation target resolution to accept `schema.groups.*`.
- Expand group invalidations into concrete member-level readback in authored
  group order.
- Integrate `review_family`, `review`, `route_only`, and `grounding` with
  `trust_surface`, `support_only`, `ignore rewrite_evidence`, and current-truth
  carriage.
- Reopen only a narrow Phase 3 prerequisite if a specific emitted Phase 4
  output cannot be expressed truthfully through the already-shipped readable
  subset.

Verification (smallest signal):
- Targeted manifest-backed runs for group invalidation consumption and
  current-truth integration.
- Compile-negative cases for invalid group targets and contradictory carrier
  use.

Docs/comments (propagation; only if needed):
- Update `docs/WORKFLOW_LAW.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/LANGUAGE_REFERENCE.md`, and diagnostics docs as needed.

Exit criteria:
- Group invalidation consumption is shipped and documented, and the control
  plane reads as one consistent semantics story.

Rollback:
- Revert to concrete-root-only invalidation targets if group consumption proves
  unsound before the phase is green.

## 7.5 Phase 5 - Proof, docs, editor parity, and closeout

Status: COMPLETED

Goal:
- Leave one honest Phase 4 completion story everywhere the repo teaches or
  validates the language.

Work:
- Run and fix the full example/diagnostic/editor ladder for touched surfaces.
- Add or update manifest-backed refs for every new positive and negative Phase 4
  example.
- Converge live docs, phase docs, and contradictory design notes, especially
  `docs/LANGUAGE_MECHANICS_SPEC.md`.
- Update editor parity if grammar/navigation changed.

Verification (smallest signal):
- `make verify-examples`
- `make verify-diagnostics` when diagnostics changed
- targeted manifest-backed example runs during iteration
- `cd editors/vscode && make` if `editors/vscode/` changed

Docs/comments (propagation; only if needed):
- Keep public docs and examples generic, and delete stale contradiction rather
  than preserving it beside shipped truth.

Exit criteria:
- Code, examples, docs, diagnostics, and editor surfaces all agree on the
  Phase 4 boundary.

Rollback:
- Revert only the non-green closeout slice; keep already-verified foundational
  work intact.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Programmatic checks

- Use targeted manifest-backed runs while implementing each new example ladder.
- Run `make verify-examples` for the full shipped corpus before closeout.
- Run `make verify-diagnostics` when diagnostics or diagnostic smoke surfaces
  change.
- Run `cd editors/vscode && make` if grammar, resolver, or editor surfaces
  change.

## 8.2 Preservation checks

- Keep the current baseline examples green unless an explicitly justified bug
  fix changes behavior.
- Prefer behavior-level corpus proof over structure-sensitive test scaffolding.
- Use the first failing corpus or diagnostic line as the routing signal when
  implementation diverges.

## 8.3 Manual checks

- Non-blocking manual review of emitted Markdown/flow refs only if a new
  rendered surface is difficult to trust from corpus output alone.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout shape

- This is compiler/docs/example/editor work, not a runtime service rollout.
- Rollout means merging a truthful language boundary, not gating live traffic.

## 9.2 Operational implications

- The important operational surface is example/diagnostic/editor parity.
- If new declarations change flow visualization output, keep `docs/EMIT_GUIDE.md`
  and emitted refs aligned.

## 9.3 Telemetry / follow-through

- No product telemetry is required.
- The durable follow-through signal is a green verification ladder plus the
  absence of live contradictory docs.

# 10) Decision Log (append-only)

- 2026-04-11 - Bootstrapped a new canonical completion plan doc instead of
  rewriting `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md`
  in place. Reason: `docs/04_*` remains the requested-scope Phase 4 spec, while
  this doc owns the honest shipped-vs-missing completion plan.
- 2026-04-11 - Locked the initial baseline assumption that schema-backed review
  contracts, workflow-law route-only/currentness primitives, and schema groups
  are already shipped prerequisites that must be preserved while finishing the
  missing dedicated Phase 4 surfaces.
- 2026-04-11 - Deep-dive pass 2 locked the implementation stance that
  `review_family` must extend the current review agreement path, dedicated
  `route_only` must reuse workflow-law branch validation instead of creating a
  parallel engine, and Phase 3 render-profile gaps are a narrow dependency only
  if a specific Phase 4 emitted surface cannot be expressed through the
  already-shipped readable subset.
- 2026-04-11 - Auto-plan completed on the Phase 4 artifact from repo evidence
  only. Research grounding, both deep-dive passes, and the authoritative
  phase plan are now present, and the next bounded controller move is
  `implement-loop`.
- 2026-04-11 - Shipped `review_family`, case-selected review families,
  dedicated `route_only`, dedicated `grounding`, and schema-group invalidation
  consumption on the shared compiler path. Added manifest-backed proof in
  `examples/68_*` through `examples/72_*`, fixed schema-group current-artifact
  overlap validation, converged live docs, and restored VS Code keyword and
  declaration coverage before the final verification pass.
