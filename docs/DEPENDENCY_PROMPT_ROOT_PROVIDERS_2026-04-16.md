---
title: "Doctrine - Dependency Prompt Root Providers - Architecture Plan"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - docs/EMIT_GUIDE.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/VERSIONING.md
  - docs/COMPILER_ERRORS.md
  - examples/75_cross_root_standard_library_imports/cases.toml
  - doctrine/project_config.py
  - doctrine/_compiler/session.py
  - doctrine/_compiler/support.py
  - doctrine/_compiler/indexing.py
  - doctrine/emit_common.py
  - doctrine/emit_docs.py
  - doctrine/emit_flow.py
  - doctrine/verify_corpus.py
  - tests/test_project_config.py
  - tests/test_import_loading.py
  - tests/test_emit_docs.py
  - tests/test_emit_flow.py
---

# TL;DR

## Outcome

Doctrine gets a small public way for an embedding runtime or installed
dependency to provide named `prompts/` roots at compile time.

## Problem

Doctrine already supports cross-root imports with
`additional_prompt_roots`. That works for external paths, `emit_docs`, and
`emit_flow`. But the host project must still put machine-specific install
paths in its compile config, or a framework must copy prompt files into the
host workspace.

## Approach

Keep `additional_prompt_roots` as the host-owned config surface. Add a
separate provider-owned API for named prompt roots. The compiler will merge
local, configured, and provided roots into the same import registry. Emit
entrypoints and output dirs will still stay inside the target project root.

## Plan

1. Add a named provider-root API and route it through compile and emit target
   loading.
2. Prove imports, runtime package emit, and flow emit without writing provider
   paths into host config.
3. Update docs, diagnostics, release notes, and generic proof so users can
   tell configured roots from provider roots.

## Non-negotiables

- Do not add a second import resolver.
- Do not add automatic package scanning in the first cut.
- Do not weaken project-root guards for configured emit entrypoints or output
  dirs.
- Do not copy provider-owned prompt files into the host project.
- Do not put motivating product names in shipped docs or examples.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-16
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None. Verified by `uv run --locked python -m unittest tests.test_project_config tests.test_import_loading tests.test_emit_docs tests.test_emit_flow` and `make verify-diagnostics`.

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
mini_plan_pass_1: done 2026-04-16
reformat_pass_1: done 2026-04-16
deep_dive_pass_1: done 2026-04-16
phase_plan: done 2026-04-16
recommended_flow: confirm North Star -> implement-loop -> audit implementation -> arch-docs after clean code audit
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If an embedding runtime can pass named provider-owned `prompts/` roots into
Doctrine's public compile and emit APIs, then a host project can import a
framework prompt library without copying it and without storing install paths
in host config. The same imports will work for direct compilation,
`emit_docs`, and `emit_flow`.

## 0.2 In scope

- Add a public provider-root object or equivalent typed API for named
  dependency-owned `prompts/` roots.
- Merge provider roots with the entrypoint-local root and
  `[tool.doctrine.compile].additional_prompt_roots`.
- Keep absolute and relative Doctrine import semantics unchanged.
- Keep relative imports rooted in the importing module's own `prompts/` tree.
- Keep duplicate-root and ambiguous-module checks fail-loud across all active
  roots.
- Preserve configured emit target guards for entrypoint and output paths.
- Prove provider roots through unit tests and generic proof.
- Update docs that explain import roots, emit config, diagnostics, examples,
  and release class.
- Preserve existing configured-root behavior as a public backward-compatible
  contract.

## 0.3 Out of scope

- New Doctrine prompt syntax.
- New host project config syntax for installed packages.
- Automatic Python entry point discovery or package scanning.
- Moving emit entrypoints or output dirs outside the target project.
- Runtime state, memory, scheduling, or adapter behavior.
- A compatibility shim that silently copies provider prompt files into the
  host workspace.
- A product- or framework-specific bridge in Doctrine.

## 0.4 Definition of done (acceptance evidence)

- A framework can call Doctrine with a named provider root such as
  `framework_stdlib -> /installed/framework/prompts`.
- The host project's `pyproject.toml` can keep only its local emit target:
  `entrypoint = "prompts/AGENTS.prompt"` and `output_dir = "build"`.
- The host project does not need `additional_prompt_roots` for the provider
  root.
- Direct compile, `emit_docs`, and `emit_flow` can import modules from the
  provider root.
- Imported provider runtime packages still emit under the target output dir,
  using the package path below the provider root.
- Provider-root errors name the provider root clearly and fail before partial
  emit output matters.
- Duplicate roots and duplicate dotted modules across local, configured, and
  provider roots still fail loudly.
- Public docs use generic framework and standard-library names.
- Existing config-backed cross-root imports keep working.
- The relevant tests and example verification pass.

## 0.5 Key invariants (fix immediately if violated)

- The entrypoint-local `prompts/` root is always one active root, but duplicate
  matching modules across roots are still errors.
- Provider roots are compile inputs only. They are not emit targets.
- Configured emit entrypoints and output dirs remain under the target project
  root.
- Provider roots must be existing directories named `prompts`.
- Provider roots must not make emitted artifacts depend on machine-specific
  host config.
- No root precedence rule may hide ambiguous imports.
- `additional_prompt_roots` remains valid host-owned config.
- Compatibility posture: additive public API. Existing config and emit
  contracts must be preserved.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Preserve Doctrine's current import semantics and fail-loud behavior.
2. Make ownership clear: host config owns host roots; provider API owns
   dependency roots.
3. Keep the public API small and direct enough for framework CLIs to use.
4. Keep emitted output anchored to the host target project.
5. Avoid machine-specific provider install paths in host config and new
   emitted metadata.
6. Add proof where it protects real behavior, not repo shape.

## 1.2 Constraints

- Provider roots must use the existing active import-root search path.
- Configured roots and provider roots must share validation rules where they
  mean the same thing.
- Provider roots need stable identity for useful diagnostics and emitted
  source identity.
- The first cut must not discover packages or scan environments by itself.
- Public docs and examples must stay generic.
- The change is a public backward-compatible compile and emit API addition.

## 1.3 Architectural principles (rules we will enforce)

- One import-root registry. No parallel resolver.
- One compile session source of truth. Emitters pass provider roots into that
  same path.
- Fail loud for invalid roots, duplicate roots, and ambiguous modules.
- Provider roots are read-only compile inputs. They never become host source
  files or emit targets.
- Keep guards in shipped code, not in docs-only checks.
- Add high-leverage comments only at the provider-root normalization boundary
  if the ownership split would otherwise be easy to miss.

## 1.4 Known tradeoffs (explicit)

- We choose an explicit embedding API over automatic package discovery. That
  makes the first cut simpler, testable, and less environment-sensitive.
- We keep `additional_prompt_roots` instead of replacing it. Host-owned shared
  roots and framework-owned roots are different ownership stories.
- We prefer named provider roots over bare provider paths. Names add a small
  API burden, but they make diagnostics and emitted identity much cleaner.
- We may add manifest support for provider roots only if it remains simple.
  Unit tests can be enough for the API surface if manifest proof would add
  ceremony without improving behavior confidence.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already supports filesystem-backed cross-root imports through
`[tool.doctrine.compile].additional_prompt_roots`. Those roots can live
outside the emitting project, and the current compile session uses them for
absolute imports. The emit pipeline already works with imported runtime
packages from active roots.

## 2.2 What's broken / missing (concrete)

The only public owner of extra roots today is host project config. A framework
can point a host project at an installed prompt library path, but that makes
the host config carry machine-specific install details. A framework can also
copy prompt files into each host workspace, but that creates source drift and
turns framework-owned prompts into host-owned files.

Doctrine needs a first-class provider path for dependency-owned or
runtime-supplied roots. The provider path should remove host config mutation
without changing import semantics or emit placement.

## 2.3 Constraints implied by the problem

- The host project still owns the local entrypoint and output dir.
- The framework or embedding runtime owns the provider root path resolution.
- The compiler owns import resolution and ambiguity checks.
- Emitters should not need one-off provider handling.
- Docs must distinguish "configured roots" from "provider roots" without
  making users learn a second import model.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal "ground truth")

## 3.1 External anchors (papers, systems, prior art)

No external research is needed for this change. The correct design is driven
by Doctrine's current compile and emit surfaces plus the ownership problem
already stated in the source plan. Automatic package discovery is rejected for
the first cut because it would add environment policy that Doctrine does not
need to own.

## 3.2 Internal ground truth (code as spec)

- `doctrine/project_config.py` owns `CompileConfig` and resolves
  `additional_prompt_roots` from `[tool.doctrine.compile]`.
- `ProjectConfig.resolve_compile_config()` validates that each configured root
  is an existing directory named `prompts`.
- `resolve_config_path()` already accepts absolute paths and resolves
  relative paths against the `pyproject.toml` directory.
- `CompilationSession` in `doctrine/_compiler/session.py` loads the nearest
  project config, resolves compile config, and calls
  `resolve_import_roots()`.
- `resolve_import_roots()` in `doctrine/_compiler/support.py` combines the
  entrypoint-local root with configured roots and rejects duplicate paths.
- `resolve_module_source()` in `doctrine/_compiler/indexing.py` searches all
  active roots for absolute imports and fails when more than one root matches
  the same dotted module.
- `load_emit_targets()` and `resolve_direct_emit_target()` in
  `doctrine/emit_common.py` build `EmitTarget` values that carry
  `ProjectConfig`.
- `emit_docs`, `emit_skill`, and `emit_flow` all compile through
  `CompilationSession(prompt_file, project_config=target.project_config)`.
- `emit_common._validate_entrypoint_within_project_root()` and
  `_validate_output_dir_within_project_root()` already enforce the non-goal.
- `emit_docs._build_runtime_emit_plan()` already emits imported runtime
  packages under the target output root by using the package path below a
  `prompts/` root.
- `tests/test_project_config.py` proves configured roots, duplicate config
  roots, and project-root emit guards.
- `tests/test_import_loading.py` proves directory-backed runtime packages
  and configured cross-root runtime package imports.
- `tests/test_emit_docs.py` and `tests/test_emit_flow.py` already cover
  imported runtime package emit behavior.
- `examples/75_cross_root_standard_library_imports` proves config-backed
  shared roots across two entrypoints plus fail-loud invalid-root and
  ambiguous-module cases.
- `docs/EMIT_GUIDE.md` explains that compile-time import search may widen but
  emitted output placement stays anchored to the entrypoint's local root.
- `docs/LANGUAGE_REFERENCE.md` explains absolute and relative import rules.
- `docs/VERSIONING.md` classifies directory-backed runtime package imports and
  matching flow behavior as additive when older local-root entrypoints keep
  working.

Canonical owner path: `doctrine/project_config.py` should own the provider-root
data shape and validation. `CompilationSession` should own merging the roots
into the compiler's active import registry.

Compatibility posture: additive. Keep existing `ProjectConfig`,
`CompileConfig`, `additional_prompt_roots`, emit targets, and import semantics
working.

Behavior-preservation signal: existing config-backed root tests and example
75 must remain green while provider-root tests prove the new path.

## 3.3 Decision gaps that must be resolved before implementation

No blocker remains. The plan chooses a named provider-root API, no automatic
package discovery, one active import registry, additive compatibility, and
generic public docs/examples.

<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/project_config.py` contains `CompileConfig`, `ProjectConfig`, TOML
  loading, and config-path resolution.
- `doctrine/_compiler/session.py` builds `CompilationSession` and currently
  passes only configured roots into the import-root resolver.
- `doctrine/_compiler/support.py` contains `resolve_prompt_root()` and
  `resolve_import_roots()`.
- `doctrine/_compiler/indexing.py` resolves absolute and relative imports
  against active roots.
- `doctrine/emit_common.py` loads emit targets and protects configured
  entrypoint/output placement.
- `doctrine/emit_docs.py`, `doctrine/emit_skill.py`, and
  `doctrine/emit_flow.py` all create compile sessions from target config.
- The verifier under `doctrine/_verify_corpus/` creates compile sessions and
  loads emit targets for examples.

## 4.2 Control paths (runtime)

This is an authoring-time and emit-time change, not a runtime harness change.
The current control path is:

1. A prompt file is parsed.
2. `CompilationSession` finds the nearest local `prompts/` root.
3. The session loads or receives `ProjectConfig`.
4. `ProjectConfig.resolve_compile_config()` returns configured
   `additional_prompt_roots`.
5. `resolve_import_roots()` makes one tuple of active root paths.
6. Absolute imports search the active roots. Relative imports stay inside the
   importing module's root.
7. Emitters collect compiled roots and write output under the configured
   target output dir.

## 4.3 Object model + key abstractions

- `ProjectConfig` carries raw TOML tables and exposes resolved compile config.
- `CompileConfig` carries `additional_prompt_roots`.
- `EmitTarget` carries the resolved entrypoint, output dir, and project config.
- `CompilationSession.import_roots` is the active root tuple used by import
  resolution.
- `IndexedUnit.prompt_root` and `IndexedUnit.package_root` preserve the root
  and package metadata needed for runtime package emit.

## 4.4 Observability + failure behavior today

- Invalid compile config is normalized into `E285`.
- Duplicate configured roots become `E286`.
- Ambiguous modules across configured roots become `E287`.
- Missing imports become `E280`.
- Configured emit entrypoints outside the project root become `E521`.
- Configured/direct emit output dirs outside the project root become `E520`.
- Some emitted metadata can fall back to absolute source paths when imported
  source lives outside the target project.

## 4.5 UI surfaces (ASCII mockups, if UI work)

No UI work.

<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- `doctrine/project_config.py` adds the provider-root data shape and shared
  root validation.
- `doctrine/_compiler/session.py` accepts provider roots and merges them with
  configured roots.
- `doctrine/_compiler/support.py` keeps one active-root merge path.
- `doctrine/emit_common.py` accepts provider roots when loading configured or
  direct emit targets.
- `doctrine/emit_docs.py`, `doctrine/emit_skill.py`, and
  `doctrine/emit_flow.py` keep compiling through target config.
- Tests add provider-root coverage alongside current configured-root coverage.
- Docs explain configured roots and provider roots as two sources for the same
  import semantics.

## 5.2 Control paths (future)

Provider root flow:

1. A framework or embedding runtime resolves its installed `prompts/` path.
2. It creates a named provider root, for example
   `ProvidedPromptRoot("framework_stdlib", framework_prompts_path)`.
3. It passes provider roots into direct compile or emit target loading.
4. `CompilationSession` builds active roots in this order:
   - entrypoint-local root
   - host-configured roots from `additional_prompt_roots`
   - provider roots from the public API
5. Absolute imports search all active roots.
6. Relative imports stay inside the importer root.
7. Emit output still lands under the host target output dir.

Order is only for deterministic diagnostics and traversal. It must not become
a precedence rule. If two roots provide the same dotted module, Doctrine still
fails with the ambiguous-module diagnostic.

## 5.3 Object model + abstractions (future)

Add one provider-owned compile input beside the existing host-owned config
input:

```python
ProvidedPromptRoot(
    name="framework_stdlib",
    path=framework_prompts_path,
)
```

The exact class name can change during implementation, but the public shape
should keep two facts:

- `name`: a stable provider label for errors and emitted metadata
- `path`: an existing directory named `prompts`

`additional_prompt_roots` stays the TOML field for host-owned roots.
`provided_prompt_roots` becomes the public API field for runtime or
dependency-owned roots.

Expose provider roots through the public Python path, not through a new host
TOML field:

- `ProjectConfig` can carry provider roots.
- `load_project_config(..., provided_prompt_roots=...)` can return a config
  with those roots.
- `load_emit_targets(..., provided_prompt_roots=...)` can attach those roots
  to every loaded target.
- `resolve_direct_emit_target(..., provided_prompt_roots=...)` can use them
  for direct `emit_flow`.
- `CompilationSession(..., provided_prompt_roots=...)` can support direct
  compile users who do not go through emit target loading.
- `compile_prompt(..., provided_prompt_roots=...)` and
  `extract_target_flow_graph(..., provided_prompt_roots=...)` can stay useful
  convenience wrappers.

This keeps the API simple for a framework CLI:

```python
target = load_emit_targets(
    host_pyproject,
    provided_prompt_roots=(
        ProvidedPromptRoot("framework_stdlib", framework_prompts_path),
    ),
)["app"]
emit_target(target)
```

No host file changes are required.

## 5.4 Invariants and boundaries

- Provider roots use the same hard path validation as configured roots:
  existing directory, directory name `prompts`, and duplicate-root rejection.
- Provider names must be non-empty and stable enough for diagnostics and
  emitted metadata.
- Provider roots are not host-owned config.
- Provider roots are not emit entrypoints.
- Provider roots cannot weaken `E520` or `E521`.
- Runtime package output placement stays as it is: provider-owned runtime
  packages emit under the target output dir by their path below the provider
  `prompts/` root.
- Provider-root final-output metadata should avoid leaking absolute install
  paths. Prefer a stable provider-root-relative identity such as:

```json
"entrypoint": "framework_stdlib:agents/editor/AGENTS.prompt"
```

If this touches existing absolute external-root behavior, keep the change
limited to roots supplied through the new provider API.

## 5.5 UI surfaces (ASCII mockups, if UI work)

No UI work.

<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Compile config data | `doctrine/project_config.py` | `CompileConfig` | Carries only `additional_prompt_roots`. | Add provider-root storage or keep provider roots on `ProjectConfig` with a resolved compile view. | Provider roots need to enter the same compile path without TOML. | Public provider-root API. | `tests/test_project_config.py` |
| Project config data | `doctrine/project_config.py` | `ProjectConfig` | Carries raw TOML compile/emit tables. | Store provider roots and provide a clear construction path. | Emit targets already carry `ProjectConfig`. | `provided_prompt_roots` parameter. | `tests/test_project_config.py`, emit tests |
| Root normalization | `doctrine/project_config.py` | `resolve_config_path` and compile-root validation | Validates configured roots inline. | Add shared prompt-root normalization for config roots and provider roots. | Prevents parallel validation logic and drift. | Root must be existing `prompts/` dir. | `tests/test_project_config.py` |
| Compile session | `doctrine/_compiler/session.py` | `CompilationSession.__init__` | Merges local and configured roots. | Accept and merge provider roots before indexing imports. | This is the canonical compile boundary. | `CompilationSession(..., provided_prompt_roots=...)` | `tests/test_import_loading.py` |
| Import root merge | `doctrine/_compiler/support.py` | `resolve_import_roots` | Rejects duplicates across local and configured roots. | Treat local, configured, and provider roots as active roots and reject duplicates. | Keeps one root registry. | Active root registry. | `tests/test_project_config.py`, `tests/test_import_loading.py` |
| Module lookup | `doctrine/_compiler/indexing.py` | `resolve_module_source` | Searches all active roots for absolute imports. | Keep behavior. Update wording if diagnostics mention configured roots only. | No new resolver. | Same import semantics. | Existing import tests plus provider import test |
| Configured targets | `doctrine/emit_common.py` | `load_emit_targets` | Loads targets with project config only. | Add provider-root argument and attach it to each target's `ProjectConfig`. | Framework CLIs use configured host targets. | `load_emit_targets(..., provided_prompt_roots=...)` | `tests/test_emit_docs.py`, `tests/test_emit_flow.py` |
| Direct flow target | `doctrine/emit_common.py` | `resolve_direct_emit_target` | Supports direct `emit_flow` with optional `pyproject`. | Accept provider roots. | Direct mode should use the same compile input story. | `resolve_direct_emit_target(..., provided_prompt_roots=...)` | `tests/test_emit_flow.py` |
| Compile wrappers | `doctrine/_compiler/session.py`, `doctrine/compiler.py` | `compile_prompt`, `extract_target_flow_graph` | Accept only project config. | Accept provider roots and pass them into `CompilationSession`. | Public convenience API should not force callers into config objects. | Wrapper provider-root args. | `tests/test_import_loading.py` or focused compiler boundary tests |
| Emit docs | `doctrine/emit_docs.py` | `emit_target` | Works when target config includes configured roots. | Should work once target config carries provider roots. | Avoid emitter-specific provider code. | No direct emit-doc API change required. | `tests/test_emit_docs.py` |
| Emit flow | `doctrine/emit_flow.py` | `emit_target_flow` | Works when target config includes configured roots. | Should work once target config carries provider roots. | Same root graph for docs and flow. | No direct emit-flow API change required. | `tests/test_emit_flow.py` |
| Emit skill | `doctrine/emit_skill.py` | `emit_target_skill` | Compiles through target config. | Inherit provider-root behavior. Add focused coverage only if needed. | Keep all emitters aligned. | Same provider-root config path. | Existing skill tests, optional new case |
| Final-output source path | `doctrine/emit_docs.py` | `_agent_entrypoint_relpath` | External sources can fall back to absolute paths. | Use provider-root-relative identity for provider roots. | Avoid machine-specific emitted metadata. | `framework_stdlib:...` identity for provider roots. | `tests/test_emit_docs.py` if final-output provider package proof is added |
| Example manifest | `doctrine/_verify_corpus/manifest.py` | `CaseSpec` and manifest loading | No provider-root support. | Add optional manifest-level provider roots only if example proof needs it. | Keep generic example verifiable without host config path hacks. | Manifest provider root field if chosen. | `tests/test_verify_corpus.py`, `make verify-examples` |
| Example runner | `doctrine/_verify_corpus/runners.py` | Session creation and target loading | Builds sessions from prompt path and repo target registry. | Pass provider roots for provider-aware example cases if manifest support is added. | Proof should match the new API. | Provider-root proof path. | `make verify-examples` |
| Build-contract runner | `doctrine/_verify_corpus/runners.py` | `_run_build_contract` | Loads repo-root emit targets with no extra provider input. | Avoid adding a broken root `pyproject` target unless provider-aware build-contract support stays simple. | Do not make normal example verification fragile. | Explicit provider proof or unit tests. | `tests/test_verify_corpus.py` if changed |
| Public docs | `docs/EMIT_GUIDE.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md`, `docs/VERSIONING.md`, `CHANGELOG.md` | Import-root, emit, diagnostics, release docs | Explain configured roots only. | Explain provider roots and additive release class. | Public API change needs docs. | Config roots vs provider roots. | `make verify-diagnostics` if diagnostics change |
| Examples docs | `examples/README.md`, optional `examples/118_provider_prompt_roots` | Example 75 covers config-backed roots. | Keep example 75 as config-backed proof. Add generic provider example only if useful and simple. | Avoid overloading existing example. | Generic provider-root proof. | `make verify-examples` if example changes |

## 6.2 Migration notes

- Canonical owner path: `doctrine/project_config.py` for provider-root data and
  validation; `CompilationSession` for active-root merge.
- Deprecated APIs: none.
- Delete list: none expected. This is an additive API.
- Adjacent surfaces included now: compile config types, compile session, emit
  target loading, direct flow target loading, diagnostics wording, public docs,
  release docs, targeted tests, and generic proof.
- Adjacent surfaces explicitly deferred: automatic package discovery and
  product-specific framework bridges.
- Compatibility posture: preserve existing `additional_prompt_roots` and emit
  target contracts.
- Live docs/comments/instructions to update: public docs listed above and any
  boundary comment needed near provider-root validation.
- Behavior-preservation signals: existing config-backed import tests,
  existing emit tests, example 75, and focused provider-root tests.

<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 - Provider Root Model And Compile Registry

Status: COMPLETE

Completed work:

- Added `ProvidedPromptRoot` and provider-root validation in
  `doctrine/project_config.py`.
- Threaded provider roots into `CompilationSession`, `compile_prompt`, and
  `extract_target_flow_graph`.
- Kept one active import-root registry and updated duplicate/ambiguous root
  diagnostics to talk about active roots when provider roots are involved.
- Proved provider runtime package imports, duplicate active roots, and
  ambiguous modules across configured and provider roots.

### Goal

Let a caller pass named provider-owned `prompts/` roots into direct compile
without host config changes.

### Work

Introduce the provider-root data shape, validate it beside configured roots,
and merge it into the current active import-root registry.

### Checklist (must all be done)

- Add the provider-root data shape in `doctrine/project_config.py`.
- Add validation for provider name and provider root path.
- Reuse or extract shared prompt-root validation so configured roots and
  provider roots do not drift.
- Merge provider roots with configured roots in `ProjectConfig` or
  `CompilationSession`.
- Add provider-root parameters to `CompilationSession`, `compile_prompt`, and
  `extract_target_flow_graph`.
- Preserve existing `additional_prompt_roots` behavior.
- Preserve relative import behavior inside the importing module's own root.
- Update diagnostic text where "configured prompts root" is no longer true.
- Add a short boundary comment if the provider-root ownership split would be
  unclear without it.

### Verification (required proof)

- Run:
  - `uv run --locked python -m unittest tests.test_project_config tests.test_import_loading`
- Run `make verify-diagnostics` if diagnostic builders or compiler error docs
  change in this phase.

### Docs/comments (propagation; only if needed)

- Update `docs/COMPILER_ERRORS.md` only if diagnostics change here.
- Keep broader guide and release docs for Phase 3 unless they become false
  during this phase.

### Exit criteria (all required)

- A direct compile caller can import a module from a provider root without
  `additional_prompt_roots`.
- Invalid provider roots fail before compilation continues.
- Duplicate paths across local, configured, and provider roots fail loudly.
- Duplicate dotted modules across configured and provider roots fail loudly.
- Existing configured-root tests still pass.

### Rollback

Remove the provider-root API and tests from this phase. Existing
`additional_prompt_roots` behavior should still be untouched.

## Phase 2 - Emit Target Integration And Provider-Safe Source Identity

Status: COMPLETE

Completed work:

- Added provider-root parameters to configured emit target loading and direct
  flow target resolution.
- Kept `emit_docs`, `emit_flow`, and `emit_skill` on the shared target config
  and compile-session path.
- Updated final-output contract source identity for provider-owned prompts to
  use `provider_name:path/below/prompts/AGENTS.prompt`.
- Proved configured docs emit, configured flow emit, and direct flow emit with
  provider roots and no provider path in host config.

### Goal

Make configured emit and direct flow consume provider roots through the same
compile path, while emitted output remains host-project anchored.

### Work

Thread provider roots through emit target loading, direct flow target
resolution, and emitted source identity for provider-owned prompt files.

### Checklist (must all be done)

- Add provider-root parameters to `load_project_config` if needed for clean
  construction.
- Add provider-root parameters to `load_emit_targets`.
- Add provider-root parameters to `resolve_direct_emit_target`.
- Ensure `emit_docs` works through target config with no emitter-local provider
  resolver.
- Ensure `emit_flow` works through target config or direct target resolution
  with no emitter-local provider resolver.
- Ensure `emit_skill` inherits provider-root behavior through target config.
- Keep configured emit entrypoint validation under the target project root.
- Keep configured and direct output dir validation under the target project
  root.
- Update provider-root final-output source identity so provider roots do not
  leak absolute install paths into emitted metadata.

### Verification (required proof)

- Run:
  - `uv run --locked python -m unittest tests.test_project_config tests.test_import_loading tests.test_emit_docs tests.test_emit_flow`
- Add focused `emit_skill` proof only if implementation changes that path
  beyond inherited target config.

### Docs/comments (propagation; only if needed)

- Add or update a short code comment at the emitted source-identity boundary
  only if the provider-root path rewrite is not self-evident.

### Exit criteria (all required)

- A host target with no provider path in `pyproject.toml` can emit docs that
  include an imported provider runtime package under the host output dir.
- `emit_flow` sees provider-owned runtime package agents and route edges.
- Direct `emit_flow` can use provider roots.
- Provider-root final-output metadata uses stable provider-root-relative
  identity instead of absolute install paths.
- `E520` and `E521` behavior remains unchanged.

### Rollback

Remove provider-root parameters from emit target loading and direct target
resolution. The configured-root emit path should still work.

## Phase 3 - Public Docs, Release Notes, And Generic Proof

Status: COMPLETE

Completed work:

- Updated the emit guide, language reference, compiler error catalog,
  versioning guide, and changelog for provider-supplied prompt roots.
- Kept public wording generic and avoided product-specific names.
- Kept example 75 as the config-backed cross-root proof.
- Used focused unit and emit tests as the provider-root proof instead of
  adding a manifest example.

### Goal

Teach the new ownership model without mixing framework-specific names into
public docs or examples.

### Work

Update public docs and add generic proof in the lowest-ceremony path that
still protects behavior.

### Checklist (must all be done)

- Update `docs/EMIT_GUIDE.md` with a small embedding example using
  `ProvidedPromptRoot("framework_stdlib", path)`.
- Update `docs/LANGUAGE_REFERENCE.md` so imports say "active roots" when they
  mean local, configured, or provider roots.
- Update `docs/COMPILER_ERRORS.md` if diagnostic names or details changed.
- Update `docs/VERSIONING.md` because this is a public backward-compatible API
  addition.
- Update `CHANGELOG.md` with the public feature entry.
- Keep public docs and examples generic. Do not use motivating product names.
- Leave `examples/75_cross_root_standard_library_imports` as the
  config-backed root proof.
- Add a generic example only if it can be verified without making the repo
  root `pyproject.toml` target unusable outside the provider-aware verifier.
- If a generic manifest example is added, update `examples/README.md` and run
  the example verification below.
- If unit tests are the right proof for an API-only provider surface, record
  that decision in Section 10 during implementation.

### Verification (required proof)

- Run:
  - `uv run --locked python -m unittest tests.test_project_config tests.test_import_loading tests.test_emit_docs tests.test_emit_flow`
- Run `make verify-examples` if a manifest-backed example or verifier support
  changes.
- Run `make verify-diagnostics` if diagnostics changed.
- Run `make verify-package` if package metadata or public install packaging
  changes.

### Docs/comments (propagation; only if needed)

- Sync only the live public docs touched by the new public API. Broader docs
  cleanup belongs to `arch-docs` after the code audit is clean.

### Exit criteria (all required)

- Public docs clearly distinguish host-owned configured roots from
  runtime-supplied provider roots.
- The example or test proof shows no provider path in host compile config.
- Release docs explain the change as additive.
- All relevant checks run or any gap is stated plainly.

### Rollback

Revert the docs and example additions for provider roots. If Phases 1 and 2
remain, public docs must not falsely mention unavailable behavior.

<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- `tests/test_project_config.py` should prove valid provider roots, invalid
  provider root paths, duplicate provider roots, and duplicate paths across
  configured and provider roots.
- `tests/test_import_loading.py` should prove provider-root imports and
  provider-root runtime package imports without `additional_prompt_roots`.
- Existing config-backed import tests should remain green as preservation
  evidence.

## 8.2 Integration tests (flows)

- `tests/test_emit_docs.py` should prove a host target emits an imported
  provider runtime package into the host output dir without provider paths in
  host config.
- `tests/test_emit_flow.py` should prove flow emit sees provider-owned runtime
  package agents and route edges.
- Existing example 75 should keep proving config-backed roots.
- Add manifest-backed provider proof only if it remains simple and useful.

## 8.3 E2E / device tests (realistic)

No device or UI tests are needed. If a manifest-backed example changes, run
`make verify-examples`. If diagnostics change, run `make verify-diagnostics`.
If public install packaging changes, run `make verify-package`.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

Ship as an additive public API. Existing users do not need to change host
config. Framework and embedding-runtime callers can opt in by passing provider
roots.

## 9.2 Telemetry changes

No telemetry changes are expected. This is a compile and emit API change, not
a runtime ops feature.

## 9.3 Operational runbook

No runtime runbook changes are expected. Public docs should show the embedding
call shape and explain that provider roots must be existing `prompts/`
directories.

# 10) Decision Log (append-only)

## 2026-04-16 - Use provider roots instead of dependency discovery

Context

Doctrine already supports filesystem-backed cross-root imports, but host
config is the only public way to supply extra roots.

Options

- Add package discovery to Doctrine.
- Add host project config syntax for packages.
- Add a public provider-root API for embedding runtimes and frameworks.

Decision

Add a public named provider-root API. Do not add package discovery or new host
TOML syntax in the first cut.

Consequences

Frameworks can resolve their own installed prompt paths and pass them to
Doctrine without copying prompt files or writing machine-specific paths into
host config. Doctrine keeps one import resolver.

Follow-ups

- Revisit package discovery only if multiple real callers need the same
  convention after the provider API ships.

## 2026-04-16 - Preserve configured-root compatibility

Context

`additional_prompt_roots` is already shipped and proved by docs, tests, and
example 75.

Options

- Replace configured roots with provider roots.
- Keep configured roots and add provider roots beside them.

Decision

Keep configured roots. Provider roots are additive and have a different
ownership story.

Consequences

Hosts can still own shared source roots in TOML. Frameworks can own dependency
roots through the embedding API.

Follow-ups

- Keep docs clear that both root sources feed the same active import semantics.

## 2026-04-16 - Use focused tests instead of a provider-root manifest example

Context

Provider roots are supplied through a Python embedding API, not through host
TOML. A manifest-backed example would need verifier support for runtime-owned
provider paths.

Options

- Add manifest support for provider roots and a new generic example.
- Prove the public API with focused unit and emit tests.

Decision

Use focused tests for the first cut. Do not add manifest support or a new
example now.

Consequences

The API proof stays close to the Python call sites that own provider roots.
Example 75 keeps proving host-owned configured roots.

Follow-ups

- Add manifest support only if future examples need to prove provider-owned
  roots through the shipped corpus.

# Appendix B) Conversion Notes

- Converted the compact mini-plan sections into the canonical full
  `miniarch-step` scaffold.
- Mapped the old `Research Grounding`, `Current Architecture`,
  `Target Architecture`, `Call-Site Audit`, and `Phase Plan` blocks into
  Sections 3 through 7.
- Expanded the two compact phases into three authoritative Section 7 phases
  with `Checklist (must all be done)` and `Exit criteria (all required)`.
- No source content was dropped. No Appendix A is needed because all
  meaning-bearing source content was placed in canonical sections.
- Status moved to `active` after North Star confirmation.
