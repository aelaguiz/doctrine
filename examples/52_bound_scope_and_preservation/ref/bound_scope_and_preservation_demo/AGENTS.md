Keep narrow ownership and preserved truth coherent through named bindings.

## Bound Scope And Preservation

Keep narrow ownership and preserved upstream truth attached to named bindings.

Current artifact: Section Metadata.

Own only {`section_metadata.name`, `section_metadata.description`}.

Preserve exact `section_metadata.*` except `section_metadata.name`, `section_metadata.description`.

Preserve structure `approved_boundary`.

## Inputs

### Section Metadata Binding

#### Section Metadata

- Source: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Approved Boundary Binding

#### Approved Boundary

- Source: Prompt
- Shape: Json Object
- Requirement: Required

## Outputs

### Coordination Handoff Binding

#### Coordination Handoff

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Comment |
| Requirement | Required |

##### Current Artifact

Name the one artifact that is current now.

##### Trust Surface

- `Current Artifact`

##### Standalone Read

This output should stand on its own. The next owner should know which artifact is current now.
