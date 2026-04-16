---
title: "Doctrine - LLM Agent Linter For Authoring"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: design
related:
  - PRINCIPLES.md
  - docs/FIRST_CLASS_OPINIONATED_WARNING_LAYER_FOR_AUTHORING_2026-04-16.md
  - docs/AUTHORING_PATTERNS.md
  - docs/COMPILER_ERRORS.md
---

# TL;DR

- Outcome: define a first-class `agent linter` for Doctrine users.
- Product boundary: the shipped core linter must enforce Doctrine's generic
  authoring laws. It must not bake in policy from this repo or from any one
  downstream harness.
- Run modes: it must work in `single-target` mode and in `batch` mode so it
  can catch both local problems and cross-agent duplication.
- Result shape: findings must use stable `AL###` codes with a short title,
  rationale, evidence, and a default recommendation.
- Non-goal: this doc does not cover provider calls, LiteLLM setup, retries, or
  transport.

## Current Artifacts

- Prompt:
  [AGENT_LINTER_PROMPT_2026-04-16.md](AGENT_LINTER_PROMPT_2026-04-16.md)
- Schema:
  [AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json](AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json)
- Proof fixture:
  [AGENT_LINTER_PROOF_FIXTURE_2026-04-16.json](AGENT_LINTER_PROOF_FIXTURE_2026-04-16.json)
- Codex CLI proof:
  [AGENT_LINTER_CODEX_CLI_PROOF_2026-04-16.md](AGENT_LINTER_CODEX_CLI_PROOF_2026-04-16.md)
- Captured structured output:
  [AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16.json](AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16.json)

# 1) Product Boundary

This linter is for people who use Doctrine to author agent systems.

It should review:

- authored prompt source
- emitted agent Markdown
- imported skills, modules, and contracts
- exact side inputs that the caller chooses to provide

It should not hard-code:

- this repo's internal workflow rules
- one team's release process
- one harness's private file layout
- one product's naming rules
- one organization's capability model

Core Doctrine should ship the generic linter.
Teams may add their own overlay rules on top.

# 2) Core Laws The Shipped Linter Should Enforce

The core `AL###` catalog should come only from Doctrine's authoring laws.

## 2.1 Core laws

- context is a budget
- load depth on demand
- write for resolvers
- keep runtime concerns out of authored doctrine
- put exact truth in typed surfaces
- reserve prose for judgment
- reuse beats repetition
- repeated work should become reusable doctrine
- make bloat visible

## 2.2 What this means in practice

The linter should ask:

- Is this always-on text bigger than it needs to be?
- Is this pasted handbook text that should live behind a pointer?
- Is this rule duplicated across several agents?
- Is this repeated method really a skill?
- Is exact truth hidden in prose?
- Is the role clear about what it owns and what it leaves behind?
- Are names and descriptions clear enough for a resolver?
- Is the prose easy to read?
- Do the instructions contradict each other?

# 3) Core Vs Overlay Rules

The shipped linter needs a hard line between core Doctrine rules and local
policy packs.

## 3.1 Core `AL###` rules

These ship with Doctrine.
They must stay generic across users.

## 3.2 Overlay rules

Teams may load extra rules from a host profile.
Those extra rules should use a different prefix, not `AL###`.

Examples of overlay-only checks:

- product-specific tone rules
- one harness's capability allowlist rules
- one repo's file naming rules
- one team's approval flow
- one org's forbidden tools

## 3.3 Why this matters

If core Doctrine ships one team's local policy as if it were a language law,
the product will feel wrong to most users.

# 4) Review Packet

The linter should run on a review packet.
The caller decides what exact facts go into that packet.

## 4.1 Core packet inputs

- authored Doctrine source for the current target
- emitted Markdown for the same target
- imported skill text
- imported module text
- typed declarations and compile graph facts
- file paths and target names

## 4.2 Optional exact side inputs

- line counts
- section size stats
- duplicate-block reports
- reading-level metrics
- declared constraints supplied by the caller

The linter may use optional side inputs only when they are actually present.

# 5) Run Modes

The linter must support two first-class run modes.

## 5.1 `single-target`

Use this when linting one compiled target with its imports.

Best for:

- readability
- vague wording
- local contradiction
- weak names and descriptions
- exact truth hidden in prose
- unclear ownership
- missing stop lines

### Good

```md
Target: `InterviewSummaryWriter`

Input packet:
- authored source for `InterviewSummaryWriter`
- emitted Markdown for `InterviewSummaryWriter`
- imported skill `SourceGrounding`
- typed output contract for the final summary
```

### Bad

```md
Target: `InterviewSummaryWriter`

Input packet:
- the agent home only

Then ask the linter to judge contradiction, duplication across agents, and
whether the final output prose matches a contract it never saw.
```

## 5.2 `batch`

Use this when linting several compiled targets together.

Best for:

- repeated doctrine across agents
- repeated step lists
- handbook text copied into many role homes
- cross-agent contradiction
- local rules that should move into one shared skill or module

### Good

```md
Batch targets:
- `InterviewSummaryWriter`
- `InterviewSummaryReviewer`
- `InterviewPlanWriter`

Shared packet:
- authored source for all three targets
- emitted Markdown for all three targets
- imported shared skills
- duplicate-block hints
```

### Bad

```md
Batch targets:
- `InterviewSummaryWriter`
- `InterviewSummaryReviewer`
- `InterviewPlanWriter`

Input packet:
- only the emitted Markdown for `InterviewSummaryWriter`

Then ask the linter to find repeated law across all three agents.
```

# 6) Output Contract

Every finding should return:

- `code`
- `title`
- `severity`
- `confidence`
- `run_mode`
- `scope`
- `affected_targets`
- `principle_rule`
- `evidence`
- `why_it_matters`
- `recommended_fix`
- `fix_steps`
- `suggested_rewrite`
- `related_evidence`
- `good_example`
- `bad_example`

If the model cannot point to exact evidence, it must not emit the finding.

## 6.1 Best-In-Class Output Goals

The best linter output should do five things well:

- tell the developer fast if the run passed or failed
- show the most important fixes first
- prove each finding with exact evidence
- make cross-agent duplication easy to see
- stay stable enough for terminals, editors, CI, and JSON consumers

The output should never feel like a vague essay.
It should read like a strong linter: short summary first, then precise finding
cards, then machine-readable detail.

## 6.2 Default Render Layers

The linter should have four render layers.

### Layer 1: run summary

Show:

- pass or fail
- targets linted
- count by severity
- top finding codes
- whether strict mode failed the run

### Layer 2: actionable findings

Show the highest-severity findings first.
Within one severity, sort by the finding with the clearest fix first.

### Layer 3: evidence and rewrite help

Each finding should show:

- the exact bad span
- any conflicting span
- why the linter thinks this is a problem
- the smallest credible fix
- a suggested rewrite when useful

### Layer 4: machine output

Return the same findings in JSON so editors, CI, and custom tools can consume
them.

## 6.3 Finding Card Shape

The human-facing finding card should include:

- severity badge
- finding code and title
- affected target or targets
- one-sentence summary
- principle rule
- exact evidence
- why it matters
- recommended fix
- concrete fix steps
- suggested rewrite when useful
- good example
- bad example

For cross-agent duplication findings, add:

- all affected targets
- normalized repeated text
- shared owner recommendation

## 6.4 Helpful Defaults

By default, the linter should:

- group findings by severity
- collapse low-severity findings behind a summary if there are many
- show only one copy of the same duplicate block, then list the affected
  targets
- show contradiction findings side by side when two spans conflict
- show a rewrite suggestion for wording, readability, and stop-line findings
- show a shared extraction suggestion for duplication findings

## 6.5 Default Colorization

Terminal output should be colorized by default.

Recommended behavior:

- `--color=auto` is the default behavior
- use color whenever stdout is a TTY
- support `--color=always`
- support `--color=never`
- respect `NO_COLOR`

The output must not rely on color alone.
Every colored item must also have a text label.

Recommended portable color map:

| Item | Default style |
| --- | --- |
| pass summary | bold green |
| fail summary | bold red |
| `high` severity | bold red |
| `medium` severity | bold yellow |
| `low` severity | bold cyan |
| code id like `AL200` | bold magenta |
| file path or target name | underline |
| evidence label | bold white |
| fix label | bold green |
| warning note | bold yellow |
| good example label | green |
| bad example label | red |

Accessibility rules:

- always print labels such as `[HIGH]`, `[FIX]`, and `[EVIDENCE]`
- keep contrast strong on dark and light terminals
- never use red vs green alone to express meaning
- use indentation and grouping so monochrome output still reads cleanly

## 6.6 Exit Status

The linter should use simple exit codes:

- `0`: no findings at or above the fail threshold
- `1`: findings at or above the fail threshold
- `2`: linter execution failed, such as invalid packet or provider failure

The run summary should always say why the exit code was chosen.

## 6.7 Mockup: Concise Single-Target Terminal Output

In the mockups below, color tags show the intended default terminal colors.

```text
<red>[FAIL]</red> Doctrine agent linter found 3 findings in <underline>InterviewSummaryWriter</underline>

  <red>[HIGH]</red>   1
  <yellow>[MEDIUM]</yellow> 2
  <cyan>[LOW]</cyan>    0

Top codes:
  <magenta>AL800</magenta> Internal contradiction
  <magenta>AL400</magenta> Exact truth hidden in prose
  <magenta>AL720</magenta> Missing priority or stop line

Next actions:
  1. Fix the contradiction in the answer-length instruction
  2. Move exact final output requirements into the declared contract
  3. Add a stop line so the role does not widen scope

Run mode: single-target
Fail threshold: medium
Exit code: 1
```

Why this mockup is good:

- verdict first
- counts are easy to scan
- top codes are visible
- next actions are short and useful

## 6.8 Mockup: Expanded Single-Target Finding Card

```text
<red>[HIGH]</red> <magenta>AL800</magenta> Internal contradiction
Target: <underline>InterviewSummaryWriter</underline>
Principle: keep instructions consistent

Summary:
  The role tells the agent to keep the answer under five lines and also asks
  for a full, exhaustive analysis.

<white>[EVIDENCE A]</white>
  "Always keep the answer under five lines."

<white>[EVIDENCE B]</white>
  "Provide a full, exhaustive analysis of every interview theme."

Why this matters:
  These instructions pull in opposite directions. The agent cannot satisfy
  both reliably.

<green>[FIX]</green>
  Pick a default and state the exception clearly.

Fix steps:
  1. Keep the short-answer rule as the default
  2. Add an exception for cases where the user asks for depth
  3. Remove the word "always" if depth is sometimes required

Suggested rewrite:
  "Be concise by default. Go longer only when the user asks for depth."

Good example:
  "Be concise by default. Go longer only when the user asks for depth."

Bad example:
  "Always keep the answer under five lines. Provide a full, exhaustive
  analysis of every interview theme."
```

Why this mockup is good:

- the conflict is proven with two spans
- the fix is small and concrete
- the rewrite is ready to use

## 6.9 Mockup: Batch Duplication Finding

```text
<yellow>[MEDIUM]</yellow> <magenta>AL200</magenta> Duplicate rule across agents
Targets:
  - <underline>InterviewSummaryWriter</underline>
  - <underline>InterviewSummaryReviewer</underline>
  - <underline>InterviewPlanWriter</underline>
Run mode: batch

Summary:
  The same three-line evidence-check rule appears in three agents.

Normalized repeated text:
  "Check each claim against a source quote.
   Mark weak quotes.
   Remove unsupported claims."

Why this matters:
  This rule now has three owners. If one copy changes, the others can drift.

<green>[FIX]</green>
  Move this rule into one shared skill, then point each agent to that skill.

Shared owner suggestion:
  skill ClaimEvidenceCheck
  description: Verify that each draft claim has direct support from a source
  quote before the writer or reviewer finalizes work.

Affected spans:
  InterviewSummaryWriter: lines 18-20
  InterviewSummaryReviewer: lines 14-16
  InterviewPlanWriter: lines 22-24
```

Why this mockup is good:

- it shows one copy of the repeated text
- it names all affected targets
- it gives the developer a clear extraction direction

## 6.10 Mockup: Readability Finding With Rewrite Help

```text
<yellow>[MEDIUM]</yellow> <magenta>AL700</magenta> Reading level too high
Target: <underline>InterviewSummaryReviewer</underline>

Summary:
  One instruction block uses dense abstract language that is harder to read
  than it needs to be.

<white>[EVIDENCE]</white>
  "Downstream operators should independently operationalize the artifact-level
  implications of the present intervention."

Why this matters:
  Short, plain language is easier to review and easier to follow.

<green>[FIX]</green>
  Replace abstract nouns with direct verbs and split the sentence.

Suggested rewrite:
  "The next reviewer should understand what changed. They should know what to
  do next."
```

Why this mockup is good:

- the hard sentence is visible
- the rewrite is simpler
- the fix explains the writing move, not just the verdict

## 6.11 Mockup: Markdown Report

The linter should also support a markdown report for PR comments, saved
artifacts, or review docs.

```md
# Doctrine Agent Linter Report

- Verdict: fail
- Run mode: batch
- Targets: `InterviewSummaryWriter`, `InterviewSummaryReviewer`
- High: 1
- Medium: 2
- Low: 0

## Highest Priority

### [HIGH] AL800 Internal contradiction

Target: `InterviewSummaryWriter`

Summary: The role gives incompatible length instructions.

Evidence:
- "Always keep the answer under five lines."
- "Provide a full, exhaustive analysis of every interview theme."

Recommended fix:
- keep short answers as the default
- add a clear exception for user-requested depth

Suggested rewrite:
> Be concise by default. Go longer only when the user asks for depth.
```

## 6.12 Mockup: JSON Output

The JSON output should carry the same truth as the terminal output.

```json
{
  "verdict": "fail",
  "run_mode": "batch",
  "fail_threshold": "medium",
  "counts": {
    "high": 1,
    "medium": 2,
    "low": 0
  },
  "targets": [
    "InterviewSummaryWriter",
    "InterviewSummaryReviewer"
  ],
  "findings": [
    {
      "code": "AL800",
      "title": "Internal contradiction",
      "severity": "high",
      "confidence": "high",
      "affected_targets": [
        "InterviewSummaryWriter"
      ],
      "principle_rule": "keep instructions consistent",
      "summary": "The role gives incompatible length instructions.",
      "evidence": [
        {
          "label": "A",
          "text": "Always keep the answer under five lines."
        },
        {
          "label": "B",
          "text": "Provide a full, exhaustive analysis of every interview theme."
        }
      ],
      "why_it_matters": "The agent cannot satisfy both instructions reliably.",
      "recommended_fix": "Keep one default rule and state the exception.",
      "fix_steps": [
        "Keep the short-answer rule as the default",
        "Add an exception for user-requested depth",
        "Remove the word 'always' if depth is sometimes required"
      ],
      "suggested_rewrite": "Be concise by default. Go longer only when the user asks for depth.",
      "good_example": "Be concise by default. Go longer only when the user asks for depth.",
      "bad_example": "Always keep the answer under five lines. Provide a full, exhaustive analysis of every interview theme."
    }
  ]
}
```

## 6.13 Best Possible Developer Experience

The output is best in class when a developer can do all of this without extra
guesswork:

- see in one screen whether the run failed
- know which finding to fix first
- see the exact bad text
- understand why it is bad
- copy a suggested rewrite when that helps
- understand which agents share a duplicate rule
- trust that the terminal output and JSON output match

# 7) Stable Code Bands

The core linter should use stable numbered codes.

| Band | Theme |
| --- | --- |
| `AL1xx` | context and load shape |
| `AL2xx` | duplication and reuse |
| `AL3xx` | runtime boundary and shadow authority |
| `AL4xx` | exact truth and declared constraints |
| `AL5xx` | role shape and handoffs |
| `AL6xx` | names and descriptions |
| `AL7xx` | readability and wording |
| `AL8xx` | contradiction and consistency |
| `AL9xx` | skill boundaries and law placement |

# 8) Core Finding Catalog

Each code below is part of the shipped Doctrine catalog.
Each one includes a real good example and a real bad example.

## `AL100` Oversized Always-On Context

### What it means

The role home carries too much always-on text.
It reads like a handbook, not a thin role.

### Why it matters

Context is a budget.
Large always-on text hides the real job and lowers signal.

### Good

```md
You write the first draft of the customer interview summary.

Read first:
- the transcript
- the summary rubric skill

Leave behind:
- one draft summary
- one blocker note if a source quote is missing
```

### Bad

```md
You write the first draft of the customer interview summary.

Before you start, read this full handbook:
- the full interview style guide
- the full editing guide
- the full quoting guide
- the full glossary
- the full archive of past summaries
- the full team review checklist

Keep all of this in mind on every turn.
```

### Default recommendation

Move deep reference material into a shared skill, module, or docs index.
Keep the role home on job, inputs, and outputs.

## `AL110` Pasted Reference Instead Of Pointer

### What it means

The author pasted long reference text into a role that should point at a shared
source.

### Why it matters

Load depth on demand beats pasted handbooks.

### Good

```md
Use the `InterviewQuotePolicy` skill for quote rules.
Do not restate the full quote policy here.
```

### Bad

```md
Quote rules:
1. Keep quotes exact.
2. Mark cuts with brackets.
3. Never merge two speakers.
4. Keep timestamps when present.
5. Avoid long quotes unless needed.
6. Prefer short evidence-rich excerpts.

Repeat this same block in every writer and reviewer role.
```

### Default recommendation

Replace pasted reference text with a pointer to one shared source.

## `AL120` Deep Procedure In The Role Home

### What it means

The role home teaches a reusable method step by step instead of calling a
shared skill or module.

### Why it matters

Repeated work should become reusable doctrine.

### Good

```md
Use the `SourceGrounding` skill before you write claims from the transcript.
```

### Bad

```md
Before you write any claim:
1. find the source quote
2. copy the quote into notes
3. mark the speaker
4. mark the time
5. compare the claim to the quote
6. remove the claim if the quote is weak

Keep this six-step method inside each role home.
```

### Default recommendation

Move the reusable method into a skill.
Keep only the trigger and expected output in the role.

## `AL200` Duplicate Rule Across Agents

### What it means

The same rule or step list appears in several agents in one batch run.

### Why it matters

Reuse beats repetition.
One rule should have one owner.

### Good

```md
Agent `InterviewSummaryWriter`:
Use the `EvidenceCheck` skill before you finalize the draft.

Agent `InterviewSummaryReviewer`:
Use the `EvidenceCheck` skill when you review factual claims.
```

### Bad

```md
Agent `InterviewSummaryWriter`:
Check each claim against a source quote.
Mark weak quotes.
Remove unsupported claims.

Agent `InterviewSummaryReviewer`:
Check each claim against a source quote.
Mark weak quotes.
Remove unsupported claims.

Agent `InterviewPlanWriter`:
Check each claim against a source quote.
Mark weak quotes.
Remove unsupported claims.
```

### Default recommendation

Lift the repeated rule into one shared skill or module.

## `AL210` Repeated Method Should Become A Skill

### What it means

Several agents carry the same decision method, but the method has no shared
skill owner.

### Why it matters

A repeated method is exactly what skills are for.

### Good

```md
skill InterviewThemeClustering
description: Group similar interview findings into themes before drafting the
summary.

Writer role:
Use `InterviewThemeClustering` before you write the themes section.
```

### Bad

```md
Writer role:
Group findings into themes by:
1. merging similar ideas
2. naming the pattern
3. keeping one quote per theme

Reviewer role:
Group findings into themes by:
1. merging similar ideas
2. naming the pattern
3. keeping one quote per theme
```

### Default recommendation

Extract the shared method into a skill.

## `AL220` Repeated Background Block Across Agents

### What it means

Several agent homes carry the same background briefing or glossary block.

### Why it matters

Shared background should live once and load where needed.

### Good

```md
Use the `InterviewContext` module for product background.
```

### Bad

```md
Writer role:
Product background:
Our product helps distributed teams run user interviews...

Reviewer role:
Product background:
Our product helps distributed teams run user interviews...

Planner role:
Product background:
Our product helps distributed teams run user interviews...
```

### Default recommendation

Move the shared background block into one importable module.

## `AL300` Runtime Boundary Leak

### What it means

The prompt starts owning runtime state, scheduling, memory, or orchestration
that should not live in authored doctrine.

### Why it matters

Doctrine should help author prompts, not become a second runtime.

### Good

```md
If you need a missing runtime feature, note the gap.
Do not invent hidden state inside the prompt.
```

### Bad

```md
Keep a private file named `session_state.md`.
Update it after every tool call.
Treat that file as the real source of truth for turn state, approvals, and
next actions.
```

### Default recommendation

Remove runtime ownership from the prompt.
Leave it to the runtime or to a host-specific overlay.

## `AL310` Shadow Control Plane

### What it means

The author created a second source of truth in prose that competes with a typed
or declared surface.

### Why it matters

Exact truth should not have two owners.

### Good

```md
Decision status comes from the declared review contract.
Do not add new status labels here.
```

### Bad

```md
The review contract uses:
- `approve`
- `revise`
- `block`

But this prompt also says reviewers may return:
- `soft_pass`
- `needs_voice_work`
- `tentative_ok`
```

### Default recommendation

Delete the shadow surface and keep one canonical owner.

## `AL400` Exact Truth Hidden In Prose

### What it means

The prompt hides exact requirements in narrative prose instead of in a typed or
declared surface.

### Why it matters

Exact truth belongs in a typed surface.
Prose should hold judgment, not machine-trustable facts.

### Good

```md
Declared final output:
- `summary`: required markdown
- `key_quotes`: required list
- `risks`: optional list

Role text:
Use prose for why the strongest quote matters.
```

### Bad

```md
Your final answer should usually include a summary and probably some key quotes.
Add risks if they seem important.
```

### Default recommendation

Move exact requirements into the declared contract.

## `AL410` Prose Drift From Declared Constraints

### What it means

The prompt text conflicts with exact constraints that were supplied in the
review packet.

### Why it matters

If a caller gives exact declared constraints, prose should not widen or narrow
them by accident.

### Good

```md
Declared constraints:
- allowed tools: `ReadFile`, `SearchDocs`

Role text:
Use the declared tools.
If something is missing, stop and note the gap.
```

### Bad

```md
Declared constraints:
- allowed tools: `ReadFile`, `SearchDocs`

Role text:
Use any browser, shell, or external search tool that seems useful.
```

### Default recommendation

Align the prose with the declared constraint surface.

## `AL500` Mixed Role Ownership

### What it means

One role owns too many jobs.

### Why it matters

Thin roles are easier to load, route, and trust.

### Good

```md
You write the first draft of the interview summary.
Do not review or publish it.
Leave behind one draft file.
```

### Bad

```md
You write the first draft, review factual accuracy, approve publication,
publish the final version, and message the team about the result.
```

### Default recommendation

Narrow the role to one clear job and one clear output.

## `AL510` Missing Handoff Artifact

### What it means

The role does not say what concrete artifact or blocker it must leave behind.

### Why it matters

Downstream work should start from a real artifact, not a vague retelling.

### Good

```md
Leave behind:
- `summary_draft.md`
- or one blocker note with the missing source quote
```

### Bad

```md
When you are done, tell the next person what happened and what you think they
should do.
```

### Default recommendation

Require a concrete artifact or a concrete blocker note.

## `AL520` Source Should Be Read, Not Remembered

### What it means

The prompt tells the agent to work from memory or paraphrase when a real source
should be read.

### Why it matters

Direct source beats remembered retelling.

### Good

```md
Read the transcript before you write any claim about the interview.
```

### Bad

```md
Write the summary from your memory of the interview.
If the transcript is long, trust your notes and fill any gaps.
```

### Default recommendation

Point to the real source and remove memory-based fallback language.

## `AL600` Weak Resolver Name

### What it means

A name is too vague to help a resolver or an author know what it is for.

### Why it matters

Names should say what a thing does and when it should load.

### Good

```md
skill ClaimEvidenceCheck
```

### Bad

```md
skill GeneralHelper
```

### Default recommendation

Rename it so the job and scope are clear.

## `AL610` Weak Description

### What it means

A description does not explain purpose, trigger, or boundary.

### Why it matters

Resolvers need short descriptions that help them choose the right thing.

### Good

```md
description: Check whether each draft claim has direct evidence from the source
before the writer finalizes the summary.
```

### Bad

```md
description: Helps with summary work.
```

### Default recommendation

Rewrite the description with purpose, trigger, and limit.

## `AL700` Reading Level Too High

### What it means

The prose is too hard to read for the active style target.
Many teams will set that target near grade 7.

### Why it matters

Short, plain language is easier for humans to review and easier for models to
follow.

### Good

```md
Start with the answer.
Use short sentences.
Name the file you changed.
Say what happens next.
```

### Bad

```md
Downstream operators should be able to independently operationalize the
artifact-level implications of the present intervention without requiring
further interpretive mediation.
```

### Default recommendation

Split long sentences and replace abstract words with common words.

## `AL710` Vague Wording

### What it means

The prose uses vague verbs or nouns that hide the real action.

### Why it matters

Vague wording makes roles wider and harder to follow.

### Good

```md
Update `summary_draft.md` with three supported themes and one quote for each.
```

### Bad

```md
Handle the summary materials carefully and make whatever updates seem
appropriate.
```

### Default recommendation

Replace vague verbs with exact actions and name the artifact directly.

## `AL720` Missing Priority Or Stop Line

### What it means

The prompt gives several goals but does not say which comes first or when to
stop.

### Why it matters

Without a stop line, roles expand on their own.

### Good

```md
First, fix unsupported claims.
If that is blocked, leave one blocker note and stop.
Do not rewrite tone in this role.
```

### Bad

```md
Fix unsupported claims, improve tone, reorganize the summary, review the quote
policy, and clean up any other issues you notice.
```

### Default recommendation

Order the work and add a clear stop rule.

## `AL800` Internal Contradiction

### What it means

One surface gives incompatible instructions.

### Why it matters

Conflicting rules cause unstable behavior.

### Good

```md
Be concise by default.
Go longer only when the user asks for depth.
```

### Bad

```md
Always keep the answer under five lines.
Provide a full, exhaustive analysis of every tradeoff.
```

### Default recommendation

State the priority rule or split default behavior from exceptions.

## `AL810` Cross-Surface Contradiction

### What it means

Two related surfaces disagree with each other.

### Why it matters

Many real prompt failures only show up when two surfaces are read together.

### Good

```md
Shared skill:
Check claims against source quotes.

Writer role:
Run the claim check skill before you finalize the draft.
```

### Bad

```md
Shared skill:
Check claims against source quotes.

Writer role:
Do not spend time checking source quotes.
Trust your first reading and move fast.
```

### Default recommendation

Align local text with the shared source of truth.

## `AL900` Skill Too Broad

### What it means

One skill mixes several unrelated jobs or reads like a handbook.

### Why it matters

Skills should be reusable and narrow enough to trigger clearly.

### Good

```md
skill ThemeClustering
description: Group similar findings into themes before the writer drafts the
summary.
```

### Bad

```md
skill SummaryMasterGuide
description: Covers planning, drafting, tone, citations, review, publishing,
stakeholder messaging, and any other summary work.
```

### Default recommendation

Split the skill by job and keep one repeatable method per skill.

## `AL910` Shared Law Trapped In Local Text

### What it means

One local role carries a rule that should be shared by many roles.

### Why it matters

Shared law should live in a shared owner, not in one local prompt.

### Good

```md
Shared module:
All customer-facing summaries must cite direct quotes for factual claims.

Writer role:
Follow the shared evidence rule.
```

### Bad

```md
Writer role only:
All customer-facing summaries must cite direct quotes for factual claims.

Reviewer and planner roles repeat the same law in their own local wording.
```

### Default recommendation

Lift the shared law into a shared module or skill.

# 9) Severity And Confidence

## 9.1 Severity

- `high`: likely to mislead the agent or create conflicting truth
- `medium`: likely to create drift, bloat, or poor reuse
- `low`: likely to reduce clarity, but lower risk

## 9.2 Confidence

- `high`: exact evidence and low ambiguity
- `medium`: strong evidence, but local intent might justify it
- `low`: weak signal; hide it by default

# 10) Prompt Rules For The Linter

The linter prompt should tell the model:

- You are not a compiler.
- You are not judging product correctness.
- You are reviewing authoring quality against the supplied Doctrine laws.
- You must cite exact evidence.
- You must prefer a few strong findings over many weak ones.
- You must not guess hidden runtime facts.
- You must not invent repo-local policy that is not in the review packet.

# 11) Hybrid Checks

Some checks work best when exact signals and LLM judgment work together.

## 11.1 Strong hybrid checks

- `AL100` oversized context
- `AL200` duplicate rule across agents
- `AL220` repeated background block
- `AL400` exact truth hidden in prose
- `AL410` prose drift from declared constraints
- `AL700` reading level too high

For these, deterministic helpers may provide:

- size stats
- duplicate-block hints
- declared constraints
- reading metrics
- target lists

## 11.2 Pure LLM-heavy checks

- `AL710` vague wording
- `AL720` missing priority or stop line
- `AL800` internal contradiction
- `AL810` cross-surface contradiction
- `AL900` skill too broad

# 12) Bottom Line

The right product is a Doctrine `agent linter`.

Its core catalog should stay generic for Doctrine users.
It should support one-target lint and batch lint.
It should use stable `AL###` codes.
And every finding should come with exact evidence, a clear rationale, and a
real good example and bad example.
