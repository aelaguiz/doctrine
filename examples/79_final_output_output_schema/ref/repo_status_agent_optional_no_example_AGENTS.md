Report repo status in structured form.

## Summarize

Summarize the repo state and end with the declared final output.

## Final Output

### Repo Status Final Response

> **Final answer contract**
> End the turn with one final assistant message that follows this schema.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Structured JSON |
| Shape | Repo Status JSON |
| Schema | Repo Status Schema |
| Profile | OpenAIStructuredOutput |
| Generated Schema | `schemas/repo_status_final_response.schema.json` |
| Requirement | Required |

#### Payload Fields

| Field | Type | Required On Wire | Null Allowed | Meaning |
| --- | --- | --- | --- | --- |
| `summary` | string | Yes | No | Short natural-language status. |
| `status` | string | Yes | No | Current repo outcome. |
| `next_step` | string | Yes | Yes | Null only when no follow-up is needed. |

- Kind: Json Object

#### Field Notes

Use the schema fields exactly once.
Keep `summary` short and user-facing.

#### Read on Its Own

The final answer should stand on its own as one structured repo-status result.
