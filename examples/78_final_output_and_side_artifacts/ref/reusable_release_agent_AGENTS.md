Ship the change through reusable outputs and still end with the dedicated final answer.

## Ship

Do the work, inherit the reusable outputs contract, and end with the declared final output.

## Outputs

### Side Artifact

#### Release Notes File

| Contract | Value |
| --- | --- |
| Target | File |
| Path | `artifacts/RELEASE_NOTES.md` |
| Shape | Markdown Document |
| Requirement | Required |

##### Standalone Read

RELEASE_NOTES.md should stand on its own and say what shipped.

## Final Output

### Release Summary Response

> **Final answer contract**
> End the turn with one final assistant message that follows this contract.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Natural-language markdown |
| Shape | Comment Text |
| Requirement | Required |

#### Expected Structure

Lead with the shipped outcome.
End with the next owner or step when one matters.

#### Read on Its Own

The user should understand what changed and what happens next.
