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
| Schema file | `schemas/repo_status.schema.json` |
| Example file | `examples/repo_status.example.json` |
| Requirement | Required |

#### Payload Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `summary` | string | Short natural-language status. |
| `status` | string | Current repo outcome. |
| `next_step` | string \| null | Null only when no follow-up is needed. |

#### Example

```json
{
  "summary": "Branch is clean and checks passed.",
  "status": "ok",
  "next_step": null
}
```

#### Field Notes

Use the schema fields exactly once.
Keep `summary` short and user-facing.

#### Read on Its Own

The final answer should stand on its own as one structured repo-status result.
