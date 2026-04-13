Do not keep reviewing against invalidated downstream truth.

## Blocked Section Review

This pass runs only when section review invalidated.

No artifact is current for this turn.

Stop: Section Review is invalidated until rebuild work completes.

Route the same issue back to RoutingOwner until review is rebuilt.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.

## Outputs

### Blocked Review Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Invalidations

Name any artifacts that are still no longer current.

#### Trust Surface

- Invalidations

#### Standalone Read

This output should stand on its own. The next owner should know what is no longer current.
