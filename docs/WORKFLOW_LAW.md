# Workflow Law

Doctrine workflow law is the shipped typed surface for turns that need explicit
branch truth, not just ordinary workflow prose.

Use it when a turn needs any of these behaviors:

- an explicit activation trigger
- one active mode or one active branch at a time
- one current artifact per active leaf branch, or explicitly no current artifact
- narrow write authority with preserved truth outside the owned scope
- comparison-only support or rewrite-evidence exclusions
- invalidation when upstream structural truth moves
- stop lines and honest reroute

If you are learning the feature family, start here and then read the active
example ladder in [`examples/30_*` through `examples/42_*`](../examples/README.md).

## Mental Model

- Authored workflow prose still explains the job in human language.
- `law` inside `workflow` decides what is true now for the current turn.
- `output` still decides what the turn emits.
- keyed guarded sections inside `output` keep conditional readback on the
  output contract instead of creating a second control plane
- `trust_surface` inside `output` names the emitted fields a downstream owner
  must be able to read and trust.
- `standalone_read` is the human-facing companion to `trust_surface`. It does
  not create semantics beyond the emitted fields and carrier rules the compiler
  validates.

The core split is:

- `law` decides local truth.
- `output` plus `trust_surface` decide portable downstream truth.

## Shipped Surface

Workflow law does not add a new top-level declaration family.

It adds two reserved child surfaces on existing owners:

- `law` on `workflow`
- `trust_surface` on `output`

It also widens normal `output` record bodies with keyed guarded sections:

```prompt
output RouteOnlyHandoffOutput: "Route-Only Handoff Output"
    ...
    rewrite_mode: "Rewrite Mode" when RouteFacts.section_status in {"new", "full_rewrite"}:
        "Name whether the section is brand new or undergoing a full rewrite."
```

Guarded output sections are still output-owned authored fields:

- they render as documented conditional shells in compiled `AGENTS.md`
- they are required only when the guard is true at runtime
- their guards may read declared inputs and enum members
- they may not read workflow-local bindings, emitted output fields, or
  undeclared runtime names

The shipped statement families are grouped by job:

- branch activation and selection:
  `active when`, `when`, `mode`, `match`, `must`
- currentness:
  `current artifact ... via ...`, `current none`
- scope and preservation:
  `own only`, `preserve exact`, `preserve structure`, `preserve decisions`,
  `preserve mapping`, `preserve vocabulary`, `forbid`
- evidence roles:
  `support_only ... for comparison`,
  `ignore ... for truth|comparison|rewrite_evidence`
- truth transitions:
  `invalidate ... via ...`
- control flow:
  `stop`, `route "..." -> Agent`, `route "..." -> Agent when expr`
- reuse:
  named law subsections plus `inherit` / `override`

## Branch Activation And Selection

Use `active when` to gate the whole workflow-law path for a turn, then `when`
or `match` to shape narrower branches under it.

```prompt
law:
    active when CurrentHandoff.owes_metadata_polish

    mode pass_mode = CurrentHandoff.active_mode as MetadataPolishMode

    match pass_mode:
        MetadataPolishMode.manifest_title:
            ...

        MetadataPolishMode.section_summary:
            ...
```

Key rules:

- `mode` binds one expression to one enum.
- `match` on an enum must be exhaustive or include `else`.
- `must` is the fail-loud surface for branch-local required facts.
- active law is evaluated per leaf branch, not as one flat list.

## Currentness And Trust Carriers

`current artifact ... via ...` means two things at once:

- the named input or output is authoritative now for the active branch
- the `Output.field` carrier tells the next owner that this is true

```prompt
output CoordinationHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    trust_surface:
        current_artifact

law:
    current artifact SectionMetadata via CoordinationHandoff.current_artifact
```

Route-only or block-only turns use `current none` instead:

```prompt
law:
    when CurrentHandoff.missing:
        current none
        stop "Current handoff is missing."
        route "Route the same issue back to RoutingOwner." -> RoutingOwner
```

Currentness rules:

- every active leaf branch must resolve exactly one current-subject form
- that form must be either `current artifact ... via ...` or `current none`
- the carrier side must point at an emitted output field
- that field must be listed in the output's `trust_surface`
- if the current artifact is itself an output root, the concrete turn must emit
  that output
- route-only outputs such as examples `40` through `42` intentionally stay
  outside `trust_surface`; they normalize comment-schema readback for
  `current none` turns instead of carrying portable current truth

## Scope And Preservation

Workflow law is how Doctrine makes narrow edit authority explicit.

```prompt
law:
    own only {SectionMetadata.name, SectionMetadata.description}
    preserve exact SectionMetadata.* except {SectionMetadata.name, SectionMetadata.description}
    preserve decisions ApprovedStructure
    forbid {SectionMetadata.taxonomy, SectionMetadata.flags}
```

Use these statements for different jobs:

- `own only` marks the writable scope for the active branch
- `preserve exact` protects the rest of the current artifact unless explicitly
  excepted
- `preserve structure`, `preserve decisions`, `preserve mapping`, and
  `preserve vocabulary` protect other declared truths that must stay stable
- `forbid` blocks narrow scope that the role must not modify

Compiler-owned checks keep this honest:

- owned paths must stay rooted in the current artifact
- owned paths must stay addressable
- owned scope cannot overlap exact preservation without an explicit `except`
- owned scope cannot overlap forbidden scope

## Evidence Roles

Not every supporting input is equal. Workflow law distinguishes comparison help
from truth and rewrite evidence.

```prompt
law:
    support_only AcceptedPeerSet for comparison

    ignore PrimaryManifest.title for rewrite_evidence when pass_mode == MetadataPolishMode.manifest_title and CurrentHandoff.rewrite_regime == RewriteRegime.rewrite
```

Use these rules when a turn needs to say:

- this artifact may guide comparison but must not become current truth
- this old wording no longer counts as rewrite evidence on rewrite passes

The shipped basis roles are:

- `truth`
- `comparison`
- `rewrite_evidence`

## Invalidation, Stop, And Route

Invalidation is a first-class truth transition.

```prompt
law:
    when CurrentHandoff.structure_changed:
        invalidate SectionReview via RewriteAwareCoordinationHandoff.invalidations
        stop "Structure moved; downstream review is no longer current."
        route "Route the same issue back to RoutingOwner for rebuild." -> RoutingOwner
```

This does not delete the artifact. It says the artifact is no longer portable as
current truth and that downstream owners must be able to see that loss of
authority on the declared carrier.

Common pattern:

- invalidate the no-longer-current artifact
- stop the current lane
- route back to an owner that can rebuild or reroute honestly

## Law Reuse Through Named Subsections

Inherited workflows patch `law` the same way Doctrine patches other compiler-
owned structure: explicitly and exhaustively.

```prompt
workflow RewriteAwareMetadataPolish[BaseMetadataPolish]: "Metadata Polish"
    law:
        inherit activation
        inherit mode_selection
        inherit scope

        override currentness:
            ...

        override evidence:
            ...

        override stop_lines:
            ...
```

Rules:

- reusable inherited `law` must be split into named subsections
- inherited children must account for every inherited subsection exactly once
- `override <section_key>:` must target a real parent subsection
- inherited law cannot mix bare statements with subsection patch entries

## Rendering Model

Rendered `AGENTS.md` stays human-first.

Workflow law compiles into plain English such as:

- which mode is active
- which artifact is current now
- what scope is owned
- what truth must be preserved
- what is comparison-only support
- what is no longer current
- when the role must stop or reroute

The language stays Doctrine-native:

- authors still write ordinary workflow prose for mission and tone
- the compiler owns law semantics, ordering, and fail-loud validation
- outputs still render as normal output contracts with readable `trust_surface`,
  guarded conditional shells, and `standalone_read` sections

## Example Ladder

The active examples are intended to be read in order:

The route-only story is staged on purpose:

- `30` introduces the narrow law surface
- `40` and `41` split the local-ownership and reroute outcomes on whether the
  next owner is still unknown
- `42` recombines those ideas into the full route-only handoff capstone

- `30_law_route_only_turns`: narrow route-only setup with `current none`,
  `stop`, and explicit reroute
- `31_currentness_and_trust_surface`: portable currentness through emitted
  carrier fields and trusted output surfaces
- `32_modes_and_match`: enum-backed `mode`, exhaustive `match`, and one current
  subject per branch
- `33_scope_and_exact_preservation`: `own only`, `preserve exact`, and narrow
  scope contradiction checks
- `34_structure_mapping_and_vocabulary_preservation`: non-exact preservation
  families for structure, mapping, and vocabulary
- `35_basis_roles_and_rewrite_evidence`: comparison-only support and rewrite-
  evidence exclusions
- `36_invalidation_and_rebuild`: invalidation as a truth transition and the
  rebuild pattern
- `37_law_reuse_and_patching`: named law subsections plus inherited explicit
  patching
- `38_metadata_polish_capstone`: the full portable-truth model across modes,
  carriers, scope, preservation, evidence, invalidation, and reroute
- `39_guarded_output_sections`: output-owned keyed guarded sections, nested
  guarded readback, and the narrowed output-guard namespace
- `40_route_only_local_ownership`: local-ownership branch of the route-only
  slice with `current none` when ownership stays local because reroute is not
  justified
- `41_route_only_reroute_handoff`: explicit reroute branch of the route-only
  slice when the next owner is still unknown, paired with a handoff comment
  contract
- `42_route_only_handoff_capstone`: the full generic Slice A route-only
  handoff model with conditional reroute and guarded output readback

The route-only ladder now proves both remaining Slice A structured couplings:

- `41` proves that a routed `next_owner` field must structurally bind the
  routed target through explicit interpolation
- `42` proves that `standalone_read` may not structurally interpolate guarded
  output detail

That proof boundary stays honest: Doctrine still does not parse arbitrary prose
inside `standalone_read`.

## Not Shipped

Doctrine intentionally does not ship these features in workflow law today:

- a packet primitive or free-floating coordination token model
- a top-level reusable `law` declaration family
- targetless `route`
- `obligation`, `lens`, `concern`, or `current status`
- nominal artifact typing as a separate declaration kind
- basis roles beyond `truth`, `comparison`, and `rewrite_evidence`
- `let`
- a separate `review` primitive

If those ideas return later, they need to strengthen the same core model rather
than open a second coordination language.

## Related Docs

- [Why Doctrine](WHY_DOCTRINE.md)
- [Language Design Notes](LANGUAGE_DESIGN_NOTES.md)
- [Agent I/O Design Notes](AGENT_IO_DESIGN_NOTES.md)
- [Compiler Errors](COMPILER_ERRORS.md)
- [Examples](../examples/README.md)
