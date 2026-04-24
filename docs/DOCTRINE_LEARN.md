# Doctrine Learn

The Doctrine Learn skill teaches an agent how to author Doctrine end-to-end.
Where [AGENT_LINTER.md](AGENT_LINTER.md) is the audit brain, Doctrine Learn is
the teaching brain.

Use it when you want to:

- write a fresh Doctrine `AGENTS.prompt`, workflow, review, output schema,
  document, or `SKILL.prompt` package
- port an existing agent or skill into Doctrine
- onboard a teammate into this repo, principles first
- review a Doctrine change with the right mental model

The compiler still owns parse, type, route, and emit failures. Doctrine Learn
teaches you how to avoid them; it does not explain a specific error code.

## Install

Generate the public install tree, then install it:

```bash
uv run --locked python -m doctrine.emit_skill --target doctrine_learn_public_skill
npx skills add .
```

Run those from the Doctrine repo root.
The first command writes `skills/.curated/doctrine-learn/`.
The second command installs that generated tree.
If the CLI asks where to install it, pick the agent you use.

Want a no-prompt Codex install?

```bash
uv run --locked python -m doctrine.emit_skill --target doctrine_learn_public_skill
npx skills add . -g -a codex -y
```

Restart Codex after install so it reloads the skill tree.

## What It Teaches

The entrypoint `SKILL.prompt` stays thin. Depth lives behind twelve
loadable references that the skill's `reference_map` routes to on demand:

- `references/principles.md`: the nine principles from
  [../PRINCIPLES.md](../PRINCIPLES.md) and the thin-harness rule from
  [THIN_HARNESS_FAT_SKILLS.md](THIN_HARNESS_FAT_SKILLS.md). Load first, every
  time.
- `references/language-overview.md`: the shape of a `.prompt` file, the
  declaration vocabulary, and the first three examples to read.
- `references/agents-and-workflows.md`: `agent`, `workflow`, route-only
  turns, `handoff_routing`, `grounding`, and workflow law.
- `references/reviews.md`: `review`, `review_family`, verdict coupling,
  carried state, and review-driven `final_output`.
- `references/outputs-and-schemas.md`: `output`, `output schema`,
  `route field`, `final_output`, output inheritance, and generated schema
  artifacts.
- `references/documents-and-tables.md`: `document`, `table`, readable lists,
  and `render_profile`.
- `references/skills-and-packages.md`: `skill`, `skill package`,
  `SKILL.prompt`, `source:`, `SKILL.source.json`, `host_contract:`,
  `bind:`, and `emit:` companions.
- `references/imports-and-refs.md`: module and symbol imports, addressable
  refs, `self:`, grouped `inherit { ... }`, and multi-root resolution.
- `references/emit-targets.md`: `pyproject.toml` emit targets, `source_root`,
  `lock_file`, `emit_flow`, `emit_skill`, runtime packages,
  `SKILL.source.json`, and `final_output.contract.json`.
- `references/authoring-patterns.md`: the task-first chooser and the
  anti-patterns to avoid.
- `references/examples-ladder.md`: the numbered corpus as a learning path.
- `references/verify-and-ship.md`: `make` targets, diagnostics, versioning,
  and the changelog shape.

Every claim the skill makes about a construct cites at least one real
example path from the shipped corpus (`examples/01_hello_world` through
`examples/149_external_skill_source_target`). No invented snippets.

## How To Use It

Naive use should work:

- `Use $doctrine-learn to teach me how to write a review that gates the
  final answer.`
- `Use $doctrine-learn to walk me through porting this agent into Doctrine.`
- `Use $doctrine-learn to help me pick between output and output schema.`

Specific asks should work too:

- `Use $doctrine-learn, load references/outputs-and-schemas.md, and show me
  the smallest working output schema that emits a nullable route field.`
- `Use $doctrine-learn to explain workflow law before I add this handoff.`

The skill routes to one matching reference for the author's surface, cites a
real example, and shows the smallest working snippet.

## Maintainer Source Of Truth

The live package source is `skills/doctrine-learn/prompts/`.
`SKILL.prompt` is the lean entry point.
Depth lives under `prompts/refs/` as Doctrine `document` declarations that
the `emit:` block compiles into `references/<slug>.md`. The emitted
`.md` bundle is verifier-owned proof; the authored truth is the `.prompt`
sources.

The repo proof bundle target is:

```bash
uv run --locked python -m doctrine.emit_skill --target doctrine_learn_skill
```

That writes the emitted proof bundle to `skills/doctrine-learn/build/`.

The public install bundle target is:

```bash
uv run --locked python -m doctrine.emit_skill --target doctrine_learn_public_skill
```

That writes the install tree to `skills/.curated/doctrine-learn/`.

## What This Is Not

Doctrine Learn is teaching-first. It does not replace surfaces the compiler
or other shipped skills already own.

- Running an audit on existing Doctrine code is
  [AGENT_LINTER.md](AGENT_LINTER.md).
- Parse, type, route, and emit failures belong to the compiler.
  See [COMPILER_ERRORS.md](COMPILER_ERRORS.md).
- Harness, runtime, memory, scheduling, and tool-orchestration concerns
  belong to the host runtime, not to Doctrine.
- Unshipped language proposals are out of scope. The skill teaches only
  what ships today in `doctrine/` and in the manifest-backed corpus.

## Maintainer Refresh

From a Doctrine source checkout, refresh the public install tree with:

```bash
rm -rf skills/.curated/doctrine-learn
uv run --locked python -m doctrine.emit_skill --target doctrine_learn_public_skill
```

That keeps the public `npx skills` surface in sync with the live package
source in `skills/doctrine-learn/prompts/`.

## Related Docs

- [../PRINCIPLES.md](../PRINCIPLES.md): the repo's core values
- [THIN_HARNESS_FAT_SKILLS.md](THIN_HARNESS_FAT_SKILLS.md): the durable
  thin-harness, fat-skills guide
- [LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md): the shipped syntax and
  declaration reference
- [SKILL_PACKAGE_AUTHORING.md](SKILL_PACKAGE_AUTHORING.md): the canonical
  skill-package authoring guide
- [EMIT_GUIDE.md](EMIT_GUIDE.md): the canonical emit and output-layout guide
- [AGENT_LINTER.md](AGENT_LINTER.md): the audit counterpart to this skill
