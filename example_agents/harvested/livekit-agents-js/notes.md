# LiveKit Agents JS

## Why This Source Matters

This repo combines a top-level CLAUDE guide, contribution rules, and nested package READMEs that define how agent/session, plugin, and provider workflows are supposed to behave.

## High-Signal Doctrine Pressure

- `scope_hierarchy`: the root guide and nested package READMEs establish what should be read before touching core framework or plugin code.
- `commands_and_quality_gates`: build, lint, API, and test commands are front-loaded, and contribution guidance says when to run formatting and docs steps.
- `negative_guardrails`: contribution rules warn against missing SPDX headers, skipping docs, or relying on outdated release habits.
- `orchestration_roles_and_delegation`: the root README and CLAUDE surface `Agent`, `AgentSession`, and `handoff()` as first-class framework concepts.
- `io_contracts_and_handoffs`: the framework descriptions spell out session lifecycle, speech handling, tool calls, and provider routing boundaries.

## What To Pull Into Doctrine

- root-vs-package-local instruction precedence
- command-first setup and verification gates
- plugin/provider capability tables as a source of branch-specific behavior
- explicit handoff/session vocabulary for multi-agent workflows
