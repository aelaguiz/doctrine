# Sentry Monorepo

## Why This Source Matters

This repo is one of the clearest examples of instruction layering across a large monorepo: root guidance, backend-specific rules, test-specific rules, and frontend-specific rules all coexist and change what a contributor should do.

## High-Signal Doctrine Pressure

- `scope_hierarchy`: the root guide routes you to backend, tests, and frontend sub-guides based on file area.
- `commands_and_quality_gates`: the repo defines required dev environment setup, venv usage, pre-commit checks, backend pytest usage, and frontend typecheck/test commands.
- `negative_guardrails`: the backend guide bans unscoped queries and broad exception handling; the tests guide bans direct `Model.objects.create` and branchy tests; the frontend guide bans several component and styling patterns.
- `domain_specific_constraints`: backend, testing, and frontend sections each impose different domain-specific conventions and helper choices.

## What To Pull Into Doctrine

- root-to-child instruction routing
- hard "must" commands tied to repo areas
- security and test-safety guardrails
- area-specific instruction files that act like policy overlays
