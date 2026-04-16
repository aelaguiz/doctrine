---
title: "Doctrine - Authoring Syntax Sugar Audit - 2026-04-16"
date: 2026-04-16
status: complete
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - doctrine/grammars/doctrine.lark
  - doctrine/parser.py
  - doctrine/_parser/io.py
  - doctrine/_parser/workflows.py
  - doctrine/_parser/reviews.py
  - doctrine/_model/io.py
  - doctrine/_compiler/resolve/refs.py
  - doctrine/_compiler/resolve/addressables.py
  - doctrine/_compiler/resolve/output_schemas.py
  - doctrine/_compiler/validate/contracts.py
  - doctrine/_compiler/validate/agents.py
  - docs/LANGUAGE_REFERENCE.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/REVIEW_SPEC.md
  - docs/WORKFLOW_LAW.md
  - examples/24_io_block_inheritance/prompts/AGENTS.prompt
  - examples/28_addressable_workflow_paths/prompts/AGENTS.prompt
  - examples/79_final_output_output_schema/prompts/AGENTS.prompt
  - examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt
  - examples/107_output_inheritance_basic/prompts/AGENTS.prompt
  - examples/108_output_inheritance_attachments/prompts/AGENTS.prompt
  - examples/117_io_omitted_wrapper_titles/prompts/AGENTS.prompt
  - docs/OMITTED_SUBITEM_TITLES_LOWER_SINGLE_CHILD_SURFACES_2026-04-15.md
  - docs/OMITTED_SUBITEM_TITLES_REUSE_PARENT_TITLES_2026-04-15.md
  - docs/DOCTRINE_LANGUAGE_AUDIT_2026-04-16.md
  - ../rally/src/rally/domain/rooted_path.py
  - ../psflows/flows/prd_factory/prompts/agents/prd_architect/AGENTS.prompt
  - ../psflows/flows/core_dev/prompts/agents/core_dev_lead/AGENTS.prompt
---

# TL;DR

## Outcome

Doctrine has real room for lower-ceremony authoring. The best wins are not
hidden compiler magic. The best wins are parser-level sugar that lowers to the
same typed model Doctrine already ships.

This second pass adds the consistency rule the first draft was missing:
Doctrine should not ship most of these changes as one-off shortcuts on one
favorite surface. If a sugar lowers the same carrier shape, authors will
expect the same sugar across that whole family.

## Biggest wins

1. Add import aliases and symbol imports.
2. Add grouped explicit `inherit` and `override` syntax.
3. Add identity-binding sugar for `review.fields` and
   `final_output.review_fields`.
4. Add one-line IO wrapper refs and wider title elision.
5. Add local path aliases and `self:` style addressable refs.
6. Add compact `output schema` field-head syntax.

## Hard no-go areas

- Do not add hidden merge by omission.
- Do not infer `final_output` from position or vibes.
- Do not infer route ownership from prose.
- Do not add wildcard imports.
- Do not blur `output`, `output shape`, and `final_output` schema ownership.

## Recommended order

1. Import aliases and symbol imports.
2. Grouped explicit patch syntax.
3. Identity-binding sugar for review fields.
4. One-line IO wrapper refs.
5. Local path aliases and `self:` refs.
6. Compact `output schema` field heads.
7. Rooted path literals for `source.path` and `target.path`.

# Scope And Method

This audit is source-first.

I treated `doctrine/` plus the manifest-backed examples as shipped truth. I
used repo docs as secondary context and `../rally` plus `../psflows` as stress
tests for what gets repetitive in real authored systems.

The main proof surfaces were:

- `doctrine/grammars/doctrine.lark`
- `doctrine/parser.py`
- `doctrine/_parser/io.py`
- `doctrine/_parser/workflows.py`
- `doctrine/_parser/reviews.py`
- `doctrine/_compiler/resolve/refs.py`
- `doctrine/_compiler/resolve/addressables.py`
- `doctrine/_compiler/resolve/output_schemas.py`
- `doctrine/_compiler/validate/contracts.py`
- `doctrine/_compiler/validate/agents.py`
- `examples/24`, `28`, `79`, `106`, `107`, `108`, `117`
- `../psflows/flows/prd_factory/prompts/agents/prd_architect/AGENTS.prompt`
- `../psflows/flows/core_dev/prompts/agents/core_dev_lead/AGENTS.prompt`

# What The Source Already Allows

Doctrine already proves a few good sugar patterns.

- `inputs`, `outputs`, `skills`, and `final_output` already accept ref or
  inline forms through shared model unions.
- IO wrapper titles may already be omitted when the section lowers to exactly
  one direct child and there are no keyed child wrappers.
- Workflow sections already accept low-ceremony local section syntax.
- `output schema` variants already support a keyed or unkeyed authored form
  that lowers to the same model.

This matters because it shows the safe pattern: add sugar in the parser, lower
early, and keep one compile path.

# Hard Guardrails From Source

The shipped compiler is strict in the places that matter. Any sugar should keep
these rules intact.

## 1. Parent accounting must stay explicit

Inherited `workflow`, `skills`, `inputs`, `outputs`, `review`, `document`,
`output schema`, and top-level `output` surfaces all require explicit parent
coverage. Missing inherited items fail loud today. That is good.

This rules out hidden "keep the rest" merge behavior as the default model.

## 2. Key identity must stay stable

Doctrine validates keyed child identity and kind. Sugar cannot silently rename
or auto-merge keyed children under the hood.

## 3. Route surfaces are already tightly constrained

Agents cannot carry multiple conflicting route-bearing control surfaces. Sugar
must not infer routing from output fields or review prose.

## 4. `schema:` ownership is sensitive

`schema:` means different things on `output`, `output shape`, and
`final_output`. Sugar should not flatten those into one fuzzy surface.

## 5. `final_output` stays explicit

The compiler requires an explicit `final_output` choice. Sugar may shorten that
syntax, but it should not guess the final carrier when multiple outputs exist.

# Second-Level Consistency Audit

This pass asks a stricter question than the first pass.

It is not enough to ask, "Where is this most painful?" We also need to ask,
"What other shipped surface uses the same underlying shape, so a partial
rollout would feel arbitrary?"

## 1. Follow carrier shapes, not declaration names

If a sugar lowers the same carrier shape, it should usually ship across the
whole family.

- `name_ref` and declaration-root `dotted_name` carriers should move together.
- explicit inherited keyed-item carriers should move together.
- semantic binding-map carriers should move together.
- section-wrapper carriers should move together only when omitted-title meaning
  is the same.
- `AddressableRef` carriers should move together.
- `output schema` typed child-item carriers should move together.
- typed path-value carriers should move together.

## 2. Partial rollouts that would feel arbitrary

These are the asymmetries Doctrine should avoid.

- Import aliases that work in `inputs:` but not in `route`, `inheritance`, or
  `schema:` refs.
- Grouped `inherit` on `output` but not on `workflow`, `skills`, `inputs`,
  `outputs`, `review`, `law`, or `output schema`.
- Bare identity bindings in `review.fields` but not in `override fields` or
  `final_output.review_fields`.
- One-line wrapper refs in `outputs` but not `inputs`.
- `self:` addressable refs in workflow bodies but not in output record refs or
  interpolation.
- Compact `output schema` heads only on top-level `field` and not on
  `override field`, nested `field`, or variant bodies.
- Rooted path literals in `input` but not `output`.
- Owner aliases in plain workflow `route` but not in `route_only`, review
  outcome routes, grounding policy routes, `law route`, or `route_from`.

## 3. Intentional asymmetries that are still fine

Some asymmetry is real and should stay.

- Omitted-title lowering is not the same as inherited-title reuse.
- `field_path` is not the same as `name_ref`.
- `path_ref` is not the same as `law_path`.
- Generic prose strings are not typed paths.
- `final_output` can gain shorthand, but it should stay an explicit agent-only
  control surface.

## 4. Consistency matrix by underlying carrier

### 4.1 `name_ref` and declaration-root `dotted_name`

If Doctrine adds import aliases or symbol imports, the new spelling should
resolve anywhere these carriers appear:

- inheritance parents like `Decl[Parent]`
- agent typed fields like `inputs`, `outputs`, `analysis`, `decision`,
  `skills`, `review`, and `final_output`
- workflow `use`, workflow `skills`, and workflow section refs
- record refs and output record refs
- skill entries
- review `subject`, `subject_map`, `contract`, and `comment_output`
- route targets in workflow, review, route-only, grounding, and law
- output attachments like `schema`, `structure`, `render_profile`, and
  `delivery_skill`
- render profile refs
- review selector enum refs
- declaration-root portions of addressable refs and law paths

### 4.2 Explicit inherited keyed-item carriers

If Doctrine adds grouped explicit patch syntax, it should cover every shipped
surface that already repeats singular `inherit` lines:

- agent authored slots
- workflow items
- workflow law sections
- skills blocks
- inputs blocks
- outputs blocks
- analysis sections
- schema block families
- document blocks
- review items
- output items and output attachments
- output shape items
- output schema items

### 4.3 Semantic binding maps

If Doctrine adds identity-binding sugar, it should cover every surface that
stores the same `ReviewFieldsConfig`-style map:

- `review fields:`
- `review override fields:`
- `final_output.review_fields:`

### 4.4 Section-wrapper carriers

If Doctrine adds one-line wrapper refs or omitted-title lowering, it should be
explicit about which wrapper family it belongs to:

- first-class IO wrappers
- generic record wrappers
- output record wrappers
- readable blocks
- inherited overrides

Those families do not all mean the same thing today, so they need one matrix,
not one vague "titles are optional now" story.

### 4.5 `AddressableRef` carriers

If Doctrine adds `self:` or local addressable aliases, the sugar should work
across every surface that already accepts `path_ref`:

- workflow section ref items
- record scalar heads
- output record scalar heads
- guarded output scalar heads
- output override scalar heads
- string interpolation that reuses addressable refs

### 4.6 `output schema` typed child-item carriers

If Doctrine adds compact field-head syntax, it should cover the whole child
item family, not only one node kind:

- `field`
- nested `field`
- `override field`
- `def`
- `override def`
- fields nested under `items:`
- fields nested under `any_of` variants

### 4.7 Typed path-value carriers

If Doctrine adds rooted path literals or path-root aliases, the sugar should
cover every typed path field, not just one declaration spelling:

- `input` file paths
- `input source` file paths
- `output` file targets
- `output target` file targets

# Repetition Pressure, In Numbers

These counts came from the shipped examples and the two sibling repos used as
pressure tests.

- `outputs: "Outputs"` appears 224 times in `examples/`.
- `inputs: "Inputs"` appears 133 times in `examples/`.
- `target: TurnResponse` appears 202 times in `examples/`.
- `shape: Comment` appears 168 times in `examples/`.
- `shape: MarkdownDocument` appears 181 times in `examples/`.
- `source: File` appears 150 times in `examples/`.
- `verdict: verdict` appears 57 times in `examples/`.
- `reviewed_artifact: reviewed_artifact` appears 55 times in `examples/`.
- `next_owner: next_owner` appears 57 times in `examples/`.
- `inherit target` appears 10 times in `examples/`.
- `inherit shape` appears 9 times in `examples/`.
- `inherit requirement` appears 9 times in `examples/`.
- `output schema` field declarations appear 45 times in `examples/`.
- `type: string` appears 32 times in those schema fields.
- `required` appears 32 times in those schema fields.
- Fully qualified refs with 2 or more dots appear about 121 times in the
  audited Rally surfaces and about 1316 times in the audited Psflows surfaces.

The pressure is not spread evenly. The biggest pain is in:

- long qualified refs
- inherited outputs and schemas
- repeated IO wrappers
- repeated review-field identity maps
- simple schemas that require many lines for small meaning

# Ranked Audit

## Rank 1. Import aliases and symbol imports

### Why this is high value

This is the cleanest win.

Today Doctrine supports `import module`, but not `import module as alias`, not
`from module import Name`, and not `from module import Name as alias`. That
forces long qualified refs everywhere, especially in real repos like Psflows.

This is the main reason custom fields, routes, analysis stages, and schemas
feel noisy even when the underlying structure is good.

### Evidence

- `doctrine/grammars/doctrine.lark` only accepts module imports.
- `doctrine/_compiler/resolve/refs.py` resolves local names or fully qualified
  imported module refs.
- `../psflows/flows/prd_factory/prompts/agents/prd_architect/AGENTS.prompt`
  repeats deep paths like
  `prd_factory.contracts.problem_framer.ProblemFrameContract`.
- `../psflows/flows/core_dev/prompts/agents/core_dev_lead/AGENTS.prompt`
  repeats long refs in outputs, routes, and currentness rules.

### Best-case syntax

```doctrine
import prd_factory.common.agents as agents
import prd_factory.contracts.problem_framer as problem_framer

from prd_factory.contracts import review as review_contract
from prd_factory.common.agents import ProblemFramer, StrategyOwner
```

Then authored refs become:

```doctrine
prove "Package Proof" from {problem_framer.ProblemFrameContract, SharedPrdContract}

route "When the run should stop early" -> StrategyOwner
route "When package work can start" -> ProblemFramer
```

### Lowering rule

Alias resolution should happen during name resolution only. It should lower to
the same fully qualified declaration ref Doctrine already compiles today.

### Inspiration

- Python `import ... as ...`
- Python `from ... import ...`
- Rust `use path::Name as Alias`

### Recommendation

Ship this first.

### Consistency sweep

If Doctrine ships aliasing here, it should also work everywhere the language
already accepts `name_ref` or a declaration-root `dotted_name`.

- inheritance parents like `workflow Child[Parent]`
- agent typed refs like `inputs:`, `outputs:`, `analysis:`, `decision:`,
  `skills:`, `review:`, and `final_output:`
- workflow `use`, workflow `skills`, and workflow section ref items
- skill entries and record refs
- output attachments like `schema:`, `structure:`, `render_profile:`, and
  `delivery_skill:`
- review `subject`, `subject_map`, `contract`, `comment_output`, selector
  enum refs, and outcome route targets
- route targets in `workflow`, `law`, `route_only`, and grounding policy
- declaration roots inside addressable refs like `Alias:deep.path`
- declaration roots inside law paths and analysis path sets

If it does not work in all of those places, the feature will feel arbitrary.

What should stay out:

- `field_path` inside review bindings
- generic prose strings
- literal file paths

## Rank 2. Grouped explicit `inherit` and `override`

### Why this is high value

This directly hits the pain the user called out.

Right now a child output or schema that changes one thing still needs a tall
stack of `inherit ...` lines just to restate unchanged parent facts.

### Evidence

`examples/107_output_inheritance_basic/prompts/AGENTS.prompt`:

```doctrine
output LessonsLeadOutput[BaseReply]: "Lessons Lead Output"
    inherit target
    inherit shape
    inherit requirement
    inherit summary
```

`examples/108_output_inheritance_attachments/prompts/AGENTS.prompt`:

```doctrine
output RoutedReviewComment[BaseReviewComment]: "Routed Review Comment"
    inherit target
    inherit shape
    inherit render_profile
    inherit requirement
    inherit current_artifact
```

`examples/79_final_output_output_schema/prompts/AGENTS.prompt` shows the same
pattern in `output schema` and `output shape`.

### Best-case syntax

```doctrine
output LessonsLeadOutput[BaseReply]: "Lessons Lead Output"
    inherit {target, shape, requirement, summary}

    hit: "Test"
        "blah blah blah"
```

```doctrine
output RoutedReviewComment[BaseReviewComment]: "Routed Review Comment"
    inherit {target, shape, render_profile, requirement, current_artifact}

    next_owner: "Next Owner"
        "Name the next owner when follow-up is needed."

    override standalone_read: "Standalone Read"
        "This comment should stand on its own."
        "It should also name the next owner when one exists."

    override trust_surface:
        current_artifact
        next_owner
```

```doctrine
output schema RepoStatusSchema[BaseRepoStatusSchema]: "Repo Status Schema"
    inherit {summary, status}

    field next_step?: string "Next Step"
        note: "Null only when no follow-up is needed."

    override example:
        summary: "Branch is clean and checks passed."
        status: "ok"
        next_step: null
```

### Lowering rule

Grouped syntax should expand to the same explicit per-item patch records the
compiler already expects.

### Recommendation

Ship grouped explicit lists.

Do not ship `inherit *` as the default form. It is tempting, but it weakens
the fail-loud accounting Doctrine already enforces.

### Consistency sweep

If Doctrine ships grouped `inherit`, it should apply to every inherited family
that already repeats singular `inherit` items.

- agent authored slots
- workflow items
- workflow `law` sections
- skills blocks
- inputs blocks
- outputs blocks
- analysis sections
- schema block families
- document blocks
- review items
- output items and attachments
- output shape items
- output schema items

Grouped `inherit` is the real consistency requirement.

Grouped `override` is more limited. It should only ship on surfaces where the
override unit is still one explicit keyed patch after lowering. Do not force a
grouped `override` form onto every multiline override surface just for visual
symmetry.

That means these asymmetries are fine:

- keep rich multiline override bodies like `override on_accept:` in their
  current form
- keep `override section foo:` style forms where the body is already the unit
- keep explicit override values for `schema`, `structure`, and
  `render_profile`

## Rank 3. Identity-binding sugar for `review.fields` and `final_output.review_fields`

### Why this is high value

Review surfaces repeat the same semantic field names again and again, even when
the authored field path is identical.

This is one of the clearest "I said the same thing twice" problems in the
whole language.

### Evidence

`examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt`
contains both:

```doctrine
fields:
    verdict: verdict
    reviewed_artifact: reviewed_artifact
    current_artifact: current_artifact
    next_owner: next_owner
```

and:

```doctrine
final_output:
    output: AcceptanceControlFinalResponse
    review_fields:
        current_artifact: current_artifact
        next_owner: next_owner
```

The identity-binding counts are high across the corpus.

### Best-case syntax

```doctrine
review AcceptanceReview: "Acceptance Review"
    subject: DraftPlan
    contract: PlanReviewContract
    comment_output: AcceptanceReviewComment

    fields:
        verdict
        reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        current_artifact
        failing_gates: failure_detail.failing_gates
        blocked_gate: failure_detail.blocked_gate
        next_owner
```

```doctrine
final_output:
    output: AcceptanceControlFinalResponse
    review_fields:
        current_artifact
        next_owner
```

### Lowering rule

A bare semantic field name should lower to `semantic_name: semantic_name`.

Anything non-identity should still require the explicit `semantic: path` form.

### Recommendation

Ship this early. It is small, obvious, and safe.

### Consistency sweep

If Doctrine ships identity-binding sugar here, it should cover the whole
semantic-binding family, not just one spelling.

- `review fields:`
- `review override fields:`
- `final_output.review_fields:`

The shorthand should work for every semantic field name, not just the most
common ones:

- `verdict`
- `reviewed_artifact`
- `analysis`
- `readback`
- `current_artifact`
- `failing_gates`
- `blocked_gate`
- `next_owner`
- `active_mode`
- `trigger_reason`

What should stay out:

- `subject_map`
- `trust_surface`
- arbitrary `field_path` settings outside review-field binding maps

## Rank 4. One-line IO wrapper refs and wider title elision

### Why this is high value

Doctrine already has one narrow version of this. Example 117 proves the parser
and resolver can lower omitted IO wrapper titles when there is one clear child.

The next step is to make the common one-ref wrapper concise.

### Evidence

`examples/24_io_block_inheritance/prompts/AGENTS.prompt`:

```doctrine
inputs BaseSectionInputs: "Your Inputs"
    scoped_catalog_truth: "Scoped Catalog Truth"
        ScopedCatalogTruth
```

`examples/117_io_omitted_wrapper_titles/prompts/AGENTS.prompt` already allows:

```doctrine
outputs SectionDossierOutputs: "Your Outputs"
    section_handoff:
        SectionHandoff
```

### Best-case syntax

```doctrine
inputs BaseSectionInputs: "Your Inputs"
    scoped_catalog_truth: ScopedCatalogTruth

    continuity_only: ForwardContinuityPacket
        "Use continuity evidence to re-earn the section."
        "Read one section ahead when the review calls for it."
```

```doctrine
outputs SectionDossierOutputs: "Your Outputs"
    section_handoff: SectionHandoff
```

### Lowering rule

The one-line form should lower to the same wrapper node as the existing
multiline form. The child declaration title should still own the default title
when no wrapper title is present.

### Recommendation

Ship this after grouped patch lists.

### Consistency sweep

This proposal really contains two linked conventions. They should not be
blended into one vague "shorter sections" story.

One-line wrapper refs should propagate to the whole first-class IO family:

- `inputs` blocks
- `outputs` blocks
- base wrapper entries
- `override` wrapper entries

Agent inline `inputs:` and `outputs:` are an adjacent expectation surface, not
the same owner path. They already have one-line keyed-ref forms through
generic `record_body`, which is exactly why first-class IO looks inconsistent
today.

The good news is that generic record bodies and output record bodies already
have a one-line keyed-ref form. So the consistency move here is mostly to make
first-class IO wrappers match the rest of the record language.

Omitted-title behavior needs a stricter matrix:

- base IO wrappers may lower when one child clearly owns the visible heading
- inherited override wrappers may keep the inherited title instead
- titleless readable lists already lower into the parent
- generic record sections, output sections, workflow sections, and document
  sections should not silently inherit the IO rule unless they get their own
  coherent lowering story

If Doctrine widens title omission, it should do so by family, not by one
surface at a time.

## Rank 5. `self:` refs and local path aliases

### Why this is high value

Deep addressable refs are one of Doctrine's best features, but they get noisy
fast when authors repeat the same root and long path chain.

### Evidence

`examples/28_addressable_workflow_paths/prompts/AGENTS.prompt` repeats:

```doctrine
ReviewRules:gates.build.check_build_honesty
```

Psflows shows the same pattern with deep contract and schema paths used across
analysis, routes, and readback rules.

### Best-case syntax

For same-declaration refs:

```doctrine
workflow ReviewRules: "Review Rules"
    gates: "Gates"
        build: "Build"
            check_build_honesty: "Check Build Honesty"
                "Compare the current build to the plan before you accept it."

    read_first: "Read First"
        review_sequence: "Review Sequence"
            self:gates
            self:gates.build.check_build_honesty
            "Run {{self:gates.build.check_build_honesty}} before you route the work."
```

For reusable local aliases:

```doctrine
alias honest_gate = ReviewRules:gates.build.check_build_honesty

output ReviewComment: "Review Comment"
    target: TurnResponse
    shape: MarkdownDocument
    requirement: Required

    honest_gate: honest_gate
```

### Lowering rule

- `self:path.to.node` lowers to the current declaration root plus the same path.
- `alias name = ref` lowers to a local immutable ref binding only.

### Inspiration

- Python and Rust `self`
- SQL and functional-language local aliases

### Recommendation

Ship same-declaration `self:` first. Add general aliases only if the grammar
stays clean.

### Consistency sweep

If `self:` ships, it should work on every surface that already accepts an
`AddressableRef`, not only workflow ref lists.

- workflow section ref items
- record scalar heads
- output record scalar heads
- guarded output scalar heads
- output override scalar heads
- string interpolation that reuses addressable refs

If local addressable aliases ship, they should work anywhere an addressable ref
already works after lowering. Otherwise authors will have to remember a second
arbitrary split.

What should stay separate:

- `law_path` and `path_set_expr` are not `AddressableRef`
- plain declaration refs do not need the same `self:` syntax

## Rank 6. Compact `output schema` field-head syntax

### Why this is high value

Small schemas cost too many lines.

Today a basic string field needs four lines even when the author only wants
"this is a required string with this title and note."

### Evidence

The examples contain 45 field declarations, 32 `type: string` lines,
32 `required` lines, and 35 `note:` lines.

`examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt`
shows the common pattern:

```doctrine
field current_artifact: "Current Artifact"
    type: string
    nullable
    note: "Current artifact after review."
```

### Best-case syntax

For simple scalar fields:

```doctrine
field current_artifact: string? "Current Artifact"
    note: "Current artifact after review."

field next_owner: string? "Next Owner"
    note: "Next owner after review when one exists."
```

For simple enums:

```doctrine
field status: enum {ok, action_required} "Status"
    note: "Current repo outcome."
```

For fields that still need the full form:

- nested object structure
- arrays with extra settings
- anything with validators or future richer metadata

### Lowering rule

Field-head sugar should lower to the exact same `OutputSchemaField` model:

- `name`
- `title`
- `type`
- nullability
- inline enum values where present

### Inspiration

- Kotlin and Swift compact typed field heads

### Recommendation

Ship the simple scalar and enum forms first. Keep the current multiline form
for richer fields.

### Consistency sweep

If compact heads ship, they should cover the whole `output schema` child-item
family, not just one top-level node kind, at least for the simple property
cases Doctrine expects authors to write often.

- `field`
- nested `field`
- `override field`
- fields inside `items:`
- fields inside `any_of` variants

If inline enum heads ship, they should follow the same propagation rule.

The nullability cleanup direction is now clear enough to simplify this
proposal. `nullable` is the authored concept on this surface, while legacy
`required` and `optional` are retired with targeted upgrade errors. If
Doctrine adds symbolic compact heads, they should track nullability, not
property presence. `string?` is the cleaner shape here. `field_name?: string`
would still read like an omittable property in too many other languages.

One acceptable asymmetry remains: `def` and `override def` may stay on the
long form if Doctrine decides the compact head is specifically about
object-property presence, not generic reusable schema fragments.

## Rank 7. Rooted path literals for `source.path` and `target.path`

### Why this is high value

Path-heavy systems repeat the same path roots and folder prefixes over and
over. Rally already solved this in its own rooted-path domain model.

This would help Doctrine authoring without changing Doctrine's runtime scope.

### Evidence

Many inputs and outputs in the examples and sibling repos repeat roots like:

- `unit_root/...`
- `section_root/...`
- `catalog/...`
- `PrdRoot/...`

### Best-case syntax

Minimal rooted path form:

```doctrine
input DraftPlan: "Draft Plan"
    source: File
        path: workspace:"unit_root/DRAFT_PLAN.md"
    shape: MarkdownDocument
    requirement: Required
```

With local root aliases:

```doctrine
path roots:
    unit_root = workspace:"unit_root"
    authoring = workspace:"section_root/_authoring"

output DurableSectionTruth: "Durable Section Truth"
    target: File
        path: authoring:"durable_section_truth.md"
    shape: MarkdownDocument
    requirement: Required
```

### Lowering rule

This should lower to the same plain path string or structured path record that
Doctrine already emits today. It should not change harness ownership of files.

### Inspiration

- Rally rooted paths

### Recommendation

Good medium-priority improvement. Keep it limited to path-valued fields.

### Consistency sweep

If rooted path literals or path-root aliases ship, they should cover every
typed file-path owner surface:

- `input` declarations
- `input source` declarations
- `output` declarations
- `output target` declarations

They should also preserve one shared path-root vocabulary across those
surfaces. Do not make `workspace:` valid in one and `root:` valid in another.

What should stay out:

- import paths
- addressable refs
- generic prose strings
- review field paths

## Rank 8. Compact head syntax for common input and output contracts

### Why this is useful

Simple IO declarations are very repetitive:

- source or target kind
- path or env
- shape
- requirement

This is a real pain, but it is a bigger grammar change than the earlier items.

### Evidence

The examples repeat:

- `target: TurnResponse` 202 times
- `shape: Comment` 168 times
- `shape: MarkdownDocument` 181 times
- `source: File` 150 times

### Best-case syntax

```doctrine
input DraftPlan: file("unit_root/DRAFT_PLAN.md") -> MarkdownDocument required

output FinalReply: turn_response -> Comment required

output DurableSectionTruth: file("section_root/_authoring/durable_section_truth.md") -> MarkdownDocument required
```

### Lowering rule

This should lower to the same `source`, `target`, `shape`, and `requirement`
fields Doctrine already uses.

### Recommendation

Keep this behind the earlier parser wins. It is attractive, but it widens the
grammar more than aliasing, grouped patching, or review-field sugar.

### Consistency sweep

If Doctrine adds compact IO heads, it should cover the whole typed IO family,
at least for the main authored pair authors use most often.

- `input`
- `output`

The constructor vocabulary should stay aligned too. If Doctrine uses
`file(...)`, `env(...)`, `prompt(...)`, and `turn_response`, those same ideas
should read the same way across input and output declarations.

What should stay explicit:

- inherited output patching
- `inputs` and `outputs` block wrappers
- `final_output`, which is not an IO declaration

One staged asymmetry is acceptable here:

- `input source`
- `output target`

Those declarations have extra owner-specific attachments today, so it is fine
to leave them on the long form in an early cut as long as plain `input` and
plain `output` move together.

## Rank 9. Named ref sets for repeated analysis and law inputs

### Why this is useful

Large analysis blocks often repeat the same set of refs across multiple stages.
That is obvious duplication.

### Evidence

`../psflows/flows/prd_factory/prompts/agents/prd_architect/AGENTS.prompt`
repeats the same large contract set for `prove`, `derive`, `compare`, and
`defend`.

### Best-case syntax

```doctrine
ref set PackageBasis:
    problem_framer.ProblemFrameContract
    copy_specifier.CopySpecContract
    learning_specialist.LearningContract
    experience_designer.ExperienceDesignContract
    design_reviewer.DesignReviewContract
    delivery_engineer.DeliveryShapeContract
    measurement_owner.MeasurementArtifactContract
    strategy_owner.StrategyArtifactContract
    shared_refs.SharedOverlayMap
    shared_refs.SharedPrdContract

analysis PrdArchitectAnalysis: "PRD Architect Analysis"
    stages: "Stages"
        prove "Package Proof" from PackageBasis
        derive "Package Basis Derivation" from PackageBasis
        compare "Contradiction Comparison" against PackageBasis
        defend "Assembly Defense" using PackageBasis
```

### Lowering rule

Expand the named set at parse or resolve time into the same explicit set of
refs the compiler already understands.

### Recommendation

Useful for large systems. Lower priority for core Doctrine ergonomics.

### Consistency sweep

If Doctrine adds named ref sets, they should work everywhere the grammar
already accepts `path_set_expr`.

- analysis `prove`
- analysis `derive`
- analysis `compare`
- analysis `defend`
- law `own only`
- law `preserve`
- law `support_only`
- law `ignore`
- law `forbid`

The set form should also compose with existing `except` syntax. Otherwise the
feature will remove one kind of repetition while adding a new special case.

What should stay separate:

- arbitrary `expr_set`
- review subject sets, which are artifact refs, not law-path sets

## Rank 10. Route owner aliases

### Why this is useful

Routes often repeat the same owner namespace.

Import aliases solve much of this already, so this is not the first change I
would ship. Still, it could help large multi-owner systems.

### Best-case syntax

```doctrine
import prd_factory.common.agents as agents

routing_rules: "Routing Rules"
    route "When package work can start" -> agents.ProblemFramer
    route "When the run should stop early" -> agents.StrategyOwner
```

Or, if Doctrine wants a dedicated route surface:

```doctrine
owner scope: prd_factory.common.agents

routing_rules: "Routing Rules"
    route "When package work can start" -> ProblemFramer
    route "When the run should stop early" -> StrategyOwner
```

### Recommendation

Import aliasing probably makes this unnecessary. Treat it as optional.

### Consistency sweep

If Doctrine adds a dedicated route-owner namespace anyway, it should cover the
whole route-bearing family:

- workflow `route`
- law `route`
- `route_from`
- review outcome routes
- `route_only` route tables
- grounding policy routes

If it only works in one routing surface, authors will still have to remember
two route dialects.

## Rank 11. `final_output` projection sugar

### Why this is useful

Split review flows often restate the chosen output plus a small projection of
review fields.

### Best-case syntax

```doctrine
final_output AcceptanceControlFinalResponse from review:
    current_artifact
    next_owner
```

### Lowering rule

This must still lower to:

- one explicit chosen output
- one explicit set of review-field bindings

### Recommendation

Helpful, but only after identity-binding sugar exists.

### Consistency sweep

If Doctrine adds `final_output` projection sugar, it should line up with every
existing public `final_output` form:

- bare `final_output: NameRef`
- block `final_output:` plus `output: NameRef`
- block `final_output:` plus `review_fields:`

The projection story should also reuse the same identity-binding shorthand as
review-field maps. Otherwise split review finals will have two similar but
different mini-languages.

What should stay explicit:

- the chosen output
- the fact that this is the agent final output surface

## Rank 12. Wider title defaulting on readable blocks

### Why this is useful

Many readable blocks repeat the same key and title in two forms.

### Best-case syntax

```doctrine
section overview:
    "Summarize the current state."

callout durable_truth required:
    "Keep this true across the turn."
```

### Recommendation

Useful, but not part of the highest-value IO and inheritance pain.

### Consistency sweep

If Doctrine widens title defaulting or title omission on readable blocks, it
should do so across the full readable family, not only one declaration owner.

- document readable blocks
- workflow root readable blocks
- record readable blocks
- output readable blocks

It also needs one clear omitted-title matrix across:

- titleless readable lists that lower into the parent
- inherited overrides that keep the inherited title
- any new base wrapper lowering rules

That matrix is already tricky enough in the repo today. Do not widen it
without one explicit public rule per family.

# Safe Now Vs Risky Later

## Safe now

- import aliases
- symbol imports
- grouped explicit patch lists
- identity review-field sugar
- one-line IO wrapper refs
- `self:` path refs
- compact simple schema field heads

## Safe but larger

- rooted path literals
- compact IO head syntax
- named ref sets
- `final_output` projection sugar

## Risky and not recommended for a first cut

- `inherit *` as the default inheritance model
- hidden keep-rest merge by omission
- inferred `final_output` from the last authored output
- wildcard imports
- route inference from `next_owner` or other output field names
- any sugar layered onto review selector syntax before the current
  grammar-parser mismatch is fixed

# Specific Notes On The User's Main Pain Points

## Outputs

Outputs are the loudest pain surface today.

The main waste is not the output body. The main waste is the wrapper syntax
around it:

- repeated `target`, `shape`, and `requirement`
- repeated inherited attachment keep-lists
- repeated route and current-artifact readback fields

The best first answer is:

1. grouped `inherit { ... }`
2. compact head syntax for simple outputs
3. identity sugar where review semantics mirror output field names

## Inputs

Inputs mostly suffer from repeated file-path and shape setup plus wrapper
ceremony inside `inputs:` blocks.

The best first answer is:

1. one-line IO wrappers
2. rooted paths
3. compact input head syntax

## Inheritance

Doctrine is right to stay explicit here. The problem is not that inheritance is
explicit. The problem is that the explicit form is too line-heavy.

Grouped patch lists solve most of that without weakening safety.

## Custom fields

Most custom-field pain is really import pain.

`your_job`, `analysis`, `decision`, `grounding`, and route fields become much
lighter once authors can alias module roots and import declaration names
directly.

## Schemas

Schemas need two kinds of sugar:

1. compact field heads for simple scalar and enum fields
2. grouped inheritance lists for child schemas and output shapes

# Best Rollout Plan

If Doctrine wants the biggest improvement per unit of parser work, ship in this
order:

1. Import aliases and symbol imports.
2. Grouped explicit `inherit` and `override`.
3. Identity-binding sugar for `review.fields` and `review_fields`.
4. One-line IO wrapper refs.
5. `self:` addressable refs.
6. Compact simple `output schema` field heads.
7. Rooted path literals.
8. Compact IO head syntax.

# Final Recommendation

Doctrine should chase lower-ceremony authoring, but it should do it in the same
style it already uses well:

- parser sugar
- early lowering
- one semantic model
- fail loud when authors leave meaning unclear

The single best near-term move is import aliasing plus grouped explicit patch
lists. Those two changes alone would remove a large share of the repeated
syntax in `outputs`, `inputs`, inheritance-heavy contracts, and custom fields
without changing Doctrine's safety model.
