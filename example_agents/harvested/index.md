# Harvested Example Index

This index is the current curated source bank under `example_agents/harvested/`.

Each package was pulled from a temp clone, reduced to a small set of
high-signal upstream artifacts, then rewritten into Doctrine-facing notes and
candidate tests. These are curated slices, not full repo mirrors.

For the markdown-native subset specifically, see
`../markdown_agents.md`.

## Current Set

| Source | Family | Strongest doctrine pressure | Package |
| --- | --- | --- | --- |
| `vercel-nextjs` | codebase AGENTS | root vs child instruction scope, command gates, anti-pattern guardrails | `harvested/vercel-nextjs/` |
| `openai-codex` | codebase AGENTS | hard repo limits, nested local overrides, sandbox-aware exclusions | `harvested/openai-codex/` |
| `sentry-monorepo` | codebase AGENTS | root/backend/tests/frontend split, scoped security and test rules | `harvested/sentry-monorepo/` |
| `openai-agents-python` | SDK docs + AGENTS | typed agents, tools, handoffs, and result surfaces | `harvested/openai-agents-python/` |
| `sentry-mcp` | MCP server docs + AGENTS | tool-budget governance, safe tool metadata, security constraints | `harvested/sentry-mcp/` |
| `agency-swarm` | orchestration repo | role preconditions, staged delegation, review-before-forwarding | `harvested/agency-swarm/` |
| `crewai-examples` | orchestration configs | explicit role/task split and branch-local output commitments | `harvested/crewai-examples/` |
| `seclab-taskflow-agent` | staged taskflow system | reusable taskflows, blocked tools, evidence-only review | `harvested/seclab-taskflow-agent/` |
| `patrickjs-awesome-cursorrules` | rule catalog | scoped child rules, `alwaysApply`, path-limited quality gates | `harvested/patrickjs-awesome-cursorrules/` |
| `cursor-memory-bank` | memory workflow | phase ladders, single source of truth, selective rule loading | `harvested/cursor-memory-bank/` |
| `cursor-security-rules` | security rule pack | hard negative guardrails, taint flow, approval gates | `harvested/cursor-security-rules/` |
| `tradingagents` | domain agent system | debate roles, shared evidence, final judge output | `harvested/tradingagents/` |
| `openclaw-medical-skills` | skill library | skill-scoped tools, required connectors, typed output packages | `harvested/openclaw-medical-skills/` |
| `system-prompts-and-models` | prompt archive | tool schemas, mode routers, read-only planning branches | `harvested/system-prompts-and-models/` |
| `claude-code-system-prompts` | prompt archive | split prompts, verification specialists, explicit security policy | `harvested/claude-code-system-prompts/` |
| `awesome-agent-skills` | skill catalog | skill metadata quality, packaging, catalog vs body split | `harvested/awesome-agent-skills/` |
| `cloudflare-agents` | codebase AGENTS | deep AGENTS hierarchy across design, docs, examples, guides, and packages | `harvested/cloudflare-agents/` |
| `cloudflare-docs` | docs AGENTS + MDX | markdown authoring law, MDX safety, AI-tooling rules, and review patterns | `harvested/cloudflare-docs/` |
| `sentry-react-native` | codebase AGENTS | repo, platform, and sample-app markdown overrides with CI guidance | `harvested/sentry-react-native/` |
| `claude-code-action` | CLAUDE-driven action | markdown action contract with auth, prompt prep, and JSON outputs | `harvested/claude-code-action/` |
| `langchain` | AGENTS + CLAUDE monorepo | stable public-interface law, repo command gates, and markdown repo contract | `harvested/langchain/` |
| `langgraph` | AGENTS + CLAUDE monorepo | markdown orchestration contract plus sublibrary behavior docs | `harvested/langgraph/` |
| `livekit-agents-js` | CLAUDE + package READMEs | plugin capability docs, session vocabulary, and contribution gates | `harvested/livekit-agents-js/` |
| `make-real` | CLAUDE + prompt family | single-HTML output contract and provider-specific markdown prompts | `harvested/make-real/` |
| `rockylinux-org` | CLAUDE + playbooks | large-site repo guidance with i18n, E2E, and upgrade markdown playbooks | `harvested/rockylinux-org/` |
| `vercel-agent-browser` | AGENTS + SKILL docs | browser automation skill contract with auth/session references | `harvested/vercel-agent-browser/` |
| `vercel-agent-skills` | AGENTS + SKILL docs | nested skill packaging and markdown-defined frontend behavior | `harvested/vercel-agent-skills/` |
| `ai-legal-claude` | skill + markdown subagents | clause/risk/compliance role split in markdown-native agent files | `harvested/ai-legal-claude/` |

## Pressure Map

- `scope_hierarchy`: `vercel-nextjs`, `openai-codex`, `sentry-monorepo`, `patrickjs-awesome-cursorrules`, `seclab-taskflow-agent`, `cloudflare-agents`, `sentry-react-native`, `langchain`, `langgraph`
- `commands_and_quality_gates`: `vercel-nextjs`, `openai-codex`, `sentry-monorepo`, `openai-agents-python`, `sentry-mcp`, `cloudflare-agents`, `sentry-react-native`, `claude-code-action`, `langchain`, `livekit-agents-js`, `rockylinux-org`
- `negative_guardrails`: `openai-codex`, `sentry-monorepo`, `cursor-security-rules`, `seclab-taskflow-agent`, `system-prompts-and-models`, `cloudflare-docs`, `claude-code-action`, `langchain`, `make-real`, `vercel-agent-browser`
- `io_contracts_and_handoffs`: `openai-agents-python`, `agency-swarm`, `crewai-examples`, `tradingagents`, `openclaw-medical-skills`, `claude-code-action`, `langgraph`, `livekit-agents-js`, `make-real`, `vercel-agent-browser`, `ai-legal-claude`
- `skills_tools_and_capabilities`: `openai-agents-python`, `sentry-mcp`, `openclaw-medical-skills`, `awesome-agent-skills`, `cloudflare-agents`, `vercel-agent-browser`, `vercel-agent-skills`
- `context_and_memory`: `cursor-memory-bank`, `claude-code-system-prompts`, `tradingagents`, `agency-swarm`, `cloudflare-agents`, `rockylinux-org`
- `orchestration_roles_and_delegation`: `agency-swarm`, `crewai-examples`, `seclab-taskflow-agent`, `tradingagents`, `claude-code-system-prompts`, `claude-code-action`, `langgraph`, `ai-legal-claude`
- `domain_specific_constraints`: `sentry-monorepo`, `sentry-mcp`, `cursor-security-rules`, `openclaw-medical-skills`, `tradingagents`, `cloudflare-docs`, `sentry-react-native`, `rockylinux-org`, `vercel-agent-skills`, `ai-legal-claude`

## How To Pull From This Bank

1. Start from `notes.md` to understand the source in Doctrine terms.
2. Use `candidate_tests.md` to choose whether the next Doctrine artifact should
   be a numbered example, a diagnostic, or a design-note pressure case.
3. Read only the corresponding files under `raw/` when the exact upstream text
   matters.
