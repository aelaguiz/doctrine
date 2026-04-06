---
title: "PyPrompt - VS Code Language Highlighting - Architecture Plan"
date: 2026-04-06
status: complete
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - docs/SYNTAX_HIGHLIGHTING_RESEARCH.md
  - docs/VSCODE_REFERENCE.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/PORT_EXAMPLE_SYNTAX_THROUGH_PHASE_FOURTEEN_2026-04-06.md
  - pyprompt/grammars/pyprompt.lark
---

# TL;DR

- Outcome: Add a repo-local VS Code language extension so current `.prompt` files are no longer plain gray text, with usable syntax highlighting, comment/string treatment, and indentation-aware editor behavior for the shipped PyPrompt surface proved by the manifest-backed corpus in `examples/01_*` through `examples/14_*`.
- Problem: PyPrompt authoring is verified primarily through the Python parser/compiler path, so editor support has to stay tightly aligned with shipped grammar truth instead of drifting toward older draft notes, aspirational tooling, or unverified pressure surfaces.
- Approach: Build a static, contribution-only VS Code extension under `editors/vscode/`, backed by `language-configuration.json` plus a hand-authored TextMate grammar, and validate its keyword surface directly against `pyprompt/grammars/pyprompt.lark`; keep any unavoidable TextMate-only regex shaping narrow, documented, and tested against the verified `01` through `14` corpus.
- Plan: 1) scaffold the isolated `editors/vscode/` static extension and local debug loop, 2) implement the language configuration, TextMate grammar, and unit fixtures, 3) add Lark-alignment validation plus the mirrored snapshot corpus, and 4) finish local-use docs and cleanup.
- Non-negotiables: The shipped Lark grammar remains the language source of truth; the first shipped extension only covers the implemented manifest-backed `01` through `14` subset in this worktree; no parallel Langium or second parser stack is introduced for phase one; no fake indentation semantics are claimed beyond what TextMate and VS Code can actually support.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-06
Verdict (code): COMPLETE
Manual QA: pending (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Run the local GUI smoke check from `editors/vscode/README.md` in a real VS Code session and confirm representative files such as `examples/01_hello_world/prompts/AGENTS.prompt`, `examples/09_outputs/prompts/AGENTS.prompt`, and `examples/14_handoff_truth/prompts/AGENTS.prompt` show the expected highlighting, folding, and Enter behavior.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-06
external_research_grounding: done 2026-04-06
deep_dive_pass_2: done 2026-04-06
recommended_flow: complete (manual QA follow-up only)
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

We can add a repo-local VS Code language extension that gives verified PyPrompt files meaningful, stable highlighting and editor behavior for the shipped `01` through `14` syntax in this worktree without creating a second grammar source of truth or widening the language beyond what `pyprompt/` currently implements.

## 0.2 In scope

- A local VS Code extension checked into this repo for PyPrompt authoring.
- Language registration for current prompt files such as `*.prompt`.
- TextMate-based syntax highlighting for the shipped lexical surface:
  - declaration keywords such as `agent`, `abstract`, `workflow`, `import`
  - workflow operation keywords such as `use`, `inherit`, `override`
  - strings, `#` comments, inheritance brackets, dotted names, and header punctuation
  - authored keys and titled block headers where regex-based highlighting is reliable
- A VS Code `language-configuration.json` that gives correct comment behavior, indentation-sensitive folding defaults where applicable, and sensible Enter/indent behavior for colon-headed blocks.
- A narrow generation or validation path that reads `pyprompt/grammars/pyprompt.lark` and keeps the VS Code highlighting artifacts aligned with shipped keywords and lexical conventions.
- Automated tests or snapshots against verified example prompts from `01` through `14`.
- Local usage documentation so the extension can be launched or installed in local VS Code while the language evolves.

## 0.3 Out of scope

- Syntax support beyond the manifest-backed `examples/01_*` through `examples/14_*` corpus in this worktree.
- A second parsing stack such as Langium, ANTLR, Tree-sitter, or a custom LSP parser for phase one.
- Semantic tokens, diagnostics, completion, go-to-definition, rename, or formatter support in the first cut.
- Marketplace publishing, Open VSX publishing, or remote distribution concerns.
- Pretending TextMate can understand dedent-driven block structure with full parser accuracy.

## 0.4 Definition of done (acceptance evidence)

- Opening verified PyPrompt example files in local VS Code with the local extension enabled shows non-plaintext highlighting for the shipped syntax.
- The extension cleanly recognizes the current prompt files used in the repo.
- Automated scope or grammar tests cover representative `01` through `14` examples and catch drift in the highlighting surface.
- The extension has a documented local install or debug flow that is cheap enough to use continuously while the grammar evolves.
- If the implementation introduces any parser-side helper to expose lexical facts, `make verify-examples` remains the behavior-preservation check for shipped language support.

## 0.5 Key invariants (fix immediately if violated)

- No second language source of truth for the shipped syntax.
- No support claims beyond the verified `01` through `14` surface.
- No runtime fallback or silent divergence between the extension's keyword set and the shipped Lark grammar.
- No editor architecture that requires a full semantic stack before users stop seeing gray text.
- No repo changes that silently alter parse or compile behavior just to serve the editor layer.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Make current `.prompt` authoring readable in local VS Code immediately.
2. Keep `pyprompt/grammars/pyprompt.lark` as the authoritative lexical source whenever the mapping to editor artifacts is honest.
3. Keep maintenance cost low as the grammar continues to evolve beyond the current `01` through `14` surface.
4. Avoid shipping a second parser or language workbench before it is actually needed.

## 1.2 Constraints

- TextMate is VS Code's baseline tokenization layer, but it is line-oriented and cannot truly model dedent-based block structure.
- The shipped language implementation in this worktree currently proves `examples/01_hello_world` through `examples/14_handoff_truth`.
- The extension must be useful locally without marketplace publishing or a separate service deployment.
- The user explicitly wants tight integration with the existing Lark grammar and current shipped compiler path.
- The repo has no existing Node or editor-tooling package surface, so any JavaScript tooling introduced for VS Code support must stay isolated under the extension subtree instead of spreading to repo root.

## 1.3 Architectural principles (rules we will enforce)

- Prefer one lexical truth surface, with derived editor artifacts.
- Keep the first extension static and local unless real highlighting gaps force richer runtime behavior.
- Fail loudly on grammar drift instead of silently letting the extension go stale.
- Treat later draft syntax as design pressure, not live highlighting scope.

## 1.4 Known tradeoffs (explicit)

- A TextMate-first extension will give immediate value but cannot perfectly express indentation-scoped semantics.
- Some VS Code grammar structure will still need curated regex rules even if the keyword inventory is derived from Lark.
- Deferring semantic tokens and a formatter keeps phase one small, but it also means some future editor accuracy work will remain.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

PyPrompt has a shipped parser/compiler/rendering path in `pyprompt/` backed by a Lark grammar and verified example manifests through `14` in this worktree. The repo now also contains a repo-local VS Code extension under `editors/vscode/`, plus the supporting grammar tests and alignment validator that landed in this run.

## 2.2 What’s broken / missing (concrete)

- Before this change, `.prompt` files were effectively plain text in local VS Code.
- Before this change, there was no language registration, syntax grammar, or editor configuration for the current DSL.
- The repo's research and older planning notes still create pressure for richer tooling, but they should not quietly override the shipped Lark grammar as the editor contract.
- The fastest full-IDE option in the research, Langium, would still introduce a second grammar stack that conflicts with the user's stated integration goal, so it remains out of scope for this first cut.

## 2.3 Constraints implied by the problem

- The first solution must deliver value without requiring a second parser implementation.
- The extension must stay anchored to the shipped subset rather than aspirational syntax.
- The path should be iterative so the highlighting surface can evolve as new grammar features become real.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- `docs/SYNTAX_HIGHLIGHTING_RESEARCH.md` — adopt the TextMate-first layering facts, reject its Langium-first recommendation for phase one — the doc is right that TextMate is the baseline and ceiling for regex tokenization, semantic tokens are additive, and indentation-sensitive languages usually need stronger tooling later; it is not aligned with this plan's explicit "no second grammar stack" invariant.
- `docs/VSCODE_REFERENCE.md` — adopt the VS Code contribution and tokenization model, keep the deeper LSP internals as later-phase reference only — it grounds how `contributes.languages`, `contributes.grammars`, `language-configuration.json`, TextMate tokenization, and semantic token overlays actually fit together.
- `for_reference_only/vscode-extension-samples/language-configuration-sample/package.json`, `for_reference_only/vscode-extension-samples/language-configuration-sample/language-configuration.json`, and `for_reference_only/vscode-extension-samples/language-configuration-sample/.vscode/launch.json` — adopt as the minimal local extension scaffold shape — this is the smallest honest package layout for a repo-local language extension with no runtime code, no `main`, and no `activationEvents`.
- `for_reference_only/vscode/extensions/coffeescript/package.json` and `for_reference_only/vscode/extensions/coffeescript/language-configuration.json` — adopt as a built-in precedent for a mostly declarative indentation-sensitive language surface — it shows that a built-in language can rely on `contributes.languages`, `contributes.grammars`, and `folding.offSide: true` without an LSP.
- `for_reference_only/vscode/extensions/pug/package.json` and `for_reference_only/vscode/extensions/pug/language-configuration.json` — adopt as a second off-side language reference, especially for folding defaults and trim-whitespace behavior — this is the closest built-in shape to a purely indentation-driven authoring experience.
- `for_reference_only/vscode/extensions/python/language-configuration.json` — adopt selectively for `onEnterRules` on colon-headed block starters, reject any assumption that this implies parser-accurate structure — it is the strongest built-in proof that VS Code's language configuration can improve block authoring ergonomics for off-side languages without solving semantic structure.
- `for_reference_only/vscode-textmate/README.md` and `for_reference_only/vscode-textmate/src/main.ts` — adopt for the execution model of grammar loading and tokenization in tests, not as a new language source of truth — this is the same engine VS Code uses to load a scope name and tokenize line-by-line.
- `for_reference_only/vscode-tmgrammar-test/README.md` — adopt as the first automated grammar test harness — it already knows how to consume an extension-style `package.json`, run TextMate scope assertions, and keep snapshot baselines cheap.
- `for_reference_only/vscode-tmgrammar-test/package.json` — adopt as proof that phase-one grammar testing can stay npm-only and does not require a VS Code runtime harness.
- `for_reference_only/vscode-extension-samples/semantic-tokens-sample/src/extension.ts` and `for_reference_only/vscode-languageserver-node/client/src/common/semanticTokens.ts` — reject for phase one, keep as phase-two anchors only — they are the right references if TextMate reaches a real ceiling later, but they add runtime code and a second moving part before the repo even has baseline highlighting.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `pyprompt/grammars/pyprompt.lark` — the shipped syntax owner for current literals, punctuation, indentation/newline handling, comments, and the actual `01` through `14` declaration surface.
  - `pyprompt/parser.py` — the parser entrypoint that proves the Lark grammar is not just design intent but live runtime behavior.
  - `pyprompt/model.py` — the shipped AST surface, which keeps the extension scope honest about what constructs are real today.
  - `pyprompt/compiler.py` — the live compile-time contract that proves only the current subset is implemented and prevents the editor plan from quietly adopting later draft syntax.
  - `pyprompt/renderer.py` — the current output shape, useful when deciding which authored constructs deserve visual distinction in the editor.
  - `pyprompt/verify_corpus.py` — the current acceptance loop and the clearest existing preservation signal for shipped syntax behavior.
  - `examples/01_hello_world/cases.toml` through `examples/14_handoff_truth/cases.toml` — the verified prompt corpus that can honestly anchor phase-one highlighting coverage claims in this worktree.
  - `docs/LANGUAGE_DESIGN_NOTES.md` — design pressure and future direction, useful context but subordinate to shipped behavior.
  - `docs/PORT_EXAMPLE_SYNTAX_THROUGH_PHASE_FOURTEEN_2026-04-06.md` — keep as historical planning context only; the current April 6, 2026 baseline now proves `07` through `14`, so this doc is no longer current syntax truth.
- Canonical path / owner to reuse:
  - `pyprompt/grammars/pyprompt.lark` — owns the keyword inventory, declaration literals, bracket punctuation, and comment/newline conventions that any extension derivation or validation path must reuse.
  - `pyprompt/verify_corpus.py` plus `examples/01_hello_world/cases.toml` through `examples/14_handoff_truth/cases.toml` — own the current behavior boundary and therefore the maximum highlighting support we can claim in phase one.
- Existing patterns to reuse:
  - `pyprompt/grammars/pyprompt.lark` — literal-keyword grammar style — the current grammar spells keywords directly as string literals (`"agent"`, `"workflow"`, `"use"`, `"inherit"`, `"override"`), which makes lexical extraction or validation tractable without inventing a second syntax file.
  - `pyprompt/grammars/pyprompt.lark` — `_NL` owns newline, indentation whitespace, and standalone `#` comment lines — this is the critical reason the highlighter should treat `#` comments and colon-headed block starts as first-class lexical surfaces.
  - `for_reference_only/vscode-extension-samples/language-configuration-sample` — declarative extension package shape — reuse this before inventing runtime activation code.
  - `for_reference_only/vscode/extensions/coffeescript/language-configuration.json`, `for_reference_only/vscode/extensions/pug/language-configuration.json`, and `for_reference_only/vscode/extensions/python/language-configuration.json` — off-side editor behavior patterns — reuse `comments`, `folding.offSide`, and narrowly targeted `onEnterRules` instead of overengineering indentation handling.
  - `for_reference_only/vscode-tmgrammar-test/README.md` — package-driven grammar tests — reuse this before writing a custom scope snapshot harness.
  - `for_reference_only/vscode-textmate/README.md` — direct registry/tokenization flow — useful if we need one narrow lower-level test around generated or validated grammar artifacts.
- Prompt surfaces / agent contract to reuse:
  - `AGENTS.md` — the repo-level contract says to trust `pyprompt/` over aspirational examples, so its example-scope notes must be kept aligned with the actual verified corpus.
  - `docs/PYPROMPT_VSCODE_LANGUAGE_HIGHLIGHTING_PLAN_2026-04-06.md` Sections `TL;DR` and `0)` — the confirmed North Star rejects a second grammar stack and caps phase one at local VS Code highlighting for the actual shipped syntax in this worktree.
- Native model or agent capabilities to lean on:
  - `VS Code language contributions` — declarative `contributes.languages`, `contributes.grammars`, and `language-configuration.json` can solve the user's immediate gray-text problem without an LSP, semantic token provider, or custom parser runtime.
  - `VS Code TextMate engine` — the editor already knows how to load a TextMate grammar and apply scopes line-by-line, so phase one only needs correct artifacts, not a bespoke tokenization engine.
- Existing grounding / tool / file exposure:
  - `docs/SYNTAX_HIGHLIGHTING_RESEARCH.md` and `docs/VSCODE_REFERENCE.md` — repo-local research already covering the design space and VS Code internals.
  - `for_reference_only/README.md` — the manifest of checked-out upstream references and versions, which keeps the plan's external grounding reproducible.
  - `for_reference_only/vscode-textmate`, `for_reference_only/vscode-oniguruma`, `for_reference_only/vscode-tmgrammar-test`, `for_reference_only/vscode-extension-samples`, `for_reference_only/vscode-languageserver-node`, and sparse `for_reference_only/vscode/extensions/*` — local code references for implementation and test-shape decisions.
- Duplicate or drifting paths relevant to this change:
  - older docs or notes that still describe `07` through `14` as future syntax — these are now stale planning artifacts, and letting them define scope would create drift between the plan narrative and the code the repo actually proves today.
  - `docs/SYNTAX_HIGHLIGHTING_RESEARCH.md` — valuable background, but its formatter and Langium emphasis is intentionally broader than the confirmed phase-one scope.
  - any future handwritten keyword list inside a VS Code subtree — this would become a drift source immediately unless it is derived from or validated against `pyprompt/grammars/pyprompt.lark`.
- Capability-first opportunities before new tooling:
  - declarative extension contributions plus a TextMate grammar — enough to eliminate plain-gray editing now.
  - a narrow Lark-derived keyword extractor or validator — enough to keep the grammar honest without adopting Langium, Tree-sitter, or a second parser.
  - `vscode-tmgrammar-test` against representative `examples/01_*` through `examples/14_*` prompt sources — enough to catch scope drift before inventing a custom test runner.
- Behavior-preservation signals already available:
  - `make verify-examples` — the repo's existing top-level preservation check for shipped syntax behavior.
  - `uv run --locked python -m pyprompt.verify_corpus --manifest examples/01_hello_world/cases.toml` — the smallest targeted shipped-syntax proof path.
  - `examples/01_hello_world/cases.toml` through `examples/14_handoff_truth/cases.toml` — the current manifest-backed corpus that should seed highlighting fixtures and snapshots.

## 3.3 Open questions (evidence-based)

- How broad should the first `onEnterRules` set be for colon-headed blocks? — settle this by mapping the verified `01` through `14` prompt corpus to the exact header shapes we need to support on day one.
- Is the unpacked local-install path cheap enough for daily use, or will the user immediately need optional `.vsix` packaging as follow-up? — settle this by trying the documented local-use loop once phase one exists.
- Does direct validation against `pyprompt/grammars/pyprompt.lark` stay stable enough in practice, or do we eventually need a parser-adjacent helper in `pyprompt/parser.py`? — settle this only if implementation shows the direct-grammar validator becoming brittle or too implicit.
- Does the mirrored snapshot tree need a tiny sync helper once it exists, or is straightforward manual refresh still cheap enough? — settle this only if keeping `editors/vscode/tests/snap/examples/**` aligned with verified examples becomes annoying in practice.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `pyprompt/` is the only shipped implementation surface. The real current behavior lives in:
  - `pyprompt/grammars/pyprompt.lark`
  - `pyprompt/indenter.py`
  - `pyprompt/parser.py`
  - `pyprompt/model.py`
  - `pyprompt/compiler.py`
  - `pyprompt/renderer.py`
  - `pyprompt/verify_corpus.py`
- `examples/01_*` through `examples/14_*` are manifest-backed prompt inputs today. Each active example has `cases.toml`, prompt sources under `prompts/`, and reference output under `ref/`.
- `examples/99_not_clean_but_useful/` remains design pressure only and does not define shipped syntax.
- `docs/` already contains the plan and the syntax-highlighting research, and `for_reference_only/` now contains the checked-out upstream references.
- The landed implementation adds one repo-local editor subtree at `editors/vscode/` with its own `package.json`, `package-lock.json`, grammar/config files, tests, and README.
- The repo still has no root-level Node package surface. The new npm tooling remains isolated under `editors/vscode/`.

## 4.2 Control paths (runtime)

- Source parsing is strict and grammar-driven:
  - `build_lark_parser()` in `pyprompt/parser.py` loads `pyprompt/grammars/pyprompt.lark` once with `parser="lalr"`, `lexer="contextual"`, `strict=True`, and `PyPromptIndenter()`.
  - `parse_text()` transforms the parse tree through `ToAst`.
  - `parse_file()` resolves a prompt path, reads the file, and attaches `source_path`.
- Compilation is downstream of parsing:
  - `compile_prompt()` in `pyprompt/compiler.py` creates `CompilationContext`.
  - `CompilationContext` indexes declarations and imports, resolves workflow reuse and inheritance, enforces agent field order, and fails loudly on subset violations.
  - Import resolution and prompt-root discovery happen inside compiler code, not parser code.
- Rendering is markdown-only:
  - `render_markdown()` in `pyprompt/renderer.py` renders compiled sections and headings, not raw source syntax.
- Verification is manifest-driven:
  - `verify_corpus()` in `pyprompt/verify_corpus.py` discovers `examples/*/cases.toml`.
  - Each manifest provides `default_prompt` plus case kinds such as `render_contract`, `parse_fail`, and `compile_fail`.
- Editor integration is static and declarative:
  - VS Code reads `editors/vscode/package.json`, `language-configuration.json`, and `syntaxes/pyprompt.tmLanguage.json`.
  - Grammar tests run under `editors/vscode/` through `vscode-tmgrammar-test`.
  - Lark alignment checks run through `editors/vscode/scripts/validate_lark_alignment.py`.

## 4.3 Object model + key abstractions

- The only shipped syntax truth is `pyprompt/grammars/pyprompt.lark`.
  - Top-level declarations: `import`, `workflow`, `input source`, `input`, `output target`, `output shape`, `output`, `json schema`, `skill`, `agent`, and `abstract agent`
  - Agent fields: `role`, `inputs`, `outputs`, `outcome`, `skills`, authored slot fields, `inherit`, and `override`
  - Workflow and record items: local section keys, record keys, `use`, `inherit`, `override`, standalone references, and `route`
  - Lexical atoms: `CNAME`, `ESCAPED_STRING`, dotted names, relative-import dots, `:` and `[` / `]`
- Indentation semantics are handled by `PyPromptIndenter` in `pyprompt/indenter.py`. There is no side preprocessor and no separate whitespace normalizer.
- Standalone `#` comments are accepted lexically through `_NL` in the grammar, not as dedicated AST nodes.
- The AST in `pyprompt/model.py` is intentionally semantic and therefore lossy for editor purposes:
  - it preserves declarations, workflow items, titles, and strings
  - it does not preserve comment nodes, raw punctuation, or all lexical distinctions needed for highlighting
- The compiler and renderer operate on semantic structure, not lexical structure, so they are the wrong owner for editor-token decisions.

## 4.4 Observability + failure behavior today

- The strongest existing preservation signal is manifest-backed verification in `pyprompt/verify_corpus.py`.
- Current failure behavior is already fail-loud:
  - parse-stage failures surface as parser exceptions against invalid prompt files
  - compile-stage failures surface as `CompileError`
  - strict grammar loading means syntax drift should fail quickly once checks are run
- The strongest existing editor-facing signals are now:
  - `uv run --locked python editors/vscode/scripts/validate_lark_alignment.py`
  - `npm test` under `editors/vscode/`
  - `make verify-examples`
- Manual GUI verification is still intentionally lightweight and non-blocking:
  - local VS Code or Extension Development Host smoke checks remain the final human confirmation path
  - the README documents that flow instead of requiring a heavier editor automation stack

## 4.5 UI surfaces (ASCII mockups, if UI work)

- Current state in a normal VS Code window with the local extension enabled:

```text
AGENTS.prompt
--------------------------------
PyPrompt language association active
# comments dimmed as comments
agent / workflow / route / output highlighted
"titles" and prose strings distinguished
prompt files fold by indentation
Enter after block headers indents sensibly
--------------------------------
```
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

The phase-one editor surface lives in one new repo-local subtree: `editors/vscode/`.

That subtree should be a static, contribution-only VS Code extension with these owned files:

- `editors/vscode/package.json`
  - declares the PyPrompt language id, `.prompt` associations, grammar contribution, configuration path, and npm-based test scripts
  - does not define a runtime `main` entry or `activationEvents` in phase one
- `editors/vscode/package-lock.json`
  - locks the isolated npm dependency surface for the extension only
- `editors/vscode/language-configuration.json`
  - owns comments, bracket and quote pairs, off-side folding, and narrowly targeted `onEnterRules`
- `editors/vscode/syntaxes/pyprompt.tmLanguage.json`
  - owns TextMate scopes for the shipped `01` through `14` lexical surface
- `editors/vscode/scripts/validate_lark_alignment.py`
  - reads `pyprompt/grammars/pyprompt.lark` directly and validates that the extension keyword inventory and lexical assumptions still match shipped syntax truth
- `editors/vscode/tests/unit/`
  - focused inline scope assertions for specific lexical cases and edge conditions
- `editors/vscode/tests/snap/examples/**/prompts/**/*.prompt`
  - mirrored snapshot fixtures for every verified `.prompt` file under `examples/01_*` through `examples/14_*`
  - adjacent `.snap` files live here because `vscode-tmgrammar-snap` writes snapshots beside its inputs
- `editors/vscode/.vscode/launch.json`
  - enables rapid local iteration in an Extension Development Host
- `editors/vscode/README.md`
  - documents the local debug loop and the normal local-install loop for daily use

The verified prompt corpus remains where it already lives under `examples/01_*` through `examples/14_*`. Unit coverage should anchor itself to that shipped corpus directly wherever the tool allows it. Snapshot coverage should mirror every verified `.prompt` file into `editors/vscode/tests/snap/examples/**` because `vscode-tmgrammar-snap` writes adjacent `.snap` files and we do not want those artifacts inside the canonical example directories. This duplication is deliberate and narrow: the examples stay the truth, and the snapshot tree stays an editor-test artifact.

## 5.2 Control paths (future)

- `pyprompt/grammars/pyprompt.lark` remains the only syntax source of truth.
- The VS Code extension remains static and declarative in phase one:
  - VS Code reads `editors/vscode/package.json`
  - registers the PyPrompt language id for `*.prompt`
  - loads `language-configuration.json`
  - loads `syntaxes/pyprompt.tmLanguage.json`
  - applies TextMate tokenization and language-configuration behavior with no runtime extension code
- The local editor/dev flow stays split cleanly:
  - opening an Extension Development Host requires only the static extension files and `.vscode/launch.json`
  - grammar testing uses isolated npm tooling under `editors/vscode/`
  - Lark alignment validation uses the repo's Python toolchain
- Lark alignment is validation-first, not generation-first:
  - the TextMate grammar is hand-authored because its regex structure does not map honestly from Lark rules one-to-one
  - `validate_lark_alignment.py` reads `pyprompt/grammars/pyprompt.lark` directly and fails if the extension's keyword inventory or lexical assumptions drift from shipped syntax
  - parser/compiler behavior stays untouched unless later evidence shows direct grammar validation is too brittle
- The editor test flow is likewise layered:
  - `npm test` under `editors/vscode/` should run grammar tests only
  - `vscode-tmgrammar-test` runs focused unit assertions against the extension package
  - `vscode-tmgrammar-snap` runs against the mirrored tree under `editors/vscode/tests/snap/examples/**`, not the live `examples/` tree
  - final manual validation uses either Extension Development Host or an unpacked local install in the user's normal VS Code
- `.vsix` packaging is not part of the phase-one control path.

## 5.3 Object model + abstractions (future)

- Canonical syntax owner:
  - `pyprompt/grammars/pyprompt.lark`
- Canonical editor owner:
  - `editors/vscode/`
- The derived editor surface has three layers:
  - `language-configuration.json` for comments, folding, pairs, and Enter behavior
  - a hand-authored TextMate grammar for scopes
  - a Python validator that checks those extension-side lexical facts against the Lark grammar
- The extension package itself is intentionally tiny:
  - static contribution files
  - isolated npm metadata and lockfile
  - no runtime JS or TS entrypoint
- The editor grammar should explicitly cover the shipped lexical surfaces that actually appear in `01` through `14`:
  - declaration keywords such as `import`, `agent`, `abstract`, `workflow`, `input`, `output`, `json`, and `skill`
  - field and workflow-item keywords such as `role`, `inputs`, `outputs`, `outcome`, `skills`, `use`, `inherit`, `override`, and `route`
  - bracketed inheritance headers
  - dotted import and workflow-target paths
  - local workflow keys and record keys before `:`
  - escaped double-quoted strings
  - standalone `#` comments
- The AST and compiler are intentionally not part of the phase-one highlighting contract because they no longer carry all lexical detail.
- Semantic tokens, diagnostics, completion, formatting, and LSP plumbing remain later-phase options only if the static TextMate-first design proves insufficient.

## 5.4 Invariants and boundaries

- `pyprompt/grammars/pyprompt.lark` stays the only syntax source of truth.
- `editors/vscode/` owns editor presentation only and must not become a parallel parser or language-definition stack.
- Validation is the bridge in phase one; code generation is not the default.
- No runtime `extension.js`, `extension.ts`, semantic-token provider, or language server is introduced in phase one.
- No root-level Node toolchain or package-manager surface is introduced; npm, if used, lives only under `editors/vscode/`.
- No support is claimed beyond the manifest-backed `01` through `14` subset.
- No checked-in keyword mirror, generated parser mirror, or second grammar file is allowed to drift independently of `pyprompt.lark`.
- No top-level `vscode/` extension subtree should be introduced; `editors/vscode/` is the canonical editor home and avoids ambiguity with `for_reference_only/vscode`.
- No `.vsix` artifact is required for phase one and no packaged binary artifact should become the repo's primary local-usage path.

## 5.5 UI surfaces (ASCII mockups, if UI work)

- Target state in local VS Code:

```text
AGENTS.prompt
--------------------------------
# comments dimmed as comments
agent / workflow / use highlighted
"titles" and prose strings distinguished
section keys and dotted targets separated
prompt files fold by indentation
Enter after a block header indents sensibly
--------------------------------
```
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Syntax truth | `pyprompt/grammars/pyprompt.lark` | grammar literals, `_NL`, declaration and workflow rules | authoritative shipped grammar only | keep unchanged as the single syntax owner; let editor validation read it directly | avoid a second grammar stack | Lark file is SSOT for editor keyword alignment too | extension alignment validator; existing corpus if grammar is ever touched |
| Parser boundary | `pyprompt/parser.py` | `build_lark_parser()`, `parse_text()`, `parse_file()` | strict parse entrypoint and AST transform | no phase-one change by default; only touch if direct grammar validation later proves insufficient | keep editor concerns out of runtime parse path unless necessary | parser remains runtime-only in phase one | `make verify-examples` if later touched |
| AST boundary | `pyprompt/model.py` | dataclasses such as `PromptFile`, `Agent`, `WorkflowBody` | semantic AST loses comments and raw punctuation | do not use as a highlight source | AST is too lossy for lexical truth | editor pipeline bypasses AST for lexical alignment | none |
| Compiler boundary | `pyprompt/compiler.py` | `CompilationContext`, `compile_prompt()` | resolves imports, inheritance, and field ordering for shipped subset | no phase-one change | highlighting does not need compiled semantics and compiler changes add regression risk | compiler remains out of editor path | `make verify-examples` if later touched |
| Verification boundary | `pyprompt/verify_corpus.py` | `verify_corpus()`, `_resolve_manifest_paths()` | manifest-backed proof surface for `examples/*/cases.toml` | reuse as the shipped-scope boundary for highlight support claims | cap scope at what the repo actually proves today | editor coverage is anchored to manifest-backed `01` through `14` only | targeted manifests and full corpus |
| Extension home | `editors/vscode/package.json` | language id, `contributes.languages`, `contributes.grammars`, npm scripts | missing | add the static extension manifest and local test scripts with no `main` or `activationEvents` | register `.prompt` files and own editor-facing packaging without runtime code | repo-local contribution-only extension contract | package-level grammar tests |
| Node tooling isolation | `editors/vscode/package-lock.json` | isolated npm lockfile | missing | add a subtree-local lockfile instead of any repo-root Node tooling | keep the new JS surface narrow and isolated | extension subtree owns npm state | npm-based grammar test reproducibility |
| Repo hygiene | `.gitignore` | `/editors/vscode/node_modules/` | root ignore list does not cover the new extension-owned npm install output | add a subtree-specific ignore for extension `node_modules/` | keep the isolated npm surface out of git while avoiding a repo-root Node policy shift | only the editor subtree's install output is ignored | none |
| Language configuration | `editors/vscode/language-configuration.json` | comments, pairs, folding, `onEnterRules` | missing | add `#` line comments, quote/bracket pairs, `folding.offSide`, and narrow block-header Enter rules | make authoring workable before richer tooling exists | editor mechanics live here, not in runtime code | manual VS Code validation; maybe unit fixtures for tricky block headers |
| TextMate scopes | `editors/vscode/syntaxes/pyprompt.tmLanguage.json` | scope rules for comments, strings, keywords, keys, targets | missing | add a hand-authored TextMate grammar for the shipped lexical subset | solve the gray-text problem now | static grammar is derived presentation, not syntax truth | `vscode-tmgrammar-test` unit and snapshot coverage |
| Lark alignment | `editors/vscode/scripts/validate_lark_alignment.py` | direct read of `pyprompt/grammars/pyprompt.lark` | missing | add a Python validator that checks extension keyword and lexical assumptions against Lark | fail loudly on drift without generating a second grammar | validation-first alignment contract | validator run plus grammar tests |
| Unit grammar tests | `editors/vscode/tests/unit/` | inline assertion fixtures for lexical edges | missing | add focused `.test.prompt` cases for comments, strings, keywords, keys, imports, and invalid-but-lexically-interesting snippets | catch scope regressions cheaply without runtime harnesses | unit fixtures own assertion syntax | `vscode-tmgrammar-test` |
| Snapshot grammar tests | `editors/vscode/tests/snap/examples/**/prompts/**/*.prompt` | mirrored verified prompt corpus with adjacent `.snap` outputs | missing | mirror every verified `.prompt` file from `examples/01_*` through `examples/14_*` into a test-owned tree | keep `examples/` clean while still getting broad grammar regression coverage, including nested import fixtures and split-by-concern prompt files | mirrored snapshot fixtures must cite their source example path and stay editor-test-only | `vscode-tmgrammar-snap` |
| Local usage docs | `editors/vscode/README.md` and `editors/vscode/.vscode/launch.json` | local install/debug workflow | missing | document Extension Development Host and unpacked local install for everyday VS Code use | the user wants immediate local usability, not just implementation | one cheap local debug loop and one cheap local use path | manual local extension smoke check |
| Repo instructions | `AGENTS.md` | first actions and shipped-scope notes | stale `01` through `06` guidance | update the repo instruction surface to the actual manifest-backed `01` through `14` baseline in this worktree | keep live instructions aligned with shipped code and active manifests | AGENTS tracks the current verified corpus boundary | `make verify-examples` |
| Packaging follow-up | `editors/vscode/package.json` | optional packaging scripts | missing | defer `.vsix` packaging and `vsce` integration out of phase one | not required to stop gray text and adds extra tooling surface | packaging is follow-up work, not a first-cut dependency | none in phase one |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `pyprompt/grammars/pyprompt.lark` owns syntax truth.
  - `editors/vscode/` owns editor presentation and test tooling.
  - `editors/vscode/scripts/validate_lark_alignment.py` is the only allowed bridge for phase-one lexical alignment.
  - `editors/vscode/package-lock.json` owns the isolated npm dependency graph if Node tooling is added.
- Deprecated APIs (if any):
  - none
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - do not leave a second checked-in keyword list or generated grammar mirror outside `editors/vscode/`
  - do not introduce a competing top-level `vscode/` subtree for the live extension
  - do not introduce a repo-root `package.json`, lockfile, or TS build surface just to support this static extension
  - delete any temporary scratch grammar files or ad hoc keyword snapshots created during implementation before the phase closes
- Capability-replacing harnesses to delete or justify:
  - `vscode-languageclient`, `vscode-languageserver-node`, semantic-token runtime code, Langium, Tree-sitter, or `@vscode/test-electron` are all out of phase one unless later evidence proves the static path insufficient
- Live docs/comments/instructions to update or delete:
  - add `editors/vscode/README.md` as the local usage source of truth
  - update `AGENTS.md` when the manifest-backed shipped corpus changes, so the repo instructions stay aligned with `make verify-examples`
  - keep this plan doc current as the canonical architecture record
  - each mirrored snapshot fixture should record its source example path so the duplicate remains auditable
  - keep `.gitignore` aligned with the isolated `editors/vscode/` npm install surface
  - no existing live product doc currently needs deletion because editor support does not exist yet
- Behavior-preservation signals for refactors:
  - `make verify-examples`
  - `uv run --locked python -m pyprompt.verify_corpus --manifest examples/01_hello_world/cases.toml`
  - `vscode-tmgrammar-test` unit assertions and snapshots against representative `01` through `14` prompts

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Editor home | `editors/vscode/` | one canonical VS Code subtree instead of scattered files | prevents editor-tooling drift and avoids ambiguity with `for_reference_only/vscode` | include |
| Node tooling | `editors/vscode/package.json` and `editors/vscode/package-lock.json` | keep npm isolated under the extension subtree | prevents accidental repo-root JS tooling spread | include |
| Unit fixtures | `editors/vscode/tests/unit/` | keep lexical edge cases local to the extension package | avoids overloading canonical examples with inline test syntax | include |
| Snapshot fixtures | `editors/vscode/tests/snap/examples/**` | mirror the verified prompt corpus into a test-owned tree | prevents `.snap` files from polluting `examples/` while preserving broad grammar coverage, including nested import files | include |
| Snapshot sync helper | `editors/vscode/scripts/` | add only if mirror maintenance becomes annoying | avoids speculative tooling before the sync burden is real | defer |
| Legacy pressure examples | `examples/99_not_clean_but_useful/` | keep out of phase-one snapshot and support claims | prevents the extension from inheriting old markdown sprawl as shipped syntax | exclude |
| Lark bridge | `editors/vscode/scripts/validate_lark_alignment.py` | validation-first direct grammar read | prevents codegen theater and keeps `pyprompt.lark` as SSOT | include |
| Parser helper | `pyprompt/parser.py` | parser-adjacent lexical helper if direct validation proves too brittle | keeps a future escalation path without forcing runtime changes now | defer |
| Runtime extension code | `extension.ts` / semantic-token provider / LSP client | add runtime code only if static TextMate proves insufficient | avoids parallel behavior stacks before the baseline works | exclude |
| Packaging | `.vsix` / `vsce` scripts | add packaging only if the unpacked local-install path is not cheap enough | avoids nonessential tooling scope in phase one | defer |
| E2E editor tests | `@vscode/test-electron` style harness | add only if TextMate tests and manual smoke checks miss real regressions | avoids heavyweight test machinery too early | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Static Extension Scaffold

Status: COMPLETE

* Goal:
  Establish the smallest valid `editors/vscode/` extension home so VS Code can recognize `.prompt` files without introducing runtime code or repo-root Node tooling.
* Work:
  - Create `editors/vscode/package.json` with the PyPrompt language id, `.prompt` file association, `contributes.languages`, `contributes.grammars`, configuration path, and grammar-test scripts.
  - Keep the package contribution-only: no `main`, no `activationEvents`, no `extension.ts`, and no TypeScript build chain.
  - Create `editors/vscode/package-lock.json` by installing only the phase-one npm dependency surface inside the extension subtree.
  - Add `editors/vscode/.vscode/launch.json` for Extension Development Host.
  - Add seed `editors/vscode/language-configuration.json` and seed `editors/vscode/syntaxes/pyprompt.tmLanguage.json` so the extension loads cleanly even before the final grammar exists.
  - Start `editors/vscode/README.md` with the local debug-loop contract.
* Verification (smallest signal):
  - Open the extension in an Extension Development Host and confirm that `*.prompt` files associate to the PyPrompt language id.
  - Confirm no repo-root `package.json`, lockfile, or TS build surface was introduced.
* Docs/comments (propagation; only if needed):
  - Seed `editors/vscode/README.md` with the extension-host workflow so the subtree is self-describing from day one.
* Exit criteria:
  - `editors/vscode/` exists as the canonical extension home.
  - VS Code can load the static extension package.
  - `.prompt` files are recognized as PyPrompt in the development host.
* Rollback:
  - Remove the entire `editors/vscode/` subtree and its isolated npm lockfile.
Completed work:
  - Added the static extension package under `editors/vscode/` with `package.json`, `.vscode/launch.json`, `language-configuration.json`, the first `pyprompt.tmLanguage.json`, and a finished subtree README.
  - Installed the isolated npm dependency surface and generated `editors/vscode/package-lock.json`.
  - Added `/editors/vscode/node_modules/` to `.gitignore` so the new subtree stays isolated without introducing repo-root Node tooling.

## Phase 2 — Baseline Highlighting And Editor Mechanics

Status: COMPLETE

* Goal:
  Make shipped `01` through `14` prompt files stop looking like plain text and give them sensible comment, folding, and Enter behavior.
* Work:
  - Implement `editors/vscode/language-configuration.json` with `#` comments, quote and bracket pairs, `folding.offSide`, and the initial narrow `onEnterRules` set for colon-headed blocks.
  - Author `editors/vscode/syntaxes/pyprompt.tmLanguage.json` for the shipped lexical surface:
    - declaration keywords
    - field and workflow-item keywords
    - strings
    - standalone comments
    - inheritance brackets
    - dotted imports and workflow targets
    - local workflow keys before `:`
  - Add `editors/vscode/tests/unit/**/*.test.prompt` fixtures for lexical edges and invalid-but-lexically-interesting shapes.
  - Wire the unit-test script so the extension package can run `vscode-tmgrammar-test` without any VS Code runtime harness.
* Verification (smallest signal):
  - Run the unit grammar tests against the extension package.
  - Manually open representative prompt files in local VS Code or an Extension Development Host:
    - `examples/01_hello_world/prompts/AGENTS.prompt`
    - `examples/03_imports/prompts/AGENTS.prompt`
    - at least one nested import file from `examples/03_imports/prompts/**`
    - `examples/09_outputs/prompts/AGENTS.prompt`
    - `examples/14_handoff_truth/prompts/AGENTS.prompt`
    - one invalid prompt such as `examples/01_hello_world/prompts/INVALID_PARSE_MISSING_COLON.prompt`
* Docs/comments (propagation; only if needed):
  - Update `editors/vscode/README.md` with the grammar-test command and the representative manual smoke files.
* Exit criteria:
  - Representative shipped prompts are no longer plain gray text.
  - Unit fixtures cover the key lexical edges the grammar is expected to own.
  - Comment toggling, off-side folding, and initial Enter behavior are present and useful.
* Rollback:
  - Revert the grammar, language configuration, and unit fixtures to the Phase 1 scaffold state.
Completed work:
  - Implemented TextMate highlighting for declaration keywords, typed fields, control words, strings, comments, inheritance brackets, dotted references, generic keys, and incomplete `agent Name` declarations.
  - Added focused unit fixtures for declarations, controls and fields, and invalid-but-lexical authoring states.
  - Verified the unit suite passes through `vscode-tmgrammar-test`.

## Phase 3 — Lark Alignment And Mirrored Snapshot Coverage

Status: COMPLETE

* Goal:
  Make grammar drift fail loudly and broaden regression coverage across every verified prompt input without polluting the canonical example tree.
* Work:
  - Implement `editors/vscode/scripts/validate_lark_alignment.py` so it reads `pyprompt/grammars/pyprompt.lark` directly and fails if the extension keyword inventory or lexical assumptions drift.
  - Mirror every verified `.prompt` file from `examples/01_*` through `examples/14_*` into `editors/vscode/tests/snap/examples/**/prompts/**/*.prompt`.
  - Ensure the mirrored snapshot fixtures record their source example path so the duplication remains auditable.
  - Wire `vscode-tmgrammar-snap` against the mirrored snapshot tree and make `npm test` run the full grammar-test surface.
  - Keep the snapshot artifacts inside the editor-owned tree only; do not point snapshot output at `examples/`.
  - If implementation unexpectedly touched any file under `pyprompt/`, include the shipped-language preservation run in this phase before closing it.
* Verification (smallest signal):
  - Run the Lark-alignment validator through the repo’s Python toolchain.
  - Run the full grammar-test suite, including mirrored snapshot coverage.
  - If any file under `pyprompt/` changed, run `make verify-examples`; if only a narrower preservation signal is needed first, run a targeted manifest and then the full corpus before finalization.
* Docs/comments (propagation; only if needed):
  - Update `editors/vscode/README.md` with the validator command and the snapshot-update workflow.
  - Add source-path notes where needed in mirrored fixtures so future sync work stays obvious.
* Exit criteria:
  - Keyword drift fails loudly against `pyprompt.lark`.
  - Snapshot coverage spans every verified `.prompt` file, including nested import fixtures.
  - The canonical `examples/` tree remains free of `.snap` artifacts.
* Rollback:
  - Remove the validator and mirrored snapshot tree while keeping the working unit-tested grammar in place.
Completed work:
  - Added `editors/vscode/scripts/validate_lark_alignment.py`, which checks the extension metadata and regex coverage against the shipped Lark grammar.
  - Mirrored all 41 verified `.prompt` files from `examples/01_*` through `examples/14_*` into `editors/vscode/tests/snap/examples/**`.
  - Generated 41 adjacent `.snap` files and verified `npm test`, the validator run, and a final `make verify-examples` pass all succeed.

## Phase 4 — Local Use Docs, Cleanup, And Final Smoke

Status: COMPLETE

* Goal:
  Make the extension cheap to use day to day and leave no stale or accidental truth surfaces behind.
* Work:
  - Finish `editors/vscode/README.md` with the normal local use path:
    - Extension Development Host
    - unpacked local install in the user’s regular VS Code
    - refresh steps after grammar changes
  - Remove any temporary scratch grammars, temporary keyword snapshots, or one-off test debris created during implementation.
  - Confirm the final package still has no runtime JS/TS entrypoint, no root-level Node tooling, and no support claims beyond `01` through `14`.
  - If the mirrored snapshot tree already feels painful to maintain, record the sync-helper need as follow-up without broadening phase-one scope.
* Verification (smallest signal):
  - Follow the README once in a normal local VS Code workflow and confirm highlighting plus basic folding and Enter behavior on representative files.
  - Re-run the extension’s grammar-test suite after any cleanup that could affect paths or scripts.
* Docs/comments (propagation; only if needed):
  - Make `editors/vscode/README.md` the single local-usage source of truth for this extension surface.
* Exit criteria:
  - The extension is locally usable in the user’s normal VS Code.
  - The docs match the real workflow.
  - No stray scratch artifacts or accidental competing tool surfaces remain.
* Rollback:
  - Revert doc and cleanup-only changes while preserving the tested extension package if needed.
Completed work:
  - Finished `editors/vscode/README.md` with install, test, Extension Development Host, unpacked local install, and refresh instructions.
  - Synced `AGENTS.md` and this plan doc to the actual manifest-backed `01` through `14` scope discovered during implementation.
  - Kept the shipped runtime untouched while landing the editor subtree, tests, snapshots, and repo hygiene changes.
Manual QA (non-blocking):
  - I did not run a GUI VS Code smoke check in this environment. Open representative files such as `examples/01_hello_world/prompts/AGENTS.prompt`, `examples/09_outputs/prompts/AGENTS.prompt`, and `examples/14_handoff_truth/prompts/AGENTS.prompt` in local VS Code or an Extension Development Host to confirm the final editor behavior visually.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

Prefer tiny contract checks around the Lark-alignment validator plus `vscode-tmgrammar-test` unit fixtures for keywords, strings, comments, keys, and dotted targets so drift is caught cheaply.

## 8.2 Integration tests (flows)

Prefer a unit-first grammar test loop plus mirrored snapshot coverage under `editors/vscode/tests/snap/examples/**`. Do not point `.snap` output at the canonical `examples/` tree.

## 8.3 E2E / device tests (realistic)

Keep final verification lightweight: load the local extension in VS Code, open representative prompt files, and confirm highlighting plus basic folding/indent behavior.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

Initial rollout is repo-local only: the extension should be usable from a local checkout without marketplace publication.

## 9.2 Telemetry changes

No telemetry changes are planned for phase one.

## 9.3 Operational runbook

When the shipped grammar changes, regenerate or revalidate the extension artifacts, run the syntax tests, and reload the local VS Code extension before trusting new highlighting behavior.

# 10) Decision Log (append-only)

## 2026-04-06 - Draft local VS Code highlighting direction

Context

The repo already has strong research on syntax highlighting and VS Code internals, but no local extension. The user explicitly wants the solution tightly integrated with the existing Lark grammar and usable during daily authoring now.

Options

- Build a Langium-based extension and accept a second grammar stack.
- Build a minimal TextMate-first local extension anchored to the shipped Lark grammar.
- Delay editor work until a fuller semantic-tooling stack is designed.

Decision

Draft the plan around a TextMate-first local VS Code extension with a narrow Lark-derived lexical bridge, and defer richer runtime tooling until current highlighting limits are proven to matter.

Consequences

- Phase one stays small and immediately useful.
- The extension will not claim full indentation-aware structural understanding.
- We still need to choose the exact extension home and derivation mechanics in research/deep-dive.

Follow-ups

- Confirm the North Star and scope boundaries.
- Lock the canonical extension path and change inventory.
- Decide whether local `.vsix` packaging belongs in phase one or follow-up work.

## 2026-04-06 - Lock phase-one extension shape and alignment strategy

Context

Deep-dive confirmed that the repo has no existing Node or editor-tooling home, that `pyprompt/grammars/pyprompt.lark` is the only honest syntax truth, and that the AST and compiler are too semantic to own lexical highlighting.

Options

- Add runtime VS Code extension code and richer editor features immediately.
- Build a static extension plus a validation-first bridge back to the Lark grammar.
- Put editor-specific helper code into the compiler or AST layer.

Decision

Lock phase one to a static, contribution-only extension in `editors/vscode/`, use a hand-authored TextMate grammar, and enforce alignment with `pyprompt/grammars/pyprompt.lark` through a small Python validator instead of a second parser stack or runtime extension code.

Consequences

- The first implementation stays narrow, local, and directly useful in VS Code.
- The syntax truth remains in one place.
- `.vsix` packaging, semantic tokens, and LSP plumbing stay deferred until the static path proves insufficient.

Follow-ups

- Write the authoritative phase plan against the locked `editors/vscode/` shape.
- Decide whether the local-use path should be unpacked install only or also include optional packaging as a later follow-up.

## 2026-04-06 - Lock isolated npm surface and editor-owned grammar test shape

Context

The second deep-dive pass confirmed that the extension can stay contribution-only with no runtime code, but it also exposed a tooling detail: `vscode-tmgrammar-snap` writes adjacent `.snap` files, so using canonical example prompts directly for snapshots would dirty the shipped example tree.

Options

- Introduce a broader JS or TS toolchain and runtime-style extension test harness.
- Keep a tiny isolated npm surface under `editors/vscode/`, use unit-first grammar tests, and mirror verified prompt files into an editor-owned snapshot tree.
- Point snapshot output directly at `examples/` and accept adjacent `.snap` files in the canonical prompt corpus.

Decision

Keep Node tooling isolated under `editors/vscode/` with a subtree-local `package-lock.json`, avoid runtime extension code and heavyweight editor test harnesses in phase one, and split grammar coverage into two editor-owned layers: small unit fixtures plus a mirrored snapshot tree under `editors/vscode/tests/snap/examples/**` for every verified `.prompt` file in `examples/01_*` through `examples/14_*`.

Consequences

- The package surface stays smaller and easier to iterate on.
- The canonical prompt corpus remains clean.
- Snapshot coverage now includes nested import and helper prompt files, not just top-level example entry files.

Follow-ups

- Keep mirrored snapshot duplication explicit and source-linked back to the originating verified examples.
- Add a sync helper only if mirror maintenance becomes annoying in practice.

## 2026-04-06 - Lock four-phase implementation order

Context

Earlier versions of the plan had the architecture locked but still left Section 7 as a placeholder. That was no longer good enough to guide implementation because the package surface, test split, and cleanup boundaries were already concrete.

Options

- Keep Section 7 high-level and let implementation choose its own execution order.
- Lock a foundational-first phase order that matches the chosen static-extension architecture.
- Collapse everything into one implementation pass and rely on the call-site audit alone.

Decision

Use four phases in this order: scaffold the isolated static extension package, implement grammar plus language configuration and unit fixtures, add Lark-alignment validation plus the mirrored snapshot corpus, then finish local-use docs and cleanup.

Consequences

- `implement` now has one authoritative execution checklist.
- The validator and mirrored snapshot tree are explicitly downstream of the first working grammar, which keeps early implementation simpler.
- Cleanup and README truth-sync work are now ship-blocking instead of implicit.

Follow-ups

- Execute the plan through `implement`.
- Revisit snapshot-sync tooling only if Phase 3 proves the manual mirror refresh too annoying.

## 2026-04-06 - Correct implementation scope to the actual verified corpus

Context

The original architecture pass was grounded when the repo narrative still described shipped support through `06`, but the implementation baseline for this run showed a different truth: `make verify-examples` now passes the manifest-backed corpus from `examples/01_hello_world` through `examples/14_handoff_truth`, and `pyprompt/grammars/pyprompt.lark` already contains the later declaration and routing surfaces.

Options

- Keep the extension plan frozen at `01` through `06` and knowingly under-serve the current worktree.
- Correct the plan, docs, and editor scope to the actual manifest-backed `01` through `14` surface now.
- Stop implementation until the repo's docs are repaired elsewhere.

Decision

Correct the plan and implementation scope to the actual verified `01` through `14` corpus in this worktree, while still keeping `pyprompt/grammars/pyprompt.lark` as the only syntax truth and excluding unverified pressure surfaces such as `examples/99_not_clean_but_useful/`.

Consequences

- The extension will immediately cover the grammar the repo actually proves today instead of an outdated subset.
- `AGENTS.md` and this plan both need truth-sync edits as part of implementation.
- Historical planning notes that treated `07` through `14` as future work remain useful background, but they are no longer authoritative scope boundaries for this run.

Follow-ups

- Keep future scope claims tied to the manifest-backed corpus, not to older planning narratives.
- Re-run the corpus and grammar tests after the editor surface lands.
