---
title: "PyPrompt - Hello World Parse To Markdown POC - Architecture Plan"
date: 2026-04-06
status: draft
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: new_system
related:
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md
  - docs/LIBRARY_RESEARCH.md
  - examples/01_hello_world/prompts/AGENTS.prompt
  - examples/01_hello_world/ref/AGENTS.md
---

# TL;DR

- Outcome: Build one working end-to-end proof of concept that parses `examples/01_hello_world/prompts/AGENTS.prompt` and compiles it into Markdown that matches `examples/01_hello_world/ref/AGENTS.md`.
- Problem: The repo currently has language notes, examples, and parser research, but no running implementation that proves the syntax can go from source file to rendered Markdown.
- Approach: Use `Lark` as the custom-syntax parser front-end, keep the supported language surface to the exact `01_hello_world` shape, map the parse tree into a small typed AST, then compile that AST into Markdown with fail-loud behavior for unsupported syntax.
- Plan: Ground the POC against the existing example and docs, define the smallest grammar and AST that can parse Hello World, implement one compile path from file input to Markdown output, and verify it against the checked-in reference output.
- Non-negotiables: No speculative support for imports, inheritance, or workflow merge in this POC; no parallel parser implementations; no silent fallbacks; the output contract is the checked-in Hello World reference.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: not started
external_research_grounding: not started
deep_dive_pass_2: not started
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

A small `Lark`-based compiler can parse the exact `01_hello_world` source shape used in this repo, transform it into a minimal typed AST, and emit Markdown that matches the checked-in reference output without adding syntax or semantics that contradict the current language design notes.

## 0.2 In scope

- Parsing one top-level declaration of the form `agent Name:`
- Supporting the `role` scalar field
- Supporting a `workflow:` block whose body contains one or more quoted string lines
- Producing the Hello World Markdown layout shown by the current reference output
- Providing one small end-to-end entrypoint that reads the source file and writes or prints compiled Markdown
- Using `Lark` and its tree-transform tooling rather than a hand-written parser or Python-only syntax strategy
- Keeping the parser, AST, semantic normalization, and Markdown rendering layers explicit even if each layer is small

## 0.3 Out of scope

- Imports
- Top-level reusable `workflow Name:` declarations
- Workflow symbol references
- Inheritance
- Ordered workflow patching, `inherit`, `override`, or merge semantics
- Rich comments, generalized CLI ergonomics, editor tooling, packaging, or release workflows
- Any attempt to model `99_not_clean_but_useful` source-side complexity in this first POC

## 0.4 Definition of done (acceptance evidence)

- Running one documented local command against `examples/01_hello_world/prompts/AGENTS.prompt` produces Markdown whose content matches `examples/01_hello_world/ref/AGENTS.md`
- Unsupported syntax outside the POC subset fails loudly with a clear compiler error instead of silently compiling incorrectly
- The implementation structure leaves a credible upgrade path to `02_sections` without forcing a different parser front-end

## 0.5 Key invariants (fix immediately if violated)

- `Lark` is the single parser front-end for this POC
- The supported language surface is exactly the Hello World subset unless the plan is explicitly expanded later
- Parsing and semantic compilation stay separate, even if the semantic layer is minimal
- No silent fallbacks, best-effort rendering, or second parser path
- The checked-in example source and checked-in reference output are the truth surfaces for this POC

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Prove that the current custom syntax can compile end to end without redesigning it into Python syntax.
2. Keep the implementation as small and legible as the example sequence itself.
3. Fail loudly on unsupported constructs rather than pretending the language is broader than it is.
4. Preserve a clean path to extend the same architecture to `02_sections` and later examples.

## 1.2 Constraints

- The repo is intentionally example-first and currently has no compiler implementation.
- The language notes bias toward explicit typed declarations, indentation-sensitive blocks, and minimal magic.
- The parser-fit analysis already recommends `Lark` as the best default if custom syntax is preserved.
- This POC must stay focused on `01_hello_world`; broader feature coverage is design creep at this stage.

## 1.3 Architectural principles (rules we will enforce)

- One parser front-end, one AST boundary, one renderer path.
- Fail-loud boundaries over permissive coercion.
- The example contract is authoritative; implementation convenience does not get to rewrite it.
- New code should make the next example easier to add, but should not implement the next example early.

## 1.4 Known tradeoffs (explicit)

- Choosing `Lark` now optimizes for custom syntax and clean grammar ownership, not the absolute smallest possible first script.
- The POC may intentionally hard-stop on constructs that later examples need.
- Exact output matching is more valuable here than generalized flexibility.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

The repo currently contains language-design notes, parser research, and example source/reference pairs. `examples/01_hello_world/prompts/AGENTS.prompt` defines the smallest supported source shape, and `examples/01_hello_world/ref/AGENTS.md` defines the expected rendered output.

## 2.2 What's broken / missing (concrete)

There is no implementation proving that the language can be parsed and compiled. That leaves the project vulnerable to design drift: syntax decisions can accumulate faster than confidence that the language is actually implementable.

## 2.3 Constraints implied by the problem

- The first implementation should prove feasibility, not chase feature breadth.
- Parser choice should reduce future churn instead of forcing a second parser strategy later.
- The POC needs a small, trustworthy acceptance signal tied directly to the existing example corpus.

# 3) Research Grounding (external + internal "ground truth")

## 3.1 External anchors (papers, systems, prior art)

Detailed parser-library grounding is deferred to `research`, but the current repo evidence already points to `Lark` as the leading choice for preserving the custom indentation-sensitive syntax while still getting structured parse and transform support.

## 3.2 Internal ground truth (code as spec)

Detailed grounding is deferred to `research`. The current authoritative inputs for this POC are:

- `docs/LANGUAGE_DESIGN_NOTES.md`
- `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md`
- `examples/01_hello_world/prompts/AGENTS.prompt`
- `examples/01_hello_world/ref/AGENTS.md`

## 3.3 Open questions from research

- Should the first grammar target `LALR` immediately, or start with the most forgiving `Lark` mode and tighten later?
- Should AST construction use plain dataclasses with a manual transformer or `lark.ast_utils.create_transformer()` from the start?
- What is the smallest error taxonomy worth defining for unsupported syntax in the POC?

# 4) Current Architecture (as-is)

## 4.1 On-disk structure

Current architecture is docs-and-examples only. There is no parser, compiler, renderer, or CLI entrypoint in the repo yet.

## 4.2 Control paths (runtime)

No runtime path exists yet. The intended future control path for this POC is source file read -> parse -> AST transform -> semantic normalization -> Markdown render.

## 4.3 Object model + key abstractions

No implementation abstractions exist yet. The language concepts already implied by the example are `agent`, `role`, and `workflow` string lines.

## 4.4 Observability + failure behavior today

There is no compiler failure surface today because nothing runs. Misalignment currently shows up only as disagreement between docs and examples.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. This is a local compiler POC with file input and Markdown output.

# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

To be filled by `deep-dive`. The intended shape is a small compiler package or module set with clear ownership for grammar definition, AST types, semantic normalization, and Markdown rendering.

## 5.2 Control paths (future)

To be filled by `deep-dive`. The intended single owner path is one end-to-end compile flow from `.prompt` input to Markdown output, with unsupported syntax failing loudly before rendering.

## 5.3 Object model + abstractions (future)

To be filled by `deep-dive`. The minimum credible future model is:

- parser tree
- typed AST for `Agent`, `Role`, and `Workflow`
- compile or render step that normalizes the AST into final Markdown sections

## 5.4 Invariants and boundaries

To be filled by `deep-dive`. The current intended boundaries are:

- `Lark` owns syntax parsing
- local compiler code owns semantics
- the renderer owns Markdown shape
- no fallback renderer or alternate parser path is allowed

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.

# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
|---|---|---|---|---|---|---|---|
| Example source | `examples/01_hello_world/prompts/AGENTS.prompt` | `agent HelloWorld` | Checked-in source contract only | Treat as parser input fixture | Defines the source syntax the POC must support | `.prompt` source subset for Hello World | Integration comparison against reference output |
| Example output | `examples/01_hello_world/ref/AGENTS.md` | rendered document | Checked-in output contract only | Treat as renderer acceptance target | Defines the output the POC must match | Markdown output contract for Hello World | Integration comparison against generated Markdown |
| Compiler implementation | new path under repo root | parser / AST / renderer entrypoint | Missing | Add minimal implementation | POC requires a real compile path | Source file in, Markdown out | Unit and integration checks to be defined in later stages |
| Docs | `docs/LANGUAGE_DESIGN_NOTES.md` and this plan | language direction | Exists | Keep aligned with shipped POC scope | Avoid docs drifting ahead of implementation | Hello World subset is the only supported feature set | Manual review of touched docs |

## 6.2 Migration notes

- Canonical owner path does not exist yet; this plan will create it rather than add a parallel implementation.
- No deprecated APIs are expected in this first POC because there is no live compiler yet.
- Live docs must stay honest about the supported subset after implementation lands.
- The primary preservation signal is exact output agreement with the checked-in Hello World reference.

# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

This section will be authored by `phase-plan` after research and deep-dive. The current expected phase shape is:

- lock the exact Hello World grammar and output contract
- implement the minimal `Lark` parse -> AST -> render path
- verify exact output and fail-loud behavior

# 8) Verification Strategy (common-sense; non-blocking)

Avoid verification bureaucracy. Prefer the smallest existing signal. Default to 1-3 checks total.

## 8.1 Unit tests (contracts)

Prefer one or two small contract checks around AST construction or Markdown rendering only if they materially clarify failures during the POC.

## 8.2 Integration tests (flows)

The primary signal should be one end-to-end compile check that compares generated Markdown for `01_hello_world` against the checked-in reference output.

## 8.3 E2E / device tests (realistic)

Not applicable beyond a short manual local run of the compile command. No bespoke harnesses, OCR layers, or broader framework work should be introduced for this POC.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

This is a local-only POC. There is no staged rollout surface yet.

## 9.2 Telemetry changes

None for the first POC. Clear compiler errors are sufficient.

## 9.3 Operational runbook

If the compile path fails, stop on the explicit parse or compile error and fix the implementation rather than adding recovery behavior.

# 10) Decision Log (append-only)

## 2026-04-06 - Use Lark for the first compiler POC

Context

The repo has multiple parser options under consideration, but the language and parser analysis now recommends `Lark` when preserving the current custom syntax.

Options

- `Lark`
- `pyparsing`
- `LibCST`
- a small hand-written parser

Decision

Use `Lark` for the first end-to-end Hello World compiler proof of concept.

Consequences

- The parser front-end stays aligned with the current custom syntax.
- AST and semantic compilation remain local project code.
- The first implementation can stay narrow without prejudging later features like imports or inheritance.

Follow-ups

- Confirm this North Star before deeper planning.
- Use later arch steps to ground the implementation structure and authoritative phase plan.
