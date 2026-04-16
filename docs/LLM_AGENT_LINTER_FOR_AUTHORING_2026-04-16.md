---
title: "Doctrine - LLM Agent Linter - Architecture Plan"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: new_system
related:
  - PRINCIPLES.md
  - docs/FIRST_CLASS_OPINIONATED_WARNING_LAYER_FOR_AUTHORING_2026-04-16.md
  - docs/AUTHORING_PATTERNS.md
  - docs/COMPILER_ERRORS.md
  - docs/README.md
  - docs/AGENT_LINTER_PROMPT_2026-04-16.md
  - docs/AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json
  - docs/AGENT_LINTER_PROOF_FIXTURE_2026-04-16.json
  - docs/AGENT_LINTER_CODEX_CLI_PROOF_2026-04-16.md
  - docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16.json
  - editors/vscode/README.md
  - editors/vscode/package.json
  - editors/vscode/extension.js
---

# TL;DR

- Outcome: turn the current linter design note into the one Doctrine plan for a shipped, optional, LLM-backed `agent linter` that feels like a real linter in the terminal, JSON, CI, and VS Code.
- Problem: we have a strong rule catalog, prompt, schema, and proof artifact, but they still live as docs, not as shipped product architecture, and the current design does not yet fully lock the compiler-vs-linter boundary or the editor integration path.
- Approach: keep one Python linter core, one stable `AL###` finding model, one review-packet builder, and one shipped prompt/schema pair, then render the same findings into terminal, JSON, Markdown, and VS Code diagnostics.
- Plan: lock the boundary and owner paths, add deterministic packet and prepass builders, promote the prompt and schema into shipped assets, ship a CLI, then extend the existing VS Code extension to consume the same JSON findings instead of inventing a second lint engine.
- Non-negotiables: the linter must stay optional but encouraged, it must not own compiler errors, core Doctrine rules must stay generic, batch duplication must be first-class, and the live docs path must teach the feature as a canonical Doctrine surface once it ships.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-16
external_research_grounding: done 2026-04-16
deep_dive_pass_2: done 2026-04-16
recommended_flow: phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

Doctrine can ship an optional `agent linter` that uses an LLM for judgment but
still behaves like a real linter. A good implementation will:

- find high-value authoring problems with exact evidence
- keep compiler errors and linter findings as two separate surfaces
- support `single-target` and `batch` runs from the same core engine
- emit stable findings that work in terminal output, JSON, CI, and VS Code
- let the current VS Code extension surface the same findings without building
  a second JS-only rules engine

If the shipped feature cannot produce stable codes, stable evidence spans, and
editor-ready findings from the same core run, the claim is false.

## 0.2 In scope

- Requested behavior scope:
  - ship a Doctrine `agent linter` for authoring quality
  - lint both authored prompt source and emitted output in the shipped feature
  - support both `single-target` and `batch` mode
  - keep stable core `AL###` codes with rationale, evidence, and fix help
  - keep the current prompt and schema work, but move shipped truth out of docs
  - support terminal, JSON, Markdown, and VS Code-facing output from one core
    finding model
  - support cross-surface findings that compare authored source, emitted output,
    imports, and declared constraints in the same run
  - support cross-agent duplication findings when a compile or lint run covers
    several agents
  - keep the feature optional at the product level, but document it as an
    encouraged part of serious Doctrine authoring workflows
- Allowed architectural convergence scope:
  - new Doctrine-owned linter code under a canonical Python owner path
  - a new CLI surface for authoring lint runs
  - optional compile-adjacent `--lint` integration after the standalone CLI is
    stable
  - shipped prompt and schema assets for the linter
  - tests and fixtures for packet building, normalization, and renderers
  - live Doctrine docs for the linter
  - `editors/vscode/` integration that consumes the canonical linter output
- Adjacent-surface scope:
  - include now: the current prompt, schema, fixture, proof doc, proof output,
    and this plan doc
  - include now: the existing VS Code extension surfaces because the user wants
    editor-grade output as part of the real feature
  - include now when the feature ships publicly: `docs/README.md`, a new live
    linter guide, `docs/AUTHORING_PATTERNS.md`, and `editors/vscode/README.md`
  - explicit defer: SARIF or GitHub code-scanning export can follow after the
    core CLI, JSON, and VS Code path are real
  - explicit out of scope: repo-local overlay policies from this repo or any
    sibling repo
- Compatibility posture:
  - preserve the current compiler and compile-error contract
  - allow a clean additive rollout for the new linter surfaces
  - do not hide missing linter configuration behind fake passes or compiler
    fallbacks

## 0.3 Out of scope

- provider-specific transport, retries, rate limiting, or LiteLLM wiring
- turning core Doctrine lint rules into repo-local or org-local policy
- using the linter to report parse, compile, schema, or emit failures that the
  compiler can already prove
- a new full Doctrine language server in phase 1
- automatic multi-file skill extraction or prompt rewrites without developer
  review
- making the linter run by default on every compile before the standalone CLI
  and editor path are trustworthy

## 0.4 Definition of done (acceptance evidence)

- The plan names one canonical owner path for the linter core, one canonical
  owner path for the shipped prompt and schema, and one editor integration path.
- The linter finding model is concrete enough to render into terminal, JSON,
  Markdown, and VS Code diagnostics without inventing a second result shape.
- The boundary between compiler errors and linter findings is explicit in the
  plan, the prompt, the schema comments, and the shipped docs.
- A batch run can surface repeated duplication across several agents using one
  normalized finding plus related locations.
- The live docs path teaches the linter as an optional but encouraged Doctrine
  surface once the feature ships.
- The VS Code extension can show linter diagnostics and quick actions using the
  same underlying finding model.
- Implementation proof is proportionate:
  - targeted linter tests and fixtures pass
  - schema validation for structured linter output passes
  - `make verify-examples` passes if compile or emit surfaces move
  - `make verify-diagnostics` runs only if compiler diagnostics move
  - `cd editors/vscode && make` passes if the extension changes
- This `reformat` pass is docs-only. I did not run verify commands here.

## 0.5 Key invariants (fix immediately if violated)

- No compiler-error ownership inside the linter.
- No repo-local policy inside core `AL###` rules.
- No finding without exact evidence.
- No second JS-only linter engine in the VS Code extension.
- No separate editor-only rule codes.
- No color-only meaning in human output.
- No `Error`-level editor diagnostics for linter findings. Compiler failures own
  that lane.
- No docs-owned shipped prompt or schema once implementation starts.
- No batch mode that silently drops cross-agent duplication.
- No source-only MVP.
- No output-only MVP.
- No later phase may add one of the missing surfaces and pretend the earlier
  shipped cut was complete.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Keep the linter trustworthy. Exact evidence, stable codes, and clear fixes
   matter more than finding every possible nit.
2. Keep compiler and linter responsibilities clean. A quality linter must not
   blur into compile diagnostics.
3. Make one core run power every output surface. Terminal, JSON, CI, and editor
   output should be views over one finding model.
4. Make batch duplication first-class. Cross-agent drift is one of the highest
   value checks in this feature.
5. Reuse the current VS Code extension instead of inventing a new editor path
   first.
6. Promote the feature into the live docs path once it is real.

## 1.2 Constraints

- Doctrine shipped truth lives in `doctrine/`, not in dated plan docs.
- The current prompt, schema, fixture, and proof are real design assets, but
  they are not yet the shipped owner paths.
- The current VS Code extension is repo-local and direct. It is not a full
  language server today.
- The feature is LLM-backed, so network-free test proof must focus on packet
  building, schema validation, normalization, and renderers rather than live
  provider calls.
- Shipped bundled prose and docs should stay near a 7th grade reading level.
- The linter is optional at the product level, so missing configuration should
  not be confused with a clean pass.

## 1.3 Architectural principles (rules we will enforce)

- One linter core, many renderers.
- One stable `AL###` catalog for core Doctrine law.
- Keep overlays separate from core.
- Use deterministic helpers for exact facts, and reserve the LLM for judgment.
- Keep editor severity lower than compiler severity. High-value lint findings can
  still fail CI without pretending to be compile errors.
- Promote prompt and schema assets into shipped code before treating the feature
  as public Doctrine truth.
- Reuse the existing VS Code extension as the first editor adapter.
- Prefer code actions that are safe, explicit, and reversible.

## 1.4 Known tradeoffs (explicit)

- Exact evidence and stable locations will make packet building more complex.
- Batch mode is higher value, but it will cost more than single-target runs.
- A direct VS Code adapter is the fastest path in this repo, but it is less
  editor-portable than a full language server.
- Quick-fix rewrites are useful, but only a small subset of findings will be
  safe to apply automatically.
- The more machine-friendly the finding model becomes, the more careful we must
  be to keep the human output plain and readable.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already has a detailed linter design note,
[AGENT_LINTER_PROMPT_2026-04-16.md](AGENT_LINTER_PROMPT_2026-04-16.md),
[AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json](AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json),
[AGENT_LINTER_PROOF_FIXTURE_2026-04-16.json](AGENT_LINTER_PROOF_FIXTURE_2026-04-16.json),
and a real [Codex CLI proof](AGENT_LINTER_CODEX_CLI_PROOF_2026-04-16.md) with a
saved [structured output example](AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16.json).

That work already proves several core ideas:

- the linter should review a packet, not raw hidden repo state
- the feature needs `single-target` and `batch` mode
- the core rule catalog should be stable and generic
- the output should feel like a real linter, not a vague essay
- the prompt and schema can already produce valid structured output

Doctrine also already ships a repo-local VS Code extension, but it is still a
syntax and navigation surface. It registers the `doctrine` language,
TextMate grammar, import links, and Go to Definition. It explicitly does not
yet provide diagnostics, hover, completion, rename, symbol search, or a full
language server.

## 2.2 What's broken / missing (concrete)

### P1. The current design is not yet a canonical architecture artifact

The current linter doc is a good design note, but it is not yet the one full
arch-step artifact that later implementation work can trust.

### P1. Shipped truth still lives in docs instead of code

The prompt, schema, and proof fixture live under `docs/`. That is fine for
proof, but not as the final owner path for a shipped Doctrine feature.

### P1. The compiler-vs-linter boundary is still too soft

The design intent says the linter should not act like a compiler, but the plan
still needs a stronger contract about severity mapping, ownership, and docs
boundaries so editor output does not look like compile failure output.

### P1. There is no canonical packet builder or normalized finding model in code

The design talks about review packets and structured findings, but there is not
yet one Doctrine-owned implementation path for building packets, validating
responses, normalizing findings, or rendering them into several front ends.

### P1. The editor path is not locked

The repo already has a VS Code extension, but the design did not yet choose
whether phase 1 should use the existing direct extension, a new language server,
or a second ad hoc integration path.

### P2. The live docs path is not decided

`docs/README.md` explicitly says dated plans are not the live reference path.
So if the linter ships, it needs a canonical live doc and cross-links in the
real docs path.

## 2.3 Constraints implied by the problem

- The feature must be additive. It cannot destabilize compiler proof.
- The implementation must treat output shape as a product surface, not a local
  helper detail.
- The packet builder must preserve exact source locations closely enough for
  editor diagnostics and rewrite help.
- The first editor path should fit the existing repo reality instead of leaping
  straight to a full LSP stack.
- The live docs path must teach the feature without turning this dated plan into
  shipped truth.

# 3) Research Grounding (external + internal "ground truth")

## 3.1 External anchors (papers, systems, prior art)

- [VS Code Programmatic Language Features](https://code.visualstudio.com/api/language-extensions/programmatic-language-features)
  says diagnostics can come from a direct `DiagnosticCollection` or from the
  Language Server Protocol, and notes that LSP gives a reusable editor backend.
  Adopt: keep the linter finding model editor-agnostic and make the first VS
  Code adapter thin.
- [Language Server Protocol 3.17](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/)
  defines a diagnostic shape with `range`, `severity`, `code`,
  `codeDescription`, `source`, `message`, `tags`, `relatedInformation`, and
  `data`. Adopt: normalize Doctrine linter findings around those concepts so the
  same run can power terminals, editors, and code actions.
- The same LSP spec says `codeDescription.href` can point to more information,
  `relatedInformation` can point at related locations, and `data` survives from
  diagnostics to code actions. Adopt: every `AL###` finding should have a docs
  URL, cross-target findings should carry related locations, and safe editor
  code actions should use structured payloads instead of reparsing free text.
- [ESLint Formatters Reference](https://eslint.org/docs/latest/use/formatters/)
  shows a strong split between human output and structured output. Its
  `json-with-metadata` formatter carries lint results plus rule metadata and fix
  suggestions. Adopt: Doctrine JSON output should carry stable rule metadata,
  docs URLs, and fixability hints. Reject: do not copy ESLint's exact JSON
  shape because Doctrine findings can be cross-target and packet-based.
- [Biome Reporters](https://biomejs.dev/reference/reporters) and
  [Biome CLI](https://biomejs.dev/reference/cli/) show one linter core with
  several reporter targets such as default terminal, JSON, GitHub, and SARIF.
  Adopt: keep renderer diversity in the design. Defer: SARIF is useful, but it
  should follow the core CLI, JSON, and VS Code path.
- [Biome VS Code Extension](https://biomejs.dev/reference/vscode/) shows a
  first-party extension that exposes diagnostics, code actions, and
  fix-on-save, with settings that can require configuration before the extension
  becomes active. Adopt: Doctrine should keep editor enablement explicit, and it
  should only expose safe quick fixes by default.
- [Ruff Editor Integrations](https://docs.astral.sh/ruff/editors/) and
  [Ruff Editor Features](https://docs.astral.sh/ruff/editors/features/) show a
  single common backend that serves diagnostics, code actions, and safe vs
  unsafe fixes. Adopt: one shared backend should own Doctrine linter truth, and
  fix safety should be first-class. Reject for phase 1: a full Doctrine language
  server is not the fastest grounded path in this repo.

Inference from these sources:

- The best phase-1 path for Doctrine is not a new language server. It is one
  Python linter core with a stable JSON result shape, then a thin adapter in the
  existing VS Code extension.
- The finding model should be LSP-shaped even if phase 1 does not yet run as an
  LSP server.
- Editor diagnostics for this feature should map to `Warning`, `Information`,
  and `Hint`, not `Error`, so the boundary with compiler errors stays clear.

## 3.2 Internal ground truth (code as spec)

- This design work already produced real assets:
  - [AGENT_LINTER_PROMPT_2026-04-16.md](AGENT_LINTER_PROMPT_2026-04-16.md)
  - [AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json](AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json)
  - [AGENT_LINTER_PROOF_FIXTURE_2026-04-16.json](AGENT_LINTER_PROOF_FIXTURE_2026-04-16.json)
  - [AGENT_LINTER_CODEX_CLI_PROOF_2026-04-16.md](AGENT_LINTER_CODEX_CLI_PROOF_2026-04-16.md)
  - [AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16.json](AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16.json)
- The prompt already says the linter is not a compiler and must work only from
  the review packet. That is the right product boundary, but it still needs a
  stronger implementation contract.
- `editors/vscode/README.md` says the extension currently covers syntax,
  import-path clicks, and definition jumps, and explicitly does not yet cover
  diagnostics or a full language server.
- `editors/vscode/extension.js` shows the current extension is a direct VS Code
  integration. It registers a document-link provider and a definition provider.
  It does not already own a diagnostics path.
- `editors/vscode/package.json` shows the extension is still packaged as a
  repo-local language support extension, not a standalone language server.
- Doctrine's existing CLI pattern is Python `argparse` modules such as
  `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, and `doctrine/verify_corpus.py`.
  The linter should follow that repo shape instead of inventing an unrelated
  CLI stack.
- `docs/README.md` says dated plans are not the live docs path. That means this
  doc must stay a plan, while a shipped linter later needs a live doc.
- `docs/COMPILER_ERRORS.md` is the canonical compiler-error catalog. The linter
  must stay out of that catalog except for clear cross-links about the boundary.

Canonical owner-path decision:

- The linter core should live under `doctrine/_linter/`.
- The first CLI surface should live under `doctrine/lint_authoring.py` and use
  the repo's current `argparse` pattern.
- The shipped prompt and schema should move under `doctrine/_linter/assets/`.
- The current docs prompt, schema, and proof files should remain as design and
  proof artifacts, but not as the final shipped owner path.
- The first editor integration should stay under `editors/vscode/` and consume
  the canonical JSON findings.

## 3.3 Decision gaps that must be resolved before implementation

This reformat resolves the main plan-shaping gaps.

Resolved decisions:

- Phase 1 editor integration will extend the current VS Code extension. It will
  not start with a new Doctrine language server.
- The linter will own a stable internal finding model that is LSP-shaped.
- Linter findings in editors will map to:
  - `high` -> `Warning`
  - `medium` -> `Information`
  - `low` -> `Hint`
  - never `Error`
- The first public output formats are terminal, JSON, and Markdown.
- SARIF is explicitly deferred.
- The feature is optional at the product level. If a user does not opt in, the
  linter does not run. If the user does opt in and the linter cannot run, it
  fails clearly instead of pretending to pass.
- Batch mode is first-class. In compile-adjacent runs, a multi-target compile
  should build one batch packet when lint is enabled.
- Safe editor quick fixes are allowed only when the finding includes one exact
  replacement for one exact span. Otherwise the editor should offer docs links,
  rerun actions, or a copyable suggestion, not silent rewrite automation.
- A live docs page will be required when the feature ships. This dated plan will
  stay a plan doc.

No plan-shaping blocker remains for implementation planning.

# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- Current design and proof docs:
  - `docs/LLM_AGENT_LINTER_FOR_AUTHORING_2026-04-16.md`
  - `docs/AGENT_LINTER_PROMPT_2026-04-16.md`
  - `docs/AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json`
  - `docs/AGENT_LINTER_PROOF_FIXTURE_2026-04-16.json`
  - `docs/AGENT_LINTER_CODEX_CLI_PROOF_2026-04-16.md`
  - `docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16.json`
- Current editor surfaces:
  - `editors/vscode/package.json`
  - `editors/vscode/extension.js`
  - `editors/vscode/resolver.js`
  - `editors/vscode/README.md`
- Current Doctrine CLI pattern:
  - `doctrine/emit_docs.py`
  - `doctrine/emit_flow.py`
  - `doctrine/verify_corpus.py`

## 4.2 Control paths (runtime)

Today there is no Doctrine-owned linter runtime path.

What exists instead:

- a design-time prompt and schema proof path through Codex CLI
- deterministic compile and emit flows for Doctrine targets
- a direct VS Code extension for syntax and navigation

What does not exist yet:

- a packet builder in Doctrine code
- a Doctrine linter runner
- a normalized finding model in Doctrine code
- terminal or JSON linter renderers in Doctrine code
- a VS Code diagnostics bridge for Doctrine authoring lint

## 4.3 Object model + key abstractions

The current design implies, but does not yet implement, these abstractions:

- review packet
- stable `AL###` rule catalog
- finding with evidence, rationale, fix help, and examples
- run summary with threshold and exit code
- single-target and batch mode

Right now those abstractions live in docs and prompt text, not in shipped code.

## 4.4 Ownership and failure boundaries

- The compiler owns parse, compile, schema, and emit failures.
- The linter should own quality findings only.
- The current docs say that boundary in words, but the repo has not yet turned
  it into code-level owner paths, docs paths, editor severity mapping, or CLI
  behavior.

# 5) Target Architecture (to-be)

## 5.1 Canonical owner paths

The shipped system should use these owner paths:

- `doctrine/_linter/`
  - `catalog.py` or equivalent for the stable core `AL###` catalog
  - `packet.py` for review-packet building
  - `prepasses.py` for deterministic helpers such as duplicate hints and
    readability metrics
  - `runner.py` for the prompt-plus-schema execution boundary
  - `normalize.py` for schema-validated finding normalization
  - `render_terminal.py`, `render_json.py`, and `render_markdown.py`
  - `assets/agent_linter_prompt.md`
  - `assets/agent_linter_output_schema.json`
- `doctrine/lint_authoring.py`
  - the first standalone CLI entrypoint, following current Doctrine CLI style
- `editors/vscode/`
  - the first editor adapter, which consumes canonical JSON findings
- `tests/fixtures/agent_linter/`
  - packet fixtures, response fixtures, and renderer fixtures
- `docs/AGENT_LINTER.md`
  - the live canonical docs page once the feature ships

## 5.2 Review packet and analysis pipeline

The core pipeline should be:

1. Compile or load the requested Doctrine target set once.
2. Build a review packet with only exact available facts.
3. Add deterministic helpers when they are cheap and exact.
4. Execute the shipped prompt with the shipped JSON schema.
5. Validate the returned JSON.
6. Normalize findings into the canonical internal model.
7. Render the same findings into the requested output surface.

Required packet facts:

- target names
- authored source text
- emitted Markdown
- imported skills
- imported modules
- declared constraints when present
- source file paths and line ranges for evidence spans
- run mode and fail threshold

Deterministic prepasses that belong here:

- duplicate-block hints across targets
- reading metrics
- size stats
- declared-constraint extraction
- target graph facts that help batch mode stay exact

The packet builder must not invent truths the compiler does not know. If a fact
is missing, the packet must stay explicit about that gap.

Surface rule:

- the shipped architecture includes both authored source and emitted output from
  the start
- this plan does not permit a source-only first cut or an output-only first cut
- a normal lint packet should include both authored source and emitted output
  for the target set whenever both exist
- imported skills, imported modules, and declared constraints stay part of the
  same packet, not side-channel context
- findings may be source-only, output-only, or cross-surface, but the core
  architecture does not split those into separate linters

## 5.3 Canonical finding model

The internal finding model should be the one source of truth for all renderers.
It should carry:

- stable `AL###` code
- title and one-line summary
- severity and confidence
- affected targets
- primary location
- exact evidence spans
- related locations
- docs URL for the rule
- why it matters
- recommended fix
- optional safe text edit metadata
- optional suggested rewrite
- examples and shared-owner suggestions where relevant

LSP-aligned mapping rules:

- `code` -> `AL###`
- `codeDescription.href` -> live docs anchor for the rule
- `message` -> short human summary
- `relatedInformation` -> contradiction peers, duplicate peers, imported-source
  conflicts, and other supporting locations
- `data` -> structured payload for safe editor code actions

Boundary rule:

- No linter finding is an LSP `Error`.
- Compiler failures keep the `Error` lane.
- The linter uses warning-like editor output plus CLI exit thresholds.

## 5.4 Renderers and UX surfaces

The same normalized finding set should support four front ends:

- terminal renderer
  - ANSI color by default with `--color=auto|always|never` and `NO_COLOR`
  - short summary first, then finding cards
  - stable exit codes `0`, `1`, and `2`
- JSON renderer
  - stable machine-readable output for scripts, CI, and editor adapters
  - includes rule metadata, docs URL, and fixability hints
- Markdown renderer
  - useful for saved reports, PR comments, or review artifacts
- VS Code diagnostics adapter
  - converts canonical findings into `DiagnosticCollection` entries and safe
    code actions

Defer:

- SARIF and other external CI reporter formats after the core surfaces are
  stable

## 5.5 VS Code integration shape

Phase-1 editor integration should be direct and thin.

What the extension should do:

- add a linter command for the current target
- add a workspace lint command for batch mode
- optionally run current-target lint on save or on explicit idle debounce
- call the canonical Doctrine linter CLI and read JSON output
- map JSON findings into VS Code diagnostics
- surface safe quick fixes when exact one-span replacements are present
- surface docs links and rerun actions when no safe rewrite exists

Why this is the right phase-1 choice:

- the current repo already has a direct VS Code extension
- Doctrine does not yet ship a language server
- a thin adapter keeps the finding logic in Python where the compiler and packet
  builder already live
- the result shape still stays LSP-friendly for future editor expansion

Required VS Code settings surface:

- `doctrine.lint.enabled`
- `doctrine.lint.runOnSave`
- `doctrine.lint.requireProjectSupport`
- `doctrine.lint.command` if the CLI path must be overridden
- `doctrine.lint.failThreshold`

The extension should stay inactive for linting when `doctrine.lint.enabled` is
false.

## 5.6 Live docs and public teaching path

Once the feature ships, the live docs path should include:

- `docs/AGENT_LINTER.md` as the canonical guide
- `docs/README.md` link to that guide
- `docs/AUTHORING_PATTERNS.md` guidance on when to use lint and how to author
  for it
- `docs/EMIT_GUIDE.md` updates if `emit_docs --lint` becomes public
- `editors/vscode/README.md` updates for lint commands, settings, and quick
  fixes

The current dated prompt, schema, fixture, and proof docs should stay linked as
proof and design history, but not as the live owner path.

## 5.7 Non-goals that stay locked even after implementation

- The linter does not become a second compiler.
- Core Doctrine does not ship local overlay rules.
- The VS Code extension does not gain its own separate rule engine.
- Auto-fix does not become silent prompt surgery.
- Live provider calls do not become required test proof.

# 6) Call-Site Audit (exhaustive change inventory)

| Surface | Paths | Why it matters | Disposition | Notes |
| --- | --- | --- | --- | --- |
| Core linter engine | new `doctrine/_linter/**` | Canonical owner for packets, rules, normalization, and renderers | include now | This is the product core. |
| Standalone CLI | new `doctrine/lint_authoring.py` and package entrypoint work if needed | Real linter users need a stable CLI before editor or compile hooks | include now | Follow Doctrine's current `argparse` pattern. |
| Shipped prompt and schema assets | new `doctrine/_linter/assets/**` | Docs cannot remain the shipped owner path | include now | Current docs versions remain proof artifacts. |
| Prompt/schema/docs proof artifacts | existing `docs/AGENT_LINTER_*` files | Preserve design and proof history, keep cross-links alive | include now | Keep linked from this plan and the later live guide. |
| Packet and response fixtures | new `tests/fixtures/agent_linter/**` | Network-free proof needs stable fixtures | include now | Move from docs-only proof to test-owned proof. |
| Targeted linter tests | new `tests/test_agent_linter_*` | Needed to prove packet building, normalization, renderers, and boundary behavior | include now | No live provider dependency in required test proof. |
| Compile-adjacent integration | `doctrine/emit_docs.py` and nearby emit helpers if lint is added there | User wants compile-process use, including multi-target batch mode | include now after standalone CLI is stable | Additive `--lint` only. Do not make lint a compile requirement. |
| Compiler diagnostics | `docs/COMPILER_ERRORS.md`, diagnostic smoke, compiler tests | Boundary must stay clear | defer unless boundary wording must cross-link | Do not merge `AL###` into compiler error catalogs. |
| Live docs path | new `docs/AGENT_LINTER.md`, `docs/README.md`, `docs/AUTHORING_PATTERNS.md`, maybe `docs/EMIT_GUIDE.md` | Dated plans are not live docs | include now for the shipped feature phase | This plan stays a plan doc. |
| VS Code extension | `editors/vscode/**` | User explicitly wants editor-grade linter behavior | include now | Reuse the current extension. |
| Other editors / LSP server | new server surface, alternate editors | Nice long-term path, not required for phase 1 | explicit defer | Keep data shape LSP-friendly now. |
| SARIF / GitHub reporter | new renderer surfaces | Good future CI path, not needed to prove core value | explicit defer | JSON and Markdown come first. |
| Example corpus | `examples/**` | Helpful teaching surface, but not the best first proof path for an LLM-backed optional feature | explicit defer | Prefer test fixtures first. |

# 7) Depth-First Phased Implementation Plan (authoritative)

## Phase 1. Lock the boundary and promote shipped assets

Goals:

- promote the prompt and schema into `doctrine/_linter/assets/`
- freeze the core `AL###` catalog in code
- define the normalized finding model and severity mapping
- tighten the docs boundary so the linter cannot claim compiler errors
- lock the no-scope-cut rule in code and docs: no source-only or output-only
  first cut

Implementation notes:

- copy the current prompt and schema into shipped asset paths
- keep the current docs copies linked as proof artifacts
- codify the editor-severity rule: lint never emits editor `Error`
- add docs-link metadata per code so `codeDescription.href` is ready

Exit criteria:

- one canonical asset pair exists in code
- one canonical finding model exists in code
- prompt, schema, and docs agree on the compiler-vs-linter boundary

## Phase 2. Build the review-packet and deterministic prepasses

Goals:

- add a packet builder for single-target and batch runs
- add deterministic helpers for duplicate hints, reading metrics, and size stats
- preserve enough source-location truth for editor diagnostics and rewrite help
- require both authored-source and emitted-output packet slots in the normal
  path so cross-surface findings are first-class from the start

Implementation notes:

- reuse the existing compile and emit session as the source of exact facts
- gather authored source, emitted Markdown, imports, and declared constraints
- build cross-target duplicate hints only from exact visible text and graph data
- keep packet gaps explicit instead of inventing facts

Exit criteria:

- single-target packet tests pass
- batch packet tests pass
- duplicate and readability prepass tests pass
- the packet can represent related locations cleanly

## Phase 3. Add the runner, validation, and renderer stack

Goals:

- add the LLM execution boundary around the shipped prompt and schema
- validate responses strictly
- normalize responses into the canonical finding model
- render terminal, JSON, and Markdown outputs from the same finding set

Implementation notes:

- provider plumbing is outside this plan's main design scope, but the runner
  contract must accept a packet and return schema-valid JSON or a clear failure
- no renderer may re-derive findings from raw prose
- JSON output should carry enough metadata for editor and CI consumers
- terminal output should preserve the best-in-class UX already designed in the
  imported notes below

Exit criteria:

- schema validation tests pass
- normalization tests pass
- terminal, JSON, and Markdown renderer tests pass
- exit codes `0`, `1`, and `2` are stable

## Phase 4. Ship the standalone CLI

Goals:

- expose the feature through a real Doctrine CLI surface
- support `single-target` and `batch` execution
- support fail thresholds and color controls

Implementation notes:

- start with `python -m doctrine.lint_authoring`
- public package entrypoint polish can follow if needed for package UX
- support output formats `text`, `json`, and `markdown`
- keep the feature optional by requiring explicit invocation

Exit criteria:

- current-target CLI runs work
- multi-target batch CLI runs work
- threshold, color, and output-format flags work

## Phase 5. Add compile-adjacent lint integration

Goals:

- let users opt into lint as part of compile flows
- support batch lint during multi-target compile runs

Implementation notes:

- add an additive `--lint` path only after the standalone CLI is stable
- `emit_docs --lint` should lint the same targets it compiles
- when one compile run covers several targets, the lint packet should be built
  in batch mode so cross-agent duplication can be caught
- lint failure should fail the linted command only when the selected threshold
  is crossed

Exit criteria:

- compile-adjacent lint works for single-target runs
- compile-adjacent lint works for multi-target runs
- no compiler tests or docs treat lint failures as compiler errors

## Phase 6. Extend the VS Code extension

Goals:

- show Doctrine linter findings in the editor
- support current-target and workspace lint commands
- add safe code actions and rule docs links

Implementation notes:

- keep the extension thin: spawn the canonical CLI, read JSON, map diagnostics
- support current-target lint on save only behind an explicit setting
- use related locations for contradiction peers and batch duplicates
- safe quick fixes are allowed only for exact one-span replacements
- all other findings should still provide docs links or rerun actions

Exit criteria:

- lint diagnostics appear in VS Code
- quick fixes work for safe rewrite cases
- workspace batch runs can show cross-target duplicate findings
- `cd editors/vscode && make` passes

## Phase 7. Promote the feature into the live docs path

Goals:

- teach the linter as a canonical Doctrine feature
- keep the dated proof and design artifacts linked, not orphaned

Implementation notes:

- add `docs/AGENT_LINTER.md`
- update `docs/README.md`
- update `docs/AUTHORING_PATTERNS.md`
- update `docs/EMIT_GUIDE.md` if compile-adjacent lint becomes public
- update `editors/vscode/README.md`

Exit criteria:

- the live docs path teaches when to use the linter, how to read its findings,
  and how it differs from compiler errors
- the proof docs remain linked for design and validation history

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Docs-only reformat proof for this pass

- No verify commands were run.
- This pass changed only
  `docs/LLM_AGENT_LINTER_FOR_AUTHORING_2026-04-16.md`.

## 8.2 Required implementation proof later

- targeted unit tests for:
  - packet building
  - duplicate and readability prepasses
  - schema validation and normalization
  - terminal, JSON, and Markdown renderers
  - compiler-vs-linter boundary behavior
- fixture-based proof for:
  - single-target runs
  - batch runs with cross-target duplication
  - safe-fix vs suggestion-only findings
- manual smoke checks for:
  - current-target CLI output
  - batch CLI output
  - docs URL resolution per `AL###` code
  - VS Code diagnostics and quick fixes once the extension changes

## 8.3 Repo proof surfaces that move only when needed

- Run `make verify-examples` if compile or emit code changes.
- Run `make verify-diagnostics` only if compiler diagnostics or diagnostic smoke
  change.
- Run `cd editors/vscode && make` if the extension changes.
- Run `make verify-package` if public package metadata or console scripts change.

## 8.4 What does not need to be blocking proof

- live provider calls in CI
- network-bound lint runs in unit tests
- SARIF export proof before SARIF is in scope
- example-corpus expansion before the core engine and fixtures are stable

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout posture

- Product posture: optional but encouraged
- Initial execution posture: explicit opt-in via CLI
- Compile posture: additive `--lint` only after standalone CLI is trusted
- Editor posture: explicit setting, off until enabled

## 9.2 Operational rules

- If lint is not requested, nothing runs.
- If lint is requested but the linter cannot run, return a clear linter failure.
  Do not fake a pass.
- If the model returns schema-invalid output, treat it as linter execution
  failure, not as a clean lint result.
- If the packet is incomplete, either narrow the finding set explicitly or fail
  the run. Do not guess.

## 9.3 User-facing runtime behavior

- terminal output should start with a fast pass/fail summary
- JSON output should stay stable enough for editor and CI consumers
- editor output should never look like compiler failure output
- docs links per rule should always point at the live linter guide once it ships

## 9.4 Telemetry posture

Doctrine does not need a new hosted telemetry system for this feature.
The useful operational signals are local:

- linter exit code
- schema validation success or failure
- packet-gap counts
- finding counts by severity and code
- editor adapter logs only when explicitly enabled for debugging

# 10) Decision Log (append-only)

- 2026-04-16: Reframed the feature as a Doctrine `agent linter`, not a generic
  warning layer.
- 2026-04-16: Kept core `AL###` rules Doctrine-generic and pushed repo-local
  policies out to overlays.
- 2026-04-16: Locked the compiler boundary. The linter does not own parse,
  compile, schema, or emit failures.
- 2026-04-16: Chose one Python linter core plus many renderers as the target
  architecture.
- 2026-04-16: Chose `doctrine/_linter/` as the canonical code owner path.
- 2026-04-16: Chose `doctrine/lint_authoring.py` as the first CLI owner path.
- 2026-04-16: Chose the existing `editors/vscode/` extension as the first
  editor adapter instead of starting with a new language server.
- 2026-04-16: Chose an LSP-shaped finding model so later editor integrations do
  not require a second result contract.
- 2026-04-16: Chose editor severity mapping that never uses `Error` for lint
  findings.
- 2026-04-16: Locked the shipped scope to both authored prompt source and
  emitted output, with cross-surface findings first-class from the start.
- 2026-04-16: Clarified that this is a hard scope boundary, not a preference.
  The plan does not allow a source-only MVP or an output-only MVP.
- 2026-04-16: Deferred SARIF until after terminal, JSON, Markdown, and VS Code
  are real.
- 2026-04-16: Chose a live docs promotion path so the feature can become part of
  Doctrine's canonical docs instead of staying trapped in a dated plan.

# Appendix A) Imported Notes (unplaced; do not delete)

These notes preserve the detailed rule catalog, examples, and mock output from
the pre-reformat design note. They are still useful design input for the real
implementation.

## Imported current design sections
## 1) Product Boundary

This linter is for people who use Doctrine to author agent systems.

It should review:

- authored prompt source
- emitted agent Markdown
- imported skills, modules, and contracts
- exact side inputs that the caller chooses to provide

It should not hard-code:

- this repo's internal workflow rules
- one team's release process
- one harness's private file layout
- one product's naming rules
- one organization's capability model

Core Doctrine should ship the generic linter.
Teams may add their own overlay rules on top.

## 2) Core Laws The Shipped Linter Should Enforce

The core `AL###` catalog should come only from Doctrine's authoring laws.

### 2.1 Core laws

- context is a budget
- load depth on demand
- write for resolvers
- keep runtime concerns out of authored doctrine
- put exact truth in typed surfaces
- reserve prose for judgment
- reuse beats repetition
- repeated work should become reusable doctrine
- make bloat visible

### 2.2 What this means in practice

The linter should ask:

- Is this always-on text bigger than it needs to be?
- Is this pasted handbook text that should live behind a pointer?
- Is this rule duplicated across several agents?
- Is this repeated method really a skill?
- Is exact truth hidden in prose?
- Is the role clear about what it owns and what it leaves behind?
- Are names and descriptions clear enough for a resolver?
- Is the prose easy to read?
- Do the instructions contradict each other?

## 3) Core Vs Overlay Rules

The shipped linter needs a hard line between core Doctrine rules and local
policy packs.

### 3.1 Core `AL###` rules

These ship with Doctrine.
They must stay generic across users.

### 3.2 Overlay rules

Teams may load extra rules from a host profile.
Those extra rules should use a different prefix, not `AL###`.

Examples of overlay-only checks:

- product-specific tone rules
- one harness's capability allowlist rules
- one repo's file naming rules
- one team's approval flow
- one org's forbidden tools

### 3.3 Why this matters

If core Doctrine ships one team's local policy as if it were a language law,
the product will feel wrong to most users.

## 4) Review Packet

The linter should run on a review packet.
The caller decides what exact facts go into that packet.

### 4.1 Core packet inputs

- authored Doctrine source for the current target
- emitted Markdown for the same target
- imported skill text
- imported module text
- typed declarations and compile graph facts
- file paths and target names

### 4.2 Optional exact side inputs

- line counts
- section size stats
- duplicate-block reports
- reading-level metrics
- declared constraints supplied by the caller

The linter may use optional side inputs only when they are actually present.

## 5) Run Modes

The linter must support two first-class run modes.

### 5.1 `single-target`

Use this when linting one compiled target with its imports.

Best for:

- readability
- vague wording
- local contradiction
- weak names and descriptions
- exact truth hidden in prose
- unclear ownership
- missing stop lines

#### Good

```md
Target: `InterviewSummaryWriter`

Input packet:
- authored source for `InterviewSummaryWriter`
- emitted Markdown for `InterviewSummaryWriter`
- imported skill `SourceGrounding`
- typed output contract for the final summary
```

#### Bad

```md
Target: `InterviewSummaryWriter`

Input packet:
- the agent home only

Then ask the linter to judge contradiction, duplication across agents, and
whether the final output prose matches a contract it never saw.
```

### 5.2 `batch`

Use this when linting several compiled targets together.

Best for:

- repeated doctrine across agents
- repeated step lists
- handbook text copied into many role homes
- cross-agent contradiction
- local rules that should move into one shared skill or module

#### Good

```md
Batch targets:
- `InterviewSummaryWriter`
- `InterviewSummaryReviewer`
- `InterviewPlanWriter`

Shared packet:
- authored source for all three targets
- emitted Markdown for all three targets
- imported shared skills
- duplicate-block hints
```

#### Bad

```md
Batch targets:
- `InterviewSummaryWriter`
- `InterviewSummaryReviewer`
- `InterviewPlanWriter`

Input packet:
- only the emitted Markdown for `InterviewSummaryWriter`

Then ask the linter to find repeated law across all three agents.
```

## 6) Output Contract

Every finding should return:

- `code`
- `title`
- `severity`
- `confidence`
- `run_mode`
- `scope`
- `affected_targets`
- `principle_rule`
- `evidence`
- `why_it_matters`
- `recommended_fix`
- `fix_steps`
- `suggested_rewrite`
- `related_evidence`
- `good_example`
- `bad_example`

If the model cannot point to exact evidence, it must not emit the finding.

### 6.1 Best-In-Class Output Goals

The best linter output should do five things well:

- tell the developer fast if the run passed or failed
- show the most important fixes first
- prove each finding with exact evidence
- make cross-agent duplication easy to see
- stay stable enough for terminals, editors, CI, and JSON consumers

The output should never feel like a vague essay.
It should read like a strong linter: short summary first, then precise finding
cards, then machine-readable detail.

### 6.2 Default Render Layers

The linter should have four render layers.

#### Layer 1: run summary

Show:

- pass or fail
- targets linted
- count by severity
- top finding codes
- whether strict mode failed the run

#### Layer 2: actionable findings

Show the highest-severity findings first.
Within one severity, sort by the finding with the clearest fix first.

#### Layer 3: evidence and rewrite help

Each finding should show:

- the exact bad span
- any conflicting span
- why the linter thinks this is a problem
- the smallest credible fix
- a suggested rewrite when useful

#### Layer 4: machine output

Return the same findings in JSON so editors, CI, and custom tools can consume
them.

### 6.3 Finding Card Shape

The human-facing finding card should include:

- severity badge
- finding code and title
- affected target or targets
- one-sentence summary
- principle rule
- exact evidence
- why it matters
- recommended fix
- concrete fix steps
- suggested rewrite when useful
- good example
- bad example

For cross-agent duplication findings, add:

- all affected targets
- normalized repeated text
- shared owner recommendation

### 6.4 Helpful Defaults

By default, the linter should:

- group findings by severity
- collapse low-severity findings behind a summary if there are many
- show only one copy of the same duplicate block, then list the affected
  targets
- show contradiction findings side by side when two spans conflict
- show a rewrite suggestion for wording, readability, and stop-line findings
- show a shared extraction suggestion for duplication findings

### 6.5 Default Colorization

Terminal output should be colorized by default.

Recommended behavior:

- `--color=auto` is the default behavior
- use color whenever stdout is a TTY
- support `--color=always`
- support `--color=never`
- respect `NO_COLOR`

The output must not rely on color alone.
Every colored item must also have a text label.

Recommended portable color map:

| Item | Default style |
| --- | --- |
| pass summary | bold green |
| fail summary | bold red |
| `high` severity | bold red |
| `medium` severity | bold yellow |
| `low` severity | bold cyan |
| code id like `AL200` | bold magenta |
| file path or target name | underline |
| evidence label | bold white |
| fix label | bold green |
| warning note | bold yellow |
| good example label | green |
| bad example label | red |

Accessibility rules:

- always print labels such as `[HIGH]`, `[FIX]`, and `[EVIDENCE]`
- keep contrast strong on dark and light terminals
- never use red vs green alone to express meaning
- use indentation and grouping so monochrome output still reads cleanly

### 6.6 Exit Status

The linter should use simple exit codes:

- `0`: no findings at or above the fail threshold
- `1`: findings at or above the fail threshold
- `2`: linter execution failed, such as invalid packet or provider failure

The run summary should always say why the exit code was chosen.

### 6.7 Mockup: Concise Single-Target Terminal Output

In the mockups below, color tags show the intended default terminal colors.

```text
<red>[FAIL]</red> Doctrine agent linter found 3 findings in <underline>InterviewSummaryWriter</underline>

  <red>[HIGH]</red>   1
  <yellow>[MEDIUM]</yellow> 2
  <cyan>[LOW]</cyan>    0

Top codes:
  <magenta>AL800</magenta> Internal contradiction
  <magenta>AL400</magenta> Exact truth hidden in prose
  <magenta>AL720</magenta> Missing priority or stop line

Next actions:
  1. Fix the contradiction in the answer-length instruction
  2. Move exact final output requirements into the declared contract
  3. Add a stop line so the role does not widen scope

Run mode: single-target
Fail threshold: medium
Exit code: 1
```

Why this mockup is good:

- verdict first
- counts are easy to scan
- top codes are visible
- next actions are short and useful

### 6.8 Mockup: Expanded Single-Target Finding Card

```text
<red>[HIGH]</red> <magenta>AL800</magenta> Internal contradiction
Target: <underline>InterviewSummaryWriter</underline>
Principle: keep instructions consistent

Summary:
  The role tells the agent to keep the answer under five lines and also asks
  for a full, exhaustive analysis.

<white>[EVIDENCE A]</white>
  "Always keep the answer under five lines."

<white>[EVIDENCE B]</white>
  "Provide a full, exhaustive analysis of every interview theme."

Why this matters:
  These instructions pull in opposite directions. The agent cannot satisfy
  both reliably.

<green>[FIX]</green>
  Pick a default and state the exception clearly.

Fix steps:
  1. Keep the short-answer rule as the default
  2. Add an exception for cases where the user asks for depth
  3. Remove the word "always" if depth is sometimes required

Suggested rewrite:
  "Be concise by default. Go longer only when the user asks for depth."

Good example:
  "Be concise by default. Go longer only when the user asks for depth."

Bad example:
  "Always keep the answer under five lines. Provide a full, exhaustive
  analysis of every interview theme."
```

Why this mockup is good:

- the conflict is proven with two spans
- the fix is small and concrete
- the rewrite is ready to use

### 6.9 Mockup: Batch Duplication Finding

```text
<yellow>[MEDIUM]</yellow> <magenta>AL200</magenta> Duplicate rule across agents
Targets:
  - <underline>InterviewSummaryWriter</underline>
  - <underline>InterviewSummaryReviewer</underline>
  - <underline>InterviewPlanWriter</underline>
Run mode: batch

Summary:
  The same three-line evidence-check rule appears in three agents.

Normalized repeated text:
  "Check each claim against a source quote.
   Mark weak quotes.
   Remove unsupported claims."

Why this matters:
  This rule now has three owners. If one copy changes, the others can drift.

<green>[FIX]</green>
  Move this rule into one shared skill, then point each agent to that skill.

Shared owner suggestion:
  skill ClaimEvidenceCheck
  description: Verify that each draft claim has direct support from a source
  quote before the writer or reviewer finalizes work.

Affected spans:
  InterviewSummaryWriter: lines 18-20
  InterviewSummaryReviewer: lines 14-16
  InterviewPlanWriter: lines 22-24
```

Why this mockup is good:

- it shows one copy of the repeated text
- it names all affected targets
- it gives the developer a clear extraction direction

### 6.10 Mockup: Readability Finding With Rewrite Help

```text
<yellow>[MEDIUM]</yellow> <magenta>AL700</magenta> Reading level too high
Target: <underline>InterviewSummaryReviewer</underline>

Summary:
  One instruction block uses dense abstract language that is harder to read
  than it needs to be.

<white>[EVIDENCE]</white>
  "Downstream operators should independently operationalize the artifact-level
  implications of the present intervention."

Why this matters:
  Short, plain language is easier to review and easier to follow.

<green>[FIX]</green>
  Replace abstract nouns with direct verbs and split the sentence.

Suggested rewrite:
  "The next reviewer should understand what changed. They should know what to
  do next."
```

Why this mockup is good:

- the hard sentence is visible
- the rewrite is simpler
- the fix explains the writing move, not just the verdict

### 6.11 Mockup: Markdown Report

The linter should also support a markdown report for PR comments, saved
artifacts, or review docs.

```md
## Doctrine Agent Linter Report

- Verdict: fail
- Run mode: batch
- Targets: `InterviewSummaryWriter`, `InterviewSummaryReviewer`
- High: 1
- Medium: 2
- Low: 0

### Highest Priority

#### [HIGH] AL800 Internal contradiction

Target: `InterviewSummaryWriter`

Summary: The role gives incompatible length instructions.

Evidence:
- "Always keep the answer under five lines."
- "Provide a full, exhaustive analysis of every interview theme."

Recommended fix:
- keep short answers as the default
- add a clear exception for user-requested depth

Suggested rewrite:
> Be concise by default. Go longer only when the user asks for depth.
```

### 6.12 Mockup: JSON Output

The JSON output should carry the same truth as the terminal output.

```json
{
  "verdict": "fail",
  "run_mode": "batch",
  "fail_threshold": "medium",
  "counts": {
    "high": 1,
    "medium": 2,
    "low": 0
  },
  "targets": [
    "InterviewSummaryWriter",
    "InterviewSummaryReviewer"
  ],
  "findings": [
    {
      "code": "AL800",
      "title": "Internal contradiction",
      "severity": "high",
      "confidence": "high",
      "affected_targets": [
        "InterviewSummaryWriter"
      ],
      "principle_rule": "keep instructions consistent",
      "summary": "The role gives incompatible length instructions.",
      "evidence": [
        {
          "label": "A",
          "text": "Always keep the answer under five lines."
        },
        {
          "label": "B",
          "text": "Provide a full, exhaustive analysis of every interview theme."
        }
      ],
      "why_it_matters": "The agent cannot satisfy both instructions reliably.",
      "recommended_fix": "Keep one default rule and state the exception.",
      "fix_steps": [
        "Keep the short-answer rule as the default",
        "Add an exception for user-requested depth",
        "Remove the word 'always' if depth is sometimes required"
      ],
      "suggested_rewrite": "Be concise by default. Go longer only when the user asks for depth.",
      "good_example": "Be concise by default. Go longer only when the user asks for depth.",
      "bad_example": "Always keep the answer under five lines. Provide a full, exhaustive analysis of every interview theme."
    }
  ]
}
```

### 6.13 Best Possible Developer Experience

The output is best in class when a developer can do all of this without extra
guesswork:

- see in one screen whether the run failed
- know which finding to fix first
- see the exact bad text
- understand why it is bad
- copy a suggested rewrite when that helps
- understand which agents share a duplicate rule
- trust that the terminal output and JSON output match

## 7) Stable Code Bands

The core linter should use stable numbered codes.

| Band | Theme |
| --- | --- |
| `AL1xx` | context and load shape |
| `AL2xx` | duplication and reuse |
| `AL3xx` | runtime boundary and shadow authority |
| `AL4xx` | exact truth and declared constraints |
| `AL5xx` | role shape and handoffs |
| `AL6xx` | names and descriptions |
| `AL7xx` | readability and wording |
| `AL8xx` | contradiction and consistency |
| `AL9xx` | skill boundaries and law placement |

## 8) Core Finding Catalog

Each code below is part of the shipped Doctrine catalog.
Each one includes a real good example and a real bad example.

### `AL100` Oversized Always-On Context

#### What it means

The role home carries too much always-on text.
It reads like a handbook, not a thin role.

#### Why it matters

Context is a budget.
Large always-on text hides the real job and lowers signal.

#### Good

```md
You write the first draft of the customer interview summary.

Read first:
- the transcript
- the summary rubric skill

Leave behind:
- one draft summary
- one blocker note if a source quote is missing
```

#### Bad

```md
You write the first draft of the customer interview summary.

Before you start, read this full handbook:
- the full interview style guide
- the full editing guide
- the full quoting guide
- the full glossary
- the full archive of past summaries
- the full team review checklist

Keep all of this in mind on every turn.
```

#### Default recommendation

Move deep reference material into a shared skill, module, or docs index.
Keep the role home on job, inputs, and outputs.

### `AL110` Pasted Reference Instead Of Pointer

#### What it means

The author pasted long reference text into a role that should point at a shared
source.

#### Why it matters

Load depth on demand beats pasted handbooks.

#### Good

```md
Use the `InterviewQuotePolicy` skill for quote rules.
Do not restate the full quote policy here.
```

#### Bad

```md
Quote rules:
1. Keep quotes exact.
2. Mark cuts with brackets.
3. Never merge two speakers.
4. Keep timestamps when present.
5. Avoid long quotes unless needed.
6. Prefer short evidence-rich excerpts.

Repeat this same block in every writer and reviewer role.
```

#### Default recommendation

Replace pasted reference text with a pointer to one shared source.

### `AL120` Deep Procedure In The Role Home

#### What it means

The role home teaches a reusable method step by step instead of calling a
shared skill or module.

#### Why it matters

Repeated work should become reusable doctrine.

#### Good

```md
Use the `SourceGrounding` skill before you write claims from the transcript.
```

#### Bad

```md
Before you write any claim:
1. find the source quote
2. copy the quote into notes
3. mark the speaker
4. mark the time
5. compare the claim to the quote
6. remove the claim if the quote is weak

Keep this six-step method inside each role home.
```

#### Default recommendation

Move the reusable method into a skill.
Keep only the trigger and expected output in the role.

### `AL200` Duplicate Rule Across Agents

#### What it means

The same rule or step list appears in several agents in one batch run.

#### Why it matters

Reuse beats repetition.
One rule should have one owner.

#### Good

```md
Agent `InterviewSummaryWriter`:
Use the `EvidenceCheck` skill before you finalize the draft.

Agent `InterviewSummaryReviewer`:
Use the `EvidenceCheck` skill when you review factual claims.
```

#### Bad

```md
Agent `InterviewSummaryWriter`:
Check each claim against a source quote.
Mark weak quotes.
Remove unsupported claims.

Agent `InterviewSummaryReviewer`:
Check each claim against a source quote.
Mark weak quotes.
Remove unsupported claims.

Agent `InterviewPlanWriter`:
Check each claim against a source quote.
Mark weak quotes.
Remove unsupported claims.
```

#### Default recommendation

Lift the repeated rule into one shared skill or module.

### `AL210` Repeated Method Should Become A Skill

#### What it means

Several agents carry the same decision method, but the method has no shared
skill owner.

#### Why it matters

A repeated method is exactly what skills are for.

#### Good

```md
skill InterviewThemeClustering
description: Group similar interview findings into themes before drafting the
summary.

Writer role:
Use `InterviewThemeClustering` before you write the themes section.
```

#### Bad

```md
Writer role:
Group findings into themes by:
1. merging similar ideas
2. naming the pattern
3. keeping one quote per theme

Reviewer role:
Group findings into themes by:
1. merging similar ideas
2. naming the pattern
3. keeping one quote per theme
```

#### Default recommendation

Extract the shared method into a skill.

### `AL220` Repeated Background Block Across Agents

#### What it means

Several agent homes carry the same background briefing or glossary block.

#### Why it matters

Shared background should live once and load where needed.

#### Good

```md
Use the `InterviewContext` module for product background.
```

#### Bad

```md
Writer role:
Product background:
Our product helps distributed teams run user interviews...

Reviewer role:
Product background:
Our product helps distributed teams run user interviews...

Planner role:
Product background:
Our product helps distributed teams run user interviews...
```

#### Default recommendation

Move the shared background block into one importable module.

### `AL300` Runtime Boundary Leak

#### What it means

The prompt starts owning runtime state, scheduling, memory, or orchestration
that should not live in authored doctrine.

#### Why it matters

Doctrine should help author prompts, not become a second runtime.

#### Good

```md
If you need a missing runtime feature, note the gap.
Do not invent hidden state inside the prompt.
```

#### Bad

```md
Keep a private file named `session_state.md`.
Update it after every tool call.
Treat that file as the real source of truth for turn state, approvals, and
next actions.
```

#### Default recommendation

Remove runtime ownership from the prompt.
Leave it to the runtime or to a host-specific overlay.

### `AL310` Shadow Control Plane

#### What it means

The author created a second source of truth in prose that competes with a typed
or declared surface.

#### Why it matters

Exact truth should not have two owners.

#### Good

```md
Decision status comes from the declared review contract.
Do not add new status labels here.
```

#### Bad

```md
The review contract uses:
- `approve`
- `revise`
- `block`

But this prompt also says reviewers may return:
- `soft_pass`
- `needs_voice_work`
- `tentative_ok`
```

#### Default recommendation

Delete the shadow surface and keep one canonical owner.

### `AL400` Exact Truth Hidden In Prose

#### What it means

The prompt hides exact requirements in narrative prose instead of in a typed or
declared surface.

#### Why it matters

Exact truth belongs in a typed surface.
Prose should hold judgment, not machine-trustable facts.

#### Good

```md
Declared final output:
- `summary`: required markdown
- `key_quotes`: required list
- `risks`: optional list

Role text:
Use prose for why the strongest quote matters.
```

#### Bad

```md
Your final answer should usually include a summary and probably some key quotes.
Add risks if they seem important.
```

#### Default recommendation

Move exact requirements into the declared contract.

### `AL410` Prose Drift From Declared Constraints

#### What it means

The prompt text conflicts with exact constraints that were supplied in the
review packet.

#### Why it matters

If a caller gives exact declared constraints, prose should not widen or narrow
them by accident.

#### Good

```md
Declared constraints:
- allowed tools: `ReadFile`, `SearchDocs`

Role text:
Use the declared tools.
If something is missing, stop and note the gap.
```

#### Bad

```md
Declared constraints:
- allowed tools: `ReadFile`, `SearchDocs`

Role text:
Use any browser, shell, or external search tool that seems useful.
```

#### Default recommendation

Align the prose with the declared constraint surface.

### `AL500` Mixed Role Ownership

#### What it means

One role owns too many jobs.

#### Why it matters

Thin roles are easier to load, route, and trust.

#### Good

```md
You write the first draft of the interview summary.
Do not review or publish it.
Leave behind one draft file.
```

#### Bad

```md
You write the first draft, review factual accuracy, approve publication,
publish the final version, and message the team about the result.
```

#### Default recommendation

Narrow the role to one clear job and one clear output.

### `AL510` Missing Handoff Artifact

#### What it means

The role does not say what concrete artifact or blocker it must leave behind.

#### Why it matters

Downstream work should start from a real artifact, not a vague retelling.

#### Good

```md
Leave behind:
- `summary_draft.md`
- or one blocker note with the missing source quote
```

#### Bad

```md
When you are done, tell the next person what happened and what you think they
should do.
```

#### Default recommendation

Require a concrete artifact or a concrete blocker note.

### `AL520` Source Should Be Read, Not Remembered

#### What it means

The prompt tells the agent to work from memory or paraphrase when a real source
should be read.

#### Why it matters

Direct source beats remembered retelling.

#### Good

```md
Read the transcript before you write any claim about the interview.
```

#### Bad

```md
Write the summary from your memory of the interview.
If the transcript is long, trust your notes and fill any gaps.
```

#### Default recommendation

Point to the real source and remove memory-based fallback language.

### `AL600` Weak Resolver Name

#### What it means

A name is too vague to help a resolver or an author know what it is for.

#### Why it matters

Names should say what a thing does and when it should load.

#### Good

```md
skill ClaimEvidenceCheck
```

#### Bad

```md
skill GeneralHelper
```

#### Default recommendation

Rename it so the job and scope are clear.

### `AL610` Weak Description

#### What it means

A description does not explain purpose, trigger, or boundary.

#### Why it matters

Resolvers need short descriptions that help them choose the right thing.

#### Good

```md
description: Check whether each draft claim has direct evidence from the source
before the writer finalizes the summary.
```

#### Bad

```md
description: Helps with summary work.
```

#### Default recommendation

Rewrite the description with purpose, trigger, and limit.

### `AL700` Reading Level Too High

#### What it means

The prose is too hard to read for the active style target.
Many teams will set that target near grade 7.

#### Why it matters

Short, plain language is easier for humans to review and easier for models to
follow.

#### Good

```md
Start with the answer.
Use short sentences.
Name the file you changed.
Say what happens next.
```

#### Bad

```md
Downstream operators should be able to independently operationalize the
artifact-level implications of the present intervention without requiring
further interpretive mediation.
```

#### Default recommendation

Split long sentences and replace abstract words with common words.

### `AL710` Vague Wording

#### What it means

The prose uses vague verbs or nouns that hide the real action.

#### Why it matters

Vague wording makes roles wider and harder to follow.

#### Good

```md
Update `summary_draft.md` with three supported themes and one quote for each.
```

#### Bad

```md
Handle the summary materials carefully and make whatever updates seem
appropriate.
```

#### Default recommendation

Replace vague verbs with exact actions and name the artifact directly.

### `AL720` Missing Priority Or Stop Line

#### What it means

The prompt gives several goals but does not say which comes first or when to
stop.

#### Why it matters

Without a stop line, roles expand on their own.

#### Good

```md
First, fix unsupported claims.
If that is blocked, leave one blocker note and stop.
Do not rewrite tone in this role.
```

#### Bad

```md
Fix unsupported claims, improve tone, reorganize the summary, review the quote
policy, and clean up any other issues you notice.
```

#### Default recommendation

Order the work and add a clear stop rule.

### `AL800` Internal Contradiction

#### What it means

One surface gives incompatible instructions.

#### Why it matters

Conflicting rules cause unstable behavior.

#### Good

```md
Be concise by default.
Go longer only when the user asks for depth.
```

#### Bad

```md
Always keep the answer under five lines.
Provide a full, exhaustive analysis of every tradeoff.
```

#### Default recommendation

State the priority rule or split default behavior from exceptions.

### `AL810` Cross-Surface Contradiction

#### What it means

Two related surfaces disagree with each other.

#### Why it matters

Many real prompt failures only show up when two surfaces are read together.

#### Good

```md
Shared skill:
Check claims against source quotes.

Writer role:
Run the claim check skill before you finalize the draft.
```

#### Bad

```md
Shared skill:
Check claims against source quotes.

Writer role:
Do not spend time checking source quotes.
Trust your first reading and move fast.
```

#### Default recommendation

Align local text with the shared source of truth.

### `AL900` Skill Too Broad

#### What it means

One skill mixes several unrelated jobs or reads like a handbook.

#### Why it matters

Skills should be reusable and narrow enough to trigger clearly.

#### Good

```md
skill ThemeClustering
description: Group similar findings into themes before the writer drafts the
summary.
```

#### Bad

```md
skill SummaryMasterGuide
description: Covers planning, drafting, tone, citations, review, publishing,
stakeholder messaging, and any other summary work.
```

#### Default recommendation

Split the skill by job and keep one repeatable method per skill.

### `AL910` Shared Law Trapped In Local Text

#### What it means

One local role carries a rule that should be shared by many roles.

#### Why it matters

Shared law should live in a shared owner, not in one local prompt.

#### Good

```md
Shared module:
All customer-facing summaries must cite direct quotes for factual claims.

Writer role:
Follow the shared evidence rule.
```

#### Bad

```md
Writer role only:
All customer-facing summaries must cite direct quotes for factual claims.

Reviewer and planner roles repeat the same law in their own local wording.
```

#### Default recommendation

Lift the shared law into a shared module or skill.

## 9) Severity And Confidence

### 9.1 Severity

- `high`: likely to mislead the agent or create conflicting truth
- `medium`: likely to create drift, bloat, or poor reuse
- `low`: likely to reduce clarity, but lower risk

### 9.2 Confidence

- `high`: exact evidence and low ambiguity
- `medium`: strong evidence, but local intent might justify it
- `low`: weak signal; hide it by default

## 10) Prompt Rules For The Linter

The linter prompt should tell the model:

- You are not a compiler.
- You are not judging product correctness.
- You are reviewing authoring quality against the supplied Doctrine laws.
- You must cite exact evidence.
- You must prefer a few strong findings over many weak ones.
- You must not guess hidden runtime facts.
- You must not invent repo-local policy that is not in the review packet.

## 11) Hybrid Checks

Some checks work best when exact signals and LLM judgment work together.

### 11.1 Strong hybrid checks

- `AL100` oversized context
- `AL200` duplicate rule across agents
- `AL220` repeated background block
- `AL400` exact truth hidden in prose
- `AL410` prose drift from declared constraints
- `AL700` reading level too high

For these, deterministic helpers may provide:

- size stats
- duplicate-block hints
- declared constraints
- reading metrics
- target lists

### 11.2 Pure LLM-heavy checks

- `AL710` vague wording
- `AL720` missing priority or stop line
- `AL800` internal contradiction
- `AL810` cross-surface contradiction
- `AL900` skill too broad

## 12) Bottom Line

The right product is a Doctrine `agent linter`.

Its core catalog should stay generic for Doctrine users.
It should support one-target lint and batch lint.
It should use stable `AL###` codes.
And every finding should come with exact evidence, a clear rationale, and a
real good example and bad example.

# Appendix B) Conversion Notes

- This file was reformatted in place into the canonical arch-step artifact.
- The strongest new material lives in Sections `0)` through `10)`: owner paths,
  editor integration choice, live docs path, and the stronger compiler-vs-lint
  boundary.
- The previous detailed design content from `# 1)` onward was preserved in
  Appendix A with heading levels demoted so it stays inside the appendix.
- I did not preserve the previous top-level `# TL;DR` verbatim because its core
  claims were moved into the new canonical `# TL;DR` and Section `0)`.
- I did not run verify commands because this was a docs-only reformat pass.
