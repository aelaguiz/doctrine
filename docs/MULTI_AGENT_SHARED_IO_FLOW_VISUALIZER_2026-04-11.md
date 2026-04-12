---
title: "Doctrine - Multi-Agent Shared I/O Flow Visualizer - Architecture Plan"
date: 2026-04-11
status: complete
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: architectural_change
related:
  - docs/archive/second_wave/DOCTRINE_AGENT_DATA_FLOW_VISUALIZATION_2026-04-10.md
  - doctrine/compiler.py
  - doctrine/emit_flow.py
  - doctrine/flow_renderer.py
  - doctrine/diagnostic_smoke.py
  - docs/EMIT_GUIDE.md
  - README.md
---

# TL;DR

## Outcome

Doctrine's flow visualizer becomes a first-class multi-agent handoff view: one
generated diagram per entrypoint that makes agent-to-agent handoffs and shared
entities obvious, ships behind one easy Doctrine-owned CLI, and is showcased by
a generated SVG embedded directly in the README.

## Problem

The shipped `emit_flow` path already extracts routes and shared I/O from
compiler-owned semantics, but the public surface still feels like an internal
artifact. The current graphs do not strongly foreground shared entities, the
beginner CLI story is target-config-first instead of obvious, the docs teach
the feature mechanically rather than compellingly, and the README does not show
one standout multi-agent SVG that immediately sells the capability.

## Approach

Extend the existing compiler-owned visualization path
(`extract_target_flow_graph` -> `render_flow_d2` -> `render_flow_svg` ->
`doctrine.emit_flow`) instead of creating a second visualizer. Evolve the graph
and renderer so one view can clearly show multiple agents handing work to each
other plus the shared inputs, outputs, and other shared compiler-owned entities
they all touch, then tighten the CLI and docs around one canonical "generate
this flow now" experience.

## Plan

1. Ground the v2 scope against the shipped graph model, renderer, CLI, and the
   archived v1 visualization plan.
2. Design the smallest graph and rendering changes that make multi-agent
   handoff chains and shared entities feel obvious instead of incidental.
3. Simplify the public CLI so the showcase flow is easy to generate and the
   general path is easy to remember.
4. Add or refresh one flagship example whose checked-in SVG is good enough to
   embed directly in the README.
5. Update README, `docs/EMIT_GUIDE.md`, and example proof surfaces so the
   visualizer reads like a shipped Doctrine feature, not a side artifact.

## Non-negotiables

- No shadow parser, repo-local analyzer, or second visualization system.
- No beginner story that depends on editing `pyproject.toml` before someone can
  see the feature work.
- No README art that is hand-maintained or disconnected from the shipped
  `emit_flow` path.
- No proprietary `paperclip_agents` content in public docs or examples.
- No compatibility shims or parallel long-term CLI surfaces unless the plan
  later proves one canonical surface cannot cover both novice and repeat use.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-11
Verdict (code): COMPLETE
Manual QA: pending (non-blocking)

## Code blockers (why code is not done)
- None. The planned compiler, renderer, CLI, showcase example, and live-doc
  surfaces all landed on the canonical path, and the fresh repo verification
  pass stayed green on 2026-04-11.
  - Evidence anchors:
    - `doctrine/compiler.py:194-216`
    - `doctrine/flow_renderer.py:23-77`
    - `doctrine/emit_common.py:136-170`
    - `doctrine/emit_flow.py:110-207`
    - `doctrine/diagnostic_smoke.py:616-692`
    - `pyproject.toml:40-43`
    - `examples/68_flow_visualizer_showcase/cases.toml:4-8`
    - `README.md:143-172`
    - `docs/EMIT_GUIDE.md:17-125`
    - `docs/COMPILER_ERRORS.md:184-188`
    - `examples/README.md:124-150`
  - Verification:
    - `uv sync`
    - `npm ci`
    - `make verify-diagnostics`
    - `make verify-examples`

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Visually inspect `examples/68_flow_visualizer_showcase/build_ref/AGENTS.flow.svg`
  and the rendered README embed to confirm the grouped shared-input,
  handoff-lane, and shared-output layout still reads cleanly to a human.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-11
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-11
recommended_flow: implement-loop
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly, a Doctrine user will be able to run one
obvious Doctrine-supported command against a showcase example and against
ordinary Doctrine entrypoints to generate a readable `.flow.d2` plus `.flow.svg`
that:

- shows multiple concrete agents in one flow
- makes handoff edges between those agents easy to follow
- makes shared entities obvious at a glance, at minimum for shared inputs and
  shared outputs and, where compiler-owned semantics support it cleanly, for
  other shared graph entities
- is documented and demonstrated clearly enough that the embedded README SVG
  feels like truthful shipped proof, not a special-case demo

## 0.2 In scope

- Evolving the existing Doctrine-owned flow visualizer so one emitted graph can
  clearly represent multi-agent handoff chains.
- Making shared entities visibly first-class in the rendered graph instead of
  leaving them as incidental node reuse.
- Shared entity support that covers shared inputs and shared outputs at minimum,
  with any broader shared-entity categories constrained to compiler-owned truth
  rather than ad hoc authored metadata.
- CLI changes on the existing Doctrine visualizer path that add a
  direct-entrypoint quick-start mode while keeping configured targets as the
  build-contract and repeated-automation path on the same command.
- A flagship example with checked-in `.flow.d2` and `.flow.svg` proof that is
  strong enough to embed in `README.md`.
- Clean documentation updates across `README.md`, `docs/EMIT_GUIDE.md`, and any
  relevant example docs or instructions touched by the feature.
- Architectural convergence work needed to keep one canonical owner path for
  visualization extraction, rendering, CLI invocation, and example proof.

## 0.3 Out of scope

- A browser app, interactive graph editor, animation-heavy playground, or other
  second product surface for visualization.
- An inheritance explorer, AST dump viewer, or generic compiler-debug diagram.
- Hand-authored SVG or README-only illustration work that is not generated by
  shipped Doctrine code.
- Pulling proprietary role names, packet names, or internal workflow doctrine
  from `../paperclip_agents` into public Doctrine examples.
- Creating a second long-lived visualization command when the current
  `emit_flow` owner path can be strengthened instead.

## 0.4 Definition of done (acceptance evidence)

- From the repo root, one obvious documented command can generate the flagship
  multi-agent flow artifacts without extra repo-local setup beyond documented
  Doctrine prerequisites.
- The flagship emitted SVG clearly shows multiple agents, their handoff edges,
  and the shared entities they all use.
- The README embeds the generated SVG from checked-in proof artifacts and the
  docs explain how that same path generalizes to ordinary Doctrine entrypoints.
- Existing deterministic flow artifacts remain deterministic after the change,
  or any approved format change is reflected consistently in proof artifacts and
  docs.
- The shipped verification path remains green after the implementation lands.

Behavior-preservation evidence:

- existing `emit_flow` target resolution and compiler-owned graph extraction
  stay on the canonical path
- existing example verification stays green
- new flow-proof checks fail for real structural regressions, not for
  hand-maintained README drift

## 0.5 Key invariants (fix immediately if violated)

- One compiler-owned visualization pipeline owns extraction, rendering, and CLI
  behavior.
- The default graph answers "who hands work to whom, and what shared entities
  do they touch?" before it tries to show secondary detail.
- Shared entities should appear once per graph and read as shared, not as
  duplicated per-agent clutter.
- The flagship README example must be generated from the shipped path and kept
  in sync with the checked-in proof artifacts.
- Fail loudly on invalid targets, invalid entrypoints, or missing renderer
  prerequisites.
- Public Doctrine docs and examples stay generic and open-source-safe.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Make multi-agent handoffs obvious in one glance.
2. Make shared entities visually legible as shared, not repeated.
3. Give the visualizer one obvious CLI story.
4. Show the feature with a standout generated example in the README.
5. Preserve one compiler-owned, deterministic visualization path.

## 1.2 Constraints

- The shipped visualizer already lives on `doctrine.emit_flow`; this cut should
  strengthen that path rather than orphan it.
- Current graphs already include multiple agents, inputs, outputs, and route
  edges, so the problem is not blank-slate feature absence.
- Public open-source docs and examples cannot import proprietary
  `paperclip_agents` terminology or internal workflow content.
- The output must remain deterministic and friendly to checked-in proof
  artifacts.
- The repo already depends on pinned D2 rendering for SVG output, so CLI and
  docs must stay honest about prerequisites.

## 1.3 Architectural principles (rules we will enforce)

- Evolve the existing graph IR and renderer instead of creating a new
  visualization lane.
- Keep shared-entity modeling rooted in compiler-owned semantics, not in
  renderer-only heuristics that invent truth.
- Prefer one canonical public CLI over multiple overlapping beginner and expert
  commands.
- The README showcase is proof of the real feature, not marketing art.
- Preserve deterministic, reviewable `.flow.d2` as the truth-first artifact
  even when the README emphasizes SVG.

## 1.4 Known tradeoffs (explicit)

- Stronger visual grouping for shared entities may require format changes to
  `.flow.d2` and `.flow.svg`, which could churn checked-in proof artifacts.
- A friendlier CLI may require supporting both configured-target and
  direct-entrypoint use cases, but the public docs still need one canonical
  story instead of two equal surfaces.
- A "badass" flagship example must still stay generic and compiler-truthful,
  which limits how much style can come from repo-specific lore or hand-tuned
  artwork.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already ships a compiler-owned `emit_flow` surface that renders one
target-scoped `.flow.d2` and `.flow.svg` from configured emit targets. The
current graph includes concrete agents, declared inputs, declared outputs, and
route edges, and the shipped repo already contains flow proofs such as
`examples/07_handoffs` and `examples/36_invalidation_and_rebuild`.

## 2.2 What’s broken / missing (concrete)

The feature is undersold and under-shaped for the user story the visualizer
should own. The graphs do not yet make "shared stuff everyone touches" feel
like a deliberate first-class section, the public CLI still reads like a config
surface before it reads like a quick-start tool, and the README lacks one
generated SVG that proves Doctrine can show a compelling multi-agent handoff
flow without explanation-heavy setup.

## 2.3 Constraints implied by the problem

The next cut needs to distinguish "improve the visualizer the repo already has"
from "invent a new visualization product." It also needs to converge example,
CLI, docs, and renderer work together, because a graph that technically exists
but is hard to discover, hard to run, or badly showcased still fails the user
goal.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- `../paperclip_agents/docs/LESSONS_WORKFLOW_SIMPLE_CLEAR.md` — adopt the
  simple workflow rule that each lane should have one clear job, one clear
  handoff, and one clear stop line, and that the next move should be obvious
  from the current packet or artifact chain — this applies directly to the
  visualizer because the flagship diagram should privilege lane-to-lane
  readability and shared-entity truth over exhaustive semantic density.
- `../paperclip_agents/docs/PAPERCLIP_GOTCHAS.md` — adopt the boundary rule
  that a convenience wrapper must not add repo-only policy or become a second
  procedure manual for the same underlying primitive — this applies here
  because any "easy CLI" must stay a thin Doctrine-owned entry to the canonical
  `emit_flow` path, not a second visualization workflow with its own driftable
  logic.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/compiler.py` — defines `FlowAgentNode`, `FlowInputNode`,
    `FlowOutputNode`, `FlowEdge`, and `FlowGraph`, and
    `CompilationContext.extract_target_flow_graph(...)` is the canonical owner
    for target-scoped graph extraction from concrete-agent inputs, outputs,
    authored routes, workflow-law routes, and currentness/invalidation notes.
  - `doctrine/flow_renderer.py` — owns the current D2 rendering contract:
    inputs, then agents, then outputs; rectangle nodes; static palettes by node
    kind; and edge styling by `consume`, `produce`, `authored_route`, and
    `law_route`.
  - `doctrine/flow_svg.mjs` — owns deterministic SVG rendering over the pinned
    D2 dependency with the current render salt and pad settings.
  - `doctrine/emit_flow.py` — owns the public flow-emission CLI today and
    currently requires configured `--target` values before it emits `.flow.d2`
    and `.flow.svg`.
  - `doctrine/emit_common.py` — owns emit target resolution, `pyproject.toml`
    discovery, supported entrypoint rules, and entrypoint-relative output
    layout; any easier CLI must converge here rather than bypassing it.
  - `doctrine/diagnostic_smoke.py` — already proves two key preservation
    surfaces: shared-I/O plus route extraction and deterministic output naming
    for `AGENTS.prompt` versus `SOUL.prompt`.
  - `examples/07_handoffs/prompts/AGENTS.prompt` — current best shipped example
    for a readable multi-agent handoff chain, but it does not showcase shared
    entities.
  - `examples/36_invalidation_and_rebuild/prompts/AGENTS.prompt` — current best
    shipped example for shared inputs, shared outputs, currentness, and
    invalidation notes, but it is a less beginner-friendly flagship story.
- Canonical path / owner to reuse:
  - `doctrine.compiler:extract_target_flow_graph` ->
    `doctrine.flow_renderer:{render_flow_d2, render_flow_svg}` ->
    `doctrine.emit_flow:emit_target_flow` — this is the existing SSOT path and
    should remain the only visualization pipeline.
- Existing patterns to reuse:
  - `doctrine/emit_common.py` — configured `EmitTarget` registry plus
    entrypoint-relative output layout; this is the canonical place to converge
    any easier invocation path.
  - `doctrine/compiler.py` — artifact-key deduplication for inputs and outputs;
    shared-entity emphasis should build on this instead of introducing a second
    grouping source.
  - `doctrine/flow_renderer.py` + `doctrine/flow_svg.mjs` — deterministic
    `.flow.d2` truth artifact plus same-command `.flow.svg` convenience render.
- Prompt surfaces / agent contract to reuse:
  - `examples/07_handoffs/prompts/AGENTS.prompt` — explicit authored `route`
    chains between concrete agents and a simple same-issue owner flow.
  - `examples/36_invalidation_and_rebuild/prompts/AGENTS.prompt` — law-driven
    currentness, invalidation, trust-surface, and carrier-output semantics that
    already create richer output notes in the graph.
  - `doctrine/diagnostic_smoke.py` shared-I/O smoke source — compact proof that
    multiple agents can consume the same input and reuse carrier outputs today.
- Native model or agent capabilities to lean on:
  - Not a primary lever for this change — the visualizer is compiler-owned and
    should use explicit authored prompt semantics instead of any model-side
    inference or heuristic reconstruction.
- Existing grounding / tool / file exposure:
  - `pyproject.toml` — current configured emit targets are the only shipped
    public discovery surface for `emit_flow`.
  - `README.md` and `docs/EMIT_GUIDE.md` — current live docs already describe
    the feature, but only mechanically and without one standout public example.
  - `examples/07_handoffs/build/AGENTS.flow.d2` and
    `examples/36_invalidation_and_rebuild/build_ref/AGENTS.flow.d2` — current
    reviewable proof artifacts for the two halves of the story.
- Duplicate or drifting paths relevant to this change:
  - `docs/archive/second_wave/DOCTRINE_AGENT_DATA_FLOW_VISUALIZATION_2026-04-10.md`
    — useful historical framing, but it is no longer the live truth surface and
    must not compete with this plan or the live docs.
  - `README.md`, `docs/EMIT_GUIDE.md`, and the shipped example proofs — all
    describe real pieces of the visualizer today, but no single public surface
    currently tells the full multi-agent plus shared-entity story cleanly.
  - any future direct-entrypoint or example-focused shortcut — if added, it
    will drift unless it resolves through `emit_common` and stays explicitly
    subordinate to `emit_flow`.
- Capability-first opportunities before new tooling:
  - use the existing graph IR plus richer renderer grouping, labeling, and
    example selection before adding any new parser, analyzer, or sidecar
    metadata format
  - use `emit_common` resolution and the existing emit target model before
    inventing a repo-only demo runner
  - use a checked-in generated SVG in `README.md` instead of hand-authored
    diagram art
- Behavior-preservation signals already available:
  - `doctrine/diagnostic_smoke.py::_check_flow_graph_extracts_routes_and_shared_io`
    — protects shared-input dedupe, route extraction, and carrier-output notes
  - `doctrine/diagnostic_smoke.py::_check_emit_flow_uses_entrypoint_stem_for_output_name`
    — protects the current emit naming contract
  - `make verify-examples` — protects the shipped corpus and checked-in proof
    artifacts when emit behavior changes

## 3.3 Open questions (evidence-based)

- What is the minimum structured node metadata the renderer needs beyond the
  current flattened detail lines — settle this by implementing the render-model
  spike against `examples/36_invalidation_and_rebuild` and the new showcase
  example, then deleting any metadata field that only served styling taste.
- How much D2 container structure is enough before the graph becomes noisy —
  settle this by comparing generated `.flow.d2` and `.flow.svg` output against
  the README showcase readability bar, not by diagram novelty alone.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/compiler.py`
  - owns the semantic flow graph IR and target-level extraction from concrete
    agents
- `doctrine/flow_renderer.py`
  - owns D2 text generation and the current flat render contract
- `doctrine/flow_svg.mjs`
  - owns deterministic SVG generation through the pinned D2 dependency
- `doctrine/emit_flow.py`
  - owns the public flow-emission CLI and only accepts configured emit targets
- `doctrine/emit_common.py` + `pyproject.toml`
  - own emit target discovery, path validation, and output layout
- `doctrine/diagnostic_smoke.py` + `doctrine/verify_corpus.py`
  - own structural smoke coverage and build-contract verification
- `README.md`, `docs/EMIT_GUIDE.md`, and `examples/README.md`
  - own the live public explanation of the visualizer
- `examples/07_handoffs`
  - owns the cleanest shipped multi-agent handoff story
- `examples/36_invalidation_and_rebuild`
  - owns the cleanest shipped shared-I/O plus currentness/invalidation flow
    proof

## 4.2 Control paths (runtime)

1. `doctrine.emit_flow:main(...)` resolves `pyproject.toml`, loads configured
   emit targets, and requires one or more `--target` arguments.
2. `emit_target_flow(...)` parses the target entrypoint, discovers all concrete
   root agents, and opens one `CompilationSession`.
3. `CompilationSession.extract_target_flow_graph(...)` delegates to
   `CompilationContext.extract_target_flow_graph(...)`, which:
   - deduplicates input and output nodes by artifact key
   - emits `consume` edges from inputs to agents
   - emits `produce` edges from agents to outputs
   - emits `authored_route` edges from authored workflow routes
   - emits `law_route` edges from workflow-law route branches
   - appends currentness and invalidation notes onto output carriers
4. `render_flow_d2(...)` emits a flat D2 diagram in this order:
   inputs, then agents, then outputs, then edges.
5. `render_flow_svg(...)` shells out to Node and the pinned D2 package to
   render the `.flow.svg`.
6. `verify_corpus._run_build_contract(...)` regenerates flow artifacts whenever
   `build_ref/` contains `.flow.d2` or `.flow.svg` and diffs the whole build
   tree against checked-in proof.

## 4.3 Object model + key abstractions

- `FlowGraph`
  - semantic graph container with separate tuples for `agents`, `inputs`,
    `outputs`, and `edges`
- `FlowAgentNode`, `FlowInputNode`, `FlowOutputNode`
  - current node model is presentation-light: title plus string
    `detail_lines`; output nodes additionally carry `trust_surface` and `notes`
- `FlowEdge`
  - the only structured relationship object; its `kind` field drives current
    renderer styling
- `EmitTarget`
  - the only public flow-emission request abstraction today; there is no direct
    entrypoint request object or synthesized target path

Current design strengths:

- semantic graph extraction already lives in the compiler
- shared inputs and shared outputs already dedupe correctly
- currentness and invalidation facts already survive as compiler-owned notes

Current design gaps:

- the renderer has no intermediate layout model for lanes, clusters, or shared
  sections
- node detail needed for richer grouping is mostly flattened into prose strings
- the public CLI has no quick-start mode outside configured targets

## 4.4 Observability + failure behavior today

- `emit_flow` fails loudly on missing config, unknown targets, invalid
  entrypoints, missing concrete agents, and renderer failures
- missing D2 support yields `E515` after `.flow.d2` generation is attempted and
  before `.flow.svg` is trusted
- checked-in build contracts surface diffable drift in emitted flow artifacts
- smoke coverage already protects:
  - shared input plus route extraction
  - carrier-output note preservation
  - entrypoint-stem output naming

What is not protected today:

- no automated guard says the rendered diagram foregrounds shared entities well
- no automated guard says the public CLI is easy to discover or easy to use
- no single example currently proves multi-agent handoffs and shared-entity
  visibility together in one public-friendly story

## 4.5 UI surfaces (ASCII mockups, if UI work)

Current visual shape is semantically correct but visually generic:

```text
[Inputs]
  SharedInput
     | consumes
[Agents]
  WorkerA ----route----> RoutingOwner
  WorkerB
     | produces
[Outputs]
  DurableArtifact
  CarrierComment
```

Current problems with that shape:

- sharedness is technically present but visually implicit
- handoff lanes and shared artifacts compete for the same visual attention
- currentness/invalidation carrier notes read like appended labels instead of a
  deliberate shared artifact section
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- keep `doctrine/compiler.py` as the semantic graph owner
- extend `doctrine/compiler.py` only enough to expose structured node metadata
  the renderer needs for grouping and badges without parsing human label text
- extend `doctrine/flow_renderer.py` with a render-model normalization layer
  that derives shared sections and agent lanes from the semantic graph
- keep `doctrine/flow_svg.mjs` as the only SVG renderer path, with at most
  small readability-tuning changes
- extend `doctrine/emit_common.py` with one shared request resolver so
  configured-target mode and direct-entrypoint mode converge onto the same emit
  pipeline
- extend `doctrine/emit_flow.py` rather than adding a second command
- add one new curated flagship example target and checked-in flow proof under
  `examples/68_flow_visualizer_showcase/`
- update `README.md`, `docs/EMIT_GUIDE.md`, and `examples/README.md` so the new
  example and quick-start path are the live truth

## 5.2 Control paths (future)

1. `doctrine.emit_flow` remains the one public command.
2. The command accepts exactly one resolution mode per run:
   - configured repo automation mode: `--target <name>`
   - public quick-start mode: `--entrypoint <AGENTS.prompt|SOUL.prompt>` plus
     `--output-dir <dir>`
3. Both modes resolve through one `emit_common` helper that returns a canonical
   `EmitTarget`-like request, so `emit_target_flow(...)` remains the only emit
   pipeline.
4. `CompilationContext.extract_target_flow_graph(...)` stays the semantic owner
   for nodes, edges, currentness, invalidation, and trust-surface facts.
5. `flow_renderer` adds one derived render model that:
   - computes artifact fan-in and fan-out from graph edges
   - classifies artifacts touched by multiple agents as shared
   - groups the diagram into explicit sections for shared inputs, agent
     handoffs, and shared outputs/carriers
   - keeps route edges visually dominant over secondary metadata wiring
6. The README showcase points at the checked-in generated SVG from the new
   flagship example's `build_ref/` tree.
7. `verify_corpus` continues to validate the same build-contract truth by
   regenerating docs plus flow artifacts from configured targets.

## 5.3 Object model + abstractions (future)

- keep `FlowGraph` as the semantic IR; do not introduce a second parser-facing
  graph model
- enrich `FlowInputNode` and `FlowOutputNode` with small structured fields the
  renderer can trust directly, such as:
  - source or target kind
  - resolved path where relevant
  - shape
  - requirement
  - trust-surface presence
  - carrier-like status where the compiler already knows it
- add a renderer-local derived model, such as `FlowRenderModel`, that owns:
  - lane ordering
  - shared-section membership
  - label emphasis and grouping
  - any D2 container structure

Boundary rule:

- semantic ownership stays in compiler output
- presentation ownership stays in renderer normalization
- CLI ownership stays in `emit_flow` plus `emit_common`

## 5.4 Invariants and boundaries

- no second visualization command and no second visualization pipeline
- no README or docs asset that is not generated from the shipped code path
- no renderer heuristics that parse human label strings to recover typed
  meaning the compiler could expose directly
- no mutation of `examples/07_handoffs` or `examples/36_invalidation_and_rebuild`
  into a broad showcase that weakens their current teaching roles
- configured targets remain the build-contract surface; direct-entrypoint mode
  is the public quick-start surface on the same command
- shared sections must be derived from compiler-owned graph truth, not from
  hand-authored diagram metadata

## 5.5 UI surfaces (ASCII mockups, if UI work)

Target visual shape:

```text
+---------------------- Shared Inputs ----------------------+
| Shared Brief | Shared Repo Facts | Shared Contract        |
+-------------------------+-------------------------------+
                          | consumes
+--------------------- Agent Handoffs ---------------------+
| Project Lead --> Research --> Writing --> Project Lead   |
|        \\---------------- blocked ----------------/      |
+-------------------------+-------------------------------+
                          | produces / carries
+--------------- Shared Outputs / Carriers ----------------+
| Handoff Comment | Draft Artifact | Current Packet        |
+----------------------------------------------------------+
```

Design intent:

- shared sections should read as deliberate anchors
- route edges should make the handoff chain obvious in one scan
- carrier outputs and durable artifacts should be legible without turning the
  graph into a full workflow-law explainer
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| semantic graph metadata | `doctrine/compiler.py` | `FlowInputNode`, `FlowOutputNode`, `_flow_input_detail_lines`, `_flow_output_detail_lines` | renderer mainly receives titles and flattened detail prose | expose small structured metadata fields alongside display prose | shared sections and badges should use compiler truth, not label parsing | enriched node metadata remains semantic and renderer-agnostic | `doctrine/diagnostic_smoke.py`, build-contract examples |
| semantic graph extraction | `doctrine/compiler.py` | `CompilationContext.extract_target_flow_graph`, `_collect_flow_from_workflow_body`, `_collect_flow_from_section_items` | extracts deduped I/O nodes plus consume, produce, authored-route, and law-route edges | preserve this as the only graph owner and add only minimal metadata or annotations needed by the new render model | prevent shadow extraction paths | `FlowGraph` remains the only semantic flow IR | `doctrine/diagnostic_smoke.py`, `make verify-examples` |
| render-model normalization | `doctrine/flow_renderer.py` | `render_flow_d2` and helpers | emits a flat node list ordered by kind with simple per-kind styling | add a renderer-local normalization pass for shared sections, lane emphasis, and stronger route/shared styling | current flat output is correct but not compelling | D2 output gains stable section containers and clearer visual hierarchy | build-contract diffs for flow examples |
| SVG rendering | `doctrine/flow_svg.mjs` | `main` | renders D2 source with the current deterministic options | tune only if the richer D2 layout needs readability adjustments; keep pinned D2 path | avoid a second renderer stack | same deterministic SVG contract, possibly with small layout-tuning changes | build-contract diffs for SVG artifacts |
| public CLI | `doctrine/emit_flow.py` | `main`, `_build_arg_parser`, `emit_target_flow` | target-only CLI backed by configured emit targets | support one quick-start resolution mode on the same command via direct entrypoint plus output dir | user asked for an easy CLI and current target-only path is configuration-first | one command, mutually exclusive resolution modes, one emit pipeline | new CLI smoke coverage, doc command receipts |
| shared request resolution | `doctrine/emit_common.py` | target loading and path-validation helpers | only configured targets can reach the emit pipeline | add one helper that synthesizes a canonical emit request from direct-entrypoint mode | prevent a second manual path inside `emit_flow.py` | configured-target mode and direct-entrypoint mode converge before emission | new CLI smoke coverage |
| build-contract verification | `doctrine/verify_corpus.py` | `_run_build_contract` | regenerates docs and optionally flow artifacts for configured targets | keep this path authoritative for the new flagship example and any changed flow outputs | preserve proof discipline | no second verifier path; showcase example must prove itself through build contract | `make verify-examples` |
| structural smoke tests | `doctrine/diagnostic_smoke.py` | shared-I/O smoke, output-name smoke, new renderer/CLI smoke | protects shared extraction and naming but not the new render-model or CLI mode | add regression checks for quick-start CLI resolution and core shared-section rendering invariants | prevent visualizer regressions from drifting silently | smoke tests protect the new CLI and sectioned render contract | `make verify-diagnostics` if diagnostics surface changes; otherwise smoke invocation |
| emit registry | `pyproject.toml` | `[tool.doctrine.emit.targets]` | only example targets `07`, `14`, and `36` are registered | add a new flagship flow showcase target | README/demo asset and build-contract proof need a stable configured target | showcase example has a stable build-contract name | `make verify-examples` |
| flagship example source and proof | `examples/68_flow_visualizer_showcase/**` | new prompt, manifest, refs, and `build_ref/AGENTS.flow.{d2,svg}` | no current example simultaneously owns public handoff clarity and shared-entity visibility | add a curated public-friendly example instead of distorting existing teaching examples | keep one new idea per existing example while still shipping a compelling showcase | new example becomes the canonical public visualizer proof | `make verify-examples`, targeted manifest verification |
| public docs | `README.md`, `docs/EMIT_GUIDE.md`, `examples/README.md` | flow docs and example guidance | docs mention `emit_flow`, but the story is split and README has no embedded flow SVG | embed the generated showcase SVG, document the quick-start mode, and point readers at the flagship example | user asked for clean docs and a README-embedded SVG | live docs tell one consistent public story | doc command receipts plus build-contract proof asset generation |
| stable error docs | `docs/COMPILER_ERRORS.md` | emit error catalog | current catalog covers target/config/D2 failures only | update only if the new quick-start mode adds or changes stable emit errors | keep docs aligned with shipped failures | stable error catalog stays honest about CLI behavior | manual doc sync plus any emit smoke/error tests |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `emit_common` resolves one request
  - `emit_flow` runs one emit command
  - `compiler.py` owns the semantic graph
  - `flow_renderer.py` owns presentation
- Deprecated APIs (if any):
  - none yet, but the docs should stop presenting configured targets as the only
    beginner-facing way to use the visualizer once direct-entrypoint mode lands
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - no second wrapper command
  - no hand-authored README SVG
  - no ad hoc demo script that bypasses `emit_flow`
- Capability-replacing harnesses to delete or justify:
  - any renderer-side text parsing of node label prose to infer typed grouping
    should be treated as a rejected shortcut unless the compiler cannot expose
    the data directly
- Live docs/comments/instructions to update or delete:
  - `README.md`
  - `docs/EMIT_GUIDE.md`
  - `examples/README.md`
  - `docs/COMPILER_ERRORS.md` if stable errors change
- Behavior-preservation signals for refactors:
  - shared-I/O smoke in `doctrine/diagnostic_smoke.py`
  - output-name smoke in `doctrine/diagnostic_smoke.py`
  - `make verify-examples` build-contract proof for affected targets

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| emit CLI resolution | `doctrine.emit_docs`, `doctrine.emit_flow`, `doctrine.emit_common` | shared request resolution instead of bespoke argument branching | avoids parallel CLI logic and path-validation drift | include for `emit_flow`, defer for `emit_docs` unless parity is almost free |
| flow proof examples | `examples/07_handoffs`, `examples/36_invalidation_and_rebuild`, new showcase example | keep narrow teaching examples and add one dedicated showcase example | prevents one proof example from carrying too many jobs | include new showcase example, defer changes to `07` and `36` beyond minimal doc references |
| public docs | `README.md`, `docs/EMIT_GUIDE.md`, `examples/README.md` | one canonical quick-start story plus one canonical showcase example | prevents split discovery paths and stale example recommendations | include |
| alternate visualization surfaces | new wrapper commands, demo scripts, or hand-authored assets | reject second visualization procedure | prevents shadow workflow law and stale demos | exclude |
<!-- arch_skill:block:call_site_audit:end -->

# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

<!-- arch_skill:block:phase_plan:start -->
## Phase 1 — Semantic graph metadata and render-model foundation

Status: COMPLETE

* Goal:
  make the existing compiler-owned flow graph rich enough for a stronger
  sectioned visualizer without creating a second graph pipeline.
* Work:
  extend `FlowInputNode` and `FlowOutputNode` with the minimum structured
  metadata the renderer needs; keep `extract_target_flow_graph(...)` as the only
  semantic owner; add a renderer-local normalization layer in
  `doctrine/flow_renderer.py` that derives shared sections, agent-lane emphasis,
  and route/shared styling from the graph; tune `flow_svg.mjs` only if the new
  D2 layout needs small readability adjustments.
* Verification (smallest signal):
  keep the shared-I/O smoke green; add one renderer-focused regression that
  proves the new sectioned layout contract at the D2 source level; run a
  targeted `emit_flow` regeneration against `example_36_invalidation_and_rebuild`
  to confirm currentness/invalidation notes still survive the richer rendering
  path.
* Docs/comments (propagation; only if needed):
  add one high-leverage comment at the compiler/renderer boundary if the new
  metadata fields could otherwise tempt future label-parsing shortcuts.
* Exit criteria:
  one semantic graph still owns flow truth, the renderer can derive shared
  sections from compiler-owned data, and no second parser or render pipeline was
  introduced.
* Rollback:
  revert the metadata and renderer-normalization changes together so the repo
  returns to the current flat `emit_flow` contract without half-landed layout
  state.

## Phase 2 — One-command CLI convergence

Status: COMPLETE

* Goal:
  make `doctrine.emit_flow` easy to use on first contact without forking the
  configured-target pipeline.
* Work:
  extend `doctrine/emit_flow.py` so one command accepts either configured target
  resolution or direct-entrypoint quick-start resolution; add the shared request
  resolver in `doctrine/emit_common.py`; keep configured targets as the
  build-contract and repeated-automation surface; ensure the help text and error
  surface make the mode split explicit instead of ambiguous.
* Verification (smallest signal):
  keep current target-mode smoke green and add a new CLI smoke that proves
  direct-entrypoint mode resolves through the same emit path and writes the same
  output layout rules.
* Docs/comments (propagation; only if needed):
  update inline CLI help text and any small docstrings needed to keep the shared
  resolver contract obvious.
* Exit criteria:
  there is still one public command, both resolution modes converge before
  emission, and there is no wrapper command or demo-only runner in the repo.
* Rollback:
  remove direct-entrypoint mode and the shared resolver changes together,
  returning to the existing target-only CLI until the quick-start design is
  ready to reland cleanly.

## Phase 3 — Showcase example and checked-in proof

Status: COMPLETE

* Goal:
  add one dedicated public-friendly example that simultaneously shows multi-agent
  handoffs and shared entities well enough to anchor the README.
* Work:
  add `examples/68_flow_visualizer_showcase/` with a narrow prompt, manifest,
  checked render refs, and checked `build_ref/AGENTS.flow.{d2,svg}` artifacts;
  register its emit target in `pyproject.toml`; keep `07` and `36` narrow and
  use the new example as the public flagship instead of mutating existing
  teaching examples into mixed-purpose demos.
* Verification (smallest signal):
  run targeted manifest verification for the new example and then run
  `make verify-examples` so the new build-contract proof and existing corpus
  stay green together.
* Docs/comments (propagation; only if needed):
  keep example comments minimal and generic; only add prompt comments that make
  the showcase intent easier to understand without product jargon.
* Exit criteria:
  the repo contains one dedicated showcase example with checked-in generated
  flow artifacts and a stable build-contract target.
* Rollback:
  remove the new example and target registration together so the corpus and emit
  registry return to the prior stable set.

## Phase 4 — README embed and docs truth-sync

Status: COMPLETE

* Goal:
  make the shipped feature easy to discover, easy to run, and visibly proven by
  a generated SVG in the README.
* Work:
  embed the generated showcase SVG in `README.md`; update `docs/EMIT_GUIDE.md`
  to document the quick-start mode, the build-contract mode, the showcase
  example, and regeneration commands; update `examples/README.md` so the
  flagship example and proof role are accurate; update `docs/COMPILER_ERRORS.md`
  only if the CLI surface introduces stable new failure modes.
* Verification (smallest signal):
  rerun the showcase `emit_flow` command through the documented path, confirm
  the README asset path resolves to the checked-in generated SVG, and keep
  `make verify-examples` green after the doc/example truth surfaces are synced.
* Manual QA (non-blocking):
  inspect the rendered README embed and the checked-in showcase SVG visually to
  confirm the grouped layout reads clearly outside the raw `.flow.d2` source.
* Docs/comments (propagation; only if needed):
  this phase is the docs propagation phase; remove stale target-only language
  where it would otherwise misteach the feature.
* Exit criteria:
  the README, emit guide, examples guide, and checked-in showcase asset all say
  the same thing about how the visualizer works and how to regenerate it.
* Rollback:
  revert the public docs and README embed together if the underlying code or
  showcase proof is not yet stable enough to be the public story.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

Prefer extending `doctrine/diagnostic_smoke.py` instead of inventing a second
test harness. The important unit-level guards are:

- shared-I/O plus route extraction still behaves correctly
- the new renderer normalization preserves the intended shared-section contract
- direct-entrypoint quick-start resolution still converges onto the same emit
  pipeline as configured targets

## 8.2 Integration tests (flows)

The integration path should stay small and real:

- one targeted `emit_flow` regeneration for
  `examples/68_flow_visualizer_showcase`
- one targeted manifest run for that example
- `make verify-examples` for the whole shipped corpus and checked-in flow proof
  artifacts

## 8.3 E2E / device tests (realistic)

Manual verification should stay small:

- inspect the generated flagship SVG and confirm the handoff chain reads in one
  pass
- confirm the shared sections actually foreground shared entities instead of
  hiding them in generic node lists
- confirm the README embed points at the checked-in generated artifact
- confirm the documented quick-start command and the configured-target path both
  work as documented

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

This should land as one repo-local cut across graph/rendering code, CLI,
example proof, and docs so the feature reads coherently the moment it ships.

## 9.2 Telemetry changes

No runtime telemetry system is expected. The relevant feedback loop is emitted
artifact readability plus verification stability in the shipped repo surfaces.

## 9.3 Operational runbook

The runbook should stay small and live in normal docs: prerequisites (`uv sync`
and `npm ci`), the canonical visualizer command, the output location, and how
to regenerate the README showcase artifact.

# 10) Decision Log (append-only)

## 2026-04-11 - Treat this as a v2 visualizer pass, not a new system

Context

Doctrine already ships `emit_flow`, a D2 renderer, and checked-in flow proof
artifacts, but the user now wants the visualizer to feel much more compelling,
obvious, and shared-entity-aware.

Options

- Start a brand-new visualization command or parallel demo pipeline.
- Evolve the existing compiler-owned graph, renderer, CLI, examples, and docs.

Decision

Evolve the existing Doctrine-owned visualization path and use this plan to
scope a stronger public surface around it.

Consequences

This plan must stay honest about what already ships today, avoid duplicate
owner paths, and treat README/demo polish as part of the shipped feature rather
than as marketing garnish.

Follow-ups

- Research whether the best easy CLI is improved target-first UX,
  direct-entrypoint UX, or one command that can cover both without public
  ambiguity.
- Deep-dive the minimum graph/rendering changes needed to make shared entities
  feel deliberate and obvious.

## 2026-04-11 - Keep one command, add direct-entrypoint quick-start, and add a dedicated showcase example

Context

The planning pass found that the current repo already has one correct semantic
graph pipeline, but the public story is split: configured targets are the only
CLI path, `07_handoffs` proves handoff chains without shared entities, and `36`
proves shared entities without serving as the best README showcase.

Options

- Keep target-only CLI and simply document one existing target better.
- Add a second wrapper command or demo runner for first-use ergonomics.
- Keep `emit_flow` as the only command, add a direct-entrypoint quick-start
  mode on the same pipeline, and add one dedicated showcase example.

Decision

Keep `doctrine.emit_flow` as the one command, add a direct-entrypoint
quick-start mode that still resolves through `emit_common`, and add a dedicated
showcase example instead of overloading `07` or `36`.

Consequences

The phase plan can now treat CLI, renderer, example proof, and README embed as
one coherent ship unit. It also means the implementation must avoid creating a
parallel wrapper workflow or weakening the current teaching roles of the
existing examples.

Follow-ups

- Specify the minimal metadata the renderer needs from compiler-owned nodes.
- Choose the exact showcase example content and keep it generic and open-source
  safe.
