Keep workflow guidance readable while still pointing directly at the typed contracts it depends on.

## Immediate Local Read

### Read Now

Start with the current routing truth.

- Current Issue Plan
- Latest Named Files Comment
- Track Metadata

If current concepts exist for this section, read them before nearby context.

- Current Concepts

### When You Finish

Leave the next owner one current output contract instead of a vague note.

- Final Handoff Comment

## Inputs

### Current Issue Plan

- Source: Prompt
- Shape: Markdown Document
- Requirement: Required

Use the current issue plan to confirm the intended owner and next step.

### Latest Named Files Comment

- Source: File
- Path: `track_root/_authoring/LATEST_NAMED_FILES_COMMENT.md`
- Shape: Markdown Document
- Requirement: Required

Use this comment to confirm which files are current now.

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
