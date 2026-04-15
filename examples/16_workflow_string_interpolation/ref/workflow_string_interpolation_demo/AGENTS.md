Keep one workflow sentence readable while still pulling the typed contract truth from named declarations.

## Immediate Local Read

### Read Now

Read the current issue, the current Issue Plan And Route, the latest issue comment that names the current files, track.meta.json at `track_root/track.meta.json`, any current CONCEPTS.md at `section_root/_authoring/CONCEPTS.md`, and nearby section context only as support evidence to re-earn.

### Handoff Shape

When you stop, leave one Final Handoff Comment through Turn Response.

## Inputs

### Current Issue Plan

- Source: Prompt
- Shape: Markdown Document
- Requirement: Required

Use the current issue plan to confirm the intended owner and next step.

### Track Metadata

- Source: File
- Path: `track_root/track.meta.json`
- Shape: Json Object
- Requirement: Required

Use this file as the current track metadata truth.

### Current Concepts

- Source: File
- Path: `section_root/_authoring/CONCEPTS.md`
- Shape: Markdown Document
- Requirement: Advisory

Use this only when the section already has live concepts to preserve.

## Outputs

### Final Handoff Comment

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Markdown Document |
| Requirement | Required |

Use this output contract when you leave the next owner one clear update.
