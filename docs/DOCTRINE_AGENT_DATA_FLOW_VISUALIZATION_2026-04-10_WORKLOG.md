# Worklog

Plan: [DOCTRINE_AGENT_DATA_FLOW_VISUALIZATION_2026-04-10.md](/Users/aelaguiz/workspace/doctrine/docs/DOCTRINE_AGENT_DATA_FLOW_VISUALIZATION_2026-04-10.md)

## 2026-04-11

- Started `implement-loop` on branch
  `feature/agent-flow-visualizer-implement-loop-20260411`.
- Confirmed the loop runtime preflight:
  - `codex_hooks` is enabled.
  - `~/.agents/skills/arch-step/` contains the installed
    `implement_loop_stop_hook.py` runner.
  - `~/.codex/hooks.json` verifies the `arch-step` Stop hook wiring.
- Implementation pass is now in progress for the workflow data-flow visualizer.
- Landed the compiler-owned graph extraction path in `doctrine/compiler.py`:
  - target-scoped flow IR now comes directly from `CompilationContext`
  - shared input/output nodes dedupe by compiler-native declaration identity
  - authored routes, workflow-law routes, currentness carriers, invalidation
    carriers, and route-only `current none` states now surface in the graph
- Extracted emit-target loading into `doctrine/emit_common.py` so
  `emit_docs` and `emit_flow` share the same target registry, prompts-root
  resolution, entrypoint validation, and output-placement rules.
- Added the new public flow emitter and pinned D2 renderer path:
  - `doctrine/emit_flow.py`
  - `doctrine/flow_renderer.py`
  - `doctrine/flow_svg.mjs`
  - repo-root `package.json` / `package-lock.json`
- Extended the verification and smoke surfaces:
  - `doctrine/verify_corpus.py` now includes flow artifacts in build-contract
    proof when the checked tree expects them
  - `doctrine/diagnostic_smoke.py` now proves graph extraction and
    `emit_flow` output naming
- Promoted the first shipped proof target:
  - added `examples/36_invalidation_and_rebuild/build_ref/AGENTS.flow.d2`
  - added `examples/36_invalidation_and_rebuild/build_ref/AGENTS.flow.svg`
- Synced the live docs and repo instructions:
  - `AGENTS.md`
  - `README.md`
  - `docs/README.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/COMPILER_ERRORS.md`
  - `examples/README.md`
- Verification completed for the final pass:
  - `uv sync`
  - `npm install`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/36_invalidation_and_rebuild/cases.toml`
  - `make verify-diagnostics`
  - `make verify-examples`
