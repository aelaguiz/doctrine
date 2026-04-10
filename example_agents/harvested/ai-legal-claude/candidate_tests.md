# Candidate Tests

## Source Summary

Harvest from a legal-analysis repo with a markdown orchestrator and five
specialist agent roles for contract review.

## High-Signal Patterns

- Pattern: flagship orchestrator that launches parallel specialist agents.
  Doctrine pull: a multi-agent workflow with an explicit aggregation step and
  a unified report output.

- Pattern: role split across clause extraction, risk, compliance, terms, and
  recommendations.
  Doctrine pull: separate examples that each prove a different stage in the
  analysis chain.

- Pattern: strict report templates and disclaimer behavior.
  Doctrine pull: an output contract that requires fixed ordering, labels, and
  legal caveats.

- Pattern: obligation mapping and negotiation language generation.
  Doctrine pull: examples that transform analysis into actionable redlines and
  calendar-style obligations.

## Candidate Doctrine Examples

- Title: Parallel contract review orchestrator
  Main bucket: `orchestration_roles_and_delegation`
  Likely surface: one skill launches multiple focused subagents and combines
  their outputs.

- Title: Clause inventory stage
  Main bucket: `io_contracts_and_handoffs`
  Likely surface: clause extraction with a structured inventory handoff.

- Title: Risk and compliance split
  Main bucket: `domain_specific_constraints`
  Likely surface: distinct risk and compliance roles with different outputs.

- Title: Obligation and recommendation stages
  Main bucket: `skills_tools_and_capabilities`
  Likely surface: timeline mapping plus negotiable replacement language.

## Candidate Diagnostics

- Diagnostic idea: reject a review flow that collapses all specialist roles into
  one generic legal analyzer.
- Diagnostic idea: reject an output that omits the required disclaimer or the
  fixed report structure.

## Keep Out

- Real legal advice claims, product marketing text, or jurisdiction-specific
  promises in the eventual Doctrine example text.
- Any fallback that turns the specialist chain into a single do-everything
  legal prompt.
