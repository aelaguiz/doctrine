# Candidate Tests

## `raw/CLAUDE.md`

- Doctrine pressure: root commands, translation requirements, component conventions, shell gotchas, and testing rules.
- Candidate example: a repo root guide that tells agents how to work in a multilingual Next.js project.
- Candidate diagnostic: warn when a change ignores the i18n requirement or skips the documented test commands.

## `raw/docs/README.md`

- Doctrine pressure: docs index, nested topic routing, and documentation standards.
- Candidate example: a docs hub that points agents toward the right playbook before editing behavior-sensitive areas.
- Candidate diagnostic: flag when a doc update fails to add itself to the index or omits a last-updated stamp.

## `raw/docs/i18n/caching-and-locale-detection.md`

- Doctrine pressure: cached locale detection, Next.js dynamic rendering, and the implemented mitigation.
- Candidate example: a root-cause analysis doc that explains why a specific routing behavior was changed.
- Candidate diagnostic: warn when an example claims locale detection is safe without acknowledging cache effects.

## `raw/docs/e2e/testing-patterns.md`

- Doctrine pressure: Playwright selector discipline, ARIA relationships, portal handling, and viewport-specific test behavior.
- Candidate example: a testing playbook that teaches agents how to write stable E2E tests for a real app.
- Candidate diagnostic: detect when an example uses brittle selectors instead of the documented ARIA pattern.

## `raw/docs/decisions/eslint-9-over-biome.md`

- Doctrine pressure: explicit tech decision, rationale, revisit conditions, and references.
- Candidate example: a decision record that preserves why a tool choice was rejected.
- Candidate diagnostic: warn if a future example drops the revisit criteria or the reason the alternative was refused.

## `raw/docs/upgrades/next-16.md`

- Doctrine pressure: upgrade checklist, renamed runtime concepts, lint modernizations, and behavioral changes.
- Candidate example: a migration playbook that records actual file edits and accepted defaults.
- Candidate diagnostic: flag examples that mention the upgrade without the file-level impact or behavior changes.

## Good Doctrine Surfaces

- `scope_hierarchy`
- `commands_and_quality_gates`
- `negative_guardrails`
- `domain_specific_constraints`
- `context_and_memory`
