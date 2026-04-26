# Stage Contracts

## Author Review

- Name: `AuthorReview`
- Id: -
- Owner: `ControllerSkill`
- Lane: `StageLane.review`
- Supports: -
- Applies to: -
- Emits: -
- Artifacts: -
- Checkpoint: `durable`
- Intent: Review the plan before handoff.
- Durable target: Review notes.
- Durable evidence: Review receipt.
- Advance condition: Review receipt landed.
- Risk guarded: -
- Entry: -
- Repair routes: -
- Waiver policy: -
- Forbidden outputs: -

### Inputs

| Key | Kind | Type |
| --- | --- | --- |
| `flow_receipt` | `receipt` | `LessonPlanReceipt` |

## Lesson Plan

- Name: `LessonPlan`
- Id: -
- Owner: `ControllerSkill`
- Lane: `StageLane.pipeline`
- Supports: -
- Applies to: -
- Emits: `LessonPlanReceipt`
- Artifacts: -
- Checkpoint: `durable`
- Intent: Plan the lesson.
- Durable target: Lesson plan.
- Durable evidence: Plan receipt.
- Advance condition: Plan receipt landed.
- Risk guarded: -
- Entry: -
- Repair routes: -
- Waiver policy: -
- Forbidden outputs: -

### Inputs

| Key | Kind | Type |
| --- | --- | --- |
| - | - | No typed inputs. |
