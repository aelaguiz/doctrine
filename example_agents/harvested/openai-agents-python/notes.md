# Notes

## Source Summary

This source is a production SDK with a strong contributor guide and several
adjacent docs pages that define how an agent is configured, how it hands off,
how it uses tools, and how run results should be read back.

## High-Signal Patterns

- Mandatory verification before marking work complete. The root guide ties
  code changes to explicit verification commands.
- Agent definition as a typed surface. `name`, `instructions`, `tools`,
  `handoffs`, `output_type`, `context`, and dynamic instructions all have
  distinct roles.
- Orchestration split between manager-style tools and peer handoffs. The docs
  keep these as different models instead of one blurry "multi-agent" bucket.
- Handoff payloads versus next-agent history. `input_type`, `input_filter`,
  and nested handoff history are separate concepts.
- Result surfaces are separated by purpose. Final output, new items, raw
  responses, interruptions, and nested agent-as-tool metadata are not treated
  as one generic response blob.
- Guardrails and tool enabling are explicit policy surfaces. The docs keep
  input, output, and tool guardrails separate from ordinary tool calls.

## What This Teaches Doctrine

This source pressures Doctrine to keep command gates, specialization, handoff
truth, and result surfaces explicit. It is especially useful for examples that
need to distinguish:

- user-facing agent configuration from runtime result inspection
- manager-style orchestration from transfer-of-control handoffs
- carrier metadata from the underlying task input
- generic output from structured or typed output
- safety checks that apply only at specific workflow boundaries

