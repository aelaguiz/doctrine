Guard route-specific fields with route.exists.

## Maybe Routed Workflow

Route only when host route facts require it.

This pass runs only when true.

No artifact is current for this turn.

Stop: Reply and stop.

When RouteFacts.should_route, hand off to ReviewLead.

## Inputs

### Route Facts

- Source: Prompt
- Shape: Json Object
- Requirement: Required

- Should Route: `Should Route`

## Outputs

### Guarded Workflow Route Binding Comment

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Comment |
| Requirement | Required |

#### Next Owner

Show this only when a routed owner exists.

Review Lead
