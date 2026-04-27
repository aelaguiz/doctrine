# Stage Contracts

## Consume Packet

- Name: `ConsumePacket`
- Id: -
- Owner: `ConsumerSkill`
- Lane: -
- Supports: -
- Applies to: -
- Emits: -
- Artifacts: -
- Checkpoint: `durable`
- Intent: Consume the durable packet.
- Durable target: Review notes.
- Durable evidence: Review notes.
- Advance condition: Review notes land.
- Risk guarded: Do not read a missing packet.
- Entry: -
- Repair routes: -
- Waiver policy: -
- Forbidden outputs: -

### Inputs

| Key | Kind | Type |
| --- | --- | --- |
| `packet` | `artifact` | `SectionPacket` |

## Produce Packet

- Name: `ProducePacket`
- Id: -
- Owner: `ProducerSkill`
- Lane: -
- Supports: -
- Applies to: -
- Emits: -
- Artifacts: `SectionPacket`
- Checkpoint: `durable`
- Intent: Produce the durable packet.
- Durable target: Section packet.
- Durable evidence: Section packet receipt.
- Advance condition: Packet is written.
- Risk guarded: Do not advance without the packet receipt.
- Entry: -
- Repair routes: -
- Waiver policy: -
- Forbidden outputs: -

### Inputs

| Key | Kind | Type |
| --- | --- | --- |
| - | - | No typed inputs. |
