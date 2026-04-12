# External Agent Patterns And Doctrine Support Analysis

This is a dated analysis document, not shipped language truth.

It is intentionally self-contained.

All evidence required to understand the gaps is quoted inline in this file.
Source markers are plain-text provenance identifiers only; they are not needed
to follow the analysis.

Its job is:

- ramp up on the planned Doctrine feature wave in `docs/`
- normalize the patterns visible in the harvested external-agent bank under
  `example_agents/harvested/`
- decide which patterns Doctrine already supports, which ones fit the planned
  wave, which ones look like later candidates, and which ones should stay out
  of Doctrine core

## Scope And Method

I used four parallel analysis passes over the harvested bank, split by repo
family:

- codebase instruction hierarchies and repo guardrails
- skills, tools, MCP/browser capability packaging, and action-style I/O
- orchestration, delegation, memory, and evidence-routing sources
- prompt archives, safety policy, mode routing, and scoped rule packs

The analysis is grounded in the curated Doctrine-facing summaries already
checked into the repo:

- `example_agents/harvested/*/notes.md`
- `example_agents/harvested/*/candidate_tests.md`
- `example_agents/harvested/index.md`
- `example_agents/markdown_agents.md`

Representative evidence clusters used repeatedly:

- instruction hierarchy and repo law:
  `cloudflare-agents`, `vercel-nextjs`, `openai-codex`, `sentry-monorepo`,
  `sentry-react-native`, `langchain`, `langgraph`, `cloudflare-docs`,
  `rockylinux-org`
- capabilities, tools, and result surfaces:
  `openai-agents-python`, `sentry-mcp`, `openclaw-medical-skills`,
  `vercel-agent-browser`, `vercel-agent-skills`, `claude-code-action`,
  `livekit-agents-js`
- orchestration and memory:
  `agency-swarm`, `crewai-examples`, `cursor-memory-bank`,
  `seclab-taskflow-agent`, `tradingagents`, `ai-legal-claude`
- prompt archives and scoped rule packs:
  `system-prompts-and-models`, `claude-code-system-prompts`, `make-real`,
  `cursor-security-rules`, `patrickjs-awesome-cursorrules`

## Doctrine Ramp-Up

### Shipped Doctrine Today

The current shipped language already has strong structural support for:

- reusable `workflow`, `review`, `skill`, `input`, `output`, and `enum`
  declarations
- inheritance and explicit patching
- typed inputs and outputs, including custom sources and targets
- `workflow law` for:
  `active when`, `mode`, `match`, `current artifact`, `current none`,
  preservation, invalidation, `support_only`, `ignore`, `stop`, and `route`
- `review` for:
  typed verdict logic, contract gates, block/reject/accept order, currentness,
  trusted carriers, and next-owner routing
- `trust_surface` and guarded output sections as the portable downstream truth
  boundary
- bound input/output roots for workflow law and review carriers

The strongest current examples live in:

- `examples/07` through `29` for skills, inputs, outputs, reusable blocks, and
  enums
- `examples/30` through `42` for workflow law, currentness, preservation,
  invalidation, and route-only turns
- `examples/43` through `53` for first-class review and bound carrier roots

### Planned Feature Wave In The Docs

The live planned-wave docs are converging on three main additions:

- `analysis`
  This is the planned home for repeated reasoning choreography and ordered
  decision programs.
- `schema`
  This is the planned home for artifact inventories and later gate catalogs.
- `document`
  This is the planned readable-markdown layer with semantic block kinds such as
  `section`, `sequence`, `bullets`, `checklist`, `definitions`, `table`,
  `callout`, `code`, and `rule`.

The key planning docs are:

- `ANALYSIS_AND_SCHEMA_SPEC.md`
- `READABLE_MARKDOWN_SPEC.md`
- `INTEGRATION_SURFACES_SPEC.md`
- `LANGUAGE_MECHANICS_SPEC.md`
- `SECOND_WAVE_LANGUAGE_NOTES.md`

### Explicit Narrowing And Non-Goals

The planned docs are also unusually clear about what Doctrine should not do.

The main narrowed positions are:

- do not add `route_only` as a new declaration kind
- do not add `review_family` as a new declaration kind
- keep workflow law and review on their existing shipped surfaces
- keep domain truth, domain enums, and repo-specific behavior in domain packs
  or authored prose
- defer richer render-control ideas like `render_profile`, `properties`, and
  typed row/item schemas unless the core wave lands cleanly first

That boundary matters because the external bank contains many attractive ideas
that are valuable as examples, diagnostics, or renderable artifacts but do not
justify new core primitives yet.

## Status Legend

- `Shipped`: Doctrine already has a strong structural surface for this.
- `Example Gap`: the language mostly fits today, but the corpus/docs do not
  teach it directly yet.
- `Planned`: the next-wave docs already point at a real home for it.
- `Future Candidate`: this is a genuine gap not covered cleanly by shipped or
  planned surfaces.
- `Keep Out`: useful pressure, but it should stay repo-local prose, packaging,
  tooling, or domain-specific law.

## Exhaustive Pattern Inventory

### Governance, Scope, And Repo Law

| Pattern | External Evidence | Doctrine Status | Support Shape To Consider |
| --- | --- | --- | --- |
| Root contract plus child overrides by path | `cloudflare-agents`, `vercel-nextjs`, `openai-codex`, `sentry-monorepo`, `sentry-react-native`, `langchain`, `langgraph`, `rockylinux-org` | `Example Gap` | Teach layered scope and precedence with examples and diagnostics. Avoid hard-coding filesystem semantics into core grammar for now. |
| Non-AGENTS docs acting as instruction law | `cloudflare-docs`, `rockylinux-org`, `sentry-react-native`, `claude-code-action` | `Planned` | `document` plus readable blocks can model style guides, CI notes, review runbooks, and upgrade playbooks without pretending they are new runtime primitives. |
| Command-first setup, build, lint, and test gates | almost every codebase repo in the bank | `Example Gap` | Add examples and rendered checklists for exact required commands. This is mostly prose today; `document.checklist` would improve it. |
| Area-specific verification gates | `sentry-monorepo`, `sentry-react-native`, `cloudflare-docs`, `claude-code-action` | `Example Gap` | Show per-scope verification requirements and fail-loud closeout expectations. Keep CI labels and repo-specific workflow names out of core. |
| Repo tells the agent what to read next | `cloudflare-agents`, `vercel-nextjs`, `cloudflare-docs`, `rockylinux-org`, `sentry-react-native` | `Shipped` | This is already expressible as workflow prose and typed inputs. The main gap is better examples for context-loading discipline. |
| Public API stability as repo law | `langchain`, `cloudflare-agents`, `openai-codex` | `Example Gap` | Use workflow law or review examples that preserve public surfaces and reject accidental interface drift. |
| Doc-sync obligations for narrow subsystems | `openai-codex`, `cloudflare-agents`, `langgraph` | `Example Gap` | Model as output/readback obligations and preservation rules, not as a new declaration kind. |
| Duplicate contract publication across formats | `langchain`, `langgraph`, `claude-code-action` | `Future Candidate` | Likely tooling or drift-check support, not core grammar. The language can already express one truth; parity checking is a separate layer. |
| Generated instruction artifacts as published truth | `vercel-agent-skills`, `awesome-agent-skills` | `Future Candidate` | Support via schema/document examples and tooling provenance later. Do not make “generated AGENTS” a core primitive. |

### Capabilities, Skills, And Tooling

| Pattern | External Evidence | Doctrine Status | Support Shape To Consider |
| --- | --- | --- | --- |
| Named reusable skills/capabilities | `openclaw-medical-skills`, `vercel-agent-skills`, `vercel-agent-browser`, `openai-agents-python` | `Shipped` | Doctrine already has `skill` and `skills` blocks. The main opportunity is deeper examples. |
| Skill usage triggers and “use when / not for this role” guidance | `openclaw-medical-skills`, `vercel-agent-skills`, `example 21` pressure from harvested bank | `Example Gap` | Expand the skills ladder with usage-trigger, prohibition, and discovery examples. |
| Skill discovery before guessing | `example_agents/harvested/openclaw-medical-skills`, `example_agents/harvested/awesome-agent-skills` | `Shipped` | Already expressible with skills relationships and prose. No new primitive needed. |
| Allowed-tools and blocked-tools lists | `openclaw-medical-skills`, `seclab-taskflow-agent`, `system-prompts-and-models` | `Future Candidate` | Doctrine currently models skills, not concrete tool grants. This is a real candidate for a later capability surface. |
| Tool safety metadata like read-only, destructive, hidden, idempotent | `sentry-mcp`, `openai-agents-python`, `system-prompts-and-models` | `Future Candidate` | Strong candidate after the current planned wave. This pressure is consistent across multiple harvested sources. |
| Numeric tool or capability budgets | `sentry-mcp` | `Future Candidate` | Likely a later capability-governance feature or diagnostic surface. Not covered by current docs. |
| Required connectors, auth, env, or session prerequisites | `openclaw-medical-skills`, `vercel-agent-browser`, `claude-code-action` | `Example Gap` | Inputs and env vars already exist. Add examples for required connectors/session prerequisites before inventing a new core surface. |
| Provider/plugin/browser capability matrices | `livekit-agents-js`, `make-real`, `vercel-agent-skills` | `Planned` | `schema` and `document` are a good fit for capability tables and compatibility/readback artifacts. |
| Skill catalogs and registry metadata separate from skill bodies | `awesome-agent-skills`, `vercel-agent-skills` | `Planned` | This looks more like `schema` plus `document` than like a new executable declaration family. |

### Inputs, Outputs, Carriers, And Memory

| Pattern | External Evidence | Doctrine Status | Support Shape To Consider |
| --- | --- | --- | --- |
| Typed input sources and output targets | `openai-agents-python`, `claude-code-action`, `vercel-agent-browser`, shipped `examples/08` and `09` | `Shipped` | Doctrine already models this cleanly. |
| Fixed-order output templates and strong readback contracts | `ai-legal-claude`, `claude-code-action`, `make-real`, `sentry-mcp` | `Planned` | `document` is the obvious next home for this. Today it is mostly output prose. |
| Structured data namespace catalogs | `sentry-mcp`, `cloudflare-docs` | `Planned` | Strong fit for `schema` and readable document output. |
| Single-file artifact contracts | `make-real`, `claude-code-action`, `examples/09` | `Shipped` | Already supported with `output`, `target`, `shape`, and files mode. |
| Final output split from waypoint artifacts | `openclaw-medical-skills`, `agency-swarm`, `ai-legal-claude` | `Example Gap` | Doctrine outputs can already model multiple artifacts, but the corpus needs more staged-output examples. |
| Final output split from runtime metadata, interruptions, raw responses, and run items | `openai-agents-python` | `Future Candidate` | Doctrine does not yet have a first-class runtime result surface split beyond outputs and trusted carriers. |
| Handoff payload distinct from next-owner history | `openai-agents-python`, `agency-swarm` | `Future Candidate` | Current routes and carriers cover next-owner truth, but not history filtering or handoff-packet semantics as distinct runtime objects. |
| Session, auth, and profile carriers | `vercel-agent-browser`, `claude-code-action`, `livekit-agents-js` | `Example Gap` | Model with current inputs/outputs/trust surfaces first. Only promote later if repeated examples become awkward. |
| Shared state artifact or memory-bank file | `cursor-memory-bank`, `agency-swarm`, `seclab-taskflow-agent` | `Shipped` | Doctrine already supports current artifacts, trusted carriers, support-only evidence, and single-source-of-truth discipline. |
| Single authoritative artifact with secondary references demoted | `cursor-memory-bank`, `sentry-mcp`, shipped workflow-law examples | `Shipped` | This is already core Doctrine territory through currentness, `trust_surface`, `support_only`, and `ignore`. |
| Patch/refactor existing artifact instead of rewrite from scratch | `make-real`, `cursor-memory-bank`, shipped preservation examples | `Example Gap` | Preservation law and current truth already support this. The gap is more explicit examples. |
| Guarded readback on outputs and comments | `ai-legal-claude`, review-heavy sources, shipped `examples/39` and `49` | `Shipped` | Strong existing surface. |

### Orchestration, Delegation, And Authority

| Pattern | External Evidence | Doctrine Status | Support Shape To Consider |
| --- | --- | --- | --- |
| Serial staged delegation with explicit checkpoints | `agency-swarm`, `crewai-examples`, `cursor-memory-bank`, `seclab-taskflow-agent` | `Shipped` | Workflows, routes, and reviews already cover this. The biggest gain is an `analysis`-style surface for repeated stage ladders. |
| Reusable phase ladders or taskflow libraries | `cursor-memory-bank`, `seclab-taskflow-agent`, `agency-swarm` | `Planned` | `analysis` is the planned home for reusable ordered reasoning and decision programs. |
| Parallel specialist fan-out plus aggregation | `ai-legal-claude`, `tradingagents` | `Future Candidate` | This is one of the clearest true gaps. Current Doctrine handles serial control flow well but does not obviously model join semantics. |
| Manager-as-tool delegation versus transfer-of-control handoff | `openai-agents-python`, `agency-swarm`, `langgraph` | `Future Candidate` | Current Doctrine can approximate this with skills and routes, but the distinction is not compiler-owned today. |
| Planning, exploration, verification, and execution as separate authority envelopes | `claude-code-system-prompts`, `system-prompts-and-models`, `agency-swarm` | `Future Candidate` | Current law `mode` and ordinary workflows help, but no first-class authority/profile surface exists yet. |
| Intent or runtime mode routers | `system-prompts-and-models`, `make-real`, `claude-code-action`, shipped `example 32` pressure | `Example Gap` | Enums plus `mode` and `match` already fit this well. The corpus just needs direct examples beyond current workflow-law mode selection. |
| Interrupt or human-response branches | `langgraph`, `livekit-agents-js`, `openai-agents-python` | `Future Candidate` | Review and workflow law can route to people, but they do not yet model runtime interrupt/resume semantics directly. |
| Reflection and archive phases | `cursor-memory-bank`, `agency-swarm` | `Example Gap` | Workflows plus outputs already fit this. Add examples for post-turn archive artifacts and reset points. |
| Role-specific preconditions or opening phrases | `agency-swarm` | `Keep Out` | This is meaningful authoring guidance but does not justify a core primitive. Keep it in prose. |

### Safety, Review, And Policy

| Pattern | External Evidence | Doctrine Status | Support Shape To Consider |
| --- | --- | --- | --- |
| Evidence-first review and no-speculation doctrine | `agency-swarm`, `seclab-taskflow-agent`, shipped review ladder | `Shipped` | Review and workflow law already support this strongly. |
| Hard negative guardrails | `openai-codex`, `sentry-monorepo`, `cursor-security-rules`, `cloudflare-docs`, `make-real` | `Example Gap` | Doctrine can already express these as prose plus diagnostics. The gap is a more explicit negative-case ladder. |
| Approval gates for dangerous actions | `cursor-security-rules`, `system-prompts-and-models`, `claude-code-system-prompts` | `Future Candidate` | Can be modeled with workflows today, but a later capability-governance surface may be warranted. |
| Secret leakage, unsafe URLs, cookies, token hygiene | `sentry-mcp`, `cursor-security-rules`, `claude-code-action` | `Example Gap` | Strong generic guardrail examples are worth adding. Keep concrete provider/OAuth details out of core. |
| Taint-style untrusted-input-to-sink reasoning | `cursor-security-rules` | `Keep Out` | Good pressure, but too stack- and language-specific for the current Doctrine core plan. |
| Language- or path-scoped safety rules | `cursor-security-rules`, `patrickjs-awesome-cursorrules`, `sentry-monorepo` | `Future Candidate` | Could become a later scoped-rule-pack surface, but examples should come first. |
| Requirement to explain missing evidence or violated rule | `agency-swarm`, `cursor-security-rules`, review-heavy sources | `Example Gap` | Output/readback and review comments already fit this. Add examples before new primitives. |
| Preview-build, codeowner, stale-review, or no-response automation | `cloudflare-docs`, `rockylinux-org` | `Keep Out` | These are repo-workflow policies, not Doctrine core language. |
| Soft rules versus hard rules | `patrickjs-awesome-cursorrules`, `system-prompts-and-models` | `Future Candidate` | There may be room later for explicit severity metadata, but today this should remain prose plus emphasized lines. |

### Rendering, Readability, And Packaging

| Pattern | External Evidence | Doctrine Status | Support Shape To Consider |
| --- | --- | --- | --- |
| Tables, checklists, definitions, and ordered sequences as first-class contract shapes | `cloudflare-docs`, `sentry-mcp`, `claude-code-action`, `ai-legal-claude`, `make-real` | `Planned` | This is exactly what `document` and the readable block layer are meant to absorb. |
| Natural rendered markdown instead of AST-looking heading ladders | almost every markdown-native source in the bank | `Planned` | Direct match for `READABLE_MARKDOWN_SPEC.md`. |
| Rich multiline authored content like code fences and examples | `cloudflare-docs`, `claude-code-action`, `make-real` | `Planned` | Strong fit for multiline string support plus readable code blocks. |
| Generated rule catalogs with separate discovery/index layers | `awesome-agent-skills`, `vercel-agent-skills`, `cloudflare-docs` | `Planned` | Model the catalog structure with `schema` and `document`. Keep generation mechanics out of core. |
| One source rendered into multiple consumer-facing formats | `langchain`, `langgraph`, `vercel-agent-skills` | `Future Candidate` | Likely a tooling problem, not a new language family. |

## Synthesis

### What The External Bank Most Strongly Validates

The harvested corpus strongly validates the current Doctrine direction in three
places:

1. `analysis` is the right response to repeated ordered reasoning ladders.
   The orchestration repos keep rediscovering named stage sequences, reusable
   flow fragments, review checkpoints, and phase ladders.

2. `schema` is the right response to repeated inventories, capability tables,
   rule catalogs, and data-backed contract sections.
   The external bank repeatedly authors artifact inventories as prose or
   markdown tables that want a typed home.

3. `document` is the right response to markdown-native agent contracts.
   The external bank is full of checklists, tables, callouts, definitions,
   ordered action lists, rule catalogs, and structured response templates that
   currently collapse into heading ladders.

### What Looks Like The Strongest Next Gap After The Planned Wave

After the current planned wave, the strongest real candidate gaps are:

- capability metadata beyond `skill`
  This means allowed tools, blocked tools, safety class, visibility, numeric
  caps, and possibly connector requirements.
- authority envelopes
  Planning, exploration, verification, and execution recur as distinct
  authorities in the external bank.
- runtime result-surface separation
  `openai-agents-python` especially pressures a distinction between final
  output, raw runtime items, interruptions, and handoff metadata.
- parallel fan-out and aggregation
  `ai-legal-claude` and `tradingagents` pressure a structural join point that
  current Doctrine does not obviously own yet.

### What Should Stay Out Of Core

The bank also contains a lot of useful pressure that should not be promoted
into Doctrine primitives:

- repo-specific command names, CI labels, local setup rituals, and package
  paths
- provider brands, browser brands, product labels, and SDK naming
- framework- or language-specific guardrails as built-in semantics
- legal, medical, finance, or domain-specific vocabulary as Doctrine truth
- upgrade details, review automation details, or house voice/style rules as
  core language
- taint-analysis specifics and sink catalogs as first-wave core semantics

Those belong in:

- domain packs
- authored prose
- generated catalogs
- tooling or drift-check layers outside the compiler

## Recommended Support Strategy

### Tier 1: Finish The Current Planned Wave

The external bank reinforces the current plan rather than contradicting it.
The highest-leverage next work is still:

- ship `analysis`
- ship `schema`
- ship `document` and readable markdown blocks
- keep inheritance, patching, addressability, and diagnostics consistent with
  shipped Doctrine

### Tier 2: Expand The Corpus Before Adding New Primitives

Before inventing more language, add example ladders for:

- root-to-child scope overrides and ignored-scope diagnostics
- command-first verification and explicit closeout gates
- skill usage triggers, discovery, and role-local exclusions
- shared state artifacts and single-source-of-truth discipline
- mode routers using enums plus `mode` and `match`
- browser/session/auth carriers using existing I/O and trust surfaces
- evidence-first security review and no-speculation review patterns
- fixed-order report outputs and disclaimers using output contracts

### Tier 3: Treat These As Real Later Candidates

After the planned wave and the example expansion, the best candidates for new
core or semi-core surfaces are:

- enriched capability metadata for tools and connectors
- authority-profile modeling for planning versus execution versus verification
- runtime result-surface separation
- parallel orchestration fan-out and aggregation
- explicit severity for soft rule versus hard rule if prose/emphasis proves
  insufficient

## Bottom Line

The external bank does not argue for a large explosion of new Doctrine
primitives.

It argues for:

- finishing the current `analysis` + `schema` + `document` wave
- teaching more of the already-shipped control-plane semantics through better
  examples
- then considering a small second follow-on wave around capability metadata,
  authority envelopes, result-surface separation, and parallel aggregation

The strongest consistent lesson across the harvested repos is:

stable operational semantics should be explicit, typed, and fail loud;
repo-local taste, vendor specifics, and domain details should stay out of core.

## Concrete External Evidence For The Gap Rows

This section makes the document freestanding.

It covers the patterns in the analysis that are not already classified
`Shipped`, and it anchors them in exact prose from the harvested raw files.

The rule used here is:

- for `Example Gap`, `Planned`, and `Future Candidate` rows, show the external
  prose that is creating pressure
- keep the examples generic enough to illuminate the pattern, but concrete
  enough that the reader has the full argument in this file without needing to
  open anything else

### Governance, Scope, And Verification Evidence

#### Root contract plus child overrides by path

- Cloudflare root declares the hierarchy directly:
  `Some directories have their own AGENTS.md with deeper guidance`
  in `../example_agents/harvested/cloudflare-agents/raw/AGENTS.md:L40`.
  This is explicit root-to-child scope routing.
- The same Cloudflare root names the scoped children:
  `packages/agents/AGENTS.md`, `examples/AGENTS.md`, `guides/AGENTS.md`,
  `docs/AGENTS.md`, and `design/AGENTS.md`
  in `../example_agents/harvested/cloudflare-agents/raw/AGENTS.md:L42`.
- Next.js root says:
  `Before editing or creating files in any subdirectory ... read all README.md files in the directory path`
  in `../example_agents/harvested/vercel-nextjs/raw/AGENTS.md:L44`.
  This is a path-sensitive context-loading rule.
- Next.js child scope narrows behavior further:
  `This is NOT the Next.js you know ... Read the relevant guide in dist/docs/ before writing any code`
  in `../example_agents/harvested/vercel-nextjs/raw/packages/next/AGENTS.md:L3`.
- Sentry monorepo root explicitly routes by path:
  `Use the right AGENTS.md for the area you're working in`
  in `../example_agents/harvested/sentry-monorepo/raw/AGENTS.md:L181`.
- OpenAI Codex has a very narrow subsystem-local override:
  `When changing the paste-burst or chat-composer state machines in this folder, keep the docs in sync`
  in `../example_agents/harvested/openai-codex/raw/codex-rs/tui/src/bottom_pane/AGENTS.md:L3`.

#### Non-AGENTS docs acting as instruction law

- Cloudflare Docs style-guide index says:
  `Use this guide when writing any content for product`
  in `../example_agents/harvested/cloudflare-docs/raw/src/content/docs/style-guide/index.mdx:L11`.
- Cloudflare Docs writing guide says:
  `Use the following writing guidelines to create product content that is clear and consistent`
  in `../example_agents/harvested/cloudflare-docs/raw/src/content/docs/style-guide/documentation-content-strategy/writing-guidelines.mdx:L10`.
- Cloudflare Docs review runbook says:
  `We have one required check that runs on every commit, CI`
  in `../example_agents/harvested/cloudflare-docs/raw/src/content/docs/style-guide/how-we-docs/reviews.mdx:L49`.
- Rocky Linux docs README says:
  `When adding new documentation:`
  in `../example_agents/harvested/rockylinux-org/raw/docs/README.md:L35`.
  It is a policy surface, not just an index.
- Sentry React Native CI runbook says:
  `run the full suite only when the PR has the label ready-to-merge`
  in `../example_agents/harvested/sentry-react-native/raw/CI.md:L5`.
  This is workflow law authored outside `AGENTS.md`.

#### Command-first setup, build, lint, and test gates

- Cloudflare Agents root says:
  `Run npm run check before considering work done`
  in `../example_agents/harvested/cloudflare-agents/raw/AGENTS.md:L173`.
- LangGraph root says:
  `When you modify code in any library, run the following commands in that library's directory before creating a pull request`
  in `../example_agents/harvested/langgraph/raw/AGENTS.md:L5`.
- LangChain root says:
  `Before running your tests, set up all packages by running:`
  in `../example_agents/harvested/langchain/raw/AGENTS.md:L47`.
- Next.js root says:
  `Default agent rule: If you are changing Next.js source or integration tests, start pnpm --filter=next dev in a separate terminal session before making edits`
  in `../example_agents/harvested/vercel-nextjs/raw/AGENTS.md:L75`.
- Rocky Linux root opens with exact commands in its quick-start section:
  `npm install` and `npm run dev`
  in `../example_agents/harvested/rockylinux-org/raw/CLAUDE.md:L9`.

#### Area-specific verification gates

- Cloudflare Docs distinguishes MDX validation from code validation:
  `Minimum validation for content changes (MDX edits)`
  and
  `Minimum validation for code changes (.ts/.tsx/.astro/.js)`
  in `../example_agents/harvested/cloudflare-docs/raw/AGENTS.md:L248`.
- Sentry React Native Android child scope requires platform-local checks such as
  `yarn lint:android` and `yarn java:pmd`
  in `../example_agents/harvested/sentry-react-native/raw/packages/core/android/AGENTS.md:L5`.
- Sentry React Native iOS child scope requires a different native stack:
  `yarn lint:clang` and `yarn lint:swift`
  in `../example_agents/harvested/sentry-react-native/raw/packages/core/ios/AGENTS.md:L5`.
- Sentry monorepo says:
  `Before you consider a coding task complete, run pre-commit on any files you created or modified`
  in `../example_agents/harvested/sentry-monorepo/raw/AGENTS.md:L90`.

#### Public API stability as repo law

- LangChain says:
  `CRITICAL: Always attempt to preserve function signatures, argument positions, and names for exported/public methods. Do not make breaking changes`
  in `../example_agents/harvested/langchain/raw/AGENTS.md:L104`.
- Cloudflare package-local rules say:
  `These are the boundaries of the public API`
  in `../example_agents/harvested/cloudflare-agents/raw/packages/agents/AGENTS.md:L7`.
- Cloudflare root says:
  `Changes to packages/ that affect the public API or fix bugs need a changeset`
  in `../example_agents/harvested/cloudflare-agents/raw/AGENTS.md:L140`.
- OpenAI Codex says:
  `All active API development should happen in app-server v2. Do not add new API surface area to v1`
  in `../example_agents/harvested/openai-codex/raw/AGENTS.md:L176`.

#### Doc-sync obligations for narrow subsystems

- OpenAI Codex root says:
  `When making a change that adds or changes an API, ensure that the documentation in the docs/ folder is up to date if applicable`
  in `../example_agents/harvested/openai-codex/raw/AGENTS.md:L23`.
- The same file says:
  `Update docs/examples when API behavior changes`
  in `../example_agents/harvested/openai-codex/raw/AGENTS.md:L205`.
- OpenAI Codex bottom-pane child scope says:
  `keep the docs in sync`
  in `../example_agents/harvested/openai-codex/raw/codex-rs/tui/src/bottom_pane/AGENTS.md:L3`.
- Cloudflare docs subtree says:
  `There is no automated sync workflow ... also update the corresponding .mdx file in cloudflare-docs`
  in `../example_agents/harvested/cloudflare-agents/raw/docs/AGENTS.md:L24`.
- Cloudflare design subtree says:
  `update the relevant design doc to reflect the new reality`
  in `../example_agents/harvested/cloudflare-agents/raw/design/AGENTS.md:L24`.

#### Duplicate contract publication across formats

- Next.js says:
  `CLAUDE.md is a symlink to AGENTS.md. They are the same file`
  in `../example_agents/harvested/vercel-nextjs/raw/AGENTS.md:L3`.
- LangChain duplicates identical public-interface law in both
  `../example_agents/harvested/langchain/raw/AGENTS.md:L104`
  and
  `../example_agents/harvested/langchain/raw/CLAUDE.md:L104`.
- LangGraph duplicates its verification contract across
  `../example_agents/harvested/langgraph/raw/AGENTS.md:L5`
  and
  `../example_agents/harvested/langgraph/raw/CLAUDE.md:L5`.

#### Generated instruction artifacts as published truth

- Vercel skill-pack authoring makes packaging part of the contract:
  `{skill-name}.zip        # Required: packaged for distribution`
  in `../example_agents/harvested/vercel-agent-skills/raw/AGENTS.md:L19`.
- The same file makes the publication step explicit:
  `zip -r {skill-name}.zip {skill-name}/`
  in `../example_agents/harvested/vercel-agent-skills/raw/AGENTS.md:L95`.
- Awesome Agent Skills acts as a published catalog surface around those
  artifacts:
  `## Skills Paths for Other AI Coding Assistants`
  in `../example_agents/harvested/awesome-agent-skills/raw/README.md:L1184`.

### Capabilities, Skills, Tools, Sessions, And Result-Surface Evidence

#### Skill usage triggers and “use when / not for this role” guidance

- OpenClaw FHIR skill frontmatter says:
  `Use when: (1) Creating FHIR REST endpoints ... (3) Implementing SMART on FHIR authorization and OAuth scopes`
  in `../example_agents/harvested/openclaw-medical-skills/raw/skills/fhir-developer-skill/SKILL.md:L4`.
- OpenClaw prior-auth skill says:
  `This skill should be used when users say "Review this PA request", "Process prior authorization for [procedure]" ...`
  in `../example_agents/harvested/openclaw-medical-skills/raw/skills/prior-auth-review-skill/SKILL.md:L3`.
- Vercel browser skill says:
  `Use when the user needs to interact with websites ... Triggers include requests to "open a website", "fill out a form", "click a button"`
  in `../example_agents/harvested/vercel-agent-browser/raw/skills/agent-browser/SKILL.md:L3`.
- Vercel skill-pack authoring rules require trigger prose:
  `description: {One sentence describing when to use this skill. Include trigger phrases ...}`
  in `../example_agents/harvested/vercel-agent-skills/raw/AGENTS.md:L34`.

#### Allowed-tools and blocked-tools lists

- Vercel browser skill frontmatter says:
  `allowed-tools: Bash(npx agent-browser:*), Bash(agent-browser:*)`
  in `../example_agents/harvested/vercel-agent-browser/raw/skills/agent-browser/SKILL.md:L4`.
- OpenClaw search strategy skill uses an allowlist style:
  `allowed-tools: read_file, run_shell_command`
  in `../example_agents/harvested/openclaw-medical-skills/raw/skills/search-strategy/SKILL.md:L24`.
- Claude Code base action exposes both sides as workflow inputs:
  `allowed_tools` and `disallowed_tools`
  in `../example_agents/harvested/claude-code-action/raw/base-action/README.md:L92`.
- OpenAI Agents Python says:
  `Disabled tools are completely hidden from the LLM at runtime`
  in `../example_agents/harvested/openai-agents-python/raw/docs/tools.md:L762`.

#### Tool safety metadata like read-only, destructive, hidden, idempotent

- Sentry MCP says:
  `All tools must include safety annotations`
  in `../example_agents/harvested/sentry-mcp/raw/docs/adding-tools.md:L77`.
- It then names the fields explicitly:
  `readOnlyHint`, `destructiveHint`, `idempotentHint`, and `openWorldHint`
  in `../example_agents/harvested/sentry-mcp/raw/docs/adding-tools.md:L80`.
- The same Sentry MCP doc defines hidden helpers:
  `internalOnly — Composition primitives ... never exposed directly via MCP`
  in `../example_agents/harvested/sentry-mcp/raw/docs/adding-tools.md:L10`.
- It also hides tools by capability:
  `If the upstream project doesn't have a capability enabled, the tool is automatically hidden`
  in `../example_agents/harvested/sentry-mcp/raw/docs/adding-tools.md:L9`.

#### Numeric tool or capability budgets

- Sentry MCP root says:
  `Tool count: Target ≤20, hard limit 25`
  in `../example_agents/harvested/sentry-mcp/raw/AGENTS.md:L13`.
- The tool-authoring guide repeats the constraint:
  `Target ~20 publicly visible tools. Never exceed 25`
  in `../example_agents/harvested/sentry-mcp/raw/docs/adding-tools.md:L18`.
- OpenAI Agents Python adds a softer namespace budget:
  `keep each namespace fairly small, ideally fewer than 10 functions`
  in `../example_agents/harvested/openai-agents-python/raw/docs/tools.md:L115`.

#### Required connectors, auth, env, or session prerequisites

- OpenClaw prior-auth skill says:
  `This skill requires 3 healthcare MCP connectors`
  in `../example_agents/harvested/openclaw-medical-skills/raw/skills/prior-auth-review-skill/SKILL.md:L47`.
- The same skill says:
  `Before proceeding, verify required MCP connectors are available`
  and
  `If any MCP connectors are not configured: Display error and exit`
  in `../example_agents/harvested/openclaw-medical-skills/raw/skills/prior-auth-review-skill/SKILL.md:L117`.
- LiveKit root says:
  `Required env vars: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, plus provider keys`
  in `../example_agents/harvested/livekit-agents-js/raw/CLAUDE.md:L49`.
- Claude Code Action says:
  `Auth priority: github_token input (user-provided) > GitHub App OIDC token (default)`
  in `../example_agents/harvested/claude-code-action/raw/CLAUDE.md:L24`.

#### Provider/plugin/browser capability matrices

- LiveKit exposes a capability matrix by plugin family:
  `Plugin capabilities by type: LLM ... STT ... TTS ... Realtime ... Avatar`
  in `../example_agents/harvested/livekit-agents-js/raw/CLAUDE.md:L106`.
- LiveKit README says:
  `Currently, only the following plugins are supported:`
  and then renders a `Plugin | Features` table
  in `../example_agents/harvested/livekit-agents-js/raw/README.md:L60`.
- OpenAI plugin README says:
  `allows for TTS, STT, LLM, as well as using the Realtime API and Responses API`
  in `../example_agents/harvested/livekit-agents-js/raw/plugins/openai/README.md:L12`.
- ElevenLabs plugin README says:
  `allows for voice synthesis`
  in `../example_agents/harvested/livekit-agents-js/raw/plugins/elevenlabs/README.md:L12`.

#### Skill catalogs and registry metadata separate from skill bodies

- Vercel skill-pack root says:
  `A collection of skills`
  and then defines package structure under `skills/{skill-name}/`
  in `../example_agents/harvested/vercel-agent-skills/raw/AGENTS.md:L7`.
- The same file says:
  `Skills are loaded on-demand — only the skill name and description are loaded at startup`
  in `../example_agents/harvested/vercel-agent-skills/raw/AGENTS.md:L72`.
- Awesome Agent Skills behaves as a pure catalog layer:
  `Skills Paths for Other AI Coding Assistants`
  in `../example_agents/harvested/awesome-agent-skills/raw/README.md:L1184`.

#### Fixed-order output templates and strong readback contracts

- AI Legal Claude makes exact format compliance part of subagent execution:
  `Return your analysis in the exact output format specified in your agent instructions.`
  in `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L87`.
- It then fixes the final report shape explicitly:
  `Generate \`CONTRACT-REVIEW-[name]-[date].md\` with this structure:`
  in `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L111`.
- The same template locks in section order and named blocks like
  `## Contract Details`, `## Risk Dashboard`, and
  `## Recommended Next Steps`
  in `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L124`,
  `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L134`,
  and
  `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L179`.
- It even fixes repeated clause-local substructure:
  `What it says:` and `Why it's risky:`
  in `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L147`
  and
  `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L148`.
- Make Real uses the same idea for single-file UI output:
  `Your entire response must be a single HTML file enclosed in a markdown code block`
  and
  `Do not include any explanatory text outside of this block`
  in `../example_agents/harvested/make-real/raw/prompts/google-system-prompt.md:L26`.

#### Structured data namespace catalogs

- Sentry MCP carries a true namespace catalog, not just prose:
  `This directory contains JSON files for OpenTelemetry semantic convention namespaces`
  in `../example_agents/harvested/sentry-mcp/raw/packages/mcp-core/src/internal/agents/tools/data/CLAUDE.md:L3`.
- It fixes the per-namespace schema explicitly:
  `Each JSON file represents a namespace and follows this structure:`
  in `../example_agents/harvested/sentry-mcp/raw/packages/mcp-core/src/internal/agents/tools/data/CLAUDE.md:L7`.
- It then names the shape fields directly:
  `namespace`, `description`, and `attributes`
  in `../example_agents/harvested/sentry-mcp/raw/packages/mcp-core/src/internal/agents/tools/data/CLAUDE.md:L11`.
- The same file also shows a maintained catalog of concrete domains:
  `Key Namespaces`
  including `gen_ai`, `db`, `http`, `rpc`, `messaging`, and `mcp`
  in `../example_agents/harvested/sentry-mcp/raw/packages/mcp-core/src/internal/agents/tools/data/CLAUDE.md:L48`.

#### Final output split from waypoint artifacts

- OpenClaw prior-auth skill names both the final package and the waypoints:
  `Output: Authorization Decision Package`
  and
  `assessment.json` / `decision.json`
  in `../example_agents/harvested/openclaw-medical-skills/raw/skills/prior-auth-review-skill/SKILL.md:L30`.
- It later distinguishes intermediate and final artifacts again:
  `Output: waypoints/assessment.json`
  versus
  `waypoints/decision.json` and `outputs/notification_letter.txt`
  in `../example_agents/harvested/openclaw-medical-skills/raw/skills/prior-auth-review-skill/SKILL.md:L204`.
- AI Legal Claude makes the same join pattern explicit:
  `Once all 5 agents return, compile the unified report`
  in `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L92`.

#### Final output split from runtime metadata, interruptions, raw responses, and run items

- OpenAI Agents Python names the result surfaces directly:
  `final_output`, `new_items`, `last_agent`, `raw_responses`, and to_state()`
  in `../example_agents/harvested/openai-agents-python/raw/docs/results.md:L8`.
- Its table separates:
  `The final answer to show the user`,
  `Rich run items with agent, tool, handoff, and approval metadata`,
  `Pending approvals and a resumable snapshot`,
  and
  `Raw model calls`
  in `../example_agents/harvested/openai-agents-python/raw/docs/results.md:L16`.
- It later says:
  `Use new_items when you need SDK metadata, or inspect raw_responses when you need the raw model payloads`
  in `../example_agents/harvested/openai-agents-python/raw/docs/results.md:L60`.
- It also makes interruption state explicit:
  `interruptions` and `to_state()`
  in `../example_agents/harvested/openai-agents-python/raw/docs/results.md:L89`.

#### Handoff payload distinct from next-owner history

- OpenAI Agents Python says:
  `input_type describes the arguments for the handoff tool call itself`
  in `../example_agents/harvested/openai-agents-python/raw/docs/handoffs.md:L86`.
- It immediately narrows the boundary:
  `It does not replace the next agent's main input`
  in `../example_agents/harvested/openai-agents-python/raw/docs/handoffs.md:L88`.
- It distinguishes model-generated metadata from durable state:
  `Use input_type for metadata the model decides at handoff time, not for application state`
  in `../example_agents/harvested/openai-agents-python/raw/docs/handoffs.md:L90`.
- It also exposes history packaging as a separate surface:
  `input_items ... allowing you to filter model input while keeping new_items intact for session history`
  in `../example_agents/harvested/openai-agents-python/raw/docs/handoffs.md:L112`.

#### Session, auth, and profile carriers

- Vercel browser skill names multiple state carriers:
  `Chrome profile reuse`, `Persistent profile`, `Session name`, `Auth vault`, and `State file`
  in `../example_agents/harvested/vercel-agent-browser/raw/skills/agent-browser/SKILL.md:L49`.
- The same file says:
  `State files contain session tokens in plaintext`
  in `../example_agents/harvested/vercel-agent-browser/raw/skills/agent-browser/SKILL.md:L62`.
- Vercel browser session-management reference defines session boundaries concretely:
  `Each session has independent: Cookies, LocalStorage / SessionStorage, IndexedDB, Cache, Browsing history, Open tabs`
  in `../example_agents/harvested/vercel-agent-browser/raw/skills/agent-browser/references/session-management.md:L35`.
- LiveKit says:
  `AgentSession — Orchestrates the full session lifecycle`
  in `../example_agents/harvested/livekit-agents-js/raw/CLAUDE.md:L68`.
- OpenAI Agents Python uses an application-state carrier distinct from handoff payloads:
  `context is a dependency-injection tool ... passed to every agent, tool, handoff`
  in `../example_agents/harvested/openai-agents-python/raw/docs/agents.md:L121`.

### Orchestration, Delegation, And Memory Evidence

#### Serial staged delegation with explicit checkpoints

- Cursor Memory Bank defines an explicit ordered ladder:
  `/van → /plan → /creative → /build → /reflect → /archive`
  in `../example_agents/harvested/cursor-memory-bank/raw/COMMANDS_README.md:L72`.
- Its command docs also define handoff points after each phase:
  `After implementation complete → /reflect`
  and
  `After reflection complete → /archive`
  in `../example_agents/harvested/cursor-memory-bank/raw/COMMANDS_README.md:L47`.
- OpenClaw prior-auth skill encodes a sequential staged flow:
  `Execute Subskill 1: Intake & Assessment` then `Execute Subskill 2: Decision & Notification`
  in `../example_agents/harvested/openclaw-medical-skills/raw/skills/prior-auth-review-skill/SKILL.md:L102`.
- Agency Swarm portfolio-manager instructions encode review checkpoints:
  `Risk Analysis Delegation`, `Risk Review`, `Report Generation Delegation`, `Final Report Review`, then `Investment Recommendation`
  in `../example_agents/harvested/agency-swarm/raw/tests/integration/fin_agency/financial_research_agency/PortfolioManager/instructions.md:L16`.

#### Reusable phase ladders or taskflow libraries

- Cursor Memory Bank root says it has
  `six specialized commands`
  that
  `work together as an integrated workflow`
  in `../example_agents/harvested/cursor-memory-bank/raw/README.md:L42`.
- Seclab Taskflow Agent says:
  `Agents can cooperate to complete sequences of tasks through so-called taskflows`
  in `../example_agents/harvested/seclab-taskflow-agent/raw/README.md:L12`.
- Its reusable flow example says:
  `with the uses directive we can reuse single task taskflows`
  in `../example_agents/harvested/seclab-taskflow-agent/raw/examples/taskflows/example_reusable_taskflows.yaml:L12`.
- Its comprehensive test explicitly lists:
  `uses`, `repeat_prompt`, `blocked_tools`, `agent handoffs`, and `headless`
  in `../example_agents/harvested/seclab-taskflow-agent/raw/examples/taskflows/comprehensive_test.yaml:L4`.

#### Parallel specialist fan-out plus aggregation

- AI Legal Claude opens with the clearest statement in the bank:
  `You launch 5 parallel subagents, aggregate their results`
  in `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L3`.
- It then says:
  `Launch ALL 5 subagents simultaneously`
  in `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L57`.
- It defines the join point explicitly:
  `Once all 5 agents return, compile the unified report`
  in `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L92`.
- CrewAI examples mention:
  `parallel chapter generation`
  in `../example_agents/harvested/crewai-examples/raw/README.md:L31`.

#### Manager-as-tool delegation versus transfer-of-control handoff

- OpenAI Agents Python makes the distinction explicit:
  `A central manager/orchestrator invokes specialized sub-agents as tools and retains control of the conversation`
  in `../example_agents/harvested/openai-agents-python/raw/docs/agents.md:L169`.
- The next line gives the contrasting case:
  `Peer agents hand off control to a specialized agent that takes over the conversation`
  in `../example_agents/harvested/openai-agents-python/raw/docs/agents.md:L170`.
- Its handoff docs say:
  `always transfers control to the specific agent you passed in`
  in `../example_agents/harvested/openai-agents-python/raw/docs/handoffs.md:L44`.
- The same doc preserves the opposite branch:
  `prefer Agent.as_tool(parameters=...) ... without transferring the conversation`
  in `../example_agents/harvested/openai-agents-python/raw/docs/handoffs.md:L101`.

#### Interrupt or human-response branches

- LangGraph root includes:
  `Human-in-the-loop`
  and
  `inspecting and modifying agent state at any point during execution`
  in `../example_agents/harvested/langgraph/raw/README.md:L40`.
- OpenAI Agents Python results docs say:
  `Pending approvals and a resumable snapshot`
  in `../example_agents/harvested/openai-agents-python/raw/docs/results.md:L23`.
- The same page says:
  `capture a resumable RunState, approve or reject the pending items, and then resume`
  in `../example_agents/harvested/openai-agents-python/raw/docs/results.md:L91`.

#### Reflection and archive phases

- Cursor Memory Bank names them directly:
  `/reflect - Reviews completed work and documents lessons learned`
  and
  `/archive - Creates comprehensive documentation and updates Memory Bank`
  in `../example_agents/harvested/cursor-memory-bank/raw/README.md:L48`.
- Its command reference mirrors the split:
  `Task Reflection`
  and
  `Task Archiving`
  in `../example_agents/harvested/cursor-memory-bank/raw/COMMANDS_README.md:L50`.
- The archive phase is active, not passive:
  `Creates comprehensive archive documentation and update Memory Bank`
  in `../example_agents/harvested/cursor-memory-bank/raw/COMMANDS_README.md:L61`.

#### Shared state artifact and single source of truth

- Cursor Memory Bank says:
  `All commands read from and update files in the memory-bank/ directory`
  in `../example_agents/harvested/cursor-memory-bank/raw/COMMANDS_README.md:L90`.
- It names one authoritative file:
  `tasks.md - Source of truth for task tracking`
  in `../example_agents/harvested/cursor-memory-bank/raw/COMMANDS_README.md:L94`.
- The optimization note reinforces this:
  `Designated tasks.md as the ONLY file for task status tracking`
  in `../example_agents/harvested/cursor-memory-bank/raw/optimization-journey/04-single-source-of-truth.md:L10`.
- It then states the anti-duplication rule directly:
  `Modified all files to reference but not duplicate task information`
  in `../example_agents/harvested/cursor-memory-bank/raw/optimization-journey/04-single-source-of-truth.md:L13`.

### Safety, Mode Routing, Read-Only Authorities, And Scoped Rule Packs

#### Intent or runtime mode routers

- The Kiro mode classifier says:
  `classify the user's intent ... into one of two main categories: Do mode ... Spec mode`
  in `../example_agents/harvested/system-prompts-and-models/raw/Kiro/Mode_Clasifier_Prompt.txt:L3`.
- The same prompt adds a fail-closed default:
  `When in doubt, classify as "Do" mode`
  in `../example_agents/harvested/system-prompts-and-models/raw/Kiro/Mode_Clasifier_Prompt.txt:L36`.
- Claude Code Action exposes runtime mode detection:
  `Mode is auto-detected: if prompt is provided, it's agent mode; if triggered by a comment/issue event with @claude, it's tag mode`
  in `../example_agents/harvested/claude-code-action/raw/CLAUDE.md:L14`.
- Make Real adds provider/runtime mode branching:
  `Supports "all" provider mode ... runs OpenAI, Anthropic, and Google in parallel`
  in `../example_agents/harvested/make-real/raw/CLAUDE.md:L46`.

#### Read-only and authority-envelope separation

- Claude Code system prompts define planning as a hard authority envelope:
  `READ-ONLY MODE - NO FILE MODIFICATIONS`
  in `../example_agents/harvested/claude-code-system-prompts/raw/system-prompts/agent-prompt-plan-mode-enhanced.md:L27`.
- The same prompt says:
  `You CANNOT and MUST NOT write, edit, or modify any files`
  in `../example_agents/harvested/claude-code-system-prompts/raw/system-prompts/agent-prompt-plan-mode-enhanced.md:L74`.
- The explore prompt uses a different read-only authority:
  `This is a READ-ONLY exploration task`
  in `../example_agents/harvested/claude-code-system-prompts/raw/system-prompts/agent-prompt-explore.md:L30`.
- The verification specialist creates a third envelope:
  `Your job is not to confirm the work. Your job is to break it`
  and
  `DO NOT MODIFY THE PROJECT`
  in `../example_agents/harvested/claude-code-system-prompts/raw/system-prompts/agent-prompt-verification-specialist.md:L9`.

#### Hard negative guardrails

- Cursor security root says:
  `these rules act as guardrails`
  in `../example_agents/harvested/cursor-security-rules/raw/README.md:L7`.
- Claude security monitor first part defines precedence explicitly:
  `By default, actions are ALLOWED. Only block if the action matches a condition in "BLOCK" below AND no exception in "ALLOW" applies`
  in `../example_agents/harvested/claude-code-system-prompts/raw/system-prompts/agent-prompt-security-monitor-for-autonomous-agent-actions-first-part.md:L27`.
- The same monitor says:
  `PREEMPTIVE BLOCK ON CLEAR INTENT`
  in `../example_agents/harvested/claude-code-system-prompts/raw/system-prompts/agent-prompt-security-monitor-for-autonomous-agent-actions-first-part.md:L74`.
- The second part lists concrete blocked classes like
  `Code from External: Downloading and executing code from external sources`
  and
  `Create Unsafe Agents`
  in `../example_agents/harvested/claude-code-system-prompts/raw/system-prompts/agent-prompt-security-monitor-for-autonomous-agent-actions-second-part.md:L26`.
- Cursor secure-development principles says:
  `Untrusted input must never be used directly in file access, command execution, database queries`
  in `../example_agents/harvested/cursor-security-rules/raw/secure-development-principles.mdc:L14`.

#### Approval gates for dangerous actions

- Cursor MCP security says:
  `Never execute system or shell commands automatically based on MCP input without explicit human review and approval`
  in `../example_agents/harvested/cursor-security-rules/raw/secure-mcp-usage.mdc:L11`.
- The same file says:
  `require explicit user confirmation`
  before tool calls that can modify files, run commands, or query databases
  in `../example_agents/harvested/cursor-security-rules/raw/secure-mcp-usage.mdc:L25`.
- Claude security monitor clarifies approval semantics:
  `Questions are not consent`
  and
  `Only treat a user message as consent if it is a clear directive`
  in `../example_agents/harvested/claude-code-system-prompts/raw/system-prompts/agent-prompt-security-monitor-for-autonomous-agent-actions-first-part.md:L58`.

#### Requirement to explain missing evidence or violated rule

- Agency Swarm makes the missing-evidence obligation explicit:
  `if evidence is missing, call it out and ask`
  in `../example_agents/harvested/agency-swarm/raw/AGENTS.md:L7`.
- The same root repeats the rule in harder form:
  `never misstate or invent facts; if evidence is missing, say so and escalate`
  in `../example_agents/harvested/agency-swarm/raw/AGENTS.md:L91`.
- Cursor secure-development principles say:
  `All violations must include a clear explanation of which rule was triggered and why`
  in `../example_agents/harvested/cursor-security-rules/raw/secure-development-principles.mdc:L11`.
- The Python-specific pack makes the remediation form concrete:
  `if code is in violation add a comment explaining why.`
  in `../example_agents/harvested/cursor-security-rules/raw/secure-dev-python.mdc:L12`.

#### Secret leakage, unsafe URLs, token hygiene, and sensitive outputs

- Cursor secure-development principles says:
  `Secrets such as API keys, credentials, private keys, or tokens must not appear in frontend code, public repositories, or client-distributed files`
  in `../example_agents/harvested/cursor-security-rules/raw/secure-development-principles.mdc:L16`.
- Cursor MCP security says:
  `Do not transmit credentials, tokens, or personally identifiable information (PII) through MCP requests or responses`
  in `../example_agents/harvested/cursor-security-rules/raw/secure-mcp-usage.mdc:L13`.
- Claude security monitor second part tightens the scope:
  `Still counts if encoded (e.g. base64) or hidden in URLs/headers`
  in `../example_agents/harvested/claude-code-system-prompts/raw/system-prompts/agent-prompt-security-monitor-for-autonomous-agent-actions-second-part.md:L18`.
- Claude Code base action warns:
  `show_full_output ... May expose secrets`
  in `../example_agents/harvested/claude-code-action/raw/base-action/README.md:L108`.

#### Scoped rule packs: global, language-specific, path-specific, and soft versus hard

- Cursor security uses a global baseline:
  `alwaysApply: true`
  in `../example_agents/harvested/cursor-security-rules/raw/secure-development-principles.mdc:L4`.
- It also uses language-scoped packs:
  `globs: **/*.py,**/*.ipynb,**/*.pyw`
  in `../example_agents/harvested/cursor-security-rules/raw/secure-dev-python.mdc:L3`.
- PatrickJS rules use path-scoped packs:
  `globs: app/**/*.*`
  in `../example_agents/harvested/patrickjs-awesome-cursorrules/raw/rules/typescript-nextjs-react-cursorrules-prompt-file/next-js-app-router-data-fetching-rendering-and-routing-rules.mdc:L2`.
- Another PatrickJS rule narrows to tests:
  `globs: **/tests/**/*.*`
  in `../example_agents/harvested/patrickjs-awesome-cursorrules/raw/rules/python-312-fastapi-best-practices-cursorrules-prom/unit-testing-requirement.mdc:L2`.
- Soft-rule pressure shows up in style-oriented rule packs:
  `Utilize Early Returns`
  and
  `Prefer conditional classes over ternary operators`
  in `../example_agents/harvested/patrickjs-awesome-cursorrules/raw/rules/javascript-typescript-code-quality-cursorrules-pro/coding-guidelines---early-returns-and-conditionals.mdc:L5`.

#### Patch/refactor existing artifact instead of rewrite from scratch

- Make Real OpenAI prompt says:
  `Return a single, self-contained HTML file`
  in `../example_agents/harvested/make-real/raw/prompts/openai-system-prompt.md:L5`.
- Make Real Google prompt goes further:
  `Existing HTML Source Code ... treat this not as a reference, but as a live document to be refactored`
  in `../example_agents/harvested/make-real/raw/prompts/google-system-prompt.md:L9`.
- The same file says:
  `Do not start over`
  when existing code is provided
  in `../example_agents/harvested/make-real/raw/prompts/google-system-prompt.md:L19`.
- Cursor Memory Bank says:
  `Modified all files to reference but not duplicate task information`
  in `../example_agents/harvested/cursor-memory-bank/raw/optimization-journey/04-single-source-of-truth.md:L13`.

### Rendering, Readability, And Packaging Evidence

#### Tables, checklists, definitions, and ordered sequences as first-class contract shapes

- AI Legal Claude renders core contract content as tables:
  `## Contract Details`
  and
  `## Risk Dashboard`
  in `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L124`
  and
  `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L134`.
- The same template uses an obligations table with fixed columns:
  `| Obligation | Party | Deadline | Consequence of Missing |`
  in `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L166`.
- It also uses an ordered action sequence:
  `## Recommended Next Steps`
  followed by numbered checklist-style steps
  in `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L179`.
- Cloudflare Docs uses review-facing comparison tables as a first-class
  artifact:
  `before/after table of links`
  in `../example_agents/harvested/cloudflare-docs/raw/src/content/docs/style-guide/how-we-docs/reviews.mdx:L72`.

#### Natural rendered markdown instead of AST-looking heading ladders

- AI Legal Claude does not ask for an AST dump or raw structured data; it asks
  for a readable report:
  `Generate \`CONTRACT-REVIEW-[name]-[date].md\` with this structure:`
  in `../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md:L111`.
- Cloudflare Docs frames policy in reader-facing question headings such as
  `What changed?`
  and
  `Is there anything else I need to check?`
  in `../example_agents/harvested/cloudflare-docs/raw/src/content/docs/style-guide/how-we-docs/reviews.mdx:L66`
  and
  `../example_agents/harvested/cloudflare-docs/raw/src/content/docs/style-guide/how-we-docs/reviews.mdx:L76`.
- Make Real likewise specifies a human-readable artifact form:
  `Your entire response must be a single HTML file enclosed in a markdown code block`
  in `../example_agents/harvested/make-real/raw/prompts/google-system-prompt.md:L26`.

#### Rich multiline authored content like code fences and examples

- Make Real requires fenced multiline output:
  `single HTML file enclosed in a markdown code block: \` \`\`\`html ... \`\`\` \``
  in `../example_agents/harvested/make-real/raw/prompts/google-system-prompt.md:L26`.
- Vercel skill-pack publishing guidance includes a multiline `SKILL.md Format`
  template with sections for usage, output, troubleshooting, and result
  presentation
  in `../example_agents/harvested/vercel-agent-skills/raw/AGENTS.md:L29`.
- Claude Code Base Action publishes long-form YAML examples and stable
  contract tables under
  `## Usage`, `## Inputs`, and `## Outputs`
  in `../example_agents/harvested/claude-code-action/raw/base-action/README.md:L7`,
  `../example_agents/harvested/claude-code-action/raw/base-action/README.md:L86`,
  and
  `../example_agents/harvested/claude-code-action/raw/base-action/README.md:L114`.

#### Generated rule catalogs with separate discovery/index layers

- Awesome Agent Skills has an explicit discovery layer:
  `## Table of Contents`
  and
  `### Official Skills by`
  in `../example_agents/harvested/awesome-agent-skills/raw/README.md:L63`
  and
  `../example_agents/harvested/awesome-agent-skills/raw/README.md:L65`.
- The same catalog adds a consumer-install index:
  `| Tool | Project Path | Global Path | Official Docs |`
  in `../example_agents/harvested/awesome-agent-skills/raw/README.md:L1186`.
- Vercel skill-pack separates lightweight discovery from full body load:
  `Skills are loaded on-demand — only the skill name and description are loaded at startup`
  in `../example_agents/harvested/vercel-agent-skills/raw/AGENTS.md:L72`.

#### One source rendered into multiple consumer-facing formats

- Vercel skill-pack treats the authored source and packaged output as distinct
  publication forms:
  `{skill-name}.zip        # Required: packaged for distribution`
  and
  `zip -r {skill-name}.zip {skill-name}/`
  in `../example_agents/harvested/vercel-agent-skills/raw/AGENTS.md:L19`
  and
  `../example_agents/harvested/vercel-agent-skills/raw/AGENTS.md:L95`.
- The same instructions then route the same skill to different consumers:
  `Claude Code:`
  and
  `claude.ai:`
  with consumer-specific install surfaces
  in `../example_agents/harvested/vercel-agent-skills/raw/AGENTS.md:L102`
  and
  `../example_agents/harvested/vercel-agent-skills/raw/AGENTS.md:L107`.
- Awesome Agent Skills generalizes that same cross-consumer publication model
  in its matrix:
  `| Tool | Project Path | Global Path | Official Docs |`
  in `../example_agents/harvested/awesome-agent-skills/raw/README.md:L1186`.

## Evidence Summary

The evidence appendix sharpens the earlier conclusions.

The highest-signal repeated pressures are:

- hierarchical instruction scope with true local overrides
- command-first verification and closeout gates
- docs and runbooks acting as governing policy surfaces
- explicit skill triggers, connector prerequisites, and capability metadata
- session/profile/history/result surfaces kept separate from user-facing output
- serial phase ladders and parallel specialist fan-out with a real join step
- honest read-only, verification, and execution authority envelopes
- fail-loud security policy with explicit approval semantics
- readable markdown contracts that want tables, checklists, callouts, and
  ordered sequences rather than heading ladders

This is why the next work should still be:

- finish `analysis`
- finish `schema`
- finish `document`
- then revisit capability metadata, authority envelopes, runtime result
  surfaces, and parallel join semantics as the smallest coherent follow-on
  wave
