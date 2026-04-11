# Worklog

Plan doc: docs/STDLIB_LAYERS_FULL_IMPLEMENTATION_PLAN_2026-04-10.md

## Initial entry
- Run started.
- Current phase: Phase 1 — Shared-root Layer 2 foundation
- Notes:
  - Shared-root authored modules do not exist yet.
  - The current verifier still constrains manifest prompt paths to the owning example directory, so shared-root proof may require a small verification-path convergence change.

## Phase 1 complete
- Implemented the shared authored-source root under `prompts/doctrine/std/**`.
- Added `coordination/enums.prompt`, `coordination/inputs.prompt`,
  `coordination/outputs.prompt`, and `coordination/workflows.prompt`.
- Added the first shared-root conformance entrypoint and example proof at
  `examples/50_stdlib_coordination/`.
- Updated `doctrine/verify_corpus.py` so manifest `default_prompt` and
  case-level `prompt` paths can target repo-root shared entrypoints while
  keeping checked refs example-local.
- Verification:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/50_stdlib_coordination/cases.toml`

## Phase 2 and Phase 3 complete
- Added `prompts/doctrine/std/role_home/workflows.prompt`.
- Added `prompts/doctrine/std/portable_truth/workflows.prompt`.
- Added the shared-root role-home and portable-truth proof at
  `examples/51_stdlib_role_home_and_portable_truth/`.
- Added the first public proving pack under
  `prompts/doctrine/packs_public/code_review/**`.
- Added the public-pack proof example and emitted-build reference under
  `examples/52_public_code_review_pack/`.
- Kept the public pack focused on a single-subject review flow so the proof
  stays about shared-root packaging, role-home reuse, portable truth, and
  review coupling rather than unnecessary pack complexity.
- Verification:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/50_stdlib_coordination/cases.toml --manifest examples/51_stdlib_role_home_and_portable_truth/cases.toml --manifest examples/52_public_code_review_pack/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/36_invalidation_and_rebuild/cases.toml --manifest examples/49_review_capstone/cases.toml`
  - `uv run --locked python -m doctrine.emit_docs --target public_code_review_pack`

## Phase 4 and Phase 5 complete
- Updated the live docs and repo instructions to describe the shipped shared-
  root `prompts/doctrine/std/**` and `prompts/doctrine/packs_public/**`
  layout honestly.
- Added the shared-root emit target for the public pack in `pyproject.toml`.
- Removed unrelated legacy worktree noise under `ports/99_port/`.
- Final verification:
  - `uv sync`
  - `make verify-examples`
- Not run:
  - `make verify-diagnostics` because diagnostics behavior and wording were
    not changed
  - `cd editors/vscode && make` because the VS Code surface was untouched
