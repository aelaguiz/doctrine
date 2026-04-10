# Candidate Tests

## `raw/AGENTS.md`

- Doctrine pressure: root-scoped command gates and nested README reading rules.
- Candidate example: a monorepo root AGENTS file that requires a dev server before source edits, mandates a specific test generator, and defines when to use full build vs fast local loops.
- Candidate diagnostic: warn when a child example ignores a required setup command or omits the README-chain requirement.

## `raw/packages/next/AGENTS.md`

- Doctrine pressure: local override that changes how the package should be interpreted.
- Candidate example: a package-local instruction that says the local docs are the source of truth and not to rely on training data assumptions.
- Candidate diagnostic: flag a scoped instruction that conflicts with the parent guide if the child file is ignored.

## Good Doctrine Surfaces

- `scope_hierarchy`
- `commands_and_quality_gates`
- `negative_guardrails`
