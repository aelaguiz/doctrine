# Warnings

Doctrine treats fail-loud errors as the default.
Some valid authoring shapes still signal likely drift. Doctrine uses warnings
for those cases when a hard error would be too strict.

Doctrine currently ships graph-scoped warnings for `skill_graph` policy lines.
Warnings are emitted into graph contracts and graph Markdown. They do not fail
compile by themselves.
The [agent-linter skill](AGENT_LINTER.md) is the current home for
judgment-first authoring review.

## Shipped Graph Warnings

These warnings only run when a graph opts in with a matching `warn <key>`
policy line.

| Code | Policy key | Meaning |
| --- | --- | --- |
| `W201` | `orphan_stage` | A visible stage is not reached from this graph's roots. |
| `W202` | `orphan_skill` | A visible skill is not reached from a stage, relation, or checked skill mention. |
| `W203` | `stage_owner_shared` | One skill owns more than one reached stage. |
| `W204` | `checked_skill_mention_unknown` | A checked skill mention does not resolve, and strict checked mentions are off. |
| `W205` | `branch_coverage_incomplete` | A graph allowed an enum branch source that does not cover every enum member. |
| `W206` | `receipt_without_consumer` | A reached receipt is not read by a reached stage input or recovery ref. |
| `W207` | `flow_without_approve` | A reached flow has no `approve:` flow. |
| `W208` | `stage_without_risk_guard` | A reached stage has no `risk_guarded:` field. |
| `W209` | `edge_route_binding_missing` | `allow unbound_edges` let a routed edge compile without `route:`. |
| `W210` | `relation_without_reason` | A skill relation has no `why:` and `require relation_reason` is off. |
| `W211` | `manual_only_default_flow_conflict` | A reached skill is marked both manual-only and a default flow member. |

Graph warning `owner` fields use the public declaration name. They do not carry
a module path. When two modules use the same public name, the warning detail
must say which local graph-entrypoint declaration is not reached and which
imported declaration was reached instead.

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

## Future Candidate Families

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
  Error codes live there. Shipped graph warning codes are listed in this file.
