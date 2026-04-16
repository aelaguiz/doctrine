Read the selected handoff owner from an emitted output.

## Outputs

### Proof Result

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Comment |
| Requirement | Required |

- Route Choice: `Route Choice`

## Final Output

### Route From Final Reply

> **Final answer contract**
> End the turn with one final assistant message that follows this contract.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Natural-language markdown |
| Shape | Comment |
| Requirement | Required |
- Next Owner: the selected route's next owner key

## Handoff Routing

Read the route choice from the emitted proof result.

Select one route from ProofResult.route_choice.
Use exactly one route choice:
- Accept
- Change

If the route choice is Accept:
- Send to AcceptanceCritic.

If the route choice is Change:
- Send to ChangeEngineer.
