Emit the review comment and end with a control-only JSON result.

## Acceptance Review

Review subject: Draft Plan.
Shared review contract: Plan Review Contract.

### Contract Checks

Reject: Outline Complete.

Accept only if The acceptance review contract passes.

### If Accepted

Current artifact: Draft Plan.

Accepted plan returns to ReviewLead.

### If Rejected

Current artifact: Draft Plan.

Rejected plan returns to PlanAuthor.

## Inputs

### Draft Plan

- Source: File
- Path: `unit_root/DRAFT_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

- Outline Missing: `Outline Missing`

## Outputs

### Acceptance Review Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Verdict

State whether the plan passed review.

#### Reviewed Artifact

Name the reviewed artifact.

#### Analysis Performed

Summarize the review analysis.

#### Output Contents That Matter

State what the next owner should read first.

#### Current Artifact

Name the artifact that remains current after review.

#### Next Owner

Name ReviewLead when accepted and PlanAuthor when rejected.

#### Failure Detail

Rendered only when verdict is changes requested.

##### Failing Gates

List exact failing gates, including Outline Complete when it fails.

#### Trust Surface

- Current Artifact

#### Standalone Read

A downstream owner should be able to read this review alone and understand the acceptance verdict, current artifact, and next owner.

## Final Output

### Acceptance Control Final Response

> **Final answer contract**
> End the turn with one schema-backed final assistant message.

| Contract | Value |
| --- | --- |
| Message kind | Final assistant message |
| Format | Structured JSON |
| Shape | Acceptance Control JSON |
| Schema | Acceptance Control Schema |
| Profile | OpenAIStructuredOutput |
| Schema file | `schemas/acceptance_control.schema.json` |
| Example file | `examples/acceptance_control.example.json` |
| Requirement | Required |

#### Payload Shape

| Field | Type | Meaning |
| --- | --- | --- |
| `route` | string | Control route for the next owner. |
| `current_artifact` | string | Current artifact after review. |
| `next_owner` | string | Next owner after review. |

#### Example Shape

```json
{
  "route": "follow_up",
  "current_artifact": "Draft Plan",
  "next_owner": "ReviewLead"
}
```

#### Field Notes

Keep `current_artifact` aligned with Current Artifact.
Use `route` value `revise` only when Outline Complete fails.

#### Changes Requested Note

Rendered only when verdict is changes requested.

Only emit this retry control when the review requests changes.

#### Read It Cold

This final JSON should be enough for the next owner to route the review result.
