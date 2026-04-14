# Worklog

Plan doc: docs/SPLIT_GIGANTIC_FILES_INTO_CLEAN_MODULES_2026-04-13.md

## Initial entry
- Run started.
- Current phase: Phase 1 — Extract explicit compiler contracts and helper owners.

## Phase 1 (Extract explicit compiler contracts and helper owners) Progress Update
- Work completed:
  - Added `doctrine/_compiler/resolved_types.py`, `constants.py`, `naming.py`, and `support_files.py`.
  - Repointed the compiler boundary and the main mixin owners off `_compiler/shared.py`.
  - Deleted `doctrine/_compiler/shared.py` after the last internal import moved.
- Tests run + results:
  - `uv run --locked python -m compileall doctrine/_compiler doctrine/compiler.py` — passed before and after deleting `_compiler/shared.py`.
  - `uv sync` — completed, but the repo still does not declare `pytest`.
  - `uv run --locked python -m unittest tests.test_compiler_boundary tests.test_import_loading` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml` — passed.
- Issues / deviations:
  - The planned `pytest` command could not run because `pytest` is not installed in this repo environment, so the same test files were run with `unittest`.
- Next steps:
  - Continue Phase 2 by moving more parser internals and then splitting the authored model.

## Phase 2 (Split authored model and parser internals behind stable boundaries) Progress Update
- Work completed:
  - Added `doctrine/_parser/__init__.py` and `doctrine/_parser/parts.py`.
  - Moved parser body-part contracts and positioned-part helpers out of `doctrine/parser.py`.
  - Kept the public parse entrypoints stable while rewiring `doctrine/parser.py` to the new internal owner.
  - Ran the full shipped corpus, fixed the surfaced `replace` import regression in `doctrine/_compiler/compile.py`, and got `make verify-examples` green again.
  - Added `doctrine/_model/core.py`, `readable.py`, `workflow.py`, `analysis.py`, `schema.py`, and `review.py`, then turned `doctrine/model.py` into the thin public authored-model boundary.
  - Added `doctrine/_parser/runtime.py` and `doctrine/_parser/transformer.py`.
  - Moved parser runtime plus shared declaration and readable helper mixins behind the new internal parser owners while keeping the public parse functions stable.
  - Added `doctrine/_model/declarations.py`.
  - Repointed `doctrine/_compiler/indexing.py`, `session.py`, `naming.py`, and `types.py` onto narrower `_model` owners.
  - Moved schema and document lowering behind `doctrine/_parser/transformer.py`, then deleted the matching duplicate methods from `doctrine/parser.py`.
  - Added `doctrine/_parser/readables.py`.
  - Moved readable block and readable payload lowering behind the new readable owner, then deleted the matching methods from `doctrine/parser.py`.
  - Shrunk `doctrine/parser.py` again to about 1,915 lines while keeping the public parse entrypoints stable.
  - Added `doctrine/_parser/reviews.py`.
  - Moved review, route-only, and grounding lowering behind the new review owner, then deleted the matching methods from `doctrine/parser.py`.
  - Added `doctrine/_parser/workflows.py`.
  - Moved workflow and workflow-law lowering behind the new workflow owner, then deleted the matching methods from `doctrine/parser.py`.
  - Shrunk `doctrine/parser.py` again to about 1,118 lines while keeping the public parse entrypoints stable.
  - Added `doctrine/_parser/analysis_decisions.py`.
  - Moved analysis and decision lowering behind the new analysis-and-decision owner, then deleted the matching methods from `doctrine/parser.py`.
  - Added `doctrine/_parser/io.py`.
  - Moved inputs, outputs, guarded outputs, trust surface, and shared io-body lowering behind the new io owner, then deleted the matching methods from `doctrine/parser.py`.
  - Shrunk `doctrine/parser.py` again to about 470 lines, which puts the public parser boundary back under the repo file-size rule while keeping the public parse entrypoints stable.
  - Added `doctrine/_model/law.py`, `io.py`, and `agent.py`.
  - Moved the law, IO, agent, skill-package, and enum families out of the mixed `_model/core.py` and `_model/workflow.py` owners while keeping `doctrine/model.py` stable.
  - Repointed `doctrine/_compiler/resolved_types.py` off the root `doctrine.model` boundary and onto the internal `doctrine._model` package.
  - Added `doctrine/_parser/agents.py`, `skills.py`, and `expressions.py`.
  - Moved the remaining agent-field, skills, record, skill-package, enum, expression, and shared syntax lowering behind those new parser owners, then deleted the matching methods from `doctrine/parser.py`.
  - Shrunk `doctrine/parser.py` again to about 126 lines while keeping the public parse entrypoints stable.
- Tests run + results:
  - `uv run --locked python -m compileall doctrine/_parser doctrine/parser.py` — passed.
  - `uv run --locked python -m unittest tests.test_parse_diagnostics` — failed first because underscore-prefixed helpers were not exported from `_parser.parts`, then passed after adding `__all__`.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml` — passed after the parser fix.
  - `make verify-examples` — failed first on later examples with `NameError: name 'replace' is not defined`, then passed after importing `replace` in `doctrine/_compiler/compile.py`.
  - `uv run --locked python -m compileall doctrine/_model doctrine/model.py doctrine/_parser doctrine/parser.py` — passed after the `_model/` split and parser runtime/helper moves.
  - `uv run --locked python -m unittest tests.test_parse_diagnostics` — passed after the `_model/` split, the parser runtime move, and the helper-mixin move.
  - `make verify-examples` — passed after the `_model/` split and again after moving parser runtime and helper mixins behind `_parser/runtime.py` and `_parser/transformer.py`.
  - `uv run --locked python -m compileall doctrine/_model doctrine/model.py doctrine/_parser doctrine/parser.py doctrine/_compiler/indexing.py doctrine/_compiler/session.py doctrine/_compiler/naming.py doctrine/_compiler/types.py` — passed after the `_model/declarations.py` owner cut and the schema/document parser move.
  - `uv run --locked python -m unittest tests.test_compiler_boundary tests.test_import_loading tests.test_parse_diagnostics` — passed after the `_model` import cut and the schema/document parser move.
  - `make verify-examples` — passed after repointing the `_compiler` imports and shrinking `doctrine/parser.py` again.
  - `uv run --locked python -m compileall doctrine/_parser doctrine/parser.py doctrine/_compiler/indexing.py doctrine/_compiler/session.py doctrine/_compiler/naming.py doctrine/_compiler/types.py doctrine/_model doctrine/model.py` — passed after the readable owner cut.
  - `uv run --locked python -m unittest tests.test_compiler_boundary tests.test_import_loading tests.test_parse_diagnostics` — passed after the readable owner cut.
  - `make verify-examples` — passed after moving readable lowering behind `doctrine/_parser/readables.py`.
  - `uv run --locked python -m compileall doctrine/_parser doctrine/parser.py doctrine/_model doctrine/model.py` — passed after the review owner cut and again after the workflow owner cut.
  - `uv run --locked python -m unittest tests.test_compiler_boundary tests.test_import_loading tests.test_parse_diagnostics tests.test_verify_corpus` — passed after the review owner cut and again after the workflow owner cut.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml` — passed after the review owner cut and again after the workflow owner cut.
  - `make verify-examples` — passed after moving review, route-only, and grounding lowering behind `doctrine/_parser/reviews.py`, and passed again after moving workflow and workflow-law lowering behind `doctrine/_parser/workflows.py`.
  - `uv run --locked python -m compileall doctrine/_parser doctrine/parser.py doctrine/_model doctrine/model.py` — passed after the combined analysis/decision and io owner cuts.
  - `uv run --locked python -m unittest tests.test_compiler_boundary tests.test_import_loading tests.test_parse_diagnostics tests.test_verify_corpus` — passed after the combined analysis/decision and io owner cuts.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml` — passed after the combined analysis/decision and io owner cuts.
  - `make verify-examples` — passed after moving analysis and decision lowering behind `doctrine/_parser/analysis_decisions.py` and moving inputs, outputs, and io lowering behind `doctrine/_parser/io.py`.
  - `uv run --locked python -m compileall doctrine/_model doctrine/model.py doctrine/_parser doctrine/parser.py doctrine/_compiler` — passed after the `_model/law.py`, `io.py`, and `agent.py` split, and passed again after adding `_parser/agents.py`, `skills.py`, and `expressions.py`.
  - `uv run --locked python -m unittest tests.test_compiler_boundary tests.test_import_loading tests.test_parse_diagnostics tests.test_verify_corpus` — passed after the `_model` regrouping and passed again after the remaining parser-family cuts.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml` — passed after the `_model` regrouping and passed again after the remaining parser-family cuts.
  - `make verify-examples` — passed after the `_model` regrouping and passed again after the remaining parser-family cuts.
- Issues / deviations:
  - Phase 2 is still in progress until the fresh audit confirms close-out. The main Phase 2 cuts named in the last audit are now landed: `doctrine/parser.py` is down to about 126 lines, `_model/core.py` is about 101 lines, `_model/workflow.py` is about 212 lines, and `doctrine/_compiler/resolved_types.py` now imports `doctrine._model` instead of the root public model boundary.
- Next steps:
  - Await the fresh audit pass.
  - If the audit still finds a real Phase 2 gap, continue from that remaining boundary cleanup.
  - If the audit closes Phase 2, advance to Phase 3.

## Phase 3 (Split diagnostics and rendering internals behind stable boundaries) Progress Update
- Work completed:
  - Added `doctrine/_diagnostics/__init__.py`, `contracts.py`, and `formatting.py`.
  - Moved the shared diagnostics data contracts plus the JSON, location, block, and excerpt formatting helpers behind the new diagnostics package while keeping `doctrine/diagnostics.py` as the public error boundary.
  - Added `doctrine/_diagnostics/parse_errors.py` and `doctrine/_diagnostics/message_builders.py`.
  - Moved the parse classifiers plus the compile and emit message builders behind the approved diagnostics owner names while keeping `doctrine/diagnostics.py` as the public error boundary.
  - Split the old compile-message catch-all into smaller private builder groups: `_message_builders_agents.py`, `_message_builders_authored.py`, `_message_builders_refs.py`, `_message_builders_readables.py`, `_message_builders_workflow_law.py`, `_message_builders_reviews.py`, and `_message_builders_emit.py`.
  - Deleted the old `parse.py`, `compile_messages.py`, and `emit_messages.py` files after callers moved.
  - Added `doctrine/_renderer/__init__.py`, `semantic.py`, and `tables.py`.
  - Moved render-profile mode resolution, semantic-section helpers, key humanizing, and table helpers behind the new renderer package while keeping `doctrine/renderer.py` as the public markdown render boundary.
  - Added `doctrine/_renderer/blocks.py`.
  - Moved the markdown block dispatcher and block render helpers behind the new renderer package while keeping `doctrine/renderer.py` as the thin public markdown boundary.
  - Added `doctrine/_flow_render/__init__.py`, `layout.py`, `d2.py`, and `svg.py`.
  - Moved lane planning, graph layout, D2 text emission, and SVG execution helpers behind the new flow-render package while keeping `doctrine/flow_renderer.py` as the public boundary.
  - Shrunk `doctrine/diagnostics.py` to about 326 lines, `doctrine/_diagnostics/message_builders.py` to about 97 internal-owner lines, `doctrine/renderer.py` to about 25 lines, and kept `doctrine/flow_renderer.py` at about 48 lines while keeping the public helper names, D2 constants, and flow-render exception types stable for callers and tests.
- Tests run + results:
  - `python -m py_compile doctrine/diagnostics.py doctrine/_diagnostics/*.py` — passed.
  - `uv run --locked python -m unittest tests.test_parse_diagnostics tests.test_emit_docs tests.test_emit_flow` — passed.
  - `make verify-diagnostics` — passed.
  - `make verify-examples` — passed after the approved diagnostics owner rename and split.
- Issues / deviations:
  - Phase 3 still needs a fresh audit pass before it can be marked complete by the loop. The reopened diagnostics owner gap appears addressed in code, but the audit block remains authoritative until the child audit reruns.
- Next steps:
  - Await the fresh audit pass.
  - Advance to Phase 4 if the fresh audit agrees the diagnostics and render boundary split is now complete.

## Phase 4 (Split compile, resolve, and validate behind CompilationContext) Progress Update
- Work completed:
  - Turned `doctrine/_compiler/compile.py` into the package `doctrine/_compiler/compile/`.
  - Added `doctrine/_compiler/compile/agent.py`, `readables.py`, `final_output.py`, and `skill_package.py`.
  - Moved the matching compile method families behind those approved owner modules while keeping `doctrine/_compiler/context.py` and `doctrine/compiler.py` stable.
  - Added smaller private compile owners: `outputs.py`, `records.py`, `readable_blocks.py`, `reviews.py`, `review_cases.py`, and `workflows.py`.
  - Moved the remaining live compile families out of `doctrine/_compiler/compile/__init__.py` and behind those purpose-built modules.
  - Shrunk `doctrine/_compiler/compile/__init__.py` to a 27-line boundary, with the new private compile owners at about 308, 260, 439, 275, 306, and 318 lines.
  - Turned `doctrine/_compiler/resolve.py` into the package `doctrine/_compiler/resolve/`.
  - Added `doctrine/_compiler/resolve/refs.py`, `outputs.py`, `workflows.py`, `schemas.py`, and `reviews.py`.
  - Moved the ref lookup, output and IO-body resolution, workflow and law resolution, schema resolution, and review resolution families behind those approved resolve owners while keeping the current internal call sites stable.
  - Fixed one real regression from the first `outputs.py` cut by restoring the original inherited-outputs behavior for patched outputs blocks.
  - Shrunk the resolve family facade to `doctrine/_compiler/resolve/__init__.py` at about 2,944 lines, down from the old 6,052-line single file.
  - Turned `doctrine/_compiler/validate.py` into the package `doctrine/_compiler/validate/`.
  - Added `doctrine/_compiler/validate/outputs.py`, `readables.py`, `routes.py`, and `agents.py`.
  - Moved the output guard and interpolation helpers, readable guard helpers, workflow-law and route validation helpers, and agent-side route and review context helpers behind those approved validate owners while keeping `CompilationContext` stable.
  - Added the approved `doctrine/_compiler/validate/reviews.py` owner and moved the shared review-semantic and review helper families behind it.
  - Split the new review owner into smaller private modules: `review_semantics.py`, `review_preflight.py`, `review_gate_observation.py`, `review_agreement.py`, and `review_branches.py`.
  - Shrunk `doctrine/_compiler/validate/reviews.py` to a 19-line boundary, with the new private review owners at about 483, 410, 438, 402, and 449 lines.
  - Deleted the duplicate live review method family from `doctrine/_compiler/validate/__init__.py`, so the review boundary now owns the behavior instead of shadowing another in-class copy.
  - Added `doctrine/_compiler/validate/route_semantics.py`, `route_semantics_context.py`, `route_semantics_reads.py`, `contracts.py`, `display.py`, `schema_helpers.py`, `addressable_children.py`, `addressable_display.py`, and `law_paths.py`.
  - Moved the remaining route-semantic, contract-summary, display, schema, addressable, and law-path helper families out of `doctrine/_compiler/validate/__init__.py` and behind those purpose-built owners.
  - Shrunk `doctrine/_compiler/validate/__init__.py` to a 320-line boundary, with the new private validate owners at about 418, 100, 474, 281, 140, 493, 378, and 417 lines.
- Tests run + results:
  - `python -m py_compile doctrine/_compiler/compile/__init__.py doctrine/_compiler/compile/agent.py doctrine/_compiler/compile/final_output.py doctrine/_compiler/compile/readables.py doctrine/_compiler/compile/skill_package.py doctrine/_compiler/context.py doctrine/compiler.py` — passed.
  - `uv run --locked python -m unittest tests.test_final_output tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_decision_attachment` — failed first because `final_output.py` imported `_dotted_decl_name` from the wrong module, then passed after fixing the import.
  - `make verify-examples` — failed first from that same bad import, then passed after the fix.
  - `python -m py_compile doctrine/_compiler/compile/__init__.py doctrine/_compiler/compile/agent.py doctrine/_compiler/compile/final_output.py doctrine/_compiler/compile/outputs.py doctrine/_compiler/compile/records.py doctrine/_compiler/compile/readable_blocks.py doctrine/_compiler/compile/readables.py doctrine/_compiler/compile/review_cases.py doctrine/_compiler/compile/reviews.py doctrine/_compiler/compile/skill_package.py doctrine/_compiler/compile/workflows.py doctrine/_compiler/context.py` — passed after the compile boundary rewrite.
  - `uv run --locked python -m unittest tests.test_final_output tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_decision_attachment` — passed after the compile boundary rewrite.
  - `make verify-examples` — passed after the compile boundary rewrite.
  - `python -m py_compile doctrine/_compiler/resolve/__init__.py doctrine/_compiler/resolve/refs.py doctrine/_compiler/context.py` — passed.
  - `uv run --locked python -m unittest tests.test_final_output tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_decision_attachment` — passed after the resolve refs cut.
  - `make verify-examples` — passed after the resolve refs cut.
  - `python -m py_compile doctrine/_compiler/resolve/outputs.py doctrine/_compiler/resolve/__init__.py` — passed.
  - `uv run --locked python -m unittest tests.test_final_output tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_decision_attachment` — failed first because the first `outputs.py` cut changed inherited outputs behavior, then passed after restoring the original `_resolve_io_body` logic.
  - `make verify-examples` — passed after the `outputs.py` cut and regression fix.
  - `python -m py_compile doctrine/_compiler/resolve/__init__.py doctrine/_compiler/resolve/reviews.py doctrine/_compiler/resolve/workflows.py doctrine/_compiler/resolve/schemas.py doctrine/_compiler/resolve/outputs.py doctrine/_compiler/resolve/refs.py` — passed after the remaining resolve owner cuts.
  - `uv run --locked python -m unittest tests.test_final_output tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_decision_attachment` — passed after the remaining resolve owner cuts.
  - `make verify-examples` — passed after the remaining resolve owner cuts.
  - `python -m py_compile doctrine/_compiler/validate/__init__.py doctrine/_compiler/validate/agents.py doctrine/_compiler/validate/outputs.py doctrine/_compiler/validate/readables.py doctrine/_compiler/validate/routes.py doctrine/_compiler/context.py` — passed after the validate package cut and again after the `agents.py` owner cut.
  - `uv run --locked python -m unittest tests.test_final_output tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_decision_attachment` — passed after the validate package cut and again after the `agents.py` owner cut.
  - `make verify-examples` — passed after the validate package cut and again after the `agents.py` owner cut.
  - `python -m py_compile doctrine/_compiler/validate/reviews.py doctrine/_compiler/validate/review_semantics.py doctrine/_compiler/validate/review_preflight.py doctrine/_compiler/validate/review_gate_observation.py doctrine/_compiler/validate/review_agreement.py doctrine/_compiler/validate/review_branches.py doctrine/_compiler/validate/__init__.py doctrine/_compiler/context.py` — passed after the first `reviews.py` owner cut.
  - `uv run --locked python -m unittest tests.test_final_output tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_decision_attachment` — passed after the first `reviews.py` owner cut and again after the follow-up import cleanup in `review_preflight.py`.
  - `make verify-examples` — passed after the review owner cut and private review module split.
  - `python -m py_compile doctrine/_compiler/validate/__init__.py doctrine/_compiler/validate/reviews.py doctrine/_compiler/validate/review_semantics.py doctrine/_compiler/validate/review_preflight.py doctrine/_compiler/validate/review_gate_observation.py doctrine/_compiler/validate/review_agreement.py doctrine/_compiler/validate/review_branches.py doctrine/_compiler/context.py` — passed after deleting the duplicate review block from `ValidateMixin`.
  - `uv run --locked python -m unittest tests.test_final_output tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_decision_attachment` — passed after deleting the duplicate review block from `ValidateMixin`.
  - `make verify-examples` — passed after deleting the duplicate review block from `ValidateMixin`.
  - `python -m py_compile doctrine/_compiler/validate/__init__.py doctrine/_compiler/validate/route_semantics_context.py doctrine/_compiler/validate/route_semantics_reads.py doctrine/_compiler/validate/route_semantics.py doctrine/_compiler/validate/contracts.py doctrine/_compiler/validate/display.py doctrine/_compiler/validate/schema_helpers.py doctrine/_compiler/validate/addressable_children.py doctrine/_compiler/validate/addressable_display.py doctrine/_compiler/validate/law_paths.py doctrine/_compiler/context.py` — passed after the remaining validate helper split.
  - `uv run --locked python -m unittest tests.test_final_output tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_decision_attachment` — passed after the remaining validate helper split.
  - `make verify-examples` — passed after the remaining validate helper split.
- Issues / deviations:
  - Phase 4 is still in progress. `doctrine/_compiler/compile/__init__.py` and `doctrine/_compiler/validate/__init__.py` are now real boundaries, but `doctrine/_compiler/resolve/__init__.py` is still about 2,944 lines.
- Next steps:
  - Continue Phase 4 with the remaining resolve family shrink work.
  - Keep rerunning the Phase 4 proof set after each landed slice.

## Phase 4 (Split compile, resolve, and validate behind CompilationContext) Progress Update
- Work completed:
  - Added the remaining resolve-family owners:
    `route_semantics.py`, `io_contracts.py`, `agent_slots.py`, `skills.py`,
    `addressable_skills.py`, `analysis.py`, `documents.py`,
    `document_blocks.py`, `section_bodies.py`, `addressables.py`, and
    `law_paths.py`.
  - Moved the remaining resolve behavior out of
    `doctrine/_compiler/resolve/__init__.py` and behind those purpose-built
    owners while keeping `CompilationContext` and the public compiler boundary
    stable.
  - Fixed one real regression from the first `law_paths.py` cut by restoring
    the `_dotted_decl_name` import from `doctrine._compiler.support_files`.
  - Shrunk `doctrine/_compiler/resolve/__init__.py` to a 39-line boundary.
- Tests run + results:
  - `python -m py_compile doctrine/_compiler/resolve/__init__.py doctrine/_compiler/resolve/route_semantics.py doctrine/_compiler/resolve/io_contracts.py doctrine/_compiler/resolve/agent_slots.py doctrine/_compiler/resolve/skills.py doctrine/_compiler/resolve/addressable_skills.py doctrine/_compiler/resolve/analysis.py doctrine/_compiler/resolve/documents.py doctrine/_compiler/resolve/document_blocks.py doctrine/_compiler/resolve/section_bodies.py doctrine/_compiler/resolve/addressables.py doctrine/_compiler/resolve/law_paths.py doctrine/_compiler/context.py` — passed.
  - `uv run --locked python -m unittest tests.test_final_output tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_decision_attachment` — failed first because `law_paths.py` imported `_dotted_decl_name` from the wrong module, then passed after fixing the import.
  - `make verify-examples` — failed first from that same bad import, then passed after the fix.
- Issues / deviations:
  - None in code after the import fix. The remaining Phase 4 blocker in the
    last audit is now landed and needs the fresh audit pass to close it.
- Next steps:
  - Await the fresh audit pass.
  - If the audit closes Phase 4, advance to Phase 5.

## Phase 5 (Split proof owners while keeping trusted commands stable) Progress Update
- Work completed:
  - Added `doctrine/_verify_corpus/__init__.py`, `manifest.py`, `report.py`,
    `diff.py`, and `runners.py`.
  - Moved manifest parsing, verifier dataclasses, report formatting, diff
    building, and case runners behind that new internal proof package while
    keeping `doctrine/verify_corpus.py` as the stable CLI and public test
    import boundary.
  - Kept the root `_run_build_contract` wrapper wired to the root
    `load_emit_targets` import so `tests/test_verify_corpus.py` can still
    patch the same public hook surface.
  - Added `doctrine/_diagnostic_smoke/__init__.py`, `fixtures.py`,
    `parse_checks.py`, `compile_checks.py`, `review_checks.py`,
    `emit_checks.py`, and `flow_checks.py`.
  - Moved the smoke runner checks behind those themed proof owners while
    keeping `doctrine/diagnostic_smoke.py` as the stable runner path.
  - Fixed two real regressions from the smoke split:
    `_review_exact_gate_stress_source()` needed the new package-relative
    example path, and the moved flow graph assertion needed the original
    `"Carries current for Durable Artifact"` note text.
  - Shrunk `doctrine/verify_corpus.py` to about 47 lines and
    `doctrine/diagnostic_smoke.py` to about 22 lines.
- Tests run + results:
  - `python -m py_compile doctrine/verify_corpus.py doctrine/_verify_corpus/__init__.py doctrine/_verify_corpus/manifest.py doctrine/_verify_corpus/report.py doctrine/_verify_corpus/diff.py doctrine/_verify_corpus/runners.py doctrine/diagnostic_smoke.py doctrine/_diagnostic_smoke/__init__.py doctrine/_diagnostic_smoke/fixtures.py doctrine/_diagnostic_smoke/parse_checks.py doctrine/_diagnostic_smoke/compile_checks.py doctrine/_diagnostic_smoke/review_checks.py doctrine/_diagnostic_smoke/emit_checks.py doctrine/_diagnostic_smoke/flow_checks.py` — passed.
  - `uv run --locked python -m unittest tests.test_verify_corpus` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml` — passed.
  - `make verify-diagnostics` — failed first because the moved review stress
    fixture still used the old source path, then failed again because the moved
    flow graph assertion had the wrong carrier-note text, then passed after
    both fixes.
- Issues / deviations:
  - `doctrine/_diagnostic_smoke/fixtures.py` and
    `doctrine/_diagnostic_smoke/flow_checks.py` are still large owner files
    even though they now each do one clear proof job. The fresh audit should
    decide whether that is acceptable for Phase 5 or whether one more internal
    split is still needed before Phase 6.
- Next steps:
  - Await the fresh audit pass.
  - If the audit closes Phase 5, advance to Phase 6 cleanup and full proof.

## Phase 6 (Delete dead paths, sync touched truth surfaces, and run full proof) Progress Update
- Work completed:
  - Replaced the root parser wildcard import with the one explicit
    `_name_ref_from_dotted_name` import that the public parser boundary still
    needs.
  - Replaced the root model wildcard facade with explicit re-exports from the
    `_model` owner modules.
  - Replaced the root compiler `globals().update(...)` export rebuild with
    explicit imports from `doctrine._compiler.resolved_types`.
  - Replaced the remaining wildcard `resolved_types` imports in the main
    compiler boundaries `doctrine/_compiler/context.py`,
    `doctrine/_compiler/flow.py`, `doctrine/_compiler/display.py`, and
    `doctrine/_compiler/validate/__init__.py`.
  - Restored the explicit `model` imports those compiler boundaries still
    needed after the wildcard cleanup.
  - Kept the public boundaries thin while preserving the same public import
    paths and passing proof.
- Tests run + results:
  - `uv sync` — passed.
  - `npm ci` — passed.
  - `python -m py_compile doctrine/parser.py doctrine/model.py doctrine/compiler.py doctrine/verify_corpus.py doctrine/diagnostic_smoke.py` — passed before the Phase 6 compiler-boundary slice.
  - `uv run --locked python -m unittest tests.test_compiler_boundary tests.test_parse_diagnostics tests.test_verify_corpus` — passed before the Phase 6 compiler-boundary slice.
  - `make verify-diagnostics` — passed before the Phase 6 compiler-boundary slice.
  - `make verify-examples` — passed before the Phase 6 compiler-boundary slice.
  - `python -m py_compile doctrine/_compiler/context.py doctrine/_compiler/flow.py doctrine/_compiler/display.py doctrine/_compiler/validate/__init__.py doctrine/parser.py doctrine/model.py doctrine/compiler.py` — passed after the compiler-boundary cleanup.
  - `uv run --locked python -m unittest tests.test_compiler_boundary tests.test_parse_diagnostics tests.test_verify_corpus` — failed first because `CompilationContext` still expected a runtime `CompilationSession` name from the old wildcard import, then failed again because `ValidateMixin` still expected `model` from the old wildcard import, then passed after both explicit imports were fixed.
  - `make verify-diagnostics` — passed after the compiler-boundary cleanup.
  - `make verify-examples` — passed after the compiler-boundary cleanup.
- Issues / deviations:
  - The broad wildcard cleanup is not fully exhausted yet. Many internal
    compiler helper modules still import `doctrine._compiler.resolved_types`
    with `*`, and `doctrine/_diagnostic_smoke/fixtures.py` plus
    `doctrine/_diagnostic_smoke/flow_checks.py` are still large owner files.
    The fresh audit should decide whether those remaining internals block
    Phase 6 close-out or whether the approved cleanup bar is now satisfied at
    the main public and boundary surfaces.
- Next steps:
  - Await the fresh audit pass.
  - If the audit still finds real remaining cleanup, continue Phase 6 from the
    next highest-value wildcard or oversized owner.

## Phase 5 (Split proof owners while keeping trusted commands stable) Progress Update
- Work completed:
  - Split the remaining `_diagnostic_smoke` monoliths into smaller themed
    owners: `fixtures_common.py`, `fixtures_reviews.py`,
    `fixtures_authored.py`, `fixtures_flow.py`,
    `fixtures_final_output.py`, `flow_route_checks.py`,
    `flow_graph_checks.py`, and `flow_emit_checks.py`.
  - Rewrote `doctrine/_diagnostic_smoke/fixtures.py` into a thin boundary
    over those new fixture modules.
  - Rewrote `doctrine/_diagnostic_smoke/flow_checks.py` into a thin runner
    boundary that delegates to the new route, graph, and emit flow checks.
  - Kept the stable runner paths unchanged:
    `doctrine/verify_corpus.py` and `doctrine/diagnostic_smoke.py`.
- Tests run + results:
  - `python -m py_compile doctrine/_diagnostic_smoke/*.py doctrine/diagnostic_smoke.py doctrine/verify_corpus.py` — passed.
  - `uv run --locked python -m unittest tests.test_verify_corpus` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml` — passed.
  - `make verify-diagnostics` — passed after the `_diagnostic_smoke` owner split.
  - `make verify-examples` — passed after the `_diagnostic_smoke` owner split.
- Issues / deviations:
  - None in code on this worktree. The remaining Phase 5 question is only the
    fresh audit pass that will judge the landed tree.
- Next steps:
  - Await the fresh audit pass.
  - If the audit closes Phase 5, keep the plan moving through Phase 6.

## Phase 6 (Delete dead paths, sync touched truth surfaces, and run full proof) Progress Update
- Work completed:
  - Removed the remaining internal
    `from doctrine._compiler.resolved_types import *` imports across the
    compile, resolve, and validate owner modules.
  - Added the explicit imports those modules still needed after the wildcard
    cleanup, including explicit `model` imports where the old broad import had
    hidden that dependency.
  - Confirmed the cleanup with `rg -n "from doctrine\\._compiler\\.resolved_types import \\*" doctrine/_compiler`,
    which returned no matches.
  - Refreshed local dependencies with `uv sync` and `npm ci` on the current
    worktree before the final full proof.
- Tests run + results:
  - `python -m py_compile doctrine/_compiler/compile/*.py doctrine/_compiler/resolve/*.py doctrine/_compiler/validate/*.py doctrine/_compiler/context.py doctrine/_compiler/flow.py doctrine/_compiler/display.py doctrine/parser.py doctrine/model.py doctrine/compiler.py doctrine/verify_corpus.py doctrine/diagnostic_smoke.py` — passed.
  - `uv run --locked python -m unittest tests.test_compiler_boundary tests.test_parse_diagnostics tests.test_verify_corpus tests.test_final_output tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_decision_attachment` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml` — passed.
  - `make verify-diagnostics` — passed.
  - `make verify-examples` — passed.
- Issues / deviations:
  - None in code on this worktree. The remaining decision is the fresh audit
    pass that will confirm whether the full approved implementation frontier
    is now closed.
- Next steps:
  - Await the fresh audit pass.
  - If the audit agrees the approved code frontier is landed, the loop can
    stop cleanly.
