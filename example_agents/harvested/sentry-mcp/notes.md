# Notes

## Source Summary

This source combines a strict repo-level AGENTS file with implementation
guidance for adding tools, securing OAuth flows, formatting responses, and
documenting structured namespace data for an embedded agent.

## High-Signal Patterns

- Tool count governance is explicit. The repo sets a hard ceiling and explains
  why the cap exists.
- Quality gates are concrete. Type-check, lint, and test commands are named
  directly, not implied.
- Tool definitions are typed and annotated. Visibility, safety, and exposure
  are treated as separate controls.
- Security rules are not generic. The docs spell out SSRF validation, token
  hygiene, cookie handling, and error sanitization.
- Response formatting has a reusable shape. Markdown sectioning and "next
  steps" guidance are treated as a contract.
- The nested CLAUDE data doc shows a schema-first content catalog for an
  embedded agent, including generation and cache rules.

## What This Teaches Doctrine

This source is useful for Doctrine examples that need:

- explicit numeric limits and fail-loud quality gates
- typed capabilities and tool visibility rules
- negative guardrails around secrets, URLs, and unsafe inputs
- reusable response formatting contracts
- data-backed agent guidance that stays separate from agent prose

