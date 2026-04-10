---
title: "Doctrine - Spec 1.3 End-to-End Implementation - Architecture Plan"
date: 2026-04-10
status: complete
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: architectural_change
related:
  - docs/PROPOSAL_SPEC1_3.md
  - docs/WORKFLOW_LAW.md
  - examples/README.md
  - doctrine/grammars/doctrine.lark
  - doctrine/parser.py
  - doctrine/model.py
  - doctrine/compiler.py
  - doctrine/renderer.py
  - doctrine/diagnostics.py
  - doctrine/verify_corpus.py
  - editors/vscode/package.json
  - editors/vscode/extension.js
  - editors/vscode/resolver.js
  - editors/vscode/syntaxes/doctrine.tmLanguage.json
---

# TL;DR

## Outcome

Doctrine ships the Slice A behavior described in
`docs/PROPOSAL_SPEC1_3.md` end to end through the grammar, parser,
model/compiler, diagnostics, renderer, example corpus, docs, and VS Code
extension, so the route-only workflow-law family behaves and renders as
intended, the staged `review` design remains non-shipped, and the editor
correctly highlights and links the shipped language surfaces while proposal
rules 9 and 10 are carried forward honestly instead of being silently deferred.

## Problem

The intended behavior is currently split across proposal prose, shipped
workflow-law docs, hand-authored illustrative examples, compiler diagnostics,
renderer output, and a VS Code extension that adapts part of the language
surface. The user has already called out two concrete failures: the examples
are helpful but not authoritative and may contain mistakes, and the rendered
output is definitely not correct yet. If Doctrine treats those illustrative
surfaces as truth instead of fixing them to match the intended language, it
will lock in drift and harden a bad language shape.

## Approach

Implement from the shipped language core outward. Treat
`docs/PROPOSAL_SPEC1_3.md` as the intended Slice A target, keep
`doctrine/` as the semantic owner, and use the examples, rendered refs, docs,
and VS Code extension as downstream consumers that must be corrected to match
that core. The work should converge the route-only and guarded-output family on
one compiler-owned contract, tighten diagnostics and rendering around that
contract, repair or replace clear example mistakes instead of preserving them,
and then align the VS Code grammar and navigation layer to the same shipped
surface so syntax coloring and link clicks follow the real language.

## Plan

1. Confirm the intended Slice A scope and its hard boundaries: `workflow` +
   `law` + rich `output`, keyed guarded output sections, and no shipped
   top-level `review` primitive.
2. Ground the current implementation in the grammar, parser, model/compiler,
   renderer, diagnostics, workflow-law docs, examples `30` through `42`, and
   the VS Code grammar/link provider to identify where actual shipped behavior
   diverges from intended behavior.
3. Define the canonical end state for semantics, rendering, diagnostics,
   examples, and editor support before changing code, including which example
   mistakes get corrected or deleted, which renderer outputs become the real
   user-facing contract, and how proposal rules 9 and 10 will be carried by
   honest compiler/proof surfaces without magic or prose parsing.
4. Implement the Doctrine core changes first, then align examples/docs/rendered
   refs, then fix the VS Code extension colorizing and definition/document-link
   behavior against the corrected language surface.
5. Verify with the shipped repo checks rather than bespoke harnesses:
   `make verify-examples`, `make verify-diagnostics` when diagnostics change,
   and `cd editors/vscode && make`.

## Non-negotiables

- `doctrine/` stays the language truth; examples and rendered refs are evidence,
  not authority.
- No new shipped top-level `review` primitive in this implementation scope.
- No output-shape duplication inside workflow law; `law` decides when a branch
  is active and `output` decides what must be emitted.
- No compatibility shims or silent fallback behavior to preserve incorrect
  examples, incorrect renders, or partial editor behavior.
- No parallel grammar or semantic model between the compiler and the VS Code
  extension.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-10
Verdict (code): COMPLETE
Manual QA: pending (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None. A fresh audit reran the plan's code-verifiable proof lanes and
  rechecked the compiler, corpus, live-doc, and VS Code anchors named in
  Phases 1 through 4.
  - Evidence anchors:
    - `doctrine/compiler.py:1459`
    - `doctrine/compiler.py:4896`
    - `doctrine/diagnostics.py:1122`
    - `examples/41_route_only_reroute_handoff/cases.toml:62`
    - `examples/42_route_only_handoff_capstone/cases.toml:86`
    - `docs/WORKFLOW_LAW.md:316`
    - `editors/vscode/tests/integration/suite/index.js:454`
    - `editors/vscode/scripts/validate_lark_alignment.py:315`
  - Plan expects:
    - Phase 1 to enforce routed `next_owner` binding and `standalone_read`
      guard discipline on the compiler-owned workflow-law/output path.
    - Phase 2 to carry those two rules into manifest-backed proof and keep the
      live docs aligned to the shipped Slice A surface.
    - Phase 3 to make guarded output headers and conditional law routes
      intentional VS Code-supported surfaces with real proof coverage.
    - Phase 4 to pass `make verify-examples`, `make verify-diagnostics`, and
      `cd editors/vscode && make`, while keeping the stale example-42 ref
      directory removed.
  - Code reality:
    - The compiler enforces both planned route-only contracts on the canonical
      path, diagnostics classify them as `E339` and `E340`, the `41` and `42`
      manifests actively prove both failures, the workflow-law docs teach those
      structured couplings explicitly, and the VS Code validator plus
      integration suite cover conditional routes and guarded-section
      navigation.
    - This audit reran `make verify-examples`, `make verify-diagnostics`, and
      `cd editors/vscode && make`; all three passed.
    - `examples/42_route_only_handoff_capstone/ref/route_only_handoff_capstone_demo`
      remains absent, so the stale downstream truth surface did not regress.
  - Fix:
    - None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Run a short live VS Code smoke on examples `39`, `41`, and `42` if human
  confirmation of click-through and colorization is still desired beyond the
  automated extension-host coverage already in place.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-10
external_research_grounding: not started
deep_dive_pass_2: not started
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

<!-- arch_skill:block:reference_pack:start -->
# Reference Pack (folded materials; phase-aligned)
Updated: 2026-04-10

## Inventory
- R1 — Spec 1.3 Proposal — docs/PROPOSAL_SPEC1_3.md
- R2 — Workflow Law — docs/WORKFLOW_LAW.md
- R3 — Examples Overview — examples/README.md

## Binding obligations (distilled; must satisfy)
- Keep Doctrine's declaration skeleton and `workflow` as the semantic home, keep rich produced-contract material on `output`, ship Slice A as `workflow` + `law` + rich `output`, and do not ship a top-level `review` primitive in the current implementation scope. (From: R1, R2)
- Keep the law/output split explicit: workflow law decides when route-only truth is in force, while `output` owns the route-only handoff schema and guarded conditional readback. Do not duplicate output-shape requirements inside workflow law. (From: R1, R2)
- Treat keyed guarded output sections as an output-owned surface only: they are keyed for identity/addressing/patching, legal inside `output` record bodies, rendered as conditional shells in static docs, and required only when their guard is true at runtime. (From: R1, R2)
- Preserve the narrowed guard-expression namespace: route-only and guarded-output sections may read declared inputs, enum members, and compiler-owned host facts, but may not read workflow-local bindings, emitted output fields, or undeclared runtime names. (From: R1, R2)
- Keep Slice A narrow: `current none` is the only currentness form inside the route-only slice, route-only conditional readback stays out of `trust_surface`, and Slice A must not silently widen into portable currentness, invalidation, obligations, lenses, concerns, or packet-like coordination surfaces. (From: R1, R2)
- Preserve fail-loud law rules: every active leaf branch resolves exactly one current-subject form, route statements require both a label and explicit target, and the route-only slice may resolve either no semantic route or exactly one semantic route after conditions are evaluated. (From: R1, R2)
- Keep rendering honest and layered: workflow prose, law activation/currentness/stop-route consequences, and output schema must remain distinct in rendered `AGENTS.md`, and `standalone_read` must not overpromise guarded detail that would be absent when a guard is false. (From: R1, R2)
- Treat the route-only ladder as staged proof-teaching material rather than untouchable authority: `30` is narrow setup, `40` is local ownership, `41` is reroute handoff, and `42` is the capstone; fix illustrative mistakes instead of changing the language to accommodate them. (From: R1, R2, R3)
- When docs, examples, refs, and implementation disagree, trust `doctrine/` and manifest-backed cases, then repair the downstream surfaces to match. A checked-in ref is not proof on its own. (From: R3)
- Keep the current proof burden honest: the route-only ladder does not yet provide integrated active proof for routed `next_owner` agreement or for `standalone_read` guard discipline, so later core-planning commands must account for that missing work explicitly rather than assuming it is already solved. (From: R1, R2, R3)
- Keep `review` work explicitly deferred: future review ideas may be recorded as staged design constraints, but they must not drive current parser/compiler implementation or broaden the shipped language surface in this plan. (From: R1, R2)
- Keep the example corpus narrow and single-surface: add one new idea per example, do not add new language primitives just to paper over a bad example, and keep shipped manifests as the active proof lane. (From: R3)

## Instruction-bearing structure (only when present; preserve exact or equivalent operational form)
### R1 — Spec 1.3 Proposal
1. Freeze decisions:
   - Keep Doctrine's declaration skeleton.
   - Keep `workflow` as the semantic home.
   - Keep rich produced-contract material on `output`.
   - Ship the route-only slice as `workflow` + `law` + rich `output`.
   - Do not ship a top-level `review` primitive as part of the current Layer 1 workflow-law family.
2. Corrections that remain binding:
   - Example 1 must not duplicate output-shape requirements inside workflow law.
   - Example 3 was too early to present as compiler-owned and stays staged design work.
3. Slice A semantic contract to preserve:
   - No specialist artifact is current on route-only turns.
   - `current none` is the only currentness form in the route-only slice.
   - Guarded output sections are keyed/titled `output`-owned surfaces.
   - Route-only output guards have a narrowed expression namespace.
   - Route-only branches may stay local or resolve exactly one semantic route.
   - `next_owner` must agree with the routed target when a route is present.
   - `standalone_read` must not promise guarded detail when a guard is false.
4. Slice B / staged review constraints:
   - Do not ship `review` now.
   - If review is revisited later, keep `workflow` + `law` + `output` as the active semantic home for the adjacent coordination problems.
   - Keep downstream mode on declared outputs, not in route syntax.
   - Keep any future review-output coupling compiler-owned, not prose-only convention.
5. Outstanding implementation burden named by the proposal:
   - Align examples `30`, `39`, `40`, `41`, and `42` to the corrected Slice A contract.
   - Carry Slice A into integrated active proof for route/output agreement and `standalone_read` guard discipline when compiler work is ready.
   - Keep Example 3 out of parser/compiler work for now.
- Hard negatives:
  - Do not smuggle a second coordination language into the core.
  - Do not widen Slice A with non-earned primitives.
  - Do not treat staged review design as shipped truth.
- Escalation or branch conditions:
  - If review is revisited later, do so only after a stronger public proof pass and with explicit output/route coupling rules.

### R2 — Workflow Law
1. Mental model:
   - Authored workflow prose explains the job in human language.
   - `law` decides local truth for the current turn.
   - `output` plus `trust_surface` decide portable downstream truth.
   - `standalone_read` is human-facing companion prose, not an extra semantic plane.
2. Shipped surface:
   - `law` is a reserved child surface on `workflow`.
   - `trust_surface` is a reserved child surface on `output`.
   - Keyed guarded sections widen `output` record bodies.
   - Shipped statement families include activation/selection, currentness, scope/preservation, evidence roles, invalidation, control flow, and law reuse.
3. Validation and render rules that later planning must preserve:
   - Active leaf branches resolve exactly one current-subject form.
   - Carriers for `current artifact ... via ...` must point at emitted trusted output fields.
   - Guarded sections render as conditional shells in compiled `AGENTS.md`.
   - Law reuse relies on named subsections with explicit `inherit` / `override`.
4. Example-ladder positioning:
   - Read examples `30` through `42` in order.
   - The route-only story is intentionally staged and currently does not yet claim integrated active proof for `next_owner` agreement or `standalone_read` overpromising guarded detail.
- Hard negatives:
  - No packet primitive or free-floating coordination token model.
  - No top-level reusable `law` declaration.
  - No targetless `route`.
  - No separate `review` primitive in shipped workflow law today.

### R3 — Examples Overview
1. Corpus role:
   - The examples are both the language teaching surface and the verification corpus.
   - `prompts/`, `cases.toml`, `ref/`, and `build_ref/` each serve distinct proof/teaching roles.
2. Reading and ladder order:
   - Read examples in numeric order.
   - For workflow law, start with `docs/WORKFLOW_LAW.md` and then the ladder from `30` through `42`.
3. Important rules:
   - A checked-in ref file is not proof on its own.
   - If docs and examples disagree, trust `doctrine/` and the manifest-backed cases.
   - Keep new examples narrow: one new idea at a time.
   - Do not add new language primitives to rescue bad examples.
   - Keep shipped manifests as the active proof surface.
4. Existing verification commands:
   - `make verify-examples`
   - targeted `uv run --locked python -m doctrine.verify_corpus --manifest ...`
   - example emit commands for configured targets
- Hard negatives:
  - Do not let refs replace manifests as proof.
  - Do not let advisory review lanes replace the single active corpus.

## Planning notes from folded references (non-authoritative; not a phase plan)
### Global notes
- Keep proposal freeze decisions and shipped workflow-law docs aligned with compiler-owned semantics, not with illustrative drift. (From: R1, R2)
- Any example/doc/ref correction must preserve the manifest-backed proof model and must not justify new language primitives just to save bad examples. (From: R1, R3)
- Keep `review` explicitly out of the current parser/compiler implementation plan even if staged review material remains referenced. (From: R1, R2)

### Core implementation notes
- Potentially relevant obligations:
  - Enforce the narrowed Slice A semantic boundary and keep `current none` as the only route-only currentness form. (From: R1, R2)
  - Preserve the narrowed output-guard namespace and fail-loud route/currentness rules. (From: R1, R2)
  - Make rendering reflect the intended layered law/output split and guarded-shell behavior. (From: R1, R2)
  - Account explicitly for the still-missing integrated proof around routed `next_owner` agreement and `standalone_read` guard discipline. (From: R1, R2, R3)
- References:
  - R1, R2, R3

### Docs, examples, and refs notes
- Potentially relevant obligations:
  - Align examples `30`, `39`, `40`, `41`, and `42` to the corrected Slice A contract. (From: R1)
  - Keep the route-only ladder staged and narrow rather than turning examples into parallel semantics. (From: R2, R3)
  - Repair rendered refs and explanatory docs so they match the corrected implementation and the manifest-backed proof burden. (From: R1, R2, R3)
- References:
  - R1, R2, R3

### Editor alignment notes
- Potentially relevant obligations:
  - Align editor highlighting and click-through behavior to the shipped grammar and reference forms after Slice A convergence, not to stale example syntax or stale docs. (From: R1, R2, R3)
  - Keep the extension as an adapter of compiler-owned Doctrine rules rather than a second policy owner. (From: R1, R2)
- References:
  - R1, R2, R3

## Folded sources (verbatim; inlined so they cannot be missed)
### R1 — Spec 1.3 Proposal — docs/PROPOSAL_SPEC1_3.md
~~~~markdown
This revision hardens **Example 1** into a real Layer 1 spec slice and keeps
**Example 3** only as staged design work.

The freeze decisions behind this revision are:

* keep Doctrine's declaration skeleton
* keep `workflow` as the semantic home
* keep rich produced-contract material on `output`
* ship the route-only slice as `workflow` + `law` + rich `output`
* do **not** ship a top-level `review` primitive as part of the current Layer 1
  workflow-law family

Two corrections from the earlier writeup matter here.

First, **Example 1 must not duplicate output-shape requirements inside workflow
law**. The route-only comment contract belongs on `output`.

Second, **Example 3 was too early to present as if it had already earned full
compiler ownership**. The shipped docs still say Doctrine does not currently
ship a separate `review` primitive, and this revision now treats that as
binding.   

---

# Spec slice A - Example 1: `RouteOnlyTurns`

## 1. Purpose

This slice formalizes the route-only prose family: turns where **no specialist artifact is current**, the turn exists only to keep ownership honest, and the emitted comment must normalize the route state, next owner, next step, and any conditional route-only readback such as repeated-problem detail or rewrite-mode detail. This is exactly the semantic bundle the Lessons bucket analysis called out in `RouteOnlyTurns`: branch activation, output-shape law, deferred ownership implications, and fallback routing.  

## 2. Design boundary

This slice is intentionally narrow.

It does **not** introduce portable currentness, trust carriers, `invalidate`,
obligations, `lens`, `concern`, or any packet-like coordination surface. The
only currentness form here is `current none`. The output contract remains an
ordinary rich `output`, and the workflow law remains an ordinary `law:` child
inside `workflow`.

This slice also keeps route-only readback deliberately out of `trust_surface`.
Facts such as rewrite-mode detail or repeated-problem detail remain authored
comment readback, not portable currentness.  

## 3. Surfaces used

No new top-level declaration is introduced.

This slice uses:

* existing `input`
* existing `output`
* existing `workflow`
* existing `agent`
* existing explicit `route "..." -> Agent`
* a `law:` child block on `workflow`
* existing rich output-contract material on `output`
* one new keyed conditional output-section form:
  `<section_key>: "Title" when expr:` inside `output`  

## 4. Normative syntax

### 4.1 Output contract additions used by this slice

```ebnf
output_record_item     ::= record_item
                         | guarded_output_section

guarded_output_section ::= CNAME ":" string "when" expr ":" NEWLINE
                           INDENT record_item+ DEDENT
```

`guarded_output_section` is a keyed/titled output section.

Its key is the stable identity used for uniqueness, addressing, and explicit
patching. Its title is the rendered heading. The form is legal anywhere an
ordinary keyed section is legal inside an `output`-owned record body. It is not
a general record-language feature outside `output` surfaces.

### 4.2 Workflow law subset used by this slice

```ebnf
law_block             ::= "law" ":" NEWLINE INDENT route_only_stmt+ DEDENT

route_only_stmt       ::= active_when_stmt
                        | current_none_stmt
                        | stop_stmt
                        | route_stmt
                        | when_stmt

active_when_stmt      ::= "active when" expr
current_none_stmt     ::= "current none"
stop_stmt             ::= "stop" [string]
route_stmt            ::= "route" string "->" agent_ref ["when" expr]
when_stmt             ::= "when" expr ":" NEWLINE INDENT route_only_stmt+ DEDENT
```

## 5. Static semantics

1. Every active branch in this slice must resolve to exactly one currentness outcome. Since this is the route-only slice, that outcome must be `current none`.

2. A branch may not contain both `current none` and any artifact-currentness statement.

3. `current none` is the only currentness form that does **not** require a carrier output field.

4. `route` requires both a rendered label string and an explicit target agent. No targetless or unlabeled form is valid.

5. A guarded output section is part of the output contract, not workflow law.
Its key is the stable section identity. When its guard is true, every field
inside that section becomes required output content for that turn.

6. Guards on route-only output sections may read only:
   declared `input`s, `enum` members, and compiler-known host facts derived
   from those surfaces.

7. Guards on route-only output sections may **not** read workflow-local law
   bindings such as `mode` names, may **not** read emitted output fields, and
   may **not** read undeclared runtime names.

8. An active route-only branch may resolve either:
   - no semantic route, in which case ownership stays local, or
   - exactly one semantic route after branch conditions are evaluated.

9. If an active route-only branch resolves a semantic route and the emitted
   output includes a field keyed `next_owner`, that field must agree with the
   routed target agent.

10. Route-only conditional readback does not participate in `trust_surface`
    for this slice. `standalone_read` may describe the branch-level readback
    contract, but it must not promise guarded detail that would be absent when
    the guard is false.

11. Output requirements declared on `RouteOnlyHandoffOutput` are not repeated
    inside workflow law. The workflow decides **when** the route-only branch is
    in force; the output decides **what** must be said.  

## 6. Render semantics

The compiler should render this slice in four layers:

1. human preamble prose from `workflow`
2. route-only activation summary from `law`
3. stop and route consequences from `law`
4. routing-comment schema from `output`

There are two render modes to keep separate:

* **Compiled static-doc render**: a guarded output section may render as a
  conditional shell with wording such as "Rendered only when ...".
* **Runtime required-content semantics**: the section is present and required
  only when its guard is true.

`current none` renders as plain human prose such as "There is no current
specialist artifact for this turn." That is the whole point of the route-only
slice: make "no durable artifact is current" explicit without inventing fake
current truth.  

## 7. Canonical positive example

```prompt
input RouteFacts: "Route Facts"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use host-provided route facts that say what live job is in force, whether the current specialist output is missing, whether the next owner is still unclear, whether the section is new or full rewrite, whether a critic miss repeated, what the next concrete step is, what keeps failing, which role returned the issue, and what the next concrete fix is."


output RouteOnlyHandoffOutput: "Routing Handoff Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    must_include: "Must Include"
        current_route: "Current Route"
            "Say the route-only state now in force, including whether the turn is routing, process repair, or owner repair."

        next_owner: "Next Owner"
            "Name the next owner when ownership is changing now. If ownership stays local, say plainly that it stays local. If the earliest clear owner is still unclear, say plainly that RoutingOwner keeps the issue."

        next_step: "Next Step"
            "Say the next concrete step now."

    rewrite_mode: "Rewrite Mode" when RouteFacts.section_status in {"new", "full_rewrite"}:
        "Say plainly that later section metadata must be rewritten instead of inherited."

    repeated_problem: "Repeated Problem" when RouteFacts.critic_miss_repeated:
        failing_pattern: "What Keeps Failing"
            "Say what keeps failing."

        returned_from: "Returned From"
            "Say which role returned it."

        next_fix: "Next Concrete Fix"
            "Say the next concrete fix."

    standalone_read: "Standalone Read"
        "A downstream owner should be able to read this comment alone and understand that no specialist artifact is current, what route-only state is now in force, who owns next, and what the next concrete step is."


agent RoutingOwner:
    role: "Own explicit reroutes when specialist work cannot continue safely."
    workflow: "Instructions"
        "Take back the same issue when the next specialist owner is still not justified."


workflow RouteOnlyTurns: "Routing-Only Turns"
    "Handle turns that can only stop, reroute, or keep ownership explicit."

    law:
        active when RouteFacts.live_job in {"routing", "process_repair", "owner_repair"} and RouteFacts.current_specialist_output_missing
        current none
        stop "No specialist artifact is current for this turn."

        route "Keep the issue on RoutingOwner until the next specialist owner is actually justified." -> RoutingOwner when RouteFacts.next_owner_unknown


agent RouteOnlyTurnsDemo:
    role: "Keep route-only work explicit when no specialist artifact is current."
    workflow: RouteOnlyTurns
    inputs: "Inputs"
        RouteFacts
    outputs: "Outputs"
        RouteOnlyHandoffOutput
```

## 8. Intended render

```md
Keep route-only work explicit when no specialist artifact is current.

## Inputs

### Route Facts
Use host-provided route facts that say what live job is in force, whether the current specialist output is missing, whether the next owner is still unclear, whether the section is new or full rewrite, whether a critic miss repeated, what the next concrete step is, what keeps failing, which role returned the issue, and what the next concrete fix is.

## Routing-Only Turns

Handle turns that can only stop, reroute, or keep ownership explicit.

This pass runs only when the live job is routing, process repair, or owner repair and no specialist artifact is current.

There is no current specialist artifact for this turn.

Stop: No specialist artifact is current for this turn.

If the next specialist owner is still unclear, keep the issue on RoutingOwner until a specialist owner is actually justified.

## Outputs

### Routing Handoff Comment

#### Must Include

##### Current Route
Say the route-only state now in force, including whether the turn is routing, process repair, or owner repair.

##### Next Owner
Name the next owner when ownership is changing now. If ownership stays local, say plainly that it stays local. If the earliest clear owner is still unclear, say plainly that RoutingOwner keeps the issue.

##### Next Step
Say the next concrete step now.

#### Rewrite Mode
Rendered only when the section is new or full rewrite.

Say plainly that later section metadata must be rewritten instead of inherited.

#### Repeated Problem
Rendered only when the same critic miss repeated.

##### What Keeps Failing
Say what keeps failing.

##### Returned From
Say which role returned it.

##### Next Concrete Fix
Say the next concrete fix.

#### Standalone Read
A downstream owner should be able to read this comment alone and understand that no specialist artifact is current, what route-only state is now in force, who owns next, and what the next concrete step is.
```

Current proof note:

The active numbered route-only ladder now teaches the split ownership outcomes,
keyed guarded output sections, and the canonical capstone render. It does not
yet provide integrated active proof for rule 9 or for `standalone_read`
overpromising guarded detail when a guard is false. Those remain part of the
Slice A design target, but not yet part of the active numbered proof burden.

## 9. Invalid examples

### 9.1 Active route-only branch without currentness

```prompt
workflow InvalidRouteOnlyTurns: "Routing-Only Turns"
    law:
        active when RouteFacts.current_specialist_output_missing
        stop "No specialist artifact is current for this turn."
```

**Error:** `E331`
Every active branch must resolve to one currentness outcome. In this slice, that must be `current none`.

### 9.2 Conflicting currentness in the same branch

```prompt
workflow InvalidRouteOnlyTurns: "Routing-Only Turns"
    law:
        active when RouteFacts.current_specialist_output_missing
        current none
        current artifact SectionMetadata via CoordinationHandoff.current_artifact
```

**Error:** `E332`
A branch may not declare both `current none` and artifact currentness.

### 9.3 Route without label

```prompt
workflow InvalidRouteOnlyTurns: "Routing-Only Turns"
    law:
        current none
        route -> RoutingOwner
```

**Error:** `E131`

### 9.4 Route without target

```prompt
workflow InvalidRouteOnlyTurns: "Routing-Only Turns"
    law:
        current none
        route "Keep the issue on Project Lead." ->
```

**Error:** `E132`

## 10. What this slice deliberately does not solve

It does not solve portable current truth, trust carriers, invalidation, or typed owed-now propagation. Those belong to the Example 2 family, where `law` and `output` are coupled by explicit carriers such as `current artifact X via Output.field`. Route-only work is the one honest case where `current none` is enough.  

---

# Spec slice B - Example 3: staged `review` design, not Layer 1

## 1. Status

This slice is **not** part of the current Layer 1 workflow-law surface.

The shipped docs already say Doctrine does not currently ship a separate
`review` primitive, and this revision now treats that as binding. Example 3
therefore remains staged design work, not a fully formed core-language spec.

## 2. Freeze decisions for the staged design

If review is revisited later, these decisions should be treated as frozen
starting points rather than reopened from scratch.

1. Do **not** ship `review` as Layer 1 now.

2. Keep `workflow` + `law` + `output` as the active semantic home for route-only
   review turns, blocked review turns, currentness, and portable truth.

3. If a later `review` surface exists, `contract:` should point only to a
   declared review-contract `workflow`, not to arbitrary "workflow-like"
   surfaces.

4. `contract.passes` should be a compiler-known derived fact over that
   referenced review-contract workflow, not a freeform magic property.

5. An agent should define **either** `workflow:` or `review:`, not both.
   `review:` should render where a normal authored workflow body would render.

6. If `review` ships at all, its semantic verdicts should be compiler-owned
   `accept` and `changes_requested`, not merely friendly prose labels.

7. If `review` ships at all, accept and reject routing should be ordered,
   first-match-wins, and total. `else` should be required unless exhaustiveness
   is statically provable.

8. Blocked or unclear review turns should stay outside `review`. They should be
   expressed with ordinary `workflow` / `law` or with a separate route-only
   review workflow.

9. Downstream mode should not travel in route syntax. If downstream mode is
   semantically required, it should travel on a declared output surface.

10. `use_now` is removed from the staged review slice. If later review work
    needs to carry real current truth, it must integrate with the existing
    portable-currentness model:
    `current artifact ... via ...` plus `trust_surface`.

## 3. What a future narrow `review` surface would own

If review returns later, it should stay small.

It should own only:

* reviewed subject selection
* one referenced review contract
* labeled reject gates
* one accept gate
* preserved truths the reviewer must confirm
* route-on-accept
* route-on-reject
* coupling to one declared comment output

It should **not** own:

* blocked or unclear-turn handling
* portable currentness
* route payloads
* full verdict-comment schema
* packet-like coordination state

The verdict-comment schema should remain on `output`, because Doctrine still
treats `output` as the one produced-contract primitive.

## 4. Minimal staged shape if review is revisited later

This is a design sketch, not normative grammar:

```prompt
review CopyReview: "Copy Review"
    subject: CopyManifestFileOutput
    contract: CopyGroundingReviewContract
    comment_output: CriticVerdictOutput

    reject "Producer handoff is invalid." when handoff.invalid
    reject "Unnamed support was treated as current truth." when current_truth.from_unnamed_support

    preserve LessonSituationsFileOutput.exact_move_boundary

    accept "Shared copy review contract passes." when contract.passes

    on accept:
        ...

    on reject:
        ...
```

If that surface is ever promoted, its comment output should carry at least:

* `verdict`
* `reviewed_artifact`
* `analysis_performed`
* `output_contents_that_matter`
* `next_owner`

If it can reject, it should also carry failure-only detail such as:

* `failing_gates`
* `owner_of_fix`
* `exact_file`
* `exact_check`

Any emitted `verdict` or `next_owner` field would need to agree with the
compiler-owned review outcome and routed next owner. That agreement should not
be left as a prose-only convention.

## 5. Why this slice is deferred

The route-only family already fits the shipped Doctrine pattern:
`workflow` + `law` + rich `output`.

The review family does not yet have the same earnedness. The open questions
were not mere wording gaps; they pointed at real undecided compiler surfaces:

* slot model
* inheritance model
* routing-case grammar
* verdict/output coupling
* public proof burden for promotion

So the corrected position is:

* **Example 1** is a real Layer 1 candidate.
* **Example 3** is staged design work and should not drive parser/compiler work
  yet.

---

## The short design theorem behind this revision

* **Example 1** is now a real Layer 1 candidate: no current artifact, explicit
  stop/reroute law, strict expression boundaries, keyed guarded output
  sections, and rich route-comment normalization on `output`.
* **Example 3** is no longer presented as if it were a finished Layer 1 slice.
  It remains staged design work until Doctrine is ready to give review the same
  level of compiler ownership that `workflow` + `law` + `output` already have.

That keeps the document aligned with Doctrine's actual center of gravity:
formalize recurring law inside existing structures, keep seam identity and tone
as prose, widen only when the compiler owns the meaning, and do not smuggle a
second coordination language into the core.

The natural next move is:

1. keep aligning `30`, `39`, `40`, `41`, and `42` to this corrected Slice A
   contract
2. carry Slice A into integrated active proof for route/output agreement and
   `standalone_read` guard discipline when compiler work is ready
3. keep Example 3 out of parser/compiler implementation work for now
4. revisit review only after a stronger public proof pass

---

## Remaining Unresolved Issues

There are no remaining Slice A design questions blocking prep in this
document.

What remains for Slice A is implementation and integrated proof work that the
current numbered corpus does not yet carry:

1. **How should active proof enforce route/output agreement for `next_owner`?**

   Rule 9 is part of the Slice A design target, but the current numbered corpus
   does not yet carry an integrated active negative that proves the emitted
   `next_owner` field agrees with the routed target when a semantic route is
   present.

2. **How should active proof enforce `standalone_read` guard discipline?**

   Rule 10 is part of the Slice A design target, but the current numbered
   corpus does not yet carry an integrated active negative that proves
   `standalone_read` does not promise guarded detail when the guard is false.

The remaining strategic questions beyond that are about any future promotion of
**Slice B**:

1. **Where should review be proved next before any core promotion?**

   I can recommend a public proving ground such as a Layer 3 code-review pack,
   because the repo's current docs already point in that direction. What I
   cannot settle from repo evidence alone is whether you want that proof burden
   to happen there first, or whether you want a narrower private/example-only
   proof cycle before any public-pack work.

2. **If a future `review` primitive is promoted, how should semantic verdict and route facts bind to output fields without relying on magic field names?**

   This revision freezes the requirement that emitted `verdict` and `next_owner`
   must agree with compiler-owned outcomes when review exists. What I cannot
   settle cleanly from current Doctrine evidence alone is the exact binding
   mechanism:
   - fixed canonical field keys such as `verdict` and `next_owner`, or
   - a small explicit mapping surface on `output`

   Doctrine currently prefers explicitness over magic, but it does not yet have
   a shipped pattern for this exact kind of semantic-output coupling outside the
   portable-currentness carrier model.
~~~~

### R2 — Workflow Law — docs/WORKFLOW_LAW.md
~~~~markdown
# Workflow Law

Doctrine workflow law is the shipped typed surface for turns that need explicit
branch truth, not just ordinary workflow prose.

Use it when a turn needs any of these behaviors:

- an explicit activation trigger
- one active mode or one active branch at a time
- one current artifact per active leaf branch, or explicitly no current artifact
- narrow write authority with preserved truth outside the owned scope
- comparison-only support or rewrite-evidence exclusions
- invalidation when upstream structural truth moves
- stop lines and honest reroute

If you are learning the feature family, start here and then read the active
example ladder in [`examples/30_*` through `examples/42_*`](../examples/README.md).

## Mental Model

- Authored workflow prose still explains the job in human language.
- `law` inside `workflow` decides what is true now for the current turn.
- `output` still decides what the turn emits.
- keyed guarded sections inside `output` keep conditional readback on the
  output contract instead of creating a second control plane
- `trust_surface` inside `output` names the emitted fields a downstream owner
  must be able to read and trust.
- `standalone_read` is the human-facing companion to `trust_surface`. It does
  not create semantics beyond the emitted fields and carrier rules the compiler
  validates.

The core split is:

- `law` decides local truth.
- `output` plus `trust_surface` decide portable downstream truth.

## Shipped Surface

Workflow law does not add a new top-level declaration family.

It adds two reserved child surfaces on existing owners:

- `law` on `workflow`
- `trust_surface` on `output`

It also widens normal `output` record bodies with keyed guarded sections:

```prompt
output RouteOnlyHandoffOutput: "Route-Only Handoff Output"
    ...
    rewrite_mode: "Rewrite Mode" when RouteFacts.section_status in {"new", "full_rewrite"}:
        "Name whether the section is brand new or undergoing a full rewrite."
```

Guarded output sections are still output-owned authored fields:

- they render as documented conditional shells in compiled `AGENTS.md`
- they are required only when the guard is true at runtime
- their guards may read declared inputs, enum members, and compiler-owned host
  facts rooted there
- they may not read workflow-local bindings, emitted output fields, or
  undeclared runtime names

The shipped statement families are grouped by job:

- branch activation and selection:
  `active when`, `when`, `mode`, `match`, `must`
- currentness:
  `current artifact ... via ...`, `current none`
- scope and preservation:
  `own only`, `preserve exact`, `preserve structure`, `preserve decisions`,
  `preserve mapping`, `preserve vocabulary`, `forbid`
- evidence roles:
  `support_only ... for comparison`,
  `ignore ... for truth|comparison|rewrite_evidence`
- truth transitions:
  `invalidate ... via ...`
- control flow:
  `stop`, `route "..." -> Agent`
- reuse:
  named law subsections plus `inherit` / `override`

## Branch Activation And Selection

Use `active when` to gate the whole workflow-law path for a turn, then `when`
or `match` to shape narrower branches under it.

```prompt
law:
    active when CurrentHandoff.owes_metadata_polish

    mode pass_mode = CurrentHandoff.active_mode as MetadataPolishMode

    match pass_mode:
        MetadataPolishMode.manifest_title:
            ...

        MetadataPolishMode.section_summary:
            ...
```

Key rules:

- `mode` binds one expression to one enum.
- `match` on an enum must be exhaustive or include `else`.
- `must` is the fail-loud surface for branch-local required facts.
- active law is evaluated per leaf branch, not as one flat list.

## Currentness And Trust Carriers

`current artifact ... via ...` means two things at once:

- the named input or output is authoritative now for the active branch
- the `Output.field` carrier tells the next owner that this is true

```prompt
output CoordinationHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    trust_surface:
        current_artifact

law:
    current artifact SectionMetadata via CoordinationHandoff.current_artifact
```

Route-only or block-only turns use `current none` instead:

```prompt
law:
    when CurrentHandoff.missing:
        current none
        stop "Current handoff is missing."
        route "Route the same issue back to RoutingOwner." -> RoutingOwner
```

Currentness rules:

- every active leaf branch must resolve exactly one current-subject form
- that form must be either `current artifact ... via ...` or `current none`
- the carrier side must point at an emitted output field
- that field must be listed in the output's `trust_surface`
- if the current artifact is itself an output root, the concrete turn must emit
  that output

## Scope And Preservation

Workflow law is how Doctrine makes narrow edit authority explicit.

```prompt
law:
    own only {SectionMetadata.name, SectionMetadata.description}
    preserve exact SectionMetadata.* except {SectionMetadata.name, SectionMetadata.description}
    preserve decisions ApprovedStructure
    forbid {SectionMetadata.taxonomy, SectionMetadata.flags}
```

Use these statements for different jobs:

- `own only` marks the writable scope for the active branch
- `preserve exact` protects the rest of the current artifact unless explicitly
  excepted
- `preserve structure`, `preserve decisions`, `preserve mapping`, and
  `preserve vocabulary` protect other declared truths that must stay stable
- `forbid` blocks narrow scope that the role must not modify

Compiler-owned checks keep this honest:

- owned paths must stay rooted in the current artifact
- owned paths must stay addressable
- owned scope cannot overlap exact preservation without an explicit `except`
- owned scope cannot overlap forbidden scope

## Evidence Roles

Not every supporting input is equal. Workflow law distinguishes comparison help
from truth and rewrite evidence.

```prompt
law:
    support_only AcceptedPeerSet for comparison

    ignore PrimaryManifest.title for rewrite_evidence when pass_mode == MetadataPolishMode.manifest_title and CurrentHandoff.rewrite_regime == RewriteRegime.rewrite
```

Use these rules when a turn needs to say:

- this artifact may guide comparison but must not become current truth
- this old wording no longer counts as rewrite evidence on rewrite passes

The shipped basis roles are:

- `truth`
- `comparison`
- `rewrite_evidence`

## Invalidation, Stop, And Route

Invalidation is a first-class truth transition.

```prompt
law:
    when CurrentHandoff.structure_changed:
        invalidate SectionReview via RewriteAwareCoordinationHandoff.invalidations
        stop "Structure moved; downstream review is no longer current."
        route "Route the same issue back to RoutingOwner for rebuild." -> RoutingOwner
```

This does not delete the artifact. It says the artifact is no longer portable as
current truth and that downstream owners must be able to see that loss of
authority on the declared carrier.

Common pattern:

- invalidate the no-longer-current artifact
- stop the current lane
- route back to an owner that can rebuild or reroute honestly

## Law Reuse Through Named Subsections

Inherited workflows patch `law` the same way Doctrine patches other compiler-
owned structure: explicitly and exhaustively.

```prompt
workflow RewriteAwareMetadataPolish[BaseMetadataPolish]: "Metadata Polish"
    law:
        inherit activation
        inherit mode_selection
        inherit scope

        override currentness:
            ...

        override evidence:
            ...

        override stop_lines:
            ...
```

Rules:

- reusable inherited `law` must be split into named subsections
- inherited children must account for every inherited subsection exactly once
- `override <section_key>:` must target a real parent subsection
- inherited law cannot mix bare statements with subsection patch entries

## Rendering Model

Rendered `AGENTS.md` stays human-first.

Workflow law compiles into plain English such as:

- which mode is active
- which artifact is current now
- what scope is owned
- what truth must be preserved
- what is comparison-only support
- what is no longer current
- when the role must stop or reroute

The language stays Doctrine-native:

- authors still write ordinary workflow prose for mission and tone
- the compiler owns law semantics, ordering, and fail-loud validation
- outputs still render as normal output contracts with readable `trust_surface`,
  guarded conditional shells, and `standalone_read` sections

## Example Ladder

The active examples are intended to be read in order:

The route-only story is staged on purpose:

- `30` introduces the narrow law surface
- `40` and `41` split the local-ownership and reroute outcomes on whether the
  next owner is still unknown
- `42` recombines those ideas into the full route-only handoff capstone

- `30_law_route_only_turns`: narrow route-only setup with `current none`,
  `stop`, and explicit reroute
- `31_currentness_and_trust_surface`: portable currentness through emitted
  carrier fields and trusted output surfaces
- `32_modes_and_match`: enum-backed `mode`, exhaustive `match`, and one current
  subject per branch
- `33_scope_and_exact_preservation`: `own only`, `preserve exact`, and narrow
  scope contradiction checks
- `34_structure_mapping_and_vocabulary_preservation`: non-exact preservation
  families for structure, mapping, and vocabulary
- `35_basis_roles_and_rewrite_evidence`: comparison-only support and rewrite-
  evidence exclusions
- `36_invalidation_and_rebuild`: invalidation as a truth transition and the
  rebuild pattern
- `37_law_reuse_and_patching`: named law subsections plus inherited explicit
  patching
- `38_metadata_polish_capstone`: the full portable-truth model across modes,
  carriers, scope, preservation, evidence, invalidation, and reroute
- `39_guarded_output_sections`: output-owned keyed guarded sections, nested
  guarded readback, and the narrowed output-guard namespace
- `40_route_only_local_ownership`: local-ownership branch of the route-only
  slice with `current none` when ownership stays local because reroute is not
  justified
- `41_route_only_reroute_handoff`: explicit reroute branch of the route-only
  slice when the next owner is still unknown, paired with a handoff comment
  contract
- `42_route_only_handoff_capstone`: the full generic Slice A route-only
  handoff model with conditional reroute and guarded output readback

The route-only ladder teaches the split ownership outcomes and rendered output
contracts. It does not yet claim integrated active proof for `next_owner`
agreement with the routed target or for `standalone_read` overpromising guarded
detail.

## Not Shipped

Doctrine intentionally does not ship these features in workflow law today:

- a packet primitive or free-floating coordination token model
- a top-level reusable `law` declaration family
- targetless `route`
- `obligation`, `lens`, `concern`, or `current status`
- nominal artifact typing as a separate declaration kind
- basis roles beyond `truth`, `comparison`, and `rewrite_evidence`
- `let`
- a separate `review` primitive

If those ideas return later, they need to strengthen the same core model rather
than open a second coordination language.

## Related Docs

- [Why Doctrine](WHY_DOCTRINE.md)
- [Language Design Notes](LANGUAGE_DESIGN_NOTES.md)
- [Agent I/O Design Notes](AGENT_IO_DESIGN_NOTES.md)
- [Compiler Errors](COMPILER_ERRORS.md)
- [Examples](../examples/README.md)
~~~~

### R3 — Examples Overview — examples/README.md
~~~~markdown
# Examples

The examples are both the language teaching surface and the verification corpus.

Each numbered example may contain:

- `prompts/`: authored `.prompt` source
- `cases.toml`: manifest-backed proof used by `doctrine.verify_corpus`
- `ref/`: checked-in expected render or error output
- `build_ref/`: checked-in emitted tree output when the emit pipeline matters

Read the examples in numeric order. The sequence is intentional.

For the shipped workflow-law model behind examples `30` through `42`, start
with [../docs/WORKFLOW_LAW.md](../docs/WORKFLOW_LAW.md).

## Reading Order

- `01` through `06`: core agent and workflow syntax, imports, inheritance, and
  explicit patching
- `07` through `14`: authored slots, routing, typed inputs and outputs, skills,
  role-home composition, and handoff truth
- `15` through `20`: readable refs, interpolation, and richer authored prose
  surfaces
- `21` through `26`: first-class block reuse, inheritance, and abstract
  authored-slot requirements
- `27` through `29`: addressable nested items, recursive workflow paths, and
  enums for closed vocabularies
- `30` through `42`: active workflow-law proof for route-only turns, portable
  currentness, trust carriers, scope and preservation law, basis roles,
  invalidation, law reuse, output-owned guarded readback, and the route-only
  handoff capstones

## Workflow Law Ladder

The route-only ladder is staged on purpose:

- `30` introduces the narrow setup
- `40` and `41` split the local and reroute ownership outcomes on whether the
  next owner is still unknown
- `42` combines them into the full route-only handoff capstone

- `30_law_route_only_turns`: narrow route-only setup with `current none`,
  `stop`, and explicit reroute
- `31_currentness_and_trust_surface`: one current artifact plus emitted trust
  carriers
- `32_modes_and_match`: enum-backed modes, exhaustive `match`, and one current
  subject per branch
- `33_scope_and_exact_preservation`: narrow ownership with exact preservation
  and overlap checks
- `34_structure_mapping_and_vocabulary_preservation`: preserve non-exact truth
  such as structure, mapping, and vocabulary
- `35_basis_roles_and_rewrite_evidence`: comparison-only support and rewrite-
  evidence exclusions
- `36_invalidation_and_rebuild`: invalidation as a truth transition plus the
  rebuild pattern
- `37_law_reuse_and_patching`: named law subsections with explicit inheritance
  and override rules
- `38_metadata_polish_capstone`: the full integrated portable-truth model
- `39_guarded_output_sections`: output-owned keyed guarded sections, nested
  guarded readback, and output-guard namespace limits
- `40_route_only_local_ownership`: local-ownership branch of the route-only
  slice with `current none` when reroute is not justified
- `41_route_only_reroute_handoff`: explicit reroute branch of the route-only
  slice when the next owner is still unknown, paired with an emitted handoff
  comment contract
- `42_route_only_handoff_capstone`: the full generic Slice A route-only
  handoff model with guarded conditional readback

The route-only ladder teaches the split ownership story and rendered contracts.
It does not yet claim integrated active proof for `next_owner` agreement with
the routed target or for `standalone_read` overpromising guarded detail.

## Important Rules

- A checked-in ref file is not proof on its own. The manifest is the proof
  surface.
- If docs and examples disagree, trust `doctrine/` and the manifest-backed
  cases.
- Keep new examples narrow: one new idea at a time.
- Do not add a new language primitive just to paper over a bad example.
- Keep the corpus single-surface: shipped manifests should stay active proof,
  not advisory review lanes.

## Useful Commands

Verify the whole active corpus:

```bash
make verify-examples
```

Verify one example manifest:

```bash
uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml
```

Emit configured example trees:

```bash
uv run --locked python -m doctrine.emit_docs --target example_07_handoffs
uv run --locked python -m doctrine.emit_docs --target example_14_handoff_truth
```
~~~~
<!-- arch_skill:block:reference_pack:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly, Doctrine will have one coherent shipped
implementation of the Slice A route-only workflow-law family such that:

- the grammar, parser, model/compiler, diagnostics, and renderer agree on the
  same route-only and guarded-output semantics
- the staged `review` design remains out of the shipped language surface
- the corrected examples and rendered refs demonstrate the shipped behavior
  instead of preserving illustrative mistakes
- the VS Code extension correctly colorizes the shipped syntax and resolves the
  link-click / go-to-definition behaviors users need for imports and shipped
  reference forms

and this will be demonstrable with the repo's shipped verification commands
instead of hand-waving over broken renders or editor behavior.

## 0.2 In scope

- Implementing the intended Slice A route-only workflow-law behavior from
  `docs/PROPOSAL_SPEC1_3.md` through the shipped Doctrine core.
- Carrying proposal rule 9 (`next_owner` agreement) and rule 10
  (`standalone_read` guard discipline) into the strongest honest
  compiler/proof surfaces this run can support without hidden heuristics.
- Tightening or correcting the workflow-law grammar, parser, model, compiler,
  diagnostics, and renderer wherever the current shipped implementation diverges
  from the intended Slice A contract.
- Correcting clear mistakes in the illustrative examples and their rendered
  reference output, especially in the workflow-law ladder around examples `30`
  through `42`.
- Aligning live docs that describe the shipped workflow-law surface when they
  drift from the corrected implementation.
- Fixing the VS Code extension's Doctrine language support so syntax highlighting
  and link-click / definition navigation work for the shipped language surface.
- Internal convergence work needed to remove duplicate or drifting truth between
  compiler semantics, renderer expectations, docs, examples, diagnostics, and
  editor support.

## 0.3 Out of scope

- Shipping a new top-level `review` primitive or treating the staged review
  design as parser/compiler scope now.
- Preserving hand-authored examples or rendered refs merely because they exist.
- Adding speculative language primitives, runtime shims, alternate renderers, or
  editor features beyond the behavior needed to support the shipped Doctrine
  surface, the requested VS Code colorizing/link clicks, and the smallest
  explicit structured contract, if one is truly required to carry proposal
  rule 9 honestly.
- Broad editor-product work such as rename, completion, hover docs, or full
  semantic language-server features unless deeper planning proves one is
  required for the requested link-click behavior.
- Reworking unrelated examples or editor behavior outside the corrected
  workflow-law and reference-navigation surface.

## 0.4 Definition of done (acceptance evidence)

- The Doctrine core implements the intended Slice A behavior coherently across
  `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`,
  `doctrine/model.py`, `doctrine/compiler.py`, `doctrine/renderer.py`, and
  `doctrine/diagnostics.py`.
- Proposal rule 9 (`next_owner` agreement) has compiler/proof coverage through
  an explicit structured surface rather than prose convention or hidden magic.
- Proposal rule 10 (`standalone_read` guard discipline) has the strongest honest
  manifest-backed proof the current language can support without prose parsing.
- The rendered output for the corrected route-only and guarded-output examples
  matches the intended contract instead of the current known-wrong rendering.
- Clear example mistakes have been corrected or replaced, and the active corpus
  proves the corrected behavior.
- The VS Code extension highlights the shipped syntax and resolves the intended
  import and definition/document-link navigation on the corrected language
  surface.
- The shipped verification signals run cleanly for the touched surfaces:
  `make verify-examples`, `make verify-diagnostics` when diagnostics change, and
  `cd editors/vscode && make`.

Behavior-preservation evidence:

- unchanged non-Slice-A examples and other shipped Doctrine surfaces still pass
  `make verify-examples`
- editor packaging/tests still pass through the existing VS Code extension build
  and test flow

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks, shims, or dual truth surfaces.
- `workflow` + `law` + rich `output` remain the semantic home for Slice A.
- `output` owns emitted comment schema and guarded readback; workflow law does
  not duplicate output-shape requirements.
- The staged `review` design remains staged and non-shipped.
- Examples are allowed to change to match the shipped language; the language is
  not allowed to warp itself around incorrect examples.
- The VS Code extension adapts compiler-owned Doctrine rules; it does not become
  an alternate grammar or policy owner.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Correct shipped language semantics over backward compatibility with
   illustrative drift.
2. Converge renderer, docs, examples, diagnostics, and editor behavior onto one
   compiler-owned contract.
3. Keep the workflow-law family human-readable and example-first without
   weakening fail-loud compiler boundaries.
4. Restore usable VS Code authoring ergonomics for the shipped surface.

## 1.2 Constraints

- The repo already ships workflow-law behavior in `doctrine/` and the examples
  corpus; implementation must preserve unrelated shipped behavior.
- The examples are useful but explicitly not perfect; they cannot be treated as
  untouchable goldens.
- The VS Code extension currently uses a TextMate grammar plus JS resolver
  helpers rather than a language server; the plan should improve the existing
  path before inventing a new editor stack.

## 1.3 Architectural principles (rules we will enforce)

- Compiler-owned semantics first; all other surfaces follow.
- Fail loud when behavior is invalid or unsupported.
- Prefer hard cutover and explicit deletes over compatibility layers.
- Reuse the existing VS Code extension architecture unless deeper planning shows
  it cannot support the required click-through behavior.

## 1.4 Known tradeoffs (explicit)

- Tightening the language around the proposal may require changing examples,
  refs, docs, and editor matching all at once, which broadens convergence scope
  but prevents long-lived drift.
- Keeping the extension on the current TextMate-plus-resolver path may limit how
  much editor intelligence ships in this scope, but it is the most credible
  existing canonical path for highlighting and definition/document-link support.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already ships workflow-law parsing, compilation, diagnostics,
verification, rendering, and a VS Code extension for Doctrine prompt files.
There is also a proposal doc for the intended Slice A semantics and an example
ladder for the workflow-law family.

## 2.2 What’s broken / missing (concrete)

- The intended behavior is not yet reliably reflected end to end in the shipped
  renderer output.
- The examples are illustrative and may encode mistakes that should not become
  language truth.
- The editor support exists but still needs working colorizing and click-through
  on the corrected shipped syntax.
- This creates drift risk across code, docs, examples, diagnostics, renders, and
  editor behavior.

## 2.3 Constraints implied by the problem

- The implementation must separate intended behavior from illustrative artifacts.
- The final plan must explicitly include convergence work across docs/examples
  and the VS Code extension, not only core compiler work.

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- None added in this pass. The research question here is canonical internal
  ownership for Spec 1.3 Slice A, and repo truth is already sufficient to name
  the right implementation boundary. The proposal and shipped docs remain
  folded product references, not external architecture owners.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/grammars/doctrine.lark` owns the shipped syntax surface for
    Slice A: `workflow ... law:`, `current artifact ... via ...`, `current
    none`, `stop`, law-owned `route`, `output ... trust_surface:`, and keyed
    guarded output sections. It also still ships a second `route_stmt` surface
    inside ordinary workflow sections, which is relevant drift for this work.
  - `doctrine/parser.py` is the syntax-to-AST boundary. `output_body()`
    collects ordinary output items separately from exactly one
    `trust_surface` block, `guarded_output_section()` builds
    `model.GuardedOutputSection`, `workflow_body()` enforces a single `law`
    block per workflow, `law_body()` and `law_route_stmt()` build the typed law
    tree, and `route_stmt()` still builds the older non-law `model.RouteLine`
    path. `parse_text()` and `parse_file()` are the only parse entry points,
    and `build_lark_parser()` depends on `doctrine/indenter.py` for
    indentation-sensitive parsing.
  - `doctrine/model.py` is the typed semantic shape for this family. The
    relevant ownership lives in `WorkflowBody.law`, `OutputDecl.items`,
    `OutputDecl.trust_surface`, `GuardedOutputSection`, `TrustSurfaceItem`, the
    `LawStmt` family, and `LawBody`. The same file also reveals a duplicate
    route representation through `RouteLine` in `SectionBodyItem`, which sits
    outside the law-owned path.
  - `doctrine/compiler.py` is the canonical semantic owner. The concrete-turn
    contract comes from `_resolve_agent_contract()`, which records the inputs
    and outputs actually wired by a concrete agent before any law validation.
    `_compile_output_decl()` validates guarded output sections, compiles
    `trust_surface`, and currently injects the compiled trust surface just
    before a keyed `standalone_read` section when present. `_compile_record_item()`
    renders guarded output sections as conditional shells. `_compile_resolved_workflow()`
    calls `_compile_workflow_law()` for workflow-law behavior, and
    `_validate_workflow_law()` plus `_collect_law_leaf_branches()` enforce the
    one-current-subject-per-active-leaf rule, owned-scope rules, invalidation
    conflicts, and route target validity. `_validate_current_artifact_stmt()`
    and `_validate_carrier_path()` enforce that currentness carriers come from
    emitted outputs and that their fields are listed in `trust_surface`.
  - `doctrine/compiler.py` also already contains the existing reusable
    guarded-section/addressable-path machinery. `_get_addressable_children()`,
    `_record_items_to_addressable_children()`, `_display_addressable_target_value()`,
    and `_resolve_output_field_node()` all treat
    `model.GuardedOutputSection` as an addressable titled node, which is the
    core reason guarded sections already stay addressable instead of being a
    renderer-only fiction.
  - `doctrine/compiler.py` still owns a second route rendering path outside
    workflow law. `_resolve_addressable_section_body_items()` turns old
    `model.RouteLine` entries into `ResolvedRouteLine`, and `_compile_section_body()`
    renders them as plain `label -> target` prose. That is a real shipped path,
    but it is not the law-owned route-only semantic path.
  - `doctrine/diagnostics.py` is the user-facing error catalog that mirrors the
    parser/compiler rules with stable summaries and hints. Relevant anchors are
    the parse-time route diagnostics (`E131`, `E132`, `E133`) and the
    compile-time workflow-law/output diagnostics (`E331` through `E338`,
    `E351` through `E372`, and `E381` through `E384`) for current-subject
    rules, carrier/trust-surface rules, output-guard namespace rules, owned
    scope, invalidation, and inherited-law structure. This file is not the
    semantic owner; it translates semantic failures into stable diagnostics.
  - `doctrine/renderer.py` is a thin serializer over `CompiledAgent` and
    `CompiledSection`. It only turns compiled trees into Markdown headings and
    prose. It does not understand workflow law, route-only behavior, guarded
    output rules, or trust-surface policy on its own, so render bugs rooted in
    Slice A meaning should be fixed in compiler output, not by moving policy
    into the renderer.
  - `doctrine/verify_corpus.py` is the existing preservation harness.
    `_run_render_contract()` exercises the full parse -> compile -> render path
    and compares it to manifest `expected_lines`. `_run_compile_fail()` and
    `_run_parse_fail()` already give stable failure-proof lanes. `approx_ref`
    diffs are surfaced for human review, but they are advisory and do not
    replace manifest-backed proof. `build_contract` depends on
    `doctrine/emit_docs.py`, which is downstream build emission rather than a
    second owner of Slice A semantics.
  - `docs/WORKFLOW_LAW.md` is the live docs-side semantic anchor. It fixes the
    public mental model for `law`, `output`, `trust_surface`, and
    `standalone_read`, positions examples `30` through `42` as the active
    ladder, and explicitly says the route-only end of the ladder does not yet
    prove `next_owner` agreement or `standalone_read` guard discipline.
  - `docs/COMPILER_ERRORS.md` is the stable docs-side failure anchor. It
    already names the route, currentness, trust-surface, output-guard, mode,
    preservation, invalidation, and inherited-law diagnostics that later
    implementation work must preserve or intentionally update.
  - `examples/README.md` is the proof-policy anchor. It says the examples are
    both the teaching surface and the verification corpus, but the active proof
    lives in manifest-backed `cases.toml`, not in checked-in `ref/**` output.
  - `examples/30_*` through `examples/42_*` are the live Slice A teaching and
    preservation ladder. Examples `30` through `39` carry most of the negative
    proof for law, currentness, trust carriers, and guarded output sections,
    while `40` through `42` currently carry the route-only end mainly as render
    proof rather than fully integrated compile/build proof.
  - `editors/vscode/package.json`, `editors/vscode/extension.js`,
    `editors/vscode/resolver.js`, `editors/vscode/syntaxes/doctrine.tmLanguage.json`,
    and `editors/vscode/README.md` are the editor adaptation boundary. They are
    not semantic owners, but they define the shipped highlighting,
    document-link, and definition-provider behavior that must follow the same
    Slice A surface as the compiler.
- Canonical owner path / boundary to reuse:
  - The canonical Doctrine owner path for Spec 1.3 Slice A is
    `doctrine/grammars/doctrine.lark` -> `doctrine/parser.py` ->
    `doctrine/model.py` -> `doctrine/compiler.py`. Grammar owns syntax,
    parser/model own the typed AST, and the compiler owns cross-reference
    validation, route-only/workflow-law semantics, guarded-output validation,
    trust-surface enforcement, and the compiled readback text shape.
  - `doctrine/renderer.py` and `doctrine/verify_corpus.py` are downstream
    consumers of compiler output, not semantic owners. `doctrine/diagnostics.py`
    is the stable presentation layer for failures, not the place to invent new
    policy. The implementation should therefore converge in the compiler path
    first and then let renderer, diagnostics, examples, and editor adapters
    follow that core.
  - Inside `doctrine/compiler.py`, the concrete owner boundary to reuse is
    `_compile_resolved_workflow()` + `_compile_workflow_law()` +
    `_validate_workflow_law()` for workflow-law semantics, together with
    `_compile_output_decl()` + `_validate_output_guard_sections()` +
    `_compile_record_item()` + `_resolve_output_field_node()` for output,
    `trust_surface`, guarded sections, and compiled readback structure.
- Existing patterns to reuse:
  - Uniqueness-at-parse-time for reserved child blocks. The parser already
    fail-louds on more than one `law` block per workflow and more than one
    `trust_surface` block per output.
  - Typed-AST then semantic-validation layering. Syntax goes into `model.*`
    nodes first, then the compiler performs all cross-reference and
    branch-level checks. Slice A work should extend that pattern, not add
    renderer-side or manifest-side semantics.
  - Branch flattening plus leaf-branch analysis. `_flatten_law_items()` and
    `_collect_law_leaf_branches()` already give the right place to hang any
    additional active-branch checks for route-only behavior.
  - Addressable-child traversal. Guarded output sections are already integrated
    into `_get_addressable_children()` and `_resolve_output_field_node()`, so
    any deeper guarded-section work should reuse that path instead of inventing
    special-case tree walkers.
  - Compiler-error then diagnostics-translation split. Semantic checks should
    stay in `doctrine/compiler.py` with plain `CompileError`s, and
    `doctrine/diagnostics.py` should continue translating those failures into
    stable codes/hints.
  - Manifest-backed preservation. `doctrine/verify_corpus.py` already proves
    exact rendered lines and exact failure codes/messages without treating
    checked-in refs as authority.
  - Ladder-by-example rollout. The shipped corpus already introduces one idea
    at a time from `30` through `42`, so implementation should correct or
    narrow the later route-only examples instead of inventing a parallel
    teaching path.
  - Thin editor registration with adapter-only resolver logic.
    `editors/vscode/extension.js` is already just provider registration, which
    is the correct boundary; convergence work should stay in the resolver and
    TextMate grammar rather than adding a second editor-side semantic engine.
  - Editor verification through repo-local fixtures. The VS Code package
    already combines tmgrammar unit tests, snapshot tests over `examples/**`,
    extension-host definition tests, and the Lark-alignment validator, so
    extension work should deepen those lanes rather than adding bespoke checks.
- Duplicate or drifting paths relevant to this change:
  - The core ships two route surfaces today. The newer Slice A route-only path
    is `LawRouteStmt` inside workflow law, while the older authored-workflow
    path is `RouteLine` inside ordinary workflow sections. Both are in the
    grammar/parser/model/compiler stack today, which means route semantics can
    drift unless the implementation treats the law path as canonical for this
    work.
  - The compiler already special-cases a keyed `standalone_read` section only
    for trust-surface placement. There is no deeper semantic enforcement of
    `standalone_read` truthfulness in core code yet, so the current render path
    can drift from the intended “do not overpromise guarded detail” rule.
  - The proposal and public docs talk about route/output agreement for emitted
    `next_owner`, but no Doctrine core file currently references `next_owner`
    at all. That is a real missing active-proof path rather than an example-only
    problem.
  - Public docs say guarded output expressions may read declared inputs, enum
    members, and compiler-owned host facts. The current compiler implementation
    of `_output_guard_ref_allowed()` only accepts declared inputs and enum
    members. Examples model host facts as ordinary declared inputs such as
    `RouteFacts`, so the current code may still be adequate for Slice A, but
    the broader wording in docs is ahead of the core if “host facts” is meant
    to be a separate root kind.
  - Checked-in example refs and rendered outputs are a downstream drift surface
    rather than proof. The core harness explicitly treats `expected_lines` in
    manifests as the contract and `approx_ref` only as surfaced inconsistency.
  - The route-only end of the ladder is weaker than the earlier workflow-law
    substrate. Examples `40`, `41`, and `42` currently prove rendered output,
    but they do not yet carry the same depth of parse/compile/build proof that
    examples `30` through `39` use for currentness, trust carriers, and guard
    validation.
  - The route-only examples omit `trust_surface` entirely while the public
    workflow-law docs keep describing `output` plus `trust_surface` as the
    portable-truth owner. That may be an intentional Slice A exception, but it
    is a real docs/example tension that deep-dive must resolve explicitly.
  - Example `42` uses inline conditional law route syntax
    (`route "..." -> Target when ...`). The grammar/parser already support
    this, but the public docs currently teach route more narrowly as
    `route "..." -> Agent`, so this is a docs/example drift surface until
    deep-dive decides whether to bless or rewrite it.
  - The VS Code extension duplicates a large amount of language policy today:
    `resolver.js` hard-codes declaration and law/trust-surface patterns,
    maintains its own indentation-walk pseudo-parse, and
    `doctrine.tmLanguage.json` carries a manual workflow-law keyword list.
    Those surfaces will drift unless Slice A changes are driven from the
    compiler-owned language contract first.
  - `editors/vscode/language-configuration.json` is a third editor policy
    surface with brittle indentation rules. Its declaration regex still omits
    `enum`, which is already an evidence-based drift risk unrelated to user
    semantics but relevant to extension correctness.
- Behavior-preservation signals already available:
  - `doctrine/verify_corpus.py` already provides the main end-to-end signal:
    parse -> compile -> render -> exact-line comparison in `render_contract`
    cases.
  - The same harness already provides exact parse/compile-failure proof through
    `parse_fail` and `compile_fail` cases, which is enough to protect new
    diagnostics and semantic checks if the existing manifests are updated
    honestly.
  - `approx_ref` diffs already surface human-readable drift between current
    rendered output and checked-in refs without making refs authoritative.
  - The compiler already exposes stable failure strings that
    `doctrine/diagnostics.py` maps to stable error codes, so behavior-preserving
    validation changes can usually be proven by existing compile-fail manifests
    rather than new harnesses.
  - The workflow-law ladder already contains strong negative proof for the
    substrate through manifest `parse_fail` and `compile_fail` cases in
    examples `30`, `31`, `32`, `33`, `35`, `36`, and `37`.
  - The route-only end also already has user-facing render-preservation hooks:
    examples `40`, `41`, and `42` all have manifest `render_contract` cases,
    which makes current renderer defects visible once the expected lines are
    corrected.
  - The VS Code extension already has a credible preservation stack in
    `editors/vscode/package.json`: tmgrammar unit tests, snapshot tests against
    `examples/**`, extension-host integration tests, and
    `scripts/validate_lark_alignment.py`.
  - Current VS Code integration coverage already protects workflow-law carrier
    refs, enum-backed modes, law-section `inherit`/`override`, and law route
    targets, but it does not yet exercise the later route-only/guarded-output
    ladder the way it exercises examples `31`, `32`, and `37`.

## 3.3 Open questions from research

There are no remaining blocking open questions after deep-dive. The list below
records the research questions that were resolved and then carried forward into
Sections 5 and 6 so the evidence trail stays explicit.

- `RouteLine` versus law route path:
  Freeze `RouteLine` as a legacy authored-workflow path and keep
  `LawRouteStmt` as the canonical Slice A route owner.
- Guarded-output “host facts”:
  Treat them as declared host-supplied inputs in this run; do not add a new
  compiler-owned host-fact root kind.
- Route-only `trust_surface` omission:
  Keep `40` through `42` outside `trust_surface` as an intentional Slice A
  boundary.
- `next_owner` and `standalone_read` proof:
  Do not invent prose parsing in this run. Proposal rule 9 still belongs in the
  implementation target, but only through existing structured output surfaces
  or the smallest explicit binding surface justified during implementation.
  Proposal rule 10 also remains in scope, but its proof must stay honest to the
  current no-prose-parser boundary and use the strongest manifest-backed signal
  the language can support.
- `standalone_read` placement:
  Keep the current compiler-owned placement rule in `_compile_output_decl()`
  unless implementation finds a concrete call-site breakage that requires a
  narrower structural refinement.
- Inline conditional law route:
  Keep and document it as a first-class shipped surface because the
  grammar/parser already ship it and the capstone already uses it.
- VS Code coverage for `39` through `42`:
  Add explicit unit, snapshot, integration, and Lark-alignment coverage rather
  than relying on incidental support.
<!-- arch_skill:block:research_grounding:end -->

# 4) Current Architecture (as-is)

<!-- arch_skill:block:current_architecture:start -->
## 4.1 On-disk structure

The current Slice A surface is spread across four concrete repo layers:

- `doctrine/`
  - `doctrine/grammars/doctrine.lark` owns shipped syntax, including
    `guarded_output_section`, `trust_surface`, `law_route_stmt`, and the older
    authored-workflow `route_stmt`.
  - `doctrine/parser.py` converts syntax into typed AST nodes and keeps
    `trust_surface` and `law` fail-loudly unique.
  - `doctrine/model.py` carries the core typed split through
    `WorkflowBody.law`, `OutputDecl.trust_surface`, `GuardedOutputSection`,
    `LawRouteStmt`, and the legacy `RouteLine`.
  - `doctrine/compiler.py` is the semantic owner.
  - `doctrine/diagnostics.py`, `doctrine/renderer.py`,
    `doctrine/verify_corpus.py`, and `doctrine/emit_docs.py` are the
    translation, serialization, proof, and emitted-ref paths that sit
    downstream of the compiler.
- `docs/`
  - `docs/WORKFLOW_LAW.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
    `docs/COMPILER_ERRORS.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, and
    `docs/README.md` are the human-facing surfaces most likely to drift if the
    core changes and the docs are not repaired in the same run.
- `examples/`
  - The workflow-law ladder is concentrated in examples `30` through `42`.
  - Each example splits authored prompts, manifest-backed proof in `cases.toml`,
    and downstream render snapshots under `ref/`.
- `editors/vscode/`
  - `package.json` and `extension.js` are a thin shell.
  - `resolver.js`, `syntaxes/doctrine.tmLanguage.json`, and
    `language-configuration.json` encode the adapter behavior that must follow
    the compiler-owned surface.
  - `tests/**` and `scripts/validate_lark_alignment.py` are the editor proof
    lane.

## 4.2 Control paths (runtime)

The current end-to-end Doctrine path is already coherent at the top level:

`parse_file()` -> `parse_text()` -> Lark grammar -> `ToAst` builders ->
`compile_prompt()` -> `CompilationContext.compile_agent()` ->
`_resolve_agent_contract()` plus `_compile_workflow_decl()` /
`_compile_output_decl()` -> `render_markdown()` -> manifest verification.

Three concrete downstream runtime paths sit on top of that shared core:

- Core compile/render path:
  - `doctrine/compiler.py::_compile_output_decl()` validates guarded output
    expressions, inserts the compiled `Trust Surface` section, and renders
    guarded output sections as conditional shells through `_compile_record_item()`.
  - `_compile_resolved_workflow()`, `_compile_workflow_law()`, and
    `_render_law_stmt_lines()` merge authored workflow prose with law-owned
    currentness, stop, and route consequences.
- Emitted-ref path:
  - `doctrine/emit_docs.py::emit_target()` parses the configured entrypoint,
    compiles each root concrete agent, and serializes the rendered `AGENTS.md`
    trees under the configured output directories.
  - That means checked-in refs are downstream products of the compiler/render
    path, not an independent source of truth.
- VS Code authoring path:
  - `editors/vscode/extension.js` registers an import-only
    `DocumentLinkProvider` plus a shared `DefinitionProvider`.
  - `editors/vscode/resolver.js` indexes declarations once per document and then
    resolves imports, declarations, addressable paths, and some workflow-law
    references through its own regex and indentation-based pseudo-parse.
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json` and
    `editors/vscode/language-configuration.json` shape the lexical and editing
    experience around that same authored text.

The main control-path fault line is still internal to the compiler:

- Slice A route semantics live on the workflow-law path.
- Older non-law route prose still flows through the legacy authored-workflow
  `RouteLine` path.

## 4.3 Object model + key abstractions

Current Slice A behavior is organized around these key abstractions:

- Output-side abstractions:
  - `OutputDecl.trust_surface`
  - `GuardedOutputSection`
  - addressable output traversal via `_get_addressable_children()`,
    `_record_items_to_addressable_children()`, and `_resolve_output_field_node()`
- Workflow-law abstractions:
  - `CurrentNoneStmt`
  - `LawRouteStmt`
  - `LawBranch` leaf analysis inside `_validate_workflow_law()` and
    `_collect_law_leaf_branches()`
- Legacy authored-workflow abstraction:
  - `RouteLine` in the AST
  - `ResolvedRouteLine` in compilation

The object-model split is actually good news: the repo already distinguishes
the canonical workflow-law route path from the older authored-workflow route
path at the model layer. The drift is not that the compiler lacks a type split;
it is that the repo still ships both paths and the public surfaces do not
explain the boundary clearly enough.

## 4.4 Observability + failure behavior today

Current failure and proof behavior is uneven but concrete:

- Compiler and parser failures are surfaced through stable diagnostics in
  `doctrine/diagnostics.py`.
- Manifest-backed corpus verification already proves exact render,
  compile-fail, parse-fail, and build behavior through
  `doctrine/verify_corpus.py`.
- Checked-in example refs are only advisory via `approx_ref`.
- The editor is intentionally fail-silent for unresolved links or definitions;
  missing targets generally produce no navigation result rather than a second
  semantic error system.

The main observed drift points are:

- The core still ships two route paths: `LawRouteStmt` for Slice A and the
  legacy `RouteLine` path for older authored workflows.
- Output-guard docs currently overstate the allowed source space. The compiler
  only accepts declared inputs and enum members today; “host facts” are modeled
  as declared inputs, not as a separate root kind.
- Route-only examples `40` through `42` intentionally omit `trust_surface`, but
  the live docs do not explain that exception sharply enough yet.
- Example `42` uses inline conditional law-route syntax
  (`route "..." -> Agent when expr`), which the grammar/parser already ship,
  but the live docs and editor coverage do not yet treat as a first-class
  public surface.
- Compiled law wording is currently clumsy in at least one route-only render:
  example `40` produces “next owner is unknown is false,” which is a compiled
  text bug, not a contract worth preserving.
- Examples `40` through `42` are proof-light compared with the earlier
  workflow-law ladder. They lean on `render_contract` plus refs and do not yet
  provide integrated active proof for routed `next_owner` agreement or for
  `standalone_read` guard discipline.

## 4.5 UI surfaces (rendered docs + editor)

The user-facing surfaces that currently matter are:

- Compiled `AGENTS.md` output
  - workflow prose
  - law activation/currentness/stop/route consequences
  - output schema, guarded-section shells, and `trust_surface`
- VS Code authoring ergonomics
  - syntax coloring
  - indentation behavior
  - import link clicks
  - go-to-definition for declarations, addressable paths, and workflow-law refs

Those surfaces are already real, but they are not equally protected.
Highlighting, indentation, and navigation coverage stop short of the corrected
`39` through `42` surface, and emitted refs still reflect at least one known
bad render phrasing.
<!-- arch_skill:block:current_architecture:end -->

# 5) Target Architecture (to-be)

<!-- arch_skill:block:target_architecture:start -->
## 5.1 On-disk structure (future)

The future on-disk ownership should be explicit and boring:

- `doctrine/grammars/doctrine.lark` -> `doctrine/parser.py` ->
  `doctrine/model.py` -> `doctrine/compiler.py` remain the one canonical owner
  path for Slice A.
- `doctrine/renderer.py`, `doctrine/diagnostics.py`,
  `doctrine/verify_corpus.py`, and `doctrine/emit_docs.py` remain downstream
  adapter or proof surfaces.
- Live docs that survive this run must match the compiler-owned truth:
  - `docs/WORKFLOW_LAW.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/COMPILER_ERRORS.md` if diagnostics wording changes
  - `docs/LANGUAGE_DESIGN_NOTES.md` where it still describes current language
    decisions
  - `docs/README.md`
  - `examples/README.md`
- The example ladder remains the public teaching/proof surface:
  - keep `30` and `39` as the strong substrate anchors
  - correct `40` through `42`
  - delete the empty stale directory
    `examples/42_route_only_handoff_capstone/ref/route_only_handoff_capstone_demo`
- The VS Code extension remains an adapter bundle:
  - thin shell in `package.json` and `extension.js`
  - syntax/navigation behavior in `resolver.js`,
    `syntaxes/doctrine.tmLanguage.json`, and
    `language-configuration.json`
  - proof in `tests/**` plus `scripts/validate_lark_alignment.py`

## 5.2 Control paths (future)

The future runtime path stays on the existing core, but with the route-only
family fully converged onto the law-owned path:

`parse_file()` -> `parse_text()` -> Lark grammar -> `ToAst` builders ->
`compile_prompt()` -> `CompilationContext.compile_agent()` ->
`_resolve_agent_contract()` plus `_compile_workflow_decl()` /
`_compile_output_decl()` -> `render_markdown()` -> `verify_corpus` and
`emit_docs` as downstream consumers.

Control-path decisions:

- All enforceable Slice A semantics stay in `doctrine/compiler.py`.
- The workflow-law path owns all route-only semantics:
  - `_compile_resolved_workflow()`
  - `_compile_workflow_law()`
  - `_render_law_stmt_lines()`
  - `_validate_workflow_law()`
  - `LawBranch` leaf analysis
- Output-side guarded readback stays on:
  - `_compile_output_decl()`
  - `_compile_record_item()`
  - `_resolve_output_field_node()`
- Emitted refs remain downstream products of the compiler plus renderer through
  `doctrine/emit_docs.py`; they are refreshed after core/render fixes, not used
  to define those fixes.
- The VS Code path remains thin:
  - imports keep using `DocumentLinkProvider`
  - all other click-through stays definition-provider based
  - resolver, grammar, indentation, validator, and tests are updated to match
    the corrected shipped syntax rather than inventing a second semantic model

## 5.3 Object model + abstractions (future)

The future object-model stance is now fully specified:

- `LawRouteStmt` is the canonical route abstraction for Slice A.
  - All route-only semantics remain on `_compile_workflow_law()`,
    `_validate_workflow_law()`, and `LawBranch`.
- `RouteLine` stays supported only as a legacy authored-workflow abstraction for
  older non-law examples and workflows.
  - It is frozen outside Slice A.
  - This run does not widen, enrich, or reinterpret it.
- `GuardedOutputSection` remains an output-owned, keyed, titled, addressable
  abstraction.
- Output guards stay narrow and compiler-owned.
  - For this run, “host facts” means declared host-supplied inputs rooted in
    the ordinary input registry.
  - This run does not add a hidden host-fact root kind.
- Route-only outputs `40` through `42` stay intentionally outside
  `trust_surface`.
  - Carrier-backed portable truth remains the `31` / `36` family.
  - Route-only comment-schema readback remains an output-owned exception for
    turns with `current none`.
- `standalone_read` stays authored explanatory prose, not a second semantic
  plane.
  - No prose parser.
  - No NLP-style validation.
  - Proposal rule 9 (`next_owner` agreement) remains part of this plan, but any
    compiler-owned enforcement must use an existing structured output surface or
    the smallest explicit binding surface justified in implementation.
  - Proposal rule 10 (`standalone_read` guard discipline) also remains part of
    this plan, but its proof path must stay honest to the current language
    boundary and cannot rely on prose parsing.

## 5.4 Invariants and boundaries

Boundary rules for implementation:

- Grammar owns syntax.
- Parser and model own the typed AST.
- Compiler owns all enforceable Slice A semantics, compiled render layering,
  and addressable output/readback structure.
- Diagnostics translate parser/compiler failures into stable codes.
- Renderer stays a dumb serializer over compiled sections.
- Manifest-backed examples, live docs, emitted refs, and the VS Code extension
  all follow the compiler-owned contract.

This architecture rejects the following escape hatches:

- no new top-level `review` surface
- no renderer-side policy patching
- no diagnostics-side policy invention
- no new host-fact root kind
- no prose parser for `standalone_read`
- no new verification harness
- no language server
- no compatibility rules in docs/examples/editor support for known-bad example
  shapes
- no expansion of the legacy `RouteLine` path to own Slice A behavior
- no editor-side semantic enforcement of `next_owner` agreement or
  `standalone_read` guard discipline

This plan still carries proposal rules 9 and 10. What it rejects is hidden
heuristics. If existing structured surfaces are insufficient for rule 9, the
only acceptable widening is a small explicit compiler-owned contract recorded
in Section 10. Rule 10 must stay within the no-prose-parser boundary even when
its proof burden is strengthened.

## 5.5 UI surfaces (rendered docs + editor)

The future user-facing surfaces should be intentionally aligned:

- Compiled `AGENTS.md` renders should keep four layers distinct:
  1. authored workflow prose
  2. law activation and currentness summary
  3. law stop/route consequences
  4. output schema plus guarded-section shells and `trust_surface`
- Public docs and examples should teach the same story:
  - `docs/WORKFLOW_LAW.md` explicitly documents the route-only no-`trust_surface`
    exception, the narrow guard-source rule, and inline conditional law routes
    if that syntax stays shipped
  - `docs/AGENT_IO_DESIGN_NOTES.md` explicitly contrasts carrier-backed portable
    truth with route-only comment-schema readback
  - `examples/README.md` explicitly says refs are not proof, `40` through `42`
    omit `trust_surface` intentionally, and `42` is the route-only capstone plus
    `39`-style guarded readback
- VS Code should expose the corrected shipped surface to authors:
  - guarded output headers are highlighted and indent correctly
  - conditional law routes are highlighted and navigable
  - imports click through with document links
  - declarations, addressable paths, guarded sections, and route targets resolve
    through go-to-definition
<!-- arch_skill:block:target_architecture:end -->

# 6) Call-Site Audit (exhaustive change inventory)

<!-- arch_skill:block:call_site_audit:start -->
## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Core syntax | `doctrine/grammars/doctrine.lark` | `guarded_output_section`, `law_route_stmt`, `route_stmt`, `trust_surface_block` | Grammar already ships guarded sections, law routes with optional `when`, and the legacy authored `route_stmt`. | Preserve guarded/trust/law forms; explicitly treat `route_stmt` as legacy only for this run. | Stops route-path drift without inventing new syntax. | Slice A route semantics live only on `law_route_stmt`. | `make verify-examples`; `30`, `39`, `41`, `42`; legacy route examples `07`, `10`, `12`, `20`, `26`. |
| Core parse | `doctrine/parser.py` | `output_body()`, `guarded_output_section()`, `current_none_stmt()`, `law_route_stmt()`, `route_stmt()` | Parser already splits `trust_surface`, builds guarded nodes, parses `current none`, and keeps law routes separate from `RouteLine`. | Preserve the AST split and keep `LawRouteStmt` plus `current none` as the Slice A route/currentness owner path; no new semantics added to `RouteLine`. | Keeps typed ownership correct and fail-loud. | No new parser path; only clarified ownership. | Existing workflow-law manifests; `30` route/currentness failures; `39` guard failures. |
| Core model | `doctrine/model.py` | `OutputDecl.trust_surface`, `GuardedOutputSection`, `CurrentNoneStmt`, `LawRouteStmt`, `RouteLine` | Model already expresses the right shipped split plus the legacy route path. | Preserve existing Slice A nodes; freeze `RouteLine` as legacy. | No new model abstraction needed for this run. | Same AST, clearer boundary. | Indirectly all workflow-law examples. |
| Core compile | `doctrine/compiler.py` | `_compile_output_decl()`, `_compile_record_item()`, `_compile_trust_surface_section()` | Compiler owns output guard validation, `trust_surface` insertion, and guarded-section rendering. | Keep policy here; fix render ordering and wording only here, not in renderer. | Output/readback layering is compiler-owned. | Compiled output remains SSOT. | `31`, `39`, `40`, `41`, `42` render contracts. |
| Core compile | `doctrine/compiler.py` | `_validate_output_guard_sections()`, `_validate_output_record_items()`, `_validate_output_guard_expr()`, `_validate_output_guard_ref()`, `_output_guard_ref_allowed()` | Guards accept inputs and enum members only, and nested guarded sections are validated recursively through the output-record traversal. | Preserve that narrow rule; align docs and diagnostics wording to it. | Prevent hidden host-fact semantics and keep nested guarded-section ownership on the compiler path that already exists. | “Host facts” means declared host-supplied inputs in this run. | `39` `E338` cases; `make verify-diagnostics` if wording changes. |
| Core compile | `doctrine/compiler.py` | `_compile_resolved_workflow()`, `_compile_workflow_law()`, `_render_law_stmt_lines()`, `_render_condition_expr()`, `_render_condition_subject()`, `_render_condition_ref()` | Workflow/law layering is centralized, but the current condition-rendering helper path still produces awkward route-only wording in example `40`. | Keep Slice A rendering on this path and fix condition phrasing here. | Avoid preserving broken renders or moving policy to serializer. | Compiled law text remains compiler-owned. | `30`, `40`, `41`, `42` render contracts. |
| Core compile | `doctrine/compiler.py` | `_validate_workflow_law()`, `_validate_law_stmt_tree()`, `_collect_law_leaf_branches()`, `_branch_with_stmt()`, `_validate_route_target()`, `_validate_carrier_path()` | Enforces one current subject per active leaf, carrier/trust rules, invalidation contradictions, and route target validity. | Preserve as canonical semantic validation path; if proposal rule 9 needs explicit route/output coupling, land it here or on adjacent compiler-owned output validation rather than in docs or the editor. | This is the right place for enforceable law semantics. | No hidden coupling; only the smallest explicit structured contract if rule 9 truly requires one. | `30` `E331/E332`; `31` `E336/E337`; `36` `E371/E372`; `37` `E381-E384`; targeted `40`-`42` proof cases. |
| Core legacy | `doctrine/compiler.py` | `_resolve_addressable_section_body_items()`, `_compile_section_body()` | Legacy `RouteLine` still compiles to plain `label -> target` prose. | Freeze as non-Slice-A legacy behavior; do not extend. | Keeps older authored workflows working without owning new law behavior. | No new Slice A behavior on `RouteLine`. | Older authored-route examples `07`, `10`, `12`, `14`, `17`, `20`, `26`. |
| Emit path | `doctrine/emit_docs.py` | `emit_target()`, `load_emit_targets()` | Emitted example refs are generated downstream from `compile_prompt()` plus `render_markdown()`, but the current plan did not name the emit path explicitly. | Treat it as the canonical ref-refresh path after render fixes; do not special-case refs by hand. | Rendered refs are part of the user-visible output lane and must follow the same compiler-owned truth. | Refs are regenerated downstream, never hand-authored policy surfaces. | targeted emit commands when ref snapshots are refreshed; `make verify-examples`. |
| Proposal gap closure | `doctrine/compiler.py`, `doctrine/verify_corpus.py`, `examples/40_route_only_local_ownership/**`, `examples/41_route_only_reroute_handoff/**`, `examples/42_route_only_handoff_capstone/**` | route/output agreement for `next_owner`; `standalone_read` guard discipline | Proposal rules 9 and 10 are target behavior, but the numbered corpus still lacks integrated active proof for them and the prior plan wording risked treating them as permanent deferrals. | Carry them into this run honestly: land the smallest explicit compiler-owned agreement surface for `next_owner` that avoids magic, and add the strongest manifest-backed integrated proof for both rules without prose parsing. | This is the main remaining proposal-alignment gap. | No hidden magic; explicit structured contract only if needed. | `40`-`42` manifests; `make verify-examples`; `make verify-diagnostics` if a new error surface appears. |
| Diagnostics | `doctrine/diagnostics.py` | `_classify_unexpected_token()`, workflow-law mappings for `E331`, `E332`, and `E338` | Stable codes already exist, but `E338` wording overpromises host-fact support and the route-only parse/compile surface spans more than one code. | Rewrite hints only if needed to match the shipped core rule and keep the route-only/guarded-output codes aligned with the compiler. | Diagnostics must describe real compiler behavior. | Stable codes preserved; only wording may narrow. | `make verify-diagnostics`; existing parse/compile-fail manifests. |
| Verification | `doctrine/verify_corpus.py`, `doctrine/renderer.py` | `_load_case()`, `_run_render_contract()`, `_run_parse_fail()`, `_run_compile_fail()`, `_run_build_contract()`, `_build_contract_ref_diff()`, `render_markdown()`, `_render_section()` | Existing harness already proves exact render, parse-fail, compile-fail, and build output, but the prior inventory understated the concrete proof path. | Preserve harness; strengthen `40` to `42` with the smallest honest existing manifest kinds. | No new harness needed. | Manifest-backed proof remains SSOT. | `make verify-examples`; targeted `verify_corpus`. |
| Live docs | `docs/WORKFLOW_LAW.md` | shipped workflow-law reference | Live mental model is good, but it under-documents inline conditional law routes, overstates guard-source breadth, and does not explain the route-only no-`trust_surface` exception sharply enough. | Rewrite to document the actual shipped Slice A contract, including conditional law routes if kept. | Main public semantic explainer must match compiler truth. | Live docs follow compiler-owned Slice A. | `39`, `40`, `42` examples as proof anchors. |
| Live docs | `docs/AGENT_IO_DESIGN_NOTES.md` | `output` / `trust_surface` / `standalone_read` boundary | Explains portable truth well, but route-only comment-schema readback is not contrasted strongly enough and host-fact wording is too broad. | Rewrite to make the `31/36` carrier path vs `40/42` route-only path explicit. | Prevents readers from “fixing” route-only examples by adding bogus `trust_surface`. | Route-only outputs remain outside `trust_surface`. | `31`, `36`, `40`, `42`. |
| Live docs | `docs/COMPILER_ERRORS.md` | canonical error catalog | Stable error coverage exists, but the doc will drift if `E338` wording is narrowed or route-only errors gain clearer wording examples. | Update only where diagnostics text or examples materially change. | The error catalog is user-facing truth, not a stale appendix. | Error docs follow shipped diagnostics wording. | `make verify-diagnostics`; doc-only. |
| Live docs | `docs/LANGUAGE_DESIGN_NOTES.md` | current language decisions | The notes still repeat the broader “compiler-owned host facts” wording and may be used as a living design explainer even if they are not the main index doc. | Sync or narrow the Slice A language-decision notes wherever they would contradict the corrected compiler-owned rule. | Prevents a second semi-live design story from surviving after the change. | Design notes follow the same Slice A boundary decisions. | doc-only. |
| Live docs | `docs/README.md`, `examples/README.md` | docs index and corpus policy | Docs index is high-level; corpus guide states refs are not proof but does not explicitly say `40` to `42` omit `trust_surface` intentionally or that `42` is the conditional-route capstone. | Rewrite the index and corpus ladder text to steer readers to manifests and the corrected Slice A story. | Keeps onboarding and corpus policy aligned. | Manifests stay the proof surface; refs stay downstream only. | `make verify-examples`; doc-only. |
| Examples anchor | `examples/30_law_route_only_turns/cases.toml`, `examples/30_law_route_only_turns/prompts/AGENTS.prompt`, `examples/30_law_route_only_turns/prompts/INVALID_*.prompt`, `examples/30_law_route_only_turns/ref/route_only_triage_demo/AGENTS.md` | route-only setup and negative currentness/route cases | `30` is the honest no-carrier setup and already proves route/currentness failures through concrete invalid prompts. | Keep semantics; tighten prose/comments where needed so they teach the intended ladder more explicitly. | Preserve the strong substrate example instead of shifting meaning elsewhere. | `30` stays the no-carrier setup with explicit parse/compile-fail proof. | Existing `30` manifests; `make verify-examples`. |
| Examples anchor | `examples/39_guarded_output_sections/cases.toml`, `examples/39_guarded_output_sections/prompts/AGENTS.prompt`, `examples/39_guarded_output_sections/prompts/INVALID_*.prompt`, `examples/39_guarded_output_sections/ref/guarded_output_sections_demo/AGENTS.md`, `examples/39_guarded_output_sections/ref/nested_guarded_output_sections_demo/AGENTS.md` | guarded-output anchor and negative guard-namespace cases | `39` is already the clean guarded-section anchor and the place where nested guarded sections plus `E338` failures are actively proven. | Keep semantics; tighten prose/comments where needed so the compiler-owned guard boundary is taught explicitly. | Preserve the strong guarded-output substrate instead of rediscovering it elsewhere. | `39` stays the guarded-output anchor. | Existing `39` manifests; `make verify-examples`; `make verify-diagnostics` if wording changes. |
| Examples capstone | `examples/40_route_only_local_ownership/cases.toml`, `examples/40_route_only_local_ownership/prompts/AGENTS.prompt`, `examples/40_route_only_local_ownership/ref/route_only_local_ownership_demo/AGENTS.md` | local-ownership route-only outcome | `40` teaches the no-reroute branch, but its current compiled wording is broken. | Keep no-`trust_surface` omission; fix prompt/comments and refresh the ref only after compiler wording is corrected. | This is the first route-only outcome users see. | Route-only output stays comment-schema readback, not portable truth. | `40` manifest and ref; `make verify-examples`. |
| Examples capstone | `examples/41_route_only_reroute_handoff/cases.toml`, `examples/41_route_only_reroute_handoff/prompts/AGENTS.prompt`, `examples/41_route_only_reroute_handoff/ref/route_only_reroute_handoff_demo/AGENTS.md` | reroute-handoff branch | `41` teaches the semantic reroute outcome and should stay paired cleanly against `40`. | Keep no-`trust_surface` omission; correct prompt/comments and refresh the ref after final compiler wording settles. | This is the clean reroute counterpart to `40`. | Route-only output stays comment-schema readback, not portable truth. | `41` manifest and ref; `make verify-examples`. |
| Examples capstone | `examples/42_route_only_handoff_capstone/cases.toml`, `examples/42_route_only_handoff_capstone/prompts/AGENTS.prompt`, `examples/42_route_only_handoff_capstone/ref/route_only_turns_demo/AGENTS.md` | route-only capstone with guarded readback and conditional route | `42` is the public capstone, but it is still half-documented and currently proof-light beyond render output. | Keep no-`trust_surface` omission; document the conditional route syntax explicitly, strengthen manifests where honest, and refresh the ref after final compiler wording settles. | This is the slice capstone and the most drift-prone example in scope. | Route-only output stays comment-schema readback, not portable truth. | `42` manifest and ref; `make verify-examples`. |
| Example refs | `examples/40_route_only_local_ownership/ref/route_only_local_ownership_demo/AGENTS.md`, `examples/41_route_only_reroute_handoff/ref/route_only_reroute_handoff_demo/AGENTS.md`, `examples/42_route_only_handoff_capstone/ref/route_only_turns_demo/AGENTS.md` | rendered downstream snapshots | Current refs encode at least one known-bad render phrasing and are not yet aligned to the corrected capstone story. | Refresh these refs only after compiler/render wording is fixed and manifests agree. | Refs should mirror shipped behavior, not pin known-bad prose. | Refs remain downstream snapshots, never semantic owners. | targeted emit + `make verify-examples`. |
| Example cleanup | `examples/42_route_only_handoff_capstone/ref/route_only_handoff_capstone_demo` | empty stale ref directory | Delete it. | Dead downstream truth surface should not remain live. | None. | N/A |
| VS Code shell | `editors/vscode/package.json`, `editors/vscode/extension.js` | `registerDefinitionProvider()` and package test scripts | The shell is already thin. For examples `39` through `42`, the relevant click surface is the definition provider, not the import-only document-link provider. | Preserve the thin shell and extend the fixture/test inputs through `39` to `42`. | Keep adapter boundary clean while proving the actual requested click-through surface. | Imports stay document-link only; route-only and guarded-output clicks stay definition-provider based. | `cd editors/vscode && make`; `npm test`. |
| VS Code resolver | `editors/vscode/resolver.js` | `ROUTE_RE`, `collectLawBodySites()`, `collectWorkflowSectionSites()`, `collectRecordBodySites()`, `resolveDirectDefinition()`, `resolveAddressableDefinition()`, `getIoChildBodySpec()`, `getRecordChildBodySpec()`, `collectShippedLawRefSites()` | Navigation for guarded sections and conditional law routes is partly incidental and partly heuristic. In particular, conditional route targets in example `42` currently survive through generic law-token fallback because `ROUTE_RE` expects the agent target at end of line. | Make guarded output sections and conditional law-route targets intentional supported paths; keep runtime-only fields non-goals. | Avoid a second policy engine while covering the shipped syntax. | Resolver adapts shipped syntax explicitly, not accidentally. | Integration tests for `39` to `42`. |
| VS Code grammar | `editors/vscode/syntaxes/doctrine.tmLanguage.json` | route rule and generic key rules | Bare law/trust syntax is covered, but guarded output headers and `route ... when ...` are not first-class. | Add explicit guarded-header and conditional law-route highlighting coverage. | Highlighting must match shipped grammar. | TextMate remains lexical adapter only. | Unit tests, snapshots, validator. |
| VS Code ergonomics | `editors/vscode/language-configuration.json` | `onEnterRules` | Indents after `law:` and `trust_surface:`, but not after guarded output headers like `rewrite_mode: "..." when ...:`. | Add a narrow guarded-section indentation rule. | Prevent editor ergonomics drift on shipped syntax. | Indentation follows shipped guarded header form. | `cd editors/vscode && make`; add targeted coverage. |
| VS Code validator | `editors/vscode/scripts/validate_lark_alignment.py` | `_require_pattern_match()` plus the current explicit keyword/regex checks | Validator exists, but it does not yet explicitly assert guarded output headers or conditional law routes, and it does not validate `language-configuration.json` indentation behavior. | Add explicit sample coverage for shipped guarded headers and `route "..." -> Agent when expr`, and keep indentation coverage honest elsewhere. | Prevents regex drift between the grammar and the editor adapter without overstating what the validator covers. | Validator asserts the corrected shipped lexical forms and nothing more. | `cd editors/vscode && make`; validator run. |
| VS Code unit fixtures | `editors/vscode/tests/unit/workflow-law.test.prompt`, `editors/vscode/tests/unit/route-highlighting.test.prompt` | lexical fixtures for workflow-law syntax | Current unit fixtures only cover bare workflow-law keywords and bare `route "..." -> Agent`, not guarded headers or conditional routes. | Add fixtures that exercise example-39 guarded output headers and example-42 conditional law routes directly. | Unit-level lexical proof should cover the actual Slice A additions. | Unit fixtures mirror the corrected shipped syntax. | `npm run test:unit`. |
| VS Code snapshots | `editors/vscode/tests/snap/examples/39_guarded_output_sections/**`, `editors/vscode/tests/snap/examples/40_route_only_local_ownership/**`, `editors/vscode/tests/snap/examples/41_route_only_reroute_handoff/**`, `editors/vscode/tests/snap/examples/42_route_only_handoff_capstone/**` | example-backed highlighting snapshots | Snapshots currently stop at example `38`, so the extension has no snapshot proof for the corrected `39` to `42` surface. | Add snapshot fixtures for examples `39` through `42`, including the example-39 invalid prompt siblings, after those prompts are corrected. | Snapshot proof should include the actual route-only and guarded-output ladder in scope. | Snapshot corpus follows corrected examples, not stale ones. | `npm run test:snap`. |
| VS Code integration | `editors/vscode/tests/integration/run.js`, `editors/vscode/tests/integration/suite/index.js` | `run()`, `testAddressableDefinitionProvider()`, `testWorkflowLawDefinitionProvider()`, full clickable-surface checks | Integration tests currently protect earlier workflow-law and addressable-path behavior but do not exercise the `39` to `42` ladder. | Add definition/navigation checks for guarded section keys, nested guarded paths, `title` hops, route-only output addressability, and conditional route targets. | The requested link-click behavior must be proven on the exact Slice A surface in scope. | Integration suite covers corrected `39` to `42` authoring flows. | `npm run test:integration`. |
| VS Code docs | `editors/vscode/README.md` | extension support matrix and smoke steps | README still describes the older support surface and does not name guarded output headers or conditional law routes. | Rewrite the support matrix and smoke checklist after the corrected Slice A alignment lands. | The editor docs are a live user-facing surface. | README follows the actual supported syntax/navigation surface. | doc-only; `cd editors/vscode && make` when packaging changes. |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `doctrine/grammars/doctrine.lark` -> `doctrine/parser.py` ->
    `doctrine/model.py` -> `doctrine/compiler.py`
- Deprecated APIs (if any):
  - No public API is deprecated in this run.
  - Internally, `RouteLine` is frozen as a legacy authored-workflow path and is
    explicitly not the Slice A route owner.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - delete the empty stale directory
    `examples/42_route_only_handoff_capstone/ref/route_only_handoff_capstone_demo`
  - delete any new editor fixtures accidentally added for illustrative-but
    non-shipped Slice A syntax
- Capability-replacing harnesses to delete or justify:
  - no new language server
  - no new verification harness
  - no prose parser for `standalone_read`
  - no hidden compiler-owned host-fact root kind
- Live docs/comments/instructions to update or delete:
  - `docs/WORKFLOW_LAW.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/COMPILER_ERRORS.md` if diagnostics wording changes
  - `docs/LANGUAGE_DESIGN_NOTES.md` where it still describes current language
    decisions for this slice
  - `docs/README.md`
  - `examples/README.md`
  - `examples/30_law_route_only_turns/cases.toml`
  - `examples/30_law_route_only_turns/prompts/AGENTS.prompt`
  - `examples/30_law_route_only_turns/prompts/INVALID_*.prompt` when route/currentness wording changes
  - `examples/30_law_route_only_turns/ref/route_only_triage_demo/AGENTS.md`
  - `examples/39_guarded_output_sections/cases.toml`
  - `examples/39_guarded_output_sections/prompts/AGENTS.prompt`
  - `examples/39_guarded_output_sections/prompts/INVALID_*.prompt` when guard-namespace wording changes
  - `examples/39_guarded_output_sections/ref/guarded_output_sections_demo/AGENTS.md`
  - `examples/39_guarded_output_sections/ref/nested_guarded_output_sections_demo/AGENTS.md`
  - `examples/40_route_only_local_ownership/cases.toml`
  - `examples/40_route_only_local_ownership/prompts/AGENTS.prompt`
  - `examples/40_route_only_local_ownership/ref/route_only_local_ownership_demo/AGENTS.md`
  - `examples/41_route_only_reroute_handoff/cases.toml`
  - `examples/41_route_only_reroute_handoff/prompts/AGENTS.prompt`
  - `examples/41_route_only_reroute_handoff/ref/route_only_reroute_handoff_demo/AGENTS.md`
  - `examples/42_route_only_handoff_capstone/cases.toml`
  - `examples/42_route_only_handoff_capstone/prompts/AGENTS.prompt`
  - `examples/42_route_only_handoff_capstone/ref/route_only_turns_demo/AGENTS.md`
  - `editors/vscode/README.md`
  - `editors/vscode/resolver.js` boundary comments if support surfaces expand
  - any emit-target comments or usage notes that still treat refs as primary
    truth instead of downstream output
- Behavior-preservation signals for refactors:
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics change
  - targeted `uv run --locked python -m doctrine.verify_corpus --manifest ...`
  - `cd editors/vscode && make`
  - existing unit/snap/integration editor tests plus
    `scripts/validate_lark_alignment.py`

## Pattern Consolidation Sweep

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Law semantics | `doctrine/compiler.py::_validate_workflow_law()` and `LawBranch` | All Slice A enforceable law semantics hang off law leaf-branch analysis. | Prevents route/currentness semantics from leaking into parser, renderer, docs, or the editor. | include |
| Output readback | `doctrine/compiler.py::_compile_output_decl()` and `_resolve_output_field_node()` | Guarded output sections stay compiler-owned, addressable, and output-owned. | Prevents a second guarded-section model in docs/examples/editor code. | include |
| Route-only teaching | `examples/30`, `40`, `41`, `42`; `docs/WORKFLOW_LAW.md`; `examples/README.md` | Route-only turns teach one explicit story: `current none`, optional law route, output-owned readback, no `trust_surface`. | Prevents the corpus from “symmetrizing” route-only examples into the portable-truth carrier model. | include |
| Rendered refs | `doctrine/emit_docs.py`; example `ref/**` trees for `30`, `39`, `40`, `41`, `42` | Checked-in refs follow the compiler/render path and manifests instead of becoming a sidecar policy source. | Prevents bad renders or hand-edited refs from turning into a second truth surface. | include |
| Editor adaptation | `editors/vscode/resolver.js`, `doctrine.tmLanguage.json`, `language-configuration.json`, validator, tests | Extension stays adapter-only and follows shipped grammar forms for guarded headers and conditional law routes. | Prevents three editor-side syntax stories from drifting away from the compiler. | include |
| Legacy authored routes | `doctrine/grammars/doctrine.lark::route_stmt`, `doctrine/model.py::RouteLine`, `doctrine/compiler.py::_compile_section_body()` | Hard-cut deletion of the legacy authored-route path. | Worth considering eventually, but it widens scope beyond the requested Slice A convergence run. | defer |
| Extra docs outside the live docs set | `docs/STDLIB_LAYERS.md`, `docs/DOCTRINE_AGENT_DATA_FLOW_VISUALIZATION_2026-04-10.md`, `docs/REVIEW_SPEC.md` | Align every non-primary doc in the same run. | Important to notice, but not part of the core live docs set this plan needs to ship cleanly. | defer |
| Host-fact semantics | new compiler root kind or editor-side synthetic roots | Introduce a special host-fact root distinct from declared inputs. | Adds new semantics and duplicate truth without necessity in this run. | exclude |
| Prose policing | prose parser for `standalone_read` or editor-side semantic checks | Parse authored prose to prove guard discipline or route/output agreement. | Would invent hidden behavior and a second semantic system. | exclude |
<!-- arch_skill:block:call_site_audit:end -->

# 7) Depth-First Phased Implementation Plan (authoritative)

<!-- arch_skill:block:phase_plan:start -->
> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan. Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. No fallbacks/runtime shims. Keep `doctrine/` as the semantic owner, keep refs/docs/editor surfaces downstream, and prefer existing proof lanes over new harnesses.

Warn-first note:

- `external_research_grounding` is still not started in `planning_passes`.
- That does not block this phase plan because internal grounding, target architecture, and the call-site audit are already strong enough to drive implementation.
- If implementation uncovers a real design ambiguity that the current repo cannot answer, stop and route that specific gap through `external-research` before widening the code path.

## Phase 1 — Compiler-owned Slice A convergence

Status: COMPLETE

Completed work:
- Created the implementation worklog at
  `docs/SPEC_1_3_END_TO_END_IMPLEMENTATION_PLAN_2026-04-10_WORKLOG.md`.
- Synced the repo with `uv sync`.
- Ran the current targeted route-only manifests for `40`, `41`, and `42` as a
  baseline before code changes. They passed against the old shipped behavior,
  which confirmed the active corpus still encoded the pre-fix route-only story.
- Fixed compiler-owned route-only condition rendering so the boolean comparison
  wording used by the route-only ladder now reads naturally instead of leaking
  raw comparison structure into the rendered output.
- Landed proposal rule 9 on the compiler-owned path without new grammar:
  routed `next_owner` fields must now structurally bind the routed target
  through the existing interpolation surface.
- Landed the honest proposal rule 10 enforcement boundary on the
  compiler-owned path: `standalone_read` may not structurally interpolate
  guarded output detail, while arbitrary prose remains outside compiler proof.
- Narrowed guarded-output source wording in diagnostics to the shipped surface
  of declared inputs and enum members.
- Added the new compiler diagnostics needed to make those boundaries explicit:
  `E339` for routed `next_owner` fields that do not structurally bind the route
  target, and `E340` for `standalone_read` interpolations that reach guarded
  output detail.
- Re-ran the targeted ladder manifests for `30`, `39`, `40`, `41`, and `42`
  against the corrected compiler behavior and they passed.
- Ran `make verify-diagnostics` after the diagnostics changes and it passed.

* Goal:
  Land the minimum Doctrine core changes needed so Slice A semantics, validation, and compiled wording are correct on the canonical `doctrine/grammars/doctrine.lark` -> `doctrine/parser.py` -> `doctrine/model.py` -> `doctrine/compiler.py` path.
* Work:
  - Preserve the shipped syntax and typed AST split unless implementation finds a real parser/model bug.
  - Fix compiler-owned route-only rendering on the law path, especially the condition-rendering helpers that currently produce broken wording in example `40`.
  - Keep all enforceable route-only semantics on the law-owned path and keep `RouteLine` frozen as legacy behavior.
  - Resolve proposal rule 9 (`next_owner` agreement) on the compiler-owned path.
    Use an existing structured output surface if possible; if not, only the
    smallest explicit binding surface is allowed, and the decision must be
    recorded rather than hidden behind docs or example convention.
  - Preserve the narrow guarded-output namespace and, if needed, narrow diagnostics wording so docs and errors stop promising a hidden host-fact root.
  - Define the honest non-prose-parser proof boundary for proposal rule 10
    (`standalone_read` guard discipline) so Phase 2 can add integrated proof
    without pretending the compiler can parse arbitrary prose.
  - Keep renderer policy-free; only touch `doctrine/renderer.py` if the serializer itself is wrong rather than the compiled section tree.
  - Keep emitted-ref generation downstream via `doctrine/emit_docs.py`; do not hand-patch refs as a substitute for core fixes.
* Verification (smallest signal):
  - Run targeted corpus checks for `examples/30_law_route_only_turns/cases.toml`, `examples/39_guarded_output_sections/cases.toml`, `examples/40_route_only_local_ownership/cases.toml`, `examples/41_route_only_reroute_handoff/cases.toml`, and `examples/42_route_only_handoff_capstone/cases.toml`.
  - Run `make verify-diagnostics` if diagnostics text or error mappings change.
* Docs/comments (propagation; only if needed):
  - Add or tighten only high-leverage comments at the compiler boundary if the law-route / guarded-output split would otherwise be easy to misread later.
* Exit criteria:
  - Targeted manifests for the `30` / `39` / `40` / `41` / `42` ladder pass against the corrected compiler behavior.
  - Proposal rule 9 has a compiler-owned implementation path that is explicit
    enough to verify and does not depend on hidden magic.
  - The plan for proposal rule 10 proof is explicit and honest before Phase 2
    starts adding corpus coverage.
  - No new semantic ownership has leaked into renderer, refs, docs, or the editor.
  - `RouteLine` remains legacy-only and Slice A behavior is owned by workflow law plus output.
* Rollback:
  - Revert the core patchset as one unit if full-corpus preservation signals fail or if the implementation starts requiring a second semantic path instead of converging onto the compiler-owned one.

## Phase 2 — Example, emitted-ref, and live-doc convergence

Status: COMPLETE

Completed work:
- Updated the route-only ladder examples so the authored prompts and expected
  rendered refs now follow the corrected compiler behavior instead of preserving
  the old hand-authored drift.
- Strengthened the route-only proof surfaces with two new manifest-backed
  failure cases:
  `examples/41_route_only_reroute_handoff/prompts/INVALID_NEXT_OWNER_OMITS_ROUTE_TARGET.prompt`
  for `E339`, and
  `examples/42_route_only_handoff_capstone/prompts/INVALID_STANDALONE_READ_REFERENCES_GUARDED_DETAIL.prompt`
  for `E340`.
- Refreshed the affected emitted refs through the normal emit/verify path and
  deleted the stale empty ref directory at
  `examples/42_route_only_handoff_capstone/ref/route_only_handoff_capstone_demo`.
- Synced the touched live docs so they now describe the shipped Slice A
  boundary: `docs/WORKFLOW_LAW.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md`,
  `docs/README.md`, and `examples/README.md`.
- Re-ran the touched ladder manifests while iterating and kept the examples,
  refs, and docs aligned to the compiler-owned truth.

* Goal:
  Make the public teaching/proof surfaces follow the corrected core truth without preserving illustrative mistakes.
* Work:
  - Update the route-only and guarded-output ladder examples in `30`, `39`, `40`, `41`, and `42`.
  - Keep `30` as the no-carrier setup, `39` as the guarded-output anchor, and `40` to `42` as the route-only ladder outside `trust_surface`.
  - Strengthen manifests only through existing proof kinds such as
    `render_contract`, `parse_fail`, `compile_fail`, and `build_contract`.
  - Add integrated proof coverage for proposal rules 9 and 10 in the `40` to
    `42` ladder using the strongest honest manifest-backed signals available
    after Phase 1.
  - Refresh emitted refs through the normal emit path after the compiler wording is correct.
  - Delete `examples/42_route_only_handoff_capstone/ref/route_only_handoff_capstone_demo`.
  - Sync the live docs that would otherwise drift: `docs/WORKFLOW_LAW.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md` when needed, `docs/LANGUAGE_DESIGN_NOTES.md` where it still describes current language decisions, `docs/README.md`, and `examples/README.md`.
* Verification (smallest signal):
  - Re-run the touched ladder manifests individually while iterating.
  - Refresh the affected emit targets if the example refs are regenerated in this phase.
* Docs/comments (propagation; only if needed):
  - Rewrite any touched example comments or notes that still imply route-only `trust_surface`, broad host-fact access, or stale capstone wording.
* Exit criteria:
  - The touched examples, manifests, refs, and live docs all tell the same Slice A story.
  - The numbered ladder no longer treats proposal rules 9 and 10 as invisible
    gaps; it either proves them with the agreed honest signals or records the
    exact remaining limit without ambiguity.
  - No checked-in ref remains as a known-bad render snapshot.
  - No touched live doc still promises behavior the compiler does not ship.
* Rollback:
  - Hold or revert ref/doc refreshes if they drift from the core implementation, and treat the core/compiler output as the authority until the public surfaces are re-aligned.

## Phase 3 — VS Code adaptation and proof expansion

Status: COMPLETE

Completed work:
- Updated `editors/vscode/resolver.js` so guarded output headers are treated as
  intentional record bodies and conditional law routes
  (`route "..." -> Agent when expr`) are definition-resolvable supported forms
  instead of incidental fallbacks.
- Updated `editors/vscode/syntaxes/doctrine.tmLanguage.json` and
  `editors/vscode/language-configuration.json` so guarded output headers and
  conditional law routes colorize and indent correctly.
- Expanded `editors/vscode/scripts/validate_lark_alignment.py` so the extension
  validates the lexical forms it now intentionally supports, including guarded
  output headers and both plain and conditional law-route endings.
- Expanded the unit, snapshot, and integration coverage for examples `39`
  through `42`, including guarded-output path navigation and conditional route
  target navigation.
- Added snapshot-fixture coverage for the corrected `39` to `42` prompts under
  `editors/vscode/tests/snap/examples/`.
- Rewrote the extension README notes so they match the corrected highlighting
  and click-through surface.
- Ran `cd editors/vscode && make` and it passed.

* Goal:
  Make the existing VS Code extension correctly colorize and resolve click-through for the corrected `39` through `42` surface without turning the extension into a second semantic engine.
* Work:
  - Keep `extension.js` and `package.json` thin; imports stay `DocumentLink`-only and the relevant route-only / guarded-output click path stays on the definition provider.
  - Update `editors/vscode/resolver.js` so guarded output sections and conditional law routes are intentional supported paths instead of incidental fallbacks.
  - Update `editors/vscode/syntaxes/doctrine.tmLanguage.json` so guarded headers and `route "..." -> Agent when expr` are first-class lexical forms.
  - Update `editors/vscode/language-configuration.json` so guarded headers indent correctly.
  - Expand `editors/vscode/scripts/validate_lark_alignment.py` only for the lexical forms it actually owns.
  - Add the missing unit, snapshot, and integration coverage for examples `39` through `42`.
  - Rewrite `editors/vscode/README.md` and any touched resolver boundary comments if the supported surface changes.
* Verification (smallest signal):
  - Run `cd editors/vscode && make`.
  - Ensure the added unit, snapshot, integration, and validator coverage passes on the corrected example set.
* Docs/comments (propagation; only if needed):
  - Update extension README support notes and boundary comments so they describe the actual supported click/highlighting surface.
* Exit criteria:
  - Examples `39` through `42` are covered by explicit VS Code proof rather than incidental support.
  - Conditional law routes no longer rely on generic resolver fallback for click-through.
  - Guarded section headers highlight and indent correctly.
* Rollback:
  - Revert the extension patchset independently if editor packaging/tests fail, while keeping the core/compiler/docs work intact.

## Phase 4 — Final convergence verification and ship cleanup

Status: COMPLETE

Completed work:
- Ran the full shipped corpus verification with `make verify-examples` and it
  passed.
- Re-ran `make verify-diagnostics` after the final diagnostics/doc convergence
  and it passed.
- Re-ran the full VS Code extension build/test/package flow with
  `cd editors/vscode && make` and it passed.
- Confirmed the stale ref directory was removed and the touched live docs and
  extension README no longer describe the retired route-only drift.
- Automated extension-host integration coverage passed for the user-visible
  editor behavior this run changed, including guarded section navigation and
  conditional route navigation.

Manual QA (non-blocking):
- No separate interactive GUI editor smoke session was run during this terminal
  pass. The honest remaining manual-only gap is the absence of a live click/test
  in an open VS Code window beyond the automated extension-host coverage above.

* Goal:
  Prove the full convergence run end to end and clear the remaining cleanup needed before implementation is considered complete.
* Work:
  - Run the full shipped corpus verification.
  - Run diagnostics verification if diagnostics changed.
  - Re-run the full VS Code extension build/test/package flow.
  - Confirm the stale ref directory is gone and no touched live doc/comment/instruction still describes retired behavior.
  - Perform a short manual editor smoke check on the corrected examples:
    `39` guarded section navigation, `41` reroute target navigation, `42` conditional route navigation, and colorization for guarded headers / conditional routes.
* Verification (smallest signal):
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics changed
  - `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  - Clean up any final stale comments, README notes, or emitted-ref usage notes discovered during the final pass.
* Exit criteria:
  - Full repo checks for the touched surfaces pass.
  - Manual editor smoke confirms the exact user-visible colorizing and link-click behavior requested.
  - The plan can move cleanly to `implement` / completion audit without open Slice A drift items.
* Rollback:
  - Reopen the earliest failing phase and revert only the latest convergence layer that introduced the regression instead of patching around it with fallbacks.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

Use the repo's shipped checks as the primary trust signals.

- Prefer targeted `uv run --locked python -m doctrine.verify_corpus --manifest ...`
  while landing core and example changes, then use the full corpus at the end of
  the run.
- Run `make verify-examples` for end-to-end corpus correctness.
- Run `make verify-diagnostics` if diagnostics or error surfaces change.
- Run `cd editors/vscode && make` for extension packaging/tests when the editor
  support changes.
- Use the emit path only to refresh downstream refs after compiler/render truth
  is settled; do not treat emitted refs as a substitute for manifest-backed
  proof.
- Add or update the smallest stable proof cases needed to catch Slice A semantic
  drift and VS Code highlighting/navigation regressions without inventing a new
  verification harness.
- Carry proposal rules 9 and 10 with the strongest honest signals we can land:
  compiler-owned structured checks where available, and manifest-backed proof
  where the current language boundary stops short of prose parsing.
- Keep final manual QA short and specific to the user-visible surfaces this plan
  changes: corrected route-only renders plus VS Code colorizing and
  click-through on examples `39` through `42`.

# 9) Rollout / Ops / Telemetry

This change is primarily a language/runtime/docs/editor convergence change, not
an operational rollout. The main rollout surface is shipping corrected docs,
example refs, and a working VS Code extension package alongside the core
implementation so users do not see mismatched behavior between the CLI/compiler
and the editor.

# 10) Decision Log (append-only)

- 2026-04-10: Initial full-arch plan created from the request to implement
  `docs/PROPOSAL_SPEC1_3.md` end to end. The plan explicitly treats
  hand-authored examples and current rendered output as non-authoritative when
  they drift from intended Slice A behavior, and it includes VS Code
  colorizing/link-click support in scope instead of leaving editor behavior as
  follow-up.
- 2026-04-10: Deep-dive locked the canonical Slice A owner path to
  `doctrine/grammars/doctrine.lark` -> `doctrine/parser.py` ->
  `doctrine/model.py` -> `doctrine/compiler.py`, froze `RouteLine` as a legacy
  non-Slice-A path, kept route-only examples `40` through `42` outside
  `trust_surface`, interpreted “host facts” as declared host-supplied inputs for
  this run, kept inline conditional law-route syntax as a first-class shipped
  surface because the grammar already ships it, and explicitly rejected prose
  parsing, hidden magic-key semantics, and editor-side semantic enforcement as
  out of scope for this implementation.
- 2026-04-10: A second deep-dive hardening pass normalized Sections 4 through 6
  onto the canonical arch-step subsection shape, added `doctrine/emit_docs.py`
  plus the concrete rendered-ref refresh path to the call-site audit, pulled in
  `docs/COMPILER_ERRORS.md` and `docs/LANGUAGE_DESIGN_NOTES.md` as live docs to
  sync when wording changes, and expanded the VS Code inventory to name the
  exact validator, unit, snapshot, and integration surfaces that must cover the
  corrected `39` through `42` ladder. This pass intentionally did not mark
  `deep_dive_pass_2` complete because no external research had been folded in.
- 2026-04-10: `phase-plan` wrote the authoritative execution checklist in
  Section 7. The plan proceeds despite missing external research because the
  repo-grounded architecture and call-site audit are already strong enough to
  implement; if implementation finds a real unresolved design gap, that gap is
  routed through `external-research` instead of widening the code path by
  assumption.
- 2026-04-10: Proposal-alignment audit found one real miss in the earlier plan:
  it had treated proposal rules 9 and 10 as if they were broadly deferred from
  this run. The corrected plan now keeps the no-prose-parser and no-hidden-magic
  stance, but it explicitly carries `next_owner` agreement and
  `standalone_read` guard-discipline proof forward as implementation work rather
  than silently demoting them to docs-only burden.
- 2026-04-10: Phase 1 implementation resolved proposal rule 9 by requiring
  routed `next_owner` fields to structurally bind the route target through the
  existing interpolation surface instead of introducing new grammar or a hidden
  magic-key semantic path.
- 2026-04-10: Phase 1 implementation resolved the honest proposal rule 10
  boundary by rejecting `standalone_read` interpolations that descend into
  guarded output detail while explicitly leaving arbitrary free prose outside
  compiler parsing and proof.
- 2026-04-10: Phase 3 adaptation made guarded output headers and conditional law
  routes first-class VS Code support surfaces, with explicit resolver,
  highlighting, indentation, validator, snapshot, and integration coverage for
  the corrected `39` through `42` ladder.
- 2026-04-10: `audit-implementation` found the planned code work complete. No
  phases were reopened. The only remaining item is a non-blocking manual VS
  Code smoke pass in a live editor window; automated extension-host coverage is
  already present for the guarded-section and conditional-route navigation this
  run changed.
- 2026-04-10: A repeat `audit-implementation` pass after the later
  `implement` re-entry rechecked the plan against current repo reality and kept
  the same verdict: no missing code work, no reopened phases, and only the
  non-blocking live VS Code smoke remaining.
