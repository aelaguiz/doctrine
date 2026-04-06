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

- Outcome: Bootstrap the first real PyPrompt language grammar with `Lark`, prove it against the Hello World subset, and use that shipped slice to define the next requirement: a reusable compiler-verification framework rather than a growing pile of one-off example checkers.
- Problem: The repo had no runnable grammar, no parse/compile loop, and no cheap way to rerun the language contract as examples evolve; now that the first loop exists, the next architecture risk is scaling verification by hard-coding more `hello world`-style checks one example at a time.
- Approach: Lock the first grammar to the exact syntax pressure already present in `examples/01_hello_world/prompts/AGENTS.prompt`, author one checked-in `Lark` grammar for it, parse into a minimal typed AST, compile a selected agent into Markdown, and treat that bootstrap loop as proof of viability rather than the final compiler-test architecture.
- Plan: Ground the first grammar in the current examples and design notes, keep the current `01_hello_world` source file parseable as-authored, wire one runner plus one `make` target, keep every unsupported construct fail-loud, and explicitly open the next phase to research and design a reusable compiler test framework before example growth turns verification into a maintenance mess.
- Non-negotiables: One parser front-end only; one checked-in grammar only; minimum custom wiring around `Lark`; `.prompt` files are the input-language SSOT; checked `AGENTS.md` files are approximate rendered examples, not pristine byte-level goldens, and may contain bugs; no hand-written fallback parser; no hidden "first agent wins" behavior; no source slicing or pre-processing to dodge unsupported syntax in the accepted fixture; if a source file contains multiple agents, the runner must select the target agent explicitly; if the language shape forces hacks, tighten or change the language instead of layering parser workarounds; and the shipped `check_hello_world` path must remain a bootstrap proof, not the long-term pattern for full-compiler verification.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-06
external_research_grounding: not started
deep_dive_pass_2: not started
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

A small `Lark`-based grammar and one repeatable local verification command can parse the agreed Hello World subset of the PyPrompt input language, compile the targeted `HelloWorld` agent into Markdown that reflects the authored prompt semantics, surface drift or bugs in approximate `AGENTS.md` examples explicitly, and force the next compiler stage to converge on a reusable verification framework instead of proliferating one-off hard-coded example checkers.

## 0.2 In scope

- Defining the first checked-in grammar for the language using `Lark` grammar syntax
- Using the checked-out `for_reference_only/lark` repo only as reference material for grammar shape, parser mode, and indentation-sensitive examples
- Supporting the smallest syntax surface needed for the first Hello World bootstrap:
  - line comments beginning with `#`
  - blank lines
  - top-level `agent Name:`
  - the exact `01_hello_world` agent field shape:
    - exactly one `role`
    - followed by exactly one `workflow`
    - no extra agent fields, repeated fields, or reordered fields in the bootstrap subset
  - both `role` forms already present in `examples/01_hello_world/prompts/AGENTS.prompt`:
    - scalar `role: "..."` text
    - titled `role: "Title"` block with quoted string lines
  - `workflow: "Title"` with one or more indented quoted string lines
- Choosing an explicit acceptance path for the current `examples/01_hello_world/prompts/AGENTS.prompt` multi-agent file so the system targets `HelloWorld` on purpose rather than by accident
- Treating checked `AGENTS.md` files as approximate rendered examples and bug-finding aids, not as byte-level language truth
- Building one small runner that reads source, parses it, builds a minimal AST, and renders Markdown
- Wiring one simple local command such as `make hello-world` to run the bootstrap parse/compile/verify loop
- Using this loop to expose holes in the current example/spec story before extending the grammar to later examples
- Making a reusable full-compiler verification framework an explicit next-step requirement, so the bootstrap checker does not silently become the testing architecture
- Preferring stock `Lark` facilities wherever they fit cleanly, including ordinary grammar rules, the built-in indentation machinery when needed, and standard tree/transform tooling

## 0.3 Out of scope

- Nested field blocks, keyed workflow entries, or block shapes beyond the exact `role` and `workflow` forms already present in `examples/01_hello_world/prompts/AGENTS.prompt`
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
- Implementing the generalized compiler test framework in this bootstrap pass; the requirement is in scope now, but its concrete design should be re-cut through external research before more compiler growth lands
- General agent-field flexibility beyond the exact bootstrap subset, including reordered fields, repeated `role` / `workflow` fields, or additional agent fields
- Any attempt to model `99_not_clean_but_useful` in this first grammar pass
- Custom parser sidecars, bespoke recovery layers, or syntax-specific hacks whose main job is to rescue a language shape that does not fit cleanly in `Lark`

## 0.4 Definition of done (acceptance evidence)

- A documented local command such as `make hello-world` runs the first end-to-end loop
- That loop parses `examples/01_hello_world/prompts/AGENTS.prompt` as-authored, explicitly targets `HelloWorld`, emits Markdown from prompt semantics, and passes a small semantic smoke check for the expected Hello World shape
- If the rendered output differs from `examples/01_hello_world/ref/AGENTS.md`, the loop reports that diff explicitly as advisory evidence or a likely ref/renderer bug instead of assuming the ref wins
- Unsupported constructs outside the initial subset fail loudly with a clear parser or compiler error
- The checked-in grammar and runner structure leave a credible extension path to `02_sections` without replacing the parser front-end or inventing a second syntax model
- The canonical plan explicitly reserves a next phase for a reusable compiler-verification framework, so future example growth does not default to more hard-coded `check_<example>` entrypoints

## 0.5 Key invariants (fix immediately if violated)

- `Lark` is the single parser front-end for the supported language subset
- One checked-in grammar file is the syntax source of truth for the supported subset
- Parsing, AST construction, semantic validation, and Markdown rendering remain separate responsibilities even if each layer is small
- No hand-written fallback parser, best-effort rendering, or hidden alternate parse path is allowed
- `.prompt` files are the language input SSOT; `AGENTS.md` files are derived output examples only
- Checked `AGENTS.md` refs are approximate, manually built artifacts that may contain bugs and must not overrule prompt semantics or explicit design decisions
- The current accepted source fixture must parse as-authored without pre-slicing, fixture duplication, or hidden source rewriting
- The acceptance path for `HelloWorld` must be explicit while the current `01_hello_world` source/ref relationship remains one-source-to-one-approximate-output-example
- The bootstrap subset stays structurally exact: one `role` followed by one `workflow`, with anything else failing loudly until later examples earn broader flexibility
- The renderer never invents visible headings or extra blank-line structure that are not implied by explicit authored titles and source ordering
- Grammar growth follows the example sequence and design notes; unsupported features fail loudly instead of being guessed
- If a proposed syntax feature requires non-idiomatic parser hacks, the default response is to change or defer the language feature instead of normalizing the hack
- Example-specific hard-coded checks may prove the first slice, but they must not become the durable verification architecture for the full compiler

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
- The existing `AGENTS.md` refs were manually built as examples and are expected to contain drift or outright bugs.
- The language direction is example-first and intentionally wants parser growth to follow the example sequence.
- The checked-out `for_reference_only/lark` tree is available for reference, but it is not itself the product code path.
- The likely grammar is indentation-sensitive, so parser-mode and indenter choices matter early.
- The user explicitly wants hard failure when the language shape starts demanding hacks; changing the language is preferred to building parser scaffolding around it.
- The current `check_hello_world` loop is intentionally narrow and would become a maintenance problem if copied across `02`, `03`, `04`, and beyond.

## 1.3 Architectural principles (rules we will enforce)

- One checked-in grammar owns the supported syntax surface.
- One parse -> AST -> render control path owns the bootstrap compiler.
- The verification loop must target `HelloWorld` explicitly while output selection rules are unsettled.
- Unsupported syntax is an error surface, not a silent branch.
- Prefer stock `Lark` grammar/lexer/parser/indenter/transform patterns before any custom wiring.
- If clean `Lark` usage stops fitting, treat that as language-design feedback first.
- Later example support extends the same core architecture rather than introducing parallel parsers or ad hoc readers.
- Compiler verification should converge on one reusable corpus-driven or contract-driven framework, not a sequence of bespoke `check_<example>` scripts.

## 1.4 Known tradeoffs (explicit)

- Supporting both `role` forms present in `examples/01_hello_world/prompts/AGENTS.prompt` is slightly broader than the original scalar-only sketch, but it avoids fixture slicing and stays within ordinary `Lark` grammar and AST work.
- Adding a tiny `Makefile` or equivalent local build surface is extra repo structure, but it buys the rerunnable contract the ask explicitly wants.
- Choosing `Lark` early forces near-term decisions on comments, indentation, and parser mode, but that pressure is desirable because it exposes language shapes that may be too hacky to keep.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

The repo currently contains:

- language-design notes
- parser-fit and library research
- example source pairs for `01` through `11` plus manually built approximate rendered refs
- a checked-out `for_reference_only/lark` tree that can be consulted while designing the first grammar

There is already a canonical planning doc for the Hello World compiler bootstrap, but there is still no runnable grammar or verification path.

## 2.2 What's broken / missing (concrete)

- No grammar file exists for the language
- No parser or compiler implementation exists
- No local `make` or similar rerun command exists
- The current `01_hello_world` example set has a cold-read hole: the source file contains `HelloWorld` and `HelloWorld2`, but the checked-in ref corresponds to only one rendered output
- The current `AGENTS.md` refs are approximate examples, so output disagreements cannot be resolved by blindly assuming the ref is correct

That means the project can keep inventing syntax faster than it can prove the language is actually parseable.

## 2.3 Constraints implied by the problem

- The first runnable loop should turn example ambiguity into an explicit plan decision or explicit error, not hidden behavior.
- The bootstrap must stay tight enough that later feature additions extend the grammar rather than replacing it.
- The verification surface should be cheap enough to rerun every time a new example or language feature is added.
- The verification surface must scale structurally as the compiler grows; a hand-written assertion bundle per example is acceptable only as bootstrap proof, not as the long-term model.

# 3) Research Grounding (external + internal "ground truth")

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- `for_reference_only/lark/docs/parsers.md` and `for_reference_only/lark/docs/json_tutorial.md` — adopt `parser='lalr'` as the first product parser mode and pin `lexer='contextual'` with it; reject Earley as the default bootstrap path because the first supported subset is intentionally narrow, the desired loop should hard-fail on grammar pressure, and the local Lark docs position LALR plus the contextual lexer as the idiomatic fast path for LR-compatible grammars.
- `for_reference_only/lark/examples/indented_tree.py` and `for_reference_only/lark/lark/indenter.py` — adopt the stock `Indenter` pattern with `_INDENT` / `_DEDENT` tokens and a custom `_NL` token; this is the clearest built-in path for indentation-sensitive grammars and keeps indentation handling inside ordinary Lark extension points instead of inventing a side preprocessor.
- `for_reference_only/lark/lark/grammars/common.lark` — adopt stock terminals for the bootstrap subset where they fit cleanly: `CNAME` for names, `ESCAPED_STRING` for quoted strings, `WS_INLINE` for inline whitespace, and `SH_COMMENT` for `#` comment lines; reject custom identifier/string/comment regexes unless the examples force them.
- `for_reference_only/lark/docs/grammar.md` — adopt `%ignore` for inline whitespace, but keep standalone comment lines inside `_NL` when indentation handling and `strict=True` make `%ignore SH_COMMENT` collide with the newline token; this keeps the bootstrap on ordinary grammar boundaries instead of adding rescue logic.
- `for_reference_only/lark/examples/advanced/create_ast.py` and `for_reference_only/lark/lark/ast_utils.py` — adopt a normal parse-tree to dataclass-AST flow using `Transformer` and `ast_utils.create_transformer()`; reject a hand-written tree walker as the default bootstrap path because the library already provides the minimal structured transform surface we need.
- `for_reference_only/lark/docs/how_to_use.md` — adopt `strict=True` as the default grammar-validation stance for the first LALR bootstrap loop because it hard-fails shift/reduce and regex collisions instead of normalizing them; note that regex collision checks depend on the `interegular` dependency path, so this becomes an explicit bootstrap choice rather than hidden behavior.
- `for_reference_only/lark/README.md` and `for_reference_only/lark/docs/tools.md` — reject stand-alone parser generation as part of the first bootstrap even though Lark supports it for LALR, because it would add a second generated artifact surface before the grammar has stabilized.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `examples/01_hello_world/prompts/AGENTS.prompt` — current authored source contract for the first bootstrap, including both `role` forms that the first grammar must parse as-authored.
  - `examples/01_hello_world/ref/AGENTS.md` — approximate manually built rendered example for `HelloWorld`; useful for output-shape guidance and ref-bug discovery, but not a byte-level spec.
  - `docs/LANGUAGE_DESIGN_NOTES.md` — language doctrine: example-first growth, explicit authored titles, fail-loud validation, and parser growth that follows the example sequence.
  - `docs/COMPILER_ERRORS.md` — canonical numbered compiler-error direction for fail-loud behavior.
  - `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md` — known spec holes, especially the `01_hello_world` source/ref ambiguity and the risk of accidental output-selection behavior.
  - `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md` — prior internal grounding that `Lark` is the best fit if the custom syntax is preserved and that later complexity pressure is more semantic than syntactic.
- Canonical path / owner to reuse:
  - `docs/HELLO_WORLD_PARSE_TO_MARKDOWN_POC_2026-04-06.md` — current planning SSOT; no code owner path exists yet, so implementation must create exactly one compiler-owned path instead of scattered scripts.
  - repo root current state (`.`) — there is no existing compiler package, no `Makefile`, and no Python project metadata yet; this confirms there is no canonical implementation path to reuse and also increases the risk of ad hoc drift if deep-dive does not pick one clean owner.
- Existing patterns to reuse:
  - `for_reference_only/lark/examples/indented_tree.py` — concrete pattern for `parser='lalr'`, `postlex=Indenter()`, `%declare _INDENT _DEDENT`, and an `_NL` token that absorbs indentation spaces and comment lines; the shipped bootstrap keeps comment lines in `_NL` rather than separately ignoring `SH_COMMENT` so `strict=True` stays clean.
  - `for_reference_only/lark/lark/indenter.py` — stock indentation stack behavior, built-in `DedentError`, and the exact post-lex boundary that should own indentation semantics.
  - `for_reference_only/lark/lark/grammars/common.lark` — stock reusable terminals that can cover the first subset without custom token regexes.
  - `for_reference_only/lark/examples/advanced/create_ast.py` and `for_reference_only/lark/lark/ast_utils.py` — minimal AST construction path with dataclasses and automatic rule-to-class transformer mapping.
  - `for_reference_only/lark/docs/json_tutorial.md` — recommended sequencing: start with a normal parse-tree flow, then only consider tree-less LALR once the transformer is already working.
- Prompt surfaces / language contract to reuse:
  - `examples/01_hello_world/prompts/AGENTS.prompt` — the first source-language fixture under test.
  - `examples/01_hello_world/ref/AGENTS.md` — the first approximate rendered-language example under review.
  - `docs/LANGUAGE_DESIGN_NOTES.md` — the current intended semantics that the first grammar subset must not silently contradict.
- Existing grounding / tool / file exposure:
  - `for_reference_only/lark/` — local docs, examples, grammar terminals, and implementation code are already available in-repo, so initial parser research can stay local and evidence-based.
  - read-only repo shell access — enough to inspect examples, docs, and the reference Lark tree without inventing external dependency on web research for the first pass.
- Duplicate or drifting paths relevant to this change:
  - `examples/01_hello_world/prompts/AGENTS.prompt` versus `examples/01_hello_world/ref/AGENTS.md` — one source file currently contains both `HelloWorld` and `HelloWorld2` while the checked-in ref covers only one rendered output.
  - `docs/LIBRARY_RESEARCH.md` and `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md` — overlapping parser-choice research already exists and both point toward `Lark`; deep-dive should reuse that grounding instead of reopening library selection from scratch.
  - repo-wide absence of compiler code — without a chosen owner path, the main drift risk is spawning one-off scripts, scratch grammars, or alternative parser experiments.
- Capability-first opportunities before new tooling:
  - `for_reference_only/lark/lark/grammars/common.lark` and `%ignore` — cover names, strings, inline whitespace, and standalone `#` comment lines before inventing custom token machinery.
  - `for_reference_only/lark/lark/indenter.py` — use the stock indentation post-lexer before inventing a custom indentation preprocessor.
  - `for_reference_only/lark/docs/how_to_use.md` strict mode — use built-in collision failure before writing lint-like side checks.
  - `for_reference_only/lark/lark/ast_utils.py` — use stock transformer/AST helpers before writing a bespoke tree-to-object layer.
  - explicit `HelloWorld` targeting in the bootstrap runner — avoids inventing multi-output package semantics before the examples settle.
- Behavior-preservation signals already available:
  - semantic smoke checks derived from `examples/01_hello_world/prompts/AGENTS.prompt` plus the current design notes — the primary signal that the renderer preserved authored semantics.
  - advisory diff against `examples/01_hello_world/ref/AGENTS.md` — useful for catching renderer bugs or ref bugs without pretending the ref is pristine truth.
  - Lark `strict=True` on the bootstrap grammar — structural signal that the grammar is not silently relying on unresolved LALR collisions.
  - whole-file parse of `examples/01_hello_world/prompts/AGENTS.prompt` plus explicit `HelloWorld` selection — protects against fixture slicing or hidden first-agent behavior.
- Likely code implications from this research:
  - the first grammar file should likely import `common.CNAME`, `common.ESCAPED_STRING`, `common.WS_INLINE`, and `common.SH_COMMENT`, declare `_INDENT` / `_DEDENT`, define `_NL` in the same style as `for_reference_only/lark/examples/indented_tree.py`, keep standalone comment lines inside `_NL`, and cover both `role` shapes present in `examples/01_hello_world/prompts/AGENTS.prompt`.
  - the first parser path should likely be `Lark(..., parser='lalr', lexer='contextual', postlex=<custom indenter>, strict=True)` rather than Earley.
  - the first implementation should keep the ordinary parse-tree -> transformer -> AST -> Markdown flow and only consider tree-less LALR after behavior is stable.
  - stand-alone parser generation and Earley ambiguity tooling are not first-pass ownership.

## 3.3 Open questions (evidence-based)

- When should the repo add either a second approximate rendered example for `HelloWorld2` or a stronger machine-checked output contract distinct from `AGENTS.md`, so the second `role` form present in `examples/01_hello_world/prompts/AGENTS.prompt` stops being parseable-but-lightly-verified bootstrap pressure? — settle when the first loop is running and `phase-plan` decides whether that is part of the next grammar step or a separate cleanup pass.
- If a future example requires syntax that breaks clean `LALR` + stock `Indenter` usage, do we widen parser mode or simplify the language? — settle by treating LALR collisions or required custom post-processing as evidence and defaulting to language simplification unless the feature is clearly worth the added complexity.
- What is the best-practice verification architecture for a growing compiler like this: golden files, corpus-driven contract tests, AST snapshots, layered parser/compiler/render checks, or some blend? — settle with `arch-step external-research` before the repo adds more example-specific checker entrypoints.
<!-- arch_skill:block:research_grounding:end -->

# 4) Current Architecture (as-is)
<!-- arch_skill:block:current_architecture:start -->
## 4.1 On-disk structure

Current repo structure is still docs-and-examples only:

- `docs/` contains language direction, parser-fit research, and the current architecture plan
- `examples/` contains the authoritative prompt corpus plus approximate rendered refs, including `examples/01_hello_world/prompts/AGENTS.prompt` and `examples/01_hello_world/ref/AGENTS.md`
- `for_reference_only/lark/` contains a checked-out local Lark reference tree for design grounding only
- `.gitignore` excludes `/for_reference_only/`, which reinforces that the reference clone is not the product code path

There is no compiler-owned package, no `Makefile`, no build metadata, and no runtime verification entrypoint.

## 4.2 Control paths (runtime)

There is no runtime control path yet. The current effective flow is human-only:

1. Read example source under `examples/`
2. Read approximate rendered refs under `examples/*/ref`
3. Read language notes and research docs under `docs/`
4. Infer the intended grammar and output behavior by hand

For Hello World specifically, the source/ref relationship is manual:

- `examples/01_hello_world/prompts/AGENTS.prompt` contains both `HelloWorld` and `HelloWorld2`
- `examples/01_hello_world/ref/AGENTS.md` contains one approximate rendered output only
- inline comments in `examples/01_hello_world/prompts/AGENTS.prompt` also carry render-contract pressure:
  - scalar `role` should render as plain leading text
  - titled `role` should render as a Markdown heading block
- there is no code path that parses the file, selects an agent, or proves which behavior is actually implemented

## 4.3 Object model + key abstractions

The repo currently implies a growing language surface without any implemented model behind it.

Immediate bootstrap pressure from `examples/01_hello_world` is:

- `PromptFile`
- `Agent`
- `Role` in two shapes:
  - scalar text
  - titled block with ordered quoted lines
- `Workflow` with explicit title and ordered quoted lines

Near-term extension pressure already exists in later examples:

- keyed nested workflow entries in `examples/02_sections`
- imports and symbol references in `examples/03_imports`
- inheritance and ordered patching in `examples/04_inheritance` through `examples/06_nested_workflows`
- additional declaration and contract pressure in `examples/08_inputs`, `examples/09_outputs`, `examples/10_turn_outcomes`, and `examples/11_skills_and_tools`

None of those concepts has an implemented AST, parser tree transform, semantic validator, or renderer today.

## 4.4 Observability + failure behavior today

There is no parser or compiler failure surface today because nothing runs.

Current failure signals are indirect:

- docs and examples can drift without an executable proof
- the `01_hello_world` mixed-fixture ambiguity is visible only through manual reading
- grammar collisions, indentation mistakes, and unsupported syntax have no runtime error path yet
- output mismatches can only be spotted by human comparison today, and those mismatches may indicate either a renderer bug or a bug in the approximate ref

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. This is a local compiler/bootstrap design.
<!-- arch_skill:block:current_architecture:end -->

# 5) Target Architecture (to-be)
<!-- arch_skill:block:target_architecture:start -->
## 5.1 On-disk structure (future)

The canonical implementation path will be a repo-root Python package plus one repo-root command surface:

- `pyproject.toml`
  - minimal Python metadata
  - declares bootstrap dependencies `lark` and `interegular`
- `pyprompt/__init__.py`
  - package boundary only
- `pyprompt/grammars/pyprompt.lark`
  - single syntax source of truth for the currently supported subset
- `pyprompt/indenter.py`
  - one tiny `Indenter` subclass and no custom indentation preprocessor
- `pyprompt/model.py`
  - typed dataclasses for the supported syntax model
- `pyprompt/parser.py`
  - grammar loading, `Lark` construction, and parse-tree -> AST transform
- `pyprompt/compiler.py`
  - explicit agent selection and fail-loud semantic validation
- `pyprompt/renderer.py`
  - Markdown rendering for the supported subset
- `pyprompt/check_hello_world.py`
  - narrow verification entrypoint for the first loop
- `Makefile`
  - user-facing `hello-world` target

The minimal relevant repo tree should look like this once the bootstrap exists:

```text
.
├── Makefile
├── pyproject.toml
├── examples/
│   └── 01_hello_world/
│       ├── prompts/
│       │   └── AGENTS.prompt
│       └── ref/
│           └── AGENTS.md
└── pyprompt/
    ├── __init__.py
    ├── check_hello_world.py
    ├── compiler.py
    ├── indenter.py
    ├── model.py
    ├── parser.py
    ├── renderer.py
    └── grammars/
        └── pyprompt.lark
```

Reading the tree top-down should already explain ownership:

- `examples/01_hello_world/prompts/AGENTS.prompt` is the authored source fixture
- `examples/01_hello_world/ref/AGENTS.md` is the approximate rendered example, not a pristine contract
- `pyprompt/grammars/pyprompt.lark` is the syntax SSOT
- `pyprompt/*.py` owns parse -> validate -> render behavior
- `Makefile` is the human-facing run surface

Deliberately not in the first architecture:

- `scripts/` helpers as a second code owner path
- duplicate fixtures under `tests/fixtures/`
- multiple grammar files for the same supported language subset
- stand-alone generated parsers
- direct runtime imports from `for_reference_only/lark`

## 5.2 Control paths (future)

The first canonical control path will be:

1. `make hello-world`
2. `python -m pyprompt.check_hello_world`
3. `pyprompt.check_hello_world` calls into `pyprompt.parser` and `pyprompt.compiler`
4. `pyprompt.parser` loads `pyprompt/grammars/pyprompt.lark` via `Lark.open(..., rel_to=__file__)`
5. `pyprompt.parser` constructs `Lark(parser='lalr', lexer='contextual', postlex=PyPromptIndenter(), strict=True, maybe_placeholders=False)`
6. `pyprompt.parser` parses `examples/01_hello_world/prompts/AGENTS.prompt` as-authored and returns a typed AST for the whole file; the grammar declares `_INDENT` / `_DEDENT`, and `_NL` must own newline + trailing indentation whitespace + standalone `#` comment lines in the same stock pattern used by `for_reference_only/lark/examples/indented_tree.py`
7. `pyprompt.compiler` selects `HelloWorld` explicitly, validates the supported subset for that selected agent, and hands the validated node to `pyprompt.renderer`
8. `pyprompt.renderer` emits Markdown
9. `pyprompt.check_hello_world` renders Markdown, runs a small semantic smoke check derived from the prompt/input contract, and may diff the result against `examples/01_hello_world/ref/AGENTS.md` as advisory output-shape evidence

Dependency boundary:

- the active Python environment must provide `lark` and `interegular`
- the bootstrap command does not silently downgrade from `strict=True`
- missing dependencies, grammar collisions, parse errors, semantic validation errors, and semantic smoke-check failures all fail loudly
- advisory diffs against approximate refs are reported explicitly and may indicate either renderer bugs or ref bugs

The intended developer UX from repo root is deliberately small:

```bash
make hello-world
```

That command is the default human entrypoint. It should do exactly one thing:

```bash
python -m pyprompt.check_hello_world
```

The direct module invocation remains valid for debugging, but it is not a second product surface. The first pass should not add a broader CLI, subcommands, or alternate runners.

This bootstrap entrypoint is intentionally narrow. It is a proof slice, not permission to add `check_sections.py`, `check_imports.py`, and more one-off verifier modules as the compiler grows. The next verification phase must converge on one reusable compiler-test surface.

Expected run behavior:

- success path:
  - parse `examples/01_hello_world/prompts/AGENTS.prompt`
  - compile the explicitly selected `HelloWorld` agent
  - render Markdown and pass the semantic smoke check derived from the input contract
  - exit `0`
- fail-loud path:
  - missing `lark` or `interegular` exits nonzero
  - grammar collisions or parser construction failures exit nonzero
  - parse errors exit nonzero
  - missing or duplicate target-agent names exit nonzero
  - out-of-subset agent shapes exit nonzero
  - semantic smoke-check failures exit nonzero
- advisory path:
  - diff against `examples/01_hello_world/ref/AGENTS.md` may be printed as a likely renderer bug or ref bug

There is intentionally no first-pass UX for:

- selecting a different target agent from the shell
- generating new refs automatically
- fallback parsing modes
- partial-success or best-effort rendering

## 5.3 Object model + abstractions (future)

The minimum supported model for the bootstrap will be:

- `PromptFile`
  - `agents: list[Agent]`
- `Agent`
  - `name: str`
  - `role: RoleScalar | RoleBlock`
  - `workflow: Workflow`
- `RoleScalar`
  - `text: str`
- `RoleBlock`
  - `title: str`
  - `lines: list[str]`
- `Workflow`
  - `title: str`
  - `lines: list[str]`

Compiler responsibilities are explicit:

- `parser.py` owns syntax parsing and AST construction
- `compiler.py` owns agent selection and subset validation
- `renderer.py` owns Markdown shape

Bootstrap validation and render behavior are also explicit:

- the compile entrypoint requires an explicit target agent name; there is no implicit "first agent wins" mode
- duplicate agent names in one parsed file are a compiler error
- selecting a missing target agent is a compiler error
- the bootstrap subset supports only agents whose field body is exactly one `role` followed by one `workflow`
- reordered fields, duplicate fields, missing required fields, or extra fields are outside the first subset and fail before rendering
- `RoleScalar` renders as opening body text with no heading
- `RoleBlock` renders as `## <title>` followed by its ordered lines
- `Workflow` renders as `## <title>` followed by its ordered lines
- sibling quoted strings inside one block preserve order and render as consecutive lines; the renderer must not invent bullets or extra blank lines between them

The first grammar will intentionally parse both `role` shapes already present in `examples/01_hello_world/prompts/AGENTS.prompt`, but the first bootstrap loop will treat the `HelloWorld` `AGENTS.md` file as an approximate rendered example only, not as an exact golden.

## 5.4 Invariants and boundaries

- `pyprompt/grammars/pyprompt.lark` is the one syntax SSOT for the supported subset
- `Lark` owns syntax parsing through stock features only:
  - `parser='lalr'`
  - `lexer='contextual'`
  - stock `Indenter`
  - stock `common` terminals
  - `%ignore` for inline whitespace only
  - `strict=True`
- parser construction also pins `maybe_placeholders=False` so optional branches do not inject surprise `None` values into the bootstrap AST
- `_NL` owns newline + indentation whitespace + standalone comment lines; comment handling must stay compatible with the stock `Indenter` contract rather than moving into a side preprocessor
- the bootstrap subset supports only agents whose field body is exactly one `role` followed by one `workflow`
- the accepted source fixture must parse as-authored; no source slicing, regex extraction, or shadow fixture copies are allowed
- explicit target-agent selection is required whenever a source file contains multiple agents
- target-agent resolution must fail loudly for missing names or duplicate agent declarations
- `for_reference_only/lark` is design input only and never a runtime dependency surface
- unsupported syntax fails before rendering
- if a future syntax feature requires non-idiomatic parser rescue logic, the default answer is to change or defer that language feature

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.
<!-- arch_skill:block:target_architecture:end -->

# 6) Call-Site Audit (exhaustive change inventory)
<!-- arch_skill:block:call_site_audit:start -->
## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
|---|---|---|---|---|---|---|---|
| Dependency owner | `pyproject.toml` | project metadata | Missing | Add minimal project metadata and declare `lark` + `interegular` | `make hello-world` needs a canonical dependency owner and must not silently downgrade from strict mode | Active env installs the exact parser deps for the bootstrap loop | `make hello-world` |
| Package boundary | `pyprompt/__init__.py` | package root | Missing | Add one importable package boundary | Avoid scripts-first drift and create one canonical owner path | All bootstrap code imports through `pyprompt.*` | Indirect via module execution |
| Grammar SSOT | `pyprompt/grammars/pyprompt.lark` | grammar file | Missing | Add the first checked grammar file covering the exact `01_hello_world` syntax pressure, including `%declare _INDENT _DEDENT` and an `_NL` token that absorbs indentation whitespace and standalone `#` comment lines | One grammar file must own the supported subset and stay compatible with the stock `Indenter` contract | Whole-file parse contract for `examples/01_hello_world/prompts/AGENTS.prompt` | `make hello-world` |
| Indentation boundary | `pyprompt/indenter.py` | `PyPromptIndenter` | Missing | Add one minimal `Indenter` subclass using stock Lark behavior | Keep indentation handling idiomatic and fail-loud | `_NL`, `_INDENT`, `_DEDENT` are the only indentation contract | `make hello-world` |
| Syntax model | `pyprompt/model.py` | `PromptFile`, `Agent`, `RoleScalar`, `RoleBlock`, `Workflow` | Missing | Add the minimal AST dataclasses for the first supported subset | Keep parse, validation, and render responsibilities separate | Typed AST boundary for the bootstrap subset, including the exact one-role-then-workflow agent shape | Optional focused unit checks later; end-to-end now |
| Parser boundary | `pyprompt/parser.py` | grammar loader, `Lark` constructor, transformer | Missing | Add grammar loading via `Lark.open(..., rel_to=__file__)`, `parser='lalr'`, `lexer='contextual'`, `strict=True`, `maybe_placeholders=False`, and parse-tree -> AST transform | Canonical parse owner path must exist before implementation grows and the bootstrap AST should not be padded with placeholder `None` values | Parse current `01` source file as-authored and return AST for all agents in file | `make hello-world` |
| Compiler boundary | `pyprompt/compiler.py` | explicit agent selection + semantic validation | Missing | Add fail-loud target-agent selection, duplicate-name checks, and subset validation | Avoid hidden first-agent behavior and keep unsupported constructs loud | `compile_prompt(..., agent_name)` or equivalent narrow boundary; missing or duplicate targets fail | `make hello-world` |
| Markdown render | `pyprompt/renderer.py` | Markdown emitter | Missing | Add renderer for the first supported AST subset with explicit `RoleScalar` versus headed-block behavior | Renderer must own Markdown shape explicitly instead of leaving `HelloWorld2` semantics to guesswork | Selected agent -> Markdown string with scalar `role` as plain text and block forms as headed sections | Ref comparison in `make hello-world` |
| Bootstrap entrypoint | `pyprompt/check_hello_world.py` | `main` | Missing | Add one narrow bootstrap verification module | One canonical runtime path should sit behind the Make target without pretending approximate refs are exact goldens | Parse current fixture, select `HelloWorld`, render, run semantic smoke checks, and optionally print advisory diff evidence | `make hello-world` |
| User command | `Makefile` | `hello-world` | Missing | Add one simple rerun command | The user asked for a cheap verification loop as examples evolve | `make hello-world` is the human-facing bootstrap contract | `make hello-world` |
| Source fixture | `examples/01_hello_world/prompts/AGENTS.prompt` | `HelloWorld`, `HelloWorld2` | Authoritative source contains both `role` shapes in one file, plus inline comments about render intent | Keep as the first authoritative source fixture and require the parser to accept it as-authored | Avoid source slicing, duplicate fixtures, or drift between examples and implementation | Whole-file parse plus explicit target-agent selection; source comments remain behavior evidence until a second checked ref exists | `make hello-world` |
| Approximate output example | `examples/01_hello_world/ref/AGENTS.md` | rendered Markdown | Manually built approximate output example for `HelloWorld` only | Keep as advisory output-shape evidence, not as an authoritative exact golden | Prevents the plan from treating manual examples as pristine truth while still using them to find bugs | Rendered output may be diffed against it and any mismatch must be called out as a likely ref bug or renderer bug | `make hello-world` |
| Verification architecture follow-on | `pyprompt/check_hello_world.py`, future compiler-test surface TBD | bootstrap checker versus reusable framework | Current shipped verifier is intentionally hard-coded to the Hello World slice | Use external research plus a follow-on design pass to choose one scalable compiler verification architecture before more examples land | Prevents the repo from normalizing a `check_<example>` proliferation pattern | Bootstrap checker is proof only; future compiler verification must converge on one reusable contract framework | Phase 4 planning, then future implementation |
| Live doctrine docs | `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md`, `docs/COMPILER_ERRORS.md`, `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md` | language rules and known gaps | Docs-only truth today | Review and update as implementation lands if shipped behavior or resolved ambiguities differ | Avoid stale truth after code exists | Docs must match the shipped subset and the actual fail-loud behavior | Manual review |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - repo-root package `pyprompt/` plus repo-root `Makefile`
- Deprecated APIs (if any):
  - none; there is no live compiler yet
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - no `scripts/`-first bootstrap path
  - no duplicate fixtures under `tests/fixtures/`
  - no second grammar file for the same supported subset
  - no stand-alone parser artifact in the first pass
- Capability-replacing harnesses to delete or justify:
  - any hand-written lexer
  - any custom indentation preprocessor
  - any bespoke CST-to-AST walker outside ordinary `Transformer` / `ast_utils` usage
  - any source-slicing helper that extracts only `HelloWorld` from the mixed file
  - any direct runtime import from `for_reference_only/lark`
- Live docs/comments/instructions to update or delete:
  - `docs/LANGUAGE_DESIGN_NOTES.md` if the first shipped subset clarifies the supported `role` shapes
  - `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md` if the shipped bootstrap subset hardens the exact `01` agent shape or render contract beyond its earlier scalar-only summary
  - `docs/COMPILER_ERRORS.md` if the first implementation earns concrete parse/compile failures that should be numbered
  - `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md` if the `01_hello_world` ambiguity is materially resolved by shipped architecture
- Behavior-preservation signals for refactors:
  - whole-file parse of `examples/01_hello_world/prompts/AGENTS.prompt`
  - semantic smoke checks derived from the prompt/input contract and current design notes
  - advisory diff against `examples/01_hello_world/ref/AGENTS.md` when useful for finding renderer/ref bugs
  - `strict=True` grammar construction with no silent fallback

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
|---|---|---|---|---|
| Live doctrine | `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md`, `docs/COMPILER_ERRORS.md` | Keep shipped subset and failure behavior aligned with the one canonical compiler path | Prevents docs from drifting ahead of the implemented grammar | include |
| First runtime fixtures | `examples/01_hello_world/prompts/AGENTS.prompt`, `examples/01_hello_world/ref/AGENTS.md` | Treat `examples/` as the authoritative prompt corpus plus approximate rendered examples | Prevents source/ref truth from being silently inverted | include |
| Next grammar pressure | `examples/02_sections/prompts/AGENTS.prompt` | Extend the same `pyprompt/` package and the same `pyprompt.lark` grammar file for keyed workflow entries | Prevents a second parser path when grammar scope grows | defer |
| Next grammar pressure | `examples/03_imports/prompts/AGENTS.prompt` and imported prompt files | Extend the same owner path for imports and symbol resolution | Prevents import behavior from being prototyped in side scripts | defer |
| Semantic growth | `examples/04_inheritance` through `examples/07_handoffs` | Add inheritance and routing semantics through the same AST/compiler path, not parallel prototypes | Prevents semantic drift and duplicated merge logic | defer |
| Declaration growth | `examples/08_inputs`, `examples/09_outputs`, `examples/10_turn_outcomes`, `examples/11_skills_and_tools` | Add new declarations and agent-side contract structure through the same package and grammar SSOT | Prevents declaration-specific side parsers and one-off side readers | defer |
| Output-pressure corpus | `examples/99_not_clean_but_useful` | Keep as rendering pressure only, not bootstrap grammar ownership | Prevents overbuilding the grammar too early | exclude |
| Alternative parser libs | `for_reference_only/LibCST`, `for_reference_only/pyparsing` | Do not reopen parser choice during bootstrap implementation | Prevents tool drift and parallel experiments | exclude |
| Duplicate test truth | `tests/fixtures/` or similar duplicate corpora | Do not create copied first-pass fixtures outside `examples/` | Prevents source/ref drift | exclude |
| Compiler verification growth | `pyprompt/check_hello_world.py`, future shared verification owner path | Converge future compiler testing onto one reusable framework instead of per-example scripts | Prevents verification drift and maintenance blow-up as examples multiply | include |
<!-- arch_skill:block:call_site_audit:end -->

# 7) Depth-First Phased Implementation Plan (authoritative)

<!-- arch_skill:block:phase_plan:start -->
> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

Warn-first note:

- `external_research_grounding` and `deep_dive_pass_2` are still not started.
- This plan proceeds anyway because the current artifact already locks one narrow owner path, one parser mode, one fixture, one run command, and one fail-loud boundary set. No unresolved external dependency or broader product question is blocking the Hello World bootstrap.

## Phase 1 - Parser Foundation

Status: COMPLETE

Completed work:
- Added the canonical package and dependency path with `pyproject.toml`, `pyprompt/__init__.py`, and the Phase 1 parser foundation files.
- Shipped a stock-`Lark` grammar plus `PyPromptIndenter` on the planned `lalr` / `contextual` / `strict=True` / `maybe_placeholders=False` boundary.
- Verified whole-file parsing of `examples/01_hello_world/prompts/AGENTS.prompt` and confirmed the AST contains both `HelloWorld` and `HelloWorld2`.
- Tightened bootstrap comment handling to standalone `#` lines through `_NL` after `strict=True` exposed the `%ignore SH_COMMENT` collision.

* Goal:
  Establish the canonical package/dependency path and get a stock-`Lark` whole-file parse of `examples/01_hello_world/prompts/AGENTS.prompt` into typed AST nodes without alternate parser paths.
* Work:
  Add `pyproject.toml`, `pyprompt/__init__.py`, `pyprompt/grammars/pyprompt.lark`, `pyprompt/indenter.py`, `pyprompt/model.py`, and `pyprompt/parser.py`.
  Pin `parser='lalr'`, `lexer='contextual'`, `strict=True`, `maybe_placeholders=False`, stock common terminals, and the `_NL` / `_INDENT` / `_DEDENT` contract already grounded in `for_reference_only/lark/examples/indented_tree.py`.
  Use the ordinary `Transformer` / `ast_utils` path for parse-tree to AST conversion instead of inventing a bespoke CST walker.
  Keep this phase limited to syntax parsing and typed AST construction for the whole file; do not add rendering, CLI broadening, or output-generation features here.
* Verification (smallest signal):
  Run a direct Python import/invocation that constructs the parser in the active environment and parses `examples/01_hello_world/prompts/AGENTS.prompt` as-authored.
  Confirm the resulting AST contains both `HelloWorld` and `HelloWorld2`, proving the accepted fixture parses as a whole file rather than via hidden source slicing.
* Docs/comments (propagation; only if needed):
  Add one brief code comment at the grammar/indenter boundary explaining that `_NL` owns newline, indentation whitespace, and standalone comment lines.
  Add one brief code comment at parser construction if the pinned `Lark` options are not otherwise obvious in code.
* Exit criteria:
  The canonical package/dependency path exists.
  Whole-file parse of `examples/01_hello_world/prompts/AGENTS.prompt` succeeds as-authored.
  There is no direct runtime dependency on `for_reference_only/lark` and no second parser path.
* Rollback:
  If stock `Lark` cannot parse the accepted fixture cleanly without rescue logic, revert the parser-foundation files together and tighten the language subset before adding compiler or renderer code.

## Phase 2 - Compile, Render, and One Command

Status: COMPLETE

Completed work:
- Added `pyprompt/compiler.py`, `pyprompt/renderer.py`, `pyprompt/check_hello_world.py`, and the repo-root `Makefile`.
- Implemented explicit target-agent selection, duplicate-name detection, and fail-loud bootstrap-subset validation for exactly one `role` followed by one `workflow`.
- Implemented the first render contract for both current `role` forms and the titled `workflow` block.
- Verified `make hello-world` passes and the negative checks fail loudly for missing target selection plus invalid bootstrap shapes.

* Goal:
  Turn the parsed AST into explicit agent selection and checked Markdown output behind one repo-root command.
* Work:
  Add `pyprompt/compiler.py`, `pyprompt/renderer.py`, `pyprompt/check_hello_world.py`, and `Makefile`.
  Implement explicit target-agent selection, duplicate-name detection, and exact bootstrap-subset validation for the one-`role`-then-one-`workflow` agent shape.
  Implement the first render contract exactly as planned from the input-language semantics: `RoleScalar` opens the document as plain text, `RoleBlock` renders a headed section, `Workflow` renders a headed section, and sibling strings preserve order without invented bullets or extra blank lines.
  Make `make hello-world` call only `python -m pyprompt.check_hello_world`; do not add a broader CLI, ref-generation mode, or alternate runner surface.
  Run semantic smoke checks against the rendered output and, when helpful, diff it against `examples/01_hello_world/ref/AGENTS.md` as advisory evidence without treating that ref as exact truth.
* Verification (smallest signal):
  `make hello-world` exits `0` when parse/render/smoke checks pass for `HelloWorld`.
  A tiny direct negative check proves missing-target selection fails nonzero.
  A tiny inline invalid-source check proves reordered, repeated, missing, or extra bootstrap fields fail before render without needing a permanent duplicate fixture.
  If the advisory diff against `examples/01_hello_world/ref/AGENTS.md` shows drift, that drift is called out explicitly as a likely ref bug or renderer bug rather than silently treated as a compiler failure.
* Docs/comments (propagation; only if needed):
  Add one brief code comment at the compiler boundary explaining the no-implicit-target rule.
  Add one brief code comment at the renderer boundary explaining that headings come only from explicit authored titles and source ordering.
* Exit criteria:
  The repo has one human-facing command, `make hello-world`, and it drives the canonical parse -> validate -> render -> semantic-smoke-check loop.
  Missing or duplicate target-agent names fail loudly.
  Out-of-subset agent shapes fail before rendering.
  Any drift against approximate `AGENTS.md` examples is surfaced explicitly instead of being mistaken for canonical truth.
  No alternate runner, fallback mode, or best-effort output path has been introduced.
* Rollback:
  Keep the Phase 1 parser foundation, but revert compiler/renderer/check/Makefile changes if the render contract or target-selection contract proves wrong and needs to be recut before shipping.

## Phase 3 - Reality Sync and Minimal Hardening

Status: COMPLETE

Completed work:
- Updated `docs/LANGUAGE_DESIGN_NOTES.md` to reflect the shipped Hello World bootstrap subset and comment-handling rule.
- Updated `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md` to remove the stale scalar-only `01` summary and record the strict-mode comment-token lesson.
- Updated `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md` to note that the bootstrap now targets `HelloWorld` explicitly while `HelloWorld2` still lacks its own approximate rendered ref.
- Reran the Hello World check after doc sync so the code, plan, and live doctrine stayed aligned.

* Goal:
  Sync live docs to the shipped bootstrap, close the most likely drift surfaces, and record any newly exposed next-step holes without broadening product scope.
* Work:
  Update `docs/LANGUAGE_DESIGN_NOTES.md` if shipped behavior tightens the supported `role` shapes or the exact bootstrap subset.
  Update `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md` so it no longer lags the canonical plan on parser construction, exact agent shape, or render contract.
  Update `docs/COMPILER_ERRORS.md` only if concrete numbered parse/compile errors were actually earned by implementation.
  Update `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md` only if explicit `HelloWorld` targeting, discovered ref bugs, or shipped behavior materially clarifies the `01` ambiguity it called out.
  Record any newly surfaced post-bootstrap language holes as explicit deferred follow-ups before touching `02_sections`; do not solve later examples in this phase.
* Verification (smallest signal):
  Rerun `make hello-world` after reality-sync edits to confirm the green path still holds.
  Do one short manual spot-check that the live docs now name the actual owner path, command surface, and fail-loud boundaries that the code ships.
* Docs/comments (propagation; only if needed):
  Rewrite or delete stale live doc claims instead of leaving legacy wording beside the new code truth.
* Exit criteria:
  The canonical plan and the touched live doctrine docs no longer materially disagree about the shipped Hello World bootstrap.
  Remaining open items are clearly deferred to later grammar growth rather than silently shipped.
* Rollback:
  Revert only doc-sync edits that do not match shipped behavior; do not keep stale explanations once code truth is known.

## Phase 4 - Verification Framework Research And Re-cut

Status: NOT STARTED

* Goal:
  Turn the current bootstrap checker into an explicit stepping stone toward a reusable full-compiler verification architecture instead of letting example-by-example hard-coded checks become the default.
* Work:
  Run `arch-step external-research` focused on best practices for compiler and language-tool verification.
  Compare reusable strategies such as corpus-driven fixture suites, layered parser/compiler/render checks, semantic contract tests, golden-file usage, and negative-corpus error tests.
  Decide which truth surfaces should be authoritative for compiler testing as the example corpus grows, while keeping `.prompt` as input SSOT and keeping approximate `AGENTS.md` refs out of byte-level truth unless they are deliberately re-earned.
  Re-cut Sections 5, 6, 7, and 8 so the canonical plan names one durable verification owner path instead of implying more `check_<example>` modules.
  Record whether `pyprompt/check_hello_world.py` remains as a thin bootstrap slice beneath the shared framework or gets subsumed by it.
* Verification (smallest signal):
  External research is folded into the canonical plan with concrete adopt/reject reasoning.
  The updated plan explicitly rejects verification growth by copy-pasting example-specific checkers.
  The next implementation pass can name one canonical compiler-test path with bounded truth surfaces and no ambiguity about goldens versus contracts.
* Docs/comments (propagation; only if needed):
  Update the plan and any touched doctrine docs so they no longer imply that the current Hello World checker pattern scales by repetition.
* Exit criteria:
  The canonical plan names a reusable verification architecture requirement for the full compiler.
  The next step after research is a concrete design or implementation pass, not more ad hoc checker growth.
  The artifact is explicit about which verification signals are semantic contracts, which are advisory refs, and which belong in negative-corpus testing.
* Rollback:
  If external research does not sharpen the architecture materially, keep the bootstrap checker as-is but do not widen it by cloning the pattern across more examples.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

Avoid verification bureaucracy. Prefer the smallest credible signal and keep the loop cheap enough to rerun often.

## 8.1 Unit tests (contracts)

Prefer at most one or two tight checks around AST construction or Markdown rendering if they materially shorten debugging once the grammar exists.

## 8.2 Integration tests (flows)

The primary shipped signal today is one end-to-end local command, `make hello-world`, that parses the supported source, compiles `HelloWorld`, and runs semantic smoke checks derived from the prompt/input contract. Diffs against checked `AGENTS.md` refs are advisory bug-finding signals, not byte-level truth.

That is bootstrap proof, not the final compiler-test architecture. Once the compiler grows beyond `01`, integration verification must converge on a reusable framework instead of multiplying example-specific checker modules.

## 8.3 E2E / device tests (realistic)

Not applicable beyond the local compiler loop. Do not add bespoke harnesses, editor automation, or other verification ceremony just to prove the first grammar works.

## 8.4 Compiler Verification Framework (next)

The next verification requirement is architectural, not cosmetic:

- the repo needs one scalable verification framework for the compiler as the example corpus grows
- that framework should be researched before the repo adds more hard-coded example-specific checkers
- the framework must keep `.prompt` as input SSOT, keep approximate `AGENTS.md` refs advisory unless explicitly re-earned, and preserve fail-loud negative testing for unsupported or invalid source shapes
- the framework should separate parser, compiler, renderer, and end-to-end contract signals cleanly enough that later examples do not turn the suite into brittle golden churn

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

## 2026-04-06 - Use one root `pyprompt/` package plus `Makefile` as the bootstrap owner path

Context

Deep-dive confirmed that the repo currently has no code owner path at all: no package, no `Makefile`, and no build metadata. The main architecture risk is ad hoc drift into scratch scripts, duplicate fixtures, or multiple grammar surfaces.

Options

- start with one-off scripts and promote a package later
- start with `src/` layout and broader packaging scaffolding immediately
- use one repo-root `pyprompt/` package plus a repo-root `Makefile`

Decision

Use one repo-root `pyprompt/` package as the canonical code owner path and a repo-root `Makefile` as the user-facing verification surface.

Consequences

- Grammar, parser, AST/model, compiler, renderer, and bootstrap check all live under one import path.
- The first verification loop gets a stable user command without creating a second code owner surface.
- Future example growth extends the same package and the same grammar file instead of branching into scripts or parallel parsers.

Follow-ups

- Implement the package boundary, grammar file, and `hello-world` Make target in the first implementation phase.

## 2026-04-06 - Parse `examples/01_hello_world/prompts/AGENTS.prompt` as-authored

Context

The accepted Hello World source fixture currently contains both `HelloWorld` and `HelloWorld2`. Because the user prefers changing the language over building hacks, deep-dive needed to choose between source slicing, duplicate fixtures, or a slightly wider first grammar.

Options

- slice the source or extract only `HelloWorld` before parsing
- duplicate the fixture into a second bootstrap-only source file
- parse the current source file as-authored and support both `role` shapes already present there

Decision

Parse `examples/01_hello_world/prompts/AGENTS.prompt` as-authored, support both `role` shapes already present in that file, and keep explicit `HelloWorld` selection for the first bootstrap loop.

Consequences

- The first grammar stays honest to the current example corpus without adding preprocessing hacks.
- The bootstrap loop still has one approximate Hello World output example for human comparison because `examples/01_hello_world/ref/AGENTS.md` remains the first rendered example on disk.
- `HelloWorld2` becomes real syntax pressure for the first parser and renderer even before it has its own approximate output example.

Follow-ups

- Decide in a later phase whether to add a second approximate rendered example for `HelloWorld2`, or a stronger checked output contract distinct from `AGENTS.md`, once the first loop is running.

## 2026-04-06 - Treat strict LALR plus stock `Lark` pieces as a hard boundary

Context

Research and deep-dive both converged on the same implementation shape: `LALR`, stock `Indenter`, stock common terminals, `%ignore`, and a normal Transformer/AST flow. The user explicitly asked for hard failure if the design starts demanding hacks.

Options

- start permissively with Earley or non-strict parser settings and tighten later
- keep `Lark` but normalize custom parser rescue logic when pressure appears
- lock the bootstrap to strict LALR and stock `Lark` extension points

Decision

Lock the bootstrap architecture to strict LALR and stock `Lark` extension points. If that stops fitting cleanly, treat it as language-design feedback rather than an excuse to add parser scaffolding.

Consequences

- Grammar collisions and missing dependency support fail early.
- Indentation handling stays inside `Indenter` rather than a side preprocessor.
- The implementation is forced to keep the language subset shaped for ordinary `Lark` usage.

Follow-ups

- Keep `interegular` in the bootstrap dependency path so `strict=True` remains real rather than ceremonial.

## 2026-04-06 - Pin the bootstrap to predictable AST construction and explicit render semantics

Context

A second deep-dive pass against `examples/01_hello_world/*` and the local `for_reference_only/lark` docs/code showed that the owner path was already locked, but three implementation-sensitive edges were still too implied: how `_NL` must cooperate with `Indenter`, whether optional grammar branches may inject placeholder `None` values into the AST, and how `RoleScalar` versus headed blocks should render in the first pass.

Options

- leave those details to implementation taste
- pin the stock-Lark construction details and the first render contract now

Decision

Pin the bootstrap to `lexer='contextual'` plus `maybe_placeholders=False`, require `_NL` to absorb indentation whitespace and standalone comment lines in the stock `Indenter` pattern, and state the first render contract explicitly: scalar `role` is plain opening text, while `RoleBlock` and `workflow` render headed sections.

Consequences

- The first parser/AST path stays closer to ordinary `Lark` behavior and avoids accidental `None` handling complexity.
- Regex-collision checking stays on an explicitly supported strict-mode lexer instead of a hidden default.
- Comment handling and indentation remain one coherent grammar/postlex contract instead of drifting into parser rescue logic.
- `HelloWorld2` stops being render-shaped guesswork even before it has its own approximate output example.

Follow-ups

- Keep the implementation honest to these boundaries in the first `phase-plan` and implementation phases.

## 2026-04-06 - Keep the bootstrap agent shape exact

Context

Another deep-dive sweep against the `01_hello_world` fixture showed one remaining implementation escape hatch: the plan still implied that every bootstrap agent has one `role` and one `workflow`, but it did not yet state whether field order, duplicates, or extra fields were part of the first supported subset.

Options

- leave field ordering and multiplicity flexible for the bootstrap as long as the chosen fixture parses
- lock the bootstrap subset to the exact field order already used by `examples/01_hello_world/prompts/AGENTS.prompt`

Decision

Lock the first shipped subset to the exact `01` agent body shape: exactly one `role`, followed by exactly one `workflow`, with any reordered, repeated, missing, or extra fields treated as out-of-subset failures.

Consequences

- The first grammar can stay narrower and more idiomatic to `Lark` instead of pre-solving general field flexibility.
- Compiler validation has a crisp fail-loud boundary instead of implementation taste.
- The parser-fit analysis doc becomes a live drift surface because it still summarizes `01` more loosely than the plan now does.

Follow-ups

- Keep broader field flexibility explicitly deferred until later examples earn it.

## 2026-04-06 - Treat `AGENTS.md` refs as approximate output examples, not exact truth

Context

The `AGENTS.md` files in `examples/*/ref` were manually built as examples. They are output artifacts, not the input language, and the user explicitly clarified that they should not be treated as pristine byte-level goldens. We should expect to find bugs or drift in them.

Options

- keep treating `AGENTS.md` refs as exact output contracts
- demote them to advisory examples while the `.prompt` files and language doctrine carry the real truth

Decision

Treat `.prompt` files as the input-language SSOT and treat checked `AGENTS.md` refs as approximate rendered examples that may contain bugs.

Consequences

- The bootstrap verifier must derive primary correctness from prompt semantics and explicit language rules, not from byte-for-byte ref matching.
- Diffs against `AGENTS.md` refs become explicit review signals that may indicate either renderer bugs or bugs in the ref artifact.
- Future work may still add a stronger machine-checked output contract, but that contract should be distinct from the current approximate `AGENTS.md` examples unless they are deliberately re-earned and cleaned up.

Follow-ups

- Keep the plan, verifier design, and worklog explicit about approximate refs so the truth hierarchy does not invert again.

## 2026-04-06 - Keep bootstrap comments as standalone lines inside `_NL`

Context

Phase 1 implementation proved one concrete strict-mode edge in the chosen `Lark` shape: keeping `%ignore SH_COMMENT` while also letting `_NL` absorb comment lines created a regex-collision failure under `strict=True`. The bootstrap only needs standalone `#` comment lines today, not free-floating comment trivia.

Options

- keep trying to ignore `SH_COMMENT` separately and add parser-side rescue work
- tighten the bootstrap comment contract so standalone comment lines are owned by `_NL`

Decision

Treat bootstrap comments as standalone `#` lines that travel through `_NL` with indentation whitespace, and keep `%ignore` limited to inline whitespace.

Consequences

- `strict=True` stays real instead of being weakened or bypassed.
- The indentation-sensitive grammar remains on ordinary stock-`Lark` boundaries.
- Inline comment behavior is intentionally out of the bootstrap subset until a later example earns it.

Follow-ups

- Revisit broader comment placement only if a later example proves the language actually needs it.

## 2026-04-06 - Treat the Hello World checker as bootstrap proof, not the full compiler test architecture

Context

The shipped `check_hello_world` path is good evidence that the first grammar slice works, but it is intentionally hard-coded to one example and one target agent. If that pattern is copied into `check_sections`, `check_imports`, `check_inheritance`, and beyond, compiler verification will become a maintenance problem instead of a trustworthy framework.

Options

- keep growing verification by adding more example-specific checker modules
- make reusable compiler verification a formal next requirement and research the right framework before more growth lands

Decision

Keep `check_hello_world` as bootstrap proof only, and make a reusable full-compiler verification framework a formal next-phase requirement.

Consequences

- The current bootstrap remains valid, but it no longer pretends to be the durable testing shape.
- Future compiler verification must be re-cut through explicit research and design rather than incremental checker sprawl.
- The artifact now reserves a dedicated phase for verification-architecture research before wider compiler growth proceeds.

Follow-ups

- Run `arch-step external-research` focused on compiler-test best practices.
- Re-cut the canonical plan after that research so the reusable verification owner path is explicit.
