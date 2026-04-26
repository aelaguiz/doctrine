---
title: Sub-plan 2 - Stage core and routed receipts
date: 2026-04-26
doc_type: sub-plan
parent_epic: docs/EPIC_DOCTRINE_SKILL_GRAPH_2026-04-26.md
status: shipped
---

# TL;DR

Add typed top-level `stage` declarations, a skeletal top-level
`skill_flow` registry, and receipt route fields that target `stage`,
`flow`, `human`, `external`, or `terminal`. Lower the resolved route
metadata and a conservative receipt `json_schema` into
`SKILL.contract.json` so a harness can route handoffs from the lowered
contract.

A post-ship Codex audit found three blockers in this slice:
`stage applies_to:` doc drift, missing receipt-route `json_schema`
lowering, and a stale shipped-corpus line in `AGENTS.md`. This repair
pass fixes all three. It does not add DAG expansion or `applies_to:`
reachability checks.

# Gate To Next

A top-level receipt can declare `route <key>: "Title"` fields that point
at a top-level `stage`, a top-level `skill_flow`, or one of the closed
sentinels (`human`, `external`, `terminal`), and the receipt-by-ref
`host_contract:` slot lowers the routes into a deterministic
`routes` map plus a conservative `json_schema` block on
`SKILL.contract.json`. Stage declarations validate at compile time as a
flow-wide sweep, so even unreferenced stages fail loud on missing or
wrong-kind body items. `applies_to:` only validates `skill_flow` refs in
this slice.

# What Shipped

## Language

- Top-level `stage Name: "Title"` declarations. Closed body items:
  - `id: "<public_id>"` optional
  - `owner: <SkillRef>` required
  - `lane: <EnumName>.<member>` optional
  - `supports:` optional list of top-level skill refs
  - `applies_to:` optional list of top-level `skill_flow` refs
  - `inputs:` optional map of `<key>: <Ref>` to `receipt`, `document`,
    `schema`, or `table`
  - `emits: <ReceiptRef>` optional
  - `intent: "..."` required
  - `durable_target: "..."` required when `checkpoint: durable`
  - `durable_evidence: "..."` required when `checkpoint: durable`
  - `advance_condition: "..."` required
  - `risk_guarded: "..."` optional
  - `forbidden_outputs:` optional list of strings
  - `checkpoint:` optional, closed value set `durable | review_only | diagnostic | none`
    (default `durable`)
- Skeletal top-level `skill_flow Name: "Title"` declarations register a
  graph flow name so receipt route targets can resolve `flow FlowName`.
  The optional body accepts only `intent: "..."`. DAG edges, branches,
  repeats, route binding, and graph emit are intentionally deferred to
  sub-plan 3.
- Top-level receipts may declare `route <key>: "Title"` fields. Each
  choice has the form `<key>: "<title>" -> <target>`. The closed target
  set is `stage <Name>`, `flow <Name>`, `human`, `external`, and
  `terminal`.

## Compiler

- `doctrine/_model/skill_graph.py` houses `StageDecl`, `StageBodyItem`
  variants, `SkillFlowDecl`, the receipt route target shapes, the raw
  `ReceiptDeclRouteField` items added to receipt bodies, and the lowered
  `ResolvedReceiptRouteField`/`ResolvedReceiptRouteChoice` shapes carried
  on `ResolvedReceipt`.
- `doctrine/_compiler/declaration_kinds.py` registers `stage` and
  `skill_flow` as first-class top-level declarations. `IndexedFlow` and
  `UnitDeclarations` carry `stages_by_name` and `skill_flows_by_name`
  registries.
- `doctrine/_compiler/resolve/stages.py` is the new stage resolver. It
  validates body shape, resolves `owner` and `supports` against
  `skills_by_name`, resolves `applies_to` against `skill_flows_by_name`,
  rejects duplicate resolved `applies_to` flows, resolves `lane` to an
  enum member, resolves `inputs` values to top-level
  `receipt`/`document`/`schema`/`table`, resolves `emits` to a top-level
  `receipt`, enforces required fields, the closed `checkpoint` value
  set, and the durable checkpoint target/evidence rule. It does not do
  flow reachability cross-checks yet.
- A new flow-wide `_validate_all_stages_in_flow` sweep runs from
  `compile_agent_from_unit` and `compile_skill_package`, so every
  visible `stage` resolves once even if no agent or package references
  it directly. This mirrors the existing rule-validation sweep.
- `doctrine/_compiler/resolve/receipts.py` extends the resolved receipt
  with a `routes` tuple. Route fields are lowered after the typed
  field-merge pass. Stage and flow targets resolve through the existing
  `_resolve_decl_ref` helper against `stages_by_name` and
  `skill_flows_by_name`. Sentinels are closed in the parser.

## Diagnostics

- `E546` covers a stage `owner:` ref that does not resolve to a top-level
  `skill`.
- `E547` covers a stage `supports:` entry that does not resolve to a
  top-level `skill`.
- `E548` covers a stage `inputs:` value that is not a top-level
  `receipt`, `document`, `schema`, or `table`.
- `E549` covers a stage `emits:` value that is not a top-level
  `receipt`.
- `E559` covers structural stage errors: missing required fields,
  duplicate scalar/support/input keys, duplicate or unresolved
  `applies_to:` refs, supports repeating owner, bad lane member ref, bad
  checkpoint value, and durable checkpoint missing target/evidence.
- `E560` covers a receipt route target whose `stage <Name>` or
  `flow <Name>` ref does not resolve. Closed sentinels are enforced by
  the parser; only `human`, `external`, and `terminal` are accepted.
- The shipped `E544` family now also fires on duplicate route fields and
  duplicate route choices inside one route field.
- `E545` and the inline `host_contract:` `E535`/`E536`/`E537` codes are
  unchanged.

## Emit

- `SKILL.contract.json` adds a deterministic `routes` block on each
  receipt-by-reference slot whose resolved receipt declares route
  fields. Each entry records the route `title` plus a `choices` map
  keyed by choice name. Each choice records `title`, `target_kind`
  (`stage`, `flow`, or `sentinel`), and `target` (the canonical
  declaration name or the sentinel keyword).
- The same receipt-by-reference slot now adds a conservative
  `json_schema` object. It includes the existing receipt data fields plus
  each route key as a required string enum property over the authored
  choice keys. Rich route labels and targets stay only in the `routes`
  map.
- Inline receipt host slots are unchanged. Sub-plan 2 does not move the
  inline form's `E537` type set.

## Docs

- `docs/LANGUAGE_REFERENCE.md` adds three subsections under skill-package
  authoring: `Top-Level Stage Declarations`, `Skeletal skill_flow
  Registration`, and `Receipt Route Fields`.
- `docs/SKILL_PACKAGE_AUTHORING.md` extends its receipt host slot
  section to describe the `routes` and `json_schema` payload on
  `SKILL.contract.json`.
- `docs/COMPILER_ERRORS.md` adds `E546`-`E549`, `E559`, and `E560`,
  extends the `E544` summary to mention duplicate route fields, and
  preserves shipped `E550` and `E551` meanings.
- `docs/README.md` indexes this sub-plan doc beside the sub-plan 1 doc.
- `examples/README.md` indexes examples `151_stage_basics` and
  `152_receipt_stage_route`.
- `CHANGELOG.md` documents the additions under the next release notes.

## Examples

- `examples/151_stage_basics/` ships one positive `render_contract` case
  for a fully typed stage with owner, lane, supports, `applies_to:`,
  inputs, emits, and forbidden outputs, plus focused negative cases for
  `E546`, `E547`, `E548`, `E549`, and two `E559` shapes.
- `examples/152_receipt_stage_route/` ships one positive
  `build_contract` case proving all five route target forms (stage
  twice, flow, and three sentinels) and locking the emitted
  `SKILL.contract.json` `routes` plus `json_schema` shape, plus one
  focused `E560` negative for a missing stage target.
- `pyproject.toml` adds `example_152_receipt_stage_route` so the build
  proof has a configured emit target.

# Verification

- `uv run --locked python -m doctrine.verify_corpus --manifest examples/151_stage_basics/cases.toml`
  (7/7 pass).
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/152_receipt_stage_route/cases.toml`
  (2/2 pass).
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/150_receipt_top_level_decl/cases.toml`
  (5/5 pass — receipt-by-ref regression intact).
- `make verify-examples` (passes).
- `make verify-diagnostics` (passes).
- `make verify-package` (passes).
- `uv run --locked python -m unittest discover tests` (571/571 pass).

# Out Of Scope

- `skill_flow` DAG edges, branches, repeats, variations, route binding,
  and changed-workflow response shape are deferred to sub-plan 3.
- `skill_graph` declarations, closure expansion, policies, graph emit,
  and `verify_skill_graph` are deferred to sub-plan 4.
- Checked `{{skill:Name}}` prose refs and graph warnings are deferred
  to sub-plan 5.
- `applies_to:` reachability cross-checks on `stage` are deferred until
  `skill_flow` has real flow expansion.
- Receipt-by-ref `json_schema` lowering is deliberately conservative in
  this slice. Builtins keep their JSON type, lists lower to arrays, enums
  lower to strings, and declared `receipt`/`schema`/`table` refs lower to
  objects here while the richer field metadata stays on `fields`.
