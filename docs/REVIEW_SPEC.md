# Review

Doctrine's `review` surface is the typed semantic home for reviewer and critic
turns. It keeps verdicts, failing gates, current truth, carried state, and
next-owner routing compiler-owned instead of spreading them across prose
conventions.

For the language overview, use [LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md).
For the numbered proof ladder, use [../examples/README.md](../examples/README.md).

## Mental Model

The governing split is:

- `review` decides what was reviewed, what failed, what passed, what remains
  current, and who owns next
- `output` still decides what the review emits
- `trust_surface` still marks which emitted fields downstream owners may trust

This is the same split workflow law uses for producer turns:

- semantic truth stays compiler-owned
- emitted contracts stay on declared outputs
- there is no review-only packet, route payload, or shadow trust channel

## Surface Overview

Doctrine ships:

- top-level `review`
- top-level `abstract review`
- an agent `review:` slot

Important rules:

- `review` is a first-class declaration, not a workflow naming convention
- a concrete agent may not define both `workflow:` and `review:`
- an `abstract review` may not be attached directly to a concrete agent
- the concrete agent must still emit the review's declared `comment_output`

## Review Contracts

`contract:` points at a named `workflow` that acts as the shared review
contract.

Example:

```prompt
workflow DraftReviewContract: "Draft Review Contract"
    completeness: "Completeness"
        "Confirm the draft covers the required sections."

    clarity: "Clarity"
        "Confirm the draft states the next action clearly."
```

The first-level keyed sections in that contract become exported gate
identities:

- `contract.completeness`
- `contract.clarity`

The shipped review semantics also expose:

- `contract.passes`
- `contract.failed_gates`

Contract workflows may use ordinary workflow prose, composition, and
inheritance, but they are not the place for operational route or currentness
semantics.

## Core Review Configuration

A concrete review declares:

- `subject:`: one reviewed input or output root, or a set of candidate roots
- `subject_map:`: the mode-to-subject disambiguation surface when multiple
  subjects are in play
- `contract:`: the shared contract workflow
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
4. Evaluate the referenced contract workflow.
5. If no failures remain, evaluate the single `accept` gate.

This is why the review ladder can keep `failing_gates`, `blocked_gate`, and
contract failures exact instead of advisory prose.

## Outcome Sections

Every concrete review must define:

- `on_accept`
- `on_reject`

Outcome sections may contain:

- `current artifact ... via ...`
- `current none`
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

Important rules:

- every terminal review branch must resolve exactly one route
- every terminal review branch must resolve exactly one currentness result
- blocked outcomes may use `current none`
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

That is why guarded output sections like this are legal on review comments:

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

- use `abstract review` for inheritance-only review doctrine
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
  trusted output carrier
- `47_review_multi_subject_mode_and_trigger_carry`: subject families and
  carried downstream state
- `48_review_inheritance_and_explicit_patching`: `abstract review` plus
  explicit review patching
- `49_review_capstone`: the integrated review surface
- `53_review_bound_carrier_roots`: bound review carriers and carried state
