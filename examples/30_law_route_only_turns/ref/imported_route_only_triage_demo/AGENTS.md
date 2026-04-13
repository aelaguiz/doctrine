Keep imported workflow-law route labels readable.

## Imported Route-Only Triage

Prove that workflow-law route labels interpolate imported agent refs too.

This pass runs only when current handoff is missing.

There is no current artifact for this turn.

Stop: Current handoff is missing.

Route the same issue back to ImportedRoutingOwner.

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

This comment should stand on its own. The next owner should know that no current artifact was carried forward.
