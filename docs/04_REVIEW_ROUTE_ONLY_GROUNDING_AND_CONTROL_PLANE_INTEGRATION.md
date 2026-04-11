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
first-class, introduces a dedicated reusable review-family surface with
case-selected reviews, adds dedicated `route_only` and `grounding`
declaration families, and converges currentness, trust surfaces,
preservation, invalidation, and compact comment rendering into one coherent
control-plane layer.

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
- case-selected multi-mode review
- `route_only`
- `grounding`
- control-plane integration with preservation, invalidation, `support_only`,
  `ignore rewrite_evidence`, and `trust_surface`
- schema-group invalidation consumption and concrete expansion
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
- the same contract-resolution rules apply inside explicitly selected review
  cases

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

### Case-selected reviews

Some critic families need one typed review surface whose live subject,
contract, currentness, and routing all change by mode while still exporting the
exact gates from the selected real contract.

Phase 4 therefore adds first-class review cases rather than relying on a hidden
"selected contract" projection.

Canonical form:

```prompt
enum ReviewMode: "Review Mode"
    dossier: "Dossier Review"
        wire: "dossier"

    copy: "Copy Review"
        wire: "copy"

review_family MultiModeArtifactReview: "Multi-Mode Artifact Review"
    comment_output: ArtifactReviewComment

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        current_artifact: current_artifact
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner
        active_mode: active_mode

    selector:
        mode active_mode = ReviewState.active_mode as ReviewMode

    cases:
        dossier: "Dossier Review"
            when ReviewMode.dossier
            subject: SectionDossier
            contract: DossierReviewContract

            checks:
                reject contract.handoff_truth when ProducerHandoff.names_wrong_current_artifact
                reject contract.citation_grounding when ReviewState.citations_missing
                accept "The dossier review contract passes." when contract.passes

            on_accept:
                current artifact SectionDossier via ArtifactReviewComment.current_artifact
                carry active_mode = ReviewMode.dossier
                route "Accepted dossier review returns to {{DossierAuthor}}." -> DossierAuthor

            on_reject:
                current artifact SectionDossier via ArtifactReviewComment.current_artifact
                carry active_mode = ReviewMode.dossier
                route "Rejected dossier review returns to {{DossierAuthor}}." -> DossierAuthor

        copy: "Copy Review"
            when ReviewMode.copy
            subject: DraftCopy
            contract: CopyReviewContract

            checks:
                reject contract.wording_precision when ReviewState.wording_missing
                reject contract.metadata_alignment when ReviewState.metadata_conflict
                accept "The copy review contract passes." when contract.passes

            on_accept:
                current artifact DraftCopy via ArtifactReviewComment.current_artifact
                carry active_mode = ReviewMode.copy
                route "Accepted copy review returns to {{CopyEditor}}." -> CopyEditor

            on_reject:
                current artifact DraftCopy via ArtifactReviewComment.current_artifact
                carry active_mode = ReviewMode.copy
                route "Rejected copy review returns to {{CopyEditor}}." -> CopyEditor
```

Requirements:

- exactly one selector is active for a case-selected review family
- exactly one case must match for any valid selected mode
- each case owns one subject, one contract, one review-check surface, and
  explicit `on_accept` and `on_reject` consequences
- `contract.*` inside a case resolves only against that case's contract
- `failing_gates` export the exact gates from the active case's contract with
  their original ownership preserved
- the selected case must determine currentness and next-owner routing in the
  same semantic place as the selected contract

Render intent when the active mode is dossier:

```markdown
## Review Mode

Dossier Review

## Failure Detail

- Failing Gates:
  - Handoff Truth
  - Citation Grounding

## Next Owner

Dossier Author
```

This is the requirement that closes the multi-mode critic gap: the rendered
review must read like the selected real review, not like a generic wrapper
contract.

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
        section_author -> SectionAuthor
        section_architect -> SectionArchitect
        playable_strategist -> PlayableStrategist
        lesson_architect -> LessonArchitect
        else -> ProjectLead
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
        if unresolved -> route ProjectLead
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
- `invalidate` may target either one concrete artifact root or one
  `schema.groups.*` entry
- invalidating a schema group must preserve member-level currentness semantics
  while expanding the readable readback into one concrete member per artifact

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

## Name Resolution And Inheritance

Phase-4 resolution rules:

- `review contract:` resolves to `workflow` or `schema`
- `review` may inherit from a `review_family`
- review-family selectors must resolve to a closed enum
- review cases resolve `when` tags, subjects, and contracts explicitly
- `route_only` routes resolve to agent targets
- `grounding` route targets resolve to agents
- `schema.groups.*` resolves to declared schema-group entries
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
- review-family selector that does not resolve to a closed enum
- duplicate or overlapping review-case selectors
- review-case set that is not total for the selected mode surface
- unresolved review-case subject or contract
- unresolved `route_only` handoff output or route target
- unresolved `grounding` route target
- invalidation target that resolves to neither a concrete artifact root nor a
  schema group
- current-artifact carriage that contradicts `current none`
- trust-surface paths that are not valid portable carriers

Phase invariants:

- one owner per seam
- one live route per seam
- review verdict mechanics remain explicit
- route-only currentness remains explicit
- grounding never silently invents receipts
- schema-group invalidation expands concrete members in authored group order

## Proof Plan

Positive ladder for phase 4:

1. schema-backed `review contract:`
2. `review_family` inheritance and patching
3. case-selected review family with exact gate export
4. `route_only` declaration with guarded handoff sections
5. `grounding` declaration with explicit unresolved routing
6. current-truth and `trust_surface` integration across review and route-only
   outputs
7. schema-group invalidation consumption with concrete readback expansion

Compile-negative ladder for phase 4:

- review references unknown schema gate
- schema contract exports no gates
- unknown `review_family`
- overlapping or non-total review cases
- review case with unresolved subject or contract
- invalid `route_only` route target
- contradictory `current none` and carried current artifact
- invalid schema-group invalidation target
- unresolved grounding route target

## Exact Implementation Order

1. Allow `review contract:` to target schema contracts and export schema gates.
2. Add `review_family` and concrete review inheritance from review families.
3. Add case-selected review families with explicit selector resolution,
   exact-case gate export, and case-owned currentness/routing.
4. Add `route_only` with explicit activation, `current none`, guarded handoff
   sections, and route tables.
5. Add `grounding` with protocol policy and unresolved routing.
6. Add schema-group invalidation targets and member-level expansion semantics.
7. Converge review and route-only readbacks onto typed markdown, render
   profiles, `properties`, guard shells, concrete invalidation expansion, and
   trusted currentness carriers.
