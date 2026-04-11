Import the shared route-only workflow and coordination comment from the repo-level stdlib root.

## Route-Only Triage

Handle turns that can only stop and reroute.

This pass runs only when inputs.currenthandoff is missing or inputs.currenthandoff is unclear.

If inputs.currenthandoff is missing:
- There is no current artifact for this turn.
- Stop: Current handoff is missing.
- Route the same issue back to RoutingOwner.

If inputs.currenthandoff is unclear:
- There is no current artifact for this turn.
- Stop: Current handoff is unclear.
- Route the same issue back to RoutingOwner.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided coordination facts for currentness, active mode, preserve basis, rewrite regime, invalidations, and stop-or-route conditions.

## Outputs

### Coordination Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Standalone Read

A downstream owner should be able to read this comment alone and understand the coordination state for this turn.
