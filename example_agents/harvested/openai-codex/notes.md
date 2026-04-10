# OpenAI Codex

## Why This Source Matters

This repo combines dense Rust code conventions with a deeper folder-specific instruction file for TUI state machines. It is useful for Doctrine because it shows both behavioral guardrails and narrow local overrides.

## High-Signal Doctrine Pressure

- `commands_and_quality_gates`: the root guide names install, format, lint, test, and lockfile maintenance commands.
- `negative_guardrails`: it forbids touching sandbox env-var code, large modules, ambiguous boolean APIs, and several Rust anti-patterns.
- `scope_hierarchy`: the `codex-rs/tui/src/bottom_pane/AGENTS.md` file adds a local requirement to keep module docs and the narrative docs synchronized.
- `skills_tools_and_capabilities`: the root guide references MCP/tool-call handling and the repo's own helper commands.

## What To Pull Into Doctrine

- precise "do not edit this" rules tied to runtime constraints
- language-specific style conventions that behave like executable guardrails
- child-directory instruction files that add doc-sync obligations for a small subsystem
- command-and-test instructions that differ by project and file area
