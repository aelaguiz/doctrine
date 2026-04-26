---
title: Sub-plan 1 - Receipt core and package bridge
date: 2026-04-26
doc_type: sub-plan
parent_epic: docs/EPIC_DOCTRINE_SKILL_GRAPH_2026-04-26.md
status: shipped
---

# TL;DR

Add top-level reusable `receipt` declarations, receipt inheritance, and a
new `host_contract: receipt key: ReceiptRef` form so a skill package can
point at a shared typed receipt type. Lower the resolved receipt into
`SKILL.contract.json` so consumers do not have to re-resolve the source
declaration.

# Gate To Next

A package compiles when one top-level `receipt` is declared, inherited,
and pointed at by name from `host_contract:`. The emitted contract
records the slot key, the receipt name, and the lowered field map with
each field's resolved kind.

# What Shipped

## Language

- Top-level `receipt Name[Parent]?: "Title"` declarations.
- Receipt fields are required and typed. Allowed types are builtin
  scalars (`string`, `integer`, `number`, `boolean`), declared `enum`,
  `table`, `schema`, or another declared `receipt`. `list[Type]` marks a
  repeating field.
- Explicit `[Parent]` inheritance with the same `inherit` and `override`
  patching model used by `output`, `workflow`, and `document`. Grouped
  inherit (`inherit {a, b}`) is supported.
- `host_contract: receipt key: ReceiptRef` form sits alongside the
  existing inline form.

## Compiler

- New `ResolveReceiptsMixin` resolves receipt parents, applies inherit
  and override, validates field types, and detects receipt inheritance
  and receipt-of-receipt cycles. The resolver returns a deterministic
  `ResolvedReceipt` with a closed `kind` per field.
- `_validate_receipt_host_slots` in the skill-package compile now also
  resolves by-reference slots and replaces them with a
  `ResolvedReceiptHostSlotRef` carrying the lowered receipt.
- Skill-entry bind validation now treats `ReceiptHostSlotRef` and
  `ResolvedReceiptHostSlotRef` like the existing `ReceiptHostSlot`:
  receipt slots are not bound at the consuming agent.
- Duplicate `host_contract:` slot keys now fail with `E535`. The parser
  passes duplicate slot items through unchanged so the compiler can raise
  the canonical diagnostic instead of an upstream parse error.

## Diagnostics

- `E544` covers every internal receipt issue: empty body, duplicate
  field, unaccounted inherit/override, missing inherited field, override
  on undefined, unknown field type, and inheritance or
  receipt-of-receipt cycle.
- `E545` covers a `host_contract:` receipt-by-reference slot whose ref
  does not resolve to a top-level `receipt`.

## Emit

- `SKILL.contract.json` host slot records for by-reference slots add a
  `receipt` key with the canonical receipt name and a `fields` map keyed
  by field name. Each field carries `type` and `kind`.
- The canonical receipt name is the resolved declaration name, taken from
  an explicit `canonical_name` field on `ResolvedReceipt` and mirrored on
  `ResolvedReceiptHostSlotRef`. Aliased imports (`from shared_receipts
  import SharedHandoffReceipt as AliasedHandoffReceipt`) emit
  `"receipt": "SharedHandoffReceipt"`, not the alias.

## Docs

- `docs/LANGUAGE_REFERENCE.md` adds a "Top-Level Receipt Declarations"
  section under skill-package authoring.
- `docs/SKILL_PACKAGE_AUTHORING.md` adds a "Receipt host slots"
  subsection that explains both shapes.
- `docs/COMPILER_ERRORS.md` adds `E544` and `E545`, and extends the
  existing `E535` summary to include duplicate slot keys.
- `examples/README.md` indexes example `150_receipt_top_level_decl`.
- `CHANGELOG.md` documents the additions under the next release notes.

## Example

- `examples/150_receipt_top_level_decl/` ships a top-level `StageReceipt`
  with an inheriting `LessonPlanReceipt`, an exported
  `SharedHandoffReceipt` in `prompts/shared_receipts/`, a controller
  package that points three host_contract receipt slots at top-level
  receipts (one local, one inherited, and one imported under the alias
  `AliasedHandoffReceipt`), and three negative cases (`E545` for unknown
  ref, `E544` for receipt inheritance cycle, `E535` for duplicate
  `host_contract:` slot keys). The build target name is
  `example_150_receipt_top_level_decl`. The aliased third slot is the
  regression that locks the canonical-name lowering.

# Verification

- `uv run --locked python -m doctrine.verify_corpus --manifest examples/150_receipt_top_level_decl/cases.toml` (5/5 pass, including the duplicate slot key `E535` regression).
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/142_skill_host_receipt_envelope/cases.toml` (4/4 pass — no regression in the inline receipt form).
- `make verify-examples` (445/445 pass).
- `make verify-diagnostics` (passes).
- `make verify-package` (passes).
- `uv run --locked python -m unittest tests.test_release_flow` (passes).

# Out Of Scope

- `stage`, `skill_flow`, `skill_graph`, graph warnings, diagrams, and
  checked `{{skill:Name}}` prose refs are deferred to later sub-plans
  per the parent epic.
- The inline receipt host slot form's E537 type set is unchanged: it
  still allows `enum`, `table`, `schema`, and `document`, and does not
  yet accept builtin scalars or top-level receipt refs. Widening that
  set was intentionally left out to avoid a backwards-incompatible move
  in this slice.
