---
title: "Doctrine - Rendered Agent Markdown Audit"
date: 2026-04-16
status: completed
owners: [aelaguiz]
doc_type: audit
related:
  - doctrine/_compiler/compile/outputs.py
  - doctrine/_compiler/compile/final_output.py
  - doctrine/_renderer/blocks.py
  - doctrine/_renderer/semantic.py
  - examples/09_outputs/ref/turn_response_output_agent/AGENTS.md
  - examples/38_metadata_polish_capstone/ref/rewrite_aware_metadata_polish_capstone_demo/AGENTS.md
  - examples/51_inherited_bound_io_roots/ref/inherited_bound_current_truth_demo/AGENTS.md
  - examples/56_document_structure_attachments/ref/lesson_plan_structure_demo/AGENTS.md
  - examples/83_review_final_output_output_schema/ref/acceptance_review_json_demo/AGENTS.md
  - examples/84_review_split_final_output_prose/ref/draft_review_split_final_output_demo/AGENTS.md
  - examples/85_review_split_final_output_output_schema/ref/acceptance_review_split_json_demo/AGENTS.md
  - examples/105_review_split_final_output_output_schema_control_ready/ref/acceptance_review_split_control_ready_demo/AGENTS.md
  - examples/119_route_only_final_output_contract/build_ref/route_only_final_output_contract_demo/AGENTS.md
---

# TL;DR

This audit is now Doctrine-only.
It is also formatting-only in intent.
It covers rendered markdown problems that come from Doctrine compile, emit, or
render presentation. It does not cover repo-local cleanup in sibling repos.

The main Doctrine-owned problems are:

- split review and final-output surfaces restate the same contract
- single-child wrapper headings and binding shells create heading ladders
- artifact-structure emission is still too eager to explain every child
- raw guard, mode, and route syntax leaks into human markdown
- small scalar contracts still default to table-heavy rendering too often

This version does not propose new Doctrine syntax.
It stays focused on markdown formatting, lowering, and emit presentation.

# Scope

- This artifact is meant to stand on its own.
- All examples below come from rendered Doctrine outputs under
  `examples/*/(ref|build_ref|build)`.
- I did not include `../psflows` or `../rally` cleanup work in this version.
- I did not run verify commands for this doc-only pass.

# Out Of Scope

- new Doctrine syntax
- new declarations or authored semantic features
- changing wire payload shape
- changing review or route semantics themselves
- repo-local prompt cleanup outside this repo

# Review Bar

This is the bar I used for "markdown first" render quality.

1. One concept should render once.
2. Wrapper headings should earn their space.
3. Tables should be for real comparison, schema, or columns.
4. Guard and route logic should read like human instructions, not compiler IR.
5. The rendered markdown should favor readability over mechanical structure
   dumps.

# Findings

## P1. Split review and final-output sections restate the same contract

This is the biggest Doctrine-owned presentation bloat front.

Today, split review examples often render:

- a readable review carrier
- a payload table for the final output
- a semantics table mapping meanings back to fields
- another field-by-field outline

That means the same contract appears in three or four forms.

Source:
`examples/105_review_split_final_output_output_schema_control_ready/ref/acceptance_review_split_control_ready_demo/AGENTS.md`

Today:

```md
### Acceptance Review Comment

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Comment |
| Requirement | Required |

#### Verdict

State whether the plan passed review or asked for changes.

#### Reviewed Artifact

Name the reviewed artifact.

#### Analysis Performed

Summarize the review analysis.

#### Output Contents That Matter

State what the next owner should read first.
```

Then later in the same file:

```md
#### Review Response Semantics

This final response is separate from the review carrier: AcceptanceReviewComment.

| Meaning | Field |
| --- | --- |
| Verdict | `verdict` |
| Current Artifact | `current_artifact` |
| Next Owner | `next_owner` |
| Blocked Gate | `blocked_gate` |

#### Field Notes

Keep `verdict` aligned with the review verdict.
Use null for `next_owner` and `blocked_gate` when this review does not set them.

#### Verdict

State whether the review accepted the plan or asked for changes.
```

Best case:

```md
### Acceptance Review

- Verdict: say whether the plan passed review or needs changes.
- Reviewed artifact: name the draft plan.
- Analysis: give the short reason for the verdict.
- Read first: say what the next owner should read first.
- Current artifact: include only when one still stands.
- Next owner: include only when one exists.
- Failure detail: include only on reject.

## Final Output

Return one control-ready JSON object with:

- `verdict`
- `current_artifact`
- `next_owner`
- `blocked_gate`

This JSON mirrors the review outcome. Do not restate the review contract here.
```

Likely owner paths:

- `doctrine/_compiler/compile/final_output.py:192-319`
- `doctrine/_compiler/compile/final_output.py:335-382`

## P1. Single-child wrapper headings and binding shells create heading ladders

Doctrine still emits a lot of wrapper structure that does not add meaning.

Source:
`examples/38_metadata_polish_capstone/ref/rewrite_aware_metadata_polish_capstone_demo/AGENTS.md`

Today:

```md
### Current Handoff Binding

#### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

### Approved Plan Binding

#### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required
```

A smaller version of the same issue appears in inherited bound roots.

Source:
`examples/51_inherited_bound_io_roots/ref/inherited_bound_current_truth_demo/AGENTS.md`

Today:

```md
## Inputs

### Approved Plan Binding

#### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required
```

Best case:

```md
## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required
```

The clean fix is usually earlier lowering, not just changing punctuation at the
end.

Main owner areas:

- `doctrine/_compiler/compile/outputs.py`
- `doctrine/_compiler/compile/records.py`

## P1. Artifact-structure emission is still too eager

This is still a formatting and emit-presentation problem, even though the owner
path sits in compile code.

Source:
`examples/56_document_structure_attachments/ref/lesson_plan_structure_demo/AGENTS.md`

Today:

```md
### Next Lesson Plan

| Contract | Value |
| --- | --- |
| Target | File |
| Path | `lesson_root/NEXT_LESSON_PLAN.md` |
| Shape | Markdown Document |
| Requirement | Required |
| Structure | Lesson Plan |

#### Artifact Structure

This artifact must follow the `Lesson Plan` structure below.

| Required Section | Kind | What it must do |
| --- | --- | --- |
| **Overview** | Section | Start with the plan overview. |
| **Sequence** | Section | List the lesson steps in order. |
```

This is not terrible. But it already shows the default pattern:

- contract table
- structure row
- structure heading
- prose lead-in
- second table

That pattern scales poorly once the structure gets larger.

Best case:

```md
### Next Lesson Plan

- Target: file
- Path: `lesson_root/NEXT_LESSON_PLAN.md`
- Shape: Markdown document
- Required structure:
  - Overview
  - Sequence
```

Main owner path:

- `doctrine/_compiler/compile/outputs.py:867-947`

## P1. Raw guard, mode, and route syntax is leaking into human markdown

Some rendered Doctrine examples still read like compiler IR.

Source:
`examples/38_metadata_polish_capstone/ref/rewrite_aware_metadata_polish_capstone_demo/AGENTS.md`

Today:

```md
Active mode: section-summary.

Current artifact: Section Metadata.

Make sure current_handoff.preserve_basis == approved_structure.

Own only {`section_metadata.name`, `section_metadata.description`}.

Preserve exact `section_metadata.*` except `section_metadata.name`, `section_metadata.description`.

If unclear(pass_mode, current_handoff.preserve_basis):
- Stop: Mode or preserve basis is unclear.
- Route the same issue back to RoutingOwner.
```

Source:
`examples/119_route_only_final_output_contract/build_ref/route_only_final_output_contract_demo/AGENTS.md`

Today:

```md
This pass runs only when RouteFacts.live_job is route_only_final.

No artifact is current for this turn.

Use exactly one mode:
- Routing Owner

If the mode is Routing Owner:
- Route to Routing Owner.
```

Best case:

```md
This pass is for `section-summary` mode.

The current artifact is Section Metadata.

Only edit:

- `section_metadata.name`
- `section_metadata.description`

Keep the rest of `section_metadata.*` unchanged.

If the mode or preserve basis is unclear, stop and route the issue back to
RoutingOwner.
```

And for the route-only case:

```md
This is a route-only turn.

No specialist artifact is current.

Route the work to Routing Owner and end the turn.
```

Doctrine already has some humanizing machinery:

- `doctrine/_renderer/semantic.py:7-38`
- `doctrine/_renderer/blocks.py:186-245`
- `doctrine/_renderer/blocks.py:447-459`

The problem is coverage. The ugliest guard and route-heavy surfaces still fall
through as raw structure.

## P2. Small scalar contracts still default to table-heavy rendering too often

Doctrine already has proof that compact output can work.

Source:
`examples/09_outputs/ref/turn_response_output_agent/AGENTS.md`

Today:

```md
# Turn Response Output Agent

Core job: return a short issue summary in the turn response.

## Your Job

- Return the issue summary in the turn response.

## Outputs

### Issue Summary Response

- Target: TurnResponse
- Shape: Issue Summary Text
- Requirement: Required
```

That is close to the right answer.

By contrast, small scalar review contracts still render too heavily.

Source:
`examples/85_review_split_final_output_output_schema/ref/acceptance_review_split_json_demo/AGENTS.md`

Today:

```md
### Acceptance Review Comment

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Comment |
| Requirement | Required |

#### Verdict

State whether the plan passed review.

#### Reviewed Artifact

Name the reviewed artifact.

#### Analysis Performed

Summarize the review analysis.
```

Best case:

```md
### Acceptance Review

- Target: turn response
- Shape: comment
- Verdict: say whether the plan passed review.
- Reviewed artifact: name the reviewed artifact.
- Analysis: summarize the review analysis.
```

This does not mean "no tables." It means tables should be for payload schema,
real comparison, or columns, not every small scalar contract.

# What Already Looks Good

Doctrine already has proof that smaller surfaces are possible.

- `examples/09_outputs/ref/turn_response_output_agent/AGENTS.md:1-24` is short
  and clear.
- `doctrine/_renderer/semantic.py:19-37` already ships sentence and concise
  modes for `ArtifactMarkdown` and `CommentMarkdown`.
- `examples/64_render_profiles_and_properties/prompts/AGENTS.prompt:1-31`
  proves that authored `render_profile` can already lower some surfaces into
  sentences and concise guard shells.

The next pass should build on those strengths instead of inventing a second
render system.

# Doctrine-only Next Pass

1. Fix split review and final-output duplication first.
   This is the highest-value change because it affects many rendered surfaces at
   once.
2. Extend wrapper lowering beyond the current omitted-title work.
   Target single-child bindings and simple shell sections.
3. Add a compact artifact-structure mode.
   Start with summary-only output for simple documents.
4. Add broader human-facing lowering for guard, route, and mode text.
5. Use bullets more often for tiny scalar contracts.

# Bottom Line

The core problem is still the same: Doctrine is rendering too much of the typed
source tree directly into markdown. This doc treats that as a formatting and
presentation problem, not a language-design project. The next win is better
lowering, simpler structure, and cleaner markdown.
