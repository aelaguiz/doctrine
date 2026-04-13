Separate comparison help, live truth, and rewrite evidence.

## Rewrite-Aware Polish

Current artifact: Section Metadata.

Accepted Peer Set is comparison-only support.

When CurrentHandoff.rewrite_regime is rewrite, ignore {`SectionMetadata.name`, `SectionMetadata.description`} for rewrite evidence.

Stale Metadata Notes does not count as truth for this pass.

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

#### Current Artifact

Name the one artifact that is current now.

#### Comparison Basis

Name any comparison-only inputs used in this pass.

#### Rewrite Evidence Exclusions

Name any fields whose old values do not count as rewrite evidence.

#### Trust Surface

- Current Artifact
- Comparison Basis
- Rewrite Evidence Exclusions on rewrite passes

#### Standalone Read

This output should stand on its own. The next owner should know what is current, what was comparison-only, and what old wording no longer counts as rewrite evidence.
