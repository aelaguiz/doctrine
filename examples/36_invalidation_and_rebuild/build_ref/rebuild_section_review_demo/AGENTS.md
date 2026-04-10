Rebuild invalidated review work and reissue it as current truth.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.

## Rebuild Section Review

Current artifact: Section Review.

The coordination handoff must name Section Review as current again.

## Outputs

### Section Review

- Target: File
- Path: `unit_root/_authoring/SECTION_REVIEW.md`
- Shape: Markdown Document
- Requirement: Required

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Trust Surface

- Current Artifact

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now and what is no longer current.
