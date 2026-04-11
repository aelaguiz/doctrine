Import stdlib role-home defaults and prove named portable-truth law overrides.

## Read First

### Current Truth First

Read the declared current artifact and its declared carrier first.
Treat the declared current artifact as authoritative for this turn.

### Comparison Boundary

Treat comparison-only artifacts as support, not as current truth.
Do not treat nearby files, stale siblings, or unaccepted artifacts as current merely because they exist.

### Lane Entry

Read the portable-truth handoff before you touch rewrite-aware metadata work.

## Workflow Core

### Portable Truth Section Contract

Use `activation` to decide whether the branch is live.
Use `mode_selection` to bind one typed mode when a mode matters.
Use `currentness` to bind one current artifact or `current none`.
Use `scope` to keep ownership and preservation explicit.
Use `evidence` to keep comparison-only help and rewrite evidence honest.
Use `invalidation` to revoke downstream portability when required.
Use `stop_lines` to keep stop and reroute behavior explicit.

### Truth Surface Boundary

Keep currentness in workflow law.
Keep downstream trust on declared output fields and trust_surface.
Do not shift portable truth back into vague handoff narrative once the output contract exists.

### Override Discipline

When a portable-truth workflow is meant to be inherited, keep named law subsections stable.
Have every child account for each inherited law subsection exactly once.
Prefer explicit patching over hidden merge or silent fallback.

### Local Portable Truth Proof

Keep activation, mode_selection, currentness, scope, evidence, invalidation, and stop_lines explicit in the rewrite-aware metadata workflow below.

## How To Take A Turn

### Turn Sequence

Read the current artifact and the declared carrier first.
Do the required analysis before you emit durable output.
Close the turn by making currentness, stop lines, and routes explicit.

### Guardrails

Do not compress uncertain state into vague summary language.
Fail loud when the next owner or current artifact is not honest yet.

## Metadata Polish

This pass runs only when metadata polish is owed now.

Work in exactly one mode:
- manifest-title
- section-summary

If mode is manifest-title:
- Preserve decisions `ApprovedPlan`.

If mode is section-summary:
- Preserve decisions `ApprovedStructure`.

Work in exactly one mode:
- manifest-title
- section-summary

If mode is manifest-title:
- Current artifact: Primary Manifest.
- Must doctrine.std.coordination.inputs.CurrentHandoff.preserve_basis == ApprovedPlan.

If mode is section-summary:
- Current artifact: Section Metadata.
- Must doctrine.std.coordination.inputs.CurrentHandoff.preserve_basis == ApprovedStructure.

Accepted Peer Set is comparison-only support.

When doctrine.std.coordination.inputs.CurrentHandoff.rewrite_regime is rewrite, ignore `SectionMetadata.description` for rewrite evidence.

If structure changed:
- Section Review is no longer current.
- Stop: Structure changed; downstream review is no longer current.
- Route the same issue back to RoutingOwner.

If unclear(pass_mode, doctrine.std.coordination.inputs.CurrentHandoff.preserve_basis):
- Stop: Mode or preserve basis is unclear.
- Route the same issue back to RoutingOwner.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided coordination facts for currentness, active mode, preserve basis, rewrite regime, invalidations, and stop-or-route conditions.

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

Use accepted peer examples only for comparison when metadata polish needs them.

## Outputs

### Primary Manifest

- Target: File
- Path: `unit_root/_authoring/primary_manifest.json`
- Shape: Json Object
- Requirement: Required

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Active Mode

Name the one active mode for this pass.

#### Preserve Basis

Name the upstream declaration whose decisions remain authoritative.

#### Comparison Basis

Name any comparison-only artifacts used in this pass.

#### Rewrite Evidence Exclusions

Name any fields whose old values do not count as rewrite evidence.

#### Invalidations

Name any artifacts that are no longer current.

#### Trust Surface

- Current Artifact
- Active Mode
- Preserve Basis
- Comparison Basis
- Rewrite Evidence Exclusions
- Invalidations

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, which mode is active, why that preserve basis remains authoritative, what was comparison-only, what old wording no longer counts as rewrite evidence on rewrite passes, and what is no longer current when structure changed.

## Standards And Support

### Trust Surface Discipline

Make the trust surface explicit for the next owner.
Keep downstream trust on declared output fields and trust_surface.

### Readback Guardrail

Do not compress currentness, comparison-only basis, rewrite exclusions, or invalidations into vague summary language.
Do not let standalone readback promise more than the declared trust surface carries.

### Local Readback Rule

Keep preserve basis, rewrite exclusions, and invalidations explicit for the next owner.

## Skills And Support

### Skill First Support

Prefer explicit reusable skills for specialist judgment.
Do not smuggle deep quality bars into one-off workflow prose when a named skill can carry them.

### Capability Boundary

Keep domain-local capability bars on named skills or pack-local support surfaces.
Do not turn temporary support prose into hidden runtime machinery.

### Local Skill Note

Keep rewrite-aware metadata checks on named reusable skills when specialist judgment is needed.
