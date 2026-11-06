Keep review verdicts, failing gates, and next-owner routing aligned.

## Draft Review

Review subject: Draft Spec.
Shared review contract: Draft Review Contract.

### Start Review

Reject: The draft still leaves the core decision unclear.

### Contract Checks

Accept only if The shared draft review contract passes.

### If Accepted

No artifact is current for this outcome.

Accepted draft goes to ReviewLead.

### If Rejected

No artifact is current for this outcome.

Rejected draft goes to DraftAuthor.

## Inputs

### Draft Spec

- Source: File
- Path: `unit_root/DRAFT_SPEC.md`
- Shape: Markdown Document
- Requirement: Required

Use the current draft spec as the reviewed artifact.

## Outputs

### Draft Review Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

- Verdict: Say whether the review accepted the draft or asked for changes.
- Reviewed Artifact: Name the reviewed artifact this review judged.
- Analysis Performed: Sum up the review work that led to the verdict.
- Output Contents That Matter: Summarize the parts of the draft the next owner must read first.
- Next Owner: Name the next owner. Use ReviewLead when the draft is accepted and DraftAuthor when it is rejected.

#### Failure Detail

Show this only when verdict is changes requested.

##### Failing Gates

Name the failing review gates in authored order.

- Standalone Read: This comment should stand on its own. The next owner should know what was reviewed, what verdict landed, who owns next, and which parts of the draft matter now.
