# Candidate Tests

## `raw/AGENTS.md`

- Doctrine pressure: repo-level docs workflow, build gates, MDX safety, and component-import rules.
- Candidate example: a root docs-repo instruction file that tells agents how to validate markdown, keep links relative, and avoid MDX syntax traps.
- Candidate diagnostic: flag a docs edit that violates the MDX escaping rules or skips the required validation path.

## `raw/src/content/docs/style-guide/index.mdx`

- Doctrine pressure: style-guide scope and navigation structure.
- Candidate example: a style-guide overview page that defines where the writing law lives and how the rest of the guide is organized.
- Candidate diagnostic: flag an internal docs page that points readers to style guide material without establishing the style-guide hierarchy.

## `raw/src/content/docs/style-guide/ai-tooling.mdx`

- Doctrine pressure: Markdown for Agents, MCP server guidance, and AI tool setup.
- Candidate example: a docs page that teaches users how to consume docs as markdown, connect to an MCP server, and wire AI tools through scripts.
- Candidate diagnostic: flag a page that claims AI support without giving the real tool/setup instructions.

## `raw/src/content/docs/style-guide/documentation-content-strategy/writing-guidelines.mdx`

- Doctrine pressure: plain language, active voice, internationalization, and accessibility rules.
- Candidate example: a style page that defines tone, sentence shape, jargon limits, and accessibility expectations.
- Candidate diagnostic: flag writing that uses contractions, passive voice, unexplained jargon, or inaccessible phrasing.

## `raw/src/content/docs/style-guide/formatting/code-block-guidelines.mdx`

- Doctrine pressure: fenced code syntax, output blocks, language selection, and command formatting.
- Candidate example: a formatting guide that distinguishes command blocks, JSON, output annotations, and playground blocks.
- Candidate diagnostic: flag a code block that omits the language, uses unsupported syntax, or prefixes terminal commands with `$`.

## `raw/src/content/docs/style-guide/how-we-docs/reviews.mdx`

- Doctrine pressure: review triage, preview builds, codeowners, and no-response automation.
- Candidate example: a docs workflow page that describes how pull requests are labeled, reviewed, previewed, and closed when blocked.
- Candidate diagnostic: flag a change review flow that omits preview verification or codeowner routing.

## Good Doctrine Surfaces

- `scope_hierarchy`
- `commands_and_quality_gates`
- `negative_guardrails`
- `skills_tools_and_capabilities`
- `context_and_memory`
- `domain_specific_constraints`
