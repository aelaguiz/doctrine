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
- Re-entered `arch-step implement` for Phase 5 and marked the shared-verifier migration as in progress in the canonical plan before touching code.
- Confirmed the current migration target is still exactly the planned one: replace `pyprompt/check_hello_world.py` with `pyprompt.verify_corpus`, move the Hello World contracts into adjacent `cases.toml`, keep `02_sections` planned-only, and make the verifier summary explicitly show active cases, planned cases, advisory ref diffs, and surfaced inconsistencies.
- Implementation immediately exposed one verifier-schema bug in the plan: `compile_fail` cases were missing an explicit `agent` field even though the compiler boundary requires intentional target selection after parse succeeds.
- Repaired that schema bug in the canonical plan instead of hiding it inside ad hoc verifier defaults.
- Shipped `pyprompt/verify_corpus.py` as the shared verifier and deleted `pyprompt/check_hello_world.py` so the repo now has one compiler-verification owner path.
- Added adjacent machine-readable manifests at `examples/01_hello_world/cases.toml` and `examples/02_sections/cases.toml`.
- Added two checked-in local negative fixtures under `examples/01_hello_world/prompts/` to exercise parse-stage and compile-stage failure contracts through the same verifier.
- Rewired `make hello-world` to the filtered manifest run and added `make verify-examples` for the active corpus plus planned-case reporting.
- Verification passed with `./.venv/bin/python -m pyprompt.verify_corpus --manifest examples/01_hello_world/cases.toml`, `./.venv/bin/python -m pyprompt.verify_corpus`, `make hello-world PYTHON=./.venv/bin/python`, and `make verify-examples PYTHON=./.venv/bin/python`.
- The first shipped shared-verifier run surfaced no unresolved language inconsistencies, no advisory ref diffs, and no need for new `.gitignore` rules because this phase only added checked-in manifests and prompt fixtures.
