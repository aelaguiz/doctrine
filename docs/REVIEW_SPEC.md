# Review

Doctrine's `review` surface is the typed semantic home for reviewer and critic
turns. It keeps verdicts, failing gates, current truth, carried state, and
next-owner routing compiler-owned instead of spreading them across prose
conventions.

For the language overview, use [LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md).
For the numbered proof ladder, use [../examples/README.md](../examples/README.md).
If you first need to decide whether the turn should be a `review` at all, use
[AUTHORING_PATTERNS.md](AUTHORING_PATTERNS.md).

## Mental Model

The governing split is:

- `review` decides what was reviewed, what failed, what passed, what remains
  current, and who owns next
- `output` still decides what the review emits
- routed-owner readback on emitted outputs may use the shared `route.*`
  semantic surface when the review resolves a real route
- `trust_surface` still marks which emitted fields downstream owners may trust

This is the same split workflow law uses for producer turns:

- semantic truth stays compiler-owned
- emitted contracts stay on declared outputs
- there is no review-only packet, route payload, or shadow trust channel

## Surface Overview

Doctrine ships:

- top-level `review`
- top-level `review_family`
- top-level `abstract review`
- an agent `review:` slot

Important rules:

- `review` is a first-class declaration, not a workflow naming convention
- `review_family` is a first-class reusable review scaffold on the same review
  compiler path
- a concrete agent may not define both `workflow:` and `review:`
- an `abstract review` may not be attached directly to a concrete agent
- a concrete agent may attach a `review_family` directly only when the family
  is already concrete, such as an exhaustive case-selected family
- the concrete agent must still emit the review's declared `comment_output`
- when a review-driven agent uses `final_output:`, it may either reuse that
  same `comment_output` or point at another emitted `TurnResponse`; the
  review's `comment_output` still remains the review carrier
- `comment_output:` may point at an imported reusable `output`, and that
  shared output may still structurally bind local routed owners on the
  concrete review without cloning the declaration into the local module

## Review Contracts

`contract:` points at a named `workflow` or `schema` that acts as the shared
review contract.

Example:

```prompt
workflow DraftReviewContract: "Draft Review Contract"
    completeness: "Completeness"
        "Confirm the draft covers the required sections."

    clarity: "Clarity"
        "Confirm the draft states the next action clearly."
```

A workflow contract exports its first-level keyed sections as gate identities.
A schema contract exports its named `gates:` items the same way.

Schema example:

```prompt
schema PlanReviewContract: "Plan Review Contract"
    gates:
        outline_complete: "Outline Complete"
            "Confirm the draft has a complete outline."

        evidence_grounded: "Evidence Grounded"
            "Confirm the draft is grounded in cited evidence."
```

Exported gate identities include:

- `contract.completeness`
- `contract.clarity`
- `contract.outline_complete`
- `contract.evidence_grounded`

The shipped review semantics also expose:

- `contract.passes`
- `contract.failed_gates`

Workflow contracts may use ordinary workflow prose, composition, and
inheritance. Schema contracts use `sections:` and optional `gates:`. Neither
contract surface is the place for operational route or currentness semantics.

## Core Review Configuration

A concrete review declares:

- `subject:`: one reviewed input or output root, or a set of candidate roots
- `subject_map:`: the mode-to-subject disambiguation surface when multiple
  subjects are in play
- `contract:`: the shared contract workflow or schema
- `comment_output:`: the durable emitted review comment
- `fields:`: semantic field bindings inside that output

Minimal shape:

```prompt
review DraftReview: "Draft Review"
    subject: DraftSpec
    contract: DraftReviewContract
    comment_output: DraftReviewComment

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner
```

## Review Families And Case Selection

`review_family` is the reusable review surface when multiple reviews share the
same durable comment contract, handoff-first scaffolds, or exhaustive
mode-selected cases.

Two shipped patterns are now valid:

- a child `review` inherits a `review_family` and explicitly accounts for the
  inherited entries it keeps
- a concrete agent attaches a case-complete `review_family` directly through
  `review:`

Case-selected review families use one explicit selector plus exhaustive cases:

```prompt
selector:
    mode selected_mode = ReviewFacts.selected_mode as ReviewMode

cases:
    draft_path: "Draft Path"
        when ReviewMode.draft_rewrite
        subject: DraftSpec
        contract: DraftReviewContract
        checks:
            accept "The draft review contract passes." when contract.passes
        on_accept:
            current artifact DraftSpec via SelectedReviewComment.current_artifact
            route "Accepted draft rewrite returns to RevisionOwner." -> RevisionOwner
        on_reject:
            current artifact DraftSpec via SelectedReviewComment.current_artifact
            route "Rejected draft rewrite returns to RevisionOwner." -> RevisionOwner
```

Important rules:

- case selectors must be non-overlapping and exhaustive
- each case declares exactly one `subject:`, one `contract:`, one `checks:`
  block, and both outcome sections
- shared pre-outcome sections still run before each case-local `checks:` block
- `fields:` may also bind `current_artifact` when reusable output logic needs
  `fields.current_artifact`

## Field Bindings

`fields:` is a distinct inherited binding surface, not a loose config bag.

Core field bindings for concrete reviews:

- `verdict`
- `reviewed_artifact`
- `analysis`
- `readback`
- `next_owner`
- `failing_gates`

Conditionally required bindings:

- `blocked_gate`: required when the review uses `block`
- `active_mode`: required when an outcome carries downstream mode
- `trigger_reason`: required when an outcome carries downstream trigger state

These bindings are relative to `comment_output`.

Important rule:

- `fields:` does not alias currentness. Review currentness still uses the
  direct carrier form `current artifact ... via output_root.field`.

## Review Outputs And Shared Route Semantics

Review-specific semantic names stay on the review surface:

- `verdict`
- `contract.*`
- `fields.*`

When a review branch also resolves a real route, any emitted output on that
turn may additionally read shared route semantics through:

- `route.exists`
- `route.next_owner`
- `route.next_owner.key`
- `route.next_owner.title`
- `route.label`
- `route.summary`
- `route.choice`
- `route.choice.key`
- `route.choice.title`
- `route.choice.wire`

Important rules:

- `route.*` is derived compiler truth, not another authored review field
- `route.choice.*` is live only when every live routed branch comes from
  `route_from`
- use verdict guards, `when route.exists:`, or both when some review branches
  do not share the same routed owner
- split review `final_output:` contracts may consume the same `route.*` truth
  without replacing `comment_output` as the durable review carrier

## Pre-Outcome Review Logic

Before the review resolves to accept or reject, it can evaluate:

- `block`
- `reject`
- `accept`
- `preserve`
- `support_only`
- `ignore`
- `when`
- `match`
- prose

Named pre-outcome sections are ordinary keyed review sections and behave like
the rest of Doctrine's patchable structure.

Example:

```prompt
start_review: "Start Review"
    block "Producer handoff is incomplete." when ProducerHandoff.invalid
    reject contract.handoff_truth when ProducerHandoff.names_wrong_current_artifact

evidence_checks: "Evidence Checks"
    support_only AcceptedPeerSet for comparison when ReviewState.peer_comparison_used
    preserve exact ApprovedBoundary.exact_scope_boundary
    accept "The shared capstone review contract passes." when contract.passes
```

Important rules:

- `block` is the handoff-first gate surface. A blocked review still emits one
  durable `changes_requested` comment.
- `accept` is the one accepting gate for the review.
- `preserve`, `support_only`, and `ignore` reuse the same meaning they have in
  workflow law, but here they apply to reviewer semantics.

## Gate Evaluation Order

Review gate ordering is deterministic.

1. Evaluate `block` gates in source order.
2. If any `block` gate fires, verdict becomes
   `ReviewVerdict.changes_requested` and content review stops for that branch.
3. Evaluate local `reject` gates and assertion-style sections.
4. Evaluate the referenced contract surface.
5. If no failures remain, evaluate the single `accept` gate.

This is why the review ladder can keep `failing_gates`, `blocked_gate`, and
contract failures exact instead of advisory prose.

## Outcome Sections

Every concrete review must define:

- `on_accept`
- `on_reject`

Outcome sections may contain:

- `current artifact ... via ...`
- `current artifact ... via ... when expr`
- `current none`
- `current none when expr`
- `carry active_mode = ...`
- `carry trigger_reason = ...`
- `route "..." -> Agent`
- `route "..." -> Agent when expr`
- `when`
- `match`
- prose

Example:

```prompt
on_accept: "If Accepted"
    current artifact DraftSpec via DraftReviewComment.current_artifact
    route "Accepted draft returns to ReviewLead." -> ReviewLead

on_reject: "If Rejected"
    current none
    route "Rejected draft returns to DraftAuthor." -> DraftAuthor
```

Blocked review outcomes may also split currentness explicitly:

```prompt
on_reject: "If Rejected"
    current artifact DraftSpec via DraftReviewComment.current_artifact when missing(blocked_gate)
    current none when present(blocked_gate)
    route "Rejected draft returns to DraftAuthor." -> DraftAuthor
```

Important rules:

- every terminal review branch must resolve exactly one currentness result
- a terminal review branch may route or stop without a route
- when some review outcomes route and others do not, the companion contract
  reports that route behavior per normalized outcome
- blocked outcomes may use `current none`, including guarded
  `current none when present(blocked_gate)` splits
- carried fields remain on emitted output fields, not on routes

## Verdicts And Semantic Refs

Review has exactly two language verdicts:

- `ReviewVerdict.accept`
- `ReviewVerdict.changes_requested`

Review logic and review-bound outputs can read resolved semantic names such as:

- `verdict`
- `contract.<gate>`
- `contract.passes`
- `fields.<semantic_field>`
- helper-style expressions such as `present(active_mode)`

That is why guarded output items like these are legal on review comments:

```prompt
next_owner: route.next_owner when route.exists
```

```prompt
failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
    failing_gates: "Failing Gates"
        "Name the failing review gates in authored order."
```

## Review Output Agreement And Trust

Review output agreement is compiler-owned and fail-loud.

The compiler validates that bound output fields stay aligned with review
semantics:

- verdict
- failing gates and blocked gate
- next owner
- currentness carrier fields
- carried `active_mode`
- carried `trigger_reason`
- required conditional output sections

`trust_surface` remains the downstream trust contract even on review comments.
Review does not invent a second trust channel.
Because `comment_output` is still an ordinary `output`, review comments may
also use the shared readable block kinds that ordinary outputs ship, such as
`definitions`, `properties`, explicit `guard` shells, `callout`, or `code`,
alongside guarded output items.
That same `comment_output` may also be the agent's `final_output:` when the
review should end with a dedicated prose or schema-backed JSON final-answer
contract.
A review-driven agent may also point `final_output:` at a second emitted
`TurnResponse` output. In that split shape, `comment_output` stays the durable
review carrier while the separate final output inherits the same review
semantic refs and guards.
That split final output may also bind a review-semantic subset:

```prompt
final_output:
    output: AcceptanceControlFinalResponse
    review_fields:
        verdict: verdict
        current_artifact: current_artifact
        next_owner: next_owner
        blocked_gate: blocked_gate
```

The compiler emits whether that split final response is `control_ready`.
Authors do not declare that mode by hand.
Imported reusable review comments keep that same behavior: the bound output
field still lives on the imported `comment_output`, while bare owner refs that
are missing from the imported module may still bind the concrete review's
local routed agents.

## Multi-Subject Review And Carried State

Review can model one subject or a reviewed subject family.

Example pattern:

```prompt
subject: {DraftSpec, MetadataRecord}
subject_map:
    ReviewMode.draft_rewrite: DraftSpec
    ReviewMode.metadata_refresh: MetadataRecord
```

This lets one review keep:

- different current artifacts
- different carried modes
- different carried trigger reasons
- the same next owner, when that is the honest outcome

Carried state still moves through bound output fields, typically on
`comment_output`, and may then be listed in `trust_surface` when downstream
owners should trust it.

## Inheritance And Patching

`review` uses the same explicit inheritance model as the rest of Doctrine.

Inherited review surfaces include:

- `fields`
- named pre-outcome sections
- `on_accept`
- `on_reject`

Important rules:

- use `review_family` for reusable shared review scaffolds that should stay on
  the ordinary review path
- use `abstract review` for inheritance-only review doctrine when no dedicated
  family surface is needed
- children must account for inherited review surfaces explicitly
- `override` requires a real inherited target
- inherited review structure is not implicitly merged by omission

## Bound Roots

Review currentness and carried-state carriers can normalize through concrete
turn bindings just like workflow law does.

That means these are valid shipped patterns:

- `current artifact draft_spec via review_comment.current_artifact`
- `carry active_mode = ReviewMode.draft_rewrite`
- `carry trigger_reason = TriggerReason.structure_gap`

The local roots `draft_spec` and `review_comment` are concrete-turn bindings,
not shadow aliases.

## Example Ladder

Read the review examples in this order:

- `43_review_basic_verdict_and_route_coupling`: the smallest first-class
  review
- `44_review_handoff_first_block_gates`: blocked review and `blocked_gate`
- `45_review_contract_gate_export_and_exact_failures`: exact contract gate
  export and faithful `failing_gates`
- `46_review_current_truth_and_trust_surface`: review-owned current truth on a
  trusted output carrier, including blocked-gate-guarded currentness
- `47_review_multi_subject_mode_and_trigger_carry`: subject families and
  carried downstream state
- `48_review_inheritance_and_explicit_patching`: `abstract review` plus
  explicit review patching
- `49_review_capstone`: the integrated review surface
- `53_review_bound_carrier_roots`: bound review carriers and carried state
- `57_schema_review_contracts`: schema-backed review contracts with exported
  schema gates
- `68_review_family_shared_scaffold`: dedicated `review_family` reuse with
  explicit inherited scaffold accounting
- `69_case_selected_review_family`: exhaustive case-selected review families
- `88_review_route_semantics_shared_binding`: review comments mixing review
  semantics and shared `route.*`
- `90_split_handoff_and_final_output_shared_route_semantics`: split durable
  review comments plus route-aware JSON `final_output:`
