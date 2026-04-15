Invalidate downstream review when structure changes.

## Structure Change

This pass runs only when structure changed.

Current artifact: Section Metadata.

Section Review is no longer current.

Stop: Structure moved; downstream review is no longer current.

Route the same issue back to RoutingOwner for rebuild.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.

## Outputs

### Section Metadata

| Contract | Value |
| --- | --- |
| Target | File |
| Path | `unit_root/_authoring/section_metadata.json` |
| Shape | Json Object |
| Requirement | Required |

### Invalidation Handoff

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Comment |
| Requirement | Required |

#### Current Artifact

Name the one artifact that is current now.

#### Invalidations

Name any artifacts that are no longer current.

#### Trust Surface

- `Current Artifact`
- `Invalidations`

#### Standalone Read

This output should stand on its own. The next owner should know what is current now and what is no longer current.
