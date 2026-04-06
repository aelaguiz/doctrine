`InvalidOverrideBriefingAgent` does not render an `AGENTS.md`.

Compiler error:

- `E001`: `override context_note` is invalid because `BaseBriefingAgent` does not define `context_note` in `workflow`.
- If the intent is to add a new section, drop `override` and define `context_note: "Context Note"` directly in the inherited order.
- In inherited workflows, every parent section must still be accounted for explicitly.

Canonical reference:

- [docs/COMPILER_ERRORS.md](/Users/aelaguiz/workspace/pyprompt/docs/COMPILER_ERRORS.md)
