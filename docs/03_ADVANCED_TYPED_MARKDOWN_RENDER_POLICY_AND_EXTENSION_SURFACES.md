---
title: "Doctrine Phase 3 - Advanced Typed Markdown Render Policy And Extension Surfaces"
status: active
doc_type: phased_plan
phase: 3
---

# Phase 3 - Advanced Typed Markdown Render Policy And Extension Surfaces

## Summary

Phase 3 grows the typed-markdown system beyond the phase-1 core blocks so the
same semantic structures can render cleanly in contracts, artifact shells, and
compact comments. It adds fact-panel primitives, explicit guard shells,
authored render policy, typed row/item schemas, and the later block extensions
that earlier drafts kept outside the first shipping cut.

This phase exists because phase 1 solves document structure, but it does not
fully solve compact readbacks, guarded comment shells, or profile-sensitive
rendering for review and route-only surfaces.

## Assumed Shipped Baseline

This phase assumes phases 1 and 2 are available:

- typed markdown block rendering is the single readable path
- `document` exists and is addressable
- `analysis` and `schema` exist and render naturally
- multiline strings exist
- `structure:` and owner-aware `schema:` are already stable

## Phase Boundary

This phase owns:

- `properties`
- explicit readable guard shells
- authored `render_profile`
- canonical contract, artifact, and comment profile families
- lowering of semantic declarations into typed markdown
- typed row and item schemas on readable blocks
- later block extensions that earlier drafts left outside v1

This phase does not own:

- dedicated `review_family`
- dedicated `route_only`
- dedicated `grounding`
- control-plane currentness semantics

Those later surfaces consume the render-policy machinery defined here.

## `properties`

### Purpose

`properties` is the compact fact-panel primitive for labeled fields such as
Target, Path, Shape, Requirement, Current Artifact, Next Owner, Active Mode,
and similar surfaces that feel awkward as bullets or headings.

### Surface syntax

```prompt
properties route_state: "Route State" required
    current_route: "Current Route"
        "route-only turn; no specialist artifact is current"
    next_owner: "Next Owner"
        "LessonsProjectLead"
    next_step: "Next Step"
        "repair ownership justification"
```

Rules:

- `properties` is a readable block kind
- entries are keyed and addressable
- each entry has a stable key and rendered label
- entry bodies are compact prose or inline markdown
- `properties` may appear in documents and in any readable body that already
  accepts shared readable blocks

### Rendering

Compact profile:

```markdown
- Current Route: route-only turn; no specialist artifact is current
- Next Owner: LessonsProjectLead
- Next Step: repair ownership justification
```

Expanded contract profile:

```markdown
### Route State

_Required · properties_

- Current Route: route-only turn; no specialist artifact is current
- Next Owner: LessonsProjectLead
- Next Step: repair ownership justification
```

## Explicit Guard Shells

### Purpose

Phase 1 block-level `when <expr>` covers many cases, but compact comments and
profile-sensitive readbacks benefit from an explicit readable shell that owns
the guarded explanation rather than attaching the condition to an arbitrary
child block.

### Surface syntax

```prompt
guard repeated_problem when RouteFacts.critic_miss_repeated
    section repeated_problem: "Repeated Problem"
        properties:
            failing_pattern: "What Keeps Failing"
                "critic keeps rejecting vague metadata handoff"
            returned_from: "Returned From"
                "LessonsAcceptanceCritic"
            next_fix: "Next Concrete Fix"
                "make section-mode preserve basis explicit"
```

Rules:

- `guard` is a readable shell, not a semantic condition evaluator
- the guard expression uses the same expression language as phase-1 block
  guards
- the body may contain any readable block family members
- profiles may render the shell as a short explanatory line, a titled shell, or
  may suppress the shell title and render only the guarded body

## `render_profile`

### Purpose

`render_profile` lets the same underlying semantic structure render
differently in contract view, artifact-shell view, and comment view without
forcing one global formatting style.

### Canonical profiles

Phase 3 ships three built-in profiles:

- `ContractMarkdown`
- `ArtifactMarkdown`
- `CommentMarkdown`

### Authored profile syntax

```prompt
render_profile LessonsHome:
    current_artifact -> sentence
    own_only -> sentence
    preserve_exact -> sentence
    review.contract_checks -> titled_section
    analysis.stages -> natural_ordered_prose
    guarded_sections -> concise_explanatory_shell
```

### Attachment

Phase 3 allows profile attachment on readable producers:

- `document render_profile: NameRef`
- `analysis render_profile: NameRef`
- `schema render_profile: NameRef`
- markdown-bearing `output render_profile: NameRef`

If no authored profile is attached:

- contract-style renders use `ContractMarkdown`
- artifact shells use `ArtifactMarkdown`
- compact comments use `CommentMarkdown`

### Rules

- profiles do not change semantics or addressability
- profiles only change readback shape
- profile rules apply after compilation into typed markdown, not before
- later phases may map specialized control-plane surfaces onto these profiles

## Lowering Semantic Declarations Into Typed Markdown

### Analysis lowering

`analysis` lowers into typed markdown so the same semantic reasoning program can
render differently by profile.

Example intent:

- contract view renders titled planning stages
- compact home view renders "What To Decide" prose
- artifact-shell view can render only exported structures when needed

### Review lowering

Phase 3 introduces the lowering target even before phase-4 control-plane
surfaces finalize the semantic declarations that feed it.

Example typed-markdown shape:

```prompt
document CriticVerdictComment: "Verdict And Handoff Comment"
    properties summary: "Review State"
        verdict: "Verdict"
        reviewed_artifact: "Reviewed Artifact"
        next_owner: "Next Owner"
        current_artifact: "Current Artifact"

    section analysis_performed: "Analysis Performed"
    section output_contents_that_matter: "Output Contents That Matter"

    guard failure_detail when verdict == changes_requested
        section failure_detail: "Failure Detail"
            sequence failing_gates: "Failing Gates"
            callout blocked_gate: "Blocked Gate"
                kind: warning
```

## Typed Row And Item Schemas

Phase 3 adds symbolic row and item shape declarations directly on readable
blocks so later review and preservation logic can refer to block shape without
relying only on prose.

### `item_schema`

```prompt
sequence step_order: "Step Order" required
    item_schema:
        step_label: "Step Label"
            "The visible step name or ordinal."
        teaching_job: "Teaching Job"
            "What the step is there to teach."
    first: "Read the active issue."
    second: "Read the current issue plan."
```

### `row_schema`

```prompt
table step_arc: "Step Arc Table" required
    row_schema:
        step: "Step"
            "Step identifier or ordinal."
        role: "Role"
            "The step role."
        introduces: "Introduces"
            "What is genuinely introduced here."
    columns:
        step: "Step"
        role: "Role"
        introduces: "Introduces"
```

Rules:

- `item_schema:` and `row_schema:` are inline block-owned schemas
- schema entries are keyed and addressable beneath the owning block
- row or item schemas do not replace visible block items or columns; they make
  the intended item shape explicit
- later phases may target these schemas when review or preservation needs
  stable symbolic shape references

## Late Block Extensions

Earlier drafts treated these as outside the first cut. Phase 3 sequences them
after the advanced render-policy work so they reuse the same typed block model
instead of inventing ad hoc escape hatches.

### Raw markdown block

```prompt
markdown appendix_notes: "Appendix Notes" advisory
    text: """
    ## Imported Notes

    This block preserves authored markdown directly.
    """
```

Rules:

- raw markdown is explicit and block-scoped
- raw markdown never becomes the default rendering path
- multiline string form is required

### HTML block

```prompt
html embed_preview: "Embed Preview" advisory
    text: """
    <div class="preview-card">Preview</div>
    """
```

Rules:

- HTML is opt-in and block-scoped
- HTML does not change the core markdown renderer for ordinary blocks
- HTML remains subject to the same explicit-accounting and addressability rules
  as other blocks

### Footnotes

```prompt
footnotes references: "References" advisory
    note_a: "Explains the comparison fallback."
    note_b: "Explains why the route stays fixed."
```

### Images

```prompt
image route_map: "Route Map" advisory
    src: "assets/route-map.png"
    alt: "Route map showing the current path."
    caption: "Current route and preserved branch points."
```

### Nested tables

Nested tables become legal only through an explicit structured-cell model:

```prompt
table summary_grid: "Summary Grid" advisory
    columns:
        topic: "Topic"
        details: "Details"
    rows:
        row_1:
            topic: "Comparables"
            details:
                table comparable_breakdown: "Comparable Breakdown"
                    columns:
                        lesson: "Lesson"
                        why: "Why"
```

Rules:

- nested tables remain illegal in plain inline cells
- nested tables require structured cell bodies
- structured cell bodies reuse the same block dispatch system rather than a
  separate renderer

## Validation And Invariants

Phase 3 fail-loud rules:

- `properties` entry keys are unique
- `guard` expressions obey existing guard visibility rules
- `render_profile` rules must target known semantic paths or known block kinds
- `row_schema` and `item_schema` keys are unique within the owning block
- raw markdown and HTML blocks require multiline `text`
- nested tables require structured cell bodies

Phase invariants:

- render policy never changes semantic meaning
- typed markdown remains the only readable-output architecture
- late extensions remain explicit blocks, not silent fallbacks

## Proof Plan

Positive ladder for phase 3:

1. `properties` in documents and comment-style outputs
2. explicit guard shells with profile-sensitive render
3. built-in and authored `render_profile`
4. analysis and review lowering into typed markdown
5. `row_schema` and `item_schema`
6. raw markdown and HTML blocks
7. footnotes, images, and nested tables through structured cells

Compile-negative ladder for phase 3:

- duplicate property key
- invalid profile target
- invalid guard source in a guard shell
- malformed `row_schema:` or `item_schema:`
- raw markdown without multiline text
- nested table in an inline cell

## Exact Implementation Order

1. Add `properties` as a compact readable block.
2. Add explicit `guard` shells on top of the phase-1 guard model.
3. Add built-in render profiles and authored `render_profile`.
4. Lower `analysis` and review-shaped readable outputs into typed markdown by
   profile.
5. Add `row_schema:` and `item_schema:` on readable blocks.
6. Add raw markdown and HTML blocks as explicit late extensions.
7. Add footnotes, images, and nested tables through structured cells.
