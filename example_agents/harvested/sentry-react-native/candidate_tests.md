# Candidate Tests

## `raw/AGENTS.md`

- Doctrine pressure: repo-wide setup, build, test, lint, commit, and PR conventions.
- Candidate example: a monorepo root instruction file that centralizes setup commands and points to nested AGENTS files for package and sample-specific behavior.
- Candidate diagnostic: flag a repo change that ignores the required build/test checklist or misses the nested instruction scope.

## `raw/CI.md`

- Doctrine pressure: label-driven CI gating for expensive jobs.
- Candidate example: a markdown CI note that explains how the `ready-to-merge` label changes what workflows run.
- Candidate diagnostic: flag a CI-sensitive workflow change that does not account for the label gate.

## `raw/packages/core/AGENTS.md`

- Doctrine pressure: JS/TS style, test discipline, import order, and native bridge patterns.
- Candidate example: a package-local instruction file that gives exact code style, Jest patterns, and recurring error-handling forms.
- Candidate diagnostic: flag code that violates package style or skips the expected Arrange-Act-Assert test structure.

## `raw/packages/core/android/AGENTS.md`

- Doctrine pressure: Java/Kotlin formatting, legacy vs new architecture, and local sentry-java workflow.
- Candidate example: an Android-specific instruction file that distinguishes old and new architecture directories and gives build/publish steps for local native development.
- Candidate diagnostic: flag Android bridge code that ignores the architecture split or the package-local formatting rules.

## `raw/packages/core/ios/AGENTS.md`

- Doctrine pressure: Objective-C/Swift conventions and local sentry-cocoa workflow.
- Candidate example: an iOS-specific instruction file that spells out formatting, nullability, native bridge patterns, and sibling-repo setup.
- Candidate diagnostic: flag iOS changes that do not follow the local pod linkage or Objective-C/Swift style expectations.

## `raw/samples/react-native/AGENTS.md`

- Doctrine pressure: runnable sample app commands, troubleshooting, legacy/new architecture differences, and local native dependency setup.
- Candidate example: a sample-app instruction file that acts like a runbook for Metro, iOS, Android, and native-library integration.
- Candidate diagnostic: flag sample instructions that omit the architecture-specific run steps or troubleshooting hints.

## Good Doctrine Surfaces

- `scope_hierarchy`
- `commands_and_quality_gates`
- `negative_guardrails`
- `context_and_memory`
- `domain_specific_constraints`
