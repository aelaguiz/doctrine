Keep source-to-target mappings stable during a narrow update.

## Inputs

### Slot Mapping

- Source: File
- Path: `unit_root/_authoring/slot_mapping.json`
- Shape: Json Object
- Requirement: Required

## Preserve Mapping

Current artifact: Slot Mapping.

Preserve the approved concept-to-slot mapping.

The coordination handoff must keep Slot Mapping named as the current truth.

## Outputs

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Trust Surface

- Current Artifact

#### Standalone Read

A downstream owner must be able to read this output alone and know which artifact remains current now.
