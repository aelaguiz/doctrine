Edit in exactly one typed mode and carry that mode through the handoff.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether edit work is owed, which mode is active, and which preserve basis stays authoritative.

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

## Mode-Aware Edit

This pass runs only when edit work is owed now.

Work in exactly one mode:
- manifest-title
- section-summary

If mode is manifest-title:
- Current artifact: Primary Manifest.
- Approved Plan must stay the preserve basis for this mode.
- The coordination handoff must name manifest-title as the active mode.

If mode is section-summary:
- Current artifact: Section Metadata.
- Approved Structure must stay the preserve basis for this mode.
- The coordination handoff must name section-summary as the active mode.

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

#### Standalone Read

A downstream owner must be able to read this output alone and know which artifact is current now and which mode is active.
