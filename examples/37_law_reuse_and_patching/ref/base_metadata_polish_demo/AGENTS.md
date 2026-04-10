Keep reusable law subsections explicit in the base workflow.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say which metadata mode is active, which preserve basis remains authoritative, whether this pass is a rewrite, and whether structure changed.

### Accepted Peer Set

- Source: File
- Path: `catalog/accepted_peers.json`
- Shape: Json Object
- Requirement: Advisory

## Base Metadata Polish

Work in exactly one metadata mode.

If mode is manifest-title, current artifact is Primary Manifest.

If mode is section-summary, current artifact is Section Metadata.

Accepted Peer Set is comparison-only support.

If mode or preserve basis is unclear, stop and route the same issue back to RoutingOwner.

## Outputs

### Primary Manifest

- Target: File
- Path: `unit_root/_authoring/primary_manifest.json`
- Shape: Json Object
- Requirement: Required

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
- Comparison Basis

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, what was comparison-only, and what is no longer current.
