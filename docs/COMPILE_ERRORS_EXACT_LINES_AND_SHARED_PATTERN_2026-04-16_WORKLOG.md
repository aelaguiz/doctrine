# Worklog

Plan doc: docs/COMPILE_ERRORS_EXACT_LINES_AND_SHARED_PATTERN_2026-04-16.md

## Initial entry
- Run started.
- Current phase: Phase 1 - Diagnostic contract, formatter, and compiler helper foundation

## 2026-04-16 - Implement pass 1
- Completed Phase 1.
- Added `DiagnosticRelatedLocation`, formatter support for `Related:`, JSON-safe
  serialization for related sites, and shared compiler helpers in
  `doctrine/_compiler/diagnostics.py`.
- Started Phase 2 by adding `SourceSpan` to authored model values that the
  first compile families read, and taught the parser lowering path to preserve
  those spans on declarations, refs, agent fields, and the first IO and output
  schema surfaces.
- Started Phase 3 by migrating indexing and import-boundary errors onto
  structured compiler diagnostics with exact prompt lines and related sites.
- Landed the first Phase 4 family slice for duplicate role fields, duplicate
  typed fields, missing role, and missing abstract authored slots.
- Added focused proof in `tests/test_compile_diagnostics.py` and updated the
  import and duplicate-declaration assertions that still expected raw legacy
  compile strings.
- Ran:
  - `uv run --locked python -m unittest tests.test_compile_diagnostics tests.test_parse_diagnostics tests.test_import_loading tests.test_table_declarations tests.test_diagnostics_formatting`
  - `make verify-diagnostics`
  - `make verify-examples`
- Current next step: widen `SourceSpan` coverage to the remaining
  compile-relevant authored nodes, then migrate the next high-volume compile
  families that can now use those spans.

## 2026-04-16 - Implement pass 2
- Completed the remaining Phase 2 span-preservation work by adding
  `SourceSpan` to law-owned, workflow-owned, review-owned, route-only,
  grounding, and nested readable authored model values, then teaching the
  parser lowering path to keep those spans on workflow-law, review, and
  readable nested nodes.
- Added focused parser proof in `tests/test_parser_source_spans.py` so the new
  lowering coverage stays locked.
- Advanced Phase 3 by making invalid Doctrine config TOML point at the exact
  `pyproject.toml` line and excerpt in `CompilationSession`.
- Advanced Phase 4 by migrating the next workflow-law diagnostic slice:
  route validation and law-path failures now keep exact authored locations,
  duplicate `route_from` arms show related sites, and the shared
  `ensure_location()` path now adds source excerpts when a migrated family
  knows the real line and column.
- Added focused compile-diagnostic proof for invalid config TOML, duplicate
  `route_from` arms, invalid computed `route_from` selectors, and wrong-kind
  `current artifact` targets in `tests/test_compile_diagnostics.py`.
- Ran:
  - `uv run --locked python -m unittest tests.test_compile_diagnostics tests.test_parser_source_spans`
  - `uv run --locked python -m unittest tests.test_project_config tests.test_import_loading tests.test_diagnostics_formatting tests.test_table_declarations tests.test_parse_diagnostics`
  - `make verify-diagnostics`
  - `make verify-examples`
- Current next step: finish the remaining Phase 3 compile-config semantic
  location policy, then keep widening Phase 4 across output, review, and
  readable compile families that still raise raw string `CompileError` paths.

## 2026-04-16 - Implement pass 3
- Completed Phase 3 by carrying bounded config-site metadata through
  `ProjectConfigError`, so Doctrine-owned compile-config semantic failures now
  point at the real `pyproject.toml` key or array item instead of falling back
  to a bare config path.
- Advanced Phase 4 through the review compile surface by adding one shared
  review diagnostic helper in `doctrine/_compiler/review_diagnostics.py` and
  migrating the main review compile families in
  `doctrine/_compiler/compile/review_contract.py`,
  `doctrine/_compiler/compile/review_cases.py`, and
  `doctrine/_compiler/compile/reviews.py`.
- Landed exact-line review diagnostics for missing review surfaces, missing
  reserved outcome sections, comment-output emission failures, duplicate
  accept gates, overlapping case-selected review families, and non-total
  case-selected families. Conflict cases now emit labeled `Related:` sites.
- Added focused proof in `tests/test_compile_diagnostics.py` for review
  comment-output emission, duplicate `accept` gates, and overlapping
  case-selected review families.
- Updated manifest-backed proof in
  `examples/69_case_selected_review_family/cases.toml` so the shipped corpus
  now matches the new structured review wording for overlapping and non-total
  case-selected review failures.
- Ran:
  - `uv run --locked python -m unittest tests.test_compile_diagnostics tests.test_project_config tests.test_parser_source_spans tests.test_diagnostics_formatting tests.test_parse_diagnostics tests.test_import_loading`
  - `make verify-diagnostics`
  - `make verify-examples`
- Current next step: keep widening Phase 4 across output, review resolution,
  readable, and file-scoped compile families, then finish Phase 5 by upgrading
  the corpus contract and removing the compile regex bridge.

## 2026-04-16 - Implement pass 4
- Advanced Phase 4 through the next review resolver slice in
  `doctrine/_compiler/resolve/reviews.py`.
- Landed exact-line resolver diagnostics for gate-less review contracts,
  wrong-kind review subjects, cyclic review inheritance, missing inherited
  review entries, duplicate review item keys, review overrides without
  inherited parents, and wrong-kind inherited review overrides.
- Preserved `source_span` on resolved review-owned sections, fields, and cases
  so parent-child review conflicts can report labeled related sites instead of
  falling back to owner labels.
- Added focused proof in `tests/test_compile_diagnostics.py` for missing
  inherited review entries, duplicate review item keys, and gate-less review
  contracts.
- Fixed a dirty-worktree compatibility blocker by re-exporting
  `CompiledRouteSelectorSpec` through `doctrine/_compiler/resolved_types.py`,
  which let the compiler import cleanly again for verification.
- Updated manifest-backed proof in
  `examples/57_schema_review_contracts/cases.toml` to match the new structured
  gate-less review-contract wording.
- Ran:
  - `uv run --locked python -m unittest tests.test_output_inheritance tests.test_decision_attachment tests.test_compile_diagnostics`
  - `make verify-diagnostics`
  - `make verify-examples`
- Result:
  - The targeted suites and `make verify-diagnostics` passed.
  - `make verify-examples` is still blocked by an unrelated dirty-worktree
    route-contract artifact drift in
    `examples/93_handoff_routing_route_from_final_output`, where the emitted
    `final_output.contract.json` no longer matches the checked-in ref.
- Current next step: either resolve the unrelated example-93 route-contract
  drift so full corpus proof can run cleanly again, or continue Phase 4 on the
  next compile family with that blocker called out explicitly.

## 2026-04-16 - Implement pass 5
- Advanced Phase 4 through the next output inheritance slice in
  `doctrine/_compiler/resolve/outputs.py` by moving the inherited-output
  conflict family onto shared structured diagnostics.
- Added a shared output diagnostic helper in
  `doctrine/_compiler/output_diagnostics.py`.
- Landed exact-line output diagnostics for missing inherited output entries,
  patch-without-parent failures, duplicate child output keys, and wrong-kind
  output overrides. Conflict cases now emit labeled `Related:` sites that
  point at the inherited parent entry or the first duplicate child entry.
- Preserved `source_span` while rebinding inherited output items and readable
  descendants so imported-parent output conflicts keep truthful related
  locations instead of collapsing to path-only output.
- Added focused proof in `tests/test_compile_diagnostics.py` for missing
  inherited output entries, patch-without-parent failures, duplicate child
  keys, and wrong-kind overrides.
- Updated stale smoke fixtures in
  `doctrine/_diagnostic_smoke/fixtures_final_output.py`,
  `doctrine/_diagnostic_smoke/compile_checks.py`, and
  `doctrine/_diagnostic_smoke/emit_checks.py` so the smoke prompts stop using
  retired output-schema `required`.
- Ran:
  - `python -m py_compile doctrine/_compiler/output_diagnostics.py doctrine/_compiler/resolve/outputs.py tests/test_compile_diagnostics.py`
  - `uv run --locked python -m unittest tests.test_compile_diagnostics tests.test_output_inheritance`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/112_output_inheritance_fail_loud/cases.toml`
  - `uv run --locked python -m unittest tests.test_compile_diagnostics tests.test_output_inheritance tests.test_diagnostics_formatting tests.test_final_output tests.test_output_schema_surface tests.test_output_schema_lowering`
  - `make verify-diagnostics`
- Result:
  - The focused output-inheritance proof passed.
  - Broader repo proof is currently blocked by unrelated output-schema syntax
    drift already present in this dirty worktree. `tests.test_final_output`,
    `tests.test_output_schema_lowering`, `tests.test_output_schema_surface`,
    and `make verify-diagnostics` still hit retired output-schema
    `required` / `optional` authoring outside the output-inheritance slice.
- Current next step: keep Phase 4 moving on the next compile family with
  targeted proof, while calling out the separate output-schema proof drift
  until that front is reconciled.
