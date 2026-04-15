Use review semantics and route semantics on the same emitted review comment.

## Draft Review

Review subject: Draft Spec.
Shared review contract: Draft Review Contract.

### Contract Checks

Accept only if The shared draft review contract passes.

### If Accepted

Current artifact: Draft Spec.

Accepted draft goes to ReviewLead.

### If Rejected

Current artifact: Draft Spec.

Rejected draft goes to DraftAuthor.

## Inputs

### Draft Spec

- Source: File
- Path: `unit_root/DRAFT_SPEC.md`
- Shape: Markdown Document
- Requirement: Required

## Outputs

### Draft Review Comment

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Comment |
| Requirement | Required |

#### Verdict

Say whether the review accepted the draft or asked for changes.

#### Reviewed Artifact

Name the reviewed artifact.

#### Analysis Performed

Summarize the review analysis.

#### Output Contents That Matter

Summarize what the next owner should read first.

#### Current Artifact

Name the artifact that remains current after review.

#### Next Owner

Name ReviewLead when accepted and DraftAuthor when rejected.

#### Failure Detail

Show this only when verdict is changes requested.

##### Failing Gates

Name the failing review gates in authored order.

#### Accepted Route

Show this only when verdict is accepted and a routed owner exists.

Accepted draft goes to ReviewLead. Next owner: Review Lead.

#### Retry Route

Show this only when verdict is changes requested and a routed owner exists.

Draft Author

#### Trust Surface

- `Current Artifact`
