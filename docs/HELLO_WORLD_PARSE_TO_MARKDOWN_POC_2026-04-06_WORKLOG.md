# Worklog

Plan doc: [docs/HELLO_WORLD_PARSE_TO_MARKDOWN_POC_2026-04-06.md](/Users/aelaguiz/workspace/pyprompt/docs/HELLO_WORLD_PARSE_TO_MARKDOWN_POC_2026-04-06.md)

## 2026-04-06

- Started `arch-step implement` on branch `hello-world-lark-bootstrap`.
- Warn-first preflight: `deep_dive_pass_1` and `phase-plan` are complete; `external_research_grounding` and `deep_dive_pass_2` remain unset, but the plan already locks a narrow owner path, parser mode, fixture, and verification command.
- Created local ignore rules for `.venv/` and `__pycache__/` so verification setup does not pollute the worktree.
- Phase 1 is now in progress.
- Paused code work to repair a truth-surface bug in the plan: `.prompt` is the input language SSOT, while `AGENTS.md` is approximate output and may contain bugs.
- Updated the plan so advisory diffs against `AGENTS.md` examples no longer masquerade as exact compiler truth.
- Ran an end-to-end plan consistency audit and corrected stale corpus references so the canonical doc now reflects `examples/10_turn_outcomes` and `examples/11_skills_and_tools` instead of the old `10_runtime_roots` wording.
- Created the canonical owner path: `pyproject.toml`, repo-root `Makefile`, and the `pyprompt/` package with grammar, indenter, model, parser, compiler, renderer, and `check_hello_world`.
- Added ignore coverage for `.venv/`, `__pycache__/`, and `*.egg-info/` before local verification setup.
- Set up `.venv/` and installed the declared bootstrap dependencies with `pip install -e .`.
- Phase 1 verification passed: the parser now parses `examples/01_hello_world/prompts/AGENTS.prompt` as-authored and returns both `HelloWorld` and `HelloWorld2`.
- Implementation surfaced one real language edge: under `strict=True`, `%ignore SH_COMMENT` collided with `_NL`, so the bootstrap comment contract was tightened to standalone `#` lines carried by `_NL`.
- Phase 2 verification passed: `make hello-world PYTHON=.venv/bin/python` exits `0`.
- Negative checks passed: missing target selection, reordered fields, repeated fields, missing workflow, and an extra unsupported field all fail loudly.
- Phase 3 doc sync is complete: updated `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md`, and `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md` to match the shipped bootstrap.
- Re-opened the canonical plan for one explicit architecture correction: `check_hello_world` is acceptable bootstrap proof, but it must not become the long-term compiler testing pattern.
- Added a new Phase 4 in the plan to research and re-cut a reusable compiler verification framework before more examples turn testing into a proliferation of hard-coded checker modules.
- Completed `arch-step external-research` on compiler verification best practices and folded the results into the canonical plan.
- External research converged on one shared corpus verifier, adjacent machine-readable case manifests under `examples/`, layered assertion styles, first-class negative cases, and deferred fuzzing as a later complement.
- Updated the plan so the next recommended move is another deep-dive pass to lock the shared verifier UX and case-manifest schema before more code lands.
- Tightened the shared-verifier seed set in the canonical plan: the first manifest-backed corpus should cover `HelloWorld`, `HelloWorld2`, and `examples/02_sections`.
- Kept that seed-set decision honest in the plan: `02_sections` is part of the first output-manifest surface, but it is not being pretended green before the grammar grows to support it.
