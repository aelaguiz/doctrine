---
title: "Doctrine - High-Value Authoring Elegance Wins - Architecture Plan"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: phased_refactor
related:
  - docs/DOCTRINE_AUTHORING_SYNTAX_SUGAR_AUDIT_2026-04-16.md
  - docs/DOCTRINE_LANGUAGE_AUDIT_2026-04-16.md
  - doctrine/grammars/doctrine.lark
  - doctrine/parser.py
  - doctrine/_parser/io.py
  - doctrine/_parser/workflows.py
  - doctrine/_parser/agents.py
  - doctrine/_model/io.py
  - doctrine/_model/review.py
  - doctrine/_compiler/indexing.py
  - doctrine/_compiler/resolve/refs.py
  - doctrine/_compiler/resolve/addressables.py
  - doctrine/_compiler/resolve/output_schemas.py
  - doctrine/_compiler/resolve/outputs.py
  - doctrine/_compiler/compile/review_contract.py
  - doctrine/_compiler/validate/contracts.py
  - tests/test_output_schema_surface.py
  - tests/test_output_schema_lowering.py
  - tests/test_final_output.py
  - tests/test_emit_docs.py
  - tests/test_compile_diagnostics.py
  - docs/LANGUAGE_REFERENCE.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/AUTHORING_PATTERNS.md
  - docs/REVIEW_SPEC.md
  - docs/COMPILER_ERRORS.md
  - docs/VERSIONING.md
  - CHANGELOG.md
  - examples/03_imports/prompts/AGENTS.prompt
  - examples/24_io_block_inheritance/prompts/AGENTS.prompt
  - examples/28_addressable_workflow_paths/prompts/AGENTS.prompt
  - examples/79_final_output_output_schema/prompts/AGENTS.prompt
  - examples/85_review_split_final_output_output_schema/prompts/AGENTS.prompt
  - examples/90_split_handoff_and_final_output_shared_route_semantics/prompts/AGENTS.prompt
  - examples/104_review_final_output_output_schema_blocked_control_ready/prompts/AGENTS.prompt
  - examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt
  - examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt
  - examples/107_output_inheritance_basic/prompts/AGENTS.prompt
  - examples/108_output_inheritance_attachments/prompts/AGENTS.prompt
  - examples/117_io_omitted_wrapper_titles/prompts/AGENTS.prompt
  - examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt
---

# TL;DR

## Outcome

Doctrine ships one high-confidence elegance wave that removes the biggest
authoring repetition without redesigning the language or adding sidecar truth
surfaces.

## Problem

Today the language makes authors repeat the same meaning through long module
prefixes, repeated `inherit` lines, repeated review-field identity maps,
verbose first-class IO wrappers, and repeated addressable roots. The repo is
also in the middle of an `output schema` nullability cleanup that must finish
cleanly before later schema sugar can stay honest.

## Approach

Implement only the parser-level and fail-loud wins that clearly lower to
existing Doctrine models:

1. finish `output schema` `nullable` cleanup
2. add import aliases and symbol imports
3. add grouped explicit `inherit { ... }`
4. add identity-binding sugar for `review.fields` and
   `final_output.review_fields`
5. add one-line first-class IO wrapper refs for `inputs` and `outputs`
6. add `self:` shorthand for addressable refs

Everything else that adds a second naming system, implicit merge, broad title
rules, or macro-like indirection stays out of this plan.

## Plan

1. Finish the `nullable` cutover across docs, examples, diagnostics, and proof.
2. Add import aliasing across the full `name_ref` family.
3. Add grouped explicit `inherit` across the inherited keyed-item families.
4. Add review-binding shorthand on the two existing semantic-binding surfaces.
5. Add first-class IO wrapper shorthand on `inputs` and `outputs`.
6. Add `self:` across the existing `PATH_REF` family.
7. Update examples, tests, docs, and compiler errors in the same wave.

## Non-negotiables

- No dual sources of truth.
- No hidden merge by omission.
- No route-only namespace shortcut surface if import aliasing already solves
  the problem.
- No inferred `final_output`.
- No broad title-defaulting sweep.
- No `inherit *`.
- No wire-shape change for the current `OpenAIStructuredOutput` profile.
- Every authoring change must come with example, test, docs, and diagnostics
  truth where appropriate.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-16
external_research_grounding: not started
deep_dive_pass_2: not started
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine implements the high-confidence elegance wave and nothing more,
authors will be able to express the same shipped contracts with materially less
repetition, while the compiler still owns one truth for refs, inheritance,
review bindings, IO wrappers, and route semantics.

## 0.2 In scope

- Finish the `output schema` nullability cleanup already in flight:
  - `nullable` is the authored nullability flag
  - legacy `required` and `optional` stay targeted hard errors on this surface
  - fields and route fields follow the same story
  - emitted wire shape stays unchanged for the current structured-output
    profile
- Add import aliases and symbol imports across the full `name_ref` family:
  - `import x as y`
  - `from x import Name`
  - `from x import Name as Alias`
- Add grouped explicit `inherit { ... }` where Doctrine already requires
  explicit inherited keyed-item accounting:
  - agent authored slots
  - workflow items and workflow law sections
  - skills
  - inputs and outputs blocks
  - analysis sections
  - schema block families
  - document blocks
  - review items
  - output, output shape, and output schema items
- Add identity-binding sugar on the existing semantic-binding surfaces:
  - `review fields:`
  - `review override fields:`
  - `final_output.review_fields:`
- Add one-line first-class IO wrapper refs on:
  - `inputs`
  - `outputs`
  - base entries and override entries
- Add `self:` shorthand across the existing `PATH_REF` family:
  - workflow section ref items
  - record scalar heads
  - output record scalar heads
  - guarded output scalar heads
  - output override scalar heads
  - interpolation that reuses addressable refs
- Update the real example families already exercising these surfaces:
  - `03_imports`
  - `24_io_block_inheritance`
  - `28_addressable_workflow_paths`
  - `79_final_output_output_schema`
  - `85_review_split_final_output_output_schema`
  - `90_split_handoff_and_final_output_shared_route_semantics`
  - `104_review_final_output_output_schema_blocked_control_ready`
  - `105_review_split_final_output_output_schema_control_ready`
  - `106_review_split_final_output_output_schema_partial`
  - `107_output_inheritance_basic`
  - `108_output_inheritance_attachments`
  - `117_io_omitted_wrapper_titles`
  - `121_nullable_route_field_final_output_contract`
- Update the live docs that teach these surfaces:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/AUTHORING_PATTERNS.md`
  - `docs/REVIEW_SPEC.md`
  - `docs/COMPILER_ERRORS.md`
  - `docs/VERSIONING.md`
  - `CHANGELOG.md`
- Add explicit compiler errors where the new surface needs one sharp story:
  - retired `output schema` nullability words
  - import alias collisions or ambiguous imported symbol ownership
  - malformed grouped inherit forms
  - malformed `self:` usage where a declaration-root addressable ref is
    required

## 0.3 Out of scope

- `inherit *` or any keep-the-rest merge-by-omission story
- route-only owner alias surfaces such as `owner scope:`
- output-side semantic tagging or `fields from output`
- compact IO heads like `file(...) -> MarkdownDocument required`
- rooted path literals and path-root registries
- named ref sets or macro-like ref aliases
- `final_output` projection sugar beyond the existing binding surface
- broad title-defaulting or title-omission expansion across unrelated readable
  families
- compact `output schema` field-head sugar in this wave
- changing the current structured-output wire shape or adding an omittable
  property mode
- tightening unrelated high-risk language-audit items such as `workflow:` typed
  field ownership, `route_from` selector typing, or emitted route-vocabulary
  normalization

## 0.4 Definition of done (acceptance evidence)

- `output schema` tells one honest nullability story in code, docs, tests, and
  examples.
- Import aliasing works across the same `name_ref` family Doctrine already
  uses, not only on one favored surface.
- Grouped explicit `inherit` lands across the inherited keyed-item families
  that currently repeat singular `inherit` lines.
- Review-field shorthand works on both review binding surfaces and keeps one
  binding truth after lowering.
- First-class IO wrappers can express one-ref buckets in one line on `inputs`
  and `outputs`.
- `self:` works anywhere Doctrine already accepts an `AddressableRef`.
- The shipped examples teach the new preferred syntax on the existing example
  families instead of adding a second parallel tutorial track.
- Unit tests, diagnostics proof, and manifest-backed examples cover the new
  syntax and the fail-loud boundaries.
- Live docs and release truth match the shipped compatibility posture.

## 0.5 Key invariants (fix immediately if violated)

- No dual sources of truth.
- One ref-resolution story.
- One inheritance-accounting story.
- One review semantic-binding story.
- One IO wrapper story per family.
- One addressable-ref story per `PATH_REF` family.
- No hidden merge.
- No route inference from prose.
- No speculative syntax layer that the compiler cannot lower directly to
  existing truth.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Remove the highest-cost repeated spelling without weakening fail-loud
   behavior.
2. Preserve one source of truth on every touched surface.
3. Prefer parser-level sugar that lowers to the same resolved model.
4. Finish the existing `nullable` cleanup before stacking more schema surface
   novelty.
5. Keep the example corpus, diagnostics, and live docs aligned in the same
   change.

## 1.2 Constraints

- `output schema` nullability is already moving through the repo and cannot be
  planned like a greenfield feature.
- The example corpus is part of shipped proof, not just illustration.
- Some wins are additive while the `nullable` cleanup is a breaking authored
  language cut on that one surface.
- The elegance wave must not turn into a second naming or projection system.

## 1.3 Architectural principles (rules we will enforce)

- Sugar follows shared carrier shapes, not one visible noun.
- Keep one lowering story per concept.
- Prefer explicit deletes and hard errors over shims or aliases that keep old
  words alive.
- Any shorthand must lower to existing compiler-owned truth.
- If a feature needs a second owner path, defer it.

## 1.4 Known tradeoffs (explicit)

- Bundling the `nullable` cleanup with additive sugar keeps the language story
  more elegant, but it mixes one breaking cut with several additive wins.
- Deferring compact schema heads, rooted paths, and macro-like ref sets leaves
  some authoring repetition behind, but it keeps this wave non-speculative.
- Grouped `inherit` should be broad; grouped `override` may stay narrower
  because override bodies are often the semantic unit.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already has the underlying features authors need:

- named imports
- explicit inheritance
- review semantic binding maps
- first-class IO wrappers
- addressable refs
- structured output schemas

The problem is not missing power. The problem is repeated qualification,
repeated explicit bookkeeping, and uneven shorthand across surfaces that lower
to the same internal shapes.

## 2.2 What’s broken / missing (concrete)

- Long module prefixes dominate real authored files.
- Child declarations often restate four or five inherited facts just to add one
  new field.
- Review bindings repeat identity maps like `verdict: verdict`.
- First-class IO wrappers are more verbose than nearby record surfaces.
- Deep addressable refs repeat the same declaration root over and over.
- The `output schema` nullability cleanup is not fully reflected yet in every
  docs and proof surface.

## 2.3 Constraints implied by the problem

- The fixes should reduce repetition without inventing parallel truth.
- The nullability cleanup must stay honest: `nullable` is nullability, not
  omittable presence.
- Any shorthand added only to one family member will look arbitrary quickly.

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- `../rally` and `../psflows` are useful as pressure tests for repetition, not
  as design authorities. Adopt only the bounded ergonomics lesson: shorten
  repeated spelling when the shorter form still lowers to one existing truth.
- Reject broader borrowing from other languages and adjacent repos when it
  adds a second namespace, macro layer, hidden merge model, or sidecar source
  of truth. The code and shipped corpus in this repo remain the authority for
  what Doctrine should add now.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/grammars/doctrine.lark` - the current surface already shows the
    carrier families this plan must move together: singular `inherit` rules,
    `semantic_field_binding`, multiline `io_section`, `PATH_REF`, and the
    `nullable` plus retired `required` / `optional` output-schema flags.
  - `doctrine/parser.py` plus `doctrine/_model/core.py` - `ImportDecl`,
    `NameRef`, and `AddressableRef` are the root carriers for import aliasing
    and `self:` shorthand. Today `import_decl` lowers only an `ImportPath`,
    and `path_ref` always lowers an explicit root name plus path.
  - `doctrine/_compiler/indexing.py` - `_resolve_import_path` and
    `IndexedUnit.imported_units` already own absolute and relative module
    loading. Import aliasing should extend this loader and lookup path, not
    add a route-only or review-only alias layer.
  - `doctrine/_compiler/resolve/refs.py` and
    `doctrine/_compiler/resolve/addressables.py` - declaration lookup and
    addressable-root resolution already define the one compiler-owned truth
    for named refs and deep path refs.
  - `doctrine/_model/io.py`, `doctrine/_parser/io.py`,
    `doctrine/_compiler/resolve/io_contracts.py`, and
    `doctrine/_compiler/validate/contracts.py` - `IoSection`,
    `OverrideIoSection`, and `_resolve_contract_bucket_ref_entry` already own
    first-class IO wrapper structure, inherited IO accounting, and direct
    declaration refs inside `inputs` and `outputs`.
  - `doctrine/_model/review.py`, `doctrine/_parser/reviews.py`,
    `doctrine/_parser/agents.py`, `doctrine/_compiler/resolve/reviews.py`, and
    `doctrine/_compiler/compile/review_contract.py` - `ReviewFieldsConfig` and
    `ReviewFieldBinding` already own review semantic bindings on both
    `review.fields` and `final_output.review_fields`.
  - `doctrine/_model/io.py` and
    `doctrine/_compiler/resolve/output_schemas.py` - `OutputSchemaFlag` now
    carries `nullable`, and the resolver already fails loud with `E236` and
    `E237` for retired `required` and `optional`.
  - `doctrine/_compiler/resolve/agent_slots.py`,
    `doctrine/_compiler/resolve/analysis.py`,
    `doctrine/_compiler/resolve/documents.py`,
    `doctrine/_compiler/resolve/addressable_skills.py`,
    `doctrine/_compiler/resolve/io_contracts.py`,
    `doctrine/_compiler/resolve/reviews.py`, and
    `doctrine/_compiler/resolve/output_schemas.py` - these are the real
    inherited keyed-item owner paths. The missing-entry and undefined-key
    fail-loud rules already repeat across them, which is why grouped explicit
    `inherit` should follow the whole carrier family instead of only outputs.
- Canonical path / owner to reuse:
  - import aliasing: `doctrine/parser.py`, `doctrine/_model/core.py`,
    `doctrine/_compiler/indexing.py`, and `doctrine/_compiler/resolve/refs.py`
    - keep one named-ref lookup story.
  - grouped explicit `inherit`: the existing `InheritItem` carrier in
    `doctrine/_model/core.py` plus each inherited-family resolver - keep one
    explicit accounting story.
  - review-binding shorthand: `ReviewFieldsConfig` /
    `ReviewFieldBinding` in `doctrine/_model/review.py` plus existing parser
    and compile paths - keep one semantic-binding story.
  - IO wrapper shorthand: `IoSection`, `OverrideIoSection`, and
    `_resolve_contract_bucket_ref_entry` - keep one IO-wrapper story.
  - `self:` shorthand: `AddressableRef` in `doctrine/_model/core.py` plus
    addressable resolution in `doctrine/_compiler/resolve/addressables.py` -
    keep one addressable-ref story.
  - output-schema nullability cleanup: `OutputSchemaFlag` and
    `doctrine/_compiler/resolve/output_schemas.py` - keep one nullability
    story and one set of retirement errors.
- Adjacent surfaces tied to the same contract family:
  - `tests/test_import_loading.py`, `tests/test_compiler_boundary.py`,
    `examples/03_imports`, and `examples/README.md` - import loading and typed
    imported-ref proof that must stay aligned if aliasing is added.
  - `tests/test_output_inheritance.py`, `examples/24_io_block_inheritance`,
    `examples/107_output_inheritance_basic`, and
    `examples/108_output_inheritance_attachments` - inherited-entry proof and
    examples that must move together if grouped `inherit` lands.
  - `tests/test_final_output.py`, `tests/test_emit_docs.py`,
    `examples/85_review_split_final_output_output_schema`,
    `examples/90_split_handoff_and_final_output_shared_route_semantics`,
    `examples/104_review_final_output_output_schema_blocked_control_ready`,
    `examples/105_review_split_final_output_output_schema_control_ready`, and
    `examples/106_review_split_final_output_output_schema_partial` - the split
    review/final-output family that already proves the binding surfaces this
    plan wants to shorten.
  - `examples/28_addressable_workflow_paths` - already has a dedicated corpus
    case that repeats explicit declaration roots on self-owned workflow and
    skills paths. That is the proof surface for `self:`; do not add a second
    tutorial track.
  - `tests/test_output_schema_surface.py`,
    `tests/test_output_schema_lowering.py`,
    `tests/test_validate_output_schema.py`,
    `tests/test_prove_output_schema_openai.py`,
    `tests/test_emit_docs.py`, `tests/test_final_output.py`,
    `examples/79_final_output_output_schema`,
    `examples/85_review_split_final_output_output_schema`,
    `examples/90_split_handoff_and_final_output_shared_route_semantics`,
    `examples/104_review_final_output_output_schema_blocked_control_ready`,
    `examples/105_review_split_final_output_output_schema_control_ready`,
    `examples/106_review_split_final_output_output_schema_partial`, and
    `examples/121_nullable_route_field_final_output_contract` - the full
    output-schema and routed-final-output family that must stay aligned while
    the nullability cut finishes.
  - `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
    `docs/AUTHORING_PATTERNS.md`, `docs/REVIEW_SPEC.md`,
    `docs/COMPILER_ERRORS.md`, `docs/VERSIONING.md`, and `CHANGELOG.md` - the
    live public docs that will drift if this wave lands only in code.
- Compatibility posture (separate from `fallback_policy`):
  - Mixed by surface, with no bridge:
    - `output schema` nullability is a clean authored-language cutover to
      `nullable`, with legacy `required` and `optional` kept only as targeted
      hard errors.
    - import aliasing, grouped explicit `inherit`, review-binding shorthand,
      IO wrapper shorthand, and `self:` are additive surface wins that should
      preserve existing authored files.
  - This is the right posture because the nullability cut is already underway
    in grammar, parser, resolver, and tests, while the other five wins lower
    cleanly to existing compiler-owned truth without changing emitted
    contracts.
- Existing patterns to reuse:
  - `tests/test_output_inheritance.py` and the repeated `E003` / undefined-key
    resolver checks - reuse the same explicit-accounting fail-loud pattern for
    grouped `inherit`.
  - `inputs_ref_field` and `outputs_ref_field` in `doctrine/grammars/doctrine.lark`
    plus `_resolve_contract_bucket_ref_entry` - reuse the existing concise
    typed-ref story when adding one-line IO wrapper refs.
  - `semantic_field_binding` in `doctrine/grammars/doctrine.lark` plus
    `ReviewFieldBinding` - add identity sugar by lowering to the same binding
    tuples, not by adding a second semantic-binding surface.
  - `_resolve_import_path` in `doctrine/_compiler/indexing.py` - extend the
    existing import loader instead of adding separate alias resolution logic.
  - `AddressableRef` plus `_resolve_addressable_ref_value` - lower `self:` to
    the same addressable carrier and resolver path.
- Prompt surfaces / agent contract to reuse:
  - `examples/03_imports`, `examples/24_io_block_inheritance`,
    `examples/28_addressable_workflow_paths`, and the `79` / `85` / `90` /
    `104` / `105` / `106` / `121` final-output examples already teach the
    real authored pressure points. Later planning should use these examples as
    the main public teaching ladder.
  - `docs/DOCTRINE_AUTHORING_SYNTAX_SUGAR_AUDIT_2026-04-16.md` and
    `docs/DOCTRINE_LANGUAGE_AUDIT_2026-04-16.md` already rank the candidate
    wins and the consistency rules. They are useful planning inputs, but the
    shipped source and manifest-backed examples stay the authority.
- Native model or agent capabilities to lean on:
  - Not applicable. This is grammar, parser, resolver, docs, and corpus work,
    not prompt repair or model-capability recovery.
- Existing grounding / tool / file exposure:
  - All needed evidence is already local: grammar, parser, model, resolve,
    validate, tests, and examples. No new helper tool, sidecar config, or
    runtime bridge is needed for planning or implementation.
- Duplicate or drifting paths relevant to this change:
  - `examples/121_nullable_route_field_final_output_contract` is already the
    live example path, but its prompt still authors `optional` on the route
    field. That is the clearest current nullability drift and should be
    treated as a same-wave cleanup, not a later doc chore.
  - `examples/28_addressable_workflow_paths` already carries a self-owned
    addressable pressure case, but it still repeats explicit declaration roots
    like `WorkflowRoot:shared...`. That is the concrete proof that `self:`
    should be a shorthand over existing addressable truth, not a new concept.
  - `doctrine/grammars/doctrine.lark` still contains only singular `inherit`
    rules and only `semantic: field_path` review bindings. The planned sugar
    is not shipped yet, so later stages must not assume these surfaces already
    exist just because the audit docs describe them.
- Capability-first opportunities before new tooling:
  - Keep this as direct language work in existing grammar, parser, model,
    resolver, tests, and docs.
  - Do not add a macro system, alias registry, wrapper file, second emitted
    contract, or repo-policing helper script.
- Behavior-preservation signals already available:
  - `tests/test_import_loading.py`, `tests/test_output_inheritance.py`,
    `tests/test_output_schema_surface.py`,
    `tests/test_output_schema_lowering.py`, `tests/test_final_output.py`,
    `tests/test_emit_docs.py`, `tests/test_validate_output_schema.py`, and
    `tests/test_prove_output_schema_openai.py` - direct behavior proof on the
    touched contract families.
  - `make verify-diagnostics` - exact compile-error proof for retired
    nullability words and any new malformed shorthand.
  - `make verify-examples` - manifest-backed proof across the real public
    example ladder.

## 3.3 Decision gaps that must be resolved before implementation

- None at the planning-scope level. The user already approved the high-value
  wave, the explicit defers, and the mixed compatibility posture. Later stages
  should treat those as locked unless new repo evidence reveals a direct
  contradiction.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- Public language surface lives in `doctrine/grammars/doctrine.lark`.
- Public parse lowering is split between `doctrine/parser.py` and the mixins in
  `doctrine/_parser/`.
  - `doctrine/parser.py` owns `import_decl`, `name_ref`, and `path_ref`.
  - `doctrine/_parser/io.py` owns `io_section`, `output schema` flags, output
    inheritance items, and many record-like authoring surfaces.
  - `doctrine/_parser/reviews.py` owns `fields:` and `semantic_field_binding`.
  - `doctrine/_parser/agents.py` owns `final_output.review_fields`.
  - `doctrine/_parser/workflows.py`, `doctrine/_parser/analysis_decisions.py`,
    `doctrine/_parser/transformer.py`, and `doctrine/_parser/skills.py` own
    the other singular `inherit` spellings.
- Typed authored carriers live in `doctrine/_model/`.
  - `doctrine/_model/core.py` owns `ImportDecl`, `NameRef`,
    `AddressableRef`, and `InheritItem`.
  - `doctrine/_model/io.py` owns `IoSection`, `OverrideIoSection`,
    `OutputSchemaFlag`, and output-schema field carriers.
  - `doctrine/_model/review.py` owns `ReviewFieldBinding` and
    `ReviewFieldsConfig`.
- Compile-time ownership is split across existing compiler paths.
  - `doctrine/_compiler/indexing.py` loads imported modules and builds each
    `IndexedUnit`.
  - `doctrine/_compiler/resolve/refs.py` owns named declaration lookup.
  - `doctrine/_compiler/resolve/addressables.py` owns addressable-root and
    path resolution.
  - inherited keyed-item ownership is spread across
    `agent_slots.py`, `workflows.py`, `analysis.py`, `documents.py`,
    `skills.py`, `addressable_skills.py`, `io_contracts.py`, `reviews.py`,
    `outputs.py`, and `output_schemas.py`.
- Public truth beyond code lives in:
  - manifest-backed examples under `examples/`
  - tests under `tests/`
  - live docs under `docs/`
  - syntax support under `editors/vscode/`

## 4.2 Control paths (runtime)

1. `doctrine/parser.py` parses authored `.prompt` files into Doctrine model
   carriers.
2. `doctrine/_compiler/indexing.py` resolves absolute and relative imports into
   `IndexedUnit.imported_units`.
3. resolve paths fan out by concept:
   - named refs through `doctrine/_compiler/resolve/refs.py`
   - addressable refs through `doctrine/_compiler/resolve/addressables.py`
   - inherited keyed items through the family-specific resolvers
4. compile paths consume the resolved declarations:
   - `doctrine/_compiler/compile/review_contract.py` normalizes review and
     split-final-response bindings
   - `doctrine/_compiler/compile/final_output.py` and
     `doctrine/_compiler/compile/agent.py` compile final-output metadata
   - `doctrine/emit_docs.py` and renderers expose public docs and contract
     output
5. proof paths validate the language:
   - targeted unit tests
   - `make verify-diagnostics`
   - `make verify-examples`

## 4.3 Object model + key abstractions

- `ImportDecl` today carries only an `ImportPath`. There is no authored alias
  or symbol-import carrier yet.
- `NameRef` carries `module_parts` plus `declaration_name`, which is why
  authors repeat long module prefixes today.
- `AddressableRef` requires an explicit declaration root plus path. There is no
  current self-owned root shorthand.
- `InheritItem` is singular. Every inherited keyed-item family spells repeated
  `inherit key` lines one at a time.
- `ReviewFieldBinding` always requires `semantic: field_path`, even for pure
  identity binds, and both `review.fields` and `final_output.review_fields`
  share that same explicit authored shape.
- `IoSection` and `OverrideIoSection` require a multiline keyed wrapper when an
  `inputs` or `outputs` bucket needs a stable local key, even when the wrapper
  only contains one child declaration ref.
- `OutputSchemaFlag` now treats `nullable` as the live nullability concept, but
  the parser still accepts `required` and `optional` on this surface only so
  the resolver can fail with targeted retirement errors.

## 4.4 Observability + failure behavior today

- Import loading already fails loud on duplicate declaration names in one
  module (`E288`) and relative imports that walk above the prompt root
  (`E290`).
- Output-schema nullability already fails loud with `E236` and `E237` for
  retired `required` and `optional`.
- Inherited keyed-item families already fail loud on missing inherited entries
  and undefined inherited keys, usually through `E003` plus family-specific
  detail text.
- Current proof is real but uneven across the planned wave:
  - `examples/28_addressable_workflow_paths` already has a self-owned path
    pressure case
  - `examples/121_nullable_route_field_final_output_contract` is the live
    example path, but its prompt still authors `optional`
  - the audit docs describe the planned sugar, but grammar and parser still
    ship only the long forms

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. This is language, compiler, docs, and corpus work.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Keep all ownership in the existing grammar, parser, model, resolve, compile,
  tests, examples, and docs paths.
- Add only the minimum authored-surface support needed for this wave:
  - import alias and symbol-import grammar in `doctrine/grammars/doctrine.lark`
  - grouped explicit `inherit` grammar on the existing inherited families
  - identity binding sugar on the existing semantic-binding surfaces
  - one-line keyed IO wrapper refs on `inputs` and `outputs`
  - `self:` support on existing `PATH_REF` surfaces
- Keep model changes minimal and local:
  - enrich `ImportDecl` in `doctrine/_model/core.py` to carry alias-aware
    import data instead of creating a second import registry
  - keep grouped `inherit` as parser sugar that lowers to ordinary
    `InheritItem`s
  - keep review-binding shorthand as parser sugar that lowers to ordinary
    `ReviewFieldBinding`s
  - keep one-line IO wrapper refs as parser sugar that lowers to ordinary
    `IoSection` / `OverrideIoSection` plus one `RecordRef` child
  - allow a small authored sentinel for `self:` only if `AddressableRef`
    cannot cleanly carry it without ambiguity; resolve it back into ordinary
    addressable truth before path descent
- Do not add sidecar config, helper registries, macro files, or new public
  emitted contracts.

## 5.2 Control paths (future)

1. Parse the new sugar in the existing grammar and transformer surface.
2. Lower sugar directly into existing compiler-owned carriers where possible:
   - grouped `inherit` -> repeated `InheritItem`
   - identity binding -> `ReviewFieldBinding(semantic_field, (semantic_field,))`
   - one-line keyed IO wrapper -> `IoSection` / `OverrideIoSection` with one
     `RecordRef` child and no extra title
3. Extend import indexing and ref resolution, not authored refs themselves:
   - `IndexedUnit` gains one local import-scope story for module aliases and
     imported symbols
   - normal ref resolution continues to own ambiguity and fail-loud behavior
4. Resolve `self:` through the shared addressable path:
   - bind it to the current owning declaration root where an addressable owner
     already exists
   - then run the same path descent, display, and validation code as ordinary
     explicit roots
5. Keep resolve, compile, emit, and validation semantics unchanged unless they
   are directly needed to support sharper diagnostics or the nullability
   cutover cleanup.

## 5.3 Object model + abstractions (future)

- One import story:
  - `ImportDecl` becomes alias-aware and symbol-aware.
  - `NameRef` remains the only named declaration ref carrier.
  - `IndexedUnit` owns one import scope that feeds normal resolution.
- One inheritance story:
  - all grouped authored forms lower to the same `InheritItem` stream the
    resolvers already understand
  - no `inherit *`
  - no merge-by-omission
- One review-binding story:
  - both `review.fields` and `final_output.review_fields` accept bare semantic
    names for identity cases
  - both still lower to the same `ReviewFieldsConfig` and
    `ReviewFieldBinding` carriers
- One IO-wrapper story:
  - `inputs` and `outputs` keyed wrappers accept `key: NameRef` when the
    bucket contains exactly one declaration ref
  - base and override wrappers move together
  - `input source` and `output target` stay out of this wave
- One addressable story:
  - `self:` is valid only on surfaces that already accept `PATH_REF`
  - `law_path` stays explicit and separate
  - no rooted-path registry and no route-owner alias layer
- One output-schema nullability story:
  - `nullable` is the only live authored nullability word
  - legacy `required` and `optional` remain targeted hard errors on this
    surface
  - emitted wire shape stays unchanged for the current
    `OpenAIStructuredOutput` profile

## 5.4 Invariants and boundaries

- No dual sources of truth.
- No fallback or shim layer.
- No wildcard imports.
- No second alias system outside the import/index path.
- No second review-binding or final-output projection system.
- No broad title-defaulting expansion outside the `inputs` / `outputs` wrapper
  family.
- No implicit inheritance semantics.
- No emitted contract drift from the five additive wins.
- Sharp compile errors are part of the public design:
  - legacy output-schema words stay targeted hard errors
  - alias collisions and ambiguous imported symbol ownership fail loud
  - malformed grouped `inherit` fails loud
  - malformed `self:` usage fails loud where no declaration-root addressable
    context exists

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Import surface grammar | `doctrine/grammars/doctrine.lark` | `import_decl`, `import_path` | Supports only `import path` with no alias or symbol import form | Add module alias and symbol-import productions; keep wildcard imports out | This is the highest-value repetition cut and must start at the public surface | `import pkg.mod as alias`; `from pkg.mod import Name`; `from pkg.mod import Name as Alias` | new parser tests; `examples/03_imports`; `make verify-examples` |
| Import parse and model | `doctrine/parser.py`, `doctrine/_model/core.py` | `import_decl`, `ImportDecl` | Lowers only an `ImportPath` | Enrich `ImportDecl` to carry alias-aware import data without changing `NameRef` | Keep one named-ref story and one import carrier | alias-aware import declarations only; `NameRef` stays the ref carrier | import-loading and parser tests |
| Import indexing and resolution | `doctrine/_compiler/indexing.py`, `doctrine/_compiler/resolve/refs.py` | `_resolve_import_path`, `IndexedUnit.imported_units`, named-ref lookup | Loads imported modules, but no local alias scope or imported-symbol scope | Add one local import-scope map and teach named-ref resolution to use it | Avoid a second alias resolver and keep fail-loud ambiguity in the compiler | module aliases and imported symbols resolve through the existing lookup path | `tests/test_import_loading.py`; `tests/test_compiler_boundary.py`; `examples/03_imports` |
| Grouped inherit grammar | `doctrine/grammars/doctrine.lark` | `agent_slot_inherit`, `workflow_inherit`, `law_inherit`, `analysis_inherit`, `schema_inherit`, `document_inherit`, `skills_inherit`, `io_inherit`, `output_inherit`, `output_schema_inherit` | Every inherited family spells singular `inherit key` lines only | Add grouped explicit `inherit { ... }` using each family's existing key token | The repeated accounting rule is shared; the sugar should follow the whole carrier family | grouped explicit `inherit` only; no `inherit *` | new parser coverage; inherited family tests |
| Grouped inherit parse lowering | `doctrine/_parser/workflows.py`, `doctrine/_parser/analysis_decisions.py`, `doctrine/_parser/transformer.py`, `doctrine/_parser/skills.py`, `doctrine/_parser/io.py` | family-specific `*_inherit` methods | Lower only one `InheritItem` at a time | Expand grouped authored forms into repeated `InheritItem`s before resolve | Keep resolver semantics unchanged and fail loud | parser-level sugar only; no resolver-side merge semantics | inherited family tests; `examples/24`; `examples/107`; `examples/108` |
| Inherited family resolvers | `doctrine/_compiler/resolve/agent_slots.py`, `doctrine/_compiler/resolve/workflows.py`, `doctrine/_compiler/resolve/analysis.py`, `doctrine/_compiler/resolve/documents.py`, `doctrine/_compiler/resolve/skills.py`, `doctrine/_compiler/resolve/addressable_skills.py`, `doctrine/_compiler/resolve/io_contracts.py`, `doctrine/_compiler/resolve/reviews.py`, `doctrine/_compiler/resolve/outputs.py`, `doctrine/_compiler/resolve/output_schemas.py` | missing-entry and undefined-key checks | Already enforce explicit inherited accounting with fail-loud errors | Reuse the same semantics unchanged; only sharpen diagnostics if grouped syntax needs clearer blame | This wave is sugar, not an inheritance redesign | same inherited semantics with grouped authoring | `tests/test_output_inheritance.py`; existing family tests |
| Review binding grammar and parse | `doctrine/grammars/doctrine.lark`, `doctrine/_parser/reviews.py`, `doctrine/_parser/agents.py` | `semantic_field_binding`, `fields_stmt`, `final_output_review_fields_stmt` | Requires `semantic: field_path` even for identity cases | Add bare semantic-name entries that lower to the same binding tuple | Remove pure ceremony without adding a second binding surface | `fields:` and `review_fields:` accept bare semantic names for identity binds | review and final-output tests; `examples/106` |
| Review compile validation | `doctrine/_compiler/compile/review_contract.py`, `doctrine/_compiler/compile/final_output.py` | final-response binding validation and payload preview wiring | Consumes explicit bindings only | Accept parser-lowered identity bindings with no semantic change | Keep one semantic-binding truth through compile and emit | no new contract fields; only shorter authoring | `tests/test_final_output.py`; `tests/test_emit_docs.py` |
| IO wrapper grammar and parse | `doctrine/grammars/doctrine.lark`, `doctrine/_parser/io.py`, `doctrine/_model/io.py` | `io_section`, `io_override_section`, `IoSection`, `OverrideIoSection` | Keyed `inputs` / `outputs` wrappers require multiline bodies, even for one child ref | Add `key: NameRef` and `override key: NameRef` sugar that lowers to one-child wrapper sections with no extra title | This is the cleanest IO-side repetition cut and stays inside one family | one-line keyed IO wrapper refs on `inputs` and `outputs` only | IO parser tests; `examples/24`; `examples/117` |
| IO resolve and validation | `doctrine/_compiler/resolve/io_contracts.py`, `doctrine/_compiler/validate/contracts.py` | `_resolve_contract_bucket_ref_entry`, `_resolve_non_inherited_io_items`, `_summarize_non_inherited_contract_items` | Already resolve direct refs and inherited IO blocks with fail-loud shape checks | Keep semantics unchanged and add fail-loud handling for malformed one-line keyed wrappers | Reuse the existing IO contract path instead of inventing a new bucket model | same resolved IO contract; shorter authoring only | IO resolve tests; manifest proof |
| `self:` path surface | `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, `doctrine/_model/core.py` | `PATH_REF`, `path_ref`, `AddressableRef` | Every addressable path requires an explicit declaration root | Add `self:` as an authored shorthand on existing `PATH_REF` surfaces and lower it into the shared addressable path story | Reduce repeated roots without creating a new addressable namespace | `self:path.to.item` on existing addressable-ref surfaces only | addressable parser tests; `examples/28` |
| `self:` resolution and validation | `doctrine/_compiler/resolve/addressables.py`, `doctrine/_compiler/validate/addressable_children.py`, `doctrine/_compiler/validate/addressable_display.py` | `_resolve_addressable_ref_value`, `_resolve_addressable_root_decl`, child walking and display | Resolve only explicit roots today | Rebind `self:` to the current owning declaration root before normal path descent and display | Keep one addressable-resolution story and one error path | same resolved addressable targets with shorter authoring | addressable tests; route and review path-read tests where affected |
| Output-schema nullability cleanup | `doctrine/grammars/doctrine.lark`, `doctrine/_parser/io.py`, `doctrine/_compiler/resolve/output_schemas.py`, `doctrine/_model/io.py` | `output_schema_nullable_stmt`, `output_schema_required_stmt`, `output_schema_optional_stmt`, `OutputSchemaFlag`, `E236`, `E237` | Grammar/parser/resolver now point toward `nullable`, but live examples and docs still drift | Finish the cut across examples, tests, docs, and diagnostics while keeping the same lowered wire shape | The rest of the elegance wave should not stack on top of an unfinished nullability story | `nullable` is the live word; `required` / `optional` stay targeted hard errors | output-schema, final-output, emit-docs, and diagnostics tests; `examples/79`; `85`; `90`; `104`; `105`; `106`; `121` |
| Live docs and release truth | `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/AUTHORING_PATTERNS.md`, `docs/REVIEW_SPEC.md`, `docs/COMPILER_ERRORS.md`, `docs/VERSIONING.md`, `CHANGELOG.md`, `examples/README.md` | public teaching and release guidance | Some docs still teach older nullability words and none yet teach the new sugar wave | Update the live authoring story in the same change | Prevent stale public truth and keep versioning honest | one coherent public story for the six in-scope wins | docs emit and example verification; release-truth review |
| Syntax support | `editors/vscode/` | TextMate grammar and packaged syntax assets | Editor support will drift if grammar changes land without sync | Update syntax support if grammar keywords or forms change | Public syntax support is part of the shipped authoring surface | matching syntax highlight and parsing hints | `cd editors/vscode && make` if touched |

## 6.2 Migration notes

* Canonical owner path / shared code path:
  - imports: `doctrine/parser.py` -> `doctrine/_compiler/indexing.py` -> `doctrine/_compiler/resolve/refs.py`
  - grouped inherit: existing `InheritItem` plus the current family-specific inherited resolvers
  - review bindings: `doctrine/_parser/reviews.py` / `doctrine/_parser/agents.py` -> `doctrine/_compiler/compile/review_contract.py`
  - IO wrappers: `doctrine/_parser/io.py` -> `doctrine/_compiler/resolve/io_contracts.py`
  - `self:`: `doctrine/parser.py` -> `doctrine/_compiler/resolve/addressables.py`
  - nullability: `doctrine/_parser/io.py` -> `doctrine/_compiler/resolve/output_schemas.py`
* Deprecated APIs (if any):
  - `output schema` `required` and `optional` stay retired authored words on this surface only
* Delete list (what must be removed; include superseded shims/parallel paths if any):
  - old `optional` / `required` teaching on live output-schema docs
  - stale `examples/121_optional_route_field_final_output_contract` once the nullable replacement is fully canonical
  - any temporary example or doc wording that suggests a second alias, binding, or path-root system
* Adjacent surfaces tied to the same contract family:
  - `examples/03`, `24`, `28`, `79`, `85`, `90`, `104`, `105`, `106`, `107`, `108`, `117`, and `121`
  - `tests/test_import_loading.py`
  - `tests/test_output_inheritance.py`
  - `tests/test_output_schema_surface.py`
  - `tests/test_output_schema_lowering.py`
  - `tests/test_final_output.py`
  - `tests/test_emit_docs.py`
  - `tests/test_validate_output_schema.py`
  - `tests/test_prove_output_schema_openai.py`
  - `editors/vscode/` if grammar changes affect public syntax support
* Compatibility posture / cutover plan:
  - clean authored-language cutover for output-schema nullability wording
  - additive compatibility for import aliasing, grouped `inherit`, review-binding shorthand, IO wrapper shorthand, and `self:`
  - no bridge and no runtime shim
* Capability-replacing harnesses to delete or justify:
  - none should be added
  - any proposal for alias registries, macro layers, rooted-path registries, or sidecar bind maps is out of scope and should be rejected
* Live docs/comments/instructions to update or delete:
  - live docs listed above
  - example prompts and manifests in the touched families
  - syntax support under `editors/vscode/` if grammar keywords or forms change
* Behavior-preservation signals for refactors:
  - `uv sync`
  - `npm ci`
  - targeted unit tests for touched surfaces
  - `make verify-diagnostics`
  - `make verify-examples`
  - `cd editors/vscode && make` if syntax support changes

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Import naming | `doctrine/parser.py`, `doctrine/_compiler/indexing.py`, `doctrine/_compiler/resolve/refs.py`, all `NameRef` surfaces | one alias-aware import scope | Prevents a route-only or review-only alias story | include |
| Inherited keyed items | all current `*_inherit` grammar and inherited resolvers | grouped explicit `inherit { ... }` lowering to `InheritItem` | Prevents outputs from becoming the only concise inheritance surface | include |
| Review semantic binding | `review.fields`, `review override fields`, `final_output.review_fields` | identity binding sugar over one `ReviewFieldBinding` carrier | Prevents two different review-binding stories | include |
| First-class IO wrappers | `inputs`, `outputs`, base and override keyed wrappers | one-line keyed wrapper refs | Prevents the same wrapper shorthand from landing on only one half of the IO family | include |
| Addressable refs | all existing `PATH_REF` surfaces | `self:` shorthand over one addressable resolver | Prevents a special workflow-only or review-only path story | include |
| Output-schema nullability | output-schema fields and route fields plus docs/examples/tests | one `nullable` story | Prevents compact sugar or docs from reintroducing `optional` semantics | include |
| Compact IO heads | `input`, `output`, `input source`, `output target` | direct head-level compact syntax | Useful, but this wave can stay elegant without widening grammar that far | defer |
| Rooted path literals | possible path-root surfaces outside `PATH_REF` | rooted literal or registry syntax | Adds another naming layer beyond the approved wave | defer |
| Compact schema heads | simple `output schema` fields | inline field-head syntax | Attractive, but it is not part of the approved non-speculative wave | defer |
<!-- arch_skill:block:call_site_audit:end -->

# 7) Depth-First Phased Implementation Plan (authoritative)

## Phase 1 - Finish `output schema` nullability cleanup

Status: planned

* Goal: Make `output schema` tell one honest nullability story everywhere.
* Work:
  - finish live-doc wording and example corpus updates
  - keep `E236` and `E237` sharp and upgrade-oriented
  - keep normal fields and route fields aligned
* Checklist (must all be done):
  - update the remaining live docs that still teach the old words
  - update `79`, `85`, `90`, `104`, `105`, `106`, and `121` as needed
  - update parser/lowering/final-output tests to the new authored wording only
  - keep emitted wire shape unchanged
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_final_output tests.test_emit_docs tests.test_validate_output_schema tests.test_prove_output_schema_openai`
  - `make verify-diagnostics`
  - `make verify-examples`
* Docs/comments (propagation; only if needed):
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/COMPILER_ERRORS.md`
  - `docs/VERSIONING.md`
  - `CHANGELOG.md`
* Exit criteria (all required):
  - no live teaching surface describes `optional` / `required` as live
    `output schema` field words
  - proof passes with unchanged wire shape
* Rollback:
  - revert the authored-language cut as one unit if the repo is not ready to
    ship the breaking surface

## Phase 2 - Add import aliases and symbol imports

Status: planned

* Goal: Remove long repeated module prefixes across the full `name_ref` family.
* Work:
  - extend grammar, parser, model use, and ref resolution for alias-aware
    imports
  - keep wildcards out
  - add fail-loud handling for alias collisions and ambiguous symbol ownership
* Checklist (must all be done):
  - support module aliasing and symbol import forms
  - prove aliasing works across inheritance, typed refs, routes, review refs,
    and declaration-root refs
  - add compile-fail proof for duplicate aliases or ambiguous imported names
  - update `examples/03_imports` as the main teaching example
* Verification (required proof):
  - targeted parser and ref-resolution unit tests
  - manifest proof through updated `03_imports`
  - full `make verify-examples`
* Docs/comments (propagation; only if needed):
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AUTHORING_PATTERNS.md`
  - `docs/COMPILER_ERRORS.md`
* Exit criteria (all required):
  - the same aliasing story works across the full `name_ref` family
  - no second route-only alias layer is needed
* Rollback:
  - remove alias grammar and resolution together

## Phase 3 - Add grouped explicit `inherit`

Status: planned

* Goal: Keep explicit inherited accounting while removing repeated singular
  `inherit` stacks.
* Work:
  - add grouped explicit `inherit { ... }`
  - propagate it across the inherited keyed-item families that share the same
    accounting rule
  - keep hidden merge and `inherit *` out
* Checklist (must all be done):
  - support grouped `inherit` on the intended inherited families
  - keep existing fail-loud missing-parent and undefined-key behavior
  - update the real inherited example families instead of inventing a side
    tutorial
  - add compile-fail proof for malformed grouped forms
* Verification (required proof):
  - targeted unit tests across each inherited family owner path
  - updated `24`, `107`, and `108`
  - full `make verify-examples`
* Docs/comments (propagation; only if needed):
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AUTHORING_PATTERNS.md`
* Exit criteria (all required):
  - grouped `inherit` lands on the real shared families, not just outputs
  - no implicit merge semantics are introduced
* Rollback:
  - drop grouped syntax and keep existing singular explicit forms

## Phase 4 - Add review-binding shorthand

Status: planned

* Goal: Remove repeated identity bindings while keeping one semantic-binding
  truth.
* Work:
  - add bare semantic-name shorthand on the existing binding-map surfaces
  - keep explicit `semantic: path` for non-identity cases
* Checklist (must all be done):
  - support shorthand on `review fields:`
  - support shorthand on `review override fields:`
  - support shorthand on `final_output.review_fields:`
  - keep existing semantic completeness validation
  - update `106` as the main partial-binding proof
* Verification (required proof):
  - targeted review/final-output tests
  - updated `106`
  - full `make verify-examples`
* Docs/comments (propagation; only if needed):
  - `docs/REVIEW_SPEC.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/LANGUAGE_REFERENCE.md`
* Exit criteria (all required):
  - the same shorthand works on both existing binding-map owners
  - no output-side semantic tagging or second binding system is added
* Rollback:
  - remove shorthand and keep explicit bindings only

## Phase 5 - Add first-class IO wrapper shorthand

Status: planned

* Goal: Make `inputs` and `outputs` one-ref wrappers as concise as nearby
  record surfaces.
* Work:
  - add one-line wrapper ref shorthand on first-class IO wrappers
  - support base entries and override entries
  - keep title omission rules family-specific
* Checklist (must all be done):
  - support shorthand on `inputs` and `outputs`
  - keep omitted-title lowering scoped to the IO family only
  - update `24` and `117`
  - add fail-loud proof for ambiguous unsupported shapes
* Verification (required proof):
  - targeted IO parser/resolve tests
  - manifest proof in updated `24` and `117`
  - full `make verify-examples`
* Docs/comments (propagation; only if needed):
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AUTHORING_PATTERNS.md`
* Exit criteria (all required):
  - first-class IO no longer looks worse than nearby record syntax
  - no broad title-defaulting expansion leaks into unrelated readable families
* Rollback:
  - remove shorthand and keep the current multiline IO wrapper form

## Phase 6 - Add `self:` addressable refs and do the final consistency pass

Status: planned

* Goal: Reduce repeated declaration roots on existing `PATH_REF` surfaces and
  finish the wave as one coherent language story.
* Work:
  - add `self:` shorthand on the existing `AddressableRef` family
  - keep `law_path` separate
  - update the real addressable-ref example and do the final docs/example/test
    consistency pass for the whole wave
* Checklist (must all be done):
  - support `self:` anywhere Doctrine already accepts `path_ref`
  - add fail-loud proof for unsupported or malformed use
  - update `28` as the main teaching example
  - run the final docs/examples/diagnostics alignment pass for the entire
    elegance wave
* Verification (required proof):
  - targeted `PATH_REF` tests
  - updated `28`
  - `make verify-diagnostics`
  - `make verify-examples`
* Docs/comments (propagation; only if needed):
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AUTHORING_PATTERNS.md`
  - `CHANGELOG.md`
* Exit criteria (all required):
  - `self:` behaves like a pure shorthand over existing addressable truth
  - the full wave reads as one coherent public story
* Rollback:
  - remove `self:` support and keep existing explicit roots

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- `tests/test_output_schema_surface.py`
- `tests/test_output_schema_lowering.py`
- `tests/test_final_output.py`
- `tests/test_emit_docs.py`
- `tests/test_compile_diagnostics.py`
- any new or adjacent parser / resolve tests needed for import aliasing,
  grouped inherit, IO shorthand, and `self:`

## 8.2 Manifest-backed proof (corpus)

- update and verify the touched example families:
  - `03_imports`
  - `24_io_block_inheritance`
  - `28_addressable_workflow_paths`
  - `79_final_output_output_schema`
  - `85_review_split_final_output_output_schema`
  - `90_split_handoff_and_final_output_shared_route_semantics`
  - `104_review_final_output_output_schema_blocked_control_ready`
  - `105_review_split_final_output_output_schema_control_ready`
  - `106_review_split_final_output_output_schema_partial`
  - `107_output_inheritance_basic`
  - `108_output_inheritance_attachments`
  - `117_io_omitted_wrapper_titles`
  - `121_nullable_route_field_final_output_contract`

## 8.3 Diagnostics proof

- keep `E236` / `E237` exact and user-facing
- add exact diagnostics where new shorthand introduces malformed or ambiguous
  forms that should fail loud
- run `make verify-diagnostics`

## 8.4 Full verification commands

- `uv sync`
- `npm ci`
- `make verify-examples`
- `make verify-diagnostics`
- if `editors/vscode/` changes, run `cd editors/vscode && make`

# 9) Rollout / Ops / Telemetry

## 9.1 Compatibility posture

- `output schema` nullability cleanup is a clean breaking authored-language
  cut on that one surface.
- The other planned wins are additive and should preserve existing prompt
  files.
- No runtime shim or alias bridge is approved.

## 9.2 Release and docs duties

- update `docs/VERSIONING.md`
- update `CHANGELOG.md`
- keep live docs and corpus proof aligned in the same change

## 9.3 Telemetry / runtime ops

Not applicable beyond compile-time proof and emitted artifact verification.

# 10) Decision Log (append-only)

- 2026-04-16: This plan intentionally takes only the high-confidence elegance
  wave from the two audit docs.
- 2026-04-16: `output schema` nullability is treated as an accepted direction
  to finish cleanly, not as an unresolved semantics question.
- 2026-04-16: Deferred from this wave by default: compact schema heads,
  compact IO heads, rooted path literals, named ref sets, route-owner aliases,
  `final_output` projection sugar, broad title-defaulting expansion,
  `inherit *`, and any output-side semantic tagging.
