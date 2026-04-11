---
title: "Doctrine Phase 4 - Review Route Only Grounding And Control Plane Integration"
status: active
doc_type: phased_plan
phase: 4
---

# Phase 4 - Review Route Only Grounding And Control Plane Integration

## Summary

Phase 4 integrates the semantic declaration work from earlier phases with
Doctrine's control-plane surfaces. It makes schema-backed review contracts
first-class, introduces a dedicated reusable review-family surface, adds
dedicated `route_only` and `grounding` declaration families, and converges
currentness, trust surfaces, preservation, invalidation, and compact comment
rendering into one coherent control-plane layer.

The purpose of this phase is not to replace workflow law or review, but to make
the repeated control-plane seams explicit where earlier drafts identified them
as structurally stable across many lanes.

## Assumed Shipped Baseline

This phase assumes phases 1 through 3 are available:

- typed markdown is the shared readable architecture
- `document`, `analysis`, and `schema` already exist
- owner-aware `schema:` resolution is stable
- schema `gates:` exist
- render profiles, `properties`, and explicit guard shells exist

## Phase Boundary

This phase owns:

- schema-backed `review contract:` integration
- `review_family`
- `route_only`
- `grounding`
- control-plane integration with preservation, invalidation, `support_only`,
  `ignore rewrite_evidence`, and `trust_surface`
- compact currentness and handoff rendering for review and route-only comments

## Schema-Backed Review Contracts

### Purpose

Reviews should be able to point at either a workflow contract or a schema
contract without changing review verdict mechanics.

### Contract rule

```prompt
review LessonPlanReview: "Lesson Plan Review"
    subject: LessonPlanFile
    contract: LessonPlanSchema
    comment_output: CriticVerdictAndHandoffOutput
```

Rules:

- `review contract:` may resolve to either a `workflow` or a `schema`
- workflow contracts export first-level keyed sections as gate identities
- schema contracts export named `gates:` items as gate identities
- `contract.some_gate` resolves against workflow section keys or schema gate
  keys depending on contract kind
- `contract.passes` remains valid for both kinds

### Render intent

```markdown
## Lesson Plan Review

Review subject: Lesson Plan File.
Shared review contract: Lesson Plan Schema.

### Contract Gate Checks

Reject: Explicit Step Roles.
Reject: No New Route.
Accept only if the shared lesson-plan contract passes.
```

## `review_family`

### Purpose

`review_family` centralizes recurring critic scaffolds such as handoff-first
blocking, failing-gate export, current-artifact carriage, and next-owner
routing.

### Surface syntax

```prompt
review_family ProducerArtifactReview: "Producer Artifact Review"
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        verdict: verdict
        reviewed_artifact: what_you_reviewed
        analysis: analysis_performed
        readback: output_contents_that_matter
        current_artifact: current_artifact
        failing_gates: failure_detail.failing_gates
        blocked_gate: failure_detail.blocked_gate
        next_owner: next_owner

    handoff_first:
        block "The producer handoff is incomplete." when producer_handoff.incomplete
        reject "The producer handoff names the wrong current artifact." when producer_handoff.names_wrong_current_artifact
```

Concrete review:

```prompt
review LessonPlanReview[ProducerArtifactReview]: "Lesson Plan Review"
    subject: LessonPlanFile
    contract: LessonPlanSchema

    contract_checks:
        reject contract.explicit_step_roles when lesson_plan.step_roles_implicit
        reject contract.no_new_route when lesson_plan.invented_route
        accept "The shared lesson-plan contract passes." when contract.passes
```

### Rules

- `review_family` is a first-class reusable declaration family
- concrete `review` declarations may inherit from a `review_family`
- family fields, handoff-first blocks, and comment output semantics are
  inherited explicitly
- concrete reviews still own artifact-specific subjects, contracts, verdict
  routing, and local prose

## `route_only`

### Purpose

`route_only` formalizes turns where no specialist artifact is current, the live
job is routing/process repair/owner repair, and the main output is a compact
routing handoff rather than a specialist artifact revision.

### Surface syntax

```prompt
route_only ProjectLeadRouteRepair: "Routing-Only Turns"
    facts: route_only_turn_facts

    when:
        live_job in {"routing", "process_repair", "owner_repair"}
        current_specialist_output_missing

    current none

    handoff_output: RouteOnlyHandoffOutput

    guarded:
        repeated_problem when critic_miss_repeated
        rewrite_mode when section_status in {"new", "full_rewrite"}

    routes:
        section_dossier_engineer -> SectionDossierEngineer
        lessons_section_architect -> LessonsSectionArchitect
        lessons_playable_strategist -> LessonsPlayableStrategist
        lessons_lesson_architect -> LessonsLessonArchitect
        else -> LessonsProjectLead
```

### Rules

- `route_only` owns activation, `current none`, handoff output choice, and
  next-owner routing for routing-only turns
- route-only comments reuse phase-3 typed markdown, `properties`, guard shells,
  and comment profiles
- `route_only` remains explicit about there being no current specialist
  artifact for the turn

## `grounding`

### Purpose

`grounding` captures wording-safe or evidence-safe behavior that earlier prompts
held only in repeated prose.

### Surface syntax

```prompt
grounding WordingGrounding: "Wording Grounding"
    source: poker_kb_interface
    target: wording

    policy:
        start_from current_wording unless rewrite
        forbid draft_first
        allow one_narrower_followup
        if unresolved -> route LessonsProjectLead
```

### Rules

- `grounding` owns protocol shape, not domain truth
- domain packs still choose the knowledge source and receipt quality
- grounding routes unresolved states explicitly instead of silently freewriting

## Control-Plane Integration Rules

The following surfaces remain first-class control-plane law in phase 4 and must
interoperate with the new declarations rather than being reimplemented beside
them:

- `preserve`
- `invalidate`
- `support_only`
- `ignore rewrite_evidence`
- current artifact via `trust_surface`

Integration rules:

- `analysis` does not replace preservation or invalidation
- `schema` does not replace current-truth carriage
- `review_family`, `review`, and `route_only` comments carry current truth
  through typed fields and trusted outputs
- render profiles and typed markdown only change readability; they do not own
  the underlying currentness semantics

## Currentness, Carriage, And Readback

Phase 4 adopts compact typed-markdown readbacks for review and route-only
outputs.

Example route-only handoff shape:

```prompt
document RouteOnlyHandoff: "Routing Handoff Comment"
    properties must_include: "Must Include"
        current_route: "Current Route"
        next_owner: "Next Owner"
        next_step: "Next Step"

    guard rewrite_mode when RouteFacts.section_status in {"new", "full_rewrite"}
        callout rewrite_mode: "Rewrite Mode"
            kind: note
            "Later section metadata must be rewritten instead of inherited."

    guard repeated_problem when RouteFacts.critic_miss_repeated
        section repeated_problem: "Repeated Problem"
            properties:
                failing_pattern: "What Keeps Failing"
                returned_from: "Returned From"
                next_fix: "Next Concrete Fix"
```

## Name Resolution And Inheritance

Phase-4 resolution rules:

- `review contract:` resolves to `workflow` or `schema`
- `review` may inherit from a `review_family`
- `route_only` routes resolve to agent targets
- `grounding` route targets resolve to agents
- control-plane readable outputs resolve document/profile refs through the
  phase-1 and phase-3 systems

Inheritance rules:

- `review_family` supports explicit keyed inheritance and override accounting
- later concrete `review` declarations must account for inherited family
  sections, fields, and contract-check surfaces explicitly
- `route_only` and `grounding` reuse Doctrine's explicit-accounting style for
  any inherited keyed subsections they gain

## Diagnostics And Invariants

Phase-4 fail-loud rules:

- unknown schema gate in `contract.some_gate`
- schema contract with no exported gates when used by review
- unknown `review_family` target
- unresolved `route_only` handoff output or route target
- unresolved `grounding` route target
- current-artifact carriage that contradicts `current none`
- trust-surface paths that are not valid portable carriers

Phase invariants:

- one owner per seam
- one live route per seam
- review verdict mechanics remain explicit
- route-only currentness remains explicit
- grounding never silently invents receipts

## Proof Plan

Positive ladder for phase 4:

1. schema-backed `review contract:`
2. `review_family` inheritance and patching
3. `route_only` declaration with guarded handoff sections
4. `grounding` declaration with explicit unresolved routing
5. current-truth and `trust_surface` integration across review and route-only
   outputs

Compile-negative ladder for phase 4:

- review references unknown schema gate
- schema contract exports no gates
- unknown `review_family`
- invalid `route_only` route target
- contradictory `current none` and carried current artifact
- unresolved grounding route target

## Exact Implementation Order

1. Allow `review contract:` to target schema contracts and export schema gates.
2. Add `review_family` and concrete review inheritance from review families.
3. Add `route_only` with explicit activation, `current none`, guarded handoff
   sections, and route tables.
4. Add `grounding` with protocol policy and unresolved routing.
5. Converge review and route-only readbacks onto typed markdown, render
   profiles, `properties`, guard shells, and trusted currentness carriers.
