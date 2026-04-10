# Candidate Tests

## `raw/AGENTS.md`

- Doctrine pressure: root guide that delegates to area-specific instruction files and defines repo-wide command gates.
- Candidate example: a large monorepo instruction file that routes agents to backend, tests, or frontend docs depending on the target path.
- Candidate diagnostic: detect when a root guide claims area-specific routing but a lower-level guide is missing from the rendered hierarchy.

## `raw/src/AGENTS.md`

- Doctrine pressure: backend-specific constraints, including scoped query patterns and explicit exception-handling rules.
- Candidate example: a backend instruction file that makes security scoping part of the agent contract rather than a code review suggestion.
- Candidate diagnostic: flag generic instructions that would allow IDOR-prone access patterns or broad exception swallowing.

## `raw/tests/AGENTS.md`

- Doctrine pressure: test placement, procedural test shape, date-stable fixtures, and factory usage.
- Candidate example: a test guide that says where test files belong and forbids branching logic inside tests.
- Candidate diagnostic: reject tests that use `Model.objects.create` directly or freeze current/future-year timestamps at module scope.

## `raw/static/AGENTS.md`

- Doctrine pressure: frontend conventions that prefer core components, typed hooks, lazy routes, and query helpers.
- Candidate example: a frontend guide that turns component and API helper preferences into hard repo rules.
- Candidate diagnostic: flag instruction text that permits new Reflux stores, CSS files, or direct styling when core components are available.

## Good Doctrine Surfaces

- `scope_hierarchy`
- `commands_and_quality_gates`
- `negative_guardrails`
- `domain_specific_constraints`
