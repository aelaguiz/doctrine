# Vercel Next.js

## Why This Source Matters

This repo shows strong repo-wide instruction hierarchy: a root guide, a package-local override, and concrete rules that change how agents should behave when editing source or tests.

## High-Signal Doctrine Pressure

- `scope_hierarchy`: the root file defines the monorepo rules, while `packages/next/AGENTS.md` adds a local warning that the package is not the same as the agent's training data.
- `commands_and_quality_gates`: the root file front-loads build, test, and bootstrap commands, plus a required dev server for source changes.
- `negative_guardrails`: the repo bans specific shortcuts such as `setTimeout` for waiting, deprecated `check()`, and unsafe module-resolution testing patterns.
- `context_and_memory`: the instructions explicitly require rereading README files along the path before editing a nested target.

## What To Pull Into Doctrine

- layered instruction precedence
- command-first examples with explicit setup and verification gates
- test-writing guardrails that reject older helper APIs
- local override text that narrows or changes the meaning of the root guide
