Patch inherited law explicitly and add rewrite-only evidence rules.

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

## Rewrite-Aware Metadata Polish

Current artifact: Section Metadata.

Accepted Peer Set is comparison-only support.

On rewrite passes, the old `description` value does not count as rewrite evidence.

If structure changed, Section Review is no longer current. The rewrite-aware handoff must name that invalidation. Stop and route the same issue back to RoutingOwner.

If preserve basis is unclear, stop and route the same issue back to RoutingOwner.

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
- Comparison Basis
- Rewrite Evidence Exclusions on rewrite passes
- Invalidations when structure changed

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, what was comparison-only, what old wording does not count as rewrite evidence on rewrite passes, and what is no longer current when structure changed.
