# Controller Graph

Graph for Author Skill.

## Roots

- `flow AuthorFlow`

## Sets

- None.

## Policy

- `require checked_skill_mentions`
- `require relation_reason`
- `allow unbound_edges`
- `warn edge_route_binding_missing`

## Skill Relations

- `AuthorSkill` requires `ReviewSkill` - Review uses review-package.

## Warnings

- `W209` `skill_flow AuthorFlow`: Edge route binding is missing. Skill flow `AuthorFlow` edge `DraftStage -> ReviewStage` is allowed by graph policy but has no `route:` binding.

## Reached

- Flows: 1
- Stages: 2
- Skills: 2
- Artifacts: 0
- Receipts: 1
- Packages: 2
