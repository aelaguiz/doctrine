# Candidate Tests

## Source Summary

TradingAgents is a good source when Doctrine needs to model a debate between specialized agents and a final judge. The important behavior is not the market domain itself, but the way the prompts force explicit roles, shared state, and a concrete final decision contract.

## High-Signal Patterns

- Pattern: bull and bear roles argue from the same evidence but in opposite directions.
  Doctrine pull: role-specific prompts with shared inputs and explicit stance separation.

- Pattern: the manager roles synthesize debate history into a final recommendation.
  Doctrine pull: examples that need current-state vs history separation and a final output artifact.

- Pattern: memory is used to pull past reflections into the current decision.
  Doctrine pull: context-sensitive examples that need portable truth across turns, not just one-shot prompts.

## Candidate Doctrine Examples

- Title: Bull/bear debate pair
  Main bucket: `orchestration_roles_and_delegation`
  Likely surface: two opposing agents reading the same evidence and producing divergent arguments.
  Why this stays generic: keep the finance context abstract so the Doctrine lesson is about debate roles, not markets.

- Title: Research manager synthesis
  Main bucket: `io_contracts_and_handoffs`
  Likely surface: a judge role that consumes prior debate history and emits a decisive plan.
  Why this stays generic: the lesson is the handoff contract and the structured decision, not the trading vocabulary.

- Title: Portfolio manager rating contract
  Main bucket: `domain_specific_constraints`
  Likely surface: a typed enum-like rating plus executive summary and thesis output.
  Why this stays generic: replace trading labels with a generic decision rubric if we turn it into a Doctrine example.

## Candidate Diagnostics

- Diagnostic idea: final judge output must use one of a fixed set of rating values.
  Failure to prove: enum-style decision outputs should fail loud when outside the allowed set.

- Diagnostic idea: a role prompt consumes `current_response` or `history` fields that are never initialized.
  Failure to prove: explicit state dependencies must be declared, not inferred.

## Keep Out

- Financial advice language or market claims that cannot be tied to a concrete agent prompt.
- Replacing the role debate with a generic chat transcript; the value here is the structured multi-role decision flow.
