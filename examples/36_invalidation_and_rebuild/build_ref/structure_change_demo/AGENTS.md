Invalidate downstream review when structure changes.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.

## Structure Change

Current artifact: Section Metadata.

Section Review is no longer current after this change.

The coordination handoff must name that invalidation.

Stop and route the same issue back to RoutingOwner for rebuild.

## Outputs

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Trust Surface

- Current Artifact
- Invalidations

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now and what is no longer current.
