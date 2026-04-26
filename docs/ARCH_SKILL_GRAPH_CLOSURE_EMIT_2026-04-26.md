---
title: "Doctrine - Skill graph closure and emit - Architecture Plan"
date: 2026-04-26
status: shipped
fallback_policy: forbidden
owners: [Codex]
reviewers: [aelaguiz]
doc_type: architectural_change
related:
  - docs/EPIC_DOCTRINE_SKILL_GRAPH_2026-04-26.md
  - docs/SKILL_GRAPH_LANGUAGE_SPEC.md
  - docs/LESSONS_STUDIO_SKILL_GRAPH_AUDIT.md
  - docs/ARCH_RECEIPT_CORE_PACKAGE_BRIDGE_2026-04-26.md
  - docs/ARCH_STAGE_CORE_ROUTED_RECEIPTS_2026-04-26.md
  - docs/ARCH_SKILL_FLOW_CORE_2026-04-26.md
  - doctrine/grammars/doctrine.lark
  - doctrine/_parser/skills.py
  - doctrine/_model/skill_graph.py
  - doctrine/model.py
  - doctrine/_compiler/declaration_kinds.py
  - doctrine/_compiler/context.py
  - doctrine/_compiler/indexing.py
  - doctrine/_compiler/session.py
  - doctrine/_compiler/resolve/skill_flows.py
  - doctrine/_compiler/resolve/stages.py
  - doctrine/_compiler/resolve/receipts.py
  - doctrine/emit_common.py
  - doctrine/emit_flow.py
  - doctrine/flow_renderer.py
  - doctrine/verify_corpus.py
  - pyproject.toml
  - docs/LANGUAGE_REFERENCE.md
  - docs/SKILL_PACKAGE_AUTHORING.md
  - docs/EMIT_GUIDE.md
  - docs/COMPILER_ERRORS.md
  - examples/README.md
  - docs/VERSIONING.md
  - CHANGELOG.md
  - AGENTS.md
---

# TL;DR

- Outcome: Doctrine will add a real top-level `skill_graph` boundary, one
  canonical graph closure object, graph emit, graph verify, and graph source
  receipts.
- Problem: sub-plans 1-3 now prove receipts, stages, and local `skill_flow`
  facts, but nothing yet closes those facts into one checked graph or emits
  the graph views the spec needs.
- Approach: keep stage, receipt, and flow resolution as the source of truth,
  add one graph resolver on top, then emit every graph artifact from that one
  closure.
- Hard lines: do not touch `../lessons_studio`, do not add checked
  `{{skill:Name}}` mentions, do not add a warning engine, and do not broaden
  runtime scheduling semantics.

# 0) Holistic North Star

## 0.1 The claim

After this slice ships, a Doctrine prompt can declare one top-level
`skill_graph` with roots, sets, recovery refs, policies, and views, and
Doctrine will either close that graph into one stable object and emit all
required graph artifacts, or fail with graph-specific errors. The worker will
not need parent context to know which graph facts are compiler-owned and which
runtime behaviors are still out of scope.

## 0.2 In scope

- Top-level `skill_graph Name: "Title"` declarations with:
  `purpose:`, `roots:`, `sets:`, `recovery:`, `policy:`, and `views:`.
- Graph closure over root stages, root flows, nested flows, repeat nodes,
  reached stages, stage owners, support skills, stage inputs, emitted
  receipts, route choices, package links, and graph sets.
- A graph-owned resolved object that is the one source for JSON, Markdown, D2,
  SVG, Mermaid, and source-receipt emit.
- Graph contract JSON and query-friendly graph JSON.
- Markdown views for graph markdown, skill inventory, flow registry, stage
  contracts, recovery audit, and stepwise manifest.
- `SKILL_GRAPH.source.json` with graph input hashes, graph output hashes, and
  linked package receipt hashes when those receipts are already available.
- `doctrine.emit_skill_graph` and `doctrine.verify_skill_graph`.
- Manifest-backed examples through the graph emit and policy slice.
- Docs, diagnostics, versioning, changelog, and `AGENTS.md` alignment for the
  shipped slice.

## 0.3 Out of scope

- Checked `{{skill:Name}}` prose refs and `require checked_skill_mentions`.
- A real warning engine, warning codes, or live warning output.
- `../lessons_studio` edits or migration work.
- Broad runtime scheduling, memory, or orchestration semantics.
- A new `GRAPH.prompt` entrypoint kind.
- Direct `skill.relations:` language in this slice.
- Per-receipt schema file emission such as `receipt_schema_dir`.
- Policy relaxers such as `allow unbound_edges` or `dag allow_cycle`.

## 0.4 Key invariants

- One resolved graph closure owns all graph emit. No view may rebuild graph
  truth from raw AST strings.
- Existing `E544` through `E561` meanings stay intact.
- Flow-local checks from sub-plan 3 stay strict unless this plan names the
  exact seam that moves to graph closure.
- Recovery and stepwise views stay static authoring truth. They do not claim
  live runtime state.
- Package receipt hashes are optional evidence. Missing optional package
  receipts must not block graph emit.

# 1) Epic Requirement Coverage

| Requirement | Disposition in sub-plan 4 | Owner / note |
| --- | --- | --- |
| Top-level `skill_graph` declarations | Owned here | Required core language for this slice |
| Graph `purpose:` | Owned here | Required field |
| Graph roots over `flow` and `stage` refs | Owned here | Compile-owned root closure |
| Graph `sets:` | Owned here | Includes repeat-over late binding |
| Graph recovery refs | Owned here | `flow_receipt`, `stage_status`, and `durable_artifact_status` only |
| Graph policy syntax needed for this slice | Owned here | Strict items only; warning items may be inert metadata |
| Graph-wide closure over root flows, nested flows, repeats, stages, receipts, routes, packages, and sets | Owned here | Core resolver work |
| Graph contract JSON | Owned here | `SKILL_GRAPH.contract.json` |
| Query-friendly graph JSON | Owned here | `references/skill-graph.json` |
| Markdown views: graph markdown, skill inventory, flow registry, stage contracts, recovery audit, stepwise manifest | Owned here | Static authoring views only |
| D2, SVG, and Mermaid output from the same closure | Owned here | Reuse pinned D2 SVG helper |
| `SKILL_GRAPH.source.json` | Owned here | Includes linked package receipt hashes when available |
| `doctrine.emit_skill_graph` | Owned here | New CLI |
| `doctrine.verify_skill_graph` | Owned here | New CLI |
| Manifest-backed examples through the graph emit and policy slice | Owned here | Examples 157-159 or clearly better equivalent |
| `skills/doctrine-learn` graph teaching surface | Owned here | Must teach shipped graph authoring, emit, verify, examples 150-159, and sub-plan 5 deferrals |
| Parser, docs, diagnostics, versioning, changelog, and `AGENTS.md` alignment | Owned here | Required ship truth |
| Stage declarations and routed receipts | Already satisfied | Shipped in sub-plan 2 |
| Full local `skill_flow` body and local DAG checks | Already satisfied | Shipped in sub-plan 3 |
| Checked `{{skill:Name}}` prose refs | Deferred | Sub-plan 5 |
| Warning engine and warning codes | Deferred | Sub-plan 5 |
| `GRAPH.prompt` entrypoint support | Out of scope | Not part of the approved sub-plan 4 slice |
| `skill.relations:` and relation emit | Out of scope | Not in the approved decomposition; do not add here |
| Lessons-studio migration or edits | Out of scope | Must stay untouched |

# 2) Current Architecture And Exact Surfaces To Change

## 2.1 What exists today

- `doctrine/grammars/doctrine.lark` knows `receipt`, `stage`, and full
  `skill_flow`, but not `skill_graph`.
- `doctrine/_model/skill_graph.py` already owns raw and resolved flow shapes,
  plus receipt route targets, but it has no graph-level or resolved-stage
  model.
- `ResolveStagesMixin` validates stage declarations but does not return a
  resolved stage object the graph layer can consume.
- `ResolveSkillFlowsMixin` returns one `ResolvedSkillFlow`, but it still treats
  `repeat over:` as local-only (`enum`, `table`, or `schema`) and does not
  know about graph sets.
- `skills/doctrine-learn` still does not teach the shipped graph surface from
  source. The generated tree has stale proposal-era graph docs, but the
  authored prompt map does not own that surface anymore.
- `CompilationContext` validates all visible stages and skill flows on agent
  and skill-package compile, but there is no graph validation sweep or graph
  compile path.
- `emit_skill.py` and `verify_skill_receipts.py` show the current source
  receipt and verify pattern that graph emit should mirror.
- `_verify_corpus/runners.py` routes every `SKILL.prompt` build target through
  `emit_skill`, so build-contract examples cannot yet prove graph emit.

## 2.2 Existing files that must change

- `doctrine/grammars/doctrine.lark`
- `doctrine/_parser/skills.py`
- `doctrine/_model/skill_graph.py`
- `doctrine/model.py`
- `doctrine/_compiler/declaration_kinds.py`
- `doctrine/_compiler/indexing.py`
- `doctrine/_compiler/context.py`
- `doctrine/_compiler/session.py`
- `doctrine/compiler.py`
- `doctrine/_compiler/resolve/__init__.py`
- `doctrine/_compiler/resolve/skill_flows.py`
- `doctrine/_compiler/resolve/stages.py`
- `doctrine/_compiler/resolve/receipts.py`
- `doctrine/emit_common.py`
- `doctrine/verify_corpus.py`
- `doctrine/_verify_corpus/runners.py`
- `pyproject.toml`
- `docs/LANGUAGE_REFERENCE.md`
- `docs/SKILL_PACKAGE_AUTHORING.md`
- `docs/EMIT_GUIDE.md`
- `docs/COMPILER_ERRORS.md`
- `examples/README.md`
- `docs/VERSIONING.md`
- `CHANGELOG.md`
- `AGENTS.md`
- `skills/doctrine-learn/prompts/SKILL.prompt`
- `skills/doctrine-learn/prompts/refs/language_overview.prompt`
- `skills/doctrine-learn/prompts/refs/examples_ladder.prompt`
- `skills/doctrine-learn/prompts/refs/emit_targets.prompt`

## 2.3 New files that should be added

- `doctrine/_compiler/resolve/skill_graphs.py`
- `doctrine/emit_skill_graph.py`
- `doctrine/verify_skill_graph.py`
- `doctrine/skill_graph_source_receipts.py`
- `doctrine/_skill_graph_render/markdown.py`
- `doctrine/_skill_graph_render/d2.py`
- `doctrine/_skill_graph_render/mermaid.py`
- `tests/test_emit_skill_graph.py`
- `tests/test_verify_skill_graph.py`
- `examples/157_skill_graph_closure/`
- `examples/158_skill_graph_emit/`
- `examples/159_skill_graph_policy/`
- `skills/doctrine-learn/prompts/refs/skill_graphs.prompt`

## 2.4 Existing files that should stay read-only in this slice

- `doctrine/emit_flow.py` except as a reuse reference
- `doctrine/flow_renderer.py` except as the reused SVG helper
- `../lessons_studio/**`

# 3) Phase Plan

## Phase 1 - Parser, model, and registry surfaces

Status: COMPLETE

Work:

- Add `skill_graph_decl` grammar and body rules for `purpose:`, `roots:`,
  `sets:`, `recovery:`, `policy:`, and `views:`.
- Extend `doctrine/_parser/skills.py` to lower closed raw graph items with
  exact source spans.
- Extend `doctrine/_model/skill_graph.py` with raw graph dataclasses and one
  resolved graph family.
- Add `skill_graph` to `DECLARATION_KINDS`, `UnitDeclarations`, and
  `IndexedFlow`.
- Re-export the new graph model from `doctrine/model.py`.

Done when:

- `skill_graph` declarations parse and index cleanly.
- Duplicate graph blocks and unknown body items fail loud at the same parser
  boundary style the repo already uses.

## Phase 2 - Resolver seam repair and graph closure

Status: COMPLETE

Work:

- Upgrade `ResolveStagesMixin` from validate-only to cached resolved-stage
  output so graph closure can consume canonical owner, support, lane, input,
  emit, checkpoint, and `applies_to:` facts.
- Adjust `ResolveSkillFlowsMixin` so `repeat over:` keeps local resolution for
  `enum`, `table`, and `schema`, but can carry a graph-set candidate forward
  for graph closure instead of hard-failing too early.
- Add `ResolveSkillGraphsMixin` in
  `doctrine/_compiler/resolve/skill_graphs.py`.
- Add `_validate_all_skill_graphs_in_flow` beside the existing stage and flow
  sweeps, and add a direct graph compile path on session/context for emit and
  tests.

Resolver rules:

- Graph roots must resolve to top-level `stage` or `skill_flow`.
- `sets:` names are graph-local and closed by name.
- `recovery:` refs must resolve to one top-level `receipt` and two top-level
  enums.
- A reached stage with `applies_to:` must include every reaching flow.
- Closure must walk:
  root stages, root flows, nested flow nodes, repeat target flows, reached
  stages, stage inputs and emits, edge route bindings, owner skills, support
  skills, package ids, and recovery refs.
- The closure should produce both:
  one authored-node graph for emit and one expanded stage-edge graph for
  graph-wide DAG checks.
- `dag acyclic` runs on the expanded graph.
- `repeat` nodes stay templates. They do not count as cycles unless the child
  flow expands back into an ancestor stage path.

Done when:

- One `ResolvedSkillGraph` (or equivalently named graph closure object) can be
  fetched by graph name from a session without compiling an agent wrapper.
- Graph closure owns the facts later phases need. Emit phases do not re-scan
  the raw AST.

## Phase 3 - Graph JSON, Markdown, diagrams, and source receipt

Status: COMPLETE

Work:

- Lower `ResolvedSkillGraph` into:
  `SKILL_GRAPH.contract.json` and `references/skill-graph.json`.
- Render stable Markdown views from the same closure:
  `skill-graph.md`, `skill-inventory.md`, `flow-registry.md`,
  `stage-contracts.md`, `recovery-audit.md`, and `stepwise-manifest.md`.
- Render D2 and Mermaid from the same closure, then call the existing
  `render_flow_svg` helper for SVG.
- Add `doctrine/skill_graph_source_receipts.py` that mirrors the skill
  receipt pattern but uses graph-owned inputs and outputs.

Emit rules:

- Default output paths use the spec names unless `views:` overrides them.
- View keys are closed in v1.
- View paths must stay inside the target output dir.
- The graph markdown is the short overview view. It should state graph name,
  purpose, roots, sets, policy summary, and reached counts without repeating
  full stage tables.
- The recovery audit and stepwise manifest are static generated references.
  They do not claim live runtime progress.
- Graph source receipt inputs should cover the prompt files that define the
  owning graph and the reached declarations. Outputs should cover every emitted
  graph artifact except the receipt itself.
- Linked package receipts are best-effort evidence. When a unique configured
  emit target already exposes a `SKILL.source.json`, record its identity and
  hash. When none exists, record nothing and do not fail emit.

Done when:

- A single graph emit pass writes every required artifact from one resolved
  graph object.
- D2, SVG, and Mermaid stay deterministic across repeated runs.

## Phase 4 - CLI, target plumbing, verify, and corpus routing

Status: COMPLETE

Work:

- Add `doctrine.emit_skill_graph` CLI.
- Add `doctrine.verify_skill_graph` CLI.
- Extend `EmitTarget` and `load_emit_targets` with an optional `graph`
  selector so one target can point at a specific visible `skill_graph`.
- Keep entrypoints on the existing supported set. Do not add `GRAPH.prompt`.
- Extend `_verify_corpus/runners.py` so a `build_contract` target with a
  configured graph selector runs `emit_skill_graph`, not `emit_skill`.

CLI rules:

- `emit_skill_graph` supports configured target mode first.
- Direct mode may reuse the existing supported entrypoints, but it must still
  require a graph name when more than one graph is visible.
- `verify_skill_graph` should follow the skill-receipt pattern:
  read on-disk graph receipt, verify actual tree shape, re-emit to a temp dir,
  compare receipt payloads, and then compare any linked package receipt hashes
  that the graph receipt recorded.

Done when:

- Graph emit and graph verify work from a configured target without manual
  setup.
- Build-contract examples can prove graph output trees under `verify_corpus`.

## Phase 5 - Examples, docs, release truth, and regressions

Status: COMPLETE

Work:

- Add three manifest-backed examples:
  `157_skill_graph_closure`, `158_skill_graph_emit`, and
  `159_skill_graph_policy`, or a clearly better equivalent trio that still
  separates closure, emit, and policy proof.
- Add target entries in `pyproject.toml` for the graph build-contract example
  targets.
- Update docs and release truth:
  `docs/LANGUAGE_REFERENCE.md`, `docs/SKILL_PACKAGE_AUTHORING.md`,
  `docs/EMIT_GUIDE.md`, `docs/COMPILER_ERRORS.md`, `examples/README.md`,
  `docs/VERSIONING.md`, `CHANGELOG.md`, and repo `AGENTS.md`.
- Add focused unit tests and diagnostic smoke coverage for graph emit and
  verify.

Example split:

- `157_skill_graph_closure` should prove graph roots, sets, recovery refs, and
  closure-owned compile failures.
- `158_skill_graph_emit` should be the capstone build-contract example. It
  should lock graph Markdown, both JSON files, D2, SVG, Mermaid, and
  `SKILL_GRAPH.source.json`.
- `159_skill_graph_policy` should lock graph-owned strict policy failures such
  as expanded-cycle detection, missing `stage_lane` under policy, and
  unresolved graph-set repeat refs.

Done when:

- The new examples teach one new idea each and prove the shipped graph emit
  story end to end.

# 4) Diagnostics Plan

## 4.1 New code family

Use the next unused band after `E561`.

| Code | Stage | Summary | Scope |
| --- | --- | --- | --- |
| `E562` | compile | Invalid skill graph | Bad graph body shape after parse, bad roots, bad sets, bad recovery refs, unsupported strict policy key, unsupported graph warning key syntax, graph-set repeat that never resolves, stage `applies_to:` closure mismatch, or expanded graph cycle |
| `E563` | emit | Invalid skill graph target | Unknown requested graph, ambiguous graph selection, or a target that names a graph the entrypoint graph cannot see |
| `E564` | emit | Invalid skill graph view path | Closed view-key violations that can only be proven at emit time, view path escaping the output dir, or output-path collisions inside one graph target |
| `E565` | emit | Skill graph emit failed | Graph emit found no reachable closure, D2 or Mermaid render failed, or graph source receipt could not be written |

## 4.2 Verify statuses

Keep verify results as status strings, not new W-codes.

- `current`
- `missing_graph_receipt`
- `stale_graph_source`
- `edited_graph_artifact`
- `missing_package_receipt`
- `stale_package_receipt`
- `graph_contract_mismatch`
- `unsupported_graph_receipt_version`

## 4.3 Non-collision rules

- Do not move or widen `E544` through `E561`.
- Keep parser-owned `skill_flow` block-shape errors on `E199`.
- Keep local flow errors on `E561`.
- Keep emit-target config on `E550` through `E553`.
- Add no warning codes in this slice.

# 5) Verification Plan

## 5.1 Focused manifest proof

Run these first:

- `uv run --locked python -m doctrine.verify_corpus --manifest examples/157_skill_graph_closure/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/158_skill_graph_emit/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/159_skill_graph_policy/cases.toml`

Run the nearby regression set next because graph closure depends on these
surfaces:

- `uv run --locked python -m doctrine.verify_corpus --manifest examples/150_receipt_top_level_decl/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/151_stage_basics/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/152_receipt_stage_route/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/153_skill_flow_linear/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/154_skill_flow_route_binding/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/155_skill_flow_branch/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/156_skill_flow_repeat/cases.toml`

## 5.2 Focused unit and smoke proof

- `uv sync`
- `npm ci`
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_skill`
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_public_skill`
- `uv run --locked python -m unittest tests.test_emit_skill_graph`
- `uv run --locked python -m unittest tests.test_verify_skill_graph`
- `uv run --locked python -m unittest discover tests`
- `make verify-diagnostics`

## 5.3 Full repo proof

- `make verify-examples`
- `make verify-package`

## 5.4 Repo-boundary proof

- `git -C ../lessons_studio status --short`

Expected result: no output. If it is dirty, record that plainly and confirm no
files there were touched.

# 6) Decision Log

- 2026-04-26: Keep `GRAPH.prompt` out of sub-plan 4. The approved scope is
  graph closure and emit, not a new flow-boundary kind. Graph targets should
  work from existing supported entrypoints plus an optional target-level
  `graph = "<Name>"` selector.
- 2026-04-26: Keep `skill.relations:` out of sub-plan 4. The approved slice
  can close lessons-studio-style stage, flow, receipt, and package truth
  without adding a second new language family.
- 2026-04-26: Keep checked `{{skill:Name}}` mentions out of sub-plan 4.
  `require checked_skill_mentions` is not allowed to silently no-op. It stays
  deferred to sub-plan 5.
- 2026-04-26: Keep the warning engine out of sub-plan 4. Warning policy items
  may be carried as inert metadata only if that materially shrinks sub-plan 5.
  They must not emit warnings or new warning codes now.
- 2026-04-26: Keep `allow unbound_edges` and `dag allow_cycle` out of sub-plan
  4. Those relax shipped flow invariants and would force a second policy owner
  path. This slice stays strict.
- 2026-04-26: Graph-set repeat refs are late-bound at graph closure. Local
  flow resolution still resolves `enum`, `table`, and `schema` immediately.
  Unknown `repeat over:` refs are not accepted as generic strings. They must
  resolve as graph-set candidates in a later graph closure or fail with
  `E562`.
- 2026-04-26: `recovery_audit` and `stepwise_manifest` are static authoring
  views only. They must not claim live runtime progress, task state, or
  scheduler decisions.
- 2026-04-26: `skills/doctrine-learn` is part of the shipped sub-plan 4 truth,
  not a follow-up. It must teach the shipped graph surface, graph emit and
  verify, examples `150` through `159`, and the exact sub-plan 5 boundary.
- 2026-04-26: Do not emit per-receipt schema files in sub-plan 4. The required
  slice already ships receipt facts in the graph contract and query JSON. A
  dedicated schema directory can wait.
- 2026-04-26: Intent-derived. Keep shipped local `skill_flow` validation
  strict on ordinary agent and skill-package compiles, and turn on graph-set
  late binding only on the graph compile path. Section 0 and Section 7 both
  require the new graph seam without breaking sub-plan 3 proof. The compile
  path now keeps `E561` for old local flow checks while `compile_skill_graph`
  uses graph-aware repeat late binding and raises `E562` when a graph set is
  still missing.

# 7) Acceptance Checklist

- [x] `skill_graph Name: "Title"` parses with `purpose:`, `roots:`, `sets:`,
  `recovery:`, `policy:`, and `views:`.
- [x] `skill_graph` is indexed as a first-class top-level declaration and can
  be looked up by graph name from a compile session.
- [x] `ResolveStagesMixin` returns cached resolved stage facts that graph
  closure consumes.
- [x] `ResolveSkillFlowsMixin` still enforces shipped local flow rules and adds
  the graph-set late-binding seam for `repeat over:`.
- [x] A new graph resolver builds one canonical closure object that includes:
  roots, reached flows, repeat nodes, reached stages, owner skills, support
  skills, package ids, receipts, route choices, graph sets, recovery refs,
  policy facts, and derived adjacency maps.
- [x] Graph closure fails with `E562` when a root does not resolve, a graph-set
  repeat never resolves, a recovery ref is wrong-kind or missing, a reached
  stage is outside its declared `applies_to:`, or the expanded graph has a
  cycle.
- [x] Accepted strict policy keys are either already enforced by shipped stage
  and flow code or are newly enforced by graph closure. Unsupported strict keys
  fail loud. No warning engine ships.
- [x] `CompilationSession` and the public compiler boundary expose a graph
  compile path that emit and tests can call without compiling an agent.
- [x] `emit_skill_graph` writes all required graph artifacts from one closure:
  `SKILL_GRAPH.contract.json`, `SKILL_GRAPH.source.json`,
  `references/skill-graph.json`, `references/skill-graph.md`,
  `references/skill-inventory.md`, `references/flow-registry.md`,
  `references/stage-contracts.md`, `references/recovery-audit.md`,
  `references/stepwise-manifest.md`, `references/skill-graph.d2`,
  `references/skill-graph.svg`, and `references/skill-graph.mmd`.
- [x] D2, SVG, and Mermaid all come from the same closure object. SVG reuses
  the existing pinned D2 helper path. No view parses another emitted view.
- [x] `SKILL_GRAPH.source.json` records graph inputs, graph outputs, graph
  hashes using the resolved graph view paths, including `views:` overrides,
  and linked package receipt hashes when those receipts are available.
- [x] `verify_skill_graph` reports the agreed status set and catches missing or
  edited graph artifacts plus stale linked package receipts when they were
  recorded.
- [x] `EmitTarget`, `load_emit_targets`, and `verify_corpus` support graph
  targets without changing the existing docs, flow, or skill target behavior.
- [x] Examples `157_skill_graph_closure`, `158_skill_graph_emit`, and
  `159_skill_graph_policy` prove the slice and keep the teaching ladder clear.
- [x] `skills/doctrine-learn` teaches the shipped graph surface from source:
  top-level `receipt`, `stage`, `skill_flow`, `skill_graph`, graph emit and
  verify, examples `150` through `159`, and the sub-plan 5 deferrals. Both
  the local `build/` tree and the curated mirror refresh from emit targets.
- [x] `docs/LANGUAGE_REFERENCE.md`, `docs/SKILL_PACKAGE_AUTHORING.md`,
  `docs/EMIT_GUIDE.md`, `docs/COMPILER_ERRORS.md`, `examples/README.md`,
  `docs/VERSIONING.md`, `CHANGELOG.md`, and `AGENTS.md` match the shipped
  behavior.
- [x] `git -C ../lessons_studio status --short` stays clean and no files there
  are edited.
