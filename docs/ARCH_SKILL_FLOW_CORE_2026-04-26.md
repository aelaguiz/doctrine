---
title: "Doctrine - Skill flow core - Architecture Plan"
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
  - doctrine/grammars/doctrine.lark
  - doctrine/_parser/skills.py
  - doctrine/_model/skill_graph.py
  - doctrine/_compiler/context.py
  - doctrine/_compiler/resolve/__init__.py
  - doctrine/_compiler/resolve/stages.py
  - doctrine/_compiler/resolve/receipts.py
  - docs/LANGUAGE_REFERENCE.md
  - docs/COMPILER_ERRORS.md
  - examples/README.md
  - pyproject.toml
  - CHANGELOG.md
  - docs/VERSIONING.md
---

# TL;DR

- Outcome: Doctrine will accept full top-level `skill_flow` declarations with local DAG checks, route binding checks, repeats, variations, and changed-workflow facts, while keeping graph-wide closure and emit out of this slice.
- Problem: sub-plan 2 only registered `skill_flow` names. Authors can point receipt routes at flows, but they still cannot declare the flow itself as typed compiler-owned structure.
- Approach: add one flow-local resolver on top of the existing stage and receipt registries. Reuse the routed-receipt facts from sub-plan 2 instead of inventing a second routing system.
- Plan: expand grammar and parser, add resolved flow model plus compile sweep, prove the slice with examples `153` through `156`, then sync docs and release truth.
- Non-negotiables: keep `E560` unchanged, do not repurpose shipped `E551`, do not add `skill_graph`, policies, warnings, checked skill mentions, or graph emit here, and do not invent an `otherwise:` syntax in this slice.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: complete (2026-04-26)
external_research_grounding: complete (2026-04-26; repo-grounded only, no web needed)
deep_dive_pass_2: complete (2026-04-26)
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

After this slice ships, a Doctrine prompt can declare a non-trivial `skill_flow`
with `start:`, `edge`, `repeat`, `variation`, `unsafe`, `approve:`, and
`changed_workflow:` entries, and the compiler will either resolve the flow
against the current stage and receipt truth or fail with stable skill-flow
errors. No `skill_graph`, graph policy, graph warning, or graph emit surface is
added in this slice.

## 0.2 In scope

- Full `skill_flow` body support in `doctrine.lark`, parser lowering, public
  model exports, and a new flow-local resolver.
- `intent:`, `start:`, `approve:`, and `edge Source -> Target:` entries.
- Edge-local `route:`, `kind:`, `when:`, and required `why:`.
- Target resolution for top-level `stage` refs, nested top-level `skill_flow`
  refs, and local `repeat` refs.
- Local recursive flow expansion only as far as needed to validate refs and DAG
  shape for one authored flow.
- `repeat Name: FlowRef` with required `over:`, `order:`, and `why:`, plus
  local name uniqueness and shadowing checks.
- `variation` and `unsafe` entries, with `safe_when:` validation for safe
  variations.
- `changed_workflow:` with compiler-owned lowered facts only.
- Route-binding validation against resolved receipt route fields from
  sub-plan 2, including exact edge-target matching.
- Shipped docs, diagnostics, and examples `153_skill_flow_linear`,
  `154_skill_flow_route_binding`, `155_skill_flow_branch`, and
  `156_skill_flow_repeat`.

## 0.3 Out of scope

- Top-level `skill_graph` declarations, graph roots, graph `sets:`, recovery
  metadata, graph-wide closure, graph policies, graph JSON, Markdown graph
  views, diagrams, `emit_skill_graph`, and `verify_skill_graph`.
- Checked `{{skill:Name}}` prose refs and the graph warning layer.
- Any edit in `../lessons_studio`.
- General boolean `when:` expressions over graph inputs. This slice supports
  enum-member branch conditions only.
- Graph-set `repeat over:` refs. This slice validates only local declared
  collection surfaces.
- An authored `otherwise:` surface. Authors must spell enum branches
  explicitly in this slice.

## 0.4 Definition of done (acceptance evidence)

- `examples/153_skill_flow_linear/cases.toml` proves a positive linear flow and
  focused `E561` negatives for bad node or DAG shape.
- `examples/154_skill_flow_route_binding/cases.toml` proves route-bound edges
  on a package compile path and focused `E561` negatives for missing or wrong
  edge binding.
- `examples/155_skill_flow_branch/cases.toml` proves enum-member branching,
  coverage rules, safe variation validation, and changed-workflow lowering.
- `examples/156_skill_flow_repeat/cases.toml` proves repeat-node resolution,
  local repeat-name precedence, `order:` validation, and shadowing checks.
- `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md`,
  `examples/README.md`, `docs/README.md`, `docs/VERSIONING.md`, and
  `CHANGELOG.md` tell the same story as the code.
- No broad verify is part of this plan gate. The slice proves itself with the
  four new manifests plus `make verify-diagnostics`.

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks or silent auto-binding. A routed edge either binds the exact
  route choice or fails.
- `E560` keeps its routed-receipt meaning. New flow-local failures use a new
  code family.
- No second handoff language appears on stages. Receipt route fields stay the
  only source of truth for routed stage-to-stage handoff.
- No graph-wide owner path is added here. All new behavior stays local to
  `skill_flow` resolution.
- Existing stage and receipt behavior must stay unchanged for prompts that do
  not opt into the new flow surface.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Make `skill_flow` fail loud on local structural mistakes.
2. Reuse the shipped stage and receipt truth instead of copying it.
3. Keep sub-plan 4 free to add graph-wide closure and emit on top of the same
   resolved flow object.
4. Keep the authoring surface small enough that examples `153` through `156`
   each teach one new idea.

## 1.2 Constraints

- `E551` and `E552` are already shipped emit-target diagnostics, so this slice
  cannot reuse those numbers.
- Doctrine has no shipped warning layer today.
- Graph `sets:` do not exist yet, so repeat validation must stop short of that
  boundary.
- Stage declarations already resolve `applies_to:` against the skeletal
  `skill_flow` registry. The new flow resolver must not break that slice.
- This turn is planning only. The plan must not depend on broad verify or code
  edits outside this repo.

## 1.3 Architectural principles (rules we will enforce)

- One resolver owns flow-local truth. Do not scatter flow checks across emit,
  examples, or docs helpers.
- Route binding is explicit under the strict default. Do not infer or silently
  pick a receipt route when a stage already emits one.
- Branch and variation conditions stay typed. In this slice that means enum
  members, not free prose.
- Keep graph-wide semantics out of sub-plan 3. If a rule needs graph roots,
  graph sets, or policy switches, it belongs to sub-plan 4 or 5.
- Prefer resolved model facts over ad hoc string parsing in later phases.

## 1.4 Known tradeoffs (explicit)

- This slice chooses strict enum-member branch coverage instead of warnings,
  because Doctrine still lacks a warning layer.
- This slice does not add `otherwise:` because the approved inputs name the
  idea but do not pin a stable authored form.
- `repeat over:` will be narrower than the proposal. It will validate only
  local declared collection surfaces now, and graph `sets:` later.
- `changed_workflow:` lowers to compiler-owned facts only. It will not emit a
  new public artifact until sub-plan 4 adds graph contract emit.

## 1.5 Epic Requirement Coverage

| Requirement | Sub-plan 3 disposition | Later owner |
| --- | --- | --- |
| Full `skill_flow` body grammar/model/parser/resolver support | Owned here | - |
| `intent:` and `start:` | Owned here | - |
| `approve:` final handoff ref | Owned here because it is part of the full body shape and appears in the approved spec examples | - |
| `edge Source -> Target:` with `route:`, `kind:`, `when:`, and required `why:` | Owned here | - |
| Target resolution for stage refs, nested flow refs, and local repeat refs | Owned here | - |
| Local recursive expansion and DAG validation for one flow | Owned here | - |
| Route-binding validation against resolved receipt route fields, including target match | Owned here; `E560` stays reserved for receipt route target resolution only | - |
| Branch conditions over enum members with minimal diagnostics | Owned here as strict compile checks on duplicate, mixed-family, or incomplete enum branching | Warning form later in sub-plan 5 |
| `otherwise:` branch edge | Explicitly not added in this slice; authors must spell enum-member branches explicitly because the approved inputs do not pin a stable authored form | No named owner in this epic |
| `repeat Name: FlowRef` with `over:`, `order:`, and `why:` | Owned here | Graph-set `over:` refs later in sub-plan 4 |
| `variation` and `unsafe`, plus `safe_when:` validation | Owned here | - |
| `changed_workflow:` with `allow provisional_flow` and `require ...` items | Owned here as compiler-owned model facts only | Emitted graph contract later in sub-plan 4 |
| Graph `sets:`, root closure, policies, graph JSON/Markdown emit, `emit_skill_graph`, `verify_skill_graph` | Deferred | Sub-plan 4 |
| Checked `{{skill:Name}}` refs and graph warnings | Deferred | Sub-plan 5 |
| Docs and examples `153` through `156` | Owned here | - |

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Sub-plan 2 added top-level `stage` declarations, receipt route fields, and a
skeletal `skill_flow` registry. The compiler can now resolve:

- `stage owner`, `supports`, `inputs`, and `emits`
- receipt route targets to `stage`, `flow`, and sentinels
- stage `applies_to:` refs against the top-level flow registry

But the registry-only `skill_flow` surface still accepts only `intent:`. It
does not own node order, route-authorized edges, branch conditions, repeats,
variations, or changed-workflow facts.

## 2.2 What’s broken / missing (concrete)

- Authors can point a receipt route at a flow, but cannot declare what that
  flow actually does.
- There is no compiler-owned place to say which stage starts a flow, which
  stage can follow which other stage, or whether a branch covers all enum
  members.
- Repeats, safe variations, unsafe variations, and changed-workflow responses
  are still prose-only.
- The current diagnostic catalog has no skill-flow-specific compile code. The
  spec suggested `E551`, but that code is already shipped for emit-target
  config.

## 2.3 Constraints implied by the problem

- Flow logic must build on the existing stage and receipt truth instead of
  duplicating it.
- The first useful slice must stay local. Graph roots, policies, and emit can
  wait, but authors still need a real flow declaration now.
- The diagnostic story must preserve shipped meanings and avoid silent
  renumbering.

# 3) Research Grounding (external + internal "ground truth")

## 3.1 External anchors (papers, systems, prior art)

- `docs/SKILL_GRAPH_LANGUAGE_SPEC.md` is the approved proposal anchor. Adopt:
  typed `skill_flow` declarations, route-bound edges, repeat nodes,
  safe/unsafe variations, and changed-workflow facts. Defer from this slice:
  graph `sets:`, graph-wide policy switches, graph emit, warnings, and
  `otherwise:` syntax.
- `docs/LESSONS_STUDIO_SKILL_GRAPH_AUDIT.md` is the concrete product-pressure
  anchor. Adopt: flow registry should become compiler-owned truth instead of
  prose, and stage handoffs should stay on typed receipts. Defer: any product
  policy judgment and any `../lessons_studio` refactor.

## 3.2 Internal ground truth (code as spec)

- `doctrine/grammars/doctrine.lark` and `doctrine/_parser/skills.py` show that
  `skill_flow` is currently registry-only.
- `doctrine/_model/skill_graph.py` and `doctrine/model.py` already carry the
  skeletal flow and routed-receipt shapes. This is the canonical model surface
  to extend.
- `doctrine/_compiler/resolve/stages.py` proves the current owner path for
  stage-local skill-graph facts.
- `doctrine/_compiler/resolve/receipts.py` already resolves routed-receipt
  choices and is the canonical source for route-binding checks.
- `doctrine/_compiler/context.py` is where flow-wide validation sweeps run
  today.
- `docs/COMPILER_ERRORS.md` and `tests/test_project_config.py` prove that
  `E551` and `E552` are already claimed by emit-target config.
- `docs/ARCH_STAGE_CORE_ROUTED_RECEIPTS_2026-04-26.md` is the authoritative
  upstream slice boundary: stage and receipt routing shipped; real flow
  expansion did not.

The canonical owner path for this slice is a new
`doctrine/_compiler/resolve/skill_flows.py` mixin wired through
`doctrine/_compiler/resolve/__init__.py` and `doctrine/_compiler/context.py`.

## 3.3 Decision gaps that must be resolved before implementation

No plan-shaping gaps remain.

Fixed decisions for implementation:

- Use a new `E561` family for compile-time skill-flow validation.
- Keep parser-owned `skill_flow` block-shape failures on parse `E199`.
- Keep `E560` only for receipt route target resolution.
- Support enum-member `when:` and `safe_when:` only.
- Support local `repeat over:` refs to declared `enum`, `table`, or `schema`
  only. Graph `sets:` wait for sub-plan 4.
- Do not add `otherwise:` in this slice.

# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/grammars/doctrine.lark`: top-level `skill_flow` accepts only
  `intent:`.
- `doctrine/_parser/skills.py`: lowers only `SkillFlowIntentItem`.
- `doctrine/_model/skill_graph.py`: has `SkillFlowDecl` plus routed-receipt and
  stage models, but no resolved flow object.
- `doctrine/_compiler/resolve/stages.py`: validates all stages once per flow.
- `doctrine/_compiler/resolve/receipts.py`: resolves receipt route targets and
  emits `ResolvedReceiptRouteField`.
- `doctrine/_compiler/context.py`: runs stage validation during
  `compile_agent` and `compile_skill_package`.
- `examples/151_stage_basics` and `examples/152_receipt_stage_route`: prove the
  current slice boundary.

## 4.2 Control paths (runtime)

1. Parse prompt files into top-level declarations.
2. Index declarations into the per-flow registries.
3. During compile, validate all rules and all stages.
4. Resolve receipt-by-ref host slots when a package compiles.
5. Emit `SKILL.contract.json` route data only from the resolved receipt.

No step validates actual flow topology today.

## 4.3 Object model + key abstractions

- `StageDecl` is a real top-level declaration with typed fields.
- `SkillFlowDecl` is only a name, title, and optional `intent:`.
- `ResolvedReceipt` already carries routed-receipt facts that a future flow
  resolver can consume.
- No compile-owned object describes resolved flow nodes, resolved edges, repeat
  nodes, or changed-workflow facts.

## 4.4 Observability + failure behavior today

- Bad routed-receipt targets fail with `E560`.
- Bad stage structure fails with `E546` through `E549` and `E559`.
- Bad flow structure cannot fail because the structure does not exist yet.
- The warning layer is documented but not shipped.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. This is compile-time language work only.

# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Extend `doctrine/grammars/doctrine.lark` and `doctrine/_parser/skills.py` to
  parse the full `skill_flow` body surface.
- Extend `doctrine/_model/skill_graph.py` and `doctrine/model.py` with raw and
  resolved flow-local dataclasses.
- Add `doctrine/_compiler/resolve/skill_flows.py` for flow-local resolution and
  diagnostics.
- Wire the new mixin through `doctrine/_compiler/resolve/__init__.py` and
  `doctrine/_compiler/context.py`.
- Leave graph-wide emit, graph contract JSON, and graph verification out of
  this slice.

## 5.2 Control paths (future)

1. Index top-level `stage`, `receipt`, and `skill_flow` declarations as today.
2. Validate all stages as today.
3. Validate all skill flows once per compile flow:
   - parse and normalize raw body items
   - resolve `start:` and `approve:`
   - register local repeat names
   - resolve edges against stages, nested flows, and local repeats
   - read routed-receipt facts from the source stage's emitted receipt
   - validate route binding, branch conditions, variations, and
     changed-workflow items
   - expand nested flow refs only as far as needed to prove a local DAG
4. Cache the resolved flow object per owner unit and flow name, just like other
   resolver surfaces.

## 5.3 Object model + abstractions (future)

- Add raw `skill_flow` body items for:
  - `start`
  - `approve`
  - `edge`
  - `repeat`
  - `variation`
  - `unsafe`
  - `changed_workflow`
- Add resolved flow-local facts for:
  - resolved node identity and node kind
  - resolved edge route binding
  - resolved enum-branch condition identity
  - resolved repeat metadata
  - resolved variation metadata
  - resolved changed-workflow requirements
  - derived terminal nodes for later graph emit

No public graph artifact is emitted yet. These are compiler-owned model facts
that sub-plan 4 can reuse.

## 5.4 Invariants and boundaries

- Use `E561` for compile-time skill-flow validation. Parser-owned
  `skill_flow` block-shape failures stay on parse `E199`. Keep shipped
  `E551`, `E552`, and `E560` meanings intact.
- `kind:` is a closed set in this slice:
  `normal`, `review`, `repair`, `recovery`, `approval`, `handoff`.
- `when:` and `safe_when:` accept only declared enum members in this slice.
- If any outgoing edge from a source stage uses enum-member branching, every
  branch edge from that source must use the same enum family and cover each
  member exactly once. There is no `otherwise:` escape hatch here.
- `route:` is optional in syntax but required in semantics whenever the source
  stage emits a routed receipt that has a choice to the chosen target.
- `repeat over:` accepts only a top-level `enum`, `table`, or `schema` ref in
  this slice. Graph `sets:` and input/field-path variants wait for sub-plan 4.
- `approve:` is optional and resolves to a top-level `skill_flow` ref only.
- No graph policy flags, warning downgrades, or relaxed `allow unbound_edges`
  behavior exist in this slice.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.

# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Surface | Files | Required change | Why |
| --- | --- | --- | --- |
| Grammar | `doctrine/grammars/doctrine.lark` | Replace the skeletal `skill_flow` body with the full flow-local body syntax. | This is the parser gate for every owned requirement in this slice. |
| Parser lowering | `doctrine/_parser/skills.py` | Lower the new body items with exact source spans. | Flow diagnostics must point at authored lines. |
| Model exports | `doctrine/_model/skill_graph.py`, `doctrine/model.py` | Add raw and resolved flow-local dataclasses and export them publicly. | Later compiler phases and docs rely on stable model names. |
| Compile owner path | `doctrine/_compiler/resolve/skill_flows.py` (new), `doctrine/_compiler/resolve/__init__.py`, `doctrine/_compiler/context.py` | Add one new resolver mixin plus one flow-wide validation sweep. | Keeps flow-local truth in one canonical place. |
| Stage/receipt integration | `doctrine/_compiler/resolve/stages.py`, `doctrine/_compiler/resolve/receipts.py` | Reuse existing helpers and, where needed, expose small lookup helpers instead of re-parsing stage or receipt facts. | Prevents duplicate truth and keeps `E560` intact. |
| Example manifests | `examples/153_skill_flow_linear/**`, `examples/154_skill_flow_route_binding/**`, `examples/155_skill_flow_branch/**`, `examples/156_skill_flow_repeat/**` | Add positive and focused negative manifest-backed proof for each new owned feature group. | The example corpus is the primary language proof surface. |
| Example emit target | `pyproject.toml` | Add exactly one emit target for `example_154_skill_flow_route_binding`. | Proves the package-compile path still validates full flows and keeps routed receipts stable. |
| Shipped docs | `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md`, `examples/README.md`, `docs/README.md`, `docs/VERSIONING.md`, `CHANGELOG.md` | Replace the skeletal flow docs with the real slice, document `E561`, register examples `153` through `156`, and record the additive language move. | Public language truth must match the shipped compiler. |

## 6.2 Migration notes

- This is an additive language move. Older prompts that do not use the new
  `skill_flow` body keep compiling unchanged.
- `docs/SKILL_PACKAGE_AUTHORING.md` stays unchanged in this slice because no
  new emitted package contract field ships here.
- `docs/SKILL_GRAPH_LANGUAGE_SPEC.md` is still a proposal document, not shipped
  truth. Implementation must align the shipped docs and examples first.

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

- Do not add a second flow checker in emit code or the verifier. The compile
  sweep must own flow-local truth.
- Do not introduce a graph-wide resolved object yet. Sub-plan 3 should produce
  a flow-local resolved object that sub-plan 4 can compose later.
- Do not encode route binding by reading rendered JSON. Reuse
  `ResolvedReceipt.routes` directly from the compiler.

# 7) Depth-First Phased Implementation Plan (authoritative)

<!-- arch_skill:block:phase_plan:start -->
> Rule: systematic build, foundational first; split Section 7 into coherent
> self-contained units. `Work` explains the unit and is explanatory only.
> `Checklist (must all be done)` is the authoritative must-do list inside the
> phase. `Exit criteria (all required)` names the concrete done state the audit
> must validate. No fallbacks. No graph-wide scope creep.

## Phase 1 — Real `skill_flow` declarations and local node resolution

* Goal: move `skill_flow` from registry-only to a real flow-local declaration with stable raw and resolved model shapes.
* Work: establish the parser and resolver backbone before route binding or branch logic piles on top.
* Checklist (must all be done):
  - Extend the grammar for `start:`, `approve:`, `edge`, `kind:`, and `why:`.
  - Add raw and resolved flow-local model types and export them through `doctrine/model.py`.
  - Create `ResolveSkillFlowsMixin` and wire it through the compile context.
  - Resolve `start:` and basic edge refs against top-level `stage` and top-level nested `skill_flow` nodes.
  - Add local recursive expansion just far enough to reject missing nodes, direct self-reference, and cycle shape violations with `E561`.
  - Run the new flow-validation sweep from both `compile_agent` and `compile_skill_package`.
  - Add `examples/153_skill_flow_linear` with one positive case and focused `E561` negatives.
* Verification (required proof):
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/153_skill_flow_linear/cases.toml`
* Docs/comments (propagation; only if needed):
  - Add one brief code comment at the recursive expansion boundary if the cycle check is not obvious from the code.
* Exit criteria (all required):
  - A linear flow with `start:` and `approve:` compiles.
  - A missing node or local DAG violation fails with `E561`.
  - Existing examples `151` and `152` still rely on the same stage and receipt behavior.
* Rollback:
  - Remove the new sweep and raw flow-body parsing, returning `skill_flow` to registry-only behavior.

## Phase 2 — Receipt-route-bound edges

* Goal: make stage edges honor the receipt route truth from sub-plan 2.
* Work: connect resolved flow edges to resolved receipt route metadata without adding graph-wide policy flags.
* Checklist (must all be done):
  - Extend the grammar and model for `route: ReceiptRef.route_field.choice`.
  - Validate that the receipt ref resolves, the route field exists, the choice exists, and the choice target matches the edge target.
  - Enforce the strict default: when a source stage emits a routed receipt that has a choice to the chosen target, the edge must name the exact `route:` binding.
  - Keep `E560` untouched for receipt route target resolution and use `E561` for missing, ambiguous, or mismatched edge binding.
  - Add `examples/154_skill_flow_route_binding` and its `pyproject.toml` build target.
* Verification (required proof):
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/154_skill_flow_route_binding/cases.toml`
* Docs/comments (propagation; only if needed):
  - None beyond shipped docs in Phase 4.
* Exit criteria (all required):
  - A package compile path proves a correctly route-bound edge.
  - A route-mismatch or missing-required-route case fails with `E561`.
  - Receipt route lowering still uses the existing `E560` path for bad receipt route targets.
* Rollback:
  - Remove route-binding checks while leaving Phase 1 flow parsing intact.

## Phase 3 — Branches, repeats, variations, and changed-workflow facts

* Goal: finish the flow-local authoring surface without crossing into graph-wide sets or warnings.
* Work: add the remaining body items and keep every rule local, typed, and fail-loud.
* Checklist (must all be done):
  - Add enum-member `when:` validation on edges.
  - Enforce one local branch rule: if a source branches by enum, all branch edges from that source use the same enum family and cover each member exactly once.
  - Add `repeat Name: FlowRef` with `over:`, `order:`, and `why:`.
  - Resolve repeat targets to top-level `skill_flow` declarations and resolve local repeat names before stage refs.
  - Enforce repeat-name uniqueness and shadowing checks against top-level `stage`, top-level `skill_flow`, and other local repeats.
  - Limit `over:` to top-level `enum`, `table`, or `schema` refs in this slice.
  - Add `variation` and `unsafe` entries, with `safe_when:` using the same enum-member validation as `when:`.
  - Add `changed_workflow:` with `allow provisional_flow` and closed `require` items lowered to compiler-owned resolved facts only.
  - Add `examples/155_skill_flow_branch` and `156_skill_flow_repeat`.
* Verification (required proof):
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/155_skill_flow_branch/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/156_skill_flow_repeat/cases.toml`
* Docs/comments (propagation; only if needed):
  - Add one brief code comment where local repeat resolution intentionally stops before graph `sets:`.
* Exit criteria (all required):
  - Enum-branch coverage is enforced with compile errors, not silent acceptance.
  - Local repeat-node resolution works and shadowing fails with `E561`.
  - `variation`, `unsafe`, and `changed_workflow:` facts survive into the resolved flow object for later graph emit.
* Rollback:
  - Revert branch/repeat-specific items while keeping Phases 1 and 2 intact.

## Phase 4 — Shipped docs, diagnostics, and release truth

* Goal: make the shipped docs and proof corpus match the new language surface.
* Work: sync the public docs and release record after the code and examples are real.
* Checklist (must all be done):
  - Replace the skeletal `skill_flow` section in `docs/LANGUAGE_REFERENCE.md` with the real flow-core authoring surface.
  - Add `E561` to `docs/COMPILER_ERRORS.md` and explicitly preserve the shipped `E551`, `E552`, and `E560` meanings.
  - Register examples `153` through `156` in `examples/README.md`.
  - Update `docs/README.md` so the active skill-graph planning trail includes the new sub-plan doc and the shipped flow-core surface after implementation.
  - Record the additive public language move in `docs/VERSIONING.md` and `CHANGELOG.md`.
* Verification (required proof):
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/153_skill_flow_linear/cases.toml --manifest examples/154_skill_flow_route_binding/cases.toml --manifest examples/155_skill_flow_branch/cases.toml --manifest examples/156_skill_flow_repeat/cases.toml`
  - `make verify-diagnostics`
* Docs/comments (propagation; only if needed):
  - None beyond the named shipped docs.
* Exit criteria (all required):
  - Shipped docs, examples, and diagnostics tell the same story as the compiler.
  - The slice lands as an additive language move with release truth updated.
* Rollback:
  - Revert docs and example registration only if the compiler slice itself is rolled back.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

- Use the four new manifest-backed examples as the primary proof surface. Each
  example owns one coherent feature group.
- Run `make verify-diagnostics` because this slice adds a new public error code
  and sharpens an existing docs contract.
- Do not default to `make verify-examples` for this sub-plan. Broad corpus proof
  is intentionally outside this planning gate.
- If implementation unexpectedly changes package emit behavior outside the new
  route-binding example, escalate then. It is not part of the default plan.

# 9) Rollout / Ops / Telemetry

- This is compile-time authoring work only. There is no runtime telemetry or
  operational migration.
- Compatibility posture: additive, non-breaking public language move.
- Downstream repos do not need to act unless they choose to author the new
  `skill_flow` surface. Existing prompts keep compiling unchanged.
- The only durable rollout artifact is the updated language version guidance
  and changelog entry.

# 10) Decision Log (append-only)

- 2026-04-26 Intent-derived: sub-plan 3 owns flow-local `skill_flow`
  resolution only. Graph `sets:`, root closure, graph policies, graph emit, and
  graph verification stay in sub-plan 4. Warnings and checked skill mentions
  stay in sub-plan 5.
- 2026-04-26 Intent-derived: preserve shipped `E551`, `E552`, and `E560`
  meanings. Use `E561` as the new primary skill-flow compile family, but
  keep parser-owned `skill_flow` block-shape failures on parse `E199`.
- 2026-04-26 Intent-derived: do not add `otherwise:` in this slice. Branches
  must cover enum members explicitly so the authoring form stays typed and
  stable.
- 2026-04-26 Intent-derived: `when:` and `safe_when:` accept enum-member refs
  only in sub-plan 3. General boolean graph-input conditions wait for a later
  graph-aware slice.
- 2026-04-26 Intent-derived: `repeat over:` validates only local top-level
  `enum`, `table`, or `schema` refs in this slice. Graph `sets:` wait for
  sub-plan 4.
- 2026-04-26 Intent-derived: `changed_workflow:` lowers to compiler-owned
  resolved facts only. No public graph contract or query JSON ships before
  sub-plan 4.
