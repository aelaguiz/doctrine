---
title: "Doctrine - Skill graph closure and emit - Worklog"
date: 2026-04-26
status: shipped
related:
  - docs/ARCH_SKILL_GRAPH_CLOSURE_EMIT_2026-04-26.md
  - docs/EPIC_DOCTRINE_SKILL_GRAPH_2026-04-26.md
---

# Summary

Sub-plan 4 shipped top-level `skill_graph`, graph closure, graph JSON and
Markdown emit, D2/SVG/Mermaid output, graph source receipts, graph verify,
graph build-contract corpus routing, examples `157` through `159`, and the
matching `doctrine-learn` teaching surface. A same-scope repair pass also
fixed top-level graph receipt summary hashes for overridden view paths. The
work stayed inside the Doctrine repo and left `../lessons_studio` untouched.

# Run facts

- Date: 2026-04-26
- Worker: Codex `gpt-5.4` with `xhigh` reasoning, per the user override for
  this implementation worker
- Repo boundary: work stayed in `/Users/aelaguiz/workspace/doctrine`
- Shell rule followed: repo commands ran through `rtk proxy`
- Shared worktree rule followed: existing dirty files were treated as shared
  state and were not reverted

# Phases completed

- **Phase 1 - Parser, model, and registry surfaces.** Added grammar and parser
  lowering for top-level `skill_graph`, added raw graph model dataclasses,
  added resolved graph and resolved stage dataclasses, indexed
  `skill_graph` as a first-class declaration, and re-exported the new model
  surface through `doctrine/model.py`.
- **Phase 2 - Resolver seam repair and graph closure.** Upgraded
  `ResolveStagesMixin` to return cached resolved stage facts, kept ordinary
  agent and skill-package flow validation strict, added graph-only repeat
  late binding, added `ResolveSkillGraphsMixin`, and exposed graph compile
  from session, context, and the public compiler boundary.
- **Phase 3 - Graph JSON, Markdown, diagrams, and source receipt.** Added one
  resolved graph closure object, lowered it to graph contract JSON and
  query JSON, rendered graph Markdown views, rendered D2 and Mermaid, reused
  the pinned D2 SVG path, and added `SKILL_GRAPH.source.json` with input,
  output, and linked package receipt hashes.
- **Phase 4 - CLI, target plumbing, verify, and corpus routing.** Added
  `doctrine.emit_skill_graph`, `doctrine.verify_skill_graph`, the target-level
  `graph = "<Name>"` selector, graph-aware direct emit mode, and graph
  build-contract routing in `verify_corpus`.
- **Phase 5 - Examples, docs, release truth, and regressions.** Added
  examples `157_skill_graph_closure`, `158_skill_graph_emit`, and
  `159_skill_graph_policy`, added focused graph unit tests, updated the
  shipped docs and release truth, refreshed the `doctrine-learn` graph
  teaching refs plus both emitted doctrine-learn trees, and ran the focused
  plus broad proof set.

# Files changed

## Implementation
- `doctrine/grammars/doctrine.lark`
- `doctrine/_parser/skills.py`
- `doctrine/_model/skill_graph.py`
- `doctrine/_model/declarations.py`
- `doctrine/model.py`
- `doctrine/_compiler/declaration_kinds.py`
- `doctrine/_compiler/indexing.py`
- `doctrine/_compiler/context.py`
- `doctrine/_compiler/session.py`
- `doctrine/compiler.py`
- `doctrine/_compiler/resolve/__init__.py`
- `doctrine/_compiler/resolve/stages.py`
- `doctrine/_compiler/resolve/skill_flows.py`
- `doctrine/_compiler/resolve/skill_graphs.py`
- `doctrine/emit_common.py`
- `doctrine/emit_skill_graph.py`
- `doctrine/verify_skill_graph.py`
- `doctrine/skill_graph_source_receipts.py`
- `doctrine/_skill_graph_render/__init__.py`
- `doctrine/_skill_graph_render/markdown.py`
- `doctrine/_skill_graph_render/d2.py`
- `doctrine/_skill_graph_render/mermaid.py`
- `doctrine/_verify_corpus/manifest.py`
- `doctrine/_verify_corpus/runners.py`

## Tests and examples
- `tests/test_emit_skill_graph.py`
- `tests/test_verify_skill_graph.py`
- `examples/157_skill_graph_closure/`
- `examples/158_skill_graph_emit/`
- `examples/159_skill_graph_policy/`
- `pyproject.toml`

## Docs and release truth
- `AGENTS.md`
- `CHANGELOG.md`
- `docs/COMPILER_ERRORS.md`
- `docs/EMIT_GUIDE.md`
- `docs/LANGUAGE_REFERENCE.md`
- `docs/README.md`
- `docs/SKILL_PACKAGE_AUTHORING.md`
- `docs/VERSIONING.md`
- `examples/README.md`
- `docs/ARCH_SKILL_GRAPH_CLOSURE_EMIT_2026-04-26.md`
- `docs/EPIC_DOCTRINE_SKILL_GRAPH_2026-04-26.md`

## Skill teaching surface
- `skills/doctrine-learn/prompts/SKILL.prompt`
- `skills/doctrine-learn/prompts/refs/language_overview.prompt`
- `skills/doctrine-learn/prompts/refs/examples_ladder.prompt`
- `skills/doctrine-learn/prompts/refs/emit_targets.prompt`
- `skills/doctrine-learn/prompts/refs/skill_graphs.prompt`
- `skills/doctrine-learn/build/`
- `skills/.curated/doctrine-learn/`

# Verification log

- `uv sync` - PASS
- `npm ci` - PASS
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/157_skill_graph_closure/cases.toml` - 3/3 PASS
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/158_skill_graph_emit/cases.toml` - 1/1 PASS
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/159_skill_graph_policy/cases.toml` - 3/3 PASS
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/150_receipt_top_level_decl/cases.toml` - 5/5 PASS
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/151_stage_basics/cases.toml` - 7/7 PASS
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/152_receipt_stage_route/cases.toml` - 2/2 PASS
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/153_skill_flow_linear/cases.toml` - 4/4 PASS
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/154_skill_flow_route_binding/cases.toml` - 4/4 PASS
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/155_skill_flow_branch/cases.toml` - 5/5 PASS
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/156_skill_flow_repeat/cases.toml` - 5/5 PASS
- `uv run --locked python -m unittest tests.test_emit_skill_graph` - 1 test, OK
- `uv run --locked python -m unittest tests.test_verify_skill_graph` - 2 tests, OK
- `uv run --locked python -m unittest discover tests` - 574 tests, OK
- `make verify-diagnostics` - PASS
- `make verify-examples` - PASS
- `make verify-package` - PASS
- `git -C ../lessons_studio status --short` - no output (clean tree)

## Repair pass verification

- `rtk proxy uv sync` - PASS
- `rtk proxy npm ci` - PASS
- `rtk proxy uv run --locked python -m doctrine.emit_skill --target doctrine_learn_skill --target doctrine_learn_public_skill` - PASS; emitted 17 files to `skills/doctrine-learn/build` and 17 files to `skills/.curated/doctrine-learn`
- `rtk proxy uv run --locked python -m unittest tests.test_emit_skill_graph tests.test_verify_skill_graph` - PASS; 3 tests, OK
- `rtk proxy uv run --locked python - <<'PY' ... emit_target_skill_graph(target, output_dir_override=repo / 'examples/158_skill_graph_emit/build_ref')` - PASS; refreshed the checked-in `example_158` graph build tree through the normal graph emit path
- `rtk proxy uv run --locked python -m doctrine.verify_corpus --manifest examples/157_skill_graph_closure/cases.toml` - PASS; 3/3
- `rtk proxy uv run --locked python -m doctrine.verify_corpus --manifest examples/158_skill_graph_emit/cases.toml` - PASS; 1/1
- `rtk proxy uv run --locked python -m doctrine.verify_corpus --manifest examples/159_skill_graph_policy/cases.toml` - PASS; 3/3
- `rtk proxy make verify-diagnostics` - PASS
- `rtk proxy uv run --locked python -m unittest discover tests` - PASS; 574 tests, OK
- `rtk proxy make verify-package` - PASS
- `rtk proxy make verify-examples` - PASS
- `rtk proxy git -C ../lessons_studio status --short` - no output (clean tree)

# Scope discoveries

- Graph-set late binding could not safely replace the shipped local
  `skill_flow` check outright. The implementation keeps ordinary
  agent and skill-package compiles strict on `repeat over:` and turns on the
  graph-set candidate seam only for `compile_skill_graph`.
- Linked package receipts are best-effort evidence. Graph emit records them
  only when one unique configured skill target already exposes
  `SKILL.source.json`.

# Open blockers

- None. Sub-plan 4 is ready for a fresh final audit.
