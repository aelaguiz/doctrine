---
title: "Paperclip - Lessons Symbolic Doctrine Port - Architecture Plan"
date: 2026-04-10
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: parity_plan
related:
  - docs/LESSONS_SYMBOLIC_DOCTRINE_FEATURE_EVALUATION_2026-04-10.md
  - docs/LESSONS_DOCTRINE_PORT_INTUITION_GUIDE_2026-04-07.md
  - ../doctrine/docs/WORKFLOW_LAW.md
  - ../doctrine/docs/REVIEW_SPEC.md
  - ../doctrine/examples/README.md
  - ../doctrine/examples/38_metadata_polish_capstone/prompts/AGENTS.prompt
  - ../doctrine/examples/42_route_only_handoff_capstone/prompts/AGENTS.prompt
  - ../doctrine/examples/49_review_capstone/prompts/AGENTS.prompt
  - ../doctrine/examples/50_bound_currentness_roots/prompts/AGENTS.prompt
  - ../doctrine/examples/51_inherited_bound_io_roots/prompts/AGENTS.prompt
  - ../doctrine/examples/52_bound_scope_and_preservation/prompts/AGENTS.prompt
  - ../doctrine/examples/53_review_bound_carrier_roots/prompts/AGENTS.prompt
---

# TL;DR

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-11
Verdict (code): NOT COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- Phase 4 exact failing-gate export is still incomplete. The critic now has a
  real first-class `review` surface plus shared `Failing Gates` and `Failing
  Gate If Blocked` carrier fields, but `LessonsCriticReview` still rejects
  through the generic `ReviewState.selected_review_basis_failed` and
  `ReviewState.scope_boundary_failed` branches instead of exporting the exact
  shared-contract gate that failed.
- Phase 5 is narrower than the prior audit said, but it is still incomplete.
  Section architecture, lesson planning, and materialization now land typed
  invalidation and preserved-upstream state in the authored source and the
  generated homes. The remaining Phase 5 blocker is curator dependency-order
  ownership, which still lives in prose and emitted `Does not choose`
  language instead of a typed workflow owner. The section-architecture
  `late_metadata_handoff` content seam is no longer a blocker here because the
  call-site audit now treats further carrier tightening there as optional
  after the typed state and restart export landed.

## Reopened phases (false-complete fixes)
- None. Fresh source and generated-home checks still show Phase 1 shared
  carriers in `doctrine/prompts/lessons/outputs/outputs.prompt`, Phase 2 typed
  metadata workflow law in
  `doctrine/prompts/lessons/contracts/metadata_wording.prompt`, Phase 3
  route-only workflow law in
  `doctrine/prompts/lessons/agents/lessons_project_lead/AGENTS.prompt`, and
  the newer typed invalidation exports in `section_architecture.prompt`,
  `lesson_plan.prompt`, and `materialization.prompt`. Phases 4 and 5 already
  remain `PARTIAL`, so this audit did not need to reopen any falsely complete
  phase status line.

## Missing items (code gaps; evidence-anchored; no tables)
- Exact failing-gate export on the first-class critic review
  - Evidence anchors:
    - `doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt:151`
    - `doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt:152`
    - `doctrine/prompts/lessons/outputs/outputs.prompt:246`
    - `doctrine/prompts/lessons/outputs/outputs.prompt:249`
    - `doctrine/build/lessons/agents/lessons_acceptance_critic/AGENTS.md:100`
    - `doctrine/build/lessons/agents/lessons_acceptance_critic/AGENTS.md:102`
    - `doctrine/build/lessons/agents/lessons_acceptance_critic/AGENTS.md:584`
    - `doctrine/build/lessons/agents/lessons_acceptance_critic/AGENTS.md:588`
    - `paperclip_home/agents/lessons_acceptance_critic/AGENTS.md:100`
    - `paperclip_home/agents/lessons_acceptance_critic/AGENTS.md:102`
    - `paperclip_home/agents/lessons_acceptance_critic/AGENTS.md:584`
    - `paperclip_home/agents/lessons_acceptance_critic/AGENTS.md:588`
  - Plan expects:
    - Phase 4 moves the critic onto shipped `review` features with explicit
      block, reject, accept, current truth, exact failing-gate export, and
      routed next-owner behavior.
  - Code reality:
    - The source now has `Failing Gates` and `Failing Gate If Blocked` in the
      shared critic output plus `failing_gates` and `blocked_gate` on
      `BaseLessonsArtifactReview`.
    - `LessonsCriticReview` still uses the generic rejects `The selected review
      basis failed.` and `The selected review scope boundary failed.`
    - A direct attempt to switch those mode-specific rejects to exact
      `contract.<gate>` lines still triggered Doctrine compiler recursion and
      was backed out.
    - The emitted build and runtime critic homes now expose the failure-detail
      headings, but the exact per-mode contract gate still never becomes the
      reject surface that drives those fields.
  - Fix:
    - Tighten the mode-specific review surface so each reject or block carries
      the exact shared-contract gate identity through `failing_gates` or
      `failing_gate_if_blocked`, and keep the change compile-safe across the
      source, emitted build homes, and runtime homes.
- Typed dependency-order ownership on the curator seam
  - Evidence anchors:
    - `doctrine/prompts/lessons/contracts/section_concepts_terms.prompt:77`
    - `doctrine/prompts/lessons/contracts/section_concepts_terms.prompt:132`
    - `doctrine/prompts/lessons/contracts/section_concepts_terms.prompt:133`
    - `doctrine/prompts/lessons/contracts/section_concepts_terms.prompt:134`
    - `doctrine/prompts/lessons/contracts/section_concepts_terms.prompt:157`
    - `doctrine/prompts/lessons/contracts/section_concepts_terms.prompt:158`
    - `doctrine/prompts/lessons/contracts/section_concepts_terms.prompt:161`
    - `doctrine/prompts/lessons/contracts/section_concepts_terms.prompt:163`
    - `doctrine/build/lessons/agents/section_concepts_terms_curator/AGENTS.md:529`
    - `paperclip_home/agents/section_concepts_terms_curator/AGENTS.md:529`
  - Plan expects:
    - Phase 5 turns curator dependency-order ownership into typed law instead
      of leaving final sequencing boundaries in surrounding prose.
  - Code reality:
    - `SectionConceptsTermsWorkflow` now owns typed currentness, preserved
      dossier truth, preserved term-surface structure, and a blocked
      `current none` stop-line back to `LessonsProjectLead`.
    - Dependency order still sits in `Dependency Notes` and `Step 7 - Set
      Dependency Order`, and the emitted curator homes still say `Does not
      choose dependency order for final concept sequencing.` instead of
      exposing a typed preserved-order owner.
  - Fix:
    - Port the remaining dependency-order ownership into typed workflow law, or
      explicitly narrow the plan if prose is the honest final owner for that
      seam.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

Outcome

Port the current Lessons doctrine family onto the shipped Doctrine workflow-law
and review features so the runtime homes get more explicit, less ambiguous, and
less drift-prone without losing operational nuance, poker-quality constraints,
or the current owner model.

Problem

The current Lessons port already improved ownership, tone, and runtime
readability, but too much real behavior is still carried by sprawling prose.
Important seams like currentness, route-only turns, metadata mode state, narrow
scope preservation, rewrite-evidence exclusions, downstream invalidation, and
the critic's exact verdict logic still depend on wording conventions instead of
compiler-owned structure. That makes subtle meaning easier to lose and harder to
cold-read.

Approach

Treat this as a structure-preserving symbolic port, not a cleanup pass and not
a rewrite for brevity. Move only the semantics that the shipped Doctrine
language can honestly own today into typed workflow-law and review surfaces.
Keep human mission, rationale, and taste guidance in prose. For every migrated
seam, preserve exact step order, conditions, hard negatives, escalation logic,
and poker-quality constraints, and keep the source meaning recoverable while the
port is in flight.

Plan

Implement in six phases:

1. Strengthen shared output carriers so current artifact, trusted readback,
   blocked-gate state, and next-owner state stop hiding in prose.
2. Use metadata as the proving seam for mode handling, one-current-file law,
   narrow scope, exact preservation, and rewrite-evidence exclusions.
3. Formalize Lessons Project Lead route-only turns with workflow law instead of
   repeated narrative coordination rules.
4. Migrate Lessons Acceptance Critic to first-class review so verdicts, failing
   gates, blocked review, routed ownership, and current truth become typed.
5. Sweep preservation, invalidation, and law reuse across the remaining
   producer contracts without widening product behavior.
6. After each source phase, run `make agents`, cold-read the emitted homes, and
   update touched docs or config so no stale truth survives the cutover.

Non-negotiables

This is not an exercise in compression. No symbolic change is allowed to drop
real instructional nuance. Do not use personal judgment as a substitute for
current poker doctrine. Use shipped Doctrine features only; do not design
around future stdlib. Keep one owner per seam, one live route per seam, and no
new fallback owners, backup modes, wrapper workflows, or shadow doctrine
systems. If a Doctrine feature cannot yet preserve a seam honestly, keep that
meaning in prose until it can.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-10
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-10
phase_plan: done 2026-04-10
recommended_flow: implement
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

Worklog: `docs/LESSONS_SYMBOLIC_DOCTRINE_PORT_IMPLEMENTATION_PLAN_2026-04-10_WORKLOG.md`

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

We can port the current Lessons doctrine family onto the shipped Doctrine
workflow-law and review features without losing meaning because the largest
remaining drift buckets are semantic, not stylistic. The language is now strong
enough to own currentness, mode state, narrow write scope, preserved truth,
rewrite-evidence exclusions, route-only law, downstream invalidation, and
critic verdict mechanics directly.

This claim is false if any of these happen during the port:

- an emitted home loses a real stop line, condition, escalation path, or hard
  negative that existed before
- a poker-quality rule, review gate, or preserved upstream lock gets weakened
  into a summary
- a route, current artifact, or metadata mode becomes less explicit than it is
  today
- a new symbolic surface requires extra prose to recover meaning that the old
  prose already carried clearly
- the port introduces new workflow layers, fallback routes, or convenience
  instructions that were not part of the live Lessons family

## 0.2 In scope

- Port the current Lessons doctrine family under `doctrine/prompts/lessons/**`
  onto shipped Doctrine workflow-law and review features already proven in
  `../doctrine/docs/**` and `../doctrine/examples/**`.
- Preserve the current owner model across shared owners, local role prompts,
  emitted build readback, and runtime homes.
- Make hidden schemas explicit where the current doctrine is using prose to
  carry routing, currentness, preservation, comparison, rewrite, or review
  law.
- Keep role mission, rationale, and quality posture in human prose where the
  Doctrine language is not supposed to replace judgment.
- Update `paperclip_home/agents/agent_configs.json` and touched repo docs when
  a doctrine change would otherwise leave stale current-state truth behind.
- Compile and cold-read the affected emitted homes after each source phase.
- Keep a recoverable source-to-symbol mapping for any seam where the port
  replaces dense instruction-bearing prose with a symbolic carrier.

Allowed architectural convergence scope:

- tighten existing shared owners such as `outputs.prompt`, `role_home.prompt`,
  and current Lessons contracts
- move duplicated local review or routing law back into shared or typed owners
- delete superseded repeated prose once the new owner is real and the emitted
  readback is proven
- adjust related docs that would otherwise keep a false live story alive

## 0.3 Out of scope

- Future Doctrine stdlib work
- New Lessons product behavior, new lesson-authoring modes, or new runtime tool
  flows
- Reinterpreting poker instruction or relaxing the existing quality bar because
  the symbolic form is easier to write
- A compression pass whose goal is shorter prompts
- Vendor changes under `vendor/paperclip/**`
- A second doctrine framework, temporary compatibility layer, or shadow
  sidecar plan system
- Runtime wrapper changes or new operator choreography

## 0.4 Definition of done (acceptance evidence)

The port is done when all of this is true:

- every targeted semantic seam has one explicit owner in shipped Doctrine
  language or remains intentionally in prose with a stated reason
- the changed prompt owners compile cleanly and sync through `make agents`
- the affected emitted homes stay direct, linear, and cold-readable without
  losing material nuance from the source owners they replaced
- side-by-side cold reads show that route-only logic, metadata mode logic,
  current file truth, preserved-scope rules, rewrite-evidence exclusions, and
  critic verdict behavior are at least as explicit as before
- the critic exports exact failing-gate identities and correct next-owner logic
  without relying on repeated prose scaffolds
- touched docs and `paperclip_home/agents/agent_configs.json` no longer tell a
  stale current Lessons story

Smallest credible acceptance evidence:

- `make agents`
- cold-read of the changed emitted homes under `doctrine/build/lessons/agents`
  and `paperclip_home/agents`
- targeted source-to-output checks on the seams that moved from prose to
  symbolic form

## 0.5 Key invariants (fix immediately if violated)

- No compression that drops real order, conditions, hard negatives, examples,
  or escalation logic.
- No use of personal judgment to replace current poker doctrine or grounding
  rules.
- No new fallback owners, backup modes, alternate live routes, or shadow
  workflow layers.
- No second source of truth for the same seam.
- No symbolic carrier that is weaker than the prose it replaces.
- If a seam cannot be preserved honestly in symbolic form today, keep it in
  prose and record why.
- Every source phase ends with a compile and a cold read before the next phase
  claims success.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Preserve meaning exactly where the current doctrine is carrying real
   behavioral constraint.
2. Move semantic seams into shipped compiler-owned surfaces wherever the
   language can now own them honestly.
3. Keep emitted runtime homes easier to cold-read, not harder.
4. Preserve one-owner-per-seam discipline across shared owners and role-local
   prompts.
5. Avoid introducing new instruction sprawl while we formalize the existing
   behavior.
6. Keep the migration incremental enough that each phase can be verified before
   the next one lands.

## 1.2 Constraints

- This plan is limited to shipped Doctrine features, not proposal-only syntax
  or future stdlib.
- The current Lessons port direction in
  `docs/LESSONS_DOCTRINE_PORT_INTUITION_GUIDE_2026-04-07.md` remains the style
  and owner-model baseline.
- The current runtime truth lives in emitted homes under
  `paperclip_home/agents/**`, not in author intent alone.
- The Lessons family is interleaved by critic review. The port must preserve
  that cadence.
- `make agents` is the current compile and sync path.
- Shared law should move to shared owners, not be recopied with local phrasing.
- The migration must preserve one durable artifact per lane and skill-first
  capability stories.

## 1.3 Architectural principles (rules we will enforce)

- Preserve explicit operational structure before chasing shorter text.
- Only move a seam into symbolic form when the Doctrine feature can fully own
  the behavior the prose was carrying.
- Prefer typed currentness, typed routing, typed preservation, and typed review
  over prose conventions where the language already supports them.
- Keep human prose for mission, rationale, and judgment-heavy taste bars.
- Repair the smallest honest owner that already governs the seam.
- Use hard cutover and explicit deletes when the new owner is proven.
- Keep recoverability of source meaning visible while a seam is being ported.

## 1.4 Known tradeoffs (explicit)

- Some source owners may become denser while emitted homes get simpler. That is
  acceptable if the runtime readback becomes clearer and the source meaning is
  still recoverable.
- Some seams may stay partly prose because preserving nuance is more important
  than forcing symbolic uniformity.
- The critic migration is the highest leverage change, but not the safest first
  move. Shared carriers and the metadata pilot should land first.
- A symbolic port can remove repeated prose, but brevity is a side effect here,
  not the goal.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Today the Lessons family already has a stronger owner model than the old port:

- shared role-home structure under
  `doctrine/prompts/lessons/common/role_home.prompt`
- shared skill story under
  `doctrine/prompts/lessons/common/skills.prompt`
- shared output contracts under
  `doctrine/prompts/lessons/outputs/outputs.prompt`
- shared producer and review contracts under
  `doctrine/prompts/lessons/contracts/**`
- role-local doctrine under `doctrine/prompts/lessons/agents/**`
- emitted readback under `doctrine/build/lessons/agents/**`
- runtime readback under `paperclip_home/agents/**`

The port already improved direct language, narrowed capabilities, and pushed
shared meaning into smaller owners.

## 2.2 What’s broken / missing (concrete)

The remaining drift is concentrated in semantics that are still carried by
prose:

- current artifact and trusted readback rules in shared outputs
- metadata mode, file-currentness, and rewrite-state handling
- route-only turns and no-current-artifact turns for Lessons Project Lead
- critic verdict mechanics, exact failing-gate export, blocked review, and
  routed next-owner logic
- preserved upstream decisions, preserved mappings, preserved vocabulary, and
  downstream invalidation across producer seams

Those rules are subtle and important. Right now they live in repeated wording
that is easy to copy, weaken, or paraphrase.

## 2.3 Constraints implied by the problem

This means the port cannot be a style pass. It needs to:

- distinguish prose that is secretly schema from prose that is truly human
  guidance
- migrate shared carriers before the critic rewrite so later phases are not
  guessing at missing typed state
- prove the new model on a narrow seam before spending it on the largest seam
- validate success by cold-reading emitted homes, not by trusting source
  elegance

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- `../doctrine/docs/WORKFLOW_LAW.md` - adopt as the authoritative description
  of shipped workflow-law features that can now own route, currentness, mode,
  preservation, and invalidation semantics directly.
- `../doctrine/docs/REVIEW_SPEC.md` - adopt as the authoritative description of
  shipped first-class review features that can now own critic verdict,
  handoff-first blocking, failing-gate export, carried state, and routed
  next-owner logic.
- `../doctrine/examples/31_currentness_and_trust_surface/prompts/AGENTS.prompt`
  - adopt for shared carrier design because the Lessons family still carries
  current artifact and trusted readback mostly by prose convention.
- `../doctrine/examples/38_metadata_polish_capstone/prompts/AGENTS.prompt` -
  adopt as the closest shipped pattern for the metadata seam because it proves
  mode binding, currentness, narrow scope, exact preservation, comparison-only
  support, rewrite exclusions, and invalidation in one place.
- `../doctrine/examples/42_route_only_handoff_capstone/prompts/AGENTS.prompt`
  - adopt as the closest shipped pattern for Lessons Project Lead route-only
  turns because it proves `current none`, route-only activation, guarded
  readback, and explicit reroute coupling.
- `../doctrine/examples/44_review_handoff_first_block_gates/prompts/AGENTS.prompt`
  - adopt for critic handoff-first stop behavior because the current critic
  explicitly sends vague or incomplete producer handoffs back before content
  review starts.
- `../doctrine/examples/45_review_contract_gate_export_and_exact_failures/prompts/AGENTS.prompt`
  - adopt for exact shared-contract gate export because the current critic
  insists on naming exact failing gates rather than vague rejection summaries.
- `../doctrine/examples/47_review_multi_subject_mode_and_trigger_carry/prompts/AGENTS.prompt`
  - adopt for carried mode and trigger state where metadata routing or
  multi-subject review still needs typed downstream state.
- `../doctrine/examples/49_review_capstone/prompts/AGENTS.prompt` - adopt as
  the closest full capstone for the critic migration.
- Future stdlib notes - reject for this plan's implementation scope. They may
  inform later cleanup, but they are not available to depend on now.

## 3.2 Internal ground truth (code as spec)

Authoritative behavior anchors:

- `docs/LESSONS_SYMBOLIC_DOCTRINE_FEATURE_EVALUATION_2026-04-10.md` - current
  repo-owned synthesis of which shipped Doctrine features fit which remaining
  Lessons seams.
- `docs/LESSONS_DOCTRINE_PORT_INTUITION_GUIDE_2026-04-07.md` - current style
  and owner-model baseline for the active Lessons port.
- `doctrine/prompts/lessons/outputs/outputs.prompt` - current shared owner for
  producer, route-only, and critic comment contracts, including the current
  metadata comment-state carrier.
- `doctrine/prompts/lessons/common/role_home.prompt` - current shared owner for
  turn order, current-truth rules, and generic handoff expectations that still
  reference output carriers.
- `doctrine/prompts/lessons/contracts/metadata_wording.prompt` - current owner
  of metadata mode, one-current-file expectations, preserved-field rules, and
  metadata review law.
- `doctrine/prompts/lessons/agents/lessons_project_lead/AGENTS.prompt` -
  current owner of route-only, process-repair, and publish-follow-up local
  behavior.
- `doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt` -
  current owner of the critic's repeated review scaffolds, routing, and local
  review posture.
- `doctrine/prompts/lessons/contracts/section_architecture.prompt` - current
  owner of `late_metadata_handoff` and `downstream_invalidation`, which are the
  clearest existing producer seams for typed preservation and invalidation.
- `doctrine/prompts/lessons/contracts/section_concepts_terms.prompt`,
  `doctrine/prompts/lessons/contracts/lesson_plan.prompt`, and
  `doctrine/prompts/lessons/contracts/materialization.prompt` - current owners
  of several preserved-truth, rewrite, and narrow-scope rules that later phases
  should formalize where the language is strong enough.
- `doctrine/Makefile` - current emit-target inventory for Lessons, Core Dev,
  and PRD Factory.
- `Makefile` - current repo-level `make agents` orchestration path for compile,
  skill import, and runtime config sync.
- `paperclip_home/agents/agent_configs.json` - runtime desired-skill allowlist
  that must stay aligned with any changed skill story.

Canonical paths or owners to reuse:

- `doctrine/prompts/lessons/outputs/outputs.prompt` - shared output carrier
  owner; tighten this first instead of scattering new handoff rules into role
  prompts.
- `doctrine/prompts/lessons/contracts/metadata_wording.prompt` - narrow pilot
  seam for workflow-law adoption.
- `doctrine/prompts/lessons/agents/lessons_project_lead/AGENTS.prompt` -
  correct local owner for route-only delta once the shared carriers are ready.
- `doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt` -
  correct local owner for critic-local review posture once first-class review
  owns the mechanics.
- `doctrine/prompts/lessons/contracts/**` - correct shared owners for producer
  preservation and invalidation law.

Existing patterns to reuse:

- `../doctrine/examples/31_currentness_and_trust_surface/prompts/AGENTS.prompt`
  - portable currentness and trust-surface carrier pattern.
- `../doctrine/examples/38_metadata_polish_capstone/prompts/AGENTS.prompt` -
  one-mode metadata capstone pattern.
- `../doctrine/examples/42_route_only_handoff_capstone/prompts/AGENTS.prompt`
  - route-only capstone pattern.
- `../doctrine/examples/49_review_capstone/prompts/AGENTS.prompt` - full
  review capstone pattern.

Prompt surfaces and runtime readback to preserve:

- `doctrine/build/lessons/agents/lessons_project_lead/AGENTS.md` - canary
  emitted home for route-only clarity.
- `doctrine/build/lessons/agents/lessons_metadata_copywriter/AGENTS.md` -
  canary emitted home for mode, file-currentness, and narrow scope.
- `doctrine/build/lessons/agents/lessons_acceptance_critic/AGENTS.md` - canary
  emitted home for review and verdict clarity.
- `paperclip_home/agents/lessons_project_lead/AGENTS.md`,
  `paperclip_home/agents/lessons_metadata_copywriter/AGENTS.md`, and
  `paperclip_home/agents/lessons_acceptance_critic/AGENTS.md` - runtime truth
  surfaces that must still read clearly after compile and sync.

Native compiler and repo capabilities to lean on:

- shipped Doctrine workflow-law support for `current none`, typed mode, typed
  current artifacts, preservation, invalidation, and route coupling
- shipped Doctrine review support for `review`, `block`, exact contract-gate
  export, current truth, and routed outcomes
- existing compile path under `make agents`; no new harness is needed to render
  the changed runtime homes

Existing file and tool exposure:

- prompt owners under `doctrine/prompts/lessons/**`
- emitted readback under `doctrine/build/lessons/agents/**`
- runtime readback under `paperclip_home/agents/**`
- shipped Doctrine docs and examples under `../doctrine/docs/**` and
  `../doctrine/examples/**`

Duplicate or drifting paths relevant to this change:

- metadata route state is currently split across
  `doctrine/prompts/lessons/outputs/outputs.prompt`,
  `doctrine/prompts/lessons/contracts/metadata_wording.prompt`,
  `doctrine/prompts/lessons/agents/lessons_project_lead/AGENTS.prompt`,
  `doctrine/prompts/lessons/agents/lessons_metadata_copywriter/AGENTS.prompt`,
  and `doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt`
- route-only currentness and no-current-artifact truth are currently split
  across `role_home.prompt`, `outputs.prompt`, and
  `lessons_project_lead/AGENTS.prompt`
- critic review mechanics are repeated across nine local review families in
  `doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt`
- preserved upstream truth and invalidation logic are still expressed largely
  as prose across producer contracts rather than shared typed law

Capability-first opportunities before new tooling:

- use shipped workflow-law and review surfaces directly before inventing any
  temporary doctrine mini-framework, helper checklist, or new support script
- use guarded output sections, trust surfaces, exact contract-gate export, and
  typed preservation/invalidation before adding more comment-format prose

Behavior-preservation signals already available:

- `make agents`
- cold-read of emitted canary homes for project lead, metadata copywriter, and
  critic
- targeted source-to-output comparisons on seams moved from prose to symbolic
  carriers
- existing phrase-count evidence showing where semantic sprawl currently sits,
  including `current file: 50` and `At minimum confirm: 112` across the current
  Lessons prompt family
- exact repeated local critic posture markers still visible today, including
  `Do not rewrite that producer truth here.` and `Who It Goes Back To` each
  repeated `9` times in the critic prompt

## 3.3 Open questions from research

- Which current seams still contain instruction-bearing nuance that the shipped
  symbolic surfaces cannot yet preserve without a supporting prose layer?
- What is the smallest durable mapping surface that keeps replaced source
  meaning recoverable during the migration?
- Which current review-specific posture should stay prose even after the critic
  moves to first-class review?
- How much inherited review structure can move into an abstract review base
  without making the emitted critic home less direct to cold-read?
<!-- arch_skill:block:research_grounding:end -->

# 4) Current Architecture (as-is)

<!-- arch_skill:block:current_architecture:start -->
## 4.1 On-disk structure

The current Lessons family is a three-layer compiled doctrine system:

- authored prompt owners under `doctrine/prompts/lessons/**`
- emitted readback under `doctrine/build/lessons/agents/**`
- live runtime homes under `paperclip_home/agents/**`

The main shared authored surfaces are:

- `doctrine/prompts/lessons/common/role_home.prompt`
- `doctrine/prompts/lessons/common/skills.prompt`
- `doctrine/prompts/lessons/outputs/outputs.prompt`
- `doctrine/prompts/lessons/contracts/**`
- `doctrine/prompts/lessons/agents/**`

The current compile and sync path is:

- `Makefile` target `agents`
- `doctrine/Makefile` target `build`
- sync from `doctrine/build/<family>/agents/<role>/{AGENTS,SOUL}.md` into
  `paperclip_home/agents/<role>/`

## 4.2 Control paths (runtime)

Lessons runs as one same-issue serial workflow with critic interleaving between
producer lanes:

`LessonsProjectLead`
-> `SectionDossierEngineer`
-> `LessonsAcceptanceCritic`
-> `SectionConceptsTermsCurator`
-> `LessonsAcceptanceCritic`
-> `LessonsSectionArchitect`
-> `LessonsAcceptanceCritic`
-> `LessonsPlayableStrategist`
-> `LessonsAcceptanceCritic`
-> `LessonsLessonArchitect`
-> `LessonsAcceptanceCritic`
-> `LessonsSituationSynthesizer`
-> `LessonsAcceptanceCritic`
-> `LessonsPlayableMaterializer`
-> `LessonsAcceptanceCritic`
-> `LessonsCopywriter`
-> `LessonsAcceptanceCritic`
-> `LessonsMetadataCopywriter` when needed
-> `LessonsAcceptanceCritic`
-> `LessonsProjectLead`

Shared turn law lives in `role_home.prompt`, shared comment law lives in
`outputs.prompt`, and durable lane truth lives in the producer contracts.
Project Lead also owns route-only, process-repair, and publish/follow-up turns
where no specialist artifact is honestly current.

Late metadata already exposes the clearest split-owner seam in the family:

- readable current route state in comment metadata fields
- durable debt classification in the dossier
- durable structural input in the section lesson map

## 4.3 Object model + key abstractions

The important current abstractions are:

- shared role-home scaffolding
- shared skill definitions
- shared output contracts
- shared producer and review contracts
- role-local mission and lane boundaries

The largest abstraction gap is that several real state machines still exist
mainly as narrative convention:

- which artifact is current now
- when no artifact is current
- which route-only branch is active
- which metadata mode is active
- which upstream truths must stay preserved
- what old wording stops counting as rewrite evidence
- which downstream artifacts became invalid
- which exact review gate failed
- who owns next under accept, reject, or handoff-first block

The critic prompt is the sharpest example. It imports shared review contracts,
but it still carries nine local review families with repeated start-review,
verdict, and who-it-goes-back-to scaffolds.

## 4.4 Observability + failure behavior today

The most reliable current observability loop is:

1. edit the current prompt owner
2. run `make agents`
3. cold-read the emitted home
4. check whether the runtime readback stayed linear and explicit

There is no trusted automation layer for rendered-home quality. The current
repo doctrine explicitly treats cold-reading the emitted homes as the real
quality gate.

Current failure modes are:

- repeated prose that quietly re-owns shared law
- comment-carried state that is readable but not typed
- review or routing rules that can be paraphrased into weaker versions
- multi-file seams where the current owner split is real, but the comment-level
  state and durable owner state still have to be mentally reconstructed

Current evidence supports that diagnosis:

- `current file` appears `50` times across the current Lessons prompt family
- `At minimum confirm` appears `112` times across the same prompt family
- the critic prompt still repeats `Do not rewrite that producer truth here.`
  `9` times and `Who It Goes Back To` `9` times

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable for this doctrine port.
<!-- arch_skill:block:current_architecture:end -->

# 5) Target Architecture (to-be)

<!-- arch_skill:block:target_architecture:start -->
## 5.1 On-disk structure (future)

Keep the same authoring and emitted-home layout. Do not add a second Lessons
doctrine family or a sidecar workflow layer. The change is in what the current
owners encode, not in where the family lives.

The future family should still compile from `doctrine/prompts/lessons/**`,
still emit to `doctrine/build/lessons/agents/**`, and still sync to
`paperclip_home/agents/**`.

## 5.2 Control paths (future)

Keep the same runtime role graph and the same same-issue serial workflow, but
move the main semantic branches into compiler-owned surfaces:

- shared outputs carry typed currentness and trusted readback
- metadata carries typed mode, scope, and rewrite law
- Project Lead carries typed route-only law with honest `current none`
- critic carries first-class review law with explicit accept, reject, and block
  outcomes
- producer contracts carry typed preservation and invalidation where that
  meaning is currently only narrated

## 5.3 Object model + abstractions (future)

The target abstraction split is:

- prose for role mission, rationale, and judgment-heavy quality bars
- workflow law for route, stop, currentness, mode, preservation, and
  invalidation semantics
- review law for critic subject, contract, block behavior, failing gates,
  current truth, and next-owner coupling

The main concrete owner moves are:

- `doctrine/prompts/lessons/outputs/outputs.prompt`
  - richer trusted carriers for producer, route-only, and critic comments
  - guarded comment sections where conditional readback is real
- `doctrine/prompts/lessons/contracts/metadata_wording.prompt`
  - typed mode binding
  - one-current-file law
  - narrow owned scope
  - exact field preservation
  - rewrite-evidence exclusions
- `doctrine/prompts/lessons/agents/lessons_project_lead/AGENTS.prompt`
  - explicit route-only workflow law
  - explicit reroute coupling when no specialist owner is justified
- `doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt`
  - one abstract shared review base plus concrete per-artifact review patches,
    instead of repeated pseudo-review workflows or a second review framework
  - exact shared-contract gate export
  - review-owned current truth and next-owner routing
- `doctrine/prompts/lessons/contracts/**`
  - explicit preservation and invalidation for producer seams where upstream
    locks or downstream restarts are currently only narrated

Migration-only source-to-symbol mapping should stay outside runtime prompts. Use
this plan and the implementation worklog as the recoverability surface while
the port is in flight.

## 5.4 Invariants and boundaries

- one owner per seam
- one live route per seam
- one current artifact or honest `current none`
- no symbolic weakening of poker-quality constraints
- no new wrappers, fallback routes, or alternate doctrine systems
- emitted homes must stay direct and human-readable
- skill allowlists stay aligned with the prompt story
- deleted repeated prose must not leave a stale second owner behind

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable for this doctrine port.
<!-- arch_skill:block:target_architecture:end -->

# 6) Call-Site Audit (exhaustive change inventory)

<!-- arch_skill:block:call_site_audit:start -->
## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Shared output carriers | `doctrine/prompts/lessons/outputs/outputs.prompt` | `HandoffOutput` | Producer comments still narrate current file and proof location mostly by prose convention | Add explicit current-artifact and trusted-readback carrier model that later workflow law can target cleanly | All later phases depend on stronger shared carriers | workflow-law-compatible producer handoff carrier | `make agents`; cold-read producer canaries |
| Shared output carriers | `doctrine/prompts/lessons/outputs/outputs.prompt` | `RouteOnlyHandoffOutput` | Route-only comments still narrate no-current-artifact truth, conditional metadata readback, and routed next owner | Add guarded route-only readback and explicit no-current-artifact carrier shape | Needed before Project Lead route-only law can simplify honestly | workflow-law-compatible route-only carrier | `make agents`; cold-read project lead canary |
| Shared output carriers | `doctrine/prompts/lessons/outputs/outputs.prompt` | `CriticVerdictAndHandoffOutput` | Critic comments still narrate current truth, blocked-gate state, and exact failing-gate payloads | Add review-compatible carrier fields and trust surface | Needed before critic can move to first-class review | review-compatible critic carrier | `make agents`; cold-read critic canary |
| Shared role-home coupling | `doctrine/prompts/lessons/common/role_home.prompt` | `HowToTakeATurn`, `EndingYourTurn`, `current_truth_rules` | Shared handoff language assumes comment fields that are still weaker than the semantics they describe | Tighten only the wording that should point at the stronger output carriers once they exist | Avoid leaving duplicated handoff law behind | shared carrier-aware turn law | `make agents`; cold-read representative homes |
| Metadata pilot | `doctrine/prompts/lessons/contracts/metadata_wording.prompt` | `MetadataWordingWorkflow` | Mode, one-current-file law, narrow scope, and rewrite exclusions are prose-heavy | Port to typed mode, scope, preservation, support-only comparison, rewrite exclusions, and invalidation where the shipped language fits | Best narrow proving seam | workflow law + metadata review alignment | `make agents`; cold-read metadata writer and critic homes |
| Metadata pilot | `doctrine/prompts/lessons/contracts/metadata_wording.prompt` | `MetadataWordingReviewContract` | Review still depends on narrated metadata mode and handoff-state reading | Align metadata review with typed mode/currentness model | Keep producer and critic semantics coupled | review-compatible metadata contract | `make agents`; cold-read metadata writer and critic homes |
| Metadata local delta | `doctrine/prompts/lessons/agents/lessons_metadata_copywriter/AGENTS.prompt` | local mode and current-file instructions | Local prompt repeats shared metadata law because the shared carrier is weak | Trim to mission, stop lines, and real local delta after the shared model lands | Prevent local drift | mission-only local metadata delta | `make agents`; cold-read emitted home |
| Route-only turns | `doctrine/prompts/lessons/agents/lessons_project_lead/AGENTS.prompt` | `RouteOnlyTurns` | Route-only activation, rewrite-aware route state, and repeated-problem handling are narrative | Port to explicit route-only workflow law, `current none`, guarded readback, and route coupling | Remove coordination drift without changing route graph | route-only workflow law | `make agents`; cold-read project lead canary |
| Critic review | `doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt` | repeated review families and routing | Verdict rules, blocked review, failing gates, and next-owner routing repeat across nine local families | Migrate to first-class review with exact failing-gate export, blocked-gate binding, current truth, and routed next-owner state | Biggest remaining prose bucket | review surfaces plus inherited review scaffolding | `make agents`; cold-read critic canary |
| Producer preservation | `doctrine/prompts/lessons/contracts/section_architecture.prompt` | `late_metadata_handoff`, `downstream_invalidation` | Typed mode plus typed restart export now exist, but the actual late-metadata section content is still prose-owned | Keep the state typed while deciding whether the remaining section content should stay as the honest prose owner or move into a stronger carrier later | Highest-value producer seam after metadata | typed mode plus typed restart export, then optional late-metadata carrier tightening | `make agents`; cold-read section architect and critic homes |
| Producer preservation | `doctrine/prompts/lessons/contracts/section_concepts_terms.prompt` | ontology, term-surface, and dependency-order preservation | Typed currentness plus preserved dossier truth, preserved term-surface structure, and a typed blocked stop-line now exist, but dependency-order ownership still stays in prose | Finish the remaining dependency-order seam where shipped law can own it honestly | Reduce drift in the early producer chain without reopening term truth | typed currentness + preserved dossier truth + preserved term-surface structure + typed blocked stop-line, then dependency-order ownership | `make agents`; cold-read curator and critic homes |
| Producer preservation | `doctrine/prompts/lessons/contracts/lesson_plan.prompt` | route inheritance and preserved upstream scope | Typed currentness plus preserved section-map and playable-strategy truth and structure now exist, and downstream rebuild-boundary ownership now exports through a typed invalidation target | Keep the rebuild boundary compiler-owned while preserving upstream route truth | Protect downstream route fidelity | typed preservation of upstream decisions and structure plus typed rebuild-boundary owner | `make agents`; cold-read lesson architect and critic homes |
| Producer preservation | `doctrine/prompts/lessons/contracts/materialization.prompt` | title out-of-scope, upstream truth, and downstream rebuild seams | Typed currentness plus preserved lesson-plan and lesson-situations truth and structure now exist, and downstream copy-or-metadata invalidation now exports through a typed invalidation target | Keep late-chain manifest truth from drifting while preserving honest restart behavior | typed currentness + preserved upstream truth and structure + exact title preservation + typed invalidation | `make agents`; cold-read materializer and critic homes |
| Runtime/readback sync | `paperclip_home/agents/**`, `paperclip_home/agents/agent_configs.json` | emitted homes and skill allowlists | Runtime truth can drift from prompt changes if sync and cold read are skipped | Recompile and sync after each source phase | Runtime truth must match source truth | synced runtime readback | cold-read only |
| Stale truth surfaces | touched docs under `docs/**` | current Lessons claims | Old docs can keep false live stories alive after the port moves a seam | Rewrite or delete touched stale docs in the same phase | Prevent split truth | current-state docs only | cold-read only |

## 6.2 Migration notes

Canonical owner path / shared code path:

- authored owners stay under `doctrine/prompts/lessons/**`
- emitted readback stays under `doctrine/build/lessons/agents/**`
- live runtime proof stays under `paperclip_home/agents/**`

Deprecated APIs (if any):

- none expected at the product-runtime level; this is a doctrine-language port,
  not a runtime API migration

Delete list (what must be removed; include superseded shims/parallel paths if any):

- repeated local route-only prose once workflow law owns that seam
- repeated local critic start-review, verdict, and who-it-goes-back-to prose
  once first-class review owns those mechanics
- duplicated local metadata state prose once typed mode/currentness law owns it
- any touched stale current-state docs that would preserve the pre-port story

Capability-replacing harnesses to delete or justify:

- none should be added
- if a temporary mini-framework, helper script, or extra doctrine layer gets
  proposed to simulate shipped workflow-law or review features, reject it unless
  the plan explicitly justifies why the shipped language cannot preserve the
  seam yet

Live docs/comments/instructions to update or delete:

- `paperclip_home/agents/agent_configs.json` if a touched role's skill story
  narrows or changes
- touched repo docs under `docs/**` that would otherwise keep a stale current
  Lessons story alive

Behavior-preservation signals for refactors:

- `make agents`
- cold-read emitted canary homes for project lead, metadata copywriter, and
  critic
- source-to-output comparison on the seams that moved from prose to symbolic
  law

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| --- | --- | --- | --- | --- |
| Shared carriers | `doctrine/prompts/lessons/outputs/outputs.prompt` | trust-surface-backed currentness and guarded readback | one shared carrier model is better than role-local comment lore | include |
| Metadata seam | `doctrine/prompts/lessons/contracts/metadata_wording.prompt` | typed mode + narrow scope + rewrite exclusions | best proving seam for symbolic preservation without product drift | include |
| Route-only seam | `doctrine/prompts/lessons/agents/lessons_project_lead/AGENTS.prompt` | route-only workflow law with `current none` | prevents route-only semantics from drifting between comments and role prose | include |
| Critic seam | `doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt` | first-class review plus inherited review scaffolding | removes repeated pseudo-review mechanics while keeping one critic owner | include |
| Producer chain | `doctrine/prompts/lessons/contracts/**` | typed preservation and invalidation | makes upstream locks and downstream restart boundaries explicit | defer until metadata and critic patterns are proven |
| Runtime docs | touched `docs/**` | current-state-only live story | avoids split truth after each phase | include when a touched doc would otherwise go stale |
<!-- arch_skill:block:call_site_audit:end -->

# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

<!-- arch_skill:block:phase_plan:start -->
## Phase 1 - Strengthen shared output carriers

Status: COMPLETE
Completed work:
- Added explicit `Current Artifact` trust carriers to shared producer and critic comment outputs in `doctrine/prompts/lessons/outputs/outputs.prompt`.
- Tightened shared handoff guidance in `doctrine/prompts/lessons/common/role_home.prompt` so `Current Artifact` carries portable current truth and `What To Use Now` stays the readable pickup summary.
- Recompiled with `make agents` and cold-read the project lead, metadata copywriter, and critic canaries under `doctrine/build/lessons/agents/**` and `paperclip_home/agents/**`.
Deferred:
- Truly guarded shared output sections still need branch-local facts that only the later route-only and review ports can legally provide, so that work stays with Phases 3 and 4 instead of being faked early.

Goal

Make shared output contracts strong enough to carry current artifact truth,
trusted readback, blocked-gate state, and routed ownership without hidden
schema living in prose.

Work

- tighten `doctrine/prompts/lessons/outputs/outputs.prompt`, especially
  `MetadataHandoffState`, `HandoffOutput`, `RouteOnlyHandoffOutput`, and
  `CriticVerdictAndHandoffOutput`
- add the smallest matching cleanup in
  `doctrine/prompts/lessons/common/role_home.prompt` if shared workflow law
  still depends on old carrier assumptions
- define how guarded output sections and trusted readback should work across
  producer, route-only, and critic comments
- record a source-to-symbol mapping for each moved carrier so the replaced
  meaning stays recoverable during the port

Verification (smallest signal)

- run `make agents`
- cold-read emitted canaries for `lessons_project_lead`,
  `lessons_metadata_copywriter`, and `lessons_acceptance_critic`
- confirm currentness, blocked-gate state, and next-owner state are at least as
  explicit as before

Docs/comments (propagation; only if needed)

- update touched docs only if a current Lessons note would otherwise describe
  the old carrier shape as still live

Exit criteria

- shared outputs can support typed currentness and trusted readback without
  inventing local duplicate law

Rollback

- revert the shared-output change set if emitted homes become less explicit or
  lose material handoff meaning

## Phase 2 - Prove the model on metadata

Status: COMPLETE
Completed work:
- Reopened this phase after verifying the earlier blocked-state note was stale. The checked-in Lessons source had not actually landed the metadata workflow-law port.
- Re-grounded the phase against `../doctrine/examples/50_bound_currentness_roots/prompts/AGENTS.prompt`, `../doctrine/examples/51_inherited_bound_io_roots/prompts/AGENTS.prompt`, `../doctrine/examples/52_bound_scope_and_preservation/prompts/AGENTS.prompt`, and `../doctrine/examples/53_review_bound_carrier_roots/prompts/AGENTS.prompt`, which now prove bound currentness, scope, preservation, and review carriers through concrete-turn bindings.
- Added `MetadataRouteFacts` and `MetadataRewriteRegime` in `doctrine/prompts/lessons/contracts/metadata_wording.prompt`, then moved mode selection, current-file truth, narrow scope, exact preservation, preserve-basis checks, rewrite exclusions, and fail-loud route-upstream handling into workflow law there.
- Flattened the metadata writer's concrete input and output bindings in `doctrine/prompts/lessons/agents/lessons_metadata_copywriter/AGENTS.prompt` so the workflow-law roots resolve through direct concrete-turn bindings instead of nested buckets.
- Aligned `doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt` and the shared metadata review contract with the same typed metadata route state.
- Recompiled with `make agents` and cold-read the metadata writer and critic canaries under `doctrine/build/lessons/agents/**` and `paperclip_home/agents/**`.

Goal

Use metadata as the narrow proving seam for typed mode state, one-current-file
law, narrow scope, exact preservation, and rewrite-evidence exclusions.

Work

- port `doctrine/prompts/lessons/contracts/metadata_wording.prompt` onto
  shipped workflow-law features that match the current behavior
- port the paired metadata review contract in the same file so the critic and
  producer read the same typed mode/currentness story
- update
  `doctrine/prompts/lessons/agents/lessons_metadata_copywriter/AGENTS.prompt`
  only where shared law now owns the seam
- keep the metadata pass grounded in current lesson and section truth rather
  than inferred naming taste
- preserve the split owner model where the dossier owns whether section
  metadata is still owed and the section lesson map owns the locked structural
  input for that later pass
- preserve every hard negative and route-upstream stop line that currently
  protects this seam

Verification (smallest signal)

- run `make agents`
- cold-read the metadata writer and critic emitted homes
- confirm the emitted readback still makes mode, current file, preserved
  fields, and rewrite-state boundaries explicit

Docs/comments (propagation; only if needed)

- update touched docs if they would otherwise describe old metadata-state
  handling as still live

Exit criteria

- metadata mode, current file, rewrite exclusions, and preserved scope are no
  longer carried mainly by prose conventions

Rollback

- revert the metadata phase if the emitted home becomes more abstract or loses
  concrete safeguards around rewrite and scope

## Phase 3 - Formalize Lessons Project Lead route-only turns

Status: COMPLETE
Completed work:
- Added `ProjectLeadRouteOnlyNextOwner` and `RouteOnlyTurnFacts` in `doctrine/prompts/lessons/agents/lessons_project_lead/AGENTS.prompt` so the active route-only job and justified next owner are explicit input state instead of comment-only prose.
- Replaced the old narrative route-only coordination seam with `RouteOnlyTurns` workflow law that now owns activation, `current none`, and next-owner routing.
- Kept route-only turns on the same issue and in the same role graph without inventing a fake specialist artifact.
- Recompiled with `make agents` and cold-read the project-lead canaries under `doctrine/build/lessons/agents/**` and `paperclip_home/agents/**`.

Goal

Replace narrative route-only logic with explicit workflow law while preserving
the same route judgment and no-current-artifact honesty.

Work

- port route-only behavior in
  `doctrine/prompts/lessons/agents/lessons_project_lead/AGENTS.prompt`
- use the strengthened shared outputs instead of local coordination prose
- make `current none`, route-only activation, and next-owner coupling explicit
- preserve repeated-problem, publish-state, and metadata-route nuances that are
  currently expressed in route-only comments
- keep route-only turns inside the same current role and issue graph rather
  than inventing a side workflow or specialist placeholder artifact

Verification (smallest signal)

- run `make agents`
- cold-read the project lead emitted home and confirm route-only turns are more
  explicit without adding new route choices

Docs/comments (propagation; only if needed)

- sync touched docs that would otherwise keep the old route-only story alive

Exit criteria

- route-only turns are typed and cold-readable, with no invented specialist
  artifact and no weaker route judgment

Rollback

- revert if the route-only port forces extra instructions or hides current
  status that used to be visible

## Phase 4 - Migrate Lessons Acceptance Critic to first-class review

Status: PARTIAL
Completed work:
- Replaced the old repeated local review scaffolds with `BaseLessonsArtifactReview` plus concrete `LessonsCriticReview` in `doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt`.
- Bound the critic onto a real `review:` surface with typed subject mapping, shared contract roots, blocked-review handling, current-artifact output, and explicit accept/reject routing.
- Wired the shared critic outputs through `CriticVerdictAndHandoffOutput` so current artifact, blocked-gate state, next owner, active mode, and trigger reason travel through the output carrier instead of staying only in prose.
- Recompiled with `make agents` after the critic cutover and cold-read the rendered review surface in the emitted build and runtime homes.
- Cold-read the emitted critic homes under `doctrine/build/lessons/agents/**` and `paperclip_home/agents/**`.
Remaining gap:
- The exact shared-contract gate that failed is not yet exported per mode. The current landing still uses `ReviewState.selected_review_basis_failed` and `ReviewState.scope_boundary_failed` as the mode-specific failure surface.
- A direct attempt to switch those rejects to exact per-mode `contract.<gate>` lines still triggered Doctrine compiler recursion and was backed out.

Goal

Replace the critic's repeated prose scaffolds with first-class review while
preserving exact verdict behavior, failing-gate identities, blocked-review
stops, and next-owner routing.

Work

- port `doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt`
  onto shipped review features
- build one abstract shared review base plus concrete per-artifact review
  patches instead of rewriting nine local pseudo-workflows again
- keep shared review-contract content in the current contract owners rather
  than re-owning it locally
- make subject, contract, block behavior, exact failing gates, current truth,
  and accept/reject routing explicit
- preserve critic posture that should remain prose, especially independence,
  handoff-first stops, and do-not-rewrite boundaries

Verification (smallest signal)

- run `make agents`
- cold-read the critic emitted home
- confirm that exact gate export, blocked review, and next-owner behavior are
  clearer and not less specific than before

Docs/comments (propagation; only if needed)

- update touched docs that explain current critic behavior if they would become
  stale after the rewrite

Exit criteria

- the critic no longer depends on repeated Start Review / Verdict Rules prose
  to express exact review behavior

Rollback

- revert if exact failing-gate identity, blocked-review behavior, or next-owner
  routing becomes less precise

## Phase 5 - Sweep preservation, invalidation, and law reuse across producer contracts

Status: PARTIAL
Completed work:
- Added `Invalidations` to `HandoffOutput` in `doctrine/prompts/lessons/outputs/outputs.prompt` so producer comments now have a shared trusted carrier for downstream restart state when typed workflow law can export it.
- Tightened `doctrine/prompts/lessons/common/role_home.prompt` so shared turn-close guidance names that `Invalidations` carrier instead of leaving future producer restart export as comment folklore.
- Added `SectionArchitectureMetadataState`, `SectionArchitectureTurnFacts`, and `DownstreamSectionPlanningAndRealizationWork` in `doctrine/prompts/lessons/contracts/section_architecture.prompt`.
- Expanded `SectionArchitectureWorkflow` so the section-architecture lane now owns one typed current section lesson map across an explicit `ordinary` versus `late-metadata-owed` mode split, preserves upstream dossier and locked-concepts decisions plus locked-concepts structure, and exports downstream restart state through a typed invalidation target.
- Wired `LessonsSectionArchitect` onto that new workflow and gave the current section lesson map a direct concrete binding in `doctrine/prompts/lessons/agents/lessons_section_architect/AGENTS.prompt`.
- Added `SectionConceptsTermsWorkflow` in `doctrine/prompts/lessons/contracts/section_concepts_terms.prompt` so the curator lane now owns one typed current concepts-and-terms file, explicitly preserves the approved dossier, structurally preserves the current term files, and owns a typed blocked stop-line back to `LessonsProjectLead`.
- Wired `SectionConceptsTermsCurator` onto that new workflow and gave the current concepts-and-terms file a direct concrete binding in `doctrine/prompts/lessons/agents/section_concepts_terms_curator/AGENTS.prompt`.
- Added `LessonPlanTurnFacts` and `DownstreamLessonBuildWork` in `doctrine/prompts/lessons/contracts/lesson_plan.prompt`.
- Added `LessonPlanWorkflow` in `doctrine/prompts/lessons/contracts/lesson_plan.prompt` so the lesson-plan lane now owns one typed current lesson plan, explicitly preserves the approved section map, the approved section-map structure, locked section concepts, the approved section playable strategy, and the approved playable-strategy structure, and exports downstream rebuild state through a typed invalidation target.
- Wired `LessonsLessonArchitect` onto that new workflow, flattened the lesson-plan inputs so the preserved roots are direct, and gave the current lesson plan a direct concrete binding in `doctrine/prompts/lessons/agents/lessons_lesson_architect/AGENTS.prompt`.
- Added `MaterializationTurnFacts` and `DownstreamCopyAndMetadataWork` in `doctrine/prompts/lessons/contracts/materialization.prompt`.
- Added workflow law to `MaterializationWorkflow` in `doctrine/prompts/lessons/contracts/materialization.prompt` so the materialization lane now owns one typed current lesson manifest, explicitly preserves approved lesson-plan truth and structure, explicitly preserves approved lesson-situations truth and structure, keeps top-level `title` under exact preservation, and exports downstream copy-or-metadata restart state through a typed invalidation target.
- Wired `LessonsPlayableMaterializer` onto that stronger workflow by giving the manifest a direct concrete output binding and flattening the lesson-plan and lesson-situations inputs so the preserved roots are direct in `doctrine/prompts/lessons/agents/lessons_playable_materializer/AGENTS.prompt`.
- Recompiled with `make agents` and cold-read the section-architect canaries under `doctrine/build/lessons/agents/**` and `paperclip_home/agents/**`.
- Recompiled with `make agents` and cold-read the curator canaries under `doctrine/build/lessons/agents/**` and `paperclip_home/agents/**`.
- Recompiled with `make agents` and cold-read the lesson-architect canaries under `doctrine/build/lessons/agents/**` and `paperclip_home/agents/**`.
- Recompiled with `make agents` and cold-read the materializer canaries under `doctrine/build/lessons/agents/**` and `paperclip_home/agents/**`.
Remaining gap:
- `section_concepts_terms.prompt` now preserves dossier truth plus current term-file structure and owns a typed blocked stop-line, but it does not yet carry typed dependency-order ownership beyond that boundary.

Goal

Turn preserved upstream truths and rebuild boundaries into explicit language
features across the remaining producer chain without widening product behavior.

Work

- port preservation and invalidation seams across the producer contracts in
  `doctrine/prompts/lessons/contracts/**`, starting with
  `section_architecture.prompt`, then `section_concepts_terms.prompt`,
  `lesson_plan.prompt`, `materialization.prompt`, and any other contract that
  still carries real preserved upstream truth mainly by prose
- use the smallest honest owner for each preserved decision, structure,
  mapping, vocabulary, or invalidation rule
- remove competing duplicated prose once the symbolic owner is proven
- keep judgment-heavy copy or grounding guidance in prose when symbolic law is
  not the right owner

Verification (smallest signal)

- run `make agents`
- cold-read the affected producer and critic emitted homes
- confirm upstream locks and rebuild rules are more explicit and not weaker

Docs/comments (propagation; only if needed)

- rewrite or delete touched repo docs that would otherwise preserve stale live
  behavior claims

Exit criteria

- the remaining shared semantic seams are carried by one honest owner and the
  family has materially less repeated hidden schema

Rollback

- revert any local port that weakens preserved upstream truth or creates a
  second owner story

## Phase 6 - Final compile, cold-read, and truth-surface cleanup

Goal

Leave the Lessons family in a state where source owners, emitted homes, runtime
homes, and touched docs all tell the same current story.

Work

- run a final `make agents`
- cold-read all affected emitted homes in `doctrine/build/lessons/agents/**`
- verify the synced runtime homes under `paperclip_home/agents/**`
- verify `paperclip_home/agents/agent_configs.json` still matches the skill
  story
- retire temporary source-to-symbol mapping notes once the replacement owner is
  stable and no longer needs migration help
- remove or update touched stale docs that would otherwise keep dead doctrine
  alive

Verification (smallest signal)

- compile succeeds
- final cold reads stay linear and preserve nuance
- no touched current-state doc contradicts the new doctrine

Docs/comments (propagation; only if needed)

- update only the docs whose live claims actually changed

Exit criteria

- the ported family is internally consistent and ready for later implementation
  work without a competing live story

Rollback

- revert only the affected final sync or doc cleanup if it introduces a stale
  mismatch instead of removing one
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

There are no meaningful code-level unit tests for this plan artifact itself.
The cheapest truthful contract check is to compile the doctrine with
`make agents` and then inspect the emitted readback for the exact semantics the
phase claimed to move.

## 8.2 Integration tests (flows)

The main integration check is a side-by-side cold read:

1. current prompt owner before the change
2. changed prompt owner after the change
3. emitted home under `doctrine/build/lessons/agents/**`
4. synced runtime home under `paperclip_home/agents/**`

For each migrated seam, verify that the symbolic form preserved:

- current artifact truth
- route or verdict behavior
- preserved scope and preserved upstream locks
- exact failing-gate or stop-line meaning
- explicit next-owner logic

## 8.3 E2E / device tests (realistic)

No UI or device flow is in scope. The closest realistic end-to-end check is a
targeted cold read of representative emitted homes after each phase, with the
critic and the role most affected by that phase treated as the canary surfaces.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

Roll out one doctrine seam family at a time in the phase order above. Do not
batch the whole port into one unreadable diff. Compile and cold-read after each
phase before starting the next one.

## 9.2 Telemetry changes

No runtime telemetry changes are expected. The operational signal is emitted
home quality and runtime-home alignment, not product metrics.

## 9.3 Operational runbook

For each source phase:

1. edit the smallest honest current owner
2. run `make agents`
3. cold-read the affected emitted homes
4. check the synced runtime homes
5. update or delete touched stale docs if needed
6. only then move to the next phase

# 10) Decision Log (append-only)

## 2026-04-10 - Preserve meaning before symbolic uniformity

Context

The user asked for a full north-star plan to move the Lessons family onto the
new Doctrine language features without turning the port into compression,
simplification, or guesswork around poker-quality rules.

Options

- treat the work as a prose cleanup and try to make the family shorter
- force every seam into symbolic form whether or not the language is ready
- treat the work as a structure-preserving symbolic port that uses shipped
  language where it is stronger and keeps prose where that is still the honest
  owner

Decision

Treat this as a structure-preserving symbolic port. Shipped Doctrine workflow
law and review features are now the target owners for semantic seams that are
currently carried by prose, but only where they preserve the full operational
meaning.

Consequences

- the migration order must be carriers first, then pilot seam, then route-only,
  then critic, then the wider preservation sweep
- cold-reading emitted homes becomes the main loss-detection method
- some prose may stay in place when symbolic form would weaken current meaning

Follow-ups

- confirm this North Star before deeper `arch-step` work
- use later `arch-step` passes to harden research grounding, architecture, and
  any phase details that still need stronger evidence

## 2026-04-10 - Keep recoverability outside runtime prompts

Context

The port needs a way to keep replaced source meaning recoverable while semantic
seams move from prose to symbolic Doctrine features.

Options

- leave the recoverability story implicit and trust git plus reviewer memory
- put migration commentary and source-to-symbol mapping inside runtime prompts
- keep recoverability in the planning and implementation artifacts while runtime
  prompts stay current-state only

Decision

Keep recoverability in this plan and the implementation worklog, not in runtime
prompts or emitted homes.

Consequences

- runtime prompts stay current-state only
- the implementation needs a short source-to-symbol mapping note for each moved
  seam while the port is in flight
- cold-read quality stays focused on the runtime brief rather than on migration
  archaeology

Follow-ups

## 2026-04-11 - Reset execution truth to the authored source and newer Doctrine examples

Context

The plan had drifted from the repo. It claimed Phase 1 was already complete and
Phase 2 was blocked by compiler limits from an earlier attempt. Cold-reading
the real Lessons source showed the shared carrier port had not actually landed
there yet, and the apparent progress came from stale generated readback rather
than current authored truth. Since that note was written, Doctrine also gained
the bound-root examples `50` through `53`, which directly cover the old
currentness, scope, preservation, and review-carrier concern.

Options

- keep the stale blocked-state note and leave metadata ownership in prose
- treat the stale generated readback as close enough and continue from a false
  phase state
- reset the execution story to the current authored source, land the shared
  carrier phase for real, and continue Phase 2 against the newer bound-root
  examples

Decision

Reset the plan to the current authored source. Treat the shared-carrier work as
the first real landed phase in this run, and continue the metadata port against
the newer bound-root Doctrine patterns instead of preserving the stale blocker
story.

Consequences

- Section 7 phase state now matches the real source tree instead of stale local
  generated readback
- Phase 2 is no longer honestly described as blocked before we try the
  bound-root model on the current metadata seam
- the worklog must carry the source-to-symbol recovery notes for this cutover

Follow-ups

- implement the metadata workflow-law port against concrete-turn bound roots
- rerun `make agents` and cold-read the metadata writer and critic canaries

## 2026-04-11 - Keep metadata bound-root repair local to the metadata seam

Context

The newer Doctrine examples proved the metadata seam was no longer blocked by
the older compiler limitation in principle, but the current Lessons metadata
writer still bound the relevant file inputs and outputs through nested local
grouping that the workflow-law roots did not resolve through directly.

Options

- keep the old blocked-state claim and leave the seam in prose
- widen shared Lessons owners so every producer carries metadata-style direct
  roots whether it needs them or not
- flatten only the metadata writer's concrete bindings so the workflow-law
  roots become direct on the one seam that needs them now

Decision

Keep the repair local. Add the typed metadata route input and flatten the
metadata writer's concrete input and output bindings so the bound workflow-law
roots resolve directly on that seam without widening shared Lessons owners.

Consequences

- Phase 2 can land honestly on the current shipped Doctrine compiler
- shared Lessons carriers stay limited to the cross-family `Current Artifact`
  port from Phase 1
- later phases can reuse the same local direct-root pattern when a seam really
  needs it instead of bloating the whole family early

Follow-ups

- use the same direct-root discipline if the critic review port needs carried
  metadata state in Phase 4
- Phase 3 route-only law has now landed in the project-lead owner, so the next
  follow-up is the remaining exact-gate gap in Phase 4 rather than route-only
  unblock work

- add the smallest useful per-seam mapping note during implementation
- delete those temporary mapping notes once the port is complete and the new
  owners are stable

## 2026-04-11 - Resume critic review after the Doctrine compiler speedup

Context

The first critic `review:` attempt had already converged structurally, but it
was expensive enough on the older local Doctrine build that the practical stop
point looked like a tool problem rather than a doctrine problem. After the
user's Doctrine changes, the critic target compiled quickly enough to continue
the port honestly.

Options

- keep the critic on the older workflow-only shape until the compiler story is
  perfect
- finish the first-class review cutover now and accept a narrower remaining
  gap if exact gate export still needs another pass
- revert the review cutover and wait for a later wider Doctrine change

Decision

Finish the first-class review cutover now. Keep the real `review:` owner,
shared base review, current-artifact carrier, and routed accept/reject logic.
Treat exact per-mode failing-gate export as the remaining Phase 4 gap instead
of pretending the whole critic migration is still unstarted.

Consequences

- Phase 3 route-only law is no longer the blocker
- the critic now renders through compiler-owned review structure instead of the
  older repeated pseudo-review families
- the plan and worklog must describe Phase 4 as partially landed, not absent

Follow-ups

- decide whether the current simplified mode-specific failure booleans are good
  enough or whether the port must keep going until exact per-mode gate export
  is explicit
- if the richer gate export matters, tighten the review surface without
  regressing compile speed or emitted-home clarity
