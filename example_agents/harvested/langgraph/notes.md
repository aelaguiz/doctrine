# LangGraph

## Why This Source Matters

This repo is a strong contrast case for Doctrine because it combines monorepo governance with concrete agent orchestration docs. The package-level markdown is closer to behavioral contracts than generic documentation.

## High-Signal Doctrine Pressure

- `scope_hierarchy`: the root AGENTS/CLAUDE pair governs the whole monorepo and points at library dependencies that can inherit changes.
- `commands_and_quality_gates`: the root guide front-loads format, lint, and test commands with a `TEST=...` escape hatch.
- `io_contracts_and_handoffs`: `libs/prebuilt/README.md` shows agent/tool/interrupt flows with structured request and response payloads.
- `orchestration_roles_and_delegation`: the prebuilt docs split `create_react_agent`, `ToolNode`, `ValidationNode`, and Agent Inbox behavior into separate role surfaces.

## What To Pull Into Doctrine

- nested repo-wide vs library-local instruction precedence
- tool-calling and validation node boundaries
- interrupt / human-response flow as a markdown-defined contract
- CLI bootstrap and deployment workflow language
