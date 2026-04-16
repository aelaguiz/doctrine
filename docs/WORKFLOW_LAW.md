# Workflow Law

Doctrine workflow law is the shipped typed surface for turns that need
compiler-checked truth, not just ordinary instruction prose.

Use it when a turn needs any of these behaviors:

- explicit activation conditions
- one current artifact per active branch, or explicitly no current artifact
- narrow write authority with preserved truth outside the owned scope
- comparison-only support or rewrite-evidence exclusions
- invalidation when upstream truth moves, including declared schema groups
- fail-loud stop lines and honest reroute

For the full declaration overview, use
[LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md). For the numbered proof ladder,
use [../examples/README.md](../examples/README.md). For the shipped
flow-visualization CLI that renders these semantics, use
[EMIT_GUIDE.md](EMIT_GUIDE.md).
If you first need to decide whether the turn should use plain `workflow`,
workflow `law`, `handoff_routing`, `route_only`, or `grounding`, start with
[AUTHORING_PATTERNS.md](AUTHORING_PATTERNS.md).

## Core Split

Workflow law does not replace normal workflow prose. It adds compiler-owned
semantics to a workflow while keeping the emitted contract on `output`.

The governing split is:

- `workflow` still explains the job in human language
- `law` inside `workflow` decides local truth and branch behavior
- `output` still defines what the turn emits
- when law resolves a real route, emitted outputs may read shared `route.*`
  semantics on that same turn
- `trust_surface` inside `output` marks which emitted fields downstream owners
  may trust
- guarded output items keep conditional readback on the output contract
  instead of creating a second control plane

## Where The Syntax Lives

Workflow law widens two existing surfaces:

- `law:` on `workflow`
- `trust_surface:` on `output`

It also relies on ordinary output structure for guarded readback:

```prompt
output RouteOnlyHandoffOutput: "Routing Handoff Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    rewrite_mode: "Rewrite Mode" when RouteFacts.section_status in {"new", "full_rewrite"}:
        "Say plainly that later metadata must be rewritten instead of inherited."
```

Important rules:

- Guarded output items are still output-owned fields.
- They are required only when their guard resolves true.
- On ordinary outputs, guards may read declared inputs, enum members, and
  `route.exists` when the active workflow-law branches expose route semantics.
- When every live routed branch comes from `route_from`, guards may also read
  `route.choice`.
- They may not read workflow-local bindings, emitted output fields, or
  undeclared runtime names.

When workflow law resolves a real route, emitted outputs may read:

- `route.exists`
- `route.next_owner`
- `route.next_owner.key`
- `route.next_owner.title`
- `route.label`
- `route.summary`
- `route.choice`
- `route.choice.key`
- `route.choice.title`
- `route.choice.wire`

Important rules:

- `route.*` is compiler-owned derived truth from authored `route "..." -> Agent`
  statements
- unguarded `route.*` reads fail loudly when some active branches may not route
- `when route.exists:` is the ordinary output-side guard for route-specific
  readback, whether the guarded item is one scalar field or one section
- `route.choice.*` is live only when every live routed branch comes from
  `route_from`
- `route.next_owner.*` may stay live across several `route_from` branches. It
  means the selected route owner.
- `route.label` and `route.summary` still need one selected branch. Guard them
  with `route.choice` when more than one route branch stays live.
- When `emit_docs` writes `final_output.contract.json`, the same route truth
  appears in the top-level `route` block. Harnesses should read that block for
  routing instead of treating copied output fields as the route contract.

## Handoff Routing Reuses The Same Route Surface

`handoff_routing:` may also carry a route-only `law:` block.

Use that when a turn needs compiler-owned route truth on `output` or
`final_output:`, but does not need workflow-law currentness, preservation, or
invalidation.

Important rules:

- `handoff_routing` law supports only `active when`, `mode`, `when`, `match`,
  `route_from`, `stop`, and `route`
- currentness, preservation, invalidation, and basis-role controls stay on
  `workflow`
- prose route lines inside `handoff_routing` do not make `route.*` live
- `handoff_routing` uses the same output-side `route.exists`,
  `route.next_owner`, `route.next_owner.key`, `route.next_owner.title`,
  `route.label`, `route.summary`, and `route.choice.*` surface ordinary
  workflow law already uses
- emitted final-output contracts use the same top-level `route` block for
  `handoff_routing` as they use for workflow law

## route_from

`route_from` selects one route from a typed selector.

Use it when the turn already receives or emits a typed route fact and you want
Doctrine to own the selected route truth.

```prompt
law:
    route_from ProofResult.route_choice as ProofRoute:
        ProofRoute.accept:
            route "Send to AcceptanceCritic." -> AcceptanceCritic
        ProofRoute.change:
            route "Send to ChangeEngineer." -> ChangeEngineer
```

Important rules:

- `route_from` is legal on `workflow` law and `handoff_routing` law.
- The selector must stay one direct ref.
- It may point at a declared input field, an emitted output field on the
  concrete turn, or an enum member.
- Do not compute inside the selector or read workflow-local bindings there.
- Each arm selects one route.
- Name each enum member at most once. Use `else` at most once.
- `route.choice.*` is live only when every live routed branch comes from
  `route_from`.
- `route.next_owner.*` works on the selected route even when several
  `route_from` branches stay live at compile time.
- `route.label` and `route.summary` still need one selected branch.

## Branch Model

Workflow law is evaluated per active leaf branch, not as one flat list.

The branch-shaping tools are:

- `active when`
- `when`
- `mode`
- `match`
- `route_from`
- `must`

Example:

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

Important rules:

- `mode` binds one expression to one enum.
- `match` on an enum must be exhaustive or include `else`.
- `must` is the fail-loud surface for branch-local required facts.
- Every active leaf branch must resolve exactly one current-subject form.

## Currentness And Carriers

Workflow law has two current-subject forms:

- `current artifact ... via ...`
- `current none`

Example:

```prompt
output CoordinationHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    trust_surface:
        current_artifact

workflow CarryCurrentTruth: "Carry Current Truth"
    law:
        current artifact SectionMetadata via CoordinationHandoff.current_artifact
```

Carrier rules:

- the carrier must point at an emitted output field
- the carrier field must be listed in that output's `trust_surface`
- if the current artifact is itself an output root, the concrete turn must emit
  that output
- route-only turns may use `current none` instead of pretending a durable
  artifact exists

Examples `40` through `42` intentionally keep their route-only handoff comments
outside `trust_surface`. They normalize comment readback for `current none`
turns; they do not carry portable current truth.

`route_only` is the dedicated declaration that lowers through this same
`current none` and route validation path. It adds authored `facts:`,
activation `when:`, `handoff_output:`, guarded top-level output keys, and
explicit `routes:` without creating a second route engine. If the turn also
declares `final_output:`, the emitted `final_output.contract.json` carries the
same compiler-owned route target in its top-level `route` block.

## Scope, Preservation, And Evidence Roles

Workflow law makes narrow edit authority explicit.

```prompt
law:
    own only {SectionMetadata.name, SectionMetadata.description}
    preserve exact SectionMetadata.* except {SectionMetadata.name, SectionMetadata.description}
    preserve decisions ApprovedStructure
    support_only AcceptedPeerSet for comparison
    ignore {SectionMetadata.name, SectionMetadata.description} for rewrite_evidence when CurrentHandoff.rewrite_regime == RewriteRegime.rewrite
```

Use these statements for different jobs:

- `own only`: the writable scope for the active branch
- `preserve exact`: exact stability outside owned scope
- `preserve structure`, `preserve decisions`, `preserve mapping`,
  `preserve vocabulary`: non-exact truth that must remain stable
- `forbid`: narrow scope the role must not modify
- `support_only ... for comparison`: comparison help that does not become truth
- `ignore ... for truth|comparison|rewrite_evidence`: declared exclusions from
  a basis role

Compiler-owned checks keep this honest:

- owned paths may root only in the current artifact, an emitted output surface
  the concrete turn owns, or a declared schema family
- owned paths must stay addressable
- `own only` does not target declared groundings
- `preserve exact` may target declared or bound concrete-turn inputs or
  outputs plus declared schema families
- `preserve structure` and `preserve decisions` may target declared or bound
  concrete-turn inputs or outputs
- `preserve mapping` may target declared or bound concrete-turn inputs or
  outputs plus declared schema families and declared groundings
- `preserve vocabulary` may target declared enums plus declared or bound
  concrete-turn inputs or outputs and declared schema families
- schema families and groundings participate as modeled roots, not arbitrary
  field-descent surfaces
- overlaps are checked after normalization, not by raw authored text alone
- `own only` cannot overlap `preserve exact` without an explicit `except`
- `own only` cannot overlap `forbid`

## Invalidation, Stop, And Route

Invalidation is a first-class truth transition:

```prompt
law:
    when CurrentHandoff.structure_changed:
        invalidate SectionReview via RewriteAwareCoordinationHandoff.invalidations
        stop "Structure moved; downstream review is no longer current."
        route "Route the same issue back to RoutingOwner for rebuild." -> RoutingOwner
```

Use this pattern when upstream truth moved and a downstream artifact must stop
counting as current.

`invalidate` may target one concrete input or output root or a declared schema
group such as `BuildSurfaceSchema.groups.downstream_rebuild`. Group
invalidations expand to concrete member artifacts in authored group order when
they render or flow through trusted carriers.

The shipped control-flow statements are:

- `stop`
- `route "..." -> Agent`
- `route "..." -> Agent when expr`

## Bound Roots And Inherited Bindings

Workflow law can root paths through named concrete-turn bindings:

```prompt
workflow CarryBoundCurrentTruth: "Carry Bound Current Truth"
    law:
        current artifact approved_plan via coordination_handoff.current_artifact
```

That bound root still normalizes to the underlying declared input or output.
It is not a string alias.

Important rules:

- bound roots work for currentness, invalidation, scope, and preservation
- inherited `inputs` and `outputs` blocks keep their bound roots visible
- examples `50`, `51`, and `52` are the canonical shipped proof for this
  model, including emitted-output and schema-family ownership roots

## Law Reuse And Patching

Inherited workflows patch `law` with the same explicit model used elsewhere.

Reusable inherited law should be split into named subsections:

```prompt
workflow RewriteAwareMetadataPolish[BaseMetadataPolish]: "Metadata Polish"
    law:
        inherit activation
        inherit mode_selection
        inherit scope

        override evidence:
            ...

        override stop_lines:
            ...
```

Important rules:

- inherited reusable law must use named subsections
- children must account for every inherited subsection exactly once
- `override <section_key>:` must target a real parent subsection
- inherited law may not mix named subsection patching with bare parent law
  statements
- Doctrine does not ship a separate reusable preservation declaration family.
  Reuse preservation pressure by factoring named law subsections and inheriting
  or patching them, as shown in `37_law_reuse_and_patching`.

## Grounding

`grounding` is not itself workflow law, but it shares the same control-plane
boundary. It declares explicit grounding policy with `source:`, `target:`, and
`policy:` items such as `start_from`, `forbid`, `allow`, and `if ... -> route
...`, while keeping routing on ordinary concrete agents and keeping output
readback on ordinary emitted surfaces.

## Example Ladder

Read the workflow-law examples in this order:

- `30_law_route_only_turns`: the narrow setup with `current none`, `stop`, and
  explicit reroute
- `31_currentness_and_trust_surface`: one current artifact plus trusted
  carriers
- `32_modes_and_match`: enum-backed mode selection and exhaustive branching
- `33_scope_and_exact_preservation`: narrow ownership and exact preservation
- `34_structure_mapping_and_vocabulary_preservation`: preserved non-exact
  truth, including schema-family mapping and vocabulary roots
- `35_basis_roles_and_rewrite_evidence`: comparison-only help and rewrite
  exclusions
- `36_invalidation_and_rebuild`: invalidation and rebuild routing
- `37_law_reuse_and_patching`: named law subsections plus inheritance
- `38_metadata_polish_capstone`: the integrated workflow-law capstone
- `39_guarded_output_sections`: conditional readback on `output`
- `40` through `42`: the staged route-only handoff ladder
- `70_route_only_declaration`: dedicated `route_only` lowered through the same
  route-only validation path
- `87_workflow_route_output_binding`: shared `route.*` reads on ordinary
  workflow-law outputs plus fail-loud unguarded route reads
- `89_route_only_shared_route_semantics`: dedicated `route_only` feeding the
  same shared output-facing route semantics
- `91_handoff_routing_route_output_binding`: `handoff_routing` law feeding the
  same shared output-facing route semantics into ordinary outputs and
  `final_output:`
- `92_route_from_basic`: first-class `route_from` on workflow law
- `93_handoff_routing_route_from_final_output`: emitted-output route selection
  on `handoff_routing` plus `final_output:`
- `94_route_choice_guard_narrowing`: `route.choice` guards narrowing
  `route.summary`
- `71_grounding_declaration`: explicit grounding protocol with ordinary route
  targets plus grounding-root preservation mapping
- `72_schema_group_invalidation`: schema-group invalidation expansion in
  authored order
- `50` through `52`: bound roots for currentness, inherited bindings, and
  preservation law
