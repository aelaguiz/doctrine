Patch inherited law explicitly and add rewrite-only evidence rules.

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

## Rewrite-Aware Metadata Polish

Work in exactly one metadata mode.

If mode is manifest-title, current artifact is Primary Manifest.

If mode is section-summary, current artifact is Section Metadata.

Accepted Peer Set is comparison-only support.

On rewrite passes, the old title or summary wording does not count as rewrite evidence.

If structure changed, Section Review is no longer current. The coordination handoff must name that invalidation. Stop and route the same issue back to RoutingOwner.

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
- Rewrite Evidence Exclusions on rewrite passes
- Invalidations when structure changed

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, what was comparison-only, and what is no longer current.
