# Compiler Errors

This document is the canonical numbered list of compiler errors for the language.

The goal is to keep error identities stable even as the wording evolves.

Current intent:
- once an error number is assigned, we should try not to reuse it for a different meaning
- parser output and examples should refer to these numbers
- wording can tighten over time, but the underlying rule should stay stable

## E001: Cannot Override Undefined Workflow Entry

This error occurs when a child agent uses `override key:` inside `workflow`, but the inherited workflow does not define that key.

Why this is an error:
- `override` means "replace an inherited entry in place"
- if the parent does not define the key, there is nothing to replace
- new workflow entries should be introduced explicitly, not smuggled in through `override`

How to fix it:
- if the entry is new, define it as a bare `key:`
- if order matters, use explicit-order mode and place the new key intentionally
- if the key was meant to override something inherited, correct the key name so it matches the parent

Current example:
- [invalid override briefing agent](/Users/aelaguiz/workspace/pyprompt/examples/05_workflow_merge/ref/invalid_override_briefing_agent/COMPILER_ERROR.md)

## E002: Missing Rendered Section Title

This error occurs when a new workflow section would render a heading, but the source does not provide the heading string explicitly.

Why this is an error:
- rendered section titles are authored data
- the compiler should never derive visible section headings from internal keys
- omission is only valid when an inherited title is being reused intentionally

How to fix it:
- add a title string to the new section, for example `context_note: "Context Note"`
- add a title string to the agent-level workflow block, for example `workflow: "Instructions"`
- add a title string to a reusable workflow declaration, for example `workflow Greeting: "Greeting"`
- if the entry is a true inherited override that should keep the old title, use `override key:` without a new title
