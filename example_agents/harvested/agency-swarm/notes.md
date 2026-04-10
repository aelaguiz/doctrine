# Notes

## Source Summary

This source combines a very strict root AGENTS file with role-specific
instruction files for a financial research workflow. The root file is about
execution discipline, while the role files show how a multi-agent chain can be
made explicit and auditable.

## High-Signal Patterns

- Evidence-first workflow. The root guide ties changes to tests, logs, or
  clear specification and asks for a reason when evidence is missing.
- Live backlog and prioritization discipline. New requests, blockers, and
  dependencies are meant to be tracked and reprioritized explicitly.
- Explicit escalation triggers. The guide defines when to stop and ask versus
  when to proceed autonomously.
- Role preconditions matter. The portfolio manager file requires a specific
  opening phrase before any task begins.
- Delegation is staged. Market data first, risk analysis second, report
  generation third, final review last.
- Each role has a narrow output contract. Research, risk scoring, and report
  formatting are separated instead of merged into one generic analyst prompt.

## What This Teaches Doctrine

This source is especially useful for Doctrine examples about:

- explicit step ordering and stop conditions
- role-specific preconditions and guardrails
- handoff chains that preserve accountability
- review checkpoints between delegated stages
- plan/backlog semantics that stay visible to the user

