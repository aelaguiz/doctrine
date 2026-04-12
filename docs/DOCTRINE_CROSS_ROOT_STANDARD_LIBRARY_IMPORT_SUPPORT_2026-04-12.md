---
title: "Doctrine - Cross-Root Standard Library Import Support - Architecture Plan"
date: 2026-04-12
status: active
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: architectural_change
related:
  - docs/RALLY_STANDARD_LIBRARY_SUPPORT_FEATURE_REQUEST_2026-04-12.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/EMIT_GUIDE.md
  - doctrine/compiler.py
  - doctrine/emit_common.py
  - doctrine/diagnostics.py
  - editors/vscode/resolver.js
  - examples/03_imports/cases.toml
---

# TL;DR

- Outcome: Doctrine supports one canonical shared standard-library source tree outside a flow's local `prompts/` root, so downstream repos such as `../rally` can compile multiple flows against the same authored Doctrine source without copying or vendoring it.
- Problem: The shipped compiler, emit path logic, diagnostics, and VS Code navigation currently encode "nearest `prompts/` root" as the import boundary, which blocks a separate shared stdlib home and pushes downstream repos toward layout distortion or duplicated source.
- Approach: Introduce one repo-level compiler config surface in `pyproject.toml` plus one compiler-owned import-root registry that extends the existing ordinary module/import semantics across explicitly declared authored roots, without narrowing support to one special stdlib file, one declaration family, or one small subset of import patterns. Then route compiler diagnostics, prompts-root-aware emit behavior, examples, docs, and editor navigation through that same model without turning Doctrine into the runner.
- Plan: Confirm the North Star, ground the exact owner path and capability contract in the current code, lock the repo-level config plus multi-root registry architecture, harden the call-site audit, and require strong `examples/` coverage across multiple use cases before implementation is considered complete, then implement compiler + diagnostics + emit + editor + corpus + docs as one coherent cutover.
- Non-negotiables: No source copying or vendored Markdown as truth. No silent fallback to weaker import behavior. No parallel import engines. No runner/session/scheduler ownership creep into Doctrine. No narrow feature that only works for one import shape or one declaration subset. Preserve existing single-root behavior and deterministic output layout unless a deliberate plan section changes it. External `../rally` validation is acceptance-only, not shipped Doctrine product scope.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-12
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None. Fresh audit verified the planned owner paths and proof surfaces in:
  - `doctrine/project_config.py`
  - `doctrine/compiler.py`
  - `doctrine/emit_common.py`
  - `doctrine/diagnostics.py`
  - `examples/75_cross_root_standard_library_imports/cases.toml`
  - `editors/vscode/resolver.js`
  - `editors/vscode/tests/integration/suite/index.js`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/EMIT_GUIDE.md`
  - `docs/COMPILER_ERRORS.md`
- Verification run during this audit:
  - `uv sync`
  - `npm ci`
  - `uv run --locked python -m unittest tests.test_project_config`
  - `make verify-examples`
  - `make verify-diagnostics`
  - `cd editors/vscode && make`
  - external `../rally` compile smoke for `PlanAuthor`, `RouteRepair`, and `Closeout`

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Use `$arch-docs` for broader docs cleanup and plan/worklog retirement.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-12
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-12
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

Doctrine will gain one compiler-owned, fail-closed cross-root import capability that lets a downstream repo keep flow-local entrypoints and one shared standard-library source home as separate authored surfaces while preserving ordinary Doctrine composition semantics across the existing import language and keeping Doctrine out of runner/session concerns.

## 0.2 In scope

- Compiler-owned support for imports that cross the current single `prompts/` root boundary through one explicit, canonical resolution model.
- The supporting configuration or capability contract required to declare that a given entrypoint or repo is allowed to use shared authored roots.
- Specific fail-loud diagnostics for unsupported cross-root layouts, invalid shared-root references, and ordinary authoring mistakes inside the new model.
- Generic support across ordinary Doctrine import patterns and declaration reuse, not only for one special import form, one special stdlib file, or workflow-only composition.
- The prompts-root-aware surfaces that must stay aligned with the compiler semantics: at minimum `doctrine/compiler.py`, `doctrine/diagnostics.py`, `doctrine/emit_common.py`, emit CLI behavior that depends on prompt roots, `editors/vscode/resolver.js`, the import example corpus, and the live docs.
- Strong `examples/` coverage that proves both the new cross-root capability and preservation of the existing single-root import behavior across a variety of use cases and scenarios.
- One external downstream acceptance smoke in `../rally` as validation only; it does not widen Doctrine's shipped framework surface.

## 0.3 Out of scope

- Turning Doctrine into the Rally runner, session manager, scheduler, wake system, or runtime adapter layer.
- Requiring copied `.prompt` files, vendored emitted Markdown, or a downstream preprocessor as the primary reuse model.
- New lifecycle, review, route-only, grounding, or machine-readable flow semantics unrelated to cross-root authored-module reuse.
- Repo-wide layout prescriptions for all Doctrine users beyond the minimal explicit contract needed to support shared authored roots.
- Backward-compatibility shims that silently downgrade cross-root usage into the old nearest-root behavior.
- Any Rally-specific syntax, config keys, file layouts, example content, naming, docs, or runtime behavior in Doctrine's shipped surfaces.

## 0.4 Definition of done (acceptance evidence)

- A new manifest-backed proof shows a concrete entrypoint under one local `prompts/` root importing ordinary Doctrine modules from a separate shared authored root and compiling through normal composition semantics.
- The example corpus includes a strong scenario matrix, not one narrow happy path:
  - absolute imports into shared roots
  - relative and parent-relative imports inside shared roots
  - transitive import chains that cross between local and shared authored surfaces
  - multiple concrete entrypoints reusing the same shared authored module
  - representative declaration reuse that demonstrates this is ordinary Doctrine source composition rather than workflow-only special casing
- At least one negative proof shows that unsupported or undeclared cross-root usage fails loudly and specifically instead of degrading silently.
- Existing single-root import proofs continue to represent the preserved baseline behavior.
- VS Code import links and definition resolution can navigate the supported shared-root layout with the same semantic model as the compiler.
- The shipped docs explain the new capability boundary clearly enough that a downstream repo can depend on it without guessing whether Doctrine is now responsible for runtime orchestration.

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks or runtime shims.
- No copied or vendored prompt truth as the primary reuse path.
- One semantics owner for import resolution; compiler truth first, all other surfaces adapt to it.
- No pattern whitelist such as "absolute imports only", "workflow-only imports", or "one special stdlib file" support.
- Emit output layout remains deterministic and does not get conflated with import search space.
- Cross-root support must fail closed when the capability is not declared or not supported.
- Doctrine remains the authoring language and compiler, not the downstream runner.
- `examples/` must show breadth strong enough that downstream adopters can trust the feature as ordinary source composition, not a demo-only carve-out.
- Downstream validation may reference `../rally`, but shipped Doctrine code, docs, examples, and config remain generic and repo-agnostic.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Preserve one canonical authored standard-library home across multiple downstream flows.
2. Keep one elegant, compiler-owned semantics model across compiler, emit, diagnostics, docs, and editor tooling.
3. Fail loudly on unsupported or invalid cross-root layouts instead of degrading silently.
4. Preserve the ergonomics and behavior of the shipped single-root import model for existing Doctrine users.
5. Prove breadth in `examples/` strongly enough that the feature cannot regress into a narrow import-pattern carve-out.
6. Add the smallest durable user-facing surface necessary to declare shared authored roots.

## 1.2 Constraints

- The shipped compiler currently resolves imports relative to the nearest `prompts/` root and treats that root as the authored module boundary.
- Emit surfaces also derive behavior from the entrypoint's `prompts/` root, so import search scope and output layout scope must not get accidentally merged.
- The VS Code extension mirrors the compiler's current prompt-root assumptions in separate JS logic, so semantic drift is a real risk if the feature is implemented only on the Python side.
- The existing import corpus already proves absolute, sibling-relative, parent-relative, deep-relative, transitive, and negative-path behavior within one root; the new feature should extend that ordinary model across roots rather than fork into a special-case subset.
- The feature request explicitly forbids solving this through runner ownership, copied source, vendored emitted artifacts, or preprocessors.

## 1.3 Architectural principles (rules we will enforce)

- The compiler owns the import semantics. Other surfaces must consume or mirror that model, not invent parallel rules.
- Cross-root capability must be explicit and deterministic; no ambient "search the repo until something matches" behavior.
- Import search space and emit output layout are separate concerns and must stay separate in code and docs.
- Preserve ordinary Doctrine source and ordinary module refs. Prefer extending the existing import system over inventing a separate standard-library dialect or a narrow list of blessed import shapes.
- Update live docs, examples, diagnostics, and editor behavior in the same change set so the shipped story remains coherent.
- Treat breadth of supported import patterns and declaration reuse as a product requirement, not as optional polish after the compiler patch lands.
- Keep external downstream acceptance checks clearly separate from Doctrine shipped framework behavior.

## 1.4 Known tradeoffs (explicit)

- Supporting more than one authored root increases resolver complexity, so the implementation has to make precedence and failure behavior explicit instead of heuristic.
- The editor cannot directly reuse Python resolver code, so semantic parity must be maintained through mirrored logic and tests.
- A very flexible multi-root search model would be easy to overbuild; the elegant solution is likely one constrained root-registry contract rather than a general-purpose package manager.
- A narrow implementation that only handles one import pattern would be cheaper short-term but would leave the downstream shared-stdlib use case underproved and fragile.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already has the declaration families and compiler-owned semantics Rally needs after source composition works: imports, composition, workflow law, review, route-only, grounding, typed I/O, diagnostics, and flow extraction. What is missing is the ability to keep shared authored modules in a separate canonical home outside a flow entrypoint's local `prompts/` tree.

## 2.2 What’s broken / missing (concrete)

- `doctrine/compiler.py` resolves the prompt root by walking upward to the nearest directory literally named `prompts`, and import loading is bound to module parts under that root.
- `doctrine/emit_common.py` and emit CLI behavior also assume the entrypoint must live under one `prompts/` tree and derive relative output layout from that root.
- `editors/vscode/resolver.js` independently reimplements the same nearest-`prompts` rule for import links and definition lookup.
- The current model makes a separate shared stdlib home impossible without copying prompt source, vendoring outputs, or distorting the downstream repo shape.
- A narrow fix that only supports one happy-path import style would still be insufficient because the downstream shared stdlib needs to behave like ordinary Doctrine source across realistic import chains and reuse scenarios.

## 2.3 Constraints implied by the problem

- Existing single-root import semantics are real product behavior and must remain stable for current users.
- The feature must preserve Doctrine's boundary as language/compiler and avoid creeping into downstream runtime management.
- Diagnostics have to distinguish "ordinary import is wrong" from "this layout depends on unsupported cross-root capability."

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- User-provided scope anchor: [docs/RALLY_STANDARD_LIBRARY_SUPPORT_FEATURE_REQUEST_2026-04-12.md](docs/RALLY_STANDARD_LIBRARY_SUPPORT_FEATURE_REQUEST_2026-04-12.md). Adopt: the boundary-preserving requirement, copied-source rejection, and fail-closed capability detection. Reject: any interpretation that would require Doctrine to own Rally runtime materialization, scheduling, or downstream repo orchestration.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py) - `CompilationSession.__init__` stores exactly one `prompt_root` for the session, `_resolve_prompt_root` walks upward to the nearest directory literally named `prompts`, and `_resolve_import_path` only rewrites module parts within that one-root model. This is the current hard semantics boundary that blocks a separate shared authored root.
  - [doctrine/emit_common.py](/Users/aelaguiz/workspace/doctrine/doctrine/emit_common.py) - `entrypoint_relative_dir` independently resolves the nearest `prompts` root to determine emit layout eligibility and relative output placement. This is a prompts-root-aware surface, but it owns output layout rather than import search and should stay separate.
  - [doctrine/diagnostics.py](/Users/aelaguiz/workspace/doctrine/doctrine/diagnostics.py) - `E280` currently explains missing modules as not found "under the current prompts root", while `E281` assumes module resolution already succeeded. Any new capability has to preserve these ordinary authoring errors while adding a distinct fail-closed path for unsupported cross-root layouts.
  - [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js) - `resolvePromptRoot`, `uriToModuleParts`, and `collectImportEntries` independently mirror the compiler's current one-root module mapping for navigation and definition lookup. This is the main semantic-drift risk outside Python.
  - [pyproject.toml](/Users/aelaguiz/workspace/doctrine/pyproject.toml) - the only shipped repo-level Doctrine config surface today is `[tool.doctrine.emit]`. That proves Doctrine already has an explicit config home, but it is emit-specific and there is no general compile-time import-root contract yet.
  - [examples/03_imports/cases.toml](/Users/aelaguiz/workspace/doctrine/examples/03_imports/cases.toml) and [examples/03_imports/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/03_imports/prompts/AGENTS.prompt) - the shipped corpus already proves absolute imports, sibling-relative imports, parent-relative imports, deep-relative imports, transitive composition, and fail-loud negatives inside one root. Cross-root support should extend this ordinary model instead of forking it.
- Canonical path / owner to reuse:
  - [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py) - the import-root registry, module identity rules, collision behavior, and load path policy need one owner here first; diagnostics, emit, docs, and editor tooling should adapt to this contract rather than create their own.
- Existing patterns to reuse:
  - [pyproject.toml](/Users/aelaguiz/workspace/doctrine/pyproject.toml) plus [doctrine/emit_common.py](/Users/aelaguiz/workspace/doctrine/doctrine/emit_common.py) - Doctrine already uses explicit repo-owned configuration instead of ambient repo crawling. The shared-root feature should reuse that explicit-contract style without inheriting emit-specific behavior.
  - [examples/03_imports/](/Users/aelaguiz/workspace/doctrine/examples/03_imports) - the repo already teaches and proves import semantics through one manifest-backed example family. The new feature should extend that example-first proof ladder rather than scatter cross-root fixtures across unrelated examples.
  - [doctrine/verify_corpus.py](/Users/aelaguiz/workspace/doctrine/doctrine/verify_corpus.py) - manifest-backed verification is already the canonical proof path for language behavior changes, so cross-root support should land with corpus cases instead of ad hoc harnesses.
- Duplicate or drifting paths relevant to this change:
  - [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py) and [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js) both encode prompt-root discovery and module-to-file mapping today. Any architecture choice that only updates one side will leave Doctrine split-brained.
  - [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py) and [doctrine/emit_common.py](/Users/aelaguiz/workspace/doctrine/doctrine/emit_common.py) both walk upward to a `prompts` directory, but for different responsibilities. The elegant solution needs shared terminology and explicit boundaries, not one merged "prompt root" abstraction that conflates import search with output layout.
  - Live docs likely to drift if not updated in the same change: [docs/LANGUAGE_REFERENCE.md](/Users/aelaguiz/workspace/doctrine/docs/LANGUAGE_REFERENCE.md), [docs/EMIT_GUIDE.md](/Users/aelaguiz/workspace/doctrine/docs/EMIT_GUIDE.md), [docs/README.md](/Users/aelaguiz/workspace/doctrine/docs/README.md), and [editors/vscode/README.md](/Users/aelaguiz/workspace/doctrine/editors/vscode/README.md).
- Behavior-preservation signals already available:
  - [examples/03_imports/cases.toml](/Users/aelaguiz/workspace/doctrine/examples/03_imports/cases.toml) - protects the current single-root import semantics and existing fail-loud diagnostics while we widen the authored-root model.
  - [pyproject.toml](/Users/aelaguiz/workspace/doctrine/pyproject.toml) emit targets plus the shipped emit example set - protect the current assumption that emitted output placement still derives from the entrypoint's local `prompts/` tree.

## 3.3 Decision gaps that must be resolved before implementation

- None after deep-dive pass 2. The plan-shaping decisions are now fixed in Sections 5, 6, and 10:
  - repo-level compile config lives in `[tool.doctrine.compile]`
  - the exact field is `additional_prompt_roots`
  - relative imports stay within the importer's owning root
  - duplicate dotted module identities across roots fail loudly
  - emit output layout stays entrypoint-rooted
  - the proof surface uses one new dedicated example family instead of overloading `03_imports`
- Remaining implementation details are non-architectural and can be settled during implementation without reopening the plan:
  - exact helper function/class names inside the shared config module
  - exact diagnostic code numbers/messages for the new config and ambiguity errors
  - the specific small TOML parser dependency used by the VS Code extension, as long as it is a real TOML parser rather than hand-rolled regex parsing
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- Compiler semantics owner: [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py)
- Emit config and entrypoint-layout owner: [doctrine/emit_common.py](/Users/aelaguiz/workspace/doctrine/doctrine/emit_common.py)
- Emit command entrypoints: [doctrine/emit_docs.py](/Users/aelaguiz/workspace/doctrine/doctrine/emit_docs.py) and [doctrine/emit_flow.py](/Users/aelaguiz/workspace/doctrine/doctrine/emit_flow.py)
- Manifest-backed verification owner: [doctrine/verify_corpus.py](/Users/aelaguiz/workspace/doctrine/doctrine/verify_corpus.py)
- Diagnostic smoke owner for compiler and emit surfaces: [doctrine/diagnostic_smoke.py](/Users/aelaguiz/workspace/doctrine/doctrine/diagnostic_smoke.py)
- Existing repo-level Doctrine config surface: [pyproject.toml](/Users/aelaguiz/workspace/doctrine/pyproject.toml) via `[tool.doctrine.emit]`
- Current import proof ladder: [examples/03_imports/](/Users/aelaguiz/workspace/doctrine/examples/03_imports)
- Editor semantic mirror and tests: [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js) and [editors/vscode/tests/integration/suite/index.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/integration/suite/index.js)

## 4.2 Control paths (runtime)

- Compiler path today:
  - parse one entrypoint with `parse_file(...)`
  - create `CompilationSession(prompt_file)`
  - `_resolve_prompt_root(prompt_file.source_path)` finds the nearest local `prompts/` directory
  - `_load_imports(...)` rewrites import paths with `_resolve_import_path(...)`
  - `_load_module(...)` maps dotted module parts to `self.prompt_root.joinpath(*module_parts).with_suffix(".prompt")`
  - imported units are cached only by dotted module parts under that one root
- Emit path today:
  - `emit_docs` and `emit_flow` resolve targets from `[tool.doctrine.emit.targets]`
  - both parse the entrypoint and construct `CompilationSession(prompt_file)` with no compile-time config input
  - `entrypoint_relative_dir(...)` independently walks to the entrypoint's nearest `prompts/` root to place output files
- Verification path today:
  - `verify_corpus` uses `CompilationSession(parse_file(prompt_path))`, `compile_prompt(...)`, and the emit commands directly
  - corpus cases therefore inherit the same one-root compiler assumption as normal usage
- Editor path today:
  - `resolvePromptRoot(document.uri)` walks upward to the nearest `prompts` directory
  - `uriToModuleParts(...)` derives module identity relative to that one root
  - `collectImportEntries(...)` and the definition providers map imports to files only beneath that same root

## 4.3 Object model + key abstractions

- `PromptFile` carries the parsed declarations plus `source_path`, which is currently the only context `CompilationSession` uses to derive module boundaries.
- `IndexedUnit` is keyed by `module_parts` only; it does not carry a root identity because the compiler assumes one root per session.
- `CompilationSession.prompt_root` is the current root-of-truth for module loading, cycle tracking, and cache keys.
- `EmitTarget` models entrypoint plus output directory only; it does not carry compile-time import-root configuration.
- The VS Code resolver models document context as `{ currentModuleParts, promptRootUri }`, which mirrors the same one-root assumption in JS.

## 4.4 Observability + failure behavior today

- Missing modules fail as `E280` with wording tied to "the current prompts root."
- Missing imported declarations fail as `E281` after module resolution succeeds.
- Cyclic imports fail loudly.
- Relative imports that walk above the current root fail loudly.
- Emit surfaces fail as `E514` when an entrypoint cannot resolve a local `prompts/` root.
- There is no current config reader for compile-time import behavior, so `compile_prompt(...)`, `verify_corpus`, and both emit commands all inherit the one-root limit transitively.
- The editor has no way to understand a repo-level shared-root contract because it only inspects prompt-file location plus inline imports.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. The user-facing surfaces here are compiler behavior, docs, examples, and editor navigation.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

Doctrine should allow:

- one entrypoint-local `prompts/` tree per flow as today
- one or more separate shared authored `prompts/` roots elsewhere in the same downstream repo
- one repo-level compiler config in `pyproject.toml` that declares those additional authored roots explicitly

This should not require copied `.prompt` files, vendored emit output, or repo-shape distortion.

## 5.2 Control paths (future)

- Compiler config resolution:
  - read one compiler-owned config surface: `[tool.doctrine.compile]`
  - use the field `additional_prompt_roots = ["path/to/prompts", ...]`
  - when a caller already resolved an authoritative `pyproject.toml` for Doctrine config, such as emit target mode, pass that same config through to compilation
  - otherwise resolve the nearest `pyproject.toml` from the prompt source path, not from CLI cwd
  - resolve `additional_prompt_roots` relative to that authoritative `pyproject.toml`
  - require each configured entry to resolve to an existing directory literally named `prompts`
  - fail loudly if a configured root duplicates the entrypoint-local root or duplicates another configured root after path resolution
- Import resolution:
  - derive one import-root registry for the session: the primary entrypoint-local root plus zero or more configured shared roots
  - absolute imports search the active registry deterministically
  - relative imports remain rooted in the importer's own authored root and never hop roots implicitly
  - transitive chains can cross roots only through ordinary absolute imports
- Module identity:
  - the ordinary dotted module path remains the user-facing module identity
  - if the same dotted module path exists in more than one configured root, compilation fails loudly as an ambiguity instead of applying root precedence heuristics
- Surface alignment:
  - `compile_prompt(...)`, `CompilationSession(...)`, `verify_corpus`, `emit_docs`, and `emit_flow` all consume the same compile config contract; callers with an already-authoritative resolved project config pass it through, and other entrypoints resolve from prompt source location
  - emit output layout continues to derive only from the entrypoint's own local `prompts/` root
  - VS Code definition and import navigation read the same repo-level compile config and apply the same root-registry model

## 5.3 Object model + abstractions (future)

The canonical design is:

- one new compiler config abstraction loaded from `pyproject.toml`
- one compiler-side import-root registry constructed from that config plus the entrypoint-local root
- one module-resolution contract that maps dotted module parts to exactly zero, one, or many concrete files across the registry

Implementation split:

- a narrow shared config helper module, `doctrine/project_config.py`, to own upward `pyproject.toml` discovery and Doctrine tool-table parsing for both compiler and emit surfaces
- `doctrine/project_config.py` should expose one project-level dataclass that includes compile config and emit config accessors so compiler and emit surfaces consume the same resolved file truth
- `doctrine/compiler.py` remains the canonical owner of import semantics, root registry construction, module collision policy, and relative-import behavior
- `CompilationSession`, `compile_prompt(...)`, and `extract_target_flow_graph(...)` gain an additive optional resolved project-config input so emit target mode can use the same authoritative `pyproject.toml` it already resolved
- `IndexedUnit` or equivalent compile-time state gains enough root identity to keep relative imports, caches, and diagnostics honest once more than one authored root exists

The architecture choice is now fixed: one repo-level compile config plus one import-root registry, not per-target import config, not syntax changes, not alias-prefixed stdlib imports, and not multiple independent resolution engines.

## 5.4 Invariants and boundaries

- One canonical import-resolution authority.
- One explicit repo-level capability contract for cross-root usage.
- No ambient repo-wide search heuristics.
- No runner/scheduler/session ownership expansion.
- No silent fallback to copied or weaker import behavior.
- No root precedence rule that silently chooses between duplicate modules.
- No narrow success condition where only certain import shapes or special-case stdlib modules work.
- Preserve deterministic emit layout and existing single-root behavior.
- No grammar change unless deep-dive pass 2 proves repo-level config cannot carry the feature cleanly.
- External downstream validation does not authorize Rally-specific shipped surfaces in Doctrine.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Project config loading | `doctrine/project_config.py` (new) plus `doctrine/emit_common.py` | upward `pyproject.toml` discovery and Doctrine tool-table parsing | Only emit has a repo-level config loader today, and it lives in emit-specific code | Extract one narrow shared config loader for compiler and emit surfaces | Compiler now needs repo-level config without copying emit-only helpers or inventing cwd-based behavior | One repo-level compile config surface at `[tool.doctrine.compile]` with `additional_prompt_roots = ["path/to/prompts", ...]` | Targeted config parsing tests, emit diagnostics smoke if helper extraction changes existing errors |
| Compiler import resolution | `doctrine/compiler.py` | `CompilationSession.__init__`, `_resolve_prompt_root`, `_resolve_import_path`, `_load_module`, `_load_imports`, `compile_prompt`, `extract_target_flow_graph` | Assumes one nearest `prompts/` root and resolves modules only beneath it | Introduce a compiler-owned import-root registry, keep relative imports root-local, and fail loud on duplicate module identities across roots | This is the canonical owner path for authored import semantics | Repo-level compile config plus deterministic multi-root registry with ambiguity errors instead of precedence; additive optional resolved project-config parameter for callers that already know the authoritative `pyproject.toml` | New cross-root corpus example, preserved `03_imports`, targeted compiler coverage if needed |
| Indexed compile state | `doctrine/compiler.py` | `IndexedUnit`, session caches, imported-unit bookkeeping | Module cache keys and imported-unit state assume one root per dotted module path | Carry enough root identity to keep relative imports, caches, and traces honest under multi-root resolution | Multi-root support otherwise risks cache collisions or misleading traces | Internal root identity attached to compile-time state only; user-facing module syntax stays unchanged | Covered by corpus plus any new unit-level resolver checks |
| Diagnostics | `doctrine/diagnostics.py` | `E280`, `E281`, prompts-root errors, new ambiguity/config errors | Error wording assumes one current prompts root and no capability distinction | Add config, ambiguity, and invalid-root diagnostics; update single-root wording only where the active registry has widened | Downstream repos must fail loudly and specifically on bad shared-root setups without weakening ordinary authoring diagnostics | Capability/config-aware import diagnostics | Negative manifest cases and `make verify-diagnostics` if codes/messages change |
| Emit path handling | `doctrine/emit_common.py`, `doctrine/emit_docs.py`, `doctrine/emit_flow.py` | `resolve_pyproject_path`, `load_emit_targets`, `resolve_direct_emit_target`, `entrypoint_relative_dir`, `emit_target`, `emit_target_flow` | Emit resolves config from `pyproject.toml` but compile semantics still come only from the entrypoint's local root | Route compilation through the shared compile config while preserving entrypoint-relative output layout and direct-mode behavior | Import search scope and emit layout scope must stay separate | Entry-point-root layout remains authoritative even when compile imports span configured shared roots | Existing emit smoke, flow direct-mode smoke, any new config-path smoke |
| Verification surfaces | `doctrine/verify_corpus.py`, `doctrine/diagnostic_smoke.py` | `CompilationSession(parse_file(...))`, `compile_prompt(...)`, emit smoke helpers | Verification inherits the one-root compiler model implicitly | Ensure every verification path uses the same config-backed compilation semantics as normal runtime usage | The feature is not real if only the main compiler path sees it | No special verification-only path; verification exercises the real compiler contract | Cross-root manifest cases, existing smoke signals preserved |
| Example corpus | `examples/03_imports/**`, `examples/75_cross_root_standard_library_imports/**` (new), `examples/README.md` | manifest-backed import proofs and corpus guide | `03_imports` proves only one-root behavior today | Preserve `03_imports` as the baseline and add one dedicated new example focused on cross-root standard-library support with broad scenario coverage | The examples rule says one new idea per example, and breadth is part of the feature | Dedicated cross-root example family with an example-local `pyproject.toml`, multiple local flow roots, one shared `prompts/` root, render/compile-fail cases, and no build-contract dependency | `verify_corpus` manifests and checked-in refs |
| VS Code navigation | `editors/vscode/resolver.js`, `editors/vscode/tests/integration/suite/index.js`, `editors/vscode/package.json` | `resolvePromptRoot`, import link/provider resolution, extension deps/tests | Mirrors nearest-`prompts` root only and has no repo-level compile config awareness | Load the repo-level compile config in JS, build the same root registry model, and extend navigation tests to cover cross-root imports | Avoid split-brain between compiler and editor | Same multi-root semantics on editor side; use a real TOML parser dependency rather than handwritten regex parsing | VS Code integration tests and package build |
| Live docs | `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`, `docs/README.md`, `examples/README.md`, `editors/vscode/README.md` | import, emit, examples, and editor docs | Describe the one-root prompt model as the only supported authored layout | Update docs to explain repo-level compile config, cross-root import semantics, preserved emit layout, new example proof, and editor parity | The shipped story has to stay coherent | Cross-root capability docs with clear compiler/emit/editor boundary | Docs only |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `doctrine/compiler.py` owns import semantics.
  - one narrow shared config helper should own `pyproject.toml` discovery/parsing so compiler and emit do not drift.
- Deprecated APIs (if any):
  - none planned on the public CLI surface.
  - the change should preserve current compile and emit entrypoints by making config loading implicit from prompt source location.
- Delete list (what must be removed):
  - no alternate import syntax
  - no alias-only stdlib dialect
  - no per-target import config that would compete with the repo-level compile contract
  - any stale doc wording that says authored imports are always confined to one nearest `prompts/` root
- Capability-replacing harnesses to delete or justify:
  - do not add downstream preprocessors, copy steps, vendored prompt bundles, or verification-only shims as part of this feature
  - if any helper script appears during implementation, it must justify why the real compiler/config path could not own the behavior
- Live docs/comments/instructions to update or delete:
  - `AGENTS.md`
  - `docs/COMPILER_ERRORS.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/EMIT_GUIDE.md`
  - `docs/README.md`
  - `examples/README.md`
  - `editors/vscode/README.md`
- Behavior-preservation signals for refactors:
  - `examples/03_imports/cases.toml` remains the single-root regression baseline
  - `doctrine/diagnostic_smoke.py` continues to protect emit layout and CLI failure behavior
  - `editors/vscode/tests/integration/suite/index.js` remains the navigation parity signal
  - the new cross-root example must prove the broader scenario matrix without weakening the old baseline
- Example layout rules for the new corpus proof:
  - keep the example-local `pyproject.toml` inside `examples/75_cross_root_standard_library_imports/`
  - use at least two concrete local flow roots plus one shared `prompts/` root in that example directory
  - use manifest `prompt = ...` overrides to prove multiple entrypoints from one example family
  - prefer `render_contract` and `compile_fail` cases over `build_contract` so the proof does not depend on root-level emit target wiring
- External downstream acceptance check:
  - the `../rally` smoke is validation-only and must not introduce Rally-specific code paths, docs, examples, or config into Doctrine

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| --- | --- | --- | --- | --- |
| Repo config loading | `doctrine/emit_common.py` and new shared helper | One shared `pyproject.toml` resolution path for Doctrine tool config | Prevent compiler/emit config lookup drift | include |
| Compiler entrypoints | `compile_prompt(...)`, `CompilationSession(...)`, `extract_target_flow_graph(...)` | Implicit compile-config loading from prompt source path | Prevent a split between library use, emit commands, and corpus verification | include |
| Emit surfaces | `emit_docs.py`, `emit_flow.py`, `entrypoint_relative_dir(...)` | Shared compile config with preserved emit layout boundary | Prevent import-root broadening from accidentally rewriting output placement | include |
| Verification surfaces | `verify_corpus.py`, `diagnostic_smoke.py` | Exercise the real multi-root compiler path, not a test-only shortcut | Prevent feature drift between shipping code and proof code | include |
| Editor resolver | `editors/vscode/resolver.js` and integration tests | Same repo-level compile config plus root-registry model as compiler | Prevent compiler/editor split-brain | include |
| Example design | `examples/03_imports`, new `examples/75_cross_root_standard_library_imports` | Keep one-root baseline separate from one new cross-root idea | Preserve the example-first teaching rule and avoid overloading `03_imports` | include |
| Grammar / parser | `doctrine/grammars/doctrine.lark`, `doctrine/parser.py` | No syntax change by default | Prevent unnecessary language-surface expansion when config can carry the feature | exclude |
| Downstream runtime ownership | Rally runner/session/scheduler surfaces | No Doctrine runtime expansion | Prevent product-boundary creep | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

Worklog: `docs/DOCTRINE_CROSS_ROOT_STANDARD_LIBRARY_IMPORT_SUPPORT_2026-04-12_WORKLOG.md`

Implementation status (parent `implement-loop` pass, 2026-04-12):

- Phase 1: COMPLETE. Shared project-config loading now lives in `doctrine/project_config.py`, and compiler plus emit surfaces share the same resolved `pyproject.toml` truth.
- Phase 2: COMPLETE. The compiler now supports one session-scoped multi-root import registry, keeps relative imports root-local, and fails loudly on invalid config or ambiguous dotted modules.
- Phase 3: COMPLETE. Emit and verification paths now thread the compile config, and `examples/75_cross_root_standard_library_imports` proves the feature with broad positive and negative cases.
- Phase 4: COMPLETE. VS Code resolver parity landed, including real TOML parsing, ambiguous-import fail-closed behavior, and integration coverage for the new example family.
- Phase 5: COMPLETE. Doctrine repo docs, instructions, and verification are aligned, `make verify-examples`, `make verify-diagnostics`, and `cd editors/vscode && make` passed, and a fresh `../rally` smoke compiled `PlanAuthor`, `RouteRepair`, and `Closeout` through the shared-root contract.
- Fresh `audit-implementation` found no Doctrine-side code gaps. Use `$arch-docs` for broader docs cleanup and plan/worklog retirement.

## Phase 1 - Shared project-config foundation

* Goal:
  Establish one shared Doctrine project-config reader that both compiler and emit surfaces can trust, with the compile contract fixed at `[tool.doctrine.compile].additional_prompt_roots`.
* Work:
  - Add `doctrine/project_config.py` with upward `pyproject.toml` discovery, typed parsing for `[tool.doctrine.compile]` plus existing emit tables, and path resolution relative to the authoritative config file.
  - Keep `doctrine/emit_common.py` as the emit-specific API surface, but route its config reads through the shared helper so emit and compiler cannot drift on config-file resolution.
  - Add an additive optional resolved-project-config parameter to `CompilationSession`, `compile_prompt(...)`, and `extract_target_flow_graph(...)` so callers that already resolved an authoritative `pyproject.toml` can reuse it.
  - Validate `additional_prompt_roots` early: each entry must resolve to an existing directory named `prompts`, may not duplicate the entrypoint-local root, and may not duplicate another configured root after path resolution.
* Verification (smallest signal):
  - Targeted config parsing checks for valid compile config, invalid root shape, duplicate configured roots, and preserved emit target loading.
  - Existing emit diagnostic smoke still passes for current config-path failure cases after the helper extraction.
* Docs/comments (propagation; only if needed):
  - Add one succinct code comment at the shared config helper explaining that compiler and emit must share one resolved project-config truth.
* Exit criteria:
  - Compiler and emit can both obtain the same resolved project config without cwd-sensitive divergence.
  - No language grammar or source syntax changes are introduced.
* Rollback:
  - Revert the shared helper extraction and additive config-threading changes as one unit if they destabilize current single-root behavior before the compiler registry lands.

## Phase 2 - Compiler multi-root import registry and fail-loud diagnostics

* Goal:
  Teach the compiler ordinary cross-root import composition while preserving current single-root semantics and keeping relative imports root-local.
* Work:
  - Replace the single `prompt_root` assumption with a session-scoped import-root registry containing the entrypoint-local root plus any configured `additional_prompt_roots`.
  - Update module loading so absolute imports resolve across the registry, while relative imports always resolve within the importer's owning root.
  - Carry enough root identity in indexed units, caches, traces, and imported-unit bookkeeping to avoid cross-root cache collisions or misleading error traces.
  - Add fail-loud diagnostics for invalid additional roots, unsupported config states, and duplicate dotted module identities across roots; keep ordinary `E280`/`E281` behavior for real missing modules/declarations.
  - Preserve public compile entrypoints and grammar; no new import syntax, aliases, or stdlib-only dialect.
* Verification (smallest signal):
  - `examples/03_imports/cases.toml` remains green as the single-root regression baseline.
  - Targeted resolver/compile checks prove duplicate-module ambiguity, invalid additional-root config, and relative-import root-local behavior.
* Docs/comments (propagation; only if needed):
  - Add one succinct comment at the compiler boundary explaining that relative imports never cross roots and that duplicate dotted modules are an ambiguity error, not a precedence rule.
* Exit criteria:
  - Compiler can resolve configured cross-root imports through ordinary absolute imports.
  - Relative imports remain root-local and existing single-root import behavior is preserved.
* Rollback:
  - Revert the registry and root-identity changes as one compiler unit rather than leaving a half-threaded multi-root cache model in place.

## Phase 3 - Emit, verification, and corpus proof convergence

* Goal:
  Ensure every shipped verification and emit path exercises the same config-backed compiler semantics, then prove the feature with one dedicated example family.
* Work:
  - Update `emit_docs.py`, `emit_flow.py`, and `emit_common.py` so emit target mode passes the already-resolved project config into compilation and direct mode resolves compile config from the entrypoint's project file without changing output layout rules.
  - Update `verify_corpus.py` and `doctrine/diagnostic_smoke.py` so they exercise the real config-backed compiler path instead of a test-only shortcut.
  - Add `examples/75_cross_root_standard_library_imports/` with an example-local `pyproject.toml`, at least two local flow `prompts/` roots, one shared `prompts/` root, and manifest `prompt = ...` overrides to prove multiple entrypoints from one example family.
  - Cover the scenario matrix in that example family: local entrypoint importing shared modules, relative imports inside the shared root, transitive chains across roots, multiple entrypoints reusing the same shared module, representative declaration reuse beyond workflow-only composition, and fail-loud negatives for invalid or ambiguous cross-root setups.
  - Keep `03_imports` unchanged as the single-root teaching and regression baseline.
* Verification (smallest signal):
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/03_imports/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/75_cross_root_standard_library_imports/cases.toml`
  - `uv run --locked python -m doctrine.diagnostic_smoke`
* Docs/comments (propagation; only if needed):
  - Add one succinct comment near the emit boundary that import search scope may widen but `entrypoint_relative_dir(...)` still owns output placement.
* Exit criteria:
  - Emit, corpus verification, and smoke diagnostics all consume the same compile-config contract.
  - The feature is proven by one dedicated cross-root example family without overloading `03_imports`.
* Rollback:
  - Revert the example-family addition and emit/verification threading together if the shared contract is not yet stable enough to prove honestly.

## Phase 4 - VS Code resolver parity

* Goal:
  Make VS Code import/document-definition behavior obey the same repo-level compile config and root-registry semantics as the compiler.
* Work:
  - Add one real TOML parser dependency to the VS Code extension package so the resolver can read `[tool.doctrine.compile].additional_prompt_roots` from the authoritative `pyproject.toml`.
  - Update `editors/vscode/resolver.js` to resolve the owning local root, load configured additional roots, keep relative imports root-local, and fail closed on ambiguous absolute module identities.
  - Extend integration tests to cover the new cross-root example family while preserving existing `03_imports` navigation expectations.
  - Keep extension activation and provider shape unchanged; this is a semantics upgrade, not a new editor feature family.
* Verification (smallest signal):
  - `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  - Add one succinct resolver comment documenting that editor import-root logic must stay semantically aligned with the compiler contract.
* Exit criteria:
  - Cross-root import navigation works in the extension for the supported example layout.
  - Existing single-root navigation still passes.
* Rollback:
  - Revert the extension dependency and resolver changes as one unit if editor parity is not yet shippable; do not pretend compiler-only support closes the feature.

## Phase 5 - Live docs, instructions, and final verification

* Goal:
  Reality-sync every shipped doc and instruction surface to the implemented contract, then run the repo’s real verification commands for the changed surfaces.
* Work:
  - Update `docs/LANGUAGE_REFERENCE.md` import rules to replace the old "nearest prompts root only" statement with the shipped repo-level compile config contract and root-local relative-import rule.
  - Update `docs/EMIT_GUIDE.md` to explain the split between compile-time import search and entrypoint-rooted emit layout.
  - Update `docs/COMPILER_ERRORS.md` with the new config/ambiguity diagnostics.
  - Update `docs/README.md`, `examples/README.md`, and `editors/vscode/README.md` to point at the new example family and cross-root behavior.
  - Update `AGENTS.md` so the shipped-corpus range and instruction truth stay aligned once example `75` exists.
  - Remove or rewrite any stale wording that implies authored imports are always confined to one nearest local `prompts/` root.
  - Run one external downstream acceptance smoke in `../rally` against the real shared-root layout so the blocker repo is proven against the shipped Doctrine contract, not just against repo-local examples.
* Verification (smallest signal):
  - `make verify-examples`
  - `make verify-diagnostics`
  - `cd editors/vscode && make`
  - one external downstream Rally smoke against the real shared-root layout in `../rally`
* Docs/comments (propagation; only if needed):
  - This phase is the docs/instructions propagation phase; no doc drift is allowed to remain afterward.
* Exit criteria:
  - Implementation, examples, diagnostics, docs, and instructions all describe the same shipped contract.
  - The repo verification commands for changed surfaces pass.
  - The downstream Rally smoke succeeds against the supported shared-root layout.
* Rollback:
  - Revert the feature-specific docs/instructions updates together with any unreleased implementation changes if the shipped contract is not yet honest.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Prefer extending the existing import corpus and any targeted diagnostic smoke over inventing new harnesses.
- If the compiler gains a root-registry abstraction, cover the smallest deterministic contract around root registration, precedence, and fail-closed error cases.
- Do not replace breadth with one hyper-specific unit test; use unit coverage to protect resolver contracts and corpus coverage to prove realistic authored usage.
- Preserve the current grammar/parsing surface unless deep-dive pass 2 records a real need for syntax changes.

## 8.2 Integration tests (flows)

- Prove a strong cross-root shared-authored scenario matrix in the manifest-backed corpus rather than one narrow happy path.
- Prefer a dedicated new example for the cross-root feature so `03_imports` remains the stable single-root baseline and teaching entrypoint for ordinary imports.
- Prefer manifest `render_contract` and `compile_fail` proof inside the new example over `build_contract`, because build-contract verification is rooted in the main repo emit target registry.
- Include scenarios that cover absolute imports from local entrypoints into shared roots, relative imports within shared-root modules, transitive chains, multiple entrypoints sharing the same module, and representative declaration reuse beyond the tiniest workflow-only demo.
- Prove VS Code import links and definition resolution for the supported shared-root layout.
- Preserve the existing single-root import example as the regression baseline.

## 8.3 E2E / device tests (realistic)

- No new device or UI harness is expected.
- Finalization should include one external downstream Rally smoke check against the supported layout once the compiler-side capability exists; this validates the blocker repo and does not add a Doctrine runtime surface.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Land the capability as an explicit compiler feature, not an implicit heuristic.
- Publish the docs and corpus proof with the code change so downstream adopters can depend on the shipped contract directly.

## 9.2 Telemetry changes

No telemetry is currently expected. If the chosen implementation benefits from debug logging during development, keep it non-productized unless the later plan shows a real long-term need.

## 9.3 Operational runbook

- Downstream users need one clear statement of how to declare shared authored roots and how unsupported usage fails.
- Rally should not need a Doctrine-side runbook beyond the shipped docs and version/capability contract.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: self-integrator
- Scope checked:
  - frontmatter, TL;DR, Sections 0 through 10, planning_passes, and helper blocks
  - owner-path, config-contract, example-proof, docs-sync, and downstream Rally validation alignment
- Findings summary:
  - Section 5 still implied prompt-source-only compile-config resolution even though the chosen design allows callers with an already-authoritative project config to pass it through.
  - Section 5 still used tentative implementation-split wording even though the plan now treats the module split as settled.
  - Section 8 required a downstream Rally smoke, but Section 7 had not yet folded that work into the authoritative checklist.
- Integrated repairs:
  - Clarified compile-config alignment so callers with authoritative resolved project config pass it through and other entrypoints resolve from prompt source location.
  - Removed tentative wording from the implementation split and made `doctrine/project_config.py` explicit.
  - Added the downstream `../rally` smoke to Phase 5 work, verification, and exit criteria.
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

## 2026-04-12 - Preserve Doctrine/Rally boundary

Context

The feature request is explicitly narrow: Rally needs one real shared authored stdlib home, but Doctrine should not absorb runner/session/scheduler responsibilities.

Options

- Expand Doctrine into a runtime/runner layer.
- Keep Doctrine as language/compiler and solve only the authored-root limitation.

Decision

Keep Doctrine as language/compiler only. Solve authored cross-root reuse without taking on Rally runtime ownership.

Consequences

- Import semantics, diagnostics, docs, emit behavior, and editor support are in scope.
- Runner/session/scheduling/materialization behavior is out of scope.

Follow-ups

- Ensure every later section and implementation choice preserves this boundary.

## 2026-04-12 - No fallback compatibility mode

Context

The feature request requires fail-closed support detection and rejects copying, vendoring, or silent downgrade behavior.

Options

- Add a permissive fallback that silently uses weaker single-root behavior.
- Require explicit support and fail loudly when a repo depends on cross-root layout without it.

Decision

Require explicit support and fail loudly.

Consequences

- Diagnostics need a capability-specific path.
- The final design must give downstream repos a truthful way to depend on the feature.

Follow-ups

- Research the cleanest explicit capability contract and record it before implementation.

## 2026-04-12 - Breadth of examples is part of the feature, not optional polish

Context

The downstream requirement is not satisfied by a feature that only works for one special import pattern or one tiny demo scenario. The shipped `examples/` corpus has to prove the capability as ordinary Doctrine source reuse.

Options

- Land the compiler feature with one narrow happy-path example and rely on future expansion.
- Require strong `examples/` coverage across varied import patterns and realistic reuse scenarios as part of the initial delivery.

Decision

Require strong `examples/` coverage as part of the feature itself.

Consequences

- The implementation is not done when the compiler patch lands; it is done when the example corpus demonstrates breadth convincingly.
- The plan has to protect against accidental narrowing to workflow-only or absolute-import-only support.

Follow-ups

- During research/deep-dive, turn this into an explicit scenario matrix in the call-site audit and phase plan.

## 2026-04-12 - Choose repo-level compiler config and a unique multi-root registry

Context

The feature has to work across `CompilationSession`, `compile_prompt`, corpus verification, emit commands, and the VS Code resolver without changing Doctrine source syntax or forcing downstream repo-shape distortion. The repo already has one explicit config home in `pyproject.toml` for emit, but compile-time import behavior has no config surface yet.

Options

- Extend emit-target config so import semantics depend on named targets.
- Add new prompt syntax or an alias-prefixed stdlib import dialect.
- Add one repo-level compiler config in `pyproject.toml` and build one compiler-owned import-root registry from it plus the entrypoint-local root.

Decision

Use one repo-level compiler config, `[tool.doctrine.compile]`, plus one compiler-owned import-root registry. The exact field is `additional_prompt_roots`. Keep ordinary absolute imports as the cross-root bridge, keep relative imports rooted in the importer's current authored root, require configured additional roots to be real `prompts` directories, and fail loudly when the same dotted module path exists in more than one configured root.

Consequences

- No grammar change is required for the planned implementation.
- Compiler, emit, verification, and editor surfaces all need repo-level config awareness.
- Emit output layout stays entrypoint-rooted even though compile import search widens.
- The example plan should add one dedicated new cross-root example rather than overloading `03_imports`.
- Callers that already resolved an authoritative `pyproject.toml`, such as emit target mode, should pass that resolved project config through to compilation instead of letting compilation rediscover a different file.
- The VS Code extension should use a real TOML parser dependency rather than a regex-only config reader.

Follow-ups

- Define the ambiguity and invalid-root diagnostic codes/messages during implementation.
- Choose the smallest acceptable TOML parser package for the VS Code extension during implementation.

## 2026-04-12 - Keep relative imports root-local and use one dedicated cross-root example

Context

Cross-root support must remain broad without becoming heuristic. The risky edges are implicit root hopping through relative imports and overloading the existing `03_imports` example until it stops being a clean single-root baseline.

Options

- Let relative imports walk across configured roots when a matching module exists.
- Keep relative imports anchored to the importer's owning root and use absolute imports to cross roots.
- Fold cross-root proof into `03_imports`.
- Preserve `03_imports` as the single-root baseline and add one new dedicated cross-root example family.

Decision

Keep relative imports root-local. Cross-root movement happens only through ordinary absolute imports. Preserve `03_imports` as the single-root baseline and add one new dedicated example family for the cross-root standard-library feature.

Consequences

- Relative-import behavior remains easy to explain: it never changes roots implicitly.
- The new feature still supports transitive cross-root reuse because shared modules can use absolute imports back into other configured roots.
- The examples stay example-first: `03_imports` keeps teaching ordinary imports, while the new example teaches one new capability.

Follow-ups

- Phase-plan should build the new example around multiple local flow roots, one shared root, and manifest `prompt = ...` overrides.

## 2026-04-12 - Keep downstream acceptance external to Doctrine shipped scope

Context

The blocker repo is `../rally`, so the plan needs one real downstream acceptance proof. That validation is useful, but it must not blur the framework boundary or justify Rally-shaped shipped behavior in Doctrine itself.

Options

- Let downstream acceptance pressure pull Rally-specific naming, docs, examples, or runtime assumptions into Doctrine.
- Keep the Doctrine plan generic and treat `../rally` only as an external acceptance target.

Decision

Keep `../rally` as an external acceptance target only. Doctrine ships generic compiler, emit, editor, example, and docs behavior; the downstream smoke proves the contract but does not become part of Doctrine's product surface.

Consequences

- The shipped Doctrine work remains framework-owned and repo-agnostic.
- External acceptance in `../rally` stays in verification/finalization rather than architecture ownership.

Follow-ups

- Keep implementation, examples, and docs free of Rally-specific naming or runtime assumptions even when validating against the downstream repo.
