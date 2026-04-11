---
title: "Doctrine - Language Mechanics Full Implementation - Architecture Plan"
date: 2026-04-11
status: historical
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: architectural_change
related:
  - docs/LANGUAGE_MECHANICS_SPEC.md
  - docs/ANALYSIS_AND_SCHEMA_SPEC.md
  - docs/READABLE_MARKDOWN_SPEC.md
  - docs/INTEGRATION_SURFACES_SPEC.md
  - docs/SECOND_WAVE_LANGUAGE_NOTES.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/README.md
  - docs/COMPILER_ERRORS.md
  - examples/README.md
  - doctrine/grammars/doctrine.lark
  - doctrine/model.py
  - doctrine/parser.py
  - doctrine/compiler.py
  - doctrine/renderer.py
  - doctrine/verify_corpus.py
  - editors/vscode/README.md
  - editors/vscode/resolver.js
  - editors/vscode/syntaxes/doctrine.tmLanguage.json
  - editors/vscode/scripts/validate_lark_alignment.py
---

# TL;DR

## Outcome

Doctrine fully ships the language-mechanics wave described by
`docs/LANGUAGE_MECHANICS_SPEC.md` and its companion specs: first-class
`analysis`, first-class `schema`, first-class `document`, the readable block
sublanguage, `schema:` and `structure:` attachments, multiline strings,
compiler-owned diagnostics, manifest-backed example coverage, evergreen docs,
and full VS Code extension parity.

## Problem

The repo currently has a split between proposed language design and shipped
truth. The mechanics/spec documents describe a larger second language wave, but
the shipped grammar, model, compiler, renderer, example corpus, diagnostics
catalog, and VS Code extension still stop at the pre-`analysis` /
pre-`document` surface. Leaving that split in place keeps Doctrine half-taught,
keeps the editor out of sync with intended language growth, and makes the spec
wave impossible to verify end to end.

## Approach

Implement the full intended surface through the existing Doctrine owners only:
`doctrine/` for grammar, AST, compile, diagnostics, rendering, and verification;
`examples/` for proof; `docs/` for evergreen shipped truth; and
`editors/vscode/` for highlighting, navigation, alignment, packaging, and
tests. The plan must not scope down to the narrow first-wave subset. It must
hard-cut the full mechanics wave into one shipped language, reconcile the dual
example-ladder numbering into one canonical post-53 corpus, avoid diagnostic
code collisions, and keep one compiler path plus one editor parity path.

## Plan

1. Lock the exact shipped scope of the full mechanics wave and reconcile the
   two spec tracks into one canonical implementation order without creating
   parallel language truth.
2. Add the shared foundations required by the full wave: new grammar surfaces,
   multiline strings, a richer readable-block IR, addressable document nodes,
   and renderer/compiler plumbing that can own both documents and rich contract
   rendering.
3. Implement `document` plus readable block kinds and `structure:` attachments,
   then implement `analysis`, `schema`, and their integration surfaces,
   including inheritance, name resolution, diagnostics, and review/output
   coupling.
4. Extend the corpus with the full positive and negative example ladder,
   keeping manifest-backed proof and deterministic diagnostics.
5. Update evergreen docs so the shipped language reference, error catalog,
   examples guide, and editor docs describe the same reality as the compiler.

## Historical Note

This umbrella plan is retained as implementation history for the broader
mechanics wave. Do not read its baseline sections as current shipped truth for
readable markdown or `structure:` attachments.

Readable markdown, typed `structure:` attachments, their post-53 proof ladder,
and VS Code parity now ship through
`docs/DOCTRINE_READABLE_MARKDOWN_FULL_IMPLEMENTATION_2026-04-11.md` plus the
evergreen docs in `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, and
`docs/AGENT_IO_DESIGN_NOTES.md`.
6. Bring the VS Code extension to full parity with the shipped language and
   verify the whole cutover with repo-owned checks.

## Non-negotiables

- No scoping down to only `analysis` plus `schema`.
- No second readable-renderer path, editor parser, or shadow compiler surface.
- No domain-specific core primitives beyond the spec set already justified.
- No silent merge rules; inheritance, override, and addressability stay
  explicit and fail loud.
- No dual ownership of the same contract seam, including `schema:` plus local
  `must_include`.
- No diagnostic-code reuse that collides with current shipped meanings.
- No docs or editor claims that outrun shipped compiler truth.
- No partial feature wave where grammar ships without examples, docs, and VS
  Code support.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-11
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-11
recommended_flow: phase plan -> implement
note: This is a warn-first checklist only. It should not hard-block execution. Both deep-dive passes are now complete and `.codex/auto-plan-state.json` remains armed, so `phase-plan` is the next required controller step unless explicit external research is inserted first.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly, Doctrine will ship the full mechanics-spec
language wave as one coherent, verified, documented, and editor-supported
surface rather than as proposal-only docs:

- `.prompt` authors will be able to declare and compile `analysis`, `schema`,
  and `document`
- readable blocks such as `section`, `sequence`, `bullets`, `checklist`,
  `definitions`, `table`, `callout`, `code`, and `rule` will compile and render
  through one shipped path
- markdown-bearing contracts will support `schema:` and `structure:` where the
  specs intend them
- multiline string support will exist as a core language feature
- the numbered corpus will extend beyond example `53` with positive and
  compile-negative proof for the new surfaces
- evergreen docs and the VS Code extension will match shipped compiler truth

The claim is false if any major surface from the mechanics spec remains
proposal-only, if compiler/editor/docs truth diverge after the cutover, or if
the repo can only demo the new language through unchecked examples or stale
spec prose.

## 0.2 In scope

- Full implementation of the language surfaces named by
  `docs/LANGUAGE_MECHANICS_SPEC.md`:
  - `analysis`
  - `schema`
  - `document`
  - the readable block sublanguage
  - `schema:` on outputs
  - `structure:` on markdown-bearing inputs and outputs
  - multiline string support
- Shared compiler and renderer convergence needed to replace the current
  `CompiledSection`-only readable tree with a richer shipped readable-block
  model.
- Addressability, inheritance, name-resolution, and diagnostic work needed to
  make the new surfaces behave like Doctrine rather than like special-purpose
  sublanguages.
- Full example-corpus delivery for the new surface, including positive and
  compile-negative proof, with one canonical post-`53` numbering scheme.
- Evergreen doc updates across the shipped docs set so language reference,
  design notes, error docs, emit docs, and examples docs all describe the same
  shipped surface.
- Full VS Code extension parity across syntax highlighting, navigation,
  alignment validation, tests, packaging, and README truth.
- Architectural convergence required to keep one compiler owner path, one
  readable-render path, one diagnostic contract, and one editor parity path.

## 0.3 Out of scope

- Scoping down to the narrow first-wave recommendation when the user explicitly
  asked for the full intended mechanics wave.
- New lesson-specific, product-specific, or workflow-specific core primitives
  beyond what the mechanics/spec set already proposes.
- Runtime markdown validation of generated artifacts.
- New HTML-specific constructs, raw markdown escape hatches, footnotes, images,
  or nested tables in v1 where the specs explicitly reject them.
- A second VS Code architecture, extension surface, or alternate editor truth
  path.
- Compatibility shims, shadow diagnostics, or fallback renderers that keep old
  and new language worlds alive in parallel.
- Unrelated product behavior changes outside the Doctrine language, example
  corpus, live docs, verification surfaces, and editor tooling needed to ship
  this wave.

## 0.4 Definition of done (acceptance evidence)

- `doctrine/grammars/doctrine.lark`, `doctrine/model.py`,
  `doctrine/parser.py`, `doctrine/compiler.py`, and `doctrine/renderer.py`
  ship the full intended mechanics surface, not only a subset.
- The numbered example corpus includes the full new wave with manifest-backed
  proof and the planned negative cases for the readable-output/document system.
- `docs/LANGUAGE_REFERENCE.md`, `docs/README.md`, `docs/COMPILER_ERRORS.md`,
  `docs/EMIT_GUIDE.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, and
  `examples/README.md` reflect shipped truth after the cutover.
- The enhancement-spec docs are either updated to match shipped reality or
  clearly demoted from live-shipped truth so the repo does not keep competing
  explanations.
- For plan closure, `editors/vscode/` must support the shipped language surface
  and `cd editors/vscode && make` must pass.
- Repo verification passes at the appropriate checkpoints, including:
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics change
  - targeted manifest-backed runs while developing the new ladder
  - `cd editors/vscode && make`

Behavior-preservation evidence:

- the shipped corpus through example `53` remains green unless an explicitly
  justified bug fix changes behavior
- diagnostics remain fail-loud and deterministic, with no reuse of current
  shipped error-code meanings
- the editor continues to resolve and highlight previously shipped surfaces
  correctly while expanding to the new ones

## 0.5 Key invariants (fix immediately if violated)

- One owner per seam.
- One live route per seam.
- No dual sources of truth between shipped code, live docs, examples, and the
  VS Code extension.
- Keys are law; titles are prose.
- Inheritance and override stay explicit-accounting surfaces.
- The new language surfaces must feel like Doctrine, not embedded
  mini-languages with separate rules.
- No fallback renderer, no shadow compiler path, and no shadow editor grammar.
- No `schema:` plus local `must_include` dual ownership.
- No diagnostic-number collisions with already shipped parse, compile, or emit
  codes.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Ship the full intended mechanics wave, not a narrowed subset.
2. Keep one coherent compiler, renderer, corpus, docs, and editor story.
3. Preserve the existing shipped language through example `53` while expanding
   the surface.
4. Keep inheritance, addressability, and diagnostics explicit and fail loud.
5. Avoid rework by converging on one readable-block architecture rather than
   layering ad hoc special cases.

## 1.2 Constraints

- The current grammar does not declare `analysis`, `schema`, or `document`.
- The current renderer is still a `CompiledSection`-only heading renderer.
- The mechanics spec proposes diagnostic ranges that currently collide with
  shipped emit codes.
- The two proposed example ladders overlap numerically and cannot both ship as
  written without reconciliation.
- The VS Code extension mirrors shipped grammar and clickable surfaces
  manually, so compiler changes require explicit editor follow-through.

## 1.3 Architectural principles (rules we will enforce)

- Shipped Doctrine code remains the source of truth.
- Reuse existing Doctrine mechanics before inventing a new merge model or
  sublanguage rule.
- Prefer one foundational readable-block IR over multiple one-off render
  structures.
- Keep editor parity tied to shipped grammar, not to stale docs or speculative
  syntax.
- Delete or rewrite stale live truth surfaces in the same wave rather than
  leaving competing explanations behind.

## 1.4 Known tradeoffs (explicit)

- Shipping the full wave in one architecture effort is more work up front than
  landing only `analysis` and `schema`, but it avoids a second disruptive
  compiler/renderer/editor rewrite later.
- Reconciling the dual example ladders into one shipped sequence may require
  renumbering or folding planned examples relative to the proposal docs.
- A richer readable-block IR increases compiler and editor surface area, but it
  is the cleanest way to ship `document`, rich contract rendering, and
  multiline `code` blocks without special cases.

# 2) Problem Statement (existing architecture + why change)

## 2.1 Historical baseline when this umbrella plan was opened

When this umbrella plan was opened, the repo had a real split between shipped
language truth and intended next-wave design. The split specs existed under
`docs/`, but the shipped language reference still described the pre-wave
surface, the core grammar/model/compiler did not yet implement the full new
declaration set, the example corpus stopped at `53`, and the VS Code extension
only mirrored the then-shipped language.

## 2.2 Historical gaps at plan open (concrete)

- At plan open, authors could not yet declare the full mechanics-spec surfaces
  in shipped Doctrine.
- At plan open, the spec set described behaviors that the compiler,
  diagnostics, examples, and editor did not yet prove.
- At plan open, the readable rendering architecture was too narrow for the
  full `document` / rich-block design.
- At plan open, diagnostic numbering proposed by the spec was not aligned with
  then-current shipped emit code usage.
- At plan open, the post-`53` example wave was not shipped, so the language
  growth was not yet example-first in Doctrine’s own standard.

## 2.3 Constraints implied by the problem

The fix has to be a hard-cutover shipped-language wave through the existing
owners. Partial compiler work without corpus/doc/editor completion would leave
Doctrine in a worse split-brain state, and editor/doc follow-through is part of
the requested behavior rather than optional polish.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- Repo-local split spec set under `docs/` — adopt as the primary intent source
  for this work, because the ask is to ship Doctrine's intended mechanics wave
  faithfully rather than to design a different language. External typed-markdown
  prior art may still be useful later, but only if it sharpens Doctrine's owned
  design without weakening the current spec set or expanding the public
  language surface.

## 3.2 Historical internal baseline at plan open (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/grammars/doctrine.lark` — at plan open, the shipped declaration
    surface still stopped at the pre-`analysis` / pre-`schema` /
    pre-`document` language,
    with `workflow`, `review`, typed IO, `skill`, and `enum` as top-level
    declarations.
  - `doctrine/model.py` — at plan open, the shipped AST and IR model still had
    no
    `AnalysisDecl`, `SchemaDecl`, `DocumentDecl`, or multiline-string node.
  - `doctrine/compiler.py` — at plan open, shipped compilation still resolved
    inheritance and addressability through the current workflow / skills / IO /
    review machinery and still compiled readable output through a
    `CompiledSection` tree.
  - `doctrine/renderer.py` — at plan open, shipped Markdown emission was still
    a heading-recursive `CompiledSection` renderer, so the full readable-block
    wave needed a foundational render-model expansion instead of ad hoc block
    hacks.
  - `doctrine/diagnostics.py` and `docs/COMPILER_ERRORS.md` — shipped emit
    diagnostics already occupy `E501` through `E516`, so the mechanics-spec
    proposal to reserve `E501-E519` for `analysis` collides with current live
    meanings and must be renumbered rather than reused.
  - `examples/README.md` and `doctrine/verify_corpus.py` — at plan open, the
    live proof corpus ended at `53_review_bound_carrier_roots`, and manifests
    were the proof surface. Any new language wave had to extend that corpus
    with manifest-backed proof rather than with unchecked examples alone.
  - `docs/README.md` — at plan open, the live docs explicitly classified the
    mechanics/spec documents as implementation-grade design specs, not shipped
    language truth, so the cutover had to either promote the shipped docs to
    cover the new surface fully or demote competing design prose cleanly.
  - `editors/vscode/resolver.js`,
    `editors/vscode/syntaxes/doctrine.tmLanguage.json`, and
    `editors/vscode/scripts/validate_lark_alignment.py` — at plan open, the VS
    Code extension was a hand-maintained shipped mirror of grammar keywords,
    clickable surfaces, and structural parsing. It had to be updated in the
    same wave as the compiler.
  - `~/.codex/hooks.json` plus
    `~/.agents/skills/arch-step/scripts/implement_loop_stop_hook.py` — the
    installed automatic controller path for `auto-plan` / `implement-loop`,
    which is present in this environment and matters for honest controller
    execution.
- Canonical path / owner to reuse:
  - `doctrine/` — the one shipped language owner for grammar, parser, model,
    compiler, diagnostics, renderer, and verification.
  - `examples/` — the one shipped proof owner for new syntax and diagnostics.
  - `docs/` — the one evergreen explanation owner after the cutover.
  - `editors/vscode/` — the one shipped editor parity owner.
- Existing patterns to reuse:
  - `doctrine/compiler.py` workflow / skills / IO / review inheritance paths —
    existing explicit-accounting patching model that the mechanics wave is
    supposed to reuse instead of replacing with new merge disciplines.
  - `doctrine/compiler.py` addressable-ref resolution — existing root-plus-path
    resolution model that `analysis`, `schema`, and `document` should extend.
  - `doctrine/verify_corpus.py` manifest and compile-fail case machinery —
    existing proof path for positive and negative language cases.
  - `editors/vscode/scripts/validate_lark_alignment.py` — existing grammar to
    editor keyword-alignment safeguard that should expand with the new surface
    instead of being bypassed.
- Duplicate or drifting paths relevant to this change:
  - `docs/LANGUAGE_MECHANICS_SPEC.md`,
    `docs/ANALYSIS_AND_SCHEMA_SPEC.md`,
    `docs/READABLE_MARKDOWN_SPEC.md`,
    `docs/INTEGRATION_SURFACES_SPEC.md`, and
    `docs/SECOND_WAVE_LANGUAGE_NOTES.md` currently describe intended language
    behavior that the shipped compiler does not yet implement.
  - `editors/vscode/resolver.js` already recognizes a keyed `schema:` reference
    surface even though the shipped grammar does not yet support `schema:` on
    `output`, which is a real compiler/editor drift point to resolve during the
    cutover.
- Capability-first opportunities before new tooling:
  - Use the existing compiler, verifier, and extension package/test owners;
    this wave does not need a new harness, wrapper, or second parser surface.
  - Extend the existing readable rendering path and extension mirror instead of
    inventing separate document-only or editor-only architectures.
- Behavior-preservation signals already available:
  - `make verify-examples` — shipped corpus preservation signal.
  - `make verify-diagnostics` — stable diagnostic-surface preservation signal
    when diagnostics change.
  - `uv run --locked python -m doctrine.verify_corpus --manifest <cases.toml>`
    — narrow manifest-backed proof while the new ladder is under construction.
  - `cd editors/vscode && make` — extension unit/integration/alignment/package
    preservation signal.

## 3.3 Open questions (evidence-based)

- What is the cleanest single implementation order for the full wave: shared
  readable-block IR first, then multiline strings, then `document`, then
  reusable rich blocks in records/workflows, then `analysis` and `schema`, or a
  different but still one-path sequence? — settled by deeper compiler and
  renderer call-site audit.
- What exact replacement diagnostic bands should `analysis` and `schema` use
  now that `E501-E516` are already live emit codes? — settled by diagnostics
  audit plus live error-catalog update plan.
- What is the canonical post-`53` example numbering and whether the two
  proposal ladders should be merged, renumbered, or partially folded together?
  — settled by corpus and docs audit.
- Which enhancement-spec docs remain evergreen design references after ship and
  which shipped docs must absorb their content directly? — settled by doc-truth
  audit in deep-dive and phase-plan.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

The current shipped owner paths are already clear, but they stop before the
mechanics wave:

- `doctrine/grammars/doctrine.lark`
  - shipped top-level declarations are `workflow`, `review`, typed IO blocks,
    `json schema`, `skill`, `enum`, and agents
  - strings are still `ESCAPED_STRING` only
  - `output_body` still only admits record items plus `trust_surface`
  - there is no shipped `analysis`, `schema`, `document`, shared readable-block
    grammar, or `structure:` attachment surface
- `doctrine/model.py` and `doctrine/parser.py`
  - own the current AST for workflows, reviews, record bodies, guarded output
    sections, addressable refs, enums, and typed IO
  - have no first-class AST for documents, readable block kinds, schema
    sections/gates, analysis statements, or multiline string literals
- `doctrine/compiler.py` and `doctrine/renderer.py`
  - already ship the current scalable compile-session architecture
  - still compile readable output into a `CompiledSection` tree and render it by
    recursive heading emission
- `examples/` and `doctrine/verify_corpus.py`
  - own the manifest-backed proof corpus through
    `53_review_bound_carrier_roots`
  - do not yet contain the mechanics-wave ladder
- `docs/`
  - split shipped truth (`LANGUAGE_REFERENCE.md`, `COMPILER_ERRORS.md`, etc.)
    from implementation-grade enhancement specs
  - still present the enhancement-spec set in the live docs index
- `editors/vscode/`
  - owns TextMate colorization, on-enter indentation rules, regex/index-based
    definition resolution, package/test wiring, and the editor README

## 4.2 Control paths (runtime)

Current shipped control paths are:

1. `doctrine/parser.py:parse_file()` parses one entrypoint against
   `doctrine/grammars/doctrine.lark`.
2. `doctrine/compiler.py:CompilationSession` indexes the prompt graph once per
   session and exposes `compile_agent()`, `compile_agents()`, and
   `extract_target_flow_graph()`.
3. `doctrine/compiler.py:CompilationContext` is task-local and owns semantic
   resolution, inheritance, addressability, review semantics, and compiled
   output construction against the session-owned graph.
4. `CompilationSession.compile_agents()` already fans out root-agent
   compilation across worker threads while preserving authored target order,
   and `doctrine/verify_corpus.py` already uses a session cache rather than
   rebuilding the graph per compile-bearing case.
5. `doctrine/renderer.py:render_markdown()` still assumes every readable node is
   either prose or `CompiledSection`, so rich block rendering does not exist yet.
6. `doctrine/emit_docs.py` and `doctrine/emit_flow.py` already reuse
   `CompilationSession`; `doctrine/verify_corpus.py` already reuses sessions for
   compile-bearing cases through `_CompilationSessionCache`.
7. `editors/vscode/extension.js` wires only two providers over
   `resolver.js`:
   import links and Go to Definition. Colorization is fully TextMate-based, and
   indentation is controlled by `language-configuration.json`.

So the repo is not on a pre-session compiler anymore. The real current gap is
the language surface and readable rendering model, not the absence of a shared
compile owner.

## 4.3 Object model + key abstractions

The current abstractions matter because the mechanics wave must extend them,
not bypass them:

- current AST/body families are separate:
  - `workflow_body`
  - `skills_body`
  - `io_body`
  - `record_body`
  - `output_body`
  These surfaces reuse some pieces, but there is no shared typed readable-block
  AST yet
- current readable compile IR is narrow:
  - `CompiledAgent` fields are `RoleScalar | CompiledSection`
  - `CompiledBodyItem` is `ProseLine | CompiledSection`
  - rich blocks such as tables, checklists, callouts, code blocks, and rules do
    not have compiled node types
- current addressability system is already broad and reusable:
  - `AddressableRef` exists in the AST
  - `IndexedUnit`, `AddressableRootDecl`, `_resolve_addressable_root_decl()`,
    and `_get_addressable_children()` already drive readable refs, path refs,
    interpolation, enum members, and review semantic roots
  - there is no document/schema/analysis root support yet
- current review contract model is workflow-only:
  - review contracts resolve against workflow section keys and exported gates
  - there is no schema-contract branch yet
- current VS Code resolver duplicates a simplified structural parser:
  - `DECLARATION_DEFINITIONS`
  - `getPromptIndex()`
  - `get*BodyItems()` helpers
  - regex site collectors such as `KEYED_DECL_REF_RE`
  This means editor parity work is real compiler-followthrough work, not just
  README cleanup

## 4.4 Observability + failure behavior today

- Fail-loud behavior is already a shipped Doctrine principle:
  parse errors, compile errors, review errors, and emit errors normalize into
  stable diagnostics and are cataloged in `docs/COMPILER_ERRORS.md`
- current diagnostic bands already reserve:
  - `E200-E469` for compile
  - `E470-E499` for review
  - `E500-E699` for emit/build
  So the mechanics-spec proposal to reserve `E501-E519` for `analysis`
  conflicts with live shipped meanings and cannot survive as written
- `make verify-examples` and manifest-backed refs are the primary proof surface
- `make verify-diagnostics` exists when diagnostic wording or bands change
- The intended extension-level closure signal for this plan is
  `cd editors/vscode && make`, which packages the extension through unit,
  snapshot, integration, and Lark-alignment checks once the editor wave is
  green
- one real current drift point already exists:
  `editors/vscode/resolver.js` treats `schema:` as a clickable keyed ref even
  though the shipped compiler grammar does not yet admit `output schema:`

## 4.5 UI surfaces (ASCII mockups, if UI work)

The shipped editor surface is intentionally narrow and should remain so:

- colorization: `syntaxes/doctrine.tmLanguage.json`
- indentation / Enter behavior: `language-configuration.json`
- navigation: `resolver.js` through `extension.js`
- verification: `tests/unit`, `tests/snap`, `tests/integration`,
  `scripts/validate_lark_alignment.py`
- non-goals today: no hover, completion, rename, symbol search, or language
  server
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

The cutover keeps the same canonical owner paths and extends them in place:

- `doctrine/grammars/doctrine.lark`
  - add top-level declarations:
    - `analysis`
    - `schema`
    - `document`
  - add shared readable-block productions for:
    - `section`
    - `sequence`
    - `bullets`
    - `checklist`
    - `definitions`
    - `table`
    - `callout`
    - `code`
    - `rule`
  - add `schema:` on `output`
  - add `structure:` on markdown-bearing `input` and `output`
  - add multiline string syntax as a core literal feature
- `doctrine/model.py` and `doctrine/parser.py`
  - add first-class AST for `analysis`, `schema`, `document`, readable blocks,
    attachments, and multiline strings
- `doctrine/compiler.py` and `doctrine/renderer.py`
  - keep `CompilationSession` as the one compiler owner
  - replace the section-only readable compile model with a richer readable-block
    union and renderer dispatch path
- `examples/`
  - ship one canonical post-`53` ladder:
    - `54_first_class_documents`
    - `55_rich_blocks_in_output_contracts`
    - `56_documents_with_tables_and_definitions`
    - `57_document_inheritance`
    - `58_document_guards`
    - `59_multiline_strings_and_code_blocks`
    - `60_analysis_basic`
    - `61_analysis_classify_compare`
    - `62_schema_output_contract`
    - `63_schema_inheritance`
    - `64_lessons_lesson_architect_capstone`
    - `65_lessons_section_architecture_capstone`
    - `66_schema_review_contract`
- `docs/`
  - promote the shipped language docs to cover the new surface directly
  - remove the enhancement-spec set from the live docs path once the cutover is
    shipped, either by archiving it or by reclassifying it explicitly as
    historical design material
- `editors/vscode/`
  - keep the current package architecture and provider wiring
  - extend syntax, indentation, navigation, tests, and README truth for the
    new language

## 5.2 Control paths (future)

The future runtime path is one extended Doctrine pipeline:

1. `parse_file()` parses old and new declarations plus multiline strings.
2. `CompilationSession` remains the one session owner and indexes the new
   declaration registries alongside the existing ones.
3. `CompilationContext` remains the task-local semantic owner and extends:
   - inheritance and override resolution for `analysis`, `schema`, and
     `document`
   - addressable-root and child resolution for document descendants, schema
     sections/gates, and analysis sections
   - output `schema:` resolution, where `schema:` resolves only to a top-level
     `schema` declaration
   - markdown-bearing input/output `structure:` resolution, where `structure:`
     resolves only to a top-level `document`
   - review contract branching so `contract:` can target either a workflow or a
     schema
4. Readable compilation no longer bottoms out at `CompiledSection` recursion.
   Instead, all shipped readable surfaces compile to a richer readable-block IR:
   ordinary sections become one block kind inside that IR, not a separate
   rendering system.
5. `render_markdown()` dispatches by block kind:
   heading sections, ordered/unordered lists, checklists, definitions, tables,
   callouts, rules, fenced code with multiline text, natural-sentence analysis
   statements, and schema section inventories.
6. `emit_docs.py`, `emit_flow.py`, and `verify_corpus.py` continue to consume
   the same compiler path and therefore inherit the new language without adding
   alternate wrappers.
7. The VS Code extension continues its current split:
   tmLanguage for tokenization, resolver for navigation, package/test harnesses
   for parity. No second editor architecture is introduced.

## 5.3 Object model + abstractions (future)

Target shipped abstractions:

- AST additions in `doctrine/model.py`
  - `AnalysisDecl`, `AnalysisBody`, `AnalysisSection`,
    `AnalysisInherit`, `AnalysisOverrideSection`
  - `DeriveStmt`, `ClassifyStmt`, `CompareStmt`, `DefendStmt`
  - `SchemaDecl`, `SchemaBody`, `SchemaSection`, `SchemaGate`,
    `OutputSchemaConfig`
  - `DocumentDecl` plus per-block node types for all readable blocks
  - `InputStructureConfig` / `OutputStructureConfig` or equivalent attachment
    nodes
  - multiline string node or equivalent normalized literal carrier
- compile-time IR additions in `doctrine/compiler.py`
  - a compiled readable-block union that can represent both legacy section
    recursion and the new typed blocks
  - document addressable roots and descendants
  - schema gate identity when a review contract targets a schema
- renderer additions in `doctrine/renderer.py`
  - block-dispatch rendering instead of heading-only recursion
  - natural-sentence analysis lowering
  - schema inventory lowering

`CompiledSection` may survive as a compatibility struct only if it becomes the
`section` variant or a thin wrapper around the new readable-block IR. It must
not remain a second rendering semantics path. The preferred outcome is one
explicit readable-block family in the compiler and renderer, with `section`
treated as one block kind rather than as a parallel legacy tree.

## 5.4 Invariants and boundaries

- Extend the existing `CompilationSession`; do not invent a second compiler
  owner path.
- Keep one readable-render path across workflows, documents, and structured IO.
- Keep one canonical post-`53` example sequence: `54` through `66` as listed
  above.
- Preserve shipped diagnostic meanings and allocate new compile bands below the
  emit range:
  - `E385-E399` for `analysis`
  - `E400-E419` for `schema`
  - `E420-E449` for `document`, readable-output validation, `structure:`, and
    multiline/readable-block validation
- Keep review codes in `E470-E499` and emit/build codes in `E500-E699`
  unchanged in meaning.
- Keep attachment ownership explicit:
  - `output schema:` must resolve only to a `schema`
  - markdown-bearing `structure:` must resolve only to a `document`
  - `schema:` plus local `must_include` remains a hard compile error in this
    wave
  - document-block `when` guards obey the same source restrictions as guarded
    outputs rather than inventing a second guard discipline
- Keep the evergreen docs cutover explicit:
  once the wave ships, `docs/README.md` must route readers to the shipped
  reference/docs path, while the enhancement specs move to historical design
  context instead of remaining first-class live-language docs.
- Keep the current VS Code extension architecture:
  no language server, no parallel parser, no new provider surface unless the
  compiler parity work truly forces it.
- The mechanics-spec doc’s explicitly explored controls
  (`properties`, standalone `guard`, `render_profile`) do not become
  ship-blocking unless the doc-truth audit explicitly promotes them; the core
  cutover ships the concrete surfaces already specified by the split spec set.

## 5.5 UI surfaces (ASCII mockups, if UI work)

After the cutover, the VS Code extension should support:

- declaration highlighting for `analysis`, `schema`, and `document`
- keyword highlighting for readable block kinds and multiline strings
- Ctrl/Cmd-click and Go to Definition on:
  - `analysis`, `schema`, and `document` refs
  - `output schema:` refs
  - `input/output structure:` refs
  - structural `inherit` / `override` keys in the new declarations
  - document path roots and descendants, including table columns and keyed rows
    when authored
  - schema gates through `contract.<gate>` when the review contract is a schema
- updated on-enter indentation for new declaration headers and readable-block
  bodies

The extension still does not grow hover, completion, rename, or a language
server in this wave.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar: top-level declarations | `doctrine/grammars/doctrine.lark` | `?declaration`, top-level `*_decl` rules | shipped grammar stops at current declarations and `json schema` | add `analysis`, `schema`, `document` declarations and inheritance forms | core language surface is missing | top-level declaration contract widens without adding a second grammar | `make verify-examples`, VS Code alignment |
| Grammar: readable blocks | `doctrine/grammars/doctrine.lark` | body rules such as `workflow_body`, `record_body`, `output_body` | current bodies only know prose, current keyed sections, refs, and guarded output | introduce shared readable-block grammar and thread it into `document` plus markdown-bearing contract surfaces | avoid one-off mini-languages and renderer hacks | one shared readable-block sublanguage | new examples `54-59`, VS Code tests |
| Grammar: literals and attachments | `doctrine/grammars/doctrine.lark` | `string`, output/input fields, review contract rule | strings are single-line only; no `schema:` / `structure:`; review contract is workflow-only | add multiline strings, `output schema:`, markdown-bearing `structure:`, and schema-aware review contract parsing | these are explicit mechanics/spec surfaces | attachment and contract grammar surfaces widen | examples, diagnostics, VS Code alignment |
| AST model | `doctrine/model.py` | declaration and block dataclasses | no AST for `analysis`, `schema`, `document`, readable blocks, or multiline strings | add first-class nodes and attachment configs | compiler and editor parity need concrete node types | new AST contract for all new surfaces | parser/compile verification |
| Parser transforms | `doctrine/parser.py` | declaration builders, body builders, attachment parsing | parser only builds current workflow/review/IO/record shapes | add builders for new declarations, block nodes, multiline strings, and attachments | shipped grammar must become shipped AST | parser output matches the widened grammar | example manifests, diagnostics |
| Compiler: indexing and decl lookup | `doctrine/compiler.py` | `IndexedUnit`, `_index_unit()`, declaration registries, root matching | session graph only indexes current decl kinds | register `analysis`, `schema`, and `document` in the session graph and decl lookup paths | new declarations must be imported, resolved, and addressable | widened indexed-unit contract | all new examples |
| Compiler: inheritance and name resolution | `doctrine/compiler.py` | workflow/skills/IO/review patching helpers, decl-ref resolution | current explicit-accounting patching exists only for current decl families | add explicit-accounting resolution for analysis/schema/document without inventing a new merge discipline | mechanics wave must feel like Doctrine | new inheritance/override contract | positive and negative corpus |
| Compiler: readable IR and renderer handoff | `doctrine/compiler.py`, `doctrine/renderer.py` | `CompiledSection`, `CompiledBodyItem`, `render_markdown()` | readable output bottoms out at sections only | add richer compiled readable-block union and renderer dispatch, retire section-only semantics as the sole path | documents, tables, checklists, callouts, code, and rules cannot ship otherwise | one readable IR and one renderer path | `54-59`, emit/verify consumers |
| Compiler: addressability | `doctrine/compiler.py` | `_resolve_addressable_root_decl()`, `_get_addressable_children()` | roots/children cover current declarations, records, workflows, skills, enums, and review semantics | add roots and descendants for `document`, `analysis`, and `schema`, including table columns, rows, and schema gates | path refs and interpolation are part of the shipped contract | widened addressability contract | new examples, diagnostics, VS Code navigation |
| Compiler: outputs / inputs / review integration | `doctrine/compiler.py` | `_compile_output_decl()`, IO resolution, review contract resolution | no `schema:` / `structure:`; review contract only understands workflow gates | compile schema-backed outputs, structure-backed markdown contracts, and workflow-or-schema review contracts | core integration surfaces are missing | output/input/review integration contract widens | `62-66`, docs, editor |
| Compiler: readable validation | `doctrine/compiler.py` | guarded readable-block compilation, attachment validation, schema gate resolution | no document-block guard rules, no `schema` plus `must_include` prohibition, no schema-gate review validation | enforce `structure -> document`, `schema -> schema`, document guard-source restrictions, `schema` plus `must_include` prohibition, and schema-gate validation for review contracts | the wave must fail loud on the same surfaces the specs make explicit | readable/document/schema validation contract | negative corpus, diagnostics |
| Diagnostics engine | `doctrine/diagnostics.py` | compile-error normalization tables | no code family for analysis/schema/document; mechanics spec collides with emit codes | add new stable compile codes and summaries for new surfaces without changing existing emit meanings | fail-loud diagnostics are shipped truth | new diagnostic code bands below `E500` | `make verify-diagnostics`, negative corpus |
| Error catalog | `docs/COMPILER_ERRORS.md` | code bands and stable code table | live catalog stops before mechanics-wave codes | document new parse/compile bands and preserve current meanings for emit/review | docs must match shipped errors | canonical error catalog expands | `make verify-diagnostics` |
| Corpus: positive ladder | `examples/README.md`, new `examples/54_*` through `examples/66_*` | corpus index and manifests | live corpus ends at `53` | add one canonical post-`53` ladder with manifests, refs, and build refs where needed | Doctrine grows example-first | shipped proof sequence extends cleanly | `make verify-examples` |
| Corpus: negative proof | new example manifests / refs | compile-fail and validation cases | readable-output/document negatives are only named in specs | add explicit compile-negative proof for bad `structure:` refs, bad `schema:` refs, `schema` plus `must_include`, document key conflicts, document guard source violations, table/callout/code validation, and unknown schema review gates | fail-loud behavior needs proof | negative corpus for new surfaces | `make verify-examples`, diagnostics |
| Shipped language docs | `docs/LANGUAGE_REFERENCE.md`, `docs/README.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `examples/README.md` | live docs index and reference content | live docs still describe pre-wave shipped language and enhancement specs separately | absorb shipped language truth into evergreen docs and remove enhancement specs from the live docs path | no competing truth surfaces after ship | evergreen docs become canonical again | doc review |
| Surface-specific docs | `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/REVIEW_SPEC.md`, `docs/EMIT_GUIDE.md` | IO/review/emit guidance | these docs do not yet describe `structure:`, schema-backed outputs, or schema-backed review contracts | update only the surfaces that change in shipped behavior | keep docs synchronized to shipped semantics | updated live-surface docs | doc review |
| Enhancement-spec disposition | `docs/ANALYSIS_AND_SCHEMA_SPEC.md`, `docs/READABLE_MARKDOWN_SPEC.md`, `docs/INTEGRATION_SURFACES_SPEC.md`, `docs/LANGUAGE_MECHANICS_SPEC.md`, `docs/SECOND_WAVE_LANGUAGE_NOTES.md` | currently indexed as language enhancement specs | they currently sit in the live docs path while the feature is unshipped | archive, demote, or explicitly reclassify after ship so they do not compete with evergreen docs | avoid split-brain documentation | one live docs path, one historical design path | docs/README review |
| Emit / verify consumers | `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, `doctrine/verify_corpus.py` | current compiler consumers | already reuse `CompilationSession` and current renderer | update only where the widened renderer/verify path requires it; keep same public surfaces | avoid wrapper drift while shipping new language | consumer parity over same compiler path | examples, emit smoke |
| Emit config plumbing | `doctrine/emit_common.py` | emit-target loading, entrypoint validation, output naming | emit config parsing is language-agnostic and already stable | keep unchanged unless a widened renderer contract forces narrow comment/doc touch-ups | this wave should not invent a new emit config model | no new emit-target contract | existing emit checks only |
| VS Code syntax and indentation | `editors/vscode/syntaxes/doctrine.tmLanguage.json`, `editors/vscode/language-configuration.json`, `editors/vscode/scripts/validate_lark_alignment.py` | keywords, declaration headers, on-enter rules, keyword alignment | grammar mirror stops at shipped pre-wave language and hardcodes current header/body starters | add new declarations, block kinds, multiline strings, and body starters; keep keyword-alignment validator honest | syntax parity is in scope | richer tmLanguage/indent/alignment contract | `cd editors/vscode && make` |
| VS Code navigation | `editors/vscode/resolver.js` | declaration indexing, site collection, body-item parsers, addressable path traversal | resolver mirrors current declarations and addressable surfaces only; already has one premature `schema:` path | add analysis/schema/document declarations, attachments, structural keys, and document descendants; align `schema:` with actual compiler truth | clickable parity is in scope | widened resolver contract on same architecture | VS Code integration + unit tests |
| VS Code package/test/docs | `editors/vscode/package.json`, `editors/vscode/Makefile`, `editors/vscode/tests/**`, `editors/vscode/README.md`, `editors/vscode/extension.js` | package flow, tests, README smoke guidance, provider wiring | tests and README stop at current shipped language; provider wiring is intentionally narrow | add coverage and README truth for new surfaces; keep provider wiring unless the compiler parity work truly requires more | avoid needless editor architecture churn | same extension shell, broader shipped behavior | `cd editors/vscode && make` |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `CompilationSession` plus `CompilationContext` in `doctrine/compiler.py`
    remain the one compiler owner path
  - one compiled readable-block IR plus renderer dispatch path replaces
    section-only readable rendering as the sole shipped model
- Deprecated APIs (if any):
  - no public compiler wrapper is planned for deletion
  - `compile_prompt()` and `extract_target_flow_graph()` should remain thin
    wrappers over the same compiler owner path
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - any temporary compatibility path that keeps section-only rendering alive as
    a second semantics path
  - any temporary duplicate document/schema navigation logic in the editor once
    the canonical resolver helpers exist
  - the `Language Enhancement Specs` branch from `docs/README.md` once shipped
    docs absorb the truth
  - any stale post-`53` corpus references that preserve the overlapping spec
    numbering after the canonical `54-66` ladder lands
  - any temporary README or comment wording that still presents the mechanics
    wave as proposal-only after ship
- Capability-replacing harnesses to delete or justify:
  - no new parser wrapper, language server, compiler sidecar, or editor shadow
    parser is justified by this work
- Intentionally unchanged infrastructure:
  - `doctrine/emit_common.py` should stay language-agnostic unless a minimal
    compatibility touch-up is required by the renderer refactor
- Live docs/comments/instructions to update or delete:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/README.md`
  - `docs/COMPILER_ERRORS.md`
  - `docs/LANGUAGE_DESIGN_NOTES.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/REVIEW_SPEC.md`
  - `docs/EMIT_GUIDE.md`
  - `examples/README.md`
  - `editors/vscode/README.md`
  - any high-leverage code comments at the readable-block IR boundary, schema
    review-contract boundary, and editor resolver helper boundary
- Behavior-preservation signals for refactors:
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics move
  - targeted manifest-backed runs on the new ladder while it is under
    construction
  - `cd editors/vscode && make`

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Readable surfaces | `doctrine/grammars/doctrine.lark`, `doctrine/model.py`, `doctrine/compiler.py`, `doctrine/renderer.py` | one shared readable-block grammar + IR across documents and markdown-bearing contracts | prevents three separate mini-languages for documents, outputs, and analysis/schema rendering | include |
| Compiler ownership | `doctrine/compiler.py` `CompilationSession`, `CompilationContext` | extend the existing session/context split instead of adding a new compiler owner | prevents parallel compile architectures | include |
| Addressability | `doctrine/compiler.py` addressable helpers, `editors/vscode/resolver.js` path traversal | extend the existing root/child resolution model to new roots and descendants | prevents one-off path rules per new surface | include |
| Corpus sequencing | `examples/README.md`, new examples `54-66` | one canonical post-`53` ladder | prevents dual numbering and teaching drift | include |
| Evergreen docs | `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, enhancement-spec docs | one live docs path plus one historical design path | prevents shipped docs and enhancement specs from competing | include |
| VS Code shell | `editors/vscode/extension.js` | keep current provider wiring; evolve resolver/tmLanguage only | avoids needless editor architecture churn | include |
| Explored controls | `properties`, standalone `guard`, `render_profile` | keep deferred unless doc-truth audit promotes them | avoids inventing under-specified behavior while claiming “full” shipped truth | exclude |
| Editor-product extras | hover, completion, rename, symbol search, language server | do not grow the extension product surface in this wave | avoids scope creep unrelated to compiler parity | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 - Shared Language And Readable-IR Foundations

Status: IN PROGRESS

Completed work:
- Started implementation on branch `feat/language-mechanics-wave`.
- Verified real `implement-loop` runtime support and armed
  `.codex/implement-loop-state.json`.
- Created the canonical worklog at
  `docs/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11_WORKLOG.md`.
- Added top-level `analysis`, `schema`, and `document` parse scaffolding in
  `doctrine/grammars/doctrine.lark`, `doctrine/model.py`, and
  `doctrine/parser.py`, including shared document-block keywords and triple
  quoted multiline string parsing.
- Added the first shared compiled readable-block IR scaffold in
  `doctrine/compiler.py` and rewired `doctrine/renderer.py` so sections and
  future readable blocks render through one block-dispatch path instead of a
  separate section-only recursion entrypoint.
- Extended compiler indexing so `analysis`, `schema`, and `document`
  declarations register as first-class addressable roots on the existing
  `CompilationSession` path.
- Updated `editors/vscode/` for the shipped foundation slice:
  `language-configuration.json`, `syntaxes/doctrine.tmLanguage.json`,
  `resolver.js`, and `scripts/validate_lark_alignment.py` now recognize the
  new declaration headers, readable-block keywords, and multiline string
  surface.
- Historical note: this pass recorded green verification when it originally
  landed, but current editor-package truth is owned by the dedicated
  readable-markdown plan and its authoritative audit block.

* Goal:
  Establish the one-path parser/compiler/render foundation for the mechanics
  wave without regressing the shipped corpus through example `53`.
* Work:
  - extend `doctrine/grammars/doctrine.lark`, `doctrine/model.py`, and
    `doctrine/parser.py` for top-level `analysis` / `schema` / `document`
    declaration scaffolding, multiline strings, shared readable-block syntax,
    and typed attachment headers
  - introduce the compiled readable-block union in `doctrine/compiler.py` and
    adapt `doctrine/renderer.py` so existing section output already flows
    through the new single readable path
  - extend session indexing and addressability registries for the new
    declaration families without adding a second compiler owner or shadow
    renderer
  - make the minimum `editors/vscode/` keyword and indentation updates needed
    to keep grammar alignment honest while full resolver parity is still
    pending
* Verification (smallest signal):
  - `make verify-examples`
  - `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  - add high-leverage code comments at the readable-block IR boundary and the
    new declaration-index/addressability seams
  - do not promote new user-facing language docs yet if a surface is not
    end-to-end shippable in this phase
* Exit criteria:
  - existing shipped examples through `53_review_bound_carrier_roots` stay
    green
  - the compiler and renderer no longer depend on section-only recursion as a
    separate semantics path
  - grammar/editor keyword alignment remains truthful
* Rollback:
  - back out partial readable-IR or declaration-registration changes if the
    shipped corpus or editor alignment regresses; do not carry a temporary dual
    renderer or half-registered declaration family forward

## Phase 2 - Document, Structure, And Multiline Readable Rollout

* Goal:
  Ship `document`, shared readable blocks, `structure:`, and multiline readable
  output end to end on the canonical compiler path.
* Work:
  - implement `document` compile/render/addressability/inheritance behavior,
    including explicit-accounting patching and keyed descendant traversal
  - implement readable-block lowering for sections, lists, checklists,
    definitions, tables, callouts, rules, and fenced code
  - implement multiline string lowering plus document-block guard validation
    under the shared guarded-source discipline
  - implement markdown-bearing `structure:` resolution on inputs and outputs
    with `structure -> document` validation
  - add the `54-59` corpus slice, including positive manifests and negative
    proof for bad `structure:` refs, duplicate document keys, guard-source
    violations, and block-shape validation
  - extend `editors/vscode/` syntax, navigation, tests, and README smoke
    guidance for documents, readable blocks, multiline strings, and document
    descendants
* Verification (smallest signal):
  - targeted manifest-backed runs for `examples/54_*` through `examples/59_*`
    while the phase is in flight
  - `make verify-examples`
  - `make verify-diagnostics` if the phase introduces document/structure
    diagnostics
  - `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  - update `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_DESIGN_NOTES.md`,
    `docs/AGENT_IO_DESIGN_NOTES.md`, and `examples/README.md` for the shipped
    document/structure/multiline surfaces
  - add concise code comments at readable-block dispatch and document-guard
    validation boundaries when the implementation would otherwise be opaque
* Exit criteria:
  - `document`, readable blocks, `structure:`, and multiline readable output
    are shipped with manifest-backed proof and editor parity
  - the live docs that mention these surfaces describe shipped truth rather
    than proposal-only behavior
* Rollback:
  - revert the document/structure slice as a unit if addressability,
    validation, or renderer behavior remains unstable; do not leave partial
    block kinds or `structure:` support alive without proof

## Phase 3 - Analysis, Schema, And Output-Schema Core Rollout

* Goal:
  Ship first-class `analysis`, first-class `schema`, and `output schema:` with
  non-colliding diagnostics on the same compiler path.
* Work:
  - implement `analysis` parse/compile/render/inheritance/addressability
  - implement `schema` parse/compile/render/inheritance/addressability,
    including gate and section inventories
  - implement `output schema:` resolution with `schema -> schema` validation
    and the hard prohibition on `schema:` plus local `must_include`
  - allocate and implement the new diagnostics bands for `analysis`,
    `schema`, and readable/document validation, and update the normalized error
    catalog accordingly
  - add the `60-63` corpus slice, including positive manifests and negative
    proof for bad `schema:` refs and `schema + must_include`
  - extend `editors/vscode/` syntax, resolver, tests, and docs for
    `analysis`, `schema`, and `output schema:` surfaces
* Verification (smallest signal):
  - targeted manifest-backed runs for `examples/60_*` through `examples/63_*`
    while the phase is in flight
  - `make verify-examples`
  - `make verify-diagnostics`
  - `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  - update `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md`,
    `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, and
    `examples/README.md`
  - add high-leverage code comments at analysis-lowering and schema-gate
    boundaries if needed
* Exit criteria:
  - `analysis`, `schema`, and `output schema:` are shipped with stable
    diagnostics, corpus proof, and editor parity
  - existing emit/build diagnostic meanings remain unchanged
* Rollback:
  - revert the analysis/schema/output-schema slice together if ownership,
    rendering, or diagnostics remain ambiguous; do not ship `schema:` without
    its validation and negative-proof obligations

## Phase 4 - Review Or Schema Integration And Capstone Corpus Completion

* Goal:
  Close the remaining integration seams so review contracts, outputs, schemas,
  and readable artifacts all resolve through one semantic path.
* Work:
  - extend review contract resolution so `contract:` can target either
    workflow review contracts or schema gates without splitting the resolver
    model
  - implement schema-gate validation, carried-state coupling, and any
    remaining review/output interactions required by the split specs
  - add the `64-66` capstone corpus slice and complete the remaining negative
    cases, especially unknown schema review gates and review/schema contract
    misuse
  - make the minimal consumer updates in `doctrine/emit_docs.py`,
    `doctrine/emit_flow.py`, and `doctrine/verify_corpus.py` required by the
    widened readable path while keeping `CompilationSession` as the only owner
  - extend `editors/vscode/` navigation/tests for schema-backed
    `contract.<gate>` resolution and the capstone examples
* Verification (smallest signal):
  - targeted manifest-backed runs for `examples/64_*` through `examples/66_*`
    while the phase is in flight
  - `make verify-examples`
  - `make verify-diagnostics`
  - targeted emit smoke on one existing emit target and one new mechanics-wave
    doc target once that target exists
  - `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  - update `docs/REVIEW_SPEC.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
    `docs/EMIT_GUIDE.md`, and any remaining surface docs touched by the
    integration work
  - add a concise code comment where review-contract branching meets schema
    gates if the final control flow would otherwise be hard to follow
* Exit criteria:
  - review/workflow/schema contracts all resolve on one path with manifest
    proof
  - emit and verify consumers still ride the same compiler owner path
* Rollback:
  - back out schema-review integration and its capstones together if the work
    creates dual contract semantics or consumer divergence; do not leave docs
    or editor support ahead of compiler proof

## Phase 5 - Evergreen Docs Cutover, VS Code Final Truth Sync, And Hard-Cut Verification

* Goal:
  Remove competing truth surfaces, finish repo-wide parity, and prove the full
  mechanics wave as shipped Doctrine behavior.
* Work:
  - remove or reclassify the `Language Enhancement Specs` branch in
    `docs/README.md` so the live docs path points only at shipped truth
  - finish the remaining evergreen doc sync across
    `docs/LANGUAGE_REFERENCE.md`, `docs/README.md`,
    `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md`,
    `examples/README.md`, and `editors/vscode/README.md`
  - sweep stale overlapping post-`53` example references, proposal-only
    wording, and any temporary compatibility comments or helper paths created
    during the implementation
  - finalize `editors/vscode/` snapshots, integration fixtures, and smoke-check
    guidance against representative new-wave examples
* Verification (smallest signal):
  - `make verify-examples`
  - `make verify-diagnostics`
  - targeted emit smoke on one existing flow target and one mechanics-wave doc
    target
  - `cd editors/vscode && make`
  - final manual smoke in the packaged extension against representative new
    examples from the document, analysis/schema, and review/schema slices
* Docs/comments (propagation; only if needed):
  - complete the live-doc cutover and historical-spec reclassification
  - delete stale README/comment wording rather than preserving legacy
    explanation in live surfaces
* Exit criteria:
  - live docs, examples, compiler, diagnostics, emit surfaces, and VS Code all
    describe and prove the same shipped language
  - no temporary compatibility paths, stale numbering, or proposal-only live
    docs remain
* Rollback:
  - revert the docs cutover and final cleanup as one slice if any shipped-truth
    surface still outruns compiler or editor proof; do not leave the live docs
    index advertising unsupported behavior
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

Doctrine should rely on repo-owned checks rather than ceremony. The full wave
should prefer the smallest credible combination of corpus verification,
diagnostic verification, targeted example runs during development, and the
existing VS Code package/test surface.

## 8.1 Unit tests (contracts)

- Parser/compiler/diagnostic regression checks where the repo already uses them.
- VS Code unit/alignment fixtures covering the new syntax and reference shapes.

## 8.2 Integration tests (flows)

- `make verify-examples`
- `make verify-diagnostics` when diagnostics change
- targeted manifest-backed example runs for the newly added ladder while the
  wave is in flight
- targeted emit smoke on one existing emit target and one mechanics-wave doc
  target after the readable-render cutover lands
- `cd editors/vscode && make`

## 8.3 E2E / device tests (realistic)

Keep final manual verification narrow:

- open the shipped extension against representative new-language examples
- confirm clickable navigation and highlighting on the newly shipped surfaces
- do not invent extra harnesses if the existing editor package/test flow is
  enough

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

This should be a repo-local hard cutover. The language, examples, docs, and VS
Code extension should move together so the repo never advertises unsupported
syntax as if it were shipped.

## 9.2 Telemetry changes

No production telemetry surface is expected. If any internal verification or
editor smoke aid is useful, it should stay proportional and repo-local.

## 9.3 Operational runbook

The operational runbook should remain simple: sync dependencies, run the
relevant Doctrine verification commands, and run `cd editors/vscode && make`
for the editor surface whenever that area changes.

# 10) Decision Log (append-only)

## 2026-04-11 - Start full mechanics-wave architecture planning

Context

The repo already has split design docs for the next language wave, but the
user explicitly asked for a full plan to ship `docs/LANGUAGE_MECHANICS_SPEC.md`
as intended and explicitly rejected narrowing the work to a smaller first-wave
subset.

Options

- Ship only `analysis` plus `schema` first.
- Ship only `document` / typed markdown first.
- Plan the full intended mechanics wave and make the later implementation order
  solve the convergence problem cleanly.

Decision

Plan the full intended mechanics wave end to end and keep the full requested
scope explicit in the North Star.

Consequences

The later planning and implementation work must reconcile the two spec tracks
into one coherent shipped surface, one example sequence, one diagnostic
strategy, one docs story, and one VS Code parity path.

Follow-ups

- Confirm the North Star before deeper planning.
- Use later `arch-step` passes to ground the exact implementation order,
  exhaustive call-site audit, and authoritative phase plan.

## 2026-04-11 - North Star approved by explicit auto-plan invocation

Context

The canonical plan was created in `draft` state pending explicit North Star
approval. The next user action was `Use $arch-step auto-plan`, which is a
stronger proceed signal than a plain `yes` and did not request changes to the
scoped outcome or invariants.

Options

- Treat the `auto-plan` command as implicit North Star approval and continue.
- Stop again for a redundant textual `yes`.

Decision

Treat the explicit `auto-plan` invocation as North Star approval and move the
canonical doc to `status: active` without changing scope.

Consequences

The planning controller may now run against this doc, but it still must stop
honestly if runtime continuation support or stage outputs are missing.

Follow-ups

- Keep scope and invariants unchanged while deeper planning sharpens the plan.

## 2026-04-11 - Extend the existing compile-session architecture, do not replace it

Context

Deep-dive pass 1 confirmed that the repo already ships
`doctrine/compiler.py:CompilationSession` and that `emit_docs.py`,
`emit_flow.py`, and `verify_corpus.py` already reuse it. The mechanics wave
therefore lands on top of an existing scalable compiler owner rather than on
the older single-context design.

Options

- Design a fresh compiler owner around the new language wave.
- Extend the existing `CompilationSession` / `CompilationContext` split.

Decision

Extend the existing session/context architecture and keep it as the sole
compiler owner path while widening the language surface and readable rendering
model.

Consequences

The hard work is in grammar/model/compiler/render/addressability expansion, not
in replacing the compiler shell. This lowers architectural churn and keeps emit
and verify consumers on the same owner path.

Follow-ups

- Phase planning should treat session reuse as already solved and should focus
  execution on the language-wave surfaces themselves.

## 2026-04-11 - Attachment contracts stay declaration-typed and fail loud

Context

Deep-dive pass 2 revisited the split specs and confirmed that the attachment
contracts are intentionally narrow: `output schema:` resolves to `schema`,
markdown-bearing `structure:` resolves to `document`, and review contracts may
target workflow review contracts or schema gates. The current draft already
pointed in that direction, but it had not yet locked the rule tightly enough
to prevent implementation drift.

Options

- Leave the attachment targets implicit and let implementation choose.
- Lock the typed attachment rules and validation errors now.

Decision

Lock the attachment rules now:
`schema:` resolves only to `schema`, `structure:` resolves only to `document`,
`schema:` plus local `must_include` is a hard compile error, and document-block
guards reuse guarded-output source restrictions instead of inventing a second
guard discipline.

Consequences

The compiler, diagnostics, corpus, docs, and VS Code navigation all get one
clear contract for the new attachment surfaces. This also makes the negative
corpus obligations explicit before phase planning.

Follow-ups

- Phase planning must schedule the attachment validations, negative examples,
  and doc/editor truth updates together rather than treating them as cleanup.

## 2026-04-11 - Execution order is foundations -> document -> analysis/schema -> review integration -> truth-sync

Context

The architecture and call-site audit leave several valid work slices, but the
implementation order matters because the readable-block IR, document
addressability, diagnostics, review/schema coupling, docs cutover, and VS Code
parity all depend on a clean convergence sequence.

Options

- Start with `analysis` / `schema` because they were the narrower first-wave
  recommendation in earlier design notes.
- Start with the shared readable-block and document foundations, then layer the
  semantic surfaces and final truth-sync on top.

Decision

Execute in this order:
shared language and readable-IR foundations, then `document` / `structure:` /
multiline rollout, then `analysis` / `schema` / `output schema:`, then
review-or-schema integration and capstones, then the evergreen-docs and VS
Code truth-sync cutover.

Consequences

The plan lands the hardest shared infrastructure before the semantics that rely
on it, keeps diagnostics and proof close to the slices that introduce them, and
reserves the live-docs cutover for the point where shipped truth is actually
complete.

Follow-ups

- `implement` should execute from the phase plan directly without inventing a
  different work order unless new repo evidence proves that order wrong.

## 2026-04-11 - Readable rendering converges onto one block IR

Context

Deep-dive pass 1 confirmed that the shipped renderer still consumes a
`CompiledSection`-only tree, while the mechanics wave needs documents, rich
contract blocks, tables, checklists, callouts, rules, and fenced code. Those
surfaces overlap too heavily to justify separate rendering models.

Options

- Keep `CompiledSection` as one semantics path and add a second document-only
  block renderer.
- Converge all readable output onto one compiled readable-block IR where
  `section` becomes one block kind.

Decision

Converge readable compilation and rendering onto one block IR. `CompiledSection`
may survive only as the `section` variant or a thin compatibility wrapper
inside that one path.

Consequences

The compiler, renderer, docs, and editor all align around one readable model.
This raises the up-front compiler change size, but it removes the risk of
parallel readable semantics drifting apart.

Follow-ups

- Phase planning must land the readable-block foundation before higher-level
  document/schema integrations that depend on it.

## 2026-04-11 - New mechanics diagnostics stay below the emit range

Context

The mechanics spec proposes `E501-E519` for `analysis`, but shipped Doctrine
already uses `E500-E699` for emit/build diagnostics and live meanings exist in
`E501-E516`.

Options

- Reuse the proposed `E501-E519` range and break stable emit meanings.
- Allocate new mechanics-wave compile codes below `E500`.

Decision

Reserve new mechanics-wave codes below the emit range:
`E385-E399` for `analysis`, `E400-E419` for `schema`, and `E420-E449` for
`document`, readable-output validation, `structure:`, and multiline/readable
validation.

Consequences

The cutover preserves all current emit/review code identities while creating a
stable home for the new compile-time failures.

Follow-ups

- Phase planning must pair compiler work with `docs/COMPILER_ERRORS.md`,
  negative-corpus proof, and `make verify-diagnostics`.

## 2026-04-11 - Canonical post-53 corpus sequence is 54 through 66

Context

The enhancement specs propose two overlapping example ladders that both try to
start at `54`, which cannot ship as a single deterministic teaching corpus.

Options

- Keep the overlap and rely on design docs to explain it.
- Renumber the analysis/schema ladder upward.
- Renumber the readable-document ladder upward.

Decision

Use one canonical shipped sequence:
`54_first_class_documents` through `59_multiline_strings_and_code_blocks`, then
`60_analysis_basic` through `66_schema_review_contract`.

Consequences

The docs, examples index, manifests, VS Code snapshots, and any live references
to post-`53` examples must use this one sequence.

Follow-ups

- Phase planning must schedule example creation and docs/editor references
  against this numbering.

## 2026-04-11 - Enhancement specs leave the live docs path after ship

Context

The enhancement-spec set is useful design context today, but once the language
wave is shipped it becomes competing truth if it remains in the live docs path
next to the evergreen shipped reference.

Options

- Keep the enhancement specs in the live docs index permanently.
- Remove or demote them from the live docs path after ship while preserving
  them as historical design material.

Decision

After the cutover, move the enhancement-spec set out of the live docs path or
reclassify it explicitly as historical design material, while the shipped docs
absorb the canonical language truth.

Consequences

`docs/README.md` and the shipped language docs become the only evergreen entry
path for users learning the language after this wave lands.

Follow-ups

- Phase planning must include live-doc cutover work, not treat it as optional
  cleanup.
