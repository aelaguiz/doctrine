Keep conditional output readback explicit and addressable.

## Read First

Read the guarded sections directly from the emitted output contract.

### Read Now

- Rewrite Mode
- Repeated Problem

Read Rewrite Mode and Repeated Problem when the conditional readback matters for this turn.

## Inputs

### Route Facts

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided route facts that say whether the current section is new or a full rewrite, whether the same critic miss repeated, and what status facts drove the turn.

## Outputs

### Guarded Readback Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Rewrite Mode

Rendered only when route facts section status is new or full rewrite.

Name whether the section is brand new or undergoing a full rewrite.

#### Repeated Problem

Rendered only when critic miss is repeated.

Say whether the same critic miss has repeated.

#### Standalone Read

A downstream owner should be able to read this comment alone and know which conditional readback blocks might appear.
