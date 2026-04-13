# Modularize Core For Elegant Boundaries - Worklog

Plan: [MODULARIZE_DOCTRINE_CORE_FOR_ELEGANT_BOUNDARIES_2026-04-12.md](MODULARIZE_DOCTRINE_CORE_FOR_ELEGANT_BOUNDARIES_2026-04-12.md)

## 2026-04-12

### Phase 1 - Package discovery and shared type-owner cut

Status: COMPLETE

- Added the internal `doctrine._compiler` package with an explicit internal-only marker.
- Moved the shared compiled and flow data contracts plus `ResolvedRenderProfile`
  into `doctrine/_compiler/types.py`.
- Switched `doctrine/renderer.py` and `doctrine/flow_renderer.py` to import
  shared types from the new canonical owner.
- Replaced the explicit setuptools package list with package discovery for
  `doctrine*`.

### Verification

Completed:

- `uv sync`
- `npm ci`
- `uv run --locked python -m unittest tests.test_emit_flow tests.test_final_output tests.test_review_imported_outputs`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml`

### Phase 2 - Session and indexing foundation extraction

Status: COMPLETE

- Added `doctrine/_compiler/session.py` and moved the live `CompilationSession`
  owner plus the `compile_prompt` and `extract_target_flow_graph` wrappers
  there.
- Added `doctrine/_compiler/indexing.py` and moved `IndexedUnit`, indexing,
  module-root resolution, and import-loading logic there.
- Added `doctrine/_compiler/support.py` and moved the remaining session/indexing
  helper reachback there so those internal owners no longer depend on
  `doctrine.compiler` for prompt-root/import-root and related support helpers.
- Added `doctrine/_compiler/context.py` and moved the session-side compile
  context state plus public entrypoints there so `session.py` no longer imports
  `CompilationContext` from the top-level compiler boundary.
- Added `doctrine/_compiler/shared.py` so the moved context/session/indexing
  owners can share compiler support types and helpers without routing back
  through the top-level `doctrine.compiler` module.
- Rewrote `doctrine/compiler.py` into a thin compatibility facade and removed
  the `context.py` globals-copy shim that previously imported
  `doctrine.compiler` wholesale.
- Reduced `doctrine/_compiler/context.py` to task-local state, public
  entrypoints, and session delegation while the remaining helper families moved
  behind the internal mixins.

### Verification

Completed:

- `uv run --locked python - <<'PY' ...` import sanity check for the public compiler boundary
- `rg -n "doctrine\\.compiler|compiler as _compiler|globals\\(\\)\\.setdefault|_CompilationContextImpl"` across `doctrine/_compiler/context.py`, `doctrine/compiler.py`, and `doctrine/_compiler/shared.py`
- `uv run --locked python - <<'PY' ...` direct `_compiler.context` import sanity check
- `uv run --locked python - <<'PY' ...` thin-context import sanity check for `CompilationContext` keeping only state, entrypoints, and `_load_module` locally
- `python -m py_compile doctrine/compiler.py doctrine/_compiler/shared.py doctrine/_compiler/context.py doctrine/_compiler/session.py doctrine/_compiler/indexing.py doctrine/_compiler/support.py`
- `uv run --locked python -m unittest tests.test_import_loading tests.test_project_config tests.test_verify_corpus tests.test_final_output tests.test_review_imported_outputs tests.test_route_output_semantics`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml`
- `make verify-diagnostics`
- `make verify-examples`

### Phase 3 - Resolution and compile extraction

Status: COMPLETE

- Added `doctrine/_compiler/display.py` and moved the `_render_*` family plus
  the related display helpers there behind a dedicated `DisplayMixin` owner.
- Added `doctrine/_compiler/compile.py` and moved the `_compile_*` family
  there behind a dedicated `CompileMixin` owner.
- Added `doctrine/_compiler/resolve.py` and moved the `_resolve_*` family plus
  the remaining contract-resolution helpers there behind a dedicated
  `ResolveMixin` owner.
- Changed `doctrine/_compiler/context.py` so `CompilationContext` now inherits
  the display, compile, and resolve owners instead of carrying those helper
  families inline.
- Phase 3 is complete.

### Verification

Completed:

- `rg -n "^    def _render_|^    def _natural_language_join|^    def _negate_condition_text|^    def _display_law_path_root"` across `doctrine/_compiler/context.py` and `doctrine/_compiler/display.py`
- `rg -n "^    def _compile_"` across `doctrine/_compiler/context.py` and `doctrine/_compiler/compile.py`
- `rg -n "^    def (_resolve_|_display_ref|_display_readable_decl|_try_resolve_enum_decl|_expr_ref_matches_review_verdict|_find_readable_decl_matches|_find_addressable_root_matches)"` across `doctrine/_compiler/context.py` and `doctrine/_compiler/resolve.py`
- `python -m py_compile doctrine/_compiler/display.py doctrine/_compiler/compile.py doctrine/_compiler/resolve.py doctrine/_compiler/context.py doctrine/compiler.py doctrine/_compiler/session.py doctrine/_compiler/indexing.py doctrine/_compiler/support.py doctrine/_compiler/shared.py`
- `uv run --locked python - <<'PY' ...` mixin import sanity check for `CompileMixin`, `DisplayMixin`, and `ResolveMixin` appearing in `CompilationContext.__mro__`
- `uv run --locked python -m unittest tests.test_emit_flow tests.test_import_loading tests.test_project_config tests.test_verify_corpus tests.test_final_output tests.test_review_imported_outputs tests.test_route_output_semantics`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml`

### Phase 4 - Validation and flow extraction

Status: COMPLETE

- Added `doctrine/_compiler/validate.py` and moved the `_validate_*`,
  `_review_*`, and `_route_*` families plus their remaining helper methods
  there behind a dedicated `ValidateMixin` owner.
- Added `doctrine/_compiler/flow.py` and moved `extract_target_flow_graph`,
  `_collect_flow_*`, and `_flow_*` helpers there behind a dedicated
  `FlowMixin` owner.
- Changed `doctrine/_compiler/context.py` so `CompilationContext` now inherits
  the flow and validate owners alongside the existing Phase 3 mixins, leaving
  only task-local state, public entrypoints, and session delegation in the
  class body.

### Verification

Completed:

- `rg -n "^    def (_validate_|_review_|_route_|_flow_|extract_target_flow_graph|_collect_flow_)"` across `doctrine/_compiler/context.py`, `doctrine/_compiler/validate.py`, and `doctrine/_compiler/flow.py`
- `python -m py_compile doctrine/_compiler/flow.py doctrine/_compiler/validate.py doctrine/_compiler/resolve.py doctrine/_compiler/compile.py doctrine/_compiler/display.py doctrine/_compiler/context.py doctrine/compiler.py doctrine/_compiler/session.py doctrine/_compiler/indexing.py doctrine/_compiler/support.py doctrine/_compiler/shared.py`
- `uv run --locked python - <<'PY' ...` mixin import sanity check for `CompilationContext.__mro__[1] is FlowMixin`, `CompilationContext.__mro__[2] is ValidateMixin`, `CompilationContext.__mro__[3] is CompileMixin`, `CompilationContext.__mro__[4] is DisplayMixin`, and `CompilationContext.__mro__[5] is ResolveMixin`
- `uv run --locked python -m unittest tests.test_emit_flow tests.test_import_loading tests.test_project_config tests.test_verify_corpus tests.test_final_output tests.test_review_imported_outputs tests.test_route_output_semantics`
- `make verify-diagnostics`
- `make verify-examples`

### Phase 5 - Compiler facade cleanup and full proof

Status: COMPLETE

- Kept `doctrine/compiler.py` as the thin public facade while the internal
  owner map finished under `doctrine._compiler`.
- Confirmed the internal owner layout now spans `types.py`, `support.py`,
  `session.py`, `indexing.py`, `display.py`, `compile.py`, `resolve.py`,
  `validate.py`, and `flow.py`.
- Rewrote the stale migration-era comment in `doctrine/_compiler/context.py`
  so the surviving source now describes the finished thin-context boundary
  instead of an in-progress extraction.
- Reran the full shipped proof surface after the final owner cuts.

### Verification

Completed:

- `make verify-diagnostics`
- `make verify-examples`
