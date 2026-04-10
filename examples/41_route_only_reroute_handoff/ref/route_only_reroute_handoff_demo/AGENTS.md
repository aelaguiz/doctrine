Keep explicit route-only reroutes aligned with the emitted handoff comment.

## Route-Only Reroute

Stop and reroute when the specialist output is missing and the next owner is still unclear.

This pass runs only when current specialist output is missing and next owner is unknown.

There is no current artifact for this turn.

Stop: No specialist artifact is current for this turn.

Route the same issue back to RoutingOwner.

## Inputs

### Route Facts

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided route facts that say whether the current specialist output is missing, whether the next owner is still unclear, and what RoutingOwner should do next after the reroute.

## Outputs

### Reroute Handoff Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Route

Say plainly that this is a route-only reroute turn: no specialist artifact is current and the issue is returning to RoutingOwner.

#### Next Owner

Say plainly that RoutingOwner now owns the rerouted turn.

#### Next Step

Name the next reroute follow-up step from the route facts.

#### Standalone Read

A downstream owner should be able to read this comment alone and understand that this route-only turn rerouted because no specialist artifact is current, who owns next, and what the next reroute step is.
