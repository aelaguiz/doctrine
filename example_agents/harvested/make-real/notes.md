# Make Real

## Why This Source Matters

This repo is a dense prompt surface: one CLAUDE guide plus several markdown system prompts that vary by model/provider and define the output contract for generated prototypes.

## High-Signal Doctrine Pressure

- `runtime_provider_selection`: the prompt files split behavior by model family and provider constraints, which is useful for tests that need different branches for different runtimes.
- `io_contracts_and_handoffs`: every prompt insists on a single self-contained HTML file and defines how previous HTML should be refactored.
- `negative_guardrails`: red annotations are excluded, external resources are limited, and unsupported assets or illustrative device mockups are ruled out.
- `commands_and_quality_gates`: the repo guide gives the basic build, dev, lint, and prompt-update workflow.
- `context_and_memory`: the prompts treat existing HTML as live context, not just static reference.

## What To Pull Into Doctrine

- strict single-file output contracts
- provider-specific prompt branching and runtime selection
- refactor-from-existing-artifact behavior
- annotation stripping and resource allowlists
