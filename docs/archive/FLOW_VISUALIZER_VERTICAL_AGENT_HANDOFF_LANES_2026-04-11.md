---
title: "Doctrine - Flow Visualizer Vertical Agent Handoff Lanes - Architecture Plan"
date: 2026-04-11
status: complete
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: architectural_change
related:
  - docs/archive/MULTI_AGENT_SHARED_IO_FLOW_VISUALIZER_2026-04-11.md
  - doctrine/emit_flow.py
  - doctrine/emit_common.py
  - doctrine/compiler.py
  - doctrine/flow_renderer.py
  - doctrine/diagnostic_smoke.py
  - examples/73_flow_visualizer_showcase/prompts/AGENTS.prompt
  - docs/EMIT_GUIDE.md
---

# TL;DR

## Outcome

Doctrine's canonical flow visualizer will render multi-agent handoffs as a
top-to-bottom lane that starts with the first routed owner in the main flow,
using declaration order only as a fallback when route data does not expose a
stronger start signal, and then follows the normal route order while still
showing shared inputs, shared carriers, local outputs, and loop-back or
side-route connections.

## Problem

The shipped visualizer is compiler-owned and truthful, but the current layout
treats the flow like a broad graph. All agents are flattened into one
horizontal handoff strip, and shared input/output edges compete equally with
the handoff path, so the real owner-to-owner story is hard to read.

## Approach

Keep `emit_flow` on its current compiler-owned path, but change the flow
extraction and rendering contract so it preserves the main lane order. Derive
lane start from the shipped route path first, use declaration order only as a
fallback when needed, preserve authored route order instead of sorting it away,
lay the main route vertically, and render shared I/O plus loop-backs as
secondary attachments rather than the primary structure.

## Plan

1. Confirm the exact ordering signals already available in the shipped language
   and compiler output.
2. Define the minimal graph-model changes needed to preserve start-owner and
   route order without inventing new Doctrine syntax.
3. Rework the D2 renderer so the main agent lane is vertical and secondary
   edges hang off it cleanly.
4. Refresh the flagship showcase proof and the smallest set of diagnostics and
   docs that protect the new layout contract.
5. Verify that the visualizer still emits deterministically and that the
   changed layout reads like a real handoff flow.

## Non-negotiables

- No new visualization system or second emit path.
- No new Doctrine language feature unless the existing model truly cannot
  express the needed ordering.
- No fallback layout that silently keeps the old flat agent strip as the
  canonical handoff view.
- No loss of deterministic `.flow.d2` output or manifest-backed proof.
- Shared inputs and outputs may stay visible, but they must not dominate the
  handoff path.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-11
Verdict (code): COMPLETE
Manual QA: complete (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-11
Verdict (code): COMPLETE
Manual QA: complete (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- No missing code items remain.
  - Evidence anchors:
    - `doctrine/compiler.py:1504`
    - `doctrine/compiler.py:1515`
    - `doctrine/flow_renderer.py:28`
    - `doctrine/flow_renderer.py:435`
    - `doctrine/diagnostic_smoke.py:652`
    - `docs/EMIT_GUIDE.md:181`
    - `README.md:160`
    - `examples/README.md:51`
    - `examples/73_flow_visualizer_showcase/build_ref/AGENTS.flow.d2:36`
    - `examples/36_invalidation_and_rebuild/build_ref/AGENTS.flow.d2:27`
    - `examples/36_invalidation_and_rebuild/build_ref/AGENTS.flow.d2:53`
    - `uv run --locked python -m doctrine.verify_corpus --manifest examples/73_flow_visualizer_showcase/cases.toml`
    - `uv run --locked python -m doctrine.verify_corpus --manifest examples/36_invalidation_and_rebuild/cases.toml`
    - `make verify-diagnostics`
    - `make verify-examples`
  - Plan expects:
    - Preserved route-relevant graph order, a route-first vertical lane render,
      refreshed checked proofs for the showcase and reroute counterexample,
      widened diagnostics, and synced live docs.
  - Code reality:
    - The compiler preserves first-seen flow order, the renderer ships the
      route-first lane planner and vertical handoff layout, checked `.flow`
      proofs are updated for both required examples, live docs describe the
      shipped behavior, and all claimed verification signals passed in this
      audit.
  - Fix:
    - None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-11
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-11
recommended_flow: complete
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

Worklog: `docs/archive/FLOW_VISUALIZER_VERTICAL_AGENT_HANDOFF_LANES_2026-04-11_WORKLOG.md`

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly, a user running `emit_flow` on a
multi-agent handoff entrypoint will get a diagram where:

- the first routed owner in the main flow appears at the top of the main lane
- the normal owner-to-owner route reads vertically in stable order
- loop-backs and secondary routes are visible as attachments, not the primary
  structure
- shared inputs, shared carriers, and local outputs remain visible without
  flattening the handoff story into a generic graph
- the flagship showcase example and at least one other relevant flow proof
  still emit deterministically and pass verification

## 0.2 In scope

- renderer and graph-ordering changes needed to show the main lane vertically
- preserving or deriving lane start from existing route and entrypoint-order
  data
- rebalancing how shared inputs, shared outputs, and loop-back edges are laid
  out
- targeted proof, diagnostic, and doc updates needed to protect the new visual
  contract
- internal convergence across `emit_common`, `compiler`, `flow_renderer`,
  example proofs, and live docs if that is what it takes to keep one canonical
  path

## 0.3 Out of scope

- new Doctrine syntax such as `primary_agent`, `main_lane`, or a second
  authored route language
- a second CLI, visualization backend, or hand-maintained diagram surface
- changes to runtime Markdown emission
- solving every arbitrary graph-layout case beyond Doctrine's current
  handoff-first multi-agent model
- productized per-example override knobs unless deeper planning proves the
  existing semantics cannot carry the feature honestly

## 0.4 Definition of done (acceptance evidence)

- `emit_flow` on `examples/73_flow_visualizer_showcase` renders a vertical main
  lane that starts at `ProjectLead` and follows the normal handoff path before
  showing the return loop
- `emit_flow` on `examples/36_invalidation_and_rebuild` renders the reroute
  family route-first instead of alphabetically flattening the agents
- shared inputs, shared carrier output, and local outputs remain visible, but
  the handoff lane is visually primary
- the checked `.flow.d2` and `.flow.svg` proof artifacts update deterministically
  for both shipped counterexamples
- the smallest credible preservation signals stay green, likely including the
  existing manifest-backed proofs plus any widened smoke coverage that protects
  ordering or renderer structure

## 0.5 Key invariants (fix immediately if violated)

- One compiler-owned visualization path: `emit_flow` -> graph extraction -> D2
  render -> SVG render.
- Lane start is derived from the shipped route path first and only falls back
  to declaration order when no stronger start signal exists.
- Authored route order must not be destroyed before layout decisions are made.
- Shared inputs, shared carriers, and local outputs are secondary visual
  attachments around the lane, not co-equal layout drivers.
- No new parallel layout mode, runtime shim, or fallback path.
- If the route-derived start rule fails on shipped multi-agent examples, stop
  and correct the architecture before implementation rather than silently
  weakening the contract.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Make the main handoff path readable at a glance.
2. Preserve compiler-owned truth and the existing `emit_flow` ownership path.
3. Keep `.flow.d2` deterministic and diff-friendly.
4. Stay within the shipped language unless repo evidence proves that is not
   enough.

## 1.2 Constraints

- The current renderer groups all agents into one `agent_handoffs` section and
  lays that section out horizontally.
- The current graph extraction path sorts agents and edges before render time,
  which risks erasing authored lane order.
- Checked example artifacts and manifest-backed proof must stay aligned with
  shipped behavior.
- The target-scoped and direct-entrypoint `emit_flow` paths must continue to
  converge onto the same canonical emission flow.

## 1.3 Architectural principles (rules we will enforce)

- Main-lane routing comes first; shared entities attach around it.
- Reuse the existing compiler-owned path instead of introducing a shadow graph
  or alternate renderer stack.
- Prefer hard cutover to one clearer layout over optional dual-layout drift.
- Fail loud if the main lane cannot be derived honestly from the shipped graph
  semantics.

## 1.4 Known tradeoffs (explicit)

- A handoff-first layout may optimize readability of the normal route over
  generic graph symmetry for unusual branch-heavy flows.
- Treating the first routed source as the primary start signal and declaration
  order as fallback is a deliberate simplification until deeper planning proves
  a stronger existing signal or a real gap.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already ships a compiler-owned flow visualizer through
`doctrine.emit_flow`. The current path extracts a `FlowGraph`, groups nodes
into shared inputs, local inputs, agent handoffs, shared outputs and carriers,
and local outputs, then renders D2 and SVG artifacts. The flagship showcase
already encodes a clear lead -> research -> writing -> lead route loop.

## 2.2 What's broken / missing (concrete)

The visualizer currently makes the flow feel like a big graph instead of a
stepwise handoff. The agent strip reads horizontally, shared-edge density
competes with the actual route path, and the first owner has no privileged
visual position. The result is truthful but not aligned with how these agents
actually work.

## 2.3 Constraints implied by the problem

The fix has to stay on the shipped `emit_flow` path, preserve deterministic
proof artifacts, and avoid inventing a new authored language surface unless the
existing graph semantics cannot support the new layout honestly. The likely
solution touches both ordering preservation in graph extraction and the layout
strategy in the D2 renderer.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- No external anchor is adopted yet.
  - Repo truth already exposes the current owner path, the current flattening
    failure, and a concrete counterexample to the earlier "first concrete
    agent" assumption.
  - External flow-diagram prior art is only worth adding if deep-dive still
    leaves the lane-start rule or branch/loop rendering ambiguous.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/emit_flow.py`
    - `emit_target_flow(...)` is the canonical flow path: parse entrypoint ->
      resolve root concrete agents -> extract compiler-owned `FlowGraph` ->
      render deterministic `.flow.d2` -> render `.flow.svg`.
  - `doctrine/emit_common.py`
    - `root_concrete_agents(...)` preserves concrete-agent declaration order
      from the entrypoint.
    - This is a useful fallback ordering signal, but research shows it is not a
      universal lane-start rule by itself.
  - `doctrine/compiler.py`
    - `extract_target_flow_graph(...)` iterates root agents in provided order,
      collects route edges from authored workflow sections and workflow-law
      routes, and therefore sees a believable handoff sequence before render
      time.
    - The same function then sorts `agents` and `edges` before returning
      `FlowGraph`, which erases authored or insertion order before the renderer
      can use it.
  - `doctrine/flow_renderer.py`
    - `render_flow_d2(...)` groups nodes into shared/local sections and places
      `agent_handoffs` as `list(graph.agents)`.
    - `_render_section(...)` forces section `direction: right`, which produces
      the flat agent strip even though the graph root direction is `down`.
  - `doctrine/diagnostic_smoke.py`
    - `_check_emit_flow_direct_mode_groups_shared_surfaces()` protects grouped
      shared surfaces and direct-mode success.
    - Current smoke coverage does not protect main-lane ordering or vertical
      handoff layout.
  - `examples/73_flow_visualizer_showcase/prompts/AGENTS.prompt`
    - The flagship showcase is a clean lead -> research -> writing -> lead
      handoff loop and is still the best proof target for a lane-style render.
  - `examples/07_handoffs/prompts/AGENTS.prompt`
    - The earlier handoff example also encodes an explicit same-issue owner
      order and strengthens the case for a handoff-first render.
  - `examples/36_invalidation_and_rebuild/prompts/AGENTS.prompt`
    - This example is the important counterexample: the first concrete agent is
      `RoutingOwner`, but the routed sources are `StructureChangeDemo` and
      `BlockedSectionReviewDemo`.
    - The checked `build_ref/AGENTS.flow.d2` is alphabetized today, which hides
      the authored route story and proves that "first concrete agent is always
      the lane start" would be the wrong universal rule.

- Canonical path / owner to reuse:
  - `doctrine/emit_flow.py` -> `doctrine/compiler.py` -> `doctrine/flow_renderer.py`
    - This is the one compiler-owned path that should own ordering preservation
      and layout correction.

- Existing patterns to reuse:
  - `doctrine/emit_common.py` direct-entrypoint and configured-target
    convergence
    - Keep one emit pipeline; do not fork a second visualizer path.
  - `doctrine/flow_renderer.py` shared-input and shared-output classification
    - Keep shared entities visible, but attach them around the lane instead of
      letting them define the whole layout.
  - `examples/73_flow_visualizer_showcase`
    - Use as flagship proof for the vertical-lane behavior.
  - `examples/36_invalidation_and_rebuild`
    - Use as the branch and reroute sanity-check so the new rule does not only
      fit the happy-path showcase.

- Duplicate or drifting paths relevant to this change:
  - `docs/archive/MULTI_AGENT_SHARED_IO_FLOW_VISUALIZER_2026-04-11.md`
    - Historical planning context only, not a live owner path.
  - `examples/*/build_ref/AGENTS.flow.{d2,svg}`
    - Checked proof surfaces, not renderer logic owners.

- Capability-first opportunities before new tooling:
  - Preserve route insertion order in `FlowGraph` before inventing new Doctrine
    syntax or manual layout metadata.
  - Derive lane start from routed-source order or route topology before falling
    back to declaration order.
  - Reweight renderer layout around route edges before introducing per-example
    knobs, override files, or a second graph model.

- Behavior-preservation signals already available:
  - `uv run --locked python -m doctrine.emit_flow --target example_73_flow_visualizer_showcase`
    - Flagship emitted proof for the main lane render.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/73_flow_visualizer_showcase/cases.toml`
    - Manifest-backed proof for the flagship example.
  - `uv run --locked python -m doctrine.emit_flow --target example_36_invalidation_and_rebuild`
    - Sanity check for reroute and branch-heavy flow behavior.
  - `make verify-examples`
    - Corpus-wide proof when checked flow artifacts change.
  - `doctrine/diagnostic_smoke.py::_check_emit_flow_direct_mode_groups_shared_surfaces`
    - Current smoke baseline to widen rather than replace.

## 3.3 Open questions from research

- No blocking research questions remain after deep-dive pass 2.
- The target architecture now fixes:
  - lane-start selection
  - forward-path versus loop-back and secondary-edge treatment
  - standalone non-routed agent anchoring
  - counterexample proof retention on the current shipped language surface
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/emit_flow.py`
  - public flow-emission CLI and canonical owner of `.flow.d2` / `.flow.svg`
    output
- `doctrine/emit_common.py`
  - configured-target and direct-entrypoint resolution plus concrete root-agent
    discovery
- `doctrine/compiler.py`
  - `FlowGraph` dataclasses, graph extraction, route-edge collection, and I/O
    summaries
- `doctrine/flow_renderer.py`
  - D2 layout construction and pinned SVG render handoff
- `doctrine/diagnostic_smoke.py`
  - direct-mode emit smoke and current grouped-shared-surface coverage
- `doctrine/verify_corpus.py`
  - manifest-backed build-contract verification path that can re-emit flow
    artifacts into a temp tree and diff them against checked `build_ref/`
- `pyproject.toml`
  - flow-capable configured targets including `example_07_handoffs`,
    `example_36_invalidation_and_rebuild`, and
    `example_73_flow_visualizer_showcase`
- `examples/73_flow_visualizer_showcase/`
  - flagship checked flow proof and current public visualizer story
- `examples/36_invalidation_and_rebuild/`
  - branch and reroute counterexample with checked flow artifacts and an
    existing `build_contract` manifest case

## 4.2 Control paths (runtime)

1. `doctrine.emit_flow:main(...)` resolves either configured targets or direct
   mode and calls `emit_target_flow(...)`.
2. `emit_target_flow(...)` parses the entrypoint, resolves root concrete agents
   via `root_concrete_agents(...)`, and constructs one `CompilationSession`.
3. `CompilationSession.extract_target_flow_graph(agent_names)` collects agent,
   input, output, consume, produce, authored-route, and law-route data into a
   `FlowGraph`.
4. `render_flow_d2(graph)` classifies nodes into shared/local sections and
   emits one deterministic `.flow.d2`.
5. `render_flow_svg(...)` renders the matching `.flow.svg` from that D2 source
   with the pinned local D2 package.
6. For checked proof, `verify_corpus._run_build_contract(...)` emits docs and,
   when `build_ref/` contains flow artifacts, emits flow artifacts into a temp
   directory and diffs them against the checked tree.

## 4.3 Object model + key abstractions

- `FlowGraph` today contains only:
  - `agents`
  - `inputs`
  - `outputs`
  - `edges`
- `FlowEdge.kind` distinguishes:
  - `consume`
  - `produce`
  - `authored_route`
  - `law_route`
- During extraction, root agents are traversed in the order passed from
  `root_concrete_agents(...)`, and route edges are appended as workflow
  sections or workflow-law statements are encountered. Meaningful route order
  exists transiently.
- At return time, `extract_target_flow_graph(...)` sorts agents, inputs,
  outputs, and edges, which erases the route-first sequencing before the
  renderer can use it.
- `render_flow_d2(...)` then builds a section-first layout:
  - `shared_inputs`
  - `local_inputs`
  - `agent_handoffs`
  - `shared_outputs_and_carriers`
  - `local_outputs`
- `_render_section(...)` forces `direction: right` for every section, so the
  agent strip becomes horizontal even though the graph root direction is
  `down`.
- Shared consume and produce edges are rendered alongside route edges with no
  separate lane plan, so they compete visually with the handoff story.

## 4.4 Observability + failure behavior today

- `examples/73_flow_visualizer_showcase/cases.toml` is already a
  `build_contract`, so its checked flow artifacts are re-emitted and diffed by
  the corpus verifier.
- `examples/36_invalidation_and_rebuild/build_ref/AGENTS.flow.{d2,svg}` exists,
  and `cases.toml` already includes a `build_contract`, so the branch-heavy
  flow artifact is also diffed by the corpus verifier today.
- `doctrine/diagnostic_smoke.py` currently protects:
  - entrypoint-stem output naming
  - direct-mode success
  - grouped shared-input/shared-output surface rendering
- It does not yet protect:
  - lane-start selection
  - route-order preservation
  - vertical handoff layout
  - loop-back versus secondary-edge treatment
- Current failures are mostly truthful-but-hard-to-read layout failures, not
  parser, compiler, or CLI failures.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Current flagship shape, simplified:

```text
Shared Inputs
  ProjectBrief   AudienceGuide

Agent Handoffs
  ProjectLead -> ResearchSpecialist -> WritingSpecialist

Shared Outputs / Carriers
  SharedHandoff

Local Outputs
  ExecutionPlan   ResearchPacket   LaunchDraft

Plus many crossing consume/produce edges.
```

Current branch / reroute counterexample, simplified:

```text
CurrentHandoff

BlockedSectionReviewDemo   RebuildSectionReviewDemo   RoutingOwner   StructureChangeDemo

BlockedSectionReviewDemo -> RoutingOwner
StructureChangeDemo      -> RoutingOwner

Produced outputs are grouped below, but the current checked flow is alphabetized
and does not foreground the routed story.
```
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

The canonical owner path stays the same:

- `doctrine/emit_flow.py` remains the only public flow-emission surface
- `doctrine/compiler.py` remains the only graph-extraction owner
- `doctrine/flow_renderer.py` remains the only D2 layout owner

The intended cut is an internal contract correction, not a new feature surface:

- no new Doctrine syntax such as `primary_agent` or `main_lane`
- no second graph model
- no second renderer or CLI
- no per-example override file

The only expected new truth surfaces are:

- updated checked flow proofs
- widened smoke coverage
- no new manifest family is required because `examples/36_invalidation_and_rebuild`
  is already an honest build-contract proof surface

## 5.2 Control paths (future)

1. `emit_flow` entrypoint resolution and output-path behavior stay unchanged.
2. `CompilationSession.extract_target_flow_graph(...)` preserves deterministic
   insertion order for agents and route-relevant edges instead of sorting away
   layout-relevant sequence.
3. `render_flow_d2(...)` derives a route-first layout plan from the route-edge
   subgraph using both `authored_route` and `law_route`.
4. Lane-start selection follows one canonical rule:
   - prefer routed sources with zero route in-degree, in first-seen order
   - if the routed subgraph is cyclic and has no zero-in-degree source, use the
     first route source encountered during extraction
   - if there are no route edges at all, fall back to root concrete agent order
5. Main-lane construction follows one canonical rule:
   - use the first lane start as the primary vertical spine
   - at each lane node, use the first-seen outgoing route edge whose target is
     not already on the current spine as the forward edge
   - render any remaining edge that targets an earlier spine node as a loop-back
   - render any remaining outgoing route edges as secondary connectors
   - when multiple routed starts exist, render them as stacked route-first
     starts in the same vertical family rather than collapsing back to an
     alphabetical strip
6. Standalone non-routed agents follow one canonical rule:
   - render them as secondary vertical stacks after the route-first family,
     ordered by first-seen agent order
   - attach their local outputs and shared-edge participation to those stacks
     without making them the primary lane
7. Shared inputs, shared carriers, and local outputs attach around the lane
   instead of determining the overall layout.

## 5.3 Object model + abstractions (future)

- Keep `FlowGraph` as the single compiler-owned graph object.
- Do not add manual art-direction metadata to the prompt language.
- Preserve order where it is already meaningful:
  - root concrete agent order from `root_concrete_agents(...)`
  - route-edge encounter order from workflow traversal
  - deterministic traversal of outputs and inputs where they attach to a given
    agent
- Add a renderer-local lane planner that derives:
  - ordered route edges
  - lane starts
  - primary-lane agents
  - loop-back and secondary route connectors
  - side attachments for shared inputs and outputs
- Treat both `authored_route` and `law_route` as lane-defining edges for
  layout, while preserving distinct edge styling so workflow-law reroutes still
  read as different from authored workflow handoffs.
- Declaration order is a fallback stability signal, not the primary semantic
  owner of lane start when route data is available.

## 5.4 Invariants and boundaries

- `emit_flow` remains the single source of truth for flow artifacts.
- Route-first ordering must survive from extraction to render time.
- No second visual mode or compatibility shim is allowed; one route-first
  layout algorithm must handle chain, loop, and simple convergence cases.
- Shared entities remain visible but cannot flatten the handoff story back into
  a generic graph.
- The same prompt must continue to produce deterministic `.flow.d2` and
  `.flow.svg` output.
- `examples/73_flow_visualizer_showcase` and
  `examples/36_invalidation_and_rebuild` remain the required manifest-backed
  proof pair for this feature unless a later plan explicitly replaces one of
  them with stronger shipped proof.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Target chain-like handoff shape:

```text
Shared Inputs
ProjectBrief
AudienceGuide
     |
     v
ProjectLead
ResearchSpecialist
WritingSpecialist
     ^
     | loop-back / return

Local Outputs / Shared Carrier Below
ExecutionPlan
ResearchPacket
LaunchDraft
SharedHandoff
```

Target convergence / reroute shape:

```text
Shared Input
CurrentHandoff
     |
     v
Route-First Lane Family
StructureChangeDemo
BlockedSectionReviewDemo  -> RoutingOwner

Standalone Secondary Lane
RebuildSectionReviewDemo

Outputs / Carriers Below
InvalidationHandoff
BlockedReviewHandoff
SectionMetadata
RebuildHandoff
SectionReview
```
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Root-order fallback | `doctrine/emit_common.py` | `root_concrete_agents(...)` | Preserves entrypoint declaration order for concrete agents | Keep as the no-route fallback ordering signal; do not promote it to the universal start rule | Research showed declaration order alone is insufficient for routed counterexamples | No public API change; fallback semantics are clarified in the plan | Indirectly exercised by flow emit proof and smoke |
| Graph sequencing | `doctrine/compiler.py` | `extract_target_flow_graph(...)` | Sorts agents, inputs, outputs, and edges before returning `FlowGraph` | Preserve deterministic insertion order for route-relevant graph sequencing instead of sorting away the handoff path | Sorting erases the route-first story before layout | Internal `FlowGraph` sequencing contract changes; public CLI unchanged | `example_73` emit/build-contract, `example_36` emit/build-contract or targeted proof, smoke |
| Route-edge collection | `doctrine/compiler.py` | workflow section route collection and workflow-law route collection | Captures `authored_route` and `law_route` edges, but they are not treated as a lane plan | Keep both route kinds in stable order so the renderer can derive lane start and main path | Vertical handoff layout must treat route edges as primary structure | Internal render input contract only | Same as above |
| Route-first lane planner | `doctrine/flow_renderer.py` | `render_flow_d2(...)` and new route-layout helpers | Builds a section-first render and lets shared edges compete equally with route edges | Derive lane starts, primary spine, loop-backs, and secondary connectors from the route-edge subgraph | Current render is truthful but visually wrong for handoff workflows | Internal render-model contract only | `example_73` / `example_36` flow proofs, smoke |
| Agent section layout | `doctrine/flow_renderer.py` | `_render_section(...)`, agent container shape, node placement helpers | Forces `direction: right` and flattens all agents into one horizontal strip | Render the primary handoff lane vertically and attach shared entities around it | The visible bug is the flat agent strip | Internal D2 layout contract only | Flow proof, smoke |
| Flagship flow proof | `examples/73_flow_visualizer_showcase/build_ref/AGENTS.flow.{d2,svg}` | checked flow artifacts | Current checked proof shows the flat strip layout | Regenerate deterministic route-first vertical-lane proof | This is the main public truth surface for the feature | None | Existing build-contract manifest, `make verify-examples` |
| Branch / reroute flow proof | `examples/36_invalidation_and_rebuild/build_ref/AGENTS.flow.{d2,svg}` | checked flow artifacts | Current checked proof is manifest-backed but visually alphabetized | Regenerate the route-first convergence proof on the existing build-contract surface | This is the main counterexample to the original lane-start assumption | No new manifest contract; existing build-contract remains authoritative | `verify_corpus`, `make verify-examples` |
| Counterexample manifest | `examples/36_invalidation_and_rebuild/cases.toml` | existing `build_contract` case | Already protects the checked flow tree | Keep the existing manifest aligned and treat it as required preservation coverage | The route-first change must keep the counterexample proof green, not just the flagship showcase | No new manifest shape | `verify_corpus`, `make verify-examples` |
| Diagnostic smoke | `doctrine/diagnostic_smoke.py` | `_check_emit_flow_direct_mode_groups_shared_surfaces()` and adjacent flow smoke coverage | Confirms grouped shared surfaces and direct mode but not lane ordering | Add the smallest stable D2 assertions for route-first ordering and vertical handoff layout | Prevent regressions from re-flattening the main lane | None | `make verify-diagnostics` if touched |
| Live docs and README | `docs/EMIT_GUIDE.md`, `README.md`, `examples/README.md` | flow visualizer reading guidance and example description | Current prose teaches a generic graph with grouped shared surfaces | Update reading guidance only if the shipped route-first semantics become visible enough to change how users should read the artifact | Touched live docs must match shipped truth | No code contract | Manual doc sync, optional diff review |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `doctrine/emit_flow.py` -> `doctrine/compiler.py` -> `doctrine/flow_renderer.py`
- Deprecated APIs (if any):
  - None expected. This is an internal layout-contract correction.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - No code-path deletes are expected yet.
  - No proof-surface deletes are planned in pass 2 because the existing
    counterexample flow refs are already manifest-backed.
- Capability-replacing harnesses to delete or justify:
  - None. This change should ride the existing compiler and render path.
- Live docs/comments/instructions to update or delete:
  - `docs/EMIT_GUIDE.md`, `README.md`, and `examples/README.md` if their
    current graph-first reading guidance becomes stale after the route-first
    render lands.
- Behavior-preservation signals for refactors:
  - `uv run --locked python -m doctrine.emit_flow --target example_73_flow_visualizer_showcase`
  - `uv run --locked python -m doctrine.emit_flow --target example_36_invalidation_and_rebuild`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/73_flow_visualizer_showcase/cases.toml`
  - `make verify-examples` after checked proof surfaces or manifests change
  - `make verify-diagnostics` if smoke coverage changes

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Branch-heavy proof retention | `examples/36_invalidation_and_rebuild/cases.toml` and `build_ref/` | Keep the existing counterexample `build_contract` in the required verification set | Prevent route-first counterexample proof from drifting silently while only the flagship showcase stays green | include |
| Live docs alignment | `docs/EMIT_GUIDE.md`, `README.md`, `examples/README.md` | Teach route-first reading guidance if shipped behavior changes visibly | Prevent stale graph-first public docs after the layout cutover | include |
| Additional handoff sanity check | `examples/07_handoffs` | Use existing emit target as optional local sanity check for same-issue lane flows | Helpful extra confidence, but not required if `example_73` plus `example_36` cover the risk | defer |
| Emit configuration | `pyproject.toml` | Add new targets or new modes | No new owner path or config surface is needed for this feature | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Preserve route-relevant graph ordering

* Goal:
  Make the compiler carry the route-first sequencing the renderer needs without
  changing the public `emit_flow` surface or the prompt language.
* Status: COMPLETE
* Completed work:
  - `doctrine/compiler.py` now preserves first-seen flow-node and edge order in
    `FlowGraph` instead of sorting away routed handoff sequence before render
    time.
  - The compiler boundary now documents that this preserved order is part of
    the renderer contract.
* Work:
  Update `doctrine/compiler.py` so `extract_target_flow_graph(...)` preserves
  deterministic insertion order for route-relevant agents and edges instead of
  sorting away the handoff story. Keep `authored_route` and `law_route` in one
  stable encounter order and preserve declaration order only as fallback
  stability data.
* Verification (smallest signal):
  Run `uv run --locked python -m doctrine.emit_flow --target example_73_flow_visualizer_showcase`
  and `uv run --locked python -m doctrine.emit_flow --target example_36_invalidation_and_rebuild`
  to confirm the emitted D2 now reflects deterministic route-first ordering
  before the renderer layout pass lands.
* Docs/comments (propagation; only if needed):
  Add one short code comment at the canonical ordering boundary only if the new
  insertion-order contract would otherwise be easy to accidentally "clean up"
  back into sorting.
* Exit criteria:
  The compiler emits a deterministic `FlowGraph` whose route-relevant order is
  preserved through to render time, and no new prompt syntax or alternate graph
  model exists.
* Rollback:
  Revert to the current sorted graph return path and leave the old checked flow
  refs in place until the route-first contract is ready to land as one cut.

## Phase 2 — Implement the route-first lane renderer

* Goal:
  Turn the preserved route ordering into the shipped vertical lane layout for
  both the flagship handoff chain and the branch-heavy counterexample.
* Status: COMPLETE
* Completed work:
  - `doctrine/flow_renderer.py` now plans a route-first lane with one primary
    lane, secondary routed starts, and standalone secondary stacks.
  - Pure handoff chains render through a downward main lane, while convergence
    cases keep routed starts grouped beside the primary owner path.
  - Shared inputs and outputs remain visible, but they no longer define one flat
    horizontal agent strip.
* Work:
  Rework `doctrine/flow_renderer.py` so it derives:
  route starts, the primary vertical spine, loop-back edges, secondary route
  connectors, and standalone secondary lanes for non-routed agents. Keep shared
  inputs, shared carriers, and local outputs attached around those lanes
  instead of defining the overall structure. Preserve distinct styling for
  `authored_route` versus `law_route`.
* Verification (smallest signal):
  Run the two targeted `emit_flow` commands again and inspect the emitted
  `.flow.d2` source for:
  route-first lane ordering, vertical handoff layout, loop-back placement, and
  standalone secondary-lane anchoring.
* Docs/comments (propagation; only if needed):
  Add one short comment inside the renderer if the lane-planning rules are
  non-obvious enough that a future cleanup pass could collapse them back into a
  generic section-first layout.
* Exit criteria:
  `example_73` reads as a top-to-bottom handoff lane and `example_36` reads as
  a route-first reroute family with `RebuildSectionReviewDemo` anchored as a
  secondary stack, without introducing dual layout modes.
* Rollback:
  Revert the renderer to the current grouped horizontal-strip layout while
  keeping Phase 1 ordering work local and unshipped if the route-first render
  cannot land cleanly in the same cut.

## Phase 3 — Refresh proof and regression coverage

* Goal:
  Make the new route-first layout a checked, regression-resistant shipped truth
  surface instead of a local visual tweak.
* Status: COMPLETE
* Completed work:
  - Refreshed checked `AGENTS.flow.{d2,svg}` artifacts for
    `examples/73_flow_visualizer_showcase` and
    `examples/36_invalidation_and_rebuild`.
  - Widened `doctrine/diagnostic_smoke.py` with route-first lane assertions so
    the showcase smoke now fails if the main lane collapses back into a flat
    strip.
* Work:
  Regenerate checked `AGENTS.flow.{d2,svg}` refs for
  `examples/73_flow_visualizer_showcase` and
  `examples/36_invalidation_and_rebuild`. Widen
  `doctrine/diagnostic_smoke.py` with the smallest stable assertions that prove
  route-first ordering and vertical handoff layout without hard-coding brittle
  SVG constants. Keep `examples/36_invalidation_and_rebuild/cases.toml`
  aligned with its existing `build_contract`.
* Verification (smallest signal):
  Run:
  `uv run --locked python -m doctrine.verify_corpus --manifest examples/73_flow_visualizer_showcase/cases.toml`
  `uv run --locked python -m doctrine.verify_corpus --manifest examples/36_invalidation_and_rebuild/cases.toml`
  and `make verify-diagnostics` if smoke coverage changed.
* Docs/comments (propagation; only if needed):
  None unless smoke assertions need one terse explanatory comment at the
  ordering-sensitive assertion point.
* Exit criteria:
  Both shipped counterexample examples stay green as manifest-backed proof, and
  smoke coverage protects the route-first layout strongly enough that a future
  flattening regression would fail for the right reason.
* Rollback:
  Restore the prior checked refs and smoke assertions together if the new proof
  surfaces cannot be made deterministic in the same change.

## Phase 4 — Sync live docs and run final closeout verification

* Goal:
  Ensure the live public story matches the shipped route-first visualizer and
  that the final repo checks are run once, not piecemeal.
* Status: COMPLETE
* Completed work:
  - Updated `docs/EMIT_GUIDE.md`, `README.md`, and `examples/README.md` so the
    live docs describe the route-first lane instead of a generic graph-only
    reading.
  - Re-ran `make verify-diagnostics` and `make verify-examples` after the final
    checked-ref refresh.
* Manual QA (non-blocking):
  - Reviewed the generated showcase SVG locally via a Quick Look PNG thumbnail
    to confirm the final render reads as a top-down handoff lane with a visible
    return loop.
* Work:
  Update `docs/EMIT_GUIDE.md`, `README.md`, and `examples/README.md` only where
  the reading guidance or example framing is now stale because the visualizer
  is route-first instead of graph-first. Then run the final repo verification
  path for the touched surfaces.
* Verification (smallest signal):
  Run `make verify-examples`. Also run `make verify-diagnostics` if not already
  covered in Phase 3. Finish with a human read of the generated showcase SVG.
* Docs/comments (propagation; only if needed):
  The live docs updates in this phase are required if the shipped behavior
  changes how users should read the artifact; no legacy explanation should be
  left behind.
* Exit criteria:
  Live docs, checked proof artifacts, and repo verification all agree on the
  route-first visualizer behavior, and the final showcase SVG reads cleanly to
  a human.
* Rollback:
  Revert live-doc wording with the proof-surface rollback if the route-first
  cut does not ship.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

Keep verification small and behavior-level. Prefer the smallest existing
signals, default to one targeted flow emit plus the smallest relevant repo
checks, and avoid new harnesses unless an existing smoke or corpus proof cannot
cover the risk honestly.

## 8.1 Unit tests (contracts)

- Prefer widening existing smoke coverage over creating a new bespoke test
  harness.
- If graph-order preservation is subtle, add the smallest deterministic
  assertion that would fail for the right reason.

## 8.2 Integration tests (flows)

- `uv run --locked python -m doctrine.emit_flow --target example_73_flow_visualizer_showcase`
- `uv run --locked python -m doctrine.emit_flow --target example_36_invalidation_and_rebuild`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/73_flow_visualizer_showcase/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/36_invalidation_and_rebuild/cases.toml`
- `make verify-diagnostics` only if diagnostics coverage changes
- `make verify-examples` before closeout if shipped proof surfaces or manifests change

## 8.3 E2E / device tests (realistic)

None expected. Manual SVG inspection is finalization-only and should stay
non-blocking until the canonical proof artifacts and repo checks are clean.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

Hard cut over on the canonical `emit_flow` path. Regenerate the checked proof
artifacts in the same change so the vertical handoff view becomes the only
shipped visual contract.

## 9.2 Telemetry changes

None expected. This is a local emit and docs surface, not a runtime telemetry
feature.

## 9.3 Operational runbook

- `uv sync`
- `npm ci`
- rerun the showcase target through `emit_flow`
- rerun the showcase and counterexample manifest-backed proofs
- run the broader repo verification path needed by the touched surfaces
- visually inspect the generated showcase SVG before calling the change done

# 10) Decision Log (append-only)

## 2026-04-11 - Start a follow-on plan for vertical handoff lanes

### Context

Doctrine already ships a broader flow visualizer plan and implementation, but
the current output still reads like a generic graph. The new requirement is to
make the visualizer read like the actual owner-to-owner flow, starting from the
first agent.

### Options

1. Add new Doctrine language syntax for a primary agent or main lane.
2. Keep the generic graph model and tune styles only.
3. Treat this as a compiler and renderer contract correction on the existing
   language surface.

### Decision

Start with option 3. The existing language already carries concrete agents,
route edges, shared inputs, and shared carriers. The first planning pass will
assume the feature can stay on the current language surface unless deeper
research proves that assumption false.

### Consequences

This plan is biased toward preserving and exposing ordering that already exists
in the repo instead of inventing a new authored feature. That likely means
graph-order preservation plus renderer rework, not a language-surface change.

### Follow-ups

- Confirm that first concrete agent is the right lane-start rule for shipped
  examples.
- Confirm whether route order alone is enough to derive the main lane cleanly.

## 2026-04-11 - Correct the lane-start assumption during research

### Context

The first draft of this plan treated "first concrete agent in the entrypoint"
as the likely start of the main lane. Research against shipped examples showed
that this is too weak as a universal rule.

### Options

1. Keep first concrete agent as the universal lane-start rule.
2. Derive lane start from routed-source order or route topology, with
   declaration order only as fallback.
3. Add new Doctrine syntax to mark the lane start explicitly.

### Decision

Adopt option 2 for planning. The showcase example still aligns with the first
declared routed owner, but `examples/36_invalidation_and_rebuild` shows that
the first concrete agent can be a reroute owner instead of the real start of
the flow. The plan now treats route-derived start as primary and declaration
order as fallback.

### Consequences

Deep-dive now needs to specify the exact lane-start derivation rule instead of
assuming root declaration order is sufficient. This still stays on the shipped
language surface and does not yet justify new syntax.

### Follow-ups

- Decide whether routed-source order alone is enough or whether route topology
  must participate in start selection.
- Decide how standalone non-routed agents such as `RebuildSectionReviewDemo`
  anchor to the route-first lane family without flattening the layout.

## 2026-04-11 - Choose a route-first layout plan for deep-dive pass 1

### Context

Research showed that the existing graph extraction path sees meaningful route
order before render time, but the returned `FlowGraph` is sorted and the D2
renderer then lays all agents out horizontally. The plan now needs an actual
target architecture instead of a general intent statement.

### Options

1. Preserve the current sorted graph contract and only restyle the SVG.
2. Keep one `FlowGraph`, preserve insertion order, and let the renderer derive
   a route-first lane plan from `authored_route` and `law_route`.
3. Add new prompt-level lane metadata or a second graph model.

### Decision

Adopt option 2. The target architecture keeps one compiler-owned graph model,
preserves deterministic encounter order where it already exists, and derives
the main lane from the routed subgraph. Declaration order remains only the
fallback when no better route-derived start signal exists.

### Consequences

Implementation likely touches both `doctrine/compiler.py` and
`doctrine/flow_renderer.py`, plus proof and smoke surfaces. This still avoids
new Doctrine syntax and keeps the change on the canonical visualizer path.

### Follow-ups

- Decide whether the lane-start algorithm can stop at routed-source order or
  needs route-topology tie-breaking.
- Decide whether `examples/36_invalidation_and_rebuild` flow refs become
  manifest-backed proof in the same cut.

## 2026-04-11 - Split execution into four foundational phases

### Context

Deep-dive pass 2 locked the route-first algorithm and the required proof pair.
The remaining question for planning was execution order: how to ship the change
without mixing graph-contract work, renderer work, proof refresh, and live-doc
sync into one blurry implementation pass.

### Options

1. Collapse the work into one broad implementation phase plus verification.
2. Split the work into compiler-ordering, renderer, proof/regression, and
   docs/final-verification phases.
3. Pull optional extra examples such as `example_07_handoffs` into the required
   checklist up front.

### Decision

Adopt option 2. The authoritative checklist now has four phases:

- preserve route-relevant graph ordering
- implement the route-first lane renderer
- refresh proof and regression coverage
- sync live docs and run final closeout verification

`example_07_handoffs` stays deferred and does not block the execution plan.

### Consequences

Implementation can now proceed depth-first without reopening architecture
questions. Preservation proof and live-doc sync are explicit work, not cleanup
afterthoughts.

### Follow-ups

- Re-evaluate whether `example_07_handoffs` should be pulled into required
  verification only if implementation exposes a concrete same-issue coverage
  gap.

## 2026-04-11 - Lock the pass-2 route-first algorithm and proof pair

### Context

Deep-dive pass 1 selected a route-first architecture but still left two
important ambiguities: how the main lane start is chosen in branch-heavy cases,
and whether the branch-heavy counterexample proof needs new manifest work. A
fresh read of the shipped proof surfaces resolved both.

### Options

1. Keep the lane-start and standalone-agent rules open until implementation.
2. Lock the route-topology tie-break, forward-edge rule, standalone secondary
   lane rule, and keep the existing `example_36` build-contract proof in scope.
3. Reopen the architecture and add explicit prompt-level metadata to avoid the
   remaining choices.

### Decision

Adopt option 2. The pass-2 target architecture now fixes:

- zero-route-in-degree starts first, then first-seen route source as the cycle
  fallback
- first unseen outgoing route edge as the forward edge
- earlier-target edges as loop-backs
- remaining routed edges as secondary connectors
- standalone non-routed agents as secondary vertical stacks after the route-
  first family
- `examples/73_flow_visualizer_showcase` plus
  `examples/36_invalidation_and_rebuild` as the required manifest-backed proof
  pair

### Consequences

`phase-plan` no longer needs to guess about the lane algorithm or the proof
surface. The remaining work is execution ordering and verification, not
architecture discovery.

### Follow-ups

- Decide whether `examples/07_handoffs` stays a deferred optional sanity check
  or is pulled into the required execution checklist during phase planning.

## 2026-04-11 - Keep the overall render top-down after the lane planner landed

### Context

The route-first lane planner landed cleanly, but an intermediate render with a
left-to-right graph root still encouraged the showcase handoff chain to spread
sideways under D2's edge pressure. The user request was specifically about the
agents reading like a vertical stepwise flow.

### Options

1. Keep the whole graph left-to-right because it places inputs and outputs on
   the sides.
2. Keep the route-first lane planner but restore a top-down graph root so the
   main handoff path remains visually vertical.
3. Add more D2-specific art-direction machinery before shipping the feature.

### Decision

Adopt option 2. The shipped renderer now keeps the route-first lane planner,
but the overall graph direction is top-down so the main handoff chain reads
vertically in the emitted `.flow.svg`.

### Consequences

Shared inputs and outputs still stay grouped and visible, but they now anchor
above and below the agent section instead of forcing a horizontal overall
graph. The plan's target mockups and live docs were updated to match that
shipped reality.

### Follow-ups

- If later D2 work makes side attachment possible without weakening the
  vertical lane, revisit it as a separate visual polish change rather than in
  this cut.
