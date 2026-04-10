Separate comparison help, live truth, and rewrite evidence.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether this pass is a rewrite.

### Accepted Peer Set

- Source: File
- Path: `catalog/accepted_peers.json`
- Shape: Json Object
- Requirement: Advisory

### Stale Metadata Notes

- Source: File
- Path: `unit_root/_authoring/stale_metadata_notes.md`
- Shape: Markdown Document
- Requirement: Advisory

## Rewrite-Aware Polish

Current artifact: Section Metadata.

Accepted Peer Set is comparison-only support.

On rewrite passes, the old `name` and `description` values do not count as rewrite evidence.

Stale metadata notes do not count as truth for this pass.

## Outputs

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

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, what was comparison-only, and what old wording no longer counts as rewrite evidence.
