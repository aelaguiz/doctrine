End a route-only turn with emitted route contract metadata.

## Route Only Final Response

Emit Route Only Final Reply.

Use this pass only when route facts live job is route_only_final.

No artifact is current for this pass.

Stop: No specialist artifact is current for this turn.

Choose one mode for this turn:
- Routing Owner

When the mode is Routing Owner:
- Route to Routing Owner.

## Inputs

### Route Facts

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use host route facts for a route-only final response.

## Final Output

### Route Only Final Reply

> **Final answer contract**
> End the turn with one final assistant message that follows this contract.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Natural-language markdown |
| Shape | Comment |
| Requirement | Required |

#### Route Handoff

Show this only when a routed owner exists.

- Next Owner: Routing Owner

##### Route Summary

Route to Routing Owner. Next owner: Routing Owner.
