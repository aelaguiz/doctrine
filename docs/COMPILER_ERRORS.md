# Compiler Errors

This document is the canonical numbered list of compiler errors for the language.

The goal is to keep error identities stable even as the wording evolves.

Current intent:
- once an error number is assigned, we should try not to reuse it for a different meaning
- parser output and examples should refer to these numbers
- wording can tighten over time, but the underlying rule should stay stable

## E001: Cannot Override Undefined Inherited Entry

This error occurs when an explicit override tries to replace an inherited entry
that does not exist.

Why this is an error:
- `override` means "replace an inherited entry in place"
- if the parent does not define the key, there is nothing to replace
- new entries should be introduced explicitly, not smuggled in through
  `override`

How to fix it:
- if the entry is new, define it as `key: "Title"` in the inherited order
- if the key was meant to override something inherited, correct the key name so it matches the parent

Current example:
- [invalid override briefing agent](/Users/aelaguiz/workspace/pyprompt/examples/05_workflow_merge/ref/invalid_override_briefing_agent/COMPILER_ERROR.md)

## E002: Missing Rendered Section Title

This error occurs when a newly rendered section would need a visible title, but
the source does not provide that title explicitly.

Why this is an error:
- rendered section titles are authored data
- the compiler should never derive visible section headings from internal keys
- omission is only valid when an inherited title is being reused intentionally

How to fix it:
- add a title string to the new section, for example `context_note: "Context Note"`
- add a title string to the agent-level workflow block, for example `workflow: "Instructions"`
- add a title string to a reusable workflow declaration, for example `workflow Greeting: "Greeting"`
- if the entry is a true inherited override that should keep the old title, use `override key:` without a new title

## E003: Missing Inherited Entry

This error occurs when an inherited surface uses explicit exhaustive patching,
but the child fails to account for one of the inherited entries.

Why this is an error:
- inherited patching in the language is explicit and exhaustive
- omission should not silently mean keep, move, or drop
- the compiler should never guess where an inherited section belongs

How to fix it:
- add `inherit key` where the inherited section should remain unchanged
- add `override key:` or `override key: "New Title"` where the inherited section should be replaced
- if we eventually add an explicit deletion form, use that instead of omission
