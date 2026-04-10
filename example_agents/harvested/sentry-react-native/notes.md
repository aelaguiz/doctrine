# Sentry React Native

## Why This Source Matters

This monorepo combines a top-level AGENTS file, a CI workflow doc, and nested package and platform AGENTS files. It is useful for Doctrine because it shows how instructions branch by package, language, native platform, and sample app.

## High-Signal Doctrine Pressure

- `scope_hierarchy`: the root instructions fan out into `packages/core/`, `packages/core/android/`, `packages/core/ios/`, and sample-app scopes.
- `commands_and_quality_gates`: the repo defines build, test, lint, and circular-dependency commands, plus label-based CI gating for expensive jobs.
- `negative_guardrails`: the package files enforce style, typing, formatting, and bridge patterns that should not be violated.
- `context_and_memory`: the root instructions explicitly tell the reader to re-read AGENTS after compaction, and the contributor docs explain how to set up sibling native repos.
- `domain_specific_constraints`: Java/Kotlin, Objective-C/Swift, React Native, Expo, and Metro each have different local expectations.

## What To Pull Into Doctrine

- branchable repo instructions with nested local overrides
- CI gates that depend on labels or workflow context
- platform-specific style constraints under one repo root
- sample-app instructions that differ from core SDK instructions
- explicit re-read / context-refresh behavior
