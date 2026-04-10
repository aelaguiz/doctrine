# Candidate Tests

## Source Summary

Harvest from an MCP server repo with hard tool-budget rules, security
constraints, and reusable data-driven guidance for an embedded agent.

## High-Signal Patterns

- Pattern: explicit tool-count cap with reasons.
  Doctrine pull: an example that proves the language can express a bounded
  capability set and fail when the set gets too large.

- Pattern: tool safety annotations and exposure controls.
  Doctrine pull: a Doctrine example that distinguishes read-only tools,
  destructive tools, and hidden internal helpers.

- Pattern: security policy around URLs, tokens, and cookies.
  Doctrine pull: a negative guardrail example for unsafe external input and
  secret leakage.

- Pattern: response formatting contract.
  Doctrine pull: a rendering example that keeps section order and "next steps"
  stable without hard-coding product names.

- Pattern: structured namespace documentation for an embedded agent.
  Doctrine pull: an example that treats documentation data as a typed catalog
  rather than prose-only memory.

## Candidate Doctrine Examples

- Title: Tool budget and capability cap
  Main bucket: `commands_and_quality_gates`
  Likely surface: a hard numeric limit on visible tools with an explicit
  reason and a compile-fail if exceeded.

- Title: Safe tool annotations
  Main bucket: `skills_tools_and_capabilities`
  Likely surface: typed tool metadata that distinguishes read-only, destructive,
  idempotent, and hidden helpers.

- Title: Security guardrails for external inputs
  Main bucket: `negative_guardrails`
  Likely surface: URL validation, secret redaction, and explicit fail-loud
  responses for unsafe inputs.

- Title: Structured data namespace catalog
  Main bucket: `domain_specific_constraints`
  Likely surface: a typed documentation artifact that defines what a domain
  namespace contains and how it is regenerated.

## Candidate Diagnostics

- Diagnostic idea: reject a tool definition that claims to be read-only but is
  annotated as destructive or omits required safety metadata.
- Diagnostic idea: reject a workflow that allows unrestricted external URLs or
  leaks token-like values in an error path.

## Keep Out

- Sentry-specific tool names, OAuth implementation details, and other repo
  labels in the final Doctrine example text.
- Broad "security best practices" prose that does not point to a specific
  contract or validation step.
