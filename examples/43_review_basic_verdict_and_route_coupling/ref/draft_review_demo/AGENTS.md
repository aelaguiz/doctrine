Keep review verdicts, failing gates, and next-owner routing aligned.

## Draft Review

Review subject: Draft Spec.
Shared review contract: Draft Review Contract.

### Start Review

Reject: The draft still leaves the core decision unclear.

### Contract Checks

Accept only if The shared draft review contract passes.

### If Accepted

There is no current artifact for this outcome.

Accepted draft returns to ReviewLead.

### If Rejected

There is no current artifact for this outcome.

Rejected draft returns to DraftAuthor.

## Inputs

### Draft Spec

- Source: File
- Path: `unit_root/DRAFT_SPEC.md`
- Shape: Markdown Document
- Requirement: Required

Use the current draft specification as the reviewed artifact.

## Outputs

### Draft Review Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Verdict

Say whether the review accepted the draft or requested changes.

#### Reviewed Artifact

Name the reviewed artifact this review judged.

#### Analysis Performed

Summarize the review analysis that led to the verdict.

#### Output Contents That Matter

Summarize the parts of the draft the next owner must read first.

#### Next Owner

Name the next owner, including ReviewLead when the draft is accepted and DraftAuthor when the draft is rejected.

#### Failure Detail

Rendered only when verdict is changes requested.

##### Failing Gates

Name the failing review gates in authored order.

#### Standalone Read

A downstream owner should be able to read this comment alone and understand what was reviewed, what verdict landed, who owns next, and which parts of the draft matter now.
