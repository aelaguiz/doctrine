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

Generate the public install tree, then install it:

```bash
uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_public_skill
npx skills add .
```

Run those from the Doctrine repo root.
The first command writes `skills/.curated/agent-linter/`.
The second command installs that generated tree.
If the CLI asks where to install it, pick the agent you use.

Want a no-prompt Codex install?

```bash
uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_public_skill
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
That is the one place the skill is authored.
`SKILL.prompt` is the lean entry point.
Depth lives under `prompts/refs/` as Doctrine `document` declarations that
the `emit:` block compiles into `references/<slug>.md` (`audit-method.md`,
`product-boundary.md`, `finding-catalog.md`, `report-contract.md`,
`error-handling.md`, `examples.md`, `install.md`). The emitted `.md`
bundle is verifier-owned proof; the authored truth is the `.prompt` sources.

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

## What This Is Not

The linter is judgment-first.
It will not replace surfaces the compiler already owns.

- Parse, type, route, and emit failures belong to the compiler.
  See [COMPILER_ERRORS.md](COMPILER_ERRORS.md).
- Easy author mistakes the compiler still accepts belong to the fail-loud
  roadmap.
  See [FAIL_LOUD_GAPS.md](FAIL_LOUD_GAPS.md).
- Product truth and domain correctness are out of scope.
- Plain code review is out of scope.

## Structured Output Proof

The skill returns a strict JSON report when driven through
`codex exec --output-schema`.
The evergreen proof inputs and outputs live under
`skills/agent-linter/build_ref/`:

- `output_schema.json`: the plain JSON Schema `codex exec --output-schema`
  accepts.
- `proof_fixture.json`: a real review packet the skill can audit.
- `codex_cli_output.json`: the captured last message from a recent proof
  run.

For an OpenAI-compatible `response_format`, wrap the schema like this:

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "doctrine_agent_linter_report",
    "strict": true,
    "schema": "<contents of skills/agent-linter/build_ref/output_schema.json>"
  }
}
```

### Reproduce The Proof Run

```bash
tmp_input=$(mktemp)
{
  cat skills/agent-linter/build/SKILL.md
  printf '\n\n## Review Packet\n\n```json\n'
  cat skills/agent-linter/build_ref/proof_fixture.json
  printf '\n```\n'
} > "$tmp_input"

codex exec \
  --ephemeral \
  --sandbox read-only \
  --color never \
  -m gpt-5.4-mini \
  -c 'model_reasoning_effort="low"' \
  --output-schema skills/agent-linter/build_ref/output_schema.json \
  --output-last-message skills/agent-linter/build_ref/codex_cli_output.json \
  - < "$tmp_input"

rm -f "$tmp_input"
```

### Validate The Saved Output

```bash
python -m json.tool skills/agent-linter/build_ref/codex_cli_output.json >/dev/null

uv run --with jsonschema python - <<'PY'
import json
from jsonschema import Draft202012Validator

with open('skills/agent-linter/build_ref/output_schema.json') as f:
    schema = json.load(f)
with open('skills/agent-linter/build_ref/codex_cli_output.json') as f:
    data = json.load(f)

Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)
errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
if errors:
    for err in errors:
        print('ERROR', list(err.absolute_path), err.message)
    raise SystemExit(1)
print('SCHEMA_VALID')
PY
```

A successful run prints `SCHEMA_VALID` and the saved output parses as JSON.

## Maintainer Refresh

From a Doctrine source checkout, refresh the public install tree with:

```bash
rm -rf skills/.curated/agent-linter
uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_public_skill
```

That keeps the public `npx skills` surface in sync with the live package
source in `skills/agent-linter/prompts/`.
