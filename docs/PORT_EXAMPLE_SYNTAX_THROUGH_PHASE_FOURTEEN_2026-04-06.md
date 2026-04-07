---
title: "pyprompt - Port Example Syntax Through Phase Fourteen - Architecture Plan"
date: 2026-04-06
status: complete
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: [aelaguiz]
doc_type: parity_plan
related:
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/COMPILER_ERRORS.md
  - docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md
  - examples/07_handoffs/prompts/AGENTS.prompt
  - examples/08_inputs/prompts/AGENTS.prompt
  - examples/09_outputs/prompts/AGENTS.prompt
  - examples/10_turn_outcomes/prompts/AGENTS.prompt
  - examples/11_skills_and_tools/prompts/AGENTS.prompt
  - examples/12_role_home_composition/prompts/AGENTS.prompt
  - examples/13_critic_protocol/prompts/AGENTS.prompt
  - examples/14_handoff_truth/prompts/AGENTS.prompt
---

# TL;DR

- Outcome: Extend the shipped `pyprompt` grammar, parser, model, compiler, renderer, and corpus verifier so the approved language surface through examples `07` to `14` is implemented cleanly, verified explicitly, and documented as shipped behavior.
- Problem: The shipped subset had stopped at `06`, while examples `07` to `14` introduced new declaration families and agent-field patterns that were still partly draft pressure, partly real language intent, and not safe to encode blindly.
- Approach: Treat examples `07` to `14` as design pressure rather than truth, extract the real syntax families they are testing, stop for explicit decisions when a draft is ambiguous or self-contradictory, and only then port the approved constructs into one clean fail-loud compiler path.
- Plan: First inventory and lock the post-`06` syntax families, then generalize the agent/declaration model, then port new constructs in example order with manifest-backed verification, and finally expand the active corpus through `14` while syncing docs and error guidance.
- Non-negotiables: `pyprompt/` remains shipped truth, handwritten `AGENTS.md` refs are not authority, `99` contributes no patterns, no speculative primitives are added to rescue bad drafts, no parallel grammar paths or fallbacks are introduced, and ambiguity triggers a design decision instead of a hack.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-06
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-06
external_research_grounding: not started
deep_dive_pass_2: not started
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

We can extend the shipped language from the current `01` to `06` subset to a clean, explicit, fail-loud `01` to `14` subset by implementing only the post-`06` constructs that survive design review, rejecting or rewriting draft mistakes instead of encoding them, and proving the result with checked-in manifests plus a passing `make verify-examples` corpus run.

## 0.2 In scope

- Port the syntax pressure introduced by examples `07_handoffs` through `14_handoff_truth` into the shipped path under [pyprompt/grammars/pyprompt.lark](/Users/aelaguiz/workspace/pyprompt/pyprompt/grammars/pyprompt.lark), [pyprompt/parser.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/parser.py), [pyprompt/model.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/model.py), [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py), [pyprompt/renderer.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/renderer.py), and [pyprompt/verify_corpus.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/verify_corpus.py).
- Generalize the agent shape beyond the current exact `role` then `workflow` subset so typed agent-local fields and named role-home composition can be expressed without inventing a second semantic model.
- Port the new declaration families and field families that appear after `06`, including the draft surfaces around routes, inputs, outputs, outcomes, skills, and imported role-by-concern file splits, but only after deciding which parts are real language primitives versus draft noise.
- Add or revise manifests for the approved `07` to `14` examples so the active corpus proves the shipped subset instead of relying on handwritten `ref` output.
- Update live docs when implementation and docs drift, especially [docs/LANGUAGE_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/LANGUAGE_DESIGN_NOTES.md) and [docs/COMPILER_ERRORS.md](/Users/aelaguiz/workspace/pyprompt/docs/COMPILER_ERRORS.md).
- Stop and surface explicit decision points whenever an example draft, comment, or handwritten ref implies a dubious or conflicting grammar rule.

## 0.3 Out of scope

- Treating `examples/*/ref/**/AGENTS.md` as authoritative proof of the language.
- Pulling language patterns from [examples/99_not_clean_but_useful](/Users/aelaguiz/workspace/pyprompt/examples/99_not_clean_but_useful).
- Porting syntax past `14`, inventing speculative primitives not earned by the examples, or promoting repo-specific workarounds like raw script paths into first-class language surface.
- Adding compatibility shims, silent fallback parse paths, or duplicate compiler flows just to keep draft syntaxes alive.
- Preserving a draft example unchanged when the cleaner move is to repair the example, narrow the construct, or ask for a decision.

## 0.4 Definition of done (acceptance evidence)

- The approved `07` to `14` syntax families are explicitly named in the plan and reflected in shipped code, not inferred from comments or refs.
- New or revised manifests exist for the example directories that become part of the shipped subset, and `make verify-examples` passes for the full active corpus.
- Existing `01` to `06` behavior still passes unchanged after the refactor work needed to support post-`06` constructs.
- Docs state clearly which post-`06` features are shipped, which draft ideas were rejected or deferred, and why.
- Any example-draft ambiguity encountered during the port was resolved explicitly with a recorded decision instead of quietly encoded as grammar.

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks or runtime shims.
- No dual grammar or compiler paths for old versus new examples.
- No draft `AGENTS.md` ref output treated as truth over shipped code.
- No `99`-driven pattern import.
- No new primitive added just to rescue a weak example when current primitives can express the intent cleanly.
- No silent behavior drift for `01` to `06` while making the model more general.
- No ambiguous draft syntax merged without a stop-and-decide checkpoint.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Keep the language and compiler semantics clean, explicit, and defensible.
2. Surface draft mistakes and open design questions early instead of encoding them as shipped behavior.
3. Preserve the already-shipped `01` to `06` subset while widening the model.
4. Keep the example sequence disciplined so each new construct earns its place.
5. Expand verification only where the shipped subset has actually been earned.

## 1.2 Constraints

- The shipped subset is still intentionally explicit and manifest-backed.
- Examples `07` to `14` started as drafts and needed manifest-backed proof before they could count as shipped truth.
- Handwritten refs can contain mistakes.
- The current docs already reject `99` as a design source and reject raw script paths as a first-class language surface.
- The parser/compiler should fail loudly rather than guess.

## 1.3 Architectural principles (rules we will enforce)

- `pyprompt/` is the shipped source of truth.
- Example drafts can propose syntax, but only manifests plus shipped compiler behavior can prove it.
- One semantic model per concept: no special ad hoc model for inline versus reusable versus inherited post-`06` structure.
- Prefer typed declarations and typed agent fields over magic strings or implicit rendering rules.
- Preserve example order as the driver for parser growth.
- Ask for a decision when a draft is ambiguous enough that two clean grammars are plausible.

## 1.4 Known tradeoffs (explicit)

- Stopping for design checkpoints slows raw implementation speed, but it prevents grammar debt and false canon.
- Generalizing agent fields will likely require deeper internal refactoring than a one-off syntax patch, but that is the cleaner long-term move.
- Some example drafts may need to be rewritten or narrowed before they can become verified shipped truth.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

The shipped parser/compiler now proves examples `01` through `14`. The
canonical path in `pyprompt/` supports the widened declaration set, authored
workflow slots, typed I/O and skill contracts, routed outcomes, and split
imports, while preserving the legacy `01` to `06` behavior and fail-loud
boundaries.

## 2.2 What’s broken / missing (concrete)

Before this port:
- examples `07` to `14` relied on agent-local named slots and typed fields that
  the shipped AST and compiler could not represent
- declaration families such as `input`, `input source`, `output`, `output target`,
  `output shape`, `json schema`, and `skill` did not exist in shipped code
- route-bearing outcome structures appeared after `06`, but the grammar only
  knew workflow items and flat role/workflow agent fields
- the draft examples mixed settled intent with exploratory wording, so a literal
  port would have encoded mistakes alongside real design decisions

## 2.3 Constraints implied by the problem

- We cannot use handwritten refs as the acceptance oracle for post-`06` work.
- We need a design-aware port, not a syntax scrape.
- The internal model likely needs one controlled widening so later fields and declarations reuse shared compiler machinery instead of adding per-example hacks.

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- None required for this step. Reject generic DSL prior-art research for now because the repo’s own design notes and draft examples already constrain the next language moves more tightly than outside analogies would.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - [pyprompt/grammars/pyprompt.lark](/Users/aelaguiz/workspace/pyprompt/pyprompt/grammars/pyprompt.lark#L14) — the shipped grammar now covers the widened declaration set through `skill`, plus reserved typed agent fields and open authored workflow slots.
  - [pyprompt/model.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/model.py#L74) — the shipped AST now carries typed declaration families and ordered agent fields beyond the original `role` plus `workflow` subset.
  - [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py#L97) — the shipped compiler now routes reserved typed fields and authored workflow slots through one canonical compilation path instead of the old exact-two-field gate.
  - [pyprompt/verify_corpus.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/verify_corpus.py#L149) — the proof surface is still manifest-backed, and the active corpus now runs through `examples/14_handoff_truth`.
- Canonical path / owner to reuse:
  - [pyprompt/](/Users/aelaguiz/workspace/pyprompt/pyprompt) — the one shipped grammar/parser/model/compiler/rendering path that must own the port.
  - [examples/*/cases.toml](/Users/aelaguiz/workspace/pyprompt/examples/01_hello_world/cases.toml#L1) plus [pyprompt/verify_corpus.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/verify_corpus.py#L89) — the canonical proof surface for what is actually shipped.
- Existing patterns to reuse:
  - [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py#L254) — explicit exhaustive inheritance and fail-loud keyed patching are already the canonical merge model.
  - [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py#L146) and [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py#L465) — import resolution and qualified reference lookup already exist and should be reused for split-by-concern modules in `14`.
  - [docs/LANGUAGE_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/LANGUAGE_DESIGN_NOTES.md#L98) — nested, reusable, and inherited structure should stay on named top-level `workflow` declarations rather than spawning a second deep-tree model.
- Prompt surfaces / agent contract to reuse:
  - [examples/07_handoffs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/07_handoffs/prompts/AGENTS.prompt#L1) — route-bearing workflow sections plus the first pressure for agent-local named slots.
  - [examples/08_inputs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/08_inputs/prompts/AGENTS.prompt#L1) — typed `input` and `input source` pressure with explicit `source`, `shape`, and `requirement`.
  - [examples/09_outputs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/09_outputs/prompts/AGENTS.prompt#L1) — `output`, `output target`, `output shape`, and `json schema` pressure.
  - [examples/10_turn_outcomes/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/10_turn_outcomes/prompts/AGENTS.prompt#L1) — `outcome` as a turn-resolution layer distinct from `output`.
  - [examples/11_skills_and_tools/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/11_skills_and_tools/prompts/AGENTS.prompt#L1) — `skill` declarations plus agent-side skill references and metadata.
  - [examples/12_role_home_composition/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/12_role_home_composition/prompts/AGENTS.prompt#L1) — role-home composition pressure using named agent slots without introducing a new primitive.
  - [examples/13_critic_protocol/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/13_critic_protocol/prompts/AGENTS.prompt#L1) — critic protocol pressure expressed with inputs, outputs, outcomes, skills, and support prose instead of a critic-specific primitive.
  - [examples/14_handoff_truth/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/14_handoff_truth/prompts/AGENTS.prompt#L1) — split-by-concern file layout and handoff-truth pressure using the existing import model.
- Native model or agent capabilities to lean on:
  - Not a runtime-model capability problem. This step is DSL/compiler design, so the right leverage is repo evidence plus manifest-backed verification, not new agent harnesses or wrappers.
- Existing grounding / tool / file exposure:
  - `uv sync` and `make verify-examples` — current environment and full shipped-subset proof loop; both passed during this research step.
  - `uv run --locked python -m pyprompt.verify_corpus --manifest <path>` — targeted proof loop for each example band as it becomes earned.
  - [docs/COMPILER_ERRORS.md](/Users/aelaguiz/workspace/pyprompt/docs/COMPILER_ERRORS.md#L1) — stable numbered error doctrine that should expand only when post-`06` failure modes are actually shipped.
- Duplicate or drifting paths relevant to this change:
  - `examples/*/ref/**/AGENTS.md` under `07` to `14` — handwritten output pressure only; not authoritative proof.
  - [docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md](/Users/aelaguiz/workspace/pyprompt/docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md#L41) — flags that the apparent H1 renderer shift in `07` refs is underexplained and should not be canonized silently.
  - [docs/LANGUAGE_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/LANGUAGE_DESIGN_NOTES.md#L253) — rendered file-name mapping and multi-agent output from one package are still explicitly pending.
  - [examples/99_not_clean_but_useful](/Users/aelaguiz/workspace/pyprompt/examples/99_not_clean_but_useful) and `99`-derived audits — valid pressure surfaces only; not grammar blueprints.
- Capability-first opportunities before new tooling:
  - [docs/AGENT_IO_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/AGENT_IO_DESIGN_NOTES.md#L44) — inputs already have a clear source-vs-shape-vs-requirement doctrine; we do not need a packet layer to move forward.
  - [docs/AGENT_IO_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/AGENT_IO_DESIGN_NOTES.md#L321) — outputs are already narrowed to one primitive plus subordinate declarations; we do not need a competing `artifact` concept.
  - [docs/LANGUAGE_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/LANGUAGE_DESIGN_NOTES.md#L224) and [docs/LANGUAGE_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/LANGUAGE_DESIGN_NOTES.md#L346) — reusable capability should stay skill-first; do not invent `runtime_tools`.
  - [docs/LANGUAGE_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/LANGUAGE_DESIGN_NOTES.md#L240) — handoff truth already has a clean non-packet direction; do not invent freshness or packet machinery unless a later example truly forces it.
- Behavior-preservation signals already available:
  - `make verify-examples` — preserves shipped `01` to `06` behavior during the core model widening.
  - Targeted manifest runs — preserve each newly earned example band without forcing the whole `07` to `14` draft surface live at once.

Post-`06` syntax inventory grounded by repo evidence:

- `07` introduces two real pressures: agent-local named slots beyond `role` plus `workflow`, and `route "..." -> AgentName` lines inside reusable workflow structure ([examples/07_handoffs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/07_handoffs/prompts/AGENTS.prompt#L42), [examples/07_handoffs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/07_handoffs/prompts/AGENTS.prompt#L106)).
- `08` introduces `input`, `input source`, and agent `inputs:` fields, with source-specific nested configuration and explicit required-versus-advisory semantics ([examples/08_inputs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/08_inputs/prompts/AGENTS.prompt#L13), [examples/08_inputs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/08_inputs/prompts/AGENTS.prompt#L47)).
- `09` introduces `output`, `output target`, `output shape`, `json schema`, and agent `outputs:` fields; docs already settle that `output` is the produced-contract primitive and that path roots stay plain strings ([examples/09_outputs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/09_outputs/prompts/AGENTS.prompt#L15), [docs/AGENT_IO_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/AGENT_IO_DESIGN_NOTES.md#L323), [docs/AGENT_IO_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/AGENT_IO_DESIGN_NOTES.md#L385)).
- `10` introduces agent-local `outcome` as a separate turn-resolution field layered on top of `inputs` and `outputs`, reusing `route` and adding explicit stop-condition structure ([examples/10_turn_outcomes/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/10_turn_outcomes/prompts/AGENTS.prompt#L101)).
- `11` introduces top-level `skill` and agent-local `skills`, with the repo explicitly favoring `skill` over any raw script or tool-path surface ([examples/11_skills_and_tools/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/11_skills_and_tools/prompts/AGENTS.prompt#L47), [docs/LANGUAGE_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/LANGUAGE_DESIGN_NOTES.md#L224)).
- `12` through `14` confirm that the basic role-home shell, critic protocol, and handoff-truth direction should be expressed by composing named workflows plus inputs/outputs/outcomes/skills, not by introducing new top-level primitives for those ideas ([docs/LANGUAGE_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/LANGUAGE_DESIGN_NOTES.md#L226), [docs/LANGUAGE_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/LANGUAGE_DESIGN_NOTES.md#L240)).

## 3.3 Open questions from research

The research step surfaced the following forks. The deep-dive resolves them with the defaults in Sections 5 and 10, so implementation should treat this list as provenance for those decisions, not as an unresolved blocker list.

- Agent-local named slots: are post-`06` agent fields an open ordered typed-field system, or a closed catalog of slot names like `read_first`, `workflow_core`, `your_job`, `how_to_take_a_turn`, `standards_and_support`, and `when_to_use_this_role`?
- Agent-slot inheritance semantics: should agent-level `inherit` / `override` follow the same exhaustive explicit patch model as workflow-body inheritance, or do inherited slots carry through unless mentioned?
- Route semantics: is `route "..." -> AgentName` the canonical primitive to ship now, and if so, is it just structured authored text inside workflows/outcomes or the first real role-graph primitive?
- Renderer contract for multi-agent packages: keep the current role-first opening used by shipped `01` to `06`, or switch to the H1 agent-name opening implied by some handwritten refs?
- Input shape identity: are names like `MarkdownDocument`, `DirectoryPath`, `JsonObject`, and `DesignDocument` built-in type names, future declarations, or validated labels only?
- Output multiplicity: should `files:` remain real `output` grammar, or should the language stay single-target and treat extra files as support surfaces?
- Closed versus open child fields: which children under `input`, `input source`, `output`, `output shape`, `output target`, `skill`, `skills`, and `outcome` are real grammar keywords versus open authored sections?
- Skill-reference buckets: are `can_run`, `discover_with`, and `not_for_this_role` fixed language buckets, or just the current example’s headings around a more general skill-reference surface?
<!-- arch_skill:block:research_grounding:end -->

# 4) Current Architecture (as-is)

<!-- arch_skill:block:current_architecture:start -->
## 4.1 On-disk structure

This section records the pre-port baseline the implementation started from.

At the start of this port, the shipped implementation lived in one narrow
canonical path:

- grammar in [pyprompt/grammars/pyprompt.lark](/Users/aelaguiz/workspace/pyprompt/pyprompt/grammars/pyprompt.lark)
- parse lowering in [pyprompt/parser.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/parser.py)
- AST model in [pyprompt/model.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/model.py)
- compilation and import resolution in [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py)
- markdown rendering in [pyprompt/renderer.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/renderer.py)
- manifest-driven proof in [pyprompt/verify_corpus.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/verify_corpus.py)

At the start of implementation, the active proof surface ran only
[examples/01_hello_world/cases.toml](/Users/aelaguiz/workspace/pyprompt/examples/01_hello_world/cases.toml)
through
[examples/06_nested_workflows/cases.toml](/Users/aelaguiz/workspace/pyprompt/examples/06_nested_workflows/cases.toml).
`07` through `14` still existed only as prompt drafts and handwritten refs, not
as shipped contracts.

## 4.2 Control paths (runtime)

At planning time, the runtime path was simple and deliberately closed:

1. [pyprompt/parser.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/parser.py#L202) reads a `.prompt` file and lowers it into `PromptFile`.
2. [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py#L486) builds a `CompilationContext`, indexes the root module plus imports, and resolves inherited/composed workflow structure.
3. [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py#L83) compiles one concrete agent into `CompiledAgent`.
4. [pyprompt/renderer.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/renderer.py#L7) renders that compiled shape into markdown.
5. [pyprompt/verify_corpus.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/verify_corpus.py#L89) discovers manifests and runs render, parse-fail, and compile-fail contracts.

The important planning-time boundary was where the compiler enforced the current
subset. [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py#L408)
rejected any agent that was not exactly `role` followed by `workflow`, so the
parser could accept some surface forms that still failed at compile time by
design.

## 4.3 Object model + key abstractions

At planning time, the model was explicit but narrower than the post-`06`
language pressure:

- [pyprompt/model.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/model.py#L97) defines `Declaration` as only `ImportDecl | WorkflowDecl | Agent`.
- [pyprompt/model.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/model.py#L86) defines `Field` as only `RoleScalar | RoleBlock | WorkflowBody`.
- [pyprompt/model.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/model.py#L67) defines workflow composition items only as local sections, `use`, `inherit`, and `override`.
- [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py#L22) fixes `CompiledAgent` to `name`, `role`, and `workflow`.
- [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py#L28) fixes `IndexedUnit` to imports, workflows, agents, and imported units only.

The reusable strength to preserve was the explicit ordered patch engine in
[pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py#L254).
The blocking limitation was that the model assumed all rich reusable structure
was workflow structure, which stopped being true once `07` to `14` introduced
typed contracts and open agent-local slots.

## 4.4 Observability + failure behavior today

At planning time, failure behavior was already clean and mostly correct for the
shipped subset. Today, the shipped path is more explicit:

- parse failures surface as structured `ParseError` diagnostics via [pyprompt/parser.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/parser.py#L289)
- compile failures surface as structured [CompileError](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py#L1774) diagnostics
- manifest proof classifies only `render_contract`, `parse_fail`, and `compile_fail` in [pyprompt/verify_corpus.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/verify_corpus.py#L233)
- `make verify-examples` was the behavior-preservation signal and passed for
  `01` through `06`

There were two meaningful planning-time limits:

- the renderer only knows prose openings plus recursive titled sections, so richer draft refs after `06` are not proof of shipped behavior
- [pyprompt/verify_corpus.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/verify_corpus.py#L94) exposes a `surfaced_inconsistencies` lane, but the current verifier does not meaningfully populate it yet, so drift detection is narrower than the report shape suggests

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable as UI work. At planning time, the visible contract was markdown
with a role-first opening and headed nested sections beneath it.
<!-- arch_skill:block:current_architecture:end -->

# 5) Target Architecture (to-be)

<!-- arch_skill:block:target_architecture:start -->
## 5.1 On-disk structure (future)

The canonical owner path stays in `pyprompt/`. The future structure should widen that existing path rather than introduce side systems:

- [pyprompt/grammars/pyprompt.lark](/Users/aelaguiz/workspace/pyprompt/pyprompt/grammars/pyprompt.lark) grows the closed declaration and field surface through `14`
- [pyprompt/parser.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/parser.py) lowers explicit typed declarations, explicit typed agent fields, and the new route leaf item
- [pyprompt/model.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/model.py) holds the widened declaration union, ordered agent-field union, and two internal body families
- [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py) remains the one semantic owner for resolution, inheritance, and compilation
- [pyprompt/renderer.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/renderer.py) renders the widened compiled agent shape without introducing a second visible document mode
- `examples/07_*` through `examples/14_*` gain adjacent `cases.toml` manifests only as each example band becomes earned

## 5.2 Control paths (future)

The future runtime path should still be one straight line, just with a wider intermediate model:

1. parse the approved top-level declarations and ordered agent-local fields
2. index declarations by kind inside one `IndexedUnit`-style module registry
3. resolve authored workflow-slot inheritance through the existing explicit patch engine
4. resolve typed declaration references for inputs, outputs, skills, routes, shapes, targets, and schemas through the same module/import spine
5. compile agents into an ordered rendered field sequence instead of a hardcoded role-plus-workflow pair
6. render that sequence with the existing role-first visible contract
7. verify behavior through manifests, targeted fail cases, and the existing corpus runner

The important design choice is that there is still one compiler path and one verifier path. This port should not introduce a second proof system, a second renderer mode, or a second import mechanism.

## 5.3 Object model + abstractions (future)

The target model through `14` is:

- a closed top-level declaration set: `import`, `workflow`, `agent`, `abstract agent`, `input`, `input source`, `output`, `output target`, `output shape`, `json schema`, and `skill`
- an ordered typed agent-field union with reserved field families for `role`, `inputs`, `outputs`, `outcome`, and `skills`
- open authored workflow-slot keys for reusable instruction sections such as `read_first`, `workflow_core`, `your_job`, `how_to_take_a_turn`, `standards_and_support`, and `when_to_use_this_role`
- two internal body families:
  - workflow-composition bodies for named reusable instruction structure, plus a typed `route` leaf item
  - record-like contract bodies for declarations and reserved typed fields
- one indexed module registry with kind-specific declaration maps

Key semantic defaults that this model must encode:

- authored workflow slots, not typed contract fields, get explicit `inherit key` and `override key` behavior through `14`
- `input.source` resolves built-ins or declared `input source`
- `output.target` resolves built-ins or declared `output target`
- `output.shape` resolves declared shapes first, then bare built-in labels
- input `shape` stays a bare symbolic label through this port
- `output` supports either `target + shape` or `files`, and ambiguous mixes fail loudly
- skill buckets stay authored and open, while direct skill-reference metadata like `requirement` and `reason` stays typed

## 5.4 Invariants and boundaries

The future architecture must preserve these boundaries:

- `pyprompt/` stays the only shipped owner path
- no packets, no `runtime_tools`, no handoff-truth primitive, no critic primitive, and no root-binding primitive are introduced in this plan
- no H1 agent-name renderer switch is introduced in this plan
- no second structured-proof oracle or document-IR rewrite is introduced in this plan
- support prose such as `must_include`, `support_files`, `owns`, `standalone_read`, `notes`, `path_notes`, `use_when`, and `does_not` stays pass-through authored structure unless a later example truly earns stronger semantics
- missing names, duplicate names, ambiguous output contracts, undefined inherits/overrides, and invalid route targets fail loudly
- `01` through `06` stay behavior-stable while the widened model lands

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable as UI work. The visible markdown contract remains role-first. Authored workflow slots and reserved typed fields render in authored order as titled sections, and `route` remains local content inside those sections rather than becoming a standalone role-graph appendix.
<!-- arch_skill:block:target_architecture:end -->

# 6) Call-Site Audit (exhaustive change inventory)

<!-- arch_skill:block:call_site_audit:start -->
## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Grammar | `pyprompt/grammars/pyprompt.lark` | `declaration` | Closed to `import`, `workflow`, `agent`, `abstract agent` | Add the approved declaration families through `14` | Parser cannot see post-`06` syntax at all | Closed expanded declaration set | `make verify-examples`, new manifests |
| Grammar | `pyprompt/grammars/pyprompt.lark` | `agent_field` | Closed to `role_field | workflow_field` | Replace with ordered typed agent-field grammar plus authored workflow-slot operations | `07`, `12`, `13`, and `14` need named slots and typed contract fields | Reserved typed fields plus open authored slot keys | `make verify-examples`, new manifests |
| Grammar | `pyprompt/grammars/pyprompt.lark` | `workflow_item`, `block_lines` | Only prose strings and workflow composition items | Add `route` where earned and add record-like bodies for declarations and typed fields | Route lines and typed contracts are impossible today | Workflow body plus record body family | `make verify-examples`, targeted manifests |
| Parse layer | `pyprompt/parser.py` | `ToAst.agent`, `ToAst.abstract_agent` | Collects untyped field tuple | Emit explicit typed agent-field nodes and authored slot ops | Compiler must stop inspecting by incidental Python type | Ordered typed agent field list | `make verify-examples`, targeted manifests |
| Parse layer | `pyprompt/parser.py` | declaration lowering methods | Only import/workflow/agent lowering exists | Add lowering for `input`, `input source`, `output`, `output target`, `output shape`, `json schema`, and `skill` | New syntax needs explicit AST ownership | Typed declaration nodes | `make verify-examples`, targeted manifests |
| Parse layer | `pyprompt/parser.py` | workflow / body lowering | Workflow body only supports prose and workflow composition | Add route lowering and record-body lowering | Examples need structured non-workflow content | Two body families with typed leaf items | `make verify-examples`, targeted manifests |
| Model | `pyprompt/model.py` | `Field` alias | Only `RoleScalar | RoleBlock | WorkflowBody` | Replace with explicit agent-field union | Prevent accidental ad hoc semantics | Reserved field nodes plus authored workflow-slot nodes | `make verify-examples`, targeted manifests |
| Model | `pyprompt/model.py` | `Declaration` alias | Only import/workflow/agent | Expand to the approved top-level declaration set | Compiler indexing must remain kind-aware and explicit | Closed expanded declaration union | `make verify-examples`, targeted manifests |
| Model | `pyprompt/model.py` | workflow item types | No route or record-body leaf types | Add route item and record-body node family | Needed for `07` to `14` without abusing strings | Typed route plus contract-record nodes | `make verify-examples`, targeted manifests |
| Compiler | `pyprompt/compiler.py` | `CompiledAgent` | Fixed to `role` and `workflow` | Replace with ordered rendered field/section representation | Post-`06` agents are not one workflow after role | Ordered rendered field sequence | Manifest render contracts |
| Compiler | `pyprompt/compiler.py` | `IndexedUnit` and `_index_unit()` | Indexes imports, workflows, agents only | Add kind-specific registries for new declarations | Needed for reference resolution and fail-loud validation | One indexed unit with explicit registries | `make verify-examples`, targeted manifests |
| Compiler | `pyprompt/compiler.py` | `_split_agent_fields()` | Rejects everything outside exact role+workflow | Replace with agent-field validation and field-family compilation | Current subset gate is too narrow | Reserved field validation plus authored slot validation | `make verify-examples`, targeted manifests |
| Compiler | `pyprompt/compiler.py` | `_resolve_agent_workflow()` | Resolves only inherited workflow field | Replace with authored workflow-slot resolution on agents | `07` and `12` need slot inheritance, not just one workflow | Explicit patching for authored slots | `make verify-examples`, targeted manifests |
| Compiler | `pyprompt/compiler.py` | `_resolve_workflow_body()` | Strong explicit patching algorithm for workflows | Reuse for authored workflow slots; extend leaf set carefully | This is the best shipped merge model already | Shared explicit patch logic | `make verify-examples`, targeted manifests |
| Compiler | `pyprompt/compiler.py` | `_resolve_workflow_target()`, `_load_module()`, `_resolve_import_path()` | Already resolve imports and workflow refs fail-loudly | Reuse, not replace; widen to other declaration references as needed | `14` wants split-by-concern files on the same import model | Common resolution spine across declaration kinds | `make verify-examples`, targeted manifests |
| Compiler | `pyprompt/compiler.py` | new typed compilers | Does not exist | Add compilers for inputs, outputs, outcome, skills, and new declarations | Post-`06` semantics must live in code, not in rendering guesses | Kind-specific compile contracts | `make verify-examples`, targeted manifests |
| Renderer | `pyprompt/renderer.py` | `render_markdown()` | Renders role plus one workflow tree | Render ordered field sequence while keeping current role-first opening | New agent shape must render without changing the visible contract casually | Stable role-first renderer through `14` | Manifest render contracts |
| Renderer | `pyprompt/renderer.py` | `_render_section()` | Only titled section tree with prose preamble | Extend or add helpers for record sections and route lines | Inputs/outputs/skills/outcome need coherent rendering | Stable titled-section and route rendering | Manifest render contracts |
| Corpus verification | `pyprompt/verify_corpus.py` | `verify_corpus()` and manifest loading | Already correct for manifest-backed proof | Prefer no code changes unless implementation proves a missing capability | Harness already matches repo doctrine | Existing manifest-backed oracle | `make verify-examples` |
| Docs | `docs/LANGUAGE_DESIGN_NOTES.md` | shipped language notes | Mixed shipped notes and pending decisions | Update with the earned declaration/field families and renderer decision | Docs must stop implying unresolved alternatives after ship | Current language truth | Manual doc read, corpus run |
| Docs | `docs/AGENT_IO_DESIGN_NOTES.md` | I/O direction notes | Working-note doctrine | Sync any locked I/O syntax that becomes shipped | Avoid design doc drift | Current I/O contract doctrine | Manual doc read |
| Docs | `docs/COMPILER_ERRORS.md` | numbered errors | Only shipped subset documented | Add only the new fail-loud error families that actually ship | Keep errors explicit, not speculative | Updated error catalog | Targeted fail cases, corpus run |
| Docs | `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md` | cold-read concerns | Flags unresolved H1/render drift | Update or retire the relevant concerns once decisions are shipped | Keep live docs current | Honest teaching story | Manual doc read |
| Examples | `examples/07_*` through `examples/14_*` | prompt sources and new manifests | Drafts with unresolved wording and no manifests | Clean draft mistakes before encoding them, add adjacent `cases.toml`, and rewrite stale header comments as examples graduate | Examples are design pressure, not authority | Verified examples instead of handwritten lore | `make verify-examples`, targeted manifests |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  [pyprompt/](/Users/aelaguiz/workspace/pyprompt/pyprompt) stays the only shipped owner path, with [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py) remaining the semantic center and [pyprompt/verify_corpus.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/verify_corpus.py) remaining the proof surface.
- Deprecated APIs (if any):
  No public API is being versioned here, but the internal exact-two-field agent assumption centered on `_split_agent_fields()` is intentionally being retired as shipped truth.
- Delete list (what must be removed):
  any H1-renderer branch, packet shim, `runtime_tools` stopgap, exact-two-field-only helper that survives after the model widening, or other draft-only rescue path introduced during porting.
- Capability-replacing harnesses to delete or justify:
  none should be introduced; a document-IR rewrite, second proof oracle, OCR-like helper stack, or any similar capability-replacing side system is out of scope for this port unless later explicitly re-approved.
- Live docs/comments/instructions to update or delete:
  [docs/LANGUAGE_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/LANGUAGE_DESIGN_NOTES.md), especially the current `Pending Decisions`, `Pending Concepts`, role-graph framing, and `Top Candidates For Next Work` sections that will overstate what remains open once this port ships.
  [docs/AGENT_IO_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/AGENT_IO_DESIGN_NOTES.md), where the old `Concrete Capability Areas To Define` and `What This Document Is Not Deciding Yet` framing was narrowed into `Post-14 Pressure Areas` and `Explicit Non-Goals For This Subset` once the minimum shipped I/O subset was locked.
  [docs/COMPILER_ERRORS.md](/Users/aelaguiz/workspace/pyprompt/docs/COMPILER_ERRORS.md), including a deliberate choice about whether `E001` and `E003` broaden from workflow-body patch failures to authored workflow-slot patch failures and whether `E002` stays the generic missing-visible-title error.
  [docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md](/Users/aelaguiz/workspace/pyprompt/docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md), especially the stale `07` inheritance description that still implies direct reassignment instead of `override read_first:`.
  [examples/07_handoffs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/07_handoffs/prompts/AGENTS.prompt), where both the prompt header and the comment above the agents were narrowed from over-broad agent-level named-slot language to authored workflow-slot language.
  [examples/09_outputs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/09_outputs/prompts/AGENTS.prompt) and [examples/13_critic_protocol/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/13_critic_protocol/prompts/AGENTS.prompt), where redundant `owns:` blocks should be pruned or justified so they stop conflicting with the settled anti-cargo-cult doctrine.
  touched `07` through `14` prompt-header comments that still describe those examples as sketches after they become shipped.
- Behavior-preservation signals for refactors:
  `make verify-examples` must keep `01` to `06` green during the model widening, and each newly earned example band should gain targeted manifest runs before it joins the active corpus.

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope |
| ---- | ------------- | ---------------- | ---------------------- | -------------- |
| Agent slot inheritance | [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py#L254) | reuse one explicit patch engine for authored workflow slots | prevents a second merge doctrine for role-home composition | include |
| Declaration resolution | [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py#L425) | one indexed-unit import and resolution spine with kind-specific registries | prevents separate loaders for inputs, outputs, skills, and imported role parts | include |
| Typed contract validation | [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py), [pyprompt/renderer.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/renderer.py) | validate only semantic core and pass through authored support prose | prevents grammar overfitting to draft headings like `must_include` and `owns` | include |
| Root and path semantics | [docs/AGENT_IO_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/AGENT_IO_DESIGN_NOTES.md), `08` to `14` examples | keep path roots as explained conventions, not declarations | prevents speculative root-binding syntax from piggybacking onto I/O work | defer |
| Proof architecture | [pyprompt/verify_corpus.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/verify_corpus.py) | do not add a second structured-proof or document-IR oracle in this port | prevents a second truth surface and a phase-14 scope blowout | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

Warn-first note: `external_research_grounding` is still not started in `planning_passes`. This plan proceeds on repo-grounded architecture only; if later external research materially changes the design, reopen Section 7 before implementation.

## Phase 1 - Widen the core model without changing shipped behavior

Status: COMPLETE

Completed work:
- Full `07` to `14` example read is complete before code changes.
- Confirmed the first real widening pressure is the mixed agent field model: legacy inherited `workflow` still needs to preserve `01` to `06`, while later examples add authored workflow slots plus typed contract fields.
- Confirmed `08` clarifies that authored workflow slots like `your_job` must support both named workflow references and inline workflow bodies.
- Shipped the widened grammar, parser, model, compiler, and renderer path without introducing a second semantic flow.
- Preserved the legacy `01` to `06` behavior, including the compile-fail guard for reordered legacy `role` and `workflow` fields.

- Goal: Replace the internal exact-two-field agent assumption with the widened declaration and field model while keeping the shipped `01` to `06` subset behavior-stable.
- Work: Expand [pyprompt/grammars/pyprompt.lark](/Users/aelaguiz/workspace/pyprompt/pyprompt/grammars/pyprompt.lark), [pyprompt/parser.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/parser.py), [pyprompt/model.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/model.py), and [pyprompt/compiler.py](/Users/aelaguiz/workspace/pyprompt/pyprompt/compiler.py) so the codebase can represent the closed top-level declaration set, ordered typed agent fields, authored workflow slots, kind-specific declaration registries, and the future `route` leaf item; preserve one compiler path, one import-resolution spine, one verifier path, and leave short code comments at the grammar and compiler boundaries explaining reserved typed fields versus authored workflow slots.
- Verification (smallest signal): `make verify-examples` stays green for the active corpus, and any temporary unsupported post-`06` constructs still fail loudly rather than silently downgrading into prose.
- Docs/comments (propagation; only if needed): Update any touched live code comments or docs that still claim agents can only ever be `role` plus `workflow`.
- Exit criteria: The shipped core can represent the widened surface through one owner path, and `01` to `06` still pass unchanged.
- Rollback: Revert the widening if it introduces a second semantic path, forces fallbacks, or regresses any active `01` to `06` manifest.

## Phase 2 - Ship authored workflow slots and narrow handoff routing for `07`

Status: COMPLETE

Completed work:
- Activated `07_handoffs` with a checked `cases.toml` contract.
- Shipped authored workflow slots on agents plus narrow `route "..." -> AgentName` lines inside workflow and outcome sections.
- Narrowed both the prompt header and the agent-body `07` slot comments so the shipped example teaches authored workflow slots precisely.

- Goal: Earn authored workflow-slot inheritance plus the narrow `route "..." -> AgentName` primitive using `07_handoffs`.
- Work: Implement authored workflow-slot fields on agents, reuse the explicit patch engine for slot-level `inherit key` and `override key`, add route parsing and route-target validation for workflow bodies, and render authored slots in authored order while keeping the current role-first opening and no H1 agent-name switch.
- Verification (smallest signal): add [examples/07_handoffs/cases.toml](/Users/aelaguiz/workspace/pyprompt/examples/07_handoffs) and run `uv run --locked python -m pyprompt.verify_corpus --manifest examples/07_handoffs/cases.toml`, then run `make verify-examples`.
- Docs/comments (propagation; only if needed): narrow the misleading comment in [examples/07_handoffs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/07_handoffs/prompts/AGENTS.prompt) so it teaches authored workflow-slot inheritance only, and update [docs/COMPILER_ERRORS.md](/Users/aelaguiz/workspace/pyprompt/docs/COMPILER_ERRORS.md) wording if `E001` and `E003` broaden with the shared patch engine in this phase.
- Exit criteria: `07` is active, verified, and taught as a clean authored-slot plus narrow-route example rather than as handwritten ref folklore.
- Rollback: Deactivate the `07` manifest and revert the slot or route slice rather than relaxing the compiler if the example still depends on draft ambiguity.

## Phase 3 - Ship input and output contract declarations for `08` and `09`

Status: COMPLETE

Completed work:
- Activated `08_inputs` and `09_outputs` with checked `cases.toml` contracts.
- Shipped `input`, `input source`, `output`, `output target`, `output shape`, and `json schema`.
- Removed the redundant `owns:` sections from `09_outputs` instead of treating them as language design.

- Goal: Earn the I/O contract layer through `input`, `input source`, `output`, `output target`, `output shape`, `json schema`, and the reserved `inputs` and `outputs` agent fields.
- Work: Implement the declaration families and resolution rules locked in Section 5, including built-in input sources `Prompt`, `File`, and `EnvVar`; built-in output targets `TurnResponse` and `File`; custom source and target declarations; symbolic input shapes; declared output shapes; strict `target + shape` versus `files` output modes; and renderer support for typed contract sections while still passing through authored support prose instead of hardcoding every draft heading.
- Verification (smallest signal): add [examples/08_inputs/cases.toml](/Users/aelaguiz/workspace/pyprompt/examples/08_inputs) and [examples/09_outputs/cases.toml](/Users/aelaguiz/workspace/pyprompt/examples/09_outputs), run `uv run --locked python -m pyprompt.verify_corpus --manifest examples/08_inputs/cases.toml --manifest examples/09_outputs/cases.toml`, then run `make verify-examples`.
- Docs/comments (propagation; only if needed): narrow [docs/AGENT_IO_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/AGENT_IO_DESIGN_NOTES.md) to the shipped minimum subset that lands here, and prune or justify redundant `owns:` sections in [examples/09_outputs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/09_outputs/prompts/AGENTS.prompt) so the example stops fighting the settled anti-cargo-cult doctrine.
- Exit criteria: `08` and `09` are active, verified, and the compiler rejects ambiguous output-contract mixes fail-loudly.
- Rollback: Revert the `08` to `09` slice rather than silently demoting `files:` to support prose or weakening the built-in versus declared resolution rules.

## Phase 4 - Ship `outcome` and `skill` semantics for `10` and `11`

Status: COMPLETE

Completed work:
- Activated `10_turn_outcomes` and `11_skills_and_tools` with checked `cases.toml` contracts.
- Shipped routed `outcome` sections and skill-first capability modeling with required-versus-advisory rendering behavior.

- Goal: Earn routed turn outcomes and skill-first capability modeling without inventing a role-graph DSL or `runtime_tools` surface.
- Work: Implement the reserved `outcome` field with route-bearing branches, stop conditions, and stop rules; implement top-level `skill` declarations and reserved `skills` agent fields with open bucket names plus typed direct-reference metadata like `requirement` and `reason`; and make the renderer enforce the current policy that required skill references become fail-loud role guidance while advisory references do not render as schema-like noise.
- Verification (smallest signal): add [examples/10_turn_outcomes/cases.toml](/Users/aelaguiz/workspace/pyprompt/examples/10_turn_outcomes) and [examples/11_skills_and_tools/cases.toml](/Users/aelaguiz/workspace/pyprompt/examples/11_skills_and_tools), run `uv run --locked python -m pyprompt.verify_corpus --manifest examples/10_turn_outcomes/cases.toml --manifest examples/11_skills_and_tools/cases.toml`, then run `make verify-examples`.
- Docs/comments (propagation; only if needed): update [docs/LANGUAGE_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/LANGUAGE_DESIGN_NOTES.md) and [docs/COMPILER_ERRORS.md](/Users/aelaguiz/workspace/pyprompt/docs/COMPILER_ERRORS.md) for the shipped route, outcome, and skill semantics that land here.
- Exit criteria: `10` and `11` are active, verified, and the shipped story remains route-narrow and skill-first.
- Rollback: Defer any bucket-specific behavior or renderer flourish that cannot be defended cleanly, but keep the core skill and outcome surfaces explicit.

## Phase 5 - Ship role-home composition and imported handoff truth for `12` to `14`

Status: COMPLETE

Completed work:
- Activated `12_role_home_composition`, `13_critic_protocol`, and `14_handoff_truth` with checked `cases.toml` contracts.
- Kept critic protocol and handoff truth on the same primitive set instead of adding a critic or freshness primitive.
- Removed the redundant `owns:` section from `13_critic_protocol`.

- Goal: Finish the phase-14 language boundary through role-home composition, critic protocol expressed with existing primitives, and split-by-concern imports for handoff truth.
- Work: Use the authored workflow-slot model plus typed fields to ship [examples/12_role_home_composition](/Users/aelaguiz/workspace/pyprompt/examples/12_role_home_composition), keep [examples/13_critic_protocol](/Users/aelaguiz/workspace/pyprompt/examples/13_critic_protocol) on the same primitive set instead of inventing a critic DSL, and ship [examples/14_handoff_truth](/Users/aelaguiz/workspace/pyprompt/examples/14_handoff_truth) through the existing import and module-resolution spine so contracts and role modules split cleanly by concern.
- Verification (smallest signal): add `cases.toml` for `12`, `13`, and `14`, run `uv run --locked python -m pyprompt.verify_corpus --manifest examples/12_role_home_composition/cases.toml --manifest examples/13_critic_protocol/cases.toml --manifest examples/14_handoff_truth/cases.toml`, then run `make verify-examples`.
- Docs/comments (propagation; only if needed): rewrite touched `07` to `14` prompt-header comments once those examples graduate from drafts, and prune or justify stale `owns:` sections in [examples/13_critic_protocol/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/pyprompt/examples/13_critic_protocol/prompts/AGENTS.prompt).
- Exit criteria: the active verified corpus now runs cleanly through `14`, with no new top-level primitives and no H1 renderer branch.
- Rollback: reopen any example band whose source still depends on a draft mistake instead of weakening the grammar or compiler to rescue it.

## Phase 6 - Converge live docs and finalize the shipped teaching story

Status: COMPLETE

Completed work:
- Updated live language notes and the I/O note to reflect the shipped subset through `14`.
- Broadened `docs/COMPILER_ERRORS.md` wording for shared explicit-patching rules.
- Rewrote the active `07` to `11` prompt headers so they describe the shipped subset directly instead of calling those manifest-backed examples draft or sketch material.
- Rewrote the stale `07` findings in [docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md](/Users/aelaguiz/workspace/pyprompt/docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md) so the document now records current teaching risk instead of recommending an H1 renderer change or exploratory handling for shipped `07`.
- Reframed the tail of [docs/AGENT_IO_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/AGENT_IO_DESIGN_NOTES.md) from pre-ship design questions into post-`14` pressure plus explicit non-goals.

- Goal: Bring the repo’s live docs, comments, and example teaching surfaces into exact alignment with the shipped `01` to `14` subset.
- Work: Rewrite the now-stale `Pending Decisions`, `Pending Concepts`, role-graph framing, and `Top Candidates For Next Work` sections in [docs/LANGUAGE_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/LANGUAGE_DESIGN_NOTES.md); narrow [docs/AGENT_IO_DESIGN_NOTES.md](/Users/aelaguiz/workspace/pyprompt/docs/AGENT_IO_DESIGN_NOTES.md) from design exploration to shipped subset plus explicit non-goals; update [docs/COMPILER_ERRORS.md](/Users/aelaguiz/workspace/pyprompt/docs/COMPILER_ERRORS.md) with broadened wording and real shipped examples; and update or retire [docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md](/Users/aelaguiz/workspace/pyprompt/docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md) so it stops teaching stale `07` inheritance claims.
- Verification (smallest signal): run `make verify-examples`, do one manual cold read of the newly activated `07` to `14` examples plus the touched docs, and confirm there are no remaining live comments or docs that contradict the shipped subset.
- Docs/comments (propagation; only if needed): this phase is the propagation phase; delete or rewrite stale live truth surfaces rather than leaving legacy explanations in place.
- Exit criteria: the shipped implementation, manifests, examples, and live docs all tell the same story through `14`.
- Rollback: if final doc convergence exposes an unresolved semantic conflict, reopen the relevant earlier phase instead of papering over it in docs.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Prefer manifest-backed compiler contracts over bespoke unit harnesses.
- Add direct parser/compiler tests only if a new failure mode cannot be cleanly expressed through example manifests.
- Keep preservation checks behavior-level rather than structure-level.
- Do not add a second structured-proof or document-IR oracle in this port; keep `cases.toml` contracts as the primary proof surface.

## 8.2 Integration tests (flows)

- Use targeted manifest runs while each syntax family is landing.
- Keep `make verify-examples` as the main integration signal because it proves the active shipped subset end to end.
- Reject negative-value proof like deletion checks or doc inventories.

## 8.3 E2E / device tests (realistic)

- Not applicable as device testing, but do one final manual cold read of the newly activated examples to confirm the teaching story still matches the shipped compiler behavior.
- If a rendered contract is unclear on cold read, fix the example or the docs rather than inventing extra test machinery.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Roll out by expanding the active verified corpus in order, not by claiming `07` to `14` support all at once.
- Keep hard cutover semantics: either a construct is shipped and verified, or it remains draft pressure.

## 9.2 Telemetry changes

None expected. This repo’s primary trust surface is the verifier output and the checked-in docs/manifests.

## 9.3 Operational runbook

- When a post-`06` example exposes an ambiguity, stop, document the exact fork, and ask for a decision before adding grammar.
- If a docs/example/compiler drift is found while porting, either fix it in the same slice or record explicitly which layer is being changed.

# 10) Decision Log (append-only)

## 2026-04-06 - Treat post-`06` examples as design pressure, not authority

Context

Examples `07` to `14` introduce the syntax the user wants to port next, but the repo guidance and direct user clarification both say these drafts are exploratory, their handwritten rendered refs may be wrong, and `99` is not a pattern source.

Options

- Port every post-`06` example literally and let the grammar absorb the drafts.
- Treat the examples as requirement pressure only, stop for ambiguous cases, and encode only the constructs that survive design review.

Decision

Treat `07` to `14` as design pressure rather than truth. The implementation target is the clean approved construct set, not literal draft parity.

Consequences

- The port will include explicit decision checkpoints.
- Some example text, comments, or refs may be corrected or narrowed instead of encoded.
- Verification must come from manifests and shipped compiler behavior, not from handwritten output alone.

Follow-ups

- Confirm this North Star before deeper planning.
- During research/deep-dive, produce the exact approved construct inventory for `07` to `14`.

## 2026-04-06 - Use open authored workflow slots plus reserved typed agent fields

Context

The post-`06` examples need both reusable role-home sections such as `read_first` and `workflow_core`, and true turn-contract fields such as `inputs`, `outputs`, `outcome`, and `skills`. A literal reading of the drafts could either freeze every slot name into grammar or, in the other direction, collapse everything back into loose workflow prose.

Options

- Make every repeated slot name a first-class grammar keyword and give each its own compiler path.
- Treat all agent-local fields as one untyped blob and try to recover semantics later by heading name.
- Keep a reserved typed-field set for the true contract surfaces, and treat every other non-reserved field key as an authored workflow slot.

Decision

Use a mixed model: reserved typed agent fields for `role`, `inputs`, `outputs`, `outcome`, and `skills`; open authored workflow-slot keys for the reusable role-home and doctrine sections.

Consequences

- `12_role_home_composition` is satisfied without inventing a new role-home primitive.
- agent inheritance stays explicit and elegant by applying only to authored workflow slots through `14`
- the compiler stays fail-loud because typed contract fields remain explicit
- draft headings do not silently become grammar

Follow-ups

- During implementation, stop if a later example truly requires inherited typed contract fields rather than authored workflow slots.
- Reflect this split clearly in language notes once the code ships.

## 2026-04-06 - Keep route narrow and keep the renderer role-first

Context

The handwritten refs after `06` imply two possible expansions: a wider role-graph rendering mode with H1 agent headings, and a richer route surface that could drift toward a standalone control-flow DSL. The repo docs and cold-read audit both say those moves are not yet clearly earned.

Options

- Adopt the H1 agent-name opening and a bigger routing model now because some refs already do it.
- Keep the renderer stable and ship `route` only as a typed line item inside existing section structure.

Decision

Keep the current role-first renderer through this port. Ship `route` as a typed line item inside workflow and outcome sections, not as a standalone role-graph primitive.

Consequences

- `01` to `06` stay visually stable.
- `07` to `14` must be verified against the shipped renderer, not against handwritten H1 refs.
- the routing model stays narrow, explicit, and easier to validate.

Follow-ups

- If agent-name headings become important later, earn them with a dedicated example and manifest.
- If a later phase needs machine-readable routing or freshness semantics, reopen that as a new design step instead of stretching `route` beyond its current job.

## 2026-04-06 - Reuse existing compiler error identities for explicit patching

Context

This plan widens explicit patching from workflow bodies to authored workflow-slot fields on agents. The repo already has numbered compiler errors for explicit patch failures, but they are currently worded as workflow-only failures in [docs/COMPILER_ERRORS.md](/Users/aelaguiz/workspace/pyprompt/docs/COMPILER_ERRORS.md).

Options

- Introduce a second set of error numbers for agent-slot patch failures.
- Keep the existing explicit-patching error identities and broaden their wording to cover both workflow bodies and authored workflow-slot fields where the underlying rule is the same.

Decision

Keep the existing error identities for the same underlying explicit-patching rules. `E001` and `E003` should broaden with the patch engine if authored workflow-slot inheritance reuses that engine. `E002` should remain the generic missing-visible-title error rather than stay workflow-only in wording.

Consequences

- the error catalog stays smaller and more stable
- examples and docs need wording updates so the numbers describe the rule, not just the original surface where the rule first shipped
- `E002` and `E003` still need clearer teaching examples once the post-`06` examples gain manifests

Follow-ups

- Update [docs/COMPILER_ERRORS.md](/Users/aelaguiz/workspace/pyprompt/docs/COMPILER_ERRORS.md) when the implementation lands.
- Prefer manifest-backed fail cases over prose-only documentation for the broadened rules.

## 2026-04-06 - Keep redundant ownership prose out of shipped examples

Context

While porting `09_outputs` and `13_critic_protocol`, several draft examples still
carried `owns:` sections whose content was already obvious from the surrounding
typed output contract.

Options

- Preserve those sections literally because they appeared in the draft.
- Remove them where they add no new information, and keep the language surface
  focused on real contract pressure instead of cargo-cult prose.

Decision

Remove the redundant `owns:` sections from the shipped teaching examples rather
than treating them as meaningful language pressure.

Consequences

- The output examples stay shorter and clearer.
- Ownership still appears where it adds real information, but it is not
  mistaken for a required design pattern.

Follow-ups

- Keep watching later example drafts for other prose sections that are only
  repeating already-modeled truth.
