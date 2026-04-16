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
  - examples/86_imported_review_comment_local_routes/prompts/AGENTS.prompt
  - examples/90_split_handoff_and_final_output_shared_route_semantics/prompts/AGENTS.prompt
  - examples/109_imported_review_handoff_output_inheritance/prompts/AGENTS.prompt
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

Doctrine ships one fully additive authoring wave that removes the biggest
authoring repetition without redesigning the language, breaking existing
prompt files, or adding sidecar truth surfaces.

## Problem

Today the language makes authors repeat the same meaning through long module
prefixes, repeated `inherit` and `override` lines, repeated review-field
identity maps, verbose first-class IO wrappers, and repeated addressable
roots. The `output schema` `nullable` baseline already shipped; this plan
treats that baseline as a locked invariant, not a wave member, and builds six
additive authoring wins on top of it.

## Approach

Implement only the parser-level and fail-loud wins that lower to existing
Doctrine models:

1. add import aliases and symbol imports
2. add grouped explicit `inherit { ... }` across the current inherited keyed-item families
3. add identity-binding sugar for `review.fields`, `review override fields`,
   and `final_output.review_fields`
4. add one-line first-class IO wrapper refs for `inputs` and `outputs`
5. add `self:` shorthand for addressable refs by extending `AddressableRef`
6. keep docs, syntax support, examples, and diagnostics aligned per phase

Everything else that adds a second naming system, implicit merge, broad title
rules, or macro-like indirection stays out of this plan.

## Plan

1. Add import aliasing across the full `name_ref` family.
2. Add grouped explicit `inherit` across the inherited keyed-item families.
3. Add review-binding shorthand on the three existing semantic-binding
   surfaces.
4. Add first-class IO wrapper shorthand on `inputs` and `outputs`.
5. Add `self:` across the existing `PATH_REF` family as an `AddressableRef`
   extension.
6. Finalize release truth, changelog, and full-wave proof.

Every feature phase updates the grammar, parser, resolver, examples, tests,
live docs, compiler errors, and editor syntax support for the surface it
touches. Phase 6 owns only the wave-level release truth, changelog, and
full-wave proof gate.

## Non-negotiables

- No dual sources of truth.
- No hidden merge by omission.
- No route-only namespace shortcut surface if import aliasing already solves
  the problem.
- No broad title-defaulting sweep.
- No `inherit *` and no wildcard imports.
- No wire-shape change for the current `OpenAIStructuredOutput` profile.
- No second addressable-ref carrier — `self:` extends `AddressableRef`, not
  a sentinel value outside the carrier.
- The shipped `output schema` `nullable` baseline stays green through every
  phase.
- Every authoring change ships with example, test, live-doc, editor-syntax,
  and diagnostics truth in the same phase.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-16
Verdict (code): NOT COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- Phase 2 is still false-complete on the current tree. Fresh audit reran
  `make verify-diagnostics` and `make verify-examples`; diagnostics passed,
  but the corpus still fails on route/readback render and build contracts
  across `30`, `32`, `70`, `72`, `87`, `89`, `91`, `94`, `111`, and `119`.
- The real remaining ordered frontier is still Phase 3 through Phase 7 under
  the repaired plan. Grouped explicit `inherit`, review-binding shorthand, IO
  wrapper shorthand, `self:`, named diagnostics `E309` / `E311` / `E312`
  with `E310` reserved, and the wave-level release truth are not shipped on
  the current tree.

## Reopened phases (false-complete fixes)
- Phase 2 (Add alias-aware imports on the existing import and ref path) — reopened because:
  - `make verify-examples` is red on the current tree, which fails the phase
    verification list
  - the phase section still overstates proof closure after that gate failed

## Missing items (code gaps; evidence-anchored; no tables)
- Phase 2 proof closure
  - Evidence anchors:
    - `doctrine/_compiler/compile/workflows.py:209`
    - `doctrine/_compiler/display.py:669`
    - `doctrine/_compiler/compile/records.py:66`
    - `doctrine/_compiler/compile/records.py:195`
    - `doctrine/_compiler/compile/records.py:227`
    - `examples/30_law_route_only_turns/cases.toml:18`
    - `examples/32_modes_and_match/cases.toml:18`
    - `examples/70_route_only_declaration/cases.toml:17`
    - `examples/72_schema_group_invalidation/cases.toml:15`
    - `examples/87_workflow_route_output_binding/cases.toml:97`
    - `examples/91_handoff_routing_route_output_binding/cases.toml:60`
    - `examples/94_route_choice_guard_narrowing/cases.toml:29`
    - `examples/111_inherited_output_route_semantics/cases.toml:17`
    - `examples/119_route_only_final_output_contract/build_ref/route_only_final_output_contract_demo/AGENTS.md:7`
  - Plan expects:
    - Phase 2 stays complete only if its full verification list passes,
      including `make verify-examples`, while preserving the shipped
      import-adjacent route and readback contracts.
  - Code reality:
    - fresh audit reran `make verify-diagnostics`; it passed.
    - fresh audit reran `make verify-examples`, and the current tree still
      drifts on route and readback examples. The compiler now emits
      `This pass runs only when ...` and section-style guarded output/readback
      blocks where the checked-in corpus still expects `Use this pass only
      when ...` and inline guarded bullets.
  - Fix:
    - restore the checked-in route and readback rendering contract or land a
      deliberate plan-backed contract migration, then rerun
      `make verify-examples` until it passes.
- Remaining approved frontier after Phase 2
  - Evidence anchors:
    - `doctrine/grammars/doctrine.lark:165`
    - `doctrine/grammars/doctrine.lark:203`
    - `doctrine/grammars/doctrine.lark:204`
    - `doctrine/grammars/doctrine.lark:643`
    - `doctrine/grammars/doctrine.lark:645`
    - `doctrine/grammars/doctrine.lark:957`
    - `doctrine/_model/core.py:101`
    - `doctrine/parser.py:159`
    - `docs/COMPILER_ERRORS.md:139`
    - `CHANGELOG.md:1`
    - `docs/VERSIONING.md:1`
  - Plan expects:
    - after Phase 2, the repaired ordered frontier still owes Phase 3 grouped
      explicit `inherit`, Phase 4 review-binding shorthand, Phase 5 IO
      wrapper shorthand, Phase 6 `self:`, the matching named diagnostics
      band with `E310` reserved, and Phase 7 release truth plus full-wave
      proof.
  - Code reality:
    - the current tree still shows only singular `inherit`, explicit
      `semantic: field_path` review bindings, multiline IO wrapper sections,
      explicit-root `PATH_REF`, an `AddressableRef` that still requires an
      explicit `root: NameRef`, and a public error catalog that stops at
      `E308`. Inference from current `CHANGELOG.md` and `docs/VERSIONING.md`:
      the wave-level release truth is not recorded yet either.
  - Fix:
    - implement and prove the remaining ordered frontier from Phase 3 through
      Phase 7 instead of treating the import phase as the whole wave.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:phase3_plan_repair:start -->
# Phase 3 Plan Repair (authoritative)
Date: 2026-04-16
Status: APPLIED

Supersedes any earlier mention in this doc that Phase 3 will ship grouped
bare-ref `override { ... }` across the full inherited family.

## Why the old Phase 3 shape was not executable
- Grouped explicit `inherit { ... }` can lower cleanly into repeated
  `InheritItem`s before resolve.
- Grouped bare-ref `override { ... }` cannot do the same on the current tree.
  The shipped override carriers for analysis, document, review, schema,
  workflow, skills, IO, output, and output-schema bodies all require an
  explicit body, value, kind, or target. Landing grouped bare-ref override
  across those families would require new resolver-side parent-kind lookup or
  a new override-preserve semantic owner, which breaks the approved
  parser-sugar-only constraint for this phase.
- Evidence anchors:
  - `doctrine/_model/analysis.py`
  - `doctrine/_model/readable.py`
  - `doctrine/_model/review.py`
  - `doctrine/_model/schema.py`
  - `doctrine/_model/workflow.py`
  - `doctrine/_model/io.py`
  - `doctrine/_compiler/resolve/analysis.py`
  - `doctrine/_compiler/resolve/documents.py`
  - `doctrine/_compiler/resolve/reviews.py`
  - `doctrine/_compiler/resolve/output_schemas.py`
  - `doctrine/_compiler/resolve/outputs.py`

## Repair applied
- Phase 3 now ships grouped explicit `inherit { ... }` only.
- Grouped bare-ref `override` is deferred out of this wave. It may return only
  in a new approved plan that explicitly allows the needed resolver semantics
  or a new authored owner.
- `E309` stays assigned to malformed grouped `inherit`.
- `E310` stays reserved for the deferred grouped-override investigation so the
  later code bands in this plan do not shift again.
- This repair is folded through the rest of the approved plan surface:
  North Star, scope, acceptance, target architecture, call-site audit,
  migration notes, pattern consolidation, phased rollout, consistency pass,
  and decision log now all carry the same deferred grouped-override story.
<!-- arch_skill:block:phase3_plan_repair:end -->

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

If Doctrine implements this fully additive authoring wave and nothing more,
authors will be able to express the same shipped contracts with materially
less repetition, while the compiler still owns one truth for refs,
inheritance, review bindings, IO wrappers, and route semantics, and no
existing prompt file needs to change to keep compiling.

## 0.2 In scope

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
  - Mixing bare semantic names and explicit `semantic: path` entries in the
    same block is legal.
- Add one-line first-class IO wrapper refs on:
  - `inputs`
  - `outputs`
  - base entries and override entries
- Add `self:` shorthand across the existing `PATH_REF` family by extending
  `AddressableRef` with a self-rooted variant (no sentinel value, no second
  carrier):
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
- Add explicit fail-loud diagnostics with named codes where the new surface
  needs one sharp story (provisional codes; finalize in each phase):
  - `E306` duplicate module alias in one module
  - `E307` duplicate imported symbol in one module
  - `E308` ambiguous imported symbol ownership at use site
  - `E309` malformed grouped `inherit` (unknown key, duplicate key, empty
    group, wrong shape)
  - `E310` reserved for the deferred grouped-override investigation so later
    code bands stay stable
  - `E311` malformed IO wrapper shorthand — teach the upgrade path to a
    multi-line wrapper in the error text
  - `E312` malformed `self:` usage where no declaration-root addressable
    context exists
  - `E236` / `E237` stay as the retired `output schema` nullability errors

## 0.3 Out of scope

- `inherit *` or any keep-the-rest merge-by-omission story
- grouped bare-ref `override { ... }` across the inherited keyed-item family
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

- The shipped `output schema` `nullable` baseline stays green through every
  phase with no authored-language change and no emitted wire-shape change.
- Import aliasing works across the same `name_ref` family Doctrine already
  uses, not only on one favored surface.
- Grouped explicit `inherit` lands across the inherited keyed-item families
  that currently repeat singular `inherit` lines.
- Review-field shorthand works on all three review binding surfaces, keeps
  one binding truth after lowering, and allows mixing bare semantic names
  with explicit `semantic: path` entries in the same block.
- First-class IO wrappers can express one-ref buckets in one line on `inputs`
  and `outputs`, with a fail-loud `E311` error that teaches the multi-line
  upgrade path when the ref resolves to more than one child.
- `self:` works anywhere Doctrine already accepts an `AddressableRef` and is
  carried by one extended `AddressableRef` variant, not a sentinel value.
- Every feature phase ships its own grammar, parser, resolver, example,
  test, live-doc, editor-syntax, and diagnostics updates together.
- The shipped examples teach the new preferred syntax on the existing
  example families instead of adding a second parallel tutorial track.
- Unit tests, diagnostics proof, and manifest-backed examples cover the new
  syntax and the fail-loud boundaries, including the named diagnostic codes
  above.
- Live docs, release truth, changelog, and editor syntax support match the
  shipped authoring surface at the end of each phase, not only at wave end.

## 0.5 Key invariants (fix immediately if violated)

- No dual sources of truth.
- One ref-resolution story.
- One inheritance-accounting story, and grouped `inherit { ... }` keys resolve
  only against inherited-parent names — never against the import scope.
- One review semantic-binding story.
- One IO wrapper story per family.
- One addressable-ref carrier: `self:` is a variant of `AddressableRef`, not
  a sentinel value or a second carrier.
- The shipped `output schema` `nullable` baseline is a locked invariant for
  this wave. Legacy `required` and `optional` stay targeted hard errors on
  that surface, emitted wire shape stays unchanged, and each phase must keep
  that baseline green.
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
4. Keep the shipped `output schema` `nullable` baseline green through every
   phase (baseline guard, not wave work).
5. Update the example corpus, diagnostics, live docs, and editor syntax
   support in the same phase as the grammar change — not at wave end.

## 1.2 Constraints

- `output schema` nullability already shipped and is treated as a locked
  regression guard for this wave, not as greenfield feature work.
- The example corpus is part of shipped proof, not just illustration.
- Every win in this wave is additive. No authored-language breaking change
  is planned and no existing prompt file should need to change.
- The authoring wave must not turn into a second naming or projection system.

## 1.3 Architectural principles (rules we will enforce)

- Sugar follows shared carrier shapes, not one visible noun.
- Keep one lowering story per concept.
- Prefer explicit deletes and hard errors over shims or aliases that keep old
  words alive.
- Any shorthand must lower to existing compiler-owned truth.
- If a feature needs a second owner path, defer it.

## 1.4 Known tradeoffs (explicit)

- Every win in this wave is additive and lowers to existing compiler-owned
  truth, so there is no breaking cut to sequence against. The shipped
  `nullable` baseline is a regression guard, not a wave member.
- Compact schema heads are a plausible wave-2 candidate (the shipped
  `nullable` flag already proves the carrier is sugar-friendly) but stay
  deferred here to keep this wave focused. Recorded in §10.
- Rooted paths and macro-like ref sets stay deferred as out-of-scope
  naming systems, not sequencing defers.
- Grouped `inherit` lands broad across the full inherited keyed-item family.
  Grouped bare-ref `override` is deferred out of this wave because the
  current override carriers would need new resolver-side parent-kind lookup
  or a new authored owner. Singular and body-carrying override forms stay
  as-is.
- Review identity shorthand allows bare semantic names and explicit
  `semantic: path` entries to mix in the same block. Forcing authors to pick
  one or the other would turn every non-identity bind into a ceremony tax.

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

- None at the planning-scope level. Locked decisions for this wave:
  - compatibility posture is fully additive across the remaining wave surface
  - `self:` lowers as an extended `AddressableRef` variant, not a sentinel
    value outside the carrier
  - grouped bare-ref `override` is deferred out of this wave; singular and
    body-carrying override forms stay on the current paths
  - review identity shorthand permits mixing bare semantic names with
    explicit `semantic: path` entries in the same block
  - grouped `inherit { ... }` keys resolve only against inherited-parent
    names, never against the import scope
  - named diagnostic codes keep the `E306`..`E312` band, with `E310`
    reserved and the shipped phase-owned codes finalized in each feature
    phase
- Later stages should treat these as locked unless new repo evidence reveals
  a direct contradiction.
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
  - extend `AddressableRef` in `doctrine/_model/core.py` with a self-rooted
    variant (for example a nullable declaration root with a `self` flag).
    This is the one carrier for `self:`. No authored sentinel value, no
    second `AddressableRef`-like type, and no resolver-side string hack.
  - the self-rooted variant is resolved against the current owning
    declaration before ordinary path descent, display, and validation
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
  - grouped bare-ref `override` is deferred out of this wave; singular and
    body-carrying override forms stay on the existing owner paths
  - grouped `inherit` keys resolve only against inherited-parent names and
    never participate in import-scope lookup
  - no `inherit *`
  - no merge-by-omission
- One review-binding story:
  - `review.fields`, `review override fields`, and
    `final_output.review_fields` all accept bare semantic names for identity
    cases
  - mixing bare semantic names with explicit `semantic: path` entries in the
    same block is legal
  - all three surfaces still lower to the same `ReviewFieldsConfig` and
    `ReviewFieldBinding` carriers
- One IO-wrapper story:
  - `inputs` and `outputs` keyed wrappers accept `key: NameRef` when the
    referenced declaration lowers to exactly one child entry through the
    existing omitted-title rule
  - base and override wrappers move together
  - the current `ValidateContractsMixin` -> `ResolveIoContractsMixin` ->
    `ResolveOutputsMixin` owner split stays the only lowering path
  - fail-loud `E311` fires when the shorthand ref does not lower to exactly
    one child, and the error text teaches the author the multi-line wrapper
    upgrade path
  - `input source` and `output target` stay out of this wave
- One addressable story:
  - `self:` is a self-rooted variant of `AddressableRef`, valid only on
    surfaces that already accept `PATH_REF`
  - `law_path` stays explicit and separate
  - no rooted-path registry, no route-owner alias layer, and no sentinel
    value outside the `AddressableRef` carrier
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
- No emitted contract drift from any of the additive wins; emitted wire
  shape for `OpenAIStructuredOutput` stays byte-equal on rewritten manifests.
- Sharp fail-loud diagnostics are part of the public design, with named
  provisional codes:
  - legacy output-schema words stay targeted hard errors (`E236`, `E237`)
  - alias and imported-symbol collisions fail loud (`E306`, `E307`)
  - ambiguous imported ownership at the use site fails loud (`E308`)
  - malformed grouped `inherit` (`E309`) fails loud at the parser or compile
    boundary
  - `E310` stays reserved for the deferred grouped-override investigation
  - malformed IO wrapper shorthand fails loud (`E311`) and the message
    teaches the multi-line wrapper upgrade path
  - malformed `self:` usage fails loud (`E312`) where no declaration-root
    addressable context exists

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
| Import indexing and resolution | `doctrine/_compiler/session.py`, `doctrine/_compiler/indexing.py`, `doctrine/_compiler/resolve/refs.py`, `doctrine/_compiler/reference_diagnostics.py` | session-scoped module graph, `_resolve_import_path`, `IndexedUnit.imported_units`, named-ref lookup | Loads imported modules through the current session-scoped graph, but no local alias scope or imported-symbol scope exists yet | Add one local import-scope map and teach named-ref resolution to use it; emit `E306` duplicate alias, `E307` duplicate imported symbol, `E308` ambiguous imported ownership | Avoid a second alias resolver and keep fail-loud ambiguity in the compiler | module aliases and imported symbols resolve through the existing lookup path | `tests/test_import_loading.py`; `tests/test_compiler_boundary.py`; `tests/test_emit_flow.py`; `tests/test_review_imported_outputs.py`; `examples/03_imports`; `examples/86_imported_review_comment_local_routes`; `examples/109_imported_review_handoff_output_inheritance` |
| Grouped inherit grammar | `doctrine/grammars/doctrine.lark` | `agent_slot_inherit`, `workflow_inherit`, `law_inherit`, `analysis_inherit`, `schema_inherit`, `document_inherit`, `review_inherit`, `skills_inherit`, `io_inherit`, `output_inherit`, `output_schema_inherit` | Every inherited family spells singular `inherit key` lines only | Add grouped explicit `inherit { ... }` using each family's existing key token | The repeated accounting rule is shared across the inherited carriers | grouped explicit `inherit`; no `inherit *` | new parser coverage; inherited-family tests |
| Grouped inherit parse lowering | `doctrine/_parser/workflows.py`, `doctrine/_parser/analysis_decisions.py`, `doctrine/_parser/transformer.py`, `doctrine/_parser/reviews.py`, `doctrine/_parser/skills.py`, `doctrine/_parser/io.py` | family-specific `*_inherit` methods | Lower only one `InheritItem` at a time | Expand grouped authored forms into repeated `InheritItem`s before resolve; emit `E309` for malformed groups | Keep resolver semantics unchanged and fail loud | parser-level sugar only; no resolver-side merge semantics; grouped keys resolve only against inherited-parent names | inherited-family tests; `examples/24`; `examples/107`; `examples/108` |
| Inherited family resolvers | `doctrine/_compiler/resolve/agent_slots.py`, `doctrine/_compiler/resolve/workflows.py`, `doctrine/_compiler/resolve/analysis.py`, `doctrine/_compiler/resolve/documents.py`, `doctrine/_compiler/resolve/skills.py`, `doctrine/_compiler/resolve/addressable_skills.py`, `doctrine/_compiler/resolve/io_contracts.py`, `doctrine/_compiler/resolve/reviews.py`, `doctrine/_compiler/resolve/outputs.py`, `doctrine/_compiler/resolve/output_schemas.py` | missing-entry and undefined-key checks | Already enforce explicit inherited accounting with fail-loud errors | Reuse the same semantics unchanged; only sharpen diagnostics if grouped syntax needs clearer blame | This wave is sugar, not an inheritance redesign | same inherited semantics with grouped authoring | `tests/test_output_inheritance.py`; existing family tests |
| Review binding grammar and parse | `doctrine/grammars/doctrine.lark`, `doctrine/_parser/reviews.py`, `doctrine/_parser/agents.py` | `semantic_field_binding`, `fields_stmt`, `final_output_review_fields_stmt`, review override fields | Requires `semantic: field_path` even for identity cases; all three surfaces repeat the same full form | Add bare semantic-name entries that lower to the same binding tuple on all three surfaces (`review.fields`, `review override fields`, `final_output.review_fields`); allow bare and explicit entries to mix in the same block | Remove pure ceremony without adding a second binding surface; keep one identity-binding rule across all three review surfaces | all three surfaces accept bare semantic names for identity binds, explicit `semantic: path` entries stay legal, and mixing both forms in the same block is legal | review and final-output tests; `tests/test_review_imported_outputs.py`; `examples/85`; `examples/86`; `examples/90`; `examples/104`; `examples/105`; `examples/106` |
| Review compile validation | `doctrine/_compiler/compile/review_contract.py`, `doctrine/_compiler/compile/final_output.py` | final-response binding validation and payload preview wiring | Consumes explicit bindings only | Accept parser-lowered identity bindings with no semantic change | Keep one semantic-binding truth through compile and emit | no new contract fields; only shorter authoring | `tests/test_final_output.py`; `tests/test_emit_docs.py` |
| IO wrapper grammar and parse | `doctrine/grammars/doctrine.lark`, `doctrine/_parser/io.py`, `doctrine/_model/io.py` | `io_section`, `io_override_section`, `IoSection`, `OverrideIoSection` | Keyed `inputs` / `outputs` wrappers require multiline bodies, even for one child ref | Add `key: NameRef` and `override key: NameRef` sugar that lowers to one-child wrapper sections through the existing omitted-title rule; emit `E311` with the multi-line upgrade path in the message when the ref resolves to more than one child | This is the cleanest IO-side repetition cut and stays inside one family | one-line keyed IO wrapper refs on `inputs` and `outputs` only | IO parser tests; `examples/24`; `examples/117` |
| IO resolve and validation | `doctrine/_compiler/validate/contracts.py`, `doctrine/_compiler/resolve/io_contracts.py`, `doctrine/_compiler/resolve/outputs.py`, `doctrine/emit_docs.py` | `_summarize_contract_field`, `_resolve_contract_bucket_ref_entry`, `_resolve_non_inherited_io_items`, `_resolve_io_section_item`, `_lower_omitted_io_section` | The live IO path already has a real owner split: contract summary in `validate/contracts.py`, bucket lowering in `resolve/io_contracts.py`, inherited IO-body and omitted-title lowering in `resolve/outputs.py`, and public contract emission in `emit_docs.py` | Add one-line keyed-wrapper behavior by extending those existing owners and reusing the current bucket and omitted-title path; keep `final_output.contract.json.io` byte-equal on rewritten manifests | Prevent a third IO lowering path and keep the runtime `io` contract stable | same resolved IO contract and emitted runtime payload; shorter authoring only | IO resolve tests; `tests/test_output_rendering.py`; `tests/test_emit_docs.py`; `examples/24`; `examples/117`; byte-equal manifest ref proof |
| `self:` path surface | `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, `doctrine/_model/core.py` | `PATH_REF`, `path_ref`, `AddressableRef` | Every addressable path requires an explicit declaration root; `AddressableRef` always carries a declaration root | Add `self:` as an authored shorthand on existing `PATH_REF` surfaces and extend `AddressableRef` with a self-rooted variant (for example a nullable declaration root plus a `self` flag). Lower `self:` into that variant and keep the one addressable-ref carrier | Reduce repeated roots without creating a new addressable namespace or a sentinel value outside the carrier | `self:path.to.item` on existing addressable-ref surfaces only; one `AddressableRef` carrier with a self-rooted variant | addressable parser tests; `examples/28` |
| `self:` resolution and validation | `doctrine/_compiler/resolve/addressables.py`, `doctrine/_compiler/validate/addressable_children.py`, `doctrine/_compiler/validate/addressable_display.py` | `_resolve_addressable_ref_value`, `_resolve_addressable_root_decl`, child walking and display | Resolve only explicit roots today | Bind the self-rooted variant to the current owning declaration before normal path descent and display; emit `E312` where no declaration-root context exists | Keep one addressable-resolution story and one error path | same resolved addressable targets with shorter authoring | addressable tests; route and review path-read tests where affected; interpolation coverage for `self:` on `PATH_REF` surfaces |
| Output-schema baseline guard | `doctrine/grammars/doctrine.lark`, `doctrine/_parser/io.py`, `doctrine/_compiler/resolve/output_schemas.py`, `doctrine/_compiler/output_schema_validation.py`, `doctrine/_compiler/output_schema_diagnostics.py`, `doctrine/_model/io.py` | `output_schema_nullable_stmt`, `output_schema_required_stmt`, `output_schema_optional_stmt`, `OutputSchemaFlag`, `E236`, `E237`, lowered-schema validator | Already shipped: grammar, parser, resolver, live docs, examples, and diagnostics all teach `nullable`; retired words stay only as targeted hard errors | Locked regression guard; each feature phase must keep the baseline green and make no authored-language or emitted-wire-shape change to this surface | The additive wave must not reopen a settled baseline | `nullable` is the live word; `required` / `optional` stay targeted hard errors; lowered-schema validation stays on the current path | output-schema, route-output, final-output, emit-docs, and diagnostics tests must stay green through every phase |
| Live docs per phase | `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/AUTHORING_PATTERNS.md`, `docs/REVIEW_SPEC.md`, `docs/COMPILER_ERRORS.md`, `examples/README.md` | public teaching of the surface touched in each phase | Live docs teach the `nullable` baseline but not the new sugar | Each feature phase updates only the live-doc sections for the surface it ships | Prevent mid-wave drift between grammar and teaching | per-phase doc parity with shipped grammar | docs emit and example verification in each phase |
| Release truth (wave-level) | `docs/VERSIONING.md`, `CHANGELOG.md`, `docs/README.md` | versioning posture and release notes | Not yet updated for this wave | Final phase records the additive wave as one coherent release entry and confirms no breaking change | Keep versioning honest and avoid per-phase changelog churn | one additive release entry for the wave | release-truth review in the final phase |
| Editor syntax support per phase | `editors/vscode/` | TextMate grammar and packaged syntax assets | Editor support will drift if grammar changes land without sync | Each feature phase that changes grammar runs `cd editors/vscode && make` and commits the updated syntax bundle | Keep the shipped authoring experience coherent per phase | matching syntax highlight and parsing hints at every phase exit | `cd editors/vscode && make` in each feature phase |

## 6.2 Migration notes

* Canonical owner path / shared code path:
  - imports: `doctrine/parser.py` -> `doctrine/_compiler/session.py` -> `doctrine/_compiler/indexing.py` -> `doctrine/_compiler/resolve/refs.py` -> `doctrine/_compiler/reference_diagnostics.py`
  - grouped inherit: existing `InheritItem` plus the current family-specific inherited resolvers
  - review bindings: `doctrine/_parser/reviews.py` / `doctrine/_parser/agents.py` -> `doctrine/_compiler/compile/review_contract.py`
  - IO wrappers: `doctrine/_parser/io.py` -> `doctrine/_compiler/validate/contracts.py` -> `doctrine/_compiler/resolve/io_contracts.py` -> `doctrine/_compiler/resolve/outputs.py` -> `doctrine/emit_docs.py`
  - `self:`: `doctrine/parser.py` -> `doctrine/_compiler/resolve/addressables.py`
  - nullability: `doctrine/_parser/io.py` -> `doctrine/_compiler/resolve/output_schemas.py` -> `doctrine/_compiler/output_schema_validation.py`
* Deprecated APIs (if any):
  - none added by this wave. `output schema` `required` and `optional`
    remain retired authored words (baseline guard, not wave work).
* Delete list (what must be removed; include superseded shims/parallel paths if any):
  - any temporary example or doc wording that suggests a second alias,
    binding, path-root, or addressable-ref system
  - any mid-wave draft that still teaches grouped bare-ref `override` as part
    of this shipped wave
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
  - fully additive across the remaining wave surface: import aliasing,
    grouped `inherit`, review-binding shorthand, IO wrapper shorthand,
    `self:` addressable variant, and per-phase docs+syntax
  - the shipped `output schema` `nullable` baseline stays as-is
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
| Override keyed items (bare ref) | all current `*_override` grammar on the same inherited families | grouped bare-ref `override { ... }` lowering to ordinary per-family override items | Still attractive, but the shipped override carriers need broader semantic work than this wave allows | defer |
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

## Phase 1 - Baseline guard (already shipped; not a wave member)

Status

- Status: COMPLETE - regression proof repaired and green on the current tree
- The `output schema` `nullable` baseline already ships in grammar, parser,
  resolver, live docs, examples, and diagnostics. Legacy `required` /
  `optional` remain targeted hard errors via `E236` / `E237`.

Role in this wave

- This phase is a regression guard, not a feature phase. It stays in the
  plan so later phases can cite one concrete invariant to keep green, not
  to add new authoring surface.

Invariants every later phase must preserve

- No authored-language change to `output schema` nullability wording.
- No emitted wire-shape change in the current `OpenAIStructuredOutput`
  profile.
- `E236` / `E237` stay exact and upgrade-oriented.
- `doctrine/_compiler/output_schema_validation.py` and
  `doctrine/_compiler/output_schema_diagnostics.py` stay aligned with the
  lowered-schema and example-validation contract.

Regression proof every later phase must rerun

- `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_route_output_semantics tests.test_final_output tests.test_emit_docs tests.test_validate_output_schema tests.test_prove_output_schema_openai`
- `make verify-diagnostics`
- `make verify-examples`

Rollback

- Not applicable. This baseline is already shipped; wave-level rollback
  does not revert it.

## Phase 2 - Add alias-aware imports on the existing import and ref path

Status

- Status: REOPENED (audit found missing code work)

Missing (code):

- Fresh audit reran `make verify-diagnostics`; it passed.
- Fresh audit reran `make verify-examples`, and the current tree still fails on
  route/readback examples in `30`, `32`, `70`, `72`, `87`, `89`, `91`, `94`,
  `111`, and `119`.
- The current drift is not limited to one example. Workflow-law active guards
  now render `This pass runs only when ...`, and guarded output/readback items
  now expand into section-style blocks where the shipped corpus still expects
  `Use this pass only when ...` and inline guarded bullets.

Goal

- Remove long repeated module prefixes without introducing a second namespace
  system.

Work

- Extend the existing import, indexing, and named-ref path so module aliases
  and imported symbols resolve through one compiler-owned scope.

Completed work

- Added `import ... as ...`, `from ... import Name`, and
  `from ... import Name as Alias` to the grammar, parser lowering, and
  `ImportDecl` model.
- Added one import-scope story in `doctrine/_compiler/indexing.py` and the
  named-ref, addressable, law-path, output, review, and validation paths so
  module aliases and imported symbols resolve through the existing compiler
  surfaces instead of a sidecar resolver.
- Finalized the import diagnostics for this phase as `E306` duplicate module
  alias, `E307` duplicate imported symbol, and `E308` ambiguous imported
  symbol ownership.
- Updated `examples/03_imports`,
  `examples/86_imported_review_comment_local_routes`, and
  `examples/109_imported_review_handoff_output_inheritance` to teach and
  prove the new import forms.
- Updated `docs/LANGUAGE_REFERENCE.md`, `docs/AUTHORING_PATTERNS.md`,
  `docs/COMPILER_ERRORS.md`, and
  `editors/vscode/syntaxes/doctrine.tmLanguage.json`.
- Added focused proof in `tests/test_parser_source_spans.py`,
  `tests/test_import_loading.py`, `tests/test_compiler_boundary.py`,
  `tests/test_emit_flow.py`, `tests/test_review_imported_outputs.py`, and
  `tests/test_compile_diagnostics.py`.

Checklist (must all be done)

- Add module-alias and symbol-import grammar forms (`import x as y`,
  `from x import Name`, `from x import Name as Alias`) while keeping
  wildcard imports out.
- Enrich `ImportDecl` and parser lowering to carry alias-aware import data
  without changing `NameRef`.
- Teach `doctrine/_compiler/indexing.py` and
  `doctrine/_compiler/resolve/refs.py` one local import-scope story for
  module aliases and imported symbols.
- Add fail-loud diagnostics with named codes:
  `E306` duplicate module alias in one module,
  `E307` duplicate imported symbol in one module,
  `E308` ambiguous imported symbol ownership at the use site. Finalize the
  exact code numbers against `docs/COMPILER_ERRORS.md` and update that file
  in the same phase.
- Preserve current absolute-import, relative-import, and imported runtime
  package behavior.
- Preserve imported review/output behavior across module boundaries.
- Update `examples/03_imports` and its manifest-backed refs to teach the new
  forms. Keep `examples/86_imported_review_comment_local_routes` and
  `examples/109_imported_review_handoff_output_inheritance` green as adjacent
  imported-ref proof.
- Add targeted parser, import-loading, compiler-boundary, emit-flow, and
  imported-review/output proof for the new import path.
- Update the live docs that teach imports in this phase:
  `docs/LANGUAGE_REFERENCE.md`, `docs/AUTHORING_PATTERNS.md`,
  `docs/COMPILER_ERRORS.md` (for `E306`..`E308`).
- Update `editors/vscode/` TextMate grammar for the new import forms and
  run `cd editors/vscode && make`.
- Keep the Phase 1 baseline guard green by rerunning the regression proof
  listed in Phase 1.

Verification (required proof)

- Run:
  - `uv run --locked python -m unittest tests.test_import_loading tests.test_compiler_boundary tests.test_emit_flow tests.test_review_imported_outputs`
  - focused parser and resolve tests for alias-aware imports
  - `make verify-diagnostics`
  - `make verify-examples`
  - Phase 1 regression proof
  - `cd editors/vscode && make`

Docs/comments (propagation; this phase)

- Add one short ownership comment near alias-scope normalization only if the
  new import scope would otherwise be easy to misread.
- Phase 2 owns its live-doc updates for imports; there is no deferred wave
  sweep for this surface.

Proof closure

- Fresh audit reran `make verify-diagnostics`; it passed.
- Fresh audit reran `make verify-examples`, and the current tree is still red
  on route/readback examples in `30`, `32`, `70`, `72`, `87`, `89`, `91`,
  `94`, `111`, and `119`.
- Phase 2 stays reopened until the full verification list is green again on
  the current tree.

Exit criteria (all required)

- Module aliases and imported symbols resolve through the existing import
  and named-ref path, not a sidecar resolver.
- Imported runtime-package behavior still passes existing proof.
- Imported review/output behavior still passes existing proof.
- `examples/03_imports` teaches the new public forms, and checked-in refs
  are refreshed.
- `E306`, `E307`, `E308` are named in `docs/COMPILER_ERRORS.md` and exercised
  in diagnostics proof.
- Editor syntax support for the new import forms ships in
  `editors/vscode/`.
- No route-only or review-only alias surface is introduced.
- The Phase 1 regression proof still passes.

Rollback

- Remove alias grammar, import-scope state, new tests, doc updates, and
  editor syntax updates together.

## Phase 3 - Add grouped explicit `inherit`

Status

- Repaired after plan audit. Implementation not started.

Goal

- Cut repeated inheritance bookkeeping while keeping the current fail-loud
  accounting model unchanged.

Work

- Add grouped authored `inherit { ... }` forms that lower to the same
  `InheritItem` stream the current inherited-family resolvers already
  consume.

Checklist (must all be done)

- Add grouped explicit `inherit { ... }` grammar on every inherited keyed-item
  family already named in scope:
  agent authored slots, workflow items, workflow law sections, skills,
  inputs, outputs, analyses, schemas, documents, reviews, output shapes, and
  output schemas.
- Expand grouped authored forms into repeated `InheritItem`s in the relevant
  parser mixins instead of changing resolver semantics.
- Enforce that keys inside `inherit { ... }` resolve
  only against inherited-parent names, never against the import scope.
- Preserve the current fail-loud behavior for missing inherited entries,
  undefined inherited keys, wrong inherited shapes, and inherited-parent
  requirements across the affected families.
- Add fail-loud diagnostic `E309` for malformed grouped `inherit`
  (unknown key, duplicate key, empty group, wrong shape). Finalize the exact
  code number in `docs/COMPILER_ERRORS.md` in the same phase.
- Add targeted parser and resolver proof across the inherited families, not
  only output inheritance.
- Update `examples/24_io_block_inheritance`,
  `examples/107_output_inheritance_basic`, and
  `examples/108_output_inheritance_attachments` to teach grouped `inherit`
  where it improves the example.
- Update the live docs that teach inheritance in this phase:
  `docs/LANGUAGE_REFERENCE.md`, `docs/AUTHORING_PATTERNS.md`,
  `docs/COMPILER_ERRORS.md` (for `E309`).
- Update `editors/vscode/` TextMate grammar for grouped `inherit` and run
  `cd editors/vscode && make`.
- Keep the Phase 1 baseline guard green by rerunning its regression proof.

Verification (required proof)

- Run:
  - `uv run --locked python -m unittest tests.test_output_inheritance`
  - focused parser and resolver tests for grouped `inherit` across the other
    affected families
  - `make verify-diagnostics`
  - `make verify-examples`
  - Phase 1 regression proof
  - `cd editors/vscode && make`

Docs/comments (propagation; this phase)

- Add one short comment only where grouped authored forms lower into repeated
  `InheritItem`s and the ownership split would otherwise be easy to miss.
- Phase 3 owns its live-doc updates for inheritance.

Exit criteria (all required)

- Grouped `inherit` works across the full intended family, not just outputs.
- Resolver semantics are unchanged apart from clearer syntax coverage.
- No hidden merge semantics, no `inherit *`, and no import-scope lookup
  inside grouped keys.
- `E309` is named in `docs/COMPILER_ERRORS.md` and exercised in diagnostics
  proof.
- Editor syntax support for grouped `inherit` ships in `editors/vscode/`.
- The Phase 1 regression proof still passes.

Rollback

- Remove grouped-`inherit` grammar, parser expansion, doc updates, and editor
  syntax updates together. Keep singular explicit forms only.

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

- Extend the review and final-output parser surfaces on all three semantic
  binding owners (`review.fields`, `review override fields`, and
  `final_output.review_fields`) so bare semantic names lower to ordinary
  `ReviewFieldBinding` entries.
- Allow mixing bare semantic names and explicit `semantic: path` entries in
  the same block; add a dedicated parser/compile test that proves mixing
  is legal and lowers identically on all three surfaces.
- Keep explicit `semantic: path` bindings for non-identity cases.
- Keep explicit identity bindings like `verdict: verdict` legal on all three
  surfaces.
- Preserve existing review completeness checks and split-final-response
  validation. Both identity forms (bare and explicit) must satisfy the same
  completeness rules.
- Update the real review-driven example family that teaches these bindings:
  `85`, `86`, `90`, `104`, `105`, and `106`. At least one example must
  exercise mixed bare/explicit entries in the same block.
- Add targeted review, final-output, imported-review/output, and
  emitted-contract proof for the new shorthand.
- Update the live docs that teach review bindings in this phase:
  `docs/REVIEW_SPEC.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/AUTHORING_PATTERNS.md`.
- Update `editors/vscode/` TextMate grammar for the bare-name form and run
  `cd editors/vscode && make`.
- Keep the Phase 1 baseline guard green by rerunning its regression proof.

Verification (required proof)

- Run:
  - `uv run --locked python -m unittest tests.test_final_output tests.test_emit_docs tests.test_review_imported_outputs`
  - focused review-binding parser and compile tests, including the
    mixed-entry case
  - `make verify-diagnostics`
  - `make verify-examples`
  - Phase 1 regression proof
  - `cd editors/vscode && make`

Docs/comments (propagation; this phase)

- Phase 4 owns its live-doc updates for review and final-output bindings.

Exit criteria (all required)

- All three review-binding owners accept the same identity shorthand.
- Mixing bare and explicit entries in the same block is proven legal and
  lowers identically.
- All bindings still lower to one `ReviewFieldBinding` story.
- Existing explicit identity bindings still parse and compile unchanged.
- No output-side semantic tagging or second binding system is introduced.
- Editor syntax support for the shorthand ships in `editors/vscode/`.
- The Phase 1 regression proof still passes.

Rollback

- Remove shorthand parsing, example updates, doc updates, and editor syntax
  updates together. Keep explicit bindings only.

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
- Add fail-loud diagnostic `E311` when the shorthand ref does not lower to
  exactly one child (multi-child record, record with a required title
  override, or any shape that breaks the omitted-title rule). The message
  must teach the multi-line wrapper upgrade path with a concrete snippet.
  Finalize the exact code number in `docs/COMPILER_ERRORS.md` in the same
  phase.
- Before rewriting the touched examples, capture baseline
  `final_output.contract.json.io` refs. After the rewrite, assert byte-equal
  refs to prove zero emit drift.
- Update `examples/24_io_block_inheritance` and
  `examples/117_io_omitted_wrapper_titles` to teach the shorthand, and
  rewrite manifest-backed refs only if the emit is provably byte-equal.
- Add targeted parser, resolve, emitted-contract, and output-rendering proof
  for the new IO path, including an `E311` diagnostics case.
- Update the live docs that teach first-class IO in this phase:
  `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/AUTHORING_PATTERNS.md`, `docs/COMPILER_ERRORS.md` (for `E311`).
- Update `editors/vscode/` TextMate grammar for the IO shorthand and run
  `cd editors/vscode && make`.
- Keep the Phase 1 baseline guard green by rerunning its regression proof.

Verification (required proof)

- Run:
  - focused parser and resolve tests for IO shorthand
  - `uv run --locked python -m unittest tests.test_output_rendering tests.test_emit_docs`
  - `make verify-diagnostics`
  - `make verify-examples` (including byte-equal ref check on the rewritten
    `24` and `117` examples)
  - Phase 1 regression proof
  - `cd editors/vscode && make`

Docs/comments (propagation; this phase)

- Add one short ownership comment only if the current IO owner split
  would otherwise be easy to misread.
- Phase 5 owns its live-doc updates for first-class IO.

Exit criteria (all required)

- One-line keyed wrappers work on both base and override entries.
- The current IO owner split stays coherent and remains the only lowering
  path for this surface.
- `final_output.contract.json.io` is byte-equal on rewritten `24` and `117`
  manifests.
- `E311` is named in `docs/COMPILER_ERRORS.md`, fires on multi-child refs,
  and the message teaches the multi-line wrapper upgrade path.
- No broad title-defaulting expansion leaks outside the `inputs` / `outputs`
  wrapper family.
- Editor syntax support for the shorthand ships in `editors/vscode/`.
- The Phase 1 regression proof still passes.

Rollback

- Remove IO shorthand, doc updates, editor syntax updates, and any related
  owner-path edits together.

## Phase 6 - Add `self:` shorthand across the existing `PATH_REF` family

Status

- Planned.

Goal

- Reduce repeated declaration roots on addressable surfaces without creating a
  new path namespace.

Work

- Add `self:` as a pure shorthand over the existing addressable resolution
  path by extending `AddressableRef` with a self-rooted variant. Keep
  `law_path` explicit and separate.

Checklist (must all be done)

- Extend `AddressableRef` in `doctrine/_model/core.py` with a self-rooted
  variant (for example a nullable declaration root plus a `self` flag).
  Do not introduce a sentinel string, a second `AddressableRef`-like type,
  or resolver-side string detection.
- Add `self:` support only on surfaces that already accept `PATH_REF`:
  workflow section ref items, record scalar heads, output record scalar
  heads, guarded output scalar heads, output override scalar heads, and
  interpolation that reuses addressable refs.
- Keep `law_path` and any non-`PATH_REF` surfaces unchanged.
- Bind the self-rooted variant to the current owning declaration root in
  `doctrine/_compiler/resolve/addressables.py` before normal path descent
  and display. Reuse `_resolve_addressable_ref_value` /
  `_resolve_addressable_root_decl` unchanged on the resolved root.
- Add fail-loud diagnostic `E312` when `self:` appears where no
  declaration-root addressable context exists. Finalize the exact code
  number in `docs/COMPILER_ERRORS.md` in the same phase.
- Update `examples/28_addressable_workflow_paths` to teach the shorthand on
  the existing self-owned pressure case.
- Add targeted parser, addressable-resolution, route/review path-read, and
  interpolation proof for `self:` across every `PATH_REF` surface named
  above, not only workflow paths.
- Update the live docs that teach addressable refs in this phase:
  `docs/LANGUAGE_REFERENCE.md`, `docs/AUTHORING_PATTERNS.md`,
  `docs/COMPILER_ERRORS.md` (for `E312`).
- Update `editors/vscode/` TextMate grammar for the `self:` token and run
  `cd editors/vscode && make`.
- Keep the Phase 1 baseline guard green by rerunning its regression proof.

Verification (required proof)

- Run:
  - focused `PATH_REF` parser and resolver tests, including every
    `PATH_REF` surface listed above
  - interpolation proof for `self:` on interpolated addressable refs
  - `uv run --locked python -m unittest tests.test_route_output_semantics`
  - `make verify-diagnostics`
  - `make verify-examples`
  - Phase 1 regression proof
  - `cd editors/vscode && make`

Docs/comments (propagation; this phase)

- Add one short comment at the self-rooted variant's resolve site only if the
  rebinding step would otherwise be easy to misunderstand.
- Phase 6 owns its live-doc updates for addressable refs.

Exit criteria (all required)

- `self:` behaves like a pure shorthand over existing addressable truth,
  carried by one extended `AddressableRef` variant.
- No rooted-path registry, route-owner alias layer, sentinel value, or
  second addressable resolver is introduced.
- Every `PATH_REF` surface in scope (including interpolation) has proof.
- The existing `28` example becomes the canonical teaching example for this
  surface.
- `E312` is named in `docs/COMPILER_ERRORS.md` and exercised in diagnostics
  proof.
- Editor syntax support for `self:` ships in `editors/vscode/`.
- The Phase 1 regression proof still passes.

Rollback

- Remove the `AddressableRef` self-rooted variant, parser support, doc
  updates, and editor syntax updates together. Keep explicit roots only.

## Phase 7 - Release truth, changelog, and full-wave proof

Status

- Planned.

Goal

- Finish the wave with aligned release truth, one coherent changelog entry,
  and a full-wave proof gate. All per-surface live docs and editor syntax
  updates already landed in the feature phase that shipped them.

Work

- Consolidate the additive wave into one release entry, confirm every
  per-phase alignment is still green, and run the full wave-level proof.

Checklist (must all be done)

- Update `docs/VERSIONING.md` to record this wave as a fully additive release
  with no breaking authored-language change.
- Update `CHANGELOG.md` with one release entry that lists the additive wins
  and the shipped diagnostic codes, while noting that `E310` stays reserved.
- Update `docs/README.md` and `examples/README.md` only if their index
  surfaces still point at deprecated teaching tracks.
- Confirm that every touched example family teaches the preferred syntax and
  that no second parallel tutorial track was left behind by any earlier
  phase.
- Confirm editor syntax support in `editors/vscode/` is current with the
  final shipped grammar and rerun its build.
- Refresh wave-level checked-in refs and manifests only where a per-phase
  refresh missed a surface.
- Run the full targeted unit suite named in Section 8.1 plus the baseline
  regression proof.

Verification (required proof)

- Run:
  - `uv sync`
  - `npm ci`
  - `uv run --locked python -m unittest tests.test_import_loading tests.test_compiler_boundary tests.test_emit_flow tests.test_review_imported_outputs tests.test_output_inheritance tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_validate_output_schema tests.test_prove_output_schema_openai tests.test_route_output_semantics tests.test_final_output tests.test_emit_docs tests.test_output_rendering tests.test_compile_diagnostics`
  - `make verify-diagnostics`
  - `make verify-examples`
  - `cd editors/vscode && make`

Docs/comments (propagation; this phase)

- Phase 7 owns only release truth, changelog, and the wave-level index
  surfaces. All per-surface live docs were updated in their feature phase.

Exit criteria (all required)

- `docs/VERSIONING.md` and `CHANGELOG.md` record the wave as fully additive
  with the named diagnostic codes.
- No stale `optional` / `required`, no second alias story, no second
  review-binding story, no second addressable carrier, and no second
  path-root story remain in public teaching surfaces.
- Every feature phase's per-phase docs and editor syntax exit criteria are
  still satisfied at wave end.
- The full targeted proof sweep passes.
- The Phase 1 regression proof still passes.

Rollback

- Revert the wave-level release-truth and changelog entries. Per-phase
  rollback is owned by each feature phase.
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

- keep `E236` / `E237` exact and user-facing (baseline guard)
- add exact diagnostics with named codes for every new fail-loud boundary:
  - `E306` duplicate module alias
  - `E307` duplicate imported symbol
  - `E308` ambiguous imported symbol ownership
  - `E309` malformed grouped `inherit`
  - `E310` reserved for the deferred grouped-override investigation
  - `E311` malformed IO wrapper shorthand (error text must teach the
    multi-line wrapper upgrade path)
  - `E312` malformed `self:` usage (no declaration-root context)
- finalize the exact code numbers against `docs/COMPILER_ERRORS.md` in the
  phase that ships each code
- run `make verify-diagnostics` in every feature phase and at wave end

## 8.4 Full verification commands

- `uv sync`
- `npm ci`
- `uv run --locked python -m unittest tests.test_import_loading tests.test_compiler_boundary tests.test_emit_flow tests.test_review_imported_outputs tests.test_output_inheritance tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_validate_output_schema tests.test_prove_output_schema_openai tests.test_route_output_semantics tests.test_final_output tests.test_emit_docs tests.test_output_rendering tests.test_compile_diagnostics`
- `make verify-examples`
- `make verify-diagnostics`
- if `editors/vscode/` changes, run `cd editors/vscode && make`

# 9) Rollout / Ops / Telemetry

## 9.1 Compatibility posture

- This wave is fully additive. No existing prompt file should need to change
  to keep compiling.
- The shipped `output schema` `nullable` baseline stays as-is; it is a
  locked regression guard, not part of this wave's release story.
- No runtime shim or alias bridge is approved.

## 9.2 Release and docs duties

- per-phase: each feature phase updates its own live-doc sections,
  `docs/COMPILER_ERRORS.md` entries for its named codes, editor syntax
  support, and example refs
- wave-level (Phase 7): update `docs/VERSIONING.md` and `CHANGELOG.md` with
  one additive release entry that lists the additive wins and the shipped
  diagnostic codes, while noting that `E310` stays reserved
- no breaking authored-language cut is recorded in release truth for this
  wave

## 9.3 Telemetry / runtime ops

Not applicable beyond compile-time proof and emitted artifact verification.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: explorer 1, explorer 2, self-integrator, north-star alignment
  pass
- Scope checked:
  - frontmatter and helper-block drift
  - `# TL;DR`
  - `# 0)` through `# 10)`
  - phase-exit completeness, verification burden, rollout duties, and
    canonical owner paths
  - PRINCIPLES.md alignment: Reuse Beats Repetition, one-fix-lands-once,
    Write For Resolvers, Put Deterministic Truth In Typed Surfaces
- Findings summary:
  - earlier revision framed `nullable` as bundled with the additive wins,
    implying a mixed compatibility posture that no longer matches the
    shipped repo
  - the `self:` carrier decision was left open ("sentinel if needed"), which
    violates one-addressable-ref-story
  - later evidence showed grouped bare-ref `override` would need broader
    semantic work than this wave allows
  - named diagnostic codes were present only for the retired nullability
    words; the six new fail-loud boundaries used the phrase "fail loud"
    without codes
  - per-phase docs and editor syntax updates were deferred to a single
    Phase 7, creating a drift window in every feature phase
  - review identity shorthand did not explicitly legalize mixing bare and
    explicit entries; authors would hit the boundary on their first
    non-identity bind
  - grouped `inherit` key scoping vs import-scope lookup was not stated
  - IO shorthand exit criterion allowed "apart from the shorter authoring
    surface that feeds it," leaving room for emit drift
- Integrated repairs:
  - reframed Phase 1 as a locked regression guard and folded the repaired
    five-win wave story through TL;DR, scope, acceptance, tradeoffs,
    compatibility, and release truth
  - locked the `self:` carrier as an extended `AddressableRef` variant;
    sentinel values and second carriers rejected in §0.5, §3.3, §5.1, §5.3,
    §5.4, §6.1, Phase 6
  - deferred grouped bare-ref `override` out of this wave and folded that
    decision through scope, target architecture, call-site audit, rollout,
    and the phase plan
  - assigned named provisional diagnostic codes `E306`..`E312` across §0.2,
    §5.4, §6.1, §8.3, and each feature phase, with `E310` kept reserved
  - moved per-phase live-doc and editor syntax updates into each feature
    phase; shrank Phase 7 to release truth, changelog, and full-wave proof
  - added explicit mixing legality and mixed-entry proof to Phase 4
  - stated inherited-parent-names-only scoping for grouped `inherit` keys in
    §0.5, §3.3, §5.3, and Phase 3
  - strengthened Phase 5 exit criterion to byte-equal
    `final_output.contract.json.io` on rewritten `24` / `117` manifests
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
- 2026-04-16: Adjustments from the north-star alignment pass (additive
  authorship value):
  - Phase 1 (`nullable` baseline) is reframed as a locked regression guard,
    not a wave member. The repaired wave now carries five additive authoring
    wins.
  - `self:` lowers as an extended `AddressableRef` variant. Sentinel values
    and any second `AddressableRef`-like carrier are rejected up front.
  - Grouped bare-ref `override { ... }` is deferred out of this wave.
    Singular and body-carrying override forms stay on the current paths
    unless a later approved plan widens the semantic owner story.
  - Review identity shorthand explicitly allows mixing bare semantic names
    with explicit `semantic: path` entries in the same block, on all three
    surfaces.
  - Grouped `inherit` keys resolve only against inherited-parent names,
    never against the import scope.
  - Named provisional diagnostic codes assigned upfront: `E306` duplicate
    module alias, `E307` duplicate imported symbol, `E308` ambiguous
    imported ownership, `E309` malformed grouped `inherit`, `E310` reserved
    for the deferred grouped-override investigation, `E311` malformed IO
    wrapper shorthand (message teaches multi-line upgrade path), `E312`
    malformed `self:` usage. `E236` / `E237` stay as the baseline guard.
  - Live-doc and editor syntax updates move into each feature phase, not
    Phase 7. Phase 7 shrinks to `docs/VERSIONING.md`, `CHANGELOG.md`,
    wave-level index surfaces, full-wave proof, and final editor sync.
  - IO shorthand exit criterion is strengthened to byte-equal
    `final_output.contract.json.io` on rewritten `24` and `117` manifests.
  - Compact schema heads are recorded as a plausible wave-2 candidate (the
    shipped `nullable` flag already proves the carrier is sugar-friendly);
    deferred here to keep this wave focused, not because the surface is
    speculative.
