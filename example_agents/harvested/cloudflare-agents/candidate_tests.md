# Candidate Tests

## `raw/AGENTS.md`

- Doctrine pressure: repo-wide setup, build, check, and test gates plus nested instruction map.
- Candidate example: a root monorepo instruction file that front-loads install/build commands and names the exact nested AGENTS files that override it.
- Candidate diagnostic: flag a change that skips the required setup or ignores a nested AGENTS override.

## `raw/design/AGENTS.md`

- Doctrine pressure: explanation-vs-RFC split, durable design records, and decision snapshots.
- Candidate example: a design folder that distinguishes living design docs from point-in-time RFCs and tells contributors how to move from proposal to implementation.
- Candidate diagnostic: flag a proposal document that is treated like a permanent design doc or a design doc that ignores prior RFCs.

## `raw/docs/AGENTS.md`

- Doctrine pressure: user-facing docs style, Diátaxis separation, MDX gotchas, and upstream sync requirements.
- Candidate example: a docs instruction file that enforces no contractions, relative links, TypeScript examples, and build-safe MDX syntax.
- Candidate diagnostic: flag an MDX page that uses unsupported syntax, relative file links, or the wrong doc type.

## `raw/examples/AGENTS.md`

- Doctrine pressure: full-stack example shape, Kumo UI requirements, and example-specific run scripts.
- Candidate example: a self-contained demo app instruction file that requires frontend/backend structure, Cloudflare Vite plugins, and a required explanatory UI pattern.
- Candidate diagnostic: flag an example that lacks the required full-stack scaffolding or uses non-standard UI conventions.

## `raw/guides/AGENTS.md`

- Doctrine pressure: tutorial-vs-example distinction and narrative README expectations.
- Candidate example: a guide instruction file that explicitly says the README is the tutorial and that code supports the walkthrough.
- Candidate diagnostic: flag a guide that reads like a terse example or omits the architecture walkthrough.

## `raw/packages/agents/AGENTS.md`

- Doctrine pressure: public API boundaries, build entry points, tests per subsystem, and no broad edits to `src/index.ts`.
- Candidate example: a package-local instruction file that defines exports, build scripts, test suites, and boundary rules for the core SDK.
- Candidate diagnostic: flag a public export or package change that forgets the matching build entry or changeset expectation.

## Good Doctrine Surfaces

- `scope_hierarchy`
- `commands_and_quality_gates`
- `negative_guardrails`
- `skills_tools_and_capabilities`
- `context_and_memory`
- `domain_specific_constraints`
