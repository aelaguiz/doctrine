# Agent Linter

The Doctrine Agent Linter is the public skill this repo ships today.
It audits Doctrine authoring with a findings-first report that is easy for a
human to use.

Use it when you want to audit:

- one `AGENTS.prompt`, `SOUL.prompt`, or `SKILL.prompt`
- a full skill package or full flow
- a repo's instruction-bearing surfaces

The compiler still owns parse, type, route, and emit failures.

## Install

Use one line:

```bash
npx skills add .
```

Run that from the Doctrine repo root.
That installs the checked-in `agent-linter` skill from this repo.
If the CLI asks where to install it, pick the agent you use.

Want a no-prompt Codex install?

```bash
npx skills add . -g -a codex -y
```

Restart Codex after install so it reloads the skill tree.

## What It Checks

The skill looks first for the highest-value authoring problems:

- weak resolver names or descriptions
- fat always-on context
- prompt bulk that does not buy clearer loading or stronger reuse
- repeated rules that should be shared
- skills that hardcode changing invocation facts
- runtime-boundary leaks
- safety or other runtime control that belongs in the harness
- exact work forced into prose
- authored-versus-emitted drift
- contradiction across related surfaces
- weak handoff shape
- hard-to-read wording

It uses exact evidence from the inspected surfaces.
If the evidence is missing, it should say that plainly.
Those calls still land under the existing `AL###` family. The skill teaches the
judgment more clearly, not with a bigger public code set.

## Prompt Comments

Lines that start with `#` in Doctrine `.prompt` files are authoring comments.
They do not go into the agent.
They are often good because they explain intent without spending runtime
budget.

The skill should not flag those comments as always-on bloat or emitted drift
by default.
It should only surface them when they mislead the author about shipped
behavior or contradict the real emitted surface.

## How To Use It

Naive use should work:

- `Audit this SKILL.prompt`
- `Audit this Doctrine skill package`
- `Audit this Doctrine flow`
- `Audit our repo's agent surfaces and tell me what to fix first`

Specific asks should work too:

- `Use $agent-linter on skills/agent-linter/prompts/SKILL.prompt`
- `Audit authored versus emitted drift for this skill package`
- `Audit this full skill package end to end`

The skill should take the full scope the ask deserves.
If you want repo-wide coverage, say that clearly and it should stay broad.

## Maintainer Source Of Truth

The live package source is `skills/agent-linter/prompts/`.

The repo proof bundle target is:

```bash
uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_skill
```

That writes the emitted proof bundle to `skills/agent-linter/build/`.

The public install bundle target is:

```bash
uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_public_skill
```

That writes the install tree to `skills/.curated/agent-linter/`.

The current structured-output proof inputs and outputs live under the dated
`docs/AGENT_LINTER_*` proof files.
Use
`docs/AGENT_LINTER_CODEX_CLI_PROOF_2026-04-16.md`
for the current proof command, fixture, schema, and saved output.

## Maintainer Refresh

From a Doctrine source checkout, refresh the public install tree with:

```bash
rm -rf skills/.curated/agent-linter
uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_public_skill
```

That keeps the public `npx skills` surface in sync with the live package
source in `skills/agent-linter/prompts/`.
