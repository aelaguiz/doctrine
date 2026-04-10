# Candidate Tests

## Source Summary

CrewAI examples are useful when we want a small, readable agent/task pair with explicit inputs and a concrete output contract. The repo is strongest when the task can be described in one prompt and the result can be summarized in a single artifact.

## High-Signal Patterns

- Pattern: `role`, `goal`, and `backstory` are separated from the task itself.
  Doctrine pull: examples that keep instruction layers separate instead of mixing role intent into every turn.

- Pattern: `expected_output` gives a concrete downstream contract.
  Doctrine pull: examples that teach `output` and `trust_surface` as typed, reviewable commitments.

- Pattern: a task can branch on a binary condition such as proceed vs reject.
  Doctrine pull: examples that need explicit branch-local truth and a non-magical handoff.

## Candidate Doctrine Examples

- Title: Meeting transcript to issue list
  Main bucket: `orchestration_roles_and_delegation`
  Likely surface: agent/task pairing with a narrow input and a JSON-shaped output contract.
  Why this stays generic: replace Trello-specific wording with a generic issue tracker output.

- Title: Candidate follow-up email branch
  Main bucket: `io_contracts_and_handoffs`
  Likely surface: branch-local output with a proceed/reject split and explicit output text.
  Why this stays generic: keep the candidate email logic but remove any company-specific hiring framing.

- Title: Flow-scoped crew config
  Main bucket: `scope_hierarchy`
  Likely surface: a doc example about nested config files and where one instruction layer ends and another begins.
  Why this stays generic: do not import CrewAI terminology into Doctrine beyond the generic idea of scoped overrides.

## Candidate Diagnostics

- Diagnostic idea: a task references an input placeholder that is never declared.
  Failure to prove: fail loud on undeclared template variables instead of silently treating them as empty.

- Diagnostic idea: a branch promises two possible outputs but only one output artifact is declared.
  Failure to prove: the current output contract should not be magical or implicit.

## Keep Out

- Trello, HR, and other repo-specific vocabulary unless the candidate test is explicitly about that domain.
- Any assumption that one role file can stand in for a framework-wide output contract.
