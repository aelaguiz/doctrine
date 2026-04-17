---
title: "Doctrine - Recurring Verbose Authoring Patterns Audit - 2026-04-16"
date: 2026-04-16
status: complete
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: audit
related:
  - doctrine/grammars/doctrine.lark
  - docs/LANGUAGE_REFERENCE.md
  - docs/REVIEW_SPEC.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - examples/21_first_class_skills_blocks/prompts/AGENTS.prompt
  - examples/22_skills_block_inheritance/prompts/AGENTS.prompt
  - examples/23_first_class_io_blocks/prompts/AGENTS.prompt
  - examples/24_io_block_inheritance/prompts/AGENTS.prompt
  - examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt
  - examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt
  - examples/48_review_inheritance_and_explicit_patching/prompts/AGENTS.prompt
  - examples/68_review_family_shared_scaffold/prompts/AGENTS.prompt
  - examples/73_flow_visualizer_showcase/prompts/AGENTS.prompt
  - examples/79_final_output_output_schema/prompts/AGENTS.prompt
  - examples/92_route_from_basic/prompts/AGENTS.prompt
  - examples/94_route_choice_guard_narrowing/prompts/AGENTS.prompt
  - examples/104_review_final_output_output_schema_blocked_control_ready/prompts/AGENTS.prompt
  - examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt
  - examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt
  - examples/107_output_inheritance_basic/prompts/AGENTS.prompt
  - examples/108_output_inheritance_attachments/prompts/AGENTS.prompt
  - examples/109_imported_review_handoff_output_inheritance/prompts/AGENTS.prompt
  - examples/110_final_output_inherited_output/prompts/AGENTS.prompt
  - examples/111_inherited_output_route_semantics/prompts/AGENTS.prompt
  - examples/117_io_omitted_wrapper_titles/prompts/AGENTS.prompt
  - examples/118_output_target_delivery_skill_binding/prompts/AGENTS.prompt
  - examples/120_route_field_final_output_contract/prompts/AGENTS.prompt
  - examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt
  - ../psflows/flows/lessons/prompts/agents/section_architect/AGENTS.prompt
  - ../psflows/flows/lessons/prompts/contracts/lesson_plan.prompt
  - ../psflows/flows/prd_factory/prompts/contracts/review.prompt
---

# TL;DR

The biggest remaining repetition is not in imports or grouped `inherit`.
Doctrine already ships good sugar for those.

The biggest remaining repetition is in four places:

1. agent-local `inputs` and `outputs` lists
2. review semantic field maps
3. split `final_output` blocks
4. `output schema` field heads

The later examples make that clear. Real repo prompts in `../psflows` confirm
it.

# Scope And Method

This audit is source-first.

I used the shipped grammar and docs to confirm what Doctrine already supports.
Then I sampled the corpus broadly, with extra weight on later examples that
teach reviews, final outputs, routes, output schemas, inheritance, and package
surfaces.

Main corpus sample:

- `21` through `24` for first-class `skills`, `inputs`, and `outputs`
- `28` for addressable `self:` refs
- `43`, `48`, and `68` for review fields and review reuse
- `73` and `74` for multi-agent and decision surfaces
- `79`, `87`, `88`, `90`, `91`, `92`, `94` for final outputs and route truth
- `104` through `111` for review JSON finals and `output[...]` inheritance
- `117`, `118`, `120`, and `121` for omitted titles, delivery skill binding,
  and routed final outputs

I also spot-checked real prompt families in `../psflows` to see which patterns
still hurt outside the teaching corpus.

Fast corpus counts from this pass:

- `87` example dirs still use inline agent `inputs: "Inputs"` or
  `outputs: "Outputs"` wrappers.
- `21` example dirs use review `fields:` blocks.
- `21` example dirs use `final_output:`.
- `12` example dirs declare `output schema`.
- `23` example dirs use explicit `inherit`.
- `52` example dirs use `standalone_read`.
- `43` example dirs use `next_owner`.

# First Cut: What Is Already Solved

These patterns still look repetitive in some files, but the language already
has a good answer. The right fix is adoption, linting, or example cleanup.

## 1. Long inherit runs are partly a style problem now

Doctrine already ships grouped `inherit { ... }` across workflow, review,
analysis, schema, document, `skills`, `inputs`, `outputs`, `output`,
`output schema`, law, and agent-slot surfaces.

Good shipped examples:

- `examples/24_io_block_inheritance/prompts/AGENTS.prompt`
- `examples/107_output_inheritance_basic/prompts/AGENTS.prompt`
- `examples/108_output_inheritance_attachments/prompts/AGENTS.prompt`

Real repo prompts still often spell these one line at a time:

- `../psflows/flows/lessons/prompts/contracts/lesson_plan.prompt`
- `../psflows/flows/lessons/prompts/contracts/section_playable_strategy.prompt`
- `../psflows/flows/prd_factory/prompts/contracts/contract.prompt`

This is a real repetition hotspot, but it is mostly an adoption gap. A linter
or codemod would pay off faster than new syntax here.

## 2. Identity review bindings already got better

Doctrine already allows bare semantic names in `fields:`, `override fields:`,
and `final_output.review_fields:` when the bind is identity-shaped.

Good shipped examples:

- `examples/104_review_final_output_output_schema_blocked_control_ready/prompts/AGENTS.prompt`
- `examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt`
- `examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt`

Older examples still show the longer form:

- `examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt`
- `examples/48_review_inheritance_and_explicit_patching/prompts/AGENTS.prompt`
- `examples/68_review_family_shared_scaffold/prompts/AGENTS.prompt`

Again, this is partly corpus drift. It is not a new parser gap by itself.

## 3. Import aliasing and `self:` already reduce long path noise

Doctrine already ships:

- `from ... import Symbol as Alias`
- `import module as alias`
- `self:` addressable refs

Good shipped examples:

- `examples/109_imported_review_handoff_output_inheritance/prompts/AGENTS.prompt`
- `examples/118_output_target_delivery_skill_binding/prompts/AGENTS.prompt`
- `examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt`

That means long module prefixes are still annoying, but this is not the best
place to spend new syntax budget first.

# Real Remaining Language Gaps

These are the places where the later corpus still repeats the same authored
shape even after the recent sugar wave.

## 1. Agent-local `inputs` and `outputs` lists are still too ceremony-heavy

### Pattern

Many agents still need this exact wrapper:

```prompt
inputs: "Inputs"
    DraftPlan

outputs: "Outputs"
    AcceptanceReviewComment
    AcceptanceControlFinalResponse
```

Representative paths:

- `examples/73_flow_visualizer_showcase/prompts/AGENTS.prompt`
- `examples/104_review_final_output_output_schema_blocked_control_ready/prompts/AGENTS.prompt`
- `examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt`
- `examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt`
- `examples/120_route_field_final_output_contract/prompts/AGENTS.prompt`
- `examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt`

### Current partial relief

- first-class `inputs` and `outputs` blocks in `23` and `24`
- omitted wrapper title lowering in `117`

Those help named reusable wrappers. They do not help the very common
agent-local inline list.

### What a compact form must preserve

- ordered item readback
- the line between a plain list and a richer keyed wrapper
- the ability to keep the current block form when wrapper prose matters
- current bound-root and addressable behavior

### Natural enhancement

Add an anonymous inline body form:

```prompt
inputs:
    DraftPlan

outputs:
    AcceptanceReviewComment
    AcceptanceControlFinalResponse
```

This feels natural because it keeps the current block shape. It only removes
the repeated title string.

## 2. Review semantic maps still repeat the same output-to-semantic bind set

### Pattern

Review comments often repeat the same semantic map:

```prompt
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

Representative paths:

- `examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt`
- `examples/48_review_inheritance_and_explicit_patching/prompts/AGENTS.prompt`
- `examples/68_review_family_shared_scaffold/prompts/AGENTS.prompt`
- `examples/104_review_final_output_output_schema_blocked_control_ready/prompts/AGENTS.prompt`
- `examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt`
- `examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt`
- `../psflows/flows/prd_factory/prompts/contracts/review.prompt`

### Current partial relief

- bare identity binds already remove some noise
- `review_family` lets authors share the full block when reuse is clean

The gap is the middle case. Many reviews reuse most of the map but still need
two or three renamed or nested paths.

### What a compact form must preserve

- explicit semantic ownership
- fail-loud missing binds for required review semantics
- support for non-identity binds
- no hidden magic based on prose titles

### Natural enhancement

Allow a source-aware map with explicit exceptions:

```prompt
fields from AcceptanceReviewComment:
    analysis: analysis_performed
    readback: output_contents_that_matter
    failing_gates: failure_detail.failing_gates
    blocked_gate: failure_detail.blocked_gate
```

Meaning:

- auto-bind same-name semantic fields from the named output
- keep explicit lines only where the output field path differs

This is still typed and fail-loud. It just stops making authors restate the
identity part of the map.

## 3. Split `final_output` blocks still use one nesting level too many

### Pattern

Later examples use this shape:

```prompt
final_output:
    output: AcceptanceControlFinalResponse
    review_fields:
        verdict
        current_artifact
        next_owner
        blocked_gate
```

Or this routed variant:

```prompt
final_output:
    output: WriterDecision
    route: next_route
```

Representative paths:

- `examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt`
- `examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt`
- `examples/120_route_field_final_output_contract/prompts/AGENTS.prompt`
- `examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt`

### Current partial relief

- the one-line `final_output: SomeOutput` form works for the simple case
- `review_fields:` already supports identity binds

The gap starts when the author needs the richer block. The `output:` line adds
structure, but it does not add much new meaning.

### What a compact form must preserve

- explicit selected final carrier
- explicit route-field binding when used
- explicit review-only availability of `review_fields`
- no implicit final output choice

### Natural enhancement

Let the selected output move into the head:

```prompt
final_output AcceptanceControlFinalResponse:
    review_fields:
        verdict
        current_artifact
        next_owner
        blocked_gate
```

And:

```prompt
final_output WriterDecision:
    route: next_route
```

This keeps all current meaning. It only removes one wrapper key.

## 4. `output schema` field heads still repeat small facts over many lines

### Pattern

Later JSON-heavy examples repeat field head boilerplate:

```prompt
field current_artifact: "Current Artifact"
    type: string
    nullable
    note: "Current artifact after review."
```

Representative paths:

- `examples/79_final_output_output_schema/prompts/AGENTS.prompt`
- `examples/83_review_final_output_output_schema/prompts/AGENTS.prompt`
- `examples/85_review_split_final_output_output_schema/prompts/AGENTS.prompt`
- `examples/90_split_handoff_and_final_output_shared_route_semantics/prompts/AGENTS.prompt`
- `examples/91_handoff_routing_route_output_binding/prompts/AGENTS.prompt`
- `examples/104_review_final_output_output_schema_blocked_control_ready/prompts/AGENTS.prompt`
- `examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt`
- `examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt`
- `examples/120_route_field_final_output_contract/prompts/AGENTS.prompt`
- `examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt`

### Current partial relief

- output inheritance reduces repeated schema owners in `107` through `111`
- `route field` lowers route-owned JSON truth in `120` and `121`

The field head itself is still long for the common scalar case.

### What a compact form must preserve

- field order
- field key
- human title
- type
- nullability
- note text
- exact JSON schema lowering
- the special route-owner rules on `route field`

### Natural enhancement

Add a compact scalar head:

```prompt
field current_artifact?: string "Current Artifact"
    note: "Current artifact after review."
```

And a matching routed head:

```prompt
route field next_route?: "Next Route"
```

Here `?` means `nullable`. The block body still owns the route options and any
extra notes.

## 5. Review comment outputs and final JSON outputs still mirror each other by hand

### Pattern

The review JSON-final examples often define:

- one review comment output with rich prose fields
- one final JSON control output with a smaller subset of the same facts
- one `review.fields` map
- one `final_output.review_fields` map

Representative paths:

- `examples/104_review_final_output_output_schema_blocked_control_ready/prompts/AGENTS.prompt`
- `examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt`
- `examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt`

### Current partial relief

- split `final_output` support exists
- output inheritance exists
- `review_fields:` can reuse review semantics on the final carrier

This is still the same truth expressed in three nearby places.

### What a compact form must preserve

- the prose comment output stays human-facing
- the final JSON output stays machine-facing
- guard conditions still stay explicit
- final-output contracts still stay exact

### Natural enhancement

This is a larger feature, not first-wave sugar. Still, it is the clearest next
step after the four simpler wins.

One plausible form:

```prompt
output AcceptanceControlFinalResponse: "Acceptance Control Final Response"
    target: TurnResponse
    shape: AcceptanceControlJson
    requirement: Required

    project review_fields:
        verdict
        current_artifact
        next_owner
        blocked_gate
```

I would rank this below the simpler parser wins because it starts to lower
semantics, not just syntax.

# Lower-Priority Motifs

These are real, but they are not the best next spend.

## 1. Repeated route readback sections

Examples:

- `examples/88_review_route_semantics_shared_binding/prompts/AGENTS.prompt`
- `examples/90_split_handoff_and_final_output_shared_route_semantics/prompts/AGENTS.prompt`
- `examples/94_route_choice_guard_narrowing/prompts/AGENTS.prompt`
- `examples/120_route_field_final_output_contract/prompts/AGENTS.prompt`
- `examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt`

The repetition is real, but there are only a few examples, and route detail is
touchy. I would not rush a shortcut here.

## 2. Repeated `target`, `shape`, `requirement` on simple outputs

Examples:

- `examples/73_flow_visualizer_showcase/prompts/AGENTS.prompt`
- `examples/107_output_inheritance_basic/prompts/AGENTS.prompt`
- `examples/110_final_output_inherited_output/prompts/AGENTS.prompt`

This is visible, but those three lines carry core contract truth. I would keep
them explicit unless a future head syntax can stay very clear.

# External Stress Check: `../psflows`

The same ranking holds in real prompts.

## Already solved, but underused

- Long plain inherit runs are still common in
  `../psflows/flows/lessons/prompts/contracts/lesson_plan.prompt` and
  `../psflows/flows/lessons/prompts/contracts/section_playable_strategy.prompt`.
- Output inheritance is sometimes still spelled line by line in
  `../psflows/flows/lessons/prompts/shared/lead_outputs.prompt`.

These should mostly move to grouped `inherit { ... }`.

## Real remaining gaps

- Agent-local `inputs` and `outputs` wrappers are still repeated across many
  flow roots such as `../psflows/flows/prd_factory/prompts/AGENTS.prompt`.
- Split final outputs still need block ceremony in
  `../psflows/flows/lessons/prompts/agents/section_concepts_terms_curator/AGENTS.prompt`.
- Review field maps still repeat in
  `../psflows/flows/prd_factory/prompts/contracts/review.prompt`.

# Recommendation Order

If the goal is to cut real authoring repetition fast, I would do this next:

1. anonymous inline `inputs:` and `outputs:` bodies
2. `fields from OutputName:` for review semantic maps
3. headed `final_output OutputName:`
4. compact `output schema` scalar field heads

I would not spend the next wave on new inherit syntax. Doctrine already has
the main win there.

# Bottom Line

Doctrine's next big authoring win is not more power. It is less wrapper noise.

The strongest additions are the ones that keep the current typed model and
only remove lines that restate already-clear structure.
