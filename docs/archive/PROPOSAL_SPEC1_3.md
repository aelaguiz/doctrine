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
