Keep reusable law subsections explicit in the base workflow.

## Base Metadata Polish

Current artifact: Section Metadata.

Accepted Peer Set is comparison-only support.

If unclear(CurrentHandoff.preserve_basis):
- Stop: Preserve basis is unclear.
- Route the same issue back to RoutingOwner.

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

#### Current Artifact

Name the one artifact that is current now.

#### Comparison Basis

Name any comparison-only artifacts used in this pass.

#### Trust Surface

- Current Artifact
- Comparison Basis

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now and what was comparison-only.
