# Final Output Design Proposal

Status: implemented in the shipped language surface on this branch.

This document proposes an optional first-class way to declare an agent's final
assistant message. It is intentionally focused on authored outcomes and emitted
contract shape, not parser or compiler implementation details.

## Problem

Doctrine already has strong output-contract surfaces:

- `output` declares an emitted artifact
- `output shape` declares the structural form
- `json schema` declares strict machine-readable JSON structure when needed
- `schema:` and `structure:` attach reusable artifact owners

That works well for files, handoffs, review comments, and other emitted
surfaces. What it does not say cleanly today is:

- which declared contract is the agent's final assistant message
- whether the final assistant message is ordinary prose or strict JSON
- how rendered agent docs should distinguish the final answer from other
  turn-local comments or artifacts

The result is that Doctrine can describe a `TurnResponse` output, but it still
does not give authors one standard agent-level place to say "this is the final
answer contract for the turn."

## Desired Outcome

Authors should be able to optionally declare one final output for an agent.

If present:

- it becomes the contract for the turn-ending assistant message
- hosts can treat it as the canonical final answer contract
- the rendered agent home shows it under a dedicated `Final Output` section

If absent:

- Doctrine keeps today's behavior
- agents can continue emitting ordinary outputs without naming a special final
  answer contract

The same surface should work for both:

- ordinary prose / markdown / comment final answers
- strict JSON final answers backed by a declared JSON schema

## Chosen Language Shape

Doctrine should not add a second parallel artifact family here.

The language already knows how to describe output contracts and JSON-backed
shapes. The missing concept is designation, not another full declaration
family.

The proposal is to add one new agent attachment:

```prompt
agent ReleaseSummaryAgent:
    role: "Ship the change and close the turn plainly."
    workflow: "Ship"
        "Do the work and end with the declared final output."
    final_output: ReleaseSummaryResponse
```

`final_output:` references an existing `output` declaration.

Why this is the right shape:

- authors reuse the `output` contract surface they already know
- JSON mode naturally reuses `output shape` plus `json schema`
- the designation stays agent-scoped, which matches the actual product need
- `outputs:` can keep owning side artifacts, support files, and non-final
  emissions

## Proposed Outcome Rules

- `final_output:` is optional.
- A concrete agent may declare at most one `final_output:`.
- `final_output:` points at an `output` declaration.
- That referenced `output` is the canonical final assistant message for the
  turn.
- The referenced output should describe one final message surface, not a
  `files:` bundle.
- The referenced output should stay on the turn-response channel rather than a
  file target.
- If the referenced output's shape carries a JSON schema, the final assistant
  message is structured JSON.
- If the referenced output's shape does not carry a JSON schema, the final
  assistant message is ordinary prose according to the output shape and any
  attached readable structure.
- `outputs:` remains available for files, handoff carriers, review comments,
  and other non-final emitted artifacts.
- Omitting `final_output:` preserves current behavior.

## Language Sketch

This proposal adds one new reserved agent field and reuses existing output
surfaces everywhere else.

### Agent Attachment

```prompt
agent SomeAgent:
    role: "..."
    workflow: "..."
    final_output: SomeFinalOutput
```

### Prose Final Output

```prompt
output ReleaseSummaryResponse: "Release Summary Response"
    target: TurnResponse
    shape: CommentText
    requirement: Required

    format_notes: "Expected Structure"
        "Lead with the shipped outcome."
        "Keep the answer concise unless the user asked for depth."
        "End with the next owner or step when one matters."

    standalone_read: "Standalone Read"
        "A user should be able to read the final answer alone and understand what changed and what happens next."


agent ReleaseSummaryAgent:
    role: "Ship the change and close the turn plainly."
    workflow: "Ship"
        "Do the work and end with the declared final output."
    final_output: ReleaseSummaryResponse
```

### JSON Final Output

```prompt
json schema RepoStatusSchema: "Repo Status Schema"
    profile: OpenAIStructuredOutput
    file: "schemas/repo_status.schema.json"


output shape RepoStatusJson: "Repo Status JSON"
    kind: JsonObject
    schema: RepoStatusSchema
    example_file: "examples/repo_status.example.json"

    explanation: "Field Notes"
        "`summary` is a short natural-language status."
        "`status` is `ok` or `action_required`."
        "`next_step` is null only when no follow-up is needed."


output RepoStatusFinalResponse: "Repo Status Final Response"
    target: TurnResponse
    shape: RepoStatusJson
    requirement: Required

    standalone_read: "Standalone Read"
        "The final answer should stand on its own as one structured repo-status result."


agent RepoStatusAgent:
    role: "Report repo status in structured form."
    workflow: "Summarize"
        "Summarize the repo state and end with the declared final output."
    final_output: RepoStatusFinalResponse
```

## Rendered Outcome

The emitted agent home should give final output its own dedicated section so
readers can tell the difference between:

- the final answer contract
- other outputs
- other assistant commentary or handoff surfaces

The final-output render should feel intentionally authored, not like a dumped
property list.

The design goal is a clean, high-signal contract block that uses Markdown well:

- start with one plain-English sentence that says what the final answer is for
- compress contract metadata into a small table instead of a long loose list
- group authored guidance under semantic headings instead of piling everything
  into one block
- show a payload preview when the final answer is schema-backed JSON
- keep enough whitespace and heading structure that the section scans quickly

The render should still talk about the user-visible outcome, not raw transport
plumbing, but it should do that with more shape and more visual clarity than a
flat sequence of bullets.

### Rendered Prose Final Output

Rendered home excerpt:

```md
## Final Output

### Release Summary Response

> **Final answer contract**  
> End the turn with one concise release summary for the user.

| Contract | Value |
| --- | --- |
| Message kind | Final assistant message |
| Format | Natural-language markdown |
| Shape | `CommentText` |
| Requirement | Required |

#### Expected Structure

1. Lead with the shipped outcome.
2. Keep the answer concise unless the user asked for depth.
3. End with the next owner or step when one matters.

#### Read It Cold

A user should be able to read the final answer alone and understand what
changed and what happens next.
```

This is the ordinary final-answer mode:

- one final assistant message
- natural-language text
- shaped by the declared output contract

### Rendered JSON Final Output

Rendered home excerpt:

```md
## Final Output

### Repo Status Final Response

> **Final answer contract**  
> End the turn with one schema-backed repo-status object.

| Contract | Value |
| --- | --- |
| Message kind | Final assistant message |
| Format | Structured JSON |
| Shape | `Repo Status JSON` |
| Schema | `Repo Status Schema` |
| Profile | `OpenAIStructuredOutput` |
| Schema file | `schemas/repo_status.schema.json` |
| Example file | `examples/repo_status.example.json` |
| Requirement | Required |

#### Payload Shape

| Field | Type | Meaning |
| --- | --- | --- |
| `summary` | string | Short natural-language status. |
| `status` | string | `ok` or `action_required`. |
| `next_step` | string \| null | Null only when no follow-up is needed. |

#### Example Shape

```json
{
  "summary": "Branch is clean and checks passed.",
  "status": "ok",
  "next_step": null
}
```

#### Read It Cold

The final answer should stand on its own as one structured repo-status result.
```

This is the structured final-answer mode:

- one final assistant message
- strict JSON instead of prose
- the same authored contract still renders readably in Markdown

## Proposed Example Ladder

If this lands, it should ship as a short manifest-backed ladder rather than one
broad capstone.

Keep it narrow and ordered like the rest of the corpus:

| ID | Focus | Expected proof |
| --- | --- | --- |
| `76_final_output_prose_basic` | Smallest opt-in prose final answer. | Parse, compile, rendered `Final Output` section. |
| `77_final_output_optional_passthrough` | Omitting `final_output:` preserves today's behavior. | Parse, compile, no `Final Output` section. |
| `78_final_output_and_side_artifacts` | `final_output:` stays distinct from ordinary `outputs:` artifacts. | Parse, compile, separate final-answer and artifact sections. |
| `79_final_output_json_schema` | Final answer switches cleanly into schema-backed JSON mode. | Parse, compile, rendered structured-JSON final-output metadata. |
| `80_final_output_rejects_file_targets` | `final_output:` cannot designate a file emission. | Compile-negative diagnostic. |
| `81_final_output_rejects_non_output_refs` | `final_output:` must point at an `output` declaration. | Compile-negative diagnostic. |

The prose sketch above can seed `76`. The JSON sketch above can seed `79`.
The other examples should stay as small deltas on top of those two anchors.

### `76_final_output_prose_basic`

Goal: prove the smallest useful prose final-answer designation.

```prompt
output FinalReply: "Final Reply"
    target: TurnResponse
    shape: CommentText
    requirement: Required


agent HelloAgent:
    role: "Answer plainly and end the turn."
    workflow: "Reply"
        "Reply and stop."
    final_output: FinalReply
```

Manifest should prove:

- parse and compile succeed
- emitted home includes a dedicated `## Final Output` section
- the final output renders as a final assistant message, not as an ordinary
  artifact bucket

### `77_final_output_optional_passthrough`

Goal: prove that this feature is truly optional.

Use the same authored surface as `01`, but remove `final_output:` and keep the
ordinary output contract.

Manifest should prove:

- parse and compile succeed
- emitted home does not invent a `## Final Output` section
- existing ordinary output rendering stays unchanged

### `78_final_output_and_side_artifacts`

Goal: prove that the designated final answer and ordinary emitted artifacts can
coexist cleanly.

```prompt
agent ReleaseAgent:
    role: "Ship the change and leave both a user-facing answer and a file artifact."
    workflow: "Ship"
        "Do the work, emit the file artifact, and end with the declared final output."
    final_output: ReleaseSummaryResponse
    outputs: "Outputs"
        ReleaseNotesFile
```

Manifest should prove:

- parse and compile succeed
- emitted home renders `Final Output` separately from ordinary `Outputs`
- `ReleaseNotesFile` stays an artifact contract and is not mistaken for the
  turn-ending answer

### `79_final_output_json_schema`

Goal: prove that structured final answers reuse the existing JSON contract
path.

```prompt
json schema RepoStatusSchema: "Repo Status Schema"
    profile: OpenAIStructuredOutput
    file: "schemas/repo_status.schema.json"


output shape RepoStatusJson: "Repo Status JSON"
    kind: JsonObject
    schema: RepoStatusSchema
    example_file: "examples/repo_status.example.json"


output RepoStatusFinalResponse: "Repo Status Final Response"
    target: TurnResponse
    shape: RepoStatusJson
    requirement: Required


agent RepoStatusAgent:
    role: "Return one structured repo-status answer."
    workflow: "Summarize"
        "Summarize the repo state and end with the declared final output."
    final_output: RepoStatusFinalResponse
```

Manifest should prove:

- parse and compile succeed
- emitted home renders a dedicated `Final Output` section
- that section clearly says the final message format is structured JSON
- schema profile, schema file, and example file all stay visible in the final
  output contract

### `80_final_output_rejects_file_targets`

Goal: fail loud when an author tries to designate a file emission as the final
assistant message.

```prompt
agent InvalidFileFinalOutputAgent:
    role: "Try to end the turn with a file artifact."
    workflow: "Reply"
        "Do the work."
    final_output: ReleaseNotesFile
```

Manifest should prove:

- compile fails
- the diagnostic says `final_output:` must designate a turn-ending assistant
  message, not a file target
- the failing output name is called out directly

### `81_final_output_rejects_non_output_refs`

Goal: fail loud when `final_output:` points at the wrong declaration kind.

```prompt
agent InvalidSchemaFinalOutputAgent:
    role: "Try to point final_output at a schema."
    workflow: "Reply"
        "Do the work."
    final_output: RepoStatusSchema
```

Manifest should prove:

- compile fails
- the diagnostic says `final_output:` must point at an `output` declaration
- the wrong declaration kind is named plainly

## What Changes For Authors

Today, authors can describe a `TurnResponse` output, but they still have to
rely on convention to mean "this is the final answer."

With this proposal:

- authors declare a normal reusable `output`
- agents optionally mark one of those outputs as `final_output:`
- the rendered contract makes that final-answer status explicit
- JSON final answers reuse the existing JSON-shape path instead of inventing a
  new schema surface

## What Stays The Same

- `output`, `output shape`, and `json schema` stay the reusable contract
  surfaces.
- `schema:` on `output shape` remains the JSON-schema attachment point.
- `schema:` and `structure:` on ordinary `output` keep their current meanings.
- `outputs:` still owns side artifacts and non-final emissions.
- Agents that do not opt into `final_output:` do not change.

## Boundaries

This proposal is intentionally narrow.

It does not try to:

- redesign ordinary output contracts
- replace `outputs:`
- invent a new inline JSON-schema mini-language
- force every agent to emit a structured final answer
- settle review-specific final-answer behavior in this first design pass

The core outcome is smaller and cleaner:

- one optional agent-level designation for the final answer
- reuse of the existing output contract model
- clean support for both prose final answers and JSON-schema final answers
