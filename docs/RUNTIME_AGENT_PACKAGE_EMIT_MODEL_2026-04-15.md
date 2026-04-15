---
title: "Doctrine - Runtime Agent Package Emit Model - Architecture Plan"
date: 2026-04-15
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - docs/EMIT_GUIDE.md
  - docs/SKILL_PACKAGE_AUTHORING.md
  - docs/WHY_DOCTRINE.md
  - docs/LANGUAGE_REFERENCE.md
  - ../doctrine2/docs/LANGUAGE_REDESIGN_SPEC.md
  - ../doctrine2/docs/LANGUAGE_REDESIGN_EXT_SPEC.md
  - examples/100_skill_package_bundled_agents/prompts/SKILL.prompt
  - ../rally/stdlib/rally/prompts/rally/base_agent.prompt
  - ../rally/stdlib/rally/prompts/rally/memory.prompt
  - ../rally/stdlib/rally/prompts/rally/turn_results.prompt
---

# TL;DR

## Outcome

Doctrine should gain a first-class runtime agent package model. One local
package directory should be able to own one real concrete routeable agent, its
optional `SOUL.prompt`, and its peer files, while one thin flow-facing build
handle still builds the whole flow. The emitted output should already be in the
stable per-agent package shape a runtime such as Rally can consume directly.

## Problem

Today Doctrine can emit concrete root agents from `AGENTS.prompt` and
`SOUL.prompt`, and it can emit real source-root bundles from `SKILL.prompt`.
But it does not have the matching package surface for runtime agents. That
pushes multi-agent flows toward one large wrapper file that duplicates local
agent truth, plus fake concrete naming stubs so routes and owners can point at
something explicit.

## Approach

Generalize the clean parts of the shipped `skill package` model into a new
runtime agent package surface, not a Rally-specific emit workaround. Keep one
explicit composition root for the flow. Let local agent packages expose real
agent identities that routes and owners can target directly. Reuse the current
prompts-root-aware emit pipeline and source-root package rules where they fit,
but do not add filesystem discovery magic or a second long-term emission path.
Keep the design headed toward the future package and export direction already
implied by `../doctrine2/docs/LANGUAGE_REDESIGN_EXT_SPEC.md`, without pulling
the whole redesign package into scope now.

## Plan

1. Teach import loading to resolve file modules and directory-backed runtime
   packages with fail-loud collisions.
2. Extract one shared ordinary-file package-layout helper without changing
   shipped `SKILL.prompt` behavior.
3. Land one shared runtime frontier and unit-aware compile path for imported
   package-owned agents before caller adoption.
4. Move `emit_docs` and `emit_flow` onto that shared frontier and emit real
   package-backed runtime trees.
5. Move corpus proof, smoke proof, and one generic example onto the new
   runtime package story.
6. Rewrite live docs and release truth so public guidance matches the shipped
   surface and release classification.
7. Run the full repo proof sweep after code, examples, diagnostics, and docs
   all agree.

## Non-negotiables

- Rally is the use case we must satisfy, not the architecture we must copy.
- The new surface must feel native to Doctrine, not like a side-emission hack.
- One explicit flow-facing build handle should remain. No directory scanning.
- No fake concrete agent stubs just to give routes or owners a name.
- No long-term duplicate truth between a flow wrapper and local agent homes.
- No runtime shims or compatibility layers that keep two competing package
  models alive.
- The chosen direction must stay compatible with the forward package and export
  story already sketched in `../doctrine2` redesign docs.
- This plan must not expand into the whole `../doctrine2` redesign package.
- The emitted package layout must be stable enough that a runtime can consume
  it directly.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-15
Verdict (code): NOT COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- The implementation stops after Phase 4. The approved ordered frontier still
  includes Phase 5, Phase 6, and Phase 7, and `DOC_PATH` does not authorize
  cutting that work.
- I did not find an execution-side rewrite in `DOC_PATH` that weakens the
  approved requirements or acceptance bar. The failure is unfinished frontier
  work, not a narrowed plan.

## Reopened phases (false-complete fixes)
- Phase 5 (Move corpus proof, smoke proof, and one generic example onto the
  new path) — reopened because:
  - the proof runner and smoke checks still follow the old runtime story
  - no generic runtime-package example target or checked-in build proof exists
- Phase 6 (Rewrite live public docs and release truth) — reopened because:
  - the touched live docs and release surfaces still teach the old
    entrypoint-only runtime story
- Phase 7 (Run the full repo proof set and clean final drift) — reopened
  because:
  - the required repo-wide proof sweep is not evidenced
  - the touched live truth still drifts from the approved runtime-package
    story

## Missing items (code gaps; evidence-anchored; no tables)
- Phase 5 proof frontier is still missing.
  - Evidence anchors:
    - `doctrine/_verify_corpus/runners.py:323`
    - `doctrine/_diagnostic_smoke/emit_checks.py:17`
    - `doctrine/_diagnostic_smoke/flow_emit_checks.py:13`
    - `tests/test_verify_corpus.py:65`
    - `pyproject.toml:40`
    - `docs/RUNTIME_AGENT_PACKAGE_EMIT_MODEL_2026-04-15_WORKLOG.md:24`
  - Plan expects:
    - build-contract proof, smoke proof, corpus tests, and one generic
      manifest-backed runtime-package example on the canonical runtime path
  - Code reality:
    - build-contract proof still branches only on `SKILL.prompt` versus other
      entrypoints, smoke checks do not add any runtime-package cases, corpus
      tests still anchor only the old flow example, the emit target list has
      no runtime-package example target, and the worklog says Phase 5 and
      later did not start
  - Fix:
    - finish Phase 5 exactly as written: add the generic example plus checked-
      in `build_ref/`, extend corpus and smoke proof to package-backed runtime
      output, and add runtime-package corpus coverage
- Phase 6 public truth is still missing.
  - Evidence anchors:
    - `docs/EMIT_GUIDE.md:6`
    - `docs/EMIT_GUIDE.md:78`
    - `docs/LANGUAGE_REFERENCE.md:41`
    - `docs/SKILL_PACKAGE_AUTHORING.md:16`
    - `examples/README.md:35`
    - `examples/README.md:86`
    - `examples/README.md:251`
    - `docs/VERSIONING.md:50`
    - `CHANGELOG.md:24`
  - Plan expects:
    - live docs, example guidance, and release truth must teach runtime
      packages, the file-module versus directory-backed import rule, the thin
      build-handle example, and the additive release classification
  - Code reality:
    - `EMIT_GUIDE` still teaches entrypoint-root runtime emit, `LANGUAGE_REFERENCE`
      still names only `AGENTS.prompt` and `SOUL.prompt` as the runtime
      entrypoints, `SKILL_PACKAGE_AUTHORING` still only frames `SKILL.prompt`
      package trees, `examples/README.md` still treats `95` through `106` as
      the package story and still mentions companion contract JSON, and
      `VERSIONING` plus `CHANGELOG` do not describe the new runtime-package
      surface at all
  - Fix:
    - land Phase 6 as written and remove the stale pre-package runtime story
      from the touched live docs
- Phase 7 final proof and drift cleanup are still missing.
  - Evidence anchors:
    - `docs/RUNTIME_AGENT_PACKAGE_EMIT_MODEL_2026-04-15_WORKLOG.md:19`
    - `docs/RUNTIME_AGENT_PACKAGE_EMIT_MODEL_2026-04-15_WORKLOG.md:24`
    - `docs/RUNTIME_AGENT_PACKAGE_EMIT_MODEL_2026-04-15.md:1271`
  - Plan expects:
    - run `uv sync`, `npm ci`, `make verify-examples`, `make verify-diagnostics`,
      and `make verify-package`, then fix the last drift they expose
  - Code reality:
    - the worklog only records the Phase 1-4 targeted unit tests, Phase 5 and
      later are explicitly unstarted, and the touched live docs and examples
      still contradict the approved runtime-package story, so the final repo
      sweep cannot be treated as complete
  - Fix:
    - after Phase 5 and Phase 6 land, run the full required repo proof set and
      record the real results

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-15
external_research_grounding: not needed
deep_dive_pass_2: done 2026-04-15
recommended_flow: implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

Doctrine can support a first-class runtime agent package model that lets one
local directory be the real source of truth for one concrete runtime agent and
its peer prompt files, while one explicit flow-facing build handle still builds
the whole flow, routes and owners point at real imported agent identities
instead of fake stubs, and emitted output lands in a stable per-agent package
tree that a runtime can consume without redoing the compiler's job. The design
should move Doctrine toward the future package and export direction already
implied by the `../doctrine2` redesign docs, but it should do so as a narrow
compatible step rather than by trying to land the whole redesign now.

This claim is false if any of these remain true after implementation:

- a multi-agent flow still needs a large behavior-owning wrapper just to emit
  the real agent homes
- routes or owners still need naming-only concrete stubs
- local agent directories still cannot be the real authored source of truth for
  one concrete runtime agent
- Doctrine solves the use case with Rally-specific side emission, wrapper
  manifests, or filesystem discovery instead of a first-class language and
  compiler surface
- the feature lands on a packaging or naming model that fights the future
  package barrel and export direction already sketched in `../doctrine2`
- the emitted tree is still missing peer files the runtime needs beside the
  compiled agent markdown
- the implementation only works by landing large unrelated parts of the full
  `../doctrine2` redesign package first
- the final design leaves two long-term package or emit stories alive

## 0.2 In scope

- A Doctrine-native runtime-agent package model and identity story.
- A local package directory that can own:
  - one concrete routeable runtime agent
  - local `AGENTS.prompt`
  - optional local `SOUL.prompt`
  - ordinary bundled peer files that should emit beside the compiled markdown
- A thin explicit flow-facing composition handle that can still build the whole
  flow through one normal entrypoint.
- Clean route-target and owner-target semantics for imported real agent
  identities.
- Emitted per-agent package trees that are stable enough for runtime
  consumption.
- Generalization from current Doctrine package and emit patterns where that
  keeps the design smaller and cleaner.
- Generic examples and docs that prove the Doctrine feature without importing
  Rally jargon into public surfaces.
- Rally-shaped proof during planning and later implementation review, because
  that is the live use case we must satisfy.
- A forward-compatible step toward the package and export direction already
  implied by the `../doctrine2` redesign docs.

Allowed architectural convergence scope:

- Widen parser, model, indexing, resolve, emit, and example work as needed to
  give the feature one canonical owner path.
- Refactor current emit code if that is what it takes to avoid parallel package
  paths.
- Reuse or generalize `skill package` and prompts-root-aware emit plumbing
  where it truly fits.

Compatibility posture for this change:

- Preserve current local-root runtime emit from `AGENTS.prompt`.
- Preserve direct `SOUL.prompt` entrypoints.
- Preserve current file-module imports.
- Add directory-backed runtime packages as a new explicit path.
- Do not add a bridge, shim, or discovery scan.

## 0.3 Out of scope

- Rally-specific runtime logic, adapter rules, or filesystem layouts as public
  Doctrine features.
- Filesystem auto-discovery of agent homes.
- A second target registry, wrapper manifest, or side-emission system owned by
  Rally.
- Landing the whole `../doctrine2` redesign package, including unrelated
  language cleanup that is not required to support runtime agent packaging.
- A generic package manager for all Doctrine assets.
- New route semantics beyond what is needed to let routes point at real
  package-owned agent identities.
- Silent compatibility shims that keep the old and new authoring models alive
  together as equal public paths.

## 0.4 Definition of done (acceptance evidence)

- Doctrine has one clear runtime agent package story that a new user can read
  in docs and examples without learning Rally internals.
- A generic example flow proves:
  - local agent package source ownership
  - one thin flow-facing composition root
  - clean route or owner references to real imported package identities
  - emitted per-agent package trees with peer files beside compiled markdown
- The implementation reuses or cleanly generalizes current emit/package code
  instead of cloning it into a second parallel path.
- The emitted output for the generic example is stable and readable.
- The design also satisfies the Rally use case:
  - no giant behavior-owning wrapper
  - no naming-only concrete stubs
  - no Rally-owned `SOUL` side-emission path
- Credible proof runs for parser, compile, emit, and corpus surfaces touched by
  the change.

## 0.5 Key invariants (fix immediately if violated)

- One explicit composition root remains. No discovery magic.
- One local runtime agent package owns one concrete routeable agent.
- Local package ownership is the source of truth for that agent's behavior.
- Routes and owners must point at real imported agent identities, not fake
  local stubs.
- Emit must have one canonical runtime-agent package path.
- No dual sources of truth between local package homes and a flow wrapper.
- No runtime shims or fallback package layouts.
- The local implementation step must not dead-end against the future package
  barrel and export direction from `../doctrine2`.
- Fail loudly on ambiguous package ownership, identity collisions, or emitted
  path collisions.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Local authored ownership should be real, not decorative.
2. The feature should reuse Doctrine's existing package and emit patterns where
   that keeps the design canonical.
3. Flow composition should stay explicit and easy to review.
4. Route and owner targeting should stay fail-loud and concrete.
5. The emitted tree should be stable enough for runtimes to consume directly.

## 1.2 Constraints

- Doctrine already has a source-root package model for `SKILL.prompt`.
- Doctrine already has prompts-root-aware emit rules for `AGENTS.prompt` and
  `SOUL.prompt`.
- `../doctrine2` already sketches a future package-barrel and export direction,
  but it does not yet specify the runtime agent package emit model itself.
- The new surface cannot depend on Rally internals.
- The public docs and example stack must stay generic.
- The current flow and route semantics should not drift while package ownership
  gets cleaner.

## 1.3 Architectural principles (rules we will enforce)

- Prefer explicit packages and explicit agent identity over implicit discovery.
- Prefer one canonical emit path over wrappers plus side-emission helpers.
- Reuse the closest shipped Doctrine pattern before inventing a new one.
- Move toward the future `../doctrine2` package and export direction where that
  path is clear, but do not import unrelated redesign scope.
- Keep ownership and route targets explicit in the authored graph.
- Delete superseded public stories instead of preserving them as parallel paths.

## 1.4 Known tradeoffs (explicit)

- Keeping one explicit composition root is slightly less magical than full
  discovery, but it fits Doctrine better and keeps failure modes honest.
- A one-agent-per-package default is more narrow than a free-form package, but
  it gives routes, owners, and emitted layout one clean identity model.
- Generalizing the current skill-package path may require deeper refactor work
  than a local emit shortcut, but it is the more canonical long-term design.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine has two relevant shipped surfaces today:

- `emit_docs` compiles concrete root agents from `AGENTS.prompt` or
  `SOUL.prompt` and emits per-agent Markdown under the entrypoint's path
  beneath `prompts/`.
- `emit_docs` only emits concrete agents declared in the entrypoint file
  itself. Imported agents can be referenced, but they do not emit as
  package-owned runtime roots today.
- `emit_skill` compiles `SKILL.prompt` into a real source-root package tree
  with `SKILL.md`, bundled ordinary files, and bundled agent companions.

Doctrine does not yet have the matching first-class package surface for runtime
agents. In practice, that means local agent directories can exist as source
organization and imported identity surfaces, but the emitted runtime tree still
wants entrypoint-owned concrete agents rather than package-owned runtime homes.

## 2.2 What’s broken / missing (concrete)

- A multi-agent flow can end up with one large wrapper file that mostly repeats
  real agent ownership already present in local homes.
- Routes and owners can need naming-only concrete stubs so the authored graph
  has something explicit to point at.
- A local runtime agent home cannot yet be the full package source of truth in
  the same clean way `SKILL.prompt` can for skill packages.
- Runtime consumers that want a stable per-agent package tree feel pressure to
  recreate part of Doctrine's job outside Doctrine.

## 2.3 Constraints implied by the problem

- The solution needs an explicit authored composition story, not discovery.
- It needs real import and identity semantics for routeable agents.
- It needs a stable emitted package tree, not just nicer source layout.
- It should converge with existing package and emit code instead of creating a
  runtime-only fork of the model.

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- `../doctrine2/docs/LANGUAGE_REDESIGN_EXT_SPEC.md` — adopt as the forward
  naming anchor for module exports and package barrels, but do not import that
  whole surface now. It shows the direction this feature should not fight.
- `../doctrine2/docs/LANGUAGE_REDESIGN_SPEC.md` — adopt as the broader redesign
  boundary, but reject landing unrelated redesign work in this plan. This
  change should stay narrow.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/emit_docs.py` — runtime emit writes Markdown only and emits only
    concrete root agents declared in the entrypoint prompt file.
  - `doctrine/emit_common.py` — shared target loading, prompts-root output
    layout, and `root_concrete_agents()` entrypoint-root selection.
  - `doctrine/emit_skill.py` — current source-root package emit path for
    `SKILL.prompt`.
  - `doctrine/_compiler/compile/skill_package.py` — bundled file copy-through,
    bundled `agents/**/*.prompt` compilation, and fail-loud path collision
    checks.
  - `doctrine/_compiler/session.py` and `doctrine/_compiler/context.py` —
    today the compiler has separate public compile entrypoints for runtime
    agents and skill packages.
  - `doctrine/grammars/doctrine.lark`, `doctrine/_parser/skills.py`,
    `doctrine/_model/io.py`, and `doctrine/_compiler/indexing.py` — Doctrine
    ships `skill package`, but it does not ship runtime-agent packages,
    `export`, or `package` declarations yet.
  - `doctrine/_compiler/resolve/refs.py`,
    `doctrine/_compiler/resolve/agent_slots.py`, and
    `doctrine/_compiler/validate/routes.py` — imported dotted agent refs
    already work for inheritance, workflow slots, and route targets, and route
    targets already fail loud unless they point at concrete agents.
- Canonical path / owner to reuse:
  - `doctrine/emit_common.py`, `doctrine/emit_docs.py`, and
    `doctrine/emit_skill.py` — keep one shared prompts-root-aware emit
    pipeline. Do not add a third long-term emitter for runtime agent packages.
  - `doctrine/_compiler/compile/skill_package.py` — reuse this source-root
    bundle logic instead of cloning it for runtime agents.
  - `doctrine/_compiler/resolve/refs.py` and
    `doctrine/_compiler/validate/routes.py` — keep imported concrete-agent
    identity and route honesty on the existing fail-loud path.
- Adjacent surfaces tied to the same contract family:
  - `doctrine/_verify_corpus/runners.py` — corpus proof still branches on
    `SKILL.prompt` versus non-`SKILL.prompt` entrypoints today.
  - `doctrine/_diagnostic_smoke/emit_checks.py` — emit smoke proof for the
    current emit split and source-root package rules.
  - `docs/EMIT_GUIDE.md`, `docs/SKILL_PACKAGE_AUTHORING.md`,
    `docs/LANGUAGE_REFERENCE.md`, and `examples/README.md` — public docs that
    must move with the final package story.
  - `examples/04_inheritance/prompts/AGENTS.prompt`,
    `examples/17_agent_mentions/prompts/AGENTS.prompt`, and
    `examples/70_route_only_declaration/prompts/IMPORTED_ROUTE_TITLES.prompt`
    — existing proof that imported dotted agent refs already work for
    inheritance, mentions, and routes.
  - `../rally/stdlib/rally/prompts/rally/base_agent.prompt` and
    `../rally/stdlib/rally/prompts/rally/memory.prompt` — real consumer-style
    agent-home surfaces the new package story should satisfy without copying
    Rally jargon into Doctrine docs.
- Compatibility posture (separate from `fallback_policy`):
  - preserve the existing contract — current `emit_docs` and `emit_skill`
    entrypoints stay valid, and the new runtime-agent package story should be
    additive, fail loud on ambiguity, and avoid any bridge or Rally-only shim.
- Existing patterns to reuse:
  - `tests/test_emit_skill.py` and
    `examples/100_skill_package_bundled_agents/prompts/SKILL.prompt` —
    source-root package trees that keep compiled agent companions and raw
    runtime metadata side by side under `agents/`.
  - `docs/LANGUAGE_REFERENCE.md` imports section and
    `tests/test_import_loading.py` — current module import and dotted-ref
    behavior, including fail-loud missing and cyclic import handling.
- Prompt surfaces / agent contract to reuse:
  - `docs/LANGUAGE_REFERENCE.md` — imported symbols are used through dotted
    declaration refs such as `shared.roles.AcceptanceCritic`.
  - `../rally/stdlib/rally/prompts/rally/base_agent.prompt` — current shared
    base-agent contract shape Rally wants to keep.
- Native model or agent capabilities to lean on:
  - not agent-backed runtime behavior — this is parser, model, resolve, and
    emit work, so the right move is compiler convergence, not wrappers or
    support tooling.
- Existing grounding / tool / file exposure:
  - named emit targets in `pyproject.toml` through `load_emit_targets()`
  - entrypoint-local `prompts/` roots plus optional additional prompt roots
  - checked-in `build_ref/` trees and manifest-backed corpus cases
- Duplicate or drifting paths relevant to this change:
  - this doc itself still said `emit_docs` emitted contract sidecars, but
    current code and `tests/test_emit_docs.py` say Markdown only.
  - `emit_docs` owns runtime-agent emission while `emit_skill` owns source-root
    package bundling. A runtime-agent package design that adds a third emitter
    would create parallel truth.
  - `docs/EMIT_GUIDE.md` and `examples/README.md` still contain older wording
    about emitted companion contract files even though `emit_docs` is now
    Markdown only.
- Capability-first opportunities before new tooling:
  - generalize the current compiler and emit paths. Do not add discovery
    scripts, wrapper manifests, or runtime post-process steps.
- Behavior-preservation signals already available:
  - `tests/test_emit_docs.py` — runtime emit proof
  - `tests/test_emit_skill.py` — source-root package proof
  - `tests/test_import_loading.py` — imported module behavior and fail-loud
    cycle handling
  - `doctrine/_diagnostic_smoke/emit_checks.py` — emit smoke proof
  - `make verify-examples` — manifest-backed end-to-end emitted proof

## 3.3 Decision gaps that must be resolved before implementation

Decisions locked by this pass:

- Runtime agent packages should stay on the existing runtime emit path, not on
  a new third emitter.
  - Current repo truth:
    - `emit_docs` already owns runtime-agent emission and `emit_skill` already
      owns source-root package bundling.
  - Locked decision:
    - reuse or generalize those two existing paths so runtime-agent packages
      ride the runtime emitter story. Do not add a new sibling emitter just for
      this feature.
  - Why:
    - a third emitter would create parallel truth and fight the plan's one-path
      goal.
- The first shipped import story for package-owned runtime agents should reuse
  current module imports and dotted agent refs.
  - Current repo truth:
    - Doctrine already supports imported dotted agent refs for inheritance,
      mentions, workflow slots, and route targets, but it does not ship
      selective imports or package barrels yet.
  - Locked decision:
    - deep-dive should treat module imports plus dotted refs as the base v1
      composition story. Any future barrel or export syntax stays a
      forward-compatibility concern, not a prerequisite for this feature.
  - Why:
    - this keeps the first step small, fits shipped behavior, and still leaves
      room for the redesign's later export model.
- Compatibility posture is additive, with no bridge.
  - Current repo truth:
    - existing `AGENTS.prompt` / `SOUL.prompt` and `SKILL.prompt` flows are
      live shipped surfaces with proof and docs.
  - Locked decision:
    - keep those surfaces valid, add the new runtime-agent package path without
      shims, and fail loud on ambiguous package ownership or path collisions.
  - Why:
    - this preserves shipped behavior while avoiding a half-migrated bridge
      story.

Deep-dive pass 2 closes the remaining design choices:

- The shared runtime frontier is the full explicit import-graph closure loaded
  from the entrypoint:
  - keep local concrete agents declared in the entrypoint itself
  - add each directory-backed runtime package unit the loader first reaches
  - preserve first-seen order
  - never use filesystem discovery
  - never require the build handle to repeat direct imports already carried by
    imported flow modules
- Optional sibling `SOUL.prompt` is valid only when:
  - it defines exactly one concrete agent
  - that concrete agent has the same name as the package-owned concrete agent
    in sibling `AGENTS.prompt`
  - any extra local helpers stay non-concrete
- The shared package-layout helper boundary is narrow:
  - share only source-root path normalization, ordinary-file enumeration,
    case-collision checks, and compiler-owned output collision checks
  - keep runtime-package prompt rules in the runtime emit path
  - keep skill-package prompt subtree rules in the skill-package compiler
- External research is not needed for this plan:
  - the repo already has enough shipped truth to settle the design
  - the remaining work is internal convergence and proof planning
- The first public proof example should teach one generic story:
  - a thin build handle
  - two imported runtime packages
  - one bundled peer file
  - one optional sibling `SOUL.prompt`
  - one route or owner ref to a real imported agent identity
  - no `SKILL.prompt` in the same example
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/emit_common.py` owns the shared emit target contract and the
  current `root_concrete_agents()` helper.
- `doctrine/emit_docs.py` owns runtime Markdown emission for `AGENTS.prompt`
  and `SOUL.prompt`.
- `doctrine/emit_flow.py` owns `.flow.d2` and `.flow.svg` emission from the
  same entrypoint family.
- `doctrine/emit_skill.py` owns `SKILL.prompt` package emission.
- `doctrine/_compiler/compile/skill_package.py` owns the only shipped
  source-root package planner in the repo today. It copies ordinary bundled
  files, compiles bundled `agents/**/*.prompt`, and rejects path collisions.
- `doctrine/_compiler/session.py` and `doctrine/_compiler/context.py` still
  treat root-agent compile as a root-unit operation. Public compile entrypoints
  compile local root agents by name or compile one skill package by name.
- `doctrine/_compiler/indexing.py` still treats imports as file modules. A
  dotted import resolves to `<module>.prompt` under one prompts root.
- `doctrine/_compiler/resolve/refs.py`,
  `doctrine/_compiler/resolve/section_bodies.py`, and
  `doctrine/_compiler/validate/routes.py` already resolve imported dotted agent
  refs and already require route targets to be concrete agents.
- `doctrine/_verify_corpus/runners.py` and
  `doctrine/_diagnostic_smoke/emit_checks.py` mirror the current emitter split:
  runtime docs on one side, skill packages on the other.

## 4.2 Control paths (runtime)

Today the runtime emit path is entrypoint-local:

1. `emit_docs.py` parses the target entrypoint.
2. `emit_common.root_concrete_agents()` scans only that parsed file and returns
   local non-abstract agent names in authored order.
3. `CompilationSession(prompt_file).compile_agents(agent_names)` compiles only
   those root-unit agent names.
4. `emit_docs.py` writes one `AGENTS.md` or `SOUL.md` per emitted agent under
   the entrypoint-relative path.

The flow emitter uses the same root rule:

1. `emit_flow.py` parses the entrypoint.
2. It calls the same `root_concrete_agents()` helper.
3. `CompilationSession.extract_target_flow_graph(agent_names)` roots the graph
   at those local concrete agents.
4. Once rooted, the flow walker can already follow imported route targets and
   imported workflow refs. Imported agents can appear in the graph as routed
   nodes, but they are not selected as emitted roots.

The skill-package path is different:

1. `emit_skill.py` parses one `SKILL.prompt`.
2. `CompilationSession.compile_skill_package()` compiles one top-level skill
   package from the root unit.
3. `compile/skill_package.py` treats the directory that contains `SKILL.prompt`
   as the package source root.
4. It writes `SKILL.md`, bundles ordinary files byte for byte, compiles bundled
   `agents/**/*.prompt`, and rejects path collisions or reserved prompt trees.

Imports are still file-backed only:

- `indexing._module_path_for_root()` resolves a dotted import to
  `<module>.prompt`.
- `load_module()` and `resolve_module_root()` search the current prompts root
  plus any configured `additional_prompt_roots`.
- There is no shipped way to import a directory-backed runtime package rooted by
  `AGENTS.prompt`.

## 4.3 Object model + key abstractions

- `PromptFile` and `IndexedUnit` model prompt files and their loaded imports,
  but they do not record a module kind such as file module versus runtime
  package.
- `EmitTarget.entrypoint` is still just a file path. The shared helper surface
  knows only three entrypoint names:
  - `AGENTS.prompt`
  - `SOUL.prompt`
  - `SKILL.prompt`
- `root_concrete_agents()` is the current runtime frontier selector. It has no
  notion of imported runtime packages, package roots, or package-owned peer
  files.
- `CompilationSession.compile_agent()` and `CompilationContext.compile_agent()`
  compile only `root_unit.agents_by_name`.
- `CompilationSession.extract_target_flow_graph()` also starts from local root
  agent names only.
- `compile/skill_package.py` is the only place that already has:
  - source-root file bundling
  - case-collision checks
  - reserved compiler-owned output paths
  - prompt-versus-ordinary-file rules
- Imported agent identity is already real for refs:
  - `_resolve_agent_ref()` can cross module boundaries
  - workflow route lines already lower to imported agent identities
  - route validation already rejects abstract targets
- Doctrine does not ship `export`, `from ... import ...`, or `package`
  declarations yet, so there is no first-class authored public package API
  layer to reuse directly.

## 4.4 Observability + failure behavior today

- Missing or wrong emit entrypoints fail loud through `E510`, `E512`, `E520`,
  and `E521`.
- Runtime emit and flow emit fail loud with `E502` when the target entrypoint
  has no local concrete agents.
- Import cycles fail loud. `tests/test_import_loading.py` proves the compiler
  does not hang on cyclic sibling imports.
- Route targets fail loud unless they resolve to concrete agents.
- Skill-package bundling fails loud on path collisions, case collisions,
  reserved compiler-owned outputs, and missing bundled files.
- There is no runtime-package-specific failure surface yet for:
  - directory-backed package imports
  - optional sibling `SOUL.prompt`
  - bundled peer files beside runtime agents
  - file-module versus package-module ambiguity

## 4.5 UI surfaces (ASCII mockups, if UI work)

No UI work is in scope. The user-facing surfaces today are:

- authored `.prompt` files
- emitted `AGENTS.md`, `SOUL.md`, and `SKILL.md`
- bundled skill-package files under emitted package trees
- checked-in `build_ref/` trees and flow artifacts used as proof
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

The chosen v1 runtime-package shape is a directory-backed package rooted by
`AGENTS.prompt`.

- A runtime agent package is one directory under `prompts/` that contains:
  - required `AGENTS.prompt`
  - optional `SOUL.prompt`
  - ordinary bundled peer files
- `AGENTS.prompt` in that package root must define exactly one concrete
  routeable agent. It may also define abstract helpers or reusable local
  declarations.
- If sibling `SOUL.prompt` exists, it must also define exactly one concrete
  agent with the same concrete name as sibling `AGENTS.prompt`. Any extra
  local helpers must stay non-concrete.
- Ordinary non-`.prompt` files under the package root bundle through under the
  same relative paths, byte for byte.
- Other prompt files under a runtime package root are not part of the public
  package contract. They should fail loud instead of being silently treated as
  bundled runtime companions.
- A thin flow-facing build handle remains one ordinary emit target entrypoint.
  In v1 it stays an `AGENTS.prompt` file. That file may define shared flow
  declarations, may keep local concrete agents when needed, and may import
  runtime package directories explicitly.
- File-backed modules such as `shared/greeters.prompt` stay valid.
- If both of these exist for the same dotted import path, the compiler must
  fail loud:
  - `<module>.prompt`
  - `<module>/AGENTS.prompt`

Emitted layout:

- A runtime package emits under the package root's relative path beneath
  `prompts/`.
- Compiler-owned runtime outputs are:
  - `AGENTS.md`
  - optional `SOUL.md`
- Bundled ordinary files emit beside those Markdown files under the same
  package-relative paths.

## 5.2 Control paths (future)

The chosen runtime path keeps one runtime emitter and one explicit import graph:

1. The entrypoint target still resolves through `EmitTarget` and the current
   prompts-root-aware target plumbing.
2. Import loading grows one new capability:
   - a dotted module path may resolve to a file module `<module>.prompt`
   - or to a directory-backed runtime package `<module>/AGENTS.prompt`
3. If both shapes exist for the same dotted import, the compiler fails loud.
   There is no precedence rule.
4. The compiler records enough metadata on loaded units to know whether a unit
   came from:
   - a file module
   - a directory-backed runtime package root
5. `emit_common` gains one shared runtime frontier collector that walks the
   full explicit import graph loaded from the entrypoint and returns the
   ordered set of runtime roots to emit. That frontier includes:
   - local concrete agents declared in the entrypoint itself, which preserves
     the current contract
   - imported directory-backed runtime packages, one concrete agent each,
     in first-seen graph order
   - no repeated roots when the same package unit is imported more than once
   - no root selection from raw filesystem scans
   - no requirement that the entrypoint restate a package import already
     reached through an imported module
6. `emit_docs` becomes package-aware but stays the canonical runtime emitter.
   It compiles each emitted root from its owning unit, writes `AGENTS.md`,
   writes optional `SOUL.md`, and bundles peer files for package-backed units.
7. `emit_flow` uses the same frontier collector as `emit_docs` so the build
   handle and the flow graph stay aligned.
8. `verify_corpus` and emit smoke checks reuse the same shared frontier and
   bundle rules so proof stays on the canonical path.

Compatibility posture:

- preserve existing file-module imports
- preserve existing local-root `emit_docs` and `emit_flow` behavior
- preserve direct `SOUL.prompt` targets
- add runtime-package imports as a new explicit surface
- do not add a bridge layer, wrapper manifest, or discovery scan
- do not add a third emitter

## 5.3 Object model + abstractions (future)

- `IndexedUnit` should gain explicit module-source metadata so later code does
  not keep guessing from file paths.
- Add one shared runtime emit plan object. It should carry:
  - owning unit
  - concrete agent identity
  - package root when the unit is package-backed
  - optional sibling `SOUL.prompt` unit
  - bundled peer files to copy
- Replace `root_concrete_agents()` with a shared runtime frontier helper in the
  emit layer. `emit_docs`, `emit_flow`, corpus proof, and smoke proof should
  all use that same helper.
- Add unit-aware compile entrypoints under the current session/context path so
  runtime emit can compile imported package agents without pretending they are
  root-unit agents. The current root-name compile helpers stay as convenience
  wrappers for existing callers.
- Extract the reusable source-root bundle planner out of
  `compile/skill_package.py` into a shared package-layout helper. Runtime
  packages and skill packages should share:
  - path normalization
  - ordinary-file enumeration
  - case-collision checks
  - reserved compiler-owned output path checks
  - byte-for-byte ordinary file bundling
- Keep prompt-shape rules outside that shared helper:
  - runtime emit owns the optional sibling `SOUL.prompt` contract and the
    fail-loud rejection of extra `.prompt` files under runtime package roots
  - `compile/skill_package.py` keeps bundled prompt subtree planning and
    `agents/**/*.prompt` compilation
- Keep runtime packages and skill packages as separate public authoring
  surfaces:
  - runtime packages are rooted by `AGENTS.prompt`
  - skill packages are rooted by `SKILL.prompt`
- Do not add new public `export` or `package` syntax in v1. The package-owned
  identity story in v1 is:
  - explicit import of the package directory module
  - dotted agent ref to the concrete agent inside that unit
- The future `../doctrine2` package-barrel story may layer on top later, but it
  is not required for this step.

## 5.4 Invariants and boundaries

- `emit_docs` stays the one canonical runtime emitter.
- The runtime frontier is:
  - local concrete agents declared in the entrypoint itself
  - plus the first-seen directory-backed runtime package units in the full
    explicit import-graph closure loaded from that entrypoint
- No filesystem discovery.
- A directory-backed runtime package must have exactly one concrete agent in
  `AGENTS.prompt`.
- Optional sibling `SOUL.prompt` must:
  - define exactly one concrete agent
  - use the same concrete agent name as sibling `AGENTS.prompt`
  - keep any extra local helpers non-concrete
- File-module and directory-package import collisions fail loud.
- Runtime-package peer files may not collide with `AGENTS.md`, `SOUL.md`, or
  each other.
- Runtime packages do not silently bundle extra prompt files.
- `emit_docs` and `emit_flow` must share the same runtime frontier rule.
- Route and owner refs continue to use real imported agent identities. There is
  no naming-only local stub path.
- `SKILL.prompt` keeps its shipped semantics. Runtime packages do not become a
  second spelling of skill packages.
- Existing local-root examples must keep working on the current path.
- Additional prompt roots keep working. Directory-backed runtime package imports
  must respect the same root and ambiguity rules as file modules.

## 5.5 UI surfaces (ASCII mockups, if UI work)

No UI work is in scope. The acceptance pack is the authored and emitted shape:

- one thin flow-facing build handle under `prompts/`
- two or more imported runtime package directories
- one emitted tree per runtime package with:
  - `AGENTS.md`
  - optional `SOUL.md`
  - bundled peer files
- one flow graph emitted from the same build handle
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Import resolution | `doctrine/_compiler/indexing.py` | `_module_path_for_root`, `load_module`, `resolve_module_root` | Imports resolve only to `<module>.prompt`. | Add directory-backed runtime package resolution to `<module>/AGENTS.prompt`, record module-source kind, and fail loud when file and directory shapes collide. | Runtime package homes must be importable without new discovery rules. | One dotted import may resolve to a file module or a directory-backed runtime package, never both. | `tests/test_import_loading.py`, new runtime-package import tests |
| Runtime frontier selection | `doctrine/emit_common.py` | `root_concrete_agents()` and shared emit helpers | Runtime emit and flow emit select only local concrete agents in the entrypoint file. | Replace the root-only helper with a shared runtime frontier collector that preserves authored order, keeps local entrypoint concrete agents, and adds first-seen directory-backed runtime package units from the full explicit import-graph closure. | `emit_docs` and `emit_flow` need the same root set without forcing duplicate direct imports in the build handle. | One shared runtime frontier for docs emit, flow emit, corpus proof, and smoke proof. | `tests/test_emit_docs.py`, `tests/test_emit_flow.py`, corpus build-contract proof |
| Unit-aware runtime compile | `doctrine/_compiler/session.py`, `doctrine/_compiler/context.py` | `compile_agent`, `compile_agents`, `extract_target_flow_graph` | Public compile and flow entrypoints compile only root-unit agent names. | Add unit-aware compile and flow helpers under the same session/context owner path. Keep current root-name helpers as wrappers. | Imported package agents must compile from their owning units, not through fake root aliases. | Runtime emit and flow graph extraction can compile `(unit, agent)` roots directly. | `tests/test_emit_docs.py`, `tests/test_emit_flow.py`, `tests/test_compiler_boundary.py` |
| Runtime package layout and companion emit | `doctrine/emit_docs.py` | `emit_target()` and output path planning | Writes only entrypoint-local `AGENTS.md` or `SOUL.md`. No peer-file bundling. | Make runtime emit package-aware: emit `AGENTS.md`, optional sibling `SOUL.md`, and bundled peer files for package-backed units while keeping current local-root behavior. | This is the user-facing runtime package feature. | `emit_docs` remains the runtime emitter, now with package-backed unit plans. | `tests/test_emit_docs.py`, new runtime-package emit tests, `make verify-examples` |
| Shared source-root bundle rules | `doctrine/_compiler/compile/skill_package.py`, `doctrine/emit_skill.py` | bundle path checks and file enumeration | Bundle planning lives only in the skill-package compiler. | Extract only the generic source-root path and ordinary-file bundle planner so runtime packages and skill packages share one collision and layout rule set while each caller keeps its own prompt policy. | Avoid parallel package planners without forcing runtime packages and skill packages into one prompt model. | One shared package-layout helper for ordinary files and collisions; prompt-shape rules stay surface-specific. | `tests/test_emit_skill.py`, package examples `95` through `103` |
| Flow parity | `doctrine/emit_flow.py`, `doctrine/_compiler/flow.py` | root graph extraction | Flow graphs root only at local entrypoint agents, though routed imported agents can appear later. | Root flow graphs at the shared runtime frontier so the thin build handle emits the same flow story as docs emit. | The feature is incomplete if the build handle emits docs but not a truthful flow graph. | `emit_flow` and `emit_docs` use the same runtime frontier. | `tests/test_emit_flow.py`, `examples/73_flow_visualizer_showcase`, new runtime-package flow example |
| Optional sibling `SOUL.prompt` contract | `doctrine/emit_docs.py`, shared package planner, diagnostics | direct `SOUL.prompt` targets only | `SOUL.prompt` is only a direct entrypoint today. There is no package-backed sibling contract. | Add sibling `SOUL.prompt` discovery for package-backed runtime units and require exactly one concrete agent with the same name as sibling `AGENTS.prompt`, while allowing only non-concrete extra helpers. Keep direct `SOUL.prompt` targets working. | The package model must support local `SOUL.prompt` without a second wrapper path. | Package-backed `SOUL.prompt` is optional, explicit, same-name, and fail-loud on extra concrete agents. | new runtime-package soul tests, `tests/test_emit_docs.py` |
| Corpus and smoke proof | `doctrine/_verify_corpus/runners.py`, `doctrine/_diagnostic_smoke/emit_checks.py`, `doctrine/_diagnostic_smoke/flow_emit_checks.py` | emitter branching and build-ref expectations | Proof branches mostly on `SKILL.prompt` versus non-`SKILL.prompt`. Runtime docs proof assumes root-only agent emit, and flow smoke still follows the current flow-root story. | Update proof helpers to exercise package-backed runtime emit and shared-frontier flow roots through the canonical runtime path. | The canonical proof path must match the new runtime path for both docs emit and flow emit. | Build-contract proof and flow smoke understand runtime package trees emitted through `emit_docs` and rooted through the shared frontier. | `tests/test_verify_corpus.py`, `make verify-examples`, `make verify-diagnostics` |
| Public docs and examples | `docs/EMIT_GUIDE.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/SKILL_PACKAGE_AUTHORING.md`, `examples/README.md`, new generic example(s) | runtime package guidance | Docs teach local-root runtime emit and `SKILL.prompt` packages, but not runtime packages rooted by `AGENTS.prompt`. | Add the runtime package story, keep `SKILL.prompt` separate, and add one generic proof example with one thin build handle, two imported runtime packages, one bundled peer file, one optional sibling `SOUL.prompt`, and one real imported route or owner ref. | The feature is public only when docs and proof teach it cleanly. | One generic runtime-package authoring and emit story. | doc review, `make verify-examples`, `make verify-package` |

Rows above include both code and non-code surfaces because this feature changes
the same runtime package contract across compiler, emitter, proof, and docs.

## 6.2 Migration notes

* Canonical owner path / shared code path:
  - `emit_docs` stays the runtime emitter.
  - import loading gains directory-backed runtime package units.
  - one shared runtime frontier selects emitted roots from the full explicit
    import-graph closure plus entrypoint-local concrete agents.
  - one shared package-layout helper owns ordinary-file bundling and path
    checks only.
* Deprecated APIs (if any):
  - no public CLI or target field is removed in this phase
  - internal root-only frontier helpers should be retired once the shared
    runtime frontier lands
* Delete list (what must be removed; include superseded shims/parallel paths if any):
  - `root_concrete_agents()` once the shared runtime frontier fully replaces it
  - duplicated source-root bundle and collision logic if it remains split
    between skill-package and runtime-package code after the refactor
  - any wrapper-only concrete stubs added just to name imported package agents
  - any file-versus-directory import precedence heuristic
* Adjacent surfaces tied to the same contract family:
  - `emit_flow`
  - corpus build-contract verification
  - emit smoke checks
  - additional prompt roots in project config
  - public emit and language docs
  - generic proof examples and `build_ref/` trees
* Compatibility posture / cutover plan:
  - preserve current local-root runtime emit and direct `SOUL.prompt` emit
  - preserve current file-module imports
  - add directory-backed runtime packages as a new explicit path
  - no bridge, no discovery scan, no third emitter
* Capability-replacing harnesses to delete or justify:
  - none. This is compiler and emit-path work. No wrapper harness or runtime
    post-processor is justified.
* Live docs/comments/instructions to update or delete:
  - `docs/EMIT_GUIDE.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/SKILL_PACKAGE_AUTHORING.md`
  - `docs/VERSIONING.md`
  - `CHANGELOG.md`
  - `examples/README.md`
  - new generic runtime-package example comments, if added
* Behavior-preservation signals for refactors:
  - `tests/test_emit_docs.py`
  - `tests/test_emit_skill.py`
  - `tests/test_emit_flow.py`
  - `tests/test_import_loading.py`
  - `tests/test_verify_corpus.py`
  - `make verify-examples`
  - `make verify-diagnostics`
  - `make verify-package`

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Package layout rules | `doctrine/_compiler/compile/skill_package.py`, runtime-package emit path | Use one shared source-root bundle and path-collision helper | Prevents skill packages and runtime packages from drifting into two file-layout rule sets | include |
| Runtime root selection | `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, `doctrine/_verify_corpus/runners.py`, `doctrine/_diagnostic_smoke/emit_checks.py` | Use one shared runtime frontier collector | Prevents emitted docs, flow graphs, smoke proof, and corpus proof from disagreeing about what the build handle owns | include |
| Import search across prompt roots | `doctrine/_compiler/indexing.py`, `doctrine/project_config.py`, `tests/test_import_loading.py` | Apply the same ambiguity and root rules to directory-backed runtime package imports as file-module imports | Prevents a second import system hidden inside the package feature | include |
| Optional sibling soul contract | package-backed runtime units and direct `SOUL.prompt` targets | Keep direct `SOUL.prompt` emit valid while adding explicit same-identity package companion emit | Prevents an accidental break in an already shipped surface | include |
| Generic proof example | `examples/README.md`, new runtime-package example, emitted `build_ref/` tree | Teach the thin build handle and package-owned runtime homes in one generic proof example | Prevents docs drift and keeps the public story separate from `SKILL.prompt` packaging | include |
| Future package barrels | `../doctrine2/docs/LANGUAGE_REDESIGN_EXT_SPEC.md` export and package surfaces | Do not implement full `export` or `package` syntax in this step | Prevents the runtime package feature from expanding into the redesign package | exclude |
| Filesystem discovery | runtime package scanning outside imports | Do not add it | Prevents implicit roots, surprise emits, and hidden coupling to repo shape | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the smallest reasonable sequence of coherent self-contained units that can be completed, verified, and built on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit; `Checklist (must all be done)` is the authoritative must-do list inside the phase; `Exit criteria (all required)` names the concrete done conditions. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 - Import loading learns directory-backed runtime packages

Status: COMPLETE

Completed work:
- The loader now resolves imports to either `<module>.prompt` or
  `<module>/AGENTS.prompt`.
- Indexed units now record explicit module-source kind and package-root
  metadata.
- File-versus-directory collisions fail loud without a precedence rule.
- Import-loading proof now covers runtime packages, root collisions, prompt
  roots, and the existing cycle failure path.

* Goal:
  Make runtime package homes importable through the same dotted import system
  that already loads file modules.
* Work:
  Extend the loader and indexed-unit model so one dotted path can resolve to a
  file module or a directory-backed runtime package root, with fail-loud
  ambiguity checks.
* Checklist (must all be done):
  - Update `doctrine/_compiler/indexing.py` so a dotted import can resolve to
    `<module>.prompt` or `<module>/AGENTS.prompt`.
  - Record explicit module-source metadata and package-root metadata on the
    loaded unit instead of making later code guess from file paths.
  - Fail loud when both shapes exist for the same dotted path. Do not add a
    precedence rule.
  - Preserve `additional_prompt_roots` behavior and the current import-cycle
    failure story.
  - Add or update import-loading tests for:
    - directory-backed runtime package resolution
    - file-versus-directory ambiguity
    - additional prompt roots
    - existing cycle failures
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_import_loading`
* Docs/comments (propagation; only if needed):
  - Add one short code comment at the module-shape collision branch if the
    failure path would otherwise be hard to read.
* Exit criteria (all required):
  - Imported runtime package units load without discovery scans.
  - File-module imports still work.
  - File-versus-directory ambiguity fails loud.
  - Import-cycle proof still passes.
* Rollback:
  - Revert the module-kind and loader changes as one patch if downstream
    callers cannot yet consume the new metadata safely.

## Phase 2 - Extract one shared ordinary-file package-layout helper

Status: COMPLETE

Completed work:
- Extracted `doctrine/_compiler/package_layout.py` for normalized bundle-path
  checks, compiler-owned output collisions, and byte-for-byte ordinary-file
  bundling.
- Moved skill-package ordinary-file bundling onto that shared helper.
- Kept bundled prompt subtree handling in
  `doctrine/_compiler/compile/skill_package.py`.

* Goal:
  Give runtime packages and skill packages one shared source-root ordinary-file
  layout rule without merging their prompt rules.
* Work:
  Pull the generic path and ordinary-file bundle logic out of the current skill
  package planner and keep prompt-shape policy in the surface-specific callers.
* Checklist (must all be done):
  - Extract one shared helper for:
    - source-root path normalization
    - ordinary-file enumeration
    - case-collision checks
    - compiler-owned output collision checks
    - byte-for-byte ordinary-file bundling
  - Keep bundled prompt subtree planning in
    `doctrine/_compiler/compile/skill_package.py`.
  - Keep `emit_skill` behavior byte-for-byte stable on the shipped test cases.
  - Shape the helper so runtime emit can call it later without cloning the
    same layout rules a second time.
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_emit_skill`
* Docs/comments (propagation; only if needed):
  - Add one short code comment at the shared-helper boundary so future edits do
    not pull prompt policy back into the generic file-layout helper.
* Exit criteria (all required):
  - One reusable ordinary-file layout helper exists.
  - Skill-package prompt behavior stays unchanged.
  - The repo no longer needs two separate ordinary-file collision rule sets.
* Rollback:
  - Revert the helper extraction as one patch if skill-package output changes
    before runtime emit adopts the shared helper.

## Phase 3 - Build the shared runtime frontier and unit-aware compile roots

Status: COMPLETE

Completed work:
- Added `collect_runtime_emit_roots()` for the shared first-seen runtime
  frontier over the full explicit import graph.
- Added unit-aware compile helpers and flow-root extraction helpers on the
  compiler session/context path.
- Kept the existing root-name compile and flow helpers as wrappers.
- Added focused proof for frontier order, unit-aware compile roots, and
  imported flow roots.

* Goal:
  Put one canonical runtime-frontier and unit-aware compile primitive in place
  before runtime docs emit, runtime flow emit, and proof surfaces adopt it.
* Work:
  Replace the root-only runtime frontier with one shared import-graph frontier,
  add compile entrypoints that can compile `(unit, agent)` roots directly, and
  keep current local-root callers stable until Phase 4 moves them over.
* Checklist (must all be done):
  - Add one shared runtime frontier collector in the emit path.
  - Make that collector:
    - keep local concrete agents declared in the entrypoint
    - add first-seen directory-backed runtime package units from the full
      explicit import-graph closure
    - dedupe repeated package units
    - avoid filesystem discovery
  - Add unit-aware compile helpers in
    `doctrine/_compiler/session.py` and `doctrine/_compiler/context.py`.
  - Keep the current root-name compile helpers as wrappers for current callers.
  - Add flow-root extraction support under the compiler path so Phase 4 can
    adopt the shared frontier without inventing a second root selector.
  - Preserve current local-root `emit_docs` and `emit_flow` callers through the
    wrapper path until Phase 4 adopts the shared frontier.
  - Add or update tests for frontier order, dedupe, and unit-aware compile
    roots.
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_compiler_boundary tests.test_emit_docs tests.test_emit_flow`
* Docs/comments (propagation; only if needed):
  - Add one short code comment where the frontier preserves first-seen
    import-graph order.
* Exit criteria (all required):
  - One shared runtime-frontier helper exists.
  - Imported package-owned agents can compile from their owning units.
  - Flow root extraction support can consume the same frontier contract.
  - Current local-root docs and flow callers still have wrapper coverage before
    package-aware caller adoption begins.
* Rollback:
  - Revert the new frontier callers together if the shared root set is not yet
    stable enough for runtime emit.

## Phase 4 - Make runtime emit and flow emit package-aware

Status: COMPLETE

Completed work:
- `emit_docs` now emits imported runtime packages through explicit runtime
  emit plans, including package-root `AGENTS.md`, optional same-name
  `SOUL.md`, and bundled peer files.
- `emit_docs` rejects extra runtime `.prompt` files under package roots and
  rejects sibling `SOUL.prompt` files with the wrong concrete shape.
- `emit_flow` now roots graphs on the same shared runtime frontier as
  `emit_docs`.
- Focused emit proof now covers package-backed runtime output, sibling soul
  success/failure, extra prompt rejection, and flow-root parity.

* Goal:
  Emit real runtime package trees and keep docs emit and flow emit on the same
  ownership story.
* Work:
  Teach `emit_docs` and `emit_flow` to use the shared frontier, compile
  package-owned units directly, bundle peer files, and enforce the sibling
  `SOUL.prompt` contract.
* Checklist (must all be done):
  - Update `doctrine/emit_docs.py` to build one runtime emit plan per selected
    root.
  - Emit `AGENTS.md` under each package-backed runtime root.
  - Emit optional sibling `SOUL.md` only when sibling `SOUL.prompt` defines
    exactly one concrete agent with the same name as sibling `AGENTS.prompt`.
  - Reject extra concrete agents in sibling `SOUL.prompt`.
  - Reject extra runtime `.prompt` files under runtime package roots instead of
    silently bundling them.
  - Bundle ordinary peer files for package-backed runtime units through the
    shared layout helper.
  - Preserve direct `SOUL.prompt` targets and current local-root
    `AGENTS.prompt` targets.
  - Move `emit_docs` and `emit_flow` onto the shared runtime frontier and the
    unit-aware compile path.
  - Update `doctrine/emit_flow.py` so flow graphs root on the same runtime
    frontier as docs emit.
  - Retire `root_concrete_agents()` once both runtime callers no longer depend
    on it.
  - Add or update emit tests for:
    - package-backed runtime output
    - sibling `SOUL.prompt` success and failure
    - extra runtime `.prompt` rejection
    - flow-root parity
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_emit_docs tests.test_emit_flow`
* Docs/comments (propagation; only if needed):
  - Add one short code comment at the sibling `SOUL.prompt` validation branch
    and one at the runtime emit-plan boundary if those branches would otherwise
    be hard to follow.
* Exit criteria (all required):
  - `emit_docs` and `emit_flow` use the same runtime frontier.
  - Package-backed runtime roots emit stable package trees.
  - Sibling `SOUL.prompt` is fail loud and same-name only.
  - Existing direct entrypoint behavior still works.
* Rollback:
  - Revert the package-aware runtime caller changes as one patch if emitted
    trees or flow parity regress before proof surfaces move over.

## Phase 5 - Move corpus proof, smoke proof, and one generic example onto the new path

Status: REOPENED (audit found missing code work)

Missing (code):
- `doctrine/_verify_corpus/runners.py`,
  `doctrine/_diagnostic_smoke/emit_checks.py`, and
  `doctrine/_diagnostic_smoke/flow_emit_checks.py` still do not prove
  package-backed runtime emit or flow roots on the canonical path.
- No generic runtime-package example target or checked-in `build_ref/` tree
  has landed yet, and `tests/test_verify_corpus.py` still only anchors the
  old flow build-contract case.

* Goal:
  Prove the shipped feature through the same canonical emit path the runtime
  will use.
* Work:
  Update the proof helpers and add one generic manifest-backed example that
  teaches the runtime package story without Rally jargon.
* Checklist (must all be done):
  - Update `doctrine/_verify_corpus/runners.py` so build-contract proof
    understands package-backed runtime output trees.
  - Update `doctrine/_diagnostic_smoke/emit_checks.py` and
    `doctrine/_diagnostic_smoke/flow_emit_checks.py` to use the shared runtime
    frontier and package-backed output expectations.
  - Add one new generic manifest-backed example with:
    - one thin build handle
    - two imported runtime packages
    - one bundled peer file
    - one optional sibling `SOUL.prompt`
    - one route or owner ref to a real imported agent identity
  - Check in the emitted `build_ref/` truth for that example.
  - Keep existing examples and diagnostics generic. Do not add Rally-only
    fixtures or special-case proof logic.
  - Add or update corpus tests for package-backed runtime verification.
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_verify_corpus`
  - `make verify-diagnostics`
  - `make verify-examples`
* Docs/comments (propagation; only if needed):
  - Keep example comments short and generic. Remove any example wording that
    would imply runtime discovery or wrapper-only concrete stubs.
* Exit criteria (all required):
  - One generic example proves the new runtime package story end to end.
  - Corpus and smoke proof no longer assume root-only runtime emit.
  - Diagnostics and example verification pass on the canonical path.
* Rollback:
  - Revert proof-surface and example truth together if emitted output is still
    moving, rather than checking in unstable `build_ref/` artifacts.

## Phase 6 - Rewrite live public docs and release truth

Status: REOPENED (audit found missing code work)

Missing (code):
- `docs/EMIT_GUIDE.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/SKILL_PACKAGE_AUTHORING.md`, and `examples/README.md` still teach the
  old runtime story instead of the new runtime-package surface.
- `docs/VERSIONING.md` and `CHANGELOG.md` do not yet classify or describe the
  additive runtime-agent package release.

* Goal:
  Leave one clear public story for runtime packages, imports, and emitted
  output.
* Work:
  Update the live docs, example guidance, and release-facing truth so they
  match the shipped runtime package model and keep `SKILL.prompt` clearly
  separate.
* Checklist (must all be done):
  - Update `docs/EMIT_GUIDE.md` with the package-backed runtime emit story.
  - Update `docs/LANGUAGE_REFERENCE.md` with the file-module versus
    directory-backed runtime package import rule.
  - Update `docs/SKILL_PACKAGE_AUTHORING.md` so it stays clear that runtime
    packages and skill packages are different public surfaces.
  - Update `examples/README.md` so it teaches the new generic example and the
    thin build-handle pattern.
  - Remove stale wording about runtime companion sidecars, wrapper-only
    concrete stubs, or parallel runtime packaging stories.
  - Update `docs/VERSIONING.md` and `CHANGELOG.md` for the new public runtime
    package surface and its release classification.
* Verification (required proof):
  - `make verify-package`
* Docs/comments (propagation; only if needed):
  - Keep all bundled Markdown prose and agent replies at the plain-language bar
    required by the repo.
* Exit criteria (all required):
  - Public docs teach one runtime package story.
  - `SKILL.prompt` and runtime-package guidance do not blur together.
  - Versioning and changelog truth match the shipped public change.
* Rollback:
  - Revert the public-doc and release-truth edits with the feature if the code
    or proof story is not yet ready to ship.

## Phase 7 - Run the full repo proof set and clean final drift

Status: REOPENED (audit found missing code work)

Missing (code):
- The required `uv sync`, `npm ci`, `make verify-examples`,
  `make verify-diagnostics`, and `make verify-package` sweep is not yet
  recorded for this feature.
- Final truth is still drifted, so Phase 7 cannot close until the Phase 5-6
  surfaces land and the full proof sweep runs clean.

* Goal:
  End with one verified, aligned, and shippable runtime package story.
* Work:
  Run the full repo commands required by the touched surfaces, fix any last
  drift they expose, and stop only when the shipped truth agrees across code,
  examples, diagnostics, and docs.
* Checklist (must all be done):
  - Run `uv sync`.
  - Run `npm ci`.
  - Run `make verify-examples`.
  - Run `make verify-diagnostics`.
  - Run `make verify-package`.
  - Repair any last example, diagnostic, or doc drift exposed by those
    commands.
  - Confirm no touched live doc, example, or instruction still teaches the old
    runtime story.
* Verification (required proof):
  - `make verify-examples`
  - `make verify-diagnostics`
  - `make verify-package`
* Docs/comments (propagation; only if needed):
  - None beyond the final truth-sync fixes exposed by the required proof.
* Exit criteria (all required):
  - The full required repo proof set passes.
  - Code, examples, diagnostics, docs, versioning, and changelog all agree.
  - No wrapper-only fallback story remains in touched live truth.
* Rollback:
  - Do not ship partial truth. Revert unfinished last-mile fixes instead of
    leaving the repo in a half-migrated runtime package state.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

This feature should avoid verification bureaucracy. Proof should stay close to
the shipped compiler and emitted artifact behavior. The final proof set should
be lean, generic, and strong enough to show both Doctrine-native correctness
and Rally-use-case fitness.

## 8.1 Unit tests (contracts)

- Import-loading and compile-boundary tests for the new module-kind and
  unit-aware runtime-root surface.
- Resolve and diagnostic tests for imported agent identity, route targets,
  owner targets, and fail-loud collisions.
- Emit-path and flow-root tests for runtime package layout, sibling
  `SOUL.prompt`, and bundled peer files.

## 8.2 Integration tests (flows)

- Generic manifest-backed examples that prove:
  - local package ownership
  - thin flow composition
  - route and owner references to imported real agent identities
  - stable emitted per-agent package trees

## 8.3 E2E / device tests (realistic)

- Repo-local emit proof should be the primary gate.
- A later manual integration read against the Rally use case is useful, but it
  should stay a final confidence check, not the main proof harness.

## 8.4 Final repo sweep

- This change touches runtime emit, flow emit, diagnostics, examples, and
  public docs, so the final sweep should use the repo's real commands:
  - `uv sync`
  - `npm ci`
  - `make verify-examples`
  - `make verify-diagnostics`
  - `make verify-package`
- Use targeted unit tests inside the earlier phases, then use the full repo
  sweep only after the public story is aligned.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

This should ship as one additive backward-compatible public feature release,
not as a hard public cutover. Current local-root runtime emit, direct
`SOUL.prompt`, and file-module imports stay valid. Directory-backed runtime
packages become the new explicit path. Internal implementation can stage the
refactor, but the shipped public story should still end with one clear runtime
package model and no equal parallel packaging story.

## 9.2 Telemetry changes

No product telemetry changes are planned. Release truth should call out the
new additive runtime-package surface, the preserved current entrypoints, and
the fail-loud package rules.

## 9.3 Operational runbook

Docs and examples will matter more than runtime ops here. The runbook burden is
mainly:

- how to author a runtime agent package
- how to compose packages into one flow
- how to emit the compiled package tree

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: explorer 1, explorer 2, self-integrator
- Scope checked:
  - frontmatter, `planning_passes`, and helper-block drift
  - `# TL;DR`
  - `# 0)` through `# 10)`
  - cross-section agreement on owner path, compatibility posture, migration
    surfaces, verification, rollout, and release truth
- Findings summary:
  - release-truth surfaces were not named consistently across the audit and
    phase plan
  - Phase 3 proof was too weak for preserved runtime-docs coverage
  - flow smoke was missing from the exhaustive audit
  - rollout wording still sounded pre-deep-dive and branchy
  - verification still asked for parser work that v1 does not plan
- Integrated repairs:
  - locked additive compatibility posture in Section 0
  - added `docs/VERSIONING.md`, `CHANGELOG.md`, and flow smoke surfaces to the
    call-site audit
  - tightened the Phase 3 and Phase 4 boundary and added `tests.test_emit_docs`
    to Phase 3 proof
  - aligned Section 8 with the chosen loader, compile, emit, and proof scope
  - rewrote rollout and release-note wording to match the additive public
    feature story
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

## 2026-04-15 - Treat Rally as the use case, not the architecture

### Context

Rally needs Doctrine to support local agent ownership, clean routing identity,
and stable per-agent emitted package trees. The risk is solving that need with
a Rally-specific wrapper or side-emission story instead of a canonical Doctrine
feature.

### Options

1. Add Rally-specific emit helpers and keep Doctrine's current runtime-agent
   story mostly unchanged.
2. Add filesystem discovery so Doctrine can infer local agent homes without an
   explicit composition root.
3. Design a first-class Doctrine runtime agent package model and identity
   story, with a thin explicit flow-facing composition root.

### Decision

Draft the plan around option 3.

### Consequences

- The plan can satisfy Rally while keeping the public feature generic.
- The implementation may require deeper compiler and emit refactor work.
- The plan will prefer explicit composition and real imported agent identity
  over discovery magic.

### Follow-ups

- Confirm the North Star.
- Research the cleanest runtime package and identity surface.
- Deep-dive the owner path through parser, resolve, and emit code.

## 2026-04-15 - Stay compatible with the future redesign direction without importing all of it now

### Context

The sibling `../doctrine2` redesign docs already sketch a future public package
and export direction. This plan should not accidentally pick a local runtime
package model that fights that direction. At the same time, the current task is
not to land the whole redesign package.

### Options

1. Ignore `../doctrine2` and optimize only for the local shortest path.
2. Require the whole redesign package to land first.
3. Make this feature a narrow step that is compatible with the future package
   and export direction, while keeping unrelated redesign work out of scope.

### Decision

Draft the North Star around option 3.

### Consequences

- The plan must study the package barrel and export direction in
  `../doctrine2`.
- The implementation should avoid syntax or emit contracts that would dead-end
  against that direction.
- The plan should still resist scope creep into unrelated redesign work.

### Follow-ups

- Confirm the revised North Star.
- Use research and deep-dive to separate the reusable redesign direction from
  the parts that should stay out of scope for this feature.

## 2026-04-15 - V1 runtime packages are directory-backed `AGENTS.prompt` modules on the existing runtime emit path

### Context

The repo already has two useful pieces:

- source-root package layout rules under `SKILL.prompt`
- real imported dotted agent identity across file modules

It does not have:

- directory-backed runtime package imports
- a shared runtime frontier for `emit_docs` and `emit_flow`
- unit-aware runtime compile for imported package agents

This pass needed one concrete owner path that reuses the shipped code instead
of adding a third emitter or pulling in the full future export syntax.

### Options

1. Add a third runtime-package emitter beside `emit_docs` and `emit_skill`.
2. Add new public export or package syntax now and make that a prerequisite.
3. Treat a directory with `AGENTS.prompt` as a runtime package module, keep
   package identity on imported dotted agent refs, and extend the current
   runtime emit path to handle package-backed units.

### Decision

Choose option 3.

### Consequences

- `emit_docs` stays the canonical runtime emitter.
- `emit_flow` must reuse the same package-aware runtime frontier.
- Import loading must fail loud when a dotted path matches both a file module
  and a directory-backed package.
- Runtime packages and skill packages should share one source-root bundle and
  path-collision rule set where that is truly the same problem.
- V1 does not need new public `export` or `package` syntax.

### Follow-ups

- Deep-dive pass 2 should harden the exact runtime frontier contract and the
  sibling `SOUL.prompt` rules.
- Phase planning should split import loading, shared frontier, unit-aware
  compile, and package-layout convergence into separate foundational phases.

## 2026-04-15 - Deep-dive pass 2 locks import-graph frontier, sibling soul rules, and the helper split

### Context

Pass 1 chose directory-backed runtime packages on the existing runtime emit
path. The remaining design risk was hidden ambiguity:

- whether the runtime frontier should stop at direct imports or use the full
  explicit import-graph closure
- whether sibling `SOUL.prompt` should match by exact concrete identity or
  allow loose drift
- whether runtime and skill package convergence should share all prompt rules
  or only the generic file-layout rules

Those choices decide whether the feature keeps one thin build handle without
duplicate imports, one fail-loud package contract, and one honest shared
helper boundary.

### Options

1. Keep the frontier direct-import-only, allow looser sibling `SOUL.prompt`
   matching, and push most package rules into one broad shared helper.
2. Use the full explicit import-graph closure, require exact same-name sibling
   concrete-agent matching, and share only the generic ordinary-file layout and
   collision rules.

### Decision

Choose option 2.

### Consequences

- The thin build handle does not need duplicate direct imports just to get the
  right runtime package roots emitted.
- Package-backed `SOUL.prompt` stays fail loud:
  - exactly one concrete agent
  - same concrete agent name as sibling `AGENTS.prompt`
  - extra helpers must stay non-concrete
- The shared package-layout helper stays small and stable:
  - ordinary-file enumeration
  - path normalization
  - case-collision checks
  - compiler-owned output collision checks
- Prompt-shape policy stays where the behavior differs:
  - runtime emit owns sibling `SOUL.prompt` and extra runtime `.prompt` rules
  - skill-package compile owns bundled prompt subtree rules
- External research is not needed for this doc because repo truth already
  settles the design.

### Follow-ups

- `phase-plan` should split the work so import loading, shared frontier,
  unit-aware compile, runtime emit, proof updates, and docs move in small
  coherent steps.
- The first generic public example should teach the runtime package story
  without mixing it with `SKILL.prompt`.

## 2026-04-15 - Implement in seven small phases with proof late and public docs last

### Context

Deep-dive locked the architecture, but the remaining risk was execution drift.
This feature touches import loading, shared helpers, runtime frontier logic,
runtime emit, proof surfaces, public docs, and release truth. A blended plan
would make it too easy to skip proof updates, ship stale docs, or hide
regressions inside a large refactor.

### Options

1. Use a small number of broad phases that mix import loading, emit changes,
   proof work, and docs cleanup.
2. Split the work into narrow foundational phases that build in this order:
   import loading, shared helper extraction, runtime frontier and unit-aware
   compile, package-aware emit, proof surfaces, public docs, and final repo
   proof.

### Decision

Choose option 2.

### Consequences

- Import loading lands before any runtime-package caller depends on it.
- Skill-package preservation gets its own proof before runtime emit starts
  using the shared ordinary-file helper.
- The shared frontier and unit-aware compile path land before docs emit and
  flow emit adopt package-backed roots.
- Generic example proof lands before public docs claim the feature is shipped.
- The final repo sweep stays last, after examples, diagnostics, docs, and
  release truth already agree.

### Follow-ups

- `consistency-pass` should now audit whether the phase plan, verification
  strategy, and earlier sections still tell one story.

## 2026-04-15 - Ship runtime packages as an additive public feature release

### Context

The architecture and phase plan preserve current local-root runtime emit,
direct `SOUL.prompt`, and file-module imports. But rollout still described the
change like a hard public cutover, and the call-site audit did not yet name
all of the release-truth surfaces that must move with that classification.

### Options

1. Keep hard-cutover rollout wording even though the plan preserves current
   entrypoints.
2. State the real contract: this is an additive backward-compatible public
   feature release, with current entrypoints preserved and runtime packages
   added as a new explicit path.

### Decision

Choose option 2.

### Consequences

- Section 0 now locks the additive compatibility posture instead of leaving it
  to later sections.
- Rollout and release-note wording now matches the preserved entrypoint story.
- `docs/VERSIONING.md` and `CHANGELOG.md` are explicit call-site surfaces, not
  just late doc cleanup.

### Follow-ups

- `implement-loop` should treat versioning and changelog truth as ship-blocking
  follow-through for this public feature.
