Handle the last narrow wording pass after structure is already locked.

## Metadata Polish

This pass runs only when metadata polish is owed now.

Active mode: section-summary.

Current artifact: Section Metadata.

Must CurrentHandoff.preserve_basis == ApprovedStructure.

Own only {`SectionMetadata.name`, `SectionMetadata.description`}.

Preserve exact `SectionMetadata.*` except `SectionMetadata.name`, `SectionMetadata.description`.

Preserve decisions `ApprovedStructure`.

Do not modify {`SectionMetadata.taxonomy`, `SectionMetadata.flags`}.

Accepted Peer Set is comparison-only support.

When pass_mode is manifest-title and CurrentHandoff.rewrite_regime is rewrite, ignore `PrimaryManifest.title` for rewrite evidence.

When pass_mode is section-summary and CurrentHandoff.rewrite_regime is rewrite, ignore {`SectionMetadata.name`, `SectionMetadata.description`} for rewrite evidence.

If structure changed:
- Section Review is no longer current.
- Stop: Structure moved; downstream review is no longer current.
- Route the same issue back to RoutingOwner for rebuild.

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

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Rewrite-Aware Coordination Handoff

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

#### Rewrite Evidence Exclusions

Name any fields whose old values do not count as rewrite evidence.

#### Invalidations

Name any artifacts that are no longer current.

#### Trust Surface

- Current Artifact
- Active Mode
- Preserve Basis
- Comparison Basis when peer comparison is used
- Rewrite Evidence Exclusions on rewrite passes
- Invalidations when structure changed

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, which mode is active, why that preserve basis remains authoritative, what old wording does not count as rewrite evidence on rewrite passes, and what is no longer current when structure changed.
