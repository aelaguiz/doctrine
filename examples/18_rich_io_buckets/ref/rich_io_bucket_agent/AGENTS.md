Core job: gather the section inputs and publish the current dossier truth.

## Your Job

Use the current plan as truth and keep prior review notes as continuity help only.
Always write the dossier file before you summarize the turn.

## Inputs

Read these inputs in order.

### Planning Truth

#### Current Section Plan

- Source: File
- Path: `section_root/_authoring/SECTION_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

##### Notes

Treat the current plan as the live section baseline.

### Continuity Only

Use prior review notes only as continuity help, not as proof.

#### Prior Review Notes

- Source: File
- Path: `section_root/_authoring/PRIOR_REVIEW_NOTES.md`
- Shape: Markdown Document
- Requirement: Advisory

## Outputs

Always produce these outputs when you own dossier work.
The file artifact is the durable truth. The turn summary points at that truth.

### File Truth

Write this to disk before you summarize the turn.

#### Dossier File

| Contract | Value |
| --- | --- |
| Target | File |
| Path | `section_root/_authoring/dossier_engineer.md` |
| Shape | Dossier Document |
| Requirement | Required |

##### Standalone Read

dossier_engineer.md should stand on its own and show the current dossier truth.

### Turn Summary

Use the turn response to say what changed and where the durable file lives.

#### Dossier Summary

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Turn Summary Text |
| Requirement | Required |

##### Purpose

Summarize what changed and point the reader at dossier_engineer.md.
