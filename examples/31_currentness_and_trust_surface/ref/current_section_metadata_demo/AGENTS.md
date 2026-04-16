Carry a newly produced artifact as the current downstream truth.

## Carry Current Truth

Keep one current artifact explicit and portable.

The current artifact is Section Metadata.

## Outputs

### Section Metadata

| Contract | Value |
| --- | --- |
| Target | File |
| Path | `unit_root/_authoring/section_metadata.json` |
| Shape | Json Object |
| Requirement | Required |

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

- Current Artifact: Name the one artifact that is current now.

#### Trust Surface

- `Current Artifact`

- Standalone Read: This output should stand on its own. The next owner should know which artifact is current now.
