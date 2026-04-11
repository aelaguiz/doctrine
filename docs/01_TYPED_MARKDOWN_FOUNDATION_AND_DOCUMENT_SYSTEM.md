---
title: "Doctrine Phase 1 - Typed Markdown Foundation And Document System"
status: active
doc_type: phased_plan
phase: 1
---

# Phase 1 - Typed Markdown Foundation And Document System

## Summary

Phase 1 builds the readable-output foundation that every later phase relies on.
It replaces the heading-only readable tree with a typed markdown block system,
ships first-class `document`, adds multiline strings, and makes markdown-bearing
contracts point at named document structures through `structure:`.

This phase exists to solve a structural problem, not a cosmetic one. Doctrine
already renders readable content, but today rich semantic differences collapse
into heading depth. The goal of this phase is to make structure explicit in the
language and preserve natural rendered Markdown without forcing every readable
surface into nested heading shells.

## Phase Boundary

This phase owns:

- the typed markdown block model
- first-class `document`
- the shared readable block family
- multiline strings
- `structure:` on markdown-bearing inputs and outputs
- the renderer conversion from section-only recursion to block dispatch
- document addressability, inheritance, validation, and proof

This phase does not own:

- `analysis`
- `schema`
- owner-aware `schema:`
- review integration
- `route_only`
- `grounding`
- authored render profiles

Those come later, but this phase must leave a stable block IR and renderer path
that later phases can reuse without redesign.

## Assumed Baseline

Baseline before phase 1:

- Doctrine already ships readable declarations and output contracts.
- Existing keyed sections, emphasized prose lines, and rendered Markdown remain
  legal and must stay backward compatible.
- Existing addressability, explicit inheritance accounting, and fail-loud
  diagnostics remain the governing language style.

## Core Decision

Doctrine should render readable output from semantic block kinds rather than
from heading depth alone.

The phase therefore introduces:

- a first-class `document` declaration
- a shared readable block family
- a richer compiled readable block union
- renderer dispatch based on block kind

The governing boundary is:

- Doctrine owns structure and rendering semantics.
- Domain packs own document names, required blocks, table names, and domain
  column meanings.

Keys are law. Titles are prose.

## Surfaces Owned By Phase 1

### Top-level declaration

```prompt
document LessonPlan: "Lesson Plan"
    ...
```

`document` is a named, addressable, inheritable schema for a markdown artifact.
It describes readable structure, not workflow control flow.

### Shared readable block family

Phase 1 ships these block kinds:

- `section`
- `sequence`
- `bullets`
- `checklist`
- `definitions`
- `table`
- `callout`
- `code`
- `rule`

Every renderable block has a stable symbolic key separate from its title.

### Attachment field

```prompt
structure: LessonPlan
```

`structure:` attaches a named `document` to a markdown-bearing `input` or
`output`.

### Multiline strings

Phase 1 adds a general multiline string literal to Doctrine. The primary use
case is `code.text`, but the feature belongs to the language core rather than
to a one-off code-block exception.

## Surface Syntax

### Canonical `document` form

```prompt
document LessonPlan: "Lesson Plan"
    callout durable_truth: "Durable Truth" advisory
        kind: important
        "This file owns the lesson job, pacing, and stable-vs-variable boundaries."

    section lesson_promise: "Lesson Promise" required
        "State what this lesson owns now."

    sequence step_order: "Step Order" required
        first: "Read the active issue."
        second: "Read the current issue plan."
        third: "Read the latest current comment."

    definitions step_roles: "Step Roles" required
        introduce: "Introduce"
            "Name what each step is doing using `introduce`."
        practice: "Practice"
            "Name what each step is doing using `practice`."

    table step_arc: "Step Arc Table" required
        columns:
            step: "Step"
                "Step identifier or ordinal."
            role: "Role"
                "The step role."
            introduces: "Introduces"
                "What is genuinely introduced here."
        notes:
            "Add one row per step."

    code example_manifest: "Example Manifest" advisory
        language: json
        text: """
        {
          "title": "PLACEHOLDER: Lesson title",
          "steps": []
        }
        """

    rule section_break
```

### Common block header

All document blocks share this header shape:

```text
<block_kind> <key>: "Title" <requirement>? <guard>?
```

Requirement values:

- `required`
- `advisory`
- `optional`

Guard form:

- `when <expr>`

### Block-specific rules

`section`

- heading plus block body
- body may contain any readable block

`sequence`

- ordered list
- keyed items are recommended because they remain addressable
- authored order is preserved

`bullets`

- unordered list
- keyed items remain the canonical style when addressability matters

`checklist`

- markdown task-list output
- used for operator checklists and contract readbacks

`definitions`

- compact labeled term/explanation rows
- clean replacement for repeated heading ladders such as "Must Include"

`table`

- ordered, keyed columns
- optional keyed rows
- column bodies serve as contract descriptions when no concrete rows are
  present
- row cells stay inline markdown in this phase

`callout`

- blockquote-style admonition
- allowed kinds in phase 1:
  - `required`
  - `important`
  - `warning`
  - `note`

`code`

- fenced code block
- optional `language`
- `text` must use multiline string form

`rule`

- thematic break rendered as `---`

## `structure:` On Inputs And Outputs

Markdown-bearing contracts may attach a named document structure.

Input example:

```prompt
input LessonPlanContract: "Lesson Plan"
    source: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: MarkdownDocument
    structure: LessonPlan
    requirement: Required
```

Output example:

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
- `structure:` is descriptive and typed, not a prose convention
- `structure:` may appear on `input` and `output`
- `structure:` requires a markdown-bearing shape such as `MarkdownDocument` or
  `AgentOutputDocument`

## Addressability And Symbolic Identity

Document roots and keyed descendants are addressable through the standard path
discipline.

Examples:

```text
{{LessonPlan:title}}
{{LessonPlan:step_arc.title}}
{{LessonPlan:step_arc.columns.role.title}}
{{LessonPlan:step_arc.columns.role}}
```

Addressability rules:

- document root is addressable
- keyed block children are addressable
- table columns are addressable
- table rows are addressable when present
- keyed list items are addressable
- keyed definition items are addressable
- anonymous list items are legal but not addressable

## Inheritance And Patching

Document inheritance follows Doctrine's explicit-accounting style.

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
- `override` may replace title, body, or both
- block kind is invariant under override
- missing inherited block accounting is a compile error
- duplicate accounting is a compile error

## Guards And Backward Compatibility

### Guards

Document blocks support `when <expr>`.

Example:

```prompt
table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" required when LessonFacts.walkthrough_in_scope
    columns:
        lesson: "Lesson"
        beat_count: "Beat Count"
```

Rules:

- guard syntax reuses Doctrine's existing expression language
- contract render mode emits guarded shells, not runtime evaluation
- document guards obey the same source restrictions as guarded output sections

### Backward compatibility

Existing authored keyed sections remain legal and compile as semantic `section`
blocks. Existing emphasized prose lines remain legal and keep their current
render behavior unless a prompt explicitly rewrites them as `callout`.

## Render And Readback Rules

Only `section` consumes heading depth. Every other readable block keeps its own
markdown syntax.

Examples:

`section`

```markdown
### Lesson Promise

_Required · section_

State what this lesson owns now.
```

`sequence`

```markdown
### Step Order

_Required · ordered list_

1. Read the active issue.
2. Read the current issue plan.
3. Read the latest current comment.
```

`definitions`

```markdown
#### Must Include

_Required · definitions_

- **Verdict** - Say `accept` or `changes requested`.
- **Reviewed Artifact** - Name the reviewed artifact this review judged.
```

`table`

```markdown
### Step Arc Table

_Required · table_

| Column | Meaning |
| --- | --- |
| Step | Step identifier or ordinal. |
| Role | The step role. |
| Introduces | What is genuinely introduced here. |
```

`callout`

```markdown
> **IMPORTANT - Durable Truth**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.
```

`code`

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

## Validation, Diagnostics, And Invariants

These rules fail loud in phase 1:

- `structure:` must resolve to a `document`
- document block keys must be unique
- inherited document blocks must be explicitly accounted for
- `override` must target an existing inherited key
- `override` must preserve block kind
- table must have columns
- column keys must be unique
- rows may reference only declared columns
- row keys must be unique
- cells must stay inline markdown in this phase
- keyed items must be unique within list and definitions blocks
- `callout.kind` must be in the closed core set
- `code.text` must use multiline string form
- guard expressions must obey existing guarded-output restrictions

Phase invariants:

- one readable renderer path
- one compiled block union
- no shadow document renderer
- keys remain stable symbolic law
- titles remain prose

## Compiler Touchpoints

Primary implementation surfaces:

- `doctrine/grammars/doctrine.lark`
- `doctrine/model.py`
- `doctrine/parser.py`
- `doctrine/compiler.py`
- `doctrine/renderer.py`

Required compiler changes:

- add `document_decl`
- add readable block node types
- add multiline string literal support
- replace the `CompiledSection`-only readable tree with a richer block union
- compile `structure:` on markdown-bearing inputs and outputs
- compile document addressable roots
- replace section-only rendering with block dispatch

## Proof Plan

Positive ladder for phase 1:

1. first-class `document`
2. rich blocks in output contracts
3. documents with tables and definitions
4. document inheritance
5. document guards
6. multiline strings and code blocks

Compile-negative ladder for phase 1:

- non-document `structure:` ref
- duplicate document block key
- document override kind mismatch
- table row references unknown column
- table without columns
- unknown `callout.kind`
- code block without multiline string

## Exact Implementation Order

1. Add the typed markdown IR and compiled block union.
2. Add multiline strings to the core grammar and parser.
3. Add first-class `document` plus block parsing.
4. Compile document addressable roots and inheritance.
5. Add `structure:` resolution for markdown-bearing inputs and outputs.
6. Replace section-only rendering with block-dispatch rendering.
7. Land the positive and negative proof ladder for the document system.
