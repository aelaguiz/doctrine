Keep route-only repair explicit when no specialist artifact is current.

## Route Repair

Emit Route Repair Comment.

This pass runs only when RouteFacts.live_job is route_repair and current specialist output is missing.

There is no current artifact for this turn.

Stop: No specialist artifact is current for this turn.

Work in exactly one mode:
- Routing Owner

If mode is Routing Owner:
- Route to Routing Owner.

## Inputs

### Route Facts

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host route facts. They say whether route repair is active, whether the current specialist output is missing, and whether routing should stay local.

## Outputs

### Route Repair Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Route Handoff

Rendered only when a routed owner exists.

- Next Owner: Routing Owner

##### Route Summary

Route to Routing Owner. Next owner: Routing Owner.
