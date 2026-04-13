End acceptance review with one schema-backed review message.

## Acceptance Review

Review subject: Draft Plan.
Shared review contract: Plan Review Contract.

### Contract Checks

Reject: Outline Complete.

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
| Schema file | `schemas/acceptance_review.schema.json` |
| Example file | `examples/acceptance_review.example.json` |
| Requirement | Required |

#### Payload Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `verdict` | string | Review verdict. |
| `reviewed_artifact` | string | Reviewed artifact name. |
| `current_artifact` | string | Current artifact after review. |
| `next_owner` | string | Next owner after review. |

#### Example

```json
{
  "verdict": "accepted",
  "reviewed_artifact": "Draft Plan",
  "current_artifact": "Draft Plan",
  "next_owner": "ReviewLead"
}
```

#### Field Notes

Use the schema fields exactly once.
Keep `next_owner` aligned with the routed outcome.

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

Show this only when verdict is changes requested.

##### Failing Gates

List exact failing gates, including Outline Complete when it fails.

#### Trust Surface

- Current Artifact

#### Read on Its Own

This review should stand on its own. A downstream owner should know the acceptance verdict, current artifact, and next owner.
