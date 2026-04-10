Handle the last narrow wording pass after structure is already locked.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether metadata polish is owed, which mode is active, which preserve basis remains authoritative, whether peer comparison is in play, whether this pass is a rewrite, and whether structure changed.

### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

### Approved Structure

- Source: File
- Path: `unit_root/_authoring/APPROVED_STRUCTURE.md`
- Shape: Markdown Document
- Requirement: Required

### Accepted Peer Set

- Source: File
- Path: `catalog/accepted_peers.json`
- Shape: Json Object
- Requirement: Advisory

## Metadata Polish

This pass runs only when metadata polish is owed now.

Active mode: manifest-title.

Current artifact: Primary Manifest.

Own only `title`.

Preserve every other manifest field exactly.

Preserve the decisions already owned by Approved Plan.

Accepted Peer Set is comparison-only support.

If mode or preserve basis is unclear, stop and route the same issue back to RoutingOwner.

## Outputs

### Primary Manifest

- Target: File
- Path: `unit_root/_authoring/primary_manifest.json`
- Shape: Json Object
- Requirement: Required

### Base Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Trust Surface

- Current Artifact
- Active Mode
- Preserve Basis
- Comparison Basis when peer comparison is used

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, which mode is active, and why that preserve basis remains authoritative.
