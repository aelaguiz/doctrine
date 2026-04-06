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

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- `for_reference_only/lark/docs/parsers.md` and `for_reference_only/lark/docs/json_tutorial.md` — adopt `parser='lalr'` as the first product parser mode; reject Earley as the default bootstrap path because the first supported subset is intentionally narrow, the desired loop should hard-fail on grammar pressure, and the local Lark docs position LALR as the fast path when the grammar is LR-compatible.
- `for_reference_only/lark/examples/indented_tree.py` and `for_reference_only/lark/lark/indenter.py` — adopt the stock `Indenter` pattern with `_INDENT` / `_DEDENT` tokens and a custom `_NL` token; this is the clearest built-in path for indentation-sensitive grammars and keeps indentation handling inside ordinary Lark extension points instead of inventing a side preprocessor.
- `for_reference_only/lark/lark/grammars/common.lark` — adopt stock terminals for the bootstrap subset where they fit cleanly: `CNAME` for names, `ESCAPED_STRING` for quoted strings, `WS_INLINE` for inline whitespace, and `SH_COMMENT` for `#` comments; reject custom identifier/string/comment regexes unless the examples force them.
- `for_reference_only/lark/docs/grammar.md` — adopt `%ignore` for inline whitespace and comments rather than threading trivia through the grammar manually, because the Lark docs call out `%ignore` as especially important for LALR grammars.
- `for_reference_only/lark/examples/advanced/create_ast.py` and `for_reference_only/lark/lark/ast_utils.py` — adopt a normal parse-tree to dataclass-AST flow using `Transformer` and `ast_utils.create_transformer()`; reject a hand-written tree walker as the default bootstrap path because the library already provides the minimal structured transform surface we need.
- `for_reference_only/lark/docs/how_to_use.md` — adopt `strict=True` as the default grammar-validation stance for the first LALR bootstrap loop because it hard-fails shift/reduce and regex collisions instead of normalizing them; note that regex collision checks depend on the `interegular` dependency path, so this becomes an explicit bootstrap choice rather than hidden behavior.
- `for_reference_only/lark/README.md` and `for_reference_only/lark/docs/tools.md` — reject stand-alone parser generation as part of the first bootstrap even though Lark supports it for LALR, because it would add a second generated artifact surface before the grammar has stabilized.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `examples/01_hello_world/prompts/AGENTS.prompt` — current authored source contract for the first bootstrap, including the scalar `role` form that the checked-in ref already exercises and the out-of-scope `HelloWorld2` nested-role variant that must stay explicit.
  - `examples/01_hello_world/ref/AGENTS.md` — exact rendered Markdown contract for the `HelloWorld` acceptance target.
  - `docs/LANGUAGE_DESIGN_NOTES.md` — language doctrine: example-first growth, explicit authored titles, fail-loud validation, and parser growth that follows the example sequence.
  - `docs/COMPILER_ERRORS.md` — canonical numbered compiler-error direction for fail-loud behavior.
  - `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md` — known spec holes, especially the `01_hello_world` source/ref ambiguity and the risk of accidental output-selection behavior.
  - `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md` — prior internal grounding that `Lark` is the best fit if the custom syntax is preserved and that later complexity pressure is more semantic than syntactic.
- Canonical path / owner to reuse:
  - `docs/HELLO_WORLD_PARSE_TO_MARKDOWN_POC_2026-04-06.md` — current planning SSOT; no code owner path exists yet, so implementation must create exactly one compiler-owned path instead of scattered scripts.
  - repo root current state (`.`) — there is no existing compiler package, no `Makefile`, and no Python project metadata yet; this confirms there is no canonical implementation path to reuse and also increases the risk of ad hoc drift if deep-dive does not pick one clean owner.
- Existing patterns to reuse:
  - `for_reference_only/lark/examples/indented_tree.py` — concrete pattern for `parser='lalr'`, `postlex=Indenter()`, `%declare _INDENT _DEDENT`, `%ignore SH_COMMENT`, and an `_NL` token that absorbs indentation spaces and comments.
  - `for_reference_only/lark/lark/indenter.py` — stock indentation stack behavior, built-in `DedentError`, and the exact post-lex boundary that should own indentation semantics.
  - `for_reference_only/lark/lark/grammars/common.lark` — stock reusable terminals that can cover the first subset without custom token regexes.
  - `for_reference_only/lark/examples/advanced/create_ast.py` and `for_reference_only/lark/lark/ast_utils.py` — minimal AST construction path with dataclasses and automatic rule-to-class transformer mapping.
  - `for_reference_only/lark/docs/json_tutorial.md` — recommended sequencing: start with a normal parse-tree flow, then only consider tree-less LALR once the transformer is already working.
- Prompt surfaces / language contract to reuse:
  - `examples/01_hello_world/prompts/AGENTS.prompt` — the first source-language fixture under test.
  - `examples/01_hello_world/ref/AGENTS.md` — the first rendered-language fixture under test.
  - `docs/LANGUAGE_DESIGN_NOTES.md` — the current intended semantics that the first grammar subset must not silently contradict.
- Existing grounding / tool / file exposure:
  - `for_reference_only/lark/` — local docs, examples, grammar terminals, and implementation code are already available in-repo, so initial parser research can stay local and evidence-based.
  - read-only repo shell access — enough to inspect examples, docs, and the reference Lark tree without inventing external dependency on web research for the first pass.
- Duplicate or drifting paths relevant to this change:
  - `examples/01_hello_world/prompts/AGENTS.prompt` versus `examples/01_hello_world/ref/AGENTS.md` — one source file currently contains both `HelloWorld` and `HelloWorld2` while the checked-in ref covers only one rendered output.
  - `docs/LIBRARY_RESEARCH.md` and `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md` — overlapping parser-choice research already exists and both point toward `Lark`; deep-dive should reuse that grounding instead of reopening library selection from scratch.
  - repo-wide absence of compiler code — without a chosen owner path, the main drift risk is spawning one-off scripts, scratch grammars, or alternative parser experiments.
- Capability-first opportunities before new tooling:
  - `for_reference_only/lark/lark/grammars/common.lark` and `%ignore` — cover names, strings, inline whitespace, and `#` comments before inventing custom token machinery.
  - `for_reference_only/lark/lark/indenter.py` — use the stock indentation post-lexer before inventing a custom indentation preprocessor.
  - `for_reference_only/lark/docs/how_to_use.md` strict mode — use built-in collision failure before writing lint-like side checks.
  - `for_reference_only/lark/lark/ast_utils.py` — use stock transformer/AST helpers before writing a bespoke tree-to-object layer.
  - explicit `HelloWorld` targeting in the bootstrap runner — avoids inventing multi-output package semantics before the examples settle.
- Behavior-preservation signals already available:
  - `examples/01_hello_world/ref/AGENTS.md` — exact output comparison for the first accepted compile target.
  - Lark `strict=True` on the bootstrap grammar — structural signal that the grammar is not silently relying on unresolved LALR collisions.
  - explicit hard failure on unsupported `HelloWorld2` nested-role syntax while it remains out of scope — protects the promise that the first subset is narrow and honest.
- Likely code implications from this research:
  - the first grammar file should likely import `common.CNAME`, `common.ESCAPED_STRING`, `common.WS_INLINE`, and `common.SH_COMMENT`, declare `_INDENT` / `_DEDENT`, and define `_NL` in the same style as `for_reference_only/lark/examples/indented_tree.py`.
  - the first parser path should likely be `Lark(..., parser='lalr', postlex=<custom indenter>, strict=True)` rather than Earley.
  - the first implementation should keep the ordinary parse-tree -> transformer -> AST -> Markdown flow and only consider tree-less LALR after behavior is stable.
  - stand-alone parser generation and Earley ambiguity tooling are not first-pass ownership.

## 3.3 Open questions (evidence-based)

- Should `strict=True` be part of the bootstrap verification command from day one, which implies choosing how to handle the `interegular` dependency path for regex-collision checking? — settle by confirming acceptable bootstrap dependencies during deep-dive.
- Should the first accepted fixture remain `examples/01_hello_world/prompts/AGENTS.prompt` with explicit `HelloWorld` targeting, or should `HelloWorld2` move to a separate later fixture before implementation starts? — settle by comparing the implementation cost of explicit targeting against the cleanup cost of splitting the example.
- What single on-disk compiler path should own the grammar, runner, AST, and renderer once implementation starts? — settle in deep-dive by choosing one path only and rejecting scratch-script drift.
- If a future example requires syntax that breaks clean `LALR` + stock `Indenter` usage, do we widen parser mode or simplify the language? — settle by treating LALR collisions or required custom post-processing as evidence and defaulting to language simplification unless the feature is clearly worth the added complexity.
<!-- arch_skill:block:research_grounding:end -->

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
