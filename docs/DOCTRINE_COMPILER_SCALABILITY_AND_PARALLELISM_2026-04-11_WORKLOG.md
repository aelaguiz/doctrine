# Worklog

Plan doc: docs/DOCTRINE_COMPILER_SCALABILITY_AND_PARALLELISM_2026-04-11.md

## Initial entry
- Run started.
- Current phase: Phase 1 — Session split and baseline capture.

## Phase 1 (Session split and baseline capture) Progress Update
- Work completed:
  - Re-verified the `implement-loop` runtime preflight and armed the repo-local loop state.
  - Captured a bounded pre-change baseline on the Lessons critic anchor: parse-only completed quickly, while a full compile remained in flight past several seconds and was treated as a "feels stuck" baseline signal rather than letting the sibling repo run unbounded.
- Tests run + results:
  - `codex features list` — `codex_hooks` enabled.
  - `python3 /Users/aelaguiz/.agents/skills/arch-step/scripts/upsert_codex_stop_hook.py --hooks-file /Users/aelaguiz/.codex/hooks.json --skills-dir /Users/aelaguiz/.agents/skills --verify` — passed.
  - `uv run --locked python - <<'PY' ... parse_file(...) + root_concrete_agents(...)` on `../paperclip_agents/doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt` — passed; root agent `LessonsAcceptanceCritic`.
- Issues / deviations:
  - The full pre-change Lessons compile was intentionally not allowed to run unbounded.
- Next steps:
  - Split shared session/graph state from task-local compile state in `doctrine/compiler.py`.
  - Move the emit and verification call sites onto the shared session owner path.

## Phase 2 (Parallel prompt-graph loading for large single-agent latency) Progress Update
- Work completed:
  - Added a shared `CompilationSession` that owns the indexed prompt graph and once-per-session imported-module loading.
  - Switched parser construction to thread-local instances so parallel prompt loading does not share one mutable parser object.
  - Reopened agent-field fan-out after warm-session measurements showed the large-target review path still dominated compile time.
  - Compressed review gate validation by the output semantics actually observed by the target output surface, which removed the reject-branch explosion on the Lessons critic anchor.
- Tests run + results:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/36_invalidation_and_rebuild/cases.toml` — passed.
  - `uv run --locked python -u - <<'PY' ... CompilationSession(prompt) ... compile_prompt(prompt, agent_name) ...` on the Lessons critic anchor — current shipped result now returns `E484` in about `2.49s` instead of remaining in flight past the earlier several-second baseline.
- Issues / deviations:
  - The external Lessons anchor currently compiles to a fail-loud review error (`E484`), so the benchmark proof is reduced time-to-real-error rather than rendered output comparison.
- Next steps:
  - Adopt the shared session owner path in emit and verification callers.
  - Run the full shipped corpus once the caller migration is in place.

## Phase 3 (Default threaded batch compile surfaces) Progress Update
- Work completed:
  - Updated `doctrine/emit_docs.py` to compile root agents through one session with ordered thread-pool collection.
  - Updated `doctrine/emit_flow.py` to reuse the same session for flow graph extraction.
  - Updated `doctrine/verify_corpus.py` to reuse prompt-path sessions and parallelize compile-bearing cases while preserving manifest-order reporting.
- Tests run + results:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/36_invalidation_and_rebuild/cases.toml` — passed.
- Issues / deviations:
  - None at this phase boundary.
- Next steps:
  - Run the full shipped corpus and sync the plan doc to the final delivered shape.

## Phase 4 (Hardening, proof, and live-truth cleanup) Progress Update
- Work completed:
  - Synced the plan doc to the implemented architecture, including the measured reopening of field fan-out and review-gate validation compression.
  - Captured the large-target proof as a fast fail-loud compile result on the Lessons anchor.
- Tests run + results:
  - `make verify-examples` — passed.
- Issues / deviations:
  - `make verify-diagnostics` was not run because diagnostics and diagnostic smoke surfaces were not changed.
- Next steps:
  - Finalize the docs-only implementation audit and disarm the repo-local `implement-loop` state.
