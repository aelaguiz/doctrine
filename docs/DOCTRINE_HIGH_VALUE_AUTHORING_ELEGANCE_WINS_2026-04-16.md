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
already on the `output schema` `nullable` baseline in grammar, live docs, and
the public example ladder. This plan should treat that baseline as current
truth and only close any leftover proof or diagnostics drift before later
authoring sugar lands.

## Approach

Implement only the parser-level and fail-loud wins that clearly lower to
existing Doctrine models:

1. keep the current `output schema` `nullable` baseline honest
2. add import aliases and symbol imports
3. add grouped explicit `inherit { ... }`
4. add identity-binding sugar for `review.fields` and
   `final_output.review_fields`
5. add one-line first-class IO wrapper refs for `inputs` and `outputs`
6. add `self:` shorthand for addressable refs

Everything else that adds a second naming system, implicit merge, broad title
rules, or macro-like indirection stays out of this plan.

## Plan

1. Lock the `nullable` baseline across docs, examples, diagnostics, and proof.
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
deep_dive_pass_2: done 2026-04-16
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

- Keep the shipped `output schema` nullability baseline honest:
  - `nullable` is the authored nullability flag
  - legacy `required` and `optional` stay targeted hard errors on this surface
  - fields and route fields follow the same story
  - live docs, release truth, and the public example ladder keep teaching that
    same baseline
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
  - `86_imported_review_comment_local_routes`
  - `90_split_handoff_and_final_output_shared_route_semantics`
  - `104_review_final_output_output_schema_blocked_control_ready`
  - `105_review_split_final_output_output_schema_control_ready`
  - `106_review_split_final_output_output_schema_partial`
  - `107_output_inheritance_basic`
  - `108_output_inheritance_attachments`
  - `109_imported_review_handoff_output_inheritance`
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
- Add explicit fail-loud diagnostics where the new surface needs one sharp
  story:
  - retired `output schema` nullability words
  - import alias collisions or ambiguous imported symbol ownership
  - malformed grouped `inherit` forms at the parser or compile boundary, as
    appropriate
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

- The shipped `output schema` `nullable` baseline stays honest in code, docs,
  tests, and examples.
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

- `output schema` nullability is now largely landed in the repo and should be
  treated as shipped baseline plus regression guard, not as greenfield feature
  work.
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
- The `output schema` nullability baseline is now mostly reflected in shipped
  docs and proof, but this plan still needs to keep that baseline honest while
  later sugar lands.

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
  - `doctrine/_compiler/session.py` and `doctrine/_compiler/context.py` -
    `CompilationSession` now owns the module graph, caches, and parallel
    compile fan-out, while `CompilationContext` owns the task-local
    resolve/validate/compile mixin boundary. Import work must preserve this
    session-scoped load path instead of adding ad hoc module state.
  - `doctrine/parser.py` plus `doctrine/_model/core.py` - `ImportDecl`,
    `NameRef`, and `AddressableRef` are the root carriers for import aliasing
    and `self:` shorthand. Today `import_decl` lowers only an `ImportPath`,
    and `path_ref` always lowers an explicit root name plus path.
  - `doctrine/_compiler/indexing.py`, `doctrine/_compiler/resolve/refs.py`,
    and `doctrine/_compiler/reference_diagnostics.py` -
    `_resolve_import_path`, `IndexedUnit.imported_units`, and the shared
    reference diagnostics helpers already own absolute and relative module
    loading plus fail-loud named-ref lookup. Import aliasing should extend
    this path, not add a route-only or review-only alias layer.
  - `doctrine/_compiler/resolve/addressables.py` and
    `doctrine/_compiler/reference_diagnostics.py` - addressable-root
    resolution, deep path descent, and fail-loud addressable diagnostics
    already define the one compiler-owned truth for deep path refs.
  - `doctrine/_model/io.py`, `doctrine/_parser/io.py`,
    `doctrine/_compiler/validate/contracts.py`,
    `doctrine/_compiler/resolve/io_contracts.py`, and
    `doctrine/_compiler/resolve/outputs.py` - `IoSection`,
    `OverrideIoSection`, contract-summary helpers, bucket-level contract
    lowering, inherited IO-body lowering, omitted-title rules, and previous-
    turn output bindings already live on a real shared owner path. IO
    shorthand should extend that path, not replace it with a third one.
  - `doctrine/_model/review.py`, `doctrine/_parser/reviews.py`,
    `doctrine/_parser/agents.py`, `doctrine/_compiler/resolve/reviews.py`, and
    `doctrine/_compiler/compile/review_contract.py` - `ReviewFieldsConfig` and
    `ReviewFieldBinding` already own review semantic bindings on both
    `review.fields` and `final_output.review_fields`.
  - `doctrine/_model/io.py`,
    `doctrine/_compiler/resolve/output_schemas.py`,
    `doctrine/_compiler/output_schema_validation.py`, and
    `doctrine/_compiler/output_schema_diagnostics.py` - `OutputSchemaFlag` now
    carries `nullable`, the resolver already fails loud with `E236` and
    `E237` for retired `required` and `optional`, and the dedicated validator
    owns the Draft 2020-12 and OpenAI-subset checks that guard lowered final
    output schemas.
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
    `doctrine/_compiler/session.py`, `doctrine/_compiler/indexing.py`,
    `doctrine/_compiler/resolve/refs.py`, and
    `doctrine/_compiler/reference_diagnostics.py` - keep one named-ref lookup
    story on the current session-scoped import graph.
  - grouped explicit `inherit`: the existing `InheritItem` carrier in
    `doctrine/_model/core.py` plus each inherited-family resolver - keep one
    explicit accounting story.
  - review-binding shorthand: `ReviewFieldsConfig` /
    `ReviewFieldBinding` in `doctrine/_model/review.py` plus existing parser
    and compile paths - keep one semantic-binding story.
  - IO wrapper shorthand: `IoSection`, `OverrideIoSection`,
    `ValidateContractsMixin`, `ResolveIoContractsMixin`, and
    `ResolveOutputsMixin` - keep the current IO owner split coherent and avoid
    a third lowering path.
  - `self:` shorthand: `AddressableRef` in `doctrine/_model/core.py` plus
    addressable resolution in `doctrine/_compiler/resolve/addressables.py` -
    keep one addressable-ref story.
  - output-schema nullability cleanup: `OutputSchemaFlag`,
    `doctrine/_compiler/resolve/output_schemas.py`,
    `doctrine/_compiler/output_schema_validation.py`, and
    `doctrine/_compiler/output_schema_diagnostics.py` - keep one nullability
    story, one set of retirement errors, and one lowered-schema validation
    path.
- Adjacent surfaces tied to the same contract family:
  - `tests/test_import_loading.py`, `tests/test_compiler_boundary.py`,
    `tests/test_emit_flow.py`, `tests/test_review_imported_outputs.py`,
    `examples/03_imports`, `examples/86_imported_review_comment_local_routes`,
    `examples/109_imported_review_handoff_output_inheritance`, and
    `examples/README.md` - import loading and imported-output proof that must
    stay aligned if aliasing is added.
  - `tests/test_output_inheritance.py`, `examples/24_io_block_inheritance`,
    `examples/107_output_inheritance_basic`, and
    `examples/108_output_inheritance_attachments` - inherited-entry proof and
    examples that must move together if grouped `inherit` lands.
  - `tests/test_final_output.py`, `tests/test_emit_docs.py`,
    `tests/test_review_imported_outputs.py`,
    `examples/85_review_split_final_output_output_schema`,
    `examples/86_imported_review_comment_local_routes`,
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
    `tests/test_output_schema_validation.py`,
    `tests/test_validate_output_schema.py`,
    `tests/test_prove_output_schema_openai.py`,
    `tests/test_emit_docs.py`, `tests/test_final_output.py`,
    `tests/test_route_output_semantics.py`,
    `examples/79_final_output_output_schema`,
    `examples/85_review_split_final_output_output_schema`,
    `examples/90_split_handoff_and_final_output_shared_route_semantics`,
    `examples/104_review_final_output_output_schema_blocked_control_ready`,
    `examples/105_review_split_final_output_output_schema_control_ready`,
    `examples/106_review_split_final_output_output_schema_partial`, and
    `examples/121_nullable_route_field_final_output_contract` - the full
    output-schema and routed-final-output family that must stay aligned while
    the nullability baseline stays locked.
  - `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
    `docs/AUTHORING_PATTERNS.md`, `docs/REVIEW_SPEC.md`,
    `docs/COMPILER_ERRORS.md`, `docs/VERSIONING.md`, and `CHANGELOG.md` - the
    live public docs that will drift if this wave lands only in code.
- Compatibility posture (separate from `fallback_policy`):
  - Mixed by surface, with no bridge:
    - `output schema` nullability now uses `nullable` as the live authored
      baseline, with legacy `required` and `optional` kept only as targeted
      hard errors.
    - import aliasing, grouped explicit `inherit`, review-binding shorthand,
      IO wrapper shorthand, and `self:` are additive surface wins that should
      preserve existing authored files.
  - This is the right posture because the nullability baseline already ships
    in grammar, parser, resolver, docs, examples, and tests, while the other
    five wins lower cleanly to existing compiler-owned truth without changing
    emitted contracts.
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
    `examples/28_addressable_workflow_paths`, and the `79` / `85` / `86` /
    `90` / `104` / `105` / `106` / `109` / `121` final-output examples
    already teach the real authored pressure points. Later planning should
    use these examples as the main public teaching ladder.
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
    live example path and authors `nullable` on the route field. The main
    nullability risk now is stale stragglers or validation drift, not a broad
    cutover that still needs to happen.
  - `examples/28_addressable_workflow_paths` already carries a self-owned
    addressable pressure case, but it still repeats explicit declaration roots
    like `WorkflowRoot:shared...`. That is the concrete proof that `self:`
    should be a shorthand over existing addressable truth, not a new concept.
  - The live output-schema docs already teach `nullable` as the public word,
    and `examples/79_final_output_output_schema` still keeps the retired
    `required` and `optional` prompts only as negative diagnostics proof.
  - `doctrine/grammars/doctrine.lark` still contains only singular `inherit`
    rules and only `semantic: field_path` review bindings. The planned sugar
    is not shipped yet, so later stages must not assume these surfaces already
    exist just because the audit docs describe them.
  - `doctrine/_compiler/resolve/outputs.py` already calls
    `_resolve_contract_bucket_items()` and owns `_resolve_io_body()`,
    `_resolve_io_section_item()`, and `_lower_omitted_io_section()`. Phase 5
    should extend this live split instead of planning a new shared-helper
    extraction from scratch.
- Capability-first opportunities before new tooling:
  - Keep this as direct language work in existing grammar, parser, model,
    resolver, tests, and docs.
  - Do not add a macro system, alias registry, wrapper file, second emitted
    contract, or repo-policing helper script.
- Behavior-preservation signals already available:
  - `tests/test_import_loading.py`, `tests/test_output_inheritance.py`,
    `tests/test_output_schema_surface.py`,
    `tests/test_output_schema_lowering.py`, `tests/test_final_output.py`,
    `tests/test_emit_docs.py`, `tests/test_validate_output_schema.py`,
    `tests/test_output_schema_validation.py`,
    `tests/test_prove_output_schema_openai.py`,
    `tests/test_review_imported_outputs.py`, and
    `tests/test_route_output_semantics.py` - direct behavior proof on the
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
  - `doctrine/_compiler/session.py` owns the stable compile session boundary,
    import-root resolution, module cache, and parallel compile fan-out.
  - `doctrine/_compiler/context.py` owns the task-local
    resolve/validate/compile/flow mixin boundary over that session.
  - `doctrine/_compiler/indexing.py` loads imported modules and builds each
    `IndexedUnit`.
  - `doctrine/_compiler/resolve/refs.py` plus
    `doctrine/_compiler/reference_diagnostics.py` own named declaration lookup
    and its fail-loud diagnostics.
  - `doctrine/_compiler/resolve/addressables.py` plus
    `doctrine/_compiler/reference_diagnostics.py` own addressable-root and
    path resolution.
  - first-class IO ownership is already split across three focused surfaces:
    - `doctrine/_compiler/validate/contracts.py` owns contract-summary and
      explicit-accounting checks for typed `inputs` / `outputs` fields
    - `doctrine/_compiler/resolve/io_contracts.py` owns bucket-level contract
      lowering and direct declaration refs
    - `doctrine/_compiler/resolve/outputs.py` owns inherited named
      `inputs` / `outputs` bodies, omitted-title lowering, field ref/patch
      resolution, previous-turn selector validation, and output bindings
  - inherited keyed-item ownership is spread across
    `agent_slots.py`, `workflows.py`, `analysis.py`, `documents.py`,
    `skills.py`, `addressable_skills.py`, `io_contracts.py`, `reviews.py`,
    `outputs.py`, and `output_schemas.py`.
  - output-schema lowering and schema-shape diagnostics are split between
    `doctrine/_compiler/resolve/output_schemas.py`,
    `doctrine/_compiler/output_schema_validation.py`, and
    `doctrine/_compiler/output_schema_diagnostics.py`.
  - package- and file-scoped compiler diagnostics now have focused helpers in
    `doctrine/_compiler/package_diagnostics.py`.
- Public truth beyond code lives in:
  - manifest-backed examples under `examples/`
  - tests under `tests/`
  - live docs under `docs/`
  - syntax support under `editors/vscode/`

## 4.2 Control paths (runtime)

1. `doctrine/parser.py` parses authored `.prompt` files into Doctrine model
   carriers.
2. `doctrine/_compiler/session.py` builds the session-scoped module graph and
   `doctrine/_compiler/indexing.py` resolves absolute and relative imports
   into `IndexedUnit.imported_units`.
3. resolve paths fan out by concept:
   - named refs through `doctrine/_compiler/resolve/refs.py` plus shared
     reference diagnostics
   - addressable refs through `doctrine/_compiler/resolve/addressables.py`
     plus shared reference diagnostics
   - inherited keyed items through the family-specific resolvers
   - IO bodies through `doctrine/_compiler/validate/contracts.py`,
     `doctrine/_compiler/resolve/io_contracts.py`, and
     `doctrine/_compiler/resolve/outputs.py`
   - output-schema lowering and validation through
     `doctrine/_compiler/resolve/output_schemas.py` and
     `doctrine/_compiler/output_schema_validation.py`
4. compile paths consume the resolved declarations:
   - `doctrine/_compiler/compile/review_contract.py` normalizes review and
     split-final-response bindings
   - `doctrine/_compiler/compile/final_output.py` and
     `doctrine/_compiler/compile/agent.py` compile final-output metadata
   - `doctrine/emit_docs.py` and renderers expose public docs and contract
     output, including the current top-level runtime `io` payload in
     `final_output.contract.json`
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
  (`E290`). Imported-review and imported-output cases now also have direct
  proof in `tests/test_emit_flow.py`, `tests/test_review_imported_outputs.py`,
  and `examples/86_imported_review_comment_local_routes`.
- Output-schema nullability already fails loud with `E236` and `E237` for
  retired `required` and `optional`, and the live docs plus public examples
  already teach `nullable` as the shipped word.
- Lowered schema and example validation now fail loud through
  `doctrine/_compiler/output_schema_validation.py` with dedicated proof in
  `tests/test_output_schema_validation.py` and route-output coverage in
  `tests/test_route_output_semantics.py`.
- Inherited keyed-item families already fail loud on missing inherited entries
  and undefined inherited keys, usually through `E003` plus family-specific
  detail text.
- Current proof is real but uneven across the planned wave:
  - `examples/28_addressable_workflow_paths` already has a self-owned path
    pressure case
  - `examples/121_nullable_route_field_final_output_contract` is the live
    route-field nullability example and already teaches `nullable`
  - import-resolution proof already extends past `03_imports` into
    `tests/test_emit_flow.py`, `tests/test_compiler_boundary.py`, and
    `tests/test_review_imported_outputs.py`, so alias work must preserve
    imported runtime-package and imported review/output behavior too
  - the audit docs describe the planned sugar, but grammar and parser still
    ship only the long forms

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. This is language, compiler, docs, and corpus work.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Keep all ownership in the existing grammar, parser, model, resolve, compile,
  tests, examples, docs, and the current session/context boundary.
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
- Extend the current IO owner split instead of inventing a new one:
  - `ValidateContractsMixin` keeps contract-summary truth
  - `ResolveIoContractsMixin` keeps bucket-level direct-ref lowering
  - `ResolveOutputsMixin` keeps inherited IO bodies, omitted-title rules, and
    field ref/patch lowering
  - `doctrine/emit_docs.py` keeps the runtime `io` payload unchanged
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
   - the session-scoped `IndexedUnit` graph gains one local import-scope story
     for module aliases and imported symbols
   - normal ref resolution continues to own ambiguity and fail-loud behavior
4. Resolve `self:` through the shared addressable path:
   - bind it to the current owning declaration root where an addressable owner
     already exists
   - then run the same path descent, display, and validation code as ordinary
     explicit roots
5. Keep resolve, compile, emit, and validation semantics unchanged unless they
   are directly needed to support sharper diagnostics, preserve the current
   `nullable` baseline, or keep the runtime `io` contract payload stable.

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
  - the current `ValidateContractsMixin` -> `ResolveIoContractsMixin` ->
    `ResolveOutputsMixin` owner split stays the only lowering path
  - `input source` and `output target` stay out of this wave
- One addressable story:
  - `self:` is valid only on surfaces that already accept `PATH_REF`
  - `law_path` stays explicit and separate
  - no rooted-path registry and no route-owner alias layer
- One output-schema nullability story:
  - `nullable` is the only live authored nullability word
  - legacy `required` and `optional` remain targeted hard errors on this
    surface
  - lowered-schema and example validation keep flowing through the dedicated
    output-schema validator path
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
- Sharp fail-loud diagnostics are part of the public design:
  - legacy output-schema words stay targeted hard errors
  - alias collisions and ambiguous imported symbol ownership fail loud
  - malformed grouped `inherit` fails loud at the parser or compile boundary,
    as appropriate
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
| Import indexing and resolution | `doctrine/_compiler/session.py`, `doctrine/_compiler/indexing.py`, `doctrine/_compiler/resolve/refs.py`, `doctrine/_compiler/reference_diagnostics.py` | session-scoped module graph, `_resolve_import_path`, `IndexedUnit.imported_units`, named-ref lookup | Loads imported modules through the current session-scoped graph, but no local alias scope or imported-symbol scope exists yet | Add one local import-scope map and teach named-ref resolution to use it | Avoid a second alias resolver and keep fail-loud ambiguity in the compiler | module aliases and imported symbols resolve through the existing lookup path | `tests/test_import_loading.py`; `tests/test_compiler_boundary.py`; `tests/test_emit_flow.py`; `tests/test_review_imported_outputs.py`; `examples/03_imports`; `examples/86_imported_review_comment_local_routes`; `examples/109_imported_review_handoff_output_inheritance` |
| Grouped inherit grammar | `doctrine/grammars/doctrine.lark` | `agent_slot_inherit`, `workflow_inherit`, `law_inherit`, `analysis_inherit`, `schema_inherit`, `document_inherit`, `review_inherit`, `skills_inherit`, `io_inherit`, `output_inherit`, `output_schema_inherit` | Every inherited family spells singular `inherit key` lines only | Add grouped explicit `inherit { ... }` using each family's existing key token | The repeated accounting rule is shared; the sugar should follow the whole carrier family | grouped explicit `inherit` only; no `inherit *` | new parser coverage; inherited family tests |
| Grouped inherit parse lowering | `doctrine/_parser/workflows.py`, `doctrine/_parser/analysis_decisions.py`, `doctrine/_parser/transformer.py`, `doctrine/_parser/reviews.py`, `doctrine/_parser/skills.py`, `doctrine/_parser/io.py` | family-specific `*_inherit` methods | Lower only one `InheritItem` at a time | Expand grouped authored forms into repeated `InheritItem`s before resolve | Keep resolver semantics unchanged and fail loud | parser-level sugar only; no resolver-side merge semantics | inherited family tests; `examples/24`; `examples/107`; `examples/108` |
| Inherited family resolvers | `doctrine/_compiler/resolve/agent_slots.py`, `doctrine/_compiler/resolve/workflows.py`, `doctrine/_compiler/resolve/analysis.py`, `doctrine/_compiler/resolve/documents.py`, `doctrine/_compiler/resolve/skills.py`, `doctrine/_compiler/resolve/addressable_skills.py`, `doctrine/_compiler/resolve/io_contracts.py`, `doctrine/_compiler/resolve/reviews.py`, `doctrine/_compiler/resolve/outputs.py`, `doctrine/_compiler/resolve/output_schemas.py` | missing-entry and undefined-key checks | Already enforce explicit inherited accounting with fail-loud errors | Reuse the same semantics unchanged; only sharpen diagnostics if grouped syntax needs clearer blame | This wave is sugar, not an inheritance redesign | same inherited semantics with grouped authoring | `tests/test_output_inheritance.py`; existing family tests |
| Review binding grammar and parse | `doctrine/grammars/doctrine.lark`, `doctrine/_parser/reviews.py`, `doctrine/_parser/agents.py` | `semantic_field_binding`, `fields_stmt`, `final_output_review_fields_stmt` | Requires `semantic: field_path` even for identity cases | Add bare semantic-name entries that lower to the same binding tuple | Remove pure ceremony without adding a second binding surface | `fields:` and `review_fields:` accept bare semantic names for identity binds while explicit identity binds stay legal | review and final-output tests; `tests/test_review_imported_outputs.py`; `examples/85`; `examples/86`; `examples/90`; `examples/104`; `examples/105`; `examples/106` |
| Review compile validation | `doctrine/_compiler/compile/review_contract.py`, `doctrine/_compiler/compile/final_output.py` | final-response binding validation and payload preview wiring | Consumes explicit bindings only | Accept parser-lowered identity bindings with no semantic change | Keep one semantic-binding truth through compile and emit | no new contract fields; only shorter authoring | `tests/test_final_output.py`; `tests/test_emit_docs.py` |
| IO wrapper grammar and parse | `doctrine/grammars/doctrine.lark`, `doctrine/_parser/io.py`, `doctrine/_model/io.py` | `io_section`, `io_override_section`, `IoSection`, `OverrideIoSection` | Keyed `inputs` / `outputs` wrappers require multiline bodies, even for one child ref | Add `key: NameRef` and `override key: NameRef` sugar that lowers to one-child wrapper sections with no extra title | This is the cleanest IO-side repetition cut and stays inside one family | one-line keyed IO wrapper refs on `inputs` and `outputs` only | IO parser tests; `examples/24`; `examples/117` |
| IO resolve and validation | `doctrine/_compiler/validate/contracts.py`, `doctrine/_compiler/resolve/io_contracts.py`, `doctrine/_compiler/resolve/outputs.py`, `doctrine/emit_docs.py` | `_summarize_contract_field`, `_resolve_contract_bucket_ref_entry`, `_resolve_non_inherited_io_items`, `_resolve_io_section_item`, `_lower_omitted_io_section` | The live IO path already has a real owner split: contract summary in `validate/contracts.py`, bucket lowering in `resolve/io_contracts.py`, inherited IO-body and omitted-title lowering in `resolve/outputs.py`, and public contract emission in `emit_docs.py` | Add one-line keyed-wrapper behavior by extending those existing owners and reusing the current bucket and omitted-title path | Prevent a third IO lowering path and keep the runtime `io` contract stable | same resolved IO contract and emitted runtime payload; shorter authoring only | IO resolve tests; `tests/test_output_rendering.py`; `tests/test_emit_docs.py`; `examples/24`; `examples/117`; manifest proof |
| `self:` path surface | `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, `doctrine/_model/core.py` | `PATH_REF`, `path_ref`, `AddressableRef` | Every addressable path requires an explicit declaration root | Add `self:` as an authored shorthand on existing `PATH_REF` surfaces and lower it into the shared addressable path story | Reduce repeated roots without creating a new addressable namespace | `self:path.to.item` on existing addressable-ref surfaces only | addressable parser tests; `examples/28` |
| `self:` resolution and validation | `doctrine/_compiler/resolve/addressables.py`, `doctrine/_compiler/validate/addressable_children.py`, `doctrine/_compiler/validate/addressable_display.py` | `_resolve_addressable_ref_value`, `_resolve_addressable_root_decl`, child walking and display | Resolve only explicit roots today | Rebind `self:` to the current owning declaration root before normal path descent and display | Keep one addressable-resolution story and one error path | same resolved addressable targets with shorter authoring | addressable tests; route and review path-read tests where affected |
| Output-schema nullability cleanup | `doctrine/grammars/doctrine.lark`, `doctrine/_parser/io.py`, `doctrine/_compiler/resolve/output_schemas.py`, `doctrine/_compiler/output_schema_validation.py`, `doctrine/_compiler/output_schema_diagnostics.py`, `doctrine/_model/io.py` | `output_schema_nullable_stmt`, `output_schema_required_stmt`, `output_schema_optional_stmt`, `OutputSchemaFlag`, `E236`, `E237`, lowered-schema validator | Grammar, parser, resolver, live docs, and public examples already align on `nullable`, and retired words remain only as negative diagnostics proof | Keep that baseline locked, close any leftover stale references, and preserve the dedicated validator and diagnostics path while later sugar lands | The rest of the elegance wave should not stack on top of a drifting nullability story | `nullable` is the live word; `required` / `optional` stay targeted hard errors; lowered-schema validation stays on the current path | output-schema, route-output, final-output, emit-docs, and diagnostics tests; `tests/test_output_schema_validation.py`; `tests/test_route_output_semantics.py`; `examples/79`; `104`; `105`; `106`; `121` |
| Live docs and release truth | `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/AUTHORING_PATTERNS.md`, `docs/REVIEW_SPEC.md`, `docs/COMPILER_ERRORS.md`, `docs/VERSIONING.md`, `CHANGELOG.md`, `examples/README.md` | public teaching and release guidance | Live docs already teach the `nullable` baseline, but they do not yet teach the new sugar wave | Update the live authoring story in the same change | Prevent stale public truth and keep versioning honest | one coherent public story for the six in-scope wins | docs emit and example verification; release-truth review |
| Syntax support | `editors/vscode/` | TextMate grammar and packaged syntax assets | Editor support will drift if grammar changes land without sync | Update syntax support if grammar keywords or forms change | Public syntax support is part of the shipped authoring surface | matching syntax highlight and parsing hints | `cd editors/vscode && make` if touched |

## 6.2 Migration notes

* Canonical owner path / shared code path:
  - imports: `doctrine/parser.py` -> `doctrine/_compiler/session.py` -> `doctrine/_compiler/indexing.py` -> `doctrine/_compiler/resolve/refs.py` -> `doctrine/_compiler/reference_diagnostics.py`
  - grouped inherit: existing `InheritItem` plus the current family-specific inherited resolvers
  - review bindings: `doctrine/_parser/reviews.py` / `doctrine/_parser/agents.py` -> `doctrine/_compiler/compile/review_contract.py`
  - IO wrappers: `doctrine/_parser/io.py` -> `doctrine/_compiler/validate/contracts.py` -> `doctrine/_compiler/resolve/io_contracts.py` -> `doctrine/_compiler/resolve/outputs.py` -> `doctrine/emit_docs.py`
  - `self:`: `doctrine/parser.py` -> `doctrine/_compiler/resolve/addressables.py`
  - nullability: `doctrine/_parser/io.py` -> `doctrine/_compiler/resolve/output_schemas.py` -> `doctrine/_compiler/output_schema_validation.py`
* Deprecated APIs (if any):
  - `output schema` `required` and `optional` stay retired authored words on this surface only
* Delete list (what must be removed; include superseded shims/parallel paths if any):
  - any stray `optional` / `required` teaching on live output-schema docs
    outside intentional invalid-example proof
  - any stale example refs, docs, or checked-in artifacts that still point at
    retired output-schema nullability words as live authoring
  - any temporary example or doc wording that suggests a second alias, binding, or path-root system
* Adjacent surfaces tied to the same contract family:
  - `examples/03`, `24`, `28`, `79`, `85`, `86`, `90`, `104`, `105`, `106`, `107`, `108`, `109`, `117`, and `121`
  - `tests/test_import_loading.py`
  - `tests/test_compiler_boundary.py`
  - `tests/test_emit_flow.py`
  - `tests/test_review_imported_outputs.py`
  - `tests/test_output_inheritance.py`
  - `tests/test_output_schema_surface.py`
  - `tests/test_output_schema_lowering.py`
  - `tests/test_output_schema_validation.py`
  - `tests/test_final_output.py`
  - `tests/test_emit_docs.py`
  - `tests/test_route_output_semantics.py`
  - `tests/test_validate_output_schema.py`
  - `tests/test_prove_output_schema_openai.py`
  - `tests/test_output_rendering.py`
  - `editors/vscode/` if grammar changes affect public syntax support
* Compatibility posture / cutover plan:
  - keep the current clean authored-language cutover for output-schema
    nullability wording
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
  - `tests/test_review_imported_outputs.py`
  - `tests/test_output_schema_validation.py`
  - `tests/test_route_output_semantics.py`
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

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 - Lock the `nullable` baseline and remove any leftover drift

Status

- Partially landed in the current repo. Keep this as the first ship gate.

Goal

- Make `output schema` tell one honest nullability story before any new sugar
  stacks on top of it.

Work

- Treat `nullable` as current public truth, close any leftover stale
  references, and keep the emitted wire contract unchanged.

Checklist (must all be done)

- Audit the remaining live `output schema` prompts, manifests, expected refs,
  docs, and release truth for any stale `required` / `optional` teaching
  outside intentional invalid-example proof.
- Keep plain fields and route fields aligned on the same `nullable` story.
- Keep `examples/79`, `104`, `105`, `106`, and `121` as the main authored
  nullability proof surfaces, and keep the broader `85` / `90` final-output
  route proof green where touched.
- Keep `E236` and `E237` sharp and upgrade-oriented for retired
  `required` and `optional`.
- Keep `doctrine/_compiler/output_schema_validation.py` and
  `doctrine/_compiler/output_schema_diagnostics.py` aligned with the lowered
  schema and example-validation flow.
- Refresh manifest-backed proof and checked-in refs only for touched
  nullability surfaces.
- Re-audit `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/COMPILER_ERRORS.md`, `docs/VERSIONING.md`, and `CHANGELOG.md`, and
  patch only the surfaces that still drift.

Verification (required proof)

- Run:
  - `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_route_output_semantics tests.test_final_output tests.test_emit_docs tests.test_validate_output_schema tests.test_prove_output_schema_openai`
  - `make verify-diagnostics`
  - `make verify-examples`

Docs/comments (propagation; only if needed)

- High-leverage comments only if a nullable-only boundary would otherwise be
  easy to misunderstand in parser or resolver code.

Exit criteria (all required)

- No live teaching surface describes `optional` or `required` as a live
  `output schema` field word outside intentional invalid-example proof.
- The live `121` example continues to teach `nullable` on the route field.
- `E236` and `E237` still prove the intended upgrade path.
- Output-schema and final-output proof pass with unchanged emitted wire shape.
- The dedicated output-schema validator path still matches the lowered-schema
  and example-validation contract.

Rollback

- Revert the authored-language nullability cut and the example-path cleanup as
  one unit.

## Phase 2 - Add alias-aware imports on the existing import and ref path

Status

- Planned.

Goal

- Remove long repeated module prefixes without introducing a second namespace
  system.

Work

- Extend the existing import, indexing, and named-ref path so module aliases
  and imported symbols resolve through one compiler-owned scope.

Checklist (must all be done)

- Add module-alias and symbol-import grammar forms while keeping wildcard
  imports out.
- Enrich `ImportDecl` and parser lowering to carry the chosen alias-aware
  import shape without changing `NameRef`.
- Teach `doctrine/_compiler/indexing.py` and
  `doctrine/_compiler/resolve/refs.py` one local import-scope story for module
  aliases and imported symbols.
- Add fail-loud handling for duplicate aliases, duplicate imported symbols,
  and ambiguous imported ownership.
- Preserve current absolute-import, relative-import, and imported runtime
  package behavior.
- Preserve imported review/output behavior across module boundaries.
- Update `examples/03_imports` and its manifest-backed refs to teach the new
  forms. Keep `examples/86_imported_review_comment_local_routes` and
  `examples/109_imported_review_handoff_output_inheritance` green as adjacent
  imported-ref proof.
- Add targeted parser, import-loading, compiler-boundary, emit-flow, and
  imported-review/output proof for the new import path.

Verification (required proof)

- Run:
  - `uv run --locked python -m unittest tests.test_import_loading tests.test_compiler_boundary tests.test_emit_flow tests.test_review_imported_outputs`
  - focused parser and resolve tests for alias-aware imports
  - `make verify-examples`

Docs/comments (propagation; only if needed)

- Add one short ownership comment near alias-scope normalization only if the
  new import scope would otherwise be easy to misread.
- Live teaching updates for new import forms are completed in Phase 7.

Exit criteria (all required)

- Module aliases and imported symbols resolve through the existing import and
  named-ref path, not a sidecar resolver.
- Imported runtime-package behavior still passes existing proof.
- Imported review/output behavior still passes existing proof.
- `examples/03_imports` teaches the new public forms.
- No route-only or review-only alias surface is introduced.

Rollback

- Remove alias grammar, import-scope state, and new tests together.

## Phase 3 - Add grouped explicit `inherit` across the real inherited families

Status

- Planned.

Goal

- Cut repeated inheritance bookkeeping while keeping the current fail-loud
  accounting model unchanged.

Work

- Add grouped authored `inherit` forms that lower to the same `InheritItem`
  stream the current inherited-family resolvers already consume.

Checklist (must all be done)

- Add grouped explicit `inherit { ... }` grammar on every inherited keyed-item
  family already named in scope:
  agent authored slots, workflow items, workflow law sections, skills,
  inputs, outputs, analyses, schemas, documents, reviews, output shapes, and
  output schemas.
- Expand grouped authored forms into repeated `InheritItem`s in the relevant
  parser mixins instead of changing resolver semantics.
- Preserve the current fail-loud behavior for missing inherited entries,
  undefined inherited keys, wrong inherited shapes, and inherited-parent
  requirements across the affected families.
- Add targeted parser and resolver proof across the inherited families, not
  only output inheritance.
- Update `examples/24_io_block_inheritance`,
  `examples/107_output_inheritance_basic`, and
  `examples/108_output_inheritance_attachments` to teach the grouped form
  where it improves the example.

Verification (required proof)

- Run:
  - `uv run --locked python -m unittest tests.test_output_inheritance`
  - focused parser and resolver tests for grouped `inherit` across the other
    affected families
  - `make verify-examples`

Docs/comments (propagation; only if needed)

- Add one short comment only where grouped authored forms lower into repeated
  `InheritItem`s and the ownership split would otherwise be easy to miss.
- Live teaching updates are completed in Phase 7.

Exit criteria (all required)

- Grouped `inherit` works across the full intended family, not just outputs.
- Resolver semantics are unchanged apart from clearer syntax coverage.
- No hidden merge semantics or `inherit *` path exists.

Rollback

- Remove grouped grammar and parser expansion together and keep singular
  explicit forms only.

## Phase 4 - Add identity shorthand on the two review-binding surfaces

Status

- Planned.

Goal

- Remove pure review-binding ceremony while preserving one semantic-binding
  model.

Work

- Add bare semantic-name shorthand to the existing `review.fields`,
  `review override fields`, and `final_output.review_fields` surfaces and keep
  all non-identity binds explicit.

Checklist (must all be done)

- Extend the review and final-output parser surfaces so bare semantic names
  lower to ordinary `ReviewFieldBinding` entries.
- Keep explicit `semantic: path` bindings for non-identity cases.
- Keep explicit identity bindings like `verdict: verdict` legal on
  `review.fields`, `review override fields`, and `final_output.review_fields`.
- Preserve existing review completeness checks and split-final-response
  validation.
- Update the real review-driven example family that teaches these bindings:
  `85`, `86`, `90`, `104`, `105`, and `106`.
- Add targeted review, final-output, imported-review/output, and
  emitted-contract proof for the new shorthand.

Verification (required proof)

- Run:
  - `uv run --locked python -m unittest tests.test_final_output tests.test_emit_docs tests.test_review_imported_outputs`
  - focused review-binding parser and compile tests
  - `make verify-examples`

Docs/comments (propagation; only if needed)

- Live teaching updates are completed in Phase 7.

Exit criteria (all required)

- Both review-binding owners accept the same identity shorthand.
- All bindings still lower to one `ReviewFieldBinding` story.
- Existing explicit identity bindings still parse and compile unchanged.
- No output-side semantic tagging or second binding system is introduced.

Rollback

- Remove shorthand parsing and keep explicit bindings only.

## Phase 5 - Add first-class IO wrapper shorthand on the current IO owner path

Status

- Planned.

Goal

- Make keyed `inputs` and `outputs` wrappers concise without creating a third
  IO lowering path.

Work

- Add one-line keyed wrapper refs on first-class IO wrappers and extend the
  current IO owner split instead of replacing it.

Checklist (must all be done)

- Add `key: NameRef` and `override key: NameRef` shorthand on `inputs` and
  `outputs` keyed wrappers only.
- Keep `input source` and `output target` out of scope in this wave.
- Preserve the existing omitted-title rule: only one lowerable direct
  declaration may reuse the child title.
- Reuse the current owner split:
  `ValidateContractsMixin` for contract summary,
  `ResolveIoContractsMixin._resolve_contract_bucket_items()` for bucket
  lowering, and `ResolveOutputsMixin._resolve_io_body()` /
  `_resolve_io_section_item()` / `_lower_omitted_io_section()` for inherited
  IO bodies and omitted-title lowering.
- Do not add a third IO helper or duplicate lowering path for this feature.
- Add fail-loud handling for malformed shorthand and unsupported shapes.
- Update `examples/24_io_block_inheritance` and
  `examples/117_io_omitted_wrapper_titles`.
- Add targeted parser, resolve, emitted-contract, and output-rendering proof
  for the new IO path.

Verification (required proof)

- Run:
  - focused parser and resolve tests for IO shorthand
  - `uv run --locked python -m unittest tests.test_output_rendering tests.test_emit_docs`
  - `make verify-examples`

Docs/comments (propagation; only if needed)

- Add one short ownership comment only if the current IO owner split
  would otherwise be easy to misread.
- Live teaching updates are completed in Phase 7.

Exit criteria (all required)

- One-line keyed wrappers work on both base and override entries.
- The current IO owner split stays coherent and remains the only lowering path
  for this surface.
- `final_output.contract.json.io` stays unchanged apart from the shorter
  authoring surface that feeds it.
- No broad title-defaulting expansion leaks outside the `inputs` / `outputs`
  wrapper family.

Rollback

- Remove IO shorthand and any related owner-path edits together.

## Phase 6 - Add `self:` shorthand across the existing `PATH_REF` family

Status

- Planned.

Goal

- Reduce repeated declaration roots on addressable surfaces without creating a
  new path namespace.

Work

- Add `self:` as a pure shorthand over the existing addressable resolution
  path and keep `law_path` explicit and separate.

Checklist (must all be done)

- Add `self:` support only on surfaces that already accept `PATH_REF`.
- Keep `law_path` and any non-`PATH_REF` surfaces unchanged.
- Bind `self:` to the current owning declaration root before ordinary path
  descent and display.
- Add fail-loud handling when `self:` appears where no declaration-root
  addressable context exists.
- Update `examples/28_addressable_workflow_paths` to teach the shorthand on
  the existing self-owned pressure case.
- Add targeted parser, addressable-resolution, and route/review path-read
  proof where the shorthand changes user-facing behavior.

Verification (required proof)

- Run:
  - focused `PATH_REF` parser and resolver tests
  - `uv run --locked python -m unittest tests.test_route_output_semantics`
  - `make verify-examples`
  - `make verify-diagnostics`

Docs/comments (propagation; only if needed)

- Add one short comment only if a `self:` sentinel or rebinding step would
  otherwise be easy to misunderstand.
- Live teaching updates are completed in Phase 7.

Exit criteria (all required)

- `self:` behaves like a pure shorthand over existing addressable truth.
- No rooted-path registry, route-owner alias layer, or second addressable
  resolver is introduced.
- The existing `28` example becomes the canonical teaching example for this
  surface.

Rollback

- Remove `self:` support and keep explicit roots only.

## Phase 7 - Align public truth, syntax support, and full-wave proof

Status

- Planned.

Goal

- Finish the wave as one coherent public language story with aligned docs,
  syntax support, examples, release truth, and proof.

Work

- Sweep the touched public surfaces after the feature work lands so no stale
  teaching track, syntax support, or release note contradicts the shipped
  language.

Checklist (must all be done)

- Update the live docs that teach the touched surfaces:
  `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/AUTHORING_PATTERNS.md`, `docs/REVIEW_SPEC.md`,
  `docs/COMPILER_ERRORS.md`, `docs/VERSIONING.md`, `CHANGELOG.md`,
  `docs/README.md`, and `examples/README.md`.
- Ensure the touched example families teach the preferred syntax and do not
  leave a second parallel tutorial track behind.
- Update `editors/vscode/` syntax support to match the final shipped grammar
  and run its build.
- Refresh checked-in refs and manifests for every touched example family.
- Run the full targeted unit suite named in Section 8.1.
- Run `uv sync` and `npm ci` before the final verification sweep.
- Run `make verify-diagnostics` and `make verify-examples` as the final public
  proof gates.

Verification (required proof)

- Run:
  - `uv sync`
  - `npm ci`
  - `uv run --locked python -m unittest tests.test_import_loading tests.test_compiler_boundary tests.test_emit_flow tests.test_review_imported_outputs tests.test_output_inheritance tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_validate_output_schema tests.test_prove_output_schema_openai tests.test_route_output_semantics tests.test_final_output tests.test_emit_docs tests.test_output_rendering tests.test_compile_diagnostics`
  - `make verify-diagnostics`
  - `make verify-examples`
  - `cd editors/vscode && make`

Docs/comments (propagation; only if needed)

- This phase owns the final live-doc, example-index, release-truth, and editor
  syntax propagation for the wave.

Exit criteria (all required)

- Live docs, examples, syntax support, and release truth all tell one coherent
  story for the six in-scope wins.
- No stale `optional` / `required`, no second alias story, no second
  review-binding story, and no second path-root story remain in public
  teaching surfaces.
- The full targeted proof sweep passes.

Rollback

- Revert any remaining public-surface alignment changes that cannot ship with
  the corresponding feature work.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- `tests/test_import_loading.py`
- `tests/test_compiler_boundary.py`
- `tests/test_emit_flow.py`
- `tests/test_review_imported_outputs.py`
- `tests/test_output_inheritance.py`
- `tests/test_output_schema_surface.py`
- `tests/test_output_schema_lowering.py`
- `tests/test_output_schema_validation.py`
- `tests/test_validate_output_schema.py`
- `tests/test_prove_output_schema_openai.py`
- `tests/test_route_output_semantics.py`
- `tests/test_final_output.py`
- `tests/test_emit_docs.py`
- `tests/test_output_rendering.py`
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
  - `86_imported_review_comment_local_routes`
  - `90_split_handoff_and_final_output_shared_route_semantics`
  - `104_review_final_output_output_schema_blocked_control_ready`
  - `105_review_split_final_output_output_schema_control_ready`
  - `106_review_split_final_output_output_schema_partial`
  - `107_output_inheritance_basic`
  - `108_output_inheritance_attachments`
  - `109_imported_review_handoff_output_inheritance`
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
- `uv run --locked python -m unittest tests.test_import_loading tests.test_compiler_boundary tests.test_emit_flow tests.test_review_imported_outputs tests.test_output_inheritance tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_validate_output_schema tests.test_prove_output_schema_openai tests.test_route_output_semantics tests.test_final_output tests.test_emit_docs tests.test_output_rendering tests.test_compile_diagnostics`
- `make verify-examples`
- `make verify-diagnostics`
- if `editors/vscode/` changes, run `cd editors/vscode && make`

# 9) Rollout / Ops / Telemetry

## 9.1 Compatibility posture

- `output schema` nullability cleanup is already the current authored-language
  baseline on that one surface. Keep it as a clean breaking line with no
  bridge.
- The other planned wins are additive and should preserve existing prompt
  files.
- No runtime shim or alias bridge is approved.

## 9.2 Release and docs duties

- update `docs/VERSIONING.md`
- update `CHANGELOG.md`
- record the authored-language breaking nullability cut and its upgrade path
  plainly in release truth
- keep live docs and corpus proof aligned in the same change

## 9.3 Telemetry / runtime ops

Not applicable beyond compile-time proof and emitted artifact verification.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: explorer 1, explorer 2, self-integrator
- Scope checked:
  - frontmatter and helper-block drift
  - `# TL;DR`
  - `# 0)` through `# 10)`
  - phase-exit completeness, verification burden, rollout duties, and
    canonical owner paths
- Findings summary:
  - the plan still treated `nullable` as unfinished broad cutover work even
    though live docs, release truth, and the public example ladder already
    teach it as current truth
  - the architecture map undercounted newer compiler owners:
    `CompilationSession`, shared reference diagnostics, output-schema
    diagnostics, and the dedicated output-schema validator
  - the IO shorthand plan still proposed a new helper extraction even though
    the live repo already has a real owner split across
    `validate/contracts.py`, `resolve/io_contracts.py`, and `resolve/outputs.py`
  - imported review/output proof and route-output proof were undercounted in
    the ship gate
- Integrated repairs:
  - reframed nullability as the current baseline and rewrote Phase 1 as a
    lock-and-audit gate
  - added the newer compiler owner paths and diagnostics helpers to the
    architecture and call-site audit
  - rewrote Phase 5 around the current live IO owner split instead of a new
    helper extraction
  - expanded proof surfaces to include
    `tests/test_review_imported_outputs.py`,
    `tests/test_output_schema_validation.py`,
    `tests/test_route_output_semantics.py`,
    `examples/86_imported_review_comment_local_routes`, and
    `examples/109_imported_review_handoff_output_inheritance`
- Remaining inconsistencies:
  - none
- Unresolved decisions:
  - none
- Unauthorized scope cuts:
  - none
- Decision-complete:
  - yes
- Decision: proceed to implement? yes
<!-- arch_skill:block:consistency_pass:end -->

# 10) Decision Log (append-only)

- 2026-04-16: This plan intentionally takes only the high-confidence elegance
  wave from the two audit docs.
- 2026-04-16: `output schema` nullability is treated as an accepted direction
  to finish cleanly, not as an unresolved semantics question.
- 2026-04-16: Deferred from this wave by default: compact schema heads,
  compact IO heads, rooted path literals, named ref sets, route-owner aliases,
  `final_output` projection sugar, broad title-defaulting expansion,
  `inherit *`, and any output-side semantic tagging.
- 2026-04-16: Grouped explicit `inherit` is a parser-level expansion to the
  existing `InheritItem` stream across the real inherited keyed-item families,
  not an inheritance-model redesign.
- 2026-04-16: Import aliasing must extend the existing import/index/ref path,
  and `self:` must resolve through the existing addressable path; neither
  feature gets a second resolver or sidecar registry.
- 2026-04-16: One-line keyed IO wrapper refs must stay on the current live IO
  owner split: `ValidateContractsMixin` for contract summary,
  `ResolveIoContractsMixin` for bucket lowering, and `ResolveOutputsMixin`
  for inherited IO bodies and omitted-title lowering.
- 2026-04-16: Section 7 uses seven phases so the final public-truth, syntax,
  and release-alignment sweep is a distinct ship gate rather than hidden
  cleanup inside the last feature phase.
- 2026-04-16: Re-audit against the current repo changed this plan in four
  ways: `nullable` is now treated as shipped baseline, newer diagnostics and
  validator modules are named as first-class owners, imported review/output
  proof is part of the ship gate, and the IO shorthand phase now extends the
  current live owner split instead of planning a fresh helper extraction.
