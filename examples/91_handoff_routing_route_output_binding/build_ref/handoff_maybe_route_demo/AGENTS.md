Keep route truth on the output contract.

## Inputs

### Route Facts

- Source: Prompt
- Shape: Json Object
- Requirement: Required

- Should Route: `Should Route`

## Outputs

### Handoff Guarded Turn Result

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Comment |
| Requirement | Required |

#### Kind

Show this only when a routed owner exists.

`handoff`

#### Next Owner

Show this only when a routed owner exists.

ReviewLead

#### Kind

Show this only when not (a routed owner exists).

`done`

#### Summary

Show this only when not (a routed owner exists).

`Write one short closeout summary.`

## Handoff Routing

Route only when the host route facts require it.

This pass runs only when true.

Stop: Hand off or finish the turn.

When RouteFacts.should_route, hand off to ReviewLead.
