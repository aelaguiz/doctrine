---
title: Epic - Doctrine skill graph implementation
date: 2026-04-26
doc_type: epic
status: complete
raw_goal: |
  rewrite this using $prompt-authoring and then execute it using $arch-loop your job is to use $arch-epic to build and automatically implement the solutions for the doctrine repo only (do not change ../lessons_studio) per docs/SKILL_GRAPH_LANGUAGE_SPEC.md and anything nto covered by that that is needed per docs/LESSONS_STUDIO_SKILL_GRAPH_AUDIT.md . maximally elegant solutions. Use $fresh-consult for all planning and implementation so that your own context stays clean as an orchestrator only. Thoughtfully handle issues do not ask for permission. Use gpt-5.4 xhigh for auditing & planning use claude 4.7 xhigh for implementation. Operate fully autonomously and accomplish our intent thoroughly don't get myopic. Max elegance outcome.
raw_goal_sha256: ac90add1d5bcc8cf35d0d41ba2ca140a669aae4a8bd264b35b2fa4af99009b00
sub_plans_approved: true
critic_runtime: codex
critic_model: gpt-5.5
critic_effort: xhigh
models_sha256: 42f95c0b6d662f8b47bca7636cb555f7d99c4e8c794e131c09233b67292589c7
auto_execution:
  schema_version: 1
  approval_policy: auto_after_decomposition
  poll_seconds: 180
  quiet_floor_seconds: 900
  stuck_floor_seconds: 1800
  max_runtime_seconds: 7200
  auto_run_dir: /Users/aelaguiz/workspace/doctrine/.arch_skill/arch-epic/auto/doctrine-skill-graph-2026-04-26/run-2026-04-26T20-50-49Z
  source_quotes:
    epic_planner: codex gpt 5.5 xhigh
    implementation_worker: codex gpt 5.5 xhigh
    repair_worker: codex gpt 5.5 xhigh
    critic: codex gpt 5.5 xhigh
  roles:
    epic_planner:
      runtime: codex
      model: gpt-5.5
      effort: xhigh
      source: user_table
    implementation_worker:
      runtime: codex
      model: gpt-5.5
      effort: xhigh
      source: user_table
    repair_worker:
      runtime: codex
      model: gpt-5.5
      effort: xhigh
      source: user_table
    critic:
      runtime: codex
      model: gpt-5.5
      effort: xhigh
      source: user_table
  execution_sha256: bb8e5435d4c70a079de095371d29e995ad3a751c9d7bf76a462f00d191537489
---

# TL;DR

The Doctrine-side skill graph epic is complete. Phases 1 through 5 now ship
the graph language, graph emit and verify, warning layer, artifact and receipt
surfaces, examples, docs, and `skills/doctrine-learn`. The only accepted
out-of-scope work is the separate `../lessons_studio` migration.

# Decomposition

1. **Receipt core and package bridge**: Add top-level reusable `receipt`
   declarations, receipt inheritance, and package receipt slots that can point
   at a shared receipt type.
   - DOC_PATH: docs/ARCH_RECEIPT_CORE_PACKAGE_BRIDGE_2026-04-26.md
   - Gate to next: Doctrine can compile a reusable receipt, lower it, and let a
     skill package point at it by reference.
   - Status: complete
   - Epic-critic verdict: /tmp/fresh-consult/doctrine-skill-graph-audit-slice1-clean-20260426T154545Z-H6awzV/final.txt (pass)
   - Evidence: example `150_receipt_top_level_decl` plus `make verify-examples`
     (445/445), `make verify-diagnostics`, and `make verify-package`.

2. **Stage core and routed receipts**: Add `stage` declarations and receipt
   route fields that can target stages, flows, or closed sentinels.
   - DOC_PATH: docs/ARCH_STAGE_CORE_ROUTED_RECEIPTS_2026-04-26.md
   - Gate to next: One stage can emit a typed receipt that routes to another
     stage or to `human`, `external`, or `terminal`.
   - Status: shipped
   - Epic-critic verdict: post-ship audit found three blockers; this repair
     pass fixed them and re-ran local verification
   - Evidence: examples `151_stage_basics` (7/7),
     `152_receipt_stage_route` (2/2), and
     `150_receipt_top_level_decl` (5/5) plus `make verify-examples`,
     `make verify-diagnostics`, `make verify-package`, and
     `uv run --locked python -m unittest discover tests` (571/571).

3. **Skill flow core**: Add `skill_flow` DAG declarations with edges, route
   binding, branch conditions, repeats, variations, and changed-workflow
   response shape.
   - DOC_PATH: /Users/aelaguiz/workspace/doctrine/docs/ARCH_SKILL_FLOW_CORE_2026-04-26.md
   - Gate to next: Doctrine can expand one nested flow, prove DAG rules, and
     fail loud when an edge disagrees with a receipt route.
   - Status: shipped
   - Epic-critic verdict: -
   - Evidence: examples `153_skill_flow_linear` (4/4),
     `154_skill_flow_route_binding` (4/4),
     `155_skill_flow_branch` (5/5), and `156_skill_flow_repeat` (5/5);
     `make verify-examples` (472/472), `make verify-diagnostics`,
     `make verify-package`, and `uv run --locked python -m unittest discover
     tests` (571/571). Worklog at
     `docs/ARCH_SKILL_FLOW_CORE_2026-04-26_WORKLOG.md`.

4. **Graph closure and emit base**: Add `skill_graph`, strict closure
   expansion, graph JSON, Markdown views, diagrams, graph source receipts,
   `emit_skill_graph`, and `verify_skill_graph`.
   - DOC_PATH: /Users/aelaguiz/workspace/doctrine/docs/ARCH_SKILL_GRAPH_CLOSURE_EMIT_2026-04-26.md
   - Gate to next: One capstone graph example emits all checked graph views
     from one resolved closure object.
   - Status: shipped
   - Epic-critic verdict: -
   - Evidence: examples `157_skill_graph_closure` (3/3),
     `158_skill_graph_emit` (1/1), and `159_skill_graph_policy` (3/3);
     nearby regressions `150` through `156` stayed green; new focused unit
     tests `tests.test_emit_skill_graph` and `tests.test_verify_skill_graph`
     passed; the `doctrine-learn` build and curated emit targets refreshed the
     shipped graph teaching surface; `make verify-diagnostics`,
     `make verify-examples`, `make verify-package`, and
     `uv run --locked python -m unittest discover tests` (574/574) all
     passed. Worklog at
     `docs/ARCH_SKILL_GRAPH_CLOSURE_EMIT_2026-04-26_WORKLOG.md`.

5. **Graph semantics completion**: Restore the Doctrine-side graph features
   that were cut out of phase 4: direct `skill.relations:`, checked
   `{{skill:Name}}` refs, a real warning layer, `GRAPH.prompt`, receipt schema
   emit, artifact inventory emit, view-scoped graph emit, and the missing
   relaxed graph policy seams.
   - DOC_PATH: /Users/aelaguiz/workspace/doctrine/docs/epic/DOCTRINE_SKILL_GRAPH_2026-04-26/PHASE_05_GRAPH_SEMANTICS_COMPLETION_2026-04-26.md
   - Gate to next: Doctrine can author, emit, warn, and verify the full graph
     contract surface from `SKILL.prompt` or `GRAPH.prompt`, including
     relations, checked mentions, warning output, receipt schemas, durable
     artifact symbols, audit metadata, and the restored graph policy and CLI
     features.
   - Status: complete
   - Auto-run status: implementation worker completed on Codex `gpt-5.5` xhigh at
     `.arch_skill/arch-epic/auto/doctrine-skill-graph-2026-04-26/run-2026-04-26T20-50-49Z`
   - Epic-critic verdict: pass at
     `.arch_skill/arch-epic/auto/doctrine-skill-graph-2026-04-26/run-2026-04-26T20-50-49Z/critics/completion-after-repair/graph-semantics-completion/run-2026-04-26T21-27-52Z/verdict.json`
   - Evidence: examples `160` through `164`, nearby graph manifests `157`
     through `159`, focused graph unit tests, `make verify-diagnostics`,
     `make verify-package`, `make verify-examples` (486/486), and
     `uv run --locked python -m unittest discover tests` (581/581) passed on
     2026-04-26. `git -C ../lessons_studio status --short` returned no output.

6. **Audit-driven authoring completeness**: Restore the remaining
   Doctrine-side audit scope that was still outside compiler-owned graph truth.
   This was folded into sub-plan 5 instead of leaving a second pending doc:
   durable artifact symbols, richer stage repair and waiver metadata, skill
   inventory metadata including aliases, graph-path repeat parity, and the
   final `skills/doctrine-learn` teaching update.
   - DOC_PATH: folded into sub-plan 5
   - Gate to next: This was the last sub-plan. The spec and audit have no known
     remaining Doctrine-side feature gap outside the accepted
     `../lessons_studio` migration boundary.
   - Status: folded into complete phase 5
   - Epic-critic verdict: covered by phase 5 and passed by the final
     completion-after-repair critic

# Orchestration Log

- 2026-04-26 Goal captured. Prompt was refactored with `prompt-authoring`
  rules into a binding implementation contract.
- 2026-04-26 Fresh planning consult ran with Codex `gpt-5.4` xhigh:
  `/tmp/fresh-consult/doctrine-skill-graph-planning-20260426T140613Z-UeWjDo`.
- 2026-04-26 Decomposition drafted as five sub-plans. Marked approved because
  the user explicitly asked for autonomous execution without permission gates.
- 2026-04-26 Sub-plan 1 (Receipt core and package bridge) shipped. New
  `receipt` declarations, `[Parent]` inheritance, by-reference host_contract
  slots, `E544`/`E545` diagnostics, the resolved `ResolvedReceiptHostSlotRef`
  contract shape, and example `150_receipt_top_level_decl` are in. Full
  example corpus (445 cases) and diagnostic + package suites pass.
- 2026-04-26 Fresh Codex audit for sub-plan 1 passed clean after two focused
  repairs: duplicate host slot keys now reach compiler-owned `E535`, and
  aliased receipt refs emit the canonical resolved receipt name.
- 2026-04-26 Sub-plan 2 (Stage core and routed receipts) shipped. New
  top-level `stage` declarations with full typed-fields validation, a
  skeletal `skill_flow` registry, top-level receipt route fields
  targeting `stage`, `flow`, `human`, `external`, and `terminal`,
  `E546`-`E549`/`E559`/`E560` diagnostics, the deterministic `routes`
  metadata in `SKILL.contract.json`, and examples
  `151_stage_basics`/`152_receipt_stage_route` are in. Full corpus
  passes (453/453), plus `make verify-diagnostics`, `make
  verify-package`, and the unit-test suite (571/571).
- 2026-04-26 A fresh Codex audit on sub-plan 2 found three blockers:
  `stage applies_to:` was still doc-only, receipt route fields were not
  yet lowering into receipt-by-ref `json_schema`, and `AGENTS.md` still
  claimed the shipped corpus ended at example 150. This repair pass
  added `applies_to:` ref validation, added conservative receipt
  `json_schema` lowering alongside the existing `routes` map, updated the
  docs and examples, and re-ran the local proof set.
- 2026-04-26 Sub-plan 3 planning doc created at
  `/Users/aelaguiz/workspace/doctrine/docs/ARCH_SKILL_FLOW_CORE_2026-04-26.md`.
  The plan keeps flow-local `skill_flow` parsing, resolution, and
  diagnostics in this slice; keeps graph `sets:`, root closure, policies,
  and emit in sub-plan 4; and keeps warnings plus checked skill mentions in
  sub-plan 5.
- 2026-04-26 Sub-plan 4 planning doc created at
  `/Users/aelaguiz/workspace/doctrine/docs/ARCH_SKILL_GRAPH_CLOSURE_EMIT_2026-04-26.md`.
  The plan keeps top-level `skill_graph`, graph-set closure, graph JSON and
  Markdown emit, D2/SVG/Mermaid output, graph source receipts, and graph
  verify in this slice. It explicitly defers checked skill mentions, the
  warning engine, `GRAPH.prompt`, and direct `skill.relations:` language.
- 2026-04-26 Sub-plan 4 (Graph closure and emit) shipped. Doctrine now has
  top-level `skill_graph`, a graph compile path, graph closure with
  graph-set late binding on the graph path only, graph JSON and Markdown
  emit, graph source receipts, `emit_skill_graph`, `verify_skill_graph`,
  examples `157` through `159`, and the matching docs and release-truth
  updates. The focused graph manifests, nearby regressions `150` through
  `156`, diagnostics, package proof, and the full unit suite all passed.
- 2026-04-26 Sub-plan 4 repair pass closed two same-scope gaps. `skills/doctrine-learn`
  now teaches the shipped graph surface, graph emit and verify, examples
  `150` through `159`, and the exact sub-plan 5 boundary from source; and
  graph source receipts now key top-level diagram hashes to the resolved
  emitted view paths, including `views:` overrides.
- 2026-04-26 Scope-restore planning pass re-read the epic, the language spec,
  the lessons-studio audit, the shipped graph code, and examples `150` through
  `159`. It confirmed that phases 1 through 4 shipped the strict graph core,
  but direct `skill.relations:`, checked skill mentions, a live warning layer,
  `GRAPH.prompt`, `receipt_schema_dir`, relaxed graph policies, and several
  audit-only authoring gaps are still unshipped or only partially modeled.
- 2026-04-26 The decomposition was expanded from five sub-plans to six. Only
  the `../lessons_studio` migration stays out of scope. The next canonical
  plan doc is
  `/Users/aelaguiz/workspace/doctrine/docs/epic/DOCTRINE_SKILL_GRAPH_2026-04-26/PHASE_05_GRAPH_SEMANTICS_COMPLETION_2026-04-26.md`.
- 2026-04-26 Sub-plan 5 planning doc created at
  `/Users/aelaguiz/workspace/doctrine/docs/epic/DOCTRINE_SKILL_GRAPH_2026-04-26/PHASE_05_GRAPH_SEMANTICS_COMPLETION_2026-04-26.md`.
  It restores the cut graph semantics first and leaves the remaining
  audit-driven authoring extensions to sub-plan 6.
- 2026-04-26 Scope-restoration implementation completed. Direct
  `skill.relations:`, checked skill mentions, graph warnings, `GRAPH.prompt`,
  receipt schema emit, artifact inventory emit, graph view selectors,
  `allow unbound_edges`, `dag allow_cycle "Reason"`, graph-path repeat
  sources, skill inventory metadata including aliases, stage entry/repair and
  waiver text, top-level durable `artifact` declarations, and
  artifact-typed stage inputs are in.
- 2026-04-26 The planned sub-plan 6 audit work was folded into sub-plan 5
  instead of being left queued. Only the `../lessons_studio` migration remains
  outside this Doctrine repo pass.
- 2026-04-26 Automatic lane corrected from Codex `gpt-5.4` xhigh to Codex
  `gpt-5.5` xhigh for the epic planner, implementation worker, repair worker,
  and critic. The stale 5.4 run directory had no worker spawned from it; the
  active run is
  `.arch_skill/arch-epic/auto/doctrine-skill-graph-2026-04-26/run-2026-04-26T20-50-49Z`.
- 2026-04-26 Phase 5 status reconciled from `shipped` to `implementing`
  because the implementation claims were in place but the final full-corpus
  proof still had not run.
- 2026-04-26 Final worker pass found one remaining Doctrine-side gap after
  reconciliation: the spec named `W205` branch coverage warnings, but code and
  docs skipped that warning. This pass added `warn branch_coverage_incomplete`
  on the graph path, proved it in example `161_skill_graph_policy_allowances`,
  refreshed `skills/doctrine-learn`, and ran the full proof set.
- 2026-04-26 Phase 5 and the epic are complete from the implementation worker
  side. `uv sync`, `npm ci`, focused graph manifests `157` through `164`,
  focused graph unit tests, `make verify-diagnostics`, `make verify-package`,
  `make verify-examples` (486/486), `uv run --locked python -m unittest
  discover tests` (581/581), and `git -C ../lessons_studio status --short`
  all passed. The `../lessons_studio` status command returned no output.
- 2026-04-26 Completion critic repair ran after verdict
  `.arch_skill/arch-epic/auto/doctrine-skill-graph-2026-04-26/run-2026-04-26T20-50-49Z/critics/completion/graph-semantics-completion/run-2026-04-26T21-07-57Z/verdict.json`
  returned `scope_change_detected` for stale public docs and release truth.
  The repair updated `docs/LANGUAGE_REFERENCE.md`, `CHANGELOG.md`,
  `docs/VERSIONING.md`, and `docs/README.md`, wrote the auto-run
  `repair-report.md`, and reran `make verify-examples`,
  `make verify-package`, `uv run --locked python -m unittest discover tests`
  (581/581), and `git -C ../lessons_studio status --short`. All passed, and
  the `../lessons_studio` status command returned no output.
- 2026-04-26 Completion-after-repair critic passed at
  `.arch_skill/arch-epic/auto/doctrine-skill-graph-2026-04-26/run-2026-04-26T20-50-49Z/critics/completion-after-repair/graph-semantics-completion/run-2026-04-26T21-27-52Z/verdict.json`
  with no discovered items. The critic found the restored Doctrine-side scope,
  public docs, release truth, and proof artifacts complete.

# Decision Log

- 2026-04-26 Advance approval applied: the user asked the orchestrator to
  operate fully autonomously and not ask for permission. This epic treats that
  as approval for the decomposition and for per-sub-plan North Stars, while
  keeping the hard scope guard: Doctrine repo only; no `../lessons_studio`
  edits.
- 2026-04-26 Sub-plan 4 scope line: keep graph emit on existing supported
  entrypoints with an optional target-level `graph = "<Name>"` selector.
  `GRAPH.prompt`, checked `{{skill:Name}}` mentions, the warning engine, and
  direct `skill.relations:` stay out of this slice.
- 2026-04-26 Scope restore rule: only the `../lessons_studio` migration is out
  of scope. Every other Doctrine-side feature named by
  `docs/SKILL_GRAPH_LANGUAGE_SPEC.md` or
  `docs/LESSONS_STUDIO_SKILL_GRAPH_AUDIT.md` stays in this epic until it ships
  or is explicitly disproven by the current Doctrine code.
- 2026-04-26 Automatic lane roles are pinned to Codex `gpt-5.5` xhigh for the
  epic planner, implementation worker, repair worker, and critic.
- 2026-04-26 Historical phase docs for sub-plans 1 through 4 stay as shipped
  records. Restored scope is tracked in the canonical phase 5 doc instead of
  rewriting those shipped plan records.
- 2026-04-26 Sub-plan 6 is no longer a separate pending phase. Its
  Doctrine-side audit items shipped inside sub-plan 5 because splitting them
  would have preserved the same false "cut feature" problem the restore pass
  was meant to fix.
- 2026-04-26 The user asked to stop after doc updates and not begin new coding.
  At that point, full-corpus verification still needed a later explicit run.
- 2026-04-26 Correction to the prior stop note: the user resumed the epic and
  asked for the async automatic implementation path. Use Codex `gpt-5.5`
  xhigh for all automatic roles.
- 2026-04-26 Final proof correction: the later explicit run completed. There
  is no remaining Doctrine-side scope gap known to this worker.
- 2026-04-26 Completion critic repair stayed inside the approved phase 5
  scope. It changed public docs, release-truth records, and arch worklogs only;
  it did not edit `../lessons_studio`.
