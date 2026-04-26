# Stage Contracts

## Prepare Graph

- Name: `PrepareGraph`
- Id: -
- Owner: `ControllerSkill`
- Lane: -
- Supports: `SlotWorkerSkill`
- Applies to: -
- Emits: -
- Artifacts: -
- Checkpoint: `durable`
- Intent: Prepare graph inputs.
- Durable target: Graph input receipt.
- Durable evidence: Graph input receipt.
- Advance condition: Graph inputs are current.
- Risk guarded: Do not run slots with stale inputs.
- Entry: Start only after graph inputs are current.
- Repair routes: Route stale inputs back to preparation.
- Waiver policy: Only a human owner can waive stale inputs.
- Forbidden outputs: -

### Inputs

| Key | Kind | Type |
| --- | --- | --- |
| - | - | No typed inputs. |

## Run Slot

- Name: `RunSlot`
- Id: -
- Owner: `SlotWorkerSkill`
- Lane: -
- Supports: -
- Applies to: -
- Emits: -
- Artifacts: -
- Checkpoint: `durable`
- Intent: Run one graph slot.
- Durable target: Slot receipt.
- Durable evidence: Slot receipt.
- Advance condition: Slot receipt lands.
- Risk guarded: Do not merge partial slot output.
- Entry: Start after preparation succeeds.
- Repair routes: -
- Waiver policy: -
- Forbidden outputs: -

### Inputs

| Key | Kind | Type |
| --- | --- | --- |
| - | - | No typed inputs. |
