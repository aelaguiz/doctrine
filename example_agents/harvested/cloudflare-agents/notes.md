# Cloudflare Agents SDK

## Why This Source Matters

This monorepo has one of the clearest markdown instruction hierarchies in the bank: a repo root guide, nested scope-specific AGENTS files, and separate docs, examples, guides, and package-local rules. It is useful for Doctrine because it shows how local instructions narrow or override parent scope without becoming a new language.

## High-Signal Doctrine Pressure

- `scope_hierarchy`: root instructions fan out into `design/`, `docs/`, `examples/`, `guides/`, and `packages/agents/`, each with distinct behavior.
- `commands_and_quality_gates`: the root file front-loads install, build, test, typecheck, and example-run commands.
- `negative_guardrails`: the repo bans `any`, native/FFI dependencies, CommonJS, and unescaped secrets, while the docs layer adds MDX and style-guide guardrails.
- `skills_tools_and_capabilities`: the package-local AGENTS file defines public exports, build entries, tests, MCP, workflows, scheduling, and client hooks.
- `context_and_memory`: nested files repeatedly tell the reader where to look next, including README and deeper AGENTS files.
- `domain_specific_constraints`: docs, examples, guides, and package internals each have different output shapes and different rules for what counts as correct work.

## What To Pull Into Doctrine

- layered instruction precedence
- repo-wide gates that appear before local exceptions
- explicit anti-patterns that fail loudly
- scope-specific behavior changes that depend on the folder being edited
- package-boundary instructions that define public API and build consequences
