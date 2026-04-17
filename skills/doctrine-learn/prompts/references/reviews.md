# Reviews

This reference teaches how to author reviewer and critic turns. Doctrine ships
a first-class `review` surface and a reusable `review_family` surface, both on
the same compiler path. Use them when the turn judges an artifact and routes
the next owner based on a verdict.

Review is not a workflow naming convention. It is a typed declaration with
compiler-owned verdicts, gates, currentness, carried state, and next-owner
routing.

Read the source of truth in this order before you ship code:

- `doctrine/grammars/doctrine.lark`
- `docs/REVIEW_SPEC.md`
- `docs/LANGUAGE_REFERENCE.md` (review and review_family sections)

## Declaration Shape

A minimal concrete review looks like this:

```prompt
review DraftReview: "Draft Review"
    subject: DraftSpec
    contract: DraftReviewContract
    comment_output: DraftReviewComment

    fields:
        verdict
        reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner

    contract_checks: "Contract Checks"
        accept "The shared contract passes." when contract.passes

    on_accept: "If Accepted"
        current artifact DraftSpec via DraftReviewComment.current_artifact
        route "Accepted draft returns to ReviewLead." -> ReviewLead

    on_reject: "If Rejected"
        current none
        route "Rejected draft returns to DraftAuthor." -> DraftAuthor
```

Core review fields:

- `subject:` is the reviewed input or output root, or a set when the review
  has multiple subjects.
- `contract:` is a named `workflow` or `schema`. Its first-level keyed
  sections (or schema `gates:`) become gate identities like `contract.clarity`.
- `comment_output:` is the durable emitted review comment. It must still be an
  ordinary `output`.
- `fields:` binds review semantic channels onto paths inside
  `comment_output`.
- `on_accept:` and `on_reject:` resolve currentness, carried state, and
  routing for each terminal branch.

See `examples/84_review_split_final_output_prose` for a minimal review paired
with a separate prose final output.

### Field Bindings

Core field bindings for concrete reviews are `verdict`, `reviewed_artifact`,
`analysis`, `readback`, `next_owner`, and `failing_gates`.

Conditional bindings:

- `blocked_gate`: required when the review uses `block`.
- `active_mode`: required when an outcome carries downstream mode.
- `trigger_reason`: required when an outcome carries downstream trigger state.

Bare identity shorthand:

- `verdict` is shorthand for `verdict: verdict`.
- Use the bare form only when the output field key matches the review semantic
  name.
- Keep `semantic: path` for non-identity binds like
  `analysis: analysis_performed` or `failing_gates: failure_detail.failing_gates`.

### Pre-Outcome Logic

Before the review resolves to accept or reject, it may use `block`, `reject`,
`accept`, `preserve`, `support_only`, `ignore`, `when`, `match`, and prose.
Named pre-outcome sections are ordinary keyed sections and patch like the rest
of Doctrine.

Gate order is deterministic:

1. `block` gates in source order. A firing `block` makes the verdict
   `ReviewVerdict.changes_requested` and content review stops for that branch.
2. Local `reject` gates and assertion-style sections.
3. The referenced contract surface.
4. The single `accept` gate when no failures remain.

### Verdict Coupling

Review has exactly two language verdicts:

- `ReviewVerdict.accept`
- `ReviewVerdict.changes_requested`

The verdict gates review-bound output items. Use it in guarded sections like:

```prompt
failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
    failing_gates: "Failing Gates"
        "Name the failing review gates in authored order."
```

Because `comment_output` is still an ordinary `output`, review comments can
carry guarded items, trusted carriers, and readable blocks just like any
other output.

### Carried State And Current-Truth Carriers

Currentness uses direct carriers like `current artifact DraftSpec via
DraftReviewComment.current_artifact`. The carrier field must be listed in the
output's `trust_surface`.

Blocked outcomes may split currentness explicitly:

```prompt
on_reject: "If Rejected"
    current artifact DraftSpec via DraftReviewComment.current_artifact when missing(blocked_gate)
    current none when present(blocked_gate)
    route "Rejected draft returns to DraftAuthor." -> DraftAuthor
```

Carried fields such as `active_mode` and `trigger_reason` still move through
bound output fields and, when trusted downstream, through `trust_surface`.

## Composition

### Review Families

`review_family` is a reusable review scaffold on the same compiler path as
`review`. Use it when several reviews share the same durable comment contract
or mode-selected cases.

- `review_family` may own `comment_output`, `fields`, shared pre-outcome
  sections, `selector`, and exhaustive `cases`.
- A child `review` may inherit a `review_family` and account for inherited
  entries explicitly.
- A concrete agent may attach a `review_family` directly only when the family
  is already case-complete (for example, every case is exhaustively selected).

Case-selected families use one explicit selector plus exhaustive cases:

```prompt
selector:
    mode selected_mode = ReviewFacts.selected_mode as ReviewMode

cases:
    draft_path: "Draft Path"
        when ReviewMode.draft_rewrite
        subject: DraftSpec
        contract: DraftReviewContract
        checks:
            accept "The shared contract passes." when contract.passes
        on_accept:
            current artifact DraftSpec via SharedComment.current_artifact
            route "Accepted draft returns." -> RevisionOwner
        on_reject:
            current artifact DraftSpec via SharedComment.current_artifact
            route "Rejected draft returns." -> RevisionOwner
```

Case selectors must be non-overlapping and exhaustive. Each case declares
exactly one `subject:`, one `contract:`, one `checks:` block, and both outcome
sections.

### Review Inheritance

`review` uses the same explicit inheritance model Doctrine uses elsewhere.
Inherited review surfaces include `fields`, named pre-outcome sections,
`on_accept`, and `on_reject`. Children must account for every inherited
surface explicitly. `abstract review` is inheritance-only and cannot attach to
a concrete agent directly.

### Schema-Backed Review Contracts

`contract:` points at either a `workflow` or a `schema`. A schema contract
uses named `gates:` items that export as gate identities such as
`contract.outline_complete`. Output-attached schemas must still expose at
least one section. Schema contracts keep the same `contract.passes` and
`contract.failed_gates` semantic surface a workflow contract exports.

## Review-Driven final_output

On a review-driven agent, `final_output:` may either reuse the review's
`comment_output:` or point at another emitted `TurnResponse`. `comment_output`
stays the review carrier in either shape.

Short form (reuse the comment):

```prompt
agent ReviewDemo:
    review: DraftReview
    final_output: DraftReviewComment
```

Split form (second final output with prose or schema-backed JSON):

```prompt
final_output:
    output: AcceptanceControlFinalResponse
    review_fields:
        verdict
        current_artifact: current_artifact
        next_owner
        blocked_gate: blocked_gate
```

Important rules:

- The split final output inherits the review's semantic refs and guards.
- `review_fields:` accepts bare identity binds like `next_owner` when the
  final-output field key matches the review semantic name.
- The compiler emits whether that split final response is `control_ready`.
  Authors do not declare that mode by hand.
- When the designated output's `output shape` carries an `output schema`, the
  final assistant message is structured JSON. Otherwise it stays prose or
  markdown according to the output contract.

See these shipped examples:

- `examples/84_review_split_final_output_prose` — split prose final output.
- `examples/104_review_final_output_output_schema_blocked_control_ready` — a
  blocked review routing a `control_ready` JSON final.
- `examples/105_review_split_final_output_output_schema_control_ready` — a
  split JSON final that reports `control_ready`.
- `examples/106_review_split_final_output_output_schema_partial` — a partial
  (not control-ready) split JSON final.

## Imported Reusable Comment Outputs

`comment_output:` may point at an imported reusable `output`. Bare refs inside
that shared output resolve locally first, then may bind the concrete review's
local declarations when the imported module does not define them. That lets a
shared review comment name local routed owners without moving the declaration.

## When To Use A Review vs A Plain Output

Use `review` when:

- The turn judges an artifact and emits a verdict.
- The verdict changes downstream routing or invalidates downstream truth.
- You need typed `failing_gates`, `blocked_gate`, or carried state.
- You need `contract.*` exports for exact gate identities.

Use a plain `output` (under `workflow:` or `route_only`) when:

- The turn produces a new artifact rather than judging one.
- The route is decided by domain facts, not a verdict on an artifact.
- There is no shared contract surface to export as gates.

## Pitfalls

- Do not put `workflow:` and `review:` on the same concrete agent. The
  compiler rejects this.
- Do not pretend a review has a durable current artifact when it does not.
  Use `current none` on blocked outcomes.
- Do not merge inherited review structure by omission. Children must account
  for every inherited surface with `inherit`, `override`, or a new key.
- Do not invent a review-only route packet. The emitted `route` block in
  `final_output.contract.json` is the route contract. Bound output fields
  that show a next owner are content.
- Do not bind a review carrier field that is not listed in that output's
  `trust_surface`. The carrier rule is compiler-checked.
- Review has exactly two verdicts (`accept` and `changes_requested`). Do not
  invent a third.

## Related References

- `references/agents-and-workflows.md` — for the `review:` agent slot and
  when to pick `review` over `workflow` or `route_only`.
- `references/outputs-and-schemas.md` — for `comment_output` as an ordinary
  `output`, split JSON finals, and `review_fields:` plus `final_output.route:`.
- `references/imports-and-refs.md` — for importing reusable comment outputs
  and contracts across modules.

**Load when:** the author is adding a reviewer turn, a verdict gate, carried
review state, or a review-driven final output.
