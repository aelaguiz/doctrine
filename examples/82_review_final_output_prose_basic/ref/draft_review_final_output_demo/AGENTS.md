Keep review final outputs aligned without adding a second message surface.

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

## Final Output

### Draft Review Comment

> **Final answer contract**
> End the turn with one final assistant message that satisfies this contract.

| Contract | Value |
| --- | --- |
| Message kind | Final assistant message |
| Format | Natural-language markdown |
| Shape | Comment |
| Requirement | Required |

#### Verdict

Say whether the review accepted the draft or asked for changes.

#### Reviewed Artifact

Name the reviewed artifact this review judged.

#### Analysis Performed

Sum up the review work that led to the verdict.

#### Output Contents That Matter

Summarize the parts of the draft the next owner must read first.

#### Current Artifact

Name the artifact that remains current after review.

#### Next Owner

Name the next owner. Use ReviewLead when the draft is accepted and DraftAuthor when it is rejected.

#### Failure Detail

Rendered only when verdict is changes requested.

##### Failing Gates

Name the failing review gates in authored order.

#### Trust Surface

- Current Artifact

#### Read It Cold

This review should stand on its own. A downstream owner should know the verdict, current artifact, and next owner.
