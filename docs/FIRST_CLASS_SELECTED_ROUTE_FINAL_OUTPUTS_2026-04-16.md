---
title: "Doctrine - First-Class Selected Route Final Outputs - Architecture Plan"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - doctrine/grammars/doctrine.lark
  - doctrine/_parser/io.py
  - doctrine/_model/io.py
  - doctrine/_model/law.py
  - doctrine/_parser/workflows.py
  - doctrine/_compiler/validate/routes.py
  - doctrine/_compiler/validate/route_semantics_context.py
  - doctrine/_compiler/compile/agent.py
  - doctrine/emit_docs.py
  - doctrine/_diagnostic_smoke/fixtures_final_output.py
  - tests/test_final_output.py
  - tests/test_route_output_semantics.py
  - tests/test_emit_docs.py
  - tests/test_output_schema_surface.py
  - tests/test_output_schema_lowering.py
  - docs/LANGUAGE_REFERENCE.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/AUTHORING_PATTERNS.md
  - docs/WORKFLOW_LAW.md
  - docs/EMIT_GUIDE.md
  - docs/VERSIONING.md
  - CHANGELOG.md
  - examples/92_route_from_basic/prompts/AGENTS.prompt
  - examples/93_handoff_routing_route_from_final_output/prompts/AGENTS.prompt
  - examples/94_route_choice_guard_narrowing/prompts/AGENTS.prompt
  - examples/119_route_only_final_output_contract/prompts/AGENTS.prompt
  - editors/vscode/README.md
---

# TL;DR

## Outcome

Doctrine gains a first-class way to author a selected route on a structured
final output from one owned declaration, while the compiler still owns named
agent routing and the emitted runtime `route` contract.

## Problem

Today a common handoff turn often has to say the same route decision twice:
once in a final-output field that carries the selected choice, and again in a
separate `route_from` table that maps that choice to a named agent.

## Approach

Add a first-class routed final-output surface that keeps the whole decision in
one place. The chosen public shape is:

- a dedicated `route field` inside `output schema`
- an explicit `final_output.route:` binding that points at that field
- a generic emitted `route.selector` block in `final_output.contract.json`
- `nullable` route fields meaning "no route selected"
- field-scoped typed route-choice refs for `route.choice` guards

Doctrine should lower that authored owner to the same internal route truth it
already uses for `route_from`, `route.choice.*`, and the top-level emitted
`route` block in `final_output.contract.json`.

## Plan

1. Add `route field` and `final_output.route:` as the public authoring
   surface.
2. Lower that surface to the existing compiler-owned route semantics instead
   of inventing a second routing path.
3. Extend the emitted top-level `route` contract with generic selector
   metadata and explicit no-route behavior.
4. Prove the behavior through parser, validation, route-choice narrowing,
   final-output, route semantics, emit-contract tests, and manifest-backed
   examples.
5. Update the language, authoring, emit, and versioning docs in the same
   change.

## Non-negotiables

- Do not add a second routing model beside Doctrine's existing route
  semantics.
- Do not weaken route truth into a plain string owner field.
- Keep named-agent routing, compiler-owned route truth, and fail-loud
  validation.
- Keep `final_output.contract.json` as the runtime route contract.
- Keep existing `route_from` legal in the first cut.
- Update code, tests, examples, docs, versioning truth, and changelog truth in
  one change.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-16
recommended_flow: research -> deep dive -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-16
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine makes routed final-output choice a first-class `route field` on a
structured final output and binds `final_output.route` to that field,
authors can express common handoff turns from one clear owner while Doctrine
still emits one canonical top-level route contract, including selector
metadata and no-route behavior, for runtime consumers.

## 0.2 In scope

- Add one additive final-output authoring surface for route-choice decisions
  on structured `TurnResponse` outputs.
- Ship the public syntax as:

  ```prompt
  output schema WriterDecisionSchema: "Writer Decision Schema"
      route field next_route: "Next Route"
          seek_muse: "Send to Muse for fresh inspiration." -> Muse
          ready_for_critic: "Send to PoemCritic for judgment." -> PoemCritic

  agent Writer:
      final_output:
          output: WriterDecision
          route: next_route
  ```

- Keep `nullable` route fields as the authoring surface for "handoff or
  finish" turns:

  ```prompt
  output schema WriterResultSchema: "Writer Result Schema"
      route field next_route: "Next Route"
          seek_muse: "Send to Muse for fresh inspiration." -> Muse
          ready_for_critic: "Send to PoemCritic for judgment." -> PoemCritic
          nullable
  ```

- Emit generic selector metadata in the top-level `route` block so the runtime
  contract says where the chosen wire value lives, not just which branches
  exist.
- Keep `route.exists` semantics explicit:
  - it means the final response carries route semantics
  - it does not mean a branch was selected on this payload
- Define `nullable` route fields as `null => no route selected` with no fake
  terminal target.
- Add typed field-scoped route-choice refs for guards, such as:

  ```prompt
  when route.choice == WriterDecisionSchema.next_route.seek_muse
  ```

- Keep the selected route visible in the final payload through the bound route
  field, so structured output and auditability stay first-class.
- Lower the new surface to the same compiler-owned route semantics already
  used by `route_from`, `route.choice.*`, and the emitted top-level `route`
  contract.
- Keep compatibility posture explicit:
  - preserve `route_from`
  - preserve the top-level `route` block as the one runtime owner
  - extend that block additively with `route.selector`
- Preserve ordinary non-review handoff support as the main target use case.
- Preserve ordinary terminal turns where the final payload ends with no
  handoff because the bound route field is `null`.
- Add focused proof in grammar, parser, model, validation, route semantics,
  route-choice narrowing, final-output compile, and emit-contract paths.
- Add or update manifest-backed examples that teach the common route-field
  final-output path, including the nullable no-route case.
- Update the main shipped docs that explain workflow law, route semantics,
  final output, and emitted route contracts.
- Update editor-facing syntax proof if the new public surface changes VS Code
  support files or snapshots.
- Update `docs/VERSIONING.md` and `CHANGELOG.md` because this is a new public
  language surface.

## 0.3 Out of scope

- Replacing `route_from` as the low-level routing primitive.
- Reconstructing route truth from payload strings outside Doctrine.
- Adding a weaker `next_owner: string` shortcut as the real routing owner.
- Keeping `type: route` plus `selected_route:` as the final public syntax.
- Implicit route inference with no explicit `final_output.route:`
  binding in the first cut.
- Redesigning review routing, `route_only`, or grounding beyond whatever
  shared lowering reuse falls out naturally from the chosen owner path.
- Shipping a reusable top-level `route choice` declaration in the first cut.
- Making raw string compares the primary public way to narrow `route.choice`.

## 0.4 Definition of done (acceptance evidence)

- Authors can express a common route-field final output from one clear owned
  declaration instead of a separate output field plus `route_from` table.
- The same authored owner defines:
  - allowed choices
  - wire values
  - human-facing labels
  - named target agents
- Doctrine still emits the canonical top-level `route` block from that one
  owner in `final_output.contract.json`.
- The emitted `route` block includes machine-readable selector metadata for
  the bound route field.
- `route.exists` is defined and proven as "this final response carries route
  semantics," not "this payload selected a routed branch."
- Structured final outputs carry the selected route choice in the bound route
  field on the payload.
- Nullable route fields compile and emit an explicit "no route selected"
  contract story without fake terminal targets.
- The emitted selector object is explicitly generic-by-contract, with v1 using
  final-output field metadata and later sources allowed to add source-specific
  fields without creating a second route contract.
- `route.choice` guards can narrow route-field branches through typed
  field-scoped choice refs.
- Existing `route_from` prompts still compile in the first cut.
- Unit tests cover parser, validation, route-choice narrowing, route
  semantics, final-output compile, and emit-contract behavior.
- Manifest-backed examples cover at least one ordinary route-field final
  output, one nullable no-route route-field final output, and any touched
  adjacent routed examples.
- Shipped docs teach the new common path and keep the old primitive positioned
  as the lower-level tool.
- Versioning and changelog truth match the public compatibility posture.

## 0.5 Key invariants (fix immediately if violated)

- One routing model: the new syntax must lower to existing Doctrine route
  semantics.
- One runtime route contract: harnesses still read the emitted top-level
  `route` block, not copied payload strings.
- One runtime selector story: if the chosen route comes from payload data, the
  emitted `route` block must say where that selector lives.
- `route.exists` must keep one meaning across the feature: route semantics are
  present on this final response, even when a nullable route field selected
  no branch.
- No silent behavior drift in route selection, `route.choice.*` reads, or
  emitted route metadata.
- No second source of truth for mapping route choices to named agents.
- `route.selector` must stay one generic contract surface, not a
  final-output-only one-off that blocks future routed owners.
- `null` on a nullable route field means "no route selected," not a fake
  terminal branch.
- Fail loud when the bound route field is malformed, ambiguous, or bound to
  an invalid final output.
- No review-only or Rally-only special case hidden inside the language shape.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Make common final-output route-choice turns read as one authored decision.
2. Keep compiler-owned named-agent route truth and emit behavior intact.
3. Make the public syntax feel native to Doctrine, not like JSON Schema glue.
4. Keep the first cut additive and low-risk for existing prompt files.
5. Keep the syntax explicit enough to avoid magic or hidden inference.
6. Keep tests, examples, docs, and release truth aligned in one pass.

## 1.2 Constraints

- Routing is already a public Doctrine surface through workflow law,
  `route_from`, `route.*`, and `final_output.contract.json`.
- `output schema` and `final_output:` are already public authoring surfaces.
- The repo already promises fail-loud route validation and canonical emitted
  route metadata.
- The new feature must fit Doctrine's generic language, not one harness's
  local workflow.
- The emitted route contract is already public. Any selector metadata added
  here is a public additive contract change and must stay generic.

## 1.3 Architectural principles (rules we will enforce)

- Add one higher-level authoring surface, not one parallel route engine.
- Prefer first-class syntax for control-bearing fields over overloading
  generic JSON type syntax.
- Prefer an explicit field binding over hidden route inference.
- Keep wire values, labels, and named targets owned by one declaration.
- Reuse existing route compile and emit paths whenever possible.
- Keep selector location compiler-owned in the emitted route contract.
- Keep no-route meaning explicit and typed, not encoded as a fake agent.
- Keep low-level `route_from` for advanced or non-final-output routing cases.

## 1.4 Known tradeoffs (explicit)

- A dedicated `route field` adds one more grammar form, but it reads more
  honestly than pretending route choice is only a generic schema type.
- An explicit `final_output.route:` binding adds one line, but it keeps the
  owner path obvious and avoids magic.
- Keeping both the new surface and raw `route_from` slightly widens the public
  language, but it keeps the compiler path single-source and additive.
- Adding `route.selector` widens the emitted route contract slightly, but it
  removes the need for harness-local selector reconstruction and keeps route
  truth single-source.
- Focusing the first cut on structured final outputs may leave wider reuse
  questions for a later change, but it keeps the common case small and clear.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already routes to named agents through workflow law, review, and
`handoff_routing`. It already exposes shared `route.*` reads to outputs. It
also already emits a canonical top-level `route` block in
`final_output.contract.json`.

For typed route selection, Doctrine ships `route_from`. That surface is sound
and strict: it is enum-backed, exhaustive, fail-loud, and tied to concrete
named agents.

## 2.2 What’s broken / missing (concrete)

The common authoring case still feels spread out. A structured final output
that carries the selected route choice often needs:

- a final-output field for the chosen wire value
- a separate `route_from` table that maps that wire value to named agents

That split adds ceremony, makes prompts harder to read, and asks authors to
keep one decision aligned across two authored surfaces.

## 2.3 Constraints implied by the problem

The fix must stay small, typed, and explicit. It must keep named-agent route
truth compiler-owned, keep runtime routing on the emitted contract, and keep
advanced routing cases available without forcing them through the new common
path. It must also define the common "handoff or finish" turn cleanly instead
of leaving `null` route values undefined.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## External anchors (papers, systems, prior art)

- None adopted for v1 — reject outside prior art as the main driver — Doctrine
  already ships the route model, emitted route contract, and final-output
  surfaces that this feature must reuse exactly.

## Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/grammars/doctrine.lark` — grammar owns `final_output`,
    `route_from`, and output-schema item syntax. Any `final_output.route:` or
    `route field` surface starts here.
  - `doctrine/_parser/agents.py` and `doctrine/_parser/parts.py` —
    `final_output` blocks currently accept only `output:` and
    `review_fields:`. A `final_output.route:` binding needs a real parse node
    here.
  - `doctrine/_model/agent.py` — `FinalOutputField` currently stores only the
    output ref and optional review-field bindings. The new owner path needs one
    explicit route-field binding on this model, not hidden inference later.
  - `doctrine/_parser/io.py` and `doctrine/_model/io.py` — output-schema
    fields are built from generic flags, settings, and enum helpers today.
    `route field` needs authored nodes here if it is to carry choices, labels,
    and targets as first-class syntax instead of hiding inside `type:`.
  - `doctrine/_compiler/resolve/output_schemas.py` — output-schema lowering
    owns wire JSON shape. This path can lower a `route field` to an ordinary
    string enum on the wire, but it does not own named-agent route meaning.
  - `doctrine/_compiler/validate/routes.py`,
    `doctrine/_compiler/validate/route_semantics_context.py`, and
    `doctrine/_compiler/validate/route_semantics_reads.py` — these files own
    route truth, route choice member extraction, and fail-loud `route.*` read
    behavior. Current `choice_members` come only from `route_from`-backed
    `LawRouteStmt` branches, and current route-choice narrowing assumes
    enum-backed compares.
  - `doctrine/_compiler/validate/agents.py` —
    `_route_output_contexts_for_agent()` is the current fan-out point that
    applies one agent-wide route context to every emitted output. That
    assumption is the main convergence seam for a final-output-owned route
    surface.
  - `doctrine/_compiler/compile/final_output.py`,
    `doctrine/_compiler/compile/agent.py`, and `doctrine/emit_docs.py` — these
    files own final-output compile, top-level final-response route contract
    normalization, and `final_output.contract.json` emission. The new surface
    must end here with the same contract family plus additive selector
    metadata.
  - `doctrine/_compiler/resolve/outputs.py` and
    `doctrine/_compiler/output_schema_validation.py` — these files prove final
    output refs, lowered JSON schema validity, and example conformance. The new
    surface must stay inside these proof rails.
- Canonical path / owner to reuse:
  - `doctrine/_compiler/validate/agents.py` plus
    `doctrine/_compiler/compile/agent.py::_compile_final_response_route_contract()`
    — keep one canonical route-contract path. New `route field` authoring must
    feed `RouteSemanticContext` for the bound final-output key instead of
    bypassing route validation or emit.
  - `doctrine/_compiler/resolve/output_schemas.py` — keep wire-shape lowering
    here. The route field should still lower to an ordinary JSON string field
    with enum-like wire values.
- Adjacent surfaces tied to the same contract family:
  - `tests/test_final_output.py`, `tests/test_route_output_semantics.py`, and
    `tests/test_emit_docs.py` — current proof for final output, route
    semantics, and emitted route contracts.
  - `tests/test_output_schema_surface.py` and
    `tests/test_output_schema_lowering.py` — proof for public output-schema
    syntax and JSON lowering.
  - `examples/92_route_from_basic`,
    `examples/93_handoff_routing_route_from_final_output`,
    `examples/94_route_choice_guard_narrowing`, and
    `examples/119_route_only_final_output_contract` — current ordinary route,
    route-choice, and emitted-contract ladder that this feature extends.
  - `examples/104_review_final_output_output_schema_blocked_control_ready`,
    `examples/105_review_split_final_output_output_schema_control_ready`, and
    `examples/106_review_split_final_output_output_schema_partial` —
    review-adjacent routed final outputs that must either stay unchanged or be
    clearly deferred in v1 docs and tests.
  - `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
    `docs/WORKFLOW_LAW.md`, `docs/EMIT_GUIDE.md`, and
    `docs/AUTHORING_PATTERNS.md` — public docs that define the route,
    final-output, and authoring story.
  - `editors/vscode/` — public syntax support must stay in sync if grammar or
    keywords change.
- Compatibility posture (separate from `fallback_policy`):
  - Preserve existing contract with an additive public feature — keep
    `route_from` legal and keep the emitted top-level `route` block as the one
    runtime owner — extend that block additively with generic `selector`
    metadata instead of inventing a second contract. This avoids a cutover,
    preserves old manifests, and keeps the runtime contract stable.
- Existing patterns to reuse:
  - `doctrine/_model/io.py` and `doctrine/_compiler/resolve/output_schemas.py`
    — string-enum lowering for object fields — reuse the same wire-value
    lowering pattern so `route field` still emits a normal string field with
    fixed allowed values.
  - `doctrine/_parser/agents.py` and `doctrine/_model/agent.py` — explicit
    `final_output:` block ownership — reuse the same one-line explicit binding
    style instead of hidden inference.
  - `doctrine/_compiler/validate/route_semantics_context.py` —
    `choice_members` extraction and branch dedupe — reuse this route metadata
    shape for emitted runtime choice detail.
  - `doctrine/_compiler/compile/agent.py` and `doctrine/emit_docs.py` — one
    normalized final-response route contract — reuse this exact runtime
    contract path and extend it with selector metadata instead of adding a
    sidecar contract.
- Prompt surfaces / agent contract to reuse:
  - `examples/93_handoff_routing_route_from_final_output/prompts/AGENTS.prompt`
    — proves today’s closest user story: a final output carries a route choice
    field, and `route_from` maps it to named agents.
  - `examples/92_route_from_basic/prompts/AGENTS.prompt` and
    `examples/94_route_choice_guard_narrowing/prompts/AGENTS.prompt` — prove
    current typed route-choice semantics, exhaustiveness, and `route.choice.*`
    guard rules from enum-backed owners.
  - `examples/119_route_only_final_output_contract/prompts/AGENTS.prompt` —
    proves the harness-facing emitted `route` contract is the runtime truth,
    not prompt-local prose.
- Native model or agent capabilities to lean on:
  - Existing structured `TurnResponse` JSON outputs — the model already picks
    enum-like wire values inside `output schema` payloads. This feature only
    needs a better authored owner for that existing behavior.
- Existing grounding / tool / file exposure:
  - `final_output.contract.json` — already exposes the top-level `route` block
    with `branches`, `behavior`, and `choice_members`, but it does not yet say
    where a payload-owned selector lives.
  - `route.*` reads — already expose compiler-owned route truth to authored
    outputs when route semantics are live.
- Duplicate or drifting paths relevant to this change:
  - `output schema` selected-choice field plus separate `route_from` table —
    this is the authored split the feature is trying to remove for common final
    output handoffs.
  - `doctrine/_compiler/validate/agents.py::_route_output_contexts_for_agent()`
    — today it assumes route truth is agent-wide and fans it to every emitted
    output. A final-output-owned route surface will drift unless this map
    becomes explicit about output-specific route context.
- Capability-first opportunities before new tooling:
  - Reuse current output-schema lowering, current route-semantic validation,
    and current emitted contract serialization — no new harness bridge, runtime
    parser, or payload-side route reconstruction is needed.
  - Keep named-agent mapping out of raw JSON schema lowering — resolve it from
    authored route choices and feed it into route semantics and final-output
    compile instead.
- Behavior-preservation signals already available:
  - `uv run --locked python -m unittest tests.test_output_schema_surface`
  - `uv run --locked python -m unittest tests.test_output_schema_lowering`
  - `uv run --locked python -m unittest tests.test_route_output_semantics`
  - `uv run --locked python -m unittest tests.test_final_output`
  - `uv run --locked python -m unittest tests.test_emit_docs`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/92_route_from_basic/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/93_handoff_routing_route_from_final_output/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/119_route_only_final_output_contract/cases.toml`
  - `make verify-examples`

## Decision gaps that must be resolved before implementation

- None blocked for user input — repo evidence checked: grammar, parser, model,
  output-schema lowering, route-semantic validation, final-output compile,
  emit-contract serialization, unit tests, and manifest-backed route examples.
  The chosen architecture is:
  - public syntax: `route field` plus `final_output.route:`
  - emitted runtime bridge: generic top-level `route.selector`
  - nullable route meaning: `null => no route selected`
  - typed compare surface: field-scoped route-choice refs
  No plan-shaping decision remains open before implementation.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 Public authoring surfaces today

Today Doctrine splits this story across three separate public surfaces:

- `output schema` owns structured payload shape and wire validation.
- `final_output:` picks which emitted `TurnResponse` output is the turn-ending
  contract surface.
- workflow law or `handoff_routing` owns named-agent route truth through
  `route`, `route_only`, review routes, or `route_from`.

There is no first-class authored surface where one final-output field both
names the selected route value and owns the mapping to named target agents.

## 4.2 Current parse and model boundaries

- `doctrine/grammars/doctrine.lark` lets `final_output:` be either one ref or a
  block with `output:` plus optional `review_fields:`.
- `doctrine/_parser/agents.py` lowers that block into `FinalOutputBodyParts`,
  and `doctrine/_model/agent.py` stores it as `FinalOutputField(value,
  review_fields)`.
- `output schema` fields are generic. `doctrine/_parser/io.py` and
  `doctrine/_model/io.py` support settings such as `type`, `ref`, `values`,
  `enum`, `items`, and nested fields, but nothing route-specific.

That means the current parser and model do not have any place to store:

- a bound route field on `final_output`
- route-choice entries on a first-class `route field`

## 4.3 Current route-semantics flow

The route contract path today is:

1. Validation collects route-bearing control surfaces from review, `workflow`
   law, and `handoff_routing` law in
   `doctrine/_compiler/validate/agents.py`.
2. `_route_semantic_context_for_agent()` enforces that only one route-bearing
   source is live for the whole agent.
3. `_route_output_contexts_for_agent()` fans that one route context to every
   emitted output key on the agent.
4. `doctrine/_compiler/compile/final_output.py` resolves the bound final
   output, asks for the route context for that output key, and uses it to
   validate any route-aware output support.
5. `doctrine/_compiler/compile/agent.py::_compile_final_response_route_contract()`
   turns that route context into the top-level emitted `route` block.
6. `doctrine/emit_docs.py` writes the contract to
   `final_output.contract.json`.

The important present-day assumption is step 3: route truth is agent-wide, so
every emitted output sees the same route context.

## 4.4 Current route-choice metadata path

`route.choice.*`, typed route-choice narrowing, and emitted `choice_members`
are currently tied to `route_from`.

- `doctrine/_model/law.py` stores `route_from` detail on `LawRouteStmt` with
  `choice_enum_ref`, `choice_case_heads`, and `choice_else`.
- `doctrine/_compiler/validate/route_semantics_context.py` converts those enum
  members into `RouteChoiceMember`.
- `doctrine/_compiler/validate/route_semantics_context.py` also narrows route
  branches from compares like `when route.choice == ProofRoute.accept`, which
  assumes enum-backed choice identities today.
- `doctrine/_compiler/validate/route_semantics_reads.py` exposes
  `route.choice.key`, `route.choice.title`, and `route.choice.wire` only when
  every live branch carries those members.
- `doctrine/_compiler/compile/agent.py` and `doctrine/emit_docs.py` serialize
  those members into the emitted route contract.

So today, route-choice metadata and typed route-choice narrowing only exist
when authored route truth came through `route_from`.

## 4.5 Current output-schema lowering and emitted contract behavior

`doctrine/_compiler/resolve/output_schemas.py` lowers `output schema` to plain
JSON Schema:

- inline enums already normalize onto one string-enum path
- object fields are always required on wire unless marked `optional`
- the lowered schema is validated for final-output use and OpenAI structured
  output compatibility

This lowerer is the right wire-shape owner, but it does not know anything
about named agents or route truth.

At the same time, the emitted top-level `route` block only says which route
branches exist. It does not say where a payload-owned selector lives. So a new
final-output-owned route surface cannot be complete until the emitted
contract grows generic selector metadata.

## 4.6 Current fail-loud boundaries

Today Doctrine already fails loud when:

- `final_output:` points at a non-output or non-emitted output
- `final_output:` points at a non-`TurnResponse` target
- lowered final-output JSON schema is invalid or its example is wrong
- several route-bearing control surfaces are live on one agent
- `route.*` reads are used where route truth is missing or not live on every
  branch
- `route_from` selectors, arms, and exhaustiveness are malformed

What is missing is not strictness. What is missing is an authored owner path
that keeps a common route-field final output in one place without creating a
second route engine. The emitted contract is also missing a first-class way to
say where a payload-owned selector lives and what `null` means for routing.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 Chosen architecture

The chosen design is:

- add `route field` as a first-class `output schema` field form
- add `final_output.route:` as the explicit binding from the chosen final
  output to one route field on that output
- keep each route-choice line as the one owner of:
  - the stable choice key
  - the human-readable route label
  - the named target agent
- lower the route field to a normal string enum on the wire
- treat `nullable` route fields as `null => no route selected`
- emit a generic top-level `route.selector` block in
  `final_output.contract.json`
- add field-scoped typed route-choice refs so `route.choice` guards stay typed
- derive route semantics directly from the bound route field for the
  final-output key only

This is one higher-level authoring surface over the same emitted route
contract. It is not a second routing system.

## 5.2 Public syntax and wire behavior

The chosen public syntax is:

```prompt
output schema WriterDecisionSchema: "Writer Decision Schema"
    route field next_route: "Next Route"
        seek_muse: "Send to Muse for fresh inspiration." -> Muse
        ready_for_critic: "Send to PoemCritic for judgment." -> PoemCritic

    field summary: "Summary"
        type: string
        required

    field route_reason: "Route Reason"
        type: string
        required

agent Writer:
    final_output:
        output: WriterDecision
        route: next_route
```

For "handoff or finish" turns, the same public shape stays clean:

```prompt
output schema WriterResultSchema: "Writer Result Schema"
    route field next_route: "Next Route"
        seek_muse: "Send to Muse for fresh inspiration." -> Muse
        ready_for_critic: "Send to PoemCritic for judgment." -> PoemCritic
        optional

    field summary: "Summary"
        type: string
        required
```

Author-facing compare syntax stays typed:

```prompt
when route.choice == WriterDecisionSchema.next_route.seek_muse
```

Wire rules are:

- the choice key is the wire value the model emits
- the quoted text is the route label, not the wire value
- a required `route field` lowers to a string enum of those choice keys
- a `nullable` `route field` lowers to the same string enum wrapped in the
  existing nullable path
- `null` is not a fake route choice. It means no route was selected for that
  turn.

This keeps the common case small. It also avoids using the route label as the
payload wire value.

## 5.3 Binding and validation rules

`final_output.route:` will reuse `field_path` syntax, not a new ref kind.
Validation will:

1. resolve the bound `final_output.output`
2. require that output to be a structured `TurnResponse` backed by an
   `output schema`
3. resolve the bound route field path on that output using the existing
   addressable output-field path resolver
4. require the resolved target to be a first-class `route field` with a
   non-empty choice list
5. let route fields keep shared non-shape metadata such as `nullable` and
   author notes, but reject route fields that try to declare conflicting shape
   owners such as `type:`, `values:`, legacy `enum:`, `ref:`, `items:`, or
   `any_of:`
6. reject duplicate choice keys, duplicate lowered wire values, and unknown
   target agents
7. reject `final_output.route:` on non-structured finals, non-`TurnResponse`
   finals, and fields that are not route fields

Inherited and overridden output-schema fields stay legal because the resolved
field node already exists after output-schema inheritance resolution.

## 5.4 Canonical compile path and SSOT

The canonical owner path is:

- authored route choices live on the resolved `route field`
- `final_output.route` chooses which one of those fields owns route
  truth for the turn-ending contract
- route truth is compiled into `RouteSemanticContext`
- `doctrine/_compiler/compile/agent.py::_compile_final_response_route_contract()`
  still owns the final emitted top-level `route` block

Two boundaries stay strict:

- output-schema lowering owns wire JSON shape only
- route validation and final route-contract emission own named-agent meaning

The route field does not push named-agent data into lowered JSON
schema. It feeds route semantics beside schema lowering, then the existing
final route-contract path emits the runtime truth.

## 5.5 Output-scoped route context, not agent-wide fan-out

This feature must not reuse the current agent-wide route-context fan-out.

The new rule is:

- workflow, `handoff_routing`, review, and `route_only` keep using the current
  agent-wide route-semantic path
- route-field-owned final outputs create route semantics only for the bound
  final-output key

That means `doctrine/_compiler/validate/agents.py` must split:

- agent-wide route-bearing control sources
- output-key-specific route-field final-output sources

Then it must build one `route_output_contexts` map where:

- existing law or review sources still fan out as they do today
- route-field-owned final outputs attach only to their own final-output key

This preserves current behavior for existing route surfaces and avoids leaking
route-field truth onto unrelated outputs.

## 5.6 Emitted route contract, selector metadata, and no-route semantics

The emitted top-level `route` block stays the one runtime route contract, but
it grows one additive generic selector object:

```json
{
  "route": {
    "exists": true,
    "behavior": "conditional",
    "has_unrouted_branch": true,
    "selector": {
      "surface": "final_output",
      "field_path": ["next_route"],
      "null_behavior": "no_route"
    },
    "branches": [
      {
        "target": { "key": "Muse" },
        "label": "Send to Muse for fresh inspiration.",
        "summary": "Send to Muse for fresh inspiration. Next owner: Muse.",
        "choice_members": [
          {
            "member_key": "seek_muse",
            "member_title": "Seek Muse",
            "member_wire": "seek_muse"
          }
        ]
      }
    ]
  }
}
```

The target rules are:

- `route.selector` is generic. It is not a selected-route-only one-off.
- In v1, its concrete fields describe final-output-bound route fields.
- Later route sources may extend the selector object with source-specific
  fields without creating a second runtime route contract.
- `route.exists` means this final response carries route semantics. It does
  not mean this payload selected a routed branch.
- For route-field finals, `route.exists` stays `true` whenever route semantics
  are present, including nullable no-route turns where the selector field is
  `null`.
- In v1, route-field final outputs emit:
  - `surface: "final_output"`
  - `field_path: [...]`
  - `null_behavior: "invalid"` for required route fields
  - `null_behavior: "no_route"` for nullable route fields
- `choice_members` remain the runtime mapping from wire choice to named target.
- For nullable route fields, the emitted contract must show:
  - `behavior: "conditional"`
  - `has_unrouted_branch: true`
- At runtime, if `route.selector` resolves to `null`, there is no selected
  route for that turn.
- Doctrine must not invent fake terminal targets such as `done`, `none`, or
  `stop` just to fill a branch slot.

This keeps routing about named-agent handoff only. Terminal outcome meaning
stays in ordinary final-output payload fields.

## 5.7 Route-choice metadata and typed compares

- `RouteChoiceMember` stops assuming an enum source is always present
- legacy `route_from` members still carry enum metadata
- route-field-owned members carry `member_key`, `member_title`, and
  `member_wire`, but no fake enum owner
- `route.choice.*` reads become source-agnostic across `route_from` and route
  fields
- typed compare refs become field-scoped route-choice identities, such as
  `WriterDecisionSchema.next_route.seek_muse`
- raw string compares may still work where Doctrine already supports them, but
  they are not the primary public path for route-field authoring

This keeps the compare story typed and compiler-owned without forcing authors
to create a second enum just for guards.

## 5.8 Compatibility posture and explicit exclusions

Compatibility posture for v1 is:

- additive language change
- preserve `route_from`
- preserve the top-level emitted `route` contract owner path
- extend the emitted top-level `route` block additively with `selector`
  metadata
- preserve existing routed examples and tests

Explicit v1 exclusions:

- no implicit route inference when `final_output.route:` is missing
- no review-driven `final_output.route:` support in this first cut
- no reusable top-level route-choice declaration
- no payload-only route reconstruction outside Doctrine
- no `type: route` / `selected_route:` public syntax alias
- no fake terminal route targets for nullable route fields

If an agent tries to combine `final_output.route` with another live
route-bearing control surface, v1 should fail loud instead of choosing between
two owners.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar | `doctrine/grammars/doctrine.lark` | `final_output_body`, `output_schema_body_line`, route-choice entry grammar | `final_output` accepts only `output:` and `review_fields:`. Output schema has `field` only, with no routed field form. | Add `route:` in `final_output` blocks. Add a dedicated `route field` form plus route-choice entry grammar under output schema. | The public syntax must read as first-class Doctrine, not as generic type glue. | `final_output.route: <field_path>` and `route field ...` with inline `choice -> Agent` entries. | `tests/test_output_schema_surface.py`, `tests/test_final_output.py` |
| Parser parts | `doctrine/_parser/parts.py` | `FinalOutputBodyParts` | Stores only `output_ref` and `review_fields`. | Add bound route field-path storage. | The parser needs one structured binding target. | `FinalOutputBodyParts(route_path=...)`. | `tests/test_final_output.py` |
| Agent parser/model | `doctrine/_parser/agents.py`, `doctrine/_model/agent.py` | `final_output_body()`, `FinalOutputField` | Final output model stores only output ref and review fields. | Parse and store `route` beside `output` and `review_fields`. | Final-output compile needs one owned route-field binding. | `FinalOutputField(..., route_path=tuple[str, ...] | None)`. | `tests/test_final_output.py` |
| Output-schema parser/model | `doctrine/_parser/io.py`, `doctrine/_model/io.py` | output-schema authored item types | Output schema supports generic settings, flags, enum/value blocks, and nested fields only. | Add authored nodes for `route field` and route-choice entries. Preserve shared field metadata such as `nullable` and notes where valid. | Route labels, wire values, and named targets need a first-class owner. | `OutputSchemaRouteField` plus `OutputSchemaRouteChoice` dedicated model types. | `tests/test_output_schema_surface.py` |
| Output-schema lowering | `doctrine/_compiler/resolve/output_schemas.py` | `_collect_output_schema_node_parts()`, `_lower_output_schema_node()` | Lowerer knows normal field shapes only and route semantics never enter here. | Lower `route field` onto the existing string-enum wire path. Reject conflicting shape owners such as `type:`, `values:`, `enum:`, `ref:`, `items:`, and `any_of:`. | Wire JSON shape must stay simple and OpenAI-compatible. | Lowered wire schema becomes string enum of route keys, nullable through the existing nullable path. | `tests/test_output_schema_lowering.py`, `tests/test_validate_output_schema.py`, `tests/test_prove_output_schema_openai.py` |
| Output-field resolution | `doctrine/_compiler/resolve/outputs.py` | `_resolve_final_output_decl()`, `_resolve_output_field_node()` and new helper near final-output JSON summary | Final-output compile resolves the output but has no route-field binding. | Reuse addressable output-field resolution for `final_output.route` and add a helper that validates the bound field is a route field on a structured final output. | This is the clean existing path for field-path binding and fail-loud unknown-field errors. | `route` binds by field path on the bound final-output output. | `tests/test_final_output.py` |
| Route-source validation | `doctrine/_compiler/validate/agents.py` | `_route_semantic_sources_for_agent()`, `_route_output_contexts_for_agent()` | One route-bearing source is collected for the whole agent and fanned to every emitted output. | Split agent-wide route sources from route-field-owned final-output sources. Build one output-key map that can carry existing fan-out plus final-output-key-only route semantics. Reject conflicting owners. | Route-field truth belongs to the final-output key, not every emitted output. | Output-key-scoped route semantics map with fail-loud owner conflicts. | `tests/test_route_output_semantics.py`, `tests/test_final_output.py`, `tests/test_emit_docs.py` |
| Route-choice model | `doctrine/_compiler/resolved_types.py`, `doctrine/_compiler/types.py`, `doctrine/_compiler/validate/route_semantics_context.py`, `doctrine/_compiler/validate/route_semantics_reads.py` | `RouteChoiceMember`, `CompiledRouteChoiceMemberSpec`, choice-member builders | Choice members assume `route_from` enum provenance. | Generalize choice members so enum metadata is optional and route fields can still produce `key/title/wire`. Keep legacy enum data when present. | `route.choice.*` and emitted contracts must work for both source kinds without fake enums. | `choice_members[*]` always carries `member_key`, `member_title`, `member_wire`; enum metadata is legacy-only when present. | `tests/test_route_output_semantics.py`, `tests/test_emit_docs.py` |
| Route-choice compare resolution | `doctrine/_compiler/validate/route_semantics_context.py`, `doctrine/_compiler/resolve/route_semantics.py`, expression-resolution helpers | `route.choice` narrowing expects enum-backed compare values today. | Teach route-choice compare resolution to accept field-scoped route-choice refs from route fields as constant choice identities. | The new public compare path must stay typed and compiler-owned. | `when route.choice == WriterDecisionSchema.next_route.seek_muse` narrows route semantics the same way enum members do today. | `tests/test_route_output_semantics.py` |
| Final-output compile and emit | `doctrine/_compiler/compile/final_output.py`, `doctrine/_compiler/compile/agent.py`, `doctrine/_compiler/flow.py`, `doctrine/emit_docs.py` | final-output compile, route-contract compile, flow consumers, route serialization | Final output can consume only existing route-output contexts, and emitted route contract has no selector metadata. | Compile route-field semantics for the final-output key, feed them through the same final route-contract path, emit generic `route.selector`, keep `route.exists` tied to route semantics rather than branch selection, and serialize route-field choice members without fake enum owner fields. | One canonical runtime route contract must survive and stay complete for payload-owned route selectors. | Top-level `route` block stays canonical; it now carries additive `selector` metadata, stable `route.exists` semantics, and route-field-backed `choice_members`. | `tests/test_final_output.py`, `tests/test_emit_docs.py`, route-contract example manifests |
| Nullable no-route semantics | `doctrine/_compiler/compile/agent.py`, `doctrine/_compiler/validate/route_semantics_reads.py`, final-output route-contract helpers | Nullable route meaning is not defined for payload-owned selectors today. | Define required route fields as `null_behavior: invalid` and nullable route fields as `null_behavior: no_route`. Emit `has_unrouted_branch: true` for nullable route fields while keeping `route.exists: true` because route semantics are still present. | The common "handoff or finish" turn must be first-class, not undefined. | Nullable route fields compile to a real no-route contract with no fake target branch and stable `route.exists` meaning. | `tests/test_final_output.py`, `tests/test_emit_docs.py`, `tests/test_route_output_semantics.py` |
| Route contract forward shape | route-contract types near `doctrine/_compiler/types.py`, `doctrine/_compiler/resolved_types.py`, `doctrine/emit_docs.py` | emitted selector object shape | No explicit contract note says selector metadata is generic beyond the current final-output source. | Model `route.selector` as a generic contract surface that can grow source-specific fields later without a second top-level route object. | The generic claim must be real architecture, not just a prose note. | One selector object family under top-level `route`, with v1 final-output fields and room for later source-specific fields. | `tests/test_emit_docs.py`, docs updates |
| Diagnostics and smoke | `doctrine/_diagnostic_smoke/flow_route_checks.py`, `doctrine/_diagnostic_smoke/fixtures_final_output.py`, `docs/COMPILER_ERRORS.md` | route/final-output smoke fixtures and public error catalog | No proof for route-field final-output routing exists. Public error catalog has no route-field or selector errors. | Add smoke fixtures and public compile-error coverage for invalid `final_output.route`, invalid route field authoring, invalid selector metadata expectations, and owner conflicts. | The feature must fail loud and stay documented. | New route-field diagnostics and smoke proof. | `make verify-diagnostics` plus focused unit tests |
| Unit proof | `tests/test_final_output.py`, `tests/test_route_output_semantics.py`, `tests/test_output_schema_surface.py`, `tests/test_output_schema_lowering.py`, `tests/test_validate_output_schema.py`, `tests/test_prove_output_schema_openai.py`, `tests/test_emit_docs.py` | public tests | Current proof covers final output, output-schema lowering, route semantics, and emitted route contracts, but not this new owner path. | Add success and fail-loud tests for syntax, lowering, no-route semantics, stable `route.exists` meaning, owner conflicts, final-output binding, route-choice reads, typed compares, emitted route selector metadata, and OpenAI subset proof. | The feature crosses syntax, schema, route semantics, compare narrowing, and emit. | New public proof ladder for route-field final outputs. | all listed suites |
| Example proof | `examples/93_handoff_routing_route_from_final_output/**`, new route-field example directories, `examples/README.md` | manifest-backed ordinary routed final-output story | The closest example still needs a split payload field plus `route_from`. | Keep `93` as the low-level route-from story. Add one manifest-backed example for always-route `route field` finals and one for nullable no-route finals. Update example index text. | Authors need both the common path and the low-level primitive, and the no-route case needs real proof. | New always-route example, new nullable no-route example, plus preserved low-level example. | `make verify-examples`, targeted `doctrine.verify_corpus` runs |
| Public docs and release truth | `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/AUTHORING_PATTERNS.md`, `docs/WORKFLOW_LAW.md`, `docs/EMIT_GUIDE.md`, `docs/VERSIONING.md`, `CHANGELOG.md`, `docs/README.md`, `editors/vscode/**` | public language, patterns, emit contract, release notes, editor support | Docs teach `route_from` as the typed selected-choice path and choice-member emit detail as route-from-only. | Teach the new common path, keep `route_from` as the lower-level primitive, document `route.selector`, nullable no-route semantics, and typed route-choice refs, update versioning/changelog truth, and update editor syntax support if shipped. | Public language, examples, and release policy must stay aligned. | New docs for `route field`, `final_output.route`, `route.selector`, and additive release note. | doc verification by corpus and `cd editors/vscode && make` if touched |

## Migration notes

* Canonical owner path / shared code path:
  `output schema` route field -> `final_output.route` binding ->
  output-key-specific `RouteSemanticContext` -> existing
  `_compile_final_response_route_contract()` -> existing `emit_docs.py`
  serializer, now with additive `route.selector`.
* Deprecated APIs (if any):
  None in v1. `route_from` stays supported as the lower-level primitive.
* Delete list (what must be removed; include superseded shims/parallel paths if any):
  No code-path delete is required in v1. Rewrite any live docs, comments, or
  tests that claim `choice_members` come only from `route_from`, that the
  emitted route contract has no selector metadata, or that route semantics are
  always agent-wide for every emitted output.
* Adjacent surfaces tied to the same contract family:
  final-output compile, emitted route contract, route-choice reads, route
  choice narrowing, output schema lowering, routed examples, and public
  routing docs all move together.
  Review-driven route-field final outputs are intentionally deferred.
* Compatibility posture / cutover plan:
  Additive cut-in. Existing `route_from` prompts and emitted top-level `route`
  blocks stay valid. Route-field `choice_members` and `route.selector` extend
  the existing contract without inventing a second route owner.
* Capability-replacing harnesses to delete or justify:
  None. This feature is pure language and compiler work. No runtime bridge,
  payload parser, or harness reconstruction path is allowed.
* Live docs/comments/instructions to update or delete:
  Update docs that position `route_from` as the only typed selected-choice
  owner. Update emitted-contract docs that describe `choice_members` as
  enum-only, misread `route.exists` as branch selection, or do not mention
  `route.selector`. Update example index text so the new common path, the
  nullable no-route path, and the old primitive are all clear.
* Behavior-preservation signals for refactors:
  `tests.test_output_schema_surface`, `tests.test_output_schema_lowering`,
  `tests.test_validate_output_schema`, `tests.test_prove_output_schema_openai`,
  `tests.test_route_output_semantics`, `tests.test_final_output`,
  `tests.test_emit_docs`, targeted `doctrine.verify_corpus` runs for routed
  examples, and `make verify-examples`.

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Output-key route context | `doctrine/_compiler/validate/agents.py`, `doctrine/_compiler/flow.py` | output-key-specific route context map | Prevent route-field truth from leaking to unrelated outputs while preserving current route fan-out behavior elsewhere. | include |
| Final-output routing proof | `examples/93_handoff_routing_route_from_final_output/**` plus new route-field examples | keep common path, nullable no-route path, and low-level path side by side | Prevent docs and manifests from implying one path replaced the other or that the no-route case is informal. | include |
| Emitted route contract docs | `docs/EMIT_GUIDE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_REFERENCE.md` | `choice_members` are source-agnostic and `route.selector` is the selector bridge | Prevent stale public truth about emitted routing metadata. | include |
| Nullable no-route semantics | route-field example refs, route-contract emit, route-read docs | `nullable` route field means `null => no route selected` | Prevent fake terminal routes or undefined `null` behavior from sneaking in later. | include |
| Typed route-choice refs | route-choice narrowing helpers, docs, and examples | field-scoped choice refs as the primary compare path | Prevent the new surface from drifting back into raw strings or second enums. | include |
| Review-driven routed finals | `examples/104_*`, `examples/105_*`, `examples/106_*`, review compile paths | route-field final outputs on review carriers or split review finals | Same contract family, but deeper scope than this request. | defer |
| Low-level route law docs | `docs/WORKFLOW_LAW.md`, `examples/92_route_from_basic/**`, `examples/94_route_choice_guard_narrowing/**` | keep `route_from` documented as the explicit lower-level primitive | Prevent the new feature from looking like a route-law replacement. | include |
| Reusable route-choice declarations | new top-level declaration surface | named reusable route choice block | Could reduce duplication later, but it is a wider language change than this request needs. | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Surface Syntax And Authored Model

* Goal:
  Make the new route-field authoring surface parse, store, and stay
  backward compatible.
* Status:
  COMPLETE
* Work:
  This phase is the public surface cut-in only. It adds the grammar, parser,
  and authored model shapes for `final_output.route` and `route field`
  declarations without changing route semantics yet.
* Checklist (must all be done):
  - Add grammar for `route:` inside `final_output:` blocks.
  - Add grammar for `route field` entries in `output schema`.
  - Add grammar for inline route-choice lines under a `route field`.
  - Extend parser parts and authored model types so `FinalOutputField` stores
    the bound route-field path and output-schema declarations can store a
    first-class route field plus route choices.
  - Preserve current `final_output: OutputName` shorthand and existing
    output-schema authored forms without behavioral drift.
  - Add parser-surface tests for the new happy path and structural fail-loud
    cases on the new syntax.
  - Update `editors/vscode/` syntax support and generated files if the shipped
    editor grammar depends on the changed public syntax.
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_output_schema_surface`
  - `uv run --locked python -m unittest tests.test_final_output`
  - `cd editors/vscode && make` if anything under `editors/vscode/` changes
* Docs/comments (propagation; only if needed):
  - None in this phase beyond editor syntax assets if touched.
* Exit criteria (all required):
  - The new public syntax parses into stable authored nodes for both the
    final-output route binding and route-field entries.
  - Existing `final_output` and `output schema` surfaces still parse without
    regression.
  - Shipped editor syntax support is updated or explicitly untouched because no
    editor-owned files changed.
* Rollback:
  - Revert the new grammar, parser, model, and editor-syntax additions
    together.

## Phase 2 — Route Field Lowering And Route Binding Validation

* Goal:
  Make route fields lower to valid structured-output wire schema and make
  invalid route-field owners fail loudly before route semantics compile.
* Work:
  This phase keeps wire-shape ownership in output-schema lowering and binding
  ownership in final-output validation. It does not yet change the emitted
  route contract path.
* Checklist (must all be done):
  - Teach output-schema lowering to map `route field` onto the existing
    string-enum lowering path using choice keys as wire values.
  - Preserve existing `nullable` null-wrapping behavior for route fields.
  - Reject invalid authored mixes such as route fields with `type:`,
    `values:`, legacy `enum:`, `ref:`, `items:`, `any_of:`, duplicate choice
    keys, duplicate lowered wire values, or empty route-choice lists.
  - Add a validation helper that resolves `final_output.route` against the
    bound output and the resolved output-schema field path.
  - Reject `final_output.route` on prose final outputs, file outputs, missing
    field paths, unknown field paths, and non-route fields.
  - Keep lowered final-output schema validation and OpenAI subset proof green
    for the new route field shape.
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_output_schema_lowering`
  - `uv run --locked python -m unittest tests.test_validate_output_schema`
  - `uv run --locked python -m unittest tests.test_prove_output_schema_openai`
  - `uv run --locked python -m unittest tests.test_final_output`
* Docs/comments (propagation; only if needed):
  - Add a short code comment only at the chosen route-field lowering seam if
    the mixed wire-shape versus route-truth boundary would otherwise be easy to
    misread.
* Exit criteria (all required):
  - `route field` lowers to a valid string-enum wire schema that matches the
    chosen choice-key wire contract.
  - Invalid route-field authoring and invalid `final_output.route` bindings fail
    loudly with targeted compiler proof.
  - Final-output schema validation and OpenAI structured-output proof remain
    green with route fields present.
* Rollback:
  - Revert the route-field lowering and route binding validation
    helpers together.

## Phase 3 — Output-Key Route Semantics And Emitted Route Contract

* Goal:
  Make route-field final outputs produce the same canonical route truth as
  existing route surfaces without leaking that truth to unrelated outputs.
* Work:
  This phase changes the route-semantics owner path. It splits output-key
  route-field semantics from the current agent-wide route fan-out, then
  feeds the result through the existing final route-contract compile and emit
  path.
* Checklist (must all be done):
  - Split route-source collection so agent-wide route-bearing surfaces and
    route-field final-output surfaces can be modeled separately.
  - Build `route_output_contexts` so workflow, `handoff_routing`, review, and
    `route_only` keep current fan-out behavior while route-field semantics
    attach only to the bound final-output key.
  - Reject agents that try to combine `final_output.route` with another live
    route-bearing owner in v1.
  - Derive `RouteSemanticContext` branches from route-field choices and
    named target agents for the bound final-output key.
  - Generalize `RouteChoiceMember` and compiled route-choice types so
    route fields and legacy `route_from` branches share one runtime
    contract path without fake enum ownership.
  - Keep `route.choice.*` reads fail-loud and correct for both route-field and
    `route_from` sources.
  - Teach route-choice narrowing to accept field-scoped route-choice refs such
    as `WriterDecisionSchema.next_route.seek_muse`.
  - Feed route-field semantics through the existing final-output compile,
    flow, and emitted top-level `route` contract path.
  - Emit additive `route.selector` metadata from the same route-contract path.
    Do not add a second serializer or payload-side reconstruction path.
  - Model `route.selector` as one generic contract surface whose v1 fields
    describe final-output route fields and whose shape can grow
    source-specific fields later without creating a second route contract.
  - Define required route fields as `null_behavior: invalid` and nullable route
    fields as `null_behavior: no_route`.
  - Emit `has_unrouted_branch: true` for nullable route fields and keep `null`
    out of `choice_members`.
  - Keep `route.exists` tied to route semantics, not selected-branch presence,
    including nullable no-route turns.
  - Add focused code comments at the output-key route-context seam only where
    the new ownership split would otherwise be hard to follow.
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_route_output_semantics`
  - `uv run --locked python -m unittest tests.test_final_output`
  - `uv run --locked python -m unittest tests.test_emit_docs`
* Docs/comments (propagation; only if needed):
  - Add high-leverage comments at the output-key route-context seam and
    generalized choice-member seam if those paths would otherwise look like
    accidental duplication.
* Exit criteria (all required):
  - Route-field final outputs emit the canonical top-level `route` block
    through the same compile and emit path used today.
  - Unrelated emitted outputs do not inherit route-field semantics by
    accident.
  - The emitted top-level `route` block includes selector metadata for
    route-field-owned finals.
  - The emitted selector object is generic-by-contract, with v1 final-output
    fields and room for later source-specific fields.
  - Nullable route fields emit a real no-route contract with no fake target
    branch.
  - `route.exists` stays `true` for nullable no-route turns because route
    semantics are present even when no branch was selected.
  - Field-scoped route-choice refs narrow route semantics the same way current
    enum-backed compares do.
  - Existing `route_from`, review, and `route_only` route-contract behavior
    stays green in focused integration proof.
* Rollback:
  - Revert the output-key route-context split and route-field route-semantic
    integration together.

## Phase 4 — Diagnostics, Smoke, And Manifest-Backed Proof

* Goal:
  Lock the public fail-loud story and end-to-end proof for both the new common
  path and the preserved low-level path.
* Work:
  This phase is the proof ladder. It adds smoke and manifest-backed examples
  for the route-field final-output story while keeping the old `route_from`
  story explicit and green.
* Checklist (must all be done):
  - Add or update compiler diagnostics and public error-catalog coverage for
    invalid `final_output.route` binding, invalid route-field authoring,
    invalid route-choice compares, and conflicting route owners.
  - Add or update diagnostic smoke fixtures for route-field final-output
    routing, selector metadata, `route.exists` behavior, no-route behavior,
    and preserved low-level route-contract behavior.
  - Add one new manifest-backed example for always-route route-field final
    outputs, including expected emitted schema and
    `final_output.contract.json` proof.
  - Add one new manifest-backed example for nullable no-route route-field
    finals, including `route.selector`, `route.exists`, and
    `has_unrouted_branch` proof.
  - Keep `examples/92_route_from_basic` and
    `examples/93_handoff_routing_route_from_final_output` as explicit
    low-level `route_from` proof, updating their refs only when the shared
    contract shape requires it.
  - Re-run and update adjacent ordinary and review-routed example proof for
    `94`, `104`, `105`, `106`, and `119` wherever the shared route-contract
    family changed.
* Verification (required proof):
  - `make verify-diagnostics`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/92_route_from_basic/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/93_handoff_routing_route_from_final_output/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/94_route_choice_guard_narrowing/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/104_review_final_output_output_schema_blocked_control_ready/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/105_review_split_final_output_output_schema_control_ready/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/106_review_split_final_output_output_schema_partial/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/119_route_only_final_output_contract/cases.toml`
  - `make verify-examples`
* Docs/comments (propagation; only if needed):
  - None beyond example-owned prompt comments or reference artifacts.
* Exit criteria (all required):
  - The new always-route example proves end-to-end route-field final-output
    behavior, including emitted route contract truth.
  - The new nullable no-route example proves end-to-end no-route behavior for
    nullable route fields.
  - Example proof makes `route.exists` meaning explicit enough that a harness
    cannot mistake it for "selected branch present."
  - The preserved `route_from` examples still prove the lower-level path.
  - Adjacent routed example proof is green anywhere the shared contract family
    was touched.
* Rollback:
  - Revert new diagnostics, smoke fixtures, and example proof together if the
    route-contract story is not stable yet.

## Phase 5 — Public Docs, Example Index, And Release Truth

* Goal:
  Publish one coherent public story for the new common path, the preserved
  lower-level path, and the additive release posture.
* Work:
  This phase updates shipped docs and release truth only after code and proof
  are already stable.
* Checklist (must all be done):
  - Update `docs/LANGUAGE_REFERENCE.md` to teach `route field`,
    `final_output.route`, field-scoped route-choice refs, and nullable
    no-route behavior.
  - Update `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/AUTHORING_PATTERNS.md`,
    `docs/WORKFLOW_LAW.md`, and `docs/EMIT_GUIDE.md` so they show the new
    common path, keep `route_from` as the lower-level primitive, document
    `route.selector`, explain nullable no-route behavior, state that
    `route.exists` means route semantics are present rather than "branch
    selected," explain that `route.selector` is generic-by-contract, and stop
    describing `choice_members` as route-from-only.
  - Update `docs/README.md` and `examples/README.md` so the new example and the
    preserved low-level examples are discoverable from the public index.
  - Update `docs/VERSIONING.md` and `CHANGELOG.md` for this additive public
    language feature and keep release guidance aligned with repo policy.
  - Rewrite or delete any touched live docs, comments, or instructions that
    would otherwise leave stale truth about route ownership, selector metadata,
    no-route semantics, choice-member emit behavior, or agent-wide route-context
    assumptions.
  - State clearly in the relevant docs that review-driven route-field final
    outputs are deferred in v1.
* Verification (required proof):
  - `make verify-examples`
  - Spot-check touched public docs against the shipped example manifests and
    emitted contract artifacts changed in Phase 4.
* Docs/comments (propagation; only if needed):
  - This whole phase is the required propagation pass for shipped docs and
    release truth.
* Exit criteria (all required):
  - Public docs teach one clear common-path syntax, one clear lower-level
    fallback path, one clear nullable no-route story, and one clear emitted
    route-contract story.
  - Public docs teach `route.exists` and `route.selector` in a way that
    prevents harness authors from reconstructing hidden local meanings.
  - Versioning and changelog truth match the additive public feature posture.
  - No touched live docs or instructions still claim stale route ownership or
    stale route selector or choice-member behavior.
* Rollback:
  - Revert the docs and release-truth patchset without undoing already-proven
    code work.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

- Run `uv sync`.
- Run `npm ci`.
- Run the smallest focused unit suites first:
  - `uv run --locked python -m unittest tests.test_output_schema_surface`
  - `uv run --locked python -m unittest tests.test_output_schema_lowering`
  - `uv run --locked python -m unittest tests.test_validate_output_schema`
  - `uv run --locked python -m unittest tests.test_prove_output_schema_openai`
  - `uv run --locked python -m unittest tests.test_route_output_semantics`
  - `uv run --locked python -m unittest tests.test_final_output`
  - `uv run --locked python -m unittest tests.test_emit_docs`
- Run `make verify-diagnostics` if diagnostics or compile-error wording moves.
- Run targeted manifest proof for the routed contract family before the full
  corpus when those examples move:
  - `examples/92_route_from_basic/cases.toml`
  - `examples/93_handoff_routing_route_from_final_output/cases.toml`
  - `examples/94_route_choice_guard_narrowing/cases.toml`
  - `examples/104_review_final_output_output_schema_blocked_control_ready/cases.toml`
  - `examples/105_review_split_final_output_output_schema_control_ready/cases.toml`
  - `examples/106_review_split_final_output_output_schema_partial/cases.toml`
  - `examples/119_route_only_final_output_contract/cases.toml`
  - the new always-route route-field final-output example manifest
  - the new nullable no-route route-field final-output example manifest
- Run `make verify-examples` before the change is done.
- If the syntax change touches `editors/vscode/`, run `cd editors/vscode &&
  make`.
- If the implementation adds or changes a public wire contract, inspect the
  emitted `final_output.contract.json` proof directly in the touched examples,
  including `route.exists`, `route.selector`, `has_unrouted_branch`, and
  `choice_members`.

# 9) Rollout / Ops / Telemetry

- No runtime rollout or telemetry work is expected. This is a language,
  compiler, proof, and docs change.
- The main rollout surface is public authoring guidance:
  - teach `route field` plus `final_output.route:` as the common path
  - teach `nullable` route fields as the common no-route path
  - keep `route_from` documented as the lower-level primitive
- The change must update `docs/VERSIONING.md` and `CHANGELOG.md` in the same
  pass so the public compatibility story stays honest.
- Release classification must match Doctrine's public-feature policy and stay
  aligned with release helper output.
- Public emit docs must call out that `route.selector` is additive runtime
  contract metadata, not a second route contract.
- Public emit docs must also call out that `route.exists` means route
  semantics are present, not that a branch was selected on this payload.

# 10) Decision Log (append-only)

- 2026-04-16: Created the draft plan doc for a first-class selected-route
  final-output surface.
- 2026-04-16: The initial draft used conservative syntax:
  `type: route` plus `choices:` on an `output schema` field, with an explicit
  `final_output.selected_route:` binding.
- 2026-04-16: Draft compatibility posture is additive. Existing `route_from`
  stays legal in the first cut.
- 2026-04-16: Draft scope focus is ordinary non-review selected-route final
  outputs first. Review-specific sugar is not part of the first-cut claim.
- 2026-04-16: North Star confirmed. Doc status moved from `draft` to `active`
  with additive compatibility posture and explicit reuse of existing route
  semantics.
- 2026-04-16: Research grounded the feature in current grammar, output-schema
  lowering, route-semantic validation, final-output compile, and emitted route
  contract paths. The main convergence seam is
  `_route_output_contexts_for_agent()`, which currently fans one agent-wide
  route context to every emitted output.
- 2026-04-16: Deep dive first chose `final_output.selected_route` plus
  `output schema` `type: route` as a conservative v1 owner path.
- 2026-04-16: The plan was then upgraded to the more Doctrine-native public
  surface: `route field` plus `final_output.route:`.
- 2026-04-16: The plan now also requires additive emitted `route.selector`
  metadata, `nullable` route fields meaning `null => no route selected`, and
  field-scoped typed route-choice refs.
- 2026-04-16: Output-key-scoped route contexts remain the chosen route owner
  path for this feature instead of reusing the current agent-wide route
  fan-out.
- 2026-04-16: Review-driven route-field finals remain deferred in v1.
- 2026-04-16: Phase planning remains five phases, but Phase 3 now explicitly
  owns selector metadata, no-route semantics, and typed route-choice
  narrowing, while Phase 4 proves both the always-route and nullable no-route
  example paths.
