# Candidate Tests

## `raw/CLAUDE.md`

- Doctrine pressure: project overview, build commands, strict TypeScript posture, and prompt update workflow.
- Candidate example: a repo-level guide that tells an agent how to generate and refine prototype output.
- Candidate diagnostic: flag when a generated example forgets the repo-wide prompt update path.

## `raw/prompts/original.md`

- Doctrine pressure: single-file HTML output, allowed external resources, and red-annotation exclusion.
- Candidate example: a generic prototype prompt that turns a wireframe into a complete HTML document.
- Candidate diagnostic: warn when the response leaves out the final HTML wrapper or uses forbidden external assets.

## `raw/prompts/google-system-prompt.md`

- Doctrine pressure: input synthesis, patch-not-rewrite behavior, and model-specific execution flow.
- Candidate example: a provider prompt that treats prior HTML as a live refactor target instead of a fresh start.
- Candidate diagnostic: detect when a generated example ignores existing code and rebuilds from scratch.

## `raw/prompts/openai-system-prompt.md`

- Doctrine pressure: compact output contract plus annotation and resource filtering.
- Candidate example: a shorter provider prompt that still enforces the same HTML and responsiveness rules.
- Candidate diagnostic: flag when the prototype includes annotation content or unsupported assets.

## `raw/prompts/anthropic-system-prompt.md`

- Doctrine pressure: Tailwind-only styling, provider-import restrictions, and state handling rules.
- Candidate example: a provider-specific prompt that narrows implementation choices more aggressively than the generic prompt.
- Candidate diagnostic: warn when the generated prototype uses the wrong state or styling mechanism.

## `raw/prompts/scratchpad.md`

- Doctrine pressure: final-line contract, responsiveness from small to very large viewports, and avoidance of device mockups.
- Candidate example: a terse markdown prompt that encodes output-shape rules as hard constraints.
- Candidate diagnostic: flag an example that breaks the `</html>` terminator or adds an illustrative device frame.

## Good Doctrine Surfaces

- `runtime_provider_selection`
- `io_contracts_and_handoffs`
- `negative_guardrails`
- `commands_and_quality_gates`
- `context_and_memory`
