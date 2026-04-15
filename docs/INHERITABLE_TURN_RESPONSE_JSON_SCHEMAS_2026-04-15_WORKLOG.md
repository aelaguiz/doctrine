# Worklog

Plan doc: docs/INHERITABLE_TURN_RESPONSE_JSON_SCHEMAS_2026-04-15.md

## Initial entry
- Run started.
- Current phase: Phase 1 — Add the new language surface and declaration plumbing

## 2026-04-15 - Phase 1 complete
- Added top-level `output schema` parsing and typed model nodes for:
  - `OutputSchemaDecl`
  - `field`
  - `def`
  - keyed `inherit`
  - keyed `override field`
  - keyed `override def`
- Extended `output shape` to support inheritance and keyed overrides.
- Added compiler indexing for `output schema` declarations.
- Resolved inherited `output shape` declarations before display and addressable traversal.
- Updated readable and addressable declaration lookup so `output shape.schema` now resolves against `output schema` declarations for `JsonObject` shapes.
- Added focused proof in `tests/test_output_schema_surface.py`.

Checks run:
- `uv run --locked python -m unittest tests.test_output_schema_surface`
- `uv run --locked python -m unittest tests.test_output_inheritance tests.test_output_rendering tests.test_final_output`
- `uv run --locked python -m unittest tests.test_emit_docs tests.test_review_imported_outputs tests.test_route_output_semantics`

Result:
- All focused Phase 1 checks passed.

Next frontier:
- Phase 2 — Implement output-schema inheritance and lowering.

## 2026-04-15 - Phase 2 complete
- Added inherited `output schema` resolution with keyed `inherit` and keyed `override` handling.
- Rebound imported parent schema refs so inherited local `def` references stay local while top-level parent declaration refs still point at the parent module.
- Added compiler-owned lowering from typed `output schema` declarations into JSON Schema for:
  - primitives
  - objects
  - arrays and `items`
  - `enum` and `const`
  - authored `optional` lowered to required nullable wire fields
  - nested `any_of`
  - local `def` / `ref`
  - recursive refs
  - supported string, number, and array constraints
- Extended the parser so the plan's authored schema surface now supports:
  - bare identifier enum and const values
  - boolean and null literals
  - floating-point numeric constraints
- Added focused proof in `tests/test_output_schema_lowering.py`.

Checks run:
- `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_parse_diagnostics`
- `uv run --locked python -m unittest tests.test_output_inheritance tests.test_output_rendering tests.test_final_output tests.test_emit_docs tests.test_review_imported_outputs tests.test_route_output_semantics`

Result:
- All focused Phase 2 checks passed.

Next frontier:
- Phase 3 — Add the validator stack and replace the raw summary path.

## 2026-04-15 - Phase 3 complete
- Replaced raw final-output schema-file parsing with compiler-owned lowered schema summaries from `output schema`.
- Added Draft 2020-12 validation and OpenAI structured-output subset validation for lowered final-output schemas.
- Added new structured-output diagnostics:
  - `E217` for invalid lowered Draft 2020-12 schemas
  - `E218` for lowered schemas outside the supported OpenAI subset
- Switched final-output example validation to the new example-file-only path and narrowed `E216` to invalid example JSON objects.
- Added focused proof in `tests/test_output_schema_validation.py`.

Checks run:
- `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation`
- `uv run --locked python -m unittest tests.test_final_output tests.test_emit_docs tests.test_review_imported_outputs tests.test_route_output_semantics`

Result:
- All focused Phase 3 checks passed.

Next frontier:
- Phase 4 — Switch final-output render, emitted contract truth, and diagnostics.

## 2026-04-15 - Phase 4 complete
- Switched final-output render and emitted contract truth to the lowered `output schema` path.
- Removed rendered `Schema file` metadata for migrated structured final outputs.
- Expanded payload preview rows to show:
  - field type
  - required-on-wire status
  - null-allowed status
  - field meaning
- Kept the emitted contract shape stable while making `schema_file` resolve to `null` on the new compiler-owned path.
- Updated compiler-owned render refs and example 79 build-contract proof to match the new contract surface.

Checks run:
- `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation`
- `uv run --locked python -m unittest tests.test_final_output tests.test_emit_docs tests.test_review_imported_outputs tests.test_route_output_semantics`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/79_final_output_json_object/cases.toml --manifest examples/83_review_final_output_json_object/cases.toml --manifest examples/85_review_split_final_output_json_object/cases.toml --manifest examples/90_split_handoff_and_final_output_shared_route_semantics/cases.toml --manifest examples/91_handoff_routing_route_output_binding/cases.toml --manifest examples/104_review_final_output_json_object_blocked_control_ready/cases.toml --manifest examples/105_review_split_final_output_json_object_control_ready/cases.toml --manifest examples/106_review_split_final_output_json_object_partial/cases.toml --manifest examples/55_owner_aware_schema_attachments/cases.toml --manifest examples/09_outputs/cases.toml`

Result:
- All focused Phase 4 checks passed.

Next frontier:
- Phase 5 — Hard-cut shipped examples, docs, diagnostics, and release guidance.

## 2026-04-15 - Phase 5 complete
- Hard-cut the remaining shipped `JsonObject` examples from raw `json schema` authoring to `output schema`.
- Replaced example 79's old raw-schema negative cases with the new real failure surfaces:
  - invalid lowered Draft 2020-12 schema
  - excessive OpenAI nesting
  - invalid example JSON object
  - missing example file
- Regenerated checked-in render refs and example 79 build-contract proof.
- Moved diagnostic smoke fixtures and checks onto the structured-schema path.
- Updated public docs and error docs so they now teach:
  - `output shape.schema` points at `output schema` for `JsonObject`
  - `output.schema` still points at Doctrine `schema`
  - `schema_file` stays in the machine contract only for compatibility

Checks run:
- `make verify-diagnostics`
- `make verify-examples`
- `make verify-package`

Result:
- Phase 5 proof passed, including diagnostics, the full shipped corpus, and package smoke.

Next frontier:
- Fresh implementation audit against the plan doc.

## 2026-04-15 - Phase 5 reopened cleanup complete
- Fixed the stale shipped emit target in `pyproject.toml` so the package and
  example surface now points at `examples/79_final_output_json_object`.

Checks run:
- `uv run --locked python -m unittest tests.test_emit_docs tests.test_final_output tests.test_emit_flow tests.test_output_schema_validation`

Result:
- The reopened Phase 5 package-target cleanup is complete.

Next frontier:
- Phase 10 — Emit the canonical lowered schema artifact.

## 2026-04-15 - Phase 10 complete
- Extended `emit_docs` so structured final outputs now emit the exact lowered
  schema at `schemas/<output-slug>.schema.json`.
- Added `generated_schema_relpath` and `lowered_schema` to the compiled
  final-output model.
- Rendered a `Generated Schema` metadata row in `AGENTS.md`.
- Regenerated the checked-in example proof so structured final-output refs and
  build trees now include the emitted schema artifact.
- Updated package smoke so `make verify-package` now exercises a structured
  final output and checks for the emitted schema file.

Checks run:
- `uv run --locked python -m unittest tests.test_emit_docs tests.test_final_output tests.test_emit_flow`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/79_final_output_json_object/cases.toml --manifest examples/83_review_final_output_json_object/cases.toml --manifest examples/85_review_split_final_output_json_object/cases.toml --manifest examples/90_split_handoff_and_final_output_shared_route_semantics/cases.toml --manifest examples/91_handoff_routing_route_output_binding/cases.toml --manifest examples/104_review_final_output_json_object_blocked_control_ready/cases.toml --manifest examples/105_review_split_final_output_json_object_control_ready/cases.toml --manifest examples/106_review_split_final_output_json_object_partial/cases.toml --manifest examples/55_owner_aware_schema_attachments/cases.toml`

Result:
- Phase 10 proof passed.

Next frontier:
- Phase 11 — Expose the file-based Python validator surface.

## 2026-04-15 - Phase 11 complete
- Moved lowered-schema validation into one shared pure module so the compiler
  and the file validator use the same Draft 2020-12 and OpenAI-subset checks.
- Added `python -m doctrine.validate_output_schema --schema ...` with optional
  `--example ...` support for validating one JSON instance against the emitted
  schema.
- Added focused CLI proof in:
  - `tests/test_validate_output_schema.py`
  - `tests/test_output_schema_validation.py`

Checks run:
- `uv run --locked python -m unittest tests.test_output_schema_validation tests.test_validate_output_schema`
- `uv run --locked python -m doctrine.validate_output_schema --schema examples/79_final_output_json_object/build_ref/repo_status_agent/schemas/repo_status_final_response.schema.json`

Result:
- Phase 11 proof passed.

Next frontier:
- Phase 12 — Add the live OpenAI proof path.

## 2026-04-15 - Phase 12 implementation landed, live proof blocked
- Added `python -m doctrine.prove_output_schema_openai --schema ... --model ...`
  as the official live-proof runner.
- The live runner validates the emitted schema file locally first, then
  submits that exact file through the OpenAI Responses API `text.format`
  `json_schema` path.
- Added focused harness proof in `tests/test_prove_output_schema_openai.py`.
- Updated public docs so the emitted machine contract, the local validator,
  and the live-proof command all point at the same schema file.

Checks run:
- `uv run --locked python -m unittest tests.test_prove_output_schema_openai tests.test_package_release`
- `make verify-examples`
- `make verify-diagnostics`
- `make verify-package`
- `uv run --with openai python -m doctrine.prove_output_schema_openai --schema examples/79_final_output_json_object/build_ref/repo_status_agent/schemas/repo_status_final_response.schema.json --model gpt-4.1`

Result:
- All reachable code and repo proof passed.
- The live OpenAI acceptance run is still blocked in this environment because
  `OPENAI_API_KEY` is not set.

Next frontier:
- Re-run the live OpenAI proof with a real `OPENAI_API_KEY`, then refresh the
  authoritative implementation audit.

## 2026-04-15 - Phase 12 live OpenAI proof passed
- Re-ran the official OpenAI acceptance proof against the emitted schema
  artifact with a real `OPENAI_API_KEY`.
- The live proof accepted the emitted schema file through the Responses API
  `text.format` `json_schema` path.

Checks run:
- `set -a; source /Users/aelaguiz/workspace/psmobile/.env >/dev/null 2>&1; set +a; uv run --with openai python -m doctrine.prove_output_schema_openai --schema examples/79_final_output_json_object/build_ref/repo_status_agent/schemas/repo_status_final_response.schema.json --model gpt-4.1`

Result:
- OpenAI accepted `examples/79_final_output_json_object/build_ref/repo_status_agent/schemas/repo_status_final_response.schema.json`.
- Response id: `resp_0afa39716a6a6e150069dfad3a6e98819487bafaf188ca455e`
- Returned JSON:
  - `{"summary":"","status":"ok","next_step":null}`

Next frontier:
- Fresh implementation audit against the plan doc.
