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

Work in exactly one mode:
- manifest-title
- section-summary

If mode is manifest-title:
- Current artifact: Primary Manifest.
- The coordination handoff must name that current artifact.
- Own only `title`.
- Preserve every other manifest field exactly.
- Preserve the decisions already owned by Approved Plan.

If mode is section-summary:
- Current artifact: Section Metadata.
- The coordination handoff must name that current artifact.
- Own only `name` and `description`.
- Preserve every other metadata field exactly.
- Preserve the decisions already owned by Approved Structure.
- Do not widen into `taxonomy` or `flags`.

Accepted Peer Set is comparison-only support.

On rewrite passes, the old title or summary wording does not count as rewrite evidence.

If structure changed, Section Review is no longer current. The coordination handoff must say so.

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
- Active Mode
- Preserve Basis
- Comparison Basis when peer comparison is used
- Rewrite Evidence Exclusions on rewrite passes
- Invalidations when structure changed

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, why it is current, and what no longer counts as current.
