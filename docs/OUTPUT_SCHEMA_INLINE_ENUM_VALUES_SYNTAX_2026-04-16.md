---
title: "Doctrine - Output Schema Inline Enum Values Syntax - Architecture Plan"
date: 2026-04-16
status: complete
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - doctrine/grammars/doctrine.lark
  - doctrine/_parser/io.py
  - doctrine/_model/io.py
  - doctrine/_compiler/resolve/output_schemas.py
  - doctrine/_diagnostic_smoke/fixtures_final_output.py
  - tests/test_output_schema_lowering.py
  - tests/test_final_output.py
  - docs/LANGUAGE_REFERENCE.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/AUTHORING_PATTERNS.md
  - docs/EMIT_GUIDE.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/VERSIONING.md
  - CHANGELOG.md
  - examples/79_final_output_output_schema/prompts/AGENTS.prompt
  - examples/85_review_split_final_output_output_schema/prompts/AGENTS.prompt
  - examples/90_split_handoff_and_final_output_shared_route_semantics/prompts/AGENTS.prompt
---

# TL;DR

## Outcome

Doctrine accepts inline `output schema` enums written as `type: enum` plus a
`values:` list, and the shipped docs and examples use that form as the normal
style.

## Problem

Today inline `output schema` enums are written as `type: string` plus a
separate `enum:` block. That lowers correctly, but it reads oddly and does
not match how authors think about a local closed vocabulary.

## Approach

Add one additive inline-enum syntax for `output schema` fields. Lower it to
the same JSON Schema string enum shape used today. Keep the current
`type: string` plus `enum:` form legal in the first cut so public prompt files
do not break. Update tests, diagnostics fixtures, examples, and docs to teach
the new form.

## Plan

1. Extend the grammar, parser, model, and lowering path for `type: enum` plus
   `values:`.
2. Prove that the new form lowers to the same wire schema and that the old
   form still works.
3. Update the shipped docs, examples, and release docs to show the new style
   and explain the change as additive.

## Non-negotiables

- Do not break existing prompt files that still use `type: string` plus
  `enum:` in the first shipping change.
- Do not create a second lowering story for equivalent inline string enums.
- Keep the emitted JSON Schema and final-output behavior unchanged for
  equivalent enum fields.
- Update code, docs, examples, versioning guidance, and changelog truth in the
  same change.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-16
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None; automated proof passed with `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_final_output`, `make verify-examples`, and `make verify-diagnostics`.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-16
phase_plan: done 2026-04-16
recommended_flow: research -> deep dive -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

WORKLOG_PATH: docs/OUTPUT_SCHEMA_INLINE_ENUM_VALUES_SYNTAX_2026-04-16_WORKLOG.md

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If `output schema` fields accept `type: enum` with a local `values:` list,
Doctrine authors can express local closed vocabularies in a clearer way while
the lowered JSON Schema and final-output behavior stay the same as today's
equivalent string enum fields.

## 0.2 In scope

- Add additive grammar support for `type: enum` and `values:` inside
  `output schema` fields and nested fields.
- Define the parser and model shape for the new inline enum form.
- Lower the new form to the same string-backed JSON Schema enum shape used by
  today's equivalent fields.
- Keep the current `type: string` plus `enum:` form legal in the first cut.
- Add focused proof in parser, lowering, final-output, and diagnostic-fixture
  surfaces.
- Update the main shipped examples that currently teach inline enum fields.
- Update the main docs that explain `output schema`, structured final output,
  and authoring patterns.
- Update `docs/VERSIONING.md` and `CHANGELOG.md` because this is a new
  backward-compatible language surface.

## 0.3 Out of scope

- Replacing top-level Doctrine `enum` declarations.
- Adding named enum refs to `output schema` fields in this change.
- Removing or soft-deprecating the current `type: string` plus `enum:` form in
  the first cut.
- Changing runtime harness behavior, emitted route contracts, or non-schema
  output semantics.
- Redesigning numeric or boolean enum syntax beyond what the current shipped
  surface already supports.

## 0.4 Definition of done (acceptance evidence)

- Authors can write:

  ```prompt
  field section_edit: "Section Edit"
      type: enum
      values:
          full_rewrite
          new_section
          existing_section_edit
      required
  ```

- Equivalent lowered schema still uses a string enum payload shape.
- Existing prompt files that use `type: string` plus `enum:` still compile.
- The relevant unit tests pass.
- The relevant manifest-backed examples pass.
- Any touched diagnostics proof passes.
- The live docs and examples show the new syntax as the preferred inline form.
- Versioning and changelog truth match the shipped compatibility posture.

## 0.5 Key invariants (fix immediately if violated)

- Compatibility posture: additive first cut. Existing inline enum prompt files
  must keep working.
- `type: enum` means one local string-backed closed vocabulary, not a second
  generic output-schema type system.
- Equivalent old and new inline enum forms must lower to the same wire shape.
- Fail loud when `type: enum` is malformed or incomplete.
- Keep one source of truth for inline enum lowering and validation.
- Do not leave shipped docs or examples teaching the old form as the normal
  style after the new form lands.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Make the authoring surface read naturally.
2. Preserve public compatibility in the first shipping cut.
3. Keep one lowering path for equivalent inline string enums.
4. Keep docs, examples, and release truth aligned with the code.

## 1.2 Constraints

- `output schema` is a public language surface.
- Lowered structured-output schema files are part of the public surface.
- The repo already ships examples, tests, and diagnostics that teach the old
  form.
- A backward-compatible syntax addition needs versioning and changelog
  alignment.

## 1.3 Architectural principles (rules we will enforce)

- One inline enum lowering story.
- Fail loud for bad inline enum shape.
- Prefer explicit authored meaning over JSON-Schema-flavored indirection.
- Keep top-level Doctrine enums and local output-schema enums as separate
  surfaces unless this plan later proves they must converge.

## 1.4 Known tradeoffs (explicit)

- Keeping both forms for now makes the parser surface slightly larger, but it
  avoids a breaking cutover.
- `type: enum` is clearer for local string vocabularies, but it does not solve
  named enum reuse in `output schema`.
- We should decide the string-backed scope clearly now instead of half-solving
  numeric or boolean local enums in the same change.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

The shipped grammar models inline enum fields as a normal `type:` setting plus
a separate `enum:` block. The parser stores `type` and `enum` separately, and
the lowering code later combines them into JSON Schema.

## 2.2 What’s broken / missing (concrete)

The current authoring form feels split in two. Authors must say `type: string`
and then list enum values, even when what they really mean is "this field is a
local enum." That friction is already visible in the shipped examples and
tests.

## 2.3 Constraints implied by the problem

We need a clearer surface without breaking existing prompt files, emitted wire
shape, or the structured final-output docs that already depend on the current
behavior.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal "ground truth")

## 3.1 External anchors (papers, systems, prior art)

No external research is needed for this change. The right shape is driven by
Doctrine's shipped output-schema grammar, lowering path, tests, examples, and
public versioning rules.

## 3.2 Internal ground truth (code as spec)

- `doctrine/grammars/doctrine.lark` owns the shipped `output schema` surface.
  Today it accepts `type:` as a named setting and `enum:` as a separate value
  block under `output_schema_item_line`.
- `doctrine/_parser/io.py` lowers that grammar into `OutputSchemaSetting` for
  `type` and `OutputSchemaEnum` for the enum value list. There is no current
  first-class inline enum node that owns the full local concept.
- `doctrine/_model/io.py` is the canonical model boundary. Any new inline enum
  syntax must fit that model or replace the split shape there instead of
  inventing a sidecar path.
- `doctrine/_compiler/resolve/output_schemas.py` is the canonical lowering and
  validation path. It chooses the resolved type, writes `schema["type"]`, and
  then writes `schema["enum"]` from `parts.enum_values`. Equivalent old and
  new inline forms should converge here.
- `tests/test_output_schema_lowering.py` already proves inherited schemas,
  nullable optional enum fields, `$defs`, arrays, and `any_of`. This is the
  main preservation signal for inline enum lowering.
- `tests/test_final_output.py` already proves structured final-output render
  behavior for inline enums in plain finals, routed nested object fields, and
  review-driven JSON finals. This is the main preservation signal for public
  final-output behavior.
- `doctrine/_diagnostic_smoke/fixtures_final_output.py` carries helper prompt
  sources that currently teach the old inline enum form. If that fixture drifts
  from the new syntax, diagnostics proof and contributor examples will diverge.
- `examples/79_final_output_output_schema` is the main shipped teaching example
  for schema-backed final output. Its main prompt plus `OPTIONAL_NO_EXAMPLE`
  and `INVALID_INVALID_EXAMPLE` prompts all currently use the old inline enum
  form.
- `examples/85_review_split_final_output_output_schema` and
  `examples/90_split_handoff_and_final_output_shared_route_semantics` are the
  shipped review-final JSON examples that also teach the old inline enum form.
- `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/AUTHORING_PATTERNS.md`, and `docs/EMIT_GUIDE.md` are the live public
  docs tied to this contract family.
- `docs/VERSIONING.md` says a backward-compatible language surface addition
  needs additive public-release treatment and language-version alignment.

Canonical owner path: keep this change inside the existing output-schema
language path across `doctrine/grammars/doctrine.lark`,
`doctrine/_parser/io.py`, `doctrine/_model/io.py`, and
`doctrine/_compiler/resolve/output_schemas.py`. Do not add a second schema
subsystem.

Adjacent surfaces tied to the same contract family:

- Tests: `tests/test_output_schema_lowering.py` and `tests/test_final_output.py`
  must stay in sync with the new syntax and unchanged wire shape.
- Diagnostics fixtures:
  `doctrine/_diagnostic_smoke/fixtures_final_output.py` must reflect the new
  preferred form if touched behavior or examples would otherwise drift.
- Shipped examples: examples 79, 85, and 90 plus the invalid and optional
  prompt files under example 79 all move with this language change.
- Live docs: the language reference, agent I/O notes, authoring patterns, emit
  guide, versioning guide, and changelog must all tell the same additive story.

Compatibility posture (separate from `fallback_policy`): preserve the existing
public syntax in the first cut and add `type: enum` plus `values:` as a new
preferred inline form. This matches the confirmed North Star and Doctrine's
versioning rules for backward-compatible language additions.

Existing patterns to reuse:

- Reuse Doctrine's normal additive-language pattern: add the new syntax while
  leaving the old form legal until a later explicit cleanup plan.
- Reuse the current enum-lowering path so equivalent old and new inline forms
  emit the same string-backed JSON Schema.
- Reuse the existing manifest-backed structured-final-output examples instead
  of inventing a new proof family.

Duplicate or drifting paths relevant to this change:

- The old inline enum form is duplicated across grammar expectations, tests,
  diagnostic fixtures, and shipped examples.
- If the code changes but the examples and docs stay on the old form, Doctrine
  will ship two competing stories for the same feature.

Behavior-preservation signals already available:

- `uv run --locked python -m unittest tests.test_output_schema_lowering`
  protects lowering and nullable-enum behavior.
- `uv run --locked python -m unittest tests.test_final_output` protects final
  output rendering and structured contract behavior.
- `make verify-examples` protects the shipped structured-final-output examples.
- `make verify-diagnostics` protects any touched diagnostics text or smoke
  fixture expectations.

## 3.3 Decision gaps that must be resolved before implementation

No blocker remains. The confirmed plan chooses a string-backed `type: enum`
inline form with `values:`, additive compatibility in the first cut, one
shared lowering story, and shipped docs/examples that teach the new form as the
preferred style.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/grammars/doctrine.lark` defines `output_schema_item_line`. Today it
  has a `type:` setting and an `enum:` block, but no `values:` block.
- `doctrine/_parser/io.py` lowers those shapes into `OutputSchemaSetting` for
  `type` and `OutputSchemaEnum` for the value list.
- `doctrine/_model/io.py` exports the output-schema node family used by parse,
  inheritance, and lowering. There is no current source-specific node for the
  new inline enum form.
- `doctrine/_compiler/resolve/output_schemas.py` is the one lowering and
  validation path for authored `output schema` nodes.
- `tests/test_output_schema_surface.py` covers parse-tree and inheritance
  surface behavior for `output schema`.
- `tests/test_output_schema_lowering.py` covers lowered JSON Schema behavior,
  including optional enum fields widening to `null`.
- `tests/test_final_output.py` covers structured-final-output rendering and
  schema emission behavior for enum-bearing schemas.
- `doctrine/_diagnostic_smoke/fixtures_final_output.py` and
  `doctrine/_diagnostic_smoke/compile_checks.py` carry helper prompt sources
  and smoke assertions that currently teach the old inline enum form.
- `examples/79_final_output_output_schema`, `examples/85_review_split_final_output_output_schema`,
  and `examples/90_split_handoff_and_final_output_shared_route_semantics` are
  the shipped manifest-backed example families that currently show the old
  inline enum form.

## 4.2 Control paths (runtime)

This is an authoring-time compile path, not a runtime harness feature. The
current control flow is:

1. A prompt file parses `output schema` items from `doctrine/grammars/doctrine.lark`.
2. `doctrine/_parser/io.py` turns `type:` into `OutputSchemaSetting(key="type", ...)`
   and `enum:` into `OutputSchemaEnum(values=...)`.
3. `_output_schema_node_parts()` in `doctrine/_compiler/resolve/output_schemas.py`
   collects `type_name` and `enum_values` separately.
4. `_lower_output_schema_node()` picks `resolved_type`, writes
   `schema["type"] = resolved_type`, then writes `schema["enum"]` when enum
   values exist.
5. Final-output compile then validates the lowered JSON Schema against Draft
   2020-12 and the OpenAI subset, renders Markdown contract tables, and emits
   `schemas/<output-slug>.schema.json`.

Important current behavior: `type:` already accepts any `CNAME`, so `type: enum`
is lexically accepted today, but it is not a real shipped surface. Without
special handling it lowers to an invalid JSON Schema type and fails later as
`E217`.

## 4.3 Object model + key abstractions

- `OutputSchemaSetting` is the generic keyed setting node. It currently carries
  both ordinary JSON-like types and any unsupported type name.
- `OutputSchemaEnum` carries one tuple of literal values for the legacy inline
  enum block.
- `_OutputSchemaNodeParts` is the lowering accumulator. It currently has
  `type_name` and `enum_values`, but no way to distinguish legacy `enum:` from
  a new `values:` source.
- `_OUTPUT_SCHEMA_BUILTIN_TYPES` defines the JSON-like built-in type names
  recognized by the lowering path.
- The final-output validators and renderers consume the lowered JSON Schema,
  not the authored syntax directly.

## 4.4 Observability + failure behavior today

- Unsupported type names reach lowering and then fail as Draft-validation
  errors rather than fail-loud authored-surface errors.
- Duplicate `enum:` blocks already fail in the output-schema lowering path.
- Optional enum fields widen to `null` in the emitted wire schema today.
- The shipped docs and example prompts currently normalize the old inline enum
  form, so changing code without changing those surfaces would leave two
  competing public stories.

## 4.5 UI surfaces (ASCII mockups, if UI work)

No UI work.

<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Keep the change inside the existing output-schema path:
  `doctrine/grammars/doctrine.lark`,
  `doctrine/_parser/io.py`,
  `doctrine/_model/io.py`, and
  `doctrine/_compiler/resolve/output_schemas.py`.
- Add the new authored `values:` block under `output schema` item lines.
- Add one source-aware model node for the new inline enum list so the compiler
  can enforce the exact authored form without adding a parallel lowering path.
- Update the focused proof, diagnostic smoke helpers, and shipped example
  prompts to use the new preferred syntax where they currently teach local
  inline enums.

## 5.2 Control paths (future)

The chosen future control flow is:

1. `type: enum` continues to parse through the existing `type:` setting path.
2. `values:` parses into a new source-aware output-schema body item.
3. The output-schema lowering prepass enforces the two exact authored forms:
   - legacy form: `type: string` plus `enum:`
   - new form: `type: enum` plus `values:`
4. Mixed forms fail loud:
   - `type: enum` without `values:`
   - `values:` without `type: enum`
   - `type: string` plus `values:`
   - `type: enum` plus legacy `enum:`
5. After validation, both legal forms normalize onto the same lowering path and
   emit the same string-backed JSON Schema:
   - `schema["type"] = "string"`
   - `schema["enum"] = [...]`
6. Final-output validation, rendering, emitted schema files, and validator
   tooling keep operating on that unchanged lowered wire shape.

## 5.3 Object model + abstractions (future)

- Keep `OutputSchemaEnum` as the legacy inline-enum source node.
- Add one new model node, such as `OutputSchemaValues`, for the new `values:`
  block.
- Extend `_OutputSchemaNodeParts` with source-aware fields so the compiler can
  validate exact authored-shape combinations before lowering.
- Keep one normalization point in `doctrine/_compiler/resolve/output_schemas.py`
  that converts the new form into the same string-enum lowering behavior used
  by the legacy form.
- Do not add a second output-schema validator, renderer, or emitted contract
  shape.

## 5.4 Invariants and boundaries

- `type: enum` is the new local inline enum form.
- `values:` is only valid with `type: enum`.
- Legacy `enum:` remains legal only with the legacy string-backed form in the
  first cut.
- Equivalent legacy and new inline enum forms must emit the same wire schema
  and final-output behavior.
- The compatibility posture stays additive in the first cut. Old syntax
  support remains until a later explicit cleanup plan changes that.
- Named Doctrine `enum` declarations remain a separate surface from local
  output-schema enums.
- Numeric, boolean, or mixed-literal redesign is out of scope for this change.

## 5.5 UI surfaces (ASCII mockups, if UI work)

No UI work.

<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar | `doctrine/grammars/doctrine.lark` | `output_schema_item_line`, enum item rules | Supports `type:` and legacy `enum:` only. | Add `values:` block support under output-schema item lines. Keep `type:` grammar unchanged because `CNAME` already parses `enum`. | The new surface needs one explicit value-list syntax without a new parser branch for `type:` itself. | `type: enum` + `values:` becomes legal authored syntax. | `tests/test_output_schema_surface.py`, `tests/test_output_schema_lowering.py` |
| Parser | `doctrine/_parser/io.py` | `output_schema_type_stmt`, `output_schema_enum_block`, new `output_schema_values_block` | Builds `OutputSchemaSetting` and `OutputSchemaEnum` only. | Add parser transform for `values:` and keep source identity separate from legacy `enum:`. | The compiler must distinguish legacy and new forms to fail loud on mixed authored shapes. | New model node for `values:`. | `tests/test_output_schema_surface.py` |
| Model | `doctrine/_model/io.py`, `doctrine/model.py` | output-schema item classes and exports | No source-aware node for the new inline enum list. | Add new output-schema body-item type for `values:` and export it. | The future architecture needs exact authored-shape validation without a sidecar system. | Source-aware inline enum body items. | `tests/test_output_schema_surface.py` |
| Lowering + authored-shape validation | `doctrine/_compiler/resolve/output_schemas.py` | `_OutputSchemaNodeParts`, `_output_schema_node_parts`, `_lower_output_schema_node` | Treats type and enum list separately and emits whatever authored type name it was given. | Enforce exact legal combinations, reject mixed forms, normalize `type: enum` + `values:` to string-backed enum lowering, and preserve legacy behavior. | One lowering story with fail-loud authored-surface rules. | New inline form emits the same lowered schema as legacy string enum form. | `tests/test_output_schema_lowering.py`, `tests/test_final_output.py` |
| Parse-surface proof | `tests/test_output_schema_surface.py` | parser/model assertions | Covers output-schema parse and inheritance shape, but not the new inline enum form. | Add coverage for new `type: enum` + `values:` parse shape and fail-loud mixed or incomplete forms. | The new syntax starts at the authored surface. | Parser/model contract for the new form. | direct |
| Lowering proof | `tests/test_output_schema_lowering.py` | inline lowering assertions | Proves legacy optional enum lowering only. | Add new-form lowering cases and legacy-compatibility cases with identical emitted wire shape. | The plan promises no wire-shape drift. | Same `type: string` plus `enum` JSON Schema output. | direct |
| Final-output proof | `tests/test_final_output.py` | structured final-output render and emitted schema assertions | Uses legacy inline enum syntax in several schema-bearing tests. | Update those authored sources to the new preferred syntax and add focused compatibility coverage so the old form still compiles. | Final-output behavior is part of the public surface. | Same rendered payload-field and example behavior. | direct |
| Diagnostic smoke helpers | `doctrine/_diagnostic_smoke/fixtures_final_output.py`, `doctrine/_diagnostic_smoke/compile_checks.py` | shared structured-final-output helper prompts and compile smoke checks | Helper prompt sources teach legacy inline enum syntax. | Update helper prompt sources that represent normal enum-bearing schemas to the new preferred syntax. Keep invalid-type smoke focused on invalid type behavior. | Diagnostic smoke and contributor examples should not keep teaching the old normal style. | Shared smoke prompt surface matches shipped style. | `make verify-diagnostics` |
| Shipped example prompts | `examples/79_final_output_output_schema/prompts/AGENTS.prompt`, `OPTIONAL_NO_EXAMPLE.prompt`, `INVALID_INVALID_EXAMPLE.prompt` | main structured-final-output teaching prompts | Teach legacy inline enum syntax. | Rewrite affected prompt files to the new preferred syntax. Leave prompts with no inline enums unchanged. | Example 79 is the main shipped teaching path for this surface. | Same manifest-backed behavior, new authored syntax. | `make verify-examples` |
| Review JSON example prompts | `examples/85_review_split_final_output_output_schema/prompts/AGENTS.prompt`, `examples/90_split_handoff_and_final_output_shared_route_semantics/prompts/AGENTS.prompt` | review-final structured-output teaching prompts | Teach legacy inline enum syntax on `route`. | Rewrite those prompts to the new preferred syntax. | The review-final JSON examples should not drift from the new normal style. | Same manifest-backed behavior, new authored syntax. | `make verify-examples` |
| Live language docs | `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/EMIT_GUIDE.md` | output-schema language and structured-final-output guidance | Explain output-schema ownership and emitted schema, but do not teach the new syntax yet. | Add the new inline enum syntax as the preferred local form and explain additive compatibility at the language level. | User-facing docs must match the shipped syntax. | New preferred authored form. | docs review plus existing proof |
| Release and compatibility docs | `docs/VERSIONING.md`, `CHANGELOG.md` | public release policy and unreleased notes | No entry for this new additive syntax yet. | Record the change as an additive public language surface and add the release note. | Public compatibility posture is part of shipped truth. | Additive release classification and language-version guidance. | release-doc alignment |
| Error catalog | `docs/COMPILER_ERRORS.md` | output-schema error documentation | Documents existing structured-final-output compile errors only. | Add the new malformed-inline-enum authoring diagnostics and their canonical messages. | Fail-loud authored-surface errors are part of the shipped public truth. | New output-schema authoring errors. | `make verify-diagnostics` |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - authored syntax in `doctrine/grammars/doctrine.lark` and
    `doctrine/_parser/io.py`
  - model in `doctrine/_model/io.py`
  - one normalization and lowering path in
    `doctrine/_compiler/resolve/output_schemas.py`
- Deprecated APIs (if any):
  - none in the first cut
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - no code-path delete in the first cut
  - rewrite shipped example prompts and diagnostic helper prompt strings that
    still present legacy inline enums as the normal style
- Adjacent surfaces tied to the same contract family:
  - parse/model proof in `tests/test_output_schema_surface.py`
  - lowering proof in `tests/test_output_schema_lowering.py`
  - final-output proof in `tests/test_final_output.py`
  - diagnostic smoke helpers under `doctrine/_diagnostic_smoke/`
  - manifest-backed example prompts under examples 79, 85, and 90
  - live docs for language, agent I/O, emit behavior, versioning, and changelog
- Compatibility posture / cutover plan:
  - additive first cut
  - old exact form stays supported
  - new exact form becomes the preferred shipped style in docs and examples
- Capability-replacing harnesses to delete or justify:
  - none; this is a direct language-path extension
- Live docs/comments/instructions to update or delete:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/EMIT_GUIDE.md`
  - `docs/VERSIONING.md`
  - `CHANGELOG.md`
  - `docs/COMPILER_ERRORS.md`
- Behavior-preservation signals for refactors:
  - `uv run --locked python -m unittest tests.test_output_schema_surface`
  - `uv run --locked python -m unittest tests.test_output_schema_lowering`
  - `uv run --locked python -m unittest tests.test_final_output`
  - `make verify-examples`
  - `make verify-diagnostics` when smoke fixtures or documented diagnostics change

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Structured-final-output teaching examples | `examples/79_final_output_output_schema/prompts/*.prompt`, `examples/85_review_split_final_output_output_schema/prompts/AGENTS.prompt`, `examples/90_split_handoff_and_final_output_shared_route_semantics/prompts/AGENTS.prompt` | Show `type: enum` plus `values:` as the preferred local inline enum form | Prevent the shipped corpus from teaching two competing “normal” styles | include |
| Diagnostic smoke helpers | `doctrine/_diagnostic_smoke/fixtures_final_output.py` | Use the new preferred inline enum form in helper sources that represent normal authored schema | Prevent smoke fixtures and contributor examples from drifting from shipped docs/examples | include |
| Legacy inline enum support | output-schema compile path | Keep `type: string` plus `enum:` legal in the first cut | Prevent a breaking cutover while the docs/examples move to the new style | include |
| Error documentation | `docs/COMPILER_ERRORS.md` | Document the malformed `type: enum` / `values:` authored-surface diagnostics | Prevent shipped diagnostics and public docs from drifting apart | include |
| Broad docs index links | `docs/AUTHORING_PATTERNS.md` | Rewrite link-only sections just because linked example prompts change | The doc mostly points at example files; changing those prompts already updates the linked truth | exclude |
| Named enum refs in output schema | output-schema language surface | Add `enum: SectionEdit` or other named-enum reuse in the same change | That is a different language design problem and was already ruled out by scope | exclude |
| Numeric or boolean local enums | output-schema language surface | Generalize the new inline form beyond string-backed local vocabularies | That would widen the feature and the diagnostics surface beyond the confirmed North Star | exclude |

<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 - Inline Enum Syntax And Model Foundation

Status: COMPLETE

Completed work:
- Added `values:` to the output-schema grammar without changing the `type:`
  parse path.
- Added the parser transform and new `OutputSchemaValues` model node while
  keeping the legacy `enum:` node intact.
- Added parse-surface coverage for new-form fields, nested fields, and legacy
  enum fields.

Goal

- Create the new authored `type: enum` plus `values:` surface on the existing
  output-schema path while preserving the current legacy parse surface.

Work

- Extend the grammar, parser, and model so the compiler can represent the new
  authored form without adding a second schema subsystem.

Checklist (must all be done)

- Extend [doctrine/grammars/doctrine.lark](doctrine/grammars/doctrine.lark) so
  `output_schema_item_line` accepts a new `values:` block for output-schema
  fields and nested fields.
- Keep the `type:` grammar unchanged so `type: enum` continues to parse through
  the existing named-setting path instead of introducing a second `type`
  parser.
- Add the parser transform for the new `values:` block in
  [doctrine/_parser/io.py](doctrine/_parser/io.py).
- Add one source-aware model node for the new `values:` block in
  [doctrine/_model/io.py](doctrine/_model/io.py) and export it through
  [doctrine/model.py](doctrine/model.py).
- Keep the legacy `enum:` block model and parser path intact in the first cut.
- Add focused parser and model coverage in
  [tests/test_output_schema_surface.py](tests/test_output_schema_surface.py) for:
  - the new `type: enum` plus `values:` authored form
  - the legacy `type: string` plus `enum:` authored form
  - nested field usage of the new form
  - the new source-aware node reaching the parsed declaration tree

Verification (required proof)

- `uv run --locked python -m unittest tests.test_output_schema_surface`

Docs/comments (propagation; only if needed)

- Add one short code comment only if the new source-aware values node or its
  parser boundary would otherwise be hard to follow.

Exit criteria (all required)

- The parser can represent the new `values:` block on `output schema` fields
  without ambiguity.
- The legacy authored form still parses unchanged.
- The parsed tree carries enough source identity for later lowering to
  distinguish legacy `enum:` from new `values:`.
- No new output-schema subsystem or alternate type parser was introduced.

Rollback

- Revert the grammar, parser, and model changes together before any lowering or
  docs work lands if the authored shape proves ambiguous.

## Phase 2 - Lowering Normalization And Fail-Loud Compatibility

Status: COMPLETE

Completed work:
- Extended the output-schema lowering parts model to track legacy `enum:` and
  new `values:` sources separately before normalization.
- Added fail-loud compile diagnostics for missing `values:`, invalid
  `values:` pairings, and mixed legacy/new inline enum forms.
- Normalized `type: enum` plus `values:` onto the same lowered string-enum
  wire shape used by the legacy form.
- Updated focused lowering and final-output proof so the new form is the
  normal authored path and the legacy form stays covered explicitly.

Goal

- Make the two legal authored forms lower to the same string-backed wire shape
  and fail loud for malformed combinations before they degrade into generic
  invalid-schema behavior.

Work

- Extend the existing output-schema lowering path so it validates exact authored
  combinations, normalizes the new form onto the existing string-enum wire
  shape, and preserves final-output behavior.

Checklist (must all be done)

- Extend `_OutputSchemaNodeParts` and the output-schema prepass in
  [doctrine/_compiler/resolve/output_schemas.py](doctrine/_compiler/resolve/output_schemas.py)
  so the compiler can distinguish legacy `enum:` from new `values:` sources.
- Preserve the legacy legal form: `type: string` plus `enum:`.
- Add the new legal form: `type: enum` plus `values:`.
- Normalize the new legal form to the same lowered JSON Schema emitted by the
  legacy string-backed form:
  - `"type": "string"`
  - `"enum": [...]`
- Reject malformed authored combinations with explicit compile-time diagnostics:
  - `type: enum` without `values:`
  - `values:` without `type: enum`
  - `type: string` plus `values:`
  - `type: enum` plus legacy `enum:`
- Add lowering coverage in
  [tests/test_output_schema_lowering.py](tests/test_output_schema_lowering.py)
  for:
  - the new legal form
  - legacy-compatibility lowering
  - optional enum widening to `null`
  - malformed authored combinations
- Update enum-bearing authored sources in
  [tests/test_final_output.py](tests/test_final_output.py) to the new preferred
  syntax where they represent the normal authored path.
- Add at least one focused final-output compatibility assertion that the legacy
  authored form still compiles and renders correctly in the first cut.

Verification (required proof)

- `uv run --locked python -m unittest tests.test_output_schema_lowering`
- `uv run --locked python -m unittest tests.test_final_output`

Docs/comments (propagation; only if needed)

- Add one short comment at the canonical normalization boundary in
  [doctrine/_compiler/resolve/output_schemas.py](doctrine/_compiler/resolve/output_schemas.py)
  only if the source-form normalization is not obvious from the types.

Exit criteria (all required)

- Both legal authored forms emit the same string-backed wire schema.
- Malformed authored combinations fail loud before they fall through as generic
  invalid JSON Schema type errors.
- Final-output rendering, emitted schema shape, and nullable-enum behavior stay
  unchanged for equivalent schemas.
- Focused proof shows the legacy authored form still works in the first cut.

Rollback

- Revert the lowering, diagnostics, and focused proof together if the new form
  cannot normalize cleanly without wire-shape drift.

## Phase 3 - Shipped Proof Surface Convergence

Status: COMPLETE

Completed work:
- Rewrote the shared final-output diagnostic fixtures to use the new inline
  enum form for normal structured-output schemas.
- Rewrote the shipped example prompts in examples 79, 85, and 90 to use
  `type: enum` plus `values:` for local inline enums.
- Kept manifest-backed and smoke-backed emitted behavior stable while the
  authored surface changed.

Goal

- Move the shipped proof surfaces to the new preferred inline enum form while
  keeping public behavior and manifest-backed outputs unchanged.

Work

- Update the diagnostic smoke helpers and shipped example prompts that currently
  teach legacy inline enums as the normal style, then run the repo’s proof
  surfaces for those artifacts.

Checklist (must all be done)

- Update the normal enum-bearing helper prompt sources in
  [doctrine/_diagnostic_smoke/fixtures_final_output.py](doctrine/_diagnostic_smoke/fixtures_final_output.py)
  to the new preferred authored form.
- Update any dependent diagnostic smoke expectations in
  [doctrine/_diagnostic_smoke/compile_checks.py](doctrine/_diagnostic_smoke/compile_checks.py)
  so they stay aligned with the new helper sources and the chosen authored
  diagnostics.
- Rewrite the enum-bearing shipped prompts in
  [examples/79_final_output_output_schema/prompts/AGENTS.prompt](examples/79_final_output_output_schema/prompts/AGENTS.prompt),
  [OPTIONAL_NO_EXAMPLE.prompt](examples/79_final_output_output_schema/prompts/OPTIONAL_NO_EXAMPLE.prompt),
  and
  [INVALID_INVALID_EXAMPLE.prompt](examples/79_final_output_output_schema/prompts/INVALID_INVALID_EXAMPLE.prompt)
  to the new preferred authored form.
- Rewrite the enum-bearing shipped prompts in
  [examples/85_review_split_final_output_output_schema/prompts/AGENTS.prompt](examples/85_review_split_final_output_output_schema/prompts/AGENTS.prompt)
  and
  [examples/90_split_handoff_and_final_output_shared_route_semantics/prompts/AGENTS.prompt](examples/90_split_handoff_and_final_output_shared_route_semantics/prompts/AGENTS.prompt)
  to the new preferred authored form.
- Leave shipped prompt files with no inline enum fields unchanged.
- Keep manifest-backed expected outputs stable unless a deliberately improved
  authored diagnostic message requires an aligned expectation update.
- Run the example and diagnostic proof after those source changes land.

Verification (required proof)

- `make verify-examples`
- `make verify-diagnostics`

Docs/comments (propagation; only if needed)

- No extra code comments are planned in this phase. The work is source-truth
  convergence across proof surfaces.

Exit criteria (all required)

- The main shipped proof surfaces now teach `type: enum` plus `values:` as the
  normal local inline enum form.
- Manifest-backed example verification passes.
- Diagnostic smoke verification passes.
- Legacy-syntax support remains covered by the focused compatibility proof from
  Phase 2 rather than by leaving the shipped examples on the old form.

Rollback

- Revert the proof-surface source changes together if they expose an unresolved
  wire-shape or diagnostic regression in the earlier phases.

## Phase 4 - Public Docs And Release Truth Alignment

Status: COMPLETE

Completed work:
- Updated the language reference, agent I/O notes, and emit guide to show
  `type: enum` plus `values:` as the preferred local inline enum form.
- Updated the compiler error catalog with the new malformed inline-enum
  diagnostics.
- Updated versioning guidance and changelog truth for the additive first cut.

Goal

- Make the public docs, compatibility guidance, and release notes tell the same
  additive story as the shipped code and proof surfaces.

Work

- Update the live docs that explain `output schema`, structured final output,
  diagnostics, and release classification so they teach the new syntax as the
  preferred inline form and keep the additive-first-cut posture explicit.

Checklist (must all be done)

- Update [docs/LANGUAGE_REFERENCE.md](docs/LANGUAGE_REFERENCE.md) so the
  `output schema` surface teaches `type: enum` plus `values:` as the preferred
  local inline enum form and still states that the first cut preserves legacy
  syntax compatibility.
- Update
  [docs/AGENT_IO_DESIGN_NOTES.md](docs/AGENT_IO_DESIGN_NOTES.md) where it
  explains structured outputs so the new preferred authored form is visible.
- Update [docs/EMIT_GUIDE.md](docs/EMIT_GUIDE.md) where it explains structured
  final outputs so the emitted-schema story stays aligned with the new authored
  syntax.
- Update [docs/COMPILER_ERRORS.md](docs/COMPILER_ERRORS.md) with the malformed
  inline-enum authored-surface diagnostics and their canonical messages.
- Update [docs/VERSIONING.md](docs/VERSIONING.md) so the language-version and
  additive-release guidance explicitly covers this new inline syntax.
- Add the release note entry in [CHANGELOG.md](CHANGELOG.md) for the new
  additive inline-enum syntax.

Verification (required proof)

- Re-run `make verify-diagnostics` after the documented diagnostic surface is
  updated.

Docs/comments (propagation; only if needed)

- No direct [docs/AUTHORING_PATTERNS.md](docs/AUTHORING_PATTERNS.md) edit is
  planned. Its linked example prompts carry the authored-syntax update once the
  shipped examples are rewritten in Phase 3.

Exit criteria (all required)

- Public docs show the new inline enum form as the preferred local authored
  style.
- The additive first-cut compatibility posture is explicit in public docs and
  release truth.
- The error catalog matches the shipped malformed-inline-enum diagnostics.
- The changelog and versioning guide are aligned with the shipped language
  surface.

Rollback

- Revert the docs and release-truth edits together if the implementation
  surface changes again before release and the published wording would become
  stale.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

- Run:
  - `uv run --locked python -m unittest tests.test_output_schema_surface`
  - `uv run --locked python -m unittest tests.test_output_schema_lowering`
  - `uv run --locked python -m unittest tests.test_final_output`
- Run `make verify-examples` because shipped manifest-backed prompt sources will
  change.
- Run `make verify-diagnostics` because diagnostic smoke helpers and documented
  diagnostics are part of the chosen shipped work.
- Keep release docs and versioning truth aligned in the same patch because this
  is a public additive language surface.

# 9) Rollout / Ops / Telemetry

This is a language and docs rollout, not an ops rollout. The main rollout work
is public release classification, upgrade wording, and keeping the docs honest
about the additive first cut.

# 10) Decision Log (append-only)

- 2026-04-16: Draft plan created for inline `output schema` enum syntax.
- 2026-04-16: Default compatibility posture set to additive first cut.
- 2026-04-16: Default scope assumes `type: enum` is string-backed and uses a
  local `values:` list.
- 2026-04-16: Named enum refs for `output schema` are out of scope for this
  change.
- 2026-04-16: North Star confirmed with additive compatibility posture and the
  new inline form as the preferred shipped style.
- 2026-04-16: Deep-dive locked the exact authored forms: legacy
  `type: string` plus `enum:` remains legal, and the new preferred form is
  `type: enum` plus `values:`.
- 2026-04-16: Deep-dive kept one lowering story on the existing output-schema
  path and rejected a second schema subsystem or a same-change named-enum
  reuse surface.
- 2026-04-16: Phase-plan split implementation into four coherent units:
  syntax/model foundation, lowering plus fail-loud compatibility, proof-surface
  convergence, and public docs plus release truth.
- 2026-04-16: `implement-loop` was armed for this plan, `WORKLOG_PATH` was
  created, and Phase 1 started.
