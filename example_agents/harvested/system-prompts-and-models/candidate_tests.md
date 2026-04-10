# Candidate Tests

## Why this source matters

This archive gives Doctrine pressure from prompts that are already operationalized in real coding agents.
The best examples are not broad assistant descriptions; they are narrow contracts that constrain tools, modes, and side effects.

## Candidate Doctrine examples

- **Tool contract example**: a prompt that lists concrete tools and required parameters, then forces exact parameter preservation.
- **Read-only planning example**: a planning branch that can inspect and draft but cannot edit, create, or delete files.
- **Mode-router example**: a small intent classifier that selects among `chat`, `do`, and `spec`-style branches from user text.
- **Execution guardrail example**: an assistant prompt that says to do only what was asked and to avoid new docs or extra files unless requested.

## Candidate diagnostics

- `INVALID_TOOL_SCHEMA_REQUIRED_PARAM` for tool definitions that omit required fields.
- `INVALID_READ_ONLY_MODE_MUTATION` for branches that claim to be planning-only but still allow edits.
- `INVALID_MODE_ROUTING_AMBIGUOUS` for prompts that mix classification with execution without a stable branch rule.
- `INVALID_UNREQUESTED_DOCUMENT_CREATION` for prompts that allow documentation creation without user intent.
