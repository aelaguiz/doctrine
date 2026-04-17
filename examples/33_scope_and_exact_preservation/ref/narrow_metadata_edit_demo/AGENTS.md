Keep narrow ownership explicit and preserve every unowned field.

## Narrow Metadata Edit

Keep narrow ownership explicit and preserve every unowned field.

Choose one mode for this turn:
- name-only
- summary-refresh

When the mode is name-only:
- The current artifact is Section Metadata.
- Only edit `SectionMetadata.name`.
- Keep `SectionMetadata.*` unchanged except `SectionMetadata.name`.
- Keep decisions from `ApprovedPlan`.

When the mode is summary-refresh:
- The current artifact is Section Metadata.
- Only edit `SectionMetadata.name` and `SectionMetadata.description`.
- Keep `SectionMetadata.*` unchanged except `SectionMetadata.name` and `SectionMetadata.description`.
- Keep decisions from `ApprovedStructure`.
- Do not modify {`SectionMetadata.taxonomy`, `SectionMetadata.flags`}.

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

## Outputs

### Section Metadata

| Contract | Value |
| --- | --- |
| Target | File |
| Path | `unit_root/_authoring/section_metadata.json` |
| Shape | Json Object |
| Requirement | Required |

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

- Current Artifact: Name the one artifact that is current now.

#### Trust Surface

- `Current Artifact`

- Standalone Read: This output should stand on its own. The next owner should know which artifact is current now.
