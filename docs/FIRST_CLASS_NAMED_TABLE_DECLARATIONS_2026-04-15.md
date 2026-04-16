---
title: "Doctrine - First-Class Named Table Declarations - Architecture Plan"
date: 2026-04-15
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - docs/LANGUAGE_REFERENCE.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/VERSIONING.md
  - CHANGELOG.md
  - examples/README.md
  - examples/21_first_class_skills_blocks/prompts/AGENTS.prompt
  - examples/56_document_structure_attachments/prompts/AGENTS.prompt
  - examples/58_readable_document_blocks/prompts/AGENTS.prompt
  - examples/63_schema_artifacts_and_groups/prompts/AGENTS.prompt
  - doctrine/grammars/doctrine.lark
  - doctrine/model.py
  - doctrine/_model/readable.py
  - doctrine/_parser/readables.py
  - doctrine/_compiler/resolve/documents.py
  - doctrine/_compiler/resolve/document_blocks.py
  - doctrine/_compiler/compile/readables.py
  - doctrine/_compiler/compile/readable_blocks.py
  - doctrine/_compiler/validate/addressable_children.py
  - doctrine/_renderer/blocks.py
  - doctrine/_renderer/tables.py
---

# TL;DR

## Outcome

Add a first-class top-level `table` declaration and a typed document use site so authors can define a named table once and use it by name inside documents without changing rendered Markdown.

## Problem

Today `table` only exists as an inline document block. That means reusable table contracts can only be copied inline or hidden behind whole-document inheritance, which is heavier and less direct than the rest of Doctrine's named-type patterns.

## Approach

Make `table` a real top-level declaration, then let documents attach it with the same local-key-plus-type pattern Doctrine already uses elsewhere: `table release_gates: ReleaseGates required`. The declaration owns the title, columns, and optional `row_schema:`. The document use site owns placement, requirement, guard, and local `rows:` / `notes:`. Keep output rendering unchanged.

## Plan

1. Add the new first-class `table` declaration and typed document use-site syntax.
2. Resolve named tables into ordinary document table blocks so addressable paths, inheritance rules, and rendering stay consistent.
3. Prove the feature with one new manifest-backed example, targeted compiler tests, and updated language docs.
4. Update release-facing docs because this is a backward-compatible public language addition.

## Non-negotiables

- The new syntax must match existing named-type patterns and avoid new generic ref syntax.
- Existing inline document tables must keep working unchanged.
- Rendered Markdown must stay the same for the same logical table.
- The document use site must stay locally addressable by its own key.
- The first cut must solve named table reuse cleanly without turning all readable blocks into a new generic declaration family.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-15
recommended_flow: research -> deep dive -> phase plan -> consistency pass -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine ships a first-class top-level `table` declaration plus a typed document use site `table <local_key>: <TableDecl>`, then authors will be able to reuse named table contracts directly, current inline table authoring will keep working, and rendered Markdown will stay unchanged for equivalent authored tables.

## 0.2 In scope

- Add a top-level `table` declaration with the same core table body Doctrine already supports today:
  - `columns:`
  - `row_schema:` when needed
  - optional declaration-owned default `notes:`
- Add a document use site with the exact first-cut shape:

```prompt
table ReleaseGates: "Release Gates"
    columns:
        gate: "Gate"
            "What must pass before shipment."

        evidence: "Evidence"
            "What proves the gate passed."


document ReleaseGuide: "Release Guide"
    section summary: "Summary"
        "Lead with the release goal and the current shipment boundary."

    table release_gates: ReleaseGates required
        rows:
            release_notes:
                gate: "Release notes"
                evidence: "Linked to the shipped proof."

            package_smoke:
                gate: "Package smoke"
                evidence: "`make verify-package` passed."


output ReleaseGuideFile: "Release Guide File"
    target: File
        path: "release_root/RELEASE_GUIDE.md"
    shape: MarkdownDocument
    structure: ReleaseGuide
    requirement: Required
```

- Make the declaration own title, columns, and optional `row_schema:`.
- Make the document use site own:
  - the local block key
  - `required` / `advisory` / `optional`
  - `when <expr>`
  - local `rows:`
  - local `notes:`
- Resolve the named table into the same compiled table shape current inline document tables use so existing addressable-path and renderer behavior stays intact.
- Keep both of these addressable and truthful:
  - `ReleaseGates:columns.evidence.title`
  - `ReleaseGuide:release_gates.columns.evidence.title`
- Keep this behavior explicit in the plan:
  - `ReleaseGates` is the named reusable table type.
  - `release_gates` is the local document key, so inheritance and addressable paths stay stable.
  - The declaration owns the table title, columns, and optional `row_schema:`.
  - The use site owns placement metadata like `required`, `advisory`, `optional`, and `when`.
  - The use site may add local `rows:` and `notes:`. If it adds nothing, the table still renders as a contract table.
- Update docs, examples, tests, the examples index, `docs/VERSIONING.md`, and `CHANGELOG.md`.
- Add one new manifest-backed example for the named declaration pattern.

## 0.3 Out of scope

- A generic `ref:` document mechanism.
- A new top-level declaration family for every readable block kind in the same change.
- Local title override on `table release_gates: ReleaseGates` in the first cut.
- Declaration-owned concrete `rows:` in the first cut.
- New rendered Markdown shapes for named tables.
- Runtime fallbacks or compatibility shims.

## 0.4 Definition of done (acceptance evidence)

- The language supports this exact first-cut shape:

```prompt
table ReleaseGates: "Release Gates"
    columns:
        gate: "Gate"
            "What must pass before shipment."

        evidence: "Evidence"
            "What proves the gate passed."


document ReleaseGuide: "Release Guide"
    section summary: "Summary"
        "Lead with the release goal and the current shipment boundary."

    table release_gates: ReleaseGates required
        rows:
            release_notes:
                gate: "Release notes"
                evidence: "Linked to the shipped proof."

            package_smoke:
                gate: "Package smoke"
                evidence: "`make verify-package` passed."


output ReleaseGuideFile: "Release Guide File"
    target: File
        path: "release_root/RELEASE_GUIDE.md"
    shape: MarkdownDocument
    structure: ReleaseGuide
    requirement: Required
```

- With rows at the use site, emitted Markdown should look exactly like today's inline table output:

```md
| **Release Gates** | Table | Use the columns `Gate` and `Evidence`. |

##### Release Gates Contract

_Required · table_

| Gate | Evidence |
| --- | --- |
| Release notes | Linked to the shipped proof. |
| Package smoke | `make verify-package` passed. |
```

- If the named table is used with no local rows, it should render the current contract form, not a new special format:

```md
##### Release Gates Contract

_Advisory · table_

| Column | Meaning |
| --- | --- |
| Gate | What must pass before shipment. |
| Evidence | What proves the gate passed. |
```

- Existing inline document tables still compile, resolve, and render with no authored changes.
- Addressable paths work on both the declaration root and the document-local block key:
  - `ReleaseGates:columns.evidence.title`
  - `ReleaseGuide:release_gates.columns.evidence.title`
  - `ReleaseGuide:release_gates.rows.package_smoke`
- Fail-loud diagnostics cover wrong declaration kind, duplicate local block keys, and invalid table use-site bodies.
- Docs and examples teach the new named table pattern and keep generic naming.
- Relevant verification passes run green.

## 0.5 Key invariants (fix immediately if violated)

- No generic ref indirection for this feature.
- No second renderer path for named tables.
- No loss of document-local addressability.
- No silent behavior drift for existing inline tables.
- No new parallel ownership path for table structure inside documents.
- No fallback or bridge syntax.
- The user-facing syntax must stay typed and local: `table release_gates: ReleaseGates`, not a path-based reuse workaround.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Make the syntax feel like a native Doctrine type, not a workaround.
2. Keep current rendered Markdown and current inline table behavior stable.
3. Preserve document-local ownership and addressable paths.
4. Reuse existing named-type and typed-use-site patterns already in the language.
5. Keep docs, examples, and tests as clear as the feature itself.

## 1.2 Constraints

- The grammar already treats `table` as a readable document block kind.
- Table columns, rows, row schema, and structured cell bodies already exist and have shipped behavior.
- Current examples already teach top-level named declarations plus keyed local use sites for other kinds.
- Public docs say `table` is a document block today, so the docs must be updated carefully and truthfully.
- `docs/VERSIONING.md` requires a minor language version update for a new backward-compatible public syntax surface.

## 1.3 Architectural principles (rules we will enforce)

- A named table declaration owns table structure.
- A document use site owns placement and local authored row content.
- The compiler should lower named table use into the same internal table shape the renderer already knows.
- Existing inline tables stay first-class and do not become a deprecated compatibility path in this change.
- The first cut should solve named table reuse only, without inventing a generic reusable-readable system.
- The new surface should match current named declaration patterns like top-level `document` and `schema`, plus keyed local attachment patterns like `skill grounding: GroundingSkill`.

## 1.4 Known tradeoffs (explicit)

- Restricting declaration ownership to title, columns, and optional row schema keeps the first cut small and canonical, but it means declaration-owned sample rows are not part of the initial feature.
- That tradeoff is good because the main reuse pain is the table contract, not shared row data.
- Keeping local title override out of the first cut makes the syntax cleaner and keeps ownership obvious.
- Reject path-based reuse like `ref: SharedDoc:release_gates` for this feature. That is a workaround for tables only existing inside documents, not the clean first-class table type this plan is meant to add.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine supports rich readable table blocks inside `document` bodies. Those blocks already support `columns:`, `rows:`, `row_schema:`, and structured cell bodies. Doctrine also already supports first-class named declarations with typed local attachments in other parts of the language.

## 2.2 What’s broken / missing (concrete)

- There is no first-class top-level `table` declaration today.
- Reusing a table contract means either copying it inline or reusing a whole document that happens to contain it.
- That is less direct than Doctrine's current named-type patterns and heavier than the author intent.
- The language already has a good-looking shape for this kind of reuse elsewhere, but tables do not get that treatment yet.

## 2.3 Constraints implied by the problem

- The fix should look like an obvious extension of current Doctrine, not a special-case alias or generic ref system.
- The change must preserve current inline table authoring.
- The feature must keep document-local keys because those keys drive interpolation, inheritance, and readability.
- The public language, examples, docs, and proof surfaces all need to move together.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- none — reject generic reusable-block prior art here — this feature should follow Doctrine's own named declaration and typed attachment patterns instead of importing a new composition model

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - [doctrine/grammars/doctrine.lark](doctrine/grammars/doctrine.lark) — the shipped declaration list currently has top-level `schema`, `document`, `workflow`, `skill`, `output target`, and related declarations, but no top-level `table`; the same file also defines `readable_table_block` and `override_readable_table_block`, which is why tables only exist as document-readable blocks today
  - [doctrine/_parser/readables.py](doctrine/_parser/readables.py) — owns current table parsing for `columns:`, `rows:`, `row_schema:`, `notes:`, and structured cell bodies, so a first-class named table should reuse this table-body path instead of growing a second mini-language
  - [doctrine/_model/readable.py](doctrine/_model/readable.py) — owns `ReadableTableColumn`, `ReadableTableRow`, `ReadableTableCell`, `ReadableTableData`, and `DocumentDecl`; the new feature should reuse the current table payload model instead of inventing a second table shape
  - [doctrine/_model/declarations.py](doctrine/_model/declarations.py), [doctrine/model.py](doctrine/model.py), [doctrine/_compiler/constants.py](doctrine/_compiler/constants.py), and [doctrine/_compiler/indexing.py](doctrine/_compiler/indexing.py) — own the first-class declaration union, readable declaration registries, addressable-root registries, and per-unit declaration maps; a top-level `table` must join these surfaces to behave like a real named type
  - [doctrine/_compiler/resolve/document_blocks.py](doctrine/_compiler/resolve/document_blocks.py) — `_resolve_readable_table_payload` is the canonical table semantics path today: it enforces column existence, duplicate-key failures, row-schema lowering, single-line inline cells, and structured cell bodies
  - [doctrine/_compiler/resolve/addressables.py](doctrine/_compiler/resolve/addressables.py) and [doctrine/_compiler/validate/addressable_children.py](doctrine/_compiler/validate/addressable_children.py) — own current addressable root lookup and table descendant traversal; declaration-root and document-root paths must both stay truthful after the change
  - [doctrine/_compiler/compile/readable_blocks.py](doctrine/_compiler/compile/readable_blocks.py), [doctrine/_renderer/blocks.py](doctrine/_renderer/blocks.py), and [doctrine/_renderer/tables.py](doctrine/_renderer/tables.py) — own the compiled table block and current Markdown render path; named tables should lower into this path unchanged
  - [doctrine/_compiler/compile/outputs.py](doctrine/_compiler/compile/outputs.py) — `_output_structure_summary_text` is the current structure-attachment summary path that emits `Use the columns ...` or note summaries for document tables, so named tables must preserve that output contract
- Canonical path / owner to reuse:
  - top-level declaration parse and indexing for table identity, plus the existing readable-table parse -> resolve -> compile -> render path for table behavior — this feature should extend those two paths and join them at the document use site instead of creating a generic ref system or a second renderer path
- Adjacent surfaces tied to the same contract family:
  - [docs/LANGUAGE_REFERENCE.md](docs/LANGUAGE_REFERENCE.md) — the public syntax and addressability story currently say `table` is a document block kind only
  - [docs/LANGUAGE_DESIGN_NOTES.md](docs/LANGUAGE_DESIGN_NOTES.md) — should record why first-class named tables fit Doctrine's current patterns better than a generic ref mechanism
  - [docs/AGENT_IO_DESIGN_NOTES.md](docs/AGENT_IO_DESIGN_NOTES.md) — should stay aligned on how `structure:` attachments expose document tables without implying any new render shape
  - [docs/VERSIONING.md](docs/VERSIONING.md) and [CHANGELOG.md](../CHANGELOG.md) — this is a backward-compatible public language surface, so the version and release story must move with the implementation
  - [examples/21_first_class_skills_blocks/prompts/AGENTS.prompt](../examples/21_first_class_skills_blocks/prompts/AGENTS.prompt), [examples/56_document_structure_attachments/prompts/AGENTS.prompt](../examples/56_document_structure_attachments/prompts/AGENTS.prompt), and [examples/63_schema_artifacts_and_groups/prompts/AGENTS.prompt](../examples/63_schema_artifacts_and_groups/prompts/AGENTS.prompt) — these are the shipped pattern anchors for top-level named declarations and keyed local typed attachments
  - [examples/58_readable_document_blocks/prompts/AGENTS.prompt](../examples/58_readable_document_blocks/prompts/AGENTS.prompt) — the current inline-table teaching example must stay valid
  - [examples/59_document_inheritance_and_descendants/prompts/AGENTS.prompt](../examples/59_document_inheritance_and_descendants/prompts/AGENTS.prompt) — shows the current whole-document inheritance workaround for table reuse and proves descendant refs must stay stable
  - [examples/65_row_and_item_schemas/prompts/AGENTS.prompt](../examples/65_row_and_item_schemas/prompts/AGENTS.prompt) and [examples/66_late_extension_blocks/prompts/AGENTS.prompt](../examples/66_late_extension_blocks/prompts/AGENTS.prompt) — row-schema descendants and structured table-cell bodies must stay intact on the named path
  - [examples/README.md](../examples/README.md) — the corpus index and learning path must teach the new example cleanly
  - [tests/test_output_rendering.py](../tests/test_output_rendering.py) — already protects document-structure rendering for tables and is the closest unit proof for unchanged table output shape
  - [tests/test_parse_diagnostics.py](../tests/test_parse_diagnostics.py) — already protects fail-loud table parse behavior such as duplicate `row_schema:`
- Compatibility posture (separate from `fallback_policy`):
  - preserve existing contract with additive syntax — existing inline tables and current rendered Markdown keep working unchanged, no authored migration is required, and `docs/VERSIONING.md` says a new backward-compatible language surface like this should bump the Doctrine language version minor when it ships publicly
- Existing patterns to reuse:
  - [examples/56_document_structure_attachments/prompts/AGENTS.prompt](../examples/56_document_structure_attachments/prompts/AGENTS.prompt) and [examples/63_schema_artifacts_and_groups/prompts/AGENTS.prompt](../examples/63_schema_artifacts_and_groups/prompts/AGENTS.prompt) — top-level named declaration pattern
  - [examples/21_first_class_skills_blocks/prompts/AGENTS.prompt](../examples/21_first_class_skills_blocks/prompts/AGENTS.prompt) — keyed local typed attachment pattern `skill grounding: GroundingSkill`
  - [examples/59_document_inheritance_and_descendants/prompts/AGENTS.prompt](../examples/59_document_inheritance_and_descendants/prompts/AGENTS.prompt) — document-local descendant paths stay stable under the local key
- Prompt surfaces / agent contract to reuse:
  - none — this feature is compiler and language only
- Native model or agent capabilities to lean on:
  - none — this feature is compiler and language only
- Existing grounding / tool / file exposure:
  - current grammar, parser, model, compiler, docs, examples, and tests already expose every affected surface; no new tool, wrapper, or harness surface is needed
- Duplicate or drifting paths relevant to this change:
  - whole-document inheritance like `inherit step_arc` in [examples/59_document_inheritance_and_descendants/prompts/AGENTS.prompt](../examples/59_document_inheritance_and_descendants/prompts/AGENTS.prompt) is the current reuse workaround for tables; named tables should remove the need for that workaround when the author wants table-only reuse
  - inline-only table authoring in [examples/58_readable_document_blocks/prompts/AGENTS.prompt](../examples/58_readable_document_blocks/prompts/AGENTS.prompt) and [examples/65_row_and_item_schemas/prompts/AGENTS.prompt](../examples/65_row_and_item_schemas/prompts/AGENTS.prompt) is the only direct table path today; the new feature must converge with it instead of forking behavior
  - top-level declaration registries currently have no table entry, which is why table semantics live only under document block handling today
- Capability-first opportunities before new tooling:
  - direct compiler-path extension is enough — add a real `table` declaration and a typed document use site instead of a generic `ref:`, sidecar registry, or extra tooling
- Behavior-preservation signals already available:
  - [tests/test_output_rendering.py](../tests/test_output_rendering.py) — protects structure rendering for document tables
  - [tests/test_parse_diagnostics.py](../tests/test_parse_diagnostics.py) — protects fail-loud parse behavior on table bodies
  - [examples/58_readable_document_blocks/cases.toml](../examples/58_readable_document_blocks/cases.toml) — protects the current no-row contract-table render shape
  - [examples/59_document_inheritance_and_descendants/cases.toml](../examples/59_document_inheritance_and_descendants/cases.toml) — protects descendant refs and the row-backed table render shape
  - [examples/65_row_and_item_schemas/cases.toml](../examples/65_row_and_item_schemas/cases.toml) — protects row-schema descendants and table output
  - `make verify-examples` and `make verify-diagnostics` when diagnostics move

## 3.3 Decision gaps that must be resolved before implementation

- none — repo evidence checked: grammar, parser, declaration registries, addressable-path handling, current table resolve and render paths, current inline-table examples, document-inheritance reuse example, row-schema example, and existing table render/parse proof — default recommendation: add a real top-level `table` declaration, add `table <local_key>: <TableDecl>` inside `document`, preserve current inline tables and current Markdown output, and ship it as an additive public language feature — answer needed: none; the user confirmed this direction
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- [doctrine/grammars/doctrine.lark](doctrine/grammars/doctrine.lark) has no top-level `table` declaration today. It only defines document-table syntax through `readable_table_block` and `override_readable_table_block`.
- [doctrine/parser.py](doctrine/parser.py) and [doctrine/_parser/readables.py](doctrine/_parser/readables.py) parse tables only through the readable-block path. There is no table-declaration transform and no typed document table-use form.
- [doctrine/_model/readable.py](doctrine/_model/readable.py) models table semantics as `ReadableTableData` payload on `ReadableBlock`. [doctrine/_model/declarations.py](doctrine/_model/declarations.py) and [doctrine/model.py](doctrine/model.py) export no `TableDecl`.
- [doctrine/_compiler/indexing.py](doctrine/_compiler/indexing.py), [doctrine/_compiler/constants.py](doctrine/_compiler/constants.py), and [doctrine/_compiler/validate/__init__.py](doctrine/_compiler/validate/__init__.py) maintain declaration registries and addressable-root registries with no `tables_by_name` entry and no `table declaration` label.
- [doctrine/_compiler/resolve/documents.py](doctrine/_compiler/resolve/documents.py) and [doctrine/_compiler/resolve/document_blocks.py](doctrine/_compiler/resolve/document_blocks.py) own all table resolution today because tables only exist as document blocks.
- [doctrine/_compiler/resolve/addressables.py](doctrine/_compiler/resolve/addressables.py) and [doctrine/_compiler/validate/addressable_children.py](doctrine/_compiler/validate/addressable_children.py) expose table descendants only through document-local block keys.
- [doctrine/_compiler/compile/readable_blocks.py](doctrine/_compiler/compile/readable_blocks.py), [doctrine/_renderer/blocks.py](doctrine/_renderer/blocks.py), [doctrine/_renderer/tables.py](doctrine/_renderer/tables.py), and [doctrine/_compiler/compile/outputs.py](doctrine/_compiler/compile/outputs.py) own compiled table rendering and the structure-summary line `Use the columns ...`.
- Public truth and proof live in [docs/LANGUAGE_REFERENCE.md](docs/LANGUAGE_REFERENCE.md), [docs/LANGUAGE_DESIGN_NOTES.md](docs/LANGUAGE_DESIGN_NOTES.md), [docs/AGENT_IO_DESIGN_NOTES.md](docs/AGENT_IO_DESIGN_NOTES.md), [examples/58_readable_document_blocks](../examples/58_readable_document_blocks), [examples/59_document_inheritance_and_descendants](../examples/59_document_inheritance_and_descendants), [examples/65_row_and_item_schemas](../examples/65_row_and_item_schemas), [tests/test_output_rendering.py](../tests/test_output_rendering.py), and [tests/test_parse_diagnostics.py](../tests/test_parse_diagnostics.py).

## 4.2 Control paths (runtime)

1. Parse top-level declarations into `PromptFile`. No top-level `table` declaration can load, import, or index today.
2. Parse `document ... table key: "Title"` into `DocumentBlock(kind="table", ...)` with `ReadableTableData(columns, rows, notes, row_schema)`.
3. Resolve document inheritance in [doctrine/_compiler/resolve/documents.py](doctrine/_compiler/resolve/documents.py). Tables participate only as ordinary document blocks keyed by the local block key.
4. Resolve table payload in [doctrine/_compiler/resolve/document_blocks.py](doctrine/_compiler/resolve/document_blocks.py) through `_resolve_readable_table_payload`, which enforces column existence, duplicate-key failures, row-schema lowering, single-line inline-cell rules, and structured cell-body handling.
5. Resolve addressable paths through the document root plus the local table key. That is why `ReleaseGuide:release_gates.columns.evidence.title` works today.
6. Compile structure summaries in [doctrine/_compiler/compile/outputs.py](doctrine/_compiler/compile/outputs.py). If notes exist, they become the summary. Otherwise the compiler emits `Use the columns ...`.
7. Render tables in [doctrine/_renderer/blocks.py](doctrine/_renderer/blocks.py): no rows produces the current contract table, rows produce the normal pipe table, and structured cells route to the structured-table renderer.
8. Reusing one table contract across documents today means copying it inline or reusing a whole document and `inherit`-ing the table block, as shown in [examples/59_document_inheritance_and_descendants/prompts/AGENTS.prompt](../examples/59_document_inheritance_and_descendants/prompts/AGENTS.prompt).

## 4.3 Object model + key abstractions

- There is no `TableDecl`, no `tables_by_name` registry, and no `_resolve_table_ref`.
- `table` is already a stable document block kind, and document inheritance already keys override behavior on `kind == "table"`.
- `ReadableTableData` is the one compiler-owned table shape from parse through render today.
- Output structure attachments and Markdown rendering both depend on resolved `ReadableTableData`, not on any declaration-level table abstraction.

## 4.4 Observability + failure behavior today

- Duplicate declaration names fail loud generically in [doctrine/_compiler/indexing.py](doctrine/_compiler/indexing.py).
- Duplicate `row_schema:` blocks fail loud at parse time, as covered in [tests/test_parse_diagnostics.py](../tests/test_parse_diagnostics.py).
- Duplicate table columns, duplicate rows, duplicate row cells, unknown column refs, and multiline inline cells fail loud during document-block resolution in [doctrine/_compiler/resolve/document_blocks.py](doctrine/_compiler/resolve/document_blocks.py).
- Structure-summary and rendered-table behavior are already covered by [tests/test_output_rendering.py](../tests/test_output_rendering.py) and the manifest-backed examples [58](../examples/58_readable_document_blocks/cases.toml), [59](../examples/59_document_inheritance_and_descendants/cases.toml), and [65](../examples/65_row_and_item_schemas/cases.toml).
- There is no wrong-kind or missing-ref diagnostic path for named tables yet because the language has no `table` declaration ref surface.

## 4.5 UI surfaces (ASCII mockups, if UI work)

No UI surface is in scope.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Add a real top-level `table` declaration to [doctrine/grammars/doctrine.lark](doctrine/grammars/doctrine.lark) and route it through the normal declaration path. Its body should be declaration-only table structure: `columns:`, optional `row_schema:`, and optional declaration default `notes:`. Declaration-owned `rows:` stay out of scope in the first cut.
- Extend document-table grammar so `table` keeps one block kind but supports two authored forms:
  - inline form: `table key: "Title" ...` with the current full inline table body
  - named form: `table key: TableRef ...` and `override table key: TableRef ...`, with a use-site body limited to local `rows:` and local `notes:`
- Add a first-class `TableDecl` to [doctrine/_model/readable.py](doctrine/_model/readable.py), export it through [doctrine/_model/declarations.py](doctrine/_model/declarations.py) and [doctrine/model.py](doctrine/model.py), and add a small unresolved named-table-use payload in the readable model so the parser can keep `table` as one document block kind until resolution.
- Add `tables_by_name` and `table declaration` support to [doctrine/_compiler/indexing.py](doctrine/_compiler/indexing.py), [doctrine/_compiler/constants.py](doctrine/_compiler/constants.py), [doctrine/_compiler/validate/__init__.py](doctrine/_compiler/validate/__init__.py), and [doctrine/_compiler/resolve/refs.py](doctrine/_compiler/resolve/refs.py).
- Resolve named table use inside the existing document path so compile, render, and structure-summary code keep consuming the same resolved table block shape they do today.
- Extend addressable-root and child traversal so table declarations become addressable roots while document-local table descendants keep their current path behavior.

## 5.2 Control paths (future)

1. Parse top-level `table ReleaseGates: "Release Gates"` into `TableDecl`.
2. Index and import it exactly like other top-level named declarations.
3. Parse document table authoring in one of two ways:
   - inline title string -> current inline table payload
   - table declaration ref -> named-table-use payload with local `rows:` and local `notes:`
4. Resolve the named table with a new `_resolve_table_ref` that uses the normal declaration-ref path and imported module support.
5. Resolve declaration-owned structure through the existing table resolver path so columns, row schema, notes, interpolation, and current fail-loud table semantics stay compiler-owned in one place.
6. Resolve the use-site local rows and local notes, then merge into one ordinary resolved table block with these rules:
   - title comes from the declaration
   - columns come from the declaration
   - `row_schema:` comes from the declaration
   - rows come from the use site only
   - notes render in declaration-first, use-site-second order
   - requirement and `when` metadata come from the use site
   - an empty named use-site body is legal and renders the current no-row contract table
7. Return one ordinary resolved `DocumentBlock(kind="table", ...)` so document inheritance, structure summaries, output rendering, and Markdown rendering keep using the current table path.
8. Keep `override table` on the same `table` kind so a child document may override a parent table with either the inline form or the named form without introducing a second override system.
9. Expose both addressable roots promised in Section 0:
   - declaration root for declaration-owned descendants such as `columns` and `row_schema`
   - document root for the local table block, including use-site rows

## 5.3 Object model + abstractions (future)

- `TableDecl` is the new first-class named type for reusable table contracts.
- The document use site stays a `table` block, not a new user-facing block kind. That preserves current kind-based inheritance and override rules.
- The unresolved named-table-use payload exists only until document resolution. After that point, the compiler should carry the same resolved table data it carries for inline tables today.
- The renderer-facing truth remains `CompiledTableBlock` only. No second compiled table contract is introduced.

## 5.4 Invariants and boundaries

- The declaration is the single structural owner for title, columns, and optional `row_schema:`.
- The document use site is the single local owner for requirement, guard, rows, local notes, and local key placement.
- Inline tables remain fully valid and unchanged.
- Named-table use must not create a generic `ref:` system, a second renderer path, or a second table override system.
- Imported table refs must work through the same named-ref rules as other top-level declarations.
- Wrong-kind refs, duplicate local keys, and invalid named-use bodies must fail loud.
- Compatibility posture is additive only: preserve current inline authoring and current Markdown output, with no bridge syntax and no shim behavior.

## 5.5 UI surfaces (ASCII mockups, if UI work)

No UI surface is in scope.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar | `doctrine/grammars/doctrine.lark` | top-level `declaration`, `readable_table_block`, `override_readable_table_block` | No top-level `table`; document tables only accept title strings | Add top-level `table` declaration plus named-use and named-override branches while keeping inline branches | Make table a real named type without forking table semantics | `table ReleaseGates: "..."`, `table release_gates: ReleaseGates`, `override table release_gates: ReleaseGates` | new focused table-declaration tests, parse diagnostics, example `116_*` |
| Parser | `doctrine/_parser/readables.py` | table parse helpers | One inline table-body path handles declaration-like and use-site concerns together | Reuse current column/row/cell builders, add declaration-only table-body parsing, add named-use parsing limited to `rows:` and `notes:` | Keep one table mini-language while failing loud on wrong use-site structure | declaration body supports `columns`, `row_schema`, `notes`; named use-site body supports `rows`, `notes` only | parse diagnostics and named-table unit tests |
| AST + exports | `doctrine/_model/readable.py`, `doctrine/_model/declarations.py`, `doctrine/model.py` | no `TableDecl` or named-use payload | Add `TableDecl` plus unresolved named-table-use payload and export both | Make `table` a real declaration and keep the document block kind stable | declaration-root table contract and unresolved named-use payload | compile/render/addressability tests |
| Declaration registries | `doctrine/_compiler/indexing.py`, `doctrine/_compiler/constants.py`, `doctrine/_compiler/validate/__init__.py` | No `tables_by_name`; no `table declaration` validation label | Add `tables_by_name`, duplicate-name validation, readable-declaration label, and addressable-root registry entry | Let tables load, import, validate, and resolve like other named declarations | importable and addressable `table declaration` | import and duplicate-declaration coverage in focused unit tests |
| Ref resolution | `doctrine/_compiler/resolve/refs.py` | no `_resolve_table_ref` | Add `_resolve_table_ref` with normal local/imported name-ref behavior and `table declaration` missing-label text | Make the use site typed and fail loud | `TableRef` resolves like `DocumentRef` or `SkillRef` | missing-ref and wrong-kind tests |
| Document resolution | `doctrine/_compiler/resolve/documents.py`, `doctrine/_compiler/resolve/document_blocks.py` | Only inline document tables resolve | Resolve named use into one ordinary resolved `table` block, preserve existing override-kind rules, and merge declaration notes before local notes | Keep inheritance, structure-summary, and render behavior on the canonical current path | one resolved `DocumentBlock(kind="table")` regardless of inline or named source | render, override, and addressability tests |
| Addressability | `doctrine/_compiler/resolve/addressables.py`, `doctrine/_compiler/validate/addressable_children.py` | Table descendants only exist under document-local block keys | Add table declaration roots and keep document-local descendants unchanged | Support both promised roots without changing local-key behavior | `ReleaseGates:columns.evidence.title` plus current `ReleaseGuide:release_gates...` paths | focused addressability tests and example assertions |
| Compile + render | `doctrine/_compiler/compile/readable_blocks.py`, `doctrine/_compiler/compile/outputs.py`, `doctrine/_renderer/blocks.py`, `doctrine/_renderer/tables.py` | Resolved inline tables already compile summaries and render current Markdown | Keep these paths behaviorally unchanged; only ensure named tables lower into them identically, including structured cell bodies | This is an authoring reuse feature, not a render redesign | emitted Markdown stays identical for equivalent tables | `tests/test_output_rendering.py`, examples `58`, `59`, `65`, `66`, new `116_*` |
| Diagnostics | `tests/test_parse_diagnostics.py`, `docs/COMPILER_ERRORS.md` if wording changes | Existing parse diagnostics cover inline table failures only | Add fail-loud coverage for invalid named-use bodies and any new wrong-kind or missing-label wording that becomes user-visible | Keep the new surface teachable and fail loud | named-use body restrictions and `table declaration` ref errors | parse diagnostics and compiler-errors doc if needed |
| Public docs | `docs/LANGUAGE_REFERENCE.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/AGENT_IO_DESIGN_NOTES.md` | Docs teach `table` only as a document block | Teach top-level named tables, typed document use sites, ownership boundaries, and unchanged render output | Keep public truth aligned with shipped language | documented named-table syntax and ownership model | doc-backed example verification |
| Examples + live instructions | `examples/58_readable_document_blocks/**`, new `examples/116_*`, `examples/README.md`, `AGENTS.md` | Inline-only table teaching today; root instructions say corpus ends at `115_*` | Keep `58` as the inline-table example, add one new named-table example, index it, and update the corpus-range line in `AGENTS.md` when `116_*` lands | Keep the teaching ladder and live repo instructions truthful | shipped corpus through `116_*`; inline and named patterns both taught | targeted manifest verify and full `make verify-examples` |
| Release surfaces | `docs/VERSIONING.md`, `CHANGELOG.md` | No entry for first-class named tables | Record this as an additive public language feature and align the release story with the implementation | New backward-compatible syntax changes the public language surface | language-version minor bump guidance and changelog entry | release-doc alignment checks |
| Focused unit proof | new `tests/test_table_declarations.py` | No dedicated unit surface for named-table declarations, imports, and dual-root addressability | Add one focused unit module for happy path, imported refs, wrong-kind refs, duplicate local keys, and empty named-use rendering | Keep the feature proof small and explicit instead of overloading unrelated modules | named-table unit proof surface | new unit module plus existing render/parse regressions |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - top-level `table` declaration -> typed document `table key: TableRef` -> existing document table resolve -> existing compile/render path
- Deprecated APIs (if any):
  - none in the first cut
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - no code-path delete is required
  - remove stale doc wording that says tables only exist as document blocks
  - update the root [AGENTS.md](../AGENTS.md) corpus-range line once `examples/116_*` lands so repo instructions stay truthful
- Adjacent surfaces tied to the same contract family:
  - language reference and design notes
  - agent I/O design notes because `structure:` summaries must stay truthful
  - example index and live repo instructions
  - current table proof examples `58`, `59`, and `65`
- Compatibility posture / cutover plan:
  - additive only; existing inline tables stay valid, current Markdown output stays unchanged, and no bridge syntax is introduced
- Capability-replacing harnesses to delete or justify:
  - none; this is a direct compiler-path extension
- Live docs/comments/instructions to update or delete:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/LANGUAGE_DESIGN_NOTES.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/VERSIONING.md`
  - `CHANGELOG.md`
  - `examples/README.md`
  - `AGENTS.md`
- Behavior-preservation signals for refactors:
  - `tests/test_output_rendering.py`
  - `tests/test_parse_diagnostics.py`
  - `examples/58_readable_document_blocks/cases.toml`
  - `examples/59_document_inheritance_and_descendants/cases.toml`
  - `examples/65_row_and_item_schemas/cases.toml`
  - `examples/66_late_extension_blocks/cases.toml`
  - new `tests/test_table_declarations.py`
  - new `examples/116_*`
  - `make verify-examples`
  - `make verify-diagnostics` if diagnostics move

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Declaration registries | `doctrine/_compiler/indexing.py`, `doctrine/_compiler/constants.py`, `doctrine/_compiler/validate/__init__.py`, `doctrine/_compiler/resolve/refs.py` | Treat `table` as a real first-class declaration everywhere named declarations already participate | Prevent imports, duplicate-name checks, and wrong-kind errors from drifting from the rest of the language | include |
| Document table overrides | `doctrine/grammars/doctrine.lark`, `doctrine/_parser/readables.py`, `doctrine/_compiler/resolve/documents.py` | Keep named tables on the same `table` block kind and support both inline and named `override table` forms | Prevent a parallel override system or a second block family | include |
| Structure-summary output | `doctrine/_compiler/compile/outputs.py` | Preserve note-first, then column-summary behavior after named-table lowering | Prevent structure attachments from drifting from current inline table output | include |
| Inheritance workaround teaching | `examples/59_document_inheritance_and_descendants`, `docs/LANGUAGE_REFERENCE.md` | Stop treating whole-document inheritance as the primary table-reuse story, while keeping the example as the inheritance example | Prevent docs from teaching the workaround as the main reuse path while preserving inheritance coverage | include for docs, defer for example body |
| Other readable block kinds | `section`, `definitions`, `callout`, `properties`, and other readable roots | Generalize first-class declarations for every readable block kind | That would widen the language beyond the approved feature and add a generic reusable-readable system by stealth | exclude |
| Declaration-owned rows | top-level `table` body | Allow shared `rows:` on table declarations | That complicates ownership, addressability, and merge rules without being required to solve reusable table contracts | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. The authoritative checklist must name the actual chosen work, not unresolved branches or `if needed` placeholders. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 - First-Class Table Declaration Foundation

### Goal

Create the new top-level `table` declaration and the smallest parser/model surface needed to represent named table use inside documents without touching render behavior yet.

### Work

This phase establishes the language surface and the new declaration identity. It should stop at parse, model, and declaration-registry truth so later phases can build on one stable representation.

### Checklist (must all be done)

- Extend [doctrine/grammars/doctrine.lark](doctrine/grammars/doctrine.lark) with a top-level `table` declaration.
- Extend [doctrine/grammars/doctrine.lark](doctrine/grammars/doctrine.lark) so document `table` blocks support both:
  - inline title-string form
  - named declaration-ref form
  - matching `override table` support for both forms
- Keep the named use-site body limited to local `rows:` and local `notes:` and make declaration-owned `rows:` invalid in the first cut.
- Reuse current table-body parse helpers in [doctrine/_parser/readables.py](doctrine/_parser/readables.py) instead of creating a second table mini-language.
- Add `TableDecl` plus the unresolved named-table-use payload in [doctrine/_model/readable.py](doctrine/_model/readable.py).
- Export the new declaration through [doctrine/_model/declarations.py](doctrine/_model/declarations.py) and [doctrine/model.py](doctrine/model.py).
- Add `tables_by_name` and `table declaration` support to [doctrine/_compiler/indexing.py](doctrine/_compiler/indexing.py), [doctrine/_compiler/constants.py](doctrine/_compiler/constants.py), and [doctrine/_compiler/validate/__init__.py](doctrine/_compiler/validate/__init__.py).
- Create [tests/test_table_declarations.py](tests/test_table_declarations.py) with the phase-1 parse and declaration-registry coverage this phase needs.
- Add focused parse coverage for:
  - top-level table declarations
  - document named-table use
  - `override table` named-table use
  - invalid named-use bodies
  - duplicate declaration names involving tables

### Verification (required proof)

- `uv run --locked python -m unittest tests.test_table_declarations tests.test_parse_diagnostics`

### Docs/comments (propagation; only if needed)

- Add short code comments only where the dual inline-or-named parse shape or the unresolved named-use payload would otherwise be hard to follow.

### Exit criteria (all required)

- The parser can represent a top-level `table` declaration and a document named-table use without ambiguity.
- Tables participate in declaration indexing and duplicate-name validation like other top-level declarations.
- Invalid named-use bodies fail loud during parse or early compile, not by falling through as generic record noise.
- [tests/test_table_declarations.py](tests/test_table_declarations.py) exists and already covers the phase-1 declaration surface.
- Existing inline table parsing still works unchanged.

### Rollback

- Revert the new declaration grammar, parser, and registry additions as one unit if the syntax shape proves ambiguous or breaks current inline table parsing.

## Phase 2 - Ref Resolution And Table Lowering

### Goal

Resolve named table refs through the normal declaration path, lower named use back into the ordinary resolved `table` block, and preserve existing document inheritance behavior.

### Work

This phase turns the new syntax into real compiler semantics while keeping one table block kind and one resolved table shape. It should preserve the current override model instead of adding a second one.

### Checklist (must all be done)

- Add `_resolve_table_ref` to [doctrine/_compiler/resolve/refs.py](doctrine/_compiler/resolve/refs.py) with the normal local/imported named-ref behavior and `table declaration` missing-label text.
- Teach [doctrine/_compiler/resolve/documents.py](doctrine/_compiler/resolve/documents.py) and [doctrine/_compiler/resolve/document_blocks.py](doctrine/_compiler/resolve/document_blocks.py) to resolve named-table use into the same ordinary resolved `DocumentBlock(kind="table", ...)` used by inline tables.
- Keep `table` on the existing document block kind so inheritance and override-kind checks continue to work through the current `table` path.
- Enforce the first-cut merge rules during resolution:
  - title from declaration
  - columns from declaration
  - `row_schema:` from declaration
  - rows from use site only
  - notes in declaration-first, use-site-second order
  - requirement and `when` from use site
- Make an empty named-use body legal so the named table still renders the current no-row contract table.
- Fail loud on wrong-kind refs, missing refs, duplicate local block keys, and any named-use body that tries to smuggle declaration-owned structure into the use site.
- Update [docs/COMPILER_ERRORS.md](docs/COMPILER_ERRORS.md) for the named-table parse or ref-resolution diagnostics introduced in this phase.
- Add focused unit coverage for:
  - local table refs
  - imported table refs
  - named `override table`
  - wrong-kind refs
  - missing refs
  - duplicate local keys
  - empty named-use rendering preconditions

### Verification (required proof)

- `uv run --locked python -m unittest tests.test_table_declarations`
- `make verify-diagnostics`

### Docs/comments (propagation; only if needed)

- Add a short code comment near the note-merge or lowering boundary if that behavior would otherwise be easy to break later.

### Exit criteria (all required)

- Named tables resolve through the ordinary declaration-ref path, including imports.
- Named-table use lowers into the same resolved document table block shape as inline tables.
- Document inheritance still uses one `table` kind and one override model.
- Wrong-kind, missing-ref, and invalid named-use failures are explicit and user-facing.
- The compiler error catalog and diagnostics verify step stay aligned with the new named-table errors.

### Rollback

- Revert named-table ref resolution and lowering together if the lowered shape does not preserve current document override semantics.

## Phase 3 - Addressability, Structure Summaries, And Render Compatibility

### Goal

Expose the new declaration root while keeping document-local paths, structure summaries, and rendered Markdown behavior unchanged.

### Work

This phase protects the user-visible output contract. It should prove that named tables are an authoring reuse feature only, not a renderer redesign.

### Checklist (must all be done)

- Extend [doctrine/_compiler/resolve/addressables.py](doctrine/_compiler/resolve/addressables.py) and [doctrine/_compiler/validate/addressable_children.py](doctrine/_compiler/validate/addressable_children.py) so table declarations become addressable roots.
- Keep current document-local table descendants unchanged under the local block key.
- Ensure declaration-root and document-root paths both work for the exact examples promised in Section 0.
- Keep [doctrine/_compiler/compile/outputs.py](doctrine/_compiler/compile/outputs.py) behavior unchanged so structure summaries still prefer notes first and otherwise emit `Use the columns ...`.
- Keep [doctrine/_compiler/compile/readable_blocks.py](doctrine/_compiler/compile/readable_blocks.py), [doctrine/_renderer/blocks.py](doctrine/_renderer/blocks.py), and [doctrine/_renderer/tables.py](doctrine/_renderer/tables.py) behavior unchanged except for consuming named tables after lowering.
- Extend focused unit coverage for:
  - declaration-root addressable paths
  - document-root addressable paths
  - no-row named-table render shape
  - row-backed named-table render shape
  - row-schema descendant paths on named tables
  - structured table-cell bodies on named tables

### Verification (required proof)

- `uv run --locked python -m unittest tests.test_table_declarations tests.test_output_rendering`

### Docs/comments (propagation; only if needed)

- Add code comments only at the canonical addressability boundary if the new declaration-root behavior would otherwise be non-obvious.

### Exit criteria (all required)

- `ReleaseGates:columns.evidence.title` resolves and displays correctly.
- `ReleaseGuide:release_gates.columns.evidence.title` and `ReleaseGuide:release_gates.rows.package_smoke` keep working.
- Named tables render the same Markdown as equivalent inline tables in both the row-backed and no-row cases.
- Structured table-cell bodies still resolve and render through the structured-table path when used in named tables.
- Structure summaries remain note-first and otherwise column-summary based.

### Rollback

- Revert declaration-root addressability and named-table lowering together if either change causes rendered or interpolated path regressions.

## Phase 4 - Focused Proof And Corpus Example

### Goal

Turn the feature into shipped proof with one focused test module and one dedicated manifest-backed example, while keeping older examples on their current teaching jobs.

### Work

This phase adds the feature-specific proof surface and updates the example ladder so named tables become the canonical reuse example and older examples remain clean regressions.

### Checklist (must all be done)

- Extend [tests/test_table_declarations.py](tests/test_table_declarations.py) as the focused unit suite for:
  - parse
  - declaration indexing and imports
  - named use resolution
  - named override behavior
  - declaration-root and document-root addressability
  - wrong-kind and missing-ref failures
  - no-row and row-backed named render behavior
  - structured cell-body behavior on named tables
- Add a new dedicated generic corpus example at `examples/116_first_class_named_tables`.
- Author the new example so it proves:
  - top-level `table ReleaseGates`
  - document use `table release_gates: ReleaseGates`
  - one row-backed named-table output
  - one declaration-root or document-root interpolation proving addressability
  - the exact current table Markdown output shape
- Keep [examples/58_readable_document_blocks](../examples/58_readable_document_blocks) as the inline-table example.
- Keep [examples/59_document_inheritance_and_descendants](../examples/59_document_inheritance_and_descendants) as the inheritance example instead of rewriting it into the new feature.
- Update [examples/README.md](../examples/README.md) so the new example is the canonical proof for named-table declarations.
- Update the root [AGENTS.md](../AGENTS.md) corpus-range line when `examples/116_*` lands so the repo instructions stay truthful.

### Verification (required proof)

- `uv run --locked python -m unittest tests.test_table_declarations tests.test_output_rendering tests.test_parse_diagnostics`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/116_first_class_named_tables/cases.toml`
- `make verify-examples`

### Docs/comments (propagation; only if needed)

- Keep the new example generic and keep the exact motivating `ReleaseGates` syntax from Section 0 as the public teaching shape.

### Exit criteria (all required)

- The focused unit suite exists and covers the feature-specific contract.
- The new example exists, verifies, and shows named-table authoring as one clean idea.
- Existing table examples still verify and still teach their original jobs.
- The root repo instructions no longer claim the corpus ends at `115_*`.

### Rollback

- Revert the new test module, the new example, the example index update, and the `AGENTS.md` corpus-range update together if the implementation contract changes before merge.

## Phase 5 - Public Docs And Release Alignment

### Goal

Align the public docs and release surfaces with the shipped language so users learn named tables as the canonical reuse path and still understand that inline tables remain valid.

### Work

This phase syncs the public truth after code and proof are stable. It should remove any touched wording that still presents tables as document-block-only or whole-document inheritance as the main reuse story.

### Checklist (must all be done)

- Update [docs/LANGUAGE_REFERENCE.md](docs/LANGUAGE_REFERENCE.md) with:
  - the top-level `table` declaration
  - the typed document use-site syntax
  - the ownership split between declaration and use site
  - the unchanged rendered Markdown behavior
- Update [docs/LANGUAGE_DESIGN_NOTES.md](docs/LANGUAGE_DESIGN_NOTES.md) to record why first-class named tables fit Doctrine's current patterns better than a generic ref mechanism.
- Update [docs/AGENT_IO_DESIGN_NOTES.md](docs/AGENT_IO_DESIGN_NOTES.md) so `structure:` attachments remain aligned with the unchanged summary and render behavior.
- Update [docs/VERSIONING.md](docs/VERSIONING.md) and [CHANGELOG.md](../CHANGELOG.md) for the additive public language feature.
- Rewrite or remove any touched live doc sentence that still says tables exist only as document blocks or that teaches whole-document inheritance as the primary table-reuse pattern.

### Verification (required proof)

- `make verify-examples`

### Docs/comments (propagation; only if needed)

- Keep public docs and examples generic. Do not introduce repo-external product names or generic reusable-readable speculation.

### Exit criteria (all required)

- Public docs tell one consistent story: top-level named tables exist, inline tables still work, and named-table use does not change rendered Markdown.
- Release docs tell the same additive-language-feature story as the implementation.
- No touched live doc still teaches the old table-only-inside-document limitation as current truth.

### Rollback

- Revert only the doc and release-note edits if the implementation slips and the public feature does not ship in the current change set.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Focused unit proof

- Use [tests/test_table_declarations.py](tests/test_table_declarations.py) as the focused suite for:
  - top-level table declarations
  - named document use
  - named overrides
  - imports
  - declaration-root and document-root addressability
  - wrong-kind and missing-ref failures
  - no-row, row-backed, and structured-cell named-table behavior
- Keep [tests/test_output_rendering.py](tests/test_output_rendering.py) as the regression suite for structure summaries and rendered Markdown shape.
- Keep [tests/test_parse_diagnostics.py](tests/test_parse_diagnostics.py) as the regression suite for fail-loud table parse behavior.

## 8.2 Corpus proof

- Add one manifest-backed example at `examples/116_first_class_named_tables`.
- Keep [examples/58_readable_document_blocks](../examples/58_readable_document_blocks), [examples/59_document_inheritance_and_descendants](../examples/59_document_inheritance_and_descendants), [examples/65_row_and_item_schemas](../examples/65_row_and_item_schemas), and [examples/66_late_extension_blocks](../examples/66_late_extension_blocks) as regression proof for unchanged inline-table behavior.
- Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/116_first_class_named_tables/cases.toml`.
- Run `make verify-examples`.

## 8.3 Diagnostics and release alignment

- Run `make verify-diagnostics` because the new named-table parse and ref-resolution errors are part of the user-facing compiler surface.
- Verify [docs/VERSIONING.md](docs/VERSIONING.md) and [CHANGELOG.md](../CHANGELOG.md) tell the same additive-language-feature story as the implementation.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Ship this as an additive public language feature with no fallback or bridge syntax.
- Keep inline tables legal and unchanged so there is no authored migration burden.
- Roll out the feature through:
  - the new canonical example
  - updated language and design docs
  - updated release docs
  - the root [AGENTS.md](../AGENTS.md) corpus-range update

## 9.2 Telemetry changes

- No telemetry or runtime rollout switch is expected.

## 9.3 Operational runbook

- This is a source-language feature, not a runtime ops feature.
- The rollout burden is on fail-loud compiler behavior, aligned docs, and aligned proof surfaces.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: explorer 1, explorer 2, self-integrator
- Scope checked:
  - frontmatter and planning state
  - TL;DR and Sections 0 through 10
  - helper-block drift
  - architecture, call-site audit, phase order, verification, rollout, and cleanup alignment
- Findings summary:
  - Phase order was not executable because early phases verified against `tests.test_table_declarations` before the plan created that module.
  - Diagnostics and compiler-error-catalog follow-through were named in the audit but not owned by any phase.
  - Structured table-cell behavior was still in scope from research but was not carried through the later proof plan.
- Integrated repairs:
  - Moved creation of [tests/test_table_declarations.py](tests/test_table_declarations.py) into Phase 1 and changed Phase 4 from add to extend.
  - Added owned diagnostics work and `make verify-diagnostics` to Phase 2 and aligned Section 8 with that requirement.
  - Added explicit structured-cell named-table coverage to Section 6, Section 7, and Section 8.
  - Tightened Section 9 so rollout obligations match the doc, example, release, and repo-instruction updates already required by Section 7.
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

- 2026-04-15: Drafted the North Star around a first-class top-level `table` declaration and a typed document use site `table <local_key>: <TableDecl>`. Rejected the earlier generic document `ref:` direction because it did not create a true named table type and did not match the intended canonical syntax.
- 2026-04-15: Drafted the first cut to keep declaration ownership on title, columns, and optional `row_schema:` while keeping rows local to the document use site. This keeps the feature focused on reusable table contracts and avoids extra syntax in v1.
- 2026-04-15: North Star confirmed. The plan is now active with the approved first-cut syntax, rendered Markdown expectations, addressable-path expectations, and release-surface updates unchanged from the confirmed draft.
- 2026-04-15: Deep-dive resolved the concrete architecture: add a real `TableDecl`, keep the document use site on the existing `table` block kind, add a small unresolved named-table-use payload before resolution, lower named use back into the ordinary resolved table block before compile/render, and keep notes in declaration-first then use-site order. Rejected a second override system and rejected generic reusable-readable expansion beyond `table`.
- 2026-04-15: Phase planning split implementation into five phases: declaration foundation, ref-resolution and lowering, addressability/render compatibility, focused proof plus the new `examples/116_first_class_named_tables` surface, and public-doc plus release alignment. This sequencing replaces the earlier rough 3-phase sketch and makes the repo-instruction update in `AGENTS.md` explicit because the new example extends the shipped corpus range.
- 2026-04-15: Consistency pass repaired three real gaps before implementation: the phase-order bug around `tests/test_table_declarations.py`, the unowned diagnostics and `docs/COMPILER_ERRORS.md` follow-through, and the dropped structured-cell proof obligation. The artifact is now decision-complete and ready for implementation.
