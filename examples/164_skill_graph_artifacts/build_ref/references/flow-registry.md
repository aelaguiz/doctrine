# Flow Registry

## Packet Flow

- Name: `PacketFlow`
- Intent: -
- Start: `ProducePacket` (stage)
- Approve: -
- Terminals: `ConsumePacket`

### Edges

| From | To | Kind | Route | When | Why |
| --- | --- | --- | --- | --- | --- |
| `ProducePacket` (stage) | `ConsumePacket` (stage) | `normal` | - | - | The consumer reads the producer artifact. |

### Repeats

| Repeat | Flow | Over | Order | Why |
| --- | --- | --- | --- | --- |
| - | - | - | - | No repeat nodes. |
