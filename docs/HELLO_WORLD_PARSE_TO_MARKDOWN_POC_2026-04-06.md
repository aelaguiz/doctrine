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
- Plan: Ground the first grammar in the current examples and design notes, keep the current `01_hello_world` source file parseable as-authored, wire one runner plus one `make` target, keep every unsupported construct fail-loud, and then converge verification onto one shared `verify_corpus` path with adjacent `cases.toml` manifests, a filtered `make hello-world` alias, and a planned `02_sections` render contract instead of growing more one-off checker modules.
- Non-negotiables: One parser front-end only; one checked-in grammar only; minimum custom wiring around `Lark`; `.prompt` files are the input-language SSOT; checked `AGENTS.md` files are approximate rendered examples, not pristine byte-level goldens, and may contain bugs; no hand-written fallback parser; no hidden "first agent wins" behavior; no source slicing or pre-processing to dodge unsupported syntax in the accepted fixture; if a source file contains multiple agents, the runner must select the target agent explicitly; if the language shape forces hacks, tighten or change the language instead of layering parser workarounds; the shared verifier must become the only durable compiler-test owner path; and the shipped `check_hello_world` logic must disappear as separate verifier logic once `verify_corpus` covers `01_hello_world`.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-06
external_research_grounding: done 2026-04-06
deep_dive_pass_2: done 2026-04-06
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
- Seeding the first shared verification corpus with three concrete rendered cases:
  - `HelloWorld`
  - `HelloWorld2`
  - `examples/02_sections`
- Locking the first shared-verifier contract and run surface:
  - `examples/*/cases.toml` loaded through Python stdlib `tomllib`
  - `make verify-examples` as the full active-corpus run
  - `make hello-world` as a filtered alias over `examples/01_hello_world/cases.toml`
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
- A custom manifest DSL, inline source-mutation mini-language, snapshot updater, or other verifier machinery beyond adjacent TOML manifests plus ordinary local prompt files

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
- Shared compiler verification converges on `pyprompt.verify_corpus`; one-off checker modules are transitional only and must be deleted once migrated
- `cases.toml` manifests are machine-checked verifier contracts distinct from approximate `AGENTS.md` refs

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

- Whether the repo still wants a second approximate human-readable ref for `HelloWorld2` once the shared verifier owns a machine-checked render contract for it — settle after the shared harness lands and the remaining value of another manual ref is clearer.
- If a future example requires syntax that breaks clean `LALR` + stock `Indenter` usage, do we widen parser mode or simplify the language? — settle by treating LALR collisions or required custom post-processing as evidence and defaulting to language simplification unless the feature is clearly worth the added complexity.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:external_research:start -->
# External Research (best-in-class references; plan-adjacent)

> Goal: anchor the plan in idiomatic compiler-test practices without importing brittle cargo cult. This section is intentionally about reusable verification architecture, not PyPrompt-specific syntax semantics.

## Topics researched (and why)

- Shared compiler-test harnesses and corpus organization — because the plan now explicitly rejects a future of `check_<example>` script proliferation.
- Output assertion strategy for compiler tools — because the repo needs stronger test truth than approximate `AGENTS.md` refs without turning every rendered artifact into brittle byte-for-byte churn.
- Negative corpus and diagnostics testing — because fail-loud unsupported syntax and compiler errors are part of the language contract, not incidental edge cases.
- Fuzzing as an adjunct signal — because parser/compiler frontends benefit from robustness checks, but the plan needs to know whether fuzzing belongs in the first reusable framework or later.

## Findings + how we apply them

### Shared Harnesses And Corpus Design

- Best practices (synthesized):
  - Serious compiler projects centralize test execution in one harness with suites or modes rather than proliferating ad hoc scripts. Rust’s `compiletest` is the main harness for a large, multi-suite compiler test corpus, and Tree-sitter runs parser tests over a dedicated corpus folder rather than per-feature scripts.
  - Test cases usually live near the domain inputs and carry local expectations, whether via inline directives/comments, specialized corpus files, or adjacent expected-output files.
  - The “escape hatch” style test is explicitly treated as the fallback, not the default. Rust documents `run-make` as the general-purpose route only when the normal suites do not fit.
- Recommended default for this plan:
  - Adopt one shared corpus verifier under `pyprompt/`, not more example-specific checker modules.
  - Keep `examples/` as the authoritative prompt corpus and place machine-readable verification manifests adjacent to each example directory instead of duplicating fixtures elsewhere.
  - Use suite-like case categories inside that shared verifier, such as parse-pass, compile-pass, render-contract, and expected-failure cases.
  - Start with a deliberately small seed corpus: `HelloWorld`, `HelloWorld2`, and `02_sections`.
  - Inference from the sources plus repo constraints: adjacent sidecar manifests are a better fit than inline test directives because `.prompt` files are both input-language SSOT and human-facing examples, so the plan should avoid polluting them with compiler-test control syntax unless later evidence proves that is cleaner.
- Pitfalls / footguns:
  - `check_<example>` proliferation creates drift in control paths, duplicated harness logic, and inconsistent truth surfaces.
  - General-purpose escape-hatch recipes become the default if the shared harness is not expressive enough early.
  - Copying prompts into a separate fixture tree makes it harder to keep language examples and compiler tests in sync.
- Sources:
  - Compiletest - Rust Compiler Development Guide — https://rustc-dev-guide.rust-lang.org/tests/compiletest.html — authoritative because it documents the Rust compiler’s main harness, suite model, and when general-purpose recipe tests are appropriate.
  - Writing Tests - Tree-sitter — https://tree-sitter.github.io/tree-sitter/creating-parsers/5-writing-tests.html — authoritative because it documents an established parser project’s corpus-driven testing model.
  - LLVM Testing Infrastructure Guide — https://llvm.org/docs/TestingGuide.html — authoritative because it documents LLVM’s shared regression harness and test organization norms.

### Output Assertions Without Brittle Goldens

- Best practices (synthesized):
  - Shared harnesses support multiple assertion styles instead of forcing every test into full exact-output comparison. Rust UI tests normalize unstable output and can compare by lines when ordering is nondeterministic. LLVM recommends FileCheck-style textual assertions for the parts that matter and warns against fragile incidental output checks.
  - Exact blessed outputs are still useful, but mainly for intentionally stable artifacts and only when normalization or generated check updates keep maintenance tolerable.
  - Tests should be minimal and explicit about what behavior matters, rather than binding to unrelated path names, generated identifiers, or incidental formatting noise.
- Recommended default for this plan:
  - Split verification truth into layers:
    - exact stabilized outputs only for surfaces the repo deliberately wants to lock
    - normalized line-based or targeted excerpt/pattern checks for human-facing Markdown where only some semantics matter
    - machine-readable semantic contracts in the case manifest for facts like selected agent, expected headings, required lines, and expected failure stage
  - Keep approximate `AGENTS.md` refs advisory until they are deliberately re-earned as stable machine-checked outputs.
  - Do not let the reusable verifier default to byte-for-byte Markdown golden files for every example.
- Pitfalls / footguns:
  - brittle whole-file goldens against approximate manual refs
  - assertions that accidentally depend on filesystem paths, ordering noise, or nondeterministic output details
  - snapshot churn that obscures real compiler regressions
- Sources:
  - UI tests - Rust Compiler Development Guide — https://rustc-dev-guide.rust-lang.org/tests/ui.html — authoritative because it documents normalized snapshot comparison, line-based comparison, and output-check controls in the Rust compiler suite.
  - Compiletest directives - Rust Compiler Development Guide — https://rustc-dev-guide.rust-lang.org/tests/directives.html — authoritative because it documents per-test directive controls and normalization hooks in the Rust compiler harness.
  - LLVM Testing Infrastructure Guide — https://llvm.org/docs/TestingGuide.html — authoritative because it documents FileCheck-oriented output verification and fragile-test avoidance in LLVM.

### Negative Corpus And Diagnostics

- Best practices (synthesized):
  - Invalid inputs are first-class test cases, not leftovers. Rust has dedicated suites and directives for expected compile failure, and Tree-sitter has an `:error` attribute specifically for invalid parse cases.
  - A good shared harness distinguishes expected-success and expected-failure modes clearly enough that test authors do not need bespoke scripts for error cases.
  - Diagnostics assertions should focus on stable contract points, such as error class, failure stage, required message excerpts, or normalized output, rather than overfitting the entire raw stderr payload.
- Recommended default for this plan:
  - Add explicit invalid-case support to the shared verifier from the start.
  - The case manifest should encode the failure stage (`parse`, `compile`, later maybe `render`) and the stable expectation (`error code`, exception class, required excerpt, or normalized diagnostic file).
  - Existing human-authored error examples like `COMPILER_ERROR.md` can remain useful reference material, but the shared harness should rely on machine-readable failure contracts instead of raw prose files as primary truth.
- Pitfalls / footguns:
  - only testing happy paths
  - exact stderr snapshots without normalization
  - unclear separation between parse failures and semantic/compiler failures
- Sources:
  - Compiletest - Rust Compiler Development Guide — https://rustc-dev-guide.rust-lang.org/tests/compiletest.html — authoritative because it documents suite-level success and failure modes and when they should be used.
  - UI tests - Rust Compiler Development Guide — https://rustc-dev-guide.rust-lang.org/tests/ui.html — authoritative because it documents compiler-output checking behavior.
  - Writing Tests - Tree-sitter — https://tree-sitter.github.io/tree-sitter/creating-parsers/5-writing-tests.html — authoritative because it documents explicit invalid-parse assertions in parser corpus tests.

### Fuzzing As A Later Complement

- Best practices (synthesized):
  - Coverage-guided fuzzing is valuable for parser/frontend robustness, but it complements rather than replaces deterministic corpus tests.
  - Fuzzers work best when they target a stable entrypoint and mutate a seed corpus, and saved failure inputs should flow back into the deterministic regression suite.
- Recommended default for this plan:
  - Defer fuzzing until after the shared deterministic verifier exists.
  - When it arrives, target the narrow parser/compiler entrypoints and seed from the existing example corpus plus invalid cases.
  - Treat fuzzing as robustness amplification, not as the primary verification architecture.
- Pitfalls / footguns:
  - adding fuzzing before deterministic contract tests exist
  - treating fuzzing as a substitute for explicit parse/compile/render expectations
- Sources:
  - LibFuzzer - a library for coverage-guided fuzz testing — https://llvm.org/docs/LibFuzzer.html — authoritative because it documents corpus-based fuzzing, stable fuzz target entrypoints, and regression reuse of discovered inputs.

## Adopt / Reject summary

- Adopt:
  - one shared corpus-driven verifier under `pyprompt/` as the canonical compiler-test owner path
  - adjacent machine-readable case manifests under `examples/<example>/` so prompts stay authoritative and fixtures do not fork
  - layered verification signals: parse/compile/render/end-to-end, with exact, normalized, or targeted assertions chosen per surface
  - first-class negative corpus support with stable failure-stage expectations
  - fuzzing only as a later complement once the deterministic corpus harness exists
- Reject:
  - more one-off `check_<example>` modules as the verification growth path
  - treating approximate `examples/*/ref/AGENTS.md` files as default exact goldens
  - broad recipe-style escape hatches as the default compiler-test architecture
  - broad fuzzing before the deterministic verifier and example contracts exist

## Open questions (ONLY if truly not answerable)

- Whether later examples beyond `02_sections` will justify broader assertion modes than `exact_lines`, stable failure excerpts, and advisory ref diffs — evidence needed: the first grammar-expansion phases after the shared harness exists.
<!-- arch_skill:block:external_research:end -->

# 4) Current Architecture (as-is)
<!-- arch_skill:block:current_architecture:start -->
## 4.1 On-disk structure

The repo now has a real but still narrow compiler slice:

- `pyproject.toml`
  - declares `lark` and `interegular`
  - already pins `requires-python = ">=3.11"`, which means stdlib `tomllib` is available for the shared verifier
- `Makefile`
  - exposes only `hello-world`
- `pyprompt/`
  - `grammars/pyprompt.lark`
  - `indenter.py`
  - `model.py`
  - `parser.py`
  - `compiler.py`
  - `renderer.py`
  - `check_hello_world.py`
- `examples/`
  - authoritative `.prompt` inputs
  - approximate `ref/AGENTS.md` outputs
  - no checked-in `cases.toml` manifests yet
- `for_reference_only/lark/`
  - local design/reference tree only
  - not a runtime dependency surface

The important missing pieces are now specific, not vague:

- there is no `pyprompt/verify_corpus.py`
- there is no checked-in machine-readable verifier contract under `examples/*/cases.toml`
- there is no canonical home for negative prompt fixtures beyond ad hoc local testing
- `examples/02_sections/` exists only as prompt plus approximate ref, not as executable or even machine-readable verifier truth

## 4.2 Control paths (runtime)

The current shipped runtime flow is:

1. `make hello-world`
2. `python -m pyprompt.check_hello_world`
3. `pyprompt.check_hello_world` calls `parse_file(PROMPT_PATH)`
4. `_run_parse_smoke_check` asserts the parsed agent-name tuple is exactly `("HelloWorld", "HelloWorld2")`
5. `compile_prompt(prompt_file, "HelloWorld")`
6. `render_markdown(compiled)`
7. `_run_render_smoke_check` exact-compares the rendered output against the hard-coded `EXPECTED_RENDERED_LINES` Python constant
8. `_print_advisory_ref_diff` optionally diffs against `examples/01_hello_world/ref/AGENTS.md`

That path proves the bootstrap works, but it also shows the present architectural limit clearly:

- render-contract truth for `HelloWorld` currently lives in Python constants, not in adjacent machine-readable example contracts
- `HelloWorld2` is parsed by the shipped command but does not yet have a checked-in render contract in the verifier path
- `02_sections` has no runtime path at all
- the current command is not a reusable harness; it is one dedicated script for one example directory

## 4.3 Object model + key abstractions

The implemented compiler model is intentionally small:

- `PromptFile`
  - `agents: tuple[Agent, ...]`
- `Agent`
  - `name: str`
  - `fields: tuple[RoleScalar | RoleBlock | Workflow, ...]`
- `RoleScalar`
  - plain opening prose
- `RoleBlock`
  - titled block with ordered lines
- `Workflow`
  - titled block with ordered lines
- `CompiledAgent`
  - explicit handoff from compiler to renderer after bootstrap validation

The important architectural gap is that the verifier does not yet have its own explicit contract model. Instead, the current verifier truth is embedded in `pyprompt/check_hello_world.py` constants:

- `TARGET_AGENT`
- `EXPECTED_AGENT_NAMES`
- `EXPECTED_RENDERED_LINES`

Near-term extension pressure remains unchanged:

- keyed nested workflow entries in `examples/02_sections`
- imports and symbol references in `examples/03_imports`
- inheritance and ordered patching in `examples/04_inheritance` through `examples/06_nested_workflows`
- additional declaration and contract pressure in `examples/08_inputs`, `examples/09_outputs`, `examples/10_turn_outcomes`, and `examples/11_skills_and_tools`

None of those concepts currently has:

- an implemented AST extension
- a checked-in machine-readable verifier contract
- a shared case runner that can report pass/fail stage consistently across examples

## 4.4 Observability + failure behavior today

There is now an explicit parser/compiler failure surface for the shipped bootstrap:

- parser construction fails loudly on grammar collisions under `strict=True`
- parsing fails loudly on unsupported syntax in the shipped subset
- compiler validation fails loudly on missing targets, duplicate targets, and out-of-subset agent shapes
- `make hello-world` exits nonzero when the semantic smoke check fails

Current remaining observability gaps are:

- `check_hello_world.py` catches every exception and collapses it into one human-readable failure line, so the current verifier does not report a stable case-by-case failure stage taxonomy
- there is no checked-in negative corpus, only manually run negative checks
- there is no shared summary surface across multiple cases or manifests
- `HelloWorld2` and `02_sections` have no machine-checked render contract in the shipped runtime path
- approximate refs can still drift without adjacent case manifests unless the verifier grows beyond the bootstrap slice

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. This is a local compiler/bootstrap design.
<!-- arch_skill:block:current_architecture:end -->

# 5) Target Architecture (to-be)
<!-- arch_skill:block:target_architecture:start -->
## 5.1 On-disk structure (future)

The canonical implementation path is still the repo-root Python package plus repo-root `Makefile`, but the durable verifier owner path is now fully specified:

- `pyproject.toml`
  - keeps the parser/runtime dependency boundary
  - does not add a separate manifest-parsing dependency because Python 3.11 stdlib `tomllib` is sufficient
- `pyprompt/grammars/pyprompt.lark`
  - one syntax SSOT
- `pyprompt/indenter.py`
  - one stock-`Lark` indentation boundary
- `pyprompt/model.py`
  - compiler AST dataclasses only
- `pyprompt/parser.py`
  - parse owner path only
- `pyprompt/compiler.py`
  - compile/validate owner path only
- `pyprompt/renderer.py`
  - render owner path only
- `pyprompt/verify_corpus.py`
  - the one durable compiler-verification runner
- `Makefile`
  - user-facing convenience targets only

The minimal relevant repo tree should look like this after the shared verifier lands:

```text
.
├── Makefile
├── pyproject.toml
├── examples/
│   ├── 01_hello_world/
│   │   ├── cases.toml
│   │   ├── prompts/
│   │   │   └── AGENTS.prompt
│   │   └── ref/
│   │       └── AGENTS.md
│   └── 02_sections/
│       ├── cases.toml
│       ├── prompts/
│       │   └── AGENTS.prompt
│       └── ref/
│           └── AGENTS.md
└── pyprompt/
    ├── __init__.py
    ├── compiler.py
    ├── indenter.py
    ├── model.py
    ├── parser.py
    ├── renderer.py
    ├── verify_corpus.py
    └── grammars/
        └── pyprompt.lark
```

Reading the tree top-down should already explain ownership:

- `examples/01_hello_world/prompts/AGENTS.prompt` is the authored source fixture
- `examples/01_hello_world/cases.toml` is the machine-readable verifier contract for both Hello World renders plus any local negative cases that example earns
- `examples/01_hello_world/ref/AGENTS.md` is the approximate rendered example, not a pristine contract
- `examples/02_sections/cases.toml` is part of the initial shared-verifier seed set and begins life as a planned render contract, not a falsely green passing example
- `pyprompt/grammars/pyprompt.lark` is the syntax SSOT
- `pyprompt/*.py` owns parse -> validate -> render behavior
- `pyprompt/verify_corpus.py` is the only long-term verification owner path
- `Makefile` is the human-facing run surface only

Any alternate prompt input needed for negative cases stays under the owning example directory, referenced by relative path from that example’s `cases.toml`. The target architecture explicitly rejects a second fixture tree and rejects inventing a mini patch DSL inside the manifest.

Deliberately not in the first architecture:

- `scripts/` helpers as a second code owner path
- duplicate fixtures under `tests/fixtures/`
- multiple grammar files for the same supported language subset
- stand-alone generated parsers
- direct runtime imports from `for_reference_only/lark`
- one verifier module per example as the long-term testing pattern
- a retained `pyprompt/check_hello_world.py` once the shared verifier covers `01_hello_world`
- a custom manifest language beyond TOML plus stdlib parsing

## 5.2 Control paths (future)

The future full-corpus control path is:

1. `make verify-examples`
2. `python -m pyprompt.verify_corpus`
3. `pyprompt.verify_corpus` discovers `examples/*/cases.toml`
4. each manifest is loaded through stdlib `tomllib`
5. the harness validates the manifest schema and example-relative paths
6. the harness executes every `status = "active"` case through the same parse -> compile -> render owner path
7. any `status = "planned"` case is reported as planned-but-not-executed and does not count green or red
8. the harness emits one summary and exits nonzero if any active case fails or any manifest is structurally invalid

The retained convenience path is:

1. `make hello-world`
2. `python -m pyprompt.verify_corpus --manifest examples/01_hello_world/cases.toml`
3. the shared verifier executes the active `01_hello_world` cases, which means both `HelloWorld` and `HelloWorld2`

This resolves the prior command-surface ambiguity:

- `make hello-world` stays because it is a useful filtered alias for the first example directory
- it no longer owns separate verifier logic
- `pyprompt/check_hello_world.py` is removed once this alias exists

Dependency and failure boundary:

- the active environment must still provide `lark` and `interegular`
- parser construction remains `strict=True`; there is no downgrade path
- missing dependencies, grammar collisions, parse errors, semantic validation errors, active-case assertion failures, and manifest-structure failures all exit nonzero
- advisory diffs against approximate refs are reported explicitly and never decide pass/fail on their own

The intended developer UX from repo root becomes:

```bash
make hello-world
make verify-examples
```

There is intentionally still no first-pass UX for:

- selecting arbitrary case subsets beyond a narrow manifest filter needed by `Makefile`
- generating new refs automatically
- snapshot update modes
- fallback parsing modes
- partial-success or best-effort rendering

## 5.3 Object model + abstractions (future)

The compiler AST stays narrow and explicit:

- `PromptFile`
- `Agent`
- `RoleScalar`
- `RoleBlock`
- `Workflow`
- later, when `02_sections` is implemented, `Workflow` should gain ordered nested section/entry nodes through the same AST instead of through a verifier-only flattening layer

The shared verifier adds one small contract model, kept deliberately minimal:

- top-level manifest fields:
  - `schema_version = 1`
  - `default_prompt = "prompts/AGENTS.prompt"`
- repeated `[[cases]]` entries
- common case fields:
  - `name`
  - `status = "active" | "planned"`
  - `kind = "render_contract" | "parse_fail" | "compile_fail"`
  - optional `prompt` override, always relative to the owning example directory
  - optional `approx_ref`
- `render_contract` fields:
  - `agent`
  - `assertion = "exact_lines"`
  - `expected_lines = [ ... ]`
- `parse_fail` / `compile_fail` fields:
  - `exception_type`
  - `message_contains = [ ... ]`

The first schema intentionally does not overbuild:

- no inline source-mutation DSL
- no regex assertion language
- no snapshot updater
- no separate verifier-only AST

Initial manifests are now fully specified:

- `examples/01_hello_world/cases.toml`
  - one active `render_contract` for `HelloWorld`
  - one active `render_contract` for `HelloWorld2`
  - exact line contracts live in the manifest, not in Python constants
  - `HelloWorld` may also carry an advisory `approx_ref = "ref/AGENTS.md"`
- `examples/02_sections/cases.toml`
  - one planned `render_contract` for `SectionsDemo`
  - exact line contract is authored now as the first non-Hello-World output contract
  - optional `approx_ref = "ref/AGENTS.md"` remains advisory only

Compiler responsibilities stay explicit:

- `parser.py` owns syntax parsing and AST construction
- `compiler.py` owns agent selection and subset validation
- `renderer.py` owns Markdown shape
- `verify_corpus.py` owns case loading, stage dispatch, assertion evaluation, and final summary/exit behavior

Bootstrap validation and render behavior remain explicit:

- the compile entrypoint requires an explicit target agent name; there is no implicit "first agent wins" mode
- duplicate agent names in one parsed file are a compiler error
- selecting a missing target agent is a compiler error
- the current bootstrap subset supports only agents whose field body is exactly one `role` followed by one `workflow`
- reordered fields, duplicate fields, missing required fields, or extra fields are outside the first subset and fail before rendering
- `RoleScalar` renders as opening body text with no heading
- `RoleBlock` renders as `## <title>` followed by its ordered lines
- `Workflow` renders as `## <title>` followed by its ordered lines
- sibling quoted strings inside one block preserve order and render as consecutive lines; the renderer must not invent bullets or extra blank lines between them

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
- one shared corpus verifier, `pyprompt.verify_corpus`, must own full-compiler verification once the follow-on phase lands
- `pyprompt/check_hello_world.py` is deleted once `verify_corpus` covers `examples/01_hello_world`
- machine-readable case expectations live adjacent to `examples/`, not in a duplicate fixture tree
- case manifests use plain TOML parsed by stdlib `tomllib`; no extra manifest parser and no custom mini-language
- per-case `prompt` overrides may point only to files inside the owning example directory; the verifier rejects escaping paths
- `status = "active"` cases execute and gate exit status; `status = "planned"` cases are schema-validated and reported but do not count as green compiler support
- the first shared verifier supports only `render_contract`, `parse_fail`, and `compile_fail` cases, plus `exact_lines` success assertions
- exact rendered-output contracts are stored only where the repo deliberately stabilizes them in machine-readable manifests, not by treating approximate refs as goldens
- approximate refs remain advisory only, even when a case points at them with `approx_ref`
- expected-failure cases are first-class and must encode stable failure-stage expectations
- fuzzing is a later complement to deterministic corpus tests, not a substitute for them

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.
<!-- arch_skill:block:target_architecture:end -->

# 6) Call-Site Audit (exhaustive change inventory)
<!-- arch_skill:block:call_site_audit:start -->
## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
|---|---|---|---|---|---|---|---|
| Dependency owner | `pyproject.toml` | project metadata | Shipped bootstrap dependency owner | Retain as the canonical dependency owner and keep manifest loading on stdlib `tomllib` instead of adding a new parser dependency | The compiler and shared verifier need one real dependency boundary without unnecessary tooling sprawl | Python 3.11 stdlib TOML parsing plus the existing `lark` / `interegular` deps | `make hello-world`, future `make verify-examples` |
| Package boundary | `pyprompt/__init__.py` | package root | Shipped package boundary | Retain as the canonical import path for compiler and verifier code | Avoid scripts-first drift and keep one canonical owner path | All compiler and verifier code imports through `pyprompt.*` | Indirect via module execution |
| Grammar SSOT | `pyprompt/grammars/pyprompt.lark` | grammar file | Shipped bootstrap grammar SSOT | Retain and extend through the same grammar file as later examples land | One grammar file must keep owning the supported subset and stay compatible with the stock `Indenter` contract | Whole-file parse contract for `examples/01_hello_world/prompts/AGENTS.prompt` and later examples | `make hello-world`, future `make verify-examples` |
| Indentation boundary | `pyprompt/indenter.py` | `PyPromptIndenter` | Shipped stock-Lark indentation boundary | Retain as the single indentation contract | Keep indentation handling idiomatic and fail-loud | `_NL`, `_INDENT`, `_DEDENT` remain the only indentation contract | `make hello-world`, future `make verify-examples` |
| Syntax model | `pyprompt/model.py` | `PromptFile`, `Agent`, `RoleScalar`, `RoleBlock`, `Workflow` | Shipped bootstrap AST model | Retain and extend the typed AST instead of introducing parallel verification-only structures | Keep parse, validation, and render responsibilities separate | Typed AST boundary for the bootstrap subset and future grammar growth | `make hello-world`, future `make verify-examples` |
| Parser boundary | `pyprompt/parser.py` | grammar loader, `Lark` constructor, transformer | Shipped bootstrap parser | Retain and extend the same parser boundary as the example corpus grows | Canonical parse owner path already exists and should stay singular | Parse current `01` source file as-authored and later shared-corpus cases through the same entrypoint | `make hello-world`, future `make verify-examples` |
| Compiler boundary | `pyprompt/compiler.py` | explicit agent selection + semantic validation | Shipped bootstrap compiler boundary | Retain and extend the same compiler boundary under the shared verifier | Avoid hidden first-agent behavior and keep unsupported constructs loud | `compile_prompt(..., agent_name)` or equivalent narrow boundary; missing or duplicate targets fail | `make hello-world`, future `make verify-examples` |
| Markdown render | `pyprompt/renderer.py` | Markdown emitter | Shipped bootstrap renderer | Retain and extend the same renderer boundary under shared verification | Renderer must keep owning Markdown shape explicitly instead of leaking expectations into test harness code | Selected agent -> Markdown string | `make hello-world`, future `make verify-examples` |
| Shared verification harness | `pyprompt/verify_corpus.py` | shared corpus runner | Missing | Add one reusable compiler verifier that loads adjacent manifests, validates schema, executes active cases, reports planned cases, and owns final pass/fail summary | Prevents `check_<example>` proliferation and centralizes compiler-test truth | One canonical verifier surface for `render_contract`, `parse_fail`, and `compile_fail` cases | `make hello-world`, `make verify-examples` |
| Retired bootstrap runner | `pyprompt/check_hello_world.py` | `main` | Shipped narrow bootstrap proof runner | Delete it once `verify_corpus` covers `examples/01_hello_world` | One canonical runtime path should own compiler verification | No separate checker logic remains for `01_hello_world` | `make hello-world`, `make verify-examples` |
| User commands | `Makefile` | `hello-world`, `verify-examples` | Only `hello-world` exists and it owns dedicated logic via `check_hello_world.py` | Rewire `hello-world` to a filtered `verify_corpus` manifest run and add `verify-examples` for the full active corpus | Keep the UX small while eliminating parallel verifier logic | `make hello-world` -> `python -m pyprompt.verify_corpus --manifest examples/01_hello_world/cases.toml`; `make verify-examples` -> `python -m pyprompt.verify_corpus` | `make hello-world`, `make verify-examples` |
| Source fixture | `examples/01_hello_world/prompts/AGENTS.prompt` | `HelloWorld`, `HelloWorld2` | Authoritative source contains both `role` shapes in one file | Keep as the first authoritative source fixture and require the parser to accept it as-authored | Avoid source slicing, duplicate fixtures, or drift between examples and implementation | Whole-file parse plus explicit target-agent selection | `make hello-world`, `make verify-examples` |
| Hello World contract | `examples/01_hello_world/cases.toml` | active render contracts | Missing | Add two active `render_contract` cases, one for `HelloWorld` and one for `HelloWorld2`, with exact line expectations in TOML | Moves verifier truth out of Python constants and covers both shipped role shapes | `schema_version = 1`, `default_prompt`, and two active exact-line cases | `make hello-world`, `make verify-examples` |
| Local negative fixtures | `examples/*/prompts/*.prompt` | per-case prompt override targets | No checked-in negative corpus owner path | Keep any future invalid inputs under the owning example directory and reference them by relative `prompt` override from `cases.toml` | Avoid a second fixture tree and avoid inventing an inline mutation DSL | Per-case `prompt` override stays example-local and path-bounded | Future `make verify-examples` |
| Approximate Hello World ref | `examples/01_hello_world/ref/AGENTS.md` | rendered Markdown | Manually built approximate output example for `HelloWorld` only | Keep as advisory output-shape evidence, not as an authoritative exact golden | Prevents the plan from treating manual examples as pristine truth while still using them to find bugs | A case may optionally carry `approx_ref`, which never decides pass/fail | `make hello-world`, `make verify-examples` |
| Sections contract | `examples/02_sections/cases.toml` | planned render contract | Missing | Add one planned `render_contract` for `SectionsDemo` with exact lines and optional advisory `approx_ref` | Seeds the first next-example output contract without pretending the current parser already supports it | `status = "planned"` until the grammar/renderer grow to support nested workflow entries | `make verify-examples` |
| Approximate sections ref | `examples/02_sections/ref/AGENTS.md` | rendered Markdown | Approximate manual output example only | Keep as advisory output-shape evidence for the planned contract | Preserves the current example surface without falsely upgrading it into executable truth | Optional `approx_ref`, advisory only | `make verify-examples` |
| Live doctrine docs | `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md`, `docs/COMPILER_ERRORS.md`, `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md` | language rules and known gaps | Docs-only truth today | Review and update as implementation lands if shipped behavior or resolved ambiguities differ | Avoid stale truth after code exists | Docs must match the shipped subset and the actual fail-loud behavior | Manual review |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - repo-root package `pyprompt/` plus repo-root `Makefile`, with `pyprompt.verify_corpus` as the durable verification owner
- Deprecated APIs (if any):
  - direct use of `python -m pyprompt.check_hello_world` once the shared verifier covers `01_hello_world`
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - `pyprompt/check_hello_world.py` after migration to `verify_corpus`
  - no `scripts/`-first bootstrap path
  - no duplicate fixtures under `tests/fixtures/`
  - no second grammar file for the same supported subset
  - no stand-alone parser artifact in the first pass
  - no inline source-mutation DSL inside `cases.toml`
- Capability-replacing harnesses to delete or justify:
  - any hand-written lexer
  - any custom indentation preprocessor
  - any bespoke CST-to-AST walker outside ordinary `Transformer` / `ast_utils` usage
  - any source-slicing helper that extracts only `HelloWorld` from the mixed file
  - any direct runtime import from `for_reference_only/lark`
  - any future per-example checker module once `verify_corpus` exists
- Live docs/comments/instructions to update or delete:
  - `docs/LANGUAGE_DESIGN_NOTES.md` if the first shipped subset clarifies the supported `role` shapes
  - `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md` if the shipped bootstrap subset hardens the exact `01` agent shape or render contract beyond its earlier scalar-only summary
  - `docs/COMPILER_ERRORS.md` if the first implementation earns concrete parse/compile failures that should be numbered
  - `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md` if the `01_hello_world` ambiguity is materially resolved by shipped architecture or the shared verifier changes how that ambiguity is described
- Behavior-preservation signals for refactors:
  - whole-file parse of `examples/01_hello_world/prompts/AGENTS.prompt`
  - existing green `make hello-world` before migrating it onto `verify_corpus`
  - post-migration green `make hello-world` running both active Hello World cases through the shared harness
  - green `make verify-examples` with active cases passing and planned cases reported separately
  - advisory diffs against approximate refs when useful for finding renderer/ref bugs
  - `strict=True` grammar construction with no silent fallback

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
|---|---|---|---|---|
| Live doctrine | `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md`, `docs/COMPILER_ERRORS.md` | Keep shipped subset and failure behavior aligned with the one canonical compiler path | Prevents docs from drifting ahead of the implemented grammar | include |
| First runtime fixtures | `examples/01_hello_world/prompts/AGENTS.prompt`, `examples/01_hello_world/ref/AGENTS.md`, `examples/02_sections/ref/AGENTS.md` | Treat `examples/` as the authoritative prompt corpus plus approximate rendered examples | Prevents source/ref truth from being silently inverted | include |
| Initial verifier seed | `examples/01_hello_world/cases.toml`, `examples/02_sections/cases.toml` | Start the shared harness with two active Hello World render contracts plus one planned headed-section contract | Gives the verifier a small but nontrivial starting corpus before later grammar pressure lands | include |
| Local negative fixtures | `examples/*/prompts/*.prompt` | Keep future invalid inputs beside their owning example and reference them via manifest path | Prevents a second fixture tree and avoids a verifier-side mutation DSL | include |
| Bootstrap verifier cleanup | `pyprompt/check_hello_world.py` | Delete the one-off checker once `verify_corpus` owns `01_hello_world` | Prevents legacy verifier drift and parallel logic | include |
| Next grammar pressure | `examples/02_sections/prompts/AGENTS.prompt` | Extend the same `pyprompt/` package and the same `pyprompt.lark` grammar file for keyed workflow entries | Prevents a second parser path when grammar scope grows | defer |
| Next grammar pressure | `examples/03_imports/prompts/AGENTS.prompt` and imported prompt files | Extend the same owner path for imports and symbol resolution | Prevents import behavior from being prototyped in side scripts | defer |
| Semantic growth | `examples/04_inheritance` through `examples/07_handoffs` | Add inheritance and routing semantics through the same AST/compiler path, not parallel prototypes | Prevents semantic drift and duplicated merge logic | defer |
| Declaration growth | `examples/08_inputs`, `examples/09_outputs`, `examples/10_turn_outcomes`, `examples/11_skills_and_tools` | Add new declarations and agent-side contract structure through the same package and grammar SSOT | Prevents declaration-specific side parsers and one-off side readers | defer |
| Output-pressure corpus | `examples/99_not_clean_but_useful` | Keep as rendering pressure only, not bootstrap grammar ownership | Prevents overbuilding the grammar too early | exclude |
| Alternative parser libs | `for_reference_only/LibCST`, `for_reference_only/pyparsing` | Do not reopen parser choice during bootstrap implementation | Prevents tool drift and parallel experiments | exclude |
| Duplicate test truth | `tests/fixtures/` or similar duplicate corpora | Do not create copied first-pass fixtures outside `examples/` | Prevents source/ref drift | exclude |
| Compiler verification growth | `pyprompt/verify_corpus.py`, `examples/*/cases.toml`, retained `Makefile` aliases only | Converge future compiler testing onto one reusable framework instead of per-example scripts | Prevents verification drift and maintenance blow-up as examples multiply | include |
<!-- arch_skill:block:call_site_audit:end -->

# 7) Depth-First Phased Implementation Plan (authoritative)

<!-- arch_skill:block:phase_plan:start -->
> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

Warn-first note:

- `external_research_grounding` and `deep_dive_pass_2` are now complete.
- The shared-verifier schema, command surface, and `02_sections` planned-contract boundary are now specific enough to implement directly.

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

Status: COMPLETE

Completed work:
- Researched compiler-test best practices from Rust `compiletest`, Rust UI/directive docs, LLVM’s testing guide, Tree-sitter’s parser corpus docs, and LLVM’s `LibFuzzer` guidance.
- Adopted one shared corpus-driven verifier as the next default architecture instead of more example-specific checker modules.
- Locked the follow-on verification shape to adjacent machine-readable case manifests, layered assertion styles, first-class negative cases, and deferred fuzzing as a complement rather than a substitute.
- Re-cut Sections 4, 5, 6, 7, and 8 so the plan names a concrete shared verification owner path.

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

## Phase 5 - Implement Shared Verification Harness

Status: NOT STARTED

* Goal:
  Replace the bootstrap-only Hello World checker as the primary testing pattern with one shared corpus-driven verification surface for the compiler.
* Work:
  Add `pyprompt/verify_corpus.py` as the canonical shared verifier.
  Load manifests through stdlib `tomllib` with a deliberately small schema: `schema_version`, `default_prompt`, and repeated `[[cases]]`.
  Support only the first required case kinds: `render_contract`, `parse_fail`, and `compile_fail`.
  Support only the first required success assertion mode: `assertion = "exact_lines"`.
  Add `examples/01_hello_world/cases.toml` with two active `render_contract` cases for `HelloWorld` and `HelloWorld2`.
  Add `examples/02_sections/cases.toml` with one planned `render_contract` for `SectionsDemo`, using exact lines as the first next-example output contract without pretending current parser support already exists.
  Add a repo-root `make verify-examples` target that runs the shared verifier across the example corpus.
  Rewire `make hello-world` to `python -m pyprompt.verify_corpus --manifest examples/01_hello_world/cases.toml` so it becomes a filtered alias over the shared verifier.
  Delete `pyprompt/check_hello_world.py` once the shared harness covers the same slice.
  Add first-class expected-failure cases for the shipped bootstrap boundaries by pointing cases at ordinary local prompt files under the owning example directory, not by inventing an inline mutation DSL.
* Verification (smallest signal):
  `make hello-world` runs both active Hello World cases through the shared harness and exits `0`.
  `make verify-examples` exits `0` with the Hello World cases green and `02_sections` reported as planned, not silently ignored.
  Negative cases fail at the expected stage with machine-checked failure contracts.
  `pyprompt/check_hello_world.py` is gone.
* Docs/comments (propagation; only if needed):
  Update the plan and any touched doctrine docs so the shared harness, case-manifest path, and truth surfaces are explicit.
* Exit criteria:
  The repo has one canonical reusable compiler verification owner path.
  The example corpus can grow without cloning checker logic.
  The Hello World bootstrap slice now runs only through the shared verifier plus a `Makefile` alias.
* Rollback:
  Keep the shipped bootstrap checker only long enough to recover from a bad migration, then either fix the shared harness or revert the migration cleanly; do not let that fallback become a reason to keep two verifier paths.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

Avoid verification bureaucracy. Prefer the smallest credible signal and keep the loop cheap enough to rerun often.

## 8.1 Unit tests (contracts)

Prefer at most one or two tight checks around AST construction or Markdown rendering if they materially shorten debugging once the grammar exists.

## 8.2 Integration tests (flows)

The primary shipped signal today is one end-to-end local command, `make hello-world`, that parses the supported source, compiles `HelloWorld`, and runs semantic smoke checks derived from the prompt/input contract. Diffs against checked `AGENTS.md` refs are advisory bug-finding signals, not byte-level truth.

That is bootstrap proof, not the final compiler-test architecture. The research-backed default is now one shared corpus verifier with adjacent case manifests and layered assertions, not a growing pile of example-specific checker modules.

## 8.3 E2E / device tests (realistic)

Not applicable beyond the local compiler loop. Do not add bespoke harnesses, editor automation, or other verification ceremony just to prove the first grammar works.

## 8.4 Compiler Verification Framework (next)

The next verification requirement is now concrete:

- the repo should converge on one shared verifier, `pyprompt/verify_corpus.py`, rather than more `check_<example>` modules
- machine-readable case manifests live adjacent to the example corpus as `examples/*/cases.toml`, loaded through stdlib `tomllib`
- the first shared-verifier seed set is now explicit:
  - `examples/01_hello_world/cases.toml` with two active exact-line `render_contract` cases
  - `examples/02_sections/cases.toml` with one planned exact-line `render_contract`
- the first manifest schema is intentionally small:
  - `schema_version`
  - `default_prompt`
  - repeated `[[cases]]`
  - `status = "active" | "planned"`
  - `kind = "render_contract" | "parse_fail" | "compile_fail"`
  - optional example-local `prompt`
  - optional advisory `approx_ref`
- exact rendered-output contracts are stored only where the repo deliberately stabilizes them in manifests; approximate `AGENTS.md` refs remain advisory
- expected-failure cases are first-class and should assert stable failure-stage contracts via `exception_type` plus `message_contains`
- `make hello-world` remains as a filtered alias over `verify_corpus`; it no longer owns separate checker logic
- fuzzing should be added only after the deterministic corpus harness exists, using the example corpus as seeds and feeding discovered failures back into deterministic regression cases

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

## 2026-04-06 - Adopt one shared corpus verifier for full-compiler testing

Context

External research across Rust `compiletest`, Rust UI/directive docs, LLVM’s testing guide, Tree-sitter’s parser corpus docs, and `LibFuzzer` showed a consistent pattern: serious compiler and parser projects centralize test execution in one harness, keep case expectations adjacent to inputs, support first-class negative cases, and avoid forcing every assertion into brittle whole-file goldens.

Options

- keep growing PyPrompt verification through one checker module per example
- adopt one shared corpus-driven verifier with adjacent machine-readable case manifests and layered assertion styles

Decision

Adopt one shared corpus-driven verifier as the canonical future compiler-test owner path, with adjacent case manifests under `examples/` and layered assertion modes for stable exact, normalized, targeted, and expected-failure checks.

Consequences

- `check_hello_world.py` is now explicitly a bootstrap slice, not the durable verification architecture.
- The next implementation phase should build `pyprompt/verify_corpus.py` and adjacent example-case manifests instead of more bespoke checker code.
- Approximate `AGENTS.md` refs remain advisory by default, while machine-readable case contracts become the primary future test truth.
- Fuzzing is useful later, but only after the deterministic corpus verifier exists.

Follow-ups

- Run a deep-dive pass to lock the shared verifier UX, case-manifest schema, and whether `make hello-world` survives as a filtered alias.
- Implement the shared verification harness in the next phase instead of widening the bootstrap checker pattern.

## 2026-04-06 - Seed the shared verifier with both Hello World renders plus `02_sections`

Context

The reusable verification architecture now has a concrete first-corpus question: which examples should seed the first adjacent case manifests so the shared harness starts small but not trivial.

Options

- seed only `HelloWorld`
- seed both `HelloWorld` render shapes from `01_hello_world`
- seed both `HelloWorld` render shapes and also add `02_sections` as the first post-bootstrap output manifest

Decision

Seed the first shared-verifier manifest set with `HelloWorld`, `HelloWorld2`, and `02_sections`.

Consequences

- The first shared harness will cover both current `role` render shapes immediately.
- The plan now has one concrete next-example manifest beyond Hello World instead of a vague future adopter.
- `02_sections` can be authored into the manifest set before its passing execution is required, which keeps verifier design and grammar growth loosely coupled without inventing duplicate truth.

Follow-ups

- Lock in the case-manifest schema during the next deep-dive pass.
- Decide in implementation whether `02_sections` turns green in the same phase as the shared verifier or remains the first queued adopter for the next grammar-expansion phase.

## 2026-04-06 - Lock the shared verifier on adjacent TOML manifests and filtered `Makefile` aliases

Context

External research established the need for one shared verifier, but the plan still had three unresolved implementation-shaping gaps: what the first manifest schema should be, whether `make hello-world` survives, and how `02_sections` can become machine-readable output truth now without pretending the current grammar already supports it.

Options

- keep the shared verifier generic in prose and defer schema plus command-surface choices until implementation
- lock a deliberately small first schema and command surface now, even if later examples may extend it

Decision

Lock the first shared verifier to adjacent `examples/*/cases.toml` manifests loaded through stdlib `tomllib`, keep `make hello-world` as a filtered alias over `pyprompt.verify_corpus`, delete `pyprompt/check_hello_world.py` once migrated, and allow `status = "planned"` cases for forward output contracts such as `02_sections`.

Consequences

- The implementation phase now has one concrete verifier schema instead of “figure it out while coding”.
- The durable verifier path is `pyprompt.verify_corpus`; any one-off checker logic is now explicitly temporary and slated for deletion.
- The first machine-readable output contracts are exact-line manifests for `HelloWorld`, `HelloWorld2`, and planned `SectionsDemo`, while approximate refs remain advisory only.
- Negative cases are expected to use ordinary local prompt files under the owning example directory rather than a custom mutation DSL.

Follow-ups

- Implement `examples/01_hello_world/cases.toml`, `examples/02_sections/cases.toml`, and `pyprompt/verify_corpus.py` directly against this schema.
- Extend assertion modes only when later examples prove the first `exact_lines` / `message_contains` boundary is insufficient.
