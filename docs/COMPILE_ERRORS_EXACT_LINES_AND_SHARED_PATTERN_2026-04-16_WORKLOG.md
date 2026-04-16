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

## 2026-04-16 - Implement pass 6
- Advanced Phase 4 through the next workflow slice in
  `doctrine/_compiler/resolve/workflows.py`.
- Added a shared workflow diagnostic helper in
  `doctrine/_compiler/workflow_diagnostics.py`.
- Landed exact-line workflow diagnostics for cyclic workflow inheritance,
  duplicate workflow item keys, patch-without-parent workflow items, missing
  inherited workflow entries, and wrong-kind workflow overrides.
- Landed exact-line inherited-law diagnostics for missing inherited law
  subsections, duplicate subsection accounting, overriding unknown law
  subsections, and inherited law blocks that mix named patch entries with bare
  law statements.
- Added focused proof in `tests/test_compile_diagnostics.py` for workflow
  duplicate keys, workflow patch-without-parent failures, missing inherited
  workflow entries, workflow override kind mismatches, duplicate inherited law
  subsections, and missing inherited law subsections.
- Kept agent-slot workflow-body resolution aligned with the new resolver
  signature in `doctrine/_compiler/resolve/agent_slots.py`.
- No manifest edits were needed in this pass because the existing
  `message_contains` assertions for the shipped workflow and law examples
  already covered the migrated wording.
- Ran:
  - `python -m py_compile doctrine/_compiler/workflow_diagnostics.py doctrine/_compiler/resolve/workflows.py doctrine/_compiler/resolve/agent_slots.py tests/test_compile_diagnostics.py`
  - `uv run --locked python -m unittest tests.test_compile_diagnostics`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/02_sections/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/37_law_reuse_and_patching/cases.toml`
  - `make verify-diagnostics`
  - `make verify-examples`
- Result:
  - The focused workflow proof passed.
  - The shipped workflow and inherited-law examples passed.
  - `make verify-diagnostics` passed.
  - `make verify-examples` passed.
- Current next step: continue Phase 4 on the next unresolved resolver,
  compiler, or validator family now that branch-wide proof is clean again.

## 2026-04-16 - Implement pass 7
- Advanced Phase 4 through the next readable and document slice in
  `doctrine/_compiler/compile/readable_blocks.py`,
  `doctrine/_compiler/resolve/document_blocks.py`, and
  `doctrine/_compiler/resolve/documents.py`.
- Added a shared readable diagnostic helper in
  `doctrine/_compiler/readable_diagnostics.py`.
- Landed exact-line readable diagnostics for duplicate readable keys across
  list items, properties, inline schemas, footnotes, and table children, plus
  invalid readable block structure on unknown callout kinds, single-line raw
  or code blocks, empty tables, unknown table columns, and multiline inline
  table cells.
- Landed exact-line document diagnostics for duplicate document block keys,
  document patch-without-parent failures, wrong-kind document overrides, and
  missing inherited document entries. Duplicate and parent-child conflicts now
  emit labeled `Related:` sites.
- Preserved authored `source_span` while rebuilding resolved readable payloads
  so the migrated readable and document conflicts can keep truthful prompt
  lines through resolution.
- Added focused proof in `tests/test_compile_diagnostics.py` for duplicate
  properties entries, unknown callout kinds, empty document tables, duplicate
  document block keys, document patch-without-parent failures, wrong-kind
  document overrides, and missing inherited document entries.
- Updated proof surfaces that still expected legacy raw readable/document
  strings in `tests/test_output_rendering.py`,
  `doctrine/_diagnostic_smoke/compile_checks.py`, and the shipped example
  manifests under `examples/59_*`, `examples/61_*`, `examples/64_*`,
  `examples/65_*`, and `examples/66_*`.
- Ran:
  - `python -m py_compile doctrine/_compiler/readable_diagnostics.py doctrine/_compiler/resolve/document_blocks.py doctrine/_compiler/resolve/documents.py doctrine/_compiler/compile/readable_blocks.py tests/test_compile_diagnostics.py`
  - `uv run --locked python -m unittest tests.test_compile_diagnostics`
  - `uv run --locked python -m unittest tests.test_output_rendering tests.test_table_declarations`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/59_document_inheritance_and_descendants/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/61_multiline_code_and_readable_failures/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/64_render_profiles_and_properties/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/65_row_and_item_schemas/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/66_late_extension_blocks/cases.toml`
  - `make verify-diagnostics`
  - `make verify-examples`
- Result:
  - The focused readable/document tests passed.
  - The shipped readable and document example manifests passed after aligning
    legacy message expectations to the new structured wording.
  - `make verify-diagnostics` passed after updating one stale smoke assertion
    that still expected the old readable-table text.
  - `make verify-examples` passed.
- Current next step: continue Phase 4 on the remaining unresolved compiler,
  resolver, and validator families, especially the broader output, readable,
  and file-scoped surfaces that still raise raw string compile failures.

## 2026-04-16 - Implement pass 8
- Advanced Phase 4 through the next readable guard slice in
  `doctrine/_compiler/validate/readables.py`,
  `doctrine/_compiler/compile/readable_blocks.py`, and
  `doctrine/_compiler/compile/readables.py`.
- Landed exact-line structured diagnostics for readable guards that read
  disallowed sources, so readable `when` failures now point at the authored
  guard expression line instead of relying on owner-label-only text.
- Aligned the remaining guard-shell compile fallbacks in the readable compile
  paths with the same readable-block diagnostic contract. The shipped grammar
  already rejects guard blocks without `when`, so the new regression proof for
  those branches uses parsed prompts with the guard expression removed at the
  model layer before compile.
- Added focused proof in `tests/test_compile_diagnostics.py` for exact-line
  readable guard failures and the guard-shell fallback paths.
- No manifest edits were needed in this pass because the shipped readable
  guard examples already asserted stable code and wording.
- Ran:
  - `python -m py_compile doctrine/_compiler/validate/readables.py doctrine/_compiler/compile/readable_blocks.py doctrine/_compiler/compile/readables.py tests/test_compile_diagnostics.py`
  - `uv run --locked python -m unittest tests.test_compile_diagnostics`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/61_multiline_code_and_readable_failures/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/64_render_profiles_and_properties/cases.toml`
  - `make verify-diagnostics`
  - `make verify-examples`
- Result:
  - The focused readable guard tests passed.
  - The shipped readable guard example manifests passed without corpus edits.
  - `make verify-diagnostics` passed.
  - `make verify-examples` passed.
- Current next step: continue Phase 4 on the remaining unresolved compile,
  resolve, and validate families outside the readable guard path, especially
  the broader output, schema, IO, agent-slot, and file-scoped surfaces that
  still raise raw string compile failures.

## 2026-04-16 - Implement pass 9
- Advanced Phase 4 through the next mapped output compile slice in
  `doctrine/_compiler/compile/outputs.py`.
- Replaced raw-string compile failures with structured, exact-line diagnostics
  for input typed-field completeness, mixed `files` versus `target` / `shape`
  output declarations, incomplete single-artifact outputs, typed-target
  validation, output-target config key failures, and the shipped output
  `schema:` / `structure:` attachment failures.
- Added labeled `Related:` sites for the real conflict pairs in this slice:
  mixed `files` versus `target` / `shape`, duplicate output target config
  keys, and empty attached schemas that point back to the attached schema
  declaration.
- Added focused proof in `tests/test_compile_diagnostics.py` for missing input
  source, mixed output contract declarations, incomplete outputs, duplicate or
  unknown or missing output-target config keys, non-markdown output
  structures, and attached schemas with no sections.
- No manifest edits were needed in this pass because the shipped output
  examples already asserted stable codes or message fragments that still match
  the migrated wording.
- Ran:
  - `python -m py_compile doctrine/_compiler/compile/outputs.py tests/test_compile_diagnostics.py`
  - `uv run --locked python -m unittest tests.test_compile_diagnostics`
  - `uv run --locked python -m unittest tests.test_output_rendering`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/56_document_structure_attachments/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/63_schema_artifacts_and_groups/cases.toml`
  - `make verify-diagnostics`
  - `make verify-examples`
- Result:
  - The focused output diagnostic tests passed.
  - The output rendering suite passed.
  - The shipped output attachment example manifests passed without corpus
    edits.
  - `make verify-diagnostics` passed.
  - `make verify-examples` passed.
- Current next step: continue Phase 4 on the remaining unresolved compile,
  resolve, and validate families, especially the raw-string output file-entry,
  output-schema, addressable, agent, flow, and file-scoped package surfaces
  that still sit outside the shared structured helper path.

## 2026-04-16 - Implement pass 10
- Advanced Phase 4 through the remaining authored output-file helper slice in
  `doctrine/_compiler/compile/outputs.py`.
- Replaced the last raw-string authored failures in that file with
  structured, exact-line diagnostics for invalid `files:` entry shape, output
  file entries that are missing `path` or `shape`, non-record
  `must_include` / `current_truth` rows, and invalid `support_files:` entry
  shape or path.
- Added focused proof in `tests/test_compile_diagnostics.py` for bad `files:`
  entry shape, missing output-file `shape`, non-record `must_include` blocks,
  bad `support_files:` entry shape, and non-string `support_files` paths.
- No manifest edits were needed in this pass because the shipped output proof
  still matched the migrated wording and the new branches were covered with
  focused unit tests plus the normal output rendering and corpus surfaces.
- Ran:
  - `python -m py_compile doctrine/_compiler/compile/outputs.py tests/test_compile_diagnostics.py`
  - `uv run --locked python -m unittest tests.test_compile_diagnostics`
  - `uv run --locked python -m unittest tests.test_output_rendering`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/09_outputs/cases.toml`
  - `make verify-diagnostics`
  - `make verify-examples`
- Result:
  - The focused output diagnostic tests passed.
  - The output rendering suite passed.
  - The shipped `09_outputs` manifest passed without corpus edits.
  - `make verify-diagnostics` passed.
  - `make verify-examples` passed.
- Current next step: continue Phase 4 on the remaining unresolved families
  outside `compile/outputs.py`, especially output-schema, addressable, final
  output, agent, flow, and file-scoped package or skill-package surfaces that
  still rely on raw compile strings or file-only fallback paths.

## 2026-04-16 - Implement pass 11
- Advanced Phase 4 through the stable-code `final_output` slice in
  `doctrine/_compiler/resolve/outputs.py`,
  `doctrine/_compiler/compile/final_output.py`,
  `doctrine/_compiler/compile/review_contract.py`,
  `doctrine/_compiler/validate/__init__.py`, and
  `doctrine/_compiler/output_schema_validation.py`.
- Added `doctrine/_compiler/final_output_diagnostics.py` so the authored
  `final_output:` surface can use the same shared compile helper path as the
  other migrated families.
- Landed exact-line structured diagnostics for `E211`, `E212`, `E213`,
  `E215`, `E216`, `E217`, and `E218`. Those now point at the authored
  `final_output:` field, the offending output `target:` or `files:` line, the
  retired `example_file` line, the schema `example:` line, or the output
  schema declaration line as the truthful best-known site.
- Threaded authored `FinalOutputField.source_span` through
  `_resolve_final_output_decl()` so `final_output` reference failures stay
  exact-line in compile, review-contract, and flow paths.
- Stopped routing output-schema validation failures back through raw compile
  strings by enriching `OutputSchemaValidationError` with structured summary,
  detail, and hint fields, then converting those to structured `CompileError`
  instances in the final-output validator boundary.
- Added focused proof in `tests/test_compile_diagnostics.py` for exact-line
  `E211` through `E218` behavior, and aligned two older wording expectations
  in `tests/test_final_output.py` plus one stale smoke assertion in
  `doctrine/_diagnostic_smoke/compile_checks.py`.
- No manifest edits were needed in this pass because the shipped final-output
  corpus already keyed on stable codes and surviving message fragments.
- Ran:
  - `python -m py_compile doctrine/_compiler/final_output_diagnostics.py doctrine/_compiler/compile/final_output.py doctrine/_compiler/compile/review_contract.py doctrine/_compiler/resolve/outputs.py doctrine/_compiler/resolve/output_schemas.py doctrine/_compiler/output_schema_validation.py doctrine/_compiler/validate/__init__.py doctrine/_compiler/flow.py tests/test_compile_diagnostics.py`
  - `uv run --locked python -m unittest tests.test_compile_diagnostics tests.test_final_output tests.test_output_schema_validation tests.test_validate_output_schema`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/79_final_output_output_schema/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/80_final_output_rejects_file_targets/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/81_final_output_rejects_non_output_refs/cases.toml`
  - `make verify-diagnostics`
  - `make verify-examples`
- Result:
  - The focused final-output and schema-validation tests passed.
  - The shipped final-output manifests for examples `79`, `80`, and `81`
    passed without corpus edits.
  - `make verify-diagnostics` passed after aligning one stale smoke assertion
    to the new structured `E216` wording.
  - `make verify-examples` passed.
- Current next step: continue Phase 4 on the remaining unresolved compile,
  resolve, and validate families outside the final-output slice, especially
  output-schema inheritance or lowering, addressable resolution, agent or flow
  compile fronts, and the explicit file-scoped package or skill-package
  surfaces.

## 2026-04-16 - Implement pass 12
- Advanced Phase 4 through the stable-code output-schema lowering slice in
  `doctrine/_compiler/resolve/output_schemas.py`.
- Added `doctrine/_compiler/output_schema_diagnostics.py` so output-schema
  lowering can use the same shared compile helper pattern as the other
  migrated families.
- Landed exact-line structured diagnostics for `E227`, `E228`, `E229`,
  `E236`, and `E237`. Those now point at the authored `type:`, `values:`,
  `enum:`, `required`, or `optional` line instead of falling back to
  location-less message-only failures, and the conflicting `type:` line now
  shows up as a labeled `Related:` site where the failure depends on it.
- Fixed the route-final-output integration path in
  `doctrine/_compiler/resolve/outputs.py` so the shared
  `_collect_output_schema_node_parts(...)` helper keeps working for route
  field final-output binding after the new `unit=` requirement.
- Added focused proof in `tests/test_compile_diagnostics.py` for exact-line
  `E227`, `E228`, `E229`, `E236`, and `E237` behavior, including the related
  `type:` site on the enum-form conflict cases.
- No manifest edits were needed in this pass because the shipped output-schema
  and final-output corpus already keyed on stable codes or message fragments
  that still match the migrated wording.
- Ran:
  - `python -m py_compile doctrine/_compiler/output_schema_diagnostics.py doctrine/_compiler/resolve/output_schemas.py tests/test_compile_diagnostics.py`
  - `uv run --locked python -m unittest tests.test_compile_diagnostics tests.test_output_schema_lowering tests.test_output_schema_surface`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/79_final_output_output_schema/cases.toml`
  - `make verify-diagnostics`
  - `make verify-examples`
- Result:
  - The focused compile-diagnostic and output-schema suites passed.
  - The shipped `79_final_output_output_schema` manifest passed without corpus
    edits.
  - `make verify-diagnostics` first exposed one missed call site in
    `resolve/outputs.py`; after aligning that helper call, diagnostics smoke
    passed.
  - `make verify-examples` passed after the same integration fix.
- Current next step: continue Phase 4 on the remaining unresolved compile,
  resolve, validate, and file-scoped package families, especially the raw
  branches in `compile/agent.py`, `compile/records.py`,
  `resolve/addressables.py`, `flow.py`, `validate/display.py`,
  `validate/review_agreement.py`, `package_layout.py`, and
  `compile/skill_package.py`.

## 2026-04-16 - Implement pass 13
- Advanced Phase 4 through the typed-declaration and config-helper slice in
  `doctrine/_compiler/compile/records.py` and
  `doctrine/_compiler/validate/display.py`.
- Added `doctrine/_compiler/authored_diagnostics.py` so these generic
  prompt-authored helpers can use the shared structured compile-error path
  without borrowing an output-specific helper name.
- Landed exact-line structured diagnostics for `E230`, `E231`, `E233`,
  `E234`, `E235`, and `E276` on compile-agent paths. Input config rows now
  point at the real bad config line for non-scalar rows, duplicate keys, and
  unknown keys, missing input config keys now point at the owning `source:`
  line, config-key declaration failures in input sources or output targets now
  point at the bad declaration line with `Related:` first-declaration sites,
  and missing local output-shape refs now point at the authored `shape:` line.
- Restored missing nested record spans in `doctrine/_parser/skills.py` so
  generic record-based declarations such as input sources and output targets
  keep `source_span` on nested scalars, sections, and refs instead of falling
  back to only the declaration line.
- Fixed `DoctrineError.ensure_location()` in `doctrine/diagnostics.py` so a
  later wrapper can fill a missing path, line, or excerpt without overwriting
  an already-known imported module path with the root prompt path. That keeps
  imported compile errors truthful once a child diagnostic already has the
  real file.
- Added focused exact-line proof in `tests/test_compile_diagnostics.py` for
  local and imported config-row failures, config-key declaration failures, and
  missing local output-shape refs, then widened parser proof with
  `tests.test_parser_source_spans`.
- No manifest edits were needed in this pass because the shipped input and
  output-target corpus already keyed on surviving render contracts or stable
  compile fragments.
- Ran:
  - `python -m py_compile doctrine/_compiler/authored_diagnostics.py doctrine/_compiler/compile/records.py doctrine/_compiler/compile/outputs.py doctrine/_compiler/validate/display.py doctrine/_compiler/resolve/outputs.py doctrine/_parser/skills.py doctrine/diagnostics.py tests/test_compile_diagnostics.py`
  - `uv run --locked python -m unittest tests.test_compile_diagnostics tests.test_output_target_delivery_skill tests.test_parser_source_spans`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/08_inputs/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/118_output_target_delivery_skill_binding/cases.toml`
  - `make verify-diagnostics`
  - `make verify-examples`
- Result:
  - The focused compile-diagnostic, parser-span, and output-target delivery
    tests passed.
  - The shipped `08_inputs` and `118_output_target_delivery_skill_binding`
    manifests passed without corpus edits.
  - `make verify-diagnostics` passed.
  - `make verify-examples` passed.
- Current next step: continue Phase 4 on the remaining unresolved compile,
  resolve, validate, and file-scoped package families, especially the raw
  branches in `compile/agent.py`, `resolve/addressables.py`, `flow.py`,
  `validate/addressable_display.py`, `validate/review_agreement.py`,
  `package_layout.py`, and `compile/skill_package.py`.
