---
title: "Doctrine - Flow Namespace - Architecture Plan"
date: 2026-04-17
status: complete
fallback_policy: forbidden
owners: []
reviewers: []
doc_type: architectural_change
related:
  - docs/LANGUAGE_REFERENCE.md
  - docs/COMPILER_ERRORS.md
  - docs/VERSIONING.md
  - examples/README.md
---

# TL;DR

**Outcome**

Doctrine would treat a flow as a directory, not a single `.prompt` file. All
`.prompt` files in one flow would share one flat namespace. `export` would mark
the declarations other flows may import. `import` would only cross flow,
package, or skill boundaries. Sibling files would stop importing each other.
This is a breaking language change. The release is now tagged as `v4.0.0`.
Fresh 2026-04-18 audit closed the plan.

**Problem**

Today `import` does two jobs that fight each other. It crosses real boundaries,
and it also acts as a local file-organization tool inside one flow. That makes
producer/critic and other cyclic sibling layouts fail with `E289 Cyclic import
module`, even when the real boundary is still inside one flow.

**Approach**

Re-key the compiler around flow roots. Index one merged `IndexedFlow` per flow
directory. Resolve bare names against the flow-wide registry. Keep imports only
for real cross-flow or package boundaries, and only against exported
declarations. Retire intra-flow relative imports and fail loud on sibling name
collisions.

**Plan**

Make one hard cut. Add explicit `export` for cross-flow visibility, replace the
unit-first compiler path with flow-first indexing, retarget diagnostics, tests,
and examples, rewrite docs and release surfaces, delete the old unit pipeline,
and cut `4.0`.

**Non-negotiables**

- No silent behavior change.
- No runtime shim or fallback path.
- True cross-flow cycles must still fail loud.
- Intra-flow sibling cycles must stop being treated as module cycles.
- The migration should stay mostly deletion-driven for authors.
- Prefer the smallest and clearest boundary model that solves the problem.
- Docs, examples, diagnostics, versioning, and release notes must move in the
  same change story.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-18
Verdict (code): COMPLETE
Manual QA: pending (non-blocking)

## Code blockers (why code is not done)
- None. Fresh 2026-04-18 audit verified the full approved Phase 1 through
  Phase 5 frontier against repo reality.
- Fresh evidence:
  - `git status --short` stayed clean before and after the proof reruns.
  - `git tag --list 'v4.0.0'` returned `v4.0.0`.
  - `git rev-parse --verify v4.0.0^{tag}` succeeded.
  - `git ls-remote --tags origin refs/tags/v4.0.0 refs/tags/v4.0.0^{}` showed
    the pushed annotated tag and peeled release commit.
  - `uv sync`, `npm ci`, `uv run --locked python -m unittest tests.test_package_release`,
    `uv run --locked python -m unittest tests.test_release_flow`,
    `make verify-examples`, `make verify-diagnostics`, and
    `make verify-package` all passed.
- I did not find evidence that execution weakened requirements, scope,
  acceptance criteria, or phase obligations to hide unfinished work.

## Reopened phases (false-complete fixes)
- None. Phase 1 through Phase 5 stay complete on fresh audit.

## Missing items (code gaps; evidence-anchored; no tables)
- None. Fresh audit found no remaining code frontier.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Run the author migration walkthrough from Section 8.3 if you still want the
  extra human readback.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-17
external_research_grounding: not started
deep_dive_pass_2: not started
recommended_flow: complete; optional arch-docs follow-through only
note: Planning, implementation, and fresh audit all closed on 2026-04-18. This block tracks stage order only.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine treats each flow root directory as the namespace owner, then:

- producer/critic, reviewer, and retry-loop layouts split across sibling files
  will compile without sibling imports
- true cross-flow import cycles will still fail loud
- sibling name collisions will fail loud with dedicated diagnostics
- cross-flow imports will only see declarations marked `export`
- author migration will be mostly deletion-driven
- the shipped corpus, targeted compiler tests, and release docs will prove the
  change without silent drift

The North Star is confirmed. This plan now chooses one hard-cut architecture:
explicit `export` for cross-flow visibility, no relative imports, and no dual
pipeline.

## 0.2 In scope

**Requested behavior scope**

- A flow is the set of `.prompt` files that compile together into one emit
  target.
- A flow root is the nearest boundary entrypoint directory.
- `AGENTS.prompt` stays the entrypoint for agent and runtime flows.
- `SKILL.prompt` stays the entrypoint for skill-package source roots.
- Every `.prompt` file under that directory is part of the flow unless it is
  inside a nested `AGENTS.prompt` or `SKILL.prompt` root.
- Bare names resolve across the merged declarations of one flow.
- Declarations are flow-local by default.
- `export` marks the declarations other flows may import.
- `import` remains for cross-flow, cross-package, and cross-skill references to
  exported declarations.
- Intra-flow relative imports are retired.
- Sibling declaration collisions fail loud.

**Allowed architectural convergence scope**

- Re-key indexing, resolution, session caches, flow-graph extraction, emit
  walkers, and verification around flows instead of per-file units.
- Rewrite affected examples, tests, diagnostics, and docs so the shipped truth
  stays consistent.
- Update versioning, changelog, and release guidance for a breaking language
  cut.

**Adjacent surfaces that move with this plan**

- `doctrine/grammars/doctrine.lark`
- `doctrine/parser.py`
- `doctrine/_compiler/indexing.py`
- `doctrine/_compiler/resolve/refs.py`
- `doctrine/_compiler/flow.py`
- `doctrine/_compiler/session.py`
- `doctrine/_model/core.py`
- `doctrine/emit_common.py`
- `doctrine/emit_flow.py`
- `doctrine/emit_docs.py`
- `doctrine/emit_skill.py`
- `doctrine/verify_corpus.py`
- `docs/COMPILER_ERRORS.md`
- `docs/LANGUAGE_REFERENCE.md`
- `docs/LANGUAGE_DESIGN_NOTES.md`
- `docs/VERSIONING.md`
- `CHANGELOG.md`
- `examples/README.md`
- the affected example and test directories named later in this plan

**Compatibility posture**

- Public posture: one hard breaking language cut from `3.0` to `4.0`.
- The accepted architecture does not include a feature flag, a public bridge,
  or a default-flip phase.
- Relative imports leave the grammar, docs, examples, and tests in the same
  cut.
- The old unit-based pipeline is deleted in the same implementation arc that
  lands the flow model.

## 0.3 Out of scope

- Any new product behavior beyond the flow-as-directory namespace change.
- New runtime memory, scheduling, orchestration, or harness behavior.
- New author-facing syntax beyond the single `export` surface chosen in this
  plan.
- A new boundary file such as `FLOW.prompt`.
- A temporary compatibility flag or long-lived dual public model.
- Unrelated compiler cleanup that is not needed to make flow namespaces the
  single source of truth.

## 0.4 Definition of done (acceptance evidence)

- The compiler builds one merged flow namespace per flow root and only exported
  declarations cross flow boundaries.
- The compiler no longer raises intra-flow false-positive `E289` errors.
- True cross-flow cycles still fail loud.
- Sibling collisions, missing exports, and intra-flow retired imports fail with
  clear diagnostics.
- The affected examples are migrated, and new proof examples cover the flat
  sibling namespace, producer/critic cycle, cross-flow import, export
  boundary, and fail-loud collision cases.
- `make verify-examples` passes on the shipped corpus.
- Any diagnostics changes are covered by `make verify-diagnostics`.
- Release/versioning docs are updated for the breaking cut, including
  `CHANGELOG.md` and `docs/VERSIONING.md`.
- The migration guide for authors is explicit, deletion-driven, and cites the
  new diagnostics they will see.

## 0.5 Key invariants (fix immediately if violated)

- No silent shadowing inside one flow.
- No runtime fallbacks or shims.
- No dual pipeline or default-flip story in the accepted architecture.
- No dual namespace story where file-level and flow-level ownership both claim
  the same declarations.
- No false-positive sibling cycle errors once the new model is active.
- No silent behavior change in examples, emitted docs, or diagnostics.
- No breaking release without the matching versioning and changelog payload.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Make the flow boundary mean something real.
2. Prefer the most elegant solution that fully solves the problem.
3. Let authors split cyclic sibling roles across files without semantic hacks.
4. Keep fail-loud behavior for real boundary bugs, name collisions, and
   ambiguity.
5. Keep the migration tight and mostly deletion-driven.
6. Keep shipped docs, examples, tests, and release guidance aligned with the
   compiler change.

## 1.2 Constraints

- This is a breaking language change, not a patch or minor release.
- The current shipped corpus spans examples `01` through `128`.
- Author tooling does not rely on the current proposal text. The shipped truth
  still lives in `doctrine/` plus the manifest-backed corpus.
- This plan deliberately chooses a hard cut. The repo should not carry the
  module-era and flow-era pipelines in parallel as part of the accepted design.
- Flow discovery becomes filesystem-driven, so hidden files, symlinks, and
  editor backups need explicit filter rules.
- Skill packages and runtime packages already mark real boundaries and must stay
  coherent under the new model.
- Fixture churn is likely larger than the direct import-test count suggests.

## 1.3 Architectural principles (rules we will enforce)

- A directory-backed flow is the namespace owner.
- Prefer one simple model over layered exceptions, side rules, or parallel
  concepts.
- `import` only crosses real boundaries.
- Sibling files auto-share declarations by bare name.
- Sibling collisions fail loud.
- Cross-flow ambiguity still fails loud.
- The compiler, emit path, docs, and proof corpus should all speak one boundary
  model.
- Keep the public migration explicit. Do not hide the break.

## 1.4 Known tradeoffs (explicit)

- File-private scope inside one flow goes away. Privacy moves up to the flow
  boundary.
- Opt-in `export` adds one new keyword, but it makes the new boundary real and
  keeps cross-flow APIs intentional.
- The migration is a larger one-time cut because same-flow imports, relative
  imports, and the old unit-first pipeline all disappear together.
- Emit output drift is possible if any emitted Markdown surface still keys off
  module-path identity. `make verify-examples` should catch it, and broad
  `ref/` or `build_ref/` regeneration may be needed in the rewrite PR.
- Flow discovery is cleaner than import-driven file loading, but it adds new
  hardening work around the filesystem.
- Skill-package and runtime-package unification under one boundary model
  broadens the audit surface during implementation.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine lets authors split a flow across multiple files only when the flow
graph has no cycles. Any producer/critic shape, any back-and-forth reviewer, or
any retry loop forces mutual imports between sibling files. That triggers
`E289 Cyclic import module` at load time.

The root cause is that `import` does two different jobs today:

1. Inter-flow boundary crossing: pull a skill, shared schema, or reusable
   package into the flow.
2. Intra-flow file organization: put `Producer` in one file and `Critic` in
   another because one giant file is unreadable.

The second job is not really a module job. It is a filesystem layout choice.

## 2.2 What’s broken / missing (concrete)

- E289 fires for sibling layout choices that should not be boundary errors.
- Authors are pushed toward one large file when the real graph is cyclic inside
  one flow.
- Flow-graph resolution gets dragged into lexical scope.
- Relative imports blur the line between "same flow" and "real boundary."
- File layout becomes semantic, when it should mostly be about readability.

The source proposal frames the re-think this way:

> Look at Go (or Rust crates, or OCaml modules):
>
> - A package is a directory of files.
> - All files in a package share one flat namespace. Bare names resolve across
>   files without any import.
> - `import` only crosses package boundaries.
> - Cyclic package imports stay illegal, and that rule means something real:
>   a true package cycle is a boundary bug.

## 2.3 Constraints implied by the problem

- Keep imports meaningful by reserving them for true boundary crossing.
- Keep cycle errors for real cross-flow cycles.
- Preserve fail-loud ambiguity and collision behavior.
- Make the migration obvious enough that authors can follow compiler errors
  instead of reading a long upgrade playbook first.
- Treat the release as breaking and version it honestly.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- **Go package model** — adopt directory-backed namespace ownership plus
  boundary-only imports — it matches the goal of making file layout a
  readability choice instead of a semantic one.
- **Rust crate boundary practice** — adopt the rule that the package boundary,
  not the local file split, is the meaningful import edge — it fits the user's
  elegance goal because it removes a fake layer instead of adding one.
- **OCaml-style fail-loud module discipline** — adopt fail-loud real boundary
  errors and reject faux privacy via sibling file layout — it keeps cycle and
  ambiguity errors meaningful.

## 3.2 Internal ground truth (code as spec)

- **Authoritative behavior anchors (do not reinvent)**
  - `doctrine/_compiler/indexing.py` — `ModuleLoadKey`, module-path resolution,
    runtime-package resolution, import loading, and `E289` cycle detection are
    all module-keyed today. `_runtime_package_path_for_root` already treats
    `<module>/AGENTS.prompt` as a real directory-backed boundary, while
    `load_imports()` still serializes import loading to avoid cycle deadlocks.
  - `doctrine/_compiler/resolve/refs.py` — bare refs resolve against the
    current `IndexedUnit` first, then against imported symbols. Imported module
    visibility and `E280`/`E308` behavior are still unit-scoped today.
  - `doctrine/_compiler/flow.py` — flow extraction is rooted in
    `(IndexedUnit, agent_name)` pairs, and route branches still load target
    units by module parts.
  - `doctrine/_compiler/session.py` — session caches and the root compile owner
    are still `_module_cache`, `_module_loading`, `_module_waits`, and
    `root_unit`.
  - `doctrine/emit_common.py` — runtime emit roots walk imported units and
    treat directory-backed runtime packages as a special imported-unit shape.
  - `doctrine/grammars/doctrine.lark` — relative imports are still first-class
    grammar surface through `relative_import_path: DOTS dotted_name`.
  - `docs/LANGUAGE_REFERENCE.md` — the shipped import contract still teaches
    both absolute and relative imports, file-backed modules, and
    directory-backed `AGENTS.prompt` runtime packages.
  - `docs/README.md` and `docs/EMIT_GUIDE.md` — `AGENTS.prompt` and
    `SOUL.prompt` are already the runtime entrypoints, while `SKILL.prompt` is
    already the skill-package entrypoint and package source root.
- **Canonical path / owner to reuse**
  - `doctrine/_compiler/indexing.py` — this should own flow discovery,
    membership, merge rules, collision rules, and load identity. It already
    owns the current import and cycle contract, so it is the right place to
    move boundary ownership.
  - `doctrine/_compiler/resolve/refs.py` — this should own the shift from
    unit-scoped bare-name lookup to flow-scoped bare-name lookup.
  - `doctrine/_compiler/flow.py` and `doctrine/emit_common.py` — these should
    follow the new flow identity instead of inventing a parallel graph model.
- **Adjacent surfaces tied to the same contract family**
  - `tests/test_import_loading.py` — proves today's sibling-cycle `E289`,
    runtime-package load shape, imported-symbol visibility, and skill-package
    local-root behavior.
  - `examples/03_imports/` — still teaches relative imports, duplicate module
    alias errors, duplicate imported symbol errors, and the current sibling
    cycle failure.
  - `examples/75_cross_root_standard_library_imports/` — still uses relative
    imports inside a shared authored library.
  - `examples/100_skill_package_bundled_agents/` and
    `examples/122_skill_package_emit_documents/` — prove that `SKILL.prompt`
    already behaves like a local package root today.
  - `docs/COMPILER_ERRORS.md`, `docs/LANGUAGE_REFERENCE.md`,
    `docs/README.md`, `docs/EMIT_GUIDE.md`, and `examples/README.md` all move
    with the same import/boundary contract.
- **Compatibility posture (separate from `fallback_policy`)**
  - Hard public cutover at language version `4.0` — repo truth already treats
    imports, runtime packages, skill packages, docs, and corpus examples as one
    contract family, so shipping both the module-era and flow-era models would
    create duplicate truth.
  - No accepted feature flag, bridge, or default-flip story — the clean design
    is one compiler path, one boundary model, and one public migration story.
  - Relative-import parsing should leave the grammar in the same cut — keeping
    it around would preserve a fake boundary concept the new model is supposed
    to delete.
- **Existing patterns to reuse**
  - `doctrine/_compiler/indexing.py` — directory-backed `AGENTS.prompt`
    resolution already exists for runtime packages; reuse that discovery shape
    instead of inventing `FLOW.prompt`.
  - `doctrine/_compiler/resolve/refs.py` — declaration kinds such as
    `render_profile` already resolve through the same ref machinery as other
    declarations, so no separate render-profile syntax is needed to move to
    flow ownership.
  - `docs/EMIT_GUIDE.md` plus skill-package examples — `SKILL.prompt` already
    marks a real package root, so the flow model should reuse that boundary
    story rather than create a second skill-specific concept.
- **Duplicate or drifting paths relevant to this change**
  - The current import contract is duplicated across grammar, docs, tests, and
    the proof corpus.
  - Relative imports appear in shipped example surfaces such as
    `examples/03_imports/` and `examples/75_cross_root_standard_library_imports/`.
  - Skill-package imports in `examples/100_skill_package_bundled_agents/` and
    `examples/122_skill_package_emit_documents/` prove that package-local import
    behavior is already part of the shipped language story.
- **Capability-first opportunities before new tooling**
  - Not applicable. This is a compiler/language change, not an agent-capability
    problem.
- **Behavior-preservation signals already available**
  - `make verify-examples` — the main corpus proof and emit snapshot signal.
  - `make verify-diagnostics` — import-diagnostic wording and related-location
    proof.
  - `tests/test_import_loading.py` — current cycle, runtime-package, and
    skill-package behavior anchors.
  - `tests/test_emit_flow.py`, `tests/test_emit_docs.py`, and
    `tests/test_compiler_boundary.py` — emit frontier and runtime-package proof.
  - `docs/VERSIONING.md` plus `tests/test_release_flow.py` — release-surface
    proof when the breaking cut lands.

Repo-settled conclusions from this research pass:

- Keep `AGENTS.prompt` as the flow-root marker for agent/runtime flows. The
  code and docs already use it as the real directory-backed boundary, so adding
  `FLOW.prompt` would introduce a second public boundary file for no grounded
  gain.
- Keep `SKILL.prompt` as the skill-package root and treat its containing
  directory as the package-local flow root. The current loader, docs, and
  examples already behave that way.
- No new author-facing `render_profile` or emit-config syntax is needed for the
  flow change. `render_profile` already resolves through ordinary declaration
  refs, so only the registry owner changes.
- Parallel file parsing inside one flow is a follow-up optimization, not a
  correctness requirement. Current import loading is intentionally serialized to
  avoid cycle deadlocks.
- Public `4.0` should be a clean cutover on relative imports. Any temporary
  parser-level acceptance belongs only to internal migration while the old and
  new pipelines are not both public contracts.

## 3.3 Resolved decisions that shape implementation

- **Ship opt-in `export` in `4.0`.** Declarations are flow-local by default.
  Cross-flow imports may target only exported declarations. This is the
  cleanest real boundary, and it avoids turning every helper in a large flow
  into accidental public API.
- **Choose a declaration-level `export` marker.** One `export` keyword before a
  top-level declaration is the smallest explicit surface. It keeps the public
  contract next to the declaration that owns it and avoids a second listing
  surface.
- **Remove relative imports in the same cut.** No deprecation window, no
  compatibility parse path, and no public dual story.
- **Keep the existing boundary entrypoints.** `AGENTS.prompt` stays the
  agent/runtime flow root. `SKILL.prompt` stays the skill-package source root.
  The compiler should treat both as one class of boundary entrypoint instead of
  adding `FLOW.prompt`.
- **Unify runtime packages and ordinary flows under one boundary model.**
  Runtime packages are flows with runtime emit rules, not a separate namespace
  concept.
- **Do not add new render-profile or emit-config syntax.** The registry owner
  changes; the authored surface does not.
- **Leave parallel file parsing as a follow-up.** It is not required for the
  correctness cut.

This section no longer blocks implementation planning. The remaining work is
execution, not architecture choice.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- A `.prompt` file is still the key indexing unit.
- The compiler treats module paths, not directories, as the main namespace
  owner.
- `AGENTS.prompt` already matters for runtime-package loading, but that
  directory-backed boundary is still a special case inside a file-first model.
- `SKILL.prompt` already marks a skill-package source root, but it is not yet
  implemented as the same general flow concept as runtime roots.

## 4.2 Control paths (runtime)

- `CompilationSession` builds `root_unit` up front and keeps `_module_cache`,
  `_module_loading`, and `_module_waits` keyed by `ModuleLoadKey`.
- `index_unit` builds one `IndexedUnit` per `.prompt` file.
- `_load_module` recursively loads imports, and `load_imports()` stays
  serialized to avoid cycle deadlocks.
- Bare-name resolution checks the current file first, then
  `imported_symbols_by_name`.
- `extract_target_flow_graph_from_units` walks the graph from root agents after
  unit-level indexing.
- `collect_runtime_emit_roots` still walks imported units and treats
  directory-backed runtime packages as a special imported-unit shape.

## 4.3 Object model + key abstractions

- `IndexedUnit` owns the declaration registries today.
- `ModuleLoadKey` identifies file/module loads.
- `ImportDecl` and `ImportPath` carry import syntax, including relative-import
  cases.
- Imported aliases and imported symbols are tracked at the unit level.
- The current model has no explicit exported-vs-internal flow boundary because
  file layout, not flow layout, still carries that job.

## 4.4 Observability + failure behavior today

- `E289 Cyclic import module` catches true module cycles and also the false
  positive sibling-cycle case that motivated this proposal.
- `E280`, `E287`, `E306`, `E307`, and `E308` all currently speak in module or
  imported-symbol terms.
- The current corpus and unit tests prove the shipped behavior today.
- The biggest known failure mode is architectural confusion, not silent success:
  cyclic sibling layouts fail loud instead of hanging.
- The repo already proves two real boundary entrypoints, `AGENTS.prompt` and
  `SKILL.prompt`, but the compiler has not unified them under one namespace
  owner.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. This is a compiler, language, docs, and proof-corpus change.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

A flow is the set of `.prompt` files that compile together under one boundary
entrypoint.

A flow root is the nearest ancestor directory that contains a boundary
entrypoint file:

- `AGENTS.prompt` for agent and runtime flows
- `SKILL.prompt` for skill-package source roots

Every `.prompt` file under that directory belongs to the flow unless a nested
`AGENTS.prompt` or `SKILL.prompt` starts a nested flow.

**Examples**

Single flow, flat layout:

```text
my_flow/
├── AGENTS.prompt
├── producer.prompt
└── critic.prompt
```

Single flow, nested layout:

```text
my_flow/
├── AGENTS.prompt
├── roles/
│   ├── producer.prompt
│   └── critic.prompt
└── contracts/
    └── shared.prompt
```

Two flows, nested:

```text
outer_flow/
├── AGENTS.prompt              # outer flow root
├── outer_agent.prompt
└── inner_flow/
    ├── AGENTS.prompt          # inner flow root (separate flow)
    └── inner_agent.prompt
```

Skill packages (`SKILL.prompt`) already mark their own boundary. Under the
accepted design, the inside of a skill package is a flow whose root is the
`SKILL.prompt` directory.

Runtime packages (directory-backed with `AGENTS.prompt` and one concrete agent)
are not a separate namespace concept. They are flows whose entrypoint is
`AGENTS.prompt` and whose emit rules require one concrete agent.

## 5.2 Control paths (future)

- Resolve the nearest boundary entrypoint directory from any `.prompt` file or
  imported flow path.
- Discover every member `.prompt` file in that flow while skipping nested
  boundary roots, hidden files, symlinks, and editor-backup noise.
- Parse each member file into a thin `IndexedUnit`.
- Merge all top-level declarations into one `IndexedFlow` registry.
- Build a second exported registry from declarations marked `export`.
- Detect sibling collisions during merge before any cross-flow import
  resolution.
- Resolve imports only between flows and only against exported declarations.
- Build the flow graph from `IndexedFlow` plus agent identity instead of
  per-file module identity.
- Retarget emit and verification walkers to `IndexedFlow`.
- Keep one compiler path. No feature flag, no default flip, and no long-lived
  legacy unit path belong in the accepted architecture.

## 5.3 Object model + abstractions (future)

- `IndexedFlow` replaces `IndexedUnit` as the owner of declaration registries,
  export registries, boundary metadata, and member units.
- `IndexedUnit` becomes a thin per-file parse container with source spans and
  local declarations.
- `FlowLoadKey` replaces `ModuleLoadKey`, with flow-root identity instead of
  per-file module identity.
- `CompilationSession.root_unit` becomes `root_flow`, and module caches rename
  to flow caches.
- Bare names resolve against the merged flow registry.
- Qualified refs like `some_flow.Thing` travel through imported-flow
  resolution and may see only exported declarations.
- `ImportDecl` stays as the cross-flow boundary primitive.
- `export_marker` becomes a new declaration-level modifier on top-level
  declarations.

Grammar and language surface under this target:

- `import_decl` stays as the cross-flow import surface.
- `export_marker` is the one new grammar surface in this cut.
- `relative_import_path` and `DOTS` leave the grammar in the same cut.

## 5.4 Invariants and boundaries

- Within one flow, every declaration is visible to every other file by bare
  name. No import is needed.
- Across flows, `import` is the only way to reach another flow's exported
  declarations.
- If two sibling files declare the same name, compilation fails loud with a
  dedicated error pointing at both declaration sites.
- If a bare name could resolve to both a flow-internal declaration and an
  imported symbol, compilation fails loud with `E308`.
- `E289` narrows. It fires only for true cross-flow mutual imports.
- Retired import forms:
  - `import .sibling`
  - `import ..parent`
  - any import whose target resolves to a file in the same flow as the
    importer

Compatibility and cutover story:

- One hard breaking cut from language version `3.0` to `4.0`.
- The same implementation arc deletes relative imports, implicit cross-flow
  visibility, and the old unit-first pipeline.
- If temporary scaffolding exists while code is in flight, it is not part of
  the accepted architecture and must be deleted before the plan is done.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. The author-facing surface is syntax and compiler behavior, not a
runtime UI.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Grammar | `doctrine/grammars/doctrine.lark` | `import_decl`, `export_marker`, `relative_import_path`, `DOTS` | Absolute and relative imports parse today, and there is no export surface | Add `export_marker`, keep only cross-flow import shapes, and delete `relative_import_path` plus `DOTS` in the same cut | `import` must mean real boundary crossing, and the public surface must stay clean | cross-flow imports only; `export` marks the cross-flow surface | `tests/test_compile_diagnostics.py`, `tests/test_flow_namespace.py` |
| Parser + model | `doctrine/parser.py`, `doctrine/_model/core.py` | top-level declaration parsing, `ImportDecl`, `ImportPath` | Parser and model assume current import syntax and no export modifier | Parse `export` on top-level declarations, carry export metadata, and remove relative-import path shapes | keep the new boundary explicit in authored syntax | declaration-level export metadata; no relative-import AST path | parser, source-span, and diagnostics tests |
| Indexing | `doctrine/_compiler/indexing.py` | `IndexedUnit`, `_load_module`, `load_imports`, cycle check, module key, runtime-package root helpers | One indexed unit per file with recursive module loading | Add `IndexedFlow`, boundary-root detection for `AGENTS.prompt` and `SKILL.prompt`, member discovery, parse-then-merge indexing, and cross-flow cycle checks; delete unit-first ownership | remove false-positive sibling cycles and make the namespace owner real | `IndexedFlow`; `FlowLoadKey`; one flow-first compiler path | `tests/test_import_loading.py`, `tests/test_flow_namespace.py`, corpus verification |
| Resolution | `doctrine/_compiler/resolve/refs.py` | `_decl_lookup_targets`, `_resolve_visible_imported_unit`, ambiguity checks | Bare names resolve against the current file plus imported symbols | Resolve bare names against the flow registry, resolve imported lookups against exported declarations only, reject same-flow imports, and retarget `E308` to flow-local vs imported ambiguity | match the new namespace model and make exports real | merged flow registry plus exported registry own lookup | `tests/test_import_loading.py`, `tests/test_compile_diagnostics.py`, `tests/test_review_imported_outputs.py` |
| Flow graph | `doctrine/_compiler/flow.py` | `extract_target_flow_graph_from_units`, graph keys | Flow graph is rooted in units/modules | Re-key graph nodes by flow identity and agent name | keep emitted routing aligned with the new owner boundary | flow-keyed graph | `tests/test_emit_flow.py`, corpus verification |
| Session | `doctrine/_compiler/session.py` | cache fields, `root_unit` | Session caches and root wiring are unit-based | Rename and re-key caches to flow identity and expose `root_flow` | keep one owner model end to end | flow-level session state | `tests/test_import_loading.py`, `tests/test_verify_corpus.py` |
| Emit | `doctrine/emit_common.py` | `collect_runtime_emit_roots` | Walks imported units for runtime packages | Walk imported flows instead and treat runtime packages as ordinary flows with runtime emit rules | keep emit discovery aligned with flow boundaries | imported flows, not imported units | `tests/test_emit_flow.py`, `tests/test_emit_docs.py`, `tests/test_emit_skill.py` |
| Emit | `doctrine/emit_flow.py`, `doctrine/emit_docs.py`, `doctrine/emit_skill.py` | target-level emit entry points | Entry flow resolves through unit-level structures | Retarget to `IndexedFlow` while keeping public emit targets stable | preserve emitted author-facing surfaces | flow-level input, same public emit targets | emit tests and corpus verification |
| Verification | `doctrine/verify_corpus.py` | manifest-backed verification session | Builds sessions around the current unit model | Use the flow-based session path without changing the public command | keep shipped proof aligned | same public runner, new flow-backed internals | `make verify-examples`, targeted manifest runs |
| Diagnostics | `docs/COMPILER_ERRORS.md`, compiler diagnostics call sites | `E280`, `E287`, `E289`, `E306`, `E307`, `E308`, new export and same-flow-import errors | Errors still describe module-era behavior | Rewrite messages and meanings for flow-era behavior, retire `E306`, and add fail-loud missing-export and same-flow-import errors | authors need accurate fail-loud guidance | flow-aware diagnostics | diagnostics formatting tests, docs review, `make verify-diagnostics` |
| Examples | `examples/03_imports/`, `04`, `14`, `15`, `16`, `17`, `30`, `86`, `109`, `115`, `100`, `122+` | import-heavy fixtures and refs | Several examples teach or rely on intra-flow imports | Delete sibling imports, add `export` where cross-flow access remains, keep real cross-flow imports, and add new proof examples | shipped corpus must teach the new mental model | sibling-sharing proof, explicit export proof, cross-flow-only import teaching | `make verify-examples` |
| Tests | `tests/test_import_loading.py`, `tests/test_compile_diagnostics.py`, `tests/test_review_imported_outputs.py`, emit tests | import-era fixtures and assertions | Current tests encode module-era failure modes and wording | Delete obsolete sibling-cycle tests, retarget cross-flow cases, add new flow-namespace and export-boundary tests, and audit fixtures for hidden collisions | proof must match shipped behavior | flow-aware test corpus | unittest targets plus `make verify-examples` |
| Docs and release | `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/EMIT_GUIDE.md`, `examples/README.md`, `docs/VERSIONING.md`, `CHANGELOG.md`, `README.md`, `PRINCIPLES.md`, `AGENTS.md`, `docs/README.md`, `docs/FAIL_LOUD_GAPS.md`, related notes docs | language and release surfaces | Docs still describe the module-era import story | Rewrite docs, versioning, and release payload to match the breaking flow story and the new `export` rule | shipped truth must stay aligned | language `4.0`, next major release | `make verify-package` when package/public install surfaces change; manual docs review |

## 6.2 Migration notes

**Canonical owner path / shared code path**

- namespace discovery and flow merge: `doctrine/_compiler/indexing.py`
- bare-name and imported-flow resolution: `doctrine/_compiler/resolve/refs.py`
- flow graph identity: `doctrine/_compiler/flow.py`
- session identity: `doctrine/_compiler/session.py`
- emit-time root walking: `doctrine/emit_common.py`
- export parsing and declaration metadata: `doctrine/grammars/doctrine.lark`,
  `doctrine/parser.py`, and `doctrine/_model/core.py`

**Retired surfaces**

- `relative_import_path` and `DOTS`
- implicit cross-flow visibility
- unit-first compiler ownership
- `E306 Duplicate module alias`

**Delete list**

- remove `relative_import_path` and `DOTS` in the same cut
- remove the old unit-based pipeline in the same implementation arc
- the two obsolete cyclic-sibling tests in `tests/test_import_loading.py`
- retired `E306 Duplicate module alias` wording and fixtures
- any intra-flow import fixtures that only exist to prove the old model
- any temporary compatibility hook or local scaffold that would preserve the
  old boundary story

**Examples that need rewrites**

- `examples/03_imports/` — heavy rewrite. It is the canonical import tutorial
  today. Retarget it in place to teach cross-flow imports only. Delete the
  `cyclic_siblings/` test case. Retire the relative-import tests.
- `examples/04_inheritance/` — drop 2 imports.
- `examples/14_handoff_truth/` — drop 5 imports. This becomes the clean
  flat-layout reference.
- `examples/15_workflow_body_refs/` — drop 1 import.
- `examples/16_workflow_string_interpolation/` — drop 2 imports.
- `examples/17_agent_mentions/` — drop 2 imports.
- `examples/30_law_route_only_turns/` — drop 1 import.
- `examples/86_imported_review_comment_local_routes/` — drop 1 import and
  verify the routed-owner binding behavior survives.
- `examples/109_imported_review_handoff_output_inheritance/` — drop 1 import.

**Cross-flow examples that stay, but may need adjustment**

- `examples/115_runtime_agent_packages/` — `writer_home` and `editor_home`
  still cross real boundaries and should remain the exemplar for cross-flow
  imports.
- `examples/100_skill_package_bundled_agents/` plus related skill-package emit
  examples such as `122`, `123`, and `124` — remove intra-skill-flow imports,
  keep cross-skill references, and audit each surface.

**New examples to add**

- `129_flow_sibling_namespace`
- `130_cyclic_producer_critic`
- `131_cross_flow_import`
- `132_flow_sibling_collision`
- `133_intra_flow_import_retired`
- `134_flow_export_boundary`

**Tests to delete**

- `tests/test_import_loading.py::test_sibling_import_cycle_fails_loud_instead_of_hanging`
- `tests/test_import_loading.py::test_concurrent_top_level_module_load_cycle_fails_loud_instead_of_deadlocking`

**Tests to rewrite**

- `tests/test_import_loading.py::test_module_alias_and_symbol_imports_resolve_through_existing_name_ref_paths`
- `tests/test_import_loading.py::test_from_import_does_not_make_the_module_path_visible`
- `tests/test_import_loading.py::test_file_and_directory_module_collision_fails_loud`
- `tests/test_import_loading.py::test_ambiguous_module_across_configured_and_provider_roots_fails_loud`
- `tests/test_import_loading.py::test_skill_package_entrypoint_fails_loud_on_local_import_collision`
- `tests/test_compile_diagnostics.py::test_missing_import_points_at_import_line`
- `tests/test_compile_diagnostics.py::test_duplicate_module_alias_reports_related_location`
  - source disposition: delete or retarget because `E306` retires
- `tests/test_compile_diagnostics.py::test_duplicate_imported_symbol_reports_related_location`
- `tests/test_compile_diagnostics.py::test_imported_symbol_ownership_conflict_reports_related_location`
- `tests/test_review_imported_outputs.py::test_imported_review_comment_output_can_bind_local_routed_agents`
- `tests/test_review_imported_outputs.py::test_imported_review_comment_output_can_feed_split_final_output_trust_surface`
- `tests/test_diagnostics_formatting.py::test_diagnostic_to_dict_keeps_related_locations_json_safe`

**Tests to keep and audit**

- Keep the prompt-root, runtime-package, provider-root, and skill-package
  entrypoint cases in `tests/test_import_loading.py`.
- Keep `tests/test_release_flow.py`.
- Keep most of `tests/test_compile_diagnostics.py` and audit fixtures for
  accidental sibling collisions.
- Audit `tests/test_emit_flow.py`, `tests/test_emit_docs.py`,
  `tests/test_emit_skill.py`, `tests/test_parser_source_spans.py`,
  `tests/test_verify_corpus.py`, `tests/test_compiler_boundary.py`, and
  `tests/test_project_config.py`.
- Add `tests/test_flow_namespace.py` with the proof cases named in the source
  proposal.

**Docs that need rewrites or scans**

- `docs/LANGUAGE_REFERENCE.md` — rewrite the imports section
- `docs/LANGUAGE_DESIGN_NOTES.md` — add a "Flows and file layout" section
- `docs/COMPILER_ERRORS.md` — rewrite E280-E290 and E306-E308; add new codes
- `docs/VERSIONING.md` — language version `3.0 -> 4.0`; required breaking
  payload
- `docs/EMIT_GUIDE.md` — update cross-root compile config and runtime-package
  guidance
- `examples/README.md` — update `03_imports` narrative and add new corpus
  entries
- `README.md` — minor flow mention if the feature summary needs it
- `PRINCIPLES.md` — optional clarification about boundary meaning
- `AGENTS.md` — shipped-truth note and docs-map update if the proposal lands
- `docs/README.md` — add the new or successor reference
- `docs/FAIL_LOUD_GAPS.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`,
  `docs/AUTHORING_PATTERNS.md`, `docs/THIN_HARNESS_FAT_SKILLS.md` — scan for
  import-related examples and adjust

**Relevant current code locations from the source proposal**

- `doctrine/_compiler/indexing.py` — module loading, `E289` detection,
  declaration registration, `load_imports`, module-key scheme, concurrency
- `doctrine/_compiler/resolve/refs.py` — name resolution, ambiguity,
  skill-package scan
- `doctrine/_compiler/flow.py` — flow-graph extraction, cross-module walk
- `doctrine/_compiler/session.py` — session cache, `root_unit` wiring
- `doctrine/_model/core.py` — `ImportDecl`, `ImportPath`
- `doctrine/emit_common.py` — runtime-package walk, `EmitTarget`
- `doctrine/emit_flow.py`, `doctrine/emit_docs.py`, `doctrine/emit_skill.py`
  — target-level emit entry points
- `doctrine/verify_corpus.py` — manifest runner
- `doctrine/grammars/doctrine.lark` — import productions
- `doctrine/parser.py` — top-level declaration parsing
- `docs/COMPILER_ERRORS.md` — import-related errors

Compatibility posture and migration summary:

- This cannot ship as a patch or minor.
- A Doctrine `3.0` project migrates by identifying flows, deleting intra-flow
  imports, adding `export` to the declarations that truly cross boundaries,
  renaming sibling collisions, keeping cross-flow imports, and running the
  standard verify command.
- The migration should be mostly deletion-driven. No silent behavior change is
  allowed.

**Behavior-preservation signals for refactors**

- `make verify-examples`
- `make verify-diagnostics` when diagnostics change
- targeted unittest coverage for import loading, flow namespace cases, emit
  paths, review-imported outputs, and release flow when touched

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Boundary roots | `doctrine/_compiler/indexing.py`, `docs/EMIT_GUIDE.md`, skill-package examples | one boundary-entrypoint discovery rule for `AGENTS.prompt` and `SKILL.prompt` | avoids keeping runtime roots and skill roots as separate namespace stories | include |
| Cross-flow visibility | grammar, parser/model, resolver, examples `115`, `100`, `122+` | explicit `export` before any declaration that crosses a flow boundary | avoids accidental public API drift as flows get larger | include |
| Import diagnostics | compiler diagnostics, `docs/COMPILER_ERRORS.md`, diagnostics tests | flow-era wording and related locations | avoids docs/tests continuing to describe file-era or flat-export behavior | include |
| Emit ownership | `doctrine/_compiler/flow.py`, `doctrine/emit_common.py`, emit tests | `IndexedFlow` as the owner path for graph and emit traversal | avoids a split between compile-time flow ownership and emit-time unit ownership | include |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 - Root the language in flows, not files

**Goal**

Make the flow the real namespace owner everywhere the compiler currently treats
the file as the owner.

**Work**

Build the new boundary model at the grammar, parser, indexing, and session
layers first. Do not keep a second long-lived compiler path alive beside it.

Status: COMPLETE (fresh audit verified 2026-04-18)

Completed work:

- Added `export` to the grammar as a top-level declaration modifier.
- Removed relative-import syntax from the shipped grammar surface.
- Updated parser output so exported declarations stay unwrapped in
  `PromptFile.declarations` while `PromptFile.exported_names` records the
  cross-flow public surface.
- Added Phase 1 flow-boundary helpers in `doctrine/_compiler/indexing.py`:
  `resolve_flow_entrypoint`, `discover_flow_members`, and `build_indexed_flow`.
- Added `tests/test_flow_namespace.py` for export parsing and flow-root
  discovery.
- Reworked `build_indexed_flow` into a real parse-then-merge owner:
  it now merges one boundary root into `IndexedFlow`, records declaration-owner
  units, and resolves same-flow imports against the already-indexed member set.
- Re-keyed `CompilationSession` around `root_flow` and flow caches.
  `load_module` now resolves through flow ownership instead of unit caches.
- Moved compile entry selection onto `root_flow` registries for root agents,
  readable declarations, and skill packages.
- Expanded the targeted proof to cover `root_flow` ownership and same-flow
  sibling import loading.
- Taught `CompilationSession` to honor the authored in-memory `PromptFile`
  object for the active source path while it builds `root_flow`.
- Split sibling `AGENTS.prompt` and `SOUL.prompt` files into separate runtime
  flows so peer runtime entrypoints do not merge into one namespace.
- Removed the shipped module-era owner aliases by deleting `ModuleLoadKey`,
  dropping `root_unit` from the public and session surfaces, and retargeting
  flow, output-validation, docs, flow emit, and corpus helpers to
  `root_flow` / `root_entrypoint_unit`.
- Cached the active `root_flow` inside `CompilationSession` so same-flow
  resolution and validation stay on the in-memory prompt graph instead of
  reparsing stale disk state.
- Moved per-unit declaration and import bundles off the `IndexedUnit` dataclass
  fields and onto `IndexedFlow` maps keyed by member path.
- Deleted the remaining `IndexedUnit` compatibility bridge for
  `unit.declarations`, `unit.loaded_imports`, and flattened `unit.*_by_name`
  lookups, and moved the last owner-sensitive compiler reads onto explicit
  flow-owned helpers.

Verification:

- `uv run --locked python -m unittest tests.test_flow_namespace tests.test_parser_source_spans`
- `uv run --locked python -m unittest tests.test_flow_namespace tests.test_parser_source_spans tests.test_import_loading`
- `uv run --locked python -m unittest tests.test_compile_diagnostics.CompileDiagnosticTests.test_guard_shell_without_when_reports_guard_line_for_agent_compile tests.test_compile_diagnostics.CompileDiagnosticTests.test_guard_shell_without_when_reports_guard_line_for_declaration_compile tests.test_compile_diagnostics.CompileDiagnosticTests.test_workflow_readable_sequence_invalid_item_points_at_block_line tests.test_compile_diagnostics.CompileDiagnosticTests.test_workflow_readable_image_payload_shape_points_at_block_line tests.test_compile_diagnostics.CompileDiagnosticTests.test_workflow_unknown_readable_block_kind_reports_internal_error_with_block_line tests.test_compile_diagnostics.CompileDiagnosticTests.test_document_definitions_invalid_entry_points_at_definition_line tests.test_compile_diagnostics.CompileDiagnosticTests.test_analysis_empty_basis_points_at_statement_line`
- `uv run --locked python -m unittest tests.test_flow_namespace tests.test_import_loading tests.test_compile_diagnostics tests.test_emit_docs tests.test_emit_flow tests.test_output_schema_lowering tests.test_output_schema_validation`
- `uv run --locked python -m unittest tests.test_flow_namespace tests.test_import_loading tests.test_compile_diagnostics`
- `make verify-examples`
- `make verify-diagnostics`

Still todo in this phase:

- None. Fresh 2026-04-18 audit confirmed the owner-path cleanup and exit
  criteria.

**Checklist (must all be done)**

- Add `export` as a top-level declaration modifier.
- Remove `relative_import_path` and `DOTS` from the grammar.
- Update `doctrine/parser.py` and `doctrine/_model/core.py` so top-level
  declarations can carry export metadata and relative-import path shapes are
  gone.
- Introduce `IndexedFlow`.
- Convert `IndexedUnit` into a thin per-file parse container.
- Add one boundary-root discovery rule for `AGENTS.prompt` and `SKILL.prompt`.
- Exclude nested boundary roots from a parent flow's member set.
- Add explicit filtering for hidden files, symlinks, and editor-backup noise.
- Replace the recursive file/module owner path with parse-first then merge.
- Re-key session identity from `root_unit` and module caches to `root_flow` and
  flow caches.
- Delete module-first ownership as the accepted design center.

**Verification (required proof)**

- Targeted parser, source-span, indexing, and session tests.
- Targeted unit tests for flow discovery and nested-root exclusion.

**Docs/comments (propagation; only if needed)**

- Add a short code comment where boundary-root discovery or filtering rules
  would be easy to misread later.

**Exit criteria (all required)**

- The compiler can build a merged `IndexedFlow` for one boundary root.
- `export` parses and carries through the model layer.
- Relative-import grammar is gone.
- No second accepted compiler path remains in the design.

**Rollback**

- If this phase is incomplete, keep the plan active and do not claim the new
  architecture is live.

## Phase 2 - Retarget resolution, imports, flow graph, and emit

**Goal**

Make lookup, imports, graph extraction, and emit all follow the same flow-owned
boundary model.

**Work**

Push the semantic cut through resolution and traversal so the compiler speaks
one boundary story end to end.

Status: COMPLETE (fresh audit verified 2026-04-18)

Completed work:

- Retargeted the red compile-diagnostics fixtures in `examples/45`, `46`,
  `47`, and `49` into nested flow roots so each invalid prompt compiles inside
  one truthful boundary under the new model.
- Fixed skill-package nested prompt compilation to resolve the bundled prompt
  through its owning flow unit instead of treating the package root file as the
  only live owner.
- Fixed runtime-package emit handling so sibling `SOUL.prompt` files compile as
  their own runtime entrypoints instead of colliding with `AGENTS.prompt`.
- Added `tests/test_flow_namespace.py` coverage that proves peer `SOUL.prompt`
  files are excluded from an `AGENTS.prompt` flow and that `SOUL.prompt` can be
  resolved as an explicit runtime entrypoint.
- Retargeted generic bare-name declaration lookup onto the owning
  `IndexedFlow`, so sibling declarations in one flow resolve without same-flow
  imports.
- Taught skill-package resolution scans to treat the whole local flow as the
  visible surface instead of only the current file.
- Retargeted same-flow resolution helpers onto the active session cache, which
  keeps workflow-readable and guard-shell validation on the live in-memory
  flow graph during compile-time mutations.
- Reworked runtime emit-root discovery into a depth-first flow walk, so
  same-flow imports can surface nested runtime packages in first-seen graph
  order without falling back to module-era root ownership.
- Retargeted the remaining review, route-only, schema-artifact, review-key,
  and final-output contract helpers onto flow-owned input and output lookups,
  so sibling-file declarations stay visible inside one flow and imported flows
  can export declarations from sibling files instead of only from
  `AGENTS.prompt`.
- Added focused proof that same-flow review contracts can bind sibling-file
  inputs and outputs, and that imported review comment outputs still work when
  the exported declaration lives in a sibling file under the imported flow
  root.
- Re-keyed flow-graph extraction, docs emit previous-turn context wiring, and
  D2 layout identity onto flow-owned `(prompt_root, flow_root, name)` keys, so
  imported sibling-named agents and artifacts no longer collide under
  module-only graph identity.
- Retargeted runtime emit-root discovery and dedupe to flow-aware unit
  ownership, and stopped helper-only imported runtime packages from failing
  loud when they contribute no concrete agent entrypoint.
- Deleted the last direct unit-owned import-table and declaration-registry
  reads in the shared resolver and validator helpers, so lookup paths now go
  through `unit_declarations(...)` and `unit_loaded_imports(...)` instead of
  asking the thin carrier for namespace ownership.
- Retargeted skill-package id resolution and emitted-document lookup to the
  owning flow registry, so same-flow package refs and public-install builds no
  longer depend on retired unit passthrough state.

Verification:

- `uv run --locked python -m unittest tests.test_compile_diagnostics`
- `uv run --locked python -m unittest tests.test_flow_namespace tests.test_emit_docs tests.test_emit_skill`
- `uv run --locked python -m unittest tests.test_flow_namespace tests.test_parser_source_spans tests.test_import_loading tests.test_compile_diagnostics tests.test_review_imported_outputs tests.test_emit_flow tests.test_emit_docs tests.test_emit_skill`
- `uv run --locked python -m unittest tests.test_flow_namespace tests.test_import_loading`
- `uv run --locked python -m unittest tests.test_flow_namespace tests.test_import_loading tests.test_compile_diagnostics tests.test_emit_docs tests.test_emit_flow tests.test_output_schema_lowering tests.test_output_schema_validation`
- `uv run --locked python -m unittest tests.test_flow_namespace tests.test_review_imported_outputs tests.test_import_loading tests.test_compile_diagnostics`
- `uv run --locked python -m unittest tests.test_emit_flow tests.test_emit_docs tests.test_output_rendering`
- `uv run --locked python -m unittest tests.test_flow_namespace tests.test_import_loading tests.test_compile_diagnostics tests.test_review_imported_outputs tests.test_emit_flow tests.test_emit_docs tests.test_output_rendering`
- `make verify-diagnostics`
- `make verify-examples`

Still todo in this phase:

- None. Fresh 2026-04-18 audit confirmed the flow-owned lookup, diagnostics,
  graph, and emit exit criteria.

**Checklist (must all be done)**

- Resolve bare names against the merged flow registry.
- Resolve imported lookups against exported declarations only.
- Reject same-flow imports with a dedicated fail-loud diagnostic.
- Narrow `E289` to true cross-flow cycles.
- Retarget `E280`, `E287`, `E307`, and `E308` to flow-era wording and
  behavior.
- Retire `E306 Duplicate module alias`.
- Add new sibling-collision, missing-export, and same-flow-import-retired
  diagnostics with real related locations.
- Re-key flow graph extraction to `IndexedFlow` plus agent identity.
- Retarget runtime emit-root discovery to imported flows instead of imported
  units.
- Make skill-package and runtime-package boundary handling match the accepted
  flow model.

**Verification (required proof)**

- `make verify-diagnostics` when diagnostics change.
- Retargeted unit tests in `tests/test_import_loading.py`,
  `tests/test_compile_diagnostics.py`, `tests/test_review_imported_outputs.py`,
  `tests/test_emit_flow.py`, `tests/test_emit_docs.py`, and
  `tests/test_emit_skill.py`.
- New `tests/test_flow_namespace.py` cases for sibling visibility, collision,
  same-flow import retirement, export boundary, cross-flow cycle, and `E308`
  ambiguity.

**Docs/comments (propagation; only if needed)**

- Update comments at the canonical lookup, emit, or diagnostics boundary if
  they would otherwise describe the old module model.

**Exit criteria (all required)**

- Intra-flow sibling cycles no longer fail as module cycles.
- Cross-flow imports see only exported declarations.
- True cross-flow cycles still fail loud.
- Graph extraction and emit traversal consume `IndexedFlow`.

**Rollback**

- If this phase is incomplete, do not move on to corpus or docs claims.

## Phase 3 - Rewrite the proof corpus and test surfaces

**Goal**

Make the shipped examples and tests teach and prove the new model instead of
the old one.

**Work**

Rewrite the import-era fixtures, add the new proof cases, and regenerate
expected artifacts where the emitted truth changed.

Status: COMPLETE (fresh audit verified 2026-04-18)

Completed work:

- Repartitioned the import-era example corpus onto real flow roots so invalid
  siblings no longer poison unrelated cases under one directory-wide
  namespace.
- Rewrote `examples/03_imports/` to teach dotted cross-flow imports without
  relative-import syntax and to prove real cross-flow cycle handling.
- Retargeted the reusable import examples in `examples/69`, `70`, and `75`
  onto explicit helper flows with exported declarations.
- Deleted same-flow skill-package imports from the host-binding corpus and from
  the emit and diagnostics smoke fixtures, then regenerated the affected
  checked-in contract truth.
- Repaired moved fixture paths across the shipped manifests and smoke checks so
  repo proof now follows the repartitioned corpus layout.
- Rewrote the remaining same-flow import-era emit and output-rendering tests to
  use bare same-flow refs and real helper flow roots where cross-flow proof is
  still needed.
- Regenerated the checked-in flow-render build snapshots that changed under the
  new flow-keyed D2 identity model in `examples/36`, `73`, and `115`.
- Added the planned `129` through `134` example set to prove the flat sibling
  namespace, producer and critic cycle, honest cross-flow import boundary,
  sibling collisions, retired same-flow imports, and export-gated cross-flow
  visibility.
- Updated `examples/README.md` so the shipped corpus index names the new
  flow-era examples and their proof purpose.

**Checklist (must all be done)**

- Rewrite the existing example directories listed in Section 6.2.
- Keep cross-flow example surfaces that are still valid, with any needed
  `export` updates.
- Add the new `129` through `134` examples.
- Delete obsolete sibling-import fixtures and relative-import teaching cases.
- Audit emit and compiler fixtures for accidental sibling collisions.
- Regenerate `ref/` and `build_ref/` snapshots where the boundary model changed
  emitted output.

**Verification (required proof)**

- `make verify-examples`
- targeted manifest-backed example verification during iteration when helpful
- targeted unittest coverage for import loading, emit, and review-imported
  outputs when fixtures move
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/03_imports/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/69_case_selected_review_family/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/70_route_only_declaration/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/75_cross_root_standard_library_imports/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/124_skill_package_host_binding/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/48_review_inheritance_and_explicit_patching/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/129_flow_sibling_namespace/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/130_cyclic_producer_critic/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/131_cross_flow_import/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/132_flow_sibling_collision/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/133_intra_flow_import_retired/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/134_flow_export_boundary/cases.toml`

**Docs/comments (propagation; only if needed)**

- Update example-local notes only where they would otherwise teach the old
  model.

Still todo in this phase:

- None. Fresh 2026-04-18 audit confirmed the shipped corpus and example exit
  criteria.

**Exit criteria (all required)**

- The shipped corpus passes.
- The new examples prove sibling visibility, export boundaries, and real
  cross-flow imports.
- No shipped example still teaches intra-flow imports as the normal pattern.

**Rollback**

- If corpus proof is red, do not claim the language cut is complete.

## Phase 4 - Rewrite docs, migration guidance, and release surfaces

**Goal**

Bring the shipped documentation and release story in line with the new language
model.

**Work**

Rewrite the language and error docs, add the breaking payload, and scan the
surrounding doctrine docs for stale module-era examples.

Status: COMPLETE (fresh audit verified 2026-04-18)

Completed work:

- Rewrote much of the public import guidance in `docs/LANGUAGE_REFERENCE.md`
  around flow roots, bare same-flow refs, `export`-gated cross-flow
  visibility, and retired same-flow imports.
- Updated `docs/COMPILER_ERRORS.md` for the flow-era import surface by
  retiring `E306` from the shipped catalog and documenting `E314`, `E315`,
  and `E316` plus the newer `E307` and `E308` wording.
- Updated `docs/README.md`, `AGENTS.md`, and `examples/README.md` so repo
  truth, corpus scope, and the numbered example index now point at the
  flow-root namespace story.
- Added the planned `4.0` breaking payload draft to `CHANGELOG.md` and
  updated `docs/VERSIONING.md` to classify the flow-root namespace cut as a
  breaking language move from `3.0` to `4.0`.
- Removed same-flow `from refs... import ...` lines from the first-party
  `agent-linter` and `doctrine-learn` skill-package flows, updated the
  matching `emit_skill` proof fixtures, and got the checked public-install
  package proof back to green.
- Extended the late doc sweep by making the live language version line truthful
  in `docs/VERSIONING.md`, retiring the last relative-import guidance in
  `docs/EMIT_GUIDE.md`, adding a flow-boundary note to
  `docs/LANGUAGE_DESIGN_NOTES.md`, and fixing stale import-era wording in
  `docs/REVIEW_SPEC.md` and `docs/AUTHORING_PATTERNS.md`.
- Finished the remaining public doc cleanup in `docs/LANGUAGE_REFERENCE.md`
  and `docs/SKILL_PACKAGE_AUTHORING.md`, so both guides now teach bare
  same-flow refs inside one flow, cross-flow `import` only at real
  boundaries, and no retired relative-import syntax.
- Rewrote the bundled `doctrine-learn` references to the flow-root model,
  refreshed the checked `skills/.curated/doctrine-learn/` install tree, and
  aligned the teaching ladder with the `01` through `134` corpus.

**Checklist (must all be done)**

- Rewrite `docs/LANGUAGE_REFERENCE.md` imports and `export` guidance.
- Add flow-boundary guidance to `docs/LANGUAGE_DESIGN_NOTES.md`.
- Rewrite `docs/COMPILER_ERRORS.md` for the flow-era diagnostics.
- Update `docs/EMIT_GUIDE.md`.
- Update `examples/README.md`.
- Update `README.md`, `PRINCIPLES.md`, `AGENTS.md`, and `docs/README.md` if
  they still teach or imply the old model.
- Scan `docs/FAIL_LOUD_GAPS.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`,
  `docs/AUTHORING_PATTERNS.md`, and `docs/THIN_HARNESS_FAT_SKILLS.md`.
- Update `docs/VERSIONING.md` for language version `4.0`.
- Add the required breaking-change payload to `CHANGELOG.md`.

**Verification (required proof)**

- `make verify-diagnostics` if doc-linked diagnostics text changed with code
- `make verify-package` if package metadata, publish-flow, or public-install
  surfaces changed
- reviewer pass over the changed docs to confirm one consistent boundary story

Verification:

- Fresh 2026-04-18 audit confirmed the Phase 4 doc surfaces now match the
  flow-root compiler and corpus story, and that the remaining frontier moved
  entirely into Phase 5 release completion.
- `make verify-package`
- `uv run --locked python -m unittest tests.test_release_flow`
- Focused readback over `docs/LANGUAGE_REFERENCE.md`,
  `docs/SKILL_PACKAGE_AUTHORING.md`, and the rewritten bundled
  `doctrine-learn` refs

**Docs/comments (propagation; only if needed)**

- This phase is the docs propagation phase. No stale shipped doc should survive
  after it.

Still todo in this phase:

- None. Fresh local proof closed the remaining stale teaching surfaces.

**Exit criteria (all required)**

- Shipped docs describe the same boundary model as the compiler and examples.
- Versioning and changelog payloads reflect a breaking release truthfully.
- The public migration story includes deleting same-flow imports and adding
  `export` where a declaration truly crosses a boundary.

**Rollback**

- Do not cut a release with mixed old and new docs.

## Phase 5 - Final delete sweep and release proof

**Goal**

Finish the hard cut cleanly and prove the release candidate end to end.

**Work**

Delete any dead unit-era code or doc residue, run the full shipped proof set,
and tag the major release only from a clean state.

Status: COMPLETE (fresh audit verified 2026-04-18)

Completed work:

- Finalized the local release-candidate surfaces by updating
  `[project].version` in `pyproject.toml` to `4.0.0` and promoting the
  breaking flow-namespace payload from `## Unreleased` to
  `## v4.0.0 - 2026-04-18` in `CHANGELOG.md`.
- Fixed the `v4.0.0` changelog release header to the exact single-line field
  shape that `make release-tag` reads back during tag preflight.
- Re-ran the full Phase 5 proof set from that finalized tree:
  `uv sync`, `npm ci`, `uv run --locked python -m unittest tests.test_package_release`,
  `uv run --locked python -m unittest tests.test_release_flow`,
  `make verify-examples`, `make verify-diagnostics`, and `make verify-package`.
- Committed the clean release-candidate tree and cut the signed annotated
  `v4.0.0` tag from commit `08330e6`, then pushed that tag to `origin`.

**Checklist (must all be done)**

- Delete any remaining unit-first ownership code, temporary scaffold, or stale
  live comment that preserves the old boundary story.
- Re-run the full shipped verification set for the release candidate.
- Finalize `docs/VERSIONING.md` and `CHANGELOG.md`.
- Record the completed hard-cut sequence in the Decision Log.
- Cut the next major release tag.

**Verification (required proof)**

- `uv sync`
- `npm ci`
- `make verify-examples`
- `make verify-diagnostics` when diagnostics changed
- `uv run --locked python -m unittest tests.test_release_flow` when release flow
  changed
- `make verify-package` for package metadata, publish-flow, or public-install
  work

Verification:

- `uv sync`
- `npm ci`
- `uv run --locked python -m unittest tests.test_package_release`
- `uv run --locked python -m unittest tests.test_release_flow`
- `make verify-examples`
- `make verify-diagnostics`
- `make verify-package`
- `make release-tag RELEASE=v4.0.0 CHANNEL=stable`
- `git tag --list 'v4.0.0'`
- `git rev-list -n 1 v4.0.0`

**Docs/comments (propagation; only if needed)**

- Delete any stale live comment or doc that still describes the retired path.

Still todo in this phase:

- None. Fresh 2026-04-18 audit confirmed the release cut and closed the plan.

**Exit criteria (all required)**

- No retired pipeline, temporary scaffold, or stale public boundary story
  remains in shipped code or docs.
- The major release carries the matching language and changelog payload.
- The public migration story is explicit and accurate.

**Rollback**

- If release proof fails, do not ship.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Add `tests/test_flow_namespace.py`.
- Rewrite the affected import-loading and diagnostics tests so they prove the
  flow-era contract.
- Keep diagnostics related-location formatting safe.
- Run `make verify-diagnostics` when diagnostics change.
- Run `uv run --locked python -m unittest tests.test_release_flow` when the
  release-flow surface changes.

## 8.2 Integration tests (flows)

- `make verify-examples` is the main proof signal.
- Audit and run the emit tests:
  - `tests/test_emit_flow.py`
  - `tests/test_emit_docs.py`
  - `tests/test_emit_skill.py`
- Audit and run the boundary/corpus-facing tests:
  - `tests/test_verify_corpus.py`
  - `tests/test_compiler_boundary.py`
  - `tests/test_project_config.py`
  - `tests/test_review_imported_outputs.py`
- Use `uv run --locked python -m doctrine.verify_corpus --manifest ...` for
  targeted iteration on one manifest-backed example when that is the cheapest
  proof.

## 8.3 E2E / device tests (realistic)

There is no UI/device surface here. The realistic end-to-end proof is:

- a migrated corpus
- a release candidate that passes the shipped verify commands
- a short author-migration walkthrough that follows the new diagnostics:
  1. identify flows by `AGENTS.prompt` or `SKILL.prompt`
  2. delete intra-flow imports
  3. add `export` to the declarations that really cross boundaries
  4. rename sibling collisions if they appear
  5. keep cross-flow imports
  6. run `make verify-examples` or the project-local verify command

Negative-value proof to avoid:

- deletion-proof tests
- doc-inventory gates
- stale-term greps
- repo-shape policing
- visual-constant checks

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

The accepted rollout is a hard-cut implementation arc:

1. land the flow-root grammar, parser, indexing, and session model
2. retarget resolution, emit, and diagnostics to flow ownership plus `export`
3. migrate the shipped corpus and tests
4. rewrite docs and release surfaces
5. delete any dead unit-era residue and cut `4.0`

There is no accepted feature flag, default-flip phase, or public bridge in this
plan.

## 9.2 Telemetry changes

No product telemetry change is required by the proposal.

Operational visibility will come from:

- fail-loud compiler diagnostics
- the shipped proof corpus
- release verification commands

If the implementation decides to warn on very large flows, the source proposal
suggests recording that in `docs/FAIL_LOUD_GAPS.md`.

## 9.3 Operational runbook

Implementation and release operators should follow this sequence:

1. `uv sync`
2. `npm ci`
3. implement the accepted phase frontier in Section 7
4. run `make verify-examples`
5. run `make verify-diagnostics` when diagnostics changed
6. run `uv run --locked python -m unittest tests.test_release_flow` when
   release-flow work changed
7. run `make verify-package` when package metadata, publish-flow, or
   public-install work changed
8. finalize `docs/VERSIONING.md` and `CHANGELOG.md`
9. tag the next major release

Author migration guidance from the source proposal:

1. Identify flows. Each directory containing `AGENTS.prompt` or `SKILL.prompt`
   is a flow root.
2. Delete intra-flow imports. Remove any `import .x`, `import ..y`, or absolute
   imports that resolve to a sibling file in the same flow.
3. Add `export` to the declarations that truly cross flow boundaries.
4. Rename collisions. If two sibling files declare the same name, rename one.
5. Keep cross-flow imports. Imports that cross flow boundaries stay unchanged.
6. Run `make verify-examples` or the project-local verify command. Errors
   should cite actionable new codes. No silent behavior change is allowed.

# 10) Decision Log (append-only)

## 2026-04-18 - Cut the signed `v4.0.0` tag from the clean hard-cut release tree

**Context**

Phase 5 had been reduced to the real release cut. The release-candidate tree
was already green, but the first tag attempt failed because the `v4.0.0`
changelog header wrapped required release fields across lines. After fixing
that helper-shape mismatch and re-running the release proof, the clean tree was
ready for the actual public tag cut.

**Options**

- keep the local `4.0.0` surfaces green but stop again without a real public
  tag
- fix the helper-facing changelog shape, re-prove the release surfaces,
  commit that repair, and cut the signed public tag now
- bypass the release helper and create an ad hoc tag by hand

**Decision**

Take the real hard-cut finish. Fix the changelog header to the exact helper
shape, rerun the release proof, commit the repair, and cut the signed
annotated `v4.0.0` tag through `make release-tag`.

**Consequences**

- The hard-cut release now exists as signed tag `v4.0.0`.
- The tag points at clean commit `08330e6`.
- The implementation frontier is finished on the code side; only fresh audit
  closeout remains before the plan can be marked complete.

**Follow-ups**

- Run one fresh implementation audit pass.
- Let that audit close the plan and clear the loop if no hidden frontier
  remains.

## 2026-04-17 - Reformat the proposal into the canonical arch-step artifact

**Context**

The source document was a detailed freeform proposal. It already contained the
real rollout, compiler, docs, example, test, and migration content, but it did
not use the canonical full-arch scaffold.

**Options**

- leave the freeform proposal in place
- reformat it into the canonical artifact without changing plan intent

**Decision**

Reformat it in place. Keep the plan in `draft`. Preserve the open decisions as
blockers instead of silently choosing them during reformat.

**Consequences**

- The proposal now has a stable TL;DR, North Star, call-site audit, and phase
  plan.
- Later arch-step commands can work against one canonical artifact.
- The doc is still not implementation-ready because Section 3.3 remains open.

**Follow-ups**

- Confirm or edit the drafted TL;DR and Section 0.
- Resolve the blocker decisions in Section 3.3 before implementation work.

## 2026-04-17 - North Star confirmed and elegance elevated to a design priority

**Context**

The user confirmed the drafted TL;DR and North Star and added one more design
constraint: optimize for elegance in the final solution.

**Options**

- treat elegance as an informal preference only
- record elegance as an explicit planning priority and architectural rule

**Decision**

Record elegance explicitly. The plan should prefer the smallest and clearest
boundary model that fully solves the problem, instead of solving it with extra
layers, parallel concepts, or migration-only public surface area.

**Consequences**

- The plan is now `active`.
- Later decisions should bias toward one clean boundary model.
- Temporary rollout machinery is still allowed internally when it helps land
  the breaking change safely, but the shipped public model should stay simple.

**Follow-ups**

- Use this bias when resolving the open decisions in Section 3.3.

## 2026-04-17 - Research grounded the current boundary model and narrowed the blocker set

**Context**

The first real research pass checked the compiler, resolver, flow extractor,
session caches, emit roots, grammar, docs, tests, and example corpus to see
which proposal decisions were already settled by repo truth.

**Options**

- keep treating all proposal open decisions as equally unresolved
- use repo evidence to settle what is already implied by the shipped code and
  docs, then ask only the one remaining public-contract question

**Decision**

Ground the plan in repo truth. Keep `AGENTS.prompt` as the agent/runtime flow
marker, keep `SKILL.prompt` as the skill-package root, avoid new public
render-profile or emit-config syntax, treat parallel file parsing as a follow-up
optimization, and keep the public `4.0` cut clean on relative imports. Leave
only the export-model choice open.

**Consequences**

- The blocker set is smaller and more concrete.
- The remaining user choice now cleanly isolates the tradeoff between migration
  size and first-cut boundary elegance.
- `auto-plan` cannot continue into deep-dive until that blocker is answered.

**Follow-ups**

- Ask the exact export-model blocker question.

## 2026-04-18 - Finalized the local `v4.0.0` release candidate and stopped before the real tag cut

**Context**

The remaining work after the fresh audit was stale public teaching plus the
Phase 5 release-candidate pass. The docs and bundled `doctrine-learn`
references were fixed, the public package tree was regenerated, and the full
local release proof passed. The only open item left was the actual public tag
cut.

**Options**

- leave the local release surfaces on the old package version and keep the
  `v4.0.0` payload under `## Unreleased`
- finalize the local `4.0.0` release surfaces now, prove them locally, and
  stop before a real tag because the worktree is still uncommitted
- try to cut or push a public release tag from a dirty worktree

**Decision**

Finalize the local `4.0.0` release candidate now. Update `pyproject.toml`,
promote the `v4.0.0` changelog entry, run the full local release proof, and
stop before the real tag cut. Do not create or push a public tag from a dirty
worktree.

**Consequences**

- The local release candidate is internally aligned and fully green.
- Phase 4 is closed locally and Phase 5 is reduced to the real release cut.
- The remaining blocker is operational, not architectural: a clean committed
  tree is still required before a signed `v4.0.0` tag can be cut.

**Follow-ups**

- Commit the release-candidate tree.
- Cut the signed `v4.0.0` tag from that clean state.

## 2026-04-17 - Choose the hard-cut elegant boundary model

**Context**

The user asked not to be pulled through point-by-point architecture choices and
explicitly said to optimize for the best outcome over safety on a zero-user
project.

**Options**

- keep the smaller flat-visibility cut and add exports later
- choose the cleaner hard cut now, even if it is a larger one-time migration

**Decision**

Choose the cleaner hard cut now. Ship opt-in `export` in `4.0`, remove
relative imports in the same cut, keep `AGENTS.prompt` and `SKILL.prompt` as
the existing boundary entrypoints, unify runtime packages and ordinary flows
under one boundary model, and reject a feature flag or default-flip plan as
part of the accepted architecture.

**Consequences**

- Section 3.3 no longer blocks implementation planning.
- The phase plan can collapse to one direct hard-cut implementation arc.
- Migration gets a bit larger, but the public model gets much cleaner:
  delete same-flow imports, add `export` where a declaration really crosses a
  boundary, rename collisions, and keep true cross-flow imports.

**Follow-ups**

- Implement Phase 1 from Section 7.

# Appendix A) Imported Notes (unplaced; do not delete)

No unplaced notes remain. All meaning-bearing source content was mapped into
Sections 0 through 10.

# Appendix B) Conversion Notes

- This file was reformatted in place from a freeform proposal into the canonical
  `arch-step` artifact.
- The reformat preserved the proposal's breaking-change posture, compiler file
  references, examples list, test list, migration steps, risk notes, and rollout
  ordering.
- No new product scope was added.
- Open decisions from the source were kept open in Section 3.3 instead of being
  smoothed away.
