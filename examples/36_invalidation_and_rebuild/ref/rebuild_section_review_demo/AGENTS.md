Rebuild invalidated review work and reissue it as current truth.

## Rebuild Section Review

This pass runs only when rebuild requested.

Current artifact: Section Review.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.

## Outputs

### Section Review

- Target: File
- Path: `unit_root/_authoring/SECTION_REVIEW.md`
- Shape: Markdown Document
- Requirement: Required

### Rebuild Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Trust Surface

- Current Artifact

#### Standalone Read

This output should stand on its own. The next owner should know what is current now.
