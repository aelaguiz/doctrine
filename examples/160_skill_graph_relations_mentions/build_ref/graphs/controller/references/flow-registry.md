# Flow Registry

## Author Flow

- Name: `AuthorFlow`
- Intent: Run Author Skill with Review Skill.
- Start: `DraftStage` (stage)
- Approve: -
- Terminals: `ReviewStage`

### Edges

| From | To | Kind | Route | When | Why |
| --- | --- | --- | --- | --- | --- |
| `DraftStage` (stage) | `ReviewStage` (stage) | `normal` | - | - | The draft moves to Review Skill. |

### Repeats

| Repeat | Flow | Over | Order | Why |
| --- | --- | --- | --- | --- |
| - | - | - | - | No repeat nodes. |
