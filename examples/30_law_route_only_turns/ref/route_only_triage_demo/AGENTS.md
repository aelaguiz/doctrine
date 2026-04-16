Set up route-only law before the richer handoff examples.

## Route-Only Triage

Handle turns that can only stop and reroute.

Use this pass only when current handoff is missing or current handoff is unclear.

If current handoff is missing:
- No artifact is current for this pass.
- Stop: Current handoff is missing.
- Route the same issue back to RoutingOwner.

If current handoff is unclear:
- No artifact is current for this pass.
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

- Standalone Read: This comment should stand on its own. The next owner should know that no current artifact was carried forward.
