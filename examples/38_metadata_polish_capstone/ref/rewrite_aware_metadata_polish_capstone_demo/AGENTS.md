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

Active mode: section-summary.

Current artifact: Section Metadata.

Own only `name` and `description`.

Preserve every other metadata field exactly.

Preserve the decisions already owned by Approved Structure.

Do not widen into `taxonomy` or `flags`.

Accepted Peer Set is comparison-only support.

On rewrite passes, the old `name` and `description` values do not count as rewrite evidence.

If structure changed, Section Review is no longer current. The rewrite-aware coordination handoff must say so. Stop and route the same issue back to RoutingOwner for rebuild.

If mode or preserve basis is unclear, stop and route the same issue back to RoutingOwner.

## Outputs

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Rewrite-Aware Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Trust Surface

- Current Artifact
- Active Mode
- Preserve Basis
- Comparison Basis when peer comparison is used
- Rewrite Evidence Exclusions on rewrite passes
- Invalidations when structure changed

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, which mode is active, why that preserve basis remains authoritative, what old wording does not count as rewrite evidence on rewrite passes, and what is no longer current when structure changed.
