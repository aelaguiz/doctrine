Handle the last narrow wording pass after structure is already locked.

## Metadata Polish

This pass runs only when metadata polish is owed now.

Active mode: manifest-title.

Current artifact: Primary Manifest.

Must CurrentHandoff.preserve_basis == ApprovedPlan.

Own only `PrimaryManifest.title`.

Preserve exact `PrimaryManifest.*` except `PrimaryManifest.title`.

Preserve decisions `ApprovedPlan`.

Accepted Peer Set is comparison-only support.

If unclear(pass_mode, CurrentHandoff.preserve_basis):
- Stop: Mode or preserve basis is unclear.
- Route the same issue back to RoutingOwner.

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

#### Current Artifact

Name the one artifact that is current now.

#### Active Mode

Name the one active mode for this pass.

#### Preserve Basis

Name the upstream declaration whose decisions remain authoritative.

#### Comparison Basis

Name any comparison-only artifacts used in this pass.

#### Trust Surface

- Current Artifact
- Active Mode
- Preserve Basis
- Comparison Basis when peer comparison is used

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, which mode is active, and why that preserve basis remains authoritative.
