---
title: "Doctrine - Integration Surfaces Full Implementation - Architecture Plan"
date: 2026-04-11
status: complete
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: architectural_change
related:
  - docs/INTEGRATION_SURFACES_SPEC.md
  - docs/ANALYSIS_AND_SCHEMA_SPEC.md
  - docs/READABLE_MARKDOWN_SPEC.md
  - docs/LANGUAGE_MECHANICS_SPEC.md
  - docs/archive/second_wave/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/REVIEW_SPEC.md
  - docs/WORKFLOW_LAW.md
  - docs/README.md
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

Doctrine ships `docs/INTEGRATION_SURFACES_SPEC.md` end to end as one coherent
language-and-tooling wave: the intended new semantic surfaces integrate cleanly
with existing workflow law, review, outputs, `trust_surface`, examples,
evergreen docs, verification, and VS Code extension behavior.

## Problem

The repo currently has split truth around the second-wave surfaces. The spec
defines how `analysis`, `schema`, readable `document` structures, output
attachments, review/schema coupling, and currentness/trust interactions should
fit Doctrine, but the shipped compiler/editor/docs path is still partial and in
places contradictory. That leaves proposal text ahead of runtime truth and
keeps the intended integration seams unverified.

## Approach

Implement the spec through Doctrine's existing owners only: keep routes,
currentness, preservation, invalidation, and route-only behavior on workflow
law; keep critic semantics, carried state, and review current truth on review;
keep durable carriers on outputs; add the intended typed attachment and
readable-output machinery without inventing parallel declaration families; then
update the corpus, evergreen docs, diagnostics, and VS Code extension in the
same cutover.

## Plan

1. Ground the plan against shipped workflow law, review, I/O, examples, and
   the current partial second-wave implementation state.
2. Close the core compiler seams the integration spec depends on:
   readable-output/document support, typed `schema:` / `structure:` attachments,
   `analysis` / `schema` end-to-end rendering, and workflow-or-schema review
   contracts.
3. Add the full example ladder and negative proof the integrated surfaces
   require, keeping the pre-54 corpus green unless an intentional bug fix says
   otherwise.
4. Update evergreen docs so the shipped path describes the real integration
   rules and clearly records which explored surfaces remain deferred.
5. Bring `editors/vscode/` to full parity with the shipped language and verify
   the full repo with the project-owned commands.

## Historical Note

This umbrella plan is retained as implementation history for the broader
integration wave. Do not read its baseline problem statements as current repo
reality for readable markdown or typed `structure:` attachments.

Readable markdown, typed `structure:` attachments, their example proof, and
editor/docs convergence now ship through
`docs/archive/second_wave/DOCTRINE_READABLE_MARKDOWN_FULL_IMPLEMENTATION_2026-04-11.md` and the
evergreen docs it updated.

## Non-negotiables

- No narrowing below the intended `INTEGRATION_SURFACES_SPEC.md` end state.
- No separate `review_family` or `route_only` declaration kinds.
- No silent promotion of explored `grounding` or user-authored
  `render_profile` into shipped core language when the spec explicitly leaves
  them later-wave or deferred.
- No second trust channel, shadow carrier model, or duplicate currentness
  semantics.
- No split-brain truth between compiler, examples, evergreen docs, and VS Code
  extension.
- No partial ship where grammar parses a surface that the compiler, examples,
  and editor cannot support honestly.

<!-- arch_skill:block:implementation_audit:start -->
# Historical Audit Snapshot (superseded)
Date: 2026-04-11

This umbrella doc is retained as historical planning context. Its old audit
snapshot is not the current authority for readable-markdown completion or
editor parity.

Current authoritative audit state for readable markdown lives in
`docs/archive/second_wave/DOCTRINE_READABLE_MARKDOWN_FULL_IMPLEMENTATION_2026-04-11.md`. Do not
treat prior pass/fail notes here as current repo truth.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-11
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-11
recommended_flow: implement-loop
note: Research, deep-dive pass 1, deep-dive pass 2, and phase-plan are complete for this artifact. External research remains not started because repo evidence was sufficient for this pass.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly, Doctrine will ship the full intended
integration behavior described by `docs/INTEGRATION_SURFACES_SPEC.md` instead
of keeping it as proposal-only design text:

- `analysis`, `schema`, and readable `document` surfaces will integrate with
  existing workflow, review, output, and addressability semantics through one
  compiler path
- typed `schema:` and `structure:` attachments will be real language features,
  not generic prose buckets pretending to be typed contracts
- review contracts will resolve through the intended workflow-or-schema model
  without inventing a second review control plane
- route-only behavior, currentness, preservation, invalidation, and trust will
  stay on existing workflow-law/review/output surfaces rather than being
  reintroduced as parallel primitives
- evergreen docs, examples, diagnostics, and `editors/vscode/` will all match
  the shipped language truth

The claim is false if any of those seams remain proposal-only, if the
implementation narrows below the spec's intended state, if explored-but-rejected
surfaces are shipped as core language anyway, or if compiler/docs/editor truth
drifts after the cutover.

## 0.2 In scope

- Full implementation of the intended integration behavior for the new language
  surfaces referenced by `docs/INTEGRATION_SURFACES_SPEC.md`, including:
  - `analysis`
  - `schema`
  - readable `document` support where the integration story depends on it
  - typed `schema:` output attachment
  - typed `structure:` attachment on markdown-bearing inputs and outputs
  - workflow-or-schema review contracts
  - review/output agreement and `trust_surface` behavior for schema-backed and
    readable-output flows
- Compiler, renderer, diagnostics, corpus, and extension convergence needed to
  keep one owner path for those seams.
- Full example and negative-proof coverage needed to make the integration story
  manifest-backed and fail-loud.
- Evergreen docs updates across the live docs path so shipped documentation
  matches actual compiler/editor truth.
- VS Code extension updates across syntax highlighting, navigation, resolver
  logic, alignment checks, README truth, packaging, and tests.
- Architectural convergence required to prevent split truth between the current
  active mechanics-wave plan, the integration spec, and shipped code.

## 0.3 Out of scope

- Narrowing the work to only the smallest subset that is easiest to land while
  leaving the rest of the intended integration story proposal-only.
- Shipping separate `review_family` or `route_only` declaration kinds when the
  spec explicitly says to keep those seams on existing review/workflow-law
  surfaces.
- Shipping first-class `grounding` or user-authored `render_profile` as part of
  this implementation wave. Full implementation of the spec means making those
  defer decisions explicit and truthful, not silently converting them into core
  language.
- New editor-product features such as hover, rename, completion, or language
  server work unrelated to parity with shipped Doctrine semantics.
- Runtime shims, fallback renderers, or compatibility layers that keep old and
  new integration semantics alive in parallel.

## 0.4 Definition of done (acceptance evidence)

- `doctrine/grammars/doctrine.lark`, `doctrine/model.py`,
  `doctrine/parser.py`, `doctrine/compiler.py`, and `doctrine/renderer.py`
  support the full intended integration story from the spec, not only parse
  scaffolding or partial indexing.
- The post-53 example ladder and its negative cases prove the integrated
  surfaces through `doctrine.verify_corpus`.
- `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/REVIEW_SPEC.md`, `docs/WORKFLOW_LAW.md`, `docs/README.md`,
  `docs/COMPILER_ERRORS.md`, and `examples/README.md` describe the same shipped
  behavior as the compiler.
- The repo has an explicit, truthful disposition for enhancement-spec docs so
  they do not compete with evergreen docs after ship.
- `editors/vscode/` fully recognizes and navigates the shipped language
  surfaces and `cd editors/vscode && make` passes.
- Relevant repo checks pass, including:
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics change
  - targeted manifest-backed corpus runs while developing new examples
  - `cd editors/vscode && make`

Behavior-preservation evidence:

- the shipped corpus through example `53_review_bound_carrier_roots` remains
  green unless an intentional bug fix is explicitly justified
- current workflow-law, review, currentness, `trust_surface`, and route-only
  semantics keep their existing owners
- no editor regression is introduced on already shipped declarations or
  navigation surfaces

## 0.5 Key invariants (fix immediately if violated)

- One owner per seam.
- One live route per seam.
- Workflow law keeps owning routes, currentness, preservation, and invalidation.
- Review keeps owning critic semantics, verdict coupling, carried state, and
  review current truth.
- Outputs keep owning durable carriers and `trust_surface`.
- No second trust channel, no shadow carrier model, and no hidden packet
  primitive.
- No split-brain truth between shipped code, examples, evergreen docs, and
  `editors/vscode/`.
- Full implementation means honoring the spec's intended boundaries, including
  its explicit rejections and deferrals.
- No fallbacks or runtime shims.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Ship the integration story the spec actually intends, not a narrower
   convenience subset.
2. Preserve existing Doctrine seam ownership while adding the new typed
   surfaces.
3. Keep one compiler/render/addressability path and one editor parity path.
4. Keep docs, examples, diagnostics, and extension truth synchronized with the
   shipped implementation.
5. Avoid letting the broader mechanics-wave artifacts and this integration
   artifact drift into competing sources of truth.

## 1.2 Constraints

- The current repo already ships workflow law, review, currentness, and
  `trust_surface`, so the implementation must extend those surfaces rather than
  replace them.
- The grammar/model/parser already know about some second-wave declarations,
  but end-to-end compiler behavior is still partial.
- The current output/review integration path is still workflow-contract-first
  and does not yet fully own typed attachment or schema-backed review behavior.
- The current evergreen docs path still labels enhancement specs as design
  references rather than shipped truth.
- The VS Code extension mirrors compiler truth manually, so language widening
  requires explicit resolver and syntax follow-through.

## 1.3 Architectural principles (rules we will enforce)

- Reuse existing Doctrine seam owners before inventing a new language family.
- Fail loud on unsupported or contradictory usage; do not preserve half-shipped
  permissive behavior.
- Extend the existing addressability and inheritance model instead of creating
  special merge rules.
- Treat docs, examples, diagnostics, and editor parity as part of shipping the
  feature, not as optional cleanup.
- When the spec defers or rejects a surface, encode that truth clearly instead
  of silently omitting it and calling the work complete.

## 1.4 Known tradeoffs (explicit)

- Full intended implementation is broader than the narrowest first-wave subset,
  so the plan will touch compiler, renderer, examples, docs, and editor code in
  one coordinated wave.
- Honoring the spec's explicit deferrals means some explored surfaces will be
  documented as not shipped even while the rest of the integration wave lands.
- Keeping one planning source of truth may require later research to merge,
  supersede, or retire overlapping mechanics-wave planning material.

# 2) Problem Statement (existing architecture + why change)

## 2.1 Historical baseline when this umbrella plan was opened

- Doctrine ships strong workflow-law, review, output, and `trust_surface`
  semantics with manifest-backed examples through `53_review_bound_carrier_roots`.
- The repo already contains `docs/INTEGRATION_SURFACES_SPEC.md` and related
  second-wave spec docs that describe the intended integration model.
- The parser/AST layer already includes top-level `analysis`, `schema`, and
  `document` declarations, and the compiler indexes them, but the emitted
  runtime and integration surfaces remain incomplete.
- The repo also contains a broader active mechanics-wave architecture plan that
  overlaps this problem space but is not scoped specifically to
  `INTEGRATION_SURFACES_SPEC.md`.

## 2.2 What’s broken / missing (concrete)

- At plan open, the intended typed output and readable-output integration seams
  were not yet shipped end to end.
- At plan open, review contracts remained workflow-only even though the
  integration spec intended schema-backed review coupling.
- At plan open, some second-wave declarations existed in parser/indexing form
  without the richer companion-spec shapes or full
  readable/rendered/addressable support.
- At plan open, examples and evergreen docs did not yet provide one shipped,
  fully integrated story for these surfaces.
- At plan open, VS Code parity for the intended integrated surfaces was
  incomplete.

## 2.3 Constraints implied by the problem

- We cannot solve this honestly by shipping parser-only or docs-only slices.
- We cannot let integration behavior move onto new parallel declarations when
  the spec explicitly assigns ownership to existing workflow-law/review/output
  seams.
- We need to preserve the existing shipped corpus and behavior while widening
  the language.
- We need to resolve overlap with existing mechanics-wave planning material
  without leaving competing architecture truth behind.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- No additional external prior-art system is adopted for this pass. Reject
  letting generic DSL, schema, or editor-language analogies outrank the repo's
  own split-spec set plus shipped code, because this work is about converging
  Doctrine's intended second-wave surfaces onto Doctrine's existing owners
  rather than cargo-culting another system.

## 3.2 Historical internal baseline at plan open (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/grammars/doctrine.lark` - at plan open, it declared top-level
    `analysis`, `schema`, and `document`, but agent reserved fields remained
    `role`, `inputs`, `outputs`, `skills`, and `review`; `output_body` still
    only knew generic record items plus `trust_surface`; review `contract:` was
    still a `workflow_ref`.
  - `doctrine/parser.py` - at plan open, it parsed the second-wave
    declarations into placeholder bodies and only split `trust_surface` out of
    `output`; there was no typed `analysis:` agent field or typed `schema:` /
    `structure:` attachment parse path yet.
  - `doctrine/model.py` - at plan open, it stored `AnalysisDecl`,
    `SchemaDecl`, and `DocumentDecl`, but those bodies were still generic
    keyed-item containers; `InputDecl` and `OutputDecl` did not yet have
    dedicated attachment slots.
  - `doctrine/compiler.py` - at plan open, it indexed second-wave declarations through
    `_READABLE_DECL_REGISTRIES` and `_ADDRESSABLE_ROOT_REGISTRIES`, compiles the
    shipped I/O and review surfaces, but `_compile_output_decl()` still treats
    second-wave attachment candidates as generic extras, `_resolve_review_contract_spec()`
    is workflow-only, and `_display_addressable_target_value()` /
    `_get_addressable_children()` still miss analysis/schema/document support.
  - `doctrine/renderer.py` - already owns one compiled readable-block markdown
    renderer and should be reused rather than replaced; the missing work is in
    compiler wiring, not a second renderer.
  - `doctrine/verify_corpus.py` plus manifest-backed examples under `examples/`
    - own behavioral proof for the shipped language through example `53`.
  - `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`,
    `docs/AGENT_IO_DESIGN_NOTES.md`, and `docs/REVIEW_SPEC.md` - describe the
    current shipped output and review model, including the existing `json schema`
    attachment on `output shape`.
  - `editors/vscode/resolver.js`,
    `editors/vscode/syntaxes/doctrine.tmLanguage.json`, and
    `editors/vscode/scripts/validate_lark_alignment.py` - are the manual
    editor-parity path and currently encode only part of the intended second-wave
    behavior.
- Canonical path / owner to reuse:
  - `doctrine/` - the only owner for language semantics, addressability,
    compile behavior, rendering, and diagnostics.
  - `examples/` - the only proof surface for shipped language behavior.
  - `docs/README.md` plus evergreen docs under `docs/` - the only live docs
    path for shipped truth.
  - `editors/vscode/` - the only editor-parity surface for repo-local prompt
    authoring.
- Existing patterns to reuse:
  - `_READABLE_DECL_REGISTRIES` / `_ADDRESSABLE_ROOT_REGISTRIES` in
    `doctrine/compiler.py` - the registration pattern for new readable and
    addressable roots.
  - Reserved typed agent fields and explicit typed contract keys in
    `doctrine/grammars/doctrine.lark` - the right pattern for adding `analysis`
    and typed attachments without making generic record keys magical.
  - Existing review agreement and `trust_surface` validation in
    `doctrine/compiler.py` - the right place to extend review/schema coupling
    without inventing a second trust channel.
  - Existing compiled readable-block classes in `doctrine/compiler.py` plus
    `doctrine/renderer.py` - the right render path for `document` and richer
    contract output.
- Prompt surfaces / agent contract to reuse:
  - `docs/AGENT_IO_DESIGN_NOTES.md` - keeps outputs as the carrier and trust
    owner even when new attachments arrive.
  - `docs/REVIEW_SPEC.md` and examples `43` through `53` - keep review
    semantics, contract facts, current truth, and carried state on the existing
    review/output seam.
  - `examples/09_outputs/prompts/AGENTS.prompt` - already demonstrates where
    future-looking `schema:` and `structure:` authoring pressures exist, but
    today those lines are still generic record keys rather than typed
    attachment surfaces.
- Existing grounding / tool / file exposure:
  - `make verify-examples`
  - `make verify-diagnostics`
  - targeted `uv run --locked python -m doctrine.verify_corpus --manifest ...`
  - `cd editors/vscode && make`
  - gbrain repo-memory note `concepts/doctrine-second-wave-compiler-gap-2026-04-11`
- Duplicate or drifting paths relevant to this change:
  - `docs/archive/second_wave/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md` -
    overlaps heavily and now contains stale claims about current repo state, so
    docs convergence must decide whether to fold, supersede, or retire its
    overlapping slice.
  - `docs/README.md` - still correctly labels the split spec set as not shipped
    truth, which becomes stale once this work lands.
  - `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, and
    `examples/09_outputs/prompts/AGENTS.prompt` - already teach
    `output shape.schema` as a `json schema` attachment, so introducing
    `output.schema` as a Doctrine `schema` attachment requires explicit
    context-sensitive resolution rather than a global `schema` rewrite.
  - `editors/vscode/resolver.js` - at plan open, it globally mapped keyed
    `schema:` refs to `json schema`, which would drift immediately unless
    owner-aware resolution replaced it.
- Capability-first opportunities before new tooling:
  - Extend the existing readable-declaration lookup and addressable-node graph
    instead of adding a second ref resolver.
  - Reuse the existing compiled readable-block renderer instead of building a
    second markdown engine for documents or schema output.
  - Reuse workflow law, review, outputs, and `trust_surface` as the existing
    seam owners instead of adding `review_family`, `route_only`, or a new
    packet primitive.
- Behavior-preservation signals already available:
  - `make verify-examples`
  - targeted manifest-backed runs for any new post-53 example
  - `make verify-diagnostics` when error behavior changes
  - `cd editors/vscode && make`

## 3.3 Open questions (evidence-based)

- Should the overlapping mechanics-wave architecture plan be folded into this
  artifact or demoted after ship? - Settle it in the docs-convergence phase by
  comparing which claims remain uniquely valuable versus which now duplicate or
  contradict this artifact.
- How much of the current placeholder AST for `analysis`, `schema`, and
  `document` can be transformed in place versus replaced outright? - Settle it
  during implementation by auditing parser/model/compiler touchpoints and
  choosing the smaller behavior-preserving rewrite.
- Should `examples/09_outputs` stay a current-language example only, with all
  typed `schema:` / `structure:` proof moved to the post-53 ladder? - Settle it
  in the corpus phase based on whether preserving backwards intent there would
  leave a misleading half-shipped story.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/grammars/doctrine.lark` already declares top-level `analysis`,
  `schema`, and `document`, but the agent surface still only reserves
  `role`, `inputs`, `outputs`, `skills`, and `review`, and typed output/input
  attachments are not first-class grammar nodes yet.
- `doctrine/model.py` stores second-wave declarations as generic keyed bodies:
  `AnalysisBody` is preamble plus titled sections, `SchemaBody` is preamble plus
  section/gate items, and `DocumentBody` is preamble plus flat block entries.
  `InputDecl` and `OutputDecl` still model everything non-core as generic record
  items.
- `doctrine/parser.py` mirrors that placeholder structure. It can parse
  top-level declarations and document block kinds, but not the richer
  companion-spec attachment and body semantics.
- `doctrine/compiler.py` owns indexing, compile, addressability, flow emission,
  and review semantics for the shipped language.
- `doctrine/renderer.py` already renders a richer compiled readable-block IR,
  but current authored surfaces reach it only partially because compiler wiring
  still treats second-wave structures as generic sections or unresolved roots.
- `examples/` remains the numbered proof ladder through
  `53_review_bound_carrier_roots`; no manifest-backed post-53 second-wave ladder
  exists yet.
- `docs/README.md` cleanly separates evergreen shipped docs from enhancement
  specs, and the enhancement-spec section still says the new wave is not shipped
  truth.
- `editors/vscode/` mirrors grammar and navigation manually through regex-based
  scanning, TextMate grammar rules, snapshot fixtures, and integration tests.

## 4.2 Control paths (runtime)

- Parse path: `parse_file()` drives Lark -> parser transforms -> prompt-file AST
  with top-level second-wave declarations, but those declarations still use the
  current placeholder shapes.
- Compile/index path: `Compiler._index_unit()` registers `analysis`, `schema`,
  and `document` in readable and addressable registries, then agent compilation
  walks only the shipped typed fields. There is no reserved `analysis:` field,
  so concrete agents cannot yet attach an `analysis` declaration through a
  compiler-owned path.
- Output path: `_compile_output_decl()` splits `target`, `shape`,
  `requirement`, `files`, and generic extras. Any future-looking `schema:` or
  `structure:` line in an `output` body currently lands in the generic-extra
  bucket and renders as fallback record content rather than as a typed
  attachment.
- Input path: `_compile_input_decl()` only knows `source`, `shape`, and
  `requirement`; there is no typed `structure:` support on markdown-bearing
  inputs.
- Existing `schema:` behavior is context-specific in author intent but not yet
  in compiler/editor implementation: shipped docs and `examples/09_outputs`
  teach `output shape.schema` as a `json schema` ref, while the integration spec
  wants `output.schema` to mean a Doctrine `schema` declaration.
- Review path: `_resolve_review_contract_spec()` only accepts workflow refs,
  collects first-level workflow section keys as contract gates, and feeds those
  into review semantic evaluation and guarded output interpolation.
- Addressability path: `_resolve_readable_decl()` and
  `_resolve_addressable_root_decl()` can find analysis/schema/document roots by
  registry, but display and child traversal are incomplete, so some second-wave
  refs still fall into internal compiler errors or dead-end addressability.
- Render path: `doctrine/renderer.py` can emit `CompiledSection`,
  `CompiledSequenceBlock`, `CompiledBulletsBlock`, `CompiledChecklistBlock`,
  `CompiledDefinitionsBlock`, `CompiledTableBlock`, `CompiledCalloutBlock`,
  `CompiledCodeBlock`, and `CompiledRuleBlock`, but the compiler does not yet
  route top-level `document`, attached `structure:`, or attached `schema:` /
  `analysis:` through that fuller surface.
- Verification path: `doctrine.verify_corpus` owns manifest-backed proof;
  editor parity is separately validated by `npm test`,
  `scripts/validate_lark_alignment.py`, and packaged VSIX checks under
  `editors/vscode/`.

## 4.3 Object model + key abstractions

- `AnalysisDecl`, `SchemaDecl`, and `DocumentDecl` are already first-class
  declaration families in the AST and compiler registries, but they are not yet
  first-class integration surfaces in concrete agent, input/output, review, or
  addressability behavior.
- `OutputDecl` is still `items + trust_surface`; typed attachments do not have
  a dedicated slot, so ownership of inventory versus readable structure is still
  implicit in authored record keys.
- `InputDecl` is still `items` only, so markdown-bearing input structure is
  authored by prose convention instead of a typed contract.
- `ReviewContractSpec` is workflow-specific, with
  `workflow_unit`, `workflow_decl`, `workflow_body`, and workflow-derived gates.
  That bakes workflow-only review contracts into downstream review agreement,
  interpolation, and diagnostics.
- `AddressableNode` and `_get_addressable_children()` already model
  input/output/workflow/review-semantic/addressable record surfaces, but not the
  descendant structure of `analysis`, `schema`, or `document`.
- The VS Code resolver duplicates declaration-kind and keyed-ref knowledge in
  regex tables and body scanners. It recognizes top-level analysis/schema/document
  declarations, but keyed refs still map `schema:` globally to `json schema`,
  and review contract navigation is still hard-coded to workflow targets.

## 4.4 Observability + failure behavior today

- The shipped language fails loudly for the current surfaces: missing typed
  source/shape/requirement, illegal output shape/target combinations, wrong
  review contract workflows with law, duplicate review gates, wrong registry
  refs, and trust-surface violations.
- The second-wave partial state still has an internal-error gap: referencing an
  `analysis` declaration through a readable/addressable path can currently fail
  with `Internal compiler error: unsupported addressable target AnalysisDecl`
  instead of a user-facing supported-surface diagnostic.
- `docs/README.md` truthfully reports that the enhancement specs are not shipped
  yet, which avoids overclaiming but also confirms the current split between
  proposal text and runtime truth.
- Extension validation is real but partial: grammar keywords are aligned, top-level
  declarations colorize, and integration tests prove clicks for shipped surfaces
  plus `json schema`, but there is no end-to-end proof yet for `analysis:`,
  `output.schema`, `input/output.structure`, document descendants, or
  schema-backed review contracts.

## 4.5 UI surfaces (ASCII mockups, if UI work)

- The only user-facing UI surface in scope is prompt authoring inside VS Code or
  Cursor.
- No ASCII mockup is needed; the real editor surfaces are syntax highlighting,
  Ctrl/Cmd-click, Go to Definition, and README smoke-check instructions.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- `doctrine/grammars/doctrine.lark` will ship the full intended integration
  surface for this wave:
  - top-level `analysis`
  - top-level `schema`
  - top-level `document`
  - reserved agent `analysis:`
  - typed `schema:` on `output`
  - typed `structure:` on markdown-bearing `input` and `output`
  - workflow-or-schema `contract:` resolution for `review`
- `doctrine/model.py` and `doctrine/parser.py` will represent those surfaces as
  typed AST nodes and typed attachment slots rather than generic record scalars
  that only look typed in authored prose.
- `doctrine/compiler.py` plus `doctrine/renderer.py` will stay the one compile
  and one render owner path. The current compiled readable-block IR will be
  extended and reused rather than replaced with a second markdown engine.
- `examples/` will grow a manifest-backed post-53 ladder that proves the new
  integrated surfaces and their negative cases.
- `docs/` will converge onto one evergreen story after ship. The enhancement
  specs may remain as historical design references, but they must no longer
  compete with evergreen docs about what is shipped.
- `editors/vscode/` will stay a repo-local manual extension, but it will match
  the shipped language exactly instead of carrying second-wave partial truth.

## 5.2 Control paths (future)

- Parse path: prompts compile into typed second-wave AST nodes, including
  explicit agent `analysis:` attachments and explicit I/O attachment slots for
  `schema:` and `structure:`.
- Agent path: a concrete agent may attach `analysis:` exactly through the
  reserved field, and the compiler renders that analysis program into natural,
  readable Markdown without moving routing, review, or trust semantics out of
  their current owners.
- Output path:
  - `output.schema` resolves only to a Doctrine `schema` declaration and emits
    the attached schema inventory or gate summary through a compiler-owned path.
  - `output.shape.schema` continues to resolve to `json schema` beneath the
    output-shape surface.
  - `output.structure` resolves only to a `document` declaration and emits the
    readable document-shape summary for markdown-bearing outputs.
  - conflicting ownership, such as `output.schema` plus a local `must_include`
    inventory on the same seam, fails loudly.
- Input path:
  - `input.structure` resolves only to a `document` declaration and emits the
    readable document-shape summary for markdown-bearing inputs.
  - non-markdown-bearing shapes reject `structure:` loudly.
- Review path:
  - `review contract:` resolves through one tagged contract abstraction that
    supports either a workflow contract or a schema contract.
  - `contract.<gate>`, `contract.passes`, `contract.failed_gates`, guarded
    review output sections, and review agreement all work uniformly across both
    contract kinds.
  - review still owns critic semantics, verdict coupling, carried state, and
    current truth; outputs still own carriers and `trust_surface`.
- Addressability path:
  - `analysis`, `schema`, and `document` become first-class readable and
    addressable roots.
  - descendants such as analysis stages/sections, schema sections/gates, and
    document blocks plus supported substructure resolve through the same
    addressable-node graph rather than through special-case interpolation logic.
- Render path:
  - the existing compiled readable-block IR remains the one markdown emission
    path.
  - `document` blocks map to semantic block kinds such as `sequence`,
    `bullets`, `checklist`, `definitions`, `table`, `callout`, `code`, and
    `rule` instead of collapsing into heading depth alone.
  - `analysis` and `schema` render through the same readable-block model so
    emitted `AGENTS.md` stays natural.
- Verification path:
  - the new example ladder proves the language end to end.
  - the VS Code extension proves syntax and navigation parity for the same
    surfaces.

## 5.3 Object model + abstractions (future)

- `analysis` becomes a typed, inheritable, patchable reasoning-program
  declaration that concrete agents can attach through `analysis:`.
- `schema` becomes the typed artifact-inventory and later gate-catalog
  declaration. It is not a second review family and not a replacement for
  outputs.
- `document` becomes the first-class readable markdown schema declaration with
  addressable descendants and compiler-owned render semantics.
- Input and output declarations gain explicit attachment slots so `schema:` and
  `structure:` are descriptive typed contracts rather than generic authored
  keys.
- Review contracts become a kind-aware abstraction instead of a workflow-only
  abstraction, but the rest of review semantics stay on the current review
  machinery.
- Context-sensitive `schema:` resolution becomes explicit law:
  - on `output shape`, `schema:` means `json schema`
  - on `output`, `schema:` means Doctrine `schema`
  This distinction must be encoded in compiler and extension resolution rather
  than inferred from prose.

## 5.4 Invariants and boundaries

- Workflow law still owns routes, currentness, preservation, invalidation, and
  route-only turn behavior.
- Review still owns critic semantics, verdict coupling, carried state, and
  review current truth.
- Outputs still own durable carriers and `trust_surface`.
- `analysis` owns reusable reasoning choreography, not operational routing or
  validation.
- `schema` owns artifact inventories and schema-backed review gates, not
  workflow law.
- `document` owns readable structure, not output currentness or review
  semantics.
- `output.schema` and local inventory prose such as `must_include` may not own
  the same seam at the same time.
- `schema` and `structure` may only coexist when they describe genuinely
  different seams - inventory versus readable document shape - and the compiler
  can render both honestly.
- One compiler path, one renderer path, one corpus proof path, one evergreen
  docs path, and one VS Code parity path.

## 5.5 UI surfaces (ASCII mockups, if UI work)

- VS Code highlighting and navigation must recognize:
  - agent `analysis:`
  - `output.schema`
  - `input.structure`
  - `output.structure`
  - schema-backed review contracts
  - top-level `document`, `analysis`, and `schema` descendants
- No new hover, rename, completion, or language-server product work is in
  scope.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Syntax | `doctrine/grammars/doctrine.lark` | top-level decls, `agent_field`, `output_body`, `contract_stmt` | Top-level second-wave decls exist, but agent `analysis:` and typed attachments do not; review contracts are workflow-only refs | Add the full intended grammar for typed `analysis`, typed `schema:` / `structure:` attachments, and workflow-or-schema review contracts | Grammar must express the intended surfaces directly instead of hiding them in generic record keys | Context-aware typed fields and attachment productions | New parser negatives, new post-53 examples, VS Code alignment |
| AST | `doctrine/model.py` | `AnalysisBody`, `SchemaBody`, `DocumentBody`, `InputDecl`, `OutputDecl`, review contract types | Placeholder keyed-item bodies; I/O attachments are implicit generic items | Replace placeholder shapes with typed bodies and explicit attachment slots; add a kind-aware review-contract model | Compiler and editor need structural ownership, not prose-shaped data | Typed analysis/schema/document nodes plus typed input/output attachment slots | Parser/compiler unit coverage and example manifests |
| Parser | `doctrine/parser.py` | second-wave declaration transforms and `output_body()` | Parses placeholder bodies and only splits `trust_surface` specially | Parse typed attachments and richer body structure; enforce once-only and owner-conflict rules | Fail-loud semantics belong in parse/transform, not ad hoc compiler fallbacks | Typed parse path for `analysis`, `schema`, `document`, `schema:`, and `structure:` | Negative examples, parser probes, full corpus |
| Agent compile | `doctrine/compiler.py` | `_RESERVED_AGENT_FIELD_KEYS`, agent field compile path | No reserved `analysis:` field | Add reserved agent `analysis:` and compile it through one readable path | Concrete agents need a compiler-owned analysis surface | Agent-level typed `analysis` attachment | Analysis examples, addressability examples |
| Input compile | `doctrine/compiler.py` | `_compile_input_decl()` and input field validation | Inputs only know `source`, `shape`, and `requirement` | Add typed `structure:` support for markdown-bearing inputs and fail-loud validation for unsupported shapes | Input-side readable structure is part of the intended integration story | `input.structure -> document` | Document/input examples and negatives |
| Output compile | `doctrine/compiler.py` | `_compile_output_decl()` and flow/detail helpers | `output` treats second-wave keys as generic extras; flow detail lines ignore attachments | Compile `output.schema` and `output.structure`, render them naturally, and enforce no dual inventory owner | Output-side integration is the center of the spec | `output.schema -> schema`, `output.structure -> document` | Schema/structure examples, flow snapshots, full corpus |
| Existing JSON-shape seam | `doctrine/compiler.py`, `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md` | `output shape.schema` | `schema:` already means `json schema` beneath `output shape` | Preserve `output shape.schema` for `json schema` while adding owner-aware `output.schema` for Doctrine `schema` | The new surface cannot silently break the shipped JSON-shape model | Context-sensitive `schema:` dispatch by owning surface | Example 09, docs, VS Code resolver/integration tests |
| Review contracts | `doctrine/compiler.py` | `_resolve_review_contract_spec()`, `_collect_review_contract_gates()`, review expr resolution | Review contracts resolve only to workflows and workflow-section gates | Introduce a tagged workflow-or-schema contract abstraction and unify gate facts across both kinds | Full intended integration requires schema-backed review without a second review control plane | Kind-aware review contract model | New schema-backed review examples, review negatives, diagnostics |
| Addressability | `doctrine/compiler.py` | `_resolve_readable_decl()`, `_resolve_addressable_root_decl()`, `_get_addressable_children()`, `_display_addressable_target_value()` | Analysis/schema/document are indexed but still incomplete as readable/addressable roots | Add readable display and descendant traversal for analysis/schema/document and supported substructure | Second-wave declarations must behave like Doctrine, not hidden parser-only nodes | Full root + descendant addressability | Interpolation/addressability examples and negatives |
| Render IR reuse | `doctrine/compiler.py`, `doctrine/renderer.py` | compiled readable-block path | Block IR exists, but second-wave surfaces do not flow through it end to end | Reuse the existing readable-block IR for document/schema/analysis output instead of adding a second renderer | One renderer path is an invariant | One compiled readable-block pipeline | New output snapshots and doc examples |
| Diagnostics | `doctrine/compiler.py`, `docs/COMPILER_ERRORS.md` | internal error fallthroughs and undocumented second-wave failures | Some second-wave gaps still fail as internal compiler errors or undocumented compile errors | Replace internal fallthroughs with stable user-facing diagnostics and document them | Fail-loud is required for shipping the surface honestly | Stable second-wave error catalog | `make verify-diagnostics` and negative corpus cases |
| Corpus | `examples/README.md`, new `examples/54_*` onward, manifests and refs | Shipped proof ends at 53; no post-53 second-wave ladder | Add the full manifest-backed ladder and negative cases for analysis/schema/document/integration surfaces | The feature is not shipped until proof exists | Post-53 numbered proof ladder | Targeted manifest runs and `make verify-examples` |
| Existing example convergence | `examples/09_outputs/prompts/AGENTS.prompt` and associated refs/cases | Uses future-looking `schema:` and `structure:` lines as generic record keys | Make example 09 honest about shipped semantics or move typed proof to the post-53 ladder | Today it teaches a half-shipped story | One truthful example ladder | Example 09 manifest/snap updates plus new examples |
| Evergreen docs | `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/REVIEW_SPEC.md`, `docs/WORKFLOW_LAW.md`, `docs/COMPILER_ERRORS.md`, `examples/README.md` | Evergreen docs still describe the pre-integration shipped truth and the specs as unshipped | Rewrite evergreen docs to the shipped second-wave truth and record the final disposition of the enhancement-spec set | No split-brain docs after ship | One live docs story | Final verification sweep and doc review |
| Planning/doc convergence | `docs/archive/second_wave/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md`, `docs/README.md` | Overlapping active mechanics plan contains stale overlapping claims | Fold, supersede, or retire overlapping narrative so only one live architecture story remains for this scope | Leaving both live would preserve planning drift after implementation | One active architecture narrative for this scope | Docs-only verification during finalization |
| VS Code syntax | `editors/vscode/syntaxes/doctrine.tmLanguage.json`, `editors/vscode/scripts/validate_lark_alignment.py` | Top-level decls colorize, but typed attachments and richer body forms are incomplete | Add syntax coverage for the new fields and attachment forms; keep grammar-alignment samples honest | Editor parity must widen with the language | Syntax parity for second-wave surfaces | `cd editors/vscode && make` |
| VS Code navigation | `editors/vscode/resolver.js`, `editors/vscode/tests/integration/suite/index.js`, unit/snap tests, `editors/vscode/README.md` | Global `schema:` -> `json schema`, no `structure:` keyed refs, review contracts assume workflows | Make resolver owner-aware for `schema:`, add `structure:` and `analysis:` coverage, add schema-backed review contract navigation, and update README smoke paths | The extension currently encodes stale semantics | Owner-aware keyed ref resolution and contract navigation | `cd editors/vscode && make` plus updated integration/snapshot suites |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `doctrine/` remains the only semantic owner.
  - `examples/` remains the only proof owner.
  - evergreen `docs/` remains the only shipped documentation owner.
  - `editors/vscode/` remains the only editor-parity owner.
- Deprecated APIs (if any):
  - Global editor resolution of keyed `schema:` as `json schema` regardless of owning surface.
  - Workflow-only review-contract assumptions in compiler, docs, and editor navigation.
  - Placeholder addressability behavior that indexes `analysis` / `schema` / `document` but cannot display or traverse them honestly.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - Any example text or docs wording that presents generic `schema:` / `structure:` record keys as if they were already typed language features.
  - Stale overlapping claims in the mechanics-wave plan or docs index once this artifact becomes the shipped truth for the overlapping scope.
  - Any compiler or editor fallback that keeps both old and new meanings of the same owner path alive in parallel without explicit surface ownership.
- Capability-replacing harnesses to delete or justify:
  - Do not add a sidecar parser, shadow renderer, or editor-only resolver path for the new surfaces.
  - Reuse the existing compiler and readable-block pipeline; justify any extra helper only if the current owner path genuinely cannot express the required rule.
- Live docs/comments/instructions to update or delete:
  - `docs/README.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/REVIEW_SPEC.md`
  - `docs/COMPILER_ERRORS.md`
  - `examples/README.md`
  - `editors/vscode/README.md`
  - the overlapping mechanics-wave plan artifact if it remains stale after ship
- Behavior-preservation signals for refactors:
  - `make verify-examples`
  - targeted `uv run --locked python -m doctrine.verify_corpus --manifest ...`
  - `make verify-diagnostics`
  - `cd editors/vscode && make`
  - the targeted repro for the current `AnalysisDecl` internal-error gap

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Typed attachments | `doctrine/grammars/doctrine.lark`, `doctrine/model.py`, `doctrine/parser.py`, `doctrine/compiler.py`, `editors/vscode/resolver.js` | Owner-aware typed attachment dispatch for `schema:` and `structure:` | Prevents record-key drift between compiler, docs, examples, and editor navigation | include |
| Readable roots | `doctrine/compiler.py`, `editors/vscode/resolver.js` | Full readable/addressable support for `analysis`, `schema`, and `document` | Prevents parser-only declarations and editor-only ghost support | include |
| Review contracts | `doctrine/compiler.py`, `docs/REVIEW_SPEC.md`, `editors/vscode/resolver.js` | Tagged workflow-or-schema contract abstraction | Prevents a second review control plane and workflow-only drift | include |
| Readable render path | `doctrine/compiler.py`, `doctrine/renderer.py` | Reuse one compiled readable-block pipeline for documents and attachment output | Prevents a second markdown renderer or heuristic special cases | include |
| Example truth | `examples/09_outputs`, new post-53 examples, `examples/README.md` | One current-first example story plus a dedicated post-53 proof ladder | Prevents mixed shipped/proposed semantics in one example | include |
| Docs convergence | `docs/README.md`, overlapping mechanics plan artifact | One live architecture and evergreen-doc story after ship | Prevents long-lived narrative drift after implementation | include |
| Extra editor product work | hover, completion, rename, LSP work | Keep parity-only editor scope | Prevents product-scope creep | exclude |
| Future readable-shape reuse on `output shape` | potential `structure:` on reusable output-shape declarations | Mention only if implementation naturally enables it without extra surface area | Prevents speculative scope creep | defer |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 - Syntax and AST convergence

Status: COMPLETED

* Goal: Replace the current placeholder second-wave syntax and AST with the full typed surfaces this integration wave depends on.
* Work:
  - Update `doctrine/grammars/doctrine.lark` for the intended `analysis`,
    `schema`, and `document` body shapes plus reserved agent `analysis:` and
    typed `schema:` / `structure:` attachments.
  - Update `doctrine/model.py` and `doctrine/parser.py` so those surfaces are
    typed AST nodes and explicit attachment slots instead of generic record
    items.
  - Encode the context-sensitive `schema:` rule explicitly:
    `output shape.schema -> json schema`, `output.schema -> Doctrine schema`.
  - Add fail-loud parse/transform rules for duplicate or unsupported attachment
    use and for owner conflicts such as `output.schema` plus local inventory
    ownership.
* Verification (smallest signal):
  - Targeted parse/compile probes for one agent `analysis:` case, one
    `output.schema` case, one `input.structure` case, and one rejected
    owner-conflict case.
  - Keep one small shipped manifest-backed example green while this phase is in
    flight.
* Docs/comments (propagation; only if needed):
  - Add high-leverage code comments at the reserved-field boundary and the
    context-sensitive `schema:` dispatch boundary.
* Exit criteria:
  - The AST carries explicit second-wave structure.
  - Old shipped examples still parse.
  - New surface ownership is no longer implicit in generic record keys.
* Rollback:
  - Revert grammar/model/parser changes as one slice if the AST cannot support
    the later compiler phases cleanly.

## Phase 2 - Compiler, render, and addressability integration

Status: COMPLETED

* Goal: Make `analysis`, `schema`, `document`, and typed attachments compile,
  render, and address through one Doctrine path.
* Work:
  - Add compiler support for agent `analysis:` attachment and natural analysis
    rendering.
  - Add compiler support for `output.schema`, `input.structure`, and
    `output.structure`, using the existing compiled readable-block pipeline.
  - Extend addressable display and child traversal for `analysis`, `schema`,
    `document`, and supported descendants.
  - Update flow/detail emission paths so typed attachments are visible anywhere
    the shipped compiler already surfaces output/input contract summaries.
  - Remove the current internal fallthrough on `AnalysisDecl` and any similar
    second-wave roots.
* Verification (smallest signal):
  - Targeted manifest-backed examples for analysis attachment, schema output
    attachment, document structure attachment, and addressability.
  - Re-run the current `AnalysisDecl` repro and confirm it no longer crashes.
* Docs/comments (propagation; only if needed):
  - Add concise canonical-boundary comments where addressable descendants and
    typed attachments are dispatched.
* Exit criteria:
  - Second-wave roots render and address through the compiler without internal
    errors.
  - There is still one renderer path.
* Rollback:
  - Revert compiler/render integration as a coordinated slice if emitted output
    becomes incoherent or breaks shipped examples.

## Phase 3 - Review/schema contract integration and diagnostics hardening

Status: COMPLETED

* Goal: Ship the intended workflow-or-schema review contract model without
  moving ownership off the current review/output seams.
* Work:
  - Replace workflow-only `ReviewContractSpec` with a tagged workflow-or-schema
    contract abstraction.
  - Extend review gate collection, `contract.*` resolution, `contract.passes`,
    guarded review output sections, and review agreement checks across both
    contract kinds.
  - Add or refine stable diagnostics for unresolved/unsupported attachment use,
    unknown schema gates, and contract-kind violations.
  - Update `docs/COMPILER_ERRORS.md` to describe the shipped error behavior.
* Verification (smallest signal):
  - Targeted manifest-backed examples for schema-backed review contracts and
    compile-negative cases.
  - `make verify-diagnostics` if diagnostics or catalog behavior changed.
* Docs/comments (propagation; only if needed):
  - Update review-boundary comments and the error catalog where second-wave
    behavior is easy to misunderstand later.
* Exit criteria:
  - Review contracts work uniformly across workflow and schema without a second
    review control plane.
  - Failures are user-facing and documented.
* Rollback:
  - Revert the review-contract abstraction and diagnostics slice together if it
    weakens current review-law guarantees.

## Phase 4 - Corpus proof and VS Code parity

Status: COMPLETED

* Goal: Ship proof and editor parity together instead of treating them as
  follow-up cleanup.
* Work:
  - Add the full post-53 example ladder and negative cases for analysis,
    schema, document, typed attachments, addressability, and schema-backed
    review integration.
  - Make `examples/09_outputs` truthful about current versus new attachment
    semantics.
  - Update `editors/vscode/syntaxes/doctrine.tmLanguage.json`,
    `editors/vscode/resolver.js`,
    `editors/vscode/scripts/validate_lark_alignment.py`,
    `editors/vscode/tests/**`, and `editors/vscode/README.md` for the widened
    language.
  - Replace the global `schema:` -> `json schema` resolver assumption with
    owner-aware resolution and add `structure:` plus schema-backed review
    contract navigation.
* Verification (smallest signal):
  - Targeted `uv run --locked python -m doctrine.verify_corpus --manifest ...`
    runs for new examples as they land.
  - `make verify-examples`
  - `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  - Refresh example guide text and VS Code smoke-check instructions to cover the
    new surfaces explicitly.
* Exit criteria:
  - The example corpus proves the new language.
  - VS Code colorization and navigation match shipped compiler truth.
* Rollback:
  - Revert examples and extension changes as one slice if parity remains broken.

## Phase 5 - Evergreen docs, artifact convergence, and final verification

Status: COMPLETED

* Goal: Leave one live language story, one live architecture story, and one
  ready-to-run implementation artifact.
* Work:
  - Update `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`,
    `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/REVIEW_SPEC.md`,
    `docs/WORKFLOW_LAW.md` if needed, `docs/COMPILER_ERRORS.md`,
    `examples/README.md`, and `editors/vscode/README.md` to match shipped
    truth.
  - Decide and apply the final disposition of the enhancement-spec docs in the
    docs index and the overlapping mechanics-wave architecture plan so there is
    no lingering split-brain narrative.
  - Run the final repo-owned verification commands and capture any durable
    implementation notes that future Doctrine work will need.
* Verification (smallest signal):
  - `make verify-examples`
  - `make verify-diagnostics` when applicable
  - `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  - Delete stale claims instead of preserving them as live docs.
* Exit criteria:
  - Evergreen docs, examples, compiler behavior, and editor support all say the
    same thing.
  - The canonical plan is ready for `implement-loop`.
* Rollback:
  - If final verification exposes unresolved semantic drift, reopen the precise
    phase that owns the drift instead of shipping partial truth.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Prefer existing parser/compiler/diagnostic tests and the smallest targeted
  additions needed to prove attachment resolution, schema-backed review
  contracts, readable-output validation, and addressability behavior.
- Do not add brittle deletion proofs, visual-constant tests, or doc-inventory
  gates.

## 8.2 Integration tests (flows)

- Use targeted manifest-backed corpus runs while developing each new example
  slice.
- Use `make verify-examples` as the primary integration signal.
- Run `make verify-diagnostics` whenever diagnostics or error-catalog behavior
  changes.

## 8.3 E2E / device tests (realistic)

- Use `cd editors/vscode && make` as the primary extension-level signal.
- Add targeted VS Code integration coverage only where it proves real parity on
  the widened language surface.
- Keep any manual editor smoke check short and finalization-oriented.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- This is a repo-shipped language/tooling rollout, not a production runtime
  rollout.
- Rollout means one coherent merge where compiler, examples, docs, diagnostics,
  and extension truth land together or in clearly sequenced, non-deceptive
  phases.

## 9.2 Telemetry changes

- No product telemetry surface is obviously required today.
- If `deep-dive` finds a useful repo-local diagnostic or editor smoke signal, it
  should stay small and repo-owned.

## 9.3 Operational runbook

- Before finalization, run the repo verification commands required by touched
  surfaces.
- Rebuild the VS Code package if extension assets change.
- Ensure the live docs index reflects final shipped truth and does not leave the
  enhancement-spec set competing with evergreen docs.

# 10) Decision Log (append-only)

## 2026-04-11 - Use a dedicated integration-surfaces plan artifact

### Context

- The user explicitly requested `$arch-step new` for a full implementation plan
  against `docs/INTEGRATION_SURFACES_SPEC.md`.
- The repo already contains
  `docs/archive/second_wave/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md`, which
  overlaps this problem space but is anchored more broadly on the mechanics-wave
  work.

### Options

- Reuse the broader mechanics-wave plan as-is.
- Create a dedicated canonical plan for the integration-surfaces spec and treat
  the broader mechanics doc as related context.

### Decision

- Create a dedicated canonical artifact for this ask.
- Treat the broader mechanics-wave plan as related evidence, not as the
  controlling doc for this workflow unless later research deliberately folds the
  two together.

### Consequences

- This artifact becomes the single planning source of truth for this workflow.
- Later planning must explicitly resolve overlap with the existing mechanics
  plan so the repo does not keep two drifting architectural narratives.

### Follow-ups

- During `research` and `deep-dive`, compare the overlap between this artifact
  and the mechanics-wave plan and decide whether to merge, supersede, or retire
  the older planning surface for the overlapping scope.

## 2026-04-11 - Keep `schema:` owner-aware instead of globally renaming it

### Context

- The shipped language already uses `schema:` beneath `output shape` to attach a
  `json schema`, and the VS Code resolver currently maps keyed `schema:` refs to
  `json schema` globally.
- `docs/INTEGRATION_SURFACES_SPEC.md` intends `schema:` on `output` itself to
  mean a Doctrine `schema` declaration.

### Options

- Rename one of the surfaces to avoid any `schema:` ambiguity.
- Keep a global `schema:` meaning and silently reinterpret existing sites.
- Keep `schema:` context-sensitive by owning surface.

### Decision

- Keep `schema:` context-sensitive by owning surface.
- `output shape.schema` remains the shipped `json schema` attachment.
- `output.schema` becomes the Doctrine `schema` attachment defined by this
  integration wave.

### Consequences

- Compiler and VS Code resolution must become owner-aware instead of using a
  global `schema -> json schema` assumption.

## 2026-04-11 - Fresh implement-loop audit closed clean

### Context

- The plan phases were already marked complete, but the authoritative
  implementation-audit block still reflected the pre-implementation repo state.
- `implement-loop` requires the artifact to reflect fresh repo reality before
  it can stop clean.

### Options

- Leave the stale `NOT COMPLETE` audit block in place and treat the loop as
  still blocked.
- Run fresh repo-owned verification, rewrite the audit block to current truth,
  and finish the controller clean.

### Decision

- Run a fresh code-completeness audit against the current repo state.
- Keep the phase statuses complete, mark the audit verdict `COMPLETE`, and end
  `implement-loop` with the mandated `Use $arch-docs` handoff.

### Consequences

- The plan artifact now matches the implemented code, examples, docs, and VS
  Code extension instead of preserving stale pre-implementation audit text.
- Any remaining work belongs to the separate docs-cleanup workflow rather than
  to more hidden `arch-step` implementation passes.
  single global keyed-field mapping for `schema:`.
- Docs and examples must explicitly teach the two owner-scoped meanings so this
  does not regress into another split-truth seam.

### Follow-ups

- Add positive and negative proof for both `output shape.schema` and
  `output.schema`.
- Remove any editor or docs fallback that treats the two sites as the same
  surface.
