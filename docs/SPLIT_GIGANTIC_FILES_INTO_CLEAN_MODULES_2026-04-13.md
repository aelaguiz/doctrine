---
title: "Doctrine - Split Gigantic Files Into Clean Modules - Architecture Plan"
date: 2026-04-13
status: complete
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: phased_refactor
related:
  - AGENTS.md
  - docs/README.md
  - doctrine/compiler.py
  - doctrine/parser.py
  - doctrine/model.py
  - doctrine/diagnostics.py
  - doctrine/diagnostic_smoke.py
  - doctrine/renderer.py
  - doctrine/flow_renderer.py
  - doctrine/verify_corpus.py
  - doctrine/_compiler/context.py
  - doctrine/_compiler/compile.py
  - doctrine/_compiler/resolve.py
  - doctrine/_compiler/validate.py
---

# TL;DR

Outcome

Doctrine will replace the current oversized parser, compiler, diagnostics,
rendering, and corpus-verification owners with smaller, purpose-built modules
that each own one job, plus a short list of intentional large boundaries with
explicit reasons. Success means shipped behavior stays the same, stable public
entrypoints still work, the proof surfaces stay green, and the repo no longer
depends on a handful of 600 to 7,000 line grab-bag files.

Problem

The repo now has several giant functional files far past the `AGENTS.md`
guideline to split files at about 500 lines unless there is a clear reason.
The worst cases are `doctrine/_compiler/validate.py` at about 7,043 lines,
`doctrine/_compiler/resolve.py` at about 6,052 lines,
`doctrine/_compiler/compile.py` at about 3,474 lines, `doctrine/parser.py`
at about 3,198 lines, `doctrine/diagnostic_smoke.py` at about 2,646 lines,
and `doctrine/diagnostics.py` at about 2,537 lines. These files mix many jobs,
hide boundaries, and make safe change harder than it should be.

Approach

Keep stable public boundaries such as [doctrine/compiler.py](../doctrine/compiler.py)
and the current parser and verification entrypoints, then move private logic
behind them into themed packages and modules with clear ownership. Split by
real responsibility, not by arbitrary chunks, and preserve behavior with the
existing shipped corpus, diagnostics checks, and targeted proof only where the
current proof is thin.

Plan

Confirm the North Star, ground the real seams and owner paths in the current
code, then implement in this order: extract shared contracts and helpers,
split model and parser internals, split diagnostics and render internals,
split compiler families, split proof owners, then delete dead broad paths and
run full proof with the public boundaries still in place.

Non-negotiables

- No silent behavior drift.
- No new parallel parser or compiler paths.
- No runtime fallbacks or compatibility shims.
- No giant replacement "utils" modules.
- Keep fail-loud compiler behavior.
- Keep stable public entrypoints simple and intentional.
- Use real proof, not repo-policing tests or doc-only checks.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-13
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None. `uv sync`, `npm ci`, `uv run --locked python -m unittest
  tests.test_compiler_boundary tests.test_parse_diagnostics
  tests.test_verify_corpus tests.test_final_output
  tests.test_route_output_semantics tests.test_review_imported_outputs
  tests.test_decision_attachment`, `make verify-diagnostics`, and
  `make verify-examples` all passed on 2026-04-13.

## Reopened phases (false-complete fixes)
- None. Phase 4 and Phase 6 close cleanly now that the full proof is green
  and Section 7 records the remaining intentional 500+ boundary owners.

## Missing items (code gaps; evidence-anchored; no tables)
- None. The original monolith files are gone, the root public boundaries are
  thin again, wildcard-import cleanup landed, and the remaining 500+ owners
  now have explicit final-boundary reasons recorded in Section 7.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- none
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-13
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-13
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine splits its current giant functional files into smaller, purpose-
built modules while keeping stable public boundaries in place, then a
contributor should be able to trace parser, compiler, diagnostics, renderer,
flow-render, and corpus-verification behavior through clear owner modules
instead of multi-thousand-line files, and the shipped proof surfaces should
still pass without user-visible regressions.

This plan is successful only if:

- the oversized mixed-responsibility files are replaced by cleaner module sets
  with explicit ownership
- stable public entrypoints still work for current callers
- `make verify-examples` still passes
- `make verify-diagnostics` still passes when diagnostics code changes
- any remaining functional file above about 500 lines has a clear written
  reason and acts as a real boundary, not a catch-all

## 0.2 In scope

- Splitting the current oversized functional owners in `doctrine/` and
  `doctrine/_compiler/` into focused modules and packages.
- Preserving current language behavior, diagnostics behavior, renderer output,
  flow-render behavior, and corpus-verification behavior unless a deliberate
  bug fix is approved and recorded.
- Keeping stable public entrypoints simple, including the public compiler
  facade in [doctrine/compiler.py](../doctrine/compiler.py) and the current
  parse and verify entrypoints.
- Moving private helpers, data types, and pass-specific logic into clearer
  owner modules with better names and tighter imports.
- Updating touched docs, comments, and instructions when module ownership or
  contributor guidance changes.
- Adding narrow behavior-preservation proof only when the current corpus and
  diagnostics surfaces are not enough for a risky refactor slice.
- Architectural convergence needed to remove duplicate truth, shadow helpers,
  and mixed-responsibility modules along the chosen canonical paths.

## 0.3 Out of scope

- New Doctrine language features, syntax, or semantic changes.
- New user-facing commands, modes, config systems, or plugin layers.
- Runtime compatibility shims that keep old private paths alive.
- Renaming stable public entrypoints without a strong need recorded in the
  plan.
- Performance work that is not required by the modularization itself.
- A docs-only cleanup that leaves the code structure unchanged.

## 0.4 Definition of done (acceptance evidence)

- The plan names the future owner paths for the parser, compiler internals,
  diagnostics, smoke coverage, rendering, flow rendering, verification, and
  model surfaces that actually need to move.
- The implementation removes the current giant mixed-responsibility files or
  shrinks them into narrow boundary modules with clear purpose.
- Stable public entrypoints still serve current callers after the refactor.
- `make verify-examples` passes after the code move.
- `make verify-diagnostics` passes for any phase that changes diagnostics.
- Touched docs and instructions match the new module ownership and proof story.
- Any remaining large file has an explicit reason that matches the `AGENTS.md`
  rule instead of drifting there by accident.

## 0.5 Key invariants (fix immediately if violated)

- No silent behavior drift during refactors.
- No second source of truth for parser, compiler, diagnostics, or verification
  behavior.
- No new parallel code paths left behind after a move.
- No fallbacks or runtime shims unless explicitly approved later in the
  Decision Log.
- Keep fail-loud compiler behavior and current proof expectations.
- Split by real responsibility. Do not replace one giant file with one giant
  helper package that still mixes many jobs.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Preserve shipped behavior first.
2. Put each job behind one clear owner module.
3. Keep stable public boundaries simple for callers.
4. Remove mixed-responsibility files instead of hiding them behind re-exports.
5. Keep proof lean and behavior-focused.
6. Keep docs and contributor guidance aligned with the new layout.

## 1.2 Constraints

- `AGENTS.md` says functional code files past about 500 lines should be split
  unless there is a clear reason not to.
- Shipped truth lives in `doctrine/` and the manifest-backed corpus.
- The repo already has a stable public compiler facade in
  [doctrine/compiler.py](../doctrine/compiler.py).
- Compiler behavior currently routes through
  [doctrine/_compiler/context.py](../doctrine/_compiler/context.py), which
  mixes large helper owners through mixins.
- The main proof surface is `make verify-examples`.
- Diagnostics changes require `make verify-diagnostics`.

## 1.3 Architectural principles (rules we will enforce)

- Split by ownership and lifecycle, not by arbitrary line counts alone.
- Keep one canonical owner path for each concern.
- Public facades may stay small and stable while internals move behind them.
- Prefer a few clear modules over broad `shared`, `helpers`, or `utils`
  dumping grounds.
- Keep fail-loud boundaries and type-rich contracts.
- Delete superseded private paths instead of keeping both old and new paths.

## 1.4 Known tradeoffs (explicit)

- More files will make navigation better, but import boundaries will need more
  care.
- Some public re-export modules may stay small on purpose.
- Refactoring large compiler mixins may require temporary internal churn before
  the final ownership gets cleaner.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- The repo has several oversized functional files that each mix many jobs:
  - `doctrine/_compiler/validate.py` at about 7,043 lines
  - `doctrine/_compiler/resolve.py` at about 6,052 lines
  - `doctrine/_compiler/compile.py` at about 3,474 lines
  - `doctrine/parser.py` at about 3,198 lines
  - `doctrine/diagnostic_smoke.py` at about 2,646 lines
  - `doctrine/diagnostics.py` at about 2,537 lines
  - `doctrine/model.py` at about 1,443 lines
  - `doctrine/verify_corpus.py` at about 888 lines
  - `doctrine/renderer.py` at about 680 lines
  - `doctrine/flow_renderer.py` at about 613 lines
- The compiler already uses a façade-plus-mixins shape:
  [doctrine/_compiler/context.py](../doctrine/_compiler/context.py) composes
  `FlowMixin`, `ValidateMixin`, `CompileMixin`, `DisplayMixin`, and
  `ResolveMixin`, but the biggest mixins are still monoliths.
- The parser keeps many positioned-part dataclasses, the `ToAst`
  transformer, parser construction, and file loading in one file.
- The proof surfaces already exist, but they currently guard behavior at a
  higher level than module ownership.

## 2.2 What's broken / missing (concrete)

- The current file sizes violate the repo's own small-file direction unless a
  clear reason exists, and most of these files do not look like narrow
  boundary modules.
- Mixed-responsibility files make it hard to see ownership, hard to review
  safely, and easy to create shadow helpers or duplicate logic.
- The compiler mixin split is only partial. The largest owners still hide many
  different concerns behind one file each.
- The diagnostics and smoke surfaces are hard to extend cleanly because each
  file carries too many unrelated cases and formatting rules.

## 2.3 Constraints implied by the problem

- The refactor must preserve current user-visible behavior.
- The work must keep stable entrypoints intact unless a stronger reason is
  documented later.
- The plan needs an exhaustive call-site inventory before implementation so
  moved helpers do not leave stale paths behind.

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- Python package facade pattern — adopt a small public module over internal
  owners — Doctrine already does this in
  [doctrine/compiler.py](../doctrine/compiler.py), so the refactor should keep
  that boundary instead of forcing callers onto private modules.
- Typed contract modules — adopt one clear home for shared data contracts —
  this matches [doctrine/_compiler/types.py](../doctrine/_compiler/types.py)
  and argues for more narrow contract owners instead of broad helper files.
- Internal modularization over framework churn — adopt repo-first ownership
  cleanup and reject generic new service layers or plugin systems — this job
  is about making Doctrine's current code clearer, not changing how users call
  it.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - [doctrine/compiler.py](../doctrine/compiler.py) — stable public compiler
    boundary. It re-exports the real compile owners under `doctrine._compiler`.
  - [doctrine/_compiler/session.py](../doctrine/_compiler/session.py) —
    stable internal compile session boundary. It owns prompt-root resolution,
    project config loading, module loading, and per-task context creation.
  - [doctrine/_compiler/context.py](../doctrine/_compiler/context.py) —
    task-local compile boundary. It is the current place where compile helper
    families meet.
  - [doctrine/parser.py](../doctrine/parser.py) — public parse entrypoints,
    parser construction, transformer, and many positioned parse helpers.
  - [doctrine/model.py](../doctrine/model.py) — canonical authored AST and
    declaration data model used across parse, compile, and render.
  - [doctrine/diagnostics.py](../doctrine/diagnostics.py) — canonical
    diagnostic data model, formatting, excerpt building, and stage-specific
    errors.
  - [doctrine/renderer.py](../doctrine/renderer.py) — canonical markdown
    rendering owner for compiled readable blocks.
  - [doctrine/flow_renderer.py](../doctrine/flow_renderer.py) — canonical flow
    rendering owner and pinned `d2` dependency boundary.
  - [doctrine/verify_corpus.py](../doctrine/verify_corpus.py) — canonical
    shipped corpus verification surface and manifest loading flow.
  - [doctrine/diagnostic_smoke.py](../doctrine/diagnostic_smoke.py) —
    canonical direct smoke surface for many exact error and render behaviors.
- Canonical path / owner to reuse:
  - [doctrine/compiler.py](../doctrine/compiler.py) — keep as the public
    compiler facade even if internals move into smaller modules.
  - [doctrine/parser.py](../doctrine/parser.py) — keep as the public parse
    facade even if parser internals move behind it.
  - [doctrine/diagnostics.py](../doctrine/diagnostics.py) — keep as the public
    diagnostics facade and error-contract owner.
  - [doctrine/_compiler/session.py](../doctrine/_compiler/session.py) +
    [doctrine/_compiler/context.py](../doctrine/_compiler/context.py) —
    current internal compile owner pair to deepen and clean up, not replace
    with a new service layer.
- Existing patterns to reuse:
  - [doctrine/compiler.py](../doctrine/compiler.py) +
    [doctrine/_compiler/session.py](../doctrine/_compiler/session.py) — thin
    public facade over internal owners.
  - [doctrine/_compiler/types.py](../doctrine/_compiler/types.py) — one clear
    contract home for compiled data shared by compiler, renderer, and flow
    renderer.
  - [doctrine/_compiler/support.py](../doctrine/_compiler/support.py) — small
    focused helper owner with a clear job.
  - [doctrine/_compiler/display.py](../doctrine/_compiler/display.py) and
    [doctrine/_compiler/flow.py](../doctrine/_compiler/flow.py) — proof that
    smaller concern-based compiler owners already fit this repo.
  - [doctrine/__init__.py](../doctrine/__init__.py) — small bootstrap export
    surface that avoids leaking internal layout.
- Prompt surfaces / agent contract to reuse:
  - Not applicable. This is parser and compiler structure work, not agent
    runtime behavior.
- Native model or agent capabilities to lean on:
  - Not applicable. The main leverage is code ownership and existing proof.
- Existing grounding / tool / file exposure:
  - Import search shows [doctrine/parser.py](../doctrine/parser.py),
    [doctrine/compiler.py](../doctrine/compiler.py),
    [doctrine/diagnostics.py](../doctrine/diagnostics.py),
    [doctrine/renderer.py](../doctrine/renderer.py), and
    [doctrine/flow_renderer.py](../doctrine/flow_renderer.py) are already used
    by emit commands, verification, smoke checks, and tests. These are real
    boundaries, not private implementation details.
  - [tests/test_compiler_boundary.py](../tests/test_compiler_boundary.py) —
    public compiler API boundary proof.
  - [tests/test_parse_diagnostics.py](../tests/test_parse_diagnostics.py) —
    parse API and parse error proof.
  - [tests/test_verify_corpus.py](../tests/test_verify_corpus.py) —
    corpus-verification behavior proof.
  - `make verify-examples` — broad shipped proof across the numbered corpus.
  - `make verify-diagnostics` — direct smoke proof for diagnostics behavior.
- Duplicate or drifting paths relevant to this change:
  - [doctrine/_compiler/shared.py](../doctrine/_compiler/shared.py) is a very
    broad dependency hub. Every main mixin and
    [doctrine/_compiler/context.py](../doctrine/_compiler/context.py) imports
    from it, often with wildcard imports. It is the clearest current gravity
    well and a likely source of ownership drift.
  - [doctrine/parser.py](../doctrine/parser.py) mixes many dataclasses,
    helper functions, the `ToAst` transformer, parser setup, and file
    entrypoints in one owner.
  - [doctrine/diagnostics.py](../doctrine/diagnostics.py) mixes the diagnostic
    data model, formatting, excerpt building, parse-error conversion, and
    message-to-diagnostic helpers.
  - [doctrine/diagnostic_smoke.py](../doctrine/diagnostic_smoke.py) is one
    long linear smoke battery with many unrelated concerns but one main entry
    command.
  - [doctrine/model.py](../doctrine/model.py) holds many feature families in
    one file. Any split must avoid import cycles and must not blur the authored
    model contract.
- Capability-first opportunities before new tooling:
  - Extend the repo's current facade pattern instead of inventing a new
    framework or service layer.
  - Reuse existing proof commands before adding any new harness.
  - Prefer small themed packages under `doctrine/` and `doctrine/_compiler/`
    over one new catch-all `utils` or `common` package.
  - Keep stable public entrypoints and move private internals behind them.
- Behavior-preservation signals already available:
  - `make verify-examples` — shipped corpus proof for parse, compile, render,
    emit, and many cross-module behaviors.
  - `make verify-diagnostics` — exact diagnostic smoke proof when diagnostics
    surfaces move.
  - [tests/test_compiler_boundary.py](../tests/test_compiler_boundary.py) —
    public compile boundary proof.
  - [tests/test_parse_diagnostics.py](../tests/test_parse_diagnostics.py) —
    parse failure behavior proof.
  - [tests/test_verify_corpus.py](../tests/test_verify_corpus.py) —
    verification engine proof.

## 3.3 Decision gaps that must be resolved before implementation

Deep-dive passes 1 and 2 resolve the main architecture choices. No user
blocker question remains. The chosen target is:

- Keep the current root public modules as stable boundaries.
- Split giant internals behind those boundaries into themed packages and
  purpose-built modules.
- Keep [doctrine/_compiler/session.py](../doctrine/_compiler/session.py) and
  [doctrine/_compiler/context.py](../doctrine/_compiler/context.py) as the
  orchestration pair.
- Retire [doctrine/_compiler/shared.py](../doctrine/_compiler/shared.py) as a
  broad catch-all by moving its contracts, constants, naming helpers, and
  support helpers into narrower owners.

Deep-dive pass 2 resolves the remaining architecture-hardening choices:

- move pure contracts and shared helper survivors first
- keep root public boundaries stable until the end
- do not keep a long-lived `_compiler/shared.py` compatibility bridge
- keep proof on public boundaries and shipped commands, not private modules

The doc is ready for `implement`. No user blocker question remains unless repo
truth changes during implementation.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- [doctrine/compiler.py](../doctrine/compiler.py) is already a small public
  compile boundary. It re-exports `CompilationSession`,
  `compile_prompt`, `extract_target_flow_graph`, and many public compile
  types from internal owners.
- [doctrine/parser.py](../doctrine/parser.py) is a single large parser owner.
  It mixes positioned parse parts, helper functions, the `ToAst`
  transformer, parser construction, and file entrypoints.
- [doctrine/model.py](../doctrine/model.py) is one large authored AST and
  declaration contract file. It covers core syntax nodes, law nodes, readable
  nodes, workflow nodes, review nodes, IO nodes, schema nodes, and agent
  nodes.
- [doctrine/diagnostics.py](../doctrine/diagnostics.py) is one large
  diagnostics owner. It mixes the diagnostic data model, string formatting,
  source excerpt building, parse-error conversion, and message-based
  diagnostic builders.
- [doctrine/renderer.py](../doctrine/renderer.py) is one large markdown
  renderer over compiled readable blocks.
- [doctrine/flow_renderer.py](../doctrine/flow_renderer.py) is one large D2
  and SVG renderer plus lane-planning owner.
- [doctrine/verify_corpus.py](../doctrine/verify_corpus.py) is one large
  verification engine. It mixes CLI parsing, manifest parsing, case models,
  compile and emit runners, diff building, and report formatting.
- [doctrine/diagnostic_smoke.py](../doctrine/diagnostic_smoke.py) is one large
  smoke runner. It holds the command entrypoint, many direct behavior checks,
  many inline source builders, and shared assertion helpers.
- The internal compiler package is partly modular already:
  [doctrine/_compiler/session.py](../doctrine/_compiler/session.py),
  [doctrine/_compiler/context.py](../doctrine/_compiler/context.py),
  [doctrine/_compiler/types.py](../doctrine/_compiler/types.py),
  [doctrine/_compiler/support.py](../doctrine/_compiler/support.py),
  [doctrine/_compiler/indexing.py](../doctrine/_compiler/indexing.py),
  [doctrine/_compiler/display.py](../doctrine/_compiler/display.py), and
  [doctrine/_compiler/flow.py](../doctrine/_compiler/flow.py) are narrower.
- The largest compiler files still dominate the package:
  [doctrine/_compiler/compile.py](../doctrine/_compiler/compile.py),
  [doctrine/_compiler/resolve.py](../doctrine/_compiler/resolve.py), and
  [doctrine/_compiler/validate.py](../doctrine/_compiler/validate.py).
- [doctrine/_compiler/shared.py](../doctrine/_compiler/shared.py) is the main
  dependency hub. The major mixin files and
  [doctrine/_compiler/context.py](../doctrine/_compiler/context.py) all import
  from it, often with wildcard imports.

## 4.2 Control paths (runtime)

1. Parse path:
   [doctrine/parser.py](../doctrine/parser.py) builds a thread-local Lark
   parser, parses source into a tree, runs `ToAst`, and returns
   `model.PromptFile`.
2. Compile path:
   callers import the public boundary in
   [doctrine/compiler.py](../doctrine/compiler.py), which delegates to
   [doctrine/_compiler/session.py](../doctrine/_compiler/session.py). The
   session builds the root `IndexedUnit`, then creates a fresh
   [doctrine/_compiler/context.py](../doctrine/_compiler/context.py) per task.
3. Internal compiler path:
   `CompilationContext` composes `FlowMixin`, `ValidateMixin`, `CompileMixin`,
   `DisplayMixin`, and `ResolveMixin`. Those owners depend on
   [doctrine/_compiler/shared.py](../doctrine/_compiler/shared.py),
   [doctrine/_compiler/types.py](../doctrine/_compiler/types.py),
   [doctrine/_compiler/indexing.py](../doctrine/_compiler/indexing.py), and
   [doctrine/_compiler/support.py](../doctrine/_compiler/support.py).
4. Emit path:
   [doctrine/emit_docs.py](../doctrine/emit_docs.py),
   [doctrine/emit_flow.py](../doctrine/emit_flow.py), and
   [doctrine/emit_skill.py](../doctrine/emit_skill.py) call the public parse
   and compile boundaries, then render or emit files.
5. Render path:
   [doctrine/renderer.py](../doctrine/renderer.py) renders compiled readable
   blocks from [doctrine/_compiler/types.py](../doctrine/_compiler/types.py).
   [doctrine/flow_renderer.py](../doctrine/flow_renderer.py) renders `FlowGraph`
   output from the compiler flow path and optionally shells out to the pinned
   `d2` renderer.
6. Verification path:
   [doctrine/verify_corpus.py](../doctrine/verify_corpus.py) parses manifests,
   runs parse, compile, render, and emit behavior, then diffs actual artifacts
   against checked-in refs.
7. Smoke path:
   [doctrine/diagnostic_smoke.py](../doctrine/diagnostic_smoke.py) calls
   public parse, compile, render, emit, and flow boundaries directly to lock
   exact behavior.

## 4.3 Object model + key abstractions

- [doctrine/model.py](../doctrine/model.py) is the canonical authored AST
  contract. `PromptFile` and nearly every declaration family live there.
- [doctrine/_compiler/indexing.py](../doctrine/_compiler/indexing.py) builds
  `IndexedUnit`, which is the registry view the compiler uses for named lookups
  and import resolution.
- [doctrine/_compiler/session.py](../doctrine/_compiler/session.py) is the
  stable compile-session owner. It resolves project config, prompt roots,
  import roots, and module loads.
- [doctrine/_compiler/context.py](../doctrine/_compiler/context.py) is the
  task-local orchestration owner. It holds resolution stacks and caches for one
  compile task.
- [doctrine/_compiler/types.py](../doctrine/_compiler/types.py) is already the
  canonical owner for compiled output contracts used by compiler, renderer, and
  flow renderer.
- [doctrine/_compiler/shared.py](../doctrine/_compiler/shared.py) still owns a
  mixed set of resolved contracts, keys, constants, regexes, naming helpers,
  and nested compile helpers. That file is the least clean object-model owner
  in the compiler package.
- [doctrine/diagnostics.py](../doctrine/diagnostics.py) owns
  `DoctrineDiagnostic`, `DoctrineError`, and the stage-specific error classes.
- [doctrine/compiler.py](../doctrine/compiler.py) exposes a stable public
  `__all__` surface. `tests/test_compiler_boundary.py` proves that this module
  must not leak accidental helper imports.

## 4.4 Observability + failure behavior today

- Parse failures raise `ParseError` with exact codes, excerpts, and source
  locations.
- Compile failures raise `CompileError` and preserve trace information through
  the public compiler boundary.
- Emit failures raise `EmitError`.
- [doctrine/flow_renderer.py](../doctrine/flow_renderer.py) raises
  `FlowRenderDependencyError` when the pinned D2 dependency is missing and
  `FlowRenderFailure` when SVG rendering fails.
- [doctrine/verify_corpus.py](../doctrine/verify_corpus.py) raises
  `ManifestError` or `VerificationError` when corpus proof fails.
- The main preservation signals already exist:
  `make verify-examples`, `make verify-diagnostics`,
  [tests/test_compiler_boundary.py](../tests/test_compiler_boundary.py),
  [tests/test_parse_diagnostics.py](../tests/test_parse_diagnostics.py), and
  [tests/test_verify_corpus.py](../tests/test_verify_corpus.py).
- There is no current proof surface that cares about file size or module
  ownership directly. That means the refactor must preserve behavior while the
  plan itself carries the structure decisions.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not UI work. The user-facing surfaces are public Python boundaries, emitted
artifacts, docs, and proof commands.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Keep these root modules as stable public boundaries:
  [doctrine/compiler.py](../doctrine/compiler.py),
  [doctrine/parser.py](../doctrine/parser.py),
  [doctrine/model.py](../doctrine/model.py),
  [doctrine/diagnostics.py](../doctrine/diagnostics.py),
  [doctrine/renderer.py](../doctrine/renderer.py),
  [doctrine/flow_renderer.py](../doctrine/flow_renderer.py),
  [doctrine/verify_corpus.py](../doctrine/verify_corpus.py), and
  [doctrine/diagnostic_smoke.py](../doctrine/diagnostic_smoke.py).
- Each of those root files should end as a thin boundary module or a small
  command runner. They should not keep large mixed-responsibility internals.
- Add `doctrine/_parser/` as the internal parser package. Its first owner
  modules should be:
  `parts.py`, `transformer.py`, and `runtime.py`.
- Add `doctrine/_model/` as the internal authored-model package. Its grouped
  owners should cover:
  `core.py`, `law.py`, `readable.py`, `workflow.py`, `schema.py`, `review.py`,
  `io.py`, and `agent.py`.
- Add `doctrine/_diagnostics/` as the internal diagnostics package. Its first
  owner modules should be:
  `contracts.py`, `formatting.py`, `parse_errors.py`, and
  `message_builders.py`.
- Add `doctrine/_renderer/` as the internal markdown-render package. Its first
  owner modules should be:
  `blocks.py`, `tables.py`, and `semantic.py`.
- Add `doctrine/_flow_render/` as the internal flow-render package. Its first
  owner modules should be:
  `layout.py` for lane planning and graph layout data,
  `d2.py` for D2 text emission, and
  `svg.py` for SVG rendering helpers.
- Add `doctrine/_verify_corpus/` as the internal corpus-verification package.
  Its first owner modules should be:
  `manifest.py`, `runners.py`, `diff.py`, and `report.py`.
- Add `doctrine/_diagnostic_smoke/` as the internal smoke package. Its first
  owner modules should be:
  `parse_checks.py`, `compile_checks.py`, `review_checks.py`, `emit_checks.py`,
  `flow_checks.py`, and `fixtures.py`.
- Keep [doctrine/_compiler/session.py](../doctrine/_compiler/session.py),
  [doctrine/_compiler/context.py](../doctrine/_compiler/context.py),
  [doctrine/_compiler/types.py](../doctrine/_compiler/types.py),
  [doctrine/_compiler/support.py](../doctrine/_compiler/support.py),
  [doctrine/_compiler/indexing.py](../doctrine/_compiler/indexing.py),
  [doctrine/_compiler/display.py](../doctrine/_compiler/display.py), and
  [doctrine/_compiler/flow.py](../doctrine/_compiler/flow.py) as the internal
  orchestration and contract owners.
- [doctrine/_compiler/__init__.py](../doctrine/_compiler/__init__.py) stays an
  internal package marker only. It does not become a second public facade.
- Split the giant compiler families into internal packages:
  `doctrine/_compiler/compile/`,
  `doctrine/_compiler/resolve/`, and
  `doctrine/_compiler/validate/`.
- The first owner modules under those packages should follow the existing
  concern lines instead of arbitrary chunks:
  `agent.py`, `readables.py`, `final_output.py`, and `skill_package.py` under
  compile;
  `refs.py`, `workflows.py`, `outputs.py`, `reviews.py`, and `schemas.py`
  under resolve;
  `agents.py`, `outputs.py`, `reviews.py`, `routes.py`, and `readables.py`
  under validate.
- Retire [doctrine/_compiler/shared.py](../doctrine/_compiler/shared.py) as a
  catch-all. Its surviving owners should be explicit:
  `resolved_types.py`, `constants.py`, `naming.py`, and
  `support_files.py`.

## 5.2 Control paths (future)

1. Public parse calls stay at
   [doctrine/parser.py](../doctrine/parser.py), but that file delegates to
   `doctrine._parser` owners.
2. Public compile calls stay at
   [doctrine/compiler.py](../doctrine/compiler.py), which keeps an explicit
   `__all__` and imports only from stable owner modules.
3. [doctrine/_compiler/session.py](../doctrine/_compiler/session.py) remains
   the compile-session owner. It still creates one fresh
   [doctrine/_compiler/context.py](../doctrine/_compiler/context.py) per task.
4. `CompilationContext` remains the task-local orchestrator. It may keep mixin
   facades, but those facades must delegate to themed modules inside
   `doctrine._compiler.compile`, `doctrine._compiler.resolve`, and
   `doctrine._compiler.validate`.
5. `renderer.py` and `flow_renderer.py` continue consuming compiled contracts,
   not compiler helper internals. `doctrine._flow_render.layout` becomes the
   canonical home for lane planning and flow layout helpers.
6. Emit and verification commands continue importing only the public root
   boundaries plus narrow support owners they already use.
7. Smoke and test surfaces continue proving behavior through public boundaries,
   not by reaching into private split modules.
8. Hard migration order for implementation:
   - first move pure contracts, constants, naming helpers, and support-file
     helpers out of `_compiler/shared.py`
   - then repoint internal imports to those explicit owners
   - then split the giant parser, diagnostics, compiler, renderer, verifier,
     and smoke files behind their stable boundaries
   - finally delete dead broad owners and any temporary internal landing files
     in the same phase they stop carrying real ownership

## 5.3 Object model + abstractions (future)

- [doctrine/model.py](../doctrine/model.py) remains the public authored-model
  facade. The actual family definitions move under `doctrine._model`.
- [doctrine/_compiler/types.py](../doctrine/_compiler/types.py) stays the
  canonical compiled-contract owner.
- `doctrine._compiler.resolved_types` becomes the canonical owner for resolved
  intermediary contracts now mixed into `shared.py`.
- [doctrine/_compiler/indexing.py](../doctrine/_compiler/indexing.py) stays the
  owner of `IndexedUnit`, import indexing, and declaration registries.
- [doctrine/diagnostics.py](../doctrine/diagnostics.py) remains the public
  diagnostics facade. The formatting and parse-message machinery move under
  `doctrine._diagnostics`.
- [doctrine/compiler.py](../doctrine/compiler.py) keeps the stable public
  export list, but it imports those names directly from their final owners
  instead of routing through a broad internal catch-all.

## 5.4 Invariants and boundaries

- No change to the public import paths above unless a later plan entry
  explicitly approves it.
- No new parallel old-versus-new logic paths. When a concern moves, the old
  private owner is deleted after callers move.
- No broad `shared`, `common`, or `utils` dumping ground replaces the current
  large files.
- No wildcard import dependence on a broad catch-all module in the final
  state.
- `CompilationSession` and `CompilationContext` stay the orchestration pair.
- `renderer.py` and `flow_renderer.py` depend on compiled contracts, not on
  compiler helper internals.
- `verify_corpus.py` and `diagnostic_smoke.py` stay behavior-first proof
  surfaces.
- `_compiler/shared.py` may not survive as a renamed broad catch-all. Its
  survivors must move into explicit owner modules.
- Tests should keep proving public boundaries. They should not migrate to the
  private split packages except for narrow internal-owner tests that prove new
  contracts.
- Avoid cross-package cycles between `_parser`, `_model`, `_diagnostics`, and
  `_compiler`.
- Any intentional boundary file that remains above about 500 lines must have a
  clear reason recorded in the plan or worklog.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not UI work. The architectural surface is Python module ownership and proof
flow.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Public compile boundary | `doctrine/compiler.py` | `CompilationSession`, `compile_prompt`, `extract_target_flow_graph`, `__all__` | Small public facade, but it still re-exports many names through `_compiler.shared` | Keep file and import path stable; switch to explicit imports from final owner modules; preserve `__all__` and leak protection | Downstream callers and tests bind here today | Public API unchanged | `tests/test_compiler_boundary.py`, `doctrine/diagnostic_smoke.py`, `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, `doctrine/verify_corpus.py` |
| Compile session | `doctrine/_compiler/session.py` | `CompilationSession`, top-level compile helpers | Stable internal session owner and public behavior bridge | Keep as canonical session owner; update only for new internal module paths | It already owns project config, prompt roots, and task creation cleanly | API unchanged | `tests/test_compiler_boundary.py`, `tests/test_import_loading.py`, broad compile behavior tests |
| Compile context | `doctrine/_compiler/context.py` | `CompilationContext` | Task-local orchestrator with caches and stacks plus mixin composition | Keep as thin orchestrator; delegate large concern families to split internal modules | This is the right task boundary already | Internal contract unchanged | Broad compile, render, and route tests |
| Internal package marker | `doctrine/_compiler/__init__.py` | Package docstring boundary | Internal package marker only | Keep narrow; do not grow public exports or helper glue here | Avoids a second accidental public facade | Internal marker only | `tests/test_compiler_boundary.py` by implication |
| Compiled contracts | `doctrine/_compiler/types.py` | Compiled dataclasses and `FlowGraph` contracts | Already a clear shared contract owner | Keep as the canonical compiled-contract owner; only move non-compiled resolved contracts out of `shared.py` into explicit owners | Renderer and flow renderer already depend on this shape | Public internal contract tightened, not broadened | `doctrine/renderer.py`, `doctrine/flow_renderer.py`, `make verify-examples` |
| Compiler support helpers | `doctrine/_compiler/support.py` | path, prompt-root, worker-count helpers | Small focused helper owner | Keep owner narrow; absorb only support helpers that truly belong with file and path operations | Prevents a new broad helper hub | Internal API may expand slightly but stays support-only | Broad compile and verify surfaces |
| Indexing registry | `doctrine/_compiler/indexing.py` | `IndexedUnit`, declaration registries, import loading | Registry and import index owner | Keep owner stable; update imports and type references as authored model modules split | This is already a real single-purpose owner | Internal API unchanged | `make verify-examples`, import-loading tests |
| Shared compiler hub | `doctrine/_compiler/shared.py` | Resolved contracts, constants, naming helpers, support helpers | Broad catch-all hub with wildcard import dependence | Move survivors into `resolved_types.py`, `constants.py`, `naming.py`, and `support_files.py`; delete broad hub by end | This is the main ownership gravity well | Internal API becomes explicit owner imports | `tests/test_compiler_boundary.py`, `make verify-examples`, `make verify-diagnostics` |
| Compile family | `doctrine/_compiler/compile.py` | `CompileMixin` helpers | One very large concern family file | Split into `doctrine/_compiler/compile/` owner modules and leave only a thin family facade if needed during migration | Mixed responsibilities hide boundaries | Internal API unchanged at context boundary | `tests/test_final_output.py`, `tests/test_review_imported_outputs.py`, `tests/test_decision_attachment.py`, `make verify-examples` |
| Resolve family | `doctrine/_compiler/resolve.py` | `ResolveMixin` helpers | One very large concern family file | Split into `doctrine/_compiler/resolve/` owner modules | Name resolution, final output, and workflow resolution need narrower owners | Internal API unchanged at context boundary | `tests/test_route_output_semantics.py`, `tests/test_final_output.py`, `make verify-examples` |
| Validate family | `doctrine/_compiler/validate.py` | `ValidateMixin` helpers | One very large concern family file | Split into `doctrine/_compiler/validate/` owner modules | Validation rules are too wide for safe review today | Internal API unchanged at context boundary | `tests/test_route_output_semantics.py`, `tests/test_final_output.py`, `doctrine/diagnostic_smoke.py`, `make verify-examples` |
| Narrow compiler families | `doctrine/_compiler/display.py`, `doctrine/_compiler/flow.py` | `DisplayMixin`, `FlowMixin` | Already narrower than the giant mixins, but still import from `shared.py` | Keep the owner split; repoint imports to explicit contracts and helpers | Preserves a good existing pattern while removing the hub | Internal API unchanged | `make verify-examples`, flow and render smoke checks |
| Parser boundary | `doctrine/parser.py` | `parse_file`, `parse_text`, `build_lark_parser`, `ToAst` | Public parse API and all parser internals in one file | Keep `parse_file` and `parse_text` stable; move helper parts and transformer internals to `doctrine._parser` | Parser is a major shipped truth surface and must stay easy to find | Public parse API unchanged | `tests/test_parse_diagnostics.py`, `doctrine/diagnostic_smoke.py`, `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, `doctrine/verify_corpus.py` |
| Authored model boundary | `doctrine/model.py` | `PromptFile` and declaration dataclasses | One giant authored AST contract file | Keep public module path stable; move family definitions to `doctrine._model` grouped by domain | The authored model is central and must stay explicit, not monolithic | Public model API unchanged | Broad parse, compile, render, and verify surfaces |
| Diagnostics boundary | `doctrine/diagnostics.py` | `DoctrineDiagnostic`, error classes, `format_diagnostic`, `diagnostic_to_dict` | Public diagnostics API and all formatting internals in one file | Keep public module path stable; move formatting and message builders to `doctrine._diagnostics` | Error contracts are shipped behavior and must stay stable | Public diagnostics API unchanged | `tests/test_parse_diagnostics.py`, `tests/test_verify_corpus.py`, `doctrine/diagnostic_smoke.py`, `make verify-diagnostics` |
| Markdown renderer | `doctrine/renderer.py` | `render_markdown`, `render_readable_block` | Public renderer plus all block rendering helpers in one file | Keep public functions stable; move block and semantic helpers to `doctrine._renderer` | Renderer is called from emit, verify, smoke, and tests | Public renderer API unchanged | `tests/test_final_output.py`, `tests/test_review_imported_outputs.py`, `doctrine/emit_docs.py`, `doctrine/verify_corpus.py` |
| Flow renderer | `doctrine/flow_renderer.py` | `ensure_pinned_d2_dependency`, `render_flow_d2`, `render_flow_svg` | Public flow-render API plus all layout and D2 helpers in one file | Keep public functions stable; move lane planning and graph layout helpers into `doctrine._flow_render/layout.py`, move D2 text emission into `doctrine._flow_render/d2.py`, and move SVG helpers into `doctrine._flow_render/svg.py` | This is a real public helper surface and a pinned dependency boundary | Public flow-render API unchanged | `doctrine/emit_flow.py`, `doctrine/verify_prereqs.py`, `doctrine/diagnostic_smoke.py` |
| Corpus verification | `doctrine/verify_corpus.py` | `verify_corpus`, manifest and diff helpers | CLI, manifest parsing, runners, diffing, and reporting in one file | Keep public function and CLI path stable; move internals to `doctrine._verify_corpus` | This is the main shipped proof engine | Public API unchanged | `tests/test_verify_corpus.py`, `make verify-examples` |
| Diagnostic smoke | `doctrine/diagnostic_smoke.py` | `main`, `_check_*`, inline source builders | One long linear smoke runner | Keep CLI path stable; split checks and fixtures into `doctrine._diagnostic_smoke` modules | This file is too large and mixes unrelated proof concerns | Public CLI unchanged | `make verify-diagnostics` |
| Emit entry surfaces | `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, `doctrine/emit_skill.py` | parse and compile imports | Entry surfaces already import public boundaries | Keep them on public boundaries only while internal modules move | They are boundary consumers and should not depend on private split layout | Public behavior unchanged | `tests/test_emit_docs.py`, `doctrine/diagnostic_smoke.py`, `doctrine/verify_corpus.py` |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  public callers keep using the root `doctrine/*.py` boundaries; internal code
  converges on `doctrine._parser`, `doctrine._model`, `doctrine._diagnostics`,
  `doctrine._renderer`, `doctrine._flow_render`, `doctrine._verify_corpus`,
  `doctrine._diagnostic_smoke`, and narrower `doctrine._compiler.*` owners.
- Migration order constraints:
  move pure contracts and helper survivors first; repoint imports second;
  split large behavior owners third; delete dead broad owners last.
- Deprecated APIs (if any):
  no public API deprecation is planned in this refactor. Internal direct
  imports from broad owners like `_compiler.shared` become migration-only and
  are removed by the end.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  delete the broad final-state dependency on `_compiler/shared.py`;
  delete any temporary split landing files in the same phase they stop owning
  real behavior;
  delete superseded monolithic private helpers after their new owners take over;
  delete wildcard-import dependence on a broad internal hub.
- Capability-replacing harnesses to delete or justify:
  none. This is not agent-runtime work.
- Live docs/comments/instructions to update or delete:
  review [AGENTS.md](../AGENTS.md) only if the stable start-here file list
  stops being truthful;
  keep or update the boundary comments in
  [doctrine/compiler.py](../doctrine/compiler.py),
  [doctrine/_compiler/context.py](../doctrine/_compiler/context.py), and
  [doctrine/_compiler/types.py](../doctrine/_compiler/types.py);
  add short boundary comments in new package `__init__.py` files where that
  prevents future drift.
- Behavior-preservation signals for refactors:
  `make verify-examples`;
  `make verify-diagnostics` when diagnostics move;
  [tests/test_compiler_boundary.py](../tests/test_compiler_boundary.py);
  [tests/test_parse_diagnostics.py](../tests/test_parse_diagnostics.py);
  [tests/test_verify_corpus.py](../tests/test_verify_corpus.py).
- Delete gates for the riskiest owners:
  `_compiler/shared.py` may be deleted only after
  `context.py`, `compile.py`, `resolve.py`, `validate.py`, `display.py`, and
  `flow.py` no longer import it;
  root public modules may shrink, but they may not disappear or stop exporting
  their current public functions until the proof surface says behavior is
  unchanged.

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Public boundaries | `doctrine/compiler.py` | Thin public facade over internal owners | Preserves caller imports while internals move | include |
| Parser boundary | `doctrine/parser.py` | Thin public facade plus internal package | Keeps shipped parse path stable and easy to find | include |
| Diagnostics boundary | `doctrine/diagnostics.py` | Thin public facade plus internal package | Keeps error contracts stable while helpers split | include |
| Renderer boundaries | `doctrine/renderer.py`, `doctrine/flow_renderer.py` | Thin public facades over themed helpers | Prevents new large rendering files | include |
| Verification boundaries | `doctrine/verify_corpus.py`, `doctrine/diagnostic_smoke.py` | Thin command runners over themed helpers | Keeps proof entrypoints stable without one-file monoliths | include |
| Compiler contracts | `doctrine/_compiler/types.py` | Single explicit owner for compiled contracts | Avoids scattering compiled render contracts | include |
| Compiler resolved contracts | `doctrine/_compiler/shared.py` survivors | Move to explicit `resolved_types.py` owner | Removes catch-all drift and wildcard imports | include |
| Compiler helper style | `doctrine/_compiler/support.py` | Small focused helper owners | Matches an existing clean pattern in the repo | include |
| Internal package boundary | `doctrine/_compiler/__init__.py` | Keep as internal marker only | Prevents a second accidental public surface | include |
| Docs and instructions | `AGENTS.md`, boundary comments | Update only if public boundaries stop being truthful | Avoids stale instructions while preventing needless churn | defer |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria +
> explicit verification plan (tests optional). Refactors, consolidations, and
> shared-path extractions must preserve existing behavior with credible
> evidence proportional to the risk. No fallbacks/runtime shims - the system
> must work correctly or fail loudly (delete superseded paths). The
> authoritative checklist must name the actual chosen work, not unresolved
> branches or "if needed" placeholders. Prefer programmatic checks per phase.
> Defer manual verification to finalization. Avoid negative-value tests and
> heuristic gates. Also: document new patterns and gotchas in code comments at
> the canonical boundary when that prevents future drift.

## Phase 1 — Extract explicit compiler contracts and helper owners

Status: COMPLETE

Completed work:
- Added `doctrine/_compiler/resolved_types.py`, `constants.py`, `naming.py`, and `support_files.py`.
- Repointed `compiler.py`, `context.py`, `compile.py`, `resolve.py`, `validate.py`, `display.py`, and `flow.py` off `_compiler/shared.py`.
- Deleted [doctrine/_compiler/shared.py](../doctrine/_compiler/shared.py) after the last internal import moved.

* Goal:
  move pure contracts, constants, naming helpers, and support-file helpers out
  of `_compiler/shared.py` so the refactor no longer depends on one broad hub.
* Work:
  create `doctrine/_compiler/resolved_types.py`, `constants.py`, `naming.py`,
  and `support_files.py`; move the matching survivors out of
  `doctrine/_compiler/shared.py`; repoint imports in `context.py`,
  `display.py`, `flow.py`, `compile.py`, `resolve.py`, `validate.py`, and
  `compiler.py`; keep `CompilationSession`, `CompilationContext`, and
  `doctrine.compiler.__all__` unchanged; do not leave a long-lived
  compatibility bridge in `_compiler/shared.py`.
* Verification (required proof):
  run [tests/test_compiler_boundary.py](../tests/test_compiler_boundary.py),
  [tests/test_import_loading.py](../tests/test_import_loading.py), and the
  focused manifest-backed example command for
  `examples/01_hello_world/cases.toml`.
* Docs/comments (propagation; only if needed):
  keep or refresh the boundary comments in
  [doctrine/compiler.py](../doctrine/compiler.py),
  [doctrine/_compiler/context.py](../doctrine/_compiler/context.py),
  [doctrine/_compiler/types.py](../doctrine/_compiler/types.py), and the new
  internal package `__init__.py` files.
* Exit criteria:
  moved symbols no longer depend on `_compiler/shared.py`, the public compiler
  boundary still exports the same names, and the focused proof passes.
* Rollback:
  revert the phase and restore `_compiler/shared.py` as the single owner for
  the moved symbols.

## Phase 2 — Split authored model and parser internals behind stable boundaries

Status: COMPLETE

Completed work:
- Added `doctrine/_parser/__init__.py` and `doctrine/_parser/parts.py`.
- Moved parser body-part contracts and positioned-part helpers behind the new internal parser package.
- Kept [doctrine/parser.py](../doctrine/parser.py) as the public parse boundary while switching it to the new `_parser.parts` owner.
- Ran `make verify-examples`, fixed the surfaced `replace` import regression in [doctrine/_compiler/compile.py](../doctrine/_compiler/compile.py), and got the full shipped corpus green again.
- Added `doctrine/_model/core.py`, `readable.py`, `workflow.py`, `analysis.py`, `schema.py`, and `review.py`, then turned [doctrine/model.py](../doctrine/model.py) into the thin public authored-model boundary.
- Added `doctrine/_parser/runtime.py` and `doctrine/_parser/transformer.py`, then moved parser runtime and shared declaration and readable helper mixins behind those new internal owners while keeping `build_lark_parser`, `parse_text`, and `parse_file` stable.
- Added `doctrine/_model/declarations.py`, then repointed [doctrine/_compiler/indexing.py](../doctrine/_compiler/indexing.py), [doctrine/_compiler/session.py](../doctrine/_compiler/session.py), [doctrine/_compiler/naming.py](../doctrine/_compiler/naming.py), and [doctrine/_compiler/types.py](../doctrine/_compiler/types.py) onto narrower `_model` owners.
- Moved schema and document lowering behind [doctrine/_parser/transformer.py](../doctrine/_parser/transformer.py), then deleted the matching duplicate methods from [doctrine/parser.py](../doctrine/parser.py) so the public parser boundary shrank again without behavior drift.
- Added [doctrine/_parser/readables.py](../doctrine/_parser/readables.py), then moved readable block and readable payload lowering behind that new owner.
- Deleted the matching readable methods from [doctrine/parser.py](../doctrine/parser.py), shrinking the public parser boundary again while the latest compile, unit, and corpus proof stayed green.
- Added [doctrine/_parser/reviews.py](../doctrine/_parser/reviews.py), then moved review, route-only, and grounding lowering behind that new owner.
- Added [doctrine/_parser/workflows.py](../doctrine/_parser/workflows.py), then moved workflow and workflow-law lowering behind that new owner.
- Deleted the matching review and workflow-law methods from [doctrine/parser.py](../doctrine/parser.py), shrinking the public parser boundary again to about 1,118 lines while the latest compile, unit, focused-manifest, and full-corpus proof stayed green.
- Added [doctrine/_parser/analysis_decisions.py](../doctrine/_parser/analysis_decisions.py), then moved analysis and decision lowering behind that new owner.
- Added [doctrine/_parser/io.py](../doctrine/_parser/io.py), then moved input, output, guarded-output, trust-surface, and shared IO-body lowering behind that new owner.
- Deleted the matching analysis, decision, and IO methods from [doctrine/parser.py](../doctrine/parser.py), shrinking the public parser boundary again to about 470 lines while the latest compile, unit, focused-manifest, and full-corpus proof stayed green.
- Added [doctrine/_model/law.py](../doctrine/_model/law.py), [doctrine/_model/io.py](../doctrine/_model/io.py), and [doctrine/_model/agent.py](../doctrine/_model/agent.py), then moved the law, IO, agent, skill-package, and enum families out of the mixed `_model/core.py` and `_model/workflow.py` owners while keeping [doctrine/model.py](../doctrine/model.py) stable.
- Repointed [doctrine/_compiler/resolved_types.py](../doctrine/_compiler/resolved_types.py) off the root `doctrine.model` boundary and onto the internal `doctrine._model` package.
- Added [doctrine/_parser/agents.py](../doctrine/_parser/agents.py), [doctrine/_parser/skills.py](../doctrine/_parser/skills.py), and [doctrine/_parser/expressions.py](../doctrine/_parser/expressions.py), then moved the remaining agent-field, skills, record, skill-package, enum, expression, and shared syntax lowering behind those new owners.
- Deleted the matching methods from [doctrine/parser.py](../doctrine/parser.py), shrinking the public parser boundary again to about 126 lines while the latest compile, unit, focused-manifest, and full-corpus proof stayed green.

* Goal:
  move authored model families and parser internals into purpose-built
  packages while keeping `doctrine/model.py` and `doctrine/parser.py` stable
  for callers.
* Work:
  create `doctrine/_model/` grouped by domain and `doctrine/_parser/` with
  `parts.py`, `transformer.py`, and `runtime.py`; keep `PromptFile`,
  `parse_file`, `parse_text`, and `build_lark_parser` stable at the public
  module paths; update indexing and compiler imports to the new explicit
  owners; delete monolithic parser and model helpers once the new owners carry
  the behavior.
* Verification (required proof):
  run [tests/test_parse_diagnostics.py](../tests/test_parse_diagnostics.py)
  and `make verify-examples`.
* Docs/comments (propagation; only if needed):
  keep the start-here comments in
  [doctrine/parser.py](../doctrine/parser.py) and
  [doctrine/model.py](../doctrine/model.py) truthful; add short package
  boundary comments where that prevents drift.
* Exit criteria:
  the public parse and model boundaries still work, the new internal owners are
  grouped by domain, and the full shipped corpus passes.
* Rollback:
  revert the phase and restore the prior parser and model ownership in one
  step.

## Phase 3 — Split diagnostics and rendering internals behind stable boundaries

Status: COMPLETE

Completed work:
- Added `doctrine/_diagnostics/__init__.py`, `contracts.py`, and
  `formatting.py`, then moved the shared diagnostics data contracts plus the
  JSON, location, block, and excerpt formatting helpers behind the new
  internal package while keeping
  [doctrine/diagnostics.py](../doctrine/diagnostics.py) as the public error
  boundary.
- Added `doctrine/_renderer/__init__.py`, `semantic.py`, and `tables.py`,
  then moved render-profile mode resolution, semantic-section helpers, key
  humanizing, and table helpers behind the new internal renderer package
  while keeping [doctrine/renderer.py](../doctrine/renderer.py) as the public
  markdown render boundary.
- Added `doctrine/_flow_render/__init__.py`, `layout.py`, `d2.py`, and
  `svg.py`, then moved lane planning, graph layout, D2 text emission, and
  SVG execution helpers behind the new internal flow-render package while
  keeping [doctrine/flow_renderer.py](../doctrine/flow_renderer.py) as the
  public flow render boundary.
- Added `doctrine/_diagnostics/parse_errors.py` and
  [doctrine/_diagnostics/message_builders.py](../doctrine/_diagnostics/message_builders.py),
  then moved the parse classifiers plus the compile and emit message builders
  behind the approved diagnostics owner names while keeping
  [doctrine/diagnostics.py](../doctrine/diagnostics.py) as the public error
  boundary.
- Split the old compile-message catch-all into smaller private builder groups:
  `_message_builders_agents.py`, `_message_builders_authored.py`,
  `_message_builders_refs.py`, `_message_builders_readables.py`,
  `_message_builders_workflow_law.py`, `_message_builders_reviews.py`, and
  `_message_builders_emit.py`, then deleted the old `parse.py`,
  `compile_messages.py`, and `emit_messages.py` files.
- Added `doctrine/_renderer/blocks.py`, then moved the markdown block
  dispatcher and block render helpers behind the internal renderer package
  while keeping [doctrine/renderer.py](../doctrine/renderer.py) as the thin
  public markdown boundary.
- Shrunk [doctrine/diagnostics.py](../doctrine/diagnostics.py) to about 327
  lines, [doctrine/renderer.py](../doctrine/renderer.py) to about 25 lines,
  and kept [doctrine/flow_renderer.py](../doctrine/flow_renderer.py) at about
  48 lines while preserving the public helper names, D2 constants, and
  flow-render exception types for callers and tests.
- Reran `uv sync`, `npm ci`,
  `uv run --locked python -m unittest tests.test_parse_diagnostics
  tests.test_emit_docs tests.test_emit_flow tests.test_verify_corpus`,
  `make verify-diagnostics`, and `make verify-examples`; all passed on the
  current worktree, so the reopened diagnostics-owner gap is closed.
- `doctrine/_renderer/blocks.py` is still about 557 lines, but it now acts as
  one readable-block dispatch and render owner instead of another cross-cutting
  helper hub.

* Goal:
  make diagnostics, markdown rendering, and flow rendering small and explicit
  without changing the public error and render surfaces.
* Work:
  create `doctrine/_diagnostics/`, `doctrine/_renderer/`, and
  `doctrine/_flow_render/`; move formatting, excerpt building, parse-error
  helpers, markdown block helpers, flow lane-planning and graph layout
  helpers, D2 text emission helpers, and SVG helpers into those owners; keep
  [doctrine/diagnostics.py](../doctrine/diagnostics.py),
  [doctrine/renderer.py](../doctrine/renderer.py), and
  [doctrine/flow_renderer.py](../doctrine/flow_renderer.py) as thin public
  boundaries; preserve exact diagnostic-code behavior and pinned D2 behavior.
* Verification (required proof):
  run `make verify-diagnostics`,
  [tests/test_parse_diagnostics.py](../tests/test_parse_diagnostics.py), and
  [tests/test_emit_docs.py](../tests/test_emit_docs.py).
* Docs/comments (propagation; only if needed):
  keep public boundary comments truthful and add one short note in new
  rendering or diagnostics package roots where that prevents future dumping
  ground drift.
* Exit criteria:
  public diagnostics and render functions stay stable, smoke coverage stays
  green, and the split owners are clearer than the old monoliths.
* Rollback:
  revert the phase and restore the prior public-plus-internal owner files.

## Phase 4 — Split compile, resolve, and validate behind CompilationContext

Status: COMPLETE

Missing (code):
- None in code on this worktree.

Completed work:
- Turned the old `compile.py`, `resolve.py`, and `validate.py` monoliths into
  the planned package families under `doctrine/_compiler/`.
- Added the remaining resolve-family owners
  `route_semantics.py`, `io_contracts.py`, `agent_slots.py`, `skills.py`,
  `addressable_skills.py`, `analysis.py`, `documents.py`,
  `document_blocks.py`, `section_bodies.py`, `addressables.py`, and
  `law_paths.py`, then moved the remaining live resolve behavior behind them.
- Kept `CompilationSession`, `CompilationContext`, and
  [doctrine/compiler.py](../doctrine/compiler.py) stable while shrinking
  `doctrine/_compiler/compile/__init__.py` to 27 lines,
  `doctrine/_compiler/resolve/__init__.py` to 39 lines, and
  `doctrine/_compiler/validate/__init__.py` to 326 lines.
- Ran `uv run --locked python -m unittest tests.test_final_output
  tests.test_route_output_semantics tests.test_review_imported_outputs
  tests.test_decision_attachment` and `make verify-examples`; both passed on
  2026-04-13.
- Recorded the remaining 500+ compiler-family owners as intentional final
  boundaries in `Recorded intentional 500+ boundaries` below. Each one now
  has a clear written reason instead of drifting there by accident.

* Goal:
  break the three biggest compiler family files into themed modules while
  keeping `CompilationSession`, `CompilationContext`, and the public compile
  boundary stable.
* Work:
  create `doctrine/_compiler/compile/` with `agent.py`, `readables.py`,
  `final_output.py`, and `skill_package.py`; create
  `doctrine/_compiler/resolve/` with `refs.py`, `workflows.py`, `outputs.py`,
  `reviews.py`, and `schemas.py`; create
  `doctrine/_compiler/validate/` with `agents.py`, `outputs.py`,
  `reviews.py`, `routes.py`, and `readables.py`; move the current method
  families into those exact owners; keep `CompilationContext` as the task-
  local orchestrator; keep emit entry surfaces on public parse and compile
  boundaries only; delete superseded monolithic helpers once their
  replacements own the behavior.
* Progress notes:
  - `doctrine/_compiler/compile.py` is now the package
    `doctrine/_compiler/compile/`.
  - Added `agent.py`, `readables.py`, `final_output.py`, and
    `skill_package.py`, then moved those method families behind the approved
    compile owners while keeping `CompilationContext` and
    `doctrine/compiler.py` stable.
  - Added smaller private compile owners `outputs.py`, `records.py`,
    `readable_blocks.py`, `reviews.py`, `review_cases.py`, and
    `workflows.py`, then moved the remaining live compile families out of
    the facade and behind those purpose-built modules.
  - `doctrine/_compiler/compile/__init__.py` is now a real boundary at about
    27 lines instead of a 1,905-line live family facade, while the new
    private compile owners each stay under about 500 lines.
  - `doctrine/_compiler/resolve.py` is now the package
    `doctrine/_compiler/resolve/`.
  - Added `refs.py`, `outputs.py`, `workflows.py`, `reviews.py`,
    `schemas.py`, `route_semantics.py`, `io_contracts.py`,
    `agent_slots.py`, `skills.py`, `addressable_skills.py`, `analysis.py`,
    `documents.py`, `document_blocks.py`, `section_bodies.py`,
    `addressables.py`, and `law_paths.py`, then moved the full resolve
    behavior behind those owners while keeping `CompilationContext` and the
    current internal call sites stable.
  - Restored the original inherited-outputs behavior inside
    `doctrine/_compiler/resolve/outputs.py` after the first cut regressed one
    patched final-output case, and restored the original
    `_dotted_decl_name` support import after the first `law_paths.py` cut.
  - `doctrine/_compiler/resolve/__init__.py` is now a 39-line family
    boundary instead of a live multi-thousand-line facade.
  - `doctrine/_compiler/validate.py` is now the package
    `doctrine/_compiler/validate/`.
  - Added `agents.py`, `outputs.py`, `routes.py`, and `readables.py`, then
    moved the matching validate method families behind those approved owners
    while keeping `CompilationContext` and current internal call sites
    stable.
  - Added the approved `doctrine/_compiler/validate/reviews.py` owner, moved
    the shared review-semantic and review helper families behind it, then
    split that review owner into smaller private modules:
    `review_semantics.py`, `review_preflight.py`,
    `review_gate_observation.py`, `review_agreement.py`, and
    `review_branches.py`.
  - Deleted the duplicate review method family from
    `doctrine/_compiler/validate/__init__.py`, so
    `doctrine/_compiler/validate/reviews.py` is now the real 19-line review
    boundary over the smaller internal review owners instead of a shadow
    wrapper beside another live copy.
  - Added `route_semantics.py`, `route_semantics_context.py`,
    `route_semantics_reads.py`, `contracts.py`, `display.py`,
    `schema_helpers.py`, `addressable_children.py`,
    `addressable_display.py`, and `law_paths.py`, then moved the remaining
    route-semantic, contract-summary, display, schema, addressable, and
    law-path helper families behind those purpose-built validate owners.
  - `doctrine/_compiler/validate/__init__.py` is now a real boundary at
    about 320 lines instead of a 2,976-line live family facade, while the
    new private validate owners each stay under about 500 lines.
* Verification (required proof):
  run `make verify-examples`,
  [tests/test_final_output.py](../tests/test_final_output.py),
  [tests/test_route_output_semantics.py](../tests/test_route_output_semantics.py),
  [tests/test_review_imported_outputs.py](../tests/test_review_imported_outputs.py),
  and [tests/test_decision_attachment.py](../tests/test_decision_attachment.py).
* Docs/comments (propagation; only if needed):
  keep the boundary comments in
  [doctrine/compiler.py](../doctrine/compiler.py),
  [doctrine/_compiler/context.py](../doctrine/_compiler/context.py), and
  [doctrine/_compiler/types.py](../doctrine/_compiler/types.py) aligned with
  the final owner paths.
* Exit criteria:
  the giant compiler families are split by concern, emit callers still use the
  same public boundaries, and high-risk compiler proof stays green.
* Rollback:
  revert the phase and restore the prior compile, resolve, and validate family
  owners behind the same public boundary.

## Phase 5 — Split proof owners while keeping trusted commands stable

Status: COMPLETE

Progress notes:
- Added `doctrine/_verify_corpus/` with `manifest.py`, `runners.py`,
  `diff.py`, and `report.py`, then shrank
  [doctrine/verify_corpus.py](../doctrine/verify_corpus.py) to a 47-line
  stable runner boundary.
- Added `doctrine/_diagnostic_smoke/` with `parse_checks.py`,
  `compile_checks.py`, `review_checks.py`, `emit_checks.py`,
  `flow_checks.py`, and `fixtures.py`, then shrank
  [doctrine/diagnostic_smoke.py](../doctrine/diagnostic_smoke.py) to a
  22-line stable runner boundary.
- Split the remaining `_diagnostic_smoke` monolith owners into smaller themed
  modules: `fixtures_common.py`, `fixtures_reviews.py`,
  `fixtures_authored.py`, `fixtures_flow.py`,
  `fixtures_final_output.py`, `flow_route_checks.py`,
  `flow_graph_checks.py`, and `flow_emit_checks.py`.
- Shrunk [doctrine/_diagnostic_smoke/fixtures.py](../doctrine/_diagnostic_smoke/fixtures.py)
  to a 34-line boundary and
  [doctrine/_diagnostic_smoke/flow_checks.py](../doctrine/_diagnostic_smoke/flow_checks.py)
  to an 11-line boundary.
- Fresh proof is green for the landed Phase 5 work:
  [tests/test_verify_corpus.py](../tests/test_verify_corpus.py),
  `uv run --locked python -m doctrine.verify_corpus --manifest
  examples/01_hello_world/cases.toml`, `make verify-diagnostics`, and
  `make verify-examples` all passed on 2026-04-13.

Missing (code):
- None in code on this worktree.

* Goal:
  turn corpus verification and diagnostic smoke into small owner packages
  without changing the commands the repo already trusts.
* Work:
  create `doctrine/_verify_corpus/` and `doctrine/_diagnostic_smoke/`; move
  manifest parsing, case runners, diff building, report formatting, smoke
  checks, and fixtures into themed modules; keep
  [doctrine/verify_corpus.py](../doctrine/verify_corpus.py) and
  [doctrine/diagnostic_smoke.py](../doctrine/diagnostic_smoke.py) as stable
  runners; keep `emit_docs`, `emit_flow`, and `emit_skill` on public
  boundaries only.
* Verification (required proof):
  run [tests/test_verify_corpus.py](../tests/test_verify_corpus.py),
  `make verify-diagnostics`, and the focused manifest-backed example command
  for `examples/01_hello_world/cases.toml`.
* Docs/comments (propagation; only if needed):
  keep runner-module comments truthful and add short package boundary comments
  where the new proof owners would otherwise drift back into one file.
* Exit criteria:
  the proof commands still behave the same, the new proof owners are split by
  job, and targeted verifier and smoke proof passes.
* Rollback:
  revert the phase and restore the old verifier and smoke owners.

## Phase 6 — Delete dead paths, sync touched truth surfaces, and run full proof

Status: COMPLETE

Missing (code):
- None in code on this worktree.

Progress notes:
- Ran `uv sync` and `npm ci` on the current worktree.
- Replaced the root parser wildcard import with the one explicit helper import
  it still needs, replaced the root model wildcard facade with explicit
  re-exports, and replaced the root compiler export rebuild with explicit
  imports from `doctrine._compiler.resolved_types`.
- Replaced the remaining wildcard `resolved_types` imports in the main
  compiler boundaries
  [doctrine/_compiler/context.py](../doctrine/_compiler/context.py),
  [doctrine/_compiler/flow.py](../doctrine/_compiler/flow.py),
  [doctrine/_compiler/display.py](../doctrine/_compiler/display.py), and
  [doctrine/_compiler/validate/__init__.py](../doctrine/_compiler/validate/__init__.py).
- Removed the remaining internal
  `from doctrine._compiler.resolved_types import *` imports across the
  compile, resolve, and validate owner modules.
- Fresh proof is green for the landed Phase 6 work:
  [tests/test_compiler_boundary.py](../tests/test_compiler_boundary.py),
  [tests/test_parse_diagnostics.py](../tests/test_parse_diagnostics.py),
  [tests/test_verify_corpus.py](../tests/test_verify_corpus.py),
  `tests.test_final_output`, `tests.test_route_output_semantics`,
  `tests.test_review_imported_outputs`,
  `tests.test_decision_attachment`, `make verify-diagnostics`, and
  `make verify-examples` all passed on 2026-04-13.
- Recorded the remaining intentional 500+ owners below so the final closeout
  keeps the file-size rule honest without reopening cohesive single-purpose
  boundaries.

* Goal:
  finish the refactor cleanly, remove temporary landing files and broad hubs,
  and prove the final state with the shipped checks.
* Work:
  refresh local dependencies with `uv sync` and `npm ci`; delete any remaining
  temporary landing files, wildcard-import dependence, and dead broad owners;
  keep `doctrine/_compiler/shared.py` deleted while the remaining cleanup
  lands; keep the root public boundaries thin; cold-read
  [AGENTS.md](../AGENTS.md) and the boundary comments, then update only the
  surfaces that the final layout made stale.
* Verification (required proof):
  run `make verify-examples`, `make verify-diagnostics`,
  [tests/test_compiler_boundary.py](../tests/test_compiler_boundary.py),
  [tests/test_parse_diagnostics.py](../tests/test_parse_diagnostics.py), and
  [tests/test_verify_corpus.py](../tests/test_verify_corpus.py).
* Docs/comments (propagation; only if needed):
  update only the surviving live instruction and boundary-comment surfaces that
  no longer match reality after the final layout lands.
* Exit criteria:
  no temporary landing files remain, `_compiler/shared.py` is gone, the public
  boundaries still export the right surfaces, and the full shipped proof is
  green.
* Rollback:
  revert the cleanup phase and reopen the last phase whose proof no longer
  passes.

## Recorded intentional 500+ boundaries

These files stay above about 500 lines by design. Each one is the canonical
owner for one cohesive boundary, and the full proof above stayed green on
2026-04-13.

- [doctrine/_compiler/resolved_types.py](../doctrine/_compiler/resolved_types.py)
  — 614 lines. It is the canonical resolved-contract owner for compiler
  internals and `doctrine.compiler`, so splitting it further would scatter the
  shared dataclasses and type aliases that define one contract family.
- [doctrine/_parser/transformer.py](../doctrine/_parser/transformer.py)
  — 534 lines. It is the shared AST-construction mixin layer that the public
  parser boundary and the specialized `_parser/*` owners reuse, so it stays as
  one boundary for shared lowering helpers.
- [doctrine/_renderer/blocks.py](../doctrine/_renderer/blocks.py)
  — 557 lines. It is the readable-block dispatch and render owner for the thin
  markdown renderer boundary.
- [doctrine/_compiler/display.py](../doctrine/_compiler/display.py)
  — 889 lines. It is the display and render helper owner for
  `CompilationContext`, so the human-facing prose rendering path stays in one
  place.
- [doctrine/_compiler/flow.py](../doctrine/_compiler/flow.py)
  — 883 lines. It is the flow extraction owner for `CompilationContext`, so
  graph building, route notes, and flow-edge collection stay on one fail-loud
  path.
- [doctrine/_compiler/compile/agent.py](../doctrine/_compiler/compile/agent.py)
  — 601 lines. It is the canonical agent compilation owner for typed fields,
  authored slots, and final-output wiring.
- [doctrine/_compiler/compile/readables.py](../doctrine/_compiler/compile/readables.py)
  — 508 lines. It is the canonical readable-declaration compilation owner for
  analysis, decision, schema, document, input, and output declarations that
  all lower through the shared readable model.
- [doctrine/_compiler/resolve/workflows.py](../doctrine/_compiler/resolve/workflows.py)
  — 648 lines. It is the canonical workflow and law resolution owner,
  including inheritance, caching, and addressable resolution.
- [doctrine/_compiler/resolve/outputs.py](../doctrine/_compiler/resolve/outputs.py)
  — 691 lines. It is the canonical output and IO-body resolution owner,
  including final-output shape summaries and render-profile resolution.
- [doctrine/_compiler/resolve/reviews.py](../doctrine/_compiler/resolve/reviews.py)
  — 1048 lines. It is the canonical review resolution owner, including
  subjects, contracts, review-semantics addressables, and shared review-body
  lowering.
- [doctrine/_compiler/resolve/document_blocks.py](../doctrine/_compiler/resolve/document_blocks.py)
  — 527 lines. It is the canonical document-block and readable-payload
  resolution owner, so all readable block kinds lower through one consistent
  path.
- [doctrine/_compiler/validate/routes.py](../doctrine/_compiler/validate/routes.py)
  — 1208 lines. It is the canonical workflow-law and route-validation owner,
  so law-branch invariants, route guards, and path-set checks stay on one
  fail-loud validation surface.
- [doctrine/_compiler/validate/addressable_children.py](../doctrine/_compiler/validate/addressable_children.py)
  — 521 lines. It is the canonical addressable-child expansion owner across
  review, schema, workflow, document, and record roots.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

Keep proof lean. Prefer existing credible signals. For this work, the baseline
proof will come from the shipped corpus, diagnostics verification when touched,
and narrow behavior checks only where a move is risky and current proof is too
coarse.

## 8.1 Unit tests (contracts)

- Reuse existing unit-like checks where they already cover the moved behavior.
- Add narrow preservation tests only for seams that the corpus does not
  observe well enough.

## 8.2 Integration tests (flows)

- Run `make verify-examples` for the full shipped corpus.
- Run a focused manifest-backed example during intermediate refactor slices
  when fast feedback is needed.

## 8.3 E2E / device tests (realistic)

- Not applicable in the device sense.
- Final realistic proof is the shipped corpus plus diagnostics verification for
  changed diagnostics surfaces.

# 9) Rollout / Ops / Telemetry

This is an internal refactor. Rollout is repo-local and should stay low drama.
The main operational risk is behavior drift during module moves.

## 9.1 Rollout plan

- Land the refactor in ordered phases.
- Keep stable public boundaries working while private internals move.
- Avoid partial duplicate paths. Delete superseded internal routes as phases
  complete.

## 9.2 Telemetry changes

- No production telemetry changes expected.
- Use existing verification output and failing proofs as the main feedback.

## 9.3 Operational runbook

- Sync with `uv sync`.
- Install pinned flow-render dependencies with `npm ci`.
- Run `make verify-examples`.
- Run `make verify-diagnostics` when diagnostics code changes.
- If a check cannot run because a dependency is missing, say that plainly.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: explorer 1, explorer 2, self-integrator
- Scope checked:
  - frontmatter, `# TL;DR`, `# 0)`, `# 1)`, `# 2)`, `# 7)`, `# 8)`, `# 9)`, `# 10)`, and helper blocks
  - `# 3)`, `# 4)`, `# 5)`, `# 6)`, and whether the architecture, migration, cleanup, and proof story still agree
- Findings summary:
  - Explorer 2 found no issues in Sections 3 through 7.
  - Explorer 1 and the parent pass found one stale readiness line and two execution gaps: the flow-render lane-planning owner was implied but not named, and Phase 4 still used example compiler module names instead of the exact chosen split.
- Integrated repairs:
  - Updated `# 3.3` so the readiness line matches the current stage.
  - Made `doctrine._flow_render.layout` the explicit home for lane planning and graph layout helpers in `# 5`, `# 6`, and Phase 3.
  - Rewrote Phase 4 to list the exact chosen `compile`, `resolve`, and `validate` owner modules instead of examples.
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

## 2026-04-13 - Start with stable public boundaries and real proof

Context

The ask is to break up giant files without changing functionality and to align
the work with the repo rules in `AGENTS.md`.

Options

- Split files directly and allow public imports to move.
- Keep current public boundaries stable while moving private internals behind
  them.
- Leave the giant files alone and only document better ownership.

Decision

Start from stable public boundaries and preserve behavior with real proof. Do
not treat docs-only cleanup as success.

Consequences

- The plan can move a lot of internal code without forcing callers to rewrite
  imports early.
- The call-site audit and target architecture must be strong before code work
  starts.

Follow-ups

- Confirm the North Star.
- Run `research`.
- Run `deep-dive`.

## 2026-04-13 - Keep root facades stable and remove broad internal catch-alls

Context

Deep-dive pass 1 grounded the current module graph. The repo already has one
good pattern: thin public boundaries like
[doctrine/compiler.py](../doctrine/compiler.py). The biggest problem is not
the public shape. It is the oversized internal owners and the broad
`_compiler/shared.py` hub.

Options

- Break public import paths and move callers onto new private modules.
- Keep root public boundaries stable and split the giant internals behind
  them.
- Leave `_compiler/shared.py` as the long-term shared owner and only split the
  biggest mixin files.

Decision

Keep the root public boundaries stable. Split the giant internals behind them.
Retire `_compiler/shared.py` as a broad catch-all by moving its surviving
contracts and helpers into explicit owners.

Consequences

- Public callers and proof surfaces can stay on known import paths.
- The refactor can proceed depth-first through internal owners without product
  churn.
- The implementation must preserve `doctrine.compiler.__all__` behavior and
  must not leave a new `common` or `utils` dumping ground behind.

Follow-ups

- Run deep-dive pass 2 to harden the final delete path and phase order.
- Write the authoritative phase plan.

## 2026-04-13 - Contracts first, broad hubs deleted last

Context

Deep-dive pass 2 had to turn the chosen architecture into a migration order
that phase-plan can execute without guessing. The biggest risk is splitting
huge files in the wrong order and then needing long-lived internal shims.

Options

- Split the biggest behavior files first and clean up shared contracts later.
- Move pure contracts and helper survivors first, then split behavior owners.
- Keep `_compiler/shared.py` as a long-lived bridge while the rest of the code
  moves.

Decision

Move pure contracts, constants, naming helpers, and support-file helpers
first. Repoint imports next. Split the big behavior owners after that. Delete
the broad hubs and landing files last, in the same phases where they stop
owning real behavior.

Consequences

- Phase-plan can sequence the work without inventing a migration story later.
- The refactor stays compatible with the no-fallback, no-parallel-path rule.
- `_compiler/shared.py` does not get to survive as a renamed or thinly wrapped
  catch-all.

Follow-ups

- Write the authoritative phase plan.

## 2026-04-13 - Use six phases with public boundaries stable until cleanup

Context

After research and two deep-dive passes, the remaining job was to turn the
architecture into one execution checklist that implementation could follow
without inventing new sequencing or fallback paths.

Options

- Use a few broad refactor phases and let implementation decide the order
  inside them.
- Use a foundation-first phase plan that starts with contracts and ends with
  final cleanup and full proof.
- Start with parser or compiler behavior splits first and clean up contracts
  later.

Decision

Use six phases: shared contracts and helpers first, model and parser second,
diagnostics and renderers third, compiler families fourth, proof owners fifth,
and final cleanup plus full proof last.

Consequences

- Implementation has one clear order to follow.
- The plan keeps public boundaries stable until the end.
- The delete work and proof work stay visible instead of getting buried as
  cleanup.

Follow-ups

- Use `implement-loop` only after the consistency pass says the doc is ready.

## 2026-04-13 - Make flow layout ownership explicit and lock compiler family cuts

Context

The consistency pass found that the main artifact still had two execution
gaps. The flow-render split implied a layout owner but did not name where lane
planning would live, and Phase 4 still listed compiler family modules as
examples instead of the exact chosen cut.

Options

- Leave those details implied and let implementation decide.
- Name the flow-layout owner and the exact compiler family modules in the main
  plan before implementation starts.

Decision

Name `doctrine._flow_render.layout` as the owner for lane planning and graph
layout helpers. Lock Phase 4 to the exact chosen compiler family modules for
`compile`, `resolve`, and `validate`.

Consequences

- Section 7 is now executable without guessing hidden module cuts.
- The plan no longer risks dropping current flow-layout behavior during the
  render split.

Follow-ups

- Proceed to `implement`.

## 2026-04-13 - Delete `_compiler/shared.py` as soon as the cutover is real

Context

Phase 1 moved the compiler boundary and the big mixin owners onto
`resolved_types.py`, `constants.py`, `naming.py`, and `support_files.py`.
That left `_compiler/shared.py` as dead competing truth instead of a live
owner.

Options

- Leave `_compiler/shared.py` in place until final cleanup.
- Delete `_compiler/shared.py` in Phase 1 as soon as all imports move off it.

Decision

Delete `_compiler/shared.py` in Phase 1 once no internal importer still needs
it.

Consequences

- The compiler no longer has a dead internal bridge that can drift back into
  use.
- Later cleanup phases can focus on the remaining giant owners instead of
  carrying a fake shared boundary forward.

Follow-ups

- Continue Phase 2 on the parser and model split.

## 2026-04-13 - Close the refactor with explicit large-boundary reasons

Context

The implementation removed the original 2,000 to 7,000 line monoliths, but a
small set of cohesive owner modules still sit above about 500 lines. The plan
already allowed that only when the reason was written down and the shipped
proof stayed green.

Options

- Reopen the refactor and keep splitting every 500+ owner again.
- Accept the remaining 500+ owners only when each one is a real single-purpose
  boundary with a clear written reason and green proof.

Decision

Accept the remaining 500+ owners as final boundaries where the module still
owns one cohesive job. Record each reason in Section 7 and close the plan
after the full proof passes.

Consequences

- The plan stays honest about the remaining large files.
- Future cleanup can still split one of those owners later if it starts mixing
  jobs, but that is no longer missing work from this refactor.

Follow-ups

- Use `arch-docs` if we want to retire or clean up the finished plan and
  worklog surfaces.
