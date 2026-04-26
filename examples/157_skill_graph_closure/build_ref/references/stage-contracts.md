# Stage Contracts

## Controller Recovery Audit

- Name: `ControllerRecoveryAudit`
- Id: -
- Owner: `ControllerSkill`
- Lane: -
- Supports: -
- Applies to: -
- Emits: -
- Checkpoint: `durable`
- Intent: Audit the section state before work starts.
- Durable target: Recovery brief.
- Durable evidence: Recovery receipt.
- Advance condition: Recovery receipt landed.
- Risk guarded: -
- Forbidden outputs: -

### Inputs

| Key | Kind | Type |
| --- | --- | --- |
| - | - | No typed inputs. |

## Lesson Plan

- Name: `LessonPlan`
- Id: -
- Owner: `ControllerSkill`
- Lane: -
- Supports: -
- Applies to: -
- Emits: -
- Checkpoint: `durable`
- Intent: Plan one lesson.
- Durable target: Lesson plan.
- Durable evidence: Plan receipt.
- Advance condition: Plan receipt landed.
- Risk guarded: -
- Forbidden outputs: -

### Inputs

| Key | Kind | Type |
| --- | --- | --- |
| - | - | No typed inputs. |
