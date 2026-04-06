`InvalidOverrideBriefingAgent` does not render an `AGENTS.md`.

Compiler error:

- `override context_note` is invalid because `BaseBriefingAgent` does not define `context_note` in `workflow`.
- If the intent is to add a new section, drop `override` and define `context_note` as a new key.
- If the intent is to control placement, use explicit-order mode and place the new section directly.
