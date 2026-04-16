Patch inherited law explicitly and add rewrite-only evidence rules.

## Rewrite-Aware Metadata Polish

If unclear(CurrentHandoff.preserve_basis):
- Stop: Preserve basis is unclear.
- Route the same issue back to RoutingOwner.

The current artifact is Section Metadata.

Accepted Peer Set is support only for comparison.

When CurrentHandoff.rewrite_regime is rewrite, ignore `SectionMetadata.description` for rewrite evidence.

If structure changed:
- Section Review is no longer current.
- Stop: Structure changed; downstream review is no longer current.
- Route the same issue back to RoutingOwner.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether the preserve basis remains clear, whether this pass is a rewrite, and whether structure changed.

### Accepted Peer Set

- Source: File
- Path: `catalog/accepted_peers.json`
- Shape: Json Object
- Requirement: Advisory

## Outputs

### Section Metadata

| Contract | Value |
| --- | --- |
| Target | File |
| Path | `unit_root/_authoring/section_metadata.json` |
| Shape | Json Object |
| Requirement | Required |

### Rewrite-Aware Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

- Current Artifact: Name the one artifact that is current now.
- Comparison Basis: Name any comparison-only artifacts used in this pass.
- Rewrite Evidence Exclusions: Name any fields whose old values do not count as rewrite evidence.
- Invalidations: Name any artifacts that are no longer current.

#### Trust Surface

- `Current Artifact`
- `Comparison Basis`
- Rewrite Evidence Exclusions on rewrite passes
- Invalidations when structure changed

- Standalone Read: This output should stand on its own. The next owner should know what is current, what was comparison-only, what old wording no longer counts as rewrite evidence on rewrite passes, and what stopped being current when structure changed.
