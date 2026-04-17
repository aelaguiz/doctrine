# Thin Harness, Fat Skills

This is Doctrine's durable read of Garry Tan's "thin harness, fat skills"
rule.
Use it when you need the short design test behind Doctrine features, docs, and
audits.
For the repo-wide value statement, see [../PRINCIPLES.md](../PRINCIPLES.md).

## The Rule

- Keep the harness thin.
- Put reusable judgment in skills and other loadable docs.
- Put exact truth in typed surfaces.
- Keep runtime behavior out of authored doctrine.

## What "Thin Harness" Means Here

- The harness runs the loop, tools, files, memory, scheduling, and safety.
- Doctrine should not try to own those jobs.
- Doctrine should help the harness load the right context at the right time.
- Always-on context should stay short.

## What "Fat Skills" Means Here

- Put task method, review order, domain judgment, and reusable process in
  loadable skills or modules.
- Write names and descriptions so a resolver can load the right thing.
- Reuse one shared home instead of copying long instructions into many places.
- If a one-off pattern repeats, turn it into reusable doctrine.
- When a skill package still needs host truth, bind it once with typed
  package host slots instead of repeating the same inputs, outputs, and final
  answer prose in every agent home.

## Deterministic Truth Versus Judgment

- Typed inputs, outputs, schemas, routes, and reviews should own exact truth.
- Prose should own reading, synthesis, comparison, and taste.
- Do not hide machine-trustable facts in long prose.
- Do not push runtime control into Doctrine when it belongs in the harness.

## Good Signs

- The agent home stays small.
- A deeper doc or skill loads only when the task needs it.
- One fix lands in one shared place.
- The compiler or emitted typed surface owns exact truth.
- Names and descriptions make the load path obvious.
- A skill package declares `host_contract:` once, the agent binds it once, and
  the package reuses `host:` across its prompt-authored emitted tree.

## Warning Signs

- Root context keeps growing.
- The same guidance is copied into many agent homes.
- A doc tries to control runtime state, scheduling, or tool orchestration.
- Exact contracts live only in prose.
- A feature adds more prompt bulk than reusable leverage.
- A skill package repeats the same host IO prose in many inline skill bridges
  because the typed link was never modeled.

## Review Questions

When you review a change, ask:

1. Did this keep always-on context small?
2. Did shared truth move into one reusable home?
3. Did exact rules move into typed surfaces?
4. Did runtime behavior stay in the harness?
5. Will a better name or description help a resolver load this at the right
   time?

## Related Docs

- [../PRINCIPLES.md](../PRINCIPLES.md): the repo's core values
- [AUTHORING_PATTERNS.md](AUTHORING_PATTERNS.md): how to apply the ideas in real
  authoring work
- [LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md): the shipped typed surfaces
- [SKILL_PACKAGE_AUTHORING.md](SKILL_PACKAGE_AUTHORING.md): how reusable skills
  package and emit, including `host_contract:` and `bind:` for typed host
  slots
- [AGENT_LINTER.md](AGENT_LINTER.md): the shipped judgment-first review skill
  that catches principle pressure the compiler cannot prove
- [DOCTRINE_LEARN.md](DOCTRINE_LEARN.md): the shipped teaching-first skill
  that loads principles, language, packaging, and verification on demand
- [WARNINGS.md](WARNINGS.md): the scoped plan for a first-class compiler
  warning layer

## Source Note

This framing comes from Garry Tan's April 11, 2026 note "Thin Harness, Fat
Skills."
This doc is the durable Doctrine version of that idea.
It replaces the old pasted article with repo-grounded guidance.
