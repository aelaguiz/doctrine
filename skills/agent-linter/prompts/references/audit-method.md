# Audit Method

This skill is an audit method, not a detector farm.
Use exact evidence plus model judgment.

## Start With Scope

Pick the full honest scope that matches the ask:

- one prompt
- one full skill package
- one full flow
- one repo surface family
- one explicit batch

Do not claim repo-wide coverage if you only read one local file.
Do not collapse a package, flow, or repo audit into one tiny slice just
because that slice was easy to open first.

## Read The Full Frontier First

Read the whole honest surface family before you decide findings.
Do not freeze on the first bad line you see.

Use this frontier map:

- one prompt: the prompt source, emitted Markdown when drift or bloat matters,
  and imported shared doctrine only when it changes meaning
- one full skill package: `SKILL.prompt`, bundled `references/`, `agents/`
  metadata, emitted bundle when shipped output matters, and install notes when
  the package makes claims about them
- one full flow: the flow root, imported skills or modules, typed routes or
  contracts that change meaning, and emitted docs or reviews when shipped
  behavior matters
- one repo surface family: the instruction-bearing files that share the asked
  job, such as `AGENTS.md`, prompt packages, skill packages, runtime metadata,
  and emitted companions when drift matters

Map the family first.
Then read enough of it to make honest cross-surface calls.

## What To Read

Use the real surfaces the runtime can inspect:

- authored prompt source
- emitted Markdown when the comparison matters
- imported skills or modules when shared doctrine is part of the question
- declared constraints or typed facts when they exist

Do not invent hidden files, hidden state, or hidden repo policy.

## Read Order

1. Lock the user ask and the honest scope.
2. Map the full frontier the ask implies.
3. Read the primary authored surfaces.
4. Read shared imports only when they change the local meaning.
5. Read emitted Markdown if the user asked for authored-versus-emitted drift
   or if always-on bloat is part of the concern.
6. Read typed constraints when you need to test prose against exact truth.
7. Decide whether each signal is no issue, one finding, or several distinct
   findings.
8. Then score the strongest real problems.
9. Re-check contradiction, drift, and duplication after the full read.

If the ask is about a package, flow, or repo family, widen early instead of
pretending one file is enough.

## Highest-Value Questions

Ask these first:

- Is the resolver clear about what the target is for and when to load it?
- Is the always-on context too fat?
- Did the added prompt bulk earn reusable leverage, clearer loading, or exact truth?
- Is the prompt helping the harness load the right context at the right time, or trying to carry everything always-on?
- Is a reusable method pasted inline instead of shared?
- Will one fix land in one shared place, or did the author create several owners?
- Is a skill acting like a reusable method call, or did it hardcode changing facts?
- Did prose start owning runtime state, memory, safety control, scheduling, or orchestration?
- Is exact work stuck in prose that should live on a typed or deterministic surface?
- Do authored and emitted surfaces drift?
- Do related surfaces contradict each other?
- Does read-many work end in one compact handoff or a pile of raw notes?
- Is the wording clear enough for a tired human to understand fast?

## Garry-Aligned Rules

Use these rules when the signal is real:

- Keep the harness thin. The prompt should teach judgment, not recreate tooling.
- Help the harness load the right context at the right time instead of stuffing more doctrine into always-on text.
- Keep the skill fat. Reusable process belongs in the skill.
- Add local prompt text only when it earns reusable leverage, clearer loading, or stronger exact truth.
- Keep one shared owner for shared truth so one fix lands in one place.
- Treat the target like parameters to one method call. The skill supplies the process. The inspected surface supplies the world.
- Keep latent work in latent space. Reading, synthesis, and judgment belong to the model.
- Keep deterministic work on deterministic surfaces. Exact counting, routing, validation, assignment, and contract truth should not hide in prose.
- Prefer one compact synthesized handoff over raw notes from many reads.

## Prompt Source Comments

Lines that start with `#` in Doctrine `.prompt` files are authoring comments.
They do not ship to the agent.
They are often good because they explain intent without spending runtime
budget.

Do not flag prompt comments as always-on bloat, emitted drift, or bad shipped
text by default.
Only surface them when they:

- mislead the author about shipped behavior
- shadow a real rule that should live on a shared owner or typed surface
- contradict emitted truth or another authoring surface in a way that matters

## Evidence Rules

- Exact evidence or no finding.
- Cite the smallest span that proves the claim.
- For contradiction, show both sides.
- For drift, show the authored span and the emitted span.
- For duplication, show one normalized duplicate plus the affected targets.
- If the finding is about shipped agent behavior, do not use a prompt comment
  as the sole evidence.
- If evidence is missing, record the gap instead of guessing.
- Push for the smallest credible fix before you suggest a bigger rewrite.

## Surface And Rewrite Discipline

Keep surface tags honest:

- `authored_source` and `emitted_markdown` are different surfaces
- cite the surface the reader will need to edit
- a rewrite should target the surface you cited
- `AL810` cross-surface contradiction findings should cite both surfaces
- use `related_evidence` for the second side of a contradiction, drift, or
  duplicate reach

## Scope Rules

Use these scope tags honestly:

- `single-target`
- `single-target-with-imports`
- `cross-surface`
- `cross-target`

Use the one that fits the evidence.

## Severity

- `high`: likely to mislead the agent or create competing truth
- `medium`: likely to create drift, bloat, or poor reuse
- `low`: lower risk, but still worth fixing when the stronger issues are gone

## Confidence

- `high`: exact evidence and low ambiguity
- `medium`: strong evidence, but local intent might justify it
- `low`: weak signal; keep it out unless it still matters after a cold read

## Output Bar

The human report should feel like a strong code review.
It should clear fog fast, not add more fog:

- findings first
- strongest issues first
- exact evidence on every finding
- concrete fixes
- rewrite help when wording is the issue
- clear next moves
- the smallest credible fix before a larger rewrite

Great output:

- names the strongest issue first
- proves it with exact evidence
- uses the narrowest correct code
- gives a fix the developer can act on now
- shows repeated text once in duplication cases
- gives a rewrite only when the rewrite is clearly useful
- sounds decisive, useful, and human

Weak output:

- sounds plausible but cannot prove the claim
- reports one repo's local policy as if it were Doctrine law
- emits several overlapping findings when one would do
- repeats the bad text with no fix
- gives a rewrite that changes meaning
- sounds flat, timid, or generic
