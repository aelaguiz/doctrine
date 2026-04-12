---
status: drafting_artifact
artifact_role: pre-phase design input
superseded_by_phase_docs: true
---

> Historical drafting artifact note (2026-04-11): This file stays at its
> original `docs/` path because archived second-wave implementation docs cite
> it directly. The implementation-order planning set now lives in the numbered
> phase docs under `docs/01_` through `docs/04_`, and current shipped language
> rules live in `docs/LANGUAGE_REFERENCE.md`, `docs/WORKFLOW_LAW.md`,
> `docs/REVIEW_SPEC.md`, and `doctrine/`. Treat the body below as pre-phase
> design history, not as the canonical sequencing view.

# Cross-Cutting Language Mechanics Spec

This document collected the language mechanics that cut across the proposed new
surfaces:

- sequencing and scope constraints
- declaration growth
- addressability and symbolic identity
- inheritance and patching discipline
- name resolution
- diagnostics
- multiline string support
- compiler touchpoints
- acceptance corpus planning
- strict invariants and non-goals

The intent was to keep the new surfaces aligned with existing Doctrine behavior
instead of introducing special-case sublanguages with different rules.

## Sequencing and scope constraints

The first important constraint in this design record was sequencing.

At the time this was written, the active plan was still incomplete around
existing surfaces:

- route-only workflow law
- critic first-class review
- producer preservation and invalidation

The new language work described in the proposal set is meant to land after
those seams are finished or on a separate branch.

This is not a compression pass.
The goal is not "shorter prompts". The goal is to move stable semantics out of
drift-prone prose and into compiler-owned structures.

Use shipped Doctrine features before inventing new layers.

Keep two structural invariants intact while doing that work:

- one owner per seam
- one live route per seam

The second important constraint is scope.

The proposal set argues for adding a very small number of new declaration
surfaces that fit the existing language shape, not a large collection of
domain-specific primitives.

## Declaration growth

Across the proposal set, the language growth is:

### New top-level declarations

- `analysis`
- `schema`
- `document`

### New shared readable block sublanguage

- `section`
- `sequence`
- `bullets`
- `checklist`
- `definitions`
- `table`
- `callout`
- `code`
- `rule`

### New attachment fields

- `schema:` on `output`
- `structure:` on markdown-bearing `input` and `output`

### Extended second-wave render controls explored

- `properties`
- `guard`
- `render_profile`

The narrower first-wave recommendation does not ship all of these at once.
It narrows the initial core to:

- `analysis`
- `schema`
- built-in natural render templates

The broader readable-output design remains the place where `document`,
block-kind rendering, and typed markdown live.

## Addressability and symbolic identity

One design rule is explicit:

Every renderable block must have a stable symbolic key that is not its title.

Titles are prose.
Keys are law.

That rule is what keeps inheritance, patching, review references, and
preservation stable even when human wording changes.

Document-path examples:

```text
LessonPlan.step_arc.columns.coaching_level
LessonPlan.prior_lesson_counts.columns.variance_reason
RouteOnlyHandoff.repeated_problem.returned_from
CriticVerdictComment.failure_detail.failing_gates
MetadataPassScope.route_state.preserve_basis
```

Interpolation examples:

```text
{{LessonPlan:title}}
{{LessonPlan:step_arc.title}}
{{LessonPlan:step_arc.columns.coaching_level.title}}
{{LessonPlan:step_arc.columns.coaching_level}}
```

Addressability rules gathered across the proposal set:

- document root is addressable
- keyed block children are addressable
- table columns are addressable
- table rows are addressable when present
- anonymous list items are not addressable
- keyed list items are addressable
- keyed definition items are addressable

The same philosophy applies to `analysis` and `schema`:

- keyed sections are the unit of inheritance and override
- domain titles are human-facing
- symbolic keys are the compiler-facing identity

## Inheritance and patching discipline

The proposal set consistently rejects special merge models.

### `analysis`

`analysis` should inherit like workflows:

- keyed sections only
- `inherit <section_key>`
- `override <section_key>:`
- missing inherited sections are compile errors
- overriding unknown sections is a compile error

### `schema`

`schema` should inherit like keyed block declarations:

- whole-declaration inheritance via `[ParentSchema]`
- `inherit sections`
- `override sections:`
- later, `inherit gates` and `override gates:`

The first version should not use per-entry conditional schema sections.
Use inheritance instead.

### `document`

`document` should inherit with explicit accounting:

- inherited blocks must be explicitly accounted for
- `override` may replace body or title
- block kind is invariant under override
- missing inherited block accounting is a compile error
- duplicate accounting is a compile error

The shared mechanical rule is:

Do not invent a separate merge discipline for each new feature.
Reuse Doctrine's existing explicit-accounting style.

## Name resolution and allowed surfaces

### `analysis`

Allowed:

- agent-authored slot value
- override slot value
- workflow use target if composition parity with workflows is wanted

Not allowed:

- review target
- inputs/outputs/skills block target
- output schema target

Resolution rules:

- bare refs and path refs use existing addressable resolution
- `classify ... as <name_ref>` must resolve to an enum declaration
- `derive`, `compare`, and `defend` path sets reuse law-path resolution

### `schema`

Resolution rules:

- `output schema:` must resolve to a `schema` declaration
- in phase 2, `review contract:` may resolve to a workflow review contract or a
  `schema`
- `contract.some_gate` resolves against workflow section keys or schema gate
  keys depending on contract kind

### `document`

Resolution rules:

- `structure:` must resolve to a `document`
- document descendants are addressable through the standard path discipline
- guards use the same expression language as output guards

## Multiline string support

The readable-output work introduces a new multiline string literal as a core
language feature.

Primary use case:

- `code.text` should use multiline string form

Rationale:

- code fences and rich examples are awkward without a multiline literal
- this should be a core Doctrine feature, not a one-off code-block hack

The proposal set explicitly says this should not be document-only. It is a
general language improvement.

## Diagnostics

### `analysis` diagnostic range

Reserve `E501-E519`.

Minimum set:

- `E501` unknown analysis enum target
- `E502` non-addressable or unresolved path in analysis basis
- `E503` invalid analysis inheritance target
- `E504` duplicate analysis section key
- `E505` analysis used in unsupported surface
- `E506` empty basis in derive, compare, or defend

### `schema` diagnostic range

Reserve `E520-E539`.

Minimum set:

- `E520` output schema ref unresolved
- `E521` duplicate schema section key
- `E522` duplicate schema gate key
- `E523` output declares both `schema` and `must_include` in phase 1
- `E524` review contract references unknown schema gate
- `E525` schema used in unsupported surface
- `E526` schema missing sections

### Readable-output validation rules

The document system also carries explicit validation rules even when the parent
doc did not assign numbered error codes to them:

- structure ref must resolve to a document
- document block keys must be unique
- inherited document blocks must be explicitly accounted for
- `override` must target an existing inherited key
- `override` must preserve block kind
- table must have columns
- column keys must be unique
- rows may reference only declared columns
- row keys must be unique
- cells must be inline markdown, not nested blocks
- keyed items must be unique within list and definitions blocks
- `callout.kind` must be in the closed core set
- `code.text` must use multiline string form
- guard expressions on document blocks must obey the same source restrictions as
  output guards

## Strict invariants

These are the rules the proposal set treats as non-negotiable:

- use shipped Doctrine features before inventing new layers
- keep one owner per seam
- keep one live route per seam
- `analysis` is for process structure, not control flow
- `schema` is for artifact structure, not runtime routing
- do not add lesson-specific or domain-specific core primitives
- `review_family` now ships as additive reusable review doctrine on the same
  review agreement path as `review`
- `route_only` now ships as a dedicated declaration that lowers through the
  existing workflow-law route-only semantics
- `grounding` now ships as an explicit control-plane protocol declaration on
  ordinary workflow and output surfaces
- do not add conditional schema sections in v1; use inheritance
- do not let outputs own both local `must_include` and `schema:` in the first
  release
- do not let rendered AGENTS.md mirror source syntax literally; renderer should
  speak in natural sentences
- do not promise automated validation of produced markdown artifacts; these
  features structure prompts and contracts, they do not inspect runtime
  markdown files
- do not add raw markdown escape-hatch blocks in v1
- do not add HTML-specific constructs in v1
- do not add footnotes, images, or nested tables in v1

## Compiler touchpoints

The proposal set consistently identifies the same files for implementation:

- `doctrine/grammars/doctrine.lark`
- `doctrine/model.py`
- `doctrine/parser.py`
- `doctrine/compiler.py`
- `doctrine/renderer.py`

Per-file responsibilities:

### `doctrine/grammars/doctrine.lark`

- add `analysis_decl`
- add `schema_decl`
- add `document_decl`
- add rich block items to document bodies
- add rich block items to record and workflow section bodies
- add multiline string literal

### `doctrine/model.py`

- add `AnalysisDecl` and related analysis node types
- add `SchemaDecl` and related schema node types
- add `DocumentDecl` and readable block node types
- add multiline string node if triple-quoted strings are introduced

### `doctrine/parser.py`

- parse the new top-level declarations
- parse block-body variants and new statements

### `doctrine/compiler.py`

- compile `analysis`
- compile `schema`
- compile `schema:` attachment on outputs
- compile `structure:` refs on inputs and outputs
- compile document addressable roots
- replace the `CompiledSection`-only readable tree with a richer compiled block
  union if the readable-output system lands

### `doctrine/renderer.py`

- add natural-sentence rendering for `analysis`
- add section-inventory rendering for `schema`
- replace heading-only recursion as the sole readable-output path if document
  blocks land
- add block-dispatch rendering functions for lists, definitions, tables,
  callouts, code, and rules

## Example-corpus planning

The proposal set contains two distinct example ladders from two different
design waves.

### Analysis and schema ladder

This is the narrower, later ladder:

1. `54_analysis_basic`
2. `55_analysis_classify_compare`
3. `56_schema_output_contract`
4. `57_schema_inheritance`
5. `58_lessons_lesson_architect_capstone`
6. `59_lessons_section_architecture_capstone`
7. `60_schema_review_contract`

What this ladder is trying to prove:

- `analysis` parses and renders naturally
- `classify` and `compare` resolve references cleanly
- `schema` attaches to outputs
- schema inheritance replaces conditional inventory logic
- later, `schema` gates can integrate with `review`

The doctrine-only useful subset of that ladder is:

1. `54_analysis_basic`
2. `55_analysis_classify_compare`
3. `56_schema_output_contract`
4. `57_schema_inheritance`
5. optionally `60_schema_review_contract`

### Readable-output ladder

This is the broader typed-markdown ladder:

1. `54_first_class_documents`
2. `55_rich_blocks_in_output_contracts`
3. `56_documents_with_tables_and_definitions`
4. `57_document_inheritance`
5. `58_document_guards`
6. `59_multiline_strings_and_code_blocks`

What this ladder is trying to prove:

- `document` parses
- rich readable blocks render with semantic markdown instead of heading depth
- tables and definitions support real contract layouts
- documents inherit and patch cleanly
- document guards obey shared expression law
- multiline strings support code fences and rich examples

### Compile-negative planning

The readable-output design also names explicit negative cases:

- `INVALID_STRUCTURE_REF_NON_DOCUMENT.prompt`
- `INVALID_DOCUMENT_DUPLICATE_BLOCK_KEY.prompt`
- `INVALID_DOCUMENT_OVERRIDE_KIND_MISMATCH.prompt`
- `INVALID_TABLE_ROW_UNKNOWN_COLUMN.prompt`
- `INVALID_TABLE_WITHOUT_COLUMNS.prompt`
- `INVALID_CALLOUT_UNKNOWN_KIND.prompt`
- `INVALID_CODE_BLOCK_WITHOUT_MULTILINE_STRING.prompt`

## Exact implementation order

Doctrine-only implementation order from the proposal set:

### Step A

Finish or isolate the currently active work on existing surfaces:

- route-only workflow-law blocker
- critic review port
- producer preservation and invalidation sweep

### Step B

Add `analysis`.

Touch:

- `doctrine/grammars/doctrine.lark`
- `doctrine/model.py`
- `doctrine/parser.py`
- `doctrine/compiler.py`
- `doctrine/renderer.py`
- example 54
- example 55

### Step C

Add `schema` plus output attachment.

Touch:

- the same core compiler files
- example 56
- example 57

### Step D

Only after the earlier analysis and schema steps are green, consider
schema-as-review-contract work.

That is where `60_schema_review_contract` belongs.

### Readable-output alternative order

If the broader typed-markdown system is pursued first, the implementation order
becomes:

1. typed markdown IR plus block union
2. multiline strings
3. `document`
4. rich block reuse in output and workflow bodies
5. `structure:` refs
6. block-dispatch renderer
7. document acceptance corpus

## What this mechanics layer is not

This mechanics layer is not:

- a replacement for domain design
- a replacement for workflow law
- a replacement for review semantics
- a runtime markdown validator
- a new general-purpose programming language inside Doctrine

Its job is to make new surfaces feel like Doctrine, not like embedded
mini-languages with different rules.
