Keep reusable law subsections explicit in the base workflow.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether the preserve basis remains clear, whether this pass is a rewrite, and whether structure changed.

### Accepted Peer Set

- Source: File
- Path: `catalog/accepted_peers.json`
- Shape: Json Object
- Requirement: Advisory

## Base Metadata Polish

Current artifact: Section Metadata.

Accepted Peer Set is comparison-only support.

If preserve basis is unclear, stop and route the same issue back to RoutingOwner.

## Outputs

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Base Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Trust Surface

- Current Artifact
- Comparison Basis

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now and what was comparison-only.
