Carry a newly produced artifact as the current downstream truth.

## Carry Current Truth

Keep one current artifact explicit and portable.

Current artifact: Section Metadata.

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

#### Trust Surface

- Current Artifact

#### Standalone Read

A downstream owner must be able to read this output alone and know which artifact is current now.
