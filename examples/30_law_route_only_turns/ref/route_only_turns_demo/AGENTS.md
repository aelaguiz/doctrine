Keep route-only work explicit when no durable artifact is current.

## Route-Only Triage

Handle turns that can only stop and reroute.

This pass runs only when current handoff is missing or current handoff is unclear.

If current handoff is missing:
- There is no current artifact for this turn.
- Stop: Current handoff is missing.
- Route the same issue back to RoutingOwner.

If current handoff is unclear:
- There is no current artifact for this turn.
- Stop: Current handoff is unclear.
- Route the same issue back to RoutingOwner.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether the current handoff is missing or unclear.

## Outputs

### Coordination Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Standalone Read

A downstream owner should be able to read this comment alone and understand that no current artifact was carried forward.
