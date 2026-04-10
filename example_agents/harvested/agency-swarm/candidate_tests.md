# Candidate Tests

## Source Summary

Harvest from a multi-agent orchestration repo that emphasizes backlog
discipline, explicit role boundaries, and sequential delegation in a financial
research workflow.

## High-Signal Patterns

- Pattern: root governance file with evidence-first change control.
  Doctrine pull: a task instruction example that requires tests, logs, or
  specification evidence before completion.

- Pattern: live backlog discipline and explicit escalation triggers.
  Doctrine pull: a workflow example that tracks blockers and only stops for a
  defined reason.

- Pattern: role precondition before any work begins.
  Doctrine pull: a negative guardrail or route example that blocks action until
  a required opening condition is satisfied.

- Pattern: staged delegation across specialist roles.
  Doctrine pull: a handoff example with ordered turns, clear ownership, and a
  final review before delivery.

- Pattern: role-specific output contracts.
  Doctrine pull: separate examples for analysis, synthesis, and final report
  formatting instead of one combined prompt.

## Candidate Doctrine Examples

- Title: Evidence-first task closeout
  Main bucket: `commands_and_quality_gates`
  Likely surface: require concrete verification before a task can be marked
  complete.

- Title: Role precondition and opening phrase
  Main bucket: `negative_guardrails`
  Likely surface: block work until a named precondition is satisfied.

- Title: Sequential delegation chain
  Main bucket: `orchestration_roles_and_delegation`
  Likely surface: a manager role that delegates in a fixed order and reviews
  each stage.

- Title: Role-specific report synthesis
  Main bucket: `io_contracts_and_handoffs`
  Likely surface: analysis output, risk output, and report output as distinct
  contracts.

## Candidate Diagnostics

- Diagnostic idea: reject a role file that asks an agent to start work before a
  required precondition is met.
- Diagnostic idea: reject a workflow that skips a required review stage before
  handing the result to the user.

## Keep Out

- The name "John Doe" and other upstream story details in Doctrine examples.
- Finance-specific labels that are only useful inside this repo's demo chain.
