End with a route-aware final JSON result.

## Final Output

### Handoff Route Final Response

> **Final answer contract**
> End the turn with one final assistant message that follows this schema.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Structured JSON |
| Shape | Turn Result JSON |
| Schema | Turn Result Schema |
| Profile | OpenAIStructuredOutput |
| Generated Schema | `schemas/handoff_route_final_response.schema.json` |
| Requirement | Required |

#### Payload Fields

| Field | Type | Required On Wire | Null Allowed | Meaning |
| --- | --- | --- | --- | --- |
| `next_owner` | string | Yes | No | The routed next owner key. |
| `summary` | string | Yes | No | Short closeout summary. |

#### Example

```json
{
  "next_owner": "ReviewLead",
  "summary": "Hand off to ReviewLead."
}
```

- Kind: Json Object
- Next Owner: ReviewLead

#### Route Summary

Hand off to ReviewLead. Next owner: Review Lead.

#### Read on Its Own

This final JSON should stand on its own.

## Handoff Routing

Route through compiler-owned handoff routing.

Use this pass only when true.

Stop: Hand off or finish the turn.

Hand off to ReviewLead.
