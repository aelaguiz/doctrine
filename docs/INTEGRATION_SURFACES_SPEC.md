---
status: drafting_artifact
artifact_role: pre-phase design input
superseded_by_phase_docs: true
---

> Historical drafting artifact note (2026-04-11): This file stays at its
> original `docs/` path because archived second-wave implementation docs cite
> it directly. The implementation-order planning set now lives in the numbered
> phase docs under `docs/01_` through `docs/04_`, and shipped integration truth
> lives in `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/WORKFLOW_LAW.md`,
> `docs/REVIEW_SPEC.md`, and `doctrine/`. Treat the body below as pre-phase
> design history, not as the canonical phased plan.

# Integration Surfaces For New Language Features

This document recorded how the second-wave language features were expected to
integrate with the rest of Doctrine during design.

Many shipped surfaces discussed here now exist, including `analysis`,
`schema`, `document`, agent `analysis:` attachments, typed `schema:` /
`structure:` attachments, and schema-backed `review contract:` support.
Deferred ideas in this document remain deferred unless the live docs say
otherwise.

The key architectural rule in this design record was:

- add the minimum number of new declaration families
- use shipped Doctrine surfaces before inventing new layers
- keep reusable control-plane semantics on existing Doctrine surfaces when they
  already fit
- let new surfaces attach to existing `workflow`, `review`, `input`, `output`,
  `trust_surface`, currentness, preservation, and invalidation machinery
  instead of building parallel systems

The structural invariant under that rule was:

- one owner per seam
- one live route per seam

The strongest design rule recorded here was:

Doctrine owns the grammar of the move.
Domain packs own the specific game being played.

If a behavior should compile-fail, route-fail, or render consistently across
many lanes, it belongs in Doctrine.
If it encodes domain pedagogy, corridor taste, or role temperament, it belongs
in the domain pack.

## Surfaces that remain on existing Doctrine features

The narrowed recommendation is:

- workflow law continues to own routes, currentness, preservation, and
  invalidation
- review continues to own critic semantics, verdict coupling, carried state, and
  current truth
- outputs continue to own durable carriers
- prose continues to own mission and judgment

That means the new surfaces are not replacements for workflow law or review.
They are complementary:

- `analysis` covers structured reasoning programs
- `schema` covers artifact inventories and later gate catalogs

Everything else should continue to reuse the current language shape.

## Output integration

The main output-side integration is:

- `schema:` attaches to outputs in the minimal first wave
- `structure:` attaches `document` schemas to markdown-bearing inputs and outputs
  in the richer readable-output design

The important distinction:

- `schema:` is an artifact inventory contract
- `structure:` is a readable document shape

These can coexist conceptually, but the first `schema` rollout deliberately
keeps the first implementation smaller by making `schema:` the primary output
attachment.

Phase 1 `schema` attachment:

```prompt
output LessonPlanFile: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: MarkdownDocument
    requirement: Required
    schema: LessonPlanSchema
```

Readable-output `structure:` attachment:

```prompt
output LessonPlanFileOutput: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: AgentOutputDocument
    structure: LessonPlan
    requirement: Required
```

Integration rule:

- the new attachment should be descriptive and typed, not a prose convention

## Review integration

### Explored surface: review-family inheritance

One early direction was to add review-family inheritance as a first-class
surface for critic behavior.

The motivating observation was:

- critics repeat the same local review scaffolds
- handoff-first blocking, failing-gate export, current-truth handling, and
  routed next-owner logic are structurally repeated

The explored shape was:

```prompt
abstract review ProducerArtifactReview: "Producer Artifact Review"
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
        block handoff_incomplete when producer_handoff.incomplete
        reject wrong_current_artifact when producer_handoff.names_wrong_current_artifact
```

Then patch per artifact:

```prompt
review LessonPlanReview[ProducerArtifactReview]: "Lesson Plan Review"
    subject: lesson_plan
    contract: LessonPlanContract

    contract_checks:
        reject contract.explicit_step_roles when lesson_plan.step_roles_implicit
        reject contract.no_invented_route when lesson_plan.invented_route
        accept "The shared lesson-plan contract passes." when contract.passes

    on_accept:
        current artifact lesson_plan via CriticVerdictAndHandoffOutput.current_artifact
        route "Accepted lesson plan returns to LessonsSituationSynthesizer." -> LessonsSituationSynthesizer

    on_reject:
        current artifact lesson_plan via CriticVerdictAndHandoffOutput.current_artifact when not present(blocked_gate)
        current none when present(blocked_gate)
        route "Rejected lesson plan returns to LessonsLessonArchitect." -> LessonsLessonArchitect
```

Before, the prompt surface looked like this:

```markdown
## Lesson Plan Review Rules
### Start Review
Read the producer's handoff comment...
### Verdict Rules
`accept` means...
`changes requested` must...
### Who It Goes Back To
For lesson-plan problems...
```

After, the prompt surface became:

```prompt
review LessonPlanReview[ProducerArtifactReview]: "Lesson Plan Review"
    subject: lesson_plan
    contract: LessonPlanContract

    contract_checks:
        reject contract.explicit_step_roles when lesson_plan.step_roles_implicit
        reject contract.no_invented_route when lesson_plan.invented_route
        accept "The shared lesson-plan contract passes." when contract.passes

    on_accept:
        current artifact lesson_plan via critic_handoff.current_artifact
        route -> LessonsSituationSynthesizer

    on_reject:
        current artifact lesson_plan via critic_handoff.current_artifact when not present(blocked_gate)
        current none when present(blocked_gate)
        route -> LessonsLessonArchitect
```

Before, the emitted AGENTS.md surface looked like:

```markdown
## Lesson Plan Review Rules

### Start Review

Read the producer's handoff comment...
Read `lesson_root/_authoring/LESSON_PLAN.md`.
Check it against the shared lesson-plan review contract...

### Verdict Rules

`accept` means...
`changes requested` must...

### Who It Goes Back To

For lesson-plan problems...
```

After, the emitted AGENTS.md became:

```markdown
## Lesson Plan Review

Review subject: Lesson Plan.
Start with the producer handoff. If it does not clearly name the current lesson
plan, stop there and send it back before content review begins.

### Contract Gates

Reject: Step Roles are still implied.
Reject: The lesson plan invents a new route.
Accept only if the shared lesson-plan contract passes.

### If Accepted

Current artifact: Lesson Plan.
Route to LessonsSituationSynthesizer.

### If Rejected

If review blocked before content review began, there is no current artifact for
this outcome.
Otherwise the current artifact remains Lesson Plan.
Route to LessonsLessonArchitect.
```

### Narrowed recommendation

Do not invent a separate `review_family` declaration kind.

Use:

- existing abstract review inheritance
- existing review patches
- later `schema` gate catalogs as review contracts in phase 2

The narrowed after-state is:

```prompt
abstract review ProducerArtifactReview: "Producer Artifact Review"
    ...
    handoff_first:
        block "The producer handoff is incomplete." when ProducerHandoff.incomplete
        reject "The producer handoff names the wrong current artifact." when ProducerHandoff.names_wrong_current_artifact

review LessonPlanReview[ProducerArtifactReview]: "Lesson Plan Review"
    subject: LessonPlanFile
    contract: LessonPlanSchema
    comment_output: CriticVerdictAndHandoffOutput
    ...
```

The intended boundary:

- review mechanics stay on Doctrine `review`
- artifact section inventories and gate names move to `schema`
- critic posture stays prose in the agent

### Review and schema integration

The second-wave integration point is:

- `review contract:` may resolve to either a workflow review contract or a
  `schema`

The effect is that section inventories and gate catalogs can live on `schema`,
while verdict mechanics, carried current truth, and next-owner coupling stay on
`review`.

## Route and currentness integration

### Explored surface: `route_only` as a first-class declaration

One early direction was to add a dedicated `route_only` declaration to absorb
route-only coordination prose.

The motivating observation was:

- some route-only semantics were already in law
- repeated critic misses, metadata debt, and routing-comment requirements were
  still narrated in prose
- route-only turns want typed `current none`, guarded readback, and next-owner
  coupling

The explored shape was:

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

Before, the prompt surface looked like:

```prompt
workflow RouteOnlyTurns: "Routing-Only Turns"
    "Use this route when no specialist output file is current yet..."
    "Keep the current issue plan and the current issue comment explicit..."
    "When the same critic miss comes back again..."
    law:
        active when ...
        current none
        stop ...
        route ...
```

After, the prompt surface became:

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

Before, the emitted AGENTS.md surface looked like:

```markdown
## Routing-Only Turns

Use this route when no specialist output file is current yet...
When the same critic miss comes back again, put one short `Repeated Problem`
section...
If it is still unclear which specialist should go next...
```

After, the emitted AGENTS.md became:

```markdown
## Routing-Only Turns

Use this turn when no specialist artifact is current and the live job is
routing, process repair, or owner repair.

There is no current artifact for this turn.

Keep the current issue plan and the routing comment explicit about the next
owner and the next step.
When the same critic miss repeats, add a short Repeated Problem section that
says what keeps failing, which role it came back from, and the next concrete
fix.
If the next specialist owner is still not justified, keep the issue on
LessonsProjectLead.
```

### Narrowed recommendation

Do not add `route_only` as a new declaration kind.

Existing workflow law already covers the route-only seam, and the active
direction is to finish porting that seam there.

The route-only integration rule is:

- keep route-only turns on `workflow` law
- use the readable-output system to render route-only handoffs and guarded
  comment sections cleanly
- keep `current none` and routing ownership as workflow-law semantics

## Preservation, invalidation, and `trust_surface`

The proposal set repeatedly identifies these existing Doctrine surfaces as the
correct layer for current truth and portable state:

- stronger `preserve`
- stronger `invalidate`
- `support_only`
- `ignore rewrite_evidence`
- current artifact via `trust_surface`

Those are reusable control-plane semantics and should remain in Doctrine rather
than being reintroduced through new declaration families.

The integration rule is:

- analysis does not replace preservation or invalidation law
- schema does not replace current-truth carriage
- review and outputs continue to carry current truth explicitly through trusted
  fields

The readable-output work should make those semantics render more readably, but
the semantics themselves remain attached to the current surfaces.

## Grounding and metadata integration

Grounding was recognized as another seam where prose currently carries
algorithmic behavior:

- start from current wording unless rewrite
- do not do draft-first grounding
- allow one narrower follow-up question if needed
- route upstream rather than freewrite when receipts are missing

An explored declaration family for that seam was:

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

The narrowed recommendation is not to add a first-class `grounding`
declaration yet.

Instead:

- keep formalizing what can already be expressed with workflow law and shared
  skills
- let the readable-output system render scope and preservation panels cleanly

Grounding and bounded-scope panels are therefore second-wave integration work,
not first-wave core language additions.

## `render_profile` integration

One early direction was to make output readability configurable through
first-class render profiles.

The explored shape:

```prompt
render_profile LessonsHome:
    current_artifact -> sentence
    own_only -> sentence
    preserve_exact -> sentence
    review.contract_checks -> titled_section
    analysis.stages -> natural_ordered_prose
    guarded_sections -> concise_explanatory_shell
```

The purpose of `render_profile` was:

- keep highly formal source surfaces from rendering mechanically
- allow the same structure to render differently in contract view, artifact
  view, and comment view

The canonical profile family explored for the typed-markdown system was:

```prompt
render_profile ContractMarkdown
render_profile ArtifactMarkdown
render_profile CommentMarkdown
```

The narrowed recommendation is:

- do not add user-authored `render_profile` in the first wave
- ship built-in renderer templates for `analysis` and `schema` first
- revisit authored render policy in a later wave once the new semantic
  declarations have been exercised

## Integration sequence

The first-wave minimal elegant expansion is:

1. finish the current parity plan on existing workflow/review surfaces
2. add `analysis`
3. add `schema`
4. add `schema:` output attachment
5. later allow `review contract:` to point at `schema`

The broader exploratory expansion proposed adding:

- `analysis`
- richer schema and semantic document contracts
- review-family inheritance
- `route_only`
- grounding
- `render_profile`

The final narrowed recommendation does not remove those ideas from the design
space. It reclassifies them:

- `analysis` and `schema` are first-wave core surfaces
- review-family behavior should use existing abstract review inheritance
- route-only behavior should stay on workflow law
- grounding and authored render profiles are later-wave work

## Boundary heuristics

The following decision test is meant to guide future integration choices:

If a behavior should compile-fail, route-fail, or render consistently across
many lanes, it belongs in Doctrine.

If a behavior encodes pedagogy, corridor taste, temperament, or other
domain-family judgment, it belongs outside Doctrine.
