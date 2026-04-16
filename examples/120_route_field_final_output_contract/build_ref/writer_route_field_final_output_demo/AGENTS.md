Choose the next owner from the final output itself.

## Final Output

### Writer Decision

> **Final answer contract**
> End the turn with one final assistant message that follows this schema.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Structured JSON |
| Shape | Writer Decision JSON |
| Schema | Writer Decision Schema |
| Profile | OpenAIStructuredOutput |
| Generated Schema | `schemas/writer_decision.schema.json` |
| Requirement | Required |

#### Payload Fields

| Field | Type | Required On Wire | Null Allowed | Meaning |
| --- | --- | --- | --- | --- |
| `next_route` | string | Yes | No | Pick the one next owner for this turn. |
| `summary` | string | Yes | No | Say what changed in this pass. |

- Kind: Json Object

#### Muse Route

Show this only when route.choice is WriterDecisionSchema.next_route.seek_muse.

Send to Muse for fresh inspiration. Next owner: Muse.

#### Critic Route

Show this only when route.choice is WriterDecisionSchema.next_route.ready_for_critic.

Send to PoemCritic for judgment. Next owner: Poem Critic.
