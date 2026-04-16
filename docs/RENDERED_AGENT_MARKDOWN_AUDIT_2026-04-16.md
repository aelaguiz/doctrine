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
  - examples/83_review_final_output_output_schema/ref/acceptance_review_json_demo/AGENTS.md
  - examples/105_review_split_final_output_output_schema_control_ready/ref/acceptance_review_split_control_ready_demo/AGENTS.md
  - examples/119_route_only_final_output_contract/build_ref/route_only_final_output_contract_demo/AGENTS.md
  - ../psflows/flows/lessons/build/agents/project_lead/AGENTS.md
  - ../psflows/flows/lessons/build/agents/section_dossier_engineer/AGENTS.md
  - ../psflows/runs/archive/LES-16/home/agents/acceptance_critic/AGENTS.md
  - ../psflows/runs/archive/LES-16/home/agents/copywriter/AGENTS.md
  - ../rally/flows/software_engineering_demo/build/agents/architect/AGENTS.md
  - ../rally/flows/software_engineering_demo/build/agents/developer_reviewer/AGENTS.md
  - ../rally/flows/poem_loop/build/agents/poem_critic/AGENTS.md
  - ../rally/flows/_stdlib_smoke/build/agents/repair_plan_reviewer/AGENTS.md
---

# TL;DR

The main problem is not that these agent homes contain too much truth. The main
problem is that the emit path is still dumping typed structure into markdown
almost one layer at a time. That makes many rendered files read like schema
output, not like clean agent homes.

The biggest Doctrine-owned bloat fronts are:

- split review and final-output sections that restate the same contract
- single-child wrapper headings and binding shells
- artifact-structure sections that show both a summary table and a second detail
  tree
- raw guard, mode, and route syntax leaking into human markdown

The biggest repo-owned bloat fronts in `../psflows` and `../rally` are:

- too much shared runtime boilerplate inside every role home
- full skill mini-manuals copied inline
- generic or stale examples inside already-large rendered files

# Scope

- This doc is meant to stand on its own. The key examples are quoted inline
  below.
- I reviewed rendered markdown under `examples/*/(ref|build_ref|build)` in this
  repo.
- I compared that with rendered agent homes in
  `../psflows/flows/lessons/build/**`,
  `../psflows/runs/**/home/agents/**`, and `../rally/flows/*/build/**`.
- I used parallel repo reads only. I did not edit `../psflows` or `../rally`.
- I did not run verify commands. This is a read-only audit plus this new doc.

# Review Bar

These rules explain what "markdown first" should mean here.

1. One concept should render once. Do not show the same contract as a table,
   then as per-field headings, then as a semantics table.
2. Wrapper headings should earn their space. If a wrapper only names one child,
   lower the wrapper or reuse the child title.
3. Tables should be for real comparison. Small scalar contracts usually scan
   better as bullets or short sentences.
4. Guards and route facts should render as plain English. Do not leak
   `present(...)`, `missing(...)`, `unclear(...)`, or raw dotted refs unless
   the exact code token is the real thing the reader must type.
5. Role homes should stay focused on the job. Wire-level schema detail, shared
   runtime boilerplate, and full skill manuals should not dominate the always-on
   surface.

# Findings

## P1. Split review and final-output sections restate the same contract

This is the biggest single source of bloat.

The same review truth is often rendered once as a readable carrier and then
again as the final JSON contract. The reader sees the same idea as headings,
tables, field notes, and semantics tables.

Source:
`examples/105_review_split_final_output_output_schema_control_ready/ref/acceptance_review_split_control_ready_demo/AGENTS.md:44-100`

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

The same file then restates the final side of the same contract.

Source:
`examples/105_review_split_final_output_output_schema_control_ready/ref/acceptance_review_split_control_ready_demo/AGENTS.md:139-183`

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

The same problem shows up in Rally.

Source:
`../rally/flows/_stdlib_smoke/build/agents/repair_plan_reviewer/AGENTS.md:38-97`

```md
### Smoke Review Response

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Smoke Review JSON |
| Requirement | Required |

#### Verdict

Say whether the review accepts the work or asks for changes.

#### Reviewed Artifact

Name the artifact path you reviewed.

#### Review Summary

Explain the review in 2-4 plain sentences.
```

Source:
`../rally/flows/_stdlib_smoke/build/agents/repair_plan_reviewer/AGENTS.md:143-218`

```md
#### Review Response Semantics

This final response is separate from the review carrier: SmokeReviewResponse.

| Meaning | Field |
| --- | --- |
| Verdict | `verdict` |
| Reviewed Artifact | `reviewed_artifact` |
| Analysis | `analysis_performed` |
| Readback | `findings_first` |
| Current Artifact | `current_artifact` |
| Blocked Gate | `failure_detail.blocked_gate` |
| Failing Gates | `failure_detail.failing_gates` |
| Next Owner | `next_owner` |

#### Verdict

Say whether the review accepts the work or asks for changes.
```

This is not just long. It pushes the same contract at the reader in too many
shapes.

There is also a sharper Doctrine problem here. Some final-output renders say
more than the payload allows.

Source:
`examples/83_review_final_output_output_schema/ref/acceptance_review_json_demo/AGENTS.md:54-119`

```md
#### Payload Fields

| Field | Type | Required On Wire | Null Allowed | Meaning |
| --- | --- | --- | --- | --- |
| `verdict` | string | Yes | No | Review verdict. |
| `reviewed_artifact` | string | Yes | No | Reviewed artifact name. |
| `current_artifact` | string | Yes | No | Current artifact after review. |
| `next_owner` | string | Yes | No | Next owner after review. |

#### Analysis Performed

Summarize the review analysis.

#### Output Contents That Matter

State what the next owner should read first.
```

Those extra sections are not in the payload table. The markdown makes the wire
shape look larger than it really is.

Likely Doctrine owner paths:

- `doctrine/_compiler/compile/final_output.py:192-319`
- `doctrine/_compiler/compile/final_output.py:335-382`

What tighter markdown should do instead:

- Keep one readable carrier contract block.
- Keep one payload table for the final JSON.
- Add one short note only when the final JSON and the carrier really differ.
- Only emit a field-specific heading when that field has a special rule that is
  not already clear from the payload table.

## P1. Single-child wrappers and binding shells create heading ladders

Many files waste space on wrapper titles that only repeat the child title below
them.

Doctrine example:

Source:
`examples/38_metadata_polish_capstone/ref/rewrite_aware_metadata_polish_capstone_demo/AGENTS.md:36-71`

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

Rally example:

Source:
`../rally/flows/poem_loop/build/agents/poem_critic/AGENTS.md:180-205`

```md
### Poem Draft File

#### Poem Draft File

- Source: File
- Path: `home:artifacts/poem.md`
- Shape: Markdown Document
- Requirement: Advisory
- Structure: Poem Draft

##### Structure: Poem Draft

###### Poem Type

Name the requested poem type in plain words.
```

Older `psflows` archived homes show the same thing at much bigger size.

Source:
`../psflows/runs/archive/LES-16/home/agents/acceptance_critic/AGENTS.md:129-190`

```md
## Your Inputs

### Review State Inputs

#### Producer Handoff

##### Producer Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

#### Review State

##### Review State

- Source: Prompt
- Shape: Json Object
- Requirement: Required
```

This is not helping the reader. It is just mirroring the source tree.

What tighter markdown should do instead:

- Lower one-child wrappers by default.
- Render simple runtime inputs as one compact `Runtime Inputs` block instead of
  one heading per env var.
- Render small file structures as bullets or one short table, not a nested
  heading stack.

This is close to the omitted-title and lowering work already underway in this
repo. The same design idea should widen to more binding and wrapper surfaces.

## P1. Artifact-structure sections dump both summary and detail

Doctrine currently builds artifact-structure sections as:

- one prose lead-in
- one summary table
- then one detail block per child when detail exists

The owner path is `doctrine/_compiler/compile/outputs.py:867-947`.

That pattern is too big for real role homes.

Source:
`../psflows/flows/lessons/build/agents/section_dossier_engineer/AGENTS.md:118-195`

```md
##### Artifact Structure

This artifact must follow the `Section Dossier` structure below.

| Required Section | Kind | What it must do |
| --- | --- | --- |
| **Learner History By Section** | Table | Add one row for each earlier section or other upstream unit. |
| **Learner Baseline** | Section | Say what the learner already knows and what this section can safely assume. |
| **Section Metadata Status** | Section | Record the section metadata status with the checklist below. |
...
###### Learner History By Section Contract

_Required · table_

| Column | Meaning |
| --- | --- |
| What It Installed | Say what that earlier section or unit taught. |
| Learner-Ready State After It | Say what the learner can now do or safely assume because of that earlier work. |
| Still Out Of Scope | Say what was still out of scope after that earlier work. |
```

The file first gives the summary table, then starts a second full contract tree.

The older archived Lessons homes show the same thing at a much larger scale.
`../psflows/runs/archive/LES-16/home/agents/acceptance_critic/AGENTS.md` is
1,144 lines. `../psflows/runs/archive/LES-16/home/agents/copywriter/AGENTS.md`
is 978 lines. A lot of that size is this pattern.

What tighter markdown should do instead:

- For simple documents, emit one compact outline only.
- For medium documents, emit the summary table only.
- For complex documents, expand detail only for the blocks that truly need
  schema or per-column explanation.
- Do not emit both a summary table and a second full detail tree by default.

## P1. Raw guard, mode, and route syntax is leaking into human markdown

Some rendered examples still look like compiler IR.

Source:
`examples/38_metadata_polish_capstone/ref/rewrite_aware_metadata_polish_capstone_demo/AGENTS.md:7-31`

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
`examples/119_route_only_final_output_contract/build_ref/route_only_final_output_contract_demo/AGENTS.md:1-18`

```md
End a route-only turn with emitted route contract metadata.

## Route Only Final Response

Emit Route Only Final Reply.

This pass runs only when RouteFacts.live_job is route_only_final.

No artifact is current for this turn.

Use exactly one mode:
- Routing Owner

If the mode is Routing Owner:
- Route to Routing Owner.
```

These are valid typed concepts. They are not good reader-facing markdown.

Doctrine already has proof that some surfaces can be humanized. Built-in
profiles in `doctrine/_renderer/semantic.py:7-38` and
`doctrine/_renderer/blocks.py:186-245` plus
`doctrine/_renderer/blocks.py:447-459` already support sentence and concise
guard lowering for some targets. The problem is that the ugliest guard and
mode-heavy surfaces still fall through as raw structure.

What tighter markdown should do instead:

- translate `present(x)` into plain English like "Show this only when `x`
  exists"
- translate `missing(x)` into "If `x` is missing"
- turn mode lists into one short decision sentence when only one live path
  exists
- hide raw dotted refs unless the reader truly needs the exact token

## P2. Shared runtime boilerplate is crowding out the actual role

This is mostly a repo-authoring problem in `../psflows` and `../rally`, not a
Doctrine renderer problem by itself.

Rally example:

Source:
`../rally/flows/software_engineering_demo/build/agents/architect/AGENTS.md:19-67`

```md
## System Context

This flow is a real Rally software engineering demo.
It starts from `home:issue.md`.
It works in one demo repo at `home:repos/demo_repo`.
Later issues build on the last accepted demo history.

### Why This Flow Exists

The goal is to show a real issue loop, not a fake prompt toy.
The flow should pressure Rally and Doctrine in honest ways.

## Issue Ledger Truth

### Opening Issue

Read the opening text before the first `## Rally` heading as the human request.

### Run History

Read later `## Rally` blocks as the shared history.
Start with the newest relevant block when you need the latest truth.

## Demo Repo Rules
```

That content is not wrong. It is just too heavy inside every role home.

Older `psflows` archived homes show the same issue in stronger form. The role
does not really begin until after a long preamble.

Source:
`../psflows/runs/archive/LES-16/home/agents/copywriter/AGENTS.md:85-103`

```md
Ignore clearly retired authoring surfaces by default.
...

## Your Job

Turn approved lesson structure into grounded learner language.
Default to meaning before flourish.
Keep locked concepts, locked term decisions, and exact-move limits intact even when smoother copy is tempting.
Treat one current lesson as your unit of work.
```

The file is 978 lines long. The role-specific part is real, but it starts late.

What tighter markdown should do instead:

- keep shared Rally operating rules in one thinner imported surface
- keep the role home focused on mission, files, outputs, and lane-specific
  exceptions
- keep repeated env-var input readback out of the main role law unless a role
  has a special case

## P2. Full skill manuals are copied inline

This is another repo-owned bloat front.

Source:
`../psflows/flows/lessons/build/agents/section_dossier_engineer/AGENTS.md:73-100`

```md
## Skills

### rally-kernel

_Required skill_

**Purpose**

Use the shared Rally kernel skill when you need one saved note on this turn.

**Use When**

A later reader needs one short saved note.

**Reason**

Rally provides this skill on every Rally-managed turn.
```

This is a simple skill fact. It already reads like a full manual card.

What tighter markdown should do instead:

- keep the role home at "skill name + when to use it"
- let `SKILL.md` own the deeper manual
- inline a full skill card only when the skill rule is truly role-specific and
  cannot live in the skill itself

## P2. Tiny contracts still render as tables when bullets would scan better

This shows up across all three repos.

Good compact example:

Source:
`examples/09_outputs/ref/turn_response_output_agent/AGENTS.md:1-24`

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

That file uses bullets and one short output section. It reads cleanly.

Heavier example:

Source:
`examples/105_review_split_final_output_output_schema_control_ready/ref/acceptance_review_split_control_ready_demo/AGENTS.md:44-78`

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
```

These are not wrong. They are just over-shaped. A two-column table for three or
four scalar rows is often worse than bullets in markdown.

What tighter markdown should do instead:

- use bullets for small scalar contracts
- reserve tables for payload schemas, real comparison, or column definitions
- avoid stacking a tiny contract table under yet another heading shell

## P3. Long files become easier to distrust when examples drift

Verbose files only help if they stay exact.

Rally already has examples where the local text disagrees with the table right
above it.

Source:
`../rally/flows/_stdlib_smoke/build/agents/closeout/AGENTS.md:61-96`

```md
| `sleep_duration_seconds` | integer | Yes | Yes | Seconds to wait when `kind` is `sleep`. |
| `current_artifact` | string | Yes | Yes | Current artifact path when the smoke test closes out. |

#### Field Notes

- Always send all five keys.
```

That file now shows six fields, then says "all five keys."

There is also example drift in owner names.

Source:
`../rally/flows/software_engineering_demo/build/agents/architect/AGENTS.md:244-253`

```json
{
  "kind": "handoff",
  "next_owner": "change_engineer",
  "summary": null,
  "reason": null,
  "sleep_duration_seconds": null
}
```

That example does not match the current flow owner names.

This is a lower-priority markdown problem, but it still matters:

- if a huge file is also slightly wrong, the extra length buys nothing
- copied example JSON should match the real owner names and route keys
- stale labels are worse in rendered files than in raw source because the build
  output looks authoritative

# Paired Before/After Examples

This section is the main before-and-after gallery. Each item shows:

- the actual rendered markdown today
- the best-case markdown target if we make the surface as elegant as we can

The "best case" side is not proposed source syntax. It is the target render.

## 1. Doctrine split review carrier

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
```

## 2. Doctrine split review final JSON

Source:
`examples/105_review_split_final_output_output_schema_control_ready/ref/acceptance_review_split_control_ready_demo/AGENTS.md`

Today:

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
### Final Output

Return one control-ready JSON object with:

- `verdict`
- `current_artifact`
- `next_owner`
- `blocked_gate`

This JSON mirrors the review outcome. Do not restate the review contract here.
```

## 3. Rally split review carrier

Source:
`../rally/flows/_stdlib_smoke/build/agents/repair_plan_reviewer/AGENTS.md`

Today:

```md
### Smoke Review Response

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Smoke Review JSON |
| Requirement | Required |

#### Verdict

Say whether the review accepts the work or asks for changes.

#### Reviewed Artifact

Name the artifact path you reviewed.

#### Review Summary

Explain the review in 2-4 plain sentences.
```

Best case:

```md
### Smoke Review

- Verdict: accept or changes requested.
- Reviewed artifact: `home:artifacts/repair_plan.md`.
- Review summary: explain the decision in 2-4 plain sentences.
- Findings first: lead with the main finding and next move.
- Current artifact: include only when one still stands.
- Next owner: include only when the review routes.
```

## 4. Rally split review final JSON

Source:
`../rally/flows/_stdlib_smoke/build/agents/repair_plan_reviewer/AGENTS.md`

Today:

```md
#### Review Response Semantics

This final response is separate from the review carrier: SmokeReviewResponse.

| Meaning | Field |
| --- | --- |
| Verdict | `verdict` |
| Reviewed Artifact | `reviewed_artifact` |
| Analysis | `analysis_performed` |
| Readback | `findings_first` |
| Current Artifact | `current_artifact` |
| Blocked Gate | `failure_detail.blocked_gate` |
| Failing Gates | `failure_detail.failing_gates` |
| Next Owner | `next_owner` |

#### Verdict

Say whether the review accepts the work or asks for changes.
```

Best case:

```md
### Final Output

Return one JSON object with:

- `verdict`
- `reviewed_artifact`
- `analysis_performed`
- `findings_first`
- `current_artifact`
- `next_owner`
- `failure_detail`

This JSON is the machine-readable review result. Keep the explanation in the
review block above.
```

## 5. Doctrine final-output payload drift

Source:
`examples/83_review_final_output_output_schema/ref/acceptance_review_json_demo/AGENTS.md`

Today:

```md
#### Payload Fields

| Field | Type | Required On Wire | Null Allowed | Meaning |
| --- | --- | --- | --- | --- |
| `verdict` | string | Yes | No | Review verdict. |
| `reviewed_artifact` | string | Yes | No | Reviewed artifact name. |
| `current_artifact` | string | Yes | No | Current artifact after review. |
| `next_owner` | string | Yes | No | Next owner after review. |

#### Analysis Performed

Summarize the review analysis.

#### Output Contents That Matter

State what the next owner should read first.
```

Best case:

```md
#### Payload Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `verdict` | string | Review verdict |
| `reviewed_artifact` | string | Reviewed artifact |
| `current_artifact` | string | Current artifact after review |
| `next_owner` | string | Next owner after review |

If the final JSON does not carry analysis or readback, do not render extra
analysis or readback sections here.
```

## 6. Doctrine single-child binding wrappers

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

## 7. Rally deep file-structure ladder

Source:
`../rally/flows/poem_loop/build/agents/poem_critic/AGENTS.md`

Today:

```md
### Poem Draft File

#### Poem Draft File

- Source: File
- Path: `home:artifacts/poem.md`
- Shape: Markdown Document
- Requirement: Advisory
- Structure: Poem Draft

##### Structure: Poem Draft

###### Poem Type

Name the requested poem type in plain words.
```

Best case:

```md
### Poem Draft

- Path: `home:artifacts/poem.md`
- Shape: Markdown document
- Include:
  - poem type
  - subject
  - poem text
```

## 8. `psflows` deep input ladder

Source:
`../psflows/runs/archive/LES-16/home/agents/acceptance_critic/AGENTS.md`

Today:

```md
## Your Inputs

### Review State Inputs

#### Producer Handoff

##### Producer Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

#### Review State

##### Review State

- Source: Prompt
- Shape: Json Object
- Requirement: Required
```

Best case:

```md
## Inputs

### Review State

- Producer handoff: prompt JSON. Required.
- Review state: prompt JSON. Required.

Use these two inputs to decide whether review can start and which review mode is
live.
```

## 9. `psflows` artifact-structure dump

Source:
`../psflows/flows/lessons/build/agents/section_dossier_engineer/AGENTS.md`

Today:

```md
##### Artifact Structure

This artifact must follow the `Section Dossier` structure below.

| Required Section | Kind | What it must do |
| --- | --- | --- |
| **Learner History By Section** | Table | Add one row for each earlier section or other upstream unit. |
| **Learner Baseline** | Section | Say what the learner already knows and what this section can safely assume. |
| **Section Metadata Status** | Section | Record the section metadata status with the checklist below. |
...
###### Learner History By Section Contract

_Required · table_
```

Best case:

```md
### Section Dossier Structure

Include these parts:

1. Learner History By Section
2. Learner Baseline
3. Section Metadata Status
4. Next Capabilities
5. Section Advancement
6. Exact Upstream References
7. Continuity And Advancement Matrix
8. Analysis Output
9. Stop Line
10. Candidate Concept Burden
11. Grounding And Open Questions

Only expand column rules for the tables that truly need them.
```

## 10. Doctrine raw guard syntax

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

## 11. Doctrine raw route-only syntax

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
This is a route-only turn.

No specialist artifact is current.

Route the work to Routing Owner and end the turn.
```

## 12. Rally shared runtime boilerplate

Source:
`../rally/flows/software_engineering_demo/build/agents/architect/AGENTS.md`

Today:

```md
## System Context

This flow is a real Rally software engineering demo.
It starts from `home:issue.md`.
It works in one demo repo at `home:repos/demo_repo`.
Later issues build on the last accepted demo history.

## Issue Ledger Truth

### Opening Issue

Read the opening text before the first `## Rally` heading as the human request.

## Demo Repo Rules
```

Best case:

```md
## Shared Rally Rules

- Read the request from `home:issue.md`.
- Work only in `home:repos/demo_repo`.
- Stay on the current issue branch.
- Keep route truth in the final JSON, not in note prose.
```

## 13. Inline skill manual

Source:
`../psflows/flows/lessons/build/agents/section_dossier_engineer/AGENTS.md`

Today:

```md
### rally-kernel

_Required skill_

**Purpose**

Use the shared Rally kernel skill when you need one saved note on this turn.

**Use When**

A later reader needs one short saved note.

**Reason**

Rally provides this skill on every Rally-managed turn.
```

Best case:

```md
## Skills

- `rally-kernel`: use it when this turn needs one saved note.
```

## 14. Already-compact output contract

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

Best case:

```md
# Turn Response Output Agent

Core job: return a short issue summary in the turn response.

## Outputs

### Issue Summary Response

- Target: TurnResponse
- Shape: Issue Summary Text
- Requirement: Required
- Keep it to one or two sentences.
```

This one is already close to the right answer.

## 15. Field-count drift in a long file

Source:
`../rally/flows/_stdlib_smoke/build/agents/closeout/AGENTS.md`

Today:

```md
| `sleep_duration_seconds` | integer | Yes | Yes | Seconds to wait when `kind` is `sleep`. |
| `current_artifact` | string | Yes | Yes | Current artifact path when the smoke test closes out. |

#### Field Notes

- Always send all five keys.
```

Best case:

```md
| `sleep_duration_seconds` | integer | Yes | Yes | Seconds to wait when `kind` is `sleep`. |
| `current_artifact` | string | Yes | Yes | Current artifact path when the smoke test closes out. |

#### Field Notes

- Always send all six keys.
```

## 16. Example owner drift

Source:
`../rally/flows/software_engineering_demo/build/agents/architect/AGENTS.md`

Today:

```json
{
  "kind": "handoff",
  "next_owner": "change_engineer",
  "summary": null,
  "reason": null,
  "sleep_duration_seconds": null
}
```

Best case:

```json
{
  "kind": "handoff",
  "next_owner": "developer",
  "summary": null,
  "reason": null,
  "sleep_duration_seconds": null
}
```

# What Already Looks Good

Doctrine already has proof that smaller surfaces are possible.

- `examples/09_outputs/ref/turn_response_output_agent/AGENTS.md:1-24` is short,
  clear, and uses markdown the way a reader would expect.
- `doctrine/_renderer/semantic.py:19-37` already ships sentence and concise
  modes for `ArtifactMarkdown` and `CommentMarkdown`.
- `examples/64_render_profiles_and_properties/prompts/AGENTS.prompt:1-31`
  proves that authored `render_profile` can already lower some surfaces into
  sentences and concise guard shells.

The next pass should build on those strengths instead of inventing a second
render system.

# Ownership Split

## Doctrine-owned work

- lower one-child wrappers and binding shells
- compact artifact-structure emission
- stop split review and final-output duplication
- humanize guard, mode, and route language before emit
- use bullets instead of tiny scalar tables more often

## `psflows` and `rally` owned work

- shrink shared runtime boilerplate in role homes
- stop inlining full skill manuals when `SKILL.md` already owns the rule
- keep role homes focused on the role, not the whole harness
- remove stale or generic example JSON and copied labels

# Recommended Next Pass

1. Fix split review and final-output duplication in Doctrine first.
   This is the highest-value change because it affects Doctrine examples and
   both sibling repos at once.
2. Extend wrapper lowering beyond the current omitted-title work.
   Target single-child bindings, repeated input wrappers, and simple structure
   shells.
3. Add a compact artifact-structure render mode.
   Start with summary-only output for simple documents and opt-in detail for
   complex ones.
4. Add a human-facing lowering pass for guards and mode text.
   Keep the typed truth in metadata and JSON. Render plain English in the
   markdown.
5. After the Doctrine pass, trim repo-local boilerplate in `../rally` and
   `../psflows`.
   Pull shared runtime rules and skill manuals back behind imports and skill
   boundaries.
6. Run a small trust pass on examples and owner names.
   Long rendered files have to be exact or they should be shorter.

# Bottom Line

The worst rendered agent homes are not large because the work is complex. They
are large because the markdown is still too close to the typed source tree.
The next win is not more prose polish. The next win is better lowering.
