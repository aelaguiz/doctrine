Handle the last narrow wording pass after structure is already locked.

## Metadata Polish

Use this pass only when metadata polish is owed now.

This pass is for `manifest-title` mode.

The current artifact is Primary Manifest.

Make sure current_handoff.preserve_basis == approved_plan.

Only edit `primary_manifest.title`.

Keep `primary_manifest.*` unchanged except `primary_manifest.title`.

Keep decisions from `approved_plan`.

Accepted Peer Set is support only for comparison.

If unclear(pass_mode, current_handoff.preserve_basis):
- Stop: Mode or preserve basis is unclear.
- Route the same issue back to RoutingOwner.

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

### Primary Manifest

| Contract | Value |
| --- | --- |
| Target | File |
| Path | `unit_root/_authoring/primary_manifest.json` |
| Shape | Json Object |
| Requirement | Required |

### Coordination Handoff Binding

#### Base Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

- Current Artifact: Name the one artifact that is current now.
- Active Mode: Name the one active mode for this pass.
- Preserve Basis: Name the upstream declaration that still decides.
- Comparison Basis: Name any comparison-only artifacts used in this pass.

##### Trust Surface

- `Current Artifact`
- `Active Mode`
- `Preserve Basis`
- Comparison Basis when peer comparison is used

- Standalone Read: This output should stand on its own. The next owner should know what is current, which mode is active, and why that preserve basis still decides.
