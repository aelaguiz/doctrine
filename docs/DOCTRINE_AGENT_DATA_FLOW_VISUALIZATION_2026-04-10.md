---
title: "Doctrine - Agent Data Flow Visualization - Architecture Plan"
date: 2026-04-10
status: complete
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: architectural_change
related:
  - docs/research_visualizations.md
  - doctrine/compiler.py
  - doctrine/emit_docs.py
  - doctrine/renderer.py
  - pyproject.toml
---

# TL;DR

## Outcome

Doctrine gains a framework-supported workflow data-flow visualizer that a repo
can run through one Doctrine-owned command or emit path against Doctrine prompt
entrypoints to get a readable, followable diagram of concrete agents, the
inputs they read, the outputs they emit, and the routes that hand work from one
agent to another.

## Problem

Today Doctrine can parse prompt files, compile one concrete agent at a time, and
emit Markdown trees through configured emit targets, but it cannot show the
multi-agent operational flow as one picture. Shared handoff outputs, shared
inputs, and route chains are therefore hard to inspect without manually reading
multiple emitted files and reconstructing the graph by hand.

## Approach

Add one Doctrine-owned visualization surface on top of the existing parse ->
compile -> emit pipeline instead of building a repo-local analyzer or a second
parser. Reuse the existing emit target model, extract a renderer-neutral
workflow graph from compiler-owned semantics, and ship a static-first D2 output
path as the first supported artifact. The initial feature stays focused on
operational data flow: concrete agent nodes, input nodes, output nodes,
consumes edges, produces edges, and route edges, with shared data contracts
deduplicated as first-class graph anchors and with layout and rendering choices
optimized for tall, readable flow inspection rather than maximum semantic
density.

## Plan

1. Add a compiler-owned target-level graph extraction boundary on
   `CompilationContext`.
2. Add a sibling `emit_flow` command that reuses existing emit targets and
   emits deterministic `.flow.d2` output.
3. Add same-command `.flow.svg` rendering only through a pinned, fail-loud D2
   dependency path.
4. Prove the feature on one existing multi-agent build target through the
   shipped `build_contract` lane.
5. Update the live docs so the new command, artifact shape, and proof model are
   described consistently across Doctrine repos.

## Non-negotiables

- No inheritance graph or generic AST dump in v1.
- No repo-local shadow parser, analyzer, or ad hoc script as the primary path.
- No width-first sprawling output that is hard to follow in normal review
  contexts.
- No second source of truth for workflow structure outside compiler-owned
  concrete agent semantics.
- No framework surface that only works in this repo and not in ordinary Doctrine
  repos using prompt entrypoints.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-11
Verdict (code): COMPLETE
Manual QA: completed for `examples/36_invalidation_and_rebuild/build/AGENTS.flow.{d2,svg}`

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None. The planned compiler, emitter, proof, and docs surfaces are present.
  - Evidence anchors:
    - `doctrine/compiler.py`
    - `doctrine/emit_common.py`
    - `doctrine/emit_flow.py`
    - `doctrine/flow_renderer.py`
    - `doctrine/diagnostic_smoke.py`
    - `doctrine/verify_corpus.py`
    - `examples/36_invalidation_and_rebuild/build_ref/AGENTS.flow.d2`
    - `examples/36_invalidation_and_rebuild/build_ref/AGENTS.flow.svg`
    - `README.md`
    - `docs/README.md`
    - `docs/AGENT_IO_DESIGN_NOTES.md`
    - `examples/README.md`
    - `AGENTS.md`
  - Plan expects:
    - `Phase 1` lands compiler-owned graph extraction from concrete-turn I/O,
      authored routes, and workflow-law routes/currentness.
    - `Phase 2` adds a sibling `emit_flow` command with deterministic `.flow.d2`
      plus pinned same-command `.flow.svg`.
    - `Phase 3` proves the feature on `example_36_invalidation_and_rebuild`
      and updates live docs/instructions.
  - Code reality:
    - `CompilationContext` now extracts a target-scoped flow graph from
      compiler-owned semantics; `emit_flow` reuses the shared emit target
      registry and writes `.flow.d2` plus `.flow.svg`; the D2 dependency is
      pinned in repo-local `package.json` / `package-lock.json`; the build
      contract for example `36` now checks both flow artifacts; and the live
      docs plus repo instructions describe the new command and `npm ci`
      requirement.
  - Fix:
    - None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None required for this cut. The representative generated graph was checked
  manually in both D2 source and rendered SVG form during the proof update.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-10
external_research_grounding: done 2026-04-10
deep_dive_pass_2: done 2026-04-10
recommended_flow: implement-loop
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly, a Doctrine repo with configured prompt
entrypoints will be able to run one Doctrine-supported workflow-visualization
path and receive a readable artifact that shows:

- the concrete agents in the target workflow family
- the inputs each concrete agent consumes
- the outputs each concrete agent emits
- the explicit routes that can hand work from one agent to another

without requiring the user to reverse engineer the flow from multiple emitted
Markdown files or inspect inheritance structure that is not part of the
operational data-flow question, and without defaulting to a width-sprawled graph
that is hard to follow in normal review.

## 0.2 In scope

- One v1 visualization surface dedicated to operational data flow for Doctrine
  multi-agent workflows.
- Concrete agent nodes only; abstract agents and inheritance trees stay out of
  the main view unless later planning proves a narrow readability win.
- Input declaration nodes and output declaration nodes deduplicated across the
  rendered graph so shared contracts become visible anchors.
- Three primary edge families:
  - input -> agent for consumed inputs
  - agent -> output for emitted outputs
  - agent -> agent for explicit route handoffs
- Labels or annotations that preserve the human-meaningful route message and
  enough I/O contract metadata to understand the graph without opening the
  prompt file immediately.
- A Doctrine-supported invocation path that works in ordinary repos by reusing
  the existing `pyproject.toml` target model instead of introducing
  repo-specific analyzer setup.
- One target-scoped visualization artifact per configured entrypoint, rather
  than one separate graph file per concrete agent.
- Readability rules that explicitly bias toward easy followability over
  exhausting every semantic detail the compiler knows.
- Proof examples, docs, and verification needed to keep the feature shipped and
  portable.

## 0.3 Out of scope

- Full inheritance visualization.
- Generic AST viewers or compiler debug dumps marketed as user-facing workflow
  diagrams.
- Interactive graph editing, drag-and-drop workflow authoring, or a browser app
  as a v1 requirement.
- Runtime trace playback, token-level execution traces, or state-machine
  debugging beyond the declared operational flow.
- Surfacing every law statement, every trust-surface field, or every branch
  invariant when that would make the main graph hard to read.
- Repo-specific diagram config that has to be hand-maintained separately from
  Doctrine entrypoint configuration.
- Parallel visualization stacks where Doctrine owns one path and repos maintain
  a second unofficial path.

## 0.4 Definition of done (acceptance evidence)

- A Doctrine-supported command can generate deterministic D2 workflow-flow
  source for at least one configured multi-agent entrypoint.
- The generated artifact clearly shows agents, declared inputs, declared
  outputs, and routing handoffs for a representative branching example.
- The generated artifact stays readable enough to follow in ordinary review
  contexts, with a top-to-bottom or otherwise non-sprawling default reading
  mode.
- Existing Doctrine emit and example proof flows still pass after the feature is
  added.
- The user-facing docs for the feature explain how any Doctrine repo can enable
  and run it.

Behavior-preservation evidence:

- existing `make verify-examples` remains green
- existing emit-target behavior remains green for current Markdown emission
- new visualization proof uses the smallest stable artifact check that survives
  internal refactors

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks and no shadow parser.
- No dual truth between the compiler-owned workflow semantics and the
  visualization extraction path.
- Readability beats exhaustiveness in the default view.
- The default diagram answers “who touches what data and where can work route
  next?” before it answers any secondary architecture question.
- Shared input and output contracts should appear once per graph, not once per
  agent copy.
- The v1 surface must work across Doctrine repos, not only in this repository.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Readability of the operational flow.
2. Framework-supported portability across Doctrine repos.
3. Extraction truth anchored in the shipped compiler and emit path.
4. Deterministic, diffable artifacts that fit the existing repo workflow.
5. Future extensibility to richer visualization views without polluting the v1
   default.

## 1.2 Constraints

- Current shipped emission is Markdown-only through `doctrine.emit_docs`.
- `pyproject.toml` already defines repo-portable emit targets for Doctrine
  entrypoints.
- `CompilationContext` already resolves concrete agent input/output ownership
  and route-related semantics, but there is no current graph artifact surface.
- The requested behavior is explicitly not an inheritance analyzer.
- The requested output must stay easy to follow in common review contexts.

## 1.3 Architectural principles (rules we will enforce)

- Reuse the existing compiler and emit owner paths before creating new
  infrastructure.
- Prefer one operational data-flow view in v1 over multiple half-supported
  visualization modes.
- Keep the extraction rooted in concrete agent contracts and route semantics,
  not raw prompt syntax reconstruction.
- Reuse the existing target config directly for v1 rather than adding a second
  visualization-specific config lane.
- Ship static and deterministic output first through a D2-based target-level
  artifact; only add richer interactivity later if the same graph IR proves
  insufficient.
- Fail loudly when the requested visualization target cannot be resolved.

## 1.4 Known tradeoffs (explicit)

- A simpler readable graph will intentionally omit some deeper law and
  inheritance detail from the main view.
- The chosen v1 shape is static-first D2 output, which keeps the feature close
  to the existing emit pipeline but puts more pressure on graph extraction and
  layout defaults.
- The strongest external candidates split into two families: static
  diagram-as-code and interactive node-canvas stacks. Picking between those
  families is a product-surface decision first and a library-brand decision
  second.
- Interactive inspection stays a possible later renderer on the same graph IR,
  but it is not the v1 owner path.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- `doctrine.emit_docs` resolves configured entrypoints from `pyproject.toml`,
  parses the prompt file, finds root concrete agents, compiles each agent, and
  writes rendered Markdown output.
- `render_markdown()` only knows how to emit a `CompiledAgent` as nested
  Markdown sections.
- The compiler already has concrete agent contract resolution for inputs and
  outputs and distinct handling for ordinary route lines and workflow-law route
  statements.
- The repo has a research note on visualization options, but no shipped feature
  yet.

## 2.2 What’s broken / missing (concrete)

- There is no single artifact that shows the operational flow across multiple
  agents.
- Shared contracts like handoff outputs remain buried inside separate emitted
  agent docs instead of showing up as central graph anchors.
- Route chains are difficult to inspect quickly, especially when the workflow is
  split across multiple concrete agents or law branches.
- Current output makes it too easy to answer “what does this one agent render?”
  and too hard to answer “how does data move through the system?”

## 2.3 Constraints implied by the problem

- The feature should reuse compiler-owned truth instead of inventing a new
  analyzer lane.
- The default artifact must privilege layout readability, not raw semantic
  completeness.
- The feature needs a repo-portable invocation path because the user wants this
  to feel like a Doctrine framework feature rather than a local experiment.

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- `docs/research_visualizations.md` is useful as a comparative note, not as a
  shipped decision. Adopt from it only the requirements-level lesson that
  layout quality and domain-specific readability hints matter for workflow
  graphs. Reject treating any listed tool or renderer as already chosen.
- The same note keeps two high-level artifact families open:
  static documentation-oriented output and richer interactive inspection. That
  is useful pressure for later design, but it does not settle the v1 output
  surface during research.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors:
  - `doctrine/parser.py` plus `doctrine/grammars/doctrine.lark` define the
    shipped prompt syntax, including authored `route "..." -> Agent` and
    workflow-law route statements.
  - `doctrine/model.py` defines the structured workflow objects the compiler
    works from, including `RouteLine`, `LawRouteStmt`, `OutputDecl`, and
    `TrustSurfaceItem`.
  - `doctrine/compiler.py` is the semantic owner for concrete agent truth:
    `CompilationContext`, `compile_prompt()`, `AgentContract`,
    `_resolve_agent_contract()`, the input/output collection helpers, route
    validation, law-branch collection, currentness, invalidation, and carrier
    validation all live here.
  - `doctrine/renderer.py` is the current Markdown-only presentation boundary.
    Once data crosses into rendered Markdown, route and I/O meaning has already
    been flattened into presentation text.
  - `doctrine/emit_docs.py` is the current framework-owned artifact path. It
    loads named emit targets from `pyproject.toml`, resolves concrete root
    agents from `AGENTS.prompt` or `SOUL.prompt`, compiles each concrete agent,
    renders Markdown, and writes one emitted file per concrete agent.
  - `doctrine/verify_corpus.py` is the current proof harness for both
    render-contract and build-contract behavior.

- Canonical path / owner to reuse:
  - The only current repo-portable artifact-generation surface is
    `pyproject.toml` `[tool.doctrine.emit.targets]` plus
    `uv run --locked python -m doctrine.emit_docs --target ...`.
  - The future feature must reuse compiler-owned workflow semantics before the
    Markdown rendering boundary. A syntax-level sidecar extractor would drift
    from imports, inheritance, override patches, resolved routes, trust
    carriers, and workflow-law branch semantics that the compiler already owns.

- Existing patterns to reuse:
  - Named target discovery from the nearest parent `pyproject.toml`.
  - Concrete-root agent discovery from the configured entrypoint.
  - One checked-in emitted tree per target under `build_ref/` when the emit
    pipeline matters.
  - Manifest-backed proof with `status = "active"` as the shipped corpus rule.
  - Fail-loud diagnostics for missing config, bad targets, and missing
    entrypoints.

- Prompt surfaces / entrypoint contract already in play:
  - The shipped entrypoint surface is `AGENTS.prompt` or `SOUL.prompt` under a
    resolvable `prompts/` root.
  - The public downstream artifact model is still compiled `AGENTS.md` or
    `SOUL.md`, not a graph-specific runtime replacement.

- Duplicate or drifting paths relevant to this change:
  - Routing truth currently exists in two compiler-owned semantic surfaces:
    authored workflow `RouteLine` and workflow-law `LawRouteStmt`. Any future
    flow view that reads only one of them will misstate the workflow.
  - Inputs and outputs can arrive through inline bodies, named blocks,
    inherited blocks, override patches, and imported declarations. Only the
    compiler currently merges those into one concrete-agent truth surface.
  - `editors/vscode/resolver.js` is an editor-side mirror for clickable
    declaration/path sites. It explicitly says the compiler owns law semantics.
    That makes it a drift surface to watch, not a semantic owner to reuse for
    visualization.
  - Live docs currently drift on the shipped corpus upper bound:
    `README.md`, `docs/README.md`, and `AGENTS.md` do not currently agree.
    That drift is pre-existing and should not be mistaken for the canonical
    owner path.

- Behavior-preservation signals already available:
  - `make verify-examples` runs the active manifest-backed corpus.
  - Render-contract cases prove the shipped parse -> compile -> render path.
  - Build-contract cases prove target-scoped emitted tree output against
    checked-in `build_ref/` trees.
  - Emit diagnostics already have a smoke-check surface through
    `make verify-diagnostics`.
  - Current build-contract coverage is narrower than the full shipped
    workflow-law corpus: the emit path is actively proved for examples `07`,
    `14`, and `36`, while the broader language corpus now runs through `53`.

## 3.3 Open questions from research

- The main architecture questions are now resolved for v1:
  - v1 is static-first and D2-first
  - v1 reuses `[tool.doctrine.emit.targets]` directly
  - the canonical semantic boundary is compiler-owned extraction on
    `CompilationContext`
  - the smallest honest preservation signal is target-backed `build_contract`
    proof, with `.flow.d2` as the hard-gated artifact
- The research-stage open questions have been closed by later passes:
  - `.flow.d2` stays the owned v1 artifact. Same-command `.flow.svg` rendering
    ships only if the D2 dependency can be pinned and invoked cleanly in the
    public command; otherwise implementation must reopen the merge decision
    instead of silently downgrading the feature.
  - `example_36_invalidation_and_rebuild` is the first shipped proof target
    because it already has target-backed build proof and exercises multi-agent
    flow, routes, shared outputs, trust carriers, and invalidation.
- No blocking research questions remain before `implement-loop`.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:external_research:start -->
# External Research (best-in-class references; plan-adjacent)

> Goal: anchor the plan in idiomatic, broadly accepted practices where
> applicable. This section intentionally avoids project-specific internals.
>
> Deep-dive later chose static-first D2 output for v1 while preserving a
> renderer-neutral graph IR. The recommendations below are the research-stage
> inputs to that decision.

## Topics researched (and why)

- Interactive node-canvas stacks — if Doctrine eventually needs an inspectable
  graph UI rather than only a generated document artifact, this is the relevant
  family.
- Static diagram-as-code tools — the ask explicitly includes readable generated
  artifacts, and D2 is the concrete static candidate raised by the user.
- Workflow-platform frameworks — FlowGram is an explicit candidate and tests
  whether Doctrine should prefer a higher-level workflow framework over a lower-
  level graph toolkit.
- State/process-specialized systems — XState/Stately and bpmn-js are strong
  adjacent ecosystems, but they may be a semantic mismatch for Doctrine's
  primary data-flow question.

## Findings + how we apply them

### Interactive Node-Canvas Stacks

- Best practices (synthesized):
  - React Flow's own docs are explicit that layout is external. A serious
    interactive graph needs both a renderer and a deliberate layout stage.
  - ELK/elkjs is a layout engine, not a diagramming framework. Its official
    docs emphasize ports, hierarchical nodes, and computed positions rather
    than rendering.
  - React Flow supports nested/grouped flows and server-side rendering, but its
    SSR/static-generation path is still an advanced application surface rather
    than a tiny CLI-style document emitter.
  - AntV splits graph visualization and analysis (`G6`) from graph editing
    (`X6`). Both are relevant, but they are not the same product surface.
- Recommended default for this plan:
  - Keep interactive stacks in scope only as one family of candidates, not as
    the assumed first ship.
  - If the plan later chooses an interactive path, require a separate layout
    stage and treat grouping, ports, and top-to-bottom readability as baseline
    requirements rather than optional polish.
  - Keep the core plan renderer-neutral until `deep-dive` compares Doctrine's
    actual artifact and invocation needs against this family.
- Pitfalls / footguns:
  - React Flow does not ship its own layout engine; layout quality remains the
    consumer's responsibility.
  - Some richer React Flow examples, including auto-layout patterns, are Pro
    examples. That is not the same as missing capability in the OSS core, but
    it does affect how much official implementation guidance is freely
    available.
  - G6 and X6 solve adjacent but different problems. Choosing between them
    without first deciding "viewer" versus "editor" is premature.
- Sources:
  - React Flow home — https://reactflow.dev/ — official positioning, MIT
    license, node-based UI scope
  - React Flow layout overview — https://reactflow.dev/learn/layouting/layouting
    — official guidance that layout is external
  - React Flow sub flows —
    https://reactflow.dev/learn/layouting/sub-flows — official grouping and
    nested-flow support
  - React Flow SSR/SSG —
    https://reactflow.dev/learn/advanced-use/ssr-ssg-configuration — official
    server-side/static generation guidance
  - ELK homepage — https://eclipse.dev/elk/ — official explanation of ports,
    hierarchical nodes, and layout-only boundary
  - elkjs GitHub — https://github.com/kieler/elkjs — official JS packaging,
    layout-only API, worker support, and options surface
  - G6 combo-combined layout —
    https://g6.antv.antgroup.com/en/manual/layout/combo-combined-layout —
    official grouped/composite layout surface
  - X6 overview — https://x6.antv.antgroup.com/tutorial/about — official
    editing-engine positioning
  - X6 examples — https://x6.antv.antgroup.com/en/examples — official examples
    including Agent Flow, DAG, BPMN, and ELK practices

### Static Diagram-As-Code

- Best practices (synthesized):
  - Prefer deterministic, diffable source with a CLI or library surface when
    the artifact is documentation-oriented and should fit ordinary review and
    build flows.
  - Keep layout-engine behavior explicit. D2's own docs distinguish between
    different layout engines and document tradeoffs directly.
  - Multi-board composition and export behavior matter if the visualization may
    later need layered or stepped views rather than a single flat diagram.
- Recommended default for this plan:
  - Keep D2 as a serious candidate only for a static/doc-first artifact
    family, not as the settled answer for the entire feature.
  - If the plan later chooses a static path, judge D2 on diffability, CLI fit,
    export behavior, and layout-engine limits rather than aesthetics alone.
- Pitfalls / footguns:
  - D2's richer non-hierarchical layout story can depend on TALA, which its
    own docs separate from the fully open-source core.
  - Static exports do not automatically satisfy the "inspect the flow" use case
    if the real need turns out to be click-to-inspect interaction rather than a
    readable generated artifact.
- Sources:
  - D2 home — https://d2lang.com/ — official feature surface
  - D2 intro — https://d2lang.com/tour/intro/ — official CLI and language
    positioning
  - D2 exports — https://d2lang.com/tour/exports/ — official export formats
    and CLI behavior
  - D2 composition — https://d2lang.com/tour/composition/ — official multi-
    board model
  - D2 composition formats —
    https://d2lang.com/tour/composition-formats/ — official composed-artifact
    export behavior
  - D2 TALA — https://d2lang.com/tour/tala/ — official separation between OSS
    D2 and proprietary TALA

### Workflow-Platform Frameworks

- Best practices (synthesized):
  - Higher-level workflow frameworks reduce assembly work only when you
    actually want platform-building concerns such as forms, materials, variable
    engines, plugins, and editor interactions.
  - Treat self-authored comparison pages as positioning material, not as a
    neutral benchmark.
- Recommended default for this plan:
  - Treat FlowGram as evidence that a higher-level AI workflow framework exists
    and is viable, but do not promote it to the default fit unless `deep-dive`
    proves Doctrine needs builder-grade platform concerns rather than a
    framework-owned visualization artifact.
  - Use FlowGram's docs to understand the extra product surface that comes with
    this family, not as proof that Doctrine should take it on.
- Pitfalls / footguns:
  - FlowGram is explicitly a workflow development framework and toolkit, not a
    lightweight renderer.
  - Its React Flow comparison page is useful for understanding its intended
    product boundary, but not as neutral evidence that React Flow loses the
    comparison outright.
- Sources:
  - FlowGram introduction —
    https://flowgram.ai/en/guide/getting-started/introduction — official docs
    on canvas, forms, variables, materials, and platform scope
  - FlowGram vs ReactFlow —
    https://flowgram.ai/en/guide/concepts/reactflow — official self-positioning
    and comparison framing

### State And Process Specialized Systems

- Best practices (synthesized):
  - Use statechart/process tooling when the primary semantics are already
    event/state transitions or BPMN processes.
  - Expect semantic translation cost when the source model is not already in
    that family.
- Recommended default for this plan:
  - Reject XState/Stately and bpmn-js as the primary default targets for
    Doctrine's v1 operational data-flow artifact.
  - Keep them only as possible future specialized projections if Doctrine later
    needs a state-machine or BPMN-specific view beyond the default data-flow
    graph.
- Pitfalls / footguns:
  - XState's current visual tooling is explicitly statechart/actor-oriented,
    and the legacy Visualizer is deprecated in favor of Studio.
  - bpmn-js brings BPMN viewer/modeler and BPMN 2.0 meta-model assumptions,
    which is a much heavier semantic translation than using a generic graph
    renderer.
- Sources:
  - XState docs — https://stately.ai/docs/xstate — official statechart/actor
    positioning
  - Stately Studio — https://stately.ai/docs/studio — official visual editor
    positioning
  - Visualizer (deprecated) — https://stately.ai/docs/visualizer — official
    deprecation status
  - bpmn-js walkthrough — https://bpmn.io/toolkit/bpmn-js/walkthrough/ —
    official BPMN viewer/modeler and BPMN meta-model/toolkit boundary

## Adopt / Reject summary

- Adopt:
  - Treat the external landscape as two serious artifact families for this
    plan: static diagram-as-code and interactive node-canvas stacks.
  - Treat layout as a first-class requirement, not a secondary polish pass.
  - Keep the core plan renderer-neutral until `deep-dive` compares Doctrine's
    actual target surface against those families.
  - Prefer tools that consume structured graph data instead of forcing Doctrine
    to emit a foreign process/state model unless that semantic shift is
    intentional.
- Reject:
  - Reject treating "Claude recommends D2" or any single comparative article as
    architectural closure.
  - Reject self-authored comparison pages as neutral evaluation.
  - Reject XState/Stately and bpmn-js as the default fit for Doctrine's primary
    v1 data-flow question.
  - Reject assuming an interactive canvas is automatically the right first ship
    just because the ecosystem is rich.

## Open questions (ONLY if truly not answerable)

- Does Doctrine's first shipped artifact need inspection-grade interactivity,
  or is a doc-first/static artifact sufficient for the user's stated workflow?
  Evidence needed:
  `deep-dive` on invocation surface, consumption context, and acceptance
  evidence.
- If the first artifact is static-first, does D2's open-source engine set give
  clear enough layout/readability guarantees for Doctrine's graph shapes
  without relying on TALA-specific behavior?
  Evidence needed:
  `deep-dive` against real Doctrine graph shapes and readability constraints.
- If the first artifact is interactive-first, is the repo willing to take on a
  frontend/runtime dependency surface that goes well beyond today's Python +
  Markdown emit path?
  Evidence needed:
  `deep-dive` on canonical owner path, dependency policy, and proof strategy.
<!-- arch_skill:block:external_research:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

The current owner paths are concrete and already split cleanly by role:

- `doctrine/grammars/doctrine.lark`
  - Owns the shipped syntax for `trust_surface`, authored `route` lines,
    `current artifact ... via ...`, and workflow-law route statements.
- `doctrine/parser.py`
  - Lowers those constructs into concrete model types:
    `route_stmt()` -> `model.RouteLine`,
    `law_route_stmt()` -> `model.LawRouteStmt`,
    `current_artifact_stmt()` -> `model.CurrentArtifactStmt`,
    `output_decl()` -> `model.OutputDecl(..., trust_surface=...)`.
- `doctrine/model.py`
  - Owns the durable syntax dataclasses the compiler reads:
    `Agent`, `InputsField`, `OutputsField`, `IoBody`, `InputDecl`,
    `OutputDecl`, `TrustSurfaceItem`, `RouteLine`, `LawRouteStmt`,
    `CurrentArtifactStmt`, and `InvalidateStmt`.
- `pyproject.toml`
  - `[tool.doctrine.emit.targets]` is the only shipped repo-portable target
    config surface.
  - Each target is exactly three strings today: `name`, `entrypoint`, and
    `output_dir`.
- `doctrine/emit_docs.py`
  - Owns target loading, entrypoint validation, root concrete-agent discovery,
    output-path derivation, and the public CLI entrypoint.
  - `EmitTarget` is the emitted-artifact scope object today.
- `doctrine/compiler.py`
  - Owns semantic truth for concrete agents, imports, resolved workflows,
    concrete-agent contracts, authored routes, workflow-law route statements,
    currentness, invalidation, and trust-carrier validation.
- `doctrine/renderer.py`
  - Is a Markdown-only projection from one `CompiledAgent` to nested headings
    and prose.
- `doctrine/verify_corpus.py`
  - Treats render output and target-scoped emitted trees as checked proof
    surfaces.

## 4.2 Control paths (runtime)

Current emitted-doc flow is fully target-scoped:

1. `doctrine.emit_docs.main()` resolves `pyproject.toml`, loads named targets,
   and loops `--target` values.
2. `load_emit_targets()` resolves each target entry relative to the config dir
   and enforces `AGENTS.prompt` or `SOUL.prompt` as the only supported
   entrypoint filenames.
3. `emit_target()` parses the configured entrypoint prompt file.
4. `_root_concrete_agents()` discovers render roots by scanning only the
   entrypoint file's top-level declarations for non-abstract `model.Agent`
   declarations.
5. For each discovered root agent, `compile_prompt(prompt_file, agent_name)`
   constructs a fresh `CompilationContext`, resolves imports from the nearest
   `prompts/` root, and compiles one concrete agent at a time.
6. Inside `CompilationContext`, the current semantic path is:
   - `_index_unit()` builds `IndexedUnit` registries and imported units.
   - `_compile_agent_decl()` resolves authored slots, resolves the concrete
     `AgentContract`, then compiles typed fields and the resolved workflow.
   - `_resolve_agent_contract()` plus the `_collect_*_decls_from_io_value()`
     helpers compute the final input/output declaration set across inline,
     named, imported, inherited, and patched I/O forms.
   - `_resolve_workflow_decl()` / `_resolve_workflow_body()` resolve inherited
     workflow structure.
   - `_resolve_section_body_items()` validates authored route targets and turns
     `model.RouteLine` into `ResolvedRouteLine`.
   - `_compile_workflow_law()` flattens and validates workflow-law statements,
     then renders them into prose.
7. `render_markdown()` converts the resulting `CompiledAgent` into Markdown.
8. `_entrypoint_relative_dir()`, `_entrypoint_output_name()`, and
   `_emit_path_for_agent()` derive the output path, then `emit_target()` writes
   the file.

There is no sibling workflow-level emit path yet, and nothing in the current
pipeline ever materializes a multi-agent graph artifact.

## 4.3 Object model + key abstractions

The relevant abstractions are already split into three layers:

- Target/config layer:
  - `EmitTarget`
- Agent-compile layer:
  - `CompiledAgent`
  - `CompiledSection`
- Compiler-semantic layer that still preserves graph meaning:
  - `IndexedUnit`
  - `AgentContract`
  - `ResolvedWorkflowBody`
  - `ResolvedSectionItem`
  - `ResolvedRouteLine`
  - `LawBranch`
  - `ResolvedLawPath`
  - `model.LawBody`
  - `model.LawRouteStmt`
  - `model.OutputDecl.trust_surface`

The key architecture boundary is that `render_markdown()` only sees one
`CompiledAgent`. That is already too late for a truthful workflow graph because
shared I/O anchors, target-level root scope, and cross-agent route structure
have been flattened into per-agent prose.

The narrower extraction findings from code are:

- `AgentContract` is the narrowest trustworthy I/O truth today. It keeps exact
  resolved input/output declaration membership keyed by
  `(module_parts, decl_name)`.
- `ResolvedWorkflowBody` plus `ResolvedSectionItem` / `ResolvedRouteLine` is the
  narrowest authored-route truth today.
- `LawBranch` from `_collect_law_leaf_branches()` is the narrowest reusable
  workflow-law truth today for current subjects, invalidations, and law-owned
  routes.
- `ResolvedIoBody` is not a good graph SSOT even though it sounds close.
  `ResolvedIoSection.section` and `ResolvedIoRef.section` already store
  `CompiledSection`, so declaration identity has been turned into presentation
  sections by the time that type exists.
- `_compile_workflow_law()` is also too late as an extraction boundary because
  law statements have already been flattened into English prose lines.

The other important current behavior is scope: root discovery is entrypoint-
local, not whole-repo global. Imported modules influence compiled semantics, but
they do not become extra emit roots unless the configured entrypoint itself
declares those concrete agents.

## 4.4 Observability + failure behavior today

Current observability is already strongest around target-scoped emit behavior:

- `doctrine/diagnostics.py` documents dedicated emit errors for unknown targets,
  missing targets, duplicate target names, unsupported entrypoints, path
  collisions, missing `prompts/` roots, and related config failures.
- `doctrine/diagnostic_smoke.py` directly smoke-tests:
  - invalid emit config TOML
  - missing entrypoint behavior
  - output-name derivation from entrypoint stem
- `doctrine/verify_corpus.py` has a build-contract lane that:
  - loads a configured `build_target`
  - calls `emit_target()`
  - diffs the resulting file tree against checked-in `build_ref/`

There is no graph artifact proof lane yet, but the existing build-contract
shape is already the right ownership pattern: target name in the manifest,
target-scoped emitted tree on disk, and deterministic checked-in output.

The compiler also already enforces the currentness/trust contract that a future
graph may need to annotate:

- `_validate_current_artifact_stmt()` requires the current artifact root to
  resolve to a declared input or output and, when rooted at an output, requires
  that output to be emitted by the concrete turn.
- `_validate_carrier_path()` requires the `via` carrier to stay rooted in an
  emitted output, point at a real output field, and match a declared
  `trust_surface` entry.
- `_resolve_output_field_node()` is the field-resolution surface for those
  carrier checks.

## 4.5 UI surfaces (ASCII mockups, if UI work)

The only shipped presentation surface today is emitted Markdown files. Their
path shape is mechanical:

- `<output_dir>/<entrypoint-relative-dir>/<agent_slug>/<AGENTS|SOUL>.md`

Concrete examples already checked into the repo:

- `examples/07_handoffs/build/project_lead/AGENTS.md`
- `examples/14_handoff_truth/build/section_author/AGENTS.md`
- `examples/36_invalidation_and_rebuild/build/routing_owner/AGENTS.md`

The requested new surface is still a generated artifact, not a browser editor.
That makes a sibling target-level artifact fit the current doctrine much better
than an interactive app as the first ship.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

The v1 owner path should stay inside the existing Doctrine compile/emit stack:

- Keep `pyproject.toml` `[tool.doctrine.emit.targets]` as the only target
  config surface for v1.
- Add a sibling CLI/emitter module next to `doctrine/emit_docs.py`, not inside
  `doctrine/renderer.py`.
  - Recommended owner path: `doctrine/emit_flow.py`
- Add one compiler-owned extraction boundary that returns a renderer-neutral
  workflow graph IR before Markdown rendering.
  - It should be owned by `CompilationContext`, because only that layer already
    has imports, inherited authored slots, resolved contracts, route validation,
    and workflow-law validation in one place.
- Keep D2 rendering as a separate presentation layer fed by that graph IR.
- Add target-scoped checked artifacts under the existing configured
  `output_dir`, not in a new repo-local folder outside the target model.

## 5.2 Control paths (future)

Recommended v1 control path:

1. `python -m doctrine.emit_flow --target <name>` resolves the same named
   target table used by `emit_docs`.
2. The emitter parses the configured entrypoint and reuses the same
   entrypoint-local root concrete-agent discovery rule.
3. The emitter instantiates one shared `CompilationContext(prompt_file)` for the
   target instead of repeatedly calling `compile_prompt()`.
4. A compiler-owned extraction pass resolves the concrete agents in that scope
   and normalizes one target-level graph IR:
   - agent nodes
   - deduplicated input nodes
   - deduplicated output nodes
   - consumes edges
   - produces edges
   - route edges from both authored `RouteLine` and workflow-law
     `LawRouteStmt`
   - optional currentness / trust annotations derived from validated law truth
5. A D2 renderer turns that graph IR into deterministic D2 source.
6. Doctrine writes one target-level graph artifact beside the existing emitted
   docs using the same `output_dir` and `prompts/`-relative placement rules.
7. The owned v1 artifact is target-level D2 source. A rendered SVG, if shipped
   in the same first pass, is a derived sibling artifact from that D2 source,
   not a second semantic owner.

## 5.3 Object model + abstractions (future)

The future abstraction stack should be explicit:

- Config scope stays `EmitTarget`.
- Semantic extraction adds one renderer-neutral graph IR scoped to one target.
- D2 is only the first renderer for that IR.

The canonical extraction boundary should be narrower and more concrete than
"extract from the compiler somewhere":

- I/O membership should come from `AgentContract`, not from `ResolvedIoBody`
  and not from `CompiledSection`.
- Authored route edges should come from resolved workflow slots via
  `_resolve_agent_slots()` and `ResolvedRouteLine`.
- Workflow-law route edges and currentness/trust annotations should come from
  `_flatten_law_items()`, `_validate_workflow_law()`,
  `_collect_law_leaf_branches()`, `_validate_current_artifact_stmt()`, and
  `_validate_carrier_path()`.
- Root/identity keys should stay compiler-native:
  - agents keyed by `(module_parts, agent_name)`
  - inputs keyed by `(module_parts, input_decl_name)`
  - outputs keyed by `(module_parts, output_decl_name)`

Recommended graph IR facts for v1:

- node kinds:
  - `agent`
  - `input`
  - `output`
- edge kinds:
  - `consumes`
  - `produces`
  - `routes`
- required metadata:
  - target name
  - entrypoint path
  - agent display name and slug
  - input/output declaration names and readable labels
  - input/output source or target kind plus declared file/env/path details when
    present
  - route label text
  - trust-surface fields where declared
  - current artifact carrier output + field when present

Recommended artifact shape:

- owned contract artifact:
  - `<output_dir>/<entrypoint-relative-dir>/<ENTRYPOINT_STEM>.flow.d2`
- derived rendered sibling if the D2 rendering dependency is accepted in the
  same pass:
  - `<output_dir>/<entrypoint-relative-dir>/<ENTRYPOINT_STEM>.flow.svg`

That keeps the graph target-scoped instead of generating one diagram per agent,
and it preserves the current expectation that `AGENTS.prompt` and `SOUL.prompt`
produce artifacts named from the entrypoint stem.

## 5.4 Invariants and boundaries

- Compiler-owned semantics remain the only truth source.
- The default view stays focused on operational data flow.
- The visualization layer may simplify or collapse details for readability, but
  it may not invent relationships not present in the compiler-owned model.
- Existing Markdown emission remains intact as a sibling emitter, not a
  displaced one.
- V1 reuses existing emit targets directly; it does not add a second
  visualization-specific target registry.
- The graph scope matches current emit scope: top-level concrete agents in the
  configured entrypoint, with imported declarations participating only through
  compiler resolution.
- D2 source is the owned graph artifact for review and diff. Rendered SVG, if
  shipped, is derived from it.
- `CompilationContext` is the semantic extraction boundary. The parser/model
  define syntax, the emitter defines target scope and output paths, and the
  renderer defines presentation.
- `ResolvedIoBody`, `CompiledAgent`, `CompiledSection`, emitted Markdown, and
  editor-side mirrors are downstream and must not become graph-semantic owners.

## 5.5 UI surfaces (ASCII mockups, if UI work)

The output should bias toward a followable top-to-bottom flow:

- agents as dominant process nodes
- input/output declarations as smaller artifact nodes
- route edges visually distinct from consumes/produces edges
- one graph per target, not a stitched wall of per-agent subgraphs

The first shipped surface is a generated static artifact, not an editor or live
inspector. If Doctrine later adds interactivity, it should reuse the same graph
IR and target scope rather than replacing the v1 owner path.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Emit target config | `pyproject.toml` | `[tool.doctrine.emit.targets]` | Configures target name, entrypoint, and output directory for `emit_docs` | Reuse this table directly for workflow visualization; do not add a second target registry in v1 | Current portability and manifest proof already key off target names | Same target names drive both Markdown emit and flow emit | build-contract style proof and docs examples |
| Emit target loading | `doctrine/emit_docs.py` | `EmitTarget`, `resolve_pyproject_path()`, `load_emit_targets()` | Resolves config from nearest parent `pyproject.toml` and validates entrypoints/output dirs | Share or extract this target-loading logic so `emit_flow` uses the exact same scope rules and diagnostics posture | A second config loader would drift immediately | Common target loader and path rules across sibling emitters | emit smoke checks, target resolution checks |
| Root concrete-agent discovery | `doctrine/emit_docs.py` | `_root_concrete_agents()` | Discovers only top-level non-abstract agents in the configured entrypoint file | Reuse this exact target-scope rule for v1 flow graphs | The current emit path is entrypoint-scoped, not whole-repo-scoped | Target graph roots are entrypoint-local concrete agents | build-contract proof on representative multi-agent targets |
| Compiler semantic extraction | `doctrine/compiler.py` | `CompilationContext`, `_resolve_agent_contract()`, `_resolve_agent_slots()`, `_resolve_workflow_body()`, `_resolve_section_body_items()`, `_flatten_law_items()`, `_collect_law_leaf_branches()`, `_validate_current_artifact_stmt()`, `_validate_carrier_path()` | Resolves concrete-agent semantics but only returns one compiled agent at a time, and some nearby types are already presentation-oriented | Add one compiler-owned graph extraction surface that works across the target's root agents before Markdown rendering and before `ResolvedIoBody` / `CompiledSection` lose declaration identity | Graph truth must include inline/named/inherited/patched I/O plus authored routes, law-owned routes, and validated currentness/trust carriers | Renderer-neutral target-level workflow graph IR extracted from compiler-native identities | graph structure checks and example-backed emitted artifacts |
| Markdown renderer boundary | `doctrine/renderer.py` | `render_markdown()` | Projects one `CompiledAgent` into headings/prose | Leave Markdown rendering as-is; do not make it the graph owner | Graph extraction after prose rendering would be lossy and brittle | Markdown stays a sibling renderer only | existing render-contract checks stay alive |
| Visualization emitter | `doctrine/emit_flow.py` | new sibling module | Does not exist | Add the new public CLI/emitter beside `emit_docs.py` and keep it target-scoped | CLI ownership, output-path ownership, and fail-loud target UX already live in the emit layer | `python -m doctrine.emit_flow --target <name>` | new emit smoke checks and target-backed artifact proof |
| D2 rendering | `doctrine/renderer.py` or new module | new D2 render function/module | Does not exist | Add D2 rendering as a presentation layer fed by graph IR, not as semantic owner | D2 is the chosen static-first renderer, but the graph model must stay Doctrine-owned | Deterministic `.flow.d2` source is required; `.flow.svg` is derived only if same-pass rendering dependency is accepted | artifact diff checks |
| Output path convention | `doctrine/emit_docs.py` | `_entrypoint_relative_dir()`, `_entrypoint_output_name()`, `_emit_path_for_agent()` | Emits per-agent Markdown under `output_dir` plus prompts-relative subpath and agent slug | Reuse prompts-relative placement, but emit one target-level flow artifact named from the entrypoint stem instead of agent slugging | Users already learn target output shape from the existing emitter | `<output_dir>/<entrypoint-relative-dir>/<ENTRYPOINT_STEM>.flow.{d2,svg}` | build-contract style tree diff |
| Verification harness | `doctrine/verify_corpus.py` | `_run_build_contract()`, `load_emit_targets()`, `emit_target()` | Verifies target-scoped emitted trees against `build_ref/` | Extend target-backed proof so visualization output is checked in the same manifest-driven style | The repo already has an honest proof lane for emitted artifacts | target-backed tree proof with exact diff on `.flow.d2`; include `.flow.svg` only if deterministic | `make verify-examples` and targeted example manifests |
| Diagnostics smoke | `doctrine/diagnostic_smoke.py` | `emit_docs_main()` smoke checks | Proves emit config failures and output-name conventions | Add parallel smoke checks for the new emitter's target resolution and artifact naming | Fail-loud CLI behavior is part of the Doctrine contract | flow-emitter smoke cases | `make verify-diagnostics` |
| Docs and examples | `docs/README.md`, `examples/README.md`, `examples/**` | shipped usage and proof surfaces | No visualization feature documented or proved | Add one representative multi-agent build target with checked graph artifacts and user docs | Keep shipped truth aligned with the new command | documented target-scoped visualization workflow | docs sync plus example proof |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - keep target config ownership in `pyproject.toml` plus shared target-loading
    helpers
  - keep semantic ownership in compiler-side extraction on `CompilationContext`
  - keep CLI/output-path ownership in a sibling emitter module
- Deprecated APIs (if any):
  - none for v1 if Markdown emit stays intact
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - reject any repo-local visualization script or second target-config table if
    they appear during implementation
- Capability-replacing harnesses to delete or justify:
  - any post-Markdown parser that tries to rebuild graph truth from emitted
    prose
- Live docs/comments/instructions to update or delete:
  - `README.md`
  - `docs/README.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `examples/README.md`
  - any new example `cases.toml` or checked `build_ref/` guidance needed for
    the visualization command
- Behavior-preservation signals for refactors:
  - existing `make verify-examples`
  - existing target-backed build-contract checks
  - new target-backed graph artifact proof using the same manifest discipline

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Target loading | `doctrine/emit_docs.py` / `EmitTarget`, `load_emit_targets()` | one shared target-loading and validation path for all emitters | prevents Markdown emit and flow emit from resolving different targets | include |
| Output placement | `doctrine/emit_docs.py` / `_entrypoint_relative_dir()` | one prompts-relative output placement convention | prevents target artifacts from scattering into tool-specific folders | include |
| Semantic ownership | `doctrine/compiler.py` / contract and route resolution | one compiler-owned graph extraction boundary before renderers | prevents graph truth from drifting from emitted prose or editor helpers | include |
| Renderer separation | `doctrine/renderer.py` and new D2 renderer | renderer-specific projection fed by shared graph IR | prevents D2 from becoming the semantic model and keeps future interactivity possible | include |
| Generic "one emit command for all formats" refactor | CLI surface | unify Markdown and flow emit into a single mega-command now | adds surface area before the v1 owner path is proved | defer |
| Visualization-specific pyproject config | `pyproject.toml` | second target registry or per-target visualization settings in v1 | duplicates scope ownership and weakens portability | exclude |
| Browser editor / inspector | frontend surface | interactive viewer as the first shipped owner path | changes product surface too early and exceeds current proof/runtime model | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Lock the compiler-owned graph contract

* Goal:
  Land one target-level workflow graph extraction boundary that is fully owned
  by `CompilationContext` and preserves real Doctrine semantics before any
  renderer or public CLI is added.
* Work:
  - Add graph IR dataclasses keyed by compiler-native identities for agents,
    inputs, outputs, and edges.
  - Add one compiler-owned extraction API that runs once per target-scoped
    `CompilationContext` and collects:
    - I/O membership from `AgentContract`
    - authored routes from resolved workflow slots and `ResolvedRouteLine`
    - workflow-law routes plus currentness/trust annotations from validated law
      branches
  - Reuse the current entrypoint-local root concrete-agent rule rather than
    inventing whole-repo graph discovery.
  - Keep the extraction surface internal until it proves truthful on at least
    one representative multi-agent target.
* Verification (smallest signal):
  - Add targeted compiler-level tests for graph extraction on one representative
    prompt family, covering:
    - deduplicated shared input/output nodes
    - authored route edges
    - workflow-law route edges
    - trust/currentness annotations where they materially affect the graph
  - Keep existing render-contract coverage green so the extraction work does not
    regress Markdown compilation.
* Docs/comments (propagation; only if needed):
  - Add brief code comments at the extraction boundary documenting why
    `ResolvedIoBody`, `CompiledAgent`, and emitted Markdown are intentionally
    not the graph owner.
* Exit criteria:
  - A single target-scoped compiler call can return one renderer-neutral graph
    IR for the configured root concrete agents.
  - The IR is sourced only from compiler-owned semantics and does not depend on
    post-Markdown recovery.
* Rollback:
  - If the extraction cannot express shared I/O anchors and both route families
    truthfully, keep it private and stop before adding any public emitter.

## Phase 2 — Add the D2-first flow emitter

* Goal:
  Expose one Doctrine-owned public command that emits a readable, target-scoped
  flow artifact through the same target model as Markdown emit.
* Work:
  - Add `doctrine.emit_flow` as a sibling emitter that reuses the existing
    target-loading, entrypoint validation, root discovery, and prompts-relative
    placement rules.
  - Add a D2 renderer that projects the graph IR into tall, readable,
    deterministic `.flow.d2` source with clear visual distinction between
    process nodes and data nodes and between route edges and consume/produce
    edges.
  - Add same-command `.flow.svg` rendering through an explicitly pinned D2
    dependency path. If that dependency cannot be pinned and invoked cleanly,
    stop and reopen the plan rather than silently downgrading the public
    feature.
  - Add fail-loud diagnostics for missing targets, bad entrypoints, path
    collisions, and any new D2-render dependency failure that affects the
    public command.
* Verification (smallest signal):
  - Add targeted tests for D2 source generation shape and output-path
    derivation.
  - Add flow-emitter smoke coverage parallel to existing emit smoke checks.
  - Run `make verify-diagnostics` if diagnostics or smoke surfaces change.
* Docs/comments (propagation; only if needed):
  - Add short code comments where target-loading or output-placement helpers are
    shared so the sibling-emitter contract stays obvious.
* Exit criteria:
  - `uv run --locked python -m doctrine.emit_flow --target <name>` produces
    deterministic `.flow.d2` output under the standard target output tree.
  - The same command also emits `.flow.svg`, or the phase stops and reopens the
    dependency decision before merge.
* Rollback:
  - If D2 emission or rendering introduces a second config lane, repo-local
    scripts, or unstable command behavior, back it out and keep the command
    private until the canonical path is restored.

## Phase 3 — Prove it on one real target and sync live docs

* Goal:
  Put the feature on the shipped proof path with the smallest honest target and
  update the live docs to current reality.
* Work:
  - Reuse `example_36_invalidation_and_rebuild` as the first checked
    visualization proof target because it already has target-backed build proof
    and exercises multi-agent flow, routes, outputs, trust carriers, and
    invalidation.
  - Extend the target's emitted tree contract to include `.flow.d2` and include
    `.flow.svg` too if the rendering output is stable enough to diff honestly.
  - Update the owning example manifest, checked `build_ref/` tree, and target
    config as needed.
  - Update `README.md`, `docs/README.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, and
    `examples/README.md` so the public command, artifact shape, and proof model
    are all described consistently.
  - Update compiler/emit error docs only if new public diagnostics or config
    constraints are introduced.
* Verification (smallest signal):
  - Run the targeted manifest for the chosen proof example.
  - Run `make verify-examples`.
  - Run `make verify-diagnostics` if diagnostics or smoke checks changed in
    Phase 2.
  - Do one short manual readability check on the generated graph to confirm the
    default layout stays followable in ordinary review.
* Docs/comments (propagation; only if needed):
  - Remove or rewrite any wording that still describes compiled `AGENTS.md` as
    the only emit-layer artifact family.
* Exit criteria:
  - One shipped example target proves the new command end-to-end on the same
    manifest-backed build-contract lane as existing emitted artifacts.
  - The live docs describe the command, output shape, and expected verification
    path without drift.
* Rollback:
  - If the feature cannot be proved cleanly on the existing build-contract lane
    or leaves live docs contradictory, do not merge the public command.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Prefer the smallest graph-structure checks around the canonical extraction
  boundary instead of testing layout trivia.
- If new graph contracts are introduced, verify nodes and edge kinds in a
  structure-insensitive way when possible.

## 8.2 Integration tests (flows)

- Prefer example-backed target-backed checks proving that a configured
  multi-agent workflow can generate the visualization artifact through the
  existing `build_contract` lane.
- Hard-gate deterministic `.flow.d2` source first. Include `.flow.svg` in exact
  artifact proof only if the rendering dependency and output stability are
  pinned tightly enough to keep diffs honest.
- Keep Markdown emission checks alive so the new feature does not silently break
  the shipped emit path.

## 8.3 E2E / device tests (realistic)

- Default to a short manual readability check on representative graphs near
  finalization.
- Do not create screenshot bureaucracy or fragile visual-constant tests unless
  later planning proves they are the cheapest honest guardrail.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

This is likely a repo-local CLI/emit feature with no live production rollout.
The rollout surface is adoption in Doctrine repos plus example/docs proof in
this repo.

## 9.2 Telemetry changes

No telemetry plan is assumed at `new` time. If the feature remains a local
compiler/emit artifact, telemetry may stay out of scope.

## 9.3 Operational runbook

The expected v1 runbook is:

- configure or reuse a standard `[tool.doctrine.emit.targets]` entry
- run `uv run --locked python -m doctrine.emit_flow --target <name>`
- inspect the generated `.flow.d2` artifact
- inspect rendered `.flow.svg` too when the same-pass rendering dependency is
  deliberately accepted

# 10) Decision Log (append-only)

## 2026-04-10 - Scope v1 around operational data flow

### Context

The ask is for a quick, easy way to inspect how multi-agent workflows route and
how data moves through them, with explicit rejection of an inheritance-focused
analyzer.

### Options

- Build a generic prompt/AST visualization tool.
- Build an inheritance-oriented architecture graph.
- Build a workflow data-flow view centered on agents, inputs, outputs, and
  routes.

### Decision

Start the plan with the workflow data-flow view as the v1 behavior target.

### Consequences

- The default artifact can optimize for readability and shared contract
  visibility.
- Some deeper semantics will be deferred from the main view unless later
  research proves they belong without harming readability.

### Follow-ups

- Confirm the North Star before research.
- Completed in the 2026-04-10 deep-dive: v1 is static-first D2 output on a
  renderer-neutral graph IR.

## 2026-04-10 - Reuse Doctrine-owned target configuration and compiler truth

### Context

The repo already has Doctrine-owned emit target configuration and a compiler path
that resolves concrete agent contracts and route semantics.

### Options

- Build a repo-local visualization analyzer separate from Doctrine.
- Reuse and extend the existing Doctrine owner paths.

### Decision

Bias the plan toward reusing Doctrine-owned target configuration and
compiler-owned semantics instead of introducing a second analyzer lane.

### Consequences

- Portability across Doctrine repos remains achievable.
- The feature must fit the existing emit/config architecture cleanly rather than
  bypassing it.

### Follow-ups

- Completed in the 2026-04-10 deep-dive: visualization belongs as a sibling
  emitter command, not a repo-local tool and not a second target registry.

## 2026-04-10 - Narrow the external landscape without locking the renderer

### Context

External research compared D2, React Flow + ELK, FlowGram, AntV G6/X6,
XState/Stately, and bpmn-js against Doctrine's stated need: a readable
operational data-flow view that works as a Doctrine-supported feature rather
than a repo-local experiment.

### Options

- Treat one named library as already chosen.
- Keep the field open across all workflow and graph tools equally.
- Narrow the serious candidates to the external families that actually match
  Doctrine's problem shape, while keeping the final renderer decision open.

### Decision

Keep the final renderer/output choice open, but narrow the serious candidate
families to:

- static diagram-as-code tooling for a doc-first artifact
- interactive node-canvas tooling plus a separate layout engine for an
  inspectable UI path

Treat higher-level workflow-platform frameworks as a different product class,
and reject statechart/BPMN systems as the default fit for v1.

### Consequences

- `deep-dive` should compare artifact families and owner-path fit, not restart
  from every diagramming tool in the ecosystem.
- Layout is now an explicit first-class concern for any interactive path.
- D2 remains a serious static candidate, but not the already-chosen answer.

### Follow-ups

- Completed in the 2026-04-10 deep-dive: keep a renderer-neutral graph IR and
  choose static-first D2 for v1 while preserving interactive rendering as a
  later option on the same IR.

## 2026-04-10 - Make compiler-native flow extraction the semantic boundary

### Context

The local code inspection showed that the compiler already owns all of the hard
semantic work needed for a workflow data-flow view, but that different
abstractions preserve truth at different depths. `AgentContract`,
`ResolvedWorkflowBody`, `ResolvedRouteLine`, `LawBranch`, current-artifact
validation, and trust-surface carrier validation all exist before Markdown
rendering. By contrast, `ResolvedIoBody`, `CompiledAgent`, `CompiledSection`,
and rendered Markdown are already partially flattened presentation surfaces.

### Options

- Extract graph data from emitted Markdown or `CompiledAgent`.
- Extract graph data from parser/model objects before compiler resolution.
- Extract graph data from `CompilationContext` after semantic resolution but
  before Markdown rendering.

### Decision

Use `CompilationContext` as the canonical semantic extraction boundary.

The narrowest trustworthy extraction inputs are:

- `AgentContract` for concrete input/output membership
- resolved workflow slots plus `ResolvedRouteLine` for authored routes
- compiler-owned law helpers and `LawBranch` for workflow-law routes and
  currentness/trust annotations

### Consequences

- The graph IR can stay Doctrine-owned and renderer-neutral.
- The emitter can stay responsible for target scope and output paths without
  re-owning semantics.
- Parser/model syntax, Markdown rendering, and editor helpers remain
  non-semantic for this feature.
- `ResolvedIoBody` should not become the graph SSOT even though it sits near
  the right area, because it already stores compiled sections.

### Follow-ups

- Carry this boundary into `phase-plan` and implementation.
- Keep any future renderer consuming graph IR only, not compiler internals or
  emitted Markdown.

## 2026-04-10 - Reuse existing emit targets and ship a static-first sibling flow emitter

### Context

The deep-dive pass confirmed that Doctrine already has one clean repo-portable
artifact pattern:

- named targets in `[tool.doctrine.emit.targets]`
- entrypoint-local root concrete-agent discovery
- prompts-relative output placement under each configured `output_dir`
- target-backed build proof through `verify_corpus`

The same pass also confirmed that `render_markdown()` is too late and too
single-agent to own workflow graph truth.

### Options

- Add a second visualization-specific config lane and a repo-local graph tool.
- Extend `emit_docs` itself to become both the Markdown and graph emitter.
- Reuse the existing target model, add a sibling flow emitter, and keep graph
  extraction compiler-owned.

### Decision

Choose the third option.

Doctrine should:

- keep `[tool.doctrine.emit.targets]` as the v1 target registry
- add a sibling `python -m doctrine.emit_flow --target <name>` command
- extract a renderer-neutral target-level workflow graph from compiler-owned
  semantics
- emit static-first D2 source as the owned v1 graph artifact
- treat rendered SVG as a derived sibling only if the same-pass D2 rendering
  dependency is deliberately accepted

### Consequences

- The feature stays close to the current emit/proof doctrine instead of
  introducing a separate platform surface.
- The graph scope matches the current mental model of an emit target: one
  configured entrypoint, one target-level artifact family.
- Future interactive rendering remains possible without replacing target config
  or semantic extraction.
- The minimum hard proof can stay anchored on deterministic `.flow.d2` output
  without pretending binary-rendered SVG is already a stable contract.

### Follow-ups

- Completed in the 2026-04-10 phase-plan: shared target helpers,
  compiler-owned graph IR, and target-backed proof shape are now locked.
- Keep the implementation stop-line from the phase plan: if same-command SVG
  rendering cannot be supported through a pinned D2 dependency path, reopen the
  merge decision instead of silently downgrading the public feature.

## 2026-04-10 - Use example 36 as the first shipped proof target

### Context

The new emitter needs one honest end-to-end proof target on the existing
manifest-backed build-contract lane. The repo already has only three checked
emit targets, and `example_36_invalidation_and_rebuild` is the richest one for
multi-agent flow semantics.

### Options

- Add a brand-new visualization-only example and proof target.
- Reuse one of the simpler existing targets such as `07` or `14`.
- Reuse `example_36_invalidation_and_rebuild` as the first proof target.

### Decision

Choose `example_36_invalidation_and_rebuild` as the first shipped proof target
for `emit_flow`.

### Consequences

- The first end-to-end proof reuses an existing checked target instead of
  creating a parallel proof lane.
- The target exercises routes, shared outputs, currentness/trust carriers, and
  invalidation without requiring a brand-new example family.
- Newer route-only examples can adopt the same proof shape later if they add
  coverage value, but they are not required to ship v1.

### Follow-ups

- Carry `example_36_invalidation_and_rebuild` through the first build-contract
  implementation in `phase-plan`.
- Reopen the proof-target choice only if implementation shows `36` hides a
  readability or graph-shape risk that a route-only example would catch better.

## 2026-04-11 - Auto-plan hardened the artifact and handed off to implement-loop

### Context

The plan already contained research, external research, both deep-dive passes,
and a full phase plan, but the artifact still carried stale research-era notes
about corpus coverage, unresolved phase-planning questions, and a
pre-phase-plan `recommended_flow`.

### Options

- Leave the stale planning notes in place and treat the artifact as "close
  enough."
- Refresh the artifact so the document itself names the current truth and the
  next real command.

### Decision

Refresh the stale planning notes, keep the controller bounded to docs-only
planning work, and treat the next move as `implement-loop`.

### Consequences

- The planning-pass block now points at the actual next workflow move.
- Section 3 no longer contradicts the already-chosen proof target, SVG stop
  line, or shipped corpus boundary.
- The artifact is ready for bounded implementation follow-through rather than
  another planning pass.

### Follow-ups

- Next command: `Use $arch-step implement-loop docs/DOCTRINE_AGENT_DATA_FLOW_VISUALIZATION_2026-04-10.md`.

## 2026-04-11 - Implement-loop finished the feature clean

### Context

The artifact was handed off to `implement-loop` with the phase plan already
locked and with `example_36_invalidation_and_rebuild` chosen as the first
proof target.

### Options

- Land only private compiler work and reopen before a public emitter.
- Ship the full compiler -> emitter -> proof -> docs path in one bounded pass.

### Decision

Ship the full target-scoped visualization path in one pass: compiler-owned
graph extraction, a shared-target `emit_flow` command, pinned same-command D2
SVG rendering, checked proof on `example_36_invalidation_and_rebuild`, and
live-doc/install updates.

### Consequences

- The plan's three implementation phases are now present in code and proof.
- `make verify-examples` now proves the new flow artifacts without weakening
  the existing Markdown emit path.
- Repo setup now includes a pinned `npm ci` step for the SVG render surface.

### Follow-ups

- None. The final implementation audit marked the plan `COMPLETE`.
