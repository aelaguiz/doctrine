Edit in exactly one typed mode and carry that mode through the handoff.

## Mode-Aware Edit

Edit in exactly one typed mode and carry that mode through the handoff.

This pass runs only when edit is owed now.

Work in exactly one mode:
- manifest-title
- section-summary

If mode is manifest-title:
- Current artifact: Approved Plan.
- Must CurrentHandoff.preserve_basis == ApprovedPlan.

If mode is section-summary:
- Current artifact: Approved Structure.
- Must CurrentHandoff.preserve_basis == ApprovedStructure.

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

## Outputs

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Active Mode

Name the active mode for this pass.

#### Trust Surface

- Current Artifact
- Active Mode

#### Standalone Read

A downstream owner must be able to read this output alone and know which artifact is current now and which mode is active.
