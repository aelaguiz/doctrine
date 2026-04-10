# Candidate Tests

## Source Summary

OpenClaw Medical Skills is a dense source of explicit agent behavior: named skills, usage triggers, tool allowlists, hard warnings, staged outputs, and domain-specific validation rules. It is ideal for Doctrine examples that need skill scoping, typed outputs, and fail-loud guardrails.

## High-Signal Patterns

- Pattern: skills declare when to use them and what tools they may use.
  Doctrine pull: skill blocks, allowed-tools surfaces, and explicit capability gating.

- Pattern: workflows often split into stages with waypoint artifacts.
  Doctrine pull: portable currentness, multi-step output contracts, and handoff truth.

- Pattern: FHIR and prior-auth style skills enforce exact validation and decision rules.
  Doctrine pull: enum validation, required fields, output package structure, and diagnostic clarity.

## Candidate Doctrine Examples

- Title: Prior authorization two-stage review
  Main bucket: `io_contracts_and_handoffs`
  Likely surface: a staged workflow with required connectors and a final decision package.
  Why this stays generic: keep the medical terminology as a source of constraints, not as a Doctrine-specific vocabulary leak.

- Title: FHIR resource validation
  Main bucket: `domain_specific_constraints`
  Likely surface: a typed API example with required fields, enum values, and exact error codes.
  Why this stays generic: the Doctrine lesson is about typed validation and failure mode selection.

- Title: Search strategy decomposition
  Main bucket: `skills_tools_and_capabilities`
  Likely surface: parallel source-specific search instructions with fallback and ranking.
  Why this stays generic: the lesson is query decomposition and source routing, not any one data provider.

- Title: Scientific brainstorming phases
  Main bucket: `context_and_memory`
  Likely surface: a conversational agent that moves through understanding, divergence, connection, critique, and synthesis.
  Why this stays generic: this should become a dialogue-shaping example, not a medical-specific one.

## Candidate Diagnostics

- Diagnostic idea: a skill invokes a tool that is not in its allowed-tools list.
  Failure to prove: capability gating must be explicit and fail loud.

- Diagnostic idea: a skill requires a connector or output file that is missing.
  Failure to prove: staged workflows should not silently continue without prerequisites.

- Diagnostic idea: a FHIR-like example uses an invalid enum or wrong required field rule.
  Failure to prove: typed domain constraints should produce precise validation failures.

## Keep Out

- Proprietary medical phrasing that does not generalize beyond the source repo.
- Turning the source into a product-specific knowledge dump instead of a reusable instruction pattern set.
