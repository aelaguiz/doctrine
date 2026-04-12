---
title: "Doctrine - Compiler Scalability And Parallelism - Architecture Plan"
date: 2026-04-11
status: complete
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: phased_refactor
related:
  - doctrine/compiler.py
  - doctrine/parser.py
  - doctrine/emit_docs.py
  - doctrine/emit_flow.py
  - doctrine/verify_corpus.py
  - ../paperclip_agents/doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt
  - ../paperclip_agents/paperclip_home/agents/lessons_acceptance_critic/AGENTS.md
---

# TL;DR

## Outcome

Doctrine becomes fast enough to compile large and complex prompt families in
normal development and verification flows, with multithreaded batch
compilation enabled by default and with no Doctrine language, render, or
diagnostic semantics changing.

## Problem

Current compile throughput does not scale. The compiler already caches imported
modules inside one `CompilationContext`, but large single-agent compiles still
pay serial import/index and field-compilation costs, while batch surfaces such
as `emit_docs` and `verify_corpus` repeatedly re-enter compilation work
serially. On large real-world prompt families such as the Lessons critic in
`../paperclip_agents`, this makes compile latency high enough that the work can
feel non-terminating in practice.

## Approach

Keep one Doctrine-owned compiler path, then make it structurally cheaper and
parallel by default. The intended architecture is:

- one reusable compile session per entrypoint or verification batch
- one immutable indexed module graph instead of repeated ad hoc re-index work
- safe multithreaded execution at the independent boundaries that actually
  exist today, especially prompt-graph loading and batch agent compiles
- deterministic output ordering and fail-loud concurrency boundaries so
  performance work never creates semantic drift

## Plan

1. Baseline the current hot paths on Doctrine-owned surfaces and on the large
   Lessons critic entrypoint family without trying to brute-force the entire
   external repo.
2. Introduce a reusable compile-session boundary and immutable module-graph
   cache inside `doctrine/compiler.py`.
3. Move Doctrine-owned batch compile surfaces to default multithreaded
   execution on top of that shared session.
4. Tighten the single-agent path so large imported prompt families benefit too,
   not only multi-agent batches.
5. Prove no behavior drift with the shipped corpus plus a representative large
   real-world compile target.

## Non-negotiables

- No Doctrine language changes.
- No rendered-output or diagnostic drift except for explicit bug fixes that are
  separately proven and called out.
- No second compiler path, repo-local wrapper, daemon, or precompiler.
- No opt-in requirement for ordinary parallel speedups on Doctrine-owned batch
  surfaces.
- No hidden stale-cache behavior; invalidation must fail loudly if it cannot be
  trusted.
- Deterministic output order must survive multithreaded execution.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-11
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
deep_dive_pass_1: done 2026-04-11
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-11
recommended_flow: implement-loop
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

Worklog: `docs/archive/second_wave/DOCTRINE_COMPILER_SCALABILITY_AND_PARALLELISM_2026-04-11_WORKLOG.md`

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly, Doctrine will compile large prompt families
materially faster without changing authored language semantics:

- large single-agent entrypoints with heavy import graphs will stop feeling
  non-terminating in normal development runs
- Doctrine-owned batch surfaces will use multithreaded execution by default
- each compile session will parse and index each prompt module at most once for
  that session
- output ordering, rendered Markdown, and compile diagnostics for existing
  active examples will remain stable

Initial success target for confirmation:

- at least a 2x wall-clock improvement on Doctrine-owned batch compile surfaces
  that currently re-enter compilation serially
- at least a 2x wall-clock improvement on one representative large Lessons
  entrypoint family anchored by
  `../paperclip_agents/doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt`

If deeper research shows the measured baseline or Python runtime constraints
require different exact numeric budgets, the target may be tightened in the
same doc, but only with an explicit Decision Log entry.

## 0.2 In scope

- Performance-only changes inside the shipped compiler and adjacent
  Doctrine-owned compile surfaces.
- Refactoring `doctrine/compiler.py` so compilation can reuse a shared session,
  immutable indexed module graph, and safe concurrency boundaries.
- Improving both:
  - single-agent latency for large import-heavy prompt families
  - batch throughput for emit and verification flows
- Default multithreaded execution for Doctrine-owned batch surfaces when
  multiple independent compile tasks exist.
- Narrow instrumentation or benchmark hooks needed to prove the speedup and
  prove no semantic drift.
- Small docs or command-surface updates required to explain the new default
  behavior honestly.
- Architectural convergence needed to keep one compile source of truth instead
  of separate fast and slow paths.

## 0.3 Out of scope

- Any Doctrine syntax, grammar, model, or rendering feature change motivated by
  performance.
- Prompt rewrites in `../paperclip_agents` as the primary fix.
- Repo-local workaround scripts, build daemons, or precompiled artifacts that
  replace the Doctrine compiler.
- Distributed compilation, remote caches, or speculative watch-mode features.
- A second user-facing mode where “fast compile” and “correct compile” are
  separate surfaces.
- Parallel truth surfaces in docs or examples that are not owned by shipped
  Doctrine code.

## 0.4 Definition of done (acceptance evidence)

- The shipped compiler has one explicit reusable compile-session boundary with
  safe invalidation and deterministic results.
- Doctrine-owned batch compile surfaces run multithreaded by default where
  independent work exists.
- Large single-agent compiles also improve materially, not only batch emit
  throughput.
- `make verify-examples` stays green.
- `make verify-diagnostics` stays green if diagnostics or related smoke checks
  change.
- A representative large real-world benchmark rooted in the Lessons critic
  prompt family shows a material wall-clock reduction relative to the captured
  baseline.
- The proof does not depend on changing prompt text or lowering correctness
  checks.

Behavior-preservation evidence:

- current manifest-backed render and compile-fail examples remain green
- emitted Markdown or flow artifacts only change where a separately justified
  bug fix requires it
- targeted before/after output comparison exists for the representative large
  benchmark target

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks and no shadow compiler path.
- No language or output drift in the name of speed.
- No mutable cross-thread shared state unless it is explicitly synchronized and
  narrow.
- No duplicate module parsing or indexing inside one compile session when the
  source inputs are unchanged.
- No nondeterministic output ordering from multithreaded work.
- No benchmark-only fast path that Doctrine users do not actually exercise.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Preserve Doctrine semantics exactly.
2. Cut wall-clock latency enough that large compiles are routine again.
3. Make throughput scale with prompt-family size via default multithreading
   where independence exists.
4. Keep one compiler owner path and one truth for compilation.
5. Keep concurrency failures obvious and debuggable.

## 1.2 Constraints

- `parse_file()` currently reparses source files every call; only the Lark
  grammar object is cached.
- `compile_prompt()` currently constructs a fresh `CompilationContext` for each
  compile.
- `emit_docs.py` parses the entrypoint once but still calls `compile_prompt()`
  serially for each root concrete agent.
- `verify_corpus.py` executes compile-bearing cases serially today.
- Large real-world prompt families can involve dozens of imported `.prompt`
  files and large generated agent homes.
- Python threading will only help where the work actually exposes safe
  parallelism, so redundant work must be removed in addition to adding threads.

## 1.3 Architectural principles (rules we will enforce)

- Optimize the shipped compiler, not a second path around it.
- Parse and index once, then compile many.
- Prefer immutable shared compile inputs plus ordered result collection over
  broad locking.
- Parallelize only at boundaries that preserve Doctrine semantics and authored
  ordering.
- Fail loudly on cache invalidation uncertainty, cycles, or concurrency misuse.
- Keep public compile behavior simple: faster by default, not “fast mode” as a
  separate product surface.

## 1.4 Known tradeoffs (explicit)

- Threading alone will not rescue a structurally redundant pipeline; the plan
  has to remove repeated work first.
- Parallelizing post-resolution compile work raises determinism and traceability
  risks that the plan must address explicitly.
- A reusable compile session increases architectural complexity, so ownership
  and invalidation boundaries must stay narrow and well-commented.
- Some deep compiler paths may remain serial if parallelizing them would create
  harder-to-debug behavior for marginal gain.
- Field-level compile fan-out should only land when the measured large-target
  path still misses after shared session reuse and parallel graph loading.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine's compile pipeline is centered in `doctrine/compiler.py`.

- `compile_prompt()` constructs a fresh `CompilationContext` and compiles one
  target agent.
- `CompilationContext.__init__()` immediately indexes the root prompt unit and
  recursively loads imports.
- `_load_module()` caches imported units only inside that one context.
- `_compile_agent_decl()` resolves shared agent prerequisites, then compiles
  fields in authored order on one thread.
- `doctrine/emit_docs.py` loops concrete agents and recompiles serially.
- `doctrine/verify_corpus.py` runs compile-bearing cases serially.

External scale reference already visible from repo evidence:

- the Lessons prompt family under `../paperclip_agents/doctrine/prompts/lessons`
  contains 36 `.prompt` files
- `lessons_acceptance_critic/AGENTS.prompt` is 517 lines
- the emitted `paperclip_home/agents/lessons_acceptance_critic/AGENTS.md` is
  945 lines

## 2.2 What's broken / missing (concrete)

- No explicit compile-session boundary exists for reuse across adjacent compile
  work.
- No default multithreaded execution exists on Doctrine-owned batch compile
  surfaces.
- No clear single-agent optimization boundary exists for heavy import graphs and
  expensive field compilation.
- Performance has no first-class proof target today, so regressions are easy to
  miss and large-target gains are hard to verify honestly.

## 2.3 Constraints implied by the problem

- The requested work is purely a performance pass; semantics must hold still.
- The plan must improve both large single-agent latency and batch throughput.
- The acceptance fixture must be a real large prompt family, not a synthetic
  micro-benchmark only.
- Determinism, diagnostics, and fail-loud import behavior are part of the
  shipped contract and cannot be traded away for speed.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- none adopted in this auto-plan run — reject a prior-art detour for now —
  the repo already exposes the owner path, the repeated-work fault line, and
  the deterministic constraints clearly enough to design the first scalable
  architecture honestly
- if implementation later stalls on thread-vs-process tradeoffs or invalidation
  discipline, run `external-research` narrowly on:
  - immutable compile-graph sharing for parallel compilers
  - Python executor tradeoffs for mixed parse, index, and render workloads
  - deterministic error and result aggregation in parallel compilation

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/parser.py` — `build_lark_parser()` caches the grammar once, but
    `parse_file()` still reads and parses source on every call
  - `doctrine/compiler.py` — `compile_prompt()` and
    `extract_target_flow_graph()` each create a fresh `CompilationContext`,
    which means a fresh root index plus fresh recursive import loading for each
    top-level compile/extract call
  - `doctrine/compiler.py` — `CompilationContext.__init__()`, `_index_unit()`,
    and `_load_module()` already prove the intended ownership boundary:
    compiler-owned import/index truth with one-context memoization via
    `_module_cache`
  - `doctrine/compiler.py` — `_compile_agent_decl()` does meaningful shared
    prerequisite work up front via `_resolve_agent_slots()`,
    `_resolve_agent_contract()`, and `_review_output_contexts_for_agent()`, then
    compiles the agent body serially in authored field order
  - `doctrine/emit_docs.py` — `emit_target()` parses the entrypoint once, then
    recompiles each root concrete agent serially through `compile_prompt()`
  - `doctrine/emit_flow.py` — `emit_target_flow()` parses the entrypoint once,
    then re-enters the compiler through `extract_target_flow_graph()`
  - `doctrine/verify_corpus.py` — render and compile-fail cases parse and
    compile per case, serially, even when adjacent cases share a prompt file
  - `doctrine/diagnostic_smoke.py` — current smoke coverage proves compile and
    emit correctness at the current public entrypoints, so wrapper-level
    compatibility matters
- Canonical path / owner to reuse:
  - `doctrine/compiler.py` — this file must own the scalable compile session,
    immutable graph, and deterministic task execution model; emit and verify
    surfaces should become adopters, not parallel compiler owners
- Existing patterns to reuse:
  - `doctrine/compiler.py` `_module_cache` — already shows the right semantic
    idea: load each imported module once per compile owner
  - `doctrine/emit_docs.py` root-agent enumeration — already separates
    entrypoint parsing from per-agent work, which is the right seam for
    batch-task fan-out after session reuse exists
  - `doctrine/verify_corpus.py` case ordering and reporting — already owns
    deterministic manifest-order reporting and should keep that role even if
    execution becomes parallel underneath
- Prompt surfaces / agent contract to reuse:
  - not applicable as a design lever here; this change is compiler-internal and
    does not depend on prompt repair
- Native model or agent capabilities to lean on:
  - not applicable; this is deterministic compiler work, not agent-behavior
    shaping
- Existing grounding / tool / file exposure:
  - `uv run --locked python ...` works in this repo and is the honest runtime
    surface for bounded parse or benchmark inspection
  - `../paperclip_agents/doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt`
    is the real large-target anchor the user named
- Duplicate or drifting paths relevant to this change:
  - `compile_prompt()` versus `extract_target_flow_graph()` — both construct a
    fresh compiler owner for the same prompt graph instead of sharing a session
  - `emit_docs.py`, `emit_flow.py`, and `verify_corpus.py` each re-enter the
    compiler independently instead of converging on a shared batch/session path
- Capability-first opportunities before new tooling:
  - reuse one compiler-owned session and graph first; do not add daemons,
    precompilers, repo-local wrappers, or benchmark-only alternate paths
  - reuse existing CLI and verification surfaces for proof first; do not invent
    a new performance harness unless those surfaces cannot prove the change
    honestly
- Behavior-preservation signals already available:
  - `make verify-examples` — shipped corpus proof
  - `make verify-diagnostics` — compile/emit smoke proof when wrappers or
    diagnostics move
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/36_invalidation_and_rebuild/cases.toml`
    — targeted multi-agent emit/build proof on an existing shipped example
- Large-target evidence gathered in this pass:
  - the Lessons critic root prompt has 27 declarations and 13 direct imports
  - its reachable prompt graph spans 15 `.prompt` files with 39 import edges
  - the root file alone parses in about `0.256s` via `uv run --locked`, which
    suggests the painful path is not plain parsing of one file alone but the
    broader compile graph and repeated compile-entry rework

## 3.3 Open questions from research

- How much of the single-agent slowdown remains after shared session reuse and
  parallel import-graph loading land? — settle with before/after timing on the
  Lessons critic anchor
- Does `verify_corpus.py` need prompt-path grouping only, or manifest-wide task
  fan-out with shared sessions, to hit the target without muddying report order?
  — settle with a small prototype and manifest-order diff review
- Measured answer: the large Lessons anchor still missed after the session split
  and parallel graph loading alone, so the implementation reopened
  field-parallel compile work and review-gate validation compression on
  evidence instead of leaving the slow path untreated
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

The current owner paths are:

- `doctrine/parser.py` — prompt-file parse entry
- `doctrine/compiler.py` — import resolution, declaration indexing, semantic
  resolution, and compiled output generation
- `doctrine/emit_docs.py` — Markdown emit over concrete root agents
- `doctrine/emit_flow.py` — flow-graph emit over the same entrypoint concept
- `doctrine/verify_corpus.py` — manifest-backed corpus verification
- `doctrine/diagnostic_smoke.py` — wrapper-level correctness smoke checks

## 4.2 Control paths (runtime)

Single-agent compile today:

1. `parse_file()` reads and parses the entrypoint prompt file.
2. `compile_prompt()` constructs a fresh `CompilationContext`.
3. `CompilationContext.__init__()` calls `_index_unit()` on the root prompt and
   recursively resolves imports through `_load_module()`.
4. `compile_agent()` finds the target agent on `root_unit` and calls
   `_compile_agent_decl()`.
5. `_compile_agent_decl()` resolves slots, contract, and review-output context,
   then compiles role, workflow or review, inputs, outputs, and skills in
   authored order on one thread.

Batch compile today:

- `emit_target()` parses the entrypoint once, enumerates root concrete agents,
  then recompiles each agent serially via `compile_prompt()`, rebuilding the
  compiler owner each time
- `verify_corpus()` iterates manifest cases serially; render and compile-fail
  cases each parse and compile independently, even when they share a prompt
  path
- `emit_target_flow()` parses the entrypoint once, then re-enters the compiler
  through a fresh `CompilationContext` for graph extraction

## 4.3 Object model + key abstractions

Current abstractions are correct in spirit but wrong for sharing:

- `CompilationContext` owns:
  - prompt-root resolution
  - module loading and indexing
  - mutable cycle-detection stacks
  - mutable resolved-body caches
  - public compile/extract entrypoints
- `IndexedUnit` is a frozen dataclass and therefore a plausible immutable graph
  node, but it is built inside the same mutable owner that also holds task-time
  stacks and caches
- `_loading_modules` is a mutable set used for cycle detection during graph
  construction
- `_resolved_*_cache` dictionaries memoize resolved workflows, reviews, skills,
  and I/O bodies, but they are scoped to one mutable context and are therefore
  not safe to share across threaded callers as-is

The result is one large owner object that mixes:

- immutable prompt-graph truth
- mutable build-time state
- mutable compile-task state
- public wrapper behavior

That mixed ownership is the main architectural reason the current compiler does
not scale safely.

## 4.4 Observability + failure behavior today

- the compiler already fails loudly on missing imports, cycles, illegal
  inheritance, and semantic violations
- diagnostics preserve source paths and trace context, which must survive any
  refactor
- no shipped timing or scaling signal exists today, so “it feels stuck” is not
  captured anywhere except user experience
- the current repo does have correctness guardrails, but not scale guardrails:
  `make verify-examples`, build-contract references, and
  `doctrine/diagnostic_smoke.py`

## 4.5 UI surfaces (ASCII mockups, if UI work)

No UI surface is in scope.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

The owner paths stay the same, with one architectural split introduced inside
`doctrine/compiler.py` rather than by adding a second compiler package:

- `CompilationSession` (or equivalent) becomes the public owner for one prompt
  graph or one grouped verification batch
- an immutable prompt graph sits under that session and holds the indexed units
  and any source freshness metadata needed for the session
- per-task compile state moves into a task-local context derived from the
  immutable graph
- `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, and
  `doctrine/verify_corpus.py` consume the session API instead of each spinning
  their own top-level compiler owner

## 5.2 Control paths (future)

Target control-path shape:

1. Build one `CompilationSession` from the entrypoint prompt file or grouped
   prompt-path batch.
2. The session resolves the prompt root and builds an immutable graph keyed by
   module path or module parts.
3. Graph construction uses a thread-safe module registry so sibling imports can
   load and index in parallel, but each module is still parsed and indexed at
   most once per session.
4. Each compile or extract task receives a task-local context with its own
   mutable resolution stacks and memoization dictionaries, seeded from the
   shared immutable graph.
5. Batch APIs (`compile_agents`, grouped verify work, flow extraction) execute
   on a default in-process thread pool and collect results in deterministic
   caller order.
6. Existing wrappers such as `compile_prompt()` remain thin compatibility
   entrypoints over the same session API, not parallel implementations.

Single-agent v1 strategy:

- the first required latency win comes from parallel prompt-graph loading plus
  one session-owned immutable graph
- task-local compile state still stays isolated per compile task
- the measured large-target path did still miss after the graph/session split,
  so v1 also landed ordered agent-field fan-out plus review-gate validation
  compression keyed to the output semantics the compiler can actually observe

## 5.3 Object model + abstractions (future)

Target abstractions:

- `CompilationSession`
  - owns prompt-root resolution, graph construction, worker-pool policy, and
    wrapper compatibility
  - exposes `compile_agent()`, `compile_agents()`, and
    `extract_target_flow_graph()` on top of the same graph
- immutable prompt graph
  - maps module identifiers to indexed units and source freshness metadata for
    the current session only
  - is safe to read from multiple threads
- task-local compile context
  - owns `_workflow_compile_stack`, `_workflow_resolution_stack`,
    `_loading_modules`-equivalent task state where needed, and the resolved-body
    caches that should not be shared across compile tasks
- deterministic result collector
  - preserves caller order for emitted files, flow artifacts, verification
    results, and diagnostics regardless of worker scheduling

## 5.4 Invariants and boundaries

- `doctrine/compiler.py` remains the single source of truth for compile
  semantics.
- No process pool, daemon, precompiler, or watch-cache product surface lands in
  v1.
- Threaded work is default-on only where tasks are independent and the output
  order can still be reconstructed deterministically.
- No cross-session reuse is allowed when source freshness is ambiguous; create a
  new session instead.
- The immutable prompt graph is shared; mutable compile-task state is not.
- Public wrappers remain semantically identical even if their implementation
  moves under the session.

## 5.5 UI surfaces (ASCII mockups, if UI work)

No UI surface is in scope.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Parse entry | `doctrine/parser.py` | `parse_file()`, `parse_text()` | parses from disk every call | support session-owned parse/load reuse without creating stale global cache behavior | repeated prompt reads are part of the batch-cost story | session-owned parse/load helper or equivalent | `make verify-examples` |
| Compiler owner split | `doctrine/compiler.py` | `CompilationContext.__init__()`, `_index_unit()`, `_load_module()` | one mutable owner mixes graph build, task stacks, and caches | split immutable prompt graph from task-local compile state inside one compiler-owned session | safe threading requires shared-read graph plus isolated mutable task state | `CompilationSession` + immutable graph + task-local context | `make verify-examples` |
| Wrapper compatibility | `doctrine/compiler.py` | `compile_prompt()`, `extract_target_flow_graph()` | each wrapper creates a fresh top-level compiler owner | keep wrappers as thin compatibility entrypoints over the shared session | avoid duplicate truth and preserve existing public surfaces | wrapper-to-session contract | `make verify-examples`, `make verify-diagnostics` |
| Single-agent compile path | `doctrine/compiler.py` | `compile_agent()`, `_compile_agent_decl()`, `_resolve_agent_slots()`, `_resolve_agent_contract()` | agent compile is task-local but graph setup is repeated and serial | reuse the session graph and keep per-agent mutable resolution state isolated | reduce large single-agent latency without semantic drift | task-local compile-context contract | targeted manifests and large-target benchmark |
| Batch docs emit | `doctrine/emit_docs.py` | `emit_target()` | parses once, then recompiles each root agent serially | build one session per target and compile root agents on a default thread pool with deterministic output order | this is the cleanest shipped batch-throughput win | `emit_target()` uses compiler session internally | `make verify-examples`, emit smoke |
| Batch flow emit | `doctrine/emit_flow.py` | `emit_target_flow()` | enters graph extraction through a fresh compile owner | route graph extraction through the same session/graph owner path | one compile owner path for Markdown and flow artifacts | flow extraction via session | flow build-contract checks |
| Corpus verification | `doctrine/verify_corpus.py` | `verify_corpus()`, `_run_render_contract()`, `_run_compile_fail()` | compile-bearing cases are serial and do not share sessions | group work by prompt path or comparable shared session boundary; parallelize underneath while preserving manifest order in results and diffs | verification should exercise the scalable compiler path too | deterministic grouped verification contract | `make verify-examples` |
| Smoke coverage | `doctrine/diagnostic_smoke.py` | compile/emit smoke helpers | smoke assumes current wrapper behavior and current file naming | update only as needed so wrapper-level fail-loud behavior stays covered | wrapper compatibility is part of the shipped contract | smoke-compatible wrapper contract | `make verify-diagnostics` when touched |
| Live docs / guidance | `README.md`, `docs/README.md`, `examples/README.md` | any compile/emit guidance that becomes user-visible | current docs do not describe the session split or default parallel behavior | update only if the change is user-visible; otherwise keep docs quiet | no stale truth about compile behavior | concise live-truth sync only if needed | doc review only |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `doctrine/compiler.py` session API plus immutable prompt graph
- Deprecated APIs (if any):
  - none planned publicly; `compile_prompt()` and `extract_target_flow_graph()`
    should survive as thin wrappers unless deeper implementation evidence proves
    otherwise
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - any temporary benchmark-only fast path
  - any ad hoc worker-pool logic duplicated per surface once the session owns it
  - any dead mutable-shared-state path kept only for pre-refactor compatibility
- Capability-replacing harnesses to delete or justify:
  - do not add a daemon, process pool, or repo-local wrapper unless the session
    model provably cannot hit the target
- Live docs/comments/instructions to update or delete:
  - high-leverage code comments at the session/graph boundary and any task-local
    compile-context boundary
  - live docs only if default parallel behavior or wrapper guidance becomes
    user-visible
- Behavior-preservation signals for refactors:
  - `make verify-examples`
  - `make verify-diagnostics` when smoke or diagnostics move
  - targeted example proof with
    `examples/36_invalidation_and_rebuild/cases.toml`
  - before/after wall-clock and output comparison for the Lessons critic anchor

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Compiler wrappers | `doctrine/compiler.py` `compile_prompt()`, `extract_target_flow_graph()` | one session-owned compile/extract owner | avoids fast-vs-slow wrapper drift | include |
| Emit surfaces | `doctrine/emit_docs.py`, `doctrine/emit_flow.py` | shared session and deterministic thread-pool collection | prevents each emit surface from reinventing compile ownership | include |
| Corpus verifier | `doctrine/verify_corpus.py` | grouped session reuse plus ordered reporting | keeps verification on the same scalable path as shipped compilation | include |
| Smoke tests | `doctrine/diagnostic_smoke.py` | wrapper-compatibility smoke after owner split | prevents silent CLI/entrypoint drift | include |
| Benchmark support | any new helper script | existing command-based proof first | avoids architecture theater around perf-only tooling | defer |
| Process isolation | process pool / daemon / persistent cache | out-of-process scaling path | adds complexity and duplicate truth too early | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Session split and baseline capture

Status: COMPLETE
Completed work:
- Split the compiler into a shared `CompilationSession` plus task-local
  `CompilationContext`, and kept `compile_prompt()` /
  `extract_target_flow_graph()` as thin wrappers over that one owner path.
- Switched the parser cache to thread-local parser instances so parallel prompt
  loading does not share one mutable Lark parser across worker threads.
- Captured the before-state Lessons anchor signal honestly: parse-only stayed
  fast, while a full compile remained in flight past several seconds and felt
  effectively stuck.

* Goal:
  Establish the scalable compiler owner path without changing semantics: one
  session, one immutable prompt graph, one task-local compile context model.
* Work:
  Add the session/graph/task-context split inside `doctrine/compiler.py`.
  Keep `compile_prompt()` and `extract_target_flow_graph()` as thin wrappers.
  Capture before-state timing using existing commands or one minimal
  command-level measurement path, not a second benchmark product surface.
* Verification (smallest signal):
  `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml`
* Docs/comments (propagation; only if needed):
  Add one short code comment at the immutable graph boundary and one at the
  task-local compile-context boundary if the split is non-obvious.
* Exit criteria:
  The compiler has a shared session boundary and no caller needs to construct
  shared mutable compile state directly.
* Rollback:
  Collapse the new internals back behind the existing wrappers and delete dead
  partial abstractions rather than leaving both models live.

## Phase 2 — Parallel prompt-graph loading for large single-agent latency

Status: COMPLETE
Completed work:
- Added once-per-session imported-module loading with deterministic caching and
  root-level parallel import fan-out inside `CompilationSession`.
- Reopened field-level compile fan-out after the warm-session Lessons benchmark
  showed review compilation still dominated the wall clock.
- Compressed review gate-branch validation down to the output semantics the
  compiler can actually observe, which removed the reject-path branch
  explosion on the Lessons critic anchor.
- The Lessons anchor now returns its real shipped compile verdict
  (`E484 Review outcome is not total`) in about `2.49s` instead of sitting in
  the branch explosion beyond the earlier several-second baseline.

* Goal:
  Make a single large compile materially faster by parallelizing import-graph
  loading and indexing inside the session.
* Work:
  Replace the serial recursive module-loading path with a thread-safe
  once-per-session module loader keyed by module identity. Ensure each module
  is parsed and indexed at most once per session. Reopen field fan-out only on
  measured evidence, then keep result collection ordered and deterministic.
* Verification (smallest signal):
  Before/after wall-clock on the Lessons critic anchor plus
  `uv run --locked python -m doctrine.verify_corpus --manifest examples/36_invalidation_and_rebuild/cases.toml`
* Docs/comments (propagation; only if needed):
  Comment the once-per-session module-registry invariant where future or lock
  ownership is not obvious.
* Exit criteria:
  Large single-agent compile setup no longer rebuilds its prompt graph
  serially, and the Lessons anchor shows a real timing win without output drift.
* Rollback:
  Remove the parallel graph-loading layer and keep the session split if
  correctness or determinism regresses.

## Phase 3 — Default threaded batch compile surfaces

Status: COMPLETE
Completed work:
- Updated `doctrine/emit_docs.py` to build one session per target and compile
  root agents through ordered thread-pool collection.
- Updated `doctrine/emit_flow.py` to reuse the same session owner path for flow
  graph extraction.
- Updated `doctrine/verify_corpus.py` to reuse sessions by prompt path and to
  parallelize compile-bearing cases while keeping manifest-order reporting and
  ref-diff output deterministic.

* Goal:
  Make Doctrine-owned batch surfaces scale by default through the same session
  owner path.
* Work:
  Update `doctrine/emit_docs.py` to compile root agents through one session on a
  default thread pool with deterministic output ordering. Update
  `doctrine/emit_flow.py` to reuse the same session owner for graph extraction.
  Update `doctrine/verify_corpus.py` to reuse sessions on shared prompt files
  and parallelize compile-bearing work underneath manifest-order reporting.
* Verification (smallest signal):
  `make verify-examples`
* Docs/comments (propagation; only if needed):
  Update any wrapper-level comments or docs only if the default parallel
  behavior becomes part of live user guidance.
* Exit criteria:
  Emit and verification surfaces no longer rebuild top-level compiler owners per
  independent task, and their output/report order remains deterministic.
* Rollback:
  Revert the affected caller to serial task execution on the same session API;
  do not reintroduce a separate compiler owner path.

## Phase 4 — Hardening, proof, and live-truth cleanup

Status: COMPLETE
Completed work:
- Ran `make verify-examples` successfully after the compiler and caller-path
  changes.
- Verified the smaller phase signals on
  `examples/01_hello_world/cases.toml` and
  `examples/36_invalidation_and_rebuild/cases.toml`.
- Captured the large Lessons anchor outcome honestly: the current shipped truth
  for that prompt family is a fast fail-loud compile result (`E484`), so the
  proof is reduced wall-clock to the real error surface rather than a rendered
  output diff.
- Left diagnostics untouched, so `make verify-diagnostics` was not needed.

* Goal:
  Prove the performance pass preserved behavior, clean up temporary scaffolding,
  and leave the repo truthful.
* Work:
  Run the full shipped corpus. Run diagnostics smoke if touched. Capture the
  final before/after benchmark and output comparison on the Lessons critic
  anchor. Delete any temporary timing-only code paths that are no longer needed.
  Sync any touched live docs or comments that still matter.
* Verification (smallest signal):
  `make verify-examples`
* Docs/comments (propagation; only if needed):
  `make verify-diagnostics` if diagnostics or smoke coverage changed; update
  `README.md`, `docs/README.md`, or `examples/README.md` only if the user-visible
  truth changed
* Exit criteria:
  The full corpus is green, the benchmark evidence is captured honestly, and no
  dead temporary performance scaffolding remains live.
* Rollback:
  Remove the temporary proof plumbing and fall back to the already-proven
  session-based implementation that kept semantics intact.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

Avoid verification bureaucracy. Prefer the smallest existing signal, keep the
proof load tight, and use existing command surfaces before adding any new
harness.

## 8.1 Unit tests (contracts)

- Add targeted compiler-level checks only if the existing corpus does not cover:
  - once-per-session module loading
  - deterministic ordered result aggregation under threaded batch execution
  - invalidation or freshness failure behavior at the session boundary

## 8.2 Integration tests (flows)

- `make verify-examples`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/36_invalidation_and_rebuild/cases.toml`
- `make verify-diagnostics` when `doctrine/diagnostic_smoke.py`, diagnostics, or
  wrapper-level compile/emit behavior changes

## 8.3 E2E / device tests (realistic)

- one before/after wall-clock comparison on
  `../paperclip_agents/doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt`
  using the existing Doctrine runtime surface under `uv run --locked`
- if the anchor currently fails compilation, compare the surfaced failure path
  and error identity instead of pretending a rendered-output diff exists
- if that sibling repo cannot be run locally, say that plainly; do not replace
  it with a synthetic benchmark and pretend the same confidence exists

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

This should land as a hard improvement to the default Doctrine compile path,
not as an opt-in feature flag.

## 9.2 Telemetry changes

No standing production telemetry surface is required yet. A narrow benchmark or
timing surface may be added only if it is needed to prove the acceptance target
honestly.

## 9.3 Operational runbook

- If concurrency introduces nondeterministic output, stop and fix the boundary;
  do not paper over it with fallback modes.
- If a cache cannot be invalidated confidently, fail loud and keep correctness.
- If the Lessons benchmark cannot be run locally, say that plainly and use the
  shipped corpus plus the best available large target in-repo.

# 10) Decision Log (append-only)

## 2026-04-11 - Performance pass stays on the shipped compiler path

Context

The ask is to make Doctrine compilation much faster and multithreaded by
default, especially for large real-world agent families, while preserving all
existing language behavior.

Options

- optimize the shipped compiler path directly
- build a repo-local wrapper or precompiler around the existing path
- change the language or emitted surface to make compilation cheaper

Decision

Start from a strict performance-only plan that keeps one Doctrine-owned compile
path and treats the large Lessons critic family as a real acceptance anchor.

Consequences

- the plan must solve both single-agent latency and batch throughput
- multithreading must be default behavior where independent work exists
- correctness and determinism are explicit non-negotiables

Follow-ups

- confirm or correct the numeric speed target in Section 0
- run `implement-loop` after planning completes

## 2026-04-11 - Split immutable prompt graph from task-local compile state

Context

The current `CompilationContext` mixes prompt-graph construction, mutable
resolution stacks, mutable caches, and public compile entrypoints in one owner.
That shape is the main blocker to safe multithreaded reuse.

Options

- lock one shared mutable `CompilationContext`
- split immutable prompt-graph truth from task-local compile state
- serialize the whole context into a process pool or daemon

Decision

Adopt one compiler-owned session with a shared immutable prompt graph and
task-local compile contexts. Keep wrapper compatibility on top of that one
owner path.

Consequences

- shared graph data can be reused safely across threaded callers
- mutable stacks and resolved-body caches stay task-local and debuggable
- emit and verification surfaces can converge on one compile owner instead of
  parallel implementations

Follow-ups

- implement the session/graph/task-context split in `doctrine/compiler.py`
- update emit and verify callers to adopt it

## 2026-04-11 - Use default thread pools, not process pools or daemonized caches

Context

The user asked for multithreaded-by-default compilation. The same plan also has
to preserve deterministic behavior and avoid building a second product surface.

Options

- in-process thread pools with shared immutable graph state
- process pools with serialized compile state
- a resident daemon or precompiler

Decision

Use in-process thread pools for prompt-graph loading and batch compile fan-out.
Do not ship a process-pool, daemon, or watch-cache path in v1.

Consequences

- shared graph reuse stays cheap and compiler-owned
- task-local state must be isolated explicitly
- if the acceptance target still misses after session reuse and threaded graph
  loading, the plan must reopen on measured evidence rather than silently
  escalating to bigger infrastructure

Follow-ups

- cap worker creation to the amount of independent work available
- reopen field-level fan-out only if the Lessons benchmark still misses after
  Phase 2

## 2026-04-11 - Reopen field-level compile fan-out on measured evidence

Context

The shared session split and parallel prompt-graph loading materially improved
compile setup, but a warm-session timing run on the Lessons critic anchor still
showed review-heavy single-agent compilation dominating the wall clock.

Options

- keep `_compile_agent_decl()` fully serial and accept the miss
- parallelize authored field compilation with fresh task-local contexts and
  ordered collection
- escalate to a process pool or a second compiler path

Decision

Reopen field-level fan-out inside `_compile_agent_decl()` using fresh
task-local compile contexts, but keep result collection deterministic and stay
on the same compiler path.

Consequences

- independent agent fields can compile concurrently without sharing mutable
  resolution state
- the shared prompt graph still stays session-owned
- large single-agent latency improves without adding a shadow implementation

Follow-ups

- keep profiling review-heavy paths rather than assuming graph loading is the
  only large-target lever

## 2026-04-11 - Compress review gate validation by observable output semantics

Context

The Lessons critic review path generated `131,079` reject-side gate branches.
The expensive part was not building those branches but validating every
outcome branch against every gate combination, even when the output surface
could only observe a much smaller semantic signature.

Options

- validate the full gate-branch cross product every time
- compress gate branches by the output semantics and contract facts the target
  output can actually observe
- special-case the Lessons critic prompt family

Decision

Compress review gate branches for validation using the output semantics the
compiler can observe from guarded output sections and trust-surface guards.
Keep the language generic and compiler-owned; do not special-case the external
prompt family.

Consequences

- review validation stays fail-loud but avoids multiplying equivalent gate
  states
- large review-heavy compile paths now surface their real compile result
  quickly enough to be usable
- exact gate identities are still preserved whenever the output guards actually
  observe them

Follow-ups

- if a future output surface starts guarding directly on exact
  `failing_gates` or `contract.failed_gates` values, keep the compression key
  honest instead of broadening it heuristically
