# Candidate Tests

## `raw/AGENTS.md`

- Doctrine pressure: monorepo-wide command gates and dependency propagation across libraries.
- Candidate example: a root instruction file that defines standard format/lint/test commands and a dependency map that determines which libraries are affected by a change.
- Candidate diagnostic: warn when a library-local example ignores the dependency map or the required test commands.

## `raw/CLAUDE.md`

- Doctrine pressure: same repo-wide rules in the alternate CLAUDE format.
- Candidate example: a duplicated root instruction file that should behave like the AGENTS version while preserving the same library hierarchy and command gates.
- Candidate diagnostic: flag format drift when the CLAUDE version of a repo guide diverges from the AGENTS version.

## `raw/libs/prebuilt/README.md`

- Doctrine pressure: concrete agent, tool, validation, and interrupt behavior.
- Candidate example: a markdown doc that defines a ReAct agent, a ToolNode, a ValidationNode, and Agent Inbox requests/responses with code examples.
- Candidate diagnostic: warn when an example collapses agent execution, tool execution, and validation into one undifferentiated step.

## `raw/libs/cli/README.md`

- Doctrine pressure: command-oriented setup for creating, developing, and deploying graphs.
- Candidate example: a CLI README that defines `langgraph new`, `dev`, `up`, `build`, and `dockerfile` with config-file expectations.
- Candidate diagnostic: flag examples that omit the config-file contract or blur local-dev versus Docker deployment modes.

## `raw/README.md`

- Doctrine pressure: the agent-engineering boundary between LangGraph, LangChain, and LangSmith.
- Candidate example: a top-level product overview that explains when to use LangGraph for low-level orchestration and how it pairs with adjacent products.
- Candidate diagnostic: warn when a downstream example treats LangGraph as a high-level app library instead of the lower-level orchestration framework.

## Good Doctrine Surfaces

- `scope_hierarchy`
- `commands_and_quality_gates`
- `io_contracts_and_handoffs`
- `orchestration_roles_and_delegation`
- `negative_guardrails`
