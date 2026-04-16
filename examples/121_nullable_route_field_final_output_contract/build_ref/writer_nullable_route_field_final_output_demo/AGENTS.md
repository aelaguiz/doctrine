Either hand off or finish from one routed final output.

## Final Output

### Writer Turn Result

> **Final answer contract**
> End the turn with one final assistant message that follows this schema.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Structured JSON |
| Shape | Writer Turn Result JSON |
| Schema | Writer Turn Result Schema |
| Profile | OpenAIStructuredOutput |
| Generated Schema | `schemas/writer_turn_result.schema.json` |
| Requirement | Required |

#### Payload Fields

| Field | Type | Required On Wire | Null Allowed | Meaning |
| --- | --- | --- | --- | --- |
| `next_route` | string | Yes | Yes | Use null when the writer can finish without a handoff. |
| `kind` | string | Yes | No | Say whether this turn hands off or finishes. |
| `summary` | string | Yes | No | Short handoff or closeout summary. |

- Kind: Json Object

#### Routed Owner

Show this only when a routed owner exists.

`Routed Owner`

Revision Partner

#### No Route

Show this only when not (a routed owner exists).

`No Route`

There is no handoff on this turn.
