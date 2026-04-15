End acceptance review with one JSON review result.

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

## Final Output

### Acceptance Review Response

> **Final answer contract**
> End the turn with one final assistant message that follows this schema.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Structured JSON |
| Shape | Acceptance Review JSON |
| Schema | Acceptance Review Schema |
| Profile | OpenAIStructuredOutput |
| Generated Schema | `schemas/acceptance_review_response.schema.json` |
| Requirement | Required |

#### Payload Fields

| Field | Type | Required On Wire | Null Allowed | Meaning |
| --- | --- | --- | --- | --- |
| `verdict` | string | Yes | No | Review verdict. |
| `reviewed_artifact` | string | Yes | No | Reviewed artifact name. |
| `current_artifact` | string | Yes | Yes | Current artifact after review. |
| `next_owner` | string | Yes | Yes | Next owner after review when one exists. |
| `blocked_gate` | string | Yes | Yes | Blocking gate when review stopped early. |

#### Example

```json
{
  "verdict": "changes_requested",
  "reviewed_artifact": "Draft Plan",
  "current_artifact": null,
  "next_owner": null,
  "blocked_gate": "The review basis is missing."
}
```

- Kind: Json Object

#### Field Notes

Keep `next_owner` aligned with the routed review branch.
Blocked branches should use null for `current_artifact` and `next_owner`.

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

#### Read on Its Own

This review should stand on its own. A downstream owner should know the verdict, current artifact when one remains, and whether a next owner exists.
