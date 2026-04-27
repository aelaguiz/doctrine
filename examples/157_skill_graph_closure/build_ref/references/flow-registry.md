# Flow Registry

## F1 - Author One Lesson

- Name: `F1AuthorLesson`
- Intent: Author one lesson from a locked slot.
- Start: `LessonPlan` (stage)
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

## F2 - Author Section

- Name: `F2AuthorSection`
- Intent: Audit the section, then run one lesson per slot.
- Start: `ControllerRecoveryAudit` (stage)
- Approve: -
- Terminals: `LessonSlotRun`

### Edges

| From | To | Kind | Route | When | Why |
| --- | --- | --- | --- | --- | --- |
| `ControllerRecoveryAudit` (stage) | `LessonSlotRun` (repeat) | `normal` | - | - | Audit before per-slot authoring starts. |

### Repeats

| Repeat | Flow | Over | Order | Why |
| --- | --- | --- | --- | --- |
| `LessonSlotRun` | `F1AuthorLesson` | `graph_set:LessonSlots` | `serial` | Each slot changes the evidence for the next slot. |
