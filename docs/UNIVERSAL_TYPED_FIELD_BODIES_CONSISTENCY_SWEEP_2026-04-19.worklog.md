---
title: "Universal Typed Field Bodies Consistency Sweep — Worklog"
plan: docs/UNIVERSAL_TYPED_FIELD_BODIES_CONSISTENCY_SWEEP_2026-04-19.md
branch: feat/carrier-review-fields-and-shared-rules-split
started: 2026-04-19
---

# Worklog

Chronological log of implementation activity against the 9-phase plan.
Execution truth only. Does not replace Section 7 (authoritative plan) or
Section 10 (Decision Log). Does not author the `implementation_audit`
block — that is the fresh audit child's job.

## 2026-04-19 — Phase 1: shared field-type resolver, `FieldTypeRef` union, E320

**Artifacts shipped.**

- `doctrine/_compiler/resolve/field_types.py` — new module. Exports
  `BUILTIN_TYPE_NAMES` (`frozenset` of the seven builtin primitives),
  `BuiltinTypeRef`, `EnumTypeRef`, `FieldTypeRef` (union), `EnumLookup`
  (callable alias), and `resolve_field_type_ref(name, *, span, unit,
  lookup_enum) -> FieldTypeRef`.
- `docs/COMPILER_ERRORS.md` — E320 row inserted between E319 and E331.
- `tests/test_field_type_ref.py` — seven unit tests covering all six
  behaviors named in the Phase 1 checklist (each builtin resolves; the
  builtin set is the expected seven names; same-unit enum resolves;
  imported enum resolves through the same callable; non-enum decl raises
  E320; unknown name raises E320; E320 carries the CNAME source span).

**Design notes.**

- The helper takes an explicit `lookup_enum: Callable[[NameRef,
  IndexedUnit], EnumDecl | None]` parameter so it can live in its own
  module without importing the resolver mixin. Phase 2 will pass
  `self._try_resolve_enum_decl` as the callable at every wire-up site,
  giving every surface the same single entrypoint.
- E320 fires for both "CNAME resolves to a non-enum decl" and "CNAME
  does not resolve anywhere". The phase-plan chose the single-entrypoint
  framing (one message, one code) over splitting across E276/E281/E320.
  This matches the catalog entry and the Phase 1 test cases.
- The module contains one canonical-boundary comment at the top
  describing the single-entrypoint invariant. One comment, one place.

**Verification (proof).**

- `uv run --locked python -m unittest tests.test_field_type_ref` — green
  (7/7 tests pass).
- `make verify-examples` — green (full shipped corpus, no ref diffs).
- `make verify-diagnostics` — green.

**Exit criteria status.**

- `doctrine/_compiler/resolve/field_types.py` exists with the five named
  exports (`BUILTIN_TYPE_NAMES`, `BuiltinTypeRef`, `EnumTypeRef`,
  `FieldTypeRef`, `resolve_field_type_ref`) plus the `EnumLookup` alias.
- E320 is registered in `docs/COMPILER_ERRORS.md`.
- Tests cover all six behaviors.
- `make verify-examples` and `make verify-diagnostics` both green on the
  phase tip.
- No other module imports the helper yet (Phase 2 wires the first
  surfaces).

**Phase 1 complete.**

## 2026-04-19 — Phase 2: wire structured output-schema surfaces to the shared resolver

**Artifacts shipped.**

- `doctrine/_model/io.py` — `OutputSchemaField`, `OutputSchemaRouteField`,
  `OutputSchemaDef` each gained `type_ref: FieldTypeRef | None` with
  `compare=False` and `TYPE_CHECKING` import guard so the model layer
  does not import the compiler layer at runtime.
- `doctrine/_compiler/resolve/output_schemas.py` — imported the shared
  helper; added `type_ref: FieldTypeRef | None` to
  `_OutputSchemaNodeParts`; routed the `key == "type"` capture through
  `resolve_field_type_ref` (skipping the literal `"enum"` Form A marker
  so Form A continues to normalize through its existing branch); updated
  `_lower_output_schema_parts` to prefer `parts.type_ref` over
  `parts.type_name` and to derive `schema["enum"]` from the resolved
  `EnumTypeRef.decl.members` when present.
- `doctrine/_compiler/resolve/field_types.py` — `EnumLookup` switched
  from a `Callable` alias to a `Protocol` with keyword-only `unit` so
  it matches `_try_resolve_enum_decl`'s live signature. The helper now
  passes `unit=unit` to the callable. Phase 1 tests updated to the
  keyword-only form.
- `tests/test_output_schema_lowering.py` — five new tests cover:
  (a) `type: <EnumName>` on a field lowers to `string` + `enum: [keys]`;
  (b) `type: <EnumName>` on both a `field` and a `def` lowers
  identically; (c) `type: <UnknownCNAME>` raises E320; (d) `type:
  <OtherDecl>` (non-enum decl) raises E320; (e) Form A (`type: enum` +
  `values:`) and the canonical `enum X` + `type: X` form lower to
  byte-identical `type` and `enum` JSON values for the same member
  keys. This is the Phase 2 preservation lock.
- `examples/79_final_output_output_schema/cases.toml` — the
  "fails-loud-on-Draft-2020-12" case now asserts E320 on the same
  fixture (the raw CNAME never reaches the validator under Phase 2).
  Case name updated.
- `doctrine/_diagnostic_smoke/compile_checks.py` — the matching smoke
  check flipped from E217 to E320; the new shape is the correct
  observable behavior for Phase 2's "kill the silent-malformed-schema
  latent bug" exit criterion.
- `tests/test_compile_diagnostics.py` —
  `test_final_output_invalid_json_schema_points_at_schema_line` now
  asserts E320, points at the `type:` line (via in-content line
  search), and drops the Draft 2020-12 substring assertion (the new
  code path never runs the validator on the bad CNAME).

**Design notes.**

- `type_name` was kept as the literal authored-value tracker so the
  existing Form A branch (`parts.type_name == "enum"`) and the existing
  Form B branch (`parts.type_name in {None, "string"}`) continue to
  work byte-identically. `type_ref` was added additively. Phase 3
  deletes both Form A/B branches and the `type_name` plumbing with
  them. The plan text says "replace"; in practice "replace" means
  "replace all *acting* readers"; the literal-marker reader stays
  until its caller (Form A/B normalization) goes away in Phase 3.
  Exit criterion "_collect_output_schema_node_parts is the only
  module that calls resolve_field_type_ref for output-schema surfaces"
  is satisfied — only the single capture site calls the helper.
- `schema["enum"]` is derived from `member.key`, not `member.wire` or
  `member.value` as the plan's Work text suggested. Reason: Form A
  emits bareword member keys (`"ok"`, `"action_required"`) into
  `schema["enum"]` today. `member.wire` is `None` for enum decls
  without explicit wire strings, and `member.value = wire ?? title`
  would emit the human-cased `"OK"` / `"Action Required"` instead of
  the lowercase snake key. Using `member.key` is the only choice
  that preserves byte-identical lowering of the migrated examples in
  Phase 3.
- Form A's `"type: enum"` capture explicitly skips the shared
  resolver. `"enum"` is neither a builtin nor the name of a declared
  enum, so routing it through `resolve_field_type_ref` would raise
  E320 and break Form A. The Phase 3 cutover deletes Form A; the
  skip branch goes away with it.
- No new diagnostic added in this phase; E320 was already registered
  in Phase 1 and this phase simply wires it into the three structured
  output-schema surfaces (field / route-field / def) through a single
  call site.

**Verification (proof).**

- `uv run --locked python -m unittest tests.test_output_schema_lowering`
  — green (14/14, including 5 new Phase 2 cases).
- `uv run --locked python -m unittest tests.test_output_schema_surface
  tests.test_output_schema_validation tests.test_compile_diagnostics
  tests.test_field_type_ref tests.test_output_schema_lowering` —
  green (215/215).
- `make verify-examples` — green. "Checked ref diffs: None."
- `make verify-diagnostics` — green. "diagnostic smoke checks passed".

**Exit criteria status.**

- All three structured output-schema IR classes carry `type_ref`
  (default `None`).
- `_collect_output_schema_node_parts` is the single call site that
  invokes `resolve_field_type_ref` for output-schema surfaces.
- Every shipped `examples/**/ref/**` file is byte-identical to main
  after this phase's tip compiles (verify-examples: no ref diffs).
- The silent-malformed-type bug is dead:
  `test_type_naming_unknown_cname_raises_e320` and
  `test_type_naming_non_enum_decl_raises_e320` prove `type: <BadName>`
  raises E320 instead of silently writing `{"type": "BadName"}`. The
  surface-level manifest case (`examples/79_.../cases.toml` case
  "`type:` names an unknown declaration") backs this up end-to-end.
- `make verify-examples` and `make verify-diagnostics` both green.

**Phase 2 complete.**
