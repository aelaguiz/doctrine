




repomix-lessons-doctrine-context.md
File

LESSONS_SYMBOLIC_DOCTRINE_PORT_IMPLEMENTATION_PLAN_2026-04-10.md
File
I'm in the process of porting our lessons agents to use some of the new doctrine features as you can see from the work plan.

However even on the other side of that there will be a huge amount of just prose in the lesson agents that can drift.

I'd like to eliminate almost all of the prose but preserve the intent of the agent on the output side.

Tell me what the most elegant language features I should add to achieve that are, and what should go into the lessons agents level vs what should go into doctrine. Give me specific examples including before/after on both the prompt and output AGENTS.md level.

I’m pulling the current Doctrine feature surface and the Lessons work plan together first, then I’ll turn that into a concrete split between language features and agent-local doctrine.

I’ve isolated the main drift seams now: currentness, metadata mode, route-only turns, review, preservation, and out-of-scope title handling. The common pattern is prose carrying state, scope, routing, and preservation law, so I’m turning those into concrete Doctrine-vs-Lessons before/after examples.



repomix-lessons-doctrine-context.md
File

LESSONS_SYMBOLIC_DOCTRINE_PORT_IMPLEMENTATION_PLAN_2026-04-10.md
File
I'm in the process of porting our lessons agents to use some of the new doctrine features as you can see from the work plan.

However even on the other side of that there will be a huge amount of just prose in the lesson agents that can drift.

I'd like to eliminate almost all of the prose but preserve the intent of the agent on the output side. The output should not become overly concise it's the input side that we're trying to formalize. The output agent should read naturally.

Tell me what the most elegant language features I should add to achieve that are, and what should go into the lessons agents level vs what should go into doctrine. Give me specific examples including before/after on both the prompt and output AGENTS.md level.

The design principle is clear now: don’t chase brevity for its own sake—promote any prose that is secretly schema into Doctrine, and leave only taste and judgment at the Lessons layer.

That sharpens the split further: make semantics compiler-owned on the authoring side, but preserve human-owned taste in the rendered AGENTS.md. I’m pulling the most reusable syntax patterns from the existing doctrine surface so the proposals extend your current language cleanly.

I’m keeping that second criterion front and center now: source prompts can become almost fully symbolic, but the rendered AGENTS.md still needs to read richly and naturally.

Thought for 30m 48s
Your work plan is already aiming at the right class of problem: the remaining drift is mostly semantic prose masquerading as instruction, not missing tone. The plan explicitly calls out shared output carriers, metadata mode/currentness, route-only turns, critic verdict mechanics, and preservation/invalidation as the seams that should move into typed Doctrine surfaces, while keeping mission, rationale, and judgment-heavy quality bars in prose. It also makes “human-readable emitted homes” a hard requirement, so the right move is more structure in source, not terser runtime output. 

 


The most elegant direction is:

Add first-class analysis blocks for repeated reasoning choreography.

Add artifact schemas with semantic gates, not just headings.

Add review families so critic logic is inherited and patched, not recopied.

Add route-only handoff schemas so routing comments stop carrying hidden law.

Add grounding protocols so wording-safe behavior is declarative.

Add readback render profiles so all that formal source still expands into natural AGENTS.md prose.

The key boundary is simple:

Doctrine should own anything that is structurally true across many roles or many teams: currentness, routing, preservation, invalidation, gated review, grounding protocol shape, analysis step ordering, trust surfaces, and render policy. The plan already points in exactly that direction with richer carriers, typed mode binding, route-only workflow law, first-class review, and typed preservation/invalidation. 


Lessons should own anything that is domain truth or family-specific judgment: poker meaning, which upstream artifacts are authoritative, what “same-route similar-burden” means, the 90–120s pacing corridor, exact-move boundaries, anti-leak heuristics, section/lesson document names, and the SOUL / role identity. The current metadata workflow is a good example: Doctrine should provide the shape, while Lessons owns lesson-title mode, section mode, metadata_route_facts, and the specific preserve/rewrite rules. 

 


The strongest design rule is: Doctrine owns the grammar of the move; Lessons owns the specific game being played.

1) Add analysis: as a first-class construct
This is the biggest missing piece after your current port plan.

Right now, large parts of LessonsLessonArchitect and similar lanes are still procedural prose: restate the lesson job, assign step roles, build nearby-lesson evidence, compare real comparable lessons, defend pacing, build step arc, then mark stable vs variable. That is clearly not “tone”; it is a reusable reasoning program. 

 


What Doctrine should add
A construct like:

analysis LessonPlanning: "Lesson Planning"
    basis:
        section_lesson_map
        section_concepts_terms
        section_playable_strategy

    stages:
        lesson_job:
            derive lesson_promise from {section_lesson_map, section_concepts_terms, section_playable_strategy}

        step_roles:
            classify step_order as StepRole
            require explicit

        continuity:
            compare nearby_lessons as prior_lessons_step_count

        comparables:
            compare accepted_lessons same_route similar_burden
            fallback least_wrong_fit
            export real_comparable_lessons

        pacing:
            defend target_duration 90..120s

        step_arc:
            derive step_arc_table
            derive guidance_plan

        boundaries:
            preserve decisions {section_lesson_map, section_playable_strategy}
            forbid invented_route
            export stable_vs_variable
What stays in Lessons
StepRole, the 90–120s corridor, what counts as “same-route”, what counts as “least-wrong fit”, and which basis files matter.

Before: prompt surface
workflow LessonPlanAnalysisSteps: "Lesson Plan Analysis Steps"
    "Restate in plain English what this lesson owns..."
    "Name what each step is doing using `introduce`, `practice`, `test`, or `capstone`..."
    "Build nearby-lesson evidence..."
    "Find real comparable lessons..."
    "Use current lesson data to defend the lesson's size..."
    "Build the `Step Arc Table`..."
    "Say what must stay stable and what may vary safely..."
After: prompt surface
enum StepRole: "Step Role"
    introduce: "introduce"
    practice: "practice"
    test: "test"
    capstone: "capstone"

analysis LessonPlanning: "Lesson Planning"
    basis:
        section_lesson_map
        section_concepts_terms
        section_playable_strategy

    stages:
        lesson_job:
            derive lesson_promise

        step_roles:
            classify steps as StepRole
            require explicit

        continuity:
            compare nearby_lessons as prior_lessons_step_count

        comparables:
            compare accepted_lessons same_route similar_burden
            fallback least_wrong_fit

        pacing:
            defend target_duration 90..120s

        step_arc:
            derive step_arc_table
            derive guidance_plan

        boundaries:
            preserve decisions {section_lesson_map, section_playable_strategy}
            forbid invented_route
Before: emitted AGENTS.md
## Lesson Plan Analysis Steps

### Step 1 - Restate The Lesson Job

Restate in plain English what this lesson owns, what it defers, and what is genuinely new here.

### Step 2 - Set The Step Roles

Name what each step is doing using `introduce`, `practice`, `test`, or `capstone` before you defend pacing.

### Step 3 - Set The Guidance Plan

Say how much help each step or step group should give.
...
After: emitted AGENTS.md
## Lesson Planning

Plan the lesson from the approved section lesson map, concepts file, and playable strategy.

### What To Decide

First restate the lesson promise.
Then give every step one explicit role: introduce, practice, test, or capstone.
Use nearby lessons for continuity evidence.
Use real same-route lessons of similar burden for comparable evidence, and name any fallback plainly.
Defend the final size against the 90–120s pacing corridor.
Make the step arc, guidance taper, and stable-versus-variable boundaries explicit.

Do not invent a new route or reopen upstream concept or playable decisions.
That is exactly the shape you want: formal source, natural output.

2) Add schema: or richer artifact contracts with semantic gates
Your current review contracts still spend enormous prose budget on “At minimum confirm…” because headings alone are not enough. The plan itself calls out preservation/invalidation as a remaining drift seam, and it explicitly wants exact shared-contract gate export in review. 

 


The existing Doctrine examples already prove that structured scope/preservation can render naturally: current artifact, own only, preserve exact, and preserve structure show up as readable sentences in the emitted home. 


What Doctrine should add
A richer document schema surface:

schema LessonPlanContract: "Shared Lesson Plan Contract"
    sections:
        lesson_promise: "Lesson Promise"
        step_order: "Step Order"
        step_roles: "Step Roles" as StepRole[]
        prior_lessons_step_count: "Prior-Lessons Step-Count Table"
        real_comparable_lessons: "Real Comparable Lessons"
        step_arc_table: "Step Arc Table"
        guidance_plan: "Guidance Plan"
        stable_vs_variable: "Stable Vs Variable"

    gates:
        explicit step_roles
        comparable_lessons not count_only_similarity
        preserve route from section_lesson_map
        stable_vs_variable explicit
What stays in Lessons
The actual sections, the domain gate names, and the meaning of “count-only similarity” or “route preservation”.

Before: prompt surface
## Shared Lesson Plan Review Contract

At minimum confirm the file has non-empty `Lesson Promise`, `Step Order`, `Step Roles`, ...
At minimum confirm the lesson does not leave `introduce`, `practice`, `test`, or `capstone` semantics implied in prose.
At minimum confirm `Real Comparable Lessons` uses real comparable lessons...
At minimum confirm the lesson plan stays inside the route already approved upstream...
After: prompt surface
schema LessonPlanContract: "Shared Lesson Plan Contract"
    sections:
        lesson_promise: "Lesson Promise"
        step_order: "Step Order"
        step_roles: "Step Roles" as StepRole[]
        real_comparable_lessons: "Real Comparable Lessons"
        stable_vs_variable: "Stable Vs Variable"

    gates:
        explicit step_roles
        real_comparable_lessons same_route_or_named_fallback
        no invented_route
        stable_vs_variable explicit
Before: emitted AGENTS.md
## Shared Lesson Plan Review Contract

At minimum confirm the file has non-empty `Lesson Promise`, `Step Order`, `Step Roles`, ...
At minimum confirm the lesson does not leave `introduce`, `practice`, `test`, or `capstone` semantics implied in prose.
...
After: emitted AGENTS.md
## Shared Lesson Plan Review Contract

Confirm that the lesson plan contains the full lesson promise, step order, explicit step roles, comparable-lesson proof, and stable-versus-variable boundaries.

Fail review if step roles are only implied, if comparable proof is only count similarity, or if the plan quietly invents a new route.
This is a much better compression ratio because you are compressing schema, not flattening meaning.

3) Add review family inheritance as a first-class surface for Critic
The plan is blunt here: the critic still repeats local review scaffolds and should move to a shared abstract review base plus concrete patches. That is the biggest remaining prose bucket. 


What Doctrine should add
You already have review and abstract review inheritance. The elegant next step is a specialized inheritance model for recurring review families: handoff-first blocking, failing-gate export, current-truth handling, and routed next-owner logic should live once.

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
Then patch per artifact:

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
What stays in Lessons
The subjects, contracts, next-owner map, and any review posture that is genuinely judgmental rather than mechanical. The plan explicitly says critic independence, handoff-first stops, and “do not rewrite that producer truth here” should remain prose. 


Before: prompt surface
## Lesson Plan Review Rules
### Start Review
Read the producer's handoff comment...
### Verdict Rules
`accept` means...
`changes requested` must...
### Who It Goes Back To
For lesson-plan problems...
After: prompt surface
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
Before: emitted AGENTS.md
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
After: emitted AGENTS.md
## Lesson Plan Review

Review subject: Lesson Plan.
Start with the producer handoff. If it does not clearly name the current lesson plan, stop there and send it back before content review begins.

### Contract Gates

Reject: Step Roles are still implied.
Reject: The lesson plan invents a new route.
Accept only if the shared lesson-plan contract passes.

### If Accepted

Current artifact: Lesson Plan.
Route to LessonsSituationSynthesizer.

### If Rejected

If review blocked before content review began, there is no current artifact for this outcome.
Otherwise the current artifact remains Lesson Plan.
Route to LessonsLessonArchitect.
That is dramatically cleaner, and it preserves natural output.

4) Add a first-class route_only: construct
Your current LessonsProjectLead source shows the exact problem: some semantics are already in law:, but a lot of coordination truth is still narrated around repeated critic misses, metadata debt, and what the routing comment must carry. 


The plan explicitly says this seam should become typed current none, guarded readback, and next-owner coupling. 


What Doctrine should add
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
What stays in Lessons
The next-owner enum, the exact labels like Repeated Problem, and the local explanation of metadata debt boundaries.

Before: prompt surface
workflow RouteOnlyTurns: "Routing-Only Turns"
    "Use this route when no specialist output file is current yet..."
    "Keep the current issue plan and the current issue comment explicit..."
    "When the same critic miss comes back again..."
    law:
        active when ...
        current none
        stop ...
        route ...
After: prompt surface
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
Before: emitted AGENTS.md
## Routing-Only Turns

Use this route when no specialist output file is current yet...
When the same critic miss comes back again, put one short `Repeated Problem` section...
If it is still unclear which specialist should go next...
After: emitted AGENTS.md
## Routing-Only Turns

Use this turn when no specialist artifact is current and the live job is routing, process repair, or owner repair.

There is no current artifact for this turn.

Keep the current issue plan and the routing comment explicit about the next owner and the next step.
When the same critic miss repeats, add a short Repeated Problem section that says what keeps failing, which role it came back from, and the next concrete fix.
If the next specialist owner is still not justified, keep the issue on LessonsProjectLead.
That preserves warmth while moving the logic out of prose.

5) Add grounding: protocols
Metadata and copy still carry real algorithmic law in prose: start from the current wording unless rewrite, do not do draft-first grounding, ask one narrower question if needed, and route upstream rather than freewrite when receipts are missing. That is not just style guidance. 


Doctrine should own
A generic grounding protocol surface:

grounding WordingGrounding: "Wording Grounding"
    source: poker_kb_interface
    target: wording

    policy:
        start_from current_wording unless rewrite
        forbid draft_first
        allow one_narrower_followup
        if unresolved -> route LessonsProjectLead
Lessons should own
Which skill is used, what counts as a safe receipt, and which fields are “teaching wording” versus cosmetic wording.

This would let you delete a shocking amount of repeated copy/metadata prose without flattening the behavior.

6) Add render_profile: / readback templates
This is the feature that makes the whole plan work.

The plan is adamant that emitted homes must stay direct and human-readable. The existing bound-scope example already proves that structured law can render as natural sentences like “Current artifact: Section Metadata.”, “Own only …”, and “Preserve exact … except …”. 


So do not let the renderer mirror the AST mechanically. Give Doctrine a render profile layer, for example:

render_profile LessonsHome:
    current_artifact -> sentence
    own_only -> sentence
    preserve_exact -> sentence
    review.contract_checks -> titled_section
    analysis.stages -> natural_ordered_prose
    guarded_sections -> concise_explanatory_shell
Doctrine owns the rendering primitives. Lessons owns the profile selection and any family-specific wording choices.

That gives you the crucial separation:

source becomes highly formal,

output remains readable, full, and natural.

What I would put in Doctrine vs Lessons
Put in Doctrine core

analysis

richer schema / semantic document contracts

review family inheritance

route_only

grounding

render_profile

stronger preserve, invalidate, support_only, ignore rewrite_evidence, current artifact via trust_surface

These are all reusable control-plane semantics, and your plan already identifies them as the correct layer for Doctrine to own. 

 


Put in lessons common/contracts

StepRole

MetadataMode

ProjectLeadRouteOnlyNextOwner

SolverFit

ExactMoveBoundary

the 90–120s pacing corridor

“same-route similar-burden”

which artifacts are preserve bases

specific review gates for lesson plan / situations / materialization / copy / metadata

Keep as prose in lessons agents

role identity and SOUL

poker-teaching taste bars

the few judgment calls that are genuinely not compile-checkable

warnings that exist because humans make repeated mistakes, not because the system lacks a semantic shape

A good test is:
If it should compile-fail, route-fail, or render consistently across many lanes, it belongs in Doctrine.
If it encodes poker pedagogy, corridor taste, or role temperament, it belongs in Lessons.

The shortest path to value
I would add only three new surfaces first:

analysis:

schema: with semantic gates

render_profile:

Then I would use them on:

LessonsLessonArchitect

LessonsAcceptanceCritic

LessonsProjectLead

That matches your current plan’s biggest drift buckets and should remove the most prose while keeping AGENTS.md natural and even more readable than it is now. 

 


The next experiment I’d run is: formalize LessonsLessonArchitect with analysis: first, because its current prompt is visibly procedural prose, and the emitted home has a clear before/after readability test. Then formalize the critic with a shared review family. That sequence gives you the largest drift reduction with the cleanest cold-read signal.


I've been working through formatting side / rendering side requirements to make the output rich and read naturally in the markdown output. Explain how you would extend this for your above feature set

The right move is not better heading heuristics. It is making the output layer typed markdown.

Today Doctrine’s renderer is essentially one recursive section walker: every nested structure becomes another heading depth, and the only real non-heading formatting it knows about is emphasized prose like **REQUIRED**:. That is why rich semantic differences collapse into ## / ### / #### and read as “outline depth” instead of “document shape.”    

At the same time, your lessons contracts already want richer document forms. The lesson-plan contract explicitly calls for things like Prior-Lessons Step-Count Table, Guided-Walkthrough Beat-Count Table, and Step Arc Table, but today those are still only prose instructions about tables, not first-class table structures.    

So the elegant enhancement is this:

Add a first-class document declaration with typed block children.
Not “more markdown strings.” Not lesson-specific hacks. A real Doctrine document AST.

The core Doctrine primitives should be:
	•	document — a named output schema
	•	section — prose block
	•	sequence — ordered list block
	•	table — markdown table block
	•	callout — portable admonition / emphasis block

Those belong in Doctrine itself because they are general markdown semantics. Things like step_arc, prior_lesson_counts, and their columns stay in the Lessons layer. The language owns shape; the workflow owns meaning. That keeps the boundary clean.    

Here is the Doctrine surface I would ship.

document LessonPlan: "Lesson Plan"
    callout durable_truth: "Durable Truth"
        kind: important
        "This file owns the lesson job, pacing, and stable-vs-variable boundaries."

    section lesson_promise: "Lesson Promise" required
        "State what this lesson owns now."

    sequence step_order: "Step Order" required
        "State the step order and what each step is there to teach."

    table step_arc: "Step Arc Table" required
        columns:
            step: "Step"
            role: "Role"
            introduces: "Introduces"
            coaching_level: "Coaching Level"
            difficulty_curve: "Difficulty Curve"
        notes:
            "Add one row per step."
            "Make introduce, practice, test, new-concept placement, and coaching taper explicit."

    table prior_lesson_counts: "Prior-Lessons Step-Count Table" required
        columns:
            lesson: "Lesson"
            step_count: "Step Count"
            comparable_kind: "Comparable Kind"
            target_count: "Target Count"
            variance_reason: "Variance Reason"
        notes:
            "Use nearby lessons and sections."
            "Make size precedent visible rather than implied."

    table real_comparables: "Real Comparable Lessons" required
        columns:
            lesson: "Lesson"
            route_match: "Route Match"
            burden_match: "Burden Match"
            why: "Why"
        notes:
            "Start with same-route, similar-burden lessons."
            "Name fallback comparisons plainly when they are only least-wrong fits."

Then the output contract should attach that structure directly:

output LessonPlanFileOutput: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: ProductionArtifactDocument
    structure: LessonPlan
    requirement: Required

That one addition changes the emitted markdown from “nested headings about headings” into a real contract document.

This is what the compiled AGENTS.md contract view should look like:

## Lesson Plan File

- Target: File
- Path: lesson_root/_authoring/LESSON_PLAN.md
- Shape: Agent Output Document
- Requirement: Required

> **IMPORTANT — Durable Truth**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.

### Lesson Promise

Required prose section.

State what this lesson owns now.

### Step Order

Required ordered sequence.

State the step order and what each step is there to teach.

### Step Arc Table

Required table.

| Column | Meaning |
| --- | --- |
| Step | Step identifier or ordinal |
| Role | introduce / practice / test / capstone |
| Introduces | What is genuinely introduced here |
| Coaching Level | How explicit the help is |
| Difficulty Curve | How challenge rises step to step |

Add one row per step.
Make introduce, practice, test, new-concept placement, and coaching taper explicit.

### Prior-Lessons Step-Count Table

Required table.

| Column | Meaning |
| --- | --- |
| Lesson | Nearby lesson used as precedent |
| Step Count | Its actual step count |
| Comparable Kind | true comparable / fallback / corridor precedent |
| Target Count | Intended count for this lesson |
| Variance Reason | Why the current lesson matches or breaks pattern |

Use nearby lessons and sections.
Make size precedent visible rather than implied.

### Real Comparable Lessons

Required table.

| Column | Meaning |
| --- | --- |
| Lesson | Named comparable lesson |
| Route Match | Same route / partial / fallback |
| Burden Match | Similar / lighter / heavier |
| Why | Why this comparison is honest |

Start with same-route, similar-burden lessons.
Name fallback comparisons plainly when they are only least-wrong fits.

And this is what the authored artifact itself should naturally converge toward:

# Lesson Plan

> **IMPORTANT**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.

## Lesson Promise

This lesson installs the first clean recognition of ...

## Step Order

1. Introduce the new idea in a low-burden spot.
2. Practice it with explicit coaching.
3. Tighten coaching while preserving the same route.
4. Test it without adding a new mechanic.

## Step Arc Table

| Step | Role | Introduces | Coaching Level | Difficulty Curve |
| --- | --- | --- | --- | --- |
| 1 | introduce | range advantage cue | high | low |
| 2 | practice | none | medium-high | low-medium |
| 3 | practice | none | medium | medium |
| 4 | test | none | low | medium-high |

## Prior-Lessons Step-Count Table

| Lesson | Step Count | Comparable Kind | Target Count | Variance Reason |
| --- | --- | --- | --- | --- |
| Lesson A | 4 | corridor precedent | 4 | same install-before-test burden |
| Lesson B | 5 | fallback | 4 | current lesson has no walkthrough |

## Real Comparable Lessons

| Lesson | Route Match | Burden Match | Why |
| --- | --- | --- | --- |
| Lesson A | same-route | similar-burden | same introduce → practice → test spine |
| Lesson C | fallback | slightly-heavier | similar coaching taper but more concepts |

The language changes needed are straightforward.

First, extend the grammar with a real document_decl plus typed block entries like section, sequence, table, and callout. Doctrine already has first-class declarations for workflows, reviews, skills, inputs, and outputs, so this is a natural extension of the language rather than a side-channel.    

Second, let outputs reference a document schema through a field like structure:. That keeps output contracts typed and reusable, instead of burying document shape inside giant must_include record trees. The current must_include trees work, but they are semantically too generic for rich document rendering.    

Third, change the renderer from “depth-based recursion” to “block-kind dispatch.” A section renders as heading + prose, a sequence renders as an ordered list shell, a table renders as a markdown table, and a callout renders as a portable blockquote-style admonition. Headings still matter, but they stop being the only tool.    

Fourth, make document paths addressable and inheritable exactly the way Doctrine already treats other structured declarations. You want things like LessonPlan.step_arc.columns.coaching_level to be referenceable, patchable, and preserved under inheritance. That keeps the feature symbolic, drift-resistant, and consistent with the rest of Doctrine’s design.  

The important design discipline is this:

Do not bake “lessonness” into Doctrine.
Doctrine should know what a table is.
Lessons should decide that one table is called Step Arc Table.

That is the clean split.

So the fully formed enhancement is: Doctrine gains a typed document system, and markdown richness comes from semantic block types instead of deeper heading depth. That gives you elegant AGENTS output, elegant authored artifacts, and a future-proof place to add tables without turning the language into raw markdown soup.

Thought for 14m 14s
Your typed-markdown direction is right, but for the feature set above I would extend it one level further:

Do not make document just another authored declaration. Make typed markdown the renderer’s target IR for all high-semantic surfaces.

Right now the remaining drift is not mainly “artifact layout drift.” It is the seams the plan already calls out: currentness, route-only turns, metadata mode/scope, review verdict mechanics, and preservation/invalidation. Those are exactly the places where the current system still depends on prose and heading depth instead of compiler-owned structure. 


So I would split the rendering architecture into two layers:

Doctrine AST
    -> semantic readback IR
    -> typed markdown IR
    -> markdown text
That one separation matters a lot. It means analysis, review, route_only, output, and bounded-scope law do not render by “recursive section walker.” They each lower into a richer block tree first, and only then into markdown.

The practical effect is:

lesson-plan contracts stop being “headings describing tables” and become real typed documents,

review stops being “headings around verdict prose” and becomes a real review shell,

route-only handoffs stop being “outline depth plus conditional paragraphs” and become a real comment document with guarded blocks,

metadata scope/preservation stops being narrated law and becomes a readable bounded-edit panel.

The lesson-plan lane already wants exactly that: Prior-Lessons Step-Count Table, Guided-Walkthrough Beat-Count Table, and Step Arc Table are explicit structural outputs, not just prose advice. 


What I would add to Doctrine itself is slightly more than your four primitives, but only slightly.

First, keep your core:

document

section

sequence

table

callout

Then add the three primitives that make the rest of the system click:

properties

guard

render_profile

properties is the missing shape for the many places where Doctrine already wants compact labeled facts rather than deeper outline nesting: Target, Path, Shape, Requirement, Current Artifact, Next Owner, Metadata Mode, and similar fields. Right now those often degrade into bullets or extra headings. guard is what makes route-only and failure-detail blocks elegant instead of awkward. render_profile is what keeps the same source structure readable in different emitted contexts: AGENTS.md contract view, authored artifact shell, and comment/handoff view. The existing route-only examples already need guarded sections like Rewrite Mode and Repeated Problem, and the review examples already need current-artifact plus trust-surface readback, so these are not speculative niceties.

The clean rule is:

Doctrine owns block shape and lowering. Lessons owns labels, schemas, row meanings, and local rendering taste.

That keeps your boundary clean: Doctrine knows what a table, guarded block, or property panel is. Lessons decides that one of those tables is called Step Arc Table, and that one guarded block is called Repeated Problem.

The important extension is that render_profile should be first-class. Without that, typed markdown still forces one rendered shape everywhere, and you will end up back in the same problem one layer later.

I would define three canonical profiles in Doctrine:

render_profile ContractMarkdown
render_profile ArtifactMarkdown
render_profile CommentMarkdown
Then let Lessons patch them lightly.

ContractMarkdown should explain required structure. ArtifactMarkdown should produce a natural authored shell. CommentMarkdown should stay compact, with properties and guarded callouts. This is especially important because the same lesson-plan structure needs to render two very different ways: once as “what the file must contain” in AGENTS, and once as the actual LESSON_PLAN.md shell. Your lesson-plan example is exactly that split. 


Here is how I would extend your document surface for artifact contracts.

document LessonPlan: "Lesson Plan"
    callout durable_truth: "Durable Truth"
        kind: important
        "This file owns the lesson job, pacing, and stable-vs-variable boundaries."

    section lesson_promise: "Lesson Promise" required
        "State what this lesson owns now."

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
        notes:
            "Add one row per step."
            "Make introduce, practice, test, new-concept placement, and coaching taper explicit."

    table prior_lesson_counts: "Prior-Lessons Step-Count Table" required
        row_schema: PriorLessonCountRow
        columns:
            lesson: "Lesson"
            step_count: "Step Count"
            comparable_kind: "Comparable Kind"
            target_count: "Target Count"
            variance_reason: "Variance Reason"

    table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" when LessonRoute.walkthrough
        row_schema: WalkthroughBeatRow
        columns:
            lesson: "Lesson"
            beat_count: "Beat Count"
            target_beats: "Target Beats"
            break_reason: "Break Reason"
The two important additions there are row_schema and required. row_schema makes the table symbolic instead of just visual. That lets later review and preservation rules point at real row fields instead of prose descriptions of columns. required belongs at the block level so contract rendering can say “Required table” naturally, while artifact rendering can omit that phrase and just render the shell.

Then the output contract should reference both the structure and the render profile:

output LessonPlanFileOutput: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    structure: LessonPlan
    render_profile: ArtifactMarkdown
    contract_render_profile: ContractMarkdown
    requirement: Required
That gives you exactly the dual view you want:

AGENTS.md says what the file must contain,

the artifact shell itself reads like a natural markdown document.

Now for the feature set above, the crucial move is to do the same thing for comments and reviews, not just durable artifacts.

For route-only handoffs, I would not author them as loose output sections. I would define a real comment document shape.

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
That is a direct typed-markdown home for what the generic route-only capstone already proves: the route-only surface needs always-on fields, guarded Rewrite Mode, guarded Repeated Problem, and an honest “no current artifact” workflow state. 


Rendered as comment markdown, it should look like this:

## Routing Handoff Comment

- Current Route: route-only turn; no specialist artifact is current
- Next Owner: LessonsProjectLead
- Next Step: repair ownership justification

> **NOTE — Rewrite Mode**
> Later section metadata must be rewritten instead of inherited.

### Repeated Problem

- What Keeps Failing: critic keeps rejecting vague metadata handoff
- Returned From: LessonsAcceptanceCritic
- Next Concrete Fix: make section-mode preserve basis explicit
That is much richer and more natural than another cascade of headings.

For review, I would not add review-specific markdown primitives. I would keep review as a semantic Doctrine feature, but make its renderer lower into typed markdown blocks.

The review surface already has stable semantic slots: subject, contract, block/reject/accept checks, current artifact, failing gates, blocked gate, next owner. The current examples show Current Artifact carried through a trusted output field, with trust_surface making that carrier explicit.

So the lowering should be something like:

review LessonPlanReview: "Lesson Plan Review"
    subject: LessonPlanFile
    contract: LessonPlanContract
    comment_output: CriticVerdictComment
and Doctrine internally lowers that to a markdown document roughly like:

document CriticVerdictComment: "Verdict And Handoff Comment"
    properties summary: "Review State"
        verdict: "Verdict"
        reviewed_artifact: "Reviewed Artifact"
        next_owner: "Next Owner"
        current_artifact: "Current Artifact"

    section analysis_performed: "Analysis Performed"
    section output_contents_that_matter: "Output Contents That Matter"

    section failure_detail: "Failure Detail" when verdict == changes_requested
        sequence failing_gates: "Failing Gates"
        callout blocked_gate: "Blocked Gate" when blocked

    section trust_surface: "Trust Surface"
        sequence entries:
            "Current Artifact"
Then ReviewMarkdown can render it in a house style that already feels natural:

## Lesson Plan Review

Review subject: Lesson Plan.
Shared review contract: Lesson Plan Contract.

### Contract Gate Checks

Reject: Step Roles are still implied.
Reject: The lesson plan invents a new route.
Accept only if the shared lesson-plan contract passes.

### If Accepted

Current artifact: Lesson Plan.
Route to LessonsSituationSynthesizer.

### If Rejected

Current artifact: Lesson Plan.
Route to LessonsLessonArchitect.
That is exactly the sort of surface your plan wants when it says the critic should move to first-class review with explicit block, reject, accept, current truth, exact failing-gate export, and routed next-owner behavior. 


For analysis, I would again keep the semantic feature separate from markdown, but let it lower into a typed document. The lesson-plan lane already has a nine-stage planning flow and explicit output tables. The point is not just to render the stages prettily; it is to let the renderer choose the right shape for each stage. Build Real Comparable Lessons is a narrative step. Prior-Lessons Step-Count Table and Step Arc Table are true tables. Set Stable And Variable Boundaries is really a bounded-rules section.

So I would add:

analysis LessonPlanning: "Lesson Planning"
    stages:
        lesson_job:
            derive lesson_promise

        step_roles:
            derive step_roles

        continuity:
            derive prior_lesson_counts

        comparables:
            derive real_comparable_lessons

        pacing:
            derive pacing_judgment

        step_arc:
            derive step_arc

        boundaries:
            derive stable_vs_variable
The renderer then lowers that into a document according to profile:

in AGENTS.md, maybe numbered planning stages,

in compact homes, maybe “What To Decide” prose plus tables,

in artifact templates, just the exported structures.

That is a much cleaner separation than baking the final markdown outline into the semantic construct itself.

For grounding, I would resist adding a domain-specific markdown primitive right away. The metadata seam already shows the real need: one current file, narrow owned scope, exact preservation, preserved decisions, and rewrite-evidence exclusions need to render readably.

That suggests the right markdown support is still generic:

properties for scope and preserve basis,

callout for stop lines,

table for nearby accepted comparisons,

optionally one later excerpt block if you truly need short quoted receipts.

So I would render metadata and grounding like this:

document MetadataPassScope: "Metadata Pass Scope"
    properties route_state: "Route State"
        metadata_mode: "Metadata Mode"
        current_file: "Current File"
        preserve_basis: "Preserve Basis"
        rewrite_regime: "Rewrite Regime"

    callout scope: "Scope"
        kind: important
        "Own only title in lesson-title mode."
        "Own only name and description in section mode."

    callout preservation: "Preservation"
        kind: note
        "Preserve exact out-of-scope fields."
        "Preserve decisions from the preserve basis."
That is the natural render home for the semantics the metadata workflow already carries in prose today. 


The other design rule I would enforce is:

every renderable block must have a stable symbolic key that is not its title.

Titles are prose. Keys are law. That is what keeps inheritance, patching, review references, and preservation stable. So yes, you should absolutely be able to reference things like:

LessonPlan.step_arc.columns.coaching_level

LessonPlan.prior_lesson_counts.columns.variance_reason

RouteOnlyHandoff.repeated_problem.returned_from

CriticVerdictComment.failure_detail.failing_gates

MetadataPassScope.route_state.preserve_basis

That is where the elegance comes from: the human surface can change wording, but the symbolic identity remains fixed.

The one thing I would not do is add lesson-specific render kinds to Doctrine. No step_arc, no review_comment_card, no metadata_scope_block. Doctrine should own only the universal block kinds and the lowering interfaces. Lessons owns the actual schemas, labels, and row semantics. That is consistent with the split your current port plan is already aiming for: Doctrine owns currentness, route-only law, review law, and preservation surfaces; Lessons owns the actual domain truth and contract content. 


So the compact version of the extension is:

Ship typed markdown as a true IR, not just a nicer authored surface.

Add properties, guard, and render_profile to your initial document / section / sequence / table / callout set.

Lower analysis, review, route_only, output, and bounded-scope law into that IR instead of letting them fall straight into heading recursion.

Keep stable symbolic block keys separate from human titles.

Keep Doctrine generic; let Lessons define named document schemas like LessonPlan, RouteOnlyHandoff, and CriticVerdictComment.

If I were sequencing this, I would implement it in this order:

typed markdown IR + properties

guard

render_profile

output structure: references

semantic lowerers for review and route_only

semantic lowerer for analysis

That gets you the biggest readability win fastest, because the worst remaining markdown collapse is not actually the durable artifact files. It is the comment and review surfaces.












repomix-lessons-doctrine-context.md
File
Right now the output formatting on the doctrine language is very naive it basically just uses increasing levels of indentation and markdown "####" 

This is not optimally using the descriptive power of markdown to create structure and emphasis in the output layer and reads clunky.

I want you to design the most elegant possible language enhancement such that the output is formatted much more richly as is possible with markdown, including support for things like tables which I don't currently support in the doctrine language but am likely to add:

document LessonPlan:
    section lesson_promise required
    section step_order required
    table step_arc required
        columns: step, role, introduces, coaching_level, difficulty_curve
    table prior_lesson_counts required
        columns: lesson, step_count, comparable_kind, target_count, variance_reason
    table real_comparables required
        columns: lesson, route_match, burden_match, why



Show me the fully formed output structure that is much more richly expressive and the language changes needed to achieve it.

I’m first grounding this in the current Doctrine surface, renderer, grammar, and shipped lesson contracts so the design fits the language instead of becoming a formatting hack. Then I’ll turn that into a concrete syntax update, the richer rendered markdown shape it enables, and the minimal new primitives needed.

I’ve confirmed the gap: lessons already want true tables, ledgers, and compact metadata blocks, but Doctrine still flattens them into recursive headings and bullets. I’m shaping this as an additive, first-class presentation layer with real block types.

Thought for 11m 19s
The right move is not better heading heuristics. It is making the output layer typed markdown.

Today Doctrine’s renderer is essentially one recursive section walker: every nested structure becomes another heading depth, and the only real non-heading formatting it knows about is emphasized prose like **REQUIRED**:. That is why rich semantic differences collapse into ## / ### / #### and read as “outline depth” instead of “document shape.” 

 


At the same time, your lessons contracts already want richer document forms. The lesson-plan contract explicitly calls for things like Prior-Lessons Step-Count Table, Guided-Walkthrough Beat-Count Table, and Step Arc Table, but today those are still only prose instructions about tables, not first-class table structures. 

 


So the elegant enhancement is this:

Add a first-class document declaration with typed block children.
Not “more markdown strings.” Not lesson-specific hacks. A real Doctrine document AST.

The core Doctrine primitives should be:

document — a named output schema

section — prose block

sequence — ordered list block

table — markdown table block

callout — portable admonition / emphasis block

Those belong in Doctrine itself because they are general markdown semantics. Things like step_arc, prior_lesson_counts, and their columns stay in the Lessons layer. The language owns shape; the workflow owns meaning. That keeps the boundary clean. 

 


Here is the Doctrine surface I would ship.

document LessonPlan: "Lesson Plan"
    callout durable_truth: "Durable Truth"
        kind: important
        "This file owns the lesson job, pacing, and stable-vs-variable boundaries."

    section lesson_promise: "Lesson Promise" required
        "State what this lesson owns now."

    sequence step_order: "Step Order" required
        "State the step order and what each step is there to teach."

    table step_arc: "Step Arc Table" required
        columns:
            step: "Step"
            role: "Role"
            introduces: "Introduces"
            coaching_level: "Coaching Level"
            difficulty_curve: "Difficulty Curve"
        notes:
            "Add one row per step."
            "Make introduce, practice, test, new-concept placement, and coaching taper explicit."

    table prior_lesson_counts: "Prior-Lessons Step-Count Table" required
        columns:
            lesson: "Lesson"
            step_count: "Step Count"
            comparable_kind: "Comparable Kind"
            target_count: "Target Count"
            variance_reason: "Variance Reason"
        notes:
            "Use nearby lessons and sections."
            "Make size precedent visible rather than implied."

    table real_comparables: "Real Comparable Lessons" required
        columns:
            lesson: "Lesson"
            route_match: "Route Match"
            burden_match: "Burden Match"
            why: "Why"
        notes:
            "Start with same-route, similar-burden lessons."
            "Name fallback comparisons plainly when they are only least-wrong fits."
Then the output contract should attach that structure directly:

output LessonPlanFileOutput: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: ProductionArtifactDocument
    structure: LessonPlan
    requirement: Required
That one addition changes the emitted markdown from “nested headings about headings” into a real contract document.

This is what the compiled AGENTS.md contract view should look like:

## Lesson Plan File

- Target: File
- Path: `lesson_root/_authoring/LESSON_PLAN.md`
- Shape: Agent Output Document
- Requirement: Required

> **IMPORTANT — Durable Truth**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.

### Lesson Promise

Required prose section.

State what this lesson owns now.

### Step Order

Required ordered sequence.

State the step order and what each step is there to teach.

### Step Arc Table

Required table.

| Column | Meaning |
| --- | --- |
| Step | Step identifier or ordinal |
| Role | introduce / practice / test / capstone |
| Introduces | What is genuinely introduced here |
| Coaching Level | How explicit the help is |
| Difficulty Curve | How challenge rises step to step |

Add one row per step.
Make introduce, practice, test, new-concept placement, and coaching taper explicit.

### Prior-Lessons Step-Count Table

Required table.

| Column | Meaning |
| --- | --- |
| Lesson | Nearby lesson used as precedent |
| Step Count | Its actual step count |
| Comparable Kind | true comparable / fallback / corridor precedent |
| Target Count | Intended count for this lesson |
| Variance Reason | Why the current lesson matches or breaks pattern |

Use nearby lessons and sections.
Make size precedent visible rather than implied.

### Real Comparable Lessons

Required table.

| Column | Meaning |
| --- | --- |
| Lesson | Named comparable lesson |
| Route Match | Same route / partial / fallback |
| Burden Match | Similar / lighter / heavier |
| Why | Why this comparison is honest |

Start with same-route, similar-burden lessons.
Name fallback comparisons plainly when they are only least-wrong fits.
And this is what the authored artifact itself should naturally converge toward:

# Lesson Plan

> **IMPORTANT**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.

## Lesson Promise

This lesson installs the first clean recognition of ...

## Step Order

1. Introduce the new idea in a low-burden spot.
2. Practice it with explicit coaching.
3. Tighten coaching while preserving the same route.
4. Test it without adding a new mechanic.

## Step Arc Table

| Step | Role | Introduces | Coaching Level | Difficulty Curve |
| --- | --- | --- | --- | --- |
| 1 | introduce | range advantage cue | high | low |
| 2 | practice | none | medium-high | low-medium |
| 3 | practice | none | medium | medium |
| 4 | test | none | low | medium-high |

## Prior-Lessons Step-Count Table

| Lesson | Step Count | Comparable Kind | Target Count | Variance Reason |
| --- | --- | --- | --- | --- |
| Lesson A | 4 | corridor precedent | 4 | same install-before-test burden |
| Lesson B | 5 | fallback | 4 | current lesson has no walkthrough |

## Real Comparable Lessons

| Lesson | Route Match | Burden Match | Why |
| --- | --- | --- | --- |
| Lesson A | same-route | similar-burden | same introduce → practice → test spine |
| Lesson C | fallback | slightly-heavier | similar coaching taper but more concepts |
The language changes needed are straightforward.

First, extend the grammar with a real document_decl plus typed block entries like section, sequence, table, and callout. Doctrine already has first-class declarations for workflows, reviews, skills, inputs, and outputs, so this is a natural extension of the language rather than a side-channel. 

 


Second, let outputs reference a document schema through a field like structure:. That keeps output contracts typed and reusable, instead of burying document shape inside giant must_include record trees. The current must_include trees work, but they are semantically too generic for rich document rendering. 

 


Third, change the renderer from “depth-based recursion” to “block-kind dispatch.” A section renders as heading + prose, a sequence renders as an ordered list shell, a table renders as a markdown table, and a callout renders as a portable blockquote-style admonition. Headings still matter, but they stop being the only tool. 

 


Fourth, make document paths addressable and inheritable exactly the way Doctrine already treats other structured declarations. You want things like LessonPlan.step_arc.columns.coaching_level to be referenceable, patchable, and preserved under inheritance. That keeps the feature symbolic, drift-resistant, and consistent with the rest of Doctrine’s design. 


The important design discipline is this:

Do not bake “lessonness” into Doctrine.
Doctrine should know what a table is.
Lessons should decide that one table is called Step Arc Table.

That is the clean split.

So the fully formed enhancement is: Doctrine gains a typed document system, and markdown richness comes from semantic block types instead of deeper heading depth. That gives you elegant AGENTS output, elegant authored artifacts, and a future-proof place to add tables without turning the language into raw markdown soup.


Yeah, give me a full spec for this, both at the language level and as the markdown output level. Think through all the different language features we have and are likely to add, and think through best-case markdown formatting for readability. Try to make rich use of the markdown feature set, and to the extent that to support those features, such as numbered bullets, we should make language changes, please expect them out as well. I'm looking for a thorough specification I can just implement and skip.

Thought for 23m 14s
The right abstraction is a typed markdown layer shared by all readable Doctrine surfaces, with a first-class document declaration at the top and a richer block AST underneath it.

That is the clean fix because the current renderer still fundamentally walks CompiledSection recursively and turns structure into deeper heading depth, while emphasized lines only become **KIND**: .... In other words, Doctrine currently knows “section nesting,” not “markdown block types.” Meanwhile the Lessons contracts already require genuinely tabular artifacts like Prior-Lessons Step-Count Table, Guided-Walkthrough Beat-Count Table, Step Arc Table, and Real Comparable Lessons, plus multiple named top-level sections that must stay separate rather than collapsing into ever-deeper heading ladders. 

 

 


So the spec I would ship is:

1. Core decision
Add a first-class readable document system to Doctrine, and make the markdown renderer operate on semantic block kinds instead of only section -> heading.

The important split is:

Doctrine owns structure and rendering semantics.

Lessons owns document names, required blocks, table names, and domain columns.

So Doctrine should know what a table, sequence, definitions, and callout are.

Lessons should decide that one particular table is called Step Arc Table.

That keeps the language beautiful and general, and keeps lesson-specific truth out of the core language. 

 


2. What ships
I would ship this as one coherent feature, not as a pile of renderer heuristics.

New top-level declaration
document LessonPlan: "Lesson Plan"
    ...
New readable block kinds
These should be first-class semantic blocks:

section — heading + block body

sequence — ordered list

bullets — unordered list

checklist — task list

definitions — compact term/explanation list

table — markdown table

callout — blockquote-style admonition

code — fenced code block

rule — thematic break

New attachment point on markdown-bearing contracts
Any markdown-bearing input or output contract may attach a document schema with:

structure: LessonPlan
New renderer model
Replace the heading-only compiled output tree with a richer block AST:

CompiledBlock =
    ParagraphBlock
    | SectionBlock
    | ListBlock
    | DefinitionsBlock
    | TableBlock
    | CalloutBlock
    | CodeBlock
    | RuleBlock
Existing authored sections compile to SectionBlock. Existing emphasized prose lines compile to either an inline emphasized paragraph or a CalloutBlock shell, depending on context. 

 


3. Canonical language spec
3.1 document
A document is a named, addressable, inheritable schema for a markdown artifact.

Canonical form:

document LessonPlan: "Lesson Plan"
    section lesson_promise: "Lesson Promise" required
        "State what this lesson owns now."

    sequence step_order: "Step Order" required
        "State the step order and what each step is there to teach."

    table step_arc: "Step Arc Table" required
        columns:
            step: "Step"
                "Step identifier or ordinal."
            role: "Role"
                "`introduce`, `practice`, `test`, or `capstone`."
            introduces: "Introduces"
                "What is genuinely introduced here."
            coaching_level: "Coaching Level"
                "How explicit the help is."
            difficulty_curve: "Difficulty Curve"
                "How challenge rises across the lesson."
        notes:
            "Add one row per step."
            "Make coaching taper explicit."
Semantics:

document is a readable declaration like workflow, skills, inputs, and outputs.

It is an addressable root.

It can be inherited and explicitly patched.

It is intended to describe the internal structure of markdown artifacts, not the operational workflow law of an agent.

3.2 Common block header shape
All document blocks share a common header shape:

<block_kind> <key>: "Title" <requirement>? <guard>?
Where:

<block_kind> is one of the supported block types

<key> is the stable symbolic identifier

"Title" is the rendered human title

<requirement> is one of:

required

advisory

optional

<guard> is:

when <expr>

Examples:

section lesson_promise: "Lesson Promise" required
table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" required when LessonFacts.walkthrough_in_scope
callout durable_truth: "Durable Truth" advisory
3.3 Block kinds
section
section lesson_promise: "Lesson Promise" required
    "State what this lesson owns now."
Renders as a heading section.

Body may contain any readable block.

sequence
sequence read_order: "Read Order" required
    first: "Read the active issue."
    second: "Read the current issue plan."
    third: "Read the latest current comment."
Renders as an ordered list.

Body items render in authored order.

Keyed items are recommended because they remain addressable.

bullets
bullets trust_surface: "Trust Surface" required
    artifact: "Current Artifact"
    active_mode: "Active Mode when present(active_mode)"
    trigger_reason: "Trigger Reason when present(trigger_reason)"
Renders as an unordered list.

checklist
checklist release_checks: "Release Checks" required
    lint: "Run lint."
    tests: "Run the minimum test suite."
    proof: "Confirm the proof artifact exists."
Renders as markdown task list items.

definitions
definitions must_include: "Must Include" required
    verdict: "Verdict"
        "Say `accept` or `changes requested`."
    reviewed_artifact: "Reviewed Artifact"
        "Name the reviewed artifact this review judged."
    analysis: "Analysis Performed"
        "Summarize the review analysis that led to the verdict."
Renders as compact term/explanation rows.

This is the best replacement for many current #### Must Include -> ##### Field Name ladders.

table
table step_arc: "Step Arc Table" required
    columns:
        step: "Step"
            "Step identifier or ordinal."
        role: "Role"
            "`introduce`, `practice`, `test`, or `capstone`."
        introduces: "Introduces"
            "What is genuinely introduced here."
        coaching_level: "Coaching Level"
            "How explicit the help is."
        difficulty_curve: "Difficulty Curve"
            "How challenge rises across the lesson."

    notes:
        "Add one row per step."
Optional row-bearing form for fixed or example tables:

table sample_arc: "Sample Arc"
    columns:
        step: "Step"
        role: "Role"
        introduces: "Introduces"

    rows:
        row_1:
            step: "1"
            role: "introduce"
            introduces: "range advantage cue"
        row_2:
            step: "2"
            role: "practice"
            introduces: "none"
Rules:

columns are ordered and keyed.

rows are optional.

Row cells must reference only declared columns.

Cells are inline markdown only, not nested block bodies.

Column bodies in schema mode are short descriptions, used by the contract renderer.

callout
callout durable_truth: "Durable Truth" required
    kind: important
    "This file owns the lesson job, pacing, and stable-vs-variable boundaries."
Allowed kind values in v1:

required

important

warning

note

This should align with the current emphasized prose vocabulary instead of inventing a second admonition family. 

 


code
code example_manifest: "Example Manifest" advisory
    language: json
    text: """
    {
      "title": "PLACEHOLDER: Lesson title",
      "steps": []
    }
    """
This requires a new multiline string literal in Doctrine. That is a good change to make anyway, because code fences and rich examples are clumsy without it.

rule
rule section_break
Renders as ---

4. New shared readable-block layer
This should not be document-only.

The same rich block kinds should be legal anywhere Doctrine currently emits readable markdown content, especially:

record_body

output_record_body

workflow_section_body

skill_entry_body

That matters because the problem is broader than lesson files.

Your current output contracts and review comment contracts are also clunky for the same reason. For example, this:

output DraftReviewComment: "Draft Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    must_include: "Must Include"
        verdict: "Verdict"
            "Say whether the review accepted the draft or requested changes."
        reviewed_artifact: "Reviewed Artifact"
            "Name the reviewed artifact this review judged."
should be writable as:

output DraftReviewComment: "Draft Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    definitions must_include: "Must Include"
        verdict: "Verdict"
            "Say whether the review accepted the draft or requested changes."
        reviewed_artifact: "Reviewed Artifact"
            "Name the reviewed artifact this review judged."
        analysis_performed: "Analysis Performed"
            "Summarize the review analysis that led to the verdict."
That gives you compact, elegant markdown in existing output contracts without forcing everything through document.

So the rule is:

document is the new top-level markdown schema declaration.

Rich block kinds are a shared sublanguage reused by documents and other readable Doctrine bodies.

That is the important architectural move.

5. structure: attachment on inputs and outputs
For markdown-bearing input/output contracts, add:

input LessonPlanContract: "Lesson Plan"
    source: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: MarkdownDocument
    structure: LessonPlan
    requirement: Required
and:

output LessonPlanFileOutput: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: AgentOutputDocument
    structure: LessonPlan
    requirement: Required
Rules:

structure: must resolve to a document.

It is descriptive and typed, not a prose convention.

It may appear on input and output.

In the future it may also appear on reusable output shape declarations, but v1 does not need that.

This is especially valuable for Lessons because the same named document can be used as:

an upstream input contract

a downstream output contract

a review basis

That is exactly the kind of durable symbolic seam Doctrine is good at. 

 


6. Addressability, interpolation, and refs
document and all keyed descendants should be addressable through the same path discipline Doctrine already uses for records and workflows.

Examples:

{{LessonPlan:title}}
{{LessonPlan:step_arc.title}}
{{LessonPlan:step_arc.columns.coaching_level.title}}
{{LessonPlan:step_arc.columns.coaching_level}}
This is important because current Doctrine already has addressable record paths, workflow paths, enums, and carried semantic fields. Documents should join that world instead of becoming inert renderer-only blobs. 


Addressability rules:

document root is addressable

keyed block children are addressable

table columns are addressable

table rows are addressable when present

anonymous list items are not addressable

keyed list/definition items are addressable

7. Inheritance and patching
document should inherit with the same explicit accounting doctrine as workflows and IO blocks.

Example:

document BaseLessonPlan: "Lesson Plan"
    section lesson_promise: "Lesson Promise" required
        "State what this lesson owns now."

    table step_arc: "Step Arc Table" required
        columns:
            step: "Step"
            role: "Role"


document WalkthroughLessonPlan[BaseLessonPlan]: "Lesson Plan"
    inherit lesson_promise
    inherit step_arc

    table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" required
        columns:
            lesson: "Lesson"
            beat_count: "Beat Count"
            target_count: "Target Count"
            variance_reason: "Variance Reason"
Rules:

inherited document blocks must be explicitly accounted for

override may replace the body or title of a block

block kind is invariant under override

missing inherited block accounting is a compile error

duplicate accounting is a compile error

That keeps the document layer aligned with the rest of Doctrine’s inheritance style.

8. Guards and conditional blocks
Document blocks should support when <expr>.

Example:

table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" required when LessonFacts.walkthrough_in_scope
    ...
Rules:

Guard syntax matches existing expression syntax.

In contract render mode, guarded blocks render as conditional shells, not as runtime-evaluated presence.

Expression visibility should reuse the same guard-expression restrictions as current guarded output sections.

A document block may not read emitted output fields directly through its guard, for the same reason guarded output sections may not. Keep one expression law.

That avoids introducing a second guard model.

9. Backward compatibility
This part is important.

Existing authored sections stay legal
Current readable keyed items:

step_one: "Step One"
    "Say hello."
become semantic sugar for:

section step_one: "Step One"
    "Say hello."
You do not need to rewrite old prompts immediately.

Existing emphasized lines stay legal
Current:

required "Read this first."
important "Keep the current plan as truth."
remain legal and keep their current render behavior.

They may optionally compile to single-line callout blocks internally, but the user-visible render should stay stable unless you explicitly migrate to blockquote callouts.

Rich blocks are opt-in
Nothing breaks unless authors choose the new blocks.

That is the migration you want.

10. Markdown rendering spec
This is the most important part for readability.

The rule is:

Only section consumes heading depth. Everything else uses its own markdown syntax.

10.1 Section
Contract render:

### Lesson Promise

_Required · section_

State what this lesson owns now.
Artifact skeleton render:

## Lesson Promise
10.2 Sequence
Contract render:

### Step Order

_Required · ordered list_

State the step order and what each step is there to teach.
If concrete items are present:

### Read Order

_Required · ordered list_

1. Read the active issue.
2. Read the current issue plan.
3. Read the latest current comment.
10.3 Bullets
### Trust Surface

_Required · unordered list_

- Current Artifact
- Active Mode when present(active_mode)
- Trigger Reason when present(trigger_reason)
10.4 Checklist
### Release Checks

_Required · checklist_

- [ ] Run lint.
- [ ] Run tests.
- [ ] Confirm proof artifact exists.
10.5 Definitions
This is the compact cure for Must Include and similar surfaces.

#### Must Include

_Required · definitions_

- **Verdict** — Say `accept` or `changes requested`.
- **Reviewed Artifact** — Name the reviewed artifact this review judged.
- **Analysis Performed** — Summarize the review analysis that led to the verdict.
If the definition body is longer:

- **Reviewed Artifact**
  Name the reviewed artifact this review judged.
  When review stopped at handoff quality, name the producer handoff instead.
10.6 Table
Schema-mode render:

### Step Arc Table

_Required · table_

| Column | Meaning |
| --- | --- |
| Step | Step identifier or ordinal. |
| Role | `introduce`, `practice`, `test`, or `capstone`. |
| Introduces | What is genuinely introduced here. |
| Coaching Level | How explicit the help is. |
| Difficulty Curve | How challenge rises across the lesson. |

Add one row per step.
Make coaching taper explicit.
Row-bearing render:

| Step | Role | Introduces | Coaching Level | Difficulty Curve |
| --- | --- | --- | --- | --- |
| 1 | introduce | range advantage cue | high | low |
| 2 | practice | none | medium | medium |
10.7 Callout
> **IMPORTANT — Durable Truth**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.
If no custom title:

> **WARNING**
> Do not reopen upstream concept or playable decisions here.
10.8 Code
#### Example Manifest

_Advisory · code · json_

```json
{
  "title": "PLACEHOLDER: Lesson title",
  "steps": []
}

### 10.9 Rule

```markdown
---
10.10 Guarded block shell
### Guided-Walkthrough Beat-Count Table

_Required · table · when walkthrough is in scope_

| Column | Meaning |
| --- | --- |
| Lesson | Nearby walkthrough lesson. |
| Beat Count | Actual comparable beat count. |
| Target Count | Planned beat count here. |
| Variance Reason | Why this lesson keeps or breaks the corridor. |
11. Fully formed example: LessonPlan
Doctrine source
document LessonPlan: "Lesson Plan"
    callout durable_truth: "Durable Truth" advisory
        kind: important
        "This file owns the lesson job, pacing, and stable-vs-variable boundaries."

    section lesson_promise: "Lesson Promise" required
        "State what this lesson owns now."

    sequence step_order: "Step Order" required
        "State the step order and what each step is there to teach."

    definitions step_roles: "Step Roles" required
        introduce: "Introduce"
            "Name what each step is doing using `introduce`."
        practice: "Practice"
            "Name what each step is doing using `practice`."
        test: "Test"
            "Name what each step is doing using `test`."
        capstone: "Capstone"
            "Name what each step is doing using `capstone`."

    table prior_lesson_counts: "Prior-Lessons Step-Count Table" required
        columns:
            lesson: "Lesson"
                "Nearby lesson used as precedent."
            step_count: "Step Count"
                "Actual step count in that lesson."
            comparable_kind: "Comparable Kind"
                "True comparable, same-route precedent, or fallback."
            target_count: "Target Count"
                "Planned count for the current lesson."
            variance_reason: "Variance Reason"
                "Why the current lesson keeps or breaks pattern."

    table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" required when LessonFacts.walkthrough_in_scope
        columns:
            lesson: "Lesson"
                "Nearby walkthrough lesson."
            beat_count: "Beat Count"
                "Actual comparable beat count."
            target_count: "Target Count"
                "Planned beat count here."
            variance_reason: "Variance Reason"
                "Why this lesson keeps or breaks the corridor."

    table step_arc: "Step Arc Table" required
        columns:
            step: "Step"
                "Step identifier or ordinal."
            role: "Role"
                "The step role."
            introduces: "Introduces"
                "What is genuinely introduced here."
            coaching_level: "Coaching Level"
                "How explicit the help is."
            difficulty_curve: "Difficulty Curve"
                "How challenge rises."

    section guidance_plan: "Guidance Plan" required
        "Say how much help each step or step group should give."

    section new_vs_reinforced_vs_deferred: "New Vs Reinforced Vs Deferred" required
        "Say what is genuinely new, what is reinforced, and what stays deferred."

    section nearby_lesson_evidence: "Nearby-Lesson Evidence" required
        "Keep nearby-lesson evidence separate from real comparable-lesson proof."

    table real_comparables: "Real Comparable Lessons" required
        columns:
            lesson: "Lesson"
                "Named comparable lesson."
            route_match: "Route Match"
                "Same-route, partial, or fallback."
            burden_match: "Burden Match"
                "Similar, lighter, or heavier."
            why: "Why"
                "Why this comparison is honest."

    section why_not_shorter: "Why Not Shorter" required
        "Explain what burden or install-before-test work would be lost."

    section why_not_longer: "Why Not Longer" required
        "Explain why extra steps would exceed earned burden."

    section stable_vs_variable: "Stable Vs Variable" required
        "State what later lanes must keep stable and what may vary safely."
Output contract
output LessonPlanFileOutput: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: AgentOutputDocument
    structure: LessonPlan
    requirement: Required
Contract render
### Lesson Plan File

- Target: File
- Path: `lesson_root/_authoring/LESSON_PLAN.md`
- Shape: Agent Output Document
- Structure: Lesson Plan
- Requirement: Required

#### Structure: Lesson Plan

> **IMPORTANT — Durable Truth**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.

##### Lesson Promise

_Required · section_

State what this lesson owns now.

##### Step Order

_Required · ordered list_

State the step order and what each step is there to teach.

##### Step Roles

_Required · definitions_

- **Introduce** — Name what each step is doing using `introduce`.
- **Practice** — Name what each step is doing using `practice`.
- **Test** — Name what each step is doing using `test`.
- **Capstone** — Name what each step is doing using `capstone`.

##### Prior-Lessons Step-Count Table

_Required · table_

| Column | Meaning |
| --- | --- |
| Lesson | Nearby lesson used as precedent. |
| Step Count | Actual step count in that lesson. |
| Comparable Kind | True comparable, same-route precedent, or fallback. |
| Target Count | Planned count for the current lesson. |
| Variance Reason | Why the current lesson keeps or breaks pattern. |

##### Guided-Walkthrough Beat-Count Table

_Required · table · when walkthrough is in scope_

| Column | Meaning |
| --- | --- |
| Lesson | Nearby walkthrough lesson. |
| Beat Count | Actual comparable beat count. |
| Target Count | Planned beat count here. |
| Variance Reason | Why this lesson keeps or breaks the corridor. |

...
Optional future skeleton render
# Lesson Plan

> **IMPORTANT**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.

## Lesson Promise

## Step Order

1.
2.
3.

## Step Roles

- **Introduce** —
- **Practice** —
- **Test** —
- **Capstone** —

## Prior-Lessons Step-Count Table

| Lesson | Step Count | Comparable Kind | Target Count | Variance Reason |
| --- | --- | --- | --- | --- |

## Guided-Walkthrough Beat-Count Table

| Lesson | Beat Count | Target Count | Variance Reason |
| --- | --- | --- | --- |

## Step Arc Table

| Step | Role | Introduces | Coaching Level | Difficulty Curve |
| --- | --- | --- | --- | --- |
That skeleton mode is not required to ship the language, but the AST should make it possible with no redesign.

12. Validation rules
These should fail loudly.

Declaration-level
structure: must resolve to a document

document block keys must be unique

inherited document blocks must be explicitly accounted for

override must target an existing inherited key

override must preserve block kind

Table-specific
table must have columns

column keys must be unique

rows may reference only declared columns

row keys must be unique

cells must be inline markdown, not nested blocks

List/definitions
keyed items must be unique within their block

anonymous string items are allowed but not addressable

mixing anonymous and keyed items is legal, but keyed items remain the canonical style

Callout/code
callout.kind must be in the closed core set

code.language is optional

code.text must use multiline string form

multiline string syntax becomes a core Doctrine feature, not a code-block hack

Guards
when expressions on document blocks use the same expression language as output guards

document guards may not read forbidden sources any more than guarded outputs may

13. Renderer rules
These are worth spelling out because they determine readability.

Top-level agent fields still start at heading depth 2.

SectionBlock increments heading depth.

ListBlock, DefinitionsBlock, TableBlock, CalloutBlock, CodeBlock, and RuleBlock do not increment heading depth.

One blank line separates sibling blocks.

No empty heading shells.

Inline code formatting remains authored responsibility.

definitions uses the compact one-line form when the definition body is a single paragraph.

callout renders with blockquote syntax, not heading syntax.

Existing emphasized lines keep their current rendering for backward compatibility unless explicitly rewritten as callout.

Contract view emits the italic metadata line:

_Required · section_

_Required · table · when walkthrough is in scope_

_Advisory · code · json_

That single italic status line does a lot of work and is much nicer than repeated deeper headings.

14. Implementation plan
Touch these files:

doctrine/grammars/doctrine.lark

doctrine/model.py

doctrine/parser.py

doctrine/compiler.py

doctrine/renderer.py

examples/** render-contract corpus and compile-negative corpus

Those are the right files because the current heading-only behavior is encoded in the renderer, and the declaration/body structure is defined in the grammar, parser, model, and compiler. 

 


Concrete compiler changes
model.py

add DocumentDecl

add document block node types

add multiline string node if you introduce triple-quoted strings

compiler.py

replace CompiledSection-only readable tree with a richer compiled block union

map old keyed sections to SectionBlock

compile structure: refs on inputs/outputs

compile document addressable roots

renderer.py

replace _render_section() recursion as the only path

add block dispatch:

_render_section_block

_render_list_block

_render_definitions_block

_render_table_block

_render_callout_block

_render_code_block

_render_rule_block

doctrine.lark

add document_decl

add rich block items to document bodies

add rich block items to record/workflow section bodies

add multiline string literal

15. Acceptance corpus to add
I would add new example folders starting at 54:

54_first_class_documents

55_rich_blocks_in_output_contracts

56_documents_with_tables_and_definitions

57_document_inheritance

58_document_guards

59_multiline_strings_and_code_blocks

And compile-negatives like:

INVALID_STRUCTURE_REF_NON_DOCUMENT.prompt

INVALID_DOCUMENT_DUPLICATE_BLOCK_KEY.prompt

INVALID_DOCUMENT_OVERRIDE_KIND_MISMATCH.prompt

INVALID_TABLE_ROW_UNKNOWN_COLUMN.prompt

INVALID_TABLE_WITHOUT_COLUMNS.prompt

INVALID_CALLout_UNKNOWN_KIND.prompt

INVALID_CODE_BLOCK_WITHOUT_MULTILINE_STRING.prompt

That fits the way Doctrine already proves new surfaces through exact render contracts and fail-loud corpus cases. 


16. What not to add in v1
To keep the feature elegant instead of sprawling:

Do not add raw markdown escape-hatch blocks in v1.
Do not add HTML-specific constructs in v1.
Do not add footnotes, images, or nested tables in v1.
Do not put lesson-specific table names or semantics in Doctrine core.

For diagrams later, a fenced code block with language: mermaid is enough. That keeps the core language small.

17. The crisp version
If I collapse this to one sentence:

Doctrine should gain a first-class document declaration plus a shared rich-readable-block system, so headings are only one block type among many, and markdown structure becomes semantic rather than indentation-shaped.

That gives you:

real tables

real numbered lists

compact field-definition surfaces

real callouts

code fences

conditional document blocks

inherited reusable document schemas

addressable document paths

output contracts that read like documents instead of heading archaeology

And it does it in a way that matches the rest of Doctrine’s design rather than sneaking a markdown formatter in through the back door. 

 













repomix-lessons-doctrine-context.md
File

LESSONS_SYMBOLIC_DOCTRINE_PORT_IMPLEMENTATION_PLAN_2026-04-10.md
File
I'm in the process of porting our lessons agents to use some of the new doctrine features as you can see from the work plan.

However even on the other side of that there will be a huge amount of just prose in the lesson agents that can drift.

I'd like to eliminate almost all of the prose but preserve the intent of the agent on the output side.

Tell me what the most elegant language features I should add to achieve that are, and what should go into the lessons agents level vs what should go into doctrine. Give me specific examples including before/after on both the prompt and output AGENTS.md level.

I’m pulling the current Doctrine feature surface and the Lessons work plan together first, then I’ll turn that into a concrete split between language features and agent-local doctrine.

I’ve isolated the main drift seams now: currentness, metadata mode, route-only turns, review, preservation, and out-of-scope title handling. The common pattern is prose carrying state, scope, routing, and preservation law, so I’m turning those into concrete Doctrine-vs-Lessons before/after examples.



repomix-lessons-doctrine-context.md
File

LESSONS_SYMBOLIC_DOCTRINE_PORT_IMPLEMENTATION_PLAN_2026-04-10.md
File
I'm in the process of porting our lessons agents to use some of the new doctrine features as you can see from the work plan.

However even on the other side of that there will be a huge amount of just prose in the lesson agents that can drift.

I'd like to eliminate almost all of the prose but preserve the intent of the agent on the output side. The output should not become overly concise it's the input side that we're trying to formalize. The output agent should read naturally.

Tell me what the most elegant language features I should add to achieve that are, and what should go into the lessons agents level vs what should go into doctrine. Give me specific examples including before/after on both the prompt and output AGENTS.md level.

The design principle is clear now: don’t chase brevity for its own sake—promote any prose that is secretly schema into Doctrine, and leave only taste and judgment at the Lessons layer.

That sharpens the split further: make semantics compiler-owned on the authoring side, but preserve human-owned taste in the rendered AGENTS.md. I’m pulling the most reusable syntax patterns from the existing doctrine surface so the proposals extend your current language cleanly.

I’m keeping that second criterion front and center now: source prompts can become almost fully symbolic, but the rendered AGENTS.md still needs to read richly and naturally.

Thought for 30m 48s
Your work plan is already aiming at the right class of problem: the remaining drift is mostly semantic prose masquerading as instruction, not missing tone. The plan explicitly calls out shared output carriers, metadata mode/currentness, route-only turns, critic verdict mechanics, and preservation/invalidation as the seams that should move into typed Doctrine surfaces, while keeping mission, rationale, and judgment-heavy quality bars in prose. It also makes “human-readable emitted homes” a hard requirement, so the right move is more structure in source, not terser runtime output. 

 


The most elegant direction is:

Add first-class analysis blocks for repeated reasoning choreography.

Add artifact schemas with semantic gates, not just headings.

Add review families so critic logic is inherited and patched, not recopied.

Add route-only handoff schemas so routing comments stop carrying hidden law.

Add grounding protocols so wording-safe behavior is declarative.

Add readback render profiles so all that formal source still expands into natural AGENTS.md prose.

The key boundary is simple:

Doctrine should own anything that is structurally true across many roles or many teams: currentness, routing, preservation, invalidation, gated review, grounding protocol shape, analysis step ordering, trust surfaces, and render policy. The plan already points in exactly that direction with richer carriers, typed mode binding, route-only workflow law, first-class review, and typed preservation/invalidation. 


Lessons should own anything that is domain truth or family-specific judgment: poker meaning, which upstream artifacts are authoritative, what “same-route similar-burden” means, the 90–120s pacing corridor, exact-move boundaries, anti-leak heuristics, section/lesson document names, and the SOUL / role identity. The current metadata workflow is a good example: Doctrine should provide the shape, while Lessons owns lesson-title mode, section mode, metadata_route_facts, and the specific preserve/rewrite rules. 

 


The strongest design rule is: Doctrine owns the grammar of the move; Lessons owns the specific game being played.

1) Add analysis: as a first-class construct
This is the biggest missing piece after your current port plan.

Right now, large parts of LessonsLessonArchitect and similar lanes are still procedural prose: restate the lesson job, assign step roles, build nearby-lesson evidence, compare real comparable lessons, defend pacing, build step arc, then mark stable vs variable. That is clearly not “tone”; it is a reusable reasoning program. 

 


What Doctrine should add
A construct like:

analysis LessonPlanning: "Lesson Planning"
    basis:
        section_lesson_map
        section_concepts_terms
        section_playable_strategy

    stages:
        lesson_job:
            derive lesson_promise from {section_lesson_map, section_concepts_terms, section_playable_strategy}

        step_roles:
            classify step_order as StepRole
            require explicit

        continuity:
            compare nearby_lessons as prior_lessons_step_count

        comparables:
            compare accepted_lessons same_route similar_burden
            fallback least_wrong_fit
            export real_comparable_lessons

        pacing:
            defend target_duration 90..120s

        step_arc:
            derive step_arc_table
            derive guidance_plan

        boundaries:
            preserve decisions {section_lesson_map, section_playable_strategy}
            forbid invented_route
            export stable_vs_variable
What stays in Lessons
StepRole, the 90–120s corridor, what counts as “same-route”, what counts as “least-wrong fit”, and which basis files matter.

Before: prompt surface
workflow LessonPlanAnalysisSteps: "Lesson Plan Analysis Steps"
    "Restate in plain English what this lesson owns..."
    "Name what each step is doing using `introduce`, `practice`, `test`, or `capstone`..."
    "Build nearby-lesson evidence..."
    "Find real comparable lessons..."
    "Use current lesson data to defend the lesson's size..."
    "Build the `Step Arc Table`..."
    "Say what must stay stable and what may vary safely..."
After: prompt surface
enum StepRole: "Step Role"
    introduce: "introduce"
    practice: "practice"
    test: "test"
    capstone: "capstone"

analysis LessonPlanning: "Lesson Planning"
    basis:
        section_lesson_map
        section_concepts_terms
        section_playable_strategy

    stages:
        lesson_job:
            derive lesson_promise

        step_roles:
            classify steps as StepRole
            require explicit

        continuity:
            compare nearby_lessons as prior_lessons_step_count

        comparables:
            compare accepted_lessons same_route similar_burden
            fallback least_wrong_fit

        pacing:
            defend target_duration 90..120s

        step_arc:
            derive step_arc_table
            derive guidance_plan

        boundaries:
            preserve decisions {section_lesson_map, section_playable_strategy}
            forbid invented_route
Before: emitted AGENTS.md
## Lesson Plan Analysis Steps

### Step 1 - Restate The Lesson Job

Restate in plain English what this lesson owns, what it defers, and what is genuinely new here.

### Step 2 - Set The Step Roles

Name what each step is doing using `introduce`, `practice`, `test`, or `capstone` before you defend pacing.

### Step 3 - Set The Guidance Plan

Say how much help each step or step group should give.
...
After: emitted AGENTS.md
## Lesson Planning

Plan the lesson from the approved section lesson map, concepts file, and playable strategy.

### What To Decide

First restate the lesson promise.
Then give every step one explicit role: introduce, practice, test, or capstone.
Use nearby lessons for continuity evidence.
Use real same-route lessons of similar burden for comparable evidence, and name any fallback plainly.
Defend the final size against the 90–120s pacing corridor.
Make the step arc, guidance taper, and stable-versus-variable boundaries explicit.

Do not invent a new route or reopen upstream concept or playable decisions.
That is exactly the shape you want: formal source, natural output.

2) Add schema: or richer artifact contracts with semantic gates
Your current review contracts still spend enormous prose budget on “At minimum confirm…” because headings alone are not enough. The plan itself calls out preservation/invalidation as a remaining drift seam, and it explicitly wants exact shared-contract gate export in review. 

 


The existing Doctrine examples already prove that structured scope/preservation can render naturally: current artifact, own only, preserve exact, and preserve structure show up as readable sentences in the emitted home. 


What Doctrine should add
A richer document schema surface:

schema LessonPlanContract: "Shared Lesson Plan Contract"
    sections:
        lesson_promise: "Lesson Promise"
        step_order: "Step Order"
        step_roles: "Step Roles" as StepRole[]
        prior_lessons_step_count: "Prior-Lessons Step-Count Table"
        real_comparable_lessons: "Real Comparable Lessons"
        step_arc_table: "Step Arc Table"
        guidance_plan: "Guidance Plan"
        stable_vs_variable: "Stable Vs Variable"

    gates:
        explicit step_roles
        comparable_lessons not count_only_similarity
        preserve route from section_lesson_map
        stable_vs_variable explicit
What stays in Lessons
The actual sections, the domain gate names, and the meaning of “count-only similarity” or “route preservation”.

Before: prompt surface
## Shared Lesson Plan Review Contract

At minimum confirm the file has non-empty `Lesson Promise`, `Step Order`, `Step Roles`, ...
At minimum confirm the lesson does not leave `introduce`, `practice`, `test`, or `capstone` semantics implied in prose.
At minimum confirm `Real Comparable Lessons` uses real comparable lessons...
At minimum confirm the lesson plan stays inside the route already approved upstream...
After: prompt surface
schema LessonPlanContract: "Shared Lesson Plan Contract"
    sections:
        lesson_promise: "Lesson Promise"
        step_order: "Step Order"
        step_roles: "Step Roles" as StepRole[]
        real_comparable_lessons: "Real Comparable Lessons"
        stable_vs_variable: "Stable Vs Variable"

    gates:
        explicit step_roles
        real_comparable_lessons same_route_or_named_fallback
        no invented_route
        stable_vs_variable explicit
Before: emitted AGENTS.md
## Shared Lesson Plan Review Contract

At minimum confirm the file has non-empty `Lesson Promise`, `Step Order`, `Step Roles`, ...
At minimum confirm the lesson does not leave `introduce`, `practice`, `test`, or `capstone` semantics implied in prose.
...
After: emitted AGENTS.md
## Shared Lesson Plan Review Contract

Confirm that the lesson plan contains the full lesson promise, step order, explicit step roles, comparable-lesson proof, and stable-versus-variable boundaries.

Fail review if step roles are only implied, if comparable proof is only count similarity, or if the plan quietly invents a new route.
This is a much better compression ratio because you are compressing schema, not flattening meaning.

3) Add review family inheritance as a first-class surface for Critic
The plan is blunt here: the critic still repeats local review scaffolds and should move to a shared abstract review base plus concrete patches. That is the biggest remaining prose bucket. 


What Doctrine should add
You already have review and abstract review inheritance. The elegant next step is a specialized inheritance model for recurring review families: handoff-first blocking, failing-gate export, current-truth handling, and routed next-owner logic should live once.

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
Then patch per artifact:

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
What stays in Lessons
The subjects, contracts, next-owner map, and any review posture that is genuinely judgmental rather than mechanical. The plan explicitly says critic independence, handoff-first stops, and “do not rewrite that producer truth here” should remain prose. 


Before: prompt surface
## Lesson Plan Review Rules
### Start Review
Read the producer's handoff comment...
### Verdict Rules
`accept` means...
`changes requested` must...
### Who It Goes Back To
For lesson-plan problems...
After: prompt surface
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
Before: emitted AGENTS.md
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
After: emitted AGENTS.md
## Lesson Plan Review

Review subject: Lesson Plan.
Start with the producer handoff. If it does not clearly name the current lesson plan, stop there and send it back before content review begins.

### Contract Gates

Reject: Step Roles are still implied.
Reject: The lesson plan invents a new route.
Accept only if the shared lesson-plan contract passes.

### If Accepted

Current artifact: Lesson Plan.
Route to LessonsSituationSynthesizer.

### If Rejected

If review blocked before content review began, there is no current artifact for this outcome.
Otherwise the current artifact remains Lesson Plan.
Route to LessonsLessonArchitect.
That is dramatically cleaner, and it preserves natural output.

4) Add a first-class route_only: construct
Your current LessonsProjectLead source shows the exact problem: some semantics are already in law:, but a lot of coordination truth is still narrated around repeated critic misses, metadata debt, and what the routing comment must carry. 


The plan explicitly says this seam should become typed current none, guarded readback, and next-owner coupling. 


What Doctrine should add
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
What stays in Lessons
The next-owner enum, the exact labels like Repeated Problem, and the local explanation of metadata debt boundaries.

Before: prompt surface
workflow RouteOnlyTurns: "Routing-Only Turns"
    "Use this route when no specialist output file is current yet..."
    "Keep the current issue plan and the current issue comment explicit..."
    "When the same critic miss comes back again..."
    law:
        active when ...
        current none
        stop ...
        route ...
After: prompt surface
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
Before: emitted AGENTS.md
## Routing-Only Turns

Use this route when no specialist output file is current yet...
When the same critic miss comes back again, put one short `Repeated Problem` section...
If it is still unclear which specialist should go next...
After: emitted AGENTS.md
## Routing-Only Turns

Use this turn when no specialist artifact is current and the live job is routing, process repair, or owner repair.

There is no current artifact for this turn.

Keep the current issue plan and the routing comment explicit about the next owner and the next step.
When the same critic miss repeats, add a short Repeated Problem section that says what keeps failing, which role it came back from, and the next concrete fix.
If the next specialist owner is still not justified, keep the issue on LessonsProjectLead.
That preserves warmth while moving the logic out of prose.

5) Add grounding: protocols
Metadata and copy still carry real algorithmic law in prose: start from the current wording unless rewrite, do not do draft-first grounding, ask one narrower question if needed, and route upstream rather than freewrite when receipts are missing. That is not just style guidance. 


Doctrine should own
A generic grounding protocol surface:

grounding WordingGrounding: "Wording Grounding"
    source: poker_kb_interface
    target: wording

    policy:
        start_from current_wording unless rewrite
        forbid draft_first
        allow one_narrower_followup
        if unresolved -> route LessonsProjectLead
Lessons should own
Which skill is used, what counts as a safe receipt, and which fields are “teaching wording” versus cosmetic wording.

This would let you delete a shocking amount of repeated copy/metadata prose without flattening the behavior.

6) Add render_profile: / readback templates
This is the feature that makes the whole plan work.

The plan is adamant that emitted homes must stay direct and human-readable. The existing bound-scope example already proves that structured law can render as natural sentences like “Current artifact: Section Metadata.”, “Own only …”, and “Preserve exact … except …”. 


So do not let the renderer mirror the AST mechanically. Give Doctrine a render profile layer, for example:

render_profile LessonsHome:
    current_artifact -> sentence
    own_only -> sentence
    preserve_exact -> sentence
    review.contract_checks -> titled_section
    analysis.stages -> natural_ordered_prose
    guarded_sections -> concise_explanatory_shell
Doctrine owns the rendering primitives. Lessons owns the profile selection and any family-specific wording choices.

That gives you the crucial separation:

source becomes highly formal,

output remains readable, full, and natural.

What I would put in Doctrine vs Lessons
Put in Doctrine core

analysis

richer schema / semantic document contracts

review family inheritance

route_only

grounding

render_profile

stronger preserve, invalidate, support_only, ignore rewrite_evidence, current artifact via trust_surface

These are all reusable control-plane semantics, and your plan already identifies them as the correct layer for Doctrine to own. 

 


Put in lessons common/contracts

StepRole

MetadataMode

ProjectLeadRouteOnlyNextOwner

SolverFit

ExactMoveBoundary

the 90–120s pacing corridor

“same-route similar-burden”

which artifacts are preserve bases

specific review gates for lesson plan / situations / materialization / copy / metadata

Keep as prose in lessons agents

role identity and SOUL

poker-teaching taste bars

the few judgment calls that are genuinely not compile-checkable

warnings that exist because humans make repeated mistakes, not because the system lacks a semantic shape

A good test is:
If it should compile-fail, route-fail, or render consistently across many lanes, it belongs in Doctrine.
If it encodes poker pedagogy, corridor taste, or role temperament, it belongs in Lessons.

The shortest path to value
I would add only three new surfaces first:

analysis:

schema: with semantic gates

render_profile:

Then I would use them on:

LessonsLessonArchitect

LessonsAcceptanceCritic

LessonsProjectLead

That matches your current plan’s biggest drift buckets and should remove the most prose while keeping AGENTS.md natural and even more readable than it is now. 

 


The next experiment I’d run is: formalize LessonsLessonArchitect with analysis: first, because its current prompt is visibly procedural prose, and the emitted home has a clear before/after readability test. Then formalize the critic with a shared review family. That sequence gives you the largest drift reduction with the cleanest cold-read signal.

Branched from Porting Lesson Agents


Great, now turn this into a full implementation-ready specification in exhaustive detail so I can just implement it as you spec it out for me. Include a mini ladder of examples that would demonstrate the language features one at a time, so it's well explained in our example set and I don't have to build the whole thing. And to see it working, I can build the examples, build the compiler features.

Thought for 26m 22s
Below is the implementation spec I would use. It is grounded in the current Lessons prompt surface, the active symbolic-port plan, and the shipped Doctrine grammar/example corpus, not in a hypothetical redesign. 

 

 

 

 


The first important constraint is sequencing. The active plan is still incomplete: route-only workflow-law for Project Lead is blocked, critic first-class review has not landed, and producer preservation/invalidation still remains to be ported. The plan is also explicit that this is not a compression pass, that shipped Doctrine features should be used before inventing new layers, and that one owner per seam / one live route per seam must remain invariant. So I would treat the spec below as the layer that comes immediately after finishing the current parity plan, not as a replacement for it. 

 


The second important constraint is scope. The current Lessons pack already shows where the remaining prose actually lives: metadata is already close to the right typed seam; Lesson Architect still carries a large numbered planning program in prose; Project Lead still carries route-only coordination largely as narrated behavior; and Acceptance Critic still repeats review families and gate prose over and over. Doctrine already has a clear pattern for top-level declaration kinds, inheritance, enums, law, trust surfaces, review, guarded sections, and example-based rollout. So the right move is not to add lots of lesson-specific primitives. It is to add a very small number of new declaration surfaces that fit the existing language shape. 

 


My recommendation is:

Finish the current parity plan exactly as scoped.

Add two new core surfaces: analysis and schema.

Defer anything else until those two have been used to rewrite the worst prose-heavy lanes.

That is the minimal elegant expansion.

1. What belongs in Doctrine vs what belongs in Lessons
Doctrine core should own

A first-class analysis declaration for structured reasoning programs.

A first-class schema declaration for document section inventories and later gate catalogs.

Output attachment for schemas.

Natural rendering rules for both, so source becomes formal while AGENTS.md stays readable.

Inheritance, patching, and name-resolution behavior for both, matching existing Doctrine patterns.

Nothing lesson-specific beyond those surfaces.

Lessons common should own

StepRole, MetadataMode, SolverFit, route labels, and any other closed vocabularies.

Lesson-plan schema, section-map schema, metadata schema, dossier schema, and so on.

Analysis declarations like LessonPlanning, SectionArchitectureAnalysis, PlayableStrategyAnalysis.

The actual meaning of “same-route”, “similar-burden”, “90–120s corridor”, “capstone route”, “exact-move boundary”.

Local lesson agents should own

Mission and role identity.

Judgment-heavy quality bars.

Rare exceptions, stop lines, and local taste notes.

Anything that is still genuinely human judgment rather than stable workflow law or output structure.

Do not add to Doctrine

route_only as a new declaration kind. Existing workflow law already covers it and the active plan is explicitly porting that seam there. 


review_family as a new declaration kind. Existing abstract review plus shared review patches are already the right surface.

StepRole, LessonRoute, MetadataMode, or any poker-specific enum as core language features.

Auto-validation of authored Markdown artifacts. That is a different system. This spec is about instruction structure, not markdown parsing.

2. The design thesis
The prose you still want to kill falls into two buckets.

The first bucket is procedural prose:
“Restate the lesson job, then set step roles, then build nearby-lesson evidence, then comparable proof, then defend pacing…”

That should become analysis.

The second bucket is inventory / gate prose:
“At minimum confirm the file has non-empty X, Y, Z…”
or
“This output must include A, B, C…”

That should become schema.

Everything else should continue to use the surfaces you already have:

workflow law for routes, currentness, preservation, invalidation

review for critic semantics

outputs for durable carriers

prose for mission and judgment

That split lines up exactly with the current plan’s target architecture: prose for mission and taste, workflow law for route/currentness/preservation/invalidation, review law for verdict/current truth/next-owner coupling. 

 


3. Feature 1: analysis
3.1 Purpose
analysis is a renderable declaration for structured reasoning steps.

It exists to replace long numbered procedural sections like the current Lesson Plan Analysis Steps in LessonsLessonArchitect with a compact, typed, reusable surface while still rendering to natural AGENTS.md prose. The current lesson-architect prompt is the clearest example of a lane whose source is still carrying a reasoning program in prose. 


3.2 Non-goals
analysis does not:

execute anything

infer results

validate produced artifacts

replace review

replace workflow law

become a general-purpose programming language

It is an authored structure with compiler-owned rendering and reference validation.

3.3 Surface syntax
Add a new top-level declaration:

analysis LessonPlanning: "Lesson Planning"
    upstream_truth: "Upstream Truth"
        SectionLessonMap
        SectionConceptsAndTerms
        SectionPlayableStrategy

    lesson_job: "Lesson Job"
        derive "Lesson Promise" from {SectionLessonMap, SectionConceptsAndTerms, SectionPlayableStrategy}
        "Do not invent a new lesson route here."

    step_roles: "Step Roles"
        classify "Step Roles" as StepRole

    comparable_proof: "Comparable Proof"
        compare "Real Comparable Lessons" against {RecentLessonContinuityContext, AcceptedLessonComparables}
        "Start with same-route, similar-burden lessons."

    pacing: "Size And Pacing"
        defend "90–120s corridor" using {SectionLessonMap, RecentLessonContinuityContext, AcceptedLessonComparables}
3.4 Grammar changes
Add analysis_decl as a top-level sibling of workflow_decl and review_decl.

Proposed grammar extension:

?declaration: import_decl
            | workflow_decl
            | analysis_decl
            | abstract_review_decl
            | review_decl
            | skills_decl
            | inputs_decl
            | input_source_decl
            | input_decl
            | outputs_decl
            | output_target_decl
            | output_shape_decl
            | output_decl
            | json_schema_decl
            | skill_decl
            | enum_decl
            | schema_decl
            | abstract_agent
            | agent

analysis_decl: "analysis" CNAME inheritance? ":" string _NL _INDENT analysis_body _DEDENT

analysis_body: analysis_body_line+
analysis_body_line: analysis_string
                  | analysis_section
                  | analysis_inherit
                  | analysis_override_section

analysis_string: prose_line _NL?

analysis_section: CNAME ":" string _NL _INDENT analysis_section_body _DEDENT
analysis_inherit: "inherit" CNAME _NL?
analysis_override_section: "override" CNAME ":" string? _NL _INDENT analysis_section_body _DEDENT

analysis_section_body: analysis_section_item+
?analysis_section_item: prose_line _NL?
                      | workflow_section_ref_item
                      | derive_stmt
                      | classify_stmt
                      | compare_stmt
                      | defend_stmt

derive_stmt: "derive" string "from" path_set_expr _NL
classify_stmt: "classify" string "as" name_ref _NL
compare_stmt: "compare" string "against" path_set_expr compare_using_clause? _NL
compare_using_clause: "using" expr_set
defend_stmt: "defend" string "using" path_set_expr _NL
3.5 Why this grammar
This is intentionally narrow:

it mirrors existing workflow inheritance and section structure

it reuses existing addressable refs, enums, and path sets

it adds only four verbs

Those four verbs cover the vast majority of prose-heavy lesson analysis:

derive

classify

compare

defend

Anything still judgment-heavy stays as ordinary prose lines inside the same analysis section.

3.6 AST / model additions
Add model types parallel to workflow types:

@dataclass(slots=True, frozen=True)
class AnalysisDecl:
    name: str
    body: AnalysisBody
    parent_ref: NameRef | None = None

@dataclass(slots=True, frozen=True)
class AnalysisBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[AnalysisItem, ...]

@dataclass(slots=True, frozen=True)
class AnalysisSection:
    key: str
    title: str
    items: tuple[AnalysisSectionItem, ...]

@dataclass(slots=True, frozen=True)
class AnalysisInherit:
    key: str

@dataclass(slots=True, frozen=True)
class AnalysisOverrideSection:
    key: str
    title: str | None
    items: tuple[AnalysisSectionItem, ...]

@dataclass(slots=True, frozen=True)
class DeriveStmt:
    target_title: str
    basis: LawPathSet

@dataclass(slots=True, frozen=True)
class ClassifyStmt:
    target_title: str
    enum_ref: NameRef

@dataclass(slots=True, frozen=True)
class CompareStmt:
    target_title: str
    basis: LawPathSet
    using_expr: Expr | None = None

@dataclass(slots=True, frozen=True)
class DefendStmt:
    target_title: str
    basis: LawPathSet
3.7 Name resolution rules
analysis should be treated as a renderable declaration:

allowed as an agent authored slot value

allowed as an override slot: AnalysisName

allowed as a workflow use target if you want composition parity with workflows

It should not be allowed:

as a review: target

as an inputs: / outputs: / skills: block target

as an output schema: target

Inside analysis:

ordinary bare refs and path refs use the existing addressable resolution rules

classify ... as <name_ref> must resolve to an enum declaration

derive, compare, defend path sets must resolve using the same law-path rules you already have for preserved scope and support-only comparison

3.8 Inheritance rules
analysis should inherit exactly like workflows:

keyed sections only

inherit <section_key>

override <section_key>:

missing inherited sections are compile errors

overriding unknown sections is a compile error

Do not invent a separate merge model.

3.9 Render rules
The renderer should keep output natural and non-symbolic.

For analysis:

declaration title renders as an H2 section

each keyed section renders as an H3

prose lines render normally

bare refs render as bullets using existing title resolution

typed statements render as natural sentences

Exact rendering templates:

derive "Lesson Promise" from {A, B, C}
-> Derive Lesson Promise from A, B, and C.

classify "Step Roles" as StepRole
-> Classify Step Roles using Step Role.

compare "Real Comparable Lessons" against {A, B}
-> Compare Real Comparable Lessons against A and B.

compare "Real Comparable Lessons" against {A, B} using {ComparableRule.same_route, ComparableRule.similar_burden}
-> Compare Real Comparable Lessons against A and B. Use same_route and similar_burden as the comparison basis.

defend "90–120s corridor" using {A, B, C}
-> Defend 90–120s corridor using A, B, and C.

This is the key output-side requirement: the source becomes symbolic, but the rendered AGENTS.md still reads like guidance, not bytecode.

3.10 Diagnostics
Reserve a new error range for analysis, for example E501–E519.

Minimum diagnostics:

E501 unknown analysis enum target

E502 non-addressable or unresolved path in analysis basis

E503 invalid analysis inheritance target

E504 duplicate analysis section key

E505 analysis used in unsupported surface

E506 empty basis in derive/compare/defend

3.11 First migrations for analysis
Land analysis first in:

LessonsLessonArchitect

LessonsSectionArchitect

LessonsPlayableStrategist

Those three are the highest-value prose-heavy producers in the current Lessons family. LessonsLessonArchitect is the cleanest first migration because its source already exposes a long, ordered planning program that maps naturally into stage sections. 


4. Feature 2: schema
4.1 Purpose
schema is a non-renderable contract declaration that centralizes:

required document sections

later, optional review gates

It exists to replace large repeated section inventories and shared “must include” prose.

4.2 Phase split
Implement schema in two subphases.

Phase 1

sections only

attach to outputs

no review integration yet

Phase 2

add optional gates

allow review contract: to target a schema

This phased split matters because it keeps the first implementation small and lets you use it immediately on producer/output seams without waiting for critic integration.

4.3 Surface syntax
Phase 1:

schema LessonPlanSchema: "Lesson Plan Schema"
    sections:
        lesson_promise: "Lesson Promise"
            "State what this lesson owns now."

        step_order: "Step Order"
            "State the step order and what each step is there to teach."

        step_roles: "Step Roles"
            "Name what each step is doing using introduce, practice, test, or capstone."

        real_comparable_lessons: "Real Comparable Lessons"
            "Name the exact comparable lessons used."

        stable_vs_variable: "Stable Vs Variable"
            "State what later lanes must keep stable and what may vary safely."
Attach it to an output:

output LessonPlanFile: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: MarkdownDocument
    requirement: Required
    schema: LessonPlanSchema
Phase 2:

schema LessonPlanSchema: "Lesson Plan Schema"
    sections:
        ...
    gates:
        explicit_step_roles: "Explicit Step Roles"
            "Fail if introduce, practice, test, or capstone are only implied in prose."

        no_new_route: "No New Route"
            "Fail if the plan quietly invents a new lesson route."

        stable_route_skeleton: "Stable Route Skeleton"
            "Fail if Stable Vs Variable leaves the inherited route skeleton too vague."
4.4 Grammar changes
Add a top-level declaration and one reserved output field.

?declaration: ...
            | schema_decl
            | ...

schema_decl: "schema" CNAME inheritance? ":" string _NL _INDENT schema_body _DEDENT

schema_body: schema_item+
?schema_item: schema_string
            | schema_sections_block
            | schema_gates_block
            | schema_inherit
            | schema_override_sections
            | schema_override_gates

schema_string: prose_line _NL?

schema_sections_block: "sections" ":" _NL _INDENT schema_section_item+ _DEDENT
schema_gates_block: "gates" ":" _NL _INDENT schema_gate_item+ _DEDENT

schema_section_item: CNAME ":" string _NL schema_section_body?
schema_gate_item: CNAME ":" string _NL schema_gate_body?

schema_section_body: _INDENT block_lines _DEDENT
schema_gate_body: _INDENT block_lines _DEDENT

schema_inherit: "inherit" schema_block_key _NL?
schema_override_sections: "override" "sections" ":" _NL _INDENT schema_section_item+ _DEDENT
schema_override_gates: "override" "gates" ":" _NL _INDENT schema_gate_item+ _DEDENT

schema_block_key: "sections" | "gates"

output_body_line: output_record_item
                | trust_surface_block
                | output_schema_stmt

output_schema_stmt: "schema" ":" name_ref _NL?
Phase 2 review integration:

contract_stmt: "contract" ":" (workflow_ref | schema_ref) _NL?
schema_ref: name_ref
4.5 AST / model additions
@dataclass(slots=True, frozen=True)
class SchemaDecl:
    name: str
    body: SchemaBody
    parent_ref: NameRef | None = None

@dataclass(slots=True, frozen=True)
class SchemaBody:
    title: str
    preamble: tuple[ProseLine, ...]
    sections: tuple[SchemaSection, ...]
    gates: tuple[SchemaGate, ...] = ()

@dataclass(slots=True, frozen=True)
class SchemaSection:
    key: str
    title: str
    body: tuple[ProseLine, ...] = ()

@dataclass(slots=True, frozen=True)
class SchemaGate:
    key: str
    title: str
    body: tuple[ProseLine, ...] = ()

@dataclass(slots=True, frozen=True)
class OutputSchemaConfig:
    schema_ref: NameRef
4.6 Static rules
Phase 1:

a schema must declare at least one section

section keys are unique

output schema: must resolve to a schema declaration

an output may attach at most one schema

in phase 1, an output with schema: may not also carry a local must_include: block

That last rule is deliberate. Do not create two owners for the same inventory seam.

Phase 2:

gate keys are unique

review contract: may resolve to either a workflow review contract or a schema

contract.some_gate must resolve against the attached workflow-section keys or schema gate keys depending on contract kind

contract.passes remains valid for both kinds

4.7 Inheritance rules
schema should inherit like existing keyed block declarations:

whole-declaration inheritance via [ParentSchema]

inherit sections

override sections:

later, inherit gates / override gates:

This lets you keep a base LessonPlanSchema and derive WalkthroughLessonPlanSchema, CapstoneLessonPlanSchema, and so on, instead of pushing route-conditional inventory logic into the language too early.

That is a very important elegance point: use inheritance, not per-entry when, in the first version.

4.8 Render rules
Phase 1 output rendering:

## Outputs

### Lesson Plan File

- Target: File
- Path: `lesson_root/_authoring/LESSON_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

#### Required Sections

##### Lesson Promise

State what this lesson owns now.

##### Step Order

State the step order and what each step is there to teach.

...
Phase 2 review rendering when a schema is used as contract:

## Lesson Plan Review

Review subject: Lesson Plan File.
Shared review contract: Lesson Plan Schema.

### Contract Gate Checks

Reject: Explicit Step Roles.
Reject: No New Route.
Reject: Stable Route Skeleton.
Accept only if The lesson plan schema passes.
4.9 Diagnostics
Reserve E520–E539.

Minimum set:

E520 output schema ref unresolved

E521 duplicate schema section key

E522 duplicate schema gate key

E523 output declares both schema and must_include in phase 1

E524 review contract references unknown schema gate

E525 schema used in unsupported surface

E526 schema missing sections

4.10 First migrations for schema
Do this in order:

Lesson Plan File

Section Lesson Map File

Section Playable Strategy File

Section Concepts And Terms File

Section Dossier File

Those are the big section inventories. Metadata and copy can stay prose longer because they are smaller and more judgment-heavy.

5. What I would explicitly defer
I would not add these in the same wave:

5.1 No first-class grounding declaration yet
You can still formalize a lot of grounding behavior with existing workflow law plus shared skills. The repeated grounding prose is real, but analysis/schema will buy you far more first, with much less compiler surface.

5.2 No render_profile declaration yet
You do need natural output, but you can get that from built-in renderer templates for analysis and schema in the first iteration. User-authored rendering policy is second-wave work.

5.3 No special “lesson contract” or “step table” primitive
Those belong in lesson schemas and lessons analysis blocks, not core Doctrine.

6. Concrete before/after on the real Lessons surfaces
6.1 LessonsLessonArchitect before
Right now the prompt carries a long numbered analysis ladder in prose:

restate the lesson job

set the step roles

set the guidance plan

build nearby-lesson evidence

build real comparable lessons

decide size and pacing

build the step arc table

set stable and variable boundaries

map analysis to output

That is exactly the kind of prose analysis is for. 


6.2 LessonsLessonArchitect after
Prompt-side source:

enum StepRole: "Step Role"
    introduce: "introduce"
    practice: "practice"
    test: "test"
    capstone: "capstone"

analysis LessonPlanning: "Lesson Planning"
    upstream_truth: "Upstream Truth"
        SectionLessonMap
        SectionConceptsAndTerms
        SectionPlayableStrategy

    lesson_job: "Lesson Job"
        derive "Lesson Promise" from {SectionLessonMap, SectionConceptsAndTerms, SectionPlayableStrategy}
        "Start from the approved section-level concept allocation, not just the route."

    step_roles: "Step Roles"
        classify "Step Roles" as StepRole

    comparable_proof: "Comparable Proof"
        compare "Real Comparable Lessons" against {RecentLessonContinuityContext, AcceptedLessonComparables}
        "Start with same-route, similar-burden lessons. Name any fallback plainly."

    pacing: "Size And Pacing"
        defend "90–120s corridor" using {SectionLessonMap, RecentLessonContinuityContext, AcceptedLessonComparables}

    stability: "Stable Vs Variable"
        defend "Inherited route skeleton" using {SectionLessonMap, SectionPlayableStrategy}
        "Do not invent a new default, secondary, or capstone route here."

schema LessonPlanSchema: "Lesson Plan Schema"
    sections:
        lesson_promise: "Lesson Promise"
            "State what this lesson owns now."
        step_order: "Step Order"
            "State the step order and what each step is there to teach."
        step_roles: "Step Roles"
            "Name what each step is doing using introduce, practice, test, or capstone."
        prior_lessons_step_count_table: "Prior-Lessons Step-Count Table"
            "Make step-count continuity visible."
        step_arc_table: "Step Arc Table"
            "Make introduce, practice, test, new-concept placement, and coaching taper explicit."
        guidance_plan: "Guidance Plan"
            "Say how much help each step or step group should give."
        new_vs_reinforced_vs_deferred: "New Vs Reinforced Vs Deferred"
            "Name what is genuinely new, reinforced, and deferred."
        nearby_lesson_evidence: "Nearby-Lesson Evidence"
            "Keep nearby continuity evidence separate from comparable-lesson proof."
        real_comparable_lessons: "Real Comparable Lessons"
            "Name the exact comparable lessons used."
        why_not_shorter: "Why Not Shorter"
            "Explain what would be lost."
        why_not_longer: "Why Not Longer"
            "Explain why extra steps would exceed earned burden."
        stable_vs_variable: "Stable Vs Variable"
            "State what later lanes must keep stable and what may vary safely."

agent LessonsLessonArchitect:
    role: "You are Lessons Lesson Architect..."
    lesson_plan_analysis: LessonPlanning

    outputs: "Outputs"
        LessonPlanFile
Output-side rendered AGENTS.md:

## Lesson Planning

### Upstream Truth

- Section Lesson Map
- Section Concepts And Terms
- Section Playable Strategy

### Lesson Job

Derive Lesson Promise from Section Lesson Map, Section Concepts And Terms, and Section Playable Strategy.
Start from the approved section-level concept allocation, not just the route.

### Step Roles

Classify Step Roles using Step Role.

### Comparable Proof

Compare Real Comparable Lessons against Recent Lesson Continuity Context and Accepted Lesson Comparables.
Start with same-route, similar-burden lessons. Name any fallback plainly.

### Size And Pacing

Defend 90–120s corridor using Section Lesson Map, Recent Lesson Continuity Context, and Accepted Lesson Comparables.

### Stable Vs Variable

Defend Inherited route skeleton using Section Lesson Map and Section Playable Strategy.
Do not invent a new default, secondary, or capstone route here.

## Outputs

### Lesson Plan File

- Target: File
- Path: `lesson_root/_authoring/LESSON_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

#### Required Sections

##### Lesson Promise

State what this lesson owns now.

...
That is much smaller on the source side, but not terse on the output side.

6.3 LessonsAcceptanceCritic before
The critic still repeats artifact-by-artifact review prose and gate inventories. The active plan explicitly calls out first-class review as still unlanded and notes the repeated local review scaffolds as a major remaining prose bucket. 

 


6.4 LessonsAcceptanceCritic after current parity plan + later schema integration
Do not invent a new critic feature. Finish the current review port first. Then, in a second wave, let some artifact contracts point at schemas for gate catalogs.

That means the after-state should look like this structurally:

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
The important point is boundary:

review mechanics stay on Doctrine review

artifact section inventories / gate names move to schema

critic posture stays prose in the agent

6.5 LessonsMetadataCopywriter
Metadata is already the proving seam for typed mode, one-current-file law, exact preservation, and rewrite exclusions. The active plan explicitly treats it that way, and the current metadata prompt already shows the typed route-facts seam in practice. 

 


So I would not use metadata as the first analysis migration. Metadata is where you finish the current law port and keep the rest mostly as prose. Lesson planning and section architecture are the places where analysis pays off.

7. Mini ladder of examples
Your example ladder should start at 54, because the shipped corpus already runs through 53 and already covers the route-only/review/currentness/preservation family you are porting against. 


Example 54 — 54_analysis_basic
Goal
Introduce the new top-level analysis declaration and basic rendering.

What it proves

parser accepts analysis

analysis renders like a readable runtime section

keyed inheritance model mirrors workflow

derive and defend render naturally

Do not include yet

enums

schema

review integration

Prompt sketch

input CurrentBrief: "Current Brief"
    source: File
        path: "unit_root/BRIEF.md"
    shape: MarkdownDocument
    requirement: Required

analysis BriefingAnalysis: "Briefing Analysis"
    basis: "Basis"
        CurrentBrief

    promise: "Promise"
        derive "Briefing Promise" from {CurrentBrief}

    size: "Size"
        defend "Briefing Size" using {CurrentBrief}

agent AnalysisBasicDemo:
    role: "Keep planning structure readable without long numbered prose."
    planning: BriefingAnalysis
Expected render
A natural AGENTS.md section titled Briefing Analysis with stage headings and templated sentences.

Example 55 — 55_analysis_classify_compare
Goal
Add enum-aware classify and reference-aware compare.

What it proves

analysis verbs can resolve enum refs

analysis can render refs and comparisons cleanly

compiler errors fire on bad enum refs or empty basis

Add

enum StepRole

classify

compare

Prompt sketch

enum StepRole: "Step Role"
    introduce: "introduce"
    practice: "practice"
    test: "test"

analysis LessonShapeAnalysis: "Lesson Shape Analysis"
    roles: "Roles"
        classify "Step Roles" as StepRole

    comparables: "Comparable Proof"
        compare "Real Comparable Lessons" against {AcceptedLessonComparables, NearbyLessonContext}

agent AnalysisClassifyCompareDemo:
    role: "Keep lesson-shape analysis structured."
    analysis: LessonShapeAnalysis
Example 56 — 56_schema_output_contract
Goal
Add schema declarations and output attachment.

What it proves

parser accepts schema

output can declare schema:

renderer emits required sections from schema

output cannot simultaneously own must_include

Prompt sketch

schema LessonPlanSchema: "Lesson Plan Schema"
    sections:
        lesson_promise: "Lesson Promise"
            "State what this lesson owns now."
        step_order: "Step Order"
            "State the step order and what each step is there to teach."

output LessonPlanFile: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: MarkdownDocument
    requirement: Required
    schema: LessonPlanSchema
Example 57 — 57_schema_inheritance
Goal
Prove route- or mode-specific schema extension without adding conditional schema logic.

What it proves

schema inheritance works

separate variants are cleaner than dynamic conditional sections in v1

Prompt sketch

schema BaseLessonPlanSchema: "Lesson Plan Schema"
    sections:
        lesson_promise: "Lesson Promise"
            "State what this lesson owns now."
        step_order: "Step Order"
            "State the step order."

schema WalkthroughLessonPlanSchema[BaseLessonPlanSchema]: "Lesson Plan Schema"
    inherit sections

    override sections:
        lesson_promise: "Lesson Promise"
            "State what this lesson owns now."
        step_order: "Step Order"
            "State the step order."
        guided_walkthrough_beat_count_table: "Guided-Walkthrough Beat-Count Table"
            "Make walkthrough beat precedent explicit."
Example 58 — 58_lessons_lesson_architect_capstone
Goal
Show a near-real lessons migration of one prose-heavy lane.

What it proves

analysis works on a real-ish lesson planning lane

schema works on a real-ish lesson-plan output

output stays human-readable

Do not include yet

critic review integration

metadata mode

route-only

This is your first “real payoff” example.

Example 59 — 59_lessons_section_architecture_capstone
Goal
Apply the same pattern to section architecture.

What it proves

analysis scales beyond one lane

schemas can describe large structural outputs elegantly

inheritance can represent common versus capstone variants

Example 60 — 60_schema_review_contract
Optional second-wave example

Goal
Let review contract: target schemas with gates:.

What it proves

schema gate export integrates cleanly with first-class review

critic can reject on contract.some_gate

gate titles remain exact and readable

I would not build Example 60 until 54–59 are green.

8. Exact implementation order in the compiler
Step A — finish the active port plan
Resolve:

phase 3 route-only blocker

phase 4 critic review port

phase 5 producer preservation/invalidation sweep

Do that first or on a separate branch, because those are already active architecture changes. 

 


Step B — add analysis
Touch:

doctrine/grammars/doctrine.lark

doctrine/model.py

doctrine/parser.py

doctrine/compiler.py

doctrine/renderer.py

example 54

example 55

Do not touch lessons prompts yet.

Step C — add schema plus output attachment
Touch:

same core compiler files

example 56

example 57

Still do not touch lessons prompts yet.

Step D — migrate one real lessons lane
Touch:

LessonsLessonArchitect

a new lessons schema owner

a new lessons analysis owner

Cold-read emitted home. This is the actual payoff check.

Step E — migrate the second lane
Use LessonsSectionArchitect or LessonsPlayableStrategist.

Step F — only then consider schema-as-review-contract
That becomes example 60 and a later lessons critic refinement.

9. Concrete repo layout I would use
Add two new lesson-common folders:

doctrine/prompts/lessons/
  analyses/
    lesson_plan.prompt
    section_architecture.prompt
    playable_strategy.prompt
  schemas/
    lesson_plan.prompt
    section_lesson_map.prompt
    section_playable_strategy.prompt
    section_concepts_terms.prompt
    section_dossier.prompt
Why separate folders:

analyses/ are structured reasoning programs

schemas/ are structured artifact inventories

contracts/ remain the current home for review contracts and shared producer/reviewer truth during transition

That keeps Doctrine ownership crisp and avoids burying new surfaces inside old prose-heavy files.

10. The strict invariants
These are the rules I would enforce while implementing:

analysis is for process structure, not control flow.

schema is for artifact structure, not runtime routing.

Do not add lesson-specific core primitives.

Do not add a separate “review family” language when abstract review already exists.

Do not add conditional schema sections in v1; use inheritance.

Do not let outputs own both local must_include and schema: in the first release.

Do not let rendered AGENTS.md mirror source syntax literally; renderer should speak in natural sentences.

Do not promise automated validation of produced markdown artifacts. These features structure prompts; they do not inspect runtime authoring files.

11. The shortest path to seeing this work
I would implement and compile in this order:

54_analysis_basic

55_analysis_classify_compare

56_schema_output_contract

57_schema_inheritance

58_lessons_lesson_architect_capstone

At that point you will already know whether the language change is worth it, because the single worst prose-heavy lane will have collapsed into a compact symbolic source while the emitted AGENTS.md still reads naturally.

That is the cleanest place to stop, evaluate, and then decide whether schema should become a review contract too.






