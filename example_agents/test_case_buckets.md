# Test Case Buckets

These buckets are the shared classification system for harvested instruction
files.

Use them in `inventory.toml`, `SOURCE.toml`, and `candidate_tests.md` so we can
find good source material quickly.

| Bucket | Pull From Sources That Show | Likely Doctrine Targets |
| --- | --- | --- |
| `scope_hierarchy` | root vs subdirectory instruction precedence, layered repo guidance, scoped overrides | inheritance, explicit patching, scoped docs examples, AGENTS precedence notes |
| `commands_and_quality_gates` | concrete build commands, lint/type/test gates, release checks, must-run verification | typed skills or authored command sections, examples that prove command-first doctrine, docs on verification expectations |
| `negative_guardrails` | explicit "do not do X" rules, hard limits, forbidden edits, safety rails | fail-loud examples, stop/reroute phrasing, narrow guardrail sections, review examples |
| `io_contracts_and_handoffs` | required outputs, handoff summaries, standalone-read rules, pickup contracts | `output`, `trust_surface`, handoff truth, portable currentness, invalidation |
| `skills_tools_and_capabilities` | named tools, MCP use, capability lists, when-to-use guidance | `skill`, `skills` blocks, tool requirement surfaces, skills inheritance examples |
| `context_and_memory` | re-read instructions after compaction, memory bank rules, context reset patterns, lessons learned | authored context-management examples, future memory or skill docs, negative examples for stale context habits |
| `orchestration_roles_and_delegation` | specialized agent teams, handoffs, manager-worker patterns, role directories | routing, handoffs, abstract agents, role-home composition, future workflow-law examples |
| `domain_specific_constraints` | platform matrices, security restrictions, legal/medical/trading boundaries, environment-specific commands | typed inputs/outputs, enum vocabularies, domain guardrail examples, docs pressure for future surfaces |
| `archive_and_curation_sources` | aggregators, prompt archives, awesome lists, system prompt dumps | source discovery only; usually not a direct Doctrine example until a concrete upstream file is harvested |

## Extraction Heuristic

When a source hits more than one bucket, prefer the bucket that gives the
cleanest Doctrine test case with the fewest repo-specific details.

Examples:

- A monorepo with nested AGENTS files is usually `scope_hierarchy` first, even
  if it also contains many build commands.
- A docs repo with hard MDX syntax limits is usually `negative_guardrails`
  first, even if it also lists build commands.
- A multi-agent SDK with instructions, tools, and handoffs is usually
  `orchestration_roles_and_delegation` first if the role split is the main new
  signal.
