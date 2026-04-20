Review polish drafts with the shared review carrier.

## Polish Critic Review

Review subject: Polish Draft.
Shared review contract: Polish Contract.

### Contract Checks

Accept only if The polish review contract passes.

### If Accepted

Current artifact: Polish Draft.

### If Rejected

Current artifact: Polish Draft.

Polish changes route back to the polish producer.

## Inputs

### Polish Draft

- Source: File
- Path: `unit_root/POLISH.md`
- Shape: Markdown Document
- Requirement: Required

## Final Output

### Shared Review Carrier

> **Final answer contract**
> End the turn with one final assistant message that follows this schema.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Structured JSON |
| Shape | Shared Review JSON |
| Schema | Shared Review Schema |
| Profile | OpenAIStructuredOutput |
| Generated Schema | `schemas/shared_review_carrier.schema.json` |
| Requirement | Required |

#### Payload Fields

| Field | Type | Required On Wire | Null Allowed | Meaning |
| --- | --- | --- | --- | --- |
| `verdict` | string | Yes | No | Review verdict. |
| `reviewed_artifact` | string | Yes | No | Reviewed artifact name. |
| `current_artifact` | string | Yes | Yes | Current artifact after review. |
| `next_owner` | string | Yes | Yes | Next owner after review when one exists. |

#### Example

```json
{
  "verdict": "changes_requested",
  "reviewed_artifact": "Outline Draft",
  "current_artifact": "Outline Draft",
  "next_owner": "OutlineProducer"
}
```

- Kind: Json Object

#### Field Notes

Keep `next_owner` aligned with the routed review branch.

#### Verdict

State whether the artifact passed review or asked for changes.

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

Name the producer when the review routes back for rework.

#### Failure Detail

Show this only when verdict is changes requested.

##### Failing Gates

List exact failing gates in authored order.

#### Trust Surface

- Current Artifact

#### Read on Its Own

This review should stand on its own.
