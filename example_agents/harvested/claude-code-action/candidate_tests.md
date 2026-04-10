# Candidate Tests

## `raw/CLAUDE.md`

- Doctrine pressure: action mode detection, prompt construction, cleanup ordering, and stable helper boundaries.
- Candidate example: a top-level action guide that explains how tag mode and agent mode are selected, how the prompt is built, and which cleanup happens in always-run steps.
- Candidate diagnostic: warn when a downstream example ignores the mode split or moves token cleanup into the wrong lifecycle stage.

## `raw/base-action/CLAUDE.md`

- Doctrine pressure: lower-level command gates, provider auth, and a standalone action contract.
- Candidate example: a sub-action instruction file that lists build/test commands and spells out authentication precedence and JSON output handling.
- Candidate diagnostic: flag examples that blur the standalone action API with the wrapper action API.

## `raw/base-action/README.md`

- Doctrine pressure: explicit input/output tables, output names, env vars, and usage examples.
- Candidate example: a markdown contract that shows prompt-only and prompt-file flows, custom environment variables, settings, MCP configuration, and execution-file outputs.
- Candidate diagnostic: warn when an example omits the required prompt-vs-prompt_file exclusivity or misstates the action outputs.

## Good Doctrine Surfaces

- `scope_hierarchy`
- `commands_and_quality_gates`
- `io_contracts_and_handoffs`
- `negative_guardrails`
