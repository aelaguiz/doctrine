# Worklog

Plan doc: docs/DOCTRINE_CROSS_ROOT_STANDARD_LIBRARY_IMPORT_SUPPORT_2026-04-12.md

## Initial entry
- Run started.
- Current phase: Phase 1 - Shared project-config foundation.

## 2026-04-12 - Parent implementation pass reached repo-complete state

- Phase 1:
  - added `doctrine/project_config.py`
  - moved Doctrine project-config loading behind one shared helper for compiler and emit surfaces
  - added targeted config parsing coverage in `tests/test_project_config.py`
- Phase 2:
  - upgraded `doctrine/compiler.py` from one-root import loading to a session-scoped import-root registry
  - kept relative imports rooted in the importing module's owning `prompts/` tree
  - added fail-loud diagnostics for invalid compile config, duplicate configured prompt roots, and ambiguous dotted modules
- Phase 3:
  - threaded resolved project config through `doctrine/emit_common.py`, `doctrine/emit_docs.py`, and `doctrine/emit_flow.py`
  - added `examples/75_cross_root_standard_library_imports/` with two local entrypoint families, one shared authored root, and negative proof for invalid root plus ambiguous import cases
  - preserved `examples/03_imports` as the single-root baseline
- Phase 4:
  - updated `editors/vscode/resolver.js` to load `[tool.doctrine.compile].additional_prompt_roots` through a real TOML parser
  - added integration coverage for cross-root link/definition behavior and ambiguous-import fail-closed behavior
  - fixed the VS Code integration staging runner so runtime dependencies are present in the packaged test extension
- Phase 5:
  - updated live docs and repo instructions for the new compile contract and example family
  - updated `AGENTS.md` shipped-corpus range to include example `75`
  - re-ran repo verification for compiler, corpus, diagnostics, and VS Code surfaces
  - ran the external `../rally` smoke against the real shared-root layout

Verification:

- `uv sync`
- `python -m py_compile doctrine/compiler.py doctrine/project_config.py doctrine/emit_common.py doctrine/emit_docs.py doctrine/emit_flow.py doctrine/verify_corpus.py doctrine/diagnostics.py`
- `uv run --locked python -m unittest tests.test_import_loading`
- `uv run --locked python -m unittest tests.test_project_config tests.test_import_loading tests.test_emit_flow tests.test_verify_corpus`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/75_cross_root_standard_library_imports/cases.toml`
- `npm ci`
- `make verify-examples`
- `make verify-diagnostics`
- `cd editors/vscode && make`
- external `../rally` compile/render smoke via `uv run --locked python - <<'PY' ...`

Notes:

- Repo-local Doctrine verification is green for the changed compiler, emit, diagnostics, corpus, and VS Code surfaces.
- The external `../rally` smoke now proves the cross-root feature path directly: `PlanAuthor` compiles through shared-root imports, and `Closeout` also compiles under the same repo-level config contract.
- `RouteRepair` in `../rally/flows/_stdlib_smoke/prompts/AGENTS.prompt` still fails with `E339` because `RallyNoCurrentArtifactHandoff.next_owner` does not structurally bind `RoutingOwner`; that is a downstream authored-law issue, not a Doctrine cross-root import failure.
- The session-scoped `implement-loop` state remains armed.
- Fresh `audit-implementation` still owns the authoritative code verdict and any later disarm decision.
