Handle the last narrow wording pass after structure is already locked.

## Metadata Polish

Use this pass only when metadata polish is owed now.

This pass is for `section-summary` mode.

The current artifact is Section Metadata.

Make sure current_handoff.preserve_basis == approved_structure.

Only edit `section_metadata.name` and `section_metadata.description`.

Keep `section_metadata.*` unchanged except `section_metadata.name` and `section_metadata.description`.

Keep decisions from `approved_structure`.

Do not modify {`section_metadata.taxonomy`, `section_metadata.flags`}.

Accepted Peer Set is support only for comparison.

When pass_mode is section-summary and current_handoff.rewrite_regime is rewrite, ignore {`section_metadata.name`, `section_metadata.description`} for rewrite evidence.

If unclear(pass_mode, current_handoff.preserve_basis):
- Stop: Mode or preserve basis is unclear.
- Route the same issue back to RoutingOwner.

If structure changed:
- Section Review is no longer current.
- Stop: Structure moved; downstream review is no longer current.
- Route the same issue back to RoutingOwner for rebuild.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host handoff facts. They say whether metadata polish is owed, which mode is active, which preserve basis still decides, whether peer comparison is in play, whether this pass is a rewrite, and whether structure changed.

### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

### Approved Structure

- Source: File
- Path: `unit_root/_authoring/APPROVED_STRUCTURE.md`
- Shape: Markdown Document
- Requirement: Required

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

### Coordination Handoff Binding

#### Rewrite-Aware Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

- Current Artifact: Name the one artifact that is current now.
- Active Mode: Name the one active mode for this pass.
- Preserve Basis: Name the upstream declaration that still decides.
- Comparison Basis: Name any comparison-only artifacts used in this pass.
- Rewrite Evidence Exclusions: Name any fields whose old values do not count as rewrite evidence.
- Invalidations: Name any artifacts that are no longer current.

##### Trust Surface

- `Current Artifact`
- `Active Mode`
- `Preserve Basis`
- Comparison Basis when peer comparison is used
- Rewrite Evidence Exclusions on rewrite passes
- Invalidations when structure changed

- Standalone Read: This output should stand on its own. The next owner should know what is current, which mode is active, why that preserve basis still decides, what old wording no longer counts as rewrite evidence on rewrite passes, and what stopped being current when structure changed.
