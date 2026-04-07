`InvalidOverrideBriefingAgent` does not render an `AGENTS.md`.

Canonical compiler error:

```text
E001 compile error: Cannot override undefined inherited entry

Location:
- examples/05_workflow_merge/prompts/AGENTS.prompt

Detail:
- Cannot override undefined workflow entry in agent BaseBriefingAgent slot workflow: context_note

Trace:
- compile agent `InvalidOverrideBriefingAgent` (examples/05_workflow_merge/prompts/AGENTS.prompt)

Hint:
- If this entry is new, define it directly instead of using `override`.

Cause:
- E001 Cannot override undefined workflow entry in agent BaseBriefingAgent slot workflow: context_note
```

Canonical reference:

- [docs/COMPILER_ERRORS.md](../../../docs/COMPILER_ERRORS.md)
