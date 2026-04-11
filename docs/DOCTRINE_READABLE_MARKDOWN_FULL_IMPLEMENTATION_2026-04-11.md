---
title: "Doctrine - Readable Markdown Full Implementation - Architecture Plan"
date: 2026-04-11
status: active
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: architectural_change
related:
  - docs/READABLE_MARKDOWN_SPEC.md
  - docs/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md
  - docs/DOCTRINE_INTEGRATION_SURFACES_FULL_IMPLEMENTATION_2026-04-11.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/REVIEW_SPEC.md
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
  - editors/vscode/language-configuration.json
  - editors/vscode/scripts/validate_lark_alignment.py
---

# TL;DR

## Outcome

Doctrine fully ships `docs/READABLE_MARKDOWN_SPEC.md` as intended, not as the
current narrowed `document`-plus-`structure:` subset. That means first-class
`document`, the shared readable block sublanguage across readable Doctrine
surfaces, real typed block semantics for `section`, `sequence`, `bullets`,
`checklist`, `definitions`, `table`, `callout`, `code`, and `rule`, deeper
addressability, multiline strings where the spec requires them, manifest-backed
examples, evergreen docs, diagnostics, and full VS Code extension parity.

## Problem

The repo currently has split truth. The spec promises a full readable-markdown
system, but shipped Doctrine only proves the narrower `document` +
markdown-bearing `structure:` slice. The grammar, AST, compiler, renderer,
examples, evergreen docs, and editor support do not yet cover the richer block
headers, shared block reuse outside `document`, deep descendant addressability,
or the renderer behaviors the spec claims are core. Leaving that gap in place
keeps the repo half-shipped and keeps live docs confusing.

## Approach

Implement the full readable-markdown wave through the existing Doctrine owners
only. Expand the grammar/model/parser/compiler/renderer around one coherent
compiled readable-block pipeline, teach the shared readable sublanguage to the
intended bodies instead of inventing parallel mini-languages, extend the corpus
with positive and compile-negative proof, then converge evergreen docs and the
VS Code extension onto the same shipped truth.

## Plan

1. Lock the exact intended `READABLE_MARKDOWN_SPEC.md` scope and separate the
   truly shipped slice from the still-missing slice without scoping the work
   down.
2. Widen the core language and IR: full block header model, multiline strings,
   typed inner block shapes, addressable descendants, and explicit inheritance
   semantics.
3. Implement renderer semantics that match the spec instead of collapsing most
   blocks into titled shells.
4. Extend the shared readable block sublanguage beyond `document` into the
   intended record, output, workflow, and skill-entry surfaces.
5. Ship the missing example ladder, negative proof, evergreen docs updates,
   diagnostics updates, and VS Code parity in the same cutover.

## Non-negotiables

- Do not scope this down to the currently shipped `document` +
  `structure:` subset.
- Do not claim the feature is complete while `definitions`, `table`,
  `callout`, `code`, or `rule` still render as heading shells instead of their
  promised markdown forms.
- Do not invent a second readable renderer path, a shadow editor grammar, or a
  parallel readable mini-language.
- Do not let docs, examples, compiler behavior, and VS Code support disagree
  about what is shipped.
- Do not silently weaken explicit spec structure such as requirements, guards,
  block-kind invariants, keyed descendant addressability, or inheritance
  accounting.
- Do not add raw-markdown escape hatches, HTML-specific constructs, images,
  footnotes, or nested tables when the spec explicitly rejects them in v1.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-11
Verdict (code): NOT COMPLETE
Manual QA: pending (non-blocking)

## Code blockers (why code is not done)
- Phase 5 remains false-complete. Fresh audit evidence shows the repo-root
  proof signals are green from this worktree, but the VS Code package path is
  still red: `make` in `editors/vscode/` exits non-zero after
  `test:integration` aborts with `SIGABRT` on all four startup attempts.

## Reopened phases (false-complete fixes)
- Phase 5 (Proof, docs, diagnostics, and editor parity cutover) — reopened
  because:
  - fresh `.venv/bin/python -m doctrine.verify_corpus` passes the full shipped
    corpus through `examples/61_multiline_code_and_readable_failures`, and
    fresh `.venv/bin/python -m doctrine.diagnostic_smoke` passes, so the
    earlier repo-root D2 blocker is no longer real in this worktree
  - fresh `make` evidence in `editors/vscode/` passes `npm install`,
    `test:unit`, and `test:snap`, resolves cached VS Code `1.115.0` after the
    version lookup falls back from `ENOTFOUND`, then still exits non-zero after
    four `SIGABRT` retries in `test:integration`, so alignment validation,
    VSIX packaging, and `cd editors/vscode && make` are not green end to end

## Missing items (code gaps; evidence-anchored; no tables)
- VS Code extension-host integration still does not pass from fresh audit
  context
  - Evidence anchors:
    - `editors/vscode/package.json:24`
    - `editors/vscode/package.json:28`
    - `editors/vscode/package.json:29`
    - `editors/vscode/tests/integration/run.js:12`
    - `editors/vscode/tests/integration/run.js:138`
    - `editors/vscode/tests/integration/run.js:157`
  - Plan expects:
    - Phase 5 ends with a passing `cd editors/vscode && make` so editor
      behavior, integration coverage, alignment validation, and VSIX packaging
      are proved against the shipped readable-markdown surface.
  - Code reality:
    - Fresh `make verify-examples` and `make verify-diagnostics` are not usable
      in this sandbox because `uv run --locked ...` fails before Python starts,
      so this audit used the equivalent direct `.venv/bin/python -m ...`
      surfaces for repo-root proof.
    - Fresh `.venv/bin/python -m doctrine.verify_corpus` passes the full
      shipped corpus, and fresh `.venv/bin/python -m doctrine.diagnostic_smoke`
      passes.
    - Fresh `make` in `editors/vscode/` passes `npm install`, `test:unit`, and
      `test:snap`.
    - The same `make` run reuses cached VS Code `1.115.0` from the short temp
      cache after version lookup falls back from `ENOTFOUND`, then
      `npm run test:integration` exits with `SIGABRT` on four consecutive
      startup attempts, so alignment validation, VSIX packaging, and
      `cd editors/vscode && make` remain red end to end.
  - Fix:
    - Make the extension-host integration run reliable from fresh audit
      context, then rerun `npm test` and `cd editors/vscode && make`.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Run the live-editor smoke ladder from `editors/vscode/README.md` after Phase
  5 is green again.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-11
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-11
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly, Doctrine will ship the full readable
markdown system described by `docs/READABLE_MARKDOWN_SPEC.md` rather than the
current narrowed subset:

- readable Doctrine bodies will support the intended block kinds and block
  semantics instead of mostly falling back to heading recursion
- `document` will be one real top-level markdown schema declaration with
  explicit inheritance, keyed descendants, guards, and rich block bodies
- the shared readable block sublanguage will be available on the intended
  readable surfaces beyond `document`
- renderer output will match the promised markdown shapes for ordered lists,
  bullets, checklists, definitions, tables, callouts, code fences, and rules
- addressability will reach the keyed descendants the spec says are part of the
  language contract
- examples, evergreen docs, diagnostics, and VS Code support will describe and
  prove the same shipped behavior

The claim is false if the repo still only ships the narrowed `document` +
`structure:` slice, if the compiler or renderer still treats most rich blocks
as titled shells, if the readable sublanguage remains document-only, if deep
addressability remains absent where the spec says it exists, or if docs/editor
truth keeps outrunning shipped behavior.

## 0.2 In scope

- Full implementation of the intended surfaces in
  `docs/READABLE_MARKDOWN_SPEC.md`, including:
  - top-level `document`
  - the shared readable block sublanguage
  - block header qualifiers such as requirement and `when`
  - typed semantics for `section`, `sequence`, `bullets`, `checklist`,
    `definitions`, `table`, `callout`, `code`, and `rule`
  - multiline string support where required by readable markdown
  - keyed descendant addressability for the document/block shapes the spec
    declares addressable
  - explicit inheritance and override accounting for `document`
- Shared compiler and renderer convergence required to keep one readable-block
  pipeline instead of a document-only branch plus legacy shells elsewhere.
- Extending the readable block sublanguage to the intended readable bodies,
  including `document`, record-style contract bodies, readable output shapes,
  workflow section bodies, and skill-entry bodies when the spec says they share
  the same readable output layer.
- Example-corpus delivery for the missing readable-markdown feature wave,
  including positive and compile-negative proof.
- Evergreen docs updates across the live docs path so shipped truth matches the
  actual readable-markdown feature set.
- Full VS Code extension parity across syntax, indentation behavior, resolver
  logic, README truth, tests, and packaging for the readable-markdown wave.
- Architectural convergence needed to remove stale or misleading claims in the
  current umbrella plan docs once the dedicated readable-markdown plan becomes
  the canonical owner for this scope.

Allowed architectural convergence scope:

- widen touched files across `doctrine/`, `examples/`, `docs/`, and
  `editors/vscode/` as needed to keep one owner path for readable markdown
- replace shell-style renderer behavior with the intended block-specific
  behavior instead of preserving both semantics in parallel
- reclassify or update stale docs that currently overclaim or underclaim the
  shipped readable-markdown surface

## 0.3 Out of scope

- Scoping the work down to only the already-shipped `document` +
  `structure:` subset.
- New product capabilities outside readable markdown, document contracts, docs
  convergence, example proof, diagnostics, and editor parity.
- New workflow-law, review, or trust-surface semantics except where readable
  block support must interoperate with already-shipped behavior.
- A raw markdown escape hatch, HTML-specific constructs, footnotes, images, or
  nested tables in v1.
- A second readable markdown architecture, renderer, or editor truth path.
- Runtime shims, fallback renderers, or compatibility layers that keep both the
  old shell rendering and the new block semantics alive as equal live truth.

## 0.4 Definition of done (acceptance evidence)

- `doctrine/grammars/doctrine.lark`, `doctrine/model.py`,
  `doctrine/parser.py`, `doctrine/compiler.py`, and `doctrine/renderer.py`
  implement the full intended readable-markdown contract, not only the narrow
  `document` + `structure:` subset.
- The block kinds and their renderer output match the spec's intended markdown
  semantics closely enough that the spec no longer claims behavior the shipped
  renderer does not own.
- The missing example ladder and compile-negative proof for the readable
  markdown system are present and manifest-backed.
- `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/REVIEW_SPEC.md`, `docs/README.md`, `docs/COMPILER_ERRORS.md`, and
  `examples/README.md` match shipped truth.
- `editors/vscode/` recognizes and navigates the readable-markdown surface, and
  `cd editors/vscode && make` passes.
- Repo verification passes at the right checkpoints:
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics change
  - targeted manifest-backed runs while developing the new readable ladder
  - `cd editors/vscode && make`

Behavior-preservation evidence:

- existing shipped prompts that rely on plain keyed sections and emphasized
  prose remain legal where the spec explicitly promises backward compatibility
- the corpus through `examples/57_schema_review_contracts` remains green unless
  a justified bug fix changes behavior
- previously shipped editor highlighting and navigation remain intact while the
  readable-markdown wave is added

## 0.5 Key invariants (fix immediately if violated)

- One readable-block pipeline, not a document-only branch plus legacy shells.
- Only `section` consumes heading depth in the shipped renderer.
- Non-section readable blocks must render through their own markdown forms, not
  fake heading ladders.
- Old keyed-section authoring stays legal where the spec explicitly says it is
  sugar for `section`.
- Inheritance and override accounting remain explicit and fail loud.
- Block-kind identity stays invariant under override.
- Docs, examples, compiler behavior, diagnostics, and VS Code support must say
  the same thing about the shipped surface.
- No fallback renderer or compatibility shim.
- No raw markdown escape hatch in v1.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Ship the full intended readable-markdown feature set, not the currently
   narrowed subset.
2. Keep one coherent compiler and renderer path for all readable surfaces.
3. Make renderer output match semantic block kinds instead of nesting depth.
4. Keep backward compatibility promises truthful and explicit.
5. Keep docs, examples, diagnostics, and editor parity synchronized to shipped
   behavior.

## 1.2 Constraints

- The repo already ships a narrowed second-wave slice, so the implementation
  cannot pretend the current state is either empty or complete.
- Existing example numbers `54` through `57` are already occupied, so the
  missing readable-markdown proof ladder must extend from the current corpus
  rather than reusing the original speculative numbering in the spec.
- Current live docs partly overclaim the readable-markdown wave, so docs work is
  not optional cleanup; it is part of shipping truth.
- VS Code support is hand-maintained and must be updated alongside grammar and
  resolver changes.

## 1.3 Architectural principles (rules we will enforce)

- Reuse Doctrine's existing owners; do not add a second readable system.
- Fail loud on unsupported or contradictory readable-markdown usage.
- Treat renderer semantics as language truth, not as optional presentation
  polish.
- Keep domain names and domain columns in authored prompts; keep block
  semantics in Doctrine core.
- Preserve explicit authored structure instead of introducing implicit merge or
  inference rules.

## 1.4 Known tradeoffs (explicit)

- Shipping the full readable-markdown system will likely broaden the compiler,
  renderer, diagnostics, examples, and editor surface at once; that breadth is
  required to avoid another half-shipped wave.
- Full descendant addressability and shared sublanguage reuse increase surface
  area, but leaving them out would keep the spec and shipped language split.
- Some current evergreen docs may need to become narrower or more explicit if a
  spec promise turns out to require slight reshaping during implementation.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine currently ships:

- top-level `document`
- `structure:` attachments on markdown-bearing inputs and outputs
- a compiled readable-block union in the implementation
- a renderer that still treats most non-section block kinds as titled shells
- manifest-backed proof for the narrowed `document` + `structure:` slice

## 2.2 What’s broken / missing (concrete)

- The spec's block header model, typed inner block shapes, and descendant
  addressability are not fully represented in the shipped grammar or AST.
- The readable block sublanguage is not yet broadly available on the intended
  non-document readable surfaces.
- Renderer semantics for `definitions`, `table`, `callout`, `code`, and `rule`
  do not yet match the spec's intended markdown output.
- The example ladder and negative corpus for the full readable-markdown wave do
  not yet exist.
- Evergreen docs and umbrella implementation docs still leave the repo's actual
  readable-markdown status ambiguous.

## 2.3 Constraints implied by the problem

- The fix cannot be parser-only or renderer-only.
- The repo cannot honestly call the wave shipped until examples, docs, and the
  VS Code extension match the same surface.
- Backward compatibility promises in the spec must either be implemented or
  explicitly revised in shipped docs.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- No external anchors are adopted in this pass. Repo evidence already settles
  the current owner paths, shipped behavior, and drift surfaces. Re-open
  external grounding only if markdown-rendering ergonomics or editor behavior
  remain ambiguous after the compiler-owned cutover.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/grammars/doctrine.lark` — `document_decl`, `document_body`,
    `document_block`, `document_override_block`, `record_body`,
    `output_record_body`, `workflow_section_body`, and `skill_entry_body`
    define the current authored surface. The current document grammar already
    knows the block kinds, but it still accepts only `kind key: "Title"` plus
    indented `block_lines`.
  - `doctrine/model.py` — `DocumentBlock`, `DocumentOverrideBlock`,
    `DocumentBody`, `DocumentDecl`, `InputStructureConfig`, and
    `OutputStructureConfig` define the shipped document and `structure:`
    attachment data model.
  - `doctrine/parser.py` — `document_decl`, `document_block`, and
    `document_override_block` parse current documents into the simple shell
    model. There is no typed inner-block parse path yet for `columns:`,
    `rows:`, `notes:`, `kind:`, `language:`, or multiline `text:`.
  - `doctrine/compiler.py` — `_resolve_document_decl`,
    `_resolve_document_body`, `_compile_document_decl`,
    `_compile_document_body`, `_compile_document_block`,
    `_document_items_to_addressable_children`, `_resolve_addressable_path_node`,
    `_flow_input_detail_lines`, `_flow_output_detail_lines`, and
    `_compile_output_decl` are the canonical compiler owners for document
    inheritance, structure attachments, addressability, and emitted contract
    rendering.
  - `doctrine/renderer.py` — `render_markdown`, `_render_block`,
    `_render_titled_block`, `_render_list_block`, `_render_code_block`, and
    `_render_rule_block` define the actual readable markdown contract today.
    They already dispatch on block kind, but several kinds still inherit titled
    shell behavior instead of block-native markdown semantics.
  - `doctrine/verify_corpus.py` — manifest-backed verification is the primary
    preservation signal and already supports parallel compile-case checking
    through shared compilation sessions.
  - `doctrine/diagnostic_smoke.py` — the current smoke suite already checks the
    shipped `structure:` path and is the correct place for stable readable
    diagnostic smoke coverage.
- Canonical owner path / boundary to reuse:
  - `doctrine/grammars/doctrine.lark` + `doctrine/parser.py` +
    `doctrine/model.py` — one authored readable language and one AST.
  - `doctrine/compiler.py` + `doctrine/renderer.py` — one readable-block
    compile and render pipeline.
  - `editors/vscode/resolver.js`,
    `editors/vscode/syntaxes/doctrine.tmLanguage.json`,
    `editors/vscode/language-configuration.json`, and
    `editors/vscode/scripts/validate_lark_alignment.py` — one editor parity
    path that must mirror the shipped language instead of inventing editor-only
    grammar.
- Existing patterns to reuse:
  - `doctrine/compiler.py::_resolve_document_decl` and
    `_resolve_document_body` already implement explicit inheritance accounting,
    cycle detection, duplicate-key rejection, undefined override rejection, and
    kind-preserving override rules for documents. Widen these helpers instead
    of replacing them.
  - `doctrine/compiler.py::_resolve_addressable_path_node` and
    `_get_addressable_children` already define the canonical addressable-path
    discipline used by schemas, workflows, records, and documents. Extend this
    tree instead of inventing a second readable lookup system.
  - `doctrine/compiler.py::_flow_input_detail_lines`,
    `_flow_output_detail_lines`, and `_compile_output_decl` already route
    `structure:` through typed owner-aware attachments on markdown-bearing
    inputs and outputs.
  - `examples/56_document_structure_attachments/cases.toml` and
    `doctrine/verify_corpus.py` already show the canonical manifest-backed
    proof pattern for this feature wave.
  - `editors/vscode/scripts/validate_lark_alignment.py` already asserts
    keyword, declaration, and current document-block alignment against the
    grammar. Extend that validator rather than adding a second editor-check
    harness.
- Prompt surfaces / agent contract to reuse:
  - None. This feature is compiler-owned and editor-owned rather than
    agent-runtime behavior.
- Native model or agent capabilities to lean on:
  - Not applicable. The work is typed language, renderer, diagnostics, and
    editor behavior.
- Existing grounding / tool / file exposure:
  - `docs/READABLE_MARKDOWN_SPEC.md` is bound into this plan's reference pack as
    the intended full behavior target.
  - `examples/56_document_structure_attachments` is the current shipped proof
    slice and the first preservation checkpoint.
  - `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`,
    `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/REVIEW_SPEC.md`, and
    `editors/vscode/README.md` are the live docs surfaces that will drift if
    they are not updated in the same cutover.
- Duplicate or drifting paths relevant to this change:
  - `docs/READABLE_MARKDOWN_SPEC.md` describes the full readable-markdown
    system, while shipped `doctrine/` plus `examples/56_document_structure_attachments`
    still prove only the narrower slice.
  - `doctrine/renderer.py` already knows the block kinds but still renders
    `definitions`, `table`, and `callout` largely through titled-shell logic.
  - `editors/vscode/resolver.js` and the TextMate grammar already recognize the
    current block headers, so editor coverage is ahead of the compiler's typed
    inner-block semantics.
  - `docs/README.md` demotes readable markdown to a second-wave design ref,
    while `docs/LANGUAGE_REFERENCE.md` presents part of it as shipped.
- Capability-first opportunities before new tooling:
  - Extend the existing grammar, parser, compiler, renderer, examples, docs,
    and editor owners. Do not add a standalone readable formatter, migration
    shim, or second markdown engine.
- Behavior-preservation signals already available:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/56_document_structure_attachments/cases.toml`
  - `make verify-examples`
  - `make verify-diagnostics`
  - `cd editors/vscode && make`
  - `doctrine/diagnostic_smoke.py`

## 3.3 Open questions from research

- Which readable descendants are first-wave addressable beyond current block
  keys: table columns only, or columns plus row keys and keyed list/definition
  items? Evidence: the spec says columns, rows, and keyed items are
  addressable, but the compiler currently stops at top-level document blocks.
- Which intended non-document bodies should accept the full readable block
  sublanguage in wave one: generic `record_body` plus `output_record_body`,
  `workflow_section_body`, and `skill_entry_body`, or a narrower subset?
  Evidence: the spec names all four surfaces, but the current grammar still
  gives them materially different body shapes.
- Should readable-markdown validation continue to reuse generic inherited-entry
  and addressable-path diagnostics, or should this wave allocate new
  readable-specific compiler codes and catalog entries? Evidence: document
  inheritance already throws `E001` and `E003`, while `docs/COMPILER_ERRORS.md`
  does not yet call out readable-markdown-specific failure families.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/grammars/doctrine.lark` owns the shipped authored syntax.
  `document_body` and `document_block` already exist, but `record_body`,
  `output_record_body`, `workflow_section_body`, and `skill_entry_body` still
  use their own legacy body rules.
- `doctrine/model.py` and `doctrine/parser.py` own the current document AST and
  parse path. Documents compile from `kind`, `key`, `title`, and `items`
  rather than from a typed inner readable-block model.
- `doctrine/compiler.py` owns document inheritance resolution, structure
  attachments, compiled readable blocks, and addressability.
- `doctrine/renderer.py` owns the emitted markdown contract.
- `examples/56_document_structure_attachments` is the clearest current proof
  slice for `document` plus `structure:`.
- `doctrine/diagnostic_smoke.py` carries the current structure-attachment smoke
  checks, and `doctrine/verify_corpus.py` carries the corpus runner.
- `editors/vscode/resolver.js`,
  `editors/vscode/syntaxes/doctrine.tmLanguage.json`,
  `editors/vscode/language-configuration.json`, and
  `editors/vscode/scripts/validate_lark_alignment.py` mirror the currently
  shipped readable-markdown header surface in the editor.
- `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/REVIEW_SPEC.md`, and
  `editors/vscode/README.md` are the live docs surfaces that already talk about
  `document` and `structure:`.

## 4.2 Control paths (runtime)

1. `parse_file()` loads `document_decl` and `structure:` attachments from
   `doctrine/grammars/doctrine.lark` into `model.DocumentDecl`,
   `InputStructureConfig`, and `OutputStructureConfig`.
2. `CompilationSession` indexes `documents_by_name` and keeps documents in the
   same declaration graph as analyses, schemas, workflows, inputs, outputs, and
   skills.
3. `doctrine/compiler.py::_resolve_document_decl` and `_resolve_document_body`
   handle document inheritance, explicit accounting, and prose interpolation,
   producing `ResolvedDocumentBody`.
4. `_compile_document_decl`, `_compile_document_body`, and
   `_compile_document_block` lower resolved document blocks into the shared
   `CompiledReadableBlock` union.
5. `_flow_input_detail_lines`, `_flow_output_detail_lines`, and
   `_compile_output_decl` surface `structure:` attachments on markdown-bearing
   inputs and outputs and embed the compiled document body inside the emitted
   contract when needed.
6. `render_markdown()` calls `_render_block()` at heading depth 2, and the
   block helpers turn compiled readable blocks into markdown.
7. `_resolve_addressable_path_node()` delegates document descendant lookup to
   `_get_addressable_children()` and `_document_items_to_addressable_children()`,
   which currently expose only the top-level keyed document blocks.
8. `editors/vscode/resolver.js` independently reconstructs declaration/body
   containers and regex-matches current document block headers for navigation
   and click targets.

## 4.3 Object model + key abstractions

- `DocumentBody` is `title + preamble + items`.
- `DocumentItem` is `ProseLine | DocumentBlock | InheritItem | DocumentOverrideBlock`.
- `DocumentBlock` and `DocumentOverrideBlock` carry `kind`, `key`, `title`, and
  `items`, where `items` are plain prose lines rather than typed descendants.
- `ResolvedDocumentBody` keeps the same top-level shape after inheritance
  accounting.
- `CompiledReadableBlock` is already a union over `section`, `sequence`,
  `bullets`, `checklist`, `definitions`, `table`, `callout`, `code`, and
  `rule`, but most variants still carry only `title + body`.
- There is no first-class representation yet for readable requirement
  qualifiers, readable guards, typed table columns/rows/notes, typed list or
  definition entries, `callout.kind`, `code.language`, or multiline code text.

## 4.4 Observability + failure behavior today

- Positive proof exists for the narrow slice through
  `examples/56_document_structure_attachments`.
- Negative proof for `structure:` currently covers non-markdown output shapes
  in example `56`.
- Document inheritance already fails loudly on duplicate keys, undefined
  overrides, kind mismatches, and missing inherited accounting inside
  `_resolve_document_body()`.
- Addressability already fails loudly through generic `Unknown addressable path`
  and `Addressable path must stay addressable` diagnostics, but the document
  path tree ends at top-level keyed blocks.
- `doctrine/diagnostic_smoke.py` already checks the structure-attachment path,
  but there is no smoke coverage yet for the richer readable-markdown failures
  the spec describes.
- The main failure mode today is split truth: the grammar, compiler, renderer,
  docs, and editor all know part of readable markdown, but they do not agree on
  the same full contract.

## 4.5 UI surfaces (ASCII mockups, if UI work)

UI scope is limited to the repo-local VS Code extension:

- TextMate grammar already recognizes `document` declarations and current block
  keywords.
- `resolver.js` already provides Ctrl/Cmd-click and definition support for
  `structure:` refs and document addressable refs such as `Decl:section.title`.
- `language-configuration.json` already indents current document block headers.
- The extension does not yet model richer header qualifiers or typed inner
  containers from the full spec.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- `doctrine/grammars/doctrine.lark` defines one shared readable-block grammar
  that can be embedded by `document_body` and the intended readable sub-bodies
  instead of keeping document-only richness plus legacy bodies elsewhere.
- `doctrine/model.py` and `doctrine/parser.py` define one typed readable AST
  with shared header metadata and typed payload nodes.
- `doctrine/compiler.py` owns one resolved and compiled readable pipeline plus
  one addressability tree for readable descendants.
- `doctrine/renderer.py` owns one markdown renderer for readable blocks, with
  no shell-only fallback path kept alive beside the typed path.
- `examples/` owns the full positive and compile-negative readable-markdown
  ladder after `57`.
- evergreen `docs/` and `editors/vscode/**` mirror the same shipped surface.

## 5.2 Control paths (future)

1. Parse the full readable header contract
   `<block_kind> <key>: "Title" <requirement>? <guard>?` plus typed payload
   containers such as `columns:`, `rows:`, `notes:`, `kind:`, `language:`, and
   multiline `text:`.
2. Reuse the same typed readable-block model across `document` and the intended
   readable bodies in `record_body`, `output_record_body`,
   `workflow_section_body`, and `skill_entry_body`, while preserving the
   backward-compatible keyed-section authoring forms the spec explicitly keeps.
3. Resolve document inheritance, block overrides, requirement metadata, guard
   metadata, and typed descendants through shared compiler helpers.
4. Keep `structure:` owner-aware and document-only on markdown-bearing inputs
   and outputs; do not widen it into a second output-shape system.
5. Compile readable blocks into one richer IR that preserves block kind,
   requirement, optional guard text, and typed descendants needed for rendering
   and addressability.
6. Render contract markdown so only `section` increments heading depth, while
   `sequence`, `bullets`, `checklist`, `definitions`, `table`, `callout`,
   `code`, and `rule` emit through their own markdown-native forms plus the
   italic metadata line where contract view requires it.
7. Extend addressability so document descendants can resolve table columns,
   table rows when present, and keyed list/definition items through the same
   addressable-path machinery used elsewhere in Doctrine.
8. Mirror the same shipped surface in the VS Code resolver, TextMate grammar,
   indentation rules, alignment validator, and editor smoke guidance.

## 5.3 Object model + abstractions (future)

- Split readable blocks into a shared header plus typed payload rather than
  `title + prose` shells.
- Represent typed descendants explicitly:
  - section bodies
  - list/checklist item sequences
  - keyed definition items
  - table columns, optional rows, and notes
  - callout metadata plus body
  - code metadata plus multiline text
  - rule blocks
- Keep a resolved form that carries inherited metadata, interpolated prose, and
  typed descendants.
- Keep a compiled form that retains block semantics needed by both the markdown
  renderer and readable descendant addressability.
- Preserve current `document` root identity and `structure:` attachment objects
  rather than inventing a second document registry.

## 5.4 Invariants and boundaries

- One readable-block pipeline across grammar, parser, compiler, renderer, and
  editor parity.
- `structure:` resolves only to `document` and only on markdown-bearing input
  and output shapes.
- `section` is the only block kind that increments heading depth.
- Non-section blocks render through their own markdown forms, not titled shells.
- Document override preserves block kind.
- Validation stays fail loud for duplicate keys, missing inherited accounting,
  kind mismatches, invalid readable payload shapes, bad `callout.kind`, bad
  `code.text` form, invalid table cell/column usage, and illegal guard reads.
- Keyed-section sugar and existing emphasized lines remain legal where the spec
  explicitly preserves them.
- `properties`, explicit `guard` blocks, `render_profile`, `row_schema:`, and
  `item_schema:` stay deferred unless a later planning pass explicitly promotes
  them.
- No raw markdown escape hatch, HTML-specific constructs, images, footnotes,
  nested tables, or runtime shims.

## 5.5 UI surfaces (ASCII mockups, if UI work)

UI scope remains repo-local editor parity:

- TextMate grammar highlights the full readable header surface, including
  requirement keywords and `when` guards where shipped.
- Resolver and navigation logic understand readable descendant paths once the
  compiler ships them.
- Enter indentation and body-container tracking recognize typed child blocks
  such as `columns:`, `rows:`, `notes:`, `kind:`, `language:`, and multiline
  `text:`.
- The VS Code README smoke ladder extends beyond example `57` to the new
  readable-markdown proof cases.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar core | `doctrine/grammars/doctrine.lark` | `document_body`, `document_block`, `document_override_block` | Document headers exist, but bodies are only `block_lines` and overrides only replace flat blocks | Add requirement / guard qualifiers, typed payload productions, and multiline string literal support | The authored surface must express the spec directly | One shared readable-block grammar contract | New readable examples, parser negatives, VS Code alignment |
| Grammar reuse | `doctrine/grammars/doctrine.lark` | `record_body`, `output_record_body`, `workflow_section_body`, `skill_entry_body` | Intended readable surfaces still use separate legacy body shapes | Reuse the shared readable-block sublanguage on the intended bodies without inventing a second mini-language | Readable markdown must not remain document-only | One readable sublanguage across intended surfaces | New non-document readable examples, VS Code resolver/alignment |
| AST | `doctrine/model.py` | `DocumentBlock`, `DocumentOverrideBlock`, `DocumentBody`, `InputStructureConfig`, `OutputStructureConfig` | Document blocks are `kind + key + title + items` shells | Introduce typed readable header and payload nodes while preserving document roots and structure attachments | Compiler and renderer need first-class semantics | Typed readable block model with explicit descendants | Compiler/render tests, manifests |
| Parser | `doctrine/parser.py` | `document_decl`, `document_block`, `document_override_block`, body parsers | Parses only the narrow document shell model and legacy non-document bodies | Parse the full readable contract and fail loudly on invalid typed readable usage | Parser must own structure rather than tolerate shell-like approximations | Typed parse path across intended surfaces | Negative corpus, diagnostics |
| Resolution | `doctrine/compiler.py` | `_resolve_document_decl`, `_resolve_document_body`, document block resolution | Inheritance and interpolation already work, but only at coarse block level | Resolve typed descendants, readable qualifiers, and guard metadata through the existing document pipeline | Reuse the current explicit-accounting owner path | One resolved readable model | New compile-fail cases, manifests |
| Structure attachments | `doctrine/compiler.py` | `_flow_input_detail_lines`, `_flow_output_detail_lines`, `_compile_output_decl` | `structure:` already resolves to documents and embeds shellish document sections | Keep `structure:` typed and document-only while rendering through the richer readable pipeline | Attachment semantics are already shipped and must stay owner-aware | Stable `structure:` contract with richer rendered body | Example `56`, new structure-focused manifests |
| Readable IR | `doctrine/compiler.py` | `_compile_document_decl`, `_compile_document_body`, `_compile_document_block`, compiled readable unions | Block union exists, but most variants still carry only title and body tuples | Retain one compiled readable owner path while adding requirement / guard / typed descendant data | Prevent a second renderer path or shell shim | One compiled readable IR | Manifests, renderer checks |
| Addressability | `doctrine/compiler.py` | `_resolve_addressable_path_node`, `_get_addressable_children`, `_document_items_to_addressable_children` | Document paths stop at top-level keyed blocks | Extend readable descendants for table columns, rows when present, and keyed list / definition items | Addressable readable descendants are part of the language contract | Widened readable path contract | New addressability examples, VS Code |
| Renderer | `doctrine/renderer.py` | `render_markdown`, `_render_block`, `_render_titled_block`, `_render_list_block`, `_render_code_block`, `_render_rule_block` | `definitions`, `table`, and `callout` still inherit titled-shell behavior; contract metadata lines are absent | Render each block kind through markdown-native semantics and emit contract metadata lines where required | Emitted markdown is part of language truth | Final readable markdown contract | New render_contract manifests, docs |
| Diagnostics | `doctrine/diagnostics.py`, `docs/COMPILER_ERRORS.md` | compile-pattern mapping and error catalog | Document inheritance reuses generic inherited-entry codes; richer readable failures are undocumented | Add readable-markdown validation coverage and keep the public error catalog honest | Fail-loud rules must be documented and stable | Documented readable failure families | `make verify-diagnostics`, compile-fail corpus |
| Diagnostic smoke | `doctrine/diagnostic_smoke.py` | structure-attachment smoke and new readable probes | Smoke covers `structure:` but not the richer readable failures | Add stable smoke checks for key readable diagnostics that are easy to regress | Keep a fast confidence signal beside the corpus | Stable smoke coverage for readable diagnostics | `make verify-diagnostics` |
| Corpus | `examples/README.md`, new example dirs after `57` | current readable ladder | Only the narrowed document slice is proven today | Add the full positive and compile-negative readable-markdown ladder after `57` | The wave is not shipped until it is manifest-backed | Manifest-backed readable proof ladder | `make verify-examples`, targeted manifests |
| Evergreen docs | `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/REVIEW_SPEC.md`, `docs/COMPILER_ERRORS.md` | live readable-markdown truth | Docs currently mix shipped truth, second-wave design framing, and partial readable support | Rewrite the live docs to match the actual shipped readable surface | No split-brain truth in evergreen docs | One live docs story | Doc review, repo verification |
| Editor resolver | `editors/vscode/resolver.js` | document block regexes, body-container tracking, readable ref resolution | Recognizes current document block headers and readable refs, but not the full typed inner-block surface | Support richer headers, child containers, and readable descendant refs through the same resolver path | Editor clicks must mirror compiler truth | One resolver parity contract | `cd editors/vscode && make` |
| Editor grammar / indent | `editors/vscode/syntaxes/doctrine.tmLanguage.json`, `editors/vscode/language-configuration.json` | tokens and onEnter rules | Current keyword and indent coverage reaches the shipped shell surface only | Add tokens and indentation rules for shipped readable qualifiers and typed child containers | Prevent editor-only grammar drift | One editor syntax / indent contract | `cd editors/vscode && make`, alignment validator |
| Editor parity tests | `editors/vscode/scripts/validate_lark_alignment.py`, `editors/vscode/tests/**`, `editors/vscode/README.md` | alignment fixtures, snapshots, smoke guidance | Current second-wave fixtures and smoke docs stop at examples `54` through `57` | Extend fixtures, tests, and README smoke checks to the new readable ladder | Packaging the extension is part of shipping truth | One editor test and smoke story | `cd editors/vscode && make` |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - authored surface: `doctrine/grammars/doctrine.lark` +
    `doctrine/parser.py` + `doctrine/model.py`
  - compile/render path: `doctrine/compiler.py` + `doctrine/renderer.py`
  - proof path: `examples/**` + `doctrine/verify_corpus.py` +
    `doctrine/diagnostic_smoke.py`
  - editor parity path: `editors/vscode/**`
- Deprecated APIs (if any):
  - no public CLI or declaration family is being removed
  - the internal shell-style assumption that non-section readable blocks can be
    treated as titled sections is retired
  - the implicit expectation that document blocks only carry flat `block_lines`
    is retired
- Delete list (what must be removed):
  - renderer branches or assumptions that preserve titled-shell semantics as an
    equal live behavior once typed block rendering ships
  - stale evergreen doc claims that readable markdown is either only a design
    reference or already fully shipped when the code disagrees
  - any editor heuristics that keep a second readable grammar alive after the
    canonical grammar changes
- Capability-replacing harnesses to delete or justify:
  - none should be added
  - do not add a standalone readable formatter, migration shim, or fallback
    renderer
- Live docs/comments/instructions to update or delete:
  - `docs/README.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/REVIEW_SPEC.md`
  - `docs/COMPILER_ERRORS.md`
  - `examples/README.md`
  - `editors/vscode/README.md`
  - only update non-evergreen umbrella plan docs if they still contradict the
    shipped surface after implementation
- Behavior-preservation signals for refactors:
  - targeted manifest proof for `examples/56_document_structure_attachments`
  - new readable-markdown manifests after `57`
  - `make verify-examples`
  - `make verify-diagnostics`
  - `cd editors/vscode && make`
  - `doctrine/diagnostic_smoke.py`

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Readable descendants | `doctrine/compiler.py::_get_addressable_children` | Extend the existing addressable tree instead of adding document-specific descendant lookup | Prevents a second readable addressability system | include |
| Shared readable parsing | `doctrine/grammars/doctrine.lark` + `doctrine/parser.py` | Reuse one readable-block grammar across intended bodies | Prevents document-only richness plus parallel legacy readable bodies | include |
| Render metadata lines | `doctrine/renderer.py` | Centralize contract metadata-line rendering across readable blocks | Prevents block helpers from inventing inconsistent contract prose | include |
| Diagnostic catalog sync | `doctrine/diagnostics.py` + `docs/COMPILER_ERRORS.md` + `doctrine/diagnostic_smoke.py` | Treat readable diagnostics as one documented surface | Prevents hidden or uncatalogued readable failures | include |
| Evergreen readable docs | live `docs/` + `examples/README.md` + `editors/vscode/README.md` | Rewrite shipped truth in the same cutover | Prevents another half-shipped readable wave | include |
| Umbrella readable plan docs | `docs/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md`, `docs/DOCTRINE_INTEGRATION_SURFACES_FULL_IMPLEMENTATION_2026-04-11.md` | Clean up only if they still mislead after the code cutover | Prevents status confusion without broadening the feature scope | defer |
| Raw markdown escape hatch | none | Keep v1 closed to escape hatches and shims | Prevents architecture creep and dual truth | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:reference_pack:start -->
# Reference Pack (folded materials; phase-aligned)
Updated: 2026-04-11

## Inventory
- R1 — Readable Markdown And Document Rendering Spec — `docs/READABLE_MARKDOWN_SPEC.md`

## Binding obligations (distilled; must satisfy)
- Ship the full readable-markdown system defined in `R1`, not just the
  currently shipped `document` + `structure:` subset. (From: R1)
- Keep `document` as a first-class readable, addressable, inheritable markdown
  schema declaration rather than a document-only shell. (From: R1)
- Ship the shared readable block sublanguage across the intended readable
  Doctrine surfaces, including `document`, record/output contract bodies,
  workflow section bodies, and skill-entry bodies. (From: R1)
- Support block kinds `section`, `sequence`, `bullets`, `checklist`,
  `definitions`, `table`, `callout`, `code`, and `rule` as first-class typed
  semantics, not title-plus-prose approximations. (From: R1)
- Support the common block header contract:
  `<block_kind> <key>: "Title" <requirement>? <guard>?`, including
  `required`, `advisory`, `optional`, and `when <expr>`. (From: R1)
- Keep `structure:` as a typed attachment for markdown-bearing inputs and
  outputs that resolves only to `document`; do not widen it into a prose
  convention or a second output-shape path in v1. (From: R1)
- Ship keyed descendant addressability for the descendants the spec declares
  addressable, including keyed document blocks, table columns, table rows when
  present, and keyed list/definition items; anonymous list items remain
  non-addressable. (From: R1)
- Preserve explicit inheritance accounting for `document`; `override` must
  target inherited entries and preserve block kind. (From: R1)
- Enforce fail-loud validation for document structure, table columns/rows,
  keyed list/definition uniqueness, `callout.kind`, `code.text` multiline form,
  and guard visibility rules. (From: R1)
- Keep backward compatibility explicit: current keyed sections remain legal as
  sugar for `section`, existing emphasized lines remain legal, and rich blocks
  are opt-in. (From: R1)
- Make renderer behavior match the spec's markdown contract: only `section`
  consumes heading depth; non-section blocks render through markdown-native
  forms; contract view emits italic metadata lines. (From: R1)
- Treat multiline string support as core language work when needed for readable
  `code` blocks. (From: R1)
- Treat `properties`, explicit `guard` blocks, `render_profile`, `row_schema:`,
  and `item_schema:` as explored/deferred surfaces, not first-wave ship
  blockers unless a later core planning command explicitly adopts them.
  (From: R1)
- Do not add raw markdown escape hatches, HTML-specific constructs, footnotes,
  images, nested tables, or domain-specific table semantics in Doctrine core
  v1. (From: R1)

## Instruction-bearing structure (only when present; preserve exact or equivalent operational form)
### R1 — Readable Markdown And Document Rendering Spec
1. Ship one coherent readable-markdown feature rather than renderer heuristics.
2. Keep `document` as the new top-level markdown schema declaration.
3. Reuse the same rich block sublanguage across the intended readable surfaces,
   not just `document`.
4. Treat renderer semantics as part of the language contract, not optional
   presentation polish.
5. Extend example and compile-negative proof until the readable-markdown system
   is manifest-backed.
- Hard negatives:
  - Do not scope the work to the current narrowed subset.
  - Do not add raw markdown escape hatches, HTML-specific constructs,
    footnotes, images, nested tables, or domain-specific table semantics in v1.
  - Do not silently promote `properties`, `guard`, `render_profile`,
    `row_schema:`, or `item_schema:` into the first shipped wave without an
    explicit later planning decision.
- Escalation or branch conditions:
  - Treat explored future artifact skeleton rendering as non-required for first
    ship.
  - Treat the expanded typed-markdown primitives as deferred unless later
    planning explicitly adopts them.

## Phase alignment guidance (advisory; core planning commands adopt into Section 7 if needed)
### Global (applies across phases)
- Keep the full spec scope live instead of narrowing to the currently shipped
  slice. (From: R1)
- Keep one readable-block compiler and renderer path. (From: R1)
- Preserve backward-compatibility promises explicitly and fail loud on new
  readable misuse. (From: R1)
- Keep deferred second-wave primitives deferred unless a later core planning
  command explicitly promotes them. (From: R1)

### Phase 1 — Full readable grammar and AST contract
- Potentially relevant obligations (advisory):
  - Support the common block header shape, typed inner block shapes, and
    multiline string syntax. (From: R1)
  - Encode explicit `document` inheritance and block-kind invariants in the AST
    and parser. (From: R1)
  - Encode fail-loud validation for document structure, tables,
    lists/definitions, callouts, code blocks, and guards. (From: R1)
- References:
  - R1

### Phase 2 — Compiler, renderer, and addressability convergence
- Potentially relevant obligations (advisory):
  - Compile rich block semantics through one readable pipeline. (From: R1)
  - Render only `section` through heading-depth increments and render
    non-section blocks through markdown-native forms. (From: R1)
  - Add descendant addressability for keyed readable descendants the spec makes
    addressable. (From: R1)
  - Emit italic metadata lines in contract view. (From: R1)
- References:
  - R1

### Phase 3 — Shared readable sublanguage rollout
- Potentially relevant obligations (advisory):
  - Extend rich readable blocks beyond `document` into the intended record,
    output, workflow, and skill-entry surfaces. (From: R1)
  - Keep `structure:` typed and limited to markdown-bearing contracts in v1.
    (From: R1)
  - Preserve old keyed-section authoring and emphasized lines as explicit
    backward-compatible surfaces. (From: R1)
- References:
  - R1

### Phase 4 — Corpus, docs, and diagnostics truth cutover
- Potentially relevant obligations (advisory):
  - Ship the readable-markdown acceptance corpus and compile-negative set.
    (From: R1)
  - Converge live docs on shipped renderer, addressability, validation, and
    deferred-surface truth. (From: R1)
  - Keep explored/deferred primitives out of the shipped v1 story unless later
    adopted explicitly. (From: R1)
- References:
  - R1

### Phase 5 — VS Code parity and final repo verification
- Potentially relevant obligations (advisory):
  - Mirror the full shipped readable-markdown surface in syntax, resolver,
    README, and tests. (From: R1)
  - Keep extension truth aligned with the same readable-block and
    addressability contracts the compiler ships. (From: R1)
- References:
  - R1

## Folded sources (verbatim; inlined so they cannot be missed)
### R1 — Readable Markdown And Document Rendering Spec — `docs/READABLE_MARKDOWN_SPEC.md`
~~~~markdown
# Readable Markdown And Document Rendering Spec

This document defines the readable-output layer for the proposed language
enhancement:

- the first-class `document` declaration
- the shared readable block sublanguage
- the richer compiled markdown block AST
- the rendering rules that keep emitted AGENTS.md and contract output natural
  instead of mechanically mirroring source nesting

The problem this work addresses is structural, not cosmetic.

The current renderer fundamentally walks nested compiled sections and turns
structure into deeper heading depth. Emphasized lines are the only real
non-heading format in the current surface. That means rich semantic differences
collapse into `##`, `###`, and `####`, and the output reads as outline depth
instead of document shape.

The correct abstraction is a typed markdown layer shared by all readable
Doctrine surfaces, with a first-class `document` declaration at the top and a
richer block AST underneath it.

## Core decision

Add a first-class readable document system to Doctrine, and make the markdown
renderer operate on semantic block kinds instead of only `section -> heading`.

The boundary is:

- Doctrine owns structure and rendering semantics.
- Domain packs own document names, required blocks, table names, and domain
  columns.

Doctrine should know what a table, sequence, definitions list, callout, code
block, and rule are.
Domain packs should decide that one particular table is called `Step Arc Table`
or `Guided-Walkthrough Beat-Count Table`.

## What ships

Ship one coherent feature, not a pile of renderer heuristics.

### New top-level declaration

```prompt
document LessonPlan: "Lesson Plan"
    ...
```

### New readable block kinds

The block kinds proposed for the readable-output layer are:

- `section` - heading plus block body
- `sequence` - ordered list
- `bullets` - unordered list
- `checklist` - task list
- `definitions` - compact term/explanation list
- `table` - markdown table
- `callout` - blockquote-style admonition
- `code` - fenced code block
- `rule` - thematic break

An earlier, smaller design sketch started with only:

- `document`
- `section`
- `sequence`
- `table`
- `callout`

The fuller rendering spec expands that set to cover the rest of the readable
surfaces that currently collapse into heading ladders.

### New attachment point on markdown-bearing contracts

Any markdown-bearing input or output contract may attach a document schema
through:

```prompt
structure: LessonPlan
```

### New renderer model

Replace the heading-only compiled output tree with a richer block AST:

```text
CompiledBlock =
    ParagraphBlock
    | SectionBlock
    | ListBlock
    | DefinitionsBlock
    | TableBlock
    | CalloutBlock
    | CodeBlock
    | RuleBlock
```

Existing authored sections compile to `SectionBlock`.
Existing emphasized prose lines compile to either an inline emphasized paragraph
or a `CalloutBlock` shell, depending on context.

An even richer rendering architecture explored during design work inserts an
explicit semantic readback layer first:

```text
Doctrine AST
    -> semantic readback IR
    -> typed markdown IR
    -> markdown text
```

That richer model is especially valuable for reviews, route-only comments, and
bounded-scope metadata panels because those surfaces want compact fact panels
and guarded comment blocks rather than more heading depth.

## Canonical document language spec

### `document`

A document is a named, addressable, inheritable schema for a markdown artifact.

Canonical form:

```prompt
document LessonPlan: "Lesson Plan"
    section lesson_promise: "Lesson Promise" required
        "State what this lesson owns now."

    sequence step_order: "Step Order" required
        "State the step order and what each step is there to teach."

    table step_arc: "Step Arc Table" required
        columns:
            step: "Step"
                "Step identifier or ordinal."
            role: "Role"
                "`introduce`, `practice`, `test`, or `capstone`."
            introduces: "Introduces"
                "What is genuinely introduced here."
            coaching_level: "Coaching Level"
                "How explicit the help is."
            difficulty_curve: "Difficulty Curve"
                "How challenge rises across the lesson."
        notes:
            "Add one row per step."
            "Make coaching taper explicit."
```

Semantics:

- `document` is a readable declaration like workflow, skills, inputs, and
  outputs.
- it is an addressable root
- it can be inherited and explicitly patched
- it describes the internal structure of markdown artifacts
- it does not describe operational workflow law

### Common block header shape

All document blocks share this header shape:

```text
<block_kind> <key>: "Title" <requirement>? <guard>?
```

Where:

- `<block_kind>` is one of the supported block types
- `<key>` is the stable symbolic identifier
- `"Title"` is the rendered human title
- `<requirement>` is one of:
  - `required`
  - `advisory`
  - `optional`
- `<guard>` is:
  - `when <expr>`

Examples:

```prompt
section lesson_promise: "Lesson Promise" required
table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" required when LessonFacts.walkthrough_in_scope
callout durable_truth: "Durable Truth" advisory
```

The stable symbolic key is law.
The human title is prose.

### Block kinds

#### `section`

```prompt
section lesson_promise: "Lesson Promise" required
    "State what this lesson owns now."
```

Semantics:

- renders as a heading section
- body may contain any readable block

#### `sequence`

```prompt
sequence read_order: "Read Order" required
    first: "Read the active issue."
    second: "Read the current issue plan."
    third: "Read the latest current comment."
```

Semantics:

- renders as an ordered list
- body items render in authored order
- keyed items are recommended because they remain addressable

#### `bullets`

```prompt
bullets trust_surface: "Trust Surface" required
    artifact: "Current Artifact"
    active_mode: "Active Mode when present(active_mode)"
    trigger_reason: "Trigger Reason when present(trigger_reason)"
```

Semantics:

- renders as an unordered list

#### `checklist`

```prompt
checklist release_checks: "Release Checks" required
    lint: "Run lint."
    tests: "Run the minimum test suite."
    proof: "Confirm the proof artifact exists."
```

Semantics:

- renders as markdown task-list items

#### `definitions`

```prompt
definitions must_include: "Must Include" required
    verdict: "Verdict"
        "Say `accept` or `changes requested`."
    reviewed_artifact: "Reviewed Artifact"
        "Name the reviewed artifact this review judged."
    analysis: "Analysis Performed"
        "Summarize the review analysis that led to the verdict."
```

Semantics:

- renders as compact term/explanation rows
- this is the clean replacement for many current
  `#### Must Include -> ##### Field Name` ladders

#### `table`

```prompt
table step_arc: "Step Arc Table" required
    columns:
        step: "Step"
            "Step identifier or ordinal."
        role: "Role"
            "`introduce`, `practice`, `test`, or `capstone`."
        introduces: "Introduces"
            "What is genuinely introduced here."
        coaching_level: "Coaching Level"
            "How explicit the help is."
        difficulty_curve: "Difficulty Curve"
            "How challenge rises across the lesson."

    notes:
        "Add one row per step."
```

Optional fixed-row or sample-row form:

```prompt
table sample_arc: "Sample Arc"
    columns:
        step: "Step"
        role: "Role"
        introduces: "Introduces"

    rows:
        row_1:
            step: "1"
            role: "introduce"
            introduces: "range advantage cue"
        row_2:
            step: "2"
            role: "practice"
            introduces: "none"
```

Rules:

- columns are ordered and keyed
- rows are optional
- row cells must reference only declared columns
- cells are inline markdown only, not nested block bodies
- column bodies in schema mode are short descriptions used by the contract
  renderer

#### `callout`

```prompt
callout durable_truth: "Durable Truth" required
    kind: important
    "This file owns the lesson job, pacing, and stable-vs-variable boundaries."
```

Allowed `kind` values in v1:

- `required`
- `important`
- `warning`
- `note`

This callout vocabulary should align with the current emphasized prose
vocabulary instead of inventing a second admonition family.

#### `code`

```prompt
code example_manifest: "Example Manifest" advisory
    language: json
    text: """
    {
      "title": "PLACEHOLDER: Lesson title",
      "steps": []
    }
    """
```

This requires a new multiline string literal in Doctrine. That change is
worthwhile on its own because code fences and rich examples are clumsy without
it.

#### `rule`

```prompt
rule section_break
```

Semantics:

- renders as `---`

## Extended readable-output layer

The readable block layer should not be document-only.

The same rich block kinds should be legal anywhere Doctrine currently emits
readable markdown content, especially:

- `record_body`
- `output_record_body`
- `workflow_section_body`
- `skill_entry_body`

That matters because the rendering problem is broader than artifact files.
Output contracts and review comment contracts are also clunky for the same
reason.

For example, this current shape:

```prompt
output DraftReviewComment: "Draft Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    must_include: "Must Include"
        verdict: "Verdict"
            "Say whether the review accepted the draft or requested changes."
        reviewed_artifact: "Reviewed Artifact"
            "Name the reviewed artifact this review judged."
```

should be writable as:

```prompt
output DraftReviewComment: "Draft Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    definitions must_include: "Must Include"
        verdict: "Verdict"
            "Say whether the review accepted the draft or requested changes."
        reviewed_artifact: "Reviewed Artifact"
            "Name the reviewed artifact this review judged."
        analysis_performed: "Analysis Performed"
            "Summarize the review analysis that led to the verdict."
```

So the architectural rule is:

- `document` is the new top-level markdown schema declaration
- rich block kinds are a shared sublanguage reused by documents and other
  readable Doctrine bodies

## `structure:` attachment on inputs and outputs

For markdown-bearing contracts:

```prompt
input LessonPlanContract: "Lesson Plan"
    source: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: MarkdownDocument
    structure: LessonPlan
    requirement: Required
```

and:

```prompt
output LessonPlanFileOutput: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: AgentOutputDocument
    structure: LessonPlan
    requirement: Required
```

Rules:

- `structure:` must resolve to a `document`
- it is descriptive and typed, not a prose convention
- it may appear on input and output
- in the future it may also appear on reusable output-shape declarations, but
  v1 does not need that

This is especially valuable because the same named document can serve as:

- an upstream input contract
- a downstream output contract
- a review basis

## Addressability, interpolation, and refs

`document` and all keyed descendants should be addressable through the same
path discipline Doctrine already uses for records and workflows.

Examples:

```text
{{LessonPlan:title}}
{{LessonPlan:step_arc.title}}
{{LessonPlan:step_arc.columns.coaching_level.title}}
{{LessonPlan:step_arc.columns.coaching_level}}
```

Addressability rules:

- document root is addressable
- keyed block children are addressable
- table columns are addressable
- table rows are addressable when present
- anonymous list items are not addressable
- keyed list and definition items are addressable

## Inheritance and patching

`document` should inherit with the same explicit accounting doctrine as
workflows and IO blocks.

Example:

```prompt
document BaseLessonPlan: "Lesson Plan"
    section lesson_promise: "Lesson Promise" required
        "State what this lesson owns now."

    table step_arc: "Step Arc Table" required
        columns:
            step: "Step"
            role: "Role"

document WalkthroughLessonPlan[BaseLessonPlan]: "Lesson Plan"
    inherit lesson_promise
    inherit step_arc

    table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" required
        columns:
            lesson: "Lesson"
            beat_count: "Beat Count"
            target_count: "Target Count"
            variance_reason: "Variance Reason"
```

Rules:

- inherited document blocks must be explicitly accounted for
- `override` may replace the body or title of a block
- block kind is invariant under override
- missing inherited block accounting is a compile error
- duplicate accounting is a compile error

## Guards and conditional blocks

Document blocks should support `when <expr>`.

Example:

```prompt
table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" required when LessonFacts.walkthrough_in_scope
    ...
```

Rules:

- guard syntax matches the existing expression syntax
- in contract render mode, guarded blocks render as conditional shells, not as
  runtime-evaluated presence
- expression visibility should reuse the same guard-expression restrictions as
  current guarded output sections
- a document block may not read emitted output fields directly through its
  guard

An earlier extension sketch also called out an explicit `guard` block kind as a
portable readable shell. The narrower document spec keeps `when <expr>` on
document blocks and avoids inventing a separate guard model.

## Backward compatibility

### Existing authored sections stay legal

Current readable keyed items:

```prompt
step_one: "Step One"
    "Say hello."
```

become semantic sugar for:

```prompt
section step_one: "Step One"
    "Say hello."
```

Old prompts do not need immediate rewrites.

### Existing emphasized lines stay legal

Current forms such as:

```prompt
required "Read this first."
important "Keep the current plan as truth."
```

remain legal and keep their current render behavior.

They may optionally compile to single-line callout blocks internally, but the
user-visible render should stay stable unless a prompt explicitly migrates to
blockquote callouts.

### Rich blocks are opt-in

Nothing breaks unless authors choose the new blocks.

## Markdown rendering spec

The key rendering rule is:

Only `section` consumes heading depth.
Everything else uses its own markdown syntax.

### Section

Contract render:

```markdown
### Lesson Promise

_Required · section_

State what this lesson owns now.
```

Artifact skeleton render:

```markdown
## Lesson Promise
```

### Sequence

Contract render:

```markdown
### Step Order

_Required · ordered list_

State the step order and what each step is there to teach.
```

If concrete items are present:

```markdown
### Read Order

_Required · ordered list_

1. Read the active issue.
2. Read the current issue plan.
3. Read the latest current comment.
```

### Bullets

```markdown
### Trust Surface

_Required · unordered list_

- Current Artifact
- Active Mode when present(active_mode)
- Trigger Reason when present(trigger_reason)
```

### Checklist

```markdown
### Release Checks

_Required · checklist_

- [ ] Run lint.
- [ ] Run tests.
- [ ] Confirm proof artifact exists.
```

### Definitions

Compact form:

```markdown
#### Must Include

_Required · definitions_

- **Verdict** — Say `accept` or `changes requested`.
- **Reviewed Artifact** — Name the reviewed artifact this review judged.
- **Analysis Performed** — Summarize the review analysis that led to the verdict.
```

Longer-form definition bodies:

```markdown
- **Reviewed Artifact**
  Name the reviewed artifact this review judged.
  When review stopped at handoff quality, name the producer handoff instead.
```

### Table

Schema-mode render:

```markdown
### Step Arc Table

_Required · table_

| Column | Meaning |
| --- | --- |
| Step | Step identifier or ordinal. |
| Role | `introduce`, `practice`, `test`, or `capstone`. |
| Introduces | What is genuinely introduced here. |
| Coaching Level | How explicit the help is. |
| Difficulty Curve | How challenge rises across the lesson. |

Add one row per step.
Make coaching taper explicit.
```

Row-bearing render:

```markdown
| Step | Role | Introduces | Coaching Level | Difficulty Curve |
| --- | --- | --- | --- | --- |
| 1 | introduce | range advantage cue | high | low |
| 2 | practice | none | medium | medium |
```

### Callout

Titled callout:

```markdown
> **IMPORTANT — Durable Truth**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.
```

Untitled or minimal callout:

```markdown
> **WARNING**
> Do not reopen upstream concept or playable decisions here.
```

### Code

````markdown
#### Example Manifest

_Advisory · code · json_

```json
{
  "title": "PLACEHOLDER: Lesson title",
  "steps": []
}
```
````

### Rule

```markdown
---
```

### Guarded block shell

```markdown
### Guided-Walkthrough Beat-Count Table

_Required · table · when walkthrough is in scope_

| Column | Meaning |
| --- | --- |
| Lesson | Nearby walkthrough lesson. |
| Beat Count | Actual comparable beat count. |
| Target Count | Planned beat count here. |
| Variance Reason | Why this lesson keeps or breaks the corridor. |
```

## Fully formed `LessonPlan` example

Doctrine source:

```prompt
document LessonPlan: "Lesson Plan"
    callout durable_truth: "Durable Truth" advisory
        kind: important
        "This file owns the lesson job, pacing, and stable-vs-variable boundaries."

    section lesson_promise: "Lesson Promise" required
        "State what this lesson owns now."

    sequence step_order: "Step Order" required
        "State the step order and what each step is there to teach."

    definitions step_roles: "Step Roles" required
        introduce: "Introduce"
            "Name what each step is doing using `introduce`."
        practice: "Practice"
            "Name what each step is doing using `practice`."
        test: "Test"
            "Name what each step is doing using `test`."
        capstone: "Capstone"
            "Name what each step is doing using `capstone`."

    table prior_lesson_counts: "Prior-Lessons Step-Count Table" required
        columns:
            lesson: "Lesson"
                "Nearby lesson used as precedent."
            step_count: "Step Count"
                "Actual step count in that lesson."
            comparable_kind: "Comparable Kind"
                "True comparable, same-route precedent, or fallback."
            target_count: "Target Count"
                "Planned count for the current lesson."
            variance_reason: "Variance Reason"
                "Why the current lesson keeps or breaks pattern."

    table walkthrough_beats: "Guided-Walkthrough Beat-Count Table" required when LessonFacts.walkthrough_in_scope
        columns:
            lesson: "Lesson"
                "Nearby walkthrough lesson."
            beat_count: "Beat Count"
                "Actual comparable beat count."
            target_count: "Target Count"
                "Planned beat count here."
            variance_reason: "Variance Reason"
                "Why this lesson keeps or breaks the corridor."

    table step_arc: "Step Arc Table" required
        columns:
            step: "Step"
                "Step identifier or ordinal."
            role: "Role"
                "The step role."
            introduces: "Introduces"
                "What is genuinely introduced here."
            coaching_level: "Coaching Level"
                "How explicit the help is."
            difficulty_curve: "Difficulty Curve"
                "How challenge rises."

    section guidance_plan: "Guidance Plan" required
        "Say how much help each step or step group should give."

    section new_vs_reinforced_vs_deferred: "New Vs Reinforced Vs Deferred" required
        "Say what is genuinely new, what is reinforced, and what stays deferred."

    section nearby_lesson_evidence: "Nearby-Lesson Evidence" required
        "Keep nearby-lesson evidence separate from real comparable-lesson proof."

    table real_comparables: "Real Comparable Lessons" required
        columns:
            lesson: "Lesson"
                "Named comparable lesson."
            route_match: "Route Match"
                "Same-route, partial, or fallback."
            burden_match: "Burden Match"
                "Similar, lighter, or heavier."
            why: "Why"
                "Why this comparison is honest."

    section why_not_shorter: "Why Not Shorter" required
        "Explain what burden or install-before-test work would be lost."

    section why_not_longer: "Why Not Longer" required
        "Explain why extra steps would exceed earned burden."

    section stable_vs_variable: "Stable Vs Variable" required
        "State what later lanes must keep stable and what may vary safely."
```

Output contract:

```prompt
output LessonPlanFileOutput: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: AgentOutputDocument
    structure: LessonPlan
    requirement: Required
```

Contract render:

```markdown
### Lesson Plan File

- Target: File
- Path: `lesson_root/_authoring/LESSON_PLAN.md`
- Shape: Agent Output Document
- Structure: Lesson Plan
- Requirement: Required

#### Structure: Lesson Plan

> **IMPORTANT — Durable Truth**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.

##### Lesson Promise

_Required · section_

State what this lesson owns now.

##### Step Order

_Required · ordered list_

State the step order and what each step is there to teach.

##### Step Roles

_Required · definitions_

- **Introduce** — Name what each step is doing using `introduce`.
- **Practice** — Name what each step is doing using `practice`.
- **Test** — Name what each step is doing using `test`.
- **Capstone** — Name what each step is doing using `capstone`.

##### Prior-Lessons Step-Count Table

_Required · table_

| Column | Meaning |
| --- | --- |
| Lesson | Nearby lesson used as precedent. |
| Step Count | Actual step count in that lesson. |
| Comparable Kind | True comparable, same-route precedent, or fallback. |
| Target Count | Planned count for the current lesson. |
| Variance Reason | Why the current lesson keeps or breaks pattern. |

##### Guided-Walkthrough Beat-Count Table

_Required · table · when walkthrough is in scope_

| Column | Meaning |
| --- | --- |
| Lesson | Nearby walkthrough lesson. |
| Beat Count | Actual comparable beat count. |
| Target Count | Planned beat count here. |
| Variance Reason | Why this lesson keeps or breaks the corridor. |

...
```

Optional future artifact skeleton render:

```markdown
# Lesson Plan

> **IMPORTANT**
> This file owns the lesson job, pacing, and stable-vs-variable boundaries.

## Lesson Promise

## Step Order

1.
2.
3.

## Step Roles

- **Introduce** -
- **Practice** -
- **Test** -
- **Capstone** -

## Prior-Lessons Step-Count Table

| Lesson | Step Count | Comparable Kind | Target Count | Variance Reason |
| --- | --- | --- | --- | --- |

## Guided-Walkthrough Beat-Count Table

| Lesson | Beat Count | Target Count | Variance Reason |
| --- | --- | --- | --- |

## Step Arc Table

| Step | Role | Introduces | Coaching Level | Difficulty Curve |
| --- | --- | --- | --- | --- |
```

That skeleton mode is not required to ship the language, but the AST should
make it possible with no redesign.

## Extended typed-markdown design explored for second wave

An expanded version of the readable-output system introduced three more
primitives to support review comments, route-only handoffs, and bounded-scope
panels:

- `properties`
- `guard`
- `render_profile`

The motivation for each:

- `properties` covers compact labeled facts like Target, Path, Shape,
  Requirement, Current Artifact, Next Owner, Metadata Mode, and similar
  surfaces that degrade into bullets or extra headings today
- `guard` makes route-only and failure-detail blocks elegant instead of awkward
- `render_profile` lets the same underlying semantic structure render
  differently in AGENTS contract view, artifact shell view, and comment view

An expanded design sketch proposed three canonical render profiles:

```prompt
render_profile ContractMarkdown
render_profile ArtifactMarkdown
render_profile CommentMarkdown
```

and later, lightly patchable domain-specific profiles such as:

```prompt
render_profile LessonsHome:
    current_artifact -> sentence
    own_only -> sentence
    preserve_exact -> sentence
    review.contract_checks -> titled_section
    analysis.stages -> natural_ordered_prose
    guarded_sections -> concise_explanatory_shell
```

The three canonical profile roles:

- `ContractMarkdown` explains required structure
- `ArtifactMarkdown` produces a natural authored shell
- `CommentMarkdown` stays compact, favoring fact panels and guarded callouts

### Typed row and item schemas explored later

One broader document-design sketch also explored optional symbolic row and item
typing on readable blocks:

```prompt
sequence step_order: "Step Order" required
    item_schema: StepOrderItem
    "State the step order and what each step is there to teach."

table step_arc: "Step Arc Table" required
    row_schema: StepArcRow
    columns:
        step: "Step"
        role: "Role"
        introduces: "Introduces"
```

The attraction of these fields was:

- make rows and sequence items symbolic instead of only visual
- give later review, preservation, and schema-contract work a stable way to
  talk about row or item shape
- keep contract view and artifact-shell view aligned without relying only on
  prose descriptions of columns

The later narrowed recommendation did not put `row_schema:` or `item_schema:`
in the first wave.

Reasons:

- block-level titles, requirements, and column declarations already buy most of
  the first readability win
- row and item typing adds another layer of resolution and validation that is
  not required for the initial document rollout
- revisit it only if later review-contract or preservation work needs stable
  symbolic row/item references

### Comment document shape with `properties`

```prompt
document RouteOnlyHandoff: "Routing Handoff Comment"
    properties must_include: "Must Include"
        current_route: "Current Route"
        next_owner: "Next Owner"
        next_step: "Next Step"

    callout rewrite_mode: "Rewrite Mode" when RouteFacts.section_status in {"new", "full_rewrite"}
        kind: note
        "Later section metadata must be rewritten instead of inherited."

    section repeated_problem: "Repeated Problem" when RouteFacts.critic_miss_repeated
        properties:
            failing_pattern: "What Keeps Failing"
            returned_from: "Returned From"
            next_fix: "Next Concrete Fix"

    section standalone_read: "Standalone Read"
        "A downstream owner should be able to read this comment alone and understand that no specialist artifact is current, what route-only state is now in force, who owns next, and what the next concrete step is."
```

Rendered as compact comment markdown:

```markdown
## Routing Handoff Comment

- Current Route: route-only turn; no specialist artifact is current
- Next Owner: LessonsProjectLead
- Next Step: repair ownership justification

> **NOTE — Rewrite Mode**
> Later section metadata must be rewritten instead of inherited.

### Repeated Problem

- What Keeps Failing: critic keeps rejecting vague metadata handoff
- Returned From: LessonsAcceptanceCritic
- Next Concrete Fix: make section-mode preserve basis explicit
```

### Review lowering into typed markdown

The readable-output system should also be able to serve as the render target for
review semantics.

Given a semantic review:

```prompt
review LessonPlanReview: "Lesson Plan Review"
    subject: LessonPlanFile
    contract: LessonPlanContract
    comment_output: CriticVerdictComment
```

the internal lowering can target a document shape like:

```prompt
document CriticVerdictComment: "Verdict And Handoff Comment"
    properties summary: "Review State"
        verdict: "Verdict"
        reviewed_artifact: "Reviewed Artifact"
        next_owner: "Next Owner"
        current_artifact: "Current Artifact"

    section analysis_performed: "Analysis Performed"
    section output_contents_that_matter: "Output Contents That Matter"

    section failure_detail: "Failure Detail" when verdict == changes_requested
        sequence failing_gates: "Failing Gates"
        callout blocked_gate: "Blocked Gate" when blocked

    section trust_surface: "Trust Surface"
        sequence entries:
            "Current Artifact"
```

### Analysis lowering into typed markdown

A separate semantic `analysis` declaration can also lower into a document
according to profile.

Example semantic surface:

```prompt
analysis LessonPlanning: "Lesson Planning"
    stages:
        lesson_job:
            derive lesson_promise

        step_roles:
            derive step_roles

        continuity:
            derive prior_lesson_counts

        comparables:
            derive real_comparable_lessons

        pacing:
            derive pacing_judgment

        step_arc:
            derive step_arc

        boundaries:
            derive stable_vs_variable
```

Intended profile behavior:

- in AGENTS.md, render as numbered or titled planning stages
- in compact homes, render as "What To Decide" prose plus tables
- in artifact templates, render only the exported structures

### Bounded-scope and metadata panel example

The readable-output system can also render bounded-scope law and grounding
surfaces readably:

```prompt
document MetadataPassScope: "Metadata Pass Scope"
    properties route_state: "Route State"
        metadata_mode: "Metadata Mode"
        current_file: "Current File"
        preserve_basis: "Preserve Basis"
        rewrite_regime: "Rewrite Regime"

    callout scope: "Scope"
        kind: important
        "Own only title in lesson-title mode."
        "Own only name and description in section mode."

    callout preservation: "Preservation"
        kind: note
        "Preserve exact out-of-scope fields."
        "Preserve decisions from the preserve basis."
```

## Validation rules

These should fail loudly.

### Declaration-level rules

- `structure:` must resolve to a document
- document block keys must be unique
- inherited document blocks must be explicitly accounted for
- `override` must target an existing inherited key
- `override` must preserve block kind

### Table-specific rules

- table must have columns
- column keys must be unique
- rows may reference only declared columns
- row keys must be unique
- cells must be inline markdown, not nested blocks

### List and definitions rules

- keyed items must be unique within their block
- anonymous string items are allowed but not addressable
- mixing anonymous and keyed items is legal, but keyed items remain the
  canonical style

### Callout and code rules

- `callout.kind` must be in the closed core set
- `code.language` is optional
- `code.text` must use multiline string form
- multiline string syntax becomes a core Doctrine feature, not a code-block
  hack

### Guard rules

- `when` expressions on document blocks use the same expression language as
  output guards
- document guards may not read forbidden sources any more than guarded outputs
  may

## Renderer rules

These determine readability and should be treated as explicit spec.

- top-level agent fields still start at heading depth 2
- `SectionBlock` increments heading depth
- `ListBlock`, `DefinitionsBlock`, `TableBlock`, `CalloutBlock`, `CodeBlock`,
  and `RuleBlock` do not increment heading depth
- one blank line separates sibling blocks
- no empty heading shells
- inline code formatting remains authored responsibility
- `definitions` uses the compact one-line form when the definition body is a
  single paragraph
- `callout` renders with blockquote syntax, not heading syntax
- existing emphasized lines keep current rendering for backward compatibility
  unless explicitly rewritten as `callout`

Contract view should emit an italic metadata line such as:

```markdown
_Required · section_
_Required · table · when walkthrough is in scope_
_Advisory · code · json_
```

That status line does more work than deeper headings and keeps the output much
cleaner.

## Implementation plan for the readable-output system

Touch these files:

- `doctrine/grammars/doctrine.lark`
- `doctrine/model.py`
- `doctrine/parser.py`
- `doctrine/compiler.py`
- `doctrine/renderer.py`
- `examples/**` render-contract corpus and compile-negative corpus

Concrete compiler changes:

`model.py`

- add `DocumentDecl`
- add document block node types
- add multiline string node if triple-quoted strings are introduced

`compiler.py`

- replace the `CompiledSection`-only readable tree with a richer compiled block
  union
- map old keyed sections to `SectionBlock`
- compile `structure:` refs on inputs and outputs
- compile document addressable roots

`renderer.py`

- replace `_render_section()` recursion as the only readable-output path
- add block dispatch:
  - `_render_section_block`
  - `_render_list_block`
  - `_render_definitions_block`
  - `_render_table_block`
  - `_render_callout_block`
  - `_render_code_block`
  - `_render_rule_block`

`doctrine.lark`

- add `document_decl`
- add rich block items to document bodies
- add rich block items to record and workflow section bodies
- add multiline string literal

## Acceptance corpus for the readable-output system

Proposed example folders:

- `54_first_class_documents`
- `55_rich_blocks_in_output_contracts`
- `56_documents_with_tables_and_definitions`
- `57_document_inheritance`
- `58_document_guards`
- `59_multiline_strings_and_code_blocks`

Proposed compile-negative cases:

- `INVALID_STRUCTURE_REF_NON_DOCUMENT.prompt`
- `INVALID_DOCUMENT_DUPLICATE_BLOCK_KEY.prompt`
- `INVALID_DOCUMENT_OVERRIDE_KIND_MISMATCH.prompt`
- `INVALID_TABLE_ROW_UNKNOWN_COLUMN.prompt`
- `INVALID_TABLE_WITHOUT_COLUMNS.prompt`
- `INVALID_CALLOUT_UNKNOWN_KIND.prompt`
- `INVALID_CODE_BLOCK_WITHOUT_MULTILINE_STRING.prompt`

## What not to add in v1

To keep the feature elegant instead of sprawling:

- do not add raw markdown escape-hatch blocks in v1
- do not add HTML-specific constructs in v1
- do not add footnotes, images, or nested tables in v1
- do not put domain-specific table names or semantics in Doctrine core
~~~~
<!-- arch_skill:block:reference_pack:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria +
> explicit verification. Refactors and shared-path extractions must preserve
> existing behavior with the smallest credible signal. No fallbacks or runtime
> shims. For this feature, the canonical path is the existing
> grammar -> parser/model -> compiler -> renderer -> corpus/docs/editor chain.

## Phase 1 - Normalize the authored readable grammar and AST

Status: COMPLETED

Goal:
Make the full readable-markdown contract directly representable in the language
surface instead of leaving it split across shell-style blocks and spec prose.

Work:

- widen `doctrine/grammars/doctrine.lark` to support the full readable header
  contract, typed payload containers, and multiline string syntax needed for
  readable `code` blocks
- replace the current shell-style document node shapes in `doctrine/model.py`
  with a typed readable header plus typed payload model
- update `doctrine/parser.py` so `document` and the intended readable bodies
  parse the full readable surface through one shared block model
- preserve backward-compatible keyed-section authoring and existing emphasized
  lines as explicit legal authored forms instead of accidental leftovers

Verification (smallest signal):

- targeted parser probes for each block family and qualifier shape
- first manifest-backed readable example added as soon as the grammar can carry
  a typed block end to end
- `uv run --locked python editors/vscode/scripts/validate_lark_alignment.py`
  once grammar keywords or header forms change

Docs/comments (propagation; only if needed):

- add only high-leverage comments at the shared readable grammar or parser
  boundary where future drift would be expensive

Exit criteria:

- the full first-wave readable header and payload shapes are parseable and
  representable directly in the AST
- no intended readable surface still requires a second mini-language

Rollback:

- revert the widened grammar / model / parser slice if it leaves the repo in a
  mixed shell-plus-typed authored state

## Phase 2 - Resolve typed readable semantics in the compiler

Status: COMPLETED

Goal:
Move readable semantics, inheritance, guards, and validation into the canonical
compiler owner path.

Work:

- widen `doctrine/compiler.py::_resolve_document_body` and related helpers to
  resolve typed readable descendants, requirements, and guards
- keep `structure:` document-only and markdown-shape-only while routing it
  through the typed readable resolution path
- decide and implement the readable-markdown validation surface, including
  duplicate keys, override kind mismatches, invalid typed payloads, bad
  `callout.kind`, bad `code.text` form, and illegal guard reads
- update `doctrine/diagnostics.py` and `docs/COMPILER_ERRORS.md` if new
  readable diagnostics are introduced or if current generic codes need explicit
  readable coverage

Verification (smallest signal):

- focused compile-fail prompts for duplicate keys, undefined overrides, kind
  mismatches, invalid table shapes, invalid callout kind, invalid code text
  form, and illegal structure attachments
- `make verify-diagnostics` when diagnostics or hints change
- targeted manifest runs for the earliest readable examples

Docs/comments (propagation; only if needed):

- sync compiler-boundary comments that would otherwise preserve the old
  shell-only mental model

Exit criteria:

- readable validation is fail loud and routed through the canonical compiler
- the compiler no longer depends on raw `block_lines` as the true readable
  semantics

Rollback:

- revert this slice if the typed readable path still depends on a live legacy
  resolution branch

## Phase 3 - Renderer and addressability cutover

Status: COMPLETED

Goal:
Ship one readable markdown rendering contract and one readable descendant lookup
contract.

Work:

- widen the compiled readable IR only as needed to carry requirement metadata,
  guard metadata, and typed descendants
- replace shell-style rendering in `doctrine/renderer.py` with block-native
  rendering for `definitions`, `table`, `callout`, `code`, and `rule`
- emit the italic metadata line for contract view where the spec requires it
- extend readable addressability in `doctrine/compiler.py` to support table
  columns, row keys when present, and keyed list / definition items
- keep `structure:` rendering on markdown-bearing inputs and outputs on the
  same readable pipeline instead of a special shell path

Verification (smallest signal):

- new render-contract manifests for `definitions`, `table`, `callout`, `code`,
  `rule`, and descendant addressability
- targeted preservation run for
  `examples/56_document_structure_attachments/cases.toml`
- `make verify-examples`
- `make verify-diagnostics` if addressability or renderer errors change

Docs/comments (propagation; only if needed):

- update touched renderer comments that still imply titled-shell rendering

Exit criteria:

- only `section` increments heading depth
- readable descendant refs resolve wherever this plan ships them
- structure attachments render through the same readable contract as top-level
  documents

Rollback:

- revert as one slice if rendered markdown or descendant lookup remains mixed
  between shell mode and typed mode

## Phase 4 - Shared readable sublanguage rollout across intended bodies

Status: COMPLETED

Goal:
Move readable markdown beyond `document` into the intended readable Doctrine
surfaces without inventing parallel contract or workflow dialects.

Work:

- enable the shared readable block model on the intended non-document bodies:
  `record_body`, `output_record_body`, `workflow_section_body`, and
  `skill_entry_body`
- preserve current surface boundaries and fail-loud restrictions where a body
  remains intentionally out of scope
- preserve the backward-compatible keyed-section and emphasized-line forms the
  spec explicitly keeps legal
- keep `structure:` attached only to markdown-bearing inputs and outputs; do
  not widen it into another shape system while rolling out broader readable
  bodies

Verification (smallest signal):

- focused manifests for output contracts, workflow sections, and skill-entry
  bodies using rich readable blocks
- regression manifests proving old keyed-section authoring still renders and
  resolves legally
- `make verify-examples`

Docs/comments (propagation; only if needed):

- update the live docs that describe readable authoring on I/O, workflow, and
  review-adjacent surfaces

Exit criteria:

- readable markdown is no longer effectively document-only
- no second readable-body dialect has been introduced

Rollback:

- revert widened non-document reuse if it creates inconsistent body rules or a
  shadow readable language

## Phase 5 - Proof, docs, diagnostics, and editor parity cutover

Status: REOPENED (audit found missing code work)

Missing (code):

- fresh `.venv/bin/python -m doctrine.verify_corpus` and
  `.venv/bin/python -m doctrine.diagnostic_smoke` are green from this
  worktree, but `make` in `editors/vscode/` still exits non-zero because
  `npm run test:integration` aborts with `SIGABRT` after four startup attempts
  before alignment validation or VSIX packaging can run

Manual QA (non-blocking):

- run the live-editor smoke ladder from `editors/vscode/README.md` after the
  extension-host suite is green again

Goal:
Make proof, live docs, diagnostics, and the extension describe the same shipped
readable-markdown surface.

Work:

- add the readable-markdown example ladder after `57`, covering:
  - rich document blocks
  - inheritance and overrides
  - guards and descendant addressability
  - readable reuse on non-document surfaces
  - multiline strings and code blocks
  - compile-negative readable failures
- update `examples/README.md`, `docs/README.md`,
  `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/REVIEW_SPEC.md`, `docs/COMPILER_ERRORS.md`, and
  `editors/vscode/README.md`
- update `editors/vscode/resolver.js`,
  `editors/vscode/syntaxes/doctrine.tmLanguage.json`,
  `editors/vscode/language-configuration.json`,
  `editors/vscode/scripts/validate_lark_alignment.py`, and extension tests so
  editor behavior mirrors compiler truth
- clean up non-evergreen readable-markdown plan docs only if they still
  contradict shipped truth after the code and evergreen docs land

Verification (smallest signal):

- `make verify-examples`
- `make verify-diagnostics`
- `cd editors/vscode && make`

Docs/comments (propagation; only if needed):

- this phase owns final live-doc truth sync and editor smoke guidance directly

Exit criteria:

- compiler behavior, example proof, diagnostics, evergreen docs, and editor
  behavior no longer disagree about readable markdown

Rollback:

- revert if any of proof, docs, diagnostics, or editor parity still advertises
  a different readable surface than the compiler ships
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- prefer targeted parser/compiler probes only where manifest coverage is too
  indirect to catch a real readable-markdown contract failure
- keep new checks behavior-level and structure-insensitive where possible

## 8.2 Integration tests (flows)

- manifest-backed example verification is the primary trust signal
- add compile-negative cases for invalid readable block usage, invalid override
  shapes, descendant path failures, and renderer-critical block contracts

## 8.3 E2E / device tests (realistic)

- use the repo-local VS Code integration suite to prove click targets and
  highlighting on the new readable-markdown surfaces
- use a short manual editor smoke pass only at finalization if needed

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- this is a repo-shipped language and tooling cutover, not a production service
  rollout
- merge only when compiler, proof, docs, and editor surfaces are aligned

## 9.2 Telemetry changes

- no runtime telemetry is expected
- observability is verification-first: manifests, diagnostics, and extension
  tests

## 9.3 Operational runbook

- develop against targeted readable-markdown manifests first
- rerun repo-wide verification before calling the wave shipped
- keep the readable-markdown plan doc authoritative until code and truth-sync
  are complete

# 10) Decision Log (append-only)

## 2026-04-11 - Create a dedicated readable-markdown full-implementation plan

### Context

- `docs/READABLE_MARKDOWN_SPEC.md` describes a larger feature wave than the
  currently shipped narrowed subset
- the repo already has umbrella second-wave plans, but no dedicated canonical
  full-arch artifact for readable markdown itself
- the user explicitly requested a full plan for `docs/READABLE_MARKDOWN_SPEC.md`
  and explicitly rejected scope-down

### Options

- keep readable markdown folded only into the umbrella mechanics and
  integration-surface artifacts
- create a dedicated canonical full-arch plan for readable markdown and treat
  the umbrella docs as related context

### Decision

- create this dedicated readable-markdown full-arch plan doc
- treat full intended spec behavior as the requested outcome, not the currently
  shipped narrowed slice

### Consequences

- readable markdown now has one dedicated planning owner path
- later planning passes can sharpen this scope directly instead of rediscovering
  it inside broader second-wave docs
- the user-facing default is explicit: do not scope this wave down

### Follow-ups

- confirm the North Star
- then continue with `research`, `deep-dive`, and `phase-plan` against this
  doc

## 2026-04-11 - North Star confirmed

### Context

- the user explicitly confirmed the readable-markdown full-implementation scope
- the plan must preserve the full intended `READABLE_MARKDOWN_SPEC.md` target
  and must not scope down to the currently shipped narrowed subset

### Options

- keep the doc in `draft` and defer activation
- mark the doc `active` and use it as the canonical readable-markdown planning
  artifact for the next `arch-step` pass

### Decision

- mark this readable-markdown full-arch plan `active`
- keep the current scope and non-negotiables unchanged

### Consequences

- this doc is now the default `DOC_PATH` for later `arch-step` commands in this
  session unless a more specific doc is supplied
- later planning passes should deepen this artifact instead of creating another
  readable-markdown plan

### Follow-ups

- run `research` or `deep-dive` against this doc next

## 2026-04-11 - Fold in `docs/READABLE_MARKDOWN_SPEC.md` as bound plan context

### Context

- the dedicated readable-markdown implementation plan must carry the full spec
  inline so later planning passes cannot miss the intended feature surface
- `arch-step fold in` is advisory and phase-aligned, so it must not rewrite the
  authoritative phased plan in Section 7

### Options

- keep `docs/READABLE_MARKDOWN_SPEC.md` only as an external related document
- fold the full spec into this plan's reference pack with distilled
  obligations, instruction-bearing structure, phase alignment guidance, and
  verbatim source

### Decision

- bind `docs/READABLE_MARKDOWN_SPEC.md` into this plan through the
  `arch_skill:block:reference_pack`
- keep Section 7 unchanged and treat the folded source as advisory context for
  later core planning passes

### Consequences

- the implementation spec now contains the full readable-markdown source of
  truth inline
- later `research`, `deep-dive`, and `phase-plan` passes can work from one
  canonical artifact without re-resolving the spec
- the folded source remains supplemental context and does not silently replace
  the plan's explicit operational structure

### Follow-ups

- continue with `arch-step research` or `arch-step deep-dive` against this doc
- adopt phase-specific obligations into Section 7 only through a later core
  planning pass

## 2026-04-11 - Auto-plan grounded the readable-markdown artifact

### Context

- the user invoked `arch-step auto-plan` against this approved readable-markdown
  plan
- the installed Codex stop hook and controller state were available, so the
  planning arc could be run as one bounded controller pass
- repo evidence was already strong enough to ground research and architecture
  without adding external research in this run

### Options

- leave the plan in its earlier bootstrap state and stop after preflight
- complete the bounded planning arc by grounding Section 3, hardening Sections
  4 through 6, and tightening Section 7 into the authoritative execution plan

### Decision

- complete the auto-plan arc through `research`, `deep-dive`, `deep-dive`, and
  `phase-plan`
- keep `external_research_grounding` unrun for now because repo evidence
  already settles the owner paths and the remaining open questions are
  implementation-shaped, not prior-art-shaped

### Consequences

- the plan now has marker-owned research, current-architecture,
  target-architecture, call-site-audit, and phase-plan blocks
- `deep_dive_pass_1` and `deep_dive_pass_2` are both marked done on
  `2026-04-11`
- the artifact is ready for `implement-loop` without needing another planning
  doc

### Follow-ups

- clear `.codex/auto-plan-state.json` at controller stop
- start implementation from Section 7, then audit against this same artifact

## 2026-04-11 - Cut an isolated implementation worktree

### Context

- the current repo worktree is intentionally dirty outside this plan scope
- implementation for readable markdown should happen away from the current
  checkout so this directory does not absorb the implementation churn
- the user asked for a separate implementation worktree branched from the
  current repo position

### Options

- implement in the current dirty worktree
- create a sibling worktree on a fresh branch from the current `HEAD` commit
  and carry this plan artifact into it explicitly

### Decision

- create the sibling worktree at
  `/Users/aelaguiz/workspace/doctrine-readable-markdown-implementation`
- use branch `codex/readable-markdown-implementation-20260411`
- branch it from source branch
  `codex/integration-surfaces-recovery-20260411` at commit `d70a274`
- carry this plan doc into that worktree explicitly because the artifact is
  local planning state rather than already committed history

### Consequences

- readable-markdown implementation can proceed in the new worktree without
  adding more churn to the current checkout
- the sibling worktree starts from the current committed repo state, not from
  unrelated local uncommitted changes in this checkout
- this plan doc must stay synchronized deliberately if planning changes continue
  in the source checkout while implementation moves in the new worktree

### Follow-ups

- use `/Users/aelaguiz/workspace/doctrine-readable-markdown-implementation` for
  implementation work
- if additional current-checkout local changes are intentionally needed there,
  port them explicitly instead of assuming the worktree inherited dirty state
