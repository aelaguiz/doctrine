Emit the review comment and end with a control-ready JSON result.

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

- Verdict: State whether the plan passed review or asked for changes.
- Reviewed Artifact: Name the reviewed artifact.
- Analysis Performed: Summarize the review analysis.
- Output Contents That Matter: State what the next owner should read first.
- Current Artifact: Show this only when present(current_artifact). Name the artifact that remains current after review.
- Next Owner: Show this only when present(next_owner). Name ReviewLead when the review accepts the plan.

#### Failure Detail

Show this only when verdict is changes requested.

##### Blocked Gate

Show this only when present(blocked_gate).

Name the blocking gate when review stopped before the normal content check.

##### Failing Gates

List exact failing gates in authored order.

#### Trust Surface

- `Current Artifact`

- Standalone Read: This review should stand on its own. A downstream owner should know the verdict, current artifact when one remains, and whether a next owner exists.

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
| Generated Schema | `schemas/acceptance_control_final_response.schema.json` |
| Requirement | Required |

#### Payload Fields

| Field | Type | Required On Wire | Null Allowed | Meaning |
| --- | --- | --- | --- | --- |
| `verdict` | string | Yes | No | Review verdict. |
| `current_artifact` | string | Yes | Yes | Current artifact after review. |
| `next_owner` | string | Yes | Yes | Next owner after review when one exists. |
| `blocked_gate` | string | Yes | Yes | Blocking gate when review stopped early. |

#### Example

```json
{
  "verdict": "accept",
  "current_artifact": "Draft Plan",
  "next_owner": "ReviewLead",
  "blocked_gate": null
}
```

This final response is separate from the review carrier: AcceptanceReviewComment.
This final response is control-ready. A host may read it as the review outcome.
- Kind: Json Object

#### Field Notes

Keep `verdict` aligned with the review verdict.
Use null for `next_owner` and `blocked_gate` when this review does not set them.

#### Verdict

State whether the review accepted the plan or asked for changes.

#### Current Artifact

Show this only when present(current_artifact).

Name the current artifact after review.

#### Next Owner

Show this only when present(next_owner).

Name ReviewLead when the review accepts the plan.

#### Blocked Gate

Show this only when present(blocked_gate).

Name the blocking gate when review stopped before the normal content check.

#### Read on Its Own

This final JSON should be enough for a host to read the review outcome.
