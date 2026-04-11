---
status: drafting_artifact
artifact_role: pre-phase design input
superseded_by_phase_docs: true
---

> Drafting artifact note (2026-04-11): This standalone readable-markdown spec
> remains in the repo for provenance, but the implementation-order planning set
> now lives in the numbered phase docs under `docs/01_` through `docs/04_`.
> Treat this file as a pre-phase design input rather than the canonical phased
> plan.

# Readable Markdown And Document Rendering Spec

This document defines the readable-output layer for the proposed language
enhancement:

- the first-class `document` declaration
- the shared readable block sublanguage
- the richer compiled markdown block AST
- the rendering rules that keep emitted AGENTS.md and contract output natural
  instead of mechanically mirroring source nesting

The problem this work addresses is structural, not cosmetic.

The current renderer fundamentally walks nested compiled sections and turns
structure into deeper heading depth. Emphasized lines are the only real
non-heading format in the current surface. That means rich semantic differences
collapse into `##`, `###`, and `####`, and the output reads as outline depth
instead of document shape.

The correct abstraction is a typed markdown layer shared by all readable
Doctrine surfaces, with a first-class `document` declaration at the top and a
richer block AST underneath it.

## Core decision

Add a first-class readable document system to Doctrine, and make the markdown
renderer operate on semantic block kinds instead of only `section -> heading`.

The boundary is:

- Doctrine owns structure and rendering semantics.
- Domain packs own document names, required blocks, table names, and domain
  columns.

Doctrine should know what a table, sequence, definitions list, callout, code
block, and rule are.
Domain packs should decide that one particular table is called `Step Arc Table`
or `Guided-Walkthrough Beat-Count Table`.

## What ships

Ship one coherent feature, not a pile of renderer heuristics.

### New top-level declaration

```prompt
document LessonPlan: "Lesson Plan"
    ...
```

### New readable block kinds

The block kinds proposed for the readable-output layer are:

- `section` - heading plus block body
- `sequence` - ordered list
- `bullets` - unordered list
- `checklist` - task list
- `definitions` - compact term/explanation list
- `table` - markdown table
- `callout` - blockquote-style admonition
- `code` - fenced code block
- `rule` - thematic break

An earlier, smaller design sketch started with only:

- `document`
- `section`
- `sequence`
- `table`
- `callout`

The fuller rendering spec expands that set to cover the rest of the readable
surfaces that currently collapse into heading ladders.

### New attachment point on markdown-bearing contracts

Any markdown-bearing input or output contract may attach a document schema
through:

```prompt
structure: LessonPlan
```

### New renderer model

Replace the heading-only compiled output tree with a richer block AST:

```text
CompiledBlock =
    ParagraphBlock
    | SectionBlock
    | ListBlock
    | DefinitionsBlock
    | TableBlock
    | CalloutBlock
    | CodeBlock
    | RuleBlock
```

Existing authored sections compile to `SectionBlock`.
Existing emphasized prose lines compile to either an inline emphasized paragraph
or a `CalloutBlock` shell, depending on context.

An even richer rendering architecture explored during design work inserts an
explicit semantic readback layer first:

```text
Doctrine AST
    -> semantic readback IR
    -> typed markdown IR
    -> markdown text
```

That richer model is especially valuable for reviews, route-only comments, and
bounded-scope metadata panels because those surfaces want compact fact panels
and guarded comment blocks rather than more heading depth.

## Canonical document language spec

### `document`

A document is a named, addressable, inheritable schema for a markdown artifact.

Canonical form:

```prompt
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
```

Semantics:

- `document` is a readable declaration like workflow, skills, inputs, and
  outputs.
- it is an addressable root
- it can be inherited and explicitly patched
- it describes the internal structure of markdown artifacts
- it does not describe operational workflow law

### Common block header shape

All document blocks share this header shape:

```text
<block_kind> <key>: "Title" <requirement>? <guard>?
```

Where:

- `<block_kind>` is one of the supported block types
- `<key>` is the stable symbolic identifier
- `"Title"` is the rendered human title
- `<requirement>` is one of:
  - `required`
  - `advisory`
  - `optional`
- `<guard>` is:
  - `when <expr>`

Examples:

```prompt
section lesson_promise: "Lesson Promise" required
table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" required when LessonFacts.walkthrough_in_scope
callout durable_truth: "Durable Truth" advisory
```

The stable symbolic key is law.
The human title is prose.

### Block kinds

#### `section`

```prompt
section lesson_promise: "Lesson Promise" required
    "State what this lesson owns now."
```

Semantics:

- renders as a heading section
- body may contain any readable block

#### `sequence`

```prompt
sequence read_order: "Read Order" required
    first: "Read the active issue."
    second: "Read the current issue plan."
    third: "Read the latest current comment."
```

Semantics:

- renders as an ordered list
- body items render in authored order
- keyed items are recommended because they remain addressable

#### `bullets`

```prompt
bullets trust_surface: "Trust Surface" required
    artifact: "Current Artifact"
    active_mode: "Active Mode when present(active_mode)"
    trigger_reason: "Trigger Reason when present(trigger_reason)"
```

Semantics:

- renders as an unordered list

#### `checklist`

```prompt
checklist release_checks: "Release Checks" required
    lint: "Run lint."
    tests: "Run the minimum test suite."
    proof: "Confirm the proof artifact exists."
```

Semantics:

- renders as markdown task-list items

#### `definitions`

```prompt
definitions must_include: "Must Include" required
    verdict: "Verdict"
        "Say `accept` or `changes requested`."
    reviewed_artifact: "Reviewed Artifact"
        "Name the reviewed artifact this review judged."
    analysis: "Analysis Performed"
        "Summarize the review analysis that led to the verdict."
```

Semantics:

- renders as compact term/explanation rows
- this is the clean replacement for many current
  `#### Must Include -> ##### Field Name` ladders

#### `table`

```prompt
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
```

Optional fixed-row or sample-row form:

```prompt
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
```

Rules:

- columns are ordered and keyed
- rows are optional
- row cells must reference only declared columns
- cells are inline markdown only, not nested block bodies
- column bodies in schema mode are short descriptions used by the contract
  renderer

#### `callout`

```prompt
callout durable_truth: "Durable Truth" required
    kind: important
    "This file owns the lesson job, pacing, and stable-vs-variable boundaries."
```

Allowed `kind` values in v1:

- `required`
- `important`
- `warning`
- `note`

This callout vocabulary should align with the current emphasized prose
vocabulary instead of inventing a second admonition family.

#### `code`

```prompt
code example_manifest: "Example Manifest" advisory
    language: json
    text: """
    {
      "title": "PLACEHOLDER: Lesson title",
      "steps": []
    }
    """
```

This requires a new multiline string literal in Doctrine. That change is
worthwhile on its own because code fences and rich examples are clumsy without
it.

#### `rule`

```prompt
rule section_break
```

Semantics:

- renders as `---`

## Extended readable-output layer

The readable block layer should not be document-only.

The same rich block kinds should be legal anywhere Doctrine currently emits
readable markdown content, especially:

- `record_body`
- `output_record_body`
- `workflow_section_body`
- `skill_entry_body`

That matters because the rendering problem is broader than artifact files.
Output contracts and review comment contracts are also clunky for the same
reason.

For example, this current shape:

```prompt
output DraftReviewComment: "Draft Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    must_include: "Must Include"
        verdict: "Verdict"
            "Say whether the review accepted the draft or requested changes."
        reviewed_artifact: "Reviewed Artifact"
            "Name the reviewed artifact this review judged."
```

should be writable as:

```prompt
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
```

So the architectural rule is:

- `document` is the new top-level markdown schema declaration
- rich block kinds are a shared sublanguage reused by documents and other
  readable Doctrine bodies

## `structure:` attachment on inputs and outputs

For markdown-bearing contracts:

```prompt
input LessonPlanContract: "Lesson Plan"
    source: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: MarkdownDocument
    structure: LessonPlan
    requirement: Required
```

and:

```prompt
output LessonPlanFileOutput: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: AgentOutputDocument
    structure: LessonPlan
    requirement: Required
```

Rules:

- `structure:` must resolve to a `document`
- it is descriptive and typed, not a prose convention
- it may appear on input and output
- in the future it may also appear on reusable output-shape declarations, but
  v1 does not need that

This is especially valuable because the same named document can serve as:

- an upstream input contract
- a downstream output contract
- a review basis

## Addressability, interpolation, and refs

`document` and all keyed descendants should be addressable through the same
path discipline Doctrine already uses for records and workflows.

Examples:

```text
{{LessonPlan:title}}
{{LessonPlan:step_arc.title}}
{{LessonPlan:step_arc.columns.coaching_level.title}}
{{LessonPlan:step_arc.columns.coaching_level}}
```

Addressability rules:

- document root is addressable
- keyed block children are addressable
- table columns are addressable
- table rows are addressable when present
- anonymous list items are not addressable
- keyed list and definition items are addressable

## Inheritance and patching

`document` should inherit with the same explicit accounting doctrine as
workflows and IO blocks.

Example:

```prompt
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
```

Rules:

- inherited document blocks must be explicitly accounted for
- `override` may replace the body or title of a block
- block kind is invariant under override
- missing inherited block accounting is a compile error
- duplicate accounting is a compile error

## Guards and conditional blocks

Document blocks should support `when <expr>`.

Example:

```prompt
table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" required when LessonFacts.walkthrough_in_scope
    ...
```

Rules:

- guard syntax matches the existing expression syntax
- in contract render mode, guarded blocks render as conditional shells, not as
  runtime-evaluated presence
- expression visibility should reuse the same guard-expression restrictions as
  current guarded output sections
- a document block may not read emitted output fields directly through its
  guard

An earlier extension sketch also called out an explicit `guard` block kind as a
portable readable shell. The narrower document spec keeps `when <expr>` on
document blocks and avoids inventing a separate guard model.

## Backward compatibility

### Existing authored sections stay legal

Current readable keyed items:

```prompt
step_one: "Step One"
    "Say hello."
```

become semantic sugar for:

```prompt
section step_one: "Step One"
    "Say hello."
```

Old prompts do not need immediate rewrites.

### Existing emphasized lines stay legal

Current forms such as:

```prompt
required "Read this first."
important "Keep the current plan as truth."
```

remain legal and keep their current render behavior.

They may optionally compile to single-line callout blocks internally, but the
user-visible render should stay stable unless a prompt explicitly migrates to
blockquote callouts.

### Rich blocks are opt-in

Nothing breaks unless authors choose the new blocks.

## Markdown rendering spec

The key rendering rule is:

Only `section` consumes heading depth.
Everything else uses its own markdown syntax.

### Section

Contract render:

```markdown
### Lesson Promise

_Required · section_

State what this lesson owns now.
```

Artifact skeleton render:

```markdown
## Lesson Promise
```

### Sequence

Contract render:

```markdown
### Step Order

_Required · ordered list_

State the step order and what each step is there to teach.
```

If concrete items are present:

```markdown
### Read Order

_Required · ordered list_

1. Read the active issue.
2. Read the current issue plan.
3. Read the latest current comment.
```

### Bullets

```markdown
### Trust Surface

_Required · unordered list_

- Current Artifact
- Active Mode when present(active_mode)
- Trigger Reason when present(trigger_reason)
```

### Checklist

```markdown
### Release Checks

_Required · checklist_

- [ ] Run lint.
- [ ] Run tests.
- [ ] Confirm proof artifact exists.
```

### Definitions

Compact form:

```markdown
#### Must Include

_Required · definitions_

- **Verdict** — Say `accept` or `changes requested`.
- **Reviewed Artifact** — Name the reviewed artifact this review judged.
- **Analysis Performed** — Summarize the review analysis that led to the verdict.
```

Longer-form definition bodies:

```markdown
- **Reviewed Artifact**
  Name the reviewed artifact this review judged.
  When review stopped at handoff quality, name the producer handoff instead.
```

### Table

Schema-mode render:

```markdown
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
```

Row-bearing render:

```markdown
| Step | Role | Introduces | Coaching Level | Difficulty Curve |
| --- | --- | --- | --- | --- |
| 1 | introduce | range advantage cue | high | low |
| 2 | practice | none | medium | medium |
```

### Callout

Titled callout:

```markdown
> **IMPORTANT — Durable Truth**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.
```

Untitled or minimal callout:

```markdown
> **WARNING**
> Do not reopen upstream concept or playable decisions here.
```

### Code

````markdown
#### Example Manifest

_Advisory · code · json_

```json
{
  "title": "PLACEHOLDER: Lesson title",
  "steps": []
}
```
````

### Rule

```markdown
---
```

### Guarded block shell

```markdown
### Guided-Walkthrough Beat-Count Table

_Required · table · when walkthrough is in scope_

| Column | Meaning |
| --- | --- |
| Lesson | Nearby walkthrough lesson. |
| Beat Count | Actual comparable beat count. |
| Target Count | Planned beat count here. |
| Variance Reason | Why this lesson keeps or breaks the corridor. |
```

## Fully formed `LessonPlan` example

Doctrine source:

```prompt
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
```

Output contract:

```prompt
output LessonPlanFileOutput: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: AgentOutputDocument
    structure: LessonPlan
    requirement: Required
```

Contract render:

```markdown
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
```

Optional future artifact skeleton render:

```markdown
# Lesson Plan

> **IMPORTANT**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.

## Lesson Promise

## Step Order

1.
2.
3.

## Step Roles

- **Introduce** -
- **Practice** -
- **Test** -
- **Capstone** -

## Prior-Lessons Step-Count Table

| Lesson | Step Count | Comparable Kind | Target Count | Variance Reason |
| --- | --- | --- | --- | --- |

## Guided-Walkthrough Beat-Count Table

| Lesson | Beat Count | Target Count | Variance Reason |
| --- | --- | --- | --- |

## Step Arc Table

| Step | Role | Introduces | Coaching Level | Difficulty Curve |
| --- | --- | --- | --- | --- |
```

That skeleton mode is not required to ship the language, but the AST should
make it possible with no redesign.

## Extended typed-markdown design explored for second wave

An expanded version of the readable-output system introduced three more
primitives to support review comments, route-only handoffs, and bounded-scope
panels:

- `properties`
- `guard`
- `render_profile`

The motivation for each:

- `properties` covers compact labeled facts like Target, Path, Shape,
  Requirement, Current Artifact, Next Owner, Metadata Mode, and similar
  surfaces that degrade into bullets or extra headings today
- `guard` makes route-only and failure-detail blocks elegant instead of awkward
- `render_profile` lets the same underlying semantic structure render
  differently in AGENTS contract view, artifact shell view, and comment view

An expanded design sketch proposed three canonical render profiles:

```prompt
render_profile ContractMarkdown
render_profile ArtifactMarkdown
render_profile CommentMarkdown
```

and later, lightly patchable domain-specific profiles such as:

```prompt
render_profile LessonsHome:
    current_artifact -> sentence
    own_only -> sentence
    preserve_exact -> sentence
    review.contract_checks -> titled_section
    analysis.stages -> natural_ordered_prose
    guarded_sections -> concise_explanatory_shell
```

The three canonical profile roles:

- `ContractMarkdown` explains required structure
- `ArtifactMarkdown` produces a natural authored shell
- `CommentMarkdown` stays compact, favoring fact panels and guarded callouts

### Typed row and item schemas explored later

One broader document-design sketch also explored optional symbolic row and item
typing on readable blocks:

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
```

The attraction of these fields was:

- make rows and sequence items symbolic instead of only visual
- give later review, preservation, and schema-contract work a stable way to
  talk about row or item shape
- keep contract view and artifact-shell view aligned without relying only on
  prose descriptions of columns

The later narrowed recommendation did not put `row_schema:` or `item_schema:`
in the first wave.

Reasons:

- block-level titles, requirements, and column declarations already buy most of
  the first readability win
- row and item typing adds another layer of resolution and validation that is
  not required for the initial document rollout
- revisit it only if later review-contract or preservation work needs stable
  symbolic row/item references

### Comment document shape with `properties`

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

Rendered as compact comment markdown:

```markdown
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
```

### Review lowering into typed markdown

The readable-output system should also be able to serve as the render target for
review semantics.

Given a semantic review:

```prompt
review LessonPlanReview: "Lesson Plan Review"
    subject: LessonPlanFile
    contract: LessonPlanContract
    comment_output: CriticVerdictComment
```

the internal lowering can target a document shape like:

```prompt
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
```

### Analysis lowering into typed markdown

A separate semantic `analysis` declaration can also lower into a document
according to profile.

Example semantic surface:

```prompt
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
```

Intended profile behavior:

- in AGENTS.md, render as numbered or titled planning stages
- in compact homes, render as "What To Decide" prose plus tables
- in artifact templates, render only the exported structures

### Bounded-scope and metadata panel example

The readable-output system can also render bounded-scope law and grounding
surfaces readably:

```prompt
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
```

## Validation rules

These should fail loudly.

### Declaration-level rules

- `structure:` must resolve to a document
- document block keys must be unique
- inherited document blocks must be explicitly accounted for
- `override` must target an existing inherited key
- `override` must preserve block kind

### Table-specific rules

- table must have columns
- column keys must be unique
- rows may reference only declared columns
- row keys must be unique
- cells must be inline markdown, not nested blocks

### List and definitions rules

- keyed items must be unique within their block
- anonymous string items are allowed but not addressable
- mixing anonymous and keyed items is legal, but keyed items remain the
  canonical style

### Callout and code rules

- `callout.kind` must be in the closed core set
- `code.language` is optional
- `code.text` must use multiline string form
- multiline string syntax becomes a core Doctrine feature, not a code-block
  hack

### Guard rules

- `when` expressions on document blocks use the same expression language as
  output guards
- document guards may not read forbidden sources any more than guarded outputs
  may

## Renderer rules

These determine readability and should be treated as explicit spec.

- top-level agent fields still start at heading depth 2
- `SectionBlock` increments heading depth
- `ListBlock`, `DefinitionsBlock`, `TableBlock`, `CalloutBlock`, `CodeBlock`,
  and `RuleBlock` do not increment heading depth
- one blank line separates sibling blocks
- no empty heading shells
- inline code formatting remains authored responsibility
- `definitions` uses the compact one-line form when the definition body is a
  single paragraph
- `callout` renders with blockquote syntax, not heading syntax
- existing emphasized lines keep current rendering for backward compatibility
  unless explicitly rewritten as `callout`

Contract view should emit an italic metadata line such as:

```markdown
_Required · section_
_Required · table · when walkthrough is in scope_
_Advisory · code · json_
```

That status line does more work than deeper headings and keeps the output much
cleaner.

## Implementation plan for the readable-output system

Touch these files:

- `doctrine/grammars/doctrine.lark`
- `doctrine/model.py`
- `doctrine/parser.py`
- `doctrine/compiler.py`
- `doctrine/renderer.py`
- `examples/**` render-contract corpus and compile-negative corpus

Concrete compiler changes:

`model.py`

- add `DocumentDecl`
- add document block node types
- add multiline string node if triple-quoted strings are introduced

`compiler.py`

- replace the `CompiledSection`-only readable tree with a richer compiled block
  union
- map old keyed sections to `SectionBlock`
- compile `structure:` refs on inputs and outputs
- compile document addressable roots

`renderer.py`

- replace `_render_section()` recursion as the only readable-output path
- add block dispatch:
  - `_render_section_block`
  - `_render_list_block`
  - `_render_definitions_block`
  - `_render_table_block`
  - `_render_callout_block`
  - `_render_code_block`
  - `_render_rule_block`

`doctrine.lark`

- add `document_decl`
- add rich block items to document bodies
- add rich block items to record and workflow section bodies
- add multiline string literal

## Acceptance corpus for the readable-output system

Proposed example folders:

- `54_first_class_documents`
- `55_rich_blocks_in_output_contracts`
- `56_documents_with_tables_and_definitions`
- `57_document_inheritance`
- `58_document_guards`
- `59_multiline_strings_and_code_blocks`

Proposed compile-negative cases:

- `INVALID_STRUCTURE_REF_NON_DOCUMENT.prompt`
- `INVALID_DOCUMENT_DUPLICATE_BLOCK_KEY.prompt`
- `INVALID_DOCUMENT_OVERRIDE_KIND_MISMATCH.prompt`
- `INVALID_TABLE_ROW_UNKNOWN_COLUMN.prompt`
- `INVALID_TABLE_WITHOUT_COLUMNS.prompt`
- `INVALID_CALLOUT_UNKNOWN_KIND.prompt`
- `INVALID_CODE_BLOCK_WITHOUT_MULTILINE_STRING.prompt`

## What not to add in v1

To keep the feature elegant instead of sprawling:

- do not add raw markdown escape-hatch blocks in v1
- do not add HTML-specific constructs in v1
- do not add footnotes, images, or nested tables in v1
- do not put domain-specific table names or semantics in Doctrine core
