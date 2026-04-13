Keep route-only work explicit when no specialist artifact is current.

## Routing-Only Turns

Handle turns that can only stop, reroute, or keep ownership explicit.

This pass runs only when route facts live job is routing, process repair, or owner repair and current specialist output is missing.

There is no current artifact for this turn.

Stop: No specialist artifact is current for this turn.

When next owner is unknown, keep the issue on RoutingOwner until the next specialist owner is clear.

## Inputs

### Route Facts

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use host route facts. They say which live job is active, whether the current specialist output is missing, whether the next owner is still unclear, whether the section is new or a full rewrite, whether the same critic miss happened again, what step comes next, what keeps failing, which role sent the issue back, and what fix comes next.

## Outputs

### Routing Handoff Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Must Include

##### Current Route

Say the route-only state now in force, including whether the turn is routing, process repair, or owner repair.

##### Next Owner

Name the next owner when ownership changes. If ownership stays local, say so. If no clear next owner is known yet, say that RoutingOwner keeps the issue.

##### Next Step

Say the next concrete step now.

#### Rewrite Mode

Rendered only when route facts section status is new or full rewrite.

Say plainly that later section metadata must be rewritten instead of inherited.

#### Repeated Problem

Rendered only when critic miss is repeated.

##### What Keeps Failing

Say what keeps failing.

##### Returned From

Say which role returned it.

##### Next Concrete Fix

Say the next concrete fix.

#### Standalone Read

This comment should stand on its own. The next owner should know that no specialist artifact is current, which route-only state is active, who owns next, and what step comes next.
