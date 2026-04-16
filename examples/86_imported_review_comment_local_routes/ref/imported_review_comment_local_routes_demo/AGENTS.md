Use an imported comment output that still binds local routed owners.

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

- Target: Turn Response
- Shape: Comment
- Requirement: Required

- Verdict: Say whether the review accepted the draft or requested changes.
- Reviewed Artifact: Name the reviewed artifact this review judged.
- Analysis Performed: Summarize the review analysis that led to the verdict.
- Output Contents That Matter: Summarize the parts of the draft the next owner must read first.
- Current Artifact: Name the artifact that remains current after review.
- Next Owner: Name the next owner, including ReviewLead when the draft is accepted and DraftAuthor when the draft is rejected.

#### Failure Detail

Show this only when verdict is changes requested.

##### Failing Gates

Name the failing review gates in authored order.

#### Trust Surface

- `Current Artifact`

- Standalone Read: A downstream owner should be able to read this review alone and understand the verdict, current artifact, and next owner.
