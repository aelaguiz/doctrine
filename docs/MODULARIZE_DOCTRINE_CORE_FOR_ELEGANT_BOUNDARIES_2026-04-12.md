---
title: "Doctrine - Modularize Core For Elegant Boundaries - Architecture Plan"
date: 2026-04-12
status: active
fallback_policy: forbidden
owners:
  - doctrine maintainers
reviewers:
  - doctrine maintainers
doc_type: phased_refactor
related:
  - docs/README.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/MODULARIZE_DOCTRINE_CORE_FOR_ELEGANT_BOUNDARIES_2026-04-12_WORKLOG.md
  - doctrine/compiler.py
  - doctrine/parser.py
  - doctrine/diagnostics.py
  - doctrine/model.py
  - doctrine/verify_corpus.py
  - pyproject.toml
---

# TL;DR

- Outcome: Doctrine's shipped Python core is reorganized so the current monolithic implementation files, especially the 18,448-line compiler, are split into responsibility-based modules with stable public entrypoints and no semantic drift across the shipped corpus.
- Problem: `doctrine/compiler.py` currently mixes compilation session orchestration, import loading, flow extraction, route and review semantics, contract validation, addressability, final-output lowering, and readable rendering prep in one catch-all file; other large core files also carry broad surfaces that make ownership and safe change harder than they should be.
- Approach: Refactor the shipped `doctrine/` core around explicit internal module boundaries and thin canonical boundary modules, moving one concern to one owner path at a time while preserving existing CLI, import, docs, diagnostics, and manifest-backed behavior.
- Plan: First ground the real seams and public-boundary requirements, then design the target module map and migration sequence, then execute the split depth-first with behavior-preservation checks after each extraction.
- Non-negotiables: No DSL feature creep, no silent semantic drift, no new parallel ownership paths, no compatibility spaghetti, and no live duplicates left behind after a cutover.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-12
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None. The final boundary-comment cleanup is present in shipped source, and
  both final proof surfaces passed in this audit run.

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
deep_dive_pass_1: done 2026-04-12
external_research_grounding: not required 2026-04-12 (internal repo truth was sufficient)
deep_dive_pass_2: done 2026-04-12
recommended_flow: implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

Doctrine can be modularized so the current 18,448-line `doctrine/compiler.py`
stops being the system's catch-all owner, the other large shipped core modules
gain explicit responsibility boundaries, and the repo still passes the shipped
corpus proof surface without language or behavior regressions.

## 0.2 In scope

- The shipped Python core under `doctrine/`, with first-class attention to
  `compiler.py`, `parser.py`, `diagnostics.py`, `model.py`, and any directly
  coupled helper modules they currently force to co-own behavior.
- Introducing internal subpackages or responsibility-specific modules under
  `doctrine/` when that is the cleanest canonical owner path.
- Updating `pyproject.toml` packaging and module discovery if subpackages are
  introduced.
- Migrating internal imports, tests, emit helpers, verifier code, and live docs
  or comments needed to reflect the new boundaries truthfully.
- Deleting superseded helpers or dead code as each canonical path lands.

## 0.3 Out of scope

- New language features, syntax, or semantics sold as "modularization."
- Broad UX or editor redesign in `editors/vscode/` unless a core module
  boundary change forces minimal follow-through.
- Performance work except where an extraction would otherwise regress the
  current shared-session or verification behavior.
- File splitting done only to hit arbitrary line-count targets without a real
  ownership improvement.
- Archive-style preservation of old implementations or duplicate paths after
  the new owner path lands.

## 0.4 Definition of done (acceptance evidence)

- Each targeted monolithic surface has one explicit disposition in the plan:
  split, keep with justification, or absorb into a clearer owner.
- The biggest mixed-responsibility surfaces are split into modules with one
  primary concern each; `doctrine/compiler.py` becomes either a thin public
  facade or a clearly bounded orchestration layer instead of the catch-all
  owner.
- `make verify-examples` passes after the refactor, and
  `make verify-diagnostics` also passes whenever diagnostics behavior or
  diagnostic code changes.
- Focused unit coverage continues to prove the extracted boundaries that matter
  most, especially compilation session behavior, route and review semantics,
  final-output handling, import loading, and emitted output rendering.
- Public and docs-facing entrypoints remain coherent: imports, emit commands,
  verifier workflow, and live docs all describe the same architecture.
- No duplicate legacy implementation path remains live after cutover.

## 0.5 Key invariants (fix immediately if violated)

- No silent semantic drift. If behavior changes, it must be deliberate, logged,
  and re-proved.
- No new parallel compile pipeline or second semantic-resolution subsystem.
- No public-facing feature work disguised as refactor.
- No compatibility wrapper that carries real logic; if a facade remains, it is
  a thin stable boundary only.
- No package layout change that breaks shipped tooling without same-pass repair.
- No refactor phase closes without running the smallest credible
  behavior-preservation signal for the code it moved.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Preserve shipped language behavior and proof surfaces while changing
   internals aggressively enough to remove the monoliths.
2. Establish one clear owner path per concern instead of line-count-only file
   splits.
3. Make the compiler core navigable enough that route, review, addressability,
   final-output, and import work can evolve without spelunking one huge file.
4. Keep public entrypoints and operator workflows coherent while internals move.
5. Delete superseded code as part of each cutover instead of normalizing
   parallel paths.

## 1.2 Constraints

- `pyproject.toml` currently ships only the top-level `doctrine` package, so
  any new subpackage layout must include packaging updates.
- Tests and shipped tools import top-level modules such as
  `doctrine.compiler`, `doctrine.parser`, `doctrine.diagnostics`, and
  `doctrine.renderer`, so public boundary decisions cannot be accidental.
- The repo treats `doctrine/` plus the manifest-backed example corpus as
  shipped truth, so architecture cleanup must stay aligned with proof and docs.
- `doctrine/compiler.py` currently owns a very wide set of behaviors, which
  creates real risk of import cycles or partial abstractions during extraction.
- The refactor must stay fail-loud and deterministic; this repo does not want
  magical compatibility layers or soft-fallback architecture.

## 1.3 Architectural principles (rules we will enforce)

- Split by responsibility and canonical owner, not by arbitrary line counts.
- Keep orchestration near the boundary and move heavy detail into explicit
  submodules.
- Preserve a stable public import story exactly once; do not let every call
  site invent its own path.
- Delete superseded internal paths immediately after the canonical replacement
  proves out.
- Make boundaries real in code: imports, data shapes, session ownership,
  validation entrypoints, and package layout should reveal the design without
  needing doctrine-by-comment.

## 1.4 Known tradeoffs (explicit)

- A semantics-preserving modularization can still require broad file movement
  and packaging churn, especially around `doctrine/compiler.py`.
- Some files may remain relatively large if they truly own one dense concept;
  elegance here means clear responsibility, not blindly minimizing every file.
- Preserving current public entrypoints may require thin facades at the package
  boundary, but those facades must stay logic-light or they become a new
  monolith in disguise.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- `doctrine/compiler.py` is currently 18,448 lines and owns both high-level
  compilation entrypoints and a large amount of subsystem detail.
- `doctrine/parser.py` is 2,705 lines, `doctrine/diagnostics.py` is 2,425
  lines, and `doctrine/model.py` is 1,399 lines, so the monolithic pressure is
  not isolated to a single file.
- Shipped tools and tests import the top-level modules directly, and the
  package layout is still a flat `doctrine/` package rather than a clearly
  layered set of internal owners.
- The repo already has strong proof surfaces through manifest-backed examples,
  targeted tests, and diagnostic smoke coverage, so the refactor can be held to
  real preservation signals.

## 2.2 What's broken / missing (concrete)

- The current compiler file mixes too many concerns for ownership to be
  obvious.
- Safe changes to route, review, final-output, addressability, or import logic
  require navigating a very large function forest in one file.
- The package layout does not currently reflect the conceptual seams implied by
  the implementation.
- "Beautiful code" is blocked by architecture more than naming polish: the
  main issue is unclear ownership and mixed concerns, not just local style.

## 2.3 Constraints implied by the problem

- The refactor must be staged around real seams rather than a one-shot rewrite.
- Packaging and import-boundary decisions are part of the work, not follow-up.
- The compiler monolith is the highest-pressure surface, but secondary
  monoliths must also receive an explicit disposition so the plan does not stop
  at one cosmetic split.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- None adopted in this pass — reject importing generic compiler-modularization
  prior art at the research stage — this repo already exposes the decisive
  constraints through its public imports, package layout, proof surfaces, and
  current file ownership.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/compiler.py` — current public compile boundary and current
    monolith. It owns `CompilationSession`, `CompilationContext`,
    `compile_prompt`, `extract_target_flow_graph`, compiled readable block
    types, flow graph types, import loading, route and review semantics,
    final-output lowering, addressability, validation, and much of the runtime
    orchestration.
  - `doctrine/parser.py` plus `doctrine/grammars/doctrine.lark` — authored
    syntax-to-AST boundary. Modularization should not smear parse ownership back
    into compiler internals.
  - `doctrine/model.py` — declaration and AST shape owner. It already models
    the language as data and is the strongest existing example of a
    responsibility-focused module in the core.
  - `doctrine/diagnostics.py` — stable parse/compile/emit diagnostic types and
    formatting surface. Any extraction that changes failure ownership must still
    preserve this public error boundary.
  - `doctrine/renderer.py` — Markdown rendering boundary. It currently imports
    many `Compiled*` readable structures plus `ResolvedRenderProfile` from
    `doctrine.compiler`, which proves the compiler file is serving as both
    algorithm owner and shared type bucket.
  - `doctrine/flow_renderer.py` — flow rendering boundary. It imports
    `FlowGraph`, `FlowAgentNode`, `FlowInputNode`, `FlowOutputNode`, and
    `FlowEdge` from `doctrine.compiler`, which creates the same boundary
    pressure around flow graph types.
  - `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, `doctrine/verify_corpus.py`,
    `doctrine/diagnostic_smoke.py`, and `tests/` — direct consumers of the
    current top-level module boundaries, so these files define the preservation
    bar for any package or module-layout change.
  - `pyproject.toml` — packaging truth. The project currently declares
    `packages = ["doctrine"]`, which means any new subpackage layout requires
    same-pass packaging changes instead of assuming setuptools will discover
    those modules automatically.
- Canonical path / owner to reuse:
  - `doctrine/compiler.py` — preserve it as the stable public compile boundary
    for this refactor wave because tools and tests already import
    `CompilationSession`, `compile_prompt`, and `extract_target_flow_graph`
    directly from it. Deep-dive should move real subsystem ownership behind this
    boundary rather than forcing a public import migration by default.
  - `doctrine/parser.py`, `doctrine/diagnostics.py`, `doctrine/renderer.py`,
    `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, and
    `doctrine/verify_corpus.py` — treat these as stable top-level operator
    boundaries unless deep-dive finds a concrete reason to change them.
- Existing patterns to reuse:
  - `doctrine/compiler.py` — `CompilationSession` versus `CompilationContext`
    already expresses a useful conceptual split between shared prompt-graph
    state and task-local compile work. The refactor should turn that implicit
    split into real modules instead of inventing a second compile model.
  - `doctrine/emit_common.py` — focused shared helper module reused by
    `emit_docs.py` and `emit_flow.py`. This is the best shipped example of
    pulling common logic into a small owner without multiplying public
    boundaries.
  - `doctrine/model.py` plus `doctrine/parser.py` — AST/data ownership and
    parse ownership are already separate. Compiler decomposition should respect
    that line instead of re-entangling those layers.
  - `doctrine/project_config.py` — dedicated config-loading owner. Packaging and
    compile-config concerns should stay similarly isolated during the split.
  - `doctrine/verify_corpus.py::_CompilationSessionCache` — existing proof that
    session reuse matters operationally. Any compiler extraction must preserve
    the current shared-session story rather than accidentally fragmenting it.
- Prompt surfaces / agent contract to reuse:
  - Not applicable. This change is ordinary Python architecture work, not an
    agent-capability design problem.
- Native model or agent capabilities to lean on:
  - Not applicable. The decisive levers are module boundaries, imports,
    packaging, and proof surfaces already present in the repo.
- Existing grounding / tool / file exposure:
  - `codex features list` with `codex_hooks` enabled and the installed Stop hook
    under `~/.agents/skills/arch-step/scripts/arch_controller_stop_hook.py` —
    the controller runtime needed for `auto-plan` is available for this doc.
  - `tests/test_final_output.py` — preserves final-output compile and render
    behavior across compiler changes.
  - `tests/test_review_imported_outputs.py` — preserves review/output
    interaction behavior.
  - `tests/test_route_output_semantics.py` — preserves route-output semantics in
    the compiler core.
  - `tests/test_import_loading.py` — preserves import and module-loading
    behavior.
  - `tests/test_emit_flow.py` — preserves flow extraction/rendering behavior
    across flow-related extractions.
  - `doctrine/diagnostic_smoke.py` — broad smoke coverage for diagnostics and
    rendered output behavior that would regress quickly if ownership moves
    broke surface contracts.
- Duplicate or drifting paths relevant to this change:
  - `doctrine/compiler.py` currently co-locates public boundary types,
    orchestration, declaration resolution, validation, route/review semantics,
    final-output work, addressability, readable compilation, and flow graph
    extraction in one owner. This is the primary drift surface the plan must
    cut apart.
  - `doctrine/renderer.py` and `doctrine/flow_renderer.py` both depend on types
    still defined in `doctrine/compiler.py`, so moving only behavior without
    deciding where those shared shapes live would produce a new hidden monolith.
  - `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, `doctrine/verify_corpus.py`,
    `doctrine/diagnostic_smoke.py`, and several tests all instantiate
    `CompilationSession` directly. Deep-dive needs to preserve one canonical
    orchestration entrypoint instead of letting each call site grow its own.
- Capability-first opportunities before new tooling:
  - Use ordinary Python package structure first: focused modules, internal
    subpackages, and thin facades can solve this without generators, audit
    scripts, or new architecture tooling.
  - Reuse existing proof surfaces first: `make verify-examples`,
    `make verify-diagnostics`, and targeted tests already protect the behavior
    that matters, so there is no need for file-shape or grep-based gates.
- Behavior-preservation signals already available:
  - `make verify-examples` — shipped manifest-backed corpus proof.
  - `make verify-diagnostics` — diagnostic behavior proof when diagnostics
    change.
  - `tests/test_final_output.py` — final-output preservation.
  - `tests/test_review_imported_outputs.py` — review/output preservation.
  - `tests/test_route_output_semantics.py` — route/output preservation.
  - `tests/test_import_loading.py` — import and module-loading preservation.
  - `tests/test_emit_flow.py` — flow extraction/rendering preservation.
  - `doctrine/diagnostic_smoke.py` — broad smoke coverage for compile/render
    error and output surfaces.

## 3.3 Decision gaps that must be resolved before implementation

- None blocking. Deep-dive pass 1 resolves the architecture-shaping choices
  that research left open:
  - preserve the current top-level module entrypoints as stable public
    boundaries by default
  - move compiler internals behind a dedicated `doctrine._compiler` package
  - give `Compiled*` and `Flow*` types one internal owner in
    `doctrine._compiler.types`
  - keep `parser.py`, `model.py`, and `diagnostics.py` as first-wave stable
    owners unless implementation exposes a concrete split that is required for
    correctness or clarity
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/` is effectively a flat package: top-level Python modules plus
  `grammars/`, with no internal compiler subpackage today.
- `doctrine/compiler.py` is both the public compile boundary and the main
  implementation dumping ground. It defines compiled render types, flow graph
  types, `IndexedUnit`, session setup, module loading, graph extraction, route
  and review semantics, final-output lowering, validation, display helpers, and
  readable compilation support in one file.
- `CompilationContext` is the main concentration point inside that file. The
  current class carries 134 `_resolve_` helpers, 55 `_compile_`, 32
  `_validate_`, 31 `_review_`, 14 `_flow_`, 12 `_route_`, and 29 `_render_`
  helpers, alongside the public orchestration entrypoints.
- `doctrine/renderer.py` imports `Compiled*` structures plus
  `ResolvedRenderProfile` from `doctrine.compiler`, and
  `doctrine/flow_renderer.py` imports `Flow*` structures from
  `doctrine.compiler`, so the compiler file doubles as a shared type bucket for
  other top-level modules.
- `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, `doctrine/verify_corpus.py`,
  `doctrine/diagnostic_smoke.py`, and focused tests all import top-level
  compiler APIs directly, which makes `doctrine.compiler` the current operator
  boundary whether or not the implementation deserves that coupling.
- `doctrine/__init__.py` exports only error types today, so introducing an
  internal `doctrine._compiler` package does not require reshaping the package
  root export story.
- `pyproject.toml` currently declares `packages = ["doctrine"]`, so the build
  config only ships the top-level package and would drop any new internal
  subpackages unless packaging changes land in the same pass.

## 4.2 Control paths (runtime)

1. `doctrine/parser.py` parses source text into `model.PromptFile` via the
   grammar and `ToAst`; this is the syntax-to-AST boundary.
2. `CompilationSession.__init__` resolves project config, prompt roots, import
   roots, module caches, module-loading locks, and the root `IndexedUnit`.
3. Public compile entrypoints such as `compile_agent`,
   `compile_readable_declaration`, and `extract_target_flow_graph` each create a
   fresh `CompilationContext`, then prepend trace and location data at the
   session boundary when failures escape.
4. `CompilationContext` performs the real work: declaration and body
   resolution, addressable lookup, contract and law validation, route and
   review semantics, final-output lowering, readable compilation, and flow
   graph extraction.
5. `doctrine/renderer.py` turns `Compiled*` readable structures into Markdown,
   and `doctrine/flow_renderer.py` turns `Flow*` graph structures into D2/SVG.
6. `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, `doctrine/verify_corpus.py`,
   and `doctrine/diagnostic_smoke.py` all drive those same surfaces, so the
   refactor has to preserve one shared compile story across CLI, tests, emit,
   and proof tooling.
7. `CompilationSession.compile_agents` and
   `verify_corpus._CompilationSessionCache` already rely on shared session state
   plus task-local contexts, so the session/context split is operational today
   even though the file boundary does not express it cleanly.

## 4.3 Object model + key abstractions

- `doctrine/model.py` is the authored declaration and AST surface. It is broad,
  but the breadth is mostly taxonomic rather than algorithmically mixed.
- `IndexedUnit` is the in-memory declaration registry and import-graph node
  used by compile-time resolution.
- `CompilationSession` owns shared prompt-graph state, project config, import
  roots, and module-loading caches.
- `CompilationContext` owns task-local stacks and caches, but it currently also
  owns most subsystem implementation detail.
- `Compiled*` dataclasses are the render contract consumed by
  `doctrine/renderer.py`.
- `Flow*` dataclasses are the graph contract consumed by
  `doctrine/flow_renderer.py`.
- The current architecture blurs three kinds of ownership inside
  `doctrine/compiler.py`: public boundary, shared data shapes, and subsystem
  implementation.

## 4.4 Observability + failure behavior today

- `doctrine/diagnostics.py` is the stable parse/compile/emit error-model and
  formatting boundary.
- `CompilationSession` wraps public entrypoints with explicit trace and
  location repair so errors fail loud with user-meaningful context.
- `tests/test_import_loading.py` proves cyclic imports fail loudly instead of
  hanging, which makes import/indexing extraction safety-critical.
- `tests/test_final_output.py`, `tests/test_review_imported_outputs.py`, and
  `tests/test_route_output_semantics.py` protect final-output, review/output,
  and route/output behavior across compiler changes.
- `tests/test_emit_flow.py`, `doctrine/diagnostic_smoke.py`,
  `make verify-examples`, and `make verify-diagnostics` protect the broader
  flow, diagnostics, and shipped-corpus surfaces.

## 4.5 UI surfaces (ASCII mockups, if UI work)

- Not applicable. This is a shipped core architecture refactor, not UI work.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Preserve the current top-level operator modules as the public repo surface:
  `compiler.py`, `parser.py`, `diagnostics.py`, `renderer.py`,
  `flow_renderer.py`, `emit_docs.py`, `emit_flow.py`, `verify_corpus.py`,
  `emit_common.py`, and `project_config.py`.
- Replace the explicit `packages = ["doctrine"]` packaging config with
  setuptools package discovery that includes `doctrine*`, so `doctrine._compiler`
  ships automatically without hand-maintained package lists.
- Add one internal compiler package, `doctrine._compiler`, and move real
  subsystem ownership there:

```text
doctrine/
  compiler.py
  parser.py
  model.py
  diagnostics.py
  renderer.py
  flow_renderer.py
  emit_docs.py
  emit_flow.py
  verify_corpus.py
  emit_common.py
  project_config.py
  _compiler/
    __init__.py
    types.py
    session.py
    indexing.py
    context.py
    resolve.py
    compile.py
    validate.py
    flow.py
    display.py
```

- `doctrine/compiler.py` becomes a thin public facade that re-exports the
  stable compile APIs from `doctrine._compiler.session` and contains no
  subsystem logic forest.
- `doctrine._compiler.types.py` becomes the single owner for `Compiled*`,
  `Flow*`, and `ResolvedRenderProfile` contracts consumed by `renderer.py` and
  `flow_renderer.py`.
- `doctrine._compiler.indexing.py` owns `IndexedUnit`, declaration indexing,
  prompt-root/module-root resolution, import loading, and cycle-handling.
- `doctrine._compiler.session.py` owns `CompilationSession`,
  `compile_prompt`, `extract_target_flow_graph`, and the shared-session setup
  contract.
- `doctrine._compiler.context.py` keeps only task-local stacks, caches, and
  orchestration glue; it no longer owns every subsystem implementation detail.
- `doctrine._compiler.resolve.py`, `compile.py`, `validate.py`, `flow.py`, and
  `display.py` own the corresponding helper families now buried in the
  monolith.
- `parser.py`, `model.py`, and `diagnostics.py` are explicitly kept as
  first-wave stable owners. Their disposition in this plan is `keep with
  justification`, not `split speculatively`.

## 5.2 Control paths (future)

1. `parser.py` remains the only syntax-to-AST entrypoint.
2. `doctrine.compiler` remains the only public compile entrypoint, but it
   delegates immediately into `doctrine._compiler.session`.
3. `doctrine._compiler.session` owns project-config loading, prompt roots,
   import roots, module caches, and root indexing; it no longer shares a file
   with validation, rendering prep, or flow extraction details.
4. `doctrine._compiler.context` constructs the task-local work surface and
   delegates to:
   - `resolve.py` for declaration, body, and addressable resolution
   - `compile.py` for agent/readable/final-output compilation
   - `validate.py` for output, route, review, law, and schema validation
   - `flow.py` for flow graph extraction
   - `display.py` for helper display/text generation
5. `renderer.py` imports compiled readable types and `ResolvedRenderProfile`
   from `doctrine._compiler.types` instead of routing through the public
   facade.
6. `flow_renderer.py` imports flow graph types from `doctrine._compiler.types`
   instead of routing through the public facade.
7. `emit_docs.py`, `emit_flow.py`, `verify_corpus.py`, `diagnostic_smoke.py`,
   and focused tests keep their current top-level `doctrine.compiler` imports
   unless a repo-wide simplification is proven necessary later. The public
   operator story stays stable while the internals move.
8. Internal import policy after cutover:
   - modules inside `doctrine._compiler` import one another directly
   - `renderer.py` and `flow_renderer.py` may import `doctrine._compiler.types`
     directly because that module is the canonical owner of shared compiled data
   - other top-level operator modules keep using the stable top-level boundaries
     rather than reaching into `doctrine._compiler`

## 5.3 Object model + abstractions (future)

- `model.py` remains the single source of truth for authored declarations and
  AST data.
- `doctrine._compiler.indexing` owns import-graph and declaration-registry
  shapes such as `IndexedUnit`.
- `doctrine._compiler.types` owns the render-facing and flow-facing compiled
  data contracts plus the shared render-profile value object they carry.
- `doctrine._compiler.session` owns the shared compile lifecycle and public
  error-wrapping boundary.
- `doctrine._compiler.context` is a thin coordinator, not a catch-all
  subsystem owner.
- `doctrine._compiler.resolve` owns `_resolve_*` families and addressable
  lookup.
- `doctrine._compiler.compile` owns `_compile_*` families, including readable
  payload and final-output construction.
- `doctrine._compiler.validate` owns `_validate_*`, `_review_*`, and `_route_*`
  invariant enforcement.
- `doctrine._compiler.flow` owns flow graph extraction and flow helper logic.
- `doctrine._compiler.display` owns display/text helpers now mixed into the
  monolith.

## 5.4 Invariants and boundaries

- `doctrine/compiler.py` must not retain substantive `_resolve_`, `_compile_`,
  `_validate_`, `_review_`, `_route_`, or `_flow_` helper forests after the
  cutover.
- The repo keeps one stable public compile boundary: `doctrine.compiler`.
- The repo keeps one shared-session implementation path:
  `doctrine._compiler.session`.
- The repo keeps one owner for compiled render/flow types:
  `doctrine._compiler.types`.
- The repo keeps one owner for declaration indexing and import loading:
  `doctrine._compiler.indexing`.
- `renderer.py` and `flow_renderer.py` must not depend on the public facade for
  internal type definitions once `doctrine._compiler.types` exists.
- Packaging must use discovery for `doctrine*` so the internal subpackage ships
  without hand-maintained package lists.
- `doctrine._compiler` stays intentionally private to the package; new external
  or operator-facing imports should not grow directly against it.
- No temporary parallel old/new implementations remain live after each moved
  subsystem proves out.

## 5.5 UI surfaces (ASCII mockups, if UI work)

- Not applicable. This is a shipped core architecture refactor, not UI work.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Packaging | `pyproject.toml` | `[tool.setuptools].packages` | ships only `["doctrine"]` | replace explicit package list with setuptools package discovery for `doctrine*` | the internal package must ship in the same pass as the refactor | build config discovers every `doctrine` subpackage automatically | `make verify-examples`, import-loading coverage |
| Public compile boundary | `doctrine/compiler.py` | `CompilationSession`, `compile_prompt`, `extract_target_flow_graph`, compile facade | public entrypoints and almost all implementation logic share one file | reduce to a thin facade over `doctrine._compiler.session` | preserve operator imports while removing monolith ownership | one stable top-level compile boundary, minimal logic | `tests/test_final_output.py`, `tests/test_review_imported_outputs.py`, `tests/test_route_output_semantics.py`, `tests/test_import_loading.py`, `tests/test_emit_flow.py`, `doctrine/diagnostic_smoke.py` |
| Session lifecycle | `doctrine/compiler.py` -> `doctrine/_compiler/session.py` | `CompilationSession`, `compile_agents`, compile wrappers | shared-session lifecycle lives beside unrelated helper forests | move session lifecycle into dedicated internal owner | session reuse and public error wrapping are central and deserve one home | session module owns shared caches and public wrappers | same broad compile/test surfaces |
| Import graph and indexing | `doctrine/compiler.py` -> `doctrine/_compiler/indexing.py` | `IndexedUnit`, `_index_unit`, `_load_imports`, `_load_module`, `_resolve_module_root` | registry/indexing and import loading live beside rendering, validation, and flow logic | move indexing and import loading into dedicated owner | cyclic-import handling and registry truth are separate concerns | one indexing owner consumed by session/context only | `tests/test_import_loading.py`, `make verify-examples` |
| Context orchestration | `doctrine/compiler.py` -> `doctrine/_compiler/context.py` | `CompilationContext.__init__`, public orchestration methods | context owns task-local stacks/caches and also every subsystem family | keep only orchestration and cache plumbing in context | task-local orchestration should not be the subsystem dumping ground | context delegates to internal subsystem modules | all compile/test surfaces indirectly |
| Resolution subsystem | `doctrine/compiler.py` -> `doctrine/_compiler/resolve.py` | `_resolve_*`, addressable/declaration lookup families | 134 resolve helpers are mixed into context | move all resolution helpers behind one subsystem owner | declaration/body/addressable resolution needs one obvious home | `resolve.py` is the only owner for `_resolve_*` families | route, review, final-output, and corpus proof surfaces |
| Compilation subsystem | `doctrine/compiler.py` -> `doctrine/_compiler/compile.py` | `_compile_*`, readable payload builders, final-output construction | compile helpers are mixed with validation and flow | move compile helpers into one owner | compiled-output construction becomes navigable and testable | `compile.py` is the only owner for `_compile_*` families | final-output, review-output, diagnostics smoke, corpus proof |
| Validation subsystem | `doctrine/compiler.py` -> `doctrine/_compiler/validate.py` | `_validate_*`, `_review_*`, `_route_*` invariant logic | fail-loud validation is scattered through the monolith | move validation into one owner | compile-time invariants need a single canonical owner | `validate.py` is the only owner for output/law/review/route/schema checks | route semantics, review outputs, diagnostics, corpus proof |
| Flow subsystem | `doctrine/compiler.py` -> `doctrine/_compiler/flow.py` | flow extraction helpers and lane/detail helpers | flow graph extraction lives inside compiler monolith | move graph extraction helpers into one owner | `emit_flow` should depend on a flow owner, not a compiler dumping ground | `flow.py` owns graph extraction while session keeps public wrapper | `tests/test_emit_flow.py`, `doctrine/emit_flow.py`, corpus proof |
| Display subsystem | `doctrine/compiler.py` -> `doctrine/_compiler/display.py` | `_render_*` and display/text helper families | readable display helpers are mixed into the compiler monolith | move display/text helpers into one owner | readable compilation and display prep need an explicit home instead of lingering as monolith residue | `display.py` is the only owner for `_render_*` and related display/text helpers | final-output, review-output, diagnostics smoke, corpus proof |
| Shared compiled/flow/render-profile types | `doctrine/compiler.py` -> `doctrine/_compiler/types.py` | `Compiled*`, `Flow*`, `ResolvedRenderProfile` | compiler file doubles as type bucket for renderers | move shared compiled, flow, and render-profile contracts to one internal module | remove type-owner pressure from the public facade | one internal type owner used by renderer and flow renderer | renderer/flow rendering coverage, final-output tests, emit-flow tests |
| Markdown renderer | `doctrine/renderer.py` | `from doctrine.compiler import Compiled*, ResolvedRenderProfile` | imports shared render contracts through public compiler facade | import `Compiled*` and `ResolvedRenderProfile` from `doctrine._compiler.types` directly | renderer should depend on the type owner, not the facade | renderer consumes the internal shared render contract directly | final-output, review-output, route-output, diagnostics smoke, corpus proof |
| Flow renderer | `doctrine/flow_renderer.py` | `from doctrine.compiler import Flow*` | imports flow types through public compiler facade | import `Flow*` from `doctrine._compiler.types` directly | flow renderer should depend on the type owner, not the facade | flow renderer consumes internal flow-type contract directly | `tests/test_emit_flow.py`, `doctrine/emit_flow.py` |
| Operator surfaces | `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, `doctrine/verify_corpus.py`, `doctrine/diagnostic_smoke.py`, `tests/test_*.py` | direct `doctrine.compiler` imports | already depend on top-level compile boundary | keep these imports stable in the first wave | avoid needless churn and preserve repo/public operator story | same top-level compile API after refactor | all named proof surfaces |
| Package root | `doctrine/__init__.py` | error re-exports only | package root does not currently expose compiler internals | keep package-root export story unchanged | `_compiler` can remain private without broad top-level churn | package root still exports only error types | import and corpus proof surfaces |
| Stable syntax/data/error owners | `doctrine/parser.py`, `doctrine/model.py`, `doctrine/diagnostics.py` | parse API, AST classes, diagnostic types/formatting | broad but currently coherent ownership surfaces | keep as first-wave stable owners; update imports only if extraction requires it | current pressure is lower and ownership is clearer than in compiler | no first-wave public split for these files | `make verify-examples`, `make verify-diagnostics`, targeted tests |

## 6.2 Migration notes

* Canonical owner path / shared code path:
  - top-level public compile boundary stays `doctrine.compiler`
  - real compile implementation moves under `doctrine._compiler`
* Deprecated APIs (if any):
  - internal repo pattern where top-level modules import `Compiled*` or `Flow*`
    from `doctrine.compiler`; after cutover those imports should point at
    `doctrine._compiler.types`
* Delete list (what must be removed; include superseded shims/parallel paths if any):
  - migrated helper implementations left in `doctrine/compiler.py`
  - compiler-as-type-bucket imports once renderer and flow-renderer move to
    `doctrine._compiler.types`
  - any temporary compatibility alias kept longer than one migration phase
* Capability-replacing harnesses to delete or justify:
  - none; this refactor should use ordinary Python package structure and
    existing proof surfaces only
* Live docs/comments/instructions to update or delete:
  - no public user docs are required to change unless package/build behavior
    becomes contributor-facing during implementation
  - add one short high-leverage boundary comment at the top-level compiler
    facade explaining that real implementation lives under
    `doctrine._compiler`
  - add one short comment in `doctrine/_compiler/__init__.py` stating that the
    package is internal and not the public operator surface
  - add one short comment in `doctrine/_compiler/types.py` explaining why
    renderer and flow-renderer import this module directly
* Behavior-preservation signals for refactors:
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics code changes
  - `tests/test_final_output.py`
  - `tests/test_review_imported_outputs.py`
  - `tests/test_route_output_semantics.py`
  - `tests/test_import_loading.py`
  - `tests/test_emit_flow.py`
  - `doctrine/diagnostic_smoke.py`

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Compiler boundary | `doctrine/compiler.py` | thin public facade over internal owner package | prevents the monolith from re-forming around the public entrypoint | include |
| Shared data contracts | `doctrine/renderer.py`, `doctrine/flow_renderer.py`, `doctrine._compiler.types.py` | one internal owner for compiled, flow, and shared render-profile contracts | prevents compiler facade from remaining a hidden type bucket | include |
| Shared-session lifecycle | `doctrine._compiler.session.py`, `doctrine/verify_corpus.py::_CompilationSessionCache` | one shared-session story, task-local contexts only | prevents parallel compile/session implementations | include |
| Small focused helpers | `doctrine/emit_common.py` | small reusable owner modules instead of sprawling facades | gives the compiler refactor a shipped local precedent | include |
| Private package boundary | `doctrine._compiler`, top-level operator modules | keep `_compiler` private and route operator usage through stable top-level boundaries | prevents internal implementation details from becoming the new public sprawl | include |
| Stable syntax/data/error owners | `doctrine/parser.py`, `doctrine/model.py`, `doctrine/diagnostics.py` | keep coherent first-wave owners intact unless implementation proves otherwise | avoids speculative widening and line-count theater | exclude |
| Operator imports | emit surfaces, tests, diagnostic smoke | keep top-level `doctrine.compiler` import contract stable | avoids churn and preserves public operator story during internal cutover | include |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Package discovery and shared type-owner cut

Status: COMPLETE

Completed work:

- replaced the explicit setuptools package list in `pyproject.toml` with
  package discovery for `doctrine*`
- added `doctrine/_compiler/__init__.py`
- moved `Compiled*`, `Flow*`, and `ResolvedRenderProfile` into
  `doctrine/_compiler/types.py`
- updated `doctrine/compiler.py` to re-export those shared contracts from the
  new internal owner
- switched `doctrine/renderer.py` and `doctrine/flow_renderer.py` to import
  shared contracts from `doctrine._compiler.types`

Tests run + results:

- `uv sync` — rebuilt and reinstalled the local `doctrine` package successfully
- `npm ci` — installed the pinned D2 dependency successfully
- `uv run --locked python -m unittest tests.test_emit_flow tests.test_final_output tests.test_review_imported_outputs` — `OK` (`22` tests)
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml` — all manifest cases passed

* Goal:
  Make `doctrine._compiler` shippable and establish one honest owner for
  shared compiled, flow, and render-profile contracts before extracting
  higher-level compiler behavior.
* Work:
  - replace explicit setuptools package listing in `pyproject.toml` with
    package discovery for `doctrine*`
  - add `doctrine/_compiler/__init__.py`
  - move `Compiled*`, `Flow*`, and `ResolvedRenderProfile` into
    `doctrine/_compiler/types.py`
  - update `doctrine/compiler.py` to re-export those types while preserving the
    current top-level boundary
  - switch `doctrine/renderer.py` and `doctrine/flow_renderer.py` to import
    their shared data contracts from `doctrine._compiler.types`
* Verification (smallest signal):
  - `uv run --locked python -m unittest tests.test_emit_flow tests.test_final_output tests.test_review_imported_outputs`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml`
* Docs/comments (propagation; only if needed):
  - add one short comment in `doctrine/_compiler/__init__.py` that the package
    is internal
  - add one short comment in `doctrine/_compiler/types.py` that renderer and
    flow-renderer consume the canonical shared compiled data here
* Exit criteria:
  - `doctrine._compiler` ships via package discovery
  - renderer and flow-renderer no longer rely on `doctrine.compiler` as a type
    bucket
  - public compile imports still resolve unchanged
* Rollback:
  - revert package discovery and restore type definitions to
    `doctrine/compiler.py`

## Phase 2 — Session and indexing foundation extraction

Status: COMPLETE

Completed work:

- added `doctrine/_compiler/session.py` as the shared session owner for
  `CompilationSession`, `compile_prompt`, and `extract_target_flow_graph`
- added `doctrine/_compiler/indexing.py` as the owner for `IndexedUnit`,
  declaration indexing, prompt-root/module-root resolution, and import loading
- added `doctrine/_compiler/support.py` so the internal session/indexing owners
  no longer import prompt-root, import-root, path-location, worker-count, or
  dotted-declaration helpers from `doctrine.compiler`
- added `doctrine/_compiler/context.py` so the internal session owner no longer
  imports `CompilationContext` from the top-level compiler boundary, and the
  compile-context state plus public entrypoints now live in that internal
  module
- added `doctrine/_compiler/shared.py` as the canonical internal owner for the
  shared compiler support types, helper functions, and constants that the
  moved context/session/indexing code still needs
- removed the live session/indexing implementation block from
  `doctrine/compiler.py` and re-exported the stable top-level boundary from the
  new internal owners
- stopped `doctrine/_compiler/context.py` from importing `doctrine.compiler`
  and copying its module globals; it now imports static support names from the
  internal shared owner instead
- reduced `doctrine/_compiler/context.py` to task-local state, public
  entrypoints, and session delegation while the remaining helper families moved
  behind the internal mixins

Missing (code):

- none for the planned Phase 2 foundation split; the shared session/indexing
  owners are real and `CompilationContext` is now the intended thin task-local
  dispatcher boundary.

Tests run + results:

- `uv run --locked python - <<'PY' ...` import sanity check — `doctrine.compiler`
  re-exported the internal `CompilationSession` and callable wrappers
- `rg -n "doctrine\\.compiler|compiler as _compiler|globals\\(\\)\\.setdefault|_CompilationContextImpl"`
  across `doctrine/_compiler/context.py`, `doctrine/compiler.py`, and
  `doctrine/_compiler/shared.py` — only the shared-owner boundary comment in
  `shared.py` matched after the cleanup
- `uv run --locked python - <<'PY' ...` direct `_compiler.context` import
  sanity check — `CompilationContext` loads from
  `doctrine._compiler.context`, `CompilationSession` loads from
  `doctrine._compiler.session`, and the public compiler callables stay live
- `uv run --locked python - <<'PY' ...` thin-context import sanity check —
  `CompilationContext` now keeps only state, entrypoints, and `_load_module`
  locally while inheriting the flow, validate, compile, display, and resolve
  owners
- `python -m py_compile doctrine/compiler.py doctrine/_compiler/shared.py
  doctrine/_compiler/context.py doctrine/_compiler/session.py
  doctrine/_compiler/indexing.py doctrine/_compiler/support.py` — all compiled
  cleanly
- `uv run --locked python -m unittest tests.test_import_loading tests.test_project_config tests.test_verify_corpus tests.test_final_output tests.test_review_imported_outputs tests.test_route_output_semantics` — `OK` (`32` tests)
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml` — all manifest cases passed
- `make verify-diagnostics` — passed
- `make verify-examples` — passed

* Goal:
  Isolate shared compile lifecycle and import/indexing ownership so the
  remaining compiler moves happen behind a stable orchestration boundary.
* Work:
  - move `CompilationSession`, `compile_prompt`, and
    `extract_target_flow_graph` orchestration into
    `doctrine/_compiler/session.py`
  - move `IndexedUnit`, declaration indexing, prompt-root/module-root
    resolution, and import-loading helpers into `doctrine/_compiler/indexing.py`
  - reduce `CompilationContext` to task-local caches/stacks plus delegation
  - keep `doctrine/compiler.py` as a thin top-level façade that imports from
    the internal session module
* Verification (smallest signal):
  - `uv run --locked python -m unittest tests.test_import_loading tests.test_project_config tests.test_verify_corpus`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml`
* Docs/comments (propagation; only if needed):
  - add one short high-leverage comment at the top of `doctrine/compiler.py`
    that real implementation lives under `doctrine._compiler`
  - delete stale comments in `doctrine/compiler.py` that still describe moved
    indexing or session logic as local
* Exit criteria:
  - one shared-session owner exists under `doctrine._compiler.session`
  - one indexing/import owner exists under `doctrine._compiler.indexing`
  - top-level compile entrypoints remain stable and fail loud
* Rollback:
  - restore session and indexing ownership to `doctrine/compiler.py` and remove
    the new internal modules

## Phase 3 — Resolution and compile extraction

Status: COMPLETE

Completed work:

- added `doctrine/_compiler/display.py` and moved the `_render_*` family plus
  related display helpers there behind a dedicated `DisplayMixin` owner
- added `doctrine/_compiler/compile.py` and moved the `_compile_*` family
  there behind a dedicated `CompileMixin` owner
- added `doctrine/_compiler/resolve.py` and moved the `_resolve_*` family plus
  the remaining contract-resolution helper methods there behind a dedicated
  `ResolveMixin` owner
- changed `doctrine/_compiler/context.py` so `CompilationContext` now inherits
  the display, compile, and resolve owners instead of carrying those helper
  families inline

Missing (code):

- none for the planned Phase 3 owner map

Tests run + results:

- `rg -n "^    def _render_|^    def _natural_language_join|^    def _negate_condition_text|^    def _display_law_path_root"`
  across `doctrine/_compiler/context.py` and `doctrine/_compiler/display.py`
  — moved render/display helpers now live only in `display.py`
- `rg -n "^    def _compile_"` across `doctrine/_compiler/context.py` and
  `doctrine/_compiler/compile.py` — moved compile helpers now live only in
  `compile.py`
- `rg -n "^    def (_resolve_|_display_ref|_display_readable_decl|_try_resolve_enum_decl|_expr_ref_matches_review_verdict|_find_readable_decl_matches|_find_addressable_root_matches)"`
  across `doctrine/_compiler/context.py` and `doctrine/_compiler/resolve.py`
  — moved resolution and contract-resolution helpers now live only in
  `resolve.py`
- `python -m py_compile doctrine/_compiler/display.py
  doctrine/_compiler/compile.py doctrine/_compiler/resolve.py
  doctrine/_compiler/context.py doctrine/compiler.py doctrine/_compiler/session.py
  doctrine/_compiler/indexing.py doctrine/_compiler/support.py
  doctrine/_compiler/shared.py` — all compiled cleanly
- `uv run --locked python - <<'PY' ...` mixin import sanity check —
  `CompileMixin`, `DisplayMixin`, and `ResolveMixin` all appeared in
  `CompilationContext.__mro__`
- `uv run --locked python -m unittest tests.test_emit_flow tests.test_import_loading tests.test_project_config tests.test_verify_corpus tests.test_final_output tests.test_review_imported_outputs tests.test_route_output_semantics`
  — `OK` (`33` tests)
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml`
  — all manifest cases passed

* Goal:
  Remove the broadest non-validation algorithmic mass from the compiler
  monolith by giving declaration resolution, readable compilation, and
  final-output construction explicit internal owners.
* Work:
  - move `_resolve_*` and addressable lookup families into
    `doctrine/_compiler/resolve.py`
  - move `_compile_*` families, readable payload builders, contract bucket
    compilation, and final-output construction into `doctrine/_compiler/compile.py`
  - move `_render_*` and related display/text helpers into
    `doctrine/_compiler/display.py`
  - keep `doctrine/_compiler/context.py` as a thin dispatcher over those
    subsystem owners
  - preserve the current public output and final-output behavior exactly
* Verification (smallest signal):
  - `uv run --locked python -m unittest tests.test_final_output tests.test_review_imported_outputs tests.test_route_output_semantics`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml`
* Docs/comments (propagation; only if needed):
  - delete or rewrite stale inline comments in `doctrine/compiler.py` that
    still claim local ownership of moved compile/resolve helpers
* Exit criteria:
  - `_resolve_*`, `_compile_*`, and `_render_*` families no longer live in the
    top-level compiler file
  - final-output, route-output, and review-output behavior stays unchanged
* Rollback:
  - re-inline the moved resolve/compile/display modules into the prior
    compiler file and restore pre-extraction imports

## Phase 4 — Validation and flow extraction

Status: COMPLETE

Completed work:

- added `doctrine/_compiler/validate.py` and moved the `_validate_*`,
  `_review_*`, and `_route_*` families plus their remaining helper methods
  there behind a dedicated `ValidateMixin` owner
- added `doctrine/_compiler/flow.py` and moved `extract_target_flow_graph`,
  `_collect_flow_*`, and `_flow_*` helpers there behind a dedicated
  `FlowMixin` owner
- changed `doctrine/_compiler/context.py` so `CompilationContext` now inherits
  the flow and validate owners alongside the existing Phase 3 mixins, leaving
  only task-local state, public entrypoints, and session delegation in the
  class body

Missing (code):

- none for the planned Phase 4 owner map; validation, review, route, and flow
  helpers no longer live directly in `doctrine/_compiler/context.py`

Tests run + results:

- `rg -n "^    def (_validate_|_review_|_route_|_flow_|extract_target_flow_graph|_collect_flow_)"`
  across `doctrine/_compiler/context.py`, `doctrine/_compiler/validate.py`,
  and `doctrine/_compiler/flow.py` — moved Phase 4 helpers now live only in
  `validate.py` and `flow.py`
- `python -m py_compile doctrine/_compiler/flow.py doctrine/_compiler/validate.py
  doctrine/_compiler/resolve.py doctrine/_compiler/compile.py
  doctrine/_compiler/display.py doctrine/_compiler/context.py doctrine/compiler.py
  doctrine/_compiler/session.py doctrine/_compiler/indexing.py
  doctrine/_compiler/support.py doctrine/_compiler/shared.py` — all compiled
  cleanly
- `uv run --locked python - <<'PY' ...` mixin import sanity check —
  `CompilationContext.__mro__[1] is FlowMixin`,
  `CompilationContext.__mro__[2] is ValidateMixin`,
  `CompilationContext.__mro__[3] is CompileMixin`,
  `CompilationContext.__mro__[4] is DisplayMixin`, and
  `CompilationContext.__mro__[5] is ResolveMixin` all returned `True`
- `uv run --locked python -m unittest tests.test_emit_flow tests.test_import_loading tests.test_project_config tests.test_verify_corpus tests.test_final_output tests.test_review_imported_outputs tests.test_route_output_semantics`
  — `OK` (`33` tests)
- `make verify-diagnostics` — passed
- `make verify-examples` — passed

* Goal:
  Give compile-time invariants and flow extraction one canonical owner each,
  while keeping emit and diagnostic surfaces honest.
* Work:
  - move `_validate_*`, `_review_*`, and `_route_*` families into
    `doctrine/_compiler/validate.py`
  - move flow graph extraction and flow helper logic into
    `doctrine/_compiler/flow.py`
  - keep `emit_flow.py` on the stable top-level compile API while
    `flow_renderer.py` reads shared types from `doctrine._compiler.types`
  - preserve diagnostic trace wrapping and fail-loud behavior at the session
    boundary
* Verification (smallest signal):
  - `uv run --locked python -m unittest tests.test_emit_flow tests.test_route_output_semantics tests.test_import_loading`
  - `make verify-diagnostics`
* Docs/comments (propagation; only if needed):
  - remove stale comments that describe validation or flow ownership as still
    local to `doctrine/compiler.py`
* Exit criteria:
  - validation and flow helpers no longer live in the top-level compiler file
  - emit-flow, route semantics, import failure behavior, and diagnostics still
    behave the same
* Rollback:
  - restore validation and flow helpers to `doctrine/compiler.py` and revert
    internal module imports

## Phase 5 — Compiler façade cleanup and full proof

Status: COMPLETE

Completed work:

- kept `doctrine/compiler.py` as the thin public facade while the internal
  owner map finished under `doctrine._compiler`
- confirmed the internal owner layout now spans `types.py`, `support.py`,
  `session.py`, `indexing.py`, `display.py`, `compile.py`, `resolve.py`,
  `validate.py`, and `flow.py`
- rewrote the surviving `doctrine/_compiler/context.py` boundary comment so it
  now describes the finished thin-context owner map instead of an in-progress
  extraction
- reran the full shipped proof surface after the final owner cuts

Missing (code):

- none; the surviving boundary comments now match the final owner map

Tests run + results:

- `make verify-diagnostics` — passed
- `make verify-examples` — passed

* Goal:
  Finish the cutover by removing residual monolith pressure from
  `doctrine/compiler.py`, leaving one thin public boundary plus full proof that
  shipped behavior held.
* Work:
  - delete any remaining moved helper implementations from
    `doctrine/compiler.py`
  - confirm top-level operator modules still import only the intended stable
    boundaries
  - keep `parser.py`, `model.py`, and `diagnostics.py` unchanged except for any
    import repairs proven necessary by the earlier phases
  - reconcile boundary comments so the surviving source explains the final
    ownership truth
* Verification (smallest signal):
  - `make verify-examples`
  - `make verify-diagnostics`
* Docs/comments (propagation; only if needed):
  - keep only the surviving boundary comments in `doctrine/compiler.py` and
    `doctrine/_compiler/__init__.py`; delete stale migration-era comments
* Exit criteria:
  - `doctrine/compiler.py` reads like a thin public façade
  - no duplicate old/new compiler implementation path remains live
  - full shipped proof passes
* Rollback:
  - revert the façade cleanup commit range and restore the last passing
    pre-cleanup compiler boundary
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Prefer targeted tests around extracted owner boundaries only when existing
  tests stop proving preservation.
- Keep tests behavior-focused: compilation session behavior, route and review
  semantics, final-output handling, import loading, and emitted output
  rendering matter more than file-shape assertions.

## 8.2 Integration tests (flows)

- `make verify-examples` is the primary preservation signal for shipped
  semantics.
- During inner-loop work, targeted manifest verification can prove a seam
  cheaply before rerunning the full corpus.

## 8.3 E2E / device tests (realistic)

- Not applicable in the device sense. This repo's realistic end-to-end surface
  is compile, render, diagnostics, and manifest-backed corpus verification.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Ship the modularization as an internal refactor behind the same user-facing
  commands and documented workflows, unless a later stage explicitly approves a
  public boundary change.

## 9.2 Telemetry changes

- None planned. This repo does not currently need new telemetry to modularize
  the shipped Python core safely.

## 9.3 Operational runbook

- Keep the work depth-first and bisectable: each extraction should have one
  clear owner change, one preservation signal, and one obvious rollback point.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: self cold-read pass 1, self cold-read pass 2, self-integrator
- Scope checked:
  - frontmatter, `# TL;DR`, Sections `0` through `10`, and helper-block drift
- Findings summary:
  - the planning-pass block still implied an external-research step even though Section `3.1` explicitly rejected it for this doc
  - the future on-disk structure omitted `model.py` even though Sections `3`, `5`, and `7` all keep it as a first-wave stable owner
  - the target architecture introduced `doctrine._compiler.display` but the call-site audit and phase plan did not yet schedule that extraction
- Integrated repairs:
  - updated `planning_passes` so the block matches the actual auto-plan path and now points at `implement`
  - restored `model.py` to the target file tree in Section `5.1`
  - added the display-subsystem migration to the call-site audit and Phase `3`
  - normalized the `_compiler/types.py` file-path reference in migration notes
- Remaining inconsistencies:
  - none
- Unresolved decisions:
  - none
- Unauthorized scope cuts:
  - none
- Decision-complete:
  - yes
- Decision: proceed to implement? yes
<!-- arch_skill:block:consistency_pass:end -->

# 10) Decision Log (append-only)

## 2026-04-12 - Treat modularization as semantics-preserving architecture work

Context

- The user asked for a full-arch plan to modularize the codebase because the
  shipped core files feel monolithic and inelegant.

Options

- Pursue a large semantics rewrite and let modularization happen as fallout.
- Treat this as a semantics-preserving architecture refactor focused on owner
  paths, package layout, and extraction order.

Decision

- Treat the work as a semantics-preserving modularization of the shipped
  `doctrine/` core, with `doctrine/compiler.py` as the highest-pressure
  boundary problem and the other large core files requiring explicit
  disposition in the same plan.

Consequences

- The plan will optimize for beautiful boundaries, explicit ownership, and
  easier safe change, not for new language capability.
- Proof surfaces such as `make verify-examples` and targeted tests become part
  of the architecture contract, not optional cleanup.

Follow-ups

- Use `research` to ground the real owner-path seams and public-boundary
  constraints before committing to a target package map.

## 2026-04-12 - Preserve top-level boundaries and split internals under `doctrine._compiler`

Context

- Research confirmed that the repo's public compile story already runs through
  top-level modules, especially `doctrine.compiler`, while the real ownership
  problem is the compiler monolith and its role as a shared type bucket.

Options

- Split public imports and force most operator surfaces onto new top-level
  modules immediately.
- Keep top-level boundaries stable, and move the real subsystem ownership into
  one internal compiler package.
- Treat every large core file as equally urgent and split parser/model/
  diagnostics in the first implementation wave too.

Decision

- Keep the current top-level operator modules as the stable public surface.
- Move real compiler ownership into `doctrine._compiler`.
- Put `Compiled*` and `Flow*` dataclasses in `doctrine._compiler.types`.
- Keep `parser.py`, `model.py`, and `diagnostics.py` as explicit first-wave
  stable owners unless implementation exposes a concrete required split.

Consequences

- The implementation can delete real compiler monolith pressure without a
  public import migration at the same time.
- Packaging changes are mandatory in the same pass because the build must ship
  `doctrine._compiler`.
- Renderer and flow-renderer imports must move off the compiler facade so the
  new type owner is honest.

Follow-ups

- Deep-dive pass 2 should harden the internal module boundaries against
  overbuild and confirm that the call-site audit is complete enough for
  `phase-plan`.

## 2026-04-12 - Keep `doctrine._compiler` private and use package discovery

Context

- Deep-dive pass 1 fixed the main architecture direction, but phase planning
  would still have been forced to choose the exact packaging posture and the
  import policy for the new internal package.

Options

- Keep explicit `packages = ["doctrine"]` and hand-maintain package lists as
  the internal package grows.
- Switch to package discovery for `doctrine*`, keep `_compiler` private, and
  route top-level operator usage through stable public modules.
- Move operator surfaces and tests to direct `_compiler` imports as part of the
  first wave.

Decision

- Use setuptools package discovery for `doctrine*`.
- Keep `doctrine._compiler` intentionally private to the package.
- Allow direct `_compiler` imports only inside `doctrine._compiler` itself and
  for the two canonical type consumers: `renderer.py` and `flow_renderer.py`.
- Keep other top-level operator modules on the stable public boundaries.

Consequences

- Packaging will no longer be a hidden blocker as internal modules are added.
- The refactor avoids turning `_compiler` into a second public sprawl surface.
- Renderer and flow-renderer can depend on the honest type owner without
  leaving the rest of the operator surface coupled to internals.

Follow-ups

- `phase-plan` should sequence packaging discovery before any extraction that
  creates files under `doctrine/_compiler/`.

## 2026-04-12 - Move `ResolvedRenderProfile` with the shared compiler type cut

Context

- Phase 1 implementation confirmed that `doctrine/renderer.py` still imported
  `ResolvedRenderProfile` from `doctrine.compiler`, so moving only `Compiled*`
  and `Flow*` would have left the top-level compiler as a residual type bucket.

Options

- Leave `ResolvedRenderProfile` in `doctrine.compiler` and accept that the
  public facade still owns part of the renderer type contract.
- Move `ResolvedRenderProfile` into `doctrine._compiler.types` with the rest of
  the shared render-facing contracts.

Decision

- Move `ResolvedRenderProfile` into `doctrine._compiler.types` as part of Phase
  1.

Consequences

- `doctrine/renderer.py` now depends on the honest internal type owner for its
  full shared render contract.
- Later compiler extractions no longer need to preserve a special
  render-profile exception in the top-level facade.

Follow-ups

- Keep later `_compiler` extractions routing shared compiled-data contracts
  through `doctrine._compiler.types` instead of recreating another compiler-side
  bucket.
