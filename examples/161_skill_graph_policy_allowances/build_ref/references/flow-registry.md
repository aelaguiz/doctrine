# Flow Registry

## Main Flow

- Name: `MainFlow`
- Intent: -
- Start: `DraftStage` (stage)
- Approve: -
- Terminals: `ReviewLoop`

### Edges

| From | To | Kind | Route | When | Why |
| --- | --- | --- | --- | --- | --- |
| `DraftStage` (stage) | `ReviewLoop` (flow) | `normal` | - | - | Drafting enters the review loop. |

### Repeats

| Repeat | Flow | Over | Order | Why |
| --- | --- | --- | --- | --- |
| - | - | - | - | No repeat nodes. |

## Review Loop

- Name: `ReviewLoop`
- Intent: -
- Start: `ReviewStage` (stage)
- Approve: -
- Terminals: `DraftStage`

### Edges

| From | To | Kind | Route | When | Why |
| --- | --- | --- | --- | --- | --- |
| `ReviewStage` (stage) | `DraftStage` (stage) | `normal` | - | `ReviewDecision.revise` | The reviewer can send the work back to drafting. |

### Repeats

| Repeat | Flow | Over | Order | Why |
| --- | --- | --- | --- | --- |
| - | - | - | - | No repeat nodes. |
