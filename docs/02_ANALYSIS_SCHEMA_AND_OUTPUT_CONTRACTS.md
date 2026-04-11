---
title: "Doctrine Phase 2 - Analysis Schema And Output Contracts"
status: active
doc_type: phased_plan
phase: 2
---

# Phase 2 - Analysis Schema And Output Contracts

## Summary

Phase 2 adds the two semantic declaration families that absorb the largest
remaining prose buckets after the typed-markdown foundation exists:

- `analysis` for repeated reasoning choreography
- `schema` for artifact inventories and gate catalogs

This phase also makes `schema:` owner-aware so that `output.schema` points at a
Doctrine `schema` while `output shape.schema` continues to mean `json schema`.
The phase leaves review/control-plane consumers for later, but it ships the
declarations, diagnostics, output contract semantics, artifact inventories, and
reusable surface groups those later integrations depend on.

## Assumed Shipped Baseline

This phase assumes phase 1 is available:

- the typed markdown block union is the only readable renderer path
- `document` is addressable and inheritable
- multiline strings exist
- markdown-bearing contracts support `structure:`
- readable-output rendering already uses block dispatch

## Phase Boundary

This phase owns:

- first-class `analysis`
- first-class `schema`
- `analysis:` attachment on concrete agents
- owner-aware `schema:` on outputs
- schema sections and gates
- schema artifacts and reusable groups
- analysis and schema inheritance, addressability, rendering, and diagnostics

This phase does not own:

- authored render profiles
- review lowering to typed markdown
- dedicated `review_family`
- dedicated `route_only`
- dedicated `grounding`
- schema-backed `review contract:` consumers

Those later phases reuse the declaration surfaces defined here.

## Doctrine And Domain Boundary

Doctrine owns:

- the reusable structure of reasoning programs
- the reusable structure of artifact inventories and gate catalogs
- compiler-owned rendering and diagnostics
- inheritance, name resolution, and owner-aware attachment rules

Domain packs own:

- domain enums
- domain gate names
- domain meanings such as corridor ranges, route identity, or comparison taste

Agent-local prose still owns mission, quality bars, rare exceptions, and local
judgment that is not yet stable enough to be law.

## `analysis`

### Purpose

`analysis` is a renderable declaration for structured reasoning steps. It
replaces long numbered procedural sections with a compact, typed, reusable
surface that still renders as natural AGENTS.md prose.

### Surface syntax

Canonical form:

```prompt
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
        defend "90-120s corridor" using {SectionLessonMap, RecentLessonContinuityContext, AcceptedLessonComparables}
```

The verb set is intentionally narrow:

- `derive`
- `classify`
- `compare`
- `defend`

Anything still judgment-heavy stays as ordinary prose inside the section body.

### Allowed placements

Allowed:

- agent `analysis:` attachment
- override slot values
- other readable composition surfaces when full parity is intentionally added

Not allowed:

- `review:` target
- `inputs:`, `outputs:`, or `skills:` target
- output `schema:` target

### Name resolution

- `classify ... as <name_ref>` must resolve to an `enum`
- `derive`, `compare`, and `defend` basis sets resolve through the ordinary
  addressable path discipline
- unresolved or non-addressable basis refs fail loud

### Inheritance

`analysis` inherits like workflows:

- keyed sections only
- `inherit <section_key>`
- `override <section_key>:`
- missing inherited sections are compile errors
- overriding unknown sections is a compile error

### Rendering

`analysis` stays readable and non-symbolic in rendered output.

Examples:

```text
derive "Lesson Promise" from {A, B, C}
-> Derive Lesson Promise from A, B, and C.

classify "Step Roles" as StepRole
-> Classify Step Roles using Step Role.

compare "Real Comparable Lessons" against {A, B}
-> Compare Real Comparable Lessons against A and B.

defend "90-120s corridor" using {A, B, C}
-> Defend 90-120s corridor using A, B, and C.
```

## `schema`

### Purpose

`schema` centralizes artifact inventories, reusable surface groups, and gate
catalogs. It replaces large repeated "must include" sections and shared gate
prose with a named declaration that outputs, reviews, and later control-plane
surfaces can reuse.

### Surface syntax

Canonical form:

```prompt
schema LessonPlanSchema: "Lesson Plan Schema"
    sections:
        lesson_promise: "Lesson Promise"
            "State what this lesson owns now."
        step_order: "Step Order"
            "State the step order and what each step is there to teach."
        step_roles: "Step Roles"
            "Name what each step is doing using introduce, practice, test, or capstone."

    gates:
        explicit_step_roles: "Explicit Step Roles"
            "Fail if introduce, practice, test, or capstone are only implied in prose."
        no_new_route: "No New Route"
            "Fail if the plan quietly invents a new lesson route."
```

### Artifact inventories and reusable groups

Phase 2 also gives `schema` a first-class place to name concrete artifact
surfaces and reusable bundles of those surfaces for later control-plane use.

Canonical form:

```prompt
schema BuildSurfaceSchema: "Build Surface Schema"
    artifacts:
        outline_file: "Outline File"
            ref: OutlineFile

        review_comment: "Review Comment"
            ref: ReviewCommentFile

        manifest_file: "Manifest File"
            ref: ManifestFile

    groups:
        downstream_rebuild: "Downstream Rebuild"
            outline_file
            review_comment
            manifest_file
```

Rules:

- `artifacts:` declares keyed, titled concrete artifact entries inside a schema
- each artifact entry owns one `ref:` that resolves to a concrete addressable
  input or output root
- `groups:` declares keyed, titled bundles of local artifact keys
- group member order is authored and preserved
- later phases may consume `schema.groups.*` directly from workflow law or
  review/control-plane lowering, but phase 2 only defines the declaration
  surfaces and readable rendering

### Owner-aware `schema:` rules

Doctrine already uses `schema:` beneath `output shape` to attach a `json
schema`. Phase 2 keeps that meaning and adds an owner-aware interpretation on
`output` itself.

Rules:

- `output.schema` resolves to a Doctrine `schema`
- `output shape.schema` resolves to a `json schema`
- these are not competing meanings; they are owner-scoped meanings
- attaching a schema to an output continues to mean "this output is governed by
  this reusable Doctrine inventory", even when the same schema also exposes
  artifacts or groups for later control-plane reuse

### Output attachment

```prompt
output LessonPlanFile: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: MarkdownDocument
    requirement: Required
    schema: LessonPlanSchema
```

### Static rules

- a schema must declare at least one `sections:` or `artifacts:` block
- section keys are unique
- gate keys are unique
- artifact keys are unique
- group keys are unique
- an output may attach at most one Doctrine `schema`
- an output with `schema:` may not also own local `must_include:`
- an output-attached schema must still expose at least one section
- every artifact `ref:` must resolve to a concrete input or output root
- every group member must name a local artifact key
- groups may not be empty

That last rule is deliberate: there must not be two owners for the same output
inventory seam.

### Inheritance

`schema` inherits with explicit accounting:

- whole-declaration inheritance via `[ParentSchema]`
- `inherit sections`
- `override sections:`
- `inherit gates`
- `override gates:`
- `inherit artifacts`
- `override artifacts:`
- `inherit groups`
- `override groups:`

Conditional schema sections are not needed because inheritance carries the
variant logic explicitly.

### Rendering

Output-side schema rendering produces a readable inventory:

```markdown
## Outputs

### Lesson Plan File

- Target: File
- Path: `lesson_root/_authoring/LESSON_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

#### Required Sections

##### Lesson Promise

State what this lesson owns now.
```

Inventory-side schema rendering also stays readable:

```markdown
## Artifact Inventory

- Outline File
- Review Comment
- Manifest File

## Surface Groups

- Downstream Rebuild
  - Outline File
  - Review Comment
  - Manifest File
```

## Addressability And Symbolic Identity

The same "keys are law" rule applies here.

Addressability:

- analysis root is addressable
- analysis sections are addressable
- schema root is addressable
- schema `sections:` items are addressable
- schema `gates:` items are addressable
- schema `artifacts:` items are addressable
- schema `groups:` items are addressable

Examples:

```text
{{LessonPlanning:title}}
{{LessonPlanning:lesson_job.title}}
{{LessonPlanSchema:sections.step_roles.title}}
{{LessonPlanSchema:gates.explicit_step_roles.title}}
{{BuildSurfaceSchema:artifacts.manifest_file.title}}
{{BuildSurfaceSchema:groups.downstream_rebuild.title}}
```

## Grammar And Model Additions

Primary surfaces added in phase 2:

- `analysis_decl`
- `schema_decl`
- analysis section items and typed verbs
- schema `sections:` block
- schema `gates:` block
- schema `artifacts:` block
- schema `groups:` block
- owner-aware `output_schema_stmt`
- typed agent `analysis:` field

Primary implementation files:

- `doctrine/grammars/doctrine.lark`
- `doctrine/model.py`
- `doctrine/parser.py`
- `doctrine/compiler.py`
- `doctrine/renderer.py`

## Diagnostics And Invariants

Reserved phase-2 ranges:

- `E501-E519` for `analysis`
- `E520-E539` for `schema`

Minimum `analysis` diagnostics:

- `E501` unknown analysis enum target
- `E502` non-addressable or unresolved analysis basis path
- `E503` invalid analysis inheritance target
- `E504` duplicate analysis section key
- `E505` analysis used in unsupported surface
- `E506` empty basis in derive, compare, or defend

Minimum `schema` diagnostics:

- `E520` output schema ref unresolved
- `E521` duplicate schema section key
- `E522` duplicate schema gate key
- `E523` output declares both Doctrine `schema:` and local `must_include:`
- `E524` unknown schema gate in later consumers
- `E525` schema used in unsupported surface
- `E526` output-attached schema missing sections
- `E527` duplicate schema artifact key
- `E528` duplicate schema group key
- `E529` schema artifact `ref:` unresolved or not a concrete artifact root
- `E530` schema group member unknown
- `E531` empty schema group

Phase invariants:

- one owner per inventory seam
- owner-aware `schema:` resolution everywhere: compiler, docs, proof, editor
- `analysis` is reasoning structure, not control flow
- `schema` is inventory, gate, and reusable surface-group structure, not
  routing law

## Proof Plan

Positive ladder for phase 2:

1. analysis attachment on a concrete agent
2. analysis classify/compare/defend coverage
3. owner-aware output `schema:` attachment
4. schema inheritance and gate catalogs
5. schema artifacts and reusable groups

Compile-negative ladder for phase 2:

- unknown `analysis:` target
- unresolved enum in `classify`
- unresolved analysis basis path
- duplicate analysis section key
- unknown output `schema:` target
- dual ownership through `schema:` plus local `must_include:`
- duplicate schema section or gate key
- duplicate schema artifact or group key
- schema artifact with unresolved `ref:`
- schema group that names an unknown artifact key
- output-attached schema with no sections

## Exact Implementation Order

1. Add first-class `analysis` plus agent `analysis:` attachment.
2. Land analysis rendering, addressability, inheritance, and diagnostics.
3. Add first-class `schema` with `sections:`.
4. Land owner-aware `output.schema` resolution without disturbing
   `output shape.schema`.
5. Add schema `gates:` plus schema inheritance and gate diagnostics.
6. Add schema `artifacts:` and `groups:` plus addressability and diagnostics.
7. Extend proof to cover both positive and negative cases before later review
   or control-plane consumers are added.
