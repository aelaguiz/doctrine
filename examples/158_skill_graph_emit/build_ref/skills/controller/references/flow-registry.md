# Flow Registry

## F1 - Author One Lesson

- Name: `F1AuthorLesson`
- Intent: Plan then review one lesson.
- Start: `LessonPlan` (stage)
- Approve: -
- Terminals: `AuthorReview`

### Edges

| From | To | Kind | Route | When | Why |
| --- | --- | --- | --- | --- | --- |
| `LessonPlan` (stage) | `AuthorReview` (stage) | `normal` | `LessonPlanReceipt.next_route.review` | - | The review stage must follow the plan receipt route. |

### Repeats

| Repeat | Flow | Over | Order | Why |
| --- | --- | --- | --- | --- |
| - | - | - | - | No repeat nodes. |
