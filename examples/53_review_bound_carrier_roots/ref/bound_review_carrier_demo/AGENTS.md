Keep review current truth and carried state aligned through named bindings.

## Bound Carrier Review

Review subject: Draft Spec.
Shared review contract: Bound Carrier Review Contract.

### Contract Checks

Reject: The draft still needs changes.

Accept only if The shared review contract passes.

### If Accepted

Current artifact: Draft Spec.

Carry active mode: draft-rewrite.

Carry trigger reason: structure-gap.

Accepted draft goes to ReviewLead.

### If Rejected

Current artifact: Draft Spec.

Carry active mode: draft-rewrite.

Carry trigger reason: structure-gap.

Rejected draft goes to DraftAuthor.

## Inputs

### Draft Spec Binding

#### Draft Spec

- Source: File
- Path: `unit_root/DRAFT_SPEC.md`
- Shape: Markdown Document
- Requirement: Required

Use the current draft spec as the reviewed artifact.

### Review Facts Binding

#### Review Facts

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host facts that say whether the draft still needs changes.

## Outputs

### Review Comment Binding

#### Bound Review Comment

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Comment |
| Requirement | Required |

##### Verdict

Say whether the review accepted the draft or asked for changes.

##### Reviewed Artifact

Name the reviewed artifact this review judged.

##### Analysis Performed

Sum up the review work that led to the verdict.

##### Output Contents That Matter

Summarize the parts of the draft the next owner must read first.

##### Next Owner

Name the next owner. Use ReviewLead when the draft is accepted and DraftAuthor when it is rejected.

##### Current Artifact

Name the artifact that remains current after this review outcome.

##### Active Mode

Show this only when present(active_mode).

Name the active review mode for the current artifact.

##### Trigger Reason

Show this only when present(trigger_reason).

Name the trigger reason for the live artifact and mode.

##### Failure Detail

Show this only when verdict is changes requested.

###### Failing Gates

Name the failing review gates in authored order.

##### Trust Surface

- `Current Artifact`
- Active Mode when present(active_mode)
- Trigger Reason when present(trigger_reason)

##### Standalone Read

This comment should stand on its own. The next owner should know what was reviewed, what verdict landed, what is still current, which mode and trigger reason are live, who owns next, and which parts of the draft still matter.
