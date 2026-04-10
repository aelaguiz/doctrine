Keep source-to-target mappings stable during a narrow update.

## Preserve Mapping

Current artifact: Slot Mapping.

Preserve mapping `SlotMapping`.

## Inputs

### Slot Mapping

- Source: File
- Path: `unit_root/_authoring/slot_mapping.json`
- Shape: Json Object
- Requirement: Required

## Outputs

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Trust Surface

- Current Artifact

#### Standalone Read

A downstream owner must be able to read this output alone and know which artifact remains current now.
