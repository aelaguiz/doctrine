Read the selected handoff owner from an emitted output.

## Outputs

### Proof Result

- Target: Turn Response
- Shape: Comment
- Requirement: Required

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

Choose a route from ProofResult.route_choice.
Use exactly one route choice:
- Accept
- Change

When the route choice is Accept:
- Send to AcceptanceCritic.

When the route choice is Change:
- Send to ChangeEngineer.
