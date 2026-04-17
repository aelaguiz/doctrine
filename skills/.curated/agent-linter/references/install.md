# Install

This skill now has one simple install command from the repo root.

## One-Line Install

```bash
npx skills add .
```

Run that from the Doctrine repo root.
That installs the checked-in `agent-linter` skill from this repo.
If the CLI asks where to install it, pick the agent you use.

## Fast Codex Install

```bash
npx skills add . -g -a codex -y
```

Restart Codex after install so it reloads the local skill tree.

## Maintainer Refresh

From a Doctrine source checkout, refresh the public install artifact with:

```bash
rm -rf skills/.curated/agent-linter
uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_public_skill
```

This writes the checked-in public install tree to:

```text
skills/.curated/agent-linter/
```

If you also want the local maintainer build tree, refresh that too:

```bash
rm -rf skills/agent-linter/build
uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_skill
```

## Use It

Use the installed skill when you want to:

- audit one Doctrine prompt or skill package
- compare authored and emitted outputs
- check several related prompts or packages for duplication or contradiction

Typical asks:

- `Use $agent-linter on skills/agent-linter/prompts/SKILL.prompt`
- `Audit this Doctrine skill package for thin-harness fit`
- `Lint these two Doctrine prompt homes for duplicate method text`
