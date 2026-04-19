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
