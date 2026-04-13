Keep schema-backed review verdicts and routes aligned.

## Schema Backed Plan Review

Review subject: Draft Plan.
Shared review contract: Plan Review Contract.

### Contract Gate Checks

Reject: Outline Complete.

Reject: Evidence Grounded.

Accept only if The schema review contract passes.

### If Accepted

There is no current artifact for this outcome.

Accepted plan goes to ReviewLead.

### If Rejected

There is no current artifact for this outcome.

Rejected plan goes to PlanAuthor.

## Inputs

### Draft Plan

- Source: File
- Path: `unit_root/DRAFT_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

- Outline Missing: `Outline Missing`
- Evidence Missing: `Evidence Missing`

## Outputs

### Plan Review Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Verdict

State the review verdict.

#### Reviewed Artifact

Name the reviewed artifact.

#### Analysis Performed

Summarize the review analysis.

#### Output Contents That Matter

State what the next owner should read first.

#### Next Owner

Name ReviewLead when accepted and PlanAuthor when rejected.

#### Failure Detail

Rendered only when verdict is changes requested.

##### Failing Gates

List exact failing gates, including Outline Complete and Evidence Grounded when they fail.
