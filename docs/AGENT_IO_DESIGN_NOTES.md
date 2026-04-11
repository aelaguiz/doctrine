# Agent I/O Model

Doctrine treats turn contracts as explicit declarations. Inputs say what a turn
may read. Outputs say what it emits. Workflow law or review says what those
outputs mean. `trust_surface` says which emitted fields downstream owners may
trust.

For the full declaration overview, use
[LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md). For workflow-law and review
semantics, use [WORKFLOW_LAW.md](WORKFLOW_LAW.md) and
[REVIEW_SPEC.md](REVIEW_SPEC.md).

## Mental Model

- `input` and `inputs` describe consumed artifacts.
- `output` and `outputs` describe emitted artifacts.
- `trust_surface` marks portable downstream readback.
- Guarded output sections keep conditional readback on the output contract.
- Workflow law and review decide currentness, invalidation, verdicts, and
  carried state.

This keeps the split clean:

- output contracts are still the emitted contract surface
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
- `json schema` attaches beneath `output shape`; it does not replace `output`.
- `outputs` blocks group outputs and may bind them under local keys for a
  concrete turn.

Output bodies can include:

- authored fields and sections
- readable declaration refs
- guarded sections
- `standalone_read`
- `trust_surface`

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
