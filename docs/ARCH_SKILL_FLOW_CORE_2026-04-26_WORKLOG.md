---
title: "Doctrine - Skill flow core - Worklog"
date: 2026-04-26
status: shipped
related:
  - docs/ARCH_SKILL_FLOW_CORE_2026-04-26.md
  - docs/EPIC_DOCTRINE_SKILL_GRAPH_2026-04-26.md
---

# Summary

Sub-plan 3 lifted top-level `skill_flow` from registry-only to a real
flow-local declaration with `start:`, `approve:`, `edge`, `route:`,
`kind:`, `when:`, `repeat`, `variation`, `unsafe`, and `changed_workflow:`
support, plus local DAG, branch coverage, and route-binding checks. The
new `E561` family covers compile-time flow validation. Parser-owned
`skill_flow` block-shape failures still use parse `E199`. Receipt route
target resolution still uses `E560`. Emit-target source-id/root pairing
keeps `E551`/`E552`. Graph closure across flows, graph policies, and
graph emit stay deferred to sub-plan 4. Checked skill mentions and
graph warnings stay deferred to sub-plan 5.

# Phases completed

- **Phase 1 - Real `skill_flow` declarations and local node resolution.**
  Grammar, parser, model, and a new resolver mixin parse and validate the
  flow-local body. The resolver wires through both `compile_agent` and
  `compile_skill_package`. Example `153_skill_flow_linear` proves a
  positive linear flow with `start:`, two edges, and `approve:`, plus
  `E561` negatives for missing nodes, direct self-edges, and local
  cycles.
- **Phase 2 - Receipt-route-bound edges.** Edge `route:
  ReceiptRef.route_field.choice` resolves through the existing
  `ResolvedReceipt.routes` from sub-plan 2. The strict default forbids
  unbound edges whenever the source stage emits a routed receipt that
  reaches the edge target. Example `154_skill_flow_route_binding` proves
  a route-bound edge through the package compile path plus three
  focused negatives. The example owns its own emit target
  `example_154_skill_flow_route_binding`.
- **Phase 3 - Branches, repeats, variations, and changed-workflow facts.**
  Edge `when:` and `safe_when:` accept only declared enum members. One
  source-level branch rule enforces single-enum coverage with no
  `otherwise:` escape hatch. `repeat <Name>: <FlowRef>` requires
  `over:`, `order:` (closed `serial`/`parallel`/`unspecified`), and
  `why:`. Repeat names are local to the flow, take precedence over
  top-level stage and flow refs, and may not shadow top-level `stage` or
  `skill_flow` declarations. `variation`, `unsafe`, and
  `changed_workflow:` lower into compiler-owned facts only. Examples
  `155_skill_flow_branch` and `156_skill_flow_repeat` prove the
  positive shape plus focused `E561` negatives.
- **Phase 4 - Shipped docs, diagnostics, and release truth.** The skeletal
  skill_flow section in `docs/LANGUAGE_REFERENCE.md` was replaced with
  the real flow-core authoring surface. `docs/COMPILER_ERRORS.md` adds
  the `E561` row and keeps the parser-vs-compile boundary truthful:
  parser-owned `skill_flow` shape errors still use `E199`, while
  compile-time flow validation uses `E561`. `E551`/`E552`/`E560` keep
  their shipped meanings. `docs/README.md` registers the sub-plan doc in
  the active skill-graph trail. `examples/README.md` adds rows for
  examples 153 through 156 and the new emit target command. `AGENTS.md`
  updates the shipped corpus range. `docs/VERSIONING.md` records the
  additive language move within the unreleased `5.7` line; `CHANGELOG.md`
  adds one Unreleased Added entry covering the full body, the resolver,
  the new `E561` family, and the four new examples.

# Files changed

## Implementation
- `doctrine/grammars/doctrine.lark` - extended `skill_flow_body` to parse
  `start:`, `approve:`, `edge`, `repeat`, `variation`, `unsafe`, and
  `changed_workflow:` blocks.
- `doctrine/_parser/skills.py` - lowered the new body items into raw
  model dataclasses with exact source spans; introduced internal Part
  helpers for edge, repeat, and changed-workflow body collection.
- `doctrine/_model/skill_graph.py` - added raw `SkillFlow*Item` shapes
  and resolved `ResolvedSkillFlow*` shapes plus closed value sets
  (`SKILL_FLOW_EDGE_KINDS`, `SKILL_FLOW_REPEAT_ORDERS`,
  `SKILL_FLOW_CHANGED_WORKFLOW_REQUIRES`).
- `doctrine/model.py` - re-exported the new model and resolved shapes.
- `doctrine/_compiler/resolve/skill_flows.py` - new
  `ResolveSkillFlowsMixin` that owns flow-local truth: edge endpoint
  resolution, edge kind/when/route validation, strict-default route
  binding, repeat resolution, branch coverage, variation and unsafe
  lowering, changed-workflow lowering, and local DAG check.
- `doctrine/_compiler/resolve/__init__.py` - registered the new mixin
  in `ResolveMixin`.
- `doctrine/_compiler/context.py` - both `compile_agent` and
  `compile_skill_package` now run `_validate_all_skill_flows_in_flow`
  after the existing rule and stage sweeps.

## Examples
- `examples/153_skill_flow_linear/` (positive plus three negatives).
- `examples/154_skill_flow_route_binding/` (positive plus three
  negatives, with the new `example_154_skill_flow_route_binding` emit
  target).
- `examples/155_skill_flow_branch/` (positive plus four negatives).
- `examples/156_skill_flow_repeat/` (positive plus four negatives).

## Docs and release truth
- `docs/LANGUAGE_REFERENCE.md` - replaced the skeletal `skill_flow`
  section with the real flow-core authoring surface.
- `docs/COMPILER_ERRORS.md` - added the `E561` row.
- `docs/README.md` - added the sub-plan 3 entry.
- `docs/VERSIONING.md` - recorded the additive language move within
  the unreleased `5.7` line.
- `CHANGELOG.md` - added the Unreleased Added entry for the full body,
  the new error code, and the four new examples.
- `AGENTS.md` - bumped the shipped corpus range to
  `examples/156_skill_flow_repeat`.
- `examples/README.md` - registered examples `153`-`156` and added the
  new `emit_skill --target example_154_skill_flow_route_binding`
  command.
- `pyproject.toml` - added the `example_154_skill_flow_route_binding`
  emit target.
- `docs/EPIC_DOCTRINE_SKILL_GRAPH_2026-04-26.md` - marked sub-plan 3
  shipped and recorded local verification evidence.
- `docs/ARCH_SKILL_FLOW_CORE_2026-04-26.md` - flipped status from
  `active` to `shipped`.

# Verification commands and results

- `uv run --locked python -m doctrine.verify_corpus --manifest
  examples/153_skill_flow_linear/cases.toml` - 4/4 PASS.
- `uv run --locked python -m doctrine.verify_corpus --manifest
  examples/154_skill_flow_route_binding/cases.toml` - 4/4 PASS.
- `uv run --locked python -m doctrine.verify_corpus --manifest
  examples/155_skill_flow_branch/cases.toml` - 5/5 PASS.
- `uv run --locked python -m doctrine.verify_corpus --manifest
  examples/156_skill_flow_repeat/cases.toml` - 5/5 PASS.
- `uv run --locked python -m doctrine.verify_corpus --manifest
  examples/151_stage_basics/cases.toml` - 7/7 PASS.
- `uv run --locked python -m doctrine.verify_corpus --manifest
  examples/152_receipt_stage_route/cases.toml` - 2/2 PASS.
- `make verify-diagnostics` - PASS (all diagnostic smoke fixtures).
- `make verify-examples` - 472/472 PASS, 0 FAIL.
- `make verify-package` - PASS (wheel and sdist smoke).
- `uv run --locked python -m unittest discover tests` - 571 tests, OK.

# Residual risk and deferrals

- Graph closure across flows, graph `sets:`, graph policies, graph
  emit, `emit_skill_graph`, and `verify_skill_graph` stay deferred to
  sub-plan 4. The resolver produces a local
  `ResolvedSkillFlow` object that sub-plan 4 can compose without
  re-resolving.
- Repeat `over:` accepts only top-level `enum`, `table`, or `schema`
  refs in this slice. Graph `sets:` arrive in sub-plan 4.
- `when:` and `safe_when:` accept only declared enum members. General
  boolean expressions over graph inputs and prose-only branch
  conditions stay out of scope.
- No `otherwise:` syntax in this slice. Authors must spell every enum
  member explicitly.
- The Doctrine language version stays at `5.7` for now. The skill
  graph language work in sub-plans 1, 2, and 3 ships as one shipped
  language slice within the unreleased `5.7` line and only crosses a
  new language version line at the next public release.
- Checked `{{skill:Name}}` prose refs and the warning layer remain
  deferred to sub-plan 5.

# Lessons-studio untouched

- `git -C ../lessons_studio status --short` - no output (clean tree).
- `git -C ../lessons_studio rev-parse HEAD` -
  `232cd1c0b4e07decaa57240f20ba2a0c090ee749`.

No edits in `../lessons_studio` were performed during this sub-plan.
