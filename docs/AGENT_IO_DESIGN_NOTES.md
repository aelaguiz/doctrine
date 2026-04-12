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
- Input bodies hold source-specific configuration plus authored explanatory
  prose.
- `structure:` may attach a named `document` to a markdown-bearing input shape.
- Input record bodies may also use ordinary readable blocks such as
  `definitions`, `table`, `callout`, and `code`.
- `inputs` blocks group inputs and optionally bind them under local keys for a
  concrete turn.

Binding example:

```prompt
inputs: "Inputs"
    draft_spec: "Draft Spec Binding"
        DraftSpec
```

That local key becomes a usable root for workflow law or review semantics.

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
- Output shapes may be named with `output shape`.
- `schema:` on `output` attaches a Doctrine `schema` declaration.
- `schema:` on `output shape` still attaches a `json schema`; the field name is
  owner-aware rather than globally retyped.
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
- `json schema` still attaches beneath `output shape`; it does not replace
  `output`.
- `outputs` blocks group outputs and may bind them under local keys for a
  concrete turn.
- `final_output:` on an agent points at one emitted `TurnResponse` output and
  gives it a dedicated `Final Output` render.
- When that designated output's `output shape` carries a `json schema`, the
  final assistant message is structured JSON. Otherwise it stays ordinary
  prose or markdown according to the output contract.

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
- guarded sections
- `standalone_read`
- `trust_surface`

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
- compiled `AGENTS.md` emission and target-scoped workflow-flow emission are
  separate build layers configured outside the prompt language; they are not
  `output target` declarations

## Guarded Output Sections

Guarded sections keep conditional readback on the output contract itself:

```prompt
failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
    failing_gates: "Failing Gates"
        "Name the failing review gates in authored order."
```

Important rules:

- Guarded sections are still output-owned fields.
- They can be keyed, nested, addressed, and interpolated like other output
  structure.
- On ordinary outputs, guards may read declared inputs and enum members.
- On review-bound outputs, guards may also read resolved review semantic names
  such as `verdict`, `contract.*`, and `fields.*`.
- A guarded output section does not become portable truth unless it is also
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
- `review_family` reuses the same `comment_output` and `fields:` surface; it
  does not introduce a second emitted review contract
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
- `39`: guarded output sections in isolation
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
