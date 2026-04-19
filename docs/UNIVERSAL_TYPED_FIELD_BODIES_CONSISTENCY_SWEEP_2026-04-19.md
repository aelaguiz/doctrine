---
title: "Doctrine Language - Universal Typed Field Bodies Consistency Sweep - Architecture Plan"
date: 2026-04-19
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - examples/29_enums
  - examples/79_final_output_output_schema
  - examples/137_shared_rules_carrier_split
  - examples/138_output_shape_case_selector
  - AGENTS.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/VERSIONING.md
---

# TL;DR

- **Outcome.** One canonical way to express a field's fixed vocabulary anywhere in the Doctrine language: declare `enum X: "title"` once, then write `type: X` on any field-shaped surface. The rendered artifact owns the vocabulary. No parallel forms, no silent fallbacks, no prose restatement by critic agents.
- **Problem.** Today the language has three ways to express a field vocabulary on output schema fields (`type: enum` + inline `values:` block, legacy `type: string` + `enum:` block, and a latent `type: <CNAME>` that silently emits malformed JSON schema) — and **zero** ways on readable `row_schema`, readable `item_schema`, readable `table` columns, and record scalars. Authors fall back to pipe-list prose, critic agents restate it, and downstream repos ship multi-thousand-word step prompts because the authoring surface can't carry the type.
- **Approach.** **Breaking change, major bump language 4.1 → 5.0.** (1) Add structured `type:` slots to every field-shaped surface that today takes only prose. Prose description stays allowed alongside the type slot. (2) Resolve every `type: <CNAME>` through one shared helper: CNAME that is a builtin stays a builtin; CNAME that names an `enum` decl resolves to the enum; anything else raises **E320**. (3) Delete the inline `type: enum` + `values:` form and the legacy `type: string` + `enum:` form. One canonical form only: separate `enum` decl + `type: X`. (4) Render "Valid values: …" uniformly in `emit_docs` for every field-shaped surface.
- **Plan.** (a) Research — done. Pivotal finding: only three output-schema surfaces have structured bodies today; every readable/record field-shaped surface is prose-only by grammar; three enum forms collapse to one; the change is breaking. (b) Deep dive: design the shared type-resolution helper, the per-surface grammar extension, the IR changes (`type_ref: NameRef | None`), the emit rendering, the migration of every shipped example that uses a secondary form, and the exhaustive call-site audit. (c) Phase plan: foundational primitives first (shared resolver + E320 + removed legacy forms), then per-surface grammar/IR/emit adoption, then examples migration, then docs + versioning + skills. (d) Implement end-to-end. (e) Audit.
- **Non-negotiables.**
  - **Breaking change, major bump language 4.1 → 5.0.** No backward-compat crud, no migration shims, no runtime fallbacks. `fallback_policy: forbidden`.
  - **One canonical form for field vocabularies:** separate `enum X: ...` decl + `type: X`. The two secondary enum forms are deleted; every shipped example that uses them gets migrated in this pass.
  - **One shared type-resolution helper.** Every field-shaped surface calls the same resolver entrypoint; no surface gets its own parallel path.
  - **Fail-loud at compile time.** Unknown `type:` CNAME raises **E320** with a message pointing to `enum` decls or builtins. No silent `{"type": "Whatever"}` malformed emit — the current latent bug dies in this pass.
  - **Consistency sweep is load-bearing.** Every field-shaped surface in the shipped grammar must either get a structured `type:` slot in this pass or be explicitly excluded in Section 0.3 with reason. Rediscovering the same gap on a neighboring surface later = failure of this plan.
  - **Downstream unblock.** After landing, `psflows/lesson_plan`'s `step_role` (and every other fixed-vocabulary field) is expressible as one `enum` decl + one `type:` annotation on whatever surface the author actually uses. Zero pipe-list prose.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-19
Verdict (code): NOT COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- Phase 1 is complete and committed (`fe8767c feat(phase 1): shared field-type resolver + E320`); Phase 2 has substantial uncommitted work on the branch but is not done by its own Checklist; Phases 3 through 9 are not started. The remaining frontier spans Phase 2 (finish) through Phase 9 (final verification).
- Prior audit ("implementation has not started; Phase 1 missing") was wrong. Evidence: `doctrine/_compiler/resolve/field_types.py` ships the five named exports plus an `EnumLookup` Protocol alias; `E320` is registered in `docs/COMPILER_ERRORS.md:158`; `tests/test_field_type_ref.py` covers the six Phase-1 behaviors; commit `fe8767c` landed them.
- No execution-side plan rewrite has weakened Section 7. Planning-integrity snag noted under Phase 8: the plan names the new finding `AL930`, but `skills/agent-linter/prompts/refs/finding_catalog.prompt:53` already defines `AL930` as "Skill Needs Host Contract". Phase 8 execution must pick an unused code and append a Decision Log entry; the audit records this as a plan-integrity item, not an implementation completion.

## Reopened phases (false-complete fixes)
- None. No phase was ever marked `Status: COMPLETE` in Section 7. Phase 1 is now truthfully complete per its Checklist and Exit criteria; Phase 2 is in-progress (uncommitted); Phases 3 through 9 are unstarted.

## Missing items (code gaps; evidence-anchored; no tables)

- Phase 2 — Wire structured output-schema surfaces to the shared resolver (in progress; uncommitted)
  - Evidence anchors:
    - `doctrine/_model/io.py:276,285,302` — `type_ref: FieldTypeRef | None` is present on `OutputSchemaField`, `OutputSchemaDef`, and `OutputSchemaRouteField`. ✓
    - `doctrine/_compiler/resolve/output_schemas.py:12-16` — imports `BuiltinTypeRef`, `EnumTypeRef`, `resolve_field_type_ref`.
    - `doctrine/_compiler/resolve/output_schemas.py:46-48` — `_OutputSchemaNodeParts` now carries both `type_name` (legacy) and `type_ref` alongside `legacy_enum_values`.
    - `doctrine/_compiler/resolve/output_schemas.py:1101-1117` — lowering prefers `parts.type_ref` for `BuiltinTypeRef`/`EnumTypeRef` and falls back to `parts.type_name` + `parts.enum_values` for Form A / Form B. ✓
    - `doctrine/_compiler/resolve/output_schemas.py:1386-1397` — the `type:` capture routes through `resolve_field_type_ref` when `item.value != "enum"` (Form A still takes the legacy path). ✓
    - `tests/` — only `test_field_type_ref.py` exists for this plan; `tests/test_output_schema_surface.py` and `tests/test_output_schema_lowering.py` contain no `type_ref`, `FieldTypeRef`, or `E320` references.
    - Phase 2 changes are uncommitted: `git status` shows `M doctrine/_compiler/resolve/output_schemas.py`, `M doctrine/_model/io.py`, `M doctrine/diagnostics.py`, and friends.
  - Plan expects (Phase 2 Checklist + Exit criteria):
    - IR on all three structured output-schema classes carries `type_ref`. ✓
    - `_collect_output_schema_node_parts` routes the `type:` capture through `resolve_field_type_ref`. ✓ for non-`enum` branch.
    - `_lower_output_schema_parts` writes `schema["type"]` and `schema["enum"]` from `parts.type_ref` when present; falls back to Form A / Form B path when `parts.type_ref is None`. ✓
    - Form A (`type: enum` + `values:`) continues to parse and compile; its lowered JSON schema is byte-identical to before Phase 2 for every shipped example that uses it. Not yet proven at the phase tip — Phase 2 artifacts are uncommitted and the worklog does not report a Phase 2 `make verify-examples` green pass.
    - Form B (`type: string` + `enum:`) continues to parse and compile; byte-identical. Same verification gap.
    - `type: <EnumName>` on the three surfaces resolves and emits `schema["type"]="string"` plus `schema["enum"]=[...]` in member order. No committed test proves this at the phase boundary.
    - `type: <UnknownCNAME>` on the three surfaces raises `E320`. No committed test proves this at the phase boundary.
    - New unit cases in `tests/test_output_schema_surface.py` and `tests/test_output_schema_lowering.py` covering (a) `type: <EnumName>` resolves and emits expected JSON schema, (b) `type: <UnknownCNAME>` raises `E320`, (c) existing Form A / Form B cases still pass byte-identically. **Missing.**
    - Targeted parser source-span test confirming `E320` carries the CNAME span on the three output-schema surfaces. **Missing** (the Phase 1 test proves span carry in isolation, not through the output-schema collector).
    - Checklist tension (`_OutputSchemaNodeParts.type_name` is replaced by `type_ref`): implementation keeps both fields so Phase 2's "Form A/B keep working" promise survives; `type_name` is scheduled to die in Phase 3 with `legacy_enum_values`. Call this an accepted transitional shape; the Phase 3 exit criteria still force the removal.
  - Code reality:
    - Wiring and IR changes present but not committed; no new unit/integration coverage; Phase 2 worklog entry absent.
  - Fix:
    - Add the unit cases and source-span test named above, run `make verify-examples` + `make verify-diagnostics` from the Phase 2 tip, append a Phase 2 worklog entry with green signals, then commit as a Phase 2 checkpoint before starting Phase 3.

- Phase 3 — Delete Form A and Form B; migrate shipped examples; lock removal
  - Evidence anchors:
    - `doctrine/grammars/doctrine.lark:776,777,804,805,806` — `output_schema_enum_block`, `output_schema_values_block`, and `output_schema_enum_value` productions and registrations are still present.
    - `doctrine/_compiler/resolve/output_schemas.py:46-48,60-63` — `_OutputSchemaNodeParts.legacy_enum_values`, `legacy_enum_source_span`, `inline_enum_values`, `inline_enum_source_span` remain; the Form A / Form B normalization branches are still live.
    - `doctrine/_compiler/resolve/output_schemas.py:17-23` (per plan anchor) — local `BUILTIN_TYPE_NAMES` constant has not moved to `field_types.py` (which now owns the authoritative copy). Both copies coexist.
    - `examples/79_final_output_output_schema/prompts/AGENTS.prompt:7-8`, plus the sibling `.../optional_no_example/AGENTS.prompt`, `.../invalid_invalid_example/AGENTS.prompt`, `examples/85_review_split_final_output_output_schema/prompts/AGENTS.prompt`, `examples/90_split_handoff_and_final_output_shared_route_semantics/prompts/AGENTS.prompt`, and `examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt` — all six still author Form A (`type: enum` + `values:`).
    - No `tests/test_enum_migration_preservation.py` (or equivalent); no manifest-backed "Form A no longer parses" or "Form B no longer parses" compile-fail cases under `doctrine/_diagnostic_smoke/`.
  - Plan expects:
    - Both grammar productions deleted with their registrations; `output_schema_enum_value` helper deleted if unused; Form A and Form B normalization branches deleted; `_OutputSchemaNodeParts.legacy_enum_values` and Form-A/B-only fields deleted; six shipped examples rewritten to canonical form and `ref/**` regenerated; test fixtures in `tests/test_output_schema_surface.py`, `tests/test_output_schema_lowering.py`, `tests/test_final_output.py`, `tests/test_compile_diagnostics.py`, and `doctrine/_diagnostic_smoke/fixtures_final_output.py` migrated; manifest-backed "no longer parses" compile-fail cases for both deleted forms; a preservation assertion test locking JSON-schema `enum` value and order against the Phase 2 tip output for every migrated example; `BUILTIN_TYPE_NAMES` local copy removed in favor of the `field_types.py` owner.
  - Code reality:
    - Grammar still parses both forms; resolver normalization branches intact; all six example files still use Form A; no preservation test; no "no longer parses" cases; dual `BUILTIN_TYPE_NAMES` definitions.
  - Fix:
    - Execute Phase 3 per its Checklist and Exit criteria after Phase 2 is closed out.

- Phase 4 — Extend structured `type:` slot to prose-only field-shaped surfaces
  - Evidence anchors:
    - `doctrine/grammars/doctrine.lark` — no `typed_field_body_line` fragment; `readable_inline_schema_item_body`, `readable_table_column_body`, `record_item_body`, and `output_record_item_body` are still prose-only.
    - `doctrine/_model/readable.py` — `ReadableSchemaEntry` and `ReadableTableColumn` carry no `type_ref`; record scalar carriers carry no `type_ref`.
    - Repo grep for `typed_field_body_line` matches only this plan doc.
  - Plan expects:
    - `typed_field_body_line` grammar fragment; `readable_inline_schema_item_body`, `readable_table_column_body`, and scalar-head `record_item_body`/`output_record_item_body` accept it; `type_ref` added to `ReadableSchemaEntry`, `ReadableTableColumn`, and the record scalar carrier; per-surface resolver call sites into `resolve_field_type_ref`; `ReadablePropertyItem` and `ReadableDefinitionItem` explicitly unchanged; unit cases for (a) builtin (b) enum (c) `E320` on each surface; parser source-span coverage for each; record-scalar rejection test when `record_head` is not scalar.
  - Code reality:
    - No grammar fragment; no IR fields; no resolver wiring; no tests.
  - Fix:
    - Execute Phase 4.

- Phase 5 — Unified emit of `Valid values: …` line across every field-shaped surface
  - Evidence anchors:
    - `doctrine/emit_common.py` — no `render_valid_values_line` (repo-wide grep matches only this plan doc).
    - `doctrine/_compiler/validate/__init__.py:271-293` (plan anchors) — `_json_schema_meaning` description-present branch still drops the enum vocabulary.
    - `doctrine/emit_docs.py` readable-table-column, readable-schema-entry, record-scalar, and output-schema renderers do not call any valid-values helper.
  - Plan expects:
    - `render_valid_values_line` helper in `emit_common.py`; all four field-shaped renderers in `emit_docs.py` call it; `_json_schema_meaning` appends `One of <values>.` when both description and enum are present; unit cases per surface plus a `_json_schema_meaning` description-plus-enum case.
  - Code reality:
    - No helper; no renderer wiring; no validator meaning extension; no tests.
  - Fix:
    - Execute Phase 5.

- Phase 6 — New example `examples/139_enum_typed_field_bodies/` as manifest-backed proof
  - Evidence anchors:
    - `examples/` — highest existing example is `138_output_shape_case_selector`; there is no `139_enum_typed_field_bodies/` directory.
  - Plan expects:
    - `examples/139_enum_typed_field_bodies/prompts/AGENTS.prompt` declaring one enum and a readable row_schema entry with `type: <EnumName>` alongside prose; `cases.toml` with `render_contract` plus `compile_fail` (unknown enum → `E320`); committed `ref/**`.
  - Code reality:
    - Directory does not exist.
  - Fix:
    - Execute Phase 6 after Phases 4–5 (so typed `row_schema` bodies and unified emit exist to be exercised).

- Phase 7 — Authoritative docs, version bump, and CHANGELOG
  - Evidence anchors:
    - `docs/VERSIONING.md` and `CHANGELOG.md` — no 4.1 → 5.0 entry; `docs/LANGUAGE_REFERENCE.md` local diff covers the output shape selector and export-namespace work from prior plans, not the canonical-form rewrite or a "Typed field bodies" subsection; `docs/LANGUAGE_DESIGN_NOTES.md` and `docs/AGENT_IO_DESIGN_NOTES.md` carry no one-canonical-form decision note and still describe Form A / Form B as live.
    - `docs/COMPILER_ERRORS.md:158` — the Phase 1 `E320` row exists and is already consistent with `doctrine/_compiler/resolve/field_types.py`; Phase 7 needs to keep that row consistent with the final CHANGELOG wording but does not author the row itself.
  - Plan expects:
    - `LANGUAGE_REFERENCE.md` output-schema subsection rewritten to canonical form; new "Typed field bodies" subsection covering row_schema / item_schema / table column / record scalar with cross-ref to `examples/139_enum_typed_field_bodies/`; one-canonical-form decision note in `LANGUAGE_DESIGN_NOTES.md`; `AGENT_IO_DESIGN_NOTES.md` Form A / Form B references rewritten to canonical; 4.1 → 5.0 entry in `VERSIONING.md` and `CHANGELOG.md` with the five-bullet summary; `docs/README.md` + `examples/README.md` index lines verified.
  - Code reality:
    - No edits in any of these files for this plan.
  - Fix:
    - Execute Phase 7.

- Phase 8 — Shipped skills: agent-linter new-finding + AL200 extension, doctrine-learn authoring-pattern + ladder
  - Evidence anchors:
    - `skills/agent-linter/prompts/refs/finding_catalog.prompt:53` — `AL930` is already assigned to "Skill Needs Host Contract" (an unrelated finding). The plan's AL930 slot is taken.
    - `skills/agent-linter/prompts/refs/examples.prompt` — no before/after pair for inlined-vocabulary-should-be-enum.
    - `skills/doctrine-learn/prompts/refs/authoring_patterns.prompt` — no task-first chooser row cross-referencing `examples/139_enum_typed_field_bodies`.
    - `skills/doctrine-learn/prompts/refs/outputs_and_schemas.prompt` — still teaches Form A guidance.
    - Local `git status` shows curated and `.prompt` files for `agent-linter` and `doctrine-learn` as modified, but their diffs belong to prior plans (not this one — repo grep for `AL930` + "Inlined Vocabulary"/"typed field bodies" returns zero matches in the skill source).
  - Plan expects:
    - New finding row + full section (what it means, why it matters, default fix, good/bad pair) for the inlined-vocabulary rule in `finding_catalog.prompt`; `AL200` section extended to name pipe-list vocabularies as a canonical duplicate-rule shape; new finding before/after pair in `examples.prompt`; task-first chooser row in `authoring_patterns.prompt` naming canonical form + cross-reference to `examples/139_enum_typed_field_bodies`; `outputs_and_schemas.prompt` rewritten off Form A; doctrine-learn examples ladder gains example 139; curated `.md` outputs regenerated under `skills/.curated/agent-linter/references/` and `skills/.curated/doctrine-learn/references/`; new prose passes the 7th-grade reading-level bar.
  - Plan-integrity gap:
    - The plan's nominated code `AL930` collides with the live catalog entry in `finding_catalog.prompt:53`. Phase 8 execution must pick an unused code, update Section 0.2, Section 6.1, Section 7 Phase 8 text, and append a Decision Log entry recording the rename. Do this in the Phase 8 run; the plan rewrite is part of the phase obligation, not a separate ticket.
  - Code reality:
    - No prompt-source edits for this plan; curated outputs untouched for this plan.
  - Fix:
    - Execute Phase 8 after Phase 6, resolving the finding-code collision in the same run.

- Phase 9 — Editor snapshots + final corpus-level verification
  - Evidence anchors:
    - `editors/vscode/tests/snap/examples/79_final_output_output_schema/...`, `.../121_nullable_route_field_final_output_contract/...` still reflect Form A pre-migration shape.
    - No final Decision Log entry in Section 10 recording green `make verify-examples`, `make verify-diagnostics`, `make verify-package`, or the psflows scratch-conversion result.
  - Plan expects:
    - Snapshots regenerated via `cd editors/vscode && make` after Phases 3 and 5 land; full `make verify-examples`, `make verify-diagnostics`, `make verify-package` green; release-flow verification status recorded (or noted as n/a); psflows `step_role` scratch conversion compiles read-only on this branch; `git diff main -- ../psflows` empty; final Decision Log entry.
  - Code reality:
    - No snapshot regeneration possible while Phases 3 and 5 are absent; no final verification entry.
  - Fix:
    - Execute Phase 9 after Phases 2 through 8 land cleanly.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None. The remaining work is entirely code, grammar, IR, resolver, emit, examples, docs, skill-prompt source edits, and editor snapshots — no manual QA gates the verdict here.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
research_pass_1: done 2026-04-19
deep_dive_pass_1: done 2026-04-19
phase_plan_pass_1: done 2026-04-19
recommended_flow: research -> deep dive -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

The shipped Doctrine language at version 5.0 has exactly one way to express a field's fixed vocabulary: declare an `enum` decl and write `type: X` on the field. This works on every field-shaped authoring surface in the language (output schema field/route field/def, readable `row_schema` entry, readable `item_schema` entry, readable `table` column, record scalar). The two prior enum forms (`type: enum` + `values:` block; legacy `type: string` + `enum:` block) are deleted from grammar, model, resolver, and emit. Unknown `type:` CNAME fails loudly with E320. The rendered artifact for every field-shaped surface shows the enum's valid values once. After this change, `psflows/lesson_plan`'s `step_role` (and every similar fixed-vocabulary field) is expressible as one `enum` decl plus one `type:` annotation on whatever surface the author uses — zero pipe-list prose.

Falsification: if after landing, (a) any field-shaped surface in the shipped grammar still rejects `type: <EnumName>`, or (b) either secondary enum form still parses, or (c) any pre-existing example survives unchanged while its semantics depended on a deleted form, or (d) unknown type CNAME silently compiles, or (e) `psflows/lesson_plan`'s `step_role` still requires pipe-list prose to express, the claim is false.

## 0.2 In scope

**Requested behavior scope.**
- **One canonical `type:` statement** on every field-shaped surface:
  - `type: <CNAME>` where CNAME is a builtin primitive (`string`, `integer`, `number`, `boolean`, `object`, `array`, `null`) or names an `enum` decl in the same unit or via imports.
  - No other forms. The inline `type: enum` + `values:` block and legacy `type: string` + `enum:` block are deleted.
- **Structured `type:` slots added to every prose-only field-shaped surface** confirmed in Section 3.2 (research):
  1. `output_schema_field` / `output_schema_route_field` / `output_schema_def` (already structured; existing `type:` resolver tightened + enum-ref support added; secondary forms deleted)
  2. Readable `row_schema` entry body (`readable_inline_schema_item_body` when under `row_schema:`)
  3. Readable `item_schema` entry body (`readable_inline_schema_item_body` when under `item_schema:`)
  4. Readable `table` column body (`readable_table_column_body`)
  5. Record scalar body (`record_keyed_item` / `output_record_keyed_item`)
  - For surfaces 2–5, grammar gains a `typed_body_stmt` alongside existing `block_lines`: prose description stays allowed; the type slot is structured.
- **One shared type-resolution helper.** Every surface calls a single helper that accepts a CNAME + its source span and returns a resolved kind (builtin | enum decl ref) or raises E320. No surface gets its own parallel path.
- **IR uniformity.** Every affected IR class gains `type_ref: NameRef | None` (or equivalent resolved union type), mirroring `OutputShapeSelectorConfig.enum_ref` at `doctrine/_model/io.py:252`.
- **Emit uniformity.** Every field-shaped emit path renders `Valid values: a, b, c.` (or the current `One of a, b.` phrasing, unified at `emit_common`) under the field description when the field has an enum `type_ref`. Builtin types render as today.
- **Diagnostic E320** for unknown type CNAME and for non-enum non-builtin decl refs. Reuse E276/E281 for "name does not resolve at all."
- **Examples migration (mandatory).** Every shipped example under `examples/` that uses a secondary enum form (inline `type: enum` + `values:` or legacy `type: string` + `enum:`) is rewritten to use the canonical `enum` decl + `type: X` form in this same pass. `ref/**` outputs may change for the rewritten examples (intentional, recorded in Decision Log); behavior-preservation signal is that the rewritten example still manifests as before (same JSON schema values) under the new form.
- **New consolidated example** `examples/139_enum_typed_field_bodies/` demonstrating the typed form on the primary motivating surface (readable `row_schema` typed column) with manifest-backed render_contract + compile-fail cases.
- **Language bump 4.1 → 5.0** (major breaking) in `docs/VERSIONING.md` and `CHANGELOG.md` with explicit breaking-change notes and migration guidance.
- **Shipped skills teach the new shape explicitly (confirmed in-scope).**
  - `agent-linter`: new finding **AL930** (prose vocabularies must become enum-typed fields) plus an AL200 extension naming pipe-list vocabularies as a canonical duplicate-rule shape. Edit the `.prompt` source; regenerate curated/build outputs.
  - `doctrine-learn`: new authoring-pattern row (task-first chooser: "fixed vocabulary on a field → declare `enum` + `type: X`"); add example 139 to the examples ladder. Edit the `.prompt` source; regenerate curated/build outputs.
- **All authoritative docs are updated (confirmed in-scope).** Every doc that carries shipped truth about field-shaped surfaces reflects the new fragment: `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md` (E320 entry), `docs/VERSIONING.md`, `CHANGELOG.md`, `examples/README.md` if it indexes typed patterns, and any `docs/README.md` index line that names the relevant surfaces. Drift between code, docs, and examples is a blocker for Definition of Done.

**Allowed architectural convergence scope.**
- Adding structured `type:` grammar to the currently-prose-only field-shaped surfaces named in Section 0.2. Prose lines remain allowed alongside.
- Deleting grammar productions for the two secondary enum forms (`output_schema_values_block` + `type: enum` normalization; `output_schema_enum_block` + legacy `type: string + enum:` normalization). Delete the associated IR carriers, resolver branches, and validator warnings.
- Introducing one shared type-resolution helper in the compiler that every surface calls. No parallel path per surface.
- Extending the affected IR classes to carry an optional resolved type ref (`type_ref: NameRef | None` or equivalent, mirroring `OutputShapeSelectorConfig.enum_ref` at `doctrine/_model/io.py:252`).
- Touching emit paths (`emit_docs.py`, `emit_common.py`) so every field-shaped surface renders the shared "Valid values: …" description line from the unified IR.
- **Migrating every shipped example that uses a deleted form** to the canonical form. Expected touches include (but are not limited to) `examples/79_final_output_output_schema/` and any other example that uses inline `values:` or legacy `enum:` blocks. Exact list is enumerated during `deep-dive`.
- Touching the agent-linter prompt source (`skills/agent-linter/prompts/refs/finding_catalog.prompt`, `examples.prompt`) to add AL930 and extend AL200.
- Touching the doctrine-learn prompt source (`skills/doctrine-learn/prompts/refs/authoring_patterns.prompt` and the examples ladder) to add the authoring-pattern row and example 139 entry.

**Adjacent surfaces in scope (same contract family).**
- Compiler resolve pipeline for any surface that normalizes a field's type.
- `doctrine/emit_docs.py` rendering of every field-shaped surface.
- `docs/LANGUAGE_REFERENCE.md` sections covering each field-shaped surface.
- `docs/COMPILER_ERRORS.md` (new E320 entry).
- Agent-linter and doctrine-learn curated outputs (regenerated from `.prompt` source).

**Compatibility posture.**
- **Clean cutover, breaking change.** Language 4.1 → 5.0 major bump. Existing programs that use deleted forms fail to compile under 5.0; authors migrate to the one canonical form. No timeboxed bridge, no runtime shim, no parser-side legacy branch.
- The shipped example corpus is migrated in-pass. Downstream Doctrine repos (including `psflows`) are responsible for their own migration; AGENTS.md plain-language migration guidance ships with the CHANGELOG entry.
- The agent-linter flags any remaining prose-vocabulary pattern via AL930; doctrine-learn teaches the canonical form in the authoring-pattern chooser.

## 0.3 Out of scope

- Arbitrary value patterns (e.g. `ans-*` receipt ids as a typed constraint). Separate language extension.
- Extending `type:` to carry generic types (lists of enums, optional/nullable markers beyond what exists today). Follow-up if demand surfaces.
- Module-qualified type refs (`Module.EnumName`) if grammar recon shows this needs a new CNAME+DOT rule. If it's free, include it; if it costs a grammar rework, defer.
- **Editing `../psflows` (hard exclusion, user-confirmed).** psflows is read-only from this repo. Do not edit any file under `../psflows`. Reference excerpts are allowed as motivation only. Downstream upgrade is a separate task owned by that repo. Any work that would require touching psflows to land is out of scope for this plan.
- Refactoring unrelated parts of the resolve pipeline that do not touch field-type resolution.
- Broad docs cleanup. Only docs that carry authoritative truth about the changed surfaces get updated in this pass.

## 0.4 Definition of done (acceptance evidence)

- `make verify-examples` is green across the **migrated** shipped corpus. Examples that previously used a deleted form are rewritten to the canonical form in this pass, and their `ref/**` outputs are regenerated.
- `make verify-diagnostics` is green. E320 has a manifest-backed compile-fail case. **Each deleted form has a manifest-backed "no longer parses" compile-fail case** so the removal is locked in.
- `make verify-package` is green (versioning docs changed; 4.1 → 5.0 major bump).
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/139_.../cases.toml` passes for render_contract + compile_fail cases on the new example.
- **Resolver unit tests per surface.** Each field-shaped surface named in Section 0.2 has a test that proves: (a) `type: <BuiltinName>` resolves; (b) `type: <EnumName>` resolves and carries the resolved enum ref; (c) `type: <UnknownName>` raises E320; (d) neither deleted form parses anywhere; (e) prose description still renders alongside the type slot.
- **Behavior preservation for the canonical form (not for deleted forms).** For every migrated example that previously used a secondary enum form, the emitted JSON schema (for output schemas) contains the same enum values in the same order as before migration. A resolver-level assertion test proves this explicitly so the migration is not eyeballed.
- Skill curated outputs regenerate cleanly: `skills/.curated/agent-linter/references/finding-catalog.md` carries AL930 and the AL200 extension, `skills/.curated/agent-linter/references/examples.md` carries the before/after pair, `skills/.curated/doctrine-learn/references/authoring-patterns.md` carries the new row, and the doctrine-learn examples ladder lists example 139.
- Every authoritative doc named in Section 0.2 reflects the new shape. `docs/LANGUAGE_DESIGN_NOTES.md` records the one-canonical-form decision. `docs/COMPILER_ERRORS.md` has E320. `docs/VERSIONING.md` + `CHANGELOG.md` name the 4.1 → 5.0 breaking bump with explicit migration guidance.
- **Downstream sanity check (local, uncommitted).** A scratch conversion of `psflows/lesson_plan`'s `step_role` prose into the canonical form compiles in isolation against this branch (excerpt-only per the psflows-read-only rule). This is the final proof the language now carries the motivating case.
- **No file under `../psflows` is modified in this branch's diff.**

## 0.5 Key invariants (fix immediately if violated)

- **One canonical form for field vocabularies.** `enum X: ...` decl + `type: X`. Two or more parseable forms for the same concept = invariant violated.
- **No parallel type-resolution paths.** Every field-shaped surface reaches the same resolver helper. No surface calls the enum resolver directly.
- **Fail-loud boundaries.** Unknown `type:` CNAME → E320 at compile time. No silent `{"type": "Whatever"}` emit. No string fallback.
- **No runtime shims, no legacy-form preservation.** `fallback_policy: forbidden`. Deleted forms stay deleted. No parser-side branch that still accepts them "just in case."
- **Consistency sweep is load-bearing, not optional.** Section 3.2 enumerates every field-shaped surface in the shipped grammar; each either gets the structured `type:` slot in this pass or is explicitly excluded in Section 0.3 with a credible reason.
- **Behavior preservation for the canonical form, not the deleted forms.** The migrated examples' resulting JSON schema (for output schemas) and rendered docs (for readable/record surfaces) must match their pre-change semantics. Deleted-form examples change shape by construction; that is the point.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. **Elegance — one canonical form.** `enum X: ...` decl + `type: X`. Two-plus forms for one concept is a bug; delete the secondary forms. This is the user's primary directive ("max elegance").
2. **Consistency across all field-shaped surfaces.** One resolver helper, one emit line, one IR carrier across output schema + readable + record surfaces.
3. **Fail-loud semantics.** Unknown type CNAME raises E320. No silent malformed emit.
4. **Emit quality.** The rendered field description shows the vocabulary once, plainly, at 7th-grade reading level.
5. **Downstream unblock.** After landing, `psflows/lesson_plan` can express `step_role` typed on whatever surface the author uses.

Backward compatibility is **not** on this list. Breaking change is accepted by user direction.

## 1.2 Constraints

- Language version bumps 4.1 → **5.0** (major, breaking). `CHANGELOG.md` entry names the deleted forms and the migration path.
- AGENTS.md "one new idea per example" rule: the example focuses on the primary motivating surface (typed `row_schema` column). Other surfaces get coverage via targeted resolver tests, not additional examples.
- Plain-language hard requirement for all shipped Markdown prose: agent-linter and doctrine-learn entries stay at ~7th-grade reading level.
- Skill source-of-truth rule: edit `.prompt` sources, regenerate curated/`build` outputs.
- `fallback_policy: forbidden` is the default; runtime shims are out.
- No editing of psflows; only reference excerpts.

## 1.3 Architectural principles (rules we will enforce)

- **One canonical form.** `enum X: ...` decl + `type: X`. Both secondary forms are deleted outright — no parser-side legacy branch, no runtime shim.
- **Single resolver entrypoint.** One helper turns a CNAME into a resolved type (builtin | enum decl ref) or raises E320. No surface calls the enum resolver directly.
- **IR carries the resolved ref, not denormalized values.** Emit reads the enum decl through the ref. Avoid eager denormalization that would drift.
- **Examples are manifest-backed proof, not ornament.** The new example has both render_contract and compile-fail cases; every deleted form has its own "no longer parses" compile-fail case.
- **Emit line is identical across surfaces.** Rendered description carries "Valid values: a, b, c." (or the unified phrasing chosen in deep-dive) under every field-shaped surface.

## 1.4 Known tradeoffs (explicit)

- **Breaking bump vs. minor bump.** Chose breaking (4.1 → 5.0) to delete secondary enum forms and tighten `type:` to fail loud. Tradeoff: every existing Doctrine program that uses a deleted form (shipped examples, downstream consumers) must migrate. Accepted by user direction.
- **Universal grammar extension vs. narrow fix.** Chose universal. Tradeoff: larger grammar and IR surface. Rejected the narrow fix because it would leave the same gap on readable `row_schema` / `item_schema` / `table` column / record scalar surfaces, exactly the failure mode the user warned against.
- **Single example vs. per-surface examples.** One new example + per-surface resolver tests keeps the corpus lean (AGENTS.md "one new idea per example"). Tradeoff: less user-facing demonstration of each surface; mitigated by a LANGUAGE_REFERENCE.md subsection that names each surface.
- **Enum decl reuse vs. new type-ref grammar.** Reuse `_resolve_enum_ref` / `_try_resolve_enum_decl` rather than invent a new type-ref node. Module-qualified type refs (`Module.EnumName`) deferred unless deep-dive finds grammar cost is trivial.
- **Diagnostic code reuse vs. new.** Mint E320 for "type ref is neither builtin nor an enum decl." Reuse E276/E281 for "name does not resolve at all." Small catalog growth.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- Grammar has a structured type slot (`output_schema_type_stmt: "type" ":" CNAME`) only on `output_schema_field`. Resolver handles `"string" | "integer" | "boolean" | ... | "enum"` plus inline `values:` and legacy `enum:` forms.
- Every other field-shaped surface (readable `row_schema` entry, readable `item_schema` entry, readable `table` column, record scalar, review-carrier field) takes a prose body only: `_INDENT block_lines _DEDENT`.
- Authors who need a field to carry a fixed vocabulary write pipe-list prose in one role and restate the same list in a critic's gate check.
- `emit_docs.py` renders output-schema enum values already, via `schema["enum"]` populated from `_normalize_output_schema_inline_enum`.
- The agent-linter already names "duplicate rule across agents" (AL200) but does not specifically flag pipe-list vocabularies as the canonical duplicate shape.
- `doctrine-learn` teaches enum decls (example 29) but does not teach "type a field by the enum" because that pattern is not expressible outside `output_schema_field`.

## 2.2 What's broken / missing (concrete)

- Authors cannot express "this field's value comes from a fixed vocabulary" in row_schema, item_schema, table columns, or record scalars. They must describe it in prose.
- Two prose copies of the same vocabulary drift by hand. The critic's gate check and the primary agent's schema drift independently.
- The result is prompt bloat. `psflows/lesson_plan` ships a ~2000-word step prompt largely because the authoring surface can't carry the types. Quoted excerpt (read-only): `step_role` values enumerated as `introduce | practice | test | capstone` in the primary role, then restated as `output_gates_pass.step_role_in_vocabulary` in the critic.
- The missing surface is a *language gap*, not a *misuse of existing patterns*. Every adjacent primitive exists (enum decls at example 29, typed output schema at example 79, shared rules at example 137, case-selected output shapes at example 138). The only missing bridge is uniform typed field bodies.

## 2.3 Constraints implied by the problem

- The fix must reach every field-shaped surface, or the gap returns on the next surface an author tries.
- The fix must fail loud on unknown type refs. A silent fallback to prose or to a malformed JSON schema re-creates the bug in a new disguise.
- The fix must converge to **one canonical form**. Parallel forms are the root failure mode; preserving them "for compatibility" is the exact anti-pattern this plan exists to delete.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal "ground truth")

## 3.1 External anchors (papers, systems, prior art)

- None adopted. The design is internal to the Doctrine language and is well-served by its own existing primitives (enum decls at example 29, typed output schema at example 79). External prior art (JSON Schema enum, Protobuf enum fields, GraphQL enum types) is culturally familiar to the target audience and informs naming ("Valid values:", "type:"), but offers no load-bearing design input.

## 3.2 Internal ground truth (code as spec)

### Structured-type surfaces (already accept `type: <CNAME>`)

All three share `output_schema_item_body` at `doctrine/grammars/doctrine.lark:763` and resolve through `_collect_output_schema_node_parts` in `doctrine/_compiler/resolve/output_schemas.py:1350`:

- `output_schema_field` — `doctrine/grammars/doctrine.lark:753` — IR `doctrine/_model/io.py:269 OutputSchemaField`.
- `output_schema_route_field` — `doctrine/grammars/doctrine.lark:754` — IR `doctrine/_model/io.py:293 OutputSchemaRouteField`.
- `output_schema_def` — `doctrine/grammars/doctrine.lark:755` — IR `doctrine/_model/io.py:277 OutputSchemaDef`.

The `type:` rule itself is `output_schema_type_stmt: "type" ":" CNAME _NL?` at `doctrine/grammars/doctrine.lark:793`. Grammar accepts any CNAME. Resolver at `output_schemas.py:1359` stores it as `parts.type_name` with no validation. Lowering at `output_schemas.py:1109` writes it straight into `schema["type"]`. Only `"enum"` has special branch handling in `_normalize_output_schema_inline_enum` at `output_schemas.py:1636-1671` (where `parts.type_name == "enum"` becomes `"string"` after harvesting `values:`). A builtin-types constant exists at `output_schemas.py:17-23` ({`array`, `boolean`, `integer`, `null`, `number`, `object`, `string`}) but is not used as a whitelist against `parts.type_name`.

**Implication.** An author who writes `type: StepRole` today gets a silent malformed JSON schema (`{"type": "StepRole"}`). There is no diagnostic. This is a latent bug independent of the consistency sweep.

### Prose-only surfaces (no structured `type:` slot today — by grammar design)

Every non-output-schema field-shaped surface uses an `_INDENT block_lines _DEDENT` prose body. None accept `type:` today:

- `readable_table_column` — `doctrine.lark:556` — body `readable_table_column_body: _INDENT block_lines _DEDENT` (`:557`) — IR `doctrine/_model/readable.py:65 ReadableTableColumn(key, title, body)` (no type field).
- `readable_inline_schema_item` — `doctrine.lark:565` — body `:566` — IR `doctrine/_model/readable.py:43 ReadableSchemaEntry` (no type field). Used for both `row_schema` and `item_schema` entries inside readable tables and readable lists.
- `readable_property_item` — `doctrine.lark:530` — body `:531` — IR `doctrine/_model/readable.py:29 ReadablePropertyItem` (no type field).
- `readable_definition_item` — `doctrine.lark:534` — body `:535` — IR `doctrine/_model/readable.py:21 ReadableDefinitionItem` (no type field).
- `record_keyed_item` / `output_record_keyed_item` — `doctrine.lark:915` / `:862` — body is `record_item_body` with prose plus nested records. No `type:` slot; record scalars carry a `record_head` reference only.
- `enum_member` — `doctrine.lark:922` — body `enum_member_body` permits only `wire:` (scalar override) plus prose. No `type:` slot; would be semantically odd anyway.
- `readable_list_keyed_item` — `doctrine.lark:526` — no body at all.
- `readable_footnote_item` — `doctrine.lark:584` — no body at all.
- `semantic_field_binding` (review carrier field) — `doctrine.lark:179` — bare `CNAME (":" field_path)?`; no body.
- `skill_entry_bind_item` — `doctrine.lark:665` — reference-only binding; no body.

**This is the pivotal research finding.** The plan's TL;DR and Section 0 imagined a shared `typed_field_body` fragment factored out of an existing structured body. In reality, only the three output-schema surfaces have a structured body at all. Extending `type: <EnumName>` to readable `row_schema` entries, readable `table` columns, record scalars, and any other prose-bodied surface is a **grammar extension at each target surface**, not a fragment factorization. Each touched surface gets: grammar rule changes (add structured body alongside or replacing prose), IR changes (new optional `type_ref: NameRef | None` field), resolve changes, emit changes.

### Resolver and validator helpers available for reuse

- Safe enum lookup: `_try_resolve_enum_decl(ref, *, unit) -> EnumDecl | None` at `doctrine/_compiler/resolve/refs.py:1031`.
- Raising enum resolver: `_resolve_enum_ref(ref, *, unit) -> tuple[IndexedUnit, EnumDecl]` at `doctrine/_compiler/resolve/refs.py:513`.
- Precedent for `enum_ref: NameRef` in IR: `OutputShapeSelectorConfig.enum_ref` at `doctrine/_model/io.py:252`.
- Existing "One of a, b." emission: `_json_schema_meaning` at `doctrine/_compiler/validate/__init__.py:271`, renders when description is empty and enum is present. Source: `f"One of {rendered}."` at line 292.

### Adjacent surfaces tied to the same contract family

- **Diagnostics catalog** — `docs/COMPILER_ERRORS.md`. Any new diagnostic code (E320 proposed) lands here.
- **Language reference** — `docs/LANGUAGE_REFERENCE.md`. Every surface that gets a new structured body must get a new subsection.
- **Language design notes** — `docs/LANGUAGE_DESIGN_NOTES.md`. The "prose-by-design" claim for readable bodies, if true, is probably documented here and must be updated in the same pass.
- **Versioning** — `docs/VERSIONING.md`, `CHANGELOG.md`. Language 4.1 → 5.0 major breaking entry.
- **Shipped skills** — `skills/agent-linter/prompts/refs/finding_catalog.prompt` (AL930 + AL200), `skills/agent-linter/prompts/refs/examples.prompt` (before/after pair), `skills/doctrine-learn/prompts/refs/authoring_patterns.prompt` (new row), plus the doctrine-learn examples ladder.
- **Example corpus** — `examples/29_enums` (existing enum decl reference), `examples/79_final_output_output_schema` (existing `type: enum` + `values:` pattern), `examples/137`/`138` (recent carrier/shape patterns for precedent). New `examples/139_...` lands one end-to-end manifest-backed case.

### Diagnostic codes inventory

- E276 — missing decl (generic) — `doctrine/_compiler/resolve/refs.py:506`.
- E281 — missing symbol — `refs.py:499`.
- E299 — generic output-schema compile error — used across `resolve/output_schemas.py`.
- E317 — review branch binding — `validate/review_branches.py:474`.
- E318 — output structure — `validate/output_structure.py:47`.
- E319 — output selector — `compile/output_selectors.py:124`.
- Next unused: **E320**.

### Compatibility posture (grounded)

- For the three output-schema surfaces: **breaking change.** Existing `type: string` + builtin primitives still parse. The inline `type: enum` + `values:` form and the legacy `type: string` + `enum:` form are both **deleted** and no longer parse. `type: <EnumName>` resolves through the new shared helper to the enum decl; unknown CNAME raises E320 instead of silently emitting `{"type": "CNAME"}`.
- For prose-only surfaces (readable `row_schema`, `item_schema`, `table column`, record scalar): structured `type:` slots are added alongside existing prose body lines. Programs that only used prose keep parsing; the `type:` slot is new capability, not a removal. The language-level change here is additive on its own, but combined with the deleted secondary forms the whole pass is breaking. Language 4.1 → **5.0** major bump.

### Behavior-preservation signals already available

- Manifest-backed `examples/**/cases.toml` render_contract cases — every pre-existing `examples/*/ref/**` output must remain byte-identical after this change. `make verify-examples` is the behavior-preservation spine.
- `tests/test_emit_docs.py`, `tests/test_compile_diagnostics.py`, `tests/test_parser_source_spans.py` are the relevant unit signal surfaces.

### Capability-first check

- This is a compile-time language change, not an agent/LLM behavior change. Capability-first ladder does not apply. The "prompt-fixed vs. grounded" distinction is relevant only to the *downstream* psflows refactor (out of scope here) and to the agent-linter finding AL930 (which will teach authors to prefer the structured form).

## 3.3 Decision gaps that must be resolved before implementation

**All decision gaps resolved 2026-04-19 by explicit user direction ("the breaking change that gets us to max elegance"). Answers are captured inline below and in Section 10. Preserved as history so later stages can see what was asked and why the answer was chosen.**

### Blocker #1: scope of the grammar extension — RESOLVED (Path A, universal)

The plan's North Star says: "`psflows/lesson_plan`'s `step_role` vocabulary can be expressed as one `enum` decl plus one `type:` annotation." This only holds if `step_role` surfaces through an authoring surface that *accepts* `type:`. Research finds:

- **Only output-schema surfaces accept `type:` today.** If psflows's `step_role` is in an `output schema` (critic output, structured emit), today's grammar already accepts `type: <CNAME>` — we only need resolver + emit work, no new grammar. Narrow fix.
- **Readable `row_schema` / `table column` / record scalars are prose-only today.** If psflows's `step_role` is in a readable row_schema body (describing a table column's semantics to the model in prose), the fix requires **adding a structured body grammar to every prose-only surface**. This is a real language extension, each surface a separate grammar + IR + resolve + emit change, not one shared fragment.

**Repo evidence checked.** The `../psflows` tree is read-only and cannot be edited from this repo, but excerpts are allowed. The user's prior message showed `step_role` as prose inside a step block (`step_role values are introduce | practice | test | capstone ...`); that prose-form tells us how authors describe it today but not which authoring surface they *would* use if typed bodies existed.

**Default recommendation.** Commit the universal sweep (Path A: extend structured bodies to every prose-only surface where typed values are authoring-natural — readable row_schema / item_schema / table column / record scalar). Section 0 already makes consistency load-bearing. Narrowing now ("only output schema") would leave readable row_schema users exactly where they started.

**Answer needed.** Confirm: should this plan extend structured `type:` slots to readable `row_schema`, readable `item_schema`, readable `table column`, and record scalar — a real language extension — or land only the narrow output-schema fix? The elegance claim in TL;DR assumes the broader answer; if the user wants the narrow fix only, TL;DR and Section 0 need correction before `deep-dive`.

**Resolution.** Path A — universal extension. Add structured `type:` slots to every prose-only field-shaped surface (readable `row_schema` entry, readable `item_schema` entry, readable `table` column, record scalar) and tighten the three existing output-schema surfaces. No narrow fix.

### Blocker #2: silent-malformed-schema latent bug — RESOLVED (fail-loud)

Current behavior: `type: NonBuiltin` on `output_schema_field` today silently writes `{"type": "NonBuiltin"}` into the emitted JSON schema. No diagnostic. No existing example exercises this, so it has not been caught. Fixing this as part of this plan (raising E320 on unknown type names) is the right move for fail-loud, but it is a **behavior change**: any existing downstream Doctrine program that accidentally wrote a non-builtin CNAME will newly fail to compile.

**Default recommendation.** Raise E320 on unknown type names as part of this plan; classify as a fail-loud-fix, not breaking. Record in Decision Log. Acknowledge it in CHANGELOG as "strictens previously-silent malformed type names."

**Answer needed.** Accept this posture, or require a probe of downstream repos first? For the shipped corpus in `examples/` the probe is trivial (`make verify-examples` will surface any affected case).

**Resolution.** Raise E320 on unknown CNAME. The latent bug dies in this pass. Classified as a fail-loud fix. Breaking change, recorded in CHANGELOG.

### Blocker #3: reuse vs. new diagnostic code — RESOLVED (E320 + reuse E276/E281)

E276 already covers missing-decl cases. The Explore agent found E320 unused. Proposed: reuse E276 when the CNAME does not resolve at all, and mint **E320** specifically for "type ref resolves to a decl but the decl is not an enum" (e.g., `type: StepArcTable` where `StepArcTable` is a record). This gives authors a pointed hint instead of a generic missing-decl error.

**Resolution.** Mint E320 for "type ref resolves to a decl that is not an enum, or CNAME is neither builtin nor a known enum." Reuse E276/E281 for "name does not resolve at all."

### Blocker #4: kill secondary enum forms — RESOLVED (delete both)

Added by user direction: "the breaking change that gets us to max elegance." Three forms for one concept is not elegant. The canonical form is `enum X: ...` decl + `type: X`. Both of these are **deleted** in this pass:

- Inline form: `type: enum` + `values:` block — grammar productions `output_schema_values_block` (`doctrine.lark:~810`) and the `type: enum` normalization branch at `output_schemas.py:1636-1671`.
- Legacy form: `type: string` + `enum:` block — grammar production `output_schema_enum_block` (`doctrine.lark:~812`) and the legacy-enum normalization branch at `output_schemas.py:1703-1716`.

Every shipped example using either form is migrated to the canonical form in this pass. Each deleted form gets a "no longer parses" manifest-backed compile-fail case.

<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

**Grammar (shipped source of truth).** `doctrine/grammars/doctrine.lark`.

- Structured field-shaped surfaces (accept `type: <CNAME>` today):
  - `output_schema_field` at `:753`, `output_schema_route_field` at `:754`, `output_schema_def` at `:755`.
  - Shared item body `output_schema_item_body: _INDENT output_schema_item_line+ _DEDENT` at `:763`.
  - Type slot `output_schema_type_stmt: "type" ":" CNAME _NL?` at `:793`. Grammar accepts any CNAME — no whitelist at parse time.
  - Form A (inline enum) carrier `output_schema_values_block: "values" ":" _NL _INDENT output_schema_enum_value+ _DEDENT` at `:805`, registered in `output_schema_item_line` at `:777`.
  - Form B (legacy enum) carrier `output_schema_enum_block: "enum" ":" _NL _INDENT output_schema_enum_value+ _DEDENT` at `:804`, registered in `output_schema_item_line` at `:776`.
- Prose-only field-shaped surfaces (no structured `type:` slot today):
  - `readable_table_column` at `:556` with body `readable_table_column_body: _INDENT block_lines _DEDENT` at `:557`.
  - `readable_inline_schema_item` at `:565` with body `readable_inline_schema_item_body: _INDENT block_lines _DEDENT` at `:566`. Grammar does not distinguish `row_schema` versus `item_schema` at the item level — the same rule serves both via `readable_row_schema_block` at `:554` and `readable_item_schema_block` at `:527`.
  - `readable_property_item` at `:530` / body at `:531`.
  - `readable_definition_item` at `:534` / body at `:535`.
  - `record_keyed_item` at `:915` / body `record_item_body: _INDENT record_body _DEDENT` at `:917`.
  - `output_record_keyed_item` at `:862` / body `output_record_item_body: _INDENT output_record_body _DEDENT` at `:866`.
  - Override variants `override_record_keyed_item` at `:860`.

**IR model (shipped source of truth).** `doctrine/_model/`.

- `doctrine/_model/io.py`
  - `OutputSchemaField(key, title, items)` at `:269`. Lowering reads type/enum from `items`.
  - `OutputSchemaDef(...)` at `:277`.
  - `OutputSchemaRouteField(...)` at `:293`.
  - `OutputShapeSelectorConfig.enum_ref: NameRef` at `:252` — precedent for IR-level resolved enum refs.
  - `EnumDecl(name, title, members)` at `:502`, `EnumMember(key, title, wire)` at `:490`.
- `doctrine/_model/readable.py`
  - `ReadableDefinitionItem(key, title, body)` at `:21` — no type field.
  - `ReadablePropertyItem(key, title, body)` at `:29` — no type field.
  - `ReadableSchemaEntry(key, title, body: tuple[ProseLine, ...])` at `:43` — no type field. Serves both `row_schema` and `item_schema` entries.
  - `ReadableTableColumn(key, title, body)` at `:65` — no type field.
- Record scalars flow through `doctrine/_model/` record types (`RecordScalar` via `record_keyed_item` resolution). No type field today.

**Resolver.** `doctrine/_compiler/resolve/`.

- `output_schemas.py` owns the three structured surfaces.
  - Builtin whitelist constant at `:17-23`: `{"array", "boolean", "integer", "null", "number", "object", "string"}` — **defined but not enforced** against `parts.type_name`.
  - `_OutputSchemaNodeParts` container with `type_name: str | None` at `:41`, `enum_values`, `legacy_enum_values` fields used by Form A / Form B normalization.
  - `_collect_output_schema_node_parts(...)` at `:1350` — walks `output_schema_item_line` children, stores `type` on `parts.type_name` at `:1359`.
  - `_normalize_output_schema_inline_enum(...)` at `:1629` — when `parts.type_name == "enum"`, harvests `parts.enum_values` from the `values:` block and rewrites `parts.type_name = "string"` at `:1671`.
  - Legacy-enum branch at `:1703-1716` — when Form B is present, merges `parts.legacy_enum_values` into `parts.enum_values`.
  - Lowering `_lower_output_schema_parts(...)` around `:1094-1190` writes `schema["type"] = parts.type_name` at `:1109` without validating the CNAME, and writes `schema["enum"] = list(parts.enum_values)` at `:1190` when an enum-vocabulary was harvested.
- `refs.py` owns decl-name resolution.
  - `_resolve_enum_ref(ref, *, unit) -> tuple[IndexedUnit, EnumDecl]` at `:513` — raising variant.
  - `_try_resolve_enum_decl(ref, *, unit) -> EnumDecl | None` at `:1031` — safe lookup.
  - E276 raised at `:506` (local decl missing), E281 at `:499` (imported decl missing).
- Prose-only surfaces bypass any type resolution because there is no type slot to resolve.

**Validator.** `doctrine/_compiler/validate/__init__.py`.

- `_json_schema_meaning(field_schema, *, root_schema) -> str` at `:271` — helper used to construct the human "meaning" sentence shown in validator error messages when a schema field has no description.
- When no description exists and `field_schema["enum"]` is present, it emits `f"One of {rendered}."` at `:292`.
- When description *is* present, the enum vocabulary is dropped from the meaning string entirely; the rendered docs downstream do not re-add it.

**Emit.** `doctrine/emit_docs.py`, `doctrine/emit_common.py`, `doctrine/emit_flow.py`.

- `emit_docs.py` renders each readable table/row/property/definition node and each output-schema surface.
- Rendered columns and schema-entry descriptions today are pure prose (`body` → prose lines). There is no "Valid values:" line anywhere for readable tables or record scalars.
- Output-schema rendering reads `schema["enum"]` already and renders enum values as part of the JSON-schema-style output; the human-prose "Valid values:" line is not consistent with the readable table renderer.

## 4.2 Control paths (runtime)

**Parse → Resolve → Lower → Emit for output-schema `type: <CNAME>` today.**

1. Parser (`doctrine/parser.py` via Lark) produces a parse tree. `output_schema_type_stmt` captures any CNAME without grammar-level validation.
2. Session compile (`doctrine/_compiler/session.py`) walks the parse tree per unit.
3. `_collect_output_schema_node_parts` (at `output_schemas.py:1350`) calls into each `output_schema_item_line`. Lines with `key == "type"` store `value` into `parts.type_name` at `:1359`. Lines with `key == "values"` store Form A enum values; lines with `key == "enum"` store Form B legacy enum values.
4. `_normalize_output_schema_inline_enum` rewrites `parts.type_name` from `"enum"` to `"string"` when Form A was used; the legacy-enum branch does the same semantic job for Form B.
5. Lowering `_lower_output_schema_parts` writes `schema["type"] = parts.type_name` **without** checking the builtin whitelist. If `parts.type_name` was `"StepRole"`, `schema["type"]` becomes `"StepRole"` and flows downstream as malformed JSON schema with no diagnostic.
6. `emit_docs.py` renders the schema; `schema["enum"]` (when present) is shown; `schema["type"]` (however malformed) is shown verbatim.

**Parse → Resolve → Emit for prose-only surfaces today.**

1. Parser produces `readable_inline_schema_item` / `readable_table_column` / `record_keyed_item` with a prose body.
2. Resolver builds `ReadableSchemaEntry(key, title, body: tuple[ProseLine, ...])` or the equivalent readable/record IR with prose lines only.
3. Emit walks prose lines verbatim. There is no type resolution, no enum lookup, no "Valid values:" synthesis.
4. Authors who want to express a fixed vocabulary write pipe-list prose inside the body. Critic agents restate the same vocabulary as a prose gate check. Two copies drift.

## 4.3 Object model + key abstractions

- **Enum decl**: `EnumDecl(name: str, title: str, members: tuple[EnumMember, ...])`, `EnumMember(key, title, wire)`. Wire value is the scalar that appears in emitted JSON. This abstraction is complete and correct today.
- **Output-schema field**: `OutputSchemaField(key, title, items: tuple[OutputSchemaItem, ...])`. `items` is a heterogeneous list whose shape depends on what the author wrote — `type:` line, `values:` block, `enum:` block, `note:`, `format:`, etc. The IR does not carry a resolved type — resolution lives on the lowered JSON schema dict.
- **Readable schema entry / table column / property / definition**: carries `body: tuple[ProseLine, ...]`. Prose-only; no type semantics.
- **Record scalar**: `RecordScalar` carries `record_head` (string/path/name ref) plus a prose body. No type semantics.
- **Shared abstractions missing:** there is no `FieldTypeRef` union in the IR today. Each surface handles its own body. The builtin whitelist exists as a constant but is unused. The safe-enum-lookup helper exists but is only called from `_normalize_output_schema_inline_enum` (via Form A) and from output-shape-selector resolution — not from `type:` resolution.

## 4.4 Observability + failure behavior today

- **Silent malformed type.** `type: StepRole` on an output-schema field produces `{"type": "StepRole"}` in the emitted JSON schema. No diagnostic fires at parse or resolve. The malformed schema propagates into `emit_docs` rendered artifacts. Existing tests do not exercise this path.
- **No diagnostic for "type must be a known thing".** Authors get no feedback if they misspell a builtin (`type: strring`) or reach for an undeclared enum. Current-state compile success does not imply well-formed JSON schema.
- **No structural way to express fixed vocabulary on prose-only surfaces.** Authors encode vocabularies as pipe-list prose in the body. Critic agents restate the list as a prose gate. Silent drift is the norm.
- **Three forms for one concept on output-schema fields.** Authors encounter `type: enum` + `values:` (Form A), `type: string` + `enum:` (Form B, not used in shipped corpus), and `enum X: "..."` + `type: X` (Form C, canonical but not currently wired to `type:` on any surface). Form A and Form B silently normalize to the same JSON schema; Form C does not compile today (the `type: X` with X as enum decl name raises no error but silently emits `{"type": "X"}`).

## 4.5 UI surfaces (ASCII mockups, if UI work)

N/A — language-level change.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

**New compiler module.** `doctrine/_compiler/resolve/field_types.py` (or `doctrine/_compiler/resolve/types.py`). Owns one shared entrypoint that every field-shaped surface calls.

```python
# doctrine/_compiler/resolve/field_types.py (new)

BUILTIN_TYPE_NAMES = frozenset({
    "array", "boolean", "integer", "null", "number", "object", "string",
})

@dataclass(frozen=True)
class BuiltinTypeRef:
    name: str  # one of BUILTIN_TYPE_NAMES

@dataclass(frozen=True)
class EnumTypeRef:
    ref: NameRef      # the original CNAME reference with source span
    decl: EnumDecl    # the resolved enum decl (from _resolve_enum_ref)

FieldTypeRef: TypeAlias = BuiltinTypeRef | EnumTypeRef

def resolve_field_type_ref(
    name: str,
    *,
    span: SourceSpan,
    unit: IndexedUnit,
) -> FieldTypeRef:
    """
    Resolve `type: <name>` on any field-shaped surface.

    - name is a builtin primitive -> BuiltinTypeRef
    - name resolves to an EnumDecl (via _try_resolve_enum_decl) -> EnumTypeRef
    - name does not resolve -> raise E320 via diagnostics.emit
    - name resolves to a non-enum decl -> raise E320
    """
```

**Grammar changes.** `doctrine/grammars/doctrine.lark`.

- **Delete** `output_schema_values_block` (line `:805`) and its registration in `output_schema_item_line` (line `:777`). Delete `output_schema_enum_block` (line `:804`) and its registration (line `:776`). Delete the `output_schema_enum_value` helper (line `:806`) if it has no other users after these deletions.
- **Extend** each prose-only field-shaped body rule to allow a structured `type:` statement alongside prose. The cleanest form reuses a new shared fragment `typed_field_body_line`:

  ```lark
  typed_field_body_line: output_schema_type_stmt
                       | prose_line _NL?
  readable_inline_schema_item_body: _INDENT typed_field_body_line+ _DEDENT
  readable_table_column_body: _INDENT typed_field_body_line+ _DEDENT
  ```

  `record_keyed_item` / `output_record_keyed_item` bodies wrap `record_body` / `output_record_body`. The type slot goes into a new `record_scalar_head_line` alternative that fires only when the `record_head` is a `string` and the body is authoring a scalar field (not a nested record). Deep-dive design: add `typed_field_body_line` as an alternative in `record_item_body` and `output_record_item_body`; the resolver enforces that it can only appear when the record head is a scalar. Exact production wording is a phase-plan implementation detail.
- `output_schema_type_stmt` grammar rule at `:793` stays unchanged. Only the resolver's interpretation tightens.

**IR model changes.** `doctrine/_model/io.py` and `doctrine/_model/readable.py`.

- Add `type_ref: FieldTypeRef | None` to:
  - `OutputSchemaField` (`io.py:269`).
  - `OutputSchemaRouteField` (`io.py:293`).
  - `OutputSchemaDef` (`io.py:277`).
  - `ReadableSchemaEntry` (`readable.py:43`).
  - `ReadableTableColumn` (`readable.py:65`).
  - Record scalar IR (exact class identified in phase-plan implementation; likely a new `RecordScalar` or an extension of the existing record-keyed-item carrier).
- **Do not** add `type_ref` to `ReadablePropertyItem` or `ReadableDefinitionItem` — these are "glossary/label" nodes, not field-shaped slots. Section 0.3 excluded them implicitly; record here explicitly: they stay prose-only. If future demand surfaces, a follow-up extension can revisit.
- Remove legacy-enum-values / inline-enum-values carrier fields from `_OutputSchemaNodeParts` (`output_schemas.py:41`). `parts.enum_values` becomes read-only from the resolved `type_ref.decl.members` at lowering time.
- `FieldTypeRef`, `BuiltinTypeRef`, `EnumTypeRef` live alongside the helper in `doctrine/_compiler/resolve/field_types.py` (or re-exported from `doctrine/_model/` if the convention prefers model-side residence; this is a convention call for phase-plan).

**Validator / emit changes.** `doctrine/_compiler/validate/__init__.py`, `doctrine/emit_docs.py`, `doctrine/emit_common.py`.

- Extend `_json_schema_meaning` at `validate/__init__.py:271` to append `One of <values>.` to the description when both description and enum are present. Direct benefit: existing output-schema fields with both a `note:` and an enum vocabulary gain a rendered valid-values line without a ref-bump. Compatible with behavior-preservation: previously the enum was dropped when description existed.
- Add a shared rendering helper in `doctrine/emit_common.py`, e.g. `render_valid_values_line(type_ref: FieldTypeRef | None) -> str | None`. Returns `"Valid values: a, b, c."` when `type_ref` is an `EnumTypeRef`; `None` otherwise (builtins and untyped fields render nothing). Uses the enum members' wire values in declared order.
- `emit_docs.py` readable-table-column renderer, readable-schema-entry renderer, and record-scalar renderer each call `render_valid_values_line(entry.type_ref)` and, when non-None, emit it as a description-adjacent line. Output-schema surfaces continue to render enum vocabularies through their existing JSON-schema path (now populated via the resolved `type_ref`).

**Diagnostic catalog.** `docs/COMPILER_ERRORS.md`.

- New entry **E320**: "Field `type:` references unknown name: <name>. Declare an `enum <name>` or use a builtin primitive (string, integer, number, boolean, object, array, null)."
- Fired from `resolve_field_type_ref` in `field_types.py` when the CNAME is neither a builtin nor resolves to an `EnumDecl` (covers "not found" via underlying E276/E281 passthrough **and** "found but not an enum" via a pointed E320 message).
- Phase-plan decides the exact split: E320 for "resolved to non-enum decl" only, with E276/E281 passthrough for "name not resolvable"; or E320 for all unknown-type-CNAME cases with a single entrypoint.

## 5.2 Control paths (future)

**Parse → Resolve → Lower → Emit (unified across all field-shaped surfaces).**

1. Parser produces the field-shaped node. Grammar allows `type: <CNAME>` on every surface listed in Section 0.2.
2. Resolver collects the item/body lines. When a `type:` line is present, the resolver calls `resolve_field_type_ref(name, span=..., unit=...)` and stores the returned `FieldTypeRef` on the IR `type_ref` field.
3. If `resolve_field_type_ref` raises E320, compilation fails loudly with a message that names the offending CNAME, points at the source span, and lists valid builtins.
4. Lowering (output-schema surfaces): when `type_ref` is `EnumTypeRef`, populate `schema["type"] = "string"` and `schema["enum"] = [m.wire for m in type_ref.decl.members]`. When `type_ref` is `BuiltinTypeRef`, populate `schema["type"] = type_ref.name`. When `type_ref` is `None`, use existing untyped logic.
5. Emit (all surfaces): each renderer calls `render_valid_values_line(type_ref)` and emits the resulting prose line immediately after the field description (when both present) or as the description (when no prose body). Output-schema's existing JSON-schema rendering path keeps working; the readable/record surfaces gain the uniform "Valid values:" line.

**No parallel resolver per surface.** Every `type:` CNAME routes through `resolve_field_type_ref`. This is the single enforcement boundary for E320.

**No fallback.** If any surface's resolver skipped the helper for a backwards-compatibility shortcut, that would violate Section 0.5. The helper is the only way the IR gets a `type_ref`.

## 5.3 Object model + abstractions (future)

- **`FieldTypeRef` union** is the new load-bearing abstraction. It carries enough for emit (enum member wire values in order) and enough for validation (the original `NameRef` span) without leaking the full `EnumDecl` graph into unrelated passes.
- **`EnumDecl` stays the single source of truth** for what an enum is. The `FieldTypeRef` holds a reference, not a denormalized copy. Emit walks `type_ref.decl.members` at render time, so a rename of the decl would re-emit correctly.
- **Readable/record IR gains one optional field, not a whole new node type.** `ReadableSchemaEntry.type_ref`, `ReadableTableColumn.type_ref`, record scalar `type_ref` — all identical shape `FieldTypeRef | None`.
- **Output-schema IR unifies its type representation.** Today `_OutputSchemaNodeParts.type_name: str | None` is a raw CNAME. After: the parts carry a resolved `type_ref: FieldTypeRef | None`, and lowering reads from it.
- **Deleted abstractions.** `_OutputSchemaNodeParts.legacy_enum_values` and the Form A / Form B normalization branches in `_normalize_output_schema_inline_enum` go away. The builtin-whitelist constant moves to `field_types.py` and is now enforced.

## 5.4 Invariants and boundaries

- **One canonical form.** Exactly one way to express a field's fixed vocabulary across the whole language: declare `enum X: "..."` once; write `type: X` on the field. Any other form fails to compile under 5.0.
- **Single resolver entrypoint.** Every field-shaped surface's `type:` line routes through `resolve_field_type_ref`. No surface gets its own resolver. If a future author adds a new field-shaped surface, the wiring pattern is: "store span + CNAME during parse, call the shared helper during resolve, emit via `render_valid_values_line`."
- **Fail-loud on unknown CNAME.** `resolve_field_type_ref` raises E320 (or passes through E276/E281) at compile time. No silent `{"type": "Whatever"}` emit anywhere in the compiler output.
- **`FieldTypeRef` is immutable and never denormalized.** Emit reads through the ref to the live `EnumDecl`. Rename or reorder of members in the enum decl propagates automatically on recompile.
- **Grammar boundary.** Structured `type:` lives alongside prose; prose is not deleted. Authors who want pure prose bodies keep them. Authors who want typed vocabulary write one extra line.
- **Emit boundary.** Valid-values rendering goes through `render_valid_values_line` in `emit_common.py`. Surface-specific emit code calls the helper and inserts its line in the right textual slot. No surface rolls its own vocabulary line.
- **Examples are the proof.** Every shipped example that previously used Form A or Form B is migrated in-pass. Each deleted form has a manifest-backed compile-fail case that locks the removal in.
- **Prose-only escape hatch.** `ReadablePropertyItem` and `ReadableDefinitionItem` stay prose-only by design (glossary/label nodes, not field-shaped). Explicit non-goal; no E320 applies to their bodies.
- **`fallback_policy: forbidden`.** No runtime shim, no parser-side "accept Form A for one more release," no resolver-side "silently coerce unknown CNAME to string." Deleted forms stay deleted. Invariant violations are compile-time hard stops.

## 5.5 UI surfaces (ASCII mockups, if UI work)

N/A.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar | `doctrine/grammars/doctrine.lark` | `output_schema_values_block` (`:805`) + registration (`:777`) | Form A enum carrier parses | Delete production and registration | One canonical form | — | `tests/test_output_schema_surface.py`, `tests/test_output_schema_lowering.py`, `tests/test_final_output.py`, `tests/test_compile_diagnostics.py` |
| Grammar | `doctrine/grammars/doctrine.lark` | `output_schema_enum_block` (`:804`) + registration (`:776`) | Form B legacy enum carrier parses | Delete production and registration | One canonical form; zero shipped uses | — | same four tests |
| Grammar | `doctrine/grammars/doctrine.lark` | `output_schema_enum_value` (`:806`) | Helper for deleted blocks | Delete if no other users after block deletions | Dead rule | — | none direct |
| Grammar | `doctrine/grammars/doctrine.lark` | `readable_inline_schema_item_body` (`:566`) | `_INDENT block_lines _DEDENT` prose only | Expand to `_INDENT typed_field_body_line+ _DEDENT` that allows `output_schema_type_stmt` alongside prose | Add structured type slot to row_schema + item_schema | New `typed_field_body_line` fragment | `tests/test_readable.py` (or equivalent), parser source-span tests |
| Grammar | `doctrine/grammars/doctrine.lark` | `readable_table_column_body` (`:557`) | Prose only | Same expansion | Add structured type slot to table columns | Same fragment | same tests |
| Grammar | `doctrine/grammars/doctrine.lark` | `record_keyed_item` (`:915`) / `output_record_keyed_item` (`:862`) body rules | Prose only scalar bodies | Allow `typed_field_body_line` when head is `string` | Add structured type slot to record scalars | Same fragment, scoped to scalar heads | record-surface tests |
| Grammar | `doctrine/grammars/doctrine.lark` | `output_schema_type_stmt` (`:793`) | CNAME accepted, unvalidated | Keep grammar rule; tighten resolver only | Resolver is the enforcement boundary | — | E320 tests |
| Resolver (new) | `doctrine/_compiler/resolve/field_types.py` | (new module) | n/a | Create `resolve_field_type_ref`, `FieldTypeRef`, `BuiltinTypeRef`, `EnumTypeRef`, `BUILTIN_TYPE_NAMES` | Single resolver entrypoint | `resolve_field_type_ref(name, span, unit) -> FieldTypeRef` raising E320 | new `tests/test_field_type_ref.py` |
| Resolver | `doctrine/_compiler/resolve/output_schemas.py` | builtin constant (`:17-23`) | Defined but unused | Move to `field_types.py`; delete local copy | Single source | — | — |
| Resolver | `doctrine/_compiler/resolve/output_schemas.py` | `_OutputSchemaNodeParts` (`:41`) | Carries `type_name`, `enum_values`, `legacy_enum_values` | Replace `type_name` with `type_ref: FieldTypeRef \| None`; delete `legacy_enum_values` | IR carries resolved ref | `FieldTypeRef` | `test_output_schema_surface.py`, `test_output_schema_lowering.py` |
| Resolver | `doctrine/_compiler/resolve/output_schemas.py` | `_collect_output_schema_node_parts` (`:1350`), `type:` capture (`:1359`) | Stores raw CNAME | Call `resolve_field_type_ref`; store `type_ref` | Single entrypoint | — | same tests |
| Resolver | `doctrine/_compiler/resolve/output_schemas.py` | `_normalize_output_schema_inline_enum` (`:1629`, `:1636-1671`) | Form A normalization | Delete Form A branch | Form A deleted | — | `test_output_schema_surface.py` |
| Resolver | `doctrine/_compiler/resolve/output_schemas.py` | legacy-enum branch (`:1703-1716`) | Form B normalization | Delete Form B branch | Form B deleted | — | same tests |
| Resolver | `doctrine/_compiler/resolve/output_schemas.py` | `_lower_output_schema_parts` (`:1094-1190`) | `schema["type"] = parts.type_name`; `schema["enum"] = list(parts.enum_values)` | Populate from `parts.type_ref`: builtin → `type` only; enum → `type="string"` + `enum=[m.wire for m in decl.members]` | Canonical lowering | — | `test_output_schema_lowering.py` |
| Resolver | `doctrine/_compiler/resolve/refs.py` | `_resolve_enum_ref` (`:513`), `_try_resolve_enum_decl` (`:1031`) | Existing helpers | Call from `resolve_field_type_ref` | Reuse | — | — |
| Resolver | `doctrine/_compiler/resolve/refs.py` | E276 (`:506`), E281 (`:499`) | Generic missing-decl | Reuse when CNAME does not resolve at all | Preserve existing catalog | — | diagnostic tests |
| Resolver | `doctrine/_compiler/resolve/` | (surface glue for readable/record) | No call site today | Add call to `resolve_field_type_ref` from each readable/record resolve path that surfaces `typed_field_body_line` | Single entrypoint | — | new per-surface tests |
| IR | `doctrine/_model/io.py` | `OutputSchemaField` (`:269`) | `(key, title, items)` | Add `type_ref: FieldTypeRef \| None` | Unified IR | — | `test_output_schema_surface.py` |
| IR | `doctrine/_model/io.py` | `OutputSchemaRouteField` (`:293`) | same | same | same | — | same |
| IR | `doctrine/_model/io.py` | `OutputSchemaDef` (`:277`) | same | same | same | — | same |
| IR | `doctrine/_model/readable.py` | `ReadableSchemaEntry` (`:43`) | `(key, title, body: tuple[ProseLine, ...])` | Add `type_ref: FieldTypeRef \| None` | Unified IR | — | `test_readable.py`, `test_emit_docs.py` |
| IR | `doctrine/_model/readable.py` | `ReadableTableColumn` (`:65`) | same | same | same | — | same |
| IR | `doctrine/_model/readable.py` | `ReadablePropertyItem` (`:29`), `ReadableDefinitionItem` (`:21`) | prose body, no type | **No change** — stay prose-only by design | Not field-shaped | — | — |
| IR | `doctrine/_model/` (record classes) | Record scalar carrier (exact class identified in phase-plan) | No type field | Add `type_ref: FieldTypeRef \| None` | Unified IR | — | record-surface tests |
| Validator | `doctrine/_compiler/validate/__init__.py` | `_json_schema_meaning` (`:271-293`) | Drops enum when description present | Append `One of <values>.` to description when enum present | Uniform "valid values" signal | — | new unit case |
| Emit | `doctrine/emit_common.py` | (new helper) | n/a | Add `render_valid_values_line(type_ref) -> str \| None` | Single rendering path | helper signature above | `test_emit_docs.py` unit cases |
| Emit | `doctrine/emit_docs.py` | readable-table-column renderer | Prose only | Call `render_valid_values_line(column.type_ref)` and insert line under description | Uniform emit | — | `test_emit_docs.py` |
| Emit | `doctrine/emit_docs.py` | readable-schema-entry renderer (row_schema + item_schema) | Prose only | Same | same | — | same |
| Emit | `doctrine/emit_docs.py` | record-scalar renderer | Prose only | Same | same | — | same |
| Emit | `doctrine/emit_docs.py` | output-schema renderer | Renders via JSON schema path | Keep JSON schema path; add human "Valid values:" line via shared helper for uniformity | Uniform emit | — | `test_emit_docs.py` |
| Emit | `doctrine/emit_flow.py` | Output-schema surfaces | Reads lowered JSON schema | No change expected; verify the new lowering path produces identical `schema["enum"]` ordering | Behavior preservation | — | `test_emit_flow.py` (and snapshot) |
| Diagnostics | `doctrine/diagnostics.py` | Catalog entries | Has E276, E281, E317, E318, E319; E320 unused | Register E320 with message template "Field `type:` references unknown name: <name>. Declare an `enum <name>` or use a builtin primitive (string, integer, number, boolean, object, array, null)." | New code | `docs/COMPILER_ERRORS.md` entry | `test_compile_diagnostics.py` (new manifest case) |
| Example | `examples/79_final_output_output_schema/prompts/AGENTS.prompt` | Form A at `:7-10` | `type: enum` + `values:` | Rewrite to `enum X: "..."` decl + `type: X` on the field | Form A deleted | — | `examples/79_.../cases.toml` (render_contract; ref/** regenerated) |
| Example | `examples/79_final_output_output_schema/prompts/optional_no_example/AGENTS.prompt` | Form A at `:7-10` | same | same | same | — | same manifest |
| Example | `examples/79_final_output_output_schema/prompts/invalid_invalid_example/AGENTS.prompt` | Form A at `:7-10` | same | same | same | — | same manifest |
| Example | `examples/85_review_split_final_output_output_schema/prompts/AGENTS.prompt` | Form A at `:3-6` | same | same | same | — | `examples/85_.../cases.toml` |
| Example | `examples/90_split_handoff_and_final_output_shared_route_semantics/prompts/AGENTS.prompt` | Form A at `:3-6` | same | same | same | — | `examples/90_.../cases.toml` |
| Example | `examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt` | Form A at `:8-11` | same | same | same | — | `examples/121_.../cases.toml` |
| Example (editor snap) | `editors/vscode/tests/snap/examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt` | cached snapshot | Form A | Regenerate snapshot after migration | Editor tests follow shipped corpus | — | `cd editors/vscode && make` |
| Example (editor snap) | `editors/vscode/tests/snap/examples/79_final_output_output_schema/prompts/AGENTS.prompt`, `.../OPTIONAL_NO_EXAMPLE.prompt` | cached snapshots with Form B test fixtures | Regenerate | Snapshots must reflect new shape | — | same as above |
| Example (new) | `examples/139_enum_typed_field_bodies/prompts/AGENTS.prompt` | n/a | n/a | Create; demonstrates typed `row_schema` column (primary motivating surface) using `enum X: "..."` + `type: X` | Primary proof | — | `examples/139_.../cases.toml` |
| Example (new) | `examples/139_enum_typed_field_bodies/cases.toml` | n/a | n/a | `render_contract` + `compile_fail` (unknown enum → E320) | Manifest-backed proof | — | `make verify-examples`, `make verify-diagnostics` |
| Example (new) | `examples/139_enum_typed_field_bodies/ref/**` | n/a | n/a | Generated expected artifacts | Proof outputs | — | — |
| Diagnostic smoke | `doctrine/_diagnostic_smoke/fixtures_final_output.py` | Form A / Form B fixtures | Exercises deleted forms | Migrate to canonical form; add E320 smoke fixture | Keep smoke coverage honest | — | `make verify-diagnostics` |
| Test | `tests/test_output_schema_surface.py` | Form A / Form B coverage | Asserts Form A / Form B compile | Rewrite: canonical form compiles; deleted forms now raise parse error | Lock removal in | — | direct |
| Test | `tests/test_output_schema_lowering.py` | Form A / Form B lowering | Asserts JSON schema from deleted forms | Rewrite to canonical form; assert same JSON schema values | Behavior preservation for migrated shape | — | direct |
| Test | `tests/test_final_output.py` | Form A / Form B fixtures | Uses deleted forms | Migrate fixtures | Same | — | direct |
| Test | `tests/test_compile_diagnostics.py` | Form A / Form B + diagnostics | Uses deleted forms | Migrate; add E320 cases; add "Form A no longer parses" + "Form B no longer parses" cases | Lock removal in | — | direct |
| Test | `tests/test_emit_docs.py` | Existing renderer tests | Prose-only on readable surfaces | Add cases for `type_ref` rendering on readable-schema-entry, readable-table-column, record-scalar, and output-schema surfaces (Valid values: line) | Emit uniformity | — | direct |
| Test | `tests/test_parser_source_spans.py` | Span coverage | Spans on existing nodes | Add spans for `typed_field_body_line` on readable/record surfaces | Grammar extension | — | direct |
| Test (new) | `tests/test_field_type_ref.py` | n/a | n/a | Unit tests for `resolve_field_type_ref`: builtin hit, enum hit, non-builtin non-enum CNAME → E320, enum decl via import, span carried through | Single-entrypoint coverage | — | direct |
| Docs | `docs/LANGUAGE_REFERENCE.md` | Existing `type: enum` + `values:` guidance, schema surface sections | Rewrite the "output schema field" subsection to the canonical form; add new subsection "Typed field bodies" covering row_schema / item_schema / table column / record scalar with example snippets; cross-ref example 139 | Single canonical source | — | doc-diff |
| Docs | `docs/LANGUAGE_DESIGN_NOTES.md` | Prose-by-design claim for readable bodies | Add decision note: "One canonical form for field vocabularies; prose-only escape hatch retained on glossary/label nodes (property/definition)." | Honest design trail | — | doc-diff |
| Docs | `docs/COMPILER_ERRORS.md` | Diagnostic catalog | Add E320 entry with message template and an authored-form example | Catalog completeness | — | `make verify-diagnostics` (catalog consistency) |
| Docs | `docs/VERSIONING.md` | Bump policy text | Add 4.1 → 5.0 major breaking entry; name deleted forms and the migration | Required by AGENTS.md for public compatibility | — | `make verify-package` |
| Docs | `CHANGELOG.md` | Version history | Add 5.0 entry: (a) deleted `type: enum` + `values:` form, (b) deleted `type: string` + `enum:` form, (c) tightened `type:` to fail loud with E320, (d) added structured `type:` to row_schema / item_schema / table column / record scalar, (e) migration: declare `enum X: "..."` then write `type: X` | Required | — | `make verify-package` |
| Docs | `docs/AGENT_IO_DESIGN_NOTES.md` | References Form A ("type: enum") | Update to canonical form | Consistency | — | doc-diff |
| Docs | `docs/README.md` | Index lines | Verify no stale references; update if typed field bodies are indexed | Consistency | — | doc-diff |
| Skill source | `skills/agent-linter/prompts/refs/finding_catalog.prompt` | Finding table + sections | Add AL930 "Inlined Vocabulary Should Be An Enum-Typed Field" row + full section; extend AL200 section to name pipe-list vocabularies as a canonical duplicate-rule shape | User-confirmed scope | — | regenerate curated; diff `skills/.curated/agent-linter/references/finding-catalog.md` |
| Skill source | `skills/agent-linter/prompts/refs/examples.prompt` | Example pairs | Add AL930 before/after pair (prose pipe-list in role vs. enum decl + typed field) | Same | — | regenerate; diff `skills/.curated/agent-linter/references/examples.md` |
| Skill source | `skills/doctrine-learn/prompts/refs/authoring_patterns.prompt` | Task-first chooser | Add row: "I need a field's value to come from a fixed vocabulary → declare `enum X` and set the field's `type: X`. Do not list values as prose. See `examples/139_enum_typed_field_bodies`." | User-confirmed scope | — | regenerate; diff `skills/.curated/doctrine-learn/references/authoring-patterns.md` |
| Skill source | `skills/doctrine-learn/prompts/refs/outputs_and_schemas.prompt` | Form A guidance | Rewrite "type: enum" + "values:" passages to canonical form | Consistency | — | regenerate curated |
| Skill source | `skills/doctrine-learn/prompts/refs/` (examples ladder) | Ladder entry | Add example 139 entry (exact filename verified during phase-plan) | User-confirmed scope | — | regenerate |

## 6.2 Migration notes

- **Canonical owner path / shared code path.** `doctrine/_compiler/resolve/field_types.py` with `resolve_field_type_ref`, `FieldTypeRef`, `BuiltinTypeRef`, `EnumTypeRef`, `BUILTIN_TYPE_NAMES`. Every field-shaped surface calls this single entrypoint. Emit calls `render_valid_values_line` in `doctrine/emit_common.py`. No other module owns `type:` resolution.
- **Deprecated APIs.** None. The two deleted forms are parser-level productions, not public APIs. Authors migrate by rewriting their `.prompt` files.
- **Delete list.**
  - `output_schema_values_block` (production + registration) in `doctrine/grammars/doctrine.lark`.
  - `output_schema_enum_block` (production + registration) in `doctrine/grammars/doctrine.lark`.
  - `output_schema_enum_value` helper if no other users.
  - `_OutputSchemaNodeParts.legacy_enum_values` and its collector in `doctrine/_compiler/resolve/output_schemas.py`.
  - Form A normalization branch at `output_schemas.py:1636-1671`.
  - Form B normalization branch at `output_schemas.py:1703-1716`.
  - Builtin-types constant at `output_schemas.py:17-23` (moves to `field_types.py`; local copy deleted).
  - Form A / Form B fixtures in `doctrine/_diagnostic_smoke/fixtures_final_output.py` (rewritten to canonical form, plus new E320 fixture).
  - Every Form A use in shipped `examples/` (`.prompt` files listed in the change map).
- **Adjacent surfaces tied to the same contract family.**
  - Output-schema JSON-schema lowering (already in scope).
  - Readable table / list / row_schema / item_schema / definition / property IR (two of six gain `type_ref`; two explicitly stay prose-only).
  - Record scalar IR.
  - Editor snapshot tests under `editors/vscode/tests/snap/examples/...` — regenerate after shipped-corpus migration.
  - Shipped skills (`agent-linter`, `doctrine-learn`) — user-confirmed in-scope.
- **Compatibility posture / cutover plan.** Clean cutover, breaking change. Language 4.1 → 5.0. No timeboxed bridge; no runtime shim; no parser-side legacy branch. Deleted forms fail to parse under 5.0. Authors migrate by rewriting. `CHANGELOG.md` documents the one-line migration: "replace `type: enum` + `values:` with a separate `enum` decl + `type: <EnumName>`; the legacy `type: string` + `enum:` form had no shipped users and is deleted outright."
- **Capability-replacing harnesses to delete or justify.** None — this is a compile-time language change, not an agent-runtime change.
- **Live docs / comments / instructions to update or delete.**
  - `docs/LANGUAGE_REFERENCE.md` — rewrite output-schema field subsection; add "Typed field bodies" subsection.
  - `docs/LANGUAGE_DESIGN_NOTES.md` — add one-canonical-form decision note.
  - `docs/COMPILER_ERRORS.md` — add E320.
  - `docs/VERSIONING.md` — 4.1 → 5.0 entry with breaking-change notes.
  - `CHANGELOG.md` — 5.0 entry.
  - `docs/AGENT_IO_DESIGN_NOTES.md` — Form A references updated to canonical form.
  - `docs/README.md` — verify index lines are not stale.
  - `examples/README.md` — add 139 if it indexes typed patterns (verify during phase-plan).
  - `skills/.curated/agent-linter/references/finding-catalog.md`, `skills/.curated/agent-linter/references/examples.md`, `skills/.curated/doctrine-learn/references/authoring-patterns.md` — regenerated from `.prompt` source; do not edit curated directly.
- **Behavior-preservation signals for refactors.**
  - `make verify-examples` across the migrated corpus; every pre-existing ref that is not a Form A / Form B migration target must be byte-identical.
  - For each migrated example, a resolver-level assertion test proves the emitted JSON schema `enum` list is byte-identical in value and order to the pre-migration output. This locks behavior preservation for the canonical form even though the source text changed.
  - `make verify-diagnostics` across the diagnostics catalog; E320 manifest case plus "Form A no longer parses" and "Form B no longer parses" manifest cases.
  - `make verify-package` for versioning surfaces.
  - `cd editors/vscode && make` for editor snapshot regeneration.
  - Scratch local conversion of `psflows/lesson_plan`'s `step_role` prose into the canonical form on this branch — compiles against the new grammar. **Read-only excerpt only; no file under `../psflows` is modified.**

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Output schema field | `output_schema_field` | `type_ref` + shared resolver + shared emit line | Already three forms drift; deletes Form A + Form B | **include** |
| Output schema route field | `output_schema_route_field` | same | Same drift risk | **include** |
| Output schema def | `output_schema_def` | same | Same drift risk | **include** |
| Readable row_schema entry | `readable_inline_schema_item` used under `row_schema:` | same | Primary motivating surface; `step_role`-class fields | **include** |
| Readable item_schema entry | `readable_inline_schema_item` used under `item_schema:` | same | Shares the grammar rule with row_schema — free inclusion | **include** |
| Readable table column | `readable_table_column` | same | Typed table columns are the natural authoring surface for fixed vocabularies | **include** |
| Record scalar | `record_keyed_item` / `output_record_keyed_item` (scalar-head variants) | same | Record scalars are field-shaped and currently prose-only | **include** |
| Readable property item | `readable_property_item` | same | Glossary/label node, not field-shaped | **exclude** (Section 0.3 rationale: not field-shaped) |
| Readable definition item | `readable_definition_item` | same | Glossary/label node, not field-shaped | **exclude** (Section 0.3 rationale: not field-shaped) |
| Readable list keyed item | `readable_list_keyed_item` | same | No body at all; reference-only | **exclude** (no body) |
| Readable footnote item | `readable_footnote_item` | same | No body at all | **exclude** (no body) |
| Semantic field binding (review carrier) | `semantic_field_binding` | same | Reference-only binding; no body | **exclude** (reference-only) |
| Skill entry bind item | `skill_entry_bind_item` | same | Reference-only | **exclude** (reference-only) |
| Enum member | `enum_member` | same | Enum members ARE the vocabulary; a `type:` slot on a member is semantically self-referential | **exclude** (semantically N/A) |
| Module-qualified type refs | `type: Module.EnumName` | CNAME `.` CNAME grammar extension | Author friction if an enum is imported; today only bare CNAME resolves | **defer** (explicit follow-up; Section 0.3) |
| Arbitrary value patterns | `type: pattern("ans-*")` or similar | Separate extension | Not a vocabulary; different concept | **exclude** (Section 0.3 non-goal) |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Shared field-type resolver, `FieldTypeRef` union, E320 diagnostic

Status: COMPLETE (audit 2026-04-19; landed in `fe8767c`; all six Checklist behaviors covered by `tests/test_field_type_ref.py`; `E320` row present in `docs/COMPILER_ERRORS.md:158`; `make verify-examples` and `make verify-diagnostics` green per worklog)

* Goal: establish the single compile-time entrypoint that every field-shaped surface will later call to resolve `type: <CNAME>`. Ship the helper, the union type, and the E320 diagnostic code in isolation so later phases can wire to a stable API.
* Work: create `doctrine/_compiler/resolve/field_types.py` with `BUILTIN_TYPE_NAMES`, `BuiltinTypeRef`, `EnumTypeRef`, `FieldTypeRef = BuiltinTypeRef | EnumTypeRef`, and `resolve_field_type_ref(name, *, span, unit) -> FieldTypeRef`. Reuse `_try_resolve_enum_decl` at `doctrine/_compiler/resolve/refs.py:1031`. Register diagnostic code E320 in `doctrine/diagnostics.py` with a message template naming the offending CNAME and listing valid builtins. Add the E320 entry to `docs/COMPILER_ERRORS.md`. The helper is not wired to any surface yet; shipped compilation is unaffected.
* Checklist (must all be done):
  - Create `doctrine/_compiler/resolve/field_types.py` exporting `BUILTIN_TYPE_NAMES`, `BuiltinTypeRef`, `EnumTypeRef`, `FieldTypeRef`, `resolve_field_type_ref`.
  - `BUILTIN_TYPE_NAMES` is exactly `{"array", "boolean", "integer", "null", "number", "object", "string"}`.
  - `resolve_field_type_ref` returns a `BuiltinTypeRef` for builtin names, an `EnumTypeRef` (carrying the original `NameRef` span plus the resolved `EnumDecl`) for names that resolve to an enum decl, and raises E320 for any other CNAME.
  - E320 is registered in `doctrine/diagnostics.py` and its message template lists the valid builtins plus the "declare `enum <name>`" hint.
  - `docs/COMPILER_ERRORS.md` carries the E320 entry (code, message template, example).
  - New `tests/test_field_type_ref.py` covers: builtin hit for each of the seven builtin names; enum hit for a same-unit enum decl; enum hit for an imported enum decl; E320 on a CNAME that resolves to a non-enum decl (e.g. a table); E320 on a CNAME that does not resolve anywhere; span is carried through on E320 to the source position of the CNAME.
  - The new module contains a brief comment at `resolve_field_type_ref` stating this is the single entrypoint for `type:` resolution across all field-shaped surfaces and that new surfaces must call it rather than rolling their own path.
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_field_type_ref` passes.
  - `make verify-diagnostics` remains green (no regressions from catalog registration).
  - `make verify-examples` remains green (helper is not wired yet).
* Docs/comments (propagation; only if needed):
  - `docs/COMPILER_ERRORS.md` E320 entry added in this phase so the diagnostic ships with code, not in a later doc sweep.
  - One-line canonical-boundary comment on `resolve_field_type_ref` stating the single-entrypoint invariant.
* Exit criteria (all required):
  - `doctrine/_compiler/resolve/field_types.py` exists with the five named exports.
  - E320 is registered and documented in `docs/COMPILER_ERRORS.md`.
  - `tests/test_field_type_ref.py` covers all six behaviors listed in Checklist and passes.
  - `make verify-examples` and `make verify-diagnostics` both green on the phase tip.
  - No other module imports the helper yet (grep check during implement is fine; this is a positive-value assertion on wiring, not a deletion check).
* Rollback: revert the new module, the E320 registration, the COMPILER_ERRORS.md entry, and the new test file. No other code changed.

## Phase 2 — Wire structured output-schema surfaces to the shared resolver

Status: IN PROGRESS (audit 2026-04-19; uncommitted partial work on branch)
Missing (code):
- New unit cases in `tests/test_output_schema_surface.py` and `tests/test_output_schema_lowering.py` covering (a) `type: <EnumName>` resolves + emits `schema["type"]="string"` and ordered `schema["enum"]`, (b) `type: <UnknownCNAME>` raises `E320`, (c) Form A / Form B byte-identical JSON schema compared with a Phase 1-tip golden.
- Parser source-span test proving `E320` carries the CNAME span when raised from the output-schema collector (Phase 1's test covers the helper in isolation, not the collector path).
- Phase 2 worklog entry recording green `make verify-examples` + `make verify-diagnostics` against the Phase 2 tip, then a Phase 2 commit so the frontier advances on a checkpoint, not on uncommitted local state.

* Goal: make every `type: <CNAME>` on `output_schema_field`, `output_schema_route_field`, and `output_schema_def` route through the shared helper. Kill the silent-malformed-schema latent bug (today `type: StepRole` silently writes `{"type": "StepRole"}`). Leave Form A and Form B working via their existing normalization branches so shipped examples continue to compile.
* Work: add `type_ref: FieldTypeRef | None` to `OutputSchemaField` (`doctrine/_model/io.py:269`), `OutputSchemaRouteField` (`:293`), and `OutputSchemaDef` (`:277`). Replace `_OutputSchemaNodeParts.type_name: str | None` with `type_ref: FieldTypeRef | None` at `doctrine/_compiler/resolve/output_schemas.py:41`. Update `_collect_output_schema_node_parts` at `output_schemas.py:1350` so the `key == "type"` capture at `:1359` calls `resolve_field_type_ref(value, span=..., unit=...)` and stores the `FieldTypeRef` on `parts.type_ref`. Update `_lower_output_schema_parts` around `:1094-1190`: when `parts.type_ref` is a `BuiltinTypeRef`, set `schema["type"] = parts.type_ref.name`; when it is an `EnumTypeRef`, set `schema["type"] = "string"` and `schema["enum"] = [m.wire for m in parts.type_ref.decl.members]`. Keep the Form A branch at `:1629-1671` and the Form B branch at `:1703-1716` intact — they set `parts.enum_values` and leave `parts.type_ref = None`; lowering prefers `parts.type_ref` and falls back to the existing enum-values path when `type_ref` is `None`. Net effect for this phase: `type: <EnumName>` compiles correctly; `type: <UnknownCNAME>` raises E320; Form A and Form B keep compiling unchanged.
* Checklist (must all be done):
  - `OutputSchemaField`, `OutputSchemaRouteField`, `OutputSchemaDef` each carry `type_ref: FieldTypeRef | None`.
  - `_OutputSchemaNodeParts.type_name` is replaced by `type_ref: FieldTypeRef | None`; all readers of `parts.type_name` are updated.
  - `_collect_output_schema_node_parts` at `output_schemas.py:1350` routes the `type:` capture through `resolve_field_type_ref` using the CNAME's source span.
  - `_lower_output_schema_parts` writes `schema["type"]` and `schema["enum"]` from `parts.type_ref` when present; falls back to the existing Form A / Form B enum-values path when `parts.type_ref is None`.
  - Form A (`type: enum` + `values:`) continues to parse and compile; its lowered JSON schema is byte-identical to before this phase for every shipped example that uses it.
  - Form B (`type: string` + `enum:`) continues to parse and compile; its lowered JSON schema is byte-identical to before this phase for every test fixture that uses it.
  - `type: <EnumName>` on any of the three structured surfaces resolves through the helper and produces `schema["type"] = "string"` plus `schema["enum"] = [m.wire ...]` in member order.
  - `type: <UnknownCNAME>` on any of the three surfaces raises E320 (previously silently compiled).
  - New unit test cases in `tests/test_output_schema_surface.py` and `tests/test_output_schema_lowering.py` cover: (a) `type: <EnumName>` resolves and emits expected JSON schema; (b) `type: <UnknownCNAME>` raises E320; (c) existing Form A / Form B cases still pass byte-identically.
* Verification (required proof):
  - `make verify-examples` green — every shipped example still compiles and every `ref/**` is byte-identical to main.
  - `make verify-diagnostics` green — existing diagnostics unchanged; new E320 path exercised by a targeted manifest case added in this phase or Phase 1 if convenient.
  - Unit tests listed in Checklist pass.
  - A targeted parser source-span test confirms E320 carries the CNAME span.
* Docs/comments (propagation; only if needed):
  - Brief comment at `_lower_output_schema_parts` noting the `type_ref`-preferred / fallback-to-enum-values shape and that the fallback path will go away in Phase 3.
* Exit criteria (all required):
  - All three structured output-schema IR classes carry `type_ref`.
  - `_collect_output_schema_node_parts` is the only module that calls `resolve_field_type_ref` for output-schema surfaces (single call site).
  - Every shipped `examples/**/ref/**` file is byte-identical to main after this phase's tip compiles.
  - The silent-malformed-type bug is dead: a new unit case proves `type: StepRole` (with `StepRole` neither builtin nor enum) raises E320.
  - `make verify-examples` and `make verify-diagnostics` both green.
* Rollback: revert IR field additions, resolver changes, and lowering switch. Phase 1 artifacts remain.

## Phase 3 — Delete Form A and Form B; migrate shipped examples; lock removal

* Goal: remove the two secondary enum forms from grammar, resolver, IR carrier, tests, and the shipped example corpus in one atomic cutover. Prove the migration preserves emitted JSON schema values via assertion tests, and lock the removal in with manifest-backed "no longer parses" cases. This is the breaking change.
* Work: delete `output_schema_values_block` (production at `doctrine/grammars/doctrine.lark:805`) and its registration in `output_schema_item_line` (`:777`); delete `output_schema_enum_block` (`:804`) and its registration (`:776`); delete `output_schema_enum_value` (`:806`) if it has no remaining users. Delete Form A normalization branch at `doctrine/_compiler/resolve/output_schemas.py:1636-1671` and the Form B branch at `:1703-1716`. Delete `_OutputSchemaNodeParts.legacy_enum_values` and any related `enum_values` collector logic that existed only to support the two deleted forms. Move `BUILTIN_TYPE_NAMES` from `output_schemas.py:17-23` to `doctrine/_compiler/resolve/field_types.py`; delete the local copy. Rewrite each of the six shipped Form A examples (`examples/79_final_output_output_schema/prompts/AGENTS.prompt` at `:7-10`, `.../optional_no_example/AGENTS.prompt` at `:7-10`, `.../invalid_invalid_example/AGENTS.prompt` at `:7-10`, `examples/85_review_split_final_output_output_schema/prompts/AGENTS.prompt` at `:3-6`, `examples/90_split_handoff_and_final_output_shared_route_semantics/prompts/AGENTS.prompt` at `:3-6`, `examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt` at `:8-11`) from `type: enum` + `values:` to a separate `enum` decl + `type: <EnumName>` on the field. Regenerate each example's `ref/**`. Migrate test fixtures in `tests/test_output_schema_surface.py`, `tests/test_output_schema_lowering.py`, `tests/test_final_output.py`, `tests/test_compile_diagnostics.py`, and `doctrine/_diagnostic_smoke/fixtures_final_output.py` off of Form A / Form B to the canonical form. Add a manifest-backed compile-fail case for each deleted form asserting it no longer parses, and add behavior-preservation assertion tests that check the emitted JSON schema `enum` list is byte-identical (value and order) between pre-migration output (captured from the Phase 2 tip) and post-migration output.
* Checklist (must all be done):
  - `doctrine/grammars/doctrine.lark` no longer contains `output_schema_values_block` or `output_schema_enum_block` productions or their registrations in `output_schema_item_line`.
  - `doctrine/grammars/doctrine.lark` no longer contains `output_schema_enum_value` if no other grammar rule references it.
  - `doctrine/_compiler/resolve/output_schemas.py` no longer contains the Form A normalization branch (previously at `:1636-1671`) or the Form B branch (previously at `:1703-1716`).
  - `_OutputSchemaNodeParts` no longer carries `legacy_enum_values` or any field whose only purpose was Form A / Form B support.
  - `BUILTIN_TYPE_NAMES` lives only in `doctrine/_compiler/resolve/field_types.py`.
  - Each of the six shipped Form A example files named in Work is rewritten to `enum X: "..."` decl + `type: X` on the field, using the canonical form.
  - Each rewritten example's `ref/**` files are regenerated and committed.
  - Test fixtures in `tests/test_output_schema_surface.py`, `tests/test_output_schema_lowering.py`, `tests/test_final_output.py`, and `tests/test_compile_diagnostics.py` no longer use Form A or Form B source text; each fixture uses the canonical form instead.
  - `doctrine/_diagnostic_smoke/fixtures_final_output.py` is migrated to the canonical form plus a new E320 smoke fixture.
  - A manifest-backed compile-fail case asserts the Form A source text no longer parses under 5.0 (minimal reproduction with `type: enum` + `values:`).
  - A manifest-backed compile-fail case asserts the Form B source text no longer parses under 5.0 (minimal reproduction with `type: string` + `enum:`).
  - A behavior-preservation assertion test (new, in `tests/` — e.g. `tests/test_enum_migration_preservation.py`) loads each of the six migrated examples, compiles it, and asserts the emitted JSON schema `enum` list matches a committed golden list (value and order). The golden list is captured from the Phase 2 tip before the source rewrites, not from the post-migration output, so the test actually locks the preservation claim rather than tautologically asserting the migrated output equals itself.
* Verification (required proof):
  - `make verify-examples` green across the migrated corpus.
  - `make verify-diagnostics` green, including the two "no longer parses" manifest cases and the E320 smoke fixture.
  - `tests/test_enum_migration_preservation.py` (or the chosen filename) passes, proving byte-identical JSON schema `enum` values and order for every migrated example.
  - `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_final_output tests.test_compile_diagnostics` passes.
* Docs/comments (propagation; only if needed): none in this phase; bulk doc updates live in Phase 7.
* Exit criteria (all required):
  - Grammar, resolver, IR, test fixtures, and the shipped example corpus no longer contain Form A or Form B source text or code paths.
  - Every migrated example's emitted JSON schema `enum` list is byte-identical (value and order) to the Phase 2 tip, asserted by the preservation test.
  - Both deleted forms have manifest-backed "no longer parses" cases that pass.
  - `make verify-examples` and `make verify-diagnostics` both green.
  - The single resolver entrypoint (Phase 1 helper) is now the only path by which `type:` resolves to an enum on output-schema surfaces.
* Rollback: revert grammar deletions, resolver deletions, IR field deletion, example source rewrites, `ref/**` regenerations, test fixture migrations, and the new preservation / compile-fail cases. Phase 2's helper wiring remains but falls back through the deleted Form A / Form B paths that would need to be restored with the revert.

## Phase 4 — Extend structured `type:` slot to prose-only field-shaped surfaces

* Goal: add a structured `type:` slot to `readable_inline_schema_item_body` (serves both `row_schema` and `item_schema` entries), `readable_table_column_body`, and record scalar bodies (`record_keyed_item`, `output_record_keyed_item` scalar-head variants). Wire each surface's resolve path through the shared helper so every field-shaped surface in the language now accepts the same canonical `type: <CNAME>` form. Prose bodies remain valid alongside the type slot. Glossary/label nodes (`readable_property_item`, `readable_definition_item`) stay prose-only by explicit design.
* Work: add a new grammar fragment `typed_field_body_line` that is an alternative of `output_schema_type_stmt` or a prose line. Expand `readable_inline_schema_item_body` at `doctrine/grammars/doctrine.lark:566` and `readable_table_column_body` at `:557` to use `_INDENT typed_field_body_line+ _DEDENT`. Expand `record_item_body` / `output_record_item_body` (at `:917` and `:866`) so that scalar-head record items (`record_keyed_item` with `record_head: string` at `:915`, and the matching `output_record_keyed_item` at `:862`) can include a `typed_field_body_line`. Add `type_ref: FieldTypeRef | None` to `ReadableSchemaEntry` at `doctrine/_model/readable.py:43`, `ReadableTableColumn` at `:65`, and the record scalar carrier IR class. Extend each surface's resolve path to collect the `type:` line and call `resolve_field_type_ref`, storing the returned `FieldTypeRef` on the IR `type_ref` field. Prose lines continue to populate the existing `body: tuple[ProseLine, ...]` field.
* Checklist (must all be done):
  - Grammar fragment `typed_field_body_line` exists in `doctrine/grammars/doctrine.lark` with alternatives that cover the `type:` statement and a prose line.
  - `readable_inline_schema_item_body` and `readable_table_column_body` use `typed_field_body_line+` bodies.
  - `record_item_body` / `output_record_item_body` accept a `typed_field_body_line` alternative when the parent `record_keyed_item` has a scalar `record_head`.
  - `ReadableSchemaEntry`, `ReadableTableColumn`, and the record scalar carrier class each gain `type_ref: FieldTypeRef | None`.
  - `ReadablePropertyItem` (`readable.py:29`) and `ReadableDefinitionItem` (`:21`) remain unchanged — no `type_ref` field, no grammar change.
  - Each surface's resolver collects a `type:` line on the body and calls `resolve_field_type_ref`, storing the resolved `FieldTypeRef` on the IR `type_ref` field.
  - Prose lines continue to populate the existing body field for each surface.
  - `type: <BuiltinName>` on each of the four typed prose-only surfaces (readable `row_schema` entry, readable `item_schema` entry, readable `table` column, record scalar) resolves to a `BuiltinTypeRef`.
  - `type: <EnumName>` on each of the four surfaces resolves to an `EnumTypeRef`.
  - `type: <UnknownCNAME>` on each of the four surfaces raises E320.
  - `tests/test_readable.py` (or equivalent) gains unit cases for (a)–(c) on each of the four surfaces.
  - `tests/test_parser_source_spans.py` gains source-span coverage for the `typed_field_body_line` on each surface.
  - A record-scalar unit test confirms that a nested record (non-scalar `record_head`) rejects a `type:` line and the rejection message is clear (implementation note: phase-plan chose grammar-level enforcement over resolve-level enforcement because parse-time failure gives better line reporting; implement accordingly).
* Verification (required proof):
  - `make verify-examples` green.
  - `make verify-diagnostics` green.
  - Unit tests listed in Checklist pass.
  - Parser source-span tests pass.
* Docs/comments (propagation; only if needed):
  - Canonical-boundary comment on the `typed_field_body_line` grammar rule (or on the single resolver helper) noting: "Every field-shaped body in the language routes `type:` through `resolve_field_type_ref`. To add a new field-shaped surface, include `typed_field_body_line` in its body rule and call the helper from its resolver." High-leverage; one comment, one location.
* Exit criteria (all required):
  - All four prose-only field-shaped surfaces parse `type: <CNAME>` alongside prose and populate `type_ref` on their IR.
  - The two glossary/label surfaces (`ReadablePropertyItem`, `ReadableDefinitionItem`) remain prose-only — no new grammar alternative, no new IR field.
  - Every surface's resolver is the single call site into `resolve_field_type_ref` for that surface (no parallel paths).
  - `type: <UnknownCNAME>` raises E320 on every typed surface.
  - `make verify-examples` and `make verify-diagnostics` both green; unit and span tests pass.
* Rollback: revert grammar extensions, IR field additions, and resolver call-site wiring on the four prose-only surfaces. Phases 1–3 artifacts remain.

## Phase 5 — Unified emit of `Valid values: …` line across every field-shaped surface

* Goal: render a single uniform `Valid values: a, b, c.` line under every field whose `type_ref` is an `EnumTypeRef`. Route every surface through one shared helper in `emit_common.py`. Extend `_json_schema_meaning` so existing output-schema fields that carry both a description and an enum vocabulary gain the valid-values line in their rendered meaning.
* Work: add `render_valid_values_line(type_ref: FieldTypeRef | None) -> str | None` to `doctrine/emit_common.py`. Returns `"Valid values: <wire_1>, <wire_2>, …, <wire_n>."` when `type_ref` is an `EnumTypeRef` (values drawn from `type_ref.decl.members` in declared order); returns `None` otherwise. In `doctrine/emit_docs.py`, wire the helper into the readable-table-column renderer, the readable-schema-entry renderer (covers both `row_schema` and `item_schema`), the record-scalar renderer, and the output-schema field renderer. The emitted valid-values line sits immediately after the field description (when a prose body is present) or as the description (when no prose body exists). Extend `_json_schema_meaning` at `doctrine/_compiler/validate/__init__.py:271-293` to append `" One of <rendered>."` to the description when both description and `field_schema["enum"]` are present (previously only the description-absent branch rendered the vocabulary).
* Checklist (must all be done):
  - `doctrine/emit_common.py` exports `render_valid_values_line` with the signature and behavior named in Work.
  - `doctrine/emit_docs.py` readable-table-column renderer calls `render_valid_values_line(column.type_ref)` and inserts the line in the rendered output when non-None.
  - `doctrine/emit_docs.py` readable-schema-entry renderer (row_schema + item_schema) calls the helper and inserts the line.
  - `doctrine/emit_docs.py` record-scalar renderer calls the helper and inserts the line.
  - `doctrine/emit_docs.py` output-schema field renderer calls the helper and inserts the line alongside the existing JSON-schema path (so the human-prose "Valid values:" line is uniform with the readable surfaces).
  - `_json_schema_meaning` at `validate/__init__.py:271-293` appends `One of <values>.` to the description when both description and enum exist; the description-absent branch is unchanged.
  - Every rendered `Valid values:` line uses the enum's wire values (`member.wire`) in declared member order, with commas between values and a period at the end.
  - `tests/test_emit_docs.py` gains unit cases for each of the four field-shaped surfaces: (a) emit with `type_ref = None` renders no valid-values line; (b) emit with `type_ref = BuiltinTypeRef(...)` renders no valid-values line; (c) emit with `type_ref = EnumTypeRef(...)` renders `"Valid values: …"` in declared order.
  - `tests/test_emit_docs.py` gains a unit case for `_json_schema_meaning` covering the description-plus-enum path.
* Verification (required proof):
  - `make verify-examples` green — every shipped `examples/**/ref/**` file is byte-identical to Phase 3's tip for examples that carried no enum vocabulary, and updated in a controlled way for examples that do (Phase 3 migrated examples already carried the canonical form; their JSON-schema output now also renders the valid-values line via the unified helper). Any `ref/**` diff in this phase is recorded in a Decision Log addendum so the shift is intentional and not accidental.
  - `make verify-diagnostics` green.
  - Unit cases listed in Checklist pass.
* Docs/comments (propagation; only if needed):
  - Canonical-boundary comment on `render_valid_values_line` stating it is the single rendering path for field vocabularies across all field-shaped surfaces.
* Exit criteria (all required):
  - `render_valid_values_line` exists in `emit_common.py` and is the only module that formats field-vocabulary prose lines for emit.
  - All four field-shaped surface renderers in `emit_docs.py` call the helper; none format their own valid-values string.
  - `_json_schema_meaning` emits the valid-values line in both the description-present and description-absent branches.
  - `make verify-examples` and `make verify-diagnostics` green; any `ref/**` changes from this phase are captured in the Decision Log as intentional.
  - Unit cases for all four surfaces and for `_json_schema_meaning` pass.
* Rollback: revert `emit_common.py` helper, `emit_docs.py` call-site wiring, `_json_schema_meaning` extension, and related unit cases. Phases 1–4 artifacts remain.

## Phase 6 — New example `examples/139_enum_typed_field_bodies/` as manifest-backed proof

* Goal: ship one end-to-end example demonstrating the canonical form on the primary motivating surface (a readable `row_schema` entry with `type: <EnumName>`). Back it with `render_contract` plus `compile_fail` cases so the language guarantee is manifest-enforced.
* Work: create `examples/139_enum_typed_field_bodies/` with `prompts/AGENTS.prompt`, `cases.toml`, and `ref/**`. The prompt declares one `enum` with a small, plainly-named vocabulary; a readable table with a `row_schema` entry whose body carries `type: <EnumName>` plus a short prose description. The manifest declares a `render_contract` case asserting the rendered artifact contains the `Valid values: …` line in declared order under the typed field. The manifest also declares a `compile_fail` case pointing at a variant source with `type: <UnknownEnumName>`, asserting E320 is raised.
* Checklist (must all be done):
  - `examples/139_enum_typed_field_bodies/prompts/AGENTS.prompt` exists with one `enum` decl and one readable table whose `row_schema` entry carries `type: <EnumName>` alongside a prose description.
  - `examples/139_enum_typed_field_bodies/cases.toml` exists with at least two cases: a `render_contract` case for the primary prompt, and a `compile_fail` case that points at an unknown-enum-name variant and asserts E320.
  - `examples/139_enum_typed_field_bodies/ref/**` contains the expected rendered artifacts, including the `Valid values: …` line under the typed field.
  - The `compile_fail` case uses a source variant (either inline in `cases.toml` or a sibling prompt under `prompts/`) that is minimal, clearly labelled, and does not reuse the primary prompt.
  - The example follows the same on-disk convention as `examples/137_shared_rules_carrier_split` and `examples/138_output_shape_case_selector` (plain-language prose; 7th-grade reading level; names that make the authoring intent obvious).
* Verification (required proof):
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/139_enum_typed_field_bodies/cases.toml` passes.
  - `make verify-examples` green including the new example.
  - `make verify-diagnostics` green including the new compile_fail case.
* Docs/comments (propagation; only if needed): none in-repo; the example itself is the documentation for the pattern.
* Exit criteria (all required):
  - `examples/139_enum_typed_field_bodies/` exists with prompts, manifest, and ref/.
  - Manifest exercises both `render_contract` and `compile_fail` cases and both pass.
  - Rendered `ref/**` shows the `Valid values: …` line in declared order.
  - `make verify-examples` and `make verify-diagnostics` both green.
* Rollback: delete the new example directory. Phases 1–5 artifacts remain.

## Phase 7 — Authoritative docs, version bump, and CHANGELOG

* Goal: make every authoritative doc that carries shipped truth about field-shaped surfaces reflect the new canonical form. Record the breaking change in versioning. Give downstream authors one clear migration path.
* Work: rewrite the output-schema field subsection in `docs/LANGUAGE_REFERENCE.md` to use the canonical form; add a new subsection "Typed field bodies" covering `row_schema` entries, `item_schema` entries, `table` columns, and record scalars with example snippets; cross-reference `examples/139_enum_typed_field_bodies/`. Add a decision note in `docs/LANGUAGE_DESIGN_NOTES.md` explaining that the language has exactly one canonical form for field vocabularies and that glossary/label nodes stay prose-only by design. Update any Form A / Form B references in `docs/AGENT_IO_DESIGN_NOTES.md` to the canonical form. Verify `docs/README.md` index lines are not stale and update them if they are. Add the 5.0 entry to `docs/VERSIONING.md` naming the deleted forms and the one-line migration. Add the 5.0 entry to `CHANGELOG.md` summarizing the five bullets: (a) deleted `type: enum` + `values:`, (b) deleted `type: string` + `enum:`, (c) tightened `type:` to fail loud with E320, (d) added structured `type:` to `row_schema` / `item_schema` / `table column` / record scalar, (e) migration: declare `enum X: "..."` then write `type: X`. Update `examples/README.md` to list example 139 if the file indexes typed patterns (verify during implement; if the file does not index by pattern, no change is required).
* Checklist (must all be done):
  - `docs/LANGUAGE_REFERENCE.md` output-schema subsection uses the canonical form in every code example and no longer shows `type: enum` + `values:` or `type: string` + `enum:`.
  - `docs/LANGUAGE_REFERENCE.md` has a new subsection titled "Typed field bodies" (or equivalent) covering `row_schema` entries, `item_schema` entries, `table` columns, and record scalars with example snippets and a cross-reference to `examples/139_enum_typed_field_bodies/`.
  - `docs/LANGUAGE_DESIGN_NOTES.md` has a decision note explaining the one-canonical-form rule and the glossary/label exception.
  - `docs/AGENT_IO_DESIGN_NOTES.md` no longer references Form A or Form B syntax.
  - `docs/README.md` index lines that name field-shaped surfaces are accurate for 5.0 (verify during implement; update as needed).
  - `docs/VERSIONING.md` has a 4.1 → 5.0 entry naming the deleted forms, E320, and the one-line migration.
  - `CHANGELOG.md` has a 5.0 entry with the five bullets listed in Work.
  - `docs/COMPILER_ERRORS.md` E320 entry from Phase 1 is consistent with the CHANGELOG wording and with the message template registered in `doctrine/diagnostics.py`.
  - `examples/README.md` lists example 139 if the file indexes typed patterns; otherwise no change.
* Verification (required proof):
  - `make verify-package` green (versioning docs changed).
  - `make verify-examples` green (no example regressions from doc edits).
  - `make verify-diagnostics` green.
  - A manual reread of `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/VERSIONING.md`, `CHANGELOG.md`, and `docs/COMPILER_ERRORS.md` shows mutual consistency on the canonical form and the 5.0 breaking change.
* Docs/comments (propagation; only if needed): this phase IS the docs propagation for the language change.
* Exit criteria (all required):
  - Every authoritative doc named in Section 0.2 and in this Checklist reflects the canonical form and the 5.0 breaking change.
  - No authoritative doc still shows Form A or Form B syntax.
  - `make verify-package` green.
  - `CHANGELOG.md` and `docs/VERSIONING.md` carry the 5.0 entry with the five-bullet summary.
* Rollback: revert the doc edits. Phases 1–6 artifacts remain.

## Phase 8 — Shipped skills: agent-linter AL930 + AL200 extension, doctrine-learn authoring-pattern + ladder

* Goal: the two shipped skills that teach Doctrine authoring now teach the canonical form explicitly. `agent-linter` flags the anti-pattern (pipe-list prose vocabulary) with a new finding code; `doctrine-learn` surfaces the canonical form in its task-first chooser and lists example 139 in its examples ladder.
* Work: edit `skills/agent-linter/prompts/refs/finding_catalog.prompt` to add the AL930 entry "Inlined Vocabulary Should Be An Enum-Typed Field" (table row plus full section with *what it means*, *why it matters*, *default fix*, *good/bad* pair), and extend the AL200 section to name pipe-list vocabularies as a canonical duplicate-rule shape. Edit `skills/agent-linter/prompts/refs/examples.prompt` to add the AL930 before/after pair (prose pipe-list in role vs. enum decl + typed field). Edit `skills/doctrine-learn/prompts/refs/authoring_patterns.prompt` to add the task-first chooser row ("I need a field's value to come from a fixed vocabulary → declare `enum X` and set the field's `type: X`. Do not list values as prose. See `examples/139_enum_typed_field_bodies`."). Rewrite any Form A / Form B guidance in `skills/doctrine-learn/prompts/refs/outputs_and_schemas.prompt` to the canonical form. Add an example-139 entry to the doctrine-learn examples ladder (exact ladder filename verified during implement — candidate filenames include `examples_ladder.prompt` or similar under `skills/doctrine-learn/prompts/refs/`). Regenerate curated and build outputs per the emit pipeline in `pyproject.toml` (current scripts under `skills/<name>/pyproject` convention). Confirm the generated `.md` files in `skills/.curated/agent-linter/references/finding-catalog.md`, `skills/.curated/agent-linter/references/examples.md`, `skills/.curated/doctrine-learn/references/authoring-patterns.md` (and the ladder curated output) carry the new content.
* Checklist (must all be done):
  - `skills/agent-linter/prompts/refs/finding_catalog.prompt` contains the AL930 table row and full section with *what it means*, *why it matters*, *default fix*, *good / bad* pair, all at 7th-grade reading level.
  - `skills/agent-linter/prompts/refs/finding_catalog.prompt` AL200 section names pipe-list vocabularies as a canonical duplicate-rule shape.
  - `skills/agent-linter/prompts/refs/examples.prompt` contains the AL930 before/after pair.
  - `skills/doctrine-learn/prompts/refs/authoring_patterns.prompt` contains the task-first chooser row naming the canonical form and cross-referencing `examples/139_enum_typed_field_bodies`.
  - `skills/doctrine-learn/prompts/refs/outputs_and_schemas.prompt` no longer contains Form A or Form B guidance; its examples use the canonical form.
  - The doctrine-learn examples ladder lists example 139 (exact ladder filename identified during implement by reading the `skills/doctrine-learn/` source tree).
  - Curated `.md` outputs are regenerated via the shipped emit pipeline: `skills/.curated/agent-linter/references/finding-catalog.md`, `skills/.curated/agent-linter/references/examples.md`, `skills/.curated/doctrine-learn/references/authoring-patterns.md`, and the ladder curated output each carry the new content.
  - All new prose passes a plain-language check at roughly 7th-grade reading level per AGENTS.md.
* Verification (required proof):
  - The curated `.md` diffs show the expected new/edited content and nothing incidental.
  - `make verify-examples` and `make verify-diagnostics` remain green.
  - A spot-read of `skills/.curated/agent-linter/references/finding-catalog.md` shows AL930 and the extended AL200 rendered correctly.
  - A spot-read of `skills/.curated/doctrine-learn/references/authoring-patterns.md` shows the new task-first chooser row.
* Docs/comments (propagation; only if needed): none beyond what this phase ships.
* Exit criteria (all required):
  - All four `.prompt` source edits named in Checklist are in place.
  - The examples ladder entry for 139 is committed.
  - Curated `.md` outputs are regenerated and committed.
  - New prose is at roughly 7th-grade reading level.
  - `agent-linter` does not cross-reference `doctrine-learn` or vice versa (two skills keep clean separation per current convention).
* Rollback: revert `.prompt` edits and regenerated curated outputs. Phases 1–7 artifacts remain.

## Phase 9 — Editor snapshots + final corpus-level verification

* Goal: bring the VS Code editor test snapshots in line with the migrated shipped corpus. Run the full verification suite once end-to-end. Confirm no file under `../psflows` is modified in the branch diff.
* Work: run `cd editors/vscode && make` to regenerate editor snapshots under `editors/vscode/tests/snap/examples/...`. Review each regenerated snapshot for correctness (the Form A migrations in Phase 3 and the unified emit in Phase 5 can both affect cached snapshots). Commit regenerated snapshots. Run the full verify suite. Perform a scratch conversion of the `psflows/lesson_plan` `step_role` excerpt into the canonical form on this branch — compile locally, confirm it resolves under 5.0. The scratch is read-only and uncommitted; `../psflows` is not edited.
* Checklist (must all be done):
  - `cd editors/vscode && make` completes cleanly.
  - Regenerated snapshots under `editors/vscode/tests/snap/examples/79_final_output_output_schema/...`, `editors/vscode/tests/snap/examples/121_nullable_route_field_final_output_contract/...`, and any other examples touched in Phase 3 or Phase 5 are committed and reflect the canonical form plus the unified `Valid values:` line.
  - A scratch file (not committed; kept locally only for the duration of this phase) demonstrates that a `psflows/lesson_plan` `step_role` excerpt, rewritten to the canonical form, compiles against this branch without E320. The excerpt is read-only; no file under `../psflows` is modified.
  - `make verify-examples` green.
  - `make verify-diagnostics` green.
  - `make verify-package` green.
  - `uv run --locked python -m unittest tests.test_release_flow` green if release-flow work was touched; if not, explicitly noted.
  - `git diff main -- ../psflows` is empty (read-only guarantee).
* Verification (required proof):
  - All three `make verify-*` targets green on the branch tip.
  - Editor snapshot regeneration is clean (no manual hand-edits required).
  - A committed Decision Log entry in Section 10 names the final verification results.
* Docs/comments (propagation; only if needed): none — this phase is verification, not authoring.
* Exit criteria (all required):
  - Editor snapshots are regenerated and committed.
  - `make verify-examples`, `make verify-diagnostics`, and `make verify-package` all green.
  - Release-flow verification status is recorded (either green or explicitly noted as not applicable).
  - Scratch psflows conversion confirms the language now expresses `step_role` as one `enum` decl plus one `type:` annotation with zero pipe-list prose.
  - No file under `../psflows` is modified in this branch's diff.
  - A final Decision Log entry in Section 10 names the green verification and declares the plan implementation-complete for 5.0.
* Rollback: revert editor snapshot commits. Phases 1–8 artifacts remain; the plan is rolled back one verification phase but still usable once snapshots regenerate cleanly.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Resolver unit tests per surface: `type: <EnumName>` resolves; unknown ref raises E320; legacy forms unchanged.
- IR round-trip: parse → resolve → emit → reparse for each surface.

## 8.2 Integration tests (flows)

- `make verify-examples` covers the new `examples/139_...` manifest end-to-end.
- `make verify-diagnostics` covers the E320 compile-fail case.
- Behavior-preservation signal: every pre-existing `examples/*/ref/**` output is unchanged after the refactor. Any ref change requires an explicit Decision Log entry justifying it.

## 8.3 E2E / device tests (realistic)

- Scratch conversion of a `psflows/lesson_plan` step excerpt into the new typed form compiles locally. This is a sanity check, not a committed artifact.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Single merge on `feat/carrier-review-fields-and-shared-rules-split` (or a rebased follow-up branch).
- Language **4.1 → 5.0** major breaking bump per AGENTS.md.
- `CHANGELOG.md` entry names the deleted forms, the new E320 diagnostic, and the one-canonical-form migration path.
- No staged rollout; the change is compile-time and breaking.

## 9.2 Telemetry changes

N/A — no runtime telemetry in this repo's scope.

## 9.3 Operational runbook

- If a downstream author reports a program that stopped compiling, the failure is expected under the 5.0 breaking change and the author follows the migration path in `CHANGELOG.md`. This is not a regression.
- If a shipped example was missed by the migration sweep and stops compiling, treat that as a plan gap: fix the example in-tree, add a targeted regression test, and record the miss in the Decision Log.

# 10) Decision Log (append-only)

## 2026-04-19 — Plan created, consistency sweep made load-bearing

**Context.** Initial scoping targeted only the primary motivating surface (readable row_schema typed column). User pushed back that partial fixes would leave the same broken pattern in other surfaces, to be rediscovered later.

**Options.**
- (A) Narrow fix: typed row_schema only.
- (B) Universal fix: shared `typed_field_body` fragment across every field-shaped surface in one pass, with explicit enumeration in research.
- (C) Staged fix: narrow fix now, broader sweep later.

**Decision.** (B). The user explicitly called out "I want to make sure what we do ends up through the language properly, not I discover same broken pattern 3 more places because I didn't ask specifically." The consistency sweep is load-bearing in Section 0 and is the core deliverable of Section 3.2.

**Consequences.**
- More grammar and resolver work in this pass.
- Lower risk of the same bug resurfacing on the next surface.
- Section 3.2 blocks Section 5 until the surface inventory is complete.

**Follow-ups.**
- Research must enumerate every field-shaped surface.
- Any surface deliberately excluded must be named in Section 0.3 with a reason.

## 2026-04-19 — North Star confirmed; skills and docs scope locked

**Context.** User confirmed the drafted North Star and reinforced three requirements explicitly.

**Decision.** Status `draft` → `active`. The following are locked in as confirmed in-scope and out-of-scope:
- **In scope:** updates to the shipped `agent-linter` skill (AL930 + AL200 extension) and the shipped `doctrine-learn` skill (authoring-pattern row + examples-ladder entry). Edit `.prompt` source, regenerate curated outputs.
- **In scope:** every authoritative doc that carries truth about field-shaped surfaces is updated (`LANGUAGE_REFERENCE.md`, `LANGUAGE_DESIGN_NOTES.md`, `COMPILER_ERRORS.md`, `VERSIONING.md`, `CHANGELOG.md`, plus any index lines that name the relevant surfaces).
- **Out of scope (hard):** no edits to `../psflows`. Reference excerpts only.

**Consequences.**
- Definition of Done includes skill regeneration and a clean diff with zero psflows changes.
- The next miniarch stage is `research`; it owns Section 3's surface enumeration.

**Follow-ups.**
- Run `$miniarch-step research` when ready to begin Section 3.

## 2026-04-19 — Research findings + break-for-elegance decision

**Context.** Research (auto-plan initial turn) uncovered a pivotal grammar reality that invalidated the TL;DR's "shared fragment across five surfaces" framing: only the three output-schema surfaces have structured bodies today; every other field-shaped surface (readable `row_schema`, `item_schema`, `table` column, record scalar) is prose-only by grammar design. Three decision gaps were surfaced as explicit blockers. User answered directly: "the breaking change that gets us to max elegance. not some narrow scope shit and not some 'omg don't break my own zero user application' shit."

**Options considered.**
- Narrow fix (resolve `type: <EnumName>` on the three output-schema surfaces only, no grammar extension).
- Universal additive fix (add structured slots to prose-only surfaces, keep all three enum forms, minor bump 4.1 → 4.2).
- **Universal breaking fix (chosen):** add structured slots to every prose-only surface, delete both secondary enum forms, tighten `type:` to fail loud on unknown CNAME, major bump 4.1 → 5.0, migrate every shipped example in-pass.

**Decision.** Universal breaking fix. Rationale: the user's North Star is elegance and consistency, not compatibility with a repo that has zero external users. Two-plus forms for one concept is the exact kind of drift the plan exists to eliminate. Breaking change is the price of one canonical form.

**Consequences.**
- Language version bump 4.1 → **5.0** (major). `docs/VERSIONING.md` + `CHANGELOG.md` carry explicit breaking-change and migration guidance.
- Every shipped example that uses a secondary enum form gets rewritten in this pass. `ref/**` outputs for those examples change by construction.
- Silent-malformed-schema latent bug (`type: <CNAME>` silently writing `{"type": "CNAME"}`) is fixed as part of E320.
- Grammar, IR, resolve, and emit all touch more surfaces than the original narrow framing anticipated. Deep-dive owns the exact file-by-file design.
- Downstream Doctrine repos that use secondary forms must migrate; the CHANGELOG documents the path, but migration is their own concern.
- `../psflows` still strictly off-limits (user-reaffirmed via standing memory).

**Follow-ups.**
- `deep-dive` enumerates every shipped example that uses a secondary enum form (expected: `examples/79_final_output_output_schema` at minimum; exhaustive list is a deep-dive deliverable).
- `deep-dive` designs the shared type-resolution helper signature and the per-surface grammar extension.
- `phase-plan` splits work into coherent phases earliest-first; foundational phase is the shared resolver + E320 + deleted-forms grammar + diagnostic compile-fail cases.

## 2026-04-19 — Phase plan authored: 9 phases, foundational-first, breaking cutover on Phase 3

**Context.** `phase-plan` pass owned Section 7. Inputs: Section 4 (current architecture), Section 5 (target architecture), Section 6 (call-site audit + migration notes + consolidation sweep). No open blockers from research or deep-dive.

**Key phase-plan decisions.**
- **9 phases, not fewer.** Each phase is one coherent self-contained unit. Preferred more phases over fewer per the quality bar; in particular, the shared resolver helper (Phase 1), its wiring to structured output-schema surfaces (Phase 2), and the breaking deletion of Form A / Form B (Phase 3) are kept separate because each is independently testable and a failure in one should not cascade into the others.
- **Phase 2 preserves Form A / Form B by design.** The new `type_ref`-preferred lowering path lets shipped examples keep compiling through this phase while the helper tightens `type:` to fail loud on unknown CNAME. The breaking cutover is deliberately deferred to Phase 3 so behavior preservation for the migrated examples can be proven in isolation.
- **Behavior-preservation test captures its golden at the Phase 2 tip.** `tests/test_enum_migration_preservation.py` (filename placeholder; implement chooses the exact name) locks the emitted JSON schema `enum` list from Phase 2 tip output and asserts byte-identical match after Phase 3's source rewrites. This is a positive-value preservation assertion, not a grep-the-repo gate.
- **Glossary nodes explicitly excluded from Phase 4.** `ReadablePropertyItem` and `ReadableDefinitionItem` remain prose-only. The checklist names the non-change so the auditor cannot claim the phase forgot them.
- **Phase 5 acknowledges a controlled `ref/**` shift.** Unifying emit via `render_valid_values_line` plus extending `_json_schema_meaning` to append `One of …` when a description exists can change rendered output for enum-valued fields that previously rendered only through the JSON-schema path. The phase requires recording any `ref/**` diff as an intentional Decision Log addendum rather than treating it as regression.
- **Phase 6 owns the one new example only.** `examples/139_enum_typed_field_bodies/` focuses on the primary motivating surface (readable `row_schema` typed entry). Per AGENTS.md "one new idea per example", additional surface coverage is through unit tests in Phase 4, not additional examples.
- **Phase 7 is the bulk docs sweep.** E320 shipped in Phase 1 (coupled to the diagnostic registration), but `LANGUAGE_REFERENCE.md`, `LANGUAGE_DESIGN_NOTES.md`, `VERSIONING.md`, `CHANGELOG.md`, `AGENT_IO_DESIGN_NOTES.md`, and `examples/README.md` all wait for Phase 7 to keep the docs change coherent rather than drip-fed per phase.
- **Phase 9 includes a psflows scratch check.** A scratch conversion of the `step_role` excerpt is run locally against the branch tip to prove the North Star's downstream unblock claim. The scratch file is read-only and uncommitted; `git diff main -- ../psflows` must remain empty.
- **Every phase names its rollback.** Each rollback is a pure git revert of that phase's artifacts; earlier phases' work is preserved.

**Consequences.**
- Section 7 is the single execution checklist. Every required obligation from Sections 5, 6, and the consolidation sweep is encoded as a Checklist item or Exit criterion; no obligations live only in `Work` prose.
- Plan is decision-complete through `phase-plan` and ready for `implement-loop`.
- `planning_passes` now marks `phase_plan_pass_1: done 2026-04-19`.

**Follow-ups.**
- `$miniarch-step implement-loop docs/UNIVERSAL_TYPED_FIELD_BODIES_CONSISTENCY_SWEEP_2026-04-19.md` — the full-frontier delivery controller takes ordered Phases 1–9 and runs `implement` across the frontier with credible programmatic proof, then `audit-implementation`.

## 2026-04-19 — Deep-dive complete: shared resolver helper + exhaustive call-site audit

**Context.** `deep-dive` pass owned Sections 4 (current architecture), 5 (target architecture), and 6 (call-site audit). Inputs: research block at Section 3 (surface inventory + 4 resolved blockers), TL;DR, Sections 0 through 2, and live code reads confirming grammar/IR/resolver/emit anchors.

**Key deep-dive decisions.**
- **Single resolver module.** New `doctrine/_compiler/resolve/field_types.py` owns `resolve_field_type_ref`, `FieldTypeRef`, `BuiltinTypeRef`, `EnumTypeRef`, `BUILTIN_TYPE_NAMES`. Every field-shaped surface calls this one helper. No surface gets its own resolver.
- **IR uniformity via optional `type_ref` field.** `OutputSchemaField`, `OutputSchemaRouteField`, `OutputSchemaDef`, `ReadableSchemaEntry`, `ReadableTableColumn`, and the record scalar carrier each gain `type_ref: FieldTypeRef | None`. Precedent: `OutputShapeSelectorConfig.enum_ref` at `doctrine/_model/io.py:252`.
- **Glossary nodes explicitly excluded.** `ReadablePropertyItem` and `ReadableDefinitionItem` stay prose-only by design — they are glossary/label nodes, not field-shaped slots. Recorded as an explicit `exclude` row in the pattern consolidation sweep rather than left implicit.
- **Grammar fragment is one new `typed_field_body_line` alt.** Not a factored fragment — each prose-only body rule takes the new alternative alongside prose lines. Record scalars gate the alternative on a scalar `record_head`.
- **Emit uniformity via `render_valid_values_line` helper in `emit_common.py`.** Every field-shaped surface calls the same helper. Validator `_json_schema_meaning` at `validate/__init__.py:271-293` is extended to append `One of <values>.` to descriptions when both exist, giving a bonus fix to today's drop-enum-when-description-present behavior.
- **Behavior preservation is test-level, not snapshot-level.** For every migrated example, a resolver-level assertion test proves the emitted JSON schema `enum` list matches pre-migration output. This is more precise than diffing `ref/**` which will change by construction for Form A migrations.
- **Six shipped examples migrate.** Confirmed via `grep`: `79/AGENTS.prompt`, `79/optional_no_example/AGENTS.prompt`, `79/invalid_invalid_example/AGENTS.prompt`, `85/AGENTS.prompt`, `90/AGENTS.prompt`, `121/AGENTS.prompt`. All six use Form A. Form B (legacy `type: string` + `enum:` block) has zero shipped uses; only test fixtures exercise it today.
- **Editor snapshots move with the corpus.** `editors/vscode/tests/snap/examples/...` caches shipped example artifacts. Regenerated via `cd editors/vscode && make` after the migration lands.

**Consequences.**
- Section 7 phase plan has a clear earliest-first skeleton: (1) shared resolver + `FieldTypeRef` + E320 + builtin whitelist enforcement (2) IR model plumbing (`type_ref` on structured surfaces first) (3) grammar deletion of Form A/Form B (4) grammar extension + IR plumbing for prose-only surfaces (5) emit uniformity via `render_valid_values_line` (6) shipped example migration + behavior-preservation assertion tests (7) example 139 creation (8) docs + version bump + `CHANGELOG.md` (9) skills regeneration (agent-linter AL930 + AL200; doctrine-learn authoring pattern + ladder) (10) editor snapshot regeneration + final verification.
- No open blockers. Every row in Section 6's change map has either a concrete file path + symbol or a "identified in phase-plan" flag for convention calls (e.g., exact record-scalar class name, ladder filename).
- Plan is decision-complete for deep-dive. Ready to advance to `phase-plan`.

**Follow-ups.**
- `$miniarch-step phase-plan <DOC_PATH>` to author Section 7 from the deep-dive's phase skeleton.

## 2026-04-19 — Controller state cleared after blocker; decisions now encoded

**Context.** `auto-plan` initial turn ran `research`, stopped on Blocker #1, cleared armed miniarch-step-auto-plan state per contract, surfaced the exact question. User answered; this Decision Log entry captures the resolution. Doc is now decision-complete for research and ready to advance to `deep-dive`.

**Decision.** Next command is `$miniarch-step auto-plan` (re-arm the controller; Stop hook will detect research is done and feed `deep-dive`) or `$miniarch-step deep-dive <DOC_PATH>` to run deep-dive explicitly.

**Consequences.** No open blockers. TL;DR, Section 0, Section 3 are mutually consistent. Section 7 stays a stub until phase-plan.

**Follow-ups.**
- User invokes the next command when ready.
