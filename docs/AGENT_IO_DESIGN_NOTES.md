# Agent I/O Model

Doctrine treats turn contracts as explicit declarations. Inputs say what a turn
may read. Outputs say what it emits. Workflow law or review says what those
outputs mean. `trust_surface` says which emitted fields downstream owners may
trust.

For the full declaration overview, use
[LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md). For workflow-law and review
semantics, use [WORKFLOW_LAW.md](WORKFLOW_LAW.md) and
[REVIEW_SPEC.md](REVIEW_SPEC.md). For the shipped emit and flow-diagram CLI,
use [EMIT_GUIDE.md](EMIT_GUIDE.md).
If you first need help choosing between `output`, `trust_surface`, `schema`,
`structure`, and `final_output:`, use
[AUTHORING_PATTERNS.md](AUTHORING_PATTERNS.md).

## Mental Model

- `input` and `inputs` describe consumed artifacts.
- `output` and `outputs` describe emitted artifacts.
- `final_output` marks the turn-ending assistant message when one emitted
  output should be treated specially.
- `trust_surface` marks portable downstream readback.
- Guarded output sections keep conditional readback on the output contract.
- Workflow law and review decide currentness, invalidation, verdicts, and
  carried state.
- Dedicated `review_family`, `route_only`, and `grounding` declarations still
  feed the same ordinary output and `trust_surface` boundary.

This keeps the split clean:

- output contracts are still the emitted contract surface
- typed `schema:` / `structure:` attachments stay on inputs or outputs
- shared readable blocks such as `definitions`, `properties`, `table`,
  explicit `guard` shells, `callout`, `code`, raw `markdown`, raw `html`,
  `footnotes`, and `image` may still appear on ordinary record bodies without
  becoming a second structure system
- named `table` declarations may be reused inside a `document` with a local
  table key, then lower to the same emitted table shape as inline tables
- compiler-owned semantics still live in `workflow law` or `review`
- downstream trust still flows through declared output fields, not through
  hidden side channels

## Inputs

An `input` describes one artifact the turn may read:

```prompt
input DraftSpec: "Draft Spec"
    source: File
        path: "unit_root/DRAFT_SPEC.md"
    shape: MarkdownDocument
    requirement: Required
```

Important rules:

- `source`, `shape`, and `requirement` are distinct axes.
- Built-in sources used in the shipped corpus include `Prompt`, `File`, and
  `EnvVar`.
- Custom sources may be declared with `input source`.
- When a previous-turn input source resolves one concrete upstream output,
  `emit_docs` records that derived contract under
  `final_output.contract.json.io.previous_turn_inputs`.
- Input bodies hold source-specific configuration plus authored explanatory
  prose.
- `structure:` may attach a named `document` to a markdown-bearing input shape.
- Input record bodies may also use ordinary readable blocks such as
  `definitions`, `table`, `callout`, and `code`.
- `inputs` blocks group inputs and optionally bind them under local keys for a
  concrete turn.

Binding example:

```prompt
inputs SharedInputs: "Inputs"
    draft_spec: DraftSpec

agent Demo:
    inputs: SharedInputs
```

That local key becomes a usable root for workflow law or review semantics.
Prefer the one-line form when the wrapper only binds one declaration and adds
no local prose. Keep the multiline wrapper when you need prose or more than
one direct item.

## Outputs

An `output` describes one emitted artifact:

```prompt
output ReviewComment: "Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required
```

Important rules:

- An output uses either `target` plus `shape`, or a titled `files:` section.
- Built-in targets used in the shipped corpus include `TurnResponse` and
  `File`.
- Custom targets may be declared with `output target`.
- Custom targets may bind one reusable delivery skill with `delivery_skill:`.
  The output still owns the artifact contract. The target owns where it goes
  and how delivery is described.
- Output shapes may be named with `output shape`.
- `schema:` on `output` attaches a Doctrine `schema` declaration.
- `schema:` on `output shape` points at an `output schema` when the shape kind
  is `JsonObject`.
- The field name stays owner-aware rather than globally retyped.
- `output schema` owns the machine-readable payload fields for structured
  `JsonObject` outputs.
- `output schema` may also declare an optional `example:` block. When present,
  Doctrine validates it and renders an `Example` section on structured final
  outputs.
- On the current structured-output profile, object properties stay present on
  the wire. That includes normal fields, route fields, and route-field
  overrides.
- Use `nullable` when an `output schema` field or route field may be `null`.
- `required` and `optional` are retired on this surface. Doctrine still
  parses them there only so it can raise targeted upgrade errors.
- Doctrine does not ship `?` shorthand for `output schema` fields.
- For a local closed string vocabulary inside `output schema`, prefer
  `type: enum` plus `values:`.
- In the first cut, legacy `type: string` plus `enum:` still compiles, and
  both forms lower to the same emitted string-enum wire shape.
- Doctrine `schema` declarations may now own reusable `sections:`, optional
  `gates:`, first-class `artifacts:`, and reusable `groups:`.
- Output-attached schemas must still expose at least one section even when the
  same schema also owns reusable artifacts or groups.
- `structure:` may attach a named `document` to a markdown-bearing output.
- A markdown-bearing `output` may not attach both `schema:` and `structure:`.
  Pick exactly one reusable owner for that artifact surface.
- `render_profile:` may attach a named markdown presentation policy to a
  markdown-bearing output.
- Ordinary output record bodies may reuse readable block kinds such as
  `definitions`, `properties`, `table`, explicit `guard` shells, `callout`,
  `code`, raw `markdown`, raw `html`, `footnotes`, and `image`.
- `output schema` still attaches beneath `output shape`; it does not replace
  `output`.
- `output Child[Parent]: "Title"` inherits one ordinary output contract and
  patches it with explicit top-level `inherit` or `override` entries.
- `outputs` blocks group outputs and may bind them under local keys for a
  concrete turn.
- Any emitted output may read shared compiler-owned route semantics through
  `route.exists`, `route.next_owner`, `route.next_owner.key`,
  `route.next_owner.title`, `route.label`, and `route.summary` when workflow
  law, `handoff_routing` law, `route_only`, `grounding`, or review resolves a
  real route.
- When every live routed branch on that turn comes from `route_from`, or when
  `final_output.route:` binds a `route field` on a structured final output,
  outputs may also read
  `route.choice`, `route.choice.key`, `route.choice.title`, and
  `route.choice.wire`.
- On `handoff_routing:`, only the slot's `law:` block makes `route.*` live.
  Prose route lines there stay readable only.
- `route.next_owner.*` may stay live across several `route_from` branches. It
  means the selected route owner.
- `route.label` and `route.summary` still need one selected branch. Guard them
  with `route.choice` when several route branches stay live.
- When `emit_docs` writes `final_output.contract.json`, that file includes the
  same compiler-owned route truth as a top-level `route` block. Harnesses
  should consume that block for routing. When a route comes from
  `final_output.route:`, that block also carries `route.selector` with the
  bound field path and null behavior. Output fields that show a next owner are
  content, not the route contract.
- The same companion file also carries a top-level `io` block.
  `io.previous_turn_inputs` records resolved previous-turn input contracts.
  `io.outputs` and `io.output_bindings` record emitted output contracts and
  readback binding paths.
- In authored output guards, `route.exists` means a routed owner exists on
  that live branch. In emitted `final_output.contract.json`, `route.exists`
  means the final response carries route semantics at all, even when an
  nullable route field selected no handoff.
- `final_output:` on an agent points at one emitted `TurnResponse` output and
  gives it a dedicated `Final Output` render.
- On review-driven agents, `final_output:` may reuse `comment_output:` or
  point at another emitted `TurnResponse` output. `comment_output:` remains
  the review carrier, and a separate `final_output:` still inherits review
  semantic refs, guards, and any shared `route.*` reads that are live on that
  output.
- The compiler resolves inherited outputs before workflow law, review,
  `final_output:`, or shared `route.*` semantics attach. Downstream consumers
  still see one ordinary output contract, not a second model.
- On split review finals, the block form may also bind review semantics into
  the final response:

```prompt
final_output:
    output: AcceptanceControlFinalResponse
    review_fields:
        verdict: verdict
        current_artifact: current_artifact
        next_owner: next_owner
```

- Structured final outputs may also bind a routed owner from one route field:

```prompt
final_output:
    output: WriterDecision
    route: next_route
```

- The compiler emits whether that split final response is `control_ready`.
  Authors do not declare that mode by hand.
- When that designated output's `output shape` carries an `output schema`, the
  final assistant message is structured JSON. Otherwise it stays ordinary
  prose or markdown according to the output contract.
- If that `output schema` omits `example:`, Doctrine still emits the payload
  contract and simply skips the `Example` section.

Preferred local inline enum form:

```prompt
field route: "Route"
    type: enum
    values:
        follow_up
        revise
```

Nullable field example:

```prompt
field next_step: "Next Step"
    type: string
    nullable
```

Shipped markdown render defaults:

- `Comment` and `CommentText` outputs default to `CommentMarkdown`
- other markdown-bearing outputs default to `ArtifactMarkdown`
- authored `render_profile` declarations may override supported readable
  rendering targets such as `properties`, guarded shells, and the shipped
  semantic lowering targets
- the shipped semantic targets are `analysis.stages`,
  `review.contract_checks`, and `control.invalidations`
- workflow-law sentences such as `current artifact`, `own only`, and
  `preserve exact` stay built-in compiler sentence lowering rather than
  authored `render_profile` targets
- if a markdown-bearing `output` uses `structure:` without its own
  `render_profile:`, an attached `document render_profile:` still governs the
  lowered readable body

Output bodies can include:

- authored fields and sections
- readable declaration refs
- readable block kinds such as `definitions`, `table`, `callout`, and `code`
- guarded output items
- `standalone_read`
- `trust_surface`

Shipped ordinary output render shape:

- This is an emitted Markdown rule, not a new input syntax rule.
- A simple `TurnResponse` ordinary output with only `Target`, `Shape`, and
  `Requirement` starts with a short bullet contract.
- Richer single-artifact ordinary outputs still start with one
  `Contract | Value` table.
- A `files:` output starts with the same contract table, then an `Artifacts`
  table.
- `current_truth`, titled `properties`, parseable `notes`, and
  `support_files` lower to tables when the authored shape is naturally tabular.
- `trust_surface` still renders as its own section, but ordinary output labels
  render as inline code.
- If `structure:` only needs titled section summaries, Doctrine renders a
  compact `Required Structure:` list.
- `structure:` still lowers to one `Artifact Structure` section with a summary
  table and any needed detail blocks when the shape is richer.
- Named tables do not add a new emitted shape. They use the same summary row,
  detail block, row-backed table, or no-row contract table that inline
  document tables use.
- A target-owned `delivery_skill:` renders as one `Delivered Via` row after
  `Target` and before target config rows. The row shows the skill title only;
  it does not print adapter commands.
- Compiler-owned `* Binding` wrappers may collapse when they only repeat one
  direct child section and add no keyed content of their own.

Example emitted shape:

```md
### Review Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required
```

Target-owned delivery example:

```prompt
skill LedgerNoteDelivery: "ledger-note-delivery"
    purpose: "Append markdown notes to the shared ledger."

output target LedgerNoteAppend: "Ledger Note Append"
    delivery_skill: LedgerNoteDelivery
    required: "Required"
        ledger_id: "Ledger ID"

output LedgerNote: "Ledger Note"
    target: LedgerNoteAppend
        ledger_id: "current-ledger"
    shape: MarkdownDocument
    requirement: Advisory
```

That output contract starts with:

```md
| Contract | Value |
| --- | --- |
| Target | Ledger Note Append |
| Delivered Via | `ledger-note-delivery` |
| Ledger ID | `current-ledger` |
| Shape | Markdown Document |
| Requirement | Advisory |
```

Typed attachment examples:

```prompt
output DeliveryPlan: "Delivery Plan"
    target: File
        path: "unit_root/DELIVERY_PLAN.md"
    shape: MarkdownDocument
    schema: DeliveryInventory
    requirement: Required
```

```prompt
output LessonPlanFile: "Lesson Plan File"
    target: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: MarkdownDocument
    structure: LessonPlan
    requirement: Required
```

## Trusted Carriers And Portable Truth

Portable truth moves through explicit carriers.

Workflow law uses:

- `current artifact ... via Output.field`
- `invalidate ... via Output.field`

Review reuses the same carrier rule through `comment_output`.

Carrier rules:

- the carrier must point at an emitted output field
- that field must be listed in the output's `trust_surface`
- if the carried artifact is itself an output root, the concrete turn must emit
  that output
- `invalidate` may also carry a declared schema group; schema-group carriers
  expand to concrete member artifacts in authored group order
- `standalone_read` explains the contract to humans, but it does not create a
  second trust channel
- compiled `AGENTS.md`, emitted structured final-output schema files under
  `schemas/<output-slug>.schema.json`, and target-scoped workflow-flow
  emission are separate build layers configured outside the prompt language;
  they are not `output target` declarations

## Guarded Output Items

Guarded output items keep conditional readback on the output contract itself:

```prompt
next_owner: route.next_owner when route.exists
```

Guarded sections still work too:

```prompt
failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
    failing_gates: "Failing Gates"
        "Name the failing review gates in authored order."
```

Important rules:

- Guarded output items are still output-owned fields.
- Guarded scalar items and guarded sections may be keyed, nested, addressed,
  and interpolated like other output structure.
- Route-bound output guards may read `route.choice` when every live routed
  branch comes from `route_from`.
- On ordinary outputs, guards may read declared inputs, enum members, and
  `route.exists` when the active turn resolves route semantics.
- On review-bound outputs, guards may also read resolved review semantic names
  such as `verdict`, `contract.*`, and `fields.*`.
- Route-specific readback should be guarded with `when route.exists:` when some
  active branches may not route. Unguarded `route.*` reads fail loudly instead
  of defaulting to fake local or terminal route values.
- A guarded output item does not become portable truth unless it is also
  listed in `trust_surface`.

## Bindings And Bound Roots

Concrete turns can bind inputs and outputs under local names:

- `approved_plan`
- `coordination_handoff`
- `review_comment`

Workflow law and review may then refer to those bound roots directly:

```prompt
law:
    current artifact approved_plan via coordination_handoff.current_artifact
```

Bound roots normalize to the underlying declared input or output. They are not
string aliases.

Important rules:

- bound roots work for currentness, invalidation, scope, and preservation
- inherited `inputs` and `outputs` blocks keep their bound keys visible
- review carrier paths may also use bound output roots

## Review Reuses The Same Output Boundary

Review does not invent a second produced-contract primitive.

Instead:

- `comment_output` names one ordinary `output`
- `fields:` binds review semantic channels into paths under that output
- `final_output:` may designate that same `comment_output` or another emitted
  `TurnResponse` when the review should end with a dedicated final-answer
  contract, including a schema-backed JSON result
- when `final_output:` is separate, `comment_output` stays the durable review
  carrier while the separate final output inherits the same review semantic
  refs, guards, and shared `route.*` reads
- that separate final output may bind a review-semantic subset through
  `final_output.review_fields:`
- the emitted companion contract tells hosts whether the split final output is
  partial or `control_ready`, and its top-level `route` block tells hosts
  which resolved named agent the final response routes to
- `review_family` reuses the same `comment_output` and `fields:` surface; it
  does not introduce a second emitted review contract
- imported reusable `comment_output` declarations may still bind local routed
  owners on the concrete review without copying the output declaration local
- review currentness still uses direct carriers such as
  `current artifact DraftSpec via ReviewComment.current_artifact`
- carried review state such as `active_mode` and `trigger_reason` still lives
  on emitted output fields and, when trusted downstream, in `trust_surface`

This is why the review ladder can add verdicts, failing gates, current truth,
and carried state without introducing route payloads or hidden review packets.

## Current Boundaries

Doctrine intentionally does not ship:

- a packet primitive
- a second downstream trust channel
- a separate root-binding declaration outside `inputs` and `outputs`
- hidden carrier inference from prose labels

The emitted contract surface is still `output`.

## Example Map

Use the numbered corpus when you want the model in proof-sized pieces:

- `08` and `09`: basic inputs and outputs
- `18`: richer I/O record structure
- `23` through `25`: first-class `inputs` and `outputs` blocks plus inheritance
- `31`: currentness plus `trust_surface`
- `39`: guarded output items in isolation
- `46`: review current truth on trusted output carriers
- `47` and `49`: carried review state on output fields
- `50` through `53`: bound roots for workflow law and review carriers
- `55`: owner-aware output `schema:` attachments
- `56`: typed `structure:` attachments on markdown-bearing inputs and outputs
- `57`: schema-backed review contracts on ordinary output carriers
- `63`: first-class schema `artifacts:` / `groups:` plus namespaced schema paths
- `58` and `59`: document blocks, inheritance, and addressable readable descendants
- `60`: shared readable blocks on workflow, skill-entry, and output bodies
- `61`: multiline readable code blocks and fail-loud readable validation
- `64`: authored `render_profile`, `properties`, and explicit readable guard shells
- `65`: typed `item_schema:` / `row_schema:` descendants on readable blocks
- `66`: explicit raw `markdown` / `html`, `footnotes`, `image`, and structured nested table cells
- `67`: semantic render-profile lowering targets plus `document render_profile:`
  surviving `output structure:` lowering
- `87`: shared `route.*` reads on ordinary workflow-law outputs plus fail-loud
  unguarded route reads
- `88`: review comments mixing review semantics and shared `route.*`
- `89`: dedicated `route_only` feeding the same shared `route.*` output surface
- `90`: split durable review comment plus JSON `final_output:` consuming the
  same shared routed-owner truth
- `91`: `handoff_routing` law feeding shared `route.*` semantics into ordinary
  outputs and `final_output:`
- `92`: first-class `route_from` on workflow law
- `93`: emitted-output route selection on `handoff_routing` plus
  `final_output:`
- `94`: `route.choice` guards narrowing branch-specific route detail
- `120`: structured `final_output:` routing owned by one `route field`
- `121`: nullable `route field` routing where `null` means no handoff
- `107`: the smallest direct `output[...]` inheritance proof
- `108`: inherited top-level output attachments such as `render_profile:`,
  `trust_surface`, and `standalone_read`
- `109`: imported reusable handoff outputs inherited and extended locally
- `110`: inherited outputs used through `final_output:`
- `111`: inherited outputs keeping shared `route.*` readback
- `112`: fail-loud output inheritance errors
- `116`: first-class named table declarations reused by local document table
  keys
