# Loop Graph

Show a named authoring loop.

## Roots

- `flow MainFlow`

## Sets

- None.

## Policy

- `dag allow_cycle`: The review loop is a named authoring loop.
- `warn branch_coverage_incomplete`

## Skill Relations

- No reached skill relations.

## Warnings

- `W205` `skill_flow ReviewLoop`: Branch coverage is incomplete. Skill flow `ReviewLoop` source `ReviewStage` branches on enum `ReviewDecision` but does not cover member(s): approve.

## Reached

- Flows: 2
- Stages: 2
- Skills: 1
- Artifacts: 0
- Receipts: 0
- Packages: 0
