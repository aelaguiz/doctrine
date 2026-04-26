# Flow Registry

## Run Graph

- Name: `RunGraph`
- Intent: -
- Start: `PrepareGraph` (stage)
- Approve: -
- Terminals: `SlotRun`

### Edges

| From | To | Kind | Route | When | Why |
| --- | --- | --- | --- | --- | --- |
| `PrepareGraph` (stage) | `SlotRun` (repeat) | `normal` | - | - | Prepared inputs feed each slot run. |

### Repeats

| Repeat | Flow | Over | Order | Why |
| --- | --- | --- | --- | --- |
| `SlotRun` | `RunOneSlot` | `graph_path:GraphInputs.lesson_slots` | `serial` | Each lesson slot gets one run from graph input facts. |

## Run One Slot

- Name: `RunOneSlot`
- Intent: -
- Start: `RunSlot` (stage)
- Approve: -
- Terminals: -

### Edges

| From | To | Kind | Route | When | Why |
| --- | --- | --- | --- | --- | --- |
| - | - | - | - | - | No authored edges. |

### Repeats

| Repeat | Flow | Over | Order | Why |
| --- | --- | --- | --- | --- |
| - | - | - | - | No repeat nodes. |
