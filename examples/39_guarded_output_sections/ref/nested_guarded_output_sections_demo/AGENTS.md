Keep nested conditional output readback explicit and addressable.

## Read First

Read the nested guarded output items directly from the emitted output contract.

### Read Now

- Status Summary
- Rewrite Detail

Read Status Summary before Rewrite Detail when nested conditional detail is in play.

## Inputs

### Route Facts

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host route facts. They say whether the current section is new or a full rewrite, whether the same critic miss happened again, and which status facts drove the turn.

## Outputs

### Nested Guarded Readback Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Detail Panel

##### Status Summary

Summarize the status facts that drove this turn.

##### Rewrite Detail

Show this only when route facts section status is new or full rewrite.

Explain why rewrite-aware handling applies on this turn.

- Standalone Read: This comment should stand on its own. The next owner should know which nested conditional details might appear.
