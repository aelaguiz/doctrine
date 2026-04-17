# Product Boundary

This skill audits Doctrine authoring quality.
It does not act like the compiler.

## What It Reviews

- Authored prompt source
- Emitted or compiled Markdown
- Imported skills and modules
- Exact side inputs the caller or runtime can prove

## What It Does Not Review

- Parse, type, route, or emit failures
- Product truth
- Repo-local policy that Doctrine does not ship
- Hidden runtime state, memory, safety control, or orchestration
- Generic code quality outside agent authoring

## Compiler Vs Linter

The compiler owns exact language truth.
This skill owns prose and authoring quality.

The compiler owns:

- parse and type failures
- declared graph correctness
- verdict and route semantics the compiler can prove
- emit failures

This skill may still flag:

- prose that shadows a typed surface
- prose that drifts from declared constraints
- shared method text that hardcodes one case
- prose that starts owning harness safety behavior or other runtime control
- exact counting or assignment work forced into prose
- read-many work that leaves raw notes instead of one compact artifact
- weak resolver names or descriptions
- wording that is hard to read or hard to act on

## Core Doctrine Laws

The bundled `AL###` rules come from these Doctrine laws:

- context is a budget
- load depth on demand
- help the harness load the right context at the right time
- write for resolvers
- keep runtime concerns out of authored doctrine
- put exact truth in typed surfaces
- reserve prose for judgment
- reuse beats repetition
- repeated work should become reusable doctrine
- keep one shared owner so one fix lands in one place
- make bloat visible
- keep the harness thin and the reusable process fat
- let the invocation supply the world and the skill supply the method
- keep exact work on deterministic surfaces and judgment in prose

## Evidence Authority

Treat the inspected evidence as the only ground truth.
Do not assume anything outside it.

The evidence may come from:

- direct file reads
- user-pasted text
- emitted Markdown
- imported companions

Use these authority rules:

- authored source is authoritative for local wording
- emitted Markdown is authoritative for always-on text
- imported skills and modules are authoritative for shared doctrine
- declared constraints and typed facts are authoritative when the evidence has them
- duplicate hints are supporting evidence, not sole evidence

## Prompt Source Comments

Lines that start with `#` in Doctrine `.prompt` files are authoring comments.
They do not go into the agent.
They are often good because they explain intent without spending runtime
budget.

Do not flag prompt comments as always-on bloat or emitted drift by default.
Only surface them when they mislead the author about shipped behavior or
contradict the real shipped surface.

## Run Modes

Use `single-target` when one prompt or package needs local review.
Use `batch` when cross-target duplication or contradiction matters.

Direct file reads and pasted text are the normal path.

## Thin Harness, Fat Skill

This package should not need a big helper harness.

Keep these boundaries clear:

- the skill owns the audit method
- the runtime owns file access, normal tool calls, safety control, and runtime control flow
- typed surfaces own exact truth
- the report contract owns the human report shape

If a local script or heuristic list is doing the thinking, the split is wrong.

## Non-Goals

Do not:

- re-report compiler errors
- invent hidden context
- turn one repo's policy into Doctrine law
- turn one repo's safety overlay into Doctrine law
- browse outside the inspected scope
- rely on memory when the evidence is missing
