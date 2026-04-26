# Stage Contracts

## Draft Stage

- Name: `DraftStage`
- Id: -
- Owner: `AuthorSkill`
- Lane: -
- Supports: -
- Applies to: -
- Emits: `DraftReceipt`
- Artifacts: -
- Checkpoint: `durable`
- Intent: Draft with Review the draft. nearby.
- Durable target: Draft receipt.
- Durable evidence: Draft receipt.
- Advance condition: Draft receipt lands.
- Risk guarded: Do not publish the draft before review.
- Entry: -
- Repair routes: -
- Waiver policy: -
- Forbidden outputs: -

### Inputs

| Key | Kind | Type |
| --- | --- | --- |
| - | - | No typed inputs. |

## Review Stage

- Name: `ReviewStage`
- Id: -
- Owner: `ReviewSkill`
- Lane: -
- Supports: -
- Applies to: -
- Emits: -
- Artifacts: -
- Checkpoint: `durable`
- Intent: Review the draft.
- Durable target: Review notes.
- Durable evidence: Review notes.
- Advance condition: Review notes land.
- Risk guarded: Check that review notes name the draft.
- Entry: -
- Repair routes: -
- Waiver policy: -
- Forbidden outputs: -

### Inputs

| Key | Kind | Type |
| --- | --- | --- |
| `draft` | `receipt` | `DraftReceipt` |
