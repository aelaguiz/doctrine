# Analysis And Schema Language Surfaces

> Status note (2026-04-11): We believe the `analysis` and `schema` surfaces
> described in this document are fully implemented in the current repo. If this
> spec and the shipped implementation ever drift, trust `doctrine/` and the
> manifest-backed examples.

This document defines the two new core semantic declaration families that the
language expansion is centered on:

- `analysis` for structured reasoning programs
- `schema` for structured artifact inventories and later gate catalogs

The design thesis behind both surfaces is:

- Do not chase brevity for its own sake.
- Promote prose that is secretly schema into Doctrine.
- Keep compiler-owned semantics on the authoring side.
- Preserve human-readable, natural AGENTS.md output on the rendered side.

The two main prose buckets that the language needs to absorb are:

1. Procedural prose:
   "Restate the lesson job, then set step roles, then build nearby-lesson
   evidence, then comparable proof, then defend pacing..."
2. Inventory and gate prose:
   "At minimum confirm the file has non-empty X, Y, Z..." or "This output must
   include A, B, C..."

The first bucket should become `analysis`.
The second bucket should become `schema`.

The boundary between Doctrine core and domain-specific packs is:

- Doctrine owns structure and reusable semantics.
- Domain packs own domain truth, domain enums, domain gate names, and domain
  meanings.

In the language expansion described here, Doctrine core should own:

- a first-class `analysis` declaration for structured reasoning programs
- a first-class `schema` declaration for document section inventories and later
  gate catalogs
- output attachment for schemas
- natural rendering rules for both, so source becomes formal while AGENTS.md
  stays readable
- inheritance, patching, and name-resolution behavior for both, matching
  existing Doctrine patterns

Domain packs should own:

- `StepRole`, `MetadataMode`, route labels, and any other closed vocabularies
- schema declarations like lesson-plan schema, section-map schema, metadata
  schema, dossier schema, and similar families
- analysis declarations like lesson planning, section architecture analysis, or
  playable-strategy analysis
- the actual meaning of concepts like "same-route", "similar-burden",
  "90-120s corridor", "capstone route", or "exact-move boundary"

Agent-local prose should continue to own:

- mission and role identity
- judgment-heavy quality bars
- rare exceptions, stop lines, and local taste notes
- anything that is still genuinely human judgment rather than stable workflow
  law or output structure

### Do not add to Doctrine

The monolith spec also made a negative boundary explicit.

Do not add:

- `route_only` as a new declaration kind when existing workflow law already
  covers that seam
- `review_family` as a new declaration kind when abstract review inheritance
  and shared review patches already fit
- domain-specific enums or vocabulary as core language features
- automated validation of authored markdown artifacts, because that is a
  separate system from prompt and contract structure

## Analysis

### Earliest surface sketch

The first design sketch for `analysis` treated it as a first-class construct for
repeated reasoning choreography:

```prompt
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
```

That sketch captures the core insight:
large numbered planning programs are not "tone". They are reusable reasoning
programs.

What remains outside Doctrine in that sketch:

- `StepRole`
- the `90-120s` corridor
- the meaning of "same-route"
- the meaning of "least-wrong fit"
- the choice of basis files

### Before and after example

Before, the authoring surface was a prose workflow:

```prompt
workflow LessonPlanAnalysisSteps: "Lesson Plan Analysis Steps"
    "Restate in plain English what this lesson owns..."
    "Name what each step is doing using `introduce`, `practice`, `test`, or `capstone`..."
    "Build nearby-lesson evidence..."
    "Find real comparable lessons..."
    "Use current lesson data to defend the lesson's size..."
    "Build the `Step Arc Table`..."
    "Say what must stay stable and what may vary safely..."
```

After, the authoring surface becomes symbolic:

```prompt
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
```

Before, the emitted AGENTS.md surface was a numbered plan:

```markdown
## Lesson Plan Analysis Steps

### Step 1 - Restate The Lesson Job

Restate in plain English what this lesson owns, what it defers, and what is
genuinely new here.

### Step 2 - Set The Step Roles

Name what each step is doing using `introduce`, `practice`, `test`, or
`capstone` before you defend pacing.

### Step 3 - Set The Guidance Plan

Say how much help each step or step group should give.
...
```

After, the emitted AGENTS.md stays natural:

```markdown
## Lesson Planning

Plan the lesson from the approved section lesson map, concepts file, and
playable strategy.

### What To Decide

First restate the lesson promise.
Then give every step one explicit role: introduce, practice, test, or
capstone.
Use nearby lessons for continuity evidence.
Use real same-route lessons of similar burden for comparable evidence, and name
any fallback plainly.
Defend the final size against the 90-120s pacing corridor.
Make the step arc, guidance taper, and stable-versus-variable boundaries
explicit.

Do not invent a new route or reopen upstream concept or playable decisions.
```

### Final recommended purpose

`analysis` is a renderable declaration for structured reasoning steps.

It exists to replace long numbered procedural sections with a compact, typed,
reusable surface while still rendering to natural AGENTS.md prose.

### Non-goals

`analysis` does not:

- execute anything
- infer results
- validate produced artifacts
- replace review
- replace workflow law
- become a general-purpose programming language

It is an authored structure with compiler-owned rendering and reference
validation.

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

Anything still judgment-heavy stays as ordinary prose lines inside the same
analysis section.

### Grammar changes

Add `analysis_decl` as a top-level sibling of `workflow_decl` and
`review_decl`.

```lark
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
```

### Why this grammar

This grammar is intentionally narrow:

- it mirrors existing workflow inheritance and section structure
- it reuses existing addressable refs, enums, and path sets
- it adds only four verbs

Those four verbs cover the vast majority of prose-heavy reasoning programs.

### AST and model additions

```python
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
```

### Name resolution rules

`analysis` should be treated as a renderable declaration.

Allowed placements:

- as an agent-authored slot value
- as an override slot value
- as a workflow use target if composition parity with workflows is desired

Not allowed:

- as a `review:` target
- as an `inputs:`, `outputs:`, or `skills:` block target
- as an output schema target

Inside `analysis`:

- ordinary bare refs and path refs use the existing addressable resolution rules
- `classify ... as <name_ref>` must resolve to an enum declaration
- `derive`, `compare`, and `defend` path sets must resolve using the same
  law-path rules already used by preserved scope and support-only comparison

### Inheritance rules

`analysis` should inherit exactly like workflows:

- keyed sections only
- `inherit <section_key>`
- `override <section_key>:`
- missing inherited sections are compile errors
- overriding unknown sections is a compile error

Do not introduce a separate merge model.

### Render rules

The renderer should keep output natural and non-symbolic.

For `analysis`:

- declaration title renders as an H2 section
- each keyed section renders as an H3
- prose lines render normally
- bare refs render as bullets using existing title resolution
- typed statements render as natural sentences

Rendering templates:

```text
derive "Lesson Promise" from {A, B, C}
-> Derive Lesson Promise from A, B, and C.

classify "Step Roles" as StepRole
-> Classify Step Roles using Step Role.

compare "Real Comparable Lessons" against {A, B}
-> Compare Real Comparable Lessons against A and B.

compare "Real Comparable Lessons" against {A, B} using {ComparableRule.same_route, ComparableRule.similar_burden}
-> Compare Real Comparable Lessons against A and B. Use same_route and similar_burden as the comparison basis.

defend "90-120s corridor" using {A, B, C}
-> Defend 90-120s corridor using A, B, and C.
```

The source becomes symbolic.
The rendered AGENTS.md must still read like guidance rather than bytecode.

### Diagnostics

Reserve `E501-E519` for `analysis`.

Minimum diagnostics:

- `E501` unknown analysis enum target
- `E502` non-addressable or unresolved path in analysis basis
- `E503` invalid analysis inheritance target
- `E504` duplicate analysis section key
- `E505` analysis used in unsupported surface
- `E506` empty basis in derive, compare, or defend

### Example ladder entries for analysis

Example 54 - `54_analysis_basic`

Goal:
Introduce the new top-level `analysis` declaration and basic rendering.

What it proves:

- parser accepts `analysis`
- `analysis` renders like a readable runtime section
- keyed inheritance model mirrors workflow
- `derive` and `defend` render naturally

Do not include yet:

- enums
- `schema`
- review integration

Prompt sketch:

```prompt
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
```

Expected render:

A natural AGENTS.md section titled `Briefing Analysis` with stage headings and
templated sentences.

Example 55 - `55_analysis_classify_compare`

Goal:
Add enum-aware `classify` and reference-aware `compare`.

What it proves:

- analysis verbs can resolve enum refs
- analysis can render refs and comparisons cleanly
- compiler errors fire on bad enum refs or empty basis

Add:

- `enum StepRole`
- `classify`
- `compare`

Prompt sketch:

```prompt
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
```

## Schema

### Earliest surface sketch

The first design sketch for `schema` treated it as a richer document-contract
surface with gates:

```prompt
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
```

That sketch captures the core insight:
the valuable compression is not flattening meaning, but compressing schema.

What remains outside Doctrine in that sketch:

- the actual section list
- domain gate names
- the meaning of concepts like "count-only similarity" or "route preservation"

### Before and after example

Before, the review contract is prose:

```markdown
## Shared Lesson Plan Review Contract

At minimum confirm the file has non-empty `Lesson Promise`, `Step Order`,
`Step Roles`, ...
At minimum confirm the lesson does not leave `introduce`, `practice`, `test`,
or `capstone` semantics implied in prose.
At minimum confirm `Real Comparable Lessons` uses real comparable lessons...
At minimum confirm the lesson plan stays inside the route already approved
upstream...
```

After, the authoring surface becomes symbolic:

```prompt
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
```

The emitted AGENTS.md becomes compact and readable:

```markdown
## Shared Lesson Plan Review Contract

Confirm that the lesson plan contains the full lesson promise, step order,
explicit step roles, comparable-lesson proof, and stable-versus-variable
boundaries.

Fail review if step roles are only implied, if comparable proof is only count
similarity, or if the plan quietly invents a new route.
```

### Final recommended purpose

`schema` is a non-renderable contract declaration that centralizes:

- required document sections
- later, optional review gates

It exists to replace large repeated section inventories and shared
"must include" prose.

### Phase split

Phase 1:

- sections only
- attach to outputs
- no review integration yet

Phase 2:

- add optional gates
- allow `review contract:` to target a schema

This phased split keeps the first implementation small and lets the language
use `schema` immediately on producer-output seams without waiting for critic
integration.

### Surface syntax

Phase 1:

```prompt
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
```

Attach to an output:

```prompt
output LessonPlanFile: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: MarkdownDocument
    requirement: Required
    schema: LessonPlanSchema
```

Phase 2:

```prompt
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
```

### Grammar changes

Add a top-level declaration and one reserved output field.

```lark
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
```

Phase 2 review integration:

```lark
contract_stmt: "contract" ":" (workflow_ref | schema_ref) _NL?
schema_ref: name_ref
```

### AST and model additions

```python
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
```

### Static rules

Phase 1:

- a schema must declare at least one section
- section keys are unique
- `output schema:` must resolve to a schema declaration
- an output may attach at most one schema
- in phase 1, an output with `schema:` may not also carry a local
  `must_include:` block

The prohibition on `schema:` plus local `must_include:` is deliberate. There
must not be two owners for the same inventory seam.

Phase 2:

- gate keys are unique
- `review contract:` may resolve to either a workflow review contract or a
  schema
- `contract.some_gate` must resolve against the attached workflow-section keys
  or schema gate keys depending on contract kind
- `contract.passes` remains valid for both kinds

### Inheritance rules

`schema` should inherit like existing keyed block declarations:

- whole-declaration inheritance via `[ParentSchema]`
- `inherit sections`
- `override sections:`
- later, `inherit gates` and `override gates:`

Use inheritance instead of per-entry `when` in the first version. That keeps
the surface simple and keeps route-conditional inventory logic out of the
language core.

### Render rules

Phase 1 output rendering:

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

##### Step Order

State the step order and what each step is there to teach.

...
```

Phase 2 review rendering when a schema is used as contract:

```markdown
## Lesson Plan Review

Review subject: Lesson Plan File.
Shared review contract: Lesson Plan Schema.

### Contract Gate Checks

Reject: Explicit Step Roles.
Reject: No New Route.
Reject: Stable Route Skeleton.
Accept only if The lesson plan schema passes.
```

### Diagnostics

Reserve `E520-E539` for `schema`.

Minimum diagnostics:

- `E520` output schema ref unresolved
- `E521` duplicate schema section key
- `E522` duplicate schema gate key
- `E523` output declares both schema and `must_include` in phase 1
- `E524` review contract references unknown schema gate
- `E525` schema used in unsupported surface
- `E526` schema missing sections

### Example ladder entries for schema

Example 56 - `56_schema_output_contract`

Goal:
Add schema declarations and output attachment.

What it proves:

- parser accepts `schema`
- output can declare `schema:`
- renderer emits required sections from schema
- output cannot simultaneously own `must_include`

Prompt sketch:

```prompt
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
```

Example 57 - `57_schema_inheritance`

Goal:
Prove route- or mode-specific schema extension without adding conditional
schema logic.

What it proves:

- schema inheritance works
- separate variants are cleaner than dynamic conditional sections in v1

Prompt sketch:

```prompt
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
```

Example 60 - `60_schema_review_contract`

Optional second-wave example.

Goal:
Let `review contract:` target schemas with `gates:`.

What it proves:

- schema gate export integrates cleanly with first-class review
- critic can reject on `contract.some_gate`
- gate titles remain exact and readable

Do not build `60_schema_review_contract` until the preceding analysis and schema
examples are green.
