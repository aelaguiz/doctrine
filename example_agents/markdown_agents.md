# Complex Markdown Agents

This is the markdown-native slice of the bank: sources where the agent contract
itself is primarily authored in markdown, such as `AGENTS.md`, `CLAUDE.md`,
`SKILL.md`, `instructions.md`, or a tightly related markdown prompt family.

Use this file when the goal is to pressure Doctrine with real markdown-based
agent behavior rather than config-first systems.

## Strongest Markdown-Native Sources

| Source | Why it matters | Strongest files |
| --- | --- | --- |
| `cloudflare-agents` | Deep AGENTS hierarchy with root, design, docs, examples, guides, and package-local overrides | `raw/AGENTS.md`, `raw/examples/AGENTS.md`, `raw/packages/agents/AGENTS.md` |
| `sentry-react-native` | Repo, package, platform, and sample-app markdown overrides plus CI playbook | `raw/AGENTS.md`, `raw/CI.md`, `raw/packages/core/android/AGENTS.md`, `raw/packages/core/ios/AGENTS.md` |
| `langchain` | Monorepo markdown contract with stable-public-interface rules and hard repo gates | `raw/AGENTS.md`, `raw/CLAUDE.md` |
| `langgraph` | Repo-wide markdown contract plus sublibrary READMEs that describe agents, interrupts, and deployment behavior | `raw/AGENTS.md`, `raw/CLAUDE.md`, `raw/libs/prebuilt/README.md`, `raw/libs/cli/README.md` |
| `claude-code-action` | CLAUDE-driven action contract with auth flow, prompt prep, inputs, and JSON result semantics | `raw/base-action/CLAUDE.md`, `raw/base-action/README.md`, `raw/CLAUDE.md` |
| `livekit-agents-js` | CLAUDE plus nested package READMEs covering plugin capability and session vocabulary | `raw/CLAUDE.md`, `raw/CONTRIBUTING.md`, `raw/agents/README.md` |
| `make-real` | Markdown system prompts that explicitly define output shape, provider differences, and scratchpad behavior | `raw/prompts/google-system-prompt.md`, `raw/prompts/anthropic-system-prompt.md`, `raw/prompts/original.md` |
| `rockylinux-org` | CLAUDE plus repo playbooks for i18n, E2E testing, lint policy, and upgrades | `raw/CLAUDE.md`, `raw/docs/i18n/caching-and-locale-detection.md`, `raw/docs/e2e/testing-patterns.md` |
| `vercel-agent-browser` | SKILL-first browser automation contract with command/reference markdown for auth and sessions | `raw/skills/agent-browser/SKILL.md`, `raw/skills/agent-browser/references/authentication.md`, `raw/skills/agent-browser/references/commands.md` |
| `vercel-agent-skills` | Complex markdown skill packaging with nested AGENTS and multiple SKILL bodies | `raw/skills/react-native-skills/AGENTS.md`, `raw/skills/react-native-skills/SKILL.md`, `raw/skills/react-view-transitions/SKILL.md` |
| `ai-legal-claude` | Orchestrator skill plus role-specific markdown subagents for clause/risk/compliance split | `raw/skills/legal-review/SKILL.md`, `raw/agents/legal-risks.md`, `raw/agents/legal-compliance.md` |
| `cloudflare-docs` | AGENTS plus MDX style-guide markdown that encodes authoring law and review behavior | `raw/AGENTS.md`, `raw/src/content/docs/style-guide/ai-tooling.mdx`, `raw/src/content/docs/style-guide/how-we-docs/reviews.mdx` |

## Best Pressure By Markdown Pattern

- Hierarchical repo markdown: `cloudflare-agents`, `sentry-react-native`, `langchain`, `langgraph`
- CLAUDE-driven runtime behavior: `claude-code-action`, `livekit-agents-js`, `rockylinux-org`
- Prompt-family markdown contracts: `make-real`, `claude-code-system-prompts`, `system-prompts-and-models`
- Skill-package markdown: `vercel-agent-browser`, `vercel-agent-skills`, `openclaw-medical-skills`, `awesome-agent-skills`
- Multi-role markdown subagents: `ai-legal-claude`, `agency-swarm`
- Docs-law markdown: `cloudflare-docs`

## Pull Order

If you want the highest-signal markdown agents first, start here:

1. `cloudflare-agents`
2. `sentry-react-native`
3. `langgraph`
4. `claude-code-action`
5. `vercel-agent-browser`
6. `ai-legal-claude`
