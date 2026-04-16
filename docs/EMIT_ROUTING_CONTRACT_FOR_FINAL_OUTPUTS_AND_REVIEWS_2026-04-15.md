---
title: "Doctrine - Emit Canonical Routing Contract For Final Outputs And Reviews - Architecture Plan"
date: 2026-04-15
status: active
fallback_policy: forbidden
owners: []
reviewers: []
doc_type: architectural_change
related:
  - docs/WORKFLOW_LAW.md
  - docs/REVIEW_SPEC.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/EMIT_GUIDE.md
  - docs/VERSIONING.md
  - doctrine/emit_docs.py
---

# TL;DR

## Outcome

Doctrine emits one canonical machine-readable top-level `route` block in
`final_output.contract.json` for every emitted final-response contract. A
harness can read whether the turn routes, which named agent it routes to, and
any live selected branch detail without asking the model to copy that route
into ad hoc payload fields. On unrouted turns, the same block says
`exists: false`.

## Problem

Doctrine already owns route truth for workflow law, `handoff_routing`,
`route_only`, `route_from`, and review. But the emitted runtime contract
standardizes final-output shape and review control data, not ordinary routing,
so harnesses still fall back to fields like `next_owner`.

## Approach

Extend the existing emitted final-output contract so it serializes
compiler-resolved routing truth from the same route semantics that power
`route.*` reads. Use one routing model for ordinary routed finals and
review-driven routed finals.

## Plan

Lock one shared compile and emit route contract, prove it on ordinary and
review final-response examples, then update the public docs and release
surfaces that define this runtime contract.

## Non-negotiables

- Doctrine stays the routing source of truth.
- There is no second routing VM and no prose scraping.
- There is no model-copied owner string for canonical routing.
- Review and non-review turns share one runtime routing model.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-15
recommended_flow: research -> deep dive -> phase plan -> consistency pass -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine emits `final_output.contract.json`, it will also emit one
canonical top-level `route` block in that file. That block will expose routed
named-agent truth when a route is live, and it will say `exists: false` when
the turn does not route. The same model will work for workflow-law turns,
`handoff_routing`, `route_only`, `route_from`, and routed reviews.

## 0.2 In scope

- Add a canonical emitted top-level `route` contract for final-response
  contracts, with routed truth when a route is live and `exists: false` when
  it is not.
- Use Doctrine-resolved named agent identity, not a copied free-form owner
  string.
- Cover ordinary routed finals, `route_only` control turns, and review-driven
  routed finals with one runtime-facing model.
- Extend the current `final_output.contract.json` path instead of inventing a
  second emitted contract surface.
- Update the emit code, tests, manifest-backed examples, and shipped docs that
  define or explain this runtime contract.
- Do the internal convergence work needed to keep routing truth in one
  canonical emit path and remove any new reason for harness-local routing
  bridges.
- Keep `final_output.contract.json` as the one public emitted file. Add the
  routing truth there instead of creating a sidecar or shim.
- Keep the adjacent surfaces in sync:
  `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/EMIT_GUIDE.md`,
  `docs/VERSIONING.md`, route-semantic examples, review examples, and emit
  contract tests.

## 0.3 Out of scope

- A new GUI or diagram feature.
- Richer prose rendering beyond small doc text needed to explain the contract.
- A harness-specific private extension or a Rally-only bridge.
- A second authoring model for routing.
- Runtime shims that reconstruct route truth outside Doctrine when Doctrine
  already resolved it.

## 0.4 Definition of done (acceptance evidence)

- `final_output.contract.json` exposes one canonical top-level `route` block
  for every emitted final-response contract. That block says `exists: false`
  when the turn does not route.
- The emitted routing block carries enough truth for a harness to decide
  whether to route, which named agent to route to, and any live selected
  branch detail Doctrine already knows.
- The same emitted model works for workflow-law routing, `handoff_routing`,
  `route_only`, `route_from`, and routed review outcomes.
- Existing final-output and review contract tests stay green, and new coverage
  proves the routing block on both ordinary and review-driven finals.
- The manifest-backed proof set covers ordinary workflow-law, handoff,
  `route_from`, `route_only`, and routed review final-response contracts end
  to end.
- Shipped docs explain the runtime contract and stay aligned with the emitted
  surface.
- Relevant verify commands from `AGENTS.md` run cleanly for the touched
  surfaces, or any gap is called out plainly.

## 0.5 Key invariants (fix immediately if violated)

- No second routing source of truth.
- No harness-local route reconstruction when Doctrine already resolved the
  route.
- No model-written `next_owner` style string as the canonical runtime route
  source.
- No parallel routing model for review versus non-review.
- No fallback or shim path that hides missing route truth.
- Fail loud when route truth is not live or not uniquely selectable.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Let a harness consume canonical route truth directly from Doctrine.
2. Keep one routing model across ordinary finals and reviews.
3. Preserve the current emitted contract path and keep the new surface easy to
   adopt.
4. Keep docs, examples, and proof aligned with shipped behavior.

## 1.2 Constraints

- The source of truth for routing already lives in compiler-resolved route
  semantics, not in output payload prose.
- `final_output.contract.json` already ships as the emitted runtime contract
  for final outputs and reviews.
- Doctrine is public and versioned, so any contract change must be explicit
  and documented.
- The plan must stay small and typed. It should not add a second control
  plane.

## 1.3 Architectural principles (rules we will enforce)

- Serialize routing from compiled route semantics, not from rendered markdown
  or model text.
- Reuse the existing final-output contract surface instead of adding a sibling
  runtime file.
- Keep review routing and non-review routing on the same emitted model when
  the runtime question is the same.
- Prefer additive convergence on the canonical emit path over host-specific
  adapters.

## 1.4 Known tradeoffs (explicit)

- A richer routing block makes the emitted contract more capable, but it also
  raises the bar for docs and compatibility clarity.
- Keeping one shared runtime model may require small refactors across emit and
  review serialization instead of a narrow local patch.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- Doctrine compiles named-agent routing through workflow law,
  `handoff_routing`, `route_only`, `route_from`, and review.
- Emitted outputs may read shared `route.*` truth such as
  `route.next_owner.key`, `route.label`, and `route.choice.*`.
- `emit_docs` already writes `final_output.contract.json` with final-output
  metadata and review control metadata.

## 2.2 What’s broken / missing (concrete)

- The emitted runtime contract does not yet expose one canonical routing block
  for ordinary final responses.
- Harnesses can still end up depending on ad hoc payload fields like
  `next_owner` even when Doctrine already resolved the route.
- Review is closer to runtime-ready control metadata than ordinary routed
  finals, which leaves one split model where there should be one.

## 2.3 Constraints implied by the problem

- The fix must come from Doctrine's own route semantics.
- It must work across routed finals with and without review.
- It must stay machine-readable and stable enough for a harness to consume
  directly.

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- None needed. The main source of truth for this change is Doctrine's own
  shipped emit and route-semantics surface.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/_compiler/resolved_types.py` - `RouteSemanticBranch`,
    `RouteSemanticContext`, and `RouteChoiceMember` already carry the routed
    target identity, route label, review verdict tie-in, and `route_from`
    branch detail Doctrine resolves today.
  - `doctrine/_compiler/resolve/route_semantics.py` - resolves
    `route.exists`, `route.next_owner.*`, `route.label`, `route.summary`, and
    `route.choice.*` from compiler-owned route truth and fails loud on
    ambiguity.
  - `doctrine/_compiler/compile/final_output.py` - final-output compile already
    receives `route_output_contexts` and validates route-bound output reads,
    but `CompiledFinalOutputSpec` does not yet carry machine-readable route
    metadata for emit.
  - `doctrine/_compiler/compile/review_contract.py` - review compile already
    emits carrier fields, split final-response metadata, `control_ready`, and
    coarse per-outcome `route_behavior`, but not canonical routed target
    identity.
  - `doctrine/emit_docs.py` - `_final_output_contract_payload`,
    `_serialize_final_output_contract`, and `_serialize_review_contract` define
    the current public `final_output.contract.json` payload. It serializes
    `final_output` and `review`, but no shared routing block yet.
  - `tests/test_emit_docs.py` - locks the current emitted contract shape,
    including `contract_version == 1`, the exact `final_output` payload, and
    the current review-control fields.
  - `tests/test_route_output_semantics.py` and `tests/test_final_output.py` -
    prove that ordinary outputs, review comments, and final outputs can already
    consume shared `route.*` truth across workflow law, review, and
    `route_from`.
- Canonical path / owner to reuse:
  - `doctrine/emit_docs.py` - the one public machine-readable emit boundary for
    `final_output.contract.json`. This should stay the serializer for any new
    routing contract data.
  - `doctrine/_compiler/resolved_types.py` plus
    `doctrine/_compiler/resolve/route_semantics.py` - the canonical resolved
    route truth to serialize. Emit should reuse this truth instead of scraping
    rendered output or trusting payload strings.
- Adjacent surfaces tied to the same contract family:
  - `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`,
    `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/EMIT_GUIDE.md`,
    `docs/VERSIONING.md` - shipped route, review, emit, and compatibility docs
    that will drift if the emitted routing contract changes without doc
    updates.
  - `tests/test_emit_docs.py` and `doctrine/_diagnostic_smoke/emit_checks.py` -
    emitted contract proof for `final_output.contract.json`.
  - `tests/test_route_output_semantics.py`, `tests/test_final_output.py`,
    `doctrine/_diagnostic_smoke/flow_route_checks.py`, and
    `doctrine/_diagnostic_smoke/review_checks.py` - existing proof that route
    truth is live on ordinary outputs, review outputs, and final outputs.
  - `examples/87_workflow_route_output_binding` through
    `examples/94_route_choice_guard_narrowing` - the manifest-backed route
    semantics ladder for ordinary workflow law, review, `route_only`,
    `handoff_routing`, and `route_from`.
  - `examples/104_review_final_output_output_schema_blocked_control_ready`
    through `examples/106_review_split_final_output_output_schema_partial` -
    the manifest-backed review final-response metadata ladder that already
    proves current emitted review control metadata.
  - `examples/111_inherited_output_route_semantics` - inherited output route
    readback that should stay aligned with the same routing contract story.
- Compatibility posture (separate from `fallback_policy`):
  - Preserve the existing contract via an additive extension on
    `final_output.contract.json` - `docs/VERSIONING.md` says emitted
    `final_output.contract.json` is a public surface, and additive public
    additions are non-breaking. Repo truth supports preserving existing
    `final_output` and `review` fields while adding canonical routing metadata,
    not a new file or cutover bridge.
- Existing patterns to reuse:
  - `doctrine/emit_docs.py::_serialize_final_output_contract` and
    `_serialize_review_contract` - existing machine-readable companion
    serialization pattern under one emitted contract payload.
  - `CompiledReviewSpec` in `doctrine/_compiler/types.py` - existing compiled
    control metadata carrier that emit can serialize after compile-time
    normalization.
- Prompt surfaces / agent contract to reuse:
  - `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`, and
    `docs/LANGUAGE_REFERENCE.md` - shipped author-facing contract that already
    promises shared `route.*` truth on outputs and reviews. The emitted runtime
    contract should mirror that same truth, not invent a separate model.
- Native model or agent capabilities to lean on:
  - Not applicable. This is compiler and emit work, not prompt repair or model
    capability recovery.
- Existing grounding / tool / file exposure:
  - The compile and emit pipeline already has the compiled agent, final-output,
    review, and route-semantic data in memory during `emit_docs`. No host-side
    bridge, parser, or runtime callback is needed to recover it.
- Duplicate or drifting paths relevant to this change:
  - Payload fields like `next_owner` in route and review outputs are
    human-facing output content, not Doctrine's generic machine-readable
    routing contract. Treating them as the runtime route source recreates a
    second control protocol.
  - Current emitted review metadata exposes only coarse `route_behavior`
    (`always`, `never`, `conditional`). That is useful, but it is not the
    canonical routed target identity the user is asking for.
- Capability-first opportunities before new tooling:
  - Extend the existing emit serializer from compiler-owned route semantics.
    Do not add a harness bridge, second emitted file, parser, or wrapper.
- Behavior-preservation signals already available:
  - `tests/test_emit_docs.py` - current `final_output.contract.json` wire shape
    and review-control metadata.
  - `tests/test_route_output_semantics.py` and `tests/test_final_output.py` -
    current route truth and final-output route reads.
  - `make verify-examples` - manifest-backed proof across the route and review
    example ladder.

## 3.3 Decision gaps that must be resolved before implementation

- None. Deep-dive resolves the architecture as one shared compiled `route`
  contract on `CompiledAgent`, serialized as an additive top-level `route`
  block in `final_output.contract.json`. The contract stays on version `1`,
  preserves the existing `final_output` and `review` keys, and uses one
  contract-response selection rule for ordinary finals and review finals.
<!-- arch_skill:block:research_grounding:end -->

# 4) Current Architecture (as-is)

<!-- arch_skill:block:current_architecture:start -->
## 4.1 On-disk structure

- `doctrine/_compiler/resolved_types.py` already holds the routed source of
  truth in `RouteSemanticBranch`, `RouteSemanticContext`, and
  `RouteChoiceMember`.
- `doctrine/_compiler/validate/agents.py` resolves exactly one live
  route-bearing control surface per agent, then fans that same
  `RouteSemanticContext` across every emitted output key through
  `_route_output_contexts_for_agent`.
- `doctrine/_compiler/compile/final_output.py` receives those route contexts
  and uses them to validate route reads and render final-output content.
- `doctrine/_compiler/compile/review_contract.py` compiles review control
  metadata and coarse per-outcome `route_behavior`.
- `doctrine/_compiler/types.py` stores compiled `final_output` and `review`
  data on `CompiledAgent`, but there is no compiled route contract field yet.
- `doctrine/emit_docs.py` is the one public serializer for
  `final_output.contract.json`. It emits `contract_version`, `agent`,
  `final_output`, and optional `review`, but no top-level routed target
  packet.

## 4.2 Control paths (runtime)

1. `workflow law`, `handoff_routing`, `route_only`, `route_from`, or review
   resolve a `RouteSemanticContext` before emit time.
2. `ValidateAgentsMixin._route_output_contexts_for_agent` copies that same
   context onto every emitted output key for the concrete turn.
3. `compile/final_output.py` uses the selected output key plus route context
   to validate `route.*` reads and final-output guards.
4. `compile/review_contract.py` separately computes review carrier fields,
   split final-response metadata, and `route_behavior`.
5. `emit_docs.py` emits `final_output.contract.json` from the compiled agent.
   Route truth stops at the compile boundary, so the runtime contract cannot
   read the resolved target directly.

## 4.3 Object model + key abstractions

- `RouteSemanticBranch` already carries target identity
  (`target_module_parts`, `target_name`, `target_title`), human route label,
  optional `review_verdict`, and optional `choice_members` for `route_from`.
- `RouteSemanticContext` already carries the live branch set,
  `has_unrouted_branch`, `route_required`, and `unrouted_review_verdicts`.
- `CompiledFinalOutputSpec` carries final-output contract shape only. It has
  no machine-readable route metadata.
- `CompiledReviewSpec` carries `comment_output`, `carrier_fields`,
  `final_response`, and per-outcome `route_behavior`, but not canonical routed
  target identity.
- `CompiledAgent` has `final_output` and `review` only. There is no shared
  compiled place to normalize one route contract for the emitted file.

## 4.4 Observability + failure behavior today

- Route-bound reads already fail loud when route truth is missing or
  ambiguous. `doctrine/_compiler/resolve/route_semantics.py` and
  `doctrine/_compiler/validate/route_semantics_reads.py` define that behavior
  and already expose shared text like `route.summary`.
- `tests/test_route_output_semantics.py` and `tests/test_final_output.py`
  prove the live route semantics on outputs and reviews today.
- `tests/test_emit_docs.py` locks the current wire shape of
  `final_output.contract.json`, including `FINAL_OUTPUT_CONTRACT_VERSION = 1`.
- `doctrine/_diagnostic_smoke/emit_checks.py` only checks that the contract
  file exists and points at the generated schema. It does not yet prove any
  route block shape.
- The route-contract gap is silent. A harness only sees it later, when it has
  to fall back to custom payload fields like `next_owner`.

## 4.5 UI surfaces (ASCII mockups, if UI work)

- No UI work.
<!-- arch_skill:block:current_architecture:end -->

# 5) Target Architecture (to-be)

<!-- arch_skill:block:target_architecture:start -->
## 5.1 On-disk structure (future)

- `final_output.contract.json` stays the one public emitted runtime contract
  file for final responses. There is no sidecar routing file.
- `doctrine/_compiler/types.py` gains a small compiled route model under
  `CompiledAgent`, not under `CompiledFinalOutputSpec` alone, so review-only
  final-response contracts can emit the same route truth.
- `doctrine/_compiler/compile/agent.py` becomes the canonical owner for
  selecting the contract-response output key and normalizing the shared route
  contract once from `RouteSemanticContext`.
- `doctrine/emit_docs.py` serializes that compiled route contract as one
  additive top-level `route` block beside the existing `final_output` and
  `review` keys.
- The current branch title and summary text stays on one canonical formatter
  path. If compile needs the same text, it must reuse the existing
  route-semantics formatter instead of copying strings.

## 5.2 Control paths (future)

1. Doctrine resolves one live `RouteSemanticContext` from the single route
   source already enforced by `ValidateAgentsMixin`.
2. `CompileAgentMixin._compile_agent_decl` chooses the one output key that
   owns `final_output.contract.json`:
   - explicit `final_output` present: use `CompiledFinalOutputSpec.output_key`
   - review with carrier final response or no explicit `final_output`: use
     `CompiledReviewSpec.comment_output.output_key`
   - review with split final response: use
     `CompiledReviewSpec.final_response.output_key`
   - no `final_output` and no review: no contract file is emitted, same as
     today
3. `compile/agent.py` normalizes one compiled route contract for that output
   key from the matching `RouteSemanticContext`.
4. `emit_docs.py` always writes a top-level `route` block whenever
   `final_output.contract.json` is emitted. That block says `exists: false`
   when no routed branch is live for the selected response.
5. Harnesses read the emitted `route` block directly. They do not need a
   copied payload field or a review-only bridge.

## 5.3 Object model + abstractions (future)

- Add one compiled route contract on `CompiledAgent`. Keep the current
  `final_output` and `review` payloads unchanged.
- The emitted top-level `route` block should have this stable shape:
  - `exists: bool`
  - `behavior: "always" | "never" | "conditional"`
  - `has_unrouted_branch: bool`
  - `unrouted_review_verdicts: list[str]`
  - `branches: list[branch]`
- Each emitted `branch` should carry:
  - `target.key`: the canonical dotted agent identity already implied by
    Doctrine route resolution
  - `target.module_parts`, `target.name`, `target.title`
  - `label`
  - `summary`: from the same formatter that powers `route.summary`
  - `review_verdict` when the branch comes from review routing
  - `choice_members` when the branch is narrowed by `route_from`, with
    `enum_module_parts`, `enum_name`, `member_key`, `member_title`, and
    `member_wire`
- `behavior` reuses the existing runtime words
  `always | never | conditional` so review and non-review routing feel like
  one model.
- `review.outcomes.route_behavior` stays for backward-compatible review detail.
  The new top-level `route` block becomes the canonical routed-target contract
  for the whole file.

## 5.4 Invariants and boundaries

- `RouteSemanticContext` stays the single routed source of truth. Compile
  normalizes from it once. Emit only serializes.
- Preserve the public file path and `contract_version: 1`. This is an additive
  contract extension, not a cutover.
- Do not add a second runtime route packet under `final_output`, under
  `review`, or in a new file.
- Do not treat payload fields like `next_owner` as canonical route truth. They
  remain user content only.
- Review-specific gate and carrier metadata stays review-owned. Routed review
  finals still use the same top-level `route` contract as ordinary routed
  finals.
- If implementation finds repo-backed evidence that version `1` cannot carry
  this addition safely, reopen the plan instead of silently bumping or
  cutting over.

## 5.5 UI surfaces (ASCII mockups, if UI work)

- No UI work.
<!-- arch_skill:block:target_architecture:end -->

# 6) Call-Site Audit (exhaustive change inventory)

<!-- arch_skill:block:call_site_audit:start -->
## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Compiled contract types | `doctrine/_compiler/types.py` | `CompiledAgent`, new compiled route spec types | `CompiledAgent` stores `final_output` and `review` only | Add one shared compiled `route` spec plus branch, target, and choice-member specs on `CompiledAgent` | Review-only final-response contracts also need the same top-level route truth | `CompiledAgent.route` carries the emitted route contract model | `tests/test_emit_docs.py`, `tests/test_final_output.py` |
| Route summary formatting | `doctrine/_compiler/validate/route_semantics_reads.py` | `_route_semantic_branch_title`, `_route_semantic_branch_summary` | Route summary text exists only on the read-validation mixin path | Reuse this formatter from compile-time route normalization, or lift it to a small shared helper in the same canonical path | Prevent drift between `route.summary` and emitted branch summaries | One shared formatter feeds both route reads and emitted `route.branches[].summary` | `tests/test_route_output_semantics.py`, `tests/test_emit_docs.py` |
| Agent compile owner path | `doctrine/_compiler/compile/agent.py` | `_compile_agent_decl` and new local helper(s) | The compile path computes route contexts, final output, and review separately, but never normalizes a runtime route contract | Select the contract-response output key once, derive `behavior`, and normalize one compiled route contract from `RouteSemanticContext` | Keep canonical routing truth in one compile path and avoid parallel ordinary vs review logic | One shared compile path for workflow, `handoff_routing`, `route_only`, `route_from`, and review finals | `tests/test_emit_docs.py`, `tests/test_final_output.py` |
| Final-output emit serializer | `doctrine/emit_docs.py` | `FINAL_OUTPUT_CONTRACT_VERSION`, `_final_output_contract_payload`, new route serializer helper(s) | The emitted contract contains `contract_version`, `agent`, `final_output`, and optional `review` only | Serialize the new top-level `route` block, keep existing keys, and preserve version `1` | Harnesses need one canonical runtime routing payload in the shipped contract | `final_output.contract.json` gains top-level `route` with stable fields | `tests/test_emit_docs.py`, `doctrine/_diagnostic_smoke/emit_checks.py` |
| Emit smoke proof | `doctrine/_diagnostic_smoke/emit_checks.py` | emitted-contract smoke checks | Smoke checks only confirm contract file presence and schema relpath | Add routed and unrouted contract assertions at the emitted JSON level | Catch wire drift earlier than full corpus review | Smoke expectations include top-level `route` | diagnostic smoke coverage, `make verify-diagnostics`, `make verify-examples` |
| Ordinary routed examples | `examples/87_workflow_route_output_binding/**`, `examples/91_handoff_routing_route_output_binding/**`, `examples/93_handoff_routing_route_from_final_output/**` | manifest-backed example refs and expected artifacts | These examples prove workflow-law route reads, handoff route reads, and `route_from` reads in final output, but not the emitted runtime contract | Update proofs so emitted `final_output.contract.json` shows the new top-level `route` block for workflow-law and handoff routed finals plus `route_from` branch detail | Keep the ordinary routing story manifest-backed and end to end across the promised route families | Example refs document canonical ordinary routed contract output | `make verify-examples` |
| Dedicated `route_only` proof | `examples/116_route_only_final_output_contract/**` | new manifest-backed example directory | There is no dedicated example that proves `route_only` through the emitted final-output contract | Add one new example instead of overloading `examples/89_route_only_shared_route_semantics` | Keep one new idea per example and prove the missing acceptance leg | New example proves top-level `route` on a `route_only` final-response contract | `make verify-examples` |
| Review routed examples | `examples/104_review_final_output_output_schema_blocked_control_ready/**`, `examples/105_review_split_final_output_output_schema_control_ready/**`, `examples/106_review_split_final_output_output_schema_partial/**` | manifest-backed review refs and expected artifacts | These examples prove review control metadata, but not canonical routed target identity in the final-output contract | Extend review proofs so carrier, split, and conditional review finals emit the same top-level `route` model | Review and non-review need one runtime routing story | Example refs show route truth for review finals without replacing `review.outcomes.route_behavior` | `make verify-examples` |
| Emit contract tests | `tests/test_emit_docs.py` | final-output contract assertions | Tests lock current file shape and review payload only | Add assertions for unrouted `route.exists == false`, ordinary routed branch payloads, and review-routed branch payloads while preserving current `final_output` and `review` assertions | This is the canonical wire-contract test file | Contract tests prove version `1` additive extension | `uv run --locked python -m unittest tests.test_emit_docs` |
| Public docs and release notes | `docs/EMIT_GUIDE.md`, `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/AUTHORING_PATTERNS.md`, `docs/VERSIONING.md`, `docs/README.md`, `examples/README.md`, `CHANGELOG.md` | emit, route, review, versioning, and docs-index text | Public docs explain route reads and review control, but not the new canonical emitted route contract | Update all live docs that define, teach, or version this contract family | Avoid stale truth and meet public-surface release rules | Docs explain top-level `route`, additive compatibility, and example coverage | doc review plus `make verify-examples`; run `make verify-package` when the public release surface changes |

## 6.2 Migration notes

* Canonical owner path / shared code path:
  `doctrine/_compiler/compile/agent.py` normalizes one compiled `route`
  contract on `CompiledAgent`. `doctrine/emit_docs.py` serializes it into the
  existing `final_output.contract.json`. `RouteSemanticContext` remains the
  routed source of truth.
* Deprecated APIs (if any):
  None. Keep current `review.outcomes.route_behavior` and any user-authored
  payload fields. They are no longer the canonical runtime route source.
* Delete list (what must be removed; include superseded shims/parallel paths if any):
  No second emitted route file. No nested duplicate route packet under
  `final_output` or `review`. No new harness bridge or copied `next_owner`
  convention added to Doctrine docs as canonical behavior.
* Adjacent surfaces tied to the same contract family:
  `tests/test_emit_docs.py`, `doctrine/_diagnostic_smoke/emit_checks.py`,
  route-semantic examples `87`, `91`, `93`, review examples `104` through
  `106`, new `route_only` proof example, `docs/EMIT_GUIDE.md`,
  `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/AUTHORING_PATTERNS.md`, `docs/VERSIONING.md`, `docs/README.md`,
  `examples/README.md`, and `CHANGELOG.md`. Monitor
  `examples/111_inherited_output_route_semantics` for drift, but only update
  it if implementation changes inherited final-output contract emission.
* Compatibility posture / cutover plan:
  Add the top-level `route` block to the existing
  `final_output.contract.json`, preserve `contract_version: 1`, preserve the
  existing `final_output` and `review` keys, and set `route.exists: false`
  for unrouted emitted contracts. This is additive, not a bridge or a
  cutover.
* Capability-replacing harnesses to delete or justify:
  None in repo. The plan forbids introducing a Doctrine-side wrapper, parser,
  or bridge that reconstructs route truth from prose or copied strings.
* Live docs/comments/instructions to update or delete:
  Update the public docs and examples listed above. If any example or doc
  teaches copied owner strings as the runtime contract, rewrite it.
* Behavior-preservation signals for refactors:
  `tests/test_emit_docs.py`, `tests/test_route_output_semantics.py`,
  `tests/test_final_output.py`, `make verify-diagnostics`,
  `make verify-examples`, and `make verify-package` because this is a public
  emitted surface with doc and release-note updates.

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Final-response contracts | `doctrine/_compiler/compile/agent.py`, `doctrine/emit_docs.py` | One compiled top-level `route` contract for both ordinary and review finals | Prevents a split runtime model between review and non-review routing | include |
| Branch summary text | `doctrine/_compiler/validate/route_semantics_reads.py` | One shared formatter for route branch titles and summaries | Prevents emitted `summary` text from drifting away from `route.summary` | include |
| Ordinary route proof ladder | `examples/87_workflow_route_output_binding`, `examples/91_handoff_routing_route_output_binding`, `examples/93_handoff_routing_route_from_final_output`, `examples/111_inherited_output_route_semantics` | Keep ordinary route-contract proof on the existing route-semantics ladder | Prevents docs and manifests from proving route reads but not the emitted contract | include for `87`, `91`, and `93`; defer `111` unless implementation touches inherited contract output |
| `route_only` proof | `examples/89_route_only_shared_route_semantics`, new `examples/116_route_only_final_output_contract` | Use a dedicated final-output contract example instead of overloading the shared route-semantics example | Prevents one example from trying to prove two new ideas at once | include |
| Review contract family | `examples/104_*` through `examples/106_*`, `tests/test_emit_docs.py` | Keep review control metadata and routed target metadata in one file without duplicate route packets | Prevents review routing from drifting into a special bridge model | include |
| Public authoring docs | `docs/EMIT_GUIDE.md`, `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/AUTHORING_PATTERNS.md`, `docs/VERSIONING.md`, `docs/README.md`, `examples/README.md` | Teach the emitted top-level `route` block as the canonical runtime contract | Prevents stale docs from sending harness authors back to copied owner strings | include |
<!-- arch_skill:block:call_site_audit:end -->

# 7) Depth-First Phased Implementation Plan (authoritative)

<!-- arch_skill:block:phase_plan:start -->
> Rule: systematic build, foundational first; split Section 7 into the best
> sequence of coherent self-contained units, optimizing for phases that are
> fully understood, credibly testable, compliance-complete, and safe to build
> on later. If two decompositions are both valid, bias toward more phases than
> fewer. `Work` explains the unit and is explanatory only for modern docs.
> `Checklist (must all be done)` is the authoritative must-do list inside the
> phase. `Exit criteria (all required)` names the exhaustive concrete done
> conditions the audit must validate. Resolve adjacent-surface dispositions and
> compatibility posture before writing the checklist. Before a phase is valid,
> run an obligation sweep and move every required promise from architecture,
> call-site audit, migration notes, delete lists, verification commitments,
> docs/comments propagation, approved bridges, and required helper
> follow-through into `Checklist` or `Exit criteria`. Refactors,
> consolidations, and shared-path extractions must preserve existing behavior
> with credible evidence proportional to the risk. For agent-backed systems,
> prefer prompt, grounding, and native-capability changes before new harnesses
> or scripts. No fallbacks/runtime shims - the system must work correctly or
> fail loudly (delete superseded paths). If a bridge is explicitly approved,
> timebox it and include removal work; otherwise plan either clean cutover or
> preservation work directly. Prefer programmatic checks per phase; defer
> manual/UI verification to finalization. Avoid negative-value tests and
> heuristic gates (deletion checks, visual constants, doc-driven gates, keyword
> or absence gates, repo-shape policing). Also: document new patterns/gotchas
> in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Shared Compile And Emit Route Contract

* Goal:
  Put all routed final-response truth on one compile-to-emit path that works
  for ordinary finals and review finals.
* Work:
  Build the shared contract model first, because later proof and docs work
  should only validate one already-chosen wire contract, not invent it.
* Checklist (must all be done):
  - Add compiled route contract types in `doctrine/_compiler/types.py` so
    `CompiledAgent` can carry one shared `route` contract with branch, target,
    and choice-member detail.
  - Add a compile helper in `doctrine/_compiler/compile/agent.py` that picks
    the one contract-response output key for the emitted
    `final_output.contract.json` file across explicit `final_output`, review
    carrier mode, and review split mode.
  - Normalize the emitted route contract once from `RouteSemanticContext`,
    including `exists`, `behavior`, `has_unrouted_branch`,
    `unrouted_review_verdicts`, branch target identity, labels, review verdict
    ties, and `route_from` choice members.
  - Reuse the existing route branch title and summary formatter so emitted
    branch summaries and `route.summary` cannot drift apart.
  - Update `doctrine/emit_docs.py` to serialize one additive top-level
    `route` block in `final_output.contract.json` while preserving
    `contract_version: 1` and the current `final_output` and `review` keys.
  - Emit `route.exists: false` and `behavior: "never"` for unrouted emitted
    contracts instead of omitting the route block.
  - Do not add a second emitted file, a nested duplicate route packet, or any
    bridge that treats copied payload fields as canonical route truth.
  - Add one brief code comment at the contract-response selection helper that
    explains why ordinary finals, review carrier finals, and review split
    finals converge on the same top-level route contract.
  - Extend direct unit coverage in `tests/test_emit_docs.py` for the new
    top-level `route` block on at least one unrouted contract and one routed
    contract while preserving current `final_output` and `review` assertions.
* Verification (required proof):
  - Run `uv run --locked python -m unittest tests.test_emit_docs
    tests.test_final_output tests.test_route_output_semantics`.
* Docs/comments (propagation; only if needed):
  - Keep the new boundary comment local to the contract-response selection
    helper. Do not spread narration through unrelated compile code.
* Exit criteria (all required):
  - `CompiledAgent` carries one shared route contract and no second route
    source is introduced in compile or emit.
  - `final_output.contract.json` emits a top-level `route` block whenever the
    file exists, and the file stays on contract version `1`.
  - Existing `final_output` and `review` payload keys remain present and keep
    their current ownership.
  - Emitted branch summaries and `route.summary` come from one shared
    formatter path.
  - The targeted unit tests above pass.
* Rollback:
  - Revert the shared route contract types, compile helper, serializer change,
    boundary comment, and direct unit tests together so the old contract path
    stays internally consistent.

## Phase 2 — Ordinary Routed Final-Response Proof Ladder

* Goal:
  Prove the new route contract on ordinary workflow, handoff, `route_from`,
  and `route_only` final responses with manifest-backed examples and emit
  smoke.
* Work:
  Extend the ordinary route proof ladder only after the core wire contract is
  stable, so example churn follows the chosen serializer instead of shaping it.
* Checklist (must all be done):
  - Update `doctrine/_diagnostic_smoke/emit_checks.py` so emitted-contract
    smoke checks assert the top-level `route` block on both routed and
    unrouted final-output contracts.
  - Update `examples/87_workflow_route_output_binding` so its manifest and
    reference artifacts prove the routed workflow-law final-output contract.
  - Update `examples/91_handoff_routing_route_output_binding` so its manifest
    and reference artifacts prove the routed ordinary final-output contract.
  - Update `examples/93_handoff_routing_route_from_final_output` so its
    manifest and reference artifacts prove `route_from` branch detail in the
    emitted contract, including choice members.
  - Add a new manifest-backed example at
    `examples/116_route_only_final_output_contract` that proves the emitted
    route contract for a `route_only` turn.
  - Keep `examples/89_route_only_shared_route_semantics` focused on shared
    route semantics instead of turning it into the new final-output contract
    proof.
  - Keep `examples/111_inherited_output_route_semantics` unchanged unless
    implementation changes inherited final-output contract emission. If that
    inheritance path changes, update its manifest and reference artifacts in
    this phase too.
* Verification (required proof):
  - Run `make verify-diagnostics`.
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/87_workflow_route_output_binding/cases.toml`.
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/91_handoff_routing_route_output_binding/cases.toml`.
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/93_handoff_routing_route_from_final_output/cases.toml`.
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/116_route_only_final_output_contract/cases.toml`.
* Docs/comments (propagation; only if needed):
  - Keep example names and titles clear about which runtime contract behavior
    each proof owns.
* Exit criteria (all required):
  - Workflow-law routed finals, handoff routed finals, `route_from`, and
    `route_only` each have manifest-backed proof for the emitted top-level
    `route` block.
  - Emit smoke now fails if routed or unrouted final-output contracts drift
    away from the planned route shape.
  - The ordinary `route_only` semantics example remains single-purpose and is
    not overloaded with the new contract proof.
  - `examples/111_inherited_output_route_semantics` is either unchanged
    because inherited contract emission did not move, or it is updated in the
    same phase because that path did move.
* Rollback:
  - Revert the ordinary example refs, the new `route_only` example, and the
    emit-smoke assertions together so the proof surface returns to its prior
    consistent state.

## Phase 3 — Review Final-Response Route Proof Ladder

* Goal:
  Prove that review carrier finals, split finals, and conditional review
  branches emit the same top-level route contract without losing existing
  review control metadata.
* Work:
  Keep review proof separate from ordinary proof so audit can see clearly that
  the shared route model holds across both control families.
* Checklist (must all be done):
  - Extend `tests/test_emit_docs.py` review assertions so review-emitted
    contracts prove the top-level `route` block while preserving existing
    `review.outcomes.route_behavior` assertions.
  - Update
    `examples/104_review_final_output_output_schema_blocked_control_ready` so
    its manifest and reference artifacts prove the emitted route contract for
    the review carrier final-response path.
  - Update
    `examples/105_review_split_final_output_output_schema_control_ready` so
    its manifest and reference artifacts prove the emitted route contract for
    the review split final-response path.
  - Update
    `examples/106_review_split_final_output_output_schema_partial` so its
    manifest and reference artifacts prove conditional review routing,
    including routed branches plus any unrouted branch metadata.
  - Preserve existing review control metadata ownership. Do not duplicate that
    metadata into the new top-level route block.
* Verification (required proof):
  - Run `uv run --locked python -m unittest tests.test_emit_docs`.
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/104_review_final_output_output_schema_blocked_control_ready/cases.toml`.
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/105_review_split_final_output_output_schema_control_ready/cases.toml`.
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/106_review_split_final_output_output_schema_partial/cases.toml`.
* Docs/comments (propagation; only if needed):
  - Keep review example text clear that `review` metadata and top-level
    `route` metadata answer different runtime questions and both still ship.
* Exit criteria (all required):
  - Review carrier, split, and conditional final-response contracts all prove
    the same top-level route contract model.
  - Existing `review.outcomes.route_behavior` stays present and keeps its
    backward-compatible role.
  - The review-targeted unit and manifest checks above pass.
* Rollback:
  - Revert the review contract assertions and review example refs together so
    review proof stays on one internally consistent surface.

## Phase 4 — Public Docs, Versioning, And Full Proof

* Goal:
  Bring the shipped docs, versioning guidance, and release notes into line
  with the new public route contract and finish with full proof.
* Work:
  Public contract work is not complete until the shipped docs and release
  surfaces say the same thing as the emitted file and example proof.
* Checklist (must all be done):
  - Update `docs/EMIT_GUIDE.md` to teach the top-level `route` block in
    `final_output.contract.json`.
  - Update `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`,
    `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_REFERENCE.md`, and
    `docs/AUTHORING_PATTERNS.md` so authored routing guidance points harness
    authors to the canonical emitted route contract instead of copied payload
    strings.
  - Update `docs/README.md` and `examples/README.md` so the docs index and
    example index point readers to the new contract story and proof examples.
  - Update `docs/VERSIONING.md` so it records the additive public
    `final_output.contract.json` contract expansion and its non-breaking
    compatibility posture.
  - Update `CHANGELOG.md` with the additive release entry and upgrade guidance
    for harness authors moving from copied owner strings to the emitted route
    block.
  - Run `uv sync`.
  - Run `npm ci`.
  - Run `uv run --locked python -m unittest tests.test_emit_docs
    tests.test_final_output tests.test_route_output_semantics`.
  - Run `make verify-diagnostics`.
  - Run `make verify-examples`.
  - Run `make verify-package`.
* Verification (required proof):
  - The checklist commands above are the required final proof set for this
    public-surface change.
* Docs/comments (propagation; only if needed):
  - Delete or rewrite any touched live doc wording that still teaches copied
    owner strings as the generic runtime route contract.
* Exit criteria (all required):
  - The emitted contract, manifest-backed examples, and live docs all teach
    the same top-level `route` model.
  - `docs/VERSIONING.md` and `CHANGELOG.md` are updated for the additive
    public surface change.
  - `uv sync`, `npm ci`, the targeted unit tests, `make verify-examples`, and
    `make verify-package` all pass, or a concrete blocking dependency gap is
    recorded plainly before audit.
* Rollback:
  - Revert the public docs, versioning updates, changelog entry, and contract
    changes together rather than shipping mixed guidance about the runtime
    route source.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Extend the existing emit-contract and route-semantic tests first.
- Likely anchors are `tests/test_emit_docs.py`, `tests/test_final_output.py`,
  and `tests/test_route_output_semantics.py`.

## 8.2 Integration tests (flows)

- Use manifest-backed route and review examples that prove the emitted
  contract, not only human-readable markdown.
- Run `make verify-diagnostics` because Phase 2 updates
  `doctrine/_diagnostic_smoke/emit_checks.py`.
- Run `make verify-examples` for the final touched surface set.
- Run `make verify-package` because `final_output.contract.json` is a public
  emitted surface and this change extends that contract.

## 8.3 E2E / device tests (realistic)

- No device work is expected.
- Manual finalization should inspect emitted `final_output.contract.json`
  outputs for at least one ordinary routed final and one routed review final.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Ship the routing contract, docs, examples, and proof in one change.
- Do not hide the new surface behind a runtime flag or host-only adapter.
- Update `docs/VERSIONING.md` and `CHANGELOG.md` in the same change because
  this is an additive public contract update.

## 9.2 Telemetry changes

- No new telemetry is expected for the compiler or emit path.
- If the final design adds new diagnostics or failure modes, document them in
  the shipped compiler error surfaces instead of adding runtime telemetry
  theater.

## 9.3 Operational runbook

- Harness authors should be able to switch from custom owner strings to the
  emitted routing block once this ships.
- The runbook burden should stay near zero because the contract is static and
  emitted at build time.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: explorer 1, explorer 2, self-integrator
- Scope checked:
  - frontmatter, helper blocks, and cross-section agreement from `TL;DR`
    through Section 10
  - outcome and scope agreement for routed and unrouted final-output
    contracts
  - architecture, call-site audit, phase plan, verification, rollout, and
    release-surface alignment
- Findings summary:
  - top-of-doc scope said the `route` block appeared only when routing was
    live, while the locked target architecture says the block is always
    emitted with `exists: false` when unrouted
  - workflow-law proof was promised by scope and research, but not scheduled
    in the authoritative phase plan
  - `examples/111_inherited_output_route_semantics` was named as an adjacent
    surface without an authoritative include or defer rule in Section 7
  - `make verify-diagnostics` was missing even though Phase 2 changes
    `doctrine/_diagnostic_smoke/emit_checks.py`
  - decision-log follow-ups still read like open planning work after the plan
    was already locked
- Integrated repairs:
  - rewrote `TL;DR`, Section `0.1`, Section `0.2`, and Section `0.4` so the
    emitted top-level `route` block scope matches the locked target
    architecture
  - added workflow-law proof to the call-site audit and Phase 2 checklist,
    verification, and exit criteria through
    `examples/87_workflow_route_output_binding`
  - made the `examples/111_inherited_output_route_semantics` defer explicit in
    migration notes, the consolidation sweep, and Phase 2 exit conditions
  - added `make verify-diagnostics` to the required proof surface in Phase 2,
    Phase 4, Section 8, and the emit-smoke call-site audit row
  - converted stale decision-log follow-ups into completed historical notes
- Remaining inconsistencies:
  - none
- Unresolved decisions:
  - none
- Unauthorized scope cuts:
  - none
- Decision-complete:
  - yes
- Decision: proceed to implement? yes
<!-- arch_skill:block:consistency_pass:end -->

# 10) Decision Log (append-only)

## 2026-04-15 - Use one emitted contract for runtime routing

### Context

Doctrine already resolves route truth and already emits
`final_output.contract.json` plus review control metadata. The missing piece is
one machine-readable routing contract for final responses.

### Options

- Keep asking models to copy route targets into ad hoc fields like
  `next_owner`.
- Add a second emitted routing file or host-specific bridge.
- Extend `final_output.contract.json` with canonical routing metadata.

### Decision

Plan around extending `final_output.contract.json` with canonical routing
metadata that works for routed finals and routed reviews.

### Consequences

- Emit code, tests, examples, and docs move together.
- Compatibility needs an explicit review because the emitted contract is a
  public surface.
- Review and non-review routing should converge on one runtime model.

### Follow-ups

- Completed in Sections 3, 5, 6, and 7: the serialized routing shape,
  versioning impact, and proof-surface audit are now fixed in the plan.

## 2026-04-15 - Normalize routed final-response metadata in compile

### Context

Research showed that Doctrine already resolves canonical routed target truth in
`RouteSemanticContext`, but `final_output.contract.json` still stops at
`final_output` and `review`. Review finals already emit control metadata, so
the real choice was where to normalize routed final-response truth without
creating a second model.

### Options

- Derive route metadata ad hoc inside `emit_docs.py` from whichever compiled
  fields happen to be present.
- Normalize one shared compiled route contract on `CompiledAgent`, then
  serialize it in the existing emit path.
- Add a second emitted route file or a review-only bridge.

### Decision

Normalize one shared compiled `route` contract on `CompiledAgent` in
`doctrine/_compiler/compile/agent.py`, and serialize it as an additive
top-level `route` block in `final_output.contract.json`. Preserve
`contract_version: 1`, preserve the current `final_output` and `review` keys,
and reuse the same branch-summary formatter that powers `route.summary`.

### Consequences

- Ordinary finals, `route_only`, `route_from`, and routed reviews now have one
  runtime routing model.
- Review control metadata can stay where it is, but routed target truth no
  longer needs a separate bridge.
- Docs, examples, and emit tests must move together because the public
  contract grows while the file path and version stay stable.

### Follow-ups

- Completed in Section 7: this architecture now has the authoritative phased
  implementation plan.
- Reopen the plan only if implementation finds repo-backed evidence that the
  additive version-`1` contract cannot hold.
