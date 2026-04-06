---
title: "PyPrompt - Hello World Grammar Bootstrap - Architecture Plan"
date: 2026-04-06
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: new_system
related:
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md
  - docs/LIBRARY_RESEARCH.md
  - docs/COMPILER_ERRORS.md
  - docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md
  - examples/01_hello_world/prompts/AGENTS.prompt
  - examples/01_hello_world/ref/AGENTS.md
  - for_reference_only/lark/docs/grammar.md
  - for_reference_only/lark/docs/parsers.md
  - for_reference_only/lark/examples/indented_tree.py
---

# TL;DR

- Outcome: Bootstrap the first real PyPrompt language grammar with `Lark`, prove it against the Hello World subset, and make it rerunnable with one simple local command such as `make hello-world`.
- Problem: The repo has language notes, examples, and a checked-out `Lark` reference tree, but no runnable grammar, no parse/compile loop, and no cheap way to rerun the language contract as examples evolve.
- Approach: Lock a narrow Hello World syntax subset, author one checked-in `Lark` grammar for it, parse into a minimal typed AST, compile a selected agent into Markdown, and use that loop to surface unresolved spec holes instead of silently inventing semantics.
- Plan: Ground the first grammar in the current examples and design notes, choose the smallest honest acceptance surface for `HelloWorld`, wire one runner plus one `make` target, and keep every unsupported construct fail-loud so later examples extend the same grammar rather than replace it.
- Non-negotiables: One parser front-end only; one checked-in grammar only; minimum custom wiring around `Lark`; no hand-written fallback parser; no hidden "first agent wins" behavior; no pretending `HelloWorld2` is supported unless the grammar and output contract explicitly say so; if the language shape forces hacks, tighten or change the language instead of layering parser workarounds.

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

A small `Lark`-based grammar and one repeatable local verification command can parse the agreed Hello World subset of the PyPrompt language, compile the targeted `HelloWorld` agent into Markdown matching the checked-in reference output, and fail loudly on unresolved syntax holes so later examples can extend the same grammar instead of forcing a parser reset.

## 0.2 In scope

- Defining the first checked-in grammar for the language using `Lark` grammar syntax
- Using the checked-out `for_reference_only/lark` repo only as reference material for grammar shape, parser mode, and indentation-sensitive examples
- Supporting the smallest syntax surface needed for the first Hello World bootstrap:
  - line comments beginning with `#`
  - blank lines
  - top-level `agent Name:`
  - scalar `role: "..."` for the initial supported role form
  - `workflow: "Title"` with one or more indented quoted string lines
- Choosing an explicit acceptance path for the current `examples/01_hello_world/prompts/AGENTS.prompt` ambiguity so the system targets `HelloWorld` on purpose rather than by accident
- Building one small runner that reads source, parses it, builds a minimal AST, and renders Markdown
- Wiring one simple local command such as `make hello-world` to run the bootstrap parse/compile/verify loop
- Using this loop to expose holes in the current example/spec story before extending the grammar to later examples
- Preferring stock `Lark` facilities wherever they fit cleanly, including ordinary grammar rules, the built-in indentation machinery when needed, and standard tree/transform tooling

## 0.3 Out of scope

- Nested `role` blocks such as the `HelloWorld2` form unless the plan is explicitly widened later
- `02_sections` and later language features, including:
  - nested keyed workflow entries
  - imports
  - top-level reusable workflows
  - inheritance
  - `inherit` / `override`
  - handoff routing
  - input and output primitives
- Settling the full long-term output-file mapping for multi-agent source packages
- Packaging, release workflows, editor integration, or generalized CLI ergonomics beyond one small local bootstrap command
- Any attempt to model `99_not_clean_but_useful` in this first grammar pass
- Custom parser sidecars, bespoke recovery layers, or syntax-specific hacks whose main job is to rescue a language shape that does not fit cleanly in `Lark`

## 0.4 Definition of done (acceptance evidence)

- A documented local command such as `make hello-world` runs the first end-to-end loop
- That loop parses the supported Hello World source surface, explicitly targets `HelloWorld`, and emits Markdown matching `examples/01_hello_world/ref/AGENTS.md`
- Unsupported constructs outside the initial subset, including the nested `HelloWorld2` role form if still out of scope, fail loudly with a clear parser or compiler error
- The checked-in grammar and runner structure leave a credible extension path to `02_sections` without replacing the parser front-end or inventing a second syntax model

## 0.5 Key invariants (fix immediately if violated)

- `Lark` is the single parser front-end for the supported language subset
- One checked-in grammar file is the syntax source of truth for the supported subset
- Parsing, AST construction, semantic validation, and Markdown rendering remain separate responsibilities even if each layer is small
- No hand-written fallback parser, best-effort rendering, or hidden alternate parse path is allowed
- The acceptance path for `HelloWorld` must be explicit while the current `01_hello_world` source/ref relationship remains ambiguous
- Grammar growth follows the example sequence and design notes; unsupported features fail loudly instead of being guessed
- If a proposed syntax feature requires non-idiomatic parser hacks, the default response is to change or defer the language feature instead of normalizing the hack

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Make the language real enough to parse and rerun locally instead of remaining docs-only.
2. Use the grammar to expose specification holes early rather than burying them inside implementation shortcuts.
3. Keep the first supported subset narrow, explicit, and fail-loud.
4. Prefer idiomatic out-of-the-box `Lark` facilities over custom parser wiring.
5. Lay out the implementation so later examples can extend the same grammar incrementally.

## 1.2 Constraints

- The repo currently has no compiler, no build tooling, and no runtime verification loop.
- `examples/01_hello_world/prompts/AGENTS.prompt` currently mixes two role forms while the checked-in ref shows only one rendered output.
- The language direction is example-first and intentionally wants parser growth to follow the example sequence.
- The checked-out `for_reference_only/lark` tree is available for reference, but it is not itself the product code path.
- The likely grammar is indentation-sensitive, so parser-mode and indenter choices matter early.
- The user explicitly wants hard failure when the language shape starts demanding hacks; changing the language is preferred to building parser scaffolding around it.

## 1.3 Architectural principles (rules we will enforce)

- One checked-in grammar owns the supported syntax surface.
- One parse -> AST -> render control path owns the bootstrap compiler.
- The verification loop must target `HelloWorld` explicitly while output selection rules are unsettled.
- Unsupported syntax is an error surface, not a silent branch.
- Prefer stock `Lark` grammar/lexer/parser/indenter/transform patterns before any custom wiring.
- If clean `Lark` usage stops fitting, treat that as language-design feedback first.
- Later example support extends the same core architecture rather than introducing parallel parsers or ad hoc readers.

## 1.4 Known tradeoffs (explicit)

- Narrowing the first supported subset to scalar `role` means the repo's `HelloWorld2` example shape may remain unsupported at first even though it sits in the same file today.
- Adding a tiny `Makefile` or equivalent local build surface is extra repo structure, but it buys the rerunnable contract the ask explicitly wants.
- Choosing `Lark` early forces near-term decisions on comments, indentation, and parser mode, but that pressure is desirable because it exposes language shapes that may be too hacky to keep.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

The repo currently contains:

- language-design notes
- parser-fit and library research
- example source/reference pairs for `01` through `09`
- a checked-out `for_reference_only/lark` tree that can be consulted while designing the first grammar

There is already a canonical planning doc for the Hello World compiler bootstrap, but there is still no runnable grammar or verification path.

## 2.2 What's broken / missing (concrete)

- No grammar file exists for the language
- No parser or compiler implementation exists
- No local `make` or similar rerun command exists
- The current `01_hello_world` example set has a cold-read hole: the source file contains `HelloWorld` and `HelloWorld2`, but the checked-in ref corresponds to only one rendered output

That means the project can keep inventing syntax faster than it can prove the language is actually parseable.

## 2.3 Constraints implied by the problem

- The first runnable loop should turn example ambiguity into an explicit plan decision or explicit error, not hidden behavior.
- The bootstrap must stay tight enough that later feature additions extend the grammar rather than replacing it.
- The verification surface should be cheap enough to rerun every time a new example or language feature is added.

# 3) Research Grounding (external + internal "ground truth")

## 3.1 External anchors (papers, systems, prior art)

For this bootstrap, the relevant external-style anchors already available in-repo are the checked-out `Lark` materials:

- `for_reference_only/lark/docs/grammar.md` for concrete grammar authoring model and terminology
- `for_reference_only/lark/docs/parsers.md` for parser-mode tradeoffs
- `for_reference_only/lark/examples/indented_tree.py` for indentation-sensitive parsing patterns close to this DSL's shape
- `for_reference_only/lark/lark/indenter.py` as the reference boundary for using built-in indentation support instead of inventing our own

Deeper external grounding can happen later if parser mode or grammar structure remains unclear after the first deep dive.

## 3.2 Internal ground truth (code as spec)

Current authoritative inputs for this bootstrap are:

- `docs/LANGUAGE_DESIGN_NOTES.md`
- `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md`
- `docs/COMPILER_ERRORS.md`
- `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md`
- `examples/01_hello_world/prompts/AGENTS.prompt`
- `examples/01_hello_world/ref/AGENTS.md`

Secondary extension pressure comes from the later example sequence in `examples/02_sections` through `examples/09_outputs`, but those examples should inform the next steps after the first Hello World grammar loop is working.

No canonical owner path exists yet for parsing or compilation; this plan will create that path instead of allowing a second experimental parser surface to appear.

## 3.3 Open questions from research

- Should the first `Lark` implementation start directly with `LALR` plus an indenter, or use a more forgiving parser mode until the grammar stabilizes?
- Should comment handling be ignored entirely at parse time, or preserved just enough to support better error locations and future tooling?
- Should the acceptance path use the current `AGENTS.prompt` plus explicit agent targeting, or should the first implementation introduce a dedicated Hello World-only fixture so the first contract is cleaner?
- Does the first bootstrap grammar need only scalar `role`, or is it worth covering the nested `HelloWorld2` role form immediately to avoid a split example story?
- Which grammar pressures count as acceptable idiomatic `Lark` use versus "hack pressure" that should force a language simplification?

# 4) Current Architecture (as-is)

## 4.1 On-disk structure

Current structure is docs, examples, and reference material only:

- `docs/` contains the language direction and planning artifacts
- `examples/` contains the authored source and expected rendered outputs
- `for_reference_only/lark/` contains a checked-out reference implementation and docs for Lark

There is no compiler-owned source directory yet.

## 4.2 Control paths (runtime)

No runtime path exists today. There is no source read -> parse -> AST -> render -> verify loop yet.

## 4.3 Object model + key abstractions

The repo currently implies language concepts such as:

- `agent`
- `role`
- `workflow`
- rendered title versus internal key identity

But there is no implemented object model yet, even for the Hello World subset.

## 4.4 Observability + failure behavior today

There is no parser or compiler failure surface today because nothing runs. The only current signal is human comparison across notes, examples, and refs.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. This is a local language/compiler bootstrap.

# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

The smallest credible future structure is:

- one compiler-owned grammar file checked into the repo
- one small Python implementation path for parse, AST, semantic checks, and Markdown render
- one local verification surface such as a `Makefile`
- one stable place for source fixtures and reference-output comparisons

Exact paths should be locked in `deep-dive`, not invented ad hoc during implementation.

## 5.2 Control paths (future)

The intended single owner path is:

`make hello-world` -> Python runner -> `Lark` grammar parse -> AST transform -> semantic validation -> Markdown render -> compare against `examples/01_hello_world/ref/AGENTS.md`

If the acceptance source still contains multiple agents, the runner must target `HelloWorld` explicitly rather than assume a hidden selection rule.

## 5.3 Object model + abstractions (future)

The minimum credible model for the bootstrap is:

- source file
- agent declaration
- scalar role field
- workflow field with title plus ordered body strings
- compiled Markdown document

If agent targeting is required for the first acceptance path, that selection logic must be a small explicit boundary rather than an ambient convention.

## 5.4 Invariants and boundaries

- `Lark` owns syntax parsing
- compiler-owned code owns AST construction, semantic validation, and Markdown rendering
- the grammar file is the syntax SSOT for the supported subset
- acceptance targeting must stay explicit while multi-agent output mapping is unsettled
- unsupported syntax fails before rendering
- custom wiring around `Lark` must stay minimal and justified; if the grammar starts depending on clever rescue logic, the language shape should change

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.

# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
|---|---|---|---|---|---|---|---|
| Example source | `examples/01_hello_world/prompts/AGENTS.prompt` | `HelloWorld`, `HelloWorld2` | Authored source contains two role forms in one file | Treat as the first syntax fixture and explicitly resolve how `HelloWorld` is targeted for acceptance | The first grammar needs one honest source contract | Supported Hello World subset plus explicit acceptance targeting rule | End-to-end parse/compile comparison |
| Example output | `examples/01_hello_world/ref/AGENTS.md` | rendered document | Checked-in Markdown contract only | Treat as the first renderer acceptance target | The bootstrap needs one exact output truth surface | Generated Markdown for `HelloWorld` must match this file | End-to-end output comparison |
| Language doctrine | `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md` | language rules and fail-loud direction | Docs-only truth today | Keep aligned with the first shipped subset | Avoid grammar drift and fake feature support | Grammar and compiler errors must stay consistent with notes | Manual review of touched docs |
| Example audit | `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md` | example ambiguity notes | Documents current cold-read gaps | Use as a spec-hole input, not as runtime truth | The first grammar should surface known holes instead of hiding them | Explicit note on `01` source/ref ambiguity | Manual review |
| Lark reference | `for_reference_only/lark/` | docs and examples only | Available for study, not runtime ownership | Consult during design only | Keep product code local while still using the checked-out reference | No direct runtime dependency on the reference tree itself | Manual review |
| Compiler implementation | new path under repo root | grammar / parser / AST / renderer / runner | Missing | Add the first real implementation path | The language needs a real parser loop | Source in, explicit target selected, Markdown out | Unit and integration checks to be chosen later |
| Local build surface | new repo-root `Makefile` or equivalent | `make hello-world` | Missing | Add one simple rerun command | The ask explicitly wants a cheap rerun loop as examples evolve | One command runs the first acceptance loop | End-to-end local verification |

## 6.2 Migration notes

- No canonical compiler path exists yet; the bootstrap must create one rather than start a parallel experiment.
- No deprecated APIs are expected because there is no live compiler today.
- If the implementation adopts explicit agent targeting for the first acceptance path, that rule must be documented clearly and treated as temporary until multi-agent output mapping is properly specified.
- Live docs about the supported subset must stay honest after implementation lands.
- Any parser customization beyond ordinary `Lark` usage needs an explicit justification or should be rejected in favor of simplifying the language subset.

# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

This section will be authored fully by `phase-plan` after research and deep-dive. The current expected shape is:

- freeze the first supported grammar subset and acceptance rule for `HelloWorld`
- implement one grammar -> AST -> render loop
- wire one simple rerun command such as `make hello-world`
- use the first running loop to record the next spec holes before expanding to `02_sections`
- reject hack-driven grammar growth; change the language subset instead when necessary

# 8) Verification Strategy (common-sense; non-blocking)

Avoid verification bureaucracy. Prefer the smallest credible signal and keep the loop cheap enough to rerun often.

## 8.1 Unit tests (contracts)

Prefer at most one or two tight checks around AST construction or Markdown rendering if they materially shorten debugging once the grammar exists.

## 8.2 Integration tests (flows)

The primary signal should be one end-to-end local command, likely `make hello-world`, that parses the supported source, compiles `HelloWorld`, and compares the result to the checked-in Markdown ref.

## 8.3 E2E / device tests (realistic)

Not applicable beyond the local compiler loop. Do not add bespoke harnesses, editor automation, or other verification ceremony just to prove the first grammar works.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

This is a local bootstrap only. There is no staged rollout surface yet.

## 9.2 Telemetry changes

None initially. Clear parse and compile errors are enough for the first pass.

## 9.3 Operational runbook

If the loop fails, stop on the explicit parser or compiler error and either tighten the grammar/spec boundary or fix the implementation. Do not add recovery behavior just to keep the loop green.

# 10) Decision Log (append-only)

## 2026-04-06 - Use Lark for the first runnable language bootstrap

Context

The repo already leans toward `Lark`, a checked-out reference tree is available, and the ask now explicitly wants the emerging language to become parseable and rerunnable from a real grammar.

Options

- `Lark`
- `pyparsing`
- `LibCST`
- a small hand-written parser

Decision

Use `Lark` as the first real grammar and parser front-end for the Hello World bootstrap.

Consequences

- The syntax becomes a checked-in grammar instead of remaining prose only.
- Parser mode, comment handling, and indentation strategy now become concrete design decisions instead of abstract notes.
- Later examples should extend the same grammar rather than restart parser selection.

Follow-ups

- Confirm this North Star before deeper planning.
- Use `research` and `deep-dive` to lock parser mode, grammar layout, and the first acceptance-source rule.

## 2026-04-06 - Keep `HelloWorld` targeting explicit in the first acceptance loop

Context

`examples/01_hello_world/prompts/AGENTS.prompt` currently contains both `HelloWorld` and `HelloWorld2`, while the checked-in ref corresponds to only one rendered output. A first runnable loop must not hide that ambiguity behind accidental selection behavior.

Options

- treat the first agent in the file as the implicit acceptance target
- introduce a dedicated Hello World-only fixture immediately
- keep the current file and target `HelloWorld` explicitly in the first acceptance loop

Decision

Plan around explicit `HelloWorld` targeting unless the example set is cleaned up before implementation begins.

Consequences

- The first runner stays honest about which source shape is actually under test.
- The bootstrap can move forward without pretending multi-agent output mapping is already specified.
- Later language work may still replace this with a better package-output contract once the examples settle.

Follow-ups

- Confirm whether you want that explicit-targeting default, or whether you would rather split `01_hello_world` into cleaner fixtures before implementation starts.

## 2026-04-06 - Prefer language simplification over Lark hacks

Context

The user explicitly wants minimum unique custom wiring around `Lark`, prefers using stock `Lark` capabilities as far as possible, and wants hard failure when the language starts demanding hacks.

Options

- freely adapt the parser with custom side logic to preserve the current language surface
- keep custom wiring minimal and treat hack pressure as a signal to simplify the language
- abandon `Lark` if the first grammar is uncomfortable

Decision

Keep `Lark` as the parser front-end, use as much of it out of the box as possible, and treat non-idiomatic parser hacks as a design failure that should push us to simplify or adjust the language.

Consequences

- Grammar design will be biased toward syntax that fits naturally in `Lark`.
- Hard parser edges become useful language feedback rather than implementation debt.
- The plan should reject bespoke recovery layers or parser scaffolding unless they are clearly ordinary `Lark` usage and genuinely minimal.

Follow-ups

- Encode this as a hard evaluation criterion during `research` and `deep-dive`.
