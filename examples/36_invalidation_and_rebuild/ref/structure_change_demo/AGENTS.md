Invalidate downstream review when structure changes.

## Structure Change

This pass runs only when structure changed.

Current artifact: Section Metadata.

Section Review is no longer current.

Stop: Structure moved; downstream review is no longer current.

Route the same issue back to RoutingOwner for rebuild.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.

## Outputs

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Invalidation Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Invalidations

Name any artifacts that are no longer current.

#### Trust Surface

- Current Artifact
- Invalidations

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now and what is no longer current.
