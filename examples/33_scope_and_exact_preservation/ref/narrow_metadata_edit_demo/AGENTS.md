Keep narrow ownership explicit and preserve every unowned field.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say which metadata edit mode is active.

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

## Narrow Metadata Edit

Keep narrow ownership explicit and preserve every unowned field.

Work in exactly one mode:
- name-only
- summary-refresh

If mode is name-only:
- Current artifact: Section Metadata.
- Own only `name`.
- Preserve every other metadata field exactly.
- Preserve the decisions already owned by Approved Plan.

If mode is summary-refresh:
- Current artifact: Section Metadata.
- Own only `name` and `description`.
- Preserve every other metadata field exactly.
- Preserve the decisions already owned by Approved Structure.
- Do not widen into `taxonomy` or `flags`.

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

#### Standalone Read

A downstream owner must be able to read this output alone and know which artifact is current now.
