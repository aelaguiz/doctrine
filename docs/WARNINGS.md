# Warnings

Doctrine treats fail-loud errors as the default.
Some authoring shapes compile cleanly today but still push against the
project principles: context budget, reuse pressure, narrow typed-truth
shadowing, weak load boundaries.

A first-class warning layer would flag those shapes without turning the
compiler into a second harness or a style linter.

This doc is the evergreen landing page for that work.
No warning codes ship in the compiler today.
The [agent-linter skill](AGENT_LINTER.md) is the current home for
judgment-first authoring review.

## Goals

- Give authors early, clear guidance on valid-but-bad authoring.
- Reuse the existing source spans, codes, and diagnostic formatting.
- Stay inside the authoring pipeline: parser, index, resolve, validate,
  compile, render, emit.
- Prove every shipped warning against the shipped corpus.

## Non-Goals

Doctrine warnings should not own any of these:

- A second semantic model or parallel authoring graph.
- An LLM judge, vibe-based lint, or prose-taste grading.
- Host-repo policy (run layout, allow-lists, sidecar naming).
- Runtime state, memory, scheduling, or tool orchestration.
- Style, tone, or "good writing" scoring.

If the compiler can prove a shape is semantically wrong, the long-term
home is an error in [COMPILER_ERRORS.md](COMPILER_ERRORS.md), not a
warning.

## Candidate First-Wave Families

These are the families most aligned with Doctrine principles. They are
candidates, not shipped codes.

- **Context budget.** A concrete agent renders an unusually large
  always-on home, or a local section carries a very large prose block.
- **Reuse pressure.** Normalized prose, step lists, or typed scaffolds
  repeat across agents or modules in one compile graph.
- **Narrow semantic shadowing.** One agent carries review or route
  control meaning twice through separate authored surfaces.
- **Transition fail-loud bridge.** A proven gap from
  [FAIL_LOUD_GAPS.md](FAIL_LOUD_GAPS.md) still compiles in a way that
  looks valid, and a hard error cannot land yet.

## Families To Keep Out

- Tone, voice, or "good writing" scoring.
- Generic naming taste across all declarations.
- Product-specific sidecar or repo-local rules.
- Flow-aware runtime checks.
- Content correctness that needs domain judgment.
- Warnings on authoring comments or emitted artifacts.

## Guardrails For Any Shipped Warning

Before a warning ships by default, each answer must be yes:

1. Can Doctrine prove the signal from its own graph?
2. Is the fix a Doctrine authoring change?
3. Is the rule generic across repos?
4. Can the warning point to one owner path and one likely fix?
5. Is the false-positive risk low?
6. Would a better model tomorrow still need this structural guidance?
7. If the shape is actually wrong, why is this not an error yet?

If any answer is weak, do not ship the warning by default.

## Related

- [AGENT_LINTER.md](AGENT_LINTER.md): the judgment-first review skill
  that covers the same principle pressure today.
- [FAIL_LOUD_GAPS.md](FAIL_LOUD_GAPS.md): easy author mistakes the
  compiler still accepts. Some may earn a warning bridge before they
  become hard errors.
- [COMPILER_ERRORS.md](COMPILER_ERRORS.md): canonical error catalog.
  Shipped warnings will land alongside errors in the same catalog.
