Keep local route-only stops explicit when specialist output is missing.

## Route-Only Local Ownership

Stop when the specialist output is missing but the next owner is clear enough to keep ownership local.

This pass runs only when current specialist output is missing and next owner is not unknown.

No artifact is current for this turn.

Stop: No specialist artifact is current for this turn.

## Inputs

### Route Facts

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host route facts. They say whether the current specialist output is missing, whether the next owner is still unclear, and what the current owner should do next before rerouting makes sense.

## Outputs

### Local Ownership Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Route

Say this is a route-only local turn. No specialist artifact is current, so ownership stays local until rerouting makes sense.

#### Next Owner

Say plainly that ownership stays local because rerouting is not justified on this turn.

#### Next Step

Name the next local repair step from the route facts.

#### Standalone Read

This comment should stand on its own. The next owner should know that this route-only turn stayed local because no specialist artifact is current, who owns next, and what local repair step comes next.
