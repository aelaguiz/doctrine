# Candidate Tests

## `raw/CLAUDE.md`

- Doctrine pressure: monorepo structure, commands, code conventions, and porting rules.
- Candidate example: a root instruction file that front-loads build/test commands and then narrows behavior for agents, plugins, and time units.
- Candidate diagnostic: flag when a nested example ignores the root build or release gates.

## `raw/README.md`

- Doctrine pressure: framework overview, plugin capability table, and agent/session terminology.
- Candidate example: a repo README that explains the core runtime and enumerates provider support in one place.
- Candidate diagnostic: warn when a child example contradicts the capability matrix or session model.

## `raw/CONTRIBUTING.md`

- Doctrine pressure: contribution workflow, SPDX compliance, docs requirements, and release hygiene.
- Candidate example: an instruction file that tells agents when to add SPDX headers, run formatting, and avoid touching manifests directly.
- Candidate diagnostic: flag code changes that skip the documented contribution gates.

## `raw/agents/README.md`

- Doctrine pressure: package-level summary for the main SDK surface.
- Candidate example: a nested README that defines a package identity without repeating the entire root guide.
- Candidate diagnostic: detect when package-local instructions get ignored in favor of the root summary.

## `raw/plugins/openai/README.md`

- Doctrine pressure: provider capability selection across LLM, STT, TTS, Realtime, and Responses.
- Candidate example: a provider README that states the exact surfaces a plugin supports.
- Candidate diagnostic: warn if an example assumes a capability that the plugin README does not advertise.

## `raw/plugins/elevenlabs/README.md`

- Doctrine pressure: narrow provider capability surface for voice synthesis.
- Candidate example: a plugin README that constrains the agent to a single capability family.
- Candidate diagnostic: flag tests that overgeneralize a narrow plugin into a broader multi-modal provider.

## Good Doctrine Surfaces

- `scope_hierarchy`
- `commands_and_quality_gates`
- `negative_guardrails`
- `orchestration_roles_and_delegation`
- `io_contracts_and_handoffs`
