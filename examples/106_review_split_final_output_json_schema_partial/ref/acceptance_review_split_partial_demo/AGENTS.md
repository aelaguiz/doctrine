Emit the review comment and end with a small partial JSON result.

## Acceptance Review

Review subject: Draft Plan.
Shared review contract: Plan Review Contract.

### Basis Checks

Block: The review basis is missing.

### Contract Checks

Reject: Outline Complete.

Accept only if The acceptance review contract passes.

### If Accepted

Current artifact: Draft Plan.

Accepted plan goes to ReviewLead.

### If Rejected

When present(blocked_gate), no artifact is current for this outcome.

When missing(blocked_gate), current artifact: Draft Plan.

## Inputs

### Draft Plan

- Source: File
- Path: `unit_root/DRAFT_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

- Basis Missing: `Basis Missing`
- Outline Missing: `Outline Missing`

## Outputs

### Acceptance Review Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Verdict

State whether the plan passed review or asked for changes.

#### Reviewed Artifact

Name the reviewed artifact.

#### Analysis Performed

Summarize the review analysis.

#### Output Contents That Matter

State what the next owner should read first.

#### Current Artifact

Show this only when present(current_artifact).

Name the artifact that remains current after review.

#### Next Owner

Show this only when present(next_owner).

Name ReviewLead when the review accepts the plan.

#### Failure Detail

Show this only when verdict is changes requested.

##### Blocked Gate

Show this only when present(blocked_gate).

Name the blocking gate when review stopped before the normal content check.

##### Failing Gates

List exact failing gates in authored order.

#### Trust Surface

- Current Artifact

## Final Output

### Acceptance Control Final Response

> **Final answer contract**
> End the turn with one final assistant message that follows this schema.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Structured JSON |
| Shape | Acceptance Control JSON |
| Schema | Acceptance Control Schema |
| Profile | OpenAIStructuredOutput |
| Schema file | `schemas/acceptance_control.schema.json` |
| Example file | `examples/acceptance_control.example.json` |
| Requirement | Required |

#### Payload Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `current_artifact` | string | Current artifact after review. |
| `next_owner` | string | Next owner after review when one exists. |

#### Example

```json
{
  "current_artifact": "Draft Plan",
  "next_owner": "ReviewLead"
}
```

#### Review Response Semantics

This final response is separate from the review carrier: AcceptanceReviewComment.

| Meaning | Field |
| --- | --- |
| Current Artifact | `current_artifact` |
| Next Owner | `next_owner` |

This final response is not control-ready. Read the review carrier for the full review outcome.

#### Current Artifact

Show this only when present(current_artifact).

Name the current artifact after review.

#### Next Owner

Show this only when present(next_owner).

Name ReviewLead when the review accepts the plan.

#### Read on Its Own

This final JSON is a small control readback, not the full review.
