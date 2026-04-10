# Candidate Tests

## `raw/AGENTS.md`

- Doctrine pressure: repo-wide rule ordering, command gates, stability constraints, and documentation standards.
- Candidate example: a monorepo root instruction file that defines setup, linting, testing, public API stability, and PR expectations.
- Candidate diagnostic: warn when a child example changes an exported interface without the corresponding stability warning.

## `raw/CLAUDE.md`

- Doctrine pressure: same behavioral contract in an alternate agent format.
- Candidate example: a duplicated root instruction file that should render the same core responsibilities but with the CLAUDE-specific format.
- Candidate diagnostic: flag drift between agent formats when the same repo-level policy is expressed inconsistently.

## `raw/README.md`

- Doctrine pressure: high-level boundary between LangChain and LangGraph, plus ecosystem and agent-engineering positioning.
- Candidate example: a top-level README that tells readers when to use LangChain versus LangGraph and frames the agent platform surface.
- Candidate diagnostic: warn when an example overstates LangChain as the orchestration layer instead of the higher-level agent layer.

## Good Doctrine Surfaces

- `scope_hierarchy`
- `commands_and_quality_gates`
- `negative_guardrails`
