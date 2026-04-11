# Second-Wave And Deferred Language Ideas

This document captures the broader language-enhancement ideas that were explored
around the same time as `analysis`, `schema`, and the readable-output system,
but were either narrowed, deferred, or explicitly rejected as first-wave core
declaration families.

The high-level design direction explored was:

- add first-class analysis blocks for repeated reasoning choreography
- add artifact schemas with semantic gates, not just headings
- add review families so critic logic is inherited and patched, not recopied
- add route-only handoff schemas so routing comments stop carrying hidden law
- add grounding protocols so wording-safe behavior is declarative
- add readback render profiles so formal source still expands into natural
  AGENTS.md prose

The boundary explored for that broader direction was:

- Doctrine should own anything that is structurally true across many roles or
  many teams: currentness, routing, preservation, invalidation, gated review,
  grounding protocol shape, analysis step ordering, trust surfaces, and render
  policy
- domain packs should own anything that is domain truth or family-specific
  judgment

The narrowed first-wave recommendation did not discard these ideas. It
reclassified them:

- some become second-wave work
- some remain on existing workflow or review surfaces
- some become readable-output implementation details instead of new top-level
  declarations

## Review-family inheritance as a dedicated concept

### Motivation

The motivating claim for a review-family feature was:

- critic prompts still repeat local review scaffolds
- the same handoff-first blocking, failing-gate export, current-truth handling,
  and routed next-owner logic appears repeatedly
- this repetition is a major prose bucket

### Explored surface

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

### Why it was attractive

This surface is attractive because it centralizes:

- handoff-first blocking
- wrong-current-artifact rejection
- failing-gate export
- blocked-gate handling
- current artifact carry-through
- next-owner routing

It lets concrete reviews patch artifact-specific contract checks instead of
copying the whole review shell.

### Why it was narrowed

The later recommendation is:

- do not add a separate `review_family` language
- existing abstract review inheritance plus shared review patches are already
  the right surface

So the second-wave position is:

- keep the review-family idea as a design heuristic
- express it through abstract reviews and shared review contracts
- let `schema` later carry gate catalogs
- keep critic posture and judgmental review tone in prose

## `route_only` as a dedicated declaration family

### Motivation

The route-only exploration started from the observation that route-only turns
already have typed semantics hidden in prose:

- live job in routing, process repair, or owner repair
- no specialist artifact is current
- current artifact is `none`
- guarded repeated-problem sections
- guarded rewrite-mode sections
- next-owner routing

### Explored surface

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

### Before and after example

Before:

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

After:

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

Rendered output:

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

### Why it was narrowed

The later recommendation is:

- do not add `route_only` as a new declaration kind
- existing workflow law already covers it
- keep typed currentness, routes, and route-only activation on workflow law
- use the readable-output layer to render route-only comments and guarded blocks
  well

So the `route_only` design remains useful as a shape study, but not as a
first-wave declaration family.

## Grounding as a first-class declaration family

### Motivation

Grounding and copy-authoring flows were recognized as another area where prose
is secretly algorithmic:

- start from current wording unless rewrite
- do not do draft-first grounding
- ask one narrower question if needed
- route upstream rather than freewrite when receipts are missing

That is not just style. It is behavioral law.

### Explored surface

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

### What this would own

Doctrine would own:

- grounding protocol shape
- start-from-current wording policy
- draft-first prohibition
- narrower-follow-up allowance
- upstream route on unresolved state

Domain packs would still own:

- which skill or knowledge interface is used
- what counts as a safe receipt
- which fields are meaning-bearing wording versus cosmetic wording

### Why it was deferred

The later recommendation is:

- do not add a first-class `grounding` declaration yet
- formalize what can already be captured with workflow law and shared skills
- let the readable-output system render scope and preservation panels cleanly
- return to grounding after the core `analysis` and `schema` surfaces prove
  themselves

So grounding remains explicitly in the design space, but outside the first
wave.

## `render_profile` and readback templates

### Motivation

This idea was treated as the feature that makes highly formal source still read
like natural AGENTS.md.

The concern was:

- source prompts can become highly symbolic
- output homes still need to read directly and naturally
- the renderer should not mirror the AST mechanically

### Explored surface

Example render profile:

```prompt
render_profile LessonsHome:
    current_artifact -> sentence
    own_only -> sentence
    preserve_exact -> sentence
    review.contract_checks -> titled_section
    analysis.stages -> natural_ordered_prose
    guarded_sections -> concise_explanatory_shell
```

The broader typed-markdown design also proposed three canonical core profiles:

```prompt
render_profile ContractMarkdown
render_profile ArtifactMarkdown
render_profile CommentMarkdown
```

The intended roles:

- `ContractMarkdown` should explain required structure
- `ArtifactMarkdown` should produce a natural authored shell
- `CommentMarkdown` should stay compact, using properties and guarded callouts

### Why it was attractive

`render_profile` gives a clean separation:

- source becomes highly formal
- output remains readable, full, and natural

It also explains how the same underlying structure can render differently in:

- AGENTS contract view
- authored artifact shell view
- review comment and route-only handoff view

### Why it was deferred

The later recommendation is:

- no first-class user-authored `render_profile` in the first wave
- built-in renderer templates for `analysis` and `schema` are enough initially
- revisit authored render policy later

The design space remains open. It is just not part of the minimal first-wave
surface set.

## `properties` and explicit guarded block primitives

### Motivation

The expanded typed-markdown design introduced three extra primitives beyond the
core document blocks:

- `properties`
- `guard`
- `render_profile`

The `properties` motivation:

- compact labeled facts like Target, Path, Shape, Requirement, Current
  Artifact, Next Owner, Metadata Mode, and similar fields degrade into bullets
  or extra headings today

The `guard` motivation:

- route-only comment blocks
- failure-detail blocks
- rewrite-mode sections
- repeated-problem sections

all want a first-class readable-shell concept instead of awkward conditional
paragraphs

### Explored use in comment documents

```prompt
document RouteOnlyHandoff: "Routing Handoff Comment"
    properties must_include: "Must Include"
        current_route: "Current Route"
        next_owner: "Next Owner"
        next_step: "Next Step"

    callout rewrite_mode: "Rewrite Mode" when RouteFacts.section_status in {"new", "full_rewrite"}
        kind: note
        "Later section metadata must be rewritten instead of inherited."

    section repeated_problem: "Repeated Problem" when RouteFacts.critic_miss_repeated
        properties:
            failing_pattern: "What Keeps Failing"
            returned_from: "Returned From"
            next_fix: "Next Concrete Fix"

    section standalone_read: "Standalone Read"
        "A downstream owner should be able to read this comment alone and understand that no specialist artifact is current, what route-only state is now in force, who owns next, and what the next concrete step is."
```

### Why it was deferred or narrowed

The later document-system spec folded much of this back into:

- ordinary `when <expr>` guards on blocks
- `bullets`, `definitions`, and `callout`
- built-in profile logic rather than user-authored `render_profile`

`properties` remains a useful second-wave candidate if compact fact panels still
feel awkward after the first document/block rollout.

## Typed row and item schemas on readable blocks

### Motivation

One broader readable-document sketch also explored symbolic row and item typing
directly on `table` and `sequence` blocks:

- `row_schema`
- `item_schema`

The motivating claim was:

- columns alone describe table shape, but not reusable row shape
- later review, preservation, or schema-contract work may want stable symbolic
  references to rows or sequence items
- row and item typing could keep contract views and artifact shells aligned
  without relying only on prose descriptions

### Explored surface

```prompt
sequence step_order: "Step Order" required
    item_schema: StepOrderItem
    "State the step order and what each step is there to teach."

table step_arc: "Step Arc Table" required
    row_schema: StepArcRow
    columns:
        step: "Step"
        role: "Role"
        introduces: "Introduces"
        coaching_level: "Coaching Level"
        difficulty_curve: "Difficulty Curve"
```

### Why it was deferred

The later narrowed recommendation was:

- no first-wave `row_schema:` or `item_schema:` fields
- get the initial document/block system working with titles, requirements,
  columns, optional rows, and built-in renderer behavior first

So typed row and item schemas remain a plausible second-wave extension, but
only if later review-contract or preservation work proves that block-level
shape is not enough.

## Stronger preservation surfaces as supporting law

The broadest proposal set also explicitly grouped the following under Doctrine
core, not domain packs:

- stronger `preserve`
- stronger `invalidate`
- `support_only`
- `ignore rewrite_evidence`
- current artifact via `trust_surface`

These are not new declaration families in the narrowed plan.
They are supporting law surfaces that the new features are expected to coexist
with and render more readably.

## Earliest recommended path to value

The broader exploratory recommendation at one point was:

Add only three new surfaces first:

- `analysis`
- `schema` with semantic gates
- `render_profile`

Then use them on:

- a large procedural producer lane
- critic review surfaces
- route-only coordination surfaces

The reason for that recommendation was simple:

- `analysis` attacks the biggest remaining procedural prose bucket
- `schema` attacks repeated section inventories and gate prose
- `render_profile` keeps the emitted homes natural

The later narrower recommendation changed that path to:

- first wave: `analysis` and `schema`
- built-in natural rendering rules
- second wave: consider authored render profiles, schema-as-review-contract,
  and grounding or richer comment/document primitives

## Explicit deferrals and rejections

The final narrowed recommendation explicitly says:

- no first-class `grounding` declaration yet
- no first-class user-authored `render_profile` yet
- no special domain-specific "lesson contract" or "step table" primitive
- no separate `review_family` declaration kind
- no separate `route_only` declaration kind

The reason for all of these deferrals is the same:

- keep the first wave minimal
- use existing Doctrine surfaces where they already fit
- let the smallest set of new semantic declarations prove themselves before
  growing the language further

## Decision heuristics for later waves

The second-wave ideas collected here should be reconsidered only if the first
wave leaves a real gap.

Use these tests:

Add a new second-wave surface only if:

- the behavior is structurally repeated
- existing workflow, review, output, and readable-output surfaces do not
  express it cleanly
- the new surface would remove a meaningful amount of semantic prose rather
  than just shorten wording

Do not add a second-wave surface if:

- it is just domain vocabulary
- it is just output wording taste
- it can be expressed as a patch on existing workflow or review law
- it exists only to save a few lines of prose without creating a real compiler
  seam
