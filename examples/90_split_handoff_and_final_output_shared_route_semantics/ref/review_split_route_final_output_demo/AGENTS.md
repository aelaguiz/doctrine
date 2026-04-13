Emit the review comment and end with a route-aware JSON control result.

## Acceptance Review

Review subject: Draft Plan.
Shared review contract: Plan Review Contract.

### Contract Checks

Accept only if The acceptance review contract passes.

### If Accepted

Current artifact: Draft Plan.

Accepted plan goes to ReviewLead.

### If Rejected

Current artifact: Draft Plan.

Rejected plan goes to PlanAuthor.

## Inputs

### Draft Plan

- Source: File
- Path: `unit_root/DRAFT_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

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

Summarize what the next owner should read first.

#### Current Artifact

Name the artifact that remains current after review.

#### Next Owner

Name ReviewLead when accepted and PlanAuthor when rejected.

#### Failure Detail

Show this only when verdict is changes requested.

##### Failing Gates

List exact failing gates, including Outline Complete when it fails.

#### Trust Surface

- Current Artifact

#### Standalone Read

From this output alone, a downstream owner should know the acceptance verdict, current artifact, and next owner.

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
| `route` | string | Control route for the next owner. |
| `current_artifact` | string | Current artifact after review. |
| `next_owner` | string | Next owner after review. |

#### Example

```json
{
  "route": "follow_up",
  "current_artifact": "Draft Plan",
  "next_owner": "ReviewLead"
}
```

#### Accepted Route

Show this only when verdict is accepted and a routed owner exists.

Accepted plan goes to ReviewLead. Next owner: Review Lead.

#### Retry Route

Show this only when verdict is changes requested and a routed owner exists.

PlanAuthor

#### Read on Its Own

This final JSON should be enough for the next owner to route the review result.
