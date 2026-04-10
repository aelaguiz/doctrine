# Candidate Tests

## Source Summary

Harvest from a production agent SDK that treats agent config, tool use,
handoffs, guardrails, and result surfaces as separate contracts.

## High-Signal Patterns

- Pattern: repo-level verification gate before marking work complete.
  Doctrine pull: an instruction file that requires explicit validation before a
  task can be closed.

- Pattern: agent config hub with typed `instructions`, `tools`, `handoffs`,
  `output_type`, and dynamic instructions.
  Doctrine pull: a single example that proves one declared object can carry
  multiple typed workflow roles without becoming magical.

- Pattern: manager-vs-handoff orchestration split.
  Doctrine pull: a pair of examples that distinguish "tool-based delegation"
  from "control transfer to a specialist."

- Pattern: handoff metadata versus next-agent history.
  Doctrine pull: a portable-truth example where a carrier field names the next
  owner while history filtering changes what the next agent sees.

- Pattern: result surfaces split into final output, run items, interruptions,
  and raw responses.
  Doctrine pull: a Doctrine example that teaches `output` and `trust_surface`
  as different from history, metadata, and resumable state.

## Candidate Doctrine Examples

- Title: Verified repo contributor workflow
  Main bucket: `commands_and_quality_gates`
  Likely surface: mandatory verification before closeout, explicit command-first
  instructions, and fail-loud completion checks.

- Title: Agent config contract
  Main bucket: `skills_tools_and_capabilities`
  Likely surface: typed declarations for instructions, tools, handoffs, and
  structured outputs.

- Title: Handoff versus tool delegation
  Main bucket: `orchestration_roles_and_delegation`
  Likely surface: distinct manager and specialist patterns, with separate
  examples for control transfer and nested delegation.

- Title: Result surface split
  Main bucket: `io_contracts_and_handoffs`
  Likely surface: final output, run items, interruptions, and nested tool
  metadata as different trust surfaces.

## Candidate Diagnostics

- Diagnostic idea: flag an instruction file or example that treats a handoff
  filter as if it chose the destination agent.
- Diagnostic idea: flag a workflow that promises a result surface it does not
  actually emit.

## Keep Out

- OpenAI product branding or SDK-specific names in the eventual Doctrine
  example text.
- Any fallback that collapses manager tools, handoffs, and result inspection
  into one generic "agent loop" concept.
