---
title: "Doctrine - Spec 1.3 End-to-End Implementation - Architecture Plan"
date: 2026-04-10
status: active
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
correctly highlights and links the shipped language surfaces.

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
   mistakes get corrected or deleted and which renderer outputs become the real
   user-facing contract.
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

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: not started
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

## Phase alignment guidance (advisory; core planning commands adopt into Section 7 if needed)
### Global (applies across phases)
- Keep proposal freeze decisions and shipped workflow-law docs aligned with compiler-owned semantics, not with illustrative drift. (From: R1, R2)
- Any example/doc/ref correction must preserve the manifest-backed proof model and must not justify new language primitives just to save bad examples. (From: R1, R3)
- Keep `review` explicitly out of the current parser/compiler implementation plan even if staged review material remains referenced. (From: R1, R2)

### Phase 1 — Doctrine core semantics, diagnostics, and renderer
- Potentially relevant obligations (advisory):
  - Enforce the narrowed Slice A semantic boundary and keep `current none` as the only route-only currentness form. (From: R1, R2)
  - Preserve the narrowed output-guard namespace and fail-loud route/currentness rules. (From: R1, R2)
  - Make rendering reflect the intended layered law/output split and guarded-shell behavior. (From: R1, R2)
  - Account explicitly for the still-missing integrated proof around routed `next_owner` agreement and `standalone_read` guard discipline. (From: R1, R2, R3)
- References:
  - R1, R2, R3

### Phase 2 — Example, ref, and doc convergence
- Potentially relevant obligations (advisory):
  - Align examples `30`, `39`, `40`, `41`, and `42` to the corrected Slice A contract. (From: R1)
  - Keep the route-only ladder staged and narrow rather than turning examples into parallel semantics. (From: R2, R3)
  - Repair rendered refs and explanatory docs so they match the corrected implementation and the manifest-backed proof burden. (From: R1, R2, R3)
- References:
  - R1, R2, R3

### Phase 3 — VS Code surface alignment
- Potentially relevant obligations (advisory):
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
  surface and the requested VS Code colorizing/link clicks.
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

Research grounding will be completed in `research`. Current authoritative
anchors are the proposal doc for intended Slice A behavior, the shipped
workflow-law docs for current public surface, the `doctrine/` implementation,
the manifest-backed example corpus, and the VS Code extension sources under
`editors/vscode/`.

# 4) Current Architecture (as-is)

Current architecture will be grounded in `deep-dive`. This section must map the
real control paths from grammar to parser/model/compiler/renderer/verification,
plus the VS Code grammar and resolver paths, before implementation starts.

# 5) Target Architecture (to-be)

Target architecture will be defined in `deep-dive` after current-state
grounding. It must name the canonical owner path for Slice A semantics, the
renderer contract, the example/doc alignment rules, and the exact extension
boundary for highlighting and navigation.

# 6) Call-Site Audit (exhaustive change inventory)

The exhaustive change map will be built in `deep-dive`. It must cover the core
Doctrine implementation, active examples and refs, workflow-law docs, compiler
error docs, and the VS Code extension/test surfaces.

# 7) Depth-First Phased Implementation Plan (authoritative)

The authoritative phase plan will be written in `phase-plan` after research and
deep-dive make the change inventory trustworthy. It must keep the order
foundation-first: Doctrine core semantics, renderer/diagnostics, examples/docs,
then VS Code extension alignment and final verification.

# 8) Verification Strategy (common-sense; non-blocking)

Use the repo's shipped checks as the primary trust signals.

- Run `make verify-examples` for end-to-end corpus correctness.
- Run `make verify-diagnostics` if diagnostics or error surfaces change.
- Run `cd editors/vscode && make` for extension packaging/tests when the editor
  support changes.
- Add or update the smallest stable proof cases needed to catch Slice A semantic
  drift and VS Code highlighting/navigation regressions without inventing a new
  verification harness.

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
