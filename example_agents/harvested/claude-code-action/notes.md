# Claude Code Action

## Why This Source Matters

This repo mixes a top-level GitHub Action guide with a lower-level base action contract. The split gives us a clean example of role boundaries, mode detection, prompt preparation, and action outputs all expressed in markdown.

## High-Signal Doctrine Pressure

- `scope_hierarchy`: the root `CLAUDE.md` governs the whole repo, while `base-action/CLAUDE.md` and `base-action/README.md` describe the embedded standalone action surface.
- `commands_and_quality_gates`: the docs front-load the exact Bun commands for test, typecheck, format, and local action testing.
- `io_contracts_and_handoffs`: the base action README spells out inputs, outputs, environment variables, and settings in a table-first format that is directly harvestable.
- `orchestration_roles_and_delegation`: the root docs describe automatic mode detection, prompt preparation, cleanup, and provider selection across GitHub workflows.
- `negative_guardrails`: the docs call out required inputs, debug-output security, and provider-specific authentication constraints.

## What To Pull Into Doctrine

- mode-aware behavior with explicit trigger conditions
- root-vs-sub-action layering
- input/output tables and provider-specific constraint handling
- command-first setup and verification gates
