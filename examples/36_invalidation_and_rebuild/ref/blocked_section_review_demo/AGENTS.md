Do not keep reviewing against invalidated downstream truth.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.

## Blocked Section Review

There is no current artifact for this turn.

Stop and route the same issue back to RoutingOwner until review is rebuilt.

## Outputs

### Blocked Review Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Trust Surface

- Invalidations

#### Standalone Read

A downstream owner must be able to read this output alone and know what is no longer current.
