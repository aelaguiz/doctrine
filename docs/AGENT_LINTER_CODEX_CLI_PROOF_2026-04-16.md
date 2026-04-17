---
title: "Doctrine - Agent Linter Prompt And Schema Codex CLI Proof"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: proof
related:
  - docs/AGENT_LINTER_PROMPT_2026-04-16.md
  - docs/AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json
  - docs/AGENT_LINTER_PROOF_FIXTURE_2026-04-16_v2.json
  - docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v3.json
  - docs/AGENT_LINTER.md
---

# TL;DR

- The prompt in [AGENT_LINTER_PROMPT_2026-04-16.md](AGENT_LINTER_PROMPT_2026-04-16.md)
  worked with `codex exec`.
- The schema in
  [AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json](AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json)
  was accepted by `codex exec --output-schema`.
- The generated output was saved to
  [AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v3.json](AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v3.json)
  and then validated again with `jsonschema`.

# Artifacts

- Prompt:
  [AGENT_LINTER_PROMPT_2026-04-16.md](AGENT_LINTER_PROMPT_2026-04-16.md)
- Plain JSON schema for `codex exec --output-schema`:
  [AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json](AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json)
- Current review-packet fixture:
  [AGENT_LINTER_PROOF_FIXTURE_2026-04-16_v2.json](AGENT_LINTER_PROOF_FIXTURE_2026-04-16_v2.json)
- Current captured structured output:
  [AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v3.json](AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v3.json)

# OpenAI Wrapper

The schema file is the exact plain JSON Schema used by `codex exec`.
For an OpenAI-compatible `response_format`, wrap that schema like this:

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "doctrine_agent_linter_report",
    "strict": true,
    "schema": "<contents of AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json>"
  }
}
```

The important part is that the `schema` field uses the exact contents of
[AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json](AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json).

# Codex CLI Proof Command

This is the working command shape that proved the prompt plus schema:

```bash
tmp_input=$(mktemp)
{
  cat docs/AGENT_LINTER_PROMPT_2026-04-16.md
  printf '\n\n## Review Packet\n\n```json\n'
  cat docs/AGENT_LINTER_PROOF_FIXTURE_2026-04-16_v2.json
  printf '\n```\n'
} > "$tmp_input"

codex exec \
  --ephemeral \
  --sandbox read-only \
  --color never \
  -m gpt-5.4-mini \
  -c 'model_reasoning_effort="low"' \
  --output-schema docs/AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json \
  --output-last-message docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v3.json \
  - < "$tmp_input"

rm -f "$tmp_input"
```

Why this proof shape is useful:

- it uses the real prompt
- it uses the real schema
- it uses a real review packet
- it saves the last message as a reusable proof artifact
- it keeps one current proof path instead of preserving same-day proof history

# Validation Commands

The output was validated two ways.

## 1. JSON parse check

```bash
python -m json.tool docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v3.json >/dev/null
```

Result:

```text
VALID_JSON
```

## 2. Schema validation

```bash
uv run --with jsonschema python - <<'PY'
import json
from jsonschema import Draft202012Validator

with open('docs/AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json') as f:
    schema = json.load(f)
with open('docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v3.json') as f:
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

Result:

```text
SCHEMA_VALID
```

# Result Summary

The proof run returned:

- verdict: `fail`
- run mode: `batch`
- fail threshold: `medium`
- `strict_mode_blocked: true`
- 1 `high` finding
- 2 `medium` findings
- 0 `low` findings

The returned findings covered:

- `AL240` skill hardcodes invocation inputs
- `AL430` deterministic work forced into prose
- `AL550` read-many work leaves raw notes

# Bottom Line

The real prompt, the real schema, and the real fixture worked together under
`codex exec --output-schema`.
The saved output file is valid JSON and schema-valid JSON.

The current proof keeps one live fixture and one live saved output.
Same-day intermediate proof-history files were retired once their durable truth
was folded into this doc and the current v3 proof path.
